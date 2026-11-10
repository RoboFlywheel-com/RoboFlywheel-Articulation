# SPDX-License-Identifier: Apache-2.0

"""Pet_Animal related / Cat flap — modular parametric template.

A framed pet-sized opening mounted in a host panel/door/wall, closed by a
top-hinged swing ``flap`` the animal pushes through (with a bottom magnet
latch). Every seed keeps at least one real opening joint (the swing flap's
REVOLUTE). Sourced from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/cat_flap.md`` and the 7 synced
5-star records (2 origin + 5 slot-fork variants) under ``data/records/``.

Structure (pattern = ``mixed``): a single grounded root ``panel_frame`` part
carrying the fixed geometry, with the operable flap(s) / lock slider / mode
button parented to it (parallel children):

  * ``opening_form`` (2, ③ Planar Boundary): rounded_rect (rectangular bezel +
    box flap) / circular (round porthole bezel + disc flap + edge ring).
  * ``host_context`` (2, ① skeleton): door_thin_panel (a single cutout panel
    host) / wall_tunnel_liner (no door panel; a 4-wall through-wall tunnel liner
    + a rear_frame ring — supplies the depth double-flap needs).
  * ``closure_lock`` (2, ② joint): magnet_latch (magnet only) / slide_lock (adds
    a lock_slider captured in guide rails on a PRISMATIC joint across the
    opening).  rounded_rect only.
  * ``control_module`` (2, ① skeleton): none / electronic_microchip (sensor
    housing + battery cover + antenna ring + a mode_button rotary dial REVOLUTE).
  * ``n_flaps`` (N in [1,2], structural; double only for rounded_rect +
    wall_tunnel_liner — front flap swings out +Y, rear flap swings in -Y so the
    two never collide) / ``n_screws`` (N in {4,6}, ④ cosmetic; 6 rounded_rect
    only): two multiplicity axes encoded into the slot_choice tuple.

Coordinate frame (adopted from the rec_...__001 / rec_form_round BezelGeometry
family): the door_panel lies in the XY plane rotated rpy=(-pi/2,0,0); +Y is the
front/outside, -Y the back/inside; the opening is centred at the origin. The
flap is BUILT at q=0 = CLOSED (hanging vertical in the opening) using the exact
local coordinates each source passed to ``_flap_origin`` (which is the angle=0
hanging position), so q=0 reproduces the source's verified closed pose and
q=+upper swings it open.

All hinge pins / sleeves / slider shoes / dial bosses are captured-pin/slide
geometry, so those joints omit ``MatingContract`` (grandfathered) and are
guarded by the flat articulation-origin baseline + element-scoped
``allow_overlap`` (mirroring each source record's run_tests allow_overlap block).
We use raw ``model.articulation(...)`` rather than the ``hinged_panel`` idiom to
keep the source captured-pin semantics (the hinge barrel/pin is an intentional
overlap the idiom's clearance solver would not model), matching
greenhouse_vent_roof.
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
    BezelGeometry,
    Box,
    Cylinder,
    KnobGeometry,
    KnobGrip,
    KnobIndicator,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
    mesh_from_geometry,
)

__modular__ = True

OpeningForm = Literal["rounded_rect", "circular"]
HostContext = Literal["door_thin_panel", "wall_tunnel_liner"]
ClosureLock = Literal["magnet_latch", "slide_lock"]
ControlModule = Literal["none", "electronic_microchip"]
PaletteStyle = Literal[
    "warm_white",
    "charcoal_wood",
    "brushed_metal",
    "graphite_glass",
    "cream_wood",
]

OPENING_FORMS: tuple[OpeningForm, ...] = ("rounded_rect", "circular")
HOST_CONTEXTS: tuple[HostContext, ...] = ("door_thin_panel", "wall_tunnel_liner")
CLOSURE_LOCKS: tuple[ClosureLock, ...] = ("magnet_latch", "slide_lock")
CONTROL_MODULES: tuple[ControlModule, ...] = ("none", "electronic_microchip")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "warm_white",
    "charcoal_wood",
    "brushed_metal",
    "graphite_glass",
    "cream_wood",
)

# --- Fixed real-world geometry (meters), from the origin/source records. ------
PANEL_W = 0.42
PANEL_H = 0.54
PANEL_T = 0.035
FRAME_D = 0.028
FRONT_Y = PANEL_T / 2.0
FRAME_FRONT_Y = FRONT_Y + FRAME_D
HINGE_Y = FRAME_FRONT_Y + 0.006
# nominal (opening_scale = 1.0) opening / frame / flap dims
BASE_OPENING_W = 0.235
BASE_OPENING_H = 0.305
BASE_FRAME_W = 0.320
BASE_FRAME_H = 0.405
BASE_FLAP_W = 0.215
BASE_FLAP_H = 0.300
BASE_OPENING_D = 0.26
BASE_FRAME_OD = 0.34
BASE_FLAP_D = 0.248
PANEL_TOP_Z = -0.012  # flap-local: top of the translucent panel below the sleeve
RIM_T = 0.012
TUNNEL_DEPTH = 0.16  # wall_tunnel_liner through-wall depth (rear_frame at -depth)
BASE_FLAP_SWING = 0.85  # nominal top-hinge open angle (rad)
BASE_SLIDE_TRAVEL = 0.34  # nominal 4-way lock slider prismatic travel

# Constant hardware colours (only trim / host / flap vary by palette).
_SHARED_RGBA: dict[str, tuple[float, float, float, float]] = {
    "seal": (0.012, 0.011, 0.010, 1.0),
    "magnet": (0.02, 0.02, 0.018, 1.0),
    "metal": (0.55, 0.55, 0.52, 1.0),
    "liner": (0.78, 0.77, 0.75, 1.0),
    "housing": (0.80, 0.80, 0.77, 1.0),
    "batt": (0.72, 0.72, 0.70, 1.0),
    "antenna": (0.10, 0.10, 0.09, 1.0),
    "button": (0.18, 0.48, 0.22, 1.0),
    "led": (0.10, 0.85, 0.25, 1.0),
    "slider": (0.28, 0.28, 0.30, 1.0),
}
_VARIANT_RGBA: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "warm_white": {
        "trim": (0.92, 0.90, 0.84, 1.0),
        "host": (0.58, 0.78, 0.82, 0.30),
        "flap": (0.36, 0.30, 0.24, 0.42),
        "flap_edge": (0.86, 0.92, 0.90, 0.70),
    },
    "charcoal_wood": {
        "trim": (0.055, 0.052, 0.050, 1.0),
        "host": (0.42, 0.23, 0.11, 1.0),
        "flap": (0.73, 0.90, 0.95, 0.42),
        "flap_edge": (0.86, 0.92, 0.90, 0.70),
    },
    "brushed_metal": {
        "trim": (0.62, 0.63, 0.60, 1.0),
        "host": (0.90, 0.90, 0.88, 1.0),
        "flap": (0.73, 0.90, 0.95, 0.42),
        "flap_edge": (0.82, 0.86, 0.88, 0.72),
    },
    "graphite_glass": {
        "trim": (0.20, 0.20, 0.22, 1.0),
        "host": (0.55, 0.72, 0.80, 0.32),
        "flap": (0.34, 0.30, 0.26, 0.44),
        "flap_edge": (0.70, 0.74, 0.78, 0.72),
    },
    "cream_wood": {
        "trim": (0.88, 0.84, 0.72, 1.0),
        "host": (0.60, 0.42, 0.24, 1.0),
        "flap": (0.80, 0.68, 0.45, 0.45),
        "flap_edge": (0.90, 0.88, 0.80, 0.72),
    },
}


def _palette_rgba(style: PaletteStyle) -> dict[str, tuple[float, float, float, float]]:
    return {**_SHARED_RGBA, **_VARIANT_RGBA[style]}


@dataclass(frozen=True)
class CatFlapConfig:
    opening_form: OpeningForm | None = None
    host_context: HostContext | None = None
    closure_lock: ClosureLock | None = None
    control_module: ControlModule | None = None
    n_flaps: int | None = None
    n_screws: int | None = None
    palette_style: PaletteStyle | None = None
    opening_scale: float = 1.0
    flap_swing_scale: float = 1.0
    slide_travel_scale: float = 1.0
    name: str = "cat_flap"


@dataclass(frozen=True)
class ResolvedCatFlapConfig:
    opening_form: OpeningForm
    host_context: HostContext
    closure_lock: ClosureLock
    control_module: ControlModule
    n_flaps: int
    n_screws: int
    palette_style: PaletteStyle
    is_round: bool
    # opening / frame / flap geometry (already opening_scaled)
    opening_w: float
    opening_h: float
    frame_w: float
    frame_h: float
    flap_w: float
    flap_h: float
    opening_d: float
    frame_od: float
    flap_d: float
    hinge_z: float
    # motion envelopes
    flap_swing: float
    slide_travel: float
    name: str


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices, default):
    return value if value in choices else default


def config_from_seed(seed: int) -> CatFlapConfig:
    rng = random.Random(seed)
    return CatFlapConfig(
        opening_form=rng.choice(OPENING_FORMS),
        host_context=rng.choice(HOST_CONTEXTS),
        closure_lock=rng.choice(CLOSURE_LOCKS),
        control_module=rng.choice(CONTROL_MODULES),
        # requested counts; resolve_config gates them to their legal contexts.
        # 1 vs 2 leaves; the rect+tunnel gate in resolve_config already makes a
        # realized double flap rare (~6% of seeds), so keep the raw draw balanced
        # so n2 actually appears among the 0-35 sweep seeds.
        n_flaps=rng.choices((1, 2), weights=(0.5, 0.5), k=1)[0],
        n_screws=rng.choice((4, 6)),
        palette_style=rng.choice(PALETTE_STYLES),
        opening_scale=round(rng.uniform(0.90, 1.12), 4),
        flap_swing_scale=round(rng.uniform(0.85, 1.10), 4),
        slide_travel_scale=round(rng.uniform(0.85, 1.10), 4),
        name=f"seeded_cat_flap_{seed}",
    )


def resolve_config(config: CatFlapConfig | None = None) -> ResolvedCatFlapConfig:
    cfg = config or CatFlapConfig()

    opening_form = _pick(cfg.opening_form, OPENING_FORMS, "rounded_rect")
    host_context = _pick(cfg.host_context, HOST_CONTEXTS, "door_thin_panel")
    closure_lock = _pick(cfg.closure_lock, CLOSURE_LOCKS, "magnet_latch")
    control_module = _pick(cfg.control_module, CONTROL_MODULES, "none")
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES, "warm_white")
    is_round = opening_form == "circular"

    # --- Compatibility gating (spec 9). ---
    # slide_lock is a rectangular sliding panel -> rounded_rect only.
    if is_round:
        closure_lock = "magnet_latch"
    # slide_lock and the electronic module both crowd the front face above the
    # opening; they are mutually exclusive (never combined in the source pool).
    if closure_lock == "slide_lock" and control_module == "electronic_microchip":
        control_module = "none"

    # n_flaps=2 (front + rear flaps in series) needs a through-wall depth and a
    # rectangular double-flap source -> rounded_rect + wall_tunnel_liner only.
    n_flaps = int(cfg.n_flaps) if cfg.n_flaps is not None else 1
    n_flaps = int(_clamp(n_flaps, 1, 2))
    if not (opening_form == "rounded_rect" and host_context == "wall_tunnel_liner"):
        n_flaps = 1

    # n_screws=6 only for rounded_rect (circle uses a 4-screw 45deg ring).
    n_screws = int(cfg.n_screws) if cfg.n_screws is not None else 4
    n_screws = 6 if (n_screws >= 6 and not is_round) else 4

    s = _clamp(cfg.opening_scale, 0.90, 1.12)
    flap_swing = _clamp(BASE_FLAP_SWING * _clamp(cfg.flap_swing_scale, 0.85, 1.10), 0.70, 1.00)
    slide_travel = _clamp(
        BASE_SLIDE_TRAVEL * _clamp(cfg.slide_travel_scale, 0.85, 1.10), 0.26, 0.40
    )

    opening_h = BASE_OPENING_H * s
    opening_d = BASE_OPENING_D * s
    hinge_z = (opening_h / 2.0 if not is_round else opening_d / 2.0) + 0.014

    return ResolvedCatFlapConfig(
        opening_form=opening_form,
        host_context=host_context,
        closure_lock=closure_lock,
        control_module=control_module,
        n_flaps=n_flaps,
        n_screws=n_screws,
        palette_style=palette_style,
        is_round=is_round,
        opening_w=BASE_OPENING_W * s,
        opening_h=opening_h,
        frame_w=BASE_FRAME_W * s,
        frame_h=BASE_FRAME_H * s,
        flap_w=BASE_FLAP_W * s,
        flap_h=BASE_FLAP_H * s,
        opening_d=opening_d,
        frame_od=BASE_FRAME_OD * s,
        flap_d=BASE_FLAP_D * s,
        hinge_z=hinge_z,
        flap_swing=flap_swing,
        slide_travel=slide_travel,
        name=cfg.name or "cat_flap",
    )


def slot_choices_for_config(
    config: CatFlapConfig | ResolvedCatFlapConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedCatFlapConfig) else resolve_config(config)
    return (
        ("opening_form", r.opening_form),
        ("host_context", r.host_context),
        ("closure_lock", r.closure_lock),
        ("control_module", r.control_module),
        ("n_flaps", f"n{r.n_flaps}"),
        ("n_screws", f"n{r.n_screws}"),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Geometry helpers.
# ---------------------------------------------------------------------------
def _make_bezel(
    r: ResolvedCatFlapConfig,
    *,
    opening: tuple[float, float],
    outer: tuple[float, float],
    depth: float,
    opening_corner: float = 0.018,
    outer_corner: float = 0.026,
) -> BezelGeometry:
    if r.is_round:
        d_open = opening[0]
        d_out = outer[0]
        return BezelGeometry(
            (d_open, d_open),
            (d_out, d_out),
            depth,
            opening_shape="circle",
            outer_shape="circle",
            center=True,
        )
    return BezelGeometry(
        opening,
        outer,
        depth,
        opening_shape="rounded_rect",
        outer_shape="rounded_rect",
        opening_corner_radius=opening_corner,
        outer_corner_radius=outer_corner,
        center=True,
    )


def _panel_cutout(r: ResolvedCatFlapConfig) -> cq.Workplane:
    """Door panel with a rect or circular through-opening (host_context=door)."""
    wp = cq.Workplane("XY").rect(PANEL_W, PANEL_H)
    if r.is_round:
        return wp.circle(r.opening_d / 2.0 + 0.005).extrude(PANEL_T, both=True)
    return wp.rect(r.opening_w + 0.010, r.opening_h + 0.010).extrude(PANEL_T, both=True)


def _flap_disc(r: ResolvedCatFlapConfig) -> cq.Workplane:
    fr = r.flap_d / 2.0
    return cq.Workplane("XY").circle(fr - 0.008).extrude(0.002, both=True)


def _edge_ring(r: ResolvedCatFlapConfig) -> cq.Workplane:
    fr = r.flap_d / 2.0
    return cq.Workplane("XY").circle(fr).circle(fr - 0.010).extrude(0.003, both=True)


# ---------------------------------------------------------------------------
# panel_frame: host + opening bezel + hardware + optional add-on fixed geometry.
# ---------------------------------------------------------------------------
def _build_frame(model: ArticulatedObject, r: ResolvedCatFlapConfig, mats: dict) -> object:
    frame = model.part("panel_frame")

    # --- host_context ---
    if r.host_context == "door_thin_panel":
        frame.visual(
            mesh_from_cadquery(_panel_cutout(r), "door_panel_with_opening", tolerance=0.0008),
            origin=Origin(rpy=(-math.pi / 2.0, 0.0, 0.0)),
            material=mats["host"],
            name="door_panel", material_class_id=("glass.frosted_smooth" if r.palette_style in {"warm_white", "charcoal_wood", "graphite_glass", "cream_wood"} else "metal.brushed_silver"),
        )
    else:
        _build_tunnel_liner(frame, r, mats)

    # --- opening_form: front trim bezel + inner seal ---
    trim = _make_bezel(
        r,
        opening=(r.opening_w, r.opening_h),
        outer=(r.frame_w, r.frame_h),
        depth=FRAME_D,
    )
    frame.visual(
        mesh_from_geometry(trim, "front_trim_bezel"),
        origin=Origin(xyz=(0.0, FRONT_Y + FRAME_D / 2.0, 0.0), rpy=(-math.pi / 2.0, 0.0, 0.0)),
        material=mats["trim"],
        name="front_trim", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"warm_white", "charcoal_wood", "graphite_glass", "cream_wood"} else "metal.brushed_silver"),
    )
    seal = _make_bezel(
        r,
        opening=(r.opening_w - 0.018, r.opening_h - 0.018),
        outer=(r.opening_w + 0.014, r.opening_h + 0.014),
        depth=0.006,
        opening_corner=0.014,
        outer_corner=0.020,
    )
    frame.visual(
        mesh_from_geometry(seal, "inner_rubber_seal"),
        origin=Origin(xyz=(0.0, FRAME_FRONT_Y + 0.003, 0.0), rpy=(-math.pi / 2.0, 0.0, 0.0)),
        material=mats["seal"],
        name="inner_seal", material_class_id="rubber.smooth_plain",
    )

    _build_screws(frame, r, mats)
    _build_hinge_hardware(frame, r, mats, hinge_z=r.hinge_z, y=HINGE_Y, x_lug=None, suffix="")
    _build_magnet(frame, r, mats, hinge_z=r.hinge_z, front=True)

    # rear hinge + magnet hardware for a double flap (tunnel only)
    if r.n_flaps == 2:
        rear_y = -TUNNEL_DEPTH - 0.006
        _build_hinge_hardware(
            frame, r, mats, hinge_z=r.hinge_z, y=rear_y, x_lug=None, suffix="_rear"
        )
        _build_magnet(frame, r, mats, hinge_z=r.hinge_z, front=False)

    if r.closure_lock == "slide_lock":
        _build_guide_rails(frame, r, mats)
    if r.control_module == "electronic_microchip":
        _build_electronic_fixed(frame, r, mats)

    return frame


def _build_tunnel_liner(frame, r: ResolvedCatFlapConfig, mats: dict) -> None:
    """4-wall through-wall liner (rounded_rect only) + a rear_frame ring."""
    liner = mats["liner"]
    hw = r.opening_w / 2.0
    hh = r.opening_h / 2.0
    wall_t = 0.020
    front_y = 0.030  # overlaps into the front trim ring
    rear_y = -TUNNEL_DEPTH
    tunnel_len = front_y - rear_y + 0.010
    cy = (front_y + rear_y) / 2.0
    frame.visual(
        Box((wall_t, tunnel_len, r.opening_h)),
        origin=Origin(xyz=(-(hw + wall_t / 2.0), cy, 0.0)),
        material=liner,
        name="tunnel_wall_0", material_class_id="plastic.opaque_generic",
    )
    frame.visual(
        Box((wall_t, tunnel_len, r.opening_h)),
        origin=Origin(xyz=(hw + wall_t / 2.0, cy, 0.0)),
        material=liner,
        name="tunnel_wall_1", material_class_id="plastic.opaque_generic",
    )
    frame.visual(
        Box((r.opening_w + 2 * wall_t, tunnel_len, wall_t)),
        origin=Origin(xyz=(0.0, cy, hh + wall_t / 2.0)),
        material=liner,
        name="tunnel_wall_2", material_class_id="plastic.opaque_generic",
    )
    frame.visual(
        Box((r.opening_w + 2 * wall_t, tunnel_len, wall_t)),
        origin=Origin(xyz=(0.0, cy, -(hh + wall_t / 2.0))),
        material=liner,
        name="tunnel_wall_3", material_class_id="plastic.opaque_generic",
    )
    rear = _make_bezel(
        r,
        opening=(r.opening_w, r.opening_h),
        outer=(r.frame_w, r.frame_h),
        depth=FRAME_D,
    )
    frame.visual(
        mesh_from_geometry(rear, "rear_frame_bezel"),
        origin=Origin(xyz=(0.0, rear_y - FRAME_D / 2.0, 0.0), rpy=(-math.pi / 2.0, 0.0, 0.0)),
        material=mats["trim"],
        name="rear_frame", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"warm_white", "charcoal_wood", "graphite_glass", "cream_wood"} else "metal.brushed_silver"),
    )


def _build_screws(frame, r: ResolvedCatFlapConfig, mats: dict) -> None:
    metal = mats["metal"]
    seal = mats["seal"]
    if r.is_round:
        rad = r.frame_od / 2.0 - 0.015
        positions = [
            (rad * math.cos(math.radians(a)), rad * math.sin(math.radians(a)))
            for a in (45, 135, 225, 315)
        ]
    else:
        cx = r.frame_w / 2.0 - 0.028
        cz = r.frame_h / 2.0 - 0.034
        positions = [(-cx, cz), (cx, cz), (-cx, -cz), (cx, -cz)]
        if r.n_screws == 6:
            mx = r.frame_w / 2.0 - 0.016
            positions += [(-mx, 0.0), (mx, 0.0)]
    for i, (x, z) in enumerate(positions):
        frame.visual(
            Cylinder(radius=0.0115, length=0.005),
            origin=Origin(xyz=(x, FRAME_FRONT_Y + 0.0025, z), rpy=(-math.pi / 2.0, 0.0, 0.0)),
            material=metal,
            name=f"screw_head_{i}", material_class_id="metal.stainless_matte",
        )
        frame.visual(
            Box((0.018, 0.0016, 0.0030)),
            origin=Origin(xyz=(x, FRAME_FRONT_Y + 0.0053, z), rpy=(0.0, 0.0, math.pi / 9.0)),
            material=seal,
            name=f"screw_slot_{i}", material_class_id="metal.blackened_gunmetal",
        )


def _build_hinge_hardware(
    frame, r: ResolvedCatFlapConfig, mats: dict, *, hinge_z: float, y: float, x_lug, suffix: str
) -> None:
    metal = mats["metal"]
    trim = mats["trim"]
    lug_x = 0.080 if r.is_round else 0.137
    pin_len = 0.18 if r.is_round else 0.282
    frame.visual(
        Cylinder(radius=0.004, length=pin_len),
        origin=Origin(xyz=(0.0, y, hinge_z), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=metal,
        name=f"hinge_pin{suffix}", material_class_id="metal.steel_bare",
    )
    for idx, xs in enumerate((-lug_x, lug_x)):
        frame.visual(
            Box((0.026, 0.018, 0.040)),
            origin=Origin(xyz=(xs, y - 0.005 if suffix else FRAME_FRONT_Y + 0.001, hinge_z - 0.006)),
            material=trim,
            name=f"hinge_lug{suffix}_{idx}", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"warm_white", "charcoal_wood", "graphite_glass", "cream_wood"} else "metal.brushed_silver"),
        )


def _build_magnet(frame, r: ResolvedCatFlapConfig, mats: dict, *, hinge_z: float, front: bool) -> None:
    magnet = mats["magnet"]
    suffix = "" if front else "_rear"
    y = (FRAME_FRONT_Y + 0.003) if front else (-TUNNEL_DEPTH - 0.003)
    frame_magnet_z = hinge_z + PANEL_TOP_Z - r.flap_h + 0.028 - 0.006
    opening_bottom = -r.opening_h / 2.0 if not r.is_round else -r.opening_d / 2.0
    mount_center_z = (opening_bottom + frame_magnet_z) / 2.0
    mount_h = abs(frame_magnet_z - opening_bottom) + 0.020
    frame.visual(
        Box((0.024, 0.006, mount_h)),
        origin=Origin(xyz=(0.0, y, mount_center_z)),
        material=magnet,
        name=f"magnet_mount{suffix}", material_class_id="metal.blackened_gunmetal",
    )
    frame.visual(
        Box((0.058, 0.006, 0.020)),
        origin=Origin(xyz=(0.0, y, frame_magnet_z)),
        material=magnet,
        name=f"frame_magnet{suffix}", material_class_id="metal.blackened_gunmetal",
    )


# ---------------------------------------------------------------------------
# Flap(s): top-hinged swing, built CLOSED at q=0.
# ---------------------------------------------------------------------------
def _build_flap(
    model: ArticulatedObject,
    frame,
    r: ResolvedCatFlapConfig,
    mats: dict,
    *,
    index: int,
    hinge_y: float,
    y_sign: float,
) -> None:
    flap = model.part(f"flap_{index}")
    edge = mats["flap_edge"]
    flap_mat = mats["flap"]
    magnet = mats["magnet"]

    def sy(v: float) -> float:
        return v * y_sign

    if r.is_round:
        fr = r.flap_d / 2.0
        disc_center_z = -fr
        flap.visual(
            Cylinder(radius=0.010, length=0.120),
            origin=Origin(rpy=(0.0, math.pi / 2.0, 0.0)),
            material=edge,
            name="hinge_sleeve", material_class_id=("plastic.frosted_translucent" if r.palette_style in {"warm_white", "charcoal_wood", "graphite_glass", "cream_wood"} else "metal.brushed_silver"),
        )
        flap.visual(
            Box((0.060, 0.006, 0.020)),
            origin=Origin(xyz=(0.0, sy(0.002), -0.010)),
            material=edge,
            name="sleeve_web", material_class_id=("plastic.frosted_translucent" if r.palette_style in {"warm_white", "charcoal_wood", "graphite_glass", "cream_wood"} else "metal.brushed_silver"),
        )
        flap.visual(
            mesh_from_cadquery(_flap_disc(r), "flap_translucent_disc", tolerance=0.0006),
            origin=Origin(xyz=(0.0, sy(0.002), disc_center_z), rpy=(-math.pi / 2.0, 0.0, 0.0)),
            material=flap_mat,
            name="translucent_panel", material_class_id="plastic.frosted_translucent",
        )
        flap.visual(
            mesh_from_cadquery(_edge_ring(r), "flap_edge_ring", tolerance=0.0006),
            origin=Origin(xyz=(0.0, sy(0.004), disc_center_z), rpy=(-math.pi / 2.0, 0.0, 0.0)),
            material=edge,
            name="edge_ring", material_class_id=("plastic.frosted_translucent" if r.palette_style in {"warm_white", "charcoal_wood", "graphite_glass", "cream_wood"} else "metal.brushed_silver"),
        )
        flap.visual(
            Box((0.052, 0.006, 0.018)),
            origin=Origin(xyz=(0.0, sy(0.007), disc_center_z - fr + 0.028)),
            material=magnet,
            name="flap_magnet", material_class_id="metal.blackened_gunmetal",
        )
    else:
        fw = r.flap_w
        fh = r.flap_h
        panel_center_z = PANEL_TOP_Z - fh / 2.0
        flap.visual(
            Cylinder(radius=0.010, length=fw + 0.012),
            origin=Origin(rpy=(0.0, math.pi / 2.0, 0.0)),
            material=edge,
            name="hinge_sleeve", material_class_id=("plastic.frosted_translucent" if r.palette_style in {"warm_white", "charcoal_wood", "graphite_glass", "cream_wood"} else "metal.brushed_silver"),
        )
        flap.visual(
            Box((fw - 0.016, 0.004, fh - 0.020)),
            origin=Origin(xyz=(0.0, sy(0.002), panel_center_z)),
            material=flap_mat,
            name="translucent_panel", material_class_id="plastic.frosted_translucent",
        )
        flap.visual(
            Box((fw, 0.008, 0.010)),
            origin=Origin(xyz=(0.0, sy(0.005), -0.007)),
            material=edge,
            name="sleeve_web", material_class_id=("plastic.frosted_translucent" if r.palette_style in {"warm_white", "charcoal_wood", "graphite_glass", "cream_wood"} else "metal.brushed_silver"),
        )
        flap.visual(
            Box((fw, 0.008, RIM_T)),
            origin=Origin(xyz=(0.0, sy(0.005), PANEL_TOP_Z - RIM_T / 2.0)),
            material=edge,
            name="top_lip", material_class_id=("plastic.frosted_translucent" if r.palette_style in {"warm_white", "charcoal_wood", "graphite_glass", "cream_wood"} else "metal.brushed_silver"),
        )
        flap.visual(
            Box((fw, 0.008, RIM_T)),
            origin=Origin(xyz=(0.0, sy(0.005), PANEL_TOP_Z - fh + RIM_T / 2.0)),
            material=edge,
            name="bottom_lip", material_class_id=("plastic.frosted_translucent" if r.palette_style in {"warm_white", "charcoal_wood", "graphite_glass", "cream_wood"} else "metal.brushed_silver"),
        )
        for idx, xs in enumerate((-(fw / 2.0 - RIM_T / 2.0), fw / 2.0 - RIM_T / 2.0)):
            flap.visual(
                Box((RIM_T, 0.008, fh)),
                origin=Origin(xyz=(xs, sy(0.005), PANEL_TOP_Z - fh / 2.0)),
                material=edge,
                name=f"side_lip_{idx}", material_class_id=("plastic.frosted_translucent" if r.palette_style in {"warm_white", "charcoal_wood", "graphite_glass", "cream_wood"} else "metal.brushed_silver"),
            )
        flap.visual(
            Box((0.052, 0.006, 0.018)),
            origin=Origin(xyz=(0.0, sy(0.007), PANEL_TOP_Z - fh + 0.028)),
            material=magnet,
            name="flap_magnet", material_class_id="metal.blackened_gunmetal",
        )

    joint = model.articulation(
        f"frame_to_flap_{index}",
        ArticulationType.REVOLUTE,
        parent=frame,
        child=flap,
        origin=Origin(xyz=(0.0, hinge_y, r.hinge_z)),
        axis=(y_sign, 0.0, 0.0),
        motion_limits=MotionLimits(effort=1.5, velocity=4.0, lower=0.0, upper=r.flap_swing),
    )
    joint.meta["role"] = f"top-hinged cat-flap swing leaf {index}"


# ---------------------------------------------------------------------------
# closure_lock = slide_lock: guide rails (frame) + lock_slider (PRISMATIC).
# ---------------------------------------------------------------------------
def _build_guide_rails(frame, r: ResolvedCatFlapConfig, mats: dict) -> None:
    trim = mats["trim"]
    rail_w = 0.014
    rail_lip_t = 0.004
    rail_h = r.frame_h + 0.035
    rail_x = r.opening_w / 2.0 + rail_w / 2.0 - 0.003
    rail_lip_y = FRAME_FRONT_Y + 0.001 + 0.005 + rail_lip_t / 2.0
    for idx, xs in enumerate((-1.0, 1.0)):
        frame.visual(
            Box((rail_w, rail_lip_t, rail_h)),
            origin=Origin(xyz=(xs * rail_x, rail_lip_y, 0.0)),
            material=trim,
            name=f"guide_rail_{idx}", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"warm_white", "charcoal_wood", "graphite_glass", "cream_wood"} else "metal.brushed_silver"),
        )


def _build_slide_lock(model: ArticulatedObject, frame, r: ResolvedCatFlapConfig, mats: dict) -> None:
    slider_mat = mats["slider"]
    slider_w = r.opening_w
    slider_h = r.opening_h
    slider_t = 0.005
    slider_y = FRAME_FRONT_Y + 0.001 + slider_t / 2.0
    retracted_z = r.frame_h / 2.0 + slider_h / 2.0 + 0.010

    lock_slider = model.part("lock_slider")
    lock_slider.visual(
        Box((slider_w, slider_t, slider_h)),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material=slider_mat,
        name="lock_panel", material_class_id="plastic.opaque_generic",
    )
    lock_slider.visual(
        Box((0.060, slider_t + 0.004, 0.018)),
        origin=Origin(xyz=(0.0, 0.0, -slider_h / 2.0 + 0.009)),
        material=slider_mat,
        name="slider_grip_tab", material_class_id="plastic.opaque_generic",
    )
    joint = model.articulation(
        "frame_to_lock_slider",
        ArticulationType.PRISMATIC,
        parent=frame,
        child=lock_slider,
        origin=Origin(xyz=(0.0, slider_y, retracted_z)),
        axis=(0.0, 0.0, -1.0),
        motion_limits=MotionLimits(effort=8.0, velocity=0.20, lower=0.0, upper=r.slide_travel),
    )
    joint.meta["role"] = "manual 4-way lock slider blocking the flap"


# ---------------------------------------------------------------------------
# control_module = electronic_microchip: fixed housing/antenna/etc + mode_button.
# ---------------------------------------------------------------------------
def _build_electronic_fixed(frame, r: ResolvedCatFlapConfig, mats: dict) -> None:
    housing_mat = mats["housing"]
    batt_mat = mats["batt"]
    antenna_mat = mats["antenna"]
    led_mat = mats["led"]
    dark = mats["seal"]

    housing_w = min(0.260, r.frame_w - 0.06)
    housing_h = 0.055
    housing_d = 0.022
    housing_bottom_z = r.hinge_z + 0.016
    housing_z = housing_bottom_z + housing_h / 2.0
    housing_y = FRAME_FRONT_Y + housing_d / 2.0

    frame.visual(
        Box((housing_w, housing_d, housing_h)),
        origin=Origin(xyz=(0.0, housing_y, housing_z)),
        material=housing_mat,
        name="sensor_housing", material_class_id="plastic.opaque_glossy_molded",
    )
    frame.visual(
        Box((housing_w + 0.016, 0.006, housing_h + 0.010)),
        origin=Origin(xyz=(0.0, FRAME_FRONT_Y - 0.003, housing_z)),
        material=housing_mat,
        name="housing_flange", material_class_id="plastic.opaque_glossy_molded",
    )
    batt_w, batt_h, batt_t = 0.058, 0.034, 0.003
    frame.visual(
        Box((batt_w, batt_t, batt_h)),
        origin=Origin(xyz=(0.050, housing_y + housing_d / 2.0 + batt_t / 2.0, housing_z - 0.004)),
        material=batt_mat,
        name="battery_cover", material_class_id="plastic.opaque_glossy_molded",
    )
    frame.visual(
        Box((0.012, 0.002, 0.008)),
        origin=Origin(
            xyz=(0.050, housing_y + housing_d / 2.0 + batt_t + 0.001, housing_z + batt_h / 2.0 - 0.008)
        ),
        material=dark,
        name="battery_latch", material_class_id="plastic.opaque_generic",
    )

    # antenna ring follows the opening form (host-conformal, Rule 4)
    antenna_border = 0.008
    if r.is_round:
        inner = r.opening_d + 0.004
        antenna = _make_bezel(
            r,
            opening=(inner, inner),
            outer=(inner + 2 * antenna_border, inner + 2 * antenna_border),
            depth=0.005,
        )
    else:
        inner_w = r.opening_w + 0.004
        inner_h = r.opening_h + 0.004
        antenna = _make_bezel(
            r,
            opening=(inner_w, inner_h),
            outer=(inner_w + 2 * antenna_border, inner_h + 2 * antenna_border),
            depth=0.005,
            opening_corner=0.017,
            outer_corner=0.023,
        )
    frame.visual(
        mesh_from_geometry(antenna, "rfid_antenna_ring"),
        origin=Origin(xyz=(0.0, FRAME_FRONT_Y + 0.0025, 0.0), rpy=(-math.pi / 2.0, 0.0, 0.0)),
        material=antenna_mat,
        name="antenna_ring", material_class_id="tech.circuit_board",
    )
    frame.visual(
        Cylinder(radius=0.004, length=0.002),
        origin=Origin(
            xyz=(0.090, housing_y + housing_d / 2.0 + 0.001, housing_z + 0.012),
            rpy=(-math.pi / 2.0, 0.0, 0.0),
        ),
        material=led_mat,
        name="led_indicator", material_class_id="tech.emissive_surface",
    )
    frame.visual(
        Cylinder(radius=0.013, length=0.004),
        origin=Origin(
            xyz=(-0.090, housing_y + housing_d / 2.0 + 0.002, housing_z),
            rpy=(-math.pi / 2.0, 0.0, 0.0),
        ),
        material=housing_mat,
        name="button_boss", material_class_id="plastic.opaque_glossy_molded",
    )


def _build_mode_button(model: ArticulatedObject, frame, r: ResolvedCatFlapConfig, mats: dict) -> None:
    button_mat = mats["button"]
    button_x = -0.090
    button_r = 0.010
    housing_h = 0.055
    housing_bottom_z = r.hinge_z + 0.016
    housing_z = housing_bottom_z + housing_h / 2.0
    housing_d = 0.022
    housing_y = FRAME_FRONT_Y + housing_d / 2.0

    mode_button = model.part("mode_button")
    dial = KnobGeometry(
        button_r * 2.0,
        0.008,
        body_style="cylindrical",
        grip=KnobGrip(style="ribbed", count=12, depth=0.0006, width=0.0012),
        indicator=KnobIndicator(style="dot", mode="raised", angle_deg=0.0),
        center=False,
    )
    mode_button.visual(
        mesh_from_geometry(dial, "mode_dial_cap"),
        origin=Origin(rpy=(-math.pi / 2.0, 0.0, 0.0)),
        material=button_mat,
        name="mode_dial", material_class_id="tech.control_interface",
    )
    joint = model.articulation(
        "housing_to_mode_button",
        ArticulationType.REVOLUTE,
        parent=frame,
        child=mode_button,
        origin=Origin(xyz=(button_x, housing_y + housing_d / 2.0 + 0.004, housing_z)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=0.3, velocity=2.0, lower=0.0, upper=math.pi * 1.5),
    )
    joint.meta["role"] = "microchip mode selector rotary dial"


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def build_cat_flap(
    config: CatFlapConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={
            "class": "Pet_Animal related/Cat flap",
            "description": (
                "A framed pet-sized opening in a host panel/door/wall closed by a "
                "top-hinged swing flap the animal pushes through."
            ),
        },
    )
    mats = {
        role: model.material(f"catflap_{role}_{r.palette_style}", rgba=rgba)
        for role, rgba in _palette_rgba(r.palette_style).items()
    }

    frame = _build_frame(model, r, mats)

    # front flap (always) swings out +Y; rear flap (double) swings in -Y.
    _build_flap(model, frame, r, mats, index=0, hinge_y=HINGE_Y, y_sign=1.0)
    if r.n_flaps == 2:
        _build_flap(
            model, frame, r, mats, index=1, hinge_y=-TUNNEL_DEPTH - 0.006, y_sign=-1.0
        )

    if r.closure_lock == "slide_lock":
        _build_slide_lock(model, frame, r, mats)
    if r.control_module == "electronic_microchip":
        _build_mode_button(model, frame, r, mats)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_cat_flap(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_cat_flap(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
_FLAP_CLOSED_ELEMS = (
    "translucent_panel",
    "sleeve_web",
    "hinge_sleeve",
    "top_lip",
    "bottom_lip",
    "side_lip_0",
    "side_lip_1",
    "edge_ring",
)
_FRAME_CLOSED_ELEMS = ("front_trim", "inner_seal", "rear_frame")


def _allow_flap(ctx, model, r: ResolvedCatFlapConfig, *, index: int, suffix: str) -> None:
    fname = f"flap_{index}"
    frame_elems = [e for e in _FRAME_CLOSED_ELEMS if e in _visual_names(model, "panel_frame")]
    flap_elems = [e for e in _FLAP_CLOSED_ELEMS if e in _visual_names(model, fname)]
    # closed flap beds against the trim / seal / rear ring at the opening
    for fe in flap_elems:
        for pe in frame_elems:
            ctx.allow_overlap(
                fname, "panel_frame", elem_a=fe, elem_b=pe,
                reason="Closed flap frame beds into the opening trim / seal at rest.",
            )
    # hinge pin captured inside the flap hinge sleeve
    for pe in (f"hinge_pin{suffix}", f"hinge_lug{suffix}_0", f"hinge_lug{suffix}_1"):
        ctx.allow_overlap(
            "panel_frame", fname, elem_a=pe, elem_b="hinge_sleeve",
            reason="The hinge pin/lug is captured inside the flap hinge sleeve proxy.",
        )
    # bottom magnet keeper meets the frame magnet catch when closed
    for pe in (f"frame_magnet{suffix}", f"magnet_mount{suffix}"):
        ctx.allow_overlap(
            fname, "panel_frame", elem_a="flap_magnet", elem_b=pe,
            reason="Closed flap bottom magnet meets the fixed frame magnet catch.",
        )
    # antenna ring wraps the opening; the hinge sleeve passes through its top border
    if "antenna_ring" in _visual_names(model, "panel_frame"):
        ctx.allow_overlap(
            fname, "panel_frame", elem_a="hinge_sleeve", elem_b="antenna_ring",
            reason="RFID antenna coil wraps the opening; the hinge sleeve passes its top border.",
        )
    # a flap hung inside a through-wall tunnel liner beds its hinge line / edges
    # against the liner walls at the top/bottom of the opening.
    if r.host_context == "wall_tunnel_liner":
        for fe in ("hinge_sleeve", "top_lip", "bottom_lip", "flap_magnet"):
            if fe in flap_elems or fe == "flap_magnet":
                for k in range(4):
                    ctx.allow_overlap(
                        fname, "panel_frame", elem_a=fe, elem_b=f"tunnel_wall_{k}",
                        reason="Flap hinge line / edges bed against the tunnel liner walls at the opening edge.",
                    )


def _allow_slide_lock(ctx, model, r: ResolvedCatFlapConfig) -> None:
    frame_names = _visual_names(model, "panel_frame")
    slider_elems = ("lock_panel", "slider_grip_tab")
    for se in slider_elems:
        for pe in (
            "inner_seal",
            "magnet_mount",
            "frame_magnet",
            "front_trim",
            "antenna_ring",
            "hinge_pin",
            "hinge_lug_0",
            "hinge_lug_1",
        ):
            if pe in frame_names:
                ctx.allow_overlap(
                    "lock_slider", "panel_frame", elem_a=se, elem_b=pe,
                    reason="Deployed lock panel slides over the opening seal / magnet / trim to block it.",
                )
        for idx in (0, 1):
            ctx.allow_overlap(
                "lock_slider", "panel_frame", elem_a=se, elem_b=f"guide_rail_{idx}",
                reason="Lock panel rides captured behind the side guide rail lip.",
            )
    # slider blocks the (closed) front flap -- that is the whole point.
    for se in slider_elems:
        for fe in ("translucent_panel", "top_lip", "bottom_lip", "hinge_sleeve"):
            if fe in _visual_names(model, "flap_0"):
                ctx.allow_overlap(
                    "lock_slider", "flap_0", elem_a=se, elem_b=fe,
                    reason="Deployed lock panel covers the closed swing flap it is meant to block.",
                )


def _visual_names(model, part_name: str) -> set[str]:
    part = model.get_part(part_name)
    if part is None:
        return set()
    return {v.name for v in part.visuals}


def run_cat_flap_tests(object_model: ArticulatedObject, config: CatFlapConfig) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)

    # ---- captured-pin / seating allowances (element-scoped). ----
    _allow_flap(ctx, object_model, r, index=0, suffix="")
    if r.n_flaps == 2:
        _allow_flap(ctx, object_model, r, index=1, suffix="_rear")
    if r.closure_lock == "slide_lock":
        _allow_slide_lock(ctx, object_model, r)

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_joint_mating_has_gap()

    # ---- identity ----
    part_names = {p.name for p in object_model.parts}
    ctx.check(
        "classified as cat flap with a grounded panel_frame root",
        object_model.meta.get("class") == "Pet_Animal related/Cat flap"
        and "panel_frame" in part_names,
        details=f"class={object_model.meta.get('class')} parts={sorted(part_names)}",
    )

    # ---- every seed has at least one real opening joint (the swing flap) ----
    movable = [
        j
        for j in object_model.articulations
        if j.articulation_type in (ArticulationType.REVOLUTE, ArticulationType.PRISMATIC)
    ]
    ctx.check(
        "has at least one operable (non-fixed) joint",
        len(movable) >= 1,
        details=f"movable joints={[j.name for j in movable]}",
    )

    # ---- flap(s): top-hinge REVOLUTE + swings open (out of the closed plane, up) ----
    for i in range(r.n_flaps):
        flap = object_model.get_part(f"flap_{i}")
        hinge = object_model.get_articulation(f"frame_to_flap_{i}")
        ctx.check(
            f"flap_{i} on a top-hinge REVOLUTE about X",
            flap is not None
            and hinge is not None
            and hinge.articulation_type == ArticulationType.REVOLUTE
            and abs(hinge.axis[0]) > 0.9,
            details=f"axis={None if hinge is None else tuple(hinge.axis)}",
        )
        if flap is None or hinge is None:
            continue
        closed = ctx.part_element_world_aabb(flap, elem="flap_magnet")
        with ctx.pose({hinge: r.flap_swing * 0.9}):
            opened = ctx.part_element_world_aabb(flap, elem="flap_magnet")
        if closed is not None and opened is not None:
            closed_cy = (closed[0][1] + closed[1][1]) * 0.5
            open_cy = (opened[0][1] + opened[1][1]) * 0.5
            y_dir = 1.0 if i == 0 else -1.0
            ctx.check(
                f"flap_{i} swings open out of the closed plane and lifts",
                (open_cy - closed_cy) * y_dir > 0.05 and opened[1][2] > closed[1][2] + 0.03,
                details=f"closed_cy={closed_cy:.3f} open_cy={open_cy:.3f} "
                f"closed_top_z={closed[1][2]:.3f} open_top_z={opened[1][2]:.3f}",
            )

    # ---- opening_form: circular keeps the disc/edge-ring mesh (Rule 3) ----
    frame = object_model.get_part("panel_frame")
    if r.is_round:
        disc = object_model.get_part("flap_0").get_visual("translucent_panel")
        ring = object_model.get_part("flap_0").get_visual("edge_ring")
        ctx.check(
            "circular flap keeps disc + edge-ring meshes",
            disc is not None and ring is not None,
            details="round flap must keep _flap_disc / _edge_ring meshes (not boxes)",
        )

    # ---- host_context: wall_tunnel_liner has a deep liner + rear frame ----
    if r.host_context == "wall_tunnel_liner":
        names = _visual_names(object_model, "panel_frame")
        ctx.check(
            "wall_tunnel_liner emits 4 tunnel walls + a rear_frame ring",
            all(f"tunnel_wall_{k}" in names for k in range(4)) and "rear_frame" in names,
            details=f"has={sorted(n for n in names if n.startswith(('tunnel_wall', 'rear_frame')))}",
        )

    # ---- closure_lock: slide_lock adds a PRISMATIC slider that deploys down ----
    if r.closure_lock == "slide_lock":
        slider = object_model.get_part("lock_slider")
        slide = object_model.get_articulation("frame_to_lock_slider")
        ctx.check(
            "slide_lock: lock_slider on a PRISMATIC joint down the opening",
            slider is not None
            and slide is not None
            and slide.articulation_type == ArticulationType.PRISMATIC
            and abs(slide.axis[2]) > 0.9,
            details=f"type={getattr(slide, 'articulation_type', None)}",
        )
        p0 = ctx.part_world_position(slider)
        with ctx.pose({slide: r.slide_travel}):
            p1 = ctx.part_world_position(slider)
        if p0 is not None and p1 is not None:
            ctx.check(
                "deployed slider translates down over the opening",
                p1[2] < p0[2] - 0.20,
                details=f"retracted_z={p0[2]:.3f} deployed_z={p1[2]:.3f}",
            )

    # ---- control_module: electronic module present + dial rotates in place ----
    if r.control_module == "electronic_microchip":
        names = _visual_names(object_model, "panel_frame")
        ctx.check(
            "electronic module: sensor_housing + antenna_ring + battery_cover present",
            {"sensor_housing", "antenna_ring", "battery_cover"} <= names,
            details=f"has={sorted(n for n in names if n in {'sensor_housing', 'antenna_ring', 'battery_cover'})}",
        )
        button = object_model.get_part("mode_button")
        mj = object_model.get_articulation("housing_to_mode_button")
        rest = ctx.part_world_position(button)
        with ctx.pose({mj: math.pi / 2.0}):
            turned = ctx.part_world_position(button)
        if rest is not None and turned is not None:
            ctx.check(
                "mode dial rotates in place (no translation)",
                abs(turned[0] - rest[0]) < 0.003 and abs(turned[2] - rest[2]) < 0.003,
                details=f"rest={rest} turned={turned}",
            )

    # ---- Rule 5: sampled-pose collision across all opening joints. ----
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=64, ignore_fixed=True)

    # ---- slot_choices recorded. ----
    ctx.check(
        "slot_choices recorded with multiplicity encoded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    return ctx.report()


__all__ = (
    "CatFlapConfig",
    "ResolvedCatFlapConfig",
    "build_cat_flap",
    "build_seeded_cat_flap",
    "config_from_seed",
    "resolve_config",
    "run_cat_flap_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
)
