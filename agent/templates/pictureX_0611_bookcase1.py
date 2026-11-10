# SPDX-License-Identifier: Apache-2.0

"""Self-contained 'bookcase1' template — tall household bookcases / display cases.

Rebuilt from the three ``pictureX/0611/bookcase1`` origin records and the accepted
forks listed in
``articraft_template_authoring/source_maps/pictureX_0611_bookcase1.md``.

Category identity: a tall household bookcase or display case — vertical side
boards, a stack of horizontal shelves, a back, and a lower cabinet band that
carries the moving hardware.  Four independent structural axes:

* ``case_frame``      — the load-bearing case family: gallery side cheeks (001),
  cubby columns (002), panelled side frames (003), and the corner-wing,
  cube-grid, raked-ladder and barrister-stack forks.
* ``lower_front``     — what closes the front and with which joint: raised-panel
  doors, framed glass doors, base drawers, a top-pivot glazed flap, or an open
  cubby base with one retained leaf.
* ``shelf_mechanism`` — fixed shelf boards versus prismatic adjustable shelves.
* ``base_style``      — plinth, turned legs, or a recessed toe kick.

Every ``case_frame`` exports the same aperture interface (front plane, aperture
half-width and centre, an upper and a lower band in z) and its own shelf rows;
``lower_front`` consumes only that aperture, so all 7 x 5 x 2 x 3 = 210
combinations build without a compatibility gate.

Coordinate frame: +X = width (centred on 0), +Y = depth with the front face at
+depth/2, +Z = height with the floor at z = 0.

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
    TemplateDomain,
    TestContext,
    TestReport,
    component_slot,
    corner_case,
    mate_axes,
    mate_planes,
    multiplicity_slot,
    register_interface_mate,
)

CaseFrame = Literal[
    "gallery_cheeks",
    "cubby_columns",
    "panelled_side_frame",
    "corner_wing",
    "cube_grid",
    "raked_ladder",
    "barrister_stack",
]
LowerFront = Literal[
    "raised_panel_doors",
    "framed_glass_doors",
    "base_drawers",
    "flip_up_glass_flap",
    "open_cubby_base",
]
ShelfMechanism = Literal["fixed_shelves", "adjustable_shelves"]
BaseStyle = Literal["plinth_base", "turned_legs", "toe_kick"]

CASE_FRAMES: tuple[CaseFrame, ...] = (
    "gallery_cheeks",
    "cubby_columns",
    "panelled_side_frame",
    "corner_wing",
    "cube_grid",
    "raked_ladder",
    "barrister_stack",
)
LOWER_FRONTS: tuple[LowerFront, ...] = (
    "raised_panel_doors",
    "framed_glass_doors",
    "base_drawers",
    "flip_up_glass_flap",
    "open_cubby_base",
)
SHELF_MECHANISMS: tuple[ShelfMechanism, ...] = ("fixed_shelves", "adjustable_shelves")
BASE_STYLES: tuple[BaseStyle, ...] = ("plinth_base", "turned_legs", "toe_kick")
SHELF_COUNTS: tuple[int, ...] = (2, 3, 5, 7)

TEMPLATE_DOMAIN = TemplateDomain(
    (
        component_slot("case_frame", CASE_FRAMES),
        component_slot("lower_front", LOWER_FRONTS),
        component_slot("shelf_mechanism", SHELF_MECHANISMS),
        component_slot("base_style", BASE_STYLES),
        multiplicity_slot("shelf_count", SHELF_COUNTS, item_slot="shelf_mechanism"),
    )
)

# Independent continuous parameters (honest dimensions; not core/raw domain).
_WIDTH_RANGE = (0.60, 1.45)
_DEPTH_RANGE = (0.24, 0.52)
_HEIGHT_RANGE = (1.10, 2.20)
_SHELF_THICKNESS_RANGE = (0.016, 0.030)

_PANEL_T = 0.020
_TOP_T = 0.034
_BACK_T = 0.014
_DOOR_T = 0.028
_GLASS_T = 0.006
_DOOR_PROUD = 0.008
_DOOR_GAP = 0.012
_FACE_POST_W = 0.020
_FACE_POST_D = 0.022
_HINGE_R = 0.009
_HINGE_LEN = 0.090
_HINGE_PIN_R = 0.0020
_PILASTER_T = 0.012
_PILASTER_ENGAGE = 0.002
_RUNNER_T = 0.020
_RUNNER_ENGAGE = 0.002
_SHELF_TRAVEL = 0.050
_DRAWER_WALL = 0.014
_DOOR_SWING = 1.62
_FLAP_SWING = 1.30
_MIN_CLEAR_PITCH = 0.060

# Fronts whose mechanism consumes interior volume at the bottom of the case.
DRAWER_FRONTS: frozenset[str] = frozenset({"base_drawers"})


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _reserved_lower(lower_front: str, body_span: float) -> float:
    """Interior height the front assembly consumes at the bottom of the case."""
    if lower_front not in DRAWER_FRONTS:
        return 0.0
    return _clamp(0.34 * body_span, 0.22, 0.50)


@dataclass(frozen=True)
class Config:
    case_frame: CaseFrame = "panelled_side_frame"
    lower_front: LowerFront = "raised_panel_doors"
    shelf_mechanism: ShelfMechanism = "fixed_shelves"
    base_style: BaseStyle = "plinth_base"
    shelf_count: int = 3
    width_m: float | None = None
    depth_m: float | None = None
    height_m: float | None = None
    shelf_thickness_m: float | None = None
    name: str = "pictureX_0611_bookcase1"


@dataclass(frozen=True)
class ResolvedConfig:
    case_frame: CaseFrame
    lower_front: LowerFront
    shelf_mechanism: ShelfMechanism
    base_style: BaseStyle
    shelf_count: int
    width_m: float
    depth_m: float
    height_m: float
    shelf_thickness_m: float
    base_lift_m: float
    body_z0_m: float
    body_z1_m: float
    interior_half_x_m: float
    interior_depth_m: float
    shelf_pitch_m: float
    reserved_lower_m: float
    shelf_zone_lo_m: float
    name: str


def config_from_seed(seed: int) -> Config:
    choices = TEMPLATE_DOMAIN.sample(seed)
    rng = random.Random(seed ^ 0xB1C1_2026)
    return Config(
        case_frame=choices["case_frame"],
        lower_front=choices["lower_front"],
        shelf_mechanism=choices["shelf_mechanism"],
        base_style=choices["base_style"],
        shelf_count=choices["shelf_count"],
        width_m=round(rng.uniform(*_WIDTH_RANGE), 4),
        depth_m=round(rng.uniform(*_DEPTH_RANGE), 4),
        height_m=round(rng.uniform(*_HEIGHT_RANGE), 4),
        shelf_thickness_m=round(rng.uniform(*_SHELF_THICKNESS_RANGE), 4),
    )


def _range_check(name: str, value: float, bounds: tuple[float, float]) -> None:
    low, high = bounds
    if not low <= value <= high:
        raise ValueError(f"{name} must be in [{low}, {high}], got {value}")


def _base_lift(base_style: BaseStyle, case_frame: CaseFrame, height: float) -> float:
    base = {"plinth_base": 0.070, "turned_legs": 0.130, "toe_kick": 0.090}[base_style]
    if case_frame == "barrister_stack":
        base = max(0.050, base * 0.70)
    if case_frame == "gallery_cheeks":
        base += 0.030
    return _clamp(base, 0.045, 0.30 * height)


def resolve_config(config: Config) -> ResolvedConfig:
    TEMPLATE_DOMAIN.validate(
        {
            "case_frame": config.case_frame,
            "lower_front": config.lower_front,
            "shelf_mechanism": config.shelf_mechanism,
            "base_style": config.base_style,
            "shelf_count": config.shelf_count,
        }
    )
    width = 0.920 if config.width_m is None else float(config.width_m)
    depth = 0.380 if config.depth_m is None else float(config.depth_m)
    height = 1.850 if config.height_m is None else float(config.height_m)
    shelf_t = 0.022 if config.shelf_thickness_m is None else float(config.shelf_thickness_m)
    _range_check("width_m", width, _WIDTH_RANGE)
    _range_check("depth_m", depth, _DEPTH_RANGE)
    _range_check("height_m", height, _HEIGHT_RANGE)
    _range_check("shelf_thickness_m", shelf_t, _SHELF_THICKNESS_RANGE)

    lift = _base_lift(config.base_style, config.case_frame, height)
    count_for_height = int(config.shelf_count)
    min_pitch = shelf_t + _MIN_CLEAR_PITCH
    for _ in range(4):
        span = max(height - _TOP_T - lift, 0.05)
        reserved = _reserved_lower(config.lower_front, span)
        required_height = (
            lift + _TOP_T + reserved + min_pitch * float(count_for_height + 1) + 0.002
        )
        if height >= required_height - 1e-9:
            break
        height = required_height
    body_z0 = lift
    body_z1 = height - _TOP_T
    reserved = _reserved_lower(config.lower_front, body_z1 - body_z0)
    shelf_zone_lo = body_z0 + reserved
    interior_half = width / 2.0 - _PANEL_T
    interior_depth = depth - _BACK_T
    count = int(config.shelf_count)
    pitch = (body_z1 - shelf_zone_lo) / float(count + 1)
    return ResolvedConfig(
        case_frame=config.case_frame,
        lower_front=config.lower_front,
        shelf_mechanism=config.shelf_mechanism,
        base_style=config.base_style,
        shelf_count=count,
        width_m=width,
        depth_m=depth,
        height_m=height,
        shelf_thickness_m=shelf_t,
        base_lift_m=lift,
        body_z0_m=body_z0,
        body_z1_m=body_z1,
        interior_half_x_m=interior_half,
        interior_depth_m=interior_depth,
        shelf_pitch_m=pitch,
        reserved_lower_m=reserved,
        shelf_zone_lo_m=shelf_zone_lo,
        name=config.name,
    )


def slot_choices_for_config(config: Config | ResolvedConfig) -> tuple[tuple[str, object], ...]:
    return (
        ("case_frame", config.case_frame),
        ("lower_front", config.lower_front),
        ("shelf_mechanism", config.shelf_mechanism),
        ("base_style", config.base_style),
        ("shelf_count", int(config.shelf_count)),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, object], ...]:
    return slot_choices_for_config(config_from_seed(seed))


def _materials(model: ArticulatedObject) -> dict[str, str]:
    model.material("case_wood", rgba=(0.36, 0.24, 0.14, 1.0))
    model.material("case_edge", rgba=(0.28, 0.18, 0.10, 1.0))
    model.material("interior_wood", rgba=(0.48, 0.35, 0.21, 1.0))
    model.material("back_wood", rgba=(0.22, 0.15, 0.09, 1.0))
    model.material("smoked_glass", rgba=(0.60, 0.68, 0.68, 0.35))
    model.material("aged_brass", rgba=(0.67, 0.56, 0.43, 1.0))
    return {
        "wood": "case_wood",
        "edge": "case_edge",
        "interior": "interior_wood",
        "back": "back_wood",
        "glass": "smoked_glass",
        "brass": "aged_brass",
    }


def _box(part, size, xyz, material: str, name: str, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(Box(size), origin=Origin(xyz=xyz, rpy=rpy), material=material, name=name, material_class_id="wood.veneer_panel")


def _cyl(part, radius, length, xyz, material: str, name: str, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=Origin(xyz=xyz, rpy=rpy),
        material=material,
        name=name, material_class_id="metal.brass_aged",
    )


@dataclass(frozen=True)
class _ShelfRow:
    z: float
    x_center: float
    half_width: float
    y_center: float
    depth: float


@dataclass(frozen=True)
class _Frame:
    """The front-aperture interface every carcass_form must provide."""

    front_y: float
    aperture_half_x: float
    aperture_x_center: float
    upper_band: tuple[float, float]
    lower_band: tuple[float, float]
    shelf_rows: tuple[_ShelfRow, ...]
    side_support_x: tuple[float, float]
    pilaster_half_x: float


def _shelf_z_values(r: ResolvedConfig) -> list[float]:
    pitch = r.shelf_pitch_m
    return [r.shelf_zone_lo_m + pitch * float(index + 1) for index in range(r.shelf_count)]


def _split_z(r: ResolvedConfig, fraction: float) -> float:
    """Aperture split: the reserved drawer band wins over the form's own split."""
    if r.reserved_lower_m > 0.0:
        return r.body_z0_m + r.reserved_lower_m
    return r.body_z0_m + fraction * (r.body_z1_m - r.body_z0_m)


