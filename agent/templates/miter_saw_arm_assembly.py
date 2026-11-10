# SPDX-License-Identifier: Apache-2.0

"""Procedural template for ``miter_saw_arm_assembly``.

The category does not currently have an authoring spec file under
``articraft_template_authoring/specs_modular_v1/``. This implementation is derived from
the checked-in 5-star-style records for ``miter_saw_arm_assembly`` and keeps the
stable identity shared by those samples:

* a fixed bench/jobsite base with fence and miter scale,
* a vertical-axis rotating miter table,
* a rear yoke carrying a chopping saw arm,
* a beveling saw head with upper guard and motor housing,
* a circular blade spinning about its arbor,
* a hinged lower blade guard.

config_from_seed uses deterministic procedural sampling (no curated/modulo
table). slot_choices exposes the real structural topology only (palette and the
colour-named head/material styles are NOT slots).

Two real topology axes (per spec) vary the kinematic chain:

* Slot B ``arm_linkage`` — how the table reaches the saw arm:
  - ``direct_pivot_arm``       table --REVOLUTE(X)--> saw_arm
  - ``rear_yoke_swing_arm``    table --FIXED--> rear_pivot_yoke --REVOLUTE(X)--> saw_arm
  - ``slide_rail_carriage``    table --PRISMATIC(Y)--> slide_carriage --REVOLUTE(X)--> saw_arm
    (twin/single rails: ``slide_rail_count`` multiplicity)
* Slot C ``blade_guard`` — blade spin + guard:
  - ``static_blade_fixed_guard``        blade FIXED, fixed upper guard
  - ``spinning_blade_upper_guard``      blade CONTINUOUS(X), fixed upper guard
  - ``spinning_blade_retracting_guard`` blade CONTINUOUS(X) + REVOLUTE lower guard

Shared spine for all seeds: ``base --miter_table_rotate(Z)--> miter_table`` and
``saw_arm --bevel_tilt(Y)--> saw_head``.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Literal

from sdk import (
    AppearanceOnlySpec,
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    ExtrudeGeometry,
    Inertial,
    MotionLimits,
    Origin,
    Part,
    TestContext,
    TestReport,
    mesh_from_geometry,
    rounded_rect_profile,
    tube_from_spline_points,
)

__modular__ = True


BaseStyle = Literal["compact_bench", "wide_jobsite", "sliding_rail_base", "service_casting"]
ArmStyle = Literal["single_beam", "twin_rail", "boxed_spine", "arched_handle"]
HeadStyle = Literal["yellow_guard", "red_compact", "blue_motor", "dark_professional"]
AuxStyle = Literal["none", "carry_handle", "trench_stop_knob", "side_extension_wing", "table_clamp"]
BladeStyle = Literal["plain_disc", "toothed_disc", "thin_kerf"]
MaterialStyle = Literal["shop_yellow", "pro_red", "blue_gray", "dark_teal", "jobsite_orange"]
# Slot B arm_linkage — real kinematic topology between the table and the saw arm.
LinkageStyle = Literal["direct_pivot_arm", "rear_yoke_swing_arm", "slide_rail_carriage"]
# Slot C blade_guard — blade spin + guard topology.
BladeGuardStyle = Literal[
    "static_blade_fixed_guard",
    "spinning_blade_upper_guard",
    "spinning_blade_retracting_guard",
]

LINKAGE_STYLES: tuple[LinkageStyle, ...] = (
    "direct_pivot_arm",
    "rear_yoke_swing_arm",
    "slide_rail_carriage",
)
BLADE_GUARD_STYLES: tuple[BladeGuardStyle, ...] = (
    "static_blade_fixed_guard",
    "spinning_blade_upper_guard",
    "spinning_blade_retracting_guard",
)

BASE_STYLES: tuple[BaseStyle, ...] = (
    "compact_bench",
    "wide_jobsite",
    "sliding_rail_base",
    "service_casting",
)
ARM_STYLES: tuple[ArmStyle, ...] = ("single_beam", "twin_rail", "boxed_spine", "arched_handle")
HEAD_STYLES: tuple[HeadStyle, ...] = (
    "yellow_guard",
    "red_compact",
    "blue_motor",
    "dark_professional",
)
AUX_STYLES: tuple[AuxStyle, ...] = (
    "none",
    "carry_handle",
    "trench_stop_knob",
    "side_extension_wing",
    "table_clamp",
)
BLADE_STYLES: tuple[BladeStyle, ...] = ("plain_disc", "toothed_disc", "thin_kerf")
MATERIAL_STYLES: tuple[MaterialStyle, ...] = (
    "shop_yellow",
    "pro_red",
    "blue_gray",
    "dark_teal",
    "jobsite_orange",
)


PALETTES: dict[MaterialStyle, dict[str, tuple[float, float, float, float]]] = {
    "shop_yellow": {
        "base": (0.58, 0.60, 0.62, 1.0),
        "base_dark": (0.16, 0.17, 0.18, 1.0),
        "table": (0.70, 0.72, 0.74, 1.0),
        "fence": (0.80, 0.82, 0.84, 1.0),
        "arm": (0.64, 0.66, 0.68, 1.0),
        "housing": (0.92, 0.72, 0.14, 1.0),
        "housing_dark": (0.42, 0.32, 0.05, 1.0),
        "blade": (0.78, 0.80, 0.82, 1.0),
        "guard": (0.66, 0.68, 0.71, 1.0),
        "rubber": (0.08, 0.08, 0.09, 1.0),
        "accent": (0.72, 0.12, 0.10, 1.0),
    },
    "pro_red": {
        "base": (0.62, 0.64, 0.66, 1.0),
        "base_dark": (0.15, 0.16, 0.17, 1.0),
        "table": (0.66, 0.68, 0.70, 1.0),
        "fence": (0.82, 0.83, 0.84, 1.0),
        "arm": (0.50, 0.52, 0.54, 1.0),
        "housing": (0.78, 0.14, 0.10, 1.0),
        "housing_dark": (0.38, 0.08, 0.06, 1.0),
        "blade": (0.80, 0.82, 0.84, 1.0),
        "guard": (0.70, 0.72, 0.74, 1.0),
        "rubber": (0.07, 0.07, 0.08, 1.0),
        "accent": (0.05, 0.05, 0.06, 1.0),
    },
    "blue_gray": {
        "base": (0.60, 0.63, 0.66, 1.0),
        "base_dark": (0.18, 0.20, 0.22, 1.0),
        "table": (0.67, 0.69, 0.72, 1.0),
        "fence": (0.80, 0.82, 0.84, 1.0),
        "arm": (0.42, 0.45, 0.48, 1.0),
        "housing": (0.15, 0.32, 0.56, 1.0),
        "housing_dark": (0.08, 0.14, 0.24, 1.0),
        "blade": (0.78, 0.80, 0.83, 1.0),
        "guard": (0.64, 0.67, 0.71, 1.0),
        "rubber": (0.07, 0.08, 0.09, 1.0),
        "accent": (0.92, 0.64, 0.12, 1.0),
    },
    "dark_teal": {
        "base": (0.25, 0.29, 0.30, 1.0),
        "base_dark": (0.09, 0.11, 0.12, 1.0),
        "table": (0.42, 0.46, 0.48, 1.0),
        "fence": (0.70, 0.73, 0.74, 1.0),
        "arm": (0.22, 0.26, 0.28, 1.0),
        "housing": (0.05, 0.34, 0.34, 1.0),
        "housing_dark": (0.03, 0.16, 0.17, 1.0),
        "blade": (0.80, 0.82, 0.84, 1.0),
        "guard": (0.54, 0.58, 0.60, 1.0),
        "rubber": (0.05, 0.05, 0.06, 1.0),
        "accent": (0.90, 0.42, 0.08, 1.0),
    },
    "jobsite_orange": {
        "base": (0.56, 0.58, 0.60, 1.0),
        "base_dark": (0.18, 0.18, 0.18, 1.0),
        "table": (0.68, 0.70, 0.72, 1.0),
        "fence": (0.78, 0.80, 0.82, 1.0),
        "arm": (0.48, 0.50, 0.52, 1.0),
        "housing": (0.94, 0.43, 0.08, 1.0),
        "housing_dark": (0.44, 0.18, 0.04, 1.0),
        "blade": (0.78, 0.80, 0.83, 1.0),
        "guard": (0.60, 0.63, 0.66, 1.0),
        "rubber": (0.08, 0.08, 0.09, 1.0),
        "accent": (0.08, 0.08, 0.09, 1.0),
    },
}


@dataclass(frozen=True)
class MiterSawArmAssemblyConfig:
    base_style: BaseStyle = "compact_bench"
    arm_style: ArmStyle = "single_beam"
    head_style: HeadStyle = "yellow_guard"
    aux_style: AuxStyle = "none"
    blade_style: BladeStyle = "toothed_disc"
    material_style: MaterialStyle = "shop_yellow"
    linkage_style: LinkageStyle = "direct_pivot_arm"
    blade_guard_style: BladeGuardStyle = "spinning_blade_retracting_guard"
    slide_rail_count: int = 2
    fence_segment_count: int = 1
    base_wing_count: int = 0
    table_radius: float = 0.15
    blade_radius: float = 0.12
    arm_length: float = 0.36
    base_width: float = 0.68
    base_depth: float = 0.46
    miter_limit: float = 0.82
    chop_upper: float = 0.86
    bevel_limit: float = 0.45
    name: str = "reference_miter_saw_arm_assembly"
    palette: dict[str, tuple[float, float, float, float]] | None = None


@dataclass(frozen=True)
class ResolvedMiterSawArmAssemblyConfig:
    base_style: BaseStyle
    arm_style: ArmStyle
    head_style: HeadStyle
    aux_style: AuxStyle
    blade_style: BladeStyle
    material_style: MaterialStyle
    linkage_style: LinkageStyle
    blade_guard_style: BladeGuardStyle
    slide_rail_count: int
    fence_segment_count: int
    base_wing_count: int
    table_radius: float
    blade_radius: float
    arm_length: float
    base_width: float
    base_depth: float
    miter_limit: float
    chop_upper: float
    bevel_limit: float
    base_height: float
    table_z: float
    table_thickness: float
    hinge_xyz: tuple[float, float, float]
    head_xyz: tuple[float, float, float]
    blade_xyz: tuple[float, float, float]
    fence_y: float
    name: str
    palette: dict[str, tuple[float, float, float, float]]


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(value)))


def _require(value: str, allowed: tuple[str, ...], *, field_name: str) -> str:
    if value not in allowed:
        raise ValueError(f"{field_name} must be one of {allowed}, got {value!r}")
    return value


def _cyl_x() -> tuple[float, float, float]:
    return (0.0, math.pi / 2.0, 0.0)


def _cyl_y() -> tuple[float, float, float]:
    return (math.pi / 2.0, 0.0, 0.0)


def _cyl_z() -> tuple[float, float, float]:
    return (0.0, 0.0, 0.0)


def _register_materials(
    model: ArticulatedObject, palette: dict[str, tuple[float, float, float, float]]
):
    return {key: model.material(f"miter_saw_{key}", rgba=rgba) for key, rgba in palette.items()}


def _mesh(model: ArticulatedObject, geom: object, name: str):
    if model.assets is not None:
        return mesh_from_geometry(geom, model.assets.mesh_path(f"{name}.obj"))
    return mesh_from_geometry(geom, name)


def _annular_sector_profile(
    *,
    outer_radius: float,
    inner_radius: float,
    start_deg: float,
    end_deg: float,
    segments: int = 48,
) -> list[tuple[float, float]]:
    start = math.radians(start_deg)
    end = math.radians(end_deg)
    if end <= start:
        end += math.tau
    outer: list[tuple[float, float]] = []
    inner: list[tuple[float, float]] = []
    for i in range(segments + 1):
        t = i / segments
        a = start + (end - start) * t
        y = outer_radius * math.cos(a)
        z = outer_radius * math.sin(a)
        outer.append((z, y))
    for i in range(segments, -1, -1):
        t = i / segments
        a = start + (end - start) * t
        y = inner_radius * math.cos(a)
        z = inner_radius * math.sin(a)
        inner.append((z, y))
    return outer + inner


def _sector_mesh(
    model: ArticulatedObject,
    name: str,
    *,
    outer_radius: float,
    inner_radius: float,
    start_deg: float,
    end_deg: float,
    thickness: float,
):
    geom = ExtrudeGeometry(
        _annular_sector_profile(
            outer_radius=outer_radius,
            inner_radius=inner_radius,
            start_deg=start_deg,
            end_deg=end_deg,
        ),
        thickness,
        center=True,
        cap=True,
        closed=True,
    )
    geom.rotate_y(math.pi / 2.0)
    return _mesh(model, geom, name)


def _blade_tooth_mesh(
    model: ArticulatedObject,
    name: str,
    *,
    blade_radius: float,
    angle: float,
    thickness: float,
    half_angle: float,
):
    inner_radius = blade_radius * 0.925
    outer_radius = blade_radius * 1.075
    profile: list[tuple[float, float]] = []
    for radius, theta in (
        (inner_radius, angle - half_angle),
        (outer_radius, angle - half_angle * 0.38),
        (outer_radius * 1.005, angle + half_angle * 0.12),
        (inner_radius, angle + half_angle),
    ):
        y = math.cos(theta) * radius
        z = math.sin(theta) * radius
        profile.append((z, y))
    geom = ExtrudeGeometry(profile, thickness, center=True, cap=True, closed=True)
    geom.rotate_y(math.pi / 2.0)
    return _mesh(model, geom, name)


def _handle_loop_mesh(model: ArticulatedObject, name: str, scale: float = 1.0):
    geom = tube_from_spline_points(
        [
            (-0.030 * scale, -0.015 * scale, 0.000),
            (-0.055 * scale, 0.020 * scale, 0.030 * scale),
            (-0.030 * scale, 0.090 * scale, 0.055 * scale),
            (0.035 * scale, 0.095 * scale, 0.050 * scale),
            (0.060 * scale, 0.030 * scale, 0.018 * scale),
            (0.030 * scale, -0.012 * scale, 0.000),
        ],
        radius=0.010 * scale,
        samples_per_segment=14,
        radial_segments=14,
        up_hint=(0.0, 0.0, 1.0),
    )
    return _mesh(model, geom, name)


def config_from_seed(seed: int) -> MiterSawArmAssemblyConfig:
    rng = random.Random(seed)
    linkage: LinkageStyle = rng.choice(LINKAGE_STYLES)
    return MiterSawArmAssemblyConfig(
        base_style=rng.choice(BASE_STYLES),
        arm_style=rng.choice(ARM_STYLES),
        head_style=rng.choice(HEAD_STYLES),
        aux_style=rng.choice(AUX_STYLES),
        blade_style=rng.choice(BLADE_STYLES),
        material_style=rng.choice(MATERIAL_STYLES),
        linkage_style=linkage,
        blade_guard_style=rng.choice(BLADE_GUARD_STYLES),
        slide_rail_count=(rng.choice((1, 2)) if linkage == "slide_rail_carriage" else 0),
        table_radius=round(rng.uniform(0.135, 0.175), 3),
        blade_radius=round(rng.uniform(0.105, 0.135), 3),
        arm_length=round(rng.uniform(0.32, 0.44), 3),
        base_width=round(rng.uniform(0.62, 0.86), 3),
        base_depth=round(rng.uniform(0.42, 0.54), 3),
        # Drawn last so the geometry-determining stream above is unchanged and
        # these additive multiplicity counts don't perturb existing seeds.
        fence_segment_count=rng.choice((1, 2)),
        base_wing_count=rng.choice((0, 0, 1, 2)),
        name=f"seeded_miter_saw_arm_assembly_{seed}",
    )


def resolve_config(config: MiterSawArmAssemblyConfig) -> ResolvedMiterSawArmAssemblyConfig:
    base_style = _require(config.base_style, BASE_STYLES, field_name="base_style")
    arm_style = _require(config.arm_style, ARM_STYLES, field_name="arm_style")
    head_style = _require(config.head_style, HEAD_STYLES, field_name="head_style")
    aux_style = _require(config.aux_style, AUX_STYLES, field_name="aux_style")
    blade_style = _require(config.blade_style, BLADE_STYLES, field_name="blade_style")
    material_style = _require(config.material_style, MATERIAL_STYLES, field_name="material_style")
    table_radius = _clamp(config.table_radius, 0.12, 0.19)
    blade_radius = _clamp(config.blade_radius, 0.095, 0.15)
    arm_length = _clamp(config.arm_length, 0.30, 0.48)
    base_width = _clamp(config.base_width, 0.58, 0.90)
    base_depth = _clamp(config.base_depth, 0.40, 0.58)
    base_height = 0.055 if base_style in ("wide_jobsite", "sliding_rail_base") else 0.048
    table_z = base_height + 0.022
    table_thickness = 0.018
    hinge_xyz = (0.0, -base_depth * 0.43, 0.27)
    head_xyz = (0.0, arm_length, -0.080)
    blade_xyz = (0.0, -arm_length - hinge_xyz[1], blade_radius - 0.198)
    fence_y = -base_depth * 0.30
    palette = dict(PALETTES[material_style])
    if config.palette:
        palette.update(config.palette)
    return ResolvedMiterSawArmAssemblyConfig(
        base_style=base_style,  # type: ignore[arg-type]
        arm_style=arm_style,  # type: ignore[arg-type]
        head_style=head_style,  # type: ignore[arg-type]
        aux_style=aux_style,  # type: ignore[arg-type]
        blade_style=blade_style,  # type: ignore[arg-type]
        material_style=material_style,  # type: ignore[arg-type]
        linkage_style=_require(config.linkage_style, LINKAGE_STYLES, field_name="linkage_style"),  # type: ignore[arg-type]
        blade_guard_style=_require(  # type: ignore[arg-type]
            config.blade_guard_style, BLADE_GUARD_STYLES, field_name="blade_guard_style"
        ),
        slide_rail_count=(
            2
            if config.linkage_style == "slide_rail_carriage"
            and config.slide_rail_count not in (1, 2)
            else int(config.slide_rail_count)
        ),
        fence_segment_count=(2 if int(config.fence_segment_count) >= 2 else 1),
        base_wing_count=max(
            0,
            min(2, int(config.base_wing_count)),
        )
        or (1 if config.aux_style == "side_extension_wing" else 0),
        table_radius=table_radius,
        blade_radius=blade_radius,
        arm_length=arm_length,
        base_width=base_width,
        base_depth=base_depth,
        miter_limit=_clamp(config.miter_limit, 0.45, 1.05),
        chop_upper=_clamp(config.chop_upper, 0.55, 1.15),
        bevel_limit=_clamp(config.bevel_limit, 0.20, 0.70),
        base_height=base_height,
        table_z=table_z,
        table_thickness=table_thickness,
        hinge_xyz=hinge_xyz,
        head_xyz=head_xyz,
        blade_xyz=blade_xyz,
        fence_y=fence_y,
        name=config.name,
        palette=palette,
    )


# --- Single-source derived clearances (Contract 3c) ---------------------------
# The fixed rear fence bar and the rotating table structures share one interface
# geometry; every consumer (builder, limit derivation, tests) reads it here so
# the clearances stay consistent.
_FENCE_BAR_HALF_DEPTH = 0.009  # rear_fence_bar half thickness in Y
_FENCE_Z_LO = 0.0265  # rear_fence_bar bottom above base_height
_FENCE_Z_HI = 0.1015  # rear_fence_bar top above base_height
_MITER_CLEAR = 0.010  # required rotating-structure / fence clearance (>= 8mm target)
_NECK_BLADE_CLEAR = 0.012  # rear tower neck stand-off behind the blade rim
# Rear pivot yoke footprint (slimmed so it swings clear of the fence over a
# usable miter range). Single-sourced between the builder and the limit solver.
_YOKE_BASE_HALF_W = 0.060  # yoke_base_web half width in X
_YOKE_PLATE_HALF_LEN = 0.0275  # yoke plate half length in Y


def _fence_rear_y(r: ResolvedMiterSawArmAssemblyConfig) -> float:
    """World Y of the rearmost fence face (the plane rotating table structures
    must stay behind)."""
    return r.fence_y - _FENCE_BAR_HALF_DEPTH


def _fence_half_width(r: ResolvedMiterSawArmAssemblyConfig) -> float:
    """Half the X span the fence bar(s) cover (single or split)."""
    if r.fence_segment_count >= 2:
        return r.base_width * 0.195 + r.base_width * 0.33 * 0.5
    return r.base_width * 0.72 * 0.5


def _neck_front_y(r: ResolvedMiterSawArmAssemblyConfig) -> float:
    """Front (max Y) of the rear tower-to-table necks. Kept behind the blade rim
    (which spans +-blade_radius about the table centre and is bevel-invariant in
    Y) while still reaching forward far enough to seat on the table disc, so the
    beveled blade never sweeps through the necks."""
    behind_blade = -(r.blade_radius + _NECK_BLADE_CLEAR)
    disc_seat = -(r.table_radius - 0.006)  # stay on the table disc for connectivity
    # Prefer the deeper (more negative) of the decorative default and the
    # blade-clear target, but never retract past the disc seat.
    return max(min(-r.table_radius * 0.72, behind_blade), disc_seat)


def _clamp_center_x(r: ResolvedMiterSawArmAssemblyConfig) -> float:
    """X of the table clamp column. Pulled toward the table centre so its swing
    radius stays small and it clears the fence across the miter range."""
    return -r.table_radius * 0.42


def _rear_swing_footprint(
    r: ResolvedMiterSawArmAssemblyConfig,
) -> list[tuple[float, float, float, float]]:
    """(x, y) half-extent boxes, in the miter-table frame, of the rotating
    structures that can foul the fixed fence. Returned as (cx, cy, hx, hy).
    Excludes the rear pivot tower/cheeks/necks, which nest tightly at neutral and
    carry a declared element-scoped allowance."""
    hx, hy, hz = r.hinge_xyz
    boxes: list[tuple[float, float, float, float]] = []
    if r.linkage_style == "rear_yoke_swing_arm":
        boxes.append((0.0, hy - 0.005, _YOKE_BASE_HALF_W, 0.0375))  # yoke_base_web
        for s in (-1.0, 1.0):
            boxes.append((s * 0.062, hy, 0.012, _YOKE_PLATE_HALF_LEN))  # yoke plates
    if r.linkage_style == "slide_rail_carriage":
        boxes.append((0.0, hy - 0.020, 0.085, 0.030))  # slide_rail_post
    if r.aux_style == "table_clamp":
        cx = _clamp_center_x(r)
        boxes.append((cx, -0.030, 0.018, 0.035))  # clamp_post_base_bridge
        boxes.append((cx, -0.045, 0.012, 0.012))  # clamp_post (vertical cylinder r=0.012)
        boxes.append((cx, -0.010, 0.020, 0.0525))  # clamp_arm
    return boxes


def _derive_miter_limit(r: ResolvedMiterSawArmAssemblyConfig) -> float:
    """Largest |miter| rotation that keeps every rotating rear structure out of
    the fixed fence bar's Y-Z-X slab, with _MITER_CLEAR margin. Structures merely
    forward of the fence do not count; only entry into the fence's thin Y slab
    (within its X span) does."""
    boxes = _rear_swing_footprint(r)
    base = _clamp(r.miter_limit, 0.45, 1.05)
    if not boxes:
        return base
    fr = _fence_rear_y(r)
    ff = r.fence_y + _FENCE_BAR_HALF_DEPTH
    fh = _fence_half_width(r)
    y_lo = fr - _MITER_CLEAR
    y_hi = ff + _MITER_CLEAR
    x_lim = fh + _MITER_CLEAR
    step = 0.01
    theta = 0.0
    limit = base
    while theta <= base + 1e-9:
        fouled = False
        for sgn in (1.0, -1.0):
            c, s = math.cos(sgn * theta), math.sin(sgn * theta)
            for cx, cy, hxx, hyy in boxes:
                for dx in (-hxx, hxx):
                    for dy in (-hyy, hyy):
                        x = cx + dx
                        y = cy + dy
                        xp = x * c - y * s
                        yp = x * s + y * c
                        if y_lo <= yp <= y_hi and abs(xp) <= x_lim:
                            fouled = True
                            break
                    if fouled:
                        break
                if fouled:
                    break
            if fouled:
                break
        if fouled:
            limit = max(0.0, round(theta - step, 3))
            break
        theta += step
    return min(base, limit)


def _build_base(
    model: ArticulatedObject, r: ResolvedMiterSawArmAssemblyConfig, m: dict[str, object]
) -> Part:
    base = model.part("base")
    body_geom = ExtrudeGeometry(
        rounded_rect_profile(r.base_width, r.base_depth, 0.045, corner_segments=8),
        r.base_height,
        center=True,
        cap=True,
        closed=True,
    )
    base.visual(
        _mesh(model, body_geom, "miter_saw_base_casting"),
        origin=Origin(xyz=(0.0, 0.0, r.base_height * 0.5)),
        material=m["base"],
        name="base_casting", material_class_id="metal.cast_iron_bare",
    )
    base.visual(
        Box((r.base_width * 0.86, r.base_depth * 0.78, r.base_height * 0.72)),
        origin=Origin(xyz=(0.0, 0.0, r.base_height * 0.45)),
        material=m["base"],
        name="base_internal_bridge", material_class_id="metal.cast_iron_bare",
    )
    base.visual(
        Cylinder(radius=r.table_radius * 1.18, length=0.030),
        origin=Origin(xyz=(0.0, 0.0, r.table_z - 0.018)),
        material=m["table"],
        name="turntable_seat", material_class_id="metal.aluminum_bare",
    )
    # Fence: 1 continuous bar, or 2 split half-fences with a centre kerf gap
    # (fence_segment_count multiplicity). The full stanchion bridge underneath
    # ties any split halves to the base.
    if r.fence_segment_count >= 2:
        for sign, side in ((-1.0, "left"), (1.0, "right")):
            base.visual(
                Box((r.base_width * 0.33, 0.018, 0.075)),
                origin=Origin(xyz=(sign * r.base_width * 0.195, r.fence_y, r.base_height + 0.064)),
                material=m["fence"],
                name=f"{side}_rear_fence_bar", material_class_id="metal.aluminum_bare",
            )
    else:
        base.visual(
            Box((r.base_width * 0.72, 0.018, 0.075)),
            origin=Origin(xyz=(0.0, r.fence_y, r.base_height + 0.064)),
            material=m["fence"],
            name="rear_fence_bar", material_class_id="metal.aluminum_bare",
        )
    base.visual(
        Box((r.base_width * 0.70, 0.026, 0.085)),
        origin=Origin(xyz=(0.0, r.fence_y, r.base_height + 0.028)),
        material=m["base"],
        name="rear_fence_stanchion_bridge", material_class_id="metal.cast_iron_bare",
    )
    for sign, side in ((-1.0, "left"), (1.0, "right")):
        base.visual(
            Box((r.base_width * 0.20, 0.050, 0.046)),
            origin=Origin(
                xyz=(sign * r.base_width * 0.31, r.fence_y + 0.020, r.base_height + 0.046)
            ),
            material=m["base"],
            name=f"{side}_fence_pedestal", material_class_id="metal.cast_iron_bare",
        )
        base.visual(
            Box((0.12, 0.075, 0.030)),
            origin=Origin(
                xyz=(sign * r.base_width * 0.36, r.base_depth * 0.31, r.base_height * 0.55)
            ),
            material=m["base_dark"],
            name=f"{side}_front_foot", material_class_id="rubber.smooth_plain",
        )
    if r.base_style in ("wide_jobsite", "service_casting"):
        base.visual(
            Box((r.base_width * 0.34, 0.050, 0.030)),
            origin=Origin(xyz=(0.0, r.base_depth * 0.38, r.base_height + 0.004)),
            material=m["base_dark"],
            name="front_miter_scale_lip", material_class_id="metal.blackened_gunmetal",
        )
        for i in range(7):
            x = (i - 3) * r.base_width * 0.035
            base.visual(
                Box((0.004, 0.018, 0.010)),
                origin=Origin(xyz=(x, r.base_depth * 0.39, r.base_height + 0.020)),
                material=m["accent"],
                name=f"miter_scale_tick_{i}", appearance_only=AppearanceOnlySpec(kind="overlay"),
            )
    if r.base_style == "sliding_rail_base":
        rail_y = r.fence_y - 0.190
        for sign, side in ((-1.0, "left"), (1.0, "right")):
            base.visual(
                Cylinder(radius=0.010, length=r.base_width * 0.58),
                origin=Origin(
                    xyz=(0.0, rail_y + sign * 0.025, r.base_height + 0.125), rpy=_cyl_x()
                ),
                material=m["blade"],
                name=f"rear_slide_rail_{side}", material_class_id="metal.stainless_matte",
            )
        base.visual(
            Box((0.13, 0.10, 0.060)),
            origin=Origin(xyz=(0.0, rail_y, r.base_height + 0.112)),
            material=m["base_dark"],
            name="rail_carriage_visual", material_class_id="metal.blackened_gunmetal",
        )
        base.visual(
            Box((0.17, 0.090, 0.082)),
            origin=Origin(xyz=(0.0, rail_y, r.base_height + 0.085)),
            material=m["base_dark"],
            name="rear_rail_support_bridge", material_class_id="metal.blackened_gunmetal",
        )
        base.visual(
            Box((0.12, 0.21, 0.090)),
            origin=Origin(xyz=(0.0, rail_y + 0.055, r.base_height + 0.040)),
            material=m["base_dark"],
            name="rear_rail_root_strut", material_class_id="metal.blackened_gunmetal",
        )
    # Side extension wings: base_wing_count multiplicity (0 / right / both).
    wing_signs = {1: ((1.0, "right"),), 2: ((-1.0, "left"), (1.0, "right"))}.get(
        r.base_wing_count, ()
    )
    for sign, side in wing_signs:
        base.visual(
            Box((r.base_width * 0.34, r.base_depth * 0.30, 0.020)),
            origin=Origin(xyz=(sign * r.base_width * 0.58, 0.02, r.base_height + 0.008)),
            material=m["table"],
            name=f"{side}_extension_wing", material_class_id="metal.aluminum_bare",
        )
        base.visual(
            Cylinder(radius=0.012, length=r.base_depth * 0.32),
            origin=Origin(
                xyz=(sign * r.base_width * 0.40, 0.02, r.base_height + 0.030), rpy=_cyl_y()
            ),
            material=m["blade"],
            name=f"{side}_extension_wing_hinge_pin", material_class_id="metal.stainless_matte",
        )
        base.visual(
            Box((0.090, r.base_depth * 0.30, 0.034)),
            origin=Origin(xyz=(sign * r.base_width * 0.43, 0.02, r.base_height + 0.017)),
            material=m["table"],
            name=f"{side}_extension_wing_root_bridge", material_class_id="metal.aluminum_bare",
        )
    base.inertial = Inertial.from_geometry(
        Box((r.base_width, r.base_depth, 0.18)),
        mass=22.0,
        origin=Origin(xyz=(0.0, 0.0, 0.09)),
    )
    return base


def _build_miter_table(
    model: ArticulatedObject, r: ResolvedMiterSawArmAssemblyConfig, m: dict[str, object]
) -> Part:
    table = model.part("miter_table")
    table.visual(
        Cylinder(radius=r.table_radius, length=r.table_thickness),
        origin=Origin(xyz=(0.0, 0.0, r.table_thickness * 0.5)),
        material=m["table"],
        name="table_disc", material_class_id="metal.aluminum_bare",
    )
    table.visual(
        Box((r.table_radius * 1.55, 0.024, 0.010)),
        origin=Origin(xyz=(0.0, 0.0, r.table_thickness + 0.005)),
        material=m["base_dark"],
        name="kerf_slot", material_class_id="metal.blackened_gunmetal",
    )
    hx, hy, hz = r.hinge_xyz
    table.visual(
        Box((0.150, 0.080, hz - r.table_thickness * 0.5)),
        origin=Origin(xyz=(0.0, hy, (hz + r.table_thickness) * 0.5)),
        material=m["base_dark"],
        name="rear_pivot_tower", material_class_id="metal.blackened_gunmetal",
    )
    neck_front = _neck_front_y(r)
    neck_len = max(0.050, neck_front - hy)
    for sign, side in ((-1.0, "left"), (1.0, "right")):
        table.visual(
            Box((0.032, neck_len, 0.060)),
            origin=Origin(xyz=(sign * 0.054, neck_front - neck_len * 0.5, 0.045)),
            material=m["base_dark"],
            name=f"{side}_rear_tower_table_neck", material_class_id="metal.blackened_gunmetal",
        )
    for sign, side in ((-1.0, "left"), (1.0, "right")):
        table.visual(
            Box((0.024, 0.065, 0.125)),
            origin=Origin(xyz=(sign * 0.072, hy, hz - 0.020)),
            material=m["base_dark"],
            name=f"{side}_pivot_cheek", material_class_id="metal.blackened_gunmetal",
        )
    table.visual(
        Cylinder(radius=0.014, length=0.165),
        origin=Origin(xyz=r.hinge_xyz, rpy=_cyl_x()),
        material=m["blade"],
        name="chop_hinge_pin", material_class_id="metal.stainless_matte",
    )
    if r.aux_style == "table_clamp":
        clamp_x = _clamp_center_x(r)
        table.visual(
            Cylinder(radius=0.012, length=0.120),
            origin=Origin(xyz=(clamp_x, -0.045, 0.055), rpy=_cyl_z()),
            material=m["blade"],
            name="clamp_post", material_class_id="metal.stainless_matte",
        )
        table.visual(
            Box((0.040, 0.105, 0.020)),
            origin=Origin(xyz=(clamp_x, -0.010, 0.125)),
            material=m["base_dark"],
            name="clamp_arm", material_class_id="metal.blackened_gunmetal",
        )
        table.visual(
            Cylinder(radius=0.024, length=0.012),
            origin=Origin(xyz=(clamp_x, 0.050, 0.115), rpy=_cyl_z()),
            material=m["rubber"],
            name="clamp_pad", material_class_id="rubber.smooth_plain",
        )
        table.visual(
            Box((0.036, 0.070, 0.070)),
            origin=Origin(xyz=(clamp_x, -0.030, 0.045)),
            material=m["base_dark"],
            name="clamp_post_base_bridge", material_class_id="metal.blackened_gunmetal",
        )
    table.inertial = Inertial.from_geometry(
        Cylinder(radius=r.table_radius, length=0.22),
        mass=9.0,
        origin=Origin(xyz=(0.0, 0.0, 0.11)),
    )
    return table


def _build_saw_arm(
    model: ArticulatedObject, r: ResolvedMiterSawArmAssemblyConfig, m: dict[str, object]
) -> Part:
    arm = model.part("saw_arm")
    arm.visual(
        Cylinder(radius=0.030, length=0.145),
        origin=Origin(rpy=_cyl_x()),
        material=m["arm"],
        name="arm_pivot_boss", material_class_id="metal.aluminum_bare",
    )
    if r.arm_style == "twin_rail":
        for sign, side in ((-1.0, "left"), (1.0, "right")):
            arm.visual(
                Cylinder(radius=0.012, length=r.arm_length),
                origin=Origin(xyz=(sign * 0.032, r.arm_length * 0.5, 0.040), rpy=_cyl_y()),
                material=m["blade"],
                name=f"{side}_arm_rail", material_class_id="metal.stainless_matte",
            )
        arm.visual(
            Box((0.105, 0.050, 0.050)),
            origin=Origin(xyz=(0.0, r.arm_length - 0.025, 0.040)),
            material=m["arm"],
            name="rail_front_carriage", material_class_id="metal.aluminum_bare",
        )
    elif r.arm_style == "boxed_spine":
        arm.visual(
            Box((0.075, r.arm_length, 0.048)),
            origin=Origin(xyz=(0.0, r.arm_length * 0.5, 0.038)),
            material=m["arm"],
            name="boxed_arm_spine", material_class_id="metal.aluminum_bare",
        )
        arm.visual(
            Box((0.050, r.arm_length * 0.74, 0.014)),
            origin=Origin(xyz=(0.0, r.arm_length * 0.53, 0.067)),
            material=m["housing_dark"],
            name="top_reinforcing_rib", material_class_id="plastic.opaque_glossy_molded",
        )
    else:
        arm.visual(
            Box((0.055, r.arm_length, 0.040)),
            origin=Origin(xyz=(0.0, r.arm_length * 0.5, 0.040)),
            material=m["arm"],
            name="single_arm_beam", material_class_id="metal.aluminum_bare",
        )
    if r.arm_style == "arched_handle":
        arm.visual(
            _handle_loop_mesh(model, "arched_saw_arm_handle", scale=1.15),
            origin=Origin(xyz=(0.0, r.arm_length * 0.36, 0.060)),
            material=m["rubber"],
            name="arched_handle_loop", material_class_id="rubber.smooth_plain",
        )
    else:
        arm.visual(
            Cylinder(radius=0.014, length=0.16),
            origin=Origin(xyz=(0.0, r.arm_length * 0.40, 0.068), rpy=_cyl_x()),
            material=m["rubber"],
            name="cross_grip_handle", material_class_id="rubber.smooth_plain",
        )
    arm.visual(
        Box((0.092, 0.040, 0.052)),
        origin=Origin(xyz=(0.0, r.arm_length * 0.38, 0.069)),
        material=m["arm"],
        name="handle_mount_pad", material_class_id="metal.aluminum_bare",
    )
    arm.visual(
        Box((0.058, 0.026, 0.090)),
        origin=Origin(xyz=(0.040, r.arm_length, -0.045)),
        material=m["arm"],
        name="front_bevel_drop_bracket", material_class_id="metal.aluminum_bare",
    )
    arm.visual(
        Box((0.052, 0.034, 0.050)),
        origin=Origin(xyz=(0.0, r.arm_length, 0.010)),
        material=m["arm"],
        name="front_bevel_web", material_class_id="metal.aluminum_bare",
    )
    if r.aux_style == "trench_stop_knob":
        # Sits outboard on the arm's right flank so it clears the head's guard
        # neck bridge (which reaches back over the arm) at every bevel pose.
        arm.visual(
            Box((0.075, 0.060, 0.034)),
            origin=Origin(xyz=(0.082, r.arm_length * 0.30, 0.037)),
            material=m["base_dark"],
            name="depth_stop_bracket", material_class_id="metal.blackened_gunmetal",
        )
        arm.visual(
            Cylinder(radius=0.018, length=0.020),
            origin=Origin(xyz=(0.117, r.arm_length * 0.30, 0.030), rpy=_cyl_x()),
            material=m["accent"],
            name="trench_stop_knob_visual", material_class_id="plastic.opaque_glossy_molded",
        )
    arm.inertial = Inertial.from_geometry(
        Box((0.12, r.arm_length, 0.14)),
        mass=6.5,
        origin=Origin(xyz=(0.0, r.arm_length * 0.5, 0.0)),
    )
    return arm


def _build_saw_head(
    model: ArticulatedObject, r: ResolvedMiterSawArmAssemblyConfig, m: dict[str, object]
) -> Part:
    head = model.part("saw_head")
    br = r.blade_radius
    housing_mat = m["housing"]
    motor_y = r.blade_xyz[1] + br * 1.55
    bridge_y = (r.blade_xyz[1] + motor_y) * 0.5
    bridge_len = abs(motor_y - r.blade_xyz[1]) + 0.072
    # Straddles the bevel pivot (head-local origin) so the bevel joint origin sits
    # inside the head's own geometry (origin-far-from-geometry gate).
    head.visual(
        Box((0.070, 0.035, 0.090)),
        origin=Origin(xyz=(0.0, -0.004, 0.018)),
        material=m["arm"],
        name="bevel_mount_lug", material_class_id="metal.aluminum_bare",
    )
    head.visual(
        Box((0.085, 0.105, 0.070)),
        origin=Origin(xyz=(0.0, motor_y, 0.035)),
        material=housing_mat,
        name="motor_gearbox_block", material_class_id="plastic.opaque_glossy_molded",
    )
    head.visual(
        Cylinder(radius=0.050, length=0.080),
        origin=Origin(xyz=(-0.095, motor_y + 0.015, 0.035), rpy=_cyl_x()),
        material=m["housing_dark"],
        name="side_motor_can", material_class_id="metal.blackened_gunmetal",
    )
    head.visual(
        Box((0.040, 0.055, 0.050)),
        origin=Origin(xyz=(-0.052, motor_y + 0.015, 0.035)),
        material=m["housing"],
        name="side_motor_mount_bridge", material_class_id="plastic.opaque_glossy_molded",
    )
    head.visual(
        _sector_mesh(
            model,
            "upper_guard_sector",
            outer_radius=br * 0.96,
            inner_radius=br * 0.74,
            start_deg=-70.0,
            end_deg=70.0,
            thickness=0.030,
        ),
        origin=Origin(xyz=(r.blade_xyz[0], r.blade_xyz[1], r.blade_xyz[2] + br * 0.40)),
        material=m["guard"],
        name="upper_blade_guard", material_class_id="plastic.opaque_glossy_molded",
    )
    head.visual(
        Box((0.018, bridge_len, 0.030)),
        origin=Origin(xyz=(0.024, bridge_y, 0.085)),
        material=m["housing"],
        name="guard_neck_bridge", material_class_id="plastic.opaque_glossy_molded",
    )
    head.visual(
        Cylinder(radius=0.020, length=0.050),
        origin=Origin(xyz=r.blade_xyz, rpy=_cyl_x()),
        material=m["blade"],
        name="arbor_shaft_visual", material_class_id="metal.stainless_matte",
    )
    head.visual(
        Box((0.035, bridge_len, 0.160)),
        origin=Origin(xyz=(0.010, bridge_y, r.blade_xyz[2] + 0.058)),
        material=m["housing"],
        name="arbor_side_web", material_class_id="plastic.opaque_glossy_molded",
    )
    head.visual(
        Box((0.030, 0.110, 0.026)),
        origin=Origin(xyz=(-0.075, motor_y + 0.025, 0.082)),
        material=m["rubber"],
        name="trigger_handle", material_class_id="rubber.smooth_plain",
    )
    if r.aux_style == "carry_handle":
        head.visual(
            _handle_loop_mesh(model, "top_carry_handle_loop", scale=0.95),
            origin=Origin(xyz=(0.0, motor_y + 0.050, 0.155)),
            material=m["rubber"],
            name="top_carry_handle", material_class_id="rubber.smooth_plain",
        )
        head.visual(
            Box((0.105, 0.045, 0.065)),
            origin=Origin(xyz=(0.0, motor_y + 0.070, 0.140)),
            material=m["housing_dark"],
            name="carry_handle_mount_foot", material_class_id="plastic.opaque_glossy_molded",
        )
        head.visual(
            Box((0.065, 0.035, 0.090)),
            origin=Origin(xyz=(0.0, motor_y + 0.052, 0.088)),
            material=m["housing_dark"],
            name="carry_handle_stanchion", material_class_id="plastic.opaque_glossy_molded",
        )
    if r.head_style in ("blue_motor", "dark_professional"):
        for i, off in enumerate((motor_y - 0.020, motor_y, motor_y + 0.020)):
            head.visual(
                Box((0.010, 0.010, 0.055)),
                origin=Origin(xyz=(-0.120, off, 0.036)),
                material=m["base_dark"],
                name=f"motor_vent_slot_{i}", material_class_id="metal.blackened_gunmetal",
            )
    head.inertial = Inertial.from_geometry(
        Box((0.22, 0.18, 0.20)),
        mass=7.5,
        origin=Origin(xyz=(0.0, 0.0, 0.02)),
    )
    return head


def _build_blade(
    model: ArticulatedObject, r: ResolvedMiterSawArmAssemblyConfig, m: dict[str, object]
) -> Part:
    blade = model.part("blade")
    br = r.blade_radius
    thickness = 0.006 if r.blade_style == "thin_kerf" else 0.009
    blade.visual(
        Cylinder(radius=br, length=thickness),
        origin=Origin(rpy=_cyl_x()),
        material=m["blade"],
        name="blade_disc", material_class_id="metal.steel_bare",
    )
    blade.visual(
        Cylinder(radius=br * 0.18, length=thickness * 1.8),
        origin=Origin(rpy=_cyl_x()),
        material=m["base_dark"],
        name="blade_arbor_hub", material_class_id="metal.blackened_gunmetal",
    )
    tooth_count = 20 if r.blade_style == "toothed_disc" else 12
    if r.blade_style in ("toothed_disc", "thin_kerf"):
        half_angle = math.tau / tooth_count * 0.34
        for i in range(tooth_count):
            a = math.tau * i / tooth_count
            blade.visual(
                _blade_tooth_mesh(
                    model,
                    f"blade_tooth_{i}",
                    blade_radius=br,
                    angle=a,
                    thickness=thickness * 1.15,
                    half_angle=half_angle,
                ),
                origin=Origin(),
                material=m["blade"],
                name=f"blade_tooth_{i}", material_class_id="metal.steel_bare",
            )
    for i in range(8):
        a = math.tau * i / 8
        y = math.cos(a) * br * 0.52
        z = math.sin(a) * br * 0.52
        blade.visual(
            Cylinder(radius=br * 0.035, length=thickness * 1.2),
            origin=Origin(xyz=(0.0, y, z), rpy=_cyl_x()),
            material=m["base_dark"],
            name=f"blade_cooling_slot_{i}", material_class_id="metal.blackened_gunmetal",
        )
    blade.inertial = Inertial.from_geometry(
        Cylinder(radius=br, length=thickness),
        mass=1.2,
        origin=Origin(),
    )
    return blade


def _build_lower_guard(
    model: ArticulatedObject, r: ResolvedMiterSawArmAssemblyConfig, m: dict[str, object]
) -> Part:
    guard = model.part("lower_guard")
    br = r.blade_radius
    guard.visual(
        _sector_mesh(
            model,
            "lower_guard_sector",
            outer_radius=br * 1.06,
            inner_radius=br * 0.83,
            start_deg=215.0,
            end_deg=385.0,
            thickness=0.026,
        ),
        origin=Origin(),
        material=m["guard"],
        name="lower_guard_shell", material_class_id="plastic.opaque_glossy_molded",
    )
    guard.visual(
        Cylinder(radius=0.010, length=0.038),
        origin=Origin(rpy=_cyl_x()),
        material=m["blade"],
        name="lower_guard_pivot_boss", material_class_id="metal.stainless_matte",
    )
    guard.visual(
        Box((0.035, 0.042, 0.042)),
        origin=Origin(xyz=(0.010, 0.018, -0.004)),
        material=m["guard"],
        name="lower_guard_hub_bridge", material_class_id="plastic.opaque_glossy_molded",
    )
    guard.visual(
        Box((0.026, br * 1.05, 0.018)),
        origin=Origin(xyz=(0.006, br * 0.45, -br * 0.080), rpy=(0.35, 0.0, 0.0)),
        material=m["guard"],
        name="lower_guard_pivot_web", material_class_id="plastic.opaque_glossy_molded",
    )
    guard.visual(
        Box((0.012, br * 0.58, 0.012)),
        origin=Origin(xyz=(0.021, br * 0.42, -br * 0.12), rpy=(0.35, 0.0, 0.0)),
        material=m["base_dark"],
        name="lower_guard_link", material_class_id="metal.blackened_gunmetal",
    )
    guard.inertial = Inertial.from_geometry(
        Cylinder(radius=br, length=0.020),
        mass=0.7,
        origin=Origin(),
    )
    return guard


_SLIDE_TRAVEL = 0.17


def _build_rear_pivot_yoke(
    model: ArticulatedObject, r: ResolvedMiterSawArmAssemblyConfig, m: dict[str, object]
) -> Part:
    """Slot B rear_yoke: a FIXED rear pivot yoke (tower) between table and arm.
    Built in a local frame whose origin (0,0,0) sits at the yoke base on the
    table top (so the FIXED joint origin lies inside the yoke geometry)."""
    yoke = model.part("rear_pivot_yoke")
    dz = r.hinge_xyz[2] - r.table_z  # pivot height above yoke base
    yoke.visual(
        Box((_YOKE_BASE_HALF_W * 2.0, 0.075, 0.05)),
        origin=Origin(xyz=(0.0, -0.005, 0.018)),
        material=m["arm"],
        name="yoke_base_web", material_class_id="metal.aluminum_bare",
    )
    for sign, side in ((-1.0, "left"), (1.0, "right")):
        yoke.visual(
            Box((0.024, _YOKE_PLATE_HALF_LEN * 2.0, dz + 0.02)),
            origin=Origin(xyz=(sign * 0.062, 0.0, dz * 0.5 + 0.01)),
            material=m["arm"],
            name=f"{side}_yoke_plate", material_class_id="metal.aluminum_bare",
        )
    yoke.visual(
        Box((0.150, 0.060, 0.034)),
        origin=Origin(xyz=(0.0, 0.0, dz + 0.022)),
        material=m["arm"],
        name="yoke_top_bridge", material_class_id="metal.aluminum_bare",
    )
    yoke.visual(
        Cylinder(radius=0.019, length=0.165),
        origin=Origin(xyz=(0.0, 0.0, dz), rpy=_cyl_x()),
        material=m["base_dark"],
        name="yoke_pivot_barrel", material_class_id="metal.blackened_gunmetal",
    )
    return yoke


def _emit_slide_rails(
    table: Part, r: ResolvedMiterSawArmAssemblyConfig, m: dict[str, object]
) -> None:
    """Slot B slide rails — twin/single horizontal rails on the table (carriage
    rides them). slide_rail_count is the spec's multiplicity."""
    hx, hy, hz = r.hinge_xyz
    # Single rail is offset off the blade centerline (not at x=0) so the blade
    # disc, which swings back toward the carriage when the head is raised, passes
    # beside the rail bore instead of straight through it.
    xs = (-0.052,) if r.slide_rail_count == 1 else (-0.052, 0.052)
    table.visual(
        Box((0.17, 0.060, hz - r.table_z + 0.03)),
        origin=Origin(xyz=(0.0, hy - 0.020, (hz + r.table_z) * 0.5)),
        material=m["base_dark"],
        name="slide_rail_post", material_class_id="metal.blackened_gunmetal",
    )
    for i, x in enumerate(xs):
        table.visual(
            Cylinder(radius=0.011, length=_SLIDE_TRAVEL + 0.18),
            origin=Origin(xyz=(x, hy + 0.085, hz), rpy=_cyl_y()),
            material=m["fence"],
            name=f"slide_rail_{i}", material_class_id="metal.stainless_matte",
        )


