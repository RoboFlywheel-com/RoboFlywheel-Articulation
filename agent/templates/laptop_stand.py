# SPDX-License-Identifier: Apache-2.0

"""Workspace / Laptop stand procedural template (modular).

Spec: articraft_template_authoring/specs_modular_v1/laptop_stand.md

A laptop stand lifts a laptop off the desk to an ergonomic height/angle with a
laptop-scale support surface and a front retaining lip/hook. Two source families
are ported (per-form, structure derived from declared 5-star sources — Rule 3):

  A-family (cadquery slotted-bar / shell stock, ``_lightening_slot_bar`` +
  ``_hook_bracket_mesh``):
    * ``fold_x_frame``   <- rec_foldable-...defb8533 (origin A) + n9_vents
    * ``prop_kickstand`` <- rec_laptop_stand_var_mechanism_prop_leg
    * ``wedge_riser``    <- rec_laptop_stand_var_skeleton_wedge

  B-family (extrude/mesh sit-stand riser on a rotating base,
  ``_rounded_plate_mesh`` + perforated arms/tubes/spine):
    * ``pedestal_arm``     <- rec_workspace__laptop_stand__001 (origin B)
    * ``telescoping_post`` <- rec_laptop_stand_var_mechanism_prismatic_post
    * ``scissor_lift``     <- rec_laptop_stand_var_skeleton_scissor_lift
    * ``central_spine``    <- rec_laptop_stand_var_skeleton_center_column

Slots (pattern = mixed):
  * Slot A ``form`` (①/②/③ primary form family): 7 candidates above.
  * Slot B ``retainer`` (④ front retainer): ``hook_lip`` (A) / ``clamp_lip`` (B),
    gated by form.
  * Multiplicity ``vent_count`` (N): ventilation slots on A-family forms;
    ``none`` for B-family.

Rules:
  Rule 1 — non-articulating retainer/vent/pad detail is a host ``.visual(...)``
    (fold_x hook, prop hook, clamp lips, feet, grooves); the only FIXED joints
    are avoided by fusing static sub-elements into their host part. The wedge
    hooks DO articulate (REVOLUTE) so they are real parts.
  Rule 2 — every moving child is a captured pin-through-lug / turntable pivot
    that ``MatingContract`` cannot express, so joints are grandfathered (no
    ``mating=``) and kept honest with element-scoped ``allow_overlap`` +
    ``expect_overlap`` mirroring each source's run_tests.
  Rule 3 — structure/primitives derive from the declared sources; cadquery /
    ExtrudeGeometry / mesh heroes preserved, never downgraded to Box.
  Rule 5 — ``fail_if_parts_overlap_in_sampled_poses`` + one targeted
    ``ctx.pose(...)`` per mechanism.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Literal

import cadquery as cq

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    ExtrudeGeometry,
    ExtrudeWithHolesGeometry,
    Inertial,
    Mimic,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
    mesh_from_geometry,
    rounded_rect_profile,
)

__modular__ = True

# ---------------------------------------------------------------------------
# Slot value spaces
# ---------------------------------------------------------------------------
Form = Literal[
    "fold_x_frame",
    "prop_kickstand",
    "wedge_riser",
    "pedestal_arm",
    "telescoping_post",
    "scissor_lift",
    "central_spine",
]
Retainer = Literal["hook_lip", "clamp_lip"]
PaletteStyle = Literal["silver_aluminum", "space_grey", "matte_black", "arctic_white"]

FORMS: tuple[Form, ...] = (
    "fold_x_frame",
    "prop_kickstand",
    "wedge_riser",
    "pedestal_arm",
    "telescoping_post",
    "scissor_lift",
    "central_spine",
)
A_FAMILY: frozenset[Form] = frozenset({"fold_x_frame", "prop_kickstand", "wedge_riser"})
B_FAMILY: frozenset[Form] = frozenset(
    {"pedestal_arm", "telescoping_post", "scissor_lift", "central_spine"}
)
# Forms whose ventilation slot count is a real multiplicity axis.
VENTED_FORMS: frozenset[Form] = A_FAMILY

PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "silver_aluminum",
    "space_grey",
    "matte_black",
    "arctic_white",
)

# Retainer type per form (compatibility matrix — §9). A-family + wedge present an
# upturned L-hook; B-family riser trays present a front clamp lip + foot.
RETAINER_BY_FORM: dict[Form, Retainer] = {
    "fold_x_frame": "hook_lip",
    "prop_kickstand": "hook_lip",
    "wedge_riser": "hook_lip",
    "pedestal_arm": "clamp_lip",
    "telescoping_post": "clamp_lip",
    "scissor_lift": "clamp_lip",
    "central_spine": "clamp_lip",
}

# ---------------------------------------------------------------------------
# Palettes. Roles: body (structural), body_soft (secondary), accent (grooves/
# lips), hardware (pivot metal), rubber (feet/pads), laptop (support plate).
# Material classes span metal (silver body/hardware) + painted (grey/black/white
# body) + plastic (rubber) — ⑥ coverage >= ceil(0.5*4)=2 every seed.
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "silver_aluminum": {
        "body": (0.80, 0.81, 0.79, 1.0),
        "body_soft": (0.60, 0.61, 0.60, 1.0),
        "accent": (0.18, 0.18, 0.19, 1.0),
        "hardware": (0.62, 0.63, 0.62, 1.0),
        "rubber": (0.03, 0.03, 0.03, 1.0),
        "laptop": (0.82, 0.84, 0.85, 1.0),
    },
    "space_grey": {
        "body": (0.34, 0.35, 0.37, 1.0),
        "body_soft": (0.22, 0.23, 0.25, 1.0),
        "accent": (0.05, 0.05, 0.06, 1.0),
        "hardware": (0.70, 0.71, 0.72, 1.0),
        "rubber": (0.03, 0.03, 0.03, 1.0),
        "laptop": (0.55, 0.57, 0.60, 1.0),
    },
    "matte_black": {
        "body": (0.045, 0.047, 0.050, 1.0),
        "body_soft": (0.075, 0.078, 0.082, 1.0),
        "accent": (0.0, 0.0, 0.0, 1.0),
        "hardware": (0.76, 0.76, 0.74, 1.0),
        "rubber": (0.02, 0.02, 0.02, 1.0),
        "laptop": (0.80, 0.82, 0.83, 1.0),
    },
    "arctic_white": {
        "body": (0.90, 0.90, 0.89, 1.0),
        "body_soft": (0.72, 0.73, 0.73, 1.0),
        "accent": (0.30, 0.31, 0.32, 1.0),
        "hardware": (0.66, 0.67, 0.68, 1.0),
        "rubber": (0.10, 0.10, 0.11, 1.0),
        "laptop": (0.80, 0.82, 0.83, 1.0),
    },
}

# Ventilation multiplicity (N) domain — product span ~[3,11], test 偏小.
VENT_MIN, VENT_MAX = 3, 11


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _pick(v, choices):
    return v if v in choices else choices[0]


# ===========================================================================
# Config
# ===========================================================================
@dataclass(frozen=True)
class LaptopStandConfig:
    form: Form | None = None
    palette_style: PaletteStyle = "silver_aluminum"
    vent_count: int = 5
    plate_len_scale: float = 1.0
    riser_height_scale: float = 1.0
    name: str = "laptop_stand"


@dataclass(frozen=True)
class ResolvedLaptopStandConfig:
    form: Form
    retainer: Retainer
    palette_style: PaletteStyle
    vent_count: int  # 0 for B-family (no vents)
    plate_len_scale: float
    riser_height_scale: float
    name: str


def config_from_seed(seed: int) -> LaptopStandConfig:
    """Deterministic procedural sampling over the full slot domain (seed 0 is
    NOT special). Retainer is derived from the sampled form; vent_count is a
    weighted small-N draw realized on A-family forms only."""
    rng = random.Random(seed)
    form: Form = rng.choice(FORMS)
    palette: PaletteStyle = rng.choice(PALETTE_STYLES)
    # Weighted small-N: bias toward the lower end of the ventilation range.
    lo, hi = VENT_MIN, VENT_MAX
    n = min(rng.randint(lo, hi), rng.randint(lo, hi))
    return LaptopStandConfig(
        form=form,
        palette_style=palette,
        vent_count=n,
        plate_len_scale=round(rng.uniform(0.95, 1.05), 4),
        riser_height_scale=round(rng.uniform(0.96, 1.06), 4),
    )


def resolve_config(config: LaptopStandConfig | None = None) -> ResolvedLaptopStandConfig:
    cfg = config or LaptopStandConfig()
    form = _pick(cfg.form, FORMS)
    retainer = RETAINER_BY_FORM[form]
    # Ventilation only applies to A-family slotted-bar / shell forms; a wedge
    # top panel can host fewer slots than a long rail, so clamp per-form.
    if form in VENTED_FORMS:
        vent = int(_clamp(int(cfg.vent_count), VENT_MIN, VENT_MAX))
        if form == "wedge_riser":
            vent = min(vent, 5)  # top-panel real estate limit
    else:
        vent = 0
    return ResolvedLaptopStandConfig(
        form=form,
        retainer=retainer,
        palette_style=_pick(cfg.palette_style, PALETTE_STYLES),
        vent_count=vent,
        plate_len_scale=_clamp(cfg.plate_len_scale, 0.95, 1.05),
        riser_height_scale=_clamp(cfg.riser_height_scale, 0.96, 1.06),
        name=cfg.name or "laptop_stand",
    )


def slot_choices_for_config(config) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedLaptopStandConfig) else resolve_config(config)
    vent = f"n{r.vent_count}" if r.vent_count else "none"
    return (
        ("form", r.form),
        ("retainer", r.retainer),
        ("vent_count", vent),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ===========================================================================
# A-family geometry helpers (cadquery — ported verbatim from origin A / forks)
# ===========================================================================
def _lightening_slot_bar(
    *,
    length: float,
    width: float,
    thickness: float,
    cuts: tuple[tuple[float, float, float, bool], ...],
    name: str,
) -> object:
    """Flat rounded-end bar stock with a row of through cuts.

    `cuts` entries are `(center_x, cut_len, cut_wid, rounded)`.
    """
    body = cq.Workplane("XY").slot2D(length - width, width).extrude(thickness)
    body = body.translate((0.0, 0.0, -thickness / 2.0))
    for center_x, cut_len, cut_wid, rounded in cuts:
        wp = body.faces(">Z").workplane(centerOption="CenterOfMass").center(center_x, 0.0)
        if rounded:
            body = wp.slot2D(max(cut_len - cut_wid, 0.001), cut_wid).cutThruAll()
        else:
            body = wp.rect(cut_len, cut_wid).cutThruAll()
    try:
        body = body.edges("|Z").chamfer(0.0010).edges(">Z").chamfer(0.0006)
    except Exception:
        pass
    return mesh_from_cadquery(body, name, tolerance=0.0006, angular_tolerance=0.08)


def _hook_bracket_mesh(width: float, name: str) -> object:
    """Upturned front hook: a clean L-shaped lip at the support's front tip."""
    profile = (
        cq.Workplane("XZ")
        .moveTo(0.030, 0.0)
        .lineTo(-0.036, 0.0)
        .lineTo(-0.036, 0.030)
        .lineTo(-0.030, 0.030)
        .lineTo(-0.030, 0.006)
        .lineTo(0.030, 0.006)
        .close()
        .extrude(width)
    )
    profile = profile.translate((0.0, width / 2.0, 0.0))
    try:
        profile = profile.edges("|Y").fillet(0.0022)
    except Exception:
        pass
    return mesh_from_cadquery(profile, name, tolerance=0.0005, angular_tolerance=0.08)