def _row_span(r: ResolvedConfig, front_y: float, back_y: float) -> tuple[float, float]:
    """Shelf board depth and y centre, clear of the back panel, flush at the front."""
    back = back_y + _BACK_T + 0.006
    depth = max(front_y - back, 0.08)
    return depth, back + depth / 2.0


def _bands(r: ResolvedConfig, split: float) -> tuple[tuple[float, float], tuple[float, float]]:
    lower = (r.body_z0_m + 0.010, split - 0.010)
    upper = (split + 0.010, r.body_z1_m - 0.010)
    return upper, lower


# --------------------------------------------------------------------------- #
# carcass_form candidates
# --------------------------------------------------------------------------- #
def _add_side_supports(
    carcass,
    r: ResolvedConfig,
    mats: dict[str, str],
    *,
    half_x: float,
    z0: float,
    z1: float,
    depth: float,
    y_center: float,
    prefix: str = "",
) -> None:
    for index, sign in enumerate((-1.0, 1.0)):
        _box(
            carcass,
            (_PANEL_T, depth, z1 - z0),
            (sign * (half_x - _PANEL_T / 2.0), y_center, (z0 + z1) / 2.0),
            mats["wood"],
            f"{prefix}side_support_{index}",
        )


def _add_top_and_deck(
    carcass,
    r: ResolvedConfig,
    mats: dict[str, str],
    *,
    half_x: float,
    depth: float,
    y_center: float,
    z_top: float,
    z_deck: float,
) -> None:
    _box(
        carcass,
        (half_x * 2.0, depth, _TOP_T),
        (0.0, y_center, z_top + _TOP_T / 2.0),
        mats["edge"],
        "top_cap",
    )
    _box(
        carcass,
        (half_x * 2.0 - 2.0 * _PANEL_T, depth, r.shelf_thickness_m),
        (0.0, y_center, z_deck + r.shelf_thickness_m / 2.0),
        mats["wood"],
        "bottom_deck",
    )


# --------------------------------------------------------------------------- #
# case_frame candidates
# --------------------------------------------------------------------------- #
def _case_frame_gallery_cheeks_build(carcass, r: ResolvedConfig, mats) -> _Frame:
    """001 L28-L272: side cheeks whose rising gallery profile steps back."""
    half_x = r.width_m / 2.0
    depth = r.depth_m
    _add_side_supports(
        carcass,
        r,
        mats,
        half_x=half_x,
        z0=r.body_z0_m,
        z1=r.body_z1_m,
        depth=depth,
        y_center=0.0,
    )
    # Three stepped cheek returns: the gallery rises from the front edge and
    # steps back toward the top, as in 001.png.
    steps = 3
    for index in range(steps):
        frac = float(index + 1) / float(steps + 1)
        step_depth = depth * (0.30 - 0.06 * index)
        for side, sign in enumerate((-1.0, 1.0)):
            _box(
                carcass,
                (0.016, max(step_depth, 0.05), 0.030),
                (
                    sign * (half_x - _PANEL_T - 0.008),
                    depth / 2.0 - max(step_depth, 0.05) / 2.0,
                    r.body_z0_m + (r.body_z1_m - r.body_z0_m) * frac,
                ),
                mats["edge"],
                f"gallery_step_{index}_{side}",
            )
    _add_top_and_deck(
        carcass,
        r,
        mats,
        half_x=half_x,
        depth=depth,
        y_center=0.0,
        z_top=r.body_z1_m,
        z_deck=r.body_z0_m,
    )
    _box(
        carcass,
        (half_x * 2.0, 0.018, 0.070),
        (0.0, -depth / 2.0 + 0.030, r.body_z1_m + _TOP_T + 0.035),
        mats["edge"],
        "gallery_rail",
    )
    split = _split_z(r, 0.34)
    upper, lower = _bands(r, split)
    row_depth, row_y = _row_span(r, depth / 2.0, -depth / 2.0)
    rows = tuple(
        _ShelfRow(
            z=z,
            x_center=0.0,
            half_width=r.interior_half_x_m,
            y_center=row_y,
            depth=row_depth,
        )
        for z in _shelf_z_values(r)
    )
    return _Frame(
        front_y=depth / 2.0,
        aperture_half_x=half_x - _PANEL_T,
        aperture_x_center=0.0,
        upper_band=upper,
        lower_band=lower,
        shelf_rows=rows,
        side_support_x=(-half_x + _PANEL_T, half_x - _PANEL_T),
        pilaster_half_x=r.interior_half_x_m,
    )


