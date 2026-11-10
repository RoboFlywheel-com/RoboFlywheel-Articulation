# SPDX-License-Identifier: Apache-2.0

"""Graduated protractor plate carrying N swing arms and one pivot-axis lock.

Design-backed rebuild of `protractor_with_swing_arm`
(`articraft_template_authoring/designs/protractor_with_swing_arm.json`,
SourceMap `.../source_maps/protractor_with_swing_arm.md`).

Frame convention taken from the SourceMap: the plate lies in XY, ``+Z`` is up and
is the rotation axis of *every* joint in the category, ``z=0`` is the plate
underside, and the plate's marked face is its ``+Z`` face.  The arm's local ``+X``
is its measuring edge, so world arm angle 0 points along ``+X`` and the graduated
material spans ``[0, body_angular_span_rad]`` counter-clockwise from ``+X``.

Deliberate departures from a source construction (each justified in place):

* Graduations are CUT into the single CAD solid of their host part (record 001
  L66-L86 / L75-L78 / L81-L86), not emitted as record 003's 108 separate ``Box``
  visuals.  ``sdk/_core/v0/exact_collisions.py`` derives one collision solid per
  visual and then splits each mesh into connected components, so 003's route turns
  a decorative scale into ~116 collision bodies AND record 002's welded ink layer
  into that many geometry islands.  001's cut route keeps one visual per part with
  the same visible detail.
* ``full_circle_annulus`` gains four slender radial spokes between the bearing boss
  and the ring.  Its source (var_body_form_full_circle L38-L66) inherits 002's
  boss but drops 002's rail, which leaves the boss floating in mid-air; a bearing
  that carries the whole arm stack cannot be an unsupported island.  This is the
  local transition geometry the candidate needs, nothing more.
* The double-ended blade profile (003 L49-L62) is authored along ``+X`` instead of
  ``+Y`` so every arm candidate shares one angular convention.  Pure frame choice;
  the outline, its point count and all proportions are the source's.
* Part-to-part seats carry a deliberate ``_CONTACT_EMBED`` (0.2 mm) overlap rather
  than the source's exact tangency, because CadQuery/triangulated tangency is not
  reliable at the 1e-6 contact tolerance.  0.2 mm stays far below both
  ``find_geometry_overlaps`` tolerances (1e-3 / 5e-3).
* The 003-family running clearance is NOT closed: `body_bearing_kind` keeps both
  branches and the arm rides a real air gap over those plates.
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
    MotionLimits,
    PlaneInterface,
    TemplateDomain,
    TestContext,
    TestReport,
    component_slot,
    corner_case,
    mate_axes,
    mate_planes,
    mesh_from_cadquery,
    multiplicity_slot,
    register_interface_mate,
)

BodyForm = Literal[
    "semicircular_solid_plate",
    "semicircular_arch_rail",
    "full_circle_annulus",
    "full_circle_solid_plate",
    "quadrant_sector",
]
ArmForm = Literal[
    "tapered_rule_pointer_tail",
    "pointed_strip",
    "double_ended_blade",
    "vernier_plate_arm",
]
LockModule = Literal[
    "knurled_clamp_screw",
    "slotted_screw",
    "capstan_screw_retainer",
    "cam_lever",
]

BODY_FORMS: tuple[BodyForm, ...] = (
    "semicircular_solid_plate",
    "semicircular_arch_rail",
    "full_circle_annulus",
    "full_circle_solid_plate",
    "quadrant_sector",
)
ARM_FORMS: tuple[ArmForm, ...] = (
    "tapered_rule_pointer_tail",
    "pointed_strip",
    "double_ended_blade",
    "vernier_plate_arm",
)
LOCK_MODULES: tuple[LockModule, ...] = (
    "knurled_clamp_screw",
    "slotted_screw",
    "capstan_screw_retainer",
    "cam_lever",
)
ARM_COUNTS: tuple[int, ...] = (1, 2, 3, 4, 5)

TEMPLATE_DOMAIN = TemplateDomain(
    slots=(
        component_slot("body_form", BODY_FORMS, role="graduated host plate"),
        component_slot("arm_form", ARM_FORMS, role="swing measuring arm"),
        component_slot("lock_module", LOCK_MODULES, role="pivot-axis locking fastener"),
        multiplicity_slot(
            "arm_count",
            ARM_COUNTS,
            role="stacked swing arms on one shared pivot",
            item_slot="arm_form",
        ),
    )
)

# --- construction constants ---------------------------------------------------
# Intra-part weld: features union into their host with this embed so a part never
# reports a disconnected geometry island at contact_tol=1e-6.  Free, because
# collisions are computed only between parts (source 003 L39 uses -0.00005 for
# exactly this reason when welding the scale rim onto the plate).
_WELD = 0.00005
# Part-to-part seating overlap.  Sized against find_geometry_overlaps' 1e-3
# default (and default_overlap_tol_from_env()'s 5e-3), never against tangency.
_CONTACT_EMBED = 0.00020
# Graduations are cut as shallow grooves into the host solid (001 L66-L86).  The
# cutter is raised `_INK_PROUD` above the marked face so the groove floor is a
# clean `_INK_T - _INK_PROUD` deep and no sliver face is left behind.
_INK_T = 0.00022
_INK_PROUD = 0.00004
_ARC_SEGMENTS = 48


# --- candidate parameter domains (mirrors the TemplateDesign) -----------------
_BODY_RANGES: dict[str, dict[str, tuple[float, float]]] = {
    "semicircular_solid_plate": {
        "body_radius_m": (0.052, 0.086),
        "body_thickness_m": (0.0013, 0.0034),
        "body_bore_r_m": (0.0026, 0.0052),
        "rule_length_m": (0.19, 0.33),
        "rule_width_m": (0.012, 0.024),
        "pivot_boss_h_m": (0.00015, 0.0008),
    },
    "semicircular_arch_rail": {
        "body_radius_m": (0.052, 0.086),
        "body_thickness_m": (0.0013, 0.0034),
        "body_bore_r_m": (0.0026, 0.0052),
        "arch_inner_ratio": (0.58, 0.80),
        "rail_length_ratio": (0.95, 1.15),
        "pivot_boss_h_m": (0.00025, 0.0009),
    },
    "full_circle_annulus": {
        "body_radius_m": (0.052, 0.086),
        "body_thickness_m": (0.0013, 0.0034),
        "body_bore_r_m": (0.0026, 0.0052),
        "annulus_inner_ratio": (0.55, 0.82),
        "pivot_boss_h_m": (0.00025, 0.0009),
    },
    "full_circle_solid_plate": {
        "body_radius_m": (0.052, 0.086),
        "body_thickness_m": (0.0013, 0.0034),
        "body_bore_r_m": (0.0026, 0.0052),
        "rim_width_ratio": (0.66, 0.88),
        "rim_height_m": (0.0002, 0.0009),
        "arm_running_gap_m": (0.00004, 0.00024),
    },
    "quadrant_sector": {
        "body_radius_m": (0.052, 0.086),
        "body_thickness_m": (0.0013, 0.0034),
        "body_bore_r_m": (0.0026, 0.0052),
        "sector_span_rad": (1.0472, 1.5708),
        "rim_width_ratio": (0.66, 0.88),
        "rim_height_m": (0.0002, 0.0009),
        "arm_running_gap_m": (0.00004, 0.00024),
    },
}

_ARM_RANGES: dict[str, dict[str, tuple[float, float]]] = {
    "tapered_rule_pointer_tail": {
        "arm_thickness_m": (0.0015, 0.0033),
        "arm_bore_r_m": (0.0026, 0.0054),
        "arm_hub_r_m": (0.0095, 0.0155),
        "blade_length_m": (0.15, 0.29),
        "pointer_tail_length_m": (0.012, 0.04),
    },
    "pointed_strip": {
        "arm_thickness_m": (0.0015, 0.0033),
        "arm_bore_r_m": (0.0026, 0.0054),
        "arm_hub_r_m": (0.0095, 0.0155),
        "blade_length_m": (0.075, 0.15),
        "strip_half_width_m": (0.0035, 0.008),
    },
    "double_ended_blade": {
        "arm_thickness_m": (0.0015, 0.0033),
        "arm_bore_r_m": (0.0026, 0.0054),
        "arm_hub_r_m": (0.0095, 0.0155),
        "upper_ruler_length_m": (0.068, 0.14),
        "pointer_length_m": (0.05, 0.105),
        "arm_boss_h_m": (0.00045, 0.0015),
    },
    "vernier_plate_arm": {
        "arm_thickness_m": (0.0015, 0.0033),
        "arm_bore_r_m": (0.0026, 0.0054),
        "arm_hub_r_m": (0.0095, 0.0155),
        "blade_length_m": (0.075, 0.15),
        "vernier_plate_half_width_m": (0.0095, 0.018),
    },
}

_LOCK_RANGES: dict[str, dict[str, tuple[float, float]]] = {
    "knurled_clamp_screw": {
        "grip_r_m": (0.0068, 0.012),
        "grip_h_m": (0.0055, 0.0125),
        "turn_range_rad": (6.2832, 14.1372),
    },
    "slotted_screw": {
        "head_r_m": (0.0045, 0.009),
        "head_h_m": (0.0016, 0.0042),
        "slot_width_m": (0.0008, 0.002),
        "turn_range_rad": (1.5708, 6.2832),
    },
    "capstan_screw_retainer": {
        "cap_r_m": (0.0072, 0.0135),
        "retainer_r_m": (0.0048, 0.009),
        "retainer_h_m": (0.0006, 0.0018),
        "turn_range_rad": (1.5708, 6.2832),
    },
    "cam_lever": {
        "cam_eccentricity_m": (0.001, 0.0032),
        "cam_lobe_r_m": (0.0052, 0.0098),
        "lever_handle_length_m": (0.016, 0.04),
        "turn_range_rad": (1.5708, 6.2832),
    },
}

_ARM_CHOICES: dict[str, dict[str, tuple[int, ...]]] = {
    "vernier_plate_arm": {"vernier_division_count": (9, 11, 13)},
}
_LOCK_CHOICES: dict[str, dict[str, tuple[int, ...]]] = {
    "knurled_clamp_screw": {"knurl_rib_count": (24, 32, 40)},
}


def _mid(bounds: tuple[float, float]) -> float:
    return 0.5 * (bounds[0] + bounds[1])


@dataclass(frozen=True)
class Config:
    body_form: BodyForm = "semicircular_solid_plate"
    arm_form: ArmForm = "tapered_rule_pointer_tail"
    lock_module: LockModule = "knurled_clamp_screw"
    arm_count: int = 1

    # body_form independents
    body_radius_m: float = 0.060
    body_thickness_m: float = 0.0022
    body_bore_r_m: float = 0.0047
    rule_length_m: float = 0.304
    rule_width_m: float = 0.018
    pivot_boss_h_m: float = 0.0005
    arch_inner_ratio: float = 0.692
    rail_length_ratio: float = 1.064
    annulus_inner_ratio: float = 0.692
    rim_width_ratio: float = 0.760
    rim_height_m: float = 0.0004
    arm_running_gap_m: float = 0.00015
    sector_span_rad: float = 1.5708

    # arm_form independents
    arm_thickness_m: float = 0.0023
    arm_bore_r_m: float = 0.0049
    arm_hub_r_m: float = 0.0125
    blade_length_m: float = 0.260
    pointer_tail_length_m: float = 0.025
    strip_half_width_m: float = 0.0052
    upper_ruler_length_m: float = 0.068
    pointer_length_m: float = 0.080
    arm_boss_h_m: float = 0.00090
    vernier_plate_half_width_m: float = 0.0130
    vernier_division_count: int = 11

    # lock_module independents
    knurl_rib_count: int = 32
    grip_r_m: float = 0.0094
    grip_h_m: float = 0.0085
    turn_range_rad: float = 4.0 * math.pi
    head_r_m: float = 0.0062
    head_h_m: float = 0.0024
    slot_width_m: float = 0.0012
    cap_r_m: float = 0.0100
    retainer_r_m: float = 0.0063
    retainer_h_m: float = 0.0009
    cam_eccentricity_m: float = 0.0018
    cam_lobe_r_m: float = 0.0070
    lever_handle_length_m: float = 0.026

    name: str = "protractor_with_swing_arm"


@dataclass(frozen=True)
class ResolvedConfig:
    body_form: BodyForm
    arm_form: ArmForm
    lock_module: LockModule
    arm_count: int

    body_radius_m: float
    body_thickness_m: float
    body_bore_r_m: float
    rule_length_m: float
    rule_width_m: float
    pivot_boss_h_m: float
    arch_inner_ratio: float
    rail_length_ratio: float
    annulus_inner_ratio: float
    rim_width_ratio: float
    rim_height_m: float
    arm_running_gap_m: float
    sector_span_rad: float

    arm_thickness_m: float
    arm_bore_r_m: float
    arm_hub_r_m: float
    blade_length_m: float
    pointer_tail_length_m: float
    strip_half_width_m: float
    upper_ruler_length_m: float
    pointer_length_m: float
    arm_boss_h_m: float
    vernier_plate_half_width_m: float
    vernier_division_count: int

    knurl_rib_count: int
    grip_r_m: float
    grip_h_m: float
    turn_range_rad: float
    head_r_m: float
    head_h_m: float
    slot_width_m: float
    cap_r_m: float
    retainer_r_m: float
    retainer_h_m: float
    cam_eccentricity_m: float
    cam_lobe_r_m: float
    lever_handle_length_m: float

    # --- binding plate_bearing_to_arm_seat -----------------------------------
    body_bearing_kind: str = "thrust_boss"
    body_top_z_m: float = 0.0
    arm_z_lo_m: float = 0.0
    arm_seat_z_m: float = 0.0
    arm_hub_top_z_m: float = 0.0

    # --- binding body_span_to_arm_range --------------------------------------
    body_angular_span_rad: float = math.pi
    arm_swing_lower_rad: float = 0.0
    arm_swing_upper_rad: float = math.pi
    outer_tick_count: int = 37

    # --- binding arm_stack_to_lock_seat --------------------------------------
    arm_stack_height_m: float = 0.0
    top_arm_z_m: float = 0.0
    lock_seat_z_m: float = 0.0
    lock_shaft_r_m: float = 0.0
    lock_seat_r_m: float = 0.0
    retainer_top_z_m: float = 0.0
    hub_relief_required: str = "no"
    lock_joint_parent_role: str = "graduated_plate"

    arm_rest_angles_rad: tuple[float, ...] = ()
    name: str = "protractor_with_swing_arm"


def _clamp_to_range(value: float, bounds: tuple[float, float]) -> float:
    return min(max(float(value), bounds[0]), bounds[1])


def _require_choice(name: str, value: int, choices: tuple[int, ...]) -> int:
    value = int(value)
    if value not in choices:
        raise ValueError(f"{name} must be one of {choices}, got {value}")
    return value


def config_from_seed(seed: int) -> Config:
    choices = TEMPLATE_DOMAIN.sample(seed)
    rng = random.Random(int(seed) ^ 0x5052_4F54_5241_4354)
    body = choices["body_form"]
    arm = choices["arm_form"]
    lock = choices["lock_module"]

    values: dict[str, object] = {}
    for table, candidate in (
        (_BODY_RANGES, body),
        (_ARM_RANGES, arm),
        (_LOCK_RANGES, lock),
    ):
        for key, bounds in table[candidate].items():
            values[key] = round(rng.uniform(bounds[0], bounds[1]), 6)
    for table, candidate in ((_ARM_CHOICES, arm), (_LOCK_CHOICES, lock)):
        for key, options in table.get(candidate, {}).items():
            values[key] = rng.choice(options)

    return Config(
        body_form=body,
        arm_form=arm,
        lock_module=lock,
        arm_count=choices["arm_count"],
        name=f"protractor_with_swing_arm_seed_{seed}",
        **values,  # type: ignore[arg-type]
    )


def slot_choices_for_config(config: Config | ResolvedConfig) -> tuple[tuple[str, object], ...]:
    return (
        ("body_form", config.body_form),
        ("arm_form", config.arm_form),
        ("lock_module", config.lock_module),
        ("arm_count", config.arm_count),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, object], ...]:
    return slot_choices_for_config(config_from_seed(seed))


def resolve_config(config: Config) -> ResolvedConfig:
    TEMPLATE_DOMAIN.validate(
        {
            "body_form": config.body_form,
            "arm_form": config.arm_form,
            "lock_module": config.lock_module,
            "arm_count": config.arm_count,
        }
    )
    # Only the ACTIVE candidate's independents are re-derived; the other
    # candidates' Config fields are inert for this combination.  Production
    # applies discrete overrides as a RAW dataclasses.replace with no
    # re-resolution, so a field the seed sampled for its own candidate can
    # arrive outside the overridden candidate's declared range (e.g.
    # turn_range_rad sampled for a single-turn lock under a knurled_clamp_screw
    # override).  Reconcile by clamping to the nearest declared bound instead
    # of rejecting the config.
    resolved: dict[str, float] = {}
    for table, candidate in (
        (_BODY_RANGES, config.body_form),
        (_ARM_RANGES, config.arm_form),
        (_LOCK_RANGES, config.lock_module),
    ):
        for key, bounds in table[candidate].items():
            resolved[key] = _clamp_to_range(getattr(config, key), bounds)

    def val(key: str) -> float:
        return resolved.get(key, float(getattr(config, key)))

    for table, candidate in ((_ARM_CHOICES, config.arm_form), (_LOCK_CHOICES, config.lock_module)):
        for key, options in table.get(candidate, {}).items():
            _require_choice(key, getattr(config, key), options)

    body = config.body_form
    arm = config.arm_form
    lock = config.lock_module
    n = int(config.arm_count)

    # binding plate_bearing_to_arm_seat -------------------------------------
    # Which bearing the plate candidate builds (SourceMap mating rule 1).
    body_bearing_kind = (
        "running_clearance"
        if body in ("full_circle_solid_plate", "quadrant_sector")
        else "thrust_boss"
    )
    rim_height_m = val("rim_height_m") if body in ("full_circle_solid_plate", "quadrant_sector") else 0.0
    body_top_z_m = val("body_thickness_m") + rim_height_m
    pivot_boss_h_m = val("pivot_boss_h_m") if body_bearing_kind == "thrust_boss" else 0.0
    arm_running_gap_m = val("arm_running_gap_m") if body_bearing_kind == "running_clearance" else 0.0

    # Frame of the arm solid.  Records 001 (L102) and 002 (L146) extrude the
    # blade from its underside (0..t) and seat it on the thrust boss; record 003
    # (L68) extrudes `both=True` about the arm origin and rides a clearance.  The
    # Z-frame is therefore a function of the bearing, exactly as the Design's
    # arm_seat_z_m branch assumes.
    arm_z_lo_m = 0.0 if body_bearing_kind == "thrust_boss" else -0.5 * val("arm_thickness_m")

    # The seat plane is SOLVED from the two declared plane interfaces rather than
    # authored twice (SourceMap mating rule 3).
    plate_marked_face = PlaneInterface(
        name=f"body_form__{body}__plate_marked_face",
        point=(0.0, 0.0, body_top_z_m),
        normal=(0.0, 0.0, 1.0),
        tangent_u=(1.0, 0.0, 0.0),
    )
    arm_underside = PlaneInterface(
        name=f"arm_form__{arm}__arm_underside",
        point=(0.0, 0.0, arm_z_lo_m),
        normal=(0.0, 0.0, -1.0),
        tangent_u=(1.0, 0.0, 0.0),
    )
    seat_gap = pivot_boss_h_m if body_bearing_kind == "thrust_boss" else arm_running_gap_m
    arm_seat_z_m = float(mate_planes(plate_marked_face, arm_underside, gap=seat_gap).origin.xyz[2])

    # Top of the topmost arm's material in its own frame.  double_ended_blade
    # carries its own boss (003 L70-L76) because its body side has none.
    arm_top_local = arm_z_lo_m + val("arm_thickness_m")
    arm_boss_h_m = val("arm_boss_h_m") if arm == "double_ended_blade" else 0.0
    arm_hub_top_z_m = arm_top_local + arm_boss_h_m

    # binding body_span_to_arm_range ----------------------------------------
    if body == "quadrant_sector":
        body_angular_span_rad = val("sector_span_rad")
    elif body in ("full_circle_annulus", "full_circle_solid_plate"):
        body_angular_span_rad = 2.0 * math.pi
    else:
        body_angular_span_rad = math.pi
    arm_swing_lower_rad = 0.0
    arm_swing_upper_rad = min(body_angular_span_rad, 2.0 * math.pi)
    outer_tick_count = int(round(math.degrees(body_angular_span_rad) / 5.0)) + 1

    # binding arm_stack_to_lock_seat ----------------------------------------
    arm_stack_height_m = n * val("arm_thickness_m")
    top_arm_z_m = arm_seat_z_m + (n - 1) * val("arm_thickness_m")
    arm_top_plane = PlaneInterface(
        name=f"arm_form__{arm}__arm_lock_seat",
        point=(0.0, 0.0, arm_hub_top_z_m),
        normal=(0.0, 0.0, 1.0),
        tangent_u=(1.0, 0.0, 0.0),
    )
    lock_underside = PlaneInterface(
        name=f"lock_module__{lock}__lock_underside",
        point=(0.0, 0.0, 0.0),
        normal=(0.0, 0.0, -1.0),
        tangent_u=(1.0, 0.0, 0.0),
    )
    lock_seat_z_m = top_arm_z_m + float(
        mate_planes(arm_top_plane, lock_underside, gap=0.0).origin.xyz[2]
    )
    lock_shaft_r_m = min(val("body_bore_r_m"), val("arm_bore_r_m")) - 0.0009
    lock_seat_r_m = min(val("arm_hub_r_m"), lock_shaft_r_m + 0.0060)
    retainer_top_z_m = -lock_seat_z_m
    hub_relief_required = "yes" if lock == "cam_lever" else "no"
    lock_joint_parent_role = (
        "graduated_plate" if lock == "knurled_clamp_screw" else "top_swing_arm"
    )

    # Rest angles are spread evenly across the plate's angular span
    # (var_arm_count_dual_arms L24-L26 generalised); every arm keeps the same
    # WORLD travel [arm_swing_lower_rad, arm_swing_upper_rad], which is what the
    # per-arm joint limits lower=-rest, upper=span-rest express (001 L253-L254,
    # var_arm_count_dual_arms L253-L254).
    arm_rest_angles_rad = tuple(
        arm_swing_lower_rad + (arm_swing_upper_rad - arm_swing_lower_rad) * (i + 1) / (n + 1)
        for i in range(n)
    )

    return ResolvedConfig(
        body_form=body,
        arm_form=arm,
        lock_module=lock,
        arm_count=n,
        body_radius_m=val("body_radius_m"),
        body_thickness_m=val("body_thickness_m"),
        body_bore_r_m=val("body_bore_r_m"),
        rule_length_m=val("rule_length_m"),
        rule_width_m=val("rule_width_m"),
        pivot_boss_h_m=pivot_boss_h_m,
        arch_inner_ratio=val("arch_inner_ratio"),
        rail_length_ratio=val("rail_length_ratio"),
        annulus_inner_ratio=val("annulus_inner_ratio"),
        rim_width_ratio=val("rim_width_ratio"),
        rim_height_m=rim_height_m,
        arm_running_gap_m=arm_running_gap_m,
        sector_span_rad=val("sector_span_rad"),
        arm_thickness_m=val("arm_thickness_m"),
        arm_bore_r_m=val("arm_bore_r_m"),
        arm_hub_r_m=val("arm_hub_r_m"),
        blade_length_m=val("blade_length_m"),
        pointer_tail_length_m=val("pointer_tail_length_m"),
        strip_half_width_m=val("strip_half_width_m"),
        upper_ruler_length_m=val("upper_ruler_length_m"),
        pointer_length_m=val("pointer_length_m"),
        arm_boss_h_m=arm_boss_h_m,
        vernier_plate_half_width_m=val("vernier_plate_half_width_m"),
        vernier_division_count=int(config.vernier_division_count),
        knurl_rib_count=int(config.knurl_rib_count),
        grip_r_m=val("grip_r_m"),
        grip_h_m=val("grip_h_m"),
        turn_range_rad=val("turn_range_rad"),
        head_r_m=val("head_r_m"),
        head_h_m=val("head_h_m"),
        slot_width_m=val("slot_width_m"),
        cap_r_m=val("cap_r_m"),
        retainer_r_m=val("retainer_r_m"),
        retainer_h_m=val("retainer_h_m"),
        cam_eccentricity_m=val("cam_eccentricity_m"),
        cam_lobe_r_m=val("cam_lobe_r_m"),
        lever_handle_length_m=val("lever_handle_length_m"),
        body_bearing_kind=body_bearing_kind,
        body_top_z_m=body_top_z_m,
        arm_z_lo_m=arm_z_lo_m,
        arm_seat_z_m=arm_seat_z_m,
        arm_hub_top_z_m=arm_hub_top_z_m,
        body_angular_span_rad=body_angular_span_rad,
        arm_swing_lower_rad=arm_swing_lower_rad,
        arm_swing_upper_rad=arm_swing_upper_rad,
        outer_tick_count=outer_tick_count,
        arm_stack_height_m=arm_stack_height_m,
        top_arm_z_m=top_arm_z_m,
        lock_seat_z_m=lock_seat_z_m,
        lock_shaft_r_m=lock_shaft_r_m,
        lock_seat_r_m=lock_seat_r_m,
        retainer_top_z_m=retainer_top_z_m,
        hub_relief_required=hub_relief_required,
        lock_joint_parent_role=lock_joint_parent_role,
        arm_rest_angles_rad=arm_rest_angles_rad,
        name=config.name,
    )


# --- shared CAD helpers -------------------------------------------------------
def _compound(solids: list[cq.Shape]) -> cq.Workplane:
    return cq.Workplane("XY").newObject([cq.Compound.makeCompound(solids)])


def _sector_disc(radius: float, span: float, z0: float, height: float) -> cq.Workplane:
    """Solid angular sector from angle 0 to `span`, faceted like source 002's
    `_semidisk` (L29-L35)."""
    if span >= 2.0 * math.pi - 1e-9:
        return cq.Workplane("XY", origin=(0.0, 0.0, z0)).circle(radius).extrude(height)
    points = [(0.0, 0.0)]
    for index in range(_ARC_SEGMENTS + 1):
        angle = span * index / _ARC_SEGMENTS
        points.append((radius * math.cos(angle), radius * math.sin(angle)))
    return cq.Workplane("XY", origin=(0.0, 0.0, z0)).polyline(points).close().extrude(height)


def _tick_edge_inset(*, tick_width: float, r_outer: float, span: float) -> float:
    """Angular keep-out at each end of a graduated span.

    A graduation groove that a straight radial plate edge bisects lengthwise is
    a degenerate boolean: OCC either grinds on the coincident faces (seed 29's
    quadrant cut did not finish in 600 s) or severs picometre-scale slivers off
    the plate, which then read as disconnected geometry islands.  Backing the
    first and last groove off by rather more than half their own width keeps
    every groove wholly inside the material.  The declared graduation COUNT is
    untouched; only where the end marks sit moves.
    """
    if span <= 0.0 or r_outer <= 0.0:
        return 0.0
    return min(span * 0.05, (tick_width * 1.5 + 0.0004) / r_outer)


def _arc_band(
    r_in: float,
    r_out: float,
    span: float,
    z0: float,
    height: float,
    *,
    edge_inset: float = 0.0,
) -> cq.Shape:
    """Annular ink band over [0, span] — the continuous guide arc of 001 L75-L78
    and the outer ink band of 002 L75-L80."""
    lo = edge_inset
    hi = span - edge_inset
    outer: list[tuple[float, float]] = []
    inner: list[tuple[float, float]] = []
    for index in range(_ARC_SEGMENTS + 1):
        angle = lo + (hi - lo) * index / _ARC_SEGMENTS
        outer.append((r_out * math.cos(angle), r_out * math.sin(angle)))
        inner.append((r_in * math.cos(angle), r_in * math.sin(angle)))
    points = outer + list(reversed(inner))
    return (
        cq.Workplane("XY", origin=(0.0, 0.0, z0))
        .polyline(points)
        .close()
        .extrude(height)
        .val()
    )


def _radial_ticks(
    *,
    count: int,
    span: float,
    r_outer: float,
    major_len: float,
    minor_len: float,
    major_w: float,
    minor_w: float,
    z0: float,
    height: float,
    edge_inset: float = 0.0,
) -> list[cq.Shape]:
    """5-degree radial graduations (001 L66-L73, 002 L83-L99, 003 L129-L148).

    Emitted as plain solids that are compounded into ONE cutter and cut in a
    single boolean — see the module docstring.  `edge_inset` keeps the end marks
    clear of a straight radial plate edge; see `_tick_edge_inset`.
    """
    solids: list[cq.Shape] = []
    denominator = max(1, count - 1)
    lo = edge_inset
    hi = span - edge_inset
    for index in range(count):
        angle = lo + (hi - lo) * index / denominator
        major = index % 2 == 0
        length = major_len if major else minor_len
        width = major_w if major else minor_w
        radial_centre = r_outer - length * 0.5
        tick = (
            cq.Workplane("XY")
            .box(length, width, height, centered=(True, True, False))
            .translate((radial_centre, 0.0, z0))
            .rotate((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), math.degrees(angle))
        )
        solids.append(tick.val())
    return solids


def _linear_ticks(
    *,
    x0: float,
    x1: float,
    pitch: float,
    y_base: float,
    major_len: float,
    minor_len: float,
    width: float,
    z0: float,
    height: float,
) -> list[cq.Shape]:
    """Straight rule graduations off a baseline (001 L81-L86, 002 L108-L117)."""
    solids: list[cq.Shape] = []
    count = max(2, int((x1 - x0) / pitch))
    for index in range(count + 1):
        x = x0 + (x1 - x0) * index / count
        major = index % 2 == 0
        length = major_len if major else minor_len
        tick = (
            cq.Workplane("XY")
            .box(width, length, height, centered=(True, True, False))
            .translate((x, y_base + length * 0.5, z0))
        )
        solids.append(tick.val())
    return solids


def _axial_bore(radius: float, z0: float, z1: float) -> cq.Workplane:
    return (
        cq.Workplane("XY", origin=(0.0, 0.0, z0)).circle(radius).extrude(z1 - z0)
    )


def _pivot_boss(*, outer_r: float, inner_r: float, z0: float, height: float) -> cq.Workplane:
    """Low annular thrust boss (001 L57, 002 L53-L60).  Welded into the plate with
    `_WELD` and carried `_CONTACT_EMBED` past the seat plane so the arm's flat
    underside is in real contact instead of tangency."""
    return (
        cq.Workplane("XY", origin=(0.0, 0.0, z0 - _WELD))
        .circle(outer_r)
        .circle(inner_r)
        .extrude(height + _WELD)
    )


# --- body_form candidates -----------------------------------------------------
def _body_form_semicircular_solid_plate_build(r: ResolvedConfig):
    """Record 001 L34-L88: one-piece half-round plate fused to a fixed rule."""
    radius = r.body_radius_m
    thickness = r.body_thickness_m

    full_disc = cq.Workplane("XY").circle(radius).extrude(thickness)
    upper_clip = (
        cq.Workplane("XY")
        .box(2.033 * radius, 1.033 * radius, thickness, centered=(True, False, False))
        .translate((0.0, -0.0033 * radius, 0.0))
    )
    half_disc = full_disc.intersect(upper_clip)

    # 001 L47-L52: 304 x 18 x 1.8 mm rule offset to (-44, -10); the rule is
    # thinner than the plate and fused into the SAME solid, not a second part.
    rule_thickness = thickness * 0.82
    rule_x0 = -0.733 * radius
    rule_y0 = -r.rule_width_m * (5.0 / 9.0)
    fixed_rule = (
        cq.Workplane("XY")
        .box(r.rule_length_m, r.rule_width_m, rule_thickness, centered=(False, False, False))
        .translate((rule_x0, rule_y0, 0.0))
    )
    body = half_disc.union(fixed_rule)
    body = body.union(
        _pivot_boss(
            outer_r=min(0.0135, max(r.body_bore_r_m + 0.0026, radius * 0.127)),
            inner_r=r.body_bore_r_m,
            z0=thickness,
            height=r.pivot_boss_h_m + _CONTACT_EMBED,
        )
    )
    body = body.cut(_axial_bore(r.body_bore_r_m, -0.002, thickness + 0.004))

    ink_top = r.body_top_z_m + _INK_PROUD
    inset = _tick_edge_inset(
        tick_width=radius * 0.011, r_outer=radius * 0.965, span=r.body_angular_span_rad
    )
    ink: list[cq.Shape] = _radial_ticks(
        count=r.outer_tick_count,
        span=r.body_angular_span_rad,
        r_outer=radius * 0.965,
        major_len=radius * 0.133,
        minor_len=radius * 0.075,
        major_w=radius * 0.011,
        minor_w=radius * 0.0075,
        z0=ink_top - _INK_T,
        height=_INK_T,
        edge_inset=inset,
    )
    for guide in (0.70, 0.85):
        ink.append(
            _arc_band(
                radius * guide - radius * 0.005,
                radius * guide + radius * 0.005,
                r.body_angular_span_rad,
                ink_top - _INK_T,
                _INK_T,
                edge_inset=inset,
            )
        )
    rule_ink_top = rule_thickness + _INK_PROUD
    ink.extend(
        _linear_ticks(
            x0=rule_x0 + 0.010,
            x1=rule_x0 + r.rule_length_m - 0.010,
            pitch=0.010,
            y_base=rule_y0 + 0.0004,
            major_len=r.rule_width_m * 0.42,
            minor_len=r.rule_width_m * 0.24,
            width=0.00055,
            z0=rule_ink_top - _INK_T,
            height=_INK_T,
        )
    )
    return body.cut(_compound(ink))


def _body_form_semicircular_arch_rail_build(r: ResolvedConfig):
    """Record 002 L29-L69 (+ markings L72-L134): open 180-degree arch spanned by a
    straight rail across both feet."""
    radius = r.body_radius_m
    thickness = r.body_thickness_m
    inner_radius = radius * r.arch_inner_ratio

    outer = _sector_disc(radius, math.pi, 0.0, thickness)
    inner_cutter = _sector_disc(inner_radius, math.pi, -0.001, thickness + 0.002)
    arch = outer.cut(inner_cutter)

    rail_length = 2.0 * radius * r.rail_length_ratio
    rail_width = radius * 0.192
    rail = (
        cq.Workplane("XY")
        .box(rail_length, rail_width, thickness, centered=(True, True, False))
        .translate((0.0, -radius * 0.032, 0.0))
    )
    body = arch.union(rail)
    body = body.union(
        _pivot_boss(
            outer_r=min(0.0135, max(r.body_bore_r_m + 0.0026, radius * 0.135)),
            inner_r=r.body_bore_r_m,
            z0=thickness,
            height=r.pivot_boss_h_m + _CONTACT_EMBED,
        )
    )
    body = body.cut(_axial_bore(r.body_bore_r_m, -0.002, thickness + 0.004))

    ink_top = r.body_top_z_m + _INK_PROUD
    inset = _tick_edge_inset(
        tick_width=radius * 0.0071, r_outer=radius * 0.977, span=math.pi
    )
    ink: list[cq.Shape] = [
        _arc_band(
            radius * 0.962,
            radius * 0.987,
            math.pi,
            ink_top - _INK_T,
            _INK_T,
            edge_inset=inset,
        )
    ]
    ink.extend(
        _radial_ticks(
            count=r.outer_tick_count,
            span=math.pi,
            r_outer=radius * 0.977,
            major_len=radius * 0.144,
            minor_len=radius * 0.086,
            major_w=radius * 0.0071,
            minor_w=radius * 0.0041,
            z0=ink_top - _INK_T,
            height=_INK_T,
            edge_inset=inset,
        )
    )
    rail_y0 = -radius * 0.032 - rail_width * 0.5
    ink.append(
        cq.Workplane("XY")
        .box(rail_length * 0.96, 0.0007, _INK_T, centered=(True, True, False))
        .translate((0.0, rail_y0 + 0.0008, ink_top - _INK_T))
        .val()
    )
    ink.extend(
        _linear_ticks(
            x0=-rail_length * 0.46,
            x1=rail_length * 0.46,
            pitch=0.010,
            y_base=rail_y0 + 0.0008,
            major_len=rail_width * 0.42,
            minor_len=rail_width * 0.27,
            width=0.00042,
            z0=ink_top - _INK_T,
            height=_INK_T,
        )
    )
    return body.cut(_compound(ink))


def _body_form_full_circle_annulus_build(r: ResolvedConfig):
    """Record var_body_form_full_circle L38-L66: closed 360-degree ring.  The
    straight rail of its 002 parent is dropped entirely — a closed ring has no
    feet to span — so the bearing boss stands alone inside the ring exactly as the
    source builds it."""
    radius = r.body_radius_m
    thickness = r.body_thickness_m
    inner_radius = radius * r.annulus_inner_ratio

    outer = cq.Workplane("XY").circle(radius).extrude(thickness)
    inner_cutter = (
        cq.Workplane("XY", origin=(0.0, 0.0, -0.001)).circle(inner_radius).extrude(thickness + 0.002)
    )
    body = outer.cut(inner_cutter)

    # Bearing hub plus four slender radial spokes out to the ring.  The source
    # inherits 002's boss but drops 002's rail, leaving the boss unsupported; a
    # bearing that carries the arm stack cannot float.
    boss_r = min(0.0135, max(r.body_bore_r_m + 0.0026, radius * 0.135))
    hub = (
        cq.Workplane("XY").circle(boss_r).circle(r.body_bore_r_m).extrude(thickness)
    )
    body = body.union(hub)
    spoke_w = max(0.0022, radius * 0.038)
    for index in range(4):
        spoke = (
            cq.Workplane("XY")
            .box(inner_radius + 0.002, spoke_w, thickness, centered=(False, True, False))
            .rotate((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), 90.0 * index + 45.0)
        )
        body = body.union(spoke)
    body = body.union(
        _pivot_boss(
            outer_r=boss_r,
            inner_r=r.body_bore_r_m,
            z0=thickness,
            height=r.pivot_boss_h_m + _CONTACT_EMBED,
        )
    )
    body = body.cut(_axial_bore(r.body_bore_r_m, -0.002, thickness + 0.004))

    ink_top = r.body_top_z_m + _INK_PROUD
    ink: list[cq.Shape] = [
        _arc_band(radius * 0.962, radius * 0.987, 2.0 * math.pi, ink_top - _INK_T, _INK_T)
    ]
    ink.extend(
        _radial_ticks(
            count=r.outer_tick_count,
            span=2.0 * math.pi,
            r_outer=radius * 0.977,
            major_len=radius * 0.144,
            minor_len=radius * 0.086,
            major_w=radius * 0.0071,
            minor_w=radius * 0.0041,
            z0=ink_top - _INK_T,
            height=_INK_T,
        )
    )
    return body.cut(_compound(ink))


def _solid_rim_plate(r: ResolvedConfig, span: float, *, edge_inset: float = 0.0):
    """Shared 003-family shell: bored plate plus a welded raised scale rim
    (003 L29-L44).  The rim is unioned at `thickness - 0.00005` so it welds into
    the plate instead of leaving a coincident face."""
    radius = r.body_radius_m
    thickness = r.body_thickness_m
    plate = cq.Workplane("XY").circle(radius).circle(r.body_bore_r_m).extrude(thickness)
    rim = (
        cq.Workplane("XY", origin=(0.0, 0.0, thickness - _WELD))
        .circle(radius)
        .circle(radius * r.rim_width_ratio)
        .extrude(r.rim_height_m + _WELD)
    )
    body = plate.union(rim)

    ink_top = r.body_top_z_m + _INK_PROUD
    ink = _radial_ticks(
        count=r.outer_tick_count,
        span=span,
        r_outer=radius - 0.0010,
        major_len=radius * 0.061,
        minor_len=radius * 0.036,
        major_w=radius * 0.0073,
        minor_w=radius * 0.0040,
        z0=ink_top - _INK_T,
        height=_INK_T,
        edge_inset=edge_inset,
    )
    # 003 L150-L168: a second, inward-reading scale at half the rhythm, cut into
    # the same rim so the part stays one solid.
    inner_count = max(2, r.outer_tick_count // 2)
    denominator = max(1, inner_count - 1)
    rim_inner = radius * r.rim_width_ratio
    for index in range(inner_count):
        angle = edge_inset + (span - 2.0 * edge_inset) * index / denominator
        length = min(radius * (0.033 if index % 3 == 0 else 0.023), (radius - rim_inner) * 0.45)
        radial_centre = rim_inner + (radius - rim_inner) * 0.30 + length * 0.5
        tick = (
            cq.Workplane("XY")
            .box(length, radius * 0.0043, _INK_T, centered=(True, True, False))
            .translate((radial_centre, 0.0, ink_top - _INK_T))
            .rotate((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), math.degrees(angle))
        )
        ink.append(tick.val())
    return body, ink


def _body_form_full_circle_solid_plate_build(r: ResolvedConfig):
    """Record 003 L29-L44: 360-degree solid plate with a raised graduation rim and
    NO bearing boss — the arm rides a real running clearance over it."""
    body, ink = _solid_rim_plate(r, 2.0 * math.pi)
    return body.cut(_compound(ink))


def _body_form_quadrant_sector_build(r: ResolvedConfig):
    """Record var_body_form_quadrant L29-L71: build the COMPLETE plate and rim,
    then cut two half-space boxes away.  Cutting from a complete body rather than
    authoring a sector profile keeps the rim weld intact."""
    radius = r.body_radius_m
    span = r.sector_span_rad
    # Graduations are cut AFTER the sector, matching the source's own order
    # (var_body_form_quadrant cuts the quadrant out of the complete plate + rim and
    # only then lays down its scale).  Cutting them first leaves the rotated
    # half-space boolean grinding against every groove face: seed 29's plate did
    # not finish in 600 s that way, and finishes in 0.2 s this way.
    body, ink = _solid_rim_plate(
        r,
        span,
        edge_inset=_tick_edge_inset(
            tick_width=radius * 0.0073, r_outer=radius - 0.0010, span=span
        ),
    )

    h_total = r.body_thickness_m + r.rim_height_m + 0.002
    cut_below_zero = (
        cq.Workplane("XY", origin=(0.0, 0.0, -0.001))
        .center(0.0, -radius)
        .rect(radius * 4.0, radius * 2.0)
        .extrude(h_total)
    )
    # The source's `cut_neg_x` removes everything past pi/2; rotating it by
    # (span - pi/2) generalises the same cut to any declared sector span.
    cut_beyond_span = (
        cq.Workplane("XY", origin=(0.0, 0.0, -0.001))
        .center(-radius, 0.0)
        .rect(radius * 2.0, radius * 4.0)
        .extrude(h_total)
        .rotate((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), math.degrees(span - math.pi / 2.0))
    )
    body = body.cut(cut_below_zero).cut(cut_beyond_span)
    return body.cut(_compound(ink))


_BODY_BUILDERS = {
    "semicircular_solid_plate": _body_form_semicircular_solid_plate_build,
    "semicircular_arch_rail": _body_form_semicircular_arch_rail_build,
    "full_circle_annulus": _body_form_full_circle_annulus_build,
    "full_circle_solid_plate": _body_form_full_circle_solid_plate_build,
    "quadrant_sector": _body_form_quadrant_sector_build,
}


# --- arm_form candidates ------------------------------------------------------
def _arm_form_tapered_rule_pointer_tail_build(r: ResolvedConfig, thickness: float):
    """Record 001 L91-L126: 5-point tapered blade, pivot boss and a short pointer
    tail on the far side of the pivot."""
    length = r.blade_length_m
    half_w = length * 0.0346
    profile = [
        (0.0, -half_w),
        (length * 0.969, -half_w * 0.889),
        (length, 0.0),
        (length * 0.969, half_w * 0.889),
        (0.0, half_w),
    ]
    blade = cq.Workplane("XY").polyline(profile).close().extrude(thickness)
    hub = cq.Workplane("XY").circle(r.arm_hub_r_m).extrude(thickness)
    tail = r.pointer_tail_length_m
    pointer_tail = (
        cq.Workplane("XY")
        .polyline(
            [
                (-tail, 0.0),
                (-tail * 0.40, -half_w * 0.667),
                (0.001, -half_w * 0.889),
                (0.001, half_w * 0.889),
                (-tail * 0.40, half_w * 0.667),
            ]
        )
        .close()
        .extrude(thickness)
    )
    ink = _linear_ticks(
        x0=r.arm_hub_r_m + 0.004,
        x1=length * 0.96,
        pitch=0.010,
        y_base=half_w * 0.30,
        major_len=half_w * 0.52,
        minor_len=half_w * 0.30,
        width=0.00050,
        z0=0.0,
        height=_INK_T,
    )
    # 001 L124: a shallow longitudinal sight line reinforcing the measuring edge.
    ink.append(
        cq.Workplane("XY")
        .box(length * 0.88, 0.00045, _INK_T, centered=(True, True, False))
        .translate((length * 0.52, -half_w * 0.62, 0.0))
        .val()
    )
    return blade.union(hub).union(pointer_tail), ink


def _arm_form_pointed_strip_build(r: ResolvedConfig, thickness: float):
    """Record 002 L137-L155 (+ tip stop L259-L264): short constant-width strip
    that narrows to a point, unioned with a broad circular pivot hub."""
    length = r.blade_length_m
    half_w = r.strip_half_width_m
    back = -min(0.008, r.arm_hub_r_m * 0.72)
    outline = [
        (back, -half_w),
        (length * 0.935, -half_w),
        (length, 0.0),
        (length * 0.935, half_w),
        (back, half_w),
    ]
    strip = cq.Workplane("XY").polyline(outline).close().extrude(thickness)
    hub = cq.Workplane("XY").circle(r.arm_hub_r_m).extrude(thickness)
    ink = _linear_ticks(
        x0=r.arm_hub_r_m + 0.003,
        x1=length * 0.94,
        pitch=0.009,
        y_base=-half_w * 0.52,
        major_len=half_w * 0.81,
        minor_len=half_w * 0.58,
        width=0.00042,
        z0=0.0,
        height=_INK_T,
    )
    # The dark end block that reads as the pointer/stop; welded into the blade's
    # top layer rather than perched on it, so it can never foul a stacked arm.
    ink.append(
        cq.Workplane("XY")
        .box(0.0060, min(0.0100, half_w * 1.2), _INK_T, centered=(True, True, False))
        .translate((length * 0.944, 0.0, 0.0))
        .val()
    )
    return strip.union(hub), ink


def _arm_form_double_ended_blade_build(r: ResolvedConfig, thickness: float):
    """Record 003 L47-L77: symmetric 12-point outline with an upper straight ruler
    and a lower tapered pointer on opposite sides of the pivot.

    Authored along +X (source authors it along +Y) so every arm candidate shares
    one angular convention; ratios are the source's.
    """
    upper = r.upper_ruler_length_m
    lower = r.pointer_length_m
    w = r.arm_hub_r_m * 0.72
    outline = [
        (upper, -w),
        (upper, w),
        (upper * 0.206, w),
        (-lower * 0.200, w * 1.611),
        (-lower * 0.550, w * 1.222),
        (-lower * 0.850, w * 0.667),
        (-lower, w * 0.422),
        (-lower, -w * 0.422),
        (-lower * 0.850, -w * 0.667),
        (-lower * 0.550, -w * 1.222),
        (-lower * 0.200, -w * 1.611),
        (upper * 0.206, -w),
    ]
    blade = cq.Workplane("XY").polyline(outline).close().extrude(thickness)
    ink: list[cq.Shape] = [
        cq.Workplane("XY")
        .box(upper * 0.706, 0.00045, _INK_T, centered=(True, True, False))
        .translate((upper * 0.588, 0.0, 0.0))
        .val(),
        cq.Workplane("XY")
        .box(lower * 0.6125, 0.00045, _INK_T, centered=(True, True, False))
        .translate((-lower * 0.5875, 0.0, 0.0))
        .val(),
    ]
    tick_count = max(4, int(round(upper / 0.008)))
    for index in range(tick_count):
        x = upper * (0.32 + 0.62 * index / max(1, tick_count - 1))
        length = w * (0.556 if index % 2 == 0 else 0.367)
        ink.append(
            cq.Workplane("XY")
            .box(0.00035, length, _INK_T, centered=(True, True, False))
            .translate((x, -length * 0.5, 0.0))
            .val()
        )
    return blade, ink


def _arm_form_vernier_plate_arm_build(r: ResolvedConfig, thickness: float):
    """Record var_reading_module_vernier_plate L158-L196 (+ ink L199-L229): the
    strip is cut back and a widened rectangular vernier reading head is unioned in
    over the hub region."""
    length = r.blade_length_m
    half_w = r.arm_hub_r_m * 0.42
    plate_half = r.vernier_plate_half_width_m
    plate_x1 = plate_half * 2.0
    back = -min(0.008, r.arm_hub_r_m * 0.72)
    strip = (
        cq.Workplane("XY")
        .polyline(
            [
                (plate_x1, -half_w),
                (length * 0.935, -half_w),
                (length, 0.0),
                (length * 0.935, half_w),
                (plate_x1, half_w),
            ]
        )
        .close()
        .extrude(thickness)
    )
    plate = (
        cq.Workplane("XY")
        .polyline(
            [
                (back, -plate_half),
                (plate_x1, -plate_half),
                (plate_x1, plate_half),
                (back, plate_half),
            ]
        )
        .close()
        .extrude(thickness)
    )
    hub = cq.Workplane("XY").circle(r.arm_hub_r_m).extrude(thickness)

    pitch = (plate_x1 - back - 0.003) / max(1, r.vernier_division_count - 1)
    baseline_y = -plate_half * 0.862
    ink: list[cq.Shape] = [
        cq.Workplane("XY")
        .box(plate_x1 - back - 0.002, 0.00055, _INK_T, centered=(True, True, False))
        .translate(((back + plate_x1) * 0.5, baseline_y, 0.0))
        .val()
    ]
    for index in range(r.vernier_division_count):
        x = back + 0.0015 + index * pitch
        major = index % 5 == 0
        tick_h = plate_half * (0.46 if major else 0.29)
        ink.append(
            cq.Workplane("XY")
            .box(0.00035 if major else 0.00028, tick_h, _INK_T, centered=(True, True, False))
            .translate((x, baseline_y + tick_h * 0.5, 0.0))
            .val()
        )
    ink.extend(
        _linear_ticks(
            x0=plate_x1 + 0.004,
            x1=length * 0.94,
            pitch=0.010,
            y_base=-half_w * 0.52,
            major_len=half_w * 0.81,
            minor_len=half_w * 0.58,
            width=0.00042,
            z0=0.0,
            height=_INK_T,
        )
    )
    return strip.union(plate).union(hub), ink


_ARM_BUILDERS = {
    "tapered_rule_pointer_tail": _arm_form_tapered_rule_pointer_tail_build,
    "pointed_strip": _arm_form_pointed_strip_build,
    "double_ended_blade": _arm_form_double_ended_blade_build,
    "vernier_plate_arm": _arm_form_vernier_plate_arm_build,
}


def _arm_shapes(r: ResolvedConfig, *, topmost: bool):
    """Place one candidate blade in the arm's Z-frame, add the hub cap, cut the
    real through-bore, and (for the cam lever) cut the source's host relief."""
    thickness = r.arm_thickness_m
    z_lo = r.arm_z_lo_m
    z_hi = z_lo + thickness
    profile, ink_flat = _ARM_BUILDERS[r.arm_form](r, thickness)
    blade = profile.translate((0.0, 0.0, z_lo))

    boss_h = r.arm_boss_h_m if (topmost and r.arm_form == "double_ended_blade") else 0.0
    hub_cap = (
        cq.Workplane("XY", origin=(0.0, 0.0, z_hi - _WELD))
        .circle(r.arm_hub_r_m)
        .circle(r.arm_bore_r_m)
        .extrude(boss_h + _CONTACT_EMBED + _WELD)
    )
    arm = blade.union(hub_cap)

    if topmost and r.hub_relief_required == "yes":
        # var_lock_cam_lever L158-L164: a flat relief CUT into the hub top for the
        # clamped handle to lie in.  Sized off the handle, not a magic constant.
        relief = (
            cq.Workplane("XY")
            .box(
                r.lever_handle_length_m * 1.38,
                min(0.0068, r.arm_hub_r_m * 0.55),
                0.0004,
                centered=(True, True, False),
            )
            .translate((r.lever_handle_length_m * 0.54, 0.0, z_hi + boss_h + _CONTACT_EMBED - 0.0004))
        )
        arm = arm.cut(relief)

    arm = arm.cut(_axial_bore(r.arm_bore_r_m, z_lo - 0.002, z_hi + boss_h + 0.004))

    ink_top = z_hi + _INK_PROUD
    ink = [shape.translate(cq.Vector(0.0, 0.0, ink_top - _INK_T)) for shape in ink_flat]
    return arm.cut(_compound(ink))


