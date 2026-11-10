# SPDX-License-Identifier: Apache-2.0

"""Self-contained 'Bookshelf_with_books' template — desktop book trays.

Rebuilt from the ``pictureX/0611/bookshelf_with_books`` origin record and the
accepted forks listed in
``articraft_template_authoring/source_maps/pictureX_0611_Bookshelf_with_books.md``.

Category identity: an injection-moulded **desktop file sorter** — a deck between
two perforated end walls, split into upright bays by N movable divider plates.
The source record states the identity explicitly: the folder is labelled
``Bookshelf_with_books`` but 001.png is a white moulded desktop file sorter, so
the perforated end walls and the tall sliding divider plates are the
recognisable structure and are preserved here.  Four independent axes:

* ``tray_body``          — the deck family: flat sorter (001), incline rack,
  stepped tiers, cube grid and mesh basket forks.
* ``end_walls``          — perforated moulded ends (the source signature),
  fold-flat hinged ends, or L-profile bookend ends with a broad foot.
* ``divider_mechanism``  — dividers sliding along the width, lifting out of
  floor sockets, or sliding bookends running on a floor rail.
* ``base_style``         — flat rails or moulded feet.

Every ``tray_body`` exports the same deck interface (deck plane, usable
half-width, bay depth and wall height); the other slots consume only that
interface, so all 5 x 3 x 3 x 2 = 90 combinations build without a gate.

Coordinate frame: +X = width (centred on 0), +Y = depth with the front edge at
+depth/2, +Z = height with the desk surface at z = 0.

This file is the only runtime truth.  It imports the stdlib and the Articraft
``sdk`` only.
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
    AxisInterface,
    Box,
    Cylinder,
    MotionLimits,
    MotionProperties,
    Origin,
    PlaneInterface,
    SlotPatternPanelGeometry,
    TemplateDomain,
    TestContext,
    TestReport,
    component_slot,
    corner_case,
    mate_axes,
    mate_planes,
    mesh_from_geometry,
    multiplicity_slot,
    register_interface_mate,
)

TrayBody = Literal[
    "flat_tray",
    "incline_rack",
    "stepped_tiers",
    "cube_grid",
    "mesh_basket",
]
EndWalls = Literal["perforated_end_walls", "fold_flat_walls", "bookend_supports"]
DividerMechanism = Literal["sliding_dividers", "liftout_dividers", "sliding_bookends"]
BaseStyle = Literal["flat_base", "footed_base"]

TRAY_BODIES: tuple[TrayBody, ...] = (
    "flat_tray",
    "incline_rack",
    "stepped_tiers",
    "cube_grid",
    "mesh_basket",
)
END_WALLS: tuple[EndWalls, ...] = (
    "perforated_end_walls",
    "fold_flat_walls",
    "bookend_supports",
)
DIVIDER_MECHANISMS: tuple[DividerMechanism, ...] = (
    "sliding_dividers",
    "liftout_dividers",
    "sliding_bookends",
)
BASE_STYLES: tuple[BaseStyle, ...] = ("flat_base", "footed_base")
DIVIDER_COUNTS: tuple[int, ...] = (2, 3, 5, 7)

TEMPLATE_DOMAIN = TemplateDomain(
    (
        component_slot("tray_body", TRAY_BODIES),
        component_slot("end_walls", END_WALLS),
        component_slot("divider_mechanism", DIVIDER_MECHANISMS),
        component_slot("base_style", BASE_STYLES),
        multiplicity_slot(
            "divider_count",
            DIVIDER_COUNTS,
            item_slot="divider_mechanism",
        ),
    )
)

# Independent continuous parameters (honest dimensions; not core/raw domain).
_WIDTH_RANGE = (0.28, 0.55)
_DEPTH_RANGE = (0.14, 0.32)
_WALL_HEIGHT_RANGE = (0.13, 0.26)
_PANEL_THICKNESS_RANGE = (0.008, 0.016)

_DECK_T = 0.014
_RAIL_H = 0.016
_FOOT_H = 0.030
_ROD_R = 0.0015  # guide rod radius (thin, so the captured shoe stays in tolerance)
_ROD_Z = 0.014  # guide rod height above the deck plane
_SHOE_R = 0.006  # divider shoe bore radius riding the rod
_DIVIDER_SEAT = 0.002  # divider foot captured inside its seat rail
_SOCKET_ENGAGE = 0.002  # lift-out divider captured inside its socket cheeks
_HINGE_R = 0.008
_HINGE_PIN_R = 0.0018
_WALL_ROOT = 0.010  # end walls reach this far below the deck plane
_BOOK_CLEAR = 0.006
_MIN_BAY = 0.032  # floor on the clear bay width at the maximum divider count
_FOLD_SWING = 1.45
_SLOT_ROWS = 5  # source end wall carries a 5 x 5 rounded slot grid
_SLOT_COLS = 5


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


@dataclass(frozen=True)
class Config:
    tray_body: TrayBody = "flat_tray"
    end_walls: EndWalls = "perforated_end_walls"
    divider_mechanism: DividerMechanism = "sliding_dividers"
    base_style: BaseStyle = "flat_base"
    divider_count: int = 3
    width_m: float | None = None
    depth_m: float | None = None
    wall_height_m: float | None = None
    panel_thickness_m: float | None = None
    name: str = "pictureX_0611_Bookshelf_with_books"


@dataclass(frozen=True)
class ResolvedConfig:
    tray_body: TrayBody
    end_walls: EndWalls
    divider_mechanism: DividerMechanism
    base_style: BaseStyle
    divider_count: int
    width_m: float
    depth_m: float
    wall_height_m: float
    panel_thickness_m: float
    base_lift_m: float
    deck_z_m: float
    usable_half_x_m: float
    bay_pitch_m: float
    divider_travel_m: float
    name: str


def config_from_seed(seed: int) -> Config:
    choices = TEMPLATE_DOMAIN.sample(seed)
    rng = random.Random(seed ^ 0xB005_2026)
    return Config(
        tray_body=choices["tray_body"],
        end_walls=choices["end_walls"],
        divider_mechanism=choices["divider_mechanism"],
        base_style=choices["base_style"],
        divider_count=choices["divider_count"],
        width_m=round(rng.uniform(*_WIDTH_RANGE), 4),
        depth_m=round(rng.uniform(*_DEPTH_RANGE), 4),
        wall_height_m=round(rng.uniform(*_WALL_HEIGHT_RANGE), 4),
        panel_thickness_m=round(rng.uniform(*_PANEL_THICKNESS_RANGE), 4),
    )


def _range_check(name: str, value: float, bounds: tuple[float, float]) -> None:
    low, high = bounds
    if not low <= value <= high:
        raise ValueError(f"{name} must be in [{low}, {high}], got {value}")


def _under_deck(tray_body: TrayBody, depth: float) -> float:
    """How far the body's own structure reaches below the deck reference plane."""
    return _DECK_T


