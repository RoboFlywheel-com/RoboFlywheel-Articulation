# SPDX-License-Identifier: Apache-2.0

"""Bag / Suitcase / Box (storage box / chest) — modular procedural template.

Category identity: a single rectangular (or chamfered / long-narrow / shallow /
upright) plank-sided storage box / chest with metal corner fittings, closed by
**one main lid-closure mechanism** (the category headline axis), optionally
carrying a handle (rope / swing bail / rotating rings), a latch (hasp / clasp /
rotating plate) on the lid, and an interior mechanism (raised feet / front
drawer / lift-out tray / sliding divider / nesting feet).

Pattern: ``parallel_children`` — every slot hangs its parts/visuals off the
shared ``box_body`` root. The only true active main axis is ``lid_closure``,
which decides the main joint type (5 REVOLUTE variants + 1 PRISMATIC sliding
lid). ``handle_style`` may add a REVOLUTE pivot (bail / rings) or be pure
visual (rope). ``latch_style`` adds a REVOLUTE sub-hinge parented to the lid
(gated: only top-hinged ``box_lid`` lids carry a latch). ``interior_base`` adds
a PRISMATIC drawer / tray / divider, or pure-visual feet.

Sources: parent ``1a9c91ba`` (chassis + hinged_flat_top + rope + hasp + plank
wall) plus 20 workbench-only 5-star fork variants. See spec
``articraft_template_authoring/specs_modular_v1/Bag_Suitcase_Box.md``.

slot_choices_for_seed returns the 6-tuple
``(lid_closure, body_form, wall_style, handle_style, latch_style, interior_base)``
consumed by the ``module_topology_diversity`` gate.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, replace
from typing import Literal

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    Inertial,
    MeshGeometry,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    TorusGeometry,
    mesh_from_geometry,
)

__modular__ = True

LidClosure = Literal[
    "hinged_flat_top",
    "front_drop_panel",
    "split_double_leaf_top",
    "sliding_top_panel",
    "hinged_front_door",
    "arched_curved_top",
]
BodyForm = Literal[
    "rectangular_standard",
    "low_wide",
    "long_narrow_rounded_ends",
    "shallow_tray",
    "beveled_corner_posts",
]
WallStyle = Literal[
    "plank_sides",
    "ribbed_vertical_slats",
    "weathered_crate_corner_blocks",
    "reinforced_metal_straps",
]
HandleStyle = Literal["rope_side_handles", "swing_bail_handle", "rotating_side_rings"]
LatchStyle = Literal["none", "hasp_latch", "rotating_clasp_latch", "rotating_hasp_plate"]
InteriorBase = Literal[
    "plain",
    "raised_feet",
    "slide_out_front_drawer",
    "lift_out_inner_tray",
    "sliding_internal_divider",
    "nesting_stackable_feet",
]
MaterialStyle = Literal["rustic_wood", "blackened_travel", "weathered", "painted_steel"]

LID_CLOSURES: tuple[LidClosure, ...] = (
    "hinged_flat_top",
    "front_drop_panel",
    "split_double_leaf_top",
    "sliding_top_panel",
    "hinged_front_door",
    "arched_curved_top",
)
BODY_FORMS: tuple[BodyForm, ...] = (
    "rectangular_standard",
    "low_wide",
    "long_narrow_rounded_ends",
    "shallow_tray",
    "beveled_corner_posts",
)
WALL_STYLES: tuple[WallStyle, ...] = (
    "plank_sides",
    "ribbed_vertical_slats",
    "weathered_crate_corner_blocks",
    "reinforced_metal_straps",
)
HANDLE_STYLES: tuple[HandleStyle, ...] = (
    "rope_side_handles",
    "swing_bail_handle",
    "rotating_side_rings",
)
LATCH_STYLES: tuple[LatchStyle, ...] = (
    "none",
    "hasp_latch",
    "rotating_clasp_latch",
    "rotating_hasp_plate",
)
INTERIOR_BASES: tuple[InteriorBase, ...] = (
    "plain",
    "raised_feet",
    "slide_out_front_drawer",
    "lift_out_inner_tray",
    "sliding_internal_divider",
    "nesting_stackable_feet",
)
MATERIAL_STYLES: tuple[MaterialStyle, ...] = (
    "rustic_wood",
    "blackened_travel",
    "weathered",
    "painted_steel",
)

# Lids that emit a single top-hinged ``box_lid`` part whose forward edge reaches
# over the front face — the only lids a front latch (slot D2) can hang from.
# split_double_leaf is excluded: its forward leaf is a separate part and the
# rear ``box_lid`` leaf does not reach the front face.
_LATCHABLE_LIDS: frozenset[LidClosure] = frozenset({"hinged_flat_top", "arched_curved_top"})
# Interior mechanisms that need real internal depth; excluded on shallow trays.
_DEEP_INTERIORS: frozenset[InteriorBase] = frozenset(
    {"slide_out_front_drawer", "lift_out_inner_tray", "sliding_internal_divider"}
)
# Lids that frame a tall front panel/door — incompatible with a very shallow body.
_TALL_FRONT_LIDS: frozenset[LidClosure] = frozenset({"front_drop_panel", "hinged_front_door"})

PALETTES: dict[MaterialStyle, dict[str, tuple[float, float, float, float]]] = {
    "rustic_wood": {
        "wood": (0.62, 0.45, 0.26, 1.0),
        "wood_dark": (0.45, 0.32, 0.18, 1.0),
        "iron": (0.22, 0.22, 0.24, 1.0),
        "rope": (0.55, 0.45, 0.28, 1.0),
        "accent": (0.70, 0.52, 0.30, 1.0),
    },
    "blackened_travel": {
        "wood": (0.30, 0.27, 0.24, 1.0),
        "wood_dark": (0.18, 0.16, 0.15, 1.0),
        "iron": (0.12, 0.12, 0.13, 1.0),
        "rope": (0.40, 0.36, 0.30, 1.0),
        "accent": (0.36, 0.33, 0.30, 1.0),
    },
    "weathered": {
        "wood": (0.55, 0.52, 0.46, 1.0),
        "wood_dark": (0.38, 0.35, 0.30, 1.0),
        "iron": (0.30, 0.30, 0.31, 1.0),
        "rope": (0.52, 0.48, 0.40, 1.0),
        "accent": (0.62, 0.58, 0.50, 1.0),
    },
    "painted_steel": {
        "wood": (0.34, 0.40, 0.46, 1.0),
        "wood_dark": (0.24, 0.29, 0.34, 1.0),
        "iron": (0.66, 0.68, 0.70, 1.0),
        "rope": (0.40, 0.42, 0.44, 1.0),
        "accent": (0.50, 0.54, 0.58, 1.0),
    },
}


@dataclass(frozen=True)
class BagSuitcaseBoxConfig:
    lid_closure: LidClosure = "hinged_flat_top"
    body_form: BodyForm = "rectangular_standard"
    wall_style: WallStyle = "plank_sides"
    handle_style: HandleStyle = "rope_side_handles"
    latch_style: LatchStyle = "hasp_latch"
    interior_base: InteriorBase = "plain"
    material_style: MaterialStyle = "rustic_wood"
    box_w: float = 0.50
    box_d: float = 0.34
    box_h: float = 0.24
    joint_range_scale: float = 1.0
    name: str = "reference_bag_suitcase_box"


@dataclass(frozen=True)
class ResolvedBagSuitcaseBoxConfig:
    lid_closure: LidClosure
    body_form: BodyForm
    wall_style: WallStyle
    handle_style: HandleStyle
    latch_style: LatchStyle
    interior_base: InteriorBase
    material_style: MaterialStyle
    box_w: float
    box_d: float
    box_h: float
    wall_t: float
    lid_t: float
    floor_z: float  # top of feet / bottom of body cavity (z of inside floor base)
    foot_h: float
    joint_range_scale: float
    name: str


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


# ---------------------------------------------------------------------------
# Compatibility resolution: latch gated by lid, interior gated by body_form.
# ---------------------------------------------------------------------------
def _resolve_latch(lid_closure: LidClosure, latch_style: LatchStyle) -> LatchStyle:
    if lid_closure not in _LATCHABLE_LIDS:
        return "none"
    # The rotating clasp / hasp-plate latches are authored for a FLAT front lid
    # edge; the arched barrel-top curves its straps down over that edge, so those
    # latch arms 穿模 the lid. Only the hanging hasp (its own arched hasp_mount)
    # rides an arched lid, so fall arched rotating latches back to it.
    if lid_closure == "arched_curved_top" and latch_style in {
        "rotating_clasp_latch",
        "rotating_hasp_plate",
    }:
        return "hasp_latch"
    return latch_style


def _resolve_handle(
    lid_closure: LidClosure, body_form: BodyForm, handle_style: HandleStyle
) -> HandleStyle:
    """A top carry-bail stands over the lid's opening arc; gate it off tops that
    sweep up through it. Double-leaf tops raise a front leaf into the grip, and on
    the wide-shallow long box a top-hinged lid arcs up through the grip. Side rope
    handles are the safe fallback (front-opening / sliding tops keep the bail)."""
    if handle_style != "swing_bail_handle":
        return handle_style
    # Split double-leaf raises a front leaf into the grip; the arched barrel-top's
    # tall crown is swept by the down-swinging bail (worst on shallow/low boxes).
    if lid_closure in {"split_double_leaf_top", "arched_curved_top"}:
        return "rope_side_handles"
    if body_form == "long_narrow_rounded_ends" and lid_closure == "hinged_flat_top":
        return "rope_side_handles"
    return handle_style


def _latch_bearing_lid_part(lid_closure: LidClosure) -> str:
    """Name of the lid part a front latch hangs from, or "" if the lid is
    not latchable. Mirrors the value returned by ``_build_lid_closure``."""
    return "box_lid" if lid_closure in _LATCHABLE_LIDS else ""


def _resolve_interior(
    body_form: BodyForm, lid_closure: LidClosure, interior_base: InteriorBase
) -> InteriorBase:
    if body_form == "shallow_tray" and interior_base in _DEEP_INTERIORS:
        return "plain"
    # A tall front closure (drop-panel or hinged door) fills the whole front
    # opening; a front drawer needs that same opening as an open cavity, and the
    # QC samples the drawer-slide and lid joints independently, so an extended
    # drawer would 穿模 the shut front. They cannot share the front face, so
    # drop the drawer for any tall-front lid.
    if lid_closure in _TALL_FRONT_LIDS and interior_base == "slide_out_front_drawer":
        return "plain"
    return interior_base


def _resolve_body_form(lid_closure: LidClosure, body_form: BodyForm) -> BodyForm:
    # A very shallow tray cannot frame a tall front drop-panel/door; fall back
    # to the standard rectangular carcass for those lids.
    if lid_closure in _TALL_FRONT_LIDS and body_form == "shallow_tray":
        return "rectangular_standard"
    return body_form


def _body_h_band(body_form: BodyForm) -> tuple[float, float]:
    if body_form == "shallow_tray":
        return (0.080, 0.105)
    if body_form == "low_wide":
        return (0.140, 0.190)
    if body_form == "long_narrow_rounded_ends":
        return (0.180, 0.300)
    if body_form == "beveled_corner_posts":
        return (0.170, 0.300)
    return (0.180, 0.580)  # rectangular_standard supports upright cases too


def _body_w_band(body_form: BodyForm) -> tuple[float, float]:
    if body_form == "low_wide":
        return (0.60, 0.82)
    if body_form == "long_narrow_rounded_ends":
        return (0.70, 0.82)
    return (0.30, 0.62)


def config_from_seed(seed: int) -> BagSuitcaseBoxConfig:
    if seed == 0:
        return BagSuitcaseBoxConfig()

    rng = random.Random(seed)
    lid_closure = rng.choice(LID_CLOSURES)
    body_form = _resolve_body_form(lid_closure, rng.choice(BODY_FORMS))
    wall_style = rng.choice(WALL_STYLES)
    handle_style = _resolve_handle(lid_closure, body_form, rng.choice(HANDLE_STYLES))
    # latch is conditional on the lid; only offer non-none when latchable.
    if lid_closure in _LATCHABLE_LIDS:
        latch_style = _resolve_latch(lid_closure, rng.choice(LATCH_STYLES))
    else:
        latch_style = "none"
    interior_base = rng.choice(INTERIOR_BASES)
    interior_base = _resolve_interior(body_form, lid_closure, interior_base)

    w_lo, w_hi = _body_w_band(body_form)
    h_lo, h_hi = _body_h_band(body_form)
    box_w = round(rng.uniform(w_lo, w_hi), 3)
    if body_form == "long_narrow_rounded_ends":
        box_d = round(rng.uniform(0.20, 0.26), 3)
    else:
        box_d = round(rng.uniform(0.26, 0.40), 3)
    box_h = round(rng.uniform(h_lo, h_hi), 3)

    return BagSuitcaseBoxConfig(
        lid_closure=lid_closure,
        body_form=body_form,
        wall_style=wall_style,
        handle_style=handle_style,
        latch_style=latch_style,
        interior_base=interior_base,
        material_style=rng.choice(MATERIAL_STYLES),
        box_w=box_w,
        box_d=box_d,
        box_h=box_h,
        joint_range_scale=round(rng.uniform(0.85, 1.05), 4),
        name=f"seeded_bag_suitcase_box_{seed}",
    )


def resolve_config(config: BagSuitcaseBoxConfig | None = None) -> ResolvedBagSuitcaseBoxConfig:
    cfg = config or BagSuitcaseBoxConfig()
    lid_closure = _pick(cfg.lid_closure, LID_CLOSURES)
    body_form = _resolve_body_form(lid_closure, _pick(cfg.body_form, BODY_FORMS))
    wall_style = _pick(cfg.wall_style, WALL_STYLES)
    handle_style = _resolve_handle(lid_closure, body_form, _pick(cfg.handle_style, HANDLE_STYLES))
    material_style = _pick(cfg.material_style, MATERIAL_STYLES)
    latch_style = _resolve_latch(lid_closure, _pick(cfg.latch_style, LATCH_STYLES))
    interior_base = _resolve_interior(
        body_form, lid_closure, _pick(cfg.interior_base, INTERIOR_BASES)
    )

    w_lo, w_hi = _body_w_band(body_form)
    h_lo, h_hi = _body_h_band(body_form)
    box_w = _clamp(cfg.box_w, w_lo, w_hi)
    if body_form == "long_narrow_rounded_ends":
        box_d = _clamp(cfg.box_d, 0.20, 0.26)
    else:
        box_d = _clamp(cfg.box_d, 0.20, 0.40)
    box_h = _clamp(cfg.box_h, h_lo, h_hi)

    if body_form == "shallow_tray":
        wall_t = 0.012
        lid_t = 0.016
    elif material_style == "painted_steel":
        wall_t = 0.012
        lid_t = 0.030
    else:
        wall_t = 0.018
        lid_t = _clamp(0.040 * (box_h / 0.24), 0.022, 0.046)

    # Feet variants raise the body so the feet rest on the ground at z=0.
    if interior_base == "raised_feet":
        foot_h = 0.030
    elif interior_base == "nesting_stackable_feet":
        foot_h = 0.034
    else:
        foot_h = 0.0
    floor_z = foot_h

    return ResolvedBagSuitcaseBoxConfig(
        lid_closure=lid_closure,
        body_form=body_form,
        wall_style=wall_style,
        handle_style=handle_style,
        latch_style=latch_style,
        interior_base=interior_base,
        material_style=material_style,
        box_w=box_w,
        box_d=box_d,
        box_h=box_h,
        wall_t=wall_t,
        lid_t=lid_t,
        floor_z=floor_z,
        foot_h=foot_h,
        joint_range_scale=_clamp(cfg.joint_range_scale, 0.85, 1.05),
        name=cfg.name or "bag_suitcase_box",
    )


def with_overrides(config: BagSuitcaseBoxConfig, **kwargs: object) -> BagSuitcaseBoxConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: BagSuitcaseBoxConfig | ResolvedBagSuitcaseBoxConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedBagSuitcaseBoxConfig) else resolve_config(config)
    return (
        ("lid_closure", r.lid_closure),
        ("body_form", r.body_form),
        ("wall_style", r.wall_style),
        ("handle_style", r.handle_style),
        ("latch_style", r.latch_style),
        ("interior_base", r.interior_base),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------
def _joint_meta(joint_type, axis, origin, limits) -> dict[str, object]:
    return {
        "type": joint_type.value,
        "axis": axis,
        "origin": origin,
        "range": None if limits is None else (limits.lower, limits.upper),
    }


def _box(part, size, xyz, material, name: str, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(Box(size), origin=Origin(xyz=xyz, rpy=rpy), material=material, name=name, material_class_id="wood.natural_generic")


def _add_quad(geom: MeshGeometry, a: int, b: int, c: int, d: int) -> None:
    geom.add_face(a, b, c)
    geom.add_face(a, c, d)


def _arched_lid_mesh(
    width: float, depth: float, edge_h: float, rise: float, *, segments: int = 18
) -> MeshGeometry:
    """Closed shallow barrel-top prism, local rear hinge at y=0 and underside z=0."""
    half_w = width / 2.0
    y_front = -depth
    y_rear = 0.0
    top: list[tuple[float, float]] = []
    for i in range(segments + 1):
        t = i / segments
        y = y_front + (y_rear - y_front) * t
        z = edge_h + rise * math.sin(math.pi * t)
        top.append((y, z))
    section = [(y_front, 0.0), (y_rear, 0.0), top[-1], *reversed(top[:-1])]
    geom = MeshGeometry()
    left = [geom.add_vertex(-half_w, y, z) for y, z in section]
    right = [geom.add_vertex(half_w, y, z) for y, z in section]
    n = len(section)
    for i in range(n):
        j = (i + 1) % n
        _add_quad(geom, left[i], left[j], right[j], right[i])
    for i in range(1, n - 1):
        geom.add_face(left[0], left[i], left[i + 1])
        geom.add_face(right[0], right[i + 1], right[i])
    return geom


# ---------------------------------------------------------------------------
# Body chassis (root) — parameterized by body_form + wall_style.
# Coordinates: floor inside-base at z=floor_z; walls rise to floor_z+box_h.
# Front face is -Y, back face is +Y. The chassis omits walls that a lid module
# replaces (front for drop-panel / front-door; top for the front-door cube).
# ---------------------------------------------------------------------------
def _build_chassis(body, r: ResolvedBagSuitcaseBoxConfig, mats: dict) -> None:
    w, d, hb, t = r.box_w, r.box_d, r.box_h, r.wall_t
    z0 = r.floor_z
    cz = z0 + hb / 2.0
    wood = mats["wood"]
    wood_dark = mats["wood_dark"]
    iron = mats["iron"]

    drawer_front = r.interior_base == "slide_out_front_drawer"

    # Floor.
    _box(body, (w, d, t), (0.0, 0.0, z0 + t / 2.0), wood_dark, "floor_panel")

    # Back wall (always).
    _box(body, (w, t, hb), (0.0, (d / 2.0 - t / 2.0), cz), wood, "wall_back")
    # Side walls (always).
    _box(body, (t, d, hb), (-(w / 2.0 - t / 2.0), 0.0, cz), wood, "wall_left")
    _box(body, (t, d, hb), ((w / 2.0 - t / 2.0), 0.0, cz), wood, "wall_right")

    # Front wall — solid unless a front-opening lid or a front drawer rebuilds it.
    front_y = -(d / 2.0 - t / 2.0)
    if drawer_front:
        # Rebuild front as a drawer opening: sill + side stiles + upper rail.
        opening_bottom = z0 + 0.014
        opening_top = z0 + min(hb - 0.030, 0.118 + z0)
        opening_top = max(opening_top, opening_bottom + 0.05)
        sill_h = opening_bottom - z0
        rail_h = (z0 + hb) - opening_top
        opening_w = min(w - 4.0 * t, max(0.14, w * 0.64))
        stile_w = (w - opening_w) / 2.0
        if sill_h > 0.004:
            _box(body, (w, t, sill_h), (0.0, front_y, z0 + sill_h / 2.0), wood_dark, "front_sill")
        if rail_h > 0.004:
            _box(
                body,
                (w, t, rail_h),
                (0.0, front_y, opening_top + rail_h / 2.0),
                wood,
                "front_upper_rail",
            )
        for sx, tag in ((-1.0, "left"), (1.0, "right")):
            _box(
                body,
                (stile_w, t, opening_top - opening_bottom),
                (
                    sx * (opening_w / 2.0 + stile_w / 2.0),
                    front_y,
                    (opening_bottom + opening_top) / 2.0,
                ),
                wood,
                f"front_stile_{tag}",
            )
    elif r.lid_closure == "front_drop_panel":
        # Fixed front frame: top rail + bottom rail + two stiles; panel fills middle.
        rail = max(0.045, hb * 0.12)
        _box(body, (w, t, rail), (0.0, front_y, z0 + hb - rail / 2.0), wood_dark, "front_top_rail")
        _box(body, (w, t, rail), (0.0, front_y, z0 + rail / 2.0), wood_dark, "front_bottom_rail")
        for sx, tag in ((-1.0, "left"), (1.0, "right")):
            _box(
                body,
                (rail, t, hb),
                (sx * (w / 2.0 - rail / 2.0), front_y, cz),
                wood_dark,
                f"front_stile_{tag}",
            )
    elif r.lid_closure == "hinged_front_door":
        # Narrow fixed frame around the door opening + fixed top panel.
        _box(body, (w, t, 0.030), (0.0, front_y, z0 + 0.015), wood_dark, "front_sill")
        _box(body, (w, t, 0.030), (0.0, front_y, z0 + hb - 0.015), wood_dark, "front_header")
        _box(
            body,
            (0.030, t, hb),
            (-(w / 2.0 - 0.015), front_y, cz),
            wood_dark,
            "front_jamb_hinge",
        )
        _box(
            body,
            (0.030, t, hb),
            ((w / 2.0 - 0.015), front_y, cz),
            wood_dark,
            "front_jamb_latch",
        )
    else:
        _box(body, (w, t, hb), (0.0, front_y, cz), wood, "wall_front")

    # Fixed top for the front-door cube (the door is on the front, not the top).
    if r.lid_closure == "hinged_front_door":
        _box(body, (w, d, t), (0.0, 0.0, z0 + hb - t / 2.0), wood_dark, "top_panel")

    # Corner brackets at the four vertical edges (skip for ribbed/strap walls
    # which carry their own corner treatment).
    if r.wall_style not in {"reinforced_metal_straps"}:
        bk = 0.030
        idx = 0
        for sx in (-1.0, 1.0):
            for sy in (-1.0, 1.0):
                _box(
                    body,
                    (bk, bk, hb - 0.02),
                    (
                        sx * (w / 2.0 - bk / 2.0 + 0.003),
                        sy * (d / 2.0 - bk / 2.0 + 0.003),
                        cz,
                    ),
                    iron,
                    f"corner_bracket_{idx}",
                )
                idx += 1

    _build_wall_style(body, r, mats)
    _build_body_form_extras(body, r, mats)


def _build_wall_style(body, r: ResolvedBagSuitcaseBoxConfig, mats: dict) -> None:
    w, d, hb = r.box_w, r.box_d, r.box_h
    z0 = r.floor_z
    cz = z0 + hb / 2.0
    wood_dark = mats["wood_dark"]
    iron = mats["iron"]
    seam = mats["accent"]

    if r.wall_style == "plank_sides":
        # Vertical iron battens on the long faces + horizontal plank seams.
        for sx in (-0.13, 0.13):
            if abs(sx) < w / 2.0 - 0.04:
                _box(
                    body,
                    (0.028, d + 0.004, 0.008),
                    (sx, 0.0, cz),
                    iron,
                    f"batten_{'l' if sx < 0 else 'r'}",
                )
        for zt, tag in ((z0 + hb * 0.36, "lower"), (z0 + hb * 0.68, "upper")):
            _box(
                body,
                (w + 0.006, 0.004, 0.006),
                (0.0, d / 2.0 + 0.003, zt),
                seam,
                f"rear_plank_seam_{tag}",
            )
            _box(
                body,
                (0.004, d + 0.006, 0.006),
                (-w / 2.0 - 0.003, 0.0, zt),
                seam,
                f"side_plank_seam_l_{tag}",
            )
            _box(
                body,
                (0.004, d + 0.006, 0.006),
                (w / 2.0 + 0.003, 0.0, zt),
                seam,
                f"side_plank_seam_r_{tag}",
            )

    elif r.wall_style == "ribbed_vertical_slats":
        # Vertical slats on side + rear faces with top/bottom binding rails.
        n = 5
        for face, (axis_len, yfix, nx) in (
            ("rear", (w, d / 2.0 + 0.004, n)),
            ("left", (d, -(w / 2.0 + 0.004), n)),
            ("right", (d, (w / 2.0 + 0.004), n)),
        ):
            for i in range(nx):
                off = (-axis_len / 2.0 + axis_len * 0.12) + (axis_len * 0.76) * (i / (nx - 1))
                if face == "rear":
                    _box(
                        body,
                        (0.020, 0.008, hb - 0.04),
                        (off, yfix, cz),
                        wood_dark,
                        f"slat_{face}_{i}",
                    )
                else:
                    _box(
                        body,
                        (0.008, 0.020, hb - 0.04),
                        (yfix, off, cz),
                        wood_dark,
                        f"slat_{face}_{i}",
                    )
        # A front-hanging hasp passes the front rim on the centerline; build the
        # rail as a notched frame there so the lid latch arm clears it. Other
        # configs keep the original solid binding plate.
        front_hasp = r.latch_style in {"hasp_latch", "rotating_hasp_plate"}
        rw, rd = w + 0.010, d + 0.010
        notch, strip = 0.060, 0.040
        for zt, tag in ((z0 + 0.018, "bottom"), (z0 + hb - 0.018, "top")):
            if front_hasp:
                _box(
                    body,
                    (rw, strip, 0.012),
                    (0.0, rd / 2.0 - strip / 2.0, zt),
                    iron,
                    f"binding_rail_rear_{tag}",
                )
                for sx, side in ((-1.0, "l"), (1.0, "r")):
                    _box(
                        body,
                        (strip, rd - 2.0 * strip, 0.012),
                        (sx * (rw / 2.0 - strip / 2.0), 0.0, zt),
                        iron,
                        f"binding_rail_side_{side}_{tag}",
                    )
                    seg_w = (rw - notch) / 2.0
                    _box(
                        body,
                        (seg_w, strip, 0.012),
                        (sx * (notch / 2.0 + seg_w / 2.0), -(rd / 2.0 - strip / 2.0), zt),
                        iron,
                        f"binding_rail_front_{side}_{tag}",
                    )
            else:
                _box(body, (rw, rd, 0.012), (0.0, 0.0, zt), iron, f"binding_rail_{tag}")

    elif r.wall_style == "weathered_crate_corner_blocks":
        # Recessed dark backing strips + four raised corner blocks.
        for zt, tag in ((z0 + hb * 0.30, "lo"), (z0 + hb * 0.70, "hi")):
            _box(
                body,
                (w - 0.06, 0.008, 0.010),
                (0.0, d / 2.0 + 0.001, zt),
                wood_dark,
                f"crate_backing_rear_{tag}",
            )
        cb = 0.034
        idx = 0
        for sx in (-1.0, 1.0):
            for sy in (-1.0, 1.0):
                _box(
                    body,
                    (cb, cb, hb - 0.01),
                    (sx * (w / 2.0 - cb / 2.0 + 0.006), sy * (d / 2.0 - cb / 2.0 + 0.006), cz),
                    wood_dark,
                    f"corner_block_{idx}",
                )
                idx += 1

    else:  # reinforced_metal_straps (bands embed slightly into the walls)
        solid_front = r.lid_closure not in {"front_drop_panel", "hinged_front_door"} and (
            r.interior_base != "slide_out_front_drawer"
        )
        # A front-hanging latch (hasp/clasp) drops over the front centerline; the
        # full-width front band would foul its arm, so notch a center gap for it
        # (mirrors the ribbed_vertical_slats front-rail treatment).
        front_latch = r.latch_style != "none"
        band_w = w + 0.020
        for zt, tag in ((z0 + 0.045, "lower"), (z0 + hb - 0.045, "upper")):
            zt = _clamp(zt, z0 + 0.02, z0 + hb - 0.02)
            _box(body, (band_w, 0.016, 0.028), (0.0, d / 2.0 + 0.003, zt), iron, f"{tag}_rear_band")
            if solid_front:
                if front_latch:
                    notch = 0.090
                    seg = (band_w - notch) / 2.0
                    for sx, side in ((-1.0, "l"), (1.0, "r")):
                        _box(
                            body,
                            (seg, 0.016, 0.028),
                            (sx * (notch / 2.0 + seg / 2.0), -(d / 2.0 + 0.003), zt),
                            iron,
                            f"{tag}_front_band_{side}",
                        )
                else:
                    _box(
                        body,
                        (band_w, 0.016, 0.028),
                        (0.0, -(d / 2.0 + 0.003), zt),
                        iron,
                        f"{tag}_front_band",
                    )
            _box(
                body,
                (0.016, d + 0.020, 0.028),
                (-(w / 2.0 + 0.003), 0.0, zt),
                iron,
                f"{tag}_side_band_l",
            )
            _box(
                body,
                (0.016, d + 0.020, 0.028),
                ((w / 2.0 + 0.003), 0.0, zt),
                iron,
                f"{tag}_side_band_r",
            )
        for sx in (-0.14, 0.14):
            if abs(sx) < w / 2.0 - 0.03:
                _box(
                    body,
                    (0.028, d + 0.018, 0.016),
                    (sx, 0.0, cz),
                    iron,
                    f"vertical_strap_{'l' if sx < 0 else 'r'}",
                )


def _build_body_form_extras(body, r: ResolvedBagSuitcaseBoxConfig, mats: dict) -> None:
    w, d, hb = r.box_w, r.box_d, r.box_h
    z0 = r.floor_z
    cz = z0 + hb / 2.0
    iron = mats["iron"]
    wood_dark = mats["wood_dark"]

    if r.body_form == "long_narrow_rounded_ends":
        # Metal rolled-edge rim bands hugging the two short (X) ends. Kept a thin
        # band inset just behind the end face so side hardware (rings/bail) clears.
        band_r = min(d / 2.0 * 0.42, 0.045)
        for sx, tag in ((-1.0, "l"), (1.0, "r")):
            body.visual(
                Cylinder(radius=band_r, length=hb - 0.04),
                origin=Origin(xyz=(sx * (w / 2.0 - 0.020), 0.0, cz)),
                material=iron,
                name=f"end_cap_{tag}", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"rustic_wood", "blackened_travel", "painted_steel"} else "rust.oxidized_metal"),
            )
    elif r.body_form == "beveled_corner_posts":
        # 45-degree chamfer posts replacing square corner iron.
        post = 0.034
        idx = 0
        for sx in (-1.0, 1.0):
            for sy in (-1.0, 1.0):
                _box(
                    body,
                    (post, post, hb - 0.006),
                    (sx * (w / 2.0 - post / 2.0), sy * (d / 2.0 - post / 2.0), cz),
                    wood_dark,
                    f"chamfer_post_{idx}",
                    rpy=(0.0, 0.0, math.pi / 4.0),
                )
                idx += 1


# ---------------------------------------------------------------------------
# Hardware: rope handles (always built on body as visuals, except where bail /
# rings replace them).  Hasp keeper (on body front) when a latch is present.
# ---------------------------------------------------------------------------
def _build_rope_handles(body, r: ResolvedBagSuitcaseBoxConfig, mats: dict) -> None:
    w, hb = r.box_w, r.box_h
    z0 = r.floor_z
    rope = mats["rope"]
    iron = mats["iron"]
    hz = z0 + hb * 0.62
    for sx, tag in ((-1.0, "left"), (1.0, "right")):
        xface = sx * (w / 2.0)
        for sy in (-0.08, 0.08):
            _box(
                body,
                (0.032, 0.024, 0.03),
                (xface + sx * 0.013, sy, hz),
                iron,
                f"staple_{tag}_{'f' if sy < 0 else 'b'}",
            )
        body.visual(
            Cylinder(radius=0.010, length=0.20),
            origin=Origin(xyz=(xface + sx * 0.022, 0.0, hz), rpy=(1.5707963, 0.0, 0.0)),
            material=rope,
            name=f"rope_{tag}", material_class_id="organic.woven_plant_fiber",
        )


def _bail_pivot_z(r: ResolvedBagSuitcaseBoxConfig) -> float:
    return r.floor_z + r.box_h + r.lid_t + 0.028


def _build_bail_brackets(body, r: ResolvedBagSuitcaseBoxConfig, mats: dict) -> None:
    w, hb = r.box_w, r.box_h
    z0 = r.floor_z
    iron = mats["iron"]
    pivot_z = _bail_pivot_z(r)
    lug_z = z0 + hb - 0.020
    for sx, tag in ((-1.0, "left"), (1.0, "right")):
        xface = sx * (w / 2.0)
        # bracket plate embeds into the side wall (inner face slightly inside it).
        _box(
            body,
            (0.030, 0.095, 2.0 * (pivot_z - lug_z)),
            (xface + sx * 0.013, 0.0, (pivot_z + lug_z) / 2.0),
            iron,
            f"side_bracket_{tag}",
        )
        for yoff, lug in ((-0.032, "front"), (0.032, "rear")):
            _box(
                body,
                (0.032, 0.018, 0.018),
                (xface + sx * 0.015, yoff, lug_z),
                iron,
                f"bracket_lug_{tag}_{lug}",
            )
        body.visual(
            Cylinder(radius=0.018, length=0.030),
            origin=Origin(xyz=(xface + sx * 0.028, 0.0, pivot_z), rpy=(0.0, 1.5707963, 0.0)),
            material=iron,
            name=f"pivot_boss_{tag}", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"rustic_wood", "blackened_travel", "painted_steel"} else "rust.oxidized_metal"),
        )


def _build_ring_clevises(body, r: ResolvedBagSuitcaseBoxConfig, mats: dict) -> None:
    w, hb = r.box_w, r.box_h
    z0 = r.floor_z
    iron = mats["iron"]
    ring_z = z0 + hb * 0.62
    for sx, tag in ((-1.0, "0"), (1.0, "1")):
        xface = sx * (w / 2.0)
        # backplate embeds into the side wall so the ring hardware is supported.
        _box(
            body,
            (0.026, 0.120, 0.056),
            (xface + sx * 0.004, 0.0, ring_z),
            iron,
            f"side_{tag}_handle_plate",
        )
        _box(
            body,
            (0.032, 0.016, 0.058),
            (xface + sx * 0.026, -0.036, ring_z),
            iron,
            f"side_{tag}_clevis_0",
        )
        _box(
            body,
            (0.032, 0.016, 0.058),
            (xface + sx * 0.026, 0.036, ring_z),
            iron,
            f"side_{tag}_clevis_1",
        )
        body.visual(
            Cylinder(radius=0.007, length=0.105),
            origin=Origin(xyz=(xface + sx * 0.034, 0.0, ring_z), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=iron,
            name=f"side_{tag}_handle_pin", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"rustic_wood", "blackened_travel", "painted_steel"} else "rust.oxidized_metal"),
        )


def _build_handle(model, body, r: ResolvedBagSuitcaseBoxConfig, mats: dict) -> None:
    iron = mats["iron"]
    w = r.box_w
    scale = r.joint_range_scale
    if r.handle_style == "rope_side_handles":
        _build_rope_handles(body, r, mats)
        return

    if r.handle_style == "swing_bail_handle":
        _build_bail_brackets(body, r, mats)
        pivot_z = _bail_pivot_z(r)
        # The joint origin sits on the LEFT pivot boss (real hinge hardware); the
        # bail's part frame is therefore offset by -px in X so (0,0,0) lands on
        # that boss and the captured pin geometry surrounds it.
        px = -(w / 2.0 + 0.028)
        bail = model.part("bail_handle")
        bail.visual(
            Cylinder(radius=0.010, length=w + 0.106),
            origin=Origin(xyz=(-px, 0.0, 0.135), rpy=(0.0, 1.5707963, 0.0)),
            material=iron,
            name="top_grip", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"rustic_wood", "blackened_travel", "painted_steel"} else "rust.oxidized_metal"),
        )
        for sx, tag in ((-1.0, "left"), (1.0, "right")):
            bail.visual(
                Cylinder(radius=0.007, length=0.135),
                origin=Origin(xyz=(sx * (w / 2.0 + 0.053) - px, 0.0, 0.0675)),
                material=iron,
                name=f"side_arm_{tag}", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"rustic_wood", "blackened_travel", "painted_steel"} else "rust.oxidized_metal"),
            )
            bail.visual(
                Cylinder(radius=0.008, length=0.032),
                origin=Origin(
                    xyz=(sx * (w / 2.0 + 0.036) - px, 0.0, 0.0), rpy=(0.0, 1.5707963, 0.0)
                ),
                material=iron,
                name=f"pivot_pin_{tag}", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"rustic_wood", "blackened_travel", "painted_steel"} else "rust.oxidized_metal"),
            )
        limits = MotionLimits(effort=4.0, velocity=3.0, lower=0.0, upper=1.4 * scale)
        origin = (px, 0.0, pivot_z)
        model.articulation(
            "bail_pivot",
            ArticulationType.REVOLUTE,
            parent=body,
            child=bail,
            origin=Origin(xyz=origin),
            axis=(1.0, 0.0, 0.0),
            motion_limits=limits,
            meta=_joint_meta(ArticulationType.REVOLUTE, (1.0, 0.0, 0.0), origin, limits),
        )
        return

    # rotating_side_rings
    _build_ring_clevises(body, r, mats)
    ring_z = r.floor_z + r.box_h * 0.62
    ring_mesh = mesh_from_geometry(
        TorusGeometry(radius=0.058, tube=0.0075, radial_segments=14, tubular_segments=48),
        "bag_box_ring_handle",
    )
    for sx, name in ((-1.0, "ring_handle_0"), (1.0, "ring_handle_1")):
        ring = model.part(name)
        ring.visual(
            ring_mesh,
            origin=Origin(xyz=(0.0, 0.0, -0.058), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=iron,
            name="ring", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"rustic_wood", "blackened_travel", "painted_steel"} else "rust.oxidized_metal"),
        )
        ring.visual(
            Box((0.018, 0.030, 0.010)),
            origin=Origin(xyz=(0.0, 0.0, -0.003)),
            material=iron,
            name="top_saddle", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"rustic_wood", "blackened_travel", "painted_steel"} else "rust.oxidized_metal"),
        )
        # The ring loop (radius 0.058) is far larger than the pivot standoff
        # (0.034), so any INWARD swing sweeps the loop straight through the side
        # wall. Clamp each ring to lift only OUTWARD (away from the box): that is
        # +theta about +Y for the left ring and -theta for the right ring.
        swing = 1.30 * scale
        if sx < 0.0:
            lower, upper = 0.0, swing
        else:
            lower, upper = -swing, 0.0
        limits = MotionLimits(effort=4.0, velocity=4.0, lower=lower, upper=upper)
        origin = (sx * (r.box_w / 2.0 + 0.034), 0.0, ring_z)
        model.articulation(
            f"{name}_pivot",
            ArticulationType.REVOLUTE,
            parent=body,
            child=ring,
            origin=Origin(xyz=origin),
            axis=(0.0, 1.0, 0.0),
            motion_limits=limits,
            meta=_joint_meta(ArticulationType.REVOLUTE, (0.0, 1.0, 0.0), origin, limits),
        )


# ---------------------------------------------------------------------------
# Lid closures.  Each emits the lid part(s) + main joint and returns the name of
# the latch-bearing lid part (box_lid for top-hinged lids; "" otherwise).
# ---------------------------------------------------------------------------
def _flat_lid_panel(lid, r, mats, name="lid_panel", extra_top=True) -> None:
    w, d = r.box_w, r.box_d
    lt = r.lid_t
    wood = mats["wood"]
    iron = mats["iron"]
    # lid authored with its hinge edge (rear, +Y) at part-frame y=0; panel
    # extends forward (-Y) and the underside sits at z=0.
    lid.visual(
        Box((w + 0.02, d + 0.02, lt)),
        origin=Origin(xyz=(0.0, -d / 2.0, lt / 2.0)),
        material=wood,
        name=name, material_class_id=("metal.paint_coated" if r.material_style == "painted_steel" else "wood.mahogany_teak_dark"),
    )
    if extra_top:
        for sx in (-0.13, 0.13):
            if abs(sx) < w / 2.0 - 0.03:
                lid.visual(
                    Box((0.028, d + 0.02, 0.006)),
                    origin=Origin(xyz=(sx, -d / 2.0, lt + 0.003)),
                    material=iron,
                    name=f"lid_strap_{'l' if sx < 0 else 'r'}", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"rustic_wood", "blackened_travel", "painted_steel"} else "rust.oxidized_metal"),
                )
    # forward hasp mount tab (reaches over the front face to meet a latch).
    lid.visual(
        Box((0.05, 0.020, 0.016)),
        origin=Origin(xyz=(0.0, -(d + 0.003), lt * 0.5)),
        material=iron,
        name="hasp_mount", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"rustic_wood", "blackened_travel", "painted_steel"} else "rust.oxidized_metal"),
    )


def _build_lid_closure(model, body, r: ResolvedBagSuitcaseBoxConfig, mats: dict) -> str:
    w, d, hb, t = r.box_w, r.box_d, r.box_h, r.wall_t
    z0 = r.floor_z
    scale = r.joint_range_scale
    wood = mats["wood"]
    wood_dark = mats["wood_dark"]
    iron = mats["iron"]
    rim_z = z0 + hb

    if r.lid_closure == "hinged_flat_top":
        lid = model.part("box_lid")
        _flat_lid_panel(lid, r, mats)
        limits = MotionLimits(effort=15.0, velocity=2.0, lower=0.0, upper=2.1 * scale)
        origin = (0.0, d / 2.0, rim_z)
        model.articulation(
            "lid_hinge",
            ArticulationType.REVOLUTE,
            parent=body,
            child=lid,
            origin=Origin(xyz=origin),
            axis=(-1.0, 0.0, 0.0),
            motion_limits=limits,
            meta=_joint_meta(ArticulationType.REVOLUTE, (-1.0, 0.0, 0.0), origin, limits),
        )
        return "box_lid"

    if r.lid_closure == "arched_curved_top":
        # rear hinge plates/barrel on the body.
        for sx in (-0.13, 0.13):
            if abs(sx) >= w / 2.0 - 0.04:
                continue
            _box(
                body,
                (0.050, 0.014, 0.045),
                (sx, d / 2.0 + 0.007, rim_z - 0.018),
                iron,
                f"rear_hinge_plate_{'l' if sx < 0 else 'r'}",
            )
        lid = model.part("box_lid")
        edge_h = 0.036
        rise = 0.040
        lid.visual(
            mesh_from_geometry(
                _arched_lid_mesh(w + 0.022, d + 0.024, edge_h, rise), "arched_chest_lid_panel"
            ),
            origin=Origin(xyz=(0.0, 0.012, 0.0)),
            material=wood,
            name="arched_lid_panel", material_class_id=("metal.paint_coated" if r.material_style == "painted_steel" else "wood.mahogany_teak_dark"),
        )
        for sx in (-0.13, 0.13):
            if abs(sx) >= w / 2.0 - 0.03:
                continue
            lid.visual(
                mesh_from_geometry(
                    _arched_lid_mesh(0.028, d + 0.026, edge_h + 0.004, rise),
                    f"arched_lid_strap_{'l' if sx < 0 else 'r'}",
                ),
                origin=Origin(xyz=(sx, 0.013, 0.0)),
                material=iron,
                name=f"lid_strap_{'l' if sx < 0 else 'r'}", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"rustic_wood", "blackened_travel", "painted_steel"} else "rust.oxidized_metal"),
            )
        lid.visual(
            Box((0.05, 0.020, 0.016)),
            origin=Origin(xyz=(0.0, -(d + 0.003), edge_h * 0.5)),
            material=iron,
            name="hasp_mount", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"rustic_wood", "blackened_travel", "painted_steel"} else "rust.oxidized_metal"),
        )
        limits = MotionLimits(effort=15.0, velocity=2.0, lower=0.0, upper=2.1 * scale)
        origin = (0.0, d / 2.0, rim_z)
        model.articulation(
            "lid_hinge",
            ArticulationType.REVOLUTE,
            parent=body,
            child=lid,
            origin=Origin(xyz=origin),
            axis=(-1.0, 0.0, 0.0),
            motion_limits=limits,
            meta=_joint_meta(ArticulationType.REVOLUTE, (-1.0, 0.0, 0.0), origin, limits),
        )
        return "box_lid"

    if r.lid_closure == "split_double_leaf_top":
        lt = r.lid_t
        half_d = (d + 0.02) / 2.0
        seam = 0.004
        # rear leaf: hinge at back rim (+Y), extends forward to seam.
        rear = model.part("box_lid")  # primary latch-bearing leaf is the rear? use front leaf
        # Build rear leaf hinged at +Y.
        rear.visual(
            Box((w + 0.02, half_d - seam, lt)),
            origin=Origin(xyz=(0.0, -(half_d - seam) / 2.0, lt / 2.0)),
            material=wood,
            name="rear_leaf_panel", material_class_id=("metal.paint_coated" if r.material_style == "painted_steel" else "wood.mahogany_teak_dark"),
        )
        rlimits = MotionLimits(effort=12.0, velocity=2.0, lower=0.0, upper=1.9 * scale)
        rorigin = (0.0, d / 2.0, rim_z)
        model.articulation(
            "rear_leaf_hinge",
            ArticulationType.REVOLUTE,
            parent=body,
            child=rear,
            origin=Origin(xyz=rorigin),
            axis=(-1.0, 0.0, 0.0),
            motion_limits=rlimits,
            meta=_joint_meta(ArticulationType.REVOLUTE, (-1.0, 0.0, 0.0), rorigin, rlimits),
        )
        # front leaf hinged at front rim (-Y), extends rearward to seam.
        front = model.part("front_lid_leaf")
        front.visual(
            Box((w + 0.02, half_d - seam, lt)),
            origin=Origin(xyz=(0.0, (half_d - seam) / 2.0, lt / 2.0)),
            material=wood,
            name="front_leaf_panel", material_class_id=("metal.paint_coated" if r.material_style == "painted_steel" else "wood.mahogany_teak_dark"),
        )
        flimits = MotionLimits(effort=12.0, velocity=2.0, lower=0.0, upper=1.9 * scale)
        forigin = (0.0, -d / 2.0, rim_z)
        model.articulation(
            "front_leaf_hinge",
            ArticulationType.REVOLUTE,
            parent=body,
            child=front,
            origin=Origin(xyz=forigin),
            axis=(1.0, 0.0, 0.0),
            motion_limits=flimits,
            meta=_joint_meta(ArticulationType.REVOLUTE, (1.0, 0.0, 0.0), forigin, flimits),
        )
        return ""  # latch gated off for split (no single front-reaching leaf)

    if r.lid_closure == "sliding_top_panel":
        runner_h = 0.008
        lt = r.lid_t
        runner_w = 0.034
        rail_x = w / 2.0 - t - runner_w / 2.0
        rail_len = d + 0.060
        for sx, tag in ((-1.0, "left"), (1.0, "right")):
            _box(
                body,
                (runner_w, rail_len, runner_h),
                (sx * rail_x, 0.010, rim_z + runner_h / 2.0),
                wood_dark,
                f"lower_runner_{tag}",
            )
            _box(
                body,
                (runner_w, rail_len, 0.006),
                (sx * rail_x, 0.010, rim_z + runner_h + lt + 0.004),
                wood_dark,
                f"upper_lip_{tag}",
            )
            # The outer web spans from the box edge inward across the full groove
            # so it solidly supports both the lower runner and the upper lip.
            web_h = runner_h + lt + 0.009
            web_w = 0.028
            _box(
                body,
                (web_w, rail_len, web_h),
                (sx * (w / 2.0 - web_w / 2.0), 0.010, rim_z + web_h / 2.0),
                wood_dark,
                f"groove_web_{tag}",
            )
        _box(
            body,
            (w, 0.018, 0.007),
            (0.0, -(d / 2.0 + 0.009), rim_z + 0.0035),
            wood_dark,
            "front_lid_stop",
        )
        # Center support rib along the slide line so the prismatic joint origin
        # (at the lid mid-plane) sits on real body geometry at the box centerline.
        rib_h = runner_h + lt
        _box(
            body,
            (0.020, rail_len, rib_h),
            (0.0, 0.010, rim_z + rib_h / 2.0),
            wood_dark,
            "center_slide_rib",
        )
        lid = model.part("sliding_lid")
        lid.visual(
            Box((w - 2.0 * t - 0.010, d + 0.020, lt)),
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
            material=wood,
            name="lid_panel", material_class_id=("metal.paint_coated" if r.material_style == "painted_steel" else "wood.mahogany_teak_dark"),
        )
        lid.visual(
            Box((w - 2.0 * t - 0.070, 0.018, 0.014)),
            origin=Origin(xyz=(0.0, -(d / 2.0 + 0.018), 0.012)),
            material=wood_dark,
            name="pull_cleat", material_class_id=("wood.walnut_dark" if r.material_style in {"rustic_wood", "blackened_travel", "weathered"} else "metal.paint_coated"),
        )
        lid_z = rim_z + runner_h + lt / 2.0
        limits = MotionLimits(effort=12.0, velocity=0.6, lower=0.0, upper=0.135 * scale)
        origin = (0.0, 0.0, lid_z)
        model.articulation(
            "lid_slide",
            ArticulationType.PRISMATIC,
            parent=body,
            child=lid,
            origin=Origin(xyz=origin),
            axis=(0.0, 1.0, 0.0),
            motion_limits=limits,
            meta=_joint_meta(ArticulationType.PRISMATIC, (0.0, 1.0, 0.0), origin, limits),
        )
        return ""

    if r.lid_closure == "front_drop_panel":
        rail = max(0.045, hb * 0.12)
        gap = 0.004
        panel_h = hb - 2.0 * rail - 2.0 * gap
        panel_w = w - 2.0 * rail - 2.0 * gap
        # front staple keeper for the panel latch plate.
        _box(
            body,
            (0.04, 0.022, 0.03),
            (0.0, -(d / 2.0) - 0.011, z0 + hb - rail / 2.0),
            iron,
            "hasp_keeper",
        )
        panel = model.part("drop_panel")
        # panel authored with hinge at lower front edge (part frame z=0 at hinge).
        panel.visual(
            Box((panel_w, t, panel_h)),
            origin=Origin(xyz=(0.0, 0.0, panel_h / 2.0)),
            material=wood,
            name="drop_panel", material_class_id=("metal.paint_coated" if r.material_style == "painted_steel" else "wood.mahogany_teak_dark"),
        )
        for sx in (-0.075, 0.075):
            if abs(sx) < panel_w / 2.0 - 0.02:
                panel.visual(
                    Box((0.022, 0.010, panel_h - 0.06)),
                    origin=Origin(xyz=(sx, -0.010, panel_h / 2.0)),
                    material=iron,
                    name=f"panel_strap_{'l' if sx < 0 else 'r'}", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"rustic_wood", "blackened_travel", "painted_steel"} else "rust.oxidized_metal"),
                )
        panel.visual(
            Box((0.052, 0.012, 0.070)),
            origin=Origin(xyz=(0.0, -0.012, panel_h - 0.040)),
            material=iron,
            name="latch_plate", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"rustic_wood", "blackened_travel", "painted_steel"} else "rust.oxidized_metal"),
        )
        panel.visual(
            Box((panel_w, 0.008, 0.022)),
            origin=Origin(xyz=(0.0, 0.008, 0.008)),
            material=iron,
            name="bottom_hinge_leaf", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"rustic_wood", "blackened_travel", "painted_steel"} else "rust.oxidized_metal"),
        )
        limits = MotionLimits(effort=12.0, velocity=2.0, lower=0.0, upper=1.55 * scale)
        origin = (0.0, -(d / 2.0 + t / 2.0), z0 + rail)
        model.articulation(
            "panel_hinge",
            ArticulationType.REVOLUTE,
            parent=body,
            child=panel,
            origin=Origin(xyz=origin),
            axis=(1.0, 0.0, 0.0),
            motion_limits=limits,
            meta=_joint_meta(ArticulationType.REVOLUTE, (1.0, 0.0, 0.0), origin, limits),
        )
        return ""

    # hinged_front_door. The hinge joint origin is centered on the hinge line
    # (z = z0+hb/2); the door is authored in a LOCAL frame whose origin is on
    # that pivot, so child (0,0,0) lands on the door panel and a body hinge
    # knuckle sits at the same point (origin on real hinge hardware).
    door_t = 0.022
    front_y = -(d / 2.0 - t / 2.0)
    hinge_x = -w / 2.0
    hinge_y = front_y - 0.026
    zc = z0 + hb / 2.0
    # right-side keeper for the door hasp.
    _box(
        body,
        (0.070, 0.040, 0.040),
        (w / 2.0 + 0.018, front_y - 0.024, zc + 0.02),
        iron,
        "hasp_keeper",
    )
    # leaf bridges from the front jamb (at front_y) forward to the knuckle so the
    # whole hinge assembly is supported by the body shell.
    leaf_y = (front_y + hinge_y) / 2.0
    leaf_depth = abs(front_y - hinge_y) + 0.014
    for i, (zoff, length) in enumerate(((-hb * 0.30, 0.050), (0.0, 0.060), (hb * 0.30, 0.050))):
        zb = zc + zoff
        _box(
            body,
            (0.034, leaf_depth, length),
            (hinge_x + 0.010, leaf_y, zb),
            iron,
            f"body_hinge_leaf_{i}",
        )
        body.visual(
            Cylinder(radius=0.010, length=length),
            origin=Origin(xyz=(hinge_x, hinge_y, zb)),
            material=iron,
            name=f"body_hinge_knuckle_{i}", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"rustic_wood", "blackened_travel", "painted_steel"} else "rust.oxidized_metal"),
        )
    door = model.part("front_door")
    # door local frame: origin on the pivot; +x toward the latch jamb.
    door.visual(
        Box((w - 0.040, door_t, hb - 0.048)),
        origin=Origin(xyz=(w / 2.0, -0.006, 0.0)),
        material=wood,
        name="door_panel", material_class_id=("metal.paint_coated" if r.material_style == "painted_steel" else "wood.mahogany_teak_dark"),
    )
    for x, tag in ((w * 0.33, "lower"), (w * 0.67, "upper")):
        door.visual(
            Box((0.020, 0.008, hb - 0.070)),
            origin=Origin(xyz=(x, -0.016, 0.0)),
            material=iron,
            name=f"door_strap_{tag}", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"rustic_wood", "blackened_travel", "painted_steel"} else "rust.oxidized_metal"),
        )
    for i, zoff in enumerate((-hb * 0.16, 0.0, hb * 0.16)):
        door.visual(
            Box((0.040, 0.008, 0.060)),
            origin=Origin(xyz=(0.020, 0.004, zoff)),
            material=iron,
            name=f"door_hinge_leaf_{i}", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"rustic_wood", "blackened_travel", "painted_steel"} else "rust.oxidized_metal"),
        )
        door.visual(
            Cylinder(radius=0.010, length=0.060),
            origin=Origin(xyz=(0.0, 0.0, zoff)),
            material=iron,
            name=f"door_hinge_knuckle_{i}", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"rustic_wood", "blackened_travel", "painted_steel"} else "rust.oxidized_metal"),
        )
    # door-mounted hasp that bridges to the right keeper.
    door.visual(
        Box((0.030, 0.006, 0.040)),
        origin=Origin(xyz=(w - 0.075, -0.018, 0.02)),
        material=iron,
        name="door_hasp_arm", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"rustic_wood", "blackened_travel", "painted_steel"} else "rust.oxidized_metal"),
    )
    limits = MotionLimits(effort=10.0, velocity=2.0, lower=0.0, upper=1.65 * scale)
    origin = (hinge_x, hinge_y, zc)
    model.articulation(
        "door_hinge",
        ArticulationType.REVOLUTE,
        parent=body,
        child=door,
        origin=Origin(xyz=origin),
        axis=(0.0, 0.0, -1.0),
        motion_limits=limits,
        meta=_joint_meta(ArticulationType.REVOLUTE, (0.0, 0.0, -1.0), origin, limits),
    )
    return ""


# ---------------------------------------------------------------------------
# Latch (D2): parented to the lid (box_lid). Only built for latchable lids.
# Lid-frame: hinge edge of the top lid is at part-frame +Y rim; the latch hangs
# from the forward edge (around y=-(d)).
# ---------------------------------------------------------------------------
def _build_latch(model, r: ResolvedBagSuitcaseBoxConfig, lid_part_name: str, mats: dict) -> None:
    if r.latch_style == "none" or not lid_part_name:
        return
    d = r.box_d
    lt = r.lid_t
    z0 = r.floor_z
    hb = r.box_h
    scale = r.joint_range_scale
    iron = mats["iron"]
    body = model.get_part("box_body")
    lid = model.get_part(lid_part_name)

    if r.latch_style == "hasp_latch":
        arm_len = min(0.10, max(0.05, hb * 0.42))
        # The keeper staple is placed where the hanging hasp eye lands (so the
        # closed eye seats over it); on shallow boxes a fixed hb*0.45 keeper
        # would sit clear of the eye while the longer arm fouls the body.
        rim_z = z0 + hb
        eye_z = rim_z + lt * 0.5 - (arm_len + 0.008)
        _box(body, (0.04, 0.012, 0.03), (0.0, -(d / 2.0) - 0.006, eye_z), iron, "hasp_keeper")
        hasp = model.part("hasp")
        # arm authored toward the lid (+y) so its top overlaps the lid hasp_mount.
        hasp.visual(
            Box((0.05, 0.020, arm_len)),
            origin=Origin(xyz=(0.0, 0.008, -arm_len / 2.0)),
            material=iron,
            name="hasp_arm", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"rustic_wood", "blackened_travel", "painted_steel"} else "rust.oxidized_metal"),
        )
        hasp.visual(
            Box((0.024, 0.014, 0.018)),
            origin=Origin(xyz=(0.0, 0.0, -(arm_len + 0.008))),
            material=iron,
            name="hasp_eye", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"rustic_wood", "blackened_travel", "painted_steel"} else "rust.oxidized_metal"),
        )
        limits = MotionLimits(effort=3.0, velocity=3.0, lower=0.0, upper=1.4 * scale)
        origin = (0.0, -(d + 0.018), lt * 0.5)
        # The down-hanging arm must lift FORWARD (-Y, away from the box) when it
        # opens; a +X axis rotates it rearward into wall_front (穿模). -X swings
        # the arm off the front face. (Contract 3d: reversed-swing bug family.)
        model.articulation(
            "hasp_hinge",
            ArticulationType.REVOLUTE,
            parent=lid,
            child=hasp,
            origin=Origin(xyz=origin),
            axis=(-1.0, 0.0, 0.0),
            motion_limits=limits,
            meta=_joint_meta(ArticulationType.REVOLUTE, (-1.0, 0.0, 0.0), origin, limits),
        )
        return

    if r.latch_style == "rotating_clasp_latch":
        for i, x in enumerate((-0.13, 0.13)):
            if abs(x) >= r.box_w / 2.0 - 0.04:
                x = (r.box_w / 2.0 - 0.06) * (1 if x > 0 else -1)
            _box(
                body,
                (0.055, 0.012, 0.038),
                (x, -(d / 2.0) - 0.006, z0 + hb - 0.068),
                iron,
                f"clasp_keeper_{i}",
            )
            lid.visual(
                Box((0.060, 0.020, 0.016)),
                origin=Origin(xyz=(x, -(d + 0.003), lt * 0.5)),
                material=iron,
                name=f"clasp_mount_{i}", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"rustic_wood", "blackened_travel", "painted_steel"} else "rust.oxidized_metal"),
            )
            clasp = model.part(f"clasp_{i}")
            clasp.visual(
                Box((0.046, 0.010, 0.086)),
                origin=Origin(xyz=(0.0, 0.0, -0.043)),
                material=iron,
                name="clasp_arm", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"rustic_wood", "blackened_travel", "painted_steel"} else "rust.oxidized_metal"),
            )
            clasp.visual(
                Box((0.030, 0.014, 0.032)),
                origin=Origin(xyz=(0.0, -0.004, -0.079)),
                material=iron,
                name="clasp_hook", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"rustic_wood", "blackened_travel", "painted_steel"} else "rust.oxidized_metal"),
            )
            limits = MotionLimits(effort=2.0, velocity=3.0, lower=0.0, upper=1.35 * scale)
            origin = (x, -(d + 0.018), lt * 0.5)
            # Same reversed-swing family as the hasp: the arm must lift forward
            # (-Y) off the front face, so open about -X, not +X.
            model.articulation(
                f"clasp_hinge_{i}",
                ArticulationType.REVOLUTE,
                parent=lid,
                child=clasp,
                origin=Origin(xyz=origin),
                axis=(-1.0, 0.0, 0.0),
                motion_limits=limits,
                meta=_joint_meta(ArticulationType.REVOLUTE, (-1.0, 0.0, 0.0), origin, limits),
            )
        return

    # rotating_hasp_plate
    _box(
        body, (0.090, 0.010, 0.038), (0.0, -(d / 2.0) - 0.005, z0 + hb - 0.090), iron, "keeper_base"
    )
    _box(
        body,
        (0.010, 0.026, 0.036),
        (-0.038, -(d / 2.0) - 0.023, z0 + hb - 0.090),
        iron,
        "keeper_lug_0",
    )
    _box(
        body,
        (0.010, 0.026, 0.036),
        (0.038, -(d / 2.0) - 0.023, z0 + hb - 0.090),
        iron,
        "keeper_lug_1",
    )
    lid.visual(
        Box((0.070, 0.018, 0.026)),
        origin=Origin(xyz=(0.0, -(d + 0.004), lt * 0.5)),
        material=iron,
        name="hasp_pivot_mount", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"rustic_wood", "blackened_travel", "painted_steel"} else "rust.oxidized_metal"),
    )
    hasp = model.part("hasp")
    hasp.visual(
        Box((0.060, 0.010, 0.082)),
        origin=Origin(xyz=(0.0, -0.002, -0.041)),
        material=iron,
        name="hasp_plate", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"rustic_wood", "blackened_travel", "painted_steel"} else "rust.oxidized_metal"),
    )
    hasp.visual(
        Cylinder(radius=0.016, length=0.014),
        origin=Origin(xyz=(0.0, -0.003, 0.0), rpy=(1.5707963, 0.0, 0.0)),
        material=iron,
        name="hasp_pivot_disk", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"rustic_wood", "blackened_travel", "painted_steel"} else "rust.oxidized_metal"),
    )
    hasp.visual(
        Box((0.034, 0.014, 0.018)),
        origin=Origin(xyz=(0.0, -0.007, -0.067)),
        material=iron,
        name="hasp_catch", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"rustic_wood", "blackened_travel", "painted_steel"} else "rust.oxidized_metal"),
    )
    limits = MotionLimits(effort=3.0, velocity=3.0, lower=0.0, upper=1.55 * scale)
    origin = (0.0, -(d + 0.014), lt * 0.5)
    model.articulation(
        "hasp_hinge",
        ArticulationType.REVOLUTE,
        parent=lid,
        child=hasp,
        origin=Origin(xyz=origin),
        axis=(0.0, 1.0, 0.0),
        motion_limits=limits,
        meta=_joint_meta(ArticulationType.REVOLUTE, (0.0, 1.0, 0.0), origin, limits),
    )


# ---------------------------------------------------------------------------
# Interior base (E): feet (pure visual) or a PRISMATIC mechanism.
# ---------------------------------------------------------------------------
def _build_interior(model, body, r: ResolvedBagSuitcaseBoxConfig, mats: dict) -> None:
    w, d, hb, t = r.box_w, r.box_d, r.box_h, r.wall_t
    z0 = r.floor_z
    scale = r.joint_range_scale
    wood = mats["wood"]
    wood_dark = mats["wood_dark"]
    iron = mats["iron"]
    accent = mats["accent"]

    if r.interior_base == "plain":
        return

    if r.interior_base == "raised_feet":
        fw = 0.040
        fh = r.foot_h
        idx = 0
        for sx in (-1.0, 1.0):
            for sy in (-1.0, 1.0):
                _box(
                    body,
                    (fw, fw, fh),
                    (sx * (w / 2.0 - fw * 0.75), sy * (d / 2.0 - fw * 0.75), fh / 2.0),
                    wood_dark,
                    f"raised_foot_{idx}",
                )
                idx += 1
        # shallow interior tray ledge just below the rim.
        lip_h = 0.020
        lip_t = 0.014
        lip_z = z0 + hb - lip_h / 2.0 - 0.010
        _box(
            body,
            (w - 2 * t, lip_t, lip_h),
            (0.0, -(d / 2.0 - t - lip_t / 2.0), lip_z),
            wood_dark,
            "front_tray_lip",
        )
        _box(
            body,
            (w - 2 * t, lip_t, lip_h),
            (0.0, (d / 2.0 - t - lip_t / 2.0), lip_z),
            wood_dark,
            "back_tray_lip",
        )
        return

    if r.interior_base == "nesting_stackable_feet":
        fw = 0.052
        fh = r.foot_h
        idx = 0
        for sx in (-1.0, 1.0):
            for sy in (-1.0, 1.0):
                _box(
                    body,
                    (fw, fw * 0.88, fh),
                    (sx * (w / 2.0 - 0.070), sy * (d / 2.0 - 0.055), fh / 2.0),
                    wood_dark,
                    f"nesting_foot_{idx}",
                )
                idx += 1
        recess_t = 0.010
        _box(
            body,
            (w - 0.26, 0.012, recess_t),
            (0.0, -(d / 2.0 - 0.090), z0 + recess_t / 2.0),
            iron,
            "bottom_recess_front",
        )
        _box(
            body,
            (w - 0.26, 0.012, recess_t),
            (0.0, (d / 2.0 - 0.090), z0 + recess_t / 2.0),
            iron,
            "bottom_recess_back",
        )
        return

    if r.interior_base == "slide_out_front_drawer":
        drawer_w = min(0.32, w - 4.0 * t)
        drawer_d = min(0.22, d - 2.0 * t - 0.02)
        drawer_h = min(0.080, hb - 0.060)
        opening_bottom = z0 + 0.014
        # drawer runners inside the cavity, resting on the floor and embedding
        # into the side walls so they are supported.
        runner_h = 0.030
        runner_x = min(drawer_w / 2.0 + 0.012, w / 2.0 - t - 0.009)
        for sx, tag in ((-1.0, "left"), (1.0, "right")):
            _box(
                body,
                (0.022, drawer_d + 0.020, runner_h),
                (sx * runner_x, -d / 2.0 + drawer_d / 2.0, z0 + t + runner_h / 2.0),
                wood_dark,
                f"drawer_runner_{tag}",
            )
        drawer = model.part("front_drawer")
        # A full-front lid (drop panel / hinged door) closes over the front
        # opening, so the drawer face + pull must sit recessed behind the body
        # front plane; otherwise the protruding face overlaps the closed lid.
        front_lid_cover = r.lid_closure in _TALL_FRONT_LIDS
        if front_lid_cover:
            drawer_front_y = -d / 2.0 + 0.036  # face + pull tip stay behind -d/2
            pull_offset = 0.016
        else:
            drawer_front_y = -d / 2.0 - 0.012
            pull_offset = 0.016
        drawer_inner_y = -d / 2.0 + drawer_d / 2.0 - 0.002
        drawer_z = opening_bottom + drawer_h / 2.0 + 0.010
        drawer.visual(
            Box((drawer_w, 0.024, drawer_h)),
            origin=Origin(xyz=(0.0, drawer_front_y, drawer_z)),
            material=wood_dark,
            name="drawer_face", material_class_id=("wood.walnut_dark" if r.material_style in {"rustic_wood", "blackened_travel", "weathered"} else "metal.paint_coated"),
        )
        drawer.visual(
            Box((drawer_w * 0.90, drawer_d, 0.014)),
            origin=Origin(xyz=(0.0, drawer_inner_y, opening_bottom + 0.007)),
            material=wood,
            name="drawer_floor", material_class_id=("metal.paint_coated" if r.material_style == "painted_steel" else "wood.mahogany_teak_dark"),
        )
        for sx, tag in ((-1.0, "left"), (1.0, "right")):
            drawer.visual(
                Box((0.014, drawer_d, drawer_h * 0.78)),
                origin=Origin(
                    xyz=(
                        sx * (drawer_w * 0.45 - 0.007),
                        drawer_inner_y,
                        opening_bottom + drawer_h * 0.39,
                    )
                ),
                material=wood,
                name=f"drawer_side_{tag}", material_class_id=("metal.paint_coated" if r.material_style == "painted_steel" else "wood.mahogany_teak_dark"),
            )
        drawer.visual(
            Box((drawer_w * 0.90, 0.014, drawer_h * 0.78)),
            origin=Origin(
                xyz=(0.0, drawer_inner_y + drawer_d / 2.0 - 0.007, opening_bottom + drawer_h * 0.39)
            ),
            material=wood,
            name="drawer_back", material_class_id=("metal.paint_coated" if r.material_style == "painted_steel" else "wood.mahogany_teak_dark"),
        )
        drawer.visual(
            Cylinder(radius=0.014, length=0.032),
            origin=Origin(
                xyz=(0.0, drawer_front_y - pull_offset, drawer_z), rpy=(1.5707963, 0.0, 0.0)
            ),
            material=iron,
            name="drawer_pull", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"rustic_wood", "blackened_travel", "painted_steel"} else "rust.oxidized_metal"),
        )
        travel = min(0.145, drawer_d * 0.66)
        limits = MotionLimits(effort=20.0, velocity=0.5, lower=0.0, upper=travel * scale)
        origin = (0.0, 0.0, 0.0)
        model.articulation(
            "drawer_slide",
            ArticulationType.PRISMATIC,
            parent=body,
            child=drawer,
            origin=Origin(xyz=origin),
            axis=(0.0, -1.0, 0.0),
            motion_limits=limits,
            meta=_joint_meta(ArticulationType.PRISMATIC, (0.0, -1.0, 0.0), origin, limits),
        )
        return

    if r.interior_base == "lift_out_inner_tray":
        tray_w = w - 2.0 * t - 0.040
        tray_d = d - 2.0 * t - 0.040
        tray_floor_t = 0.012
        tray_h = min(0.060, hb * 0.26)
        rim = z0 + hb
        # The till rests low in the cavity and RAISES so its top comes just under
        # the rim — never above it into a closed lid. QC samples the tray-lift
        # and lid joints independently, so a "lift fully out of the box" pose
        # would 穿模 the shut lid; cap the travel at the rim instead.
        top_gap = 0.010
        rest_z = z0 + max(0.030, hb * 0.20)
        rest_top = rest_z + tray_floor_t + tray_h
        if rest_top > rim - top_gap - 0.010:
            rest_z = rim - top_gap - 0.010 - tray_floor_t - tray_h
        lift = (rim - top_gap) - (rest_z + tray_floor_t + tray_h)
        lift = max(0.02, min(lift, 0.140))
        rail_z = rest_z - 0.009
        for sx, tag in ((-1.0, "left"), (1.0, "right")):
            _box(
                body,
                (0.026, d - 2.0 * t, 0.018),
                (sx * (w / 2.0 - t - 0.013), 0.0, rail_z),
                wood_dark,
                f"inner_cleat_{tag}",
            )
        for sy, tag in ((-1.0, "front"), (1.0, "back")):
            _box(
                body,
                (w - 2.0 * t, 0.022, 0.018),
                (0.0, sy * (d / 2.0 - t - 0.011), rail_z),
                wood_dark,
                f"inner_cleat_{tag}",
            )
        # Center support cross-cleat under the tray gives the lift joint origin
        # real parent geometry at the box centerline.
        _box(body, (0.026, d - 2.0 * t, 0.018), (0.0, 0.0, rail_z), wood_dark, "inner_cleat_center")
        tray = model.part("lift_tray")
        # Tray frame: z=0 at the center cleat top (rail_z); floor underside sits
        # a touch above so it rests on the cleats at q=0.
        zf = rest_z - rail_z  # ~0.009
        tray.visual(
            Box((tray_w, tray_d, tray_floor_t)),
            origin=Origin(xyz=(0.0, 0.0, zf + tray_floor_t / 2.0)),
            material=accent,
            name="tray_floor", material_class_id=("metal.paint_coated" if r.material_style == "painted_steel" else "wood.rustic_weathered"),
        )
        for sy, tag in ((-1.0, "front"), (1.0, "back")):
            tray.visual(
                Box((tray_w, 0.014, tray_h)),
                origin=Origin(
                    xyz=(0.0, sy * (tray_d / 2.0 - 0.007), zf + tray_floor_t + tray_h / 2.0)
                ),
                material=accent,
                name=f"tray_{tag}", material_class_id=("metal.paint_coated" if r.material_style == "painted_steel" else "wood.rustic_weathered"),
            )
        for sx, tag in ((-1.0, "left"), (1.0, "right")):
            tray.visual(
                Box((0.014, tray_d, tray_h)),
                origin=Origin(
                    xyz=(sx * (tray_w / 2.0 - 0.007), 0.0, zf + tray_floor_t + tray_h / 2.0)
                ),
                material=accent,
                name=f"tray_{tag}", material_class_id=("metal.paint_coated" if r.material_style == "painted_steel" else "wood.rustic_weathered"),
            )
            tray.visual(
                Box((0.020, tray_d, tray_floor_t)),
                origin=Origin(xyz=(sx * (tray_w / 2.0 + 0.010), 0.0, zf + tray_floor_t / 2.0)),
                material=accent,
                name=f"tray_runner_{tag}", material_class_id=("metal.paint_coated" if r.material_style == "painted_steel" else "wood.rustic_weathered"),
            )
        limits = MotionLimits(effort=20.0, velocity=0.6, lower=0.0, upper=lift * scale)
        origin = (0.0, 0.0, rail_z)
        model.articulation(
            "tray_lift",
            ArticulationType.PRISMATIC,
            parent=body,
            child=tray,
            origin=Origin(xyz=origin),
            axis=(0.0, 0.0, 1.0),
            motion_limits=limits,
            meta=_joint_meta(ArticulationType.PRISMATIC, (0.0, 0.0, 1.0), origin, limits),
        )
        return

    # sliding_internal_divider. The divider is authored in a child frame whose
    # origin sits on the box floor centerline (z=0 == floor top), so the joint
    # origin lands on the real floor panel and the child frame includes (0,0,0).
    div_t = 0.018
    div_d = d - 2.0 * t - 0.040
    div_h = hb - 0.066
    floor_top = z0 + t
    rail_len = w - 2.0 * t
    rail_y = d / 2.0 - t - 0.007
    for sy, tag in ((-1.0, "front"), (1.0, "back")):
        _box(
            body,
            (rail_len, 0.014, 0.014),
            (0.0, sy * rail_y, floor_top + 0.008),
            wood_dark,
            f"divider_lower_rail_{tag}",
        )
        _box(
            body,
            (rail_len, 0.014, 0.012),
            (0.0, sy * rail_y, z0 + hb - 0.040),
            wood_dark,
            f"divider_upper_rail_{tag}",
        )
    divider = model.part("divider_panel")
    # local z: 0 at floor top. Board rises from ~0.016 to div_h.
    divider.visual(
        Box((div_t, div_d, div_h)),
        origin=Origin(xyz=(0.0, 0.0, 0.016 + div_h / 2.0)),
        material=wood_dark,
        name="divider_board", material_class_id=("wood.walnut_dark" if r.material_style in {"rustic_wood", "blackened_travel", "weathered"} else "metal.paint_coated"),
    )
    divider.visual(
        Box((div_t + 0.010, div_d + 0.012, 0.016)),
        origin=Origin(xyz=(0.0, 0.0, 0.016)),
        material=wood,
        name="lower_tongue", material_class_id=("metal.paint_coated" if r.material_style == "painted_steel" else "wood.mahogany_teak_dark"),
    )
    divider.visual(
        Box((div_t + 0.010, div_d + 0.012, 0.014)),
        origin=Origin(xyz=(0.0, 0.0, (z0 + hb - 0.040) - floor_top)),
        material=wood,
        name="upper_tongue", material_class_id=("metal.paint_coated" if r.material_style == "painted_steel" else "wood.mahogany_teak_dark"),
    )
    divider.visual(
        Cylinder(radius=0.010, length=0.070),
        origin=Origin(
            xyz=(0.0, -div_d / 2.0 - 0.006, 0.016 + div_h / 2.0), rpy=(0.0, 1.5707963, 0.0)
        ),
        material=iron,
        name="divider_finger_pull", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"rustic_wood", "blackened_travel", "painted_steel"} else "rust.oxidized_metal"),
    )
    span = w / 2.0 - t - div_t / 2.0 - 0.02
    limits = MotionLimits(effort=8.0, velocity=0.4, lower=-span * scale, upper=span * scale)
    origin = (0.0, 0.0, floor_top)
    model.articulation(
        "divider_slide",
        ArticulationType.PRISMATIC,
        parent=body,
        child=divider,
        origin=Origin(xyz=origin),
        axis=(1.0, 0.0, 0.0),
        motion_limits=limits,
        meta=_joint_meta(ArticulationType.PRISMATIC, (1.0, 0.0, 0.0), origin, limits),
    )


# ---------------------------------------------------------------------------
# Top-level build
# ---------------------------------------------------------------------------
def build_bag_suitcase_box(
    config: BagSuitcaseBoxConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    palette = PALETTES[r.material_style]
    mats = {
        key: model.material(f"bsb_{key}_{r.material_style}", rgba=palette[key])
        for key in ("wood", "wood_dark", "iron", "rope", "accent")
    }

    body = model.part("box_body")
    _build_chassis(body, r, mats)
    body.inertial = Inertial.from_geometry(
        Box((r.box_w, r.box_d, r.box_h)),
        mass=6.0 + r.box_w * r.box_d * 30.0,
        origin=Origin(xyz=(0.0, 0.0, r.floor_z + r.box_h / 2.0)),
    )

    lid_part = _build_lid_closure(model, body, r, mats)
    _build_handle(model, body, r, mats)
    _build_latch(model, r, lid_part, mats)
    _build_interior(model, body, r, mats)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_bag_suitcase_box(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_bag_suitcase_box(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests / allowances
# ---------------------------------------------------------------------------
def run_bag_suitcase_box_tests(
    object_model: ArticulatedObject,
    config: BagSuitcaseBoxConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    body = object_model.get_part("box_body")
    part_names = {p.name for p in object_model.parts}
    joint_names = {j.name for j in object_model.articulations}

    ctx.check("box_body present", "box_body" in part_names)
    ctx.check(
        "slot_choices recorded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    # --- Main lid joint present + correct type. ---
    if r.lid_closure == "hinged_flat_top":
        ctx.check("lid_hinge present", "lid_hinge" in joint_names)
        ctx.allow_overlap(
            body,
            object_model.get_part("box_lid"),
            reason="closed flat lid seats on the body rim (0-6 mm gap)",
        )
    elif r.lid_closure == "arched_curved_top":
        ctx.check("arched lid_hinge present", "lid_hinge" in joint_names)
        ctx.allow_overlap(
            body, object_model.get_part("box_lid"), reason="closed arched lid seats on the body rim"
        )
    elif r.lid_closure == "split_double_leaf_top":
        ctx.check(
            "split leaf hinges present", {"rear_leaf_hinge", "front_leaf_hinge"} <= joint_names
        )
        for leaf in ("box_lid", "front_lid_leaf"):
            ctx.allow_overlap(
                body, object_model.get_part(leaf), reason="closed lid leaf seats on the body rim"
            )
        ctx.allow_overlap(
            object_model.get_part("box_lid"),
            object_model.get_part("front_lid_leaf"),
            reason="the two leaves meet at the center seam when closed",
        )
    elif r.lid_closure == "sliding_top_panel":
        ctx.check("lid_slide prismatic present", "lid_slide" in joint_names)
        slide = object_model.get_articulation("lid_slide")
        ctx.check(
            "lid_slide is prismatic",
            slide.articulation_type == ArticulationType.PRISMATIC,
            details=str(slide.articulation_type),
        )
        ctx.allow_overlap(
            body,
            object_model.get_part("sliding_lid"),
            reason="sliding lid rides captured in the side runners and on the center rib",
        )
    elif r.lid_closure == "front_drop_panel":
        ctx.check("panel_hinge present", "panel_hinge" in joint_names)
        panel = object_model.get_part("drop_panel")
        ctx.allow_overlap(
            body,
            panel,
            elem_a="front_bottom_rail",
            elem_b="bottom_hinge_leaf",
            reason="the drop panel hinge leaf is seated in the fixed lower rail",
        )
        ctx.allow_overlap(body, panel, reason="closed drop panel fills the framed front opening")
    else:  # hinged_front_door
        ctx.check("door_hinge present", "door_hinge" in joint_names)
        door = object_model.get_part("front_door")
        # Interleaved hinge knuckles share the pivot line (captured hinge pin).
        ctx.allow_overlap(
            body,
            door,
            elem_a="body_hinge_knuckle_1",
            elem_b="door_hinge_knuckle_1",
            reason="body and door hinge knuckles interleave on the shared pivot pin",
        )
        ctx.allow_overlap(
            body, door, reason="closed front door seats against the fixed front frame"
        )

    # --- Handle. ---
    if r.handle_style == "swing_bail_handle":
        ctx.check("bail_pivot present", "bail_pivot" in joint_names)
        bail = object_model.get_part("bail_handle")
        for tag in ("left", "right"):
            ctx.allow_overlap(
                body,
                bail,
                elem_a=f"pivot_boss_{tag}",
                elem_b=f"pivot_pin_{tag}",
                reason="captured bail pivot pin rides inside the side pivot boss",
            )
            ctx.allow_overlap(
                body,
                bail,
                elem_a=f"side_bracket_{tag}",
                elem_b=f"pivot_pin_{tag}",
                reason="captured bail pivot pin passes through the mounting bracket",
            )
            ctx.allow_overlap(
                body,
                bail,
                elem_a=f"side_bracket_{tag}",
                elem_b=f"side_arm_{tag}",
                reason="bail side arm overlaps its mounting bracket at the pivot",
            )
    elif r.handle_style == "rotating_side_rings":
        for i in (0, 1):
            ctx.check(f"ring_handle_{i}_pivot present", f"ring_handle_{i}_pivot" in joint_names)
            ring = object_model.get_part(f"ring_handle_{i}")
            # Each ring must swing only OUTWARD (the loop is wider than its pivot
            # standoff; an inward swing sweeps through the side wall). Left ring
            # (i=0) opens +theta -> [0, +]; right ring (i=1) opens -theta -> [-, 0].
            pivot = object_model.get_articulation(f"ring_handle_{i}_pivot")
            lim = pivot.motion_limits
            if i == 0:
                ctx.check(
                    "left ring swings outward only (lower>=0)",
                    lim.lower >= 0.0 and lim.upper > 0.0,
                    details=f"({lim.lower}, {lim.upper})",
                )
            else:
                ctx.check(
                    "right ring swings outward only (upper<=0)",
                    lim.upper <= 0.0 and lim.lower < 0.0,
                    details=f"({lim.lower}, {lim.upper})",
                )
            ctx.allow_overlap(
                body,
                ring,
                elem_a=f"side_{i}_handle_pin",
                elem_b="ring",
                reason="ring threads over the captured clevis pin",
            )
            ctx.allow_overlap(
                body,
                ring,
                elem_a=f"side_{i}_handle_pin",
                elem_b="top_saddle",
                reason="captured clevis pin passes through the ring's top saddle",
            )
            ctx.allow_overlap(
                body,
                ring,
                elem_a=f"side_{i}_clevis_0",
                elem_b="ring",
                reason="ring passes between the clevis cheeks at the pin",
            )
            ctx.allow_overlap(
                body,
                ring,
                elem_a=f"side_{i}_clevis_1",
                elem_b="ring",
                reason="ring passes between the clevis cheeks at the pin",
            )
            ctx.allow_overlap(
                body,
                ring,
                elem_a=f"side_{i}_clevis_0",
                elem_b="top_saddle",
                reason="ring saddle straddles the clevis cheeks",
            )
            ctx.allow_overlap(
                body,
                ring,
                elem_a=f"side_{i}_clevis_1",
                elem_b="top_saddle",
                reason="ring saddle straddles the clevis cheeks",
            )
            ctx.allow_overlap(
                body,
                ring,
                elem_a=f"side_{i}_handle_plate",
                elem_b="ring",
                reason="ring hangs against its mounting backplate",
            )

    # --- Latch (on the lid). ---
    if r.latch_style == "hasp_latch":
        ctx.check("hasp_hinge present", "hasp_hinge" in joint_names)
        ctx.check(
            "hasp opens forward off the wall (axis -X)",
            tuple(object_model.get_articulation("hasp_hinge").axis) == (-1.0, 0.0, 0.0),
            details=str(object_model.get_articulation("hasp_hinge").axis),
        )
        hasp = object_model.get_part("hasp")
        lid_part = _latch_bearing_lid_part(r.lid_closure)
        lid_for_latch = object_model.get_part(lid_part) if lid_part else None
        ctx.allow_overlap(
            body,
            hasp,
            elem_a="hasp_keeper",
            elem_b="hasp_eye",
            reason="closed hasp eye seats over the body keeper staple",
        )
        ctx.allow_overlap(
            body,
            hasp,
            elem_a="hasp_keeper",
            elem_b="hasp_arm",
            reason="hasp arm straddles the keeper staple just above the captured eye",
        )
        if lid_for_latch is not None:
            ctx.allow_overlap(
                lid_for_latch,
                hasp,
                elem_a="hasp_mount",
                elem_b="hasp_arm",
                reason="hasp arm hangs from and overlaps the lid hasp mount tab",
            )
            ctx.allow_overlap(
                lid_for_latch, hasp, reason="closed hasp arm lies flat against the lid front edge"
            )
    elif r.latch_style == "rotating_clasp_latch":
        for i in (0, 1):
            ctx.check(f"clasp_hinge_{i} present", f"clasp_hinge_{i}" in joint_names)
            ctx.check(
                f"clasp_{i} opens forward off the wall (axis -X)",
                tuple(object_model.get_articulation(f"clasp_hinge_{i}").axis) == (-1.0, 0.0, 0.0),
                details=str(object_model.get_articulation(f"clasp_hinge_{i}").axis),
            )
            ctx.allow_overlap(
                body,
                object_model.get_part(f"clasp_{i}"),
                elem_a=f"clasp_keeper_{i}",
                elem_b="clasp_hook",
                reason="closed clasp hook seats over its front keeper",
            )
            lid_part = _latch_bearing_lid_part(r.lid_closure)
            if lid_part:
                ctx.allow_overlap(
                    object_model.get_part(lid_part),
                    object_model.get_part(f"clasp_{i}"),
                    elem_a=f"clasp_mount_{i}",
                    elem_b="clasp_arm",
                    reason="clasp arm hinges from and overlaps its lid mount tab",
                )
    elif r.latch_style == "rotating_hasp_plate":
        ctx.check("hasp_hinge plate present", "hasp_hinge" in joint_names)
        ctx.allow_overlap(
            body,
            object_model.get_part("hasp"),
            elem_a="keeper_base",
            elem_b="hasp_catch",
            reason="closed rotating hasp plate covers the front keeper",
        )
        lid_part = _latch_bearing_lid_part(r.lid_closure)
        if lid_part:
            lid_for_latch = object_model.get_part(lid_part)
            hasp = object_model.get_part("hasp")
            # The plate + pivot disk bear against the lid's front pivot tabs at the
            # hinge line; all element pairs there are pivot-bearing engagement.
            for tab in ("hasp_pivot_mount", "hasp_mount"):
                for part in ("hasp_plate", "hasp_pivot_disk"):
                    ctx.allow_overlap(
                        lid_for_latch,
                        hasp,
                        elem_a=tab,
                        elem_b=part,
                        reason="rotating hasp plate/disk pivots on its lid mount tab",
                    )
            # The pivot pin (disk) sits at the lid front edge and embeds slightly
            # into the panel it is mounted on.
            ctx.allow_overlap(
                lid_for_latch,
                hasp,
                elem_a="lid_panel",
                elem_b="hasp_pivot_disk",
                reason="rotating hasp pivot pin bears in the lid front edge",
            )

    # --- Interior mechanism. ---
    if r.interior_base == "slide_out_front_drawer":
        ctx.check("drawer_slide present", "drawer_slide" in joint_names)
        ctx.allow_overlap(
            body,
            object_model.get_part("front_drawer"),
            reason="drawer slides inside the cavity; closed face meets the front frame",
        )
    elif r.interior_base == "lift_out_inner_tray":
        ctx.check("tray_lift present", "tray_lift" in joint_names)
        ctx.allow_overlap(
            body,
            object_model.get_part("lift_tray"),
            reason="lift-out tray nests inside the cavity, resting on inner cleats",
        )
    elif r.interior_base == "sliding_internal_divider":
        ctx.check("divider_slide present", "divider_slide" in joint_names)
        ctx.allow_overlap(
            body,
            object_model.get_part("divider_panel"),
            reason="divider slides captured in the interior guide rails",
        )

    if "panel_hinge" in joint_names:
        ctx.allow_isolated_part(
            object_model.get_part("drop_panel"),
            reason="drop panel swings down on its hinge and loses body contact",
        )

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)
    return ctx.report()


__all__ = (
    "BagSuitcaseBoxConfig",
    "ResolvedBagSuitcaseBoxConfig",
    "build_bag_suitcase_box",
    "build_seeded_bag_suitcase_box",
    "config_from_seed",
    "resolve_config",
    "run_bag_suitcase_box_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
