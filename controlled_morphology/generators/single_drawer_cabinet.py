# SPDX-License-Identifier: Apache-2.0

"""pictureX/0611 kitchen_cabinet — Design-backed single-file template.

A compact kitchen base cabinet assembled from reviewed source components: a real panel
carcass, thin laminate worktop, four adjustable legs on an open or toe-board-closed bay, and
either hinged leaves, a stack of hollow drawer trays, or top-hinged lift flaps on stay arms.

Unit width, height, hinge line and travel all derive from the real front opening and from N,
so every declared slot combination builds and no overlap allowance is emitted.

Coordinate convention: X = width, Y = depth with the FRONT at -Y, Z = height.
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

# The access face is the -Y side, matching the source cabinet images and the
# semantic preview camera.
__preview_front_axis__ = "-y"

CabinetBody = Literal["base_cabinet", "plinth_deck_cabinet"]
AccessModule = Literal["hinged_doors", "drawer_stack", "lift_up_flap"]
DoorFace = Literal["shaker_panel", "flat_panel", "seamed_slab", "reeded_slab"]
TopTreatment = Literal["laminate_worktop", "stone_slab_worktop", "worktop_with_upstand"]
SupportBase = Literal["adjustable_legs", "legs_with_toe_board", "solid_plinth", "block_feet"]
HandleType = Literal["bar", "knob"]

_DOOR_FACES: tuple[DoorFace, ...] = ("shaker_panel", "flat_panel", "seamed_slab", "reeded_slab")
_TOP_TREATMENTS: tuple[TopTreatment, ...] = (
    "laminate_worktop",
    "stone_slab_worktop",
    "worktop_with_upstand",
)
_SUPPORT_BASES: tuple[SupportBase, ...] = (
    "adjustable_legs",
    "legs_with_toe_board",
    "solid_plinth",
    "block_feet",
)

TEMPLATE_DOMAIN = TemplateDomain(
    (
        component_slot("cabinet_body", ("base_cabinet", "plinth_deck_cabinet")),
        component_slot("access_module", ("hinged_doors", "drawer_stack", "lift_up_flap")),
        component_slot("door_face", _DOOR_FACES),
        component_slot("top_treatment", _TOP_TREATMENTS),
        component_slot("support_base", _SUPPORT_BASES),
        multiplicity_slot("access_count", (1, 2, 3), item_slot="access_module"),
        multiplicity_slot("shelf_count", (1, 2), item_slot="cabinet_body"),
    )
)

_WALL_T = 0.018
_BACK_T = 0.012
_CAP_T = 0.018
_FRONT_T = 0.019
_FRONT_GAP = 0.002
_BARREL_R = 0.008
_SETBACK = 0.012
_REVEAL = 0.004
_OUTER_REVEAL = 0.022
_LEVEL_REVEAL = 0.006
_RAIL_W = 0.014
_RAIL_EMBED = 0.010
_RAIL_H = 0.012
_RUNNER_W = 0.009
_RUNNER_ENGAGE = 0.003
_TRAY_WALL_T = 0.010
_TRAY_FLOOR_T = 0.010
_TRAY_FRONT_REACH = 0.016
_SIDE_CLEAR = 0.003
_SHELF_T = 0.016
_MIN_LEAF_W = 0.055
_MIN_FRONT_H = 0.050
_HANDLE_EDGE_MARGIN = 0.012
_HANDLE_LENGTH_BOUNDS = (0.040, 0.320)
_HANDLE_THICKNESS_BOUNDS = (0.008, 0.032)
_HANDLE_CLEARANCE_BOUNDS = (0.008, 0.080)

RGBA = tuple[float, float, float, float]
_PALETTES: tuple[dict[str, RGBA], ...] = (
    {
        "carcass": (0.88, 0.88, 0.86, 1.0),
        "front": (0.94, 0.94, 0.92, 1.0),
        "dark": (0.28, 0.29, 0.30, 1.0),
        "metal": (0.74, 0.75, 0.76, 1.0),
        "worktop": (0.97, 0.97, 0.95, 1.0),
    },
    {
        "carcass": (0.84, 0.85, 0.83, 1.0),
        "front": (0.20, 0.34, 0.30, 1.0),
        "dark": (0.10, 0.18, 0.16, 1.0),
        "metal": (0.78, 0.68, 0.36, 1.0),
        "worktop": (0.96, 0.95, 0.92, 1.0),
    },
    {
        "carcass": (0.80, 0.80, 0.80, 1.0),
        "front": (0.62, 0.16, 0.14, 1.0),
        "dark": (0.14, 0.14, 0.15, 1.0),
        "metal": (0.80, 0.82, 0.84, 1.0),
        "worktop": (0.98, 0.98, 0.96, 1.0),
    },
    {
        "carcass": (0.86, 0.84, 0.80, 1.0),
        "front": (0.42, 0.46, 0.52, 1.0),
        "dark": (0.18, 0.20, 0.23, 1.0),
        "metal": (0.70, 0.72, 0.74, 1.0),
        "worktop": (0.95, 0.94, 0.91, 1.0),
    },
)

_BODY_BOUNDS = {
    # The source family is a compact floor-standing kitchen base cabinet.  Keep
    # the host in that proportion family; front mechanisms provide the variation.
    "base_cabinet": {"w": (0.48, 0.78), "d": (0.50, 0.62), "h": (0.62, 0.82)},
    "plinth_deck_cabinet": {"w": (0.48, 0.86), "d": (0.50, 0.62), "h": (0.62, 0.82)},
}
# 002/004/005 raise the bottom deck and set a dark toe board back from the front.
_PLINTH_RISE = 0.052
_TOE_SETBACK = 0.030
_LEG_H_BOUNDS = (0.080, 0.180)
# 004 closes the leg bay with a black rail 0.024 deep, held 0.015 inside the leg
# line in x, overlapping the leg shafts and running up into the raised deck.
_TOE_BOARD_T = 0.024
_TOE_BOARD_OVERBITE = 0.004
_TOE_BOARD_SIDE_REACH = 0.016
_TOE_BOARD_FLOOR_RATIO = 0.62
_TOE_BOARD_EMBED = 0.008
# Authored base and top extensions.  Every support member ends 0.008 inside the
# carcass floor panel so the base stays one connected solid, and no top member
# ever reaches below the worktop underside, which is the only free plane the
# lift flap sweeps through at full travel.
_PLINTH_T = 0.020
_PLINTH_REVEAL_H = 0.008
_PLINTH_SETBACK_BOUNDS = (0.030, 0.070)
_BLOCK_FOOT_W = 0.062
_BLOCK_GLIDE_H = 0.012
_UPSTAND_T = 0.020
_UPSTAND_RETURN_D = 0.070
_UPSTAND_H_BOUNDS = (0.040, 0.120)
_SCOTIA_R = 0.010


@dataclass(frozen=True)
class Config:
    cabinet_body: CabinetBody = "base_cabinet"
    access_module: AccessModule = "drawer_stack"
    door_face: DoorFace = "flat_panel"
    top_treatment: TopTreatment = "laminate_worktop"
    support_base: SupportBase = "adjustable_legs"
    access_count: int = 1
    shelf_count: int = 1
    carcass_width_m: float | None = None
    carcass_depth_m: float | None = None
    carcass_height_m: float | None = None
    door_swing_rad: float | None = None
    drawer_travel_ratio: float | None = None
    lift_flap_rad: float | None = None
    shaker_frame_w_m: float | None = None
    panel_t_m: float | None = None
    worktop_t_m: float | None = None
    plinth_leg_h_m: float | None = None
    upstand_h_m: float | None = None
    plinth_setback_m: float | None = None
    handle_type: HandleType = "bar"
    handle_orientation_rad: float = 0.0
    handle_length_m: float | None = None
    handle_thickness_m: float | None = None
    handle_clearance_m: float | None = None
    handle_horizontal_position_ratio: float = 0.5
    handle_vertical_position_ratio: float = 0.72
    palette: int = 0
    name: str = "controlled_single_drawer_cabinet"


@dataclass(frozen=True)
class ResolvedConfig:
    cabinet_body: CabinetBody
    access_module: AccessModule
    door_face: DoorFace
    top_treatment: TopTreatment
    support_base: SupportBase
    access_count: int
    shelf_count: int
    palette: int
    name: str
    carcass_width_m: float
    carcass_depth_m: float
    carcass_height_m: float
    door_swing_rad: float
    drawer_travel_ratio: float
    lift_flap_rad: float
    shaker_frame_w_m: float
    panel_t_m: float
    worktop_t_m: float
    plinth_leg_h_m: float
    upstand_h_m: float
    plinth_setback_m: float
    handle_type: HandleType
    handle_orientation_rad: float
    handle_length_m: float
    handle_thickness_m: float
    handle_clearance_m: float
    handle_horizontal_position_ratio: float
    handle_vertical_position_ratio: float
    floor_z_m: float
    carcass_top_z_m: float
    cavity_lo_z_m: float
    cavity_hi_z_m: float
    front_y_m: float
    back_y_m: float
    half_w_m: float
    front_t_m: float


def variable_space() -> dict[str, object]:
    """Describe task-facing interventions and their deterministic descendants."""

    return {
        "schema_version": 1,
        "generator": "single_drawer_cabinet",
        "intervention_semantics": (
            "One explicit Config field changes per OAT cell. Geometry and kinematics derived "
            "deterministically from that field are expected to change and are recorded."
        ),
        "task_contract": {
            "movable_part_count": 1,
            "joint_type": "prismatic",
            "joint_axis": "-Y",
            "accepted_topology": {
                "access_module": "drawer_stack",
                "access_count": 1,
            },
        },
        "variables": {
            "handle_type": {
                "priority": "P0",
                "kind": "categorical",
                "values": ["bar", "knob"],
                "control": "direct",
                "derived_effects": ["handle topology", "active handle parameters"],
            },
            "handle_orientation_rad": {
                "priority": "P0",
                "kind": "continuous",
                "unit": "rad",
                "range": [0.0, math.pi],
                "endpoint": "upper_exclusive",
                "control": "direct",
                "active_when": {"handle_type": "bar"},
                "derived_effects": ["grip axis", "geometry-dependent fit bounds"],
            },
            "handle_length_m": {
                "priority": "P0",
                "kind": "continuous",
                "unit": "m",
                "nominal_range": [0.040, 0.320],
                "control": "direct_with_fit_constraint",
                "active_when": {"handle_type": "bar"},
                "derived_effects": ["valid handle position interval"],
            },
            "handle_thickness_m": {
                "priority": "P0",
                "kind": "continuous",
                "unit": "m",
                "nominal_range": [0.008, 0.032],
                "control": "direct_with_fit_constraint",
                "derived_effects": ["grip radius", "valid handle position interval"],
            },
            "handle_clearance_m": {
                "priority": "P0",
                "kind": "continuous",
                "unit": "m",
                "range": [0.008, 0.080],
                "control": "direct",
                "derived_effects": ["handle depth", "grasp frame"],
            },
            "handle_horizontal_position_ratio": {
                "priority": "P0",
                "kind": "continuous",
                "unit": "ratio",
                "nominal_range": [0.0, 1.0],
                "control": "direct_with_fit_constraint",
                "derived_effects": ["handle center"],
            },
            "handle_vertical_position_ratio": {
                "priority": "P0",
                "kind": "continuous",
                "unit": "ratio",
                "nominal_range": [0.0, 1.0],
                "control": "direct_with_fit_constraint",
                "derived_effects": ["handle center"],
            },
            "carcass_width_m": {
                "priority": "P0",
                "kind": "continuous",
                "unit": "m",
                "range_for_canonical_body": [0.48, 0.78],
                "control": "direct_upstream",
                "derived_effects": [
                    "front width",
                    "drawer tray width",
                    "handle fit bounds",
                ],
            },
            "carcass_depth_m": {
                "priority": "P0",
                "kind": "continuous",
                "unit": "m",
                "range": [0.50, 0.62],
                "control": "direct_upstream",
                "derived_effects": ["drawer box depth", "absolute joint travel"],
            },
            "carcass_height_m": {
                "priority": "P0",
                "kind": "continuous",
                "unit": "m",
                "range": [0.62, 0.82],
                "control": "direct_upstream",
                "derived_effects": ["front height", "drawer tray height", "handle fit bounds"],
            },
            "panel_t_m": {
                "priority": "P0",
                "kind": "continuous",
                "unit": "m",
                "range": [0.016, 0.026],
                "control": "direct",
                "active_when": {"door_face": "flat_panel"},
                "derived_effects": ["front thickness", "handle depth"],
            },
            "drawer_travel_ratio": {
                "priority": "P1",
                "kind": "continuous",
                "unit": "ratio",
                "range": [0.34, 0.60],
                "control": "direct",
                "derived_effects": ["absolute joint travel", "opening endpoint"],
            },
        },
        "derived_measurements": [
            "morphology.carcass",
            "morphology.front_opening",
            "morphology.target_panel",
            "morphology.drawer_tray",
            "morphology.motion",
        ],
        "replaceable_components": {
            "cabinet_body": ["base_cabinet", "plinth_deck_cabinet"],
            "door_face": list(_DOOR_FACES),
            "top_treatment": list(_TOP_TREATMENTS),
            "support_base": list(_SUPPORT_BASES),
        },
        "deferred_structural_slices": {
            "access_count": "family builder supports 1-3; task-facing entry is fixed to 1",
            "access_module": (
                "family builder also has hinged_doors and lift_up_flap; register separately"
            ),
            "layout": "family builder uses equal-height full-width vertical stacks",
            "appearance_and_dynamics": "deferred materialization stage",
        },
    }


def _clamp(v, lo, hi):
    return max(lo, min(hi, v))


def _pick(v, d):
    return d if v is None else float(v)


def _finite_float(value: float, field_name: str) -> float:
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{field_name} must be finite, got {value!r}")
    return result


def _handle_radius(handle_type: HandleType, thickness: float) -> float:
    return thickness * 1.15 if handle_type == "knob" else thickness / 2.0


def _reference_front_size(
    *,
    access_module: AccessModule,
    access_count: int,
    width: float,
    cavity_lo: float,
    cavity_hi: float,
) -> tuple[float, float]:
    """Return the first access unit's face size used to resolve handle fit."""

    opening_w = width - 2 * _WALL_T
    opening_h = cavity_hi - cavity_lo - 0.008
    if access_module == "drawer_stack":
        gap = _LEVEL_REVEAL
        band = (opening_h - (access_count - 1) * gap) / access_count
        if band < _MIN_FRONT_H:
            gap = 0.002
            band = max((opening_h - (access_count - 1) * gap) / access_count, 0.024)
        return opening_w - 0.004, band - 0.004
    cell_w = opening_w / access_count
    if access_module == "hinged_doors":
        return (
            max(cell_w - _OUTER_REVEAL - _SETBACK - _REVEAL, _MIN_LEAF_W),
            max(opening_h - 0.006, 0.080),
        )
    return max(cell_w - 0.008, _MIN_LEAF_W), max(opening_h - 0.010, 0.070)