def _column_count(r: ResolvedConfig) -> int:
    return int(_clamp(round(r.width_m / 0.40), 2, 4))


def _case_frame_cubby_columns_build(carcass, r: ResolvedConfig, mats) -> _Frame:
    """002 L158-L308: full-height column dividers splitting the case into cubbies."""
    half_x = r.width_m / 2.0
    depth = r.depth_m
    _add_side_supports(
        carcass,
        r,
        mats,
        half_x=half_x,
        z0=r.body_z0_m,
        z1=r.body_z1_m,
        depth=depth,
        y_center=0.0,
    )
    _add_top_and_deck(
        carcass,
        r,
        mats,
        half_x=half_x,
        depth=depth,
        y_center=0.0,
        z_top=r.body_z1_m,
        z_deck=r.body_z0_m,
    )
    cols = _column_count(r)
    col_w = (r.interior_half_x_m * 2.0) / float(cols)
    for index in range(1, cols):
        x = -r.interior_half_x_m + col_w * float(index)
        _box(
            carcass,
            (_PANEL_T, depth - _BACK_T, r.body_z1_m - r.body_z0_m),
            (x, -_BACK_T / 2.0, (r.body_z0_m + r.body_z1_m) / 2.0),
            mats["wood"],
            f"column_divider_{index - 1}",
        )
    split = _split_z(r, 0.32)
    upper, lower = _bands(r, split)
    row_depth, row_y = _row_span(r, depth / 2.0, -depth / 2.0)
    rows = tuple(
        _ShelfRow(
            z=z,
            x_center=-r.interior_half_x_m + col_w * (float(index % cols) + 0.5),
            half_width=col_w / 2.0 - _PANEL_T / 2.0,
            y_center=row_y,
            depth=row_depth,
        )
        for index, z in enumerate(_shelf_z_values(r))
    )
    return _Frame(
        front_y=depth / 2.0,
        aperture_half_x=col_w / 2.0 - 0.006,
        aperture_x_center=-r.interior_half_x_m + col_w * 0.5,
        upper_band=upper,
        lower_band=lower,
        shelf_rows=rows,
        side_support_x=(-half_x + _PANEL_T, half_x - _PANEL_T),
        pilaster_half_x=r.interior_half_x_m,
    )


def _case_frame_panelled_side_frame_build(carcass, r: ResolvedConfig, mats) -> _Frame:
    """003 L32-L350: stile-and-rail raised frame treatment on both side panels."""
    half_x = r.width_m / 2.0
    depth = r.depth_m
    _add_side_supports(
        carcass,
        r,
        mats,
        half_x=half_x,
        z0=r.body_z0_m,
        z1=r.body_z1_m,
        depth=depth,
        y_center=0.0,
    )
    span_z = r.body_z1_m - r.body_z0_m
    z_mid = (r.body_z0_m + r.body_z1_m) / 2.0
    for side, sign in enumerate((-1.0, 1.0)):
        x = sign * (half_x - 0.004)
        _box(
            carcass,
            (0.010, 0.060, span_z),
            (x, depth / 2.0 - 0.040, z_mid),
            mats["edge"],
            f"side_front_stile_{side}",
        )
        _box(
            carcass,
            (0.010, 0.060, span_z),
            (x, -depth / 2.0 + 0.040, z_mid),
            mats["edge"],
            f"side_rear_stile_{side}",
        )
        for index, z in enumerate((r.body_z0_m + 0.050, r.body_z1_m - 0.050)):
            _box(
                carcass,
                (0.010, depth - 0.100, 0.055),
                (x, 0.0, z),
                mats["edge"],
                f"side_rail_{side}_{index}",
            )
    _add_top_and_deck(
        carcass,
        r,
        mats,
        half_x=half_x,
        depth=depth,
        y_center=0.0,
        z_top=r.body_z1_m,
        z_deck=r.body_z0_m,
    )
    split = _split_z(r, 0.36)
    upper, lower = _bands(r, split)
    row_depth, row_y = _row_span(r, depth / 2.0, -depth / 2.0)
    rows = tuple(
        _ShelfRow(
            z=z,
            x_center=0.0,
            half_width=r.interior_half_x_m,
            y_center=row_y,
            depth=row_depth,
        )
        for z in _shelf_z_values(r)
    )
    return _Frame(
        front_y=depth / 2.0,
        aperture_half_x=half_x - _PANEL_T,
        aperture_x_center=0.0,
        upper_band=upper,
        lower_band=lower,
        shelf_rows=rows,
        side_support_x=(-half_x + _PANEL_T, half_x - _PANEL_T),
        pilaster_half_x=r.interior_half_x_m,
    )


def _case_frame_corner_wing_build(carcass, r: ResolvedConfig, mats) -> _Frame:
    """corner fork L80-L400: L-plan case with a perpendicular return wing."""
    half_x = r.width_m / 2.0
    depth = r.depth_m
    wing = max(0.22, half_x * 0.9)
    z_mid = (r.body_z0_m + r.body_z1_m) / 2.0
    _box(
        carcass,
        (_PANEL_T, depth, r.body_z1_m - r.body_z0_m),
        (-half_x + _PANEL_T / 2.0, -depth / 2.0 + wing / 2.0, z_mid),
        mats["wood"],
        "side_support_0",
    )
    _box(
        carcass,
        (_PANEL_T, depth, r.body_z1_m - r.body_z0_m),
        (half_x - _PANEL_T / 2.0, 0.0, z_mid),
        mats["wood"],
        "side_support_1",
    )
    _box(
        carcass,
        (half_x * 2.0, _PANEL_T, r.body_z1_m - r.body_z0_m),
        (0.0, -depth / 2.0 + _PANEL_T / 2.0, z_mid),
        mats["back"],
        "return_wing_panel",
    )
    _add_top_and_deck(
        carcass,
        r,
        mats,
        half_x=half_x,
        depth=depth,
        y_center=0.0,
        z_top=r.body_z1_m,
        z_deck=r.body_z0_m,
    )
    split = _split_z(r, 0.34)
    upper, lower = _bands(r, split)
    row_depth, row_y = _row_span(r, depth / 2.0 - 0.026, -depth / 2.0)
    rows = tuple(
        _ShelfRow(
            z=z,
            x_center=0.0,
            half_width=r.interior_half_x_m,
            y_center=row_y,
            depth=row_depth,
        )
        for z in _shelf_z_values(r)
    )
    return _Frame(
        front_y=depth / 2.0,
        aperture_half_x=(half_x - _PANEL_T) * 0.52,
        aperture_x_center=(half_x - _PANEL_T) * 0.44,
        upper_band=upper,
        lower_band=lower,
        shelf_rows=rows,
        side_support_x=(-half_x + _PANEL_T, half_x - _PANEL_T),
        pilaster_half_x=r.interior_half_x_m,
    )


def _case_frame_cube_grid_build(carcass, r: ResolvedConfig, mats) -> _Frame:
    """cube_grid fork L52-L212: rows x cols cube matrix of boards and dividers."""
    half_x = r.width_m / 2.0
    depth = r.depth_m
    _add_side_supports(
        carcass,
        r,
        mats,
        half_x=half_x,
        z0=r.body_z0_m,
        z1=r.body_z1_m,
        depth=depth,
        y_center=0.0,
    )
    _add_top_and_deck(
        carcass,
        r,
        mats,
        half_x=half_x,
        depth=depth,
        y_center=0.0,
        z_top=r.body_z1_m,
        z_deck=r.body_z0_m,
    )
    cols = int(_clamp(round(r.width_m / 0.36), 2, 4))
    cell_w = (r.interior_half_x_m * 2.0) / float(cols)
    for col in range(1, cols):
        x = -r.interior_half_x_m + cell_w * float(col)
        _box(
            carcass,
            (_PANEL_T, depth - _BACK_T, r.body_z1_m - r.body_z0_m),
            (x, -_BACK_T / 2.0, (r.body_z0_m + r.body_z1_m) / 2.0),
            mats["wood"],
            f"cell_divider_{col - 1}",
        )
    split = _split_z(r, 0.30)
    upper, lower = _bands(r, split)
    row_depth, row_y = _row_span(r, depth / 2.0, -depth / 2.0)
    rows = tuple(
        _ShelfRow(
            z=z,
            x_center=-r.interior_half_x_m + cell_w * (float(index % cols) + 0.5),
            half_width=cell_w / 2.0 - _PANEL_T / 2.0,
            y_center=row_y,
            depth=row_depth,
        )
        for index, z in enumerate(_shelf_z_values(r))
    )
    return _Frame(
        front_y=depth / 2.0,
        aperture_half_x=cell_w / 2.0 - 0.006,
        aperture_x_center=-r.interior_half_x_m + cell_w * 0.5,
        upper_band=upper,
        lower_band=lower,
        shelf_rows=rows,
        side_support_x=(-half_x + _PANEL_T, half_x - _PANEL_T),
        pilaster_half_x=r.interior_half_x_m,
    )


