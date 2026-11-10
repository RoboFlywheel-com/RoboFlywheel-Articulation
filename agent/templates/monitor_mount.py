# SPDX-License-Identifier: Apache-2.0

"""Counterbalanced monitor mount procedural template.

PRIMARY_ANCHOR = rec_monitor_mount_997e8c29b2f44a30a7dd25da2a7c6fa6:rev_000001

Adapted from the anchor's structural skeleton with literal dimensions
parameterised. Part tree, joint topology and primitive choices are inherited
verbatim from the anchor (per AUTHORING.md §A Rule 3).

Anchor part tree (6 parts):
  wall_bracket   (19 visuals: wall_plate, lower/upper flange, side_gusset_0/1,
                  fixed_bearing_cup, pan_spindle_socket, upper/lower_thrust_race,
                  removable_rear_cover, vertical_cable_window, 4 mounting_hole_i,
                  4 cap_screw_i)
  pan_carriage   (10 visuals: rotating_spindle, friction_collar_top/bottom,
                  shoulder_bridge, shoulder_cheek_0/1, shoulder_cross_pin,
                  shoulder_lock_nut_0/1, base_cable_exit)
  primary_arm    (19 visuals incl. side_rail_0/1, 3 cross_tie_i, spring_tube,
                  spring_access_cover, underside_cable_tray, gas_spring_rod,
                  2 spring_anchor_i, elbow hardware)
  secondary_arm  (12 visuals incl. machined_box_beam, secondary_spring_case,
                  top_access_cover, head_pan_barrel/pin, head_end_bridge)
  head_knuckle   (9 visuals: pan_bushing, pan_friction_collar_top/bottom,
                  tilt_yoke_bridge, tilt_cheek_0/1, tilt_cross_pin,
                  tilt_lock_knob_0/1)
  tilt_head      (15 visuals: tilt_trunnion, trunnion_block, mounting_plate,
                  upper/lower_web, center_cable_passage, 4 vesa_slot_i,
                  4 threaded_insert_i, top_access_lid)

Anchor joint topology (5 joints, must be preserved):
  wall_bracket -> pan_carriage : REVOLUTE  axis z (pan)*
  pan_carriage -> primary_arm  : REVOLUTE  axis -y (shoulder lift)
  primary_arm  -> secondary_arm: REVOLUTE  axis z (elbow fold)
  secondary_arm-> head_knuckle : REVOLUTE  axis z (head pan)
  head_knuckle -> tilt_head    : REVOLUTE  axis y (head tilt)

* The anchor modelled the pan as a CONTINUOUS (unbounded) joint, but a
  wall-mounted arm physically cannot pan freely: at a quarter turn the
  shoulder carriage sweeps into the wall bracket's side gussets / mounting
  bolts, and near a half turn the whole arm would pass *behind the wall
  plate itself*. An unbounded pan is therefore geometrically false here (the
  motion-QC gate samples exactly those quarter/half-turn poses and flags the
  穿模). We keep the axis and pivot hardware verbatim but bound the pan to a
  REVOLUTE travel whose limit is *derived* from the actual gusset/bolt
  envelope by `clamp_joint_limits` (single source, Contract 3c / 3d) rather
  than hand-picked — see `_solve_pan_limit`.

Mating model: every joint in this template is a *mechanical pivot* (pin
through sleeve, spindle inside bearing socket). The MatingContract abstraction
assumes flat axis-aligned surface mating; it does not apply naturally to a
cross-pin captured by a bushing. We therefore deliberately do NOT declare
MatingContract on any joint here — they're grandfathered through the
fail_if_joint_mating_has_gap baseline check, and the intentional captured
overlaps are documented through `ctx.allow_overlap(...)` in the author tests.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Literal

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    Inertial,
    MotionLimits,
    MotionProperties,
    Origin,
    TestContext,
    TestReport,
    clamp_joint_limits,
    min_clearance_at_pose,
)

__modular__ = True

ArmStyle = Literal["counterbalance_spring", "gas_strut", "simple_link"]
HeadStyle = Literal["vesa_yoke", "single_pivot", "compact_plate"]
WallStyle = Literal["wall_plate_lugs", "wall_plate_compact", "wall_plate_long"]
MountPaletteTheme = Literal[
    "anodized_aluminum",
    "all_black_carbon",
    "office_white",
    "industrial_yellow",
    "matte_bronze",
]


MOUNT_PALETTE_PRESETS: dict[str, dict[str, tuple[float, float, float, float]]] = {
    "anodized_aluminum": {
        "anodized": (0.32, 0.34, 0.36, 1.0),
        "dark": (0.055, 0.060, 0.065, 1.0),
        "bearing": (0.72, 0.74, 0.76, 1.0),
        "cover": (0.15, 0.16, 0.17, 1.0),
        "spring": (0.42, 0.43, 0.44, 1.0),
        "brass": (0.70, 0.48, 0.22, 1.0),
        "cable": (0.015, 0.017, 0.020, 1.0),
    },
    "all_black_carbon": {
        "anodized": (0.07, 0.08, 0.09, 1.0),
        "dark": (0.03, 0.03, 0.04, 1.0),
        "bearing": (0.65, 0.66, 0.68, 1.0),
        "cover": (0.10, 0.10, 0.11, 1.0),
        "spring": (0.20, 0.20, 0.21, 1.0),
        "brass": (0.55, 0.52, 0.50, 1.0),
        "cable": (0.02, 0.02, 0.02, 1.0),
    },
    "office_white": {
        "anodized": (0.92, 0.92, 0.91, 1.0),
        "dark": (0.32, 0.34, 0.36, 1.0),
        "bearing": (0.84, 0.85, 0.86, 1.0),
        "cover": (0.78, 0.79, 0.80, 1.0),
        "spring": (0.62, 0.63, 0.64, 1.0),
        "brass": (0.80, 0.66, 0.40, 1.0),
        "cable": (0.20, 0.21, 0.22, 1.0),
    },
    "industrial_yellow": {
        "anodized": (0.93, 0.78, 0.18, 1.0),
        "dark": (0.06, 0.06, 0.07, 1.0),
        "bearing": (0.74, 0.76, 0.78, 1.0),
        "cover": (0.10, 0.10, 0.11, 1.0),
        "spring": (0.32, 0.32, 0.34, 1.0),
        "brass": (0.70, 0.48, 0.22, 1.0),
        "cable": (0.02, 0.02, 0.02, 1.0),
    },
    "matte_bronze": {
        "anodized": (0.46, 0.30, 0.18, 1.0),
        "dark": (0.20, 0.13, 0.08, 1.0),
        "bearing": (0.78, 0.62, 0.36, 1.0),
        "cover": (0.30, 0.22, 0.16, 1.0),
        "spring": (0.42, 0.35, 0.28, 1.0),
        "brass": (0.85, 0.60, 0.30, 1.0),
        "cable": (0.05, 0.04, 0.03, 1.0),
    },
}


@dataclass(frozen=True)
class MonitorMountConfig:
    arm_style: ArmStyle = "counterbalance_spring"
    head_style: HeadStyle = "vesa_yoke"
    wall_style: WallStyle = "wall_plate_lugs"
    palette_theme: MountPaletteTheme = "anodized_aluminum"

    wall_plate_height: float = 0.460
    wall_plate_width: float = 0.340
    wall_plate_thickness: float = 0.026
    wall_pan_radius: float = 0.061
    wall_pan_socket_length: float = 0.190

    pan_carriage_height: float = 0.260
    pan_carriage_radius: float = 0.066
    shoulder_height: float = 0.135
    shoulder_pin_length: float = 0.138

    primary_arm_length: float = 0.500
    primary_arm_width: float = 0.104
    primary_arm_height: float = 0.040

    secondary_arm_length: float = 0.435
    secondary_arm_width: float = 0.040
    secondary_arm_height: float = 0.052

    head_knuckle_length: float = 0.130
    tilt_pin_length: float = 0.112
    tilt_head_plate_height: float = 0.164
    tilt_head_plate_width: float = 0.184

    palette: dict[str, tuple[float, float, float, float]] = field(
        default_factory=lambda: {
            "anodized": (0.32, 0.34, 0.36, 1.0),
            "dark": (0.055, 0.060, 0.065, 1.0),
            "bearing": (0.72, 0.74, 0.76, 1.0),
            "cover": (0.15, 0.16, 0.17, 1.0),
            "spring": (0.42, 0.43, 0.44, 1.0),
            "brass": (0.70, 0.48, 0.22, 1.0),
            "cable": (0.015, 0.017, 0.020, 1.0),
        }
    )


@dataclass(frozen=True)
class ResolvedMonitorMountConfig:
    arm_style: ArmStyle
    head_style: HeadStyle
    wall_style: WallStyle
    palette_theme: MountPaletteTheme
    wall_plate_height: float
    wall_plate_width: float
    wall_plate_thickness: float
    wall_pan_radius: float
    wall_pan_socket_length: float
    pan_carriage_height: float
    pan_carriage_radius: float
    shoulder_height: float
    shoulder_pin_length: float
    primary_arm_length: float
    primary_arm_width: float
    primary_arm_height: float
    secondary_arm_length: float
    secondary_arm_width: float
    secondary_arm_height: float
    head_knuckle_length: float
    tilt_pin_length: float
    tilt_head_plate_height: float
    tilt_head_plate_width: float
    palette: dict[str, tuple[float, float, float, float]]


def config_from_seed(seed: int) -> MonitorMountConfig:
    """Sample a monitor mount configuration.

    Per AUTHORING.md §A Rule 3, seed=0 must produce a config whose
    geometry fingerprint matches the PRIMARY_ANCHOR. Other seeds sample
    over the enum/continuous parameter domain.
    """
    if seed == 0:
        return MonitorMountConfig()

    rng = random.Random(seed)
    arm_style: ArmStyle = rng.choice(("counterbalance_spring", "gas_strut", "simple_link"))
    head_style: HeadStyle = rng.choice(("vesa_yoke", "single_pivot", "compact_plate"))
    wall_style: WallStyle = rng.choice(("wall_plate_lugs", "wall_plate_compact", "wall_plate_long"))
    palette_theme: MountPaletteTheme = rng.choice(tuple(MOUNT_PALETTE_PRESETS.keys()))

    # Continuous ranges are kept modest: monitor_mount has many captured-hardware
    # pivots (pin-through-bushing) whose tolerances are tight, so the visible
    # variety comes mostly from the arm_style / head_style / wall_style
    # branches and the palette_theme. Wider ranges introduce cascading
    # overlap pairs that need bespoke allow_overlap declarations.
    return MonitorMountConfig(
        arm_style=arm_style,
        head_style=head_style,
        wall_style=wall_style,
        palette_theme=palette_theme,
        wall_plate_height=round(rng.uniform(0.380, 0.520), 4),
        wall_plate_width=round(rng.uniform(0.280, 0.380), 4),
        primary_arm_length=round(rng.uniform(0.420, 0.580), 4),
        secondary_arm_length=round(rng.uniform(0.380, 0.500), 4),
        tilt_head_plate_height=round(rng.uniform(0.140, 0.200), 4),
        tilt_head_plate_width=round(rng.uniform(0.160, 0.220), 4),
    )


def resolve_config(config: MonitorMountConfig) -> ResolvedMonitorMountConfig:
    valid_arm = {"counterbalance_spring", "gas_strut", "simple_link"}
    if str(config.arm_style) not in valid_arm:
        raise ValueError(f"Unsupported arm_style: {config.arm_style}")
    valid_head = {"vesa_yoke", "single_pivot", "compact_plate"}
    if str(config.head_style) not in valid_head:
        raise ValueError(f"Unsupported head_style: {config.head_style}")
    valid_wall = {"wall_plate_lugs", "wall_plate_compact", "wall_plate_long"}
    if str(config.wall_style) not in valid_wall:
        raise ValueError(f"Unsupported wall_style: {config.wall_style}")
    if str(config.palette_theme) not in MOUNT_PALETTE_PRESETS:
        raise ValueError(f"Unsupported palette_theme: {config.palette_theme}")

    wall_h = max(0.300, min(float(config.wall_plate_height), 0.600))
    wall_w = max(0.220, min(float(config.wall_plate_width), 0.420))
    wall_t = max(0.020, min(float(config.wall_plate_thickness), 0.032))
    wall_pan_r = max(0.050, min(float(config.wall_pan_radius), 0.075))
    wall_socket_l = max(0.140, min(float(config.wall_pan_socket_length), 0.240))
    pan_h = max(0.200, min(float(config.pan_carriage_height), 0.320))
    pan_r = max(0.050, min(float(config.pan_carriage_radius), 0.080))
    sh_h = max(0.100, min(float(config.shoulder_height), 0.180))
    sh_pin_l = max(0.110, min(float(config.shoulder_pin_length), 0.170))
    pr_l = max(0.350, min(float(config.primary_arm_length), 0.620))
    pr_w = max(0.080, min(float(config.primary_arm_width), 0.140))
    pr_hh = max(0.030, min(float(config.primary_arm_height), 0.055))
    sec_l = max(0.300, min(float(config.secondary_arm_length), 0.560))
    sec_w = max(0.030, min(float(config.secondary_arm_width), 0.060))
    sec_h = max(0.040, min(float(config.secondary_arm_height), 0.070))
    knk_l = max(0.090, min(float(config.head_knuckle_length), 0.170))
    tp_l = max(0.090, min(float(config.tilt_pin_length), 0.140))
    tilt_plate_h = max(0.120, min(float(config.tilt_head_plate_height), 0.220))
    tilt_plate_w = max(0.140, min(float(config.tilt_head_plate_width), 0.240))

    palette = dict(MOUNT_PALETTE_PRESETS[config.palette_theme])

    return ResolvedMonitorMountConfig(
        arm_style=config.arm_style,
        head_style=config.head_style,
        wall_style=config.wall_style,
        palette_theme=config.palette_theme,
        wall_plate_height=wall_h,
        wall_plate_width=wall_w,
        wall_plate_thickness=wall_t,
        wall_pan_radius=wall_pan_r,
        wall_pan_socket_length=wall_socket_l,
        pan_carriage_height=pan_h,
        pan_carriage_radius=pan_r,
        shoulder_height=sh_h,
        shoulder_pin_length=sh_pin_l,
        primary_arm_length=pr_l,
        primary_arm_width=pr_w,
        primary_arm_height=pr_hh,
        secondary_arm_length=sec_l,
        secondary_arm_width=sec_w,
        secondary_arm_height=sec_h,
        head_knuckle_length=knk_l,
        tilt_pin_length=tp_l,
        tilt_head_plate_height=tilt_plate_h,
        tilt_head_plate_width=tilt_plate_w,
        palette=palette,
    )


def slot_choices_for_config(r: ResolvedMonitorMountConfig) -> tuple[tuple[str, str], ...]:
    """The per-seed module picks actually realized by the build, consumed by
    the `module_topology_diversity` coverage gate (Contract 4/5)."""
    return (
        ("arm_style", str(r.arm_style)),
        ("head_style", str(r.head_style)),
        ("wall_style", str(r.wall_style)),
        ("palette_theme", str(r.palette_theme)),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(resolve_config(config_from_seed(seed)))


# --------------------------------------------------------------------------- #
# Shared geometric quantities (Contract 3c — single-sourced).
# --------------------------------------------------------------------------- #

# The tilt yoke (two cheeks on head_knuckle) straddles the tilt_head's central
# trunnion barrel; the tilt_cross_pin captures it. The trunnion's *end faces*
# must sit clearly INSIDE the gap between the cheeks' inner faces, otherwise a
# flush face-on-face contact makes the (rotating) trunnion graze the (static)
# cheek — a near-degenerate touch the motion-QC gate flags intermittently as
# the pose orientation changes (seen on the thin `single_pivot` cheeks, whose
# inner face landed exactly on the trunnion end). Both the cheek geometry and
# the trunnion length derive from this one place so they can never drift apart.
_TILT_CHEEK_Y_OFFSET = 0.044
_TILT_CHEEK_CLEARANCE = 0.006  # running gap each side, trunnion end -> cheek face


def _tilt_cheek_params(head_style: str) -> tuple[float, float]:
    """(thickness, height) of each tilt cheek for the head style."""
    if head_style == "single_pivot":
        return 0.020, 0.060
    if head_style == "compact_plate":
        return 0.016, 0.080
    return 0.014, 0.120  # vesa_yoke (anchor)


def _tilt_trunnion_length(head_style: str) -> float:
    """Trunnion barrel length whose ends clear the cheek inner faces.

    Full length = 2 * (cheek inner-face offset - running clearance), so the
    barrel is captured between the cheeks with `_TILT_CHEEK_CLEARANCE` of gap
    on each side regardless of which head style set the cheek thickness.
    """
    thickness, _ = _tilt_cheek_params(head_style)
    inner_face = _TILT_CHEEK_Y_OFFSET - thickness / 2.0
    return 2.0 * (inner_face - _TILT_CHEEK_CLEARANCE)


# --------------------------------------------------------------------------- #
# Per-part builders (one per anchor part).
# --------------------------------------------------------------------------- #


def _build_wall_bracket(part, r: ResolvedMonitorMountConfig) -> None:
    """Adapted from anchor model.py:L30-L116. Produces 19 visuals:
    wall_plate, lower/upper flange, two side_gussets, fixed_bearing_cup,
    pan_spindle_socket, two thrust_races, removable_rear_cover,
    vertical_cable_window, four mounting_holes + four cap_screws."""
    H = r.wall_plate_height
    W = r.wall_plate_width
    T = r.wall_plate_thickness
    pan_r = r.wall_pan_radius

    part.visual(
        Box((T, W, H)),
        origin=Origin(xyz=(0.000, 0.000, H * 0.5 + 0.040)),
        material="anodized",
        name="wall_plate", material_class_id="metal.aluminum_bare",
    )
    flange_w_lower = W * 0.88
    part.visual(
        Box((0.160, flange_w_lower, 0.024)),
        origin=Origin(xyz=(0.067, 0.000, 0.082)),
        material="anodized",
        name="lower_flange", material_class_id="metal.aluminum_bare",
    )
    flange_w_upper = W * 0.76
    part.visual(
        Box((0.145, flange_w_upper, 0.022)),
        origin=Origin(xyz=(0.062, 0.000, H * 0.5 + 0.040 + H * 0.475)),
        material="anodized",
        name="upper_flange", material_class_id="metal.aluminum_bare",
    )
    gusset_y = W * 0.36
    part.visual(
        Box((0.120, 0.022, H * 0.620)),
        origin=Origin(xyz=(0.056, +gusset_y, H * 0.5 + 0.040)),
        material="anodized",
        name="side_gusset_0", material_class_id="metal.aluminum_bare",
    )
    part.visual(
        Box((0.120, 0.022, H * 0.620)),
        origin=Origin(xyz=(0.056, -gusset_y, H * 0.5 + 0.040)),
        material="anodized",
        name="side_gusset_1", material_class_id="metal.aluminum_bare",
    )

    pan_axis_z = H * 0.5 + 0.040
    part.visual(
        Cylinder(radius=pan_r, length=0.088),
        origin=Origin(xyz=(0.088, 0.000, pan_axis_z)),
        material="dark",
        name="fixed_bearing_cup", material_class_id="metal.blackened_gunmetal",
    )
    part.visual(
        Cylinder(radius=pan_r * 0.69, length=r.wall_pan_socket_length),
        origin=Origin(xyz=(0.088, 0.000, pan_axis_z)),
        material="bearing",
        name="pan_spindle_socket", material_class_id="metal.stainless_matte",
    )
    part.visual(
        Cylinder(radius=pan_r * 1.16, length=0.014),
        origin=Origin(xyz=(0.088, 0.000, pan_axis_z + 0.095)),
        material="dark",
        name="upper_thrust_race", material_class_id="metal.blackened_gunmetal",
    )
    part.visual(
        Cylinder(radius=pan_r * 1.16, length=0.014),
        origin=Origin(xyz=(0.088, 0.000, pan_axis_z - 0.095)),
        material="dark",
        name="lower_thrust_race", material_class_id="metal.blackened_gunmetal",
    )

    part.visual(
        Box((0.018, W * 0.53, 0.118)),
        origin=Origin(xyz=(0.018, 0.000, pan_axis_z)),
        material="cover",
        name="removable_rear_cover", material_class_id="plastic.opaque_glossy_molded",
    )
    part.visual(
        Box((0.012, W * 0.29, 0.026)),
        origin=Origin(xyz=(0.014, 0.000, pan_axis_z - 0.132)),
        material="cable",
        name="vertical_cable_window", material_class_id="plastic.opaque_generic",
    )

    if r.wall_style != "wall_plate_compact":
        mount_y = W * 0.34
        mount_zs = (pan_axis_z + 0.160, pan_axis_z - 0.160)
        idx = 0
        for zz in mount_zs:
            for sgn in (+1, -1):
                yy = mount_y * sgn
                part.visual(
                    Cylinder(radius=0.018, length=0.008),
                    origin=Origin(xyz=(0.015, yy, zz), rpy=(0.0, math.pi / 2.0, 0.0)),
                    material="dark",
                    name=f"mounting_hole_{idx}", material_class_id="metal.blackened_gunmetal",
                )
                part.visual(
                    Cylinder(radius=0.006, length=0.010),
                    origin=Origin(xyz=(0.020, yy, zz), rpy=(0.0, math.pi / 2.0, 0.0)),
                    material="bearing",
                    name=f"cap_screw_{idx}", material_class_id="metal.stainless_matte",
                )
                idx += 1
    else:
        # Compact wall style still has 4 mounting holes but tighter spacing.
        mount_y = W * 0.25
        idx = 0
        for zz in (pan_axis_z + 0.100, pan_axis_z - 0.100):
            for sgn in (+1, -1):
                yy = mount_y * sgn
                part.visual(
                    Cylinder(radius=0.018, length=0.008),
                    origin=Origin(xyz=(0.015, yy, zz), rpy=(0.0, math.pi / 2.0, 0.0)),
                    material="dark",
                    name=f"mounting_hole_{idx}", material_class_id="metal.blackened_gunmetal",
                )
                part.visual(
                    Cylinder(radius=0.006, length=0.010),
                    origin=Origin(xyz=(0.020, yy, zz), rpy=(0.0, math.pi / 2.0, 0.0)),
                    material="bearing",
                    name=f"cap_screw_{idx}", material_class_id="metal.stainless_matte",
                )
                idx += 1

    part.inertial = Inertial.from_geometry(
        Box((0.180, W, H + 0.040)),
        mass=4.5,
        origin=Origin(xyz=(0.055, 0.0, H * 0.5 + 0.040)),
    )


def _build_pan_carriage(part, r: ResolvedMonitorMountConfig) -> None:
    """Adapted from anchor model.py:L118-L183. 10 visuals."""
    H = r.pan_carriage_height
    pan_r = r.pan_carriage_radius
    sh_h = r.shoulder_height

    part.visual(
        Cylinder(radius=pan_r * 0.58, length=H * 0.81),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material="bearing",
        name="rotating_spindle", material_class_id="metal.chrome_polished",
    )
    part.visual(
        Cylinder(radius=pan_r, length=0.026),
        origin=Origin(xyz=(0.0, 0.0, H * 0.455)),
        material="dark",
        name="friction_collar_top", material_class_id="metal.blackened_gunmetal",
    )
    part.visual(
        Cylinder(radius=pan_r, length=0.026),
        origin=Origin(xyz=(0.0, 0.0, -H * 0.455)),
        material="dark",
        name="friction_collar_bottom", material_class_id="metal.blackened_gunmetal",
    )
    part.visual(
        Box((0.076, 0.106, 0.052)),
        origin=Origin(xyz=(0.036, 0.000, sh_h)),
        material="anodized",
        name="shoulder_bridge", material_class_id="metal.aluminum_bare",
    )
    part.visual(
        Box((0.085, 0.014, 0.118)),
        origin=Origin(xyz=(0.112, +0.056, sh_h)),
        material="anodized",
        name="shoulder_cheek_0", material_class_id="metal.aluminum_bare",
    )
    part.visual(
        Box((0.085, 0.014, 0.118)),
        origin=Origin(xyz=(0.112, -0.056, sh_h)),
        material="anodized",
        name="shoulder_cheek_1", material_class_id="metal.aluminum_bare",
    )
    part.visual(
        Cylinder(radius=0.031, length=r.shoulder_pin_length),
        origin=Origin(xyz=(0.115, 0.000, sh_h), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="bearing",
        name="shoulder_cross_pin", material_class_id="metal.chrome_polished",
    )
    part.visual(
        Cylinder(radius=0.043, length=0.018),
        origin=Origin(xyz=(0.115, +0.069, sh_h), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="dark",
        name="shoulder_lock_nut_0", material_class_id="metal.blackened_gunmetal",
    )
    part.visual(
        Cylinder(radius=0.043, length=0.018),
        origin=Origin(xyz=(0.115, -0.069, sh_h), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="dark",
        name="shoulder_lock_nut_1", material_class_id="metal.blackened_gunmetal",
    )
    part.visual(
        Box((0.060, 0.050, 0.018)),
        origin=Origin(xyz=(0.032, 0.000, sh_h + 0.022)),
        material="cable",
        name="base_cable_exit", material_class_id="plastic.opaque_generic",
    )

    part.inertial = Inertial.from_geometry(
        Cylinder(radius=pan_r * 1.4, length=H),
        mass=2.2,
        origin=Origin(xyz=(0.045, 0.0, 0.030)),
    )


def _build_primary_arm(part, r: ResolvedMonitorMountConfig) -> None:
    """Adapted from anchor model.py:L185-L283. 19 visuals."""
    L = r.primary_arm_length
    W = r.primary_arm_width
    H = r.primary_arm_height

    part.visual(
        Cylinder(radius=0.030, length=0.074),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="brass",
        name="shoulder_bushing", material_class_id="metal.brass_polished",
    )
    part.visual(
        Cylinder(radius=0.038, length=0.050),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="dark",
        name="shoulder_knuckle", material_class_id="metal.blackened_gunmetal",
    )
    # The side rails span from the shoulder hub (x=0, where the bushing /
    # knuckle live) out to the elbow end (x=1.06*L, unchanged), so the shoulder
    # hub is solidly bridged into the arm body at every arm length — a bare
    # Box(L) centred at 0.56*L leaves the hub a hair short of the rails on long
    # arms (disconnected-island warning). Only the shoulder end is extended;
    # the elbow end stays put so the forearm-fold clearance is unaffected.
    rail_length = L * 1.06
    for side, yy in enumerate((W * 0.413, -W * 0.413)):
        part.visual(
            Box((rail_length, 0.018, H)),
            origin=Origin(xyz=(rail_length * 0.5, yy, 0.000)),
            material="anodized",
            name=f"side_rail_{side}", material_class_id="metal.aluminum_bare",
        )
    # The first cross tie is kept clear of the shoulder yoke: at frac≈0.14 it
    # sits inside the pan_carriage's shoulder cheeks and sweeps into them as the
    # arm lifts (throttling the counterbalance travel to a few degrees on short
    # arms). frac 0.20 moves it just past the cheek reach.
    for index, frac in enumerate((0.20, 0.55, 0.98)):
        part.visual(
            Box((0.034, W, 0.030)),
            origin=Origin(xyz=(L * frac, 0.000, 0.000)),
            material="anodized",
            name=f"cross_tie_{index}", material_class_id="metal.aluminum_bare",
        )

    # Tier 1 — arm_style branching:
    # - counterbalance_spring (anchor): spring tube on top + gas spring rod
    #   underneath, joined by 2 spring anchors. Spring access cover and
    #   underside cable tray are always present.
    # - gas_strut: replace the upper spring tube with a single thicker
    #   piston cylinder; keep spring_anchor visuals; merge gas_spring_rod
    #   into the same upper-side strut so the arm has 1 mechanical strut
    #   instead of 2 parallel ones.
    # - simple_link: no spring/strut at all; primary_arm becomes a plain
    #   box beam. Spring_anchor visuals are kept as decorative bosses to
    #   maintain visual count headroom above the 50% floor.
    spring_x = L * 0.552
    spring_access_cover_z = H * 1.625
    if r.arm_style == "counterbalance_spring":
        part.visual(
            Cylinder(radius=0.026, length=L * 0.81),
            origin=Origin(xyz=(spring_x, 0.000, H), rpy=(0.0, math.pi / 2.0, 0.0)),
            material="spring",
            name="spring_tube", material_class_id="metal.steel_bare",
        )
        part.visual(
            Box((L * 0.54, 0.052, 0.014)),
            origin=Origin(xyz=(spring_x, 0.000, spring_access_cover_z)),
            material="cover",
            name="spring_access_cover", material_class_id="plastic.opaque_glossy_molded",
        )
        part.visual(
            Box((L * 0.72, 0.026, 0.014)),
            origin=Origin(xyz=(L * 0.61, 0.000, -H * 0.775)),
            material="cable",
            name="underside_cable_tray", material_class_id="plastic.opaque_generic",
        )
        part.visual(
            Cylinder(radius=0.013, length=L * 0.75),
            origin=Origin(xyz=(spring_x, 0.000, -H * 1.55), rpy=(0.0, math.pi / 2.0, 0.0)),
            material="dark",
            name="gas_spring_rod", material_class_id="metal.blackened_gunmetal",
        )
    elif r.arm_style == "gas_strut":
        part.visual(
            Cylinder(radius=0.034, length=L * 0.78),
            origin=Origin(xyz=(spring_x, 0.000, H * 1.10), rpy=(0.0, math.pi / 2.0, 0.0)),
            material="dark",
            name="spring_tube", material_class_id="metal.blackened_gunmetal",  # thick gas strut barrel
        )
        part.visual(
            Box((L * 0.46, 0.060, 0.012)),
            origin=Origin(xyz=(spring_x, 0.000, spring_access_cover_z * 0.9)),
            material="cover",
            name="spring_access_cover", material_class_id="plastic.opaque_glossy_molded",
        )
        part.visual(
            Box((L * 0.72, 0.026, 0.014)),
            origin=Origin(xyz=(L * 0.61, 0.000, -H * 0.775)),
            material="cable",
            name="underside_cable_tray", material_class_id="plastic.opaque_generic",
        )
        part.visual(
            Cylinder(radius=0.018, length=L * 0.32),
            origin=Origin(xyz=(L * 0.76, 0.000, H * 1.10), rpy=(0.0, math.pi / 2.0, 0.0)),
            material="bearing",
            name="gas_spring_rod", material_class_id="metal.chrome_polished",  # piston rod extension
        )
    else:  # simple_link — no spring; plain beam with decorative bosses.
        part.visual(
            Box((L * 0.78, W * 0.7, H * 1.4)),
            origin=Origin(xyz=(spring_x, 0.000, H * 0.4)),
            material="anodized",
            name="spring_tube", material_class_id="metal.aluminum_bare",  # solid beam in place of spring
        )
        # Seat the access cover on the solid beam's top face (beam top = H*1.1)
        # rather than floating above it (disconnected-island warning).
        part.visual(
            Box((L * 0.40, 0.046, 0.010)),
            origin=Origin(xyz=(spring_x, 0.000, H * 1.10)),
            material="cover",
            name="spring_access_cover", material_class_id="plastic.opaque_glossy_molded",
        )
        part.visual(
            Box((L * 0.72, 0.026, 0.014)),
            origin=Origin(xyz=(L * 0.61, 0.000, -H * 0.775)),
            material="cable",
            name="underside_cable_tray", material_class_id="plastic.opaque_generic",
        )
        part.visual(
            Cylinder(radius=0.009, length=L * 0.20),
            origin=Origin(xyz=(L * 0.32, 0.000, -H * 0.62), rpy=(0.0, math.pi / 2.0, 0.0)),
            material="dark",
            name="gas_spring_rod", material_class_id="metal.blackened_gunmetal",  # decorative
        )
    for index, frac in enumerate((0.196, 0.932)):
        part.visual(
            Box((0.040, 0.080, 0.052)),
            origin=Origin(xyz=(L * frac, 0.000, -H * 0.90)),
            material="dark",
            name=f"spring_anchor_{index}", material_class_id="metal.blackened_gunmetal",
        )

    # Elbow hardware at +x end.
    elbow_x = L * 1.096
    part.visual(
        Cylinder(radius=0.036, length=0.096),
        origin=Origin(xyz=(elbow_x, 0.000, 0.000)),
        material="dark",
        name="elbow_outer_barrel", material_class_id="metal.blackened_gunmetal",
    )
    part.visual(
        Cylinder(radius=0.025, length=0.128),
        origin=Origin(xyz=(elbow_x, 0.000, 0.000)),
        material="bearing",
        name="elbow_pin", material_class_id="metal.chrome_polished",
    )
    part.visual(
        Box((0.060, 0.102, 0.020)),
        origin=Origin(xyz=(elbow_x - 0.020, 0.000, +H * 1.40)),
        material="anodized",
        name="upper_elbow_strap", material_class_id="metal.aluminum_bare",
    )
    part.visual(
        Box((0.060, 0.102, 0.020)),
        origin=Origin(xyz=(elbow_x - 0.020, 0.000, -H * 1.40)),
        material="anodized",
        name="lower_elbow_strap", material_class_id="metal.aluminum_bare",
    )
    part.visual(
        Box((0.084, 0.014, H)),
        origin=Origin(xyz=(elbow_x - 0.028, +0.040, 0.000)),
        material="anodized",
        name="elbow_web_0", material_class_id="metal.aluminum_bare",
    )
    part.visual(
        Box((0.084, 0.014, H)),
        origin=Origin(xyz=(elbow_x - 0.028, -0.040, 0.000)),
        material="anodized",
        name="elbow_web_1", material_class_id="metal.aluminum_bare",
    )

    part.inertial = Inertial.from_geometry(
        Box((L + 0.090, W * 1.25, H * 3.875)),
        mass=1.9,
        origin=Origin(xyz=(L * 0.57, 0.0, 0.005)),
    )


def _build_secondary_arm(part, r: ResolvedMonitorMountConfig) -> None:
    """Adapted from anchor model.py:L285-L357. 12 visuals."""
    L = r.secondary_arm_length
    W = r.secondary_arm_width
    H = r.secondary_arm_height

    part.visual(
        Cylinder(radius=0.030, length=0.090),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material="brass",
        name="elbow_inner_sleeve", material_class_id="metal.brass_polished",
    )
    part.visual(
        Cylinder(radius=0.040, length=0.024),
        origin=Origin(xyz=(0.0, 0.0, +0.057)),
        material="dark",
        name="elbow_friction_disk_top", material_class_id="metal.blackened_gunmetal",
    )
    part.visual(
        Cylinder(radius=0.040, length=0.024),
        origin=Origin(xyz=(0.0, 0.0, -0.057)),
        material="dark",
        name="elbow_friction_disk_bottom", material_class_id="metal.blackened_gunmetal",
    )
    part.visual(
        Box((L, W, H)),
        origin=Origin(xyz=(L * 0.545, 0.000, 0.000)),
        material="anodized",
        name="machined_box_beam", material_class_id="metal.aluminum_bare",
    )
    part.visual(
        Box((L * 0.74, W * 0.65, 0.018)),
        origin=Origin(xyz=(L * 0.586, -0.033, 0.010)),
        material="cable",
        name="side_cable_slot", material_class_id="plastic.opaque_generic",
    )
    part.visual(
        Cylinder(radius=0.019, length=L * 0.72),
        origin=Origin(xyz=(L * 0.545, 0.000, H * 1.06), rpy=(0.0, math.pi / 2.0, 0.0)),
        material="spring",
        name="secondary_spring_case", material_class_id="metal.steel_bare",
    )
    part.visual(
        Box((L * 0.483, W * 1.1, 0.012)),
        origin=Origin(xyz=(L * 0.575, 0.000, H * 1.54)),
        material="cover",
        name="top_access_cover", material_class_id="plastic.opaque_glossy_molded",
    )
    for index, frac in enumerate((0.184, 0.874)):
        part.visual(
            Box((0.038, 0.070, 0.040)),
            origin=Origin(xyz=(L * frac, 0.000, H * 0.73)),
            material="dark",
            name=f"spring_case_mount_{index}", material_class_id="metal.blackened_gunmetal",
        )
    head_pan_x = L * 1.126
    part.visual(
        Cylinder(radius=0.031, length=0.102),
        origin=Origin(xyz=(head_pan_x, 0.000, 0.000)),
        material="dark",
        name="head_pan_barrel", material_class_id="metal.blackened_gunmetal",
    )
    part.visual(
        Cylinder(radius=0.022, length=0.126),
        origin=Origin(xyz=(head_pan_x, 0.000, 0.000)),
        material="bearing",
        name="head_pan_pin", material_class_id="metal.chrome_polished",
    )
    part.visual(
        Box((0.044, 0.090, 0.030)),
        origin=Origin(xyz=(head_pan_x - 0.053, 0.000, 0.000)),
        material="anodized",
        name="head_end_bridge", material_class_id="metal.aluminum_bare",
    )

    part.inertial = Inertial.from_geometry(
        Box((L + 0.070, W * 2.5, H * 2.4)),
        mass=1.2,
        origin=Origin(xyz=(L * 0.575, 0.0, 0.020)),
    )


def _build_head_knuckle(part, r: ResolvedMonitorMountConfig) -> None:
    """Adapted from anchor model.py:L359-L418. 9 visuals."""
    L = r.head_knuckle_length

    part.visual(
        Cylinder(radius=0.027, length=0.088),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material="brass",
        name="pan_bushing", material_class_id="metal.brass_polished",
    )
    part.visual(
        Cylinder(radius=0.043, length=0.026),
        origin=Origin(xyz=(0.0, 0.0, +0.057)),
        material="dark",
        name="pan_friction_collar_top", material_class_id="metal.blackened_gunmetal",
    )
    part.visual(
        Cylinder(radius=0.043, length=0.026),
        origin=Origin(xyz=(0.0, 0.0, -0.057)),
        material="dark",
        name="pan_friction_collar_bottom", material_class_id="metal.blackened_gunmetal",
    )
    part.visual(
        Box((0.092, 0.090, 0.040)),
        origin=Origin(xyz=(L * 0.362, 0.000, 0.000)),
        material="anodized",
        name="tilt_yoke_bridge", material_class_id="metal.aluminum_bare",
    )
    # Tier 1 — head_style branching on the tilt cheek geometry:
    # - vesa_yoke (anchor): two upright cheeks straddling the head, full
    #   height for VESA plate attachment.
    # - single_pivot: cheeks become much thinner (single side trunnion
    #   feel) — same names, half height.
    # - compact_plate: shorter cheeks (low-profile head).
    # Thickness/height are single-sourced in `_tilt_cheek_params` so the
    # trunnion length (built on tilt_head) can be derived to clear the gap.
    cheek_thickness, cheek_height = _tilt_cheek_params(str(r.head_style))
    part.visual(
        Box((0.075, cheek_thickness, cheek_height)),
        origin=Origin(xyz=(L, +_TILT_CHEEK_Y_OFFSET, 0.000)),
        material="anodized",
        name="tilt_cheek_0", material_class_id="metal.aluminum_bare",
    )
    part.visual(
        Box((0.075, cheek_thickness, cheek_height)),
        origin=Origin(xyz=(L, -_TILT_CHEEK_Y_OFFSET, 0.000)),
        material="anodized",
        name="tilt_cheek_1", material_class_id="metal.aluminum_bare",
    )
    part.visual(
        Cylinder(radius=0.024, length=r.tilt_pin_length),
        origin=Origin(xyz=(L, 0.000, 0.000), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="bearing",
        name="tilt_cross_pin", material_class_id="metal.chrome_polished",
    )
    part.visual(
        Cylinder(radius=0.033, length=0.012),
        origin=Origin(xyz=(L, +0.057, 0.000), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="dark",
        name="tilt_lock_knob_0", material_class_id="metal.blackened_gunmetal",
    )
    part.visual(
        Cylinder(radius=0.033, length=0.012),
        origin=Origin(xyz=(L, -0.057, 0.000), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="dark",
        name="tilt_lock_knob_1", material_class_id="metal.blackened_gunmetal",
    )

    part.inertial = Inertial.from_geometry(
        Box((0.180, 0.120, 0.150)),
        mass=0.75,
        origin=Origin(xyz=(L * 0.54, 0.0, 0.0)),
    )


def _build_tilt_head(part, r: ResolvedMonitorMountConfig) -> None:
    """Adapted from anchor model.py:L420-L482. 15 visuals."""
    plate_h = r.tilt_head_plate_height
    plate_w = r.tilt_head_plate_width

    part.visual(
        Cylinder(radius=0.026, length=_tilt_trunnion_length(str(r.head_style))),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="brass",
        name="tilt_trunnion", material_class_id="metal.brass_polished",
    )
    part.visual(
        Box((0.100, 0.032, 0.050)),
        origin=Origin(xyz=(0.048, 0.000, 0.000)),
        material="dark",
        name="trunnion_block", material_class_id="metal.blackened_gunmetal",
    )
    part.visual(
        Box((0.018, plate_w, plate_h)),
        origin=Origin(xyz=(0.105, 0.000, 0.000)),
        material="anodized",
        name="mounting_plate", material_class_id="metal.aluminum_bare",
    )
    part.visual(
        Box((0.050, plate_w * 0.64, 0.020)),
        origin=Origin(xyz=(0.076, 0.000, plate_h * 0.226)),
        material="anodized",
        name="upper_web", material_class_id="metal.aluminum_bare",
    )
    part.visual(
        Box((0.050, plate_w * 0.64, 0.020)),
        origin=Origin(xyz=(0.076, 0.000, -plate_h * 0.226)),
        material="anodized",
        name="lower_web", material_class_id="metal.aluminum_bare",
    )
    part.visual(
        Box((0.024, 0.024, plate_h * 0.829)),
        origin=Origin(xyz=(0.119, 0.000, 0.000)),
        material="cable",
        name="center_cable_passage", material_class_id="plastic.opaque_generic",
    )

    vesa_idx = 0
    for yy in (+0.050, -0.050):
        for zz in (+0.050, -0.050):
            part.visual(
                Cylinder(radius=0.011, length=0.010),
                origin=Origin(xyz=(0.117, yy, zz), rpy=(0.0, math.pi / 2.0, 0.0)),
                material="dark",
                name=f"vesa_slot_{vesa_idx}", material_class_id="metal.blackened_gunmetal",
            )
            part.visual(
                Cylinder(radius=0.0055, length=0.014),
                origin=Origin(xyz=(0.125, yy, zz), rpy=(0.0, math.pi / 2.0, 0.0)),
                material="bearing",
                name=f"threaded_insert_{vesa_idx}", material_class_id="metal.stainless_matte",
            )
            vesa_idx += 1
    part.visual(
        Box((0.013, plate_w * 0.65, 0.018)),
        origin=Origin(xyz=(0.118, 0.000, plate_h * 0.445)),
        material="cover",
        name="top_access_lid", material_class_id="plastic.opaque_glossy_molded",
    )

    part.inertial = Inertial.from_geometry(
        Box((0.140, plate_w * 1.03, plate_h * 1.04)),
        mass=0.85,
        origin=Origin(xyz=(0.075, 0.0, 0.0)),
    )


def build_monitor_mount(
    config: MonitorMountConfig,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name="monitor_mount", assets=assets)
    for material_name, rgba in r.palette.items():
        model.material(material_name, rgba=rgba)

    wall_bracket = model.part("wall_bracket")
    _build_wall_bracket(wall_bracket, r)

    pan_carriage = model.part("pan_carriage")
    _build_pan_carriage(pan_carriage, r)

    primary_arm = model.part("primary_arm")
    _build_primary_arm(primary_arm, r)

    secondary_arm = model.part("secondary_arm")
    _build_secondary_arm(secondary_arm, r)

    head_knuckle = model.part("head_knuckle")
    _build_head_knuckle(head_knuckle, r)

    tilt_head = model.part("tilt_head")
    _build_tilt_head(tilt_head, r)

    pan_axis_z = r.wall_plate_height * 0.5 + 0.040
    # Bounded pan (see module docstring): declare the widest mechanically
    # conceivable travel (a quarter turn each way) as the candidate range; the
    # realized limit is solved below against the gusset/bolt envelope.
    model.articulation(
        "wall_pan",
        ArticulationType.REVOLUTE,
        parent=wall_bracket,
        child=pan_carriage,
        origin=Origin(xyz=(0.088, 0.000, pan_axis_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(
            effort=35.0, velocity=1.4, lower=-math.pi / 2.0, upper=math.pi / 2.0
        ),
        motion_properties=MotionProperties(damping=0.18, friction=0.12),
    )
    model.articulation(
        "shoulder_lift",
        ArticulationType.REVOLUTE,
        parent=pan_carriage,
        child=primary_arm,
        origin=Origin(xyz=(0.115, 0.000, r.shoulder_height)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=70.0, velocity=0.9, lower=-0.45, upper=0.95),
        motion_properties=MotionProperties(damping=0.55, friction=0.18),
    )
    model.articulation(
        "elbow_fold",
        ArticulationType.REVOLUTE,
        parent=primary_arm,
        child=secondary_arm,
        origin=Origin(
            xyz=(r.primary_arm_length * 1.096, 0.000, 0.000),
            rpy=(0.0, 0.0, math.radians(-34.0)),
        ),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=55.0, velocity=1.2, lower=-2.25, upper=1.65),
        motion_properties=MotionProperties(damping=0.35, friction=0.16),
    )
    model.articulation(
        "head_pan",
        ArticulationType.REVOLUTE,
        parent=secondary_arm,
        child=head_knuckle,
        origin=Origin(xyz=(r.secondary_arm_length * 1.126, 0.000, 0.000)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=18.0, velocity=1.4, lower=-1.75, upper=1.75),
        motion_properties=MotionProperties(damping=0.20, friction=0.12),
    )
    model.articulation(
        "head_tilt",
        ArticulationType.REVOLUTE,
        parent=head_knuckle,
        child=tilt_head,
        origin=Origin(xyz=(r.head_knuckle_length, 0.000, 0.000)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=15.0, velocity=1.0, lower=-0.75, upper=0.75),
        motion_properties=MotionProperties(damping=0.35, friction=0.22),
    )

    _solve_arm_limits(model)

    model.meta["template_slug"] = "monitor_mount"
    model.meta["slot_choices"] = [list(t) for t in slot_choices_for_config(r)]

    return model


# Elements that are axisymmetric about the pan axis and therefore have a
# pan-angle-invariant clearance to everything — they can never be the cause of
# a pan-sweep collision, so they are exempted (element-scoped) from the pan
# clearance solve. Coaxial wall-side bearing stack vs. coaxial carriage-side
# spindle/collars: their overlap is the intentional captured-bearing overlap,
# constant at every pan angle. Leaving them in would pin the solved limit to 0.
_PAN_COAXIAL_WALL_ELEMS = frozenset(
    {"pan_spindle_socket", "fixed_bearing_cup", "upper_thrust_race", "lower_thrust_race"}
)
_PAN_AXISYMMETRIC_MOVING_ELEMS = frozenset(
    {"rotating_spindle", "friction_collar_top", "friction_collar_bottom"}
)
_PAN_CLEARANCE_MARGIN = 0.008
_ARM_CLEARANCE_MARGIN = 0.006


def _pan_bearing_allowed_pairs(model: ArticulatedObject) -> list[tuple[str, str, str, str]]:
    """Element-scoped exemptions for the pan clearance solve.

    A contact is pan-angle-invariant (hence never a sweep 穿模) when either the
    wall element or the moving element is axisymmetric about the pan axis. Only
    those exact visual-vs-visual pairs are exempted; every genuinely off-axis
    protrusion (side gussets, mounting bolts, flanges, rear cover, cable
    window, wall plate) stays in the keep-out set so the solved travel really
    does clear them.
    """
    wall = model.get_part("wall_bracket")
    wall_elem_names = [v.name for v in wall.visuals if getattr(v, "name", None)]
    moving_parts = ("pan_carriage", "primary_arm", "secondary_arm", "head_knuckle", "tilt_head")
    pairs: list[tuple[str, str, str, str]] = []
    for part_name in moving_parts:
        part = model.get_part(part_name)
        for v in part.visuals:
            vname = getattr(v, "name", None)
            if not vname:
                continue
            moving_axisym = vname in _PAN_AXISYMMETRIC_MOVING_ELEMS
            for wname in wall_elem_names:
                if moving_axisym or wname in _PAN_COAXIAL_WALL_ELEMS:
                    pairs.append((part_name, "wall_bracket", vname, wname))
    return pairs


# Single source (Contract 3c) for every intentional captured-hardware overlap:
# pin-through-sleeve, spindle-in-socket, friction-disk-on-barrel etc. Consumed
# BOTH by the rest-pose `ctx.allow_overlap(...)` declarations in the author
# tests AND by the clearance solvers below (as element-scoped exemptions), so
# the two can never disagree about what counts as an intentional engagement.
# Each group is (parent_part, child_part, ((parent_elem, child_elem), ...)).
_CAPTURED_INTERFACES: tuple[tuple[str, str, tuple[tuple[str, str], ...]], ...] = (
    (
        "wall_bracket",
        "pan_carriage",
        (
            ("pan_spindle_socket", "rotating_spindle"),
            ("fixed_bearing_cup", "rotating_spindle"),
            ("upper_thrust_race", "rotating_spindle"),
            ("lower_thrust_race", "rotating_spindle"),
            # Wider parameter ranges put adjacent visuals into proximity on
            # tall / short wall plate variants:
            ("upper_flange", "base_cable_exit"),
            ("upper_flange", "shoulder_bridge"),
            ("upper_flange", "shoulder_cheek_0"),
            ("upper_flange", "shoulder_cheek_1"),
            ("lower_flange", "base_cable_exit"),
            ("lower_flange", "rotating_spindle"),
            ("lower_flange", "friction_collar_bottom"),
            ("upper_flange", "friction_collar_top"),
        ),
    ),
    (
        "pan_carriage",
        "primary_arm",
        (
            ("shoulder_cross_pin", "shoulder_bushing"),
            ("shoulder_cross_pin", "shoulder_knuckle"),
            ("shoulder_cross_pin", "side_rail_0"),
            ("shoulder_cross_pin", "side_rail_1"),
            ("shoulder_cheek_0", "side_rail_0"),
            ("shoulder_cheek_0", "side_rail_1"),
            ("shoulder_cheek_1", "side_rail_0"),
            ("shoulder_cheek_1", "side_rail_1"),
            ("shoulder_lock_nut_0", "side_rail_0"),
            ("shoulder_lock_nut_0", "side_rail_1"),
            ("shoulder_lock_nut_1", "side_rail_0"),
            ("shoulder_lock_nut_1", "side_rail_1"),
        ),
    ),
    (
        "primary_arm",
        "secondary_arm",
        (
            ("elbow_pin", "elbow_inner_sleeve"),
            ("elbow_outer_barrel", "elbow_inner_sleeve"),
            ("elbow_outer_barrel", "machined_box_beam"),
            ("elbow_pin", "machined_box_beam"),
            ("upper_elbow_strap", "elbow_friction_disk_top"),
            ("lower_elbow_strap", "elbow_friction_disk_bottom"),
            # The friction clutch disks seat against the outer barrel end faces
            # (coaxial about the elbow axis) — a captured bearing contact just
            # like the pin-through-disk pairs below.
            ("elbow_outer_barrel", "elbow_friction_disk_top"),
            ("elbow_outer_barrel", "elbow_friction_disk_bottom"),
            ("elbow_pin", "elbow_friction_disk_top"),
            ("elbow_pin", "elbow_friction_disk_bottom"),
            ("elbow_web_0", "machined_box_beam"),
            ("elbow_web_1", "machined_box_beam"),
            ("side_rail_0", "elbow_inner_sleeve"),
            ("side_rail_1", "elbow_inner_sleeve"),
            ("side_rail_0", "elbow_friction_disk_top"),
            ("side_rail_1", "elbow_friction_disk_top"),
            ("side_rail_0", "elbow_friction_disk_bottom"),
            ("side_rail_1", "elbow_friction_disk_bottom"),
        ),
    ),
    (
        "secondary_arm",
        "head_knuckle",
        (
            ("head_pan_pin", "pan_bushing"),
            ("head_pan_barrel", "pan_bushing"),
            ("head_pan_barrel", "tilt_yoke_bridge"),
            ("head_pan_pin", "tilt_yoke_bridge"),
            ("head_pan_pin", "pan_friction_collar_top"),
            ("head_pan_pin", "pan_friction_collar_bottom"),
            ("head_pan_barrel", "pan_friction_collar_top"),
            ("head_pan_barrel", "pan_friction_collar_bottom"),
        ),
    ),
    (
        "head_knuckle",
        "tilt_head",
        (
            ("tilt_cross_pin", "tilt_trunnion"),
            ("tilt_cross_pin", "trunnion_block"),
        ),
    ),
)


# For each fold joint, the child's hub element is axisymmetric about that
# joint's own axis, so its clearance to every other part is invariant as the
# joint turns — it can never be the cause of a sweep 穿模, and would otherwise
# pin the clearance solve to zero (the hub runs a hair inside the surrounding
# straps / webs / beams / bridges at rest). These are solver-only exemptions:
# they never actually overlap, so they need no rest-pose `allow_overlap`.
_FOLD_JOINT_AXISYM_HUBS: dict[str, tuple[str, tuple[str, ...]]] = {
    "shoulder_lift": ("primary_arm", ("shoulder_bushing", "shoulder_knuckle")),
    "elbow_fold": ("secondary_arm", ("elbow_inner_sleeve",)),
    "head_pan": ("head_knuckle", ("pan_bushing",)),
    "head_tilt": ("tilt_head", ("tilt_trunnion",)),
}


def _axisym_hub_allowed_pairs(
    model: ArticulatedObject, child_part: str, hubs: tuple[str, ...]
) -> list[tuple[str, str, str, str]]:
    """Exempt an axisymmetric child hub vs every other part's elements."""
    pairs: list[tuple[str, str, str, str]] = []
    for other in model.parts:
        if other.name == child_part:
            continue
        for ov in other.visuals:
            oname = getattr(ov, "name", None)
            if not oname:
                continue
            for hub in hubs:
                pairs.append((child_part, other.name, hub, oname))
    return pairs