def _base_lift(base_style: BaseStyle, depth: float) -> float:
    """Floor-to-deck lift set by the moulded base the sorter stands on."""
    return {"flat_base": _RAIL_H, "footed_base": _FOOT_H}[base_style]


def resolve_config(config: Config) -> ResolvedConfig:
    TEMPLATE_DOMAIN.validate(
        {
            "tray_body": config.tray_body,
            "end_walls": config.end_walls,
            "divider_mechanism": config.divider_mechanism,
            "base_style": config.base_style,
            "divider_count": config.divider_count,
        }
    )
    width = 0.520 if config.width_m is None else float(config.width_m)
    depth = 0.220 if config.depth_m is None else float(config.depth_m)
    wall_h = 0.185 if config.wall_height_m is None else float(config.wall_height_m)
    panel_t = 0.012 if config.panel_thickness_m is None else float(config.panel_thickness_m)
    _range_check("width_m", width, _WIDTH_RANGE)
    _range_check("depth_m", depth, _DEPTH_RANGE)
    _range_check("wall_height_m", wall_h, _WALL_HEIGHT_RANGE)
    _range_check("panel_thickness_m", panel_t, _PANEL_THICKNESS_RANGE)

    count = int(config.divider_count)
    # Host capacity: every bay must still take a book row, so the tray grows
    # wide enough for the divider count it carries.
    min_width = 2.0 * panel_t + float(count + 1) * (_MIN_BAY + panel_t) + 0.004
    width = max(width, min_width)
    lift = _base_lift(config.base_style, depth)
    # The tray seats 2 mm onto its base rails/feet, so it is never a floating island.
    deck_z = lift + _under_deck(config.tray_body, depth) - 0.002
    usable_half = width / 2.0 - panel_t
    pitch = (usable_half * 2.0) / float(count + 1)
    # Two neighbouring dividers may never meet, so the travel is capped by half
    # of the clear gap between their widest elements: the divider cap is 1.8x
    # the panel thickness, and a sliding bookend also carries a foot.
    half_span = 0.9 * panel_t
    if config.divider_mechanism == "sliding_bookends":
        half_span = max(half_span, 0.18 * pitch)
    clear_gap = max(pitch - 2.0 * half_span - 0.004, 0.002)
    travel = min(_clamp(0.26 * pitch, 0.004, 0.045), clear_gap / 2.0)
    return ResolvedConfig(
        tray_body=config.tray_body,
        end_walls=config.end_walls,
        divider_mechanism=config.divider_mechanism,
        base_style=config.base_style,
        divider_count=count,
        width_m=width,
        depth_m=depth,
        wall_height_m=wall_h,
        panel_thickness_m=panel_t,
        base_lift_m=lift,
        deck_z_m=deck_z,
        usable_half_x_m=usable_half,
        bay_pitch_m=pitch,
        divider_travel_m=travel,
        name=config.name,
    )


def slot_choices_for_config(config: Config | ResolvedConfig) -> tuple[tuple[str, object], ...]:
    return (
        ("tray_body", config.tray_body),
        ("end_walls", config.end_walls),
        ("divider_mechanism", config.divider_mechanism),
        ("base_style", config.base_style),
        ("divider_count", int(config.divider_count)),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, object], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# --------------------------------------------------------------------------- #
# Materials and primitive helpers
# --------------------------------------------------------------------------- #
def _materials(model: ArticulatedObject) -> dict[str, str]:
    model.material("tray_wood", rgba=(0.55, 0.40, 0.24, 1.0))
    model.material("tray_edge", rgba=(0.42, 0.29, 0.17, 1.0))
    model.material("divider_panel", rgba=(0.72, 0.60, 0.42, 1.0))
    model.material("steel_grey", rgba=(0.52, 0.54, 0.56, 1.0))
    model.material("book_red", rgba=(0.55, 0.18, 0.16, 1.0))
    model.material("book_blue", rgba=(0.20, 0.30, 0.50, 1.0))
    model.material("book_cream", rgba=(0.82, 0.76, 0.60, 1.0))
    return {
        "wood": "tray_wood",
        "edge": "tray_edge",
        "panel": "divider_panel",
        "steel": "steel_grey",
        "book_a": "book_red",
        "book_b": "book_blue",
        "book_c": "book_cream",
    }


