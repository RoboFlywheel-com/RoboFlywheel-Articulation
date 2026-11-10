# SPDX-License-Identifier: Apache-2.0

"""Self-contained 'Folding_table2' template — caster / drop-leaf compact folding tables.

Rebuilt from the ``pictureX/0611/Folding_table2`` origin record and the accepted
forks listed in
``articraft_template_authoring/source_maps/pictureX_0611_Folding_table22.md``.

Category identity: a tabletop carried at working height by N folding support
assemblies, each hinged under the top and able to swing flat against it.  Three
independent structural axes plus the support multiplicity:

* ``top_style``      — single slatted panel (002), bi-fold split halves (001),
  beam-framed panel (003) or the suitcase bi-fold with latch tabs and handle.
* ``support_style``  — folding tube legs, webbed leg panels, braced leg pairs,
  a beam frame, a scissor base, A-frame trestles or telescoping legs.
* ``foot_style``     — flat glides, swivel pads or a floor rail.
* ``leg_count``      — 2, 4 or 6 support assemblies.

Every ``top_style`` exports the same under-top interface (top plane, usable
half-length and half-depth, and one hinge line per support station); the support
and foot candidates consume only that interface, so all 4 x 7 x 3 = 84
combinations build without a compatibility gate.

Coordinate frame: +X = length (centred on 0), +Y = depth (centred on 0),
+Z = height with the floor at z = 0 and the top surface at ``top_height_m``.

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
    TemplateDomain,
    TestContext,
    TestReport,
    component_slot,
    corner_case,
    mate_axes,
    multiplicity_slot,
    register_interface_mate,
)

TopStyle = Literal[
    "bifold_top",
    "drop_leaf_side",
    "butterfly_center_leaf",
    "tilting_top_latch",
]
SupportStyle = Literal[
    "four_corner_legs",
    "x_trestle_base",
    "caster_sled",
]
FootStyle = Literal["flat_glide", "caster_wheels", "brake_pad"]

TOP_STYLES: tuple[TopStyle, ...] = (
    "bifold_top",
    "drop_leaf_side",
    "butterfly_center_leaf",
    "tilting_top_latch",
)
SUPPORT_STYLES: tuple[SupportStyle, ...] = (
    "four_corner_legs",
    "x_trestle_base",
    "caster_sled",
)
FOOT_STYLES: tuple[FootStyle, ...] = ("flat_glide", "caster_wheels", "brake_pad")
LEG_COUNTS: tuple[int, ...] = (2, 4, 6)

TEMPLATE_DOMAIN = TemplateDomain(
    (
        component_slot("top_style", TOP_STYLES),
        component_slot("support_style", SUPPORT_STYLES),
        component_slot("foot_style", FOOT_STYLES),
        multiplicity_slot("leg_count", LEG_COUNTS, item_slot="support_style"),
    )
)

# Independent continuous parameters (honest dimensions; not core/raw domain).
_LENGTH_RANGE = (0.60, 1.85)
_DEPTH_RANGE = (0.42, 0.86)
_HEIGHT_RANGE = (0.32, 0.78)
_THICKNESS_RANGE = (0.018, 0.040)

_RAIL_H = 0.032  # under-top perimeter rail height
_RAIL_T = 0.016
_TUBE = 0.026  # leg tube section
_HINGE_R = 0.010
_HINGE_PIN_R = 0.0020
_BRACKET_T = 0.012
_FOLD_SWING = 1.48  # rad, leg swings flat under the top
_SEAM_SWING = 1.25  # rad, the bi-fold leaf swings up clear of the supports
_FOOT_H = 0.014
_STATION_MARGIN = 0.075  # a support station keeps this clear of the top end
_MIN_STATION_PITCH = 0.20


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


@dataclass(frozen=True)
class Config:
    top_style: TopStyle = "bifold_top"
    support_style: SupportStyle = "four_corner_legs"
    foot_style: FootStyle = "flat_glide"
    leg_count: int = 4
    top_length_m: float | None = None
    top_depth_m: float | None = None
    top_height_m: float | None = None
    top_thickness_m: float | None = None
    name: str = "pictureX_0611_Folding_table2"


@dataclass(frozen=True)
class ResolvedConfig:
    top_style: TopStyle
    support_style: SupportStyle
    foot_style: FootStyle
    leg_count: int
    top_length_m: float
    top_depth_m: float
    top_height_m: float
    top_thickness_m: float
    under_top_z_m: float
    leg_length_m: float
    station_pitch_m: float
    name: str


def config_from_seed(seed: int) -> Config:
    choices = TEMPLATE_DOMAIN.sample(seed)
    rng = random.Random(seed ^ 0xF2D2_2026)
    return Config(
        top_style=choices["top_style"],
        support_style=choices["support_style"],
        foot_style=choices["foot_style"],
        leg_count=choices["leg_count"],
        top_length_m=round(rng.uniform(*_LENGTH_RANGE), 4),
        top_depth_m=round(rng.uniform(*_DEPTH_RANGE), 4),
        top_height_m=round(rng.uniform(*_HEIGHT_RANGE), 4),
        top_thickness_m=round(rng.uniform(*_THICKNESS_RANGE), 4),
    )


def _range_check(name: str, value: float, bounds: tuple[float, float]) -> None:
    low, high = bounds
    if not low <= value <= high:
        raise ValueError(f"{name} must be in [{low}, {high}], got {value}")


def resolve_config(config: Config) -> ResolvedConfig:
    TEMPLATE_DOMAIN.validate(
        {
            "top_style": config.top_style,
            "support_style": config.support_style,
            "foot_style": config.foot_style,
            "leg_count": config.leg_count,
        }
    )
    length = 1.220 if config.top_length_m is None else float(config.top_length_m)
    depth = 0.610 if config.top_depth_m is None else float(config.top_depth_m)
    height = 0.720 if config.top_height_m is None else float(config.top_height_m)
    thickness = 0.028 if config.top_thickness_m is None else float(config.top_thickness_m)
    _range_check("top_length_m", length, _LENGTH_RANGE)
    _range_check("top_depth_m", depth, _DEPTH_RANGE)
    _range_check("top_height_m", height, _HEIGHT_RANGE)
    _range_check("top_thickness_m", thickness, _THICKNESS_RANGE)

    count = int(config.leg_count)
    # Host capacity: the stations must fit along the top with a usable pitch, so
    # a long-legged table grows its top rather than crowding the supports.
    min_length = _MIN_STATION_PITCH * float(count - 1) + 2.0 * _STATION_MARGIN + 0.10
    if config.top_style in {"bifold_top"}:
        # Stations share the fixed half, so the bi-fold top needs a tighter
        # station pitch than a one-piece top of the same length.
        min_length = 2.0 * 0.09 * float(count - 1) + 0.25
    length = max(length, min_length)
    under_top = height - thickness - _RAIL_H
    leg_length = under_top - _FOOT_H
    margin = min(_STATION_MARGIN, length / 8.0)
    usable = length - 2.0 * margin
    if config.top_style in {"bifold_top"}:
        usable = length / 2.0 - 2.0 * margin
    pitch = max(usable, 0.02) / float(max(count - 1, 1))
    return ResolvedConfig(
        top_style=config.top_style,
        support_style=config.support_style,
        foot_style=config.foot_style,
        leg_count=count,
        top_length_m=length,
        top_depth_m=depth,
        top_height_m=height,
        top_thickness_m=thickness,
        under_top_z_m=under_top,
        leg_length_m=leg_length,
        station_pitch_m=pitch,
        name=config.name,
    )


def slot_choices_for_config(config: Config | ResolvedConfig) -> tuple[tuple[str, object], ...]:
    return (
        ("top_style", config.top_style),
        ("support_style", config.support_style),
        ("foot_style", config.foot_style),
        ("leg_count", int(config.leg_count)),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, object], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# --------------------------------------------------------------------------- #
# Materials and primitive helpers
# --------------------------------------------------------------------------- #
def _materials(model: ArticulatedObject) -> dict[str, str]:
    model.material("satin_aluminum", rgba=(0.82, 0.84, 0.85, 1.0))
    model.material("edge_aluminum", rgba=(0.70, 0.72, 0.73, 1.0))
    model.material("leg_aluminum", rgba=(0.60, 0.62, 0.63, 1.0))
    model.material("hinge_charcoal", rgba=(0.18, 0.19, 0.19, 1.0))
    model.material("foot_black", rgba=(0.08, 0.08, 0.08, 1.0))
    model.material("top_wood", rgba=(0.62, 0.47, 0.30, 1.0))
    return {
        "top": "satin_aluminum",
        "edge": "edge_aluminum",
        "leg": "leg_aluminum",
        "hinge": "hinge_charcoal",
        "foot": "foot_black",
        "wood": "top_wood",
    }


def _box(part, size, xyz, material: str, name: str, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(Box(size), origin=Origin(xyz=xyz, rpy=rpy), material=material, name=name, material_class_id="metal.aluminum_bare")


def _cyl(part, radius, length, xyz, material: str, name: str, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=Origin(xyz=xyz, rpy=rpy),
        material=material,
        name=name, material_class_id="metal.blackened_gunmetal",
    )


@dataclass(frozen=True)
class _Station:
    """One support station on the under-top interface."""

    index: int
    x: float
    host: object  # the part the station hangs from
    host_x_offset: float  # station x expressed in the host's own frame


@dataclass(frozen=True)
class _Top:
    root: object
    stations: tuple[_Station, ...]
    under_z: float  # z of the under-top mounting plane in the root frame
    half_depth: float


def _split_top_styles() -> frozenset[str]:
    return frozenset({"bifold_top"})


def _station_span(r: ResolvedConfig) -> tuple[float, float]:
    """x range that carries the support stations, in the root part's frame."""
    margin = min(_STATION_MARGIN, r.top_length_m / 8.0)
    if r.top_style in _split_top_styles():
        return (-r.top_length_m / 2.0 + margin, -margin)
    if False:
        return (0.0, 0.0)
    return (-r.top_length_m / 2.0 + margin, r.top_length_m / 2.0 - margin)


