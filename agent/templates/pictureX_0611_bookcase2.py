# SPDX-License-Identifier: Apache-2.0

"""Self-contained 'bookcase2' template — two-tier / sliding-door / mobile bookcases.

Rebuilt from the three ``pictureX/0611/bookcase2`` origin records and the accepted
forks listed in
``articraft_template_authoring/source_maps/pictureX_0611_bookcase2.md``.

Category identity: a free-standing bookcase built as an open bay frame or a
panel carcass, whose front band carries the moving hardware — hinged doors,
bypass sliding doors, drawers or a pull-out shelf tray — and which may stand on
casters.  Four independent structural axes:

* ``case_frame``      — open bay frame (001), panel carcass (002), slim upright
  (003), and the two-tier, bay-grid and raked-ladder forks.
* ``lower_front``     — hinged upper doors, hinged lower doors, bypass sliding
  doors (prismatic along the width), lower drawers, a pull-out shelf tray, or an
  open cubby that keeps one full-width sliding drawer.
* ``shelf_mechanism`` — fixed shelf boards versus prismatic adjustable shelves.
* ``base_style``      — plinth, casters, or a recessed toe kick.

Every ``case_frame`` exports the same aperture interface (front plane, aperture
half-width and centre, an upper and a lower band in z) and its own shelf rows;
``lower_front`` consumes only that aperture, so all 6 x 6 x 2 x 3 = 216
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
    "open_bay_frame",
    "panel_carcass",
    "slim_upright",
    "two_tier_split",
    "bay_grid",
    "raked_ladder_frame",
]
LowerFront = Literal[
    "hinged_upper_doors",
    "hinged_lower_doors",
    "bypass_sliding_doors",
    "lower_drawers",
    "pullout_shelf",
    "open_cubby_with_drawer",
]
ShelfMechanism = Literal["fixed_shelves", "adjustable_shelves"]
BaseStyle = Literal["plinth_base", "caster_base", "toe_kick"]

CASE_FRAMES: tuple[CaseFrame, ...] = (
    "open_bay_frame",
    "panel_carcass",
    "slim_upright",
    "two_tier_split",
    "bay_grid",
    "raked_ladder_frame",
)
LOWER_FRONTS: tuple[LowerFront, ...] = (
    "hinged_upper_doors",
    "hinged_lower_doors",
    "bypass_sliding_doors",
    "lower_drawers",
    "pullout_shelf",
    "open_cubby_with_drawer",
)
SHELF_MECHANISMS: tuple[ShelfMechanism, ...] = ("fixed_shelves", "adjustable_shelves")
BASE_STYLES: tuple[BaseStyle, ...] = ("plinth_base", "caster_base", "toe_kick")
SHELF_COUNTS: tuple[int, ...] = (2, 4, 5, 7)

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
_WIDTH_RANGE = (0.60, 1.50)
_DEPTH_RANGE = (0.24, 0.52)
_HEIGHT_RANGE = (1.05, 2.10)
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
DRAWER_FRONTS: frozenset[str] = frozenset(
    {"lower_drawers", "pullout_shelf", "open_cubby_with_drawer"}
)


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _reserved_lower(lower_front: str, body_span: float) -> float:
    """Interior height the front assembly consumes at the bottom of the case."""
    if lower_front not in DRAWER_FRONTS:
        return 0.0
    return _clamp(0.34 * body_span, 0.22, 0.50)


@dataclass(frozen=True)
class Config:
    case_frame: CaseFrame = "panel_carcass"
    lower_front: LowerFront = "hinged_lower_doors"
    shelf_mechanism: ShelfMechanism = "fixed_shelves"
    base_style: BaseStyle = "plinth_base"
    shelf_count: int = 4
    width_m: float | None = None
    depth_m: float | None = None
    height_m: float | None = None
    shelf_thickness_m: float | None = None
    name: str = "pictureX_0611_bookcase2"


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
    rng = random.Random(seed ^ 0xB2C2_2026)
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
    base = {"plinth_base": 0.070, "caster_base": 0.110, "toe_kick": 0.090}[base_style]
    if case_frame == "open_bay_frame":
        base = max(0.050, base * 0.80)
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
    width = 0.960 if config.width_m is None else float(config.width_m)
    depth = 0.380 if config.depth_m is None else float(config.depth_m)
    height = 1.780 if config.height_m is None else float(config.height_m)
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
def _case_frame_open_bay_frame_build(carcass, r: ResolvedConfig, mats) -> _Frame:
    """001 L156-L381: an open bay frame of slim uprights and full-width rails."""
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
    # Front and rear rails tie the uprights together at every shelf line.
    for index, z in enumerate(_shelf_z_values(r)):
        for tag, y in (("front", depth / 2.0 - 0.026), ("rear", -depth / 2.0 + 0.026)):
            _box(
                carcass,
                (half_x * 2.0 - 2.0 * _PANEL_T + 0.006, 0.024, 0.026),
                (0.0, y, z - r.shelf_thickness_m / 2.0 - 0.014),
                mats["edge"],
                f"bay_rail_{tag}_{index}",
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
    split = _split_z(r, 0.30)
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


def _case_frame_panel_carcass_build(carcass, r: ResolvedConfig, mats) -> _Frame:
    """002 L47-L262: a closed panel carcass with thick wrapped side panels."""
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
    # Wrapped panel edges: the carcass reads as one manufactured shell.
    for side, sign in enumerate((-1.0, 1.0)):
        _box(
            carcass,
            (0.012, depth + 0.006, r.body_z1_m - r.body_z0_m + 0.020),
            (
                sign * (half_x + 0.004),
                0.0,
                (r.body_z0_m + r.body_z1_m) / 2.0,
            ),
            mats["edge"],
            f"panel_wrap_{side}",
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


def _case_frame_slim_upright_build(carcass, r: ResolvedConfig, mats) -> _Frame:
    """003 L110-L186: slim stiles carrying a deep shelf run behind the doors."""
    half_x = r.width_m / 2.0
    depth = r.depth_m
    stile_t = _PANEL_T * 0.7
    for index, sign in enumerate((-1.0, 1.0)):
        _box(
            carcass,
            (stile_t, depth, r.body_z1_m - r.body_z0_m),
            (
                sign * (half_x - stile_t / 2.0),
                0.0,
                (r.body_z0_m + r.body_z1_m) / 2.0,
            ),
            mats["wood"],
            f"side_support_{index}",
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
    split = _split_z(r, 0.32)
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


def _case_frame_two_tier_split_build(carcass, r: ResolvedConfig, mats) -> _Frame:
    """two_tier fork L47-L262: upper and lower carcass split at a mid deck."""
    half_x = r.width_m / 2.0
    depth = r.depth_m
    upper_depth = max(0.170, depth * 0.74)
    z_values = _shelf_z_values(r)
    if r.reserved_lower_m > 0.0:
        split = r.body_z0_m + r.reserved_lower_m
    else:
        index = max((len(z_values) - 1) // 2, 0)
        split = (
            (z_values[index] + z_values[index + 1]) / 2.0
            if index + 1 < len(z_values)
            else z_values[index] + r.shelf_pitch_m / 2.0
        )
    upper_y = -(depth - upper_depth) / 2.0
    _add_side_supports(
        carcass,
        r,
        mats,
        half_x=half_x,
        z0=r.body_z0_m,
        z1=split,
        depth=depth,
        y_center=0.0,
        prefix="lower_",
    )
    _add_side_supports(
        carcass,
        r,
        mats,
        half_x=half_x,
        z0=split,
        z1=r.body_z1_m,
        depth=upper_depth,
        y_center=upper_y,
    )
    _box(
        carcass,
        (half_x * 2.0, depth, r.shelf_thickness_m * 1.2),
        (0.0, 0.0, split),
        mats["edge"],
        "mid_deck",
    )
    _add_top_and_deck(
        carcass,
        r,
        mats,
        half_x=half_x,
        depth=upper_depth,
        y_center=upper_y,
        z_top=r.body_z1_m,
        z_deck=r.body_z0_m,
    )
    upper, lower = _bands(r, split)
    upper_row_depth, upper_row_y = _row_span(
        r, upper_y + upper_depth / 2.0, upper_y - upper_depth / 2.0
    )
    lower_row_depth, lower_row_y = _row_span(r, depth / 2.0, -depth / 2.0)
    rows = []
    for z in z_values:
        if z > split:
            rows.append(
                _ShelfRow(
                    z=z,
                    x_center=0.0,
                    half_width=r.interior_half_x_m,
                    y_center=upper_row_y,
                    depth=upper_row_depth,
                )
            )
        else:
            rows.append(
                _ShelfRow(
                    z=z,
                    x_center=0.0,
                    half_width=r.interior_half_x_m,
                    y_center=lower_row_y,
                    depth=lower_row_depth,
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


def _case_frame_bay_grid_build(carcass, r: ResolvedConfig, mats) -> _Frame:
    """bays_n4 fork L156-L339: side-by-side bays divided by full-depth uprights."""
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
    bays = int(_clamp(round(r.width_m / 0.42), 2, 4))
    bay_w = (r.interior_half_x_m * 2.0) / float(bays)
    for index in range(1, bays):
        x = -r.interior_half_x_m + bay_w * float(index)
        _box(
            carcass,
            (_PANEL_T, depth - _BACK_T, r.body_z1_m - r.body_z0_m),
            (x, -_BACK_T / 2.0, (r.body_z0_m + r.body_z1_m) / 2.0),
            mats["wood"],
            f"bay_upright_{index - 1}",
        )
    split = _split_z(r, 0.30)
    upper, lower = _bands(r, split)
    row_depth, row_y = _row_span(r, depth / 2.0, -depth / 2.0)
    rows = tuple(
        _ShelfRow(
            z=z,
            x_center=-r.interior_half_x_m + bay_w * (float(index % bays) + 0.5),
            half_width=bay_w / 2.0 - _PANEL_T / 2.0,
            y_center=row_y,
            depth=row_depth,
        )
        for index, z in enumerate(_shelf_z_values(r))
    )
    return _Frame(
        front_y=depth / 2.0,
        aperture_half_x=bay_w / 2.0 - 0.006,
        aperture_x_center=-r.interior_half_x_m + bay_w * 0.5,
        upper_band=upper,
        lower_band=lower,
        shelf_rows=rows,
        side_support_x=(-half_x + _PANEL_T, half_x - _PANEL_T),
        pilaster_half_x=r.interior_half_x_m,
    )


def _case_frame_raked_ladder_frame_build(carcass, r: ResolvedConfig, mats) -> _Frame:
    """raked ladder fork L110-L228: raked uprights over a vertical lower cabinet."""
    half_x = r.width_m / 2.0
    depth = r.depth_m
    box_top = r.body_z0_m + max(
        _clamp(0.34 * (r.body_z1_m - r.body_z0_m), 0.26, 0.62),
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
        prefix="lower_",
    )
    _box(
        carcass,
        (half_x * 2.0, depth, r.shelf_thickness_m * 1.5),
        (0.0, 0.0, box_top),
        mats["edge"],
        "box_deck",
    )
    rake = _clamp(0.11 * (r.body_z1_m - box_top), 0.05, 0.15)
    stile_h = r.body_z1_m - box_top
    tilt = math.atan2(rake, stile_h)
    for index, sign in enumerate((-1.0, 1.0)):
        _box(
            carcass,
            (_PANEL_T, 0.070, math.hypot(stile_h, rake)),
            (
                sign * (half_x - _PANEL_T / 2.0 - 0.016),
                depth / 2.0 - 0.045 - rake / 2.0,
                box_top + stile_h / 2.0,
            ),
            mats["wood"],
            f"side_support_{index}",
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
            shrink = 1.0 - 0.24 * frac
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
                    half_width=max(0.10, half_x - 0.034),
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


_CASE_BUILDERS = {
    "open_bay_frame": _case_frame_open_bay_frame_build,
    "panel_carcass": _case_frame_panel_carcass_build,
    "slim_upright": _case_frame_slim_upright_build,
    "two_tier_split": _case_frame_two_tier_split_build,
    "bay_grid": _case_frame_bay_grid_build,
    "raked_ladder_frame": _case_frame_raked_ladder_frame_build,
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


def _base_style_caster_base_build(carcass, r: ResolvedConfig, mats) -> None:
    """caster_base fork L156-L431: four caster assemblies on mounting plates."""
    half_x = r.width_m / 2.0
    plate_t = 0.014
    wheel_r = max((r.base_lift_m - plate_t) / 2.0, 0.018)
    for index, (sx, sy) in enumerate(((-1.0, -1.0), (-1.0, 1.0), (1.0, -1.0), (1.0, 1.0))):
        x = sx * (half_x - 0.055)
        y = sy * (r.depth_m / 2.0 - 0.055)
        _box(
            carcass,
            (0.070, 0.070, plate_t),
            (x, y, r.base_lift_m - plate_t / 2.0),
            mats["edge"],
            f"caster_plate_{index}",
        )
        _box(
            carcass,
            (0.028, 0.040, r.base_lift_m - plate_t),
            (x, y, (r.base_lift_m - plate_t) / 2.0),
            mats["edge"],
            f"caster_fork_{index}",
        )
        _cyl(
            carcass,
            wheel_r,
            0.024,
            (x, y, wheel_r),
            mats["back"],
            f"caster_wheel_{index}",
            rpy=(0.0, math.pi / 2.0, 0.0),
        )
    _box(
        carcass,
        (half_x * 2.0 - 0.060, r.depth_m - 0.060, 0.024),
        (0.0, 0.0, r.base_lift_m - 0.012),
        mats["edge"],
        "caster_rail",
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
    "caster_base": _base_style_caster_base_build,
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
    travel = min(_SHELF_TRAVEL, max(0.012, 0.30 * (r.shelf_pitch_m - r.shelf_thickness_m)))
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
        f"hinge_bracket_{tag}_{'l' if x < 0 else 'r'}_{int(z * 1000)}",
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
    tag: str = "",
) -> None:
    """Carcass-side hinge pins running through the door barrels (003 L162-L171).

    The pin is coaxial with the barrel, so the door keeps a real support path at
    every angle, and it is thin enough (2*_HINGE_PIN_R) that the captured
    engagement stays well inside the collision tolerance.
    """
    barrel = _barrel_length(height)
    for index, fraction in enumerate((0.18, 0.82)):
        z = z_base + height * fraction
        _cyl(
            carcass,
            _HINGE_PIN_R,
            barrel + 0.060,
            (x, y, z),
            mats["brass"],
            f"hinge_pin_{tag}{index}_{'l' if x < 0 else 'r'}_{int(z * 1000)}",
        )
        bracket_z = z - barrel / 2.0 - 0.010 if index == 0 else z + barrel / 2.0 + 0.010
        _pin_bracket(
            carcass,
            mats,
            x=x,
            front_y=front_y,
            axis_y=y,
            z=bracket_z,
            tag=f"{tag}{index}",
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
        tag=f"door_{side}_",
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
# bypass sliding leaves and the pull-out tray
# --------------------------------------------------------------------------- #
def _add_sliding_door(
    model: ArticulatedObject,
    carcass,
    r: ResolvedConfig,
    mats,
    frame: _Frame,
    *,
    name: str,
    band: tuple[float, float],
    side: int,
) -> str:
    """One bypass leaf running on its own track (sliding_doors fork L234-L300).

    The leaf's head rail stays captured inside its carcass track over the whole
    travel, so a sliding leaf keeps a real support path at every pose.
    """
    z_lo, z_hi = band
    height = max(z_hi - z_lo - 0.010, 0.10)
    leaf_w = max(frame.aperture_half_x * 1.02, 0.10)
    travel = max(frame.aperture_half_x * 1.9 - leaf_w, 0.05)
    track_y = frame.front_y + (0.032 if side == 0 else 0.012)
    z_center = (z_lo + z_hi) / 2.0
    start_x = frame.aperture_x_center + (-1.0 if side == 0 else 1.0) * (leaf_w / 2.0)

    leaf = model.part(name, meta={"role": "door", "side": side, "track": side})
    _box(leaf, (leaf_w, _GLASS_T + 0.008, height), (0.0, 0.0, 0.0), mats["wood"], "leaf_panel")
    _box(
        leaf,
        (leaf_w, 0.014, 0.026),
        (0.0, 0.0, height / 2.0 - 0.013),
        mats["edge"],
        "leaf_head_rail",
    )
    _box(
        leaf,
        (leaf_w, 0.014, 0.022),
        (0.0, 0.0, -height / 2.0 + 0.011),
        mats["edge"],
        "leaf_foot_rail",
    )
    pull_x = (leaf_w / 2.0 - 0.045) * (1.0 if side == 0 else -1.0)
    if side == 0:
        # Front-track leaf: a real knob pull standing off the outer face.
        _cyl(
            leaf,
            0.010,
            0.018,
            (pull_x, 0.014, 0.0),
            mats["brass"],
            "leaf_pull",
            rpy=(math.pi / 2.0, 0.0, 0.0),
        )
    else:
        # Rear-track leaf: a flush finger pull, so the bypassing front leaf
        # always clears it.
        _box(
            leaf,
            (0.030, 0.005, 0.090),
            (pull_x, 0.0075, 0.0),
            mats["brass"],
            "leaf_pull",
        )

    # Carcass tracks: head and sill channels spanning the aperture plus travel.
    track_len = frame.aperture_half_x * 2.0 + 0.020
    for tag, z, thickness in (
        ("head", z_center + height / 2.0 + 0.010 - 0.002, 0.020),
        ("sill", z_center - height / 2.0 - 0.008 + 0.002, 0.016),
    ):
        _box(
            carcass,
            (track_len, 0.026, thickness),
            (frame.aperture_x_center, track_y, z),
            mats["edge"],
            f"{name.rsplit('__', 1)[-1]}_{tag}_track",
        )

    joint_name = f"{name}__slide"
    lower = 0.0 if side == 0 else -travel
    upper = travel if side == 0 else 0.0
    model.articulation(
        joint_name,
        ArticulationType.PRISMATIC,
        parent=carcass,
        child=leaf,
        origin=Origin(xyz=(start_x, track_y, z_center)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=40.0, velocity=0.4, lower=lower, upper=upper),
        motion_properties=MotionProperties(damping=1.2, friction=0.5),
        meta={"mechanism": "bypass sliding leaf"},
    )
    return joint_name


def _add_pullout_tray(
    model: ArticulatedObject,
    carcass,
    r: ResolvedConfig,
    mats,
    frame: _Frame,
    *,
    name: str,
    z_center: float,
) -> str:
    """Open shelf tray that pulls out of the case (pullout_shelf fork L27-L191)."""
    tray_half = max(frame.aperture_half_x - 0.020, 0.05)
    tray_depth = _clamp(0.64 * r.depth_m, 0.14, r.depth_m - 0.05)
    travel = _clamp(0.42 * r.depth_m, 0.08, tray_depth - 0.06)
    wall = 0.012

    tray = model.part(name, meta={"role": "drawer", "kind": "pullout_tray"})
    _box(
        tray,
        (tray_half * 2.0, tray_depth, 0.014),
        (0.0, -tray_depth / 2.0, -0.020),
        mats["interior"],
        "tray_bottom",
    )
    for index, sign in enumerate((-1.0, 1.0)):
        _box(
            tray,
            (wall, tray_depth, 0.048),
            (sign * (tray_half - wall / 2.0), -tray_depth / 2.0, 0.0),
            mats["edge"],
            f"tray_side_{index}",
        )
    _box(
        tray,
        (tray_half * 2.0, wall, 0.048),
        (0.0, -tray_depth + wall / 2.0, 0.0),
        mats["edge"],
        "tray_back",
    )
    _box(
        tray,
        (tray_half * 2.0, wall, 0.032),
        (0.0, -wall / 2.0, 0.008),
        mats["edge"],
        "tray_front_lip",
    )

    runner_len = tray_depth + travel + 0.030
    runner_y = frame.front_y - runner_len / 2.0 - 0.005
    runner_inner = tray_half - _RUNNER_ENGAGE
    runner_outer = max(frame.aperture_half_x - 0.004, runner_inner + _RUNNER_T)
    runner_w = runner_outer - runner_inner
    for index, sign in enumerate((-1.0, 1.0)):
        _box(
            carcass,
            (runner_w, runner_len, 0.026),
            (
                frame.aperture_x_center + sign * (runner_inner + runner_w / 2.0),
                runner_y,
                z_center - 0.014,
            ),
            mats["edge"],
            f"{name.rsplit('__', 1)[-1]}_runner_{index}",
        )

    joint_name = f"{name}__slide"
    model.articulation(
        joint_name,
        ArticulationType.PRISMATIC,
        parent=carcass,
        child=tray,
        origin=Origin(xyz=(frame.aperture_x_center, frame.front_y - 0.004, z_center)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=60.0, velocity=0.35, lower=0.0, upper=travel),
        motion_properties=MotionProperties(damping=2.0, friction=0.8),
        meta={"mechanism": "pull-out shelf tray"},
    )
    return joint_name


# --------------------------------------------------------------------------- #
# lower_front candidates
# --------------------------------------------------------------------------- #
def _lower_front_hinged_upper_doors_build(model, carcass, r, mats, frame) -> list[str]:
    """upper_doors fork L26-L225: paired doors closing the upper opening."""
    return [
        _add_swing_door(
            model,
            carcass,
            r,
            mats,
            frame,
            name=f"lower_front__hinged_upper_doors__door_{side}",
            band=frame.upper_band,
            side=side,
            leaf_width=_leaf_width(frame),
            glazed=True,
        )
        for side in (0, 1)
    ]


def _lower_front_hinged_lower_doors_build(model, carcass, r, mats, frame) -> list[str]:
    """003 L26-L214: paired lower cabinet doors about vertical stiles."""
    return [
        _add_swing_door(
            model,
            carcass,
            r,
            mats,
            frame,
            name=f"lower_front__hinged_lower_doors__door_{side}",
            band=frame.lower_band,
            side=side,
            leaf_width=_leaf_width(frame),
            glazed=False,
        )
        for side in (0, 1)
    ]


def _lower_front_bypass_sliding_doors_build(model, carcass, r, mats, frame) -> list[str]:
    """sliding_doors fork L234-L300: two bypass leaves on front and rear tracks."""
    band = (frame.lower_band[0], frame.upper_band[1])
    return [
        _add_sliding_door(
            model,
            carcass,
            r,
            mats,
            frame,
            name=f"lower_front__bypass_sliding_doors__leaf_{side}",
            band=band,
            side=side,
        )
        for side in (0, 1)
    ]


def _lower_front_lower_drawers_build(model, carcass, r, mats, frame) -> list[str]:
    """lower_drawers fork L200-L270: stacked drawer boxes in the lower band."""
    joints = []
    for index, sub in enumerate(_split_band(frame.lower_band, 2)):
        joints.append(
            _add_drawer(
                model,
                carcass,
                r,
                mats,
                frame,
                name=f"lower_front__lower_drawers__drawer_{index}",
                z_center=(sub[0] + sub[1]) / 2.0,
                front_height=(sub[1] - sub[0]) - 0.012,
            )
        )
    return joints


def _lower_front_pullout_shelf_build(model, carcass, r, mats, frame) -> list[str]:
    """pullout_shelf fork L27-L418: a shelf tray that pulls out on side runners."""
    band = frame.lower_band
    return [
        _add_pullout_tray(
            model,
            carcass,
            r,
            mats,
            frame,
            name="lower_front__pullout_shelf__tray_0",
            z_center=band[0] + (band[1] - band[0]) * 0.55,
        )
    ]


def _lower_front_open_cubby_with_drawer_build(model, carcass, r, mats, frame) -> list[str]:
    """lower_open_cubby fork L202-L233: open cubby keeping one sliding drawer."""
    band = frame.lower_band
    height = min(band[1] - band[0], 0.24)
    return [
        _add_drawer(
            model,
            carcass,
            r,
            mats,
            frame,
            name="lower_front__open_cubby_with_drawer__drawer_0",
            z_center=band[0] + height / 2.0,
            front_height=height - 0.012,
        )
    ]


_FRONT_BUILDERS = {
    "hinged_upper_doors": _lower_front_hinged_upper_doors_build,
    "hinged_lower_doors": _lower_front_hinged_lower_doors_build,
    "bypass_sliding_doors": _lower_front_bypass_sliding_doors_build,
    "lower_drawers": _lower_front_lower_drawers_build,
    "pullout_shelf": _lower_front_pullout_shelf_build,
    "open_cubby_with_drawer": _lower_front_open_cubby_with_drawer_build,
}


# --------------------------------------------------------------------------- #
# Assembly
# --------------------------------------------------------------------------- #
def build_pictureX_0611_bookcase2(
    config: Config | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config or config_from_seed(0))
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={
            "category": "pictureX_0611_bookcase2",
            "identified_object": "two-tier / sliding-door bookcase",
            "slot_choices": slot_choices_for_config(r),
            "source_layout": "a bay frame or panel carcass carrying a shelf stack over a front band",
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


def run_pictureX_0611_bookcase2_tests(
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
        "category_anchor: two vertical side supports",
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
            "category_anchor: N horizontal shelf boards span the side supports",
            len(shelf_visuals) == r.shelf_count,
            details=f"shelf visuals={len(shelf_visuals)} expected={r.shelf_count}",
        )
    else:
        ctx.check(
            "category_anchor: N horizontal shelf boards span the side supports",
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
        "narrow_tall_bay_grid_with_sliding_leaves",
        {
            "case_frame": "bay_grid",
            "lower_front": "bypass_sliding_doors",
            "shelf_mechanism": "adjustable_shelves",
            "base_style": "caster_base",
            "shelf_count": 7,
            "width_m": 0.60,
            "depth_m": 0.24,
            "height_m": 2.10,
            "shelf_thickness_m": 0.030,
        },
        reason="narrowest bay aperture with two bypass leaves and moving shelves on casters",
    ),
    corner_case(
        "wide_shallow_open_bay_frame_with_pullout_tray",
        {
            "case_frame": "open_bay_frame",
            "lower_front": "pullout_shelf",
            "shelf_mechanism": "fixed_shelves",
            "base_style": "toe_kick",
            "shelf_count": 2,
            "width_m": 1.50,
            "depth_m": 0.24,
            "height_m": 1.05,
            "shelf_thickness_m": 0.016,
        },
        reason="widest, shallowest case with the longest pull-out tray travel",
    ),
    corner_case(
        "raked_ladder_frame_with_deep_drawers",
        {
            "case_frame": "raked_ladder_frame",
            "lower_front": "lower_drawers",
            "shelf_mechanism": "adjustable_shelves",
            "base_style": "plinth_base",
            "shelf_count": 5,
            "width_m": 1.20,
            "depth_m": 0.52,
            "height_m": 2.00,
            "shelf_thickness_m": 0.028,
        },
        reason="raked frame hosting the deepest drawer travel inside its lower cabinet",
    ),
    corner_case(
        "two_tier_split_with_upper_doors",
        {
            "case_frame": "two_tier_split",
            "lower_front": "hinged_upper_doors",
            "shelf_mechanism": "fixed_shelves",
            "base_style": "caster_base",
            "shelf_count": 4,
            "width_m": 1.45,
            "depth_m": 0.50,
            "height_m": 2.08,
            "shelf_thickness_m": 0.026,
        },
        reason="tallest split case with doors on the shallower upper tier",
    ),
    corner_case(
        "panel_carcass_dense_shelves_with_open_cubby",
        {
            "case_frame": "panel_carcass",
            "lower_front": "open_cubby_with_drawer",
            "shelf_mechanism": "adjustable_shelves",
            "base_style": "toe_kick",
            "shelf_count": 7,
            "width_m": 0.85,
            "depth_m": 0.30,
            "height_m": 1.55,
            "shelf_thickness_m": 0.030,
        },
        reason="densest moving-shelf stack over a single retained drawer",
    ),
    corner_case(
        "slim_upright_with_lower_doors",
        {
            "case_frame": "slim_upright",
            "lower_front": "hinged_lower_doors",
            "shelf_mechanism": "fixed_shelves",
            "base_style": "plinth_base",
            "shelf_count": 5,
            "width_m": 1.48,
            "depth_m": 0.46,
            "height_m": 1.95,
            "shelf_thickness_m": 0.022,
        },
        reason="widest slim-stile frame with a full-width lower door pair",
    ),
)


__all__ = [
    "Config",
    "ResolvedConfig",
    "TEMPLATE_CORNERS",
    "TEMPLATE_DOMAIN",
    "build_pictureX_0611_bookcase2",
    "config_from_seed",
    "resolve_config",
    "run_pictureX_0611_bookcase2_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
]
