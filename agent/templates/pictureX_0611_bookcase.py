# SPDX-License-Identifier: Apache-2.0

"""Self-contained 'bookcase' template — free-standing shelved book cases.

Rebuilt from the six ``pictureX/0611/bookcase`` origin records plus the accepted
forks listed in
``articraft_template_authoring/source_maps/pictureX_0611_bookcase.md``.

Category identity: a free-standing case of vertical side supports carrying a
stack of horizontal book shelves, with at least one real non-fixed joint (a
glazed/panel door, a drawer, or a prismatic adjustable shelf).

Five independent structural axes, each a distinct sub-assembly of the sources:

* ``carcass_form``    — the load-bearing case family (005/002 upright, 003
  two-tier hutch, 004 legged highboy, 006 grid hutch, and the ladder / corner /
  cube_grid / barrister forks).
* ``front_treatment`` — what closes the front aperture and with which joint
  (vertical-axis revolute doors, horizontal-axis flip-up flaps, prismatic
  drawers).
* ``shelf_mechanism`` — fixed shelf boards (005 L291-L299) versus prismatic
  adjustable shelves (rec_bookcase_var_adjustable_shelves L316-L383).
* ``base_style``      — how the case meets the floor: plinth, turned legs, or a
  recessed toe kick.
* ``back_panel``      — solid board, open back, or beadboard battens.

Host adaptation instead of compatibility gates: every ``carcass_form`` derives
the same front-aperture interface (front plane, aperture half-width, an upper
band and a lower band in z) out of its own geometry, and ``front_treatment``
consumes only that interface.  All 8 x 6 x 2 x 3 x 3 = 864 combinations build.

Coordinate frame: +X = width (centred on 0), +Y = depth with the front face at
+depth/2, +Z = height with the floor at z = 0.

This file is the only runtime truth.  It imports the stdlib and the Articraft
``sdk`` only; it never reads the SourceMap, the TemplateDesign or any source
``model.py``.
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
    ExtrudeGeometry,
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
    mesh_from_geometry,
    multiplicity_slot,
    register_interface_mate,
)

CarcassForm = Literal[
    "rectangular_upright",
    "two_tier_hutch",
    "legged_highboy",
    "grid_hutch",
    "ladder",
    "corner",
    "cube_grid",
    "barrister",
]
FrontTreatment = Literal[
    "full_glass_doors",
    "upper_glass_base_drawers",
    "glass_top_panel_base_doors",
    "open_shelving",
    "base_cabinet_doors",
    "flip_up_glass",
]
ShelfMechanism = Literal["fixed_shelves", "adjustable_shelves"]
BaseStyle = Literal["plinth", "legs", "toe_kick"]
BackPanel = Literal["solid_back", "open_back", "beadboard_back"]

CARCASS_FORMS: tuple[CarcassForm, ...] = (
    "rectangular_upright",
    "two_tier_hutch",
    "legged_highboy",
    "grid_hutch",
    "ladder",
    "corner",
    "cube_grid",
    "barrister",
)
FRONT_TREATMENTS: tuple[FrontTreatment, ...] = (
    "full_glass_doors",
    "upper_glass_base_drawers",
    "glass_top_panel_base_doors",
    "open_shelving",
    "base_cabinet_doors",
    "flip_up_glass",
)
SHELF_MECHANISMS: tuple[ShelfMechanism, ...] = ("fixed_shelves", "adjustable_shelves")
BASE_STYLES: tuple[BaseStyle, ...] = ("plinth", "legs", "toe_kick")
BACK_PANELS: tuple[BackPanel, ...] = ("solid_back", "open_back", "beadboard_back")
SHELF_COUNTS: tuple[int, ...] = (2, 3, 5, 8)

TEMPLATE_DOMAIN = TemplateDomain(
    (
        component_slot("carcass_form", CARCASS_FORMS),
        component_slot("front_treatment", FRONT_TREATMENTS),
        component_slot("shelf_mechanism", SHELF_MECHANISMS),
        component_slot("base_style", BASE_STYLES),
        component_slot("back_panel", BACK_PANELS),
        multiplicity_slot("shelf_count", SHELF_COUNTS, item_slot="shelf_mechanism"),
    )
)

# Independent continuous parameters (honest dimensions; not core/raw domain).
_WIDTH_RANGE = (0.62, 1.60)
_DEPTH_RANGE = (0.26, 0.58)
_HEIGHT_RANGE = (1.20, 2.30)
_SHELF_THICKNESS_RANGE = (0.018, 0.032)

_PANEL_T = 0.020  # side / partition panel thickness
_TOP_T = 0.036  # top cap thickness
_BACK_T = 0.016
_DOOR_T = 0.028  # door frame thickness (source 005 L62-L89: 0.028)
_GLASS_T = 0.006
_DOOR_PROUD = 0.008  # door back face stands this far in front of the case face
_DOOR_GAP = 0.012  # centre seam between paired leaves (source 005 L469-L475)
_FACE_POST_W = 0.020  # front face-frame post on each aperture edge
_FACE_POST_D = 0.022  # post depth behind the case face
_HINGE_R = 0.009
_HINGE_LEN = 0.090
_HINGE_PIN_R = 0.0020  # carcass hinge pin running inside the door barrel
_PILASTER_T = 0.012  # adjustable-shelf standard on the interior side face
_PILASTER_ENGAGE = 0.002  # shelf end captured by the pilaster at every pose
_RUNNER_T = 0.020
_RUNNER_ENGAGE = 0.002  # drawer side captured by its carcass runner
_SHELF_TRAVEL = 0.055  # adjustable shelf half travel
_DRAWER_WALL = 0.014
_DOOR_SWING = 1.62  # rad, outward
_FLAP_SWING = 1.30  # rad, up and forward
_MIN_CLEAR_PITCH = 0.060  # geometric floor: shelf travel + board must fit a bay


# Fronts whose mechanism consumes interior volume: their drawers reserve the
# bottom of the case, so the shelf stack starts above the reserved band.
DRAWER_FRONTS: frozenset[str] = frozenset({"upper_glass_base_drawers", "open_shelving"})


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _reserved_lower(front_treatment: str, body_span: float) -> float:
    """Interior height the front assembly consumes at the bottom of the case."""
    if front_treatment not in DRAWER_FRONTS:
        return 0.0
    return _clamp(0.34 * body_span, 0.24, 0.52)


@dataclass(frozen=True)
class Config:
    carcass_form: CarcassForm = "rectangular_upright"
    front_treatment: FrontTreatment = "upper_glass_base_drawers"
    shelf_mechanism: ShelfMechanism = "fixed_shelves"
    base_style: BaseStyle = "plinth"
    back_panel: BackPanel = "solid_back"
    shelf_count: int = 3
    width_m: float | None = None
    depth_m: float | None = None
    height_m: float | None = None
    shelf_thickness_m: float | None = None
    name: str = "pictureX_0611_bookcase"


@dataclass(frozen=True)
class ResolvedConfig:
    carcass_form: CarcassForm
    front_treatment: FrontTreatment
    shelf_mechanism: ShelfMechanism
    base_style: BaseStyle
    back_panel: BackPanel
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
    rng = random.Random(seed ^ 0xB00C_2026)
    return Config(
        carcass_form=choices["carcass_form"],
        front_treatment=choices["front_treatment"],
        shelf_mechanism=choices["shelf_mechanism"],
        base_style=choices["base_style"],
        back_panel=choices["back_panel"],
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


def _base_lift(base_style: BaseStyle, carcass_form: CarcassForm, height: float) -> float:
    """Floor-to-case lift; the highboy asks its base for a taller stance."""
    base = {"plinth": 0.075, "legs": 0.135, "toe_kick": 0.095}[base_style]
    if carcass_form == "legged_highboy":
        base += 0.150
    if carcass_form == "barrister":
        base = max(0.055, base * 0.75)
    return _clamp(base, 0.045, 0.30 * height)


def resolve_config(config: Config) -> ResolvedConfig:
    TEMPLATE_DOMAIN.validate(
        {
            "carcass_form": config.carcass_form,
            "front_treatment": config.front_treatment,
            "shelf_mechanism": config.shelf_mechanism,
            "base_style": config.base_style,
            "back_panel": config.back_panel,
            "shelf_count": config.shelf_count,
        }
    )
    width = 0.980 if config.width_m is None else float(config.width_m)
    depth = 0.420 if config.depth_m is None else float(config.depth_m)
    height = 1.900 if config.height_m is None else float(config.height_m)
    shelf_t = 0.024 if config.shelf_thickness_m is None else float(config.shelf_thickness_m)
    _range_check("width_m", width, _WIDTH_RANGE)
    _range_check("depth_m", depth, _DEPTH_RANGE)
    _range_check("height_m", height, _HEIGHT_RANGE)
    _range_check("shelf_thickness_m", shelf_t, _SHELF_THICKNESS_RANGE)

    lift = _base_lift(config.base_style, config.carcass_form, height)
    # Host capacity: a shelf bay must still take a book, so the case grows to the
    # height its own shelf count needs instead of crushing the bays.
    count_for_height = int(config.shelf_count)
    min_pitch = shelf_t + _MIN_CLEAR_PITCH
    for _ in range(4):
        span = max(height - _TOP_T - lift, 0.05)
        reserved = _reserved_lower(config.front_treatment, span)
        required_height = lift + _TOP_T + reserved + min_pitch * float(count_for_height + 1) + 0.002
        if height >= required_height - 1e-9:
            break
        height = required_height
    body_z0 = lift
    body_z1 = height - _TOP_T
    reserved = _reserved_lower(config.front_treatment, body_z1 - body_z0)
    shelf_zone_lo = body_z0 + reserved
    interior_half = width / 2.0 - _PANEL_T
    interior_depth = depth - _BACK_T
    count = int(config.shelf_count)
    pitch = (body_z1 - shelf_zone_lo) / float(count + 1)
    return ResolvedConfig(
        carcass_form=config.carcass_form,
        front_treatment=config.front_treatment,
        shelf_mechanism=config.shelf_mechanism,
        base_style=config.base_style,
        back_panel=config.back_panel,
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
        ("carcass_form", config.carcass_form),
        ("front_treatment", config.front_treatment),
        ("shelf_mechanism", config.shelf_mechanism),
        ("base_style", config.base_style),
        ("back_panel", config.back_panel),
        ("shelf_count", int(config.shelf_count)),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, object], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# --------------------------------------------------------------------------- #
# Materials and primitive helpers
# --------------------------------------------------------------------------- #
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
    part.visual(Box(size), origin=Origin(xyz=xyz, rpy=rpy), material=material, name=name, material_class_id="wood.polished_varnished")


def _cyl(part, radius, length, xyz, material: str, name: str, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=Origin(xyz=xyz, rpy=rpy),
        material=material,
        name=name, material_class_id="metal.brass_aged",
    )


def _profile_panel(
    part,
    profile: list[tuple[float, float]],
    thickness: float,
    xyz,
    material: str,
    name: str,
    rpy=(0.0, 0.0, 0.0),
) -> None:
    """Extrude an XZ profile through Y for tapered panels and stiles."""
    geometry = ExtrudeGeometry(profile, thickness, center=True).rotate_x(math.pi / 2.0)
    part.visual(
        mesh_from_geometry(geometry, name),
        origin=Origin(xyz=xyz, rpy=rpy),
        material=material,
        name=name, material_class_id="wood.polished_varnished",
    )


@dataclass(frozen=True)
class _ShelfRow:
    z: float
    x_center: float
    half_width: float
    y_center: float
    depth: float
    yaw: float = 0.0
    adjustable_inset: float = 0.0


@dataclass(frozen=True)
class _BackSurface:
    """One locally planar rear support surface owned by a carcass family."""

    name: str
    center: tuple[float, float, float]
    width: float
    height: float
    thickness: float = _BACK_T
    roll: float = 0.0
    yaw: float = 0.0
    top_width: float | None = None


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
    front_yaw: float = 0.0
    back_surfaces: tuple[_BackSurface, ...] = ()


def _front_vectors(frame: _Frame) -> tuple[tuple[float, float], tuple[float, float]]:
    """Return local front tangent (+X) and outward normal (+Y) in world XY."""
    tangent = (math.cos(frame.front_yaw), math.sin(frame.front_yaw))
    normal = (-math.sin(frame.front_yaw), math.cos(frame.front_yaw))
    return tangent, normal


def _front_point(
    frame: _Frame,
    local_x: float,
    normal_offset: float = 0.0,
    *,
    z: float | None = None,
) -> tuple[float, float] | tuple[float, float, float]:
    tangent, normal = _front_vectors(frame)
    x = frame.aperture_x_center + tangent[0] * local_x + normal[0] * normal_offset
    y = frame.front_y + tangent[1] * local_x + normal[1] * normal_offset
    if z is None:
        return (x, y)
    return (x, y, z)


def _row_point(
    row: _ShelfRow,
    local_x: float = 0.0,
    local_y: float = 0.0,
    *,
    z: float | None = None,
) -> tuple[float, float] | tuple[float, float, float]:
    tangent = (math.cos(row.yaw), math.sin(row.yaw))
    normal = (-math.sin(row.yaw), math.cos(row.yaw))
    x = row.x_center + tangent[0] * local_x + normal[0] * local_y
    y = row.y_center + tangent[1] * local_x + normal[1] * local_y
    if z is None:
        return (x, y)
    return (x, y, z)


def _surface_basis(
    surface: _BackSurface,
) -> tuple[
    tuple[float, float, float],
    tuple[float, float, float],
    tuple[float, float, float],
]:
    """Local XYZ basis for a rear surface using Rz(yaw) * Rx(roll)."""
    cy = math.cos(surface.yaw)
    sy = math.sin(surface.yaw)
    cr = math.cos(surface.roll)
    sr = math.sin(surface.roll)
    return (
        (cy, sy, 0.0),
        (-sy * cr, cy * cr, sr),
        (sy * sr, -cy * sr, cr),
    )


def _surface_point(
    surface: _BackSurface,
    local_x: float = 0.0,
    local_y: float = 0.0,
    local_z: float = 0.0,
) -> tuple[float, float, float]:
    basis_x, basis_y, basis_z = _surface_basis(surface)
    return tuple(
        surface.center[index]
        + basis_x[index] * local_x
        + basis_y[index] * local_y
        + basis_z[index] * local_z
        for index in range(3)
    )


def _surface_width_at(surface: _BackSurface, fraction: float) -> float:
    """Width of a rectangular or symmetrically tapered rear surface."""
    top_width = surface.width if surface.top_width is None else surface.top_width
    return surface.width + (top_width - surface.width) * _clamp(fraction, 0.0, 1.0)


def _default_back_surface(r: ResolvedConfig) -> _BackSurface:
    return _BackSurface(
        name="rear",
        center=(
            0.0,
            -r.depth_m / 2.0 + _BACK_T / 2.0,
            (r.body_z0_m + r.body_z1_m) / 2.0,
        ),
        width=r.width_m - 2.0 * _PANEL_T + 0.004,
        height=r.body_z1_m - r.body_z0_m,
    )


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


def _carcass_form_rectangular_upright_build(carcass, r: ResolvedConfig, mats) -> _Frame:
    """005 L240-L324 / 002 L152-L218: one upright box carrying the shelf stack."""
    half_x = r.width_m / 2.0
    y_center = 0.0
    depth = r.depth_m
    _add_side_supports(
        carcass,
        r,
        mats,
        half_x=half_x,
        z0=r.body_z0_m,
        z1=r.body_z1_m,
        depth=depth,
        y_center=y_center,
    )
    _add_top_and_deck(
        carcass,
        r,
        mats,
        half_x=half_x,
        depth=depth,
        y_center=y_center,
        z_top=r.body_z1_m,
        z_deck=r.body_z0_m,
    )
    # Raised front edge bands: the framed slab construction of 005 L254-L267.
    for index, sign in enumerate((-1.0, 1.0)):
        _box(
            carcass,
            (0.014, 0.040, r.body_z1_m - r.body_z0_m),
            (
                sign * (half_x - _PANEL_T + 0.007),
                depth / 2.0 - 0.020,
                (r.body_z0_m + r.body_z1_m) / 2.0,
            ),
            mats["edge"],
            f"front_band_{index}",
        )
    split = _split_z(r, 0.40)
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


def _carcass_form_two_tier_hutch_build(carcass, r: ResolvedConfig, mats) -> _Frame:
    """003 L194-L297: upper and lower carcass split by a mid divider shelf."""
    half_x = r.width_m / 2.0
    depth = r.depth_m
    # The source hutch uses two separate apertures but keeps their face frames
    # almost coplanar.  A deep setback made the upper doors float in front of
    # the case; retain only the source-like 20 mm rear reduction.
    upper_depth = max(0.180, depth - 0.020)
    split = _split_z(r, 0.44)
    lower_y = 0.0
    upper_y = depth / 2.0 - upper_depth / 2.0

    _add_side_supports(
        carcass,
        r,
        mats,
        half_x=half_x,
        z0=r.body_z0_m,
        z1=split,
        depth=depth,
        y_center=lower_y,
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
        prefix="",
    )
    _box(
        carcass,
        (half_x * 2.0, depth, r.shelf_thickness_m * 1.6),
        (0.0, lower_y, split),
        mats["edge"],
        "mid_divider",
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
    divider_clear = r.shelf_thickness_m * 1.6 + _SHELF_TRAVEL + 0.014
    rows = []
    for index, z in enumerate(_shelf_z_values(r)):
        if abs(z - split) < divider_clear:
            z = split + divider_clear
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


def _carcass_form_legged_highboy_build(carcass, r: ResolvedConfig, mats) -> _Frame:
    """004 L269-L477: the case rides on four turned legs under a crown band."""
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
    # Crown band over the top cap and a skirt apron under the case.
    _box(
        carcass,
        (half_x * 2.0 + 0.030, depth + 0.024, 0.055),
        (0.0, 0.0, r.body_z1_m + _TOP_T + 0.0275),
        mats["edge"],
        "crown_band",
    )
    _box(
        carcass,
        (half_x * 2.0 - 0.020, depth - 0.020, 0.045),
        (0.0, 0.0, r.body_z0_m - 0.0225),
        mats["edge"],
        "skirt_apron",
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


def _bay_count(r: ResolvedConfig) -> int:
    return int(_clamp(round(r.width_m / 0.46), 2, 4))


def _carcass_form_grid_hutch_build(carcass, r: ResolvedConfig, mats) -> _Frame:
    """006 L392-L542: side-by-side bays split by full-depth vertical partitions."""
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
    bays = _bay_count(r)
    bay_width = (r.interior_half_x_m * 2.0) / float(bays)
    partition_z0 = (
        r.body_z0_m + r.reserved_lower_m + 0.012
        if r.front_treatment in DRAWER_FRONTS
        else r.body_z0_m
    )
    partition_h = max(r.body_z1_m - partition_z0, 0.10)
    for index in range(1, bays):
        x = -r.interior_half_x_m + bay_width * float(index)
        _box(
            carcass,
            (_PANEL_T, depth - _BACK_T, partition_h),
            (x, -_BACK_T / 2.0, partition_z0 + partition_h / 2.0),
            mats["wood"],
            f"partition_{index - 1}",
        )
    split = _split_z(r, 0.38)
    upper, lower = _bands(r, split)
    row_depth, row_y = _row_span(r, depth / 2.0, -depth / 2.0)
    rows = []
    for index, z in enumerate(_shelf_z_values(r)):
        bay = index % bays
        x_center = -r.interior_half_x_m + bay_width * (float(bay) + 0.5)
        rows.append(
            _ShelfRow(
                z=z,
                x_center=x_center,
                half_width=bay_width / 2.0 - _PANEL_T / 2.0,
                y_center=row_y,
                depth=row_depth,
            )
        )
    return _Frame(
        front_y=depth / 2.0,
        aperture_half_x=r.interior_half_x_m,
        aperture_x_center=0.0,
        upper_band=upper,
        lower_band=lower,
        shelf_rows=tuple(rows),
        side_support_x=(-half_x + _PANEL_T, half_x - _PANEL_T),
        pilaster_half_x=r.interior_half_x_m,
    )


def _carcass_form_ladder_build(carcass, r: ResolvedConfig, mats) -> _Frame:
    """rec_bookcase_var_ladder L64-L295: raked stiles over a vertical base box."""
    half_x = r.width_m / 2.0
    depth = r.depth_m
    box_top = r.body_z0_m + max(
        _clamp(0.30 * (r.body_z1_m - r.body_z0_m), 0.28, 0.62),
        r.reserved_lower_m + 0.040,
    )
    # Vertical base box: the ladder's own cabinet, and the front aperture host.
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
    # Raked stiles: one trapezoidal profile per side follows the source loft
    # without the stepped silhouette produced by stacked box approximations.
    rake = _clamp(0.10 * (r.body_z1_m - box_top), 0.05, 0.16)
    stile_h = r.body_z1_m - box_top
    tilt = math.atan2(rake, stile_h)
    top_shrink = 0.24
    stile_width = 0.038
    base_center_x = half_x - 0.038
    top_center_x = base_center_x * (1.0 - top_shrink)
    for side, sign in enumerate((-1.0, 1.0)):
        bottom_x = sign * base_center_x
        top_x = sign * top_center_x
        _profile_panel(
            carcass,
            [
                (bottom_x - stile_width / 2.0, -stile_h / 2.0),
                (bottom_x + stile_width / 2.0, -stile_h / 2.0),
                (top_x + stile_width / 2.0, stile_h / 2.0),
                (top_x - stile_width / 2.0, stile_h / 2.0),
            ],
            0.075,
            (
                0.0,
                depth / 2.0 - 0.045 - rake / 2.0,
                box_top + stile_h / 2.0,
            ),
            mats["wood"],
            f"side_support_raked_{side}",
            rpy=(tilt, 0.0, 0.0),
        )
    split = (
        r.body_z0_m + r.reserved_lower_m
        if r.reserved_lower_m > 0.0
        else r.body_z0_m + 0.5 * (box_top - r.body_z0_m)
    )
    upper = (split + 0.010, box_top - 0.012)
    lower = (r.body_z0_m + 0.010, split - 0.010)
    rows = []
    deck_clear = r.shelf_thickness_m * 1.5 + _SHELF_TRAVEL + 0.014
    z_values = [
        z if abs(z - box_top) > deck_clear else box_top + deck_clear for z in _shelf_z_values(r)
    ]
    for z in z_values:
        if z <= box_top:
            box_row_depth, box_row_y = _row_span(r, depth / 2.0, -depth / 2.0)
            rows.append(
                _ShelfRow(
                    z=z,
                    x_center=0.0,
                    half_width=r.interior_half_x_m,
                    y_center=box_row_y,
                    depth=box_row_depth,
                )
            )
        else:
            frac = (z - box_top) / max(stile_h, 1e-6)
            shrink = 1.0 - 0.28 * frac
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
                    half_width=max(0.10, (half_x - 0.038) * (1.0 - top_shrink * frac) + 0.005),
                    y_center=row_y,
                    depth=row_depth,
                    adjustable_inset=0.035,
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
        back_surfaces=(
            _BackSurface(
                name="ladder_back_base",
                center=(
                    0.0,
                    -depth / 2.0 + _BACK_T / 2.0,
                    (r.body_z0_m + box_top) / 2.0,
                ),
                width=r.width_m - 2.0 * _PANEL_T + 0.004,
                height=box_top - r.body_z0_m,
            ),
            _BackSurface(
                name="ladder_back_upper",
                center=(
                    0.0,
                    -depth / 2.0 + _BACK_T / 2.0 - rake / 2.0,
                    (box_top + r.body_z1_m) / 2.0,
                ),
                width=r.width_m - 2.0 * _PANEL_T + 0.004,
                height=math.hypot(stile_h, rake),
                roll=tilt,
                top_width=(r.width_m - 2.0 * _PANEL_T + 0.004) * (1.0 - top_shrink),
            ),
        ),
    )


def _corner_plan(
    r: ResolvedConfig,
) -> tuple[
    tuple[float, float],
    tuple[float, float],
    tuple[float, float],
    float,
    float,
]:
    """Diagonal-front L-plan fitted inside the configured width/depth bounds."""
    half_x = r.width_m / 2.0
    rear_y = -r.depth_m / 2.0
    front_y = r.depth_m / 2.0
    wing_depth = _clamp(
        0.42 * min(r.width_m, r.depth_m),
        0.10,
        min(r.width_m, r.depth_m) - 2.0 * _PANEL_T,
    )
    left_front = (-half_x + wing_depth, front_y)
    right_rear = (half_x, rear_y + wing_depth)
    dx = right_rear[0] - left_front[0]
    dy = right_rear[1] - left_front[1]
    span = math.hypot(dx, dy)
    center = (
        (left_front[0] + right_rear[0]) / 2.0,
        (left_front[1] + right_rear[1]) / 2.0,
    )
    return left_front, right_rear, center, math.atan2(dy, dx), span


def _carcass_form_corner_build(carcass, r: ResolvedConfig, mats) -> _Frame:
    """rec_bookcase_var_corner L175-L360: two rear wings and a diagonal front."""
    half_x = r.width_m / 2.0
    rear_y = -r.depth_m / 2.0
    front_y = r.depth_m / 2.0
    left_front, right_rear, front_center, front_yaw, diagonal_span = _corner_plan(r)
    wing_depth = left_front[0] + half_x
    body_height = r.body_z1_m - r.body_z0_m
    body_mid_z = (r.body_z0_m + r.body_z1_m) / 2.0

    # The two outer end panels close the ends of the perpendicular rear wings.
    _box(
        carcass,
        (_PANEL_T, wing_depth, body_height),
        (
            half_x - _PANEL_T / 2.0,
            rear_y + wing_depth / 2.0,
            body_mid_z,
        ),
        mats["wood"],
        "side_support_0",
    )
    _box(
        carcass,
        (wing_depth, _PANEL_T, body_height),
        (
            -half_x + wing_depth / 2.0,
            front_y - _PANEL_T / 2.0,
            body_mid_z,
        ),
        mats["wood"],
        "side_support_1",
    )
    _box(
        carcass,
        (_PANEL_T, _PANEL_T, body_height),
        (-half_x + _PANEL_T / 2.0, rear_y + _PANEL_T / 2.0, body_mid_z),
        mats["edge"],
        "rear_corner_post",
    )

    # L-shaped top and deck are expressed as two joined wing slabs.  This keeps
    # the empty front-right quadrant open instead of filling it with a rectangle.
    for level_name, z, thickness, material in (
        ("top", r.body_z1_m + _TOP_T / 2.0, _TOP_T, mats["edge"]),
        (
            "deck",
            r.body_z0_m + r.shelf_thickness_m / 2.0,
            r.shelf_thickness_m,
            mats["wood"],
        ),
    ):
        _box(
            carcass,
            (r.width_m, wing_depth, thickness),
            (0.0, rear_y + wing_depth / 2.0, z),
            material,
            f"{level_name}_wing_x",
        )
        _box(
            carcass,
            (wing_depth, r.depth_m, thickness),
            (-half_x + wing_depth / 2.0, 0.0, z),
            material,
            f"{level_name}_wing_y",
        )

    split = _split_z(r, 0.36)
    upper, lower = _bands(r, split)
    tangent = (math.cos(front_yaw), math.sin(front_yaw))
    outward = (-tangent[1], tangent[0])
    shelf_depth = max(0.08, wing_depth * 0.82)
    shelf_center = (
        front_center[0] - outward[0] * (shelf_depth / 2.0 + 0.006),
        front_center[1] - outward[1] * (shelf_depth / 2.0 + 0.006),
    )
    rows = tuple(
        _ShelfRow(
            z=z,
            x_center=shelf_center[0],
            half_width=max(0.08, diagonal_span / 2.0 - 0.7 * _PANEL_T),
            y_center=shelf_center[1],
            depth=shelf_depth,
            yaw=front_yaw,
        )
        for z in _shelf_z_values(r)
    )

    # Rear panels are supplied as two surfaces so every back-panel candidate
    # follows the L footprint rather than adding one loose rectangular slab.
    back_surfaces = (
        _BackSurface(
            name="corner_back_x",
            center=(
                0.0,
                rear_y + _BACK_T / 2.0,
                body_mid_z,
            ),
            width=r.width_m - _PANEL_T,
            height=body_height,
        ),
        _BackSurface(
            name="corner_back_y",
            center=(
                -half_x + _BACK_T / 2.0,
                0.0,
                body_mid_z,
            ),
            width=r.depth_m - _PANEL_T,
            height=body_height,
            yaw=math.pi / 2.0,
        ),
    )
    return _Frame(
        front_y=front_center[1],
        aperture_half_x=max(0.08, diagonal_span / 2.0 - _FACE_POST_W),
        aperture_x_center=front_center[0],
        upper_band=upper,
        lower_band=lower,
        shelf_rows=rows,
        side_support_x=(-half_x + _PANEL_T, half_x - _PANEL_T),
        pilaster_half_x=max(0.08, diagonal_span / 2.0 - _FACE_POST_W),
        front_yaw=front_yaw,
        back_surfaces=back_surfaces,
    )


def _carcass_form_cube_grid_build(carcass, r: ResolvedConfig, mats) -> _Frame:
    """rec_bookcase_var_cube_grid L210-L363: rows x cols cube matrix."""
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
    cols = int(_clamp(round(r.width_m / 0.40), 2, 4))
    cell_w = (r.interior_half_x_m * 2.0) / float(cols)
    z_values = _shelf_z_values(r)
    divider_z0 = (
        r.body_z0_m + r.reserved_lower_m + 0.012
        if r.front_treatment in DRAWER_FRONTS
        else r.body_z0_m
    )
    divider_h = max(r.body_z1_m - divider_z0, 0.10)
    for col in range(1, cols):
        x = -r.interior_half_x_m + cell_w * float(col)
        _box(
            carcass,
            (_PANEL_T, depth - _BACK_T, divider_h),
            (x, -_BACK_T / 2.0, divider_z0 + divider_h / 2.0),
            mats["wood"],
            f"cell_divider_{col - 1}",
        )
    row_depth, row_y = _row_span(r, depth / 2.0, -depth / 2.0)
    rows = tuple(
        _ShelfRow(
            z=z,
            x_center=-r.interior_half_x_m + cell_w * (float(index % cols) + 0.5),
            half_width=cell_w / 2.0 - _PANEL_T / 2.0,
            y_center=row_y,
            depth=row_depth,
        )
        for index, z in enumerate(z_values)
    )
    split = _split_z(r, 0.34)
    upper, lower = _bands(r, split)
    return _Frame(
        front_y=depth / 2.0,
        aperture_half_x=r.interior_half_x_m,
        aperture_x_center=0.0,
        upper_band=upper,
        lower_band=lower,
        shelf_rows=rows,
        side_support_x=(-half_x + _PANEL_T, half_x - _PANEL_T),
        pilaster_half_x=r.interior_half_x_m,
    )


def _carcass_form_barrister_build(carcass, r: ResolvedConfig, mats) -> _Frame:
    """rec_bookcase_var_barrister L59-L229: a stack of framed sections."""
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
    # One framed section rail per shelf: the stacked-case signature.
    for index, z in enumerate(_shelf_z_values(r)):
        _box(
            carcass,
            (half_x * 2.0 + 0.016, 0.006, 0.030),
            (0.0, depth / 2.0 - 0.004, z + r.shelf_thickness_m / 2.0 + 0.015),
            mats["edge"],
            f"section_rail_{index}",
        )
    split = _split_z(r, 0.30)
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


_CARCASS_BUILDERS = {
    "rectangular_upright": _carcass_form_rectangular_upright_build,
    "two_tier_hutch": _carcass_form_two_tier_hutch_build,
    "legged_highboy": _carcass_form_legged_highboy_build,
    "grid_hutch": _carcass_form_grid_hutch_build,
    "ladder": _carcass_form_ladder_build,
    "corner": _carcass_form_corner_build,
    "cube_grid": _carcass_form_cube_grid_build,
    "barrister": _carcass_form_barrister_build,
}


# --------------------------------------------------------------------------- #
# base_style candidates
# --------------------------------------------------------------------------- #
def _corner_base_wings(
    carcass,
    r: ResolvedConfig,
    mats,
    *,
    height: float,
    z_center: float,
    inset: float,
    prefix: str,
) -> None:
    """Two joined slabs following the corner carcass's L-plan footprint."""
    half_x = r.width_m / 2.0
    rear_y = -r.depth_m / 2.0
    wing_depth = _corner_plan(r)[0][0] + half_x
    _box(
        carcass,
        (
            max(r.width_m - 2.0 * inset, 0.08),
            max(wing_depth - 2.0 * inset, 0.06),
            height,
        ),
        (0.0, rear_y + wing_depth / 2.0, z_center),
        mats["edge"],
        f"{prefix}_wing_x",
    )
    _box(
        carcass,
        (
            max(wing_depth - 2.0 * inset, 0.06),
            max(r.depth_m - 2.0 * inset, 0.08),
            height,
        ),
        (-half_x + wing_depth / 2.0, 0.0, z_center),
        mats["edge"],
        f"{prefix}_wing_y",
    )


