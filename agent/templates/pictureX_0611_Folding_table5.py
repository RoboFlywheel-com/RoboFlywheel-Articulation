# SPDX-License-Identifier: Apache-2.0

"""Self-contained round gateleg drop-leaf table.

One rigid ``table_frame`` root carries the fixed centre spine of the top, the
steel carcass under it and every support pivot.  Two ``drop_leaf`` parts are
REVOLUTE children of the frame, hinged on both long edges of the spine: q=0 is
raised and coplanar, q=upper is folded straight down beside the frame.

Because a folded leaf hangs on the hinge line while every support swings out
well outboard of it, no support and no folded leaf ever share space, so all
support x frame x support_per_leaf combinations build.

No source-replay import, no motion clamping, no whole-part overlap allowance.
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
    AxisInterface,
    Box,
    Cylinder,
    ExtrudeGeometry,
    Mimic,
    MotionLimits,
    Origin,
    TemplateDomain,
    TestContext,
    TestReport,
    component_slot,
    corner_case,
    mate_axes,
    mesh_from_geometry,
    multiplicity_slot,
    register_interface_mate,
)

SupportBuild = Literal[
    "swing_gate", "arc_gate", "cross_trestle", "telescoping_brace", "wall_bracket", "latch_gate"
]
FrameBuild = Literal["open_spine", "shelf_spine", "double_shelf"]
FootBuild = Literal["fixed_glide", "pad_foot", "swivel_caster", "braked_caster"]
PaletteStyle = Literal["warm_oak", "bamboo", "walnut", "grey_ash"]

SUPPORT_BUILDS: tuple[SupportBuild, ...] = (
    "swing_gate",
    "arc_gate",
    "cross_trestle",
    "telescoping_brace",
    "wall_bracket",
    "latch_gate",
)
FRAME_BUILDS: tuple[FrameBuild, ...] = ("open_spine", "shelf_spine", "double_shelf")
FOOT_BUILDS: tuple[FootBuild, ...] = (
    "fixed_glide",
    "pad_foot",
    "swivel_caster",
    "braked_caster",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = ("warm_oak", "bamboo", "walnut", "grey_ash")

TEMPLATE_DOMAIN = TemplateDomain(
    slots=(
        component_slot("support_build", SUPPORT_BUILDS),
        component_slot("frame_build", FRAME_BUILDS),
        component_slot("foot_build", FOOT_BUILDS),
        multiplicity_slot("support_per_leaf", (1, 2), item_slot="support_build"),
    )
)

PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "warm_oak": {
        "wood": (0.72, 0.51, 0.28, 1.0),
        "edge": (0.55, 0.36, 0.18, 1.0),
        "steel": (0.13, 0.13, 0.14, 1.0),
        "hardware": (0.34, 0.35, 0.36, 1.0),
        "rubber": (0.05, 0.05, 0.05, 1.0),
    },
    "bamboo": {
        "wood": (0.84, 0.69, 0.40, 1.0),
        "edge": (0.66, 0.51, 0.27, 1.0),
        "steel": (0.20, 0.20, 0.21, 1.0),
        "hardware": (0.42, 0.43, 0.44, 1.0),
        "rubber": (0.06, 0.06, 0.06, 1.0),
    },
    "walnut": {
        "wood": (0.36, 0.23, 0.15, 1.0),
        "edge": (0.25, 0.16, 0.10, 1.0),
        "steel": (0.11, 0.11, 0.12, 1.0),
        "hardware": (0.30, 0.31, 0.32, 1.0),
        "rubber": (0.04, 0.04, 0.04, 1.0),
    },
    "grey_ash": {
        "wood": (0.70, 0.69, 0.66, 1.0),
        "edge": (0.52, 0.51, 0.49, 1.0),
        "steel": (0.24, 0.25, 0.26, 1.0),
        "hardware": (0.50, 0.51, 0.52, 1.0),
        "rubber": (0.07, 0.07, 0.07, 1.0),
    },
}

TOP_T = 0.022  # tabletop thickness
SEAM = 0.0015  # visible seam between spine and leaf
HINGE_DROP = 0.026  # butt-hinge axis below the tabletop plane
LEAF_FOLD = math.radians(88.0)
SUPPORT_SWING = math.radians(90.0)
RAIL_H = 0.048  # frame spine rail depth
UPRIGHT_W = 0.038  # frame upright section
SPLAY_KNEE_Z = 0.190  # uprights start splaying below this height
YOKE_Y = 0.024  # half spacing of every bearing yoke cheek
SUPPORT_X0 = 0.034  # support geometry starts outboard of its bearing plate
MOUNT = 0.0008  # intra-part embedment so one part stays one island
CASTER_R = 0.032  # caster wheel radius


@dataclass(frozen=True)
class Config:
    support_build: SupportBuild = "swing_gate"
    frame_build: FrameBuild = "open_spine"
    foot_build: FootBuild = "fixed_glide"
    support_per_leaf: int = 1
    top_diameter_m: float | None = None
    spine_width_ratio: float | None = None
    table_height_m: float | None = None
    palette_style: PaletteStyle = "warm_oak"
    name: str = "pictureX_0611_Folding_table5"


@dataclass(frozen=True)
class ResolvedConfig:
    support_build: SupportBuild
    frame_build: FrameBuild
    foot_build: FootBuild
    support_per_leaf: int
    palette_style: PaletteStyle
    palette: dict[str, tuple[float, float, float, float]]
    top_diameter_m: float
    spine_width_ratio: float
    table_height_m: float
    top_radius_m: float
    hinge_offset_m: float
    leaf_reach_m: float
    support_reach_m: float
    support_total: int
    support_y: tuple[float, ...]
    top_z: float
    under_z: float
    hinge_z: float
    pivot_x_m: float
    upright_y: float
    frame_drop_m: float
    support_pivot_z: float
    foot_x_m: float
    caster_count: int
    name: str


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(value)))


def config_from_seed(seed: int) -> Config:
    rng = random.Random(int(seed) ^ 0x0F75_3305)
    choices = TEMPLATE_DOMAIN.sample(rng)
    return Config(
        support_build=choices["support_build"],
        frame_build=choices["frame_build"],
        foot_build=choices["foot_build"],
        support_per_leaf=choices["support_per_leaf"],
        top_diameter_m=round(rng.uniform(0.95, 1.30), 4),
        spine_width_ratio=round(rng.uniform(0.19, 0.30), 4),
        table_height_m=round(rng.uniform(0.70, 0.78), 4),
        palette_style=rng.choice(PALETTE_STYLES),
        name=f"folding_table5_seed_{int(seed)}",
    )


def resolve_config(config: Config) -> ResolvedConfig:
    TEMPLATE_DOMAIN.validate(
        {
            "support_build": config.support_build,
            "frame_build": config.frame_build,
            "foot_build": config.foot_build,
            "support_per_leaf": config.support_per_leaf,
        }
    )
    if config.palette_style not in PALETTES:
        raise ValueError(f"unsupported palette_style: {config.palette_style}")
    if config.top_diameter_m is not None and not 0.95 <= float(config.top_diameter_m) <= 1.30:
        raise ValueError("top_diameter_m must be in [0.95, 1.30]")
    if config.spine_width_ratio is not None and not (
        0.19 <= float(config.spine_width_ratio) <= 0.30
    ):
        raise ValueError("spine_width_ratio must be in [0.19, 0.30]")
    if config.table_height_m is not None and not 0.70 <= float(config.table_height_m) <= 0.78:
        raise ValueError("table_height_m must be in [0.70, 0.78]")

    diameter = (
        _clamp(config.top_diameter_m, 0.95, 1.30) if config.top_diameter_m is not None else 1.10
    )
    ratio = (
        _clamp(config.spine_width_ratio, 0.19, 0.30)
        if config.spine_width_ratio is not None
        else 0.24
    )
    height = (
        _clamp(config.table_height_m, 0.70, 0.78) if config.table_height_m is not None else 0.742
    )

    radius = diameter * 0.5
    hinge_offset = diameter * ratio * 0.5
    leaf_reach = radius - hinge_offset
    support_reach = _clamp(0.62 * leaf_reach + 0.020, 0.18, 0.34)
    top_z = height - TOP_T * 0.5
    under_z = height - TOP_T
    hinge_z = height - HINGE_DROP
    # Supports pivot just outboard of the spine so their whole swing clears the
    # hinge line a folded leaf hangs on.
    pivot_x = hinge_offset - 0.040
    upright_y = radius * 0.80
    frame_drop = under_z - RAIL_H
    foot_x = max(hinge_offset + 0.060, 0.110)

    n = int(config.support_per_leaf)
    if n == 1:
        stations = (0.0,)
    else:
        stations = (-upright_y * 0.10, upright_y * 0.10)
    # A stowed gate lies along the spine toward its own end of the table, so it
    # stops short of the end frame and never meets the other station's gate.
    support_reach = min(support_reach, upright_y * 0.80 - 0.045)
    # The gate and its leaf turn together, so the gate's top rail has to stay
    # under the leaf plane at EVERY matched angle, not just at the ends.  The
    # worst case is the deepest the tilting leaf ever reaches over the gate.
    worst = 0.0
    for step in range(1, 90):
        a = math.radians(step)
        worst = max(worst, support_reach * math.sin(a) - 0.040 * math.tan(a))
    support_depth = worst + 0.030

    caster_count = 4 if config.foot_build in ("swivel_caster", "braked_caster") else 0
    return ResolvedConfig(
        support_build=config.support_build,
        frame_build=config.frame_build,
        foot_build=config.foot_build,
        support_per_leaf=n,
        palette_style=config.palette_style,
        palette=dict(PALETTES[config.palette_style]),
        top_diameter_m=diameter,
        spine_width_ratio=ratio,
        table_height_m=height,
        top_radius_m=radius,
        hinge_offset_m=hinge_offset,
        leaf_reach_m=leaf_reach,
        support_reach_m=support_reach,
        support_total=2 * n,
        support_y=tuple(stations),
        top_z=top_z,
        under_z=under_z,
        hinge_z=hinge_z,
        pivot_x_m=pivot_x,
        upright_y=upright_y,
        frame_drop_m=frame_drop,
        support_pivot_z=hinge_z - support_depth,
        foot_x_m=foot_x,
        caster_count=caster_count,
        name=config.name,
    )


def slot_choices_for_config(config: Config | ResolvedConfig) -> tuple[tuple[str, object], ...]:
    return (
        ("support_build", config.support_build),
        ("frame_build", config.frame_build),
        ("foot_build", config.foot_build),
        ("support_per_leaf", config.support_per_leaf),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, object], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# --- helpers ----------------------------------------------------------------
def _materials(model: ArticulatedObject, r: ResolvedConfig) -> dict[str, str]:
    mats: dict[str, str] = {}
    for key, rgba in r.palette.items():
        model.material(f"ft5_{r.palette_style}_{key}", rgba=rgba)
        mats[key] = f"ft5_{r.palette_style}_{key}"
    return mats


def _rod(part, p0, p1, radius: float, material: str, name: str) -> None:
    vx, vy, vz = p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]
    length = math.sqrt(vx * vx + vy * vy + vz * vz)
    horiz = math.hypot(vx, vy)
    yaw = math.atan2(vy, vx) if horiz > 1e-12 else 0.0
    pitch = math.atan2(horiz, vz)
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=Origin(
            xyz=((p0[0] + p1[0]) * 0.5, (p0[1] + p1[1]) * 0.5, (p0[2] + p1[2]) * 0.5),
            rpy=(0.0, pitch, yaw),
        ),
        material=material,
        name=name, material_class_id="metal.steel_bare",
    )


def _axis_joint(
    model: ArticulatedObject,
    *,
    name: str,
    parent,
    child,
    point,
    axis,
    radial,
    child_axis=(0.0, 1.0, 0.0),
    child_radial=(1.0, 0.0, 0.0),
    mimic: Mimic | None = None,
    lower: float,
    upper: float,
    effort: float,
    velocity: float,
    meta: dict | None = None,
) -> None:
    provider = AxisInterface(name=f"{name}__provider", point=point, axis=axis, radial=radial)
    consumer = AxisInterface(name=f"{name}__consumer", axis=child_axis, radial=child_radial)
    mate = mate_axes(provider, consumer)
    model.articulation(
        name,
        ArticulationType.REVOLUTE,
        parent=parent,
        child=child,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(lower=lower, upper=upper, effort=effort, velocity=velocity),
        mimic=mimic,
        meta=meta or {},
    )
    register_interface_mate(model, name, mate)


def _spine_polygon(r: ResolvedConfig, segments: int = 40):
    """Centre strip clipped out of the full round top."""
    hx = r.hinge_offset_m
    xs = [-hx + 2.0 * hx * i / segments for i in range(segments + 1)]
    half = [math.sqrt(max(r.top_radius_m**2 - x * x, 1e-6)) for x in xs]
    return [(x, h) for x, h in zip(xs, half)] + [
        (x, -h) for x, h in zip(reversed(xs), reversed(half))
    ]


def _leaf_polygon(r: ResolvedConfig, segments: int = 44):
    """One semicircular leaf in its hinge-local frame, extending along +X."""
    hx = r.hinge_offset_m
    span = r.leaf_reach_m - SEAM
    us = [SEAM + span * i / segments for i in range(segments + 1)]
    half = [math.sqrt(max(r.top_radius_m**2 - (hx + u) ** 2, 0.0)) for u in us]
    top = list(zip(us, half))
    bottom = [(u, -h) for u, h in zip(reversed(us), reversed(half))]
    return top + bottom[1:]


# --- frame ------------------------------------------------------------------
def _build_frame(model: ArticulatedObject, r: ResolvedConfig, mats: dict[str, str]):
    frame = model.part("table_frame", meta={"role": "table_frame"})
    frame.visual(
        mesh_from_geometry(
            ExtrudeGeometry(_spine_polygon(r), TOP_T, center=True), "spine_slab_mesh"
        ),
        origin=Origin(xyz=(0.0, 0.0, r.top_z)),
        material=mats["wood"],
        name=f"frame_build__{r.frame_build}__spine_slab", material_class_id=("wood.bamboo" if r.palette_style in {"warm_oak", "bamboo", "walnut"} else "wood.natural_generic"),
    )
    # Steel spine rails and end uprights.
    for side, sx in enumerate((-1.0, 1.0)):
        frame.visual(
            Box((0.026, 2.0 * r.upright_y + 0.040, RAIL_H)),
            origin=Origin(
                xyz=(sx * (r.hinge_offset_m - 0.020), 0.0, r.under_z - RAIL_H * 0.5 + MOUNT)
            ),
            material=mats["steel"],
            name=f"spine_rail_{side}", material_class_id="metal.steel_bare",
        )
    glide_z = 0.0 if r.foot_build in ("fixed_glide", "pad_foot") else 2.0 * CASTER_R
    # Two centre posts at the ends of the spine, each standing on a cross foot
    # bar; the whole quarter-annulus a gate sweeps through is left free.
    for end, sy in enumerate((-1.0, 1.0)):
        uy = sy * r.upright_y
        base_z = glide_z + (0.014 if glide_z == 0.0 else 0.056)
        height = r.under_z - base_z
        frame.visual(
            Box((0.046, 0.046, height)),
            origin=Origin(xyz=(0.0, uy, base_z + height * 0.5)),
            material=mats["steel"],
            name=f"frame_end_post_{end}", material_class_id="metal.steel_bare",
        )
        frame.visual(
            Box((2.0 * r.foot_x_m + 0.050, 0.038, 0.028)),
            origin=Origin(xyz=(0.0, uy, base_z + 0.014)),
            material=mats["steel"],
            name=f"frame_foot_bar_{end}", material_class_id="metal.steel_bare",
        )
        frame.visual(
            Box((0.040, 0.040, r.under_z - base_z - 0.060)),
            origin=Origin(
                xyz=(0.0, uy - sy * 0.030, base_z + 0.030 + (r.under_z - base_z - 0.060) * 0.5)
            ),
            material=mats["steel"],
            name=f"frame_end_brace_{end}", material_class_id="metal.steel_bare",
        )
    kind = r.frame_build
    shelf_half = max(r.pivot_x_m - 0.030, 0.020)
    if kind in ("shelf_spine", "double_shelf"):
        levels = (0.34,) if kind == "shelf_spine" else (0.26, 0.50)
        for level_index, frac in enumerate(levels):
            z = glide_z + (r.under_z - glide_z) * frac
            frame.visual(
                Box((2.0 * shelf_half, 2.0 * r.upright_y - 0.010, 0.016)),
                origin=Origin(xyz=(0.0, 0.0, z)),
                material=mats["wood"],
                name=f"frame_build__{kind}__shelf_{level_index}", material_class_id=("wood.bamboo" if r.palette_style in {"warm_oak", "bamboo", "walnut"} else "wood.natural_generic"),
            )
            frame.visual(
                Box((2.0 * shelf_half + 0.006, 0.014, 0.026)),
                origin=Origin(xyz=(0.0, r.upright_y - 0.010, z + 0.012)),
                material=mats["edge"],
                name=f"frame_build__{kind}__shelf_rail_{level_index}", material_class_id=("wood.bamboo" if r.palette_style in {"warm_oak", "bamboo", "walnut"} else "wood.natural_generic"),
            )
    return frame


def _build_casters(model: ArticulatedObject, frame, r: ResolvedConfig, mats: dict[str, str]):
    """Swivelling casters, each with a vertical swivel and a rolling wheel."""
    kind = r.foot_build
    for i, (sx, sy) in enumerate(((-1.0, -1.0), (1.0, -1.0), (-1.0, 1.0), (1.0, 1.0))):
        ux = sx * r.foot_x_m
        uy = sy * r.upright_y
        fork = model.part(
            f"foot_build__{kind}__caster_fork_{i}", meta={"role": "caster_fork", "index": i}
        )
        fork.visual(
            Cylinder(radius=0.014, length=0.020),
            origin=Origin(xyz=(0.0, 0.0, -0.0105)),
            material=mats["hardware"],
            name=f"foot_build__{kind}__fork_stem_{i}", material_class_id="metal.brushed_silver",
        )
        for cheek, cy in enumerate((-1.0, 1.0)):
            fork.visual(
                Box((0.030, 0.008, 0.0655)),
                origin=Origin(xyz=(-0.014, cy * 0.0165, -0.0423)),
                material=mats["hardware"],
                name=f"foot_build__{kind}__fork_cheek_{i}_{cheek}", material_class_id="metal.brushed_silver",
            )
        fork.visual(
            Box((0.044, 0.041, 0.014)),
            origin=Origin(xyz=(-0.010, 0.0, -0.0165)),
            material=mats["hardware"],
            name=f"foot_build__{kind}__fork_yoke_{i}", material_class_id="metal.brushed_silver",
        )
        swivel_z = 2.0 * CASTER_R + 0.056 - 0.015
        _axis_joint(
            model,
            name=f"frame_to_caster_swivel_{i}",
            parent=frame,
            child=fork,
            point=(ux, uy, swivel_z),
            axis=(0.0, 0.0, 1.0),
            radial=(1.0, 0.0, 0.0),
            child_axis=(0.0, 0.0, 1.0),
            child_radial=(1.0, 0.0, 0.0),
            lower=-math.pi,
            upper=math.pi,
            effort=6.0,
            velocity=3.0,
            meta={"positive_motion": "swivels the caster fork"},
        )
        wheel = model.part(
            f"foot_build__{kind}__caster_wheel_{i}", meta={"role": "caster_wheel", "index": i}
        )
        wheel.visual(
            Cylinder(radius=CASTER_R, length=0.024),
            origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["rubber"],
            name=f"foot_build__{kind}__wheel_tyre_{i}", material_class_id="rubber.smooth_plain",
        )
        wheel.visual(
            Cylinder(radius=CASTER_R * 0.45, length=0.028),
            origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["hardware"],
            name=f"foot_build__{kind}__wheel_hub_{i}", material_class_id="metal.brushed_silver",
        )
        _axis_joint(
            model,
            name=f"caster_{i}_roll",
            parent=fork,
            child=wheel,
            point=(-0.014, 0.0, CASTER_R - swivel_z),
            axis=(0.0, 1.0, 0.0),
            radial=(1.0, 0.0, 0.0),
            lower=-math.pi,
            upper=math.pi,
            effort=4.0,
            velocity=6.0,
            meta={"positive_motion": "rolls the caster wheel forward"},
        )
        if kind == "braked_caster":
            pedal = model.part(
                f"foot_build__{kind}__brake_pedal_{i}", meta={"role": "brake_pedal", "index": i}
            )
            pedal.visual(
                Box((0.034, 0.022, 0.009)),
                origin=Origin(xyz=(0.017, 0.0, 0.0)),
                material=mats["hardware"],
                name=f"foot_build__{kind}__pedal_plate_{i}", material_class_id="metal.brushed_silver",
            )
            pedal.visual(
                Box((0.012, 0.020, 0.012)),
                origin=Origin(xyz=(0.032, 0.0, -0.006)),
                material=mats["rubber"],
                name=f"foot_build__{kind}__pedal_shoe_{i}", material_class_id="rubber.smooth_plain",
            )
            _axis_joint(
                model,
                name=f"caster_{i}_brake",
                parent=fork,
                child=pedal,
                point=(-0.014, 0.030, -0.010),
                axis=(0.0, 1.0, 0.0),
                radial=(1.0, 0.0, 0.0),
                lower=0.0,
                upper=0.55,
                effort=6.0,
                velocity=2.0,
                meta={"positive_motion": "swings the brake pedal down onto the tyre"},
            )


# --- foot candidates --------------------------------------------------------
def _foot_stations(r: ResolvedConfig):
    for i, (sx, sy) in enumerate(((-1.0, -1.0), (1.0, -1.0), (-1.0, 1.0), (1.0, 1.0))):
        yield i, sx * r.foot_x_m, sy * r.upright_y


def _foot_build_fixed_glide_build(model, frame, r: ResolvedConfig, mats) -> None:
    """Small rubber glides let the frame stand straight on the floor."""
    for i, ux, uy in _foot_stations(r):
        frame.visual(
            Box((0.052, 0.052, 0.018)),
            origin=Origin(xyz=(ux, uy, 0.011)),
            material=mats["rubber"],
            name=f"foot_build__fixed_glide__floor_glide_{i}", material_class_id="rubber.smooth_plain",
        )


def _foot_build_pad_foot_build(model, frame, r: ResolvedConfig, mats) -> None:
    """Broad flat pads spreading the load along the foot bar."""
    for i, ux, uy in _foot_stations(r):
        frame.visual(
            Box((0.110, 0.060, 0.012)),
            origin=Origin(xyz=(ux, uy, 0.008)),
            material=mats["rubber"],
            name=f"foot_build__pad_foot__support_pad_{i}", material_class_id="rubber.smooth_plain",
        )
        frame.visual(
            Box((0.070, 0.044, 0.010)),
            origin=Origin(xyz=(ux, uy, 0.017)),
            material=mats["hardware"],
            name=f"foot_build__pad_foot__pad_plate_{i}", material_class_id="metal.brushed_silver",
        )


def _foot_build_swivel_caster_build(model, frame, r: ResolvedConfig, mats) -> None:
    """Swivelling casters: a vertical swivel over a rolling wheel."""
    _caster_plates(frame, r, mats)
    _build_casters(model, frame, r, mats)


def _foot_build_braked_caster_build(model, frame, r: ResolvedConfig, mats) -> None:
    """The same casters plus a brake pedal that swings onto each tyre."""
    _caster_plates(frame, r, mats)
    _build_casters(model, frame, r, mats)


def _caster_plates(frame, r: ResolvedConfig, mats) -> None:
    for i, ux, uy in _foot_stations(r):
        frame.visual(
            Box((0.060, 0.060, 0.018)),
            origin=Origin(xyz=(ux, uy, 2.0 * CASTER_R + 0.056 - 0.006)),
            material=mats["hardware"],
            name=f"foot_build__{r.foot_build}__caster_plate_{i}", material_class_id="metal.brushed_silver",
        )


_FOOT_BUILDERS = {
    "fixed_glide": _foot_build_fixed_glide_build,
    "pad_foot": _foot_build_pad_foot_build,
    "swivel_caster": _foot_build_swivel_caster_build,
    "braked_caster": _foot_build_braked_caster_build,
}


def _build_feet(model: ArticulatedObject, frame, r: ResolvedConfig, mats: dict[str, str]) -> None:
    _FOOT_BUILDERS[r.foot_build](model, frame, r, mats)


# --- leaves -----------------------------------------------------------------
def _build_leaf(model: ArticulatedObject, frame, r: ResolvedConfig, mats, index: int):
    side = 1.0 if index == 0 else -1.0
    leaf = model.part(
        f"frame_build__{r.frame_build}__drop_leaf_{index}",
        meta={"role": "drop_leaf", "index": index},
    )
    leaf.visual(
        mesh_from_geometry(
            ExtrudeGeometry(_leaf_polygon(r), TOP_T, center=True), f"leaf_slab_mesh_{index}"
        ),
        origin=Origin(xyz=(0.0, 0.0, HINGE_DROP)),
        material=mats["wood"],
        name=f"leaf_slab_{index}", material_class_id=("wood.bamboo" if r.palette_style in {"warm_oak", "bamboo", "walnut"} else "wood.natural_generic"),
    )
    # Alternating butt-hinge knuckles below the seam, three per leaf.
    for k, frac in enumerate((-0.55, 0.0, 0.55)):
        y = frac * r.upright_y
        leaf.visual(
            Cylinder(radius=0.008, length=0.070),
            origin=Origin(xyz=(0.0, y, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["hardware"],
            name=f"leaf_hinge_knuckle_{index}_{k}", material_class_id="metal.brushed_silver",
        )
        leaf.visual(
            Box((0.040, 0.070, 0.007)),
            origin=Origin(xyz=(0.022, y, 0.008)),
            material=mats["hardware"],
            name=f"leaf_hinge_plate_{index}_{k}", material_class_id="metal.brushed_silver",
        )
        leaf.visual(
            Box((0.016, 0.070, HINGE_DROP - 0.008 + MOUNT)),
            origin=Origin(xyz=(0.012, y, 0.008 + (HINGE_DROP - 0.008 + MOUNT) * 0.5)),
            material=mats["hardware"],
            name=f"leaf_hinge_web_{index}_{k}", material_class_id="metal.brushed_silver",
        )
    # Batten stiffening the curved leaf edge, outboard of every support pad.
    batten_lo = r.support_reach_m + 0.040
    batten_hi = max(r.leaf_reach_m - 0.030, batten_lo + 0.020)
    leaf.visual(
        Box((batten_hi - batten_lo, 0.048, 0.024)),
        origin=Origin(
            xyz=((batten_lo + batten_hi) * 0.5, 0.0, HINGE_DROP - TOP_T * 0.5 - 0.012 + MOUNT)
        ),
        material=mats["edge"],
        name=f"leaf_batten_{index}", material_class_id=("wood.bamboo" if r.palette_style in {"warm_oak", "bamboo", "walnut"} else "wood.natural_generic"),
    )
    _axis_joint(
        model,
        name=f"frame_to_leaf_{index}",
        parent=frame,
        child=leaf,
        point=(side * r.hinge_offset_m, 0.0, r.hinge_z),
        axis=(0.0, side, 0.0),
        radial=(side, 0.0, 0.0),
        lower=0.0,
        upper=LEAF_FOLD,
        effort=40.0,
        velocity=1.0,
        meta={"positive_motion": f"drops leaf {index} beside the frame"},
    )
    # Root knuckles on the frame interleave with the leaf knuckles.
    for k, frac in enumerate((-0.82, -0.28, 0.28, 0.82)):
        y = frac * r.upright_y
        frame.visual(
            Cylinder(radius=0.008, length=0.070),
            origin=Origin(
                xyz=(side * r.hinge_offset_m, y, r.hinge_z), rpy=(math.pi / 2.0, 0.0, 0.0)
            ),
            material=mats["hardware"],
            name=f"root_hinge_knuckle_{index}_{k}", material_class_id="metal.brushed_silver",
        )
        frame.visual(
            Box((0.040, 0.070, 0.007)),
            origin=Origin(xyz=(side * (r.hinge_offset_m - 0.022), y, r.hinge_z + 0.008)),
            material=mats["hardware"],
            name=f"root_hinge_plate_{index}_{k}", material_class_id="metal.brushed_silver",
        )
        frame.visual(
            Box((0.016, 0.070, HINGE_DROP - 0.008 + MOUNT)),
            origin=Origin(
                xyz=(
                    side * (r.hinge_offset_m - 0.012),
                    y,
                    r.hinge_z + 0.008 + (HINGE_DROP - 0.008 + MOUNT) * 0.5,
                )
            ),
            material=mats["hardware"],
            name=f"root_hinge_web_{index}_{k}", material_class_id="metal.brushed_silver",
        )
    return leaf


# --- leaf support candidates ------------------------------------------------
# Every support pivots on a vertical axis in the frame at (+/-pivot_x, station)
# and swings out under its leaf.  Local +X points outward across the leaf.
def _support_build_swing_gate_build(support, r, mats, tag: str) -> None:
    x0, reach, drop = SUPPORT_X0, r.support_reach_m, r.support_pivot_z - 0.020
    _rod(
        support,
        (x0, 0.0, 0.0),
        (reach, 0.0, 0.0),
        0.011,
        mats["steel"],
        f"support_build__swing_gate__top_rail_{tag}",
    )
    _rod(
        support,
        (reach, 0.0, 0.0),
        (reach, 0.0, -drop),
        0.011,
        mats["steel"],
        f"support_build__swing_gate__outer_stile_{tag}",
    )
    _rod(
        support,
        (x0, 0.0, -drop * 0.55),
        (reach, 0.0, -drop * 0.55),
        0.009,
        mats["steel"],
        f"support_build__swing_gate__mid_rail_{tag}",
    )
    _rod(
        support,
        (x0, 0.0, 0.0),
        (x0, 0.0, -drop * 0.55),
        0.010,
        mats["steel"],
        f"support_build__swing_gate__inner_stile_{tag}",
    )
    support.visual(
        Box((0.048, 0.048, 0.014)),
        origin=Origin(xyz=(reach, 0.0, -drop - 0.005)),
        material=mats["rubber"],
        name=f"support_build__swing_gate__foot_pad_{tag}", material_class_id="rubber.smooth_plain",
    )


def _support_build_arc_gate_build(support, r, mats, tag: str) -> None:
    x0, reach, drop = SUPPORT_X0, r.support_reach_m, r.support_pivot_z - 0.020
    steps = 6
    span = reach - x0
    for i in range(steps):
        a0 = math.pi * 0.5 * i / steps
        a1 = math.pi * 0.5 * (i + 1) / steps
        p0 = (x0 + span * math.sin(a0), 0.0, -drop * 0.30 * (1.0 - math.cos(a0)))
        p1 = (x0 + span * math.sin(a1), 0.0, -drop * 0.30 * (1.0 - math.cos(a1)))
        _rod(support, p0, p1, 0.010, mats["steel"], f"support_build__arc_gate__arc_seg_{tag}_{i}")
    _rod(
        support,
        (reach, 0.0, -drop * 0.30),
        (reach, 0.0, -drop),
        0.011,
        mats["steel"],
        f"support_build__arc_gate__outer_stile_{tag}",
    )
    _rod(
        support,
        (x0, 0.0, 0.0),
        (x0, 0.0, -drop * 0.40),
        0.010,
        mats["steel"],
        f"support_build__arc_gate__inner_stile_{tag}",
    )
    _rod(
        support,
        (x0, 0.0, -drop * 0.40),
        (reach, 0.0, -drop * 0.62),
        0.009,
        mats["steel"],
        f"support_build__arc_gate__diagonal_{tag}",
    )
    support.visual(
        Box((0.048, 0.048, 0.014)),
        origin=Origin(xyz=(reach, 0.0, -drop - 0.005)),
        material=mats["rubber"],
        name=f"support_build__arc_gate__foot_pad_{tag}", material_class_id="rubber.smooth_plain",
    )


def _support_build_cross_trestle_build(support, r, mats, tag: str) -> None:
    x0, reach, drop = SUPPORT_X0, r.support_reach_m, r.support_pivot_z - 0.020
    _rod(
        support,
        (x0, 0.0, 0.0),
        (reach, 0.0, -drop),
        0.011,
        mats["steel"],
        f"support_build__cross_trestle__x_leg_{tag}_0",
    )
    _rod(
        support,
        (reach, 0.0, 0.0),
        (x0, 0.0, -drop),
        0.011,
        mats["steel"],
        f"support_build__cross_trestle__x_leg_{tag}_1",
    )
    _rod(
        support,
        (x0, 0.0, 0.0),
        (reach, 0.0, 0.0),
        0.010,
        mats["steel"],
        f"support_build__cross_trestle__top_rail_{tag}",
    )
    support.visual(
        Cylinder(radius=0.010, length=0.030),
        origin=Origin(xyz=((x0 + reach) * 0.5, 0.0, -drop * 0.5), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["hardware"],
        name=f"support_build__cross_trestle__cross_pin_{tag}", material_class_id="metal.brushed_silver",
    )
    for i, x in enumerate((x0, reach)):
        support.visual(
            Box((0.048, 0.048, 0.014)),
            origin=Origin(xyz=(x, 0.0, -drop - 0.005)),
            material=mats["rubber"],
            name=f"support_build__cross_trestle__foot_pad_{tag}_{i}", material_class_id="rubber.smooth_plain",
        )


def _support_build_wall_bracket_build(support, r, mats, tag: str) -> None:
    x0, reach = SUPPORT_X0, r.support_reach_m
    post = (reach - x0) * 0.72
    _rod(
        support,
        (x0, 0.0, 0.0),
        (reach, 0.0, 0.0),
        0.012,
        mats["steel"],
        f"support_build__wall_bracket__arm_{tag}",
    )
    _rod(
        support,
        (x0, 0.0, -post),
        (reach - 0.020, 0.0, -0.006),
        0.010,
        mats["steel"],
        f"support_build__wall_bracket__diagonal_{tag}",
    )
    _rod(
        support,
        (x0, 0.0, 0.006),
        (x0, 0.0, -post),
        0.012,
        mats["steel"],
        f"support_build__wall_bracket__post_{tag}",
    )
    support.visual(
        Box((0.030, 0.044, 0.012)),
        origin=Origin(xyz=(reach - 0.014, 0.0, 0.010)),
        material=mats["hardware"],
        name=f"support_build__wall_bracket__bearing_pad_{tag}", material_class_id="metal.brushed_silver",
    )


def _support_build_latch_gate_build(support, r, mats, tag: str) -> None:
    _support_build_swing_gate_build(support, r, mats, tag)
    reach = r.support_reach_m
    support.visual(
        Box((0.056, 0.020, 0.026)),
        origin=Origin(xyz=(reach * 0.5 + SUPPORT_X0 * 0.5, 0.0, 0.014)),
        material=mats["hardware"],
        name=f"support_build__latch_gate__latch_body_{tag}", material_class_id="metal.brushed_silver",
    )
    support.visual(
        Cylinder(radius=0.008, length=0.034),
        origin=Origin(
            xyz=(reach * 0.5 + SUPPORT_X0 * 0.5, 0.0, 0.024), rpy=(math.pi / 2.0, 0.0, 0.0)
        ),
        material=mats["hardware"],
        name=f"support_build__latch_gate__latch_hook_{tag}", material_class_id="metal.brushed_silver",
    )


def _support_build_telescoping_brace_build(support, r, mats, tag: str) -> None:
    _support_build_swing_gate_build(support, r, mats, tag)
    reach = r.support_reach_m
    drop = r.support_pivot_z - 0.020
    mid = SUPPORT_X0 + (reach - SUPPORT_X0) * 0.42
    for cheek, sy in enumerate((-1.0, 1.0)):
        support.visual(
            Box((0.070, 0.008, 0.030)),
            origin=Origin(xyz=(mid, sy * 0.0125, -drop * 0.30)),
            material=mats["hardware"],
            name=f"support_build__telescoping_brace__brace_sleeve_{tag}_{cheek}", material_class_id="metal.brushed_silver",
        )
    support.visual(
        Box((0.070, 0.033, 0.007)),
        origin=Origin(xyz=(mid, 0.0, -drop * 0.30 - 0.0115)),
        material=mats["hardware"],
        name=f"support_build__telescoping_brace__sleeve_floor_{tag}", material_class_id="metal.brushed_silver",
    )
    support.visual(
        Box((0.014, 0.033, 0.030)),
        origin=Origin(xyz=(mid - 0.042, 0.0, -drop * 0.30)),
        material=mats["hardware"],
        name=f"support_build__telescoping_brace__sleeve_stop_{tag}", material_class_id="metal.brushed_silver",
    )
    _rod(
        support,
        (SUPPORT_X0, 0.0, -drop * 0.30),
        (mid - 0.038, 0.0, -drop * 0.30),
        0.009,
        mats["hardware"],
        f"support_build__telescoping_brace__sleeve_strut_{tag}",
    )


_SUPPORT_BUILDERS = {
    "swing_gate": _support_build_swing_gate_build,
    "arc_gate": _support_build_arc_gate_build,
    "cross_trestle": _support_build_cross_trestle_build,
    "telescoping_brace": _support_build_telescoping_brace_build,
    "wall_bracket": _support_build_wall_bracket_build,
    "latch_gate": _support_build_latch_gate_build,
}


def _build_supports(model: ArticulatedObject, frame, r: ResolvedConfig, mats) -> list:
    units = []
    for side_index, side in enumerate((1.0, -1.0)):
        for j, y in enumerate(r.support_y):
            tag = f"{side_index}_{j}"
            support = model.part(
                f"support_build__{r.support_build}__unit_{tag}",
                meta={"role": "leaf_support", "index": len(units)},
            )
            _SUPPORT_BUILDERS[r.support_build](support, r, mats, tag)
            _rod(
                support,
                (0.006, 0.0, 0.0),
                (SUPPORT_X0 + 0.004, 0.0, 0.0),
                0.011,
                mats["hardware"],
                f"support_hub_stub_{tag}",
            )
            # The support hangs from a bearing plate let into the spine rail;
            # the plate spans its own vertical pivot axis.
            plate_z = r.support_pivot_z + 0.0315
            frame.visual(
                Box((0.056, 0.056, 0.014)),
                origin=Origin(xyz=(side * r.pivot_x_m, y, plate_z)),
                material=mats["hardware"],
                name=f"support_pivot_plate_{tag}", material_class_id="metal.brushed_silver",
            )
            post_h = r.frame_drop_m - plate_z + 0.010
            frame.visual(
                Box((0.032, 0.032, post_h)),
                origin=Origin(xyz=(side * r.pivot_x_m, y, plate_z + post_h * 0.5)),
                material=mats["steel"],
                name=f"support_pivot_post_{tag}", material_class_id="metal.steel_bare",
            )
            support.visual(
                Cylinder(radius=0.014, length=0.048),
                origin=Origin(),
                material=mats["hardware"],
                name=f"support_pivot_hub_{tag}", material_class_id="metal.brushed_silver",
            )
            # Stow toward this station's own end of the table.  The axis stays
            # +Z so the child frame keeps its own up direction; the sense comes
            # from the limit range and the mimic multiplier instead.
            toward_end = 1.0 if (side * y) >= 0.0 else -1.0
            _axis_joint(
                model,
                name=f"frame_to_leaf_support_{tag}",
                parent=frame,
                child=support,
                point=(side * r.pivot_x_m, y, r.support_pivot_z),
                axis=(0.0, 0.0, 1.0),
                radial=(side, 0.0, 0.0),
                child_axis=(0.0, 0.0, 1.0),
                child_radial=(1.0, 0.0, 0.0),
                lower=0.0 if toward_end > 0 else -SUPPORT_SWING,
                upper=SUPPORT_SWING if toward_end > 0 else 0.0,
                effort=30.0,
                velocity=1.4,
                mimic=Mimic(
                    joint=f"frame_to_leaf_{side_index}",
                    multiplier=toward_end * SUPPORT_SWING / LEAF_FOLD,
                    offset=0.0,
                ),
                meta={"positive_motion": "swings the support back in as its leaf drops"},
            )
            units.append(support)
    return units


def _build_telescoping_locks(model: ArticulatedObject, supports, r: ResolvedConfig, mats) -> None:
    """The prismatic lock rod that distinguishes the telescoping brace."""
    reach = r.support_reach_m
    drop = r.support_pivot_z - 0.020
    for index, support in enumerate(supports):
        tag = support.name.rsplit("__unit_", 1)[1]
        rod = model.part(
            f"support_build__telescoping_brace__lock_rod_{tag}",
            meta={"role": "brace_rod", "index": index},
        )
        rod.visual(
            Box((0.090, 0.018, 0.018)),
            origin=Origin(xyz=(0.045, 0.0, 0.0)),
            material=mats["steel"],
            name=f"support_build__telescoping_brace__lock_rod_bar_{tag}", material_class_id="metal.steel_bare",
        )
        rod.visual(
            Box((0.014, 0.018, 0.022)),
            origin=Origin(xyz=(0.090, 0.0, 0.0)),
            material=mats["hardware"],
            name=f"support_build__telescoping_brace__lock_tip_{tag}", material_class_id="metal.brushed_silver",
        )
        model.articulation(
            f"support_{tag}_brace_extend",
            ArticulationType.PRISMATIC,
            parent=support,
            child=rod,
            origin=Origin(
                xyz=(
                    SUPPORT_X0 + (reach - SUPPORT_X0) * 0.42 - 0.030,
                    0.0,
                    -drop * 0.30,
                )
            ),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(
                lower=0.0,
                upper=max(
                    0.020,
                    reach - 0.080 - (SUPPORT_X0 + (reach - SUPPORT_X0) * 0.42) - 0.030,
                ),
                effort=40.0,
                velocity=0.3,
            ),
            meta={"positive_motion": "telescopes the lock rod out of its sleeve"},
        )


# --- assembly ---------------------------------------------------------------
def build_picturex_0611_folding_table5(
    config: Config | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config or Config())
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={
            "category": "pictureX_0611_Folding_table5",
            "slot_choices": slot_choices_for_config(r),
            "mechanism": "gateleg drop-leaf table with swing-out leaf supports",
        },
    )
    mats = _materials(model, r)
    frame = _build_frame(model, r, mats)
    for index in range(2):
        _build_leaf(model, frame, r, mats, index)
    supports = _build_supports(model, frame, r, mats)
    if r.support_build == "telescoping_brace":
        _build_telescoping_locks(model, supports, r, mats)
    _build_feet(model, frame, r, mats)

    # The supports are mimicked to their own leaf, so only the leaf hinges are
    # free; posing a support independently would contradict the linkage.
    leaf_joints = [f"frame_to_leaf_{i}" for i in range(2)]
    model.meta["risk_poses"] = (
        {name: 0.0 for name in leaf_joints},
        {name: LEAF_FOLD for name in leaf_joints},
        {leaf_joints[0]: LEAF_FOLD, leaf_joints[1]: 0.0},
    )
    model.meta["coupled_joint_pairs"] = ((leaf_joints[0], leaf_joints[1]),)
    return model


def build_seeded_picturex_0611_folding_table5(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_picturex_0611_folding_table5(config_from_seed(seed), assets=assets)


# --- authored tests ---------------------------------------------------------
def _parts_by_role(model: ArticulatedObject, role: str):
    return [p for p in model.parts if p.meta.get("role") == role]


def run_picturex_0611_folding_table5_tests(model: ArticulatedObject, config: Config) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)

    frames = _parts_by_role(model, "table_frame")
    leaves = _parts_by_role(model, "drop_leaf")
    supports = _parts_by_role(model, "leaf_support")
    joints = {j.name: j for j in model.articulations}
    leaf_joints = [joints.get(f"frame_to_leaf_{i}") for i in range(2)]

    ctx.check(
        "category_anchor: both leaves drop beside the fixed spine",
        len(frames) == 1
        and len(leaves) == 2
        and bool(model.root_parts())
        and model.root_parts()[0].name == "table_frame"
        and all(
            j is not None
            and j.articulation_type == ArticulationType.REVOLUTE
            and j.parent == "table_frame"
            and tuple(round(abs(v), 6) for v in j.axis) == (0.0, 1.0, 0.0)
            and j.motion_limits is not None
            and abs(j.motion_limits.upper - LEAF_FOLD) < 1e-6
            for j in leaf_joints
        ),
        details=f"leaves={len(leaves)}",
    )

    support_joints = [
        joints.get(f"frame_to_leaf_support_{s}_{j}")
        for s in range(2)
        for j in range(r.support_per_leaf)
    ]
    # Preflight never materialises meshes, so every AABB is read from a primitive.
    pad_ok = True
    pads = []
    for s in range(2):
        for j in range(r.support_per_leaf):
            tag = f"{s}_{j}"
            elem = {
                "swing_gate": f"support_build__swing_gate__foot_pad_{tag}",
                "arc_gate": f"support_build__arc_gate__foot_pad_{tag}",
                "cross_trestle": f"support_build__cross_trestle__foot_pad_{tag}_1",
                "telescoping_brace": f"support_build__swing_gate__foot_pad_{tag}",
                "latch_gate": f"support_build__swing_gate__foot_pad_{tag}",
                "wall_bracket": f"support_build__wall_bracket__bearing_pad_{tag}",
            }[r.support_build]
            part = next((p for p in supports if p.name.endswith(f"__unit_{tag}")), None)
            box = ctx.part_element_world_aabb(part, elem=elem) if part else None
            pads.append(None if box is None else round(box[1][0], 4))
            if box is None or abs(box[1][0]) < r.hinge_offset_m + 0.070:
                pad_ok = False
    ctx.check(
        "category_anchor: the swing-out supports reach under a raised leaf",
        len(supports) == r.support_total
        and pad_ok
        and all(
            j is not None
            and j.articulation_type == ArticulationType.REVOLUTE
            and j.parent == "table_frame"
            and tuple(round(abs(v), 6) for v in j.axis) == (0.0, 0.0, 1.0)
            and j.motion_limits is not None
            and abs(j.motion_limits.upper - j.motion_limits.lower) > 1.0
            for j in support_joints
        ),
        details=f"supports={len(supports)} pad_x={pads} hinge={r.hinge_offset_m}",
    )

    visual_names = {v.name or "" for p in model.parts for v in p.visuals}
    support_marker = {
        "swing_gate": "swing_gate__mid_rail_",
        "arc_gate": "arc_gate__arc_seg_",
        "cross_trestle": "cross_trestle__cross_pin_",
        "telescoping_brace": "telescoping_brace__sleeve_floor_",
        "wall_bracket": "wall_bracket__diagonal_",
        "latch_gate": "latch_gate__latch_hook_",
    }[r.support_build]
    ctx.check(
        "category_anchor: support_build identity",
        any(support_marker in n for n in visual_names),
        details=f"support_build={r.support_build}",
    )

    foot_marker = {
        "fixed_glide": "fixed_glide__floor_glide_",
        "pad_foot": "pad_foot__support_pad_",
        "swivel_caster": "swivel_caster__wheel_tyre_",
        "braked_caster": "braked_caster__pedal_shoe_",
    }[r.foot_build]
    ctx.check(
        "category_anchor: foot_build identity",
        any(foot_marker in n for n in visual_names)
        and len(_parts_by_role(model, "caster_wheel")) == r.caster_count,
        details=f"foot_build={r.foot_build} casters={r.caster_count}",
    )

    frame_marker = {
        "open_spine": "frame_build__open_spine__spine_slab",
        "shelf_spine": "shelf_spine__shelf_0",
        "double_shelf": "double_shelf__shelf_1",
    }[r.frame_build]
    ctx.check(
        "category_anchor: frame_build identity",
        any(frame_marker in n for n in visual_names)
        and (r.frame_build != "open_spine" or not any("__shelf_" in n for n in visual_names)),
        details=f"frame_build={r.frame_build}",
    )

    # Decisive motion evidence: leaf 0 really drops beside the frame.
    leaf = leaves[0]
    batten = "leaf_batten_0"
    rest = ctx.part_element_world_aabb(leaf, elem=batten)
    with ctx.pose({leaf_joints[0]: LEAF_FOLD}):
        folded = ctx.part_element_world_aabb(leaf, elem=batten)
    ctx.check(
        "leaf 0 drops beside the frame",
        rest is not None
        and folded is not None
        and folded[0][2] < rest[0][2] - r.leaf_reach_m * 0.55
        and folded[1][0] < rest[1][0] - r.leaf_reach_m * 0.55,
        details=f"rest={rest} folded={folded}",
    )

    ctx.check(
        "support stations are pitched along the spine clear of the leaf hinges",
        len(r.support_y) == r.support_per_leaf
        and 0.0 < r.pivot_x_m < r.hinge_offset_m
        and r.pivot_x_m + r.support_reach_m > r.hinge_offset_m + 0.090
        and r.pivot_x_m + r.support_reach_m < r.hinge_offset_m + r.leaf_reach_m - 0.030
        and all(abs(y) <= r.upright_y * 0.50 + 1e-9 for y in r.support_y),
        details=f"stations={r.support_y} pivot_x={r.pivot_x_m} reach={r.support_reach_m}",
    )

    ctx.check(
        "domain choices recorded on the model",
        model.meta.get("slot_choices") == slot_choices_for_config(r),
    )
    return ctx.report()


TEMPLATE_CORNERS = (
    corner_case(
        "narrow_spine_widest_top_two_supports",
        {
            "support_build": "cross_trestle",
            "frame_build": "double_shelf",
            "foot_build": "braked_caster",
            "support_per_leaf": 2,
            "top_diameter_m": 1.30,
            "spine_width_ratio": 0.19,
            "table_height_m": 0.78,
        },
        reason="narrowest spine with the longest leaves, two trestles a side and braked casters",
    ),
    corner_case(
        "widest_spine_smallest_top_single",
        {
            "support_build": "wall_bracket",
            "frame_build": "double_shelf",
            "support_per_leaf": 1,
            "top_diameter_m": 0.95,
            "spine_width_ratio": 0.30,
            "table_height_m": 0.70,
        },
        reason="widest spine and shortest leaf over a double-shelf carcass at the lowest height",
    ),
    corner_case(
        "telescoping_on_casters",
        {
            "support_build": "telescoping_brace",
            "frame_build": "open_spine",
            "foot_build": "swivel_caster",
            "support_per_leaf": 2,
            "top_diameter_m": 1.30,
            "spine_width_ratio": 0.30,
            "table_height_m": 0.70,
        },
        reason="four telescoping braces at full travel over swivelling casters",
    ),
    corner_case(
        "arc_gate_open_frame_tight",
        {
            "support_build": "arc_gate",
            "frame_build": "open_spine",
            "support_per_leaf": 1,
            "top_diameter_m": 0.95,
            "spine_width_ratio": 0.19,
            "table_height_m": 0.78,
        },
        reason="tallest open frame with the narrowest spine and a single arched gate a side",
    ),
)


__all__ = [
    "TEMPLATE_DOMAIN",
    "TEMPLATE_CORNERS",
    "Config",
    "ResolvedConfig",
    "config_from_seed",
    "resolve_config",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "build_picturex_0611_folding_table5",
    "build_seeded_picturex_0611_folding_table5",
    "run_picturex_0611_folding_table5_tests",
]
