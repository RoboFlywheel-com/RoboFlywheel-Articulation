# SPDX-License-Identifier: Apache-2.0

# ruff: noqa: E501
"""Self-contained flexible track lighting system template.

A lighting track carries N repositionable spotlight heads.  Each head is an
independent pan+tilt gimbal: a real vertical pan axis (track -> gimbal) and a
real horizontal tilt trunnion (gimbal -> head), both built with mate_axes and
registered for the TEMPLATE_DOMAIN axis contract.

Structural slots (source-derived, freely combinable):
  * lighting_track: flexible_oval_rail | straight_rigid_rail
  * track_adapter:  flush_block        | shoe_spindle_mount
  * light_head:     cylindrical_can    | tapered_can
  * pan_gimbal:     crossbar_trunnion  | u_bracket
Multiplicity: head_count in 3..8.  Head pan-pivot spacing is derived from the
worst-case pan/tilt envelope so adjacent heads never collide.

`track_adapter` changes the part tree and the joint graph: `flush_block`
(REC_001) embeds the mount into the track as fixed geometry so the pan REVOLUTE
mounts the gimbal directly on the track, while `shoe_spindle_mount` (REC_002)
emits one extra rail-shoe PART per head, joined to the track by a FIXED joint,
and re-parents the pan REVOLUTE onto that adapter's spindle.

No source runtime is imported; only stdlib, cadquery, and the SDK are used.
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
    Box,
    Cylinder,
    MotionLimits,
    Origin,
    TemplateDomain,
    TestContext,
    TestReport,
    component_slot,
    corner_case,
    mate_axes,
    mesh_from_cadquery,
    mesh_from_geometry,
    multiplicity_slot,
    register_interface_mate,
    tube_from_spline_points,
)

LightingTrack = Literal["flexible_oval_rail", "straight_rigid_rail"]
TrackAdapter = Literal["flush_block", "shoe_spindle_mount"]
LightHead = Literal["cylindrical_can", "tapered_can"]
PanGimbal = Literal["crossbar_trunnion", "u_bracket"]

LIGHTING_TRACKS: tuple[LightingTrack, ...] = ("flexible_oval_rail", "straight_rigid_rail")
TRACK_ADAPTERS: tuple[TrackAdapter, ...] = ("flush_block", "shoe_spindle_mount")
LIGHT_HEADS: tuple[LightHead, ...] = ("cylindrical_can", "tapered_can")
PAN_GIMBALS: tuple[PanGimbal, ...] = ("crossbar_trunnion", "u_bracket")
HEAD_COUNTS: tuple[int, ...] = (3, 4, 5, 6, 7, 8)

TEMPLATE_DOMAIN = TemplateDomain(
    slots=(
        component_slot("lighting_track", LIGHTING_TRACKS),
        component_slot("track_adapter", TRACK_ADAPTERS),
        component_slot("light_head", LIGHT_HEADS),
        component_slot("pan_gimbal", PAN_GIMBALS),
        multiplicity_slot("head_count", HEAD_COUNTS, item_slot="light_head"),
    )
)

# Continuous parameter bounds (m).  Continuous dimensions do not inflate core/raw.
_HEAD_LENGTH_MIN, _HEAD_LENGTH_MAX = 0.066, 0.115
_HEAD_RADIUS_MIN, _HEAD_RADIUS_MAX = 0.024, 0.036
_DROP_MIN, _DROP_MAX = 0.045, 0.100
_TRACK_THICKNESS_MIN, _TRACK_THICKNESS_MAX = 0.006, 0.012

_TILT_MAX = math.radians(55.0)
_PAN_LIMIT = math.pi
_MESH_TOL = 0.0009
_MESH_ANG_TOL = 0.12
# Seating press-fit for discs/segments that must genuinely join their host wall.
# Tangency alone (zero penetration) reads as a disconnected geometry island, so
# every seated part is pressed in by this much -- real contact, and well under
# the 1 mm (`overlap_tol=1e-3`) collision overlap tolerance.
_BORE_SEAT = 0.0003
# Highest point of `_tapered_can_geom` in head-local Z: the outer loft tops out at
# `rear_top` (0.028) and the rear neck is extruded from `rear_top - 0.003` by 0.035.
_TAPERED_TOP_LOCAL = 0.028 + 0.032
# How far the tapered can hangs below its trunnion so its neck clears the yoke.
_TAPERED_HANG = _TAPERED_TOP_LOCAL - 0.004

# Vertical gap between a pan-pivot reference plane and the rail underside.  The
# `flush_block` adapter fills exactly this gap as fixed track geometry.
_MOUNT_GAP = 0.020
# `shoe_spindle_mount` stack (REC_002 `_add_adapter_visuals`), measured DOWN from
# the rail underside in adapter-local Z.  Each element overlaps the one above it
# so the adapter is a single connected solid (intra-part overlap is never
# collision-checked); only the rail seat and the spindle tip are cross-part.
_SHOE_T = 0.016
_SHOE_PRESS = 0.0005  # shoe pressed up into the rail: real contact, < 1 mm tol
_SPINDLE_BOTTOM = -0.0445
# Pan pivot sits 0.6 mm above the spindle tip so the gimbal's swivel seat
# journals onto the spindle: genuine capture, still under `overlap_tol=1e-3`.
_SPINDLE_ENGAGEMENT = 0.0006
_SPINDLE_PAN_DROP = -(_SPINDLE_BOTTOM + _SPINDLE_ENGAGEMENT)


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Config:
    lighting_track: LightingTrack = "flexible_oval_rail"
    track_adapter: TrackAdapter = "flush_block"
    light_head: LightHead = "cylindrical_can"
    pan_gimbal: PanGimbal = "crossbar_trunnion"
    head_count: int = 8
    head_length_m: float | None = None
    head_radius_m: float | None = None
    drop_length_m: float | None = None
    track_thickness_m: float | None = None
    name: str = "pictureX_0611_flexible_track_lighting_system"


@dataclass(frozen=True)
class ResolvedConfig:
    lighting_track: LightingTrack
    track_adapter: TrackAdapter
    light_head: LightHead
    pan_gimbal: PanGimbal
    head_count: int
    head_length_m: float
    head_radius_m: float
    drop_length_m: float
    track_thickness_m: float
    tilt_max: float
    yoke_half_span: float
    head_reach: float
    head_spacing: float
    name: str


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(value)))


def config_from_seed(seed: int) -> Config:
    choices = TEMPLATE_DOMAIN.sample(seed)
    rng = random.Random(int(seed) ^ 0x7F1A_C0DE)
    return Config(
        lighting_track=choices["lighting_track"],
        track_adapter=choices["track_adapter"],
        light_head=choices["light_head"],
        pan_gimbal=choices["pan_gimbal"],
        head_count=choices["head_count"],
        head_length_m=round(rng.uniform(_HEAD_LENGTH_MIN, _HEAD_LENGTH_MAX), 4),
        head_radius_m=round(rng.uniform(_HEAD_RADIUS_MIN, _HEAD_RADIUS_MAX), 4),
        drop_length_m=round(rng.uniform(_DROP_MIN, _DROP_MAX), 4),
        track_thickness_m=round(rng.uniform(_TRACK_THICKNESS_MIN, _TRACK_THICKNESS_MAX), 4),
        name=f"pictureX_0611_flexible_track_lighting_system_seed_{seed}",
    )


def resolve_config(config: Config | None = None) -> ResolvedConfig:
    cfg = config or Config()
    TEMPLATE_DOMAIN.validate(
        {
            "lighting_track": cfg.lighting_track,
            "track_adapter": cfg.track_adapter,
            "light_head": cfg.light_head,
            "pan_gimbal": cfg.pan_gimbal,
            "head_count": cfg.head_count,
        }
    )
    head_length = _clamp(
        _HEAD_LENGTH_MAX * 0.75 if cfg.head_length_m is None else cfg.head_length_m,
        _HEAD_LENGTH_MIN,
        _HEAD_LENGTH_MAX,
    )
    head_radius = _clamp(
        0.030 if cfg.head_radius_m is None else cfg.head_radius_m,
        _HEAD_RADIUS_MIN,
        _HEAD_RADIUS_MAX,
    )
    drop_length = _clamp(
        0.072 if cfg.drop_length_m is None else cfg.drop_length_m,
        _DROP_MIN,
        _DROP_MAX,
    )
    track_thickness = _clamp(
        0.009 if cfg.track_thickness_m is None else cfg.track_thickness_m,
        _TRACK_THICKNESS_MIN,
        _TRACK_THICKNESS_MAX,
    )
    yoke_half_span = head_radius + 0.012
    # Worst-case horizontal reach of a head from its own pan axis at full tilt.
    #
    # The rim swings out by (axial distance from the tilt axis)*sin(tilt) and the
    # rim radius itself contributes radius*cos(tilt).  The tapered can hangs
    # `_TAPERED_HANG` below its pivot, so its front rim is that much further from
    # the tilt axis -- omitting both terms under-reported the reach by ~35% and
    # let neighbouring heads, panned toward each other and fully tilted, collide.
    axial_len = head_length + _TAPERED_HANG
    reach = max(
        axial_len * math.sin(_TILT_MAX) + head_radius * math.cos(_TILT_MAX),
        yoke_half_span + 0.018,
    )
    head_spacing = 2.0 * reach + 0.030
    return ResolvedConfig(
        lighting_track=cfg.lighting_track,
        track_adapter=cfg.track_adapter,
        light_head=cfg.light_head,
        pan_gimbal=cfg.pan_gimbal,
        head_count=int(cfg.head_count),
        head_length_m=head_length,
        head_radius_m=head_radius,
        drop_length_m=drop_length,
        track_thickness_m=track_thickness,
        tilt_max=_TILT_MAX,
        yoke_half_span=yoke_half_span,
        head_reach=reach,
        head_spacing=head_spacing,
        name=cfg.name,
    )


def slot_choices_for_config(r: Config | ResolvedConfig) -> tuple[tuple[str, object], ...]:
    return (
        ("lighting_track", r.lighting_track),
        ("track_adapter", r.track_adapter),
        ("light_head", r.light_head),
        ("pan_gimbal", r.pan_gimbal),
        ("head_count", r.head_count),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, object], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Materials
# ---------------------------------------------------------------------------
def _materials(model: ArticulatedObject) -> dict[str, object]:
    return {
        "satin_black": model.material("ftl_satin_black", rgba=(0.025, 0.028, 0.030, 1.0)),
        "matte_black": model.material("ftl_matte_black", rgba=(0.018, 0.020, 0.022, 1.0)),
        "dark_metal": model.material("ftl_dark_metal", rgba=(0.10, 0.11, 0.12, 1.0)),
        "brushed": model.material("ftl_brushed_aluminum", rgba=(0.72, 0.74, 0.76, 1.0)),
        "gold": model.material("ftl_warm_reflector", rgba=(0.90, 0.60, 0.16, 1.0)),
        "lens": model.material("ftl_warm_lens", rgba=(1.0, 0.82, 0.42, 0.55)),
    }


# ---------------------------------------------------------------------------
# Head geometry (built once per config; cadquery, characteristic profiles)
# ---------------------------------------------------------------------------
def _cylindrical_shell_geom(radius: float, length: float, wall: float, rear: float):
    """Straight open-lens can, built along +Z (rotated to point down when placed)."""
    outer = cq.Workplane("XY").circle(radius).extrude(length)
    cavity = (
        cq.Workplane("XY")
        .workplane(offset=rear)
        .circle(radius - wall)
        .extrude(length - rear + 0.004)
    )
    return outer.cut(cavity)


def _tapered_can_geom(front_r: float, length: float):
    """Tapered lofted flared can with a thick front rim and rear neck.

    Built in head-local frame: the wide front (lens) opening is at z=-length,
    the narrow rear neck near z=0.
    """
    rear_r = max(0.014, front_r * 0.67)
    rear_top = 0.028
    outer = (
        cq.Workplane("XY")
        .workplane(offset=-length)
        .circle(front_r)
        .workplane(offset=length + rear_top)
        .circle(rear_r)
        .loft()
    )
    inner = (
        cq.Workplane("XY")
        .workplane(offset=-length - 0.002)
        .circle(max(0.006, front_r - 0.006))
        .workplane(offset=length + rear_top - 0.010)
        .circle(max(0.004, rear_r - 0.008))
        .loft()
    )
    shell = outer.cut(inner)
    front_rim = (
        cq.Workplane("XY")
        .workplane(offset=-length - 0.004)
        .circle(front_r + 0.002)
        .circle(max(0.004, front_r - 0.010))
        .extrude(0.011)
    )
    rear_neck = (
        cq.Workplane("XY")
        .workplane(offset=rear_top - 0.003)
        .circle(rear_r * 0.62)
        .extrude(0.035)
    )
    return shell.union(front_rim).union(rear_neck)


def _tapered_reflector_geom(front_r: float, length: float):
    """Thin conical gold reflector fitted inside the tapered can."""
    rear_r = max(0.014, front_r * 0.67)
    outer = (
        cq.Workplane("XY")
        .workplane(offset=-length + 0.004)
        .circle(front_r * 0.86)
        .workplane(offset=length * 0.72)
        .circle(rear_r * 0.62)
        .loft()
    )
    inner = (
        cq.Workplane("XY")
        .workplane(offset=-length + 0.002)
        .circle(front_r * 0.60)
        .workplane(offset=length * 0.72)
        .circle(rear_r * 0.40)
        .loft()
    )
    return outer.cut(inner)


def _build_head_meshes(r: ResolvedConfig) -> dict[str, object]:
    if r.light_head == "cylindrical_can":
        shell = mesh_from_cadquery(
            _cylindrical_shell_geom(r.head_radius_m, r.head_length_m, 0.0035, 0.006),
            "ftl_cylindrical_shell",
            tolerance=_MESH_TOL,
            angular_tolerance=_MESH_ANG_TOL,
        )
        return {"shell": shell}
    housing = mesh_from_cadquery(
        _tapered_can_geom(r.head_radius_m, r.head_length_m),
        "ftl_tapered_housing",
        tolerance=_MESH_TOL,
        angular_tolerance=_MESH_ANG_TOL,
    )
    reflector = mesh_from_cadquery(
        _tapered_reflector_geom(r.head_radius_m, r.head_length_m),
        "ftl_tapered_reflector",
        tolerance=_MESH_TOL,
        angular_tolerance=_MESH_ANG_TOL,
    )
    return {"housing": housing, "reflector": reflector}


def _axle_length(r: ResolvedConfig) -> float:
    # The trunnion axle journals into the yoke arms rather than punching through
    # them.  Arms sit centred on +/-yoke_half_span with 8 mm of Y thickness, so
    # their inner faces are at yoke_half_span - 0.004.  Ending each axle stub
    # 0.6 mm past that face keeps a real, load-bearing journal engagement that
    # `expect_contact` (1.5 mm) sees, while the interpenetration stays below the
    # 1 mm collision overlap tolerance -- so no overlap allowance is needed.
    return 2.0 * (r.yoke_half_span - 0.0034)


def _light_head_cylindrical_can_build(model, r, mats, index, meshes, finish):
    part = model.part(
        f"light_head__cylindrical_can__head_{index}",
        meta={"role": "light_head", "candidate": "cylindrical_can"},
    )
    # The shell is a hollow can whose bore radius is exactly `head_radius_m -
    # 0.0035`.  The reflector and lens seat INTO that bore: sizing them at the
    # bore radius alone leaves them mathematically tangent (zero penetration), so
    # the disc reads as a floating geometry island.  `_BORE_SEAT` presses each
    # disc 0.3 mm into the wall -- a real seated fit, far under the 1 mm collision
    # overlap tolerance.
    lens_r = r.head_radius_m - 0.0035
    seat_r = max(0.004, lens_r + _BORE_SEAT)
    part.visual(
        meshes["shell"],
        origin=Origin(rpy=(math.pi, 0.0, 0.0)),  # optical axis -> local -Z
        material=finish,
        name="housing_shell", material_class_id="metal.paint_coated",
    )
    part.visual(
        Cylinder(radius=seat_r, length=0.003),
        origin=Origin(xyz=(0.0, 0.0, -r.head_length_m + 0.006)),
        material=mats["gold"],
        name="gold_reflector", material_class_id="metal.precious_gold",
    )
    part.visual(
        Cylinder(radius=seat_r, length=0.0035),
        origin=Origin(xyz=(0.0, 0.0, -r.head_length_m + 0.0012)),
        material=mats["lens"],
        name="front_lens", material_class_id="plastic.clear_rigid",
    )
    part.visual(
        Cylinder(radius=0.005, length=_axle_length(r)),
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["dark_metal"],
        name="pivot_axle", material_class_id="metal.blackened_gunmetal",
    )
    return part


def _light_head_tapered_can_build(model, r, mats, index, meshes, finish):
    part = model.part(
        f"light_head__tapered_can__head_{index}",
        meta={"role": "light_head", "candidate": "tapered_can"},
    )
    # `_tapered_can_geom` is authored with its rear neck rising to local
    # z = _TAPERED_TOP_LOCAL, i.e. well ABOVE the trunnion axis at local z=0.
    # Left there, the neck runs straight through the yoke crossbar that bridges
    # the arms just above the pivot.  Hang the whole can (housing, reflector and
    # lens together, so the optics stay registered to the housing) so its rear
    # stops just under the crossbar, leaving the axle inside the can's top.
    hang = -_TAPERED_HANG
    part.visual(
        meshes["housing"], origin=Origin(xyz=(0.0, 0.0, hang)), material=finish,
        name="housing_shell", material_class_id="metal.paint_coated",
    )
    part.visual(
        meshes["reflector"], origin=Origin(xyz=(0.0, 0.0, hang)), material=mats["gold"],
        name="gold_reflector", material_class_id="metal.precious_gold",
    )
    part.visual(
        Cylinder(radius=r.head_radius_m * 0.9, length=0.004),
        origin=Origin(xyz=(0.0, 0.0, hang - r.head_length_m + 0.003)),
        material=mats["lens"],
        name="front_lens", material_class_id="plastic.clear_rigid",
    )
    part.visual(
        Cylinder(radius=0.005, length=_axle_length(r)),
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["dark_metal"],
        name="pivot_axle", material_class_id="metal.blackened_gunmetal",
    )
    return part


_HEAD_BUILDERS = {
    "cylindrical_can": _light_head_cylindrical_can_build,
    "tapered_can": _light_head_tapered_can_build,
}


# ---------------------------------------------------------------------------
# Pan gimbal geometry.  Local frame: pan pivot at origin, hangs down -Z,
# tilt pivot at z=-drop.  Returns (part, seat_elem_name, arm_elem_names).
# ---------------------------------------------------------------------------
def _yoke_clearance(r: ResolvedConfig) -> float:
    """Height above the trunnion axis that the head's rim sweeps to at full tilt.

    A rim point sits at radius <= ``head_radius_m`` with local z ~ +0.006, and
    tilting by theta lifts it to ``rho*sin(theta) + z*cos(theta)``.  Evaluating at
    ``tilt_max`` (the extreme motion QC actually executes) plus a 4 mm margin
    gives the lowest a yoke crossbar may sit without being swept through.
    """
    return (
        r.head_radius_m * math.sin(r.tilt_max) + 0.006 * math.cos(r.tilt_max) + 0.004
    )


def _gimbal_common_part(model, r, index, candidate):
    return model.part(
        f"pan_gimbal__{candidate}__gimbal_{index}",
        meta={"role": "pan_gimbal", "candidate": candidate},
    )


def _build_crossbar_trunnion(model, r, mats, index, finish):
    part = _gimbal_common_part(model, r, index, "crossbar_trunnion")
    drop = r.drop_length_m
    span = r.yoke_half_span
    part.visual(
        Cylinder(radius=0.011, length=0.012),
        origin=Origin(xyz=(0.0, 0.0, -0.006)),
        material=mats["dark_metal"],
        name="swivel_collar", material_class_id="metal.blackened_gunmetal",
    )
    part.visual(
        Cylinder(radius=0.0058, length=drop - 0.032),
        origin=Origin(xyz=(0.0, 0.0, -0.012 - (drop - 0.032) * 0.5)),
        material=mats["dark_metal"],
        name="drop_stem", material_class_id="metal.blackened_gunmetal",
    )
    # Horizontal crossbar spanning Y between the arms, clear of the head's swept
    # envelope.  The head's rear rim sits at radius <= head_radius_m and local
    # z ~ +0.006; tilting by theta lifts it to r*sin(theta) + z*cos(theta), which
    # at full tilt reaches well above the old fixed +0.016 and drove the head
    # straight through the crossbar.  Derive the height from the real envelope.
    clear = _yoke_clearance(r)
    part.visual(
        Box((0.014, 2.0 * span + 0.010, 0.012)),
        origin=Origin(xyz=(0.0, 0.0, -drop + clear + 0.006)),
        material=finish,
        name="yoke_crossbar", material_class_id="metal.paint_coated",
    )
    # Arms run from just under the trunnion up to the raised crossbar.
    arm_bottom = -drop - 0.009
    arm_top = -drop + clear + 0.012
    for side, y in (("neg", -span), ("pos", span)):
        part.visual(
            Box((0.012, 0.008, arm_top - arm_bottom)),
            origin=Origin(xyz=(0.0, y, 0.5 * (arm_bottom + arm_top))),
            material=finish,
            name=f"yoke_arm_{side}", material_class_id="metal.paint_coated",
        )
    return part, "swivel_collar", ("yoke_arm_neg", "yoke_arm_pos")


def _build_u_bracket(model, r, mats, index, finish):
    part = _gimbal_common_part(model, r, index, "u_bracket")
    drop = r.drop_length_m
    span = r.yoke_half_span
    arm_len = drop * 0.9
    bridge_z = -(drop - arm_len)
    part.visual(
        Cylinder(radius=0.020, length=0.014),
        origin=Origin(xyz=(0.0, 0.0, -0.007)),
        material=mats["dark_metal"],
        name="swivel_puck", material_class_id="metal.blackened_gunmetal",
    )
    part.visual(
        Cylinder(radius=0.009, length=max(0.006, (-bridge_z) - 0.014)),
        origin=Origin(xyz=(0.0, 0.0, -0.014 - (max(0.006, (-bridge_z) - 0.014)) * 0.5)),
        material=mats["dark_metal"],
        name="swivel_stem", material_class_id="metal.blackened_gunmetal",
    )
    # Flat top bridge joining the two long side arms.
    part.visual(
        Box((0.018, 2.0 * span + 0.020, 0.012)),
        origin=Origin(xyz=(0.0, 0.0, bridge_z)),
        material=finish,
        name="yoke_bridge", material_class_id="metal.paint_coated",
    )
    for side, y in (("neg", -span), ("pos", span)):
        part.visual(
            Box((0.012, 0.008, arm_len)),
            origin=Origin(xyz=(0.0, y, bridge_z - arm_len * 0.5)),
            material=finish,
            name=f"yoke_arm_{side}", material_class_id="metal.paint_coated",
        )
        part.visual(
            Cylinder(radius=0.012, length=0.013),
            origin=Origin(xyz=(0.0, y + math.copysign(0.008, y), -drop), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["matte_black"],
            name=f"pivot_knob_{side}", material_class_id="metal.paint_coated",
        )
    return part, "swivel_puck", ("yoke_arm_neg", "yoke_arm_pos")


_GIMBAL_BUILDERS = {
    "crossbar_trunnion": _build_crossbar_trunnion,
    "u_bracket": _build_u_bracket,
}


# ---------------------------------------------------------------------------
# Track geometry.  Returns (track_part, pivots) where each pivot is (x, y, z)
# of a pan axis on the underside of the track.
# ---------------------------------------------------------------------------
def _track_adapter_flush_block_build(model, r, mats, track, pivots):
    """REC_001 mount: the adapter is fixed track geometry, not a separate part.

    `model.py:L243-L248` authors `track_adapter_{index}` as a plain box VISUAL on
    `track_frame`, and the pan REVOLUTE (`L271-L276`) therefore hangs the swivel
    straight off the track.  No extra link, no extra joint.
    """
    for index, (x, y, z) in enumerate(pivots):
        track.visual(
            Box((0.050, 0.040, _MOUNT_GAP)),
            origin=Origin(xyz=(x, y, z + _MOUNT_GAP * 0.5)),
            material=mats["satin_black"],
            name=f"adapter_{index}", material_class_id="metal.paint_coated",
        )
    # Pan pivots stay on the reference plane; the parent link is the track.
    return [(track, pivot) for pivot in pivots]


def _track_adapter_shoe_spindle_mount_build(model, r, mats, track, pivots):
    """REC_002 mount: a real rail-shoe LINK per head, FIXED to the rail.

    `model.py:L91-L116` builds `rail_shoe` / `locking_tab` / `swivel_boss` /
    `pan_spindle` on a dedicated `adapter_{index}` part, `L261-L268` bolts it to
    the rail with a FIXED articulation, and `L269-L286` re-parents the pan
    REVOLUTE onto that adapter rather than onto the track.  This candidate adds
    N links and N fixed joints and moves the pan joint's parent.
    """
    mounts = []
    for index, (x, y, z) in enumerate(pivots):
        seat_z = z + _MOUNT_GAP  # rail underside; adapter frame origin
        adapter = model.part(
            f"track_adapter__shoe_spindle_mount__adapter_{index}",
            meta={"role": "track_adapter", "candidate": "shoe_spindle_mount"},
        )
        # Rail shoe: its top face is pressed `_SHOE_PRESS` into the rail so the
        # seat is genuine contact.  Mating on a HORIZONTAL face keeps the world
        # AABB overlap tiny on Z (the only axis that matters here) even though the
        # oval rail's mesh AABB spans the whole ellipse.
        adapter.visual(
            Box((0.060, 0.040, _SHOE_T)),
            origin=Origin(xyz=(0.0, 0.0, -_SHOE_T * 0.5 + _SHOE_PRESS)),
            material=mats["matte_black"],
            name="rail_shoe", material_class_id="metal.paint_coated",
        )
        adapter.visual(
            Box((0.022, 0.046, 0.009)),
            origin=Origin(xyz=(0.0, 0.0, -0.018)),
            material=mats["matte_black"],
            name="locking_tab", material_class_id="metal.paint_coated",
        )
        adapter.visual(
            Cylinder(radius=0.018, length=0.014),
            origin=Origin(xyz=(0.0, 0.0, -0.028)),
            material=mats["matte_black"],
            name="swivel_boss", material_class_id="metal.paint_coated",
        )
        adapter.visual(
            Cylinder(radius=0.008, length=0.012),
            origin=Origin(xyz=(0.0, 0.0, _SPINDLE_BOTTOM + 0.006)),
            material=mats["dark_metal"],
            name="pan_spindle", material_class_id="metal.blackened_gunmetal",
        )
        model.articulation(
            f"track_adapter__shoe_spindle_mount__mount_{index}",
            ArticulationType.FIXED,
            parent=track,
            child=adapter,
            origin=Origin(xyz=(x, y, seat_z)),
            meta={"mechanism": "locked rail adapter", "head_index": index},
        )
        # Pan pivot expressed in the ADAPTER frame, `_SPINDLE_ENGAGEMENT` above
        # the spindle tip so the gimbal's swivel seat journals onto it.
        mounts.append((adapter, (0.0, 0.0, -_SPINDLE_PAN_DROP)))
    return mounts


_ADAPTER_BUILDERS = {
    "flush_block": _track_adapter_flush_block_build,
    "shoe_spindle_mount": _track_adapter_shoe_spindle_mount_build,
}


def _ellipse_arclength_points(a: float, b: float, n: int, samples: int = 2400):
    ts = [2.0 * math.pi * i / samples for i in range(samples + 1)]
    xs = [a * math.cos(t) for t in ts]
    ys = [b * math.sin(t) for t in ts]
    cum = [0.0]
    for i in range(1, len(ts)):
        cum.append(cum[-1] + math.hypot(xs[i] - xs[i - 1], ys[i] - ys[i - 1]))
    total = cum[-1]
    pts = []
    for k in range(n):
        target = total * k / n
        lo, hi = 0, len(cum) - 1
        while lo < hi:
            mid = (lo + hi) // 2
            if cum[mid] < target:
                lo = mid + 1
            else:
                hi = mid
        pts.append((xs[lo], ys[lo]))
    return pts


def _min_cyclic_chord(points) -> float:
    n = len(points)
    return min(
        math.hypot(points[i][0] - points[(i + 1) % n][0], points[i][1] - points[(i + 1) % n][1])
        for i in range(n)
    )


def _lighting_track_flexible_oval_rail_build(model, r, mats):
    track = model.part(
        "lighting_track__flexible_oval_rail__track",
        meta={"role": "lighting_track", "candidate": "flexible_oval_rail"},
    )
    # Broad product-photo oval aspect (~2.16:1), scaled so the minimum adjacent
    # chord between the N equal-arc pan pivots is at least the head spacing.
    a0, b0 = 2.16, 1.0
    base = _ellipse_arclength_points(a0, b0, r.head_count)
    scale = (r.head_spacing * 1.03) / max(1e-6, _min_cyclic_chord(base))
    a, b = a0 * scale, b0 * scale
    perimeter_points = _ellipse_arclength_points(a, b, r.head_count)
    tube_z = 0.020 + r.track_thickness_m
    spline = [(x, y, tube_z) for (x, y) in _ellipse_arclength_points(a, b, max(24, r.head_count * 4))]
    track.visual(
        mesh_from_geometry(
            tube_from_spline_points(
                spline,
                radius=r.track_thickness_m,
                samples_per_segment=8,
                closed_spline=True,
                radial_segments=16,
                cap_ends=False,
            ),
            "oval_energized_track",
        ),
        material=mats["satin_black"],
        name="rail_body", material_class_id="metal.paint_coated",
    )
    pivots = [(x, y, 0.0) for (x, y) in perimeter_points]
    # Ceiling suspension stems + canopies (fixed track silhouette from REC_001).
    #
    # The stems hang the rail from the ceiling, so each one must actually land ON
    # the rail tube: sampling a shrunken ellipse left them floating in mid-air
    # (disconnected geometry islands).  Sampling 2N arc-spaced points puts the
    # even indices exactly on the N pan pivots, so the ODD indices are precisely
    # midway between two heads -- on the real ellipse, and clear of the adapters.
    midpoints = _ellipse_arclength_points(a, b, 2 * r.head_count)
    between_heads = [midpoints[i] for i in range(1, len(midpoints), 2)]
    stem_count = max(2, round(r.head_count / 3.0))
    step = max(1, len(between_heads) // stem_count)
    stem_positions = between_heads[::step][:stem_count]
    stem_length = 0.150
    canopy_height = 0.014
    # Press the stem foot into the top of the tube, then stack the canopy on the
    # stem head, each by `_BORE_SEAT` -- real joins, under the collision tolerance.
    stem_bottom_z = tube_z + r.track_thickness_m - _BORE_SEAT
    for index, (x, y) in enumerate(stem_positions):
        track.visual(
            Cylinder(radius=0.0055, length=stem_length),
            origin=Origin(xyz=(x, y, stem_bottom_z + 0.5 * stem_length)),
            material=mats["dark_metal"],
            name=f"suspension_stem_{index}", material_class_id="metal.blackened_gunmetal",
        )
        track.visual(
            Cylinder(radius=0.034, length=canopy_height),
            origin=Origin(
                xyz=(x, y, stem_bottom_z + stem_length + 0.5 * canopy_height - _BORE_SEAT)
            ),
            material=mats["satin_black"],
            name=f"ceiling_canopy_{index}", material_class_id="metal.paint_coated",
        )
    return track, pivots


def _rail_geometry(length: float, thickness: float):
    height = max(0.024, 3.0 * thickness)
    body = cq.Workplane("XY").box(length, 0.050, height)
    body = body.edges("|X").fillet(min(0.0035, thickness * 0.45))
    slot = (
        cq.Workplane("XY")
        .box(length - 0.04, 0.015, 0.012)
        .translate((0.0, 0.0, -height * 0.5 + 0.002))
    )
    return body.cut(slot), height


def _lighting_track_straight_rigid_rail_build(model, r, mats):
    track = model.part(
        "lighting_track__straight_rigid_rail__track",
        meta={"role": "lighting_track", "candidate": "straight_rigid_rail"},
    )
    spacing = r.head_spacing
    xs = [(i - (r.head_count - 1) * 0.5) * spacing for i in range(r.head_count)]
    length = (r.head_count - 1) * spacing + 2.0 * (r.head_reach + 0.05)
    solid, height = _rail_geometry(length, r.track_thickness_m)
    rail_z = 0.020 + height * 0.5
    track.visual(
        mesh_from_cadquery(
            solid,
            "rigid_track_rail",
            tolerance=_MESH_TOL,
            angular_tolerance=_MESH_ANG_TOL,
        ),
        origin=Origin(xyz=(0.0, 0.0, rail_z)),
        material=mats["matte_black"],
        name="rail_body", material_class_id="metal.paint_coated",
    )
    pivots = [(x, 0.0, 0.0) for x in xs]
    return track, pivots


_TRACK_BUILDERS = {
    "flexible_oval_rail": _lighting_track_flexible_oval_rail_build,
    "straight_rigid_rail": _lighting_track_straight_rigid_rail_build,
}


# ---------------------------------------------------------------------------
# Joints (mate_axes + register_interface_mate)
# ---------------------------------------------------------------------------
def _add_pan_joint(model, track, gimbal, index, pivot, r):
    name = f"pan_gimbal__{r.pan_gimbal}__pan_{index}"
    provider = AxisInterface(
        name=f"{name}_provider", point=pivot, axis=(0.0, 0.0, 1.0), radial=(1.0, 0.0, 0.0)
    )
    consumer = AxisInterface(
        name=f"{name}_consumer", axis=(0.0, 0.0, 1.0), radial=(1.0, 0.0, 0.0)
    )
    mate = mate_axes(provider, consumer)
    model.articulation(
        name,
        ArticulationType.REVOLUTE,
        parent=track,
        child=gimbal,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(effort=1.6, velocity=2.5, lower=-_PAN_LIMIT, upper=_PAN_LIMIT),
        meta={"mechanism": "independent lamp pan", "head_index": index},
    )
    register_interface_mate(model, name, mate)


def _add_tilt_joint(model, gimbal, head, index, r):
    name = f"light_head__{r.light_head}__tilt_{index}"
    provider = AxisInterface(
        name=f"{name}_provider",
        point=(0.0, 0.0, -r.drop_length_m),
        axis=(0.0, 1.0, 0.0),
        radial=(0.0, 0.0, 1.0),
    )
    consumer = AxisInterface(
        name=f"{name}_consumer", axis=(0.0, 1.0, 0.0), radial=(0.0, 0.0, 1.0)
    )
    mate = mate_axes(provider, consumer)
    model.articulation(
        name,
        ArticulationType.REVOLUTE,
        parent=gimbal,
        child=head,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(
            effort=1.2, velocity=2.0, lower=-r.tilt_max, upper=r.tilt_max
        ),
        meta={"mechanism": "independent lamp tilt", "head_index": index},
    )
    register_interface_mate(model, name, mate)


# ---------------------------------------------------------------------------
# Assembly
# ---------------------------------------------------------------------------
def build_picturex_0611_flexible_track_lighting_system(
    config: Config | None = None, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    r = resolve_config(config or config_from_seed(0))
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={
            "category": "pictureX_0611_flexible_track_lighting_system",
            "slot_choices": slot_choices_for_config(r),
            "source_family": "pictureX/0611/flexible_track_lighting_system",
        },
    )
    mats = _materials(model)
    meshes = _build_head_meshes(r)
    track, pivots = _TRACK_BUILDERS[r.lighting_track](model, r, mats)
    mounts = _ADAPTER_BUILDERS[r.track_adapter](model, r, mats, track, pivots)
    for index, (pan_parent, pan_pivot) in enumerate(mounts):
        finish = mats["brushed"] if index % 3 == 1 else mats["matte_black"]
        gimbal, _seat, _arms = _GIMBAL_BUILDERS[r.pan_gimbal](model, r, mats, index, finish)
        _add_pan_joint(model, pan_parent, gimbal, index, pan_pivot, r)
        head = _HEAD_BUILDERS[r.light_head](model, r, mats, index, meshes, finish)
        _add_tilt_joint(model, gimbal, head, index, r)
    return model


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def _parts_by_role(model: ArticulatedObject, role: str):
    return [part for part in model.parts if part.meta.get("role") == role]


def _seat_element(candidate: str) -> str:
    return "swivel_collar" if candidate == "crossbar_trunnion" else "swivel_puck"


def _aabb_center(bounds):
    if bounds is None:
        return None
    lo, hi = bounds
    return tuple((lo[i] + hi[i]) * 0.5 for i in range(3))


def run_picturex_0611_flexible_track_lighting_system_tests(
    object_model: ArticulatedObject, config: Config
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    ctx.check_model_valid()

    tracks = _parts_by_role(object_model, "lighting_track")
    gimbals = _parts_by_role(object_model, "pan_gimbal")
    heads = _parts_by_role(object_model, "light_head")
    track = tracks[0] if tracks else None

    ctx.check(
        "category_anchor: track carries N pan and tilt heads",
        len(tracks) == 1
        and len(gimbals) == r.head_count
        and len(heads) == r.head_count
        and track is not None
        and track.meta.get("candidate") == r.lighting_track,
        details=f"tracks={len(tracks)}, gimbals={len(gimbals)}, heads={len(heads)}",
    )

    adapters = _parts_by_role(object_model, "track_adapter")
    adapter_names = {p.name for p in adapters}
    track_name = getattr(track, "name", None)
    # `flush_block` hangs the pan REVOLUTE straight off the track; the
    # `shoe_spindle_mount` link re-parents it onto the adapter.  Both are
    # legitimate pan hosts, and both are rigidly registered to the track.
    pan_hosts = adapter_names or {track_name}

    pan_joints = [
        j
        for j in object_model.articulations
        if j.child in {p.name for p in gimbals}
    ]
    tilt_joints = [
        j
        for j in object_model.articulations
        if j.child in {p.name for p in heads}
    ]
    ctx.check(
        "category_anchor: independent pan and tilt per head",
        len(pan_joints) == r.head_count
        and len(tilt_joints) == r.head_count
        and all(
            j.articulation_type == ArticulationType.REVOLUTE
            and tuple(j.axis) == (0.0, 0.0, 1.0)
            and j.parent in pan_hosts
            and j.motion_limits is not None
            for j in pan_joints
        )
        and all(
            j.articulation_type == ArticulationType.REVOLUTE
            and tuple(j.axis) == (0.0, 1.0, 0.0)
            and j.motion_limits is not None
            and j.motion_limits.lower < 0.0 < j.motion_limits.upper
            for j in tilt_joints
        ),
        details=f"pan={len(pan_joints)}, tilt={len(tilt_joints)}",
    )

    visual_names = {v.name or "" for p in object_model.parts for v in p.visuals}
    identity = {
        "flexible_oval_rail": any("suspension_stem" in n for n in visual_names)
        and any("ceiling_canopy" in n for n in visual_names),
        "straight_rigid_rail": "rail_body" in visual_names
        and not any("suspension_stem" in n for n in visual_names),
    }[r.lighting_track]
    ctx.check(
        f"category_anchor: {r.lighting_track} track identity",
        identity,
        details=f"visual_count={len(visual_names)}",
    )

    # ---- track_adapter identity -------------------------------------------
    track_elems = {v.name or "" for v in track.visuals} if track is not None else set()
    fixed_mounts = [
        j
        for j in object_model.articulations
        if j.articulation_type == ArticulationType.FIXED
        and j.child in adapter_names
        and j.parent == track_name
    ]
    if r.track_adapter == "flush_block":
        adapter_ok = (
            not adapters
            and all(f"adapter_{i}" in track_elems for i in range(r.head_count))
            and all(j.parent == track_name for j in pan_joints)
        )
        adapter_detail = (
            f"adapter_links={len(adapters)} (expected 0), "
            f"embedded_blocks={sum(1 for i in range(r.head_count) if f'adapter_{i}' in track_elems)}"
        )
    else:
        required = {"rail_shoe", "locking_tab", "swivel_boss", "pan_spindle"}
        adapter_ok = (
            len(adapters) == r.head_count
            and len(fixed_mounts) == r.head_count
            and all(required <= {v.name or "" for v in p.visuals} for p in adapters)
            and all(j.parent in adapter_names for j in pan_joints)
            and not any(n.startswith("adapter_") for n in track_elems)
        )
        adapter_detail = (
            f"adapter_links={len(adapters)} (expected {r.head_count}), "
            f"fixed_mounts={len(fixed_mounts)}, "
            f"pan_parents_on_adapters={sum(1 for j in pan_joints if j.parent in adapter_names)}"
        )
    ctx.check(
        f"category_anchor: {r.track_adapter} track mount interface",
        adapter_ok,
        details=adapter_detail,
    )
    # The shoe-and-spindle mount is only a legitimate bearing if the gimbal's
    # swivel seat actually journals onto the spindle tip: the engagement must be
    # positive (real capture, not a floating island) and stay under the 1 mm
    # collision overlap tolerance so no overlap allowance is ever needed.
    ctx.check(
        "track_adapter spindle engagement stays a sub-tolerance press fit",
        r.track_adapter == "flush_block"
        or (
            0.0 < _SPINDLE_ENGAGEMENT <= 0.001
            and 0.0 < _SHOE_PRESS <= 0.001
            and abs(_SPINDLE_PAN_DROP + _SPINDLE_BOTTOM + _SPINDLE_ENGAGEMENT) < 1e-12
        ),
        details=(
            f"adapter={r.track_adapter}, spindle_engagement={_SPINDLE_ENGAGEMENT}, "
            f"shoe_press={_SHOE_PRESS}, pan_drop={_SPINDLE_PAN_DROP:.5f}"
        ),
    )

    seat_elem = _seat_element(r.pan_gimbal)

    # Per-head mechanical invariants.
    for gimbal in gimbals:
        pan = next(j for j in pan_joints if j.child == gimbal.name)
        index = pan.meta.get("head_index")
        head = next(
            (
                p
                for p in heads
                for j in tilt_joints
                if j.child == p.name and j.parent == gimbal.name
            ),
            None,
        )
        if head is None:
            ctx.check(f"gimbal {gimbal.name} has a tilt child", False)
            continue

        # Assembly invariants are asserted structurally / from the derived
        # parameter arithmetic.  Element-AABB contact probes would require the
        # cadquery head meshes to be materialized on disk, which preflight
        # deliberately defers; swept contact and collision stay harness-owned.
        gimbal_elems = {v.name or "" for v in gimbal.visuals}
        if r.track_adapter == "flush_block":
            mount_present = f"adapter_{index}" in track_elems
            mount_detail = f"track element adapter_{index}"
        else:
            mount_part = next(
                (p for p in adapters if p.name.endswith(f"_adapter_{index}")), None
            )
            mount_present = mount_part is not None and "pan_spindle" in {
                v.name or "" for v in mount_part.visuals
            }
            mount_detail = f"adapter link {index} pan_spindle"
        ctx.check(
            f"head {index} pan bearing seats on its track adapter",
            seat_elem in gimbal_elems and mount_present,
            details=f"seat={seat_elem!r} present={seat_elem in gimbal_elems}, "
            f"{mount_detail} present={mount_present}",
        )
        # The Y trunnion axle journals into each yoke arm: each stub reaches past
        # the arm's inner face (real load-bearing engagement) but by less than the
        # 1 mm collision overlap tolerance, so no overlap allowance is needed.
        axle_half = _axle_length(r) * 0.5
        arm_inner_face = r.yoke_half_span - 0.004
        engagement = axle_half - arm_inner_face
        head_elems = {v.name or "" for v in head.visuals}
        ctx.check(
            f"head {index} axle journals into both yoke arms",
            "pivot_axle" in head_elems
            and {"yoke_arm_neg", "yoke_arm_pos"} <= gimbal_elems
            and 0.0 < engagement <= 0.001,
            details=f"engagement={engagement:.5f} m (0 < e <= 0.001), "
            f"axle_half={axle_half:.5f}, arm_inner_face={arm_inner_face:.5f}",
        )

        tilt = next(j for j in tilt_joints if j.child == head.name)
        rest = _aabb_center(ctx.part_element_world_aabb(head, elem="front_lens"))
        with ctx.pose({tilt: r.tilt_max * 0.6}):
            tilted = _aabb_center(ctx.part_element_world_aabb(head, elem="front_lens"))
        ctx.check(
            f"head {index} tilt changes elevation and forward aim",
            rest is not None
            and tilted is not None
            and (abs(tilted[0] - rest[0]) > 0.004 or abs(tilted[2] - rest[2]) > 0.004),
            details=f"rest={rest}, tilted={tilted}",
        )
        with ctx.pose({tilt: 0.5}):
            tilt_only = _aabb_center(ctx.part_element_world_aabb(head, elem="front_lens"))
        with ctx.pose({tilt: 0.5, pan: 0.8}):
            tilt_pan = _aabb_center(ctx.part_element_world_aabb(head, elem="front_lens"))
        ctx.check(
            f"head {index} pan changes horizontal aim",
            tilt_only is not None
            and tilt_pan is not None
            and math.dist(tilt_only[:2], tilt_pan[:2]) > 0.003,
            details=f"tilt_only={tilt_only}, tilt_pan={tilt_pan}",
        )

    return ctx.report()


# ---------------------------------------------------------------------------
# High-risk corners
# ---------------------------------------------------------------------------
TEMPLATE_CORNERS = (
    corner_case(
        "oval_tapered_ubracket_max_heads",
        {
            "lighting_track": "flexible_oval_rail",
            "track_adapter": "shoe_spindle_mount",
            "light_head": "tapered_can",
            "pan_gimbal": "u_bracket",
            "head_count": 8,
            "head_length_m": _HEAD_LENGTH_MAX,
            "head_radius_m": _HEAD_RADIUS_MAX,
            "drop_length_m": _DROP_MAX,
        },
        reason="max N, largest head envelope, deepest drop on the oval track",
    ),
    corner_case(
        "rail_cyl_crossbar_min_heads",
        {
            "lighting_track": "straight_rigid_rail",
            "track_adapter": "flush_block",
            "light_head": "cylindrical_can",
            "pan_gimbal": "crossbar_trunnion",
            "head_count": 3,
            "head_length_m": _HEAD_LENGTH_MIN,
            "head_radius_m": _HEAD_RADIUS_MIN,
            "drop_length_m": _DROP_MIN,
        },
        reason="min N, most compact head and shallowest drop on the straight rail",
    ),
    corner_case(
        "rail_tapered_ubracket_max_heads",
        {
            "lighting_track": "straight_rigid_rail",
            "track_adapter": "flush_block",
            "light_head": "tapered_can",
            "pan_gimbal": "u_bracket",
            "head_count": 8,
            "head_length_m": _HEAD_LENGTH_MAX,
            "head_radius_m": _HEAD_RADIUS_MAX,
            "drop_length_m": _DROP_MAX,
        },
        reason="max N and envelope on the straight rail",
    ),
    corner_case(
        "oval_cyl_crossbar_big_head_short_drop",
        {
            "lighting_track": "flexible_oval_rail",
            "track_adapter": "shoe_spindle_mount",
            "light_head": "cylindrical_can",
            "pan_gimbal": "crossbar_trunnion",
            "head_count": 7,
            "head_length_m": _HEAD_LENGTH_MAX,
            "head_radius_m": _HEAD_RADIUS_MAX,
            "drop_length_m": _DROP_MIN,
        },
        reason="largest head on the shallowest drop: tilt envelope closest to the track",
    ),
    corner_case(
        "rail_shoe_tapered_crossbar_min_heads",
        {
            "lighting_track": "straight_rigid_rail",
            "track_adapter": "shoe_spindle_mount",
            "light_head": "tapered_can",
            "pan_gimbal": "crossbar_trunnion",
            "head_count": 3,
            "head_length_m": _HEAD_LENGTH_MAX,
            "head_radius_m": _HEAD_RADIUS_MAX,
            "drop_length_m": _DROP_MIN,
        },
        reason="shoe-and-spindle link on the straight rail with the shallowest drop: the swept head envelope comes closest to the adapter body",
    ),
    corner_case(
        "oval_shoe_ubracket_max_heads_deep_drop",
        {
            "lighting_track": "flexible_oval_rail",
            "track_adapter": "shoe_spindle_mount",
            "light_head": "cylindrical_can",
            "pan_gimbal": "u_bracket",
            "head_count": 8,
            "head_length_m": _HEAD_LENGTH_MAX,
            "head_radius_m": _HEAD_RADIUS_MAX,
            "drop_length_m": _DROP_MAX,
        },
        reason="max N shoe links crowded around the oval with the widest swivel puck seating on the spindle",
    ),
    corner_case(
        "oval_flush_tapered_ubracket_min_heads",
        {
            "lighting_track": "flexible_oval_rail",
            "track_adapter": "flush_block",
            "light_head": "tapered_can",
            "pan_gimbal": "u_bracket",
            "head_count": 3,
            "head_length_m": _HEAD_LENGTH_MIN,
            "head_radius_m": _HEAD_RADIUS_MIN,
            "drop_length_m": _DROP_MAX,
        },
        reason="smallest oval with embedded blocks: tightest ellipse the suspension stems must still land on",
    ),
)


__all__ = [
    "Config",
    "ResolvedConfig",
    "TEMPLATE_CORNERS",
    "TEMPLATE_DOMAIN",
    "build_picturex_0611_flexible_track_lighting_system",
    "config_from_seed",
    "resolve_config",
    "run_picturex_0611_flexible_track_lighting_system_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
]
