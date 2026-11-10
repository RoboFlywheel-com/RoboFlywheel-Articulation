# SPDX-License-Identifier: Apache-2.0

"""Industrial / Industrial vice - modular procedural template.

A bench / machinist vise: a bolt-down ``base`` (round cast swivel turntable or
rectangular plate) carrying a heavy ``body`` casting (rear anvil + fixed jaw
plate), a sliding ``front_jaw`` on a horizontal PRISMATIC slide, and a
``lead_screw`` + handle that spins / cranks the jaw closed. A ``side_lock``
handle (parallel child of the base) locks the swivel turntable.

Slot graph (pattern = mixed: fixed serial spine + parallel side_lock child +
2 multiplicity axes ``lug_count`` / ``plate_screw_count``):

    base (root; round_base / rect_base)
        |-[base_to_body: REVOLUTE|CONTINUOUS|FIXED, Z]-> body (cast_body / welded_box_body)
        |     |-[body_to_front_jaw: PRISMATIC, X]-> front_jaw (flat_jaws / pipe_combo_jaws)
        |     |     |-[front_jaw_to_screw: CONTINUOUS|REVOLUTE, X]-> lead_screw (thandle_screw / cam_lever)
        |-[base_to_side_lock: REVOLUTE, Z; swivel mounts only]-> side_lock

Adapted per AUTHORING.md sec.A/sec.B from the confirmed 5-star Industrial-vice pool
(spec: specs_modular_v1/Industrial_Industrial_vice.md). All joints are emitted
manually (parallel-children idiom, same as
Urban_Environment_Tipping_Barrow): every slot declares only a ``downstream``
interface (re-export the base) so the assembler emits no auto chain joint.

Sources (model.py:Lx-Ly in the spec Module Source Index):
  S1  origin primary rec_industrial__...b597f2dc - round cast swivel base, cast
      arched body, flat jaws, T-handle CONTINUOUS screw, side swivel-lock.
  S2/S3 lugs_three / lugs_six - lug_count multiplicity.
  S4  rect_base          - rectangular flat plate base ((3)).
  S5  welded_box_body    - fabricated welded box body ((3)).
  S6  continuous_swivel  - CONTINUOUS 360 turntable ((2)).
  S7  fixed_base         - FIXED bolt-down mount, no side_lock ((1)/(2)).
  S8  pipe_jaws          - integral toothed pipe V-jaws ((3)/(1)).
  S9  plate_screws       - N indexed retaining screws per plate (mult/(4)).
  S10 lever_drive        - single cam lever, REVOLUTE screw arc ((2)/(3)).

Coordinate frame: Z-up. Base centered at origin. +X = toward the moving jaw /
handle. Each child part's local frame origin sits at its incoming joint origin
(URDF semantics), so part visuals are authored exactly as in the 5-star sources.
``size_scale`` scales every cadquery solid (about the part origin) plus all
Box / Cylinder / Sphere dims and joint origins uniformly.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from functools import lru_cache
from typing import Literal

import cadquery as cq

from agent.templates._modular import (
    InterfaceSpec,
    ModuleBuild,
    ModuleBuildContext,
    SlotSpec,
    assemble,
)
from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    MotionLimits,
    Origin,
    Sphere,
    TestContext,
    TestReport,
    mesh_from_cadquery,
)

# Modular template: sweep coverage uses module_topology_diversity.
__modular__ = True


BaseModule = Literal["round_base", "rect_base"]
BodyModule = Literal["cast_body", "welded_box_body"]
MountModule = Literal["revolute_swivel", "continuous_swivel", "fixed_mount"]
JawModule = Literal["flat_jaws", "pipe_combo_jaws"]
DriveModule = Literal["thandle_screw", "cam_lever"]
VicePalette = Literal[
    "classic_blue",
    "machinist_gray",
    "safety_red",
    "cast_black",
    "galv_silver",
    "hammertone_green",
]

_SWIVEL_MOUNTS = ("revolute_swivel", "continuous_swivel")

# Canonical dimensions (origin primary). boss_top: turntable boss top face = body
# seat plane; single-sourced so every base form exposes the same mount face.
BOSS_TOP = 0.065
BODY_SEAT_Z = 0.066   # body-local z of the front-jaw slide axis (from origin)
FRONT_X = 0.205       # body-local x of the front-jaw slide origin
SCREW_X = 0.055       # front_jaw-local x of the lead-screw origin


# --------------------------------------------------------------------------- #
# Palettes (>=6 colorways; painted main color + shared metal tokens)
# --------------------------------------------------------------------------- #

PALETTES: dict[str, dict[str, tuple[float, float, float, float]]] = {
    "classic_blue": {
        "paint": (0.005, 0.155, 0.470, 1.0),
        "steel": (0.72, 0.72, 0.69, 1.0),
        "dark": (0.05, 0.05, 0.045, 1.0),
        "bare": (0.52, 0.54, 0.55, 1.0),
    },
    "machinist_gray": {
        "paint": (0.40, 0.42, 0.45, 1.0),
        "steel": (0.70, 0.71, 0.69, 1.0),
        "dark": (0.06, 0.06, 0.07, 1.0),
        "bare": (0.55, 0.57, 0.58, 1.0),
    },
    "safety_red": {
        "paint": (0.60, 0.09, 0.09, 1.0),
        "steel": (0.73, 0.73, 0.70, 1.0),
        "dark": (0.05, 0.05, 0.05, 1.0),
        "bare": (0.54, 0.55, 0.56, 1.0),
    },
    "cast_black": {
        "paint": (0.09, 0.09, 0.10, 1.0),
        "steel": (0.68, 0.69, 0.67, 1.0),
        "dark": (0.02, 0.02, 0.02, 1.0),
        "bare": (0.50, 0.52, 0.53, 1.0),
    },
    "galv_silver": {
        "paint": (0.66, 0.68, 0.70, 1.0),
        "steel": (0.78, 0.79, 0.80, 1.0),
        "dark": (0.10, 0.11, 0.12, 1.0),
        "bare": (0.60, 0.62, 0.63, 1.0),
    },
    "hammertone_green": {
        "paint": (0.13, 0.32, 0.22, 1.0),
        "steel": (0.71, 0.72, 0.69, 1.0),
        "dark": (0.05, 0.06, 0.05, 1.0),
        "bare": (0.53, 0.55, 0.54, 1.0),
    },
}
PALETTE_NAMES = tuple(PALETTES.keys())


# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class IndustrialViceConfig:
    base_module: BaseModule = "round_base"
    body_module: BodyModule = "cast_body"
    mount_module: MountModule = "revolute_swivel"
    jaw_module: JawModule = "flat_jaws"
    drive_module: DriveModule = "thandle_screw"
    palette_style: VicePalette = "classic_blue"

    lug_count: int = 4           # round base mounting lugs; rect base -> 4 pads
    plate_screw_count: int = 3   # retaining screws per jaw plate

    size_scale: float = 1.0
    jaw_travel: float = 0.085    # PRISMATIC upper (m)
    swivel_range: float = 1.35   # revolute_swivel +/- bound (rad)
    screw_arc: float = 1.20      # cam_lever REVOLUTE +/- arc (rad)


@dataclass(frozen=True)
class ResolvedIndustrialViceConfig:
    base_module: BaseModule
    body_module: BodyModule
    mount_module: MountModule
    jaw_module: JawModule
    drive_module: DriveModule
    palette_style: str

    lug_count: int
    plate_screw_count: int

    size_scale: float
    jaw_travel: float
    swivel_range: float
    screw_arc: float

    # Derived mounting envelope (single-sourced; Contract 3c).
    boss_top: float

    palette: dict[str, tuple[float, float, float, float]]


def config_from_seed(seed: int) -> IndustrialViceConfig:
    """Deterministic procedural sampling.

    seed 0 is pinned to the origin primary combination (round_base x4 lugs +
    cast_body + revolute_swivel + flat_jaws x3 screws + thandle_screw,
    classic_blue) as a documented regression anchor; every other seed is fully
    procedural.
    """
    if seed == 0:
        return IndustrialViceConfig()

    rng = random.Random(seed)

    base_module: BaseModule = rng.choice(("round_base", "rect_base"))
    body_module: BodyModule = rng.choice(("cast_body", "welded_box_body"))
    mount_module: MountModule = rng.choice(
        ("revolute_swivel", "continuous_swivel", "fixed_mount")
    )
    jaw_module: JawModule = rng.choice(("flat_jaws", "pipe_combo_jaws"))
    drive_module: DriveModule = rng.choice(("thandle_screw", "cam_lever"))
    palette_style = rng.choice(PALETTE_NAMES)

    lug_count = rng.choices((3, 4, 6), weights=(0.25, 0.5, 0.25))[0]
    plate_screw_count = rng.choices((2, 3, 4), weights=(0.35, 0.30, 0.35))[0]

    size_scale = round(rng.uniform(0.90, 1.15), 4)
    jaw_travel = round(rng.uniform(0.060, 0.100), 4)
    swivel_range = round(rng.uniform(1.00, 1.45), 4)
    screw_arc = round(rng.uniform(0.90, 1.30), 4)

    return IndustrialViceConfig(
        base_module=base_module,
        body_module=body_module,
        mount_module=mount_module,
        jaw_module=jaw_module,
        drive_module=drive_module,
        palette_style=palette_style,
        lug_count=lug_count,
        plate_screw_count=plate_screw_count,
        size_scale=size_scale,
        jaw_travel=jaw_travel,
        swivel_range=swivel_range,
        screw_arc=screw_arc,
    )


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(float(v), hi))


def resolve_config(config: IndustrialViceConfig) -> ResolvedIndustrialViceConfig:
    if str(config.base_module) not in {"round_base", "rect_base"}:
        raise ValueError(f"Unsupported base_module: {config.base_module}")
    if str(config.body_module) not in {"cast_body", "welded_box_body"}:
        raise ValueError(f"Unsupported body_module: {config.body_module}")
    if str(config.mount_module) not in {
        "revolute_swivel",
        "continuous_swivel",
        "fixed_mount",
    }:
        raise ValueError(f"Unsupported mount_module: {config.mount_module}")
    if str(config.jaw_module) not in {"flat_jaws", "pipe_combo_jaws"}:
        raise ValueError(f"Unsupported jaw_module: {config.jaw_module}")
    if str(config.drive_module) not in {"thandle_screw", "cam_lever"}:
        raise ValueError(f"Unsupported drive_module: {config.drive_module}")
    if str(config.palette_style) not in PALETTES:
        raise ValueError(f"Unsupported palette_style: {config.palette_style}")

    size_scale = _clamp(config.size_scale, 0.90, 1.15)
    jaw_travel = _clamp(config.jaw_travel, 0.060, 0.100)
    swivel_range = _clamp(config.swivel_range, 1.00, 1.45)
    screw_arc = _clamp(config.screw_arc, 0.90, 1.30)

    # lug_count only for the round base; rect base uses 4 fixed corner pads.
    if config.base_module == "round_base":
        lug_count = int(config.lug_count) if int(config.lug_count) in (3, 4, 6) else 4
    else:
        lug_count = 4
    plate_screw_count = int(_clamp(config.plate_screw_count, 2, 4))

    return ResolvedIndustrialViceConfig(
        base_module=config.base_module,
        body_module=config.body_module,
        mount_module=config.mount_module,
        jaw_module=config.jaw_module,
        drive_module=config.drive_module,
        palette_style=config.palette_style,
        lug_count=lug_count,
        plate_screw_count=plate_screw_count,
        size_scale=size_scale,
        jaw_travel=jaw_travel,
        swivel_range=swivel_range,
        screw_arc=screw_arc,
        boss_top=BOSS_TOP * size_scale,
        palette=dict(PALETTES[config.palette_style]),
    )


# --------------------------------------------------------------------------- #
# Scaling helpers
# --------------------------------------------------------------------------- #


def _bx(a: float, b: float, c: float, s: float) -> Box:
    return Box((a * s, b * s, c * s))


def _cy(radius: float, length: float, s: float) -> Cylinder:
    return Cylinder(radius=radius * s, length=length * s)


def _sp(radius: float, s: float) -> Sphere:
    return Sphere(radius=radius * s)


def _o(x: float, y: float, z: float, s: float, rpy=(0.0, 0.0, 0.0)) -> Origin:
    return Origin(xyz=(x * s, y * s, z * s), rpy=rpy)


def _safe_fillet(shape: cq.Workplane, radius: float) -> cq.Workplane:
    try:
        return shape.edges().fillet(radius)
    except Exception:
        return shape


def _scaled_cq_mesh(wp: cq.Workplane, name: str, s: float, *, ang: float = 0.09):
    """Tessellate a cadquery workplane, scaling the solid about the part origin
    (no re-boolean) so size_scale stays cheap."""
    solid = wp.val()
    if abs(s - 1.0) > 1e-6:
        solid = solid.scale(s)
        wp = cq.Workplane(obj=solid)
    return mesh_from_cadquery(wp, name, tolerance=0.0008, angular_tolerance=ang)


# --------------------------------------------------------------------------- #
# Cadquery castings (nominal, unscaled; cached on discrete params)
# --------------------------------------------------------------------------- #


@lru_cache(maxsize=8)
def _round_base_casting(lug_count: int) -> cq.Workplane:
    """Round cast swivel base + N mounting lugs + turntable boss (origin S1;
    lug loop from lugs_three S2 / lugs_six S3)."""
    lug_r, lug_disc = 0.150, 0.040
    base = cq.Workplane("XY").circle(0.110).extrude(0.030)
    lug_xy = []
    for i in range(lug_count):
        ang = i * (2.0 * math.pi / lug_count)
        x, y = lug_r * math.cos(ang), lug_r * math.sin(ang)
        lug_xy.append((x, y))
        base = base.union(cq.Workplane("XY").center(x, y).circle(lug_disc).extrude(0.030))
    # Raised swivel turntable boss (top at BOSS_TOP=0.065) + shallow lower ring.
    base = base.union(cq.Workplane("XY").circle(0.088).extrude(0.035).translate((0.0, 0.0, 0.030)))
    base = base.union(cq.Workplane("XY").circle(0.125).extrude(0.010).translate((0.0, 0.0, 0.010)))
    for x, y in lug_xy:
        cutter = cq.Workplane("XY").center(x, y).circle(0.014).extrude(0.090).translate((0.0, 0.0, -0.015))
        base = base.cut(cutter)
    return _safe_fillet(base, 0.004)


@lru_cache(maxsize=2)
def _rect_base_casting() -> cq.Workplane:
    """Rectangular flat plate + 4 square corner pads + central turntable boss
    (rect_base S4)."""
    plate_z = 0.030
    base = cq.Workplane("XY").box(0.30, 0.20, plate_z).translate((0.0, 0.0, plate_z / 2.0))
    pads = ((0.145, 0.075), (0.145, -0.075), (-0.145, 0.075), (-0.145, -0.075))
    for x, y in pads:
        base = base.union(cq.Workplane("XY").box(0.058, 0.058, 0.032).translate((x, y, 0.016)))
    base = base.union(cq.Workplane("XY").circle(0.088).extrude(0.035).translate((0.0, 0.0, plate_z)))
    for x, y in pads:
        base = base.cut(cq.Workplane("XY").center(x, y).circle(0.014).extrude(0.090).translate((0.0, 0.0, -0.015)))
    return _safe_fillet(base, 0.004)


@lru_cache(maxsize=2)
def _cast_body_casting() -> cq.Workplane:
    """Cast arched vise body: side profile + seat disc + boolean throat + slide
    tunnel (origin S1)."""
    width = 0.160
    side_profile = [
        (-0.160, 0.000), (0.135, 0.000), (0.150, 0.050), (0.128, 0.128),
        (0.098, 0.198), (0.042, 0.256), (-0.095, 0.260), (-0.138, 0.224),
        (-0.158, 0.130),
    ]
    body = cq.Workplane("XZ").polyline(side_profile).close().extrude(width).translate((0.0, width / 2.0, 0.0))
    body = body.union(cq.Workplane("XY").circle(0.080).extrude(0.035))
    throat_rect = cq.Workplane("XZ").center(0.028, 0.125).rect(0.112, 0.128).extrude(width + 0.030).translate((0.0, width / 2.0 + 0.015, 0.0))
    throat_arch = cq.Workplane("XZ").center(0.030, 0.188).circle(0.056).extrude(width + 0.030).translate((0.0, width / 2.0 + 0.015, 0.0))
    slide_tunnel = cq.Workplane("XY").box(0.285, 0.078, 0.052).translate((0.000, 0.000, 0.066))
    body = body.cut(throat_rect).cut(throat_arch).cut(slide_tunnel)
    return _safe_fillet(body, 0.003)


@lru_cache(maxsize=2)
def _welded_box_body_casting() -> cq.Workplane:
    """Fabricated welded steel box body: flat L-profile, straight slide tunnel,
    no throat arch (welded_box_body S5)."""
    width = 0.160
    profile = [
        (-0.160, 0.000), (0.140, 0.000), (0.140, 0.100),
        (-0.020, 0.100), (-0.020, 0.260), (-0.160, 0.260),
    ]
    body = cq.Workplane("XZ").polyline(profile).close().extrude(width).translate((0.0, width / 2.0, 0.0))
    slide_tunnel = cq.Workplane("XY").box(0.330, 0.080, 0.054).translate((0.000, 0.0, 0.066))
    body = body.cut(slide_tunnel)
    return _safe_fillet(body, 0.002)


@lru_cache(maxsize=2)
def _front_jaw_casting() -> cq.Workplane:
    """Sliding front jaw casting with arched throat (origin S1)."""
    width = 0.156
    profile = [
        (-0.055, -0.020), (0.045, -0.020), (0.064, 0.042), (0.058, 0.177),
        (0.032, 0.224), (-0.035, 0.224), (-0.058, 0.166), (-0.052, 0.040),
    ]
    jaw = cq.Workplane("XZ").polyline(profile).close().extrude(width).translate((0.0, width / 2.0, 0.0))
    throat_rect = cq.Workplane("XZ").center(0.005, 0.102).rect(0.062, 0.102).extrude(width + 0.030).translate((0.0, width / 2.0 + 0.015, 0.0))
    throat_arch = cq.Workplane("XZ").center(0.005, 0.150).circle(0.034).extrude(width + 0.030).translate((0.0, width / 2.0 + 0.015, 0.0))
    jaw = jaw.cut(throat_rect).cut(throat_arch)
    return _safe_fillet(jaw, 0.003)


@lru_cache(maxsize=2)
def _pipe_v_jaw_casting() -> cq.Workplane:
    """Curved toothed pipe V-jaw (pipe_jaws S8)."""
    w, h, d = 0.085, 0.058, 0.024
    vd, vs, td, nt = 0.016, 0.018, 0.002, 5
    front_x, back_x = d / 2.0, -d / 2.0
    apex_x = front_x - vd
    upper_pts = []
    for i in range(1, nt * 2):
        frac = i / (nt * 2)
        x = front_x - vd * frac + (td if i % 2 == 1 else 0.0)
        upper_pts.append((x, vs * (1.0 - frac)))
    lower_pts = []
    for i in range(1, nt * 2):
        frac = i / (nt * 2)
        x = apex_x + vd * frac + (td if i % 2 == 1 else 0.0)
        lower_pts.append((x, -vs * frac))
    profile = [
        (back_x, h / 2.0), (front_x, h / 2.0), (front_x, vs), *upper_pts,
        (apex_x, 0.0), *lower_pts, (front_x, -vs), (front_x, -h / 2.0), (back_x, -h / 2.0),
    ]
    jaw = cq.Workplane("XZ").polyline(profile).close().extrude(w).translate((0.0, -w / 2.0, 0.0))
    curve_radius = 0.200
    cutter = cq.Workplane("XY").center(-curve_radius + d * 0.35, 0.0).circle(curve_radius).extrude(h + 0.020).translate((0.0, 0.0, -(h + 0.020) / 2.0))
    back_box = cq.Workplane("XY").box(d * 1.5, w + 0.020, h + 0.020).translate((-d * 0.6, 0.0, 0.0))
    jaw = jaw.cut(cutter.intersect(back_box))
    return _safe_fillet(jaw, 0.001)


# --------------------------------------------------------------------------- #
# Shared visual helpers
# --------------------------------------------------------------------------- #


def _add_plate_screws(part, s: float, *, screw_x: float, plate_center_z: float,
                      plate_height: float, name_prefix: str, n: int) -> None:
    """N retaining screws in a vertical column, evenly distributed within the
    plate's z extent (plate_screws S9)."""
    margin = plate_height / (n + 1)
    z_min = plate_center_z - plate_height / 2.0 + margin
    step = (plate_height - 2.0 * margin) / max(n - 1, 1)
    for i in range(n):
        z = z_min + i * step
        part.visual(
            _cy(0.007, 0.005, s),
            origin=_o(screw_x, 0.0, z, s, rpy=(0.0, math.pi / 2.0, 0.0)),
            material="dark",
            name=f"{name_prefix}_{i}", material_class_id="metal.blackened_gunmetal",
        )


