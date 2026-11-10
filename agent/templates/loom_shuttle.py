# SPDX-License-Identifier: Apache-2.0

"""Loom shuttle — modular procedural template.

An elongated wooden shuttle body (Slot A ``body_form``, the ③ Primary-Form-Family
slot) carries a spinning weft package (Slot B ``bobbin_mechanism``) and an optional
underside race-roller bogie (Slot C ``underside``, with an N multiplicity axis).

Pattern = ``mixed``: a single grounded ``body`` root; the weft mechanism mounts on
the body's shared *axle interface* (``axle_z`` / ``±bearing_x`` / cavity floor), and
the rollers are parallel CONTINUOUS children of the body keel.

* Slot A ``body_form`` (3): boat_hollow / flat_plank / ski_upswept — each a carved
  cadquery hull exposing the same axle interface, so any mechanism mounts on any form.
* Slot B ``bobbin_mechanism`` (3): through_axle (1 REVOLUTE +X spin) /
  spindle_arm (REVOLUTE +Y loading hinge + REVOLUTE +X pirn spin) /
  end_delivery (fixed cantilever LatheGeometry pirn, 1 REVOLUTE +X spin + nose gate).
* Slot C ``underside`` (2): plain_race / roller_bogie (N in [2,6] CONTINUOUS +Y rollers).

Sources (all 8 read): origins ``..._c079a660`` (boat 002) + ``..._79eba550`` (boat 001),
forks skeleton_flat_open / form_ski / mechanism_spindle_arm / mechanism_end_delivery /
mechanism_roller / n_rollers4. Spec:
``articraft_template_authoring/specs_modular_v1/loom_shuttle.md``.

The bobbin/pirn journals, the arm pivot pin, the pirn-on-spindle fit, and the
roller-on-axle bearings are captured pins (no clean axis-aligned face pair) — ``mating``
omitted, grandfathered, and guarded by element-scoped ``allow_overlap`` in run_tests
(mirrors cable_reel and the source records).
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Literal

import cadquery as cq

from sdk import (
    AppearanceOnlySpec,
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    ConeGeometry,
    Cylinder,
    LatheGeometry,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    TorusGeometry,
    mesh_from_cadquery,
    mesh_from_geometry,
)

__modular__ = True

TAU = 2.0 * math.pi
_CYL_TO_X = (0.0, math.pi / 2.0, 0.0)  # local Z cylinder -> along world +X
_CYL_TO_Y = (math.pi / 2.0, 0.0, 0.0)  # local Z cylinder -> along world +Y


# --------------------------------------------------------------------------- #
# Slot enums                                                                   #
# --------------------------------------------------------------------------- #
BodyForm = Literal["boat_hollow", "flat_plank", "ski_upswept"]
BobbinMechanism = Literal["through_axle", "spindle_arm", "end_delivery"]
Underside = Literal["plain_race", "roller_bogie"]
PaletteStyle = Literal[
    "honey_oiled",
    "dark_walnut",
    "pale_pine",
    "oiled_brown",
    "weathered_gray",
]

BODY_FORMS: tuple[BodyForm, ...] = ("boat_hollow", "flat_plank", "ski_upswept")
BOBBIN_MECHANISMS: tuple[BobbinMechanism, ...] = ("through_axle", "spindle_arm", "end_delivery")
UNDERSIDES: tuple[Underside, ...] = ("plain_race", "roller_bogie")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "honey_oiled",
    "dark_walnut",
    "pale_pine",
    "oiled_brown",
    "weathered_gray",
)

N_MIN, N_MAX = 2, 6
_N_VALUES: tuple[int, ...] = tuple(range(N_MIN, N_MAX + 1))
# Small-N common, tail rare (weight decays away from 2).
_N_WEIGHTS: tuple[float, ...] = tuple(1.0 / (1.0 + abs(n - 2)) for n in _N_VALUES)


# --------------------------------------------------------------------------- #
# Palettes (>=3 realistic colorways; every key drives a .visual material).     #
# --------------------------------------------------------------------------- #
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "honey_oiled": {
        "hull": (0.56, 0.34, 0.12, 1.0),
        "cavity": (0.14, 0.08, 0.04, 1.0),
        "grain": (0.24, 0.12, 0.04, 1.0),
        "metal": (0.55, 0.58, 0.56, 1.0),
        "eyelet": (0.015, 0.018, 0.017, 1.0),
        "yarn": (0.86, 0.78, 0.60, 1.0),
        "red": (0.85, 0.05, 0.03, 1.0),
        "bobbin_wood": (0.34, 0.17, 0.06, 1.0),
        "roller_steel": (0.72, 0.74, 0.76, 1.0),
    },
    "dark_walnut": {
        "hull": (0.30, 0.17, 0.08, 1.0),
        "cavity": (0.09, 0.05, 0.03, 1.0),
        "grain": (0.16, 0.09, 0.04, 1.0),
        "metal": (0.60, 0.62, 0.64, 1.0),
        "eyelet": (0.02, 0.02, 0.02, 1.0),
        "yarn": (0.80, 0.70, 0.48, 1.0),
        "red": (0.78, 0.10, 0.06, 1.0),
        "bobbin_wood": (0.24, 0.12, 0.05, 1.0),
        "roller_steel": (0.66, 0.68, 0.70, 1.0),
    },
    "pale_pine": {
        "hull": (0.72, 0.55, 0.30, 1.0),
        "cavity": (0.30, 0.20, 0.11, 1.0),
        "grain": (0.42, 0.28, 0.12, 1.0),
        "metal": (0.62, 0.64, 0.62, 1.0),
        "eyelet": (0.03, 0.03, 0.03, 1.0),
        "yarn": (0.93, 0.86, 0.66, 1.0),
        "red": (0.82, 0.18, 0.08, 1.0),
        "bobbin_wood": (0.55, 0.38, 0.18, 1.0),
        "roller_steel": (0.78, 0.80, 0.82, 1.0),
    },
    "oiled_brown": {
        "hull": (0.48, 0.26, 0.10, 1.0),
        "cavity": (0.12, 0.07, 0.03, 1.0),
        "grain": (0.22, 0.12, 0.05, 1.0),
        "metal": (0.70, 0.55, 0.24, 1.0),
        "eyelet": (0.015, 0.018, 0.017, 1.0),
        "yarn": (0.88, 0.80, 0.58, 1.0),
        "red": (0.86, 0.06, 0.04, 1.0),
        "bobbin_wood": (0.36, 0.19, 0.07, 1.0),
        "roller_steel": (0.70, 0.71, 0.72, 1.0),
    },
    "weathered_gray": {
        "hull": (0.52, 0.47, 0.40, 1.0),
        "cavity": (0.20, 0.18, 0.15, 1.0),
        "grain": (0.34, 0.30, 0.25, 1.0),
        "metal": (0.58, 0.60, 0.60, 1.0),
        "eyelet": (0.03, 0.03, 0.03, 1.0),
        "yarn": (0.82, 0.78, 0.68, 1.0),
        "red": (0.74, 0.16, 0.10, 1.0),
        "bobbin_wood": (0.40, 0.34, 0.26, 1.0),
        "roller_steel": (0.74, 0.75, 0.76, 1.0),
    },
}


def _material_class_id(
    surface: Literal[
        "hull",
        "cavity_wood",
        "bobbin_wood",
        "eyelet_metal",
        "hardware_metal",
        "roller_steel",
        "cotton_yarn",
        "red_thread",
    ],
) -> str:
    """Return the exact formal-library pool for a resolved material visual."""
    return {
        "hull": "wood.polished_varnished",
        "cavity_wood": "wood.rustic_weathered",
        "bobbin_wood": "wood.natural_generic",
        "eyelet_metal": "metal.blackened_gunmetal",
        "hardware_metal": "metal.generic_scratched",
        "roller_steel": "metal.stainless_matte",
        "cotton_yarn": "fabric.thread_yarn",
        "red_thread": "fabric.thread_yarn",
    }[surface]


# --------------------------------------------------------------------------- #
# Per-form nominal geometry (pre-scale). ``ls`` scales +X features; ``rs``     #
# scales bobbin radii. Everything the mechanisms/rollers need lands in the     #
# resolved axle interface (Contract 3c single-source).                         #
# --------------------------------------------------------------------------- #
_FORM_NOMINAL: dict[BodyForm, dict[str, float]] = {
    "boat_hollow": dict(
        length=0.36,
        half_width=0.028,
        top_z=0.034,
        cavity_floor_top=0.0049,
        bearing_x=0.105,
        keel_bottom=0.0,
    ),
    "flat_plank": dict(
        length=0.36,
        half_width=0.027,
        top_z=0.014,
        cavity_floor_top=0.0078,
        bearing_x=0.100,
        keel_bottom=0.0,
    ),
    "ski_upswept": dict(
        length=0.42,
        half_width=0.0195,
        top_z=0.024,
        cavity_floor_top=0.016,
        bearing_x=0.120,
        keel_bottom=0.0,
    ),
}

_FLANGE_R0 = 0.0142  # nominal flange radius (widest bobbin feature)
_CORE_R0 = 0.0061  # nominal axle-core radius
_THREAD_R0 = 0.0132  # nominal wound-thread radius
_AXLE_CLEAR = 0.0016  # flange-to-floor clearance margin
_ROLLER_R = 0.006  # roller wheel radius
_ROLLER_KEEL_GAP = 0.0015


# --------------------------------------------------------------------------- #
# Config                                                                       #
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class LoomShuttleConfig:
    body_form: BodyForm | None = None
    bobbin_mechanism: BobbinMechanism | None = None
    underside: Underside | None = None
    n_rollers: int | None = None
    palette_style: PaletteStyle = "honey_oiled"
    length_scale: float = 1.0
    bobbin_radius_scale: float = 1.0
    arm_open: float = 1.0
    name: str = "loom_shuttle"


@dataclass(frozen=True)
class ResolvedLoomShuttleConfig:
    body_form: BodyForm
    bobbin_mechanism: BobbinMechanism
    underside: Underside
    n: int
    palette_style: PaletteStyle
    ls: float
    rs: float
    arm_open: float
    name: str
    # derived axle interface
    length: float
    half_width: float
    top_z: float
    keel_bottom_z: float
    cavity_floor_top_z: float
    bearing_x: float
    axle_z: float
    flange_radius: float
    core_radius: float
    thread_radius: float
    core_length: float
    roller_radius: float
    roller_z: float


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(v)))


def _pick(value, choices):
    return value if value in choices else choices[0]


def config_from_seed(seed: int) -> LoomShuttleConfig:
    rng = random.Random(seed)
    return LoomShuttleConfig(
        body_form=rng.choice(BODY_FORMS),
        bobbin_mechanism=rng.choice(BOBBIN_MECHANISMS),
        underside=rng.choice(UNDERSIDES),
        n_rollers=rng.choices(_N_VALUES, weights=_N_WEIGHTS, k=1)[0],
        palette_style=rng.choice(PALETTE_STYLES),
        length_scale=round(rng.uniform(0.90, 1.15), 4),
        bobbin_radius_scale=round(rng.uniform(0.94, 1.06), 4),
        arm_open=round(rng.uniform(0.80, 1.15), 4),
        name=f"seeded_loom_shuttle_{seed}",
    )


def resolve_config(config: LoomShuttleConfig | None = None) -> ResolvedLoomShuttleConfig:
    cfg = config or LoomShuttleConfig()
    form = _pick(cfg.body_form, BODY_FORMS)
    ls = _clamp(cfg.length_scale, 0.90, 1.15)
    rs = _clamp(cfg.bobbin_radius_scale, 0.94, 1.06)
    n = int(cfg.n_rollers) if cfg.n_rollers is not None else N_MIN
    nom = _FORM_NOMINAL[form]

    flange_radius = _FLANGE_R0 * rs
    core_radius = _CORE_R0 * rs
    thread_radius = _THREAD_R0 * rs
    cavity_floor_top_z = float(nom["cavity_floor_top"])
    bearing_x = float(nom["bearing_x"]) * ls
    # Derived: axle high enough that the flange clears the cavity floor (Contract 3e).
    axle_z = cavity_floor_top_z + flange_radius + _AXLE_CLEAR
    core_length = 2.0 * bearing_x + 0.006
    keel_bottom_z = float(nom["keel_bottom"])
    # Derived: wheel crown hangs just below the keel with a small gap.
    roller_z = keel_bottom_z - _ROLLER_KEEL_GAP - _ROLLER_R

    return ResolvedLoomShuttleConfig(
        body_form=form,
        bobbin_mechanism=_pick(cfg.bobbin_mechanism, BOBBIN_MECHANISMS),
        underside=_pick(cfg.underside, UNDERSIDES),
        n=int(_clamp(n, N_MIN, N_MAX)),
        palette_style=_pick(cfg.palette_style, PALETTE_STYLES),
        ls=ls,
        rs=rs,
        arm_open=_clamp(cfg.arm_open, 0.70, 1.25),
        name=cfg.name or "loom_shuttle",
        length=float(nom["length"]) * ls,
        half_width=float(nom["half_width"]),
        top_z=float(nom["top_z"]),
        keel_bottom_z=keel_bottom_z,
        cavity_floor_top_z=cavity_floor_top_z,
        bearing_x=bearing_x,
        axle_z=axle_z,
        flange_radius=flange_radius,
        core_radius=core_radius,
        thread_radius=thread_radius,
        core_length=core_length,
        roller_radius=_ROLLER_R,
        roller_z=roller_z,
    )


def slot_choices_for_config(config) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedLoomShuttleConfig) else resolve_config(config)
    roller_n = f"n{r.n}" if r.underside == "roller_bogie" else "n0"
    return (
        ("body_form", r.body_form),
        ("bobbin_mechanism", r.bobbin_mechanism),
        ("underside", r.underside),
        ("roller_n", roller_n),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# --------------------------------------------------------------------------- #
# Cadquery hull meshes (Slot A) — ported from the 5-star sources, ls-scaled X. #
# --------------------------------------------------------------------------- #
def _boat_profile(length: float, max_width: float) -> list[tuple[float, float]]:
    half_l = length / 2.0
    half_w = max_width / 2.0
    top: list[tuple[float, float]] = []
    for i in range(25):
        x = -half_l + length * i / 24.0
        t = abs(x) / half_l
        y = 0.0 if t >= 1.0 else half_w * (1.0 - t**1.75) ** 0.48
        top.append((x, y))
    bottom = [(x, -y) for x, y in reversed(top[1:-1])]
    return top + bottom


def _rounded_rect_profile(length, width, radius, *, segments: int = 8):
    r = min(radius, length / 2.0 - 1e-5, width / 2.0 - 1e-5)
    hx = length / 2.0 - r
    hy = width / 2.0 - r
    centers = [(hx, hy), (-hx, hy), (-hx, -hy), (hx, -hy)]
    ranges = [
        (0.0, math.pi / 2.0),
        (math.pi / 2.0, math.pi),
        (math.pi, 1.5 * math.pi),
        (1.5 * math.pi, 2.0 * math.pi),
    ]
    pts: list[tuple[float, float]] = []
    for (cx, cy), (a0, a1) in zip(centers, ranges):
        for j in range(segments + 1):
            a = a0 + (a1 - a0) * j / segments
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def _make_boat_mesh(ls: float):
    outer = _boat_profile(0.36 * ls, 0.056)
    return (
        cq.Workplane("XY")
        .polyline(outer)
        .close()
        .extrude(0.034)
        .faces(">Z")
        .workplane(centerOption="CenterOfBoundBox")
        .slot2D(0.225 * ls, 0.044)
        .cutBlind(-0.030)
    )


def _make_plank_mesh(ls: float):
    outline = _rounded_rect_profile(0.36 * ls, 0.054, 0.007)
    plank = cq.Workplane("XY").polyline(outline).close().extrude(0.014)
    plank = (
        plank.faces(">Z")
        .workplane(centerOption="CenterOfBoundBox")
        .slot2D(0.22 * ls, 0.036)
        .cutBlind(-0.007)
    )
    plank = (
        plank.faces(">Z")
        .workplane(centerOption="CenterOfBoundBox")
        .pushPoints([(-0.150 * ls, 0.0), (0.150 * ls, 0.0)])
        .rect(0.058, 0.014)
        .cutBlind(-0.012)
    )
    return plank


def _ski_half_width_at(x: float, length: float, max_width: float) -> float:
    half_l = length / 2.0
    half_w = max_width / 2.0
    t = abs(x) / half_l
    return 0.0 if t >= 1.0 else half_w * (1.0 - t**2.0) ** 0.55


def _make_ski_mesh(ls: float):
    length = 0.42 * ls
    max_width = 0.038
    body_height = 0.022
    channel_depth = 0.007
    channel_length = 0.28 * ls
    channel_width = 0.026
    tip_lift = 0.014
    tip_region = 0.070 * ls
    half_l = length / 2.0
    plan = [
        (
            -half_l + length * i / 35.0,
            _ski_half_width_at(-half_l + length * i / 35.0, length, max_width),
        )
        for i in range(36)
    ]
    plan += [(x, -y) for x, y in reversed(plan[1:-1])]

    body = cq.Workplane("XY").polyline(plan).close().extrude(body_height)
    body = (
        body.faces(">Z")
        .workplane(centerOption="CenterOfBoundBox")
        .slot2D(channel_length, channel_width)
        .cutBlind(-channel_depth)
    )
    for sign in (-1, 1):
        x_tip = sign * half_l
        x_start = sign * (half_l - tip_region)
        cutter = (
            cq.Workplane("XZ")
            .moveTo(x_start, -0.001)
            .lineTo(x_tip, -0.001)
            .lineTo(x_tip, tip_lift)
            .close()
            .extrude(max_width * 3.0)
            .translate((0.0, -max_width * 1.5, 0.0))
        )
        body = body.cut(cutter)
    for sign in (-1, 1):
        x_tip = sign * half_l
        x_start = sign * (half_l - tip_region)
        ramp_w = max_width * 0.6
        ramp = (
            cq.Workplane("XZ")
            .moveTo(x_start, body_height)
            .lineTo(x_tip, body_height + tip_lift * 0.7)
            .lineTo(x_tip, body_height)
            .close()
            .extrude(ramp_w)
            .translate((0.0, -ramp_w / 2.0, 0.0))
        )
        try:
            body = body.union(ramp)
        except Exception:
            pass
    try:
        body = body.edges(">Z").fillet(0.0015)
    except Exception:
        pass
    return body


_HULL_BUILDERS = {
    "boat_hollow": _make_boat_mesh,
    "flat_plank": _make_plank_mesh,
    "ski_upswept": _make_ski_mesh,
}


def _cone_tip_mesh(name: str, radius: float, length: float, *, toward_positive_x: bool):
    cone = ConeGeometry(radius, length, radial_segments=32, closed=True)
    cone.rotate_y(math.pi / 2.0 if toward_positive_x else -math.pi / 2.0)
    return mesh_from_geometry(cone, name)


def _torus_mesh(name: str, radius: float, tube: float, *, normal: str):
    torus = TorusGeometry(radius, tube, radial_segments=20, tubular_segments=36)
    if normal == "x":
        torus.rotate_y(math.pi / 2.0)
    elif normal == "y":
        torus.rotate_x(math.pi / 2.0)
    return mesh_from_geometry(torus, name)


# --------------------------------------------------------------------------- #
# Body assembly (Slot A) — hull + cavity floor + tips + bearings + ④ decor.    #
# --------------------------------------------------------------------------- #
def _emit_bearings(body, r: ResolvedLoomShuttleConfig, mats):
    """Two bearing blocks + eyelet rings that capture the weft axle at axle_z."""
    top = r.axle_z + 0.003
    # Root the saddle from the keel up through the solid floor so it is embedded
    # in the carved hull (connected), and straddle the axle at the top.
    bottom = r.keel_bottom_z
    h = top - bottom
    cz = bottom + h / 2.0
    for side, sx in (("front", -1.0), ("rear", 1.0)):
        x = sx * r.bearing_x
        body.visual(
            Box((0.008, 0.012, max(h, 0.004))),
            origin=Origin(xyz=(x, 0.0, cz)),
            material=mats["eyelet"],
            name=f"{side}_bearing_saddle",
            material_class_id=_material_class_id("eyelet_metal"),
        )
        body.visual(
            _torus_mesh(f"{side}_bearing_ring", 0.0075, 0.0016, normal="x"),
            origin=Origin(xyz=(x, 0.0, r.axle_z)),
            material=mats["eyelet"],
            name=f"{side}_bearing",
            material_class_id=_material_class_id("eyelet_metal"),
        )


def _floor_params(r: ResolvedLoomShuttleConfig):
    """Cavity/channel floor box (w, d, thickness, center_z) per form — single source."""
    w, d, thk, cz = {
        "boat_hollow": (0.210, 0.030, 0.0012, 0.0043),
        "flat_plank": (0.180, 0.028, 0.0008, 0.0074),
        "ski_upswept": (0.250, 0.020, 0.0010, 0.0155),
    }[r.body_form]
    return w * r.ls, d, thk, cz


def _emit_surface_decor(body, r: ResolvedLoomShuttleConfig, mats):
    """Host-conformal ④ decoration that always embeds in solid material.

    Drilled top holes are drilled into the *solid* nose/tail ends (outboard of the
    open cavity slot); wood-grain wear streaks are recessed into the solid cavity
    floor. Both land in wood that is guaranteed present, so no part-internal islands.
    """
    ls = r.ls
    top = r.top_z
    _fw, fd, fthk, fcz = _floor_params(r)
    floor_top = fcz + fthk / 2.0
    floor_half_y = fd / 2.0
    # Drilled holes in the solid wood just outboard of the open cavity slot (on the
    # centerline), derived from each form's slot half-length so they never land over
    # the open bay; long+deep so they intersect the solid across surface variation.
    slot_half = {"boat_hollow": 0.1125, "flat_plank": 0.110, "ski_upswept": 0.140}[r.body_form] * ls
    for i, (sx, off) in enumerate(((-1.0, 0.009), (-1.0, 0.016), (1.0, 0.009), (1.0, 0.016))):
        body.visual(
            Cylinder(radius=0.0024, length=0.014),
            origin=Origin(xyz=(sx * (slot_half + off), 0.0, top - 0.006)),
            material=mats["eyelet"],
            name=f"top_hole_{i}", material_class_id=_material_class_id("eyelet_metal"),
        )
    # Wear-line grain streaks recessed into the solid cavity floor.
    grain = [
        (-0.16, 0.45, 0.055),
        (0.0, 0.55, 0.070),
        (0.16, 0.45, 0.055),
        (-0.10, -0.50, 0.050),
        (0.10, -0.50, 0.050),
        (0.24, -0.35, 0.040),
    ]
    for i, (fx, yfrac, sx) in enumerate(grain):
        yy = _clamp(yfrac * floor_half_y, -floor_half_y + 0.002, floor_half_y - 0.002)
        body.visual(
            Box((min(sx, 0.9 * fd) * ls, 0.0016, 0.0028)),
            origin=Origin(xyz=(fx * r.length, yy, floor_top - 0.0008)),
            material=mats["grain"],
            name=f"wood_grain_{i}", appearance_only=AppearanceOnlySpec(kind="overlay"),
        )


def _build_body(model, r: ResolvedLoomShuttleConfig, mats):
    body = model.part("body")
    body.visual(
        mesh_from_cadquery(_HULL_BUILDERS[r.body_form](r.ls), "carved_hull", tolerance=0.0007),
        material=mats["hull"],
        name="carved_hull",
        material_class_id=_material_class_id("hull"),
    )
    # Dark worn cavity/channel floor, slightly proud so the hollow reads.
    fw, fd, fthk, fcz = _floor_params(r)
    body.visual(
        Box((fw, fd, fthk)),
        origin=Origin(xyz=(0.0, 0.0, fcz)),
        material=mats["cavity"],
        name="cavity_floor",
        material_class_id=_material_class_id("cavity_wood"),
    )
    # Metal pointed nose tips (boat + ski; the plank has forked notches instead).
    if r.body_form in ("boat_hollow", "ski_upswept"):
        tip_r, tip_len = (0.012, 0.030) if r.body_form == "boat_hollow" else (0.008, 0.024)
        tip_x = 0.475 * r.length
        tip_z = 0.018 if r.body_form == "boat_hollow" else r.top_z * 0.6
        body.visual(
            _cone_tip_mesh("front_tip_m", tip_r, tip_len, toward_positive_x=False),
            origin=Origin(xyz=(-tip_x, 0.0, tip_z)),
            material=mats["metal"],
            name="front_metal_tip",
            material_class_id=_material_class_id("hardware_metal"),
        )
        body.visual(
            _cone_tip_mesh("rear_tip_m", tip_r, tip_len, toward_positive_x=True),
            origin=Origin(xyz=(tip_x, 0.0, tip_z)),
            material=mats["metal"],
            name="rear_metal_tip",
            material_class_id=_material_class_id("hardware_metal"),
        )
    _emit_bearings(body, r, mats)
    _emit_surface_decor(body, r, mats)
    return body


# --------------------------------------------------------------------------- #
# Bobbin spool (shared by through_axle + spindle_arm).                         #
# --------------------------------------------------------------------------- #
def _emit_spool(bobbin, r: ResolvedLoomShuttleConfig, mats, *, core_length: float):
    bobbin.visual(
        Cylinder(radius=r.core_radius, length=core_length),
        origin=Origin(rpy=_CYL_TO_X),
        material=mats["bobbin_wood"],
        name="bobbin_core",
        material_class_id=_material_class_id("bobbin_wood"),
    )
    bobbin.visual(
        Cylinder(radius=r.thread_radius, length=0.142 * r.ls),
        origin=Origin(rpy=_CYL_TO_X),
        material=mats["yarn"],
        name="cotton_thread",
        material_class_id=_material_class_id("cotton_yarn"),
    )
    for x, nm in ((-0.078 * r.ls, "front_flange"), (0.078 * r.ls, "rear_flange")):
        bobbin.visual(
            Cylinder(radius=r.flange_radius, length=0.010),
            origin=Origin(xyz=(x, 0.0, 0.0), rpy=_CYL_TO_X),
            material=mats["eyelet"],
            name=nm,
            material_class_id=_material_class_id("eyelet_metal"),
        )
        bobbin.visual(
            Cylinder(radius=0.0080 * r.rs, length=0.006),
            origin=Origin(xyz=(x * 1.03, 0.0, 0.0), rpy=_CYL_TO_X),
            material=mats["bobbin_wood"],
            name=f"{nm}_boss",
            material_class_id=_material_class_id("bobbin_wood"),
        )
    # Off-axis red thread tail makes the spin visually apparent.
    bobbin.visual(
        Box((0.014, 0.004, 0.003)),
        origin=Origin(xyz=(0.071 * r.ls, 0.001, r.flange_radius - 0.0004), rpy=(0.0, 0.0, 0.08)),
        material=mats["red"],
        name="red_thread",
        material_class_id=_material_class_id("red_thread"),
    )


# --------------------------------------------------------------------------- #
# Slot B mechanisms.                                                           #
# --------------------------------------------------------------------------- #
def _build_through_axle(model, body, r: ResolvedLoomShuttleConfig, mats):
    bobbin = model.part("bobbin")
    _emit_spool(bobbin, r, mats, core_length=r.core_length)
    model.articulation(
        "body_to_bobbin",
        ArticulationType.REVOLUTE,
        parent=body,
        child=bobbin,
        origin=Origin(xyz=(0.0, 0.0, r.axle_z)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=0.4, velocity=8.0, lower=-math.pi, upper=math.pi),
    )


def _build_spindle_arm(model, body, r: ResolvedLoomShuttleConfig, mats):
    arm_length = 2.0 * r.bearing_x
    # Front latch catch on the body (host visual).
    body.visual(
        Box((0.008, 0.010, 0.006)),
        origin=Origin(xyz=(-r.bearing_x, 0.0, r.axle_z)),
        material=mats["metal"],
        name="front_latch_notch",
        material_class_id=_material_class_id("hardware_metal"),
    )
    # Pivoting spindle arm (hinged at the rear bearing).
    arm = model.part("spindle_arm")
    arm.visual(
        Cylinder(radius=0.0025, length=arm_length),
        origin=Origin(xyz=(-arm_length / 2.0, 0.0, 0.0), rpy=_CYL_TO_X),
        material=mats["metal"],
        name="spindle_rod",
        material_class_id=_material_class_id("hardware_metal"),
    )
    arm.visual(
        Cylinder(radius=0.004, length=0.018),
        origin=Origin(rpy=_CYL_TO_X),
        material=mats["eyelet"],
        name="pivot_pin",
        material_class_id=_material_class_id("eyelet_metal"),
    )
    arm.visual(
        Cylinder(radius=0.0062, length=0.003),
        origin=Origin(rpy=_CYL_TO_X),
        material=mats["eyelet"],
        name="pivot_collar",
        material_class_id=_material_class_id("eyelet_metal"),
    )
    arm.visual(
        Box((0.012, 0.008, 0.006)),
        origin=Origin(xyz=(-arm_length + 0.006, 0.0, -0.001)),
        material=mats["metal"],
        name="latch_hook",
        material_class_id=_material_class_id("hardware_metal"),
    )
    model.articulation(
        "body_to_spindle_arm",
        ArticulationType.REVOLUTE,
        parent=body,
        child=arm,
        origin=Origin(xyz=(r.bearing_x, 0.0, r.axle_z)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=1.0, velocity=4.0, lower=0.0, upper=r.arm_open),
    )
    bobbin = model.part("bobbin")
    # Core kept short of the arm ends so it clears the pivot pin and latch hook.
    _emit_spool(bobbin, r, mats, core_length=arm_length - 0.04)
    model.articulation(
        "spindle_arm_to_bobbin",
        ArticulationType.REVOLUTE,
        parent=arm,
        child=bobbin,
        origin=Origin(xyz=(-arm_length / 2.0, 0.0, 0.0)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=0.4, velocity=8.0, lower=-math.pi, upper=math.pi),
    )


def _pirn_core_mesh():
    profile = [
        (0.000, 0.000),
        (0.0105, 0.000),
        (0.0100, 0.015),
        (0.0090, 0.035),
        (0.0075, 0.060),
        (0.0058, 0.085),
        (0.0042, 0.110),
        (0.0030, 0.130),
        (0.0020, 0.138),
        (0.000, 0.140),
    ]
    return mesh_from_geometry(LatheGeometry(profile, segments=32), "pirn_core")


def _pirn_thread_mesh():
    profile = [
        (0.000, 0.005),
        (0.0130, 0.005),
        (0.0125, 0.020),
        (0.0115, 0.040),
        (0.0100, 0.060),
        (0.0082, 0.078),
        (0.0065, 0.092),
        (0.000, 0.092),
    ]
    return mesh_from_geometry(LatheGeometry(profile, segments=32), "pirn_thread")


def _build_end_delivery(model, body, r: ResolvedLoomShuttleConfig, mats):
    # Fixed cantilever spindle rod + collar (body visuals). The rod is *rooted at
    # the rear bearing*: its rear end coincides with ``bearing_x`` for every
    # body_form, so it always seats into the solid rear bearing saddle/collar
    # (previously a fixed forward span left the rod short of the bearing on the
    # longer ski form, orphaning it as a disconnected island).
    rod_len = 0.130 * r.ls
    rod_cx = r.bearing_x - rod_len / 2.0
    body.visual(
        Cylinder(radius=0.0028, length=rod_len),
        origin=Origin(xyz=(rod_cx, 0.0, r.axle_z), rpy=_CYL_TO_X),
        material=mats["metal"],
        name="spindle_rod",
        material_class_id=_material_class_id("hardware_metal"),
    )
    body.visual(
        Cylinder(radius=0.0062, length=0.008),
        origin=Origin(xyz=(r.bearing_x, 0.0, r.axle_z), rpy=_CYL_TO_X),
        material=mats["metal"],
        name="spindle_collar",
        material_class_id=_material_class_id("hardware_metal"),
    )
    # Nose tension gate. The post is planted deep into the solid hull: it spans
    # from just above the keel base slab up past the top surface, so it always
    # intersects the solid wood that survives below the open cavity/notch,
    # regardless of body_form (anchoring on the nominal top surface alone left it
    # floating above the tapered/notched nose). The eyelet rides on the post top.
    gate_x = -0.42 * r.length
    post_bottom = r.keel_bottom_z + 0.001
    post_top = r.top_z + 0.012
    post_len = post_top - post_bottom
    body.visual(
        Cylinder(radius=0.0020, length=post_len),
        origin=Origin(xyz=(gate_x, 0.0, (post_bottom + post_top) / 2.0)),
        material=mats["metal"],
        name="tension_gate_post",
        material_class_id=_material_class_id("hardware_metal"),
    )
    tg = TorusGeometry(0.0040, 0.0010, radial_segments=16, tubular_segments=24)
    tg.rotate_y(math.pi / 2.0)
    body.visual(
        mesh_from_geometry(tg, "tension_gate_eyelet_m"),
        origin=Origin(xyz=(gate_x, 0.0, post_top + 0.002)),
        material=mats["eyelet"],
        name="tension_gate_eyelet",
        material_class_id=_material_class_id("eyelet_metal"),
    )
    # Tapered LatheGeometry pirn (Rule 3: never downgraded to a Cylinder).
    bobbin = model.part("bobbin")
    pirn_rot = (0.0, -math.pi / 2.0, 0.0)
    bobbin.visual(
        _pirn_core_mesh(),
        origin=Origin(rpy=pirn_rot),
        material=mats["bobbin_wood"],
        name="bobbin_core",
        material_class_id=_material_class_id("bobbin_wood"),
    )
    bobbin.visual(
        _pirn_thread_mesh(),
        origin=Origin(rpy=pirn_rot),
        material=mats["yarn"],
        name="cotton_thread",
        material_class_id=_material_class_id("cotton_yarn"),
    )
    bobbin.visual(
        Cylinder(radius=0.0120, length=0.006),
        origin=Origin(xyz=(0.003, 0.0, 0.0), rpy=_CYL_TO_X),
        material=mats["eyelet"],
        name="rear_flange",
        material_class_id=_material_class_id("eyelet_metal"),
    )
    bobbin.visual(
        Cylinder(radius=0.0110, length=0.005),
        origin=Origin(xyz=(-0.016, 0.0, 0.0), rpy=_CYL_TO_X),
        material=mats["eyelet"],
        name="front_flange",
        material_class_id=_material_class_id("eyelet_metal"),
    )
    bobbin.visual(
        Box((0.012, 0.004, 0.003)),
        origin=Origin(xyz=(-0.040, 0.001, 0.009), rpy=(0.0, 0.0, 0.08)),
        material=mats["red"],
        name="red_thread",
        material_class_id=_material_class_id("red_thread"),
    )
    model.articulation(
        "body_to_bobbin",
        ArticulationType.REVOLUTE,
        parent=body,
        child=bobbin,
        origin=Origin(xyz=(r.bearing_x - 0.005, 0.0, r.axle_z)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=0.4, velocity=8.0, lower=-math.pi, upper=math.pi),
    )


_MECHANISM_BUILDERS = {
    "through_axle": _build_through_axle,
    "spindle_arm": _build_spindle_arm,
    "end_delivery": _build_end_delivery,
}


# --------------------------------------------------------------------------- #
# Slot C — underside roller bogie (multiplicity N).                            #
# --------------------------------------------------------------------------- #
def _roller_positions(r: ResolvedLoomShuttleConfig) -> list[float]:
    spacing = 0.060 * r.ls
    start = -(r.n - 1) * spacing / 2.0
    return [start + i * spacing for i in range(r.n)]


def _emit_roller_bogie(model, body, r: ResolvedLoomShuttleConfig, mats):
    wheel_len = 0.018
    bracket_off = wheel_len / 2.0 + 0.002
    bracket_h = abs(r.roller_z - r.keel_bottom_z)
    for i, x in enumerate(_roller_positions(r)):
        # Fixed body-side axle pin + fork brackets that bridge the keel to the axle.
        for ysign, tag in ((-1.0, "L"), (1.0, "R")):
            body.visual(
                Box((0.006, 0.003, bracket_h)),
                origin=Origin(xyz=(x, ysign * bracket_off, r.keel_bottom_z - bracket_h / 2.0)),
                material=mats["metal"],
                name=f"roller_bracket_{i}_{tag}",
                material_class_id=_material_class_id("hardware_metal"),
            )
        body.visual(
            Cylinder(radius=0.0016, length=0.030),
            origin=Origin(xyz=(x, 0.0, r.roller_z), rpy=_CYL_TO_Y),
            material=mats["metal"],
            name=f"roller_axle_{i}",
            material_class_id=_material_class_id("hardware_metal"),
        )
        roller = model.part(f"roller_{i}")
        roller.visual(
            Cylinder(radius=r.roller_radius, length=wheel_len),
            origin=Origin(rpy=_CYL_TO_Y),
            material=mats["roller_steel"],
            name=f"roller_wheel_{i}",
            material_class_id=_material_class_id("roller_steel"),
        )
        model.articulation(
            f"body_to_roller_{i}",
            ArticulationType.CONTINUOUS,
            parent=body,
            child=roller,
            origin=Origin(xyz=(x, 0.0, r.roller_z)),
            axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(effort=0.2, velocity=16.0),
        )


# --------------------------------------------------------------------------- #
# Build                                                                        #
# --------------------------------------------------------------------------- #
def build_loom_shuttle(
    config: LoomShuttleConfig | None = None, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={"domain": "Textiles_Fabric", "small_class": "Loom shuttle"},
    )
    mats = {
        k: model.material(f"ls_{k}_{r.palette_style}", rgba=rgba)
        for k, rgba in PALETTES[r.palette_style].items()
    }

    body = _build_body(model, r, mats)
    _MECHANISM_BUILDERS[r.bobbin_mechanism](model, body, r, mats)
    if r.underside == "roller_bogie":
        _emit_roller_bogie(model, body, r, mats)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_loom_shuttle(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_loom_shuttle(config_from_seed(seed), assets=assets)


# --------------------------------------------------------------------------- #
# Tests                                                                        #
# --------------------------------------------------------------------------- #
def _allow_captures(ctx, model, r: ResolvedLoomShuttleConfig):
    body = model.get_part("body")
    bobbin = model.get_part("bobbin")
    bearing_elems = ("front_bearing", "rear_bearing", "front_bearing_saddle", "rear_bearing_saddle")

    if r.bobbin_mechanism == "through_axle":
        for be in bearing_elems:
            ctx.allow_overlap(
                body,
                bobbin,
                elem_a=be,
                elem_b="bobbin_core",
                reason="Bobbin axle is journaled through the bearing block (captured).",
            )
    if r.bobbin_mechanism == "spindle_arm":
        arm = model.get_part("spindle_arm")
        for ea, eb, why in (
            (
                "carved_hull",
                "pivot_pin",
                "Captured hinge pin passes through the hull at the rear bearing.",
            ),
            ("rear_bearing", "pivot_pin", "Captured hinge pin seats in the rear bearing bore."),
            (
                "rear_bearing_saddle",
                "pivot_pin",
                "Captured hinge pin passes through the rear bearing block.",
            ),
            (
                "rear_bearing",
                "pivot_collar",
                "Retention collar is wider than the bearing bore (captured).",
            ),
            (
                "rear_bearing_saddle",
                "pivot_collar",
                "Retention collar bears against the rear bearing block.",
            ),
            (
                "front_bearing",
                "spindle_rod",
                "Arm rod tip rests in the front bearing when latched.",
            ),
            (
                "front_bearing_saddle",
                "spindle_rod",
                "Arm rod tip rests in the front bearing block when latched.",
            ),
            (
                "front_bearing",
                "latch_hook",
                "Latch hook engages the front bearing region when closed.",
            ),
            (
                "front_bearing_saddle",
                "latch_hook",
                "Latch hook engages the front bearing block when closed.",
            ),
            (
                "front_latch_notch",
                "latch_hook",
                "Latch hook seats in the front latch notch when closed.",
            ),
        ):
            ctx.allow_overlap(body, arm, elem_a=ea, elem_b=eb, reason=why)
    if r.bobbin_mechanism == "end_delivery":
        for ea in ("spindle_rod", "spindle_collar", "rear_bearing", "rear_bearing_saddle"):
            for eb in ("bobbin_core", "cotton_thread", "rear_flange", "front_flange"):
                ctx.allow_overlap(
                    body,
                    bobbin,
                    elem_a=ea,
                    elem_b=eb,
                    reason="Fixed cantilever spindle passes through the pirn bore (end-delivery seat).",
                )
    if r.body_form == "ski_upswept":
        for eb in ("bobbin_core", "cotton_thread", "front_flange", "rear_flange"):
            ctx.allow_overlap(
                body,
                bobbin,
                elem_a="carved_hull",
                elem_b=eb,
                reason="Bobbin rides in the shallow open ski channel; thread overlaps the hull walls.",
            )
    if r.underside == "roller_bogie":
        for i in range(r.n):
            roller = model.get_part(f"roller_{i}")
            ctx.allow_overlap(
                body,
                roller,
                elem_a=f"roller_axle_{i}",
                elem_b=f"roller_wheel_{i}",
                reason="Roller wheel rides on its fixed body-side axle pin (captured journal).",
            )


def _aabb_center(aabb):
    if aabb is None:
        return None
    lo, hi = aabb
    return tuple((lo[i] + hi[i]) * 0.5 for i in range(3))


def run_loom_shuttle_tests(
    object_model: ArticulatedObject, config: LoomShuttleConfig
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    body = object_model.get_part("body")
    bobbin = object_model.get_part("bobbin")
    spin = object_model.get_articulation(
        "body_to_bobbin" if r.bobbin_mechanism != "spindle_arm" else "spindle_arm_to_bobbin"
    )

    _allow_captures(ctx, object_model, r)

    # --- Compiler baseline (same as the sweep) ---
    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_joint_mating_has_gap()
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=32, ignore_fixed=True)

    # --- Identity ---
    ctx.check(
        "small class is Loom shuttle",
        object_model.meta.get("small_class") == "Loom shuttle"
        and "loom_shuttle" in object_model.name,
        details=f"name={object_model.name}, meta={object_model.meta}",
    )
    hull_aabb = ctx.part_element_world_aabb(body, elem="carved_hull")
    if hull_aabb is not None:
        lo, hi = hull_aabb
        dx, dy, dz = hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2]
        ctx.check(
            "body is an elongated shuttle (length >> width, low height)",
            dx > 0.30 and dy < 0.075 and dx / max(dy, 1e-6) > 4.0 and dz < 0.06,
            details=f"dx={dx:.3f} dy={dy:.3f} dz={dz:.3f}",
        )

    # --- Weft package spins about +X ---
    ctx.check(
        "weft package spins about the long +X axis (REVOLUTE)",
        spin.articulation_type == ArticulationType.REVOLUTE
        and tuple(round(v, 3) for v in spin.axis) == (1.0, 0.0, 0.0),
        details=f"type={spin.articulation_type}, axis={spin.axis}",
    )
    ctx.expect_within(
        bobbin,
        body,
        axes="xy",
        margin=0.004,
        name="weft package is retained inside the shuttle footprint",
    )
    ctx.expect_overlap(
        bobbin,
        body,
        axes="x",
        min_overlap=0.08,
        name="weft package spans the central cavity lengthwise",
    )

    # --- Bobbin/pirn spin visibly carries the off-axis red thread mark ---
    rest = _aabb_center(ctx.part_element_world_aabb(bobbin, elem="red_thread"))
    with ctx.pose({spin: 1.2}):
        turned = _aabb_center(ctx.part_element_world_aabb(bobbin, elem="red_thread"))
    ctx.check(
        "spinning the weft package moves the red thread mark off-axis",
        rest is not None
        and turned is not None
        and abs(rest[1] - turned[1]) + abs(rest[2] - turned[2]) > 0.003,
        details=f"rest={rest}, turned={turned}",
    )

    # --- Mechanism-specific structure + motion ---
    if r.bobbin_mechanism == "spindle_arm":
        hinge = object_model.get_articulation("body_to_spindle_arm")
        ctx.check(
            "spindle arm hinge is REVOLUTE about +Y",
            hinge.articulation_type == ArticulationType.REVOLUTE
            and tuple(round(v, 3) for v in hinge.axis) == (0.0, 1.0, 0.0),
            details=f"type={hinge.articulation_type}, axis={hinge.axis}",
        )
        rest_z = ctx.part_world_position(bobbin)
        with ctx.pose({hinge: r.arm_open}):
            lifted_z = ctx.part_world_position(bobbin)
        ctx.check(
            "arm hinge lifts the pirn up out of the cavity for loading",
            rest_z is not None and lifted_z is not None and lifted_z[2] > rest_z[2] + 0.02,
            details=f"rest_z={None if rest_z is None else rest_z[2]:.4f}, "
            f"lifted_z={None if lifted_z is None else lifted_z[2]:.4f}",
        )
    elif r.bobbin_mechanism == "end_delivery":
        ctx.check(
            "end-delivery has a fixed cantilever spindle + nose tension gate",
            body.get_visual("spindle_rod") is not None
            and body.get_visual("tension_gate_post") is not None,
            details=f"body visuals={sorted(v.name for v in body.visuals)[:12]}",
        )
        pirn_aabb = ctx.part_element_world_aabb(bobbin, elem="bobbin_core")
        ctx.check(
            "pirn is cantilevered forward of the rear spindle root",
            pirn_aabb is not None and pirn_aabb[0][0] < r.bearing_x - 0.05,
            details=f"pirn min_x={None if pirn_aabb is None else pirn_aabb[0][0]:.4f}",
        )

    # --- Roller bogie: N rollers, each a CONTINUOUS +Y wheel that hangs below the keel ---
    if r.underside == "roller_bogie":
        for i in range(r.n):
            roller = object_model.get_part(f"roller_{i}")
            rj = object_model.get_articulation(f"body_to_roller_{i}")
            ctx.check(
                f"roller_{i} is a CONTINUOUS +Y wheel",
                roller is not None
                and rj.articulation_type == ArticulationType.CONTINUOUS
                and abs(rj.axis[1]) > 0.99
                and roller.get_visual(f"roller_wheel_{i}") is not None,
                details=f"type={rj.articulation_type}, axis={rj.axis}",
            )
            ctx.expect_gap(
                body,
                roller,
                axis="z",
                positive_elem="carved_hull",
                negative_elem=f"roller_wheel_{i}",
                min_gap=0.0005,
                name=f"roller_{i} hangs below the hull keel",
            )
        # Rollers spin in place (continuous joint, no translation).
        r0 = object_model.get_part("roller_0")
        rest_r = ctx.part_world_position(r0)
        with ctx.pose({object_model.get_articulation("body_to_roller_0"): 1.5}):
            spun_r = ctx.part_world_position(r0)
        ctx.check(
            "roller spins in place without translating",
            rest_r is not None
            and spun_r is not None
            and all(abs(rest_r[k] - spun_r[k]) < 1e-6 for k in range(3)),
            details=f"rest={rest_r}, spun={spun_r}",
        )

    ctx.check(
        "slot_choices recorded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )
    return ctx.report()


__all__ = (
    "LoomShuttleConfig",
    "ResolvedLoomShuttleConfig",
    "build_loom_shuttle",
    "build_seeded_loom_shuttle",
    "config_from_seed",
    "resolve_config",
    "run_loom_shuttle_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
)