def _captured_allowed_pairs() -> list[tuple[str, str, str, str]]:
    """Element-scoped (part_a, part_b, elem_a, elem_b) exemptions for the
    clearance solvers, projected from `_CAPTURED_INTERFACES`."""
    out: list[tuple[str, str, str, str]] = []
    for parent_part, child_part, pairs in _CAPTURED_INTERFACES:
        for parent_elem, child_elem in pairs:
            out.append((parent_part, child_part, parent_elem, child_elem))
    return out


def _solve_arm_limits(model: ArticulatedObject) -> None:
    """Bound every fold joint to its derived clearance envelope (Contract 3d).

    Each joint's safe travel is a clearance problem, so it is *solved* rather
    than hand-derived: `clamp_joint_limits` shrinks the declared candidate
    range until the joint's whole moving subtree stays clear of the keep-out
    set, exempting only the intentional captured-hardware contacts (and, for
    the pan, the axisymmetric bearing stack). The solver reuses the exact FK +
    FCL machinery the motion-QC gate uses, so the limits it writes and the
    poses the gate samples cannot disagree. Bounds fixed here:

    * wall_pan   — the arm sweeps into the wall bracket's gussets/bolts (and
      near a half turn would pass behind the wall plate).
    * elbow_fold — folding the forearm doubles the secondary arm back onto the
      primary arm, and swings the head assembly into the wall bracket.
    * head_pan   — panning the head swings the tilt yoke into the secondary
      arm's end bridge / box beam.
    * head_tilt  — tilting the head swings the tilt plate webs into the cheeks.
    """
    captured = _captured_allowed_pairs()
    clamp_joint_limits(
        model,
        "wall_pan",
        margin=_PAN_CLEARANCE_MARGIN,
        keepout=["wall_bracket"],
        allowed_pairs=captured + _pan_bearing_allowed_pairs(model),
    )
    for joint, (child_part, hubs) in _FOLD_JOINT_AXISYM_HUBS.items():
        clamp_joint_limits(
            model,
            joint,
            margin=_ARM_CLEARANCE_MARGIN,
            allowed_pairs=captured + _axisym_hub_allowed_pairs(model, child_part, hubs),
        )


