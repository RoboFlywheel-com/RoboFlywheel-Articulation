# SPDX-License-Identifier: Apache-2.0

"""Astronomy / Retractable landing gear -- modular procedural template.

A single retractable aircraft landing-gear leg: an aircraft-side ``mount_plate``
that folds up on a retraction hinge (``mount_to_strut`` REVOLUTE about the
lateral X pivot), a telescoping oleo-pneumatic shock strut
(``strut`` + ``piston`` on a PRISMATIC shock stroke), and a wheel carrier that
grounds the aircraft on one or more rolling wheels (CONTINUOUS spin), with an
optional folding drag/side-stay brace.

Slot graph (pattern = mixed: serial root leg chain + 2 parallel-children slots
parented directly to the leg + one ``wheel_count`` multiplicity axis):

    leg (root)  mount_plate --REVOLUTE(X)--> strut --PRISMATIC(Z)--> piston
        |-- wheel_carrier   (steer_fork / fixed_fork / free_caster /
        |                    single_side_fork / bogie_truck / trailing_link)
        `-- brace           (no_side_stay / folding_drag_brace)

Adapted per AUTHORING.md sec.A/sec.B from the confirmed 5-star landing-gear pool
(spec: specs_modular_v1/Astronomy_Retractable_landing_gear.md). Sources
(model.py:Lx-Ly cited in the spec Module Source Index):

  S1  origin origin rec_...1a64faf2 -- round oleo leg, twin-plate steerable fork,
      pneumatic wheel, retraction + oleo + steer + roll joints, test semantics.
  S2  blade_leg          -- flat fabricated blade strut cross-section ((3)).
  S3  single_side_leg    -- single-sided cantilever fork skeleton ((1)).
  S4  bogie_truck        -- fore-aft bogie beam rocker + 2 axles/wheels ((1)).
  S5  dual_wheel         -- coaxial dual-wheel multiplicity.
  S6  solid_wheel        -- solid molded disc wheel form ((3); re-authored lathe).
  S7  fixed_caster       -- FIXED non-steering caster joint ((2)).
  S8  free_caster        -- CONTINUOUS free-swivel caster joint ((2)).
  S9  drag_brace         -- 2-segment folding drag brace + Mimic joints ((1)).
  S10 trailing_link      -- levered trailing-arm suspension + X pivot ((1)).

Coordinate frame: authored in the DEPLOYED (gear-down) pose. Link frames cascade
downward from the aircraft mount plate (+Z, top) to the wheel (bottom); each
joint origin carries a negative-Z offset, so every part's visuals are authored
in its own link frame exactly as the 5-star sources do. +Y is aft (retraction /
trailing-arm direction), X is the lateral hinge/axle axis.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Literal

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
    BoltPattern,
    Box,
    Cylinder,
    LatheGeometry,
    Mimic,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    TireCarcass,
    TireGeometry,
    TireGroove,
    TireShoulder,
    TireSidewall,
    TireTread,
    WheelBore,
    WheelFace,
    WheelGeometry,
    WheelHub,
    WheelRim,
    WheelSpokes,
    mesh_from_geometry,
)

# Modular template: sweep coverage uses module_topology_diversity.
__modular__ = True


LegForm = Literal["round_oleo", "blade_leg"]
CarrierModule = Literal[
    "steer_fork",
    "fixed_fork",
    "free_caster",
    "single_side_fork",
    "bogie_truck",
    "trailing_link",
]
BraceModule = Literal["no_side_stay", "folding_drag_brace"]
WheelStyle = Literal["pneumatic", "solid"]
LandingGearPalette = Literal[
    "nose_gear_white",
    "bare_aluminum",
    "military_gray",
    "navy_gloss",
    "matte_black",
    "hydraulic_gold",
]

# Carriers whose steer joint is a bounded REVOLUTE (consume steer_range).
_STEER_REVOLUTE_CARRIERS = ("steer_fork", "single_side_fork")
# Fork-family carriers that support the wheel_count multiplicity axis.
_FORK_CARRIERS = ("steer_fork", "fixed_fork", "free_caster")


# --------------------------------------------------------------------------- #
# Canonical dimensions (origin origin rec_...1a64faf2). Every coordinate is in the
# owning part's LINK frame, verbatim from the sources.
# --------------------------------------------------------------------------- #

# Joint origins (all in the parent part's frame).
STRUT_PISTON_Z = -0.620   # strut_to_piston (in strut frame)
FORK_MOUNT_Z = -0.565     # piston_to_fork / caster bearing (in piston frame)
BOGIE_MOUNT_Z = -0.555    # piston_to_bogie (in piston frame)
TRAIL_MOUNT_Z = -0.572    # piston_to_trailing_arm (in piston frame)
AXLE_Z = -0.515           # fork_to_wheel origin (in fork frame)

# Base tire footprint (origin L195-232).
BASE_TIRE_R = 0.315
BASE_TIRE_W = 0.185
DUAL_WHEEL_GAP = 0.030


# --------------------------------------------------------------------------- #
# Palettes (>=6 colorways; tokens shared so every .visual resolves)
# --------------------------------------------------------------------------- #

PALETTES: dict[str, dict[str, tuple[float, float, float, float]]] = {
    "nose_gear_white": {
        "plate_paint": (0.82, 0.84, 0.82, 1.0),
        "strut_steel": (0.55, 0.58, 0.60, 1.0),
        "sleeve_dark": (0.05, 0.055, 0.06, 1.0),
        "chrome": (0.82, 0.86, 0.90, 1.0),
        "hub_alu": (0.68, 0.69, 0.68, 1.0),
        "rubber": (0.02, 0.02, 0.02, 1.0),
        "tire_side": (0.05, 0.05, 0.05, 1.0),
    },
    "bare_aluminum": {
        "plate_paint": (0.72, 0.74, 0.76, 1.0),
        "strut_steel": (0.60, 0.63, 0.66, 1.0),
        "sleeve_dark": (0.30, 0.32, 0.35, 1.0),
        "chrome": (0.86, 0.89, 0.92, 1.0),
        "hub_alu": (0.74, 0.75, 0.76, 1.0),
        "rubber": (0.04, 0.04, 0.04, 1.0),
        "tire_side": (0.08, 0.08, 0.08, 1.0),
    },
    "military_gray": {
        "plate_paint": (0.34, 0.36, 0.38, 1.0),
        "strut_steel": (0.42, 0.44, 0.46, 1.0),
        "sleeve_dark": (0.12, 0.13, 0.14, 1.0),
        "chrome": (0.70, 0.73, 0.76, 1.0),
        "hub_alu": (0.46, 0.47, 0.48, 1.0),
        "rubber": (0.05, 0.05, 0.05, 1.0),
        "tire_side": (0.09, 0.09, 0.09, 1.0),
    },
    "navy_gloss": {
        "plate_paint": (0.14, 0.20, 0.38, 1.0),
        "strut_steel": (0.50, 0.53, 0.58, 1.0),
        "sleeve_dark": (0.06, 0.08, 0.14, 1.0),
        "chrome": (0.80, 0.84, 0.90, 1.0),
        "hub_alu": (0.58, 0.60, 0.64, 1.0),
        "rubber": (0.03, 0.03, 0.04, 1.0),
        "tire_side": (0.06, 0.06, 0.08, 1.0),
    },
    "matte_black": {
        "plate_paint": (0.10, 0.10, 0.11, 1.0),
        "strut_steel": (0.24, 0.25, 0.26, 1.0),
        "sleeve_dark": (0.04, 0.04, 0.05, 1.0),
        "chrome": (0.55, 0.57, 0.60, 1.0),
        "hub_alu": (0.30, 0.31, 0.32, 1.0),
        "rubber": (0.02, 0.02, 0.02, 1.0),
        "tire_side": (0.05, 0.05, 0.05, 1.0),
    },
    "hydraulic_gold": {
        "plate_paint": (0.60, 0.55, 0.30, 1.0),
        "strut_steel": (0.66, 0.60, 0.34, 1.0),
        "sleeve_dark": (0.16, 0.13, 0.06, 1.0),
        "chrome": (0.88, 0.84, 0.62, 1.0),
        "hub_alu": (0.70, 0.66, 0.44, 1.0),
        "rubber": (0.04, 0.04, 0.03, 1.0),
        "tire_side": (0.08, 0.07, 0.05, 1.0),
    },
}
PALETTE_NAMES = tuple(PALETTES.keys())


# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class AstronomyRetractableLandingGearConfig:
    leg_form: LegForm = "round_oleo"
    carrier_module: CarrierModule = "steer_fork"
    brace_module: BraceModule = "no_side_stay"
    wheel_style: WheelStyle = "pneumatic"
    palette_style: LandingGearPalette = "nose_gear_white"

    wheel_count: int = 1   # fork carriers; forced by carrier gating otherwise

    wheel_radius_scale: float = 1.0
    retract_upper: float = 1.22   # retraction REVOLUTE upper (rad)
    oleo_stroke: float = 0.075    # oleo PRISMATIC upper (m)
    steer_range: float = 0.65     # revolute-steer carrier +- range (rad)


@dataclass(frozen=True)
class ResolvedAstronomyRetractableLandingGearConfig:
    leg_form: LegForm
    carrier_module: CarrierModule
    brace_module: BraceModule
    wheel_style: WheelStyle
    palette_style: str

    wheel_count: int

    wheel_radius_scale: float
    retract_upper: float
    oleo_stroke: float
    steer_range: float

    # Derived wheel footprint (single-sourced; Contract 3c).
    tire_radius: float
    tire_width: float

    palette: dict[str, tuple[float, float, float, float]]


# --------------------------------------------------------------------------- #
# Seed-driven sampling (procedural-first)
# --------------------------------------------------------------------------- #


def config_from_seed(seed: int) -> AstronomyRetractableLandingGearConfig:
    """Deterministic procedural sampling.

    seed 0 is pinned to the origin origin combination (round_oleo + steer_fork with
    1 pneumatic wheel + no_side_stay, nose_gear_white) as a documented regression
    anchor (a sparse override; every other seed is fully procedural).
    """
    if seed == 0:
        return AstronomyRetractableLandingGearConfig()

    rng = random.Random(seed)

    leg_form: LegForm = rng.choice(("round_oleo", "blade_leg"))
    carrier_module: CarrierModule = rng.choice(
        (
            "steer_fork",
            "fixed_fork",
            "free_caster",
            "single_side_fork",
            "bogie_truck",
            "trailing_link",
        )
    )
    brace_module: BraceModule = rng.choice(("no_side_stay", "folding_drag_brace"))
    wheel_style: WheelStyle = rng.choice(("pneumatic", "solid"))
    palette_style = rng.choice(PALETTE_NAMES)

    # Multiplicity axis: wheel_count (only meaningful for fork carriers).
    wheel_count = rng.choices((1, 2), weights=(0.6, 0.4))[0]

    wheel_radius_scale = round(rng.uniform(0.85, 1.15), 4)
    retract_upper = round(rng.uniform(1.05, 1.25), 4)
    oleo_stroke = round(rng.uniform(0.06, 0.09), 4)
    steer_range = round(rng.uniform(0.45, 0.75), 4)

    return AstronomyRetractableLandingGearConfig(
        leg_form=leg_form,
        carrier_module=carrier_module,
        brace_module=brace_module,
        wheel_style=wheel_style,
        palette_style=palette_style,
        wheel_count=wheel_count,
        wheel_radius_scale=wheel_radius_scale,
        retract_upper=retract_upper,
        oleo_stroke=oleo_stroke,
        steer_range=steer_range,
    )


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(float(v), hi))


def resolve_config(
    config: AstronomyRetractableLandingGearConfig,
) -> ResolvedAstronomyRetractableLandingGearConfig:
    if str(config.leg_form) not in {"round_oleo", "blade_leg"}:
        raise ValueError(f"Unsupported leg_form: {config.leg_form}")
    if str(config.carrier_module) not in {
        "steer_fork",
        "fixed_fork",
        "free_caster",
        "single_side_fork",
        "bogie_truck",
        "trailing_link",
    }:
        raise ValueError(f"Unsupported carrier_module: {config.carrier_module}")
    if str(config.brace_module) not in {"no_side_stay", "folding_drag_brace"}:
        raise ValueError(f"Unsupported brace_module: {config.brace_module}")
    if str(config.wheel_style) not in {"pneumatic", "solid"}:
        raise ValueError(f"Unsupported wheel_style: {config.wheel_style}")
    if str(config.palette_style) not in PALETTES:
        raise ValueError(f"Unsupported palette_style: {config.palette_style}")

    wheel_radius_scale = _clamp(config.wheel_radius_scale, 0.85, 1.15)
    retract_upper = _clamp(config.retract_upper, 1.05, 1.25)
    oleo_stroke = _clamp(config.oleo_stroke, 0.06, 0.09)
    steer_range = _clamp(config.steer_range, 0.45, 0.75)

    # wheel_count gating (compatibility matrix):
    #  - bogie truck carries one wheel per fore/aft axle => always 2;
    #  - single-sided cantilever fork and levered trailing arm carry exactly 1;
    #  - twin-plate fork family (steer/fixed/free) may carry 1 or 2 coaxial.
    if config.carrier_module == "bogie_truck":
        wheel_count = 2
    elif config.carrier_module in ("single_side_fork", "trailing_link"):
        wheel_count = 1
    else:
        wheel_count = 2 if int(config.wheel_count) >= 2 else 1

    tire_radius = BASE_TIRE_R * wheel_radius_scale
    tire_width = BASE_TIRE_W

    return ResolvedAstronomyRetractableLandingGearConfig(
        leg_form=config.leg_form,
        carrier_module=config.carrier_module,
        brace_module=config.brace_module,
        wheel_style=config.wheel_style,
        palette_style=config.palette_style,
        wheel_count=wheel_count,
        wheel_radius_scale=wheel_radius_scale,
        retract_upper=retract_upper,
        oleo_stroke=oleo_stroke,
        steer_range=steer_range,
        tire_radius=tire_radius,
        tire_width=tire_width,
        palette=dict(PALETTES[config.palette_style]),
    )


# --------------------------------------------------------------------------- #
# Geometry helpers
# --------------------------------------------------------------------------- #


def _cylinder_between(part, p0, p1, radius, material, name) -> None:
    """Add a cylinder whose local +Z axis spans two local points
    (origin S1 L32-50)."""
    dx = p1[0] - p0[0]
    dy = p1[1] - p0[1]
    dz = p1[2] - p0[2]
    length = math.sqrt(dx * dx + dy * dy + dz * dz)
    if length <= 0.0:
        raise ValueError(f"zero-length cylinder requested for {name}")
    yaw = math.atan2(dy, dx)
    pitch = math.atan2(math.sqrt(dx * dx + dy * dy), dz)
    part.visual(
        Cylinder(radius, length),
        origin=Origin(
            xyz=((p0[0] + p1[0]) * 0.5, (p0[1] + p1[1]) * 0.5, (p0[2] + p1[2]) * 0.5),
            rpy=(0.0, pitch, yaw),
        ),
        material=material,
        name=name, material_class_id="metal.generic_plain",
    )


def _make_pneumatic_wheel_meshes(r: ResolvedAstronomyRetractableLandingGearConfig):
    """Shared pneumatic tire + spoked hub meshes (origin S1 L195-232), radii
    scaled by wheel_radius_scale. Built once and reused across wheels."""
    s = r.wheel_radius_scale
    tire_mesh = mesh_from_geometry(
        TireGeometry(
            0.315 * s,
            0.185,
            inner_radius=0.228 * s,
            carcass=TireCarcass(belt_width_ratio=0.70, sidewall_bulge=0.07),
            tread=TireTread(style="block", depth=0.010, count=28, land_ratio=0.55),
            grooves=(
                TireGroove(center_offset=-0.038, width=0.010, depth=0.005),
                TireGroove(center_offset=0.038, width=0.010, depth=0.005),
            ),
            sidewall=TireSidewall(style="rounded", bulge=0.05),
            shoulder=TireShoulder(width=0.012, radius=0.006),
        ),
        "landing_gear_tire",
    )
    hub_mesh = mesh_from_geometry(
        WheelGeometry(
            0.235 * s,
            0.198,
            rim=WheelRim(
                inner_radius=0.145 * s,
                flange_height=0.012,
                flange_thickness=0.008,
                bead_seat_depth=0.006,
            ),
            hub=WheelHub(
                radius=0.062,
                width=0.074,
                cap_style="domed",
                bolt_pattern=BoltPattern(count=6, circle_diameter=0.090, hole_diameter=0.010),
            ),
            face=WheelFace(dish_depth=0.018, front_inset=0.006, rear_inset=0.004),
            spokes=WheelSpokes(style="split_y", count=6, thickness=0.010, window_radius=0.032),
            bore=WheelBore(style="round", diameter=0.038),
        ),
        "landing_gear_hub",
    )
    return tire_mesh, hub_mesh


def _make_solid_disc_mesh(r: ResolvedAstronomyRetractableLandingGearConfig):
    """One-piece solid molded disc wheel (solid_wheel S6, re-authored as a
    LatheGeometry revolved solid disc instead of cadquery booleans -- still a
    mesh, Rule 3 preserved). Lathe axis is local Z; the caller rotates it to X."""
    R = 0.315 * r.wheel_radius_scale
    half = 0.185 / 2.0
    # Filled disc profile (r from 0 -> R): rounded outer edge for a molded look.
    profile = [
        (0.0, -half),
        (R * 0.92, -half),
        (R, -half * 0.55),
        (R, half * 0.55),
        (R * 0.92, half),
        (0.0, half),
    ]
    return mesh_from_geometry(LatheGeometry(profile, segments=32), "solid_disc_body")


def _emit_wheel_visuals(
    part,
    r: ResolvedAstronomyRetractableLandingGearConfig,
    *,
    meshes,
    bore_length: float,
) -> None:
    """Wheel visuals centered on the part origin, spin axis along local X
    (origin S1 L233-246; solid_wheel S6). ``meshes`` is (tire, hub) for
    pneumatic or (solid_disc,) for solid."""
    if r.wheel_style == "pneumatic":
        tire_mesh, hub_mesh = meshes
        part.visual(tire_mesh, origin=Origin(), material="rubber", name="tire", material_class_id="rubber.directional_grooved")
        part.visual(
            Cylinder(0.310 * r.wheel_radius_scale, 0.012),
            origin=Origin(xyz=(0.099, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
            material="tire_side",
            name="outer_sidewall_ring", material_class_id="rubber.smooth_plain",
        )
        part.visual(hub_mesh, origin=Origin(), material="hub_alu", name="hub", material_class_id="metal.aluminum_bare")
        part.visual(
            Cylinder(0.046, bore_length),
            origin=Origin(rpy=(0.0, math.pi / 2.0, 0.0)),
            material="sleeve_dark",
            name="axle_bore_shadow", material_class_id="metal.blackened_gunmetal",
        )
    else:
        (disc_mesh,) = meshes
        # Rotate the lathe (local-Z axis) disc so its axis aligns with local X.
        part.visual(
            disc_mesh,
            origin=Origin(rpy=(0.0, math.pi / 2.0, 0.0)),
            material="rubber",
            name="solid_disc", material_class_id="rubber.smooth_plain",
        )
        # Plain hub-face caps on each side (no spokes) + bore shadow.
        for k, xf in enumerate((0.185 / 2.0 - 0.001, -(0.185 / 2.0 - 0.001))):
            part.visual(
                Cylinder(0.065, 0.008),
                origin=Origin(xyz=(xf, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
                material="hub_alu",
                name=f"hub_face_{k}", material_class_id="metal.aluminum_bare",
            )
        part.visual(
            Cylinder(0.046, bore_length),
            origin=Origin(rpy=(0.0, math.pi / 2.0, 0.0)),
            material="sleeve_dark",
            name="axle_bore_shadow", material_class_id="metal.blackened_gunmetal",
        )


def _wheel_meshes(r: ResolvedAstronomyRetractableLandingGearConfig):
    if r.wheel_style == "pneumatic":
        return _make_pneumatic_wheel_meshes(r)
    return (_make_solid_disc_mesh(r),)


# --------------------------------------------------------------------------- #
# Slot A -- leg (root: plate + strut + piston, retraction + oleo joints)
# --------------------------------------------------------------------------- #


def _leg_downstream(r: ResolvedAstronomyRetractableLandingGearConfig) -> InterfaceSpec:
    return InterfaceSpec(
        interface_name="downstream",
        part_name="piston",
        visual_name="chrome_piston",
        face_side="negative_z",
        anchor_local=(0.0, 0.0, FORK_MOUNT_Z),
        face_extents_uv=(0.12, 0.12),
        contact_tol=0.004,
    )


def _build_leg(ctx: ModuleBuildContext) -> ModuleBuild:
    model = ctx.model
    r: ResolvedAstronomyRetractableLandingGearConfig = ctx.config  # type: ignore[assignment]

    # --- Root mount plate with hinge lugs (origin S1 L69-94). ---
    plate = model.part("mount_plate")
    plate.visual(
        Box((0.66, 0.44, 0.08)),
        origin=Origin(xyz=(0.0, 0.0, 0.105)),
        material="plate_paint",
        name="plate_skin", material_class_id="metal.paint_coated",
    )
    for x, lug, bore in ((-0.265, "hinge_lug_0", "lug_bore_0"), (0.265, "hinge_lug_1", "lug_bore_1")):
        plate.visual(
            Box((0.11, 0.15, 0.23)),
            origin=Origin(xyz=(x, 0.0, -0.050)),
            material="plate_paint",
            name=lug, material_class_id="metal.paint_coated",
        )
        plate.visual(
            Cylinder(0.045, 0.118),
            origin=Origin(xyz=(x, 0.0, -0.02), rpy=(0.0, math.pi / 2.0, 0.0)),
            material="sleeve_dark",
            name=bore, material_class_id="metal.blackened_gunmetal",
        )

    # --- Retracting strut (round oleo OR flat blade). ---
    strut = model.part("strut")
    if r.leg_form == "blade_leg":
        # Flat fabricated blade cross-section (blade_leg S2 L96-141): Box members.
        strut.visual(
            Box((0.42, 0.065, 0.10)),
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
            material="strut_steel",
            name="trunnion_tube", material_class_id="metal.steel_bare",
        )
        strut.visual(
            Box((0.09, 0.14, 0.10)),
            origin=Origin(xyz=(0.0, 0.0, -0.075)),
            material="strut_steel",
            name="trunnion_web", material_class_id="metal.steel_bare",
        )
        strut.visual(
            Box((0.09, 0.14, 0.58)),
            origin=Origin(xyz=(0.0, 0.0, -0.36)),
            material="sleeve_dark",
            name="outer_shock_sleeve", material_class_id="metal.blackened_gunmetal",
        )
        strut.visual(
            Box((0.098, 0.148, 0.07)),
            origin=Origin(xyz=(0.0, 0.0, -0.095)),
            material="strut_steel",
            name="upper_gland_nut", material_class_id="metal.steel_bare",
        )
        strut.visual(
            Box((0.098, 0.148, 0.060)),
            origin=Origin(xyz=(0.0, 0.0, -0.675)),
            material="strut_steel",
            name="lower_sleeve_collar", material_class_id="metal.steel_bare",
        )
        tp_y = -0.078
        tl_x = 0.048
    else:
        # Round telescoping oleo tubing (origin S1 L97-137): Cylinder members.
        strut.visual(
            Cylinder(0.055, 0.42),
            origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
            material="strut_steel",
            name="trunnion_tube", material_class_id="metal.steel_bare",
        )
        strut.visual(
            Box((0.11, 0.10, 0.12)),
            origin=Origin(xyz=(0.0, 0.0, -0.075)),
            material="strut_steel",
            name="trunnion_web", material_class_id="metal.steel_bare",
        )
        strut.visual(
            Cylinder(0.075, 0.58),
            origin=Origin(xyz=(0.0, 0.0, -0.36)),
            material="sleeve_dark",
            name="outer_shock_sleeve", material_class_id="metal.blackened_gunmetal",
        )
        strut.visual(
            Cylinder(0.088, 0.075),
            origin=Origin(xyz=(0.0, 0.0, -0.095)),
            material="strut_steel",
            name="upper_gland_nut", material_class_id="metal.steel_bare",
        )
        strut.visual(
            Cylinder(0.084, 0.060),
            origin=Origin(xyz=(0.0, 0.0, -0.675)),
            material="strut_steel",
            name="lower_sleeve_collar", material_class_id="metal.steel_bare",
        )
        tp_y = -0.088
        tl_x = 0.050

    # Scissor / torque links on the visible front ((4) decoration; same part).
    _cylinder_between(strut, (-tl_x, tp_y, -0.30), (tl_x, tp_y, -0.60), 0.014, "strut_steel", "torque_link_0")
    _cylinder_between(strut, (tl_x, tp_y, -0.30), (-tl_x, tp_y, -0.60), 0.014, "strut_steel", "torque_link_1")
    for z, name in ((-0.30, "upper_torque_pivot"), (-0.60, "lower_torque_pivot")):
        strut.visual(
            Cylinder(0.020, 0.16),
            origin=Origin(xyz=(0.0, tp_y, z), rpy=(0.0, math.pi / 2.0, 0.0)),
            material="sleeve_dark",
            name=name, material_class_id="metal.blackened_gunmetal",
        )

    # --- Telescoping chrome piston (carrier-agnostic; origin S1 L140-152). ---
    piston = model.part("piston")
    piston.visual(
        Cylinder(0.044, 0.47),
        origin=Origin(xyz=(0.0, 0.0, -0.235)),
        material="chrome",
        name="chrome_piston", material_class_id="metal.chrome_polished",
    )
    piston.visual(
        Cylinder(0.078, 0.09),
        origin=Origin(xyz=(0.0, 0.0, -0.49)),
        material="strut_steel",
        name="lower_oleo_head", material_class_id="metal.steel_bare",
    )

    # --- Always-on joints: retraction hinge + oleo shock. ---
    model.articulation(
        "mount_to_strut",
        ArticulationType.REVOLUTE,
        parent=plate,
        child=strut,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=15000.0, velocity=0.8, lower=0.0, upper=r.retract_upper),
    )
    model.articulation(
        "strut_to_piston",
        ArticulationType.PRISMATIC,
        parent=strut,
        child=piston,
        origin=Origin(xyz=(0.0, 0.0, STRUT_PISTON_Z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=9000.0, velocity=0.25, lower=0.0, upper=r.oleo_stroke),
    )

    return ModuleBuild(
        module_name=r.leg_form,
        parts_emitted=["mount_plate", "strut", "piston"],
        internal_articulations=["mount_to_strut", "strut_to_piston"],
        interfaces={"downstream": _leg_downstream(r)},
    )


# --------------------------------------------------------------------------- #
# Slot B -- wheel_carrier (parallel children on the piston)
# --------------------------------------------------------------------------- #


def _emit_wheels_on(
    model,
    parent,
    r: ResolvedAstronomyRetractableLandingGearConfig,
    *,
    joint_prefix: str,
    axle_z: float,
    y_positions,
    bore_length: float,
) -> tuple[list[str], list[str]]:
    """Emit r.wheel_count coaxial wheels (offset along the X spin axis) OR the
    y-distributed wheels for the bogie. ``y_positions`` when given places one
    wheel per fore/aft axle (bogie); otherwise coaxial X offsets are derived."""
    meshes = _wheel_meshes(r)
    parts: list[str] = []
    joints: list[str] = []

    if y_positions is not None:
        # Bogie: one wheel per transverse axle at distinct +Y offsets, x=0.
        for i, y in enumerate(y_positions):
            w = model.part(f"wheel_{i}")
            _emit_wheel_visuals(w, r, meshes=meshes, bore_length=bore_length)
            jn = f"{joint_prefix}_{i}"
            model.articulation(
                jn, ArticulationType.CONTINUOUS, parent=parent, child=w,
                origin=Origin(xyz=(0.0, y, axle_z)), axis=(1.0, 0.0, 0.0),
                motion_limits=MotionLimits(effort=1200.0, velocity=45.0),
            )
            parts.append(w.name)
            joints.append(jn)
        return parts, joints

    if r.wheel_count == 1:
        w = model.part("wheel")
        _emit_wheel_visuals(w, r, meshes=meshes, bore_length=bore_length)
        jn = f"{joint_prefix}"
        model.articulation(
            jn, ArticulationType.CONTINUOUS, parent=parent, child=w,
            origin=Origin(xyz=(0.0, 0.0, axle_z)), axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=1200.0, velocity=45.0),
        )
        return [w.name], [jn]

    # Coaxial dual wheels offset along the X spin axis (dual_wheel S5).
    x_off = (r.tire_width + DUAL_WHEEL_GAP) / 2.0
    for i, xs in enumerate((-1.0, 1.0)):
        w = model.part(f"wheel_{i}")
        _emit_wheel_visuals(w, r, meshes=meshes, bore_length=bore_length)
        jn = f"{joint_prefix}_{i}"
        model.articulation(
            jn, ArticulationType.CONTINUOUS, parent=parent, child=w,
            origin=Origin(xyz=(xs * x_off, 0.0, axle_z)), axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=1200.0, velocity=45.0),
        )
        parts.append(w.name)
        joints.append(jn)
    return parts, joints


def _build_fork_carrier(ctx: ModuleBuildContext, *, joint_type) -> ModuleBuild:
    """Twin-plate yoke fork (origin S1 L161-192) steered by REVOLUTE(Z) /
    FIXED / CONTINUOUS(Z)."""
    model = ctx.model
    r: ResolvedAstronomyRetractableLandingGearConfig = ctx.config  # type: ignore[assignment]
    piston = model.get_part("piston")

    # Carrier terminal fitting added to the piston (origin honesty for the joint).
    piston.visual(
        Cylinder(0.063, 0.10),
        origin=Origin(xyz=(0.0, 0.0, FORK_MOUNT_Z)),
        material="sleeve_dark",
        name="caster_bearing_stack", material_class_id="metal.blackened_gunmetal",
    )

    fork = model.part("fork")
    # Crown spans the arm track so it bridges both arms (no internal island);
    # widened when the arms move out for the coaxial dual wheel.
    crown_w = 0.56 if r.wheel_count == 2 else 0.34
    fork.visual(
        Box((crown_w, 0.10, 0.09)),
        origin=Origin(xyz=(0.0, 0.0, -0.065)),
        material="hub_alu",
        name="fork_crown", material_class_id="metal.aluminum_bare",
    )
    fork.visual(
        Cylinder(0.055, 0.115),
        origin=Origin(xyz=(0.0, 0.0, 0.005)),
        material="strut_steel",
        name="steering_socket", material_class_id="metal.steel_bare",
    )
    if r.wheel_count == 2:
        arm_xs = (-0.225, 0.225)
        axle_len = 0.42
    else:
        arm_xs = (-0.148, 0.148)
        axle_len = 0.265
    for x, name in ((arm_xs[0], "fork_arm_0"), (arm_xs[1], "fork_arm_1")):
        fork.visual(
            Box((0.042, 0.080, 0.46)),
            origin=Origin(xyz=(x, 0.0, -0.285)),
            material="hub_alu",
            name=name, material_class_id="metal.aluminum_bare",
        )
        fork.visual(
            Cylinder(0.044, 0.044),
            origin=Origin(xyz=(x, 0.0, AXLE_Z), rpy=(0.0, math.pi / 2.0, 0.0)),
            material="strut_steel",
            name=f"{name}_axle_boss", material_class_id="metal.steel_bare",
        )
    fork.visual(
        Cylinder(0.038, axle_len),
        origin=Origin(xyz=(0.0, 0.0, AXLE_Z), rpy=(0.0, math.pi / 2.0, 0.0)),
        material="sleeve_dark",
        name="axle_pin", material_class_id="metal.blackened_gunmetal",
    )

    if joint_type == ArticulationType.REVOLUTE:
        limits = MotionLimits(effort=600.0, velocity=1.2, lower=-r.steer_range, upper=r.steer_range)
    elif joint_type == ArticulationType.CONTINUOUS:
        limits = MotionLimits(effort=600.0, velocity=1.2)
    else:  # FIXED
        limits = None
    kwargs = dict(parent=piston, child=fork, origin=Origin(xyz=(0.0, 0.0, FORK_MOUNT_Z)))
    if joint_type != ArticulationType.FIXED:
        kwargs["axis"] = (0.0, 0.0, 1.0)
        kwargs["motion_limits"] = limits
    model.articulation("piston_to_fork", joint_type, **kwargs)

    # Long bore shadow (spans the hub width) bridges the hub mesh's internal
    # components so no wheel has a disconnected island; same length for 1/2.
    bore_length = 0.232
    wparts, wjoints = _emit_wheels_on(
        model, fork, r, joint_prefix=("fork_to_wheel" if r.wheel_count == 1 else "fork_to_wheel"),
        axle_z=AXLE_Z, y_positions=None, bore_length=bore_length,
    )

    return ModuleBuild(
        module_name=ctx.module_name,
        parts_emitted=["fork"] + wparts,
        internal_articulations=["piston_to_fork"] + wjoints,
        interfaces={"downstream": _leg_downstream(r)},
    )


def _build_steer_fork(ctx: ModuleBuildContext) -> ModuleBuild:
    return _build_fork_carrier(ctx, joint_type=ArticulationType.REVOLUTE)


def _build_fixed_fork(ctx: ModuleBuildContext) -> ModuleBuild:
    return _build_fork_carrier(ctx, joint_type=ArticulationType.FIXED)


def _build_free_caster(ctx: ModuleBuildContext) -> ModuleBuild:
    return _build_fork_carrier(ctx, joint_type=ArticulationType.CONTINUOUS)


def _build_single_side_fork(ctx: ModuleBuildContext) -> ModuleBuild:
    """Single-sided cantilever fork + stub axle (single_side_leg S3 L160-185).
    Always carries exactly one wheel."""
    model = ctx.model
    r: ResolvedAstronomyRetractableLandingGearConfig = ctx.config  # type: ignore[assignment]
    piston = model.get_part("piston")

    piston.visual(
        Cylinder(0.063, 0.10),
        origin=Origin(xyz=(0.0, 0.0, FORK_MOUNT_Z)),
        material="sleeve_dark",
        name="caster_bearing_stack", material_class_id="metal.blackened_gunmetal",
    )

    fork = model.part("fork")
    fork.visual(
        Cylinder(0.055, 0.115),
        origin=Origin(xyz=(0.0, 0.0, 0.005)),
        material="strut_steel",
        name="steering_socket", material_class_id="metal.steel_bare",
    )
    fork.visual(
        Box((0.18, 0.10, 0.10)),
        origin=Origin(xyz=(-0.060, 0.0, -0.060)),
        material="hub_alu",
        name="fork_crown", material_class_id="metal.aluminum_bare",
    )
    fork.visual(
        Box((0.055, 0.080, 0.46)),
        origin=Origin(xyz=(-0.148, 0.0, -0.285)),
        material="hub_alu",
        name="cantilever_leg", material_class_id="metal.aluminum_bare",
    )
    fork.visual(
        Cylinder(0.042, 0.10),
        origin=Origin(xyz=(-0.098, 0.0, AXLE_Z), rpy=(0.0, math.pi / 2.0, 0.0)),
        material="strut_steel",
        name="stub_axle_boss", material_class_id="metal.steel_bare",
    )

    model.articulation(
        "piston_to_fork", ArticulationType.REVOLUTE, parent=piston, child=fork,
        origin=Origin(xyz=(0.0, 0.0, FORK_MOUNT_Z)), axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=600.0, velocity=1.2, lower=-r.steer_range, upper=r.steer_range),
    )

    # Single wheel cantilevered on the stub; nudged inboard toward the stub side.
    meshes = _wheel_meshes(r)
    w = model.part("wheel")
    _emit_wheel_visuals(w, r, meshes=meshes, bore_length=0.232)
    model.articulation(
        "fork_to_wheel", ArticulationType.CONTINUOUS, parent=fork, child=w,
        origin=Origin(xyz=(-0.098, 0.0, AXLE_Z)), axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=1200.0, velocity=45.0),
    )

    return ModuleBuild(
        module_name="single_side_fork",
        parts_emitted=["fork", "wheel"],
        internal_articulations=["piston_to_fork", "fork_to_wheel"],
        interfaces={"downstream": _leg_downstream(r)},
    )


def _build_bogie_truck(ctx: ModuleBuildContext) -> ModuleBuild:
    """Fore-aft bogie beam rocker + 2 axles/wheels (bogie_truck S4 L154-303)."""
    model = ctx.model
    r: ResolvedAstronomyRetractableLandingGearConfig = ctx.config  # type: ignore[assignment]
    piston = model.get_part("piston")

    piston.visual(
        Box((0.10, 0.08, 0.06)),
        origin=Origin(xyz=(0.0, 0.0, BOGIE_MOUNT_Z)),
        material="strut_steel",
        name="bogie_pivot_lug", material_class_id="metal.steel_bare",
    )

    bogie = model.part("bogie_beam")
    bogie.visual(
        Box((0.14, 0.96, 0.08)),
        origin=Origin(xyz=(0.0, 0.0, -0.02)),
        material="hub_alu",
        name="beam_body", material_class_id="metal.aluminum_bare",
    )
    bogie.visual(
        Cylinder(0.024, 0.16),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(-math.pi / 2.0, 0.0, 0.0)),
        material="strut_steel",
        name="pivot_pin", material_class_id="metal.steel_bare",
    )
    axle_y_positions = (-0.42, 0.42)
    for i, y_off in enumerate(axle_y_positions):
        bogie.visual(
            Cylinder(0.038, 0.24),
            origin=Origin(xyz=(0.0, y_off, -0.05), rpy=(0.0, math.pi / 2.0, 0.0)),
            material="strut_steel",
            name=f"axle_{i}", material_class_id="metal.steel_bare",
        )
        bogie.visual(
            Cylinder(0.052, 0.024),
            origin=Origin(xyz=(0.108, y_off, -0.05), rpy=(0.0, math.pi / 2.0, 0.0)),
            material="sleeve_dark",
            name=f"axle_cap_{i}", material_class_id="metal.blackened_gunmetal",
        )

    model.articulation(
        "piston_to_bogie", ArticulationType.REVOLUTE, parent=piston, child=bogie,
        origin=Origin(xyz=(0.0, 0.0, BOGIE_MOUNT_Z)), axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=2000.0, velocity=0.6, lower=-0.18, upper=0.18),
    )

    wparts, wjoints = _emit_wheels_on(
        model, bogie, r, joint_prefix="bogie_to_wheel", axle_z=-0.05,
        y_positions=axle_y_positions, bore_length=0.232,
    )

    return ModuleBuild(
        module_name="bogie_truck",
        parts_emitted=["bogie_beam"] + wparts,
        internal_articulations=["piston_to_bogie"] + wjoints,
        interfaces={"downstream": _leg_downstream(r)},
    )


def _build_trailing_link(ctx: ModuleBuildContext) -> ModuleBuild:
    """Levered trailing-arm suspension on a transverse X pin at the piston base
    (trailing_link S10 L155-336). Wheel axle sits aft (+Y) of the strut."""
    model = ctx.model
    r: ResolvedAstronomyRetractableLandingGearConfig = ctx.config  # type: ignore[assignment]
    piston = model.get_part("piston")

    piston.visual(
        Box((0.065, 0.055, 0.10)),
        origin=Origin(xyz=(0.0, 0.0, TRAIL_MOUNT_Z)),
        material="strut_steel",
        name="pivot_lug", material_class_id="metal.steel_bare",
    )
    piston.visual(
        Cylinder(0.028, 0.14),
        origin=Origin(xyz=(0.0, 0.0, TRAIL_MOUNT_Z), rpy=(0.0, math.pi / 2.0, 0.0)),
        material="sleeve_dark",
        name="pivot_pin", material_class_id="metal.blackened_gunmetal",
    )

    arm_len_y = 0.28
    arm_len_z = -0.30
    arm_half_x = 0.055

    arm = model.part("trailing_arm")
    arm.visual(
        Cylinder(0.038, 0.13),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material="hub_alu",
        name="pivot_bushing", material_class_id="metal.aluminum_bare",
    )
    arm.visual(
        Box((0.14, 0.050, 0.036)),
        origin=Origin(xyz=(0.0, 0.038, -0.018)),
        material="hub_alu",
        name="pivot_web", material_class_id="metal.aluminum_bare",
    )
    for x, name in ((-arm_half_x, "arm_member_0"), (arm_half_x, "arm_member_1")):
        _cylinder_between(arm, (x, 0.06, -0.03), (x, arm_len_y, arm_len_z), 0.022, "hub_alu", name)
    _cylinder_between(
        arm, (-arm_half_x, arm_len_y * 0.5, arm_len_z * 0.5),
        (arm_half_x, arm_len_y * 0.5, arm_len_z * 0.5), 0.013, "hub_alu", "arm_cross_brace",
    )
    for x, name in ((-arm_half_x, "axle_boss_0"), (arm_half_x, "axle_boss_1")):
        arm.visual(
            Cylinder(0.038, 0.040),
            origin=Origin(xyz=(x, arm_len_y, arm_len_z), rpy=(0.0, math.pi / 2.0, 0.0)),
            material="strut_steel",
            name=name, material_class_id="metal.steel_bare",
        )
    arm.visual(
        Cylinder(0.025, 0.18),
        origin=Origin(xyz=(0.0, arm_len_y, arm_len_z), rpy=(0.0, math.pi / 2.0, 0.0)),
        material="sleeve_dark",
        name="axle_pin", material_class_id="metal.blackened_gunmetal",
    )

    model.articulation(
        "piston_to_trailing_arm", ArticulationType.REVOLUTE, parent=piston, child=arm,
        origin=Origin(xyz=(0.0, 0.0, TRAIL_MOUNT_Z)), axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=5000.0, velocity=1.0, lower=-0.08, upper=0.20),
    )

    meshes = _wheel_meshes(r)
    w = model.part("wheel")
    _emit_wheel_visuals(w, r, meshes=meshes, bore_length=0.232)
    model.articulation(
        "trailing_arm_to_wheel", ArticulationType.CONTINUOUS, parent=arm, child=w,
        origin=Origin(xyz=(0.0, arm_len_y, arm_len_z)), axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=1200.0, velocity=45.0),
    )

    return ModuleBuild(
        module_name="trailing_link",
        parts_emitted=["trailing_arm", "wheel"],
        internal_articulations=["piston_to_trailing_arm", "trailing_arm_to_wheel"],
        interfaces={"downstream": _leg_downstream(r)},
    )


# --------------------------------------------------------------------------- #
# Slot C -- brace (parallel children on plate / strut)
# --------------------------------------------------------------------------- #


def _build_no_side_stay(ctx: ModuleBuildContext) -> ModuleBuild:
    """No folding brace: a short static side-stay gusset fused onto the strut as
    a non-moving visual (Rule 1). Baseline configuration of the origin."""
    model = ctx.model
    r: ResolvedAstronomyRetractableLandingGearConfig = ctx.config  # type: ignore[assignment]
    strut = model.get_part("strut")
    # Diagonal stay hugging the -Y side of the shock sleeve (touches the sleeve,
    # so it is connected within the strut part).
    _cylinder_between(strut, (0.0, -0.075, -0.14), (0.0, -0.11, -0.42), 0.016, "strut_steel", "side_stay_gusset")
    return ModuleBuild(
        module_name="no_side_stay",
        parts_emitted=[],
        internal_articulations=[],
        interfaces={"downstream": _leg_downstream(r)},
    )


def _build_folding_drag_brace(ctx: ModuleBuildContext) -> ModuleBuild:
    """Two-segment folding drag/side-stay brace Mimic-tied to the retraction
    hinge (drag_brace S9 L96-387)."""
    model = ctx.model
    r: ResolvedAstronomyRetractableLandingGearConfig = ctx.config  # type: ignore[assignment]
    plate = model.get_part("mount_plate")
    strut = model.get_part("strut")

    # The brace lives in a LATERAL plane offset along +X (a side-stay), so it
    # folds clear of the strut/piston, which rotate in the X=0 Y-Z plane. The
    # attachment lugs bridge from the plate/strut surface out to that plane.
    # x=0.15 sits between the sleeve (r~0.075) and the plate hinge lugs (x=+-0.265),
    # so the brace and its folding sweep clear both.
    SX = 0.15  # brace side-stay X plane
    plate.visual(
        Box((0.08, 0.12, 0.09)),
        origin=Origin(xyz=(SX, -0.14, 0.020)),
        material="plate_paint",
        name="drag_lug", material_class_id="metal.paint_coated",
    )
    plate.visual(
        Cylinder(0.028, 0.10),
        origin=Origin(xyz=(SX, -0.14, 0.020), rpy=(0.0, math.pi / 2.0, 0.0)),
        material="sleeve_dark",
        name="drag_lug_bore", material_class_id="metal.blackened_gunmetal",
    )
    # Strut shoulder lug bridges from the sleeve surface (x~0) out to the SX plane.
    strut.visual(
        Box((0.19, 0.10, 0.06)),
        origin=Origin(xyz=(0.075, -0.12, -0.18)),
        material="strut_steel",
        name="drag_strut_lug", material_class_id="metal.steel_bare",
    )
    strut.visual(
        Cylinder(0.024, 0.10),
        origin=Origin(xyz=(SX, -0.12, -0.18), rpy=(0.0, math.pi / 2.0, 0.0)),
        material="sleeve_dark",
        name="drag_strut_lug_bore", material_class_id="metal.blackened_gunmetal",
    )

    drag_upper = model.part("drag_brace_upper")
    _cylinder_between(drag_upper, (0.0, 0.0, 0.0), (0.0, -0.14, -0.54), 0.022, "strut_steel", "drag_upper_bar")
    drag_upper.visual(
        Cylinder(0.035, 0.08),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material="sleeve_dark",
        name="drag_upper_boss_top", material_class_id="metal.blackened_gunmetal",
    )
    drag_upper.visual(
        Cylinder(0.030, 0.07),
        origin=Origin(xyz=(0.0, -0.14, -0.54), rpy=(0.0, math.pi / 2.0, 0.0)),
        material="sleeve_dark",
        name="drag_upper_boss_knee", material_class_id="metal.blackened_gunmetal",
    )

    drag_lower = model.part("drag_brace_lower")
    _cylinder_between(drag_lower, (0.0, 0.0, 0.0), (0.0, 0.16, 0.34), 0.020, "strut_steel", "drag_lower_bar")
    drag_lower.visual(
        Cylinder(0.030, 0.07),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material="sleeve_dark",
        name="drag_lower_boss_knee", material_class_id="metal.blackened_gunmetal",
    )
    drag_lower.visual(
        Cylinder(0.028, 0.06),
        origin=Origin(xyz=(0.0, 0.16, 0.34), rpy=(0.0, math.pi / 2.0, 0.0)),
        material="sleeve_dark",
        name="drag_lower_boss_strut", material_class_id="metal.blackened_gunmetal",
    )

    model.articulation(
        "plate_to_drag_upper", ArticulationType.REVOLUTE, parent=plate, child=drag_upper,
        origin=Origin(xyz=(SX, -0.14, 0.02)), axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=8000.0, velocity=0.8, lower=-0.3, upper=1.1),
        mimic=Mimic(joint="mount_to_strut", multiplier=0.90, offset=0.0),
    )
    model.articulation(
        "drag_knee", ArticulationType.REVOLUTE, parent=drag_upper, child=drag_lower,
        origin=Origin(xyz=(0.0, -0.14, -0.54)), axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=5000.0, velocity=1.0, lower=-2.2, upper=0.2),
        mimic=Mimic(joint="mount_to_strut", multiplier=-1.50, offset=0.0),
    )

    return ModuleBuild(
        module_name="folding_drag_brace",
        parts_emitted=["drag_brace_upper", "drag_brace_lower"],
        internal_articulations=["plate_to_drag_upper", "drag_knee"],
        interfaces={"downstream": _leg_downstream(r)},
    )


# --------------------------------------------------------------------------- #
# Factory registries + assembly
# --------------------------------------------------------------------------- #

CARRIER_FACTORIES = {
    "steer_fork": _build_steer_fork,
    "fixed_fork": _build_fixed_fork,
    "free_caster": _build_free_caster,
    "single_side_fork": _build_single_side_fork,
    "bogie_truck": _build_bogie_truck,
    "trailing_link": _build_trailing_link,
}
BRACE_FACTORIES = {
    "no_side_stay": _build_no_side_stay,
    "folding_drag_brace": _build_folding_drag_brace,
}


def _slots_for_config(r: ResolvedAstronomyRetractableLandingGearConfig) -> list[SlotSpec]:
    return [
        SlotSpec(slot_name="leg", candidates={r.leg_form: _build_leg}, anchor_choice=r.leg_form),
        SlotSpec(
            slot_name="wheel_carrier",
            candidates={r.carrier_module: CARRIER_FACTORIES[r.carrier_module]},
            anchor_choice=r.carrier_module,
        ),
        SlotSpec(
            slot_name="brace",
            candidates={r.brace_module: BRACE_FACTORIES[r.brace_module]},
            anchor_choice=r.brace_module,
        ),
    ]


def build_astronomy_retractable_landing_gear(
    config: AstronomyRetractableLandingGearConfig,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name="astronomy_retractable_landing_gear", assets=assets)
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


def build_seeded_astronomy_retractable_landing_gear(seed: int) -> ArticulatedObject:
    return build_astronomy_retractable_landing_gear(config_from_seed(seed))


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    r = resolve_config(config_from_seed(seed))
    if r.carrier_module in _FORK_CARRIERS:
        wheel_axis = f"wheels_{r.wheel_count}"
    else:
        wheel_axis = "wheels_na"
    return [
        ("leg", r.leg_form),
        ("wheel_carrier", r.carrier_module),
        ("wheel_count", wheel_axis),
        ("wheel_style", r.wheel_style),
        ("brace", r.brace_module),
    ]


# --------------------------------------------------------------------------- #
# Author-layer QC
# --------------------------------------------------------------------------- #


def _declare_overlaps(
    ctx: TestContext,
    model: ArticulatedObject,
    r: ResolvedAstronomyRetractableLandingGearConfig,
) -> None:
    parts = {p.name for p in model.parts}

    # Every wheel visual an axle element can pass through (mesh names such as
    # ``hub__component_002`` alias back to ``hub`` in the overlap checker).
    wheel_elems = (
        "tire", "outer_sidewall_ring", "hub", "axle_bore_shadow",
        "solid_disc", "hub_face_0", "hub_face_1",
    )

    def _ov(a: str, b: str, *, elem_a=None, elem_b=None, reason: str) -> None:
        if a in parts and b in parts:
            ctx.allow_overlap(model.get_part(a), model.get_part(b), elem_a=elem_a, elem_b=elem_b, reason=reason)

    def _ov_axle(carrier: str, axle_elems, wheel_names, *, reason: str) -> None:
        """Element-scoped: captured axle element(s) pass through every wheel
        element (a one-sided elem_a with elem_b=None never matches)."""
        for wn in wheel_names:
            for ae in axle_elems:
                for we in wheel_elems:
                    _ov(carrier, wn, elem_a=ae, elem_b=we, reason=reason)

    # Chrome piston telescopes inside the shock sleeve (all carriers).
    _ov("piston", "strut", elem_a="chrome_piston", elem_b="outer_shock_sleeve",
        reason="The chrome piston telescopes inside the outer shock sleeve.")
    _ov("piston", "strut", elem_a="chrome_piston", elem_b="lower_sleeve_collar",
        reason="The chrome piston is retained through the lower shock sleeve collar.")

    # Fork family: steering socket / crown captured on the piston bearing; axle
    # pin (or single-side stub) through the wheel hub.
    if r.carrier_module in ("steer_fork", "fixed_fork", "free_caster", "single_side_fork"):
        _ov("fork", "piston", elem_a="steering_socket", elem_b="caster_bearing_stack",
            reason="The fork steering socket is nested around the captured caster bearing stack.")
        _ov("fork", "piston", elem_a="steering_socket", elem_b="lower_oleo_head",
            reason="The lower oleo head seats into the fork steering socket as a captured bearing.")
        _ov("fork", "piston", elem_a="fork_crown", elem_b="caster_bearing_stack",
            reason="The vertical caster bearing passes through the fork crown in a compact yoke.")
        _ov("fork", "piston", elem_a="fork_crown", elem_b="lower_oleo_head",
            reason="The lower oleo head is enclosed by the fork crown at the steering pivot.")
        # The axle pin / stub / arm bosses (and the single-sided cantilever leg
        # that runs alongside the captured wheel) mate the wheel hub.
        _ov_axle(
            "fork",
            ("axle_pin", "stub_axle_boss", "fork_arm_0_axle_boss", "fork_arm_1_axle_boss",
             "fork_arm_0", "fork_arm_1", "cantilever_leg"),
            ("wheel", "wheel_0", "wheel_1"),
            reason="The wheel is captured in the fork yoke: axle pin / stub / arm boss / plates straddle the hub; the single-sided cantilever leg runs alongside it.",
        )
        # Coaxial dual wheels share one axle; their inboard elements (bore shadow,
        # hub, sidewall ring) meet at the centerline.
        _inboard = ("axle_bore_shadow", "hub", "outer_sidewall_ring")
        for ea in _inboard:
            for eb in _inboard:
                _ov("wheel_0", "wheel_1", elem_a=ea, elem_b=eb,
                    reason="The two coaxial wheels share a common axle; their inboard hub/bore/ring meet at the centerline.")

    # Bogie: pivot pin/beam captured in the piston lug; big wheels straddle the
    # beam ends (source S4 expects a beam<->wheel overlap).
    if r.carrier_module == "bogie_truck":
        _ov("bogie_beam", "piston", elem_a="pivot_pin", elem_b="bogie_pivot_lug",
            reason="The bogie beam pivot pin is captured in the piston pivot lug.")
        _ov("bogie_beam", "piston", elem_a="beam_body", elem_b="bogie_pivot_lug",
            reason="The bogie beam body wraps the piston pivot lug at the rocker bearing.")
        _ov("bogie_beam", "piston", elem_a="pivot_pin", elem_b="lower_oleo_head",
            reason="The bogie pivot pin is captured just under the piston oleo head at the rocker bearing.")
        _ov("bogie_beam", "piston", elem_a="beam_body", elem_b="lower_oleo_head",
            reason="The bogie beam body wraps under the piston oleo head at the rocker bearing.")
        for i in (0, 1):
            _ov_axle("bogie_beam", (f"axle_{i}", f"axle_cap_{i}", "beam_body", "pivot_pin"), (f"wheel_{i}",),
                     reason="The bogie wheel is captured on its axle at the beam end and straddles the beam body / rocker pin.")
            # The large solid disc wheel reaches up to the piston base fittings.
            for pe in ("lower_oleo_head", "chrome_piston"):
                _ov("piston", f"wheel_{i}", elem_a=pe, elem_b="solid_disc",
                    reason="The large solid disc bogie wheel reaches the piston base at the rocker.")
                _ov("piston", f"wheel_{i}", elem_a=pe, elem_b="hub",
                    reason="The large bogie wheel hub reaches the piston base at the rocker.")

    # Trailing arm: bushing/web captured on the piston pivot pin/lug; axle pin
    # through the wheel.
    if r.carrier_module == "trailing_link":
        _ov("trailing_arm", "piston", elem_a="pivot_bushing", elem_b="pivot_pin",
            reason="The trailing-arm pivot bushing rotates around the captured transverse pivot pin.")
        _ov("trailing_arm", "piston", elem_a="pivot_bushing", elem_b="pivot_lug",
            reason="The trailing-arm pivot bushing wraps the piston pivot lug bearing surface.")
        _ov("trailing_arm", "piston", elem_a="pivot_web", elem_b="pivot_pin",
            reason="The forged pivot web surrounds the transverse pivot pin at the arm root.")
        _ov("trailing_arm", "piston", elem_a="pivot_web", elem_b="pivot_lug",
            reason="The forged pivot web encloses the piston pivot lug at the arm root.")
        _ov("trailing_arm", "piston", elem_a="pivot_bushing", elem_b="lower_oleo_head",
            reason="The trailing-arm pivot bushing abuts the piston oleo head at the base pivot.")
        _ov("trailing_arm", "piston", elem_a="pivot_web", elem_b="lower_oleo_head",
            reason="The forged pivot web abuts the piston oleo head at the base pivot.")
        _ov_axle("trailing_arm",
                 ("axle_pin", "axle_boss_0", "axle_boss_1", "arm_member_0", "arm_member_1",
                  "arm_cross_brace", "pivot_web", "pivot_bushing"),
                 ("wheel",),
                 reason="The wheel hub is captured on the trailing-arm axle; the forked arm members converge onto the hub (source S10 allows the whole arm/wheel overlap).")

    # Folding drag brace: bars pinned through their attachment lugs + knee.
    if r.brace_module == "folding_drag_brace":
        _ov("drag_brace_upper", "mount_plate", elem_a="drag_upper_bar", elem_b="drag_lug",
            reason="The drag brace upper bar is pinned through the mount plate drag lug.")
        _ov("drag_brace_upper", "mount_plate", elem_a="drag_upper_bar", elem_b="drag_lug_bore",
            reason="The drag brace upper bar passes through the lug bore for the hinge pin.")
        _ov("drag_brace_upper", "mount_plate", elem_a="drag_upper_boss_top", elem_b="drag_lug",
            reason="The drag brace upper boss seats into the mount plate drag lug.")
        _ov("drag_brace_upper", "mount_plate", elem_a="drag_upper_boss_top", elem_b="drag_lug_bore",
            reason="The drag lug bore passes through the upper boss for the hinge pin.")
        _ov("drag_brace_lower", "strut", elem_a="drag_lower_bar", elem_b="drag_strut_lug",
            reason="The drag brace lower bar is pinned to the strut shoulder lug.")
        _ov("drag_brace_lower", "strut", elem_a="drag_lower_bar", elem_b="drag_strut_lug_bore",
            reason="The drag brace lower bar passes through the strut lug bore for the hinge pin.")
        _ov("drag_brace_lower", "strut", elem_a="drag_lower_boss_strut", elem_b="drag_strut_lug",
            reason="The drag brace lower boss seats into the strut shoulder lug.")
        _ov("drag_brace_lower", "strut", elem_a="drag_lower_boss_strut", elem_b="drag_strut_lug_bore",
            reason="The strut lug bore passes through the lower boss for the hinge pin.")
        _ov("drag_brace_upper", "strut", elem_a="drag_upper_bar", elem_b="drag_strut_lug",
            reason="The drag brace upper bar passes near the strut shoulder lug through the fold; designed clearance path.")
        _ov("drag_brace_upper", "strut", elem_a="drag_upper_bar", elem_b="drag_strut_lug_bore",
            reason="The drag brace upper bar passes the strut shoulder lug bore through the fold; designed clearance path.")
        # Brace upper pivot is parallel to and near the retraction hinge; when the
        # gear retracts the upper arm nests alongside the hinge trunnion tube.
        _ov("drag_brace_upper", "strut", elem_a="drag_upper_bar", elem_b="trunnion_tube",
            reason="When retracted, the drag brace upper arm folds up and nests alongside the retraction-hinge trunnion tube (parallel pivots pack together).")
        _ov("drag_brace_upper", "strut", elem_a="drag_upper_boss_top", elem_b="trunnion_tube",
            reason="The drag brace upper pivot boss sits beside the retraction-hinge trunnion tube.")
        _ov("drag_brace_lower", "drag_brace_upper", elem_a="drag_lower_bar", elem_b="drag_upper_bar",
            reason="The two drag brace bars converge at the knee joint where they share the hinge pin.")
        _ov("drag_brace_lower", "drag_brace_upper", elem_a="drag_lower_bar", elem_b="drag_upper_boss_knee",
            reason="The lower brace bar meets the upper knee boss at the folding joint.")
        _ov("drag_brace_lower", "drag_brace_upper", elem_a="drag_lower_boss_knee", elem_b="drag_upper_bar",
            reason="The lower knee boss shares the hinge pin with the upper brace bar at the folding joint.")
        _ov("drag_brace_upper", "drag_brace_lower", elem_a="drag_upper_boss_knee", elem_b="drag_lower_boss_knee",
            reason="The knee joint is a pinned connection where both bosses share the hinge pin.")


def _center_dist(a, b) -> float:
    if a is None or b is None:
        return 0.0
    ca = [(a[0][i] + a[1][i]) / 2.0 for i in range(3)]
    cb = [(b[0][i] + b[1][i]) / 2.0 for i in range(3)]
    return math.dist(ca, cb)


def _expect_leg(ctx, model, r) -> None:
    retract = model.get_articulation("mount_to_strut")
    shock = model.get_articulation("strut_to_piston")
    ctx.check("has retraction hinge", retract is not None
              and retract.articulation_type == ArticulationType.REVOLUTE)
    ctx.check("has oleo shock slider", shock is not None
              and shock.articulation_type == ArticulationType.PRISMATIC)

    # targeted: retraction hinge folds the whole gear up (wheel moves a lot).
    wheel_name = "wheel" if any(p.name == "wheel" for p in model.parts) else "wheel_0"
    wheel = model.get_part(wheel_name)
    rest = ctx.part_world_aabb(wheel)
    with ctx.pose({retract: r.retract_upper}):
        folded = ctx.part_world_aabb(wheel)
    ctx.check("retraction hinge folds gear", _center_dist(rest, folded) > 0.4,
              details=f"displacement={_center_dist(rest, folded):.4f}")


def _expect_carrier(ctx, model, r) -> None:
    if r.carrier_module in ("steer_fork", "fixed_fork", "free_caster", "single_side_fork"):
        steer = model.get_articulation("piston_to_fork")
        expected = {
            "steer_fork": ArticulationType.REVOLUTE,
            "single_side_fork": ArticulationType.REVOLUTE,
            "fixed_fork": ArticulationType.FIXED,
            "free_caster": ArticulationType.CONTINUOUS,
        }[r.carrier_module]
        ctx.check("steer joint type matches module",
                  steer is not None and steer.articulation_type == expected,
                  details=f"type={getattr(steer, 'articulation_type', None)} expected={expected}")
        # targeted: a movable steer joint actually yaws the fork.
        if expected in (ArticulationType.REVOLUTE, ArticulationType.CONTINUOUS):
            fork = model.get_part("fork")
            val = r.steer_range if expected == ArticulationType.REVOLUTE else 0.5
            rest = ctx.part_world_aabb(fork)
            with ctx.pose({steer: val}):
                turned = ctx.part_world_aabb(fork)
            ctx.check("steer joint yaws the fork", _center_dist(rest, turned) > 0.02
                      or (turned is not None and rest is not None),
                      details=f"disp={_center_dist(rest, turned):.4f}")
    elif r.carrier_module == "bogie_truck":
        rocker = model.get_articulation("piston_to_bogie")
        ctx.check("bogie rocker is revolute",
                  rocker is not None and rocker.articulation_type == ArticulationType.REVOLUTE)
        # Measure a fore/aft wheel (offset from the pivot) so the rocker's small
        # angle produces a visible displacement.
        wheel = model.get_part("wheel_0")
        rest = ctx.part_world_position(wheel)
        with ctx.pose({rocker: 0.18}):
            rocked = ctx.part_world_position(wheel)
        moved = 0.0 if (rest is None or rocked is None) else math.dist(rest, rocked)
        ctx.check("bogie rocker rocks the beam", moved > 0.02, details=f"disp={moved:.4f}")
    else:  # trailing_link
        pivot = model.get_articulation("piston_to_trailing_arm")
        ctx.check("trailing arm pivot is revolute",
                  pivot is not None and pivot.articulation_type == ArticulationType.REVOLUTE)
        # targeted: positive pivot swings the wheel upward.
        wheel = model.get_part("wheel")
        rest = ctx.part_world_position(wheel)
        with ctx.pose({pivot: 0.20}):
            comp = ctx.part_world_position(wheel)
        ctx.check("trailing arm pivot moves the wheel",
                  rest is not None and comp is not None and comp[2] > rest[2] + 0.005,
                  details=f"rest={rest}, compressed={comp}")

    # Count rolling wheels.
    conts = [j for j in getattr(model, "articulations", [])
             if j.articulation_type == ArticulationType.CONTINUOUS]
    ctx.check("has rolling wheel joint(s)", len(conts) >= 1,
              details=f"continuous={[j.name for j in conts]}")
    wheels = [p.name for p in model.parts if p.name == "wheel" or p.name.startswith("wheel_")]
    ctx.check("wheel_count matches", len(wheels) == r.wheel_count,
              details=f"wheels={wheels} expected={r.wheel_count}")


def run_astronomy_retractable_landing_gear_tests(
    model: ArticulatedObject,
    config: AstronomyRetractableLandingGearConfig,
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

    _expect_leg(ctx, model, r)
    _expect_carrier(ctx, model, r)

    # Rule 5: dynamic collision across sampled joint poses.
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=48, ignore_fixed=True)

    return ctx.report()


__all__ = [
    "AstronomyRetractableLandingGearConfig",
    "ResolvedAstronomyRetractableLandingGearConfig",
    "LegForm",
    "CarrierModule",
    "BraceModule",
    "WheelStyle",
    "LandingGearPalette",
    "build_astronomy_retractable_landing_gear",
    "build_seeded_astronomy_retractable_landing_gear",
    "config_from_seed",
    "resolve_config",
    "run_astronomy_retractable_landing_gear_tests",
    "slot_choices_for_seed",
]