def _case_frame_raked_ladder_build(carcass, r: ResolvedConfig, mats) -> _Frame:
    """ladder fork L37-L344: raked side panels tapering over a vertical base box."""
    half_x = r.width_m / 2.0
    depth = r.depth_m
    box_top = r.body_z0_m + max(
        _clamp(0.32 * (r.body_z1_m - r.body_z0_m), 0.26, 0.60),
        r.reserved_lower_m + 0.040,
    )
    _add_side_supports(
        carcass,
        r,
        mats,
        half_x=half_x,
        z0=r.body_z0_m,
        z1=box_top,
        depth=depth,
        y_center=0.0,
    )
    _box(
        carcass,
        (half_x * 2.0, depth, r.shelf_thickness_m * 1.5),
        (0.0, 0.0, box_top),
        mats["edge"],
        "box_deck",
    )
    rake = _clamp(0.12 * (r.body_z1_m - box_top), 0.05, 0.16)
    stile_h = r.body_z1_m - box_top
    tilt = math.atan2(rake, stile_h)
    for index, sign in enumerate((-1.0, 1.0)):
        _box(
            carcass,
            (_PANEL_T, 0.080, math.hypot(stile_h, rake)),
            (
                sign * (half_x - _PANEL_T / 2.0 - 0.018),
                depth / 2.0 - 0.050 - rake / 2.0,
                box_top + stile_h / 2.0,
            ),
            mats["wood"],
            f"side_support_raked_{index}",
            rpy=(tilt, 0.0, 0.0),
        )
    split = (
        r.body_z0_m + r.reserved_lower_m
        if r.reserved_lower_m > 0.0
        else r.body_z0_m + 0.5 * (box_top - r.body_z0_m)
    )
    upper = (split + 0.010, box_top - 0.012)
    lower = (r.body_z0_m + 0.010, split - 0.010)
    deck_clear = r.shelf_thickness_m * 1.5 + _SHELF_TRAVEL + 0.014
    rows = []
    for z in [
        z if abs(z - box_top) > deck_clear else box_top + deck_clear
        for z in _shelf_z_values(r)
    ]:
        if z <= box_top:
            box_depth_row, box_row_y = _row_span(r, depth / 2.0, -depth / 2.0)
            rows.append(
                _ShelfRow(
                    z=z,
                    x_center=0.0,
                    half_width=r.interior_half_x_m,
                    y_center=box_row_y,
                    depth=box_depth_row,
                )
            )
        else:
            frac = (z - box_top) / max(stile_h, 1e-6)
            shrink = 1.0 - 0.26 * frac
            row_front = depth / 2.0 - rake * frac - 0.010
            row_back = max(
                -depth / 2.0 + _BACK_T + 0.006,
                row_front - (depth - _BACK_T) * shrink,
            )
            row_depth, row_y = _row_span(r, row_front, row_back - _BACK_T - 0.006)
            rows.append(
                _ShelfRow(
                    z=z,
                    x_center=0.0,
                    half_width=max(0.10, half_x - 0.036),
                    y_center=row_y,
                    depth=row_depth,
                )
            )
    return _Frame(
        front_y=depth / 2.0,
        aperture_half_x=half_x - _PANEL_T,
        aperture_x_center=0.0,
        upper_band=upper,
        lower_band=lower,
        shelf_rows=tuple(rows),
        side_support_x=(-half_x + _PANEL_T, half_x - _PANEL_T),
        pilaster_half_x=r.interior_half_x_m,
    )


def _case_frame_barrister_stack_build(carcass, r: ResolvedConfig, mats) -> _Frame:
    """barrister fork L160-L295: a stack of framed sections."""
    half_x = r.width_m / 2.0
    depth = r.depth_m
    _add_side_supports(
        carcass,
        r,
        mats,
        half_x=half_x,
        z0=r.body_z0_m,
        z1=r.body_z1_m,
        depth=depth,
        y_center=0.0,
    )
    _add_top_and_deck(
        carcass,
        r,
        mats,
        half_x=half_x,
        depth=depth,
        y_center=0.0,
        z_top=r.body_z1_m,
        z_deck=r.body_z0_m,
    )
    for index, z in enumerate(_shelf_z_values(r)):
        _box(
            carcass,
            (half_x * 2.0 + 0.014, 0.006, 0.028),
            (0.0, depth / 2.0 - 0.004, z + r.shelf_thickness_m / 2.0 + 0.014),
            mats["edge"],
            f"section_rail_{index}",
        )
    split = _split_z(r, 0.28)
    upper, lower = _bands(r, split)
    row_depth, row_y = _row_span(r, depth / 2.0 - 0.014, -depth / 2.0)
    rows = tuple(
        _ShelfRow(
            z=z,
            x_center=0.0,
            half_width=r.interior_half_x_m,
            y_center=row_y,
            depth=row_depth,
        )
        for z in _shelf_z_values(r)
    )
    return _Frame(
        front_y=depth / 2.0,
        aperture_half_x=half_x - _PANEL_T,
        aperture_x_center=0.0,
        upper_band=upper,
        lower_band=lower,
        shelf_rows=rows,
        side_support_x=(-half_x + _PANEL_T, half_x - _PANEL_T),
        pilaster_half_x=r.interior_half_x_m,
    )


_CASE_BUILDERS = {
    "gallery_cheeks": _case_frame_gallery_cheeks_build,
    "cubby_columns": _case_frame_cubby_columns_build,
    "panelled_side_frame": _case_frame_panelled_side_frame_build,
    "corner_wing": _case_frame_corner_wing_build,
    "cube_grid": _case_frame_cube_grid_build,
    "raked_ladder": _case_frame_raked_ladder_build,
    "barrister_stack": _case_frame_barrister_stack_build,
}


def _base_style_plinth_base_build(carcass, r: ResolvedConfig, mats) -> None:
    half_x = r.width_m / 2.0
    _box(
        carcass,
        (half_x * 2.0 - 0.030, r.depth_m - 0.030, r.base_lift_m),
        (0.0, -0.004, r.base_lift_m / 2.0),
        mats["edge"],
        "base_plinth",
    )


def _base_style_turned_legs_build(carcass, r: ResolvedConfig, mats) -> None:
    half_x = r.width_m / 2.0
    radius = _clamp(0.030, 0.020, r.depth_m * 0.09)
    for index, (sx, sy) in enumerate(((-1.0, -1.0), (-1.0, 1.0), (1.0, -1.0), (1.0, 1.0))):
        _cyl(
            carcass,
            radius,
            r.base_lift_m,
            (
                sx * (half_x - radius - 0.020),
                sy * (r.depth_m / 2.0 - radius - 0.020),
                r.base_lift_m / 2.0,
            ),
            mats["wood"],
            f"turned_leg_{index}",
        )
        # Turned collar: the source legs are profiled, not plain dowels.
        _cyl(
            carcass,
            radius * 1.25,
            0.030,
            (
                sx * (half_x - radius - 0.020),
                sy * (r.depth_m / 2.0 - radius - 0.020),
                r.base_lift_m - 0.040,
            ),
            mats["edge"],
            f"leg_collar_{index}",
        )
    _box(
        carcass,
        (half_x * 2.0 - 0.060, r.depth_m - 0.060, 0.030),
        (0.0, 0.0, r.base_lift_m - 0.015),
        mats["edge"],
        "leg_rail",
    )


def _base_style_toe_kick_build(carcass, r: ResolvedConfig, mats) -> None:
    half_x = r.width_m / 2.0
    kick_depth = r.depth_m - 0.070
    _box(
        carcass,
        (half_x * 2.0 - 0.020, kick_depth, r.base_lift_m),
        (0.0, -0.035, r.base_lift_m / 2.0),
        mats["edge"],
        "toe_kick_box",
    )
    _box(
        carcass,
        (half_x * 2.0, 0.020, 0.055),
        (0.0, r.depth_m / 2.0 - 0.010, r.base_lift_m - 0.0275),
        mats["wood"],
        "toe_kick_apron",
    )