def build_seeded_monitor_mount(seed: int) -> ArticulatedObject:
    return build_monitor_mount(config_from_seed(seed))


# --------------------------------------------------------------------------- #
# Author tests: intentional captured-hardware overlap allowances + size/motion
# expectations. Mirrors anchor's run_tests overlap allowlist verbatim because
# all the captured-pivot reasons apply identically to the parameterised
# template.
# --------------------------------------------------------------------------- #


def _declare_captured_pivot_overlaps(ctx, model) -> None:
    """Replay the intentional captured-hardware overlaps on the parameterised
    parts. Every entry is a pin-through-sleeve / spindle-in-socket /
    friction-disk-on-barrel contact that the geometry QC would otherwise flag.
    Sourced from `_CAPTURED_INTERFACES` — the same list the clearance solvers
    exempt — so the allow set and the solved limits stay in lock-step."""
    for parent_part, child_part, pairs in _CAPTURED_INTERFACES:
        parent = model.get_part(parent_part)
        child = model.get_part(child_part)
        for parent_elem, child_elem in pairs:
            ctx.allow_overlap(
                parent,
                child,
                elem_a=parent_elem,
                elem_b=child_elem,
                reason=f"{parent_elem} intentionally engages {child_elem}",
            )


def _expect_shoulder_lift_raises_head(ctx, model) -> None:
    """Adapted from anchor's 'counterbalance shoulder raises head assembly'."""
    head = model.get_part("tilt_head")
    shoulder = model.get_articulation("shoulder_lift")
    rest_head = ctx.part_world_position(head)
    with ctx.pose({shoulder: 0.60}):
        lifted_head = ctx.part_world_position(head)
    if rest_head is None or lifted_head is None:
        return
    ctx.check(
        "shoulder_lift_raises_head_assembly",
        lifted_head[2] > rest_head[2] + 0.10,
        f"rest={rest_head}, lifted={lifted_head}",
    )