# --- lock_module candidates ---------------------------------------------------
def _lock_module_knurled_clamp_screw_build(r: ResolvedConfig):
    """Record 001 L129-L144: captive shaft running well below the plate, lower
    flange, ribbed grip and cap, plus the dark washer that seats on the arm."""
    shaft_bottom = -(r.lock_seat_z_m + 0.010)
    shaft = (
        cq.Workplane("XY", origin=(0.0, 0.0, shaft_bottom))
        .circle(r.lock_shaft_r_m)
        .extrude(0.002 - shaft_bottom)
    )
    washer = (
        cq.Workplane("XY", origin=(0.0, 0.0, -_CONTACT_EMBED))
        .circle(r.lock_seat_r_m)
        .extrude(0.0006 + _CONTACT_EMBED)
    )
    lower = (
        cq.Workplane("XY", origin=(0.0, 0.0, 0.0004))
        .circle(r.grip_r_m * 0.979)
        .extrude(0.0028)
    )
    grip = (
        cq.Workplane("XY", origin=(0.0, 0.0, 0.0030))
        .circle(r.grip_r_m)
        .extrude(r.grip_h_m)
    )
    cap = (
        cq.Workplane("XY", origin=(0.0, 0.0, 0.0030 + r.grip_h_m - _WELD))
        .circle(r.grip_r_m * 0.947)
        .extrude(r.grip_h_m * 0.329 + _WELD)
    )
    fastener = shaft.union(washer).union(lower).union(grip).union(cap)
    for index in range(r.knurl_rib_count):
        angle = 360.0 * index / r.knurl_rib_count
        rib = (
            cq.Workplane("XY")
            .box(0.0012, 0.0010, r.grip_h_m * 0.965, centered=(True, True, False))
            .translate((r.grip_r_m * 0.984, 0.0, 0.0032))
            .rotate((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), angle)
        )
        fastener = fastener.union(rib)
    return fastener, None


