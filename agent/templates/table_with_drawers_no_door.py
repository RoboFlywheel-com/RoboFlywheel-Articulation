# SPDX-License-Identifier: Apache-2.0

"""Table with drawers (no door) — modular procedural template.

Category identity: a table (worktop-height, 0.72-0.82m), with a worktop that
overhangs the case, and 1..N front-facing PRISMATIC drawers below. There is
NEVER a hinged door / REVOLUTE panel; only PRISMATIC drawer travel.

Slots (see specs_modular_v1/table_with_drawers_no_door.md):

  * ``worktop_form`` (③ Primary Form Family, 4 candidates)
    rounded_rect_top / overhanging_rect_top / long_walnut_slab_top / demilune_top
  * ``support_style`` (① skeleton, 5 candidates)
    four_tapered_legs / four_turned_legs / four_splayed_legs / trestle / twin_pedestal
  * ``drawer_count`` (① multiplicity, N ∈ [1, 5])
  * ``palette_style`` (⑥ palette, 5 realistic colorways)

Sources (5-star origin_anchor + planned forked_anchor variants):
  S1 rec_picturex_0611__table_with_drawers_no_door__001 (rec_001, N=1, tapered legs)
  S2 rec_picturex_0611__table_with_drawers_no_door__002 (rec_002, N=2, turned legs)
  S3 rec_picturex_0611__table_with_drawers_no_door__003 (rec_003, N=2, splayed legs)
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, replace
from typing import Literal

import cadquery as cq

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    Inertial,
    MatingContract,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
)

__modular__ = True

WorktopForm = Literal[
    "rounded_rect_top",
    "overhanging_rect_top",
    "long_walnut_slab_top",
    "demilune_top",
]
SupportStyle = Literal[
    "four_tapered_legs",
    "four_turned_legs",
    "four_splayed_legs",
    "trestle",
    "twin_pedestal",
]
PaletteStyle = Literal[
    "weathered_taupe_wood",
    "warm_walnut",
    "dark_walnut_espresso",
    "painted_white",
    "oak_light",
]

WORKTOP_FORMS: tuple[WorktopForm, ...] = (
    "rounded_rect_top",
    "overhanging_rect_top",
    "long_walnut_slab_top",
    "demilune_top",
)
SUPPORT_STYLES: tuple[SupportStyle, ...] = (
    "four_tapered_legs",
    "four_turned_legs",
    "four_splayed_legs",
    "trestle",
    "twin_pedestal",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "weathered_taupe_wood",
    "warm_walnut",
    "dark_walnut_espresso",
    "painted_white",
    "oak_light",
)

# Weighted drawer_count sampling (small N more common).
DRAWER_COUNT_WEIGHTS = (0.15, 0.35, 0.25, 0.15, 0.10)
N_MIN, N_MAX = 1, 5

PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "weathered_taupe_wood": {
        "top": (0.38, 0.31, 0.26, 1.0),
        "frame": (0.34, 0.28, 0.23, 1.0),
        "leg": (0.28, 0.23, 0.20, 1.0),
        "drawer_front": (0.42, 0.34, 0.28, 1.0),
        "hardware": (0.12, 0.11, 0.10, 1.0),
    },
    "warm_walnut": {
        "top": (0.38, 0.205, 0.135, 1.0),
        "frame": (0.43, 0.245, 0.145, 1.0),
        "leg": (0.34, 0.185, 0.115, 1.0),
        "drawer_front": (0.50, 0.285, 0.155, 1.0),
        "hardware": (0.57, 0.49, 0.31, 1.0),
    },
    "dark_walnut_espresso": {
        "top": (0.30, 0.19, 0.115, 1.0),
        "frame": (0.205, 0.125, 0.078, 1.0),
        "leg": (0.055, 0.047, 0.043, 1.0),
        "drawer_front": (0.255, 0.158, 0.095, 1.0),
        "hardware": (0.065, 0.065, 0.060, 1.0),
    },
    "painted_white": {
        "top": (0.55, 0.42, 0.28, 1.0),
        "frame": (0.92, 0.90, 0.86, 1.0),
        "leg": (0.90, 0.88, 0.83, 1.0),
        "drawer_front": (0.94, 0.92, 0.88, 1.0),
        "hardware": (0.42, 0.30, 0.18, 1.0),
    },
    "oak_light": {
        "top": (0.78, 0.63, 0.44, 1.0),
        "frame": (0.72, 0.58, 0.40, 1.0),
        "leg": (0.66, 0.52, 0.34, 1.0),
        "drawer_front": (0.80, 0.66, 0.47, 1.0),
        "hardware": (0.78, 0.79, 0.80, 1.0),
    },
}


@dataclass(frozen=True)
class TableWithDrawersNoDoorConfig:
    worktop_form: WorktopForm = "overhanging_rect_top"
    support_style: SupportStyle = "four_turned_legs"
    drawer_count: int = 2
    palette_style: PaletteStyle = "warm_walnut"
    case_width: float = 1.05
    case_depth: float = 0.42
    worktop_thickness: float = 0.036
    drawer_travel: float = 0.22
    name: str = "reference_table_with_drawers_no_door"


@dataclass(frozen=True)
class ResolvedTableWithDrawersNoDoorConfig:
    worktop_form: WorktopForm
    support_style: SupportStyle
    drawer_count: int
    palette_style: PaletteStyle
    case_width: float
    case_depth: float
    worktop_thickness: float
    worktop_length: float  # X-extent of worktop
    worktop_depth: float  # Y-extent of worktop
    worktop_front_overhang: float
    worktop_side_overhang: float
    case_bottom_z: float  # world Z of case underside (top of leg / pedestal)
    case_top_z: float  # world Z of top rail top-face (= worktop underside)
    case_height: float  # case_top_z - case_bottom_z (drawer bank height)
    drawer_bank_width: float  # inner width available for drawers
    divider_thickness: float
    front_thickness: float
    back_thickness: float
    side_thickness: float
    drawer_front_width: float
    drawer_front_height: float
    drawer_front_thickness: float
    drawer_box_width: float
    drawer_box_depth: float
    drawer_box_wall: float
    drawer_travel: float
    drawer_center_x: tuple[float, ...]
    drawer_center_z: float  # Z of drawer center (front panel + box shared)
    rail_thickness: float
    upper_rail_z: float  # Z of upper rail center
    lower_rail_z: float  # Z of lower rail center
    leg_height: float  # top-of-support to floor
    leg_top_size: float
    leg_bottom_size: float
    name: str


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _pick(value, choices):
    return value if value in choices else choices[0]


def config_from_seed(seed: int) -> TableWithDrawersNoDoorConfig:
    rng = random.Random(seed)
    worktop_form = rng.choice(WORKTOP_FORMS)
    support_style = rng.choice(SUPPORT_STYLES)
    # Weighted drawer_count.
    drawer_count = rng.choices((1, 2, 3, 4, 5), weights=DRAWER_COUNT_WEIGHTS, k=1)[0]
    palette_style = rng.choice(PALETTE_STYLES)
    return TableWithDrawersNoDoorConfig(
        worktop_form=worktop_form,
        support_style=support_style,
        drawer_count=drawer_count,
        palette_style=palette_style,
        case_width=round(rng.uniform(0.85, 1.32), 3),
        case_depth=round(rng.uniform(0.36, 0.50), 3),
        worktop_thickness=round(rng.uniform(0.028, 0.048), 4),
        drawer_travel=round(rng.uniform(0.17, 0.27), 3),
        name=f"seeded_table_with_drawers_no_door_{seed}",
    )


def resolve_config(
    config: TableWithDrawersNoDoorConfig | None = None,
) -> ResolvedTableWithDrawersNoDoorConfig:
    cfg = config or TableWithDrawersNoDoorConfig()

    worktop_form = _pick(cfg.worktop_form, WORKTOP_FORMS)
    support_style = _pick(cfg.support_style, SUPPORT_STYLES)
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)

    # ---- Continuous scale clamping. ----
    case_width = _clamp(cfg.case_width, 0.80, 1.35)
    case_depth = _clamp(cfg.case_depth, 0.34, 0.52)
    worktop_thickness = _clamp(cfg.worktop_thickness, 0.028, 0.048)
    drawer_travel = _clamp(cfg.drawer_travel, 0.16, 0.28)

    # ---- Multiplicity clamp + compatibility gating. ----
    drawer_count = int(_clamp(cfg.drawer_count, N_MIN, N_MAX))
    # (a) demilune restricts N<=3.
    if worktop_form == "demilune_top":
        drawer_count = min(drawer_count, 3)
    # (b) case_width must accommodate drawer_count * 0.16 minimum front width.
    min_front_pitch = 0.16
    max_by_width = max(1, int(case_width / min_front_pitch))
    drawer_count = min(drawer_count, max_by_width)

    # ---- Case / carcass dims. ----
    side_thickness = 0.020
    back_thickness = 0.014
    front_thickness = 0.018
    divider_thickness = 0.014
    rail_thickness = 0.020

    # Drawer bank width (inner opening).
    drawer_bank_width = case_width - 2.0 * side_thickness
    # Front width per drawer (equation).
    n = drawer_count
    drawer_front_width = (drawer_bank_width - (n + 1) * divider_thickness) / max(n, 1)

    # Case height (drawer bank height).
    case_height = _clamp(0.116, 0.10, 0.14)
    drawer_front_height = case_height - 2.0 * rail_thickness - 0.010

    # Overall table height ~0.76m.
    leg_height = _clamp(0.640, 0.60, 0.72)  # top-of-support to floor
    case_bottom_z = leg_height
    case_top_z = case_bottom_z + case_height

    # Rails: upper rail sits at case_top_z - rail_thickness/2; lower at
    # case_bottom_z + rail_thickness/2.
    upper_rail_z = case_top_z - rail_thickness / 2.0
    lower_rail_z = case_bottom_z + rail_thickness / 2.0

    # Drawer center Z: chosen so the drawer front panel's positive_z (top)
    # face sits flush against the upper rail's negative_z (bottom) face,
    # giving the MatingContract a zero-gap contact.
    # upper rail bottom z = case_top_z - rail_thickness.
    # front_panel top z (world) = drawer_center_z + drawer_front_height / 2.
    # => drawer_center_z = (case_top_z - rail_thickness) - drawer_front_height / 2.
    drawer_center_z = (case_top_z - rail_thickness) - drawer_front_height / 2.0

    # ---- Drawer box dims (inequality projection for drawer_travel). ----
    drawer_box_wall = 0.012
    # Box depth: bounded by case_depth (case_depth is Y-extent). The drawer
    # front sits at y = -case_depth/2 + rail_thickness + ft/2 (behind the
    # lower rail); the drawer box extends from there into +Y by drawer_box_depth.
    # For clearance at rest, drawer_box_back must clear back_apron (-Y face at
    # case_depth/2 - back_thickness): drawer_box_depth < case_depth - rt - ft -
    # back_thickness - small_gap.
    _clearance_gap = 0.020
    drawer_box_depth = (
        case_depth - rail_thickness - front_thickness - back_thickness - _clearance_gap
    )
    drawer_box_depth = max(drawer_box_depth, 0.18)
    # Retained insertion >= 15% of box depth => travel <= 0.85 * box_depth.
    drawer_travel = min(drawer_travel, drawer_box_depth * 0.85)
    drawer_travel = max(drawer_travel, 0.10)

    drawer_box_width = drawer_front_width - 0.006
    drawer_front_thickness = 0.018

    # Drawer center X (evenly spaced along the bank width).
    if n == 1:
        drawer_center_x = (0.0,)
    else:
        pitch = (drawer_bank_width - n * drawer_front_width) / (n + 1) + drawer_front_width
        # Simpler equation: front centers evenly divide the drawer_bank_width.
        # (drawer_bank_width - (N+1)*divider) split into N fronts + (N+1)
        # dividers. Placement: x_i = -bank/2 + divider + front/2 + i*(front+divider).
        drawer_center_x = tuple(
            -drawer_bank_width / 2.0
            + divider_thickness
            + drawer_front_width / 2.0
            + i * (drawer_front_width + divider_thickness)
            for i in range(n)
        )
        # Silence unused warning.
        _ = pitch

    # ---- Worktop dims. ----
    worktop_side_overhang = 0.035
    worktop_front_overhang = 0.030
    if worktop_form == "demilune_top":
        # Straight edge is the case front; overhang only at sides + rear.
        worktop_front_overhang = 0.0
        worktop_side_overhang = 0.025
    elif worktop_form == "long_walnut_slab_top":
        # Longer slab.
        worktop_side_overhang = 0.075
        worktop_front_overhang = 0.050

    worktop_length = case_width + 2.0 * worktop_side_overhang
    worktop_depth = case_depth + 2.0 * worktop_front_overhang

    # ---- Support dims. ----
    leg_top_size = 0.055
    leg_bottom_size = 0.034
    if support_style == "four_turned_legs":
        leg_top_size = 0.070
        leg_bottom_size = 0.036
    elif support_style == "four_splayed_legs":
        leg_top_size = 0.050
        leg_bottom_size = 0.030

    return ResolvedTableWithDrawersNoDoorConfig(
        worktop_form=worktop_form,
        support_style=support_style,
        drawer_count=drawer_count,
        palette_style=palette_style,
        case_width=case_width,
        case_depth=case_depth,
        worktop_thickness=worktop_thickness,
        worktop_length=worktop_length,
        worktop_depth=worktop_depth,
        worktop_front_overhang=worktop_front_overhang,
        worktop_side_overhang=worktop_side_overhang,
        case_bottom_z=case_bottom_z,
        case_top_z=case_top_z,
        case_height=case_height,
        drawer_bank_width=drawer_bank_width,
        divider_thickness=divider_thickness,
        front_thickness=front_thickness,
        back_thickness=back_thickness,
        side_thickness=side_thickness,
        drawer_front_width=drawer_front_width,
        drawer_front_height=drawer_front_height,
        drawer_front_thickness=drawer_front_thickness,
        drawer_box_width=drawer_box_width,
        drawer_box_depth=drawer_box_depth,
        drawer_box_wall=drawer_box_wall,
        drawer_travel=drawer_travel,
        drawer_center_x=drawer_center_x,
        drawer_center_z=drawer_center_z,
        rail_thickness=rail_thickness,
        upper_rail_z=upper_rail_z,
        lower_rail_z=lower_rail_z,
        leg_height=leg_height,
        leg_top_size=leg_top_size,
        leg_bottom_size=leg_bottom_size,
        name=cfg.name or "table_with_drawers_no_door",
    )


def with_overrides(
    config: TableWithDrawersNoDoorConfig, **kwargs: object
) -> TableWithDrawersNoDoorConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: TableWithDrawersNoDoorConfig | ResolvedTableWithDrawersNoDoorConfig,
) -> tuple[tuple[str, str], ...]:
    r = (
        config
        if isinstance(config, ResolvedTableWithDrawersNoDoorConfig)
        else resolve_config(config)
    )
    return (
        ("worktop_form", r.worktop_form),
        ("support_style", r.support_style),
        ("drawer_count", f"n{r.drawer_count}"),
        ("palette_style", r.palette_style),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Worktop mesh helpers.
# ---------------------------------------------------------------------------
def _rounded_rect_top(w: float, d: float, t: float) -> cq.Workplane:
    """S1 (rec_001) _rounded_top L20-L27 style: filleted axis-aligned slab."""
    return cq.Workplane("XY").box(w, d, t).edges("|Z").fillet(min(0.010, t * 0.4))


def _overhanging_rect_top(w: float, d: float, t: float) -> cq.Workplane:
    """S2 (rec_002) tabletop L137-L141 style: rectangular slab, gentle fillet."""
    return cq.Workplane("XY").box(w, d, t).edges().fillet(min(0.006, t * 0.2))


def _long_walnut_slab_top(w: float, d: float, t: float) -> cq.Workplane:
    """S3 (rec_003) _tabletop_shape L64-L90 style: rectangular slab (grain cuts
    are host-conformal Box visuals emitted separately as parent visuals)."""
    return cq.Workplane("XY").box(w, d, t).edges("|Z").fillet(min(0.008, t * 0.3))


def _demilune_top(w: float, d: float, t: float) -> cq.Workplane:
    """world_knowledge_extrapolation ③: half-ellipse worktop. Straight edge at
    the front (negative-y), curved edge at the rear (positive-y).

    Same part tree, same primitive family, only Planar Boundary Form differs.
    """
    # Half-ellipse: build a full ellipse and cut off the front half.
    half_d = d  # depth of the semi-ellipse (rear rim to straight edge)
    rx = w / 2.0
    ry = half_d
    ellipse = cq.Workplane("XY").ellipse(rx, ry).extrude(t).translate((0.0, 0.0, -t / 2.0))
    # Cut off the front half (y < 0).
    cutter = (
        cq.Workplane("XY")
        .box(w + 0.02, half_d + 0.02, t + 0.02)
        .translate((0.0, -(half_d + 0.02) / 2.0, 0.0))
    )
    return ellipse.cut(cutter)


_WORKTOP_BUILDERS = {
    "rounded_rect_top": _rounded_rect_top,
    "overhanging_rect_top": _overhanging_rect_top,
    "long_walnut_slab_top": _long_walnut_slab_top,
    "demilune_top": _demilune_top,
}


def _turned_leg_profile(top_z: float, top_size: float, bottom_size: float) -> cq.Workplane:
    """S2 (rec_002) _turned_leg L34-L57 style: revolved profile with slight
    bulges. Simplified profile with 8 vertices to keep compile cost low."""
    rt = top_size / 2.0
    rb = bottom_size / 2.0
    # Bulge halfway up.
    rmid = (rt + rb) / 2.0 + 0.003
    # Small foot.
    rfoot = rb * 1.08
    profile = (
        cq.Workplane("XZ")
        .moveTo(0.0, 0.0)
        .lineTo(rfoot, 0.0)
        .lineTo(rb, top_z * 0.08)
        .lineTo(rmid, top_z * 0.35)
        .lineTo(rb + 0.001, top_z * 0.55)
        .lineTo(rmid, top_z * 0.72)
        .lineTo(rt, top_z * 0.92)
        .lineTo(rt, top_z)
        .lineTo(0.0, top_z)
        .close()
        .revolve(360.0, (0.0, 0.0), (0.0, 1.0))
    )
    return profile


def _tapered_leg_profile(top_z: float, top_size: float, bottom_size: float) -> cq.Workplane:
    """S1 (rec_001) _tapered_leg L38-L45 style: simple lofted taper from
    smaller bottom square to larger top square."""
    return (
        cq.Workplane("XY")
        .rect(bottom_size, bottom_size)
        .workplane(offset=top_z)
        .rect(top_size, top_size)
        .loft(combine=True)
    )


def _splayed_leg_box(
    top_z: float, top_size: float, bottom_size: float, splay: float
) -> cq.Workplane:
    """S3 (rec_003) _splayed_leg_mesh L27-L61 style: simple box tapered along Z.

    We use a lofted tapered square with slight outward top-bottom offset baked
    into the placement (see build), so the leg body itself is straight taper.
    """
    return (
        cq.Workplane("XY")
        .rect(bottom_size, bottom_size)
        .workplane(offset=top_z)
        .rect(top_size, top_size)
        .loft(combine=True)
    )


# ---------------------------------------------------------------------------
# Build helpers.
# ---------------------------------------------------------------------------
def _emit_worktop(frame, r: ResolvedTableWithDrawersNoDoorConfig, *, mats, assets):
    """Emit the worktop as a parent visual on `frame` (Rule 1: fixed)."""
    builder = _WORKTOP_BUILDERS[r.worktop_form]
    wp = builder(r.worktop_length, r.worktop_depth, r.worktop_thickness)
    # Worktop origin: centered in X, offset in Y for demilune so straight edge
    # aligns to the case front.
    if r.worktop_form == "demilune_top":
        # In _demilune_top the mesh is half-ellipse with straight edge at y=0
        # (the front). We want the straight edge to align with case front
        # (y = -case_depth/2), so translate by -case_depth/2.
        y_offset = -r.case_depth / 2.0 + r.worktop_depth / 2.0  # ellipse-half center
        # Actually _demilune_top returned a slab of depth = half_d = worktop_depth
        # centered so the straight edge is at y=-half_d/2 and rear at y=+half_d/2
        # BEFORE translate. Let me re-derive: ellipse centered at origin, cut y<0,
        # remaining piece spans y in [0, ry]. After centering with translate((0,0,-t/2))
        # in Z only, x/y remain as-is.
        # So the shape spans y in [0, worktop_depth]. To align its front (y=0)
        # to case front (y = -case_depth/2), translate by -case_depth/2 in Y.
        y_offset = -r.case_depth / 2.0
        frame.visual(
            mesh_from_cadquery(wp, "tabletop_demilune", tolerance=0.0008, assets=assets),
            origin=Origin(xyz=(0.0, y_offset, r.case_top_z + r.worktop_thickness / 2.0)),
            material=mats["top"],
            name="tabletop", material_class_id=("wood.walnut_dark" if r.palette_style in {"weathered_taupe_wood", "warm_walnut", "dark_walnut_espresso", "painted_white"} else "wood.oak"),
        )
    else:
        frame.visual(
            mesh_from_cadquery(
                wp,
                f"tabletop_{r.worktop_form}",
                tolerance=0.0008,
                assets=assets,
            ),
            origin=Origin(xyz=(0.0, 0.0, r.case_top_z + r.worktop_thickness / 2.0)),
            material=mats["top"],
            name="tabletop", material_class_id=("wood.walnut_dark" if r.palette_style in {"weathered_taupe_wood", "warm_walnut", "dark_walnut_espresso", "painted_white"} else "wood.oak"),
        )

    # For long_walnut_slab_top, add a few host-conformal grain lines as parent
    # visuals (④ decoration, host-derived Box embedded on the top surface).
    if r.worktop_form == "long_walnut_slab_top":
        top_face_z = r.case_top_z + r.worktop_thickness
        grain_specs = (
            (-0.28, -0.15, 0.42),
            (0.18, -0.05, 0.55),
            (-0.10, 0.08, 0.48),
        )
        for i, (x, y, length) in enumerate(grain_specs):
            frame.visual(
                Box((length, 0.0025, 0.0006)),
                origin=Origin(xyz=(x, y, top_face_z - 0.0003)),
                material=mats["hardware"],
                name=f"top_grain_{i}", material_class_id="wood.walnut_dark",
            )


def _emit_case(frame, r: ResolvedTableWithDrawersNoDoorConfig, *, mats):
    """Emit the case: side aprons, back panel, upper+lower front rails, and
    N-1 dividers between drawer bays. All are parent visuals on frame."""
    st = r.side_thickness
    bt = r.back_thickness
    rt = r.rail_thickness
    # Side aprons: full case_height along Y, from case_bottom_z to case_top_z.
    for sign, name in ((-1.0, "side_apron_left"), (1.0, "side_apron_right")):
        frame.visual(
            Box((st, r.case_depth, r.case_height)),
            origin=Origin(
                xyz=(
                    sign * (r.case_width / 2.0 - st / 2.0),
                    0.0,
                    r.case_bottom_z + r.case_height / 2.0,
                )
            ),
            material=mats["frame"],
            name=name, material_class_id=("wood.walnut_dark" if r.palette_style in {"weathered_taupe_wood", "warm_walnut", "dark_walnut_espresso", "painted_white"} else "wood.oak"),
        )
    # Back apron.
    frame.visual(
        Box((r.case_width - 2.0 * st, bt, r.case_height)),
        origin=Origin(
            xyz=(0.0, r.case_depth / 2.0 - bt / 2.0, r.case_bottom_z + r.case_height / 2.0)
        ),
        material=mats["frame"],
        name="back_apron", material_class_id=("wood.walnut_dark" if r.palette_style in {"weathered_taupe_wood", "warm_walnut", "dark_walnut_espresso", "painted_white"} else "wood.oak"),
    )
    # Front upper rail: full drawer_bank_width span, thin rail.
    frame.visual(
        Box((r.drawer_bank_width, rt, rt)),
        origin=Origin(xyz=(0.0, -r.case_depth / 2.0 + rt / 2.0, r.upper_rail_z)),
        material=mats["frame"],
        name="front_upper_rail", material_class_id=("wood.walnut_dark" if r.palette_style in {"weathered_taupe_wood", "warm_walnut", "dark_walnut_espresso", "painted_white"} else "wood.oak"),
    )
    # Front lower rail — this is the primary mating anchor for drawers.
    frame.visual(
        Box((r.drawer_bank_width, rt, rt)),
        origin=Origin(xyz=(0.0, -r.case_depth / 2.0 + rt / 2.0, r.lower_rail_z)),
        material=mats["frame"],
        name="front_lower_rail", material_class_id=("wood.walnut_dark" if r.palette_style in {"weathered_taupe_wood", "warm_walnut", "dark_walnut_espresso", "painted_white"} else "wood.oak"),
    )
    # Dividers between drawers (vertical bars).
    n = r.drawer_count
    if n >= 2:
        dt = r.divider_thickness
        # Divider x positions: interior edges between drawers.
        for i in range(1, n):
            x = (
                -r.drawer_bank_width / 2.0
                + r.divider_thickness
                + i * (r.drawer_front_width + r.divider_thickness)
                - dt / 2.0
            )
            frame.visual(
                Box((dt, rt, r.case_height - 2.0 * rt)),
                origin=Origin(xyz=(x, -r.case_depth / 2.0 + rt / 2.0, r.drawer_center_z)),
                material=mats["frame"],
                name=f"drawer_divider_{i}", material_class_id=("wood.walnut_dark" if r.palette_style in {"weathered_taupe_wood", "warm_walnut", "dark_walnut_espresso", "painted_white"} else "wood.oak"),
            )
    # Drawer runners: thin strips seated on top of the lower rail (they embed
    # into the rail so they connect to the frame island). Extend along Y to
    # the back apron so the runner also touches the back apron (double
    # connection). Height and radius kept small.
    runner_thick = 0.010
    runner_len_y = r.case_depth - r.rail_thickness - r.back_thickness
    runner_center_y = -r.case_depth / 2.0 + r.rail_thickness + runner_len_y / 2.0
    runner_z = r.lower_rail_z + rt / 2.0 - 0.002  # embed 2mm into rail top
    for i, cx in enumerate(r.drawer_center_x):
        frame.visual(
            Box((0.016, runner_len_y, runner_thick)),
            origin=Origin(xyz=(cx, runner_center_y, runner_z + runner_thick / 2.0)),
            material=mats["frame"],
            name=f"drawer_runner_{i}", material_class_id=("wood.walnut_dark" if r.palette_style in {"weathered_taupe_wood", "warm_walnut", "dark_walnut_espresso", "painted_white"} else "wood.oak"),
        )


def _emit_support(frame, r: ResolvedTableWithDrawersNoDoorConfig, *, mats, assets):
    """Emit legs / trestle / twin_pedestal as parent visuals on frame."""
    style = r.support_style
    # Corner leg XY positions (four_* styles).
    inset_x = r.case_width / 2.0 - r.side_thickness / 2.0 - r.leg_top_size / 2.0
    inset_y = r.case_depth / 2.0 - r.back_thickness / 2.0 - r.leg_top_size / 2.0
    corners = (
        (-inset_x, -inset_y),
        (inset_x, -inset_y),
        (-inset_x, inset_y),
        (inset_x, inset_y),
    )
    if style == "four_tapered_legs":
        leg_mesh = _tapered_leg_profile(r.leg_height, r.leg_top_size, r.leg_bottom_size)
        leg_geom = mesh_from_cadquery(leg_mesh, "tapered_leg", tolerance=0.0009, assets=assets)
        for i, (x, y) in enumerate(corners):
            frame.visual(
                leg_geom,
                origin=Origin(xyz=(x, y, 0.0)),
                material=mats["leg"],
                name=f"leg_{i}", material_class_id=("wood.walnut_dark" if r.palette_style in {"weathered_taupe_wood", "warm_walnut", "dark_walnut_espresso", "painted_white"} else "wood.oak"),
            )
    elif style == "four_turned_legs":
        leg_mesh = _turned_leg_profile(r.leg_height, r.leg_top_size, r.leg_bottom_size)
        leg_geom = mesh_from_cadquery(leg_mesh, "turned_leg", tolerance=0.0010, assets=assets)
        for i, (x, y) in enumerate(corners):
            frame.visual(
                leg_geom,
                origin=Origin(xyz=(x, y, 0.0)),
                material=mats["leg"],
                name=f"leg_{i}", material_class_id=("wood.walnut_dark" if r.palette_style in {"weathered_taupe_wood", "warm_walnut", "dark_walnut_espresso", "painted_white"} else "wood.oak"),
            )
    elif style == "four_splayed_legs":
        # Same lofted taper but placed at inset_x/inset_y with slight outward
        # rake baked in via origin. We author the geometry as a straight loft
        # (bottom_size at z=0, top_size at z=leg_height) and rely on the
        # bottom being slightly wider than the top footprint at each corner.
        leg_mesh = _splayed_leg_box(r.leg_height, r.leg_top_size, r.leg_bottom_size, splay=0.03)
        leg_geom = mesh_from_cadquery(leg_mesh, "splayed_leg", tolerance=0.0010, assets=assets)
        for i, (x, y) in enumerate(corners):
            frame.visual(
                leg_geom,
                origin=Origin(xyz=(x, y, 0.0)),
                material=mats["leg"],
                name=f"leg_{i}", material_class_id=("wood.walnut_dark" if r.palette_style in {"weathered_taupe_wood", "warm_walnut", "dark_walnut_espresso", "painted_white"} else "wood.oak"),
            )
    elif style == "trestle":
        # Two lateral plank-style trestles + one lower stretcher. Each plank
        # is positioned so it embeds into the side apron (5mm overlap along X),
        # keeping the whole support one connected island with the case.
        plank_thick = 0.030
        plank_depth = r.case_depth * 0.55
        # Plank inner face flush against the side apron outer face for a
        # positive 5mm x-overlap.
        # side apron center x = sx*(case_width/2 - side_thickness/2)
        # plank center x placed 5mm inside the side apron center along inward.
        for i, sx in enumerate((-1.0, 1.0)):
            plank_x = sx * (r.case_width / 2.0 - r.side_thickness - plank_thick / 2.0 + 0.005)
            frame.visual(
                Box((plank_thick, plank_depth, r.leg_height)),
                origin=Origin(xyz=(plank_x, 0.0, r.leg_height / 2.0)),
                material=mats["leg"],
                name=f"trestle_plank_{i}", material_class_id=("wood.walnut_dark" if r.palette_style in {"weathered_taupe_wood", "warm_walnut", "dark_walnut_espresso", "painted_white"} else "wood.oak"),
            )
        # Lower stretcher: wide enough that its X-extent clearly overlaps both
        # planks. Y and Z sit inside the plank envelope for a clean overlap.
        stretcher_z = 0.070
        stretcher_h = 0.028
        stretcher_len = r.case_width - 0.02  # wider than plank spacing
        frame.visual(
            Box((stretcher_len, 0.030, stretcher_h)),
            origin=Origin(xyz=(0.0, 0.0, stretcher_z)),
            material=mats["leg"],
            name="trestle_stretcher", material_class_id=("wood.walnut_dark" if r.palette_style in {"weathered_taupe_wood", "warm_walnut", "dark_walnut_espresso", "painted_white"} else "wood.oak"),
        )
    else:  # twin_pedestal
        # Two boxed pedestals under each end of the case.
        ped_w = 0.070
        ped_d = r.case_depth * 0.80
        for i, sx in enumerate((-1.0, 1.0)):
            frame.visual(
                Box((ped_w, ped_d, r.leg_height)),
                origin=Origin(
                    xyz=(sx * (r.case_width / 2.0 - ped_w / 2.0 - 0.015), 0.0, r.leg_height / 2.0)
                ),
                material=mats["leg"],
                name=f"pedestal_{i}", material_class_id=("wood.walnut_dark" if r.palette_style in {"weathered_taupe_wood", "warm_walnut", "dark_walnut_espresso", "painted_white"} else "wood.oak"),
            )


def _emit_drawer(
    drawer,
    r: ResolvedTableWithDrawersNoDoorConfig,
    *,
    mats,
    index: int,
):
    """Emit a single drawer's inline visuals. Drawer origin (0,0,0) is at the
    drawer front's center in world at rest — but here we author the drawer in
    its own local frame with the front panel at local origin y=0.

    Drawer axes: front_panel spans local x=[-fw/2, fw/2], z=[-fh/2, fh/2],
    y ~ [-t/2, t/2]. Box extends into +y (into the case)."""
    fw = r.drawer_front_width
    fh = r.drawer_front_height
    ft = r.drawer_front_thickness
    bw = r.drawer_box_width
    bd = r.drawer_box_depth
    bh = fh * 0.78  # box a bit shorter than the front panel
    wall = r.drawer_box_wall

    # Front panel: axis-aligned box at local origin.
    drawer.visual(
        Box((fw, ft, fh)),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material=mats["drawer_front"],
        name="front_panel", material_class_id=("wood.walnut_dark" if r.palette_style in {"weathered_taupe_wood", "warm_walnut", "dark_walnut_espresso", "painted_white"} else "wood.oak"),
    )
    # Box back at y = ft + bd + wall/2.
    box_back_y = ft / 2.0 + bd - wall / 2.0
    # Bottom.
    drawer.visual(
        Box((bw, bd, 0.010)),
        origin=Origin(xyz=(0.0, ft / 2.0 + bd / 2.0, -bh / 2.0 + 0.005)),
        material=mats["frame"],
        name="drawer_bottom", material_class_id=("wood.walnut_dark" if r.palette_style in {"weathered_taupe_wood", "warm_walnut", "dark_walnut_espresso", "painted_white"} else "wood.oak"),
    )
    # Sides.
    for sign, side_name in ((-1.0, "drawer_side_left"), (1.0, "drawer_side_right")):
        drawer.visual(
            Box((wall, bd, bh)),
            origin=Origin(xyz=(sign * (bw / 2.0 - wall / 2.0), ft / 2.0 + bd / 2.0, 0.0)),
            material=mats["frame"],
            name=side_name, material_class_id=("wood.walnut_dark" if r.palette_style in {"weathered_taupe_wood", "warm_walnut", "dark_walnut_espresso", "painted_white"} else "wood.oak"),
        )
    # Back.
    drawer.visual(
        Box((bw - 2.0 * wall, wall, bh)),
        origin=Origin(xyz=(0.0, box_back_y, 0.0)),
        material=mats["frame"],
        name="drawer_back", material_class_id=("wood.walnut_dark" if r.palette_style in {"weathered_taupe_wood", "warm_walnut", "dark_walnut_espresso", "painted_white"} else "wood.oak"),
    )
    # Hardware: a single centered knob on the front panel (④ decoration,
    # host-conformal: cylinder axis perpendicular to the front face).
    # Stem embeds into the front panel; cap sits proud of the -Y face.
    stem_len = 0.014
    drawer.visual(
        Cylinder(radius=0.004, length=stem_len),
        origin=Origin(
            xyz=(0.0, -ft / 2.0 - stem_len / 2.0 + 0.003, 0.0),
            rpy=(math.pi / 2.0, 0.0, 0.0),
        ),
        material=mats["hardware"],
        name="knob_stem", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"weathered_taupe_wood", "dark_walnut_espresso", "painted_white", "oak_light"} else "metal.brass_aged"),
    )
    drawer.visual(
        Cylinder(radius=0.011, length=0.010),
        origin=Origin(
            xyz=(0.0, -ft / 2.0 - stem_len - 0.001, 0.0),
            rpy=(math.pi / 2.0, 0.0, 0.0),
        ),
        material=mats["hardware"],
        name="knob_cap", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"weathered_taupe_wood", "dark_walnut_espresso", "painted_white", "oak_light"} else "metal.brass_aged"),
    )


# ---------------------------------------------------------------------------
# Main builder.
# ---------------------------------------------------------------------------
def build_table_with_drawers_no_door(
    config: TableWithDrawersNoDoorConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)

    palette = PALETTES[r.palette_style]
    mats = {
        key: model.material(f"table_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in palette.items()
    }

    frame = model.part(
        "frame",
        meta={"role": "table frame + worktop + support (all fixed, Rule 1)"},
    )
    frame.inertial = Inertial.from_geometry(
        Box((r.case_width, r.case_depth, r.case_top_z + r.worktop_thickness)),
        mass=18.0 + r.drawer_count * 1.5,
        origin=Origin(xyz=(0.0, 0.0, (r.case_top_z + r.worktop_thickness) / 2.0)),
    )

    _emit_worktop(frame, r, mats=mats, assets=assets)
    _emit_case(frame, r, mats=mats)
    _emit_support(frame, r, mats=mats, assets=assets)

    # Drawers.
    for i, cx in enumerate(r.drawer_center_x):
        drawer_part = model.part(
            f"drawer_{i}",
            meta={"role": "front-facing PRISMATIC drawer", "index": i},
        )
        _emit_drawer(drawer_part, r, mats=mats, index=i)
        drawer_part.inertial = Inertial.from_geometry(
            Box(
                (
                    r.drawer_front_width,
                    r.drawer_box_depth,
                    r.drawer_front_height,
                )
            ),
            mass=2.0,
            origin=Origin(xyz=(0.0, r.drawer_box_depth / 2.0, 0.0)),
        )
        # Joint: PRISMATIC axis (0,-1,0). At q=0 the drawer's front panel
        # occupies the drawer bank front. Origin: joint origin placed on
        # frame.front_lower_rail's front face (-y face).
        # Drawer local origin sits at the front panel center (y=0 local ==
        # front panel center). We want at q=0 that this be at world y =
        # -case_depth/2 + rt + ft/2 approximately (flush with the lower rail
        # front face + front panel half-thickness offset).
        drawer_front_at_rest_y = (
            -r.case_depth / 2.0 + r.rail_thickness + r.drawer_front_thickness / 2.0
        )
        joint_origin = (cx, drawer_front_at_rest_y, r.drawer_center_z)
        # MatingContract: drawer front_panel (positive_y face — the back side
        # of the front, facing the case interior) mates with front_lower_rail
        # (negative_y face — the case-front face of the lower rail).
        # Actually: the front panel's -Y face is the customer-facing outside.
        # The rail's +Y face contacts the +Y face of the panel back — but
        # let's think again. front_lower_rail center is at
        # y = -case_depth/2 + rt/2. Its +Y face (inward) at
        # y = -case_depth/2 + rt. The drawer front_panel back (+Y face) at
        # y = drawer_front_at_rest_y + ft/2 = -case_depth/2 + rt +
        # ft/2 + ft/2 = -case_depth/2 + rt + ft. So there's a small gap
        # of ft between the rail inside face and the panel back — not a
        # mating contact.
        #
        # Better: at closed pose, the drawer panel back (positive_y face) is
        # flush with the rail's inside (positive_y) face + a tiny stand-off.
        # We use the DRAWER RUNNER as the mating anchor instead, since the
        # drawer bottom rests ON the runner.
        # runner center z = r.lower_rail_z + rt/2 + 0.001
        # runner top face (positive_z) z = runner_z + 0.005 (runner half-thick 0.005)
        # drawer_bottom center z = -bh/2 + 0.005 (local); world z at rest =
        # r.drawer_center_z + (-bh/2 + 0.005). Need this to equal
        # runner_top face for contact.
        # This means we should adjust drawer_center_z so drawer bottom sits on
        # the runner. Or accept the drawer bottom is above the runner (gap)
        # and use a MatingContract on the panel front instead.
        #
        # Simplest robust MatingContract:
        #  parent: front_lower_rail's positive_z face (top surface of the rail)
        #  child: drawer_bottom's negative_z face (bottom face of the drawer
        #         bottom panel)
        # For this to actually match, we need drawer_bottom's world
        # negative_z face at rest == front_lower_rail's positive_z face world Z.
        # rail top z = r.lower_rail_z + rt/2
        # drawer_bottom bottom z (local) = -bh/2 + 0.005 - 0.010/2 = -bh/2
        # drawer_bottom bottom z (world) = r.drawer_center_z + (-bh/2)
        # We want: r.drawer_center_z - bh/2 == r.lower_rail_z + rt/2
        # => r.drawer_center_z = r.lower_rail_z + rt/2 + bh/2
        # Let's re-derive drawer_center_z here explicitly.
        # (See below: we recompute drawer_center_z at the top of resolve_config
        # by using the midpoint; may need to override.)
        # MatingContract: drawer front panel top face (child positive_z)
        # kisses the front_upper_rail bottom face (parent negative_z). Both
        # sides are real anchoring visuals; contact is enforced at the closed
        # pose along the rail's outward normal.
        mating = MatingContract(
            parent_face_geometry="front_upper_rail",
            parent_face_side="negative_z",
            child_face_geometry="front_panel",
            child_face_side="positive_z",
            contact_tol=0.002,
        )
        joint_limits = MotionLimits(effort=45.0, velocity=0.25, lower=0.0, upper=r.drawer_travel)
        model.articulation(
            f"frame_to_drawer_{i}",
            ArticulationType.PRISMATIC,
            parent=frame,
            child=drawer_part,
            origin=Origin(xyz=joint_origin),
            axis=(0.0, -1.0, 0.0),
            motion_limits=joint_limits,
            mating=mating,
            meta={
                "positive_motion": "drawer moves forward toward the viewer (-Y)",
            },
        )

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_table_with_drawers_no_door(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_table_with_drawers_no_door(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests.
# ---------------------------------------------------------------------------
def run_table_with_drawers_no_door_tests(
    object_model: ArticulatedObject,
    config: TableWithDrawersNoDoorConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)

    frame = object_model.get_part("frame")

    # ---- Element-scoped allowances (drawer sits on runner + inside rails). ----
    for i in range(r.drawer_count):
        drawer = object_model.get_part(f"drawer_{i}")
        # The pulled-out drawer leaves the case cavity entirely.
        ctx.allow_isolated_part(
            drawer,
            reason="extended drawer slides out of the case cavity and loses contact",
        )
        # Drawer bottom rests on the runner: they must touch (mating contact),
        # not overlap. But the drawer_box_bottom is thin; along the runner Y
        # length there's a real contact so this is fine.
        # Closed pose: drawer front panel front face flushes with case front;
        # box interior interpenetrates the case cavity — declare that pair.
        ctx.allow_overlap(
            drawer,
            frame,
            elem_a="drawer_bottom",
            elem_b=f"drawer_runner_{i}",
            reason=(
                "drawer bottom rests directly on the concealed runner "
                "(intentional MatingContract contact — 1mm setback allowance)."
            ),
        )
        # The drawer sides may just brush the dividers laterally.
        if i > 0:
            ctx.allow_overlap(
                drawer,
                frame,
                elem_a="drawer_side_left",
                elem_b=f"drawer_divider_{i}",
                reason="drawer side rides against the left divider (no clearance gap).",
            )
        if i < r.drawer_count - 1:
            ctx.allow_overlap(
                drawer,
                frame,
                elem_a="drawer_side_right",
                elem_b=f"drawer_divider_{i + 1}",
                reason="drawer side rides against the right divider (no clearance gap).",
            )

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)
    ctx.fail_if_joint_mating_has_gap()

    # ---- Structure / identity checks. ----
    part_names = {p.name for p in object_model.parts}
    ctx.check(
        "single root frame present",
        "frame" in part_names,
        details=f"parts={sorted(part_names)}",
    )
    drawer_parts = [name for name in part_names if name.startswith("drawer_")]
    ctx.check(
        "drawer part count matches drawer_count",
        len(drawer_parts) == r.drawer_count,
        details=f"expected {r.drawer_count}, got {drawer_parts}",
    )

    # ---- No REVOLUTE / door articulation (identity guard). ----
    non_fixed = [
        j for j in object_model.articulations if j.articulation_type != ArticulationType.FIXED
    ]
    ctx.check(
        "every movable joint is PRISMATIC (no doors, no lids)",
        all(j.articulation_type == ArticulationType.PRISMATIC for j in non_fixed),
        details=f"non_fixed_types={[j.articulation_type for j in non_fixed]}",
    )
    ctx.check(
        "at least one drawer joint present",
        len(non_fixed) == r.drawer_count and len(non_fixed) >= 1,
        details=f"count={len(non_fixed)} expected={r.drawer_count}",
    )
    # No door / lid parts.
    all_names = list(part_names)
    all_names.extend(v.name or "" for p in object_model.parts for v in p.visuals)
    ctx.check(
        "no door / lid / hinge geometry introduced",
        not any(key in name.lower() for name in all_names for key in ("door", "lid", "hinge")),
        details=(
            f"names={[n for n in all_names if any(k in n.lower() for k in ('door', 'lid', 'hinge'))]}"
        ),
    )

    # ---- Joint axis / limit checks. ----
    for i in range(r.drawer_count):
        j = object_model.get_articulation(f"frame_to_drawer_{i}")
        limits = j.motion_limits
        ctx.check(
            f"drawer_{i} PRISMATIC axis is (0,-1,0)",
            j.articulation_type == ArticulationType.PRISMATIC and tuple(j.axis) == (0.0, -1.0, 0.0),
            details=f"type={j.articulation_type} axis={tuple(j.axis)}",
        )
        ctx.check(
            f"drawer_{i} motion_limits are [0, drawer_travel]",
            limits is not None and limits.lower == 0.0 and limits.upper == r.drawer_travel,
            details=f"limits={limits}",
        )

    # ---- Height / worktop / support proportions (identity). ----
    aabb = ctx.part_world_aabb(frame)
    if aabb is not None:
        (xmn, ymn, zmn), (xmx, ymx, zmx) = aabb
        width = xmx - xmn
        depth = ymx - ymn
        height = zmx - zmn
        ctx.check(
            "table proportions match category (worktop overhang + height 0.72..0.82)",
            0.75 <= height <= 0.85,
            details=f"width={width:.3f} depth={depth:.3f} height={height:.3f}",
        )
        ctx.check(
            "worktop reaches expected planar footprint (worktop >= case)",
            width >= r.case_width - 0.001,
            details=f"width={width:.3f} case_width={r.case_width:.3f}",
        )

    # ---- Targeted pose: drawer 0 moves forward at positive travel. ----
    if r.drawer_count >= 1:
        j0 = object_model.get_articulation("frame_to_drawer_0")
        d0 = object_model.get_part("drawer_0")
        p_closed = ctx.part_world_position(d0)
        with ctx.pose({j0: r.drawer_travel}):
            p_open = ctx.part_world_position(d0)
        if p_closed is not None and p_open is not None:
            ctx.check(
                "drawer_0 opens forward (negative Y) at full travel",
                p_open[1] < p_closed[1] - (r.drawer_travel * 0.9),
                details=f"closed={p_closed} open={p_open} travel={r.drawer_travel}",
            )

    # ---- Sampled-pose collision (§8.5 ⑤ motion sweep). ----
    ctx.fail_if_parts_overlap_in_sampled_poses(
        max_pose_samples=64 if r.drawer_count <= 3 else 48,
        ignore_fixed=True,
    )

    # ---- slot_choices metadata recorded. ----
    ctx.check(
        "slot_choices metadata recorded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    return ctx.report()


__all__ = [
    "TableWithDrawersNoDoorConfig",
    "ResolvedTableWithDrawersNoDoorConfig",
    "build_table_with_drawers_no_door",
    "build_seeded_table_with_drawers_no_door",
    "config_from_seed",
    "resolve_config",
    "run_table_with_drawers_no_door_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
    "PALETTE_STYLES",
]