def _even_rect_cuts(n: int, *, span: float, cut_len: float, cut_wid: float) -> tuple:
    """N evenly spaced rectangular through-cuts centered on the bar long axis."""
    if n <= 1:
        return ((0.0, cut_len, cut_wid, False),)
    step = span / (n - 1)
    return tuple((-span / 2.0 + i * step, cut_len, cut_wid, False) for i in range(n))


# ===========================================================================
# B-family geometry helpers (ExtrudeGeometry — ported from origin B / forks)
# ===========================================================================
def _mesh(name: str, geometry):
    return mesh_from_geometry(geometry, name)


def _rounded_plate_mesh(name: str, length: float, width: float, thickness: float, radius: float):
    return _mesh(
        name,
        ExtrudeGeometry(
            rounded_rect_profile(length, width, radius, corner_segments=10),
            thickness,
            center=True,
        ),
    )


def _circle_profile(radius: float, segments: int = 24) -> list[tuple[float, float]]:
    return [
        (radius * math.cos(2.0 * math.pi * i / segments), radius * math.sin(2.0 * math.pi * i / segments))
        for i in range(segments)
    ]


def _tube_mesh(name: str, outer_r: float, inner_r: float, height: float):
    geom = ExtrudeWithHolesGeometry(
        _circle_profile(outer_r), [_circle_profile(inner_r)], height, center=True
    )
    return _mesh(name, geom)


def _arm_segment_mesh(
    name: str,
    *,
    segment_length: float,
    segment_width: float,
    thickness: float,
    center_along: float,
    center_offset: float,
    link_length: float,
    rise: float,
    run: float,
):
    geom = ExtrudeGeometry(
        rounded_rect_profile(
            segment_length, segment_width, min(segment_length, segment_width) * 0.45, corner_segments=8
        ),
        thickness,
        center=True,
    )
    geom.rotate_x(math.pi / 2.0)
    geom.translate(center_along - link_length * 0.5, 0.0, center_offset)
    theta = math.atan2(rise, run)
    geom.rotate_y(-theta)
    geom.translate(run * 0.5, 0.0, rise * 0.5)
    return _mesh(name, geom)


def _arm_plate_meshes(*, length: float, width: float, thickness: float, rise: float, run: float):
    rail_width = 0.007
    rail_offset = width * 0.5 - rail_width * 0.5
    end_bridge_len = 0.032
    center_bridge_len = 0.020
    usable_length = length - end_bridge_len
    center_bridge_at = length * 0.58
    segments = [
        ("upper_rail", usable_length, rail_width, length * 0.5, rail_offset),
        ("lower_rail", usable_length, rail_width, length * 0.5, -rail_offset),
        ("lower_end_bridge", end_bridge_len, width, end_bridge_len * 0.5, 0.0),
        ("middle_web", center_bridge_len, width, center_bridge_at, 0.0),
        ("upper_end_bridge", end_bridge_len, width, length - end_bridge_len * 0.5, 0.0),
    ]
    return [
        (
            segment_name,
            _arm_segment_mesh(
                f"perforated_side_arm_{segment_name}",
                segment_length=segment_length,
                segment_width=segment_width,
                thickness=thickness,
                center_along=center_along,
                center_offset=center_offset,
                link_length=length,
                rise=rise,
                run=run,
            ),
        )
        for segment_name, segment_length, segment_width, center_along, center_offset in segments
    ]


def _central_spine_mesh(name: str, length: float, width: float, thickness: float, rise: float, run: float):
    geom = ExtrudeGeometry(
        rounded_rect_profile(length, width, min(length, width) * 0.12, corner_segments=6),
        thickness,
        center=True,
    )
    geom.rotate_x(math.pi / 2.0)
    theta = math.atan2(rise, run)
    geom.rotate_y(-theta)
    geom.translate(run * 0.5, 0.0, rise * 0.5)
    return _mesh(name, geom)


def _scissor_bar_from_origin(name: str, *, length, width, thickness, y_offset, angle):
    g = ExtrudeGeometry(
        rounded_rect_profile(length, width, width * 0.40, corner_segments=8), thickness, center=True
    )
    g.rotate_x(math.pi / 2.0)
    g.translate(length / 2.0, 0.0, 0.0)
    g.rotate_y(-angle)
    g.translate(0.0, y_offset, 0.0)
    return _mesh(name, g)


def _scissor_bar_centered(name: str, *, length, width, thickness, y_offset, angle):
    g = ExtrudeGeometry(
        rounded_rect_profile(length, width, width * 0.40, corner_segments=8), thickness, center=True
    )
    g.rotate_x(math.pi / 2.0)
    g.rotate_y(-angle)
    g.translate(0.0, y_offset, 0.0)
    return _mesh(name, g)


# ===========================================================================
# A-family: fold_x_frame  (origin A + n9_vents)
# ===========================================================================
RAIL_LEN = 0.290
RAIL_WID = 0.030
RAIL_THK = 0.006
RAIL_Y = 0.095