def _box(part, size, xyz, material: str, name: str, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(Box(size), origin=Origin(xyz=xyz, rpy=rpy), material=material, name=name, material_class_id="wood.natural_generic")


def _cyl(part, radius, length, xyz, material: str, name: str, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=Origin(xyz=xyz, rpy=rpy),
        material=material,
        name=name, material_class_id="metal.steel_bare",
    )


@dataclass(frozen=True)
class _Deck:
    """The deck interface every tray_body must provide (tray-local frame)."""

    deck_top_z: float
    usable_half_x: float
    bay_depth: float
    bay_y_center: float
    wall_height: float
    book_height: float
    pitch_boost_z: float


def _bay_x_centers(r: ResolvedConfig) -> list[float]:
    return [
        -r.usable_half_x_m + r.bay_pitch_m * (float(index) + 0.5)
        for index in range(r.divider_count + 1)
    ]


def _divider_x_positions(r: ResolvedConfig) -> list[float]:
    return [
        -r.usable_half_x_m + r.bay_pitch_m * float(index + 1)
        for index in range(r.divider_count)
    ]


# --------------------------------------------------------------------------- #
# tray_body candidates (all geometry is authored in the tray part frame)
# --------------------------------------------------------------------------- #
def _add_deck_slab(tray, r: ResolvedConfig, mats, *, depth: float, y_center: float) -> None:
    _box(
        tray,
        (r.width_m, depth, _DECK_T),
        (0.0, y_center, -_DECK_T / 2.0),
        mats["wood"],
        "deck_board",
    )


def _tray_body_flat_tray_build(tray, r: ResolvedConfig, mats) -> _Deck:
    """001 L106-L253: a flat deck with a low rear rail."""
    _add_deck_slab(tray, r, mats, depth=r.depth_m, y_center=0.0)
    _box(
        tray,
        (r.width_m, r.panel_thickness_m, r.wall_height_m * 0.45),
        (0.0, -r.depth_m / 2.0 + r.panel_thickness_m / 2.0, r.wall_height_m * 0.225),
        mats["edge"],
        "rear_rail",
    )
    return _Deck(
        deck_top_z=0.0,
        usable_half_x=r.usable_half_x_m,
        bay_depth=r.depth_m - 2.0 * r.panel_thickness_m,
        bay_y_center=0.0,
        wall_height=r.wall_height_m,
        book_height=r.wall_height_m * 0.86,
        pitch_boost_z=0.0,
    )


def _tray_body_incline_rack_build(tray, r: ResolvedConfig, mats) -> _Deck:
    """incline_rack fork L114-L272: a leaning back rest with a front lip.

    The deck itself stays flat so every divider mechanism keeps the same seat;
    the rack character comes from the raked back rest the books lean against and
    from the retaining lip at the front edge.
    """
    _add_deck_slab(tray, r, mats, depth=r.depth_m, y_center=0.0)
    rake = math.radians(8.0)
    rest_h = r.wall_height_m
    _box(
        tray,
        (r.width_m, r.panel_thickness_m, rest_h),
        (
            0.0,
            -r.depth_m / 2.0 + 0.018 + math.sin(rake) * rest_h / 2.0,
            rest_h / 2.0 - 0.006,
        ),
        mats["edge"],
        "raked_back_rest",
        rpy=(-rake, 0.0, 0.0),
    )
    _box(
        tray,
        (r.width_m, r.panel_thickness_m, 0.045),
        (0.0, r.depth_m / 2.0 - r.panel_thickness_m / 2.0, 0.0165),
        mats["edge"],
        "front_lip",
    )
    bay_back = -r.depth_m / 2.0 + 0.018 + math.sin(rake) * rest_h + 0.012
    bay_front = r.depth_m / 2.0 - 0.014
    bay_depth = max(bay_front - bay_back, 0.05)
    return _Deck(
        deck_top_z=0.0,
        usable_half_x=r.usable_half_x_m,
        bay_depth=bay_depth,
        bay_y_center=(bay_front + bay_back) / 2.0,
        wall_height=r.wall_height_m,
        book_height=r.wall_height_m * 0.80,
        pitch_boost_z=0.0,
    )


def _tray_body_stepped_tiers_build(tray, r: ResolvedConfig, mats) -> _Deck:
    """stepped_tiers fork L135-L308: a raised rear tier stepped above the front."""
    front_depth = r.depth_m * 0.58
    rear_depth = r.depth_m - front_depth
    step_h = _clamp(r.wall_height_m * 0.32, 0.035, 0.075)
    _add_deck_slab(tray, r, mats, depth=front_depth, y_center=r.depth_m / 2.0 - front_depth / 2.0)
    _box(
        tray,
        (r.width_m, rear_depth, _DECK_T),
        (0.0, -r.depth_m / 2.0 + rear_depth / 2.0, step_h - _DECK_T / 2.0),
        mats["wood"],
        "rear_tier_board",
    )
    _box(
        tray,
        (r.width_m, r.panel_thickness_m, step_h),
        (0.0, -r.depth_m / 2.0 + rear_depth - r.panel_thickness_m / 2.0, step_h / 2.0 - _DECK_T),
        mats["edge"],
        "step_riser",
    )
    return _Deck(
        deck_top_z=0.0,
        usable_half_x=r.usable_half_x_m,
        bay_depth=front_depth - r.panel_thickness_m,
        bay_y_center=r.depth_m / 2.0 - front_depth / 2.0,
        wall_height=r.wall_height_m,
        book_height=r.wall_height_m * 0.84,
        pitch_boost_z=0.0,
    )


def _tray_body_cube_grid_build(tray, r: ResolvedConfig, mats) -> _Deck:
    """cube_grid fork L81-L345: a mid board splits the tray into two rows."""
    _add_deck_slab(tray, r, mats, depth=r.depth_m, y_center=0.0)
    mid_z = r.wall_height_m * 0.62
    _box(
        tray,
        (r.width_m, r.depth_m, _DECK_T * 0.9),
        (0.0, 0.0, mid_z),
        mats["wood"],
        "mid_board",
    )
    _box(
        tray,
        (r.width_m, r.panel_thickness_m, r.wall_height_m),
        (0.0, -r.depth_m / 2.0 + r.panel_thickness_m / 2.0, r.wall_height_m / 2.0),
        mats["edge"],
        "back_board",
    )
    return _Deck(
        deck_top_z=0.0,
        usable_half_x=r.usable_half_x_m,
        bay_depth=r.depth_m - 2.0 * r.panel_thickness_m,
        bay_y_center=0.0,
        wall_height=max(mid_z - 0.020, 0.052),
        book_height=max(mid_z - 0.034, 0.038),
        pitch_boost_z=0.0,
    )


def _tray_body_mesh_basket_build(tray, r: ResolvedConfig, mats) -> _Deck:
    """mesh_basket fork L146-L398: lattice walls instead of solid boards."""
    _add_deck_slab(tray, r, mats, depth=r.depth_m, y_center=0.0)
    slats = int(_clamp(round(r.wall_height_m / 0.035), 3, 6))
    for index in range(slats):
        z = r.wall_height_m * (float(index) + 0.5) / float(slats)
        _box(
            tray,
            (r.width_m, r.panel_thickness_m * 0.8, 0.010),
            (0.0, -r.depth_m / 2.0 + r.panel_thickness_m / 2.0, z),
            mats["steel"],
            f"mesh_slat_rear_{index}",
        )
    posts = int(_clamp(round(r.width_m / 0.09), 3, 8))
    for index in range(posts):
        x = -r.width_m / 2.0 + r.width_m * (float(index) + 0.5) / float(posts)
        _box(
            tray,
            (0.006, r.panel_thickness_m * 0.8, r.wall_height_m),
            (x, -r.depth_m / 2.0 + r.panel_thickness_m / 2.0, r.wall_height_m / 2.0),
            mats["steel"],
            f"mesh_post_{index}",
        )
    return _Deck(
        deck_top_z=0.0,
        usable_half_x=r.usable_half_x_m,
        bay_depth=r.depth_m - 2.0 * r.panel_thickness_m,
        bay_y_center=0.0,
        wall_height=r.wall_height_m,
        book_height=r.wall_height_m * 0.86,
        pitch_boost_z=0.0,
    )


_TRAY_BUILDERS = {
    "flat_tray": _tray_body_flat_tray_build,
    "incline_rack": _tray_body_incline_rack_build,
    "stepped_tiers": _tray_body_stepped_tiers_build,
    "cube_grid": _tray_body_cube_grid_build,
    "mesh_basket": _tray_body_mesh_basket_build,
}


# --------------------------------------------------------------------------- #
# end_walls candidates
# --------------------------------------------------------------------------- #
def _slot_panel_mesh(
    r: ResolvedConfig,
    *,
    panel_w: float,
    panel_h: float,
    name: str,
):
    """One moulded panel carrying the source's rounded through-slot grid.

    Source ``_end_wall_mm`` cuts a 5 x 5 grid of 23 x 10 mm rounded slots out of
    the end wall (model.py:L47-L105); that perforation is the recognisable
    feature of the moulding, so it is cut here rather than approximated by a
    solid plate.
    """
    # The panel is authored in its own XY plane and extruded along Z; it is
    # placed with its local X along the world height, so the slots stand
    # upright like the source's.
    pitch_v = panel_h / float(_SLOT_ROWS + 1.2)
    pitch_u = panel_w / float(_SLOT_COLS + 0.6)
    # The slot envelope must stay inside its pitch on both axes, so the slot
    # size is derived from the pitch rather than clamped up to a fixed minimum.
    slot_long = max(0.0030, min(pitch_v * 0.62, 0.045))
    slot_short = max(0.0025, min(pitch_u * 0.34, slot_long * 0.85))
    frame = _clamp(min(panel_w, panel_h) * 0.12, 0.008, min(panel_w, panel_h) * 0.44)
    geom = SlotPatternPanelGeometry(
        (panel_h, panel_w),
        r.panel_thickness_m,
        slot_size=(slot_long, slot_short),
        pitch=(pitch_v, pitch_u),
        frame=frame,
        corner_radius=min(panel_w, panel_h) * 0.09,
    )
    return mesh_from_geometry(geom, name)


def _add_perforated_wall(part, r: ResolvedConfig, mats, deck: _Deck, *, x: float, tag: str) -> None:
    """Perforated moulded end wall standing on the deck (source L47-L105)."""
    panel_w = deck.bay_depth * 0.96
    panel_h = deck.wall_height + _WALL_ROOT
    mesh = _slot_panel_mesh(r, panel_w=panel_w, panel_h=panel_h, name=tag)
    part.visual(
        mesh,
        origin=Origin(
            xyz=(x, deck.bay_y_center, panel_h / 2.0 - _WALL_ROOT),
            rpy=(0.0, math.pi / 2.0, 0.0),
        ),
        material=mats["wood"],
        name=tag, material_class_id="wood.veneer_panel",
    )
    # Moulded rim: the perforated field is framed by a solid edge, and the rim
    # is what the deck and the divider standards actually meet.
    rim = r.panel_thickness_m * 1.15
    _box(
        part,
        (rim, panel_w, 0.012),
        (x, deck.bay_y_center, deck.wall_height - 0.006),
        mats["edge"],
        f"{tag}_top_rim",
    )
    _box(
        part,
        (rim, panel_w, 0.014 + _WALL_ROOT),
        (x, deck.bay_y_center, (0.014 - _WALL_ROOT) / 2.0),
        mats["edge"],
        f"{tag}_foot_rim",
    )


def _end_walls_perforated_end_walls_build(model, tray, r, mats, deck) -> list[str]:
    """001 L47-L105: the two perforated moulded end walls of the sorter."""
    for index, sign in enumerate((-1.0, 1.0)):
        _add_perforated_wall(
            tray,
            r,
            mats,
            deck,
            x=sign * (r.width_m / 2.0 - r.panel_thickness_m / 2.0),
            tag=f"end_walls__perforated_end_walls__wall_{index}",
        )
    return []


def _end_walls_fold_flat_walls_build(model, tray, r, mats, deck) -> list[str]:
    """fold_flat fork L267-L306: end walls hinge down flat about the depth axis."""
    joints: list[str] = []
    # The hinge clears the guide rod and its shoe, and the leaf stays at least
    # twice as tall as it is thick so a fold is a fold, not a stub rotating in
    # place.
    hinge_z = _clamp(0.40 * deck.wall_height, 0.024, 0.120)
    leaf_depth = deck.bay_depth * 0.78
    cheek_y = min(r.depth_m / 2.0 - 0.010, leaf_depth / 2.0 + 0.020)
    barrel_y = min(leaf_depth * 0.38, cheek_y - 0.034)
    for index, sign in enumerate((-1.0, 1.0)):
        hinge_x = sign * (r.width_m / 2.0 - r.panel_thickness_m)
        # Fixed lower end panel: the folding leaf hinges above it.
        skirt_top = hinge_z - _HINGE_R * 1.6
        _box(
            tray,
            (r.panel_thickness_m, deck.bay_depth * 0.96, skirt_top + _WALL_ROOT),
            (
                hinge_x,
                deck.bay_y_center,
                (skirt_top - _WALL_ROOT) / 2.0,
            ),
            mats["wood"],
            f"fixed_end_wall_{index}",
        )
        wall = model.part(
            f"end_walls__fold_flat_walls__wall_{index}",
            meta={"role": "end_wall", "side": index},
        )
        height = max(deck.wall_height - hinge_z - 0.004, 2.0 * r.panel_thickness_m)
        _box(
            wall,
            (r.panel_thickness_m, leaf_depth, height),
            (0.0, deck.bay_y_center, height / 2.0),
            mats["wood"],
            "wall_panel",
        )
        _box(
            wall,
            (r.panel_thickness_m * 1.6, deck.bay_depth * 0.30, 0.014),
            (0.0, deck.bay_y_center, height - 0.007),
            mats["edge"],
            "wall_cap",
        )
        for barrel, y in enumerate(
            (deck.bay_y_center - barrel_y, deck.bay_y_center + barrel_y)
        ):
            _cyl(
                wall,
                _HINGE_R,
                deck.bay_depth * 0.16,
                (0.0, y, 0.0),
                mats["steel"],
                f"hinge_barrel_{barrel}",
                rpy=(math.pi / 2.0, 0.0, 0.0),
            )
            # Tray-side pin through the barrel plus its carrying cheek.
            _cyl(
                tray,
                _HINGE_PIN_R,
                (cheek_y - barrel_y) + 0.060,
                (
                    hinge_x,
                    deck.bay_y_center
                    + (1.0 if y > deck.bay_y_center else -1.0) * (barrel_y + cheek_y) / 2.0,
                    hinge_z,
                ),
                mats["steel"],
                f"fold_pin_{index}_{barrel}",
                rpy=(math.pi / 2.0, 0.0, 0.0),
            )
            _box(
                tray,
                (0.012, 0.016, hinge_z),
                (
                    hinge_x,
                    deck.bay_y_center
                    + (1.0 if y > deck.bay_y_center else -1.0) * cheek_y,
                    hinge_z / 2.0,
                ),
                mats["edge"],
                f"fold_cheek_{index}_{barrel}",
            )

        joint_name = f"end_walls__fold_flat_walls__wall_{index}__fold"
        axis = (0.0, 1.0, 0.0)
        provider = AxisInterface(
            name=f"{joint_name}__provider",
            point=(hinge_x, deck.bay_y_center, hinge_z),
            axis=axis,
            radial=(0.0, 0.0, 1.0),
            radius=_HINGE_R + 0.003,
        )
        consumer = AxisInterface(
            name=f"{joint_name}__consumer",
            point=(0.0, deck.bay_y_center, 0.0),
            axis=axis,
            radial=(0.0, 0.0, 1.0),
            radius=_HINGE_R,
        )
        mate = mate_axes(provider, consumer)
        limits = (
            MotionLimits(effort=6.0, velocity=1.2, lower=0.0, upper=_FOLD_SWING)
            if sign > 0
            else MotionLimits(effort=6.0, velocity=1.2, lower=-_FOLD_SWING, upper=0.0)
        )
        model.articulation(
            joint_name,
            ArticulationType.REVOLUTE,
            parent=tray,
            child=wall,
            origin=mate.origin,
            axis=mate.axis,
            motion_limits=limits,
            motion_properties=MotionProperties(damping=0.3, friction=0.2),
            meta={"mechanism": "fold-flat end wall"},
        )
        register_interface_mate(model, joint_name, mate)
        joints.append(joint_name)
    return joints


def _end_walls_bookend_supports_build(model, tray, r, mats, deck) -> list[str]:
    """bookend_supports fork L47-L123: L-profile ends with a broad foot."""
    for index, sign in enumerate((-1.0, 1.0)):
        x = sign * (r.width_m / 2.0 - r.panel_thickness_m / 2.0)
        _box(
            tray,
            (
                r.panel_thickness_m,
                deck.bay_depth * 0.96,
                deck.wall_height + _WALL_ROOT,
            ),
            (x, deck.bay_y_center, (deck.wall_height - _WALL_ROOT) / 2.0),
            mats["wood"],
            f"end_walls__bookend_supports__wall_{index}",
        )
        _box(
            tray,
            (r.bay_pitch_m * 0.45, deck.bay_depth * 0.80, 0.008),
            (x - sign * r.bay_pitch_m * 0.22, deck.bay_y_center, 0.004),
            mats["edge"],
            f"end_walls__bookend_supports__foot_{index}",
        )
    return []


_END_WALL_BUILDERS = {
    "perforated_end_walls": _end_walls_perforated_end_walls_build,
    "fold_flat_walls": _end_walls_fold_flat_walls_build,
    "bookend_supports": _end_walls_bookend_supports_build,
}


# --------------------------------------------------------------------------- #
# divider_mechanism candidates
# --------------------------------------------------------------------------- #
def _add_guide_rod(tray, r: ResolvedConfig, mats, deck: _Deck, *, name: str) -> float:
    """Round guide rod the sliding dividers ride on.

    The rod runs along +X — the same axis the tilt cradle turns about — so the
    engagement between a divider shoe and the rod is unchanged at every pose.
    """
    rod_z = _ROD_Z
    _cyl(
        tray,
        _ROD_R,
        r.usable_half_x_m * 2.0 + 0.020,
        (0.0, deck.bay_y_center, rod_z),
        mats["steel"],
        name,
        rpy=(0.0, math.pi / 2.0, 0.0),
    )
    for index, sign in enumerate((-1.0, 1.0)):
        _box(
            tray,
            (0.014, 0.016, rod_z + 0.004),
            (
                sign * (r.usable_half_x_m + 0.004),
                deck.bay_y_center,
                (rod_z + 0.004) / 2.0 - 0.004,
            ),
            mats["edge"],
            f"{name}_post_{index}",
        )
    return rod_z


def _add_shoe(part, r: ResolvedConfig, mats, deck: _Deck) -> None:
    """Cylindrical shoe wrapping the guide rod, coaxial with the slide axis."""
    _cyl(
        part,
        _SHOE_R,
        0.024,
        (0.0, deck.bay_y_center, _ROD_Z),
        mats["steel"],
        "rail_shoe",
        rpy=(0.0, math.pi / 2.0, 0.0),
    )


def _divider_panel(part, r: ResolvedConfig, mats, deck: _Deck, *, height: float) -> None:
    base_z = _ROD_Z + _SHOE_R - 0.002
    _box(
        part,
        (r.panel_thickness_m, deck.bay_depth * 0.92, height),
        (0.0, deck.bay_y_center, base_z + height / 2.0),
        mats["panel"],
        "divider_panel",
    )
    _box(
        part,
        (r.panel_thickness_m * 1.8, deck.bay_depth * 0.30, 0.010),
        (0.0, deck.bay_y_center, base_z + height - 0.005),
        mats["edge"],
        "divider_cap",
    )


def _divider_mechanism_sliding_dividers_build(model, tray, r, mats, deck) -> list[str]:
    """001 L254-L338: divider panels sliding along the tray width."""
    joints: list[str] = []
    height = deck.wall_height * 0.78
    _add_guide_rod(tray, r, mats, deck, name="divider_guide_rod")
    for index, x in enumerate(_divider_x_positions(r)):
        divider = model.part(
            f"divider_mechanism__sliding_dividers__divider_{index}",
            meta={"role": "divider", "index": index},
        )
        _divider_panel(divider, r, mats, deck, height=height)
        _add_shoe(divider, r, mats, deck)
        provider = PlaneInterface(
            name=f"deck_bay_{index}",
            point=(x, deck.bay_y_center, deck.deck_top_z),
            normal=(0.0, 0.0, 1.0),
            tangent_u=(1.0, 0.0, 0.0),
            extent=(r.bay_pitch_m, deck.bay_depth),
        )
        consumer = PlaneInterface(
            name=f"divider_foot_{index}",
            point=(0.0, deck.bay_y_center, 0.0),
            normal=(0.0, 0.0, -1.0),
            tangent_u=(1.0, 0.0, 0.0),
            extent=(r.panel_thickness_m, deck.bay_depth * 0.92),
        )
        mate = mate_planes(provider, consumer)
        joint_name = f"divider_mechanism__sliding_dividers__divider_{index}__slide"
        model.articulation(
            joint_name,
            ArticulationType.PRISMATIC,
            parent=tray,
            child=divider,
            origin=mate.origin,
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(
                effort=20.0,
                velocity=0.3,
                lower=-r.divider_travel_m,
                upper=r.divider_travel_m,
            ),
            motion_properties=MotionProperties(damping=0.8, friction=0.4),
            meta={"mechanism": "divider sliding along the tray width"},
        )
        joints.append(joint_name)
    return joints


def _divider_mechanism_liftout_dividers_build(model, tray, r, mats, deck) -> list[str]:
    """liftout fork L112-L360: dividers lift straight out of floor sockets."""
    joints: list[str] = []
    height = deck.wall_height * 0.74
    travel = min(r.divider_travel_m, height * 0.35)
    socket_h = travel + 0.030
    for index, x in enumerate(_divider_x_positions(r)):
        for cheek, sign in enumerate((-1.0, 1.0)):
            _box(
                tray,
                (0.008, deck.bay_depth * 0.40, socket_h),
                (
                    x + sign * (r.panel_thickness_m / 2.0 + 0.004 - _SOCKET_ENGAGE),
                    deck.bay_y_center,
                    socket_h / 2.0 - _DIVIDER_SEAT,
                ),
                mats["edge"],
                f"divider_socket_{index}_{cheek}",
            )
        divider = model.part(
            f"divider_mechanism__liftout_dividers__divider_{index}",
            meta={"role": "divider", "index": index},
        )
        _divider_panel(divider, r, mats, deck, height=height)
        provider = PlaneInterface(
            name=f"deck_socket_{index}",
            point=(x, deck.bay_y_center, deck.deck_top_z),
            normal=(0.0, 0.0, 1.0),
            tangent_u=(1.0, 0.0, 0.0),
            extent=(r.bay_pitch_m, deck.bay_depth),
        )
        consumer = PlaneInterface(
            name=f"divider_foot_{index}",
            point=(0.0, deck.bay_y_center, 0.0),
            normal=(0.0, 0.0, -1.0),
            tangent_u=(1.0, 0.0, 0.0),
            extent=(r.panel_thickness_m, deck.bay_depth * 0.92),
        )
        mate = mate_planes(provider, consumer)
        joint_name = f"divider_mechanism__liftout_dividers__divider_{index}__lift"
        model.articulation(
            joint_name,
            ArticulationType.PRISMATIC,
            parent=tray,
            child=divider,
            origin=mate.origin,
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=15.0, velocity=0.3, lower=0.0, upper=travel),
            motion_properties=MotionProperties(damping=0.6, friction=0.3),
            meta={"mechanism": "divider lifting out of its socket"},
        )
        joints.append(joint_name)
    return joints


