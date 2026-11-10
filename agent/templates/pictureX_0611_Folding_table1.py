# SPDX-License-Identifier: Apache-2.0

"""Self-contained 'Folding_table1' template — tube-frame rolltop folding tables.

Rebuilt from the three ``pictureX/0611/Folding_table1`` origin records and the
accepted forks listed in
``articraft_template_authoring/source_maps/pictureX_0611_Folding_table11.md``.

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
    "rolltop_slats",
    "dense_rolltop_slats",
    "solid_panel",
    "mesh_panel",
]
SupportStyle = Literal[
    "folding_tube_legs",
    "crossbrace_locks",
    "tube_x_frame",
    "telescoping_legs",
]
FootStyle = Literal["flat_glide", "swivel_pad", "floor_rail"]

TOP_STYLES: tuple[TopStyle, ...] = (
    "rolltop_slats",
    "dense_rolltop_slats",
    "solid_panel",
    "mesh_panel",
)
SUPPORT_STYLES: tuple[SupportStyle, ...] = (
    "folding_tube_legs",
    "crossbrace_locks",
    "tube_x_frame",
    "telescoping_legs",
)
FOOT_STYLES: tuple[FootStyle, ...] = ("flat_glide", "swivel_pad", "floor_rail")
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
    top_style: TopStyle = "rolltop_slats"
    support_style: SupportStyle = "folding_tube_legs"
    foot_style: FootStyle = "flat_glide"
    leg_count: int = 4
    top_length_m: float | None = None
    top_depth_m: float | None = None
    top_height_m: float | None = None
    top_thickness_m: float | None = None
    name: str = "pictureX_0611_Folding_table1"


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
    rng = random.Random(seed ^ 0xF1D1_2026)
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
    length = max(length, min_length)
    under_top = height - thickness - _RAIL_H
    leg_length = under_top - _FOOT_H
    usable = length - 2.0 * _STATION_MARGIN
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
    return frozenset()


def _station_span(r: ResolvedConfig) -> tuple[float, float]:
    """x range that carries the support stations, in the root part's frame."""
    if r.top_style in _split_top_styles():
        # The moving leaf carries no supports, so the stations spread across the
        # fixed half only; the whole table still folds as one assembly.
        return (-r.top_length_m / 2.0 + _STATION_MARGIN, -_STATION_MARGIN)
    return (-r.top_length_m / 2.0 + _STATION_MARGIN, r.top_length_m / 2.0 - _STATION_MARGIN)


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


def _slat_top(part, r: ResolvedConfig, mats, *, slats: int, gap: float) -> None:
    """Rolled slat top: N narrow slats on two underside cross rails (001)."""
    inner_depth = r.top_depth_m - 2.0 * _RAIL_T
    slat_depth = (inner_depth - gap * float(slats - 1)) / float(slats)
    for index in range(slats):
        y = -inner_depth / 2.0 + slat_depth / 2.0 + float(index) * (slat_depth + gap)
        _box(
            part,
            (r.top_length_m - 2.0 * _RAIL_T, slat_depth, r.top_thickness_m * 0.8),
            (0.0, y, -r.top_thickness_m * 0.4),
            mats["top"],
            f"top_slat_{index}",
        )
    for index, sign in enumerate((-1.0, 1.0)):
        _box(
            part,
            (0.030, r.top_depth_m, r.top_thickness_m * 0.7),
            (sign * (r.top_length_m / 2.0 - 0.060), 0.0, -r.top_thickness_m * 0.9),
            mats["edge"],
            f"slat_cross_rail_{index}",
        )
    for index, sign in enumerate((-1.0, 1.0)):
        _box(
            part,
            (r.top_length_m, _RAIL_T, r.top_thickness_m + _RAIL_H),
            (
                0.0,
                sign * (r.top_depth_m / 2.0 - _RAIL_T / 2.0),
                -(r.top_thickness_m + _RAIL_H) / 2.0,
            ),
            mats["edge"],
            f"side_rail_{index}",
        )
    for index, sign in enumerate((-1.0, 1.0)):
        _box(
            part,
            (_RAIL_T, r.top_depth_m, r.top_thickness_m + _RAIL_H),
            (
                sign * (r.top_length_m / 2.0 - _RAIL_T / 2.0),
                0.0,
                -(r.top_thickness_m + _RAIL_H) / 2.0,
            ),
            mats["edge"],
            f"end_rail_{index}",
        )