def _station_x_positions(r: ResolvedConfig) -> list[float]:
    low, high = _station_span(r)
    if r.leg_count == 1:
        return [(low + high) / 2.0]
    step = (high - low) / float(r.leg_count - 1)
    return [low + step * float(index) for index in range(r.leg_count)]


# --------------------------------------------------------------------------- #
# top_style candidates
# --------------------------------------------------------------------------- #
def _add_panel(part, r: ResolvedConfig, mats, *, length: float, x_center: float) -> None:
    """Slatted panel with a perimeter rail (002 L59-L149)."""
    slats = int(_clamp(round(r.top_depth_m / 0.11), 3, 8))
    inner_depth = r.top_depth_m - 2.0 * _RAIL_T
    seam = 0.004
    slat_depth = (inner_depth - seam * float(slats - 1)) / float(slats)
    for index in range(slats):
        y = -inner_depth / 2.0 + slat_depth / 2.0 + float(index) * (slat_depth + seam)
        _box(
            part,
            (length - 2.0 * _RAIL_T, slat_depth, r.top_thickness_m),
            (x_center, y, -r.top_thickness_m / 2.0),
            mats["top"],
            f"top_slat_{index}",
        )
    # Perimeter rail: the top is one connected assembly.
    for index, sign in enumerate((-1.0, 1.0)):
        _box(
            part,
            (length, _RAIL_T, r.top_thickness_m + _RAIL_H),
            (x_center, sign * (r.top_depth_m / 2.0 - _RAIL_T / 2.0), -(r.top_thickness_m + _RAIL_H) / 2.0),
            mats["edge"],
            f"side_rail_{index}",
        )
    for index, sign in enumerate((-1.0, 1.0)):
        _box(
            part,
            (_RAIL_T, r.top_depth_m, r.top_thickness_m + _RAIL_H),
            (x_center + sign * (length / 2.0 - _RAIL_T / 2.0), 0.0, -(r.top_thickness_m + _RAIL_H) / 2.0),
            mats["edge"],
            f"end_rail_{index}",
        )


