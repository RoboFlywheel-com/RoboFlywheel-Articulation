# SPDX-License-Identifier: Apache-2.0

"""Paper shredder — modular procedural template.

pattern = mixed (parallel_children + multiplicity). A single bin/cabinet ``body``
root carries several parallel child mechanisms that each mate to an independent
face/recess of the same chassis:

  BODY_FORM (root shell): rect_cabinet (rounded box) | round_drum (cylinder)
  ACCESS   : pull_out_basket (PRISMATIC drawer) | hinged_door (REVOLUTE +Z door
             + fixed bin) | tilt_head (REVOLUTE +X head that splits off the body)
  FEED     : open_feed_slot (host visual) | autofeed_lid (REVOLUTE +X lid)
  CUTTING  : static_rollers (host visuals) | powered_shafts (2×CONTINUOUS +X)
  SUPPORT  : caster_wheels (4×CONTINUOUS +X) | desk_feet (4 fixed foot visuals)
  multiplicity: button_count N in {2,3,5}

The top-surface children (feed / cutting / buttons / switch) parent to ``top_part``
= the ``head`` part when ACCESS==tilt_head (so they tilt with the head), else the
``body``. A single ``_to_top`` transform maps world coords to head-local when
tilted (head-local origin = the world rear-top hinge point).

Object-intrinsic frame (001 family, adopted): +Y out of the FRONT face, +Z up,
+X = width. Compatibility gates: round_drum ⇒ pull_out_basket only; hinged_door /
tilt_head ⇒ rect_cabinet only.

5-star sources adapted (AUTHORING §A Rule 3 — real cadquery / TireGeometry /
Extrude geometry kept, never downgraded to placeholders):
  rec_workspace__paper_shredder__001 / __002        : rect body + basket + feed
      slot + controls + static cutter rollers + caster wheels
  rec_paper_shredder_var_round_bin                  : cylindrical drum shell
  rec_paper_shredder_var_door                       : side-hinged cabinet door
  rec_paper_shredder_var_tilt_head                  : tilt-up shredder head
  rec_paper_shredder_var_autofeed_lid               : feed housing + hinged lid
  rec_paper_shredder_var_cutter_shafts              : powered cutter shafts
  rec_paper_shredder_var_desk_feet                  : fixed rubber feet
  rec_paper_shredder_var_controls_n5                : 5-button control array

__modular__ = True
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Literal, Optional

import cadquery as cq
from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    Inertial,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    TireGeometry,
    mesh_from_cadquery,
    mesh_from_geometry,
)

__modular__ = True


# ====================================================================== #
# Slot enums + weighted domains                                          #
# ====================================================================== #

BodyForm = Literal["rect_cabinet", "round_drum"]
Access = Literal["pull_out_basket", "hinged_door", "tilt_head"]
Feed = Literal["open_feed_slot", "autofeed_lid"]
Cutting = Literal["static_rollers", "powered_shafts"]
Support = Literal["caster_wheels", "desk_feet"]
PaletteStyle = Literal["charcoal", "gloss_black", "graphite", "silver_top", "warm_grey"]

BODY_FORMS: tuple[BodyForm, ...] = ("rect_cabinet", "round_drum")
RECT_ACCESS: tuple[Access, ...] = ("pull_out_basket", "hinged_door", "tilt_head")
FEEDS: tuple[Feed, ...] = ("open_feed_slot", "autofeed_lid")
CUTTINGS: tuple[Cutting, ...] = ("static_rollers", "powered_shafts")
SUPPORTS: tuple[Support, ...] = ("caster_wheels", "desk_feet")
BUTTON_COUNTS: tuple[int, ...] = (2, 3, 5)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "charcoal",
    "gloss_black",
    "graphite",
    "silver_top",
    "warm_grey",
)


# ====================================================================== #
# Palettes (body / head / window / control / rubber / silver tokens)     #
# ====================================================================== #

PALETTE_PRESETS: dict[str, dict[str, tuple[float, float, float, float]]] = {
    "charcoal": {
        "body": (0.035, 0.038, 0.036, 1.0),
        "head": (0.015, 0.016, 0.016, 1.0),
        "gloss": (0.0, 0.0, 0.0, 1.0),
        "silver": (0.72, 0.72, 0.68, 1.0),
        "smoked": (0.08, 0.10, 0.11, 0.46),
        "control": (0.82, 0.84, 0.80, 1.0),
        "rubber": (0.004, 0.004, 0.004, 1.0),
        "paper": (0.92, 0.93, 0.96, 1.0),
    },
    "gloss_black": {
        "body": (0.010, 0.010, 0.011, 1.0),
        "head": (0.0, 0.0, 0.0, 1.0),
        "gloss": (0.02, 0.02, 0.02, 1.0),
        "silver": (0.80, 0.81, 0.83, 1.0),
        "smoked": (0.06, 0.075, 0.08, 0.46),
        "control": (0.55, 0.56, 0.58, 1.0),
        "rubber": (0.002, 0.002, 0.002, 1.0),
        "paper": (0.92, 0.93, 0.96, 1.0),
    },
    "graphite": {
        "body": (0.16, 0.17, 0.18, 1.0),
        "head": (0.10, 0.11, 0.12, 1.0),
        "gloss": (0.06, 0.06, 0.07, 1.0),
        "silver": (0.78, 0.79, 0.81, 1.0),
        "smoked": (0.10, 0.12, 0.14, 0.46),
        "control": (0.86, 0.87, 0.89, 1.0),
        "rubber": (0.02, 0.02, 0.02, 1.0),
        "paper": (0.93, 0.94, 0.96, 1.0),
    },
    "silver_top": {
        "body": (0.22, 0.23, 0.24, 1.0),
        "head": (0.13, 0.14, 0.15, 1.0),
        "gloss": (0.05, 0.05, 0.06, 1.0),
        "silver": (0.82, 0.83, 0.85, 1.0),
        "smoked": (0.09, 0.11, 0.13, 0.46),
        "control": (0.88, 0.89, 0.90, 1.0),
        "rubber": (0.03, 0.03, 0.03, 1.0),
        "paper": (0.94, 0.95, 0.97, 1.0),
    },
    "warm_grey": {
        "body": (0.30, 0.29, 0.27, 1.0),
        "head": (0.20, 0.19, 0.18, 1.0),
        "gloss": (0.10, 0.09, 0.08, 1.0),
        "silver": (0.74, 0.72, 0.68, 1.0),
        "smoked": (0.12, 0.11, 0.10, 0.46),
        "control": (0.86, 0.84, 0.80, 1.0),
        "rubber": (0.04, 0.04, 0.04, 1.0),
        "paper": (0.94, 0.93, 0.90, 1.0),
    },
}


# ====================================================================== #
# Config                                                                 #
# ====================================================================== #


@dataclass(frozen=True)
class PaperShredderConfig:
    """Public, unclamped config (the sampler's raw draw)."""

    body_form: BodyForm = "rect_cabinet"
    access: Access = "pull_out_basket"
    feed: Feed = "open_feed_slot"
    cutting: Cutting = "static_rollers"
    support: Support = "caster_wheels"
    button_count: int = 3
    palette_style: PaletteStyle = "charcoal"

    body_width_scale: float = 1.0
    body_height_scale: float = 1.0
    body_depth_scale: float = 1.0

    basket_travel: float = 0.120
    door_open_angle_deg: float = 100.0
    head_tilt_angle_deg: float = 80.0
    lid_open_angle_deg: float = 95.0


@dataclass(frozen=True)
class ResolvedPaperShredderConfig:
    body_form: BodyForm
    access: Access
    feed: Feed
    cutting: Cutting
    support: Support
    button_count: int
    palette_style: PaletteStyle

    # scales
    ws: float
    ds: float
    hs: float

    # master body dims
    body_w: float
    body_d: float
    lower_h: float
    base_z: float
    lower_top_z: float
    front_y: float
    rear_y: float

    # cavity (front bin opening)
    cavity_w: float
    cavity_d: float
    cavity_h: float
    cavity_cy: float
    cavity_cz: float

    # head + top surface
    head_top_z: float
    top_z: float
    throat_z: float
    hinge_z: float  # head tilt hinge z (world)

    # round drum
    drum_r: float
    drum_h: float

    # basket footprint (fits cavity)
    basket_w: float
    basket_d: float

    # caster ring
    caster_x: float
    caster_y: float
    caster_ring_r: float

    # joint ranges (radians / metres)
    basket_travel: float
    door_open_angle: float
    head_tilt_angle: float
    lid_open_angle: float


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def config_from_seed(seed: int) -> PaperShredderConfig:
    """Deterministic per-seed procedural sampling (seed 0 is not special).

    Weighted draw over the 6 discrete axes with body_form->access gating and a
    mild bias toward the origin baseline (rect + basket + open slot + static
    rollers + casters + N=3) so the common console shredder appears often while
    every legal combo remains reachable.
    """
    rng = random.Random(seed * 2654435761 + 40503)

    body_form = rng.choices(BODY_FORMS, weights=(0.72, 0.28), k=1)[0]
    if body_form == "round_drum":
        # A rectangular swing door / rear tilt-head hinge do not seat on a round
        # drum wall (round+lift-off head was only a compatibility_probe).
        access: Access = "pull_out_basket"
    else:
        access = rng.choices(RECT_ACCESS, weights=(0.50, 0.25, 0.25), k=1)[0]

    feed = rng.choices(FEEDS, weights=(0.60, 0.40), k=1)[0]
    cutting = rng.choices(CUTTINGS, weights=(0.58, 0.42), k=1)[0]
    support = rng.choices(SUPPORTS, weights=(0.62, 0.38), k=1)[0]
    button_count = rng.choices(BUTTON_COUNTS, weights=(0.30, 0.45, 0.25), k=1)[0]
    palette_style = rng.choice(PALETTE_STYLES)

    return PaperShredderConfig(
        body_form=body_form,
        access=access,
        feed=feed,
        cutting=cutting,
        support=support,
        button_count=button_count,
        palette_style=palette_style,
        body_width_scale=rng.uniform(0.90, 1.12),
        body_height_scale=rng.uniform(0.92, 1.10),
        body_depth_scale=rng.uniform(0.94, 1.08),
        basket_travel=rng.uniform(0.09, 0.13),
        door_open_angle_deg=rng.uniform(90.0, 105.0),
        head_tilt_angle_deg=rng.uniform(70.0, 85.0),
        lid_open_angle_deg=rng.uniform(85.0, 100.0),
    )


def resolve_config(config: PaperShredderConfig) -> ResolvedPaperShredderConfig:
    body_form = config.body_form if config.body_form in BODY_FORMS else "rect_cabinet"
    access = config.access
    # Enforce compatibility gates.
    if body_form == "round_drum":
        access = "pull_out_basket"
    if access not in RECT_ACCESS:
        access = "pull_out_basket"

    # Compatibility gate: the tilt-up head carries only host-visual top features
    # (open feed slot + static rollers). Moving top-surface CHILD parts on a
    # tilting head are gated to the non-tilt accesses.
    feed = config.feed if config.feed in FEEDS else "open_feed_slot"
    cutting = config.cutting if config.cutting in CUTTINGS else "static_rollers"
    if access == "tilt_head":
        feed = "open_feed_slot"
        cutting = "static_rollers"

    ws = _clamp(config.body_width_scale, 0.90, 1.12)
    ds = _clamp(config.body_depth_scale, 0.94, 1.08)
    hs = _clamp(config.body_height_scale, 0.92, 1.10)

    body_w = 0.42 * ws
    body_d = 0.34 * ds
    lower_h = 0.49 * hs
    base_z = 0.058
    lower_top_z = base_z + lower_h
    front_y = body_d / 2.0
    rear_y = -body_d / 2.0

    # Front bin cavity (open at the front).
    cavity_w = body_w - 0.098
    cavity_d = 0.335 * ds
    cavity_h = 0.405 * hs
    cavity_cy = 0.030 * ds
    cavity_cz = base_z + 0.244 * hs

    head_top_z = lower_top_z + 0.082 * hs
    top_z = head_top_z + 0.004
    # Throat housing breaks the top surface (intersects the top plate) so it is a
    # connected feature of the top part, not a buried island.
    throat_z = top_z - 0.006
    hinge_z = lower_top_z + 0.004

    drum_r = 0.195 * ws
    drum_h = 0.400 * hs

    basket_w = cavity_w - 0.030
    # Front-back depth. At q=0 the basket is seated (front panel flush with the
    # front face at front_y); it slides OUT at positive q. Depth is bounded so
    # the seated back stays ahead of the cavity rear wall.
    basket_d = min(0.240 * ds, cavity_d - 0.030)
    if body_form == "round_drum":
        # Basket must fit inside the circular wall.
        basket_w = min(basket_w, 2.0 * (drum_r - 0.040))

    caster_x = body_w / 2.0 - 0.050
    caster_y = body_d / 2.0 - 0.045
    caster_ring_r = drum_r - 0.075

    basket_travel = _clamp(config.basket_travel, 0.09, 0.13)
    basket_travel = min(basket_travel, cavity_d - 0.14)

    return ResolvedPaperShredderConfig(
        body_form=body_form,
        access=access,
        feed=feed,
        cutting=cutting,
        support=config.support if config.support in SUPPORTS else "caster_wheels",
        button_count=int(config.button_count) if int(config.button_count) in BUTTON_COUNTS else 3,
        palette_style=config.palette_style if config.palette_style in PALETTE_PRESETS else "charcoal",
        ws=ws,
        ds=ds,
        hs=hs,
        body_w=body_w,
        body_d=body_d,
        lower_h=lower_h,
        base_z=base_z,
        lower_top_z=lower_top_z,
        front_y=front_y,
        rear_y=rear_y,
        cavity_w=cavity_w,
        cavity_d=cavity_d,
        cavity_h=cavity_h,
        cavity_cy=cavity_cy,
        cavity_cz=cavity_cz,
        head_top_z=head_top_z,
        top_z=top_z,
        throat_z=throat_z,
        hinge_z=hinge_z,
        drum_r=drum_r,
        drum_h=drum_h,
        basket_w=basket_w,
        basket_d=basket_d,
        caster_x=caster_x,
        caster_y=caster_y,
        caster_ring_r=caster_ring_r,
        basket_travel=basket_travel,
        door_open_angle=math.radians(_clamp(config.door_open_angle_deg, 90.0, 105.0)),
        head_tilt_angle=math.radians(_clamp(config.head_tilt_angle_deg, 70.0, 85.0)),
        lid_open_angle=math.radians(_clamp(config.lid_open_angle_deg, 85.0, 100.0)),
    )


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    """Per-seed module picks consumed by the axis_realization report."""
    r = resolve_config(config_from_seed(seed))
    return [
        ("body_form", r.body_form),
        ("access", r.access),
        ("feed", r.feed),
        ("cutting", r.cutting),
        ("support", r.support),
        ("button_count", f"buttons_{r.button_count}"),
    ]


# ====================================================================== #
# Geometry helpers                                                       #
# ====================================================================== #


def _rounded_box(size: tuple[float, float, float], radius: float = 0.0) -> cq.Workplane:
    sx, sy, sz = size
    shape = cq.Workplane("XY").box(sx, sy, sz)
    if radius > 0.0:
        shape = shape.edges("|Z").fillet(min(radius, sx * 0.34, sy * 0.34))
    return shape


def _rect_body_shell(r: ResolvedPaperShredderConfig, include_head: bool) -> cq.Workplane:
    """Rounded rectangular cabinet: side/rear/bin frame + optional overhang head."""
    lower = _rounded_box((r.body_w, r.body_d, r.lower_h), 0.020 * r.hs).translate(
        (0.0, 0.0, r.base_z + r.lower_h / 2.0)
    )
    cavity = cq.Workplane("XY").box(r.cavity_w, r.cavity_d, r.cavity_h).translate(
        (0.0, r.cavity_cy, r.cavity_cz)
    )
    body = lower.cut(cavity)
    if include_head:
        head = _rounded_box(
            (r.body_w + 0.020, r.body_d + 0.025, 0.120 * r.hs), 0.030 * r.hs
        ).translate((0.0, -0.005 * r.ds, r.head_top_z - 0.060 * r.hs))
        body = body.union(head)
    plinth = _rounded_box((r.body_w, 0.080 * r.ds, 0.040 * r.hs), 0.012).translate(
        (0.0, 0.130 * r.ds, r.base_z + 0.017 * r.hs)
    )
    return body.union(plinth)


def _round_body_shell(r: ResolvedPaperShredderConfig) -> cq.Workplane:
    """Hollow cylindrical drum wall with a rectangular front basket opening."""
    outer_r = r.drum_r
    wall = 0.018
    height = r.drum_h
    z0 = r.base_z + 0.013
    shell = cq.Workplane("XY").circle(outer_r).circle(outer_r - wall).extrude(height)
    cut_half_w = min(0.155, outer_r - 0.030)
    cut_lo = 0.030
    cut_hi = height - 0.006
    cutter = cq.Workplane("XY").box(
        cut_half_w * 2.0, wall * 5.0, cut_hi - cut_lo
    ).translate((0.0, outer_r, (cut_lo + cut_hi) / 2.0))
    shell = shell.cut(cutter)
    shell = shell.translate((0.0, 0.0, z0))
    # Circular base plate.
    base = cq.Workplane("XY").circle(outer_r).extrude(0.018).translate((0.0, 0.0, r.base_z))
    shell = shell.union(base)
    # Cylindrical overhang head: extended DOWN to overlap the drum wall top so it
    # fuses into one connected solid (no floating head island).
    wall_top = z0 + height
    head_bottom = wall_top - 0.014
    head_h = r.head_top_z - head_bottom
    head = (
        cq.Workplane("XY")
        .circle(outer_r + 0.008)
        .extrude(head_h)
        .translate((0.0, 0.0, head_bottom))
    )
    return shell.union(head)


def _paper_fill_mesh(r: ResolvedPaperShredderConfig, joint_y: float = 0.0):
    """A single connected shredded-paper mass (adapted from 001 L74-L149).

    ``joint_y`` is the basket world y-offset; for the round drum the mass is
    clamped so its corners stay inside the cylindrical inner wall.
    """
    from sdk import MeshGeometry

    width = min(0.265, r.basket_w - 0.020)
    depth = min(0.205, r.basket_d - 0.080)
    if r.body_form == "round_drum":
        # Keep the packed paper inside the drum inner radius given the basket's
        # forward offset (paper is centred at basket-local origin => world y).
        inner = r.drum_r - 0.026
        margin = abs(joint_y)
        # Largest half-depth so the front corner clears the inner wall.
        max_hd = max(0.05, (inner ** 2 - min(0.5 * width, inner - 0.01) ** 2) ** 0.5 - margin)
        depth = min(depth, 2.0 * max_hd)
        width = min(width, 2.0 * (inner - 0.02))
    nx, ny = 8, 7
    geom = MeshGeometry()
    top: list[list[int]] = []
    bot: list[list[int]] = []
    for ix in range(nx + 1):
        tr, br = [], []
        x = -width / 2.0 + width * ix / nx
        for iy in range(ny + 1):
            y = -depth / 2.0 + depth * iy / ny
            z = 0.130 + 0.010 * math.sin(ix * 1.7) + 0.007 * math.cos(iy * 2.3)
            tr.append(geom.add_vertex(x, y, z))
            br.append(geom.add_vertex(x, y, 0.0))
        top.append(tr)
        bot.append(br)
    for ix in range(nx):
        for iy in range(ny):
            a, b, c, d = top[ix][iy], top[ix + 1][iy], top[ix + 1][iy + 1], top[ix][iy + 1]
            geom.add_face(a, b, c)
            geom.add_face(a, c, d)
            ab, bb, cb, db = bot[ix][iy], bot[ix + 1][iy], bot[ix + 1][iy + 1], bot[ix][iy + 1]
            geom.add_face(ab, cb, bb)
            geom.add_face(ab, db, cb)
    for ix in range(nx):
        a, b = top[ix][0], top[ix + 1][0]
        ab, bb = bot[ix][0], bot[ix + 1][0]
        geom.add_face(ab, a, b)
        geom.add_face(ab, b, bb)
        c, d = top[ix][ny], top[ix + 1][ny]
        cb, db = bot[ix][ny], bot[ix + 1][ny]
        geom.add_face(cb, db, d)
        geom.add_face(cb, d, c)
    for iy in range(ny):
        a, b = top[0][iy], top[0][iy + 1]
        ab, bb = bot[0][iy], bot[0][iy + 1]
        geom.add_face(ab, bb, b)
        geom.add_face(ab, b, a)
        c, d = top[nx][iy], top[nx][iy + 1]
        cb, db = bot[nx][iy], bot[nx][iy + 1]
        geom.add_face(cb, c, d)
        geom.add_face(cb, d, db)
    return mesh_from_geometry(geom, "paper_fill")


# ====================================================================== #
# Root body + top-surface helpers                                        #
# ====================================================================== #


def _to_top(r: ResolvedPaperShredderConfig, x: float, y: float, z: float) -> tuple[float, float, float]:
    """Map a WORLD coord onto the top_part local frame. Identity for body-mounted
    top surfaces; head-local (world minus hinge) when ACCESS==tilt_head."""
    if r.access == "tilt_head":
        return (x, y - r.rear_y, z - r.hinge_z)
    return (x, y, z)


def _build_body(model: ArticulatedObject, r: ResolvedPaperShredderConfig, mats: dict) -> None:
    body = model.part("body")
    include_head = r.access != "tilt_head"  # tilt splits the head off
    if r.body_form == "round_drum":
        body.visual(
            mesh_from_cadquery(_round_body_shell(r), "body_shell", tolerance=0.0012),
            material=mats["body"],
            name="lower_shell", material_class_id="plastic.opaque_glossy_molded",
        )
    else:
        body.visual(
            mesh_from_cadquery(_rect_body_shell(r, include_head), "body_shell", tolerance=0.0012),
            material=mats["body"],
            name="lower_shell", material_class_id="plastic.opaque_glossy_molded",
        )

    # Basket slide guide rails: bridge from the cavity side wall inward to the
    # basket runner (a ~2 mm light overlap on each end) so the rail is supported
    # by the shell AND retains/contacts the basket runner at every travel pose.
    if r.body_form != "round_drum":
        # Slide/guide rails carry the basket runners (drawer AND the fixed door
        # bin, so the bin stays supported by real contact with the shell).
        # Runner outer face is at cavity_w/2 - 0.018 (see _build_basket); the
        # cavity wall inner face is at cavity_w/2. Centre the 0.022-wide rail so
        # it embeds 2 mm into the wall and overlaps the runner by ~2 mm.
        rail_cx = r.cavity_w / 2.0 - 0.006
        rail_z = 0.115 + 0.152 * r.hs  # matches the basket runner world z
        for i, x in enumerate((-rail_cx, rail_cx)):
            body.visual(
                Box((0.016, 0.225 * r.ds, 0.020)),
                origin=Origin(xyz=(x, r.cavity_cy - 0.020, rail_z)),
                material=mats["gloss"],
                name=f"guide_{i}", material_class_id="plastic.opaque_glossy_molded",
            )

    # Side viewing window recessed into the shell wall (visible + connected). On
    # the round drum the flat pane is embedded a few mm into the curved wall so
    # it overlaps the wall band solidly (not just a tangent edge).
    if r.body_form == "round_drum":
        win_x = -(r.drum_r - 0.008)
        win_th = 0.012
    else:
        win_x = -(r.body_w / 2.0)
        win_th = 0.006
    body.visual(
        Box((win_th, 0.058 * r.ds, 0.150 * r.hs)),
        origin=Origin(xyz=(win_x, -0.030 * r.ds, r.cavity_cz)),
        material=mats["smoked"],
        name="side_window", material_class_id="glass.smoked_tinted",
    )
    body.inertial = Inertial.from_geometry(
        Box((r.body_w, r.body_d, r.lower_top_z + 0.10)),
        mass=9.0,
        origin=Origin(xyz=(0.0, 0.0, (r.lower_top_z + 0.10) / 2.0)),
    )


def _build_head_part(model: ArticulatedObject, r: ResolvedPaperShredderConfig, mats: dict, overlaps: list) -> None:
    """Tilt-up head part (ACCESS==tilt_head). Head-local origin = world hinge."""
    body = model.get_part("body")
    # Body-side hinge barrel at the rear top edge.
    body.visual(
        Cylinder(radius=0.012, length=0.38 * r.ws),
        origin=Origin(xyz=(0.0, r.rear_y, r.hinge_z), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["head"],
        name="hinge_barrel", material_class_id="metal.blackened_gunmetal",
    )
    head = model.part("head")
    head_solid = _rounded_box(
        (r.body_w + 0.020, r.body_d + 0.025, 0.080 * r.hs), 0.030 * r.hs
    ).translate((0.0, (r.body_d / 2.0) - 0.005, 0.040 * r.hs))
    head.visual(mesh_from_cadquery(head_solid, "head_shell", tolerance=0.0012), material=mats["head"], name="head_shell", material_class_id="plastic.opaque_glossy_molded")
    head.visual(
        Cylinder(radius=0.014, length=0.36 * r.ws),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["head"],
        name="hinge_knuckle", material_class_id="metal.blackened_gunmetal",
    )
    head.inertial = Inertial.from_geometry(
        Box((r.body_w, r.body_d, 0.08)), mass=2.6,
        origin=Origin(xyz=(0.0, r.body_d / 2.0, 0.04)),
    )
    model.articulation(
        "body_to_head",
        ArticulationType.REVOLUTE,
        parent=body,
        child=head,
        origin=Origin(xyz=(0.0, r.rear_y, r.hinge_z)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=8.0, velocity=1.5, lower=0.0, upper=r.head_tilt_angle),
    )
    overlaps.append(("body", "head", "hinge_barrel", "hinge_knuckle",
                     "Head hinge knuckle wraps the body barrel pin (captured pivot)."))
    overlaps.append(("body", "head", "hinge_barrel", "head_shell",
                     "Barrel pin protrudes into the rear of the head housing at the pivot."))
    overlaps.append(("body", "head", "lower_shell", "hinge_knuckle",
                     "Head hinge knuckle nests against the rear-top shell rim at the pivot boss."))


def _top_plate_and_feed(model: ArticulatedObject, r: ResolvedPaperShredderConfig, mats: dict, top_name: str) -> None:
    top = model.get_part(top_name)
    # Silver top plate.
    tp = _rounded_box((0.285 * r.ws, 0.225 * r.ds, 0.008), 0.010).translate(
        _to_top(r, 0.0, -0.022 * r.ds, r.top_z)
    )
    top.visual(mesh_from_cadquery(tp, "silver_top_panel", tolerance=0.0008), material=mats["silver"], name="top_panel", material_class_id="metal.brushed_silver")
    if r.feed == "open_feed_slot":
        top.visual(
            Box((0.235 * r.ws, 0.020 * r.ds, 0.006)),
            origin=Origin(xyz=_to_top(r, 0.0, -0.100 * r.ds, r.top_z + 0.004)),
            material=mats["gloss"],
            name="feed_slot", material_class_id="plastic.opaque_glossy_molded",
        )


def _build_feed(model: ArticulatedObject, r: ResolvedPaperShredderConfig, mats: dict, top_name: str, overlaps: list) -> None:
    if r.feed != "autofeed_lid":
        return
    top = model.get_part(top_name)
    # Raised auto-feed housing with a recessed stack-tray well.
    hz = r.top_z + 0.026
    outer = _rounded_box((0.260 * r.ws, 0.200 * r.ds, 0.045 * r.hs), 0.012).translate(
        _to_top(r, 0.0, -0.040 * r.ds, hz)
    )
    recess = cq.Workplane("XY").box(0.220 * r.ws, 0.160 * r.ds, 0.032 * r.hs).translate(
        _to_top(r, 0.0, -0.035 * r.ds, hz + 0.014)
    )
    top.visual(mesh_from_cadquery(outer.cut(recess), "feed_housing", tolerance=0.001), material=mats["head"], name="feed_housing", material_class_id="plastic.opaque_glossy_molded")
    top.visual(
        Box((0.218 * r.ws, 0.158 * r.ds, 0.008)),
        origin=Origin(xyz=_to_top(r, 0.0, -0.035 * r.ds, hz - 0.002 * r.hs)),
        material=mats["gloss"],
        name="stack_tray", material_class_id="plastic.opaque_glossy_molded",
    )
    barrel_z = hz + 0.020
    barrel_y = -0.040 * r.ds - 0.097 * r.ds
    top.visual(
        Cylinder(radius=0.005, length=0.220 * r.ws),
        origin=Origin(xyz=_to_top(r, 0.0, barrel_y, barrel_z), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["head"],
        name="lid_hinge_barrel", material_class_id="metal.blackened_gunmetal",
    )
    # Hinged feed lid part (rear hinge, opens up).
    feed_lid = model.part("feed_lid")
    feed_lid.visual(Box((0.240 * r.ws, 0.180 * r.ds, 0.008)), origin=Origin(xyz=(0.0, 0.090 * r.ds, 0.007)), material=mats["head"], name="lid_panel", material_class_id="plastic.opaque_glossy_molded")
    feed_lid.visual(Box((0.244 * r.ws, 0.184 * r.ds, 0.003)), origin=Origin(xyz=(0.0, 0.090 * r.ds, 0.013)), material=mats["gloss"], name="lid_rim", material_class_id="plastic.opaque_glossy_molded")
    feed_lid.visual(Box((0.060 * r.ws, 0.018 * r.ds, 0.012)), origin=Origin(xyz=(0.0, 0.175 * r.ds, 0.010)), material=mats["silver"], name="lid_grip", material_class_id="metal.brushed_silver")
    feed_lid.visual(Cylinder(radius=0.006, length=0.200 * r.ws), origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)), material=mats["head"], name="lid_knuckle", material_class_id="metal.blackened_gunmetal")
    feed_lid.inertial = Inertial.from_geometry(Box((0.24, 0.18, 0.02)), mass=0.25, origin=Origin(xyz=(0.0, 0.09, 0.007)))
    model.articulation(
        f"{top_name}_to_feed_lid",
        ArticulationType.REVOLUTE,
        parent=top,
        child=feed_lid,
        origin=Origin(xyz=_to_top(r, 0.0, barrel_y, barrel_z)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=8.0, velocity=1.2, lower=0.0, upper=r.lid_open_angle),
    )
    overlaps.append((top_name, "feed_lid", "lid_hinge_barrel", "lid_knuckle",
                     "Feed-lid knuckle wraps the housing hinge barrel (captured pivot)."))
    overlaps.append((top_name, "feed_lid", "feed_housing", "lid_knuckle",
                     "Lid knuckle nests in the rear rim of the feed housing."))


def _build_cutting(model: ArticulatedObject, r: ResolvedPaperShredderConfig, mats: dict, top_name: str, overlaps: list) -> None:
    top = model.get_part(top_name)
    throat_y = -0.100 * r.ds
    # Shredder throat recess block on the top part (host visual for both modules).
    top.visual(
        Box((0.300 * r.ws, 0.030 * r.ds, 0.026 * r.hs)),
        origin=Origin(xyz=_to_top(r, 0.0, throat_y, r.throat_z)),
        material=mats["gloss"],
        name="shredder_throat", material_class_id="plastic.opaque_glossy_molded",
    )
    cutter_len = 0.280 * r.ws
    if r.cutting == "static_rollers":
        for i, dy in enumerate((-0.008 * r.ds, 0.008 * r.ds)):
            top.visual(
                Cylinder(radius=0.010, length=cutter_len),
                origin=Origin(xyz=_to_top(r, 0.0, throat_y + dy, r.throat_z - 0.006), rpy=(0.0, math.pi / 2.0, 0.0)),
                material=mats["gloss"],
                name=f"cutter_roller_{i}", material_class_id="metal.stainless_matte",
            )
    else:  # powered_shafts
        for i, dy in enumerate((-0.013 * r.ds, 0.013 * r.ds)):
            shaft = model.part(f"cutter_shaft_{i}")
            shaft.visual(
                Cylinder(radius=0.010, length=cutter_len),
                origin=Origin(rpy=(0.0, math.pi / 2.0, 0.0)),
                material=mats["gloss"],
                name="shaft", material_class_id="metal.stainless_matte",
            )
            shaft.inertial = Inertial.from_geometry(
                Cylinder(radius=0.010, length=cutter_len), mass=0.12,
                origin=Origin(rpy=(0.0, math.pi / 2.0, 0.0)),
            )
            model.articulation(
                f"{top_name}_to_cutter_shaft_{i}",
                ArticulationType.CONTINUOUS,
                parent=top,
                child=shaft,
                origin=Origin(xyz=_to_top(r, 0.0, throat_y + dy, r.throat_z - 0.006)),
                axis=(1.0, 0.0, 0.0),
                motion_limits=MotionLimits(effort=4.0, velocity=8.0),
            )
            overlaps.append((top_name, f"cutter_shaft_{i}", "shredder_throat", "shaft",
                             "Cutter shaft is captured inside the shredder throat (pin-in-sleeve)."))
            # The throat is bored into the head; the spinning shaft rides in that
            # bore, so it also overlaps the shell/head housing at the pivot.
            shell_elem = "head_shell" if top_name == "head" else "lower_shell"
            overlaps.append((top_name, f"cutter_shaft_{i}", shell_elem, "shaft",
                             "Cutter shaft rides in the throat bore through the shredder head housing."))
            overlaps.append((top_name, f"cutter_shaft_{i}", "top_panel", "shaft",
                             "Cutter shaft rides in the throat bore under the top plate."))


def _build_controls(model: ArticulatedObject, r: ResolvedPaperShredderConfig, mats: dict, top_name: str, overlaps: list) -> None:
    top = model.get_part(top_name)
    ctrl_y = 0.070 * r.ds
    # Control panel recess.
    top.visual(
        Box((0.150 * r.ws, 0.044 * r.ds, 0.006)),
        origin=Origin(xyz=_to_top(r, -0.060 * r.ws, ctrl_y, r.top_z)),
        material=mats["gloss"],
        name="control_panel", material_class_id="plastic.opaque_glossy_molded",
    )
    n = r.button_count
    spacing = 0.023 * r.ws
    base_x = -0.060 * r.ws - (n - 1) * spacing / 2.0
    for i in range(n):
        bx = base_x + i * spacing
        button = model.part(f"button_{i}")
        button.visual(
            Cylinder(radius=0.0075, length=0.006),
            origin=Origin(xyz=(0.0, 0.0, 0.003)),
            material=mats["control"],
            name="button_cap", material_class_id="plastic.opaque_glossy_molded",
        )
        button.inertial = Inertial.from_geometry(Cylinder(radius=0.0075, length=0.006), mass=0.01)
        model.articulation(
            f"{top_name}_to_button_{i}",
            ArticulationType.PRISMATIC,
            parent=top,
            child=button,
            origin=Origin(xyz=_to_top(r, bx, ctrl_y, r.top_z + 0.003)),
            axis=(0.0, 0.0, -1.0),
            motion_limits=MotionLimits(effort=2.0, velocity=0.05, lower=0.0, upper=0.004),
        )
        # The push button seats in its top-panel recess; on-axis press overlaps
        # the control panel / top plate (captured seated interface).
        overlaps.append((f"button_{i}", top_name, "button_cap", "control_panel",
                         "Push button seats into the control-panel recess (on-axis press)."))
        overlaps.append((f"button_{i}", top_name, "button_cap", "top_panel",
                         "Push button seats into the top-plate recess (on-axis press)."))
    # Slide mode switch.
    switch = model.part("mode_switch")
    switch.visual(Box((0.019, 0.012, 0.006)), origin=Origin(xyz=(0.0, 0.0, 0.003)), material=mats["control"], name="switch_slider", material_class_id="plastic.opaque_glossy_molded")
    switch.inertial = Inertial.from_geometry(Box((0.019, 0.012, 0.006)), mass=0.01)
    model.articulation(
        f"{top_name}_to_mode_switch",
        ArticulationType.PRISMATIC,
        parent=top,
        child=switch,
        origin=Origin(xyz=_to_top(r, base_x + n * spacing + 0.010, ctrl_y, r.top_z + 0.004)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=1.0, velocity=0.08, lower=-0.011, upper=0.011),
    )
    overlaps.append(("mode_switch", top_name, "switch_slider", "control_panel",
                     "Slide switch rides in the control-panel recess (captured slider)."))
    overlaps.append(("mode_switch", top_name, "switch_slider", "top_panel",
                     "Slide switch rides in the top-plate recess (captured slider)."))


def _build_basket(model: ArticulatedObject, r: ResolvedPaperShredderConfig, mats: dict, fixed: bool, overlaps: list) -> None:
    body = model.get_part("body")
    basket = model.part("basket")
    bw = r.basket_w
    bd = r.basket_d
    wall = 0.018
    hh = 0.300 * r.hs
    # ``fixed`` == the hinged-door cabinet: the interior is a plain open-front
    # fixed bin (no overlay drawer face) covered by an overlay door. For the
    # sliding accesses (pull-out / tilt-head) the basket is a pull-out drawer
    # with an inset front face.
    bin_mode = fixed
    # Basket seats at the front face at q=0 for every access (the overlay door
    # sits proud in front of the fixed bin, so no recess is needed). The fixed
    # door bin rests on the cavity floor (its FIXED joint origin lands on real
    # shell geometry); the sliding drawer rides the guide rails higher up.
    cavity_floor = r.cavity_cz - r.cavity_h / 2.0
    # The fixed door bin's FIXED joint origin must land within 0.015 m of shell
    # geometry, so keep its origin z close to the cavity floor (still rail-height
    # so the runners keep contacting the guides). The drawer origin stays higher.
    joint_z = (cavity_floor + 0.012) if bin_mode else 0.115
    joint_y = r.front_y - bd / 2.0

    # Basket-local frame: y in [-bd/2 (rear), +bd/2 (front)], z from 0 up. The
    # bottom tray + full-depth side walls + rear wall (+ inset drawer front /
    # bin lip) share edges, so the basket is one connected part. Runners ride the
    # shell guide rails for every access, keeping the fixed door bin supported.
    basket.visual(Box((bw, bd, 0.026)), origin=Origin(xyz=(0.0, 0.0, 0.013)), material=mats["gloss"], name="basket_bottom", material_class_id="plastic.opaque_glossy_molded")
    for i, sx in enumerate((-1.0, 1.0)):
        basket.visual(Box((wall, bd, hh)), origin=Origin(xyz=(sx * (bw / 2.0 - wall / 2.0), 0.0, hh / 2.0)), material=mats["gloss"], name=f"basket_side_{i}", material_class_id="plastic.opaque_glossy_molded")
        # Runner protrudes outward past the side wall so it rides in the body
        # guide rail (declared rail-in-channel overlap in run_tests).
        basket.visual(Box((0.014, bd - 0.020, 0.018)), origin=Origin(xyz=(sx * (bw / 2.0), 0.0, 0.152 * r.hs)), material=mats["gloss"], name=f"runner_{i}", material_class_id="plastic.opaque_glossy_molded")
    basket.visual(Box((bw, wall, hh)), origin=Origin(xyz=(0.0, -bd / 2.0 + wall / 2.0, hh / 2.0)), material=mats["gloss"], name="basket_back", material_class_id="plastic.opaque_glossy_molded")
    if bin_mode:
        # Fixed door bin: plain open-front receptacle with a low front rim (no
        # overlay drawer face); the overlay cabinet door covers it.
        basket.visual(Box((bw, wall, 0.100 * r.hs)), origin=Origin(xyz=(0.0, bd / 2.0 - wall / 2.0, 0.050 * r.hs)), material=mats["gloss"], name="basket_front_lip", material_class_id="plastic.opaque_glossy_molded")
    elif r.body_form == "rect_cabinet":
        # Inset drawer front sized to fit WITHIN the cabinet opening in x and z:
        # narrower than the opening, its z band bounded above by the head/shell
        # ceiling and below by the cavity floor, and its front face flush with
        # the shell front face. Because it stays inside the opening footprint it
        # never bites the surrounding shell face at any travel pose.
        include_head = r.access != "tilt_head"
        ceiling = (r.lower_top_z - 0.046 * r.hs) if include_head else (r.lower_top_z - 0.010)
        # The front must stay within the cavity OPENING in z (never poking into
        # the solid shell above the mouth) as well as below the head/ceiling.
        band_lo = r.cavity_cz - r.cavity_h / 2.0 + 0.018
        band_hi = min(ceiling - 0.014, r.cavity_cz + r.cavity_h / 2.0 - 0.016)
        fp_h = max(0.12, band_hi - band_lo)
        fp_zc = 0.5 * (band_lo + band_hi) - joint_z  # basket-local z
        fp_w = min(bw + 0.040, r.cavity_w - 0.018)
        fp_y = bd / 2.0 - 0.010  # front face flush with the shell front face
        win_h = min(0.052 * r.hs, fp_h * 0.42)
        front_panel = _rounded_box((fp_w, 0.020, fp_h), 0.014)
        window = cq.Workplane("XY").box(0.100, 0.030, win_h).translate((0.0, 0.0, -fp_h * 0.18))
        front_panel = front_panel.cut(window)
        basket.visual(mesh_from_cadquery(front_panel, "basket_front_panel", tolerance=0.001), origin=Origin(xyz=(0.0, fp_y, fp_zc)), material=mats["body"], name="front_panel", material_class_id="plastic.opaque_glossy_molded")
        basket.visual(Box((0.100, 0.004, win_h)), origin=Origin(xyz=(0.0, fp_y + 0.008, fp_zc - fp_h * 0.18)), material=mats["smoked"], name="front_window", material_class_id="glass.smoked_tinted")
        basket.visual(Box((0.126, 0.014, 0.020)), origin=Origin(xyz=(0.0, fp_y + 0.006, fp_zc + fp_h * 0.42)), material=mats["gloss"], name="pull_handle", material_class_id="plastic.opaque_glossy_molded")
    else:  # round_drum: front panel proud of the tray, nested in the drum wall
        fp_w = min(bw + 0.030, 2.0 * (r.drum_r - 0.030))
        fp_h = 0.340 * r.hs
        fp_zc = 0.150 * r.hs
        # Rear kisses the tray front (bd/2) so it stays edge-connected to the
        # basket; the panel is declared to nest inside the drum wall.
        fp_y = bd / 2.0 + 0.008
        front_panel = _rounded_box((fp_w, 0.020, fp_h), 0.014)
        window = cq.Workplane("XY").box(0.100, 0.030, 0.052 * r.hs).translate((0.0, 0.0, -0.030 * r.hs))
        front_panel = front_panel.cut(window)
        basket.visual(mesh_from_cadquery(front_panel, "basket_front_panel", tolerance=0.001), origin=Origin(xyz=(0.0, fp_y, fp_zc)), material=mats["body"], name="front_panel", material_class_id="plastic.opaque_glossy_molded")
        basket.visual(Box((0.100, 0.004, 0.052 * r.hs)), origin=Origin(xyz=(0.0, fp_y + 0.006, fp_zc - 0.030 * r.hs)), material=mats["smoked"], name="front_window", material_class_id="glass.smoked_tinted")
        basket.visual(Box((0.126, 0.014, 0.020)), origin=Origin(xyz=(0.0, fp_y + 0.008, fp_zc + 0.140 * r.hs)), material=mats["gloss"], name="pull_handle", material_class_id="plastic.opaque_glossy_molded")
    basket.visual(_paper_fill_mesh(r, joint_y), origin=Origin(xyz=(0.0, 0.0, 0.024)), material=mats["paper"], name="paper_fill", material_class_id="paper.plain_sheet")
    basket.inertial = Inertial.from_geometry(Box((bw, bd, 0.34)), mass=0.7, origin=Origin(xyz=(0.0, 0.0, 0.15)))

    if bin_mode:
        model.articulation(
            "body_to_basket", ArticulationType.FIXED, parent=body, child=basket,
            origin=Origin(xyz=(0.0, joint_y, joint_z)),
        )
    else:
        model.articulation(
            "body_to_basket", ArticulationType.PRISMATIC, parent=body, child=basket,
            origin=Origin(xyz=(0.0, joint_y, joint_z)),
            axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(effort=45.0, velocity=0.35, lower=0.0, upper=r.basket_travel),
        )
    if r.body_form == "round_drum":
        # Rect basket nested in the round bin: every wall/front/contents rides
        # inside the cylindrical wall envelope (retained insertion), exactly the
        # abstraction the round_bin 5-star source declares for its basket.
        for elem in ("basket_bottom", "basket_side_0", "basket_side_1", "basket_back",
                     "runner_0", "runner_1", "front_panel", "paper_fill"):
            overlaps.append(("basket", "body", elem, "lower_shell",
                             "Basket nests inside the cylindrical drum wall (retained insertion)."))
    else:  # rect drawer and rect door bin both ride the guide rails
        for i in range(2):
            overlaps.append(("basket", "body", f"runner_{i}", f"guide_{i}",
                             "Basket runner rides captured inside the body guide rail (rail-in-channel)."))


def _build_door(model: ArticulatedObject, r: ResolvedPaperShredderConfig, mats: dict, overlaps: list) -> None:
    body = model.get_part("body")
    thickness = 0.020
    # Overlay cabinet door: it sits PROUD of the shell front face (rear flush at
    # front_y) so it never fouls the interior bin. Its z band is bounded below by
    # the cavity opening floor and above by the head-overhang bottom, so the
    # swinging door clears the overhang at every angle.
    ceiling = r.lower_top_z - 0.046 * r.hs  # head-overhang underside
    band_lo = r.cavity_cz - r.cavity_h / 2.0 + 0.006
    band_hi = min(ceiling - 0.012, r.cavity_cz + r.cavity_h / 2.0)
    height = max(0.14, band_hi - band_lo)
    door_zc = 0.5 * (band_lo + band_hi)
    jamb_x = -(r.cavity_w / 2.0 + 0.008)
    width = r.cavity_w + 0.016
    # Push the whole door proud of the face so that even swung past 90 deg its
    # front-face corner near the hinge never dips behind the shell front plane.
    hinge_y = r.front_y + 0.008

    # Body-side hinge barrel at the left front jamb; a fat barrel bites 2 mm into
    # the shell face so it stays connected while the door sits proud.
    body.visual(
        Cylinder(radius=0.010, length=height),
        origin=Origin(xyz=(jamb_x, hinge_y, door_zc)),
        material=mats["head"],
        name="hinge_barrel", material_class_id="metal.blackened_gunmetal",
    )
    door = model.part("door")
    # Hinge edge at local x=0; panel extends toward +x (free edge) and +y (front).
    panel = cq.Workplane("XY").box(width, thickness, height).edges("|Z").fillet(0.006)
    panel = panel.translate((width / 2.0, thickness / 2.0, 0.0))
    win = cq.Workplane("XY").box(0.100, thickness + 0.010, 0.052 * r.hs).translate((width / 2.0, thickness / 2.0, -height * 0.15))
    panel = panel.cut(win)
    door.visual(mesh_from_cadquery(panel, "door_panel", tolerance=0.001), material=mats["body"], name="door_panel", material_class_id="plastic.opaque_glossy_molded")
    door.visual(Box((0.100, 0.004, 0.052 * r.hs)), origin=Origin(xyz=(width / 2.0, thickness + 0.001, -height * 0.15)), material=mats["smoked"], name="front_window", material_class_id="glass.smoked_tinted")
    door.visual(Box((0.110, 0.004, 0.020)), origin=Origin(xyz=(width / 2.0, thickness + 0.001, height * 0.36)), material=mats["gloss"], name="pull_handle", material_class_id="plastic.opaque_glossy_molded")
    door.inertial = Inertial.from_geometry(Box((width, thickness, height)), mass=0.8, origin=Origin(xyz=(width / 2.0, thickness / 2.0, 0.0)))
    model.articulation(
        "body_to_door", ArticulationType.REVOLUTE, parent=body, child=door,
        origin=Origin(xyz=(jamb_x, hinge_y, door_zc)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=8.0, velocity=1.5, lower=0.0, upper=r.door_open_angle),
    )
    overlaps.append(("body", "door", "hinge_barrel", "door_panel",
                     "Hinge barrel pin is captured inside the door panel hinge edge."))


def _build_support(model: ArticulatedObject, r: ResolvedPaperShredderConfig, mats: dict, overlaps: list) -> None:
    body = model.get_part("body")
    if r.body_form == "round_drum":
        rr = r.caster_ring_r
        positions = [
            (-rr * 0.7, rr * 0.7, 0.030),
            (rr * 0.7, rr * 0.7, 0.030),
            (-rr * 0.7, -rr * 0.7, 0.030),
            (rr * 0.7, -rr * 0.7, 0.030),
        ]
    else:
        positions = [
            (-r.caster_x, r.caster_y, 0.030),
            (r.caster_x, r.caster_y, 0.030),
            (-r.caster_x, -r.caster_y, 0.030),
            (r.caster_x, -r.caster_y, 0.030),
        ]
    if r.support == "desk_feet":
        for i, (x, y, _z) in enumerate(positions):
            body.visual(
                Box((0.036, 0.036, 0.024)),
                origin=Origin(xyz=(x, y, r.base_z - 0.008)),
                material=mats["rubber"],
                name=f"foot_{i}", material_class_id="rubber.smooth_plain",
            )
        return
    # caster_wheels
    for i, (x, y, z) in enumerate(positions):
        for j, dx in enumerate((-0.020, 0.020)):
            body.visual(Box((0.006, 0.018, 0.038)), origin=Origin(xyz=(x + dx, y, z + 0.017)), material=mats["head"], name=f"caster_yoke_{i}_{j}", material_class_id="metal.blackened_gunmetal")
        body.visual(Box((0.050, 0.024, 0.010)), origin=Origin(xyz=(x, y, 0.062)), material=mats["head"], name=f"caster_mount_{i}", material_class_id="metal.blackened_gunmetal")
        body.visual(Cylinder(radius=0.006, length=0.054), origin=Origin(xyz=(x, y, z), rpy=(0.0, math.pi / 2.0, 0.0)), material=mats["head"], name=f"caster_axle_{i}", material_class_id="metal.steel_bare")
        wheel = model.part(f"caster_wheel_{i}")
        wheel.visual(mesh_from_geometry(TireGeometry(0.024, 0.024, inner_radius=0.013), f"caster_tire_{i}"), material=mats["rubber"], name="rubber_tire", material_class_id="rubber.smooth_plain")
        wheel.visual(Cylinder(radius=0.014, length=0.027), origin=Origin(rpy=(0.0, math.pi / 2.0, 0.0)), material=mats["head"], name="hub", material_class_id="metal.blackened_gunmetal")
        wheel.inertial = Inertial.from_geometry(Cylinder(radius=0.024, length=0.027), mass=0.05, origin=Origin(rpy=(0.0, math.pi / 2.0, 0.0)))
        model.articulation(
            f"body_to_caster_wheel_{i}", ArticulationType.CONTINUOUS, parent=body, child=wheel,
            origin=Origin(xyz=(x, y, z)), axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=1.5, velocity=8.0),
        )
        overlaps.append(("body", f"caster_wheel_{i}", f"caster_axle_{i}", "hub",
                         "Caster hub rotates around the fixed axle pin (captured)."))


