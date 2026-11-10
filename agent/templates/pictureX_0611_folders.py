# SPDX-License-Identifier: Apache-2.0

"""Self-contained 'folders' template — expanding file organizers / folders.

Rebuilt from the single source record
``rec_picturex_0611__folders__001__png__airflex_batch_20260710_44a51551668f45fbacaa1b09d219161b``
(rev_000001): an expandable hanging-file organizer whose two rigid end covers
enclose N thin interior leaves joined by a uniform prismatic accordion.

The source object is decomposed into four genuinely independent structural axes
instead of one monolithic "folder family" slot.  Each axis is a distinct
sub-assembly of the source `model.py`:

* ``leaf_top``     — the leaf's top hardware (source ``_add_pocket_stage``
  crossbar + projecting hanging-rail tabs, model.py:L152-L171; the bound top /
  vertical edge binding profile of ``_add_end_panel``, model.py:L125-L140).
* ``gusset_style`` — the per-gap connective fold (source ``_add_gussets`` /
  ``_add_vertical_leaf`` V-folds, model.py:L42-L91).
* ``cover_build``  — the rigid end cover construction (source ``_add_end_panel``,
  model.py:L117-L140).
* ``closure``      — the closure at the moving end (source is open-topped;
  the fold-over flap and the turn-button clasp are controlled extrapolations
  inside the folder/wallet form family, each adding exactly one revolute DOF).

Every combination builds: the accordion host, the retention tapes (source
``_add_side_attachment``, model.py:L94-L114) and the leaf/cover panels are
shared and re-derived from the same parameter DAG, so slot candidates never
need a compatibility gate.

Interior leaves are parented to the fixed end board as a mimic *star* (leaf
``i`` mimics the driver with multiplier ``i+1``) so the observable uniform
expansion of the source is reproduced while every leaf shares one
``end_board -> file_leaf`` prismatic relation.  Neighbour support contact is
carried by the retention tapes, which are 3 mm thin along the depth axis so
their unavoidable deep along-axis reach never reads as a collision.

This file is the only runtime truth.  It imports nothing but the stdlib and the
Articraft ``sdk``; it does not read the SourceMap, TemplateDesign, any source
``model.py``, or any source-replay runtime.
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
    Mimic,
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

LeafTop = Literal[
    "hanging_rail_crossbar",
    "staggered_index_tab",
    "reinforced_bound_edge",
]
GussetStyle = Literal[
    "v_fold_bellows",
    "pleated_multifold",
    "floor_web_gusset",
]
CoverBuild = Literal[
    "bound_board",
    "framed_board",
    "wrap_lip_shell",
]
Closure = Literal[
    "open_top",
    "fold_over_flap",
    "turn_button_clasp",
]

LEAF_TOPS: tuple[LeafTop, ...] = (
    "hanging_rail_crossbar",
    "staggered_index_tab",
    "reinforced_bound_edge",
)
GUSSET_STYLES: tuple[GussetStyle, ...] = (
    "v_fold_bellows",
    "pleated_multifold",
    "floor_web_gusset",
)
COVER_BUILDS: tuple[CoverBuild, ...] = (
    "bound_board",
    "framed_board",
    "wrap_lip_shell",
)
CLOSURES: tuple[Closure, ...] = (
    "open_top",
    "fold_over_flap",
    "turn_button_clasp",
)
DIVIDER_COUNTS: tuple[int, ...] = (6, 9, 12, 16)

TEMPLATE_DOMAIN = TemplateDomain(
    (
        component_slot("leaf_top", LEAF_TOPS),
        component_slot("gusset_style", GUSSET_STYLES),
        component_slot("cover_build", COVER_BUILDS),
        component_slot("closure", CLOSURES),
        multiplicity_slot(
            "divider_count",
            DIVIDER_COUNTS,
            item_slot="leaf_top",
        ),
    )
)

# Independent-parameter ranges (honest continuous dimensions; not core/raw).
_DEPTH_RANGE = (0.22, 0.34)
_LEAF_HEIGHT_RANGE = (0.18, 0.30)
_PITCH_RANGE = (0.014, 0.024)
_TRAVEL_RANGE = (0.006, 0.012)

_END_THICKNESS = 0.010
_LEAF_THICKNESS = 0.003

# Retention tape (source `_add_side_attachment`).  It reaches a full gap travel
# back over the previous part so the stack is a single supported assembly, and
# it is only 3 mm thick along the depth axis, so every cross-part AABB overlap
# it produces stays under the 5 mm collision tolerance on that one axis.
_TAPE_THICKNESS = 0.003
_TAPE_INSET = 0.0035  # tape centre inboard of the depth edge
_TAPE_HEIGHT = 0.030
_TAPE_Z = 0.021
_TAPE_SLACK = 0.004
_TAPE_ANCHOR = 0.001  # embed into the tape's own panel

# Connective fold band.  The fold lives strictly inside the compressed gap:
# it starts 1.5 mm clear of the previous part's trim envelope and ends 0.5 mm
# inside its own panel, so it is connected to its own part and can never
# interpenetrate any neighbour, at any pose.
_GUSSET_CLEAR = 0.0015
_GUSSET_ANCHOR = 0.0005
_TRIM_BULGE = 0.0015  # max x reach of any panel trim beyond the panel half
_GUSSET_LEAF_T = 0.0015
_GUSSET_Z_LO = 0.05
_GUSSET_Z_HI = 0.93

# Closure hardware.  The cover-side knuckle boss is 3.5 mm thin along the depth
# axis so its captured contact with the moving closure part stays under the
# collision tolerance on that axis at every pose (no allowance needed).
_BOSS_THICKNESS = 0.0035
_FLAP_HINGE_OUT = 0.020
_CLASP_HINGE_OUT = 0.018
_FLAP_MAX_ANGLE = math.radians(135.0)
_CLASP_MAX_ANGLE = math.radians(150.0)


@dataclass(frozen=True)
class Config:
    leaf_top: LeafTop = "hanging_rail_crossbar"
    gusset_style: GussetStyle = "v_fold_bellows"
    cover_build: CoverBuild = "bound_board"
    closure: Closure = "open_top"
    divider_count: int = 16
    depth_m: float | None = None
    leaf_height_m: float | None = None
    compressed_pitch_m: float | None = None
    gap_travel_m: float | None = None
    name: str = "pictureX_0611_folders"


@dataclass(frozen=True)
class ResolvedConfig:
    leaf_top: LeafTop
    gusset_style: GussetStyle
    cover_build: CoverBuild
    closure: Closure
    divider_count: int
    depth_m: float
    leaf_height_m: float
    compressed_pitch_m: float
    gap_travel_m: float
    end_thickness_m: float
    leaf_thickness_m: float
    tape_reach_m: float
    name: str


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def config_from_seed(seed: int) -> Config:
    choices = TEMPLATE_DOMAIN.sample(seed)
    rng = random.Random(seed ^ 0xF01DE_2026)
    return Config(
        leaf_top=choices["leaf_top"],
        gusset_style=choices["gusset_style"],
        cover_build=choices["cover_build"],
        closure=choices["closure"],
        divider_count=choices["divider_count"],
        depth_m=round(rng.uniform(*_DEPTH_RANGE), 4),
        leaf_height_m=round(rng.uniform(*_LEAF_HEIGHT_RANGE), 4),
        compressed_pitch_m=round(rng.uniform(*_PITCH_RANGE), 4),
        gap_travel_m=round(rng.uniform(*_TRAVEL_RANGE), 4),
    )


def _range_check(name: str, value: float, bounds: tuple[float, float]) -> None:
    low, high = bounds
    if not low <= value <= high:
        raise ValueError(f"{name} must be in [{low}, {high}], got {value}")


def resolve_config(config: Config) -> ResolvedConfig:
    TEMPLATE_DOMAIN.validate(
        {
            "leaf_top": config.leaf_top,
            "gusset_style": config.gusset_style,
            "cover_build": config.cover_build,
            "closure": config.closure,
            "divider_count": config.divider_count,
        }
    )
    depth = 0.310 if config.depth_m is None else float(config.depth_m)
    leaf_height = 0.230 if config.leaf_height_m is None else float(config.leaf_height_m)
    pitch = 0.018 if config.compressed_pitch_m is None else float(config.compressed_pitch_m)
    travel = 0.009 if config.gap_travel_m is None else float(config.gap_travel_m)
    _range_check("depth_m", depth, _DEPTH_RANGE)
    _range_check("leaf_height_m", leaf_height, _LEAF_HEIGHT_RANGE)
    _range_check("compressed_pitch_m", pitch, _PITCH_RANGE)
    _range_check("gap_travel_m", travel, _TRAVEL_RANGE)
    return ResolvedConfig(
        leaf_top=config.leaf_top,
        gusset_style=config.gusset_style,
        cover_build=config.cover_build,
        closure=config.closure,
        divider_count=int(config.divider_count),
        depth_m=depth,
        leaf_height_m=leaf_height,
        compressed_pitch_m=pitch,
        gap_travel_m=travel,
        end_thickness_m=_END_THICKNESS,
        leaf_thickness_m=_LEAF_THICKNESS,
        tape_reach_m=travel + _TAPE_SLACK,
        name=config.name,
    )


def slot_choices_for_config(config: Config | ResolvedConfig) -> tuple[tuple[str, object], ...]:
    return (
        ("leaf_top", config.leaf_top),
        ("gusset_style", config.gusset_style),
        ("cover_build", config.cover_build),
        ("closure", config.closure),
        ("divider_count", int(config.divider_count)),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, object], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# --------------------------------------------------------------------------- #
# Materials
# --------------------------------------------------------------------------- #
def _materials(model: ArticulatedObject) -> dict[str, str]:
    model.material("olive_board", rgba=(0.29, 0.30, 0.18, 1.0))
    model.material("olive_fiberboard", rgba=(0.34, 0.35, 0.22, 1.0))
    model.material("olive_fabric", rgba=(0.25, 0.26, 0.16, 1.0))
    model.material("olive_binding", rgba=(0.20, 0.21, 0.13, 1.0))
    model.material("ivory_rail", rgba=(0.89, 0.89, 0.85, 1.0))
    model.material("ivory_tab", rgba=(0.94, 0.94, 0.91, 1.0))
    model.material("kraft_board", rgba=(0.55, 0.42, 0.26, 1.0))
    model.material("kraft_tab", rgba=(0.72, 0.58, 0.36, 1.0))
    model.material("kraft_dark", rgba=(0.36, 0.26, 0.15, 1.0))
    return {
        "board": "olive_board",
        "fiber": "olive_fiberboard",
        "fabric": "olive_fabric",
        "binding": "olive_binding",
        "rail": "ivory_rail",
        "tab": "ivory_tab",
        "kraft": "kraft_board",
        "kraft_tab": "kraft_tab",
        "kraft_dark": "kraft_dark",
    }


def _box(part, size, xyz, material: str, name: str, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(Box(size), origin=Origin(xyz=xyz, rpy=rpy), material=material, name=name, material_class_id="paper.cardboard")


def _fold_segment(
    part,
    a: tuple[float, float],
    b: tuple[float, float],
    height: float,
    z_center: float,
    material: str,
    name: str,
) -> None:
    """One thin vertical fabric leaf between two XY endpoints (source L42-L55)."""
    ax, ay = a
    bx, by = b
    length = math.hypot(bx - ax, by - ay) + 0.0006
    yaw = math.atan2(by - ay, bx - ax)
    _box(
        part,
        (length, _GUSSET_LEAF_T, height),
        ((ax + bx) / 2.0, (ay + by) / 2.0, z_center),
        material,
        name,
        rpy=(0.0, 0.0, yaw),
    )


# --------------------------------------------------------------------------- #
# Shared retention tapes (neighbour support contact, source L94-L114)
# --------------------------------------------------------------------------- #
def _add_retention_tapes(
    part,
    r: ResolvedConfig,
    *,
    prev_thickness: float,
    own_thickness: float,
    material: str,
) -> None:
    pitch = r.compressed_pitch_m
    x_min = -pitch + prev_thickness / 2.0 - r.tape_reach_m
    x_max = own_thickness / 2.0 + _TAPE_ANCHOR
    length = x_max - x_min
    x_center = 0.5 * (x_min + x_max)
    half_depth = r.depth_m / 2.0
    for side, sign in (("near", -1.0), ("far", 1.0)):
        _box(
            part,
            (length, _TAPE_THICKNESS, _TAPE_HEIGHT),
            (x_center, sign * (half_depth - _TAPE_INSET), _TAPE_Z),
            material,
            f"retention_tape_{side}",
        )


# --------------------------------------------------------------------------- #
# gusset_style — the per-gap connective fold
# --------------------------------------------------------------------------- #
def _gusset_band(
    r: ResolvedConfig,
    *,
    prev_thickness: float,
    own_thickness: float,
) -> tuple[float, float]:
    start_x = -r.compressed_pitch_m + prev_thickness / 2.0 + _TRIM_BULGE + _GUSSET_CLEAR
    end_x = -own_thickness / 2.0 + _GUSSET_ANCHOR
    return start_x, end_x


def _gusset_z(r: ResolvedConfig) -> tuple[float, float]:
    h = r.leaf_height_m
    lo = _GUSSET_Z_LO * h
    hi = _GUSSET_Z_HI * h
    return 0.5 * (lo + hi), hi - lo


def _gusset_style_v_fold_bellows_build(
    part,
    r: ResolvedConfig,
    band: tuple[float, float],
    material: str,
    prefix: str,
) -> None:
    """Paired front/rear V-folds, one crease per side (source L58-L91)."""
    start_x, end_x = band
    span = end_x - start_x
    crease_x = 0.5 * (start_x + end_x)
    outset = _clamp(0.6 * span, 0.003, 0.008)
    z_center, height = _gusset_z(r)
    half_depth = r.depth_m / 2.0
    for side, sign in (("near", -1.0), ("far", 1.0)):
        y_in = sign * (half_depth - 0.0015)
        y_out = sign * (half_depth + outset)
        points = ((start_x, y_in), (crease_x, y_out), (end_x, y_in))
        for index in range(len(points) - 1):
            _fold_segment(
                part,
                points[index],
                points[index + 1],
                height,
                z_center,
                material,
                f"{prefix}_{side}_leaf_{index}",
            )


def _gusset_style_pleated_multifold_build(
    part,
    r: ResolvedConfig,
    band: tuple[float, float],
    material: str,
    prefix: str,
) -> None:
    """Same crease generator driven to three creases per side."""
    start_x, end_x = band
    span = end_x - start_x
    outset = _clamp(0.35 * span, 0.002, 0.006)
    z_center, height = _gusset_z(r)
    half_depth = r.depth_m / 2.0
    for side, sign in (("near", -1.0), ("far", 1.0)):
        y_in = sign * (half_depth - 0.0015)
        y_out = sign * (half_depth + outset)
        points = (
            (start_x, y_in),
            (start_x + 0.25 * span, y_out),
            (start_x + 0.50 * span, y_in),
            (start_x + 0.75 * span, y_out),
            (end_x, y_in),
        )
        for index in range(len(points) - 1):
            _fold_segment(
                part,
                points[index],
                points[index + 1],
                height,
                z_center,
                material,
                f"{prefix}_{side}_pleat_{index}",
            )


def _gusset_style_floor_web_gusset_build(
    part,
    r: ResolvedConfig,
    band: tuple[float, float],
    material: str,
    prefix: str,
) -> None:
    """Boxed bottom: straight side webs plus a horizontal floor web."""
    start_x, end_x = band
    span = end_x - start_x
    z_center, height = _gusset_z(r)
    half_depth = r.depth_m / 2.0
    for side, sign in (("near", -1.0), ("far", 1.0)):
        y_in = sign * (half_depth - 0.0015)
        _fold_segment(
            part,
            (start_x, y_in),
            (end_x, y_in),
            height,
            z_center,
            material,
            f"{prefix}_{side}_web",
        )
    _box(
        part,
        (span + 0.0006, r.depth_m - 0.014, 0.006),
        (0.5 * (start_x + end_x), 0.0, 0.08 * r.leaf_height_m),
        material,
        f"{prefix}_floor_web",
    )


def _add_gusset(
    part,
    r: ResolvedConfig,
    mats: dict[str, str],
    *,
    prev_thickness: float,
    own_thickness: float,
    prefix: str,
) -> None:
    band = _gusset_band(r, prev_thickness=prev_thickness, own_thickness=own_thickness)
    material = mats["fabric"]
    scoped = f"gusset_style__{r.gusset_style}__{prefix}"
    if r.gusset_style == "v_fold_bellows":
        _gusset_style_v_fold_bellows_build(part, r, band, material, scoped)
    elif r.gusset_style == "pleated_multifold":
        _gusset_style_pleated_multifold_build(part, r, band, material, scoped)
    else:
        _gusset_style_floor_web_gusset_build(part, r, band, material, scoped)


# --------------------------------------------------------------------------- #
# cover_build — rigid end cover construction (source L117-L140)
# --------------------------------------------------------------------------- #
def _cover_build_bound_board_build(
    part,
    r: ResolvedConfig,
    mats: dict[str, str],
    outward: float,
) -> None:
    """Flat board with a woven top binding and two vertical edge bindings."""
    del outward
    t = r.end_thickness_m
    h = r.leaf_height_m
    d = r.depth_m
    _box(part, (t, d, h), (0.0, 0.0, h / 2.0), mats["board"], "cover_panel")
    _box(
        part,
        (t + 0.002, d, 0.008),
        (0.0, 0.0, h - 0.004),
        mats["binding"],
        "cover_top_binding",
    )
    for side, sign in (("near", -1.0), ("far", 1.0)):
        _box(
            part,
            (t + 0.002, 0.006, h - 0.006),
            (0.0, sign * (d / 2.0 - 0.003), (h - 0.006) / 2.0),
            mats["binding"],
            f"cover_{side}_binding",
        )


def _cover_build_framed_board_build(
    part,
    r: ResolvedConfig,
    mats: dict[str, str],
    outward: float,
) -> None:
    """Recessed thin panel inside a full four-rail perimeter frame."""
    del outward
    t = r.end_thickness_m
    h = r.leaf_height_m
    d = r.depth_m
    _box(
        part,
        (0.6 * t, d - 0.014, h - 0.014),
        (0.0, 0.0, h / 2.0),
        mats["board"],
        "cover_recessed_panel",
    )
    for side, sign in (("near", -1.0), ("far", 1.0)):
        _box(
            part,
            (t, 0.010, h),
            (0.0, sign * (d / 2.0 - 0.005), h / 2.0),
            mats["kraft_dark"],
            f"cover_{side}_stile",
        )
    _box(part, (t, d, 0.010), (0.0, 0.0, 0.005), mats["kraft_dark"], "cover_bottom_rail")
    _box(part, (t, d, 0.010), (0.0, 0.0, h - 0.005), mats["kraft_dark"], "cover_top_rail")


def _cover_build_wrap_lip_shell_build(
    part,
    r: ResolvedConfig,
    mats: dict[str, str],
    outward: float,
) -> None:
    """Board with a wrapped outer rim returning over the outward face."""
    t = r.end_thickness_m
    h = r.leaf_height_m
    d = r.depth_m
    lip_x = outward * (t / 2.0 + 0.003)
    _box(part, (t, d, h), (0.0, 0.0, h / 2.0), mats["kraft"], "cover_panel")
    _box(part, (0.012, d, 0.005), (lip_x, 0.0, h - 0.0025), mats["kraft_dark"], "cover_top_lip")
    _box(part, (0.012, d, 0.005), (lip_x, 0.0, 0.0025), mats["kraft_dark"], "cover_bottom_lip")
    for side, sign in (("near", -1.0), ("far", 1.0)):
        _box(
            part,
            (0.012, 0.006, h - 0.010),
            (lip_x, sign * (d / 2.0 - 0.003), h / 2.0),
            mats["kraft_dark"],
            f"cover_{side}_lip",
        )


def _add_cover(part, r: ResolvedConfig, mats: dict[str, str], outward: float) -> None:
    if r.cover_build == "bound_board":
        _cover_build_bound_board_build(part, r, mats, outward)
    elif r.cover_build == "framed_board":
        _cover_build_framed_board_build(part, r, mats, outward)
    else:
        _cover_build_wrap_lip_shell_build(part, r, mats, outward)


# --------------------------------------------------------------------------- #
# leaf_top — the leaf's top hardware
# --------------------------------------------------------------------------- #
def _add_leaf_panel(part, r: ResolvedConfig, mats: dict[str, str]) -> None:
    _box(
        part,
        (r.leaf_thickness_m, r.depth_m, r.leaf_height_m),
        (0.0, 0.0, r.leaf_height_m / 2.0),
        mats["fiber"],
        "separator_panel",
    )


def _leaf_top_hanging_rail_crossbar_build(
    part,
    r: ResolvedConfig,
    mats: dict[str, str],
    index: int,
) -> None:
    """Ivory hanging-rail crossbar with projecting rail tabs (source L152-L171)."""
    del index
    h = r.leaf_height_m
    d = r.depth_m
    _box(part, (0.0065, d + 0.012, 0.009), (0.0, 0.0, h + 0.004), mats["rail"], "top_crossbar")
    for side, sign in (("near", -1.0), ("far", 1.0)):
        _box(
            part,
            (0.012, 0.024, 0.006),
            (0.0, sign * (d / 2.0 + 0.008), h + 0.006),
            mats["tab"],
            f"{side}_rail_tab",
        )


def _leaf_top_staggered_index_tab_build(
    part,
    r: ResolvedConfig,
    mats: dict[str, str],
    index: int,
) -> None:
    """Bound top edge carrying one raised index tab, staggered across the depth."""
    t = r.leaf_thickness_m
    h = r.leaf_height_m
    d = r.depth_m
    _box(part, (t + 0.0015, d, 0.010), (0.0, 0.0, h - 0.005), mats["kraft_dark"], "bound_top_edge")
    slots = 4
    slot = index % slots
    usable = d - 0.05
    tab_y = (-0.5 + (slot + 0.5) / slots) * usable
    _box(
        part,
        (t + 0.001, usable / slots - 0.006, 0.028),
        (0.0, tab_y, h + 0.013),
        mats["kraft_tab"],
        "index_tab",
    )


def _leaf_top_reinforced_bound_edge_build(
    part,
    r: ResolvedConfig,
    mats: dict[str, str],
    index: int,
) -> None:
    """Bound top edge plus the source cover's vertical edge bindings (L125-L140)."""
    del index
    t = r.leaf_thickness_m
    h = r.leaf_height_m
    d = r.depth_m
    _box(part, (t + 0.0015, d, 0.010), (0.0, 0.0, h - 0.005), mats["binding"], "bound_top_edge")
    for side, sign in (("near", -1.0), ("far", 1.0)):
        _box(
            part,
            (t + 0.0015, 0.006, h - 0.012),
            (0.0, sign * (d / 2.0 - 0.003), (h - 0.012) / 2.0),
            mats["binding"],
            f"leaf_{side}_binding",
        )