def _lock_module_slotted_screw_build(r: ResolvedConfig):
    """Record 002 L177-L197: shaft plus a low round head with a REAL driver slot
    cut into it, and a dark insert dropped into the machined slot."""
    shaft_bottom = -(r.lock_seat_z_m + 0.001)
    shaft = (
        cq.Workplane("XY", origin=(0.0, 0.0, shaft_bottom))
        .circle(r.lock_shaft_r_m)
        .extrude(0.0005 - shaft_bottom)
    )
    head = (
        cq.Workplane("XY", origin=(0.0, 0.0, -_CONTACT_EMBED))
        .circle(r.head_r_m)
        .extrude(r.head_h_m + _CONTACT_EMBED)
    )
    screw = shaft.union(head)
    slot_depth = min(0.0007, r.head_h_m * 0.30)
    slot_cutter = (
        cq.Workplane("XY", origin=(0.0, 0.0, r.head_h_m - slot_depth))
        .box(r.head_r_m * 1.32, r.slot_width_m, slot_depth + 0.001, centered=(True, True, False))
    )
    screw = screw.cut(slot_cutter)
    inlay = (
        cq.Workplane("XY", origin=(0.0, 0.0, r.head_h_m - slot_depth - _WELD))
        .box(
            r.head_r_m * 1.26,
            r.slot_width_m * 0.75,
            slot_depth * 0.45 + _WELD,
            centered=(True, True, False),
        )
    )
    return screw, inlay