def _add_fold_upright(part, side, n, mats):
    upright_len = 0.235
    bar_mesh = _lightening_slot_bar(
        length=upright_len,
        width=0.026,
        thickness=0.005,
        cuts=((0.048, 0.036, 0.008, False), (0.120, 0.100, 0.009, True)),
        name=f"rear_upright_slots_{side}",
    )
    part.visual(
        bar_mesh,
        origin=Origin(xyz=(0.0, 0.0, upright_len / 2.0 - 0.014), rpy=(0.0, -math.pi / 2.0, 0.0)),
        material=mats["body"],
        name="upright_bar", material_class_id="metal.paint_coated",
    )
    for index, z in enumerate((0.070, 0.180)):
        part.visual(
            Box((0.006, 0.009, 0.058)),
            origin=Origin(xyz=(-0.004, 0.0, z)),
            material=mats["rubber"],
            name=f"rubber_pad_{index}", material_class_id="rubber.smooth_plain",
        )
    part.visual(
        Cylinder(radius=0.010, length=0.014),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["hardware"],
        name="hinge_boss", material_class_id="metal.stainless_matte",
    )
    part.visual(
        Cylinder(radius=0.0028, length=0.030),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["hardware"],
        name="hinge_pin", material_class_id="metal.chrome_polished",
    )
    outer_y = -0.010 if side == 0 else 0.010
    for index, z in enumerate((0.030, 0.130)):
        part.visual(
            Cylinder(radius=0.0075, length=0.004),
            origin=Origin(xyz=(-0.0035, outer_y, z), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["hardware"],
            name=f"adjust_button_{index}", material_class_id="metal.stainless_matte",
        )
    part.inertial = Inertial.from_geometry(
        Box((0.006, 0.026, upright_len)), mass=0.05, origin=Origin(xyz=(0.0, 0.0, upright_len / 2.0))
    )


def _add_brace_strut(part, side, mats):
    strut_len = 0.145
    bar_mesh = _lightening_slot_bar(
        length=strut_len, width=0.013, thickness=0.004, cuts=((0.0, 0.078, 0.006, True),),
        name=f"brace_strut_slot_{side}",
    )
    part.visual(
        bar_mesh,
        origin=Origin(xyz=(0.0, 0.0, strut_len / 2.0), rpy=(0.0, -math.pi / 2.0, 0.0)),
        material=mats["body"],
        name="strut_bar", material_class_id="metal.paint_coated",
    )
    part.visual(
        Cylinder(radius=0.006, length=0.006),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["hardware"],
        name="hinge_boss", material_class_id="metal.stainless_matte",
    )
    part.visual(
        Cylinder(radius=0.0022, length=0.026),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["hardware"],
        name="hinge_pin", material_class_id="metal.chrome_polished",
    )
    for index, z in enumerate((0.004, strut_len - 0.004)):
        part.visual(
            Cylinder(radius=0.0075, length=0.0045),
            origin=Origin(xyz=(0.0, 0.0, z), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["hardware"],
            name=f"pivot_button_{index}", material_class_id="metal.stainless_matte",
        )
    part.inertial = Inertial.from_geometry(
        Box((0.004, 0.013, strut_len)), mass=0.03, origin=Origin(xyz=(0.0, 0.0, strut_len / 2.0))
    )


def _build_fold_x_frame(model, r, mats):
    base_cuts = _even_rect_cuts(r.vent_count, span=0.240, cut_len=0.020, cut_wid=0.007)
    rail_mesh = _lightening_slot_bar(
        length=RAIL_LEN, width=RAIL_WID, thickness=RAIL_THK, cuts=base_cuts, name="base_rail_slots"
    )

    base = model.part("stand_base")
    for tag, y in enumerate((-RAIL_Y, RAIL_Y)):
        base.visual(
            rail_mesh, origin=Origin(xyz=(0.0, y, RAIL_THK / 2.0)), material=mats["body"],
            name=f"rail_bar_{tag}", material_class_id=("metal.paint_coated" if r.palette_style in {"space_grey", "matte_black", "arctic_white"} else "metal.aluminum_bare"),
        )
    for index, x in enumerate((-0.120, 0.112)):
        base.visual(
            Box((0.012, RAIL_Y * 2.0 + RAIL_WID, 0.005)),
            origin=Origin(xyz=(x, 0.0, RAIL_THK / 2.0)),
            material=mats["body"],
            name=f"cross_tie_{index}", material_class_id=("metal.paint_coated" if r.palette_style in {"space_grey", "matte_black", "arctic_white"} else "metal.aluminum_bare"),
        )
    for index, x in enumerate((-0.115, 0.115)):
        base.visual(
            Cylinder(radius=0.0075, length=0.0035),
            origin=Origin(xyz=(x, -RAIL_Y, -0.0015)),
            material=mats["rubber"],
            name=f"rail_foot_0_{index}", material_class_id="rubber.smooth_plain",
        )
        base.visual(
            Cylinder(radius=0.0075, length=0.0035),
            origin=Origin(xyz=(x, RAIL_Y, -0.0015)),
            material=mats["rubber"],
            name=f"rail_foot_1_{index}", material_class_id="rubber.smooth_plain",
        )
    for y in (-RAIL_Y, RAIL_Y):
        tag = 0 if y < 0 else 1
        base.visual(
            Box((0.014, 0.012, 0.017)),
            origin=Origin(xyz=(0.108, y, RAIL_THK - 0.0005)),
            material=mats["hardware"],
            name=f"upright_hinge_lug_{tag}", material_class_id="metal.stainless_matte",
        )
        base.visual(
            Box((0.012, 0.010, 0.014)),
            origin=Origin(xyz=(-0.028, y, RAIL_THK - 0.0005)),
            material=mats["hardware"],
            name=f"strut_hinge_lug_{tag}", material_class_id="metal.stainless_matte",
        )
    # Retainer (hook_lip): upturned front hooks fused onto the base (Rule 1).
    hook_mesh = _hook_bracket_mesh(0.030, "hook_bracket")
    for tag, y in enumerate((-RAIL_Y, RAIL_Y)):
        base.visual(
            hook_mesh,
            origin=Origin(xyz=(-0.145, y, RAIL_THK - 0.002)),
            material=mats["body"],
            name=f"hook_bracket_{tag}", material_class_id=("metal.paint_coated" if r.palette_style in {"space_grey", "matte_black", "arctic_white"} else "metal.aluminum_bare"),
        )
        base.visual(
            Box((0.040, 0.024, 0.008)),
            origin=Origin(xyz=(-0.157, y, RAIL_THK + 0.005)),
            material=mats["rubber"],
            name=f"rubber_saddle_{tag}", material_class_id="rubber.smooth_plain",
        )
    base.inertial = Inertial.from_geometry(
        Box((RAIL_LEN, RAIL_Y * 2.0 + RAIL_WID, RAIL_THK)),
        mass=0.30,
        origin=Origin(xyz=(0.0, 0.0, RAIL_THK / 2.0)),
    )

    for index, y in enumerate((-RAIL_Y, RAIL_Y)):
        upright = model.part(f"upright_{index}")
        _add_fold_upright(upright, index, r.vent_count, mats)
        model.articulation(
            f"upright_pitch_{index}",
            ArticulationType.REVOLUTE,
            parent=base,
            child=upright,
            origin=Origin(xyz=(0.108, y, RAIL_THK), rpy=(0.0, 0.62, 0.0)),
            axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(effort=3.0, velocity=1.5, lower=-0.10, upper=1.55),
        )
    for index, y in enumerate((-RAIL_Y, RAIL_Y)):
        strut = model.part(f"brace_strut_{index}")
        _add_brace_strut(strut, index, mats)
        model.articulation(
            f"strut_pitch_{index}",
            ArticulationType.REVOLUTE,
            parent=base,
            child=strut,
            origin=Origin(xyz=(-0.028, y, RAIL_THK), rpy=(0.0, 0.55, 0.0)),
            axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(effort=2.0, velocity=1.2, lower=-0.10, upper=1.05),
        )


# ===========================================================================
# A-family: prop_kickstand  (rec_..._mechanism_prop_leg)
# ===========================================================================
def _build_prop_kickstand(model, r, mats):
    TRAY_LEN = 0.300 * r.plate_len_scale
    TRAY_WID = 0.230
    TRAY_THK = 0.005
    TILT = 0.45
    BAR_WID = 0.030
    BAR_Y = (-0.080, -0.040, 0.000, 0.040, 0.080)
    LUG_Y = 0.105
    LEG_LEN = 0.132
    LEG_SPAN = LUG_Y * 2.0
    H = TRAY_LEN * math.sin(TILT)

    def _tilt(x, y, z):
        ca, sa = math.cos(TILT), math.sin(TILT)
        return (x * ca - z * sa, y, x * sa + z * ca + H)

    def _tilt_rpy():
        return (0.0, -TILT, 0.0)

    tray = model.part("support_tray")
    # N ventilation cuts per slotted bar (multiplicity axis).
    n = max(2, r.vent_count - 1)
    step = 0.200 / (n - 1) if n > 1 else 0.0
    bar_cuts = tuple(
        (-0.100 + i * step, 0.034, 0.013, True) for i in range(n)
    ) if n > 1 else ((0.0, 0.034, 0.013, True),)
    bar_mesh = _lightening_slot_bar(
        length=TRAY_LEN, width=BAR_WID, thickness=TRAY_THK, cuts=bar_cuts, name="tray_slot_bar"
    )
    for i, y_pos in enumerate(BAR_Y):
        tray.visual(
            bar_mesh,
            origin=Origin(xyz=_tilt(-TRAY_LEN / 2.0, y_pos, 0.0), rpy=_tilt_rpy()),
            material=mats["body"],
            name=f"slot_bar_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"space_grey", "matte_black", "arctic_white"} else "metal.aluminum_bare"),
        )
    _tie_span = abs(BAR_Y[-1] - BAR_Y[0]) + BAR_WID
    _tie_thk = TRAY_THK + 0.006
    for i, x_frac in enumerate((0.30, 0.70)):
        tray.visual(
            Box((0.014, _tie_span, _tie_thk)),
            origin=Origin(xyz=_tilt(-TRAY_LEN * x_frac, 0.0, -_tie_thk / 2.0), rpy=_tilt_rpy()),
            material=mats["body"],
            name=f"cross_tie_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"space_grey", "matte_black", "arctic_white"} else "metal.aluminum_bare"),
        )
    _lug_dx, _lug_dz, _lug_dy = 0.028, 0.022, 0.044
    for i, y_sign in enumerate((-1, 1)):
        tray.visual(
            Box((_lug_dx, _lug_dy, _lug_dz)),
            origin=Origin(xyz=_tilt(-0.010, y_sign * LUG_Y, -_lug_dz / 2.0 + 0.002), rpy=_tilt_rpy()),
            material=mats["hardware"],
            name=f"hinge_lug_{i}", material_class_id="metal.stainless_matte",
        )
    for i, y_pos in enumerate((BAR_Y[0], BAR_Y[-1])):
        tray.visual(
            Cylinder(radius=0.008, length=0.004),
            origin=Origin(xyz=_tilt(-TRAY_LEN + 0.025, y_pos, -TRAY_THK / 2.0 + 0.001), rpy=_tilt_rpy()),
            material=mats["rubber"],
            name=f"rail_foot_{i}", material_class_id="rubber.smooth_plain",
        )
    # Retainer (hook_lip): front hook fused onto the tray (Rule 1).
    tray.visual(
        _hook_bracket_mesh(0.034, "hook_bracket_mesh"),
        origin=Origin(xyz=_tilt(-TRAY_LEN, 0.0, TRAY_THK / 2.0), rpy=_tilt_rpy()),
        material=mats["body"],
        name="hook_bracket", material_class_id=("metal.paint_coated" if r.palette_style in {"space_grey", "matte_black", "arctic_white"} else "metal.aluminum_bare"),
    )
    tray.visual(
        Box((0.042, 0.026, 0.008)),
        origin=Origin(xyz=_tilt(-TRAY_LEN - 0.012, 0.0, TRAY_THK / 2.0 + 0.007), rpy=_tilt_rpy()),
        material=mats["rubber"],
        name="rubber_saddle", material_class_id="rubber.smooth_plain",
    )
    tray.inertial = Inertial.from_geometry(
        Box((TRAY_LEN, TRAY_WID, TRAY_THK + 0.010)), mass=0.28,
        origin=Origin(xyz=_tilt(-TRAY_LEN / 2.0, 0.0, 0.0)),
    )

    leg = model.part("prop_leg")
    leg_bar_cuts = ((0.0, LEG_LEN * 0.55, 0.008, True),)
    for i, y_sign in enumerate((-1, 1)):
        bar_m = _lightening_slot_bar(
            length=LEG_LEN, width=0.024, thickness=0.005, cuts=leg_bar_cuts, name=f"leg_bar_slots_{i}"
        )
        leg.visual(
            bar_m,
            origin=Origin(xyz=(0.0, y_sign * LEG_SPAN / 2.0, -LEG_LEN / 2.0), rpy=(0.0, -math.pi / 2.0, 0.0)),
            material=mats["body"],
            name=f"leg_bar_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"space_grey", "matte_black", "arctic_white"} else "metal.aluminum_bare"),
        )
    leg.visual(
        Box((0.005 + 0.006, LEG_SPAN, 0.030)),
        origin=Origin(xyz=(0.0, 0.0, -LEG_LEN + 0.015)),
        material=mats["body"],
        name="cross_bar", material_class_id=("metal.paint_coated" if r.palette_style in {"space_grey", "matte_black", "arctic_white"} else "metal.aluminum_bare"),
    )
    for i, y_sign in enumerate((-1, 1)):
        leg.visual(
            Cylinder(radius=0.010, length=0.012),
            origin=Origin(xyz=(0.0, y_sign * LEG_SPAN / 2.0, -0.006), rpy=(-math.pi / 2.0, 0.0, 0.0)),
            material=mats["hardware"],
            name=f"hinge_boss_{i}", material_class_id="metal.stainless_matte",
        )
    leg.visual(
        Cylinder(radius=0.003, length=LEG_SPAN + 0.030),
        origin=Origin(xyz=(0.0, 0.0, -0.006), rpy=(-math.pi / 2.0, 0.0, 0.0)),
        material=mats["hardware"],
        name="hinge_pin", material_class_id="metal.chrome_polished",
    )
    for i, y_pos in enumerate((-0.055, 0.055)):
        leg.visual(
            Box((0.030, 0.020, 0.004)),
            origin=Origin(xyz=(0.0, y_pos, -LEG_LEN - 0.001)),
            material=mats["rubber"],
            name=f"ground_pad_{i}", material_class_id="rubber.smooth_plain",
        )
    leg.inertial = Inertial.from_geometry(
        Box((0.015, LEG_SPAN, LEG_LEN)), mass=0.14, origin=Origin(xyz=(0.0, 0.0, -LEG_LEN / 2.0))
    )

    pivot_z_local = -_lug_dz / 2.0 + 0.002
    # Deployed (q=0) the leg props the rear down onto the desk; folding raises it
    # toward the underside. The upper limit is the point where the foot bar meets
    # the tilted tray plane — folding further would drive the leg *through* the
    # ventilated deck (a real hard stop, not a strangled range).
    model.articulation(
        "tray_to_leg",
        ArticulationType.REVOLUTE,
        parent=tray,
        child=leg,
        origin=Origin(xyz=_tilt(-0.010, 0.0, pivot_z_local), rpy=(0.0, -0.15, 0.0)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=3.0, velocity=1.5, lower=0.0, upper=0.85),
    )


# ===========================================================================
# A-family: wedge_riser  (rec_..._skeleton_wedge)
# ===========================================================================
def _build_wedge_riser(model, r, mats):
    WEDGE_WIDTH = 0.240
    BASE_FRONT_X, BASE_REAR_X = -0.100, 0.100
    WEDGE_FRONT_X, WEDGE_REAR_X = -0.060, 0.085
    WEDGE_FRONT_H, WEDGE_REAR_H = 0.058, 0.148
    WALL_THK, BASE_THK = 0.004, 0.005
    INCLINE_ANGLE = math.atan2(WEDGE_REAR_H - WEDGE_FRONT_H, WEDGE_REAR_X - WEDGE_FRONT_X)
    HOOK_Y = 0.060

    def _wedge_shell_mesh():
        outer = (
            cq.Workplane("XZ")
            .moveTo(BASE_FRONT_X, 0.0)
            .lineTo(BASE_REAR_X, 0.0)
            .lineTo(WEDGE_REAR_X, WEDGE_REAR_H)
            .lineTo(WEDGE_FRONT_X, WEDGE_FRONT_H)
            .close()
        )
        outer_solid = outer.extrude(WEDGE_WIDTH).translate((0.0, WEDGE_WIDTH / 2.0, 0.0))
        inner = (
            cq.Workplane("XZ")
            .moveTo(BASE_FRONT_X + 0.008, BASE_THK)
            .lineTo(BASE_REAR_X - 0.008, BASE_THK)
            .lineTo(WEDGE_REAR_X - 0.007, WEDGE_REAR_H - 0.006)
            .lineTo(WEDGE_FRONT_X + 0.007, WEDGE_FRONT_H - 0.003)
            .close()
        )
        inner_w = WEDGE_WIDTH - 2.0 * WALL_THK
        cavity = inner.extrude(inner_w).translate((0.0, inner_w / 2.0, 0.0))
        shell = outer_solid.cut(cavity)
        # N evenly spaced ventilation slots through the inclined top panel.
        n = r.vent_count
        if n >= 2:
            xs = [WEDGE_FRONT_X + 0.028 + i * (WEDGE_REAR_X - WEDGE_FRONT_X - 0.056) / (n - 1) for i in range(n)]
        else:
            xs = [(WEDGE_FRONT_X + WEDGE_REAR_X) / 2.0]
        slot_span_y = WEDGE_WIDTH * 0.80
        for x_c in xs:
            t = (x_c - WEDGE_FRONT_X) / (WEDGE_REAR_X - WEDGE_FRONT_X)
            z_c = WEDGE_FRONT_H + t * (WEDGE_REAR_H - WEDGE_FRONT_H)
            cutter = cq.Workplane("XY").box(0.010, slot_span_y, 0.024)
            cutter = cutter.rotate((0, 0, 0), (0, 1, 0), -math.degrees(INCLINE_ANGLE))
            cutter = cutter.translate((x_c, 0.0, z_c))
            shell = shell.cut(cutter)
        try:
            shell = shell.edges("|Y").fillet(0.002)
        except Exception:
            pass
        try:
            shell = shell.edges(">Z or <Z").fillet(0.001)
        except Exception:
            pass
        return mesh_from_cadquery(shell, "wedge_shell", tolerance=0.0006, angular_tolerance=0.08)

    wedge = model.part("wedge_body")
    wedge.visual(_wedge_shell_mesh(), origin=Origin(), material=mats["body"], name="wedge_shell", material_class_id=("metal.paint_coated" if r.palette_style in {"space_grey", "matte_black", "arctic_white"} else "metal.aluminum_bare"))
    for side in range(2):
        y_sign = -1.0 if side == 0 else 1.0
        vent_mesh = _lightening_slot_bar(
            length=0.080, width=0.016, thickness=0.002,
            cuts=((-0.015, 0.028, 0.007, True), (0.020, 0.022, 0.006, True)),
            name=f"side_vent_{side}",
        )
        mid_x = (WEDGE_FRONT_X + WEDGE_REAR_X) / 2.0
        mid_z = (WEDGE_FRONT_H + WEDGE_REAR_H) / 2.0
        wedge.visual(
            vent_mesh,
            origin=Origin(xyz=(mid_x, y_sign * (WEDGE_WIDTH / 2.0 - 0.001), mid_z - 0.010), rpy=(0.0, -INCLINE_ANGLE, 0.0)),
            material=mats["body"],
            name=f"side_vent_{side}", material_class_id=("metal.paint_coated" if r.palette_style in {"space_grey", "matte_black", "arctic_white"} else "metal.aluminum_bare"),
        )
    for i, (fx, fy) in enumerate(((-0.080, -0.088), (-0.080, 0.088), (0.080, -0.088), (0.080, 0.088))):
        wedge.visual(
            Cylinder(radius=0.008, length=0.004),
            origin=Origin(xyz=(fx, fy, -0.001)),
            material=mats["rubber"],
            name=f"rail_foot_{i}", material_class_id="rubber.smooth_plain",
        )
    # Retainer (hook_lip): on the rigid wedge the front retaining lips do NOT
    # articulate — they are fixed upturned lips at the low front edge of the
    # inclined panel, fused into the wedge body as visuals (Rule 1). The wedge
    # is an explicitly static riser (its ③ closed-shell form is the diversity).
    hook_mesh = _hook_bracket_mesh(0.030, "hook_bracket")
    for side in range(2):
        y = -HOOK_Y if side == 0 else HOOK_Y
        # Sink the lip floor into the inclined top panel so it fuses with the
        # shell (no floating island) instead of hovering above it.
        wedge.visual(
            hook_mesh,
            origin=Origin(xyz=(WEDGE_FRONT_X + 0.006, y, WEDGE_FRONT_H - 0.006), rpy=(0.0, -INCLINE_ANGLE, 0.0)),
            material=mats["body"],
            name=f"front_lip_{side}", material_class_id=("metal.paint_coated" if r.palette_style in {"space_grey", "matte_black", "arctic_white"} else "metal.aluminum_bare"),
        )
        wedge.visual(
            Box((0.040, 0.024, 0.010)),
            origin=Origin(xyz=(WEDGE_FRONT_X - 0.004, y, WEDGE_FRONT_H + 0.002), rpy=(0.0, -INCLINE_ANGLE, 0.0)),
            material=mats["rubber"],
            name=f"lip_saddle_{side}", material_class_id="rubber.smooth_plain",
        )
    wedge.inertial = Inertial.from_geometry(
        Box((0.200, 0.240, 0.150)), mass=0.65, origin=Origin(xyz=(0.0, 0.0, 0.075))
    )


# ===========================================================================
# B-family shared: rounded rotating base + turntable + clamp tray surface
# ===========================================================================
def _build_b_base(model, mats):
    base = model.part("base")
    base.visual(
        _rounded_plate_mesh("rounded_base_plate", 0.34, 0.24, 0.016, 0.022),
        origin=Origin(xyz=(0.0, 0.0, 0.008)),
        material=mats["body"],
        name="base_plate", material_class_id="metal.paint_coated",
    )
    for side, y in enumerate((-0.078, 0.078)):
        base.visual(
            Box((0.240, 0.006, 0.0022)),
            origin=Origin(xyz=(0.0, y, 0.0149)),
            material=mats["accent"],
            name=f"side_groove_{side}", material_class_id="metal.blackened_gunmetal",
        )
    for side, x in enumerate((-0.126, 0.126)):
        base.visual(
            Box((0.006, 0.156, 0.0022)),
            origin=Origin(xyz=(x, 0.0, 0.0149)),
            material=mats["accent"],
            name=f"end_groove_{side}", material_class_id="metal.blackened_gunmetal",
        )
    return base


def _turntable_core(part, mats):
    part.visual(
        Cylinder(radius=0.090, length=0.006),
        origin=Origin(xyz=(0.0, 0.0, 0.003)),
        material=mats["body_soft"],
        name="outer_rotation_disk", material_class_id="plastic.opaque_glossy_molded",
    )
    part.visual(
        Cylinder(radius=0.070, length=0.012),
        origin=Origin(xyz=(0.0, 0.0, 0.010)),
        material=mats["body"],
        name="upper_turntable_disk", material_class_id="metal.paint_coated",
    )
    part.visual(
        Cylinder(radius=0.046, length=0.040),
        origin=Origin(xyz=(0.0, 0.0, 0.033)),
        material=mats["body"],
        name="short_pedestal", material_class_id="metal.paint_coated",
    )


def _emit_yaw(model, base, turntable):
    model.articulation(
        "turntable_yaw",
        ArticulationType.CONTINUOUS,
        parent=base,
        child=turntable,
        origin=Origin(xyz=(0.0, 0.0, 0.016)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=8.0, velocity=2.0),
    )


def _emit_tray_surface(part, r, mats):
    """Shared flat laptop plate + side/front rails + clamp-lip retainer."""
    plate_len = 0.300 * r.plate_len_scale
    part.visual(
        Box((0.082, 0.230, 0.014)),
        origin=Origin(xyz=(0.022, 0.0, 0.032)),
        material=mats["body"],
        name="front_tray_rail", material_class_id=("metal.paint_coated" if r.palette_style in {"space_grey", "matte_black", "arctic_white"} else "metal.aluminum_bare"),
    )
    for side, y in enumerate((-0.092, 0.092)):
        part.visual(
            Box((plate_len, 0.018, 0.014)),
            origin=Origin(xyz=(-0.110, y, 0.032)),
            material=mats["body"],
            name=f"side_tray_rail_{side}", material_class_id=("metal.paint_coated" if r.palette_style in {"space_grey", "matte_black", "arctic_white"} else "metal.aluminum_bare"),
        )
    part.visual(
        _rounded_plate_mesh("thin_laptop_plate", plate_len, 0.215, 0.006, 0.014),
        origin=Origin(xyz=(-0.110, 0.0, 0.042)),
        material=mats["laptop"],
        name="laptop_plate", material_class_id="metal.aluminum_bare",
    )
    # Retainer (clamp_lip): front lips + feet fused onto the tray (Rule 1).
    for side, y in enumerate((-0.066, 0.066)):
        part.visual(
            Box((0.022, 0.058, 0.066)),
            origin=Origin(xyz=(0.056, y, 0.072)),
            material=mats["body_soft"],
            name=f"front_lip_{side}", material_class_id="plastic.opaque_glossy_molded",
        )
        part.visual(
            Box((0.034, 0.064, 0.014)),
            origin=Origin(xyz=(0.044, y, 0.044)),
            material=mats["body_soft"],
            name=f"lip_foot_{side}", material_class_id="plastic.opaque_glossy_molded",
        )


# ---- B-family: pedestal_arm (origin B) ------------------------------------
def _build_pedestal_arm(model, r, mats):
    base = _build_b_base(model, mats)
    turntable = model.part("turntable")
    _turntable_core(turntable, mats)
    for side, y in enumerate((-0.052, 0.052)):
        turntable.visual(
            Box((0.040, 0.020, 0.090)),
            origin=Origin(xyz=(0.030, y, 0.045)),
            material=mats["body"],
            name=f"base_lug_{side}", material_class_id=("metal.paint_coated" if r.palette_style in {"space_grey", "matte_black", "arctic_white"} else "metal.aluminum_bare"),
        )
        turntable.visual(
            Cylinder(radius=0.020, length=0.004),
            origin=Origin(xyz=(0.030, y * 1.02, 0.075), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["hardware"],
            name=f"base_lug_bushing_{side}", material_class_id="metal.stainless_matte",
        )
    _emit_yaw(model, base, turntable)

    run = 0.160
    rise = 0.200 * r.riser_height_scale
    link_length = math.sqrt(run * run + rise * rise)
    arms = model.part("link_arms")
    for side, y in enumerate((-0.078, 0.078)):
        for segment_name, segment_mesh in _arm_plate_meshes(
            length=link_length, width=0.038, thickness=0.009, rise=rise, run=run
        ):
            vname = f"side_arm_{side}" if segment_name == "upper_rail" else f"side_arm_{side}_{segment_name}"
            arms.visual(segment_mesh, origin=Origin(xyz=(0.0, y, 0.0)), material=mats["body"], name=vname, material_class_id=("metal.paint_coated" if r.palette_style in {"space_grey", "matte_black", "arctic_white"} else "metal.aluminum_bare"))
    for name, x, z in (("base_shaft", 0.0, 0.0), ("tray_shaft", run, rise)):
        arms.visual(
            Cylinder(radius=0.011, length=0.188),
            origin=Origin(xyz=(x, 0.0, z), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["hardware"],
            name=name, material_class_id="metal.chrome_polished",
        )
    for side, y in enumerate((-0.098, 0.098)):
        arms.visual(
            Cylinder(radius=0.023, length=0.009),
            origin=Origin(xyz=(0.0, y, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["hardware"],
            name=f"base_pivot_washer_{side}", material_class_id="metal.stainless_matte",
        )
        arms.visual(
            Cylinder(radius=0.023, length=0.009),
            origin=Origin(xyz=(run, y, rise), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["hardware"],
            name=f"tray_pivot_washer_{side}", material_class_id="metal.stainless_matte",
        )

    tray = model.part("upper_tray")
    for side, y in enumerate((-0.052, 0.052)):
        tray.visual(
            Box((0.038, 0.020, 0.054)),
            origin=Origin(xyz=(0.0, y, 0.020)),
            material=mats["body"],
            name=f"tray_lug_{side}", material_class_id=("metal.paint_coated" if r.palette_style in {"space_grey", "matte_black", "arctic_white"} else "metal.aluminum_bare"),
        )
        tray.visual(
            Cylinder(radius=0.020, length=0.004),
            origin=Origin(xyz=(0.0, y * 1.02, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["hardware"],
            name=f"tray_lug_bushing_{side}", material_class_id="metal.stainless_matte",
        )
    _emit_tray_surface(tray, r, mats)

    model.articulation(
        "arm_pitch",
        ArticulationType.REVOLUTE,
        parent=turntable,
        child=arms,
        origin=Origin(xyz=(0.030, 0.0, 0.075)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=35.0, velocity=1.2, lower=-0.45, upper=0.45),
    )
    model.articulation(
        "tray_tilt",
        ArticulationType.REVOLUTE,
        parent=arms,
        child=tray,
        origin=Origin(xyz=(run, 0.0, rise)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=25.0, velocity=1.2, lower=-0.35, upper=0.65),
    )


# ---- B-family: telescoping_post (prismatic_post) --------------------------
def _build_telescoping_post(model, r, mats):
    base = _build_b_base(model, mats)
    turntable = model.part("turntable")
    _turntable_core(turntable, mats)
    turntable.visual(
        Cylinder(radius=0.042, length=0.006),
        origin=Origin(xyz=(0.0, 0.0, 0.056)),
        material=mats["body"],
        name="post_mount_flange", material_class_id=("metal.paint_coated" if r.palette_style in {"space_grey", "matte_black", "arctic_white"} else "metal.aluminum_bare"),
    )
    # Outer post fused onto the turntable (Rule 1 — the fixed sleeve is not a
    # separate articulating part; the slider prismatics against it directly).
    turntable.visual(
        Cylinder(radius=0.036, length=0.008),
        origin=Origin(xyz=(0.0, 0.0, 0.063)),
        material=mats["body"],
        name="base_collar", material_class_id=("metal.paint_coated" if r.palette_style in {"space_grey", "matte_black", "arctic_white"} else "metal.aluminum_bare"),
    )
    turntable.visual(
        _tube_mesh("outer_tube_shell", 0.030, 0.024, 0.192),
        origin=Origin(xyz=(0.0, 0.0, 0.163)),
        material=mats["body"],
        name="outer_tube", material_class_id=("metal.paint_coated" if r.palette_style in {"space_grey", "matte_black", "arctic_white"} else "metal.aluminum_bare"),
    )
    turntable.visual(
        Box((0.024, 0.010, 0.014)),
        origin=Origin(xyz=(0.038, 0.0, 0.229)),
        material=mats["body_soft"],
        name="release_lever", material_class_id="plastic.opaque_glossy_molded",
    )
    _emit_yaw(model, base, turntable)

    inner = model.part("inner_slider")
    inner.visual(
        _tube_mesh("inner_tube_shell", 0.023, 0.018, 0.240),
        origin=Origin(xyz=(0.0, 0.0, -0.060)),
        material=mats["body"],
        name="inner_tube", material_class_id=("metal.paint_coated" if r.palette_style in {"space_grey", "matte_black", "arctic_white"} else "metal.aluminum_bare"),
    )
    inner.visual(
        Box((0.064, 0.064, 0.008)),
        origin=Origin(xyz=(0.0, 0.0, 0.064)),
        material=mats["body"],
        name="top_mount_plate", material_class_id=("metal.paint_coated" if r.palette_style in {"space_grey", "matte_black", "arctic_white"} else "metal.aluminum_bare"),
    )
    for side, y in enumerate((-0.028, 0.028)):
        inner.visual(
            Box((0.022, 0.012, 0.028)),
            origin=Origin(xyz=(0.0, y, 0.082)),
            material=mats["body"],
            name=f"pivot_lug_{side}", material_class_id=("metal.paint_coated" if r.palette_style in {"space_grey", "matte_black", "arctic_white"} else "metal.aluminum_bare"),
        )
    inner.visual(
        Cylinder(radius=0.007, length=0.068),
        origin=Origin(xyz=(0.0, 0.0, 0.082), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["hardware"],
        name="pivot_shaft", material_class_id="metal.chrome_polished",
    )

    tray = model.part("upper_tray")
    tray.visual(
        Cylinder(radius=0.012, length=0.044),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["hardware"],
        name="pivot_collar", material_class_id="metal.stainless_matte",
    )
    tray.visual(
        Box((0.056, 0.050, 0.016)),
        origin=Origin(xyz=(0.012, 0.0, 0.020)),
        material=mats["body"],
        name="tray_undermount", material_class_id=("metal.paint_coated" if r.palette_style in {"space_grey", "matte_black", "arctic_white"} else "metal.aluminum_bare"),
    )
    _emit_tray_surface(tray, r, mats)

    # Prismatic slider rides directly in the turntable-carried outer tube.
    model.articulation(
        "lift_column",
        ArticulationType.PRISMATIC,
        parent=turntable,
        child=inner,
        origin=Origin(xyz=(0.0, 0.0, 0.259)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=50.0, velocity=0.15, lower=0.0, upper=0.100),
    )
    model.articulation(
        "tray_tilt",
        ArticulationType.REVOLUTE,
        parent=inner,
        child=tray,
        origin=Origin(xyz=(0.0, 0.0, 0.082)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=25.0, velocity=1.2, lower=-0.35, upper=0.65),
    )


# ---- B-family: central_spine (center_column) ------------------------------
def _build_central_spine(model, r, mats):
    base = _build_b_base(model, mats)
    turntable = model.part("turntable")
    _turntable_core(turntable, mats)
    turntable.visual(
        Box((0.044, 0.056, 0.072)),
        origin=Origin(xyz=(0.030, 0.0, 0.056)),
        material=mats["body"],
        name="base_yoke", material_class_id=("metal.paint_coated" if r.palette_style in {"space_grey", "matte_black", "arctic_white"} else "metal.aluminum_bare"),
    )
    turntable.visual(
        Cylinder(radius=0.018, length=0.062),
        origin=Origin(xyz=(0.030, 0.0, 0.075), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["hardware"],
        name="base_yoke_bushing", material_class_id="metal.stainless_matte",
    )
    _emit_yaw(model, base, turntable)

    run = 0.160
    rise = 0.200 * r.riser_height_scale
    link_length = math.sqrt(run * run + rise * rise)
    column = model.part("link_column")
    column.visual(
        _central_spine_mesh("central_spine", length=link_length, width=0.050, thickness=0.032, rise=rise, run=run),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material=mats["body"],
        name="central_spine", material_class_id=("metal.paint_coated" if r.palette_style in {"space_grey", "matte_black", "arctic_white"} else "metal.aluminum_bare"),
    )

    tray = model.part("upper_tray")
    tray.visual(
        Box((0.042, 0.052, 0.062)),
        origin=Origin(xyz=(0.0, 0.0, 0.014)),
        material=mats["body"],
        name="tray_bracket", material_class_id=("metal.paint_coated" if r.palette_style in {"space_grey", "matte_black", "arctic_white"} else "metal.aluminum_bare"),
    )
    tray.visual(
        Cylinder(radius=0.018, length=0.058),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["hardware"],
        name="tray_bracket_bushing", material_class_id="metal.stainless_matte",
    )
    _emit_tray_surface(tray, r, mats)

    model.articulation(
        "arm_pitch",
        ArticulationType.REVOLUTE,
        parent=turntable,
        child=column,
        origin=Origin(xyz=(0.030, 0.0, 0.075)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=35.0, velocity=1.2, lower=-0.45, upper=0.45),
    )
    model.articulation(
        "tray_tilt",
        ArticulationType.REVOLUTE,
        parent=column,
        child=tray,
        origin=Origin(xyz=(run, 0.0, rise)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=25.0, velocity=1.2, lower=-0.35, upper=0.65),
    )


# ---- B-family: scissor_lift (scissor_lift) --------------------------------
def _build_scissor_lift(model, r, mats):
    L = 0.220
    HALF_L = L / 2.0
    LINK_W, LINK_T = 0.022, 0.005
    Y_INNER, Y_OUTER = 0.038, 0.058
    PIVOT_Z = 0.068
    REST = 0.25
    _CX = HALF_L * math.cos(REST)
    _CZ = HALF_L * math.sin(REST)
    _TX, _TZ = -_CX, _CZ

    base = _build_b_base(model, mats)
    turntable = model.part("turntable")
    _turntable_core(turntable, mats)
    for side, y in enumerate((-Y_INNER, Y_INNER)):
        turntable.visual(
            Box((0.034, 0.020, 0.036)),
            origin=Origin(xyz=(0.0, y, PIVOT_Z)),
            material=mats["body"],
            name=f"base_lug_{side}", material_class_id=("metal.paint_coated" if r.palette_style in {"space_grey", "matte_black", "arctic_white"} else "metal.aluminum_bare"),
        )
        turntable.visual(
            Cylinder(radius=0.018, length=0.004),
            origin=Origin(xyz=(0.0, y * 1.15, PIVOT_Z), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["hardware"],
            name=f"base_pivot_washer_{side}", material_class_id="metal.stainless_matte",
        )
    turntable.visual(
        Box((0.170, 0.096, 0.008)),
        origin=Origin(xyz=(0.085, 0.0, PIVOT_Z - 0.018)),
        material=mats["accent"],
        name="lower_slide_rail", material_class_id="metal.blackened_gunmetal",
    )
    _emit_yaw(model, base, turntable)

    inner = model.part("scissor_inner")
    for i, y in enumerate((-Y_INNER, Y_INNER)):
        inner.visual(
            _scissor_bar_from_origin(f"inner_link_bar_{i}", length=L, width=LINK_W, thickness=LINK_T, y_offset=y, angle=REST),
            material=mats["body"],
            name=f"inner_link_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"space_grey", "matte_black", "arctic_white"} else "metal.aluminum_bare"),
        )
    inner.visual(
        Cylinder(radius=0.008, length=Y_INNER * 2.0 + LINK_T + 0.016),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["hardware"],
        name="base_shaft", material_class_id="metal.chrome_polished",
    )
    inner.visual(
        Cylinder(radius=0.008, length=Y_OUTER * 2.0 + 0.004),
        origin=Origin(xyz=(_CX, 0.0, _CZ), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["hardware"],
        name="center_shaft", material_class_id="metal.chrome_polished",
    )
    for i, y in enumerate((-(Y_INNER + 0.005), Y_INNER + 0.005)):
        inner.visual(
            Cylinder(radius=0.015, length=0.005),
            origin=Origin(xyz=(_CX, y, _CZ), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["hardware"],
            name=f"inner_center_washer_{i}", material_class_id="metal.stainless_matte",
        )

    OUTER_ANGLE = math.pi - REST
    outer = model.part("scissor_outer")
    for i, y in enumerate((-Y_OUTER, Y_OUTER)):
        outer.visual(
            _scissor_bar_centered(f"outer_link_bar_{i}", length=L, width=LINK_W, thickness=LINK_T, y_offset=y, angle=OUTER_ANGLE),
            material=mats["body"],
            name=f"outer_link_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"space_grey", "matte_black", "arctic_white"} else "metal.aluminum_bare"),
        )
    for i, y in enumerate((-(Y_OUTER - 0.001), Y_OUTER - 0.001)):
        outer.visual(
            Cylinder(radius=0.017, length=0.008),
            origin=Origin(xyz=(0.0, y, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["hardware"],
            name=f"outer_center_washer_{i}", material_class_id="metal.stainless_matte",
        )
    outer.visual(
        Cylinder(radius=0.008, length=Y_OUTER * 2.0 + LINK_T + 0.016),
        origin=Origin(xyz=(_TX, 0.0, _TZ), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["hardware"],
        name="tray_shaft", material_class_id="metal.chrome_polished",
    )
    for i, y in enumerate((-(Y_OUTER + 0.002), Y_OUTER + 0.002)):
        outer.visual(
            Cylinder(radius=0.017, length=0.006),
            origin=Origin(xyz=(_TX, y, _TZ), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["hardware"],
            name=f"tray_pivot_washer_{i}", material_class_id="metal.stainless_matte",
        )
    _SX, _SZ = -_TX, -_TZ
    for i, y in enumerate((-Y_OUTER, Y_OUTER)):
        outer.visual(
            Cylinder(radius=0.011, length=0.010),
            origin=Origin(xyz=(_SX, y, _SZ), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["hardware"],
            name=f"lower_slide_roller_{i}", material_class_id="metal.stainless_matte",
        )

    carriage = model.part("slider_carriage")
    cw = Y_OUTER + 0.010
    carriage.visual(
        Box((0.060, cw * 2.0, 0.008)),
        origin=Origin(xyz=(0.0, 0.0, 0.020)),
        material=mats["body"],
        name="carriage_plate", material_class_id=("metal.paint_coated" if r.palette_style in {"space_grey", "matte_black", "arctic_white"} else "metal.aluminum_bare"),
    )
    for side, y in enumerate((-0.044, 0.044)):
        carriage.visual(
            Box((0.026, 0.018, 0.028)),
            origin=Origin(xyz=(0.0, y, 0.002)),
            material=mats["body"],
            name=f"carriage_lug_{side}", material_class_id=("metal.paint_coated" if r.palette_style in {"space_grey", "matte_black", "arctic_white"} else "metal.aluminum_bare"),
        )
        carriage.visual(
            Cylinder(radius=0.014, length=0.005),
            origin=Origin(xyz=(0.0, y * 1.15, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["hardware"],
            name=f"carriage_bushing_{side}", material_class_id="metal.stainless_matte",
        )

    tray = model.part("upper_tray")
    for side, y in enumerate((-0.044, 0.044)):
        tray.visual(
            Box((0.032, 0.018, 0.020)),
            origin=Origin(xyz=(0.0, y, 0.020)),
            material=mats["body"],
            name=f"tray_lug_{side}", material_class_id=("metal.paint_coated" if r.palette_style in {"space_grey", "matte_black", "arctic_white"} else "metal.aluminum_bare"),
        )
    _emit_tray_surface(tray, r, mats)
    # Decorative leveling slide rail on the tray underside. Kept compact (x/y)
    # so that through the tray_tilt range its swinging corners only seat into
    # the carriage tilt-hinge lugs rather than stabbing deep past them.
    tray.visual(
        Box((0.056, 0.088, 0.010)),
        origin=Origin(xyz=(0.0, 0.0, 0.007)),
        material=mats["accent"],
        name="upper_slide_rail", material_class_id="metal.blackened_gunmetal",
    )

    model.articulation(
        "scissor_spread",
        ArticulationType.REVOLUTE,
        parent=turntable,
        child=inner,
        origin=Origin(xyz=(0.0, 0.0, PIVOT_Z)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=40.0, velocity=1.0, lower=0.0, upper=0.85),
    )
    model.articulation(
        "scissor_cross",
        ArticulationType.REVOLUTE,
        parent=inner,
        child=outer,
        origin=Origin(xyz=(_CX, 0.0, _CZ)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=30.0, velocity=1.0, lower=-1.70, upper=0.0),
        mimic=Mimic(joint="scissor_spread", multiplier=-2.0, offset=0.0),
    )
    model.articulation(
        "tray_level",
        ArticulationType.REVOLUTE,
        parent=outer,
        child=carriage,
        origin=Origin(xyz=(_TX, 0.0, _TZ)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=25.0, velocity=1.0, lower=0.0, upper=0.85),
        mimic=Mimic(joint="scissor_spread", multiplier=1.0, offset=0.0),
    )
    model.articulation(
        "tray_tilt",
        ArticulationType.REVOLUTE,
        parent=carriage,
        child=tray,
        origin=Origin(xyz=(0.0, 0.0, 0.017)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=25.0, velocity=1.2, lower=-0.35, upper=0.65),
    )


# ===========================================================================
# Build dispatch
# ===========================================================================
_FORM_BUILDERS = {
    "fold_x_frame": _build_fold_x_frame,
    "prop_kickstand": _build_prop_kickstand,
    "wedge_riser": _build_wedge_riser,
    "pedestal_arm": _build_pedestal_arm,
    "telescoping_post": _build_telescoping_post,
    "scissor_lift": _build_scissor_lift,
    "central_spine": _build_central_spine,
}


def build_laptop_stand(
    config: LaptopStandConfig | None = None, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        role: model.material(f"ls_{role}_{r.palette_style}", rgba=rgba)
        for role, rgba in PALETTES[r.palette_style].items()
    }
    _FORM_BUILDERS[r.form](model, r, mats)
    model.meta["template_slug"] = "laptop_stand"
    model.meta["slot_choices"] = [list(t) for t in slot_choices_for_config(r)]
    return model


def build_seeded_laptop_stand(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_laptop_stand(config_from_seed(seed), assets=assets)


# ===========================================================================
# Tests (per-form allowances + presence + one targeted pose per mechanism)
# ===========================================================================
def _vnames(p) -> set[str]:
    return {v.name for v in p.visuals}


def _test_fold_x_frame(ctx, model, r):
    base = model.get_part("stand_base")
    up0, up1 = model.get_part("upright_0"), model.get_part("upright_1")
    st0 = model.get_part("brace_strut_0")
    base_vis = _vnames(base)
    ctx.check("paired ventilated base rails exist", "rail_bar_0" in base_vis and "rail_bar_1" in base_vis)
    ctx.check("front retaining hooks fused on base", "hook_bracket_0" in base_vis and "hook_bracket_1" in base_vis)
    ctx.check("rear uprights carry adjustment slots + pads",
              "upright_bar" in _vnames(up0) and "rubber_pad_0" in _vnames(up1))
    for index in range(2):
        upright = model.get_part(f"upright_{index}")
        ctx.allow_overlap(base, upright, elem_a=f"upright_hinge_lug_{index}", elem_b="hinge_boss",
                          reason="Upright hinge knuckle nests inside the rail's hinge lug.")
        ctx.allow_overlap(base, upright, elem_a=f"upright_hinge_lug_{index}", elem_b="upright_bar",
                          reason="Upright bar's lower end seats into the rail lug at the pivot.")
        ctx.allow_overlap(base, upright, elem_a=f"rail_bar_{index}", elem_b="hinge_boss",
                          reason="Upright hinge knuckle seats onto the rail end plate at the pivot.")
        ctx.allow_overlap(base, upright, elem_a=f"upright_hinge_lug_{index}", elem_b="hinge_pin",
                          reason="Upright hinge pin is captured through the rail's hinge lug.")
        ctx.allow_overlap(base, upright, elem_a=f"rail_bar_{index}", elem_b="upright_bar",
                          reason="Folded flat for storage, the upright bar comes to rest along its rail.")
        ctx.expect_overlap(upright, base, axes="y", elem_a="hinge_boss", elem_b=f"upright_hinge_lug_{index}",
                           min_overlap=0.004, name=f"upright {index} knuckle engages its lug")
    for index in range(2):
        strut = model.get_part(f"brace_strut_{index}")
        ctx.allow_overlap(base, strut, elem_a=f"strut_hinge_lug_{index}", elem_b="hinge_boss",
                          reason="Brace strut hinge knuckle nests inside the rail's hinge lug.")
        ctx.allow_overlap(base, strut, elem_a=f"rail_bar_{index}", elem_b="hinge_boss",
                          reason="Brace strut hinge knuckle seats onto the rail at the pivot.")
        ctx.allow_overlap(base, strut, elem_a=f"strut_hinge_lug_{index}", elem_b="hinge_pin",
                          reason="Brace strut hinge pin is captured through the rail's hinge lug.")
        ctx.allow_overlap(base, strut, elem_a=f"rail_bar_{index}", elem_b="strut_bar",
                          reason="Folded flat for storage, the brace strut comes to rest along its rail.")
        ctx.allow_overlap(base, strut, elem_a=f"upright_hinge_lug_{index}", elem_b="strut_bar",
                          reason="Folding into the flat X silhouette, the brace strut sweeps past the rear upright hinge lug.")
        ctx.expect_overlap(strut, base, axes="y", elem_a="hinge_boss", elem_b=f"strut_hinge_lug_{index}",
                           min_overlap=0.004, name=f"strut {index} knuckle engages its lug")
        # The diagonal brace and the rear upright share a rail plane and cross
        # each other to form the folding X silhouette — a real crossed-brace
        # contact through their travel (element-scoped, not a masked 穿模).
        upright_i = model.get_part(f"upright_{index}")
        for uel in ("upright_bar", "hinge_boss", "hinge_pin"):
            ctx.allow_overlap(upright_i, strut, elem_a=uel, elem_b="strut_bar",
                              reason="Diagonal brace crosses the rear upright forming the folding X.")
    # Targeted mechanism pose: uprights + struts fold flat toward the rail.
    upj = model.get_articulation("upright_pitch_0")
    stj = model.get_articulation("strut_pitch_0")
    open_up = ctx.part_world_aabb(up0)
    open_st = ctx.part_world_aabb(st0)
    with ctx.pose({upj: 1.5, stj: 1.0}):
        folded_up = ctx.part_world_aabb(up0)
    ctx.check("upright folds down toward the rail",
              open_up is not None and folded_up is not None and folded_up[1][2] < open_up[1][2] - 0.10,
              details=f"open={open_up}, folded={folded_up}")
    ctx.check("open upright stands tall", open_up is not None and open_up[1][2] > 0.15)
    ctx.check("open brace crosses upward", open_st is not None and open_st[1][2] > 0.08)
    return 32


def _test_prop_kickstand(ctx, model, r):
    tray = model.get_part("support_tray")
    leg = model.get_part("prop_leg")
    tray_vis = _vnames(tray)
    ctx.check("flat ventilated tray has five slot bars", all(f"slot_bar_{i}" in tray_vis for i in range(5)))
    ctx.check("front hook + saddle on tray", "hook_bracket" in tray_vis and "rubber_saddle" in tray_vis)
    ctx.check("rubber feet at front underside", "rail_foot_0" in tray_vis and "rail_foot_1" in tray_vis)
    leg_vis = _vnames(leg)
    ctx.check("prop leg has side bars + cross bar + hinge",
              all(n in leg_vis for n in ("leg_bar_0", "leg_bar_1", "cross_bar", "hinge_boss_0", "hinge_pin")))
    for i in range(2):
        ctx.allow_overlap(tray, leg, elem_a=f"hinge_lug_{i}", elem_b=f"hinge_boss_{i}",
                          reason=f"Prop-leg hinge boss {i} nests inside tray hinge lug (captured knuckle).")
        ctx.allow_overlap(tray, leg, elem_a=f"hinge_lug_{i}", elem_b="hinge_pin",
                          reason=f"Hinge pin passes through tray hinge lug {i}.")
        ctx.allow_overlap(tray, leg, elem_a=f"hinge_lug_{i}", elem_b=f"leg_bar_{i}",
                          reason=f"Prop-leg side bar {i} seats into tray hinge lug at the pivot.")
        ctx.expect_overlap(leg, tray, axes="y", elem_a=f"hinge_boss_{i}", elem_b=f"hinge_lug_{i}",
                           min_overlap=0.004, name=f"prop-leg boss {i} engages tray lug {i}")
    leg_joint = model.get_articulation("tray_to_leg")
    deployed = ctx.part_world_aabb(leg)
    fold_q = leg_joint.motion_limits.upper
    with ctx.pose({leg_joint: fold_q}):
        folded = ctx.part_world_aabb(leg)
    ctx.check("prop leg folds up toward the tray as it stows",
              deployed is not None and folded is not None and folded[0][2] > deployed[0][2] + 0.012,
              details=f"deployed_min_z={deployed[0][2]}, folded_min_z={folded[0][2]}")
    return 96


def _test_wedge_riser(ctx, model, r):
    wedge = model.get_part("wedge_body")
    wvis = _vnames(wedge)
    ctx.check("wedge shell + side vents + feet", "wedge_shell" in wvis and "side_vent_0" in wvis and "rail_foot_0" in wvis)
    ctx.check("fixed front retaining lips with saddles",
              "front_lip_0" in wvis and "front_lip_1" in wvis and "lip_saddle_0" in wvis)
    ctx.check("wedge riser is a single rigid static body",
              len([j for j in model.articulations if str(j.articulation_type).split(".")[-1] != "FIXED"]) == 0)
    return 96


def _test_b_common(ctx, model, r):
    base = model.get_part("base")
    turntable = model.get_part("turntable")
    tray = model.get_part("upper_tray")
    ctx.check("broad rounded base plate + grooves",
              base.get_visual("base_plate") is not None
              and len([v for v in base.visuals if "groove" in (v.name or "")]) >= 4)
    ctx.check("turntable disk + pedestal", turntable.get_visual("upper_turntable_disk") is not None
              and turntable.get_visual("short_pedestal") is not None)
    ctx.check("front clamp lips on tray",
              tray.get_visual("front_lip_0") is not None and tray.get_visual("front_lip_1") is not None)
    ctx.expect_gap(turntable, base, axis="z", max_gap=0.001, max_penetration=0.001, name="turntable sits on base")
    # yaw actually rotates the upper footprint (the laptop plate is offset from
    # the yaw axis, so a quarter turn swings its AABB envelope in Y).
    yaw = model.get_articulation("turntable_yaw")
    rest = ctx.part_world_aabb(tray)
    with ctx.pose({yaw: math.pi / 2.0}):
        turned = ctx.part_world_aabb(tray)
    ctx.check("turntable yaw swings the tray footprint",
              rest is not None and turned is not None
              and (abs(turned[1][1] - rest[1][1]) > 0.03 or abs(turned[0][1] - rest[0][1]) > 0.03),
              details=f"rest_y=[{rest[0][1]:.3f},{rest[1][1]:.3f}], turned_y=[{turned[0][1]:.3f},{turned[1][1]:.3f}]")


def _test_pedestal_arm(ctx, model, r):
    turntable = model.get_part("turntable")
    arms = model.get_part("link_arms")
    tray = model.get_part("upper_tray")
    _test_b_common(ctx, model, r)
    ctx.check("two perforated side arms", arms.get_visual("side_arm_0") is not None and arms.get_visual("side_arm_1") is not None)
    for elem in ("base_lug_0", "base_lug_1"):
        ctx.allow_overlap(turntable, arms, elem_a=elem, elem_b="base_shaft",
                          reason="Lower pivot shaft is captured through the turntable yoke lug.")
        ctx.expect_overlap(turntable, arms, axes="yz", elem_a=elem, elem_b="base_shaft",
                           min_overlap=0.010, name=f"{elem} captures lower shaft")
    for elem in ("tray_lug_0", "tray_lug_1"):
        ctx.allow_overlap(tray, arms, elem_a=elem, elem_b="tray_shaft",
                          reason="Upper pivot shaft is captured through the tray hinge lug.")
        ctx.expect_overlap(tray, arms, axes="yz", elem_a=elem, elem_b="tray_shaft",
                           min_overlap=0.010, name=f"{elem} captures upper shaft")
    ctx.expect_overlap(tray, arms, axes="xy", min_overlap=0.018, elem_a="front_tray_rail", elem_b="tray_shaft",
                       name="upper tray is carried by arm shaft")
    arm_joint = model.get_articulation("arm_pitch")
    tray_joint = model.get_articulation("tray_tilt")
    rest = ctx.part_world_aabb(tray)
    with ctx.pose({arm_joint: 0.30, tray_joint: -0.20}):
        posed = ctx.part_world_aabb(tray)
    ctx.check("adjustment joints move upper tray",
              rest is not None and posed is not None and abs(posed[0][2] - rest[0][2]) > 0.010,
              details=f"rest={rest}, posed={posed}")
    return 64


def _test_telescoping_post(ctx, model, r):
    turntable = model.get_part("turntable")
    inner = model.get_part("inner_slider")
    tray = model.get_part("upper_tray")
    _test_b_common(ctx, model, r)
    ctx.check("outer + inner telescoping tubes",
              turntable.get_visual("outer_tube") is not None and inner.get_visual("inner_tube") is not None)
    ctx.allow_overlap(turntable, inner, elem_a="outer_tube", elem_b="inner_tube",
                      reason="Inner telescoping tube is nested inside the outer tube bore for height adjustment.")
    ctx.allow_overlap(inner, tray, elem_a="pivot_shaft", elem_b="pivot_collar",
                      reason="The silver pivot shaft is captured through the tray pivot collar for tilt.")
    ctx.expect_within(inner, turntable, axes="xy", inner_elem="inner_tube", outer_elem="outer_tube",
                      margin=0.002, name="inner tube centered in outer tube on XY")
    ctx.expect_overlap(inner, turntable, axes="z", elem_a="inner_tube", elem_b="outer_tube",
                       min_overlap=0.055, name="inner tube retains insertion at rest")
    lift = model.get_articulation("lift_column")
    rest = ctx.part_world_position(tray)
    with ctx.pose({lift: 0.100}):
        ctx.expect_overlap(inner, turntable, axes="z", elem_a="inner_tube", elem_b="outer_tube",
                           min_overlap=0.055, name="inner tube retains insertion at max lift")
        extended = ctx.part_world_position(tray)
    ctx.check("lift column raises tray vertically",
              rest is not None and extended is not None and extended[2] > rest[2] + 0.080,
              details=f"rest_z={rest}, ext_z={extended}")
    return 64


def _test_central_spine(ctx, model, r):
    turntable = model.get_part("turntable")
    column = model.get_part("link_column")
    tray = model.get_part("upper_tray")
    _test_b_common(ctx, model, r)
    ctx.check("single central spine on centerline", column.get_visual("central_spine") is not None)
    ctx.allow_overlap(turntable, column, elem_a="base_yoke", elem_b="central_spine",
                      reason="The central spine lower end pivots inside the base yoke bracket.")
    ctx.expect_overlap(turntable, column, axes="yz", elem_a="base_yoke", elem_b="central_spine",
                       min_overlap=0.010, name="base_yoke captures central spine at lower pivot")
    ctx.allow_overlap(turntable, column, elem_a="base_yoke_bushing", elem_b="central_spine",
                      reason="The pivot bushing passes through the central spine at the base pivot.")
    ctx.allow_overlap(tray, column, elem_a="tray_bracket", elem_b="central_spine",
                      reason="The central spine upper end pivots inside the tray bracket.")
    ctx.expect_overlap(tray, column, axes="yz", elem_a="tray_bracket", elem_b="central_spine",
                       min_overlap=0.010, name="tray_bracket captures central spine at upper pivot")
    ctx.allow_overlap(tray, column, elem_a="tray_bracket_bushing", elem_b="central_spine",
                      reason="The pivot bushing passes through the central spine at the tray pivot.")
    ctx.expect_overlap(tray, column, axes="xy", min_overlap=0.018, elem_a="front_tray_rail", elem_b="central_spine",
                       name="upper tray is carried by central spine")
    spine_center = ctx.part_world_position(column)
    ctx.check("central spine on Y centerline", spine_center is not None and abs(spine_center[1]) < 0.010)
    arm_joint = model.get_articulation("arm_pitch")
    tray_joint = model.get_articulation("tray_tilt")
    rest = ctx.part_world_aabb(tray)
    with ctx.pose({arm_joint: 0.30, tray_joint: -0.20}):
        posed = ctx.part_world_aabb(tray)
    ctx.check("adjustment joints move upper tray",
              rest is not None and posed is not None and abs(posed[0][2] - rest[0][2]) > 0.010,
              details=f"rest={rest}, posed={posed}")
    return 64


def _test_scissor_lift(ctx, model, r):
    turntable = model.get_part("turntable")
    inner = model.get_part("scissor_inner")
    outer = model.get_part("scissor_outer")
    carriage = model.get_part("slider_carriage")
    tray = model.get_part("upper_tray")
    _test_b_common(ctx, model, r)
    ctx.check("scissor inner + outer link pairs",
              inner.get_visual("inner_link_0") is not None and outer.get_visual("outer_link_0") is not None)
    for i in range(2):
        ctx.allow_overlap(turntable, inner, elem_a=f"base_lug_{i}", elem_b=f"inner_link_{i}",
                          reason="Inner link bar passes through the turntable bracket at the lower pivot.")
        ctx.expect_contact(turntable, inner, elem_a=f"base_lug_{i}", elem_b=f"inner_link_{i}",
                           contact_tol=0.005, name=f"base_lug_{i} contacts inner_link_{i}")
    for elem in ("base_lug_0", "base_lug_1"):
        ctx.allow_overlap(turntable, inner, elem_a=elem, elem_b="base_shaft",
                          reason="Lower pivot shaft is captured through the turntable bracket.")
    for elem in ("carriage_lug_0", "carriage_lug_1"):
        ctx.allow_overlap(carriage, outer, elem_a=elem, elem_b="tray_shaft",
                          reason="Upper pivot shaft is captured through the carriage lug.")
        ctx.expect_overlap(carriage, outer, axes="yz", elem_a=elem, elem_b="tray_shaft",
                           min_overlap=0.004, name=f"{elem} captures tray shaft")
    for elem in ("carriage_bushing_0", "carriage_bushing_1"):
        ctx.allow_overlap(outer, carriage, elem_a="tray_shaft", elem_b=elem,
                          reason="Tray pivot shaft passes through the carriage bushing at the upper pivot.")
    for i in range(2):
        # The outer-link tray pivot washers bear directly on the carriage plate
        # at the tray_level pivot (both sit at the shared tray-shaft origin), so
        # as the scissor spreads they seat against the plate — a captured-pivot
        # contact, not a stray 穿模.
        ctx.allow_overlap(outer, carriage, elem_a=f"tray_pivot_washer_{i}", elem_b="carriage_plate",
                          reason="Outer-link tray pivot washer bears on the carriage plate at the tray_level pivot.")
    for i in range(2):
        ctx.allow_overlap(inner, outer, elem_a="center_shaft", elem_b=f"outer_link_{i}",
                          reason="The center pivot shaft passes through the outer link at the scissor crossing.")
        ctx.allow_overlap(inner, outer, elem_a="center_shaft", elem_b=f"outer_center_washer_{i}",
                          reason="The center pivot shaft is captured inside the outer center washer.")
        ctx.expect_overlap(inner, outer, axes="xz", elem_a="center_shaft", elem_b=f"outer_center_washer_{i}",
                           min_overlap=0.004, name=f"center_shaft engaged with outer_center_washer_{i}")
    for elem in ("tray_lug_0", "tray_lug_1"):
        ctx.allow_overlap(tray, carriage, elem_a=elem, elem_b="carriage_plate",
                          reason="Tray pivot lug seats against the carriage plate.")
    ctx.allow_overlap(tray, carriage, elem_a="upper_slide_rail", elem_b="carriage_plate",
                      reason="The tray underside slide rail passes near the carriage plate at the tilt pivot.")
    for i in range(2):
        # Through the tray_tilt range the tray underside slide rail swings and
        # seats into the sibling carriage tilt-hinge lug (right beside the plate
        # it already grazes) — the same hinge-seat region, not a distant 穿模.
        ctx.allow_overlap(carriage, tray, elem_a=f"carriage_lug_{i}", elem_b="upper_slide_rail",
                          reason="Tray underside slide rail seats into the carriage tilt-hinge lug through the tray_tilt range.")
    ctx.expect_contact(tray, carriage, elem_a="tray_lug_0", elem_b="carriage_plate",
                       contact_tol=0.005, name="tray lug contacts carriage plate at tilt joint")
    spread = model.get_articulation("scissor_spread")
    rest = ctx.part_world_aabb(tray)
    with ctx.pose({spread: 0.70}):
        lifted = ctx.part_world_aabb(tray)
    ctx.check("scissor spread raises tray vertically",
              rest is not None and lifted is not None and lifted[0][2] > rest[0][2] + 0.020,
              details=f"rest={rest}, lifted={lifted}")
    return 48


_TEST_DISPATCH = {
    "fold_x_frame": _test_fold_x_frame,
    "prop_kickstand": _test_prop_kickstand,
    "wedge_riser": _test_wedge_riser,
    "pedestal_arm": _test_pedestal_arm,
    "telescoping_post": _test_telescoping_post,
    "scissor_lift": _test_scissor_lift,
    "central_spine": _test_central_spine,
}


def run_laptop_stand_tests(object_model: ArticulatedObject, config: LaptopStandConfig) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)

    # Universal identity: every form except the explicitly-static wedge riser
    # carries at least one real height/tilt/rotation articulation.
    non_fixed = [
        j for j in object_model.articulations
        if str(j.articulation_type).split(".")[-1] != "FIXED"
    ]
    if r.form != "wedge_riser":
        ctx.check("at least one real height/tilt/rotation articulation",
                  len(non_fixed) >= 1, details=f"non_fixed={[j.name for j in non_fixed]}")

    max_samples = _TEST_DISPATCH[r.form](ctx, object_model, r)

    # Rule 5 — no 穿模 across the full sampled motion envelope.
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=max_samples, ignore_fixed=True)
    return ctx.report()


__all__ = [
    "LaptopStandConfig",
    "ResolvedLaptopStandConfig",
    "config_from_seed",
    "resolve_config",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "build_laptop_stand",
    "build_seeded_laptop_stand",
    "run_laptop_stand_tests",
    "__modular__",
]