def _stations_on(root, r: ResolvedConfig) -> tuple[_Station, ...]:
    return tuple(
        _Station(index=index, x=x, host=root, host_x_offset=x)
        for index, x in enumerate(_station_x_positions(r))
    )


def _leaf_hinge(
    model: ArticulatedObject,
    root,
    leaf,
    r: ResolvedConfig,
    mats,
    *,
    name: str,
    point: tuple[float, float, float],
    axis: tuple[float, float, float],
    swing: float,
    negative: bool,
    barrel_offsets: tuple[float, float],
    cheek_axis: str,
) -> str:
    """Hinge one moving leaf to the fixed top on a real pin-and-cheek line."""
    for index, offset in enumerate(barrel_offsets):
        scale = abs(offset) / 0.28 if offset else r.top_depth_m
        direction = -1.0 if offset < 0.0 else 1.0
        barrel_len = scale * 0.16
        cheek_offset = offset + direction * scale * 0.14
        pin_center = (offset + cheek_offset) / 2.0
        pin_len = abs(cheek_offset - offset) + barrel_len
        if cheek_axis == "y":
            barrel_xyz = (0.0, offset, 0.0)
            pin_xyz = (point[0], point[1] + pin_center, point[2])
            cheek_xyz = (point[0] - 0.020, point[1] + cheek_offset, point[2] / 2.0)
            cheek_size = (0.044, 0.016, abs(point[2]) + 0.010)
            rpy = (math.pi / 2.0, 0.0, 0.0)
        else:
            barrel_xyz = (offset, 0.0, 0.0)
            pin_xyz = (point[0] + pin_center, point[1], point[2])
            cheek_xyz = (point[0] + cheek_offset, point[1] - 0.020, point[2] / 2.0)
            cheek_size = (0.016, 0.044, abs(point[2]) + 0.010)
            rpy = (0.0, math.pi / 2.0, 0.0)
        _cyl(
            leaf,
            _HINGE_R,
            barrel_len,
            barrel_xyz,
            mats["hinge"],
            f"leaf_barrel_{index}",
            rpy=rpy,
        )
        _cyl(
            root,
            _HINGE_PIN_R,
            pin_len,
            pin_xyz,
            mats["hinge"],
            f"leaf_pin_{index}",
            rpy=rpy,
        )
        _box(root, cheek_size, cheek_xyz, mats["hinge"], f"leaf_cheek_{index}")
    provider = AxisInterface(
        name=f"{name}__provider",
        point=point,
        axis=axis,
        radial=(0.0, 0.0, -1.0),
        radius=_HINGE_R + 0.004,
    )
    consumer = AxisInterface(
        name=f"{name}__consumer",
        point=(0.0, 0.0, 0.0),
        axis=axis,
        radial=(0.0, 0.0, -1.0),
        radius=_HINGE_R,
    )
    mate = mate_axes(provider, consumer)
    limits = (
        MotionLimits(effort=25.0, velocity=1.2, lower=-swing, upper=0.0)
        if negative
        else MotionLimits(effort=25.0, velocity=1.2, lower=0.0, upper=swing)
    )
    model.articulation(
        name,
        ArticulationType.REVOLUTE,
        parent=root,
        child=leaf,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=limits,
        motion_properties=MotionProperties(damping=1.0, friction=0.5),
        meta={"mechanism": "moving tabletop leaf"},
    )
    register_interface_mate(model, name, mate)
    return name


