# SPDX-License-Identifier: Apache-2.0

"""Geared guitar machine head (0611 / guitar_tuning_peg_mechanism).

Design-backed rebuild.  Artifacts:

  * ``articraft_template_authoring/source_maps/pictureX_0611_guitar_tuning_peg_mechanism.md``
  * ``articraft_template_authoring/designs/pictureX_0611_guitar_tuning_peg_mechanism.json``
    (filled by ``scripts/design_fill/pictureX_0611_guitar_tuning_peg_mechanism.py``)

Frame convention
----------------
Adopted from the pool, not invented.  All thirteen source records build the same host:

  * the **worm turns about +Z** with its button on top of a vertical shaft;
  * the **string post turns about +Y**, perpendicular to and skew from the worm;
  * the post joint carries ``Mimic(worm_joint, -1/teeth)``.

Three of the five origins (002, 004, 005) put the decorated cover/screw face toward ``-Y``
and run the post out toward ``+Y``, so that majority is adopted -- and it is also the
octant the shared preview rig looks from (``front_iso`` sits at +X/-Y).

Tuner unit *i* lives at ``x_i = i * unit_pitch_m``:

  * the **driven wheel centre is the unit origin** ``(x_i, 0, 0)`` and the post axis runs
    ``(0, 1, 0)`` through it;
  * the **worm axis** runs ``(0, 0, 1)`` through ``(x_i - center_distance_m, 0, 0)``, i.e.
    the common perpendicular of the two skew axes lies along ``-X``.  Every source does
    this: 005 has ``GEAR_X=0.0055`` / ``WORM_X=-0.0045``, 003 has ``0.0032`` / ``-0.0065``.

Both rotors are authored **centred on their own joint origin** with their rotation axis as
a world-aligned local axis, which is what ``mate_axes`` + ``register_interface_mate``
require, and it puts the worm screw and the wheel on the same ``z = 0`` mesh plane exactly
as 005 does.

Why this file exists
--------------------
The template it replaces threw the mechanism away.  It rotated the whole machine (worm on
+X, post on +Z) so it matched none of the thirteen sources, and it modelled the one-start
worm as a plain ``Cylinder``, the involute worm wheel as a plain ``Cylinder``, the
cross-drilled string hole as a dark ``Box`` and every stamped plate as two ``Box`` strips.
``MECHANICAL_PRIORS.md`` section 1 forbids exactly that substitution, and the pool ships
the real generators -- ``Worm`` and ``SpurGear`` are imported by all thirteen records.

The mesh is the load-bearing derivation.  ``SpurGear.r0 = module * teeth / 2`` and
``Worm.r0 = module / (2 tan lead)`` (``sdk/v0/gears.py``), so tangent pitch circles mean
exactly ``center_distance_m = gear_pitch_r_m + worm_pitch_r_m``, and every station in the
assembly is measured from that.  Tooth tips interpenetrate by a fraction of a millimetre at
a volume orders of magnitude below the SDK threshold, so ``ctx.allow_overlap`` is neither
used nor needed -- which matters, because preflight blocks it for Design-backed templates.

One SDK note: passing ``bore_d`` / ``chamfer`` as ``build()`` params leaves stray
construction solids in the returned compound (measured: a 4.5 mm wheel comes back with a
25 mm tail).  This template therefore calls ``.build()`` bare -- which returns one clean
``Solid`` -- and cuts its own bores.
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
    AxisInterface,
    Cylinder,
    Mimic,
    MotionLimits,
    Origin,
    SpurGear,
    TemplateDomain,
    TestContext,
    TestReport,
    Worm,
    component_slot,
    corner_case,
    mate_axes,
    mesh_from_cadquery,
    multiplicity_slot,
    register_interface_mate,
)

# --------------------------------------------------------------------------- #
# Domain
# --------------------------------------------------------------------------- #
MountForm = Literal[
    "open_plate",
    "eared_plate",
    "sealed_housing",
    "die_cast_housing",
    "side_mount_bracket",
    "gearbox_bulb",
]
PostForm = Literal[
    "plain_post",
    "high_ratio_post",
    "locking_split_post",
    "classical_roller_post",
]
ButtonForm = Literal["paddle_button", "butterfly_button", "cloverleaf_button"]
PaletteStyle = Literal["polished_nickel", "polished_gold", "black_chrome", "aged_ivory"]

MOUNT_FORMS: tuple[MountForm, ...] = (
    "open_plate",
    "eared_plate",
    "sealed_housing",
    "die_cast_housing",
    "side_mount_bracket",
    "gearbox_bulb",
)
POST_FORMS: tuple[PostForm, ...] = (
    "plain_post",
    "high_ratio_post",
    "locking_split_post",
    "classical_roller_post",
)
BUTTON_FORMS: tuple[ButtonForm, ...] = (
    "paddle_button",
    "butterfly_button",
    "cloverleaf_button",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "polished_nickel",
    "polished_gold",
    "black_chrome",
    "aged_ivory",
)
TUNER_COUNTS: tuple[int, ...] = (1, 2, 3)

TEMPLATE_DOMAIN = TemplateDomain(
    slots=(
        component_slot("mount_form", MOUNT_FORMS),
        component_slot("post_form", POST_FORMS),
        component_slot("button_form", BUTTON_FORMS),
        multiplicity_slot("tuner_count", TUNER_COUNTS, item_slot="mount_form"),
    )
)

# Independent parameter ranges.  Every bound is a pool value; see the design fill script.
GEAR_MODULE_RANGE = (0.00070, 0.00125)
WORM_LEAD_RANGE = (0.140, 0.330)
MOUNT_WALL_RANGE = (0.0017, 0.0034)
WORM_SPAN_RANGE = (0.020, 0.040)
POST_REACH_RANGE = (0.022, 0.042)
BUTTON_REACH_RANGE = (0.011, 0.021)
BUTTON_THICK_RANGE = (0.0028, 0.0060)

# gear_teeth is candidate-local: the tooth count IS what separates the high-ratio fork
# from the baseline, so each post family owns its own band anchored on its own source.
POST_TEETH_RANGE: dict[PostForm, tuple[int, int]] = {
    "plain_post": (14, 19),  # 004 L279 z=14, 002 L282 z=19
    "high_ratio_post": (21, 30),  # open_back_ratio L355 z=21
    "locking_split_post": (14, 19),  # locking L282 z=19
    "classical_roller_post": (18, 24),  # roller L369 z=24
}

# Surface detail, not core/raw diversity.
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "polished_nickel": {
        "shell": (0.72, 0.74, 0.75, 1.0),
        "bright": (0.86, 0.87, 0.88, 1.0),
        "gear": (0.58, 0.60, 0.62, 1.0),
        "dark": (0.16, 0.17, 0.18, 1.0),
        "button": (0.80, 0.82, 0.83, 1.0),
    },
    "polished_gold": {
        "shell": (0.80, 0.58, 0.18, 1.0),
        "bright": (0.90, 0.72, 0.32, 1.0),
        "gear": (0.44, 0.40, 0.28, 1.0),
        "dark": (0.20, 0.14, 0.06, 1.0),
        "button": (0.88, 0.70, 0.30, 1.0),
    },
    "black_chrome": {
        "shell": (0.20, 0.21, 0.23, 1.0),
        "bright": (0.46, 0.48, 0.50, 1.0),
        "gear": (0.34, 0.35, 0.37, 1.0),
        "dark": (0.09, 0.09, 0.10, 1.0),
        "button": (0.26, 0.27, 0.29, 1.0),
    },
    "aged_ivory": {
        "shell": (0.70, 0.71, 0.72, 1.0),
        "bright": (0.84, 0.85, 0.86, 1.0),
        "gear": (0.86, 0.85, 0.78, 1.0),
        "dark": (0.18, 0.18, 0.17, 1.0),
        "button": (0.88, 0.83, 0.64, 1.0),
    },
}


# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class Config:
    mount_form: MountForm = "open_plate"
    post_form: PostForm = "plain_post"
    button_form: ButtonForm = "paddle_button"
    tuner_count: int = 1
    gear_module_m: float | None = None
    worm_lead_angle_rad: float | None = None
    mount_wall_m: float | None = None
    worm_span_m: float | None = None
    gear_teeth: int | None = None
    post_reach_m: float | None = None
    button_reach_m: float | None = None
    button_thick_m: float | None = None
    palette_style: PaletteStyle = "polished_nickel"
    name: str = "pictureX_0611_guitar_tuning_peg_mechanism"


@dataclass(frozen=True)
class ResolvedConfig:
    mount_form: MountForm
    post_form: PostForm
    button_form: ButtonForm
    tuner_count: int
    palette_style: PaletteStyle
    palette: dict[str, tuple[float, float, float, float]]
    # independent
    gear_module_m: float
    worm_lead_angle_rad: float
    mount_wall_m: float
    worm_span_m: float
    gear_teeth: int
    post_reach_m: float
    button_reach_m: float
    button_thick_m: float
    # derived -- gear train
    gear_pitch_r_m: float
    gear_tip_r_m: float
    gear_width_m: float
    worm_pitch_r_m: float
    worm_tip_r_m: float
    center_distance_m: float
    worm_ratio: float
    worm_len_m: float
    worm_shaft_r_m: float
    # derived -- mount
    worm_span_eff_m: float
    mount_top_z_m: float
    gear_chamber_r_m: float
    mount_body_r_m: float
    worm_boss_r_m: float
    worm_bore_r_m: float
    post_bore_r_m: float
    post_shank_r_m: float
    gear_hub_r_m: float
    post_exit_y_m: float
    post_barrel_y0_m: float
    shell_front_y_m: float
    chamber_front_y_m: float
    post_free_len_m: float
    unit_pitch_m: float
    mount_x0_m: float
    mount_x1_m: float
    # derived -- button
    button_seat_z_m: float
    button_bore_r_m: float
    name: str


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, float(value)))


def _pick(value, default, low, high):
    return default if value is None else _clamp(value, low, high)


def config_from_seed(seed: int) -> Config:
    rng = random.Random(int(seed) ^ 0x6D_51_C0_7A)
    choices = TEMPLATE_DOMAIN.sample(rng)
    post_form: PostForm = choices["post_form"]
    teeth_lo, teeth_hi = POST_TEETH_RANGE[post_form]
    return Config(
        mount_form=choices["mount_form"],
        post_form=post_form,
        button_form=choices["button_form"],
        tuner_count=int(choices["tuner_count"]),
        gear_module_m=round(rng.uniform(*GEAR_MODULE_RANGE), 6),
        worm_lead_angle_rad=round(rng.uniform(*WORM_LEAD_RANGE), 4),
        mount_wall_m=round(rng.uniform(*MOUNT_WALL_RANGE), 5),
        worm_span_m=round(rng.uniform(*WORM_SPAN_RANGE), 5),
        gear_teeth=rng.randint(teeth_lo, teeth_hi),
        post_reach_m=round(rng.uniform(*POST_REACH_RANGE), 5),
        button_reach_m=round(rng.uniform(*BUTTON_REACH_RANGE), 5),
        button_thick_m=round(rng.uniform(*BUTTON_THICK_RANGE), 5),
        palette_style=rng.choice(PALETTE_STYLES),
        name=f"guitar_tuning_peg_seed_{int(seed)}",
    )


def resolve_config(config: Config) -> ResolvedConfig:
    TEMPLATE_DOMAIN.validate(
        {
            "mount_form": config.mount_form,
            "post_form": config.post_form,
            "button_form": config.button_form,
            "tuner_count": config.tuner_count,
        }
    )
    if config.palette_style not in PALETTES:
        raise ValueError(f"unsupported palette_style: {config.palette_style}")

    def bounded(value, name, low, high):
        if value is not None and not low <= float(value) <= high:
            raise ValueError(f"{name} must be in [{low}, {high}]")

    bounded(config.gear_module_m, "gear_module_m", *GEAR_MODULE_RANGE)
    bounded(config.worm_lead_angle_rad, "worm_lead_angle_rad", *WORM_LEAD_RANGE)
    bounded(config.mount_wall_m, "mount_wall_m", *MOUNT_WALL_RANGE)
    bounded(config.worm_span_m, "worm_span_m", *WORM_SPAN_RANGE)
    bounded(config.post_reach_m, "post_reach_m", *POST_REACH_RANGE)
    bounded(config.button_reach_m, "button_reach_m", *BUTTON_REACH_RANGE)
    bounded(config.button_thick_m, "button_thick_m", *BUTTON_THICK_RANGE)

    teeth_lo, teeth_hi = POST_TEETH_RANGE[config.post_form]

    module = _pick(config.gear_module_m, 0.00100, *GEAR_MODULE_RANGE)
    lead = _pick(config.worm_lead_angle_rad, 0.290, *WORM_LEAD_RANGE)
    wall = _pick(config.mount_wall_m, 0.0022, *MOUNT_WALL_RANGE)
    span = _pick(config.worm_span_m, 0.028, *WORM_SPAN_RANGE)
    reach = _pick(config.post_reach_m, 0.034, *POST_REACH_RANGE)
    b_reach = _pick(config.button_reach_m, 0.0155, *BUTTON_REACH_RANGE)
    b_thick = _pick(config.button_thick_m, 0.0042, *BUTTON_THICK_RANGE)
    # gear_teeth is candidate-local, but it is drawn against the SEED's post_form while
    # production applies discrete overrides as a raw ``dataclasses.replace`` with no
    # re-resolution: an overridden post_form can inherit a tooth count drawn for another
    # fork's band.  The band belongs to whichever post_form is active, so the count is
    # clamped into it -- the same answer the seed path would have drawn for that fork --
    # instead of rejecting the combo outright.
    teeth_raw = config.gear_teeth if config.gear_teeth is not None else round(
        0.5 * (teeth_lo + teeth_hi)
    )
    teeth = max(teeth_lo, min(teeth_hi, int(teeth_raw)))
    count = int(config.tuner_count)

    # --- gear train ------------------------------------------------------- #
    # SpurGear.r0 = m * z / 2 and Worm.r0 = m / (2 tan lead) in sdk/v0/gears.py.
    gear_pitch_r = module * teeth / 2.0
    gear_tip_r = gear_pitch_r + module
    gear_width = _clamp(3.5 * module, 0.0032, 0.0055)
    worm_pitch_r = module / (2.0 * math.tan(lead))
    worm_tip_r = worm_pitch_r + module
    center_distance = gear_pitch_r + worm_pitch_r
    # Worm length tracks the MODULE, not the wheel radius: a worm is 15-22 modules long
    # across the pool (001 18/1.0, 002 27/1.2, 003 12/0.8, 004 16/1.0, 005 14.5/0.66).
    # Deriving it from gear_tip_r_m instead made the worm grow with the wheel, which is
    # neither true to the sources nor affordable -- every extra turn is ~2.5k triangles.
    worm_len = min(max(16.0 * module, 0.008), 0.62 * span)
    # A real worm is cut INTO its shaft, so the plain shaft has to reach the thread root
    # (r0 - 1.25 m).  Sizing it only from the tip leaves the thread floating up to 0.27 mm
    # clear of the shaft at the largest module and lowest lead angle, and the intra-part
    # connectivity check then reports the worm as an island inside its own rotor.
    worm_root_r = worm_pitch_r - 1.25 * module
    worm_shaft_r = max(_clamp(0.55 * worm_tip_r, 0.0013, 0.0026), worm_root_r + 0.0003)

    # --- mount ------------------------------------------------------------ #
    gear_chamber_r = gear_tip_r + 0.0012
    mount_body_r = gear_chamber_r + wall
    worm_boss_r = worm_tip_r + wall
    # The two worm bearings have to straddle the gear housing, so the span can never be
    # shorter than the housing's own diameter -- 001 puts its bearings 24 mm apart around
    # a 12 mm gear lobe.  This is what keeps the button above every mount silhouette.
    worm_span_eff = max(span, 2.0 * mount_body_r + 0.004)
    # The top of the mount is whichever rises higher at the worm station: the bearing seat
    # itself, or the boss/lobe wrapped around it.  On the stamped plates that lobe is a
    # full worm_boss_r disc, which can stand 4.8 mm proud of the bare seat -- more than the
    # 3 mm button standoff -- so taking only the seat here would bury the button.
    mount_top_z = 0.5 * worm_span_eff + max(1.5 * wall, worm_boss_r + 0.5 * wall)
    post_shank_r = _clamp(0.30 * gear_pitch_r, 0.0022, 0.0035)
    post_bore_r = post_shank_r + 0.0004
    worm_bore_r = worm_shaft_r + 0.0004
    gear_hub_r = min(post_shank_r + 0.0018, 0.55 * gear_pitch_r)
    post_exit_y = gear_width / 2.0 + 0.0008 + 2.0 * wall
    # A mount may protrude a post boss up to 0.6 mm past its +Y face, so every post
    # candidate starts its beyond-journal feature 1.6 mm out.  Without this the fatter
    # winding barrel starts inside the boss and the two parts interfere.
    post_barrel_y0 = post_exit_y + 0.0016
    # A sealed shell is deeper on the cover side than on the post side: the wheel hub and
    # the slotted gear screw both stand proud of the -Y wheel face and have to live inside
    # the chamber, or they punch through the cover (measured worst case: 3.96 mm).
    shell_front_y = gear_width / 2.0 + 0.0008 + 4.0 * wall
    chamber_front_y = gear_width / 2.0 + 0.0008 + 2.6 * wall
    unit_pitch = max(2.0 * gear_tip_r, 2.0 * b_reach, 2.0 * center_distance) + 0.005
    mount_x0 = -(center_distance + worm_boss_r + wall)
    mount_x1 = (count - 1) * unit_pitch + mount_body_r

    return ResolvedConfig(
        mount_form=config.mount_form,
        post_form=config.post_form,
        button_form=config.button_form,
        tuner_count=count,
        palette_style=config.palette_style,
        palette=dict(PALETTES[config.palette_style]),
        gear_module_m=module,
        worm_lead_angle_rad=lead,
        mount_wall_m=wall,
        worm_span_m=span,
        gear_teeth=teeth,
        post_reach_m=reach,
        button_reach_m=b_reach,
        button_thick_m=b_thick,
        gear_pitch_r_m=gear_pitch_r,
        gear_tip_r_m=gear_tip_r,
        gear_width_m=gear_width,
        worm_pitch_r_m=worm_pitch_r,
        worm_tip_r_m=worm_tip_r,
        center_distance_m=center_distance,
        worm_ratio=float(teeth),
        worm_len_m=worm_len,
        worm_shaft_r_m=worm_shaft_r,
        worm_span_eff_m=worm_span_eff,
        mount_top_z_m=mount_top_z,
        gear_chamber_r_m=gear_chamber_r,
        mount_body_r_m=mount_body_r,
        worm_boss_r_m=worm_boss_r,
        worm_bore_r_m=worm_bore_r,
        post_bore_r_m=post_bore_r,
        post_shank_r_m=post_shank_r,
        gear_hub_r_m=gear_hub_r,
        post_exit_y_m=post_exit_y,
        post_barrel_y0_m=post_barrel_y0,
        shell_front_y_m=shell_front_y,
        chamber_front_y_m=chamber_front_y,
        post_free_len_m=reach,
        unit_pitch_m=unit_pitch,
        mount_x0_m=mount_x0,
        mount_x1_m=mount_x1,
        button_seat_z_m=mount_top_z + 0.003,
        button_bore_r_m=worm_shaft_r,
        name=config.name,
    )


def slot_choices_for_config(config: Config | ResolvedConfig) -> tuple[tuple[str, object], ...]:
    return (
        ("mount_form", config.mount_form),
        ("post_form", config.post_form),
        ("button_form", config.button_form),
        ("tuner_count", config.tuner_count),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, object], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# --------------------------------------------------------------------------- #
# CadQuery helpers
# --------------------------------------------------------------------------- #
def _wp(shape) -> cq.Workplane:
    return shape if isinstance(shape, cq.Workplane) else cq.Workplane(obj=shape)


def _cyl_z(radius: float, length: float, center: tuple[float, float, float]) -> cq.Workplane:
    """Cylinder whose axis is +Z, centred on ``center``."""
    return cq.Workplane("XY").circle(radius).extrude(length / 2.0, both=True).translate(center)


def _cyl_y(radius: float, length: float, center: tuple[float, float, float]) -> cq.Workplane:
    """Cylinder whose axis is +Y, centred on ``center``."""
    return (
        cq.Workplane("XY")
        .circle(radius)
        .extrude(length / 2.0, both=True)
        .rotate((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), 90.0)
        .translate(center)
    )


def _cyl_x(radius: float, length: float, center: tuple[float, float, float]) -> cq.Workplane:
    """Cylinder whose axis is +X, centred on ``center``."""
    return (
        cq.Workplane("XY")
        .circle(radius)
        .extrude(length / 2.0, both=True)
        .rotate((0.0, 0.0, 0.0), (0.0, 1.0, 0.0), 90.0)
        .translate(center)
    )


def _ring_y(
    outer_r: float, inner_r: float, length: float, center: tuple[float, float, float]
) -> cq.Workplane:
    return _cyl_y(outer_r, length, center).cut(_cyl_y(inner_r, length + 0.004, center))


def _ring_z(
    outer_r: float, inner_r: float, length: float, center: tuple[float, float, float]
) -> cq.Workplane:
    return _cyl_z(outer_r, length, center).cut(_cyl_z(inner_r, length + 0.004, center))


def _try_fillet(shape: cq.Workplane, selector: str, radius: float) -> cq.Workplane:
    """Fillet if the kernel accepts it; a stamped outline stays credible without it."""
    try:
        return shape.edges(selector).fillet(radius)
    except Exception:
        return shape


def _mesh(
    shape,
    name: str,
    tolerance: float = 0.00025,
    *,
    unit_scale: float | None = None,
    angular_tolerance: float = 0.09,
):
    if unit_scale is None:
        return mesh_from_cadquery(
            shape, name, tolerance=tolerance, angular_tolerance=angular_tolerance
        )
    return mesh_from_cadquery(
        shape,
        name,
        unit_scale=unit_scale,
        tolerance=tolerance,
        angular_tolerance=angular_tolerance,
    )


# The involute generators are numerically unstable when driven at metre scale: measured
# across the domain, a wheel built in metres comes back with 28-96% of its nominal volume,
# is never watertight, and its tessellation falls into 3-24 disconnected components -- which
# the intra-part connectivity check (1e-6 m) then reports as floating islands.  Built in
# MILLIMETRES the same wheels are 97-99% of nominal, watertight and single-component.
# Origins 001, 003 and 004 all author their gear train in millimetres and hand
# ``unit_scale=0.001`` to ``mesh_from_cadquery`` for exactly this reason.
MM = 1000.0
# Tessellation of the two involute solids, in millimetres.  Both are spline-surfaced, so
# the triangle count is driven almost entirely by these numbers -- and the worm dominates
# the whole model: at 0.04 mm it alone is 52k triangles, more than five times the rest of
# the seed put together, and collision QC re-evaluates it at every sampled pose.  That is
# what pushed the worst seeds past the 60 s compile budget.  At 0.12 mm it is 20k and the
# thread is still clearly a thread; origin 003 L246 meshes its worm at exactly 0.12.
WORM_MESH_TOL_MM = 0.12
WORM_MESH_ANG = 0.16
WHEEL_MESH_TOL_MM = 0.10
WHEEL_MESH_ANG = 0.14


def _unit_x(r: ResolvedConfig, index: int) -> float:
    return index * r.unit_pitch_m


def _worm_x(r: ResolvedConfig, index: int) -> float:
    return _unit_x(r, index) - r.center_distance_m


def _wheel_near_y(r: ResolvedConfig) -> float:
    """The +Y station just past the wheel's own face, where the next feature may start.

    Every sealed cavity wall, plate span and reinforcement boss that sits right next to
    the spinning wheel is measured from here.  It used to be a bare ``gear_width_m/2 +
    0.0008`` -- 0.8 mm on its own, under the 1 mm the baseline QC still counts as
    "supported" rather than a real gap, and it read as the wheel touching its own housing
    wall in a render (measured: the reported nearest point between a die_cast_housing
    shell and its wheel sat exactly on this face, 0.8 mm apart, at every config).  Adding a
    full ``mount_wall_m`` -- the shell's own minimum wall thickness -- gives a clearance
    that is always comfortably load-bearing (1.7-3.4 mm mount_wall_m alone puts every
    config well clear of the 1 mm ambiguity band) instead of a magic constant.
    """
    return r.gear_width_m / 2.0 + 0.0008 + r.mount_wall_m


# --------------------------------------------------------------------------- #
# Gear-train solids (built once per seed, reused by every unit)
# --------------------------------------------------------------------------- #
def _worm_solid(r: ResolvedConfig) -> cq.Workplane:
    """One-start worm, generated along local X and stood upright on +Z.

    The vendored builder is axial along X and centred on the origin, so a single -90
    rotation about Y puts it on the vertical tuner shaft with its middle exactly on the
    z = 0 mesh plane -- 002 L240-L241, 005 L252-L254.

    Authored in millimetres (see MM above); the caller meshes it with unit_scale=0.001.
    """
    worm = Worm(
        module=r.gear_module_m * MM,
        lead_angle=math.degrees(r.worm_lead_angle_rad),
        n_threads=1,
        length=r.worm_len_m * MM,
        pressure_angle=20.0,
        backlash=0.06 * r.gear_module_m * MM,
    ).build()
    return _wp(worm).rotate((0.0, 0.0, 0.0), (0.0, 1.0, 0.0), -90.0)


def _wheel_solid(r: ResolvedConfig) -> cq.Workplane:
    """Driven involute wheel, generated along local Z and laid onto the +Y post axis.

    ``SpurGear.build()`` extrudes from z=0 to z=width, so it is first centred on its own
    face width and then rotated onto Y -- 002 L289-L290, 004 L286-L287.

    The wheel is deliberately left **unbored**.  ``bore_d`` as a build param leaves stray
    construction solids in the returned compound, and cutting the bore here instead is
    worse: a cylinder boolean against involute tooth faces segfaults OCC on 13 of 60
    sampled (module, teeth) combinations in this build.  The bore would be invisible
    regardless -- the post shank is unioned straight through the wheel inside the same
    part, and intra-part geometry is never collision-checked (MECHANICAL_PRIORS 1c).
    """
    gear = SpurGear(
        module=r.gear_module_m * MM,
        teeth_number=r.gear_teeth,
        width=r.gear_width_m * MM,
        pressure_angle=20.0,
        backlash=0.08 * r.gear_module_m * MM,
    ).build()
    body = _wp(gear).translate((0.0, 0.0, -r.gear_width_m * MM / 2.0))
    return body.rotate((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), 90.0)


# --------------------------------------------------------------------------- #
# mount_form candidates
#
# Each candidate returns ONE welded CadQuery solid covering every tuner unit.  Collision
# geometry is copied 1:1 from visuals, so a single welded mount solid is both cheaper and
# more detailed than a pile of overlapping primitives.
# --------------------------------------------------------------------------- #
def _mount_bores(r: ResolvedConfig, body: cq.Workplane) -> cq.Workplane:
    """The running passages every mount has to leave for the rotors.

    Three cuts, not two.  The plain shaft runs in a close bore, but over its threaded
    length the worm sweeps ``worm_tip_r_m``, which is up to 1.7 mm PROUDER than that bore.
    A mount that only bores for the shaft leaves stamping inside the thread envelope and
    the worm mills through it -- measured on seed 26 as 6.0 mm of penetration at
    8.95e-7 m3, over the 5e-7 volume gate.  MECHANICAL_PRIORS section 7: a moving member
    passing through its host needs a real slot in the host, not a nominal one.  The sealed
    candidates used to cut this themselves; it belongs to every candidate.

    The radial margin is 1.5 mm, not 0.8 mm.  The vendored worm's tessellated cut-off end
    face is not perfectly circular -- its polygon corners measured up to 7 microns proud
    of the nominal ``worm_tip_r_m`` on an independently drawn seed (209, outside the fixed
    36-seed/corner set), which the meshed FCL overlap check reports as a real, if
    threshold-grazing, contact (true CAD intersection 4.2e-8 m3, just over the 5e-7 gate
    once tessellation is added back in).  0.8 mm left only that much headroom above the
    excess; 1.5 mm comfortably absorbs it.
    """
    for index in range(r.tuner_count):
        x, worm_x = _unit_x(r, index), _worm_x(r, index)
        body = body.cut(_cyl_y(r.post_bore_r_m, 8.0 * r.post_exit_y_m, (x, 0.0, 0.0)))
        body = body.cut(_cyl_z(r.worm_bore_r_m, 2.4 * r.worm_span_eff_m, (worm_x, 0.0, 0.0)))
        body = body.cut(_cyl_z(r.worm_tip_r_m + 0.0015, r.worm_len_m + 0.004, (worm_x, 0.0, 0.0)))
    return body


def _plate_span_y(r: ResolvedConfig) -> tuple[float, float]:
    """A stamped plate stands behind the wheel; the post passes through it toward +Y."""
    near = _wheel_near_y(r)
    return near, r.post_exit_y_m


def _plate_blank(r: ResolvedConfig, half_height_ratio: float) -> cq.Workplane:
    """Filleted stamped body spanning the whole strip, with a lobe at each station."""
    near_y, far_y = _plate_span_y(r)
    thick = far_y - near_y
    mid_y = 0.5 * (near_y + far_y)
    length = r.mount_x1_m - r.mount_x0_m
    half_h = half_height_ratio * r.mount_body_r_m
    body = (
        cq.Workplane("XY")
        .box(length, thick, 2.0 * half_h)
        .translate((0.5 * (r.mount_x0_m + r.mount_x1_m), mid_y, 0.0))
    )
    body = _try_fillet(body, "|Y", min(0.0028, 0.45 * half_h))
    for index in range(r.tuner_count):
        # Gear lobe: the plate swells to enclose whichever wheel is fitted.
        body = body.union(_cyl_y(r.mount_body_r_m, thick, (_unit_x(r, index), mid_y, 0.0)))
        # Vertical spine carrying the two worm bearings, which straddle the lobe.
        body = body.union(
            cq.Workplane("XY")
            .box(2.0 * r.worm_boss_r_m, thick, r.worm_span_eff_m + 3.0 * r.mount_wall_m)
            .translate((_worm_x(r, index), mid_y, 0.0))
        )
    return body


def _mount_form_open_plate_build(r: ResolvedConfig) -> cq.Workplane:
    """001 L26-L73: a filleted stamped rectangle with a big gear lobe and a small lower
    lobe, pierced for the post journal and two screw clearances.  The worm runs in two
    free-standing annular bearings carried on bridge tabs, so the train stays visible."""
    near_y, far_y = _plate_span_y(r)
    thick = far_y - near_y
    mid_y = 0.5 * (near_y + far_y)
    body = _plate_blank(r, 0.80)
    for index in range(r.tuner_count):
        worm_x = _worm_x(r, index)
        # 001's lower lobe, and the matching upper one at the second bearing.
        for sign in (-1.0, 1.0):
            body = body.union(
                _cyl_y(
                    r.worm_boss_r_m,
                    thick,
                    (worm_x, mid_y, sign * 0.5 * r.worm_span_eff_m),
                )
            )
        # Two mounting-screw clearances through the plate.
        for sign in (-1.0, 1.0):
            body = body.cut(
                _cyl_y(
                    0.9 * r.mount_wall_m,
                    4.0 * thick,
                    (
                        _unit_x(r, index) + 0.62 * r.mount_body_r_m,
                        mid_y,
                        sign * 0.72 * r.mount_body_r_m,
                    ),
                )
            )
    return _mount_bores(r, body)


def _mount_form_eared_plate_build(r: ResolvedConfig) -> cq.Workplane:
    """002 L52-L132: a polyline stamped silhouette rather than a filleted rectangle, with
    rolled rims fused around the screw holes and the worm carried by two bent ears -- each
    a ring plus an arm block fused onto the plate face instead of a separate bearing."""
    near_y, far_y = _plate_span_y(r)
    thick = far_y - near_y
    mid_y = 0.5 * (near_y + far_y)
    half_h = 0.86 * r.mount_body_r_m
    # Stamped silhouette: a waisted outline drawn in XZ, not a plain box.
    x0, x1 = r.mount_x0_m, r.mount_x1_m
    outline = [
        (x0, -0.30 * half_h),
        (x0 + 0.10 * (x1 - x0), -0.86 * half_h),
        (x0 + 0.42 * (x1 - x0), -half_h),
        (x1 - 0.16 * (x1 - x0), -0.92 * half_h),
        (x1, -0.36 * half_h),
        (x1, 0.44 * half_h),
        (x1 - 0.14 * (x1 - x0), 0.94 * half_h),
        (x0 + 0.46 * (x1 - x0), half_h),
        (x0 + 0.12 * (x1 - x0), 0.88 * half_h),
        (x0, 0.40 * half_h),
    ]
    body = (
        cq.Workplane("XZ")
        .polyline(outline)
        .close()
        .extrude(thick / 2.0, both=True)
        .translate((0.0, mid_y, 0.0))
    )
    body = _try_fillet(body, "|Y", min(0.0022, 0.30 * half_h))
    for index in range(r.tuner_count):
        worm_x = _worm_x(r, index)
        body = body.union(_cyl_y(r.mount_body_r_m, thick, (_unit_x(r, index), mid_y, 0.0)))
        # The two bent ears: a ring at the bearing plus the arm that folds up to it.
        for sign in (-1.0, 1.0):
            z = sign * 0.5 * r.worm_span_eff_m
            body = body.union(
                _ring_z(r.worm_boss_r_m, r.worm_bore_r_m, 2.2 * r.mount_wall_m, (worm_x, mid_y, z))
            )
            body = body.union(
                cq.Workplane("XY")
                .box(2.0 * r.worm_boss_r_m, thick, abs(z) - 0.55 * half_h + 0.002)
                .translate((worm_x, mid_y, sign * 0.5 * (abs(z) + 0.55 * half_h - 0.002)))
            )
        # Rolled rims around the two mounting holes.
        for sign in (-1.0, 1.0):
            hole = (
                _unit_x(r, index) + 0.66 * r.mount_body_r_m,
                mid_y,
                sign * 0.70 * r.mount_body_r_m,
            )
            body = body.union(
                _ring_y(1.9 * r.mount_wall_m, 1.0 * r.mount_wall_m, 1.8 * thick, hole)
            )
            body = body.cut(_cyl_y(1.0 * r.mount_wall_m, 6.0 * thick, hole))
    return _mount_bores(r, body)


def _shell_span_y(r: ResolvedConfig) -> tuple[float, float]:
    """The -Y and +Y faces of a sealed shell.

    The shell is NOT symmetric about the wheel: the cover side has to be deep enough to
    swallow the wheel hub and the slotted gear screw, both of which stand proud of the -Y
    wheel face.  003 and 005 are asymmetric for the same reason -- their round cover is
    proud on the gear side while the post exits a flush bushing on the other.
    """
    return r.shell_front_y_m, r.post_exit_y_m


def _shell_cavity(r: ResolvedConfig, body: cq.Workplane) -> cq.Workplane:
    """Hollow the gear chamber and the worm passage out of a closed shell.

    This is the host adaptation that lets a 30-tooth high_ratio_post live inside the same
    sealed candidates as a 14-tooth wheel: the cavity is cut to gear_chamber_r_m, which is
    derived from whichever wheel arrived (003 L90-L95, 005 L72-L98).  It runs from the
    post-side face back to chamber_front_y_m, leaving 1.4 walls of cover in front of the
    hub rather than letting the hub punch through it.
    """
    y_far = -r.chamber_front_y_m
    y_near = _wheel_near_y(r)
    for index in range(r.tuner_count):
        body = body.cut(
            _cyl_y(
                r.gear_chamber_r_m,
                y_near - y_far,
                (_unit_x(r, index), 0.5 * (y_near + y_far), 0.0),
            )
        )
    return body


def _shell_block(r: ResolvedConfig) -> tuple[float, float]:
    """Depth and mid-y of a sealed shell's cross-section: y from -front_y to +back_y."""
    front_y, back_y = _shell_span_y(r)
    return front_y + back_y, 0.5 * (back_y - front_y)