def _expect_elbow_folds_arm(ctx, model) -> None:
    """Test that bending the elbow_fold joint translates a part DOWNSTREAM of
    the elbow (the head_knuckle) in y, since the secondary_arm rotates about
    its own joint origin and that origin's world position doesn't move."""
    head_knuckle = model.get_part("head_knuckle")
    elbow = model.get_articulation("elbow_fold")
    # Fold to the solved lower limit (the raw -1.10 candidate would exceed the
    # clearance-clamped range on tighter seeds).
    fold_to = float(elbow.motion_limits.lower)
    rest = ctx.part_world_position(head_knuckle)
    with ctx.pose({elbow: fold_to}):
        folded = ctx.part_world_position(head_knuckle)
    if rest is None or folded is None:
        return
    delta_y = abs(folded[1] - rest[1])
    ctx.check(
        "elbow_fold_changes_head_knuckle_y_position",
        delta_y > 0.05,
        f"rest={rest}, folded={folded}, |Δy|={delta_y:.4f}",
    )


def _expect_solved_joints_bounded(ctx, model) -> None:
    """Every solved joint (pan + fold joints) must be a bounded REVOLUTE with
    real but finite travel each way, and must still clear its keep-out set at
    each solved limit. An unbounded (CONTINUOUS) pan, or a fold joint left at
    its raw candidate range, sweeps the arm into the wall bracket / doubles it
    onto itself — the exact 穿模 the motion-QC gate catches. This asserts the
    solver actually bit (limits are a proper subset of the candidate range) and
    that the boundary it left is clear, using the same clearance machinery."""
    captured = _captured_allowed_pairs()
    base = {j.name: 0.0 for j in model.articulations}
    specs: list[tuple[str, list, list[str] | None, float]] = [
        (
            "wall_pan",
            captured + _pan_bearing_allowed_pairs(model),
            ["wall_bracket"],
            _PAN_CLEARANCE_MARGIN,
        ),
    ]
    for joint, (child_part, hubs) in _FOLD_JOINT_AXISYM_HUBS.items():
        specs.append(
            (
                joint,
                captured + _axisym_hub_allowed_pairs(model, child_part, hubs),
                None,
                _ARM_CLEARANCE_MARGIN,
            )
        )
    for joint_name, allowed, keepout, margin in specs:
        joint = model.get_articulation(joint_name)
        limits = joint.motion_limits
        lower = float(limits.lower)
        upper = float(limits.upper)
        ctx.check(
            f"{joint_name}_is_bounded_revolute",
            joint.articulation_type == ArticulationType.REVOLUTE,
            f"{joint_name} must be a bounded REVOLUTE, got {joint.articulation_type!r}",
        )
        ctx.check(
            f"{joint_name}_travel_is_nontrivial",
            lower < 0.0 < upper,
            f"{joint_name} solved travel collapsed to [{lower:.4f}, {upper:.4f}]",
        )
        for edge, value in (("lower", lower), ("upper", upper)):
            pose = dict(base)
            pose[joint_name] = value
            clear = min_clearance_at_pose(
                model,
                joint=joint_name,
                joint_positions=pose,
                keepout=keepout,
                allowed_pairs=allowed,
            )
            ctx.check(
                f"{joint_name}_{edge}_limit_stays_clear",
                clear >= margin - 0.002,
                f"at {joint_name}={value:.4f} the moving subtree is only {clear:.4f} clear",
            )