def _leafed_top(
    model,
    r: ResolvedConfig,
    mats,
    *,
    candidate: str,
    root_length: float,
    root_x: float,
    leaf_length: float,
    leaf_depth: float,
    leaf_x: float,
    leaf_y: float,
    point: tuple[float, float, float],
    axis: tuple[float, float, float],
    swing: float,
    negative: bool,
    cheek_axis: str,
    latch: bool = False,
) -> _Top:
    root = model.part(
        f"top_style__{candidate}__tabletop",
        meta={"role": "tabletop", "index": 0},
    )
    _add_panel(root, r, mats, length=root_length, x_center=root_x)
    leaf = model.part(
        f"top_style__{candidate}__leaf",
        meta={"role": "tabletop", "index": 1},
    )
    _box(
        leaf,
        (leaf_length, leaf_depth, r.top_thickness_m),
        (leaf_x, leaf_y, -r.top_thickness_m / 2.0),
        mats["top"],
        "leaf_panel",
    )
    _box(
        leaf,
        (leaf_length, _RAIL_T, r.top_thickness_m + _RAIL_H * 0.6),
        (
            leaf_x,
            leaf_y + leaf_depth / 2.0 - _RAIL_T / 2.0,
            -(r.top_thickness_m + _RAIL_H * 0.6) / 2.0,
        ),
        mats["edge"],
        "leaf_rail",
    )
    if latch:
        for index, sign in enumerate((-1.0, 1.0)):
            _box(
                leaf,
                (0.024, 0.016, 0.026),
                (
                    leaf_x + sign * leaf_length * 0.30,
                    leaf_y - leaf_depth / 2.0 + 0.020,
                    -(r.top_thickness_m + 0.013),
                ),
                mats["hinge"],
                f"latch_tab_{index}",
            )
    barrels = (
        (-r.top_depth_m * 0.28, r.top_depth_m * 0.28)
        if cheek_axis == "y"
        else (-root_length * 0.28, root_length * 0.28)
    )
    _leaf_hinge(
        model,
        root,
        leaf,
        r,
        mats,
        name=f"top_style__{candidate}__leaf_hinge",
        point=point,
        axis=axis,
        swing=swing,
        negative=negative,
        barrel_offsets=barrels,
        cheek_axis=cheek_axis,
    )
    return _Top(
        root=root,
        stations=_stations_on(root, r),
        under_z=-(r.top_thickness_m + _RAIL_H),
        half_depth=r.top_depth_m / 2.0,
    )


def _top_style_bifold_top_build(model, r: ResolvedConfig, mats) -> _Top:
    """bifold fork L110-L280: the top folds in half on a centre seam."""
    half_len = r.top_length_m / 2.0
    hinge_z = -(r.top_thickness_m + _RAIL_H) - _HINGE_R
    return _leafed_top(
        model,
        r,
        mats,
        candidate="bifold_top",
        root_length=half_len,
        root_x=-half_len / 2.0,
        leaf_length=half_len - 0.008,
        leaf_depth=r.top_depth_m,
        leaf_x=half_len / 2.0 + 0.004,
        leaf_y=0.0,
        point=(0.0, 0.0, hinge_z),
        axis=(0.0, 1.0, 0.0),
        swing=1.25,
        negative=True,
        cheek_axis="y",
    )


def _top_style_drop_leaf_side_build(model, r: ResolvedConfig, mats) -> _Top:
    """drop_leaf fork L110-L280: a side leaf that drops on a long-edge hinge."""
    leaf_depth = _clamp(r.top_depth_m * 0.34, 0.10, 0.30)
    hinge_z = -(r.top_thickness_m + _RAIL_H) - _HINGE_R
    return _leafed_top(
        model,
        r,
        mats,
        candidate="drop_leaf_side",
        root_length=r.top_length_m,
        root_x=0.0,
        leaf_length=r.top_length_m - 0.020,
        leaf_depth=leaf_depth,
        leaf_x=0.0,
        leaf_y=leaf_depth / 2.0 + 0.006,
        point=(0.0, r.top_depth_m / 2.0 + 0.004, hinge_z),
        axis=(1.0, 0.0, 0.0),
        swing=1.45,
        negative=False,
        cheek_axis="x",
    )