def _lock_module_capstan_screw_retainer_build(r: ResolvedConfig):
    """Record 003 L230-L270: cap above the arm boss, shaft through both real
    bores, and an underside retainer whose top face lands on the plate underside —
    the fastener CAPTURES the plate rather than resting on it."""
    # The retainer only captures if it is genuinely wider than the plate bore it
    # passes through; the declared radius is floored on that bore.
    retainer_r = max(r.retainer_r_m, r.body_bore_r_m + 0.0010)
    retainer_top = r.retainer_top_z_m + _CONTACT_EMBED
    retainer = (
        cq.Workplane("XY", origin=(0.0, 0.0, retainer_top - r.retainer_h_m))
        .circle(retainer_r)
        .extrude(r.retainer_h_m)
    )
    shaft = (
        cq.Workplane("XY", origin=(0.0, 0.0, retainer_top - r.retainer_h_m))
        .circle(r.lock_shaft_r_m)
        .extrude(0.0005 - (retainer_top - r.retainer_h_m))
    )
    cap = (
        cq.Workplane("XY", origin=(0.0, 0.0, -_CONTACT_EMBED))
        .circle(r.cap_r_m)
        .extrude(0.0011 + _CONTACT_EMBED)
    )
    screw = retainer.union(shaft).union(cap)
    bar_x = (
        cq.Workplane("XY", origin=(0.0, 0.0, 0.0011 - _WELD))
        .box(r.cap_r_m * 1.30, 0.0010, 0.00018 + _WELD, centered=(True, True, False))
    )
    bar_y = (
        cq.Workplane("XY", origin=(0.0, 0.0, 0.0011 - _WELD))
        .box(0.0010, r.cap_r_m * 1.30, 0.00018 + _WELD, centered=(True, True, False))
    )
    return screw, bar_x.union(bar_y)