def _base_downstream(r: ResolvedIndustrialViceConfig) -> InterfaceSpec:
    return InterfaceSpec(
        interface_name="downstream",
        part_name="base",
        visual_name="base_with_bolt_holes",
        face_side="positive_z",
        anchor_local=(0.0, 0.0, r.boss_top),
        contact_tol=0.004,
    )


# --------------------------------------------------------------------------- #
# Slot A - base (root, (3) + lug_count multiplicity)
# --------------------------------------------------------------------------- #


def _build_base(ctx: ModuleBuildContext) -> ModuleBuild:
    model = ctx.model
    r: ResolvedIndustrialViceConfig = ctx.config  # type: ignore[assignment]
    s = r.size_scale
    base = model.part("base", meta={"bolt_holes": r.lug_count})

    if r.base_module == "round_base":
        wp = _round_base_casting(r.lug_count)
    else:
        wp = _rect_base_casting()
    base.visual(
        _scaled_cq_mesh(wp, "base_with_bolt_holes", s),
        material="paint",
        name="base_with_bolt_holes", material_class_id="metal.paint_coated",
    )
    # Exposed-metal paint chips seated into the painted casting ((4)).
    # Positions kept inside both the round disc (r<0.110, outside boss r 0.088)
    # and the rectangular plate footprint (|x|<0.15, |y|<0.10); z straddles the
    # base top (0.030) so each chip embeds into the top face on both forms.
    base.visual(_bx(0.042, 0.008, 0.002, s), origin=_o(0.045, -0.085, 0.0295, s), material="bare", name="base_paint_chip_0", material_class_id="metal.cast_iron_bare")
    base.visual(_bx(0.030, 0.007, 0.002, s), origin=_o(-0.060, 0.070, 0.0295, s), material="bare", name="base_paint_chip_1", material_class_id="metal.cast_iron_bare")

    return ModuleBuild(
        module_name=r.base_module,
        parts_emitted=["base"],
        interfaces={"downstream": _base_downstream(r)},
    )


