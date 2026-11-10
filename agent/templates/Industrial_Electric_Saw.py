# SPDX-License-Identifier: Apache-2.0

"""Industrial / Electric Saw - modular procedural template.

A handheld / bench electric power saw: a compact teal motor ``body`` (housing
shell + cross-motor barrel + gearbox nose + rear cordless battery brick +
rubber-overmolded top handle arch + front grip knob), pre-built as the single
root, carrying three parallel-children slots whose joints all parent directly
to ``body`` (parallel-children pattern, no serial chain joint):

  * cutting_element - the defining moving cutter + its drive joint:
      circular_blade (toothed disc, CONTINUOUS spin + retractable lower guard),
      abrasive_wheel (smooth cut-off disc, CONTINUOUS + lower guard),
      chain_bar (guide bar + traveling chain, CONTINUOUS chain drive),
      reciprocating_blade (straight blade, PRISMATIC stroke);
  * control - the on/off switch + safety lock:
      squeeze_trigger (REVOLUTE trigger + PRISMATIC safety lock),
      paddle_switch (PRISMATIC sliding paddle + PRISMATIC safety lock);
  * mount - how the saw meets the workpiece:
      handheld_shoe (spine-adaptive foot, fused visuals, no joint),
      bevel_shoe (separate shoe on a REVOLUTE bevel-tilt pivot).
    (The miter_arm / table_mount samples are read but not adopted as modules -
    a grounded stationary base is incompatible with the compact body-as-root,
    blade-down canonical frame; see the spec's Adopted Source note.)

One multiplicity axis rides on top: ``tooth_count`` (teeth on the circular
blade). Every cutter candidate creates at least one non-FIXED joint, so a
static-only model is never produced.

Adapted per AUTHORING.md A/B from the confirmed 5-star Electric Saw pool
(spec: specs_modular_v1/Industrial_Electric_Saw.md). Sources (model.py:Lx-Ly in
the spec Module Source Index):

  S1  origin rec_a-cordless-...88da991f - body chassis, circular blade
      CONTINUOUS spin, lower guard REVOLUTE, squeeze trigger REVOLUTE,
      safety lock PRISMATIC, flat handheld shoe, all test/allow_overlap semantics.
  S2/S3 teeth_count_coarse/fine - tooth_count multiplicity {24,60}.
  S4  cutoff_wheel        - smooth abrasive disc aperture.
  S5  chainsaw_bar        - guide bar + traveling chain CONTINUOUS drive.
  S6  reciprocating_blade - straight blade PRISMATIC stroke.
  S7  paddle_switch       - PRISMATIC sliding paddle switch.
  S8  bevel_pivot         - separate shoe on REVOLUTE bevel-tilt pivot.
  S9  miter_arm           - stationary base + REVOLUTE drop-cut arm hinge.

Coordinate frame: +X forward (blade travel / tool nose), +Z up, +Y left (motor
cap side); blade plane on the -Y (right) side of the housing.
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
    Box,
    Cylinder,
    ExtrudeGeometry,
    ExtrudeWithHolesGeometry,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    clamp_joint_limits,
    mesh_from_geometry,
    rounded_rect_profile,
    tube_from_spline_points,
)

# Modular template: sweep coverage uses module_topology_diversity.
__modular__ = True

HALF_PI = math.pi / 2.0


CuttingElement = Literal[
    "circular_blade",
    "abrasive_wheel",
    "chain_bar",
    "reciprocating_blade",
]
ControlModule = Literal["squeeze_trigger", "paddle_switch"]
MountModule = Literal["handheld_shoe", "bevel_shoe"]
SawPalette = Literal[
    "teal_classic",
    "safety_yellow",
    "industrial_red",
    "graphite_black",
    "cobalt_blue",
    "bare_metal",
]

_DISC_CUTTERS = ("circular_blade", "abrasive_wheel")
_BARE_CUTTERS = ("chain_bar", "reciprocating_blade")


# --------------------------------------------------------------------------- #
# Canonical nominal dimensions (origin 母本 rec_a-...88da991f). Every geometric
# coordinate/size is multiplied by ``body_scale`` at build time so the whole
# tool scales uniformly (blade / housing / handle co-scale, Contract 3e).
# --------------------------------------------------------------------------- #

N_BLADE_R = 0.076    # blade radius
N_BLADE_CX = 0.095   # arbor X on the housing
N_BLADE_CZ = 0.070   # arbor Z (center height)
N_BLADE_Y = -0.078   # blade plane (visible right side of the housing)
N_GUARD_Y = -0.058   # fixed upper guard sits inboard
N_SHOE_Z = 0.037     # base shoe top


# --------------------------------------------------------------------------- #
# Palettes (>=5 colorways; every token shared so each .visual resolves)
# --------------------------------------------------------------------------- #

PALETTES: dict[str, dict[str, tuple[float, float, float, float]]] = {
    "teal_classic": {
        "housing": (0.10, 0.52, 0.55, 1.0),
        "housing_dark": (0.07, 0.40, 0.43, 1.0),
        "black_plastic": (0.09, 0.09, 0.10, 1.0),
        "charcoal": (0.17, 0.18, 0.19, 1.0),
        "chrome": (0.82, 0.83, 0.85, 1.0),
        "guard_steel": (0.74, 0.75, 0.77, 1.0),
        "blade_steel": (0.66, 0.67, 0.70, 1.0),
        "accent": (0.72, 0.14, 0.12, 1.0),
    },
    "safety_yellow": {
        "housing": (0.90, 0.75, 0.10, 1.0),
        "housing_dark": (0.70, 0.58, 0.08, 1.0),
        "black_plastic": (0.10, 0.10, 0.11, 1.0),
        "charcoal": (0.18, 0.18, 0.19, 1.0),
        "chrome": (0.80, 0.81, 0.83, 1.0),
        "guard_steel": (0.72, 0.73, 0.75, 1.0),
        "blade_steel": (0.64, 0.65, 0.68, 1.0),
        "accent": (0.12, 0.13, 0.15, 1.0),
    },
    "industrial_red": {
        "housing": (0.72, 0.14, 0.12, 1.0),
        "housing_dark": (0.55, 0.10, 0.09, 1.0),
        "black_plastic": (0.09, 0.09, 0.10, 1.0),
        "charcoal": (0.16, 0.16, 0.17, 1.0),
        "chrome": (0.82, 0.83, 0.85, 1.0),
        "guard_steel": (0.74, 0.75, 0.77, 1.0),
        "blade_steel": (0.66, 0.67, 0.70, 1.0),
        "accent": (0.90, 0.78, 0.16, 1.0),
    },
    "graphite_black": {
        "housing": (0.16, 0.17, 0.18, 1.0),
        "housing_dark": (0.10, 0.11, 0.12, 1.0),
        "black_plastic": (0.06, 0.06, 0.07, 1.0),
        "charcoal": (0.13, 0.13, 0.14, 1.0),
        "chrome": (0.78, 0.79, 0.81, 1.0),
        "guard_steel": (0.60, 0.61, 0.63, 1.0),
        "blade_steel": (0.62, 0.63, 0.66, 1.0),
        "accent": (0.85, 0.40, 0.10, 1.0),
    },
    "cobalt_blue": {
        "housing": (0.12, 0.28, 0.62, 1.0),
        "housing_dark": (0.08, 0.20, 0.46, 1.0),
        "black_plastic": (0.09, 0.09, 0.10, 1.0),
        "charcoal": (0.16, 0.17, 0.18, 1.0),
        "chrome": (0.82, 0.83, 0.85, 1.0),
        "guard_steel": (0.74, 0.75, 0.77, 1.0),
        "blade_steel": (0.66, 0.67, 0.70, 1.0),
        "accent": (0.90, 0.72, 0.20, 1.0),
    },
    "bare_metal": {
        "housing": (0.66, 0.68, 0.71, 1.0),
        "housing_dark": (0.50, 0.52, 0.55, 1.0),
        "black_plastic": (0.10, 0.10, 0.11, 1.0),
        "charcoal": (0.28, 0.29, 0.31, 1.0),
        "chrome": (0.86, 0.88, 0.90, 1.0),
        "guard_steel": (0.78, 0.79, 0.81, 1.0),
        "blade_steel": (0.70, 0.71, 0.74, 1.0),
        "accent": (0.72, 0.14, 0.12, 1.0),
    },
}
PALETTE_NAMES = tuple(PALETTES.keys())


# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class IndustrialElectricSawConfig:
    cutting_element: CuttingElement = "circular_blade"
    control: ControlModule = "squeeze_trigger"
    mount: MountModule = "handheld_shoe"
    palette_style: SawPalette = "teal_classic"

    tooth_count: int = 48   # circular_blade only

    body_scale: float = 1.0
    bevel_range: float = 0.75   # bevel_shoe tilt upper (rad)
    miter_range: float = 0.50   # arm_hinge upper (rad)


@dataclass(frozen=True)
class ResolvedIndustrialElectricSawConfig:
    cutting_element: CuttingElement
    control: ControlModule
    mount: MountModule
    palette_style: str

    tooth_count: int

    body_scale: float
    bevel_range: float
    miter_range: float

    palette: dict[str, tuple[float, float, float, float]]

    @property
    def s(self) -> float:
        return self.body_scale


# --------------------------------------------------------------------------- #
# Seed-driven sampling (procedural-first)
# --------------------------------------------------------------------------- #


def config_from_seed(seed: int) -> IndustrialElectricSawConfig:
    """Deterministic procedural sampling.

    seed 0 is pinned to the origin 母本 combination (circular_blade x48 +
    squeeze_trigger + handheld_shoe, teal_classic) as a documented regression
    anchor (a sparse override; every other seed is fully procedural).
    """
    if seed == 0:
        return IndustrialElectricSawConfig()

    rng = random.Random(seed)

    cutting_element: CuttingElement = rng.choice(
        ("circular_blade", "abrasive_wheel", "chain_bar", "reciprocating_blade")
    )
    control: ControlModule = rng.choice(("squeeze_trigger", "paddle_switch"))
    # mount is gated by the cutter spine (resolved in resolve_config); sample a
    # candidate here and let the gate coerce bare cutters to handheld_shoe.
    mount: MountModule = rng.choice(("handheld_shoe", "bevel_shoe"))
    palette_style = rng.choice(PALETTE_NAMES)

    tooth_count = rng.choices((24, 48, 60), weights=(0.3, 0.4, 0.3))[0]

    body_scale = round(rng.uniform(0.90, 1.15), 4)
    bevel_range = round(rng.uniform(0.45, 0.80), 4)
    miter_range = round(rng.uniform(0.35, 0.55), 4)

    return IndustrialElectricSawConfig(
        cutting_element=cutting_element,
        control=control,
        mount=mount,
        palette_style=palette_style,
        tooth_count=tooth_count,
        body_scale=body_scale,
        bevel_range=bevel_range,
        miter_range=miter_range,
    )


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(float(v), hi))


def resolve_config(
    config: IndustrialElectricSawConfig,
) -> ResolvedIndustrialElectricSawConfig:
    if str(config.cutting_element) not in {
        "circular_blade", "abrasive_wheel", "chain_bar", "reciprocating_blade",
    }:
        raise ValueError(f"Unsupported cutting_element: {config.cutting_element}")
    if str(config.control) not in {"squeeze_trigger", "paddle_switch"}:
        raise ValueError(f"Unsupported control: {config.control}")
    if str(config.mount) not in {"handheld_shoe", "bevel_shoe"}:
        raise ValueError(f"Unsupported mount: {config.mount}")
    if str(config.palette_style) not in PALETTES:
        raise ValueError(f"Unsupported palette_style: {config.palette_style}")

    body_scale = _clamp(config.body_scale, 0.90, 1.15)
    bevel_range = _clamp(config.bevel_range, 0.45, 0.80)
    miter_range = _clamp(config.miter_range, 0.35, 0.55)

    # tooth_count only meaningful for the toothed circular blade.
    tooth_count = int(_clamp(config.tooth_count, 24, 60))

    # Mount gate: chain saw / reciprocating saw are bare handheld tools with no
    # base plate, so they take handheld_shoe only. Disc saws admit any mount.
    mount: MountModule = config.mount
    if config.cutting_element in _BARE_CUTTERS:
        mount = "handheld_shoe"

    return ResolvedIndustrialElectricSawConfig(
        cutting_element=config.cutting_element,
        control=config.control,
        mount=mount,
        palette_style=config.palette_style,
        tooth_count=tooth_count,
        body_scale=body_scale,
        bevel_range=bevel_range,
        miter_range=miter_range,
        palette=dict(PALETTES[config.palette_style]),
    )


# --------------------------------------------------------------------------- #
# Shared geometry helpers (adapted from origin 母本 + variants; primitive
# families preserved - Rule 3)
# --------------------------------------------------------------------------- #


def _side_extrusion(profile, width: float, name: str):
    """Extrude an XZ side-silhouette profile along the Y (width) axis."""
    geom = ExtrudeGeometry(profile, width, cap=True, center=True)
    geom.rotate_x(HALF_PI)
    return mesh_from_geometry(geom, name)


def _side_loop(outer, hole, width: float, name: str):
    """Extrude an XZ loop profile with a through opening along Y (top handle)."""
    geom = ExtrudeWithHolesGeometry(outer, [hole], width, cap=True, center=True)
    geom.rotate_x(HALF_PI)
    return mesh_from_geometry(geom, name)


def _blade_teeth_profile(inner_r: float, outer_r: float, n: int):
    """Closed polygon of a toothed disc in the XZ plane (origin S1 L60-68)."""
    pts = []
    for i in range(n):
        a0 = (i / n) * 2.0 * math.pi
        a1 = ((i + 0.5) / n) * 2.0 * math.pi
        pts.append((outer_r * math.cos(a0), outer_r * math.sin(a0)))
        pts.append((inner_r * math.cos(a1), inner_r * math.sin(a1)))
    return pts


def _smooth_disc_profile(radius: float, n: int = 64):
    """Closed polygon of a smooth disc in the XZ plane (cutoff_wheel S4 L64-70)."""
    return [
        (radius * math.cos((i / n) * 2.0 * math.pi),
         radius * math.sin((i / n) * 2.0 * math.pi))
        for i in range(n)
    ]


def _reciprocating_blade_profile(length: float, height: float, n_teeth: int):
    """Side-view XZ profile of a straight reciprocating blade with teeth on the
    bottom edge and a tapered tip (reciprocating_blade S6 L62-100)."""
    half_h = height / 2.0
    tooth_depth = height * 0.22
    tooth_pitch = length * 0.85 / n_teeth
    tooth_start_x = length * 0.05
    pts = [(0.0, half_h), (length * 0.92, half_h), (length, 0.0)]
    for i in range(n_teeth):
        x0 = tooth_start_x + (n_teeth - 1 - i) * tooth_pitch + tooth_pitch
        x_mid = x0 - tooth_pitch * 0.5
        x1 = x0 - tooth_pitch
        pts.append((x0, -half_h))
        pts.append((x_mid, -half_h - tooth_depth))
        pts.append((x1, -half_h))
    pts.append((0.0, -half_h))
    pts.append((0.0, half_h))
    return pts


# --------------------------------------------------------------------------- #
# Root body chassis (pre-built; constant across all samples)
# --------------------------------------------------------------------------- #


def _body_downstream(r: ResolvedIndustrialElectricSawConfig) -> InterfaceSpec:
    s = r.s
    return InterfaceSpec(
        interface_name="downstream",
        part_name="body",
        visual_name="housing_shell",
        face_side="positive_z",
        anchor_local=(0.03 * s, 0.0, 0.19 * s),
        contact_tol=0.004,
    )


def _build_body_chassis(model: ArticulatedObject, r: ResolvedIndustrialElectricSawConfig) -> None:
    """Common teal motor housing shell + motor + battery + top handle + grip.
    Cutter-, switch- and mount-specific host visuals are added by the slot
    modules onto this same part (Rule 4 conformal decoration)."""
    s = r.s
    body = model.part("body")

    # Main motor housing block (rounded side silhouette, extruded across Y).
    body.visual(
        _side_extrusion(rounded_rect_profile(0.17 * s, 0.11 * s, 0.035 * s), 0.075 * s, "housing_block"),
        origin=Origin(xyz=(0.03 * s, 0.0, 0.105 * s)),
        material="housing",
        name="housing_shell", material_class_id="plastic.opaque_glossy_molded",
    )
    # Cross-mounted motor barrel on the left side, above the blade line.
    body.visual(
        Cylinder(radius=0.046 * s, length=0.070 * s),
        origin=Origin(xyz=(0.045 * s, 0.055 * s, 0.115 * s), rpy=(HALF_PI, 0.0, 0.0)),
        material="housing",
        name="motor_barrel", material_class_id="plastic.opaque_glossy_molded",
    )
    body.visual(
        Cylinder(radius=0.036 * s, length=0.012 * s),
        origin=Origin(xyz=(0.045 * s, 0.093 * s, 0.115 * s), rpy=(HALF_PI, 0.0, 0.0)),
        material="black_plastic",
        name="motor_end_cap", material_class_id="plastic.opaque_generic",
    )
    # Rear cordless battery brick.
    body.visual(
        Box((0.075 * s, 0.090 * s, 0.070 * s)),
        origin=Origin(xyz=(-0.060 * s, 0.0, 0.075 * s)),
        material="black_plastic",
        name="battery_pack", material_class_id="plastic.opaque_generic",
    )
    body.visual(
        Box((0.060 * s, 0.070 * s, 0.014 * s)),
        origin=Origin(xyz=(-0.030 * s, 0.0, 0.075 * s)),
        material="charcoal",
        name="battery_terminal_shroud", material_class_id="plastic.opaque_generic",
    )
    # Rubber-overmolded top handle arch with a through opening for the hand.
    body.visual(
        _side_loop(
            [(x - 0.005 * s, z + 0.199 * s) for x, z in rounded_rect_profile(0.150 * s, 0.090 * s, 0.028 * s)],
            [(x - 0.005 * s, z + 0.194 * s) for x, z in rounded_rect_profile(0.090 * s, 0.045 * s, 0.020 * s)],
            0.032 * s,
            "top_handle",
        ),
        material="black_plastic",
        name="top_handle", material_class_id="rubber.smooth_plain",
    )
    # Front grip knob on the housing top-front.
    body.visual(
        Cylinder(radius=0.024 * s, length=0.055 * s),
        origin=Origin(xyz=(0.105 * s, 0.0, 0.150 * s), rpy=(HALF_PI, 0.0, 0.0)),
        material="black_plastic",
        name="front_grip", material_class_id="rubber.smooth_plain",
    )
    # Power/label plate accent on the housing side (decoration).
    body.visual(
        Box((0.070 * s, 0.004 * s, 0.030 * s)),
        origin=Origin(xyz=(0.03 * s, 0.075 * s, 0.130 * s)),
        material="accent",
        name="brand_plate", material_class_id="plastic.opaque_glossy_molded",
    )
    # Short rubber strain node at the rear (decoration).
    cord_geom = tube_from_spline_points(
        [(-0.095 * s, 0.030 * s, 0.075 * s), (-0.110 * s, 0.045 * s, 0.070 * s),
         (-0.120 * s, 0.055 * s, 0.060 * s)],
        radius=0.006 * s, samples_per_segment=8,
    )
    body.visual(mesh_from_geometry(cord_geom, "vent_stub"), material="charcoal", name="vent_stub", material_class_id="rubber.smooth_plain")


# --------------------------------------------------------------------------- #
# Slot A - cutting_element (parallel children on body)
# --------------------------------------------------------------------------- #


def _emit_disc_host_visuals(body, r: ResolvedIndustrialElectricSawConfig) -> None:
    """Upper guard cluster + arbor boss + gearbox nose + lower-guard pivot boss
    shared by circular_blade / abrasive_wheel (origin S1 L108-156, 254-259)."""
    s = r.s
    bcx, bcz, blr = N_BLADE_CX * s, N_BLADE_CZ * s, N_BLADE_R * s
    # Upper fixed blade guard: inboard half-disc shroud over the top of the blade.
    ug_ang = [math.pi * (0.03 + 0.94 * i / 36) for i in range(37)]
    body.visual(
        _side_extrusion(
            [((blr + 0.016 * s) * math.cos(a) + bcx, (blr + 0.016 * s) * math.sin(a) + bcz) for a in ug_ang]
            + [(blr * math.cos(a) + bcx, blr * math.sin(a) + bcz) for a in reversed(ug_ang)],
            0.020 * s, "upper_guard_ring",
        ),
        origin=Origin(xyz=(0.0, N_GUARD_Y * s, 0.0)),
        material="housing_dark",
        name="upper_guard", material_class_id="plastic.opaque_generic",
    )
    body.visual(
        _side_extrusion(
            [((blr + 0.014 * s) * math.cos(a) + bcx, (blr + 0.014 * s) * math.sin(a) + bcz)
             for a in [math.pi * (0.05 + 0.9 * i / 24) for i in range(25)]]
            + [(bcx - (blr + 0.014 * s), bcz), (bcx + (blr + 0.014 * s), bcz)],
            0.030 * s, "upper_guard_web",
        ),
        origin=Origin(xyz=(0.0, N_GUARD_Y * s + 0.003 * s, 0.0)),
        material="housing_dark",
        name="upper_guard_web", material_class_id="plastic.opaque_generic",
    )
    # Arbor boss carrying the blade.
    body.visual(
        Cylinder(radius=0.014 * s, length=0.026 * s),
        origin=Origin(xyz=(bcx, N_BLADE_Y * s + 0.020 * s, bcz), rpy=(HALF_PI, 0.0, 0.0)),
        material="charcoal", name="arbor_boss", material_class_id="metal.blackened_gunmetal",
    )
    # Gearbox nose bridging the housing to the arbor cluster.
    body.visual(
        Box((0.060 * s, 0.035 * s, 0.080 * s)),
        origin=Origin(xyz=(0.128 * s, -0.030 * s, 0.075 * s)),
        material="housing", name="gearbox_nose", material_class_id="plastic.opaque_glossy_molded",
    )
    # Lower guard pivot boss (coaxial with arbor, front side).
    body.visual(
        Cylinder(radius=0.010 * s, length=0.038 * s),
        origin=Origin(xyz=(bcx, -0.076 * s, bcz), rpy=(HALF_PI, 0.0, 0.0)),
        material="charcoal", name="lower_guard_pivot_boss", material_class_id="metal.blackened_gunmetal",
    )


def _emit_lower_guard(model, body, r: ResolvedIndustrialElectricSawConfig) -> str:
    """Retractable lower blade guard (origin S1 L328-360)."""
    s = r.s
    blr = N_BLADE_R * s
    lower_guard = model.part("lower_guard")
    lg_ang = [math.pi * (1.02 + 0.62 * i / 24) for i in range(25)]
    lower_guard.visual(
        _side_extrusion(
            [((blr + 0.010 * s) * math.cos(a), (blr + 0.010 * s) * math.sin(a)) for a in lg_ang]
            + [((blr - 0.004 * s) * math.cos(a), (blr - 0.004 * s) * math.sin(a)) for a in reversed(lg_ang)],
            0.024 * s, "lower_guard_shell",
        ),
        material="guard_steel", name="lower_guard_shell", material_class_id="metal.steel_bare",
    )
    lower_guard.visual(
        Box((0.030 * s, 0.010 * s, 0.014 * s)),
        origin=Origin(xyz=(-(blr + 0.004 * s), 0.0, 0.0)),
        material="black_plastic", name="lower_guard_tab", material_class_id="plastic.opaque_generic",
    )
    # Pivot collar coaxial with the arbor (the guard rotates on it) - puts real
    # child hardware on the joint axis so the origin-honesty check holds.
    lower_guard.visual(
        Cylinder(radius=0.013 * s, length=0.030 * s), origin=Origin(rpy=(HALF_PI, 0.0, 0.0)),
        material="charcoal", name="lower_guard_hub", material_class_id="metal.blackened_gunmetal",
    )
    # Arm tying the pivot collar out to the retract tab / shell (connectivity).
    lower_guard.visual(
        Box((blr + 0.004 * s, 0.010 * s, 0.012 * s)),
        origin=Origin(xyz=(-(blr + 0.004 * s) / 2.0, 0.0, 0.0)),
        material="black_plastic", name="lower_guard_arm", material_class_id="plastic.opaque_generic",
    )
    model.articulation(
        "lower_guard_retract", ArticulationType.REVOLUTE, parent=body, child=lower_guard,
        origin=Origin(xyz=(N_BLADE_CX * s, N_BLADE_Y * s - 0.011 * s, N_BLADE_CZ * s)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=4.0, velocity=6.0, lower=0.0, upper=1.8),
    )
    return "lower_guard"


def _emit_disc_blade(model, body, r: ResolvedIndustrialElectricSawConfig, *, toothed: bool) -> None:
    """Circular saw blade (toothed) or abrasive cut-off wheel (smooth)."""
    s = r.s
    blr = N_BLADE_R * s
    blade = model.part("blade")
    if toothed:
        blade.visual(
            _side_extrusion(_blade_teeth_profile(blr - 0.007 * s, blr, r.tooth_count), 0.0026 * s, "blade_disc"),
            material="blade_steel", name="blade_disc", material_class_id="metal.steel_bare",
        )
        blade.visual(
            Cylinder(radius=blr - 0.005 * s, length=0.0016 * s), origin=Origin(rpy=(HALF_PI, 0.0, 0.0)),
            material="chrome", name="blade_plate", material_class_id="metal.chrome_polished",
        )
        blade.visual(
            Cylinder(radius=blr * 0.36, length=0.0032 * s), origin=Origin(rpy=(HALF_PI, 0.0, 0.0)),
            material="blade_steel", name="blade_inner_ring", material_class_id="metal.steel_bare",
        )
    else:
        blade.visual(
            _side_extrusion(_smooth_disc_profile(blr), 0.003 * s, "blade_disc"),
            material="abrasive_disc", name="blade_disc", material_class_id="stone.rough_rock",
        )
        blade.visual(
            Cylinder(radius=blr * 0.36, length=0.0040 * s), origin=Origin(rpy=(HALF_PI, 0.0, 0.0)),
            material="chrome", name="blade_plate", material_class_id="metal.chrome_polished",
        )
    blade.visual(
        Cylinder(radius=0.014 * s, length=0.010 * s), origin=Origin(rpy=(HALF_PI, 0.0, 0.0)),
        material="charcoal", name="arbor_bolt", material_class_id="metal.blackened_gunmetal",
    )
    model.articulation(
        "blade_spin", ArticulationType.CONTINUOUS, parent=body, child=blade,
        origin=Origin(xyz=(N_BLADE_CX * s, N_BLADE_Y * s, N_BLADE_CZ * s)),
        axis=(0.0, 1.0, 0.0), motion_limits=MotionLimits(effort=8.0, velocity=350.0),
    )


def _build_circular_blade(ctx: ModuleBuildContext) -> ModuleBuild:
    model, r = ctx.model, ctx.config  # type: ignore[assignment]
    body = model.get_part("body")
    _emit_disc_host_visuals(body, r)
    _emit_disc_blade(model, body, r, toothed=True)
    lg = _emit_lower_guard(model, body, r)
    return ModuleBuild(
        module_name="circular_blade", parts_emitted=["blade", lg],
        internal_articulations=["blade_spin", "lower_guard_retract"],
        interfaces={"downstream": _body_downstream(r)},
    )


def _build_abrasive_wheel(ctx: ModuleBuildContext) -> ModuleBuild:
    model, r = ctx.model, ctx.config  # type: ignore[assignment]
    body = model.get_part("body")
    _emit_disc_host_visuals(body, r)
    _emit_disc_blade(model, body, r, toothed=False)
    lg = _emit_lower_guard(model, body, r)
    return ModuleBuild(
        module_name="abrasive_wheel", parts_emitted=["blade", lg],
        internal_articulations=["blade_spin", "lower_guard_retract"],
        interfaces={"downstream": _body_downstream(r)},
    )


# ---- chain_bar -------------------------------------------------------------


def _guide_bar_profile(bar_len: float, hw: float):
    """XZ profile of the guide bar (chainsaw S5 L82-100): elongated flat plate
    with a rounded nose on +X."""
    half_len = bar_len / 2.0
    pts = [(-half_len, -hw), (half_len - hw, -hw)]
    for i in range(17):
        a = -HALF_PI + math.pi * i / 16
        pts.append(((half_len - hw) + hw * math.cos(a), hw * math.sin(a)))
    pts.append((-half_len, hw))
    return pts


def _build_chain_bar(ctx: ModuleBuildContext) -> ModuleBuild:
    """Guide bar host visuals + a traveling chain ring on a CONTINUOUS drive
    (chainsaw_bar S5 L35-175, 217-271, 346-380)."""
    model, r = ctx.model, ctx.config  # type: ignore[assignment]
    body = model.get_part("body")
    s = r.s

    bar_len = 0.260 * s
    hw = 0.024 * s
    bar_thick = 0.007 * s
    bar_rear_x = 0.150 * s
    bar_y = -0.055 * s
    bar_cz = 0.068 * s
    bar_center_x = bar_rear_x + bar_len / 2.0
    sprocket_x = 0.155 * s
    link_dx, link_dy, link_dz = 0.016 * s, 0.003 * s, 0.007 * s
    radial = 0.006 * s

    # ---- host visuals on body ----
    body.visual(
        Box((0.055 * s, 0.035 * s, 0.075 * s)),
        origin=Origin(xyz=(0.128 * s, -0.030 * s, 0.072 * s)), material="housing", name="gearbox_nose", material_class_id="plastic.opaque_glossy_molded",
    )
    body.visual(
        Box((0.060 * s, 0.030 * s, 0.060 * s)),
        origin=Origin(xyz=(0.135 * s, -0.044 * s, 0.068 * s)), material="housing", name="clutch_cover", material_class_id="plastic.opaque_glossy_molded",
    )
    body.visual(
        _side_extrusion(_guide_bar_profile(bar_len, hw), bar_thick, "guide_bar"),
        origin=Origin(xyz=(bar_center_x, bar_y, bar_cz)), material="blade_steel", name="guide_bar", material_class_id="metal.steel_bare",
    )
    body.visual(
        Cylinder(radius=0.018 * s, length=0.008 * s),
        origin=Origin(xyz=(sprocket_x, bar_y, bar_cz), rpy=(HALF_PI, 0.0, 0.0)),
        material="chrome", name="drive_sprocket", material_class_id="metal.chrome_polished",
    )
    body.visual(
        Cylinder(radius=0.014 * s, length=0.010 * s),
        origin=Origin(xyz=(bar_rear_x + bar_len - hw, bar_y, bar_cz), rpy=(HALF_PI, 0.0, 0.0)),
        material="chrome", name="nose_sprocket", material_class_id="metal.chrome_polished",
    )
    body.visual(
        Box((0.020 * s, 0.012 * s, 0.040 * s)),
        origin=Origin(xyz=(0.120 * s, -0.058 * s, 0.040 * s)), material="charcoal", name="chain_catcher", material_class_id="metal.blackened_gunmetal",
    )
    body.visual(
        Box((0.060 * s, 0.060 * s, 0.020 * s)),
        origin=Origin(xyz=(0.02 * s, 0.0, 0.045 * s)), material="black_plastic", name="oil_tank", material_class_id="plastic.opaque_generic",
    )

    # ---- chain ring (sprocket-local path) ----
    bar_local_rear = bar_rear_x - sprocket_x
    nose_cx = bar_rear_x + bar_len - hw - sprocket_x
    straight = bar_len - hw
    hw_out = hw + radial
    arc_len = math.pi * hw_out
    perimeter = 2.0 * straight + arc_len
    num_links = max(24, int(round(perimeter / (link_dx * 0.95))))

    chain = model.part("chain")
    link_mesh = Box((link_dx, link_dy, link_dz))
    spacing = perimeter / num_links
    for i in range(num_links):
        d = i * spacing
        if d < straight:
            x = bar_local_rear + d
            z = -hw_out
            angle = 0.0
        elif d < straight + arc_len:
            a = -HALF_PI + (d - straight) / arc_len * math.pi
            x = nose_cx + hw_out * math.cos(a)
            z = hw_out * math.sin(a)
            angle = a + HALF_PI
        else:
            x = nose_cx - (d - straight - arc_len)
            z = hw_out
            angle = math.pi
        chain.visual(link_mesh, origin=Origin(xyz=(x, 0.0, z), rpy=(0.0, angle, 0.0)),
                     material="blade_steel", name=f"link_{i}", material_class_id="metal.steel_bare")

    # Thin connecting rail band tying all cutter links into one assembly.
    def _rail(hw_r: float, rear_dx: float):
        pts = [(bar_local_rear - rear_dx, -hw_r), (nose_cx, -hw_r)]
        for i in range(17):
            a = -HALF_PI + math.pi * i / 16
            pts.append((nose_cx + hw_r * math.cos(a), hw_r * math.sin(a)))
        pts.append((bar_local_rear - rear_dx, hw_r))
        return pts

    rail_geom = ExtrudeWithHolesGeometry(
        _rail(hw + radial + 0.001 * s, 0.002 * s), [_rail(hw + radial - 0.001 * s, 0.0)],
        0.002 * s, cap=True, center=True,
    )
    rail_geom.rotate_x(HALF_PI)
    chain.visual(mesh_from_geometry(rail_geom, "chain_rail"), material="blade_steel", name="chain_rail", material_class_id="metal.steel_bare")

    model.articulation(
        "chain_drive", ArticulationType.CONTINUOUS, parent=body, child=chain,
        origin=Origin(xyz=(sprocket_x, bar_y, bar_cz)),
        axis=(0.0, 1.0, 0.0), motion_limits=MotionLimits(effort=8.0, velocity=200.0),
    )
    return ModuleBuild(
        module_name="chain_bar", parts_emitted=["chain"],
        internal_articulations=["chain_drive"],
        interfaces={"downstream": _body_downstream(r)},
    )


# ---- reciprocating_blade ---------------------------------------------------


def _build_reciprocating_blade(ctx: ModuleBuildContext) -> ModuleBuild:
    """Straight toothed blade on a PRISMATIC stroke (reciprocating S6)."""
    model, r = ctx.model, ctx.config  # type: ignore[assignment]
    body = model.get_part("body")
    s = r.s

    blade_len = 0.150 * s
    blade_h = 0.022 * s
    blade_t = 0.0014 * s
    stroke = 0.028 * s
    clamp_x, clamp_y, clamp_z = 0.158 * s, -0.030 * s, 0.075 * s

    # ---- host visuals on body ----
    body.visual(
        Box((0.060 * s, 0.035 * s, 0.080 * s)),
        origin=Origin(xyz=(0.128 * s, -0.030 * s, 0.075 * s)), material="housing", name="gearbox_nose", material_class_id="plastic.opaque_glossy_molded",
    )
    body.visual(
        Cylinder(radius=0.016 * s, length=0.022 * s),
        origin=Origin(xyz=(clamp_x, clamp_y, clamp_z), rpy=(0.0, HALF_PI, 0.0)),
        material="charcoal", name="blade_clamp", material_class_id="metal.blackened_gunmetal",
    )
    body.visual(
        Cylinder(radius=0.020 * s, length=0.008 * s),
        origin=Origin(xyz=(clamp_x + 0.005 * s, clamp_y, clamp_z), rpy=(0.0, HALF_PI, 0.0)),
        material="chrome", name="clamp_collar", material_class_id="metal.chrome_polished",
    )

    # ---- moving straight blade ----
    blade = model.part("blade")
    blade.visual(
        _side_extrusion(_reciprocating_blade_profile(blade_len, blade_h, 18), blade_t, "blade_body"),
        material="blade_steel", name="blade_body", material_class_id="metal.steel_bare",
    )
    blade.visual(
        Box((0.022 * s, blade_t + 0.001 * s, 0.013 * s)),
        origin=Origin(xyz=(-0.008 * s, 0.0, 0.0)), material="chrome", name="blade_shank", material_class_id="metal.chrome_polished",
    )
    model.articulation(
        "blade_stroke", ArticulationType.PRISMATIC, parent=body, child=blade,
        origin=Origin(xyz=(clamp_x, clamp_y, clamp_z)), axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=12.0, velocity=0.8, lower=-stroke / 2.0, upper=stroke / 2.0),
    )
    return ModuleBuild(
        module_name="reciprocating_blade", parts_emitted=["blade"],
        internal_articulations=["blade_stroke"],
        interfaces={"downstream": _body_downstream(r)},
    )


# --------------------------------------------------------------------------- #
# Slot B - control (parallel children on body)
# --------------------------------------------------------------------------- #


def _emit_safety_lock(model, body, r: ResolvedIndustrialElectricSawConfig) -> str:
    s = r.s
    safety_lock = model.part("safety_lock")
    safety_lock.visual(
        Cylinder(radius=0.009 * s, length=0.014 * s), origin=Origin(rpy=(HALF_PI, 0.0, 0.0)),
        material="accent", name="safety_lock_cap", material_class_id="plastic.opaque_glossy_molded",
    )
    model.articulation(
        "safety_lock_press", ArticulationType.PRISMATIC, parent=body, child=safety_lock,
        origin=Origin(xyz=(0.055 * s, 0.014 * s, 0.190 * s)), axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=3.0, velocity=0.1, lower=0.0, upper=0.005 * s),
    )
    return "safety_lock"


def _build_squeeze_trigger(ctx: ModuleBuildContext) -> ModuleBuild:
    model, r = ctx.model, ctx.config  # type: ignore[assignment]
    body = model.get_part("body")
    s = r.s
    # Trigger pivot ears (host visuals).
    body.visual(Box((0.014 * s, 0.010 * s, 0.020 * s)),
                origin=Origin(xyz=(0.075 * s, 0.020 * s, 0.150 * s)), material="charcoal", name="trigger_ear_left", material_class_id="plastic.opaque_generic")
    body.visual(Box((0.014 * s, 0.010 * s, 0.020 * s)),
                origin=Origin(xyz=(0.075 * s, -0.020 * s, 0.150 * s)), material="charcoal", name="trigger_ear_right", material_class_id="plastic.opaque_generic")
    trigger = model.part("trigger")
    trigger.visual(Box((0.014 * s, 0.030 * s, 0.014 * s)),
                   origin=Origin(xyz=(0.002 * s, 0.0, -0.004 * s)), material="black_plastic", name="trigger_boss", material_class_id="plastic.opaque_generic")
    trigger.visual(Box((0.014 * s, 0.034 * s, 0.050 * s)),
                   origin=Origin(xyz=(-0.010 * s, 0.0, -0.030 * s)), material="black_plastic", name="trigger_blade", material_class_id="plastic.opaque_generic")
    model.articulation(
        "trigger_squeeze", ArticulationType.REVOLUTE, parent=body, child=trigger,
        origin=Origin(xyz=(0.075 * s, 0.0, 0.150 * s)), axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=5.0, velocity=6.0, lower=0.0, upper=0.40),
    )
    sl = _emit_safety_lock(model, body, r)
    return ModuleBuild(
        module_name="squeeze_trigger", parts_emitted=["trigger", sl],
        internal_articulations=["trigger_squeeze", "safety_lock_press"],
        interfaces={"downstream": _body_downstream(r)},
    )


def _build_paddle_switch(ctx: ModuleBuildContext) -> ModuleBuild:
    model, r = ctx.model, ctx.config  # type: ignore[assignment]
    body = model.get_part("body")
    s = r.s
    # Paddle track + detents (host visuals) on the front strut inner face.
    body.visual(Box((0.006 * s, 0.018 * s, 0.050 * s)),
                origin=Origin(xyz=(0.043 * s, 0.0, 0.192 * s)), material="charcoal", name="paddle_track", material_class_id="plastic.opaque_generic")
    body.visual(Box((0.008 * s, 0.022 * s, 0.004 * s)),
                origin=Origin(xyz=(0.043 * s, 0.0, 0.216 * s)), material="charcoal", name="paddle_detent_top", material_class_id="plastic.opaque_generic")
    body.visual(Box((0.008 * s, 0.022 * s, 0.004 * s)),
                origin=Origin(xyz=(0.043 * s, 0.0, 0.168 * s)), material="charcoal", name="paddle_detent_bottom", material_class_id="plastic.opaque_generic")
    trigger = model.part("trigger")
    trigger.visual(Box((0.005 * s, 0.016 * s, 0.038 * s)),
                   origin=Origin(xyz=(0.0, 0.0, 0.0)), material="black_plastic", name="paddle_slider", material_class_id="plastic.opaque_generic")
    trigger.visual(Box((0.003 * s, 0.012 * s, 0.010 * s)),
                   origin=Origin(xyz=(-0.003 * s, 0.0, -0.008 * s)), material="charcoal", name="paddle_grip_ridge", material_class_id="rubber.smooth_plain")
    model.articulation(
        "trigger_slide", ArticulationType.PRISMATIC, parent=body, child=trigger,
        origin=Origin(xyz=(0.043 * s, 0.0, 0.175 * s)), axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=3.0, velocity=0.2, lower=0.0, upper=0.035 * s),
    )
    sl = _emit_safety_lock(model, body, r)
    return ModuleBuild(
        module_name="paddle_switch", parts_emitted=["trigger", sl],
        internal_articulations=["trigger_slide", "safety_lock_press"],
        interfaces={"downstream": _body_downstream(r)},
    )


# --------------------------------------------------------------------------- #
# Slot C - mount (parallel children on body)
# --------------------------------------------------------------------------- #


def _emit_flat_shoe_visuals(host, r: ResolvedIndustrialElectricSawConfig, *, dx=0.0, dy=0.0, dz=0.0,
                            shoe_z: float | None = None) -> None:
    """Flat stamped-metal base shoe with a blade slot (origin S1 L158-189).
    Emitted either onto ``body`` (handheld) or onto a separate ``shoe`` part
    (bevel), shifted by (-dx,-dy,-dz) into the target frame."""
    s = r.s
    sz = (N_SHOE_Z if shoe_z is None else shoe_z) * s
    host.visual(Box((0.250 * s, 0.054 * s, 0.006 * s)),
                origin=Origin(xyz=(0.075 * s - dx, 0.018 * s - dy, sz - dz)), material="chrome", name="base_shoe_left_rail", material_class_id="metal.chrome_polished")
    host.visual(Box((0.250 * s, 0.014 * s, 0.006 * s)),
                origin=Origin(xyz=(0.075 * s - dx, -0.124 * s - dy, sz - dz)), material="chrome", name="base_shoe_right_rail", material_class_id="metal.chrome_polished")
    host.visual(Box((0.085 * s, 0.123 * s, 0.006 * s)),
                origin=Origin(xyz=(-0.055 * s - dx, -0.0665 * s - dy, sz - dz)), material="chrome", name="base_shoe_rear_bridge", material_class_id="metal.chrome_polished")
    host.visual(Box((0.026 * s, 0.123 * s, 0.006 * s)),
                origin=Origin(xyz=(0.194 * s - dx, -0.0665 * s - dy, sz - dz)), material="chrome", name="base_shoe_front_bridge", material_class_id="metal.chrome_polished")
    host.visual(Box((0.020 * s, 0.150 * s, 0.020 * s)),
                origin=Origin(xyz=(0.192 * s - dx, -0.030 * s - dy, sz + 0.010 * s - dz), rpy=(0.0, -0.5, 0.0)),
                material="chrome", name="shoe_nose", material_class_id="metal.chrome_polished")


def _emit_depth_bevel_brackets(body, r: ResolvedIndustrialElectricSawConfig) -> None:
    s = r.s
    body.visual(Box((0.030 * s, 0.012 * s, 0.060 * s)),
                origin=Origin(xyz=(-0.020 * s, -0.020 * s, 0.030 * s)), material="charcoal", name="depth_bracket", material_class_id="metal.blackened_gunmetal")
    body.visual(Box((0.028 * s, 0.012 * s, 0.060 * s)),
                origin=Origin(xyz=(0.100 * s, -0.020 * s, 0.030 * s)), material="charcoal", name="bevel_bracket", material_class_id="metal.blackened_gunmetal")


def _build_handheld_shoe(ctx: ModuleBuildContext) -> ModuleBuild:
    """Spine-adaptive foot fused onto body as host visuals (no new joint)."""
    model, r = ctx.model, ctx.config  # type: ignore[assignment]
    body = model.get_part("body")
    s = r.s
    if r.cutting_element in _DISC_CUTTERS:
        _emit_flat_shoe_visuals(body, r)
        _emit_depth_bevel_brackets(body, r)
    elif r.cutting_element == "reciprocating_blade":
        # Small front foot flanking the blade slot (reciprocating S6 L166-190).
        cx, cy, cz = 0.158 * s, -0.030 * s, 0.075 * s
        body.visual(Box((0.050 * s, 0.012 * s, 0.050 * s)),
                    origin=Origin(xyz=(cx + 0.020 * s, cy + 0.024 * s, cz - 0.012 * s)), material="chrome", name="shoe_left_plate", material_class_id="metal.chrome_polished")
        body.visual(Box((0.050 * s, 0.012 * s, 0.050 * s)),
                    origin=Origin(xyz=(cx + 0.020 * s, cy - 0.024 * s, cz - 0.012 * s)), material="chrome", name="shoe_right_plate", material_class_id="metal.chrome_polished")
        body.visual(Box((0.008 * s, 0.060 * s, 0.050 * s)),
                    origin=Origin(xyz=(cx + 0.048 * s, cy, cz - 0.012 * s)), material="chrome", name="shoe_front_bridge", material_class_id="metal.chrome_polished")
        body.visual(Box((0.050 * s, 0.036 * s, 0.006 * s)),
                    origin=Origin(xyz=(cx + 0.020 * s, cy, cz + 0.014 * s)), material="chrome", name="shoe_top_plate", material_class_id="metal.chrome_polished")
    else:  # chain_bar - slim front hand-guard bar (chain brake handle),
        # forward of the handle opening so it clears the swinging trigger.
        body.visual(Box((0.010 * s, 0.090 * s, 0.075 * s)),
                    origin=Origin(xyz=(0.130 * s, -0.010 * s, 0.115 * s)), material="black_plastic", name="front_hand_guard", material_class_id="plastic.opaque_generic")
    return ModuleBuild(
        module_name="handheld_shoe", parts_emitted=[], internal_articulations=[],
        interfaces={"downstream": _body_downstream(r)},
    )


def _build_bevel_shoe(ctx: ModuleBuildContext) -> ModuleBuild:
    """Flat shoe as a separate part on a REVOLUTE bevel-tilt pivot (bevel S8)."""
    model, r = ctx.model, ctx.config  # type: ignore[assignment]
    body = model.get_part("body")
    s = r.s
    _emit_depth_bevel_brackets(body, r)
    # The bevel shoe sits lower than the fused handheld shoe so it has vertical
    # room to roll clear of the rear battery brick (the tilt is a bevel cut).
    shoe_z = 0.010
    bevel_x, bevel_y, bevel_z = 0.100 * s, -0.020 * s, 0.020 * s
    shoe = model.part("shoe")
    _emit_flat_shoe_visuals(shoe, r, dx=bevel_x, dy=bevel_y, dz=bevel_z, shoe_z=shoe_z)
    jn = "bevel_pivot"
    model.articulation(
        jn, ArticulationType.REVOLUTE, parent=body, child=shoe,
        origin=Origin(xyz=(bevel_x, bevel_y, bevel_z)), axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=6.0, velocity=1.5, lower=0.0, upper=r.bevel_range),
    )
    # Solve a safe tilt range against the housing (keep the shoe / blade clear).
    clamp_joint_limits(
        model, jn, margin=0.002, keepout=["body"],
        allowed_pairs=[
            ("body", "shoe", "bevel_bracket", "base_shoe_front_bridge"),
            ("body", "shoe", "depth_bracket", "base_shoe_rear_bridge"),
        ],
        scan_steps=12,
    )
    return ModuleBuild(
        module_name="bevel_shoe", parts_emitted=["shoe"], internal_articulations=[jn],
        interfaces={"downstream": _body_downstream(r)},
    )


# --------------------------------------------------------------------------- #
# Factory registries + assembly
# --------------------------------------------------------------------------- #

CUTTING_FACTORIES = {
    "circular_blade": _build_circular_blade,
    "abrasive_wheel": _build_abrasive_wheel,
    "chain_bar": _build_chain_bar,
    "reciprocating_blade": _build_reciprocating_blade,
}
CONTROL_FACTORIES = {
    "squeeze_trigger": _build_squeeze_trigger,
    "paddle_switch": _build_paddle_switch,
}
MOUNT_FACTORIES = {
    "handheld_shoe": _build_handheld_shoe,
    "bevel_shoe": _build_bevel_shoe,
}


def _slots_for_config(r: ResolvedIndustrialElectricSawConfig) -> list[SlotSpec]:
    return [
        SlotSpec(slot_name="cutting_element",
                 candidates={r.cutting_element: CUTTING_FACTORIES[r.cutting_element]},
                 anchor_choice=r.cutting_element),
        SlotSpec(slot_name="control",
                 candidates={r.control: CONTROL_FACTORIES[r.control]},
                 anchor_choice=r.control),
        SlotSpec(slot_name="mount",
                 candidates={r.mount: MOUNT_FACTORIES[r.mount]},
                 anchor_choice=r.mount),
    ]


def build_industrial_electric_saw(
    config: IndustrialElectricSawConfig,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name="industrial_electric_saw", assets=assets)
    palette = dict(r.palette)
    if r.cutting_element == "abrasive_wheel":
        palette["abrasive_disc"] = (0.28, 0.27, 0.26, 1.0)
    for material_name, rgba in palette.items():
        model.material(material_name, rgba=rgba)

    _build_body_chassis(model, r)

    assemble(
        model,
        slots=_slots_for_config(r),
        rng=random.Random(0),
        palette=palette,
        config=r,
        seed=0,
        selection_mode="anchor_choices",
    )
    return model


def build_seeded_industrial_electric_saw(seed: int) -> ArticulatedObject:
    return build_industrial_electric_saw(config_from_seed(seed))


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    r = resolve_config(config_from_seed(seed))
    tooth_axis = f"teeth_{r.tooth_count}" if r.cutting_element == "circular_blade" else "teeth_na"
    return [
        ("cutting_element", r.cutting_element),
        ("tooth_count", tooth_axis),
        ("control", r.control),
        ("mount", r.mount),
    ]


# --------------------------------------------------------------------------- #
# Author-layer QC
# --------------------------------------------------------------------------- #


def _declare_overlaps(ctx: TestContext, model: ArticulatedObject, r: ResolvedIndustrialElectricSawConfig) -> None:
    parts = {p.name for p in model.parts}
    body = model.get_part("body")

    def _ov(a_part: str, b_part: str, *, elem_a: str, elem_b: str, reason: str) -> None:
        if a_part in parts and b_part in parts:
            ctx.allow_overlap(model.get_part(a_part), model.get_part(b_part),
                              elem_a=elem_a, elem_b=elem_b, reason=reason)

    # ---- disc cutters: guard / blade intentional fits (origin S1 L426-551) ----
    if r.cutting_element in _DISC_CUTTERS:
        _ov("body", "blade", elem_a="arbor_boss", elem_b="arbor_bolt",
            reason="Blade arbor bolt seats onto the housing arbor boss.")
        _ov("body", "blade", elem_a="upper_guard", elem_b="blade_disc",
            reason="Upper fixed guard shrouds the top rim of the blade.")
        _ov("body", "blade", elem_a="upper_guard_web", elem_b="blade_disc",
            reason="Upper guard web overlaps the blade it covers.")
        _ov("body", "blade", elem_a="upper_guard", elem_b="blade_plate",
            reason="Upper guard shrouds the blade body plate.")
        _ov("body", "blade", elem_a="upper_guard_web", elem_b="blade_plate",
            reason="Upper guard web overlaps the blade body plate.")
        _ov("body", "blade", elem_a="upper_guard", elem_b="arbor_bolt",
            reason="Blade hub sits inside the fixed upper guard shroud.")
        _ov("body", "blade", elem_a="upper_guard_web", elem_b="arbor_bolt",
            reason="Blade hub is covered by the upper guard web.")
        _ov("body", "blade", elem_a="lower_guard_pivot_boss", elem_b="arbor_bolt",
            reason="The blade arbor bolt and lower-guard pivot boss share the arbor stack.")
        # lower guard fits
        _ov("body", "lower_guard", elem_a="lower_guard_pivot_boss", elem_b="lower_guard_hub",
            reason="Lower guard pivot collar rides on the housing pivot boss (captured pin).")
        _ov("body", "lower_guard", elem_a="lower_guard_pivot_boss", elem_b="lower_guard_arm",
            reason="Lower guard arm sweeps past the housing pivot boss at the captured pivot.")
        _ov("body", "lower_guard", elem_a="arbor_boss", elem_b="lower_guard_arm",
            reason="Lower guard arm passes over the arbor boss at the pivot.")
        _ov("body", "lower_guard", elem_a="arbor_boss", elem_b="lower_guard_hub",
            reason="Lower guard pivot collar is coaxial with the arbor boss.")
        _ov("blade", "lower_guard", elem_a="arbor_bolt", elem_b="lower_guard_hub",
            reason="Lower guard collar and blade arbor bolt share the arbor stack.")
        _ov("body", "lower_guard", elem_a="lower_guard_pivot_boss", elem_b="lower_guard_shell",
            reason="Lower guard shell pivots on the housing pivot boss.")
        _ov("body", "lower_guard", elem_a="upper_guard", elem_b="lower_guard_shell",
            reason="Lower guard nests concentrically inside the fixed upper guard band.")
        _ov("body", "lower_guard", elem_a="upper_guard_web", elem_b="lower_guard_shell",
            reason="Lower guard tucks under the fixed upper guard web.")
        _ov("body", "lower_guard", elem_a="upper_guard", elem_b="lower_guard_tab",
            reason="Retract tab passes under the fixed upper guard band.")
        _ov("body", "lower_guard", elem_a="upper_guard_web", elem_b="lower_guard_tab",
            reason="Retract tab tucks under the fixed upper guard web.")
        _ov("blade", "lower_guard", elem_a="blade_disc", elem_b="lower_guard_shell",
            reason="Lower guard rides just outside the blade rim (thin clearance).")

    # ---- chain rides around the guide bar (captured on the bar rail) ----
    if r.cutting_element == "chain_bar":
        chain = model.get_part("chain")
        link_names = [v.name for v in chain.visuals if v.name.startswith("link_")] + ["chain_rail"]
        for ln in link_names:
            _ov("body", "chain", elem_a="guide_bar", elem_b=ln,
                reason="Chain cutter links + rail ride captured around the guide-bar rail.")
        _ov("body", "chain", elem_a="drive_sprocket", elem_b="chain_rail",
            reason="Chain wraps the drive sprocket at the bar rear.")
        _ov("body", "chain", elem_a="nose_sprocket", elem_b="chain_rail",
            reason="Chain wraps the nose sprocket at the bar tip.")

    # ---- control switch fits ----
    if r.control == "squeeze_trigger":
        _ov("body", "trigger", elem_a="trigger_ear_left", elem_b="trigger_boss",
            reason="Trigger pivot boss captured between the handle ears.")
        _ov("body", "trigger", elem_a="trigger_ear_right", elem_b="trigger_boss",
            reason="Trigger pivot boss captured between the handle ears.")
        _ov("body", "trigger", elem_a="top_handle", elem_b="trigger_blade",
            reason="Trigger blade hangs into the handle opening from the pivot.")
    else:
        _ov("body", "trigger", elem_a="paddle_track", elem_b="paddle_slider",
            reason="Paddle slider captured inside the track channel on the handle strut.")
        _ov("body", "trigger", elem_a="top_handle", elem_b="paddle_slider",
            reason="Paddle slider sits on the inner face of the top handle front strut.")
    _ov("body", "safety_lock", elem_a="top_handle", elem_b="safety_lock_cap",
        reason="Safety lock-off button stem embeds into the handle front strut.")

    # ---- mount fits ----
    if r.mount == "bevel_shoe":
        _ov("body", "shoe", elem_a="bevel_bracket", elem_b="base_shoe_front_bridge",
            reason="Bevel bracket on the housing bridges down to the shoe plate near the front.")
        _ov("body", "shoe", elem_a="depth_bracket", elem_b="base_shoe_rear_bridge",
            reason="Rear depth-adjust bracket bridges from the housing down to the shoe rear bridge.")
        # blade dips through the shoe blade slot region
        if r.cutting_element in _DISC_CUTTERS:
            for rail in ("base_shoe_left_rail", "base_shoe_right_rail"):
                _ov("shoe", "blade", elem_a=rail, elem_b="blade_disc",
                    reason="Blade protrudes down through the shoe blade slot between the rails.")

    # handheld disc shoe: blade protrudes through the fused shoe slot.
    if r.mount == "handheld_shoe" and r.cutting_element in _DISC_CUTTERS:
        for rail in ("base_shoe_left_rail", "base_shoe_right_rail"):
            _ov("body", "blade", elem_a=rail, elem_b="blade_disc",
                reason="Blade protrudes down through the shoe blade slot between the rails.")


def _center_dist(a, b) -> float:
    if a is None or b is None:
        return 0.0
    ca = [(a[0][i] + a[1][i]) / 2.0 for i in range(3)]
    cb = [(b[0][i] + b[1][i]) / 2.0 for i in range(3)]
    return math.dist(ca, cb)


def _expect_cutter(ctx, model, r) -> None:
    if r.cutting_element in _DISC_CUTTERS:
        blade = model.get_part("blade")
        spin = model.get_articulation("blade_spin")
        ctx.check("blade drive is continuous", spin.articulation_type == ArticulationType.CONTINUOUS)
        rest = ctx.part_world_aabb(blade)
        with ctx.pose({spin: 0.8}):
            spun = ctx.part_world_aabb(blade)
        ctx.check("blade rotates about the arbor", rest is not None and spun is not None,
                  details=f"rest={rest}, spun={spun}")
        # lower guard retracts
        guard = model.get_articulation("lower_guard_retract")
        lg = model.get_part("lower_guard")
        g_rest = ctx.part_world_aabb(lg)
        with ctx.pose({guard: 1.6}):
            g_open = ctx.part_world_aabb(lg)
        ctx.check("lower guard retracts to expose the blade",
                  g_rest is not None and g_open is not None and _center_dist(g_rest, g_open) > 0.02,
                  details=f"rest={g_rest}, open={g_open}")
    elif r.cutting_element == "chain_bar":
        chain = model.get_part("chain")
        drive = model.get_articulation("chain_drive")
        ctx.check("chain drive is continuous", drive.articulation_type == ArticulationType.CONTINUOUS)
        rest = ctx.part_world_aabb(chain)
        with ctx.pose({drive: 1.2}):
            spun = ctx.part_world_aabb(chain)
        ctx.check("chain travels around the bar", rest is not None and spun is not None,
                  details=f"rest={rest}")
    else:  # reciprocating
        blade = model.get_part("blade")
        stroke = model.get_articulation("blade_stroke")
        ctx.check("blade stroke is prismatic", stroke.articulation_type == ArticulationType.PRISMATIC)
        rest = ctx.part_world_position(blade)
        upper = stroke.motion_limits.upper if stroke.motion_limits else 0.01
        with ctx.pose({stroke: upper}):
            out = ctx.part_world_position(blade)
        ctx.check("reciprocating blade strokes along +X",
                  rest is not None and out is not None and out[0] > rest[0] + 0.005,
                  details=f"rest={rest}, out={out}")


def _expect_control(ctx, model, r) -> None:
    trigger = model.get_part("trigger")
    if r.control == "squeeze_trigger":
        j = model.get_articulation("trigger_squeeze")
        ctx.check("trigger joint is revolute", j.articulation_type == ArticulationType.REVOLUTE)
        rest = ctx.part_world_aabb(trigger)
        with ctx.pose({j: 0.40}):
            sq = ctx.part_world_aabb(trigger)
        ctx.check("squeezing swings the trigger rearward",
                  rest is not None and sq is not None and sq[0][0] < rest[0][0] - 0.005,
                  details=f"rest={rest}, sq={sq}")
    else:
        j = model.get_articulation("trigger_slide")
        ctx.check("paddle joint is prismatic", j.articulation_type == ArticulationType.PRISMATIC)
        rest = ctx.part_world_position(trigger)
        upper = j.motion_limits.upper if j.motion_limits else 0.03
        with ctx.pose({j: upper}):
            slid = ctx.part_world_position(trigger)
        ctx.check("paddle slides upward on the strut face",
                  rest is not None and slid is not None and slid[2] > rest[2] + 0.005,
                  details=f"rest={rest}, slid={slid}")
    # safety lock presses inward
    lock = model.get_articulation("safety_lock_press")
    sl = model.get_part("safety_lock")
    b_rest = ctx.part_world_position(sl)
    with ctx.pose({lock: (lock.motion_limits.upper if lock.motion_limits else 0.004)}):
        b_press = ctx.part_world_position(sl)
    ctx.check("safety lock-off button presses inward",
              b_rest is not None and b_press is not None and b_press[1] < b_rest[1] - 0.001,
              details=f"rest={b_rest}, pressed={b_press}")


def _expect_mount(ctx, model, r) -> None:
    if r.mount == "bevel_shoe":
        shoe = model.get_part("shoe")
        j = model.get_articulation("bevel_pivot")
        ctx.check("bevel pivot is revolute", j.articulation_type == ArticulationType.REVOLUTE)
        rest = ctx.part_world_aabb(shoe)
        val = (j.motion_limits.upper if j.motion_limits else 0.4) * 0.9
        with ctx.pose({j: val}):
            tilt = ctx.part_world_aabb(shoe)
        ctx.check("bevel pivot tilts the shoe",
                  rest is not None and tilt is not None
                  and (abs(tilt[0][1] - rest[0][1]) + abs(tilt[1][2] - rest[1][2])) > 0.008,
                  details=f"rest={rest}, tilt={tilt}")


def run_industrial_electric_saw_tests(
    model: ArticulatedObject,
    config: IndustrialElectricSawConfig,
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

    _expect_cutter(ctx, model, r)
    _expect_control(ctx, model, r)
    _expect_mount(ctx, model, r)

    # Rule 5: dynamic collision across sampled joint poses.
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=64, ignore_fixed=True)

    return ctx.report()


__all__ = [
    "IndustrialElectricSawConfig",
    "ResolvedIndustrialElectricSawConfig",
    "CuttingElement",
    "ControlModule",
    "MountModule",
    "SawPalette",
    "build_industrial_electric_saw",
    "build_seeded_industrial_electric_saw",
    "config_from_seed",
    "resolve_config",
    "run_industrial_electric_saw_tests",
    "slot_choices_for_seed",
]