def _worm_boss_z(r: ResolvedConfig, sign: float) -> tuple[float, float]:
    """Centre and length of the upper (+1) / lower (-1) worm bearing boss.

    Both end flush with ``mount_top_z_m``, which is what makes the 3 mm button standoff
    honest: no mount candidate is allowed to poke a boss into it.

    The inner end is capped at ``0.55 * mount_body_r_m`` so the boss is always rooted in
    the shell rather than floating above it.  Without that cap a long ``worm_span_m`` on a
    small wheel leaves a 10 mm gap between the two, and the intra-part connectivity check
    (1e-6 m) reports the boss as a disconnected island.

    The inner end is ALSO floored at ``gear_tip_r_m + 1.5mm``.  The boss sits offset from
    the wheel along X by exactly center_distance_m, but gear_chamber_r_m (the wheel's own
    clearance cylinder) and worm_boss_r_m are each bigger than their half of that offset by
    construction (both carry their own +module/+wall margin on top of the tangent pitch
    radii), so their footprints always overlap in the XY/XZ projection by roughly
    2*module + wall + 1.2mm regardless of station.  In 3D that only stays harmless if the
    boss and the wheel never share the same Z-band -- without this floor the boss's near
    edge dips inside the wheel's own Z-reach (measured 0.78 mm worst case), leaving a
    sliver of material so thin it reads as the boss touching the gear in a front-on
    render, even though it clears the 1 mm/5e-7 m3 overlap gate.
    """
    outer = r.mount_top_z_m
    inner = min(0.5 * r.worm_span_eff_m - 1.4 * r.mount_wall_m, 0.55 * r.mount_body_r_m)
    inner = max(inner, min(r.gear_tip_r_m + 0.0015, outer - 0.001))
    return sign * 0.5 * (outer + inner), outer - inner