def _lock_module_cam_lever_build(r: ResolvedConfig):
    """Record var_lock_cam_lever L210-L252: eccentric lobe, straight handle,
    rounded tip and a collar that seats on the arm hub.  The eccentricity IS the
    clamping action."""
    shaft_bottom = -(r.lock_seat_z_m + 0.001)
    shaft = (
        cq.Workplane("XY", origin=(0.0, 0.0, shaft_bottom))
        .circle(r.lock_shaft_r_m)
        .extrude(0.0005 - shaft_bottom)
    )
    collar = (
        cq.Workplane("XY", origin=(0.0, 0.0, -_CONTACT_EMBED))
        .circle(min(r.lock_seat_r_m, r.cam_lobe_r_m * 0.60))
        .extrude(0.0010 + _CONTACT_EMBED)
    )
    lobe = (
        cq.Workplane("XY", origin=(0.0, 0.0, 0.0))
        .center(r.cam_eccentricity_m, 0.0)
        .circle(r.cam_lobe_r_m)
        .extrude(0.0022)
    )
    handle_length = r.lever_handle_length_m
    handle = (
        cq.Workplane("XY", origin=(0.0, 0.0, 0.0))
        .box(handle_length, r.cam_lobe_r_m * 0.83, 0.0022, centered=(True, True, False))
        .translate((r.cam_eccentricity_m + handle_length * 0.5 - 0.0018, 0.0, 0.0))
    )
    tip = (
        cq.Workplane("XY", origin=(0.0, 0.0, 0.0))
        .center(r.cam_eccentricity_m + handle_length - 0.0018, 0.0)
        .circle(r.cam_lobe_r_m * 0.414)
        .extrude(0.0022)
    )
    lever = shaft.union(collar).union(lobe).union(handle).union(tip)
    indicator = (
        cq.Workplane("XY", origin=(0.0, 0.0, 0.0022 - _WELD))
        .box(handle_length * 0.62, 0.0009, 0.00018 + _WELD, centered=(True, True, False))
        .translate((r.cam_eccentricity_m + handle_length * 0.5, 0.0, 0.0))
    )
    return lever, indicator