_BASE_BUILDERS = {
    "plinth_base": _base_style_plinth_base_build,
    "turned_legs": _base_style_turned_legs_build,
    "toe_kick": _base_style_toe_kick_build,
}


def _add_back_panel(carcass, r: ResolvedConfig, mats, frame: _Frame) -> None:
    """002/003: one continuous back board closing the case."""
    half_x = r.width_m / 2.0
    _box(
        carcass,
        (half_x * 2.0 - 2.0 * _PANEL_T + 0.004, _BACK_T, r.body_z1_m - r.body_z0_m),
        (0.0, -r.depth_m / 2.0 + _BACK_T / 2.0, (r.body_z0_m + r.body_z1_m) / 2.0),
        mats["back"],
        "back_panel",
    )


def _shelf_mechanism_fixed_shelves_build(
    model: ArticulatedObject,
    carcass,
    r: ResolvedConfig,
    mats,
    frame: _Frame,
) -> list[str]:
    """005 L291-L299: shelf boards fused into the carcass, no joint."""
    for index, row in enumerate(frame.shelf_rows):
        _box(
            carcass,
            (row.half_width * 2.0, row.depth, r.shelf_thickness_m),
            (row.x_center, row.y_center, row.z),
            mats["interior"],
            f"shelf_mechanism__fixed_shelves__shelf_{index}",
        )
    return []


def _shelf_mechanism_adjustable_shelves_build(
    model: ArticulatedObject,
    carcass,
    r: ResolvedConfig,
    mats,
    frame: _Frame,
) -> list[str]:
    """rec_bookcase_var_adjustable_shelves L316-L383: prismatic shelf parts.

    Each shelf rides a pair of carcass-mounted pilaster standards; the shelf end
    stays captured in its standard by ``_PILASTER_ENGAGE`` at every pose, so the
    moving board keeps a real support path over its whole travel.
    """
    joints: list[str] = []
    travel = min(_SHELF_TRAVEL, max(0.012, 0.35 * (r.shelf_pitch_m - r.shelf_thickness_m)))
    for index, row in enumerate(frame.shelf_rows):
        # The moving board keeps a 2 mm clearance from the fixed case walls and
        # is captured by _PILASTER_ENGAGE inside its two standards instead.
        board_half = max(row.half_width - _FACE_POST_W / 2.0 - 0.002, 0.04)
        # The standard bridges from just inside the board edge out to the case
        # wall, so it is both a real support and part of the connected carcass.
        stand_inner = board_half - _PILASTER_ENGAGE
        stand_outer = row.half_width + _PANEL_T / 2.0 + 0.004
        stand_w = max(stand_outer - stand_inner, _PILASTER_T)
        for side, sign in enumerate((-1.0, 1.0)):
            _box(
                carcass,
                (stand_w, row.depth * 0.85, 2.0 * travel + r.shelf_thickness_m + 0.060),
                (
                    row.x_center + sign * (stand_inner + stand_w / 2.0),
                    row.y_center,
                    row.z,
                ),
                mats["edge"],
                f"shelf_standard_{index}_{side}",
            )
        shelf = model.part(
            f"shelf_mechanism__adjustable_shelves__shelf_{index}",
            meta={"role": "shelf", "index": index},
        )
        _box(
            shelf,
            (board_half * 2.0, row.depth, r.shelf_thickness_m),
            (0.0, 0.0, 0.0),
            mats["interior"],
            "shelf_board",
        )
        _box(
            shelf,
            (board_half * 2.0, 0.016, r.shelf_thickness_m + 0.008),
            (0.0, row.depth / 2.0 - 0.008, 0.0),
            mats["edge"],
            "shelf_front_edge",
        )
        provider = PlaneInterface(
            name=f"shelf_bay_{index}",
            point=(row.x_center, row.y_center, row.z),
            normal=(0.0, 0.0, 1.0),
            tangent_u=(1.0, 0.0, 0.0),
            extent=(row.half_width * 2.0, row.depth),
        )
        consumer = PlaneInterface(
            name=f"shelf_board_{index}",
            point=(0.0, 0.0, 0.0),
            normal=(0.0, 0.0, -1.0),
            tangent_u=(1.0, 0.0, 0.0),
            extent=(board_half * 2.0, row.depth),
        )
        mate = mate_planes(provider, consumer)
        joint_name = f"shelf_mechanism__adjustable_shelves__shelf_lift_{index}"
        model.articulation(
            joint_name,
            ArticulationType.PRISMATIC,
            parent=carcass,
            child=shelf,
            origin=mate.origin,
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(
                effort=40.0, velocity=0.2, lower=-travel, upper=travel
            ),
            motion_properties=MotionProperties(damping=1.5, friction=0.6),
            meta={"mechanism": "adjustable shelf height", "shelf_index": index},
        )
        joints.append(joint_name)
    return joints


_SHELF_BUILDERS = {
    "fixed_shelves": _shelf_mechanism_fixed_shelves_build,
    "adjustable_shelves": _shelf_mechanism_adjustable_shelves_build,
}


def _door_leaf_geometry(
    part,
    r: ResolvedConfig,
    mats,
    *,
    width: float,
    height: float,
    sign: float,
    glazed: bool,
) -> None:
    """Stile / rail / panel door in a hinge-line local frame (005 L46-L118)."""
    rail = _clamp(0.075 * height, 0.040, 0.075)
    rail = min(rail, width * 0.32)
    # The leaf body stands in front of its hinge axis so the carcass knuckle can
    # capture the barrel at every angle without ever entering the frame members.
    body_y = _DOOR_T / 2.0 - 0.002
    outer_x = sign * (rail / 2.0)
    inner_x = sign * (width - rail / 2.0)
    mid_x = sign * (width / 2.0)
    _box(part, (rail, _DOOR_T, height), (outer_x, body_y, height / 2.0), mats["edge"], "outer_stile")
    _box(part, (rail, _DOOR_T, height), (inner_x, body_y, height / 2.0), mats["edge"], "inner_stile")
    _box(
        part,
        (max(width - 2.0 * rail, 0.02), _DOOR_T, rail),
        (mid_x, body_y, height - rail / 2.0),
        mats["edge"],
        "top_rail",
    )
    _box(
        part,
        (max(width - 2.0 * rail, 0.02), _DOOR_T, rail),
        (mid_x, body_y, rail / 2.0),
        mats["edge"],
        "bottom_rail",
    )
    panel_w = max(width - 1.7 * rail, 0.02)
    panel_h = max(height - 1.7 * rail, 0.02)
    if glazed:
        _box(
            part,
            (panel_w, _GLASS_T, panel_h),
            (mid_x, body_y - 0.002, height / 2.0),
            mats["glass"],
            "glass",
        )
    else:
        _box(
            part,
            (panel_w, _DOOR_T * 0.55, panel_h),
            (mid_x, body_y - 0.004, height / 2.0),
            mats["wood"],
            "solid_panel",
        )
    # Pull close to the free stile (005 L108-L117).
    _cyl(
        part,
        0.011,
        0.020,
        (inner_x, body_y + _DOOR_T / 2.0 + 0.010, height * 0.52),
        mats["brass"],
        "door_pull",
        rpy=(math.pi / 2.0, 0.0, 0.0),
    )


def _barrel_length(height: float) -> float:
    return _clamp(0.35 * height, 0.030, _HINGE_LEN)


def _add_hinge_barrels(part, height: float, mats) -> None:
    length = _barrel_length(height)
    for index, z in enumerate((height * 0.18, height * 0.82)):
        _cyl(part, _HINGE_R, length, (0.0, 0.0, z), mats["edge"], f"hinge_barrel_{index}")


def _pin_bracket(
    carcass,
    mats,
    *,
    x: float,
    front_y: float,
    axis_y: float,
    z: float,
    size: tuple[float, float] = (0.014, 0.012),
    tag: str = "",
) -> None:
    """Cheek bracket carrying a hinge pin off the case face (005 L307-L315).

    It reaches exactly to the pin axis, so it grips the pin while staying clear
    of the door barrel, which is offset along the pin.
    """
    y_lo = front_y - 0.012
    y_hi = axis_y + _HINGE_PIN_R * 0.5
    _box(
        carcass,
        (size[0], max(y_hi - y_lo, 0.004), size[1]),
        (x, (y_lo + y_hi) / 2.0, z),
        mats["edge"],
        f"hinge_bracket_{tag}_{int(z * 1000)}",
    )