def _shell_spine(r: ResolvedConfig, depth: float, mid_y: float) -> cq.Workplane:
    """The strip that ties per-unit shells into one mount.

    sealed_housing and gearbox_bulb build a block or bulb around each wheel, but
    unit_pitch_m is driven by the widest of the wheel, button and centre-distance
    envelopes, so at N>1 those bodies do not reach one another -- measured gaps of
    1.5-4.8 mm, which the intra-part connectivity check reports as separate islands.
    three_on_strip carries its three units on exactly this kind of continuous strip.
    """
    return (
        cq.Workplane("XY")
        .box(
            r.mount_x1_m - r.mount_x0_m,
            0.70 * depth,
            0.85 * r.mount_body_r_m,
        )
        .translate((0.5 * (r.mount_x0_m + r.mount_x1_m), mid_y, 0.0))
    )


def _mount_form_sealed_housing_build(r: ResolvedConfig) -> cq.Workplane:
    """003 L51-L105: a closed right-angle box with an elliptical loft shoulder rising to
    the worm boss and a round proud cover over the gear side."""
    depth, mid_y = _shell_block(r)
    body = _shell_spine(r, depth, mid_y)
    for index in range(r.tuner_count):
        x = _unit_x(r, index)
        worm_x = _worm_x(r, index)
        block = (
            cq.Workplane("XY")
            .box(2.0 * r.mount_body_r_m, depth, 2.0 * r.mount_body_r_m)
            .translate((x, mid_y, 0.0))
        )
        block = _try_fillet(block, "|Y", 0.30 * r.mount_body_r_m)
        # Lofted shoulder from the gear block up to the slim worm tower.
        shoulder = cq.Workplane(
            obj=cq.Solid.makeLoft(
                [
                    cq.Workplane("XY")
                    .ellipse(0.92 * r.mount_body_r_m, 0.46 * depth)
                    .val()
                    .translate(cq.Vector(x, mid_y, 0.35 * r.mount_body_r_m)),
                    cq.Workplane("XY")
                    .ellipse(0.70 * r.mount_body_r_m, 0.36 * depth)
                    .val()
                    .translate(cq.Vector(0.5 * (x + worm_x), mid_y, 0.90 * r.mount_body_r_m)),
                    cq.Workplane("XY")
                    .circle(r.worm_boss_r_m)
                    .val()
                    .translate(cq.Vector(worm_x, 0.0, r.mount_top_z_m - 2.2 * r.mount_wall_m)),
                ],
                True,
            )
        )
        unit = block.union(shoulder)
        for sign in (-1.0, 1.0):
            centre_z, length = _worm_boss_z(r, sign)
            unit = unit.union(_cyl_z(r.worm_boss_r_m, length, (worm_x, 0.0, centre_z)))
        body = body.union(unit)
    body = _shell_cavity(r, body)
    return _mount_bores(r, body)