# --------------------------------------------------------------------------- #
# Slot B - body ((3) body form)
# --------------------------------------------------------------------------- #


def _build_body(ctx: ModuleBuildContext) -> ModuleBuild:
    model = ctx.model
    r: ResolvedIndustrialViceConfig = ctx.config  # type: ignore[assignment]
    s = r.size_scale
    body = model.part("body", meta={"rear_anvil": True})

    wp = _cast_body_casting() if r.body_module == "cast_body" else _welded_box_body_casting()
    body.visual(_scaled_cq_mesh(wp, "body_casting", s), material="paint", name="body_casting", material_class_id="metal.paint_coated")

    # Rear anvil block + fixed jaw plate (steel). The fixed plate is backed into
    # the clean rear_anvil Box (which reliably overlaps the body casting on both
    # forms), so connectivity does not depend on the filleted casting's
    # tessellation-component split.
    body.visual(_bx(0.130, 0.128, 0.070, s), origin=_o(-0.220, 0.000, 0.150, s), material="steel", name="rear_anvil", material_class_id="metal.steel_bare")
    body.visual(_bx(0.030, 0.148, 0.064, s), origin=_o(-0.150, 0.000, 0.205, s), material="steel", name="fixed_plate", material_class_id="metal.steel_bare")
    _add_plate_screws(body, s, screw_x=-0.140, plate_center_z=0.205, plate_height=0.064,
                      name_prefix="fixed_plate_screw", n=r.plate_screw_count)

    # Cast-on embossing / ribs ((4)), on the -Y side face; positions scale with body.
    for i, x in enumerate((-0.133, -0.115, -0.096, -0.076)):
        body.visual(_bx(0.010, 0.006, 0.027, s), origin=_o(x, -0.083, 0.104, s), material="paint", name=f"embossed_mark_{i}", material_class_id="metal.paint_coated")
    body.visual(_bx(0.014, 0.010, 0.142, s), origin=_o(-0.142, -0.083, 0.103, s), material="paint", name="rear_rib", material_class_id="metal.paint_coated")
    body.visual(_bx(0.012, 0.010, 0.115, s), origin=_o(0.108, -0.083, 0.086, s), material="paint", name="front_rib", material_class_id="metal.paint_coated")
    body.visual(_bx(0.035, 0.008, 0.002, s), origin=_o(-0.082, -0.084, 0.244, s), material="bare", name="body_paint_chip", material_class_id="metal.cast_iron_bare")

    return ModuleBuild(
        module_name=r.body_module,
        parts_emitted=["body"],
        interfaces={"downstream": _base_downstream(r)},
    )


