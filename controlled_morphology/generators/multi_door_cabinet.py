# SPDX-License-Identifier: Apache-2.0

"""Controlled multi-door cabinet derived from pictureX/0611 Cabinet_with_doors.

One load-bearing carcass (rectilinear case, curved bow drum or tapered case) encloses a
storage cavity whose primary articulation is one or more door leaves (vertical butt hinge,
offset bypass tracks, or a folding bifold pair) over a shelf ladder, standing on legs, feet,
a plinth or a wall cleat.

Every host derives a planar front jamb -- the drum strikes a flat chord frame across its
opening arc, the tapered case sizes its opening from the narrow top width -- so any front
treatment and any mechanism mounts on a real supporting face and every declared slot
combination builds. Leaf width, height, hinge line, track planes and interior swing limits
are derived from the opening and from N; no combination is excluded and no overlap
allowance is emitted.

Coordinate convention (from origin 002): X = width, Y = depth with the FRONT at -Y,
Z = height, hinge axis +Z, leaves open outward toward -Y.

The copied template keeps the source generator's wider categorical surface for provenance.
The task-facing entry point accepts one to four side-hinged revolute leaves, exposes explicit
handle controls, and emits deterministic per-door benchmark metadata.
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
    LatheGeometry,
    LoftGeometry,
    MotionLimits,
    Origin,
    PlaneInterface,
    Sphere,
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

BodyForm = Literal["rect_box", "curved_bow_shell", "tapered_box"]
DoorKind = Literal[
    "framed_cane", "glazed_curtain", "fretwork_pierced", "raised_panel", "flush_slab"
]
DoorMechanism = Literal["revolute_swing", "sliding_bypass", "bifold"]
SupportBase = Literal[
    "metal_legs", "dowel_legs", "turned_feet", "feet_plinth", "recessed_plinth", "wall_mount"
]
InteriorFitment = Literal["plain_shelf", "edge_banded_shelf"]
HingeSide = Literal["left", "right"]
HandleType = Literal["bar", "knob"]

# The access face is the -Y side, matching the object coordinate convention.
__preview_front_axis__ = "-y"

TEMPLATE_DOMAIN = TemplateDomain(
    (
        component_slot("body_form", ("rect_box", "curved_bow_shell", "tapered_box")),
        component_slot(
            "door_kind",
            ("framed_cane", "glazed_curtain", "fretwork_pierced", "raised_panel", "flush_slab"),
        ),
        component_slot("door_mechanism", ("revolute_swing", "sliding_bypass", "bifold")),
        component_slot(
            "support_base",
            (
                "metal_legs",
                "dowel_legs",
                "turned_feet",
                "feet_plinth",
                "recessed_plinth",
                "wall_mount",
            ),
        ),
        component_slot("interior_fitment", ("plain_shelf", "edge_banded_shelf")),
        multiplicity_slot("door_count", (1, 2, 3, 4), item_slot="door_kind"),
        multiplicity_slot("shelf_count", (1, 2, 3), item_slot="interior_fitment"),
    )
)

# ---------------------------------------------------------------------------
# manufacturing constants (metres) shared by every accepted source record
# ---------------------------------------------------------------------------
_TOP_T = 0.030
_BASE_T = 0.028
_BACK_T = 0.018
_FRAME_W = 0.048
_FRAME_T = 0.022
_REVEAL = 0.007
_OUTER_REVEAL = 0.024
_ROW_REVEAL = 0.010
_BARREL_R = 0.008
_ROSETTE_T = 0.014
_LEAF_GAP = 0.002
_MAX_SWING = 1.92
_SHELF_FRONT_CLEAR = 0.020
_MIN_LEAF_W = 0.045
_MIN_LEAF_H = 0.100
_MIN_SHELF_GAP = 0.130
_TAPER_DEPTH_RATIO = 0.94

RGBA = tuple[float, float, float, float]
_PALETTES: tuple[dict[str, RGBA], ...] = (
    {  # dark walnut, origin 001/004
        "wood": (0.32, 0.19, 0.10, 1.0),
        "dark": (0.12, 0.07, 0.04, 1.0),
        "panel": (0.43, 0.27, 0.15, 1.0),
        "metal": (0.74, 0.76, 0.76, 1.0),
        "glass": (0.54, 0.66, 0.72, 0.35),
        "accent": (0.66, 0.45, 0.22, 1.0),
    },
    {  # pale maple with rattan, origin 002
        "wood": (0.86, 0.70, 0.42, 1.0),
        "dark": (0.55, 0.40, 0.22, 1.0),
        "panel": (0.79, 0.62, 0.36, 1.0),
        "metal": (0.72, 0.58, 0.31, 1.0),
        "glass": (0.60, 0.72, 0.78, 0.34),
        "accent": (0.66, 0.45, 0.22, 1.0),
    },
    {  # distressed ivory, origin 003
        "wood": (0.90, 0.87, 0.79, 1.0),
        "dark": (0.44, 0.40, 0.34, 1.0),
        "panel": (0.83, 0.79, 0.70, 1.0),
        "metal": (0.70, 0.60, 0.34, 1.0),
        "glass": (0.58, 0.68, 0.72, 0.33),
        "accent": (0.62, 0.52, 0.36, 1.0),
    },
    {  # warm oak, origin 005
        "wood": (0.58, 0.39, 0.20, 1.0),
        "dark": (0.23, 0.14, 0.08, 1.0),
        "panel": (0.72, 0.58, 0.38, 1.0),
        "metal": (0.62, 0.64, 0.66, 1.0),
        "glass": (0.58, 0.72, 0.82, 0.38),
        "accent": (0.50, 0.33, 0.16, 1.0),
    },
    {  # painted case with steel legs, var_wall_mounted
        "wood": (0.86, 0.84, 0.78, 1.0),
        "dark": (0.22, 0.23, 0.24, 1.0),
        "panel": (0.92, 0.90, 0.84, 1.0),
        "metal": (0.55, 0.56, 0.58, 1.0),
        "glass": (0.62, 0.78, 0.88, 0.35),
        "accent": (0.72, 0.18, 0.14, 1.0),
    },
)

_SUPPORT_HEIGHT_FIELD: dict[str, str] = {
    "metal_legs": "metal_leg_h_m",
    "dowel_legs": "dowel_leg_h_m",
    "turned_feet": "turned_foot_h_m",
    "feet_plinth": "plinth_h_m",
    "recessed_plinth": "toe_kick_h_m",
    "wall_mount": "mount_clearance_m",
}


# ---------------------------------------------------------------------------
# config
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Config:
    body_form: BodyForm = "rect_box"
    door_kind: DoorKind = "flush_slab"
    door_mechanism: DoorMechanism = "revolute_swing"
    support_base: SupportBase = "recessed_plinth"
    interior_fitment: InteriorFitment = "plain_shelf"
    door_count: int = 2
    shelf_count: int = 1
    hinge_side: HingeSide = "left"
    handle_type: HandleType = "bar"
    handle_orientation_rad: float = math.pi / 2.0
    handle_length_m: float = 0.130
    handle_thickness_m: float = 0.014
    handle_clearance_m: float = 0.035
    handle_hinge_distance_ratio: float = 0.86
    handle_vertical_position_ratio: float = 0.50
    carcass_width_m: float | None = None
    carcass_depth_m: float | None = None
    carcass_height_m: float | None = None
    rect_side_panel_t_m: float | None = None
    shell_wall_t_m: float | None = None
    front_opening_deg: float | None = None
    taper_top_ratio: float | None = None
    cane_frame_w_m: float | None = None
    curtain_pleat_depth_m: float | None = None
    fret_bar_w_m: float | None = None
    raise_bevel_m: float | None = None
    slab_t_m: float | None = None
    door_swing_rad: float | None = None
    slide_travel_m: float | None = None
    fold_swing_rad: float | None = None
    metal_leg_h_m: float | None = None
    dowel_leg_h_m: float | None = None
    turned_foot_h_m: float | None = None
    plinth_h_m: float | None = None
    toe_kick_h_m: float | None = None
    mount_clearance_m: float | None = None
    shelf_t_m: float | None = None
    edge_band_h_m: float | None = None
    palette: int = 0
    name: str = "multi_door_cabinet"


@dataclass(frozen=True)
class ResolvedConfig:
    body_form: BodyForm
    door_kind: DoorKind
    door_mechanism: DoorMechanism
    support_base: SupportBase
    interior_fitment: InteriorFitment
    door_count: int
    shelf_count: int
    hinge_side: HingeSide
    handle_type: HandleType
    palette: int
    name: str
    # independent, resolved
    carcass_width_m: float
    carcass_depth_m: float
    carcass_height_m: float
    rect_side_panel_t_m: float
    shell_wall_t_m: float
    front_opening_deg: float
    taper_top_ratio: float
    cane_frame_w_m: float
    curtain_pleat_depth_m: float
    fret_bar_w_m: float
    raise_bevel_m: float
    slab_t_m: float
    door_swing_rad: float
    slide_travel_m: float
    fold_swing_rad: float
    metal_leg_h_m: float
    dowel_leg_h_m: float
    turned_foot_h_m: float
    plinth_h_m: float
    toe_kick_h_m: float
    mount_clearance_m: float
    shelf_t_m: float
    edge_band_h_m: float
    handle_orientation_rad: float
    handle_length_m: float
    handle_thickness_m: float
    handle_clearance_m: float
    handle_hinge_distance_ratio: float
    handle_vertical_position_ratio: float
    # derived
    wall_t_m: float
    body_bottom_z_m: float
    body_top_z_m: float
    outer_radius_m: float
    inner_radius_m: float
    open_half_rad: float
    front_y_m: float
    opening_w_m: float
    opening_lo_z_m: float
    opening_hi_z_m: float
    clear_w_m: float
    clear_lo_z_m: float
    clear_hi_z_m: float
    leaf_t_m: float
    leaf_relief_m: float
    leaf_back_y_m: float
    hinge_y_m: float
    rows: tuple[tuple[float, float, int], ...]
    leaf_w_m: float
    leaf_h_m: float
    interior_swing_rad: float
    bypass_leaf_w_m: float
    bypass_travel_m: float
    cavity_lo_z_m: float
    cavity_hi_z_m: float
    shelf_span_m: float
    shelf_depth_m: float


def _base_variable_space() -> dict[str, object]:
    """Describe task-facing interventions and their deterministic descendants."""

    return {
        "schema_version": 1,
        "generator": "single_door_cabinet",
        "intervention_semantics": (
            "One explicit Config field changes per OAT cell. Geometry and kinematics derived "
            "deterministically from that field are expected to change and are recorded."
        ),
        "task_contract": {
            "movable_part_count": 1,
            "joint_type": "revolute",
            "hinge_axis": "+Z",
            "accepted_topology": {
                "door_mechanism": "revolute_swing",
                "door_count": 1,
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
                "nominal_range": [0.006, 0.040],
                "control": "direct_with_fit_constraint",
                "derived_effects": ["grip radius", "valid handle position interval"],
            },
            "handle_clearance_m": {
                "priority": "P0",
                "kind": "continuous",
                "unit": "m",
                "range": [0.010, 0.080],
                "control": "direct",
                "derived_effects": ["handle depth", "grasp frame"],
            },
            "handle_hinge_distance_ratio": {
                "priority": "P0",
                "kind": "continuous",
                "unit": "ratio",
                "nominal_range": [0.0, 1.0],
                "control": "direct_with_fit_constraint",
                "derived_effects": ["handle center", "absolute hinge distance"],
            },
            "handle_vertical_position_ratio": {
                "priority": "P0_auxiliary",
                "kind": "continuous",
                "unit": "ratio",
                "nominal_range": [0.0, 1.0],
                "control": "direct_with_fit_constraint",
                "derived_effects": ["handle center"],
            },
            "hinge_side": {
                "priority": "P0",
                "kind": "categorical",
                "values": ["left", "right"],
                "control": "direct",
                "derived_effects": [
                    "hinge position",
                    "leaf handedness",
                    "joint limits",
                    "opening sign",
                    "handle position",
                ],
            },
            "carcass_width_m": {
                "priority": "P0",
                "kind": "continuous",
                "unit": "m",
                "range_for_canonical_body": [0.66, 1.50],
                "control": "direct_upstream",
                "derived_effects": [
                    "opening width",
                    "door width",
                    "door aspect ratio",
                    "shelf width",
                    "sweep radius",
                    "absolute handle position",
                ],
            },
            "carcass_height_m": {
                "priority": "P0",
                "kind": "continuous",
                "unit": "m",
                "range_for_canonical_body": [0.92, 1.80],
                "control": "direct_upstream",
                "derived_effects": [
                    "opening height",
                    "door height",
                    "door aspect ratio",
                    "absolute handle position",
                ],
            },
            "slab_t_m": {
                "priority": "P0",
                "kind": "continuous",
                "unit": "m",
                "range": [0.016, 0.032],
                "control": "direct",
                "active_when": {"door_kind": "flush_slab"},
                "derived_effects": ["door thickness", "handle depth"],
            },
            "door_swing_rad": {
                "priority": "P1",
                "kind": "continuous",
                "unit": "rad",
                "range": [1.40, 1.92],
                "control": "direct",
                "derived_effects": ["signed joint limits", "opening endpoint"],
            },
        },
        "derived_measurements": [
            "morphology.carcass",
            "morphology.target_panel",
            "morphology.motion",
            "morphology.handle",
        ],
        "deferred_structural_slices": {
            "door_count": "family builder supports 1-4; task-facing entry is fixed to 1",
            "door_mechanism": (
                "family builder also has sliding_bypass and bifold; register separately"
            ),
            "horizontal_flap": "available from another family and should be a separate group",
            "appearance_and_dynamics": "deferred materialization stage",
        },
    }


def variable_space() -> dict[str, object]:
    """Describe the controlled revolute-door topology and handle variables."""

    space = _base_variable_space()
    variables = space["variables"]
    assert isinstance(variables, dict)
    variables["door_count"] = {
        "priority": "P1",
        "kind": "integer",
        "values": [1, 2, 3, 4],
        "control": "direct_topology",
        "derived_effects": [
            "movable part count",
            "revolute joint count",
            "row and cell layout",
            "door dimensions and aspect ratios",
            "positional hinge assignment",
            "joint limits and opening endpoints",
            "handle frames",
        ],
    }
    hinge_side = variables["hinge_side"]
    assert isinstance(hinge_side, dict)
    hinge_side.update(
        {
            "control": "direct_for_singleton_rows",
            "active_when": "a resolved row contains exactly one door",
            "multi_cell_rule": "hinge side is assigned deterministically by cell position",
        }
    )

    space.update(
        {
            "generator": "multi_door_cabinet",
            "entry_point": "build_multi_door_cabinet",
            "intervention_semantics": (
                "Set explicit Config fields; geometry, topology, kinematics, and handle frames "
                "are deterministic descendants of those fields."
            ),
            "task_contract": {
                "joint_type": "revolute",
                "hinge_axis": "+Z",
                "door_mechanism": "revolute_swing",
                "door_count": [1, 2, 3, 4],
                "movable_part_count": "equals resolved door_count",
            },
            "deterministic_layout": {
                "enumeration_order": "rows bottom-to-top, cells left-to-right",
                "single_row_rule": "one row containing door_count cells",
                "tiered_rule": (
                    "for door_count >= 3, split when two minimum-height tiers fit and either "
                    "door_count is 4 or a single-row cell is narrower than the mechanism minimum"
                ),
                "tiered_counts": "lower=floor(door_count/2), upper=ceil(door_count/2)",
                "canonical_rows_by_count": {
                    "1": [1],
                    "2": [2],
                    "3": [3],
                    "4": [2, 2],
                },
                "hinge_assignment": (
                    "a singleton row uses Config.hinge_side; in a multi-cell row, cells with "
                    "cell_index < doors_in_row/2 hinge left and the remainder hinge right"
                ),
                "interior_limit_rule": (
                    "a leaf with a neighbour on its hinge side uses interior_swing_rad; "
                    "outer leaves use door_swing_rad"
                ),
            },
            "primary_target_policy": "articulation index 0 in deterministic enumeration order",
            "unsupported_topologies": {
                "sliding_bypass": "preserved in the copied family builder but rejected here",
                "bifold": "preserved in the copied family builder but rejected here",
                "horizontal_flap": "belongs to a separate controlled generator family",
            },
            "out_of_scope": {
                "material": {
                    "priority": "P2",
                    "status": "out_of_scope",
                    "lifecycle": "permanent",
                },
                "color": {
                    "priority": "P2",
                    "status": "out_of_scope",
                    "lifecycle": "permanent",
                },
                "texture": {
                    "priority": "P2",
                    "status": "out_of_scope",
                    "lifecycle": "permanent",
                },
            },
        }
    )
    space.pop("deferred_structural_slices", None)
    return space


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value: float | None, default: float) -> float:
    return default if value is None else float(value)


def _finite_float(value: float, field_name: str) -> float:
    resolved = float(value)
    if not math.isfinite(resolved):
        raise ValueError(f"{field_name} must be finite, got {value!r}")
    return resolved


def _handle_radius(handle_type: HandleType, thickness: float) -> float:
    return thickness * 1.15 if handle_type == "knob" else thickness / 2.0


def _resolve_handle_controls(
    config: Config, leaf_w: float, leaf_h: float
) -> tuple[float, float, float, float, float, float]:
    """Resolve a handle capsule and clamp its frame to the door field."""

    orientation = _finite_float(config.handle_orientation_rad, "handle_orientation_rad") % math.pi
    requested_thickness = _finite_float(config.handle_thickness_m, "handle_thickness_m")
    max_thickness = max(0.006, min(0.040, min(leaf_w, leaf_h) * 0.35))
    thickness = _clamp(requested_thickness, 0.006, max_thickness)
    radius = _handle_radius(config.handle_type, thickness)

    abs_cos = abs(math.cos(orientation))
    abs_sin = abs(math.sin(orientation))
    length_caps = [0.320]
    if abs_cos > 1.0e-9:
        length_caps.append(max((leaf_w - 2.0 * abs_sin * radius) / abs_cos, 0.0))
    if abs_sin > 1.0e-9:
        length_caps.append(max((leaf_h - 2.0 * abs_cos * radius) / abs_sin, 0.0))
    max_length = max(min(length_caps), thickness)
    min_length = min(0.040, max_length)
    length = _clamp(
        _finite_float(config.handle_length_m, "handle_length_m"), min_length, max_length
    )

    if config.handle_type == "knob":
        half_x = radius
        half_z = radius
    else:
        half_x = abs_cos * length / 2.0 + abs_sin * radius
        half_z = abs_sin * length / 2.0 + abs_cos * radius

    hinge_to_free_edge = _leaf_setback_value() + leaf_w
    ratio_low = (_leaf_setback_value() + half_x) / hinge_to_free_edge
    ratio_high = (_leaf_setback_value() + leaf_w - half_x) / hinge_to_free_edge
    hinge_ratio = _clamp(
        _finite_float(config.handle_hinge_distance_ratio, "handle_hinge_distance_ratio"),
        ratio_low,
        ratio_high,
    )
    vertical_ratio = _clamp(
        _finite_float(config.handle_vertical_position_ratio, "handle_vertical_position_ratio"),
        half_z / leaf_h,
        1.0 - half_z / leaf_h,
    )
    clearance = _clamp(
        _finite_float(config.handle_clearance_m, "handle_clearance_m"), 0.010, 0.080
    )
    return orientation, length, thickness, clearance, hinge_ratio, vertical_ratio


def _config_from_seed(seed: int) -> Config:
    rng = random.Random(seed)
    body_form: BodyForm = rng.choice(("rect_box", "curved_bow_shell", "tapered_box"))
    door_kind: DoorKind = rng.choice(
        ("framed_cane", "glazed_curtain", "fretwork_pierced", "raised_panel", "flush_slab")
    )
    mechanism: DoorMechanism = rng.choice(("revolute_swing", "sliding_bypass", "bifold"))
    support: SupportBase = rng.choice(
        (
            "metal_legs",
            "dowel_legs",
            "turned_feet",
            "feet_plinth",
            "recessed_plinth",
            "wall_mount",
        )
    )
    fitment: InteriorFitment = rng.choice(("plain_shelf", "edge_banded_shelf"))
    if body_form == "curved_bow_shell":
        width = round(rng.uniform(0.62, 0.92), 3)
        depth = width
        height = round(rng.uniform(0.90, 1.40), 3)
    elif body_form == "tapered_box":
        width = round(rng.uniform(0.66, 1.36), 3)
        depth = round(rng.uniform(0.34, 0.50), 3)
        height = round(rng.uniform(0.92, 1.70), 3)
    else:
        width = round(rng.uniform(0.66, 1.50), 3)
        depth = round(rng.uniform(0.34, 0.50), 3)
        height = round(rng.uniform(0.92, 1.80), 3)
    hinge_side: HingeSide = rng.choice(("left", "right"))
    handle_type: HandleType = rng.choice(("bar", "knob"))
    return Config(
        body_form=body_form,
        door_kind=door_kind,
        door_mechanism=mechanism,
        support_base=support,
        interior_fitment=fitment,
        door_count=rng.choice((1, 2, 3, 4)),
        shelf_count=rng.choice((1, 2, 3)),
        hinge_side=hinge_side,
        handle_type=handle_type,
        handle_orientation_rad=rng.choice((0.0, math.pi / 6.0, math.pi / 3.0, math.pi / 2.0)),
        handle_length_m=round(rng.uniform(0.070, 0.220), 4),
        handle_thickness_m=round(rng.uniform(0.010, 0.024), 4),
        handle_clearance_m=round(rng.uniform(0.020, 0.060), 4),
        handle_hinge_distance_ratio=round(rng.uniform(0.62, 0.92), 4),
        handle_vertical_position_ratio=round(rng.uniform(0.25, 0.75), 4),
        carcass_width_m=width,
        carcass_depth_m=depth,
        carcass_height_m=height,
        rect_side_panel_t_m=round(rng.uniform(0.018, 0.032), 4),
        shell_wall_t_m=round(rng.uniform(0.022, 0.044), 4),
        front_opening_deg=round(rng.uniform(96.0, 148.0), 2),
        taper_top_ratio=round(rng.uniform(0.68, 0.92), 3),
        cane_frame_w_m=round(rng.uniform(0.036, 0.064), 4),
        curtain_pleat_depth_m=round(rng.uniform(0.006, 0.018), 4),
        fret_bar_w_m=round(rng.uniform(0.008, 0.020), 4),
        raise_bevel_m=round(rng.uniform(0.010, 0.024), 4),
        slab_t_m=round(rng.uniform(0.016, 0.032), 4),
        door_swing_rad=round(rng.uniform(1.40, 1.92), 3),
        slide_travel_m=round(rng.uniform(0.24, 0.46), 3),
        fold_swing_rad=round(rng.uniform(1.30, 1.75), 3),
        metal_leg_h_m=round(rng.uniform(0.22, 0.40), 3),
        dowel_leg_h_m=round(rng.uniform(0.22, 0.40), 3),
        turned_foot_h_m=round(rng.uniform(0.085, 0.180), 3),
        plinth_h_m=round(rng.uniform(0.100, 0.210), 3),
        toe_kick_h_m=round(rng.uniform(0.060, 0.150), 3),
        mount_clearance_m=round(rng.uniform(0.60, 1.25), 3),
        shelf_t_m=round(rng.uniform(0.014, 0.030), 4),
        edge_band_h_m=round(rng.uniform(0.018, 0.045), 4),
        palette=rng.randrange(len(_PALETTES)),
        name=f"pictureX_0611_Cabinet_with_doors_seed_{seed}",
    )


def _leaf_setback_value() -> float:
    """Radial clearance between the hinge line and the nearest leaf material."""

    return _BARREL_R + 0.004


def _swing_leaf_width(cell_w: float) -> float:
    """Leaf width that keeps the free edge inside its own cell at rest."""

    return max(
        cell_w - _OUTER_REVEAL - _leaf_setback_value() - _REVEAL,
        _MIN_LEAF_W,
    )


def _fold_knuckle_offset(leaf_t: float, relief: float) -> float:
    """Knuckle offset that keeps the folding leaf clear of the primary face."""

    setback = _leaf_setback_value()
    envelope = math.hypot(setback, leaf_t / 2.0 + relief)
    return envelope + 0.004


def _bifold_half_width(cell_w: float, leaf_t: float, relief: float) -> float:
    """Half-leaf width so primary + fold knuckle + folding leaf fit one cell."""

    usable = (
        cell_w
        - _OUTER_REVEAL
        - 2.0 * _leaf_setback_value()
        - _fold_knuckle_offset(leaf_t, relief)
        - _REVEAL
    )
    return usable / 2.0


def _leaf_front_relief(door_kind: str, leaf_t: float, raise_bevel: float, fret_bar: float) -> float:
    """How far the front treatment stands proud of the leaf face."""

    if door_kind == "raised_panel":
        return max(leaf_t * 0.36 + raise_bevel + _ROSETTE_T - leaf_t / 2.0, 0.0)
    if door_kind == "fretwork_pierced":
        return max(fret_bar / 2.0 - 0.002, 0.0)
    return 0.0


def _track_pitch(leaf_t: float, relief: float) -> float:
    """Bypass track spacing derived from the real leaf thickness and relief."""

    return leaf_t + relief + 0.010


def _row_layout(
    door_count: int, lo_z: float, hi_z: float, clear_w: float, min_cell_w: float
) -> tuple[tuple[float, float, int], ...]:
    """Row bands as (row_bottom_z, row_top_z, doors_in_row).

    Host capacity decides the split: a row is only kept if every cell in it is
    wide enough for its leaf, and a tiered layout is only taken if both tiers
    still clear the minimum leaf height.
    """

    height = hi_z - lo_z
    two_tier_fits = height >= 2.0 * _MIN_LEAF_H + _ROW_REVEAL
    single_row_fits = clear_w / max(door_count, 1) >= min_cell_w
    if door_count >= 3 and two_tier_fits and (door_count == 4 or not single_row_fits):
        upper = (door_count + 1) // 2
        lower = door_count - upper
        mid = (lo_z + hi_z) / 2.0
        return (
            (lo_z, mid - _ROW_REVEAL / 2.0, lower),
            (mid + _ROW_REVEAL / 2.0, hi_z, upper),
        )
    return ((lo_z, hi_z, door_count),)


def resolve_config(config: Config) -> ResolvedConfig:
    body_form = config.body_form
    door_kind = config.door_kind
    mechanism = config.door_mechanism
    support = config.support_base
    fitment = config.interior_fitment

    if config.hinge_side not in ("left", "right"):
        raise ValueError(f"hinge_side must be 'left' or 'right', got {config.hinge_side!r}")
    if config.handle_type not in ("bar", "knob"):
        raise ValueError(f"handle_type must be 'bar' or 'knob', got {config.handle_type!r}")

    door_count = int(_clamp(int(config.door_count), 1, 4))
    shelf_count = int(_clamp(int(config.shelf_count), 1, 3))

    rect_t = _clamp(_pick(config.rect_side_panel_t_m, 0.024), 0.018, 0.032)
    shell_t = _clamp(_pick(config.shell_wall_t_m, 0.030), 0.022, 0.044)
    open_deg = _clamp(_pick(config.front_opening_deg, 128.0), 96.0, 148.0)
    taper_ratio = _clamp(_pick(config.taper_top_ratio, 0.80), 0.68, 0.92)

    if body_form == "curved_bow_shell":
        width = _clamp(_pick(config.carcass_width_m, 0.78), 0.62, 0.92)
        depth = width
        height = _clamp(_pick(config.carcass_height_m, 1.12), 0.90, 1.40)
        wall_t = shell_t
    elif body_form == "tapered_box":
        width = _clamp(_pick(config.carcass_width_m, 0.98), 0.66, 1.36)
        depth = _clamp(_pick(config.carcass_depth_m, 0.42), 0.34, 0.50)
        height = _clamp(_pick(config.carcass_height_m, 1.24), 0.92, 1.70)
        wall_t = 0.024
    else:
        width = _clamp(_pick(config.carcass_width_m, 0.98), 0.66, 1.50)
        depth = _clamp(_pick(config.carcass_depth_m, 0.42), 0.34, 0.50)
        height = _clamp(_pick(config.carcass_height_m, 1.24), 0.92, 1.80)
        wall_t = rect_t

    support_value = _pick(getattr(config, _SUPPORT_HEIGHT_FIELD[support]), 0.30)
    support_bounds = {
        "metal_legs": (0.22, 0.40),
        "dowel_legs": (0.22, 0.40),
        "turned_feet": (0.085, 0.180),
        "feet_plinth": (0.100, 0.210),
        "recessed_plinth": (0.060, 0.150),
        "wall_mount": (0.60, 1.25),
    }[support]
    body_bottom_z = _clamp(support_value, *support_bounds)
    body_top_z = body_bottom_z + height

    # --- planar front jamb, derived per host -------------------------------
    outer_radius = width / 2.0
    inner_radius = outer_radius - wall_t
    open_half = math.radians(open_deg) / 2.0
    if body_form == "curved_bow_shell":
        front_y = -inner_radius * math.cos(open_half)
        opening_w = 2.0 * inner_radius * math.sin(open_half)
    elif body_form == "tapered_box":
        front_y = -depth / 2.0
        opening_w = taper_ratio * width - 2.0 * wall_t
    else:
        front_y = -depth / 2.0
        opening_w = width - 2.0 * wall_t
    opening_w = max(opening_w, 3.0 * _MIN_LEAF_W)

    opening_lo_z = body_bottom_z + _BASE_T + _REVEAL
    opening_hi_z = body_top_z - _TOP_T - _REVEAL
    clear_w = max(opening_w - 2.0 * _FRAME_W, 2.4 * _MIN_LEAF_W)
    clear_lo_z = opening_lo_z + _FRAME_W
    clear_hi_z = opening_hi_z - _FRAME_W

    leaf_t = _clamp(_pick(config.slab_t_m, 0.022), 0.016, 0.032)
    if door_kind != "flush_slab":
        leaf_t = 0.022
    leaf_relief = _leaf_front_relief(
        door_kind,
        leaf_t,
        _clamp(_pick(config.raise_bevel_m, 0.016), 0.010, 0.024),
        _clamp(_pick(config.fret_bar_w_m, 0.012), 0.008, 0.020),
    )
    leaf_back_y = front_y - _LEAF_GAP
    hinge_y = leaf_back_y - leaf_t / 2.0

    # --- row / cell layout --------------------------------------------------
    min_cell_w = 0.150 if mechanism == "bifold" else 0.090
    rows = _row_layout(door_count, clear_lo_z, clear_hi_z, clear_w, min_cell_w)
    per_row = max(row[2] for row in rows)
    cell_w = clear_w / per_row
    leaf_w = _swing_leaf_width(cell_w)
    if mechanism == "bifold":
        leaf_w = max(_bifold_half_width(cell_w, leaf_t, leaf_relief), 0.012)
    leaf_h = min(max(row_hi - row_lo, _MIN_LEAF_H) for row_lo, row_hi, _ in rows)

    door_swing = _clamp(_pick(config.door_swing_rad, 1.70), 1.40, _MAX_SWING)
    fold_swing = _clamp(_pick(config.fold_swing_rad, 1.55), 1.30, 1.75)
    interior_swing = min(door_swing, math.pi / 2.0 - 0.03)

    # a longer bypass stroke is bought with a narrower leaf: the reveal a leaf
    # can open is exactly the opening it does not cover
    slide_travel = _clamp(_pick(config.slide_travel_m, 0.34), 0.24, 0.46)
    if door_count == 1:
        bypass_leaf_w = _clamp(clear_w - slide_travel, clear_w * 0.35, clear_w * 0.90)
    else:
        bypass_leaf_w = _clamp(
            clear_w / door_count + 0.05 * (door_count - 1) / door_count - slide_travel * 0.25,
            max(_MIN_LEAF_W, clear_w * 0.15),
            clear_w * 0.60,
        )
    bypass_travel = max(min(slide_travel, clear_w - bypass_leaf_w - 0.010), 0.012)

    # --- cavity / shelves ---------------------------------------------------
    cavity_lo = body_bottom_z + _BASE_T
    cavity_hi = body_top_z - _TOP_T
    if body_form == "curved_bow_shell":
        shelf_span = 2.0 * inner_radius
        shelf_depth = 2.0 * inner_radius
    else:
        shelf_span = width - 2.0 * wall_t
        if body_form == "tapered_box":
            shelf_span = taper_ratio * width - 2.0 * wall_t + 0.010
        shelf_depth = depth - _BACK_T - _SHELF_FRONT_CLEAR
    shelf_t = _clamp(_pick(config.shelf_t_m, 0.020), 0.014, 0.030)
    edge_band_h = _clamp(_pick(config.edge_band_h_m, 0.030), 0.018, 0.045)
    (
        handle_orientation,
        handle_length,
        handle_thickness,
        handle_clearance,
        handle_hinge_ratio,
        handle_vertical_ratio,
    ) = _resolve_handle_controls(config, leaf_w, leaf_h)

    return ResolvedConfig(
        body_form=body_form,
        door_kind=door_kind,
        door_mechanism=mechanism,
        support_base=support,
        interior_fitment=fitment,
        door_count=door_count,
        shelf_count=shelf_count,
        hinge_side=config.hinge_side,
        handle_type=config.handle_type,
        palette=int(config.palette) % len(_PALETTES),
        name=config.name,
        carcass_width_m=width,
        carcass_depth_m=depth,
        carcass_height_m=height,
        rect_side_panel_t_m=rect_t,
        shell_wall_t_m=shell_t,
        front_opening_deg=open_deg,
        taper_top_ratio=taper_ratio,
        cane_frame_w_m=_clamp(_pick(config.cane_frame_w_m, 0.048), 0.036, 0.064),
        curtain_pleat_depth_m=_clamp(_pick(config.curtain_pleat_depth_m, 0.010), 0.006, 0.018),
        fret_bar_w_m=_clamp(_pick(config.fret_bar_w_m, 0.012), 0.008, 0.020),
        raise_bevel_m=_clamp(_pick(config.raise_bevel_m, 0.016), 0.010, 0.024),
        slab_t_m=_clamp(_pick(config.slab_t_m, 0.022), 0.016, 0.032),
        door_swing_rad=door_swing,
        slide_travel_m=_clamp(_pick(config.slide_travel_m, 0.34), 0.24, 0.46),
        fold_swing_rad=fold_swing,
        metal_leg_h_m=_clamp(_pick(config.metal_leg_h_m, 0.30), 0.22, 0.40),
        dowel_leg_h_m=_clamp(_pick(config.dowel_leg_h_m, 0.30), 0.22, 0.40),
        turned_foot_h_m=_clamp(_pick(config.turned_foot_h_m, 0.130), 0.085, 0.180),
        plinth_h_m=_clamp(_pick(config.plinth_h_m, 0.150), 0.100, 0.210),
        toe_kick_h_m=_clamp(_pick(config.toe_kick_h_m, 0.100), 0.060, 0.150),
        mount_clearance_m=_clamp(_pick(config.mount_clearance_m, 0.95), 0.60, 1.25),
        shelf_t_m=shelf_t,
        edge_band_h_m=edge_band_h,
        handle_orientation_rad=handle_orientation,
        handle_length_m=handle_length,
        handle_thickness_m=handle_thickness,
        handle_clearance_m=handle_clearance,
        handle_hinge_distance_ratio=handle_hinge_ratio,
        handle_vertical_position_ratio=handle_vertical_ratio,
        wall_t_m=wall_t,
        body_bottom_z_m=body_bottom_z,
        body_top_z_m=body_top_z,
        outer_radius_m=outer_radius,
        inner_radius_m=inner_radius,
        open_half_rad=open_half,
        front_y_m=front_y,
        opening_w_m=opening_w,
        opening_lo_z_m=opening_lo_z,
        opening_hi_z_m=opening_hi_z,
        clear_w_m=clear_w,
        clear_lo_z_m=clear_lo_z,
        clear_hi_z_m=clear_hi_z,
        leaf_t_m=leaf_t,
        leaf_relief_m=leaf_relief,
        leaf_back_y_m=leaf_back_y,
        hinge_y_m=hinge_y,
        rows=rows,
        leaf_w_m=leaf_w,
        leaf_h_m=leaf_h,
        interior_swing_rad=interior_swing,
        bypass_leaf_w_m=bypass_leaf_w,
        bypass_travel_m=bypass_travel,
        cavity_lo_z_m=cavity_lo,
        cavity_hi_z_m=cavity_hi,
        shelf_span_m=shelf_span,
        shelf_depth_m=shelf_depth,
    )


# ---------------------------------------------------------------------------
# small geometry helpers
# ---------------------------------------------------------------------------
def _bx(part, size, xyz, material, name, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(
        Box(size=(float(size[0]), float(size[1]), float(size[2]))),
        origin=Origin(xyz=(float(xyz[0]), float(xyz[1]), float(xyz[2])), rpy=rpy),
        material=material,
        name=name, material_class_id="wood.natural_generic",
    )


def _cy(part, radius, length, xyz, material, name, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(
        Cylinder(radius=float(radius), length=float(length)),
        origin=Origin(xyz=(float(xyz[0]), float(xyz[1]), float(xyz[2])), rpy=rpy),
        material=material,
        name=name, material_class_id="metal.generic_plain",
    )


def _materials(model: ArticulatedObject, palette: int) -> dict[str, object]:
    table = _PALETTES[palette % len(_PALETTES)]
    return {key: model.material(f"cabinet_{palette}_{key}", rgba=value) for key, value in table.items()}


def _axis_mate(*, provider_name, point, consumer_name, consumer_radius):
    provider = AxisInterface(
        name=provider_name,
        point=(float(point[0]), float(point[1]), float(point[2])),
        axis=(0.0, 0.0, 1.0),
        radial=(1.0, 0.0, 0.0),
        radius=_BARREL_R,
    )
    consumer = AxisInterface(
        name=consumer_name,
        point=(0.0, 0.0, 0.0),
        axis=(0.0, 0.0, 1.0),
        radial=(1.0, 0.0, 0.0),
        radius=consumer_radius,
    )
    return mate_axes(provider, consumer, require_fit=True)


def _plane_mate(*, provider_name, provider_point, provider_extent, consumer_name, consumer_extent):
    provider = PlaneInterface(
        name=provider_name,
        point=(float(provider_point[0]), float(provider_point[1]), float(provider_point[2])),
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


def _taper_half_width(r: ResolvedConfig, z: float) -> float:
    """Half width of the tapered carcass at world height z."""

    span = max(r.carcass_height_m, 1e-6)
    t = _clamp((z - r.body_bottom_z_m) / span, 0.0, 1.0)
    return (r.carcass_width_m / 2.0) * (1.0 - t * (1.0 - r.taper_top_ratio))


# ---------------------------------------------------------------------------
# body_form candidates
# ---------------------------------------------------------------------------
def _body_form_rect_box_build(carcass, r: ResolvedConfig, mats) -> None:
    tag = "body_form__rect_box"
    w, d, t = r.carcass_width_m, r.carcass_depth_m, r.wall_t_m
    zc = (r.body_bottom_z_m + r.body_top_z_m) / 2.0
    _bx(carcass, (t, d, r.carcass_height_m), (-w / 2 + t / 2, 0.0, zc), mats["wood"], f"{tag}__side_panel_0")
    _bx(carcass, (t, d, r.carcass_height_m), (w / 2 - t / 2, 0.0, zc), mats["wood"], f"{tag}__side_panel_1")
    _bx(carcass, (w + 0.030, d + 0.020, _TOP_T), (0.0, 0.0, r.body_top_z_m - _TOP_T / 2), mats["wood"], f"{tag}__top_slab")
    _bx(carcass, (w, d, _BASE_T), (0.0, 0.0, r.body_bottom_z_m + _BASE_T / 2), mats["wood"], f"{tag}__base_panel")
    _bx(
        carcass,
        (w - 2 * t + 0.006, _BACK_T, r.carcass_height_m - _TOP_T - _BASE_T + 0.008),
        (0.0, d / 2 - _BACK_T / 2, zc),
        mats["dark"],
        f"{tag}__back_panel",
    )


def _body_form_curved_bow_shell_build(carcass, r: ResolvedConfig, mats) -> None:
    tag = "body_form__curved_bow_shell"
    ro, ri = r.outer_radius_m, r.inner_radius_m
    a_lo = -math.pi / 2 + r.open_half_rad
    a_hi = -math.pi / 2 + 2 * math.pi - r.open_half_rad
    profile: list[tuple[float, float]] = []
    segments = 56
    for i in range(segments + 1):
        a = a_lo + (a_hi - a_lo) * i / segments
        profile.append((ro * math.cos(a), ro * math.sin(a)))
    for i in range(segments + 1):
        a = a_hi - (a_hi - a_lo) * i / segments
        profile.append((ri * math.cos(a), ri * math.sin(a)))
    shell = mesh_from_geometry(
        ExtrudeGeometry(profile, r.carcass_height_m, center=False), f"{tag}__shell_mesh"
    )
    carcass.visual(
        shell,
        origin=Origin(xyz=(0.0, 0.0, r.body_bottom_z_m)),
        material=mats["wood"],
        name=f"{tag}__curved_shell", material_class_id="wood.natural_generic",
    )
    _cy(carcass, ro, _TOP_T, (0.0, 0.0, r.body_top_z_m - _TOP_T / 2), mats["wood"], f"{tag}__top_disc")
    _cy(carcass, ro, _BASE_T, (0.0, 0.0, r.body_bottom_z_m + _BASE_T / 2), mats["wood"], f"{tag}__base_disc")


def _body_form_tapered_box_build(carcass, r: ResolvedConfig, mats) -> None:
    tag = "body_form__tapered_box"
    w, d, t = r.carcass_width_m, r.carcass_depth_m, r.wall_t_m
    w_top = w * r.taper_top_ratio
    d_top = d * _TAPER_DEPTH_RATIO
    z0, z1 = r.body_bottom_z_m, r.body_top_z_m

    def rect(cx: float, dx: float, dy: float, z: float):
        return [
            (cx - dx / 2, -dy / 2, z),
            (cx + dx / 2, -dy / 2, z),
            (cx + dx / 2, dy / 2, z),
            (cx - dx / 2, dy / 2, z),
        ]

    for sign, label in ((-1.0, "side_panel_0"), (1.0, "side_panel_1")):
        bx = sign * (w / 2 - t / 2)
        tx = sign * (w_top / 2 - t / 2)
        side = mesh_from_geometry(
            LoftGeometry([rect(bx, t, d, z0), rect(tx, t, d_top, z1)]), f"{tag}__{label}_mesh"
        )
        carcass.visual(side, material=mats["wood"], name=f"{tag}__{label}", material_class_id="wood.natural_generic")
    back = mesh_from_geometry(
        LoftGeometry(
            [
                rect(0.0, w - 2 * t + 0.006, _BACK_T, z0),
                rect(0.0, w_top - 2 * t + 0.006, _BACK_T, z1),
            ]
        ),
        f"{tag}__back_panel_mesh",
    )
    carcass.visual(
        back,
        origin=Origin(xyz=(0.0, d / 2 - _BACK_T / 2, 0.0)),
        material=mats["dark"],
        name=f"{tag}__back_panel", material_class_id="wood.engineered_board",
    )
    _bx(carcass, (w_top + 0.020, d_top + 0.020, _TOP_T), (0.0, 0.0, z1 - _TOP_T / 2), mats["wood"], f"{tag}__top_slab")
    _bx(carcass, (w, d, _BASE_T), (0.0, 0.0, z0 + _BASE_T / 2), mats["wood"], f"{tag}__base_panel")


_BODY_BUILDERS = {
    "rect_box": _body_form_rect_box_build,
    "curved_bow_shell": _body_form_curved_bow_shell_build,
    "tapered_box": _body_form_tapered_box_build,
}


def _build_front_frame(carcass, r: ResolvedConfig, mats) -> None:
    """Planar jamb every host derives: two stiles plus top and bottom rails."""

    tag = f"body_form__{r.body_form}"
    half = r.opening_w_m / 2.0
    fy = r.front_y_m + _FRAME_T / 2.0
    z0, z1 = r.opening_lo_z_m, r.opening_hi_z_m
    zc = (z0 + z1) / 2.0
    for sign, index in ((-1.0, 0), (1.0, 1)):
        # inner edge on the opening line, outer edge overlapping the host wall
        cx = sign * (half - _FRAME_W / 2 + 0.006)
        _bx(
            carcass,
            (_FRAME_W + 0.012, _FRAME_T, z1 - z0 + 0.012),
            (cx, fy, zc),
            mats["wood"],
            f"{tag}__jamb_stile_{index}",
        )
    rail_w = r.opening_w_m + 0.012
    _bx(carcass, (rail_w, _FRAME_T, _FRAME_W + 0.010), (0.0, fy, z1 - _FRAME_W / 2), mats["wood"], f"{tag}__head_rail")
    _bx(carcass, (rail_w, _FRAME_T, _FRAME_W + 0.010), (0.0, fy, z0 + _FRAME_W / 2), mats["wood"], f"{tag}__sill_rail")


# ---------------------------------------------------------------------------
# support_base candidates
# ---------------------------------------------------------------------------
def _leg_positions(r: ResolvedConfig, inset: float) -> list[tuple[float, float]]:
    if r.body_form == "curved_bow_shell":
        radius = max(r.outer_radius_m - inset, 0.06)
        return [
            (radius * math.cos(math.radians(45 + 90 * i)), radius * math.sin(math.radians(45 + 90 * i)))
            for i in range(4)
        ]
    lx = max(r.carcass_width_m / 2 - inset, 0.05)
    ly = max(r.carcass_depth_m / 2 - inset, 0.05)
    return [(-lx, -ly), (lx, -ly), (-lx, ly), (lx, ly)]


def _support_base_metal_legs_build(carcass, r: ResolvedConfig, mats) -> None:
    tag = "support_base__metal_legs"
    h = r.body_bottom_z_m
    for i, (x, y) in enumerate(_leg_positions(r, 0.090)):
        _cy(carcass, 0.014, h + 0.010, (x, y, (h + 0.010) / 2.0), mats["metal"], f"{tag}__leg_{i}")
        _cy(carcass, 0.022, 0.012, (x, y, 0.006), mats["dark"], f"{tag}__floor_glide_{i}")


def _support_base_dowel_legs_build(carcass, r: ResolvedConfig, mats) -> None:
    tag = "support_base__dowel_legs"
    h = r.body_bottom_z_m
    for i, (x, y) in enumerate(_leg_positions(r, 0.080)):
        _cy(carcass, 0.026, h + 0.010, (x, y, (h + 0.010) / 2.0), mats["wood"], f"{tag}__leg_{i}")
        _bx(carcass, (0.072, 0.062, 0.036), (x, y, h - 0.010), mats["dark"], f"{tag}__leg_socket_{i}")


def _support_base_turned_feet_build(carcass, r: ResolvedConfig, mats) -> None:
    tag = "support_base__turned_feet"
    h = r.body_bottom_z_m
    foot = mesh_from_geometry(
        LatheGeometry(
            [
                (0.0, 0.0),
                (0.034, 0.0),
                (0.028, h * 0.30),
                (0.019, h * 0.58),
                (0.030, h * 0.82),
                (0.022, h),
                (0.0, h),
            ],
            segments=22,
        ),
        f"{tag}__turned_foot_mesh",
    )
    for i, (x, y) in enumerate(_leg_positions(r, 0.070)):
        carcass.visual(
            foot, origin=Origin(xyz=(x, y, 0.0)), material=mats["wood"], name=f"{tag}__turned_foot_{i}", material_class_id="wood.natural_generic"
        )
    if r.body_form == "curved_bow_shell":
        _cy(carcass, r.outer_radius_m * 0.96, 0.022, (0.0, 0.0, h - 0.011), mats["dark"], f"{tag}__apron_band")
    else:
        _bx(
            carcass,
            (r.carcass_width_m * 0.98, r.carcass_depth_m * 0.98, 0.022),
            (0.0, 0.0, h - 0.011),
            mats["dark"],
            f"{tag}__apron_band",
        )


def _support_base_feet_plinth_build(carcass, r: ResolvedConfig, mats) -> None:
    tag = "support_base__feet_plinth"
    h = r.body_bottom_z_m
    for i, (x, y) in enumerate(_leg_positions(r, 0.060)):
        _bx(carcass, (0.078, 0.088, h), (x, y, h / 2.0), mats["dark"], f"{tag}__bracket_foot_{i}")
    if r.body_form == "curved_bow_shell":
        _cy(carcass, r.outer_radius_m * 0.92, h * 0.70, (0.0, 0.0, h * 0.35), mats["wood"], f"{tag}__plinth_core")
        _cy(carcass, r.outer_radius_m * 0.97, 0.024, (0.0, 0.0, h - 0.012), mats["dark"], f"{tag}__plinth_moulding")
    else:
        _bx(
            carcass,
            (r.carcass_width_m * 0.92, r.carcass_depth_m * 0.92, h * 0.70),
            (0.0, 0.0, h * 0.35),
            mats["wood"],
            f"{tag}__plinth_core",
        )
        _bx(
            carcass,
            (r.carcass_width_m * 0.97, r.carcass_depth_m * 0.97, 0.024),
            (0.0, 0.0, h - 0.012),
            mats["dark"],
            f"{tag}__plinth_moulding",
        )


def _support_base_recessed_plinth_build(carcass, r: ResolvedConfig, mats) -> None:
    tag = "support_base__recessed_plinth"
    h = r.body_bottom_z_m
    if r.body_form == "curved_bow_shell":
        _cy(carcass, max(r.outer_radius_m - 0.035, 0.08), h + 0.006, (0.0, 0.0, (h + 0.006) / 2.0), mats["dark"], f"{tag}__toe_kick_box")
    else:
        _bx(
            carcass,
            (r.carcass_width_m - 0.060, r.carcass_depth_m - 0.050, h + 0.006),
            (0.0, 0.025, (h + 0.006) / 2.0),
            mats["dark"],
            f"{tag}__toe_kick_box",
        )


def _support_base_wall_mount_build(carcass, r: ResolvedConfig, mats) -> None:
    tag = "support_base__wall_mount"
    if r.body_form == "curved_bow_shell":
        # the cleat is let into the drum wall at the back of the shell
        rail_cy = r.outer_radius_m - 0.018
        rail_w = r.outer_radius_m
    else:
        rail_cy = r.carcass_depth_m / 2.0 - _BACK_T + 0.010
        rail_w = r.carcass_width_m * 0.86
    for i, frac in enumerate((0.78, 0.22)):
        z = r.body_bottom_z_m + r.carcass_height_m * frac
        _bx(carcass, (rail_w, 0.030, 0.052), (0.0, rail_cy, z), mats["metal"], f"{tag}__hanging_rail_{i}")
        for j, sign in enumerate((-1.0, 1.0)):
            _bx(
                carcass,
                (0.052, 0.026, 0.090),
                (sign * rail_w * 0.42, rail_cy, z),
                mats["metal"],
                f"{tag}__mount_plate_{i}_{j}",
            )


_SUPPORT_BUILDERS = {
    "metal_legs": _support_base_metal_legs_build,
    "dowel_legs": _support_base_dowel_legs_build,
    "turned_feet": _support_base_turned_feet_build,
    "feet_plinth": _support_base_feet_plinth_build,
    "recessed_plinth": _support_base_recessed_plinth_build,
    "wall_mount": _support_base_wall_mount_build,
}


# ---------------------------------------------------------------------------
# interior_fitment candidates (fused carcass geometry seated on the cavity)
# ---------------------------------------------------------------------------
def _shelf_levels(r: ResolvedConfig) -> list[float]:
    lo = r.cavity_lo_z_m + _MIN_SHELF_GAP * 0.4
    hi = r.cavity_hi_z_m - _MIN_SHELF_GAP * 0.4
    if hi <= lo:
        lo, hi = r.cavity_lo_z_m, r.cavity_hi_z_m
    return [lo + (i + 1) * (hi - lo) / (r.shelf_count + 1) for i in range(r.shelf_count)]


def _shelf_disc_profile(r: ResolvedConfig, radius: float) -> list[tuple[float, float]]:
    """Circular shelf clipped behind the chord jamb so it never enters the door zone."""

    clip_y = r.front_y_m + _SHELF_FRONT_CLEAR
    points: list[tuple[float, float]] = []
    for i in range(49):
        a = -math.pi / 2 + 2 * math.pi * i / 48
        x, y = radius * math.cos(a), radius * math.sin(a)
        points.append((x, max(y, clip_y)))
    return points


def _shelf_slab(carcass, r: ResolvedConfig, mats, index: float, z: float, thickness: float, tag: str) -> None:
    if r.body_form == "curved_bow_shell":
        disc = mesh_from_geometry(
            ExtrudeGeometry(_shelf_disc_profile(r, r.inner_radius_m + 0.005), thickness, center=True),
            f"{tag}__shelf_mesh_{index}",
        )
        carcass.visual(
            disc, origin=Origin(xyz=(0.0, 0.0, z)), material=mats["dark"], name=f"{tag}__shelf_{index}", material_class_id="wood.engineered_board"
        )
        return
    if r.body_form == "tapered_box":
        span = 2.0 * _taper_half_width(r, z) - 2.0 * r.wall_t_m + 0.008
    else:
        span = r.shelf_span_m + 0.008
    y_front = r.front_y_m + _SHELF_FRONT_CLEAR
    y_back = r.carcass_depth_m / 2 - _BACK_T + 0.006
    _bx(
        carcass,
        (max(span, 0.10), max(y_back - y_front, 0.06), thickness),
        (0.0, (y_front + y_back) / 2.0, z),
        mats["dark"],
        f"{tag}__shelf_{index}",
    )


def _interior_fitment_plain_shelf_build(carcass, r: ResolvedConfig, mats) -> None:
    tag = "interior_fitment__plain_shelf"
    for index, z in enumerate(_shelf_levels(r)):
        _shelf_slab(carcass, r, mats, index, z, r.shelf_t_m, tag)


def _interior_fitment_edge_banded_shelf_build(carcass, r: ResolvedConfig, mats) -> None:
    tag = "interior_fitment__edge_banded_shelf"
    band_t = 0.014
    for index, z in enumerate(_shelf_levels(r)):
        _shelf_slab(carcass, r, mats, index, z, r.shelf_t_m * 0.8, tag)
        band_h = r.edge_band_h_m
        band_z = z - band_h / 2 + r.shelf_t_m * 0.4
        if r.body_form == "curved_bow_shell":
            band_w = 2.0 * r.inner_radius_m * math.sin(r.open_half_rad) * 0.98
        elif r.body_form == "tapered_box":
            band_w = 2.0 * _taper_half_width(r, z) - 2.0 * r.wall_t_m
        else:
            band_w = r.shelf_span_m
        _bx(
            carcass,
            (max(band_w, 0.10), band_t, band_h),
            (0.0, r.front_y_m + _SHELF_FRONT_CLEAR + band_t / 2 - 0.004, band_z),
            mats["accent"],
            f"{tag}__shelf_edge_{index}",
        )


_FITMENT_BUILDERS = {
    "plain_shelf": _interior_fitment_plain_shelf_build,
    "edge_banded_shelf": _interior_fitment_edge_banded_shelf_build,
}


# ---------------------------------------------------------------------------
# door_kind candidates -- front treatments authored in leaf-local frame
#
# Leaf-local frame: hinge/track axis at the origin, the leaf extends
# +sign * x from `setback`, the leaf back face sits at local y = +leaf_t/2 and
# the front face at local y = -leaf_t/2 (the whole leaf is forward of the jamb).
# ---------------------------------------------------------------------------
def _leaf_setback(r: ResolvedConfig) -> float:
    del r
    return _leaf_setback_value()


def _leaf_field(r: ResolvedConfig, sign: float, leaf_w: float) -> float:
    """Centre x of the leaf field in leaf-local coordinates."""

    return sign * (_leaf_setback(r) + leaf_w / 2.0)


def _frame_scale(leaf_w: float, leaf_h: float) -> float:
    """Shrink a stile/rail set proportionally on a narrow or short leaf."""

    return min(1.0, leaf_w / 0.220, leaf_h / 0.300)


def _door_frame_members(leaf, r, mats, sign, leaf_w, leaf_h, tag, frame_w) -> tuple[float, float, float]:
    s = _leaf_setback(r)
    t = r.leaf_t_m
    outer_x = sign * (s + frame_w / 2)
    inner_x = sign * (s + leaf_w - frame_w / 2)
    cx = _leaf_field(r, sign, leaf_w)
    _bx(leaf, (frame_w, t, leaf_h), (outer_x, 0.0, 0.0), mats["wood"], f"{tag}__outer_stile")
    _bx(leaf, (frame_w, t, leaf_h), (inner_x, 0.0, 0.0), mats["wood"], f"{tag}__inner_stile")
    rail_z = leaf_h / 2 - frame_w / 2
    field_w = max(leaf_w - 2 * frame_w, leaf_w * 0.20)
    _bx(leaf, (field_w, t, frame_w), (cx, 0.0, rail_z), mats["wood"], f"{tag}__top_rail")
    _bx(leaf, (field_w, t, frame_w), (cx, 0.0, -rail_z), mats["wood"], f"{tag}__bottom_rail")
    return cx, field_w, max(leaf_h - 2 * frame_w, leaf_h * 0.20)


def _handle_layout(
    r: ResolvedConfig, sign: float, leaf_w: float, leaf_h: float
) -> dict[str, object]:
    """Return the resolved grasp frame in leaf-local coordinates."""

    radius = _handle_radius(r.handle_type, r.handle_thickness_m)
    center_x = sign * r.handle_hinge_distance_ratio * (_leaf_setback(r) + leaf_w)
    center_z = (r.handle_vertical_position_ratio - 0.5) * leaf_h
    mount_face_y = -r.leaf_t_m / 2.0 - r.leaf_relief_m
    center_y = mount_face_y - r.handle_clearance_m - radius
    orientation = r.handle_orientation_rad
    grip_axis = (math.cos(orientation), 0.0, math.sin(orientation))
    return {
        "xyz": (center_x, center_y, center_z),
        "rpy": (0.0, math.pi / 2.0 - orientation, 0.0),
        "approach_axis": (0.0, -1.0, 0.0),
        "grip_axis": grip_axis,
        "mount_face_y": mount_face_y,
    }


def _door_pull(leaf, r, mats, sign, leaf_w, leaf_h, tag, style: str) -> None:
    if str(getattr(leaf, "meta", {}).get("role") or "") == "fold_leaf":
        # only the leading leaf of a bifold pair carries a pull
        return
    if r.door_mechanism == "sliding_bypass":
        # bypass leaves pass each other on adjacent tracks, so the source-style
        # protruding pull becomes a recessed finger pull inside the leaf face
        depth = min(0.008, r.leaf_t_m * 0.4)
        hx = sign * (_leaf_setback(r) + leaf_w - 0.030)
        _bx(
            leaf,
            (0.028, depth, min(0.150, leaf_h * 0.45)),
            (hx, -r.leaf_t_m / 2 + depth / 2, 0.0),
            mats["dark"],
            f"{tag}__flush_pull",
        )
        return

    del style
    layout = _handle_layout(r, sign, leaf_w, leaf_h)
    center = layout["xyz"]
    assert isinstance(center, tuple)
    hx, hy, hz = center
    radius = _handle_radius(r.handle_type, r.handle_thickness_m)
    mount_face_y = float(layout["mount_face_y"])
    post_length = mount_face_y - hy
    post_y = mount_face_y - post_length / 2.0
    post_radius = min(max(r.handle_thickness_m * 0.50, 0.0025), radius)

    leaf.meta["handle_frame"] = {
        "xyz": [float(v) for v in center],
        "rpy": [float(v) for v in layout["rpy"]],
        "approach_axis": [float(v) for v in layout["approach_axis"]],
        "grip_axis": [float(v) for v in layout["grip_axis"]],
    }
    if r.handle_type == "knob":
        _cy(
            leaf,
            post_radius,
            post_length,
            (hx, post_y, hz),
            mats["metal"],
            f"{tag}__handle_post",
            rpy=(math.pi / 2.0, 0.0, 0.0),
        )
        leaf.visual(
            Sphere(radius=radius),
            origin=Origin(xyz=(hx, hy, hz), rpy=layout["rpy"]),
            material=mats["metal"],
            name=f"{tag}__handle_knob",
            material_class_id="metal.generic_plain",
        )
        return

    grip_axis = layout["grip_axis"]
    assert isinstance(grip_axis, tuple)
    _cy(
        leaf,
        radius,
        r.handle_length_m,
        center,
        mats["metal"],
        f"{tag}__handle_grip",
        rpy=layout["rpy"],
    )
    post_offset = max(r.handle_length_m / 2.0 - 1.25 * radius, 0.0)
    for index, endpoint_sign in enumerate((-1.0, 1.0)):
        px = hx + endpoint_sign * post_offset * grip_axis[0]
        pz = hz + endpoint_sign * post_offset * grip_axis[2]
        _cy(
            leaf,
            post_radius,
            post_length,
            (px, post_y, pz),
            mats["metal"],
            f"{tag}__handle_post_{index}",
            rpy=(math.pi / 2.0, 0.0, 0.0),
        )


def _door_kind_framed_cane_build(leaf, r, mats, sign, leaf_w, leaf_h, tag) -> None:
    frame_w = r.cane_frame_w_m * _frame_scale(leaf_w, leaf_h)
    cx, fw, fh = _door_frame_members(leaf, r, mats, sign, leaf_w, leaf_h, tag, frame_w)
    _bx(leaf, (fw + 0.008, 0.007, fh + 0.008), (cx, 0.0, 0.0), mats["accent"], f"{tag}__cane_panel")
    yf = -r.leaf_t_m / 2 + 0.004
    for j in range(3):
        _bx(leaf, (0.006, 0.007, fh), (cx + (j - 1) * fw / 3.0, yf, 0.0), mats["dark"], f"{tag}__cane_warp_{j}")
    for j in range(4):
        _bx(leaf, (fw, 0.007, 0.006), (cx, yf, (j - 1.5) * fh / 4.0), mats["dark"], f"{tag}__cane_weft_{j}")
    _door_pull(leaf, r, mats, sign, leaf_w, leaf_h, tag, "pull")


def _door_kind_glazed_curtain_build(leaf, r, mats, sign, leaf_w, leaf_h, tag) -> None:
    frame_w = 0.046 * _frame_scale(leaf_w, leaf_h)
    cx, fw, fh = _door_frame_members(leaf, r, mats, sign, leaf_w, leaf_h, tag, frame_w)
    depth = r.curtain_pleat_depth_m
    _bx(leaf, (fw + 0.006, 0.006, fh + 0.006), (cx, -r.leaf_t_m / 2 + 0.005, 0.0), mats["glass"], f"{tag}__glass_panel")
    _bx(leaf, (fw * 0.97, 0.006, fh * 0.97), (cx, -r.leaf_t_m / 2 + 0.010, 0.0), mats["accent"], f"{tag}__curtain_backing")
    for j in range(6):
        _bx(
            leaf,
            (max(fw / 11.0, 0.006), depth, fh * 0.94),
            (cx + (j - 2.5) * fw / 6.0, -r.leaf_t_m / 2 + 0.010 + depth / 2 - 0.003, 0.0),
            mats["accent"],
            f"{tag}__curtain_fold_{j}",
        )
    _door_pull(leaf, r, mats, sign, leaf_w, leaf_h, tag, "drop")


def _door_kind_fretwork_pierced_build(leaf, r, mats, sign, leaf_w, leaf_h, tag) -> None:
    frame_w = 0.050 * _frame_scale(leaf_w, leaf_h)
    cx, fw, fh = _door_frame_members(leaf, r, mats, sign, leaf_w, leaf_h, tag, frame_w)
    bar = r.fret_bar_w_m
    _bx(leaf, (fw + 0.006, 0.006, fh + 0.006), (cx, r.leaf_t_m / 2 - 0.004, 0.0), mats["dark"], f"{tag}__fret_backing")
    yf = -r.leaf_t_m / 2 + bar / 2 - 0.002
    for j in range(4):
        _bx(leaf, (bar, bar, fh), (cx + (j - 1.5) * fw / 4.0, yf, 0.0), mats["wood"], f"{tag}__fret_bar_{j}")
    for j in range(3):
        _bx(leaf, (fw, bar, bar), (cx, yf, (j - 1.0) * fh / 3.0), mats["wood"], f"{tag}__fret_rail_{j}")
    _door_pull(leaf, r, mats, sign, leaf_w, leaf_h, tag, "drop")


def _door_kind_raised_panel_build(leaf, r, mats, sign, leaf_w, leaf_h, tag) -> None:
    s = _leaf_setback(r)
    t = r.leaf_t_m
    cx = _leaf_field(r, sign, leaf_w)
    _bx(leaf, (leaf_w, t * 0.72, leaf_h), (cx, 0.0, 0.0), mats["panel"], f"{tag}__panel_slab")
    fw = max(leaf_w - 0.090, leaf_w * 0.40)
    fh = max(leaf_h - 0.090, leaf_h * 0.40)
    bevel = r.raise_bevel_m
    yf = -t * 0.36 - bevel / 2 + 0.002
    for label, (dx, dz, sx, sz) in {
        "raise_top": (0.0, fh / 2, fw, 0.018),
        "raise_bottom": (0.0, -fh / 2, fw, 0.018),
        "raise_left": (-fw / 2, 0.0, 0.018, fh),
        "raise_right": (fw / 2, 0.0, 0.018, fh),
    }.items():
        _bx(leaf, (sx, bevel, sz), (cx + dx, yf, dz), mats["wood"], f"{tag}__{label}")
    _cy(
        leaf,
        min(0.050, max(fw, 0.06) * 0.18),
        _ROSETTE_T,
        # the carved rosette is let into the raised field, not floated in front of it
        (cx, -t * 0.36 - _ROSETTE_T / 2 + 0.004, 0.0),
        mats["accent"],
        f"{tag}__medallion",
        rpy=(math.pi / 2, 0.0, 0.0),
    )
    _door_pull(leaf, r, mats, sign, leaf_w, leaf_h, tag, "knob")
    del s


def _door_kind_flush_slab_build(leaf, r, mats, sign, leaf_w, leaf_h, tag) -> None:
    cx = _leaf_field(r, sign, leaf_w)
    _bx(leaf, (leaf_w, r.leaf_t_m, leaf_h), (cx, 0.0, 0.0), mats["panel"], f"{tag}__door_slab")
    _door_pull(leaf, r, mats, sign, leaf_w, leaf_h, tag, "pull")


_DOOR_KIND_BUILDERS = {
    "framed_cane": _door_kind_framed_cane_build,
    "glazed_curtain": _door_kind_glazed_curtain_build,
    "fretwork_pierced": _door_kind_fretwork_pierced_build,
    "raised_panel": _door_kind_raised_panel_build,
    "flush_slab": _door_kind_flush_slab_build,
}


def _new_leaf(model, r: ResolvedConfig, index: int, role: str, mechanism: str):
    return model.part(
        f"door_kind__{r.door_kind}__{role}_{index}",
        meta={
            "role": role,
            "slot": "door_kind",
            "candidate": r.door_kind,
            "index": index,
            "mechanism": mechanism,
        },
    )


def _build_leaf_body(leaf, r: ResolvedConfig, mats, sign: float, leaf_w: float, leaf_h: float) -> None:
    tag = f"door_kind__{r.door_kind}"
    _DOOR_KIND_BUILDERS[r.door_kind](leaf, r, mats, sign, leaf_w, leaf_h, tag)


def _hinge_strap(leaf, r: ResolvedConfig, mats, sign: float, station_z: float, name: str) -> None:
    """Strap that ties a leaf barrel into the leaf field."""

    reach = _leaf_setback_value() + 0.006
    _bx(
        leaf,
        (reach, min(r.leaf_t_m, 0.014), 0.016),
        (sign * reach / 2.0, 0.0, station_z),
        mats["metal"],
        name,
    )


def _hinge_mullion(carcass, r: ResolvedConfig, mats, hinge_x: float, tag: str, index: str) -> None:
    """Face-frame member at a hinge line, tying the sill rail to the head rail."""

    z0, z1 = r.opening_lo_z_m, r.opening_hi_z_m
    _bx(
        carcass,
        (_FRAME_W, _FRAME_T, z1 - z0),
        (hinge_x, r.front_y_m + _FRAME_T / 2.0, (z0 + z1) / 2.0),
        mats["wood"],
        f"{tag}__hinge_mullion_{index}",
    )


def _hinge_hardware(
    carcass,
    leaf,
    r: ResolvedConfig,
    mats,
    hinge_x: float,
    zc: float,
    leaf_h: float,
    sign: float,
    tag: str,
    index: str,
) -> None:
    """Carcass knuckles and leaf barrels interleaved along the hinge line."""

    _hinge_mullion(carcass, r, mats, hinge_x, tag, index)
    stations = (-leaf_h * 0.34, leaf_h * 0.34)
    for station_index, station in enumerate(stations):
        _cy(
            carcass,
            _BARREL_R,
            0.030,
            (hinge_x, r.hinge_y_m, zc + station),
            mats["metal"],
            f"{tag}__fixed_knuckle_{index}_{station_index}",
        )
        # bracket back to the jamb frame face, clear of the leaf sweep cylinder
        _bx(
            carcass,
            (0.018, max(r.front_y_m + _FRAME_T - r.hinge_y_m, 0.010), 0.020),
            (hinge_x, (r.hinge_y_m + r.front_y_m + _FRAME_T) / 2.0, zc + station),
            mats["metal"],
            f"{tag}__knuckle_plate_{index}_{station_index}",
        )
        for barrel_index, offset in enumerate((-0.022, 0.022)):
            _cy(
                leaf,
                _BARREL_R * 0.86,
                0.022,
                (0.0, 0.0, station + offset),
                mats["metal"],
                f"{tag}__barrel_{index}_{station_index}_{barrel_index}",
            )
            _hinge_strap(
                leaf,
                r,
                mats,
                sign,
                station + offset,
                f"{tag}__hinge_strap_{index}_{station_index}_{barrel_index}",
            )


# ---------------------------------------------------------------------------
# door_mechanism candidates
# ---------------------------------------------------------------------------
def _cell_geometry(r: ResolvedConfig):
    """Yield (index, row_index, cell_index, per_row, cell_left, row_lo, row_hi)."""

    index = 0
    for row_index, (row_lo, row_hi, per_row) in enumerate(r.rows):
        cell_w = r.clear_w_m / per_row
        for cell_index in range(per_row):
            cell_left = -r.clear_w_m / 2 + cell_index * cell_w
            yield index, row_index, cell_index, per_row, cell_left, cell_w, row_lo, row_hi
            index += 1


@dataclass(frozen=True)
class _RevoluteLeafLayout:
    index: int
    row_index: int
    cell_index: int
    doors_in_row: int
    leaf_width_m: float
    leaf_height_m: float
    hinge_x_m: float
    hinge_z_m: float
    hinge_left: bool
    has_neighbour: bool
    limit_rad: float

    @property
    def sign(self) -> float:
        return 1.0 if self.hinge_left else -1.0

    @property
    def hinge_side(self) -> str:
        return "left" if self.hinge_left else "right"

    @property
    def limits(self) -> tuple[float, float]:
        return (-self.limit_rad, 0.0) if self.hinge_left else (0.0, self.limit_rad)

    @property
    def opening_sign(self) -> float:
        return -1.0 if self.hinge_left else 1.0

    @property
    def opening_endpoint(self) -> float:
        return self.opening_sign * self.limit_rad


def _revolute_leaf_layouts(r: ResolvedConfig) -> tuple[_RevoluteLeafLayout, ...]:
    layouts: list[_RevoluteLeafLayout] = []
    for (
        index,
        row_index,
        cell_index,
        per_row,
        cell_left,
        cell_w,
        row_lo,
        row_hi,
    ) in _cell_geometry(r):
        leaf_h = max(row_hi - row_lo, _MIN_LEAF_H)
        hinge_left = (
            r.hinge_side == "left" if per_row == 1 else cell_index < per_row / 2.0
        )
        hinge_x = (
            cell_left + _OUTER_REVEAL if hinge_left else cell_left + cell_w - _OUTER_REVEAL
        )
        has_neighbour = (cell_index > 0) if hinge_left else (cell_index < per_row - 1)
        layouts.append(
            _RevoluteLeafLayout(
                index=index,
                row_index=row_index,
                cell_index=cell_index,
                doors_in_row=per_row,
                leaf_width_m=_swing_leaf_width(cell_w),
                leaf_height_m=leaf_h,
                hinge_x_m=hinge_x,
                hinge_z_m=(row_lo + row_hi) / 2.0,
                hinge_left=hinge_left,
                has_neighbour=has_neighbour,
                limit_rad=r.interior_swing_rad if has_neighbour else r.door_swing_rad,
            )
        )
    return tuple(layouts)


def _door_mechanism_revolute_swing_build(model, carcass, r: ResolvedConfig, mats) -> list[object]:
    tag = "door_mechanism__revolute_swing"
    leaves: list[object] = []
    for layout in _revolute_leaf_layouts(r):
        leaf = _new_leaf(model, r, layout.index, "door_leaf", "vertical butt hinge")
        leaf.meta["hinge_side"] = layout.hinge_side
        _build_leaf_body(
            leaf, r, mats, layout.sign, layout.leaf_width_m, layout.leaf_height_m
        )
        _hinge_hardware(
            carcass,
            leaf,
            r,
            mats,
            layout.hinge_x_m,
            layout.hinge_z_m,
            layout.leaf_height_m,
            layout.sign,
            tag,
            str(layout.index),
        )
        mate = _axis_mate(
            provider_name=f"body_form.front_opening.hinge_{layout.index}",
            point=(layout.hinge_x_m, r.hinge_y_m, layout.hinge_z_m),
            consumer_name=f"door_mechanism.hinge_line_{layout.index}",
            consumer_radius=_BARREL_R * 0.86,
        )
        joint = f"{tag}__leaf_joint_{layout.index}"
        lower, upper = layout.limits
        model.articulation(
            joint,
            ArticulationType.REVOLUTE,
            parent=carcass,
            child=leaf,
            origin=mate.origin,
            axis=mate.axis,
            motion_limits=MotionLimits(effort=12.0, velocity=1.4, lower=lower, upper=upper),
            meta={
                "opening_direction": "outward toward -Y",
                "opening_sign": layout.opening_sign,
                "opening_endpoint": layout.opening_endpoint,
                "hinge_side": layout.hinge_side,
            },
        )
        register_interface_mate(model, joint, mate)
        leaves.append(leaf)
    return leaves


def _door_mechanism_sliding_bypass_build(model, carcass, r: ResolvedConfig, mats) -> list[object]:
    tag = "door_mechanism__sliding_bypass"
    leaves: list[object] = []
    n = r.door_count
    leaf_w = r.bypass_leaf_w_m
    row_lo, row_hi = r.clear_lo_z_m, r.clear_hi_z_m
    leaf_h = max(row_hi - row_lo - 0.030, _MIN_LEAF_H)
    zc = (row_lo + row_hi) / 2.0
    travel = r.bypass_travel_m
    for index in range(n):
        plane_y = r.front_y_m - _LEAF_GAP - index * _track_pitch(r.leaf_t_m, r.leaf_relief_m)
        # rest positions tile the opening left to right
        if n == 1:
            rest_cx = 0.0
        else:
            rest_cx = -r.clear_w_m / 2 + leaf_w / 2 + index * (r.clear_w_m - leaf_w) / (n - 1)
        slide_sign = 1.0 if rest_cx <= 0.0 else -1.0
        room = (
            r.clear_w_m / 2 - leaf_w / 2 - rest_cx
            if slide_sign > 0
            else rest_cx + r.clear_w_m / 2 - leaf_w / 2
        )
        leaf_travel = max(min(travel, max(room, 0.0)), 0.012)
        # head guide and sill sit clear above and below the leaf and run back to
        # the jamb face, so every track is carried by real carcass structure
        track_back_y = r.front_y_m + 0.004
        track_front_y = plane_y - 0.004
        track_d = max(track_back_y - track_front_y, 0.014)
        track_cy = (track_back_y + track_front_y) / 2.0
        # the run of each track is the leaf plus its own travel, so a longer
        # bypass stroke needs a longer guide and sill
        track_run = min(leaf_w + leaf_travel + 0.020, r.opening_w_m + 0.020)
        track_cx = rest_cx + slide_sign * leaf_travel / 2.0
        _bx(
            carcass,
            (track_run, track_d, 0.014),
            (track_cx, track_cy, row_hi - 0.006),
            mats["dark"],
            f"{tag}__top_guide_{index}",
        )
        _bx(
            carcass,
            (track_run, track_d, 0.014),
            (track_cx, track_cy, row_lo + 0.006),
            mats["dark"],
            f"{tag}__track_sill_{index}",
        )
        leaf = _new_leaf(model, r, index, "door_leaf", "offset bypass track")
        _build_leaf_body(leaf, r, mats, 1.0, leaf_w, leaf_h)
        # rollers stand proud of the leaf edge and engage the guide and sill
        for j, z in enumerate((leaf_h / 2 - 0.001, -leaf_h / 2 + 0.001)):
            _bx(
                leaf,
                (0.050, 0.016, 0.014),
                (_leaf_setback(r) + leaf_w / 2, r.leaf_t_m / 2 + 0.002, z),
                mats["metal"],
                f"{tag}__roller_{index}_{j}",
            )
        mate = _plane_mate(
            provider_name=f"body_form.front_opening.track_{index}",
            provider_point=(
                rest_cx - _leaf_setback(r) - leaf_w / 2,
                plane_y - r.leaf_t_m / 2.0,
                zc,
            ),
            provider_extent=(r.opening_w_m, row_hi - row_lo),
            consumer_name=f"door_mechanism.track_seat_{index}",
            consumer_extent=(leaf_w, leaf_h),
        )
        joint = f"{tag}__leaf_joint_{index}"
        lower, upper = (0.0, leaf_travel) if slide_sign > 0 else (-leaf_travel, 0.0)
        model.articulation(
            joint,
            ArticulationType.PRISMATIC,
            parent=carcass,
            child=leaf,
            origin=mate.origin,
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=26.0, velocity=0.32, lower=lower, upper=upper),
            meta={"positive_motion": "leaf slides across the opening on its own track"},
        )
        register_interface_mate(model, joint, mate)
        leaves.append(leaf)
    return leaves


def _door_mechanism_bifold_build(model, carcass, r: ResolvedConfig, mats) -> list[object]:
    tag = "door_mechanism__bifold"
    leaves: list[object] = []
    for index, _row, cell_index, per_row, cell_left, cell_w, row_lo, row_hi in _cell_geometry(r):
        leaf_h = max(row_hi - row_lo, _MIN_LEAF_H)
        zc = (row_lo + row_hi) / 2.0
        # the pair shares one cell: primary + knuckle offset + folding leaf all
        # stay inside the cell so neighbouring pairs never meet at rest
        half_w = max(_bifold_half_width(cell_w, r.leaf_t_m, r.leaf_relief_m), 0.012)
        hinge_left = (
            r.hinge_side == "left" if per_row == 1 else cell_index < per_row / 2.0
        )
        sign = 1.0 if hinge_left else -1.0
        hinge_x = (
            cell_left + _OUTER_REVEAL if hinge_left else cell_left + cell_w - _OUTER_REVEAL
        )
        has_neighbour = (cell_index > 0) if hinge_left else (cell_index < per_row - 1)
        limit = r.interior_swing_rad if has_neighbour else r.door_swing_rad

        primary = _new_leaf(model, r, index, "door_leaf", "bifold primary leaf")
        _build_leaf_body(primary, r, mats, sign, half_w, leaf_h)
        _hinge_hardware(carcass, primary, r, mats, hinge_x, zc, leaf_h, sign, tag, str(index))
        mate = _axis_mate(
            provider_name=f"body_form.front_opening.hinge_{index}",
            point=(hinge_x, r.hinge_y_m, zc),
            consumer_name=f"door_mechanism.hinge_line_{index}",
            consumer_radius=_BARREL_R * 0.86,
        )
        joint = f"{tag}__leaf_joint_{index}"
        lower, upper = (-limit, 0.0) if sign > 0 else (0.0, limit)
        model.articulation(
            joint,
            ArticulationType.REVOLUTE,
            parent=carcass,
            child=primary,
            origin=mate.origin,
            axis=mate.axis,
            motion_limits=MotionLimits(effort=12.0, velocity=1.4, lower=lower, upper=upper),
            meta={"positive_motion": "primary leaf swings outward toward -Y"},
        )
        register_interface_mate(model, joint, mate)

        # secondary leaf folds off the primary leading stile
        fold_x = sign * (
            _leaf_setback(r) + half_w + _fold_knuckle_offset(r.leaf_t_m, r.leaf_relief_m)
        )
        fold = _new_leaf(model, r, index, "fold_leaf", "bifold folding leaf")
        _build_leaf_body(fold, r, mats, sign, half_w, leaf_h)
        knuckle_reach = abs(fold_x) - (_leaf_setback(r) + half_w) + 0.006
        for station_index, station in enumerate((-leaf_h * 0.30, leaf_h * 0.30)):
            _cy(
                primary,
                _BARREL_R,
                0.026,
                (fold_x, 0.0, station),
                mats["metal"],
                f"{tag}__fold_knuckle_{index}_{station_index}",
            )
            _bx(
                primary,
                (knuckle_reach, 0.006, 0.020),
                (fold_x - sign * (knuckle_reach / 2.0 - 0.002), 0.0, station),
                mats["metal"],
                f"{tag}__fold_knuckle_plate_{index}_{station_index}",
            )
            for barrel_index, offset in enumerate((-0.019, 0.019)):
                _cy(
                    fold,
                    _BARREL_R * 0.86,
                    0.020,
                    (0.0, 0.0, station + offset),
                    mats["metal"],
                    f"{tag}__fold_barrel_{index}_{station_index}_{barrel_index}",
                )
                _hinge_strap(
                    fold,
                    r,
                    mats,
                    sign,
                    station + offset,
                    f"{tag}__fold_strap_{index}_{station_index}_{barrel_index}",
                )
        fold_mate = _axis_mate(
            provider_name=f"door_kind.leading_stile_{index}",
            point=(fold_x, 0.0, 0.0),
            consumer_name=f"door_mechanism.fold_line_{index}",
            consumer_radius=_BARREL_R * 0.86,
        )
        fold_joint = f"{tag}__fold_joint_{index}"
        # the folding leaf follows the primary outward (-Y); folding the other
        # way would drive it back through the carcass front frame
        fold_lower, fold_upper = (
            (-r.fold_swing_rad, 0.0) if sign > 0 else (0.0, r.fold_swing_rad)
        )
        model.articulation(
            fold_joint,
            ArticulationType.REVOLUTE,
            parent=primary,
            child=fold,
            origin=fold_mate.origin,
            axis=fold_mate.axis,
            motion_limits=MotionLimits(effort=10.0, velocity=1.4, lower=fold_lower, upper=fold_upper),
            meta={"positive_motion": "secondary leaf folds back against the primary leaf"},
        )
        register_interface_mate(model, fold_joint, fold_mate)
        leaves.extend((primary, fold))
    return leaves


_MECHANISM_BUILDERS = {
    "revolute_swing": _door_mechanism_revolute_swing_build,
    "sliding_bypass": _door_mechanism_sliding_bypass_build,
    "bifold": _door_mechanism_bifold_build,
}


# ---------------------------------------------------------------------------
# build
# ---------------------------------------------------------------------------
def _build_source_family(
    config: Config | None = None, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    r = resolve_config(config or Config())
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = _materials(model, r.palette)
    carcass = model.part(
        "carcass",
        meta={"role": "carcass", "slot": "body_form", "candidate": r.body_form},
    )
    _SUPPORT_BUILDERS[r.support_base](carcass, r, mats)
    _BODY_BUILDERS[r.body_form](carcass, r, mats)
    _build_front_frame(carcass, r, mats)
    _FITMENT_BUILDERS[r.interior_fitment](carcass, r, mats)
    _MECHANISM_BUILDERS[r.door_mechanism](model, carcass, r, mats)
    carcass.inertial = None
    model.meta["slot_choices"] = (
        ("body_form", r.body_form),
        ("door_kind", r.door_kind),
        ("door_mechanism", r.door_mechanism),
        ("support_base", r.support_base),
        ("interior_fitment", r.interior_fitment),
        ("door_count", str(r.door_count)),
        ("shelf_count", str(r.shelf_count)),
    )
    return model


def _require_multi_door_revolute(config: Config, r: ResolvedConfig) -> None:
    if config.door_mechanism != "revolute_swing" or r.door_mechanism != "revolute_swing":
        raise ValueError("multi-door assets require door_mechanism='revolute_swing'")
    if isinstance(config.door_count, bool) or not isinstance(config.door_count, int):
        raise ValueError("multi-door assets require integer door_count in [1, 4]")
    if not 1 <= config.door_count <= 4 or r.door_count != config.door_count:
        raise ValueError("multi-door assets require integer door_count in [1, 4]")


def build_multi_door_cabinet(
    config: Config | None = None, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    """Build one to four deterministic side-hinged revolute doors."""

    resolved_config = config or Config()
    r = resolve_config(resolved_config)
    _require_multi_door_revolute(resolved_config, r)
    return _build_source_family(resolved_config, assets=assets)


def _articulation_metadata(
    r: ResolvedConfig, layout: _RevoluteLeafLayout
) -> dict[str, object]:
    target_link = f"door_kind__{r.door_kind}__door_leaf_{layout.index}"
    handle_layout = _handle_layout(
        r, layout.sign, layout.leaf_width_m, layout.leaf_height_m
    )

    def _float_list(value: object) -> list[float]:
        if not isinstance(value, tuple):
            raise TypeError(f"expected tuple metadata value, got {type(value).__name__}")
        return [float(item) for item in value]

    lower, upper = layout.limits
    return {
        "index": layout.index,
        "row_index": layout.row_index,
        "cell_index": layout.cell_index,
        "hinge_side": layout.hinge_side,
        "target_joint": f"door_mechanism__revolute_swing__leaf_joint_{layout.index}",
        "target_link": target_link,
        "joint_type": "revolute",
        "axis": [0.0, 0.0, 1.0],
        "joint_origin": [layout.hinge_x_m, r.hinge_y_m, layout.hinge_z_m],
        "limits": {"lower": lower, "upper": upper},
        "opening_sign": layout.opening_sign,
        "opening_endpoint": layout.opening_endpoint,
        "handle_frame": {
            "link": target_link,
            "reference": "target_link_local_at_closed_pose",
            "xyz": _float_list(handle_layout["xyz"]),
            "rpy": _float_list(handle_layout["rpy"]),
            "approach_axis": _float_list(handle_layout["approach_axis"]),
            "grip_axis": _float_list(handle_layout["grip_axis"]),
        },
    }


def benchmark_metadata(config: Config) -> dict[str, object]:
    """Return primary and per-door task metadata for a revolute door-count asset."""

    r = resolve_config(config)
    _require_multi_door_revolute(config, r)
    articulations = [
        _articulation_metadata(r, layout)
        for layout in _revolute_leaf_layouts(r)
    ]
    if len(articulations) != r.door_count:
        raise ValueError(
            f"resolved door_count={r.door_count} produced {len(articulations)} articulations"
        )
    primary = articulations[0]
    primary_keys = (
        "target_joint",
        "target_link",
        "joint_type",
        "axis",
        "joint_origin",
        "limits",
        "opening_sign",
        "opening_endpoint",
        "handle_frame",
    )
    metadata = {key: primary[key] for key in primary_keys}
    metadata.update(
        {
            "primary_articulation_index": 0,
            "hinge_side": primary["hinge_side"],
            "door_count": r.door_count,
            "articulations": articulations,
            "layout": {
                "enumeration_order": "rows bottom-to-top, cells left-to-right",
                "rows": [
                    {
                        "row_index": row_index,
                        "lower_z_m": row_lo,
                        "upper_z_m": row_hi,
                        "door_count": per_row,
                    }
                    for row_index, (row_lo, row_hi, per_row) in enumerate(r.rows)
                ],
            },
            "front_axis": [0.0, -1.0, 0.0],
            "up_axis": [0.0, 0.0, 1.0],
            "parameter_conventions": {
                "primary_target": "articulation index 0",
                "opening_endpoint": "signed joint coordinate at the fully open pose",
            },
        }
    )
    return metadata


def _build_seeded_source_family(seed: int) -> ArticulatedObject:
    return _build_source_family(_config_from_seed(seed))


# ---------------------------------------------------------------------------
# author tests
# ---------------------------------------------------------------------------
def _run_source_family_tests(
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
        "category_anchor: one load-bearing carcass",
        len(roles.get("carcass", [])) == 1,
        details=str(roles.get("carcass")),
    )

    leaf_names = roles.get("door_leaf", [])
    moving = {
        j.child: j
        for j in object_model.articulations
        if j.articulation_type != ArticulationType.FIXED
    }
    ctx.check(
        "category_anchor: every door leaf is a moving child of the carcass",
        len(leaf_names) == r.door_count
        and all(name in moving and moving[name].parent == "carcass" for name in leaf_names),
        details=f"leaves={leaf_names} expected={r.door_count}",
    )

    if r.door_mechanism == "revolute_swing":
        name = leaf_names[0]
        joint = moving[name]
        rest = ctx.part_world_aabb(parts[name])
        limit = joint.motion_limits.upper or joint.motion_limits.lower or 0.0
        with ctx.pose({joint: limit * 0.6}):
            opened = ctx.part_world_aabb(parts[name])
        advanced = (
            rest is not None and opened is not None and opened[0][1] < rest[0][1] - 0.02
        )
        ctx.check(
            "category_anchor: swing leaf opens outward from the front plane",
            advanced,
            details=f"rest_min_y={None if rest is None else round(rest[0][1], 4)} "
            f"open_min_y={None if opened is None else round(opened[0][1], 4)}",
        )
    elif r.door_mechanism == "sliding_bypass":
        name = leaf_names[0]
        joint = moving[name]
        rest = ctx.part_world_aabb(parts[name])
        limit = joint.motion_limits.upper or joint.motion_limits.lower or 0.0
        with ctx.pose({joint: limit}):
            slid = ctx.part_world_aabb(parts[name])
        moved = (
            0.0
            if rest is None or slid is None
            else abs((slid[0][0] + slid[1][0]) / 2 - (rest[0][0] + rest[1][0]) / 2)
        )
        ctx.check(
            "category_anchor: bypass leaf translates across the opening",
            moved > 0.008,
            details=f"dx={moved:.4f}",
        )
    else:
        fold_names = roles.get("fold_leaf", [])
        ok = len(fold_names) == r.door_count and all(
            name in moving and moving[name].parent in leaf_names for name in fold_names
        )
        ctx.check(
            "category_anchor: fold leaf hinges off the primary leaf",
            ok,
            details=f"folds={fold_names} primaries={leaf_names}",
        )

    # the cavity keeps a real shelf ladder derived from N
    shelf_visuals = [
        v.name
        for v in parts["carcass"].visuals
        if "__shelf_" in str(v.name) and "__shelf_edge_" not in str(v.name)
    ]
    ctx.check(
        "shelf ladder matches shelf_count",
        len(shelf_visuals) == r.shelf_count,
        details=str(shelf_visuals),
    )

    ctx.check(
        "door leaves stay forward of the jamb face",
        r.leaf_back_y_m <= r.front_y_m,
        details=f"leaf_back_y={r.leaf_back_y_m:.4f} front_y={r.front_y_m:.4f}",
    )

    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=64, ignore_fixed=True)
    return ctx.report()


_run_source_family_tests.__test__ = False


def run_multi_door_cabinet_tests(
    object_model: ArticulatedObject, config: Config
) -> TestReport:
    r = resolve_config(config)
    _require_multi_door_revolute(config, r)
    return _run_source_family_tests(object_model, config)


run_multi_door_cabinet_tests.__test__ = False


# ---------------------------------------------------------------------------
# authored high-risk cross-slot corners
# ---------------------------------------------------------------------------
TEMPLATE_CORNERS = (
    corner_case(
        "drum_widest_opening_four_bypass_tracks",
        {
            "body_form": "curved_bow_shell",
            "door_kind": "glazed_curtain",
            "door_mechanism": "sliding_bypass",
            "support_base": "wall_mount",
            "interior_fitment": "edge_banded_shelf",
            "door_count": 4,
            "shelf_count": 3,
            "carcass_width_m": 0.92,
            "carcass_height_m": 1.40,
            "shell_wall_t_m": 0.022,
            "front_opening_deg": 148.0,
            "slide_travel_m": 0.46,
            "mount_clearance_m": 1.25,
            "edge_band_h_m": 0.045,
        },
        reason="widest chord frame on the smallest drum wall with the deepest multi-track stack",
    ),
    corner_case(
        "narrow_taper_four_bifold_pairs",
        {
            "body_form": "tapered_box",
            "door_kind": "fretwork_pierced",
            "door_mechanism": "bifold",
            "support_base": "feet_plinth",
            "interior_fitment": "plain_shelf",
            "door_count": 4,
            "shelf_count": 3,
            "carcass_width_m": 0.66,
            "carcass_depth_m": 0.34,
            "carcass_height_m": 1.70,
            "taper_top_ratio": 0.68,
            "fold_swing_rad": 1.75,
            "door_swing_rad": 1.92,
            "plinth_h_m": 0.210,
        },
        reason="narrowest opening after the strongest taper, folded pairs at full travel",
    ),
    corner_case(
        "widest_case_three_swing_leaves",
        {
            "body_form": "rect_box",
            "door_kind": "raised_panel",
            "door_mechanism": "revolute_swing",
            "support_base": "turned_feet",
            "interior_fitment": "edge_banded_shelf",
            "door_count": 3,
            "shelf_count": 1,
            "carcass_width_m": 1.50,
            "carcass_depth_m": 0.50,
            "carcass_height_m": 0.92,
            "door_swing_rad": 1.92,
            "rect_side_panel_t_m": 0.032,
            "turned_foot_h_m": 0.085,
        },
        reason="shortest leaf height with a middle leaf between two neighbours at full swing",
    ),
    corner_case(
        "drum_single_swing_leaf_minimum",
        {
            "body_form": "curved_bow_shell",
            "door_kind": "flush_slab",
            "door_mechanism": "revolute_swing",
            "support_base": "recessed_plinth",
            "interior_fitment": "plain_shelf",
            "door_count": 1,
            "shelf_count": 1,
            "carcass_width_m": 0.62,
            "carcass_height_m": 0.90,
            "front_opening_deg": 96.0,
            "shell_wall_t_m": 0.044,
            "slab_t_m": 0.032,
            "door_swing_rad": 1.92,
            "toe_kick_h_m": 0.060,
        },
        reason="smallest drum with the narrowest opening arc and the thickest leaf",
    ),
)


__all__ = [
    "TEMPLATE_DOMAIN",
    "Config",
    "HandleType",
    "HingeSide",
    "ResolvedConfig",
    "benchmark_metadata",
    "build_multi_door_cabinet",
    "resolve_config",
    "run_multi_door_cabinet_tests",
    "variable_space",
]