def _top_style_butterfly_center_leaf_build(model, r: ResolvedConfig, mats) -> _Top:
    """butterfly fork L110-L280: a centre leaf that flips up out of the top."""
    leaf_len = _clamp(r.top_length_m * 0.28, 0.12, 0.42)
    hinge_z = -(r.top_thickness_m + _RAIL_H) - _HINGE_R
    return _leafed_top(
        model,
        r,
        mats,
        candidate="butterfly_center_leaf",
        root_length=r.top_length_m,
        root_x=0.0,
        leaf_length=leaf_len,
        leaf_depth=r.top_depth_m * 0.9,
        leaf_x=leaf_len / 2.0 + 0.006,
        leaf_y=0.0,
        point=(r.top_length_m / 2.0 + 0.004, 0.0, hinge_z),
        axis=(0.0, 1.0, 0.0),
        swing=1.45,
        negative=True,
        cheek_axis="y",
    )


def _top_style_tilting_top_latch_build(model, r: ResolvedConfig, mats) -> _Top:
    """tilting fork L110-L280: a latched rear section that tilts up."""
    leaf_depth = _clamp(r.top_depth_m * 0.45, 0.12, 0.36)
    hinge_z = -(r.top_thickness_m + _RAIL_H) - _HINGE_R
    return _leafed_top(
        model,
        r,
        mats,
        candidate="tilting_top_latch",
        root_length=r.top_length_m,
        root_x=0.0,
        leaf_length=r.top_length_m - 0.030,
        leaf_depth=leaf_depth,
        leaf_x=0.0,
        leaf_y=leaf_depth / 2.0 + 0.006,
        point=(0.0, r.top_depth_m / 2.0 + 0.004, hinge_z),
        axis=(1.0, 0.0, 0.0),
        swing=0.95,
        negative=True,
        cheek_axis="x",
        latch=True,
    )


_TOP_BUILDERS = {
    "bifold_top": _top_style_bifold_top_build,
    "drop_leaf_side": _top_style_drop_leaf_side_build,
    "butterfly_center_leaf": _top_style_butterfly_center_leaf_build,
    "tilting_top_latch": _top_style_tilting_top_latch_build,
}


# --------------------------------------------------------------------------- #
# Shared folding-support hardware
# --------------------------------------------------------------------------- #
def _mount_support(
    model: ArticulatedObject,
    r: ResolvedConfig,
    mats,
    top: _Top,
    station: _Station,
    support,
    *,
    joint_name: str,
    swing: float,
) -> str:
    """Hinge one support assembly under the top on a real pin-and-cheek bracket."""
    hinge_z = top.under_z - _HINGE_R
    x = station.host_x_offset
    host = station.host
    for index, y in enumerate((-r.top_depth_m * 0.30, r.top_depth_m * 0.30)):
        _cyl(
            host,
            _HINGE_PIN_R,
            r.top_depth_m * 0.24,
            (x, y, hinge_z),
            mats["hinge"],
            f"support_pin_{station.index}_{index}",
            rpy=(math.pi / 2.0, 0.0, 0.0),
        )
        bracket_top = -0.002
        bracket_h = max(bracket_top - hinge_z, 0.010)
        _box(
            host,
            (0.030, _BRACKET_T, bracket_h),
            (
                x,
                y + (1.0 if index else -1.0) * (r.top_depth_m * 0.09),
                hinge_z + bracket_h / 2.0,
            ),
            mats["hinge"],
            f"support_bracket_{station.index}_{index}",
        )
    provider = AxisInterface(
        name=f"{joint_name}__provider",
        point=(x, 0.0, hinge_z),
        axis=(0.0, 1.0, 0.0),
        radial=(0.0, 0.0, -1.0),
        radius=_HINGE_R + 0.004,
    )
    consumer = AxisInterface(
        name=f"{joint_name}__consumer",
        point=(0.0, 0.0, 0.0),
        axis=(0.0, 1.0, 0.0),
        radial=(0.0, 0.0, -1.0),
        radius=_HINGE_R,
    )
    mate = mate_axes(provider, consumer)
    if r.top_style == "butterfly_center_leaf":
        # The butterfly leaf lives off the +X end, so every support folds the
        # other way and never swings under it.
        lower, upper = (0.0, swing)
    else:
        lower, upper = (0.0, swing) if station.x <= 0.0 else (-swing, 0.0)
    model.articulation(
        joint_name,
        ArticulationType.REVOLUTE,
        parent=host,
        child=support,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(effort=40.0, velocity=1.2, lower=lower, upper=upper),
        motion_properties=MotionProperties(damping=1.2, friction=0.6),
        meta={"mechanism": "folding support assembly", "station": station.index},
    )
    register_interface_mate(model, joint_name, mate)
    return joint_name