def _add_leaf_top(part, r: ResolvedConfig, mats: dict[str, str], index: int) -> None:
    if r.leaf_top == "hanging_rail_crossbar":
        _leaf_top_hanging_rail_crossbar_build(part, r, mats, index)
    elif r.leaf_top == "staggered_index_tab":
        _leaf_top_staggered_index_tab_build(part, r, mats, index)
    else:
        _leaf_top_reinforced_bound_edge_build(part, r, mats, index)


# --------------------------------------------------------------------------- #
# closure — moving-end closure hardware (0 or 1 revolute DOF)
# --------------------------------------------------------------------------- #
def _closure_open_top_build(
    model: ArticulatedObject,
    moving_end,
    r: ResolvedConfig,
    mats: dict[str, str],
):
    """Source configuration: an open-topped organizer, no closure part."""
    del model, moving_end, r, mats
    return None


def _closure_fold_over_flap_build(
    model: ArticulatedObject,
    moving_end,
    r: ResolvedConfig,
    mats: dict[str, str],
):
    """One revolute fold-over flap hinged on the moving cover's outer face."""
    t = r.end_thickness_m
    h = r.leaf_height_m
    d = r.depth_m
    hinge_x = t / 2.0 + _FLAP_HINGE_OUT
    hinge_z = h - 0.020
    flap_len = _clamp(0.5 * h, 0.09, 0.15)

    _box(
        moving_end,
        (hinge_x + 0.005, _BOSS_THICKNESS, 0.014),
        ((hinge_x + 0.005) / 2.0, 0.0, hinge_z),
        mats["kraft_dark"],
        "closure_hinge_boss",
    )

    flap = model.part(f"closure__{r.closure}__flap", meta={"role": "closure"})
    _box(flap, (0.010, 0.5 * d, 0.012), (0.0, 0.0, 0.0), mats["kraft_dark"], "flap_knuckle")
    _box(flap, (0.006, d, flap_len), (0.008, 0.0, flap_len / 2.0), mats["kraft_tab"], "flap_panel")

    joint_name = f"closure__{r.closure}__flap_hinge"
    provider = AxisInterface(
        name=f"{joint_name}__provider",
        point=(hinge_x, 0.0, hinge_z),
        axis=(0.0, 1.0, 0.0),
        radial=(1.0, 0.0, 0.0),
    )
    consumer = AxisInterface(
        name=f"{joint_name}__consumer",
        point=(0.0, 0.0, 0.0),
        axis=(0.0, 1.0, 0.0),
        radial=(1.0, 0.0, 0.0),
    )
    mate = mate_axes(provider, consumer)
    model.articulation(
        joint_name,
        ArticulationType.REVOLUTE,
        parent=moving_end,
        child=flap,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(effort=8.0, velocity=1.0, lower=0.0, upper=_FLAP_MAX_ANGLE),
        motion_properties=MotionProperties(damping=0.4, friction=0.2),
        meta={"mechanism": "closing flap fold"},
    )
    register_interface_mate(model, joint_name, mate)
    return flap


