# SPDX-License-Identifier: Apache-2.0

"""Container kettle — modular procedural template (teapot / electric kettle /
stovetop whistler).

Category identity: an upright hollow kettle. A lathe/loft circular hollow open
shell (``kettle_body``) carries a pour ``spout`` on +X (the defining feature
that separates a kettle from a cup / jar). A handle mechanism grips it and a lid
mechanism closes it; the base/heating form decides the root and whether the body
lifts off a power base / trivet.

Four parallel slots (spec ``Container_Kettle.md``):

  * ``body_form`` (4) — the ``kettle_body`` shell + spout type:
      - straight_barrel (electric): tall waisted ``_loft`` barrel, collar flare
        spout, no whistle cap.
      - bell_lathe (stovetop): wide-base bell ``_loft_z``, through-wall tapered
        tube spout + root fairing + whistle cap.
      - gooseneck_pour (stovetop): low wide pear, short spline pour tube + root
        fairing + whistle cap.
      - squat_round (electric): squat pot-belly ovoid, collar flare spout.
  * ``handle`` (4) — the grip mechanism:
      - swing_bail: arching bail, 1 REVOLUTE +Y.
      - fixed_c_handle: rear C handle, fixed body visual (0 joint).
      - folding_bail: two-segment folding bail, 2 chained REVOLUTE +Y.
      - side_loop_handle: rear-quarter D-ring, 1 REVOLUTE +Z (vertical).
  * ``lid_closure`` (4) — the closure mechanism (each >=1 non-fixed joint):
      - liftoff_knob: domed knob lid, PRISMATIC +Z lift.
      - rear_flip_hinge: rear-hinged flip disc, REVOLUTE rear hinge.
      - screw_cap: domed twist cap, REVOLUTE +Z twist.
      - hinged_pour_flap: fixed dome (body visual) + small front pour flap
        REVOLUTE on a visible hinge line.
  * ``base_heating`` (3) — root / body-lift form:
      - flat_stovetop: body is ROOT, sits at z=0, no base part / no body lift.
      - cordless_power_base: round power base ROOT + body_lift PRISMATIC +Z.
      - trivet_stand: 4-leg cast-iron trivet ROOT + trivet_to_body PRISMATIC +Z.

Two structurally distinct motion spines (electric power-base root + body lift;
stovetop body root sitting on ground / trivet) are handled by ``base_heating``
choosing the root chain. The spout type is bound to ``body_form`` (not the base
family) and the body's interface points (rim_z, collar/cap seat, mount line,
hinge) are expressed in one body-local frame so every handle / lid / base
combination assembles safely. ``whistle_cap`` is emitted only for the stovetop
``body_form`` candidates (conditional).

Continuous size/proportion variation lives in ``resolve_config`` as clamped
params, never as slot candidates. ``palette_style`` is palette-only (9 family-
orthogonal colorways + finish), not a slot choice.

Sources (articraft_data ``picture/Container/Kettle`` 5-star pool): parents
``d04a456a`` (electric flip-lid power base), ``89ab783c`` (stovetop whistler),
plus qwen forks ``gooseneck_body``, ``squat_round_body``, ``folding_bail``,
``side_loop_handle``, ``screw_cap_lid``, ``sliding_pour_lid``, ``trivet_stand``.

Canonical spec: ``articraft_template_authoring/specs_modular_v1/Container_Kettle.md``
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
    BoxGeometry,
    Cylinder,
    CylinderGeometry,
    Inertial,
    MotionLimits,
    Origin,
    SphereGeometry,
    TestContext,
    TestReport,
    TorusGeometry,
    mesh_from_cadquery,
    mesh_from_geometry,
    tube_from_spline_points,
)

__modular__ = True

# ---------------------------------------------------------------------------
# Slot domains
# ---------------------------------------------------------------------------
BodyForm = Literal["straight_barrel", "bell_lathe", "gooseneck_pour", "squat_round"]
Handle = Literal["swing_bail", "fixed_c_handle", "folding_bail", "side_loop_handle"]
LidClosure = Literal["liftoff_knob", "rear_flip_hinge", "screw_cap", "hinged_pour_flap"]
BaseHeating = Literal["flat_stovetop", "cordless_power_base", "trivet_stand"]
PaletteStyle = Literal[
    "brushed_steel",
    "polished_stainless",
    "matte_black_electric",
    "copper_stovetop",
    "enamel_pastel",
    "enamel_red",
    "glossy_ceramic_white",
    "cast_iron_trivet",
    "two_tone_cream_steel",
]

BODY_FORMS: tuple[BodyForm, ...] = (
    "straight_barrel",
    "bell_lathe",
    "gooseneck_pour",
    "squat_round",
)
HANDLES: tuple[Handle, ...] = (
    "swing_bail",
    "fixed_c_handle",
    "folding_bail",
    "side_loop_handle",
)
LID_CLOSURES: tuple[LidClosure, ...] = (
    "liftoff_knob",
    "rear_flip_hinge",
    "screw_cap",
    "hinged_pour_flap",
)
BASE_HEATINGS: tuple[BaseHeating, ...] = (
    "flat_stovetop",
    "cordless_power_base",
    "trivet_stand",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "brushed_steel",
    "polished_stainless",
    "matte_black_electric",
    "copper_stovetop",
    "enamel_pastel",
    "enamel_red",
    "glossy_ceramic_white",
    "cast_iron_trivet",
    "two_tone_cream_steel",
)

# Stovetop body_form candidates carry a through-wall tube spout + whistle cap.
_STOVETOP_BODIES: frozenset[BodyForm] = frozenset({"bell_lathe", "gooseneck_pour"})


# ---------------------------------------------------------------------------
# Palette: 9 family-orthogonal colorways. Each maps the four component groups
# (body shell / handle grip / lid·spout / base·accent) + a finish dimension.
# Anchored to 5-star source RGBA where available, rest derived in-domain.
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class _Palette:
    body: tuple[float, float, float, float]
    grip: tuple[float, float, float, float]
    lid: tuple[float, float, float, float]
    spout: tuple[float, float, float, float]
    rim: tuple[float, float, float, float]  # rim / collar / cap shadow
    base: tuple[float, float, float, float]
    accent: tuple[float, float, float, float]
    finish: str


PALETTES: dict[PaletteStyle, _Palette] = {
    "brushed_steel": _Palette(
        body=(0.78, 0.79, 0.81, 1.0),
        grip=(0.12, 0.12, 0.13, 1.0),
        lid=(0.78, 0.79, 0.81, 1.0),
        spout=(0.78, 0.79, 0.81, 1.0),
        rim=(0.66, 0.67, 0.69, 1.0),
        base=(0.78, 0.79, 0.81, 1.0),
        accent=(0.66, 0.67, 0.69, 1.0),
        finish="brushed_stainless",
    ),
    "polished_stainless": _Palette(
        body=(0.85, 0.86, 0.88, 1.0),
        grip=(0.12, 0.12, 0.13, 1.0),
        lid=(0.85, 0.86, 0.88, 1.0),
        spout=(0.85, 0.86, 0.88, 1.0),
        rim=(0.80, 0.81, 0.83, 1.0),
        base=(0.85, 0.86, 0.88, 1.0),
        accent=(0.80, 0.81, 0.83, 1.0),
        finish="polished_stainless",
    ),
    "matte_black_electric": _Palette(
        body=(0.10, 0.10, 0.11, 1.0),
        grip=(0.18, 0.18, 0.20, 1.0),
        lid=(0.18, 0.18, 0.20, 1.0),
        spout=(0.66, 0.67, 0.69, 1.0),
        rim=(0.18, 0.18, 0.20, 1.0),
        base=(0.10, 0.10, 0.11, 1.0),
        accent=(0.30, 0.40, 0.48, 0.85),
        finish="matte_black_electric",
    ),
    "copper_stovetop": _Palette(
        body=(0.78, 0.79, 0.81, 1.0),
        grip=(0.12, 0.12, 0.13, 1.0),
        lid=(0.78, 0.79, 0.81, 1.0),
        spout=(0.72, 0.45, 0.20, 1.0),
        rim=(0.72, 0.45, 0.20, 1.0),
        base=(0.78, 0.79, 0.81, 1.0),
        accent=(0.72, 0.45, 0.20, 1.0),
        finish="polished_copper_accent",
    ),
    "enamel_pastel": _Palette(
        body=(0.62, 0.80, 0.78, 1.0),
        grip=(0.12, 0.12, 0.13, 1.0),
        lid=(0.62, 0.80, 0.78, 1.0),
        spout=(0.66, 0.67, 0.69, 1.0),
        rim=(0.66, 0.67, 0.69, 1.0),
        base=(0.66, 0.67, 0.69, 1.0),
        accent=(0.66, 0.67, 0.69, 1.0),
        finish="enamel_gloss_pastel",
    ),
    "enamel_red": _Palette(
        body=(0.74, 0.12, 0.10, 1.0),
        grip=(0.12, 0.12, 0.13, 1.0),
        lid=(0.74, 0.12, 0.10, 1.0),
        spout=(0.66, 0.67, 0.69, 1.0),
        rim=(0.66, 0.67, 0.69, 1.0),
        base=(0.66, 0.67, 0.69, 1.0),
        accent=(0.12, 0.12, 0.13, 1.0),
        finish="enamel_gloss_red",
    ),
    "glossy_ceramic_white": _Palette(
        body=(0.93, 0.92, 0.89, 1.0),
        grip=(0.20, 0.20, 0.22, 1.0),
        lid=(0.93, 0.92, 0.89, 1.0),
        spout=(0.20, 0.20, 0.22, 1.0),
        rim=(0.20, 0.20, 0.22, 1.0),
        base=(0.20, 0.20, 0.22, 1.0),
        accent=(0.20, 0.20, 0.22, 1.0),
        finish="glossy_ceramic",
    ),
    "cast_iron_trivet": _Palette(
        body=(0.78, 0.79, 0.81, 1.0),
        grip=(0.12, 0.12, 0.13, 1.0),
        lid=(0.78, 0.79, 0.81, 1.0),
        spout=(0.78, 0.79, 0.81, 1.0),
        rim=(0.66, 0.67, 0.69, 1.0),
        base=(0.22, 0.22, 0.24, 1.0),
        accent=(0.22, 0.22, 0.24, 1.0),
        finish="cast_iron",
    ),
    "two_tone_cream_steel": _Palette(
        body=(0.90, 0.86, 0.78, 1.0),
        grip=(0.12, 0.12, 0.13, 1.0),
        lid=(0.78, 0.79, 0.81, 1.0),
        spout=(0.78, 0.79, 0.81, 1.0),
        rim=(0.66, 0.67, 0.69, 1.0),
        base=(0.78, 0.79, 0.81, 1.0),
        accent=(0.66, 0.67, 0.69, 1.0),
        finish="two_tone",
    ),
}


# ---------------------------------------------------------------------------
# Per body_form base geometry (meters). All interface points are expressed in
# the SAME body-local frame (body base near z=0) so handle / lid / base
# builders are body-agnostic and any cross-family combination assembles.
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class _FormGeom:
    # outer/inner loft sections as (z, r) circle stacks in body-local frame.
    base_z: float  # z of the body shell bottom (sits on root)
    rim_z: float  # z of the open mouth rim (lid mount plane)
    neck_r: float  # outer radius at the rim / neck
    belly_r: float  # widest outer radius (for mount/handle clearance)
    collar_z: float  # z where the upper collar / cap-seat band begins
    mount_z: float  # shoulder mount line z (handle pivot height)
    spout_kind: str  # "collar" (electric flare) | "tube" (stovetop)


# straight_barrel (electric) — d04a456a. base ~0.012, rim 0.196.
_GEOM_BARREL = _FormGeom(
    base_z=0.012,
    rim_z=0.196,
    neck_r=0.066,
    belly_r=0.066,
    collar_z=0.156,
    mount_z=0.150,
    spout_kind="collar",
)
# bell_lathe (stovetop) — 89ab783c. base 0.0, rim 0.150, wide base.
_GEOM_BELL = _FormGeom(
    base_z=0.0,
    rim_z=0.150,
    neck_r=0.058,
    belly_r=0.090,
    collar_z=0.130,
    mount_z=0.134,
    spout_kind="tube",
)
# gooseneck_pour (stovetop) — gooseneck_body. low wide pear, rim 0.148.
_GEOM_GOOSE = _FormGeom(
    base_z=0.0,
    rim_z=0.148,
    neck_r=0.038,
    belly_r=0.086,
    collar_z=0.124,
    mount_z=0.112,
    spout_kind="goose",
)
# squat_round (electric) — squat_round_body. squat ovoid, rim 0.125.
_GEOM_SQUAT = _FormGeom(
    base_z=0.012,
    rim_z=0.125,
    neck_r=0.052,
    belly_r=0.095,
    collar_z=0.100,
    mount_z=0.100,
    spout_kind="collar",
)

_FORM_GEOMS: dict[BodyForm, _FormGeom] = {
    "straight_barrel": _GEOM_BARREL,
    "bell_lathe": _GEOM_BELL,
    "gooseneck_pour": _GEOM_GOOSE,
    "squat_round": _GEOM_SQUAT,
}

# Travel / size nominal constants.
_LID_LIFT = 0.040
_CAP_TWIST_UPPER = 1.05
_POUR_FLAP_UPPER = 1.18
_FLIP_UPPER = 1.22
_BAIL_UPPER = 1.6
_LOOP_UPPER = math.pi / 2.0
_POWER_BASE_LIFT = 0.040
_TRIVET_LIFT = 0.040

# Dock capture interface (power base / trivet): a post on the base slides in a
# receiver tube inside the body so the lifted body keeps support contact with
# the grounded base through the full prismatic travel. The heel / floor carry a
# clearance bore for the post; the receiver bore is a light press fit.
_DOCK_POST_R = 0.008
_DOCK_BORE_R = 0.0065
_DOCK_CLEARANCE_R = 0.010
_DOCK_OUTER_R = 0.012
_DOCK_DEPTH = 0.052

WALL = 0.006


@dataclass(frozen=True)
class ContainerKettleConfig:
    body_form: BodyForm = "bell_lathe"
    handle: Handle = "swing_bail"
    lid_closure: LidClosure = "liftoff_knob"
    base_heating: BaseHeating = "flat_stovetop"
    palette_style: PaletteStyle = "brushed_steel"
    body_height_scale: float = 1.0
    body_radius_scale: float = 1.0
    spout_reach_scale: float = 1.0
    handle_offset_scale: float = 1.0
    joint_travel_scale: float = 1.0
    name: str = "container_kettle"


@dataclass(frozen=True)
class ResolvedContainerKettleConfig:
    body_form: BodyForm
    handle: Handle
    lid_closure: LidClosure
    base_heating: BaseHeating
    palette_style: PaletteStyle
    body_height_scale: float
    body_radius_scale: float
    spout_reach_scale: float
    handle_offset_scale: float
    joint_travel_scale: float
    # derived geometry (body-local frame)
    base_z: float
    rim_z: float
    neck_r: float
    belly_r: float
    collar_z: float
    mount_z: float
    spout_kind: str
    has_whistle: bool
    # handle equation outputs
    mount_y: float  # lug half-span (handle pivot Y offset)
    handle_reach: float  # rear C-grip / loop outward offset from body surface
    bail_mount_z: float  # bail / folding pivot line z (shoulder, just below rim)
    bail_crown_dz: float  # crown rise above the mount line (clears the lid)
    name: str


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _pick(value, choices):
    return value if value in choices else choices[0]


# ---------------------------------------------------------------------------
# Seed / resolve
# ---------------------------------------------------------------------------
def config_from_seed(seed: int) -> ContainerKettleConfig:
    """Deterministic procedural sampling (seed 0 is not special).

    To keep seed quality high, the discrete slot choices stay on the two native
    kettle families instead of wandering across odd cross-family mixes:

      * ``cordless_power_base`` -> electric body / handle / lid set
      * ``flat_stovetop`` and ``trivet_stand`` -> stovetop set

    The sampler still covers the native combinatorics deterministically across
    seeds, while the continuous scales and palette remain varied.
    """
    rng = random.Random(seed)

    base_heating = BASE_HEATINGS[seed % len(BASE_HEATINGS)]
    variant = seed // len(BASE_HEATINGS)
    electric_family = base_heating == "cordless_power_base"
    if electric_family:
        body_opts: tuple[BodyForm, ...] = ("straight_barrel", "squat_round")
        handle_opts: tuple[Handle, ...] = ("fixed_c_handle", "side_loop_handle")
        lid_opts: tuple[LidClosure, ...] = ("rear_flip_hinge", "screw_cap")
    else:
        body_opts = ("bell_lathe", "gooseneck_pour")
        handle_opts = ("swing_bail", "folding_bail")
        lid_opts = ("liftoff_knob", "hinged_pour_flap")

    return ContainerKettleConfig(
        body_form=body_opts[variant % len(body_opts)],
        handle=handle_opts[(variant // len(body_opts)) % len(handle_opts)],
        lid_closure=lid_opts[(variant // (len(body_opts) * len(handle_opts))) % len(lid_opts)],
        base_heating=base_heating,
        palette_style=rng.choice(PALETTE_STYLES),
        body_height_scale=round(rng.uniform(0.85, 1.20), 4),
        body_radius_scale=round(rng.uniform(0.88, 1.15), 4),
        spout_reach_scale=round(rng.uniform(0.90, 1.12), 4),
        handle_offset_scale=round(rng.uniform(0.90, 1.12), 4),
        joint_travel_scale=round(rng.uniform(0.85, 1.10), 4),
        name=f"seeded_container_kettle_{seed}",
    )


def resolve_config(
    config: ContainerKettleConfig | None = None,
) -> ResolvedContainerKettleConfig:
    cfg = config or ContainerKettleConfig()
    body_form = _pick(cfg.body_form, BODY_FORMS)
    handle = _pick(cfg.handle, HANDLES)
    lid_closure = _pick(cfg.lid_closure, LID_CLOSURES)
    base_heating = _pick(cfg.base_heating, BASE_HEATINGS)
    palette = _pick(cfg.palette_style, PALETTE_STYLES)

    g = _FORM_GEOMS[body_form]
    h_scale = _clamp(cfg.body_height_scale, 0.85, 1.20)
    r_scale = _clamp(cfg.body_radius_scale, 0.88, 1.15)
    sr_scale = _clamp(cfg.spout_reach_scale, 0.90, 1.12)
    ho_scale = _clamp(cfg.handle_offset_scale, 0.90, 1.12)
    jt_scale = _clamp(cfg.joint_travel_scale, 0.85, 1.10)

    # Height scaling lifts the rim / collar / mount heights about the base.
    base_z = g.base_z
    rim_z = base_z + (g.rim_z - base_z) * h_scale
    collar_z = base_z + (g.collar_z - base_z) * h_scale
    mount_z = base_z + (g.mount_z - base_z) * h_scale
    neck_r = g.neck_r * r_scale
    belly_r = g.belly_r * r_scale

    # whistle cap is conditional on the stovetop body_form spout type.
    has_whistle = body_form in _STOVETOP_BODIES

    # handle_offset equation: lug span / grip reach track body radius. The lug
    # half-span must straddle outside the lid (neck_r + clearance) so a bail /
    # folding handle arches over, not into, the closure.
    mount_y = _clamp(max(belly_r + 0.010, neck_r + 0.026) * ho_scale, 0.05, 0.13)
    handle_reach = _clamp((belly_r + 0.040) * ho_scale, belly_r + 0.020, belly_r + 0.075)

    # Bail / folding handles spring from the shoulder just below the rim and
    # arch high enough to clear the lid envelope, regardless of where the
    # body_form's native mount line sits.
    bail_mount_z = rim_z - 0.030
    # Single-source lid-clearance derivation (Contract 3c): at rest the bail
    # grip sleeve arcs over the lid; its underside must clear the FULLY-LIFTED
    # liftoff-knob envelope by >= 8 mm across every lid_closure / joint_travel
    # combo. The lid builder rises the knob top to rim_z + 0.051 + lid_lift
    # (knob center local 0.040 + sphere radius 0.011), and the SAME jt_scale
    # drives both joints. Grip sleeve radius 0.011, clearance 0.008 -> the grip
    # center (crown apex) must reach knob_top + 0.011 + 0.008 = knob_top + 0.019.
    lid_lift = _LID_LIFT * jt_scale
    knob_top_world = rim_z + 0.051 + lid_lift
    crown_apex_world = max(rim_z + 0.095, knob_top_world + 0.019)
    bail_crown_dz = crown_apex_world - bail_mount_z

    return ResolvedContainerKettleConfig(
        body_form=body_form,
        handle=handle,
        lid_closure=lid_closure,
        base_heating=base_heating,
        palette_style=palette,
        body_height_scale=h_scale,
        body_radius_scale=r_scale,
        spout_reach_scale=sr_scale,
        handle_offset_scale=ho_scale,
        joint_travel_scale=jt_scale,
        base_z=base_z,
        rim_z=rim_z,
        neck_r=neck_r,
        belly_r=belly_r,
        collar_z=collar_z,
        mount_z=mount_z,
        spout_kind=g.spout_kind,
        has_whistle=has_whistle,
        mount_y=mount_y,
        handle_reach=handle_reach,
        bail_mount_z=bail_mount_z,
        bail_crown_dz=bail_crown_dz,
        name=cfg.name or "container_kettle",
    )


def slot_choices_for_config(
    config: ContainerKettleConfig | ResolvedContainerKettleConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedContainerKettleConfig) else resolve_config(config)
    return (
        ("body_form", r.body_form),
        ("handle", r.handle),
        ("lid_closure", r.lid_closure),
        ("base_heating", r.base_heating),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Shared loft helper (circular section stacks along +Z) — derived from every
# 5-star source's ``_loft`` / ``_loft_z``.
# ---------------------------------------------------------------------------
def _loft_z(sections) -> cq.Workplane:
    wp = cq.Workplane("XY")
    prev = 0.0
    for i, (z, rr) in enumerate(sections):
        off = z if i == 0 else z - prev
        if i > 0 or abs(off) > 1e-12:
            wp = wp.workplane(offset=off)
        wp = wp.circle(rr)
        prev = z
    return wp.loft(ruled=False)


# ---------------------------------------------------------------------------
# Body shells (Slot A). Each is a hollow open shell; the spout is a fixed body
# visual whose type is bound to the body_form.
# ---------------------------------------------------------------------------
def _barrel_shell(r: ResolvedContainerKettleConfig) -> cq.Workplane:
    br = r.neck_r
    bz, tz, cz = r.base_z, r.rim_z, r.collar_z
    outer = _loft_z(
        [
            (bz, br - 0.004),
            (bz + 0.010, br),
            (bz + (tz - bz) * 0.40, br - 0.002),
            (cz, br - 0.001),
            (tz, br - 0.003),
        ]
    )
    inner = _loft_z(
        [
            (bz + WALL, br - 0.004 - WALL),
            (bz + (tz - bz) * 0.40, br - 0.002 - WALL),
            (cz, br - 0.001 - WALL),
            (tz + 0.012, br - 0.003 - WALL),
        ]
    )
    return outer.cut(inner)


def _squat_shell(r: ResolvedContainerKettleConfig) -> cq.Workplane:
    bz, tz, cz = r.base_z, r.rim_z, r.collar_z
    belly = r.belly_r
    rim_r = r.neck_r
    bottom_r = max(rim_r * 0.96, belly * 0.52)
    belly_z = bz + (cz - bz) * 0.62
    outer = _loft_z(
        [
            (bz, bottom_r),
            (bz + (cz - bz) * 0.25, bottom_r + (belly - bottom_r) * 0.55),
            (belly_z, belly),
            (bz + (cz - bz) * 0.85, belly * 0.84),
            (cz, rim_r + 0.006),
            (tz, rim_r),
        ]
    )
    inner = _loft_z(
        [
            (bz + WALL, bottom_r - WALL),
            (belly_z, belly - WALL),
            (bz + (cz - bz) * 0.85, belly * 0.84 - WALL),
            (cz, rim_r + 0.006 - WALL),
            (tz + 0.012, rim_r - WALL),
        ]
    )
    return outer.cut(inner)


def _bell_shell(r: ResolvedContainerKettleConfig) -> cq.Workplane:
    bz, tz = r.base_z, r.rim_z
    base_r = r.belly_r
    neck_r = r.neck_r
    neck_z = bz + (tz - bz) * 0.93
    outer = _loft_z(
        [
            (bz, base_r * 0.80),
            (bz + (tz - bz) * 0.08, base_r),
            (bz + (tz - bz) * 0.33, base_r * 0.99),
            (bz + (tz - bz) * 0.63, base_r * 0.89),
            (neck_z, neck_r),
            (tz, neck_r + 0.004),
        ]
    )
    inner = _loft_z(
        [
            (bz + WALL, base_r * 0.73),
            (bz + (tz - bz) * 0.33, base_r * 0.92),
            (bz + (tz - bz) * 0.63, base_r * 0.82),
            (neck_z, neck_r - 0.006),
            (tz + 0.02, neck_r - 0.004),
        ]
    )
    return outer.cut(inner)


def _goose_shell(r: ResolvedContainerKettleConfig) -> cq.Workplane:
    bz, tz = r.base_z, r.rim_z
    base_r = r.belly_r
    neck_r = r.neck_r
    neck_z = bz + (tz - bz) * 0.94
    outer = _loft_z(
        [
            (bz, base_r * 0.63),
            (bz + (tz - bz) * 0.07, base_r * 0.86),
            (bz + (tz - bz) * 0.20, base_r),
            (bz + (tz - bz) * 0.43, base_r * 0.98),
            (bz + (tz - bz) * 0.67, base_r * 0.77),
            (bz + (tz - bz) * 0.84, base_r * 0.54),
            (neck_z, neck_r),
            (tz, neck_r + 0.004),
        ]
    )
    inner = _loft_z(
        [
            (bz + WALL, base_r * 0.55),
            (bz + (tz - bz) * 0.19, base_r * 0.90),
            (bz + (tz - bz) * 0.43, base_r * 0.88),
            (bz + (tz - bz) * 0.67, base_r * 0.68),
            (neck_z, neck_r - 0.006),
            (tz + 0.018, neck_r - 0.003),
        ]
    )
    return outer.cut(inner)


_SHELL_BUILDERS = {
    "straight_barrel": _barrel_shell,
    "squat_round": _squat_shell,
    "bell_lathe": _bell_shell,
    "gooseneck_pour": _goose_shell,
}


def _outer_profile(r: ResolvedContainerKettleConfig):
    """Representative (z, outer_radius) silhouette of the active body form.

    Mirrors the section stacks of the shell builders so handle lugs / struts can
    be planted on the *actual* shell radius at any height (critical for the
    tapered bell / pear / squat forms whose radius is not constant)."""
    bz, tz, cz = r.base_z, r.rim_z, r.collar_z
    if r.body_form == "straight_barrel":
        br = r.neck_r
        return [(bz, br - 0.004), (bz + 0.010, br), (cz, br - 0.001), (tz, br - 0.003)]
    if r.body_form == "squat_round":
        belly = r.belly_r
        rim_r = r.neck_r
        bottom_r = max(rim_r * 0.96, belly * 0.52)
        belly_z = bz + (cz - bz) * 0.62
        return [
            (bz, bottom_r),
            (bz + (cz - bz) * 0.25, bottom_r + (belly - bottom_r) * 0.55),
            (belly_z, belly),
            (bz + (cz - bz) * 0.85, belly * 0.84),
            (cz, rim_r + 0.006),
            (tz, rim_r),
        ]
    if r.body_form == "bell_lathe":
        base_r = r.belly_r
        neck_r = r.neck_r
        neck_z = bz + (tz - bz) * 0.93
        return [
            (bz, base_r * 0.80),
            (bz + (tz - bz) * 0.08, base_r),
            (bz + (tz - bz) * 0.33, base_r * 0.99),
            (bz + (tz - bz) * 0.63, base_r * 0.89),
            (neck_z, neck_r),
            (tz, neck_r + 0.004),
        ]
    # gooseneck_pour
    base_r = r.belly_r
    neck_r = r.neck_r
    neck_z = bz + (tz - bz) * 0.94
    return [
        (bz, base_r * 0.63),
        (bz + (tz - bz) * 0.07, base_r * 0.86),
        (bz + (tz - bz) * 0.20, base_r),
        (bz + (tz - bz) * 0.43, base_r * 0.98),
        (bz + (tz - bz) * 0.67, base_r * 0.77),
        (bz + (tz - bz) * 0.84, base_r * 0.54),
        (neck_z, neck_r),
        (tz, neck_r + 0.004),
    ]


def _body_r_at_z(r: ResolvedContainerKettleConfig, z: float) -> float:
    """Linear-interpolated outer body radius at height z (clamped to ends)."""
    prof = _outer_profile(r)
    if z <= prof[0][0]:
        return prof[0][1]
    if z >= prof[-1][0]:
        return prof[-1][1]
    for i in range(len(prof) - 1):
        z0, r0 = prof[i]
        z1, r1 = prof[i + 1]
        if z0 <= z <= z1:
            t = (z - z0) / (z1 - z0) if z1 > z0 else 0.0
            return r0 + t * (r1 - r0)
    return prof[-1][1]


# ---------------------------------------------------------------------------
# Spout helpers. Electric = collar flare (parent ``_spout``); stovetop bell =
# through-wall tapered tube + root fairing (parent ``_spout_solid``); gooseneck
# = short spline pour tube + fairing.
# ---------------------------------------------------------------------------
def _collar_spout_solid(r: ResolvedContainerKettleConfig) -> cq.Workplane:
    """Collar flare pour lip (electric). Rises from the collar at +X."""
    cz = r.collar_z
    base_x = r.neck_r - 0.012
    reach = 0.044 * r.spout_reach_scale
    outer = (
        cq.Workplane("YZ")
        .workplane(offset=base_x)
        .moveTo(0.0, cz + 0.006)
        .ellipse(0.020, 0.012)
        .workplane(offset=reach * 0.45)
        .moveTo(0.0, cz + 0.024)
        .ellipse(0.016, 0.010)
        .workplane(offset=reach * 0.32)
        .moveTo(0.0, cz + 0.040)
        .ellipse(0.011, 0.007)
        .loft(ruled=False)
    )
    inner = (
        cq.Workplane("YZ")
        .workplane(offset=base_x - 0.006)
        .moveTo(0.0, cz + 0.006)
        .ellipse(0.015, 0.009)
        .workplane(offset=reach * 0.50)
        .moveTo(0.0, cz + 0.024)
        .ellipse(0.012, 0.007)
        .workplane(offset=reach * 0.45)
        .moveTo(0.0, cz + 0.044)
        .ellipse(0.008, 0.005)
        .loft(ruled=False)
    )
    return outer.cut(inner)


def _tube_spout_axis(r: ResolvedContainerKettleConfig):
    """Root and tip of the stovetop through-wall tube spout (XZ plane)."""
    root = (r.belly_r * 0.96, 0.0, r.base_z + (r.rim_z - r.base_z) * 0.37)
    reach = 0.064 * r.spout_reach_scale
    rise = 0.050 * r.spout_reach_scale
    tip = (root[0] + reach, 0.0, root[2] + rise)
    dx, dz = tip[0] - root[0], tip[2] - root[2]
    length = math.hypot(dx, dz)
    ax = (dx / length, 0.0, dz / length)
    return root, tip, ax, length


def _tube_spout_solid(r: ResolvedContainerKettleConfig):
    root, _tip, ax, length = _tube_spout_axis(r)
    embed = 0.034
    r_root, r_tip = 0.024, 0.014
    start = (root[0] - ax[0] * embed, 0.0, root[2] - ax[2] * embed)
    plane = cq.Plane(origin=start, normal=ax)
    outer = (
        cq.Workplane(plane)
        .circle(r_root)
        .workplane(offset=length + embed)
        .circle(r_tip)
        .loft(ruled=True)
    )
    bore = _tube_spout_bore(r)
    return mesh_from_cadquery(outer.cut(bore), "spout")


def _tube_spout_bore(r: ResolvedContainerKettleConfig) -> cq.Workplane:
    root, _tip, ax, length = _tube_spout_axis(r)
    embed = 0.034
    bore_start = -embed - 0.006
    bore_end = length + 0.012
    start = (root[0] + ax[0] * bore_start, 0.0, root[2] + ax[2] * bore_start)
    plane = cq.Plane(origin=start, normal=ax)
    return (
        cq.Workplane(plane)
        .circle(0.016)
        .workplane(offset=bore_end - bore_start)
        .circle(0.008)
        .loft(ruled=True)
    )


def _tube_spout_fairing(r: ResolvedContainerKettleConfig):
    root, _tip, ax, _length = _tube_spout_axis(r)
    inset, outset = 0.024, 0.016
    start = (root[0] - ax[0] * inset, 0.0, root[2] - ax[2] * inset)
    plane = cq.Plane(origin=start, normal=ax)
    fairing = (
        cq.Workplane(plane)
        .circle(0.035)
        .workplane(offset=inset + outset)
        .circle(0.027)
        .loft(ruled=False)
    )
    return mesh_from_cadquery(fairing.cut(_tube_spout_bore(r)), "spout_root_fairing")


def _goose_spout_points(r: ResolvedContainerKettleConfig):
    """Short downturned spline pour spout points (gooseneck)."""
    x0 = r.belly_r * 0.93
    z0 = r.base_z + (r.rim_z - r.base_z) * 0.59
    reach = 0.104 * r.spout_reach_scale
    return [
        (x0, 0.0, z0),
        (x0 + reach * 0.26, 0.0, z0 + 0.020),
        (x0 + reach * 0.55, 0.0, z0 + 0.035),
        (x0 + reach * 0.83, 0.0, z0 + 0.036),
        (x0 + reach, 0.0, z0 + 0.026),
    ]


def _goose_spout_mesh(r: ResolvedContainerKettleConfig):
    pts = _goose_spout_points(r)
    tube = tube_from_spline_points(
        pts,
        radius=0.011,
        samples_per_segment=18,
        radial_segments=18,
        cap_ends=True,
        up_hint=(0.0, 0.0, 1.0),
    )
    return mesh_from_geometry(tube, "spout")


def _goose_fairing(r: ResolvedContainerKettleConfig):
    pts = _goose_spout_points(r)
    p0, p1 = pts[0], pts[1]
    dx, dz = p1[0] - p0[0], p1[2] - p0[2]
    length = math.hypot(dx, dz)
    ax = (dx / length, 0.0, dz / length)
    inset, outset = 0.012, 0.014
    start = (p0[0] - ax[0] * inset, 0.0, p0[2] - ax[2] * inset)
    plane = cq.Plane(origin=start, normal=ax)
    fairing = (
        cq.Workplane(plane)
        .circle(0.011 * 2.5)
        .workplane(offset=inset + outset)
        .circle(0.011 * 1.35)
        .loft(ruled=False)
    )
    return mesh_from_cadquery(fairing, "spout_root_fairing")


def _spout_tip(r: ResolvedContainerKettleConfig):
    """World tip + outward axis of the active spout (for whistle cap mount)."""
    if r.spout_kind == "tube":
        _root, tip, ax, _length = _tube_spout_axis(r)
        return tip, ax
    # goose
    pts = _goose_spout_points(r)
    p_prev, p_tip = pts[-2], pts[-1]
    dx, dz = p_tip[0] - p_prev[0], p_tip[2] - p_prev[2]
    length = math.hypot(dx, dz)
    return p_tip, (dx / length, 0.0, dz / length)


# ---------------------------------------------------------------------------
# Body emit (Slot A): shell + collar/heel + spout fixed visual, plus optional
# whistle_cap part for stovetop body forms.
# ---------------------------------------------------------------------------
def _collar_band(r: ResolvedContainerKettleConfig) -> cq.Workplane:
    """Black/steel collar band at the mouth (electric bodies)."""
    cz = r.collar_z
    return (
        cq.Workplane("XY")
        .workplane(offset=cz - 0.002)
        .circle(r.neck_r + 0.001)
        .extrude(r.rim_z - cz + 0.004)
        .faces(">Z")
        .workplane()
        .circle(r.neck_r - WALL)
        .cutThruAll()
    )


def _heel_ring(r: ResolvedContainerKettleConfig, *, docked: bool) -> cq.Workplane:
    """Bottom heel ring / heating plate skirt (electric bodies).

    When the body docks on a base (power base / trivet), the heel carries a
    center clearance bore for the base dock post (the cordless-kettle center
    connector recess)."""
    foot_r = max(r.neck_r, r.belly_r * 0.58)
    heel = (
        cq.Workplane("XY")
        .workplane(offset=r.base_z)
        .circle(foot_r)
        .extrude(0.014)
        .edges(">Z")
        .fillet(0.003)
    )
    if docked:
        bore = (
            cq.Workplane("XY")
            .workplane(offset=r.base_z - 0.002)
            .circle(_DOCK_CLEARANCE_R)
            .extrude(0.018)
        )
        heel = heel.cut(bore)
    return heel


def _emit_body(model, r, mats) -> "object":
    body = model.part("kettle_body")
    shell = _SHELL_BUILDERS[r.body_form](r)
    # Bodies that dock on a base (power base / trivet) carry a center dock
    # interface: a clearance bore through the shell floor + a receiver tube in
    # the cavity that the base dock post slides into (captured lift).
    docked = r.base_heating in ("cordless_power_base", "trivet_stand")

    if r.spout_kind == "collar":
        # front pour channel cut through the upper wall so the spout opens in.
        pour_cut = (
            cq.Workplane("XY")
            .workplane(offset=r.collar_z + 0.002)
            .center(r.neck_r - 0.006, 0.0)
            .rect(0.060, 0.020)
            .extrude(r.rim_z - r.collar_z + 0.030)
        )
        shell = shell.cut(pour_cut)

    if docked:
        floor_bore = (
            cq.Workplane("XY")
            .workplane(offset=r.base_z - 0.002)
            .circle(_DOCK_CLEARANCE_R)
            .extrude(WALL + 0.004)
        )
        shell = shell.cut(floor_bore)

    body.visual(mesh_from_cadquery(shell, "body_shell"), material=mats["body"], name="body_shell", material_class_id=("ceramic.decorative_glazed" if r.palette_style in {"matte_black_electric", "enamel_pastel", "enamel_red", "glossy_ceramic_white"} else "metal.stainless_matte"))

    # rim ring so the lid has a visible seat.
    rim = TorusGeometry(r.neck_r + 0.002, 0.006, radial_segments=12, tubular_segments=40)
    rim.translate(0.0, 0.0, r.rim_z)
    body.visual(mesh_from_geometry(rim, "top_rim"), material=mats["rim"], name="top_rim", material_class_id=("metal.stainless_matte" if r.palette_style in {"brushed_steel", "polished_stainless", "copper_stovetop", "enamel_pastel", "enamel_red", "cast_iron_trivet", "two_tone_cream_steel"} else "metal.blackened_gunmetal"))

    # spout fixed visual (type bound to body_form).
    if r.spout_kind == "collar":
        pour_cut = (
            cq.Workplane("XY")
            .workplane(offset=r.collar_z + 0.002)
            .center(r.neck_r - 0.006, 0.0)
            .rect(0.060, 0.020)
            .extrude(r.rim_z - r.collar_z + 0.030)
        )
        collar = _collar_band(r).cut(pour_cut)
        body.visual(
            mesh_from_cadquery(collar, "top_collar"), material=mats["rim"], name="top_collar", material_class_id=("metal.stainless_matte" if r.palette_style in {"brushed_steel", "polished_stainless", "copper_stovetop", "enamel_pastel", "enamel_red", "cast_iron_trivet", "two_tone_cream_steel"} else "metal.blackened_gunmetal")
        )
        body.visual(
            mesh_from_cadquery(_heel_ring(r, docked=docked), "base_collar"),
            material=mats["rim"],
            name="base_collar", material_class_id=("metal.stainless_matte" if r.palette_style in {"brushed_steel", "polished_stainless", "copper_stovetop", "enamel_pastel", "enamel_red", "cast_iron_trivet", "two_tone_cream_steel"} else "metal.blackened_gunmetal"),
        )
        body.visual(
            mesh_from_cadquery(_collar_spout_solid(r), "spout"),
            material=mats["spout"],
            name="spout", material_class_id=("metal.stainless_matte" if r.palette_style in {"brushed_steel", "polished_stainless", "matte_black_electric", "copper_stovetop", "enamel_pastel", "enamel_red", "cast_iron_trivet", "two_tone_cream_steel"} else "plastic.opaque_glossy_molded"),
        )
    elif r.spout_kind == "tube":
        body.visual(_tube_spout_solid(r), material=mats["spout"], name="spout", material_class_id=("metal.stainless_matte" if r.palette_style in {"brushed_steel", "polished_stainless", "matte_black_electric", "copper_stovetop", "enamel_pastel", "enamel_red", "cast_iron_trivet", "two_tone_cream_steel"} else "plastic.opaque_glossy_molded"))
        body.visual(_tube_spout_fairing(r), material=mats["rim"], name="spout_root_fairing", material_class_id=("metal.stainless_matte" if r.palette_style in {"brushed_steel", "polished_stainless", "copper_stovetop", "enamel_pastel", "enamel_red", "cast_iron_trivet", "two_tone_cream_steel"} else "metal.blackened_gunmetal"))
        body.visual(
            mesh_from_cadquery(_heel_ring(r, docked=docked), "base_collar"),
            material=mats["rim"],
            name="base_collar", material_class_id=("metal.stainless_matte" if r.palette_style in {"brushed_steel", "polished_stainless", "copper_stovetop", "enamel_pastel", "enamel_red", "cast_iron_trivet", "two_tone_cream_steel"} else "metal.blackened_gunmetal"),
        )
    else:  # goose
        body.visual(_goose_spout_mesh(r), material=mats["spout"], name="spout", material_class_id=("metal.stainless_matte" if r.palette_style in {"brushed_steel", "polished_stainless", "matte_black_electric", "copper_stovetop", "enamel_pastel", "enamel_red", "cast_iron_trivet", "two_tone_cream_steel"} else "plastic.opaque_glossy_molded"))
        body.visual(_goose_fairing(r), material=mats["rim"], name="spout_root_fairing", material_class_id=("metal.stainless_matte" if r.palette_style in {"brushed_steel", "polished_stainless", "copper_stovetop", "enamel_pastel", "enamel_red", "cast_iron_trivet", "two_tone_cream_steel"} else "metal.blackened_gunmetal"))
        body.visual(
            mesh_from_cadquery(_heel_ring(r, docked=docked), "base_collar"),
            material=mats["rim"],
            name="base_collar", material_class_id=("metal.stainless_matte" if r.palette_style in {"brushed_steel", "polished_stainless", "copper_stovetop", "enamel_pastel", "enamel_red", "cast_iron_trivet", "two_tone_cream_steel"} else "metal.blackened_gunmetal"),
        )

    if docked:
        # Receiver tube welded into the shell floor: the base dock post slides
        # in its bore so the body keeps support contact through the full lift.
        receiver = (
            cq.Workplane("XY")
            .workplane(offset=r.base_z)
            .circle(_DOCK_OUTER_R)
            .circle(_DOCK_BORE_R)
            .extrude(_DOCK_DEPTH)
        )
        body.visual(
            mesh_from_cadquery(receiver, "base_receiver"),
            material=mats["rim"],
            name="base_receiver", material_class_id=("metal.stainless_matte" if r.palette_style in {"brushed_steel", "polished_stainless", "copper_stovetop", "enamel_pastel", "enamel_red", "cast_iron_trivet", "two_tone_cream_steel"} else "metal.blackened_gunmetal"),
        )

    body.inertial = Inertial.from_geometry(
        Cylinder(max(r.belly_r, r.neck_r), r.rim_z),
        mass=0.9,
        origin=Origin(xyz=(0.0, 0.0, (r.base_z + r.rim_z) * 0.5)),
    )
    return body


def _emit_whistle_cap(model, body, r, mats) -> None:
    """Whistle flap at the spout tip (stovetop body forms only)."""
    tip, ax = _spout_tip(r)
    spout_ang = math.atan2(ax[2], ax[0])
    mouth_r = 0.014 + 0.002
    up = (-math.sin(spout_ang), math.cos(spout_ang))
    hinge = (tip[0] + mouth_r * up[0], 0.0, tip[2] + mouth_r * up[1])
    off = (tip[0] - hinge[0], 0.0, tip[2] - hinge[2])

    cap = model.part("whistle_cap")
    flap = CylinderGeometry(mouth_r, 0.005, radial_segments=22)
    flap.rotate_y(math.pi / 2.0 - spout_ang)
    flap.translate(off[0], 0.0, off[2])
    cap.visual(mesh_from_geometry(flap, "cap_flap"), material=mats["rim"], name="cap_flap", material_class_id=("metal.stainless_matte" if r.palette_style in {"brushed_steel", "polished_stainless", "copper_stovetop", "enamel_pastel", "enamel_red", "cast_iron_trivet", "two_tone_cream_steel"} else "metal.blackened_gunmetal"))
    tab = BoxGeometry((0.006, 0.012, 0.010))
    tab.rotate_y(math.pi / 2.0 - spout_ang)
    tab.translate(off[0] + ax[0] * 0.006, 0.0, off[2] + ax[2] * 0.006)
    cap.visual(mesh_from_geometry(tab, "cap_tab"), material=mats["grip"], name="cap_tab", material_class_id="plastic.opaque_generic")
    cap.inertial = Inertial.from_geometry(Cylinder(mouth_r, 0.008), mass=0.01)
    model.articulation(
        "spout_to_cap",
        ArticulationType.REVOLUTE,
        parent=body,
        child=cap,
        origin=Origin(xyz=hinge),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=2.0, velocity=3.0, lower=0.0, upper=1.4),
    )


# ---------------------------------------------------------------------------
# Base / root (Slot D): decides the root chain.
# ---------------------------------------------------------------------------
def _power_base_solid() -> cq.Workplane:
    disc = cq.Workplane("XY").circle(0.080).extrude(0.018).edges(">Z").fillet(0.006)
    boss = cq.Workplane("XY").workplane(offset=0.018).circle(0.030).extrude(0.006)
    return disc.union(boss)


def _emit_power_base(model, body, r, mats) -> "object":
    base = model.part("power_base")
    base.visual(
        mesh_from_cadquery(_power_base_solid(), "base_disc"),
        material=mats["base"],
        name="base_disc", material_class_id=("metal.stainless_matte" if r.palette_style in {"brushed_steel", "polished_stainless", "copper_stovetop", "enamel_pastel", "enamel_red", "cast_iron_trivet", "two_tone_cream_steel"} else "plastic.opaque_generic"),
    )
    base.visual(
        Box((0.050, 0.034, 0.004)),
        origin=Origin(xyz=(0.080 - 0.030, 0.0, 0.018 + 0.001)),
        material=mats["accent"],
        name="control_pad", material_class_id="tech.control_interface",
    )
    base.visual(
        mesh_from_geometry(
            CylinderGeometry(0.006, 0.003).translate(0.080 - 0.030, 0.0, 0.018 + 0.004),
            "power_button",
        ),
        material=mats["accent"],
        name="power_button", material_class_id="tech.control_interface",
    )
    lift = _POWER_BASE_LIFT * r.joint_travel_scale
    # Center dock post (the cordless-kettle connector): rises into the body
    # receiver tube and stays engaged through the full lift so the body keeps
    # support contact with the base at every travel pose.
    post_top = 0.018 + 0.005 + lift + 0.004
    post = CylinderGeometry(_DOCK_POST_R, post_top - 0.012, radial_segments=18)
    post.translate(0.0, 0.0, (post_top + 0.012) * 0.5)
    base.visual(
        mesh_from_geometry(post, "dock_post"),
        material=mats["base"],
        name="dock_post", material_class_id=("metal.stainless_matte" if r.palette_style in {"brushed_steel", "polished_stainless", "copper_stovetop", "enamel_pastel", "enamel_red", "cast_iron_trivet", "two_tone_cream_steel"} else "plastic.opaque_generic"),
    )
    base.inertial = Inertial.from_geometry(
        Cylinder(0.080, 0.018), mass=0.45, origin=Origin(xyz=(0.0, 0.0, 0.009))
    )
    # Body authored at base_z>0; place the lift origin on the base top and shift
    # the body down by base_z so its heel rests on the base at q=0.
    model.articulation(
        "body_lift",
        ArticulationType.PRISMATIC,
        parent=base,
        child=body,
        origin=Origin(xyz=(0.0, 0.0, 0.018 + 0.005 - r.base_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=60.0, velocity=0.2, lower=0.0, upper=lift),
    )
    return base


def _trivet_ring() -> cq.Workplane:
    leg_h = 0.020
    ring = (
        cq.Workplane("XY").circle(0.085).circle(0.055).extrude(0.008).translate((0.0, 0.0, leg_h))
    )
    # Two cross spokes spanning the open center to a small central seating boss
    # the kettle heel rests on (also gives the trivet real geometry at the
    # centerline for the trivet_to_body joint origin). The heat opening stays
    # visible between the spokes.
    spoke_a = (
        cq.Workplane("XY")
        .workplane(offset=leg_h)
        .box(2 * 0.085, 0.012, 0.008, centered=(True, True, False))
    )
    spoke_b = (
        cq.Workplane("XY")
        .workplane(offset=leg_h)
        .box(0.012, 2 * 0.085, 0.008, centered=(True, True, False))
    )
    boss = cq.Workplane("XY").workplane(offset=leg_h).circle(0.018).extrude(0.010)
    return ring.union(spoke_a).union(spoke_b).union(boss)


def _emit_trivet(model, body, r, mats) -> "object":
    leg_h = 0.020
    ring_thick = 0.008
    top_z = leg_h + ring_thick
    trivet = model.part("trivet_stand")
    trivet.visual(
        mesh_from_cadquery(_trivet_ring(), "trivet_ring"), material=mats["base"], name="trivet_ring", material_class_id="metal.cast_iron_bare"
    )
    for i in range(4):
        ang = i * math.pi / 2.0
        rr = (0.085 + 0.055) / 2.0
        leg = CylinderGeometry(0.012, leg_h, radial_segments=18)
        leg.translate(rr * math.cos(ang), rr * math.sin(ang), leg_h / 2.0)
        trivet.visual(
            mesh_from_geometry(leg, f"trivet_leg_{i}"),
            material=mats["base"],
            name=f"trivet_leg_{i}", material_class_id="metal.cast_iron_bare",
        )
    trivet.inertial = Inertial.from_geometry(
        Cylinder(0.085, top_z), mass=1.2, origin=Origin(xyz=(0.0, 0.0, top_z / 2.0))
    )
    lift = _TRIVET_LIFT * r.joint_travel_scale
    # Center dock post rising from the seating boss into the body receiver
    # tube; it stays engaged through the full lift so the body keeps support
    # contact with the trivet at every travel pose.
    post_top = top_z + lift + 0.004
    post = CylinderGeometry(_DOCK_POST_R, post_top - leg_h, radial_segments=18)
    post.translate(0.0, 0.0, (post_top + leg_h) * 0.5)
    trivet.visual(
        mesh_from_geometry(post, "dock_post"),
        material=mats["base"],
        name="dock_post", material_class_id="metal.cast_iron_bare",
    )
    model.articulation(
        "trivet_to_body",
        ArticulationType.PRISMATIC,
        parent=trivet,
        child=body,
        origin=Origin(xyz=(0.0, 0.0, top_z - r.base_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=40.0, velocity=0.3, lower=0.0, upper=lift),
    )
    return trivet


# ---------------------------------------------------------------------------
# Handle (Slot B).
# ---------------------------------------------------------------------------
def _bail_points(r: ResolvedContainerKettleConfig, my: float):
    crown = r.bail_crown_dz
    return [
        (0.0, my, 0.0),
        (0.006, my * 0.92, crown * 0.40),
        (0.008, my * 0.55, crown * 0.82),
        (0.008, 0.0, crown),
        (0.008, -my * 0.55, crown * 0.82),
        (0.006, -my * 0.92, crown * 0.40),
        (0.0, -my, 0.0),
    ]


def _emit_mount_lugs(body, r, mats) -> None:
    """Two shoulder lugs carrying a bail / folding handle pivot.

    Each lug is a horizontal boss that bridges from the body shell out to one
    bail-leg end. The lugs cross the kettle centerline at the bail mount line so
    the body has real geometry exactly at the handle joint origin
    (0,0,bail_mount_z)."""
    for sgn, nm in ((1.0, "mount_lug_0"), (-1.0, "mount_lug_1")):
        # Span from the centerline out to the bail leg seat (so the inner end
        # passes through x=y=0 at the mount line -> origin sits on real shell).
        half_len = r.mount_y + 0.006
        lug = CylinderGeometry(0.009, half_len, radial_segments=18).rotate_x(math.pi / 2.0)
        lug.translate(0.0, sgn * (half_len * 0.5), r.bail_mount_z)
        body.visual(mesh_from_geometry(lug, nm), material=mats["rim"], name=nm, material_class_id=("metal.stainless_matte" if r.palette_style in {"brushed_steel", "polished_stainless", "copper_stovetop", "enamel_pastel", "enamel_red", "cast_iron_trivet", "two_tone_cream_steel"} else "metal.blackened_gunmetal"))


def _emit_swing_bail(model, body, r, mats) -> None:
    _emit_mount_lugs(body, r, mats)
    my = r.mount_y
    crown = r.bail_crown_dz
    handle = model.part("bail_handle")
    bail = tube_from_spline_points(
        _bail_points(r, my), radius=0.006, samples_per_segment=16, radial_segments=14
    )
    handle.visual(mesh_from_geometry(bail, "bail_arch"), material=mats["body"], name="bail_arch", material_class_id=("ceramic.decorative_glazed" if r.palette_style in {"matte_black_electric", "enamel_pastel", "enamel_red", "glossy_ceramic_white"} else "metal.stainless_matte"))
    # Pivot rod along the mount line (handle-local z=0) so real child geometry
    # exists at the joint origin (the bail legs alone sit out at +/-Y).
    pivot_rod = CylinderGeometry(0.006, 2 * my + 0.006, radial_segments=14)
    pivot_rod.rotate_x(math.pi / 2.0)
    handle.visual(
        mesh_from_geometry(pivot_rod, "bail_pivot"), material=mats["rim"], name="bail_pivot", material_class_id=("metal.stainless_matte" if r.palette_style in {"brushed_steel", "polished_stainless", "copper_stovetop", "enamel_pastel", "enamel_red", "cast_iron_trivet", "two_tone_cream_steel"} else "metal.blackened_gunmetal")
    )
    grip_pts = [
        (0.008, 0.032, crown * 0.92),
        (0.008, 0.0, crown),
        (0.008, -0.032, crown * 0.92),
    ]
    grip = tube_from_spline_points(
        grip_pts, radius=0.011, samples_per_segment=14, radial_segments=16
    )
    handle.visual(
        mesh_from_geometry(grip, "grip_sleeve"), material=mats["grip"], name="grip_sleeve", material_class_id="rubber.smooth_plain"
    )
    handle.inertial = Inertial.from_geometry(
        Box((0.02, 2 * my, crown)), mass=0.06, origin=Origin(xyz=(0.0, 0.0, crown * 0.5))
    )
    # Axis (0,-1,0): positive travel swings the crown (rest +Z) toward -X (the
    # REAR), away from the +X pour spout — a real kettle bail lays back over the
    # heel, it does not fold down through its own spout.
    model.articulation(
        "body_to_handle",
        ArticulationType.REVOLUTE,
        parent=body,
        child=handle,
        origin=Origin(xyz=(0.0, 0.0, r.bail_mount_z)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(
            effort=3.0, velocity=3.0, lower=0.0, upper=_BAIL_UPPER * r.joint_travel_scale
        ),
    )


def _emit_folding_bail(model, body, r, mats) -> None:
    _emit_mount_lugs(body, r, mats)
    my = r.mount_y
    knuckle_x = 0.008
    # Legs splay OUTSIDE the lid radius so the upper grip clears the closure.
    knuckle_y_half = max(my * 0.70, r.neck_r + 0.020)
    # Knuckle line sits near the crown so the folding grip arch + pin ride well
    # above the lid knob (knob top ~ rim_z + 0.040).
    knuckle_z = r.bail_crown_dz * 0.94

    legs = model.part("bail_legs")
    for i, sgn in enumerate((1.0, -1.0)):
        pts = [
            (0.0, sgn * my, 0.0),
            (0.004, sgn * max(my * 0.92, knuckle_y_half + 0.004), knuckle_z * 0.36),
            (0.007, sgn * max(my * 0.80, knuckle_y_half), knuckle_z * 0.70),
            (knuckle_x, sgn * knuckle_y_half, knuckle_z),
        ]
        leg = tube_from_spline_points(pts, radius=0.005, samples_per_segment=12, radial_segments=12)
        legs.visual(mesh_from_geometry(leg, f"leg_{i}"), material=mats["body"], name=f"leg_{i}", material_class_id=("ceramic.decorative_glazed" if r.palette_style in {"matte_black_electric", "enamel_pastel", "enamel_red", "glossy_ceramic_white"} else "metal.stainless_matte"))
    # Pivot rod along the mount line (legs-local z=0) so child geometry exists at
    # the body_to_legs joint origin.
    legs_pivot = CylinderGeometry(0.006, 2 * my + 0.006, radial_segments=14)
    legs_pivot.rotate_x(math.pi / 2.0)
    legs.visual(
        mesh_from_geometry(legs_pivot, "legs_pivot"), material=mats["rim"], name="legs_pivot", material_class_id=("metal.stainless_matte" if r.palette_style in {"brushed_steel", "polished_stainless", "copper_stovetop", "enamel_pastel", "enamel_red", "cast_iron_trivet", "two_tone_cream_steel"} else "metal.blackened_gunmetal")
    )
    knuckle_bar = CylinderGeometry(0.006, 2 * knuckle_y_half + 0.008, radial_segments=16)
    knuckle_bar.rotate_x(math.pi / 2.0)
    knuckle_bar.translate(knuckle_x, 0.0, knuckle_z)
    legs.visual(
        mesh_from_geometry(knuckle_bar, "knuckle_bar"), material=mats["rim"], name="knuckle_bar", material_class_id=("metal.stainless_matte" if r.palette_style in {"brushed_steel", "polished_stainless", "copper_stovetop", "enamel_pastel", "enamel_red", "cast_iron_trivet", "two_tone_cream_steel"} else "metal.blackened_gunmetal")
    )
    legs.inertial = Inertial.from_geometry(
        Box((0.02, 2 * my, knuckle_z + 0.02)),
        mass=0.03,
        origin=Origin(xyz=(knuckle_x / 2.0, 0.0, knuckle_z / 2.0)),
    )
    # Axis (0,-1,0): the folding bail lays back toward -X (the REAR), away from
    # the +X pour spout / whistle cap, matching the swing_bail spine.
    model.articulation(
        "body_to_legs",
        ArticulationType.REVOLUTE,
        parent=body,
        child=legs,
        origin=Origin(xyz=(0.0, 0.0, r.bail_mount_z)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(
            effort=3.0, velocity=3.0, lower=0.0, upper=_BAIL_UPPER * r.joint_travel_scale
        ),
    )

    grip = model.part("bail_grip")
    arch_pts = [
        (0.0, knuckle_y_half, 0.0),
        (0.0, knuckle_y_half * 0.65, 0.020),
        (0.0, 0.0, 0.038),
        (0.0, -knuckle_y_half * 0.65, 0.020),
        (0.0, -knuckle_y_half, 0.0),
    ]
    arch = tube_from_spline_points(
        arch_pts, radius=0.005, samples_per_segment=14, radial_segments=12
    )
    grip.visual(mesh_from_geometry(arch, "grip_arch"), material=mats["body"], name="grip_arch", material_class_id=("ceramic.decorative_glazed" if r.palette_style in {"matte_black_electric", "enamel_pastel", "enamel_red", "glossy_ceramic_white"} else "metal.stainless_matte"))
    # Knuckle pin along the grip-local knuckle line (z=0) so child geometry sits
    # at the legs_to_grip joint origin.
    grip_pin = CylinderGeometry(0.005, 2 * knuckle_y_half + 0.004, radial_segments=12)
    grip_pin.rotate_x(math.pi / 2.0)
    grip.visual(mesh_from_geometry(grip_pin, "grip_pin"), material=mats["rim"], name="grip_pin", material_class_id=("metal.stainless_matte" if r.palette_style in {"brushed_steel", "polished_stainless", "copper_stovetop", "enamel_pastel", "enamel_red", "cast_iron_trivet", "two_tone_cream_steel"} else "metal.blackened_gunmetal"))
    sleeve_pts = [(0.0, 0.026, 0.026), (0.0, 0.0, 0.038), (0.0, -0.026, 0.026)]
    sleeve = tube_from_spline_points(
        sleeve_pts, radius=0.010, samples_per_segment=12, radial_segments=14
    )
    grip.visual(
        mesh_from_geometry(sleeve, "grip_sleeve"), material=mats["grip"], name="grip_sleeve", material_class_id="rubber.smooth_plain"
    )
    grip.inertial = Inertial.from_geometry(
        Box((0.02, 2 * knuckle_y_half, 0.04)), mass=0.03, origin=Origin(xyz=(0.0, 0.0, 0.009))
    )
    # Axis (0,-1,0): grip folds in the same rearward sense as the legs so the
    # folded assembly stays on the -X (rear) side, clear of the +X spout.
    model.articulation(
        "legs_to_grip",
        ArticulationType.REVOLUTE,
        parent=legs,
        child=grip,
        origin=Origin(xyz=(knuckle_x, 0.0, knuckle_z)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(
            effort=2.0, velocity=3.0, lower=0.0, upper=_BAIL_UPPER * r.joint_travel_scale
        ),
    )


def _emit_fixed_c_handle(model, body, r, mats) -> None:
    """Rear C handle as a fixed body visual (0 joint)."""
    grip_x = -(r.handle_reach)
    top_z = r.collar_z + 0.030
    bot_z = r.base_z + (r.rim_z - r.base_z) * 0.20

    def _strut(x0, z0, x1, z1):
        dx, dz = x1 - x0, z1 - z0
        length = math.hypot(dx, dz)
        ang = math.atan2(dz, dx)
        bar = cq.Workplane("XY").box(length, 0.024, 0.012).edges("|X").fillet(0.004)
        bar = bar.rotate((0, 0, 0), (0, 1, 0), -math.degrees(ang))
        bar = bar.translate(((x0 + x1) * 0.5, 0.0, (z0 + z1) * 0.5))
        return bar

    grip = (
        cq.Workplane("XY")
        .workplane(offset=bot_z)
        .center(grip_x, 0.0)
        .rect(0.016, 0.026)
        .workplane(offset=(top_z - bot_z) * 0.5)
        .center(0.004, 0.0)
        .rect(0.016, 0.028)
        .workplane(offset=(top_z - bot_z) * 0.5)
        .center(-0.004, 0.0)
        .rect(0.016, 0.026)
        .loft(ruled=False)
    )
    upper_attach_z = r.collar_z + 0.006
    lower_attach_z = bot_z + 0.020
    upper = _strut(grip_x, top_z - 0.004, -_body_r_at_z(r, upper_attach_z) + 0.004, upper_attach_z)
    lower = _strut(grip_x, bot_z + 0.006, -_body_r_at_z(r, lower_attach_z) + 0.004, lower_attach_z)
    handle_solid = grip.union(upper).union(lower)
    body.visual(mesh_from_cadquery(handle_solid, "handle"), material=mats["grip"], name="handle", material_class_id="plastic.opaque_generic")


def _emit_side_loop(model, body, r, mats) -> None:
    """Rear-quarter D-ring carry loop swinging about a vertical (+Z) axis."""
    lug_angle = math.radians(135.0)
    # Keep the lug pair on a body section where the shell radius is roughly
    # constant so the bosses always sit on real shell and the vertical pivot
    # line stays close to the body surface (the bell / pear taper otherwise
    # pulls the pivot >15mm off the narrow upper shell).
    span_lo = 0.30
    span_hi = 0.52
    lug_z_lower = r.base_z + (r.rim_z - r.base_z) * span_lo
    lug_z_upper = r.base_z + (r.rim_z - r.base_z) * span_hi
    lug_mid_z = (lug_z_upper + lug_z_lower) / 2.0
    half_span = (lug_z_upper - lug_z_lower) / 2.0
    # plant lugs on the actual shell radius at the lug mid height.
    shell_r = _body_r_at_z(r, lug_mid_z)
    lug_r_outer = shell_r + 0.010
    pivot_x = lug_r_outer * math.cos(lug_angle)
    pivot_y = lug_r_outer * math.sin(lug_angle)

    # two lug bosses on the body, +Y rear quarter, each rooted on the local
    # shell radius at its own height.
    for i, z_c in enumerate((lug_z_lower, lug_z_upper)):
        lug_start = _body_r_at_z(r, z_c) - 0.004
        lug = (
            cq.Workplane("YZ")
            .center(0.0, z_c)
            .circle(0.009)
            .extrude(0.010 + 0.004)
            .translate((lug_start, 0.0, 0.0))
        )
        lug = lug.edges(">X").fillet(0.002)
        lug = lug.rotate((0, 0, 0), (0, 0, 1), math.degrees(lug_angle))
        body.visual(mesh_from_cadquery(lug, f"lug_{i}"), material=mats["grip"], name=f"lug_{i}", material_class_id="plastic.opaque_generic")

    # D-ring carry loop in local frame (origin at pivot midpoint, +X outward).
    n = 9
    curve_pts = []
    for i in range(n):
        ang = (i / (n - 1)) * math.pi
        curve_pts.append((half_span * math.sin(ang), 0.0, half_span * math.cos(ang)))
    curved = tube_from_spline_points(
        curve_pts,
        radius=0.005,
        samples_per_segment=8,
        radial_segments=12,
        cap_ends=True,
        up_hint=(0.0, 1.0, 0.0),
    )
    bar = CylinderGeometry(0.005, half_span * 2, radial_segments=12, closed=True)
    upper_pin = CylinderGeometry(0.003, 0.005, radial_segments=8, closed=True)
    upper_pin.translate(0.0, 0.0, half_span + 0.0025)
    lower_pin = CylinderGeometry(0.003, 0.005, radial_segments=8, closed=True)
    lower_pin.translate(0.0, 0.0, -half_span - 0.0025)
    d_ring = curved.merge(bar).merge(upper_pin).merge(lower_pin)

    loop = model.part("carry_loop")
    loop.visual(mesh_from_geometry(d_ring, "d_ring"), material=mats["grip"], name="d_ring", material_class_id="plastic.opaque_generic")
    loop.inertial = Inertial.from_geometry(
        Cylinder(0.005 * 3, half_span * 2),
        mass=0.04,
        origin=Origin(xyz=(half_span * 0.5, 0.0, 0.0)),
    )
    model.articulation(
        "loop_pivot",
        ArticulationType.REVOLUTE,
        parent=body,
        child=loop,
        origin=Origin(xyz=(pivot_x, pivot_y, lug_mid_z), rpy=(0.0, 0.0, math.pi / 4.0)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(
            effort=3.0, velocity=2.0, lower=0.0, upper=_LOOP_UPPER * r.joint_travel_scale
        ),
    )


# ---------------------------------------------------------------------------
# Lid closure (Slot C).
# ---------------------------------------------------------------------------
def _liftoff_lid_mesh(r: ResolvedContainerKettleConfig):
    nr = r.neck_r
    lid = _loft_z(
        [
            (0.0, nr + 0.006),
            (0.006, nr + 0.002),
            (0.016, nr - 0.012),
            (0.024, nr - 0.030),
        ]
    )
    return mesh_from_cadquery(lid, "lid_dome")


def _emit_liftoff_knob(model, body, r, mats) -> None:
    # Anchor the +Z prismatic origin on the rim wall (real shell hardware), and
    # author the lid mesh shifted by -anchor so it re-centers on the kettle axis
    # after the off-axis origin is applied. lid-local z=0 is the rim plane.
    anchor = r.neck_r
    lid = model.part("lid")
    lid.visual(
        _liftoff_lid_mesh(r),
        material=mats["lid"],
        origin=Origin(xyz=(-anchor, 0.0, 0.0)),
        name="lid_dome", material_class_id=("metal.stainless_matte" if r.palette_style in {"brushed_steel", "polished_stainless", "matte_black_electric", "copper_stovetop", "cast_iron_trivet", "two_tone_cream_steel"} else "ceramic.decorative_glazed"),
    )
    stem = CylinderGeometry(0.006, 0.012, radial_segments=16)
    stem.translate(-anchor, 0.0, 0.030)
    lid.visual(mesh_from_geometry(stem, "knob_stem"), material=mats["grip"], name="knob_stem", material_class_id="plastic.opaque_generic")
    knob = SphereGeometry(0.011, width_segments=20, height_segments=14)
    knob.translate(-anchor, 0.0, 0.040)
    lid.visual(mesh_from_geometry(knob, "knob_ball"), material=mats["grip"], name="knob_ball", material_class_id="plastic.opaque_generic")
    lid.inertial = Inertial.from_geometry(
        Cylinder(r.neck_r, 0.024), mass=0.12, origin=Origin(xyz=(-anchor, 0.0, 0.012))
    )
    model.articulation(
        "body_to_lid",
        ArticulationType.PRISMATIC,
        parent=body,
        child=lid,
        origin=Origin(xyz=(anchor, 0.0, r.rim_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(
            effort=20.0, velocity=0.2, lower=0.0, upper=_LID_LIFT * r.joint_travel_scale
        ),
    )


def _emit_rear_flip(model, body, r, mats) -> None:
    lid_r = r.neck_r - 0.006
    disc = cq.Workplane("XY").circle(lid_r).extrude(0.008).edges(">Z").fillet(0.003)
    knob = (
        cq.Workplane("XY")
        .workplane(offset=0.008)
        .circle(0.012)
        .extrude(0.010)
        .edges(">Z")
        .fillet(0.004)
    )
    lid_solid = disc.union(knob).translate((lid_r, 0.0, 0.0))  # disc center forward of hinge

    lid = model.part("lid")
    lid.visual(mesh_from_cadquery(lid_solid, "lid_disc"), material=mats["lid"], name="lid_disc", material_class_id=("metal.stainless_matte" if r.palette_style in {"brushed_steel", "polished_stainless", "matte_black_electric", "copper_stovetop", "cast_iron_trivet", "two_tone_cream_steel"} else "ceramic.decorative_glazed"))
    knuckle = TorusGeometry(0.006, 0.004, radial_segments=12, tubular_segments=24).rotate_x(
        math.pi / 2.0
    )
    lid.visual(
        mesh_from_geometry(knuckle, "hinge_knuckle"), material=mats["grip"], name="hinge_knuckle", material_class_id="plastic.opaque_generic"
    )
    lid.inertial = Inertial.from_geometry(
        Cylinder(lid_r, 0.018), mass=0.05, origin=Origin(xyz=(lid_r, 0.0, 0.004))
    )
    hinge_x = -r.neck_r + 0.004
    hinge_z = r.rim_z + 0.006
    model.articulation(
        "lid_hinge",
        ArticulationType.REVOLUTE,
        parent=body,
        child=lid,
        origin=Origin(xyz=(hinge_x, 0.0, hinge_z)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(
            effort=4.0, velocity=2.0, lower=0.0, upper=_FLIP_UPPER * r.joint_travel_scale
        ),
    )


def _emit_screw_cap(model, body, r, mats) -> None:
    plug_r = r.neck_r - WALL - 0.006
    flange_r = r.neck_r - 0.001
    cap_seat_z = r.rim_z + 0.002

    # Rim seat collar on the body: a low ring ledge at the mouth that the twist
    # cap seats onto. It reaches inward to a small central bore so the body has
    # real geometry near the on-axis cap_twist origin (the open mouth alone is
    # hollow at the centerline). This is genuine kettle rim hardware.
    seat_inner = 0.008  # near-closed sealing ledge (the twist cap caps the mouth)
    seat = (
        cq.Workplane("XY")
        .workplane(offset=r.rim_z - 0.004)
        .circle(r.neck_r + 0.001)
        .circle(seat_inner)
        .extrude(0.006)
    )
    body.visual(mesh_from_cadquery(seat, "cap_seat"), material=mats["rim"], name="cap_seat", material_class_id=("metal.stainless_matte" if r.palette_style in {"brushed_steel", "polished_stainless", "copper_stovetop", "enamel_pastel", "enamel_red", "cast_iron_trivet", "two_tone_cream_steel"} else "metal.blackened_gunmetal"))

    plug = cq.Workplane("XY").workplane(offset=-0.012).circle(plug_r).extrude(0.012)
    thread = (
        cq.Workplane("XY")
        .workplane(offset=-0.008)
        .circle(plug_r + 0.002)
        .circle(plug_r - 0.001)
        .extrude(0.003)
    )
    flange = cq.Workplane("XY").circle(flange_r).extrude(0.004).edges(">Z").fillet(0.001)
    dome = (
        cq.Workplane("XY")
        .workplane(offset=0.004)
        .circle(flange_r - 0.003)
        .workplane(offset=0.005)
        .circle(flange_r * 0.55)
        .workplane(offset=0.005)
        .circle(0.010)
        .loft(ruled=False)
    )
    knob = (
        cq.Workplane("XY")
        .workplane(offset=0.014)
        .circle(0.009)
        .extrude(0.007)
        .edges(">Z")
        .fillet(0.003)
    )
    cap_solid = plug.union(thread).union(flange).union(dome).union(knob)

    cap = model.part("cap")
    cap.visual(mesh_from_cadquery(cap_solid, "cap_body"), material=mats["lid"], name="cap_body", material_class_id=("metal.stainless_matte" if r.palette_style in {"brushed_steel", "polished_stainless", "matte_black_electric", "copper_stovetop", "cast_iron_trivet", "two_tone_cream_steel"} else "ceramic.decorative_glazed"))
    # 3 bayonet lugs, first offset 60deg to avoid +X spout.
    lug_radial, lug_tangential, lug_h = 0.003, 0.008, 0.004
    base_lug = (
        cq.Workplane("XY")
        .workplane(offset=-0.009)
        .center(plug_r + lug_radial * 0.5, 0.0)
        .rect(lug_radial, lug_tangential)
        .extrude(lug_h)
    )
    for i in range(3):
        ang = 60.0 + i * 120.0
        lug = base_lug.rotate((0, 0, 0), (0, 0, 1), ang)
        cap.visual(
            mesh_from_cadquery(lug, f"cap_lug_{i}"), material=mats["accent"], name=f"cap_lug_{i}", material_class_id="metal.stainless_matte"
        )
    cap.inertial = Inertial.from_geometry(
        Cylinder(flange_r, 0.022), mass=0.04, origin=Origin(xyz=(0.0, 0.0, 0.004))
    )
    model.articulation(
        "cap_twist",
        ArticulationType.REVOLUTE,
        parent=body,
        child=cap,
        origin=Origin(xyz=(0.0, 0.0, cap_seat_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=3.0, velocity=2.0, lower=0.0, upper=_CAP_TWIST_UPPER),
    )


def _emit_hinged_pour_flap(model, body, r, mats) -> None:
    """Fixed dome (body visual) + a small front pour flap on a visible hinge."""
    nr = r.neck_r
    dome_top_z = 0.014
    pour_open_x = 0.50 * nr + 0.006
    pour_open_r = min(0.012, nr * 0.32)
    flap_thick = 0.003
    hinge_x = pour_open_x - pour_open_r - 0.004
    hinge_z = r.rim_z + dome_top_z + 0.001
    flap_center_x = pour_open_r + 0.006

    # Fixed lid dome on the body, with a front pour opening near the spout.
    dome = _loft_z(
        [
            (0.0, nr + 0.006),
            (0.004, nr + 0.003),
            (0.008, nr),
            (0.011, nr - 0.002),
            (dome_top_z, nr - 0.004),
        ]
    )
    opening = cq.Workplane("XY").center(pour_open_x, 0.0).circle(pour_open_r).extrude(0.025)
    dome = dome.cut(opening)
    body.visual(
        mesh_from_cadquery(dome, "lid_dome"),
        material=mats["lid"],
        origin=Origin(xyz=(0.0, 0.0, r.rim_z)),
        name="lid_dome", material_class_id=("metal.stainless_matte" if r.palette_style in {"brushed_steel", "polished_stainless", "matte_black_electric", "copper_stovetop", "cast_iron_trivet", "two_tone_cream_steel"} else "ceramic.decorative_glazed"),
    )
    pour_lip = TorusGeometry(pour_open_r + 0.002, 0.002, radial_segments=10, tubular_segments=32)
    pour_lip.translate(pour_open_x, 0.0, r.rim_z + dome_top_z)
    body.visual(mesh_from_geometry(pour_lip, "pour_lip"), material=mats["accent"], name="pour_lip", material_class_id=("metal.stainless_matte" if r.palette_style in {"brushed_steel", "polished_stainless", "copper_stovetop", "enamel_pastel", "enamel_red", "cast_iron_trivet", "two_tone_cream_steel"} else "metal.blackened_gunmetal"))

    knob_center_x = -0.20 * nr
    knob_base_z = r.rim_z + dome_top_z
    knob_top_z = knob_base_z + flap_thick + 0.014
    stem_h = knob_top_z - knob_base_z
    knob_stem = CylinderGeometry(0.004, stem_h, radial_segments=14)
    knob_stem.translate(knob_center_x, 0.0, knob_base_z + stem_h / 2.0)
    body.visual(mesh_from_geometry(knob_stem, "knob_stem"), material=mats["grip"], name="knob_stem", material_class_id="plastic.opaque_generic")
    knob_ball = SphereGeometry(0.007, width_segments=16, height_segments=12)
    knob_ball.translate(knob_center_x, 0.0, knob_top_z)
    body.visual(mesh_from_geometry(knob_ball, "knob_ball"), material=mats["grip"], name="knob_ball", material_class_id="plastic.opaque_generic")

    # Compact hinge ears on the fixed dome make the flap support visible.
    ear_t, ear_h = 0.004, 0.007
    for i in range(2):
        sgn = -1.0 if i == 0 else 1.0
        ear = BoxGeometry((ear_t, 0.004, ear_h))
        ear.translate(hinge_x, sgn * (pour_open_r - 0.002), hinge_z + ear_h / 2.0 - 0.003)
        body.visual(
            mesh_from_geometry(ear, f"hinge_ear_{i}"), material=mats["rim"], name=f"hinge_ear_{i}", material_class_id=("metal.stainless_matte" if r.palette_style in {"brushed_steel", "polished_stainless", "copper_stovetop", "enamel_pastel", "enamel_red", "cast_iron_trivet", "two_tone_cream_steel"} else "metal.blackened_gunmetal")
        )

    # Small pour flap: a low cover pad, a hinge barrel, and a front pull tab.
    flap_cover = (
        cq.Workplane("XY")
        .center(flap_center_x, 0.0)
        .circle(pour_open_r + 0.004)
        .extrude(flap_thick)
    )
    front_tab = (
        cq.Workplane("XY")
        .center(flap_center_x + pour_open_r + 0.004, 0.0)
        .rect(0.008, 0.010)
        .extrude(0.006)
    )
    flap_solid = flap_cover.union(front_tab)

    flap = model.part("pour_flap")
    flap.visual(
        mesh_from_cadquery(flap_solid, "flap_cover"), material=mats["rim"], name="flap_cover", material_class_id=("metal.stainless_matte" if r.palette_style in {"brushed_steel", "polished_stainless", "copper_stovetop", "enamel_pastel", "enamel_red", "cast_iron_trivet", "two_tone_cream_steel"} else "metal.blackened_gunmetal")
    )
    barrel = CylinderGeometry(0.003, (pour_open_r * 2.0) - 0.004, radial_segments=14)
    barrel.rotate_x(math.pi / 2.0)
    barrel.translate(0.0, 0.0, 0.003)
    flap.visual(
        mesh_from_geometry(barrel, "flap_hinge_barrel"),
        material=mats["grip"],
        name="flap_hinge_barrel", material_class_id="plastic.opaque_generic",
    )
    flap.inertial = Inertial.from_geometry(
        Cylinder(pour_open_r + 0.004, 0.010),
        mass=0.02,
        origin=Origin(xyz=(flap_center_x, 0.0, 0.003)),
    )
    model.articulation(
        "body_to_flap",
        ArticulationType.REVOLUTE,
        parent=body,
        child=flap,
        origin=Origin(xyz=(hinge_x, 0.0, hinge_z)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(
            effort=4.0, velocity=1.0, lower=0.0, upper=_POUR_FLAP_UPPER * r.joint_travel_scale
        ),
    )


_HANDLE_BUILDERS = {
    "swing_bail": _emit_swing_bail,
    "fixed_c_handle": _emit_fixed_c_handle,
    "folding_bail": _emit_folding_bail,
    "side_loop_handle": _emit_side_loop,
}
_LID_BUILDERS = {
    "liftoff_knob": _emit_liftoff_knob,
    "rear_flip_hinge": _emit_rear_flip,
    "screw_cap": _emit_screw_cap,
    "hinged_pour_flap": _emit_hinged_pour_flap,
}


# ---------------------------------------------------------------------------
# Build entry point
# ---------------------------------------------------------------------------
def build_container_kettle(
    config: ContainerKettleConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)

    pal = PALETTES[r.palette_style]
    mats = {
        "body": model.material(f"ck_body_{r.palette_style}_{pal.finish}", rgba=pal.body),
        "grip": model.material(f"ck_grip_{r.palette_style}", rgba=pal.grip),
        "lid": model.material(f"ck_lid_{r.palette_style}_{pal.finish}", rgba=pal.lid),
        "spout": model.material(f"ck_spout_{r.palette_style}", rgba=pal.spout),
        "rim": model.material(f"ck_rim_{r.palette_style}", rgba=pal.rim),
        "base": model.material(f"ck_base_{r.palette_style}", rgba=pal.base),
        "accent": model.material(f"ck_accent_{r.palette_style}", rgba=pal.accent),
    }

    # --- body shell + spout (+ whistle cap conditional on stovetop body) ----
    body = _emit_body(model, r, mats)

    # --- base / root chain (Slot D) decides the root ------------------------
    if r.base_heating == "cordless_power_base":
        _emit_power_base(model, body, r, mats)
    elif r.base_heating == "trivet_stand":
        _emit_trivet(model, body, r, mats)
    # flat_stovetop: body is the root (no base part / joint).

    # --- handle (Slot B) ----------------------------------------------------
    _HANDLE_BUILDERS[r.handle](model, body, r, mats)

    # --- lid closure (Slot C) -----------------------------------------------
    _LID_BUILDERS[r.lid_closure](model, body, r, mats)

    # --- whistle cap (conditional) ------------------------------------------
    if r.has_whistle:
        _emit_whistle_cap(model, body, r, mats)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_container_kettle(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_container_kettle(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests / QC. Captured-fit overlaps (lid skirt over rim, bail legs on lugs,
# cap plug in collar, pour flap on dome, spout fairing in shell, heel on base /
# trivet, dock post in the body receiver tube) are grandfathered via
# element-scoped allow_overlap; joint origins sit on real hinge / mount /
# collar / rim hardware. Each mechanism action is exercised.
# ---------------------------------------------------------------------------
def _ext(aabb):
    mn, mx = aabb
    return (mx[0] - mn[0], mx[1] - mn[1], mx[2] - mn[2])


def _has_visual(part, name: str) -> bool:
    try:
        return part.get_visual(name) is not None
    except Exception:
        return False


def _allow_dock_overlaps(ctx, body, base) -> None:
    """Allowances for the captured dock interface (base post + body receiver).

    The receiver tube is welded into the shell floor / heel ring, and the base
    dock post rides in its bore with a light press fit so the lifted body keeps
    support contact with the base through the full prismatic travel."""
    ctx.allow_overlap(
        body,
        body,
        elem_a="base_receiver",
        elem_b="body_shell",
        reason="The dock receiver tube is welded into the shell floor around the dock bore.",
    )
    ctx.allow_overlap(
        body,
        body,
        elem_a="base_receiver",
        elem_b="base_collar",
        reason="The dock receiver tube passes through the heel ring dock bore.",
    )
    ctx.allow_overlap(
        body,
        base,
        elem_a="base_receiver",
        elem_b="dock_post",
        reason="The base dock post slides inside the body receiver tube as a captured press-fit guide.",
    )


def run_container_kettle_tests(
    object_model: ArticulatedObject,
    config: ContainerKettleConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)

    body = object_model.get_part("kettle_body")

    # ---- body is a real hollow vessel with a spout ----
    body_aabb = ctx.part_world_aabb(body)
    bext = _ext(body_aabb)
    ctx.check(
        "kettle body has real volume",
        bext[0] > 0.05 and bext[1] > 0.05 and bext[2] > 0.05,
        details=f"body extents={bext}",
    )
    spout_aabb = ctx.part_element_world_aabb(body, elem="spout")
    # The spout must break past the mouth/neck radius at +X (collar spouts rise
    # from the rim, so they reach past the neck, not necessarily the wide belly).
    ctx.check(
        "pour spout projects out to the +X side past the mouth",
        spout_aabb is not None and spout_aabb[1][0] > r.neck_r,
        details=f"spout aabb={spout_aabb}, neck_r={r.neck_r:.4f}",
    )

    # spout fairing seats into the shell (stovetop body forms).
    if r.spout_kind in ("tube", "goose"):
        ctx.allow_overlap(
            body,
            body,
            elem_a="spout_root_fairing",
            elem_b="body_shell",
            reason="The spout root fairing penetrates the kettle shoulder as a welded saddle.",
        )
        ctx.allow_overlap(
            body,
            body,
            elem_a="spout",
            elem_b="spout_root_fairing",
            reason="The hollow spout tube passes through its welded root fairing.",
        )

    # ---- base / root chain ----
    if r.base_heating == "cordless_power_base":
        base = object_model.get_part("power_base")
        body_lift = object_model.get_articulation("body_lift")
        for elem_a in ("base_collar", "body_shell"):
            ctx.allow_overlap(
                body,
                base,
                elem_a=elem_a,
                elem_b="base_disc",
                reason="Kettle heel / shell bottom seats onto the power base when docked.",
            )
        _allow_dock_overlaps(ctx, body, base)
        ctx.check(
            "body_lift is PRISMATIC +Z",
            body_lift.articulation_type == ArticulationType.PRISMATIC
            and abs(body_lift.axis[2]) > 0.99,
            details=f"axis={body_lift.axis}, type={body_lift.articulation_type}",
        )
        rest = ctx.part_world_position(body)
        with ctx.pose({body_lift: _POWER_BASE_LIFT * r.joint_travel_scale}):
            lifted = ctx.part_world_position(body)
        ctx.check(
            "kettle body lifts up off the power base",
            lifted[2] > rest[2] + 0.02,
            details=f"rest_z={rest[2]:.4f}, lifted_z={lifted[2]:.4f}",
        )
    elif r.base_heating == "trivet_stand":
        trivet = object_model.get_part("trivet_stand")
        trivet_joint = object_model.get_articulation("trivet_to_body")
        for elem_a in ("base_collar", "body_shell"):
            ctx.allow_overlap(
                body,
                trivet,
                elem_a=elem_a,
                elem_b="trivet_ring",
                reason="Kettle heel / shell bottom seats onto the trivet ring when docked.",
            )
        _allow_dock_overlaps(ctx, body, trivet)
        ctx.check(
            "trivet_to_body is PRISMATIC +Z",
            trivet_joint.articulation_type == ArticulationType.PRISMATIC
            and abs(trivet_joint.axis[2]) > 0.99,
            details=f"axis={trivet_joint.axis}, type={trivet_joint.articulation_type}",
        )
        rest = ctx.part_world_position(body)
        with ctx.pose({trivet_joint: _TRIVET_LIFT * r.joint_travel_scale}):
            lifted = ctx.part_world_position(body)
        ctx.check(
            "kettle body lifts up off the trivet",
            lifted[2] > rest[2] + 0.03,
            details=f"rest_z={rest[2]:.4f}, lifted_z={lifted[2]:.4f}",
        )
    else:
        # flat_stovetop: body is the unique root and sits on the ground.
        ctx.check(
            "flat stovetop body rests near the ground",
            body_aabb[0][2] < 0.02,
            details=f"body min z={body_aabb[0][2]:.4f}",
        )

    # ---- handle mechanism ----
    if r.handle == "swing_bail":
        handle = object_model.get_part("bail_handle")
        joint = object_model.get_articulation("body_to_handle")
        for i in range(2):
            ctx.allow_overlap(
                handle,
                body,
                elem_a="bail_arch",
                elem_b=f"mount_lug_{i}",
                reason="Bail leg ends seat into the mount lugs that carry the pivot.",
            )
            ctx.allow_overlap(
                handle,
                body,
                elem_a="bail_pivot",
                elem_b=f"mount_lug_{i}",
                reason="Bail pivot rod runs through the mount lugs.",
            )
        for elem_b in ("body_shell", "top_collar"):
            if elem_b == "top_collar" and not _has_visual(body, "top_collar"):
                continue
            ctx.allow_overlap(
                handle,
                body,
                elem_a="bail_pivot",
                elem_b=elem_b,
                reason="The bail pivot rod spans the mount line through the shoulder shell/collar.",
            )
        ctx.check(
            "body_to_handle is REVOLUTE +Y",
            joint.articulation_type == ArticulationType.REVOLUTE and abs(joint.axis[1]) > 0.99,
            details=f"axis={joint.axis}",
        )
        rest_top = ctx.part_world_aabb(handle)[1][2]
        with ctx.pose({joint: 1.5}):
            down_top = ctx.part_world_aabb(handle)[1][2]
        ctx.check(
            "bail handle swings down to the side",
            down_top < rest_top - 0.02,
            details=f"rest_top={rest_top:.4f}, down_top={down_top:.4f}",
        )
    elif r.handle == "folding_bail":
        legs = object_model.get_part("bail_legs")
        grip = object_model.get_part("bail_grip")
        legs_joint = object_model.get_articulation("body_to_legs")
        grip_joint = object_model.get_articulation("legs_to_grip")
        for i in range(2):
            ctx.allow_overlap(
                legs,
                body,
                elem_a=f"leg_{i}",
                elem_b=f"mount_lug_{i}",
                reason="Bail leg lower ends seat into the mount lugs.",
            )
            ctx.allow_overlap(
                legs,
                body,
                elem_a="legs_pivot",
                elem_b=f"mount_lug_{i}",
                reason="Legs pivot rod runs through the mount lugs.",
            )
        for elem_b in ("body_shell", "top_collar"):
            if elem_b == "top_collar" and not _has_visual(body, "top_collar"):
                continue
            ctx.allow_overlap(
                legs,
                body,
                elem_a="legs_pivot",
                elem_b=elem_b,
                reason="The legs pivot rod spans the mount line through the shoulder shell/collar.",
            )
        ctx.allow_overlap(
            grip,
            legs,
            elem_a="grip_arch",
            elem_b="knuckle_bar",
            reason="Grip arch endpoints seat on the knuckle pin that carries the folding hinge.",
        )
        ctx.allow_overlap(
            grip,
            legs,
            elem_a="grip_pin",
            elem_b="knuckle_bar",
            reason="The grip knuckle pin nests on the legs' knuckle bar.",
        )
        for i in range(2):
            ctx.allow_overlap(
                grip,
                legs,
                elem_a="grip_pin",
                elem_b=f"leg_{i}",
                reason="The grip knuckle pin seats against the leg tops at the folding hinge.",
            )
            ctx.allow_overlap(
                grip,
                legs,
                elem_a="grip_arch",
                elem_b=f"leg_{i}",
                reason="The grip arch endpoints meet the leg tops at the folding knuckle.",
            )
        ctx.check(
            "body_to_legs and legs_to_grip are both REVOLUTE +Y",
            legs_joint.articulation_type == ArticulationType.REVOLUTE
            and abs(legs_joint.axis[1]) > 0.99
            and grip_joint.articulation_type == ArticulationType.REVOLUTE
            and abs(grip_joint.axis[1]) > 0.99,
            details=f"legs={legs_joint.axis}, grip={grip_joint.axis}",
        )
        rest_top = ctx.part_world_aabb(grip)[1][2]
        with ctx.pose({grip_joint: 1.4}):
            folded_top = ctx.part_world_aabb(grip)[1][2]
        ctx.check(
            "folding grip folds inward at the knuckle",
            folded_top < rest_top - 0.01,
            details=f"rest_top={rest_top:.4f}, folded_top={folded_top:.4f}",
        )
    elif r.handle == "side_loop_handle":
        loop = object_model.get_part("carry_loop")
        joint = object_model.get_articulation("loop_pivot")
        for i in range(2):
            ctx.allow_overlap(
                loop,
                body,
                elem_a="d_ring",
                elem_b=f"lug_{i}",
                reason="Carry loop pivot pin is captured in the lug bore.",
            )
        ctx.allow_overlap(
            loop,
            body,
            elem_a="d_ring",
            elem_b="body_shell",
            reason="At rest the carry loop folds flat against the body shell side.",
        )
        ctx.check(
            "loop_pivot is REVOLUTE +Z (vertical axis)",
            joint.articulation_type == ArticulationType.REVOLUTE and abs(joint.axis[2]) > 0.99,
            details=f"axis={joint.axis}",
        )

        def _radial(aabb):
            corners = [
                (aabb[0][0], aabb[0][1]),
                (aabb[0][0], aabb[1][1]),
                (aabb[1][0], aabb[0][1]),
                (aabb[1][0], aabb[1][1]),
            ]
            return max(math.hypot(x, y) for x, y in corners)

        rest_extent = _radial(ctx.part_world_aabb(loop))
        with ctx.pose({joint: _LOOP_UPPER * r.joint_travel_scale}):
            deployed_extent = _radial(ctx.part_world_aabb(loop))
        ctx.check(
            "carry loop deploys outward",
            deployed_extent > rest_extent + 0.003,
            details=f"rest={rest_extent:.4f}, deployed={deployed_extent:.4f}",
        )
    else:  # fixed_c_handle
        ctx.check(
            "fixed C-handle is a body visual on the rear (-X)",
            _has_visual(body, "handle"),
            details="handle visual not found",
        )
        handle_aabb = ctx.part_element_world_aabb(body, elem="handle")
        ctx.check(
            "fixed C-handle sits on the rear (-X) side",
            handle_aabb is not None and handle_aabb[0][0] < -r.belly_r,
            details=f"handle min_x={handle_aabb[0][0] if handle_aabb else None}",
        )

    # ---- lid closure mechanism ----
    if r.lid_closure == "liftoff_knob":
        lid = object_model.get_part("lid")
        joint = object_model.get_articulation("body_to_lid")
        ctx.allow_isolated_part(
            lid,
            reason="lid lifts off the kettle rim and loses body contact",
        )
        ctx.allow_overlap(
            lid,
            body,
            elem_a="lid_dome",
            elem_b="top_rim",
            reason="The lid skirt seats over the kettle rim when closed.",
        )
        ctx.check(
            "body_to_lid is PRISMATIC +Z",
            joint.articulation_type == ArticulationType.PRISMATIC and abs(joint.axis[2]) > 0.99,
            details=f"axis={joint.axis}",
        )
        rest_z = ctx.part_world_position(lid)[2]
        with ctx.pose({joint: _LID_LIFT * r.joint_travel_scale}):
            up_z = ctx.part_world_position(lid)[2]
        ctx.check(
            "lid lifts straight up off the kettle top",
            up_z > rest_z + (_LID_LIFT * r.joint_travel_scale) * 0.5,
            details=f"rest_z={rest_z:.4f}, up_z={up_z:.4f}",
        )
    elif r.lid_closure == "rear_flip_hinge":
        lid = object_model.get_part("lid")
        hinge = object_model.get_articulation("lid_hinge")
        ctx.allow_isolated_part(
            lid,
            reason="flip lid swings open on its hinge and loses body contact",
        )
        for elem_b in ("top_rim", "body_shell", "top_collar"):
            if elem_b == "top_collar" and not _has_visual(body, "top_collar"):
                continue
            ctx.allow_overlap(
                lid,
                body,
                elem_a="hinge_knuckle",
                elem_b=elem_b,
                reason="Rear hinge knuckle is captured at the body rim/collar hardware.",
            )
            ctx.allow_overlap(
                lid,
                body,
                elem_a="lid_disc",
                elem_b=elem_b,
                reason="Closed lid disc seats a hair into the mouth rim/collar.",
            )
        ctx.check(
            "lid_hinge is REVOLUTE (rear hinge, axis≈(0,-1,0))",
            hinge.articulation_type == ArticulationType.REVOLUTE and abs(hinge.axis[1]) > 0.99,
            details=f"axis={hinge.axis}",
        )
        top0 = ctx.part_world_aabb(lid)[1][2]
        with ctx.pose({hinge: 1.0 * r.joint_travel_scale}):
            top1 = ctx.part_world_aabb(lid)[1][2]
        ctx.check(
            "flip lid front edge lifts up when opened",
            top1 > top0 + 0.02,
            details=f"closed_top_z={top0:.4f}, open_top_z={top1:.4f}",
        )
    elif r.lid_closure == "screw_cap":
        cap = object_model.get_part("cap")
        twist = object_model.get_articulation("cap_twist")
        if _has_visual(body, "top_collar"):
            ctx.allow_overlap(
                cap,
                body,
                elem_a="cap_body",
                elem_b="top_collar",
                reason="Cap plug skirt inserts into the collar bore as a twist-lock fit.",
            )
        ctx.allow_overlap(
            cap,
            body,
            elem_a="cap_body",
            elem_b="top_rim",
            reason="Cap plug skirt inserts into the mouth rim as a twist-lock fit.",
        )
        ctx.allow_overlap(
            cap,
            body,
            elem_a="cap_body",
            elem_b="cap_seat",
            reason="Cap plug seats onto the rim seat collar ledge as a twist-lock fit.",
        )
        ctx.allow_overlap(
            cap,
            body,
            elem_a="cap_body",
            elem_b="body_shell",
            reason="Cap plug skirt inserts into the body mouth bore as a twist-lock fit.",
        )
        for i in range(3):
            for elem_b in ("cap_seat", "top_collar", "body_shell"):
                if elem_b == "top_collar" and not _has_visual(body, "top_collar"):
                    continue
                ctx.allow_overlap(
                    cap,
                    body,
                    elem_a=f"cap_lug_{i}",
                    elem_b=elem_b,
                    reason="Bayonet lugs engage the rim seat / collar bore as twist-lock teeth.",
                )
        ctx.check(
            "cap_twist is REVOLUTE +Z",
            twist.articulation_type == ArticulationType.REVOLUTE and abs(twist.axis[2]) > 0.99,
            details=f"axis={twist.axis}",
        )
        lug0_rest = ctx.part_element_world_aabb(cap, elem="cap_lug_0")
        rest_c = (
            (lug0_rest[0][0] + lug0_rest[1][0]) * 0.5,
            (lug0_rest[0][1] + lug0_rest[1][1]) * 0.5,
        )
        with ctx.pose({twist: _CAP_TWIST_UPPER}):
            lug0_t = ctx.part_element_world_aabb(cap, elem="cap_lug_0")
            twist_c = ((lug0_t[0][0] + lug0_t[1][0]) * 0.5, (lug0_t[0][1] + lug0_t[1][1]) * 0.5)
        ctx.check(
            "cap rotation sweeps lugs angularly about Z",
            math.hypot(twist_c[0] - rest_c[0], twist_c[1] - rest_c[1]) > 0.004,
            details=f"rest={rest_c}, twisted={twist_c}",
        )
    else:  # hinged_pour_flap
        flap = object_model.get_part("pour_flap")
        joint = object_model.get_articulation("body_to_flap")
        ctx.allow_overlap(
            flap,
            body,
            elem_a="flap_cover",
            elem_b="lid_dome",
            reason="The pour flap sits down onto the fixed lid dome when closed.",
        )
        ctx.allow_overlap(
            flap,
            body,
            elem_a="flap_hinge_barrel",
            elem_b="hinge_ear_0",
            reason="The flap hinge barrel is captured by the left hinge ear.",
        )
        ctx.check(
            "lid dome and hinge ears are fixed body visuals",
            _has_visual(body, "lid_dome")
            and _has_visual(body, "hinge_ear_0")
            and _has_visual(body, "hinge_ear_1"),
            details="lid dome or hinge ears not found",
        )
        lip_aabb = ctx.part_element_world_aabb(body, elem="pour_lip")
        ctx.check(
            "pour opening sits on the front (+X) side of the lid dome",
            lip_aabb is not None and ((lip_aabb[0][0] + lip_aabb[1][0]) * 0.5) > 0.0,
            details=f"pour_lip aabb={lip_aabb}",
        )
        ctx.allow_overlap(
            flap,
            body,
            elem_a="flap_hinge_barrel",
            elem_b="hinge_ear_1",
            reason="The flap hinge barrel is captured by the right hinge ear.",
        )
        ctx.check(
            "body_to_flap is REVOLUTE about the lateral hinge axis",
            joint.articulation_type == ArticulationType.REVOLUTE and abs(joint.axis[1]) > 0.99,
            details=f"axis={joint.axis}",
        )
        top0 = ctx.part_world_aabb(flap)[1][2]
        with ctx.pose({joint: _POUR_FLAP_UPPER * 0.75 * r.joint_travel_scale}):
            top1 = ctx.part_world_aabb(flap)[1][2]
        ctx.check(
            "pour flap swings upward to uncover the pour opening",
            top1 > top0 + 0.01,
            details=f"closed_top_z={top0:.4f}, open_top_z={top1:.4f}",
        )

    # ---- whistle cap (stovetop body forms) ----
    if r.has_whistle:
        cap = object_model.get_part("whistle_cap")
        cap_joint = object_model.get_articulation("spout_to_cap")
        ctx.allow_isolated_part(
            cap,
            reason="whistle cap flips open clear of the spout and loses contact",
        )
        ctx.allow_overlap(
            cap,
            body,
            elem_a="cap_flap",
            elem_b="spout",
            reason="The whistle flap caps the spout mouth when closed.",
        )
        ctx.check(
            "spout_to_cap is REVOLUTE",
            cap_joint.articulation_type == ArticulationType.REVOLUTE,
            details=f"type={cap_joint.articulation_type}",
        )

    # ---- single unique root (no part is a joint child of two parents) ----
    child_names = {
        (j.child if isinstance(j.child, str) else j.child.name) for j in object_model.articulations
    }
    roots = [p for p in object_model.parts if p.name not in child_names]
    ctx.check(
        "exactly one root part",
        len(roots) == 1,
        details=f"roots={[p.name for p in roots]}",
    )

    # ---- at least one non-fixed joint exists ----
    non_fixed = [
        j for j in object_model.articulations if j.articulation_type != ArticulationType.FIXED
    ]
    ctx.check(
        "at least one non-fixed mechanism joint exists",
        len(non_fixed) >= 1,
        details=f"non-fixed joints={[j.name for j in non_fixed]}",
    )

    return ctx.report()