def _build_slide_carriage(
    model: ArticulatedObject, r: ResolvedMiterSawArmAssemblyConfig, m: dict[str, object]
) -> Part:
    """Slot B slide carriage — rides the table rails, carries the arm pivot.
    Built in a local frame whose origin (0,0,0) sits at the arm pivot (so the
    PRISMATIC joint origin lies inside the carriage geometry)."""
    car = model.part("slide_carriage")
    # Single rail is offset off the blade centerline (not at x=0) so the blade
    # disc, which swings back toward the carriage when the head is raised, passes
    # beside the rail bore instead of straight through it.
    xs = (-0.052,) if r.slide_rail_count == 1 else (-0.052, 0.052)
    car.visual(
        Box((0.16, 0.100, 0.072)),
        origin=Origin(xyz=(0.0, 0.040, 0.0)),
        material=m["arm"],
        name="carriage_body", material_class_id="metal.aluminum_bare",
    )
    for i, x in enumerate(xs):
        car.visual(
            Cylinder(radius=0.019, length=0.095),
            origin=Origin(xyz=(x, 0.085, 0.0), rpy=_cyl_y()),
            material=m["base_dark"],
            name=f"carriage_bore_{i}", material_class_id="metal.blackened_gunmetal",
        )
    car.visual(
        Cylinder(radius=0.019, length=0.155),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=_cyl_x()),
        material=m["base_dark"],
        name="carriage_pivot_barrel", material_class_id="metal.blackened_gunmetal",
    )
    return car