def _divider_mechanism_sliding_bookends_build(model, tray, r, mats, deck) -> list[str]:
    """sliding_bookend fork L306-L410: L-profile bookends on a floor rail."""
    joints: list[str] = []
    height = deck.wall_height * 0.70
    _add_guide_rod(tray, r, mats, deck, name="bookend_guide_rod")
    for index, x in enumerate(_divider_x_positions(r)):
        bookend = model.part(
            f"divider_mechanism__sliding_bookends__bookend_{index}",
            meta={"role": "divider", "index": index},
        )
        _box(
            bookend,
            (r.panel_thickness_m, deck.bay_depth * 0.92, height),
            (0.0, deck.bay_y_center, _ROD_Z + _SHOE_R + 0.004 + height / 2.0),
            mats["panel"],
            "divider_panel",
        )
        _box(
            bookend,
            (r.bay_pitch_m * 0.18, deck.bay_depth * 0.80, 0.008),
            (
                r.bay_pitch_m * 0.09,
                deck.bay_y_center,
                _ROD_Z + _SHOE_R + 0.004,
            ),
            mats["edge"],
            "bookend_foot",
        )
        _add_shoe(bookend, r, mats, deck)
        provider = PlaneInterface(
            name=f"deck_rail_{index}",
            point=(x, deck.bay_y_center, deck.deck_top_z),
            normal=(0.0, 0.0, 1.0),
            tangent_u=(1.0, 0.0, 0.0),
            extent=(r.bay_pitch_m, deck.bay_depth),
        )
        consumer = PlaneInterface(
            name=f"bookend_shoe_{index}",
            point=(0.0, deck.bay_y_center, 0.0),
            normal=(0.0, 0.0, -1.0),
            tangent_u=(1.0, 0.0, 0.0),
            extent=(0.026, deck.bay_depth * 0.92),
        )
        mate = mate_planes(provider, consumer)
        joint_name = f"divider_mechanism__sliding_bookends__bookend_{index}__slide"
        model.articulation(
            joint_name,
            ArticulationType.PRISMATIC,
            parent=tray,
            child=bookend,
            origin=mate.origin,
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(
                effort=20.0,
                velocity=0.3,
                lower=-r.divider_travel_m,
                upper=r.divider_travel_m,
            ),
            motion_properties=MotionProperties(damping=0.8, friction=0.4),
            meta={"mechanism": "bookend sliding on the floor rail"},
        )
        joints.append(joint_name)
    return joints