def _resolve_handle_parameters(
    config: Config,
    *,
    face_width: float,
    face_height: float,
) -> tuple[HandleType, float, float, float, float, float, float]:
    """Resolve a handle into the face rectangle without changing its requested direction.

    Position ratios are measured left-to-right and bottom-to-top in the panel's
    local X/Z plane.  The returned ratios describe the actual, fit-safe centre.
    """

    if config.handle_type not in ("bar", "knob"):
        raise ValueError(f"handle_type must be 'bar' or 'knob', got {config.handle_type!r}")
    handle_type: HandleType = config.handle_type
    angle = _finite_float(config.handle_orientation_rad, "handle_orientation_rad") % math.pi
    requested_thickness = _pick(config.handle_thickness_m, 0.014)
    radial_scale = 1.0 / 1.15 if handle_type == "knob" else 2.0
    max_thickness = min(
        _HANDLE_THICKNESS_BOUNDS[1],
        max(
            0.002,
            radial_scale * (min(face_width, face_height) / 2.0 - _HANDLE_EDGE_MARGIN),
        ),
    )
    thickness = _clamp(
        _finite_float(requested_thickness, "handle_thickness_m"),
        min(_HANDLE_THICKNESS_BOUNDS[0], max_thickness),
        max_thickness,
    )
    radius = _handle_radius(handle_type, thickness)
    clearance = _clamp(
        _finite_float(_pick(config.handle_clearance_m, 0.020), "handle_clearance_m"),
        *_HANDLE_CLEARANCE_BOUNDS,
    )

    requested_length = _finite_float(_pick(config.handle_length_m, 0.180), "handle_length_m")
    if handle_type == "bar":
        available_x = max(face_width / 2.0 - _HANDLE_EDGE_MARGIN - radius, 0.0)
        available_z = max(face_height / 2.0 - _HANDLE_EDGE_MARGIN - radius, 0.0)
        cos_a, sin_a = abs(math.cos(angle)), abs(math.sin(angle))
        max_x = math.inf if cos_a < 1e-9 else 2.0 * available_x / cos_a
        max_z = math.inf if sin_a < 1e-9 else 2.0 * available_z / sin_a
        max_length = min(_HANDLE_LENGTH_BOUNDS[1], max_x, max_z)
        if max_length <= 0.0:
            raise ValueError(
                f"front {face_width:.4f} x {face_height:.4f} m is too small for a handle"
            )
        length = _clamp(
            requested_length,
            min(_HANDLE_LENGTH_BOUNDS[0], max_length),
            max_length,
        )
        extent_x = cos_a * length / 2.0 + radius
        extent_z = sin_a * length / 2.0 + radius
    else:
        length = _clamp(requested_length, *_HANDLE_LENGTH_BOUNDS)
        extent_x = radius
        extent_z = radius

    horizontal = _clamp(
        _finite_float(config.handle_horizontal_position_ratio, "handle_horizontal_position_ratio"),
        0.0,
        1.0,
    )
    vertical = _clamp(
        _finite_float(config.handle_vertical_position_ratio, "handle_vertical_position_ratio"),
        0.0,
        1.0,
    )
    requested_x = (horizontal - 0.5) * face_width
    requested_z = (vertical - 0.5) * face_height
    x_limit = max(face_width / 2.0 - _HANDLE_EDGE_MARGIN - extent_x, 0.0)
    z_limit = max(face_height / 2.0 - _HANDLE_EDGE_MARGIN - extent_z, 0.0)
    actual_x = _clamp(requested_x, -x_limit, x_limit)
    actual_z = _clamp(requested_z, -z_limit, z_limit)
    return (
        handle_type,
        angle,
        length,
        thickness,
        clearance,
        actual_x / face_width + 0.5,
        actual_z / face_height + 0.5,
    )


def config_from_seed(seed: int) -> Config:
    rng = random.Random(seed)
    body: CabinetBody = rng.choice(("base_cabinet", "plinth_deck_cabinet"))
    b = _BODY_BOUNDS[body]
    return Config(
        cabinet_body=body,
        access_module=rng.choice(("hinged_doors", "drawer_stack", "lift_up_flap")),
        door_face=rng.choice(_DOOR_FACES),
        top_treatment=rng.choice(_TOP_TREATMENTS),
        support_base=rng.choice(_SUPPORT_BASES),
        access_count=rng.choice((1, 2, 3)),
        shelf_count=rng.choice((1, 2)),
        carcass_width_m=round(rng.uniform(*b["w"]), 3),
        carcass_depth_m=round(rng.uniform(*b["d"]), 3),
        carcass_height_m=round(rng.uniform(*b["h"]), 3),
        door_swing_rad=round(rng.uniform(1.30, 1.90), 3),
        drawer_travel_ratio=round(rng.uniform(0.34, 0.62), 3),
        lift_flap_rad=round(rng.uniform(1.00, 1.55), 3),
        shaker_frame_w_m=round(rng.uniform(0.045, 0.075), 4),
        panel_t_m=round(rng.uniform(0.016, 0.026), 4),
        worktop_t_m=round(rng.uniform(0.020, 0.050), 4),
        plinth_leg_h_m=round(rng.uniform(0.080, 0.180), 3),
        upstand_h_m=round(rng.uniform(*_UPSTAND_H_BOUNDS), 4),
        plinth_setback_m=round(rng.uniform(*_PLINTH_SETBACK_BOUNDS), 4),
        handle_type=rng.choice(("bar", "knob")),
        handle_orientation_rad=round(rng.uniform(0.0, math.pi), 4),
        handle_length_m=round(rng.uniform(*_HANDLE_LENGTH_BOUNDS), 4),
        handle_thickness_m=round(rng.uniform(*_HANDLE_THICKNESS_BOUNDS), 4),
        handle_clearance_m=round(rng.uniform(*_HANDLE_CLEARANCE_BOUNDS), 4),
        handle_horizontal_position_ratio=round(rng.uniform(0.2, 0.8), 4),
        handle_vertical_position_ratio=round(rng.uniform(0.2, 0.8), 4),
        palette=rng.randrange(len(_PALETTES)),
        name=f"controlled_single_drawer_cabinet_seed_{seed}",
    )


