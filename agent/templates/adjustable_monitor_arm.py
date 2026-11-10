# SPDX-License-Identifier: Apache-2.0

"""Adjustable monitor arm procedural template (modular).

__modular__ = True. No single PRIMARY_ANCHOR: structure is composed from per-slot
5-star module sources declared in
`articraft_template_authoring/specs_modular_v1/adjustable_monitor_arm.md`.

Slots (all realized in `slot_choices_for_seed`):
  * support_base  : c_clamp / grommet_mount / freestanding_base / wall_mount
  * arm_skeleton  : single_segment / two_segment / three_segment
  * head_terminal : stamped_vesa_plate / captured_monitor_head
  * riser         : fixed_riser / prismatic_riser
  * n_arms        : 1 / 2 / 3 (multiplicity — full arm subchain copied on a shared pole)

Every module factory adapts a real 5-star source (part tree / joint semantics /
primitive types preserved per AUTHORING §A Rule 3). All joints are captured
mechanical pivots (swivel sleeve on pole, clevis pin through hinge eye, rotation
boss in backplate, prismatic collar on pole); like `monitor_mount.py` these are
grandfathered through `fail_if_joint_mating_has_gap` (no MatingContract) and
their intentional overlaps are element-scoped `allow_overlap`ed in run_tests.

Sources (model.py line refs in the spec):
  A rec_workspace__adjustable_monitor_arm__001 — captured monitor head, two-seg arm
  B rec_workspace__adjustable_monitor_arm__002 — c_clamp + pole, VESA plate, two-seg
  forks: base_grommet / base_freestanding / base_wall / skeleton_single_seg /
         skeleton_three_seg / joint_pole_prismatic / n2 / n3
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Literal

import cadquery as cq

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
)

__modular__ = True

SupportBase = Literal["c_clamp", "grommet_mount", "freestanding_base", "wall_mount"]
ArmSkeleton = Literal["single_segment", "two_segment", "three_segment"]
HeadTerminal = Literal["stamped_vesa_plate", "captured_monitor_head"]
Riser = Literal["fixed_riser", "prismatic_riser"]
PaletteTheme = Literal["satin_silver", "all_black", "office_white"]

_POLED_BASES = ("c_clamp", "grommet_mount", "freestanding_base")
ARM_STAGGER = 0.16  # vertical spacing between stacked arms on a shared pole

# Palette keys: body(shells), dark(hardware), metal(pole/steel), arm(cast shell),
# gloss(monitor shell), glass(screen).
PALETTE_PRESETS: dict[str, dict[str, tuple[float, float, float, float]]] = {
    "satin_silver": {
        "body": (0.015, 0.017, 0.016, 1.0),
        "dark": (0.05, 0.055, 0.052, 1.0),
        "metal": (0.58, 0.64, 0.62, 1.0),
        "arm": (0.56, 0.61, 0.58, 1.0),
        "gloss": (0.10, 0.10, 0.11, 1.0),
        "glass": (0.50, 0.70, 0.72, 0.72),
    },
    "all_black": {
        "body": (0.02, 0.02, 0.02, 1.0),
        "dark": (0.04, 0.04, 0.045, 1.0),
        "metal": (0.22, 0.22, 0.23, 1.0),
        "arm": (0.10, 0.10, 0.11, 1.0),
        "gloss": (0.03, 0.03, 0.035, 1.0),
        "glass": (0.32, 0.42, 0.46, 0.72),
    },
    "office_white": {
        "body": (0.90, 0.90, 0.89, 1.0),
        "dark": (0.32, 0.34, 0.36, 1.0),
        "metal": (0.80, 0.82, 0.83, 1.0),
        "arm": (0.78, 0.79, 0.80, 1.0),
        "gloss": (0.86, 0.86, 0.85, 1.0),
        "glass": (0.55, 0.72, 0.74, 0.72),
    },
}


# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class AdjustableMonitorArmConfig:
    support_base: SupportBase = "c_clamp"
    arm_skeleton: ArmSkeleton = "two_segment"
    head_terminal: HeadTerminal = "stamped_vesa_plate"
    riser: Riser = "fixed_riser"
    palette_theme: PaletteTheme = "satin_silver"
    n_arms: int = 1
    pole_height: float = 0.500
    arm_reach_scale: float = 1.0
    head_size_scale: float = 1.0


@dataclass(frozen=True)
class ResolvedAdjustableMonitorArmConfig:
    support_base: SupportBase
    arm_skeleton: ArmSkeleton
    head_terminal: HeadTerminal
    riser: Riser
    palette_theme: PaletteTheme
    n_arms: int
    pole_height: float
    arm_reach_scale: float
    head_size_scale: float
    # derived
    has_pole: bool
    effective_pole_len: float
    swivel_z: float
    swivel_x: float
    swivel_limit: float
    vesa_rot_limit: float
    palette: dict[str, tuple[float, float, float, float]] = field(default_factory=dict)


def config_from_seed(seed: int) -> AdjustableMonitorArmConfig:
    """Deterministic procedural sampling for every seed, including seed 0
    (modular: no special-cased anchor seed)."""
    rng = random.Random(seed)
    support_base: SupportBase = rng.choice(
        ("c_clamp", "grommet_mount", "freestanding_base", "wall_mount")
    )
    arm_skeleton: ArmSkeleton = rng.choice(
        ("single_segment", "two_segment", "three_segment")
    )
    head_terminal: HeadTerminal = rng.choice(
        ("stamped_vesa_plate", "captured_monitor_head")
    )
    riser: Riser = rng.choice(("fixed_riser", "prismatic_riser"))
    palette_theme: PaletteTheme = rng.choice(tuple(PALETTE_PRESETS.keys()))
    # Multiplicity: small-N heavy.
    n_arms = rng.choices((1, 2, 3), weights=(0.70, 0.20, 0.10), k=1)[0]

    pole_height = round(rng.uniform(0.42, 0.62), 4)
    arm_reach_scale = round(rng.uniform(0.88, 1.14), 4)
    head_size_scale = round(rng.uniform(0.90, 1.14), 4)

    return AdjustableMonitorArmConfig(
        support_base=support_base,
        arm_skeleton=arm_skeleton,
        head_terminal=head_terminal,
        riser=riser,
        palette_theme=palette_theme,
        n_arms=n_arms,
        pole_height=pole_height,
        arm_reach_scale=arm_reach_scale,
        head_size_scale=head_size_scale,
    )


def resolve_config(
    config: AdjustableMonitorArmConfig,
) -> ResolvedAdjustableMonitorArmConfig:
    support_base = str(config.support_base)
    if support_base not in ("c_clamp", "grommet_mount", "freestanding_base", "wall_mount"):
        raise ValueError(f"Unsupported support_base: {support_base}")
    arm_skeleton = str(config.arm_skeleton)
    if arm_skeleton not in ("single_segment", "two_segment", "three_segment"):
        raise ValueError(f"Unsupported arm_skeleton: {arm_skeleton}")
    head_terminal = str(config.head_terminal)
    if head_terminal not in ("stamped_vesa_plate", "captured_monitor_head"):
        raise ValueError(f"Unsupported head_terminal: {head_terminal}")
    riser = str(config.riser)
    if riser not in ("fixed_riser", "prismatic_riser"):
        raise ValueError(f"Unsupported riser: {riser}")
    palette_theme = str(config.palette_theme)
    if palette_theme not in PALETTE_PRESETS:
        raise ValueError(f"Unsupported palette_theme: {palette_theme}")

    has_pole = support_base in _POLED_BASES
    n_arms = max(1, min(int(config.n_arms), 3))

    # --- Compatibility gating (spec §7 conditional). ---
    if not has_pole:  # wall_mount: no pole → single arm, no prismatic riser
        riser = "fixed_riser"
        n_arms = 1
    if n_arms >= 2:
        # Multi-arm stacks directly on the pole and uses the compact VESA plate
        # so stacked heads clear each other.
        riser = "fixed_riser"
        head_terminal = "stamped_vesa_plate"
    if riser == "prismatic_riser":
        n_arms = 1  # single arm rides the sliding collar
    if head_terminal == "captured_monitor_head":
        n_arms = 1  # bulky head → single arm

    pole_height = max(0.42, min(float(config.pole_height), 0.62))
    arm_reach_scale = max(0.88, min(float(config.arm_reach_scale), 1.14))
    head_size_scale = max(0.90, min(float(config.head_size_scale), 1.14))

    # --- Derived geometry (single-sourced). ---
    effective_pole_len = pole_height + (n_arms - 1) * ARM_STAGGER
    if has_pole:
        swivel_z = 0.040 + effective_pole_len  # top-arm mount height on the pole
        swivel_x = 0.0
    else:
        swivel_z = 0.540  # wall stub-tip pivot height (fixed)
        swivel_x = 0.074

    # base_swivel travel: full turn for a lone pole arm; forward arc for a wall
    # arm (a ±π sweep would drive the arm through the wall panel); disjoint
    # azimuth sectors for multi-arm poles so arms never collide.
    if n_arms >= 2:
        swivel_limit = math.pi / n_arms - 0.20
    elif not has_pole:
        swivel_limit = 1.30
    else:
        swivel_limit = math.pi

    # VESA roll: a bare plate spins freely; the bulky monitor head is clamped so
    # its corners never sweep into the arm.
    vesa_rot_limit = math.pi if head_terminal == "stamped_vesa_plate" else 0.85

    return ResolvedAdjustableMonitorArmConfig(
        support_base=support_base,  # type: ignore[arg-type]
        arm_skeleton=arm_skeleton,  # type: ignore[arg-type]
        head_terminal=head_terminal,  # type: ignore[arg-type]
        riser=riser,  # type: ignore[arg-type]
        palette_theme=palette_theme,  # type: ignore[arg-type]
        n_arms=n_arms,
        pole_height=pole_height,
        arm_reach_scale=arm_reach_scale,
        head_size_scale=head_size_scale,
        has_pole=has_pole,
        effective_pole_len=effective_pole_len,
        swivel_z=swivel_z,
        swivel_x=swivel_x,
        swivel_limit=swivel_limit,
        vesa_rot_limit=vesa_rot_limit,
        palette=dict(PALETTE_PRESETS[palette_theme]),
    )


def slot_choices_for_config(
    r: ResolvedAdjustableMonitorArmConfig,
) -> tuple[tuple[str, str], ...]:
    return (
        ("support_base", str(r.support_base)),
        ("arm_skeleton", str(r.arm_skeleton)),
        ("head_terminal", str(r.head_terminal)),
        ("riser", str(r.riser)),
        ("n_arms", str(r.n_arms)),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(resolve_config(config_from_seed(seed)))


# --------------------------------------------------------------------------- #
# Mesh helpers (adapted verbatim from the 5-star sources; primitive types kept)
# --------------------------------------------------------------------------- #
def _rounded_box_mesh(length, width, height, radius, name):
    fillet = min(radius, length * 0.18, width * 0.42, height * 0.42)
    shape = cq.Workplane("XY").box(length, width, height).edges().fillet(fillet)
    return mesh_from_cadquery(shape, name, tolerance=0.0009, angular_tolerance=0.1)


def _tube_mesh(outer_radius, inner_radius, length, name):
    outer = cq.Workplane("XY").circle(outer_radius).extrude(length)
    cutter = (
        cq.Workplane("XY")
        .circle(inner_radius)
        .extrude(length * 3.0)
        .translate((0.0, 0.0, -length))
    )
    shape = outer.cut(cutter).translate((0.0, 0.0, -length / 2.0))
    return mesh_from_cadquery(shape, name, tolerance=0.0008, angular_tolerance=0.09)


def _oval_plate_mesh(rx, ry, thickness, name):
    shape = (
        cq.Workplane("XY").ellipse(rx, ry).extrude(thickness).translate((0.0, 0.0, -thickness / 2.0))
    )
    return mesh_from_cadquery(shape, name, tolerance=0.0009, angular_tolerance=0.1)


def _tapered_hub_mesh(top_radius, bottom_radius, height, name):
    shape = (
        cq.Workplane("XY")
        .circle(bottom_radius)
        .workplane(offset=height)
        .circle(top_radius)
        .loft()
        .translate((0.0, 0.0, -height / 2.0))
    )
    return mesh_from_cadquery(shape, name, tolerance=0.0008, angular_tolerance=0.09)


def _hex_prism_mesh(flat_to_flat, thickness, name):
    circ = flat_to_flat / math.cos(math.pi / 6.0)
    shape = (
        cq.Workplane("XY").polygon(6, circ).extrude(thickness).translate((0.0, 0.0, -thickness / 2.0))
    )
    return mesh_from_cadquery(shape, name, tolerance=0.0006, angular_tolerance=0.06)


def _washer_mesh(outer_radius, inner_radius, thickness, name):
    shape = (
        cq.Workplane("XY")
        .circle(outer_radius)
        .circle(inner_radius)
        .extrude(thickness)
        .translate((0.0, 0.0, -thickness / 2.0))
    )
    return mesh_from_cadquery(shape, name, tolerance=0.0008, angular_tolerance=0.09)


# --------------------------------------------------------------------------- #
# Support base modules (Slot A) — one root part "support_base"
# --------------------------------------------------------------------------- #
def _build_support_base(part, r: ResolvedAdjustableMonitorArmConfig) -> None:
    P = r.effective_pole_len
    pole_center_z = 0.074 + P / 2.0
    pole_top_z = 0.074 + P
    base = r.support_base

    def _pole():
        part.visual(
            Cylinder(radius=0.020, length=P),
            origin=Origin(xyz=(0.0, 0.0, pole_center_z)),
            material="metal",
            name="vertical_pole", material_class_id="metal.stainless_matte",
        )
        part.visual(
            Cylinder(radius=0.022, length=0.014),
            origin=Origin(xyz=(0.0, 0.0, pole_top_z - 0.013)),
            material="dark",
            name="thrust_collar", material_class_id="metal.blackened_gunmetal",
        )
        # extra stop collars between stacked arms
        for i in range(1, r.n_arms):
            part.visual(
                Cylinder(radius=0.022, length=0.010),
                origin=Origin(xyz=(0.0, 0.0, r.swivel_z - i * ARM_STAGGER + ARM_STAGGER * 0.5)),
                material="dark",
                name=f"mid_collar_{i}", material_class_id="metal.blackened_gunmetal",
            )

    if base == "c_clamp":  # source B L57-L117
        part.visual(Box((0.18, 0.10, 0.024)), origin=Origin(xyz=(0.0, 0.0, 0.062)),
                    material="body", name="top_saddle", material_class_id="metal.paint_coated")
        part.visual(Box((0.11, 0.025, 0.018)), origin=Origin(xyz=(0.038, 0.038, 0.079), rpy=(0, 0, 0.22)),
                    material="body", name="splayed_foot_0", material_class_id="metal.paint_coated")
        part.visual(Box((0.11, 0.025, 0.018)), origin=Origin(xyz=(0.038, -0.038, 0.079), rpy=(0, 0, -0.22)),
                    material="body", name="splayed_foot_1", material_class_id="metal.paint_coated")
        part.visual(Box((0.045, 0.070, 0.145)), origin=Origin(xyz=(-0.055, 0.0, -0.010)),
                    material="body", name="clamp_spine", material_class_id="metal.paint_coated")
        part.visual(Box((0.130, 0.075, 0.018)), origin=Origin(xyz=(-0.055, 0.0, -0.090)),
                    material="body", name="lower_jaw", material_class_id="metal.paint_coated")
        part.visual(Cylinder(radius=0.008, length=0.092), origin=Origin(xyz=(-0.055, 0.0, -0.145)),
                    material="dark", name="clamp_screw", material_class_id="metal.blackened_gunmetal")
        part.visual(Cylinder(radius=0.026, length=0.010), origin=Origin(xyz=(-0.055, 0.0, -0.195)),
                    material="dark", name="pressure_pad", material_class_id="rubber.smooth_plain")
        part.visual(Cylinder(radius=0.007, length=0.090),
                    origin=Origin(xyz=(-0.055, 0.0, -0.185), rpy=(math.pi / 2, 0, 0)),
                    material="dark", name="thumb_bar", material_class_id="rubber.smooth_plain")
        _pole()
    elif base == "grommet_mount":  # grommet fork L87-L142
        part.visual(Cylinder(radius=0.050, length=0.010), origin=Origin(xyz=(0.0, 0.0, 0.069)),
                    material="body", name="top_plate", material_class_id="metal.paint_coated")
        part.visual(_tube_mesh(0.025, 0.020, 0.012, "pole_socket"),
                    origin=Origin(xyz=(0.0, 0.0, 0.080)), material="dark", name="pole_socket", material_class_id="plastic.opaque_glossy_molded")
        part.visual(Cylinder(radius=0.012, length=0.100), origin=Origin(xyz=(0.0, 0.0, 0.014)),
                    material="dark", name="grommet_stud", material_class_id="metal.blackened_gunmetal")
        part.visual(_washer_mesh(0.038, 0.012, 0.010, "backing_flange"),
                    origin=Origin(xyz=(0.0, 0.0, 0.029)), material="body", name="backing_flange", material_class_id="metal.paint_coated")
        part.visual(_hex_prism_mesh(0.032, 0.014, "lock_nut"),
                    origin=Origin(xyz=(0.0, 0.0, 0.017)), material="dark", name="lock_nut", material_class_id="metal.blackened_gunmetal")
        _pole()
    elif base == "freestanding_base":  # freestanding fork L82-L115
        part.visual(_oval_plate_mesh(0.140, 0.100, 0.022, "base_plate"),
                    origin=Origin(xyz=(0.0, 0.0, 0.011)), material="body", name="base_plate", material_class_id="metal.paint_coated")
        part.visual(_tapered_hub_mesh(0.022, 0.034, 0.052, "pole_hub"),
                    origin=Origin(xyz=(0.0, 0.0, 0.048)), material="body", name="pole_hub", material_class_id="metal.paint_coated")
        for i, (x, y) in enumerate(((0.080, 0.058), (0.080, -0.058), (-0.080, 0.058), (-0.080, -0.058))):
            part.visual(Cylinder(radius=0.012, length=0.003), origin=Origin(xyz=(x, y, -0.001)),
                        material="dark", name=f"rubber_foot_{i}", material_class_id="rubber.smooth_plain")
        _pole()
    else:  # wall_mount fork L58-L114 (pole-less)
        wz = r.swivel_z
        part.visual(Box((0.010, 0.160, 0.220)), origin=Origin(xyz=(0.005, 0.0, wz)),
                    material="body", name="wall_plate_panel", material_class_id="metal.paint_coated")
        for i, (yo, zo) in enumerate(((0.055, 0.080), (0.055, -0.080), (-0.055, 0.080), (-0.055, -0.080))):
            part.visual(Cylinder(radius=0.009, length=0.006),
                        origin=Origin(xyz=(-0.001, yo, wz + zo), rpy=(0, math.pi / 2, 0)),
                        material="metal", name=f"wall_screw_{i}", material_class_id="metal.stainless_matte")
        part.visual(Box((0.014, 0.078, 0.078)), origin=Origin(xyz=(0.017, 0.0, wz)),
                    material="body", name="bracket_flange", material_class_id="metal.paint_coated")
        part.visual(_rounded_box_mesh(0.064, 0.050, 0.050, 0.006, "stub_bracket"),
                    origin=Origin(xyz=(0.042, 0.0, wz)), material="body", name="stub_bracket", material_class_id="metal.paint_coated")
        part.visual(Cylinder(radius=0.020, length=0.100), origin=Origin(xyz=(0.074, 0.0, wz + 0.004)),
                    material="metal", name="swivel_pivot", material_class_id="metal.stainless_matte")
        part.visual(Cylinder(radius=0.034, length=0.014), origin=Origin(xyz=(0.074, 0.0, wz + 0.057)),
                    material="dark", name="thrust_collar", material_class_id="metal.blackened_gunmetal")


def _build_height_slider(part, r: ResolvedAdjustableMonitorArmConfig) -> None:
    """Prismatic riser (Slot D) — collar riding the pole, adapted from the
    joint_pole_prismatic fork L123-L146. Local frame centered on the collar; the
    swivel post sits at local +z so the arm mounts above it."""
    part.visual(_tube_mesh(0.036, 0.020, 0.090, "slider_collar"), material="dark", name="slider_collar", material_class_id="metal.blackened_gunmetal")
    # Lever sits low on the collar (below the arm's swing plane) so a lone
    # single-segment arm's gas-spring link cannot sweep into it at full base_swivel.
    part.visual(Cylinder(radius=0.009, length=0.026),
                origin=Origin(xyz=(-0.038, 0.0, -0.014), rpy=(0, math.pi / 2, 0)),
                material="dark", name="lever_pivot", material_class_id="metal.blackened_gunmetal")
    part.visual(Box((0.006, 0.018, 0.052)), origin=Origin(xyz=(-0.052, 0.0, -0.014)),
                material="body", name="clamp_lever", material_class_id="plastic.opaque_glossy_molded")
    # swivel platform caps the collar top and fuses the thin swivel post to the
    # collar body (post radius < collar bore, so without this disk the post would
    # float in the bore as a disconnected island).
    part.visual(Cylinder(radius=0.030, length=0.012), origin=Origin(xyz=(0.0, 0.0, 0.047)),
                material="dark", name="swivel_platform", material_class_id="metal.blackened_gunmetal")
    # swivel post the arm's swivel sleeve clamps around (captured pivot)
    part.visual(Cylinder(radius=0.014, length=0.070), origin=Origin(xyz=(0.0, 0.0, 0.075)),
                material="metal", name="swivel_post", material_class_id="metal.stainless_matte")


# --------------------------------------------------------------------------- #
# Arm skeleton modules (Slot B). Each emits its parts + internal joints and
# returns wiring info. `p` is the per-arm name prefix ("" for a lone arm).
# `s` is arm_reach_scale (applied to x reach dims only).
# --------------------------------------------------------------------------- #
def _clevis(part, *, x, cheek_y, cheek_size, pin_r, pin_l, bolt_r, bolt_y, prefix,
            shell_end_x, eye_radius):
    # Solid yoke web: part of the arm casting that bridges the arm shell to the
    # clevis cheeks so the {cheeks, pin, bolts} are never a floating island. It
    # runs from inside the shell's flat body out to just short of the child eye
    # (x - eye_radius), overlapping both cheeks in y — all intra-part, so no
    # cross-part overlap allowance is needed. (AUTHORING §A Rule 2 anchoring.)
    web_x1 = x - (eye_radius + 0.003)
    web_x0 = shell_end_x - 0.018
    if web_x1 > web_x0 + 0.004:
        half_y = cheek_y + cheek_size[1] / 2.0
        part.visual(
            Box((web_x1 - web_x0, 2.0 * half_y, 0.044)),
            origin=Origin(xyz=(0.5 * (web_x0 + web_x1), 0.0, 0.0)),
            material="arm", name=f"{prefix}_yoke_web", material_class_id="metal.paint_coated",
        )
    part.visual(Box(cheek_size), origin=Origin(xyz=(x, cheek_y, 0.0)), material="dark", name=f"{prefix}_cheek_0", material_class_id="metal.blackened_gunmetal")
    part.visual(Box(cheek_size), origin=Origin(xyz=(x, -cheek_y, 0.0)), material="dark", name=f"{prefix}_cheek_1", material_class_id="metal.blackened_gunmetal")
    part.visual(Cylinder(radius=pin_r, length=pin_l), origin=Origin(xyz=(x, 0.0, 0.0), rpy=(math.pi / 2, 0, 0)),
                material="dark", name=f"{prefix}_pin", material_class_id="metal.blackened_gunmetal")
    part.visual(Cylinder(radius=bolt_r, length=0.010), origin=Origin(xyz=(x, bolt_y, 0.0), rpy=(math.pi / 2, 0, 0)),
                material="body", name=f"{prefix}_bolt_head_0", material_class_id="metal.paint_coated")
    part.visual(Cylinder(radius=bolt_r, length=0.010), origin=Origin(xyz=(x, -bolt_y, 0.0), rpy=(math.pi / 2, 0, 0)),
                material="body", name=f"{prefix}_bolt_head_1", material_class_id="metal.paint_coated")


def _wrist_yoke_web(part, prefix, *, shell_end_x, wrist_x, cheek_y, cheek_thk, eye_radius):
    """Solid connecting web at the arm tip that fuses the arm shell to the wrist
    clevis cheeks (intra-part; replaces the old low-floating bridge). Stops short
    of the child wrist tilt eye so no cross-part overlap allowance is needed."""
    web_x1 = wrist_x - (eye_radius + 0.003)
    web_x0 = shell_end_x - 0.018
    if web_x1 > web_x0 + 0.004:
        half_y = cheek_y + cheek_thk / 2.0
        part.visual(
            Box((web_x1 - web_x0, 2.0 * half_y, 0.044)),
            origin=Origin(xyz=(0.5 * (web_x0 + web_x1), 0.0, 0.0)),
            material="arm", name=f"{prefix}wrist_yoke_bridge", material_class_id="metal.paint_coated",
        )


def _build_wrist_head(model, p, r):
    wh = model.part(f"{p}wrist_head")
    wh.visual(_tube_mesh(0.022, 0.008, 0.028, f"{p}wrist_tilt_eye"),
              origin=Origin(rpy=(math.pi / 2, 0, 0)), material="dark", name=f"{p}wrist_tilt_eye", material_class_id="metal.blackened_gunmetal")
    wh.visual(_rounded_box_mesh(0.070, 0.036, 0.036, 0.007, f"{p}wrist_neck"),
              origin=Origin(xyz=(0.055, 0.0, 0.0)), material="body", name=f"{p}wrist_neck", material_class_id="metal.paint_coated")
    wh.visual(Cylinder(radius=0.024, length=0.036), origin=Origin(xyz=(0.103, 0.0, 0.0), rpy=(0, math.pi / 2, 0)),
              material="dark", name=f"{p}rotation_bearing", material_class_id="metal.stainless_matte")
    return wh


def _emit_skeleton(model, p, r):
    """Emit the arm-root..wrist_head parts + internal joints. Returns dict with
    root_part name, wrist_head name, and vesa_rotation origin/rpy."""
    s = r.arm_reach_scale
    sk = r.arm_skeleton

    if sk == "single_segment":  # single fork L121-L180
        arm = model.part(f"{p}arm")
        arm.visual(_tube_mesh(0.036, 0.010, 0.092, f"{p}base_swivel_sleeve"),
                   material="metal", name=f"{p}base_swivel_sleeve", material_class_id="metal.stainless_matte")
        arm.visual(_rounded_box_mesh(0.470 * s, 0.054, 0.050, 0.006, f"{p}arm_shell"),
                   origin=Origin(xyz=(0.265 * s, 0.0, 0.0)), material="arm", name=f"{p}arm_shell", material_class_id="metal.paint_coated")
        arm.visual(Box((0.370 * s, 0.018, 0.018)), origin=Origin(xyz=(0.230 * s, 0.0, -0.040)),
                   material="body", name=f"{p}gas_spring_link", material_class_id="metal.paint_coated")
        arm.visual(Box((0.020, 0.022, 0.036)), origin=Origin(xyz=(0.080 * s, 0.0, -0.030)),
                   material="body", name=f"{p}gas_link_mount_0", material_class_id="metal.paint_coated")
        arm.visual(Box((0.020, 0.022, 0.036)), origin=Origin(xyz=(0.400 * s, 0.0, -0.030)),
                   material="body", name=f"{p}gas_link_mount_1", material_class_id="metal.paint_coated")
        arm.visual(Box((0.028, 0.070, 0.008)), origin=Origin(xyz=(0.320 * s, 0.0, -0.028)),
                   material="dark", name=f"{p}cable_clip", material_class_id="plastic.opaque_generic")
        wrist_x = 0.530 * s
        arm.visual(Box((0.064, 0.012, 0.060)), origin=Origin(xyz=(wrist_x, 0.028, 0.0)),
                   material="dark", name=f"{p}wrist_cheek_0", material_class_id="metal.blackened_gunmetal")
        arm.visual(Box((0.064, 0.012, 0.060)), origin=Origin(xyz=(wrist_x, -0.028, 0.0)),
                   material="dark", name=f"{p}wrist_cheek_1", material_class_id="metal.blackened_gunmetal")
        arm.visual(Cylinder(radius=0.008, length=0.078), origin=Origin(xyz=(wrist_x, 0.0, 0.0), rpy=(math.pi / 2, 0, 0)),
                   material="dark", name=f"{p}wrist_pin", material_class_id="metal.blackened_gunmetal")
        _wrist_yoke_web(arm, p, shell_end_x=0.500 * s, wrist_x=wrist_x,
                        cheek_y=0.028, cheek_thk=0.012, eye_radius=0.022)
        wh = _build_wrist_head(model, p, r)
        model.articulation(f"{p}wrist_tilt", ArticulationType.REVOLUTE, parent=arm, child=wh,
                           origin=Origin(xyz=(wrist_x, 0.0, 0.0)), axis=(0, 1, 0),
                           motion_limits=MotionLimits(effort=10, velocity=1.5, lower=-0.65, upper=0.65))
        return {"root": f"{p}arm", "wrist_head": f"{p}wrist_head",
                "vesa_x": 0.120, "vesa_rpy": (0.0, 0.0, 0.0),
                "joints": [f"{p}wrist_tilt"]}

    if sk == "two_segment":  # source B L121-L233
        lower = model.part(f"{p}lower_arm")
        lower.visual(_tube_mesh(0.036, 0.010, 0.092, f"{p}base_swivel_sleeve"),
                     material="metal", name=f"{p}base_swivel_sleeve", material_class_id="metal.stainless_matte")
        lower.visual(_rounded_box_mesh(0.335 * s, 0.052, 0.044, 0.010, f"{p}lower_arm_shell"),
                     origin=Origin(xyz=(0.198 * s, 0.0, 0.0)), material="arm", name=f"{p}lower_arm_shell", material_class_id="metal.paint_coated")
        lower.visual(Box((0.026, 0.070, 0.008)), origin=Origin(xyz=(0.235 * s, 0.0, -0.024)),
                     material="dark", name=f"{p}lower_cable_clip", material_class_id="plastic.opaque_generic")
        elbow_x = 0.400 * s
        _clevis(lower, x=elbow_x, cheek_y=0.032, cheek_size=(0.080, 0.015, 0.076),
                pin_r=0.010, pin_l=0.095, bolt_r=0.006, bolt_y=0.046, prefix=f"{p}elbow",
                shell_end_x=0.3655 * s, eye_radius=0.027)
        upper = model.part(f"{p}upper_arm")
        _emit_upper_two_seg(upper, p, s, eye_name=f"{p}elbow_eye")
        model.articulation(f"{p}elbow_pitch", ArticulationType.REVOLUTE, parent=lower, child=upper,
                           origin=Origin(xyz=(elbow_x, 0.0, 0.0), rpy=(0, -0.42, 0)), axis=(0, 1, 0),
                           motion_limits=MotionLimits(effort=30, velocity=1.0, lower=-0.75, upper=0.85))
        wrist_x = 0.420 * s
        wh = _build_wrist_head(model, p, r)
        model.articulation(f"{p}wrist_tilt", ArticulationType.REVOLUTE, parent=upper, child=wh,
                           origin=Origin(xyz=(wrist_x, 0.0, 0.0)), axis=(0, 1, 0),
                           motion_limits=MotionLimits(effort=10, velocity=1.5, lower=-0.65, upper=0.65))
        return {"root": f"{p}lower_arm", "wrist_head": f"{p}wrist_head",
                "vesa_x": 0.120, "vesa_rpy": (0.0, 0.42, 0.0),
                "joints": [f"{p}elbow_pitch", f"{p}wrist_tilt"]}

    # three_segment — three fork L167-L319
    lower = model.part(f"{p}lower_arm")
    lower.visual(_tube_mesh(0.036, 0.010, 0.092, f"{p}base_swivel_sleeve"),
                 material="metal", name=f"{p}base_swivel_sleeve", material_class_id="metal.stainless_matte")
    lower.visual(_rounded_box_mesh(0.240 * s, 0.052, 0.044, 0.010, f"{p}lower_arm_shell"),
                 origin=Origin(xyz=(0.150 * s, 0.0, 0.0)), material="arm", name=f"{p}lower_arm_shell", material_class_id="metal.paint_coated")
    lower.visual(Box((0.026, 0.070, 0.008)), origin=Origin(xyz=(0.200 * s, 0.0, -0.024)),
                 material="dark", name=f"{p}lower_cable_clip", material_class_id="plastic.opaque_generic")
    elbow_x = 0.320 * s
    _clevis(lower, x=elbow_x, cheek_y=0.032, cheek_size=(0.074, 0.015, 0.076),
            pin_r=0.010, pin_l=0.095, bolt_r=0.006, bolt_y=0.046, prefix=f"{p}elbow",
            shell_end_x=0.270 * s, eye_radius=0.027)
    mid = model.part(f"{p}mid_arm")
    mid.visual(_tube_mesh(0.027, 0.012, 0.035, f"{p}mid_elbow_eye"),
               origin=Origin(rpy=(math.pi / 2, 0, 0)), material="dark", name=f"{p}mid_elbow_eye", material_class_id="metal.blackened_gunmetal")
    # proximal-anchored so the eye stays fused to the shell across arm_reach_scale
    mid.visual(_rounded_box_mesh(0.220 * s, 0.050, 0.046, 0.011, f"{p}mid_arm_shell"),
               origin=Origin(xyz=(0.125 * s, 0.0, 0.0)), material="arm", name=f"{p}mid_arm_shell", material_class_id="metal.paint_coated")
    mid.visual(Box((0.026, 0.066, 0.008)), origin=Origin(xyz=(0.190 * s, 0.0, -0.025)),
               material="dark", name=f"{p}mid_cable_clip", material_class_id="plastic.opaque_generic")
    mid_x = 0.300 * s
    _clevis(mid, x=mid_x, cheek_y=0.030, cheek_size=(0.068, 0.014, 0.070),
            pin_r=0.009, pin_l=0.088, bolt_r=0.006, bolt_y=0.044, prefix=f"{p}mid_fold",
            shell_end_x=0.235 * s, eye_radius=0.025)
    upper = model.part(f"{p}upper_arm")
    upper.visual(_tube_mesh(0.025, 0.011, 0.032, f"{p}mid_fold_eye"),
                 origin=Origin(rpy=(math.pi / 2, 0, 0)), material="dark", name=f"{p}mid_fold_eye", material_class_id="metal.blackened_gunmetal")
    _emit_upper_three_seg(upper, p, s)
    model.articulation(f"{p}elbow_pitch", ArticulationType.REVOLUTE, parent=lower, child=mid,
                       origin=Origin(xyz=(elbow_x, 0.0, 0.0), rpy=(0, -0.30, 0)), axis=(0, 1, 0),
                       motion_limits=MotionLimits(effort=30, velocity=1.0, lower=-0.75, upper=0.85))
    model.articulation(f"{p}mid_fold", ArticulationType.REVOLUTE, parent=mid, child=upper,
                       origin=Origin(xyz=(mid_x, 0.0, 0.0), rpy=(0, -0.25, 0)), axis=(0, 1, 0),
                       motion_limits=MotionLimits(effort=28, velocity=1.0, lower=-0.70, upper=0.80))
    wrist_x = 0.340 * s
    wh = _build_wrist_head(model, p, r)
    model.articulation(f"{p}wrist_tilt", ArticulationType.REVOLUTE, parent=upper, child=wh,
                       origin=Origin(xyz=(wrist_x, 0.0, 0.0)), axis=(0, 1, 0),
                       motion_limits=MotionLimits(effort=10, velocity=1.5, lower=-0.65, upper=0.65))
    return {"root": f"{p}lower_arm", "wrist_head": f"{p}wrist_head",
            "vesa_x": 0.126, "vesa_rpy": (0.0, 0.55, 0.0),
            "joints": [f"{p}elbow_pitch", f"{p}mid_fold", f"{p}wrist_tilt"]}


def _emit_upper_two_seg(upper, p, s, *, eye_name):
    upper.visual(_tube_mesh(0.027, 0.012, 0.035, eye_name),
                 origin=Origin(rpy=(math.pi / 2, 0, 0)), material="dark", name=eye_name, material_class_id="metal.blackened_gunmetal")
    upper.visual(_rounded_box_mesh(0.370 * s, 0.054, 0.052, 0.012, f"{p}upper_arm_shell"),
                 origin=Origin(xyz=(0.205 * s, 0.0, 0.0)), material="arm", name=f"{p}upper_arm_shell", material_class_id="metal.paint_coated")
    upper.visual(Box((0.310 * s, 0.018, 0.018)), origin=Origin(xyz=(0.220 * s, 0.0, -0.047)),
                 material="body", name=f"{p}gas_spring_link", material_class_id="metal.paint_coated")
    upper.visual(Box((0.020, 0.022, 0.036)), origin=Origin(xyz=(0.080 * s, 0.0, -0.032)),
                 material="body", name=f"{p}gas_link_mount_0", material_class_id="metal.paint_coated")
    upper.visual(Box((0.020, 0.022, 0.036)), origin=Origin(xyz=(0.350 * s, 0.0, -0.032)),
                 material="body", name=f"{p}gas_link_mount_1", material_class_id="metal.paint_coated")
    upper.visual(Box((0.028, 0.070, 0.008)), origin=Origin(xyz=(0.280 * s, 0.0, -0.030)),
                 material="dark", name=f"{p}upper_cable_clip", material_class_id="plastic.opaque_generic")
    wrist_x = 0.420 * s
    upper.visual(Box((0.064, 0.012, 0.060)), origin=Origin(xyz=(wrist_x, 0.028, 0.0)),
                 material="dark", name=f"{p}wrist_cheek_0", material_class_id="metal.blackened_gunmetal")
    upper.visual(Box((0.064, 0.012, 0.060)), origin=Origin(xyz=(wrist_x, -0.028, 0.0)),
                 material="dark", name=f"{p}wrist_cheek_1", material_class_id="metal.blackened_gunmetal")
    upper.visual(Cylinder(radius=0.008, length=0.078), origin=Origin(xyz=(wrist_x, 0.0, 0.0), rpy=(math.pi / 2, 0, 0)),
                 material="dark", name=f"{p}wrist_pin", material_class_id="metal.blackened_gunmetal")
    _wrist_yoke_web(upper, p, shell_end_x=0.390 * s, wrist_x=wrist_x,
                    cheek_y=0.028, cheek_thk=0.012, eye_radius=0.022)


def _emit_upper_three_seg(upper, p, s):
    # proximal-anchored so mid_fold_eye stays fused to the shell across scale
    upper.visual(_rounded_box_mesh(0.260 * s, 0.054, 0.052, 0.012, f"{p}upper_arm_shell"),
                 origin=Origin(xyz=(0.145 * s, 0.0, 0.0)), material="arm", name=f"{p}upper_arm_shell", material_class_id="metal.paint_coated")
    upper.visual(Box((0.220 * s, 0.018, 0.018)), origin=Origin(xyz=(0.155 * s, 0.0, -0.047)),
                 material="body", name=f"{p}gas_spring_link", material_class_id="metal.paint_coated")
    upper.visual(Box((0.020, 0.022, 0.036)), origin=Origin(xyz=(0.060 * s, 0.0, -0.032)),
                 material="body", name=f"{p}gas_link_mount_0", material_class_id="metal.paint_coated")
    upper.visual(Box((0.020, 0.022, 0.036)), origin=Origin(xyz=(0.255 * s, 0.0, -0.032)),
                 material="body", name=f"{p}gas_link_mount_1", material_class_id="metal.paint_coated")
    upper.visual(Box((0.028, 0.070, 0.008)), origin=Origin(xyz=(0.200 * s, 0.0, -0.030)),
                 material="dark", name=f"{p}upper_cable_clip", material_class_id="plastic.opaque_generic")
    wrist_x = 0.340 * s
    upper.visual(Box((0.064, 0.012, 0.060)), origin=Origin(xyz=(wrist_x, 0.028, 0.0)),
                 material="dark", name=f"{p}wrist_cheek_0", material_class_id="metal.blackened_gunmetal")
    upper.visual(Box((0.064, 0.012, 0.060)), origin=Origin(xyz=(wrist_x, -0.028, 0.0)),
                 material="dark", name=f"{p}wrist_cheek_1", material_class_id="metal.blackened_gunmetal")
    upper.visual(Cylinder(radius=0.008, length=0.078), origin=Origin(xyz=(wrist_x, 0.0, 0.0), rpy=(math.pi / 2, 0, 0)),
                 material="dark", name=f"{p}wrist_pin", material_class_id="metal.blackened_gunmetal")
    _wrist_yoke_web(upper, p, shell_end_x=0.275 * s, wrist_x=wrist_x,
                    cheek_y=0.028, cheek_thk=0.012, eye_radius=0.022)


# --------------------------------------------------------------------------- #
# Head terminal modules (Slot C)
# --------------------------------------------------------------------------- #
def _build_stamped_vesa_plate(model, p, r):  # source B L259-L288
    hs = r.head_size_scale
    plate = model.part(f"{p}vesa_plate")
    plate.visual(Box((0.010, 0.118 * hs, 0.118 * hs)), material="body", name=f"{p}vesa_backplate", material_class_id="metal.paint_coated")
    ear = 0.052 * hs
    for i, (y, z) in enumerate(((ear, ear), (ear, -ear), (-ear, ear), (-ear, -ear))):
        plate.visual(Cylinder(radius=0.018, length=0.010), origin=Origin(xyz=(0.0, y, z), rpy=(0, math.pi / 2, 0)),
                     material="body", name=f"{p}corner_ear_{i}", material_class_id="metal.paint_coated")
    plate.visual(Cylinder(radius=0.032, length=0.018), origin=Origin(xyz=(0.010, 0.0, 0.0), rpy=(0, math.pi / 2, 0)),
                 material="dark", name=f"{p}center_boss", material_class_id="metal.blackened_gunmetal")
    fst = 0.0375 * hs
    for i, (y, z) in enumerate(((fst, fst), (fst, -fst), (-fst, fst), (-fst, -fst))):
        plate.visual(Cylinder(radius=0.006, length=0.006), origin=Origin(xyz=(0.008, y, z), rpy=(0, math.pi / 2, 0)),
                     material="metal", name=f"{p}vesa_fastener_{i}", material_class_id="metal.stainless_matte")
    return f"{p}vesa_plate", f"{p}vesa_backplate"


def _build_captured_monitor_head(model, p, r):  # origin A L399-L472 (scaled)
    hs = r.head_size_scale
    mh = model.part(f"{p}vesa_mount")
    mh.visual(Cylinder(radius=0.041, length=0.022), origin=Origin(xyz=(0.010, 0.0, 0.0), rpy=(0, math.pi / 2, 0)),
              material="dark", name=f"{p}rotation_boss", material_class_id="metal.blackened_gunmetal")
    mh.visual(Box((0.012, 0.150 * hs, 0.150 * hs)), origin=Origin(xyz=(0.024, 0.0, 0.0)),
              material="body", name=f"{p}vesa_backplate", material_class_id="metal.paint_coated")
    for row, z in enumerate((-0.050 * hs, 0.050 * hs)):
        for col, y in enumerate((-0.050 * hs, 0.050 * hs)):
            mh.visual(Cylinder(radius=0.008, length=0.010), origin=Origin(xyz=(0.035, y, z), rpy=(0, math.pi / 2, 0)),
                      material="metal", name=f"{p}vesa_screw_{row}_{col}", material_class_id="metal.stainless_matte")
            mh.visual(Cylinder(radius=0.0055, length=0.044), origin=Origin(xyz=(0.057, y, z), rpy=(0, math.pi / 2, 0)),
                      material="dark", name=f"{p}vesa_standoff_{row}_{col}", material_class_id="metal.blackened_gunmetal")
    mw = 0.300 * hs
    mht = 0.420 * hs
    mh.visual(Box((0.035, mw, mht)), origin=Origin(xyz=(0.086, 0.0, 0.016)), material="gloss", name=f"{p}monitor_body", material_class_id="plastic.opaque_glossy_molded")
    mh.visual(Box((0.0025, mw * 0.83, mht * 0.85)), origin=Origin(xyz=(0.10475, 0.0, 0.016)),
              material="glass", name=f"{p}screen_inset", material_class_id="glass.smoked_tinted")
    mh.visual(Box((0.005, mw * 0.97, 0.024)), origin=Origin(xyz=(0.106, 0.0, 0.016 + mht * 0.5 - 0.012)),
              material="gloss", name=f"{p}top_bezel", material_class_id="plastic.opaque_glossy_molded")
    mh.visual(Box((0.005, mw * 0.97, 0.028)), origin=Origin(xyz=(0.106, 0.0, 0.016 - mht * 0.5 + 0.014)),
              material="gloss", name=f"{p}bottom_bezel", material_class_id="plastic.opaque_glossy_molded")
    mh.visual(Box((0.005, 0.026, mht)), origin=Origin(xyz=(0.106, -mw * 0.5 + 0.013, 0.016)),
              material="gloss", name=f"{p}side_bezel_0", material_class_id="plastic.opaque_glossy_molded")
    mh.visual(Box((0.005, 0.026, mht)), origin=Origin(xyz=(0.106, mw * 0.5 - 0.013, 0.016)),
              material="gloss", name=f"{p}side_bezel_1", material_class_id="plastic.opaque_glossy_molded")
    for i, y in enumerate((-0.090 * hs, 0.0, 0.090 * hs)):
        mh.visual(Box((0.003, 0.006, mht * 0.95)), origin=Origin(xyz=(0.067, y, 0.016)),
                  material="dark", name=f"{p}rear_rib_{i}", material_class_id="plastic.opaque_generic")
    return f"{p}vesa_mount", f"{p}vesa_backplate"


# --------------------------------------------------------------------------- #
# Plan (single source consumed by build + tests)
# --------------------------------------------------------------------------- #
def _plan(r: ResolvedAdjustableMonitorArmConfig) -> dict:
    arms = []
    n = r.n_arms
    for i in range(n):
        prefix = "" if n == 1 else f"arm{i}_"
        yaw = 0.0 if n == 1 else i * (2.0 * math.pi / n)
        z = r.swivel_z - i * ARM_STAGGER
        arms.append({"prefix": prefix, "yaw": yaw, "z": z})
    return {"arms": arms}


# --------------------------------------------------------------------------- #
# Build
# --------------------------------------------------------------------------- #
def build_adjustable_monitor_arm(
    config: AdjustableMonitorArmConfig,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name="adjustable_monitor_arm", assets=assets)
    for name, rgba in r.palette.items():
        model.material(name, rgba=rgba)

    base = model.part("support_base")
    _build_support_base(base, r)

    plan = _plan(r)

    slider = None
    if r.riser == "prismatic_riser":  # gated to poled single-arm
        slider = model.part("height_slider")
        _build_height_slider(slider, r)
        model.articulation("height_slide", ArticulationType.PRISMATIC, parent=base, child=slider,
                           origin=Origin(xyz=(0.0, 0.0, r.swivel_z - 0.075)), axis=(0, 0, 1),
                           motion_limits=MotionLimits(effort=40, velocity=0.08, lower=-0.18, upper=0.12))

    for arm in plan["arms"]:
        p = arm["prefix"]
        sk = _emit_skeleton(model, p, r)

        if slider is not None:
            swivel_parent = slider
            swivel_origin = Origin(xyz=(0.0, 0.0, 0.075), rpy=(0, 0, arm["yaw"]))  # slider-local post center
        else:
            swivel_parent = base
            swivel_origin = Origin(xyz=(r.swivel_x, 0.0, arm["z"]), rpy=(0, 0, arm["yaw"]))
        model.articulation(f"{p}base_swivel", ArticulationType.REVOLUTE, parent=swivel_parent,
                           child=model.get_part(sk["root"]), origin=swivel_origin, axis=(0, 0, 1),
                           motion_limits=MotionLimits(effort=25, velocity=1.4,
                                                      lower=-r.swivel_limit, upper=r.swivel_limit))

        if r.head_terminal == "stamped_vesa_plate":
            head_part, _ = _build_stamped_vesa_plate(model, p, r)
        else:
            head_part, _ = _build_captured_monitor_head(model, p, r)
        model.articulation(f"{p}vesa_rotation", ArticulationType.REVOLUTE,
                           parent=model.get_part(sk["wrist_head"]), child=model.get_part(head_part),
                           origin=Origin(xyz=(sk["vesa_x"], 0.0, 0.0), rpy=sk["vesa_rpy"]), axis=(1, 0, 0),
                           motion_limits=MotionLimits(effort=8, velocity=2.0,
                                                      lower=-r.vesa_rot_limit, upper=r.vesa_rot_limit))

    model.meta["template_slug"] = "adjustable_monitor_arm"
    model.meta["slot_choices"] = [list(t) for t in slot_choices_for_config(r)]
    return model


def build_seeded_adjustable_monitor_arm(seed: int) -> ArticulatedObject:
    return build_adjustable_monitor_arm(config_from_seed(seed))


# --------------------------------------------------------------------------- #
# Author tests
# --------------------------------------------------------------------------- #
def _captured_pairs(model, r: ResolvedAdjustableMonitorArmConfig):
    """(parent_part, child_part, elem_a, elem_b, reason) captured-pivot overlaps."""
    out = []
    if r.riser == "prismatic_riser":
        out.append(("support_base", "height_slider", "vertical_pole", "slider_collar",
                    "slider collar rides the pole bore as a captured prismatic joint"))
    plan = _plan(r)
    for arm in plan["arms"]:
        p = arm["prefix"]
        sk = r.arm_skeleton
        head_backplate = f"{p}vesa_backplate"
        head_part = f"{p}vesa_plate" if r.head_terminal == "stamped_vesa_plate" else f"{p}vesa_mount"
        wh = f"{p}wrist_head"
        root = f"{p}arm" if sk == "single_segment" else f"{p}lower_arm"
        sleeve = f"{p}base_swivel_sleeve"
        wrist_owner = f"{p}arm" if sk == "single_segment" else f"{p}upper_arm"
        # base_swivel: the collar clamps the pole / pivot / slider post (captured),
        # and the thick collar surrounds any coaxial pole-top collar hardware.
        if r.riser == "prismatic_riser":
            out += [
                ("height_slider", root, "swivel_post", sleeve, "swivel post seats in the arm sleeve bore"),
                ("height_slider", root, "swivel_platform", sleeve, "arm sleeve seats down onto the swivel platform thrust washer"),
                ("height_slider", root, "slider_collar", sleeve, "arm sleeve caps the slider collar"),
                ("support_base", root, "vertical_pole", sleeve, "arm sleeve collar clamps the pole"),
                ("support_base", root, "thrust_collar", sleeve, "arm sleeve surrounds the pole thrust collar"),
                ("support_base", "height_slider", "vertical_pole", "swivel_post", "swivel post is coaxial with the pole"),
                ("support_base", "height_slider", "vertical_pole", "swivel_platform", "pole passes coaxially through the swivel platform"),
                ("support_base", "height_slider", "thrust_collar", "swivel_post", "swivel post reaches the pole thrust collar"),
                ("support_base", "height_slider", "thrust_collar", "swivel_platform", "swivel platform reaches the pole thrust collar"),
                ("support_base", "height_slider", "thrust_collar", "slider_collar", "slider collar reaches the pole thrust collar"),
            ]
        elif not r.has_pole:
            out += [
                ("support_base", root, "swivel_pivot", sleeve, "swivel pivot pin passes through the arm sleeve bore"),
                ("support_base", root, "stub_bracket", sleeve, "the arm sleeve wraps the wall-plate stub bracket"),
                ("support_base", root, "thrust_collar", sleeve, "arm sleeve surrounds the wall thrust collar"),
            ]
        else:
            out += [
                ("support_base", root, "vertical_pole", sleeve, "the arm sleeve collar clamps the vertical pole"),
                ("support_base", root, "thrust_collar", sleeve, "arm sleeve surrounds the pole thrust collar"),
            ]
        if sk == "two_segment":
            lo, up = f"{p}lower_arm", f"{p}upper_arm"
            out += [
                (lo, up, f"{p}elbow_pin", f"{p}elbow_eye", "elbow pin captured through the elbow eye"),
                (lo, up, f"{p}elbow_cheek_0", f"{p}elbow_eye", "elbow eye between the elbow cheeks"),
                (lo, up, f"{p}elbow_cheek_1", f"{p}elbow_eye", "elbow eye between the elbow cheeks"),
                (lo, up, f"{p}elbow_cheek_0", f"{p}upper_arm_shell", "upper arm shell seats between the elbow clevis cheeks"),
                (lo, up, f"{p}elbow_cheek_1", f"{p}upper_arm_shell", "upper arm shell seats between the elbow clevis cheeks"),
            ]
        elif sk == "three_segment":
            lo, mi, up = f"{p}lower_arm", f"{p}mid_arm", f"{p}upper_arm"
            out += [
                (lo, mi, f"{p}elbow_pin", f"{p}mid_elbow_eye", "elbow pin captured through the mid eye"),
                (lo, mi, f"{p}elbow_cheek_0", f"{p}mid_elbow_eye", "mid eye between the elbow cheeks"),
                (lo, mi, f"{p}elbow_cheek_1", f"{p}mid_elbow_eye", "mid eye between the elbow cheeks"),
                (lo, mi, f"{p}elbow_cheek_0", f"{p}mid_arm_shell", "mid arm shell seats between the elbow clevis cheeks"),
                (lo, mi, f"{p}elbow_cheek_1", f"{p}mid_arm_shell", "mid arm shell seats between the elbow clevis cheeks"),
                (mi, up, f"{p}mid_fold_pin", f"{p}mid_fold_eye", "mid-fold pin captured through the fold eye"),
                (mi, up, f"{p}mid_fold_cheek_0", f"{p}mid_fold_eye", "fold eye between the mid-fold cheeks"),
                (mi, up, f"{p}mid_fold_cheek_1", f"{p}mid_fold_eye", "fold eye between the mid-fold cheeks"),
                (mi, up, f"{p}mid_fold_cheek_0", f"{p}upper_arm_shell", "upper arm shell seats between the mid-fold cheeks"),
                (mi, up, f"{p}mid_fold_cheek_1", f"{p}upper_arm_shell", "upper arm shell seats between the mid-fold cheeks"),
            ]
        # wrist clevis (all skeletons): eye/neck captured between the wrist cheeks + yoke
        out += [
            (wrist_owner, wh, f"{p}wrist_pin", f"{p}wrist_tilt_eye", "wrist pin captured through the tilt eye"),
            (wrist_owner, wh, f"{p}wrist_cheek_0", f"{p}wrist_tilt_eye", "tilt eye between the wrist cheeks"),
            (wrist_owner, wh, f"{p}wrist_cheek_1", f"{p}wrist_tilt_eye", "tilt eye between the wrist cheeks"),
            (wrist_owner, wh, f"{p}wrist_cheek_0", f"{p}wrist_neck", "wrist neck pivots between the wrist cheeks"),
            (wrist_owner, wh, f"{p}wrist_cheek_1", f"{p}wrist_neck", "wrist neck pivots between the wrist cheeks"),
            (wrist_owner, wh, f"{p}wrist_yoke_bridge", f"{p}wrist_neck", "wrist neck pivots over the yoke bridge"),
        ]
        out.append((wh, head_part, f"{p}rotation_bearing", head_backplate,
                    "rotation bearing seats into the head backplate as a captured boss"))
        if r.head_terminal == "captured_monitor_head":
            out.append((wh, head_part, f"{p}rotation_bearing", f"{p}rotation_boss",
                        "monitor rotation boss nests into the wrist rotation bearing"))
        else:
            out.append((wh, head_part, f"{p}rotation_bearing", f"{p}center_boss",
                        "plate center boss is coaxial with and nests into the rotation bearing"))
    return out


def _declare_captured_overlaps(ctx, model, r):
    for pa, pb, ea, eb, reason in _captured_pairs(model, r):
        try:
            ctx.allow_overlap(model.get_part(pa), model.get_part(pb), elem_a=ea, elem_b=eb, reason=reason)
        except Exception:
            # part absent for this config → skip (robust to gating)
            continue


def run_adjustable_monitor_arm_tests(
    model: ArticulatedObject,
    config: AdjustableMonitorArmConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)

    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    _declare_captured_overlaps(ctx, model, r)
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)
    ctx.fail_if_joint_mating_has_gap()

    plan = _plan(r)
    for arm in plan["arms"]:
        p = arm["prefix"]
        # axis sanity
        swivel = model.get_articulation(f"{p}base_swivel")
        ctx.check(f"{p}base_swivel_axis_z", tuple(swivel.axis) == (0.0, 0.0, 1.0),
                  f"expected z axis, got {swivel.axis!r}")
        rot = model.get_articulation(f"{p}vesa_rotation")
        ctx.check(f"{p}vesa_rotation_axis_x", tuple(rot.axis) == (1.0, 0.0, 0.0),
                  f"expected x axis, got {rot.axis!r}")

        head_part = model.get_part(f"{p}vesa_plate") if r.head_terminal == "stamped_vesa_plate" \
            else model.get_part(f"{p}vesa_mount")
        wh = model.get_part(f"{p}wrist_head")

        # base swivel swings the arm laterally
        rest = ctx.part_world_position(wh)
        with ctx.pose({swivel: min(0.75, r.swivel_limit)}):
            swung = ctx.part_world_position(wh)
        if rest is not None and swung is not None:
            ctx.check(f"{p}base_swivel_swings_arm",
                      abs(swung[0] - rest[0]) > 0.05 or abs(swung[1] - rest[1]) > 0.05,
                      f"rest={rest}, swung={swung}")

        # elbow raises/lowers the head (skeletons with an elbow)
        if r.arm_skeleton in ("two_segment", "three_segment"):
            elbow = model.get_articulation(f"{p}elbow_pitch")
            with ctx.pose({elbow: -0.45}):
                lo = ctx.part_world_position(wh)
            with ctx.pose({elbow: 0.45}):
                hi = ctx.part_world_position(wh)
            if lo is not None and hi is not None:
                ctx.check(f"{p}elbow_changes_head_height", abs(hi[2] - lo[2]) > 0.08,
                          f"low={lo}, high={hi}")

        # wrist tilt nods the head
        tilt = model.get_articulation(f"{p}wrist_tilt")
        with ctx.pose({tilt: -0.45}):
            tl = ctx.part_world_position(head_part)
        with ctx.pose({tilt: 0.45}):
            th = ctx.part_world_position(head_part)
        if tl is not None and th is not None:
            ctx.check(f"{p}wrist_tilt_nods_head", abs(th[2] - tl[2]) > 0.04, f"low={tl}, high={th}")

        # vesa rotation rolls the head
        rest_aabb = ctx.part_world_aabb(head_part)
        with ctx.pose({rot: min(0.55, r.vesa_rot_limit)}):
            rolled_aabb = ctx.part_world_aabb(head_part)
        if rest_aabb is not None and rolled_aabb is not None:
            rest_h = rest_aabb[1][2] - rest_aabb[0][2]
            rolled_h = rolled_aabb[1][2] - rolled_aabb[0][2]
            ctx.check(f"{p}vesa_rotation_rolls_head", abs(rolled_h - rest_h) > 0.010,
                      f"rest_h={rest_h:.3f}, rolled_h={rolled_h:.3f}")

    # prismatic riser translates the arm vertically
    if r.riser == "prismatic_riser":
        slide = model.get_articulation("height_slide")
        ctx.check("height_slide_is_prismatic", slide.articulation_type == ArticulationType.PRISMATIC,
                  f"expected PRISMATIC, got {slide.articulation_type!r}")
        wh0 = model.get_part("wrist_head")
        with ctx.pose({slide: -0.15}):
            down = ctx.part_world_position(wh0)
        with ctx.pose({slide: 0.10}):
            up = ctx.part_world_position(wh0)
        if down is not None and up is not None:
            ctx.check("height_slide_translates_arm", abs(up[2] - down[2]) > 0.15,
                      f"down={down}, up={up}")

    # Rule 5 — full-travel collision sweep.
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=32, ignore_fixed=True)

    return ctx.report()


__all__ = [
    "__modular__",
    "SupportBase",
    "ArmSkeleton",
    "HeadTerminal",
    "Riser",
    "AdjustableMonitorArmConfig",
    "ResolvedAdjustableMonitorArmConfig",
    "build_adjustable_monitor_arm",
    "build_seeded_adjustable_monitor_arm",
    "config_from_seed",
    "resolve_config",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "run_adjustable_monitor_arm_tests",
]