_DIVIDER_BUILDERS = {
    "sliding_dividers": _divider_mechanism_sliding_dividers_build,
    "liftout_dividers": _divider_mechanism_liftout_dividers_build,
    "sliding_bookends": _divider_mechanism_sliding_bookends_build,
}


# --------------------------------------------------------------------------- #
# Book contents (decorative count; not part of core/raw domain)
# --------------------------------------------------------------------------- #
def _add_filed_documents(tray, r: ResolvedConfig, mats, deck: _Deck) -> None:
    """Sparse upright document stacks — the sorter in use.

    The reference sorter is photographed empty, so the contents stay sparse
    (every other bay) and thin, and they keep clear of the divider travel
    envelope so a moving divider never has to push them.
    """
    foot_reach = r.bay_pitch_m * 0.19 if r.divider_mechanism == "sliding_bookends" else 0.0
    free_half = max(
        r.bay_pitch_m / 2.0
        - r.panel_thickness_m
        - r.divider_travel_m
        - foot_reach
        - _BOOK_CLEAR,
        0.006,
    )
    palette = (mats["book_a"], mats["book_b"], mats["book_c"])
    for bay, x_center in enumerate(_bay_x_centers(r)):
        if bay % 2:
            continue
        stacks = int(_clamp(round(free_half * 2.0 / 0.030), 1, 3))
        pitch = (free_half * 2.0) / float(stacks)
        for index in range(stacks):
            x = x_center - free_half + pitch * (float(index) + 0.5)
            height = deck.book_height * (0.72 + 0.06 * float(index % 3))
            _box(
                tray,
                (pitch * 0.62, deck.bay_depth * 0.66, height),
                (x, deck.bay_y_center, height / 2.0),
                palette[(bay + index) % 3],
                f"filed_document_{bay}_{index}",
            )