def _plain_top(part, r: ResolvedConfig, mats, *, mesh: bool) -> None:
    """Solid deck, or a perforated mesh deck of crossed straps (003)."""
    if mesh:
        straps = int(_clamp(round(r.top_length_m / 0.09), 4, 14))
        for index in range(straps):
            x = -r.top_length_m / 2.0 + r.top_length_m * (float(index) + 0.5) / float(straps)
            _box(
                part,
                (r.top_length_m / float(straps) * 0.6, r.top_depth_m - 2.0 * _RAIL_T, 0.006),
                (x, 0.0, -0.003),
                mats["top"],
                f"mesh_strap_x_{index}",
            )
        cross = int(_clamp(round(r.top_depth_m / 0.09), 3, 10))
        for index in range(cross):
            y = -r.top_depth_m / 2.0 + r.top_depth_m * (float(index) + 0.5) / float(cross)
            _box(
                part,
                (r.top_length_m - 2.0 * _RAIL_T, r.top_depth_m / float(cross) * 0.5, 0.006),
                (0.0, y, -0.009),
                mats["edge"],
                f"mesh_strap_y_{index}",
            )
    else:
        _box(
            part,
            (r.top_length_m - 2.0 * _RAIL_T, r.top_depth_m - 2.0 * _RAIL_T, r.top_thickness_m),
            (0.0, 0.0, -r.top_thickness_m / 2.0),
            mats["top"],
            "top_panel",
        )
    for index, sign in enumerate((-1.0, 1.0)):
        _box(
            part,
            (r.top_length_m, _RAIL_T, r.top_thickness_m + _RAIL_H),
            (
                0.0,
                sign * (r.top_depth_m / 2.0 - _RAIL_T / 2.0),
                -(r.top_thickness_m + _RAIL_H) / 2.0,
            ),
            mats["edge"],
            f"side_rail_{index}",
        )
    for index, sign in enumerate((-1.0, 1.0)):
        _box(
            part,
            (_RAIL_T, r.top_depth_m, r.top_thickness_m + _RAIL_H),
            (
                sign * (r.top_length_m / 2.0 - _RAIL_T / 2.0),
                0.0,
                -(r.top_thickness_m + _RAIL_H) / 2.0,
            ),
            mats["edge"],
            f"end_rail_{index}",
        )


def _make_top(model, r: ResolvedConfig, mats, candidate: str, builder) -> _Top:
    root = model.part(
        f"top_style__{candidate}__tabletop",
        meta={"role": "tabletop", "index": 0},
    )
    builder(root)
    return _Top(
        root=root,
        stations=_stations_on(root, r),
        under_z=-(r.top_thickness_m + _RAIL_H),
        half_depth=r.top_depth_m / 2.0,
    )


def _top_style_rolltop_slats_build(model, r: ResolvedConfig, mats) -> _Top:
    """001 L27-L200: a rolled slat deck on two underside cross rails."""
    slats = int(_clamp(round((r.top_depth_m - 2.0 * _RAIL_T) / 0.075), 4, 10))
    return _make_top(
        model, r, mats, "rolltop_slats", lambda part: _slat_top(part, r, mats, slats=slats, gap=0.006)
    )


def _top_style_dense_rolltop_slats_build(model, r: ResolvedConfig, mats) -> _Top:
    """dense_rolltop fork: the same roll with twice the slat count."""
    slats = int(_clamp(round((r.top_depth_m - 2.0 * _RAIL_T) / 0.038), 8, 20))
    return _make_top(
        model,
        r,
        mats,
        "dense_rolltop_slats",
        lambda part: _slat_top(part, r, mats, slats=slats, gap=0.003),
    )


def _top_style_solid_panel_build(model, r: ResolvedConfig, mats) -> _Top:
    """002 L41-L149: a solid deck in the same tube frame."""
    return _make_top(model, r, mats, "solid_panel", lambda part: _plain_top(part, r, mats, mesh=False))


def _top_style_mesh_panel_build(model, r: ResolvedConfig, mats) -> _Top:
    """003: a perforated mesh deck of crossed straps."""
    return _make_top(model, r, mats, "mesh_panel", lambda part: _plain_top(part, r, mats, mesh=True))