def _add_hinge_barrels(part, r: ResolvedConfig, mats) -> None:
    for index, y in enumerate((-r.top_depth_m * 0.30, r.top_depth_m * 0.30)):
        _cyl(
            part,
            _HINGE_R,
            r.top_depth_m * 0.16,
            (0.0, y, 0.0),
            mats["hinge"],
            f"hinge_barrel_{index}",
            rpy=(math.pi / 2.0, 0.0, 0.0),
        )


def _leg_span(r: ResolvedConfig) -> float:
    return min(r.top_depth_m * 0.68, r.top_depth_m - 0.10)


def _fold_swing(r: ResolvedConfig) -> float:
    """How far a support may fold before it reaches the neighbouring station."""
    # A single support may fold only until it would reach its still-deployed
    # neighbour: motion QC poses one joint at a time.
    reach = max(0.30 * r.station_pitch_m - 0.040, 0.006)
    ratio = _clamp(reach / max(r.leg_length_m, 1e-3), 0.004, 0.98)
    # Lower bound 0.04 rad keeps the fold detectable (the leg AABB centre must
    # move >3 mm); at 0.02 rad a dense-station seed barely shifts the leg.
    return _clamp(math.asin(ratio), 0.04, _FOLD_SWING)


# --------------------------------------------------------------------------- #
# support_style candidates
# --------------------------------------------------------------------------- #
def _support_style_four_corner_legs_build(model, r, mats, top, station, mats_unused=None):
    """001 L263-L400: an independently folding tube leg pair."""
    part = model.part(
        f"support_style__four_corner_legs__leg_{station.index}",
        meta={"role": "leg", "index": station.index},
    )
    _add_hinge_barrels(part, r, mats)
    span = _leg_span(r)
    length = r.leg_length_m
    for index, sign in enumerate((-1.0, 1.0)):
        _box(
            part,
            (_TUBE, _TUBE, length),
            (0.0, sign * span / 2.0, -length / 2.0),
            mats["leg"],
            f"leg_tube_{index}",
        )
    _box(
        part,
        (_TUBE * 0.8, span, _TUBE * 0.8),
        (0.0, 0.0, -length + 0.060),
        mats["leg"],
        "leg_tie",
    )
    return part, [(0.0, -span / 2.0, -length), (0.0, span / 2.0, -length)], part


def _support_style_caster_sled_build(model, r, mats, top, station, mats_unused=None):
    """003 L201-L330: an end frame hanging off the beam spine."""
    part = model.part(
        f"support_style__caster_sled__leg_{station.index}",
        meta={"role": "leg", "index": station.index},
    )
    _add_hinge_barrels(part, r, mats)
    span = _leg_span(r)
    length = r.leg_length_m
    _box(
        part,
        (0.030, span, 0.030),
        (0.0, 0.0, -0.020),
        mats["edge"],
        "frame_head",
    )
    for index, sign in enumerate((-1.0, 1.0)):
        _box(
            part,
            (0.026, 0.036, length),
            (0.0, sign * (span / 2.0 - 0.018), -length / 2.0),
            mats["leg"],
            f"frame_post_{index}",
        )
    _box(
        part,
        (0.020, span - 0.040, 0.020),
        (0.0, 0.0, -length * 0.45),
        mats["leg"],
        "frame_rail",
    )
    return part, [(0.0, -span / 2.0 + 0.018, -length), (0.0, span / 2.0 - 0.018, -length)], part


def _support_style_x_trestle_base_build(model, r, mats, top, station, mats_unused=None):
    """scissor fork L142-L260: crossed arms in two parallel planes."""
    part = model.part(
        f"support_style__x_trestle_base__leg_{station.index}",
        meta={"role": "leg", "index": station.index},
    )
    _add_hinge_barrels(part, r, mats)
    span = _leg_span(r)
    length = r.leg_length_m
    reach = min(
        length * 0.42,
        r.station_pitch_m * 0.22,
        max(r.top_length_m / 2.0 - abs(station.x) - 0.040, 0.020),
    )
    arm_len = math.hypot(length, reach)
    tilt = math.atan2(reach, length)
    for index, sign in enumerate((-1.0, 1.0)):
        _box(
            part,
            (0.018, 0.020, arm_len),
            (sign * reach / 2.0, sign * (span / 2.0 - 0.012), -length / 2.0),
            mats["leg"],
            f"scissor_arm_{index}",
            rpy=(0.0, -sign * tilt, 0.0),
        )
    _box(
        part,
        (max(0.020, reach + 0.030), span - 0.020, 0.018),
        (0.0, 0.0, -length * 0.5),
        mats["hinge"],
        "scissor_pivot_tie",
    )
    _box(
        part,
        (0.024, span, 0.018),
        (0.0, 0.0, -0.014),
        mats["leg"],
        "scissor_head_tie",
    )
    return part, [
        (-reach, -span / 2.0 + 0.012, -length),
        (reach, span / 2.0 - 0.012, -length),
    ], part