def resolve_config(config: Config) -> ResolvedConfig:
    body = config.cabinet_body
    b = _BODY_BOUNDS[body]
    width = _clamp(_pick(config.carcass_width_m, sum(b["w"]) / 2), *b["w"])
    depth = _clamp(_pick(config.carcass_depth_m, sum(b["d"]) / 2), *b["d"])
    height = _clamp(_pick(config.carcass_height_m, sum(b["h"]) / 2), *b["h"])
    support = config.support_base
    floor_z = _clamp(
        _pick(config.plinth_leg_h_m, sum(_LEG_H_BOUNDS) / 2),
        *_LEG_H_BOUNDS,
    )
    top_z = floor_z + height
    cavity_lo = floor_z + _WALL_T + (_PLINTH_RISE if body == "plinth_deck_cabinet" else 0.0)
    cavity_hi = top_z - _CAP_T
    access_count = int(_clamp(int(config.access_count), 1, 3))
    front_t = (
        _clamp(_pick(config.panel_t_m, 0.019), 0.016, 0.026)
        if config.door_face == "flat_panel"
        else _FRONT_T
    )
    face_width, face_height = _reference_front_size(
        access_module=config.access_module,
        access_count=access_count,
        width=width,
        cavity_lo=cavity_lo,
        cavity_hi=cavity_hi,
    )
    (
        handle_type,
        handle_orientation,
        handle_length,
        handle_thickness,
        handle_clearance,
        handle_horizontal,
        handle_vertical,
    ) = _resolve_handle_parameters(config, face_width=face_width, face_height=face_height)
    return ResolvedConfig(
        cabinet_body=body,
        access_module=config.access_module,
        door_face=config.door_face,
        top_treatment=config.top_treatment,
        support_base=support,
        access_count=access_count,
        shelf_count=int(_clamp(int(config.shelf_count), 1, 2)),
        palette=int(config.palette) % len(_PALETTES),
        name=config.name,
        carcass_width_m=width,
        carcass_depth_m=depth,
        carcass_height_m=height,
        door_swing_rad=_clamp(_pick(config.door_swing_rad, 1.60), 1.30, 1.90),
        drawer_travel_ratio=_clamp(_pick(config.drawer_travel_ratio, 0.48), 0.34, 0.60),
        lift_flap_rad=_clamp(_pick(config.lift_flap_rad, 1.28), 1.00, 1.55),
        shaker_frame_w_m=_clamp(_pick(config.shaker_frame_w_m, 0.062), 0.045, 0.075),
        panel_t_m=_clamp(_pick(config.panel_t_m, 0.019), 0.016, 0.026),
        worktop_t_m=_clamp(_pick(config.worktop_t_m, 0.025), 0.020, 0.050),
        plinth_leg_h_m=floor_z,
        upstand_h_m=_clamp(_pick(config.upstand_h_m, 0.070), *_UPSTAND_H_BOUNDS),
        # The plinth cannot be set back past the leg line, or the front board
        # would leave the carcass footprint on the shallowest host depth.
        plinth_setback_m=min(
            _clamp(_pick(config.plinth_setback_m, 0.045), *_PLINTH_SETBACK_BOUNDS),
            max(depth / 2 - 0.090, _PLINTH_SETBACK_BOUNDS[0]),
        ),
        handle_type=handle_type,
        handle_orientation_rad=handle_orientation,
        handle_length_m=handle_length,
        handle_thickness_m=handle_thickness,
        handle_clearance_m=handle_clearance,
        handle_horizontal_position_ratio=handle_horizontal,
        handle_vertical_position_ratio=handle_vertical,
        floor_z_m=floor_z,
        carcass_top_z_m=top_z,
        cavity_lo_z_m=cavity_lo,
        cavity_hi_z_m=cavity_hi,
        front_y_m=-depth / 2.0,
        back_y_m=depth / 2.0 - _BACK_T,
        half_w_m=width / 2.0 - _WALL_T,
        front_t_m=front_t,
    )