# --------------------------------------------------------------------------- #
# base_style candidates
# --------------------------------------------------------------------------- #
def _base_style_flat_base_build(model, base, tray, r, mats, deck) -> str:
    """001 L136-L200: the tray sits flat on two full-length floor rails."""
    for index, sign in enumerate((-1.0, 1.0)):
        _box(
            base,
            (r.width_m - 0.020, 0.030, _RAIL_H),
            (0.0, sign * (r.depth_m / 2.0 - 0.030), _RAIL_H / 2.0),
            mats["edge"],
            f"floor_rail_{index}",
        )
    _box(
        base,
        (r.width_m - 0.020, r.depth_m - 0.070, _RAIL_H),
        (0.0, 0.0, _RAIL_H / 2.0),
        mats["edge"],
        "floor_cross_rail",
    )
    joint_name = "base_style__flat_base__deck_mount"
    model.articulation(
        joint_name,
        ArticulationType.FIXED,
        parent=base,
        child=tray,
        origin=Origin(xyz=(0.0, 0.0, r.deck_z_m)),
        meta={"mechanism": "tray seated on its floor rails"},
    )
    return joint_name


def _base_style_footed_base_build(model, base, tray, r, mats, deck) -> str:
    """footed_base fork L59-L296: four feet lift the tray off the desk."""
    for index, (sx, sy) in enumerate(((-1.0, -1.0), (-1.0, 1.0), (1.0, -1.0), (1.0, 1.0))):
        _box(
            base,
            (0.045, 0.038, _FOOT_H),
            (
                sx * (r.width_m / 2.0 - 0.040),
                sy * (r.depth_m / 2.0 - 0.032),
                _FOOT_H / 2.0,
            ),
            mats["edge"],
            f"foot_{index}",
        )
    for index, sign in enumerate((-1.0, 1.0)):
        _box(
            base,
            (r.width_m - 0.060, 0.026, 0.014),
            (0.0, sign * (r.depth_m / 2.0 - 0.032), _FOOT_H - 0.007),
            mats["edge"],
            f"foot_rail_{index}",
        )
    _box(
        base,
        (0.030, r.depth_m - 0.064, 0.014),
        (0.0, 0.0, _FOOT_H - 0.007),
        mats["edge"],
        "foot_cross_rail",
    )
    joint_name = "base_style__footed_base__deck_mount"
    model.articulation(
        joint_name,
        ArticulationType.FIXED,
        parent=base,
        child=tray,
        origin=Origin(xyz=(0.0, 0.0, r.deck_z_m)),
        meta={"mechanism": "tray seated on its feet"},
    )
    return joint_name