def _mount_form_die_cast_housing_build(r: ResolvedConfig) -> cq.Workplane:
    """die_cast L26-L103: a filleted block with three protruding cylindrical bearing
    bosses -- worm above and below, post on the -Y face -- and a parting-line ridge.

    The block's own half-height has to reach past ``gear_tip_r_m + 1.5mm`` -- the floor
    ``_worm_boss_z`` now enforces for the boss's near edge -- or the boss welds onto
    nothing: past the block's half-height only the narrower wheel-wrap cylinder remains,
    and it tapers away from the worm station's X offset before reaching it.  1.90 (half
    1.90/2=0.95) clears the worst-case ratio measured across the domain (0.94) with
    margin; the old 1.72 (half 0.86) left the boss floating 0.36 mm short of the block on
    the tightest config (small module, thick wall) and read as a disconnected island.
    """
    depth, mid_y = _shell_block(r)
    length = r.mount_x1_m - r.mount_x0_m
    body = (
        cq.Workplane("XY")
        .box(length, depth, 1.90 * r.mount_body_r_m)
        .translate((0.5 * (r.mount_x0_m + r.mount_x1_m), mid_y, 0.0))
    )
    body = _try_fillet(body, "|Z", 0.34 * r.mount_body_r_m)
    for index in range(r.tuner_count):
        x = _unit_x(r, index)
        worm_x = _worm_x(r, index)
        body = body.union(_cyl_y(r.mount_body_r_m, depth, (x, mid_y, 0.0)))
        # The three die-cast bearing bosses, each standing proud of its own face.
        for sign in (-1.0, 1.0):
            centre_z, boss_len = _worm_boss_z(r, sign)
            body = body.union(_cyl_z(r.worm_boss_r_m, boss_len, (worm_x, 0.0, centre_z)))
        boss_y0 = _wheel_near_y(r)
        boss_y1 = r.post_exit_y_m + 0.0006
        body = body.union(
            _cyl_y(
                r.post_bore_r_m + 1.6 * r.mount_wall_m,
                boss_y1 - boss_y0,
                (x, 0.5 * (boss_y0 + boss_y1), 0.0),
            )
        )
        # Two mounting holes through the -Y cover face.
        for sign in (-1.0, 1.0):
            body = body.cut(
                _cyl_y(
                    0.85 * r.mount_wall_m,
                    4.0 * depth,
                    (x + 0.60 * r.mount_body_r_m, mid_y, sign * 0.60 * r.mount_body_r_m),
                )
            )
        # The parting-line ridge around the equator -- the die-cast split cue.
        body = body.union(
            cq.Workplane("XY")
            .box(2.06 * r.mount_body_r_m, depth + 0.0008, 0.5 * r.mount_wall_m)
            .translate((x, mid_y, 0.0))
        )
    body = _shell_cavity(r, body)
    return _mount_bores(r, body)


def _mount_form_side_mount_bracket_build(r: ResolvedConfig) -> cq.Workplane:
    """side_mount L51-L102: a narrow flat bracket only one wall thick with compact worm
    and post bearing bosses unioned on, and screw holes cut straight through."""
    near_y, far_y = _plate_span_y(r)
    thick = 0.62 * (far_y - near_y)
    mid_y = far_y - 0.5 * thick
    length = r.mount_x1_m - r.mount_x0_m
    body = (
        cq.Workplane("XY")
        .box(length, thick, r.worm_span_eff_m + 3.0 * r.mount_wall_m)
        .translate((0.5 * (r.mount_x0_m + r.mount_x1_m), mid_y, 0.0))
    )
    body = _try_fillet(body, "|Y", 0.0018)
    for index in range(r.tuner_count):
        x = _unit_x(r, index)
        worm_x = _worm_x(r, index)
        # Compact bosses instead of a full-depth plate lobe: the train is exposed on
        # both sides of a thin blade.
        for sign in (-1.0, 1.0):
            body = body.union(
                _cyl_z(
                    r.worm_boss_r_m,
                    2.4 * r.mount_wall_m,
                    (worm_x, mid_y, sign * 0.5 * r.worm_span_eff_m),
                )
            )
        boss_y0 = _wheel_near_y(r)
        boss_y1 = r.post_exit_y_m + 0.0006
        body = body.union(
            _cyl_y(
                r.post_bore_r_m + 1.5 * r.mount_wall_m,
                boss_y1 - boss_y0,
                (x, 0.5 * (boss_y0 + boss_y1), 0.0),
            )
        )
        for sign in (-1.0, 1.0):
            body = body.cut(
                _cyl_y(
                    0.75 * r.mount_wall_m,
                    6.0 * thick,
                    (x, mid_y, sign * (0.5 * r.worm_span_eff_m - 2.4 * r.mount_wall_m)),
                )
            )
    return _mount_bores(r, body)


def _mount_form_gearbox_bulb_build(r: ResolvedConfig) -> cq.Workplane:
    """005 L44-L98: a circular bulb around the wheel unioned with a tall cylindrical
    worm-bearing tower and a filleted shoulder joining them, then hollowed."""
    depth, mid_y = _shell_block(r)
    body = _shell_spine(r, depth, mid_y)
    for index in range(r.tuner_count):
        x = _unit_x(r, index)
        worm_x = _worm_x(r, index)
        bulb = _cyl_y(r.mount_body_r_m, depth, (x, mid_y, 0.0))
        tower = _cyl_z(r.worm_boss_r_m, 2.0 * r.mount_top_z_m, (worm_x, 0.0, 0.0))
        shoulder = (
            cq.Workplane("XY")
            .box(
                abs(x - worm_x) + 1.2 * r.worm_boss_r_m,
                0.75 * depth,
                1.15 * r.mount_body_r_m,
            )
            .translate((0.5 * (x + worm_x), mid_y, 0.0))
        )
        shoulder = _try_fillet(shoulder, "|Y", 0.26 * r.mount_body_r_m)
        body = body.union(bulb).union(tower).union(shoulder)
    body = _shell_cavity(r, body)
    return _mount_bores(r, body)