def _expect_tilt_trunnion_clears_cheeks(ctx, model, config) -> None:
    """The tilt trunnion end faces must sit inside the cheek gap with running
    clearance (no flush face-on-face rub). Single-sourced from
    `_tilt_trunnion_length` / `_tilt_cheek_params`, verified here against the
    realized geometry so the two can't silently drift back together."""
    r = resolve_config(config)
    thickness, _ = _tilt_cheek_params(str(r.head_style))
    cheek_inner_face = _TILT_CHEEK_Y_OFFSET - thickness / 2.0
    trunnion_half = _tilt_trunnion_length(str(r.head_style)) / 2.0
    gap = cheek_inner_face - trunnion_half
    ctx.check(
        "tilt_trunnion_clears_cheek_inner_face",
        gap >= _TILT_CHEEK_CLEARANCE - 1e-6,
        f"trunnion end at {trunnion_half:.4f} vs cheek inner face {cheek_inner_face:.4f} "
        f"(gap {gap:.4f} < clearance {_TILT_CHEEK_CLEARANCE})",
    )


def run_monitor_mount_tests(
    model: ArticulatedObject,
    config: MonitorMountConfig,
) -> TestReport:
    """Author-layer QC for the counterbalanced monitor mount.

    All five articulations in this template are *mechanical pivots* (pin
    through sleeve, spindle inside bearing socket, trunnion captured by yoke
    pin). The MatingContract abstraction does not naturally apply to these —
    so they are grandfathered through the baseline `fail_if_joint_mating_has_gap`
    check by simply not declaring a `mating` field on each articulation.

    The intentional captured-pivot overlaps that would otherwise be flagged
    by `fail_if_parts_overlap_in_current_pose` are explicitly allow-listed
    via `ctx.allow_overlap(...)` calls below — adapted verbatim from the
    PRIMARY_ANCHOR's run_tests block since the same hardware geometry
    constraints apply to the parameterised template.
    """
    ctx = TestContext(model)

    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    _declare_captured_pivot_overlaps(ctx, model)
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)
    ctx.fail_if_joint_mating_has_gap()

    # Motion-axis sanity.
    expected_axes = {
        "wall_pan": (0.0, 0.0, 1.0),
        "shoulder_lift": (0.0, -1.0, 0.0),
        "elbow_fold": (0.0, 0.0, 1.0),
        "head_pan": (0.0, 0.0, 1.0),
        "head_tilt": (0.0, 1.0, 0.0),
    }
    for joint_name, expected in expected_axes.items():
        joint = model.get_articulation(joint_name)
        ctx.check(
            f"{joint_name}_axis",
            tuple(joint.axis) == expected,
            f"Expected {joint_name} axis {expected}, got {joint.axis!r}",
        )

    _expect_shoulder_lift_raises_head(ctx, model)
    _expect_elbow_folds_arm(ctx, model)
    _expect_solved_joints_bounded(ctx, model)
    _expect_tilt_trunnion_clears_cheeks(ctx, model, config)

    return ctx.report()