_BASE_BUILDERS = {
    "flat_base": _base_style_flat_base_build,
    "footed_base": _base_style_footed_base_build,
}


# --------------------------------------------------------------------------- #
# Assembly
# --------------------------------------------------------------------------- #
def build_pictureX_0611_Bookshelf_with_books(
    config: Config | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config or config_from_seed(0))
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={
            "category": "pictureX_0611_Bookshelf_with_books",
            "identified_object": "desktop file sorter with perforated ends and movable dividers",
            "slot_choices": slot_choices_for_config(r),
            "source_layout": "a deck between two perforated end walls, split into upright bays by N dividers",
        },
    )
    mats = _materials(model)
    base = model.part(
        f"base_style__{r.base_style}__base",
        meta={"role": "base_body", "base": r.base_style},
    )
    tray = model.part(
        f"tray_body__{r.tray_body}__tray",
        meta={"role": "tray", "body": r.tray_body},
    )
    deck = _TRAY_BUILDERS[r.tray_body](tray, r, mats)
    _END_WALL_BUILDERS[r.end_walls](model, tray, r, mats, deck)
    _add_filed_documents(tray, r, mats, deck)
    _BASE_BUILDERS[r.base_style](model, base, tray, r, mats, deck)
    _DIVIDER_BUILDERS[r.divider_mechanism](model, tray, r, mats, deck)
    return model


# --------------------------------------------------------------------------- #
# Author tests / category anchors
# --------------------------------------------------------------------------- #
def _parts_by_role(model: ArticulatedObject, role: str):
    return [part for part in model.parts if part.meta.get("role") == role]


def _visual_names(part) -> set[str]:
    return {visual.name for visual in part.visuals}