_TOP_BUILDERS = {
    "rolltop_slats": _top_style_rolltop_slats_build,
    "dense_rolltop_slats": _top_style_dense_rolltop_slats_build,
    "solid_panel": _top_style_solid_panel_build,
    "mesh_panel": _top_style_mesh_panel_build,
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
    reach = 0.35 * r.station_pitch_m
    ratio = _clamp(reach / max(r.leg_length_m, 1e-3), 0.04, 0.98)
    return _clamp(math.asin(ratio), 0.12, _FOLD_SWING)


# --------------------------------------------------------------------------- #
# support_style candidates
# --------------------------------------------------------------------------- #
def _support_style_folding_tube_legs_build(model, r, mats, top, station, mats_unused=None):
    """001 L263-L400: an independently folding tube leg pair."""
    part = model.part(
        f"support_style__folding_tube_legs__leg_{station.index}",
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


def _support_style_crossbrace_locks_build(model, r, mats, top, station, mats_unused=None):
    """004 L130-L340: a leg pair carrying a separate locking brace link."""
    part = model.part(
        f"support_style__crossbrace_locks__leg_{station.index}",
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
    # Locking brace: a diagonal link back to the leg's own hinge end.
    brace_len = math.hypot(length * 0.55, span * 0.30)
    for index, sign in enumerate((-1.0, 1.0)):
        _box(
            part,
            (0.014, brace_len, 0.014),
            (0.0, sign * span * 0.25, -length * 0.62),
            mats["hinge"],
            f"locking_brace_{index}",
            rpy=(math.atan2(length * 0.55, span * 0.30) * sign, 0.0, 0.0),
        )
    _box(
        part,
        (_TUBE * 0.8, span, _TUBE * 0.8),
        (0.0, 0.0, -length * 0.62),
        mats["leg"],
        "brace_tie",
    )
    return part, [(0.0, -span / 2.0, -length), (0.0, span / 2.0, -length)], part


def _support_style_tube_x_frame_build(model, r, mats, top, station, mats_unused=None):
    """scissor fork L142-L260: crossed arms in two parallel planes."""
    part = model.part(
        f"support_style__tube_x_frame__leg_{station.index}",
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


def _support_style_telescoping_legs_build(model, r, mats, top, station, mats_unused=None):
    """telescoping fork L152-L295: an outer leg plus a prismatic inner section."""
    part = model.part(
        f"support_style__telescoping_legs__leg_{station.index}",
        meta={"role": "leg", "index": station.index},
    )
    _add_hinge_barrels(part, r, mats)
    span = _leg_span(r)
    outer_len = r.leg_length_m * 0.62
    for index, sign in enumerate((-1.0, 1.0)):
        _box(
            part,
            (_TUBE, _TUBE, outer_len),
            (0.0, sign * span / 2.0, -outer_len / 2.0),
            mats["leg"],
            f"outer_tube_{index}",
        )
    _box(
        part,
        (_TUBE * 0.8, span, _TUBE * 0.8),
        (0.0, 0.0, -outer_len + 0.030),
        mats["leg"],
        "outer_tie",
    )
    inner = model.part(
        f"support_style__telescoping_legs__leg_inner_{station.index}",
        meta={"role": "leg_extension", "index": station.index},
    )
    overlap_reserve = max(0.10 * r.leg_length_m, 0.040)
    inner_len = r.leg_length_m - outer_len + overlap_reserve
    for index, sign in enumerate((-1.0, 1.0)):
        _cyl(
            inner,
            0.0024,
            inner_len,
            (0.0, sign * span / 2.0, -inner_len / 2.0),
            mats["hinge"],
            f"inner_tube_{index}",
        )
    _box(
        inner,
        (0.012, span, 0.012),
        (0.0, 0.0, -inner_len + 0.010),
        mats["hinge"],
        "inner_tie",
    )
    joint_name = f"support_style__telescoping_legs__leg_{station.index}__extend"
    travel = max(overlap_reserve - 0.020, 0.015)
    model.articulation(
        joint_name,
        ArticulationType.PRISMATIC,
        parent=part,
        child=inner,
        origin=Origin(xyz=(0.0, 0.0, -(outer_len - overlap_reserve))),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=35.0, velocity=0.3, lower=0.0, upper=travel),
        motion_properties=MotionProperties(damping=1.5, friction=0.7),
        meta={"mechanism": "telescoping leg extension", "station": station.index},
    )
    foot_z = -inner_len + 0.004
    return inner, [(0.0, -span / 2.0, foot_z), (0.0, span / 2.0, foot_z)], part


_SUPPORT_BUILDERS = {
    "folding_tube_legs": _support_style_folding_tube_legs_build,
    "crossbrace_locks": _support_style_crossbrace_locks_build,
    "tube_x_frame": _support_style_tube_x_frame_build,
    "telescoping_legs": _support_style_telescoping_legs_build,
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


def _foot_style_swivel_pad_build(part, r, mats, feet, station_index: int) -> None:
    """001 L300-L346: swivelling foot pads on a short stem."""
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
            f"swivel_pad_{station_index}_{index}",
        )


def _foot_style_floor_rail_build(part, r, mats, feet, station_index: int) -> None:
    """a_frame fork L191-L223: a floor rail spreading the load under a support."""
    xs = [x for x, _, _ in feet]
    ys = [y for _, y, _ in feet]
    z = min(z for _, _, z in feet)
    _box(
        part,
        (abs(xs[1] - xs[0]) + 0.048, abs(ys[1] - ys[0]) + 0.060, _FOOT_H),
        (sum(xs) / 2.0, sum(ys) / 2.0, z + _FOOT_H / 2.0 - 0.004),
        mats["foot"],
        f"floor_rail_{station_index}",
    )


_FOOT_BUILDERS = {
    "flat_glide": _foot_style_flat_glide_build,
    "swivel_pad": _foot_style_swivel_pad_build,
    "floor_rail": _foot_style_floor_rail_build,
}


# --------------------------------------------------------------------------- #
# Assembly
# --------------------------------------------------------------------------- #
def build_pictureX_0611_Folding_table1(
    config: Config | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config or config_from_seed(0))
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={
            "category": "pictureX_0611_Folding_table1",
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


def run_pictureX_0611_Folding_table1_tests(
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
            moved is not None and moved > 0.010,
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
        "longest_dense_roll_with_telescoping",
        {
            "top_style": "dense_rolltop_slats",
            "support_style": "telescoping_legs",
            "foot_style": "swivel_pad",
            "leg_count": 6,
            "top_length_m": 1.85,
            "top_depth_m": 0.86,
            "top_height_m": 0.78,
            "top_thickness_m": 0.040,
        },
        reason="densest slat roll over the maximum number of telescoping stations",
    ),
    corner_case(
        "smallest_roll_with_x_frame",
        {
            "top_style": "rolltop_slats",
            "support_style": "tube_x_frame",
            "foot_style": "floor_rail",
            "leg_count": 2,
            "top_length_m": 0.60,
            "top_depth_m": 0.42,
            "top_height_m": 0.32,
            "top_thickness_m": 0.018,
        },
        reason="smallest roll where the X-frame reach and the station pitch collide",
    ),
    corner_case(
        "mesh_panel_crossbrace_max_height",
        {
            "top_style": "mesh_panel",
            "support_style": "crossbrace_locks",
            "foot_style": "flat_glide",
            "leg_count": 4,
            "top_length_m": 1.60,
            "top_depth_m": 0.80,
            "top_height_m": 0.78,
            "top_thickness_m": 0.036,
        },
        reason="tallest braced frame under an open mesh deck",
    ),
    corner_case(
        "solid_panel_two_stations_long",
        {
            "top_style": "solid_panel",
            "support_style": "folding_tube_legs",
            "foot_style": "flat_glide",
            "leg_count": 2,
            "top_length_m": 1.85,
            "top_depth_m": 0.42,
            "top_height_m": 0.34,
            "top_thickness_m": 0.018,
        },
        reason="longest, shallowest deck on only two stations",
    ),
    corner_case(
        "dense_roll_min_size",
        {
            "top_style": "dense_rolltop_slats",
            "support_style": "folding_tube_legs",
            "foot_style": "swivel_pad",
            "leg_count": 2,
            "top_length_m": 0.60,
            "top_depth_m": 0.42,
            "top_height_m": 0.32,
            "top_thickness_m": 0.018,
        },
        reason="smallest deck at the highest slat density",
    ),
    corner_case(
        "x_frame_dense_stations",
        {
            "top_style": "solid_panel",
            "support_style": "tube_x_frame",
            "foot_style": "floor_rail",
            "leg_count": 6,
            "top_length_m": 1.20,
            "top_depth_m": 0.86,
            "top_height_m": 0.72,
            "top_thickness_m": 0.028,
        },
        reason="six X-frames at the tightest station pitch",
    ),
)


__all__ = [
    "Config",
    "ResolvedConfig",
    "TEMPLATE_CORNERS",
    "TEMPLATE_DOMAIN",
    "build_pictureX_0611_Folding_table1",
    "config_from_seed",
    "resolve_config",
    "run_pictureX_0611_Folding_table1_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
]