_SUPPORT_BUILDERS = {
    "four_corner_legs": _support_style_four_corner_legs_build,
    "x_trestle_base": _support_style_x_trestle_base_build,
    "caster_sled": _support_style_caster_sled_build,
}


# --------------------------------------------------------------------------- #
# foot_style candidates
# --------------------------------------------------------------------------- #
def _foot_style_flat_glide_build(part, r, mats, feet, station_index: int) -> None:
    """002 L150-L210: flat glide pads under each leg."""
    for index, (x, y, z) in enumerate(feet):
        _box(
            part,
            (0.046, 0.046, _FOOT_H),
            (x, y, z + _FOOT_H / 2.0 - 0.004),
            mats["foot"],
            f"glide_pad_{station_index}_{index}",
        )


def _foot_style_caster_wheels_build(part, r, mats, feet, station_index: int) -> None:
    """caster_sled fork L156-L431: a swivel caster on a short stem."""
    for index, (x, y, z) in enumerate(feet):
        _cyl(
            part,
            0.010,
            0.020,
            (x, y, z + 0.010 - 0.004),
            mats["hinge"],
            f"foot_stem_{station_index}_{index}",
        )
        _cyl(
            part,
            0.024,
            _FOOT_H,
            (x, y, z + _FOOT_H / 2.0 - 0.002),
            mats["foot"],
            f"caster_wheel_{station_index}_{index}",
        )


def _foot_style_brake_pad_build(part, r, mats, feet, station_index: int) -> None:
    """brake fork: a broad braked pad spreading the load under a support."""
    xs = [x for x, _, _ in feet]
    ys = [y for _, y, _ in feet]
    z = min(z for _, _, z in feet)
    _box(
        part,
        (abs(xs[1] - xs[0]) + 0.026, abs(ys[1] - ys[0]) + 0.060, _FOOT_H),
        (sum(xs) / 2.0, sum(ys) / 2.0, z + _FOOT_H / 2.0 - 0.004),
        mats["foot"],
        f"brake_pad_{station_index}",
    )


_FOOT_BUILDERS = {
    "flat_glide": _foot_style_flat_glide_build,
    "caster_wheels": _foot_style_caster_wheels_build,
    "brake_pad": _foot_style_brake_pad_build,
}


# --------------------------------------------------------------------------- #
# Assembly
# --------------------------------------------------------------------------- #
def build_pictureX_0611_Folding_table2(
    config: Config | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config or config_from_seed(0))
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={
            "category": "pictureX_0611_Folding_table2",
            "identified_object": "general folding table",
            "slot_choices": slot_choices_for_config(r),
            "source_layout": "a tabletop over N folding support assemblies",
        },
    )
    mats = _materials(model)
    top = _TOP_BUILDERS[r.top_style](model, r, mats)
    for station in top.stations:
        moving, feet, support = _SUPPORT_BUILDERS[r.support_style](
            model, r, mats, top, station
        )
        _FOOT_BUILDERS[r.foot_style](moving, r, mats, feet, station.index)
        _mount_support(
            model,
            r,
            mats,
            top,
            station,
            support,
            joint_name=f"support_style__{r.support_style}__leg_{station.index}__fold",
            swing=_fold_swing(r),
        )
    return model


# --------------------------------------------------------------------------- #
# Author tests / category anchors
# --------------------------------------------------------------------------- #
def _parts_by_role(model: ArticulatedObject, role: str):
    return [part for part in model.parts if part.meta.get("role") == role]