def _base_style_plinth_build(carcass, r: ResolvedConfig, mats) -> None:
    if r.carcass_form == "corner":
        _corner_base_wings(
            carcass,
            r,
            mats,
            height=r.base_lift_m,
            z_center=r.base_lift_m / 2.0,
            inset=0.018,
            prefix="corner_plinth",
        )
        return
    half_x = r.width_m / 2.0
    _box(
        carcass,
        (half_x * 2.0 - 0.030, r.depth_m - 0.030, r.base_lift_m),
        (0.0, -0.004, r.base_lift_m / 2.0),
        mats["edge"],
        "base_plinth",
    )


def _base_style_legs_build(carcass, r: ResolvedConfig, mats) -> None:
    half_x = r.width_m / 2.0
    radius = _clamp(0.030, 0.020, r.depth_m * 0.09)
    if r.carcass_form == "corner":
        rear_y = -r.depth_m / 2.0
        front_y = r.depth_m / 2.0
        margin = radius + 0.020
        leg_points = (
            (-half_x + margin, rear_y + margin),
            (half_x - margin, rear_y + margin),
            (-half_x + margin, front_y - margin),
        )
    else:
        leg_points = tuple(
            (
                sx * (half_x - radius - 0.020),
                sy * (r.depth_m / 2.0 - radius - 0.020),
            )
            for sx, sy in ((-1.0, -1.0), (-1.0, 1.0), (1.0, -1.0), (1.0, 1.0))
        )
    for index, (x, y) in enumerate(leg_points):
        _cyl(
            carcass,
            radius,
            r.base_lift_m,
            (x, y, r.base_lift_m / 2.0),
            mats["wood"],
            f"turned_leg_{index}",
        )
        # Turned collar: the source legs are profiled, not plain dowels.
        _cyl(
            carcass,
            radius * 1.25,
            0.030,
            (x, y, r.base_lift_m - 0.040),
            mats["edge"],
            f"leg_collar_{index}",
        )
    if r.carcass_form == "corner":
        _corner_base_wings(
            carcass,
            r,
            mats,
            height=0.030,
            z_center=r.base_lift_m - 0.015,
            inset=0.030,
            prefix="corner_leg_rail",
        )
    else:
        _box(
            carcass,
            (half_x * 2.0 - 0.060, r.depth_m - 0.060, 0.030),
            (0.0, 0.0, r.base_lift_m - 0.015),
            mats["edge"],
            "leg_rail",
        )