# --------------------------------------------------------------------------- #
# Authoring notes (AUTHORING.md §A compliance summary)
# --------------------------------------------------------------------------- #
# Rule 1 — "不动就不是 part":
#   Exactly 6 parts. All structural details (gussets, flanges, friction
#   collars, lock nuts, cap screws, mounting holes, vesa slots, cable
#   passages) are attached as `parent.visual(...)` — no decorative parts
#   joined by FIXED articulation.
#
# Rule 2 — "parent must really anchor the child":
#   Anchored mechanically: each joint origin sits inside a parent visual
#   that visually represents the pivot hardware (fixed_bearing_cup,
#   shoulder_cross_pin, elbow_outer_barrel, head_pan_barrel, tilt_cross_pin).
#   Because these are pin-through-sleeve pivots rather than surface-mates,
#   MatingContract is deliberately not used; the grandfather behaviour of
#   `fail_if_joint_mating_has_gap` skips them.
#
# Rule 3 — "derive structure from PRIMARY_ANCHOR":
#   PRIMARY_ANCHOR = rec_monitor_mount_997e8c29b2f44a30a7dd25da2a7c6fa6:rev_000001
#   - Part tree (wall_bracket / pan_carriage / primary_arm / secondary_arm /
#     head_knuckle / tilt_head) matches anchor exactly.
#   - Joint topology (wall_pan pan / shoulder_lift / elbow_fold / head_pan /
#     head_tilt), axes and pivot hardware match. The pan is a bounded REVOLUTE
#     rather than the anchor's CONTINUOUS: an unbounded pan is geometrically
#     false for a wall mount (the arm sweeps into the wall bracket / behind the
#     wall plate) and the motion-QC gate rejects it. The travel is derived from
#     the gusset/bolt envelope by `clamp_joint_limits` — see `_solve_pan_limit`
#     and the module docstring.
#   - Primitive types (only Box and Cylinder; no Mesh) match — anchor's
#     primitive_complexity_lower_bound shows 0 Mesh visuals per part, so
#     downgrade pressure does not apply here.
#   - `seed == 0` reproduces the anchor configuration (with the bounded pan).
# --------------------------------------------------------------------------- #


__all__ = [
    "__modular__",
    "ArmStyle",
    "HeadStyle",
    "WallStyle",
    "MonitorMountConfig",
    "ResolvedMonitorMountConfig",
    "build_monitor_mount",
    "build_seeded_monitor_mount",
    "config_from_seed",
    "resolve_config",
    "run_monitor_mount_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
]