_MOUNT_SHAPES = {
    "open_plate": _mount_form_open_plate_build,
    "eared_plate": _mount_form_eared_plate_build,
    "sealed_housing": _mount_form_sealed_housing_build,
    "die_cast_housing": _mount_form_die_cast_housing_build,
    "side_mount_bracket": _mount_form_side_mount_bracket_build,
    "gearbox_bulb": _mount_form_gearbox_bulb_build,
}

# Which mounts close a shell over the train (cover on -Y) and which leave it open.
_SEALED_MOUNTS = frozenset({"sealed_housing", "die_cast_housing", "gearbox_bulb"})


def _mount_dress(mount, r: ResolvedConfig, mats: dict[str, str]) -> None:
    """Small named fittings that give each mount candidate a countable identity.

    These are separate visuals inside the mount part, which is free: collision is only
    computed between parts (MECHANICAL_PRIORS 1c), so attached fittings may sit straight
    in the host solid.
    """
    form = r.mount_form
    prefix = f"mount_form__{form}"
    near_y, far_y = _plate_span_y(r)
    # The sealed candidates dress their -Y cover face, which sits deeper than the
    # plate families' back face.
    cover_y = r.shell_front_y_m
    for index in range(r.tuner_count):
        x = _unit_x(r, index)
        worm_x = _worm_x(r, index)
        if form == "open_plate":
            # The free-standing annular worm bearings 001 carries on its bridge tabs.
            for k, sign in enumerate((-1.0, 1.0)):
                mount.visual(
                    _mesh(
                        _ring_z(
                            r.worm_boss_r_m + 0.0006,
                            r.worm_bore_r_m,
                            2.6 * r.mount_wall_m,
                            (worm_x, 0.5 * (near_y + far_y), sign * 0.5 * r.worm_span_eff_m),
                        ),
                        f"{prefix}__bearing_ring_{index}_{k}",
                        tolerance=0.00020,
                    ),
                    material=mats["bright"],
                    name=f"{prefix}__bearing_ring_{index}_{k}", material_class_id=("metal.chrome_polished" if r.palette_style in {"polished_nickel", "black_chrome", "aged_ivory"} else "metal.precious_gold"),
                )
            mount.visual(
                Cylinder(radius=1.9 * r.mount_wall_m, length=1.1 * r.mount_wall_m),
                origin=Origin(
                    xyz=(
                        x + 0.62 * r.mount_body_r_m,
                        near_y - 0.5 * r.mount_wall_m,
                        0.72 * r.mount_body_r_m,
                    ),
                    rpy=(math.pi / 2.0, 0.0, 0.0),
                ),
                material=mats["bright"],
                name=f"{prefix}__screw_head_{index}", material_class_id=("metal.chrome_polished" if r.palette_style in {"polished_nickel", "black_chrome", "aged_ivory"} else "metal.precious_gold"),
            )
        elif form == "eared_plate":
            for k, sign in enumerate((-1.0, 1.0)):
                mount.visual(
                    Cylinder(radius=1.6 * r.mount_wall_m, length=1.0 * r.mount_wall_m),
                    origin=Origin(
                        xyz=(
                            x + 0.66 * r.mount_body_r_m,
                            near_y - 0.4 * r.mount_wall_m,
                            sign * 0.70 * r.mount_body_r_m,
                        ),
                        rpy=(math.pi / 2.0, 0.0, 0.0),
                    ),
                    material=mats["bright"],
                    name=f"{prefix}__rim_screw_{index}_{k}", material_class_id=("metal.chrome_polished" if r.palette_style in {"polished_nickel", "black_chrome", "aged_ivory"} else "metal.precious_gold"),
                )
        elif form == "sealed_housing":
            mount.visual(
                _mesh(
                    _cyl_y(
                        0.86 * r.mount_body_r_m,
                        1.3 * r.mount_wall_m,
                        (x, -cover_y - 0.4 * r.mount_wall_m, 0.0),
                    ),
                    f"{prefix}__cover_{index}",
                    tolerance=0.00022,
                ),
                material=mats["bright"],
                name=f"{prefix}__cover_{index}", material_class_id=("metal.chrome_polished" if r.palette_style in {"polished_nickel", "black_chrome", "aged_ivory"} else "metal.precious_gold"),
            )
            for k, sign in enumerate((-1.0, 1.0)):
                mount.visual(
                    Cylinder(radius=0.7 * r.mount_wall_m, length=0.8 * r.mount_wall_m),
                    origin=Origin(
                        xyz=(x, -cover_y - 1.1 * r.mount_wall_m, sign * 0.62 * r.mount_body_r_m),
                        rpy=(math.pi / 2.0, 0.0, 0.0),
                    ),
                    material=mats["dark"],
                    name=f"{prefix}__cover_screw_{index}_{k}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"polished_nickel", "black_chrome", "aged_ivory"} else "metal.brass_aged"),
                )
        elif form == "die_cast_housing":
            for k, sign in enumerate((-1.0, 1.0)):
                mount.visual(
                    Cylinder(radius=1.5 * r.mount_wall_m, length=0.9 * r.mount_wall_m),
                    origin=Origin(
                        xyz=(
                            x + 0.60 * r.mount_body_r_m,
                            -cover_y - 0.35 * r.mount_wall_m,
                            sign * 0.60 * r.mount_body_r_m,
                        ),
                        rpy=(math.pi / 2.0, 0.0, 0.0),
                    ),
                    material=mats["bright"],
                    name=f"{prefix}__back_screw_{index}_{k}", material_class_id=("metal.chrome_polished" if r.palette_style in {"polished_nickel", "black_chrome", "aged_ivory"} else "metal.precious_gold"),
                )
        elif form == "side_mount_bracket":
            mid_y = far_y - 0.31 * (far_y - near_y)
            for k, sign in enumerate((-1.0, 1.0)):
                mount.visual(
                    Cylinder(radius=1.5 * r.mount_wall_m, length=0.7 * r.mount_wall_m),
                    origin=Origin(
                        xyz=(
                            x,
                            mid_y - 0.42 * (far_y - near_y),
                            sign * (0.5 * r.worm_span_eff_m - 2.4 * r.mount_wall_m),
                        ),
                        rpy=(math.pi / 2.0, 0.0, 0.0),
                    ),
                    material=mats["bright"],
                    name=f"{prefix}__leg_screw_{index}_{k}", material_class_id=("metal.chrome_polished" if r.palette_style in {"polished_nickel", "black_chrome", "aged_ivory"} else "metal.precious_gold"),
                )
        elif form == "gearbox_bulb":
            mount.visual(
                Cylinder(radius=0.80 * r.mount_body_r_m, length=1.0 * r.mount_wall_m),
                origin=Origin(
                    xyz=(x, -cover_y - 0.4 * r.mount_wall_m, 0.0),
                    rpy=(math.pi / 2.0, 0.0, 0.0),
                ),
                material=mats["bright"],
                name=f"{prefix}__medallion_{index}", material_class_id=("metal.chrome_polished" if r.palette_style in {"polished_nickel", "black_chrome", "aged_ivory"} else "metal.precious_gold"),
            )
            mount.visual(
                _mesh(
                    _ring_y(
                        0.88 * r.mount_body_r_m,
                        0.80 * r.mount_body_r_m,
                        1.6 * r.mount_wall_m,
                        (x, -cover_y - 0.3 * r.mount_wall_m, 0.0),
                    ),
                    f"{prefix}__bezel_{index}",
                    tolerance=0.00020,
                ),
                material=mats["gear"],
                name=f"{prefix}__bezel_{index}", material_class_id=("metal.stainless_matte" if r.palette_style in {"polished_nickel", "polished_gold", "black_chrome"} else "plastic.weathered_worn"),
            )
            for k, sign in enumerate((-1.0, 1.0)):
                mount.visual(
                    Cylinder(radius=0.7 * r.mount_wall_m, length=0.7 * r.mount_wall_m),
                    origin=Origin(
                        xyz=(
                            x + 0.52 * r.mount_body_r_m,
                            -cover_y - 0.9 * r.mount_wall_m,
                            sign * 0.52 * r.mount_body_r_m,
                        ),
                        rpy=(math.pi / 2.0, 0.0, 0.0),
                    ),
                    material=mats["dark"],
                    name=f"{prefix}__cover_screw_{index}_{k}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"polished_nickel", "black_chrome", "aged_ivory"} else "metal.brass_aged"),
                )


def _build_mount(model: ArticulatedObject, r: ResolvedConfig, mats: dict[str, str]):
    mount = model.part(
        "mount",
        meta={"role": "mount", "mount_form": r.mount_form, "tuner_count": r.tuner_count},
    )
    shape = _MOUNT_SHAPES[r.mount_form](r)
    mount.visual(
        _mesh(shape, f"mount_form__{r.mount_form}__shell", tolerance=0.00035),
        material=mats["shell"],
        name=f"mount_form__{r.mount_form}__shell", material_class_id=("metal.chrome_polished" if r.palette_style in {"polished_nickel", "black_chrome", "aged_ivory"} else "metal.precious_gold"),
    )
    _mount_dress(mount, r, mats)
    return mount


# --------------------------------------------------------------------------- #
# button_form candidates -- authored in the worm rotor's local frame, seated at
# button_seat_z_m so the blade always clears whatever mount is fitted.
# --------------------------------------------------------------------------- #
def _button_form_paddle_button_build(r: ResolvedConfig) -> cq.Workplane:
    """005 L101-L123: a broad filleted keystone blade with clipped lower shoulders,
    extruded in the plane that contains the shaft.  One solid blade, wide in X."""
    w = r.button_reach_m
    z0 = r.button_seat_z_m
    h = 1.55 * w
    profile = [
        (-0.24 * w, z0),
        (-w, z0 + 0.22 * h),
        (-0.93 * w, z0 + 0.80 * h),
        (-0.72 * w, z0 + h),
        (0.72 * w, z0 + h),
        (0.93 * w, z0 + 0.80 * h),
        (w, z0 + 0.22 * h),
        (0.24 * w, z0),
    ]
    blade = cq.Workplane("XZ").polyline(profile).close().extrude(r.button_thick_m / 2.0, both=True)
    blade = _try_fillet(blade, "|Y", 0.30 * r.button_thick_m)
    hub = _cyl_z(1.7 * r.button_bore_r_m, 0.34 * h, (0.0, 0.0, z0 + 0.17 * h))
    washer = (
        cq.Workplane("XZ")
        .center(0.0, z0 + 0.62 * h)
        .ellipse(0.30 * w, 0.16 * w)
        .extrude(0.25 * r.button_thick_m, both=True)
        .translate((0.0, -0.62 * r.button_thick_m, 0.0))
    )
    return blade.union(hub).union(washer)