def _add_hinge_leaves(
    carcass,
    mats,
    *,
    x: float,
    y: float,
    z_base: float,
    height: float,
    front_y: float,
    side: int,
) -> None:
    """Carcass-side hinge pins running through the door barrels (003 L162-L171).

    The pin is coaxial with the barrel, so the door keeps a real support path at
    every angle, and it is thin enough (2*_HINGE_PIN_R) that the captured
    engagement stays well inside the collision tolerance.
    """
    barrel = _barrel_length(height)
    leaf = "l" if side == 0 else "r"
    for index, fraction in enumerate((0.18, 0.82)):
        z = z_base + height * fraction
        _cyl(
            carcass,
            _HINGE_PIN_R,
            barrel + 0.060,
            (x, y, z),
            mats["brass"],
            f"hinge_pin_{index}_{leaf}_{int(z * 1000)}",
        )
        bracket_z = z - barrel / 2.0 - 0.010 if index == 0 else z + barrel / 2.0 + 0.010
        _pin_bracket(
            carcass,
            mats,
            x=x,
            front_y=front_y,
            axis_y=y,
            z=bracket_z,
            tag=f"{index}_{leaf}",
        )


def _add_swing_door(
    model: ArticulatedObject,
    carcass,
    r: ResolvedConfig,
    mats,
    frame: _Frame,
    *,
    name: str,
    band: tuple[float, float],
    side: int,
    leaf_width: float,
    glazed: bool,
) -> str:
    """One vertical-axis revolute leaf hinged on an aperture edge."""
    z_lo, z_hi = band
    height = max(z_hi - z_lo, 0.10)
    edge_x = (
        frame.aperture_x_center - frame.aperture_half_x
        if side == 0
        else frame.aperture_x_center + frame.aperture_half_x
    )
    hinge_x = edge_x
    hinge_y = frame.front_y + _DOOR_PROUD + 0.002
    door = model.part(name, meta={"role": "door", "side": side})
    _door_leaf_geometry(
        door,
        r,
        mats,
        width=leaf_width,
        height=height,
        sign=1.0 if side == 0 else -1.0,
        glazed=glazed,
    )
    _add_hinge_barrels(door, height, mats)
    _add_hinge_leaves(
        carcass,
        mats,
        x=hinge_x,
        y=hinge_y,
        z_base=z_lo,
        height=height,
        front_y=frame.front_y,
        side=side,
    )

    joint_name = f"{name}__hinge"
    # Both leaves turn about +Z on their own hinge line; the mirrored leaf opens
    # through negative joint values, so the closed pose stays the neutral 0.
    axis = (0.0, 0.0, 1.0)
    limits = (
        MotionLimits(effort=12.0, velocity=1.4, lower=0.0, upper=_DOOR_SWING)
        if side == 0
        else MotionLimits(effort=12.0, velocity=1.4, lower=-_DOOR_SWING, upper=0.0)
    )
    provider = AxisInterface(
        name=f"{joint_name}__provider",
        point=(hinge_x, hinge_y, z_lo),
        axis=axis,
        radial=(1.0, 0.0, 0.0),
        radius=_HINGE_R + 0.004,
    )
    consumer = AxisInterface(
        name=f"{joint_name}__consumer",
        point=(0.0, 0.0, 0.0),
        axis=axis,
        radial=(1.0, 0.0, 0.0),
        radius=_HINGE_R,
    )
    mate = mate_axes(provider, consumer)
    model.articulation(
        joint_name,
        ArticulationType.REVOLUTE,
        parent=carcass,
        child=door,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=limits,
        motion_properties=MotionProperties(damping=0.6, friction=0.3),
        meta={"mechanism": "outward swinging door"},
    )
    register_interface_mate(model, joint_name, mate)
    return joint_name


def _add_flip_flap(
    model: ArticulatedObject,
    carcass,
    r: ResolvedConfig,
    mats,
    frame: _Frame,
    *,
    name: str,
    band: tuple[float, float],
    side: int,
    leaf_width: float,
) -> str:
    """Top-pivot glazed flap turning about the width axis (flip_up fork L442-L460)."""
    z_lo, z_hi = band
    height = max(z_hi - z_lo, 0.10)
    hinge_y = frame.front_y + _DOOR_PROUD + 0.002
    sign = -1.0 if side == 0 else 1.0
    x_center = frame.aperture_x_center + sign * (leaf_width / 2.0 + _DOOR_GAP / 2.0)
    flap = model.part(name, meta={"role": "door", "side": side})
    rail = _clamp(0.06 * height, 0.030, 0.060)
    body_y = _DOOR_T / 2.0 - 0.002
    _box(flap, (leaf_width, _DOOR_T, rail), (0.0, body_y, -rail / 2.0), mats["edge"], "top_rail")
    _box(
        flap,
        (leaf_width, _DOOR_T, rail),
        (0.0, body_y, -height + rail / 2.0),
        mats["edge"],
        "bottom_rail",
    )
    for index, s in enumerate((-1.0, 1.0)):
        _box(
            flap,
            (rail, _DOOR_T, height),
            (s * (leaf_width / 2.0 - rail / 2.0), body_y, -height / 2.0),
            mats["edge"],
            f"stile_{index}",
        )
    _box(
        flap,
        (max(leaf_width - 2.0 * rail, 0.02), _GLASS_T, max(height - 2.0 * rail, 0.02)),
        (0.0, body_y - 0.002, -height / 2.0),
        mats["glass"],
        "glass",
    )
    _cyl(
        flap,
        0.011,
        0.020,
        (0.0, body_y + _DOOR_T / 2.0 + 0.010, -height + rail * 0.5),
        mats["brass"],
        "flap_pull",
        rpy=(math.pi / 2.0, 0.0, 0.0),
    )
    for index, s in enumerate((-1.0, 1.0)):
        barrel = _barrel_length(leaf_width)
        _cyl(
            flap,
            _HINGE_R,
            barrel,
            (s * (leaf_width / 2.0 - barrel / 2.0 - 0.012), 0.0, 0.0),
            mats["edge"],
            f"hinge_barrel_{index}",
            rpy=(0.0, math.pi / 2.0, 0.0),
        )
        pin_x = x_center + s * (leaf_width / 2.0 - barrel / 2.0 - 0.012)
        _cyl(
            carcass,
            _HINGE_PIN_R,
            barrel + 0.060,
            (pin_x, hinge_y, z_hi),
            mats["brass"],
            f"flap_hinge_pin_{side}_{index}",
            rpy=(0.0, math.pi / 2.0, 0.0),
        )
        _pin_bracket(
            carcass,
            mats,
            x=pin_x + s * (barrel / 2.0 + 0.010),
            front_y=frame.front_y,
            axis_y=hinge_y,
            z=z_hi,
            size=(0.012, 0.014),
            tag=f"flap{side}{index}",
        )

    joint_name = f"{name}__flap_hinge"
    provider = AxisInterface(
        name=f"{joint_name}__provider",
        point=(x_center, hinge_y, z_hi),
        axis=(1.0, 0.0, 0.0),
        radial=(0.0, 0.0, 1.0),
        radius=_HINGE_R + 0.004,
    )
    consumer = AxisInterface(
        name=f"{joint_name}__consumer",
        point=(0.0, 0.0, 0.0),
        axis=(1.0, 0.0, 0.0),
        radial=(0.0, 0.0, 1.0),
        radius=_HINGE_R,
    )
    mate = mate_axes(provider, consumer)
    model.articulation(
        joint_name,
        ArticulationType.REVOLUTE,
        parent=carcass,
        child=flap,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(effort=10.0, velocity=1.2, lower=0.0, upper=_FLAP_SWING),
        motion_properties=MotionProperties(damping=0.5, friction=0.3),
        meta={"mechanism": "top-pivot flip-up glass flap"},
    )
    register_interface_mate(model, joint_name, mate)
    return joint_name