# --------------------------------------------------------------------------- #
# Slot C - mount ((2) swivel joint type + (1) side_lock)
# --------------------------------------------------------------------------- #


def _build_mount(ctx: ModuleBuildContext) -> ModuleBuild:
    model = ctx.model
    r: ResolvedIndustrialViceConfig = ctx.config  # type: ignore[assignment]
    s = r.size_scale
    base = model.get_part("base")
    body = model.get_part("body")

    parts, joints = [], []

    if r.mount_module == "fixed_mount":
        model.articulation(
            "base_to_body", ArticulationType.FIXED, parent=base, child=body,
            origin=_o(0.0, 0.0, BOSS_TOP, s),
        )
        joints.append("base_to_body")
    else:
        if r.mount_module == "continuous_swivel":
            limits = MotionLimits(effort=80.0, velocity=0.6)
            jtype = ArticulationType.CONTINUOUS
        else:
            limits = MotionLimits(effort=80.0, velocity=0.6, lower=-r.swivel_range, upper=r.swivel_range)
            jtype = ArticulationType.REVOLUTE
        model.articulation(
            "base_to_body", jtype, parent=base, child=body,
            origin=_o(0.0, 0.0, BOSS_TOP, s), axis=(0.0, 0.0, 1.0),
            motion_limits=limits,
        )
        joints.append("base_to_body")

        # Side swivel-lock handle (parallel child of the base). The joint is
        # yawed so the handle points RADIALLY OUTWARD from the base center: the
        # pivot sits outside the turntable boss (r>boss_r) and the handle lies
        # above the base top plane, so neither the swivelling body (z>=boss_top)
        # nor the boss is ever swept into as the lock rotates +/-0.8.
        lock_x, lock_y = -0.035, -0.095
        out_yaw = math.atan2(lock_y, lock_x)  # local +X -> outward radial
        side_lock = model.part("side_lock", meta={"swivel_lock_handle": True})
        side_lock.visual(
            _cy(0.011, 0.030, s), origin=_o(0.0, 0.0, 0.0, s),
            material="steel", name="lock_boss", material_class_id="metal.steel_bare",
        )
        side_lock.visual(
            _cy(0.006, 0.060, s), origin=_o(0.040, 0.0, 0.014, s, rpy=(0.0, math.pi / 2.0, 0.0)),
            material="dark", name="lock_lever", material_class_id="metal.blackened_gunmetal",
        )
        model.articulation(
            "base_to_side_lock", ArticulationType.REVOLUTE, parent=base, child=side_lock,
            origin=_o(lock_x, lock_y, 0.030, s, rpy=(0.0, 0.0, out_yaw)), axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=2.0, velocity=2.0, lower=-0.8, upper=0.8),
        )
        parts.append("side_lock")
        joints.append("base_to_side_lock")

    return ModuleBuild(
        module_name=r.mount_module,
        parts_emitted=parts,
        internal_articulations=joints,
        interfaces={"downstream": _base_downstream(r)},
    )