_LOCK_BUILDERS = {
    "knurled_clamp_screw": _lock_module_knurled_clamp_screw_build,
    "slotted_screw": _lock_module_slotted_screw_build,
    "capstan_screw_retainer": _lock_module_capstan_screw_retainer_build,
    "cam_lever": _lock_module_cam_lever_build,
}


# --- assembly -----------------------------------------------------------------
def _materials(model: ArticulatedObject) -> dict[str, str]:
    model.material("protractor_plate", rgba=(0.72, 0.78, 0.80, 0.62))
    model.material("protractor_arm", rgba=(0.45, 0.76, 0.88, 0.66))
    model.material("scale_ink_black", rgba=(0.06, 0.07, 0.07, 0.97))
    model.material("scale_ink_red", rgba=(0.74, 0.13, 0.16, 0.94))
    model.material("machined_steel", rgba=(0.64, 0.66, 0.68, 1.0))
    model.material("fastener_dark", rgba=(0.11, 0.12, 0.13, 1.0))
    return {
        "plate": "protractor_plate",
        "arm": "protractor_arm",
        "black": "scale_ink_black",
        "red": "scale_ink_red",
        "steel": "machined_steel",
        "dark": "fastener_dark",
    }


def _build_graduated_plate(model: ArticulatedObject, r: ResolvedConfig, mats: dict[str, str]):
    prefix = f"body_form__{r.body_form}"
    shell = _BODY_BUILDERS[r.body_form](r)
    part = model.part(
        f"{prefix}__graduated_plate",
        meta={
            "role": "graduated_plate",
            "candidate": r.body_form,
            "bearing_kind": r.body_bearing_kind,
            "angular_span_rad": r.body_angular_span_rad,
        },
    )
    part.visual(
        mesh_from_cadquery(shell, f"{prefix}__body_shell", tolerance=0.00030),
        material=mats["plate"],
        name=f"{prefix}__body_shell", material_class_id="plastic.clear_rigid",
    )
    return part


