# SPDX-License-Identifier: Apache-2.0

"""Modular template: pictureX_0611 ball transfer unit with spring-loaded ball.

A housing/cup capturing ONE large load-bearing ball that rolls freely on a
captive support-ball race (two CONTINUOUS rolling joints, ball center held
captive), spring-loaded (PRISMATIC preload) or rigidly seated, with a mounting
interface. Derived from the 13 declared 5-star sources under
``data/records/rec_(picturex|ball_transfer_unit_...)*`` — see
``specs_modular_v1/pictureX_0611_ball_transfer_unit_with_spring_loaded_ball.md``.

Slots (all report into ``slot_choices_for_seed``):
  A mount        press_fit | bolt_flange | threaded_stud | side_bracket | machined_square_base
  B body_form    stepped_round_cylinder | hex_prism | shallow_wide_cup   (③ Primary Form Family)
  C preload      spring_prismatic | rigid_fixed_seat                     (② joint type)
  D orientation  ball_up | ball_down                                     (① skeleton)
  E support_ball_count  6..20 single radial ring                         (N multiplicity)
  palette_style  6 realistic steel colorways                            (⑥ finish)

Slots A/B/D co-shape the single ``housing`` cadquery part; C/E hang off the
carrier. ball_down applies a rigid 180 deg rotation about x to the whole
assembly (geometry solids rotated, every joint origin/axis mapped by
R(x,y,z)=(x,-y,-z)) so it is an exact re-expression of the same kinematic tree.
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
    Cylinder,
    MatingContract,
    MotionLimits,
    MotionProperties,
    Origin,
    Part,
    Sphere,
    TestContext,
    TestReport,
    mesh_from_cadquery,
)

__modular__ = True


# --------------------------------------------------------------------------- #
# Slot vocabularies
# --------------------------------------------------------------------------- #
Mount = Literal[
    "press_fit",
    "bolt_flange",
    "threaded_stud",
    "side_bracket",
    "machined_square_base",
]
MOUNTS: tuple[Mount, ...] = (
    "press_fit",
    "bolt_flange",
    "threaded_stud",
    "side_bracket",
    "machined_square_base",
)

BodyForm = Literal["stepped_round_cylinder", "hex_prism", "shallow_wide_cup"]
BODY_FORMS: tuple[BodyForm, ...] = (
    "stepped_round_cylinder",
    "hex_prism",
    "shallow_wide_cup",
)

Preload = Literal["spring_prismatic", "rigid_fixed_seat"]
PRELOADS: tuple[Preload, ...] = ("spring_prismatic", "rigid_fixed_seat")

Orientation = Literal["ball_up", "ball_down"]
ORIENTATIONS: tuple[Orientation, ...] = ("ball_up", "ball_down")

PaletteStyle = Literal[
    "satin_steel",
    "polished_steel",
    "bearing_steel",
    "dark_steel",
    "zinc",
    "stainless",
]
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "satin_steel",
    "polished_steel",
    "bearing_steel",
    "dark_steel",
    "zinc",
    "stainless",
)

# rgba lifted / extended from the origin record materials (L114-125):
#   satin_steel .60/.62/.66, polished_steel .82/.84/.88,
#   bearing_steel .70/.73/.79, dark_steel .24/.27/.31.
# keys: body / retainer / spring / carrier / load_ball / support / core
PALETTES: dict[str, dict[str, tuple[float, float, float, float]]] = {
    "satin_steel": {
        "body": (0.60, 0.62, 0.66, 1.0),
        "retainer": (0.82, 0.84, 0.88, 1.0),
        "spring": (0.24, 0.27, 0.31, 1.0),
        "carrier": (0.30, 0.33, 0.37, 1.0),
        "load_ball": (0.82, 0.84, 0.88, 1.0),
        "support": (0.70, 0.73, 0.79, 1.0),
        "core": (0.70, 0.73, 0.79, 1.0),
    },
    "polished_steel": {
        "body": (0.80, 0.82, 0.86, 1.0),
        "retainer": (0.88, 0.90, 0.93, 1.0),
        "spring": (0.30, 0.33, 0.37, 1.0),
        "carrier": (0.42, 0.45, 0.50, 1.0),
        "load_ball": (0.90, 0.92, 0.95, 1.0),
        "support": (0.78, 0.81, 0.86, 1.0),
        "core": (0.72, 0.75, 0.80, 1.0),
    },
    "bearing_steel": {
        "body": (0.66, 0.69, 0.74, 1.0),
        "retainer": (0.78, 0.81, 0.86, 1.0),
        "spring": (0.26, 0.29, 0.33, 1.0),
        "carrier": (0.34, 0.37, 0.42, 1.0),
        "load_ball": (0.74, 0.77, 0.83, 1.0),
        "support": (0.70, 0.73, 0.79, 1.0),
        "core": (0.68, 0.71, 0.77, 1.0),
    },
    "dark_steel": {
        "body": (0.26, 0.28, 0.32, 1.0),
        "retainer": (0.44, 0.47, 0.52, 1.0),
        "spring": (0.14, 0.15, 0.18, 1.0),
        "carrier": (0.20, 0.22, 0.26, 1.0),
        "load_ball": (0.58, 0.61, 0.66, 1.0),
        "support": (0.50, 0.53, 0.58, 1.0),
        "core": (0.46, 0.49, 0.54, 1.0),
    },
    "zinc": {
        "body": (0.72, 0.74, 0.72, 1.0),
        "retainer": (0.84, 0.86, 0.84, 1.0),
        "spring": (0.34, 0.36, 0.35, 1.0),
        "carrier": (0.48, 0.50, 0.49, 1.0),
        "load_ball": (0.86, 0.88, 0.86, 1.0),
        "support": (0.76, 0.78, 0.76, 1.0),
        "core": (0.72, 0.74, 0.72, 1.0),
    },
    "stainless": {
        "body": (0.70, 0.72, 0.75, 1.0),
        "retainer": (0.86, 0.88, 0.90, 1.0),
        "spring": (0.28, 0.30, 0.34, 1.0),
        "carrier": (0.40, 0.43, 0.47, 1.0),
        "load_ball": (0.88, 0.90, 0.92, 1.0),
        "support": (0.80, 0.82, 0.85, 1.0),
        "core": (0.74, 0.77, 0.81, 1.0),
    },
}

# Origin record nominal load-ball radius (dia 25mm). Radial geometry follows the
# ball via sr = ball_radius / NOMINAL_BALL_R so the moving stack always fits.
NOMINAL_BALL_R = 0.0125
_HEX_FACTOR = 2.0 / math.sqrt(3.0)  # across-flats -> circumscribed-circle dia
_BOLT_COUNTS: tuple[int, ...] = (3, 4, 6)


# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class PictureX0611BallTransferUnitWithSpringLoadedBallConfig:
    mount: Mount | None = None
    body_form: BodyForm | None = None
    preload: Preload | None = None
    orientation: Orientation | None = None
    palette_style: PaletteStyle = "satin_steel"
    support_ball_count: int = 8
    n_bolt: int = 4
    ball_radius: float = 0.0125
    body_scale: float = 1.0
    travel: float = 0.003


@dataclass(frozen=True)
class ResolvedPictureX0611BallTransferUnitWithSpringLoadedBallConfig:
    mount: Mount
    body_form: BodyForm
    preload: Preload
    orientation: Orientation
    palette_style: PaletteStyle
    support_ball_count: int
    n_bolt: int
    ball_radius: float
    body_scale: float
    travel: float
    # derived
    sr: float
    zf: float
    heights: dict[str, float]
    pitch: float
    support_radius: float
    palette: dict[str, tuple[float, float, float, float]]


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(v)))


def _stack_heights(body_form: BodyForm) -> dict[str, float]:
    """Single-source (Contract 3c) canonical ball-up stack z-layout + radii.

    All values in the ``sr = 1`` frame; the caller multiplies lengths by ``sr``
    (radial girth additionally by ``body_scale`` where noted). Derived from the
    origin record (tall) and var_shallow_wide_cup (shallow).
    """
    if body_form == "shallow_wide_cup":
        # var_shallow_wide_cup: low-profile wide flanged cup. Deepened vs the
        # raw source so a 25mm ball has real spring travel below it without
        # driving the cup/ball into the floor web.
        return {
            "ball_center_z": 0.019,
            "flange_top": 0.023,
            "flange_bot": 0.018,
            "body_bot": 0.0,
            "body_top": 0.018,
            "chamber_bot": 0.002,
            "chamber_top": 0.025,
            "spring_bottom": 0.002,
            "spring_len": 0.003,
            "r_body": 0.024,
            "r_flange": 0.038,
            "r_bore": 0.017,
            "r_retainer": 0.024,
            "cavity_r": 0.0129,
            "race_z": -0.009,
            "shoulder": 0.0,  # no distinct shoulder
        }
    # tall stepped/hex: origin record layout.
    return {
        "ball_center_z": 0.053,
        "flange_top": 0.056,
        "flange_bot": 0.044,
        "body_bot": 0.0,
        "body_top": 0.044,
        "shoulder_bot": 0.0425,
        "shoulder_top": 0.046,
        "chamber_bot": 0.008,
        "chamber_top": 0.058,
        "spring_bottom": 0.008,
        "spring_len": 0.014,
        "r_body": 0.020,
        "r_shoulder": 0.023,
        "r_flange": 0.028,
        "r_bore": 0.017,
        "r_retainer": 0.026,
        "cavity_r": 0.0129,
        "race_z": -0.009,
        "shoulder": 1.0,
    }


def config_from_seed(
    seed: int,
) -> PictureX0611BallTransferUnitWithSpringLoadedBallConfig:
    rng = random.Random(seed)
    mount = rng.choice(MOUNTS)
    return PictureX0611BallTransferUnitWithSpringLoadedBallConfig(
        mount=mount,
        body_form=rng.choice(BODY_FORMS),
        preload=rng.choice(PRELOADS),
        orientation=rng.choice(ORIENTATIONS),
        palette_style=rng.choice(PALETTE_STYLES),
        support_ball_count=rng.randint(6, 20),
        n_bolt=rng.choice(_BOLT_COUNTS) if mount == "bolt_flange" else 4,
        ball_radius=round(rng.uniform(0.0110, 0.0135), 5),
        body_scale=round(rng.uniform(0.90, 1.18), 4),
        travel=round(rng.uniform(0.0022, 0.0038), 5),
    )


def resolve_config(
    config: PictureX0611BallTransferUnitWithSpringLoadedBallConfig,
) -> ResolvedPictureX0611BallTransferUnitWithSpringLoadedBallConfig:
    mount = config.mount or "press_fit"
    body_form = config.body_form or "stepped_round_cylinder"
    preload = config.preload or "spring_prismatic"
    orientation = config.orientation or "ball_up"
    palette_style = config.palette_style or "satin_steel"

    for value, pool, label in (
        (mount, MOUNTS, "mount"),
        (body_form, BODY_FORMS, "body_form"),
        (preload, PRELOADS, "preload"),
        (orientation, ORIENTATIONS, "orientation"),
        (palette_style, PALETTE_STYLES, "palette_style"),
    ):
        if value not in pool:
            raise ValueError(f"Unsupported {label}: {value!r}")

    n = int(_clamp(config.support_ball_count, 6, 20))
    ball_radius = _clamp(config.ball_radius, 0.0105, 0.0135)
    sr = ball_radius / NOMINAL_BALL_R
    body_scale = _clamp(config.body_scale, 0.88, 1.20)
    zf = 1.0 if orientation == "ball_up" else -1.0

    heights = _stack_heights(body_form)

    # Support-ball ring (single radial ring in the lower race). Pitch chosen so
    # the balls kiss the load ball and embed in the cup; radius shrinks for a
    # dense ring so the ring never self-overlaps (equation constraint §7).
    pitch = 0.0105 * sr
    max_r_no_selfoverlap = 0.9 * pitch * math.sin(math.pi / n)
    support_radius = min(0.0018 * sr, max_r_no_selfoverlap)

    # Spring travel is bounded by the real clearance below the moving stack
    # (Contract 3e): the ball, cup and support balls must not descend into the
    # housing floor web. Binding on the shallow cup; slack on the tall body.
    floor = heights["chamber_bot"] * sr
    ball_bottom = heights["ball_center_z"] * sr - ball_radius
    cup_bottom = (heights["ball_center_z"] - 0.0137) * sr
    support_bottom = (heights["ball_center_z"] - 0.009) * sr - support_radius
    travel_avail = min(ball_bottom, cup_bottom, support_bottom) - floor - 0.0006
    travel = _clamp(config.travel, 0.0020, 0.0040)
    travel = min(travel, max(0.0008, travel_avail))

    n_bolt = int(config.n_bolt) if mount == "bolt_flange" else 4
    if n_bolt not in _BOLT_COUNTS:
        n_bolt = 4

    return ResolvedPictureX0611BallTransferUnitWithSpringLoadedBallConfig(
        mount=mount,
        body_form=body_form,
        preload=preload,
        orientation=orientation,
        palette_style=palette_style,
        support_ball_count=n,
        n_bolt=n_bolt,
        ball_radius=ball_radius,
        body_scale=body_scale,
        travel=travel,
        sr=sr,
        zf=zf,
        heights=heights,
        pitch=pitch,
        support_radius=support_radius,
        palette=dict(PALETTES[palette_style]),
    )


# --------------------------------------------------------------------------- #
# Orientation helpers — R(x,y,z) = (x, zf*y, zf*z), zf in {+1, -1}
# --------------------------------------------------------------------------- #
def _r_pt(x: float, y: float, z: float, zf: float) -> tuple[float, float, float]:
    return (x, zf * y, zf * z)


def _r_ax(ax: float, ay: float, az: float, zf: float) -> tuple[float, float, float]:
    return (ax, zf * ay, zf * az)


def _orient_solid(wp: cq.Workplane, zf: float) -> cq.Workplane:
    if zf < 0:
        return wp.rotate((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), 180.0)
    return wp


# --------------------------------------------------------------------------- #
# Housing solid (Slots A mount x B body_form), canonical ball-up
# --------------------------------------------------------------------------- #
def _housing_solid(
    r: ResolvedPictureX0611BallTransferUnitWithSpringLoadedBallConfig,
) -> cq.Workplane:
    h = r.heights
    sr = r.sr
    bs = r.body_scale

    # ---- B: main upper body / cup ----
    if r.body_form == "hex_prism":
        lower_af = 0.044 * sr * bs
        shoulder_af = 0.050 * sr * bs
        lower = (
            cq.Workplane("XY")
            .polygon(6, lower_af * _HEX_FACTOR)
            .extrude(h["body_top"] * sr)
        )
        shoulder = (
            cq.Workplane("XY")
            .workplane(offset=h["shoulder_bot"] * sr)
            .polygon(6, shoulder_af * _HEX_FACTOR)
            .extrude((h["shoulder_top"] - h["shoulder_bot"]) * sr)
        )
        flange = (
            cq.Workplane("XY")
            .workplane(offset=h["flange_bot"] * sr)
            .circle(h["r_retainer"] * sr)
            .extrude((h["flange_top"] - h["flange_bot"]) * sr)
        )
        body = lower.union(shoulder).union(flange)
    elif r.body_form == "shallow_wide_cup":
        cup = cq.Workplane("XY").circle(h["r_body"] * sr * bs).extrude(h["body_top"] * sr)
        flange = (
            cq.Workplane("XY")
            .workplane(offset=h["flange_bot"] * sr)
            .circle(h["r_flange"] * sr)
            .extrude((h["flange_top"] - h["flange_bot"]) * sr)
        )
        body = cup.union(flange)
    else:  # stepped_round_cylinder
        lower = cq.Workplane("XY").circle(h["r_body"] * sr * bs).extrude(h["body_top"] * sr)
        shoulder = (
            cq.Workplane("XY")
            .workplane(offset=h["shoulder_bot"] * sr)
            .circle(h["r_shoulder"] * sr * bs)
            .extrude((h["shoulder_top"] - h["shoulder_bot"]) * sr)
        )
        flange = (
            cq.Workplane("XY")
            .workplane(offset=h["flange_bot"] * sr)
            .circle(h["r_flange"] * sr)
            .extrude((h["flange_top"] - h["flange_bot"]) * sr)
        )
        body = lower.union(shoulder).union(flange)

    # ---- A: mounting interface, added below z=0 so the stack layout is fixed ----
    if r.mount == "bolt_flange":
        plate_t = 0.005 * sr
        plate_r = 0.038 * sr
        plate = (
            cq.Workplane("XY")
            .workplane(offset=-plate_t)
            .circle(plate_r)
            .extrude(plate_t)
        )
        body = body.union(plate)
        bolt_circle = 0.030 * sr
        for i in range(r.n_bolt):
            ang = 2.0 * math.pi * i / r.n_bolt
            bx = bolt_circle * math.cos(ang)
            by = bolt_circle * math.sin(ang)
            hole = (
                cq.Workplane("XY")
                .workplane(offset=-plate_t - 0.001 * sr)
                .center(bx, by)
                .circle(0.0025 * sr)
                .extrude(plate_t + 0.002 * sr)
            )
            body = body.cut(hole)
    elif r.mount == "machined_square_base":
        plate_t = 0.008 * sr
        half = 0.038 * sr
        plate = (
            cq.Workplane("XY")
            .workplane(offset=-plate_t)
            .rect(2 * half, 2 * half)
            .extrude(plate_t)
        )
        body = body.union(plate)
        off = 0.030 * sr
        for sx in (-1, 1):
            for sy in (-1, 1):
                hole = (
                    cq.Workplane("XY")
                    .workplane(offset=-plate_t - 0.001 * sr)
                    .center(sx * off, sy * off)
                    .circle(0.0035 * sr)
                    .extrude(plate_t + 0.002 * sr)
                )
                body = body.cut(hole)
    elif r.mount == "threaded_stud":
        collar = (
            cq.Workplane("XY")
            .workplane(offset=-0.005 * sr)
            .polygon(6, 0.022 * sr)
            .extrude(0.005 * sr)
        )
        shank = (
            cq.Workplane("XY")
            .workplane(offset=-0.028 * sr)
            .circle(0.005 * sr)
            .extrude(0.023 * sr)
        )
        body = body.union(collar).union(shank)
    elif r.mount == "side_bracket":
        body_r = h["r_body"] * sr * bs
        tab_w = 0.016 * sr
        tab_x = 0.018 * sr
        tab_t = 0.004 * sr
        tab_z = 0.016 * sr
        overlap = 0.003 * sr
        for sign in (1, -1):
            tab_cx = sign * (body_r - overlap + tab_x / 2.0)
            tab = (
                cq.Workplane("XY")
                .workplane(offset=tab_z)
                .center(tab_cx, 0.0)
                .rect(tab_x, tab_w)
                .extrude(tab_t)
            )
            bolt_cx = sign * (body_r + tab_x - overlap - 0.005 * sr)
            hole = (
                cq.Workplane("XY")
                .workplane(offset=tab_z - 0.001 * sr)
                .center(bolt_cx, 0.0)
                .circle(0.0025 * sr)
                .extrude(tab_t + 0.002 * sr)
            )
            tab = tab.cut(hole)
            body = body.union(tab)
    # press_fit: nothing added.

    # ---- internal carrier chamber: wide bore for the carrier/cup, then a
    # narrower top aperture lip so the retainer's on-axis FIXED joint origin
    # stays within 15mm of real housing geometry (aperture < ball dia keeps the
    # ball captive too). ----
    cbot = h["chamber_bot"] * sr
    ctop = h["chamber_top"] * sr
    lip_bot = (h["ball_center_z"] + 0.001) * sr
    r_ap = r.ball_radius + 0.0009  # clears the ball crown, < 15mm always
    main_bore = (
        cq.Workplane("XY")
        .workplane(offset=cbot)
        .circle(h["r_bore"] * sr)
        .extrude(lip_bot - cbot)
    )
    aperture = (
        cq.Workplane("XY")
        .workplane(offset=lip_bot)
        .circle(r_ap)
        .extrude(ctop - lip_bot)
    )
    body = body.cut(main_bore).cut(aperture)
    return _orient_solid(body, r.zf)


def _retainer_solid(
    r: ResolvedPictureX0611BallTransferUnitWithSpringLoadedBallConfig,
) -> cq.Workplane:
    h = r.heights
    sr = r.sr
    ring = cq.Workplane("XY").circle(h["r_retainer"] * sr).extrude(0.004 * sr)
    cavity = (
        cq.Workplane("XY")
        .workplane(offset=-0.003 * sr)
        .sphere(h["cavity_r"] * sr)
    )
    return _orient_solid(ring.cut(cavity), r.zf)


def _carrier_solid(
    r: ResolvedPictureX0611BallTransferUnitWithSpringLoadedBallConfig,
) -> cq.Workplane:
    """Lower spherical race cup + central post, in carrier frame (origin = ball
    center). Post reaches the spring top (spring preload) or the housing floor
    (rigid seat). Unifies origin (L63-87), shallow (L62-90) and rigid (L62-87).
    """
    h = r.heights
    sr = r.sr
    outer = cq.Workplane("XY").sphere(0.0138 * sr)
    inner = cq.Workplane("XY").sphere(h["cavity_r"] * sr)
    shell = outer.cut(inner)
    lower_zone = (
        cq.Workplane("XY")
        .workplane(offset=-0.0081 * sr)
        .box(0.040 * sr, 0.040 * sr, 0.0112 * sr)
    )
    cup = shell.intersect(lower_zone)

    carrier_z = h["ball_center_z"]
    bowl_bottom_cf = -0.0125 * sr  # in carrier frame
    if r.preload == "rigid_fixed_seat":
        target_world = h["chamber_bot"]  # grounded on the floor web
        post_r = 0.006 * sr
    else:
        target_world = h["spring_bottom"] + h["spring_len"]  # rest on spring top
        post_r = 0.0048 * sr
    target_cf = (target_world - carrier_z) * sr
    post_len = bowl_bottom_cf - target_cf
    if post_len > 0:
        post = (
            cq.Workplane("XY")
            .workplane(offset=target_cf)
            .circle(post_r)
            .extrude(post_len)
        )
        cup = cup.union(post)
    return _orient_solid(cup, r.zf)


# --------------------------------------------------------------------------- #
# Assembly
# --------------------------------------------------------------------------- #
def build_pictureX_0611_ball_transfer_unit_with_spring_loaded_ball(
    config: PictureX0611BallTransferUnitWithSpringLoadedBallConfig,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    h = r.heights
    sr = r.sr
    zf = r.zf

    model = ArticulatedObject(
        name="spring_loaded_ball_transfer_unit",
        assets=assets,
        meta={
            "category": "0611/ball_transfer_unit_with_spring_loaded_ball",
            "source_traceability": "pictureX/0611/ball_transfer_unit_with_spring_loaded_ball/001.png",
        },
    )
    for key, rgba in r.palette.items():
        model.material(key, rgba=rgba)

    tol = dict(tolerance=0.00025, angular_tolerance=0.06)

    # ---- housing (root) ----
    housing = model.part("housing", meta={"role": "root support + mounting body"})
    housing.visual(
        mesh_from_cadquery(_housing_solid(r), "stepped_housing", **tol),
        material="body",
        name="stepped_housing", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"polished_steel", "bearing_steel", "dark_steel", "zinc", "stainless"} else "metal.brushed_silver"),
    )

    # ---- retainer (FIXED, with MatingContract to the flange face) ----
    retainer = model.part("retainer", meta={"role": "pressed retaining cup"})
    retainer.visual(
        mesh_from_cadquery(_retainer_solid(r), "retaining_cup", **tol),
        material="retainer",
        name="retaining_cup", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"polished_steel", "bearing_steel", "dark_steel", "zinc", "stainless"} else "metal.brushed_silver"),
    )
    house_top_side = "positive_z" if zf > 0 else "negative_z"
    ret_seat_side = "negative_z" if zf > 0 else "positive_z"
    model.articulation(
        "housing_to_retainer",
        ArticulationType.FIXED,
        parent=housing,
        child=retainer,
        origin=Origin(xyz=_r_pt(0.0, 0.0, h["flange_top"] * sr, zf)),
        mating=MatingContract(
            parent_face_geometry="stepped_housing",
            parent_face_side=house_top_side,
            child_face_geometry="retaining_cup",
            child_face_side=ret_seat_side,
            contact_tol=0.0015,
        ),
    )

    # ---- compression spring (only for spring preload) ----
    if r.preload == "spring_prismatic":
        spring = model.part("compression_spring", meta={"role": "axial preload"})
        spring.visual(
            Cylinder(radius=0.0035 * sr, length=h["spring_len"] * sr),
            origin=Origin(xyz=_r_pt(0.0, 0.0, h["spring_len"] * sr / 2.0, zf)),
            material="spring",
            name="spring_envelope", material_class_id="metal.blackened_gunmetal",
        )
        model.articulation(
            "housing_to_spring",
            ArticulationType.FIXED,
            parent=housing,
            child=spring,
            origin=Origin(xyz=_r_pt(0.0, 0.0, h["spring_bottom"] * sr, zf)),
        )

    # ---- spring carrier (PRISMATIC preload | FIXED rigid seat) ----
    carrier = model.part("spring_carrier", meta={"role": "lower race carrier"})
    carrier.visual(
        mesh_from_cadquery(_carrier_solid(r), "spring_plunger", **tol),
        material="carrier",
        name="spring_plunger", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"polished_steel", "bearing_steel", "dark_steel", "zinc", "stainless"} else "metal.brushed_silver"),
    )
    carrier_origin = Origin(xyz=_r_pt(0.0, 0.0, h["ball_center_z"] * sr, zf))
    if r.preload == "spring_prismatic":
        travel = r.travel * sr
        model.articulation(
            "housing_to_carrier",
            ArticulationType.PRISMATIC,
            parent=housing,
            child=carrier,
            origin=carrier_origin,
            axis=_r_ax(0.0, 0.0, 1.0, zf),
            motion_limits=MotionLimits(
                effort=900.0, velocity=0.05, lower=-travel, upper=0.0
            ),
            motion_properties=MotionProperties(damping=18.0, friction=4.0),
        )
    else:
        model.articulation(
            "housing_to_carrier",
            ArticulationType.FIXED,
            parent=housing,
            child=carrier,
            origin=carrier_origin,
        )

    # ---- rolling core (CONTINUOUS x) + load ball (CONTINUOUS y) ----
    roll_frame = model.part("roll_frame", meta={"role": "hidden rolling core"})
    roll_frame.visual(Sphere(radius=0.0020 * sr), material="core", name="bearing_core", material_class_id="metal.steel_bare")
    model.articulation(
        "carrier_to_roll_frame",
        ArticulationType.CONTINUOUS,
        parent=carrier,
        child=roll_frame,
        origin=Origin(),
        axis=_r_ax(1.0, 0.0, 0.0, zf),
        motion_limits=MotionLimits(effort=120.0, velocity=12.0),
        motion_properties=MotionProperties(damping=0.02, friction=0.01),
    )

    load_ball = model.part("load_ball", meta={"role": "load-bearing transfer ball"})
    load_ball.visual(
        Sphere(radius=r.ball_radius), material="load_ball", name="load_ball", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"polished_steel", "bearing_steel", "dark_steel", "zinc", "stainless"} else "metal.brushed_silver")
    )
    model.articulation(
        "roll_frame_to_ball",
        ArticulationType.CONTINUOUS,
        parent=roll_frame,
        child=load_ball,
        origin=Origin(),
        axis=_r_ax(0.0, 1.0, 0.0, zf),
        motion_limits=MotionLimits(effort=120.0, velocity=12.0),
        motion_properties=MotionProperties(damping=0.015, friction=0.008),
    )

    # ---- support-ball nest (Slot E multiplicity), FIXED to the carrier ----
    for i in range(r.support_ball_count):
        ang = 2.0 * math.pi * i / r.support_ball_count
        bx = r.pitch * math.cos(ang)
        by = r.pitch * math.sin(ang)
        bz = h["race_z"] * sr
        ball_part = model.part(
            f"support_ball_{i:02d}", meta={"role": "captive support ball"}
        )
        ball_part.visual(
            Sphere(radius=r.support_radius),
            material="support",
            name=f"support_ball_{i:02d}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"polished_steel", "bearing_steel", "dark_steel", "zinc", "stainless"} else "metal.brushed_silver"),
        )
        # support-ball local offset lives in the carrier frame; apply R for
        # orientation so the whole ring rotates with the assembly.
        model.articulation(
            f"carrier_to_support_{i:02d}",
            ArticulationType.FIXED,
            parent=carrier,
            child=ball_part,
            origin=Origin(xyz=_r_pt(bx, by, bz, zf)),
        )

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_pictureX_0611_ball_transfer_unit_with_spring_loaded_ball(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_pictureX_0611_ball_transfer_unit_with_spring_loaded_ball(
        config_from_seed(seed), assets=assets
    )


# --------------------------------------------------------------------------- #
# Slot choices
# --------------------------------------------------------------------------- #
def slot_choices_for_config(
    r: ResolvedPictureX0611BallTransferUnitWithSpringLoadedBallConfig,
) -> list[tuple[str, str]]:
    choices = [
        ("mount", r.mount),
        ("body_form", r.body_form),
        ("preload", r.preload),
        ("orientation", r.orientation),
        ("support_ball_count", str(r.support_ball_count)),
    ]
    if r.mount == "bolt_flange":
        choices.append(("n_bolt", str(r.n_bolt)))
    return choices


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    return slot_choices_for_config(resolve_config(config_from_seed(seed)))


# --------------------------------------------------------------------------- #
# Tests
# --------------------------------------------------------------------------- #
def run_pictureX_0611_ball_transfer_unit_with_spring_loaded_ball_tests(
    object_model: ArticulatedObject,
    config: PictureX0611BallTransferUnitWithSpringLoadedBallConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)

    housing = object_model.get_part("housing")
    retainer = object_model.get_part("retainer")
    carrier = object_model.get_part("spring_carrier")
    roll_frame = object_model.get_part("roll_frame")
    load_ball = object_model.get_part("load_ball")
    part_names = {p.name for p in object_model.parts}

    roll_x = object_model.get_articulation("carrier_to_roll_frame")
    roll_y = object_model.get_articulation("roll_frame_to_ball")
    carrier_joint = object_model.get_articulation("housing_to_carrier")

    # ---- captured-geometry allowances (element-scoped, honored at every pose) ----
    ctx.allow_overlap(
        roll_frame, load_ball,
        elem_a="bearing_core", elem_b="load_ball",
        reason="hidden orthogonal rolling core enclosed by the load ball (2nd scalar rolling frame)",
    )
    ctx.allow_overlap(
        load_ball, carrier,
        elem_a="load_ball", elem_b="spring_plunger",
        reason="load ball seated in the concave lower bearing race (captured fit)",
    )
    if "compression_spring" in part_names:
        spring = object_model.get_part("compression_spring")
        ctx.allow_overlap(
            spring, housing,
            elem_a="spring_envelope", elem_b="stepped_housing",
            reason="hidden spring envelope seated with a tiny embed at the closed housing floor",
        )
        ctx.allow_overlap(
            carrier, spring,
            elem_a="spring_plunger", elem_b="spring_envelope",
            reason="compliant spring proxy shortens into the plunger during compression",
        )
    # The lower race cup / seat post seats into the housing floor web (captured
    # seat); a small local embed is intentional for both preload variants.
    ctx.allow_overlap(
        carrier, housing,
        elem_a="spring_plunger", elem_b="stepped_housing",
        reason="lower race carrier seated into the housing floor web (captured seat)",
    )

    support_parts: list[Part] = []
    for i in range(r.support_ball_count):
        pname = f"support_ball_{i:02d}"
        bp = object_model.get_part(pname)
        support_parts.append(bp)
        ctx.allow_overlap(
            bp, carrier,
            elem_a=pname, elem_b="spring_plunger",
            reason=f"support ball {i:02d} seated in the concave lower race",
        )
        ctx.allow_overlap(
            bp, load_ball,
            elem_a=pname, elem_b="load_ball",
            reason=f"support ball {i:02d} is the rolling bed the load ball rests on",
        )

    # ---- identity: two real rolling joints, ball center held captive ----
    ctx.check(
        "load ball has two CONTINUOUS rolling joints",
        roll_x.articulation_type == ArticulationType.CONTINUOUS
        and roll_y.articulation_type == ArticulationType.CONTINUOUS,
        details=f"roll_x={roll_x.articulation_type}, roll_y={roll_y.articulation_type}",
    )
    center_before = ctx.part_world_position(load_ball)
    with ctx.pose({roll_x: 0.8, roll_y: -0.7}):
        center_after = ctx.part_world_position(load_ball)
    ctx.check(
        "two-axis rolling keeps ball center captive",
        center_before is not None
        and center_after is not None
        and all(
            math.isclose(a, b, rel_tol=0.0, abs_tol=1e-7)
            for a, b in zip(center_before, center_after)
        ),
        details=f"before={center_before}, after={center_after}",
    )

    # ---- preload mechanism consistency ----
    if r.preload == "spring_prismatic":
        ctx.check(
            "spring preload: housing_to_carrier is PRISMATIC + spring present",
            carrier_joint.articulation_type == ArticulationType.PRISMATIC
            and "compression_spring" in part_names,
            details=f"joint={carrier_joint.articulation_type}, parts={sorted(part_names)}",
        )
        # targeted compression pose: ball crown retracts toward the housing.
        crown_before = ctx.part_world_aabb(load_ball)
        with ctx.pose({carrier_joint: carrier_joint.motion_limits.lower}):
            crown_after = ctx.part_world_aabb(load_ball)
        moved = (
            crown_before is not None
            and crown_after is not None
            and abs(
                (crown_before[1][2] - crown_before[0][2])
                - (crown_after[1][2] - crown_after[0][2])
            )
            < 1e-6
            and any(
                abs(crown_before[k][2] - crown_after[k][2]) > 0.0015
                for k in (0, 1)
            )
        )
        ctx.check(
            "spring compression displaces the load ball axially",
            moved,
            details=f"before={crown_before}, after={crown_after}",
        )
    else:
        ctx.check(
            "rigid seat: housing_to_carrier is FIXED + no spring part",
            carrier_joint.articulation_type == ArticulationType.FIXED
            and "compression_spring" not in part_names,
            details=f"joint={carrier_joint.articulation_type}, parts={sorted(part_names)}",
        )

    # ---- retainer captures the ball crown (ball stays radially inside) ----
    ctx.expect_within(
        load_ball, retainer,
        axes="xy", inner_elem="load_ball", outer_elem="retaining_cup",
        margin=0.0, name="load ball stays radially inside the retaining cup",
    )

    # ---- multiplicity: support-ball ring count matches N ----
    ctx.check(
        f"support-ball ring has exactly N={r.support_ball_count} balls",
        len(support_parts) == r.support_ball_count
        and all(
            f"support_ball_{i:02d}" in part_names for i in range(r.support_ball_count)
        ),
        details=f"found {len(support_parts)}",
    )
    ctx.check(
        "support balls are FIXED to the carrier",
        all(
            object_model.get_articulation(f"carrier_to_support_{i:02d}").articulation_type
            == ArticulationType.FIXED
            for i in range(r.support_ball_count)
        ),
        details="captive bed",
    )

    # ---- palette / material assignment ----
    material_names = {m.name for m in object_model.materials}
    ctx.check(
        "steel palette materials assigned",
        {"body", "retainer", "load_ball", "support"} <= material_names,
        details=f"materials={sorted(material_names)}",
    )

    # ---- Rule 5: no 穿模 across the full sampled motion envelope ----
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=96, ignore_fixed=True)

    return ctx.report()


__all__ = [
    "__modular__",
    "PictureX0611BallTransferUnitWithSpringLoadedBallConfig",
    "ResolvedPictureX0611BallTransferUnitWithSpringLoadedBallConfig",
    "config_from_seed",
    "resolve_config",
    "build_pictureX_0611_ball_transfer_unit_with_spring_loaded_ball",
    "build_seeded_pictureX_0611_ball_transfer_unit_with_spring_loaded_ball",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "run_pictureX_0611_ball_transfer_unit_with_spring_loaded_ball_tests",
]