def _add_drawer(
    model: ArticulatedObject,
    carcass,
    r: ResolvedConfig,
    mats,
    frame: _Frame,
    *,
    name: str,
    z_center: float,
    front_height: float,
) -> str:
    """Hollow drawer tray on side runners (005 L120-L214, L362-L398)."""
    front_width = frame.aperture_half_x * 2.0 - 0.010
    box_half = max(front_width / 2.0 - 0.030, 0.05)
    box_depth = _clamp(0.66 * r.depth_m, 0.14, r.depth_m - 0.05)
    travel = _clamp(0.46 * r.depth_m, 0.09, box_depth - 0.06)
    box_height = max(front_height - 0.040, 0.055)
    front_y_local = 0.0

    drawer = model.part(name, meta={"role": "drawer"})
    _box(
        drawer,
        (front_width, 0.030, front_height),
        (0.0, front_y_local + 0.015, 0.0),
        mats["wood"],
        "drawer_front",
    )
    _box(
        drawer,
        (front_width, 0.005, 0.012),
        (0.0, front_y_local + 0.032, front_height / 2.0 - 0.008),
        mats["edge"],
        "front_edge_band",
    )
    for index, sign in enumerate((-1.0, 1.0)):
        _box(
            drawer,
            (_DRAWER_WALL, box_depth, box_height),
            (sign * (box_half - _DRAWER_WALL / 2.0), -box_depth / 2.0, 0.0),
            mats["edge"],
            f"drawer_side_{index}",
        )
        _cyl(
            drawer,
            0.012,
            0.022,
            (sign * front_width * 0.26, front_y_local + 0.041, 0.0),
            mats["brass"],
            f"drawer_pull_{index}",
            rpy=(math.pi / 2.0, 0.0, 0.0),
        )
    _box(
        drawer,
        (box_half * 2.0, _DRAWER_WALL, box_height),
        (0.0, -box_depth + _DRAWER_WALL / 2.0, 0.0),
        mats["edge"],
        "drawer_back",
    )
    _box(
        drawer,
        (box_half * 2.0, box_depth, 0.012),
        (0.0, -box_depth / 2.0, -box_height / 2.0 + 0.006),
        mats["edge"],
        "drawer_bottom",
    )

    # Carcass runners: the drawer side stays captured by _RUNNER_ENGAGE at every
    # pose, so the tray keeps a real support path when fully extended.
    runner_len = box_depth + travel + 0.030
    runner_y = frame.front_y - runner_len / 2.0 - 0.005
    runner_inner = box_half - _RUNNER_ENGAGE
    runner_outer = max(frame.aperture_half_x - 0.006, runner_inner + _RUNNER_T)
    runner_w = runner_outer - runner_inner
    for index, sign in enumerate((-1.0, 1.0)):
        _box(
            carcass,
            (runner_w, runner_len, 0.030),
            (
                frame.aperture_x_center + sign * (runner_inner + runner_w / 2.0),
                runner_y,
                z_center - box_height / 2.0 + 0.012,
            ),
            mats["edge"],
            f"{name.rsplit('__', 1)[-1]}_runner_{index}",
        )

    joint_name = f"{name}__slide"
    model.articulation(
        joint_name,
        ArticulationType.PRISMATIC,
        parent=carcass,
        child=drawer,
        origin=Origin(xyz=(frame.aperture_x_center, frame.front_y + 0.004, z_center)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=70.0, velocity=0.35, lower=0.0, upper=travel),
        motion_properties=MotionProperties(damping=2.5, friction=1.0),
        meta={"mechanism": "front pull-out drawer"},
    )
    return joint_name


def _add_face_frame(carcass, r: ResolvedConfig, mats, frame: "_Frame") -> None:
    """Front posts on the aperture edges tied back by top and bottom rails.

    The posts carry every hinge pin and drawer runner, so the front hardware is
    always part of one connected carcass instead of a floating island.
    """
    half_x = r.width_m / 2.0
    for index, sign in enumerate((-1.0, 1.0)):
        _box(
            carcass,
            (_FACE_POST_W, _FACE_POST_D, r.body_z1_m - r.body_z0_m),
            (
                frame.aperture_x_center + sign * frame.aperture_half_x,
                frame.front_y - _FACE_POST_D / 2.0 + 0.002,
                (r.body_z0_m + r.body_z1_m) / 2.0,
            ),
            mats["edge"],
            f"face_post_{index}",
        )
    for index, z in (
        (0, r.body_z0_m + 0.015),
        (1, r.body_z1_m - 0.015),
    ):
        _box(
            carcass,
            (half_x * 2.0 - 2.0 * _PANEL_T + 0.006, _FACE_POST_D * 0.8, 0.030),
            (0.0, frame.front_y - _FACE_POST_D / 2.0, z),
            mats["edge"],
            f"face_rail_{index}",
        )


def _split_band(band: tuple[float, float], count: int) -> list[tuple[float, float]]:
    z_lo, z_hi = band
    span = (z_hi - z_lo) / float(count)
    return [(z_lo + span * index, z_lo + span * (index + 1)) for index in range(count)]


def _leaf_width(frame: _Frame) -> float:
    return max(frame.aperture_half_x - _DOOR_GAP / 2.0, 0.06)


# --------------------------------------------------------------------------- #
# front_treatment candidates
# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #
# lower_front candidates
# --------------------------------------------------------------------------- #
def _lower_front_raised_panel_doors_build(model, carcass, r, mats, frame) -> list[str]:
    """003 L71-L208: overlay raised-panel doors on the lower cabinet band."""
    return [
        _add_swing_door(
            model,
            carcass,
            r,
            mats,
            frame,
            name=f"lower_front__raised_panel_doors__door_{side}",
            band=frame.lower_band,
            side=side,
            leaf_width=_leaf_width(frame),
            glazed=False,
        )
        for side in (0, 1)
    ]


def _lower_front_framed_glass_doors_build(model, carcass, r, mats, frame) -> list[str]:
    """glass_doors fork L124-L470: glazed frame-and-panel doors over the stack."""
    band = (frame.lower_band[0], frame.upper_band[1])
    return [
        _add_swing_door(
            model,
            carcass,
            r,
            mats,
            frame,
            name=f"lower_front__framed_glass_doors__door_{side}",
            band=band,
            side=side,
            leaf_width=_leaf_width(frame),
            glazed=True,
        )
        for side in (0, 1)
    ]


def _lower_front_base_drawers_build(model, carcass, r, mats, frame) -> list[str]:
    """001 L273-L330: stacked drawer units sliding out of the base band."""
    joints = []
    for index, sub in enumerate(_split_band(frame.lower_band, 2)):
        joints.append(
            _add_drawer(
                model,
                carcass,
                r,
                mats,
                frame,
                name=f"lower_front__base_drawers__drawer_{index}",
                z_center=(sub[0] + sub[1]) / 2.0,
                front_height=(sub[1] - sub[0]) - 0.012,
            )
        )
    return joints


def _lower_front_flip_up_glass_flap_build(model, carcass, r, mats, frame) -> list[str]:
    """flip_up fork L138-L436: top-pivot glazed flaps over the display band."""
    return [
        _add_flip_flap(
            model,
            carcass,
            r,
            mats,
            frame,
            name=f"lower_front__flip_up_glass_flap__flap_{side}",
            band=frame.upper_band,
            side=side,
            leaf_width=_leaf_width(frame),
        )
        for side in (0, 1)
    ]


def _lower_front_open_cubby_base_build(model, carcass, r, mats, frame) -> list[str]:
    """cubby_cols fork L138-L340: open cubby base with one retained door leaf."""
    return [
        _add_swing_door(
            model,
            carcass,
            r,
            mats,
            frame,
            name="lower_front__open_cubby_base__door_0",
            band=frame.lower_band,
            side=0,
            leaf_width=_leaf_width(frame),
            glazed=False,
        )
    ]


_FRONT_BUILDERS = {
    "raised_panel_doors": _lower_front_raised_panel_doors_build,
    "framed_glass_doors": _lower_front_framed_glass_doors_build,
    "base_drawers": _lower_front_base_drawers_build,
    "flip_up_glass_flap": _lower_front_flip_up_glass_flap_build,
    "open_cubby_base": _lower_front_open_cubby_base_build,
}