def _base_style_toe_kick_build(carcass, r: ResolvedConfig, mats) -> None:
    if r.carcass_form == "corner":
        _corner_base_wings(
            carcass,
            r,
            mats,
            height=r.base_lift_m,
            z_center=r.base_lift_m / 2.0,
            inset=0.035,
            prefix="corner_toe_kick",
        )
        _, _, front_center, front_yaw, diagonal_span = _corner_plan(r)
        outward = (-math.sin(front_yaw), math.cos(front_yaw))
        _box(
            carcass,
            (max(diagonal_span - 0.050, 0.08), 0.020, 0.055),
            (
                front_center[0] - outward[0] * 0.018,
                front_center[1] - outward[1] * 0.018,
                r.base_lift_m - 0.0275,
            ),
            mats["wood"],
            "corner_toe_kick_apron",
            rpy=(0.0, 0.0, front_yaw),
        )
        return
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
    "plinth": _base_style_plinth_build,
    "legs": _base_style_legs_build,
    "toe_kick": _base_style_toe_kick_build,
}


# --------------------------------------------------------------------------- #
# back_panel candidates
# --------------------------------------------------------------------------- #
def _back_panel_solid_back_build(carcass, r: ResolvedConfig, mats, frame: _Frame) -> None:
    for surface in frame.back_surfaces or (_default_back_surface(r),):
        top_width = surface.width if surface.top_width is None else surface.top_width
        if abs(top_width - surface.width) < 1e-6:
            _box(
                carcass,
                (surface.width, surface.thickness, surface.height),
                surface.center,
                mats["back"],
                f"{surface.name}__solid_panel",
                rpy=(surface.roll, 0.0, surface.yaw),
            )
            continue
        _profile_panel(
            carcass,
            [
                (-surface.width / 2.0, -surface.height / 2.0),
                (surface.width / 2.0, -surface.height / 2.0),
                (top_width / 2.0, surface.height / 2.0),
                (-top_width / 2.0, surface.height / 2.0),
            ],
            surface.thickness,
            surface.center,
            mats["back"],
            f"{surface.name}__solid_panel",
            rpy=(surface.roll, 0.0, surface.yaw),
        )