# --------------------------------------------------------------------------- #
# Slot D - jaw_set ((3)/(1) jaw type + plate_screw_count multiplicity)
# --------------------------------------------------------------------------- #


def _build_jaw_set(ctx: ModuleBuildContext) -> ModuleBuild:
    model = ctx.model
    r: ResolvedIndustrialViceConfig = ctx.config  # type: ignore[assignment]
    s = r.size_scale
    body = model.get_part("body")
    front_jaw = model.part("front_jaw", meta={"sliding_jaw": True})

    front_jaw.visual(_scaled_cq_mesh(_front_jaw_casting(), "front_casting", s), material="paint", name="front_casting", material_class_id="metal.paint_coated")
    # Slide bar sized to fill the body slide tunnel in z (tunnel height ~0.052)
    # so it seats against the tunnel walls on both body forms (retained slide
    # fit -> real contact for connectivity; overlap allowed in run_tests).
    front_jaw.visual(_bx(0.226, 0.045, 0.056, s), origin=_o(-0.098, 0.000, 0.000, s), material="paint", name="slide_bar", material_class_id="metal.paint_coated")
    front_jaw.visual(_bx(0.014, 0.148, 0.064, s), origin=_o(-0.050, 0.000, 0.140, s), material="steel", name="moving_plate", material_class_id="metal.steel_bare")
    _add_plate_screws(front_jaw, s, screw_x=-0.059, plate_center_z=0.140, plate_height=0.064,
                      name_prefix="moving_plate_screw", n=r.plate_screw_count)
    front_jaw.visual(_bx(0.028, 0.007, 0.002, s), origin=_o(0.020, -0.080, 0.198, s), material="bare", name="jaw_paint_chip", material_class_id="metal.cast_iron_bare")

    if r.jaw_module == "pipe_combo_jaws":
        # Integral lower toothed pipe V-jaws (combination vise). The fixed V-jaw
        # is added to the already-built body; the moving V-jaw rides the front
        # jaw. Both seated slightly embedded into their host castings.
        body.visual(
            _scaled_cq_mesh(_pipe_v_jaw_casting(), "fixed_v_jaw", s, ang=0.10),
            origin=_o(-0.150, 0.0, 0.144, s), material="steel", name="fixed_v_jaw", material_class_id="metal.steel_bare",
        )
        front_jaw.visual(
            _scaled_cq_mesh(_pipe_v_jaw_casting(), "moving_v_jaw", s, ang=0.10),
            origin=_o(-0.045, 0.0, 0.079, s, rpy=(0.0, 0.0, math.pi)), material="steel", name="moving_v_jaw", material_class_id="metal.steel_bare",
        )

    model.articulation(
        "body_to_front_jaw", ArticulationType.PRISMATIC, parent=body, child=front_jaw,
        origin=_o(FRONT_X, 0.0, BODY_SEAT_Z, s), axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=120.0, velocity=0.08, lower=0.0, upper=r.jaw_travel * s),
    )

    return ModuleBuild(
        module_name=r.jaw_module,
        parts_emitted=["front_jaw"],
        internal_articulations=["body_to_front_jaw"],
        interfaces={"downstream": _base_downstream(r)},
    )