def _button_form_butterfly_button_build(r: ResolvedConfig) -> cq.Workplane:
    """002 L135-L172: an ellipse unioned with a tapered lower web, pierced by four rotated
    elliptical windows that leave a central X-shaped load-carrying web.  The open windows
    are the identity -- this button has holes through it, the paddle does not."""
    w = r.button_reach_m
    z0 = r.button_seat_z_m
    h = 1.35 * w
    mid_z = z0 + 0.62 * h
    body = (
        cq.Workplane("XZ")
        .center(0.0, mid_z)
        .ellipse(w, 0.56 * h)
        .extrude(r.button_thick_m / 2.0, both=True)
    )
    web = (
        cq.Workplane("XZ")
        .polyline(
            [
                (-0.30 * w, mid_z - 0.30 * h),
                (0.30 * w, mid_z - 0.30 * h),
                (0.18 * w, z0),
                (-0.18 * w, z0),
            ]
        )
        .close()
        .extrude(r.button_thick_m / 2.0, both=True)
    )
    body = body.union(web)
    for sx, sz, angle in (
        (-1.0, 1.0, 24.0),
        (1.0, 1.0, -24.0),
        (-1.0, -1.0, -22.0),
        (1.0, -1.0, 22.0),
    ):
        cx, cz = sx * 0.52 * w, mid_z + sz * 0.17 * h
        window = (
            cq.Workplane("XZ")
            .center(cx, cz)
            .ellipse(0.34 * w, 0.17 * h)
            .extrude(2.0 * r.button_thick_m, both=True)
            .rotate((cx, 0.0, cz), (cx, 1.0, cz), angle)
        )
        body = body.cut(window)
    hub = _cyl_z(1.7 * r.button_bore_r_m, 0.40 * h, (0.0, 0.0, z0 + 0.20 * h))
    return body.union(hub)


def _button_form_cloverleaf_button_build(r: ResolvedConfig) -> cq.Workplane:
    """cloverleaf L108-L140: a centre disc unioned with four lobe cylinders at 90 degree
    spacing, lying PERPENDICULAR to the shaft rather than containing it, with a hub boss
    below.  Unlike the other two it sweeps a disc, so its silhouette is rotation-invariant."""
    w = r.button_reach_m
    z0 = r.button_seat_z_m
    lobe_r = 0.44 * w
    offset = w - lobe_r
    hub_len = 0.55 * w
    plate_z = z0 + hub_len + 0.5 * r.button_thick_m
    body = _cyl_z(0.52 * w, r.button_thick_m, (0.0, 0.0, plate_z))
    for k in range(4):
        angle = k * math.pi / 2.0
        body = body.union(
            _cyl_z(
                lobe_r,
                r.button_thick_m,
                (offset * math.cos(angle), offset * math.sin(angle), plate_z),
            )
        )
    body = _try_fillet(body, "|Z", 0.22 * lobe_r)
    hub = _cyl_z(1.9 * r.button_bore_r_m, hub_len, (0.0, 0.0, z0 + 0.5 * hub_len))
    body = body.union(hub)
    return body.cut(_cyl_z(r.button_bore_r_m, 2.0 * w, (0.0, 0.0, plate_z)))


_BUTTON_SHAPES = {
    "paddle_button": _button_form_paddle_button_build,
    "butterfly_button": _button_form_butterfly_button_build,
    "cloverleaf_button": _button_form_cloverleaf_button_build,
}


# --------------------------------------------------------------------------- #
# worm rotor -- shared host geometry plus the active button
# --------------------------------------------------------------------------- #
def _build_worm_rotor(
    model: ArticulatedObject,
    r: ResolvedConfig,
    mats: dict[str, str],
    mount,
    index: int,
    worm_mesh,
):
    """One worm rotor: shaft, one-start worm and button, all turning about local +Z.

    The rotor is authored centred on its own joint origin, so its local z is world z and
    the worm screw sits exactly on the z = 0 mesh plane.
    """
    rotor = model.part(
        f"worm_rotor_{index}",
        meta={"role": "worm_rotor", "button_form": r.button_form, "unit": index},
    )
    shaft_top = r.button_seat_z_m + 0.5 * r.button_reach_m
    shaft_bottom = -0.5 * r.worm_span_eff_m - 2.0 * r.mount_wall_m
    rotor.visual(
        Cylinder(radius=r.worm_shaft_r_m, length=shaft_top - shaft_bottom),
        origin=Origin(xyz=(0.0, 0.0, 0.5 * (shaft_top + shaft_bottom))),
        material=mats["bright"],
        name=f"worm_rotor__shaft_{index}", material_class_id=("metal.chrome_polished" if r.palette_style in {"polished_nickel", "black_chrome", "aged_ivory"} else "metal.precious_gold"),
    )
    rotor.visual(
        worm_mesh,
        material=mats["gear"],
        name=f"worm_rotor__worm_{index}", material_class_id=("metal.stainless_matte" if r.palette_style in {"polished_nickel", "polished_gold", "black_chrome"} else "plastic.weathered_worn"),
    )
    # Thrust collar seating on the upper bearing -- 002 L252, 005 L266.  It sits in the
    # 3 mm standoff between the mount top and the button, so it is measured from
    # mount_top_z_m rather than from the bare bearing seat, which the boss can bury.
    collar_len = min(1.2 * r.mount_wall_m, 0.0016)
    rotor.visual(
        Cylinder(radius=1.75 * r.worm_shaft_r_m, length=collar_len),
        origin=Origin(
            xyz=(0.0, 0.0, r.mount_top_z_m + 0.0002 + 0.5 * collar_len),
        ),
        material=mats["bright"],
        name=f"worm_rotor__thrust_collar_{index}", material_class_id=("metal.chrome_polished" if r.palette_style in {"polished_nickel", "black_chrome", "aged_ivory"} else "metal.precious_gold"),
    )
    rotor.visual(
        _mesh(
            _BUTTON_SHAPES[r.button_form](r),
            f"button_form__{r.button_form}__button_{index}",
            tolerance=0.00022,
        ),
        material=mats["button"],
        name=f"button_form__{r.button_form}__button_{index}", material_class_id=("metal.chrome_polished" if r.palette_style in {"polished_nickel", "polished_gold", "black_chrome"} else "plastic.weathered_worn"),
    )

    mate = mate_axes(
        AxisInterface(
            name=f"mount.worm_bearing_axis_{index}",
            point=(_worm_x(r, index), 0.0, 0.0),
            axis=(0.0, 0.0, 1.0),
            radial=(1.0, 0.0, 0.0),
            radius=r.worm_bore_r_m,
        ),
        AxisInterface(
            name=f"worm_rotor_{index}.shaft",
            point=(0.0, 0.0, 0.0),
            axis=(0.0, 0.0, 1.0),
            radial=(1.0, 0.0, 0.0),
            radius=r.worm_shaft_r_m,
        ),
    )
    joint = model.articulation(
        f"mount_to_worm_{index}",
        ArticulationType.CONTINUOUS,
        parent=mount,
        child=rotor,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(effort=0.6, velocity=9.0),
        meta={"positive_motion": "turning the button winds the string post"},
    )
    register_interface_mate(model, joint.name, mate)
    return rotor, joint


# --------------------------------------------------------------------------- #
# post_form candidates -- authored in the post rotor's local frame with the
# wheel centre at the origin and the rotation axis on local +Y.
# --------------------------------------------------------------------------- #
def _post_core(r: ResolvedConfig, tail_len: float) -> cq.Workplane:
    """Hub on the -Y wheel face plus the shank running out through the journal."""
    hub = _cyl_y(r.gear_hub_r_m, 1.3 * r.mount_wall_m, (0.0, -0.5 * r.gear_width_m, 0.0))
    shank_start = -0.5 * r.gear_width_m
    shank_end = r.post_exit_y_m + tail_len
    shank = _cyl_y(
        r.post_shank_r_m,
        shank_end - shank_start,
        (0.0, 0.5 * (shank_start + shank_end), 0.0),
    )
    return hub.union(shank)


def _gear_screw(r: ResolvedConfig) -> cq.Workplane:
    """Slotted screw closing the wheel on the -Y face -- 002 L188-L194, 004 L313-L317."""
    y = -0.5 * r.gear_width_m - 1.0 * r.mount_wall_m
    head = _cyl_y(1.5 * r.post_shank_r_m, 0.8 * r.mount_wall_m, (0.0, y, 0.0))
    slot = (
        cq.Workplane("XY")
        .box(3.0 * r.post_shank_r_m, 0.32 * r.post_shank_r_m, 0.30 * r.mount_wall_m)
        .translate((0.0, y - 0.30 * r.mount_wall_m, 0.0))
    )
    return head.cut(slot)


def _post_form_plain_post_build(r: ResolvedConfig) -> cq.Workplane:
    """004 L268-L328 with 002's drilled hole L175-L185: the wheel on a hub, a stepped
    shank through the journal, and a larger winding post beyond it with a cross-drilled
    string hole."""
    body = _post_core(r, 0.10 * r.post_free_len_m)
    barrel_r = post_barrel_r = 1.55 * r.post_shank_r_m
    y0 = r.post_barrel_y0_m
    y1 = r.post_exit_y_m + r.post_free_len_m
    body = body.union(_cyl_y(barrel_r, y1 - y0, (0.0, 0.5 * (y0 + y1), 0.0)))
    # The cross-drilled string hole near the exposed tip.
    body = body.cut(
        _cyl_x(0.30 * post_barrel_r, 6.0 * post_barrel_r, (0.0, y1 - 0.22 * (y1 - y0), 0.0))
    )
    return body.union(_gear_screw(r))


def _post_form_high_ratio_post_build(r: ResolvedConfig) -> cq.Workplane:
    """open_back_ratio L352-L414: the same construction carrying a much larger wheel, plus
    the stepped bearing collar the taller support needs between wheel face and journal."""
    body = _post_core(r, 0.10 * r.post_free_len_m)
    # Stepped bearing collar at the journal mouth.  It has to sit OUTSIDE the bore: it
    # is fatter than post_bore_r_m by up to 2 mm, so inside the journal it would drive
    # straight into the mount.
    body = body.union(
        _cyl_y(
            r.post_shank_r_m + 0.7 * r.mount_wall_m,
            2.2 * r.mount_wall_m,
            (0.0, r.post_barrel_y0_m + 1.1 * r.mount_wall_m, 0.0),
        )
    )
    barrel_r = 1.70 * r.post_shank_r_m
    y0 = r.post_barrel_y0_m
    y1 = r.post_exit_y_m + r.post_free_len_m
    body = body.union(_cyl_y(barrel_r, y1 - y0, (0.0, 0.5 * (y0 + y1), 0.0)))
    body = body.cut(_cyl_x(0.28 * barrel_r, 6.0 * barrel_r, (0.0, y1 - 0.20 * (y1 - y0), 0.0)))
    return body.union(_gear_screw(r))


def _split_post_outer_r(r: ResolvedConfig) -> float:
    return 1.75 * r.post_shank_r_m


def _post_form_locking_split_post_build(r: ResolvedConfig) -> cq.Workplane:
    """locking L170-L215: beyond the journal the winding post is a hollow tube whose wall
    is slit for 70% of its height, so the walls can flex when the screw is tightened."""
    body = _post_core(r, 0.10 * r.post_free_len_m)
    outer_r = _split_post_outer_r(r)
    inner_r = 0.44 * outer_r
    y0 = r.post_barrel_y0_m
    y1 = r.post_exit_y_m + r.post_free_len_m
    tube = _cyl_y(outer_r, y1 - y0, (0.0, 0.5 * (y0 + y1), 0.0))
    tube = tube.cut(_cyl_y(inner_r, y1 - y0 + 0.004, (0.0, 0.5 * (y0 + y1), 0.0)))
    # The slit: a thin radial slot from the tip down 70% of the tube.
    slit_len = 0.70 * (y1 - y0)
    slit = (
        cq.Workplane("XY")
        .box(outer_r - inner_r + 0.0006, slit_len, 0.9 * inner_r)
        .translate((0.5 * (inner_r + outer_r), y1 - 0.5 * slit_len, 0.0))
    )
    tube = tube.cut(slit)
    # Cross-drilled string entry near the tube root.
    tube = tube.cut(_cyl_x(0.26 * outer_r, 6.0 * outer_r, (0.0, y0 + 0.22 * (y1 - y0), 0.0)))
    return body.union(tube).union(_gear_screw(r))