def _back_panel_open_back_build(carcass, r: ResolvedConfig, mats, frame: _Frame) -> None:
    # Each carcass supplies its own rear planes. A light perimeter frame follows
    # every plane, so corner and raked cases remain visibly open without loose
    # world-axis braces crossing outside the case.
    for surface in frame.back_surfaces or (_default_back_surface(r),):
        rail = min(0.030, surface.width * 0.12, surface.height * 0.12)
        top_width = surface.width if surface.top_width is None else surface.top_width
        if abs(top_width - surface.width) >= 1e-6:
            for index, (fraction, local_z) in enumerate(
                (
                    (0.0, -surface.height / 2.0 + rail / 2.0),
                    (1.0, surface.height / 2.0 - rail / 2.0),
                )
            ):
                _box(
                    carcass,
                    (_surface_width_at(surface, fraction), surface.thickness, rail),
                    _surface_point(surface, local_z=local_z),
                    mats["back"],
                    f"{surface.name}__open_rail_h_{index}",
                    rpy=(surface.roll, 0.0, surface.yaw),
                )
            _box(
                carcass,
                (rail, surface.thickness, surface.height),
                surface.center,
                mats["back"],
                f"{surface.name}__open_center_stile",
                rpy=(surface.roll, 0.0, surface.yaw),
            )
            continue
        for index, local_z in enumerate(
            (-surface.height / 2.0 + rail / 2.0, surface.height / 2.0 - rail / 2.0)
        ):
            _box(
                carcass,
                (surface.width, surface.thickness, rail),
                _surface_point(surface, local_z=local_z),
                mats["back"],
                f"{surface.name}__open_rail_h_{index}",
                rpy=(surface.roll, 0.0, surface.yaw),
            )
        for index, local_x in enumerate(
            (-surface.width / 2.0 + rail / 2.0, surface.width / 2.0 - rail / 2.0)
        ):
            _box(
                carcass,
                (rail, surface.thickness, surface.height),
                _surface_point(surface, local_x=local_x),
                mats["back"],
                f"{surface.name}__open_rail_v_{index}",
                rpy=(surface.roll, 0.0, surface.yaw),
            )


