# SPDX-License-Identifier: Apache-2.0

"""Air vent / exhaust ventilation fan modular template.

NOTE on the slug name: "vent" here = **air vent / exhaust ventilation fan /
register** (a fixed housing with a continuously spinning axial impeller behind
an outlet grille, plus an optional backdraft shutter), NOT a soft grille
decoration and NOT a standalone louvered shutter (which has no impeller). The
invariant identity is: a fixed *housing* + a CONTINUOUS-spinning *impeller*
(hub press-fit on a fixed motor shaft) + an outlet *grille*, with an optional
REVOLUTE *backdraft shutter*.

Sourced from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/Other_Vent.md`` and the
``picture/Other/Vent`` 5-star sample pool (4 parents + 4 slot-fork variants),
all synced under ``data/records/``.

Structure (pattern = ``mixed``): a single root ``housing`` part (outer shell
mesh chosen by ``housing_form``) with three named module axes attaching as
parallel children / inline visuals, plus three multiplicity axes:

  * ``housing_form`` (4): round_through_wall / square_wall /
    inline_duct_cylinder / round_flange — the outer shell + bore + outlet
    opening + fixed motor shaft. Determines part tree and interface points.
  * ``grille_style`` (5): woven_square_mesh / ring_spoke_grille /
    wire_guard_cage / louvered_front_grille / perforated_plate — the outlet
    face that shrouds the impeller. Independent FIXED grille part or an inline
    housing visual (non-moving, Rule 1).
  * ``backdraft_shutter`` (4): none / single_gravity_flap (1 REVOLUTE +Y) /
    single_disc_flap_topring (1 REVOLUTE +Y) / multi_blade_louver_shutter
    (N independent REVOLUTE +Y) — the real joint-topology axis. All hinge about
    the transverse +Y pin so the flap/blades tilt open ALONG the duct (they do
    not orbit sideways out through the housing wall).
  * ``impeller_blade_count`` (Kb in {3,5,7,8}): FanRotorGeometry blade count;
    encoded as ``("impeller_blade_count", f"kb{Kb}")``. The rotor is a single
    CONTINUOUS child; no per-blade joint (Rule 1).
  * ``shutter_flap_count`` (Nf in [2,6]): only active when backdraft_shutter ==
    multi_blade_louver_shutter; N independent REVOLUTE louver blades. Encoded
    as ``("shutter_flap_count", f"nf{Nf}")``.
  * ``guard_ring_count`` (Rg in [2,6]): only active when grille_style is
    ring_spoke_grille / wire_guard_cage; N concentric rings (inline, no joint).
    Encoded as ``("guard_ring_count", f"rg{Rg}")``.

Unified duct axis = world +X (spec §; P1/P3 are already +X). Every housing
helper authors its axial mesh about local +Z and rotates it so local +Z -> the
world +X duct axis; the impeller spins about +X and grilles mount on the +X
outlet face.

All shaft/pin/press-fit interfaces are captured-shaft / captured-pin geometry,
so those joints omit ``MatingContract`` (grandfathered) and are guarded by the
flat articulation-origin baseline + element-scoped ``allow_overlap`` (mirroring
each source record's run_tests allow_overlap block).

Compatibility gating (resolve_config, spec §9):
  * multi_blade_louver_shutter needs a square/rectangular frame opening -> only
    compatible with square_wall / round_flange; on round_through_wall /
    inline_duct_cylinder it degrades to single_gravity_flap (which uses a
    top-edge hinge that fits a round sleeve).
  * Nf is only meaningful for multi_blade_louver_shutter; Rg only for
    ring_spoke_grille / wire_guard_cage. Otherwise the axis is omitted from
    the slot_choice tuple.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, replace
from typing import Literal

import cadquery as cq

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    FanRotorBlade,
    FanRotorGeometry,
    FanRotorHub,
    Inertial,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    TorusGeometry,
    mesh_from_cadquery,
    mesh_from_geometry,
)

__modular__ = True

HousingForm = Literal[
    "round_through_wall",
    "square_wall",
    "inline_duct_cylinder",
    "round_flange",
]
GrilleStyle = Literal[
    "woven_square_mesh",
    "ring_spoke_grille",
    "wire_guard_cage",
    "louvered_front_grille",
    "perforated_plate",
]
BackdraftShutter = Literal[
    "none",
    "single_gravity_flap",
    "single_disc_flap_topring",
    "multi_blade_louver_shutter",
]
PaletteStyle = Literal[
    "cream_plastic",
    "white_grey_plastic",
    "brushed_steel_industrial",
    "pale_grey_painted",
    "matte_black_register",
    "warm_anodized_bronze",
]

HOUSING_FORMS: tuple[HousingForm, ...] = (
    "round_through_wall",
    "square_wall",
    "inline_duct_cylinder",
    "round_flange",
)
GRILLE_STYLES: tuple[GrilleStyle, ...] = (
    "woven_square_mesh",
    "ring_spoke_grille",
    "wire_guard_cage",
    "louvered_front_grille",
    "perforated_plate",
)
BACKDRAFT_SHUTTERS: tuple[BackdraftShutter, ...] = (
    "none",
    "single_gravity_flap",
    "single_disc_flap_topring",
    "multi_blade_louver_shutter",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "cream_plastic",
    "white_grey_plastic",
    "brushed_steel_industrial",
    "pale_grey_painted",
    "matte_black_register",
    "warm_anodized_bronze",
)

# Multiplicity sampling domains (spec §8).
KB_CHOICES = (3, 5, 7, 8)
KB_WEIGHTS = (0.12, 0.34, 0.34, 0.20)  # mid-weighted
KB_MIN, KB_MAX = 3, 9
NF_CHOICES = (2, 3, 4, 5, 6)
NF_WEIGHTS = (0.32, 0.28, 0.20, 0.12, 0.08)  # small-weighted
NF_MIN, NF_MAX = 2, 6
RG_CHOICES = (2, 3, 4, 5, 6)
RG_WEIGHTS = (0.18, 0.26, 0.26, 0.18, 0.12)  # mid-weighted
RG_MIN, RG_MAX = 2, 6

# Guard-ring axis is only active for these grille styles.
RING_GRILLE_STYLES: tuple[GrilleStyle, ...] = ("ring_spoke_grille", "wire_guard_cage")
# Louver shutter needs a square/rectangular frame opening.
LOUVER_HOUSING_FORMS: tuple[HousingForm, ...] = ("square_wall", "round_flange")

# Material palettes: each key drives a distinct surface role.
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "cream_plastic": {
        "shell": (0.91, 0.89, 0.83, 1.0),
        "trim": (0.94, 0.92, 0.87, 1.0),
        "grille": (0.80, 0.81, 0.82, 1.0),
        "blade": (0.93, 0.93, 0.94, 1.0),
        "motor": (0.24, 0.24, 0.26, 1.0),
        "steel": (0.66, 0.66, 0.69, 1.0),
        "flap": (0.94, 0.92, 0.87, 1.0),
    },
    "white_grey_plastic": {
        "shell": (0.88, 0.88, 0.86, 1.0),
        "trim": (0.78, 0.79, 0.81, 1.0),
        "grille": (0.80, 0.81, 0.82, 1.0),
        "blade": (0.80, 0.81, 0.82, 1.0),
        "motor": (0.45, 0.45, 0.47, 1.0),
        "steel": (0.66, 0.67, 0.69, 1.0),
        "flap": (0.86, 0.86, 0.84, 1.0),
    },
    "brushed_steel_industrial": {
        "shell": (0.72, 0.73, 0.75, 1.0),
        "trim": (0.60, 0.61, 0.63, 1.0),
        "grille": (0.60, 0.61, 0.63, 1.0),
        "blade": (0.18, 0.19, 0.21, 1.0),
        "motor": (0.26, 0.27, 0.29, 1.0),
        "steel": (0.55, 0.56, 0.58, 1.0),
        "flap": (0.58, 0.60, 0.63, 1.0),
    },
    "pale_grey_painted": {
        "shell": (0.78, 0.79, 0.81, 1.0),
        "trim": (0.70, 0.71, 0.73, 1.0),
        "grille": (0.67, 0.68, 0.71, 1.0),
        "blade": (0.67, 0.68, 0.71, 1.0),
        "motor": (0.40, 0.41, 0.44, 1.0),
        "steel": (0.50, 0.51, 0.54, 1.0),
        "flap": (0.58, 0.60, 0.63, 1.0),
    },
    "matte_black_register": {
        "shell": (0.10, 0.10, 0.11, 1.0),
        "trim": (0.18, 0.18, 0.19, 1.0),
        "grille": (0.22, 0.22, 0.24, 1.0),
        "blade": (0.30, 0.30, 0.32, 1.0),
        "motor": (0.06, 0.06, 0.07, 1.0),
        "steel": (0.40, 0.40, 0.42, 1.0),
        "flap": (0.16, 0.16, 0.17, 1.0),
    },
    "warm_anodized_bronze": {
        "shell": (0.55, 0.43, 0.30, 1.0),
        "trim": (0.66, 0.52, 0.36, 1.0),
        "grille": (0.48, 0.38, 0.27, 1.0),
        "blade": (0.40, 0.32, 0.23, 1.0),
        "motor": (0.22, 0.18, 0.13, 1.0),
        "steel": (0.62, 0.50, 0.36, 1.0),
        "flap": (0.60, 0.47, 0.33, 1.0),
    },
}

# ---------------------------------------------------------------------------
# Base real-world dimensions (meters). Duct axis = world +X. The outlet face
# (room side) is at +X; the housing extends back toward -X.
#
# Nominal bore inner radius and outlet depth per housing form, derived from the
# parents (P1 sleeve r≈0.05; P2 opening r≈0.13; P3 tube r≈0.155; P4 collar
# r≈0.08). We use one consistent template-scale so the four forms read as a
# common small wall/duct vent family.
# ---------------------------------------------------------------------------
_BORE_R = 0.085  # nominal outlet bore inner radius (impeller swept radius zone)
_SHELL_WALL = 0.010
_OUTLET_X = 0.0  # outlet face plane (room side); shell extends to -X
_MOTOR_SHAFT_R = 0.005
_MOTOR_SHAFT_LEN = 0.040

_HUB_R = 0.026  # impeller hub radius
_ROTOR_T = 0.024  # impeller axial thickness
_HUB_BORE_D = 0.0095  # impeller hub bore (motor shaft press-fits in)
_TIP_CLEARANCE = 0.006  # bore-to-tip radial clearance

_DEPTH = 0.090  # nominal housing axial depth (back face at x = -_DEPTH)

# Grille recess: the grille plane sits this far behind the outlet face.
_GRILLE_RECESS = 0.012
_GRILLE_RING_W = 0.0034
_GRILLE_RING_R0 = 0.022
_GRILLE_RING_PITCH = 0.012

# Backdraft.
_FLAP_OPEN = 1.35  # gravity-flap open angle
_DISC_OPEN = 1.40  # top-ring disc-flap open angle
_LOUVER_OPEN = 1.22  # louver-blade open angle

# Rotate a local +Z-axis solid so its axis runs along world +X.
_AXIS_TO_X = (0.0, math.pi / 2.0, 0.0)


@dataclass(frozen=True)
class VentConfig:
    housing_form: HousingForm | None = None
    grille_style: GrilleStyle | None = None
    backdraft_shutter: BackdraftShutter | None = None
    impeller_blade_count: int | None = None
    shutter_flap_count: int | None = None
    guard_ring_count: int | None = None
    palette_style: PaletteStyle = "cream_plastic"
    housing_dia_scale: float = 1.0
    housing_depth_scale: float = 1.0
    grille_recess_scale: float = 1.0
    flap_open_angle_scale: float = 1.0
    louver_pitch_scale: float = 1.0
    guard_ring_pitch_scale: float = 1.0
    name: str = "vent"


@dataclass(frozen=True)
class ResolvedVentConfig:
    housing_form: HousingForm
    grille_style: GrilleStyle
    backdraft_shutter: BackdraftShutter
    impeller_blade_count: int
    shutter_flap_count: int  # resolved value (only used when louver active)
    guard_ring_count: int  # resolved value (only used when ring/guard active)
    palette_style: PaletteStyle
    # Concrete geometry (scaled).
    bore_r: float
    shell_wall: float
    depth: float
    hub_r: float
    rotor_t: float
    rotor_outer_r: float
    grille_recess: float
    grille_ring_w: float
    grille_ring_r0: float
    grille_ring_pitch: float
    flap_open: float
    disc_open: float
    louver_open: float
    louver_pitch_scale: float
    name: str

    @property
    def louver_active(self) -> bool:
        return self.backdraft_shutter == "multi_blade_louver_shutter"

    @property
    def ring_active(self) -> bool:
        return self.grille_style in RING_GRILLE_STYLES


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


def config_from_seed(seed: int) -> VentConfig:
    rng = random.Random(seed)
    return VentConfig(
        housing_form=rng.choice(HOUSING_FORMS),
        grille_style=rng.choice(GRILLE_STYLES),
        backdraft_shutter=rng.choice(BACKDRAFT_SHUTTERS),
        impeller_blade_count=rng.choices(KB_CHOICES, weights=KB_WEIGHTS, k=1)[0],
        shutter_flap_count=rng.choices(NF_CHOICES, weights=NF_WEIGHTS, k=1)[0],
        guard_ring_count=rng.choices(RG_CHOICES, weights=RG_WEIGHTS, k=1)[0],
        palette_style=rng.choice(PALETTE_STYLES),
        housing_dia_scale=round(rng.uniform(0.88, 1.15), 4),
        housing_depth_scale=round(rng.uniform(0.85, 1.15), 4),
        grille_recess_scale=round(rng.uniform(0.85, 1.10), 4),
        flap_open_angle_scale=round(rng.uniform(0.85, 1.10), 4),
        louver_pitch_scale=round(rng.uniform(0.90, 1.10), 4),
        guard_ring_pitch_scale=round(rng.uniform(0.90, 1.10), 4),
        name=f"seeded_vent_{seed}",
    )


def resolve_config(config: VentConfig | None = None) -> ResolvedVentConfig:
    cfg = config or VentConfig()
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)

    housing_form = _pick(cfg.housing_form, HOUSING_FORMS)
    grille_style = _pick(cfg.grille_style, GRILLE_STYLES)
    backdraft_shutter = _pick(cfg.backdraft_shutter, BACKDRAFT_SHUTTERS)

    # --- Compatibility gating (spec §9). ---
    # (1) multi_blade_louver_shutter needs a square/rectangular frame opening;
    #     on round forms it degrades to a single gravity flap (top-edge hinge).
    if (
        backdraft_shutter == "multi_blade_louver_shutter"
        and housing_form not in LOUVER_HOUSING_FORMS
    ):
        backdraft_shutter = "single_gravity_flap"

    kb = int(cfg.impeller_blade_count) if cfg.impeller_blade_count is not None else 7
    kb = int(_clamp(kb, KB_MIN, KB_MAX))
    nf = int(cfg.shutter_flap_count) if cfg.shutter_flap_count is not None else 5
    nf = int(_clamp(nf, NF_MIN, NF_MAX))
    rg = int(cfg.guard_ring_count) if cfg.guard_ring_count is not None else 4
    rg = int(_clamp(rg, RG_MIN, RG_MAX))

    dia_scale = _clamp(cfg.housing_dia_scale, 0.88, 1.15)
    depth_scale = _clamp(cfg.housing_depth_scale, 0.85, 1.15)
    recess_scale = _clamp(cfg.grille_recess_scale, 0.85, 1.10)
    angle_scale = _clamp(cfg.flap_open_angle_scale, 0.85, 1.10)
    louver_pitch_scale = _clamp(cfg.louver_pitch_scale, 0.90, 1.10)
    ring_pitch_scale = _clamp(cfg.guard_ring_pitch_scale, 0.90, 1.10)
    if backdraft_shutter == "multi_blade_louver_shutter":
        # N * slot_h must fit the frame opening. Values above 1.0 would overflow
        # the bore; values below 1.0 deliberately leave symmetric margin.
        louver_pitch_scale = min(louver_pitch_scale, 1.0)

    bore_r = _BORE_R * dia_scale
    depth = _DEPTH * depth_scale
    hub_r = _HUB_R * dia_scale
    # impeller_dia derives from housing_dia (spec equation): tip clears bore.
    rotor_outer_r = bore_r - _TIP_CLEARANCE
    rotor_t = _ROTOR_T

    grille_recess = _GRILLE_RECESS * recess_scale
    ring_pitch = _GRILLE_RING_PITCH * ring_pitch_scale

    # --- Concentric-ring clearance (spec §7): rings must fit in the opening.
    # RING_R0 + (Rg-1)*pitch + ring_w/2 <= bore_r - margin. Shrink pitch first.
    if grille_style in RING_GRILLE_STYLES:
        margin = 0.004
        max_outer = bore_r - margin
        for _ in range(40):
            outer = _GRILLE_RING_R0 + (rg - 1) * ring_pitch + _GRILLE_RING_W / 2.0
            if outer <= max_outer:
                break
            if ring_pitch > 0.006:
                ring_pitch = max(0.006, ring_pitch - 0.0008)
            else:
                rg = max(RG_MIN, rg - 1)
        # Hard clamp pitch if still too wide.
        outer = _GRILLE_RING_R0 + (rg - 1) * ring_pitch + _GRILLE_RING_W / 2.0
        if outer > max_outer and rg > 1:
            ring_pitch = max(0.004, (max_outer - _GRILLE_RING_R0 - _GRILLE_RING_W / 2.0) / (rg - 1))

    flap_open = _clamp(_FLAP_OPEN * angle_scale, 1.0, math.pi * 0.92)
    disc_open = _clamp(_DISC_OPEN * angle_scale, 1.0, math.pi * 0.92)
    louver_open = _clamp(_LOUVER_OPEN * angle_scale, 0.9, math.pi * 0.92)

    return ResolvedVentConfig(
        housing_form=housing_form,
        grille_style=grille_style,
        backdraft_shutter=backdraft_shutter,
        impeller_blade_count=kb,
        shutter_flap_count=nf,
        guard_ring_count=rg,
        palette_style=palette_style,
        bore_r=bore_r,
        shell_wall=_SHELL_WALL,
        depth=depth,
        hub_r=hub_r,
        rotor_t=rotor_t,
        rotor_outer_r=rotor_outer_r,
        grille_recess=grille_recess,
        grille_ring_w=_GRILLE_RING_W,
        grille_ring_r0=_GRILLE_RING_R0,
        grille_ring_pitch=ring_pitch,
        flap_open=flap_open,
        disc_open=disc_open,
        louver_open=louver_open,
        louver_pitch_scale=louver_pitch_scale,
        name=cfg.name or "vent",
    )


def with_overrides(config: VentConfig, **kwargs: object) -> VentConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: VentConfig | ResolvedVentConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedVentConfig) else resolve_config(config)
    choices: list[tuple[str, str]] = [
        ("housing_form", r.housing_form),
        ("grille_style", r.grille_style),
        ("backdraft_shutter", r.backdraft_shutter),
        ("impeller_blade_count", f"kb{r.impeller_blade_count}"),
    ]
    if r.louver_active:
        choices.append(("shutter_flap_count", f"nf{r.shutter_flap_count}"))
    if r.ring_active:
        choices.append(("guard_ring_count", f"rg{r.guard_ring_count}"))
    return tuple(choices)


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Impeller: an angled/swept FanRotor so its AABB genuinely changes when spun
# (the axisymmetric-rotor AABB-spin gotcha is avoided by blade_sweep_deg > 0,
# matching the real fan sources P1/P3). One CONTINUOUS child, no per-blade
# joint (Rule 1 multiplicity for impeller_blade_count).
# ---------------------------------------------------------------------------
def _rotor_geometry(r: ResolvedVentConfig) -> FanRotorGeometry:
    return FanRotorGeometry(
        r.rotor_outer_r,
        r.hub_r,
        r.impeller_blade_count,
        thickness=r.rotor_t,
        blade_pitch_deg=30.0,
        blade_sweep_deg=24.0,  # swept -> non-axisymmetric AABB under rotation
        blade=FanRotorBlade(shape="scimitar", camber=0.16, tip_clearance=0.004),
        hub=FanRotorHub(style="domed", bore_diameter=_HUB_BORE_D),
    )


# ---------------------------------------------------------------------------
# Housing forms (Slot A). Each emits the outer shell + a fixed motor shaft (for
# impeller press-fit) onto the root ``housing`` part, all about world +X. The
# shells are HOLLOW tubes / bored boxes so the impeller sits in a real bore void
# (no part overlap). Front trim/bezel is an inline visual (Rule 1, parent.visual
# — never a FIXED joint). Returns the shaft mid-x (impeller hub plane).
# ---------------------------------------------------------------------------
def _tube(outer_r: float, inner_r: float, length: float) -> cq.Workplane:
    """Hollow cylinder extruded along local +Z from z=0 to z=length."""
    return cq.Workplane("XY").circle(outer_r).circle(inner_r).extrude(length)


def _impeller_x(r: ResolvedVentConfig) -> float:
    """Impeller hub-plane x. The rotor front face sits a clearance behind the
    grille plane (-grille_recess) so even the deepest grille feature (tilted
    louver slats) clears the spinning rotor."""
    grille_clearance = 0.018
    return -r.grille_recess - grille_clearance - r.rotor_t / 2.0


def _emit_round_through_wall(housing, r: ResolvedVentConfig, mats, *, assets) -> float:
    """Short through-wall sleeve + donut bezel ring. Source: P1 (f4fe4250)."""
    outer_r = r.bore_r + r.shell_wall
    inner_r = r.bore_r
    length = r.depth
    # Hollow tube (real bore void), outlet face at x=0, extending back to -length.
    housing.visual(
        mesh_from_cadquery(_tube(outer_r, inner_r, length), "sleeve_tube", assets=assets),
        origin=Origin(xyz=(-length, 0.0, 0.0), rpy=_AXIS_TO_X),
        material=mats["shell"],
        name="sleeve_tube", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"cream_plastic", "white_grey_plastic"} else "metal.brushed_silver"),
    )
    # Front donut bezel (torus) on the outlet rim.
    housing.visual(
        mesh_from_geometry(
            TorusGeometry(outer_r * 0.92, r.shell_wall * 0.9, radial_segments=20, tubular_segments=48),
            "bezel_torus",
        ),
        origin=Origin(xyz=(0.002, 0.0, 0.0), rpy=_AXIS_TO_X),
        material=mats["trim"],
        name="bezel_ring", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"cream_plastic", "white_grey_plastic"} else "metal.brushed_silver"),
    )
    _emit_motor_shaft(housing, r, mats, shaft_back_x=-length + 0.018)
    return _impeller_x(r)


def _emit_square_wall(housing, r: ResolvedVentConfig, mats, *, assets) -> float:
    """Square wall-mounted box with a round opening. Source: P2 (4c3504f2)."""
    side = 2.0 * (r.bore_r + r.shell_wall * 2.4)
    length = r.depth
    # Rear box shell with a bored circular opening (real bore void). Box is
    # authored about local +Z (length axis) then rotated so length runs along X.
    shell = (
        cq.Workplane("XY")
        .box(side, side, length, centered=(True, True, False))
        .cut(cq.Workplane("XY").circle(r.bore_r).extrude(length))
    )
    housing.visual(
        mesh_from_cadquery(shell, "housing_shell", assets=assets),
        origin=Origin(xyz=(-length, 0.0, 0.0), rpy=_AXIS_TO_X),
        material=mats["shell"],
        name="housing_shell", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"cream_plastic", "white_grey_plastic"} else "metal.brushed_silver"),
    )
    # Raised square border rim on the outlet face: a picture FRAME with the
    # round outlet bore cut through it (was a solid full-face plate that occluded
    # the whole opening). The grille/impeller reads through the open bore.
    frame = (
        cq.Workplane("XY")
        .box(side, side, 0.006, centered=(True, True, False))
        .cut(cq.Workplane("XY").circle(r.bore_r).extrude(0.006))
    )
    housing.visual(
        mesh_from_cadquery(frame, "border_rim", assets=assets),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=_AXIS_TO_X),
        material=mats["trim"],
        name="border_rim", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"cream_plastic", "white_grey_plastic"} else "metal.brushed_silver"),
    )
    _emit_motor_shaft(housing, r, mats, shaft_back_x=-length + 0.018)
    return _impeller_x(r)


def _emit_inline_duct_cylinder(housing, r: ResolvedVentConfig, mats, *, assets) -> float:
    """Long open-ended duct tube (both ends open). Source: P3 (4010e666)."""
    outer_r = r.bore_r + r.shell_wall
    inner_r = r.bore_r
    length = r.depth * 1.7  # inline ducts are longer
    housing.visual(
        mesh_from_cadquery(_tube(outer_r, inner_r, length), "duct_shell", assets=assets),
        origin=Origin(xyz=(-length, 0.0, 0.0), rpy=_AXIS_TO_X),
        material=mats["shell"],
        name="duct_shell", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"cream_plastic", "white_grey_plastic"} else "metal.brushed_silver"),
    )
    # Rolled rim bulges at both ends.
    for tag, x in (("front", -0.002), ("rear", -length + 0.002)):
        housing.visual(
            mesh_from_geometry(
                TorusGeometry(outer_r, r.shell_wall * 0.7, radial_segments=16, tubular_segments=48),
                f"rim_{tag}",
            ),
            origin=Origin(xyz=(x, 0.0, 0.0), rpy=_AXIS_TO_X),
            material=mats["trim"],
            name=f"duct_rim_{tag}", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"cream_plastic", "white_grey_plastic"} else "metal.brushed_silver"),
        )
    _emit_motor_shaft(housing, r, mats, shaft_back_x=-r.depth * 0.85)
    return _impeller_x(r)


def _emit_round_flange(housing, r: ResolvedVentConfig, mats, *, assets) -> float:
    """Round flange + collar + drum + bolt circle. Source: P4 (6e21aa96)."""
    flange_r = r.bore_r + r.shell_wall * 4.0
    length = r.depth
    # Flange plate on the outlet face (annular: bored opening for the bore).
    housing.visual(
        mesh_from_cadquery(_tube(flange_r, r.bore_r, 0.006), "flange_plate", assets=assets),
        origin=Origin(xyz=(-0.006, 0.0, 0.0), rpy=_AXIS_TO_X),
        material=mats["shell"],
        name="flange_plate", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"cream_plastic", "white_grey_plastic"} else "metal.brushed_silver"),
    )
    # Raised collar ring around the opening.
    housing.visual(
        mesh_from_geometry(
            TorusGeometry(r.bore_r + r.shell_wall, r.shell_wall * 0.9, radial_segments=16, tubular_segments=48),
            "collar_ring",
        ),
        origin=Origin(xyz=(0.004, 0.0, 0.0), rpy=_AXIS_TO_X),
        material=mats["trim"],
        name="collar_ring", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"cream_plastic", "white_grey_plastic"} else "metal.brushed_silver"),
    )
    # Drum shell behind the flange (hollow).
    housing.visual(
        mesh_from_cadquery(_tube(r.bore_r + r.shell_wall, r.bore_r, length), "drum_shell", assets=assets),
        origin=Origin(xyz=(-length, 0.0, 0.0), rpy=_AXIS_TO_X),
        material=mats["shell"],
        name="drum_shell", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"cream_plastic", "white_grey_plastic"} else "metal.brushed_silver"),
    )
    # 8 hex bolts on the flange rim (inline visuals, half-embedded).
    bolt_r = flange_r - 0.010
    for i in range(8):
        ang = 2.0 * math.pi * i / 8.0
        housing.visual(
            Cylinder(radius=0.006, length=0.008),
            origin=Origin(
                xyz=(-0.001, bolt_r * math.cos(ang), bolt_r * math.sin(ang)),
                rpy=_AXIS_TO_X,
            ),
            material=mats["steel"],
            name=f"flange_bolt_{i}", material_class_id="metal.steel_bare",
        )
    _emit_motor_shaft(housing, r, mats, shaft_back_x=-length + 0.018)
    return _impeller_x(r)


def _emit_motor_shaft(housing, r: ResolvedVentConfig, mats, *, shaft_back_x: float) -> None:
    """Fixed motor pod + radial strut + shaft inside the bore. The impeller hub
    bore press-fits onto the shaft (captured shaft). Strut spans the bore so the
    motor structure is supported by the shell wall (no floating island)."""
    impeller_x = _impeller_x(r)
    # Radial strut spanning the bore (ends embed in the shell wall).
    housing.visual(
        Box((0.006, 2.0 * (r.bore_r + r.shell_wall * 0.4), 0.007)),
        origin=Origin(xyz=(shaft_back_x + 0.006, 0.0, 0.0)),
        material=mats["shell"],
        name="motor_strut", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"cream_plastic", "white_grey_plastic"} else "metal.brushed_silver"),
    )
    # Motor pod (dark can) on the strut, behind the impeller.
    pod_len = 0.018
    housing.visual(
        Cylinder(radius=0.014, length=pod_len),
        origin=Origin(xyz=(shaft_back_x + 0.006 + pod_len / 2.0, 0.0, 0.0), rpy=_AXIS_TO_X),
        material=mats["motor"],
        name="motor_pod", material_class_id="metal.paint_coated",
    )
    # Motor shaft: from the pod front forward to inside the impeller hub bore.
    shaft_front_x = impeller_x + 0.004  # tip hidden in the hub bore
    shaft_start_x = shaft_back_x + 0.006 + pod_len
    shaft_len = max(_MOTOR_SHAFT_LEN * 0.4, shaft_front_x - shaft_start_x)
    housing.visual(
        Cylinder(radius=_MOTOR_SHAFT_R, length=shaft_len),
        origin=Origin(xyz=(shaft_start_x + shaft_len / 2.0, 0.0, 0.0), rpy=_AXIS_TO_X),
        material=mats["steel"],
        name="motor_shaft", material_class_id="metal.steel_bare",
    )


_HOUSING_BUILDERS = {
    "round_through_wall": _emit_round_through_wall,
    "square_wall": _emit_square_wall,
    "inline_duct_cylinder": _emit_inline_duct_cylinder,
    "round_flange": _emit_round_flange,
}


# ---------------------------------------------------------------------------
# Impeller (always present). CONTINUOUS spin about the +X duct axis; hub bore
# press-fit onto the fixed motor shaft (captured shaft, allow_overlap).
# ---------------------------------------------------------------------------
def _emit_impeller(model, r: ResolvedVentConfig, housing, mats, *, impeller_x: float) -> None:
    impeller = model.part("impeller")
    impeller.visual(
        mesh_from_geometry(_rotor_geometry(r), "impeller_rotor"),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=_AXIS_TO_X),
        material=mats["blade"],
        name="impeller_rotor", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"cream_plastic", "white_grey_plastic"} else "metal.blackened_gunmetal"),
    )
    impeller.inertial = Inertial.from_geometry(
        Cylinder(radius=r.rotor_outer_r, length=r.rotor_t + 0.006),
        mass=0.16,
        origin=Origin(rpy=_AXIS_TO_X),
    )
    model.articulation(
        "impeller_spin",
        ArticulationType.CONTINUOUS,
        parent=housing,
        child=impeller,
        origin=Origin(xyz=(impeller_x, 0.0, 0.0)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=2.0, velocity=30.0),
    )


# ---------------------------------------------------------------------------
# Grille styles (Slot B). All recessed behind the outlet face, shrouding the
# impeller. Independent FIXED grille part (mesh/perforated) or inline housing
# visual (ring/louvered, Rule 1). Guard-ring multiplicity = Rg concentric rings.
# ---------------------------------------------------------------------------
def _grille_plane_x(r: ResolvedVentConfig) -> float:
    """World/child x of the grille plane (recessed behind the outlet face)."""
    return -r.grille_recess


def _grille_joint_origin(r: ResolvedVentConfig) -> Origin:
    """FIXED grille joint origin: on the shell BORE WALL rim at the grille plane,
    not on-axis. The bore center is a void (hollow tube), so an on-axis origin is
    far from real geometry; the bore-wall rim is where the grille rim physically
    press-fits, giving both joint→parent and joint→child distances < 0.015 tol
    (required by the baseline ``fail_if_articulation_origin_far_from_geometry``
    gate). Child grille visuals are authored in a local frame rebased by
    ``_grille_center_offset_z`` so their circular/radial geometry still centers
    on the duct axis instead of inheriting this rim offset."""
    return Origin(xyz=(-r.grille_recess, 0.0, _grille_anchor_z(r)))


def _grille_anchor_z(r: ResolvedVentConfig) -> float:
    return r.bore_r - 0.004


def _grille_center_offset_z(r: ResolvedVentConfig) -> float:
    return -_grille_anchor_z(r)


def _emit_woven_square_mesh(model, r: ResolvedVentConfig, housing, mats) -> None:
    """Independent FIXED mesh_grille: rim + crossing bars (~square mesh)."""
    grille = model.part("mesh_grille")
    rim_r = r.bore_r - 0.002
    bar_section = 0.0026
    bar_end_r = rim_r - 0.002
    center_z = _grille_center_offset_z(r)
    n = 7
    pitch = (2.0 * bar_end_r) / (n + 1)
    # Rim ring (a tube): outer cyl minus inner is approximated by a thin torus.
    grille.visual(
        mesh_from_geometry(
            TorusGeometry(rim_r, 0.004, radial_segments=14, tubular_segments=48),
            "grille_rim",
        ),
        origin=Origin(xyz=(0.0, 0.0, center_z), rpy=_AXIS_TO_X),
        material=mats["grille"],
        name="grille_rim", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"cream_plastic", "white_grey_plastic"} else "metal.brushed_silver"),
    )
    for k in range(-(n // 2), n // 2 + 1):
        offset = k * pitch
        half_len = math.sqrt(max(bar_end_r**2 - offset**2, 1e-6))
        idx = k + n // 2
        grille.visual(
            Box((bar_section, 2.0 * half_len, bar_section)),
            origin=Origin(xyz=(0.0, 0.0, center_z + offset)),
            material=mats["grille"],
            name=f"grille_bar_h_{idx}", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"cream_plastic", "white_grey_plastic"} else "metal.mesh_chainmail"),
        )
        grille.visual(
            Box((bar_section, bar_section, 2.0 * half_len)),
            origin=Origin(xyz=(0.0, offset, center_z)),
            material=mats["grille"],
            name=f"grille_bar_v_{idx}", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"cream_plastic", "white_grey_plastic"} else "metal.mesh_chainmail"),
        )
    model.articulation(
        "housing_to_grille",
        ArticulationType.FIXED,
        parent=housing,
        child=grille,
        origin=_grille_joint_origin(r),
    )


def _emit_ring_spoke_grille(model, r: ResolvedVentConfig, housing, mats) -> None:
    """Inline housing visuals: center cap + Rg concentric rings + 6 spokes."""
    plane_x = _grille_plane_x(r)
    rg = r.guard_ring_count
    # Center cap disc.
    housing.visual(
        Cylinder(radius=r.grille_ring_r0 * 0.75, length=0.004),
        origin=Origin(xyz=(plane_x + 0.002, 0.0, 0.0), rpy=_AXIS_TO_X),
        material=mats["grille"],
        name="ring_cap", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"cream_plastic", "white_grey_plastic"} else "metal.brushed_silver"),
    )
    for k in range(rg):
        r_mid = r.grille_ring_r0 + k * r.grille_ring_pitch
        housing.visual(
            mesh_from_geometry(
                TorusGeometry(r_mid, r.grille_ring_w / 2.0, radial_segments=10, tubular_segments=40),
                f"guard_ring_{k}",
            ),
            origin=Origin(xyz=(plane_x, 0.0, 0.0), rpy=_AXIS_TO_X),
            material=mats["grille"],
            name=f"guard_ring_{k}", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"cream_plastic", "white_grey_plastic"} else "metal.mesh_chainmail"),
        )
    # 6 radial spokes from the center cap out PAST the outer ring to the bore
    # wall (radius bore_r) so the inline ring grille embeds into the shell and
    # is not a floating island in the bore void.
    spoke_len = r.bore_r + 0.004  # reach into the shell wall
    for i in range(6):
        ang = 2.0 * math.pi * i / 6.0 + math.pi / 6.0
        cx = spoke_len / 2.0
        housing.visual(
            Box((0.004, spoke_len, 0.005)),
            origin=Origin(
                xyz=(plane_x, cx * math.cos(ang), cx * math.sin(ang)),
                rpy=(ang, 0.0, 0.0),
            ),
            material=mats["grille"],
            name=f"ring_spoke_{i}", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"cream_plastic", "white_grey_plastic"} else "metal.mesh_chainmail"),
        )


def _emit_wire_guard_cage(model, r: ResolvedVentConfig, housing, mats) -> None:
    """Independent FIXED front_guard: Rg concentric rings + 8 dished spokes +
    hub plate (industrial spider guard). Source: P3 wire guard (4010e666)."""
    guard = model.part("front_guard")
    rg = r.guard_ring_count
    center_z = _grille_center_offset_z(r)
    dish = 0.018  # axial dish depth (rings recede toward -X to the hub)
    outer = r.grille_ring_r0 + (rg - 1) * r.grille_ring_pitch
    for k in range(rg):
        r_mid = r.grille_ring_r0 + k * r.grille_ring_pitch
        # Outer rings sit at x=0; inner rings dish back toward -X.
        ring_x = -dish * (1.0 - r_mid / max(outer, 1e-6))
        guard.visual(
            mesh_from_geometry(
                TorusGeometry(r_mid, r.grille_ring_w / 2.0, radial_segments=10, tubular_segments=40),
                f"guard_ring_{k}",
            ),
            origin=Origin(xyz=(ring_x, 0.0, center_z), rpy=_AXIS_TO_X),
            material=mats["grille"],
            name=f"guard_ring_{k}", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"cream_plastic", "white_grey_plastic"} else "metal.mesh_chainmail"),
        )
    # 8 spokes from the hub plate out PAST the outer ring to the bore wall so the
    # guard spans the whole opening (not a small central spider) and embeds into
    # the shell for every ring count Rg (mirrors ring_spoke_grille reach).
    reach = r.bore_r + 0.004
    for i in range(8):
        ang = 2.0 * math.pi * i / 8.0
        cx = reach / 2.0
        guard.visual(
            Box((dish, reach, 0.004)),
            origin=Origin(
                xyz=(-dish / 2.0, cx * math.cos(ang), center_z + cx * math.sin(ang)),
                rpy=(ang, 0.0, 0.0),
            ),
            material=mats["grille"],
            name=f"guard_spoke_{i}", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"cream_plastic", "white_grey_plastic"} else "metal.mesh_chainmail"),
        )
    # Central hub plate at the dish bottom.
    guard.visual(
        Cylinder(radius=r.grille_ring_r0 * 0.7, length=0.004),
        origin=Origin(xyz=(-dish, 0.0, center_z), rpy=_AXIS_TO_X),
        material=mats["grille"],
        name="guard_hub_plate", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"cream_plastic", "white_grey_plastic"} else "metal.brushed_silver"),
    )
    model.articulation(
        "housing_to_guard",
        ArticulationType.FIXED,
        parent=housing,
        child=guard,
        origin=_grille_joint_origin(r),
    )


def _emit_louvered_front_grille(model, r: ResolvedVentConfig, housing, mats) -> None:
    """Independent FIXED louver_grille part: a frame ring + N fixed angled louver
    slats whose ends embed into the frame ring (self-connected, Rule 1 fixed,
    non-moving). Source: louvered_front_grille fork (2901e840)."""
    grille = model.part("louver_grille")
    frame_r = r.bore_r - 0.002
    center_z = _grille_center_offset_z(r)
    # Frame ring (torus) that every slat end embeds into.
    grille.visual(
        mesh_from_geometry(
            TorusGeometry(frame_r, 0.004, radial_segments=12, tubular_segments=48),
            "louver_frame",
        ),
        origin=Origin(xyz=(0.0, 0.0, center_z), rpy=_AXIS_TO_X),
        material=mats["trim"],
        name="louver_frame", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"cream_plastic", "white_grey_plastic"} else "metal.brushed_silver"),
    )
    n = 6
    span = 2.0 * frame_r
    slot_h = span / n
    tilt = math.radians(30.0)
    # Slats run full chord (ends reach past the frame radius to embed in the ring).
    for i in range(n):
        z = span / 2.0 - (i + 0.5) * slot_h
        half_w = math.sqrt(max(frame_r**2 - z**2, 1e-4)) + 0.004
        grille.visual(
            Box((0.008, 2.0 * half_w, slot_h * 0.9)),
            origin=Origin(xyz=(0.0, 0.0, center_z + z), rpy=(0.0, tilt, 0.0)),
            material=mats["grille"],
            name=f"louver_slat_{i}", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"cream_plastic", "white_grey_plastic"} else "metal.brushed_silver"),
        )
    model.articulation(
        "housing_to_louver_grille",
        ArticulationType.FIXED,
        parent=housing,
        child=grille,
        origin=_grille_joint_origin(r),
    )


def _emit_perforated_plate(model, r: ResolvedVentConfig, housing, mats) -> None:
    """Independent FIXED perforated_plate: rim + disc with a hole grid (modeled
    as a solid disc; the perforation reads from the surface). Source:
    perforated_plate fork (67dfdf18)."""
    plate = model.part("perforated_plate")
    rim_r = r.bore_r - 0.002
    center_z = _grille_center_offset_z(r)
    plate.visual(
        Cylinder(radius=rim_r, length=0.004),
        origin=Origin(xyz=(0.0, 0.0, center_z), rpy=_AXIS_TO_X),
        material=mats["grille"],
        name="perf_disc", material_class_id=("plastic.patterned_textured" if r.palette_style in {"cream_plastic", "white_grey_plastic"} else "metal.patterned_sheet_panel"),
    )
    plate.visual(
        mesh_from_geometry(
            TorusGeometry(rim_r, 0.003, radial_segments=12, tubular_segments=48),
            "plate_rim",
        ),
        origin=Origin(xyz=(0.0, 0.0, center_z), rpy=_AXIS_TO_X),
        material=mats["trim"],
        name="plate_rim", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"cream_plastic", "white_grey_plastic"} else "metal.brushed_silver"),
    )
    model.articulation(
        "housing_to_plate",
        ArticulationType.FIXED,
        parent=housing,
        child=plate,
        origin=_grille_joint_origin(r),
    )


_GRILLE_BUILDERS = {
    "woven_square_mesh": _emit_woven_square_mesh,
    "ring_spoke_grille": _emit_ring_spoke_grille,
    "wire_guard_cage": _emit_wire_guard_cage,
    "louvered_front_grille": _emit_louvered_front_grille,
    "perforated_plate": _emit_perforated_plate,
}


# ---------------------------------------------------------------------------
# Backdraft shutters (Slot C). The real joint-topology axis: 0 / 1 / N REVOLUTE.
# Hinge hardware lives on the housing; the flap/blade is a captured-pin child.
# All rest poses are q=0 (gravity-closed). MatingContract is grandfathered.
# ---------------------------------------------------------------------------
def _emit_single_gravity_flap(model, r: ResolvedVentConfig, housing, mats) -> None:
    """Single gravity disc flap on a top-edge hinge (1 REVOLUTE +Y). Source:
    single_gravity_flap fork (bf2f8952). Closed = disc hangs over the rear bore;
    open = swings outward (-X)."""
    back_x = -r.depth + 0.004
    hinge_z = r.bore_r + 0.008
    flap_r = r.bore_r - 0.002
    # Hinge lugs + pin on the housing top-back.
    for i, sy in enumerate((-1.0, 1.0)):
        housing.visual(
            Box((0.008, 0.008, 0.018)),
            origin=Origin(xyz=(back_x + 0.004, sy * 0.016, hinge_z - 0.006)),
            material=mats["shell"],
            name=f"hinge_lug_{i}", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"cream_plastic", "white_grey_plastic"} else "metal.brushed_silver"),
        )
    housing.visual(
        Cylinder(radius=0.0025, length=0.044),
        origin=Origin(xyz=(back_x, 0.0, hinge_z), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["steel"],
        name="hinge_pin", material_class_id="metal.steel_bare",
    )
    # Flap part: disc hanging from the hinge (top edge at the pivot).
    flap = model.part("backdraft_flap")
    flap.visual(
        Cylinder(radius=flap_r, length=0.003),
        origin=Origin(xyz=(0.0, 0.0, -flap_r), rpy=_AXIS_TO_X),
        material=mats["flap"],
        name="flap_disc", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"cream_plastic", "white_grey_plastic"} else "metal.brushed_silver"),
    )
    flap.visual(
        Cylinder(radius=0.0045, length=0.026),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["flap"],
        name="flap_knuckle", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"cream_plastic", "white_grey_plastic"} else "metal.brushed_silver"),
    )
    flap.inertial = Inertial.from_geometry(
        Cylinder(radius=flap_r, length=0.003),
        mass=0.05,
        origin=Origin(xyz=(0.0, 0.0, -flap_r), rpy=_AXIS_TO_X),
    )
    model.articulation(
        "flap_hinge",
        ArticulationType.REVOLUTE,
        parent=housing,
        child=flap,
        origin=Origin(xyz=(back_x, 0.0, hinge_z)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=1.0, velocity=3.0, lower=0.0, upper=r.flap_open),
    )


def _emit_single_disc_flap_topring(model, r: ResolvedVentConfig, housing, mats) -> None:
    """Single top-hinged disc flap inside the drum (1 REVOLUTE +Y). Source: P4
    (6e21aa96). Closed = vertical disc covering the rear bore; open = tilts back
    (-X) about the transverse +Y pin. Hinge at the top of the drum interior."""
    back_x = -r.depth * 0.7
    hinge_z = r.bore_r + 0.002
    flap_r = r.bore_r - 0.004
    # Hinge brackets + pin on the drum interior top.
    for i, sx in enumerate((-1.0, 1.0)):
        housing.visual(
            Box((0.007, 0.013, 0.007)),
            origin=Origin(xyz=(back_x, sx * 0.018, hinge_z - 0.004)),
            material=mats["shell"],
            name=f"hinge_bracket_{i}", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"cream_plastic", "white_grey_plastic"} else "metal.brushed_silver"),
        )
    housing.visual(
        Cylinder(radius=0.003, length=0.052),
        origin=Origin(xyz=(back_x, 0.0, hinge_z), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["steel"],
        name="hinge_pin", material_class_id="metal.steel_bare",
    )
    # Flap part: vertical disc hanging from the top hinge (covers the bore).
    flap = model.part("backdraft_flap")
    flap.visual(
        Cylinder(radius=flap_r, length=0.0025),
        origin=Origin(xyz=(0.0, 0.0, -flap_r), rpy=_AXIS_TO_X),
        material=mats["flap"],
        name="flap_disc", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"cream_plastic", "white_grey_plastic"} else "metal.brushed_silver"),
    )
    for i, sy in enumerate((-1.0, 1.0)):
        flap.visual(
            Cylinder(radius=0.0045, length=0.010),
            origin=Origin(xyz=(0.0, sy * 0.018, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["flap"],
            name=f"flap_knuckle_{i}", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"cream_plastic", "white_grey_plastic"} else "metal.brushed_silver"),
        )
        flap.visual(
            Box((0.010, 0.004, 0.012)),
            origin=Origin(xyz=(0.0, sy * 0.018, -0.010)),
            material=mats["flap"],
            name=f"flap_tab_{i}", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"cream_plastic", "white_grey_plastic"} else "metal.brushed_silver"),
        )
    flap.inertial = Inertial.from_geometry(
        Cylinder(radius=flap_r, length=0.0025),
        mass=0.05,
        origin=Origin(xyz=(0.0, 0.0, -flap_r), rpy=_AXIS_TO_X),
    )
    model.articulation(
        "flap_hinge",
        ArticulationType.REVOLUTE,
        parent=housing,
        child=flap,
        origin=Origin(xyz=(back_x, 0.0, hinge_z)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=2.0, velocity=4.0, lower=0.0, upper=r.disc_open),
    )


def _emit_multi_blade_louver_shutter(model, r: ResolvedVentConfig, housing, mats) -> None:
    """N independent louver blades, each its own REVOLUTE (+Y). Source:
    multi_blade_louver_shutter fork (d3db9306). Closed = all blades hang
    vertically across the round bore; open = same-direction tilt back about the
    transverse +Y pins (blades tilt ALONG the duct, not orbit sideways out the
    wall). Only on square/flange forms."""
    n = r.shutter_flap_count
    # Backdraft louver sits BEHIND the impeller (rear/exhaust side), clear of
    # the impeller back face and any rear-dished front grille.
    back_x = _impeller_x(r) - r.rotor_t / 2.0 - 0.014
    bore_r = r.bore_r
    side = 2.0 * (bore_r - 0.006)
    # louver_pitch_scale tunes the per-blade slot pitch (clamped so N blades
    # still fit within the frame opening).
    slot_h = (side / n) * r.louver_pitch_scale
    louver_span = n * slot_h
    top_z = louver_span / 2.0
    blade_t = 0.0022
    pivot_x = back_x

    def _chord(z: float) -> float:
        """Half-width of the round bore at height z."""
        return math.sqrt(max(bore_r * bore_r - z * z, 1e-4))

    # Inline louver frame on the housing: an OPEN torus ring around the round
    # bore (was a solid slab that sealed the intake). Embeds into the shell/drum
    # wall at the bore rim and leaves the opening clear for airflow.
    housing.visual(
        mesh_from_geometry(
            TorusGeometry(bore_r - 0.002, 0.005, radial_segments=12, tubular_segments=48),
            "louver_frame",
        ),
        origin=Origin(xyz=(back_x - 0.003, 0.0, 0.0), rpy=_AXIS_TO_X),
        material=mats["trim"],
        name="louver_frame", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"cream_plastic", "white_grey_plastic"} else "metal.brushed_silver"),
    )
    # Pivot rails between slots, each spanning the local bore chord so its ends
    # reach the bore wall / frame ring (no floating island).
    for i in range(1, n):
        z = top_z - i * slot_h
        housing.visual(
            Box((0.004, 2.0 * (_chord(z) + 0.002), 0.0028)),
            origin=Origin(xyz=(back_x, 0.0, z)),
            material=mats["trim"],
            name=f"louver_rail_{i}", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"cream_plastic", "white_grey_plastic"} else "metal.brushed_silver"),
        )
    # N independent blades, each pivoting about +Y at its slot top. Each blade's
    # width follows the round bore chord at its outermost edge so no corner pokes
    # out through the round shell (was a full-square blade wider than the bore).
    for i in range(n):
        pivot_z = top_z - i * slot_h
        # Blade box spans world z in [pivot_z - slot_h*0.98, pivot_z - slot_h*0.02];
        # size to the chord at whichever edge is farther from the axis center.
        z_edge = max(abs(pivot_z - slot_h * 0.98), abs(pivot_z - slot_h * 0.02))
        blade_w = 2.0 * _chord(z_edge)
        blade = model.part(f"shutter_blade_{i}")
        blade.visual(
            Box((blade_t, blade_w, slot_h * 0.96)),
            origin=Origin(xyz=(0.0, 0.0, -slot_h / 2.0)),
            material=mats["flap"],
            name=f"shutter_blade_{i}", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"cream_plastic", "white_grey_plastic"} else "metal.brushed_silver"),
        )
        # Knuckle straddling the pivot rail (captured pin geometry sense).
        blade.visual(
            Cylinder(radius=0.0035, length=blade_w * 0.9),
            origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["flap"],
            name=f"shutter_knuckle_{i}", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"cream_plastic", "white_grey_plastic"} else "metal.brushed_silver"),
        )
        blade.inertial = Inertial.from_geometry(
            Box((blade_t, blade_w, slot_h)),
            mass=0.012,
            origin=Origin(xyz=(0.0, 0.0, -slot_h / 2.0)),
        )
        model.articulation(
            f"shutter_blade_{i}_hinge",
            ArticulationType.REVOLUTE,
            parent=housing,
            child=blade,
            origin=Origin(xyz=(pivot_x, 0.0, pivot_z)),
            axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(effort=0.3, velocity=0.8, lower=0.0, upper=r.louver_open),
        )


_BACKDRAFT_BUILDERS = {
    "none": None,
    "single_gravity_flap": _emit_single_gravity_flap,
    "single_disc_flap_topring": _emit_single_disc_flap_topring,
    "multi_blade_louver_shutter": _emit_multi_blade_louver_shutter,
}


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def build_vent(
    config: VentConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        key: model.material(f"vent_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in PALETTES[r.palette_style].items()
    }

    housing = model.part("housing")
    housing.inertial = Inertial.from_geometry(
        Box((r.depth, 2.0 * (r.bore_r + r.shell_wall), 2.0 * (r.bore_r + r.shell_wall))),
        mass=0.9,
        origin=Origin(xyz=(-r.depth / 2.0, 0.0, 0.0)),
    )
    impeller_x = _HOUSING_BUILDERS[r.housing_form](housing, r, mats, assets=assets)

    # Impeller (always present) — CONTINUOUS spin about +X.
    _emit_impeller(model, r, housing, mats, impeller_x=impeller_x)

    # Grille (outlet face, shrouds impeller).
    _GRILLE_BUILDERS[r.grille_style](model, r, housing, mats)

    # Backdraft shutter (optional).
    builder = _BACKDRAFT_BUILDERS[r.backdraft_shutter]
    if builder is not None:
        builder(model, r, housing, mats)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_vent(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_vent(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def run_vent_tests(
    object_model: ArticulatedObject,
    config: VentConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    housing = object_model.get_part("housing")
    impeller = object_model.get_part("impeller")

    # ---- Captured-shaft (impeller) allowance: hub bore on the motor shaft. ----
    ctx.allow_overlap(
        impeller, housing,
        elem_a="impeller_rotor", elem_b="motor_shaft",
        reason="The rotor hub bore is press-fit onto the fixed motor shaft (captured axle).",
    )
    ctx.allow_overlap(
        impeller, housing,
        elem_a="impeller_rotor", elem_b="motor_pod",
        reason="The rotor hub seats just in front of the motor pod can.",
    )

    # ---- Grille allowances (rim/part press-fit into the bore). ----
    if r.grille_style == "woven_square_mesh":
        grille = object_model.get_part("mesh_grille")
        ctx.allow_overlap(
            grille, housing, reason="The mesh grille rim is press-fit into the outlet bore.",
        )
    elif r.grille_style == "wire_guard_cage":
        guard = object_model.get_part("front_guard")
        ctx.allow_overlap(
            guard, housing, reason="The wire guard outer ring clips into the outlet bore.",
        )
    elif r.grille_style == "perforated_plate":
        plate = object_model.get_part("perforated_plate")
        ctx.allow_overlap(
            plate, housing, reason="The perforated plate rim is press-fit into the outlet bore.",
        )
    elif r.grille_style == "louvered_front_grille":
        louver = object_model.get_part("louver_grille")
        ctx.allow_overlap(
            louver, housing, reason="The louver grille frame ring is press-fit into the outlet bore.",
        )

    # ---- Backdraft captured-pin allowances. ----
    if r.backdraft_shutter == "single_gravity_flap":
        flap = object_model.get_part("backdraft_flap")
        ctx.allow_overlap(
            flap, housing, elem_a="flap_knuckle", elem_b="hinge_pin",
            reason="The flap knuckle wraps around the housing hinge pin (captured pivot).",
        )
        ctx.allow_overlap(
            flap, housing, reason="The closed gravity flap seats over the rear bore opening.",
        )
    elif r.backdraft_shutter == "single_disc_flap_topring":
        flap = object_model.get_part("backdraft_flap")
        for i in range(2):
            ctx.allow_overlap(
                flap, housing, elem_a=f"flap_knuckle_{i}", elem_b="hinge_pin",
                reason="The flap hinge knuckle is captured around the drum hinge pin.",
            )
        ctx.allow_overlap(
            flap, housing, reason="The closed disc flap covers the rear bore inside the drum.",
        )
    elif r.backdraft_shutter == "multi_blade_louver_shutter":
        n = r.shutter_flap_count
        for i in range(n):
            blade = object_model.get_part(f"shutter_blade_{i}")
            ctx.allow_overlap(
                blade, housing, reason="Each louver blade pivots on its frame pivot rail and overlaps the inline frame.",
            )
            for j in range(i + 1, n):
                ctx.allow_overlap(
                    blade, object_model.get_part(f"shutter_blade_{j}"),
                    reason="Adjacent closed louver blades overlap slightly at the slot seam.",
                )

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_joint_mating_has_gap()

    # ---- Structure / identity. ----
    part_names = {p.name for p in object_model.parts}
    ctx.check("housing part present", "housing" in part_names, details=str(sorted(part_names)))
    ctx.check("impeller part present", "impeller" in part_names)

    # ---- Impeller: CONTINUOUS spin about the +X duct axis. ----
    spin = object_model.get_articulation("impeller_spin")
    ctx.check(
        "impeller spin is CONTINUOUS about +X duct axis",
        spin.articulation_type == ArticulationType.CONTINUOUS and abs(spin.axis[0]) > 0.99,
        details=f"type={spin.articulation_type} axis={tuple(spin.axis)}",
    )
    lim = spin.motion_limits
    ctx.check(
        "impeller spin is unlimited rotation",
        lim is not None and lim.lower is None and lim.upper is None,
        details=f"limits={lim}",
    )

    # The swept impeller's AABB genuinely changes under a quarter turn (the
    # axisymmetric-rotor spin-check gotcha is avoided by blade sweep).
    rest = ctx.part_world_aabb(impeller)
    with ctx.pose({spin: math.pi / 4.0}):
        posed = ctx.part_world_aabb(impeller)
    if rest is not None and posed is not None:
        rest_dy = float(rest[1][1] - rest[0][1])
        rest_dz = float(rest[1][2] - rest[0][2])
        posed_dy = float(posed[1][1] - posed[0][1])
        posed_dz = float(posed[1][2] - posed[0][2])
        ctx.check(
            "impeller blades sweep when spun (non-axisymmetric AABB)",
            abs(posed_dy - rest_dy) > 0.0015 or abs(posed_dz - rest_dz) > 0.0015,
            details=f"rest dy/dz={rest_dy:.4f}/{rest_dz:.4f} posed={posed_dy:.4f}/{posed_dz:.4f}",
        )

    # ---- Impeller blade count encoded. ----
    ctx.check(
        "impeller blade count in declared range",
        KB_MIN <= r.impeller_blade_count <= KB_MAX,
        details=f"kb={r.impeller_blade_count}",
    )

    # ---- Grille topology. ----
    if r.grille_style in (
        "woven_square_mesh",
        "wire_guard_cage",
        "perforated_plate",
        "louvered_front_grille",
    ):
        grille_part = {
            "woven_square_mesh": "mesh_grille",
            "wire_guard_cage": "front_guard",
            "perforated_plate": "perforated_plate",
            "louvered_front_grille": "louver_grille",
        }[r.grille_style]
        ctx.check(
            f"{r.grille_style} is an independent FIXED grille part",
            grille_part in part_names,
            details=str(sorted(part_names)),
        )
    if r.ring_active:
        ring_carrier = object_model.get_part("front_guard") if r.grille_style == "wire_guard_cage" else housing
        ring_visuals = [v.name for v in ring_carrier.visuals if v.name.startswith("guard_ring_")]
        ctx.check(
            "Rg concentric guard rings inlined (Rule 1)",
            len(ring_visuals) == r.guard_ring_count,
            details=f"rings={sorted(ring_visuals)} expected Rg={r.guard_ring_count}",
        )

    # ---- Backdraft topology + actuation. ----
    if r.backdraft_shutter == "none":
        ctx.check(
            "no backdraft part (empty mechanism)",
            "backdraft_flap" not in part_names
            and not any(p.startswith("shutter_blade_") for p in part_names),
            details=str(sorted(part_names)),
        )
    elif r.backdraft_shutter == "single_gravity_flap":
        j = object_model.get_articulation("flap_hinge")
        ctx.check(
            "gravity flap is REVOLUTE about +Y",
            j.articulation_type == ArticulationType.REVOLUTE and abs(j.axis[1]) > 0.99,
            details=f"type={j.articulation_type} axis={tuple(j.axis)}",
        )
        _check_flap_opens(ctx, object_model, "flap_hinge", "backdraft_flap", r.flap_open)
    elif r.backdraft_shutter == "single_disc_flap_topring":
        j = object_model.get_articulation("flap_hinge")
        ctx.check(
            "disc flap is REVOLUTE about +Y (transverse pin, tilts along duct)",
            j.articulation_type == ArticulationType.REVOLUTE and abs(j.axis[1]) > 0.99,
            details=f"type={j.articulation_type} axis={tuple(j.axis)}",
        )
        _check_flap_opens(ctx, object_model, "flap_hinge", "backdraft_flap", r.disc_open)
    else:  # multi_blade_louver_shutter
        n = r.shutter_flap_count
        blades = [p for p in part_names if p.startswith("shutter_blade_")]
        ctx.check(
            "N independent louver blades present",
            len(blades) == n,
            details=f"blades={sorted(blades)} expected N={n}",
        )
        # Each blade has its own REVOLUTE +Y hinge (transverse pin; tilts along
        # the duct rather than orbiting sideways out through the wall).
        ok_axis = True
        for i in range(n):
            ji = object_model.get_articulation(f"shutter_blade_{i}_hinge")
            if not (ji.articulation_type == ArticulationType.REVOLUTE and abs(ji.axis[1]) > 0.99):
                ok_axis = False
        ctx.check("each louver blade is its own REVOLUTE about +Y", ok_axis)
        _check_flap_opens(ctx, object_model, "shutter_blade_0_hinge", "shutter_blade_0", r.louver_open)

    # ---- slot_choices recorded with multiplicity encoded. ----
    ctx.check(
        "slot_choices recorded with multiplicity encoded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    return ctx.report()


def _check_flap_opens(ctx, object_model, joint_name: str, part_name: str, open_q: float) -> None:
    """A backdraft flap/blade actually TILTS OPEN ALONG THE DUCT when driven.

    The correct transverse (+Y) hinge tilts the flap/blade about a horizontal
    pin, so the part's X-extent (the duct axis) changes markedly as it opens. A
    regressed duct-axis (+/-X) hinge instead orbits the part sideways in the
    Y-Z plane, leaving the X-extent invariant -- so requiring an X-extent change
    both confirms real actuation AND rejects the swing-through axis bug."""
    j = object_model.get_articulation(joint_name)
    part = object_model.get_part(part_name)
    closed = ctx.part_world_aabb(part)
    with ctx.pose({j: open_q * 0.8}):
        opened = ctx.part_world_aabb(part)
    if closed is not None and opened is not None:
        x_moved = (
            abs(opened[0][0] - closed[0][0]) > 0.010
            or abs(opened[1][0] - closed[1][0]) > 0.010
        )
        ctx.check(
            f"{part_name} tilts open along the duct axis when its hinge is driven",
            x_moved,
            details=f"closed={closed} opened={opened}",
        )


__all__ = (
    "VentConfig",
    "ResolvedVentConfig",
    "build_vent",
    "build_seeded_vent",
    "config_from_seed",
    "resolve_config",
    "run_vent_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