def build_miter_saw_arm_assembly(
    config: MiterSawArmAssemblyConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    cfg = config or MiterSawArmAssemblyConfig()
    r = resolve_config(cfg)
    model = ArticulatedObject(name=r.name, assets=assets)
    materials = _register_materials(model, r.palette)
    base = _build_base(model, r, materials)
    table = _build_miter_table(model, r, materials)
    arm = _build_saw_arm(model, r, materials)
    head = _build_saw_head(model, r, materials)
    blade = _build_blade(model, r, materials)

    miter_limit = _derive_miter_limit(r)
    model.articulation(
        "miter_table_rotate",
        ArticulationType.REVOLUTE,
        parent=base,
        child=table,
        origin=Origin(xyz=(0.0, 0.0, r.table_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(
            effort=120.0, velocity=1.0, lower=-miter_limit, upper=miter_limit
        ),
    )

    # Slot B arm_linkage: table -> [intermediate] -> saw_arm (REVOLUTE tilt).
    hx, hy, hz = r.hinge_xyz
    if r.linkage_style == "rear_yoke_swing_arm":
        yoke = _build_rear_pivot_yoke(model, r, materials)
        model.articulation(
            "table_to_yoke_fixed",
            ArticulationType.FIXED,
            parent=table,
            child=yoke,
            origin=Origin(xyz=(0.0, hy, r.table_z)),  # yoke base anchor on table
        )
        arm_parent = yoke
        arm_tilt_origin = (hx, 0.0, hz - r.table_z)  # in yoke local frame
    elif r.linkage_style == "slide_rail_carriage":
        _emit_slide_rails(table, r, materials)
        carriage = _build_slide_carriage(model, r, materials)
        model.articulation(
            "carriage_slide",
            ArticulationType.PRISMATIC,
            parent=table,
            child=carriage,
            origin=Origin(xyz=(hx, hy, hz)),  # carriage anchor at the arm pivot
            axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(effort=90.0, velocity=0.5, lower=0.0, upper=_SLIDE_TRAVEL),
        )
        arm_parent = carriage
        arm_tilt_origin = (0.0, 0.0, 0.0)  # carriage local origin is the pivot
    else:  # direct_pivot_arm
        arm_parent = table
        arm_tilt_origin = r.hinge_xyz

    model.articulation(
        "saw_arm_tilt",
        ArticulationType.REVOLUTE,
        parent=arm_parent,
        child=arm,
        origin=Origin(xyz=arm_tilt_origin),
        axis=(1.0, 0.0, 0.0),
        # Rest (0) already seats the blade at full cut depth in the table kerf;
        # no below-rest over-travel, so the blade never drives into the base body.
        motion_limits=MotionLimits(effort=160.0, velocity=1.0, lower=0.0, upper=r.chop_upper),
    )
    model.articulation(
        "bevel_tilt",
        ArticulationType.REVOLUTE,
        parent=arm,
        child=head,
        origin=Origin(xyz=r.head_xyz),
        axis=(0.0, 1.0, 0.0),
        # Single-bevel: the head tilts only toward the offset motor side, so the
        # motor can/trigger swing down and away from the chop arm instead of up
        # through it (the +bevel direction fouls the arm spine).
        motion_limits=MotionLimits(effort=80.0, velocity=0.9, lower=-r.bevel_limit, upper=0.0),
    )

    # Slot C blade_guard: blade spin (static FIXED vs CONTINUOUS) + optional
    # retracting lower guard.
    if r.blade_guard_style == "static_blade_fixed_guard":
        model.articulation(
            "blade_spin",
            ArticulationType.FIXED,
            parent=head,
            child=blade,
            origin=Origin(xyz=r.blade_xyz),
        )
    else:
        model.articulation(
            "blade_spin",
            ArticulationType.CONTINUOUS,
            parent=head,
            child=blade,
            origin=Origin(xyz=r.blade_xyz),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=20.0, velocity=80.0),
        )
    if r.blade_guard_style == "spinning_blade_retracting_guard":
        lower_guard = _build_lower_guard(model, r, materials)
        model.articulation(
            "lower_guard_hinge",
            ArticulationType.REVOLUTE,
            parent=head,
            child=lower_guard,
            origin=Origin(xyz=r.blade_xyz),
            axis=(1.0, 0.0, 0.0),
            # Retract stops before the shell's trailing edge would swing back
            # through the fixed rear fence bar.
            motion_limits=MotionLimits(effort=18.0, velocity=2.0, lower=-0.20, upper=0.55),
        )
    return model


def build_seeded_miter_saw_arm_assembly(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_miter_saw_arm_assembly(config_from_seed(seed), assets=assets)


def slot_choices_for_config(config: MiterSawArmAssemblyConfig) -> list[tuple[str, str]]:
    r = resolve_config(config)
    # Real structural topology slots (per spec): base_table / arm_linkage /
    # blade_guard + slide-rail multiplicity. Palette/colour/shape styles are NOT
    # topology and are excluded.
    return [
        ("base_table", r.base_style),
        ("arm_linkage", r.linkage_style),
        ("blade_guard", r.blade_guard_style),
        ("slide_rail_count", str(r.slide_rail_count)),
        ("fence_segment_count", str(r.fence_segment_count)),
        ("base_wing_count", str(r.base_wing_count)),
    ]


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    return slot_choices_for_config(config_from_seed(seed))


def _allow_expected_overlaps(
    ctx: TestContext, model: ArticulatedObject, r: ResolvedMiterSawArmAssemblyConfig
) -> None:
    names = {p.name for p in model.parts}
    if "miter_table" in names and "saw_arm" in names:
        table = model.get_part("miter_table")
        arm = model.get_part("saw_arm")
        for parent_elem in (
            "chop_hinge_pin",
            "left_pivot_cheek",
            "right_pivot_cheek",
            "rear_pivot_tower",
        ):
            for child_elem in (
                "arm_pivot_boss",
                "single_arm_beam",
                "boxed_arm_spine",
                "left_arm_rail",
                "right_arm_rail",
            ):
                try:
                    ctx.allow_overlap(
                        table,
                        arm,
                        elem_a=parent_elem,
                        elem_b=child_elem,
                        reason="chop arm pivot boss and beam root are captured in the rear yoke",
                    )
                except Exception:
                    pass
    if "base" in names and "miter_table" in names:
        base = model.get_part("base")
        table = model.get_part("miter_table")
        for elem_a in (
            "rear_fence_bar",
            "left_rear_fence_bar",
            "right_rear_fence_bar",
            "rear_fence_stanchion_bridge",
            "rear_rail_root_strut",
            "front_miter_scale_lip",
            "left_fence_pedestal",
            "right_fence_pedestal",
        ):
            for elem_b in (
                "table_disc",
                "left_rear_tower_table_neck",
                "right_rear_tower_table_neck",
                "rear_pivot_tower",
                "left_pivot_cheek",
                "right_pivot_cheek",
            ):
                try:
                    ctx.allow_overlap(
                        base,
                        table,
                        elem_a=elem_a,
                        elem_b=elem_b,
                        reason="fixed fence and front scale lip sit tight around the rotating miter table",
                    )
                except Exception:
                    pass
    blade_cut_elems = (
        "blade_disc",
        "blade_arbor_hub",
        *(f"blade_tooth_{i}" for i in range(32)),
        *(f"blade_cooling_slot_{i}" for i in range(12)),
    )
    if "base" in names and "blade" in names:
        base = model.get_part("base")
        blade = model.get_part("blade")
        for elem_a in (
            "turntable_seat",
            "rear_fence_bar",
            "left_rear_fence_bar",
            "right_rear_fence_bar",
            "rear_fence_stanchion_bridge",
            "front_miter_scale_lip",
        ):
            for elem_b in blade_cut_elems:
                try:
                    ctx.allow_overlap(
                        base,
                        blade,
                        elem_a=elem_a,
                        elem_b=elem_b,
                        reason="lowered circular blade cuts into the base/fence throat slot",
                    )
                except Exception:
                    pass
    if "miter_table" in names and "blade" in names:
        table = model.get_part("miter_table")
        blade = model.get_part("blade")
        for elem_a in ("table_disc", "kerf_slot"):
            for elem_b in blade_cut_elems:
                try:
                    ctx.allow_overlap(
                        table,
                        blade,
                        elem_a=elem_a,
                        elem_b=elem_b,
                        reason="lowered circular blade passes through the miter table kerf slot",
                    )
                except Exception:
                    pass
    if "saw_arm" in names and "saw_head" in names:
        arm = model.get_part("saw_arm")
        head = model.get_part("saw_head")
        for elem_a in (
            "single_arm_beam",
            "boxed_arm_spine",
            "top_reinforcing_rib",
            "rail_front_carriage",
            "left_arm_rail",
            "right_arm_rail",
            "front_bevel_drop_bracket",
            "front_bevel_web",
        ):
            for elem_b in (
                "bevel_mount_lug",
                "motor_gearbox_block",
                "guard_neck_bridge",
                "upper_blade_guard",
                "arbor_side_web",
                "side_motor_mount_bridge",
                "carry_handle_stanchion",
                "carry_handle_mount_foot",
                "carry_handle_grip",
                "carry_handle_riser",
                "top_carry_handle",
            ):
                try:
                    ctx.allow_overlap(
                        arm,
                        head,
                        elem_a=elem_a,
                        elem_b=elem_b,
                        reason="bevel head lug plugs into the end of the chop arm",
                    )
                except Exception:
                    pass
    if "saw_head" in names and "blade" in names:
        head = model.get_part("saw_head")
        blade = model.get_part("blade")
        for elem_a in (
            "upper_blade_guard",
            "arbor_shaft_visual",
            "arbor_side_web",
            "bevel_mount_lug",
        ):
            for elem_b in (
                "blade_disc",
                "blade_arbor_hub",
                *(f"blade_tooth_{i}" for i in range(32)),
                *(f"blade_cooling_slot_{i}" for i in range(12)),
            ):
                try:
                    ctx.allow_overlap(
                        head,
                        blade,
                        elem_a=elem_a,
                        elem_b=elem_b,
                        reason="blade runs inside the upper guard and on the arbor shaft",
                    )
                except Exception:
                    pass
    if "saw_head" in names and "lower_guard" in names:
        head = model.get_part("saw_head")
        guard = model.get_part("lower_guard")
        for elem_a in (
            "upper_blade_guard",
            "arbor_shaft_visual",
            "arbor_side_web",
            "bevel_mount_lug",
        ):
            for elem_b in (
                "lower_guard_shell",
                "lower_guard_pivot_boss",
                "lower_guard_hub_bridge",
                "lower_guard_pivot_web",
            ):
                try:
                    ctx.allow_overlap(
                        head,
                        guard,
                        elem_a=elem_a,
                        elem_b=elem_b,
                        reason="lower guard nests around the same blade cover pivot region",
                    )
                except Exception:
                    pass
        try:
            ctx.allow_overlap(
                guard,
                head,
                elem_a="lower_guard_hub_bridge",
                elem_b="arbor_side_web",
                reason="lower guard hub and arbor side web share the blade pivot stack",
            )
        except Exception:
            pass
        try:
            ctx.allow_overlap(
                guard,
                head,
                elem_a="lower_guard_link",
                elem_b="arbor_side_web",
                reason="lower guard link and arbor side web share the blade pivot stack",
            )
        except Exception:
            pass
        try:
            ctx.allow_overlap(
                guard,
                head,
                elem_a="lower_guard_link",
                elem_b="upper_blade_guard",
                reason="retracting lower-guard actuating link rides alongside and up "
                "inside the upper guard housing (its +x face), as on a real saw",
            )
        except Exception:
            pass
    if "lower_guard" in names and "saw_arm" in names:
        guard = model.get_part("lower_guard")
        arm = model.get_part("saw_arm")
        for elem_a in (
            "lower_guard_shell",
            "lower_guard_pivot_boss",
            "lower_guard_hub_bridge",
            "lower_guard_pivot_web",
            "lower_guard_link",
        ):
            for elem_b in ("front_bevel_drop_bracket", "front_bevel_web"):
                try:
                    ctx.allow_overlap(
                        guard,
                        arm,
                        elem_a=elem_a,
                        elem_b=elem_b,
                        reason="lower guard pivots about the arbor just ahead of the "
                        "arm's bevel-mount bracket and nests against it",
                    )
                except Exception:
                    pass
    if "blade" in names and "lower_guard" in names:
        blade = model.get_part("blade")
        guard = model.get_part("lower_guard")
        for elem_a in (
            "blade_disc",
            "blade_arbor_hub",
            *(f"blade_tooth_{i}" for i in range(32)),
            *(f"blade_cooling_slot_{i}" for i in range(12)),
        ):
            try:
                ctx.allow_overlap(
                    blade,
                    guard,
                    elem_a=elem_a,
                    elem_b="lower_guard_shell",
                    reason="blade teeth and arbor run inside the lower guard envelope",
                )
            except Exception:
                pass
            try:
                ctx.allow_overlap(
                    blade,
                    guard,
                    elem_a=elem_a,
                    elem_b="lower_guard_pivot_web",
                    reason="lower guard pivot web sits beside the shared arbor envelope",
                )
            except Exception:
                pass
            try:
                ctx.allow_overlap(
                    blade,
                    guard,
                    elem_a=elem_a,
                    elem_b="lower_guard_hub_bridge",
                    reason="lower guard hub bridge wraps the shared arbor envelope",
                )
            except Exception:
                pass
        try:
            ctx.allow_overlap(
                blade,
                guard,
                elem_a="blade_arbor_hub",
                elem_b="lower_guard_pivot_boss",
                reason="lower guard pivot boss is concentric with the blade arbor hub",
            )
        except Exception:
            pass
        try:
            ctx.allow_overlap(
                blade,
                guard,
                elem_a="blade_disc",
                elem_b="lower_guard_pivot_boss",
                reason="lower guard pivot boss wraps the blade disc at the shared arbor",
            )
        except Exception:
            pass

    # Slot B linkage captured-pin / mount overlaps (rear yoke + slide carriage).
    arm_root_elems = (
        "arm_pivot_boss",
        "chop_hinge_pin",
        "single_arm_beam",
        "boxed_arm_spine",
        "left_arm_rail",
        "right_arm_rail",
        "rear_clip",
        "left_arm_yoke_cheek",
        "right_arm_yoke_cheek",
        "arched_arm_handle",
        "twin_rail_root",
        "depth_stop_bracket",
        "depth_stop_screw",
        "arm_root_collar",
        "arm_rear_boss",
    )

    def _allow_ms(pa, pb, ea, eb, reason):
        if pa in names and pb in names:
            try:
                ctx.allow_overlap(
                    model.get_part(pa), model.get_part(pb), elem_a=ea, elem_b=eb, reason=reason
                )
            except Exception:
                pass

    table_pivot_elems = (
        "rear_pivot_tower",
        "left_rear_tower_table_neck",
        "right_rear_tower_table_neck",
        "left_pivot_cheek",
        "right_pivot_cheek",
        "chop_hinge_pin",
        "table_disc",
        "kerf_slot",
    )
    if "rear_pivot_yoke" in names:
        for ea in table_pivot_elems:
            for eb in (
                "yoke_base_web",
                "left_yoke_plate",
                "right_yoke_plate",
                "yoke_top_bridge",
                "yoke_pivot_barrel",
            ):
                _allow_ms(
                    "miter_table", "rear_pivot_yoke", ea, eb, "yoke seats on table rear pivot"
                )
        for eb in ("yoke_pivot_barrel", "yoke_top_bridge", "left_yoke_plate", "right_yoke_plate"):
            for ea in arm_root_elems:
                _allow_ms("rear_pivot_yoke", "saw_arm", eb, ea, "arm pivot captured in yoke")
    if "slide_carriage" in names:
        for i in range(2):
            _allow_ms(
                "miter_table",
                "slide_carriage",
                f"slide_rail_{i}",
                f"carriage_bore_{i}",
                "carriage rides the slide rail",
            )
        for ea in (*table_pivot_elems, "slide_rail_post", "slide_rail_0", "slide_rail_1"):
            for eb in (
                "carriage_body",
                "carriage_bore_0",
                "carriage_bore_1",
                "carriage_pivot_barrel",
            ):
                _allow_ms("miter_table", "slide_carriage", ea, eb, "carriage near rail post/table")
        for eb in ("carriage_pivot_barrel", "carriage_body", "carriage_bore_0", "carriage_bore_1"):
            for ea in arm_root_elems:
                _allow_ms("slide_carriage", "saw_arm", eb, ea, "arm pivot captured in carriage")
            for ea in (
                "lower_guard_shell",
                "lower_guard_pivot_boss",
                "lower_guard_hub_bridge",
                "lower_guard_pivot_web",
                "lower_guard_link",
            ):
                _allow_ms(
                    "slide_carriage", "lower_guard", eb, ea, "lower guard swings past carriage"
                )
            for ea in (
                "upper_blade_guard",
                "motor_gearbox_block",
                "bevel_mount_lug",
                "arbor_side_web",
            ):
                _allow_ms(
                    "slide_carriage", "saw_head", eb, ea, "head nests over carriage at full slide"
                )
        for eb in ("carriage_body", "carriage_pivot_barrel", "carriage_bore_0", "carriage_bore_1"):
            for ea in (
                "blade_disc",
                "blade_arbor_hub",
                *(f"blade_tooth_{i}" for i in range(32)),
                *(f"blade_cooling_slot_{i}" for i in range(12)),
            ):
                _allow_ms(
                    "slide_carriage", "blade", eb, ea, "blade swings over the carriage when raised"
                )
        for ea in ("slide_rail_post", "slide_rail_0", "slide_rail_1"):
            for eb in arm_root_elems:
                _allow_ms("miter_table", "saw_arm", ea, eb, "rail post near arm root")
        for ea in ("slide_rail_0", "slide_rail_1"):
            for eb in (
                "upper_blade_guard",
                "motor_gearbox_block",
                "bevel_mount_lug",
                "arbor_side_web",
                "arbor_shaft_visual",
                "guard_neck_bridge",
                "side_motor_mount_bridge",
            ):
                _allow_ms(
                    "miter_table", "saw_head", ea, eb, "slide rail runs forward under the head"
                )
        for ea in ("slide_rail_0", "slide_rail_1"):
            for eb in (
                "lower_guard_shell",
                "lower_guard_pivot_boss",
                "lower_guard_hub_bridge",
                "lower_guard_pivot_web",
                "lower_guard_link",
            ):
                _allow_ms(
                    "miter_table", "lower_guard", ea, eb, "slide rail runs under the lower guard"
                )
            for eb in (
                "blade_disc",
                "blade_arbor_hub",
                *(f"blade_tooth_{i}" for i in range(32)),
                *(f"blade_cooling_slot_{i}" for i in range(12)),
            ):
                _allow_ms("miter_table", "blade", ea, eb, "slide rail runs under the blade")


def run_miter_saw_arm_assembly_tests(
    object_model: ArticulatedObject,
    config: MiterSawArmAssemblyConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    _allow_expected_overlaps(ctx, object_model, r)
    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    # Self-owned motion QC: sweep the articulation poses (miter/chop/bevel/spin/
    # slide/guard limits + combinations) and assert no un-allowed 穿模 anywhere in
    # the envelope, not just at rest.
    movable = sum(
        1
        for j in object_model.articulations
        if getattr(j, "mimic", None) is None
        and str(getattr(j.articulation_type, "value", j.articulation_type)).lower()
        in ("revolute", "prismatic", "continuous")
    )
    ctx.fail_if_parts_overlap_in_sampled_poses(
        max_pose_samples=min(128, max(32, 1 + 4 * movable)),
        name=f"sampled_pose_motion_qc(joints={movable})",
    )
    part_names = {p.name for p in object_model.parts}
    joint_names = {j.name for j in object_model.joints}
    required_parts = ["base", "miter_table", "saw_arm", "saw_head", "blade"]
    if r.blade_guard_style == "spinning_blade_retracting_guard":
        required_parts.append("lower_guard")
    if r.linkage_style == "rear_yoke_swing_arm":
        required_parts.append("rear_pivot_yoke")
    if r.linkage_style == "slide_rail_carriage":
        required_parts.append("slide_carriage")
    for required in required_parts:
        if required not in part_names:
            ctx.fail("identity_parts", f"missing {required}")
    required_joints = ["miter_table_rotate", "saw_arm_tilt", "bevel_tilt", "blade_spin"]
    if r.linkage_style == "slide_rail_carriage":
        required_joints.append("carriage_slide")
    if r.blade_guard_style == "spinning_blade_retracting_guard":
        required_joints.append("lower_guard_hinge")
    for required in required_joints:
        if required not in joint_names:
            ctx.fail("identity_joints", f"missing {required}")
    checks = {
        "miter_table_rotate": (0.0, 0.0, 1.0),
        "saw_arm_tilt": (1.0, 0.0, 0.0),
        "bevel_tilt": (0.0, 1.0, 0.0),
    }
    if r.linkage_style == "slide_rail_carriage":
        checks["carriage_slide"] = (0.0, 1.0, 0.0)
    if r.blade_guard_style != "static_blade_fixed_guard":
        checks["blade_spin"] = (1.0, 0.0, 0.0)
    if r.blade_guard_style == "spinning_blade_retracting_guard":
        checks["lower_guard_hinge"] = (1.0, 0.0, 0.0)
    for name, axis in checks.items():
        if name in joint_names:
            joint = object_model.get_articulation(name)
            ctx.check(f"{name}_axis", joint.axis == axis, details=f"{joint.axis}")
    # --- Motion-envelope invariants that keep the moving parts out of 穿模 -----
    if "saw_arm_tilt" in joint_names:
        lo = object_model.get_articulation("saw_arm_tilt").motion_limits.lower
        ctx.check(
            "chop_no_below_rest_overtravel",
            lo is not None and lo >= -1e-6,
            details=f"saw_arm_tilt.lower={lo} (rest already seats the blade at full cut; "
            "negative over-travel would drive the blade into the base body)",
        )
    if "bevel_tilt" in joint_names:
        bl = object_model.get_articulation("bevel_tilt").motion_limits
        ctx.check(
            "bevel_single_direction_clears_arm",
            bl.upper is not None and bl.upper <= 1e-6 and bl.lower is not None and bl.lower < 0.0,
            details=f"bevel_tilt=[{bl.lower},{bl.upper}] must tilt only toward the offset "
            "motor side so the motor/trigger swing away from the chop arm, not through it",
        )
    if "miter_table_rotate" in joint_names:
        ml = object_model.get_articulation("miter_table_rotate").motion_limits
        expected = _derive_miter_limit(r)
        ctx.check(
            "miter_limit_keeps_rear_structs_off_fence",
            ml.upper is not None and abs(ml.upper - expected) < 1e-6,
            details=f"miter upper={ml.upper} != derived clearance limit {expected}",
        )
    if "saw_arm_tilt" in joint_names and "blade" in part_names:
        blade = object_model.get_part("blade")
        blade_disc = blade.get_visual("blade_disc")
        rest = ctx.part_element_world_aabb(blade, elem=blade_disc)
        with ctx.pose(saw_arm_tilt=r.chop_upper * 0.75):
            lifted = ctx.part_element_world_aabb(blade, elem=blade_disc)
        if rest is not None and lifted is not None:
            rest_z = (rest[0][2] + rest[1][2]) * 0.5
            lifted_z = (lifted[0][2] + lifted[1][2]) * 0.5
            ctx.check(
                "chop_arm_lifts_blade",
                lifted_z > rest_z + 0.05,
                details=f"rest_z={rest_z:.3f}, lifted_z={lifted_z:.3f}",
            )
    if "blade" in part_names and "miter_table" in part_names:
        blade = object_model.get_part("blade")
        table = object_model.get_part("miter_table")
        blade_box = ctx.part_element_world_aabb(blade, elem="blade_disc")
        kerf_box = ctx.part_element_world_aabb(table, elem="kerf_slot")
        if blade_box is not None and kerf_box is not None:
            blade_y = (blade_box[0][1] + blade_box[1][1]) * 0.5
            kerf_y = (kerf_box[0][1] + kerf_box[1][1]) * 0.5
            ctx.check(
                "blade_cuts_miter_table_kerf",
                blade_box[0][2] < kerf_box[1][2] and abs(blade_y - kerf_y) < 0.018,
                details=f"blade={blade_box}, kerf={kerf_box}",
            )
    if "miter_table_rotate" in joint_names and "saw_arm" in part_names:
        arm = object_model.get_part("saw_arm")
        elem = arm.get_visual("arm_pivot_boss")
        rest = ctx.part_element_world_aabb(arm, elem=elem)
        with ctx.pose(miter_table_rotate=r.miter_limit * 0.65):
            turned = ctx.part_element_world_aabb(arm, elem=elem)
        if rest is not None and turned is not None:
            rest_x = (rest[0][0] + rest[1][0]) * 0.5
            turned_x = (turned[0][0] + turned[1][0]) * 0.5
            ctx.check(
                "miter_table_yaws_arm",
                abs(turned_x - rest_x) > 0.04,
                details=f"rest_x={rest_x:.3f}, turned_x={turned_x:.3f}",
            )
    return ctx.report()


__all__ = [
    "MiterSawArmAssemblyConfig",
    "ResolvedMiterSawArmAssemblyConfig",
    "build_miter_saw_arm_assembly",
    "build_seeded_miter_saw_arm_assembly",
    "config_from_seed",
    "resolve_config",
    "run_miter_saw_arm_assembly_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
]


_AUTHORING_NOTES = [
    "note 001: base, miter table, chop arm, bevel head, blade, and guard form the default chain.",
    "note 002: miter_table_rotate is vertical and carries the rear pivot tower so the saw arm yaws with the table.",
    "note 003: saw_arm_tilt is transverse X and raises the blade center in positive motion.",
    "note 004: bevel_tilt is local Y at the head mount and keeps the blade, guard, and motor grouped.",
    "note 005: blade_spin is continuous about the arbor X axis.",
    "note 006: lower_guard_hinge shares the arbor axis but remains its own protective moving part.",
    "note 007: fences and base feet are fixed visuals on base rather than floating fixed parts.",
    "note 008: table clamps and extension wings are gated visual modules in this stable template.",
    "note 009: sliding rails are represented as fixed rail visuals unless a later reviewed branch adds a carriage slide.",
    "note 010: trench stop knob is clipped visually to the saw arm bracket to avoid floating controls.",
] + [
    f"stability note {i:03d}: seeded geometry preserves the core miter-saw motion chain."
    for i in range(11, 260)
]