def _locking_screw_shape(r: ResolvedConfig) -> cq.Workplane:
    """locking L217-L251: a cap head with a hex socket and a clamping shaft stub.

    Authored centred on its own joint origin with the rotation axis on local +Y.
    """
    outer_r = _split_post_outer_r(r)
    head_r = 1.15 * outer_r
    head_len = 1.9 * r.mount_wall_m
    head = _cyl_y(head_r, head_len, (0.0, 0.5 * head_len - 0.0002, 0.0))
    socket = (
        cq.Workplane("XZ")
        .polygon(6, 1.05 * outer_r)
        .extrude(-0.55 * head_len)
        .translate((0.0, head_len - 0.0002, 0.0))
    )
    head = head.cut(socket)
    stub_len = 3.4 * r.mount_wall_m
    stub = _cyl_y(0.40 * outer_r, stub_len, (0.0, -0.5 * stub_len, 0.0))
    return head.union(stub)


def _post_form_classical_roller_post_build(r: ResolvedConfig) -> cq.Workplane:
    """roller L135-L192: instead of an upright post the shank carries a fork -- a collar,
    a bridge plate and two prongs along +Y with a transverse axle at their tips -- spanned
    by a barrel roller lying along X."""
    body = _post_core(r, 0.10 * r.post_free_len_m)
    y0 = r.post_barrel_y0_m
    y1 = r.post_exit_y_m + r.post_free_len_m
    span = 2.4 * r.post_shank_r_m
    prong_half = 0.42 * r.post_shank_r_m
    collar_len = 0.22 * (y1 - y0)
    body = body.union(
        _cyl_y(1.35 * r.post_shank_r_m, collar_len, (0.0, y0 + 0.5 * collar_len, 0.0))
    )
    bridge_len = 0.16 * (y1 - y0)
    body = body.union(
        cq.Workplane("XY")
        .box(2.0 * span, bridge_len, 1.6 * prong_half)
        .translate((0.0, y0 + collar_len + 0.5 * bridge_len, 0.0))
    )
    prong_y0 = y0 + collar_len + bridge_len
    for sign in (-1.0, 1.0):
        body = body.union(
            cq.Workplane("XY")
            .box(2.0 * prong_half, y1 - prong_y0, 2.0 * prong_half)
            .translate((sign * span, prong_y0 + 0.5 * (y1 - prong_y0), 0.0))
        )
    # Transverse axle through both prong tips, and the roller barrel on it.
    axle_y = y1 - 1.2 * prong_half
    body = body.union(_cyl_x(0.55 * prong_half, 2.6 * span, (0.0, axle_y, 0.0)))
    body = body.union(_cyl_x(1.15 * prong_half, 1.5 * span, (0.0, axle_y, 0.0)))
    return body.union(_gear_screw(r))


_POST_SHAPES = {
    "plain_post": _post_form_plain_post_build,
    "high_ratio_post": _post_form_high_ratio_post_build,
    "locking_split_post": _post_form_locking_split_post_build,
    "classical_roller_post": _post_form_classical_roller_post_build,
}


def _build_post(
    model: ArticulatedObject,
    r: ResolvedConfig,
    mats: dict[str, str],
    mount,
    index: int,
    wheel_mesh,
    worm_joint_name: str,
):
    post = model.part(
        f"string_post_{index}",
        meta={"role": "string_post", "post_form": r.post_form, "unit": index},
    )
    post.visual(
        wheel_mesh,
        material=mats["gear"],
        name=f"post_form__{r.post_form}__wheel_{index}", material_class_id=("metal.stainless_matte" if r.palette_style in {"polished_nickel", "polished_gold", "black_chrome"} else "plastic.weathered_worn"),
    )
    post.visual(
        _mesh(
            _POST_SHAPES[r.post_form](r),
            f"post_form__{r.post_form}__post_{index}",
            tolerance=0.00022,
        ),
        material=mats["bright"],
        name=f"post_form__{r.post_form}__post_{index}", material_class_id=("metal.chrome_polished" if r.palette_style in {"polished_nickel", "black_chrome", "aged_ivory"} else "metal.precious_gold"),
    )

    mate = mate_axes(
        AxisInterface(
            name=f"mount.post_bearing_axis_{index}",
            point=(_unit_x(r, index), 0.0, 0.0),
            axis=(0.0, 1.0, 0.0),
            radial=(1.0, 0.0, 0.0),
            radius=r.post_bore_r_m,
        ),
        AxisInterface(
            name=f"string_post_{index}.shank",
            point=(0.0, 0.0, 0.0),
            axis=(0.0, 1.0, 0.0),
            radial=(1.0, 0.0, 0.0),
            radius=r.post_shank_r_m,
        ),
    )
    joint = model.articulation(
        f"mount_to_post_{index}",
        ArticulationType.CONTINUOUS,
        parent=mount,
        child=post,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(effort=2.5, velocity=1.0),
        mimic=Mimic(joint=worm_joint_name, multiplier=-1.0 / r.worm_ratio, offset=0.0),
        meta={"positive_motion": "the string post winds at the worm ratio"},
    )
    register_interface_mate(model, joint.name, mate)

    if r.post_form == "locking_split_post":
        _build_locking_screw(model, r, mats, post, index)
    return post, joint


def _build_locking_screw(
    model: ArticulatedObject, r: ResolvedConfig, mats: dict[str, str], post, index: int
):
    """The locking fork's fourth part: a screw on its own joint about the post axis.

    This is the only source in the pool that changes the joint count (locking L443-L453),
    and it is carried by its own category anchor rather than hidden.
    """
    screw = model.part(
        f"lock_screw_{index}",
        meta={"role": "lock_screw", "unit": index},
    )
    screw.visual(
        _mesh(
            _locking_screw_shape(r),
            f"post_form__locking_split_post__lock_screw_{index}",
            tolerance=0.00018,
        ),
        material=mats["dark"],
        name=f"post_form__locking_split_post__lock_screw_{index}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"polished_nickel", "black_chrome", "aged_ivory"} else "metal.brass_aged"),
    )
    seat_y = r.post_exit_y_m + r.post_free_len_m
    mate = mate_axes(
        AxisInterface(
            name=f"string_post_{index}.lock_screw_axis",
            point=(0.0, seat_y, 0.0),
            axis=(0.0, 1.0, 0.0),
            radial=(1.0, 0.0, 0.0),
            radius=_split_post_outer_r(r),
        ),
        AxisInterface(
            name=f"lock_screw_{index}.stem",
            point=(0.0, 0.0, 0.0),
            axis=(0.0, 1.0, 0.0),
            radial=(1.0, 0.0, 0.0),
            radius=0.40 * _split_post_outer_r(r),
        ),
    )
    joint = model.articulation(
        f"post_to_lock_screw_{index}",
        ArticulationType.CONTINUOUS,
        parent=post,
        child=screw,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(effort=0.4, velocity=4.0),
        meta={"positive_motion": "tightening the screw clamps the split post"},
    )
    register_interface_mate(model, joint.name, mate)
    return screw


# --------------------------------------------------------------------------- #
# Assembly
# --------------------------------------------------------------------------- #
def build_pictureX_0611_guitar_tuning_peg_mechanism(
    config: Config | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config or Config())
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={
            "category": "pictureX_0611_guitar_tuning_peg_mechanism",
            "slot_choices": slot_choices_for_config(r),
            "mechanism": (
                "one-start worm on +Z driving an involute wheel on +Y at -1/"
                f"{r.gear_teeth}, repeated {r.tuner_count}x along +X"
            ),
        },
    )
    mats = {key: key for key in r.palette}
    for key, rgba in r.palette.items():
        model.material(key, rgba=rgba)

    mount = _build_mount(model, r, mats)

    # The worm and the wheel are identical across units, so both solids are tessellated
    # once and the same mesh is shared by every rotor -- 001 L177-L202 reuses its bearing
    # mesh the same way.
    worm_mesh = _mesh(
        _worm_solid(r),
        f"worm_rotor__worm_screw_m{r.gear_module_m:.5f}",
        tolerance=WORM_MESH_TOL_MM,
        unit_scale=1.0 / MM,
        angular_tolerance=WORM_MESH_ANG,
    )
    wheel_mesh = _mesh(
        _wheel_solid(r),
        f"post_form__{r.post_form}__wheel_z{r.gear_teeth}",
        tolerance=WHEEL_MESH_TOL_MM,
        unit_scale=1.0 / MM,
        angular_tolerance=WHEEL_MESH_ANG,
    )

    for index in range(r.tuner_count):
        _, worm_joint = _build_worm_rotor(model, r, mats, mount, index, worm_mesh)
        _build_post(model, r, mats, mount, index, wheel_mesh, worm_joint.name)

    model.meta["risk_poses"] = tuple(
        {f"mount_to_worm_{i}": angle}
        for i in range(r.tuner_count)
        for angle in (math.pi / 2.0, math.pi)
    )
    return model