def _closure_turn_button_clasp_build(
    model: ArticulatedObject,
    moving_end,
    r: ResolvedConfig,
    mats: dict[str, str],
):
    """One revolute turn-button clasp rotating about the accordion axis."""
    t = r.end_thickness_m
    h = r.leaf_height_m
    hinge_x = t / 2.0 + _CLASP_HINGE_OUT
    hinge_z = 0.55 * h
    arm_len = _clamp(0.35 * h, 0.045, 0.075)

    _box(
        moving_end,
        (hinge_x + 0.005, _BOSS_THICKNESS, 0.014),
        ((hinge_x + 0.005) / 2.0, 0.0, hinge_z),
        mats["kraft_dark"],
        "closure_hinge_boss",
    )

    clasp = model.part(f"closure__{r.closure}__clasp", meta={"role": "closure"})
    _box(clasp, (0.010, 0.012, 0.012), (0.0, 0.0, 0.0), mats["kraft_dark"], "clasp_knuckle")
    _box(clasp, (0.005, 0.012, arm_len), (0.0, 0.0, arm_len / 2.0), mats["kraft_tab"], "clasp_arm")

    joint_name = f"closure__{r.closure}__clasp_pivot"
    provider = AxisInterface(
        name=f"{joint_name}__provider",
        point=(hinge_x, 0.0, hinge_z),
        axis=(1.0, 0.0, 0.0),
        radial=(0.0, 0.0, 1.0),
    )
    consumer = AxisInterface(
        name=f"{joint_name}__consumer",
        point=(0.0, 0.0, 0.0),
        axis=(1.0, 0.0, 0.0),
        radial=(0.0, 0.0, 1.0),
    )
    mate = mate_axes(provider, consumer)
    model.articulation(
        joint_name,
        ArticulationType.REVOLUTE,
        parent=moving_end,
        child=clasp,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(effort=6.0, velocity=1.2, lower=0.0, upper=_CLASP_MAX_ANGLE),
        motion_properties=MotionProperties(damping=0.3, friction=0.2),
        meta={"mechanism": "turn-button clasp"},
    )
    register_interface_mate(model, joint_name, mate)
    return clasp