# ====================================================================== #
# Build entry points                                                     #
# ====================================================================== #


def build_paper_shredder(
    config: PaperShredderConfig, *, assets: Optional[AssetContext] = None
) -> ArticulatedObject:
    r = resolve_config(config)
    colors = PALETTE_PRESETS[r.palette_style]
    model = ArticulatedObject(name="paper_shredder", assets=assets)
    mats = {key: model.material(f"ps_{key}", rgba=rgba) for key, rgba in colors.items()}

    overlaps: list[tuple] = []
    top_name = "head" if r.access == "tilt_head" else "body"

    _build_body(model, r, mats)
    if r.access == "tilt_head":
        _build_head_part(model, r, mats, overlaps)

    # Top surface (parented to top_part).
    _top_plate_and_feed(model, r, mats, top_name)
    _build_feed(model, r, mats, top_name, overlaps)
    _build_cutting(model, r, mats, top_name, overlaps)
    _build_controls(model, r, mats, top_name, overlaps)

    # Access mechanism.
    if r.access == "hinged_door":
        _build_basket(model, r, mats, fixed=True, overlaps=overlaps)
        _build_door(model, r, mats, overlaps)
    else:
        _build_basket(model, r, mats, fixed=False, overlaps=overlaps)

    _build_support(model, r, mats, overlaps)

    model._ps_resolved = r  # type: ignore[attr-defined]
    model._ps_overlaps = overlaps  # type: ignore[attr-defined]
    model._ps_top = top_name  # type: ignore[attr-defined]
    return model