# --------------------------------------------------------------------------- #
# Slot E - drive ((2) screw joint + (3) handle form)
# --------------------------------------------------------------------------- #


def _build_drive(ctx: ModuleBuildContext) -> ModuleBuild:
    model = ctx.model
    r: ResolvedIndustrialViceConfig = ctx.config  # type: ignore[assignment]
    s = r.size_scale
    front_jaw = model.get_part("front_jaw")
    lead_screw = model.part("lead_screw", meta={"spins_to_drive_jaw": True})

    lead_screw.visual(_cy(0.011, 0.320, s), origin=_o(0.110, 0.0, 0.0, s, rpy=(0.0, math.pi / 2.0, 0.0)), material="steel", name="lead_screw", material_class_id="metal.steel_bare")
    lead_screw.visual(_cy(0.023, 0.052, s), origin=_o(0.0, 0.0, 0.0, s, rpy=(0.0, math.pi / 2.0, 0.0)), material="steel", name="screw_collar", material_class_id="metal.steel_bare")

    if r.drive_module == "thandle_screw":
        lead_screw.visual(_cy(0.0075, 0.205, s), origin=_o(0.250, 0.0, 0.0, s, rpy=(-math.pi / 2.0, 0.0, 0.0)), material="steel", name="t_handle", material_class_id="metal.steel_bare")
        lead_screw.visual(_sp(0.017, s), origin=_o(0.250, 0.106, 0.0, s), material="dark", name="handle_knob_0", material_class_id="plastic.opaque_glossy_molded")
        lead_screw.visual(_sp(0.017, s), origin=_o(0.250, -0.106, 0.0, s), material="dark", name="handle_knob_1", material_class_id="plastic.opaque_glossy_molded")
        lead_screw.visual(_sp(0.014, s), origin=_o(0.282, 0.0, 0.0, s), material="dark", name="screw_end_cap", material_class_id="plastic.opaque_glossy_molded")
        model.articulation(
            "front_jaw_to_screw", ArticulationType.CONTINUOUS, parent=front_jaw, child=lead_screw,
            origin=_o(SCREW_X, 0.0, 0.0, s), axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=8.0, velocity=6.0),
        )
    else:  # cam_lever (speed-vise quick clamp)
        lead_screw.visual(_cy(0.009, 0.150, s), origin=_o(0.250, 0.0, 0.075, s), material="steel", name="cam_lever", material_class_id="metal.steel_bare")
        lead_screw.visual(_sp(0.018, s), origin=_o(0.250, 0.0, 0.155, s), material="dark", name="lever_grip", material_class_id="plastic.opaque_glossy_molded")
        model.articulation(
            "front_jaw_to_screw", ArticulationType.REVOLUTE, parent=front_jaw, child=lead_screw,
            origin=_o(SCREW_X, 0.0, 0.0, s), axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=8.0, velocity=6.0, lower=-r.screw_arc, upper=r.screw_arc),
        )

    return ModuleBuild(
        module_name=r.drive_module,
        parts_emitted=["lead_screw"],
        internal_articulations=["front_jaw_to_screw"],
        interfaces={"downstream": _base_downstream(r)},
    )