def run_pictureX_0611_Bookshelf_with_books_tests(
    model: ArticulatedObject,
    config: Config,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)

    bases = _parts_by_role(model, "base_body")
    trays = _parts_by_role(model, "tray")
    dividers = _parts_by_role(model, "divider")
    end_walls = _parts_by_role(model, "end_wall")

    ctx.check(
        "category_anchor: one grounded base carries one sorter body",
        len(bases) == 1 and len(trays) == 1,
        details=f"base={len(bases)}, tray={len(trays)}",
    )
    tray = trays[0]
    names = _visual_names(tray)
    ctx.check(
        "category_anchor: the sorter has a deck board",
        any("deck_board" in name or "tier_board" in name for name in names),
        details=f"deck visuals={[n for n in names if 'deck' in n or 'board' in n]}",
    )
    ctx.check(
        "category_anchor: two end walls close the sorter bays",
        len([n for n in names if "wall" in n]) >= 2 or len(end_walls) == 2,
        details=f"wall visuals={[n for n in names if 'wall' in n]}, wall parts={len(end_walls)}",
    )
    filed = [n for n in names if n.startswith("filed_document_")]
    ctx.check(
        "category_anchor: the sorter carries upright filed contents",
        len(filed) >= 1,
        details=f"filed documents={len(filed)}",
    )
    if r.end_walls == "perforated_end_walls":
        ctx.check(
            "category_anchor: the moulded end walls are perforated",
            len([n for n in names if "perforated_end_walls__wall" in n and "rim" not in n]) == 2,
            details=f"perforated panels={[n for n in names if 'perforated' in n]}",
        )
    ctx.check(
        "category_anchor: N movable dividers split the sorter bays",
        len(dividers) == r.divider_count,
        details=f"divider parts={len(dividers)} expected={r.divider_count}",
    )

    movers = [
        joint
        for joint in model.articulations
        if joint.articulation_type != ArticulationType.FIXED
    ]
    ctx.check(
        "category_anchor: the sorter has at least one real non-fixed joint",
        len(movers) >= 1,
        details=f"non-fixed joints={[joint.name for joint in movers]}",
    )
    ctx.check(
        "bays stay wide enough for filed contents",
        r.bay_pitch_m - r.panel_thickness_m >= _MIN_BAY - 1e-4,
        details=f"bay pitch={r.bay_pitch_m:.3f}",
    )

    for divider in dividers:
        joint = next(joint for joint in model.articulations if joint.child == divider.name)
        move_value = max((joint.motion_limits.lower, joint.motion_limits.upper), key=abs)
        rest = ctx.part_world_position(divider)
        with ctx.pose({joint: move_value}):
            moved = ctx.part_world_position(divider)
        ctx.check(
            f"{divider.name} moves along its declared axis",
            rest is not None
            and moved is not None
            and max(abs(moved[index] - rest[index]) for index in range(3))
            > 0.5 * abs(move_value),
            details=f"rest={rest}, moved={moved}",
        )

    for wall in end_walls:
        joint = next(joint for joint in model.articulations if joint.child == wall.name)
        fold_value = max((joint.motion_limits.lower, joint.motion_limits.upper), key=abs)
        upright = ctx.part_world_aabb(wall)
        with ctx.pose({joint: fold_value}):
            folded = ctx.part_world_aabb(wall)
        leaf_h = None if upright is None else upright[1][2] - upright[0][2]
        ctx.check(
            f"{wall.name} folds down flat",
            upright is not None
            and folded is not None
            and (
                folded[1][2] < upright[1][2] - 0.3 * leaf_h
                or (folded[1][0] - folded[0][0]) > (upright[1][0] - upright[0][0]) + 0.3 * leaf_h
            ),
            details=f"upright={upright}, folded={folded}",
        )

    return ctx.report()


TEMPLATE_CORNERS = (
    corner_case(
        "widest_sorter_max_dividers_liftout",
        {
            "tray_body": "flat_tray",
            "end_walls": "fold_flat_walls",
            "divider_mechanism": "liftout_dividers",
            "base_style": "footed_base",
            "divider_count": 7,
            "width_m": 0.55,
            "depth_m": 0.32,
            "wall_height_m": 0.26,
            "panel_thickness_m": 0.016,
        },
        reason="maximum divider count lifting out of the widest sorter with folding ends",
    ),
    corner_case(
        "smallest_incline_rack_with_sliding_bookends",
        {
            "tray_body": "incline_rack",
            "end_walls": "bookend_supports",
            "divider_mechanism": "sliding_bookends",
            "base_style": "footed_base",
            "divider_count": 2,
            "width_m": 0.28,
            "depth_m": 0.14,
            "wall_height_m": 0.13,
            "panel_thickness_m": 0.008,
        },
        reason="smallest body with the shallowest pitched deck and sliding bookends",
    ),
    corner_case(
        "cube_grid_dense_dividers_perforated",
        {
            "tray_body": "cube_grid",
            "end_walls": "perforated_end_walls",
            "divider_mechanism": "sliding_dividers",
            "base_style": "flat_base",
            "divider_count": 7,
            "width_m": 0.55,
            "depth_m": 0.30,
            "wall_height_m": 0.26,
            "panel_thickness_m": 0.016,
        },
        reason="densest divider pack under the cube-grid mid board with perforated ends",
    ),
    corner_case(
        "perforated_ends_min_panel",
        {
            "tray_body": "flat_tray",
            "end_walls": "perforated_end_walls",
            "divider_mechanism": "liftout_dividers",
            "base_style": "flat_base",
            "divider_count": 2,
            "width_m": 0.28,
            "depth_m": 0.14,
            "wall_height_m": 0.13,
            "panel_thickness_m": 0.008,
        },
        reason="smallest perforated panel the slot grid must still fit inside its frame",
    ),
    corner_case(
        "stepped_tiers_liftout_min_size",
        {
            "tray_body": "stepped_tiers",
            "end_walls": "bookend_supports",
            "divider_mechanism": "liftout_dividers",
            "base_style": "flat_base",
            "divider_count": 2,
            "width_m": 0.28,
            "depth_m": 0.14,
            "wall_height_m": 0.13,
            "panel_thickness_m": 0.008,
        },
        reason="shallowest stepped deck with the shortest lift-out sockets",
    ),
    corner_case(
        "cube_grid_perforated_min_body",
        {
            "tray_body": "cube_grid",
            "end_walls": "perforated_end_walls",
            "divider_mechanism": "sliding_dividers",
            "base_style": "flat_base",
            "divider_count": 7,
            "width_m": 0.28,
            "depth_m": 0.14,
            "wall_height_m": 0.13,
            "panel_thickness_m": 0.008,
        },
        reason=(
            "shortest perforated panel in the fleet: the cube grid's mid board "
            "crushes the end wall, and the slot grid must still fit inside its "
            "own pitch"
        ),
    ),
    corner_case(
        "cube_grid_fold_flat_shortest_wall",
        {
            "tray_body": "cube_grid",
            "end_walls": "fold_flat_walls",
            "divider_mechanism": "sliding_dividers",
            "base_style": "flat_base",
            "divider_count": 7,
            "width_m": 0.28,
            "depth_m": 0.32,
            "wall_height_m": 0.13,
            "panel_thickness_m": 0.016,
        },
        reason=(
            "thickest panel on the shortest wall the cube grid leaves: the "
            "folding leaf must stay taller than it is thick and still fold"
        ),
    ),
    corner_case(
        "mesh_basket_max_dividers_folding_ends",
        {
            "tray_body": "mesh_basket",
            "end_walls": "fold_flat_walls",
            "divider_mechanism": "sliding_bookends",
            "base_style": "footed_base",
            "divider_count": 7,
            "width_m": 0.55,
            "depth_m": 0.16,
            "wall_height_m": 0.26,
            "panel_thickness_m": 0.010,
        },
        reason="lattice walls with the maximum bookend count on the shallowest basket",
    ),
)


__all__ = [
    "Config",
    "ResolvedConfig",
    "TEMPLATE_CORNERS",
    "TEMPLATE_DOMAIN",
    "build_pictureX_0611_Bookshelf_with_books",
    "config_from_seed",
    "resolve_config",
    "run_pictureX_0611_Bookshelf_with_books_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
]
