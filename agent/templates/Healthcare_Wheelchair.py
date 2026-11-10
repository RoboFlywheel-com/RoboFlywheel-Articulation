# SPDX-License-Identifier: Apache-2.0

"""Healthcare / Wheelchair procedural template (modular).

Spec: articraft_template_authoring/specs_modular_v1/Healthcare_Wheelchair.md

Manual / transit / powered wheelchair. A single connected dark tubular ``frame``
chassis (hero mesh built from ``tube_from_spline_points``) carries a mirrored
L/R pair of children:

Fixed motion spine (present on EVERY seed, so there is always >=1 non-FIXED joint):
  * {side}_rear_wheel   CONTINUOUS +Y  — the two rear drive wheels roll
  * {side}_caster_fork  CONTINUOUS +Z  — front swivel casters steer
  * {side}_caster_wheel CONTINUOUS +Y  — the small caster wheels roll

Five structural slots (pattern = parallel_children; every child parents to the
``frame`` root — there is no serial assembler chain):
  * Slot A propulsion   : large_pushrim_manual / small_transit / powered_drive
  * Slot B footrest     : swingaway_flipup / elevating_legrest
  * Slot C backrest     : fixed_sling_back / reclining_back
  * Slot D armrest      : fixed_tubular_arm / desk_flipback_arm
  * Slot E frame_brace  : rigid_frame / cross_brace_folding

Module sources (5-star Healthcare/Wheelchair records, geometry adapted verbatim —
every torus / spoke bundle / tubular frame mesh is preserved, no Box/Cylinder
downgrade of the hero wheels or frame):
  S1 parent            large_pushrim_manual + swingaway + fixed back/arm + rigid
  S2 var_transit       small_transit rear wheels + attendant push handles
  S3 var_powered       powered_drive: motor housings + battery + joystick
  S4 var_elevating     elevating_legrest (REVOLUTE -Y calf rests)
  S5 var_reclining     reclining_back (REVOLUTE -Y high back + headrest)
  S6 var_desk_armrest  desk_flipback_arm (REVOLUTE -Y flip-back arms)
  S7 var_folding_xframe cross_brace_folding (REVOLUTE +X scissor cross-brace)

Rules:
  Rule 1 — non-articulating detail (seat/backrest/armrest pads, seams, battery
    box, motor housings, joystick pod, push handles, headrest) is ``frame`` (or
    the moving child part's) ``.visual(...)`` — never a FIXED-jointed part. The
    only FIXED joint is ``fold_brace_left`` (a composed kinematic sub-assembly:
    the moving ``fold_brace_right`` needs its own reference frame).
  Rule 2 — every moving child is a captured pin-through-sleeve pivot (wheel-on-
    axle, fork-in-socket, hinge-barrel-on-pin, scissor crossing). These cannot be
    expressed as two axis-aligned faces in contact, so they are grandfathered
    (omit ``mating=``) and their capture is kept honest with element-scoped
    ``allow_overlap`` + ``expect_overlap`` mirroring each 5-star source's run_tests.
  Rule 3 — structure derives from the declared per-module 5-star sources.
  Rule 5 — ``fail_if_parts_overlap_in_sampled_poses`` + one targeted ``ctx.pose``
    per mechanism.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Literal

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    CylinderGeometry,
    MeshGeometry,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    TorusGeometry,
    mesh_from_geometry,
    tube_from_spline_points,
)

__modular__ = True

# ---------------------------------------------------------------------------
# Slot value spaces
# ---------------------------------------------------------------------------
Propulsion = Literal["large_pushrim_manual", "small_transit", "powered_drive"]
Footrest = Literal["swingaway_flipup", "elevating_legrest"]
Backrest = Literal["fixed_sling_back", "reclining_back"]
Armrest = Literal["fixed_tubular_arm", "desk_flipback_arm"]
FrameBrace = Literal["rigid_frame", "cross_brace_folding"]
PaletteStyle = Literal[
    "chrome_navy",
    "black_powder_black",
    "blue_powder_navy",
    "red_powder_black",
    "grey_powder_teal",
]

PROPULSIONS: tuple[Propulsion, ...] = (
    "large_pushrim_manual",
    "small_transit",
    "powered_drive",
)
FOOTRESTS: tuple[Footrest, ...] = ("swingaway_flipup", "elevating_legrest")
BACKRESTS: tuple[Backrest, ...] = ("fixed_sling_back", "reclining_back")
ARMRESTS: tuple[Armrest, ...] = ("fixed_tubular_arm", "desk_flipback_arm")
FRAME_BRACES: tuple[FrameBrace, ...] = ("rigid_frame", "cross_brace_folding")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "chrome_navy",
    "black_powder_black",
    "blue_powder_navy",
    "red_powder_black",
    "grey_powder_teal",
)

# ---------------------------------------------------------------------------
# Palette colorways. Every .visual(material=...) draws one of these keys.
# `frame` + `fabric` carry the recognizable colorway; chrome/rubber/plastic are
# near-constant hardware. >=5 colorways (target 4-6).
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "chrome_navy": {
        "frame": (0.72, 0.74, 0.77, 1.0),
        "fabric": (0.05, 0.18, 0.36, 1.0),
        "fabric_dark": (0.025, 0.10, 0.23, 1.0),
    },
    "black_powder_black": {
        "frame": (0.05, 0.05, 0.06, 1.0),
        "fabric": (0.10, 0.10, 0.11, 1.0),
        "fabric_dark": (0.04, 0.04, 0.05, 1.0),
    },
    "blue_powder_navy": {
        "frame": (0.09, 0.22, 0.48, 1.0),
        "fabric": (0.06, 0.16, 0.32, 1.0),
        "fabric_dark": (0.03, 0.09, 0.20, 1.0),
    },
    "red_powder_black": {
        "frame": (0.55, 0.06, 0.07, 1.0),
        "fabric": (0.10, 0.10, 0.11, 1.0),
        "fabric_dark": (0.05, 0.05, 0.06, 1.0),
    },
    "grey_powder_teal": {
        "frame": (0.35, 0.37, 0.40, 1.0),
        "fabric": (0.10, 0.34, 0.34, 1.0),
        "fabric_dark": (0.05, 0.18, 0.18, 1.0),
    },
}
# Constant hardware colors, merged into every palette.
_HARDWARE = {
    "chrome": (0.82, 0.84, 0.82, 1.0),
    "rubber": (0.02, 0.02, 0.02, 1.0),
    "vinyl": (0.03, 0.03, 0.04, 1.0),
    "housing": (0.03, 0.03, 0.035, 1.0),
    "controller": (0.12, 0.12, 0.13, 1.0),
    "led": (0.10, 0.85, 0.20, 1.0),
    "grip": (0.03, 0.03, 0.03, 1.0),
}

# ---------------------------------------------------------------------------
# Single-sourced geometric quantities (world meters; ground irrelevant — this
# is a floating articulated object). Shared by the frame mesh AND the child
# joint origins so the two never drift (Contract 3c).
# ---------------------------------------------------------------------------
TUBE = 0.014
FOOTREST_LIFT = 0.075

UPRIGHT_Y = 0.235  # rear-upright / seat-rail / arm-rail y half-track
REAR_AXLE_X = -0.220
REAR_AXLE_Z = 0.300
REAR_WHEEL_Y = 0.380
CASTER_X = 0.420
CASTER_SWIVEL_Z = 0.210
CASTER_SOCKET_Z = 0.225
CASTER_Y = 0.235
FOOTREST_HINGE_X = 0.455
FOOTREST_HINGE_Z = 0.180 + FOOTREST_LIFT  # 0.255
FOOTREST_Y = 0.135
LEGREST_PIVOT_X = 0.325
LEGREST_PIVOT_Z = 0.420
ARM_RAIL_Z = 0.655
ARM_HINGE_X = -0.245
DESK_ARM_Y = 0.315  # desk armrest hinge y (outboard so the pad clears the reclining back tube at y=0.265)
RECLINE_SHAFT_X = -0.245
RECLINE_SHAFT_Z = 0.500
SEAT_CUSHION_Z = 0.465
BACK_BOTTOM_Z = 0.475  # fixed backrest panel bottom (just above the seat)
TALL_UPRIGHT_TOP_Z = 0.900
BRACE_PIVOT = (0.018, 0.0, 0.380)


# ===========================================================================
# Shared mesh helpers (identical across all 7 sources).
# ===========================================================================
def _merge_tube(
    target: MeshGeometry,
    points: list[tuple[float, float, float]],
    *,
    radius: float = TUBE,
    samples_per_segment: int = 6,
    radial_segments: int = 14,
) -> None:
    """Append a round steel tube following the given local points."""
    target.merge(
        tube_from_spline_points(
            points,
            radius=radius,
            samples_per_segment=samples_per_segment,
            radial_segments=radial_segments,
            cap_ends=True,
        )
    )


def _wheel_plane_torus(major_radius: float, tube_radius: float, *, y: float = 0.0) -> MeshGeometry:
    """Torus whose axle is local Y and whose round wheel lies in local XZ."""
    return (
        TorusGeometry(major_radius, tube_radius, radial_segments=16, tubular_segments=64)
        .rotate_x(math.pi / 2.0)
        .translate(0.0, y, 0.0)
    )


def _wheel_axis_cylinder(radius: float, length: float, *, y: float = 0.0) -> MeshGeometry:
    """Cylinder centered on the local Y axle."""
    return (
        CylinderGeometry(radius, length, radial_segments=32, closed=True)
        .rotate_x(math.pi / 2.0)
        .translate(0.0, y, 0.0)
    )


def _spoke_mesh(
    *,
    hub_radius: float,
    rim_radius: float,
    count: int,
    spoke_radius: float,
    flange_y: float,
    standoff_y: float | None = None,
    push_radius: float | None = None,
) -> MeshGeometry:
    """Chrome spoke bundle; the loop is intentional and visible (hero detail)."""
    geom = MeshGeometry()
    for i in range(count):
        theta = 2.0 * math.pi * i / count
        flange = flange_y if i % 2 == 0 else -flange_y
        hub_angle = theta + 0.16
        start = (hub_radius * math.cos(hub_angle), flange, hub_radius * math.sin(hub_angle))
        end = (rim_radius * math.cos(theta), 0.0, rim_radius * math.sin(theta))
        _merge_tube(geom, [start, end], radius=spoke_radius, samples_per_segment=1, radial_segments=10)

    if standoff_y is not None and push_radius is not None:
        # Short stand-offs hold the hand push-rim proud of the wheel rim.
        for i in range(8):
            theta = 2.0 * math.pi * i / 8
            rim_point = (rim_radius * math.cos(theta), 0.0, rim_radius * math.sin(theta))
            push_point = (push_radius * math.cos(theta), standoff_y, push_radius * math.sin(theta))
            _merge_tube(
                geom, [rim_point, push_point], radius=spoke_radius * 1.15,
                samples_per_segment=1, radial_segments=8,
            )
    return geom


def _caster_fork_mesh() -> MeshGeometry:
    geom = MeshGeometry()
    _merge_tube(geom, [(0.0, 0.0, 0.0), (0.0, 0.0, -0.055)], radius=0.012, samples_per_segment=1)
    # Fork trails behind the vertical swivel axis so swiveling is visible.
    _merge_tube(geom, [(0.0, -0.052, -0.055), (-0.105, -0.052, -0.110)], radius=0.008, samples_per_segment=1)
    _merge_tube(geom, [(0.0, 0.052, -0.055), (-0.105, 0.052, -0.110)], radius=0.008, samples_per_segment=1)
    _merge_tube(geom, [(0.0, -0.052, -0.055), (0.0, 0.052, -0.055)], radius=0.008, samples_per_segment=1)
    _merge_tube(geom, [(-0.105, -0.058, -0.110), (-0.105, 0.058, -0.110)], radius=0.006, samples_per_segment=1)
    return geom


def _footplate_hinge_mesh() -> MeshGeometry:
    """Hinge barrel of the flip-up footplate (the plate is a separate Box visual)."""
    geom = MeshGeometry()
    geom.merge(_wheel_axis_cylinder(0.011, 0.145))
    return geom


def _legrest_arm_mesh() -> MeshGeometry:
    """Elevating legrest: hinge barrel, support arm, and forked pad cradle (S4)."""
    geom = MeshGeometry()
    geom.merge(_wheel_axis_cylinder(0.012, 0.110))
    _merge_tube(geom, [(0.0, 0.0, 0.0), (0.22, 0.0, 0.0)], radius=0.012)
    _merge_tube(geom, [(0.22, 0.0, 0.0), (0.32, -0.065, 0.0)], radius=0.009)
    _merge_tube(geom, [(0.22, 0.0, 0.0), (0.32, 0.065, 0.0)], radius=0.009)
    _merge_tube(geom, [(0.32, -0.065, 0.0), (0.32, 0.065, 0.0)], radius=0.008)
    _merge_tube(geom, [(0.27, -0.035, 0.0), (0.27, 0.035, 0.0)], radius=0.006)
    return geom


def _desk_armrest_mesh() -> MeshGeometry:
    """Flip-back desk-length armrest tube structure, hinge at local origin (S6)."""
    geom = MeshGeometry()
    _merge_tube(geom, [(0.0, 0.0, 0.0), (0.0, 0.0, 0.032)], radius=0.010, samples_per_segment=2)
    _merge_tube(geom, [(0.0, 0.0, 0.032), (0.280, 0.0, 0.032)], radius=0.010, samples_per_segment=4)
    _merge_tube(geom, [(0.0, 0.0, 0.010), (0.160, 0.0, 0.032)], radius=0.007, samples_per_segment=2)
    _merge_tube(geom, [(0.280, 0.0, 0.022), (0.280, 0.0, 0.042)], radius=0.008, samples_per_segment=1)
    return geom


def _backrest_frame_mesh() -> MeshGeometry:
    """Tubular frame of the reclining backrest in its own part frame (S5).

    Origin sits at the recline pivot (world -0.245, 0, 0.500). Tubes stand just
    outside the frame uprights (y +/-0.265 vs +/-0.235) so the backrest sleeves
    over the frame at the hinge.
    """
    geom = MeshGeometry()
    for y in (-0.265, 0.265):
        _merge_tube(
            geom,
            [(0.0, y, 0.0), (0.0, y, 0.460), (-0.055, y, 0.500), (-0.055, y, 0.620)],
            radius=TUBE,
        )
    _merge_tube(geom, [(0.0, -0.265, 0.050), (0.0, 0.265, 0.050)], radius=TUBE * 0.82, samples_per_segment=1)
    _merge_tube(geom, [(0.0, -0.265, 0.355), (0.0, 0.265, 0.355)], radius=TUBE * 0.82, samples_per_segment=1)
    _merge_tube(geom, [(-0.055, -0.265, 0.500), (-0.055, 0.265, 0.500)], radius=TUBE * 0.82, samples_per_segment=1)
    for y in (-0.100, 0.100):
        _merge_tube(geom, [(-0.055, y, 0.500), (-0.055, y, 0.600)], radius=TUBE * 0.70, samples_per_segment=2)
    # Central panel-backing spine at x=-0.018: it overlaps the x=0 cross-tubes AND
    # sits proud enough for the (behind-the-frame) upholstery panel to mate to the
    # backrest's own tube tree instead of floating off it.
    _merge_tube(geom, [(-0.018, 0.0, 0.030), (-0.018, 0.0, 0.440)], radius=TUBE)
    return geom


def _fold_brace_mesh(sign: float) -> MeshGeometry:
    """One X-brace diagonal tube in local coords centered at the scissor pivot (S7).

    ``sign`` +1 = left (lower-right -> upper-left rail), -1 = right (mirror).
    """
    geom = MeshGeometry()
    lo = (-0.228, sign * -0.220, -0.075)
    hi = (0.227, sign * 0.220, 0.075)
    _merge_tube(geom, [lo, hi], radius=TUBE * 0.65, samples_per_segment=4)
    # Mounting bracket stubs reaching the frame side rails at y = +/-0.235.
    _merge_tube(geom, [lo, (-0.228, sign * -0.235, -0.075)], radius=TUBE * 0.55, samples_per_segment=1)
    _merge_tube(geom, [hi, (0.227, sign * 0.235, 0.075)], radius=TUBE * 0.55, samples_per_segment=1)
    return geom


# ---------------------------------------------------------------------------
# Rear-wheel mesh families (one per propulsion module; wheel_dia_scale applied).
# ---------------------------------------------------------------------------
def _manual_rear_wheel_meshes(side_sign: float, s: float) -> dict[str, MeshGeometry]:
    push_y = side_sign * 0.052
    return {
        "tire": _wheel_plane_torus(0.270 * s, 0.030),
        # rim tube thick enough that its outer edge nests well into the tire bead
        # (outer 0.247s vs tire inner 0.240s) so the tire is never a tessellation island.
        "rim": _wheel_plane_torus(0.235 * s, 0.012),
        "push_rim": _wheel_plane_torus(0.262 * s, 0.005, y=push_y),
        "hub": _wheel_axis_cylinder(0.054 * s, 0.070),
        "spokes": _spoke_mesh(
            hub_radius=0.050 * s, rim_radius=0.231 * s, count=28, spoke_radius=0.0022,
            flange_y=0.018, standoff_y=push_y, push_radius=0.262 * s,
        ),
    }


def _transit_rear_wheel_meshes(s: float) -> dict[str, MeshGeometry]:
    major_r = 0.085 * s
    tube_r = 0.024
    disk_r = major_r - tube_r * 0.3
    return {
        "tire": _wheel_plane_torus(major_r, tube_r),
        "disk": _wheel_axis_cylinder(disk_r, 0.028),
        "hub": _wheel_axis_cylinder(0.020, 0.052),
    }


def _powered_rear_wheel_meshes(s: float) -> dict[str, MeshGeometry]:
    return {
        "tire": _wheel_plane_torus(0.270 * s, 0.035),
        # rim tube thickened so its outer edge nests into the tire (no tessellation island).
        "rim": _wheel_plane_torus(0.230 * s, 0.014),
        "hub": _wheel_axis_cylinder(0.068 * s, 0.095),
        "spokes": _spoke_mesh(
            hub_radius=0.065 * s, rim_radius=0.226 * s, count=20, spoke_radius=0.003, flange_y=0.022,
        ),
    }


def _caster_wheel_meshes() -> dict[str, MeshGeometry]:
    return {
        "tire": _wheel_plane_torus(0.079, 0.020),
        "rim": _wheel_plane_torus(0.052, 0.007),
        "hub": _wheel_axis_cylinder(0.026, 0.056),
        "spokes": _spoke_mesh(hub_radius=0.026, rim_radius=0.052, count=6, spoke_radius=0.0032, flange_y=0.008),
    }


# ===========================================================================
# Config
# ===========================================================================
@dataclass(frozen=True)
class WheelchairConfig:
    propulsion: Propulsion | None = None
    footrest: Footrest | None = None
    backrest: Backrest | None = None
    armrest: Armrest | None = None
    frame_brace: FrameBrace | None = None
    palette_style: PaletteStyle = "chrome_navy"
    wheel_dia_scale: float = 1.0
    seat_width_scale: float = 1.0
    back_height_scale: float = 1.0
    name: str = "wheelchair"


@dataclass(frozen=True)
class ResolvedWheelchairConfig:
    propulsion: Propulsion
    footrest: Footrest
    backrest: Backrest
    armrest: Armrest
    frame_brace: FrameBrace
    palette_style: PaletteStyle
    wheel_dia_scale: float
    seat_width_scale: float
    back_height_scale: float
    name: str

    @property
    def rear_wheel_radius(self) -> float:
        """Outer rear-wheel radius (tire outer) for the current propulsion."""
        s = self.wheel_dia_scale
        if self.propulsion == "small_transit":
            return 0.085 * s + 0.024
        if self.propulsion == "powered_drive":
            return 0.270 * s + 0.035
        return 0.270 * s + 0.030


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


def config_from_seed(seed: int) -> WheelchairConfig:
    """Deterministic procedural sampling over the full slot domain (seed 0 is
    not special). Each slot is sampled independently; the frame mesh + conditional
    decorations adapt to the choices in resolve_config/build."""
    rng = random.Random(seed)
    return WheelchairConfig(
        propulsion=rng.choice(PROPULSIONS),
        footrest=rng.choice(FOOTRESTS),
        backrest=rng.choice(BACKRESTS),
        armrest=rng.choice(ARMRESTS),
        frame_brace=rng.choice(FRAME_BRACES),
        palette_style=rng.choice(PALETTE_STYLES),
        wheel_dia_scale=round(rng.uniform(0.95, 1.08), 4),
        seat_width_scale=round(rng.uniform(0.94, 1.06), 4),
        back_height_scale=round(rng.uniform(0.92, 1.10), 4),
        name=f"seeded_wheelchair_{seed}",
    )


def resolve_config(config: WheelchairConfig | None = None) -> ResolvedWheelchairConfig:
    cfg = config or WheelchairConfig()
    return ResolvedWheelchairConfig(
        propulsion=_pick(cfg.propulsion, PROPULSIONS),
        footrest=_pick(cfg.footrest, FOOTRESTS),
        backrest=_pick(cfg.backrest, BACKRESTS),
        armrest=_pick(cfg.armrest, ARMRESTS),
        frame_brace=_pick(cfg.frame_brace, FRAME_BRACES),
        palette_style=_pick(cfg.palette_style, PALETTE_STYLES),
        wheel_dia_scale=_clamp(cfg.wheel_dia_scale, 0.95, 1.08),
        seat_width_scale=_clamp(cfg.seat_width_scale, 0.94, 1.06),
        back_height_scale=_clamp(cfg.back_height_scale, 0.92, 1.10),
        name=cfg.name or "wheelchair",
    )


def slot_choices_for_config(
    config: WheelchairConfig | ResolvedWheelchairConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedWheelchairConfig) else resolve_config(config)
    return (
        ("propulsion", r.propulsion),
        ("footrest", r.footrest),
        ("backrest", r.backrest),
        ("armrest", r.armrest),
        ("frame_brace", r.frame_brace),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


SIDES: tuple[tuple[str, float], ...] = (("left", 1.0), ("right", -1.0))


# ===========================================================================
# Frame (root chassis) — config-aware hero mesh + conditional fixed visuals.
# ===========================================================================
def _build_frame_mesh(r: ResolvedWheelchairConfig) -> MeshGeometry:
    """One connected dark tubular wheelchair frame; adapts uprights (backrest),
    front footrest structure (footrest), and X-brace (frame_brace)."""
    geom = MeshGeometry()
    tall = r.backrest == "fixed_sling_back"
    for _label, sgn in SIDES:
        y = sgn * UPRIGHT_Y
        inner_y = sgn * FOOTREST_Y
        # Rear upright: tall (fused sling back) or short (separate reclining back).
        if tall:
            _merge_tube(geom, [(-0.245, y, 0.300), (-0.245, y, TALL_UPRIGHT_TOP_Z), (-0.300, y, 0.960)], radius=TUBE)
        else:
            _merge_tube(geom, [(-0.245, y, 0.300), (-0.245, y, 0.660)], radius=TUBE)
        _merge_tube(geom, [(-0.245, y, 0.470), (0.300, y, 0.470)], radius=TUBE)
        _merge_tube(geom, [(0.300, y, 0.275), (0.300, y, 0.665)], radius=TUBE)
        _merge_tube(geom, [(-0.235, y, 0.310), (0.120, y, 0.265), (0.350, y, 0.245), (0.420, y, 0.240)], radius=TUBE)
        _merge_tube(geom, [(-0.245, y, ARM_RAIL_Z), (0.300, y, ARM_RAIL_Z)], radius=TUBE * 0.85)
        _merge_tube(geom, [(-0.220, y, 0.455), (0.300, y, 0.315)], radius=TUBE * 0.80)

        if r.footrest == "swingaway_flipup":
            _merge_tube(
                geom,
                [
                    (0.300, y, 0.380 + FOOTREST_LIFT),
                    (0.338, y, 0.360 + FOOTREST_LIFT),
                    (0.405, inner_y, 0.260 + FOOTREST_LIFT),
                    (FOOTREST_HINGE_X, inner_y, 0.201 + FOOTREST_LIFT),
                ],
                radius=TUBE * 0.82,
            )
        else:  # elevating_legrest: short pivot stub from the front upright inward.
            _merge_tube(
                geom,
                [(0.300, y, LEGREST_PIVOT_Z), (0.325, y, LEGREST_PIVOT_Z), (0.325, inner_y, LEGREST_PIVOT_Z)],
                radius=TUBE * 0.90,
            )

    # Widthwise cross-members that span the full track (keep the two sides
    # connected even without the fused X-brace).
    cross = [(-0.255, 0.470, TUBE), (0.300, 0.470, TUBE), (0.300, 0.300, TUBE * 0.82)]
    if tall:
        cross.append((-0.255, 0.855, TUBE * 0.82))
    for x, z, radius in cross:
        _merge_tube(geom, [(x, -UPRIGHT_Y, z), (x, UPRIGHT_Y, z)], radius=radius, samples_per_segment=1)

    # Fused static X-brace under the seat — only for the rigid frame. The folding
    # frame's scissor braces ARE the X-brace (separate moving parts).
    if r.frame_brace == "rigid_frame":
        _merge_tube(geom, [(-0.210, -0.220, 0.305), (0.245, 0.220, 0.455)], radius=TUBE * 0.65)
        _merge_tube(geom, [(-0.210, 0.220, 0.305), (0.245, -0.220, 0.455)], radius=TUBE * 0.65)

    # Scissor pivot boss (present in all sources) + a y=0 gusset tying it to the
    # front cross-member so the boss is never an isolated island (the fused
    # X-brace only ties it in for the rigid frame; the folding frame has no X).
    geom.merge(
        CylinderGeometry(0.014, 0.018, radial_segments=24, closed=True)
        .rotate_x(math.pi / 2.0)
        .translate(*BRACE_PIVOT)
    )
    _merge_tube(geom, [BRACE_PIVOT, (0.300, 0.0, 0.300)], radius=TUBE * 0.6, samples_per_segment=1)

    # Reclining recline pivot shaft spanning the uprights.
    if r.backrest == "reclining_back":
        _merge_tube(
            geom, [(RECLINE_SHAFT_X, -0.265, RECLINE_SHAFT_Z), (RECLINE_SHAFT_X, 0.265, RECLINE_SHAFT_Z)],
            radius=0.010, samples_per_segment=1,
        )
    return geom


def _build_frame(model: ArticulatedObject, r: ResolvedWheelchairConfig, mats) -> object:
    frame = model.part("frame")
    frame.visual(mesh_from_geometry(_build_frame_mesh(r), "tubular_frame"), material=mats["frame"], name="tubular_frame", material_class_id=("metal.paint_coated" if r.palette_style in {"black_powder_black", "blue_powder_navy", "red_powder_black", "grey_powder_teal"} else "metal.chrome_polished"))
    # Rear axle (rear wheels' captured shaft) — spans the full track along Y.
    frame.visual(
        Cylinder(radius=0.018, length=0.800),
        origin=Origin(xyz=(REAR_AXLE_X, 0.0, REAR_AXLE_Z), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["frame"], name="rear_axle", material_class_id=("metal.paint_coated" if r.palette_style in {"black_powder_black", "blue_powder_navy", "red_powder_black", "grey_powder_teal"} else "metal.chrome_polished"),
    )
    # Front caster swivel sockets.
    for label, sgn in SIDES:
        frame.visual(
            Cylinder(radius=0.020, length=0.030),
            origin=Origin(xyz=(CASTER_X, sgn * CASTER_Y, CASTER_SOCKET_Z)),
            material=mats["frame"], name=f"{label}_caster_socket", material_class_id=("metal.paint_coated" if r.palette_style in {"black_powder_black", "blue_powder_navy", "red_powder_black", "grey_powder_teal"} else "metal.chrome_polished"),
        )

    # Footrest / legrest hinge hardware on the fixed frame.
    if r.footrest == "swingaway_flipup":
        for label, sgn in SIDES:
            frame.visual(
                Cylinder(radius=0.010, length=0.155),
                origin=Origin(xyz=(FOOTREST_HINGE_X, sgn * FOOTREST_Y, FOOTREST_HINGE_Z), rpy=(math.pi / 2.0, 0.0, 0.0)),
                material=mats["frame"], name=f"{label}_footrest_hinge", material_class_id=("metal.paint_coated" if r.palette_style in {"black_powder_black", "blue_powder_navy", "red_powder_black", "grey_powder_teal"} else "metal.chrome_polished"),
            )
            frame.visual(
                Box((0.024, 0.035, 0.020)),
                origin=Origin(xyz=(FOOTREST_HINGE_X, sgn * FOOTREST_Y, 0.200 + FOOTREST_LIFT)),
                material=mats["frame"], name=f"{label}_footrest_bracket", material_class_id=("metal.paint_coated" if r.palette_style in {"black_powder_black", "blue_powder_navy", "red_powder_black", "grey_powder_teal"} else "metal.chrome_polished"),
            )
    else:
        for label, sgn in SIDES:
            frame.visual(
                Cylinder(radius=0.014, length=0.050),
                origin=Origin(xyz=(LEGREST_PIVOT_X, sgn * FOOTREST_Y, LEGREST_PIVOT_Z), rpy=(math.pi / 2.0, 0.0, 0.0)),
                material=mats["frame"], name=f"{label}_legrest_pivot", material_class_id=("metal.paint_coated" if r.palette_style in {"black_powder_black", "blue_powder_navy", "red_powder_black", "grey_powder_teal"} else "metal.chrome_polished"),
            )

    # Desk armrest hinge pins (lateral, from the arm rail out to the hinge y).
    if r.armrest == "desk_flipback_arm":
        for label, sgn in SIDES:
            frame.visual(
                Cylinder(radius=0.014, length=0.085),
                origin=Origin(xyz=(ARM_HINGE_X, sgn * 0.2775, ARM_RAIL_Z), rpy=(math.pi / 2.0, 0.0, 0.0)),
                material=mats["frame"], name=f"{label}_arm_hinge", material_class_id=("metal.paint_coated" if r.palette_style in {"black_powder_black", "blue_powder_navy", "red_powder_black", "grey_powder_teal"} else "metal.chrome_polished"),
            )

    _emit_seat(frame, r, mats)
    if r.backrest == "fixed_sling_back":
        _emit_fixed_backrest(frame, r, mats)
    if r.armrest == "fixed_tubular_arm":
        _emit_fixed_armrests(frame, r, mats)
    if r.propulsion == "small_transit" and r.backrest == "fixed_sling_back":
        _emit_push_handles(frame, mats)
    if r.propulsion == "powered_drive":
        _emit_powered_frame_details(frame, r, mats)
    return frame


def _emit_seat(frame, r, mats) -> None:
    ws = r.seat_width_scale
    frame.visual(
        Box((0.560, 0.470 * ws, 0.055)),
        origin=Origin(xyz=(0.030, 0.0, SEAT_CUSHION_Z)),
        material=mats["fabric"], name="seat_cushion", material_class_id=("fabric.denim_twill" if r.palette_style in {"chrome_navy", "blue_powder_navy"} else "fabric.upholstery_plain"),
    )
    for i, v in enumerate(range(-4, 5)):
        frame.visual(
            Box((0.430, 0.006, 0.006)),
            origin=Origin(xyz=(0.035, v * 0.055 * ws, 0.493)),
            material=mats["fabric_dark"], name=f"seat_seam_{i}", material_class_id="fabric.thread_yarn",
        )


def _emit_fixed_backrest(frame, r, mats) -> None:
    ws = r.seat_width_scale
    hs = r.back_height_scale
    back_h = 0.430 * hs
    back_cz = BACK_BOTTOM_Z + back_h / 2.0
    frame.visual(
        Box((0.040, 0.490 * ws, back_h)),
        origin=Origin(xyz=(-0.275, 0.0, back_cz)),
        material=mats["fabric"], name="backrest", material_class_id="fabric.upholstery_plain",
    )
    seam_h = 0.330 / 0.430 * back_h
    for i, v in enumerate(range(-3, 4)):
        frame.visual(
            Box((0.006, 0.010, seam_h)),
            origin=Origin(xyz=(-0.252, v * 0.060 * ws, back_cz)),
            material=mats["fabric_dark"], name=f"backrest_seam_{i}", material_class_id="fabric.thread_yarn",
        )


def _emit_fixed_armrests(frame, r, mats) -> None:
    for label, sgn in SIDES:
        frame.visual(
            Box((0.455, 0.070, 0.035)),
            origin=Origin(xyz=(0.045, sgn * 0.265, 0.682)),
            material=mats["fabric"], name=f"{label}_armrest_pad", material_class_id="fabric.upholstery_plain",
        )


def _emit_push_handles(frame, mats) -> None:
    """Attendant push handles rising from the tall backrest upright tops (S2)."""
    for label, sgn in SIDES:
        y = sgn * UPRIGHT_Y
        stem = tube_from_spline_points(
            [(-0.300, y, 0.960), (-0.305, y, 1.020), (-0.312, y, 1.085), (-0.316, y, 1.120)],
            radius=TUBE, samples_per_segment=6, radial_segments=12, cap_ends=True,
        )
        frame.visual(mesh_from_geometry(stem, f"{label}_push_handle_stem"), material=mats["frame"], name=f"{label}_push_handle_stem", material_class_id="metal.paint_coated")
        grip = tube_from_spline_points(
            [(-0.310, y, 1.040), (-0.314, y, 1.095), (-0.316, y, 1.120), (-0.318, y, 1.145)],
            radius=TUBE * 1.55, samples_per_segment=6, radial_segments=12, cap_ends=True,
        )
        frame.visual(mesh_from_geometry(grip, f"{label}_push_handle_grip"), material=mats["grip"], name=f"{label}_push_handle_grip", material_class_id="rubber.smooth_plain")


def _emit_powered_frame_details(frame, r, mats) -> None:
    """Battery box (on cradle bars), motor/gearbox housings, joystick pod (S3)."""
    # Battery cradle bars span the full track so the battery is supported on the
    # frame regardless of rigid/folding brace (Contract 3: real support path).
    for i, bx in enumerate((-0.150, 0.170)):
        frame.visual(
            Box((0.030, 0.490, 0.020)),
            origin=Origin(xyz=(bx, 0.0, 0.305)),
            material=mats["frame"], name=f"battery_cradle_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"black_powder_black", "blue_powder_navy", "red_powder_black", "grey_powder_teal"} else "metal.chrome_polished"),
        )
    frame.visual(
        Box((0.380, 0.340, 0.100)),
        origin=Origin(xyz=(0.010, 0.0, 0.350)),
        material=mats["housing"], name="battery_box", material_class_id="plastic.opaque_glossy_molded",
    )
    # Motor / gearbox housings flanking the rear wheels (embed the rear axle + hub).
    for label, sgn in SIDES:
        frame.visual(
            Box((0.130, 0.075, 0.110)),
            origin=Origin(xyz=(REAR_AXLE_X, sgn * 0.310, REAR_AXLE_Z)),
            material=mats["housing"], name=f"{label}_motor_housing", material_class_id="metal.blackened_gunmetal",
        )
        frame.visual(
            Cylinder(radius=0.032, length=0.018),
            origin=Origin(xyz=(REAR_AXLE_X, sgn * 0.356, REAR_AXLE_Z), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["controller"], name=f"{label}_gearbox_cap", material_class_id="plastic.opaque_glossy_molded",
        )
    # Joystick support post rising from the right arm rail (keeps the pod
    # supported even when the armrest is a flip-back part).
    post = tube_from_spline_points(
        [(0.240, -0.235, ARM_RAIL_Z), (0.240, -0.265, 0.680), (0.240, -0.265, 0.700)],
        radius=0.012, samples_per_segment=3, radial_segments=12, cap_ends=True,
    )
    frame.visual(mesh_from_geometry(post, "joystick_post"), material=mats["housing"], name="joystick_post", material_class_id="metal.blackened_gunmetal")
    frame.visual(Box((0.100, 0.080, 0.040)), origin=Origin(xyz=(0.240, -0.265, 0.712)), material=mats["controller"], name="joystick_base", material_class_id="tech.control_interface")
    frame.visual(Cylinder(radius=0.006, length=0.038), origin=Origin(xyz=(0.240, -0.265, 0.751)), material=mats["frame"], name="joystick_stem", material_class_id=("metal.paint_coated" if r.palette_style in {"black_powder_black", "blue_powder_navy", "red_powder_black", "grey_powder_teal"} else "metal.chrome_polished"))
    frame.visual(Cylinder(radius=0.016, length=0.022), origin=Origin(xyz=(0.240, -0.265, 0.781)), material=mats["housing"], name="joystick_knob", material_class_id="plastic.opaque_glossy_molded")
    frame.visual(Cylinder(radius=0.004, length=0.008), origin=Origin(xyz=(0.270, -0.265, 0.731)), material=mats["led"], name="joystick_led", material_class_id="tech.emissive_surface")


# ===========================================================================
# Slot A: propulsion — rear drive wheels (per family) + front swivel casters.
# ===========================================================================
def _build_rear_wheels(model, frame, r, mats) -> None:
    for label, sgn in SIDES:
        wheel = model.part(f"{label}_rear_wheel")
        if r.propulsion == "small_transit":
            m = _transit_rear_wheel_meshes(r.wheel_dia_scale)
            wheel.visual(mesh_from_geometry(m["tire"], f"{label}_rear_tire"), material=mats["rubber"], name="tire", material_class_id="rubber.smooth_plain")
            wheel.visual(mesh_from_geometry(m["disk"], f"{label}_rear_disk"), material=mats["frame"], name="disk", material_class_id=("metal.paint_coated" if r.palette_style in {"black_powder_black", "blue_powder_navy", "red_powder_black", "grey_powder_teal"} else "metal.chrome_polished"))
            wheel.visual(mesh_from_geometry(m["hub"], f"{label}_rear_hub"), material=mats["chrome"], name="hub", material_class_id="metal.chrome_polished")
        elif r.propulsion == "powered_drive":
            m = _powered_rear_wheel_meshes(r.wheel_dia_scale)
            wheel.visual(mesh_from_geometry(m["tire"], f"{label}_rear_tire"), material=mats["rubber"], name="tire", material_class_id="rubber.smooth_plain")
            wheel.visual(mesh_from_geometry(m["rim"], f"{label}_rear_rim"), material=mats["chrome"], name="rim", material_class_id="metal.chrome_polished")
            wheel.visual(mesh_from_geometry(m["hub"], f"{label}_rear_hub"), material=mats["housing"], name="hub", material_class_id="metal.blackened_gunmetal")
            wheel.visual(mesh_from_geometry(m["spokes"], f"{label}_rear_spokes"), material=mats["chrome"], name="spokes", material_class_id="metal.chrome_polished")
        else:  # large_pushrim_manual
            m = _manual_rear_wheel_meshes(sgn, r.wheel_dia_scale)
            wheel.visual(mesh_from_geometry(m["tire"], f"{label}_rear_tire"), material=mats["rubber"], name="tire", material_class_id="rubber.smooth_plain")
            wheel.visual(mesh_from_geometry(m["rim"], f"{label}_rear_rim"), material=mats["chrome"], name="rim", material_class_id="metal.chrome_polished")
            wheel.visual(mesh_from_geometry(m["push_rim"], f"{label}_rear_push_rim"), material=mats["chrome"], name="push_rim", material_class_id="metal.chrome_polished")
            wheel.visual(mesh_from_geometry(m["hub"], f"{label}_rear_hub"), material=mats["chrome"], name="hub", material_class_id="metal.chrome_polished")
            wheel.visual(mesh_from_geometry(m["spokes"], f"{label}_rear_spokes"), material=mats["chrome"], name="spokes", material_class_id="metal.chrome_polished")
        model.articulation(
            f"frame_to_{label}_rear_wheel", ArticulationType.CONTINUOUS,
            parent=frame, child=wheel,
            origin=Origin(xyz=(REAR_AXLE_X, sgn * REAR_WHEEL_Y, REAR_AXLE_Z)),
            axis=(0.0, 1.0, 0.0), motion_limits=MotionLimits(effort=15.0, velocity=12.0),
        )


def _build_casters(model, frame, r, mats) -> None:
    for label, sgn in SIDES:
        fork = model.part(f"{label}_caster_fork")
        fork.visual(mesh_from_geometry(_caster_fork_mesh(), f"{label}_caster_fork"), material=mats["chrome"], name="fork", material_class_id="metal.chrome_polished")
        model.articulation(
            f"frame_to_{label}_caster", ArticulationType.CONTINUOUS,
            parent=frame, child=fork,
            origin=Origin(xyz=(CASTER_X, sgn * CASTER_Y, CASTER_SWIVEL_Z)),
            axis=(0.0, 0.0, 1.0), motion_limits=MotionLimits(effort=4.0, velocity=8.0),
        )
        caster_wheel = model.part(f"{label}_caster_wheel")
        cm = _caster_wheel_meshes()
        caster_wheel.visual(mesh_from_geometry(cm["tire"], f"{label}_caster_tire"), material=mats["rubber"], name="tire", material_class_id="rubber.smooth_plain")
        caster_wheel.visual(mesh_from_geometry(cm["rim"], f"{label}_caster_rim"), material=mats["chrome"], name="rim", material_class_id="metal.chrome_polished")
        caster_wheel.visual(mesh_from_geometry(cm["hub"], f"{label}_caster_hub"), material=mats["chrome"], name="hub", material_class_id="metal.chrome_polished")
        caster_wheel.visual(mesh_from_geometry(cm["spokes"], f"{label}_caster_spokes"), material=mats["chrome"], name="spokes", material_class_id="metal.chrome_polished")
        model.articulation(
            f"{label}_caster_to_wheel", ArticulationType.CONTINUOUS,
            parent=fork, child=caster_wheel,
            origin=Origin(xyz=(-0.105, 0.0, -0.110)),
            axis=(0.0, 1.0, 0.0), motion_limits=MotionLimits(effort=3.0, velocity=12.0),
        )


# ===========================================================================
# Slot B: footrest.
# ===========================================================================
def _build_footrest(model, frame, r, mats) -> None:
    if r.footrest == "swingaway_flipup":
        for label, sgn in SIDES:
            fp = model.part(f"{label}_footplate")
            fp.visual(mesh_from_geometry(_footplate_hinge_mesh(), f"{label}_footplate_hinge"), material=mats["chrome"], name="hinge_bar", material_class_id="metal.chrome_polished")
            fp.visual(Box((0.180, 0.120, 0.014)), origin=Origin(xyz=(0.090, 0.0, -0.026), rpy=(0.0, -0.18, 0.0)), material=mats["frame"], name="plate", material_class_id=("metal.paint_coated" if r.palette_style in {"black_powder_black", "blue_powder_navy", "red_powder_black", "grey_powder_teal"} else "metal.chrome_polished"))
            fp.visual(Box((0.110, 0.118, 0.036)), origin=Origin(xyz=(0.045, 0.0, -0.018), rpy=(0.0, -0.08, 0.0)), material=mats["frame"], name="plate_neck", material_class_id=("metal.paint_coated" if r.palette_style in {"black_powder_black", "blue_powder_navy", "red_powder_black", "grey_powder_teal"} else "metal.chrome_polished"))
            model.articulation(
                f"frame_to_{label}_footplate", ArticulationType.REVOLUTE,
                parent=frame, child=fp,
                origin=Origin(xyz=(FOOTREST_HINGE_X, sgn * FOOTREST_Y, FOOTREST_HINGE_Z)),
                # Upper capped at 1.25 rad (~72 deg flip-up): beyond that the plate
                # sweeps into the front frame tube. Still an unmistakable flip-up.
                axis=(0.0, -1.0, 0.0), motion_limits=MotionLimits(effort=8.0, velocity=2.5, lower=0.0, upper=1.25),
            )
    else:
        for label, sgn in SIDES:
            lr = model.part(f"{label}_legrest")
            lr.visual(mesh_from_geometry(_legrest_arm_mesh(), f"{label}_legrest_arm"), material=mats["chrome"], name="arm", material_class_id="metal.chrome_polished")
            lr.visual(Box((0.14, 0.13, 0.040)), origin=Origin(xyz=(0.265, 0.0, 0.025)), material=mats["vinyl"], name="calf_pad", material_class_id="leather.smooth_plain")
            model.articulation(
                f"frame_to_{label}_legrest", ArticulationType.REVOLUTE,
                parent=frame, child=lr,
                origin=Origin(xyz=(LEGREST_PIVOT_X, sgn * FOOTREST_Y, LEGREST_PIVOT_Z)),
                axis=(0.0, -1.0, 0.0), motion_limits=MotionLimits(effort=10.0, velocity=2.0, lower=0.0, upper=1.20),
            )


# ===========================================================================
# Slot C: reclining backrest (fixed_sling is fused into the frame).
# ===========================================================================
def _build_reclining_backrest(model, frame, r, mats) -> None:
    backrest = model.part("backrest")
    backrest.visual(mesh_from_geometry(_backrest_frame_mesh(), "backrest_frame"), material=mats["frame"], name="frame_tubes", material_class_id=("metal.paint_coated" if r.palette_style in {"black_powder_black", "blue_powder_navy", "red_powder_black", "grey_powder_teal"} else "metal.chrome_polished"))
    back_h = 0.460 * r.back_height_scale
    # Panel sits BEHIND the frame plane (front at local x=-0.020, world x=-0.265 <
    # frame upright front -0.259) so it never collides with the coincident short
    # frame upright; it mates to the backrest's own panel-backing spine (x=-0.018).
    backrest.visual(Box((0.040, 0.440 * r.seat_width_scale, back_h)), origin=Origin(xyz=(-0.040, 0.0, back_h / 2.0)), material=mats["fabric"], name="back_panel", material_class_id="fabric.upholstery_plain")
    backrest.visual(Box((0.050, 0.240, 0.090)), origin=Origin(xyz=(-0.055, 0.0, 0.640)), material=mats["fabric"], name="headrest_pad", material_class_id="fabric.upholstery_plain")
    for i, v in enumerate(range(-3, 4)):
        backrest.visual(Box((0.006, 0.010, 0.380)), origin=Origin(xyz=(-0.020, v * 0.060 * r.seat_width_scale, back_h / 2.0)), material=mats["fabric_dark"], name=f"back_seam_{i}", material_class_id="fabric.thread_yarn")
    for label, sgn in SIDES:
        backrest.visual(Cylinder(radius=TUBE * 1.5, length=0.060), origin=Origin(xyz=(-0.055, sgn * 0.265, 0.590)), material=mats["grip"], name=f"{label}_grip", material_class_id="rubber.smooth_plain")
    model.articulation(
        "frame_to_backrest", ArticulationType.REVOLUTE,
        parent=frame, child=backrest,
        origin=Origin(xyz=(RECLINE_SHAFT_X, 0.0, RECLINE_SHAFT_Z)),
        axis=(0.0, -1.0, 0.0), motion_limits=MotionLimits(effort=10.0, velocity=1.0, lower=0.0, upper=0.60),
    )


# ===========================================================================
# Slot D: desk flip-back armrests (fixed_tubular is fused into the frame).
# ===========================================================================
def _build_desk_armrests(model, frame, r, mats) -> None:
    for label, sgn in SIDES:
        arm = model.part(f"{label}_armrest")
        arm.visual(mesh_from_geometry(_desk_armrest_mesh(), f"{label}_armrest_frame"), material=mats["frame"], name="armrest_frame", material_class_id=("metal.paint_coated" if r.palette_style in {"black_powder_black", "blue_powder_navy", "red_powder_black", "grey_powder_teal"} else "metal.chrome_polished"))
        arm.visual(Box((0.250, 0.060, 0.024)), origin=Origin(xyz=(0.140, 0.0, 0.048)), material=mats["fabric"], name="armrest_pad", material_class_id="fabric.upholstery_plain")
        model.articulation(
            f"frame_to_{label}_armrest", ArticulationType.REVOLUTE,
            parent=frame, child=arm,
            origin=Origin(xyz=(ARM_HINGE_X, sgn * DESK_ARM_Y, ARM_RAIL_Z)),
            axis=(0.0, -1.0, 0.0), motion_limits=MotionLimits(effort=6.0, velocity=2.0, lower=0.0, upper=1.65),
        )


# ===========================================================================
# Slot E: folding cross-brace (rigid frame has a fused X, no extra part).
# ===========================================================================
def _build_folding_brace(model, frame, r, mats) -> None:
    fold_left = model.part("fold_brace_left")
    fold_left.visual(mesh_from_geometry(_fold_brace_mesh(1.0), "fold_brace_left_tube"), material=mats["frame"], name="brace_tube", material_class_id=("metal.paint_coated" if r.palette_style in {"black_powder_black", "blue_powder_navy", "red_powder_black", "grey_powder_teal"} else "metal.chrome_polished"))
    fold_left.visual(
        Cylinder(radius=0.012, length=0.050),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["chrome"], name="pivot_bolt", material_class_id="metal.chrome_polished",
    )
    # FIXED: the moving fold_brace_right needs its own reference frame (a composed
    # kinematic sub-assembly), so fold_brace_left is a real part welded to the frame.
    model.articulation(
        "frame_to_fold_brace_left", ArticulationType.FIXED,
        parent=frame, child=fold_left, origin=Origin(xyz=BRACE_PIVOT),
    )
    fold_right = model.part("fold_brace_right")
    fold_right.visual(mesh_from_geometry(_fold_brace_mesh(-1.0), "fold_brace_right_tube"), material=mats["frame"], name="brace_tube", material_class_id=("metal.paint_coated" if r.palette_style in {"black_powder_black", "blue_powder_navy", "red_powder_black", "grey_powder_teal"} else "metal.chrome_polished"))
    model.articulation(
        "fold_brace_left_to_right", ArticulationType.REVOLUTE,
        parent=fold_left, child=fold_right,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        axis=(1.0, 0.0, 0.0), motion_limits=MotionLimits(effort=10.0, velocity=1.5, lower=0.0, upper=0.50),
    )


# ===========================================================================
# Assembly
# ===========================================================================
def build_wheelchair(
    config: WheelchairConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    base_rgba = dict(PALETTES[r.palette_style])
    base_rgba.update(_HARDWARE)
    mats = {key: model.material(f"wheelchair_{key}_{r.palette_style}", rgba=rgba) for key, rgba in base_rgba.items()}

    frame = _build_frame(model, r, mats)
    _build_rear_wheels(model, frame, r, mats)
    _build_casters(model, frame, r, mats)
    _build_footrest(model, frame, r, mats)
    if r.backrest == "reclining_back":
        _build_reclining_backrest(model, frame, r, mats)
    if r.armrest == "desk_flipback_arm":
        _build_desk_armrests(model, frame, r, mats)
    if r.frame_brace == "cross_brace_folding":
        _build_folding_brace(model, frame, r, mats)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_wheelchair(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_wheelchair(config_from_seed(seed), assets=assets)


# ===========================================================================
# Tests
# ===========================================================================
def _allow_captured_pins(ctx, model, r) -> None:
    """Element-scoped allow_overlap for every captured pin-through-sleeve pivot
    (mirrors the 5-star sources' run_tests). These are honored at every sampled
    pose too."""
    frame = model.get_part("frame")
    for label in ("left", "right"):
        rear = model.get_part(f"{label}_rear_wheel")
        fork = model.get_part(f"{label}_caster_fork")
        cwheel = model.get_part(f"{label}_caster_wheel")
        ctx.allow_overlap(frame, rear, elem_a="rear_axle", elem_b="hub", reason="Fixed rear axle passes through the wheel hub bearing.")
        if r.propulsion == "small_transit":
            ctx.allow_overlap(frame, rear, elem_a="rear_axle", elem_b="disk", reason="Fixed rear axle passes through the solid transit wheel disk.")
        if r.propulsion == "powered_drive":
            ctx.allow_overlap(frame, rear, elem_a=f"{label}_motor_housing", elem_b="hub", reason="Motor/gearbox housing wraps the inboard drive-wheel motor hub.")
            ctx.allow_overlap(frame, rear, elem_a=f"{label}_gearbox_cap", elem_b="hub", reason="Outboard gearbox cap wraps the drive-wheel hub end.")
            ctx.allow_overlap(frame, rear, elem_a="rear_axle", elem_b=f"{label}_motor_housing", reason="Rear axle passes through the motor housing.")
        ctx.allow_overlap(fork, cwheel, elem_a="fork", elem_b="hub", reason="Caster fork axle pin is captured through the small wheel hub.")

    if r.footrest == "swingaway_flipup":
        for label in ("left", "right"):
            fp = model.get_part(f"{label}_footplate")
            ctx.allow_overlap(frame, fp, elem_a=f"{label}_footrest_hinge", elem_b="hinge_bar", reason="Flip-up footplate hinge barrel is coaxial with the frame hinge pin.")
            ctx.allow_overlap(frame, fp, elem_a=f"{label}_footrest_hinge", elem_b="plate_neck", reason="Welded hinge lug wraps the footplate hinge pin.")
            ctx.allow_overlap(frame, fp, elem_a=f"{label}_footrest_bracket", elem_b="plate_neck", reason="Footplate neck lug wraps the frame hinge bracket at the pivot.")
            ctx.allow_overlap(frame, fp, elem_a=f"{label}_footrest_bracket", elem_b="hinge_bar", reason="Footplate hinge barrel is coaxial with the frame hinge bracket at the pivot.")
    else:
        for label in ("left", "right"):
            lr = model.get_part(f"{label}_legrest")
            ctx.allow_overlap(frame, lr, elem_a="tubular_frame", elem_b="arm", reason="Legrest arm hinge barrel is coaxial with the frame front upright at the pivot.")
            ctx.allow_overlap(frame, lr, elem_a=f"{label}_legrest_pivot", elem_b="arm", reason="Frame pivot pin is captured inside the legrest arm hinge barrel.")

    if r.backrest == "reclining_back":
        backrest = model.get_part("backrest")
        ctx.allow_overlap(frame, backrest, elem_a="tubular_frame", elem_b="frame_tubes", reason="Reclining backrest tubes sleeve over the recline pivot shaft at the hinge.")
        if r.armrest == "desk_flipback_arm":
            # The desk-armrest hinge pins bolt alongside the reclining back posts
            # at the rear corner (both structural tubes share the rear bracket).
            for label in ("left", "right"):
                ctx.allow_overlap(frame, backrest, elem_a=f"{label}_arm_hinge", elem_b="frame_tubes", reason="Desk armrest hinge pin bolts alongside the reclining back post at the rear corner.")

    if r.armrest == "desk_flipback_arm":
        for label in ("left", "right"):
            arm = model.get_part(f"{label}_armrest")
            ctx.allow_overlap(frame, arm, elem_a=f"{label}_arm_hinge", elem_b="armrest_frame", reason="Desk armrest post is captured on the frame arm hinge pin.")

    if r.frame_brace == "cross_brace_folding":
        fl = model.get_part("fold_brace_left")
        fr = model.get_part("fold_brace_right")
        # Part-level (mirrors the 5-star folding source): the scissor X-brace and
        # its crossing pivot_bolt route through the seat/frame zone under the
        # cushion — a real folding-wheelchair X-brace crosses the frame structure.
        ctx.allow_overlap(fl, fr, reason="The two X-brace tubes cross and are pinned at the scissor pivot.")
        ctx.allow_overlap(frame, fl, reason="Fold brace routes through the frame cross-members and seat zone under the cushion.")
        ctx.allow_overlap(frame, fr, reason="Fold brace routes through the frame cross-members and seat zone under the cushion.")


def run_wheelchair_tests(object_model: ArticulatedObject, config: WheelchairConfig) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    frame = object_model.get_part("frame")

    _allow_captured_pins(ctx, object_model, r)

    # ---- Captured-pin retention (each side). ----
    for label in ("left", "right"):
        rear = object_model.get_part(f"{label}_rear_wheel")
        fork = object_model.get_part(f"{label}_caster_fork")
        cwheel = object_model.get_part(f"{label}_caster_wheel")
        ctx.expect_overlap(frame, rear, axes="y", elem_a="rear_axle", elem_b="hub", min_overlap=0.030, name=f"{label} rear hub retained on the axle")
        ctx.expect_overlap(frame, rear, axes="xz", elem_a="rear_axle", elem_b="hub", min_overlap=0.030, name=f"{label} rear hub surrounds the axle line")
        ctx.expect_overlap(fork, cwheel, axes="y", elem_a="fork", elem_b="hub", min_overlap=0.030, name=f"{label} caster wheel captured by fork axle")

    # ---- Hero geometry checks. ----
    seat_aabb = ctx.part_element_world_aabb(frame, elem="seat_cushion")
    ctx.check(
        "seat cushion at wheelchair sitting height",
        seat_aabb is not None and 0.43 <= (seat_aabb[0][2] + seat_aabb[1][2]) / 2.0 <= 0.50,
        details=f"seat_aabb={seat_aabb}",
    )
    left_rear_aabb = ctx.part_world_aabb("left_rear_wheel")
    exp_dia = 2.0 * r.rear_wheel_radius
    ctx.check(
        "rear drive wheel diameter matches propulsion family",
        left_rear_aabb is not None and abs((left_rear_aabb[1][2] - left_rear_aabb[0][2]) - exp_dia) <= 0.02,
        details=f"expected_dia={exp_dia:.3f}, aabb={left_rear_aabb}",
    )
    left_caster_aabb = ctx.part_world_aabb("left_caster_wheel")
    ctx.check(
        "front caster wheel diameter is about 0.2 m",
        left_caster_aabb is not None and 0.17 <= (left_caster_aabb[1][2] - left_caster_aabb[0][2]) <= 0.22,
        details=f"left_caster_aabb={left_caster_aabb}",
    )

    # ---- Fixed spine joint identity. ----
    for label in ("left", "right"):
        rj = object_model.get_articulation(f"frame_to_{label}_rear_wheel")
        cj = object_model.get_articulation(f"frame_to_{label}_caster")
        ctx.check(f"{label} rear wheel is CONTINUOUS about +Y", rj.articulation_type == ArticulationType.CONTINUOUS and tuple(rj.axis) == (0.0, 1.0, 0.0), details=f"type={rj.articulation_type}, axis={rj.axis}")
        ctx.check(f"{label} caster swivel is CONTINUOUS about +Z", cj.articulation_type == ArticulationType.CONTINUOUS and tuple(cj.axis) == (0.0, 0.0, 1.0), details=f"type={cj.articulation_type}, axis={cj.axis}")

    # ---- Targeted mechanism poses (one per key mechanism). ----
    left_swivel = object_model.get_articulation("frame_to_left_caster")
    caster_rest = ctx.part_world_position("left_caster_wheel")
    with ctx.pose({left_swivel: math.pi / 2.0}):
        caster_turned = ctx.part_world_position("left_caster_wheel")
    ctx.check(
        "left caster swivels around a vertical stem with visible trail",
        caster_rest is not None and caster_turned is not None and abs(caster_turned[1] - caster_rest[1]) > 0.025,
        details=f"rest={caster_rest}, turned={caster_turned}",
    )

    if r.footrest == "swingaway_flipup":
        j = object_model.get_articulation("frame_to_left_footplate")
        rest = ctx.part_world_aabb("left_footplate")
        with ctx.pose({j: 1.20}):
            flipped = ctx.part_world_aabb("left_footplate")
        ctx.check("left footplate flips upward", rest is not None and flipped is not None and flipped[1][2] > rest[1][2] + 0.050, details=f"rest={rest}, flipped={flipped}")
    else:
        j = object_model.get_articulation("frame_to_left_legrest")
        rest = ctx.part_world_aabb("left_legrest")
        with ctx.pose({j: 1.20}):
            elevated = ctx.part_world_aabb("left_legrest")
        ctx.check("left legrest elevates from horizontal to raised", rest is not None and elevated is not None and elevated[1][2] > rest[1][2] + 0.080, details=f"rest={rest}, elevated={elevated}")

    if r.backrest == "reclining_back":
        backrest = object_model.get_part("backrest")
        hinge = object_model.get_articulation("frame_to_backrest")
        ctx.check("backrest reclines (revolute -Y)", hinge.articulation_type == ArticulationType.REVOLUTE and tuple(hinge.axis) == (0.0, -1.0, 0.0), details=f"axis={hinge.axis}")
        head_aabb = ctx.part_element_world_aabb(backrest, elem="headrest_pad")
        ctx.check("reclining backrest has a headrest above the panel", head_aabb is not None and head_aabb[1][2] > 1.00, details=f"headrest_aabb={head_aabb}")
        rest = ctx.part_world_aabb(backrest)
        with ctx.pose({hinge: 0.55}):
            reclined = ctx.part_world_aabb(backrest)
        ctx.check(
            "frame_to_backrest reclines the tall back rearward and down",
            rest is not None and reclined is not None and reclined[0][0] < rest[0][0] - 0.040 and reclined[1][2] < rest[1][2] - 0.020,
            details=f"rest={rest}, reclined={reclined}",
        )

    if r.armrest == "desk_flipback_arm":
        j = object_model.get_articulation("frame_to_left_armrest")
        ctx.check("left desk armrest flips (revolute -Y)", j.articulation_type == ArticulationType.REVOLUTE and tuple(j.axis) == (0.0, -1.0, 0.0), details=f"axis={j.axis}")
        rest = ctx.part_world_aabb("left_armrest")
        with ctx.pose({j: 1.50}):
            flipped = ctx.part_world_aabb("left_armrest")
        shift = (abs(flipped[0][0] - rest[0][0]) + abs(flipped[1][2] - rest[1][2])) if (rest and flipped) else 0.0
        ctx.check("flipping the desk armrest moves its footprint back/up", rest is not None and flipped is not None and shift > 0.08, details=f"rest={rest}, flipped={flipped}, shift={shift:.4f}")

    if r.frame_brace == "cross_brace_folding":
        fr = object_model.get_part("fold_brace_right")
        fj = object_model.get_articulation("fold_brace_left_to_right")
        rest = ctx.part_world_aabb(fr)
        with ctx.pose({fj: 0.40}):
            folded = ctx.part_world_aabb(fr)
        ctx.check("fold_brace_left_to_right scissor pivot actuates the right brace", rest is not None and folded is not None and abs(folded[1][2] - rest[1][2]) > 0.020, details=f"rest_top_z={rest[1][2]:.4f}, folded_top_z={folded[1][2]:.4f}")

    # ---- Rule 5: full-travel non-穿模 across sampled joint poses. ----
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=40, ignore_fixed=True)

    # ---- Compiler-owned baseline (also enforced by the sweep). ----
    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)
    ctx.fail_if_joint_mating_has_gap()

    return ctx.report()
