# SPDX-License-Identifier: Apache-2.0

"""Procedural modular template for ``freestanding_security_safe``.

A freestanding (floor-standing) metal security safe: a fixed hollow
thick-walled box body (back / hinge-side / latch-side / top / bottom walls
with a front opening), a thick door hinged on the right vertical edge via a
``door_hinge`` REVOLUTE on a knuckle stack, a ``bolt_carriage`` PRISMATIC
(``bolt_slide``) carrying N locking bolts into bored strike pockets in the
latch wall, and door-face controls (a turn handle + a lock-entry interface),
plus optional interior layout and base stance.

Motion spine (world frame: +X = front, +Z = up)::

    safe_body --door_hinge(Z @ right knuckle stack)--> door
        |-- handle_spin (REVOLUTE, door-normal @ handle_boss) --> turn_handle
        |-- dial_spin(s) (CONTINUOUS, door-normal @ dial_boss) --> lock_entry
        |       (keypad variant: no dial_spin; 12 PRISMATIC button presses)
        |-- bolt_slide (PRISMATIC, latch-edge) --> bolt_carriage(N bolts)

Slots (deterministic per-seed sampling in ``config_from_seed``):

* ``turn_handle``  : four_spoke_wheel | tbar_handle | lever_handle
* ``lock_entry``   : rotary_dial | electronic_keypad | dual_rotary_dial
* ``interior_layout`` : single_shelf | no_shelf | pull_out_drawer
* ``base_stance``  : flush_bottom | leveling_feet | plinth_base
* ``bolt_count``   : weighted int multiplicity in [2, 6]
* ``palette_style``: charcoal_steel | gunmetal | sand_vault | navy_vault | brushed_inox

Decorative non-moving elements (feet, plinth skirt, bosses, index mark, gold
props, runners) are ``parent.visual(...)``, never FIXED-joint parts. Every
non-FIXED joint is anchored on a real visible parent face. Sophisticated
primitives from the parent / variant sources are preserved (KnobGeometry for
the dial knob, cadquery for the latch-wall pockets, drawer tray, leveling
foot, gold ingot).
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from math import cos, pi, sin
from typing import Literal

import cadquery as cq

from sdk import (
    AppearanceOnlySpec,
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    KnobGeometry,
    KnobGrip,
    KnobIndicator,
    MotionLimits,
    Origin,
    Sphere,
    TestContext,
    TestReport,
    max_joint_value,
    mesh_from_cadquery,
    mesh_from_geometry,
)

__modular__ = True


# ---------------------------------------------------------------------------
# Slot enums
# ---------------------------------------------------------------------------
TurnHandle = Literal["four_spoke_wheel", "tbar_handle", "lever_handle"]
LockEntry = Literal["rotary_dial", "electronic_keypad", "dual_rotary_dial"]
InteriorLayout = Literal["single_shelf", "no_shelf", "pull_out_drawer"]
BaseStance = Literal["flush_bottom", "leveling_feet", "plinth_base"]
PaletteStyle = Literal["charcoal_steel", "gunmetal", "sand_vault", "navy_vault", "brushed_inox"]

TURN_HANDLES: tuple[TurnHandle, ...] = (
    "four_spoke_wheel",
    "tbar_handle",
    "lever_handle",
)
LOCK_ENTRIES: tuple[LockEntry, ...] = (
    "rotary_dial",
    "electronic_keypad",
    "dual_rotary_dial",
)
INTERIOR_LAYOUTS: tuple[InteriorLayout, ...] = (
    "single_shelf",
    "no_shelf",
    "pull_out_drawer",
)
BASE_STANCES: tuple[BaseStance, ...] = (
    "flush_bottom",
    "leveling_feet",
    "plinth_base",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "charcoal_steel",
    "gunmetal",
    "sand_vault",
    "navy_vault",
    "brushed_inox",
)


# ---------------------------------------------------------------------------
# Palettes: each colorway maps the safe's material roles to rgba. Every
# `.visual(material=...)` is driven off the resolved palette so the batch
# seeds look colour-diverse rather than monochrome.
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "charcoal_steel": {
        "body": (0.16, 0.17, 0.18, 1.0),
        "door": (0.34, 0.35, 0.37, 1.0),
        "interior": (0.46, 0.47, 0.48, 1.0),
        "brushed": (0.68, 0.70, 0.72, 1.0),
        "polished": (0.80, 0.82, 0.85, 1.0),
        "silver": (0.85, 0.86, 0.88, 1.0),
        "black": (0.05, 0.05, 0.06, 1.0),
        "gold": (0.85, 0.66, 0.14, 1.0),
    },
    "gunmetal": {
        "body": (0.22, 0.24, 0.26, 1.0),
        "door": (0.30, 0.33, 0.36, 1.0),
        "interior": (0.40, 0.42, 0.45, 1.0),
        "brushed": (0.60, 0.63, 0.66, 1.0),
        "polished": (0.74, 0.78, 0.82, 1.0),
        "silver": (0.80, 0.82, 0.85, 1.0),
        "black": (0.06, 0.07, 0.08, 1.0),
        "gold": (0.88, 0.70, 0.20, 1.0),
    },
    "sand_vault": {
        "body": (0.55, 0.50, 0.40, 1.0),
        "door": (0.66, 0.61, 0.50, 1.0),
        "interior": (0.50, 0.46, 0.38, 1.0),
        "brushed": (0.74, 0.70, 0.60, 1.0),
        "polished": (0.84, 0.80, 0.70, 1.0),
        "silver": (0.80, 0.78, 0.72, 1.0),
        "black": (0.14, 0.12, 0.09, 1.0),
        "gold": (0.86, 0.68, 0.16, 1.0),
    },
    "navy_vault": {
        "body": (0.13, 0.18, 0.27, 1.0),
        "door": (0.18, 0.25, 0.36, 1.0),
        "interior": (0.30, 0.36, 0.44, 1.0),
        "brushed": (0.56, 0.62, 0.70, 1.0),
        "polished": (0.74, 0.80, 0.86, 1.0),
        "silver": (0.82, 0.84, 0.88, 1.0),
        "black": (0.04, 0.05, 0.08, 1.0),
        "gold": (0.90, 0.72, 0.22, 1.0),
    },
    "brushed_inox": {
        "body": (0.58, 0.60, 0.62, 1.0),
        "door": (0.70, 0.72, 0.74, 1.0),
        "interior": (0.52, 0.54, 0.56, 1.0),
        "brushed": (0.80, 0.82, 0.84, 1.0),
        "polished": (0.88, 0.90, 0.92, 1.0),
        "silver": (0.86, 0.88, 0.90, 1.0),
        "black": (0.14, 0.15, 0.16, 1.0),
        "gold": (0.84, 0.66, 0.18, 1.0),
    },
}


# ---------------------------------------------------------------------------
# Nominal geometry constants (parent compact_security_safe), in meters.
# Body outer envelope: 0.50 deep (X) x 0.50 wide (Y) x 0.55 tall (Z).
# ---------------------------------------------------------------------------
WALL = 0.045
NOM_BODY_X = 0.50
NOM_BODY_Y = 0.50
NOM_BODY_Z = 0.55

NOM_DOOR_THICK = 0.065

BOLT_R = 0.016
BOLT_LEN = 0.075
BOLT_STROKE = 0.032
POCKET_R = 0.018

KNUCKLE_R = 0.014
KNUCKLE_L = 0.06

# Base lifts derived per base_stance.
FOOT_R = 0.022
FOOT_H = 0.030
PLINTH_H = 0.045
PLINTH_INSET = 0.015
PLINTH_WALL = 0.012


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, float(value)))


def _clamp_int(value: int, low: int, high: int) -> int:
    return max(low, min(high, int(round(value))))


def _choice(value: str | None, choices: tuple[str, ...], fallback: str) -> str:
    if value in choices:
        return value
    return fallback


# ---------------------------------------------------------------------------
# Config dataclasses
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class FreestandingSecuritySafeConfig:
    turn_handle: TurnHandle | None = None
    lock_entry: LockEntry | None = None
    interior_layout: InteriorLayout | None = None
    base_stance: BaseStance | None = None
    palette_style: PaletteStyle = "charcoal_steel"
    bolt_count: int = 3
    body_width_scale: float = 1.0
    body_height_scale: float = 1.0
    body_depth_scale: float = 1.0
    door_thick_scale: float = 1.0
    name: str = "reference_freestanding_security_safe"


@dataclass(frozen=True)
class ResolvedFreestandingSecuritySafeConfig:
    turn_handle: TurnHandle
    lock_entry: LockEntry
    interior_layout: InteriorLayout
    base_stance: BaseStance
    palette_style: PaletteStyle
    bolt_count: int
    # Resolved envelope.
    body_x: float
    body_y: float
    body_z: float
    door_thick: float
    base_lift: float
    # Derived door layout (hinge-local frame).
    hinge_x: float
    hinge_y: float
    hinge_z: float
    door_w: float
    door_h: float
    door_cy: float
    door_x_out: float
    door_x_in: float
    door_edge_y: float
    door_knuckle_zs: tuple[float, ...]
    body_knuckle_zs: tuple[float, ...]
    bolt_zs: tuple[float, ...]
    pocket_cx: float
    pocket_cy: float
    carriage_origin_y: float
    dial_z: float
    handle_z: float
    face_cy: float
    name: str


def resolve_config(
    config: FreestandingSecuritySafeConfig,
) -> ResolvedFreestandingSecuritySafeConfig:
    turn_handle = _choice(config.turn_handle, TURN_HANDLES, "four_spoke_wheel")
    lock_entry = _choice(config.lock_entry, LOCK_ENTRIES, "rotary_dial")
    interior_layout = _choice(config.interior_layout, INTERIOR_LAYOUTS, "single_shelf")
    base_stance = _choice(config.base_stance, BASE_STANCES, "flush_bottom")
    palette_style = _choice(config.palette_style, PALETTE_STYLES, "charcoal_steel")

    wsc = _clamp(config.body_width_scale, 0.85, 1.15)
    hsc = _clamp(config.body_height_scale, 0.85, 1.20)
    dsc = _clamp(config.body_depth_scale, 0.85, 1.15)
    tsc = _clamp(config.door_thick_scale, 0.85, 1.20)

    body_x = NOM_BODY_X * dsc
    body_y = NOM_BODY_Y * wsc
    body_z = NOM_BODY_Z * hsc
    door_thick = NOM_DOOR_THICK * tsc

    # Base lift derived from base_stance: feet/plinth raise the whole assembly
    # so the lowest point sits on the floor (z=0). Added to EVERY z anchor.
    if base_stance == "leveling_feet":
        base_lift = FOOT_H
    elif base_stance == "plinth_base":
        base_lift = PLINTH_H
    else:
        base_lift = 0.0

    half_y = body_y / 2.0

    hinge_x = body_x / 2.0 + 0.012  # hinge axis sits slightly proud of front
    hinge_y = half_y - WALL / 2.0  # centered on the right wall thickness
    hinge_z = body_z / 2.0 + base_lift

    # Door leaf width spans the opening minus the two side-wall thicknesses
    # and a small jamb clearance on each side.
    door_w = body_y - 2.0 * WALL - 0.015
    door_h = body_z - 2.0 * WALL - 0.010
    # Door leaf center in hinge-local Y: the hinge is at +Y, leaf extends -Y.
    door_cy = -(door_w / 2.0 + (half_y - hinge_y) + 0.001)
    door_x_out = -0.007
    door_x_in = door_x_out - door_thick
    door_edge_y = door_cy - door_w / 2.0  # free (latch) edge, hinge-local Y

    # Door / body hinge knuckle stacks interleave end-to-end along the hinge
    # axis: a 5-barrel stack centered on hinge_z with spacing == KNUCKLE_L so
    # adjacent door/body barrels touch (door at k=-2,0,+2; body at k=-1,+1).
    door_knuckle_zs = (-2.0 * KNUCKLE_L, 0.0, 2.0 * KNUCKLE_L)
    body_knuckle_zs = (
        hinge_z - KNUCKLE_L,
        hinge_z + KNUCKLE_L,
    )

    # Bolt rows evenly distributed over the door height. The count is clamped
    # so adjacent bolts keep >= 2*BOLT_R + gap spacing even when the body is
    # scaled short.
    bolt_extent = door_h * 0.36
    min_spacing = 2.0 * BOLT_R + 0.012
    max_count = max(2, int(2.0 * bolt_extent / min_spacing) + 1)
    bolt_count = _clamp_int(config.bolt_count, 2, min(6, max_count))
    if bolt_count <= 1:
        bolt_zs = (0.0,)
    else:
        step = (2.0 * bolt_extent) / float(bolt_count - 1)
        bolt_zs = tuple(-bolt_extent + step * i for i in range(bolt_count))

    # Strike-pocket bore center in latch-wall-local frame (the latch wall part
    # frame is at the body's -Y wall center). The bore sits near the front
    # opening (positive wall-local X) so the door bolts can reach it, and the
    # cut starts just inside the inner wall face.
    pocket_cx = body_x * 0.445
    pocket_cy = -WALL / 2.0 + 0.005

    carriage_origin_y = door_edge_y - 0.001

    dial_z = door_h * 0.22
    # Handle sits well below the dial band so a swinging handle (t-bar / lever
    # reaching straight up) keeps clear of the combination dial(s) above it,
    # even on the shortest sampled door.
    handle_z = -door_h * 0.24
    face_cy = door_cy

    return ResolvedFreestandingSecuritySafeConfig(
        turn_handle=turn_handle,  # type: ignore[arg-type]
        lock_entry=lock_entry,  # type: ignore[arg-type]
        interior_layout=interior_layout,  # type: ignore[arg-type]
        base_stance=base_stance,  # type: ignore[arg-type]
        palette_style=palette_style,  # type: ignore[arg-type]
        bolt_count=bolt_count,
        body_x=body_x,
        body_y=body_y,
        body_z=body_z,
        door_thick=door_thick,
        base_lift=base_lift,
        hinge_x=hinge_x,
        hinge_y=hinge_y,
        hinge_z=hinge_z,
        door_w=door_w,
        door_h=door_h,
        door_cy=door_cy,
        door_x_out=door_x_out,
        door_x_in=door_x_in,
        door_edge_y=door_edge_y,
        door_knuckle_zs=door_knuckle_zs,
        body_knuckle_zs=body_knuckle_zs,
        bolt_zs=bolt_zs,
        pocket_cx=pocket_cx,
        pocket_cy=pocket_cy,
        carriage_origin_y=carriage_origin_y,
        dial_z=dial_z,
        handle_z=handle_z,
        face_cy=face_cy,
        name=str(config.name or "freestanding_security_safe"),
    )


# ---------------------------------------------------------------------------
# Deterministic per-seed sampler
# ---------------------------------------------------------------------------
def config_from_seed(seed: int) -> FreestandingSecuritySafeConfig:
    rng = random.Random(seed)
    turn_handle = rng.choice(TURN_HANDLES)
    lock_entry = rng.choice(LOCK_ENTRIES)
    interior_layout = rng.choice(INTERIOR_LAYOUTS)
    base_stance = rng.choice(BASE_STANCES)
    palette_style = rng.choice(PALETTE_STYLES)
    bolt_count = rng.choices([2, 3, 4, 5, 6], weights=[3, 4, 3, 2, 1])[0]
    return FreestandingSecuritySafeConfig(
        turn_handle=turn_handle,
        lock_entry=lock_entry,
        interior_layout=interior_layout,
        base_stance=base_stance,
        palette_style=palette_style,
        bolt_count=bolt_count,
        body_width_scale=rng.uniform(0.88, 1.12),
        body_height_scale=rng.uniform(0.88, 1.16),
        body_depth_scale=rng.uniform(0.88, 1.12),
        door_thick_scale=rng.uniform(0.90, 1.15),
        name=f"seeded_freestanding_security_safe_{seed}",
    )


def slot_choices_for_config(
    config: FreestandingSecuritySafeConfig,
) -> list[tuple[str, str]]:
    r = resolve_config(config)
    return [
        ("turn_handle", r.turn_handle),
        ("lock_entry", r.lock_entry),
        ("interior_layout", r.interior_layout),
        ("base_stance", r.base_stance),
        ("palette_style", r.palette_style),
        ("bolt_multiplicity", f"{r.bolt_count}_bolts"),
    ]


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Mesh helpers (preserve parent / variant cadquery primitives)
# ---------------------------------------------------------------------------
def _ingot_mesh():
    """Trapezoid-section gold ingot, base 0.055 x 0.14, 0.034 tall, base at z=0."""
    solid = (
        cq.Workplane("XY")
        .rect(0.055, 0.14)
        .workplane(offset=0.034)
        .rect(0.042, 0.118)
        .loft(combine=True)
    )
    return mesh_from_cadquery(solid, "gold_ingot")


def _latch_wall_mesh(r: ResolvedFreestandingSecuritySafeConfig):
    """Latch-side wall with N bored strike pockets that receive the door bolts.

    Built in latch-wall-local frame (part origin at the -Y wall center). The
    SAME ``r.bolt_zs`` list drives both this pocket loop and the carriage bolt
    loop so pocket count stays in lockstep with bolt_count.
    """
    wall = cq.Workplane("XY").box(r.body_x, WALL, r.body_z)
    for zr in r.bolt_zs:
        pocket = cq.Solid.makeCylinder(
            POCKET_R,
            0.06,
            cq.Vector(r.pocket_cx, r.pocket_cy, zr),
            cq.Vector(0.0, 1.0, 0.0),
        )
        wall = wall.cut(pocket)
    return mesh_from_cadquery(wall, "side_wall_latch")


def _drawer_dims(r: ResolvedFreestandingSecuritySafeConfig) -> tuple[float, float, float]:
    """Drawer tray (depth_x, width_y, origin_x) sized to fit the cavity.

    The tray is set back against the back wall at rest (q=0) and fills only
    about half the usable cavity depth, so the drawer can slide a meaningful
    distance forward (+X) BEFORE its front edge reaches the closed-door plane.
    Motion-QC samples ``drawer_slide`` independently of ``door_hinge``, so the
    extended tray must never pass the back face of the closed door's inner
    panel; the front travel room here plus the solver clamp on ``drawer_slide``
    guarantee that. ``origin_x`` is the tray center == the joint origin.
    """
    half_x = r.body_x / 2.0
    back_inner_x = -half_x + WALL
    # Tray back edge clears the back wall by ~10 mm at rest.
    gap_back = 0.010
    # Forward clear boundary in body-local X: the min-X (back) face of the
    # closed door's inner panel, which projects ~door_thick into the cavity.
    # door_inner_panel min-x face = hinge_x + door_x_in - 0.011 (see _build_door).
    front_clear = r.hinge_x + r.door_x_in - 0.011
    usable = front_clear - (back_inner_x + gap_back)
    # Tray fills ~half the usable depth; the rest is forward travel room.
    td = usable * 0.50
    origin_x = back_inner_x + gap_back + td / 2.0
    tw = r.body_y * 0.72
    return td, tw, origin_x


def _drawer_tray_mesh(r: ResolvedFreestandingSecuritySafeConfig):
    """Open-top cash drawer tray: full-footprint base plate, four walls."""
    td, tw, _ = _drawer_dims(r)
    outer = cq.Workplane("XY").box(td, tw, 0.106, centered=(True, True, False))
    inner = (
        cq.Workplane("XY")
        .workplane(offset=0.006)
        .box(td - 0.012, tw - 0.012, 0.100, centered=(True, True, False))
    )
    return mesh_from_cadquery(outer.cut(inner), "drawer_tray")


def _leveling_foot_mesh():
    """Short brushed-steel leveling foot: cylinder with a chamfered base edge."""
    foot = cq.Workplane("XY").circle(FOOT_R).extrude(FOOT_H)
    foot = foot.edges("<Z").chamfer(0.003)
    return mesh_from_cadquery(foot, "leveling_foot")


def _dial_knob_mesh(name: str):
    """Black fluted knob cap with engraved tick indicator (parent KnobGeometry)."""
    return mesh_from_geometry(
        KnobGeometry(
            0.064,
            0.022,
            body_style="cylindrical",
            edge_radius=0.0012,
            grip=KnobGrip(style="fluted", count=24, depth=0.0012),
            indicator=KnobIndicator(style="line", mode="engraved", depth=0.0008),
            center=False,
        ),
        name,
    )


# ---------------------------------------------------------------------------
# Body (interior + base stance inlined as visuals)
# ---------------------------------------------------------------------------
def _build_body(
    model: ArticulatedObject,
    r: ResolvedFreestandingSecuritySafeConfig,
    m: dict[str, str],
):
    body = model.part("safe_body")
    lift = r.base_lift
    half_x = r.body_x / 2.0
    half_y = r.body_y / 2.0
    body_mid_z = r.body_z / 2.0 + lift

    # ----- six-face hollow box (front open) -----
    body.visual(
        Box((WALL, r.body_y, r.body_z)),
        origin=Origin(xyz=(-half_x + WALL / 2.0, 0.0, body_mid_z)),
        material=m["body"],
        name="back_wall", material_class_id=("metal.paint_coated" if r.palette_style in {"charcoal_steel", "sand_vault", "navy_vault", "brushed_inox"} else "metal.blackened_gunmetal"),
    )
    body.visual(
        Box((r.body_x, WALL, r.body_z)),
        origin=Origin(xyz=(0.0, half_y - WALL / 2.0, body_mid_z)),
        material=m["body"],
        name="side_wall_hinge", material_class_id=("metal.paint_coated" if r.palette_style in {"charcoal_steel", "sand_vault", "navy_vault", "brushed_inox"} else "metal.blackened_gunmetal"),
    )
    body.visual(
        _latch_wall_mesh(r),
        origin=Origin(xyz=(0.0, -half_y + WALL / 2.0, body_mid_z)),
        material=m["body"],
        name="side_wall_latch", material_class_id=("metal.paint_coated" if r.palette_style in {"charcoal_steel", "sand_vault", "navy_vault", "brushed_inox"} else "metal.blackened_gunmetal"),
    )
    body.visual(
        Box((r.body_x, r.body_y, WALL)),
        origin=Origin(xyz=(0.0, 0.0, r.body_z - WALL / 2.0 + lift)),
        material=m["body"],
        name="top_wall", material_class_id=("metal.paint_coated" if r.palette_style in {"charcoal_steel", "sand_vault", "navy_vault", "brushed_inox"} else "metal.blackened_gunmetal"),
    )
    body.visual(
        Box((r.body_x, r.body_y, WALL)),
        origin=Origin(xyz=(0.0, 0.0, WALL / 2.0 + lift)),
        material=m["body"],
        name="bottom_wall", material_class_id=("metal.paint_coated" if r.palette_style in {"charcoal_steel", "sand_vault", "navy_vault", "brushed_inox"} else "metal.blackened_gunmetal"),
    )

    # ----- interior layout (Slot C) -----
    _build_interior(body, r, m)

    # ----- body-side hinge knuckles + straps -----
    for i, zk in enumerate(r.body_knuckle_zs):
        body.visual(
            Cylinder(radius=KNUCKLE_R, length=KNUCKLE_L),
            origin=Origin(xyz=(r.hinge_x, r.hinge_y, zk)),
            material=m["brushed"],
            name=f"body_knuckle_{i}", material_class_id="metal.brushed_silver",
        )
        body.visual(
            Box((0.025, 0.025, 0.05)),
            origin=Origin(xyz=(r.hinge_x - 0.0075, r.hinge_y, zk)),
            material=m["body"],
            name=f"body_knuckle_strap_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"charcoal_steel", "sand_vault", "navy_vault", "brushed_inox"} else "metal.blackened_gunmetal"),
        )

    # ----- base stance (Slot D), inline body visuals (no FIXED parts) -----
    _build_base(body, r, m)

    return body


def _build_interior(
    body,
    r: ResolvedFreestandingSecuritySafeConfig,
    m: dict[str, str],
):
    lift = r.base_lift
    ingot = _ingot_mesh()

    if r.interior_layout == "single_shelf":
        shelf_z = r.body_z / 2.0 + lift
        # Shelf embeds ~3 mm into BOTH side walls (Y) so it welds to the body
        # (no disconnected island). Its front edge stays well behind the door
        # opening so it never collides with the bolt carriage. The back edge
        # embeds into the back wall too.
        shelf_w = (r.body_y - 2.0 * WALL) + 0.006
        back_inner_x = -(r.body_x / 2.0) + WALL
        shelf_front_x = r.body_x / 2.0 - r.door_thick - 0.045
        shelf_d = (shelf_front_x - back_inner_x) + 0.006  # +6 mm embeds back wall
        shelf_cx = back_inner_x - 0.003 + shelf_d / 2.0
        body.visual(
            Box((shelf_d, shelf_w, 0.022)),
            origin=Origin(xyz=(shelf_cx, 0.0, shelf_z)),
            material=m["interior"],
            name="shelf", material_class_id=("metal.paint_coated" if r.palette_style in {"charcoal_steel", "gunmetal", "sand_vault", "navy_vault"} else "metal.stainless_matte"),
        )
        shelf_top = shelf_z + 0.011
        floor_positions = [
            (-0.14, -0.08, lift + 0.044),
            (-0.14, 0.08, lift + 0.044),
            (-0.07, -0.08, lift + 0.044),
            (-0.07, 0.08, lift + 0.044),
            (-0.105, 0.0, lift + 0.077),
        ]
        # Shelf ingots oriented along depth (0.14 length in X) so they stay
        # clear of the side walls; bottom embeds ~1 mm into the shelf top.
        shelf_positions = [
            (-0.11, -0.05, shelf_top - 0.001),
            (-0.11, 0.05, shelf_top - 0.001),
            (-0.05, 0.0, shelf_top - 0.001),
        ]
        for i, xyz in enumerate(floor_positions):
            body.visual(ingot, origin=Origin(xyz=xyz), material=m["gold"], name=f"gold_ingot_{i}", material_class_id="metal.precious_gold")
        for j, xyz in enumerate(shelf_positions):
            body.visual(
                ingot,
                origin=Origin(xyz=xyz, rpy=(0.0, 0.0, pi / 2.0)),
                material=m["gold"],
                name=f"gold_ingot_{len(floor_positions) + j}", material_class_id="metal.precious_gold",
            )

    elif r.interior_layout == "no_shelf":
        floor_positions = [
            (-0.14, -0.08, lift + 0.044),
            (-0.14, 0.08, lift + 0.044),
            (-0.07, -0.08, lift + 0.044),
            (-0.07, 0.08, lift + 0.044),
            (-0.105, 0.0, lift + 0.077),
        ]
        for i, xyz in enumerate(floor_positions):
            body.visual(ingot, origin=Origin(xyz=xyz), material=m["gold"], name=f"gold_ingot_{i}", material_class_id="metal.precious_gold")

    elif r.interior_layout == "pull_out_drawer":
        # Runner ledges welded to both side walls at mid height plus a central
        # rear support shelf the drawer rides on. These are body visuals (the
        # runner is a fixed track) and the central shelf anchors drawer_slide.
        td, _tw, origin_x = _drawer_dims(r)
        runner_y = r.body_y / 2.0 - WALL - 0.008
        runner_z = r.body_z / 2.0 + lift
        runner_size = (td, 0.016, 0.020)
        for i, y_sign in enumerate((1.0, -1.0)):
            body.visual(
                Box(runner_size),
                origin=Origin(xyz=(origin_x, y_sign * runner_y, runner_z)),
                material=m["interior"],
                name=f"runner_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"charcoal_steel", "gunmetal", "sand_vault", "navy_vault"} else "metal.stainless_matte"),
            )
        # Central support shelf under the drawer, embedding ~3 mm into BOTH
        # side walls (Y) so it welds to the body (no disconnected island),
        # while its top is raised into the tray base plate so they touch at
        # 1e-6 and the drawer_slide origin sits on real central body geometry.
        shelf_top = runner_z - 0.003
        support_w = (r.body_y - 2.0 * WALL) + 0.006
        body.visual(
            Box((td * 0.7, support_w, 0.012)),
            origin=Origin(xyz=(origin_x, 0.0, shelf_top - 0.006)),
            material=m["interior"],
            name="drawer_support_shelf", material_class_id=("metal.paint_coated" if r.palette_style in {"charcoal_steel", "gunmetal", "sand_vault", "navy_vault"} else "metal.stainless_matte"),
        )
        # Floor ingots below the drawer.
        floor_positions = [
            (-0.14, -0.08, lift + 0.044),
            (-0.14, 0.08, lift + 0.044),
            (-0.07, 0.0, lift + 0.044),
        ]
        for i, xyz in enumerate(floor_positions):
            body.visual(ingot, origin=Origin(xyz=xyz), material=m["gold"], name=f"gold_ingot_{i}", material_class_id="metal.precious_gold")


def _build_base(
    body,
    r: ResolvedFreestandingSecuritySafeConfig,
    m: dict[str, str],
):
    if r.base_stance == "leveling_feet":
        foot_mesh = _leveling_foot_mesh()
        foot_inset = r.body_x / 2.0 - WALL / 2.0 - FOOT_R
        foot_inset_y = r.body_y / 2.0 - WALL / 2.0 - FOOT_R
        # Feet fill [0, FOOT_H]; the body bottom wall is lifted to z=FOOT_H.
        corners = [
            (-foot_inset, -foot_inset_y),
            (-foot_inset, foot_inset_y),
            (foot_inset, -foot_inset_y),
            (foot_inset, foot_inset_y),
        ]
        for i, (fx, fy) in enumerate(corners):
            body.visual(
                foot_mesh,
                origin=Origin(xyz=(fx, fy, 0.0)),
                material=m["brushed"],
                name=f"leveling_foot_{i}", material_class_id="metal.brushed_silver",
            )

    elif r.base_stance == "plinth_base":
        plinth_outer_half_x = r.body_x / 2.0 - PLINTH_INSET
        plinth_outer_half_y = r.body_y / 2.0 - PLINTH_INSET
        plinth_inner_half_x = plinth_outer_half_x - PLINTH_WALL
        body.visual(
            Box((2.0 * plinth_outer_half_x, 2.0 * plinth_outer_half_y, 0.006)),
            origin=Origin(xyz=(0.0, 0.0, 0.003)),
            material=m["brushed"],
            name="plinth_base", material_class_id="metal.brushed_silver",
        )
        panels = [
            (
                (PLINTH_WALL, 2.0 * plinth_outer_half_y, PLINTH_H),
                (plinth_outer_half_x - PLINTH_WALL / 2.0, 0.0, PLINTH_H / 2.0),
            ),
            (
                (PLINTH_WALL, 2.0 * plinth_outer_half_y, PLINTH_H),
                (-plinth_outer_half_x + PLINTH_WALL / 2.0, 0.0, PLINTH_H / 2.0),
            ),
            (
                (2.0 * plinth_inner_half_x, PLINTH_WALL, PLINTH_H),
                (0.0, plinth_outer_half_y - PLINTH_WALL / 2.0, PLINTH_H / 2.0),
            ),
            (
                (2.0 * plinth_inner_half_x, PLINTH_WALL, PLINTH_H),
                (0.0, -plinth_outer_half_y + PLINTH_WALL / 2.0, PLINTH_H / 2.0),
            ),
        ]
        for i, (size, xyz) in enumerate(panels):
            body.visual(
                Box(size), origin=Origin(xyz=xyz), material=m["body"], name=f"plinth_panel_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"charcoal_steel", "sand_vault", "navy_vault", "brushed_inox"} else "metal.blackened_gunmetal")
            )


# ---------------------------------------------------------------------------
# Door (slab + knuckles + bosses; lock-entry mounting surface inlined)
# ---------------------------------------------------------------------------
def _build_door(
    model: ArticulatedObject,
    r: ResolvedFreestandingSecuritySafeConfig,
    m: dict[str, str],
):
    door = model.part("door")
    door.visual(
        Box((r.door_thick, r.door_w, r.door_h)),
        origin=Origin(xyz=(r.door_x_out - r.door_thick / 2.0, r.door_cy, 0.0)),
        material=m["door"],
        name="door_slab", material_class_id=("metal.paint_coated" if r.palette_style in {"charcoal_steel", "sand_vault", "navy_vault", "brushed_inox"} else "metal.blackened_gunmetal"),
    )
    door.visual(
        Box((0.012, r.door_w * 0.86, r.door_h * 0.87)),
        origin=Origin(xyz=(r.door_x_in - 0.005, r.door_cy, 0.0)),
        material=m["door"],
        name="door_inner_panel", material_class_id=("metal.paint_coated" if r.palette_style in {"charcoal_steel", "sand_vault", "navy_vault", "brushed_inox"} else "metal.blackened_gunmetal"),
    )
    for i, zk in enumerate(r.door_knuckle_zs):
        door.visual(
            Cylinder(radius=KNUCKLE_R, length=KNUCKLE_L),
            origin=Origin(xyz=(0.0, 0.0, zk)),
            material=m["brushed"],
            name=f"hinge_knuckle_{i}", material_class_id="metal.brushed_silver",
        )
        door.visual(
            Box((0.024, 0.040, 0.05)),
            origin=Origin(xyz=(0.002, -0.015, zk)),
            material=m["door"],
            name=f"hinge_strap_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"charcoal_steel", "sand_vault", "navy_vault", "brushed_inox"} else "metal.blackened_gunmetal"),
        )

    # Handle boss (always present, hosts handle_spin).
    door.visual(
        Cylinder(radius=0.040, length=0.016),
        origin=Origin(xyz=(r.door_x_out + 0.006, r.face_cy, r.handle_z), rpy=(0.0, pi / 2.0, 0.0)),
        material=m["door"],
        name="handle_boss", material_class_id=("metal.paint_coated" if r.palette_style in {"charcoal_steel", "sand_vault", "navy_vault", "brushed_inox"} else "metal.blackened_gunmetal"),
    )

    # Lock-entry mounting surface(s) on the door face.
    if r.lock_entry == "rotary_dial":
        door.visual(
            Cylinder(radius=0.052, length=0.016),
            origin=Origin(
                xyz=(r.door_x_out + 0.006, r.face_cy, r.dial_z), rpy=(0.0, pi / 2.0, 0.0)
            ),
            material=m["door"],
            name="dial_boss", material_class_id=("metal.paint_coated" if r.palette_style in {"charcoal_steel", "sand_vault", "navy_vault", "brushed_inox"} else "metal.blackened_gunmetal"),
        )
        door.visual(
            Box((0.003, 0.005, 0.009)),
            origin=Origin(xyz=(r.door_x_out + 0.001, r.face_cy, r.dial_z + 0.055)),
            material=m["black"],
            name="dial_index_mark", appearance_only=AppearanceOnlySpec(kind="overlay"),
        )
    elif r.lock_entry == "dual_rotary_dial":
        for i, (dy, dz) in enumerate(_dual_dial_positions(r)):
            door.visual(
                Cylinder(radius=0.052, length=0.016),
                origin=Origin(xyz=(r.door_x_out + 0.006, dy, dz), rpy=(0.0, pi / 2.0, 0.0)),
                material=m["door"],
                name=f"dial_boss_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"charcoal_steel", "sand_vault", "navy_vault", "brushed_inox"} else "metal.blackened_gunmetal"),
            )
    elif r.lock_entry == "electronic_keypad":
        _build_keypad_face(door, r, m)

    return door


def _dual_dial_positions(
    r: ResolvedFreestandingSecuritySafeConfig,
) -> tuple[tuple[float, float], tuple[float, float]]:
    """(y, z) mounts for the two combination dials, side by side and raised.

    The dials sit HORIZONTALLY next to each other high on the door face rather
    than stacked vertically. The turn handle mounts below them at the door
    centerline (y == face_cy) and sweeps in the vertical plane; a laterally
    stacked pair keeps that swept arc (t-bar / lever reaching straight up) from
    ever passing through a dial, which a vertically stacked lower dial could not
    avoid on shorter doors. The ~0.072 m lateral offset clears the widest handle
    sweep while both dials stay within the door leaf width.
    """
    z = r.dial_z + 0.030
    dy = 0.072
    return ((r.face_cy - dy, z), (r.face_cy + dy, z))


# ---- Keypad layout (hinge-local), driven off the door face ----
def _keypad_layout(r: ResolvedFreestandingSecuritySafeConfig):
    keypad_z = r.dial_z
    housing_thick = 0.014
    housing_w = 0.100
    housing_h = 0.140
    embed = 0.002
    housing_cx = r.door_x_out + housing_thick / 2.0 - embed
    keypad_x_out = housing_cx + housing_thick / 2.0
    return keypad_z, housing_thick, housing_w, housing_h, housing_cx, keypad_x_out


KEYPAD_BTN_SIZE = 0.020
KEYPAD_BTN_THICK = 0.006
KEYPAD_BTN_STROKE = 0.003
KEYPAD_COLS = 3
KEYPAD_ROWS = 4
KEYPAD_SPACING_Y = 0.028
KEYPAD_SPACING_Z = 0.028


def _build_keypad_face(
    door,
    r: ResolvedFreestandingSecuritySafeConfig,
    m: dict[str, str],
):
    keypad_z, h_thick, h_w, h_h, h_cx, x_out = _keypad_layout(r)
    door.visual(
        Box((h_thick, h_w, h_h)),
        origin=Origin(xyz=(h_cx, r.face_cy, keypad_z)),
        material=m["door"],
        name="keypad_housing", material_class_id=("metal.paint_coated" if r.palette_style in {"charcoal_steel", "sand_vault", "navy_vault", "brushed_inox"} else "metal.blackened_gunmetal"),
    )
    display_cx = x_out - 0.003 / 2.0 - 0.001
    display_z = keypad_z + h_h / 2.0 - 0.009
    door.visual(
        Box((0.003, 0.080, 0.014)),
        origin=Origin(xyz=(display_cx, r.face_cy, display_z)),
        material=m["black"],
        name="keypad_display", material_class_id="tech.emissive_surface",
    )


# ---------------------------------------------------------------------------
# Bolt carriage
# ---------------------------------------------------------------------------
def _build_carriage(
    model: ArticulatedObject,
    r: ResolvedFreestandingSecuritySafeConfig,
    m: dict[str, str],
):
    carriage = model.part("bolt_carriage")
    bar_h = (r.bolt_zs[-1] - r.bolt_zs[0]) + 0.06 if len(r.bolt_zs) > 1 else 0.10
    carriage.visual(
        Box((0.018, 0.05, bar_h)),
        origin=Origin(xyz=(0.0, 0.035, 0.0)),
        material=m["brushed"],
        name="carriage_bar", material_class_id="metal.brushed_silver",
    )
    for i, zr in enumerate(r.bolt_zs):
        carriage.visual(
            Cylinder(radius=BOLT_R, length=BOLT_LEN),
            origin=Origin(xyz=(0.0, -0.001, zr), rpy=(pi / 2.0, 0.0, 0.0)),
            material=m["brushed"],
            name=f"lock_bolt_{i}", material_class_id="metal.brushed_silver",
        )
    return carriage


# ---------------------------------------------------------------------------
# Lock entry (Slot B) child parts
# ---------------------------------------------------------------------------
def _build_dial(
    model: ArticulatedObject,
    r: ResolvedFreestandingSecuritySafeConfig,
    m: dict[str, str],
    part_name: str,
    knob_name: str,
):
    dial = model.part(part_name)
    dial.visual(
        Cylinder(radius=0.047, length=0.007),
        origin=Origin(xyz=(0.0, 0.0, 0.0035)),
        material=m["silver"],
        name="dial_ring", material_class_id="metal.chrome_polished",
    )
    dial.visual(
        _dial_knob_mesh(knob_name),
        origin=Origin(xyz=(0.0, 0.0, 0.0065)),
        material=m["black"],
        name="dial_knob", material_class_id="plastic.opaque_glossy_molded",
    )
    for i in range(12):
        theta = i * pi / 6.0
        dial.visual(
            Box((0.009, 0.0022, 0.0024)),
            origin=Origin(
                xyz=(0.040 * cos(theta), 0.040 * sin(theta), 0.007), rpy=(0.0, 0.0, theta)
            ),
            material=m["black"],
            name=f"dial_tick_{i}", appearance_only=AppearanceOnlySpec(kind="overlay"),
        )
    return dial


def _build_keypad_button(
    model: ArticulatedObject,
    m: dict[str, str],
    idx: int,
):
    btn = model.part(f"keypad_button_{idx}")
    btn.visual(
        Box((KEYPAD_BTN_SIZE, KEYPAD_BTN_SIZE, KEYPAD_BTN_THICK)),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material=m["black"],
        name=f"button_face_{idx}", material_class_id="plastic.opaque_glossy_molded",
    )
    return btn


# ---------------------------------------------------------------------------
# Turn handle (Slot A) child parts
# ---------------------------------------------------------------------------
def _build_handle(
    model: ArticulatedObject,
    r: ResolvedFreestandingSecuritySafeConfig,
    m: dict[str, str],
):
    if r.turn_handle == "four_spoke_wheel":
        handle = model.part("handle_wheel")
        handle.visual(
            Cylinder(radius=0.020, length=0.034),
            origin=Origin(xyz=(0.0, 0.0, 0.017)),
            material=m["polished"],
            name="handle_hub", material_class_id="metal.chrome_polished",
        )
        handle.visual(
            Sphere(radius=0.019),
            origin=Origin(xyz=(0.0, 0.0, 0.032)),
            material=m["polished"],
            name="hub_cap", material_class_id="metal.chrome_polished",
        )
        for i in range(4):
            theta = pi / 4.0 + i * pi / 2.0
            handle.visual(
                Cylinder(radius=0.0085, length=0.125),
                origin=Origin(
                    xyz=(0.0625 * cos(theta), 0.0625 * sin(theta), 0.020),
                    rpy=(0.0, pi / 2.0, theta),
                ),
                material=m["polished"],
                name=f"spoke_{i}", material_class_id="metal.chrome_polished",
            )
            handle.visual(
                Sphere(radius=0.012),
                origin=Origin(xyz=(0.125 * cos(theta), 0.125 * sin(theta), 0.020)),
                material=m["polished"],
                name=f"spoke_knob_{i}", material_class_id="metal.chrome_polished",
            )
        return handle

    if r.turn_handle == "tbar_handle":
        handle = model.part("tbar_handle")
        handle.visual(
            Cylinder(radius=0.018, length=0.030),
            origin=Origin(xyz=(0.0, 0.0, 0.015)),
            material=m["polished"],
            name="handle_hub", material_class_id="metal.chrome_polished",
        )
        handle.visual(
            Cylinder(radius=0.009, length=0.18),
            origin=Origin(xyz=(0.0, 0.0, 0.022), rpy=(pi / 2.0, 0.0, 0.0)),
            material=m["polished"],
            name="cross_bar", material_class_id="metal.chrome_polished",
        )
        for i, y_sign in enumerate((-1.0, 1.0)):
            handle.visual(
                Sphere(radius=0.013),
                origin=Origin(xyz=(0.0, y_sign * 0.09, 0.022)),
                material=m["polished"],
                name=f"knob_end_{i}", material_class_id="metal.chrome_polished",
            )
        return handle

    # lever_handle
    handle = model.part("handle_lever")
    handle.visual(
        Cylinder(radius=0.018, length=0.028),
        origin=Origin(xyz=(0.0, 0.0, 0.014)),
        material=m["polished"],
        name="handle_hub", material_class_id="metal.chrome_polished",
    )
    # Shorter lever arm so its straight-up reach at handle_spin=pi/2 stays clear
    # of the combination dial mounted above the handle on the door face.
    handle.visual(
        Cylinder(radius=0.009, length=0.105),
        origin=Origin(xyz=(0.0, 0.0525, 0.020), rpy=(pi / 2.0, 0.0, 0.0)),
        material=m["polished"],
        name="lever_arm", material_class_id="metal.chrome_polished",
    )
    handle.visual(
        Sphere(radius=0.013),
        origin=Origin(xyz=(0.0, 0.105, 0.020)),
        material=m["polished"],
        name="lever_grip", material_class_id="metal.chrome_polished",
    )
    return handle


# ---------------------------------------------------------------------------
# Interior child part (drawer)
# ---------------------------------------------------------------------------
def _build_drawer(
    model: ArticulatedObject,
    r: ResolvedFreestandingSecuritySafeConfig,
    m: dict[str, str],
):
    drawer = model.part("cash_drawer")
    drawer.visual(
        _drawer_tray_mesh(r),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material=m["interior"],
        name="drawer_tray", material_class_id=("metal.paint_coated" if r.palette_style in {"charcoal_steel", "gunmetal", "sand_vault", "navy_vault"} else "metal.stainless_matte"),
    )
    ingot = _ingot_mesh()
    # Ingots oriented along the drawer WIDTH (unrotated, 0.14 m length runs in
    # Y), so they stay short (0.055 m) in the depth (X) direction and fit inside
    # the shallow set-back tray at any sampled scale without poking out its
    # back into the safe back wall. Lined up front-to-back near the tray center.
    td, _tw, _ox = _drawer_dims(r)
    # Ingot base at z=0.004 embeds into the tray base plate (top at z=0.006) so
    # the contents weld to the tray (no disconnected island inside the part).
    positions = [
        (-td * 0.20, -0.030, 0.004),
        (-td * 0.20, 0.030, 0.004),
        (td * 0.12, 0.0, 0.004),
    ]
    for i, xyz in enumerate(positions):
        drawer.visual(
            ingot,
            origin=Origin(xyz=xyz),
            material=m["gold"],
            name=f"drawer_ingot_{i}", material_class_id="metal.precious_gold",
        )
    return drawer


# ---------------------------------------------------------------------------
# Material registration
# ---------------------------------------------------------------------------
def _register_materials(model: ArticulatedObject, style: PaletteStyle) -> dict[str, str]:
    palette = PALETTES[style]
    return {name: model.material(f"{style}_{name}", rgba=rgba) for name, rgba in palette.items()}


# ---------------------------------------------------------------------------
# Top-level builder
# ---------------------------------------------------------------------------
def build_freestanding_security_safe(
    config: FreestandingSecuritySafeConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    _ = assets
    config = config or FreestandingSecuritySafeConfig()
    r = resolve_config(config)
    model = ArticulatedObject(r.name)
    m = _register_materials(model, r.palette_style)

    body = _build_body(model, r, m)
    door = _build_door(model, r, m)
    carriage = _build_carriage(model, r, m)
    handle = _build_handle(model, r, m)

    # ----- door hinge (REVOLUTE, vertical, on right knuckle stack) -----
    model.articulation(
        "door_hinge",
        ArticulationType.REVOLUTE,
        parent=body,
        child=door,
        origin=Origin(xyz=(r.hinge_x, r.hinge_y, r.hinge_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=90.0, velocity=1.2, lower=0.0, upper=2.094),
    )

    # ----- handle spin (REVOLUTE, door-normal, on handle_boss) -----
    if r.turn_handle == "lever_handle":
        handle_limits = MotionLimits(effort=40.0, velocity=2.0, lower=0.0, upper=pi / 2.0)
    else:
        handle_limits = MotionLimits(effort=40.0, velocity=2.0, lower=-pi / 2.0, upper=pi / 2.0)
    model.articulation(
        "handle_spin",
        ArticulationType.REVOLUTE,
        parent=door,
        child=handle,
        origin=Origin(xyz=(r.door_x_out + 0.014, r.face_cy, r.handle_z), rpy=(0.0, pi / 2.0, 0.0)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=handle_limits,
    )

    # ----- lock entry (Slot B) -----
    if r.lock_entry == "rotary_dial":
        dial = _build_dial(model, r, m, "combination_dial", "dial_knob")
        model.articulation(
            "dial_spin",
            ArticulationType.CONTINUOUS,
            parent=door,
            child=dial,
            origin=Origin(
                xyz=(r.door_x_out + 0.014, r.face_cy, r.dial_z), rpy=(0.0, pi / 2.0, 0.0)
            ),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=2.0, velocity=6.0),
        )
    elif r.lock_entry == "dual_rotary_dial":
        for i, (dy, dz) in enumerate(_dual_dial_positions(r)):
            dial = _build_dial(model, r, m, f"combination_dial_{i}", f"dial_knob_{i}")
            model.articulation(
                f"dial_spin_{i}",
                ArticulationType.CONTINUOUS,
                parent=door,
                child=dial,
                origin=Origin(xyz=(r.door_x_out + 0.014, dy, dz), rpy=(0.0, pi / 2.0, 0.0)),
                axis=(0.0, 0.0, 1.0),
                motion_limits=MotionLimits(effort=2.0, velocity=6.0),
            )
    elif r.lock_entry == "electronic_keypad":
        _keypad_z, _ht, _hw, _hh, _hcx, x_out = _keypad_layout(r)
        btn_rest_x = x_out + KEYPAD_BTN_THICK / 2.0
        z_base = r.dial_z - 0.042
        for idx in range(12):
            col = idx % KEYPAD_COLS
            row = idx // KEYPAD_COLS
            by = r.face_cy + (col - 1) * KEYPAD_SPACING_Y
            bz = z_base + row * KEYPAD_SPACING_Z
            btn = _build_keypad_button(model, m, idx)
            model.articulation(
                f"button_press_{idx}",
                ArticulationType.PRISMATIC,
                parent=door,
                child=btn,
                origin=Origin(xyz=(btn_rest_x, by, bz), rpy=(0.0, -pi / 2.0, 0.0)),
                axis=(0.0, 0.0, 1.0),
                motion_limits=MotionLimits(
                    effort=5.0, velocity=0.5, lower=0.0, upper=KEYPAD_BTN_STROKE
                ),
            )

    # ----- bolt carriage (PRISMATIC, latch edge) -----
    model.articulation(
        "bolt_slide",
        ArticulationType.PRISMATIC,
        parent=door,
        child=carriage,
        origin=Origin(xyz=(r.door_x_out - r.door_thick / 2.0, r.carriage_origin_y, 0.0)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(
            effort=60.0, velocity=0.2, lower=-BOLT_STROKE / 2.0, upper=BOLT_STROKE / 2.0
        ),
    )

    # ----- interior drawer (Slot C, optional) -----
    if r.interior_layout == "pull_out_drawer":
        drawer = _build_drawer(model, r, m)
        # Origin sits on the central support shelf (top at runner_z - 0.010),
        # near central body geometry so the joint anchors cleanly.
        _td, _tw, origin_x = _drawer_dims(r)
        runner_z = r.body_z / 2.0 + r.base_lift
        model.articulation(
            "drawer_slide",
            ArticulationType.PRISMATIC,
            parent=body,
            child=drawer,
            origin=Origin(xyz=(origin_x, 0.0, runner_z - 0.006)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=40.0, velocity=0.15, lower=0.0, upper=0.25),
        )
        # Derive the safe forward travel with the clearance solver at the
        # worst-case (default all-zero == door-closed, bolts extended) base
        # pose: the extended tray must not sweep into the door slab / inner
        # panel, the bolt carriage, or the door-face controls. The drawer
        # legitimately rides on the body runners + support shelf (element-
        # scoped-allowed in the tests), and the body never blocks the forward
        # (+X, out-the-front-opening) path, so the whole cash_drawer<->safe_body
        # pair is allowed for the solve; the real clamp comes from the door
        # subtree.
        solved_upper = max_joint_value(
            model,
            joint="drawer_slide",
            limit=0.25,
            margin=0.008,
            allowed_pairs=[("cash_drawer", "safe_body")],
        )
        drawer_joint = model.get_articulation("drawer_slide")
        drawer_joint.motion_limits = MotionLimits(
            effort=40.0, velocity=0.15, lower=0.0, upper=solved_upper
        )

    return model


def build_seeded_freestanding_security_safe(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_freestanding_security_safe(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Element-scoped expected overlaps
# ---------------------------------------------------------------------------
def _try_allow(ctx: TestContext, a, b, elem_a, elem_b, reason):
    try:
        ctx.allow_overlap(a, b, elem_a=elem_a, elem_b=elem_b, reason=reason)
    except Exception:
        pass


def _allow_expected_overlaps(ctx: TestContext, model: ArticulatedObject) -> None:
    names = {p.name for p in model.parts}
    bolt_names = [f"lock_bolt_{i}" for i in range(8)]

    body = model.get_part("safe_body") if "safe_body" in names else None
    door = model.get_part("door") if "door" in names else None

    # --- bolt carriage rides inside the door slab; bolts engage the strike
    #     pockets in the latch wall (intentional seated penetration). ---
    if "bolt_carriage" in names and door is not None:
        carriage = model.get_part("bolt_carriage")
        _try_allow(
            ctx,
            carriage,
            door,
            "carriage_bar",
            "door_slab",
            "Bolt carriage bar intentionally slides inside the solid door slab proxy.",
        )
        for bn in bolt_names:
            _try_allow(
                ctx,
                carriage,
                door,
                bn,
                "door_slab",
                "Locking bolt intentionally passes through the solid door slab proxy.",
            )
            if body is not None:
                _try_allow(
                    ctx,
                    carriage,
                    body,
                    bn,
                    "side_wall_latch",
                    "Locking bolt seats into the bored strike pocket in the latch wall.",
                )

    # --- door hinge knuckles interleave with body knuckles and ride at the
    #     hinge-side wall (hinge mechanism overlaps, rest + open pose). ---
    if door is not None and body is not None:
        for dk in ("hinge_knuckle_0", "hinge_knuckle_1", "hinge_knuckle_2"):
            for bk in ("side_wall_hinge", "body_knuckle_0", "body_knuckle_1"):
                _try_allow(
                    ctx,
                    door,
                    body,
                    dk,
                    bk,
                    "Door hinge knuckle interleaves with body knuckles / hinge wall.",
                )
        for ds in ("hinge_strap_0", "hinge_strap_1", "hinge_strap_2"):
            for bk in ("side_wall_hinge", "body_knuckle_0", "body_knuckle_1"):
                _try_allow(
                    ctx,
                    door,
                    body,
                    ds,
                    bk,
                    "Door hinge strap wraps the hinge-side wall and body knuckles.",
                )

    # --- lock-entry controls seat coaxially on their door bosses. ---
    dial_elems = ("dial_ring", "dial_knob") + tuple(f"dial_tick_{i}" for i in range(12))
    for dial_name, boss in (
        ("combination_dial", "dial_boss"),
        ("combination_dial_0", "dial_boss_0"),
        ("combination_dial_1", "dial_boss_1"),
    ):
        if dial_name in names and door is not None:
            dial = model.get_part(dial_name)
            for elem_a in dial_elems:
                for elem_b in (boss, "door_slab"):
                    _try_allow(
                        ctx,
                        dial,
                        door,
                        elem_a,
                        elem_b,
                        "Combination dial seats coaxially on its raised door boss.",
                    )

    # --- turn handle hub seats on the handle boss. ---
    handle_elems = (
        (
            "handle_hub",
            "hub_cap",
            "cross_bar",
            "lever_arm",
            "lever_grip",
        )
        + tuple(f"spoke_{i}" for i in range(4))
        + tuple(f"spoke_knob_{i}" for i in range(4))
        + ("knob_end_0", "knob_end_1")
    )
    for handle_name in ("handle_wheel", "tbar_handle", "handle_lever"):
        if handle_name in names and door is not None:
            handle = model.get_part(handle_name)
            for elem_a in handle_elems:
                for elem_b in ("handle_boss", "door_slab"):
                    _try_allow(
                        ctx,
                        handle,
                        door,
                        elem_a,
                        elem_b,
                        "Turn handle hub seats on its raised door boss.",
                    )

    # --- keypad buttons embed in the keypad housing / door slab. ---
    if door is not None:
        for idx in range(12):
            bname = f"keypad_button_{idx}"
            if bname in names:
                btn = model.get_part(bname)
                for elem_b in ("keypad_housing", "door_slab"):
                    _try_allow(
                        ctx,
                        btn,
                        door,
                        f"button_face_{idx}",
                        elem_b,
                        "Keypad button embeds in the keypad housing / door slab proxy.",
                    )

    # --- cash drawer rides on the body runner ledges. ---
    if "cash_drawer" in names and body is not None:
        drawer = model.get_part("cash_drawer")
        drawer_elems = ("drawer_tray",) + tuple(f"drawer_ingot_{i}" for i in range(3))
        for elem_a in drawer_elems:
            for elem_b in ("runner_0", "runner_1", "drawer_support_shelf", "shelf", "bottom_wall"):
                _try_allow(
                    ctx,
                    drawer,
                    body,
                    elem_a,
                    elem_b,
                    "Cash drawer tray/contents ride on the body runner ledges and support shelf.",
                )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def run_freestanding_security_safe_tests(
    object_model: ArticulatedObject,
    config: FreestandingSecuritySafeConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    _allow_expected_overlaps(ctx, object_model)

    part_names = {p.name for p in object_model.parts}
    if "cash_drawer" in part_names:
        ctx.allow_isolated_part(
            object_model.get_part("cash_drawer"),
            reason="cash drawer slides out of the safe and loses body contact",
        )

    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.02)

    part_names = {p.name for p in object_model.parts}
    joint_names = {j.name for j in object_model.joints}

    body = object_model.get_part("safe_body")
    door = object_model.get_part("door")
    carriage = object_model.get_part("bolt_carriage")

    # ----- identity parts / joints -----
    for required in ("safe_body", "door", "bolt_carriage"):
        if required not in part_names:
            ctx.fail("identity_parts", f"missing {required}")
    for required in ("door_hinge", "handle_spin", "bolt_slide"):
        if required not in joint_names:
            ctx.fail("identity_joints", f"missing {required}")

    # ----- door swings outward about the right vertical hinge -----
    hinge = object_model.get_articulation("door_hinge")
    slab_rest = ctx.part_element_world_aabb(door, elem="door_slab")
    with ctx.pose({hinge: 1.22}):
        ctx.fail_if_parts_overlap_in_current_pose(name="door_open_no_box_penetration")
        slab_open = ctx.part_element_world_aabb(door, elem="door_slab")
        ctx.check(
            "door swings outward about the right-side vertical hinge",
            slab_rest is not None
            and slab_open is not None
            and (slab_open[0][0] + slab_open[1][0]) / 2.0
            > (slab_rest[0][0] + slab_rest[1][0]) / 2.0 + 0.12
            and (slab_open[0][1] + slab_open[1][1]) / 2.0
            > (slab_rest[0][1] + slab_rest[1][1]) / 2.0 + 0.04,
            details=f"slab rest={slab_rest}, open={slab_open}",
        )

    # ----- closed door leaves a latch-side jamb gap; door within envelope -----
    ctx.expect_gap(
        door,
        body,
        axis="y",
        positive_elem="door_slab",
        negative_elem="side_wall_latch",
        min_gap=0.002,
        max_gap=0.03,
        name="closed door leaves a latch-side jamb gap",
    )

    # ----- hinge knuckle stack contact -----
    ctx.expect_contact(
        door,
        body,
        elem_a="hinge_knuckle_0",
        elem_b="body_knuckle_0",
        contact_tol=1e-3,
        name="door knuckle stacks against body knuckle",
    )

    # ----- envelope roughly right (~body_x x body_y x (body_z+base_lift)) -----
    aabb = ctx.part_world_aabb(body)
    wall_aabb = ctx.part_element_world_aabb(body, elem="side_wall_hinge")
    ctx.check(
        "safe body envelope matches the resolved scale",
        aabb is not None
        and wall_aabb is not None
        and abs((wall_aabb[1][0] - wall_aabb[0][0]) - r.body_x) < 0.02
        and abs((aabb[1][1] - aabb[0][1]) - r.body_y) < 0.02
        and abs((aabb[1][2] - aabb[0][2]) - (r.body_z + r.base_lift)) < 0.02,
        details=f"body aabb={aabb}, hinge wall aabb={wall_aabb}, base_lift={r.base_lift}",
    )

    # ----- base sits on the floor (nothing sinks) -----
    if aabb is not None:
        ctx.check(
            "assembly rests on the floor (z>=~0)",
            aabb[0][2] > -0.005,
            details=f"min z={aabb[0][2]:.4f}",
        )
    if r.base_stance == "leveling_feet":
        foot_aabb = ctx.part_element_world_aabb(body, elem="leveling_foot_0")
        ctx.check(
            "leveling foot lifts the body off the floor",
            foot_aabb is not None and foot_aabb[0][2] < 0.006,
            details=f"foot0 aabb={foot_aabb}",
        )
    elif r.base_stance == "plinth_base":
        plinth_aabb = ctx.part_element_world_aabb(body, elem="plinth_base")
        ctx.check(
            "plinth base sits on the floor",
            plinth_aabb is not None and plinth_aabb[0][2] < 0.008,
            details=f"plinth base aabb={plinth_aabb}",
        )

    # ----- bolts protrude at rest, retract when carriage slides -----
    bolt_slide = object_model.get_articulation("bolt_slide")
    mid_idx = r.bolt_count // 2
    bolt_rest = ctx.part_element_world_aabb(carriage, elem=f"lock_bolt_{mid_idx}")
    latch_aabb = ctx.part_element_world_aabb(body, elem="side_wall_latch")
    ctx.check(
        "rest pose: bolts protrude toward the latch wall strike pockets",
        bolt_rest is not None
        and latch_aabb is not None
        and bolt_rest[0][1] < latch_aabb[1][1] + 0.002,
        details=f"mid bolt aabb={bolt_rest}, latch aabb={latch_aabb}",
    )
    with ctx.pose({bolt_slide: -0.016}):
        bolt_open = ctx.part_element_world_aabb(carriage, elem=f"lock_bolt_{mid_idx}")
        ctx.check(
            "retracted carriage pulls the bolts back toward the door",
            bolt_open is not None
            and bolt_rest is not None
            and bolt_open[0][1] > bolt_rest[0][1] + 0.012,
            details=f"mid bolt retracted aabb={bolt_open}",
        )

    # ----- bolt multiplicity matches bolt_count -----
    bolt_visuals = sum(1 for v in carriage.visuals if v.name.startswith("lock_bolt_"))
    ctx.check(
        "bolt carriage carries bolt_count locking bolts",
        bolt_visuals == r.bolt_count,
        details=f"found {bolt_visuals} bolts, expected {r.bolt_count}",
    )

    # ----- handle turns about door-normal -----
    handle_spin = object_model.get_articulation("handle_spin")
    handle_part = None
    handle_probe_elem = None
    if r.turn_handle == "four_spoke_wheel":
        handle_part = object_model.get_part("handle_wheel")
        handle_probe_elem = "spoke_knob_0"
    elif r.turn_handle == "tbar_handle":
        handle_part = object_model.get_part("tbar_handle")
        handle_probe_elem = "knob_end_0"
    else:
        handle_part = object_model.get_part("handle_lever")
        handle_probe_elem = "lever_grip"
    if handle_part is not None and handle_probe_elem is not None:
        probe_rest = ctx.part_element_world_aabb(handle_part, elem=handle_probe_elem)
        with ctx.pose({handle_spin: pi / 2.0}):
            probe_turned = ctx.part_element_world_aabb(handle_part, elem=handle_probe_elem)
            ctx.check(
                "handle end orbits about the door-normal axis when turned",
                probe_rest is not None
                and probe_turned is not None
                and abs(
                    (probe_turned[0][2] + probe_turned[1][2]) / 2.0
                    - (probe_rest[0][2] + probe_rest[1][2]) / 2.0
                )
                > 0.03,
                details=f"rest={probe_rest}, turned={probe_turned}",
            )

    # ----- lock entry behaviour (guarded by active module) -----
    if r.lock_entry == "rotary_dial":
        dial = object_model.get_part("combination_dial")
        dial_spin = object_model.get_articulation("dial_spin")
        ctx.check(
            "dial_spin is a CONTINUOUS joint",
            dial_spin.articulation_type == ArticulationType.CONTINUOUS,
            details=f"type={dial_spin.articulation_type}",
        )
        tick_rest = ctx.part_element_world_aabb(dial, elem="dial_tick_0")
        with ctx.pose({dial_spin: pi / 2.0}):
            tick_spun = ctx.part_element_world_aabb(dial, elem="dial_tick_0")
            ctx.check(
                "dial tick orbits when the dial spins",
                tick_rest is not None
                and tick_spun is not None
                and abs(
                    (tick_spun[0][2] + tick_spun[1][2]) / 2.0
                    - (tick_rest[0][2] + tick_rest[1][2]) / 2.0
                )
                > 0.02,
                details=f"tick rest={tick_rest}, spun={tick_spun}",
            )
    elif r.lock_entry == "dual_rotary_dial":
        ctx.check(
            "no single dial_spin joint when dual dials are present",
            "dial_spin" not in joint_names,
        )
        for i in range(2):
            dial = object_model.get_part(f"combination_dial_{i}")
            dial_spin = object_model.get_articulation(f"dial_spin_{i}")
            ctx.check(
                f"dial_spin_{i} is a CONTINUOUS joint",
                dial_spin.articulation_type == ArticulationType.CONTINUOUS,
                details=f"type={dial_spin.articulation_type}",
            )
            tick_rest = ctx.part_element_world_aabb(dial, elem="dial_tick_0")
            with ctx.pose({dial_spin: pi / 2.0}):
                tick_spun = ctx.part_element_world_aabb(dial, elem="dial_tick_0")
                ctx.check(
                    f"dial {i} tick orbits when spun",
                    tick_rest is not None
                    and tick_spun is not None
                    and abs(
                        (tick_spun[0][2] + tick_spun[1][2]) / 2.0
                        - (tick_rest[0][2] + tick_rest[1][2]) / 2.0
                    )
                    > 0.02,
                    details=f"tick rest={tick_rest}, spun={tick_spun}",
                )
    elif r.lock_entry == "electronic_keypad":
        ctx.check(
            "keypad variant has no dial_spin joint",
            "dial_spin" not in joint_names,
        )
        btn_count = 0
        for idx in range(12):
            if f"keypad_button_{idx}" in part_names and f"button_press_{idx}" in joint_names:
                j = object_model.get_articulation(f"button_press_{idx}")
                if j.articulation_type == ArticulationType.PRISMATIC:
                    btn_count += 1
        ctx.check(
            "12 keypad buttons exist with prismatic joints",
            btn_count == 12,
            details=f"found {btn_count} prismatic button joints",
        )
        btn0 = object_model.get_part("keypad_button_0")
        btn0_joint = object_model.get_articulation("button_press_0")
        btn0_rest = ctx.part_element_world_aabb(btn0, elem="button_face_0")
        with ctx.pose({btn0_joint: KEYPAD_BTN_STROKE}):
            btn0_pressed = ctx.part_element_world_aabb(btn0, elem="button_face_0")
            ctx.check(
                "button press moves the button inward along the door normal",
                btn0_rest is not None
                and btn0_pressed is not None
                and btn0_pressed[0][0] < btn0_rest[0][0] - 0.001,
                details=f"rest={btn0_rest}, pressed={btn0_pressed}",
            )

    # ----- interior drawer behaviour (guarded) -----
    if r.interior_layout == "pull_out_drawer" and "drawer_slide" in joint_names:
        drawer = object_model.get_part("cash_drawer")
        drawer_slide = object_model.get_articulation("drawer_slide")
        # The upper limit is the solver-derived safe forward travel (the tray
        # cannot pass the closed-door plane). Probe at that realized limit and
        # assert the tray actually translates the full stroke, plus a design
        # guard that the derived travel stays a usable pull-out.
        upper = float(drawer_slide.motion_limits.upper)
        ctx.check(
            "derived drawer travel stays a usable pull-out (>= 0.10 m)",
            upper >= 0.10,
            details=f"solved drawer_slide upper={upper:.4f}",
        )
        rest = ctx.part_element_world_aabb(drawer, elem="drawer_tray")
        with ctx.pose({drawer_slide: upper}):
            pulled = ctx.part_element_world_aabb(drawer, elem="drawer_tray")
            ctx.check(
                "drawer slides outward (+X) to its full derived travel",
                rest is not None
                and pulled is not None
                and (pulled[0][0] + pulled[1][0]) / 2.0
                > (rest[0][0] + rest[1][0]) / 2.0 + upper * 0.9,
                details=f"rest={rest}, pulled={pulled}, upper={upper:.4f}",
            )
    elif r.interior_layout == "single_shelf":
        shelf_aabb = ctx.part_element_world_aabb(body, elem="shelf")
        ctx.check(
            "interior shelf spans the cavity",
            shelf_aabb is not None and (shelf_aabb[1][1] - shelf_aabb[0][1]) > r.body_y * 0.6,
            details=f"shelf aabb={shelf_aabb}",
        )

    return ctx.report()


__all__ = [
    "FreestandingSecuritySafeConfig",
    "ResolvedFreestandingSecuritySafeConfig",
    "build_freestanding_security_safe",
    "build_seeded_freestanding_security_safe",
    "config_from_seed",
    "resolve_config",
    "run_freestanding_security_safe_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
]