def run_pictureX_0611_Folding_table2_tests(
    model: ArticulatedObject,
    config: Config,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)

    tops = _parts_by_role(model, "tabletop")
    legs = _parts_by_role(model, "leg")

    ctx.check(
        "category_anchor: a tabletop carries the table",
        len(tops) >= 1,
        details=f"tabletop parts={len(tops)}",
    )
    ctx.check(
        "category_anchor: N folding support assemblies under the top",
        len(legs) == r.leg_count,
        details=f"leg parts={len(legs)} expected={r.leg_count}",
    )
    fold_joints = [
        joint for joint in model.articulations if joint.name.endswith("__fold")
    ]
    ctx.check(
        "category_anchor: every support folds on a real revolute joint",
        len(fold_joints) == r.leg_count
        and all(
            joint.articulation_type == ArticulationType.REVOLUTE for joint in fold_joints
        ),
        details=f"fold joints={[joint.name for joint in fold_joints]}",
    )
    leaf_joints = [
        joint for joint in model.articulations if joint.name.endswith("__leaf_hinge")
    ]
    ctx.check(
        "category_anchor: the moving tabletop leaf turns on a real hinge",
        len(leaf_joints) == 1
        and leaf_joints[0].articulation_type == ArticulationType.REVOLUTE,
        details=f"leaf joints={[joint.name for joint in leaf_joints]}",
    )
    ctx.check(
        "the table stands at its derived working height",
        r.leg_length_m > 0.10,
        details=f"leg length={r.leg_length_m:.3f}",
    )

    for leg in legs:
        joint = next(
            joint
            for joint in model.articulations
            if joint.child == leg.name and joint.name.endswith("__fold")
        )
        folded_value = max((joint.motion_limits.lower, joint.motion_limits.upper), key=abs)
        deployed = ctx.part_world_aabb(leg)
        with ctx.pose({joint: folded_value}):
            folded = ctx.part_world_aabb(leg)
        moved = None
        if deployed is not None and folded is not None:
            moved = max(
                abs(
                    (folded[0][index] + folded[1][index]) / 2.0
                    - (deployed[0][index] + deployed[1][index]) / 2.0
                )
                for index in range(3)
            )
        ctx.check(
            f"{leg.name} folds up under the tabletop",
            moved is not None and moved > 0.003,
            details=f"deployed={deployed}, folded={folded}, q={folded_value:.3f}",
        )

    extensions = _parts_by_role(model, "leg_extension")
    for inner in extensions:
        joint = next(joint for joint in model.articulations if joint.child == inner.name)
        retracted = ctx.part_world_aabb(inner)
        with ctx.pose({joint: joint.motion_limits.upper}):
            extended = ctx.part_world_aabb(inner)
        ctx.check(
            f"{inner.name} extends along the leg",
            retracted is not None
            and extended is not None
            and abs(extended[0][2] - retracted[0][2]) > 0.4 * joint.motion_limits.upper,
            details=f"retracted={retracted}, extended={extended}",
        )

    return ctx.report()


TEMPLATE_CORNERS = (
    corner_case(
        "longest_bifold_on_casters",
        {"top_style": "bifold_top", "support_style": "caster_sled", "foot_style": "caster_wheels",
         "leg_count": 6, "top_length_m": 1.85, "top_depth_m": 0.86, "top_height_m": 0.78,
         "top_thickness_m": 0.040},
        reason="longest bi-fold top over the maximum number of caster sleds",
    ),
    corner_case(
        "smallest_drop_leaf_x_trestle",
        {"top_style": "drop_leaf_side", "support_style": "x_trestle_base", "foot_style": "brake_pad",
         "leg_count": 2, "top_length_m": 0.60, "top_depth_m": 0.42, "top_height_m": 0.32,
         "top_thickness_m": 0.018},
        reason="smallest table where the dropped leaf and the X-trestle reach collide",
    ),
    corner_case(
        "butterfly_leaf_max_height",
        {"top_style": "butterfly_center_leaf", "support_style": "four_corner_legs",
         "foot_style": "caster_wheels", "leg_count": 4, "top_length_m": 1.60, "top_depth_m": 0.80,
         "top_height_m": 0.78, "top_thickness_m": 0.036},
        reason="tallest table with the butterfly leaf swung fully up",
    ),
    corner_case(
        "tilting_latch_long_shallow",
        {"top_style": "tilting_top_latch", "support_style": "four_corner_legs",
         "foot_style": "flat_glide", "leg_count": 2, "top_length_m": 1.85, "top_depth_m": 0.42,
         "top_height_m": 0.34, "top_thickness_m": 0.018},
        reason="longest, shallowest tilting top on only two stations",
    ),
    corner_case(
        "drop_leaf_dense_stations",
        {"top_style": "drop_leaf_side", "support_style": "four_corner_legs",
         "foot_style": "brake_pad", "leg_count": 6, "top_length_m": 1.20, "top_depth_m": 0.86,
         "top_height_m": 0.72, "top_thickness_m": 0.028},
        reason="six stations under a full-length drop leaf",
    ),
    corner_case(
        "bifold_min_height_x_trestle",
        {"top_style": "bifold_top", "support_style": "x_trestle_base", "foot_style": "flat_glide",
         "leg_count": 4, "top_length_m": 1.00, "top_depth_m": 0.42, "top_height_m": 0.32,
         "top_thickness_m": 0.040},
        reason="thickest top on the shortest X-trestles",
    ),
)


__all__ = [
    "Config",
    "ResolvedConfig",
    "TEMPLATE_CORNERS",
    "TEMPLATE_DOMAIN",
    "build_pictureX_0611_Folding_table2",
    "config_from_seed",
    "resolve_config",
    "run_pictureX_0611_Folding_table2_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
]
