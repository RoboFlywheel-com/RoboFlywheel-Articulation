# SPDX-License-Identifier: Apache-2.0

"""Angle grinder — modular procedural template.

Mixed parallel topology. A grounded ``body`` (motor housing lathe + right-angle
gear head loft) is the root. Every active sub-assembly parents directly to the
body (parallel children, no serial chain):

* ``spindle_disc`` CONTINUOUS — the abrasive/cutting disc that defines the
  category. Always present, always spinning about the vertical spindle axis.
* ``spindle_lock`` PRISMATIC — baseline lock button on the gear head (always).
* Slot A ``disc_guard`` — bare_disc (no guard) / half_shroud_guard (cadquery
  half shroud, REVOLUTE about spindle) / cutting_wheel_guard (loft arc-wall
  guard, REVOLUTE about spindle; disc becomes a thin cutting wheel).
* Slot B ``switch`` — top_slide (PRISMATIC) / deadman_trigger (REVOLUTE) /
  top_rocker (REVOLUTE). Mutually exclusive; exactly one switch part exists.
* Slot C ``power_source`` — corded (strain-relief boot + drooping cord on the
  body) / cordless (slide-on battery rail on the body + ``battery_pack``
  PRISMATIC release).
* Multiplicity ``handle_boss_count`` {1,2,3} — threaded side-handle bosses, one
  FIXED part each, around the gear head (flanks + top).

seed=0 anchor: bare_disc + top_slide + corded + 1 handle boss (the parent).

Sources (5★, adapted verbatim — no primitive downgrade):
* body / spindle_disc / top_slide / corded / spindle_lock — parent record
  rec_model-a-compact-electric-angle-grinder-...-grinder_..._28a8a3ef
* half_shroud_guard — rec_angle_grinder_var_guard (cadquery)
* cutting_wheel_guard — rec_angle_grinder_var_guardcut (loft arc-wall mesh)
* deadman_trigger — rec_angle_grinder_var_trigger
* top_rocker — rec_angle_grinder_var_rocker (cadquery filleted body)
* cordless — rec_angle_grinder_var_cordless
* handle_boss multiplicity — rec_angle_grinder_var_handle{2,3}
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Literal

import cadquery as cq

from sdk import (
    AppearanceOnlySpec,
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    CylinderGeometry,
    LatheGeometry,
    LoftGeometry,
    MeshGeometry,
    MotionLimits,
    Origin,
    Part,
    TestContext,
    TestReport,
    mesh_from_cadquery,
    mesh_from_geometry,
    rounded_rect_profile,
    tube_from_spline_points,
)

__modular__ = True


# ---------------------------------------------------------------------------
# Slot enums
# ---------------------------------------------------------------------------
DiscGuard = Literal["bare_disc", "half_shroud_guard", "cutting_wheel_guard"]
Switch = Literal["top_slide", "deadman_trigger", "top_rocker"]
PowerSource = Literal["corded", "cordless"]
PaletteStyle = Literal["yellow_black", "teal", "red", "green"]

DISC_GUARD_MODULES: tuple[DiscGuard, ...] = (
    "bare_disc",
    "half_shroud_guard",
    "cutting_wheel_guard",
)
SWITCH_MODULES: tuple[Switch, ...] = ("top_slide", "deadman_trigger", "top_rocker")
POWER_MODULES: tuple[PowerSource, ...] = ("corded", "cordless")
HANDLE_BOSS_COUNTS: tuple[int, ...] = (1, 2, 3)


# ---------------------------------------------------------------------------
# Palettes. Each palette names every material the visuals reference. Per-seed
# palette diversity (>= 3 distinct named materials) is required: every .visual
# gets a named material; no bare RGB inside factories.
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "yellow_black": {
        "housing": (0.95, 0.72, 0.06, 1.0),
        "trim": (0.08, 0.08, 0.08, 1.0),
        "rubber": (0.05, 0.05, 0.05, 1.0),
        "steel": (0.60, 0.61, 0.63, 1.0),
        "fiber": (0.46, 0.38, 0.29, 1.0),
    },
    "teal": {
        "housing": (0.10, 0.55, 0.55, 1.0),
        "trim": (0.10, 0.11, 0.12, 1.0),
        "rubber": (0.06, 0.06, 0.07, 1.0),
        "steel": (0.62, 0.64, 0.66, 1.0),
        "fiber": (0.50, 0.42, 0.31, 1.0),
    },
    "red": {
        "housing": (0.78, 0.12, 0.12, 1.0),
        "trim": (0.09, 0.09, 0.09, 1.0),
        "rubber": (0.05, 0.05, 0.05, 1.0),
        "steel": (0.61, 0.62, 0.64, 1.0),
        "fiber": (0.45, 0.37, 0.28, 1.0),
    },
    "green": {
        "housing": (0.15, 0.45, 0.18, 1.0),
        "trim": (0.08, 0.08, 0.09, 1.0),
        "rubber": (0.05, 0.05, 0.06, 1.0),
        "steel": (0.60, 0.61, 0.63, 1.0),
        "fiber": (0.47, 0.39, 0.30, 1.0),
    },
}


# ---------------------------------------------------------------------------
# Layout constants (meters). Motor axis runs along X: rear grip at -X, gear
# head at +X. The spindle axis is vertical (Z); the disc sits under the head.
# (Adapted from the parent record's module-scope constants.)
# ---------------------------------------------------------------------------
MOTOR_AXIS_Z = 0.062
BARREL_RADIUS = 0.035
BARREL_FRONT_X = -0.035
HEAD_REAR_X = -0.050
HEAD_CENTER_Z = 0.060
HEAD_TOP_Z = 0.0991
COLLAR_BOTTOM_Z = 0.014
SWITCH_X = -0.115
DISC_RADIUS = 0.0575
WHEEL_THICKNESS = 0.0010  # thin cutting wheel for cutting_wheel_guard
TRIGGER_PIVOT_X = -0.195
FLANK_Y = 0.033  # gear-head lateral flank where bosses mount


# ---------------------------------------------------------------------------
# Public + resolved config
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class AngleGrinderConfig:
    disc_guard: DiscGuard | None = None
    switch: Switch | None = None
    power_source: PowerSource | None = None
    palette_style: PaletteStyle = "yellow_black"
    handle_boss_count: int = 1
    body_scale: float = 1.0
    palette: dict[str, tuple[float, float, float, float]] = field(
        default_factory=lambda: dict(PALETTES["yellow_black"])
    )


@dataclass(frozen=True)
class ResolvedAngleGrinderConfig:
    disc_guard: DiscGuard
    switch: Switch
    power_source: PowerSource
    palette_style: PaletteStyle
    handle_boss_count: int
    body_scale: float
    palette: dict[str, tuple[float, float, float, float]]


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(v)))


def config_from_seed(seed: int) -> AngleGrinderConfig:
    if seed == 0:
        return AngleGrinderConfig(
            disc_guard="bare_disc",
            switch="top_slide",
            power_source="corded",
            palette_style="yellow_black",
            handle_boss_count=1,
            body_scale=1.0,
        )
    rng = random.Random(seed)
    disc_guard = rng.choice(DISC_GUARD_MODULES)
    power_source = rng.choice(POWER_MODULES)
    switch = rng.choice(SWITCH_MODULES)
    # Compatibility gate: a slide-on battery pack occupies the rear grip
    # underside, which collides with the deadman trigger's pivot/paddle that
    # hangs from the same region. Re-sample the switch to a top-mounted
    # control when cordless. (corded+deadman_trigger remains eligible.)
    if power_source == "cordless" and switch == "deadman_trigger":
        switch = rng.choice(("top_slide", "top_rocker"))
    return AngleGrinderConfig(
        disc_guard=disc_guard,
        switch=switch,
        power_source=power_source,
        palette_style=rng.choice(tuple(PALETTES.keys())),
        handle_boss_count=rng.choice(HANDLE_BOSS_COUNTS),
        body_scale=round(rng.uniform(0.9, 1.12), 4),
    )


def resolve_config(config: AngleGrinderConfig) -> ResolvedAngleGrinderConfig:
    disc_guard = config.disc_guard or "bare_disc"
    switch = config.switch or "top_slide"
    power_source = config.power_source or "corded"
    for value, pool, label in (
        (disc_guard, DISC_GUARD_MODULES, "disc_guard"),
        (switch, SWITCH_MODULES, "switch"),
        (power_source, POWER_MODULES, "power_source"),
    ):
        if value not in pool:
            raise ValueError(f"Unsupported {label}: {value!r}")
    if config.palette_style not in PALETTES:
        raise ValueError(f"Unsupported palette_style: {config.palette_style!r}")
    if config.handle_boss_count not in HANDLE_BOSS_COUNTS:
        raise ValueError(f"Unsupported handle_boss_count: {config.handle_boss_count!r}")
    if power_source == "cordless" and switch == "deadman_trigger":
        raise ValueError(
            "Incompatible combo: cordless battery + deadman_trigger occupy the "
            "same rear-underside volume."
        )
    return ResolvedAngleGrinderConfig(
        disc_guard=disc_guard,
        switch=switch,
        power_source=power_source,
        palette_style=config.palette_style,
        handle_boss_count=int(config.handle_boss_count),
        body_scale=_clamp(config.body_scale, 0.9, 1.12),
        palette=dict(PALETTES[config.palette_style]),
    )


# ===========================================================================
# body (root)
# ===========================================================================
def _build_body(model: ArticulatedObject, r: ResolvedAngleGrinderConfig) -> Part:
    body = model.part("body")

    # Tapered cylindrical motor housing built as a lathe along +Z, then
    # rotated so the lathe axis becomes -X (front at x=BARREL_FRONT_X).
    housing_profile = [
        (0.0, 0.0),
        (0.0345, 0.0),
        (0.035, 0.012),
        (0.035, 0.130),
        (0.032, 0.160),
        (0.0285, 0.185),
        (0.0265, 0.205),
        (0.0258, 0.210),
        (0.0, 0.210),
    ]
    housing_geom = LatheGeometry(housing_profile, segments=48)
    housing_geom.rotate_y(-math.pi / 2.0)  # lathe +Z -> world -X
    housing_geom.translate(BARREL_FRONT_X, 0.0, MOTOR_AXIS_Z)
    body.visual(
        mesh_from_geometry(housing_geom, "motor_housing"),
        material="housing",
        name="motor_housing", material_class_id="plastic.opaque_glossy_molded",
    )

    # Right-angle gear head: rounded-rectangle loft narrowing to the front.
    head_sections = []
    for vert, lat, rad, zp in (
        (0.080, 0.066, 0.013, 0.000),
        (0.078, 0.064, 0.013, 0.055),
        (0.060, 0.050, 0.010, 0.085),
    ):
        loop = [(px, py, zp) for px, py in rounded_rect_profile(vert, lat, rad)]
        head_sections.append(loop)
    head_geom = LoftGeometry(head_sections, cap=True)
    head_geom.rotate_y(math.pi / 2.0)  # loft +Z -> world +X
    head_geom.translate(HEAD_REAR_X, 0.0, HEAD_CENTER_Z)
    body.visual(
        mesh_from_geometry(head_geom, "gear_head"),
        material="housing",
        name="gear_head", material_class_id="plastic.opaque_glossy_molded",
    )

    # Spindle collar boss under the gear head (the spindle exits through it).
    body.visual(
        Cylinder(radius=0.017, length=0.010),
        origin=Origin(xyz=(0.0, 0.0, 0.019)),
        material="housing",
        name="spindle_collar", material_class_id="plastic.opaque_glossy_molded",
    )

    # Recessed black ventilation slots around the front of the motor barrel.
    slot_index = 0
    for slot_x in (-0.048, -0.078):
        for phi in (-1.15, -0.70, 0.70, 1.15):
            body.visual(
                Box((0.026, 0.0045, 0.006)),
                origin=Origin(
                    xyz=(
                        slot_x,
                        -0.0335 * math.sin(phi),
                        MOTOR_AXIS_Z + 0.0335 * math.cos(phi),
                    ),
                    rpy=(phi, 0.0, 0.0),
                ),
                material="trim",
                name=f"vent_slot_{slot_index}", material_class_id="plastic.opaque_generic",
            )
            slot_index += 1

    # Black vent slots on the gear-head front face.
    for j, yoff in enumerate((-0.011, 0.011)):
        body.visual(
            Box((0.003, 0.005, 0.024)),
            origin=Origin(xyz=(0.0345, yoff, HEAD_CENTER_Z)),
            material="trim",
            name=f"head_vent_{j}", material_class_id="plastic.opaque_generic",
        )

    # Black rectangular brand label panel on the housing flank.
    body.visual(
        Box((0.060, 0.0035, 0.024)),
        origin=Origin(xyz=(-0.115, -0.0342, MOTOR_AXIS_Z)),
        material="trim",
        name="brand_label", appearance_only=AppearanceOnlySpec(kind="decal"),
    )

    return body


# ===========================================================================
# spindle_disc (CONTINUOUS) — always present
# ===========================================================================
def _build_spindle_disc(
    model: ArticulatedObject, body: Part, r: ResolvedAngleGrinderConfig
) -> None:
    cutting = r.disc_guard == "cutting_wheel_guard"
    disc_thk = WHEEL_THICKNESS if cutting else 0.0028
    disc_mat = "steel" if cutting else "fiber"
    disc_name = "cutting_wheel" if cutting else "grinding_disc"
    disc_z = -0.0059 if not cutting else -0.0066

    spindle_disc = model.part("spindle_disc")
    spindle_disc.visual(
        Cylinder(radius=0.0055, length=0.016),
        origin=Origin(xyz=(0.0, 0.0, -0.0020)),
        material="steel",
        name="spindle_shaft", material_class_id="metal.steel_bare",
    )
    spindle_disc.visual(
        Cylinder(radius=0.013, length=0.0045),
        origin=Origin(xyz=(0.0, 0.0, -0.00275)),
        material="steel",
        name="backing_flange", material_class_id="metal.steel_bare",
    )
    spindle_disc.visual(
        Cylinder(radius=DISC_RADIUS, length=disc_thk),
        origin=Origin(xyz=(0.0, 0.0, disc_z)),
        material=disc_mat,
        name=disc_name, material_class_id=("metal.steel_bare" if r.disc_guard == "cutting_wheel_guard" else "fabric.open_mesh"),
    )
    nut_geom = CylinderGeometry(radius=0.0085, height=0.005, radial_segments=6)
    nut_geom.translate(0.0, 0.0, disc_z - disc_thk / 2.0 - 0.0025)
    spindle_disc.visual(
        mesh_from_geometry(nut_geom, "clamp_nut"),
        material="steel",
        name="clamp_nut", material_class_id="metal.steel_bare",
    )
    # Off-axis printed label patch embedded into the visible underside of the
    # disc; it gives the rotation test a non-axisymmetric feature to track.
    # Straddle the disc bottom face so the label touches (no island).
    spindle_disc.visual(
        Box((0.016, 0.011, 0.0014)),
        origin=Origin(xyz=(0.030, 0.0, disc_z - disc_thk / 2.0)),
        material="trim",
        name="disc_label", appearance_only=AppearanceOnlySpec(kind="decal"),
    )

    model.articulation(
        "spindle_spin",
        ArticulationType.CONTINUOUS,
        parent=body,
        child=spindle_disc,
        origin=Origin(xyz=(0.0, 0.0, COLLAR_BOTTOM_Z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=6.0, velocity=120.0),
    )


# ===========================================================================
# spindle_lock (PRISMATIC) — always present baseline
# ===========================================================================
def _build_spindle_lock(model: ArticulatedObject, body: Part) -> None:
    spindle_lock = model.part("spindle_lock")
    spindle_lock.visual(
        Cylinder(radius=0.0065, length=0.006),
        origin=Origin(xyz=(0.0, 0.0, 0.0030)),
        material="trim",
        name="lock_cap", material_class_id="plastic.opaque_glossy_molded",
    )
    spindle_lock.visual(
        Cylinder(radius=0.004, length=0.010),
        origin=Origin(xyz=(0.0, 0.0, -0.0040)),
        material="trim",
        name="lock_stem", material_class_id="plastic.opaque_glossy_molded",
    )
    model.articulation(
        "lock_press",
        ArticulationType.PRISMATIC,
        parent=body,
        child=spindle_lock,
        origin=Origin(xyz=(0.0, 0.0, HEAD_TOP_Z)),
        axis=(0.0, 0.0, -1.0),
        motion_limits=MotionLimits(effort=1.0, velocity=0.05, lower=0.0, upper=0.004),
    )


# ===========================================================================
# Slot A: disc-guard
# ===========================================================================
def _half_shroud_guard_shape(
    outer_r: float, inner_r: float, collar_r: float, plate_thk: float,
    shroud_drop: float, clamp_height: float,
):
    """Cadquery half-shroud: tube wall + clamp plate, +X half cut away."""
    shroud_tube = (
        cq.Workplane("XY")
        .circle(outer_r)
        .circle(inner_r)
        .extrude(shroud_drop)
    ).translate((0, 0, -shroud_drop))
    top_plate = (
        cq.Workplane("XY")
        .circle(outer_r)
        .circle(collar_r)
        .extrude(plate_thk + clamp_height)
    ).translate((0, 0, -plate_thk))
    guard_solid = shroud_tube.union(top_plate)
    cutter_height = shroud_drop + clamp_height + 0.02
    cutter_z = (clamp_height - shroud_drop) / 2.0
    cutter = (
        cq.Workplane("XY")
        .box(outer_r * 2, outer_r * 4, cutter_height)
        .translate((outer_r, 0, cutter_z))
    )
    return guard_solid.cut(cutter)


def _build_half_shroud_guard(model: ArticulatedObject, body: Part) -> None:
    guard_outer_r = 0.062
    guard_inner_r = 0.060
    guard_collar_r = 0.0165  # slightly < collar r=0.017 for clamp fit
    guard_plate_thk = 0.002
    guard_shroud_drop = 0.014
    guard_clamp_height = 0.003
    guard_shape = _half_shroud_guard_shape(
        guard_outer_r, guard_inner_r, guard_collar_r,
        guard_plate_thk, guard_shroud_drop, guard_clamp_height,
    )
    guard = model.part("guard")
    guard.visual(
        mesh_from_cadquery(guard_shape, "guard_band"),
        material="steel",
        name="guard_band", material_class_id="metal.steel_bare",
    )
    # Clamp collar ring centered on the spindle axis: it wraps the gear-head
    # collar and gives the revolute joint origin real on-axis hardware to sit
    # on (otherwise the half-shroud has a central hole at the pivot).
    guard.visual(
        Cylinder(radius=0.018, length=guard_plate_thk + guard_clamp_height),
        origin=Origin(xyz=(0.0, 0.0, (guard_clamp_height - guard_plate_thk) / 2.0)),
        material="steel",
        name="guard_clamp_collar", material_class_id="metal.steel_bare",
    )
    model.articulation(
        "guard_to_body",
        ArticulationType.REVOLUTE,
        parent=body,
        child=guard,
        origin=Origin(xyz=(0.0, 0.0, COLLAR_BOTTOM_Z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=2.0, velocity=1.0, lower=-1.0, upper=1.0),
    )


def _arc_wall(inner_r, outer_r, z_top, z_bot, start_rad, end_rad, segments):
    """Partial cylindrical shell with inner and outer surfaces."""
    mesh = MeshGeometry()
    span = end_rad - start_rad
    for i in range(segments + 1):
        t = start_rad + span * i / segments
        c, s = math.cos(t), math.sin(t)
        mesh.add_vertex(outer_r * c, outer_r * s, z_top)
        mesh.add_vertex(outer_r * c, outer_r * s, z_bot)
        mesh.add_vertex(inner_r * c, inner_r * s, z_top)
        mesh.add_vertex(inner_r * c, inner_r * s, z_bot)
    for i in range(segments):
        b = i * 4
        n = b + 4
        mesh.add_face(b, n, n + 1)
        mesh.add_face(b, n + 1, b + 1)
        mesh.add_face(b + 2, b + 3, n + 3)
        mesh.add_face(b + 2, n + 3, n + 2)
    mesh.add_face(0, 2, 3)
    mesh.add_face(0, 3, 1)
    e = segments * 4
    mesh.add_face(e, e + 1, e + 3)
    mesh.add_face(e, e + 3, e + 2)
    return mesh


def _annular_sector(inner_r, outer_r, z_bot, z_top, start_rad, end_rad, segments):
    """Flat annular sector (ring slice) with top, bottom, inner, outer faces."""
    mesh = MeshGeometry()
    span = end_rad - start_rad
    for i in range(segments + 1):
        t = start_rad + span * i / segments
        c, s = math.cos(t), math.sin(t)
        mesh.add_vertex(outer_r * c, outer_r * s, z_top)
        mesh.add_vertex(outer_r * c, outer_r * s, z_bot)
        mesh.add_vertex(inner_r * c, inner_r * s, z_top)
        mesh.add_vertex(inner_r * c, inner_r * s, z_bot)
    for i in range(segments):
        b = i * 4
        n = b + 4
        mesh.add_face(b, n, n + 2)
        mesh.add_face(b, n + 2, b + 2)
        mesh.add_face(b + 1, b + 3, n + 3)
        mesh.add_face(b + 1, n + 3, n + 1)
        mesh.add_face(b, b + 1, n + 1)
        mesh.add_face(b, n + 1, n)
        mesh.add_face(b + 2, n + 2, n + 3)
        mesh.add_face(b + 2, n + 3, b + 3)
    mesh.add_face(0, 2, 3)
    mesh.add_face(0, 3, 1)
    e = segments * 4
    mesh.add_face(e, e + 1, e + 3)
    mesh.add_face(e, e + 3, e + 2)
    return mesh


def _build_cutting_wheel_guard(model: ArticulatedObject, body: Part) -> None:
    GUARD_OUTER_R = 0.064
    GUARD_INNER_R = 0.062
    GUARD_PLATE_INNER_R = 0.020
    GUARD_PLATE_THICKNESS = 0.003
    GUARD_WALL_DEPTH = 0.014
    GUARD_ARC_START = math.radians(35.0)
    GUARD_ARC_END = math.radians(35.0 + 250.0)
    GUARD_ARC_SEGMENTS = 40

    wheel_guard = model.part("wheel_guard")

    # Guard local frame z=0 is the joint origin (world z=COLLAR_BOTTOM_Z). The
    # cutting wheel sits just below the origin; the guard wraps it from above
    # and around, hanging BELOW the gear head (which starts above the origin).
    top_plate_z = -0.003  # plate just above the cutting wheel
    top_plate_mesh = _annular_sector(
        GUARD_PLATE_INNER_R, GUARD_OUTER_R,
        top_plate_z, top_plate_z + GUARD_PLATE_THICKNESS,
        GUARD_ARC_START, GUARD_ARC_END, GUARD_ARC_SEGMENTS,
    )
    wheel_guard.visual(
        mesh_from_geometry(top_plate_mesh, "guard_top_plate"),
        material="trim",
        name="guard_top_plate", material_class_id="metal.paint_coated",
    )

    wall_z_top = top_plate_z + GUARD_PLATE_THICKNESS
    wall_z_bot = top_plate_z - GUARD_WALL_DEPTH
    wall_mesh = _arc_wall(
        GUARD_INNER_R, GUARD_OUTER_R,
        wall_z_top, wall_z_bot,
        GUARD_ARC_START, GUARD_ARC_END, GUARD_ARC_SEGMENTS,
    )
    wheel_guard.visual(
        mesh_from_geometry(wall_mesh, "guard_side_wall"),
        material="trim",
        name="guard_side_wall", material_class_id="metal.paint_coated",
    )

    # Clamp collar centered on the spindle axis: bridges the arc plate to the
    # axis (so the guard is one connected piece) and gives the revolute joint
    # origin real on-axis hardware to sit on. Spans local z=[-0.003,+0.010] so
    # it contains the origin and clamps the body spindle collar above.
    collar_bot = top_plate_z
    collar_top = 0.005  # world z=0.019, below the gear-head bottom (0.020)
    wheel_guard.visual(
        Cylinder(radius=0.021, length=collar_top - collar_bot),
        origin=Origin(xyz=(0.0, 0.0, 0.5 * (collar_bot + collar_top))),
        material="trim",
        name="guard_mount_bracket", material_class_id="metal.paint_coated",
    )

    model.articulation(
        "guard_rotate",
        ArticulationType.REVOLUTE,
        parent=body,
        child=wheel_guard,
        origin=Origin(xyz=(0.0, 0.0, COLLAR_BOTTOM_Z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=3.0, velocity=1.5, lower=-0.5, upper=1.5),
    )


def _build_disc_guard(model: ArticulatedObject, body: Part, r: ResolvedAngleGrinderConfig) -> None:
    if r.disc_guard == "half_shroud_guard":
        _build_half_shroud_guard(model, body)
    elif r.disc_guard == "cutting_wheel_guard":
        _build_cutting_wheel_guard(model, body)
    # bare_disc: no guard part (structural empty).


# ===========================================================================
# Slot B: switch (mutually exclusive)
# ===========================================================================
def _build_top_slide(model: ArticulatedObject, body: Part) -> None:
    power_switch = model.part("power_switch")
    power_switch.visual(
        Box((0.034, 0.0165, 0.006)),
        origin=Origin(xyz=(0.0, 0.0, 0.0010)),
        material="trim",
        name="switch_base", material_class_id="plastic.opaque_glossy_molded",
    )
    power_switch.visual(
        Box((0.022, 0.0145, 0.0055)),
        origin=Origin(xyz=(0.004, 0.0, 0.00625)),
        material="trim",
        name="switch_paddle", material_class_id="plastic.opaque_glossy_molded",
    )
    for k, rib_x in enumerate((-0.002, 0.004, 0.010)):
        power_switch.visual(
            Box((0.0025, 0.013, 0.0014)),
            origin=Origin(xyz=(rib_x, 0.0, 0.0094)),
            material="trim",
            name=f"switch_rib_{k}", material_class_id="plastic.opaque_glossy_molded",
        )
    model.articulation(
        "switch_slide",
        ArticulationType.PRISMATIC,
        parent=body,
        child=power_switch,
        origin=Origin(xyz=(SWITCH_X, 0.0, MOTOR_AXIS_Z + BARREL_RADIUS)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=2.0, velocity=0.05, lower=0.0, upper=0.012),
    )


def _build_deadman_trigger(model: ArticulatedObject, body: Part) -> None:
    trigger_paddle = model.part("trigger_paddle")
    # Pivot boss — cylindrical hinge knuckle at the joint origin.
    trigger_paddle.visual(
        Cylinder(radius=0.007, length=0.022),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="trim",
        name="trigger_boss", material_class_id="plastic.opaque_glossy_molded",
    )
    # Connecting arm bridging the boss to the lever body (overlaps both).
    trigger_paddle.visual(
        Box((0.020, 0.017, 0.008)),
        origin=Origin(xyz=(0.010, 0.0, -0.008)),
        material="trim",
        name="trigger_arm", material_class_id="plastic.opaque_glossy_molded",
    )
    # Main paddle lever — extends forward and downward from the arm.
    trigger_paddle.visual(
        Box((0.048, 0.019, 0.005)),
        origin=Origin(xyz=(0.044, 0.0, -0.014)),
        material="trim",
        name="trigger_lever", material_class_id="plastic.opaque_glossy_molded",
    )
    for i, rib_x in enumerate((0.030, 0.044, 0.058)):
        trigger_paddle.visual(
            Box((0.003, 0.017, 0.002)),
            origin=Origin(xyz=(rib_x, 0.0, -0.0175)),
            material="trim",
            name=f"trigger_rib_{i}", material_class_id="plastic.opaque_glossy_molded",
        )
    model.articulation(
        "trigger_pivot",
        ArticulationType.REVOLUTE,
        parent=body,
        child=trigger_paddle,
        origin=Origin(xyz=(TRIGGER_PIVOT_X, 0.0, MOTOR_AXIS_Z - BARREL_RADIUS + 0.002)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=3.0, velocity=2.0, lower=0.0, upper=0.35),
    )


def _build_top_rocker(model: ArticulatedObject, body: Part) -> None:
    rocker_switch = model.part("rocker_switch")
    rocker_shape = (
        cq.Workplane("XY")
        .box(0.030, 0.015, 0.008)
        .edges("|Z")
        .fillet(0.002)
        .edges("#Z")
        .fillet(0.0012)
    )
    rocker_switch.visual(
        mesh_from_cadquery(rocker_shape, "rocker_body"),
        material="trim",
        name="rocker_body", material_class_id="plastic.opaque_glossy_molded",
    )
    for k, rib_x in enumerate((-0.008, -0.003, 0.002, 0.007)):
        rocker_switch.visual(
            Box((0.002, 0.012, 0.0015)),
            origin=Origin(xyz=(rib_x, 0.0, 0.00455)),
            material="trim",
            name=f"rocker_rib_{k}", material_class_id="plastic.opaque_glossy_molded",
        )
    for k, side in enumerate((-1, 1)):
        rocker_switch.visual(
            Cylinder(radius=0.002, length=0.004),
            origin=Origin(xyz=(0.0, side * 0.0095, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material="trim",
            name=f"rocker_pivot_pin_{k}", material_class_id="metal.blackened_gunmetal",
        )
    model.articulation(
        "rocker_pivot",
        ArticulationType.REVOLUTE,
        parent=body,
        child=rocker_switch,
        origin=Origin(xyz=(SWITCH_X, 0.0, MOTOR_AXIS_Z + BARREL_RADIUS)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=2.0, velocity=1.5, lower=-0.30, upper=0.30),
    )


def _build_switch(model: ArticulatedObject, body: Part, r: ResolvedAngleGrinderConfig) -> None:
    if r.switch == "top_slide":
        _build_top_slide(model, body)
    elif r.switch == "deadman_trigger":
        _build_deadman_trigger(model, body)
    elif r.switch == "top_rocker":
        _build_top_rocker(model, body)


# ===========================================================================
# Slot C: power-source
# ===========================================================================
# Cordless rail interface constants (shared between body visuals and joint).
RAIL_BASE_X = -0.210
RAIL_LENGTH = 0.060
RAIL_BOTTOM_Z = MOTOR_AXIS_Z - 0.027
BATTERY_RELEASE_TRAVEL = 0.055


def _build_corded_tail(body: Part) -> None:
    # Black rubber strain-relief boot and drooping power cord at the rear.
    boot_profile = [
        (0.0, 0.0),
        (0.0095, 0.0),
        (0.0080, 0.018),
        (0.0062, 0.034),
        (0.0, 0.034),
    ]
    boot_geom = LatheGeometry(boot_profile, segments=32)
    boot_geom.rotate_y(-math.pi / 2.0)
    boot_geom.translate(-0.243, 0.0, MOTOR_AXIS_Z)
    body.visual(
        mesh_from_geometry(boot_geom, "cord_boot"),
        material="rubber",
        name="cord_boot", material_class_id="rubber.directional_grooved",
    )
    cord_pts = [
        (-0.270, 0.000, 0.062),
        (-0.300, 0.002, 0.057),
        (-0.330, 0.006, 0.044),
        (-0.352, 0.010, 0.028),
    ]
    cord_geom = tube_from_spline_points(cord_pts, radius=0.0042)
    body.visual(
        mesh_from_geometry(cord_geom, "power_cord"),
        material="rubber",
        name="power_cord", material_class_id="rubber.smooth_plain",
    )


def _build_cordless_rail(body: Part) -> None:
    # Two parallel rail ridges + base plate + rear stop on the grip underside.
    body.visual(
        Box((RAIL_LENGTH, 0.048, 0.004)),
        origin=Origin(xyz=(RAIL_BASE_X, 0.0, RAIL_BOTTOM_Z)),
        material="housing",
        name="rail_baseplate", material_class_id="plastic.opaque_glossy_molded",
    )
    for i, yoff in enumerate((-0.016, 0.016)):
        body.visual(
            Box((RAIL_LENGTH, 0.006, 0.006)),
            origin=Origin(xyz=(RAIL_BASE_X, yoff, RAIL_BOTTOM_Z - 0.005)),
            material="housing",
            name=f"rail_guide_{i}", material_class_id="plastic.opaque_glossy_molded",
        )
    body.visual(
        Box((0.004, 0.048, 0.016)),
        origin=Origin(xyz=(RAIL_BASE_X + RAIL_LENGTH / 2.0 + 0.002, 0.0, RAIL_BOTTOM_Z - 0.006)),
        material="trim",
        name="rail_rear_stop", material_class_id="plastic.opaque_glossy_molded",
    )


def _build_battery_pack(model: ArticulatedObject, body: Part) -> None:
    battery_pack = model.part("battery_pack")
    battery_pack.visual(
        Box((0.072, 0.052, 0.040)),
        origin=Origin(xyz=(-0.005, 0.0, -0.018)),
        material="housing",
        name="battery_shell", material_class_id="plastic.opaque_glossy_molded",
    )
    battery_pack.visual(
        Box((0.065, 0.044, 0.004)),
        origin=Origin(xyz=(0.0, 0.0, 0.002)),
        material="trim",
        name="battery_slide_plate", material_class_id="plastic.opaque_glossy_molded",
    )
    for i, yoff in enumerate((-0.016, 0.016)):
        battery_pack.visual(
            Box((0.060, 0.007, 0.005)),
            origin=Origin(xyz=(0.0, yoff, 0.0065)),
            material="trim",
            name=f"battery_rail_groove_{i}", material_class_id="plastic.opaque_glossy_molded",
        )
    battery_pack.visual(
        Box((0.004, 0.030, 0.014)),
        origin=Origin(xyz=(0.032, 0.0, -0.008)),
        material="trim",
        name="battery_latch", material_class_id="plastic.opaque_glossy_molded",
    )
    for i, yoff in enumerate((-0.010, 0.0, 0.010)):
        battery_pack.visual(
            Box((0.003, 0.006, 0.006)),
            origin=Origin(xyz=(-0.038, yoff, -0.012)),
            material="steel",
            name=f"battery_led_{i}", material_class_id="tech.emissive_surface",
        )
    model.articulation(
        "battery_release",
        ArticulationType.PRISMATIC,
        parent=body,
        child=battery_pack,
        origin=Origin(xyz=(RAIL_BASE_X, 0.0, RAIL_BOTTOM_Z - 0.004)),
        axis=(-1.0, 0.0, 0.0),
        motion_limits=MotionLimits(
            effort=8.0, velocity=0.10, lower=0.0, upper=BATTERY_RELEASE_TRAVEL
        ),
    )


def _build_power_source(model: ArticulatedObject, body: Part, r: ResolvedAngleGrinderConfig) -> None:
    if r.power_source == "corded":
        _build_corded_tail(body)
    else:
        _build_cordless_rail(body)
        _build_battery_pack(model, body)


# ===========================================================================
# Multiplicity: handle bosses (FIXED) — 1..3
# ===========================================================================
# Mount configurations: (joint_origin_xyz, joint_origin_rpy). Local +Z points
# outward from the gear-head mount surface. (Adapted from handle3 record.)
_BOSS_MOUNTS = [
    ((-0.005, FLANK_Y, 0.062), (-math.pi / 2.0, 0.0, 0.0)),   # +Y flank
    ((-0.005, -FLANK_Y, 0.062), (math.pi / 2.0, 0.0, 0.0)),   # -Y flank
    ((-0.020, 0.0, 0.0995), (0.0, 0.0, 0.0)),                 # gear-head top
]


def _add_handle_boss_visuals(boss_part: Part) -> None:
    """Boss cylinder + thread socket along local +Z.

    The boss body extends ~1 mm below the joint plane so it seats into the
    gear-head surface for reliable contact (no phantom anchor).
    """
    boss_part.visual(
        Cylinder(radius=0.011, length=0.018),
        origin=Origin(xyz=(0.0, 0.0, 0.008)),
        material="housing",
        name="boss_body", material_class_id="plastic.opaque_glossy_molded",
    )
    boss_part.visual(
        Cylinder(radius=0.0048, length=0.003),
        origin=Origin(xyz=(0.0, 0.0, 0.0185)),
        material="trim",
        name="boss_socket", material_class_id="metal.blackened_gunmetal",
    )


def _build_handle_bosses(model: ArticulatedObject, body: Part, r: ResolvedAngleGrinderConfig) -> None:
    for i in range(r.handle_boss_count):
        xyz, rpy = _BOSS_MOUNTS[i]
        boss_part = model.part(f"handle_boss_{i}")
        _add_handle_boss_visuals(boss_part)
        # FIXED: a threaded mounting boss does not articulate; it needs its
        # own frame so the +1/-1/top mounts share one geometry helper rotated
        # into place. Body anchors it via the gear-head flank/top contact.
        model.articulation(
            f"boss_mount_{i}",
            ArticulationType.FIXED,
            parent=body,
            child=boss_part,
            origin=Origin(xyz=xyz, rpy=rpy),
        )


# ===========================================================================
# Top-level build
# ===========================================================================
def slot_choices_for_config(r: ResolvedAngleGrinderConfig) -> list[tuple[str, str]]:
    return [
        ("disc_guard", r.disc_guard),
        ("switch", r.switch),
        ("power_source", r.power_source),
        ("handle_boss_count", f"boss_x{r.handle_boss_count}"),
    ]


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    return slot_choices_for_config(resolve_config(config_from_seed(seed)))


def build_angle_grinder(
    config: AngleGrinderConfig, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name="angle_grinder", assets=assets)
    for material, rgba in r.palette.items():
        model.material(material, rgba=rgba)

    body = _build_body(model, r)
    _build_spindle_disc(model, body, r)
    _build_spindle_lock(model, body)
    _build_disc_guard(model, body, r)
    _build_switch(model, body, r)
    _build_power_source(model, body, r)
    _build_handle_bosses(model, body, r)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_angle_grinder(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_angle_grinder(config_from_seed(seed), assets=assets)


# ===========================================================================
# Tests / acceptance
# ===========================================================================
def _declare_overlaps(ctx: TestContext, model: ArticulatedObject, r: ResolvedAngleGrinderConfig) -> None:
    body = model.get_part("body")
    spindle_disc = model.get_part("spindle_disc")
    spindle_lock = model.get_part("spindle_lock")

    ctx.allow_overlap(
        spindle_disc, body,
        elem_a="spindle_shaft", elem_b="spindle_collar",
        reason="The spindle shaft is captured inside the collar boss proxy that stands in for the gear-head bearing bore.",
    )
    ctx.allow_overlap(
        spindle_lock, body,
        elem_a="lock_stem", elem_b="gear_head",
        reason="The lock-button stem is captured inside the gear-head boss that stands in for its guide bore.",
    )

    # Handle bosses seat into the gear-head flank/top surface.
    for i in range(r.handle_boss_count):
        boss = model.get_part(f"handle_boss_{i}")
        ctx.allow_overlap(
            boss, body,
            elem_a="boss_body", elem_b="gear_head",
            reason="The threaded handle boss is seated into the gear-head surface so it reads mounted, not floating.",
        )

    # Slot B switch seating.
    if r.switch == "top_slide":
        power_switch = model.get_part("power_switch")
        ctx.allow_overlap(
            power_switch, body,
            elem_a="switch_base", elem_b="motor_housing",
            reason="The flat switch base plate is seated into the curved barrel top so the control reads mounted.",
        )
    elif r.switch == "deadman_trigger":
        trigger = model.get_part("trigger_paddle")
        ctx.allow_overlap(
            trigger, body,
            elem_a="trigger_boss", elem_b="motor_housing",
            reason="The trigger pivot boss is nested against the housing underside so the hinge reads as a captured pin, not floating.",
        )
    elif r.switch == "top_rocker":
        rocker = model.get_part("rocker_switch")
        ctx.allow_overlap(
            rocker, body,
            elem_a="rocker_body", elem_b="motor_housing",
            reason="The rocker body is seated into the curved barrel crown so the toggle reads mounted, not floating.",
        )

    # Slot A guard clamp wraps the spindle collar.
    if r.disc_guard == "half_shroud_guard":
        guard = model.get_part("guard")
        spindle_disc = model.get_part("spindle_disc")
        ctx.allow_overlap(
            guard, body,
            elem_a="guard_clamp_collar", elem_b="spindle_collar",
            reason="The guard clamp collar wraps around the gear-head spindle collar to represent the clamping fit (intentional interference).",
        )
        ctx.allow_overlap(
            guard, spindle_disc,
            elem_a="guard_clamp_collar", elem_b="spindle_shaft",
            reason="The guard clamp collar wraps the spindle: the spinning shaft passes through its bore (captured pivot).",
        )
    elif r.disc_guard == "cutting_wheel_guard":
        wheel_guard = model.get_part("wheel_guard")
        spindle_disc = model.get_part("spindle_disc")
        ctx.allow_overlap(
            wheel_guard, body,
            elem_a="guard_mount_bracket", elem_b="spindle_collar",
            reason="The guard mounting collar clamps around the gear-head spindle collar (intentional interference).",
        )
        ctx.allow_overlap(
            wheel_guard, spindle_disc,
            elem_a="guard_mount_bracket", elem_b="spindle_shaft",
            reason="The guard clamp collar wraps the spindle: the spinning shaft passes through its bore (captured pivot).",
        )

    # Slot C cordless: battery rail grooves interlock with the body rail guides
    # and nest into the housing/rail proxy geometry.
    if r.power_source == "cordless":
        battery = model.get_part("battery_pack")
        for i in (0, 1):
            ctx.allow_overlap(
                battery, body,
                elem_a=f"battery_rail_groove_{i}", elem_b=f"rail_guide_{i}",
                reason="The battery rail grooves interlock with the body rail guides as a sliding mechanical interface.",
            )
            ctx.allow_overlap(
                battery, body,
                elem_a=f"battery_rail_groove_{i}", elem_b="motor_housing",
                reason="The battery rail grooves nest into the underside of the motor housing where a real T-slot rail would be milled; the lathe housing proxy omits that recess.",
            )
        ctx.allow_overlap(
            battery, body,
            elem_a="battery_shell", elem_b="motor_housing",
            reason="The battery shell seats against the curved underside of the motor housing where a real tool would have a flat recess; the lathe proxy omits it.",
        )
        for i in (0, 1):
            ctx.allow_overlap(
                battery, body,
                elem_a="battery_shell", elem_b=f"rail_guide_{i}",
                reason="The battery shell wraps around the rail guide as part of the slide-on interface; the guide is captured within the pack body.",
            )
        ctx.allow_overlap(
            battery, body,
            elem_a="battery_slide_plate", elem_b="rail_baseplate",
            reason="The battery slide plate rests directly on the rail base plate as the seated sliding interface.",
        )


def run_angle_grinder_tests(
    object_model: ArticulatedObject, config: AngleGrinderConfig
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)

    body = object_model.get_part("body")
    spindle_disc = object_model.get_part("spindle_disc")
    spin = object_model.get_articulation("spindle_spin")

    _declare_overlaps(ctx, object_model, r)

    # --- Identity: disc is continuous, centered, full diameter --------------
    ctx.check(
        "spindle joint is continuous",
        spin.articulation_type == ArticulationType.CONTINUOUS,
        details=f"type={spin.articulation_type}",
    )
    disc_elem = "cutting_wheel" if r.disc_guard == "cutting_wheel_guard" else "grinding_disc"
    disc_aabb = ctx.part_element_world_aabb(spindle_disc, elem=disc_elem)
    if disc_aabb is not None:
        dx = disc_aabb[1][0] - disc_aabb[0][0]
        dy = disc_aabb[1][1] - disc_aabb[0][1]
        cx = 0.5 * (disc_aabb[0][0] + disc_aabb[1][0])
        cy = 0.5 * (disc_aabb[0][1] + disc_aabb[1][1])
        ctx.check(
            "disc diameter is ~0.115 m",
            0.112 <= dx <= 0.118 and 0.112 <= dy <= 0.118,
            details=f"dx={dx:.4f}, dy={dy:.4f}",
        )
        ctx.check(
            "disc is centered on the spindle axis",
            abs(cx) < 0.004 and abs(cy) < 0.004,
            details=f"cx={cx:.4f}, cy={cy:.4f}",
        )
    else:
        ctx.fail("disc element resolves", f"{disc_elem} AABB unavailable")

    # Disc spins about the vertical spindle axis (track the off-axis label).
    label0 = ctx.part_element_world_aabb(spindle_disc, elem="disc_label")
    with ctx.pose({spin: math.pi}):
        label1 = ctx.part_element_world_aabb(spindle_disc, elem="disc_label")
    if label0 is not None and label1 is not None:
        cx0 = 0.5 * (label0[0][0] + label0[1][0])
        cx1 = 0.5 * (label1[0][0] + label1[1][0])
        ctx.check(
            "disc assembly spins about the vertical spindle axis",
            cx0 > 0.02 and cx1 < -0.02,
            details=f"cx0={cx0:.4f}, cx1={cx1:.4f}",
        )
    else:
        ctx.fail("disc label element resolves", "disc_label AABB unavailable")

    # --- spindle_lock baseline ---------------------------------------------
    press = object_model.get_articulation("lock_press")
    ctx.check(
        "lock joint is prismatic",
        press.articulation_type == ArticulationType.PRISMATIC,
        details=f"type={press.articulation_type}",
    )

    # --- Slot A: disc-guard -------------------------------------------------
    if r.disc_guard == "half_shroud_guard":
        guard_joint = object_model.get_articulation("guard_to_body")
        ctx.check(
            "guard joint is revolute about Z",
            guard_joint.articulation_type == ArticulationType.REVOLUTE
            and guard_joint.axis == (0.0, 0.0, 1.0),
            details=f"type={guard_joint.articulation_type}, axis={guard_joint.axis}",
        )
        guard = object_model.get_part("guard")
        g0 = ctx.part_world_aabb(guard)
        with ctx.pose({guard_joint: 0.8}):
            g1 = ctx.part_world_aabb(guard)
        if g0 is not None and g1 is not None:
            ctx.check(
                "guard rotates about the vertical spindle axis",
                abs(g1[0][0] - g0[0][0]) > 0.005,
                details=f"d_minx={g1[0][0] - g0[0][0]:.4f}",
            )
    elif r.disc_guard == "cutting_wheel_guard":
        guard_joint = object_model.get_articulation("guard_rotate")
        ctx.check(
            "cutting-wheel guard joint is revolute about Z",
            guard_joint.articulation_type == ArticulationType.REVOLUTE
            and guard_joint.axis == (0.0, 0.0, 1.0),
            details=f"type={guard_joint.articulation_type}, axis={guard_joint.axis}",
        )
    else:
        # bare_disc: no guard part must exist.
        part_names = {p.name for p in object_model.parts}
        ctx.check(
            "bare disc has no guard part",
            "guard" not in part_names and "wheel_guard" not in part_names,
            details=f"parts={sorted(part_names)}",
        )

    # --- Slot B: switch -----------------------------------------------------
    if r.switch == "top_slide":
        slide = object_model.get_articulation("switch_slide")
        power_switch = object_model.get_part("power_switch")
        ctx.check(
            "slide switch joint is prismatic along the motor axis",
            slide.articulation_type == ArticulationType.PRISMATIC
            and slide.axis == (1.0, 0.0, 0.0),
            details=f"type={slide.articulation_type}, axis={slide.axis}",
        )
        off_pos = ctx.part_world_position(power_switch)
        with ctx.pose({slide: 0.012}):
            on_pos = ctx.part_world_position(power_switch)
        if off_pos is not None and on_pos is not None:
            ctx.check(
                "switch slides forward from OFF to ON",
                abs((on_pos[0] - off_pos[0]) - 0.012) < 1e-6,
                details=f"off={off_pos}, on={on_pos}",
            )
    elif r.switch == "deadman_trigger":
        trig = object_model.get_articulation("trigger_pivot")
        ctx.check(
            "trigger joint is revolute",
            trig.articulation_type == ArticulationType.REVOLUTE,
            details=f"type={trig.articulation_type}",
        )
        lim = trig.motion_limits
        ctx.check(
            "trigger pivot has a realistic squeeze range",
            lim is not None and lim.upper is not None and lim.lower is not None
            and lim.upper - lim.lower > 0.1,
            details=f"limits=({lim.lower},{lim.upper})",
        )
    elif r.switch == "top_rocker":
        rock = object_model.get_articulation("rocker_pivot")
        ctx.check(
            "rocker joint is revolute about Y",
            rock.articulation_type == ArticulationType.REVOLUTE
            and rock.axis == (0.0, 1.0, 0.0),
            details=f"type={rock.articulation_type}, axis={rock.axis}",
        )

    # --- Slot C: power-source ----------------------------------------------
    if r.power_source == "corded":
        cord_aabb = ctx.part_element_world_aabb(body, elem="power_cord")
        ctx.check(
            "power cord exits the rear of the grip",
            cord_aabb is not None and cord_aabb[0][0] <= -0.30,
            details=f"cord_aabb={cord_aabb}",
        )
    else:
        battery = object_model.get_part("battery_pack")
        batt_release = object_model.get_articulation("battery_release")
        ctx.check(
            "battery release is prismatic along the rail",
            batt_release.articulation_type == ArticulationType.PRISMATIC
            and batt_release.axis == (-1.0, 0.0, 0.0),
            details=f"type={batt_release.articulation_type}, axis={batt_release.axis}",
        )
        seated = ctx.part_world_position(battery)
        with ctx.pose({batt_release: BATTERY_RELEASE_TRAVEL}):
            released = ctx.part_world_position(battery)
        if seated is not None and released is not None:
            ctx.check(
                "battery slides backward to release",
                (seated[0] - released[0]) > 0.04,
                details=f"seated={seated}, released={released}",
            )

    # --- Multiplicity: handle bosses ---------------------------------------
    boss_parts = [
        object_model.get_part(f"handle_boss_{i}") for i in range(r.handle_boss_count)
    ]
    ctx.check(
        "expected number of handle bosses exist",
        len(boss_parts) == r.handle_boss_count,
        details=f"count={len(boss_parts)}",
    )
    for i in range(r.handle_boss_count):
        joint = object_model.get_articulation(f"boss_mount_{i}")
        ctx.check(
            f"handle_boss_{i} is FIXED",
            joint.articulation_type == ArticulationType.FIXED,
            details=f"type={joint.articulation_type}",
        )

    # --- Overall proportions ------------------------------------------------
    head_aabb = ctx.part_element_world_aabb(body, elem="gear_head")
    barrel_aabb = ctx.part_element_world_aabb(body, elem="motor_housing")
    if head_aabb is not None and barrel_aabb is not None:
        overall = head_aabb[1][0] - barrel_aabb[0][0]
        ctx.check(
            "tool body is ~0.28 m long overall",
            0.270 <= overall <= 0.292,
            details=f"overall={overall:.4f}",
        )

    return ctx.report()


__all__ = [
    "AngleGrinderConfig",
    "ResolvedAngleGrinderConfig",
    "config_from_seed",
    "resolve_config",
    "build_angle_grinder",
    "build_seeded_angle_grinder",
    "slot_choices_for_seed",
    "slot_choices_for_config",
    "run_angle_grinder_tests",
    "__modular__",
]