def _back_panel_beadboard_back_build(carcass, r: ResolvedConfig, mats, frame: _Frame) -> None:
    """006 L48-L91: vertical battens with raised beads instead of a plain board."""
    for surface in frame.back_surfaces or (_default_back_surface(r),):
        battens = int(_clamp(round(surface.width / 0.11), 4, 14))
        pitch = surface.width / float(battens)
        top_width = surface.width if surface.top_width is None else surface.top_width
        bottom_half = surface.width / 2.0
        top_half = top_width / 2.0
        for index in range(battens):
            local_x = -surface.width / 2.0 + pitch * (float(index) + 0.5)
            if abs(top_width - surface.width) < 1e-6 or abs(local_x) <= top_half:
                batten_h = surface.height
            else:
                fraction = (bottom_half - abs(local_x)) / max(bottom_half - top_half, 1e-6)
                batten_h = max(0.04, surface.height * _clamp(fraction, 0.0, 1.0))
            local_z = -surface.height / 2.0 + batten_h / 2.0
            _box(
                carcass,
                (pitch * 0.94, surface.thickness * 0.75, batten_h),
                _surface_point(surface, local_x=local_x, local_z=local_z),
                mats["back"],
                f"{surface.name}__beadboard_batten_{index}",
                rpy=(surface.roll, 0.0, surface.yaw),
            )
            _box(
                carcass,
                (0.008, surface.thickness * 0.5, batten_h),
                _surface_point(
                    surface,
                    local_x=local_x + pitch * 0.47,
                    local_y=surface.thickness * 0.35,
                    local_z=local_z,
                ),
                mats["edge"],
                f"{surface.name}__beadboard_bead_{index}",
                rpy=(surface.roll, 0.0, surface.yaw),
            )