def _wood_bx(part, size, xyz, material, name, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(
        Box(size=(float(size[0]), float(size[1]), float(size[2]))),
        origin=Origin(xyz=(float(xyz[0]), float(xyz[1]), float(xyz[2])), rpy=rpy),
        material=material,
        name=name,
        material_class_id="wood.engineered_board",
    )


def _wood_cy(part, radius, length, xyz, material, name, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(
        Cylinder(radius=float(radius), length=float(length)),
        origin=Origin(xyz=(float(xyz[0]), float(xyz[1]), float(xyz[2])), rpy=rpy),
        material=material,
        name=name,
        material_class_id="wood.engineered_board",
    )


def _metal_bx(part, size, xyz, material, name, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(
        Box(size=(float(size[0]), float(size[1]), float(size[2]))),
        origin=Origin(xyz=(float(xyz[0]), float(xyz[1]), float(xyz[2])), rpy=rpy),
        material=material,
        name=name,
        material_class_id="metal.stainless_matte",
    )


def _metal_cy(part, radius, length, xyz, material, name, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(
        Cylinder(radius=float(radius), length=float(length)),
        origin=Origin(xyz=(float(xyz[0]), float(xyz[1]), float(xyz[2])), rpy=rpy),
        material=material,
        name=name,
        material_class_id="metal.stainless_matte",
    )


def _stone_bx(part, size, xyz, material, name, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(
        Box(size=(float(size[0]), float(size[1]), float(size[2]))),
        origin=Origin(xyz=(float(xyz[0]), float(xyz[1]), float(xyz[2])), rpy=rpy),
        material=material,
        name=name,
        material_class_id="stone.polished_granite",
    )


def _stone_cy(part, radius, length, xyz, material, name, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(
        Cylinder(radius=float(radius), length=float(length)),
        origin=Origin(xyz=(float(xyz[0]), float(xyz[1]), float(xyz[2])), rpy=rpy),
        material=material,
        name=name,
        material_class_id="stone.polished_granite",
    )


def _rubber_cy(part, radius, length, xyz, material, name, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(
        Cylinder(radius=float(radius), length=float(length)),
        origin=Origin(xyz=(float(xyz[0]), float(xyz[1]), float(xyz[2])), rpy=rpy),
        material=material,
        name=name,
        material_class_id="rubber.smooth_plain",
    )


def _materials(model, palette):
    table = _PALETTES[palette % len(_PALETTES)]
    return {k: model.material(f"kitchen_{palette}_{k}", rgba=v) for k, v in table.items()}


def _axis_mate(*, provider_name, point, axis, radial, consumer_name, consumer_radius):
    provider = AxisInterface(
        name=provider_name,
        point=tuple(float(v) for v in point),
        axis=axis,
        radial=radial,
        radius=_BARREL_R,
    )
    consumer = AxisInterface(
        name=consumer_name, point=(0.0, 0.0, 0.0), axis=axis, radial=radial, radius=consumer_radius
    )
    return mate_axes(provider, consumer, require_fit=True)


def _plane_mate(*, provider_name, provider_point, provider_extent, consumer_name, consumer_extent):
    provider = PlaneInterface(
        name=provider_name,
        point=tuple(float(v) for v in provider_point),
        normal=(0.0, -1.0, 0.0),
        tangent_u=(1.0, 0.0, 0.0),
        extent=provider_extent,
    )
    consumer = PlaneInterface(
        name=consumer_name,
        point=(0.0, 0.0, 0.0),
        normal=(0.0, 1.0, 0.0),
        tangent_u=(1.0, 0.0, 0.0),
        extent=consumer_extent,
    )
    return mate_planes(provider, consumer)


# --------------------------------------------------------------------------- cabinet_body
def _build_box_carcass(carcass, r: ResolvedConfig, mats, tag: str) -> None:
    w, d = r.carcass_width_m, r.carcass_depth_m
    h = r.carcass_top_z_m - r.floor_z_m
    zc = (r.floor_z_m + r.carcass_top_z_m) / 2.0
    for i, sx in enumerate((-1.0, 1.0)):
        _wood_bx(
            carcass,
            (_WALL_T, d, h),
            (sx * (w / 2 - _WALL_T / 2), 0.0, zc),
            mats["carcass"],
            f"{tag}__side_panel_{i}",
        )
    _wood_bx(
        carcass,
        (w, d, _WALL_T),
        (0.0, 0.0, r.floor_z_m + _WALL_T / 2),
        mats["carcass"],
        f"{tag}__floor_panel",
    )
    _wood_bx(
        carcass,
        (w, d, _CAP_T),
        (0.0, 0.0, r.carcass_top_z_m - _CAP_T / 2),
        mats["carcass"],
        f"{tag}__top_panel",
    )
    _wood_bx(
        carcass,
        (w - 2 * _WALL_T + 0.006, _BACK_T, h - 0.010),
        (0.0, d / 2 - _BACK_T / 2, zc),
        mats["dark"],
        f"{tag}__back_panel",
    )
    # Keep the repeated interior shelf ladder at the rear of the cavity.  This
    # preserves the source cabinet read while leaving the full front envelope
    # available to a stacked drawer or a hinged leaf.
    shelf_d = min(0.040, max(0.018, d - _BACK_T - 0.020))
    for i, z in enumerate(_shelf_levels(r)):
        _wood_bx(
            carcass,
            (w - 2 * _WALL_T + 0.006, shelf_d, _SHELF_T),
            (0.0, r.back_y_m - shelf_d / 2.0, z),
            mats["carcass"],
            f"{tag}__shelf_{i}",
        )


def _shelf_zone_h(r: ResolvedConfig) -> float:
    """Use the whole low-cabinet cavity for the repeated rear shelf ladder."""

    cavity = max(r.cavity_hi_z_m - r.cavity_lo_z_m, 0.06)
    return cavity


def _shelf_levels(r: ResolvedConfig) -> list[float]:
    hi = r.cavity_hi_z_m - 0.006
    lo = hi - _shelf_zone_h(r)
    return [lo + (i + 1) * (hi - lo) / (r.shelf_count + 1) for i in range(r.shelf_count)]


def _cabinet_body_base_cabinet_build(carcass, r, mats) -> None:
    _build_box_carcass(carcass, r, mats, "cabinet_body__base_cabinet")


def _cabinet_body_plinth_deck_cabinet_build(carcass, r, mats) -> None:
    """002/004/005: the deck is raised over a recessed toe board.

    The side panels still run to the floor line, but the storage deck sits a
    plinth height above them and a dark toe rail is set back from the front, so
    the base reads as a plinth rather than an open leg bay.
    """

    tag = "cabinet_body__plinth_deck_cabinet"
    _build_box_carcass(carcass, r, mats, tag)
    w, d = r.carcass_width_m, r.carcass_depth_m
    deck_z = r.floor_z_m + _WALL_T + _PLINTH_RISE
    _wood_bx(
        carcass,
        (w - 2 * _WALL_T + 0.004, d - _BACK_T, _WALL_T),
        (0.0, -_BACK_T / 2.0, deck_z - _WALL_T / 2),
        mats["carcass"],
        f"{tag}__bottom_deck",
    )
    _wood_bx(
        carcass,
        (w - 2 * _WALL_T - 0.010, 0.018, _PLINTH_RISE - 0.008),
        (
            0.0,
            r.front_y_m + _TOE_SETBACK,
            r.floor_z_m + _WALL_T + (_PLINTH_RISE - 0.008) / 2.0,
        ),
        mats["dark"],
        f"{tag}__recessed_toe_rail",
    )


_BODY_BUILDERS = {
    "base_cabinet": _cabinet_body_base_cabinet_build,
    "plinth_deck_cabinet": _cabinet_body_plinth_deck_cabinet_build,
}


# --------------------------------------------------------------------------- top_treatment
def _top_treatment_laminate_worktop_build(carcass, r, mats) -> None:
    tag = "top_treatment__laminate_worktop"
    w, d = r.carcass_width_m, r.carcass_depth_m
    over = 0.020 + d * 0.02
    thickness = r.worktop_t_m
    _wood_bx(
        carcass,
        (w + 0.020, d + over, thickness),
        (0.0, -over / 2.0, r.carcass_top_z_m + thickness / 2 - 0.004),
        mats["worktop"],
        f"{tag}__worktop_slab",
    )
    _wood_bx(
        carcass,
        (w + 0.020, 0.012, thickness * 0.5),
        (0.0, -d / 2 - over / 2 + 0.006, r.carcass_top_z_m + thickness * 0.25),
        mats["worktop"],
        f"{tag}__worktop_edge",
    )


def _worktop_slab(r) -> tuple[float, float, float, float, float]:
    """Shared slab envelope: (width, depth, front overhang, thickness, bottom z).

    Every top candidate keeps this bottom plane.  It is the only clearance the
    lift flap has when it swings out to horizontal under the front overhang, so
    no top member is allowed to hang below it.
    """

    d = r.carcass_depth_m
    over = 0.020 + d * 0.02
    return (r.carcass_width_m + 0.020, d + over, over, r.worktop_t_m, r.carcass_top_z_m - 0.004)


def _top_treatment_stone_slab_worktop_build(carcass, r, mats) -> None:
    """Heavy slab read: a bullnose runs the full front and both side edges.

    The nose is a half-round of the slab's own thickness, so the profile stays
    inside the slab's z band and the extra reach is a real rounded edge rather
    than a thicker box.
    """

    tag = "top_treatment__stone_slab_worktop"
    sw, sd, over, t, z_b = _worktop_slab(r)
    z_c = z_b + t / 2.0
    y_c = -over / 2.0
    nose_r = t / 2.0
    _stone_bx(carcass, (sw, sd, t), (0.0, y_c, z_c), mats["worktop"], f"{tag}__worktop_slab")
    _stone_cy(
        carcass,
        nose_r,
        sw,
        (0.0, y_c - sd / 2.0, z_c),
        mats["worktop"],
        f"{tag}__front_bullnose",
        rpy=(0.0, math.pi / 2, 0.0),
    )
    for i, sx in enumerate((-1.0, 1.0)):
        _stone_cy(
            carcass,
            nose_r,
            sd,
            (sx * sw / 2.0, y_c, z_c),
            mats["worktop"],
            f"{tag}__side_bullnose_{i}",
            rpy=(math.pi / 2, 0.0, 0.0),
        )
        # A vertical quarter-round closes the mitre where the two noses meet.
        _stone_cy(
            carcass,
            nose_r,
            t,
            (sx * sw / 2.0, y_c - sd / 2.0, z_c),
            mats["worktop"],
            f"{tag}__front_corner_round_{i}",
        )


def _top_treatment_worktop_with_upstand_build(carcass, r, mats) -> None:
    """Slab plus a rear upstand, short side returns and a scotia fillet."""

    tag = "top_treatment__worktop_with_upstand"
    sw, sd, over, t, z_b = _worktop_slab(r)
    y_c = -over / 2.0
    top_z = z_b + t
    back_y = y_c + sd / 2.0
    up_h = r.upstand_h_m
    _wood_bx(
        carcass, (sw, sd, t), (0.0, y_c, z_b + t / 2.0), mats["worktop"], f"{tag}__worktop_slab"
    )
    _wood_bx(
        carcass,
        (sw, _UPSTAND_T, up_h),
        (0.0, back_y - _UPSTAND_T / 2.0, top_z + up_h / 2.0 - 0.004),
        mats["worktop"],
        f"{tag}__rear_upstand",
    )
    _wood_cy(
        carcass,
        _SCOTIA_R,
        sw,
        (0.0, back_y - _UPSTAND_T - _SCOTIA_R + 0.004, top_z + _SCOTIA_R - 0.004),
        mats["worktop"],
        f"{tag}__scotia_fillet",
        rpy=(0.0, math.pi / 2, 0.0),
    )
    ret_d = min(_UPSTAND_RETURN_D, sd * 0.4)
    for i, sx in enumerate((-1.0, 1.0)):
        _wood_bx(
            carcass,
            (_UPSTAND_T, ret_d, up_h),
            (
                sx * (sw / 2.0 - _UPSTAND_T / 2.0),
                back_y - ret_d / 2.0,
                top_z + up_h / 2.0 - 0.004,
            ),
            mats["worktop"],
            f"{tag}__side_return_{i}",
        )
    _wood_bx(
        carcass,
        (sw, 0.012, t * 0.5),
        (0.0, y_c - sd / 2.0 + 0.006, z_b + t * 0.25),
        mats["worktop"],
        f"{tag}__worktop_edge",
    )


_TOP_BUILDERS = {
    "laminate_worktop": _top_treatment_laminate_worktop_build,
    "stone_slab_worktop": _top_treatment_stone_slab_worktop_build,
    "worktop_with_upstand": _top_treatment_worktop_with_upstand_build,
}


# --------------------------------------------------------------------------- support_base
def _leg_inset(r: ResolvedConfig) -> tuple[float, float]:
    """Leg centre offsets shared by every support candidate."""

    return (
        max(r.carcass_width_m / 2 - 0.055, 0.030),
        max(r.carcass_depth_m / 2 - 0.055, 0.030),
    )


def _leg_quad_build(carcass, r, mats, tag: str) -> None:
    h = r.floor_z_m
    lx, ly = _leg_inset(r)
    for i, (x, y) in enumerate(((-lx, -ly), (lx, -ly), (-lx, ly), (lx, ly))):
        _rubber_cy(carcass, 0.021, 0.010, (x, y, 0.005), mats["dark"], f"{tag}__foot_{i}")
        stem_h = max(h - 0.018, 0.040)
        _metal_cy(
            carcass, 0.008, stem_h, (x, y, 0.010 + stem_h / 2.0), mats["metal"], f"{tag}__stem_{i}"
        )
        _metal_bx(
            carcass, (0.048, 0.048, 0.008), (x, y, h - 0.004), mats["dark"], f"{tag}__mount_{i}"
        )


def _support_base_adjustable_legs_build(carcass, r, mats) -> None:
    _leg_quad_build(carcass, r, mats, "support_base__adjustable_legs")


def _support_base_legs_with_toe_board_build(carcass, r, mats) -> None:
    """Same four legs as 001, with 004's dark rail closing the front of the bay."""

    tag = "support_base__legs_with_toe_board"
    _leg_quad_build(carcass, r, mats, tag)
    h = r.floor_z_m
    lx, ly = _leg_inset(r)
    # The board straddles the front leg shafts, so it stays one connected solid
    # with the legs and the carcass floor panel it runs up into.
    half_w = min(lx + _TOE_BOARD_SIDE_REACH, r.carcass_width_m / 2 - 0.006)
    top_z = h + _TOE_BOARD_EMBED
    bottom_z = _TOE_BOARD_FLOOR_RATIO * h
    _wood_bx(
        carcass,
        (2 * half_w, _TOE_BOARD_T, top_z - bottom_z),
        (0.0, -ly - _TOE_BOARD_OVERBITE, (top_z + bottom_z) / 2.0),
        mats["dark"],
        f"{tag}__toe_board",
    )


def _support_base_solid_plinth_build(carcass, r, mats) -> None:
    """A continuous recessed plinth on the front and both sides.

    The three boards mitre into each other at the front corners and each ends
    0.008 inside the carcass floor panel, so the skirt is one solid with the
    carcass.  A dark reveal strip under the top edge keeps the shadow gap that
    separates a plinth from the carcass in every source photo.
    """

    tag = "support_base__solid_plinth"
    w, d, h = r.carcass_width_m, r.carcass_depth_m, r.floor_z_m
    back = r.plinth_setback_m
    top_z = h + _TOE_BOARD_EMBED
    board_h = top_z
    front_y = r.front_y_m + back + _PLINTH_T / 2.0
    side_x = w / 2.0 - back - _PLINTH_T / 2.0
    side_d = d - back - _PLINTH_T
    side_y = r.front_y_m + back + side_d / 2.0
    _wood_bx(
        carcass,
        (2.0 * (side_x + _PLINTH_T / 2.0), _PLINTH_T, board_h),
        (0.0, front_y, board_h / 2.0),
        mats["carcass"],
        f"{tag}__plinth_board_front",
    )
    for i, sx in enumerate((-1.0, 1.0)):
        _wood_bx(
            carcass,
            (_PLINTH_T, side_d, board_h),
            (sx * side_x, side_y, board_h / 2.0),
            mats["carcass"],
            f"{tag}__plinth_board_side_{i}",
        )
    # Shadow reveal: a recessed dark band just under the carcass overhang.
    _wood_bx(
        carcass,
        (2.0 * (side_x + _PLINTH_T / 2.0) - 0.004, 0.010, _PLINTH_REVEAL_H),
        (0.0, front_y - _PLINTH_T / 2.0 + 0.005, h - _PLINTH_REVEAL_H / 2.0),
        mats["dark"],
        f"{tag}__plinth_reveal_front",
    )
    for i, sx in enumerate((-1.0, 1.0)):
        _wood_bx(
            carcass,
            (0.010, side_d - 0.004, _PLINTH_REVEAL_H),
            (
                sx * (side_x + _PLINTH_T / 2.0 - 0.005),
                side_y,
                h - _PLINTH_REVEAL_H / 2.0,
            ),
            mats["dark"],
            f"{tag}__plinth_reveal_side_{i}",
        )


def _support_base_block_feet_build(carcass, r, mats) -> None:
    """Four chunky square timber blocks on felt glides instead of slim stems."""

    tag = "support_base__block_feet"
    h = r.floor_z_m
    lx, ly = _leg_inset(r)
    bw = min(_BLOCK_FOOT_W, 2.0 * lx - 0.020, 2.0 * ly - 0.020)
    # The block sinks into the glide so the foot stays one connected solid.
    block_lo = _BLOCK_GLIDE_H - 0.004
    block_hi = h + _TOE_BOARD_EMBED
    for i, (x, y) in enumerate(((-lx, -ly), (lx, -ly), (-lx, ly), (lx, ly))):
        _rubber_cy(
            carcass,
            bw * 0.40,
            _BLOCK_GLIDE_H,
            (x, y, _BLOCK_GLIDE_H / 2.0),
            mats["dark"],
            f"{tag}__glide_{i}",
        )
        _wood_bx(
            carcass,
            (bw, bw, block_hi - block_lo),
            (x, y, (block_hi + block_lo) / 2.0),
            mats["carcass"],
            f"{tag}__foot_block_{i}",
        )
        # A slimmer collar reads as the chamfer where the block meets the case.
        _metal_bx(
            carcass,
            (bw + 0.010, bw + 0.010, 0.010),
            (x, y, h - 0.005),
            mats["dark"],
            f"{tag}__block_cap_{i}",
        )


_SUPPORT_BUILDERS = {
    "adjustable_legs": _support_base_adjustable_legs_build,
    "legs_with_toe_board": _support_base_legs_with_toe_board_build,
    "solid_plinth": _support_base_solid_plinth_build,
    "block_feet": _support_base_block_feet_build,
}

# (name token, exact count) per candidate.  The author check reads this instead
# of hard-coding one candidate's member list.
_SUPPORT_MEMBERS: dict[str, tuple[tuple[str, int], ...]] = {
    "adjustable_legs": (("__foot_", 4), ("__stem_", 4), ("__mount_", 4)),
    "legs_with_toe_board": (("__foot_", 4), ("__stem_", 4), ("__mount_", 4), ("__toe_board", 1)),
    "solid_plinth": (("__plinth_board_", 3), ("__plinth_reveal_", 3)),
    "block_feet": (("__glide_", 4), ("__foot_block_", 4), ("__block_cap_", 4)),
}


# --------------------------------------------------------------------------- door_face
def _face_frame_w(r: ResolvedConfig, w: float, h: float) -> float:
    """Frame width scales with the parameter instead of being clipped away."""

    return r.shaker_frame_w_m * min(1.0, w / 0.240, h / 0.240)


def _door_face_shaker_panel_build(unit, r, mats, w, h, y0, tag) -> None:
    """Front authored around (0, y0, 0): y0 is the outer face plane."""

    t = r.front_t_m
    frame = _face_frame_w(r, w, h)
    _wood_bx(unit, (w, t, h), (0.0, y0 + t / 2, 0.0), mats["front"], f"{tag}__front_slab")
    fw = max(w - 2 * frame, w * 0.2)
    fh = max(h - 2 * frame, h * 0.2)
    _wood_bx(
        unit, (fw, 0.008, fh), (0.0, y0 + t - 0.004, 0.0), mats["carcass"], f"{tag}__recessed_panel"
    )
    for label, (dx, dz, sx, sz) in {
        "stile_left": (-(w - frame) / 2, 0.0, frame, h),
        "stile_right": ((w - frame) / 2, 0.0, frame, h),
        "rail_top": (0.0, (h - frame) / 2, fw, frame),
        "rail_bottom": (0.0, -(h - frame) / 2, fw, frame),
    }.items():
        _wood_bx(unit, (sx, 0.010, sz), (dx, y0 - 0.003, dz), mats["front"], f"{tag}__{label}")
    _bar_pull(unit, r, mats, w, h, y0, tag)


def _door_face_flat_panel_build(unit, r, mats, w, h, y0, tag) -> None:
    _wood_bx(
        unit,
        (w, r.front_t_m, h),
        (0.0, y0 + r.front_t_m / 2, 0.0),
        mats["front"],
        f"{tag}__front_slab",
    )
    _bar_pull(unit, r, mats, w, h, y0, tag)


def _door_face_seamed_slab_build(unit, r, mats, w, h, y0, tag) -> None:
    """004.png L150-L210: a full slab with proud frame members and routed seams.

    The centre field stays flush with the slab instead of being recessed, and
    four dark seam strips outline it, which is how 004 reads its front.
    """

    t = r.front_t_m
    frame = _face_frame_w(r, w, h) * 0.72
    _wood_bx(unit, (w, t, h), (0.0, y0 + t / 2, 0.0), mats["front"], f"{tag}__front_slab")
    fw = max(w - 2 * frame, w * 0.2)
    fh = max(h - 2 * frame, h * 0.2)
    for label, (dx, dz, sx, sz) in {
        "rail_top": (0.0, (h - frame) / 2, w, frame),
        "rail_bottom": (0.0, -(h - frame) / 2, w, frame),
        "stile_left": (-(w - frame) / 2, 0.0, frame, h - 2 * frame),
        "stile_right": ((w - frame) / 2, 0.0, frame, h - 2 * frame),
    }.items():
        _wood_bx(unit, (sx, 0.010, sz), (dx, y0 - 0.003, dz), mats["front"], f"{tag}__{label}")
    for label, (dx, dz, sx, sz) in {
        "seam_top": (0.0, fh / 2 - 0.002, fw, 0.004),
        "seam_bottom": (0.0, -(fh / 2 - 0.002), fw, 0.004),
        "seam_left": (-(fw / 2 - 0.002), 0.0, 0.004, fh),
        "seam_right": ((fw / 2 - 0.002), 0.0, 0.004, fh),
    }.items():
        _wood_bx(unit, (sx, 0.004, sz), (dx, y0 - 0.001, dz), mats["dark"], f"{tag}__{label}")
    _bar_pull(unit, r, mats, w, h, y0, tag)


def _handle_layout(r: ResolvedConfig, w: float, h: float, y0: float):
    x = (r.handle_horizontal_position_ratio - 0.5) * w
    z = (r.handle_vertical_position_ratio - 0.5) * h
    radius = _handle_radius(r.handle_type, r.handle_thickness_m)
    long_axis = (
        math.cos(r.handle_orientation_rad),
        0.0,
        math.sin(r.handle_orientation_rad),
    )
    if r.handle_type == "bar":
        y = y0 - r.handle_clearance_m - radius
        rpy = (0.0, math.pi / 2.0 - r.handle_orientation_rad, 0.0)
    else:
        cap_length = max(r.handle_thickness_m * 0.70, 0.010)
        y = y0 - r.handle_clearance_m - cap_length / 2.0
        rpy = (math.pi / 2.0, 0.0, 0.0)
    return (x, y, z), long_axis, rpy


def _bar_pull(unit, r, mats, w, h, y0, tag) -> None:
    """Build the configured pull on a face whose outer plane is ``y0``.

    A bar's cylinder axis lies at ``handle_orientation_rad`` in the local X/Z
    panel plane.  Its two Y-axis posts overlap both the panel and the grip so
    the visual geometry remains connected at every supported orientation.
    """

    centre, long_axis, bar_rpy = _handle_layout(r, w, h, y0)
    x, y, z = centre
    radius = _handle_radius(r.handle_type, r.handle_thickness_m)
    embed = min(max(radius * 0.30, 0.0015), 0.003)
    if r.handle_type == "knob":
        cap_length = max(r.handle_thickness_m * 0.70, 0.010)
        _metal_cy(
            unit,
            radius,
            cap_length,
            centre,
            mats["metal"],
            f"{tag}__pull_knob",
            rpy=bar_rpy,
        )
        stem_length = r.handle_clearance_m + 2.0 * embed
        _metal_cy(
            unit,
            min(max(r.handle_thickness_m * 0.50, 0.003), radius),
            stem_length,
            (x, y0 - r.handle_clearance_m / 2.0, z),
            mats["metal"],
            f"{tag}__pull_mount_0",
            rpy=(math.pi / 2.0, 0.0, 0.0),
        )
        return

    _metal_cy(
        unit,
        radius,
        r.handle_length_m,
        centre,
        mats["metal"],
        f"{tag}__pull_bar",
        rpy=bar_rpy,
    )
    post_radius = min(max(radius * 0.65, 0.003), 0.008)
    post_offset = max(r.handle_length_m / 2.0 - 1.5 * radius, r.handle_length_m * 0.30)
    post_length = r.handle_clearance_m + radius + 2.0 * embed
    for index, sign in enumerate((-1.0, 1.0)):
        _metal_cy(
            unit,
            post_radius,
            post_length,
            (
                x + sign * post_offset * long_axis[0],
                y0 - (r.handle_clearance_m + radius) / 2.0,
                z + sign * post_offset * long_axis[2],
            ),
            mats["metal"],
            f"{tag}__pull_mount_{index}",
            rpy=(math.pi / 2.0, 0.0, 0.0),
        )


def _door_face_reeded_slab_build(unit, r, mats, w, h, y0, tag) -> None:
    """A fluted front: repeated proud half-reeds between two plain stiles.

    The reed pitch is derived from the real leaf width, so a narrow drawer front
    and a wide door carry the same reed rhythm instead of a stretched pattern.
    """

    t = r.front_t_m
    _wood_bx(unit, (w, t, h), (0.0, y0 + t / 2, 0.0), mats["front"], f"{tag}__front_slab")
    stile = min(max(0.018, _face_frame_w(r, w, h) * 0.45), w * 0.18)
    field_w = max(w - 2 * stile, w * 0.30)
    count = int(max(3, min(16, field_w // 0.034)))
    pitch = field_w / count
    reed_w = pitch * 0.62
    reed_h = max(h - 0.020, h * 0.60)
    reed_r = min(reed_w / 2.0, 0.008)
    for i in range(count):
        x = -field_w / 2.0 + (i + 0.5) * pitch
        _wood_bx(
            unit, (reed_w, 0.010, reed_h), (x, y0 - 0.003, 0.0), mats["front"], f"{tag}__reed_{i}"
        )
        # Vertical half-round nose on each reed; the axis runs up the leaf.
        _wood_cy(
            unit, reed_r, reed_h, (x, y0 - 0.008, 0.0), mats["front"], f"{tag}__reed_round_{i}"
        )
    for i, sx in enumerate((-1.0, 1.0)):
        _wood_bx(
            unit,
            (stile, 0.010, h),
            (sx * (w - stile) / 2.0, y0 - 0.003, 0.0),
            mats["front"],
            f"{tag}__stile_{i}",
        )
    _bar_pull(unit, r, mats, w, h, y0, tag)


_FACE_BUILDERS = {
    "shaker_panel": _door_face_shaker_panel_build,
    "flat_panel": _door_face_flat_panel_build,
    "seamed_slab": _door_face_seamed_slab_build,
    "reeded_slab": _door_face_reeded_slab_build,
}


# --------------------------------------------------------------------------- access_module
def _opening(r: ResolvedConfig) -> tuple[float, float, float, float]:
    return (-r.half_w_m, r.half_w_m, r.cavity_lo_z_m + 0.004, r.cavity_hi_z_m - 0.004)


def _new_unit(model, r, index, mech):
    return model.part(
        f"door_face__{r.door_face}__access_unit_{index}",
        meta={
            "role": "access_unit",
            "slot": "access_module",
            "candidate": r.access_module,
            "index": index,
            "mechanism": mech,
        },
    )


def _access_module_hinged_doors_build(model, carcass, r, mats) -> list[object]:
    tag = "access_module__hinged_doors"
    x0, x1, z0, z1 = _opening(r)
    n = r.access_count
    zc = (z0 + z1) / 2.0
    leaf_h = max(z1 - z0 - 0.006, 0.080)
    cell_w = (x1 - x0) / n
    hinge_y = r.front_y_m - _FRONT_GAP - r.front_t_m / 2
    units = []
    for k in range(n):
        cell_x0 = x0 + k * cell_w
        hinge_left = k < n / 2.0 or n == 1
        sign = 1.0 if hinge_left else -1.0
        hinge_x = cell_x0 + _OUTER_REVEAL if hinge_left else cell_x0 + cell_w - _OUTER_REVEAL
        leaf_w = max(cell_w - _OUTER_REVEAL - _SETBACK - _REVEAL, _MIN_LEAF_W)
        has_neighbour = (k > 0) if hinge_left else (k < n - 1)
        limit = min(r.door_swing_rad, math.pi / 2 - 0.03) if has_neighbour else r.door_swing_rad
        unit = _new_unit(model, r, k, "vertical butt hinge")
        _FACE_BUILDERS[r.door_face](
            unit, r, mats, leaf_w, leaf_h, -r.front_t_m / 2, f"door_face__{r.door_face}"
        )
        # shift the whole face out along the leaf, away from the hinge line
        for v in list(unit.visuals):
            x, y, z = v.origin.xyz
            v.origin = Origin(xyz=(x + sign * (_SETBACK + leaf_w / 2), y, z), rpy=v.origin.rpy)
        for si, station in enumerate((-leaf_h * 0.34, leaf_h * 0.34)):
            _metal_cy(
                carcass,
                _BARREL_R,
                0.030,
                (hinge_x, hinge_y, zc + station),
                mats["metal"],
                f"{tag}__fixed_knuckle_{k}_{si}",
            )
            _metal_bx(
                carcass,
                (0.018, 0.030, 0.020),
                (hinge_x, hinge_y + 0.016, zc + station),
                mats["metal"],
                f"{tag}__knuckle_plate_{k}_{si}",
            )
            for bi, off in enumerate((-0.022, 0.022)):
                _metal_cy(
                    unit,
                    _BARREL_R * 0.86,
                    0.022,
                    (0.0, 0.0, station + off),
                    mats["metal"],
                    f"{tag}__barrel_{k}_{si}_{bi}",
                )
                reach = _SETBACK + 0.008
                _metal_bx(
                    unit,
                    (reach, 0.012, 0.016),
                    (sign * reach / 2.0, 0.0, station + off),
                    mats["metal"],
                    f"{tag}__hinge_strap_{k}_{si}_{bi}",
                )
        _wood_bx(
            carcass,
            (0.038, 0.018, z1 - z0 + 0.012),
            (hinge_x, hinge_y + 0.018, zc),
            mats["carcass"],
            f"{tag}__hinge_mullion_{k}",
        )
        mate = _axis_mate(
            provider_name=f"cabinet_body.front_opening.hinge_{k}",
            point=(hinge_x, hinge_y, zc),
            axis=(0.0, 0.0, 1.0),
            radial=(1.0, 0.0, 0.0),
            consumer_name=f"access_module.unit_mount_{k}",
            consumer_radius=_BARREL_R * 0.86,
        )
        joint = f"{tag}__unit_joint_{k}"
        lower, upper = (-limit, 0.0) if sign > 0 else (0.0, limit)
        model.articulation(
            joint,
            ArticulationType.REVOLUTE,
            parent=carcass,
            child=unit,
            origin=mate.origin,
            axis=mate.axis,
            motion_limits=MotionLimits(effort=12.0, velocity=1.5, lower=lower, upper=upper),
            meta={"positive_motion": "leaf swings outward toward -Y"},
        )
        register_interface_mate(model, joint, mate)
        units.append(unit)
    return units


def _drawer_stack_layout(r: ResolvedConfig):
    x0, x1, z0, z1 = _opening(r)
    gap = _LEVEL_REVEAL
    band = (z1 - z0 - (r.access_count - 1) * gap) / r.access_count
    if band < _MIN_FRONT_H:
        gap = 0.002
        band = max((z1 - z0 - (r.access_count - 1) * gap) / r.access_count, 0.024)
    y_front = r.front_y_m + 0.010
    y_back = r.back_y_m
    box_depth = max(y_back - y_front - 0.050, 0.140) + _TRAY_FRONT_REACH
    travel = min(box_depth * r.drawer_travel_ratio, box_depth * 0.60)
    return x0, x1, z0, z1, gap, band, y_front, y_back, box_depth, travel


def _drawer_handle_frame(r: ResolvedConfig, index: int) -> dict[str, object]:
    x0, x1, z0, _z1, gap, band, y_front, _y_back, _box_depth, _travel = _drawer_stack_layout(r)
    lz0 = z0 + index * (band + gap)
    floor_z = lz0 + 0.012
    face_width = x1 - x0 - 0.004
    face_height = band - 0.004
    face_y0 = r.front_y_m - _FRONT_GAP - r.front_t_m - y_front
    centre, long_axis, handle_rpy = _handle_layout(r, face_width, face_height, face_y0)
    face_centre_z_in_link = lz0 + band / 2.0 - floor_z
    target_link = f"door_face__{r.door_face}__access_unit_{index}"
    origin_xyz = [centre[0], centre[1], centre[2] + face_centre_z_in_link]
    return {
        "parent_link": target_link,
        "origin_xyz": origin_xyz,
        "origin_xyz_object_rest": [
            origin_xyz[0],
            y_front + origin_xyz[1],
            floor_z + origin_xyz[2],
        ],
        "orientation_rpy": list(handle_rpy),
        "grip_axis": list(long_axis) if r.handle_type == "bar" else [0.0, -1.0, 0.0],
        "approach_axis": [0.0, -1.0, 0.0],
    }


def _access_module_drawer_stack_build(model, carcass, r, mats) -> list[object]:
    tag = "access_module__drawer_stack"
    x0, x1, z0, z1, gap, band, y_front, y_back, box_depth, travel = _drawer_stack_layout(r)
    n = r.access_count
    units = []
    z = z0
    for k in range(n):
        lz0, lz1 = z, z + band
        cell_w = x1 - x0
        tray_half = max(cell_w / 2.0 - _RAIL_W - _SIDE_CLEAR, 0.040)
        tray_w = 2 * tray_half
        # Leave a small rear service ledge for the repeated interior shelf and
        # back panel; the tray remains a genuine open-top box with full front
        # access and side runners.
        floor_z = lz0 + 0.012
        box_h = max(min(band - 0.020, lz1 - floor_z - 0.006), 0.022)
        box_cy = box_depth / 2.0 - _TRAY_FRONT_REACH
        unit = _new_unit(model, r, k, "side runner slide")
        _wood_bx(
            unit,
            (tray_w, box_depth, _TRAY_FLOOR_T),
            (0.0, box_cy, _TRAY_FLOOR_T / 2),
            mats["carcass"],
            f"{tag}__tray_floor_{k}",
        )
        for side, sign in enumerate((-1.0, 1.0)):
            _wood_bx(
                unit,
                (_TRAY_WALL_T, box_depth, box_h),
                (sign * (tray_half - _TRAY_WALL_T / 2), box_cy, box_h / 2),
                mats["carcass"],
                f"{tag}__tray_side_{k}_{side}",
            )
            _metal_bx(
                unit,
                (_RUNNER_W, box_depth, _RAIL_H),
                (sign * (tray_half + _RUNNER_W / 2 - _RUNNER_ENGAGE), box_cy, -0.001),
                mats["dark"],
                f"{tag}__tray_runner_{k}_{side}",
            )
            outer = max(r.half_w_m - abs(x0 if side == 0 else x1), 0.0) + _RAIL_EMBED
            direction = 1.0 if side == 0 else -1.0
            _metal_bx(
                carcass,
                (_RAIL_W + outer, max(y_back + 0.004 - (y_front + 0.002), 0.10), _RAIL_H),
                (
                    (x0 if side == 0 else x1) + direction * (_RAIL_W - outer) / 2.0,
                    (y_front + 0.002 + y_back + 0.004) / 2.0,
                    lz0 + _RAIL_H / 2 - 0.002,
                ),
                mats["dark"],
                f"{tag}__runner_rail_{k}_{side}",
            )
        _wood_bx(
            unit,
            (tray_w, _TRAY_WALL_T, box_h),
            (0.0, box_depth - _TRAY_FRONT_REACH - _TRAY_WALL_T / 2, box_h / 2),
            mats["carcass"],
            f"{tag}__tray_rear_{k}",
        )
        if k > 0:
            _wood_bx(
                carcass,
                (2 * r.half_w_m + 0.020, max(y_back - y_front, 0.10), 0.010),
                (0.0, (y_front + y_back) / 2.0, lz0 - gap / 2),
                mats["dark"],
                f"{tag}__level_rail_{k}",
            )
        face_y0 = r.front_y_m - _FRONT_GAP - r.front_t_m - (y_front)
        _FACE_BUILDERS[r.door_face](
            unit, r, mats, cell_w - 0.004, band - 0.004, face_y0, f"door_face__{r.door_face}"
        )
        for v in list(unit.visuals):
            if "door_face__" in str(v.name):
                x, y, zz = v.origin.xyz
                v.origin = Origin(xyz=(x, y, zz + (lz0 + lz1) / 2.0 - floor_z), rpy=v.origin.rpy)
        unit.meta["handle_frame"] = _drawer_handle_frame(r, k)
        unit.meta["handle"] = {
            "type": r.handle_type,
            "orientation_rad": r.handle_orientation_rad,
            "length_m": r.handle_length_m,
            "thickness_m": r.handle_thickness_m,
            "clearance_m": r.handle_clearance_m,
            "horizontal_position_ratio": r.handle_horizontal_position_ratio,
            "vertical_position_ratio": r.handle_vertical_position_ratio,
        }
        mate = _plane_mate(
            provider_name=f"cabinet_body.front_opening.cell_{k}",
            provider_point=((x0 + x1) / 2.0, y_front, floor_z),
            provider_extent=(cell_w, band),
            consumer_name=f"access_module.unit_mount_{k}",
            consumer_extent=(tray_w, box_h),
        )
        joint = f"{tag}__unit_joint_{k}"
        model.articulation(
            joint,
            ArticulationType.PRISMATIC,
            parent=carcass,
            child=unit,
            origin=mate.origin,
            axis=(0.0, -1.0, 0.0),
            motion_limits=MotionLimits(effort=55.0, velocity=0.30, lower=0.0, upper=travel),
            meta={"mechanism": "side runner pair riding on the carcass rails"},
        )
        register_interface_mate(model, joint, mate)
        units.append(unit)
        z = lz1 + gap
    return units


def _access_module_lift_up_flap_build(model, carcass, r, mats) -> list[object]:
    tag = "access_module__lift_up_flap"
    x0, x1, z0, z1 = _opening(r)
    n = r.access_count
    cell_w = (x1 - x0) / n
    pivot_y = r.front_y_m - _FRONT_GAP - r.front_t_m / 2
    # one head rail carries every flap knuckle and reaches both side panels
    _wood_bx(
        carcass,
        (2 * r.half_w_m + 0.020, 0.024, 0.020),
        (0.0, pivot_y + 0.028, z1 - 0.008 + 0.013),
        mats["carcass"],
        f"{tag}__flap_head_rail",
    )
    units = []
    for k in range(n):
        cell_x0 = x0 + k * cell_w
        cx = cell_x0 + cell_w / 2.0
        flap_w = max(cell_w - 0.008, _MIN_LEAF_W)
        flap_h = max(z1 - z0 - 0.010, 0.070)
        pivot_z = z1 - 0.008
        unit = _new_unit(model, r, k, "top hinged lift flap")
        _FACE_BUILDERS[r.door_face](
            unit, r, mats, flap_w, flap_h, -r.front_t_m / 2, f"door_face__{r.door_face}"
        )
        for v in list(unit.visuals):
            x, y, z = v.origin.xyz
            v.origin = Origin(xyz=(x, y, z - (_SETBACK + flap_h / 2)), rpy=v.origin.rpy)
        stations = (cx - flap_w * 0.26, cx + flap_w * 0.26)
        for si, station in enumerate(stations):
            _metal_cy(
                carcass,
                _BARREL_R,
                0.028,
                (station, pivot_y, pivot_z),
                mats["metal"],
                f"{tag}__fixed_knuckle_{k}_{si}",
                rpy=(0.0, math.pi / 2, 0.0),
            )
            _metal_bx(
                carcass,
                (0.020, 0.028, 0.018),
                (station, pivot_y + 0.016, pivot_z + 0.013),
                mats["metal"],
                f"{tag}__knuckle_plate_{k}_{si}",
            )
            for bi, off in enumerate((-0.020, 0.020)):
                _metal_cy(
                    unit,
                    _BARREL_R * 0.86,
                    0.018,
                    (station - cx + off, 0.0, 0.0),
                    mats["metal"],
                    f"{tag}__barrel_{k}_{si}_{bi}",
                    rpy=(0.0, math.pi / 2, 0.0),
                )
                _metal_bx(
                    unit,
                    (0.016, 0.012, _SETBACK + 0.008),
                    (station - cx + off, 0.0, -(_SETBACK + 0.008) / 2.0),
                    mats["metal"],
                    f"{tag}__hinge_strap_{k}_{si}_{bi}",
                )
        stay_len = max(flap_h * math.sin(r.lift_flap_rad) * 0.5, 0.020)
        for si, station in enumerate(stations):
            _metal_bx(
                carcass,
                (0.012, 0.012, stay_len + 0.018),
                (station, pivot_y + 0.026, pivot_z + (stay_len - 0.018) / 2),
                mats["metal"],
                f"{tag}__stay_{k}_{si}",
            )
        mate = _axis_mate(
            provider_name=f"cabinet_body.front_opening.flap_{k}",
            point=(cx, pivot_y, pivot_z),
            axis=(1.0, 0.0, 0.0),
            radial=(0.0, 0.0, 1.0),
            consumer_name=f"access_module.unit_mount_{k}",
            consumer_radius=_BARREL_R * 0.86,
        )
        joint = f"{tag}__unit_joint_{k}"
        model.articulation(
            joint,
            ArticulationType.REVOLUTE,
            parent=carcass,
            child=unit,
            origin=mate.origin,
            axis=mate.axis,
            motion_limits=MotionLimits(
                effort=14.0, velocity=1.2, lower=-r.lift_flap_rad, upper=0.0
            ),
            meta={"positive_motion": "flap lifts up and out"},
        )
        register_interface_mate(model, joint, mate)
        units.append(unit)
    return units


_ACCESS_BUILDERS = {
    "hinged_doors": _access_module_hinged_doors_build,
    "drawer_stack": _access_module_drawer_stack_build,
    "lift_up_flap": _access_module_lift_up_flap_build,
}


# --------------------------------------------------------------------------- build
def build_pictureX_0611_kitchen_cabinet(
    config: Config | None = None, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    r = resolve_config(config or Config())
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = _materials(model, r.palette)
    carcass = model.part(
        "carcass", meta={"role": "carcass", "slot": "cabinet_body", "candidate": r.cabinet_body}
    )
    _SUPPORT_BUILDERS[r.support_base](carcass, r, mats)
    _BODY_BUILDERS[r.cabinet_body](carcass, r, mats)
    _TOP_BUILDERS[r.top_treatment](carcass, r, mats)
    _ACCESS_BUILDERS[r.access_module](model, carcass, r, mats)
    carcass.inertial = None
    model.meta["slot_choices"] = (
        ("cabinet_body", r.cabinet_body),
        ("access_module", r.access_module),
        ("door_face", r.door_face),
        ("top_treatment", r.top_treatment),
        ("support_base", r.support_base),
        ("access_count", str(r.access_count)),
        ("shelf_count", str(r.shelf_count)),
    )
    return model


def build_seeded_pictureX_0611_kitchen_cabinet(seed: int) -> ArticulatedObject:
    return build_pictureX_0611_kitchen_cabinet(config_from_seed(seed))


def _require_single_drawer(r: ResolvedConfig) -> None:
    if r.access_module != "drawer_stack" or r.access_count != 1:
        raise ValueError(
            "controlled single-drawer assets require "
            "access_module='drawer_stack' and access_count=1"
        )


def build_single_drawer_cabinet(
    config: Config | None = None, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    """Task-facing alias whose default is the canonical one-drawer cabinet."""

    resolved_config = config or Config()
    _require_single_drawer(resolve_config(resolved_config))
    return build_pictureX_0611_kitchen_cabinet(resolved_config, assets=assets)


def benchmark_metadata(config: Config) -> dict[str, object]:
    """Describe the canonical drawer task in JSON-friendly object coordinates."""

    r = resolve_config(config)
    _require_single_drawer(r)
    x0, x1, z0, z1, _gap, band, _y_front, _y_back, box_depth, travel = (
        _drawer_stack_layout(r)
    )
    opening_width = x1 - x0
    opening_height = z1 - z0
    front_width = opening_width - 0.004
    front_height = band - 0.004
    tray_width = 2.0 * max(opening_width / 2.0 - _RAIL_W - _SIDE_CLEAR, 0.040)
    tray_height = max(band - 0.020, 0.022)
    handle_frame = _drawer_handle_frame(r, 0)
    handle_rest_xyz = list(handle_frame["origin_xyz_object_rest"])
    joint_axis = [0.0, -1.0, 0.0]
    handle_open_xyz = [handle_rest_xyz[i] + travel * joint_axis[i] for i in range(3)]
    target_link = f"door_face__{r.door_face}__access_unit_0"
    return {
        "target_joint": "access_module__drawer_stack__unit_joint_0",
        "target_link": target_link,
        "joint_type": "prismatic",
        "axis": joint_axis,
        "limits": {"lower": 0.0, "upper": travel},
        "opening_sign": 1,
        "opening_endpoint": travel,
        "opening_endpoint_handle_origin_xyz": handle_open_xyz,
        "handle_frame": handle_frame,
        "front_axis": [0.0, -1.0, 0.0],
        "up_axis": [0.0, 0.0, 1.0],
        "object_frame": {
            "right_axis": [1.0, 0.0, 0.0],
            "front_axis": [0.0, -1.0, 0.0],
            "up_axis": [0.0, 0.0, 1.0],
        },
        "handle": {
            "type": r.handle_type,
            "orientation_rad": r.handle_orientation_rad,
            "length_m": r.handle_length_m,
            "thickness_m": r.handle_thickness_m,
            "effective_grip_radius_m": _handle_radius(r.handle_type, r.handle_thickness_m),
            "effective_grip_diameter_m": 2.0
            * _handle_radius(r.handle_type, r.handle_thickness_m),
            "clearance_m": r.handle_clearance_m,
            "horizontal_position_ratio": r.handle_horizontal_position_ratio,
            "vertical_position_ratio": r.handle_vertical_position_ratio,
            "position_ratio_convention": "0=left/bottom, 0.5=center, 1=right/top",
            "clearance_definition": "net gap from panel front plane to grip back surface",
            "active_parameters": (
                [
                    "orientation_rad",
                    "length_m",
                    "thickness_m",
                    "clearance_m",
                    "horizontal_position_ratio",
                    "vertical_position_ratio",
                ]
                if r.handle_type == "bar"
                else [
                    "thickness_m",
                    "clearance_m",
                    "horizontal_position_ratio",
                    "vertical_position_ratio",
                ]
            ),
        },
        "morphology": {
            "dependency_policy": "one explicit intervention with deterministic descendants",
            "carcass": {
                "variant": r.cabinet_body,
                "width_m": r.carcass_width_m,
                "depth_m": r.carcass_depth_m,
                "height_m": r.carcass_height_m,
            },
            "front_opening": {
                "width_m": opening_width,
                "height_m": opening_height,
            },
            "target_panel": {
                "profile": r.door_face,
                "width_m": front_width,
                "height_m": front_height,
                "nominal_thickness_m": r.front_t_m,
                "aspect_ratio_width_over_height": front_width / front_height,
            },
            "drawer_tray": {
                "width_m": tray_width,
                "depth_m": box_depth,
                "height_m": tray_height,
            },
            "motion": {
                "requested_travel_ratio": r.drawer_travel_ratio,
                "effective_travel_ratio": travel / box_depth,
                "joint_travel_m": travel,
            },
        },
    }


def run_pictureX_0611_kitchen_cabinet_tests(
    object_model: ArticulatedObject, config: Config
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    parts = {p.name: p for p in object_model.parts}
    roles: dict[str, list[str]] = {}
    for part in object_model.parts:
        role = str(getattr(part, "meta", {}).get("role") or "")
        if role:
            roles.setdefault(role, []).append(part.name)

    ctx.check(
        "category_anchor: one rigid cabinet carcass",
        len(roles.get("carcass", [])) == 1,
        details=str(roles.get("carcass")),
    )

    carcass_visual_names = {str(v.name) for v in parts["carcass"].visuals}
    top_prefix = f"top_treatment__{r.top_treatment}__"
    ctx.check(
        "category_anchor: a visible worktop closes the top of the carcass",
        f"{top_prefix}worktop_slab" in carcass_visual_names
        and sum(1 for name in carcass_visual_names if name.startswith("top_treatment__")) >= 2,
        details=f"top_treatment={r.top_treatment}",
    )
    support_prefix = f"support_base__{r.support_base}__"
    support_names = [name for name in carcass_visual_names if name.startswith(support_prefix)]
    expected = _SUPPORT_MEMBERS[r.support_base]
    ctx.check(
        "category_anchor: the carcass stands on its own floor support",
        all(sum(token in name for name in support_names) == n for token, n in expected)
        and len(support_names) == sum(n for _, n in expected),
        details=f"support_base={r.support_base} names={sorted(support_names)}",
    )
    ctx.check(
        "category_anchor: the toe board closes the front of the leg bay",
        (
            sum("__toe_board" in name for name in support_names) == 1
            if r.support_base == "legs_with_toe_board"
            else not any("__toe_board" in name for name in carcass_visual_names)
        ),
        details=f"support_base={r.support_base} names={sorted(support_names)}",
    )

    units = roles.get("access_unit", [])
    moving = {
        j.child: j
        for j in object_model.articulations
        if j.articulation_type != ArticulationType.FIXED
    }
    ctx.check(
        "category_anchor: every access unit is a moving child of the carcass",
        len(units) == r.access_count
        and all(name in moving and moving[name].parent == "carcass" for name in units),
        details=f"units={units} expected={r.access_count}",
    )

    shelves = [str(v.name) for v in parts["carcass"].visuals if "__shelf_" in str(v.name)]
    ctx.check(
        "category_anchor: the carcass carries its interior shelves",
        len(shelves) == r.shelf_count,
        details=str(shelves),
    )

    name = units[0]
    joint = moving[name]
    rest = ctx.part_world_aabb(parts[name])
    limit = joint.motion_limits.upper or joint.motion_limits.lower or 0.0
    with ctx.pose({joint: limit * 0.7}):
        opened = ctx.part_world_aabb(parts[name])
    if r.access_module == "hinged_doors":
        ctx.check(
            "category_anchor: hinged leaf opens outward from the front plane",
            rest is not None and opened is not None and opened[0][1] < rest[0][1] - 0.015,
            details=f"rest={None if rest is None else round(rest[0][1], 4)} open={None if opened is None else round(opened[0][1], 4)}",
        )
    elif r.access_module == "drawer_stack":
        hollow = all(
            any("__tray_floor_" in str(v.name) for v in parts[u].visuals)
            and sum(1 for v in parts[u].visuals if "__tray_side_" in str(v.name)) == 2
            and any("__tray_rear_" in str(v.name) for v in parts[u].visuals)
            for u in units
        )
        ctx.check(
            "category_anchor: drawer trays are hollow boxes",
            hollow,
            details="floor + two sides + rear on every tray",
        )
    else:
        moved = (
            0.0
            if rest is None or opened is None
            else abs((opened[0][2] + opened[1][2]) / 2 - (rest[0][2] + rest[1][2]) / 2)
        )
        ctx.check(
            "category_anchor: lift flap rotates about its horizontal pivot",
            moved > 0.010,
            details=f"dz={moved:.4f}",
        )

    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=64, ignore_fixed=True)
    return ctx.report()


run_pictureX_0611_kitchen_cabinet_tests.__test__ = False


def run_single_drawer_cabinet_tests(
    object_model: ArticulatedObject, config: Config
) -> TestReport:
    _require_single_drawer(resolve_config(config))
    return run_pictureX_0611_kitchen_cabinet_tests(object_model, config)


run_single_drawer_cabinet_tests.__test__ = False


TEMPLATE_CORNERS = (
    corner_case(
        "widest_base_three_hinged_shaker",
        {
            "cabinet_body": "base_cabinet",
            "access_module": "hinged_doors",
            "door_face": "shaker_panel",
            "top_treatment": "laminate_worktop",
            "support_base": "adjustable_legs",
            "access_count": 3,
            "shelf_count": 2,
            "carcass_width_m": 0.78,
            "carcass_depth_m": 0.62,
            "carcass_height_m": 0.82,
            "door_swing_rad": 1.90,
            "shaker_frame_w_m": 0.075,
            "worktop_t_m": 0.050,
            "plinth_leg_h_m": 0.180,
        },
        reason="widest compact base with repeated hinged fronts and the widest shaker frame",
    ),
    corner_case(
        "narrow_base_single_lift_flap",
        {
            "cabinet_body": "base_cabinet",
            "access_module": "lift_up_flap",
            "door_face": "flat_panel",
            "top_treatment": "laminate_worktop",
            "support_base": "adjustable_legs",
            "access_count": 1,
            "shelf_count": 1,
            "carcass_width_m": 0.48,
            "carcass_depth_m": 0.50,
            "carcass_height_m": 0.62,
            "lift_flap_rad": 1.55,
            "panel_t_m": 0.016,
            "worktop_t_m": 0.020,
            "plinth_leg_h_m": 0.080,
        },
        reason="smallest source-backed compact base at full lift travel",
    ),
    corner_case(
        "wide_base_three_drawers",
        {
            "cabinet_body": "base_cabinet",
            "access_module": "drawer_stack",
            "door_face": "flat_panel",
            "top_treatment": "laminate_worktop",
            "support_base": "adjustable_legs",
            "access_count": 3,
            "shelf_count": 2,
            "carcass_width_m": 0.78,
            "carcass_depth_m": 0.62,
            "carcass_height_m": 0.82,
            "drawer_travel_ratio": 0.62,
            "panel_t_m": 0.026,
            "worktop_t_m": 0.050,
            "plinth_leg_h_m": 0.180,
        },
        reason="widest compact base with the longest repeated drawer stroke",
    ),
    corner_case(
        "narrow_base_two_drawers_minimum",
        {
            "cabinet_body": "base_cabinet",
            "access_module": "drawer_stack",
            "door_face": "shaker_panel",
            "top_treatment": "laminate_worktop",
            "support_base": "adjustable_legs",
            "access_count": 2,
            "shelf_count": 1,
            "carcass_width_m": 0.48,
            "carcass_depth_m": 0.50,
            "carcass_height_m": 0.62,
            "drawer_travel_ratio": 0.34,
            "shaker_frame_w_m": 0.045,
            "worktop_t_m": 0.020,
            "plinth_leg_h_m": 0.080,
        },
        reason="narrowest compact base with the smallest drawer travel",
    ),
    corner_case(
        "widest_plinth_deck_toe_board_tallest_legs",
        {
            "cabinet_body": "plinth_deck_cabinet",
            "access_module": "hinged_doors",
            "door_face": "seamed_slab",
            "top_treatment": "laminate_worktop",
            "support_base": "legs_with_toe_board",
            "access_count": 3,
            "shelf_count": 2,
            "carcass_width_m": 0.86,
            "carcass_depth_m": 0.62,
            "carcass_height_m": 0.82,
            "door_swing_rad": 1.90,
            "worktop_t_m": 0.050,
            "plinth_leg_h_m": 0.180,
        },
        reason="widest plinth-deck host where the toe board spans the longest leg bay above the tallest legs",
    ),
    corner_case(
        "narrow_base_toe_board_shortest_legs",
        {
            "cabinet_body": "base_cabinet",
            "access_module": "drawer_stack",
            "door_face": "flat_panel",
            "top_treatment": "laminate_worktop",
            "support_base": "legs_with_toe_board",
            "access_count": 1,
            "shelf_count": 1,
            "carcass_width_m": 0.48,
            "carcass_depth_m": 0.50,
            "carcass_height_m": 0.62,
            "drawer_travel_ratio": 0.62,
            "panel_t_m": 0.016,
            "worktop_t_m": 0.020,
            "plinth_leg_h_m": 0.080,
        },
        reason="shortest legs leave the thinnest toe board and the least clearance above the levelling feet",
    ),
    corner_case(
        "widest_stone_bullnose_over_shallow_plinth",
        {
            "cabinet_body": "base_cabinet",
            "access_module": "hinged_doors",
            "door_face": "reeded_slab",
            "top_treatment": "stone_slab_worktop",
            "support_base": "solid_plinth",
            "access_count": 3,
            "shelf_count": 2,
            "carcass_width_m": 0.78,
            "carcass_depth_m": 0.62,
            "carcass_height_m": 0.82,
            "door_swing_rad": 1.90,
            "shaker_frame_w_m": 0.075,
            "worktop_t_m": 0.050,
            "plinth_leg_h_m": 0.180,
            "plinth_setback_m": 0.030,
        },
        reason="thickest slab gives the deepest bullnose reach while three reeded leaves swing over the shallowest plinth setback",
    ),
    corner_case(
        "tallest_upstand_on_block_feet_lift_flap",
        {
            "cabinet_body": "plinth_deck_cabinet",
            "access_module": "lift_up_flap",
            "door_face": "shaker_panel",
            "top_treatment": "worktop_with_upstand",
            "support_base": "block_feet",
            "access_count": 1,
            "shelf_count": 1,
            "carcass_width_m": 0.48,
            "carcass_depth_m": 0.50,
            "carcass_height_m": 0.62,
            "lift_flap_rad": 1.55,
            "shaker_frame_w_m": 0.045,
            "worktop_t_m": 0.020,
            "plinth_leg_h_m": 0.080,
            "upstand_h_m": 0.120,
        },
        reason="tallest upstand on the thinnest slab while a full-height flap sweeps to maximum travel over the shortest block feet",
    ),
    corner_case(
        "shortest_upstand_deepest_plinth_drawers",
        {
            "cabinet_body": "plinth_deck_cabinet",
            "access_module": "drawer_stack",
            "door_face": "seamed_slab",
            "top_treatment": "worktop_with_upstand",
            "support_base": "solid_plinth",
            "access_count": 3,
            "shelf_count": 2,
            "carcass_width_m": 0.86,
            "carcass_depth_m": 0.62,
            "carcass_height_m": 0.82,
            "drawer_travel_ratio": 0.62,
            "worktop_t_m": 0.050,
            "plinth_leg_h_m": 0.180,
            "upstand_h_m": 0.040,
            "plinth_setback_m": 0.070,
        },
        reason="widest plinth-deck host at the deepest plinth setback and shortest upstand with the longest drawer stroke",
    ),
)


__all__ = [
    "TEMPLATE_CORNERS",
    "TEMPLATE_DOMAIN",
    "Config",
    "HandleType",
    "ResolvedConfig",
    "benchmark_metadata",
    "build_pictureX_0611_kitchen_cabinet",
    "build_seeded_pictureX_0611_kitchen_cabinet",
    "build_single_drawer_cabinet",
    "config_from_seed",
    "resolve_config",
    "run_pictureX_0611_kitchen_cabinet_tests",
    "run_single_drawer_cabinet_tests",
    "variable_space",
]