def _build_swing_arms(
    model: ArticulatedObject,
    r: ResolvedConfig,
    mats: dict[str, str],
    plate,
):
    prefix = f"arm_form__{r.arm_form}"
    needs_two = r.arm_count > 1 and (
        r.arm_form == "double_ended_blade" or r.hub_relief_required == "yes"
    )
    top_mesh = mesh_from_cadquery(
        _arm_shapes(r, topmost=True), f"{prefix}__arm_shell_top", tolerance=0.00025
    )
    if needs_two:
        low_mesh = mesh_from_cadquery(
            _arm_shapes(r, topmost=False), f"{prefix}__arm_shell_lower", tolerance=0.00025
        )
    else:
        low_mesh = top_mesh

    arms = []
    for index in range(r.arm_count):
        topmost = index == r.arm_count - 1
        part = model.part(
            f"{prefix}__swing_arm_{index}",
            meta={
                "role": "swing_arm",
                "candidate": r.arm_form,
                "arm_index": index,
                "topmost": topmost,
            },
        )
        part.visual(
            top_mesh if topmost else low_mesh,
            material=mats["arm"],
            name=f"{prefix}__arm_shell_{index}", material_class_id="plastic.clear_rigid",
        )

        rest = r.arm_rest_angles_rad[index]
        provider = AxisInterface(
            name=f"body_form__{r.body_form}__plate_pivot_axis_{index}",
            point=(0.0, 0.0, r.arm_seat_z_m + index * r.arm_thickness_m),
            axis=(0.0, 0.0, 1.0),
            radial=(1.0, 0.0, 0.0),
            radius=r.body_bore_r_m,
        )
        consumer = AxisInterface(
            name=f"{prefix}__arm_bore_axis_{index}",
            point=(0.0, 0.0, 0.0),
            axis=(0.0, 0.0, 1.0),
            radial=(1.0, 0.0, 0.0),
            radius=r.arm_bore_r_m,
        )
        mate = mate_axes(provider, consumer, spin=rest)
        joint_name = f"{prefix}__arm_pivot_{index}"
        model.articulation(
            joint_name,
            ArticulationType.REVOLUTE,
            parent=plate,
            child=part,
            origin=mate.origin,
            axis=mate.axis,
            motion_limits=MotionLimits(
                effort=2.0,
                velocity=2.5,
                lower=r.arm_swing_lower_rad - rest,
                upper=r.arm_swing_upper_rad - rest,
            ),
            meta={"mechanism": "swing arm on the shared plate pivot", "arm_index": index},
        )
        register_interface_mate(model, joint_name, mate)
        arms.append(part)
    return arms


def _build_pivot_lock(
    model: ArticulatedObject,
    r: ResolvedConfig,
    mats: dict[str, str],
    plate,
    arms,
):
    prefix = f"lock_module__{r.lock_module}"
    body_shape, detail_shape = _LOCK_BUILDERS[r.lock_module](r)
    part = model.part(
        f"{prefix}__pivot_lock",
        meta={
            "role": "pivot_lock",
            "candidate": r.lock_module,
            "joint_parent_role": r.lock_joint_parent_role,
        },
    )
    part.visual(
        mesh_from_cadquery(body_shape, f"{prefix}__lock_body", tolerance=0.00020),
        material=mats["steel"],
        name=f"{prefix}__lock_body", material_class_id="metal.steel_bare",
    )
    if detail_shape is not None:
        part.visual(
            mesh_from_cadquery(detail_shape, f"{prefix}__lock_detail", tolerance=0.00014),
            material=mats["dark"],
            name=f"{prefix}__lock_detail", material_class_id="metal.blackened_gunmetal",
        )

    top_arm = arms[-1]
    if r.lock_joint_parent_role == "graduated_plate":
        parent = plate
        provider = AxisInterface(
            name=f"body_form__{r.body_form}__plate_lock_axis",
            point=(0.0, 0.0, r.lock_seat_z_m),
            axis=(0.0, 0.0, 1.0),
            radial=(1.0, 0.0, 0.0),
            radius=r.body_bore_r_m,
        )
    else:
        parent = top_arm
        provider = AxisInterface(
            name=f"arm_form__{r.arm_form}__arm_lock_axis",
            point=(0.0, 0.0, r.arm_hub_top_z_m),
            axis=(0.0, 0.0, 1.0),
            radial=(1.0, 0.0, 0.0),
            radius=r.arm_bore_r_m,
        )
    consumer = AxisInterface(
        name=f"{prefix}__lock_bore_axis",
        point=(0.0, 0.0, 0.0),
        axis=(0.0, 0.0, 1.0),
        radial=(1.0, 0.0, 0.0),
        radius=r.lock_shaft_r_m,
    )
    mate = mate_axes(provider, consumer)
    joint_name = f"{prefix}__lock_turn"
    model.articulation(
        joint_name,
        ArticulationType.REVOLUTE,
        parent=parent,
        child=part,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(
            effort=1.5,
            velocity=4.5,
            lower=-r.turn_range_rad,
            upper=r.turn_range_rad,
        ),
        meta={"mechanism": "pivot-axis locking fastener"},
    )
    register_interface_mate(model, joint_name, mate)
    return part


def build_protractor_with_swing_arm(
    config: Config | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    source_config = config or config_from_seed(0)
    r = resolve_config(source_config)
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={
            "category": "protractor_with_swing_arm",
            "slot_choices": slot_choices_for_config(source_config),
            "bearing_kind": r.body_bearing_kind,
            "lock_joint_parent_role": r.lock_joint_parent_role,
        },
    )
    mats = _materials(model)
    plate = _build_graduated_plate(model, r, mats)
    arms = _build_swing_arms(model, r, mats, plate)
    _build_pivot_lock(model, r, mats, plate, arms)

    arm_joints = [f"arm_form__{r.arm_form}__arm_pivot_{i}" for i in range(r.arm_count)]
    lock_joint = f"lock_module__{r.lock_module}__lock_turn"
    # Authored high-risk coupled poses: the whole stack swept to each end of the
    # plate's angular span while the fastener is at its own travel limits.
    model.meta["risk_poses"] = (
        {**{name: r.arm_swing_lower_rad - r.arm_rest_angles_rad[i] for i, name in enumerate(arm_joints)},
         lock_joint: -r.turn_range_rad},
        {**{name: r.arm_swing_upper_rad - r.arm_rest_angles_rad[i] for i, name in enumerate(arm_joints)},
         lock_joint: r.turn_range_rad},
    )
    if r.arm_count > 1:
        model.meta["coupled_joint_pairs"] = tuple(
            (arm_joints[i], arm_joints[i + 1]) for i in range(r.arm_count - 1)
        )
    return model