def build_seeded_paper_shredder(seed: int) -> ArticulatedObject:
    return build_paper_shredder(config_from_seed(seed))


# ====================================================================== #
# Tests                                                                  #
# ====================================================================== #


def run_paper_shredder_tests(model: ArticulatedObject, config: PaperShredderConfig) -> TestReport:
    ctx = TestContext(model)
    r: ResolvedPaperShredderConfig = getattr(model, "_ps_resolved", None) or resolve_config(config)
    overlaps: list[tuple] = getattr(model, "_ps_overlaps", [])
    top_name: str = getattr(model, "_ps_top", "body")

    # Replay intentional captured-pin / seat overlaps.
    for (pa, pb, ea, eb, reason) in overlaps:
        ctx.allow_overlap(model.get_part(pa), model.get_part(pb), elem_a=ea, elem_b=eb, reason=reason)

    body = model.get_part("body")
    basket = model.get_part("basket")

    # ---- Identity: shredder head + feed over a receptacle ---- #
    body_aabb = ctx.part_world_aabb(body)
    ctx.check(
        "body reads as a bin/cabinet with an overhanging head",
        body_aabb is not None and (body_aabb[1][2] - body_aabb[0][2]) > 0.45,
        details=f"body_aabb={body_aabb}",
    )

    # ---- ACCESS mechanism motion ---- #
    if r.access == "pull_out_basket":
        slide = model.get_articulation("body_to_basket")
        rest = ctx.part_world_position(basket)
        with ctx.pose({slide: r.basket_travel}):
            out = ctx.part_world_position(basket)
        ctx.check(
            "waste basket slides out forward (+Y)",
            rest is not None and out is not None and out[1] > rest[1] + 0.06,
            details=f"rest={rest}, out={out}",
        )
    elif r.access == "hinged_door":
        door = model.get_part("door")
        hinge = model.get_articulation("body_to_door")
        closed = ctx.part_world_aabb(door)
        with ctx.pose({hinge: r.door_open_angle}):
            opened = ctx.part_world_aabb(door)
        ctx.check(
            "cabinet door swings outward (+Y) on the +Z jamb hinge",
            closed is not None and opened is not None and opened[1][1] > closed[1][1] + 0.05,
            details=f"closed={closed}, open={opened}",
        )
        basket_joint = model.get_articulation("body_to_basket")
        ctx.check(
            "interior bin is a fixed receptacle behind the door",
            basket_joint.articulation_type == ArticulationType.FIXED,
            details=f"type={basket_joint.articulation_type}",
        )
    else:  # tilt_head
        head = model.get_part("head")
        hinge = model.get_articulation("body_to_head")
        rest = ctx.part_world_aabb(head)
        with ctx.pose({hinge: r.head_tilt_angle}):
            tilted = ctx.part_world_aabb(head)
        ctx.check(
            "shredder head tilts up exposing the bin",
            rest is not None and tilted is not None and tilted[1][2] > rest[1][2] + 0.06,
            details=f"rest={rest}, tilted={tilted}",
        )

    # ---- FEED lid ---- #
    if r.feed == "autofeed_lid":
        lid = model.get_part("feed_lid")
        lid_joint = model.get_articulation(f"{top_name}_to_feed_lid")
        closed = ctx.part_world_aabb(lid)
        with ctx.pose({lid_joint: r.lid_open_angle}):
            opened = ctx.part_world_aabb(lid)
        ctx.check(
            "auto-feed lid opens upward revealing the tray",
            closed is not None and opened is not None and opened[1][2] > closed[1][2] + 0.04,
            details=f"closed={closed}, open={opened}",
        )

    # ---- CUTTING shafts ---- #
    if r.cutting == "powered_shafts":
        for i in range(2):
            joint = model.get_articulation(f"{top_name}_to_cutter_shaft_{i}")
            ctx.check(
                f"cutter shaft {i} is a CONTINUOUS +X spindle",
                joint.articulation_type == ArticulationType.CONTINUOUS and tuple(joint.axis) == (1.0, 0.0, 0.0),
                details=f"type={joint.articulation_type}, axis={joint.axis}",
            )

    # ---- SUPPORT ---- #
    if r.support == "caster_wheels":
        joint = model.get_articulation("body_to_caster_wheel_0")
        ctx.check(
            "caster wheel is a CONTINUOUS roller about +X",
            joint.articulation_type == ArticulationType.CONTINUOUS and tuple(joint.axis) == (1.0, 0.0, 0.0),
            details=f"type={joint.articulation_type}, axis={joint.axis}",
        )

    # ---- Controls ---- #
    b0_joint = model.get_articulation(f"{top_name}_to_button_0")
    b0 = model.get_part("button_0")
    rest = ctx.part_world_position(b0)
    with ctx.pose({b0_joint: 0.004}):
        pressed = ctx.part_world_position(b0)
    ctx.check(
        "push button depresses downward",
        rest is not None and pressed is not None and pressed[2] < rest[2] - 0.003,
        details=f"rest={rest}, pressed={pressed}",
    )
    sw_joint = model.get_articulation(f"{top_name}_to_mode_switch")
    sw = model.get_part("mode_switch")
    with ctx.pose({sw_joint: -0.011}):
        left = ctx.part_world_position(sw)
    with ctx.pose({sw_joint: 0.011}):
        right = ctx.part_world_position(sw)
    ctx.check(
        "mode switch slides across the panel (+X)",
        left is not None and right is not None and right[0] > left[0] + 0.015,
        details=f"left={left}, right={right}",
    )

    # ---- Rule 5: full-travel non-penetration ---- #
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=48, ignore_fixed=True)

    return ctx.report()


# Aliases the sweep harness / generic model may probe.
build = build_paper_shredder
run_paper_shredder_template_tests = run_paper_shredder_tests


__all__ = [
    "PaperShredderConfig",
    "ResolvedPaperShredderConfig",
    "build_paper_shredder",
    "build_seeded_paper_shredder",
    "config_from_seed",
    "resolve_config",
    "slot_choices_for_seed",
    "run_paper_shredder_tests",
]