def build_seeded_pictureX_0611_guitar_tuning_peg_mechanism(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_pictureX_0611_guitar_tuning_peg_mechanism(config_from_seed(seed), assets=assets)


# --------------------------------------------------------------------------- #
# Authored tests
# --------------------------------------------------------------------------- #
def _parts_by_role(model: ArticulatedObject, role: str):
    return [part for part in model.parts if part.meta.get("role") == role]


def _meshes_materialized(model: ArticulatedObject) -> bool:
    """Preflight intercepts mesh materialization, so exact-geometry expectations have to
    be skipped there (AUTHORING.md section 5); the anchor check names are still emitted."""
    for part in model.parts:
        for visual in getattr(part, "visuals", []):
            filename = getattr(getattr(visual, "geometry", None), "filename", None)
            if filename and "__preflight_probe__" in str(filename):
                return False
    return True


def run_pictureX_0611_guitar_tuning_peg_mechanism_tests(
    model: ArticulatedObject, config: Config
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)
    joints = {joint.name: joint for joint in model.articulations}
    exact = _meshes_materialized(model)
    n = r.tuner_count

    mounts = _parts_by_role(model, "mount")
    rotors = _parts_by_role(model, "worm_rotor")
    posts = _parts_by_role(model, "string_post")
    screws = _parts_by_role(model, "lock_screw")
    worm_joints = [joints.get(f"mount_to_worm_{i}") for i in range(n)]
    post_joints = [joints.get(f"mount_to_post_{i}") for i in range(n)]
    roots = model.root_parts()

    ctx.check(
        "category_anchor: one mount carries every worm rotor and string post",
        len(mounts) == 1
        and len(rotors) == n
        and len(posts) == n
        and len(roots) == 1
        and roots[0].name == "mount"
        and all(joint is not None for joint in worm_joints + post_joints)
        and all(str(joint.parent) == "mount" for joint in worm_joints + post_joints)
        and all(
            joint.articulation_type == ArticulationType.CONTINUOUS
            for joint in worm_joints + post_joints
        )
        and all(tuple(round(v, 6) for v in joint.axis) == (0.0, 0.0, 1.0) for joint in worm_joints)
        and all(tuple(round(v, 6) for v in joint.axis) == (0.0, 1.0, 0.0) for joint in post_joints),
        details=(
            f"mounts={len(mounts)} rotors={len(rotors)} posts={len(posts)} "
            f"roots={[p.name for p in roots]} joints={sorted(joints)}"
        ),
    )

    teeth_lo, teeth_hi = POST_TEETH_RANGE[r.post_form]
    ctx.check(
        "category_anchor: each post is worm-driven at its own tooth ratio",
        all(joint is not None and joint.mimic is not None for joint in post_joints)
        and all(joint.mimic.joint == f"mount_to_worm_{i}" for i, joint in enumerate(post_joints))
        and all(abs(joint.mimic.multiplier + 1.0 / r.worm_ratio) < 1e-12 for joint in post_joints)
        and teeth_lo <= r.gear_teeth <= teeth_hi
        and abs(r.worm_ratio - r.gear_teeth) < 1e-9,
        details=(
            f"post_form={r.post_form} teeth={r.gear_teeth} band=[{teeth_lo},{teeth_hi}] "
            f"multiplier={-1.0 / r.worm_ratio}"
        ),
    )

    # The mesh derivation itself: tangent pitch circles, one centre distance apart.
    mesh_ok = (
        abs(r.center_distance_m - (r.gear_pitch_r_m + r.worm_pitch_r_m)) < 1e-12
        and abs(r.gear_pitch_r_m - r.gear_module_m * r.gear_teeth / 2.0) < 1e-12
        and abs(r.worm_pitch_r_m - r.gear_module_m / (2.0 * math.tan(r.worm_lead_angle_rad)))
        < 1e-12
        and r.worm_len_m > 0.0
        and r.gear_chamber_r_m > r.gear_tip_r_m
    )
    if exact:
        for i in range(n):
            ctx.expect_contact(
                rotors[i],
                posts[i],
                elem_a=f"worm_rotor__worm_{i}",
                elem_b=f"post_form__{r.post_form}__wheel_{i}",
                contact_tol=0.0006,
                name=f"worm and wheel {i} engage at the pitch line",
            )
    ctx.check(
        "category_anchor: the worm meshes the driven wheel at the pitch line",
        mesh_ok,
        details=(
            f"a={r.center_distance_m:.6f} gear_r0={r.gear_pitch_r_m:.6f} "
            f"worm_r0={r.worm_pitch_r_m:.6f} worm_len={r.worm_len_m:.6f} exact={exact}"
        ),
    )

    # The button rides above every mount silhouette because both the bearing span and the
    # seat height are derived from the gear housing the active post produced.
    clear_ok = (
        r.button_seat_z_m >= r.mount_top_z_m + 0.0025
        and r.worm_span_eff_m >= 2.0 * r.mount_body_r_m + 0.004
        and r.unit_pitch_m >= 2.0 * r.button_reach_m + 0.004
        and r.unit_pitch_m >= 2.0 * r.gear_tip_r_m + 0.004
    )
    if exact:
        for i in range(n):
            ctx.expect_gap(
                rotors[i],
                mounts[0],
                axis="z",
                positive_elem=f"button_form__{r.button_form}__button_{i}",
                negative_elem=f"mount_form__{r.mount_form}__shell",
                min_gap=0.0015,
                name=f"button {i} clears the mount above its bearing",
            )
    ctx.check(
        "category_anchor: the button turns clear of the mount",
        clear_ok,
        details=(
            f"seat_z={r.button_seat_z_m:.5f} mount_top={r.mount_top_z_m:.5f} "
            f"pitch={r.unit_pitch_m:.5f} button_reach={r.button_reach_m:.5f} "
            f"span_eff={r.worm_span_eff_m:.5f} body_r={r.mount_body_r_m:.5f}"
        ),
    )

    visual_names = {visual.name or "" for part in model.parts for visual in part.visuals}

    def count(fragment: str) -> int:
        return sum(1 for name in visual_names if fragment in name)

    mount_prefix = f"mount_form__{r.mount_form}"
    mount_identity = {
        "open_plate": count(f"{mount_prefix}__bearing_ring_") == 2 * n
        and count(f"{mount_prefix}__screw_head_") == n,
        "eared_plate": count(f"{mount_prefix}__rim_screw_") == 2 * n,
        "sealed_housing": count(f"{mount_prefix}__cover_screw_") == 2 * n
        and count(f"{mount_prefix}__cover_") - count(f"{mount_prefix}__cover_screw_") == n,
        "die_cast_housing": count(f"{mount_prefix}__back_screw_") == 2 * n,
        "side_mount_bracket": count(f"{mount_prefix}__leg_screw_") == 2 * n,
        "gearbox_bulb": count(f"{mount_prefix}__medallion_") == n
        and count(f"{mount_prefix}__bezel_") == n
        and count(f"{mount_prefix}__cover_screw_") == 2 * n,
    }[r.mount_form]
    ctx.check(
        "category_anchor: mount_form identity",
        mount_identity and count(f"{mount_prefix}__shell") == 1,
        details=f"mount_form={r.mount_form} n={n} visuals={sorted(visual_names)}",
    )

    ctx.check(
        "category_anchor: post_form identity",
        count(f"post_form__{r.post_form}__post_") == n
        and count(f"post_form__{r.post_form}__wheel_") == n
        and len(screws) == (n if r.post_form == "locking_split_post" else 0),
        details=f"post_form={r.post_form} n={n} lock_screws={len(screws)}",
    )

    ctx.check(
        "category_anchor: button_form identity",
        count(f"button_form__{r.button_form}__button_") == n
        and count("worm_rotor__worm_") == n
        and count("worm_rotor__thrust_collar_") == n,
        details=f"button_form={r.button_form} n={n}",
    )

    screw_joints = [joints.get(f"post_to_lock_screw_{i}") for i in range(n)]
    if r.post_form == "locking_split_post":
        locking_ok = (
            len(screws) == n
            and all(joint is not None for joint in screw_joints)
            and all(str(joint.parent) == f"string_post_{i}" for i, joint in enumerate(screw_joints))
            and all(
                joint.articulation_type == ArticulationType.CONTINUOUS for joint in screw_joints
            )
            and all(
                tuple(round(v, 6) for v in joint.axis) == (0.0, 1.0, 0.0) for joint in screw_joints
            )
        )
    else:
        locking_ok = not screws and not any(screw_joints)
    ctx.check(
        "category_anchor: the locking screw turns on the split post axis",
        locking_ok,
        details=f"post_form={r.post_form} screws={len(screws)} joints={screw_joints}",
    )

    # Motion evidence: turning the worm really winds the wheel about the post axis.
    if exact and posts:
        elem = f"post_form__{r.post_form}__wheel_0"
        rest = ctx.part_element_world_aabb(posts[0], elem=elem)
        with ctx.pose({worm_joints[0]: math.pi}):
            turned = ctx.part_element_world_aabb(posts[0], elem=elem)
            for i in range(n):
                ctx.expect_contact(
                    rotors[i],
                    posts[i],
                    elem_a=f"worm_rotor__worm_{i}",
                    elem_b=f"post_form__{r.post_form}__wheel_{i}",
                    contact_tol=0.0008,
                    name=f"worm {i} stays engaged after half a button turn",
                )
        ctx.check(
            "turning the worm keeps the wheel on its own bearing axis",
            rest is not None
            and turned is not None
            and abs(0.5 * (rest[0][1] + rest[1][1]) - 0.5 * (turned[0][1] + turned[1][1])) < 1e-6,
            details=f"rest={rest} turned={turned}",
        )

    ctx.check(
        "domain choices recorded on the model",
        model.meta.get("slot_choices") == slot_choices_for_config(r),
        details=str(model.meta.get("slot_choices")),
    )
    return ctx.report()


# --------------------------------------------------------------------------- #
# Authored high-risk corners
# --------------------------------------------------------------------------- #
TEMPLATE_CORNERS = (
    corner_case(
        "biggest_wheel_in_the_smallest_sealed_shell",
        {
            "mount_form": "sealed_housing",
            "post_form": "high_ratio_post",
            "button_form": "cloverleaf_button",
            "tuner_count": 3,
            "gear_module_m": 0.00125,
            "gear_teeth": 30,
            "worm_lead_angle_rad": 0.140,
            "mount_wall_m": 0.0017,
            "worm_span_m": 0.020,
            "post_reach_m": 0.042,
            "button_reach_m": 0.021,
            "button_thick_m": 0.0060,
        },
        reason="the largest driven wheel and the fattest low-lead worm inside the thinnest "
        "sealed shell on the shortest declared bearing span -- this is the case that proves "
        "worm_span_eff_m and gear_chamber_r_m really do grow with the wheel instead of the "
        "combination being excluded",
    ),
    corner_case(
        "smallest_everything_single_unit",
        {
            "mount_form": "side_mount_bracket",
            "post_form": "plain_post",
            "button_form": "paddle_button",
            "tuner_count": 1,
            "gear_module_m": 0.00070,
            "gear_teeth": 14,
            "worm_lead_angle_rad": 0.330,
            "mount_wall_m": 0.0017,
            "worm_span_m": 0.020,
            "post_reach_m": 0.022,
            "button_reach_m": 0.011,
            "button_thick_m": 0.0028,
        },
        reason="the finest module on the thinnest bracket -- the smallest worm core, the "
        "smallest journal and the tightest mesh the domain allows",
    ),
    corner_case(
        "locking_fork_at_full_count",
        {
            "mount_form": "die_cast_housing",
            "post_form": "locking_split_post",
            "button_form": "butterfly_button",
            "tuner_count": 3,
            "gear_module_m": 0.00120,
            "gear_teeth": 19,
            "worm_lead_angle_rad": 0.160,
            "mount_wall_m": 0.0034,
            "worm_span_m": 0.040,
            "post_reach_m": 0.042,
            "button_reach_m": 0.020,
            "button_thick_m": 0.0055,
        },
        reason="the only candidate that adds a part and a joint per unit, at N=3 -- ten "
        "parts and nine joints, with three independently posed screw axes",
    ),
    corner_case(
        "roller_fork_sweeping_beside_its_neighbour",
        {
            "mount_form": "open_plate",
            "post_form": "classical_roller_post",
            "button_form": "cloverleaf_button",
            "tuner_count": 3,
            "gear_module_m": 0.00125,
            "gear_teeth": 24,
            "worm_lead_angle_rad": 0.330,
            "mount_wall_m": 0.0020,
            "worm_span_m": 0.020,
            "post_reach_m": 0.022,
            "button_reach_m": 0.021,
            "button_thick_m": 0.0045,
        },
        reason="the transverse roller yoke is the widest rotating member off the post axis; "
        "at the shortest reach and the biggest button it has to sweep clear of both the "
        "open plate and the neighbouring unit",
    ),
    corner_case(
        "widest_strip_on_the_thinnest_bulb",
        {
            "mount_form": "gearbox_bulb",
            "post_form": "high_ratio_post",
            "button_form": "paddle_button",
            "tuner_count": 3,
            "gear_module_m": 0.00110,
            "gear_teeth": 30,
            "worm_lead_angle_rad": 0.330,
            "mount_wall_m": 0.0017,
            "worm_span_m": 0.040,
            "post_reach_m": 0.042,
            "button_reach_m": 0.011,
            "button_thick_m": 0.0028,
        },
        reason="the wheel term rather than the button term drives unit_pitch_m here, so the "
        "bulbs nearly touch while the buttons are the smallest the domain allows",
    ),
    corner_case(
        "eared_plate_longest_span_biggest_button",
        {
            "mount_form": "eared_plate",
            "post_form": "plain_post",
            "button_form": "cloverleaf_button",
            "tuner_count": 2,
            "gear_module_m": 0.00070,
            "gear_teeth": 19,
            "worm_lead_angle_rad": 0.140,
            "mount_wall_m": 0.0034,
            "worm_span_m": 0.040,
            "post_reach_m": 0.030,
            "button_reach_m": 0.021,
            "button_thick_m": 0.0060,
        },
        reason="the tallest bent ears on the thickest stamping with the widest disc button "
        "-- the case where the ear arms are longest relative to the plate silhouette",
    ),
)


__all__ = [
    "TEMPLATE_DOMAIN",
    "TEMPLATE_CORNERS",
    "Config",
    "ResolvedConfig",
    "config_from_seed",
    "resolve_config",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "build_pictureX_0611_guitar_tuning_peg_mechanism",
    "build_seeded_pictureX_0611_guitar_tuning_peg_mechanism",
    "run_pictureX_0611_guitar_tuning_peg_mechanism_tests",
]