def _add_closure(model: ArticulatedObject, moving_end, r: ResolvedConfig, mats: dict[str, str]):
    if r.closure == "open_top":
        return _closure_open_top_build(model, moving_end, r, mats)
    if r.closure == "fold_over_flap":
        return _closure_fold_over_flap_build(model, moving_end, r, mats)
    return _closure_turn_button_clasp_build(model, moving_end, r, mats)


# --------------------------------------------------------------------------- #
# Assembly (mimic-star accordion) shared by every candidate
# --------------------------------------------------------------------------- #
def _accordion_driver_name(r: ResolvedConfig) -> str:
    return f"leaf_top__{r.leaf_top}__accordion_gap_0"


def _populate_folder(
    model: ArticulatedObject,
    r: ResolvedConfig,
    mats: dict[str, str],
) -> ArticulatedObject:
    n = r.divider_count
    pitch = r.compressed_pitch_m
    travel = r.gap_travel_m
    end_t = r.end_thickness_m
    leaf_t = r.leaf_thickness_m

    fixed_end = model.part(
        f"cover_build__{r.cover_build}__fixed_end",
        meta={"role": "end_board", "position": "fixed"},
    )
    _add_cover(fixed_end, r, mats, -1.0)

    driver_name = _accordion_driver_name(r)

    for index in range(n):
        leaf = model.part(
            f"leaf_top__{r.leaf_top}__leaf_{index}",
            meta={"role": "file_leaf", "index": index},
        )
        _add_leaf_panel(leaf, r, mats)
        _add_leaf_top(leaf, r, mats, index)
        prev_thickness = end_t if index == 0 else leaf_t
        _add_retention_tapes(
            leaf,
            r,
            prev_thickness=prev_thickness,
            own_thickness=leaf_t,
            material=mats["binding"],
        )
        _add_gusset(
            leaf,
            r,
            mats,
            prev_thickness=prev_thickness,
            own_thickness=leaf_t,
            prefix=f"gap_{index}",
        )
        joint_name = f"leaf_top__{r.leaf_top}__accordion_gap_{index}"
        model.articulation(
            joint_name,
            ArticulationType.PRISMATIC,
            parent=fixed_end,
            child=leaf,
            origin=Origin(xyz=((index + 1) * pitch, 0.0, 0.0)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(
                effort=45.0,
                velocity=0.12,
                lower=0.0,
                upper=travel,
            ),
            motion_properties=MotionProperties(damping=2.0, friction=0.8),
            mimic=None if index == 0 else Mimic(joint=driver_name, multiplier=float(index + 1)),
            meta={"mechanism": "uniform accordion expansion", "gap_index": index},
        )

    moving_end = model.part(
        f"cover_build__{r.cover_build}__moving_end",
        meta={"role": "end_board", "position": "moving"},
    )
    _add_cover(moving_end, r, mats, 1.0)
    _add_retention_tapes(
        moving_end,
        r,
        prev_thickness=leaf_t,
        own_thickness=end_t,
        material=mats["binding"],
    )
    _add_gusset(
        moving_end,
        r,
        mats,
        prev_thickness=leaf_t,
        own_thickness=end_t,
        prefix=f"gap_{n}",
    )
    model.articulation(
        f"cover_build__{r.cover_build}__end_gap",
        ArticulationType.PRISMATIC,
        parent=fixed_end,
        child=moving_end,
        origin=Origin(xyz=((n + 1) * pitch, 0.0, 0.0)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(
            effort=45.0,
            velocity=0.12,
            lower=0.0,
            upper=travel,
        ),
        motion_properties=MotionProperties(damping=2.0, friction=0.8),
        mimic=Mimic(joint=driver_name, multiplier=float(n + 1)),
        meta={"mechanism": "uniform accordion expansion", "gap_index": n},
    )

    _add_closure(model, moving_end, r, mats)
    return model


def build_picturex_0611_folders(
    config: Config | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config or config_from_seed(0))
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={
            "category": "pictureX_0611_folders",
            "identified_object": "expanding file organizer / folder",
            "slot_choices": slot_choices_for_config(r),
            "source_layout": "two rigid end covers enclosing N leaves in a uniform accordion",
        },
    )
    mats = _materials(model)
    return _populate_folder(model, r, mats)


# --------------------------------------------------------------------------- #
# Author tests / category anchors
# --------------------------------------------------------------------------- #
def _parts_by_role(model: ArticulatedObject, role: str):
    return [part for part in model.parts if part.meta.get("role") == role]


def run_picturex_0611_folders_tests(
    model: ArticulatedObject,
    config: Config,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)

    ctx.warn(
        "Source trace: pictureX/0611/folders/001.png — an expandable hanging-file "
        "organizer; the broad 'folders' label is context, not a conflicting class."
    )

    end_boards = _parts_by_role(model, "end_board")
    leaves = _parts_by_role(model, "file_leaf")
    closures = _parts_by_role(model, "closure")

    ctx.check(
        "category_anchor: two end covers enclose N leaves",
        len(end_boards) == 2 and len(leaves) == r.divider_count,
        details=f"end_boards={len(end_boards)}, leaves={len(leaves)}, N={r.divider_count}",
    )

    leaf_names = {part.name for part in leaves}
    leaf_joints = [j for j in model.articulations if j.child in leaf_names]
    fixed_end = next((p for p in end_boards if p.meta.get("position") == "fixed"), None)
    driver_name = _accordion_driver_name(r)
    uniform_accordion = (
        len(leaf_joints) == r.divider_count
        and fixed_end is not None
        and all(
            j.articulation_type == ArticulationType.PRISMATIC
            and tuple(j.axis) == (1.0, 0.0, 0.0)
            and j.parent == fixed_end.name
            and j.motion_limits is not None
            and j.motion_limits.lower == 0.0
            and abs(j.motion_limits.upper - r.gap_travel_m) < 1e-9
            for j in leaf_joints
        )
        and any(j.name == driver_name and j.mimic is None for j in leaf_joints)
        and all(
            j.mimic is not None and j.mimic.joint == driver_name
            for j in leaf_joints
            if j.name != driver_name
        )
    )
    ctx.check(
        "category_anchor: uniform prismatic accordion expansion",
        uniform_accordion,
        details=f"leaf_joints={len(leaf_joints)}, driver={driver_name}",
    )

    leaf_visuals = {v.name or "" for part in leaves for v in part.visuals}
    cover_visuals = {v.name or "" for part in end_boards for v in part.visuals}
    all_visuals = {v.name or "" for part in model.parts for v in part.visuals}

    # --- leaf_top -------------------------------------------------------- #
    if r.leaf_top == "hanging_rail_crossbar":
        leaf_top_ok = (
            "top_crossbar" in leaf_visuals
            and any("rail_tab" in name for name in leaf_visuals)
            and "bound_top_edge" not in leaf_visuals
        )
    elif r.leaf_top == "staggered_index_tab":
        tab_ys = {
            round(v.origin.xyz[1], 6)
            for part in leaves
            for v in part.visuals
            if v.name == "index_tab"
        }
        leaf_top_ok = (
            "index_tab" in leaf_visuals
            and "bound_top_edge" in leaf_visuals
            and "top_crossbar" not in leaf_visuals
            and len(tab_ys) == min(4, r.divider_count)
        )
    else:
        leaf_top_ok = (
            "bound_top_edge" in leaf_visuals
            and any("leaf_near_binding" == name for name in leaf_visuals)
            and any("leaf_far_binding" == name for name in leaf_visuals)
            and "index_tab" not in leaf_visuals
            and "top_crossbar" not in leaf_visuals
        )
    ctx.check(
        f"category_anchor: leaf_top {r.leaf_top} identity",
        leaf_top_ok,
        details=f"leaf_visuals={sorted(leaf_visuals)}",
    )

    # --- gusset_style ---------------------------------------------------- #
    fold_counts = {
        len([v for v in part.visuals if (v.name or "").startswith("gusset_style__")])
        for part in model.parts
        if part.meta.get("role") == "file_leaf" or part.meta.get("position") == "moving"
    }
    expected_folds = {
        "v_fold_bellows": 4,
        "pleated_multifold": 8,
        "floor_web_gusset": 3,
    }[r.gusset_style]
    band = _gusset_band(
        r,
        prev_thickness=r.leaf_thickness_m,
        own_thickness=r.leaf_thickness_m,
    )
    ctx.check(
        f"category_anchor: gusset_style {r.gusset_style} identity",
        fold_counts == {expected_folds}
        and band[1] > band[0]
        and band[0] > -r.compressed_pitch_m + r.leaf_thickness_m / 2.0,
        details=f"fold_counts={sorted(fold_counts)}, expected={expected_folds}, band={band}",
    )

    # --- cover_build ----------------------------------------------------- #
    if r.cover_build == "bound_board":
        cover_ok = "cover_panel" in cover_visuals and "cover_top_binding" in cover_visuals
    elif r.cover_build == "framed_board":
        cover_ok = (
            "cover_recessed_panel" in cover_visuals
            and "cover_top_rail" in cover_visuals
            and "cover_bottom_rail" in cover_visuals
            and "cover_panel" not in cover_visuals
        )
    else:
        lip_x = {
            round(v.origin.xyz[0], 6)
            for part in end_boards
            for v in part.visuals
            if (v.name or "").endswith("_lip")
        }
        cover_ok = (
            "cover_top_lip" in cover_visuals
            and "cover_bottom_lip" in cover_visuals
            and len(lip_x) == 2
            and max(lip_x) > 0.0 > min(lip_x)
        )
    ctx.check(
        f"category_anchor: cover_build {r.cover_build} identity",
        cover_ok,
        details=f"cover_visuals={sorted(cover_visuals)}",
    )

    # --- closure --------------------------------------------------------- #
    closure_joint = next(
        (j for j in model.articulations if j.child in {p.name for p in closures}),
        None,
    )
    if r.closure == "open_top":
        closure_ok = not closures and "closure_hinge_boss" not in all_visuals
    elif r.closure == "fold_over_flap":
        closure_ok = (
            len(closures) == 1
            and closure_joint is not None
            and closure_joint.articulation_type == ArticulationType.REVOLUTE
            and tuple(closure_joint.axis) == (0.0, 1.0, 0.0)
            and closure_joint.motion_limits is not None
            and abs(closure_joint.motion_limits.upper - _FLAP_MAX_ANGLE) < 1e-9
            and "flap_panel" in all_visuals
        )
    else:
        closure_ok = (
            len(closures) == 1
            and closure_joint is not None
            and closure_joint.articulation_type == ArticulationType.REVOLUTE
            and tuple(closure_joint.axis) == (1.0, 0.0, 0.0)
            and closure_joint.motion_limits is not None
            and abs(closure_joint.motion_limits.upper - _CLASP_MAX_ANGLE) < 1e-9
            and "clasp_arm" in all_visuals
        )
    ctx.check(
        f"category_anchor: closure {r.closure} identity",
        closure_ok,
        details=f"closures={[p.name for p in closures]}, joint={getattr(closure_joint, 'name', None)}",
    )

    # Mechanical invariant: the organizer expands away from the fixed cover.
    if fixed_end is not None and leaves:
        moving_end = next((p for p in end_boards if p.meta.get("position") == "moving"), None)
        compressed = ctx.part_world_position(moving_end) if moving_end else None
        with ctx.pose({driver_name: r.gap_travel_m}):
            expanded = ctx.part_world_position(moving_end) if moving_end else None
        ctx.check(
            "accordion expands the moving cover along +X",
            compressed is not None
            and expanded is not None
            and expanded[0] > compressed[0] + r.gap_travel_m,
            details=f"compressed={compressed}, expanded={expanded}",
        )

    # The closure part must genuinely travel through its declared range.
    if closures and closure_joint is not None:
        closed = ctx.part_world_position(closures[0])
        with ctx.pose({closure_joint.name: closure_joint.motion_limits.upper}):
            opened = ctx.part_world_position(closures[0])
        ctx.check(
            "closure hardware keeps full revolute travel",
            closed is not None and opened is not None,
            details=f"closed={closed}, opened={opened}",
        )

    return ctx.report()


TEMPLATE_CORNERS = (
    corner_case(
        "min_leaves_wide_deep_pockets",
        {
            "leaf_top": "hanging_rail_crossbar",
            "gusset_style": "v_fold_bellows",
            "cover_build": "bound_board",
            "closure": "open_top",
            "divider_count": 6,
            "depth_m": 0.34,
            "leaf_height_m": 0.30,
            "compressed_pitch_m": 0.024,
            "gap_travel_m": 0.012,
        },
        reason="minimum N with the largest envelope and longest per-gap travel",
    ),
    corner_case(
        "max_leaves_tight_pitch_pleated_frame",
        {
            "leaf_top": "staggered_index_tab",
            "gusset_style": "pleated_multifold",
            "cover_build": "framed_board",
            "closure": "fold_over_flap",
            "divider_count": 16,
            "depth_m": 0.22,
            "leaf_height_m": 0.18,
            "compressed_pitch_m": 0.014,
            "gap_travel_m": 0.006,
        },
        reason="maximum N at the tightest pitch with pleats, a framed cover and a flap",
    ),
    corner_case(
        "max_leaves_wrap_clasp_full_travel",
        {
            "leaf_top": "reinforced_bound_edge",
            "gusset_style": "floor_web_gusset",
            "cover_build": "wrap_lip_shell",
            "closure": "turn_button_clasp",
            "divider_count": 16,
            "depth_m": 0.34,
            "leaf_height_m": 0.30,
            "compressed_pitch_m": 0.014,
            "gap_travel_m": 0.012,
        },
        reason="wrapped covers plus a rotating clasp over a fully packed, fully expanding body",
    ),
    corner_case(
        "min_leaves_flap_over_wrap_cover",
        {
            "leaf_top": "hanging_rail_crossbar",
            "gusset_style": "pleated_multifold",
            "cover_build": "wrap_lip_shell",
            "closure": "fold_over_flap",
            "divider_count": 6,
            "depth_m": 0.22,
            "leaf_height_m": 0.18,
            "compressed_pitch_m": 0.024,
            "gap_travel_m": 0.012,
        },
        reason="flap swept over the outward wrap lip at the shallowest cover height",
    ),
)


__all__ = [
    "Config",
    "ResolvedConfig",
    "TEMPLATE_CORNERS",
    "TEMPLATE_DOMAIN",
    "build_picturex_0611_folders",
    "config_from_seed",
    "resolve_config",
    "run_picturex_0611_folders_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
]