_BACK_BUILDERS = {
    "solid_back": _back_panel_solid_back_build,
    "open_back": _back_panel_open_back_build,
    "beadboard_back": _back_panel_beadboard_back_build,
}


# --------------------------------------------------------------------------- #
# shelf_mechanism candidates
# --------------------------------------------------------------------------- #
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
            rpy=(0.0, 0.0, row.yaw),
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
        board_half = max(
            row.half_width - _FACE_POST_W / 2.0 - 0.002 - row.adjustable_inset,
            0.04,
        )
        # The standard bridges from just inside the board edge out to the case
        # wall, so it is both a real support and part of the connected carcass.
        stand_inner = board_half - _PILASTER_ENGAGE
        stand_outer = row.half_width + _PANEL_T / 2.0 + 0.004
        stand_w = max(stand_outer - stand_inner, _PILASTER_T)
        for side, sign in enumerate((-1.0, 1.0)):
            _box(
                carcass,
                (stand_w, row.depth * 0.85, 2.0 * travel + r.shelf_thickness_m + 0.060),
                _row_point(
                    row,
                    local_x=sign * (stand_inner + stand_w / 2.0),
                    z=row.z,
                ),
                mats["edge"],
                f"shelf_standard_{index}_{side}",
                rpy=(0.0, 0.0, row.yaw),
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
            tangent_u=(math.cos(row.yaw), math.sin(row.yaw), 0.0),
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
            motion_limits=MotionLimits(effort=40.0, velocity=0.2, lower=-travel, upper=travel),
            motion_properties=MotionProperties(damping=1.5, friction=0.6),
            meta={"mechanism": "adjustable shelf height", "shelf_index": index},
        )
        joints.append(joint_name)
    return joints


_SHELF_BUILDERS = {
    "fixed_shelves": _shelf_mechanism_fixed_shelves_build,
    "adjustable_shelves": _shelf_mechanism_adjustable_shelves_build,
}


# --------------------------------------------------------------------------- #
# front_treatment helpers — doors, flaps and drawers on the aperture interface
# --------------------------------------------------------------------------- #
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
    _box(
        part, (rail, _DOOR_T, height), (outer_x, body_y, height / 2.0), mats["edge"], "outer_stile"
    )
    _box(
        part, (rail, _DOOR_T, height), (inner_x, body_y, height / 2.0), mats["edge"], "inner_stile"
    )
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
    frame: _Frame,
    local_x: float,
    axis_offset: float,
    z: float,
    size: tuple[float, float] = (0.014, 0.012),
    tag: str = "",
) -> None:
    """Cheek bracket carrying a hinge pin off the case face (005 L307-L315).

    It reaches exactly to the pin axis, so it grips the pin while staying clear
    of the door barrel, which is offset along the pin.
    """
    normal_lo = -0.012
    normal_hi = axis_offset + _HINGE_PIN_R * 0.5
    center = _front_point(
        frame,
        local_x,
        (normal_lo + normal_hi) / 2.0,
        z=z,
    )
    _box(
        carcass,
        (size[0], max(normal_hi - normal_lo, 0.004), size[1]),
        center,
        mats["edge"],
        f"hinge_bracket_{tag}_{'l' if local_x < 0 else 'r'}_{int(z * 1000)}",
        rpy=(0.0, 0.0, frame.front_yaw),
    )