# --------------------------------------------------------------------------- #
# Assembly
# --------------------------------------------------------------------------- #
def build_pictureX_0611_bookcase1(
    config: Config | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config or config_from_seed(0))
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={
            "category": "pictureX_0611_bookcase1",
            "identified_object": "tall household bookcase / display case",
            "slot_choices": slot_choices_for_config(r),
            "source_layout": "vertical side boards carrying a shelf stack over a cabinet band",
        },
    )
    mats = _materials(model)
    carcass = model.part(
        f"case_frame__{r.case_frame}__carcass",
        meta={"role": "case_body", "frame": r.case_frame},
    )
    frame = _CASE_BUILDERS[r.case_frame](carcass, r, mats)
    _BASE_BUILDERS[r.base_style](carcass, r, mats)
    _add_back_panel(carcass, r, mats, frame)
    _add_face_frame(carcass, r, mats, frame)
    _SHELF_BUILDERS[r.shelf_mechanism](model, carcass, r, mats, frame)
    _FRONT_BUILDERS[r.lower_front](model, carcass, r, mats, frame)
    return model


# --------------------------------------------------------------------------- #
# Author tests / category anchors
# --------------------------------------------------------------------------- #
def _parts_by_role(model: ArticulatedObject, role: str):
    return [part for part in model.parts if part.meta.get("role") == role]


def _visual_names(part) -> set[str]:
    return {visual.name for visual in part.visuals}


def run_pictureX_0611_bookcase1_tests(
    model: ArticulatedObject,
    config: Config,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)

    bodies = _parts_by_role(model, "case_body")
    shelves = _parts_by_role(model, "shelf")
    doors = _parts_by_role(model, "door")
    drawers = _parts_by_role(model, "drawer")

    ctx.check(
        "category_anchor: one grounded case body carries the shelf stack",
        len(bodies) == 1,
        details=f"case_body parts={len(bodies)}",
    )
    carcass = bodies[0]
    names = _visual_names(carcass)
    side_supports = [name for name in names if "side_support" in name]
    ctx.check(
        "category_anchor: two vertical side boards",
        len(side_supports) >= 2,
        details=f"side supports={sorted(side_supports)}",
    )
    ctx.check(
        "category_anchor: a closed back encloses the case",
        any("back_panel" in name for name in names),
        details=f"back visuals={[n for n in names if 'back' in n]}",
    )

    if r.shelf_mechanism == "fixed_shelves":
        shelf_visuals = [name for name in names if "__shelf_" in name]
        ctx.check(
            "category_anchor: N horizontal shelf boards span the side boards",
            len(shelf_visuals) == r.shelf_count,
            details=f"shelf visuals={len(shelf_visuals)} expected={r.shelf_count}",
        )
    else:
        ctx.check(
            "category_anchor: N horizontal shelf boards span the side boards",
            len(shelves) == r.shelf_count,
            details=f"shelf parts={len(shelves)} expected={r.shelf_count}",
        )

    movers = [
        joint
        for joint in model.articulations
        if joint.articulation_type != ArticulationType.FIXED
    ]
    ctx.check(
        "category_anchor: the case has at least one real non-fixed joint",
        len(movers) >= 1,
        details=f"non-fixed joints={[joint.name for joint in movers]}",
    )
    ctx.check(
        "every moving assembly is a child of the load-bearing case body",
        all(joint.parent == carcass.name for joint in movers),
        details=f"parents={sorted({joint.parent for joint in movers})}",
    )

    clear_pitch = r.shelf_pitch_m - r.shelf_thickness_m
    ctx.check(
        "shelf bays keep their derived clear height",
        clear_pitch >= _MIN_CLEAR_PITCH - 1e-4,
        details=f"clear pitch={clear_pitch:.3f}",
    )
    if clear_pitch < 0.13:
        ctx.warn(
            f"dense shelf pitch {clear_pitch:.3f} m: this seed reads as a display "
            "rack rather than a full-height book bay"
        )

    for door in doors:
        joint = next(joint for joint in model.articulations if joint.child == door.name)
        open_value = max((joint.motion_limits.lower, joint.motion_limits.upper), key=abs)
        closed = ctx.part_world_aabb(door)
        with ctx.pose({joint: open_value}):
            opened = ctx.part_world_aabb(door)
        ctx.check(
            f"{door.name} swings clear of the closed pose",
            closed is not None
            and opened is not None
            and (
                opened[1][1] > closed[1][1] + 0.05
                or abs(opened[1][0] - closed[1][0]) > 0.05
                or opened[1][2] > closed[1][2] + 0.05
            ),
            details=f"closed={closed}, opened={opened}",
        )

    for drawer in drawers:
        joint = next(joint for joint in model.articulations if joint.child == drawer.name)
        rest = ctx.part_world_position(drawer)
        with ctx.pose({joint: joint.motion_limits.upper}):
            extended = ctx.part_world_position(drawer)
        ctx.check(
            f"{drawer.name} extends toward the front",
            rest is not None
            and extended is not None
            and extended[1] > rest[1] + 0.5 * joint.motion_limits.upper,
            details=f"rest={rest}, extended={extended}",
        )

    for shelf in shelves:
        joint = next(joint for joint in model.articulations if joint.child == shelf.name)
        rest = ctx.part_world_position(shelf)
        with ctx.pose({joint: joint.motion_limits.upper}):
            lifted = ctx.part_world_position(shelf)
        ctx.check(
            f"{shelf.name} travels vertically in its standards",
            rest is not None and lifted is not None and lifted[2] > rest[2] + 0.005,
            details=f"rest={rest}, lifted={lifted}",
        )

    return ctx.report()


TEMPLATE_CORNERS = (
    corner_case(
        "narrow_tall_corner_wing_with_moving_shelves",
        {
            "case_frame": "corner_wing",
            "lower_front": "flip_up_glass_flap",
            "shelf_mechanism": "adjustable_shelves",
            "base_style": "turned_legs",
            "shelf_count": 7,
            "width_m": 0.60,
            "depth_m": 0.24,
            "height_m": 2.20,
            "shelf_thickness_m": 0.030,
        },
        reason="narrowest L-plan aperture at maximum shelf count with moving shelves and flaps",
    ),
    corner_case(
        "wide_shallow_cube_grid_with_glass_doors",
        {
            "case_frame": "cube_grid",
            "lower_front": "framed_glass_doors",
            "shelf_mechanism": "fixed_shelves",
            "base_style": "toe_kick",
            "shelf_count": 2,
            "width_m": 1.45,
            "depth_m": 0.24,
            "height_m": 1.10,
            "shelf_thickness_m": 0.016,
        },
        reason="widest single-cell aperture on the shallowest, shortest case",
    ),
    corner_case(
        "raked_ladder_base_box_with_deep_drawers",
        {
            "case_frame": "raked_ladder",
            "lower_front": "base_drawers",
            "shelf_mechanism": "adjustable_shelves",
            "base_style": "plinth_base",
            "shelf_count": 5,
            "width_m": 1.20,
            "depth_m": 0.52,
            "height_m": 2.00,
            "shelf_thickness_m": 0.028,
        },
        reason="raked form hosting the deepest drawer travel inside its vertical base box",
    ),
    corner_case(
        "gallery_cheeks_with_raised_panel_doors",
        {
            "case_frame": "gallery_cheeks",
            "lower_front": "raised_panel_doors",
            "shelf_mechanism": "fixed_shelves",
            "base_style": "turned_legs",
            "shelf_count": 3,
            "width_m": 1.40,
            "depth_m": 0.50,
            "height_m": 2.18,
            "shelf_thickness_m": 0.026,
        },
        reason="tallest lifted gallery case with a full-width lower door pair",
    ),
    corner_case(
        "barrister_stack_with_open_cubby_base",
        {
            "case_frame": "barrister_stack",
            "lower_front": "open_cubby_base",
            "shelf_mechanism": "adjustable_shelves",
            "base_style": "toe_kick",
            "shelf_count": 7,
            "width_m": 0.85,
            "depth_m": 0.30,
            "height_m": 1.60,
            "shelf_thickness_m": 0.030,
        },
        reason="densest section stack with moving shelves and a single retained leaf",
    ),
    corner_case(
        "cubby_columns_max_with_base_drawers",
        {
            "case_frame": "cubby_columns",
            "lower_front": "base_drawers",
            "shelf_mechanism": "fixed_shelves",
            "base_style": "plinth_base",
            "shelf_count": 5,
            "width_m": 1.44,
            "depth_m": 0.46,
            "height_m": 1.95,
            "shelf_thickness_m": 0.022,
        },
        reason="maximum column count over a reserved drawer band",
    ),
)


__all__ = [
    "Config",
    "ResolvedConfig",
    "TEMPLATE_CORNERS",
    "TEMPLATE_DOMAIN",
    "build_pictureX_0611_bookcase1",
    "config_from_seed",
    "resolve_config",
    "run_pictureX_0611_bookcase1_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
]
