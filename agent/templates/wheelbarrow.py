# SPDX-License-Identifier: Apache-2.0

"""Wheelbarrow — modular procedural template.

A single-wheel wheelbarrow: a grounded rigid ``frame``/``chassis`` (tray +
two tubular handles + rear support legs/feet + a fork/axle interface) that
carries exactly ONE ``front_wheel`` spinning about the lateral (side) axis
through the sole always-on CONTINUOUS ``wheel_spin`` joint. The default
mature domain is single-DOF: only ``wheel_spin`` moves. A GATED
``aux_articulation`` slot may add a second DOF on the rear support only
(folding rear stand / paired level feet) — the tray itself never
articulates — and defaults to ``none``.

This template uses the slot/module/assembler abstraction in
``agent.templates._modular``. Five slots:

  chassis_body (root) → rear_support_detail → wheel_mount → front_wheel
                                                  ↑              ↑
                                          (fork/axle)     CONTINUOUS wheel_spin
                      → aux_articulation (gated second DOF / multiplicity)

Topology is *mixed* (per the spec):

  * ``chassis_body`` is the root. It emits the ``frame`` part and (for split
    variants) extra FIXED ``tray`` / ``rear_legs`` parts parented internally
    to the frame (parallel-children pattern, like dj_equipment).
  * ``rear_support_detail`` fuses rear legs/feet into the frame as visuals,
    or (for tube_legs) attaches a FIXED ``rear_legs`` part — anchored on the
    frame, parallel-children style (no upstream interface).
  * ``wheel_mount`` is the structural bridge to the wheel. For the
    ``integrated`` anchor the fork/axle is built directly into the frame and
    the wheel's parent is the frame. For ``fork_module`` / ``axle_module``
    the fork (and axle) are separate FIXED parts. For ``axle_root`` the axle
    is the chain anchor and the body pivots on it. In every case wheel_mount
    exposes a ``downstream`` interface at the axle center so the next slot
    chains the wheel onto it.
  * ``front_wheel`` exposes an ``upstream`` interface whose
    ``consumer_joint_type`` is CONTINUOUS — that is the assembler-emitted
    ``rear_support_detail`` / ``wheel_mount`` → ``front_wheel`` chain joint:
    the sole always-on ``wheel_spin`` DOF. The hub is centered on the part
    origin (0,0,0) so the joint origin lies in the wheel's visuals.
  * ``aux_articulation`` is the gated optional second DOF, parented to the
    frame and acting only on a separate rear-support part (a folding stand or
    paired leveling feet). The tray stays rigidly FIXED. It defaults to
    ``none`` (single-DOF mature domain).

Coordinate frame: Z-up. ``body_axis`` selects the body long axis:
  * ``x_forward`` (anchor): wheel is at +x, handles at -x, wheel_spin axis
    = (0, 1, 0) (side / lateral).
  * ``y_forward`` is accepted for compatibility, but sampled seeds use the
    canonical x_forward layout so the wheel reads like a normal side-view
    wheelbarrow wheel: vertical disk, axle through the body width.

seed == 0 picks the anchor combination: monolithic_frame + tube_legs_with_pads
+ integrated_fork_axle + sdk_wheel_tire_geometry + aux=none + x_forward,
reproducing the canonical single_wheel_wheelbarrow topology
(rec_wheelbarrow_9de7eb...). Other seeds RNG-pick uniformly per slot.

Adopted sources (see spec Adopted Source Index):
  S2  9de7eb — monolithic frame, integrated fork/axle, SDK wheel/tire
  S3/4/5 0002 — stacked-cylinder wheel, skid legs, dump tray (Loft)
  S6  cb2aea — bolted-tray split
  S7  1c02a48 — upper_body chain, separate axle module, lathe wheel,
                box-strut legs
  S8  194a0d — full split, torus-annulus wheel, separate fork,
                tube_from_spline legs/pads
  S10 efeca1 — folding rear stand
  S11 2960ce — paired level feet (PRISMATIC multiplicity)
  S12 224ee9 — fold-flat revolute set
  S13 e94d07 — axle-root dump pivot
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
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
    ExtrudeWithHolesGeometry,
    Inertial,
    LatheGeometry,
    MatingContract,
    MeshGeometry,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    TireGeometry,
    TireShoulder,
    TireSidewall,
    TireTread,
    TorusGeometry,
    WheelBore,
    WheelFace,
    WheelGeometry,
    WheelHub,
    WheelRim,
    WheelSpokes,
    mesh_from_geometry,
    rounded_rect_profile,
    tube_from_spline_points,
)

# Modular template: sweep coverage uses module_topology_diversity.
__modular__ = True


# --------------------------------------------------------------------------- #
# Module enums
# --------------------------------------------------------------------------- #


ChassisBodyModule = Literal[
    "monolithic_frame",
    "frame_plus_bolted_tray",
    "upper_body_module_chain",
    "frame_tray_handles_legs_split",
]
WheelMountModule = Literal[
    "integrated_fork_axle",
    "separate_fork_module",
    "separate_axle_module",
    "axle_root_pivot",
]
FrontWheelModule = Literal[
    "sdk_wheel_tire_geometry",
    "lathe_profile_wheel",
    "stacked_cylinder_wheel",
    "torus_annulus_wheel",
]
AuxArticulationModule = Literal[
    "none_single_dof",
    "folding_rear_stand_revolute",
    "level_foot_prismatic",
]
RearSupportModule = Literal[
    "tube_legs_with_pads",
    "box_strut_legs",
    "skid_rest_legs",
]
BodyAxis = Literal["x_forward", "y_forward"]
WheelbarrowPalette = Literal[
    "anchor_green",
    "utility_red",
    "industrial_blue",
    "zinc_gray",
    "powder_orange",
]


WB_PALETTE_PRESETS: dict[str, dict[str, tuple[float, float, float, float]]] = {
    "anchor_green": {
        "tray_paint": (0.08, 0.36, 0.15, 1.0),
        "frame_steel": (0.06, 0.07, 0.07, 1.0),
        "rubber": (0.04, 0.04, 0.04, 1.0),
        "rim_paint": (0.72, 0.06, 0.035, 1.0),
        "axle_steel": (0.55, 0.56, 0.52, 1.0),
        "hub_steel": (0.30, 0.31, 0.34, 1.0),
        "zinc": (0.75, 0.76, 0.78, 1.0),
        "foot_accent": (0.92, 0.48, 0.16, 1.0),
        "grip": (0.10, 0.10, 0.10, 1.0),
    },
    "utility_red": {
        "tray_paint": (0.74, 0.10, 0.08, 1.0),
        "frame_steel": (0.18, 0.20, 0.22, 1.0),
        "rubber": (0.05, 0.05, 0.05, 1.0),
        "rim_paint": (0.73, 0.76, 0.80, 1.0),
        "axle_steel": (0.64, 0.67, 0.70, 1.0),
        "hub_steel": (0.29, 0.30, 0.33, 1.0),
        "zinc": (0.78, 0.80, 0.82, 1.0),
        "foot_accent": (0.92, 0.48, 0.16, 1.0),
        "grip": (0.08, 0.08, 0.08, 1.0),
    },
    "industrial_blue": {
        "tray_paint": (0.18, 0.30, 0.56, 1.0),
        "frame_steel": (0.40, 0.42, 0.45, 1.0),
        "rubber": (0.10, 0.10, 0.10, 1.0),
        "rim_paint": (0.20, 0.34, 0.60, 1.0),
        "axle_steel": (0.75, 0.76, 0.78, 1.0),
        "hub_steel": (0.40, 0.42, 0.45, 1.0),
        "zinc": (0.75, 0.76, 0.78, 1.0),
        "foot_accent": (0.92, 0.48, 0.16, 1.0),
        "grip": (0.09, 0.09, 0.10, 1.0),
    },
    "zinc_gray": {
        "tray_paint": (0.31, 0.39, 0.14, 1.0),
        "frame_steel": (0.17, 0.18, 0.17, 1.0),
        "rubber": (0.06, 0.06, 0.06, 1.0),
        "rim_paint": (0.64, 0.66, 0.69, 1.0),
        "axle_steel": (0.78, 0.80, 0.82, 1.0),
        "hub_steel": (0.29, 0.30, 0.33, 1.0),
        "zinc": (0.78, 0.80, 0.82, 1.0),
        "foot_accent": (0.85, 0.50, 0.18, 1.0),
        "grip": (0.12, 0.12, 0.12, 1.0),
    },
    "powder_orange": {
        "tray_paint": (0.86, 0.42, 0.10, 1.0),
        "frame_steel": (0.14, 0.15, 0.16, 1.0),
        "rubber": (0.05, 0.05, 0.05, 1.0),
        "rim_paint": (0.20, 0.20, 0.22, 1.0),
        "axle_steel": (0.62, 0.64, 0.66, 1.0),
        "hub_steel": (0.33, 0.34, 0.37, 1.0),
        "zinc": (0.75, 0.76, 0.78, 1.0),
        "foot_accent": (0.20, 0.20, 0.22, 1.0),
        "grip": (0.10, 0.10, 0.10, 1.0),
    },
}


# --------------------------------------------------------------------------- #
# Config dataclasses
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class WheelbarrowConfig:
    """Public wheelbarrow config. Module selection is opt-in: leave any module
    field as ``None`` to let ``config_from_seed`` / ``resolve_config`` fill in
    the anchor default.

    The continuous dimensions describe the canonical x-forward envelope: the
    tray + handles run from the wheel at +x back to the grips at -x; rear legs
    drop down behind the tray. ``wheel_radius`` is the big-wheel constraint
    driver (kept > 0.55 × frame_height).
    """

    chassis_body_module: ChassisBodyModule | None = None
    wheel_mount_module: WheelMountModule | None = None
    front_wheel_module: FrontWheelModule | None = None
    aux_articulation_module: AuxArticulationModule | None = None
    rear_support_module: RearSupportModule | None = None
    body_axis: BodyAxis = "x_forward"
    palette_theme: WheelbarrowPalette = "anchor_green"

    # Envelope (x-forward canonical frame).
    overall_length: float = 1.35
    track_width: float = 0.62
    frame_height: float = 0.74

    # Tray
    tray_len: float = 0.66
    tray_width: float = 0.56
    tray_depth: float = 0.24

    # Wheel
    wheel_radius: float = 0.205
    wheel_width: float = 0.110
    hub_radius: float = 0.048
    fork_clearance: float = 0.012

    # Aux DOF limits (only used in their gated branch).
    dump_limit: float = 0.55
    stand_fold_limit: float = 1.25
    foot_travel: float = 0.045

    palette: dict[str, tuple[float, float, float, float]] = field(
        default_factory=lambda: dict(WB_PALETTE_PRESETS["anchor_green"])
    )


@dataclass(frozen=True)
class ResolvedWheelbarrowConfig:
    """Dimension-clamped + module-resolved config consumed by builders.

    Adds derived geometry: ``axle_x`` / ``axle_z`` (wheel axle center in the
    canonical frame), ``fork_gap`` (clear span between the fork plates =
    wheel_width + 2·fork_clearance), ``wheel_spin_axis`` (lateral side axis
    derived from ``body_axis``), and ``body_yaw`` (frame z-rotation for
    y_forward).
    """

    chassis_body_module: ChassisBodyModule
    wheel_mount_module: WheelMountModule
    front_wheel_module: FrontWheelModule
    aux_articulation_module: AuxArticulationModule
    rear_support_module: RearSupportModule
    body_axis: BodyAxis
    palette_theme: WheelbarrowPalette

    overall_length: float
    track_width: float
    frame_height: float
    tray_len: float
    tray_width: float
    tray_depth: float
    wheel_radius: float
    wheel_width: float
    hub_radius: float
    fork_clearance: float
    dump_limit: float
    stand_fold_limit: float
    foot_travel: float

    # Derived
    axle_x: float
    axle_z: float
    fork_gap: float
    wheel_spin_axis: tuple[float, float, float]
    body_yaw: float

    palette: dict[str, tuple[float, float, float, float]]


# --------------------------------------------------------------------------- #
# Seed-driven sampling
# --------------------------------------------------------------------------- #


_CHASSIS_CHOICES: tuple[ChassisBodyModule, ...] = (
    "monolithic_frame",
    "frame_plus_bolted_tray",
    "upper_body_module_chain",
    "frame_tray_handles_legs_split",
)
_WHEEL_MOUNT_CHOICES: tuple[WheelMountModule, ...] = (
    "integrated_fork_axle",
    "separate_fork_module",
    "separate_axle_module",
    "axle_root_pivot",
)
_WHEEL_CHOICES: tuple[FrontWheelModule, ...] = (
    "sdk_wheel_tire_geometry",
    "lathe_profile_wheel",
    "stacked_cylinder_wheel",
    "torus_annulus_wheel",
)
_AUX_CHOICES: tuple[AuxArticulationModule, ...] = (
    "none_single_dof",
    "folding_rear_stand_revolute",
    "level_foot_prismatic",
)
_REAR_CHOICES: tuple[RearSupportModule, ...] = (
    "tube_legs_with_pads",
    "box_strut_legs",
    "skid_rest_legs",
)
_BODY_AXIS_CHOICES: tuple[BodyAxis, ...] = ("x_forward", "y_forward")
_SAMPLED_BODY_AXIS_CHOICES: tuple[BodyAxis, ...] = ("x_forward",)


def config_from_seed(seed: int) -> WheelbarrowConfig:
    """Sample a wheelbarrow configuration for the given seed.

    seed == 0 returns the anchor combination (monolithic_frame +
    integrated_fork_axle + sdk_wheel_tire_geometry + aux=none +
    tube_legs_with_pads + x_forward) at canonical dimensions. Other seeds
    RNG-pick modules uniformly per slot and sample continuous dimensions.

    ``aux_articulation`` only ever moves a separate rear-support part (a
    folding stand or paired leveling feet) — the tray never articulates. It is
    gated to ``none`` under ``axle_root_pivot`` so that mount stays a clean
    single-DOF topology.
    """
    if seed == 0:
        return WheelbarrowConfig(
            chassis_body_module="monolithic_frame",
            wheel_mount_module="integrated_fork_axle",
            front_wheel_module="sdk_wheel_tire_geometry",
            aux_articulation_module="none_single_dof",
            rear_support_module="tube_legs_with_pads",
            body_axis="x_forward",
            palette_theme="anchor_green",
        )

    rng = random.Random(seed)
    chassis = rng.choice(_CHASSIS_CHOICES)
    wheel_mount = rng.choice(_WHEEL_MOUNT_CHOICES)
    wheel = rng.choice(_WHEEL_CHOICES)
    aux = rng.choice(_AUX_CHOICES)
    rear = rng.choice(_REAR_CHOICES)
    rng.choice(_BODY_AXIS_CHOICES)
    body_axis = "x_forward"
    palette_theme = rng.choice(tuple(WB_PALETTE_PRESETS.keys()))

    aux = _gate_aux(aux, chassis=chassis, wheel_mount=wheel_mount)

    overall_length = round(rng.uniform(1.05, 1.55), 4)
    track_width = round(rng.uniform(0.56, 0.78), 4)
    frame_height = round(rng.uniform(0.66, 0.82), 4)
    tray_len = round(rng.uniform(0.58, 0.74), 4)
    tray_width = round(rng.uniform(0.50, 0.64), 4)
    tray_depth = round(rng.uniform(0.20, 0.30), 4)
    wheel_radius = round(rng.uniform(0.165, 0.235), 4)
    wheel_width = round(rng.uniform(0.090, 0.125), 4)
    hub_radius = round(rng.uniform(0.040, 0.056), 4)
    dump_limit = round(rng.uniform(0.46, 0.76), 4)
    stand_fold_limit = round(rng.uniform(1.05, 1.40), 4)
    foot_travel = round(rng.uniform(0.035, 0.058), 4)

    return WheelbarrowConfig(
        chassis_body_module=chassis,
        wheel_mount_module=wheel_mount,
        front_wheel_module=wheel,
        aux_articulation_module=aux,
        rear_support_module=rear,
        body_axis=body_axis,
        palette_theme=palette_theme,
        overall_length=overall_length,
        track_width=track_width,
        frame_height=frame_height,
        tray_len=tray_len,
        tray_width=tray_width,
        tray_depth=tray_depth,
        wheel_radius=wheel_radius,
        wheel_width=wheel_width,
        hub_radius=hub_radius,
        dump_limit=dump_limit,
        stand_fold_limit=stand_fold_limit,
        foot_travel=foot_travel,
    )


def _gate_aux(
    aux: AuxArticulationModule,
    *,
    chassis: ChassisBodyModule,
    wheel_mount: WheelMountModule,
) -> AuxArticulationModule:
    """Drop incompatible aux selections back to ``none`` (single DOF).

    ``axle_root_pivot`` introduces a distinct axle-root part graph; we keep it
    a clean single-DOF topology (only the wheel spins), so any rear-support aux
    collapses to ``none`` under that mount.
    """
    if wheel_mount == "axle_root_pivot":
        return "none_single_dof"
    return aux


def resolve_config(config: WheelbarrowConfig) -> ResolvedWheelbarrowConfig:
    """Validate enums, clamp floats, fill None modules with anchors, and derive
    axle position / fork gap / wheel-spin axis / body yaw."""

    chassis = config.chassis_body_module or "monolithic_frame"
    wheel_mount = config.wheel_mount_module or "integrated_fork_axle"
    wheel = config.front_wheel_module or "sdk_wheel_tire_geometry"
    aux = config.aux_articulation_module or "none_single_dof"
    rear = config.rear_support_module or "tube_legs_with_pads"
    body_axis = config.body_axis or "x_forward"

    if chassis not in _CHASSIS_CHOICES:
        raise ValueError(f"Unsupported chassis_body_module: {chassis}")
    if wheel_mount not in _WHEEL_MOUNT_CHOICES:
        raise ValueError(f"Unsupported wheel_mount_module: {wheel_mount}")
    if wheel not in _WHEEL_CHOICES:
        raise ValueError(f"Unsupported front_wheel_module: {wheel}")
    if aux not in _AUX_CHOICES:
        raise ValueError(f"Unsupported aux_articulation_module: {aux}")
    if rear not in _REAR_CHOICES:
        raise ValueError(f"Unsupported rear_support_module: {rear}")
    if body_axis not in _BODY_AXIS_CHOICES:
        raise ValueError(f"Unsupported body_axis: {body_axis}")
    if str(config.palette_theme) not in WB_PALETTE_PRESETS:
        raise ValueError(f"Unsupported palette_theme: {config.palette_theme}")

    # Re-gate so a directly-built config (not via config_from_seed) also stays
    # in a valid mature domain.
    aux = _gate_aux(aux, chassis=chassis, wheel_mount=wheel_mount)

    overall_length = max(0.95, min(float(config.overall_length), 1.65))
    track_width = max(0.55, min(float(config.track_width), 0.80))
    frame_height = max(0.62, min(float(config.frame_height), 0.86))
    tray_len = max(0.52, min(float(config.tray_len), 0.78))
    tray_width = max(0.46, min(float(config.tray_width), 0.68))
    tray_depth = max(0.18, min(float(config.tray_depth), 0.32))
    wheel_width = max(0.085, min(float(config.wheel_width), 0.130))
    hub_radius = max(0.036, min(float(config.hub_radius), 0.060))

    # Big-wheel constraint: tire DIAMETER > 0.55 * frame_height (matches the
    # S2 5-star check `tire_diameter > 0.55 * frame_height`), i.e.
    # wheel_radius > 0.29 * frame_height. Enforce the floor with a small margin
    # while keeping the radius in a realistic [0.15, 0.245] m band.
    wheel_radius = max(0.150, min(float(config.wheel_radius), 0.245))
    wheel_radius = max(wheel_radius, 0.30 * frame_height)
    wheel_radius = min(wheel_radius, 0.245)

    fork_clearance = max(0.008, min(float(config.fork_clearance), 0.022))
    fork_gap = wheel_width + 2.0 * fork_clearance

    dump_limit = max(0.45, min(float(config.dump_limit), 0.78))
    stand_fold_limit = max(1.0, min(float(config.stand_fold_limit), 1.45))
    foot_travel = max(0.030, min(float(config.foot_travel), 0.060))

    # Axle center in the canonical x-forward frame: front of the body, at a
    # height that keeps the big wheel's bottom at/just above ground (z=0) and
    # the tray above the wheel.
    axle_z = wheel_radius + 0.020
    axle_x = 0.5 * overall_length + 0.10

    wheel_spin_axis = (0.0, 1.0, 0.0)
    body_yaw = 0.0

    palette = dict(WB_PALETTE_PRESETS[config.palette_theme])

    return ResolvedWheelbarrowConfig(
        chassis_body_module=chassis,
        wheel_mount_module=wheel_mount,
        front_wheel_module=wheel,
        aux_articulation_module=aux,
        rear_support_module=rear,
        body_axis=body_axis,
        palette_theme=config.palette_theme,
        overall_length=overall_length,
        track_width=track_width,
        frame_height=frame_height,
        tray_len=tray_len,
        tray_width=tray_width,
        tray_depth=tray_depth,
        wheel_radius=wheel_radius,
        wheel_width=wheel_width,
        hub_radius=hub_radius,
        fork_clearance=fork_clearance,
        dump_limit=dump_limit,
        stand_fold_limit=stand_fold_limit,
        foot_travel=foot_travel,
        axle_x=axle_x,
        axle_z=axle_z,
        fork_gap=fork_gap,
        wheel_spin_axis=wheel_spin_axis,
        body_yaw=body_yaw,
        palette=palette,
    )


# --------------------------------------------------------------------------- #
# Mesh / shape helpers (adapted from S1/S2 _origin_between/_tube + S8 annulus)
# --------------------------------------------------------------------------- #


def _origin_between(
    start: tuple[float, float, float],
    end: tuple[float, float, float],
) -> tuple[Origin, float]:
    """Cylinder origin/length with local +Z aligned start→end.

    Adapted verbatim from S2 (rec_9de7eb model.py:L39-L55).
    """
    sx, sy, sz = start
    ex, ey, ez = end
    vx, vy, vz = ex - sx, ey - sy, ez - sz
    length = math.sqrt(vx * vx + vy * vy + vz * vz)
    if length <= 1e-9:
        raise ValueError("Cannot build a zero-length tube")
    nx, ny, nz = vx / length, vy / length, vz / length
    horizontal = math.sqrt(nx * nx + ny * ny)
    pitch = math.atan2(horizontal, nz)
    yaw = math.atan2(ny, nx) if horizontal > 1e-9 else 0.0
    return Origin(xyz=((sx + ex) / 2, (sy + ey) / 2, (sz + ez) / 2), rpy=(0.0, pitch, yaw)), length


def _tube(
    part,
    start: tuple[float, float, float],
    end: tuple[float, float, float],
    radius: float,
    *,
    material: str,
    name: str,
) -> None:
    """A straight cylindrical tube between two points (S2 _tube helper)."""
    origin, length = _origin_between(start, end)
    part.visual(Cylinder(radius=radius, length=length), origin=origin, material=material, name=name, material_class_id="metal.steel_bare")


def _spline_tube(points, *, radius: float, name: str):
    """Mesh of a swept tube through spline points (S7/S8 tube_from_spline)."""
    return mesh_from_geometry(
        tube_from_spline_points(
            list(points),
            radius=radius,
            samples_per_segment=14,
            radial_segments=16,
            cap_ends=True,
        ),
        name,
    )


def _circle_profile(radius: float, *, segments: int = 40) -> list[tuple[float, float]]:
    """Circle profile (S8 circle_profile helper)."""
    return [
        (
            radius * math.cos((2.0 * math.pi * i) / segments),
            radius * math.sin((2.0 * math.pi * i) / segments),
        )
        for i in range(segments)
    ]


def _annulus_mesh(
    outer_radius: float,
    inner_radius: float,
    thickness: float,
    *,
    segments: int = 40,
) -> MeshGeometry:
    """Annular extruded ring (S8 annulus_mesh helper)."""
    return ExtrudeWithHolesGeometry(
        _circle_profile(outer_radius, segments=segments),
        [_circle_profile(inner_radius, segments=segments)],
        thickness,
        center=True,
        closed=True,
    )


def _tapered_tray_mesh(r: ResolvedWheelbarrowConfig, *, z0: float) -> MeshGeometry:
    """Tapered open tray shell with real wall thickness (S1/S2 _tray_shell).

    Adapted from S2 (rec_9de7eb model.py:L93-L115). Parameterized to the
    config's tray footprint; ``z0`` is the bottom of the tray in part frame.
    """
    L = r.tray_len
    W = r.tray_width
    D = r.tray_depth
    wall = 0.05
    mesh = MeshGeometry()
    sections = {
        "outer_bottom": (L * 0.66, W * 0.57, 0.045, 0.0, 0.0, z0 + 0.005),
        "outer_top": (L, W, 0.085, 0.0, 0.0, z0 + D),
        "inner_top": (L - 2.0 * wall, W - 2.0 * wall, 0.055, 0.0, 0.0, z0 + D - 0.02),
        "inner_bottom": (L * 0.50, W * 0.40, 0.030, 0.0, 0.0, z0 + 0.025),
    }
    loops: dict[str, list[int]] = {}
    for key, (length, width, radius, cx, cy, z) in sections.items():
        loop: list[int] = []
        for px, py in rounded_rect_profile(length, width, radius, corner_segments=8):
            loop.append(mesh.add_vertex(px + cx, py + cy, z))
        loops[key] = loop

    def _ring(outer: list[int], inner: list[int]) -> None:
        count = len(outer)
        for i in range(count):
            j = (i + 1) % count
            mesh.add_face(outer[i], outer[j], inner[j])
            mesh.add_face(outer[i], inner[j], inner[i])

    def _cap(loop: list[int], *, reverse: bool) -> None:
        center = mesh.add_vertex(
            sum(mesh.vertices[i][0] for i in loop) / len(loop),
            sum(mesh.vertices[i][1] for i in loop) / len(loop),
            sum(mesh.vertices[i][2] for i in loop) / len(loop),
        )
        for i in range(len(loop)):
            j = (i + 1) % len(loop)
            if reverse:
                mesh.add_face(center, loop[j], loop[i])
            else:
                mesh.add_face(center, loop[i], loop[j])

    _ring(loops["outer_bottom"], loops["outer_top"])
    _ring(loops["outer_top"], loops["inner_top"])
    _ring(loops["inner_top"], loops["inner_bottom"])
    _cap(loops["outer_bottom"], reverse=True)
    _cap(loops["inner_bottom"], reverse=False)
    return mesh


# --------------------------------------------------------------------------- #
# Wheel construction helpers (one per Slot C candidate — Rule 3: preserve
# primitive types from each cited source).
# --------------------------------------------------------------------------- #
#
# Every wheel module centers its hub on the part origin (0, 0, 0) and lays the
# spin axis along the part-frame y-axis (lateral). The upstream chain joint
# (wheel_spin) is positioned at the parent's axle center, so the wheel's
# (0,0,0) coincides with the joint origin (satisfies origin-in-geometry).


def _build_sdk_wheel(part, r: ResolvedWheelbarrowConfig) -> None:
    """SDK TireGeometry + WheelGeometry high-fidelity wheel (S2 L160-L190).

    Hub centered on origin; tire/rim rotated about z by 90° so the spin axis
    is the part-frame y-axis (matching S2's rpy=(0,0,pi/2)).
    """
    R = r.wheel_radius
    width = r.wheel_width
    hub_r = r.hub_radius
    inner_r = R * 0.69
    rim_inner = R * 0.44
    tire_mesh = mesh_from_geometry(
        TireGeometry(
            R,
            width,
            inner_radius=inner_r,
            tread=TireTread(style="block", depth=0.010, count=22, land_ratio=0.55),
            sidewall=TireSidewall(style="square", bulge=0.025),
            shoulder=TireShoulder(width=0.010, radius=0.004),
        ),
        "front_utility_tire",
    )
    rim_mesh = mesh_from_geometry(
        WheelGeometry(
            inner_r,
            width * 0.71,
            rim=WheelRim(
                inner_radius=rim_inner,
                flange_height=0.012,
                flange_thickness=0.006,
                bead_seat_depth=0.005,
            ),
            hub=WheelHub(
                radius=hub_r,
                width=width * 0.78,
                cap_style="domed",
                bolt_pattern=BoltPattern(
                    count=4, circle_diameter=hub_r * 1.15, hole_diameter=0.007
                ),
            ),
            face=WheelFace(dish_depth=0.010, front_inset=0.004, rear_inset=0.004),
            spokes=WheelSpokes(style="straight", count=6, thickness=0.007, window_radius=0.016),
            bore=WheelBore(style="round", diameter=0.020),
        ),
        "front_rim",
    )
    part.visual(
        tire_mesh, origin=Origin(rpy=(0.0, 0.0, math.pi / 2)), material="rubber", name="tire", material_class_id="rubber.directional_grooved"
    )
    part.visual(
        rim_mesh, origin=Origin(rpy=(0.0, 0.0, math.pi / 2)), material="rim_paint", name="rim", material_class_id="metal.paint_coated"
    )
    part.inertial = Inertial.from_geometry(
        Cylinder(radius=R, length=width),
        mass=4.2,
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
    )


def _build_lathe_wheel(part, r: ResolvedWheelbarrowConfig) -> None:
    """LatheGeometry rotated tire/rim/hub profiles (S2b/S7 L228-L272).

    Profiles are authored around local z, then rotate_x(pi/2) so the rotation
    axis lies along part-frame y (lateral).
    Adapted from S7 (rec_1c02a48 model.py:L312-L378), scaled to wheel_radius.
    """
    R = r.wheel_radius
    half_w = r.wheel_width * 0.5
    hub_r = r.hub_radius
    # tire profile: outer tread band tapering to bead seat (radius, axial)
    tire_profile = [
        (R * 0.50, -half_w * 0.90),
        (R * 0.80, -half_w),
        (R * 0.96, -half_w * 0.72),
        (R, -half_w * 0.22),
        (R, half_w * 0.22),
        (R * 0.96, half_w * 0.72),
        (R * 0.80, half_w),
        (R * 0.50, half_w * 0.90),
        (R * 0.47, half_w * 0.36),
        (R * 0.47, -half_w * 0.36),
        (R * 0.50, -half_w * 0.90),
    ]
    rim_profile = [
        (hub_r * 0.38, -half_w * 0.64),
        (R * 0.30, -half_w * 0.64),
        (R * 0.49, -half_w * 0.36),
        (R * 0.51, -half_w * 0.09),
        (R * 0.51, half_w * 0.09),
        (R * 0.49, half_w * 0.36),
        (R * 0.30, half_w * 0.64),
        (hub_r * 0.38, half_w * 0.64),
        (hub_r * 0.38, half_w * 0.32),
        (R * 0.26, half_w * 0.32),
        (R * 0.38, 0.0),
        (R * 0.26, -half_w * 0.32),
        (hub_r * 0.38, -half_w * 0.32),
        (hub_r * 0.38, -half_w * 0.64),
    ]
    hub_outer_profile = [
        (hub_r * 0.38, -half_w * 1.35),
        (hub_r * 0.55, -half_w * 1.35),
        (hub_r * 0.72, -half_w * 1.08),
        (hub_r * 0.84, -half_w * 0.54),
        (hub_r * 0.84, half_w * 0.54),
        (hub_r * 0.72, half_w * 1.08),
        (hub_r * 0.55, half_w * 1.35),
        (hub_r * 0.38, half_w * 1.35),
    ]
    # Axle bore. Capped at 14 mm so the wheel_spin joint origin (the wheel
    # center) always stays within 15 mm of the bore wall — with big hubs an
    # uncapped hub_r*0.30 bore fails fail_if_articulation_origin_far_from_geometry.
    bore_r = min(hub_r * 0.30, 0.014)
    hub_inner_profile = [
        (bore_r, -half_w * 1.35),
        (bore_r, half_w * 1.35),
    ]
    part.visual(
        mesh_from_geometry(
            LatheGeometry(tire_profile, segments=64).rotate_x(math.pi / 2.0), "lathe_tire"
        ),
        material="rubber",
        name="tire", material_class_id="rubber.directional_grooved",
    )
    part.visual(
        mesh_from_geometry(
            LatheGeometry(rim_profile, segments=56).rotate_x(math.pi / 2.0), "lathe_rim"
        ),
        material="rim_paint",
        name="rim", material_class_id="metal.paint_coated",
    )
    part.visual(
        mesh_from_geometry(
            LatheGeometry.from_shell_profiles(
                hub_outer_profile,
                hub_inner_profile,
                segments=48,
                start_cap="flat",
                end_cap="flat",
            ).rotate_x(math.pi / 2.0),
            "lathe_hub",
        ),
        material="hub_steel",
        name="hub", material_class_id="metal.steel_bare",
    )
    part.inertial = Inertial.from_geometry(
        Cylinder(radius=R, length=r.wheel_width),
        mass=4.6,
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
    )


def _build_stacked_cylinder_wheel(part, r: ResolvedWheelbarrowConfig) -> None:
    """Stacked coaxial Cylinder wheel + radial tube spokes (S3 L89-L139).

    Adapted from rec_0002 ``_wheel_visual``. Spin axis along part-frame y via
    rpy=(pi/2,0,0). The spoke set is authored as thin cylinders in the wheel's
    x-z plane so the front view reads as a real utility-wheel hub, not as flat
    slabs on the tire face.
    """
    R = r.wheel_radius
    width = r.wheel_width
    hub_r = r.hub_radius
    spin_rpy = (math.pi / 2.0, 0.0, 0.0)
    part.visual(
        Cylinder(radius=R, length=width),
        origin=Origin(rpy=spin_rpy),
        material="rubber",
        name="tire", material_class_id="rubber.directional_grooved",
    )
    part.visual(
        Cylinder(radius=R * 0.82, length=width * 0.76),
        origin=Origin(rpy=spin_rpy),
        material="rubber",
        name="tire_sidewall", material_class_id="rubber.smooth_plain",
    )
    part.visual(
        Cylinder(radius=R * 0.65, length=width * 0.61),
        origin=Origin(rpy=spin_rpy),
        material="rim_paint",
        name="rim_band", material_class_id="metal.paint_coated",
    )
    part.visual(
        Cylinder(radius=hub_r * 1.50, length=width * 0.87),
        origin=Origin(rpy=spin_rpy),
        material="hub_steel",
        name="hub_shell", material_class_id="metal.steel_bare",
    )
    part.visual(
        Cylinder(radius=hub_r * 0.54, length=width * 1.28),
        origin=Origin(rpy=spin_rpy),
        material="hub_steel",
        name="axle_sleeve", material_class_id="metal.steel_bare",
    )
    for index in range(6):
        angle = (2.0 * math.pi * index) / 6.0
        radial = (math.cos(angle), 0.0, math.sin(angle))
        _tube(
            part,
            (radial[0] * hub_r * 1.35, 0.0, radial[2] * hub_r * 1.35),
            (radial[0] * R * 0.58, 0.0, radial[2] * R * 0.58),
            0.0055,
            material="hub_steel",
            name=f"spoke_{index}",
        )
    part.inertial = Inertial.from_geometry(
        Cylinder(radius=R, length=width),
        mass=4.2,
        origin=Origin(rpy=spin_rpy),
    )


def _build_torus_annulus_wheel(part, r: ResolvedWheelbarrowConfig) -> None:
    """Torus tread + extruded annulus rim/disc/hub (S8 L478-L512).

    Adapted from rec_194a0d. The torus + annuli are authored about the local
    z-axis then rotate_x(pi/2) so the wheel axis lies along part-frame y.
    """
    R = r.wheel_radius
    half_w = r.wheel_width * 0.5
    hub_r = r.hub_radius
    tube_r = half_w * 0.85
    tread_center_r = R - tube_r
    tire_geom = TorusGeometry(tread_center_r, tube_r, radial_segments=24, tubular_segments=48)
    tire_geom.rotate_x(math.pi / 2.0)
    rim_geom = _annulus_mesh(tread_center_r * 0.82, R * 0.42, r.wheel_width * 0.60, segments=48)
    rim_geom.rotate_x(math.pi / 2.0)
    disc_l = _annulus_mesh(R * 0.46, hub_r * 0.90, 0.006, segments=48)
    disc_l.rotate_x(math.pi / 2.0).translate(0.0, half_w * 0.30, 0.0)
    disc_r = _annulus_mesh(R * 0.46, hub_r * 0.90, 0.006, segments=48)
    disc_r.rotate_x(math.pi / 2.0).translate(0.0, -half_w * 0.30, 0.0)
    hub_geom = _annulus_mesh(hub_r, hub_r * 0.26, r.wheel_width * 0.66, segments=40)
    hub_geom.rotate_x(math.pi / 2.0)
    part.visual(mesh_from_geometry(tire_geom, "torus_tire"), material="rubber", name="tire", material_class_id="rubber.directional_grooved")
    part.visual(mesh_from_geometry(rim_geom, "torus_rim"), material="rim_paint", name="rim", material_class_id="metal.paint_coated")
    part.visual(mesh_from_geometry(disc_l, "torus_disc_left"), material="zinc", name="disc_left", material_class_id="metal.steel_galvanized")
    part.visual(mesh_from_geometry(disc_r, "torus_disc_right"), material="zinc", name="disc_right", material_class_id="metal.steel_galvanized")
    part.visual(mesh_from_geometry(hub_geom, "torus_hub"), material="hub_steel", name="hub", material_class_id="metal.steel_bare")
    part.inertial = Inertial.from_geometry(
        Cylinder(radius=R, length=r.wheel_width),
        mass=4.8,
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
    )


_WHEEL_BUILDERS = {
    "sdk_wheel_tire_geometry": _build_sdk_wheel,
    "lathe_profile_wheel": _build_lathe_wheel,
    "stacked_cylinder_wheel": _build_stacked_cylinder_wheel,
    "torus_annulus_wheel": _build_torus_annulus_wheel,
}

# Wheel modules whose spoke/disc geometry is genuinely multi-piece; every piece
# must physically touch the hub/rim (the island check has no allowance path).
_MULTI_PIECE_WHEELS = {"stacked_cylinder_wheel", "torus_annulus_wheel"}


# --------------------------------------------------------------------------- #
# Frame visual helpers — shared tray / handle / brace geometry on the frame.
# --------------------------------------------------------------------------- #


def _bed_rail_params(r: ResolvedWheelbarrowConfig) -> tuple[float, float, float]:
    """(rear y, rear z, front-at-fork y) of the under-tray bed rail centerline."""
    W = r.tray_width * 0.5
    z0 = _tray_z0(r)
    bed_y = W * 0.6  # outboard enough to carry the box-strut legs + flat trays
    bed_z = z0 - 0.010  # rail top ~ z0+0.006: the tray rests on these two rails
    fork_bed_y = r.fork_gap * 0.5 + 0.012
    return bed_y, bed_z, fork_bed_y


def _bed_rail_point(r: ResolvedWheelbarrowConfig, x: float) -> tuple[float, float]:
    """(y, z) of the +y bed rail centerline at longitudinal station ``x``."""
    L = r.tray_len * 0.5
    ax, az = r.axle_x, r.axle_z
    bed_y, bed_z, fork_bed_y = _bed_rail_params(r)
    t = (x - (-L - 0.02)) / (ax - (-L - 0.02))
    t = 0.0 if t < 0.0 else (1.0 if t > 1.0 else t)
    return (bed_y + t * (fork_bed_y - bed_y), bed_z + t * ((az + 0.006) - bed_z))


def _emit_tray_mount_stays(frame, r: ResolvedWheelbarrowConfig, *, z0: float) -> None:
    """Bolt-on mounting stays welding the lofted tray shell onto the bed rails.

    The tapered shell's bottom (footprint 0.66L x 0.57W at z0+0.005) floats
    ~30-55 mm above the sloping bed rails, so without these the whole
    tray_shell + rim-tube cluster is a disconnected island inside ``frame``.
    Each stay is a short box column that (a) engulfs the local bed-rail
    centerline and (b) sinks ~11 mm into the solid shell-bottom slab
    (z0+0.005 .. z0+0.025, below the inner floor so nothing pokes into the
    bowl). Same-part overlaps are legal, so both ends embed generously."""
    L = r.tray_len * 0.5
    for xs, sfx_x in ((-L * 0.42, "rear"), (L * 0.10, "front")):
        ry, rz = _bed_rail_point(r, xs)
        top_z = z0 + 0.016
        bot_z = rz - 0.020  # below the rail centerline: the rail runs through it
        for sign, sfx in ((1.0, "l"), (-1.0, "r")):
            frame.visual(
                Box((0.050, 0.032, top_z - bot_z)),
                origin=Origin(xyz=(xs, sign * ry, (top_z + bot_z) * 0.5)),
                material="frame_steel",
                name=f"tray_stay_{sfx_x}_{sfx}", material_class_id="metal.steel_bare",
            )


def _emit_handles_and_braces(frame, r: ResolvedWheelbarrowConfig) -> None:
    """Connected frame weldment (mirrors the 5-star anchor S2 L135-L158).

    The two HANDLE rails are the backbone: each runs from a rear grip, flanks
    the tray side wall, and hands off to the fork arm at the front. An
    under-tray ladder (two bed rails + cross rungs) carries the tray floor from
    below; short posts behind the tray tie the handles down to the ladder; the
    rear mount tubes (rear-leg / aux-hinge datums) ride on the ladder. Every
    member overlaps another, so nothing floats, and nothing rises into the bowl.
    """
    z0 = _tray_z0(r)
    L = r.tray_len * 0.5
    W = r.tray_width * 0.5
    rear_x = -r.overall_length * 0.5
    ax, az = r.axle_x, r.axle_z
    half_gap = r.fork_gap * 0.5

    # --- Handle rails (backbone): flank the tray walls, slope down to the fork.
    rail_y = W + 0.006  # rides against the tray side wall (overlaps it)
    hz_rear = z0 + r.tray_depth * 0.70  # rear grip height, near the rim
    hz_front = z0 - 0.01  # drops to just below the floor at the tray front
    h_front_x = L + 0.02
    # Front hand-off point == root of the fork arm (see _emit_fork_interface),
    # so the handle welds straight onto the fork.
    fork_root = (L - 0.04, half_gap + 0.04, z0 + 0.02)

    def _hpt(x: float, sign: float) -> tuple[float, float, float]:
        t = (x - rear_x) / (h_front_x - rear_x)
        t = 0.0 if t < 0.0 else (1.0 if t > 1.0 else t)
        return (x, sign * rail_y, hz_rear + t * (hz_front - hz_rear))

    for sign, sfx in ((1.0, "0"), (-1.0, "1")):
        _tube(
            frame,
            _hpt(rear_x, sign),
            _hpt(h_front_x, sign),
            0.018,
            material="frame_steel",
            name=f"handle_{sfx}",
        )
        _tube(
            frame,
            _hpt(h_front_x, sign),
            (fork_root[0], sign * fork_root[1], fork_root[2]),
            0.018,
            material="frame_steel",
            name=f"handle_fork_{sfx}",
        )
        gp = _hpt(rear_x, sign)
        _tube(
            frame,
            (rear_x - 0.04, gp[1], gp[2] + 0.004),
            (rear_x + 0.20, gp[1], gp[2] - 0.012),
            0.027,
            material="grip",
            name=f"grip_{sfx}",
        )

    # --- Under-tray ladder: two longitudinal bed rails CARRY the tray (their
    #     tops just touch the tray floor / shell bottom), kept inboard so they
    #     sit under the narrow tapered shell. The tray rests on these two rails;
    #     the cross rungs (below) tie them into one support frame.
    bed_y, bed_z, fork_bed_y = _bed_rail_params(r)
    for sign, sfx in ((1.0, "0"), (-1.0, "1")):
        _tube(
            frame,
            (-L - 0.02, sign * bed_y, bed_z),
            (ax, sign * fork_bed_y, az + 0.006),
            0.016,
            material="frame_steel",
            name=f"bed_rail_{sfx}",
        )

    def _bed_pt(x: float) -> tuple[float, float]:
        return _bed_rail_point(r, x)

    # Cross rungs sit just BELOW the bed rails (following their slope) and span
    # the bed width at their x, overlapping the two rails — they are part of the
    # lower support frame, NOT pressed against the tray. Placed over the flatter
    # rear run of the rails (before they dive to the fork).
    for cx, nm in ((-L * 0.6, "rear"), (-L * 0.05, "mid"), (L * 0.4, "front")):
        ry, rz = _bed_pt(cx)
        _tube(
            frame,
            (cx, -(ry + 0.006), rz - 0.012),
            (cx, ry + 0.006, rz - 0.012),
            0.014,
            material="frame_steel",
            name=f"{nm}_crossbrace",
        )

    # --- Rear posts tying each handle down to the ladder (behind the tray).
    post_x = -L - 0.012
    for sign, sfx in ((1.0, "0"), (-1.0, "1")):
        _tube(
            frame,
            _hpt(post_x, sign),
            (post_x, sign * bed_y, bed_z),
            0.014,
            material="frame_steel",
            name=f"rear_post_{sfx}",
        )

    # --- Rear underframe cross tube (rear-leg FIXED mount datum) + pivot
    #     bracket (gated-aux hinge datum), both tied into the ladder.
    rear_mount_z = z0 - 0.02
    _tube(
        frame,
        (-L - 0.01, -bed_y * 1.05, rear_mount_z),
        (-L - 0.01, bed_y * 1.05, rear_mount_z),
        0.016,
        material="frame_steel",
        name="rear_underframe",
    )
    aux_pivot_x = -L - 0.10
    _tube(
        frame,
        (aux_pivot_x, -bed_y * 0.7, rear_mount_z),
        (aux_pivot_x, bed_y * 0.7, rear_mount_z),
        0.020,
        material="frame_steel",
        name="rear_pivot_bracket",
    )
    _tube(
        frame,
        (aux_pivot_x, 0.0, rear_mount_z),
        (-L - 0.01, 0.0, rear_mount_z),
        0.014,
        material="frame_steel",
        name="rear_pivot_stay",
    )


def _emit_tray_rim(frame_or_tray, r: ResolvedWheelbarrowConfig, *, z0: float) -> None:
    """Rolled rim tubes around the top of the tray (S2 L129-L132)."""
    L = r.tray_len * 0.5
    W = r.tray_width * 0.5
    # Seat the rim tubes right on the shell's top edge (overlap it) so the rim
    # welds to the tray shell rather than floating just inside it.
    rim_z = z0 + r.tray_depth - 0.004
    _tube(
        frame_or_tray,
        (-L, W * 0.96, rim_z),
        (L, W * 0.96, rim_z),
        0.016,
        material="tray_paint",
        name="rim_side_0",
    )
    _tube(
        frame_or_tray,
        (-L, -W * 0.96, rim_z),
        (L, -W * 0.96, rim_z),
        0.016,
        material="tray_paint",
        name="rim_side_1",
    )
    _tube(
        frame_or_tray,
        (L * 0.96, -W * 0.9, rim_z),
        (L * 0.96, W * 0.9, rim_z),
        0.016,
        material="tray_paint",
        name="front_rim",
    )
    _tube(
        frame_or_tray,
        (-L * 0.96, -W * 0.9, rim_z),
        (-L * 0.96, W * 0.9, rim_z),
        0.016,
        material="tray_paint",
        name="rear_rim",
    )


def _tray_z0(r: ResolvedWheelbarrowConfig) -> float:
    """Bottom of the tray in the canonical frame — above the wheel axle so the
    tray clears the big front wheel."""
    return r.axle_z + r.wheel_radius * 0.35 + 0.04


def _emit_fork_interface(frame, r: ResolvedWheelbarrowConfig, *, integrated: bool) -> None:
    """Fork arms + plates + axle bosses built into the frame (integrated mount)
    OR the frame-side mount stub the separate fork bolts to.

    Adapted from S2 L153-L158. The two fork plates straddle the tire on both
    sides of the axle at y = ±fork_gap/2 (just clear of the tire), leaving the
    wheel free to spin between them.
    """
    ax = r.axle_x
    az = r.axle_z
    half_gap = r.fork_gap * 0.5
    plate_inset = half_gap + 0.008  # plate sits just outside the tire face
    # Fork arms sweeping from the tray front down to the axle plates.
    tray_front_x = r.tray_len * 0.5 - 0.04
    tray_front_z = _tray_z0(r) + 0.02
    if integrated:
        _tube(
            frame,
            (tray_front_x, half_gap + 0.04, tray_front_z),
            (ax, plate_inset, az + 0.005),
            0.018,
            material="frame_steel",
            name="fork_arm_0",
        )
        _tube(
            frame,
            (tray_front_x, -(half_gap + 0.04), tray_front_z),
            (ax, -plate_inset, az + 0.005),
            0.018,
            material="frame_steel",
            name="fork_arm_1",
        )
    # Fork plates straddle the tire.
    plate_h = max(0.075, r.wheel_radius * 0.40)
    plate_len = max(0.070, r.wheel_radius * 0.36)
    frame.visual(
        Box((plate_len, 0.014, plate_h)),
        origin=Origin(xyz=(ax, plate_inset, az)),
        material="frame_steel",
        name="fork_plate_0", material_class_id="metal.steel_bare",
    )
    frame.visual(
        Box((plate_len, 0.014, plate_h)),
        origin=Origin(xyz=(ax, -plate_inset, az)),
        material="frame_steel",
        name="fork_plate_1", material_class_id="metal.steel_bare",
    )
    # Axle bosses sit between the plate and the tire face (captured pin).
    boss_y = half_gap + 0.004
    _tube(
        frame,
        (ax, boss_y - 0.020, az),
        (ax, boss_y + 0.010, az),
        0.026,
        material="axle_steel",
        name="axle_boss_0",
    )
    _tube(
        frame,
        (ax, -(boss_y + 0.010), az),
        (ax, -(boss_y - 0.020), az),
        0.026,
        material="axle_steel",
        name="axle_boss_1",
    )
    # Axle spindle spanning plate-to-plate through the wheel center, so the
    # wheel_spin joint origin (ax, 0, az) lies inside frame geometry and the
    # two fork plates are connected (no internal island).
    _tube(
        frame,
        (ax, -(plate_inset + 0.005), az),
        (ax, plate_inset + 0.005, az),
        0.014,
        material="axle_steel",
        name="axle_spindle",
    )


# --------------------------------------------------------------------------- #
# Slot A — chassis_body factories (root). Each emits the `frame` part and the
# shared handles/braces; split variants emit FIXED tray / rear pieces.
# --------------------------------------------------------------------------- #


def _frame_inertial(frame, r: ResolvedWheelbarrowConfig) -> None:
    frame.inertial = Inertial.from_geometry(
        Box((r.overall_length, r.track_width, r.frame_height)),
        mass=16.0,
        origin=Origin(xyz=(0.0, 0.0, r.frame_height * 0.45)),
    )


def _frame_downstream_interface(r: ResolvedWheelbarrowConfig) -> InterfaceSpec:
    """The frame's downstream face — its fork plate front, where the wheel
    mount continues. The next slot (rear_support / wheel_mount) reads
    ``ctx.upstream_interface.part_name`` to find the frame."""
    return InterfaceSpec(
        interface_name="downstream",
        part_name="frame",
        visual_name="fork_plate_0",
        face_side="positive_z",
        anchor_local=(r.axle_x, 0.0, r.axle_z),
        face_extents_uv=(r.track_width, r.frame_height),
        extents_tol=0.60,
        contact_tol=0.0030,
    )


def _build_monolithic_frame(ctx: ModuleBuildContext) -> ModuleBuild:
    """Anchor chassis — single ``frame`` part fusing tray shell + rim + handles
    + braces + integrated fork interface (S2 L121-L158). Rear legs/feet and the
    fork detail are added by the rear_support / wheel_mount slots."""
    model = ctx.model
    r: ResolvedWheelbarrowConfig = ctx.config  # type: ignore[assignment]

    frame = model.part("frame")
    _frame_inertial(frame, r)
    z0 = _tray_z0(r)
    frame.visual(
        mesh_from_geometry(_tapered_tray_mesh(r, z0=z0), "tapered_tray_shell"),
        material="tray_paint",
        name="tray_shell", material_class_id="metal.paint_coated",
    )
    _emit_tray_rim(frame, r, z0=z0)
    _emit_handles_and_braces(frame, r)
    _emit_tray_mount_stays(frame, r, z0=z0)

    return ModuleBuild(
        module_name="monolithic_frame",
        parts_emitted=["frame"],
        internal_articulations=[],
        interfaces={"downstream": _frame_downstream_interface(r)},
    )


def _build_frame_plus_bolted_tray(ctx: ModuleBuildContext) -> ModuleBuild:
    """Alt chassis — frame (handles + braces + a thin support deck) with a
    separate ``tray`` part FIXED-bolted on top (S6 cb2aea L310-L316).

    The tray is a separate part because it is a bolt-on shell with its own
    reference frame in the real article (the dump variants re-use this seam as
    the REVOLUTE pivot). The frame keeps a real support deck visual under the
    tray so the FIXED joint mates to genuine geometry (Rule 2)."""
    model = ctx.model
    r: ResolvedWheelbarrowConfig = ctx.config  # type: ignore[assignment]

    frame = model.part("frame")
    _frame_inertial(frame, r)
    z0 = _tray_z0(r)
    # Support deck the tray bolts onto.
    frame.visual(
        Box((r.tray_len * 0.92, r.tray_width * 0.86, 0.030)),
        origin=Origin(xyz=(0.0, 0.0, z0 - 0.015)),
        material="frame_steel",
        name="tray_deck", material_class_id="metal.steel_bare",
    )
    _emit_handles_and_braces(frame, r)

    tray = model.part("tray")
    _build_tray_part(tray, r, deck_z=z0)
    model.articulation(
        "frame_to_tray",
        ArticulationType.FIXED,
        parent=frame,
        child=tray,
        origin=Origin(xyz=(0.0, 0.0, z0)),
        mating=MatingContract(
            parent_face_geometry="tray_deck",
            parent_face_side="positive_z",
            child_face_geometry="tray_floor",
            child_face_side="negative_z",
            contact_tol=0.0030,
        ),
    )

    return ModuleBuild(
        module_name="frame_plus_bolted_tray",
        parts_emitted=["frame", "tray"],
        internal_articulations=["frame_to_tray"],
        interfaces={"downstream": _frame_downstream_interface(r)},
    )


def _build_upper_body_module_chain(ctx: ModuleBuildContext) -> ModuleBuild:
    """Alt chassis — ``upper_body`` single part fusing tray + handles + legs as
    a bolt-on root module (S7 1c02a48 L34-L199). Named ``frame`` for downstream
    slot consistency. The tray walls are flat box panels (not a loft shell),
    matching S7's construction."""
    model = ctx.model
    r: ResolvedWheelbarrowConfig = ctx.config  # type: ignore[assignment]

    frame = model.part("frame")
    _frame_inertial(frame, r)
    z0 = _tray_z0(r)
    L = r.tray_len * 0.5
    W = r.tray_width * 0.5
    # Flat-panel tray (S7 tray_floor + 4 walls).
    frame.visual(
        Box((r.tray_len, r.tray_width, 0.018)),
        origin=Origin(xyz=(0.0, 0.0, z0 + 0.009)),
        material="tray_paint",
        name="tray_floor", material_class_id="metal.paint_coated",
    )
    frame.visual(
        Box((r.tray_len, 0.020, r.tray_depth)),
        origin=Origin(xyz=(0.0, W - 0.01, z0 + r.tray_depth * 0.5)),
        material="tray_paint",
        name="tray_left_wall", material_class_id="metal.paint_coated",
    )
    frame.visual(
        Box((r.tray_len, 0.020, r.tray_depth)),
        origin=Origin(xyz=(0.0, -(W - 0.01), z0 + r.tray_depth * 0.5)),
        material="tray_paint",
        name="tray_right_wall", material_class_id="metal.paint_coated",
    )
    frame.visual(
        Box((0.020, r.tray_width, r.tray_depth * 0.92)),
        origin=Origin(xyz=(L - 0.01, 0.0, z0 + r.tray_depth * 0.46)),
        material="tray_paint",
        name="tray_front_wall", material_class_id="metal.paint_coated",
    )
    frame.visual(
        Box((0.020, r.tray_width, r.tray_depth * 0.66)),
        origin=Origin(xyz=(-(L - 0.01), 0.0, z0 + r.tray_depth * 0.33)),
        material="tray_paint",
        name="tray_back_wall", material_class_id="metal.paint_coated",
    )
    _emit_handles_and_braces(frame, r)

    return ModuleBuild(
        module_name="upper_body_module_chain",
        parts_emitted=["frame"],
        internal_articulations=[],
        interfaces={"downstream": _frame_downstream_interface(r)},
    )


def _build_frame_tray_handles_legs_split(ctx: ModuleBuildContext) -> ModuleBuild:
    """Alt chassis — maximal split: ``frame`` is the handle frame (handles +
    braces + support deck); ``tray`` is a separate FIXED part on the deck
    (S9 194a0d L514-L527). Rear legs come from the rear_support slot as a
    separate part too."""
    model = ctx.model
    r: ResolvedWheelbarrowConfig = ctx.config  # type: ignore[assignment]

    frame = model.part("frame")
    _frame_inertial(frame, r)
    z0 = _tray_z0(r)
    frame.visual(
        Box((r.tray_len * 0.94, r.tray_width * 0.90, 0.026)),
        origin=Origin(xyz=(0.0, 0.0, z0 - 0.013)),
        material="frame_steel",
        name="tray_deck", material_class_id="metal.steel_bare",
    )
    _emit_handles_and_braces(frame, r)

    tray = model.part("tray")
    _build_tray_part(tray, r, deck_z=z0)
    model.articulation(
        "frame_to_tray",
        ArticulationType.FIXED,
        parent=frame,
        child=tray,
        origin=Origin(xyz=(0.0, 0.0, z0)),
        mating=MatingContract(
            parent_face_geometry="tray_deck",
            parent_face_side="positive_z",
            child_face_geometry="tray_floor",
            child_face_side="negative_z",
            contact_tol=0.0030,
        ),
    )

    return ModuleBuild(
        module_name="frame_tray_handles_legs_split",
        parts_emitted=["frame", "tray"],
        internal_articulations=["frame_to_tray"],
        interfaces={"downstream": _frame_downstream_interface(r)},
    )


def _build_tray_part(tray, r: ResolvedWheelbarrowConfig, *, deck_z: float) -> None:
    """A separate tray part (loft-style tapered shell + floor pad), used by the
    bolted / split chassis variants and re-anchored by the dump pivot.

    The tray's local frame origin is at the deck top: ``tray_floor`` straddles
    z=0 so a FIXED/REVOLUTE joint at the deck mates to it, and the negative_z
    face of tray_floor sits at z=0 (anchor for the chain). Geometry adapted
    from S5 (rec_0002 L298-L364) but parameterized + centered."""
    L = r.tray_len * 0.5
    W = r.tray_width * 0.5
    D = r.tray_depth
    tray.inertial = Inertial.from_geometry(
        Box((r.tray_len, r.tray_width, D)),
        mass=8.0,
        origin=Origin(xyz=(0.0, 0.0, D * 0.4)),
    )
    # Floor sits ON the deck: its -z face is at local z=0 (the mating face),
    # so a FIXED/REVOLUTE joint at the deck top mates flush. Centered at
    # +half-thickness.
    floor_t = 0.024
    tray.visual(
        Box((r.tray_len, r.tray_width, floor_t)),
        origin=Origin(xyz=(0.0, 0.0, floor_t * 0.5)),
        material="tray_paint",
        name="tray_floor", material_class_id="metal.paint_coated",
    )
    tray.visual(
        Box((r.tray_len, 0.018, D)),
        origin=Origin(xyz=(0.0, W - 0.01, D * 0.5)),
        material="tray_paint",
        name="left_side_panel", material_class_id="metal.paint_coated",
    )
    tray.visual(
        Box((r.tray_len, 0.018, D)),
        origin=Origin(xyz=(0.0, -(W - 0.01), D * 0.5)),
        material="tray_paint",
        name="right_side_panel", material_class_id="metal.paint_coated",
    )
    tray.visual(
        Box((0.022, r.tray_width, D * 0.92)),
        origin=Origin(xyz=(L - 0.011, 0.0, D * 0.46)),
        material="tray_paint",
        name="front_panel", material_class_id="metal.paint_coated",
    )
    tray.visual(
        Box((0.022, r.tray_width, D * 0.66)),
        origin=Origin(xyz=(-(L - 0.011), 0.0, D * 0.33)),
        material="tray_paint",
        name="rear_panel", material_class_id="metal.paint_coated",
    )


# --------------------------------------------------------------------------- #
# Slot E — rear_support_detail factories (parallel children of frame).
# These emit a separate FIXED ``rear_legs`` part OR fuse rear legs into frame.
# No upstream interface — they re-export the frame downstream so the chain
# continues to wheel_mount.
# --------------------------------------------------------------------------- #


def _rear_anchor_x(r: ResolvedWheelbarrowConfig) -> float:
    """X of the rear-leg mount on the frame — just behind the tray rear edge so
    the legs clear the (possibly separate) tray footprint."""
    return -r.tray_len * 0.5 - 0.03


def _build_tube_legs_with_pads(ctx: ModuleBuildContext) -> ModuleBuild:
    """Anchor rear support — separate ``rear_legs`` part: bent spline tube legs
    + spreader + orange foot pads + mount risers (S8 194a0d L292-L374),
    FIXED to the frame."""
    model = ctx.model
    r: ResolvedWheelbarrowConfig = ctx.config  # type: ignore[assignment]
    housing_name = (
        ctx.upstream_interface.part_name if ctx.upstream_interface is not None else "frame"
    )
    frame = model.get_part(housing_name)

    rear_legs = model.part("rear_legs")
    rx = _rear_anchor_x(r)
    ly = r.track_width * 0.40
    top_z = _tray_z0(r)
    # Mount point (frame coords) — on the frame's rear_underframe cross tube
    # (at _tray_z0 - 0.02). The part is authored RELATIVE to this so the FIXED
    # joint origin lands inside the rear_legs geometry AND on the frame tube.
    mx, my, mz = rx + 0.02, 0.0, top_z - 0.02
    rear_legs.inertial = Inertial.from_geometry(
        Box((0.30, r.track_width, top_z)),
        mass=2.6,
        origin=Origin(xyz=(-0.06, 0.0, -top_z * 0.55)),
    )
    for sign, side in ((1.0, "left"), (-1.0, "right")):
        y = ly * sign
        rear_legs.visual(
            _spline_tube(
                [
                    (0.0, (y * 0.86) - my, top_z - mz),
                    (-0.05, (y * 0.94) - my, top_z * 0.55 - mz),
                    (-0.08, y - my, 0.025 - mz),
                ],
                radius=0.016,
                name=f"rear_legs_{side}_leg",
            ),
            material="frame_steel",
            name=f"{side}_leg", material_class_id="metal.steel_bare",
        )
        # Mount riser bridges the leg top to the frame deck region (straddles
        # the joint origin at local (0,0,0) so origin-in-geometry holds).
        rear_legs.visual(
            Box((0.07, 0.06, 0.07)),
            origin=Origin(xyz=(0.0, (y * 0.86) - my, top_z - mz)),
            material="frame_steel",
            name=f"{side}_mount_riser", material_class_id="metal.steel_bare",
        )
        # Foot pad + stem (the stem bridges pad to leg bottom).
        rear_legs.visual(
            Box((0.10, 0.05, 0.016)),
            origin=Origin(xyz=(-0.08, y - my, 0.008 - mz)),
            material="foot_accent",
            name=f"{side}_foot_pad", material_class_id="plastic.opaque_glossy_molded",
        )
        rear_legs.visual(
            Box((0.03, 0.03, 0.06)),
            origin=Origin(xyz=(-0.08, y - my, 0.034 - mz)),
            material="frame_steel",
            name=f"{side}_foot_stem", material_class_id="metal.steel_bare",
        )
    # Top cross-mount bar straddling the joint origin (local y=0), tying the
    # two risers together so the part is one connected island at the seam.
    rear_legs.visual(
        Box((0.06, r.track_width * 0.86, 0.05)),
        origin=Origin(xyz=(0.0, 0.0, top_z - mz)),
        material="frame_steel",
        name="mount_bar", material_class_id="metal.steel_bare",
    )
    # Cross spreader tying the two legs near the feet.
    rear_legs.visual(
        Box((0.04, r.track_width * 0.84, 0.028)),
        origin=Origin(xyz=(-0.07, 0.0, 0.06 - mz)),
        material="frame_steel",
        name="rear_spreader", material_class_id="metal.steel_bare",
    )
    model.articulation(
        "frame_to_rear_legs",
        ArticulationType.FIXED,
        parent=frame,
        child=rear_legs,
        origin=Origin(xyz=(mx, my, mz)),
    )

    return ModuleBuild(
        module_name="tube_legs_with_pads",
        parts_emitted=["rear_legs"],
        internal_articulations=["frame_to_rear_legs"],
        interfaces={"downstream": _passthrough_downstream(ctx, r)},
    )


def _build_box_strut_legs(ctx: ModuleBuildContext) -> ModuleBuild:
    """Alt rear support — box-strut legs fused INTO the frame as visuals
    (S7 1c02a48 L126-L185): spline-ish straight tubes + box leg clamps + box
    feet + leg spreader. No separate part (Rule 1: these don't articulate)."""
    model = ctx.model
    r: ResolvedWheelbarrowConfig = ctx.config  # type: ignore[assignment]
    housing_name = (
        ctx.upstream_interface.part_name if ctx.upstream_interface is not None else "frame"
    )
    frame = model.get_part(housing_name)

    rx = _rear_anchor_x(r)
    ly = r.track_width * 0.40
    top_z = _tray_z0(r)
    # The clamp must always bridge the leg top onto the rear_underframe cross
    # tube (x=-L-0.01, z=top_z-0.02, span y=±bed_y*1.05). When track_width is
    # wide relative to tray_width the leg top (0.352*track) can sit outboard of
    # the tube end (0.315*tray_width) — so the clamp plate stretches inboard
    # far enough to always capture the tube (else the whole leg cluster is a
    # disconnected island inside `frame`).
    bed_y, _, _ = _bed_rail_params(r)
    under_half = bed_y * 1.05
    for sign, side in ((1.0, "left"), (-1.0, "right")):
        y = ly * sign
        y_top = abs(y) * 0.88
        clamp_out = y_top + 0.035
        clamp_in = min(under_half - 0.020, y_top - 0.035)
        _tube(
            frame,
            (rx + 0.02, y * 0.88, top_z - 0.01),
            (rx - 0.04, y, 0.022),
            0.017,
            material="frame_steel",
            name=f"{side}_box_leg",
        )
        frame.visual(
            Box((0.05, clamp_out - clamp_in, 0.06)),
            origin=Origin(xyz=(rx + 0.02, sign * (clamp_out + clamp_in) * 0.5, top_z - 0.02)),
            material="frame_steel",
            name=f"{side}_leg_clamp", material_class_id="metal.steel_bare",
        )
        frame.visual(
            Box((0.10, 0.04, 0.024)),
            origin=Origin(xyz=(rx - 0.04, y, 0.02)),
            material="frame_steel",
            name=f"{side}_box_foot", material_class_id="metal.steel_bare",
        )
    frame.visual(
        Box((0.04, r.track_width * 0.86, 0.028)),
        origin=Origin(xyz=(rx - 0.04, 0.0, 0.06)),
        material="frame_steel",
        name="leg_spreader", material_class_id="metal.steel_bare",
    )

    return ModuleBuild(
        module_name="box_strut_legs",
        parts_emitted=[],
        internal_articulations=[],
        interfaces={"downstream": _passthrough_downstream(ctx, r)},
    )


def _build_skid_rest_legs(ctx: ModuleBuildContext) -> ModuleBuild:
    """Alt rear support — short angled rear legs + big box skids + rest pads,
    fused into the frame (S4 rec_0002 L162-L267). The wide skids give a stable
    static rest (used by dump-tray bottom-out)."""
    model = ctx.model
    r: ResolvedWheelbarrowConfig = ctx.config  # type: ignore[assignment]
    housing_name = (
        ctx.upstream_interface.part_name if ctx.upstream_interface is not None else "frame"
    )
    frame = model.get_part(housing_name)

    rx = _rear_anchor_x(r)
    ly = r.track_width * 0.38
    top_z = _tray_z0(r)
    # Clamp plates weld each leg top onto the rear_underframe cross tube
    # (x=rx+0.02, z=top_z-0.02, span y=±bed_y*1.05). With a wide track the leg
    # top (0.38*track) sits outboard of the tube end (0.315*tray_width), so the
    # clamp stretches inboard far enough to always capture the tube — otherwise
    # the whole skid-leg cluster is a disconnected island inside `frame`.
    bed_y, _, _ = _bed_rail_params(r)
    under_half = bed_y * 1.05
    for sign, side in ((1.0, "left"), (-1.0, "right")):
        y = ly * sign
        clamp_out = abs(y) + 0.035
        clamp_in = min(under_half - 0.020, abs(y) - 0.035)
        frame.visual(
            Box((0.06, clamp_out - clamp_in, 0.06)),
            origin=Origin(xyz=(rx + 0.03, sign * (clamp_out + clamp_in) * 0.5, top_z - 0.02)),
            material="frame_steel",
            name=f"{side}_skid_clamp", material_class_id="metal.steel_bare",
        )
        _tube(
            frame,
            (rx + 0.04, y, top_z - 0.02),
            (rx - 0.06, y * 0.92, 0.06),
            0.018,
            material="frame_steel",
            name=f"{side}_rear_leg",
        )
        frame.visual(
            Box((0.16, 0.06, 0.07)),
            origin=Origin(xyz=(rx - 0.06, y * 0.92, 0.035)),
            material="frame_steel",
            name=f"{side}_rear_skid", material_class_id="metal.steel_bare",
        )
        frame.visual(
            Box((0.14, 0.05, 0.024)),
            origin=Origin(xyz=(rx + 0.10, y * 0.86, top_z - 0.04)),
            material="frame_steel",
            name=f"{side}_rest_pad", material_class_id="metal.steel_bare",
        )
        # Post bridging the rest pad to the leg/frame region.
        frame.visual(
            Box((0.05, 0.04, 0.06)),
            origin=Origin(xyz=(rx + 0.06, y * 0.88, top_z - 0.06)),
            material="frame_steel",
            name=f"{side}_pad_post", material_class_id="metal.steel_bare",
        )

    return ModuleBuild(
        module_name="skid_rest_legs",
        parts_emitted=[],
        internal_articulations=[],
        interfaces={"downstream": _passthrough_downstream(ctx, r)},
    )


def _passthrough_downstream(ctx: ModuleBuildContext, r: ResolvedWheelbarrowConfig) -> InterfaceSpec:
    """Re-export the frame's downstream (fork) interface so the chain continues
    from the frame to the wheel_mount after the rear_support slot."""
    if ctx.upstream_interface is not None:
        return ctx.upstream_interface
    return _frame_downstream_interface(r)


# --------------------------------------------------------------------------- #
# Slot B — wheel_mount factories. Each exposes a ``downstream`` interface at
# the axle center (where front_wheel chains via wheel_spin). For separate
# fork/axle, the new parts are FIXED to the frame internally.
# --------------------------------------------------------------------------- #


def _wheel_mount_downstream(part_name: str, r: ResolvedWheelbarrowConfig) -> InterfaceSpec:
    """Downstream interface consumed by front_wheel. The wheel chains onto this
    with consumer_joint_type CONTINUOUS (the sole wheel_spin DOF)."""
    return InterfaceSpec(
        interface_name="downstream",
        part_name=part_name,
        visual_name="axle_boss_0" if part_name == "frame" else "axle_shaft",
        face_side="positive_y",
        anchor_local=(
            r.axle_x if part_name == "frame" else 0.0,
            0.0,
            r.axle_z if part_name == "frame" else 0.0,
        ),
        face_extents_uv=(r.wheel_radius, r.wheel_radius),
        extents_tol=0.60,
        contact_tol=0.0040,
    )


def _build_integrated_fork_axle(ctx: ModuleBuildContext) -> ModuleBuild:
    """Anchor mount — fork arms + plates + axle bosses built directly on the
    frame; wheel parent = frame (S2 L153-L158,L192-L200)."""
    model = ctx.model
    r: ResolvedWheelbarrowConfig = ctx.config  # type: ignore[assignment]
    frame_name = ctx.upstream_interface.part_name if ctx.upstream_interface is not None else "frame"
    frame = model.get_part(frame_name)
    _emit_fork_interface(frame, r, integrated=True)

    return ModuleBuild(
        module_name="integrated_fork_axle",
        parts_emitted=[],
        internal_articulations=[],
        interfaces={"downstream": _wheel_mount_downstream("frame", r)},
    )


def _build_separate_fork_module(ctx: ModuleBuildContext) -> ModuleBuild:
    """Alt mount — a separate ``fork_assembly`` part (crown + arms + plates +
    axle boss) FIXED to the frame; wheel parent = fork (S8 194a0d L376-L445).
    Frame still emits a small mount stub so the FIXED joint mates to geometry."""
    model = ctx.model
    r: ResolvedWheelbarrowConfig = ctx.config  # type: ignore[assignment]
    frame_name = ctx.upstream_interface.part_name if ctx.upstream_interface is not None else "frame"
    frame = model.get_part(frame_name)

    # Frame-side mount stub UNDER the tray front (so the fork bolts to the
    # underframe and stays clear of the bolted tray shell). Its +x face is at
    # the joint origin x.
    stub_x = r.tray_len * 0.5 - 0.02
    stub_z = _tray_z0(r) - 0.05
    frame.visual(
        Box((0.07, r.track_width * 0.4, 0.06)),
        origin=Origin(xyz=(stub_x - 0.035, 0.0, stub_z)),
        material="frame_steel",
        name="fork_mount_stub", material_class_id="metal.steel_bare",
    )

    fork = model.part("fork_assembly")
    fork.inertial = Inertial.from_geometry(
        Box((0.30, r.fork_gap + 0.1, 0.30)),
        mass=4.0,
        origin=Origin(xyz=((r.axle_x - stub_x) * 0.5 + 0.04, 0.0, (r.axle_z - stub_z) * 0.5)),
    )
    # The fork part frame origin coincides with the frame stub +x face at the
    # joint. All visuals are offset by (stub_x, stub_z); the crown sits just
    # forward of the origin so its -x mating face is at x=0 (the joint origin).
    ox, oz = stub_x, stub_z
    half_gap = r.fork_gap * 0.5
    plate_inset = half_gap + 0.008
    # Crown block: -x face at the joint origin (x=0), spanning forward.
    fork.visual(
        Box((0.07, r.track_width * 0.34, 0.07)),
        origin=Origin(xyz=(0.035, 0.0, 0.0)),
        material="frame_steel",
        name="crown_block", material_class_id="metal.steel_bare",
    )
    fork.visual(
        Box((0.05, 0.10, 0.05)),
        origin=Origin(xyz=(r.axle_x - ox, plate_inset, r.axle_z - oz)),
        material="frame_steel",
        name="fork_mount_plate", material_class_id="metal.steel_bare",
    )
    fork.visual(
        Box((0.05, 0.10, 0.05)),
        origin=Origin(xyz=(r.axle_x - ox, -plate_inset, r.axle_z - oz)),
        material="frame_steel",
        name="fork_mount_plate_1", material_class_id="metal.steel_bare",
    )
    _tube(
        fork,
        (0.035, half_gap + 0.03, 0.0),
        (r.axle_x - ox, plate_inset, r.axle_z - oz),
        0.016,
        material="frame_steel",
        name="left_arm",
    )
    _tube(
        fork,
        (0.035, -(half_gap + 0.03), 0.0),
        (r.axle_x - ox, -plate_inset, r.axle_z - oz),
        0.016,
        material="frame_steel",
        name="right_arm",
    )
    plate_h = max(0.075, r.wheel_radius * 0.40)
    plate_len = max(0.070, r.wheel_radius * 0.36)
    fork.visual(
        Box((plate_len, 0.014, plate_h)),
        origin=Origin(xyz=(r.axle_x - ox, plate_inset, r.axle_z - oz)),
        material="frame_steel",
        name="fork_plate_0", material_class_id="metal.steel_bare",
    )
    fork.visual(
        Box((plate_len, 0.014, plate_h)),
        origin=Origin(xyz=(r.axle_x - ox, -plate_inset, r.axle_z - oz)),
        material="frame_steel",
        name="fork_plate_1", material_class_id="metal.steel_bare",
    )
    boss_y = half_gap + 0.004
    _tube(
        fork,
        (r.axle_x - ox, boss_y - 0.020, r.axle_z - oz),
        (r.axle_x - ox, boss_y + 0.010, r.axle_z - oz),
        0.026,
        material="axle_steel",
        name="axle_boss_0",
    )
    _tube(
        fork,
        (r.axle_x - ox, -(boss_y + 0.010), r.axle_z - oz),
        (r.axle_x - ox, -(boss_y - 0.020), r.axle_z - oz),
        0.026,
        material="axle_steel",
        name="axle_boss_1",
    )
    # Axle spindle through the wheel center (y=0) so the wheel_spin origin lies
    # in the fork geometry and the two plates are one island.
    _tube(
        fork,
        (r.axle_x - ox, -(plate_inset + 0.005), r.axle_z - oz),
        (r.axle_x - ox, plate_inset + 0.005, r.axle_z - oz),
        0.014,
        material="axle_steel",
        name="axle_spindle",
    )

    model.articulation(
        "frame_to_fork",
        ArticulationType.FIXED,
        parent=frame,
        child=fork,
        origin=Origin(xyz=(stub_x, 0.0, stub_z)),
        mating=MatingContract(
            parent_face_geometry="fork_mount_stub",
            parent_face_side="positive_x",
            child_face_geometry="crown_block",
            child_face_side="negative_x",
            contact_tol=0.0040,
        ),
    )

    # Downstream: wheel mounts on the fork's axle, at the fork's local axle pos.
    iface = InterfaceSpec(
        interface_name="downstream",
        part_name="fork_assembly",
        visual_name="axle_boss_0",
        face_side="positive_y",
        anchor_local=(r.axle_x - ox, 0.0, r.axle_z - oz),
        face_extents_uv=(r.wheel_radius, r.wheel_radius),
        extents_tol=0.60,
        contact_tol=0.0040,
    )
    return ModuleBuild(
        module_name="separate_fork_module",
        parts_emitted=["fork_assembly"],
        internal_articulations=["frame_to_fork"],
        interfaces={"downstream": iface},
    )


def _build_separate_axle_module(ctx: ModuleBuildContext) -> ModuleBuild:
    """Alt mount — fork (on frame) plus a separate ``axle_module`` (shaft +
    spacers + nuts) FIXED to the frame; wheel parent = axle_module
    (S7 1c02a48 L268-L303,L387-L402). The axle shaft is centered on the part
    origin and lies along part-frame y (lateral)."""
    model = ctx.model
    r: ResolvedWheelbarrowConfig = ctx.config  # type: ignore[assignment]
    frame_name = ctx.upstream_interface.part_name if ctx.upstream_interface is not None else "frame"
    frame = model.get_part(frame_name)
    # Fork still built into frame (plates straddle the tire).
    _emit_fork_interface(frame, r, integrated=True)

    axle = model.part("axle_module")
    half_gap = r.fork_gap * 0.5
    axle.inertial = Inertial.from_geometry(
        Cylinder(radius=0.02, length=r.fork_gap + 0.06),
        mass=0.9,
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
    )
    # Axle shaft along y, centered on origin (origin lies in geometry).
    axle.visual(
        Cylinder(radius=0.0085, length=r.fork_gap + 0.05),
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="zinc",
        name="axle_shaft", material_class_id="metal.steel_galvanized",
    )
    for sign, side in ((1.0, "left"), (-1.0, "right")):
        axle.visual(
            Cylinder(radius=r.hub_radius * 0.40, length=0.016),
            origin=Origin(xyz=(0.0, sign * (half_gap - 0.012), 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material="zinc",
            name=f"{side}_spacer", material_class_id="metal.steel_galvanized",
        )
        axle.visual(
            Box((0.030, 0.016, 0.030)),
            origin=Origin(xyz=(0.0, sign * (half_gap + 0.012), 0.0)),
            material="zinc",
            name=f"{side}_nut", material_class_id="metal.steel_galvanized",
        )
    model.articulation(
        "frame_to_axle",
        ArticulationType.FIXED,
        parent=frame,
        child=axle,
        origin=Origin(xyz=(r.axle_x, 0.0, r.axle_z)),
    )

    iface = InterfaceSpec(
        interface_name="downstream",
        part_name="axle_module",
        visual_name="axle_shaft",
        face_side="positive_y",
        anchor_local=(0.0, 0.0, 0.0),
        face_extents_uv=(r.wheel_radius, r.wheel_radius),
        extents_tol=0.60,
        contact_tol=0.0040,
    )
    return ModuleBuild(
        module_name="separate_axle_module",
        parts_emitted=["axle_module"],
        internal_articulations=["frame_to_axle"],
        interfaces={"downstream": iface},
    )


def _build_axle_root_pivot(ctx: ModuleBuildContext) -> ModuleBuild:
    """Alt mount — a distinct ``axle`` part bridges the frame and the wheel
    (axle topology from S13 e94d07 L334-L342), but kept single-DOF: the axle is
    FIXED to the frame and only the wheel spins on it (CONTINUOUS, chained by
    the front_wheel slot). The body / tray does not pivot.

    Because the assembler chains parent=frame-side downstream → child=this
    module's upstream, we DON'T expose an upstream (the frame is already root).
    Instead we emit the axle part, FIX it to the frame via the fork bosses
    (frame still holds the fork), and the wheel chains onto the axle's
    downstream."""
    model = ctx.model
    r: ResolvedWheelbarrowConfig = ctx.config  # type: ignore[assignment]
    frame_name = ctx.upstream_interface.part_name if ctx.upstream_interface is not None else "frame"
    frame = model.get_part(frame_name)
    _emit_fork_interface(frame, r, integrated=True)

    axle = model.part("axle")
    half_gap = r.fork_gap * 0.5
    axle.inertial = Inertial.from_geometry(
        Cylinder(radius=0.02, length=r.fork_gap + 0.04),
        mass=1.2,
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
    )
    axle.visual(
        Cylinder(radius=0.012, length=r.fork_gap + 0.04),
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="zinc",
        name="axle_shaft", material_class_id="metal.steel_galvanized",
    )
    for sign, side in ((1.0, "left"), (-1.0, "right")):
        axle.visual(
            Cylinder(radius=r.hub_radius * 0.55, length=0.018),
            origin=Origin(xyz=(0.0, sign * (half_gap - 0.014), 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material="zinc",
            name=f"{side}_axle_collar", material_class_id="metal.steel_galvanized",
        )
    # Axle FIXED to the frame: single-DOF (only the wheel spins; the body /
    # tray never pivots). Captured pin (axle through fork bosses) —
    # grandfathered (no mating).
    model.articulation(
        "frame_to_axle",
        ArticulationType.FIXED,
        parent=frame,
        child=axle,
        origin=Origin(xyz=(r.axle_x, 0.0, r.axle_z)),
    )

    iface = InterfaceSpec(
        interface_name="downstream",
        part_name="axle",
        visual_name="axle_shaft",
        face_side="positive_y",
        anchor_local=(0.0, 0.0, 0.0),
        face_extents_uv=(r.wheel_radius, r.wheel_radius),
        extents_tol=0.60,
        contact_tol=0.0040,
    )
    return ModuleBuild(
        module_name="axle_root_pivot",
        parts_emitted=["axle"],
        internal_articulations=["frame_to_axle"],
        interfaces={"downstream": iface},
    )


# --------------------------------------------------------------------------- #
# Slot C — front_wheel factory (chains via wheel_spin CONTINUOUS).
# --------------------------------------------------------------------------- #


def _build_front_wheel(ctx: ModuleBuildContext) -> ModuleBuild:
    """The single front wheel. Emits the sole always-on ``wheel_spin`` joint
    itself (parallel-children style) rather than via the assembler chain,
    because the wheel-on-axle coupling is captured/co-axial — its
    MatingContract is intentionally OMITTED (grandfathered), with the
    hub-in-fork / axle-through-hub overlaps declared in run_wheelbarrow_tests.

    The wheel hub is centered on (0,0,0); the spin axis lies along part-frame y
    in the wheel's own geometry, but the joint axis is ``r.wheel_spin_axis``
    (the lateral side axis derived from body_axis). The joint origin is the
    parent's axle center, read from ``ctx.upstream_interface`` — so the wheel's
    (0,0,0) coincides with the joint origin (origin-in-geometry holds).

    No ``upstream`` interface is exposed, which suppresses the assembler's
    auto-chain joint (we own the wheel_spin joint)."""
    model = ctx.model
    r: ResolvedWheelbarrowConfig = ctx.config  # type: ignore[assignment]

    iface = ctx.upstream_interface
    if iface is None:
        parent_name = "frame"
        origin_xyz = (r.axle_x, 0.0, r.axle_z)
    else:
        parent_name = iface.part_name
        ax = iface.anchor_local
        # The parent module placed the wheel-attach point at its anchor_local
        # in its own part frame; for separate axle/fork parts that origin is at
        # (0,0,0) and the joint between the parent and its grandparent sits at
        # the axle center, so the wheel joint origin matches the parent anchor.
        origin_xyz = (ax[0], ax[1], ax[2])
    parent = model.get_part(parent_name)

    wheel = model.part("front_wheel")
    builder = _WHEEL_BUILDERS[r.front_wheel_module]
    builder(wheel, r)

    model.articulation(
        "wheel_spin",
        ArticulationType.CONTINUOUS,
        parent=parent,
        child=wheel,
        origin=Origin(xyz=origin_xyz),
        axis=r.wheel_spin_axis,
        motion_limits=MotionLimits(effort=20.0, velocity=20.0),
    )
    return ModuleBuild(
        module_name=r.front_wheel_module,
        parts_emitted=["front_wheel"],
        internal_articulations=["wheel_spin"],
        interfaces={"downstream": _passthrough_downstream(ctx, r)},
    )


# --------------------------------------------------------------------------- #
# Slot D — aux_articulation factories (gated second DOF / multiplicity).
# Parallel children of the frame; ``none`` emits nothing (single-DOF default).
# --------------------------------------------------------------------------- #


def _build_aux_none(ctx: ModuleBuildContext) -> ModuleBuild:
    """Default mature domain — no second DOF. Only wheel_spin moves."""
    r: ResolvedWheelbarrowConfig = ctx.config  # type: ignore[assignment]
    return ModuleBuild(
        module_name="none_single_dof",
        parts_emitted=[],
        internal_articulations=[],
        interfaces={"downstream": _passthrough_downstream(ctx, r)},
    )


def _build_folding_rear_stand_revolute(ctx: ModuleBuildContext) -> ModuleBuild:
    """Gated — a separate ``rear_stand`` part folds up via REVOLUTE about the
    lateral side axis (S10 efeca1 L383-L437)."""
    model = ctx.model
    r: ResolvedWheelbarrowConfig = ctx.config  # type: ignore[assignment]
    frame = model.get_part("frame")

    # Pivot well behind the tray; the stand legs splay BACKWARD (−x) so their
    # foot pads land clear of the fixed rear legs/feet (which sit forward of
    # this pivot). Narrower track than the rear legs so the stand tucks inside.
    rx = -r.tray_len * 0.5 - 0.10
    z_pivot = _tray_z0(r) - 0.02
    ly = r.track_width * 0.26
    stand_len = max(0.30, r.frame_height * 0.55)
    leg_back = 0.16  # backward (−x) reach of the stand legs

    rear_stand = model.part("rear_stand")
    rear_stand.inertial = Inertial.from_geometry(
        Box((leg_back + 0.10, r.track_width * 0.6, stand_len)),
        mass=1.8,
        origin=Origin(xyz=(-leg_back * 0.5, 0.0, -stand_len * 0.5)),
    )
    # Hinge sleeve along the side axis, centered on the part origin (joint
    # origin lies in geometry).
    rear_stand.visual(
        Cylinder(radius=0.022, length=r.track_width * 0.62),
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="zinc",
        name="hinge_sleeve", material_class_id="metal.steel_galvanized",
    )
    for sign, side in ((1.0, "left"), (-1.0, "right")):
        y = ly * sign
        rear_stand.visual(
            Box((0.05, 0.05, 0.06)),
            origin=Origin(xyz=(0.0, y, -0.03)),
            material="frame_steel",
            name=f"{side}_hinge_weld", material_class_id="metal.steel_bare",
        )
        # Stand leg as an angled tube from the hinge back-and-down to the pad.
        _tube(
            rear_stand,
            (0.0, y, -0.02),
            (-leg_back, y, -stand_len),
            0.018,
            material="frame_steel",
            name=f"{side}_stand_leg",
        )
        rear_stand.visual(
            Box((0.10, 0.07, 0.024)),
            origin=Origin(xyz=(-leg_back, y, -stand_len + 0.012)),
            material="rubber",
            name=f"{side}_foot_pad", material_class_id="rubber.smooth_plain",
        )
    # Cross spreader tying the two stand legs (one connected island).
    rear_stand.visual(
        Box((0.04, ly * 2.0, 0.026)),
        origin=Origin(xyz=(-leg_back * 0.5, 0.0, -stand_len * 0.5)),
        material="frame_steel",
        name="stand_spreader", material_class_id="metal.steel_bare",
    )
    model.articulation(
        "frame_to_rear_stand",
        ArticulationType.REVOLUTE,
        parent=frame,
        child=rear_stand,
        origin=Origin(xyz=(rx, 0.0, z_pivot)),
        axis=r.wheel_spin_axis,
        motion_limits=MotionLimits(effort=80.0, velocity=1.5, lower=0.0, upper=r.stand_fold_limit),
    )
    return ModuleBuild(
        module_name="folding_rear_stand_revolute",
        parts_emitted=["rear_stand"],
        internal_articulations=["frame_to_rear_stand"],
        interfaces={"downstream": _passthrough_downstream(ctx, r)},
    )


def _build_level_foot_prismatic(ctx: ModuleBuildContext) -> ModuleBuild:
    """Gated multiplicity — a pair of ``side_tube`` parts FIXED to the frame,
    each carrying a ``level_foot`` part that slides on a PRISMATIC z axis
    (S11 2960ce L298-L395). Left/right side tubes are separate parts, each a
    single connected piece."""
    model = ctx.model
    r: ResolvedWheelbarrowConfig = ctx.config  # type: ignore[assignment]
    frame = model.get_part("frame")

    # Mount the side tubes on the under-tray ladder's front cross rung (which
    # spans the bed rails just below the tray floor at x=tray_len*0.275), well
    # forward of the rear legs so the two grounding mechanisms don't collide.
    foot_y = r.tray_width * 0.30 * 0.8
    mount_x = r.tray_len * 0.275
    # 8 mm below the tray datum: close enough (< 15 mm) to the monolithic loft
    # shell's bottom face at z0+0.005 for the FIXED-joint origin check, while
    # still inside the tray_deck / under the tray_floor of the other chassis.
    top_z = _tray_z0(r) - 0.008
    travel = r.foot_travel
    for index, sign in enumerate((1.0, -1.0)):
        y = foot_y * sign
        # Mount point (frame coords) — side_tube authored RELATIVE to it.
        mx, my, mz = mount_x, y, top_z
        tube = model.part(f"side_tube_{index}")
        tube.inertial = Inertial.from_geometry(
            Box((0.10, 0.08, top_z)),
            mass=0.8,
            origin=Origin(xyz=(-0.04, 0.0, -top_z * 0.5)),
        )
        # Mount block straddling the joint origin (local 0,0,0) so the FIXED
        # joint origin lies in side_tube geometry AND it contacts the frame.
        # Slightly biased downward so its top ends at z0+0.015: it embeds into
        # the monolithic shell's bottom slab (contact) without poking through
        # the flat-panel tray floors into the bowl.
        tube.visual(
            Box((0.07, 0.06, 0.06)),
            origin=Origin(xyz=(0.0, 0.0, -0.007)),
            material="frame_steel",
            name="mount_block", material_class_id="metal.steel_bare",
        )
        # Foot sleeve global position — straight down from the mount, ending
        # near the ground. The stem rides inside it.
        sleeve_gx, sleeve_gy, sleeve_gz = mx, y, 0.10
        # Bent tube from the frame mount down to the foot sleeve (relative).
        tube.visual(
            _spline_tube(
                [
                    (0.0, 0.0, 0.0),
                    (sleeve_gx - mx, sleeve_gy - my, top_z * 0.5 - mz),
                    (sleeve_gx - mx, sleeve_gy - my, sleeve_gz - mz),
                ],
                radius=0.017,
                name=f"side_tube_{index}_sweep",
            ),
            material="frame_steel",
            name="bent_tube", material_class_id="metal.steel_bare",
        )
        # Foot sleeve at the bottom (the prismatic stem rides inside it).
        tube.visual(
            Cylinder(radius=0.028, length=0.12),
            origin=Origin(xyz=(sleeve_gx - mx, sleeve_gy - my, sleeve_gz - mz)),
            material="foot_accent",
            name="foot_sleeve", material_class_id="plastic.opaque_glossy_molded",
        )
        model.articulation(
            f"frame_to_side_tube_{index}",
            ArticulationType.FIXED,
            parent=frame,
            child=tube,
            origin=Origin(xyz=(mx, my, mz)),
        )

        # level_foot: PRISMATIC child of the side_tube. Joint origin is the
        # foot sleeve center in the side_tube's LOCAL frame.
        sleeve_local = (sleeve_gx - mx, sleeve_gy - my, sleeve_gz - mz)
        foot = model.part(f"level_foot_{index}")
        foot.inertial = Inertial.from_geometry(
            Cylinder(radius=0.05, length=0.12),
            mass=0.4,
            origin=Origin(xyz=(0.0, 0.0, -0.02)),
        )
        # Stem centered on origin (the joint origin lies in geometry).
        foot.visual(
            Cylinder(radius=0.010, length=0.13),
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
            material="foot_accent",
            name="threaded_stem", material_class_id="plastic.opaque_glossy_molded",
        )
        foot.visual(
            Cylinder(radius=0.052, length=0.014),
            origin=Origin(xyz=(0.0, 0.0, -0.058)),
            material="rubber",
            name="level_pad", material_class_id="rubber.smooth_plain",
        )
        model.articulation(
            f"side_tube_to_level_foot_{index}",
            ArticulationType.PRISMATIC,
            parent=tube,
            child=foot,
            origin=Origin(xyz=sleeve_local),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(
                effort=45.0, velocity=0.05, lower=-travel * 0.4, upper=travel
            ),
        )

    return ModuleBuild(
        module_name="level_foot_prismatic",
        parts_emitted=["side_tube_0", "side_tube_1", "level_foot_0", "level_foot_1"],
        internal_articulations=[
            "frame_to_side_tube_0",
            "frame_to_side_tube_1",
            "side_tube_to_level_foot_0",
            "side_tube_to_level_foot_1",
        ],
        interfaces={"downstream": _passthrough_downstream(ctx, r)},
    )


# --------------------------------------------------------------------------- #
# Slot graph + entry points
# --------------------------------------------------------------------------- #


CHASSIS_FACTORIES = {
    "monolithic_frame": _build_monolithic_frame,
    "frame_plus_bolted_tray": _build_frame_plus_bolted_tray,
    "upper_body_module_chain": _build_upper_body_module_chain,
    "frame_tray_handles_legs_split": _build_frame_tray_handles_legs_split,
}
REAR_SUPPORT_FACTORIES = {
    "tube_legs_with_pads": _build_tube_legs_with_pads,
    "box_strut_legs": _build_box_strut_legs,
    "skid_rest_legs": _build_skid_rest_legs,
}
WHEEL_MOUNT_FACTORIES = {
    "integrated_fork_axle": _build_integrated_fork_axle,
    "separate_fork_module": _build_separate_fork_module,
    "separate_axle_module": _build_separate_axle_module,
    "axle_root_pivot": _build_axle_root_pivot,
}
FRONT_WHEEL_FACTORIES = {
    "single_front_wheel": _build_front_wheel,
}
AUX_FACTORIES = {
    "none_single_dof": _build_aux_none,
    "folding_rear_stand_revolute": _build_folding_rear_stand_revolute,
    "level_foot_prismatic": _build_level_foot_prismatic,
}


def _slots_for_config(r: ResolvedWheelbarrowConfig) -> list[SlotSpec]:
    """Build the slot graph pinned to the chosen module per slot.

    Slot order matters:
      1. chassis_body (root) — emits frame (+ tray for split variants).
      2. rear_support_detail — parallel children of frame; re-exports the
         frame's fork interface downstream.
      3. wheel_mount — emits fork/axle; exposes the axle-center downstream.
      4. front_wheel — chains onto wheel_mount via the CONTINUOUS wheel_spin
         joint (front_wheel's upstream interface).
      5. aux_articulation — gated second DOF / multiplicity, parented to frame.
    """
    return [
        SlotSpec(
            slot_name="chassis_body",
            candidates={r.chassis_body_module: CHASSIS_FACTORIES[r.chassis_body_module]},
            anchor_choice=r.chassis_body_module,
        ),
        SlotSpec(
            slot_name="rear_support_detail",
            candidates={r.rear_support_module: REAR_SUPPORT_FACTORIES[r.rear_support_module]},
            anchor_choice=r.rear_support_module,
        ),
        SlotSpec(
            slot_name="wheel_mount",
            candidates={r.wheel_mount_module: WHEEL_MOUNT_FACTORIES[r.wheel_mount_module]},
            anchor_choice=r.wheel_mount_module,
        ),
        SlotSpec(
            slot_name="front_wheel",
            candidates={"single_front_wheel": _build_front_wheel},
            anchor_choice="single_front_wheel",
        ),
        SlotSpec(
            slot_name="aux_articulation",
            candidates={r.aux_articulation_module: AUX_FACTORIES[r.aux_articulation_module]},
            anchor_choice=r.aux_articulation_module,
        ),
    ]


def build_wheelbarrow(
    config: WheelbarrowConfig,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    """Compose a wheelbarrow model by running each slot's module factory.

    The assembler walks chassis_body → rear_support_detail → wheel_mount →
    front_wheel → aux_articulation. Only the wheel_mount → front_wheel pair
    is an auto-chained joint (wheel_spin CONTINUOUS); the other slots emit
    their joints internally with parent=frame.

    The geometry is authored in the x-forward canonical frame, with the wheel
    disk in the x-z plane and its axle on the side-to-side y axis.
    """
    r = resolve_config(config)
    model = ArticulatedObject(name="wheelbarrow", assets=assets)
    for material_name, rgba in r.palette.items():
        model.material(material_name, rgba=rgba)

    rng = random.Random(0)
    assemble(
        model,
        slots=_slots_for_config(r),
        rng=rng,
        palette=r.palette,
        config=r,
        seed=0,
        selection_mode="anchor_choices",
    )
    _apply_body_axis(model, r)
    return model


def _apply_body_axis(model: ArticulatedObject, r: ResolvedWheelbarrowConfig) -> None:
    """Compatibility hook for ``body_axis``.

    Keep the sampled template in the canonical x-forward wheelbarrow frame.
    The front wheel is a vertical disk in the body long-axis plane and rotates
    around the visible side-to-side axle.
    """
    return


def build_seeded_wheelbarrow(seed: int) -> ArticulatedObject:
    return build_wheelbarrow(config_from_seed(seed))


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    """Return the (slot, module) picks for inspection — used by the
    module_topology_diversity gate to count unique topologies. ``body_axis``
    is included as a slot so it contributes to topology diversity."""
    cfg = config_from_seed(seed)
    r = resolve_config(cfg)
    return [
        ("chassis_body", r.chassis_body_module),
        ("rear_support_detail", r.rear_support_module),
        ("wheel_mount", r.wheel_mount_module),
        ("front_wheel", r.front_wheel_module),
        ("aux_articulation", r.aux_articulation_module),
        ("body_axis", r.body_axis),
    ]


# --------------------------------------------------------------------------- #
# Author-layer QC — wheelbarrow-specific sanity + captured-pivot allowances.
# --------------------------------------------------------------------------- #


def _declare_captured_overlaps(ctx: TestContext, model: ArticulatedObject) -> None:
    """Declare expected inter-part overlaps for captured/co-axial geometry.

    The wheel hub sits between the fork plates / inside the axle bosses; the
    axle shaft passes through the wheel hub; the rear_legs riser welds into the
    frame handle region; the level-foot stem rides inside its side_tube sleeve.
    These are all intentional captured-geometry overlaps that the MatingContract
    abstraction cannot model, so we grandfather them here."""
    parts = {p.name for p in model.parts}

    def _overlap(a: str, b: str, *, reason: str) -> None:
        if a in parts and b in parts:
            ctx.allow_overlap(model.get_part(a), model.get_part(b), reason=reason)

    # Wheel ↔ whatever holds it (frame integrated fork, fork_assembly, axle*).
    for holder in ("frame", "fork_assembly", "axle_module", "axle"):
        _overlap(
            holder,
            "front_wheel",
            reason="captured wheel hub — fork plates / axle bosses straddle the tire and the axle passes through the hub",
        )
    # Separate fork bolts onto the frame stub (captured weld).
    _overlap("frame", "fork_assembly", reason="fork assembly welds onto the frame mount stub")
    _overlap("frame", "axle_module", reason="axle module clamps into the frame fork plates")
    _overlap("frame", "axle", reason="axle pivot pin captured in the frame fork bosses")
    # Rear legs FIXED to frame (riser weld into handle region).
    _overlap("frame", "rear_legs", reason="rear leg risers weld into the frame handle/deck region")
    # On split chassis the rear-leg mount bar tucks under the separate tray.
    _overlap("rear_legs", "tray", reason="rear leg mount bar welds under the separate tray floor")
    # Tray bolts/pivots onto the frame deck.
    _overlap("frame", "tray", reason="tray bolts/pivots onto the frame support deck")
    # Aux: rear stand hinge onto frame.
    _overlap("frame", "rear_stand", reason="rear stand hinge sleeve captured on the frame pivot")
    # Level feet multiplicity.
    for i in (0, 1):
        _overlap("frame", f"side_tube_{i}", reason="leveling side tube welds to the frame")
        _overlap(
            f"side_tube_{i}",
            f"level_foot_{i}",
            reason="leveling foot stem rides inside the side-tube sleeve",
        )
        # The side tube passes under the tray and welds to the underframe.
        _overlap(
            f"side_tube_{i}",
            "tray",
            reason="leveling side tube passes under the bolted tray floor (welded to underframe)",
        )


def _expect_single_front_wheel(ctx: TestContext, model: ArticulatedObject) -> None:
    """Exactly one spinning wheel part named front_wheel (not a cart)."""
    wheel_parts = [p.name for p in model.parts if "wheel" in p.name.lower()]
    ctx.check(
        "exactly_one_front_wheel",
        wheel_parts == ["front_wheel"],
        details=f"wheel parts: {wheel_parts}",
    )


def _find_wheel_spin(model: ArticulatedObject):
    """Return the joint whose child is the front_wheel (the wheel_spin DOF)."""
    for j in getattr(model, "articulations", []):
        child = getattr(j, "child", None)
        child_name = getattr(child, "name", None) or str(child)
        if "front_wheel" in str(child_name) or getattr(j, "name", "") == "wheel_spin":
            return j
    return None


def _expect_wheel_spin_continuous_lateral(
    ctx: TestContext, model: ArticulatedObject, r: ResolvedWheelbarrowConfig
) -> None:
    """wheel_spin must be CONTINUOUS, axis = visible axle cylinder, no limits."""
    spin = _find_wheel_spin(model)
    if spin is None:
        ctx.fail("wheel_spin_present", "no joint chaining to front_wheel found")
        return
    ctx.check(
        "wheel_spin_is_continuous",
        spin.articulation_type == ArticulationType.CONTINUOUS,
        details=f"type={spin.articulation_type}",
    )
    ctx.check(
        "wheel_spin_axis_is_lateral",
        tuple(spin.axis) == r.wheel_spin_axis,
        details=f"axis={spin.axis}, expected {r.wheel_spin_axis}",
    )
    lim = spin.motion_limits
    ctx.check(
        "wheel_spin_unbounded",
        lim is None or (lim.lower is None and lim.upper is None),
        details=f"limits={lim}",
    )


def _expect_revolute_axes_match_visible_cylinders(
    ctx: TestContext, model: ArticulatedObject, r: ResolvedWheelbarrowConfig
) -> None:
    """Wheel and folding-stand revolutes must follow their modeled cylinder axes."""
    expected_axis = r.wheel_spin_axis
    joints_by_name = {joint.name: joint for joint in getattr(model, "articulations", [])}
    for joint_name in ("wheel_spin", "frame_to_rear_stand"):
        joint = joints_by_name.get(joint_name)
        if joint is None:
            continue
        ctx.check(
            f"{joint_name}_axis_matches_visible_cylinder",
            tuple(joint.axis) == expected_axis,
            details=f"axis={joint.axis}, expected {expected_axis}",
        )


def _expect_wheel_spins_in_place(ctx: TestContext, model: ArticulatedObject) -> None:
    """Spinning the wheel keeps its axle position fixed (rolls, not orbits)."""
    spin = _find_wheel_spin(model)
    if spin is None:
        return
    wheel = model.get_part("front_wheel")
    rest = ctx.part_world_position(wheel)
    with ctx.pose({spin: math.pi / 2.0}):
        turned = ctx.part_world_position(wheel)
    if rest is None or turned is None:
        return
    ctx.check(
        "wheel_spins_in_place",
        all(abs(rest[i] - turned[i]) < 1e-6 for i in range(3)),
        details=f"rest={rest}, turned={turned}",
    )


def _expect_big_wheel(
    ctx: TestContext, model: ArticulatedObject, r: ResolvedWheelbarrowConfig
) -> None:
    """Wheel is large relative to the frame (wheel_radius > 0.55*frame_height)."""
    wheel = model.get_part("front_wheel")
    frame = model.get_part("frame")
    w_aabb = ctx.part_world_aabb(wheel)
    f_aabb = ctx.part_world_aabb(frame)
    if w_aabb is None or f_aabb is None:
        return
    tire_d = max(w_aabb[1][0] - w_aabb[0][0], w_aabb[1][2] - w_aabb[0][2])
    frame_h = f_aabb[1][2] - f_aabb[0][2]
    ctx.check(
        "wheel_is_big_relative_to_frame",
        tire_d > 0.30 and tire_d > 0.55 * frame_h,
        details=f"tire_d={tire_d:.3f}, frame_h={frame_h:.3f}",
    )


def run_wheelbarrow_tests(
    model: ArticulatedObject,
    config: WheelbarrowConfig,
) -> TestReport:
    """Author-layer QC for the modular wheelbarrow template.

    The compiler-owned baseline runs the hard QC stack (model validity,
    isolated parts, current-pose overlap, articulation-origin distance, joint
    mating gap, and a WARN-level internal-island check). This function:

      * declares allow_overlap for all captured/co-axial geometry (the
        captured wheel hub, axle-through-hub, welded rear legs, hinge pins,
        level-foot stem-in-sleeve), and
      * adds wheelbarrow-specific identity/axis checks (single front wheel,
        wheel_spin CONTINUOUS + lateral + unbounded, spins-in-place, big wheel).
    """
    r = resolve_config(config)
    ctx = TestContext(model)

    _declare_captured_overlaps(ctx, model)

    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.020)
    ctx.fail_if_joint_mating_has_gap()

    _expect_single_front_wheel(ctx, model)
    _expect_wheel_spin_continuous_lateral(ctx, model, r)
    _expect_revolute_axes_match_visible_cylinders(ctx, model, r)
    _expect_wheel_spins_in_place(ctx, model)
    _expect_big_wheel(ctx, model, r)

    return ctx.report()


__all__ = [
    "AuxArticulationModule",
    "BodyAxis",
    "ChassisBodyModule",
    "FrontWheelModule",
    "RearSupportModule",
    "ResolvedWheelbarrowConfig",
    "WheelMountModule",
    "WheelbarrowConfig",
    "WheelbarrowPalette",
    "build_seeded_wheelbarrow",
    "build_wheelbarrow",
    "config_from_seed",
    "resolve_config",
    "run_wheelbarrow_tests",
    "slot_choices_for_seed",
]