def _add_hinge_leaves(
    carcass,
    mats,
    *,
    frame: _Frame,
    local_x: float,
    axis_offset: float,
    z_base: float,
    height: float,
) -> None:
    """Carcass-side hinge pins running through the door barrels (003 L162-L171).

    The pin is coaxial with the barrel, so the door keeps a real support path at
    every angle, and it is thin enough (2*_HINGE_PIN_R) that the captured
    engagement stays well inside the collision tolerance.
    """
    barrel = _barrel_length(height)
    hinge_xy = _front_point(frame, local_x, axis_offset)
    for index, fraction in enumerate((0.18, 0.82)):
        z = z_base + height * fraction
        _cyl(
            carcass,
            _HINGE_PIN_R,
            barrel + 0.060,
            (hinge_xy[0], hinge_xy[1], z),
            mats["brass"],
            f"hinge_pin_{index}_{'l' if local_x < 0 else 'r'}_{int(z * 1000)}",
        )
        bracket_z = z - barrel / 2.0 - 0.010 if index == 0 else z + barrel / 2.0 + 0.010
        _pin_bracket(
            carcass,
            mats,
            frame=frame,
            local_x=local_x,
            axis_offset=axis_offset,
            z=bracket_z,
            tag=str(index),
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
    edge_local_x = -frame.aperture_half_x if side == 0 else frame.aperture_half_x
    axis_offset = _DOOR_PROUD + 0.002
    hinge_xy = _front_point(frame, edge_local_x, axis_offset)
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
        frame=frame,
        local_x=edge_local_x,
        axis_offset=axis_offset,
        z_base=z_lo,
        height=height,
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
        point=(hinge_xy[0], hinge_xy[1], z_lo),
        axis=axis,
        radial=(*_front_vectors(frame)[0], 0.0),
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
    axis_offset = _DOOR_PROUD + 0.002
    sign = -1.0 if side == 0 else 1.0
    center_local_x = sign * (leaf_width / 2.0 + _DOOR_GAP / 2.0)
    hinge_xy = _front_point(frame, center_local_x, axis_offset)
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
        pin_local_x = center_local_x + s * (leaf_width / 2.0 - barrel / 2.0 - 0.012)
        pin_xy = _front_point(frame, pin_local_x, axis_offset)
        _cyl(
            carcass,
            _HINGE_PIN_R,
            barrel + 0.060,
            (pin_xy[0], pin_xy[1], z_hi),
            mats["brass"],
            f"flap_hinge_pin_{side}_{index}",
            rpy=(0.0, math.pi / 2.0, frame.front_yaw),
        )
        _pin_bracket(
            carcass,
            mats,
            frame=frame,
            local_x=pin_local_x + s * (barrel / 2.0 + 0.010),
            axis_offset=axis_offset,
            z=z_hi,
            size=(0.012, 0.014),
            tag=f"flap{side}{index}",
        )

    joint_name = f"{name}__flap_hinge"
    provider = AxisInterface(
        name=f"{joint_name}__provider",
        point=(hinge_xy[0], hinge_xy[1], z_hi),
        axis=(*_front_vectors(frame)[0], 0.0),
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
    nominal_depth = _clamp(0.66 * r.depth_m, 0.14, r.depth_m - 0.05)
    # A diagonal corner aperture tapers immediately behind its front. Keep the
    # tray inside the depth supplied by that host while retaining the full-width
    # false front; otherwise a rectangular tray cuts through one rear wing.
    if abs(frame.front_yaw) > 1e-6 and frame.shelf_rows:
        box_depth = max(
            0.070,
            min(nominal_depth, min(row.depth for row in frame.shelf_rows) - 0.018),
        )
        travel = max(0.030, min(0.46 * r.depth_m, box_depth - 0.035))
    else:
        box_depth = nominal_depth
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
    runner_inner = box_half - _RUNNER_ENGAGE
    runner_outer = max(frame.aperture_half_x - 0.006, runner_inner + _RUNNER_T)
    runner_w = runner_outer - runner_inner
    for index, sign in enumerate((-1.0, 1.0)):
        runner_center = _front_point(
            frame,
            sign * (runner_inner + runner_w / 2.0),
            -runner_len / 2.0 - 0.005,
            z=z_center - box_height / 2.0 + 0.012,
        )
        _box(
            carcass,
            (runner_w, runner_len, 0.030),
            runner_center,
            mats["edge"],
            f"{name.rsplit('__', 1)[-1]}_runner_{index}",
            rpy=(0.0, 0.0, frame.front_yaw),
        )

    joint_name = f"{name}__slide"
    model.articulation(
        joint_name,
        ArticulationType.PRISMATIC,
        parent=carcass,
        child=drawer,
        origin=Origin(
            xyz=_front_point(frame, 0.0, 0.004, z=z_center),
            rpy=(0.0, 0.0, frame.front_yaw),
        ),
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
    z_lo = min(frame.lower_band[0], frame.upper_band[0])
    z_hi = max(frame.lower_band[1], frame.upper_band[1])
    post_height = max(z_hi - z_lo, 0.10)
    normal_offset = -_FACE_POST_D / 2.0 + 0.002
    for index, sign in enumerate((-1.0, 1.0)):
        _box(
            carcass,
            (_FACE_POST_W, _FACE_POST_D, post_height),
            _front_point(
                frame,
                sign * frame.aperture_half_x,
                normal_offset,
                z=(z_lo + z_hi) / 2.0,
            ),
            mats["edge"],
            f"face_post_{index}",
            rpy=(0.0, 0.0, frame.front_yaw),
        )
    for index, z in (
        (0, z_lo + 0.015),
        (1, z_hi - 0.015),
    ):
        _box(
            carcass,
            (
                frame.aperture_half_x * 2.0 + _FACE_POST_W,
                _FACE_POST_D * 0.8,
                0.030,
            ),
            _front_point(frame, 0.0, normal_offset, z=z),
            mats["edge"],
            f"face_rail_{index}",
            rpy=(0.0, 0.0, frame.front_yaw),
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
def _front_treatment_full_glass_doors_build(model, carcass, r, mats, frame) -> list[str]:
    """001 L64-L459: paired full-height glazed doors over the whole aperture."""
    band = (frame.lower_band[0], frame.upper_band[1])
    return [
        _add_swing_door(
            model,
            carcass,
            r,
            mats,
            frame,
            name=f"front_treatment__full_glass_doors__door_{side}",
            band=band,
            side=side,
            leaf_width=_leaf_width(frame),
            glazed=True,
        )
        for side in (0, 1)
    ]


def _front_treatment_upper_glass_base_drawers_build(model, carcass, r, mats, frame) -> list[str]:
    """005 L326-L398: upper glazed doors over prismatic base drawers."""
    joints = [
        _add_swing_door(
            model,
            carcass,
            r,
            mats,
            frame,
            name=f"front_treatment__upper_glass_base_drawers__door_{side}",
            band=frame.upper_band,
            side=side,
            leaf_width=_leaf_width(frame),
            glazed=True,
        )
        for side in (0, 1)
    ]
    for index, sub in enumerate(_split_band(frame.lower_band, 2)):
        joints.append(
            _add_drawer(
                model,
                carcass,
                r,
                mats,
                frame,
                name=f"front_treatment__upper_glass_base_drawers__drawer_{index}",
                z_center=(sub[0] + sub[1]) / 2.0,
                front_height=(sub[1] - sub[0]) - 0.012,
            )
        )
    return joints


def _front_treatment_glass_top_panel_base_doors_build(model, carcass, r, mats, frame) -> list[str]:
    """003 L298-L367: glazed upper doors above solid lower panel doors."""
    joints = []
    for side in (0, 1):
        joints.append(
            _add_swing_door(
                model,
                carcass,
                r,
                mats,
                frame,
                name=f"front_treatment__glass_top_panel_base_doors__upper_door_{side}",
                band=frame.upper_band,
                side=side,
                leaf_width=_leaf_width(frame),
                glazed=True,
            )
        )
    for side in (0, 1):
        joints.append(
            _add_swing_door(
                model,
                carcass,
                r,
                mats,
                frame,
                name=f"front_treatment__glass_top_panel_base_doors__lower_door_{side}",
                band=frame.lower_band,
                side=side,
                leaf_width=_leaf_width(frame),
                glazed=False,
            )
        )
    return joints


def _front_treatment_open_shelving_build(model, carcass, r, mats, frame) -> list[str]:
    """open_shelving fork L25-L170: exposed shelves plus one base drawer."""
    band = frame.lower_band
    height = min(band[1] - band[0], 0.26)
    z_center = band[0] + height / 2.0
    return [
        _add_drawer(
            model,
            carcass,
            r,
            mats,
            frame,
            name="front_treatment__open_shelving__drawer_0",
            z_center=z_center,
            front_height=height - 0.012,
        )
    ]


def _front_treatment_base_cabinet_doors_build(model, carcass, r, mats, frame) -> list[str]:
    """base_cabinet_doors fork L25-L232: open upper shelves, paired lower doors."""
    return [
        _add_swing_door(
            model,
            carcass,
            r,
            mats,
            frame,
            name=f"front_treatment__base_cabinet_doors__door_{side}",
            band=frame.lower_band,
            side=side,
            leaf_width=_leaf_width(frame),
            glazed=False,
        )
        for side in (0, 1)
    ]


def _front_treatment_flip_up_glass_build(model, carcass, r, mats, frame) -> list[str]:
    """flip_up_glass fork L370-L460: top-pivot glazed flaps over the shelf stack."""
    return [
        _add_flip_flap(
            model,
            carcass,
            r,
            mats,
            frame,
            name=f"front_treatment__flip_up_glass__flap_{side}",
            band=frame.upper_band,
            side=side,
            leaf_width=_leaf_width(frame),
        )
        for side in (0, 1)
    ]


_FRONT_BUILDERS = {
    "full_glass_doors": _front_treatment_full_glass_doors_build,
    "upper_glass_base_drawers": _front_treatment_upper_glass_base_drawers_build,
    "glass_top_panel_base_doors": _front_treatment_glass_top_panel_base_doors_build,
    "open_shelving": _front_treatment_open_shelving_build,
    "base_cabinet_doors": _front_treatment_base_cabinet_doors_build,
    "flip_up_glass": _front_treatment_flip_up_glass_build,
}


# --------------------------------------------------------------------------- #
# Assembly
# --------------------------------------------------------------------------- #
def build_pictureX_0611_bookcase(
    config: Config | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config or config_from_seed(0))
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={
            "category": "pictureX_0611_bookcase",
            "identified_object": "free-standing bookcase",
            "slot_choices": slot_choices_for_config(r),
            "source_layout": "vertical side supports carrying a stack of book shelves",
        },
    )
    mats = _materials(model)
    carcass = model.part(
        f"carcass_form__{r.carcass_form}__carcass",
        meta={"role": "case_body", "form": r.carcass_form},
    )
    frame = _CARCASS_BUILDERS[r.carcass_form](carcass, r, mats)
    _BASE_BUILDERS[r.base_style](carcass, r, mats)
    _BACK_BUILDERS[r.back_panel](carcass, r, mats, frame)
    _add_face_frame(carcass, r, mats, frame)
    _SHELF_BUILDERS[r.shelf_mechanism](model, carcass, r, mats, frame)
    _FRONT_BUILDERS[r.front_treatment](model, carcass, r, mats, frame)
    return model


# --------------------------------------------------------------------------- #
# Author tests / category anchors
# --------------------------------------------------------------------------- #
def _parts_by_role(model: ArticulatedObject, role: str):
    return [part for part in model.parts if part.meta.get("role") == role]


def _visual_names(part) -> set[str]:
    return {visual.name for visual in part.visuals}


def run_pictureX_0611_bookcase_tests(
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
        joint for joint in model.articulations if joint.articulation_type != ArticulationType.FIXED
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
        front_yaw = _corner_plan(r)[3] if r.carcass_form == "corner" else 0.0
        outward = (-math.sin(front_yaw), math.cos(front_yaw))
        outward_travel = (
            (extended[0] - rest[0]) * outward[0] + (extended[1] - rest[1]) * outward[1]
            if rest is not None and extended is not None
            else 0.0
        )
        ctx.check(
            f"{drawer.name} extends toward the front",
            rest is not None
            and extended is not None
            and outward_travel > 0.5 * joint.motion_limits.upper,
            details=(f"rest={rest}, extended={extended}, outward_travel={outward_travel:.4f}"),
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

    if r.carcass_form == "corner":
        expected_back_prefixes = ("corner_back_x__", "corner_back_y__")
        ctx.check(
            "corner carcass back treatment follows both rear wings",
            all(
                any(name.startswith(prefix) for name in names) for prefix in expected_back_prefixes
            ),
            details=f"back visuals={sorted(name for name in names if 'back' in name)}",
        )
        ctx.check(
            "corner front frame follows the diagonal aperture",
            abs(_corner_plan(r)[3]) > 0.05,
            details=f"front_yaw={_corner_plan(r)[3]:.4f}",
        )
    if r.carcass_form == "ladder":
        ctx.check(
            "ladder back treatment follows the raked rear plane",
            any(name.startswith("ladder_back_") for name in names),
            details=f"back visuals={sorted(name for name in names if 'back' in name)}",
        )
    if r.carcass_form == "corner":
        base_prefix = {
            "plinth": "corner_plinth_",
            "legs": "corner_leg_rail_",
            "toe_kick": "corner_toe_kick_",
        }[r.base_style]
        ctx.check(
            "corner base follows the L-plan footprint",
            any(name.startswith(base_prefix) for name in names),
            details=f"base visuals={sorted(name for name in names if 'corner_' in name)}",
        )

    return ctx.report()


TEMPLATE_CORNERS = (
    corner_case(
        "corner_full_glass_doors_with_segmented_solid_back",
        {
            "carcass_form": "corner",
            "front_treatment": "full_glass_doors",
            "shelf_mechanism": "fixed_shelves",
            "base_style": "plinth",
            "back_panel": "solid_back",
            "shelf_count": 5,
            "width_m": 1.25,
            "depth_m": 0.48,
            "height_m": 2.05,
            "shelf_thickness_m": 0.024,
        },
        reason="diagonal full-swing doors paired with two rear-wing solid panels",
    ),
    corner_case(
        "narrow_tall_corner_case_with_flip_up_flaps",
        {
            "carcass_form": "corner",
            "front_treatment": "flip_up_glass",
            "shelf_mechanism": "adjustable_shelves",
            "base_style": "legs",
            "back_panel": "open_back",
            "shelf_count": 8,
            "width_m": 0.62,
            "depth_m": 0.26,
            "height_m": 2.30,
            "shelf_thickness_m": 0.032,
        },
        reason="narrowest L-plan aperture at maximum shelf count with moving shelves and flaps",
    ),
    corner_case(
        "wide_shallow_cube_grid_with_full_glass_doors",
        {
            "carcass_form": "cube_grid",
            "front_treatment": "full_glass_doors",
            "shelf_mechanism": "fixed_shelves",
            "base_style": "toe_kick",
            "back_panel": "beadboard_back",
            "shelf_count": 2,
            "width_m": 1.60,
            "depth_m": 0.26,
            "height_m": 1.20,
            "shelf_thickness_m": 0.018,
        },
        reason="widest single-cell aperture on the shallowest, shortest case",
    ),
    corner_case(
        "ladder_base_box_with_drawers_at_max_depth",
        {
            "carcass_form": "ladder",
            "front_treatment": "upper_glass_base_drawers",
            "shelf_mechanism": "adjustable_shelves",
            "base_style": "plinth",
            "back_panel": "solid_back",
            "shelf_count": 5,
            "width_m": 1.20,
            "depth_m": 0.58,
            "height_m": 2.10,
            "shelf_thickness_m": 0.030,
        },
        reason="raked form hosting the deepest drawer travel inside its vertical base box",
    ),
    corner_case(
        "highboy_two_tier_style_lift_with_panel_doors",
        {
            "carcass_form": "legged_highboy",
            "front_treatment": "glass_top_panel_base_doors",
            "shelf_mechanism": "fixed_shelves",
            "base_style": "legs",
            "back_panel": "solid_back",
            "shelf_count": 3,
            "width_m": 1.45,
            "depth_m": 0.55,
            "height_m": 2.28,
            "shelf_thickness_m": 0.028,
        },
        reason="tallest lifted case with four door leaves over both aperture bands",
    ),
    corner_case(
        "barrister_stack_with_open_shelving_drawer",
        {
            "carcass_form": "barrister",
            "front_treatment": "open_shelving",
            "shelf_mechanism": "adjustable_shelves",
            "base_style": "toe_kick",
            "back_panel": "open_back",
            "shelf_count": 8,
            "width_m": 0.90,
            "depth_m": 0.32,
            "height_m": 1.60,
            "shelf_thickness_m": 0.032,
        },
        reason="densest section stack with moving shelves and a single base drawer",
    ),
    corner_case(
        "grid_hutch_max_bays_with_base_cabinet_doors",
        {
            "carcass_form": "grid_hutch",
            "front_treatment": "base_cabinet_doors",
            "shelf_mechanism": "fixed_shelves",
            "base_style": "plinth",
            "back_panel": "beadboard_back",
            "shelf_count": 5,
            "width_m": 1.58,
            "depth_m": 0.50,
            "height_m": 2.00,
            "shelf_thickness_m": 0.024,
        },
        reason="maximum bay count with a full-width lower door pair",
    ),
)


__all__ = [
    "Config",
    "ResolvedConfig",
    "TEMPLATE_CORNERS",
    "TEMPLATE_DOMAIN",
    "build_pictureX_0611_bookcase",
    "config_from_seed",
    "resolve_config",
    "run_pictureX_0611_bookcase_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
]