# --------------------------------------------------------------------------- #
# Factory registries + assembly
# --------------------------------------------------------------------------- #

BASE_FACTORIES = {"round_base": _build_base, "rect_base": _build_base}
BODY_FACTORIES = {"cast_body": _build_body, "welded_box_body": _build_body}
MOUNT_FACTORIES = {m: _build_mount for m in ("revolute_swivel", "continuous_swivel", "fixed_mount")}
JAW_FACTORIES = {"flat_jaws": _build_jaw_set, "pipe_combo_jaws": _build_jaw_set}
DRIVE_FACTORIES = {"thandle_screw": _build_drive, "cam_lever": _build_drive}


def _slots_for_config(r: ResolvedIndustrialViceConfig) -> list[SlotSpec]:
    return [
        SlotSpec(slot_name="base", candidates={r.base_module: _build_base}, anchor_choice=r.base_module),
        SlotSpec(slot_name="body", candidates={r.body_module: _build_body}, anchor_choice=r.body_module),
        SlotSpec(slot_name="mount", candidates={r.mount_module: _build_mount}, anchor_choice=r.mount_module),
        SlotSpec(slot_name="jaw_set", candidates={r.jaw_module: _build_jaw_set}, anchor_choice=r.jaw_module),
        SlotSpec(slot_name="drive", candidates={r.drive_module: _build_drive}, anchor_choice=r.drive_module),
    ]


def build_industrial_industrial_vice(
    config: IndustrialViceConfig,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name="industrial_industrial_vice", assets=assets)
    for material_name, rgba in r.palette.items():
        model.material(material_name, rgba=rgba)

    assemble(
        model,
        slots=_slots_for_config(r),
        rng=random.Random(0),
        palette=r.palette,
        config=r,
        seed=0,
        selection_mode="anchor_choices",
    )
    return model


def build_seeded_industrial_industrial_vice(seed: int) -> ArticulatedObject:
    return build_industrial_industrial_vice(config_from_seed(seed))


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    r = resolve_config(config_from_seed(seed))
    lug_axis = f"lugs_{r.lug_count}" if r.base_module == "round_base" else "lugs_rect4"
    screw_axis = f"plate_screws_{r.plate_screw_count}"
    return [
        ("base", r.base_module),
        ("lug_count", lug_axis),
        ("body", r.body_module),
        ("mount", r.mount_module),
        ("jaw_set", r.jaw_module),
        ("plate_screw_count", screw_axis),
        ("drive", r.drive_module),
    ]


# --------------------------------------------------------------------------- #
# Author-layer QC
# --------------------------------------------------------------------------- #


def _declare_overlaps(ctx: TestContext, model: ArticulatedObject, r: ResolvedIndustrialViceConfig) -> None:
    parts = {p.name for p in model.parts}
    base = model.get_part("base")
    body = model.get_part("body")
    front_jaw = model.get_part("front_jaw")
    lead_screw = model.get_part("lead_screw")

    # Captured lead screw / slide bar in the jaw + body bores (origin S1 semantics).
    ctx.allow_overlap(front_jaw, lead_screw, elem_a="front_casting", elem_b="screw_collar",
                      reason="Screw collar is captured in the moving jaw bore.")
    ctx.allow_overlap(front_jaw, lead_screw, elem_a="slide_bar", elem_b="lead_screw",
                      reason="Lead screw passes through the sliding bar's threaded bore.")
    ctx.allow_overlap(front_jaw, lead_screw, elem_a="front_casting", elem_b="lead_screw",
                      reason="Lead screw passes through the moving jaw bore before the handle.")
    ctx.allow_overlap(body, front_jaw, elem_a="body_casting", elem_b="slide_bar",
                      reason="Slide bar is retained inside the cast body's guide tunnel.")

    # Body seats on the base turntable boss (coincident faces).
    ctx.allow_overlap(base, body, elem_a="base_with_bolt_holes", elem_b="body_casting",
                      reason="Body seats flush on the base turntable boss top face.")

    # Swivel lock post seated in a drilled boss on the base.
    if "side_lock" in parts:
        ctx.allow_overlap(base, model.get_part("side_lock"), elem_a="base_with_bolt_holes", elem_b="lock_boss",
                          reason="Swivel lock boss is seated in a drilled boss on the base.")

    # Combination pipe V-jaws embedded into their host castings.
    if r.jaw_module == "pipe_combo_jaws":
        ctx.allow_overlap(body, front_jaw, elem_a="fixed_v_jaw", elem_b="moving_v_jaw",
                          reason="Fixed / moving pipe V-jaws share the same jaw line; embedded roots overlap at the mount.")
        ctx.allow_overlap(base, body, elem_a="base_with_bolt_holes", elem_b="fixed_v_jaw",
                          reason="Fixed V-jaw root embedded into the body casting near the base seat.")