def build_seeded_protractor_with_swing_arm(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_protractor_with_swing_arm(config_from_seed(seed), assets=assets)


# --- authored tests -----------------------------------------------------------
def _plan_overlap(a, b) -> float:
    if a is None or b is None:
        return -1.0
    return min(
        min(a[1][axis], b[1][axis]) - max(a[0][axis], b[0][axis]) for axis in (0, 1)
    )


def run_protractor_with_swing_arm_tests(
    object_model: ArticulatedObject, config: Config
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()

    plate = object_model.get_part(f"body_form__{r.body_form}__graduated_plate")
    arms = [
        object_model.get_part(f"arm_form__{r.arm_form}__swing_arm_{i}")
        for i in range(r.arm_count)
    ]
    arm_joints = [
        object_model.get_articulation(f"arm_form__{r.arm_form}__arm_pivot_{i}")
        for i in range(r.arm_count)
    ]
    lock = object_model.get_part(f"lock_module__{r.lock_module}__pivot_lock")
    lock_joint = object_model.get_articulation(f"lock_module__{r.lock_module}__lock_turn")

    # --- anchor: protractor_swing_arm_identity --------------------------------
    ctx.check(
        "category_anchor: every arm pivot is revolute about +Z through the plate centre",
        len(arm_joints) == r.arm_count
        and all(
            joint.articulation_type == ArticulationType.REVOLUTE
            and tuple(float(v) for v in joint.axis) == (0.0, 0.0, 1.0)
            and abs(joint.origin.xyz[0]) < 1e-9
            and abs(joint.origin.xyz[1]) < 1e-9
            and abs(joint.origin.xyz[2] - (r.arm_seat_z_m + i * r.arm_thickness_m)) < 1e-9
            and isinstance(joint.meta.get("interface_mate"), dict)
            for i, joint in enumerate(arm_joints)
        ),
        details=f"origins={[tuple(j.origin.xyz) for j in arm_joints]}, seat={r.arm_seat_z_m}",
    )

    plate_box = ctx.part_world_aabb(plate)
    arm_boxes = [ctx.part_world_aabb(arm) for arm in arms]
    crossings = [_plan_overlap(box, plate_box) for box in arm_boxes]
    ctx.check(
        "category_anchor: every arm crosses the graduated plate in plan",
        plate_box is not None and all(value >= 0.010 for value in crossings),
        details=f"plan_overlaps={crossings}, plate={plate_box}",
    )

    span = r.body_angular_span_rad
    ctx.check(
        "category_anchor: arm swing range does not exceed the plate angular span",
        abs(r.arm_swing_upper_rad - min(span, 2.0 * math.pi)) < 1e-9
        and r.arm_swing_lower_rad == 0.0
        and all(
            joint.motion_limits is not None
            and joint.motion_limits.upper - joint.motion_limits.lower <= span + 1e-9
            and joint.motion_limits.lower + r.arm_rest_angles_rad[i] >= -1e-9
            and joint.motion_limits.upper + r.arm_rest_angles_rad[i] <= span + 1e-9
            for i, joint in enumerate(arm_joints)
        ),
        details=(
            f"span={span}, limits={[(j.motion_limits.lower, j.motion_limits.upper) for j in arm_joints]}, "
            f"rest={r.arm_rest_angles_rad}"
        ),
    )

    ctx.check(
        "category_anchor: arms are parented to the plate, never chained arm to arm",
        all(joint.parent == plate.name for joint in arm_joints)
        and len({joint.child for joint in arm_joints}) == r.arm_count
        and len(object_model.root_parts()) == 1
        and object_model.root_parts()[0].name == plate.name,
        details=f"parents={[j.parent for j in arm_joints]}",
    )

    # --- anchor: protractor_pivot_lock_identity -------------------------------
    ctx.check(
        "category_anchor: the pivot lock is concentric with the arm pivot within 0.1 mm",
        lock_joint.articulation_type == ArticulationType.REVOLUTE
        and tuple(float(v) for v in lock_joint.axis) == (0.0, 0.0, 1.0)
        and math.hypot(lock_joint.origin.xyz[0], lock_joint.origin.xyz[1]) <= 0.0001
        and all(math.hypot(j.origin.xyz[0], j.origin.xyz[1]) <= 0.0001 for j in arm_joints)
        and isinstance(lock_joint.meta.get("interface_mate"), dict),
        details=f"lock_origin={tuple(lock_joint.origin.xyz)}",
    )

    ctx.check(
        "category_anchor: plate and every arm carry a real through-bore larger than the lock shaft",
        r.lock_shaft_r_m > 0.0
        and abs(r.lock_shaft_r_m - (min(r.body_bore_r_m, r.arm_bore_r_m) - 0.0009)) < 1e-12
        and r.body_bore_r_m - r.lock_shaft_r_m >= 0.0007
        and r.arm_bore_r_m - r.lock_shaft_r_m >= 0.0007,
        details=(
            f"shaft={r.lock_shaft_r_m}, body_bore={r.body_bore_r_m}, arm_bore={r.arm_bore_r_m}"
        ),
    )

    captures_plate = r.lock_module == "capstan_screw_retainer"
    ctx.check(
        "category_anchor: the lock seats on the topmost arm or captures the plate",
        abs(r.lock_seat_z_m - (r.top_arm_z_m + r.arm_hub_top_z_m)) < 1e-12
        and abs(r.top_arm_z_m - (r.arm_seat_z_m + (r.arm_count - 1) * r.arm_thickness_m)) < 1e-12
        and (
            not captures_plate
            or (
                abs(r.retainer_top_z_m + r.lock_seat_z_m) < 1e-12
                and max(r.retainer_r_m, r.body_bore_r_m + 0.0010) > r.body_bore_r_m
            )
        )
        and (
            r.lock_joint_parent_role == "graduated_plate"
            and lock_joint.parent == plate.name
            or r.lock_joint_parent_role == "top_swing_arm"
            and lock_joint.parent == arms[-1].name
        ),
        details=(
            f"lock_seat_z={r.lock_seat_z_m}, top_arm_z={r.top_arm_z_m}, "
            f"parent={lock_joint.parent}, role={r.lock_joint_parent_role}"
        ),
    )

    # --- bearing branch: the 003 family keeps a real running clearance ---------
    if r.body_bearing_kind == "thrust_boss":
        bearing_ok = (
            r.pivot_boss_h_m > 0.0
            and r.arm_running_gap_m == 0.0
            and abs(r.arm_seat_z_m - (r.body_top_z_m + r.pivot_boss_h_m)) < 1e-12
            and r.arm_z_lo_m == 0.0
        )
    else:
        bearing_ok = (
            r.pivot_boss_h_m == 0.0
            and 0.00002 <= r.arm_running_gap_m <= 0.00025
            and abs(
                r.arm_seat_z_m
                - (r.body_top_z_m + r.arm_running_gap_m + 0.5 * r.arm_thickness_m)
            )
            < 1e-12
            and abs(r.arm_z_lo_m + 0.5 * r.arm_thickness_m) < 1e-12
        )
    ctx.check(
        "arm seat plane is derived from the bearing the plate actually builds",
        bearing_ok,
        details=(
            f"kind={r.body_bearing_kind}, body_top={r.body_top_z_m}, boss={r.pivot_boss_h_m}, "
            f"gap={r.arm_running_gap_m}, seat={r.arm_seat_z_m}, arm_z_lo={r.arm_z_lo_m}"
        ),
    )

    # --- quadrant re-derives limits AND graduation count ----------------------
    ctx.check(
        "plate angular span re-derives the arm range and the graduation count",
        r.outer_tick_count == int(round(math.degrees(span) / 5.0)) + 1
        and r.outer_tick_count >= 13
        and (r.body_form != "quadrant_sector" or abs(span - r.sector_span_rad) < 1e-12)
        and (
            r.body_form
            not in ("full_circle_annulus", "full_circle_solid_plate")
            or abs(span - 2.0 * math.pi) < 1e-12
        )
        and (
            r.body_form
            not in ("semicircular_solid_plate", "semicircular_arch_rail")
            or abs(span - math.pi) < 1e-12
        ),
        details=f"span={span}, ticks={r.outer_tick_count}",
    )

    # --- cam lever host adaptation is real -----------------------------------
    ctx.check(
        "cam lever forces a cut hub relief on the topmost arm",
        (r.hub_relief_required == "yes") == (r.lock_module == "cam_lever"),
        details=f"relief={r.hub_relief_required}, lock={r.lock_module}",
    )

    # --- multiplicity: N arms stack on one axis at one thickness pitch --------
    stack_ok = all(
        abs(
            arm_joints[i + 1].origin.xyz[2] - arm_joints[i].origin.xyz[2] - r.arm_thickness_m
        )
        < 1e-12
        for i in range(r.arm_count - 1)
    )
    ctx.check(
        "arm_count stacks N arms on the shared axis and lifts the lock onto the topmost",
        len(arms) == r.arm_count
        and stack_ok
        and abs(r.arm_stack_height_m - r.arm_count * r.arm_thickness_m) < 1e-12
        and r.arm_stack_height_m <= r.body_radius_m * 0.6
        and len({tuple(round(a, 9) for a in r.arm_rest_angles_rad)}) == 1
        and len(set(r.arm_rest_angles_rad)) == r.arm_count,
        details=f"n={r.arm_count}, stack={r.arm_stack_height_m}, rest={r.arm_rest_angles_rad}",
    )

    ctx.check(
        "domain choices are recorded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(config),
        details=f"slot_choices={object_model.meta.get('slot_choices')}",
    )

    # A 003-family plate holds the arm on a real air gap, so unless the fastener
    # captures the plate from underneath the arm/lock cluster is retained by its
    # registered pivot mates rather than by contact.  This is the source's own
    # running fit (003 L406-L413), not a suppressed intersection.
    if r.body_bearing_kind == "running_clearance" and not captures_plate:
        reason = (
            "003-family plate builds no thrust boss; the arm rides the source's "
            "0.15 mm running clearance and is carried by its registered +Z axis mate."
        )
        for arm in arms:
            ctx.allow_isolated_part(arm, reason=reason)
        ctx.allow_isolated_part(lock, reason=reason)

    return ctx.report()


# --- high-risk cross-slot / boundary corners ----------------------------------
TEMPLATE_CORNERS = (
    corner_case(
        "quadrant_span_min_with_long_double_blade",
        {
            "body_form": "quadrant_sector",
            "arm_form": "double_ended_blade",
            "lock_module": "capstan_screw_retainer",
            "arm_count": 5,
            "sector_span_rad": 1.0472,
            "body_radius_m": 0.052,
            "body_thickness_m": 0.0013,
            "body_bore_r_m": 0.0026,
            "rim_height_m": 0.0009,
            "rim_width_ratio": 0.66,
            "arm_running_gap_m": 0.00004,
            "arm_thickness_m": 0.0033,
            "arm_bore_r_m": 0.0054,
            "arm_hub_r_m": 0.0155,
            "upper_ruler_length_m": 0.14,
            "pointer_length_m": 0.105,
            "arm_boss_h_m": 0.0015,
            "cap_r_m": 0.0135,
            "retainer_r_m": 0.0048,
            "retainer_h_m": 0.0018,
            "turn_range_rad": 6.2832,
        },
        reason=(
            "narrowest plate span re-deriving the joint range and tick count, on the "
            "smallest plate, with the tallest arm stack and the capturing fastener"
        ),
    ),
    corner_case(
        "running_clearance_plate_with_cam_lever_stack",
        {
            "body_form": "full_circle_solid_plate",
            "arm_form": "pointed_strip",
            "lock_module": "cam_lever",
            "arm_count": 5,
            "body_radius_m": 0.086,
            "body_thickness_m": 0.0013,
            "arm_running_gap_m": 0.00024,
            "rim_height_m": 0.0002,
            "arm_thickness_m": 0.0015,
            "blade_length_m": 0.150,
            "strip_half_width_m": 0.008,
            "arm_hub_r_m": 0.0095,
            "cam_eccentricity_m": 0.0032,
            "cam_lobe_r_m": 0.0098,
            "lever_handle_length_m": 0.040,
            "turn_range_rad": 1.5708,
        },
        reason=(
            "widest running clearance under a five-arm stack while the cam lever's "
            "host relief must still be cut into the topmost hub"
        ),
    ),
    corner_case(
        "thrust_boss_min_with_longest_tapered_blade",
        {
            "body_form": "semicircular_solid_plate",
            "arm_form": "tapered_rule_pointer_tail",
            "lock_module": "knurled_clamp_screw",
            "arm_count": 1,
            "body_radius_m": 0.052,
            "body_thickness_m": 0.0013,
            "body_bore_r_m": 0.0052,
            "pivot_boss_h_m": 0.00015,
            "rule_length_m": 0.33,
            "rule_width_m": 0.024,
            "arm_thickness_m": 0.0015,
            "arm_bore_r_m": 0.0026,
            "blade_length_m": 0.29,
            "pointer_tail_length_m": 0.040,
            "grip_r_m": 0.012,
            "grip_h_m": 0.0125,
            "knurl_rib_count": 40,
            "turn_range_rad": 14.1372,
        },
        reason=(
            "shallowest thrust boss and smallest bore pair against the longest blade "
            "and the multi-turn plate-parented screw"
        ),
    ),
    corner_case(
        "annulus_plate_with_vernier_head_stack",
        {
            "body_form": "full_circle_annulus",
            "arm_form": "vernier_plate_arm",
            "lock_module": "slotted_screw",
            "arm_count": 4,
            "body_radius_m": 0.086,
            "annulus_inner_ratio": 0.82,
            "body_bore_r_m": 0.0026,
            "pivot_boss_h_m": 0.0009,
            "arm_bore_r_m": 0.0026,
            "blade_length_m": 0.075,
            "vernier_plate_half_width_m": 0.018,
            "vernier_division_count": 13,
            "head_r_m": 0.009,
            "head_h_m": 0.0042,
            "slot_width_m": 0.002,
            "turn_range_rad": 6.2832,
        },
        reason=(
            "shortest blade over the widest open ring, with the widest reading head "
            "and the smallest bore pair driving the shaft clearance derivation"
        ),
    ),
)


__all__ = [
    "TEMPLATE_CORNERS",
    "TEMPLATE_DOMAIN",
    "Config",
    "ResolvedConfig",
    "build_protractor_with_swing_arm",
    "build_seeded_protractor_with_swing_arm",
    "config_from_seed",
    "resolve_config",
    "run_protractor_with_swing_arm_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
]