def _expect_mount(ctx: TestContext, model, r) -> None:
    body = model.get_part("body")
    j = model.get_articulation("base_to_body")
    if r.mount_module == "fixed_mount":
        ctx.check("base_to_body is FIXED", j.articulation_type == ArticulationType.FIXED)
        ctx.check("no side_lock on fixed mount", "side_lock" not in [p.name for p in model.parts])
        return
    if r.mount_module == "continuous_swivel":
        ctx.check("base_to_body is CONTINUOUS swivel",
                  j.articulation_type == ArticulationType.CONTINUOUS
                  and j.motion_limits is not None
                  and j.motion_limits.lower is None and j.motion_limits.upper is None)
    else:
        ctx.check("base_to_body is bounded REVOLUTE swivel",
                  j.articulation_type == ArticulationType.REVOLUTE
                  and j.motion_limits is not None and j.motion_limits.upper > 0.5)
    ctx.check("side_lock present on swivel mount", "side_lock" in [p.name for p in model.parts])
    # targeted: the swivel actually rotates the body assembly.
    rest = ctx.part_world_aabb(body)
    with ctx.pose({j: 0.6}):
        spun = ctx.part_world_aabb(body)
    moved = _center_dist(rest, spun)
    ctx.check("swivel rotates body assembly", moved > 0.01, details=f"disp={moved:.4f}")


def _expect_jaw_slide(ctx: TestContext, model, r) -> None:
    body = model.get_part("body")
    front_jaw = model.get_part("front_jaw")
    slide = model.get_articulation("body_to_front_jaw")
    ctx.check("jaw slide is PRISMATIC",
              slide.articulation_type == ArticulationType.PRISMATIC
              and slide.motion_limits is not None and slide.motion_limits.upper > 0.03)
    # targeted: front jaw translates outward (jaw opens).
    rest = ctx.part_world_position(front_jaw)
    with ctx.pose({slide: slide.motion_limits.upper}):
        ext = ctx.part_world_position(front_jaw)
    ok = rest is not None and ext is not None and ext[0] > rest[0] + 0.03
    ctx.check("front jaw slides outward", ok, details=f"rest={rest}, ext={ext}")
    if r.jaw_module == "pipe_combo_jaws":
        ctx.check("pipe V-jaws present",
                  body.get_visual("fixed_v_jaw") is not None and front_jaw.get_visual("moving_v_jaw") is not None)


def _expect_drive(ctx: TestContext, model, r) -> None:
    lead_screw = model.get_part("lead_screw")
    j = model.get_articulation("front_jaw_to_screw")
    if r.drive_module == "thandle_screw":
        ctx.check("screw spins (CONTINUOUS)", j.articulation_type == ArticulationType.CONTINUOUS)
        ctx.check("T-handle present", lead_screw.get_visual("t_handle") is not None)
        elem = "handle_knob_0"
    else:
        ctx.check("cam lever arc (REVOLUTE)",
                  j.articulation_type == ArticulationType.REVOLUTE
                  and j.motion_limits is not None and j.motion_limits.upper > 0.5)
        ctx.check("cam lever present", lead_screw.get_visual("cam_lever") is not None)
        elem = "lever_grip"
    # targeted: handle/lever sweeps about the screw axis.
    rest = ctx.part_element_world_aabb(lead_screw, elem=elem)
    val = (math.pi / 2.0) if r.drive_module == "thandle_screw" else j.motion_limits.upper
    with ctx.pose({j: val}):
        moved = ctx.part_element_world_aabb(lead_screw, elem=elem)
    ctx.check("handle sweeps about screw axis", _center_dist(rest, moved) > 0.02,
              details=f"disp={_center_dist(rest, moved):.4f}")


def _center_dist(a, b) -> float:
    if a is None or b is None:
        return 0.0
    ca = [(a[0][i] + a[1][i]) / 2.0 for i in range(3)]
    cb = [(b[0][i] + b[1][i]) / 2.0 for i in range(3)]
    return math.dist(ca, cb)


def run_industrial_industrial_vice_tests(
    model: ArticulatedObject,
    config: IndustrialViceConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)

    _declare_overlaps(ctx, model, r)

    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.020)
    ctx.fail_if_joint_mating_has_gap()

    # Category identity.
    base = model.get_part("base")
    ctx.check("base + body + front_jaw + lead_screw present",
              all(n in [p.name for p in model.parts] for n in ("base", "body", "front_jaw", "lead_screw")))
    ctx.check("base has N bolt lugs", base.meta.get("bolt_holes") in (3, 4, 6))

    _expect_mount(ctx, model, r)
    _expect_jaw_slide(ctx, model, r)
    _expect_drive(ctx, model, r)

    # Rule 5: dynamic collision across sampled joint poses.
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=48, ignore_fixed=True)

    return ctx.report()


__all__ = [
    "IndustrialViceConfig",
    "ResolvedIndustrialViceConfig",
    "BaseModule",
    "BodyModule",
    "MountModule",
    "JawModule",
    "DriveModule",
    "VicePalette",
    "build_industrial_industrial_vice",
    "build_seeded_industrial_industrial_vice",
    "config_from_seed",
    "resolve_config",
    "run_industrial_industrial_vice_tests",
    "slot_choices_for_seed",
]
