# SPDX-License-Identifier: Apache-2.0

"""Self-contained hand-crank clothes wringer template.

One rigid ``frame`` root carries the enamelled top and bottom beams, the paired
side rails, the two fixed lower bearing blocks and whichever support mount is
active.  Two ``pressure_block`` bearing carriers ride PRISMATIC (+z) on the
frame and journal the ``upper_roller``; the ``lower_roller`` is journalled in
the frame's own bearing blocks.  Every bearing block and clamp boss is a
CadQuery solid with a real bore, so an axle is retained by a 0.8 mm running fit
instead of an overlap allowance.  ``crank_drive`` turns CONTINUOUS about the
upper roller axis and both roller spins mimic it -- the lower one reversed --
so the nip counter-rotates.

Five component slots vary independently: four genuine support structures, four
pressure mechanisms, fixed or folding crank topology, fixed apron or folding
feed shelf, and one indexed roller-bank implementation.  ``roller_count`` is
the only multiplicity and emits either two or three real articulated rollers.
The top beam, bearing rows and side-frame height derive from that count.  No
source-replay import, compatibility gate, motion clamping, or overlap allowance.
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
    Mimic,
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

SupportMount = Literal[
    "classic_boss_clamps",
    "reinforced_table_clamps",
    "freestanding_floor_frame",
    "wall_bench_bracket",
]
PressureMechanism = Literal[
    "centre_screw",
    "overhead_screw_bridge",
    "spring_loaded_bridge",
    "dual_handwheels",
]
CrankStyle = Literal["fixed_bent_crank", "folding_park_crank"]
FeedModule = Literal["plain_front_apron", "fold_down_shelf"]
RollerBank = Literal["indexed_parallel_roller_bank"]
PaletteStyle = Literal["turquoise_enamel", "cream_enamel", "cast_iron", "galvanised"]

SUPPORT_MOUNTS: tuple[SupportMount, ...] = (
    "classic_boss_clamps",
    "reinforced_table_clamps",
    "freestanding_floor_frame",
    "wall_bench_bracket",
)
PRESSURE_MECHANISMS: tuple[PressureMechanism, ...] = (
    "centre_screw",
    "overhead_screw_bridge",
    "spring_loaded_bridge",
    "dual_handwheels",
)
CRANK_STYLES: tuple[CrankStyle, ...] = ("fixed_bent_crank", "folding_park_crank")
FEED_MODULES: tuple[FeedModule, ...] = ("plain_front_apron", "fold_down_shelf")
ROLLER_BANKS: tuple[RollerBank, ...] = ("indexed_parallel_roller_bank",)
ROLLER_COUNTS = (2, 3)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "turquoise_enamel",
    "cream_enamel",
    "cast_iron",
    "galvanised",
)


TEMPLATE_DOMAIN = TemplateDomain(
    slots=(
        component_slot("support_mount", SUPPORT_MOUNTS),
        component_slot("pressure_mechanism", PRESSURE_MECHANISMS),
        component_slot("crank_style", CRANK_STYLES),
        component_slot("feed_module", FEED_MODULES),
        component_slot("roller_bank", ROLLER_BANKS),
        multiplicity_slot("roller_count", ROLLER_COUNTS, item_slot="roller_bank"),
    )
)


PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "turquoise_enamel": {
        "enamel": (0.12, 0.65, 0.67, 1.0),
        "enamel_dark": (0.08, 0.48, 0.50, 1.0),
        "roller": (0.93, 0.94, 0.90, 1.0),
        "dark": (0.035, 0.038, 0.040, 1.0),
        "steel": (0.16, 0.18, 0.19, 1.0),
        "bright": (0.72, 0.75, 0.76, 1.0),
    },
    "cream_enamel": {
        "enamel": (0.90, 0.87, 0.78, 1.0),
        "enamel_dark": (0.72, 0.69, 0.60, 1.0),
        "roller": (0.88, 0.86, 0.80, 1.0),
        "dark": (0.10, 0.09, 0.08, 1.0),
        "steel": (0.28, 0.28, 0.29, 1.0),
        "bright": (0.78, 0.79, 0.80, 1.0),
    },
    "cast_iron": {
        "enamel": (0.17, 0.17, 0.18, 1.0),
        "enamel_dark": (0.10, 0.10, 0.11, 1.0),
        "roller": (0.85, 0.83, 0.76, 1.0),
        "dark": (0.06, 0.06, 0.06, 1.0),
        "steel": (0.32, 0.33, 0.34, 1.0),
        "bright": (0.70, 0.72, 0.74, 1.0),
    },
    "galvanised": {
        "enamel": (0.62, 0.65, 0.67, 1.0),
        "enamel_dark": (0.45, 0.48, 0.50, 1.0),
        "roller": (0.90, 0.90, 0.86, 1.0),
        "dark": (0.09, 0.09, 0.10, 1.0),
        "steel": (0.30, 0.32, 0.34, 1.0),
        "bright": (0.80, 0.82, 0.84, 1.0),
    },
}


# Fixed manufacturing cross-sections (surface detail, not core/raw).
BEAM_T = 0.034            # top/bottom beam thickness
RAIL_W = 0.026            # side-rail width in x
RAIL_D = 0.020            # side-rail depth in y
RAIL_Y = 0.035            # side-rail centre offset in y
AXLE_R = 0.006            # roller axle radius
NIP = 0.002               # closed nip gap between the two rubber faces
TRAVEL = 0.010            # pressure-block prismatic travel
# Radial running fit.  Under the 1 mm assembly-gap tolerance, so QC reads an
# axle as journalled (supported) rather than isolated, with no penetration.
FIT = 0.0008
# Sub-millimetre seating lap for a fitting resting on its host.
SEAT = 0.0006
BLOCK_W = 0.022           # bearing block / pressure block width in x
BLOCK_D = 0.048           # pressure block depth in y (1 mm clear of the rails)
LOWER_BLOCK_D = 0.056     # frame bearing block depth (laps the rails, same part)
GEAR_T = 0.014            # gear ring thickness in x
GEAR_TEETH = 16
CLAMP_LIFT = 0.110        # bench-clamp frame lift
STAND_LIFT = 0.300        # floor-stand frame lift
WALL_LIFT = 0.085         # wall bracket clears the bench ledge
_MOUNT_LIFT: dict[SupportMount, float] = {
    "classic_boss_clamps": CLAMP_LIFT,
    "reinforced_table_clamps": CLAMP_LIFT + 0.020,
    "freestanding_floor_frame": STAND_LIFT,
    "wall_bench_bracket": WALL_LIFT,
}


@dataclass(frozen=True)
class Config:
    support_mount: SupportMount = "classic_boss_clamps"
    pressure_mechanism: PressureMechanism = "centre_screw"
    crank_style: CrankStyle = "fixed_bent_crank"
    feed_module: FeedModule = "plain_front_apron"
    roller_bank: RollerBank = "indexed_parallel_roller_bank"
    roller_count: int = 2
    roller_length_m: float | None = None
    roller_radius_m: float | None = None
    frame_height_m: float | None = None
    palette_style: PaletteStyle = "turquoise_enamel"
    name: str = "pictureX_0611_Hand_crank_clothes_wringer"


@dataclass(frozen=True)
class ResolvedConfig:
    support_mount: SupportMount
    pressure_mechanism: PressureMechanism
    crank_style: CrankStyle
    feed_module: FeedModule
    roller_bank: RollerBank
    roller_count: int
    palette_style: PaletteStyle
    palette: dict[str, tuple[float, float, float, float]]
    roller_length_m: float
    roller_radius_m: float
    frame_height_m: float
    bearing_plane_x_m: float
    half_x: float
    nip_centre_distance_m: float
    base_z: float
    lower_axis_z: float
    upper_axis_z: float
    block_h: float
    top_beam_top_z_m: float
    top_beam_bottom_z: float
    rail_z0: float
    gear_x: float
    gear_tip_r: float
    crank_joint_x: float
    crank_arm_x0: float
    crank_throw: float
    axle_x_max: float
    name: str


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(value)))


def config_from_seed(seed: int) -> Config:
    rng = random.Random(int(seed) ^ 0x57_9A_11_C3)
    choices = TEMPLATE_DOMAIN.sample(rng)
    return Config(
        support_mount=choices["support_mount"],
        pressure_mechanism=choices["pressure_mechanism"],
        crank_style=choices["crank_style"],
        feed_module=choices["feed_module"],
        roller_bank=choices["roller_bank"],
        roller_count=choices["roller_count"],
        roller_length_m=round(rng.uniform(0.280, 0.420), 4),
        roller_radius_m=round(rng.uniform(0.024, 0.040), 4),
        frame_height_m=round(rng.uniform(0.200, 0.300), 4),
        palette_style=rng.choice(PALETTE_STYLES),
        name=f"hand_crank_clothes_wringer_seed_{int(seed)}",
    )


def resolve_config(config: Config) -> ResolvedConfig:
    TEMPLATE_DOMAIN.validate(
        {
            "support_mount": config.support_mount,
            "pressure_mechanism": config.pressure_mechanism,
            "crank_style": config.crank_style,
            "feed_module": config.feed_module,
            "roller_bank": config.roller_bank,
            "roller_count": config.roller_count,
        }
    )
    if config.palette_style not in PALETTES:
        raise ValueError(f"unsupported palette_style: {config.palette_style}")
    if config.roller_length_m is not None and not 0.280 <= float(config.roller_length_m) <= 0.420:
        raise ValueError("roller_length_m must be in [0.280, 0.420]")
    if config.roller_radius_m is not None and not 0.024 <= float(config.roller_radius_m) <= 0.040:
        raise ValueError("roller_radius_m must be in [0.024, 0.040]")
    if config.frame_height_m is not None and not 0.200 <= float(config.frame_height_m) <= 0.300:
        raise ValueError("frame_height_m must be in [0.200, 0.300]")

    length = (
        _clamp(config.roller_length_m, 0.280, 0.420)
        if config.roller_length_m is not None
        else 0.350
    )
    radius = (
        _clamp(config.roller_radius_m, 0.024, 0.040)
        if config.roller_radius_m is not None
        else 0.031
    )
    height = (
        _clamp(config.frame_height_m, 0.200, 0.300)
        if config.frame_height_m is not None
        else 0.250
    )

    bearing_x = length * 0.5 + 0.022
    half_x = bearing_x + 0.023
    centre_distance = 2.0 * radius + NIP
    block_h = 2.0 * radius

    base_z = _MOUNT_LIFT[config.support_mount]
    lower_axis = base_z + BEAM_T + 0.010 + radius
    upper_axis = lower_axis + (config.roller_count - 1) * centre_distance
    # The top beam is lifted whenever the nip plus the full pressure travel
    # would otherwise crush the headroom above the raised bearing carriers.
    # Preserve the requested continuous height response, then add one roller
    # pitch for the N=3 host before enforcing the hard pressure-headroom floor.
    height_eff = height + (config.roller_count - 2) * centre_distance
    top_top = base_z + height_eff
    beam_bottom = top_top - BEAM_T
    required_bottom = upper_axis + TRAVEL + 0.5 * block_h + 0.014
    if beam_bottom < required_bottom:
        beam_bottom = required_bottom
        top_top = beam_bottom + BEAM_T
        height_eff = top_top - base_z

    gear_x = half_x + 0.014
    gear_tip_r = 0.5 * centre_distance - 0.0015
    crank_joint_x = half_x + 0.007
    crank_arm_x0 = 0.030
    crank_throw = 0.34 * height_eff

    return ResolvedConfig(
        support_mount=config.support_mount,
        pressure_mechanism=config.pressure_mechanism,
        crank_style=config.crank_style,
        feed_module=config.feed_module,
        roller_bank=config.roller_bank,
        roller_count=config.roller_count,
        palette_style=config.palette_style,
        palette=dict(PALETTES[config.palette_style]),
        roller_length_m=length,
        roller_radius_m=radius,
        frame_height_m=height_eff,
        bearing_plane_x_m=bearing_x,
        half_x=half_x,
        nip_centre_distance_m=centre_distance,
        base_z=base_z,
        lower_axis_z=lower_axis,
        upper_axis_z=upper_axis,
        block_h=block_h,
        top_beam_top_z_m=top_top,
        top_beam_bottom_z=beam_bottom,
        rail_z0=base_z + 0.030,
        gear_x=gear_x,
        gear_tip_r=gear_tip_r,
        crank_joint_x=crank_joint_x,
        crank_arm_x0=crank_arm_x0,
        crank_throw=crank_throw,
        axle_x_max=half_x + 0.0066,
        name=config.name,
    )


def slot_choices_for_config(config: Config | ResolvedConfig) -> tuple[tuple[str, object], ...]:
    return (
        ("support_mount", config.support_mount),
        ("pressure_mechanism", config.pressure_mechanism),
        ("crank_style", config.crank_style),
        ("feed_module", config.feed_module),
        ("roller_bank", config.roller_bank),
        ("roller_count", config.roller_count),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, object], ...]:
    return slot_choices_for_config(config_from_seed(seed))


def _materials(model: ArticulatedObject, r: ResolvedConfig) -> dict[str, str]:
    mats: dict[str, str] = {}
    for key, rgba in r.palette.items():
        name = f"wringer_{r.palette_style}_{key}"
        model.material(name, rgba=rgba)
        mats[key] = name
    return mats


def _x_cyl(part, name: str, radius: float, length: float, xyz, material: str) -> None:
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=Origin(xyz=xyz, rpy=(0.0, math.pi / 2.0, 0.0)),
        material=material,
        name=name, material_class_id="metal.generic_plain",
    )


def _bored_block_mesh(name: str, w: float, d: float, h: float, bore_r: float):
    """A real bearing block: a solid with an x-axis bore, not a capped box."""
    solid = cq.Workplane("XY").box(w, d, h)
    solid = solid.cut(
        cq.Workplane("XY").cylinder(height=w * 3.0, radius=bore_r, direct=(1.0, 0.0, 0.0))
    )
    return mesh_from_cadquery(solid, name)


def _bored_boss_mesh(name: str, radius: float, length: float, bore_r: float):
    """A threaded mounting boss with a real through bore along z."""
    solid = cq.Workplane("XY").cylinder(height=length, radius=radius)
    solid = solid.cut(
        cq.Workplane("XY").cylinder(height=length * 3.0, radius=bore_r, direct=(0.0, 0.0, 1.0))
    )
    return mesh_from_cadquery(solid, name)


def _bored_plate_mesh(name: str, w: float, d: float, t: float, bore_r: float):
    """A mounting plate with a real z-bore for the screw that passes through it."""
    solid = cq.Workplane("XY").box(w, d, t)
    solid = solid.cut(
        cq.Workplane("XY").cylinder(height=t * 3.0, radius=bore_r, direct=(0.0, 0.0, 1.0))
    )
    return mesh_from_cadquery(solid, name)


def _bored_hub_mesh(name: str, radius: float, length: float, bore_r: float):
    """A shaft hub with a real x-bore so the axle runs through it, not into it."""
    solid = cq.Workplane("XY").cylinder(height=length, radius=radius, direct=(1.0, 0.0, 0.0))
    solid = solid.cut(
        cq.Workplane("XY").cylinder(height=length * 3.0, radius=bore_r, direct=(1.0, 0.0, 0.0))
    )
    return mesh_from_cadquery(solid, name)


def _bored_y_hub_mesh(name: str, radius: float, length: float, bore_r: float):
    """A hinge eye with a real y-axis bore for its retained pivot pin."""
    solid = cq.Workplane("XY").cylinder(
        height=length,
        radius=radius,
        direct=(0.0, 1.0, 0.0),
    )
    solid = solid.cut(
        cq.Workplane("XY").cylinder(
            height=length * 3.0,
            radius=bore_r,
            direct=(0.0, 1.0, 0.0),
        )
    )
    return mesh_from_cadquery(solid, name)


def _baked_x_cylinder_mesh(
    name: str,
    radius: float,
    length: float,
    xyz: tuple[float, float, float],
):
    """An x-axis cylinder whose placement is baked into its mesh coordinates."""
    solid = cq.Workplane("XY").cylinder(
        height=length,
        radius=radius,
        direct=(1.0, 0.0, 0.0),
    )
    return mesh_from_cadquery(solid.translate(xyz), name)


def _folding_grip_mesh(
    name: str,
    *,
    center_x: float,
    center_z: float,
    length: float,
    radius: float,
):
    """A local-coordinate grip sleeve with a slightly flared closed end."""
    sleeve = (
        cq.Workplane("XY")
        .cylinder(height=length, radius=radius, direct=(1.0, 0.0, 0.0))
        .translate((center_x, 0.0, center_z))
    )
    cap = (
        cq.Workplane("XY")
        .cylinder(height=0.006, radius=radius + 0.003, direct=(1.0, 0.0, 0.0))
        .translate((center_x + 0.5 * length, 0.0, center_z))
    )
    return mesh_from_cadquery(sleeve.union(cap), name)


def _roller_body_mesh(
    name: str,
    *,
    roller_length: float,
    roller_radius: float,
    axle_center_x: float,
    axle_length: float,
):
    """Weld rubber body and steel axle into one connected rotor solid."""
    rubber = cq.Workplane("XY").cylinder(
        height=roller_length,
        radius=roller_radius,
        direct=(1.0, 0.0, 0.0),
    )
    axle = (
        cq.Workplane("XY")
        .transformed(offset=(axle_center_x, 0.0, 0.0))
        .cylinder(height=axle_length, radius=AXLE_R, direct=(1.0, 0.0, 0.0))
    )
    return mesh_from_cadquery(rubber.union(axle), name)


def _top_beam_mesh(name: str, w: float, d: float, t: float, holes: tuple[tuple[float, float], ...]):
    """The top beam plate, cut with the apertures the pressure candidate needs."""
    solid = cq.Workplane("XY").box(w, d, t)
    for x, hole_r in holes:
        solid = solid.cut(
            cq.Workplane("XY")
            .transformed(offset=(x, 0.0, 0.0))
            .cylinder(height=t * 3.0, radius=hole_r, direct=(0.0, 0.0, 1.0))
        )
    return mesh_from_cadquery(solid, name)


def _helix_mesh(name: str, coil_r: float, wire_r: float, height: float, turns: float):
    points = []
    total = int(turns * 20) + 1
    for i in range(total):
        t = i / (total - 1)
        angle = 2.0 * math.pi * turns * t
        points.append((coil_r * math.cos(angle), coil_r * math.sin(angle), height * t))
    return mesh_from_geometry(
        tube_from_spline_points(points, radius=wire_r, samples_per_segment=6, radial_segments=10),
        name,
    )


def _axis_joint(
    model: ArticulatedObject,
    *,
    name: str,
    parent,
    child,
    point: tuple[float, float, float],
    axis: tuple[float, float, float],
    radial: tuple[float, float, float],
    effort: float,
    velocity: float,
    mimic: Mimic | None = None,
    meta: dict | None = None,
) -> None:
    provider = AxisInterface(name=f"{name}__provider", point=point, axis=axis, radial=radial)
    consumer = AxisInterface(name=f"{name}__consumer", axis=axis, radial=radial)
    mate = mate_axes(provider, consumer)
    model.articulation(
        name,
        ArticulationType.CONTINUOUS,
        parent=parent,
        child=child,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(effort=effort, velocity=velocity),
        mimic=mimic,
        meta=meta or {},
    )
    register_interface_mate(model, name, mate)


def _bounded_axis_joint(
    model: ArticulatedObject,
    *,
    name: str,
    parent,
    child,
    point: tuple[float, float, float],
    axis: tuple[float, float, float],
    radial: tuple[float, float, float],
    lower: float,
    upper: float,
    effort: float,
    velocity: float,
    meta: dict | None = None,
) -> None:
    provider = AxisInterface(name=f"{name}__provider", point=point, axis=axis, radial=radial)
    consumer = AxisInterface(name=f"{name}__consumer", axis=axis, radial=radial)
    mate = mate_axes(provider, consumer)
    model.articulation(
        name,
        ArticulationType.REVOLUTE,
        parent=parent,
        child=child,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(
            effort=effort,
            velocity=velocity,
            lower=lower,
            upper=upper,
        ),
        meta=meta or {},
    )
    register_interface_mate(model, name, mate)


# --- support mount candidates -----------------------------------------------
def _support_mount_classic_boss_clamps_build(
    frame, r: ResolvedConfig, mats: dict[str, str]
) -> None:
    """Bench C-clamp mounts: bosses under the bottom beam, screws in real bores."""
    for i, sx in enumerate((-1.0, 1.0)):
        x = sx * r.half_x * 0.66
        frame.visual(
            _bored_plate_mesh(
                f"wringer_clamp_plate_{i}", 0.055, 0.045, 0.014, 0.0055 + FIT
            ),
            origin=Origin(xyz=(x, 0.0, r.base_z - 0.005)),
            material=mats["enamel"],
            name=f"support_mount__classic_boss_clamps__mount_plate_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"turquoise_enamel", "cream_enamel", "galvanised"} else "metal.cast_iron_bare"),
        )
        frame.visual(
            _bored_boss_mesh(f"wringer_clamp_boss_{i}", 0.014, 0.030, 0.0055 + FIT),
            origin=Origin(xyz=(x, 0.0, r.base_z - 0.026)),
            material=mats["bright"],
            name=f"support_mount__classic_boss_clamps__boss_{i}", material_class_id="metal.stainless_matte",
        )


def _support_mount_reinforced_table_clamps_build(
    frame, r: ResolvedConfig, mats: dict[str, str]
) -> None:
    """Deep jaw brackets, paired gussets, and threaded bushings."""
    for i, sx in enumerate((-1.0, 1.0)):
        x = sx * r.half_x * 0.66
        frame.visual(
            _bored_plate_mesh(
                f"reinforced_top_jaw_{i}",
                0.064,
                0.070,
                0.018,
                0.006 + FIT,
            ),
            origin=Origin(xyz=(x, 0.0, r.base_z - 0.004)),
            material=mats["enamel"],
            name=f"support_mount__reinforced_table_clamps__top_jaw_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"turquoise_enamel", "cream_enamel", "galvanised"} else "metal.cast_iron_bare"),
        )
        frame.visual(
            _bored_plate_mesh(
                f"reinforced_deep_bracket_{i}",
                0.020,
                0.070,
                0.082,
                0.006 + FIT,
            ),
            origin=Origin(xyz=(x, 0.0, r.base_z - 0.045)),
            material=mats["enamel_dark"],
            name=f"support_mount__reinforced_table_clamps__deep_bracket_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"turquoise_enamel", "cream_enamel", "galvanised"} else "metal.cast_iron_bare"),
        )
        for j, sy in enumerate((-1.0, 1.0)):
            frame.visual(
                Box((0.050, 0.010, 0.050)),
                origin=Origin(xyz=(x, sy * 0.030, r.base_z - 0.034)),
                material=mats["enamel"],
                name=f"support_mount__reinforced_table_clamps__gusset_{i}_{j}", material_class_id=("metal.paint_coated" if r.palette_style in {"turquoise_enamel", "cream_enamel", "galvanised"} else "metal.cast_iron_bare"),
            )
        frame.visual(
            _bored_boss_mesh(f"reinforced_clamp_bushing_{i}", 0.016, 0.034, 0.006 + FIT),
            origin=Origin(xyz=(x, 0.0, r.base_z - 0.081)),
            material=mats["bright"],
            name=f"support_mount__reinforced_table_clamps__threaded_bushing_{i}", material_class_id="metal.stainless_matte",
        )


def _support_mount_freestanding_floor_frame_build(
    frame, r: ResolvedConfig, mats: dict[str, str]
) -> None:
    """Splayed four-leg floor stand with rubber feet and four cross braces."""
    top_z = r.base_z + 0.006
    foot_h = 0.014
    corners = [
        (-(r.half_x - 0.050), -0.042, -(r.half_x + 0.010), -0.078),
        (r.half_x - 0.050, -0.042, r.half_x + 0.010, -0.078),
        (-(r.half_x - 0.050), 0.042, -(r.half_x + 0.010), 0.078),
        (r.half_x - 0.050, 0.042, r.half_x + 0.010, 0.078),
    ]
    for i, (xt, yt, xb, yb) in enumerate(corners):
        leg = tube_from_spline_points(
            [
                (xt, yt, top_z),
                (0.5 * (xt + xb), 0.5 * (yt + yb), 0.5 * (top_z + foot_h)),
                (xb, yb, foot_h),
            ],
            radius=0.014,
            samples_per_segment=8,
            radial_segments=12,
        )
        frame.visual(
            mesh_from_geometry(leg, f"wringer_leg_{i}"),
            material=mats["enamel"],
            name=f"support_mount__freestanding_floor_frame__leg_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"turquoise_enamel", "cream_enamel", "galvanised"} else "metal.cast_iron_bare"),
        )
        frame.visual(
            Cylinder(radius=0.022, length=foot_h + 0.004),
            origin=Origin(xyz=(xb, yb, 0.5 * (foot_h + 0.004))),
            material=mats["dark"],
            name=f"support_mount__freestanding_floor_frame__foot_{i}", material_class_id="rubber.smooth_plain",
        )

    def _leg_xy(idx: int, t: float) -> tuple[float, float]:
        xt, yt, xb, yb = corners[idx]
        return xb + (xt - xb) * t, yb + (yt - yb) * t

    brace_z = foot_h + 0.32 * (top_z - foot_h)
    t_brace = (brace_z - foot_h) / max(1e-6, top_z - foot_h)
    for i, (a, b) in enumerate(((0, 1), (2, 3), (0, 2), (1, 3))):
        xa, ya = _leg_xy(a, t_brace)
        xb2, yb2 = _leg_xy(b, t_brace)
        frame.visual(
            mesh_from_geometry(
                tube_from_spline_points(
                    [(xa, ya, brace_z), (xb2, yb2, brace_z)],
                    radius=0.009,
                    samples_per_segment=4,
                    radial_segments=10,
                ),
                f"wringer_brace_{i}",
            ),
            material=mats["enamel"],
            name=f"support_mount__freestanding_floor_frame__brace_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"turquoise_enamel", "cream_enamel", "galvanised"} else "metal.cast_iron_bare"),
        )


def _support_mount_wall_bench_bracket_build(
    frame, r: ResolvedConfig, mats: dict[str, str]
) -> None:
    """Rear mounting plate with four wall bolts and two deep gussets."""
    frame.visual(
        Box((2.0 * r.half_x + 0.035, 0.016, 0.150)),
        origin=Origin(xyz=(0.0, 0.070, 0.075)),
        material=mats["steel"],
        name="support_mount__wall_bench_bracket__rear_plate", material_class_id="metal.steel_bare",
    )
    for i, sx in enumerate((-1.0, 1.0)):
        frame.visual(
            Box((0.026, 0.110, 0.070)),
            origin=Origin(xyz=(sx * (r.half_x - 0.025), 0.020, 0.050)),
            material=mats["enamel"],
            name=f"support_mount__wall_bench_bracket__gusset_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"turquoise_enamel", "cream_enamel", "galvanised"} else "metal.cast_iron_bare"),
        )
    index = 0
    for sx in (-1.0, 1.0):
        for sz in (0.035, 0.115):
            frame.visual(
                Cylinder(radius=0.009, length=0.007),
                origin=Origin(
                    xyz=(sx * (r.half_x - 0.030), 0.059, sz),
                    rpy=(math.pi / 2.0, 0.0, 0.0),
                ),
                material=mats["steel"],
                name=f"support_mount__wall_bench_bracket__wall_bolt_{index}", material_class_id="metal.steel_bare",
            )
            index += 1


_SUPPORT_BUILDERS = {
    "classic_boss_clamps": _support_mount_classic_boss_clamps_build,
    "reinforced_table_clamps": _support_mount_reinforced_table_clamps_build,
    "freestanding_floor_frame": _support_mount_freestanding_floor_frame_build,
    "wall_bench_bracket": _support_mount_wall_bench_bracket_build,
}


# --- drive side candidates ---------------------------------------------------
def _spur_gear_ring(
    part,
    r: ResolvedConfig,
    mats: dict[str, str],
    *,
    x: float,
    z: float,
    phase: float,
    prefix: str,
    bored: bool = False,
) -> None:
    """A 16-tooth ring: a hub disc plus loop-emitted tooth blocks, as in source."""
    tip = r.gear_tip_r
    hub_r = tip - 0.006
    if bored:
        part.visual(
            _bored_hub_mesh(f"{prefix}__gear_hub", hub_r, GEAR_T, AXLE_R + FIT),
            origin=Origin(xyz=(x, 0.0, z)),
            material=mats["steel"],
            name=f"{prefix}__gear_hub", material_class_id="metal.steel_bare",
        )
    else:
        _x_cyl(part, f"{prefix}__gear_hub", hub_r, GEAR_T, (x, 0.0, z), mats["steel"])
    tooth_h = 0.008
    for index in range(GEAR_TEETH):
        angle = phase + 2.0 * math.pi * index / GEAR_TEETH
        rad = tip - tooth_h * 0.5
        part.visual(
            Box((GEAR_T, 0.009, tooth_h)),
            origin=Origin(
                xyz=(x, rad * math.sin(angle), z + rad * math.cos(angle)),
                rpy=(angle, 0.0, 0.0),
            ),
            material=mats["steel"],
            name=f"{prefix}__tooth_{index}", material_class_id="metal.steel_bare",
        )


def _drive_side_exposed_gears_build(frame, r: ResolvedConfig, mats: dict[str, str]) -> None:
    """The exposed candidate adds no host geometry; the rings ride the rotors."""
    return None


def _housing_mesh(r: ResolvedConfig):
    depth = r.housing_x1 - r.housing_x0
    cx = 0.5 * (r.housing_x0 + r.housing_x1)
    drum = cq.Workplane("XY").transformed(offset=(cx, 0.0, 0.0)).cylinder(
        height=depth, radius=r.housing_r_out, direct=(1.0, 0.0, 0.0)
    )
    drum = drum.cut(
        cq.Workplane("XY").transformed(offset=(cx, 0.0, 0.0)).cylinder(
            height=depth * 1.2, radius=r.housing_r_in, direct=(1.0, 0.0, 0.0)
        )
    )
    cover = cq.Workplane("XY").transformed(offset=(r.cover_x, 0.0, 0.0)).cylinder(
        height=0.005, radius=r.housing_r_out, direct=(1.0, 0.0, 0.0)
    )
    # Round clearance hole for the lower shaft.
    low_z = -0.5 * r.nip_centre_distance_m
    cover = cover.cut(
        cq.Workplane("XY").transformed(offset=(r.cover_x, 0.0, low_z)).cylinder(
            height=0.05, radius=AXLE_R + FIT, direct=(1.0, 0.0, 0.0)
        )
    )
    # Vertical slot for the crank shaft: the upper axis rises with the pressure
    # travel, so a round hole would foul the shaft at the top of its stroke.
    up_z = 0.5 * r.nip_centre_distance_m
    slot_r = 0.010 + FIT
    cover = cover.cut(
        cq.Workplane("XY")
        .transformed(offset=(r.cover_x, 0.0, up_z + 0.5 * TRAVEL))
        .box(0.05, 2.0 * slot_r, TRAVEL + 2.0 * slot_r)
    )
    return mesh_from_cadquery(drum.union(cover), "wringer_gear_housing")


def _drive_side_enclosed_housing_build(frame, r: ResolvedConfig, mats: dict[str, str]) -> None:
    """A closed gear-housing drum with a cut cover plate on the crank side."""
    mid_z = 0.5 * (r.lower_axis_z + r.upper_axis_z)
    frame.visual(
        _housing_mesh(r),
        origin=Origin(xyz=(0.0, 0.0, mid_z)),
        material=mats["enamel"],
        name="drive_side__enclosed_housing__housing", material_class_id=("metal.paint_coated" if r.palette_style in {"turquoise_enamel", "cream_enamel", "galvanised"} else "metal.cast_iron_bare"),
    )
    frame.visual(
        _bored_hub_mesh(
            "wringer_lower_shaft_hub", AXLE_R + 0.009, 0.007, AXLE_R + FIT
        ),
        origin=Origin(xyz=(r.cover_x + 0.005, 0.0, r.lower_axis_z)),
        material=mats["steel"],
        name="drive_side__enclosed_housing__lower_shaft_hub", material_class_id="metal.steel_bare",
    )


_DRIVE_HOST_BUILDERS = {
    "exposed_gears": _drive_side_exposed_gears_build,
    "enclosed_housing": _drive_side_enclosed_housing_build,
}


# --- pressure mechanism candidates ------------------------------------------
def _pressure_holes(r: ResolvedConfig) -> tuple[tuple[float, float], ...]:
    if r.pressure_mechanism in ("centre_screw", "overhead_screw_bridge"):
        return ((0.0, 0.005 + FIT),)
    return (
        (-r.bearing_plane_x_m, 0.004 + FIT),
        (r.bearing_plane_x_m, 0.004 + FIT),
    )


def _pressure_mechanism_centre_screw_build(model, frame, r, mats) -> list:
    screw = model.part(
        "pressure_mechanism__centre_screw__screw",
        meta={"role": "pressure_adjuster"},
    )
    stem_len = 0.006 + BEAM_T + 0.020
    stem_c = r.top_beam_bottom_z - 0.006 + 0.5 * stem_len
    screw.visual(
        Cylinder(radius=0.005, length=stem_len),
        origin=Origin(xyz=(0.0, 0.0, stem_c - r.top_beam_top_z_m)),
        material=mats["bright"],
        name="pressure_mechanism__centre_screw__stem", material_class_id="metal.stainless_matte",
    )
    screw.visual(
        Cylinder(radius=0.015, length=0.016),
        origin=Origin(xyz=(0.0, 0.0, 0.012)),
        material=mats["dark"],
        name="pressure_mechanism__centre_screw__hub", material_class_id="metal.cast_iron_bare",
    )
    _x_cyl(
        screw,
        "pressure_mechanism__centre_screw__handle",
        0.012,
        0.070,
        (0.0, 0.0, 0.022),
        mats["dark"],
    )
    _axis_joint(
        model,
        name="pressure_screw_turn",
        parent=frame,
        child=screw,
        point=(0.0, 0.0, r.top_beam_top_z_m),
        axis=(0.0, 0.0, 1.0),
        radial=(1.0, 0.0, 0.0),
        effort=18.0,
        velocity=2.0,
        meta={"positive_motion": "screws the roller pressure down"},
    )
    return [screw]


def _pressure_mechanism_overhead_screw_bridge_build(model, frame, r, mats) -> list:
    """Raised twin-post yoke with a central screw and pressure bar."""
    for i, sx in enumerate((-1.0, 1.0)):
        x = sx * (r.bearing_plane_x_m - 0.012)
        frame.visual(
            Box((0.018, 0.052, 0.088)),
            origin=Origin(xyz=(x, 0.0, r.top_beam_top_z_m + 0.044)),
            material=mats["enamel_dark"],
            name=f"pressure_mechanism__overhead_screw_bridge__post_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"turquoise_enamel", "cream_enamel", "galvanised"} else "metal.cast_iron_bare"),
        )
    frame.visual(
        _top_beam_mesh(
            "overhead_bridge_crossbar",
            2.0 * r.bearing_plane_x_m,
            0.060,
            0.020,
            ((0.0, 0.006 + FIT),),
        ),
        origin=Origin(xyz=(0.0, 0.0, r.top_beam_top_z_m + 0.090)),
        material=mats["enamel"],
        name="pressure_mechanism__overhead_screw_bridge__crossbar", material_class_id=("metal.paint_coated" if r.palette_style in {"turquoise_enamel", "cream_enamel", "galvanised"} else "metal.cast_iron_bare"),
    )
    for i, sx in enumerate((-1.0, 1.0)):
        frame.visual(
            Box((r.bearing_plane_x_m - 0.025, 0.040, 0.012)),
            origin=Origin(
                xyz=(sx * 0.5 * (r.bearing_plane_x_m + 0.025), 0.0, r.top_beam_top_z_m + 0.028)
            ),
            material=mats["steel"],
            name=f"pressure_mechanism__overhead_screw_bridge__pressure_pad_{i}", material_class_id="metal.steel_bare",
        )
    screw = model.part(
        "pressure_mechanism__overhead_screw_bridge__screw",
        meta={"role": "pressure_adjuster"},
    )
    screw.visual(
        Cylinder(radius=0.006, length=0.105),
        origin=Origin(xyz=(0.0, 0.0, -0.045)),
        material=mats["bright"],
        name="pressure_mechanism__overhead_screw_bridge__knurled_screw", material_class_id="metal.stainless_matte",
    )
    screw.visual(
        Cylinder(radius=0.014, length=0.004),
        origin=Origin(xyz=(0.0, 0.0, -0.004)),
        material=mats["steel"],
        name="pressure_mechanism__overhead_screw_bridge__thrust_collar", material_class_id="metal.steel_bare",
    )
    _x_cyl(
        screw,
        "pressure_mechanism__overhead_screw_bridge__handle",
        0.010,
        0.080,
        (0.0, 0.0, 0.012),
        mats["dark"],
    )
    _axis_joint(
        model,
        name="bridge_screw_turn",
        parent=frame,
        child=screw,
        point=(0.0, 0.0, r.top_beam_top_z_m + 0.100),
        axis=(0.0, 0.0, 1.0),
        radial=(1.0, 0.0, 0.0),
        effort=22.0,
        velocity=2.0,
    )
    return [screw]


def _pressure_mechanism_spring_loaded_bridge_build(model, frame, r, mats) -> list:
    towers = []
    for i, sx in enumerate((-1.0, 1.0)):
        x = sx * r.bearing_plane_x_m
        tower = model.part(
            f"pressure_mechanism__spring_loaded_bridge__tower_{i}",
            meta={"role": "pressure_adjuster", "index": i},
        )
        stud_len = 0.006 + BEAM_T + 0.062
        stud_top = 0.062
        tower.visual(
            Cylinder(radius=0.004, length=stud_len),
            origin=Origin(xyz=(0.0, 0.0, stud_top - 0.5 * stud_len)),
            material=mats["bright"],
            name=f"pressure_mechanism__spring_loaded_bridge__guide_post_{i}", material_class_id="metal.stainless_matte",
        )
        tower.visual(
            Cylinder(radius=0.012, length=0.005),
            origin=Origin(xyz=(0.0, 0.0, 0.0025 - SEAT)),
            material=mats["steel"],
            name=f"pressure_mechanism__spring_loaded_bridge__lower_seat_{i}", material_class_id="metal.steel_bare",
        )
        tower.visual(
            _helix_mesh(f"wringer_coil_spring_{i}", 0.0055, 0.0018, 0.042, 5.0),
            origin=Origin(xyz=(0.0, 0.0, 0.005)),
            material=mats["bright"],
            name=f"pressure_mechanism__spring_loaded_bridge__coil_spring_{i}", material_class_id="metal.stainless_matte",
        )
        tower.visual(
            Cylinder(radius=0.012, length=0.005),
            origin=Origin(xyz=(0.0, 0.0, 0.0495)),
            material=mats["steel"],
            name=f"pressure_mechanism__spring_loaded_bridge__upper_seat_{i}", material_class_id="metal.steel_bare",
        )
        tower.visual(
            Cylinder(radius=0.009, length=0.009),
            origin=Origin(xyz=(0.0, 0.0, 0.058)),
            material=mats["steel"],
            name=f"pressure_mechanism__spring_loaded_bridge__anchor_hub_{i}", material_class_id="metal.steel_bare",
        )
        tower.visual(
            Box((0.030, 0.006, 0.012)),
            origin=Origin(xyz=(0.0, 0.0, 0.058)),
            material=mats["steel"],
            name=f"pressure_mechanism__spring_loaded_bridge__bridge_anchor_{i}", material_class_id="metal.steel_bare",
        )
        model.articulation(
            f"spring_tower_mount_{i}",
            ArticulationType.FIXED,
            parent=frame,
            child=tower,
            origin=Origin(xyz=(x, 0.0, r.top_beam_top_z_m)),
        )
        towers.append(tower)
    return towers


def _pressure_mechanism_dual_handwheels_build(model, frame, r, mats) -> list:
    """Paired threaded posts and handwheels tied across the bearing lines."""
    frame.visual(
        _top_beam_mesh(
            "dual_handwheel_tie_bar",
            2.0 * r.bearing_plane_x_m + 0.020,
            0.046,
            0.014,
            (
                (-r.bearing_plane_x_m, 0.005 + FIT),
                (r.bearing_plane_x_m, 0.005 + FIT),
            ),
        ),
        origin=Origin(xyz=(0.0, 0.0, r.top_beam_top_z_m + 0.006)),
        material=mats["enamel_dark"],
        name="pressure_mechanism__dual_handwheels__tie_bar", material_class_id=("metal.paint_coated" if r.palette_style in {"turquoise_enamel", "cream_enamel", "galvanised"} else "metal.cast_iron_bare"),
    )
    wheels = []
    for i, sx in enumerate((-1.0, 1.0)):
        wheel = model.part(
            f"pressure_mechanism__dual_handwheels__wheel_{i}",
            meta={"role": "pressure_adjuster", "index": i},
        )
        wheel.visual(
            Cylinder(radius=0.005, length=0.062),
            origin=Origin(xyz=(0.0, 0.0, -0.020)),
            material=mats["bright"],
            name=f"pressure_mechanism__dual_handwheels__threaded_post_{i}", material_class_id="metal.stainless_matte",
        )
        wheel.visual(
            Cylinder(radius=0.030, length=0.008),
            origin=Origin(xyz=(0.0, 0.0, 0.010)),
            material=mats["dark"],
            name=f"pressure_mechanism__dual_handwheels__handwheel_{i}", material_class_id="metal.cast_iron_bare",
        )
        for spoke in range(4):
            angle = spoke * math.pi / 2.0
            wheel.visual(
                Box((0.050, 0.005, 0.005)),
                origin=Origin(xyz=(0.0, 0.0, 0.010), rpy=(0.0, 0.0, angle)),
                material=mats["bright"],
                name=f"pressure_mechanism__dual_handwheels__spoke_{i}_{spoke}", material_class_id="metal.stainless_matte",
            )
        _axis_joint(
            model,
            name=f"handwheel_turn_{i}",
            parent=frame,
            child=wheel,
            point=(sx * r.bearing_plane_x_m, 0.0, r.top_beam_top_z_m + 0.040),
            axis=(0.0, 0.0, 1.0),
            radial=(1.0, 0.0, 0.0),
            effort=16.0,
            velocity=2.2,
            mimic=None if i == 0 else Mimic("handwheel_turn_0", 1.0, 0.0),
        )
        wheels.append(wheel)
    return wheels


_PRESSURE_BUILDERS = {
    "centre_screw": _pressure_mechanism_centre_screw_build,
    "overhead_screw_bridge": _pressure_mechanism_overhead_screw_bridge_build,
    "spring_loaded_bridge": _pressure_mechanism_spring_loaded_bridge_build,
    "dual_handwheels": _pressure_mechanism_dual_handwheels_build,
}


# --- frame -------------------------------------------------------------------
def _build_frame(model: ArticulatedObject, r: ResolvedConfig, mats: dict[str, str]):
    frame = model.part("frame", meta={"role": "frame"})
    frame.visual(
        Box((2.0 * r.half_x - 0.036, 0.110, BEAM_T)),
        origin=Origin(xyz=(0.0, 0.006, r.base_z + 0.5 * BEAM_T)),
        material=mats["enamel"],
        name="bottom_beam", material_class_id=("metal.paint_coated" if r.palette_style in {"turquoise_enamel", "cream_enamel", "galvanised"} else "metal.cast_iron_bare"),
    )
    frame.visual(
        _top_beam_mesh(
            "wringer_top_beam", 2.0 * r.half_x, 0.090, BEAM_T, _pressure_holes(r)
        ),
        origin=Origin(xyz=(0.0, 0.0, r.top_beam_top_z_m - 0.5 * BEAM_T)),
        material=mats["enamel"],
        name="top_beam", material_class_id=("metal.paint_coated" if r.palette_style in {"turquoise_enamel", "cream_enamel", "galvanised"} else "metal.cast_iron_bare"),
    )
    if r.feed_module == "plain_front_apron":
        frame.visual(
            Box((2.0 * r.half_x - 0.062, 0.014, 0.030)),
            origin=Origin(xyz=(0.0, -0.052, r.base_z + 0.030)),
            material=mats["enamel_dark"],
            name="feed_module__plain_front_apron__apron", material_class_id=("metal.paint_coated" if r.palette_style in {"turquoise_enamel", "cream_enamel", "galvanised"} else "metal.cast_iron_bare"),
        )

    rail_z1 = r.top_beam_bottom_z + 0.004
    rail_h = rail_z1 - r.rail_z0
    for side, sx in enumerate((-1.0, 1.0)):
        x = sx * (r.half_x - 0.5 * RAIL_W)
        for rail, sy in enumerate((-1.0, 1.0)):
            frame.visual(
                Box((RAIL_W, RAIL_D, rail_h)),
                origin=Origin(xyz=(x, sy * RAIL_Y, r.rail_z0 + 0.5 * rail_h)),
                material=mats["enamel"],
                name=f"side_rail_{side}_{rail}", material_class_id=("metal.paint_coated" if r.palette_style in {"turquoise_enamel", "cream_enamel", "galvanised"} else "metal.cast_iron_bare"),
            )
        frame.visual(
            Box((RAIL_W, 0.070, 0.025)),
            origin=Origin(xyz=(x, 0.0, r.base_z + 0.044)),
            material=mats["enamel"],
            name=f"side_bridge_{side}", material_class_id=("metal.paint_coated" if r.palette_style in {"turquoise_enamel", "cream_enamel", "galvanised"} else "metal.cast_iron_bare"),
        )
        for row in range(r.roller_count - 1):
            row_z = r.lower_axis_z + row * r.nip_centre_distance_m
            frame.visual(
                _bored_block_mesh(
                    f"wringer_fixed_bearing_{side}_{row}",
                    BLOCK_W,
                    LOWER_BLOCK_D,
                    r.block_h,
                    AXLE_R + FIT,
                ),
                origin=Origin(xyz=(sx * r.bearing_plane_x_m, 0.0, row_z)),
                material=mats["dark"],
                name=f"roller_bank__indexed_parallel_roller_bank__bearing_{row}_{side}", material_class_id="metal.cast_iron_bare",
            )
        for fastener, fz in enumerate((0.22, 0.78)):
            frame.visual(
                Cylinder(radius=0.006, length=0.010),
                origin=Origin(
                    xyz=(x, -0.047, r.rail_z0 + fz * rail_h),
                    rpy=(math.pi / 2.0, 0.0, 0.0),
                ),
                material=mats["bright"],
                name=f"frame_fastener_{side}_{fastener}", material_class_id="metal.stainless_matte",
            )

    _SUPPORT_BUILDERS[r.support_mount](frame, r, mats)
    return frame


# --- rollers, crank and pressure carriers ------------------------------------
def _build_rollers(model: ArticulatedObject, frame, r: ResolvedConfig, mats: dict[str, str]):
    blocks = []
    for i, sx in enumerate((-1.0, 1.0)):
        block = model.part(f"pressure_block_{i}", meta={"role": "pressure_block", "index": i})
        block.visual(
            _bored_block_mesh(
                f"wringer_pressure_block_{i}", BLOCK_W, BLOCK_D, r.block_h, AXLE_R + FIT
            ),
            material=mats["dark"],
            name=f"pressure_block__carrier_{i}", material_class_id="metal.cast_iron_bare",
        )
        joint = f"pressure_slide_{i}"
        model.articulation(
            joint,
            ArticulationType.PRISMATIC,
            parent=frame,
            child=block,
            origin=Origin(xyz=(sx * r.bearing_plane_x_m, 0.0, r.upper_axis_z)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=500.0, velocity=0.015, lower=0.0, upper=TRAVEL),
            mimic=None if i == 0 else Mimic(joint="pressure_slide_0", multiplier=1.0, offset=0.0),
            meta={"positive_motion": "opens the roller nip"},
        )
        blocks.append(block)

    upper = model.part("upper_roller", meta={"role": "upper_roller"})
    lower = model.part("lower_roller", meta={"role": "lower_roller"})
    axle_x0 = -(r.bearing_plane_x_m + 0.012)
    upper_axle_len = r.axle_x_max - axle_x0
    _x_cyl(
        upper,
        "upper_roller__axle",
        AXLE_R,
        upper_axle_len,
        (0.5 * (axle_x0 + r.axle_x_max) + r.bearing_plane_x_m, 0.0, 0.0),
        mats["bright"],
    )
    _x_cyl(
        upper,
        "upper_roller__rubber",
        r.roller_radius_m,
        r.roller_length_m,
        (r.bearing_plane_x_m, 0.0, 0.0),
        mats["roller"],
    )

    lower_x_max = r.gear_x + 0.5 * GEAR_T if r.drive_side == "exposed_gears" else r.cover_x + 0.010
    lower_axle_len = lower_x_max - axle_x0
    _x_cyl(
        lower,
        "lower_roller__axle",
        AXLE_R,
        lower_axle_len,
        (0.5 * (axle_x0 + lower_x_max), 0.0, 0.0),
        mats["bright"],
    )
    _x_cyl(
        lower,
        "lower_roller__rubber",
        r.roller_radius_m,
        r.roller_length_m,
        (0.0, 0.0, 0.0),
        mats["roller"],
    )

    crank = model.part("crank_drive", meta={"role": "crank_drive"})
    if r.drive_side == "exposed_gears":
        _spur_gear_ring(
            lower,
            r,
            mats,
            x=r.gear_x,
            z=0.0,
            phase=math.pi / GEAR_TEETH,
            prefix="drive_side__exposed_gears__lower_gear",
        )
        _spur_gear_ring(
            crank,
            r,
            mats,
            x=r.gear_x - r.crank_joint_x,
            z=0.0,
            phase=0.0,
            prefix="drive_side__exposed_gears__drive_gear",
        )
    else:
        shaft_x1 = r.cover_x + 0.012 - r.crank_joint_x
        _x_cyl(
            crank,
            "drive_side__enclosed_housing__crank_shaft",
            0.010,
            shaft_x1 + 0.006,
            (0.5 * (shaft_x1 - 0.006), 0.0, 0.0),
            mats["steel"],
        )
        _x_cyl(
            crank,
            "drive_side__enclosed_housing__crank_hub",
            0.020,
            0.008,
            (shaft_x1 - 0.004, 0.0, 0.0),
            mats["dark"],
        )

    throw = r.crank_throw
    x0 = r.crank_arm_x0
    crank_path = tube_from_spline_points(
        [
            (0.006, 0.0, 0.0),
            (x0, 0.0, 0.0),
            (x0 + 0.018, 0.0, 0.012),
            (x0 + 0.025, 0.0, 0.42 * throw),
            (x0 + 0.025, 0.0, 0.82 * throw),
            (x0 + 0.040, 0.0, throw),
            (x0 + 0.070, 0.0, throw),
            (x0 + 0.120, 0.0, throw),
        ],
        radius=0.006,
        samples_per_segment=10,
        radial_segments=14,
    )
    crank.visual(
        mesh_from_geometry(crank_path, "wringer_bent_crank"),
        material=mats["enamel"],
        name="crank_drive__bent_crank", material_class_id=("metal.paint_coated" if r.palette_style in {"turquoise_enamel", "cream_enamel", "galvanised"} else "metal.cast_iron_bare"),
    )
    _x_cyl(crank, "crank_drive__grip", 0.014, 0.082, (x0 + 0.098, 0.0, throw), mats["dark"])
    _x_cyl(crank, "crank_drive__grip_end", 0.017, 0.005, (x0 + 0.140, 0.0, throw), mats["dark"])

    _axis_joint(
        model,
        name="crank_rotation",
        parent=blocks[1],
        child=crank,
        # Joint origins are parent-relative: pressure_block_1 already sits at
        # (+bearing_plane_x, 0, upper_axis_z), so only the outboard offset remains.
        point=(r.crank_joint_x - r.bearing_plane_x_m, 0.0, 0.0),
        axis=(1.0, 0.0, 0.0),
        radial=(0.0, 0.0, 1.0),
        effort=65.0,
        velocity=4.0,
        meta={"positive_motion": "turns the crank and drives the nip"},
    )
    _axis_joint(
        model,
        name="upper_roller_spin",
        parent=blocks[0],
        child=upper,
        # pressure_block_0 is already on the upper roller axis.
        point=(0.0, 0.0, 0.0),
        axis=(1.0, 0.0, 0.0),
        radial=(0.0, 0.0, 1.0),
        effort=65.0,
        velocity=4.0,
        mimic=Mimic(joint="crank_rotation", multiplier=1.0, offset=0.0),
    )
    _axis_joint(
        model,
        name="lower_roller_spin",
        parent=frame,
        child=lower,
        point=(0.0, 0.0, r.lower_axis_z),
        axis=(1.0, 0.0, 0.0),
        radial=(0.0, 0.0, 1.0),
        effort=65.0,
        velocity=4.0,
        mimic=Mimic(joint="crank_rotation", multiplier=-1.0, offset=math.pi / GEAR_TEETH),
    )
    return upper, lower, crank, blocks


def _crank_style_fixed_bent_crank_build(
    model, crank, r: ResolvedConfig, mats: dict[str, str]
) -> list:
    """One-piece swept crank, grip, and end cap."""
    x0 = r.crank_arm_x0
    throw = r.crank_throw
    crank.visual(
        mesh_from_geometry(
            tube_from_spline_points(
                [
                    (GEAR_T + 0.010, 0.0, 0.0),
                    (x0, 0.0, 0.0),
                    (x0 + 0.025, 0.0, 0.42 * throw),
                    (x0 + 0.040, 0.0, throw),
                    (x0 + 0.120, 0.0, throw),
                ],
                radius=0.006,
                samples_per_segment=10,
                radial_segments=14,
            ),
            "wringer_fixed_bent_crank",
        ),
        material=mats["enamel"],
        name="crank_style__fixed_bent_crank__arm", material_class_id=("metal.paint_coated" if r.palette_style in {"turquoise_enamel", "cream_enamel", "galvanised"} else "metal.cast_iron_bare"),
    )
    _x_cyl(
        crank,
        "crank_style__fixed_bent_crank__grip",
        0.014,
        0.082,
        (x0 + 0.098, 0.0, throw),
        mats["dark"],
    )
    return []


def _crank_style_folding_park_crank_build(
    model, crank, r: ResolvedConfig, mats: dict[str, str]
) -> list:
    """Forked hinge, retained eye, swept handle, and overlapping grip."""
    hinge_x = r.crank_arm_x0 + 0.035
    crank.visual(
        mesh_from_geometry(
            tube_from_spline_points(
                [(GEAR_T + 0.010, 0.0, 0.0), (hinge_x - 0.014, 0.0, 0.0)],
                radius=0.007,
                samples_per_segment=8,
                radial_segments=14,
            ),
            "wringer_folding_crank_stub",
        ),
        material=mats["enamel"],
        name="crank_style__folding_park_crank__stub", material_class_id=("metal.paint_coated" if r.palette_style in {"turquoise_enamel", "cream_enamel", "galvanised"} else "metal.cast_iron_bare"),
    )
    for cheek, sy in enumerate((-1.0, 1.0)):
        crank.visual(
            Box((0.030, 0.009, 0.020)),
            origin=Origin(xyz=(hinge_x, sy * 0.011, 0.0)),
            material=mats["enamel"],
            name=f"crank_style__folding_park_crank__hinge_cheek_{cheek}", material_class_id=("metal.paint_coated" if r.palette_style in {"turquoise_enamel", "cream_enamel", "galvanised"} else "metal.cast_iron_bare"),
        )
    crank.visual(
        Cylinder(radius=0.003, length=0.030),
        origin=Origin(xyz=(hinge_x, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["bright"],
        name="crank_style__folding_park_crank__hinge_pin", material_class_id="metal.stainless_matte",
    )
    handle = model.part(
        "crank_style__folding_park_crank__handle",
        meta={"role": "crank_handle"},
    )
    throw = r.crank_throw
    handle.visual(
        _bored_y_hub_mesh(
            "wringer_folding_crank_hinge_eye",
            0.008,
            0.014,
            0.003 + FIT,
        ),
        material=mats["steel"],
        name="crank_style__folding_park_crank__hinge_eye", material_class_id="metal.steel_bare",
    )
    handle.visual(
        mesh_from_geometry(
            tube_from_spline_points(
                [
                    # Sink the first swept section into the hinge-eye boss.  A
                    # merely tangent start can open a sub-millimetre mesh gap
                    # after tessellation at some sampled crank dimensions.
                    (0.000, 0.0, 0.006),
                    (0.014, 0.0, 0.27 * throw),
                    (0.024, 0.0, 0.52 * throw),
                    (0.025, 0.0, 0.81 * throw),
                    (0.040, 0.0, throw),
                    (0.050, 0.0, throw),
                ],
                radius=0.006,
                samples_per_segment=14,
                radial_segments=16,
            ),
            "wringer_folding_crank_handle",
        ),
        material=mats["enamel"],
        name="crank_style__folding_park_crank__swing_arm", material_class_id=("metal.paint_coated" if r.palette_style in {"turquoise_enamel", "cream_enamel", "galvanised"} else "metal.cast_iron_bare"),
    )
    # Keep the exposed spindle and the sleeve as identity-origin meshes.  Some
    # downstream viewers mishandle a rotated primitive's non-zero visual
    # origin under the fold joint, which made the sleeve appear to float even
    # though the URDF link was correct.  The spindle overlaps both the swept
    # elbow and the sleeve, giving the visible assembly a real load path.
    handle.visual(
        _baked_x_cylinder_mesh(
            "wringer_folding_crank_grip_spindle",
            0.006,
            0.116,
            (0.094, 0.0, throw),
        ),
        material=mats["enamel"],
        name="crank_style__folding_park_crank__grip_spindle", material_class_id=("metal.paint_coated" if r.palette_style in {"turquoise_enamel", "cream_enamel", "galvanised"} else "metal.cast_iron_bare"),
    )
    handle.visual(
        _folding_grip_mesh(
            "wringer_folding_crank_grip",
            center_x=0.108,
            center_z=throw,
            length=0.082,
            radius=0.014,
        ),
        material=mats["dark"],
        name="crank_style__folding_park_crank__grip", material_class_id="rubber.smooth_plain",
    )
    _bounded_axis_joint(
        model,
        name="crank_fold",
        parent=crank,
        child=handle,
        point=(hinge_x, 0.0, 0.0),
        axis=(0.0, 1.0, 0.0),
        radial=(1.0, 0.0, 0.0),
        lower=0.0,
        upper=math.pi / 2.0,
        effort=12.0,
        velocity=2.0,
        meta={"positive_motion": "parks the handle against the side frame"},
    )
    return [handle]


_CRANK_BUILDERS = {
    "fixed_bent_crank": _crank_style_fixed_bent_crank_build,
    "folding_park_crank": _crank_style_folding_park_crank_build,
}


def _roller_bank_indexed_parallel_roller_bank_build(
    model: ArticulatedObject,
    frame,
    r: ResolvedConfig,
    mats: dict[str, str],
):
    """Emit N real rollers, N spin joints, and the N-derived bearing topology."""
    blocks = []
    for i, sx in enumerate((-1.0, 1.0)):
        block = model.part(f"pressure_block_{i}", meta={"role": "pressure_block", "index": i})
        block.visual(
            _bored_block_mesh(
                f"wringer_pressure_block_{i}",
                BLOCK_W,
                BLOCK_D,
                r.block_h,
                AXLE_R + FIT,
            ),
            material=mats["dark"],
            name=f"roller_bank__indexed_parallel_roller_bank__moving_bearing_{i}", material_class_id="metal.cast_iron_bare",
        )
        model.articulation(
            f"pressure_slide_{i}",
            ArticulationType.PRISMATIC,
            parent=frame,
            child=block,
            origin=Origin(xyz=(sx * r.bearing_plane_x_m, 0.0, r.upper_axis_z)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(
                effort=500.0,
                velocity=0.015,
                lower=0.0,
                upper=TRAVEL,
            ),
            mimic=(
                None
                if i == 0
                else Mimic(joint="pressure_slide_0", multiplier=1.0, offset=0.0)
            ),
            meta={"positive_motion": "opens the upper wringing nip"},
        )
        blocks.append(block)

    crank = model.part("crank_drive", meta={"role": "crank_drive"})
    _spur_gear_ring(
        crank,
        r,
        mats,
        x=r.gear_x - r.crank_joint_x,
        z=0.0,
        phase=0.0,
        prefix="roller_bank__indexed_parallel_roller_bank__drive_gear",
        bored=True,
    )
    _x_cyl(
        crank,
        "roller_bank__indexed_parallel_roller_bank__crank_shoulder",
        0.010,
        0.013,
        (0.0195, 0.0, 0.0),
        mats["steel"],
    )
    _CRANK_BUILDERS[r.crank_style](model, crank, r, mats)
    _axis_joint(
        model,
        name="crank_rotation",
        parent=blocks[1],
        child=crank,
        point=(r.crank_joint_x - r.bearing_plane_x_m, 0.0, 0.0),
        axis=(1.0, 0.0, 0.0),
        radial=(0.0, 0.0, 1.0),
        effort=65.0,
        velocity=4.0,
        meta={"positive_motion": "turns the crank and drives the roller bank"},
    )

    rollers = []
    top_index = r.roller_count - 1
    axle_x0 = -(r.bearing_plane_x_m + 0.012)
    axle_x1 = r.gear_x + 0.5 * GEAR_T
    axle_len = axle_x1 - axle_x0
    for index in range(r.roller_count):
        is_top = index == top_index
        roller = model.part(
            f"roller_bank__indexed_parallel_roller_bank__roller_{index}",
            meta={
                "role": "roller",
                "index": index,
                "position": "upper" if is_top else "fixed",
            },
        )
        local_x = r.bearing_plane_x_m if is_top else 0.0
        roller.visual(
            _roller_body_mesh(
                f"wringer_welded_roller_{index}",
                roller_length=r.roller_length_m,
                roller_radius=r.roller_radius_m,
                axle_center_x=0.5 * (axle_x0 + axle_x1),
                axle_length=axle_len,
            ),
            origin=Origin(xyz=(local_x, 0.0, 0.0)),
            material=mats["roller"],
            name=f"roller_bank__indexed_parallel_roller_bank__rubber_axle_{index}", material_class_id="rubber.smooth_plain",
        )
        if not is_top:
            _spur_gear_ring(
                roller,
                r,
                mats,
                x=r.gear_x,
                z=0.0,
                phase=(top_index - index) * math.pi / GEAR_TEETH,
                prefix=f"roller_bank__indexed_parallel_roller_bank__gear_{index}",
            )
        multiplier = 1.0 if (top_index - index) % 2 == 0 else -1.0
        _axis_joint(
            model,
            name=f"roller_spin_{index}",
            parent=blocks[0] if is_top else frame,
            child=roller,
            point=(0.0, 0.0, 0.0)
            if is_top
            else (0.0, 0.0, r.lower_axis_z + index * r.nip_centre_distance_m),
            axis=(1.0, 0.0, 0.0),
            radial=(0.0, 0.0, 1.0),
            effort=65.0,
            velocity=4.0,
            mimic=Mimic(
                joint="crank_rotation",
                multiplier=multiplier,
                offset=index * math.pi / GEAR_TEETH,
            ),
        )
        rollers.append(roller)
    return rollers, crank, blocks


def _feed_module_plain_front_apron_build(model, frame, r, mats) -> list:
    """The frame builder owns the welded baseline apron."""
    return []


def _feed_module_fold_down_shelf_build(model, frame, r, mats) -> list:
    """Broad shelf on a registered bounded hinge at the frame front."""
    shelf = model.part(
        "feed_module__fold_down_shelf__shelf",
        meta={"role": "feed_shelf"},
    )
    shelf.visual(
        Box((2.0 * r.half_x - 0.160, 0.145, 0.012)),
        origin=Origin(xyz=(0.0, -0.070, 0.008)),
        material=mats["enamel"],
        name="feed_module__fold_down_shelf__panel", material_class_id=("metal.paint_coated" if r.palette_style in {"turquoise_enamel", "cream_enamel", "galvanised"} else "metal.cast_iron_bare"),
    )
    for i, sx in enumerate((-1.0, 1.0)):
        shelf.visual(
            Cylinder(radius=0.0035, length=0.028),
            origin=Origin(
                xyz=(sx * (r.half_x - 0.067), 0.0, 0.0),
                rpy=(0.0, math.pi / 2.0, 0.0),
            ),
            material=mats["bright"],
            name=f"feed_module__fold_down_shelf__hinge_barrel_{i}", material_class_id="metal.stainless_matte",
        )
    _bounded_axis_joint(
        model,
        name="feed_shelf_fold",
        parent=frame,
        child=shelf,
        point=(0.0, -0.048, r.base_z + BEAM_T),
        axis=(1.0, 0.0, 0.0),
        radial=(0.0, 1.0, 0.0),
        lower=0.0,
        upper=math.pi / 2.0,
        effort=8.0,
        velocity=1.5,
        meta={"positive_motion": "folds the shelf down from the feed position"},
    )
    return [shelf]


_FEED_BUILDERS = {
    "plain_front_apron": _feed_module_plain_front_apron_build,
    "fold_down_shelf": _feed_module_fold_down_shelf_build,
}


def _build_clamps(model: ArticulatedObject, frame, r: ResolvedConfig, mats: dict[str, str]) -> list:
    clamps = []
    prefix = f"support_mount__{r.support_mount}"
    reinforced = r.support_mount == "reinforced_table_clamps"
    for i, sx in enumerate((-1.0, 1.0)):
        clamp = model.part(f"{prefix}__clamp_{i}", meta={"role": "mount_clamp"})
        clamp.visual(
            Cylinder(radius=0.006 if reinforced else 0.0055, length=0.118 if reinforced else 0.060),
            origin=Origin(xyz=(0.0, 0.0, -0.072 if reinforced else -0.044)),
            material=mats["bright"],
            name=f"{prefix}__screw_{i}", material_class_id="metal.stainless_matte",
        )
        clamp.visual(
            Cylinder(radius=0.010, length=0.014),
            origin=Origin(xyz=(0.0, 0.0, -0.120 if reinforced else -0.067)),
            material=mats["steel"],
            name=f"{prefix}__pad_socket_{i}", material_class_id="metal.steel_bare",
        )
        clamp.visual(
            Cylinder(radius=0.030 if reinforced else 0.026, length=0.010),
            origin=Origin(xyz=(0.0, 0.0, -0.130 if reinforced else -0.076)),
            material=mats["dark"],
            name=f"{prefix}__pad_{i}", material_class_id="rubber.smooth_plain",
        )
        if reinforced:
            _x_cyl(
                clamp,
                f"{prefix}__cross_handle_{i}",
                0.004,
                0.070,
                (0.0, 0.0, -0.040),
                mats["steel"],
            )
        model.articulation(
            f"clamp_adjust_{i}",
            ArticulationType.PRISMATIC,
            parent=frame,
            child=clamp,
            origin=Origin(xyz=(sx * r.half_x * 0.66, 0.0, r.base_z)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=300.0, velocity=0.020, lower=-0.015, upper=0.012),
            meta={"positive_motion": "tightens the clamp against the bench"},
        )
        clamps.append(clamp)
    return clamps


# --- assembly ----------------------------------------------------------------
def build_picturex_0611_hand_crank_clothes_wringer(
    config: Config | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config or Config())
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={
            "category": "pictureX_0611_Hand_crank_clothes_wringer",
            "slot_choices": slot_choices_for_config(r),
            "mechanism": "counter-rotating roller nip driven by a side hand crank",
        },
    )
    mats = _materials(model, r)
    frame = _build_frame(model, r, mats)
    _roller_bank_indexed_parallel_roller_bank_build(model, frame, r, mats)
    _PRESSURE_BUILDERS[r.pressure_mechanism](model, frame, r, mats)
    _FEED_BUILDERS[r.feed_module](model, frame, r, mats)
    if r.support_mount in ("classic_boss_clamps", "reinforced_table_clamps"):
        _build_clamps(model, frame, r, mats)

    risk: list[dict[str, float]] = [
        {"pressure_slide_0": 0.0, "crank_rotation": 0.0},
        {"pressure_slide_0": TRAVEL, "crank_rotation": math.pi},
        {"pressure_slide_0": TRAVEL, "crank_rotation": math.pi / 2.0},
    ]
    if r.support_mount in ("classic_boss_clamps", "reinforced_table_clamps"):
        risk[1]["clamp_adjust_0"] = -0.015
        risk[2]["clamp_adjust_0"] = 0.012
    if r.crank_style == "folding_park_crank":
        risk[1]["crank_fold"] = math.pi / 2.0
    if r.feed_module == "fold_down_shelf":
        risk[2]["feed_shelf_fold"] = math.pi / 2.0
    model.meta["risk_poses"] = tuple(risk)
    model.meta["coupled_joint_pairs"] = (("pressure_slide_0", "crank_rotation"),)
    return model


def build_seeded_picturex_0611_hand_crank_clothes_wringer(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_picturex_0611_hand_crank_clothes_wringer(config_from_seed(seed), assets=assets)


# --- authored tests -----------------------------------------------------------
def _parts_by_role(model: ArticulatedObject, role: str):
    return [p for p in model.parts if p.meta.get("role") == role]


def run_picturex_0611_hand_crank_clothes_wringer_tests(
    model: ArticulatedObject, config: Config
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)
    if r.feed_module == "fold_down_shelf":
        ctx.allow_isolated_part(
            "feed_module__fold_down_shelf__shelf",
            reason="bounded hinge barrels retain the shelf with a deliberate running clearance",
        )
    if r.crank_style == "folding_park_crank":
        ctx.allow_isolated_part(
            "crank_style__folding_park_crank__handle",
            reason="bounded hinge pin retains the folding handle with a deliberate running clearance",
        )

    frames = _parts_by_role(model, "frame")
    rollers = _parts_by_role(model, "roller")
    upper = [p for p in rollers if p.meta.get("position") == "upper"]
    cranks = _parts_by_role(model, "crank_drive")
    blocks = _parts_by_role(model, "pressure_block")
    joints = {j.name: j for j in model.articulations}

    def _is_cont_x(name: str) -> bool:
        j = joints.get(name)
        return (
            j is not None
            and j.articulation_type == ArticulationType.CONTINUOUS
            and tuple(round(abs(v), 6) for v in j.axis) == (1.0, 0.0, 0.0)
        )

    def _is_pris_z(name: str) -> bool:
        j = joints.get(name)
        return (
            j is not None
            and j.articulation_type == ArticulationType.PRISMATIC
            and tuple(round(v, 6) for v in j.axis) == (0.0, 0.0, 1.0)
            and j.motion_limits is not None
            and j.motion_limits.upper > j.motion_limits.lower
        )

    ctx.check(
        "category_anchor: hand-crank wringer nip and drive chain",
        len(frames) == 1
        and len(rollers) == r.roller_count
        and len(upper) == 1
        and len(cranks) == 1
        and len(blocks) == 2
        and bool(model.root_parts())
        and model.root_parts()[0].name == "frame"
        and _is_cont_x("crank_rotation")
        and all(_is_cont_x(f"roller_spin_{i}") for i in range(r.roller_count))
        and _is_pris_z("pressure_slide_0")
        and _is_pris_z("pressure_slide_1")
        and all(joints[f"roller_spin_{i}"].parent == "frame" for i in range(r.roller_count - 1))
        and joints[f"roller_spin_{r.roller_count - 1}"].parent == "pressure_block_0"
        and joints["crank_rotation"].parent == "pressure_block_1"
        and all(
            joints[f"roller_spin_{i}"].mimic is not None
            and joints[f"roller_spin_{i}"].mimic.joint == "crank_rotation"
            for i in range(r.roller_count)
        ),
        details=(
            f"frames={len(frames)} rollers={len(rollers)} upper={len(upper)} "
            f"cranks={len(cranks)} blocks={len(blocks)} joints={sorted(joints)}"
        ),
    )

    # Every axle runs in a real bore with a running fit under the 1 mm assembly
    # tolerance, and the nip stays closed to a real wringing gap.
    ctx.check(
        "category_anchor: rollers stay journalled in their bearing bores",
        0.0 < FIT <= 0.001
        and r.block_h > 2.0 * (AXLE_R + FIT)
        and abs(r.nip_centre_distance_m - (2.0 * r.roller_radius_m + NIP)) < 1e-9
        and abs(
            r.upper_axis_z
            - r.lower_axis_z
            - (r.roller_count - 1) * r.nip_centre_distance_m
        )
        < 1e-9
        and r.bearing_plane_x_m > 0.5 * r.roller_length_m + 0.5 * BLOCK_W
        and r.top_beam_bottom_z >= r.upper_axis_z + TRAVEL + 0.5 * r.block_h + 0.013,
        details=(
            f"fit={FIT} block_h={r.block_h} centre_distance={r.nip_centre_distance_m} "
            f"bearing_x={r.bearing_plane_x_m} beam_bottom={r.top_beam_bottom_z}"
        ),
    )

    visual_names = {v.name or "" for p in model.parts for v in p.visuals}
    support_ok = {
        "classic_boss_clamps": any("classic_boss_clamps__boss" in n for n in visual_names)
        and len(_parts_by_role(model, "mount_clamp")) == 2,
        "reinforced_table_clamps": any(
            "reinforced_table_clamps__deep_bracket" in n for n in visual_names
        )
        and len(_parts_by_role(model, "mount_clamp")) == 2,
        "freestanding_floor_frame": any(
            "freestanding_floor_frame__brace" in n for n in visual_names
        )
        and sum(1 for n in visual_names if "freestanding_floor_frame__leg" in n) == 4,
        "wall_bench_bracket": any("wall_bench_bracket__rear_plate" in n for n in visual_names)
        and sum(1 for n in visual_names if "wall_bench_bracket__wall_bolt" in n) == 4,
    }[r.support_mount]
    ctx.check(
        "category_anchor: support_mount identity",
        support_ok,
        details=f"support_mount={r.support_mount}",
    )

    ctx.check(
        "category_anchor: roller_bank multiplicity",
        len(rollers) == r.roller_count
        and sum(1 for n in visual_names if "__rubber_" in n) == r.roller_count
        and all(f"roller_spin_{i}" in joints for i in range(r.roller_count)),
        details=f"roller_count={r.roller_count}",
    )

    adjusters = _parts_by_role(model, "pressure_adjuster")
    pressure_ok = {
        "centre_screw": len(adjusters) == 1
        and any("centre_screw__handle" in n for n in visual_names)
        and joints.get("pressure_screw_turn") is not None
        and joints["pressure_screw_turn"].articulation_type == ArticulationType.CONTINUOUS,
        "overhead_screw_bridge": len(adjusters) == 1
        and any("overhead_screw_bridge__crossbar" in n for n in visual_names)
        and "bridge_screw_turn" in joints,
        "spring_loaded_bridge": len(adjusters) == 2
        and sum(1 for n in visual_names if "spring_loaded_bridge__coil_spring" in n) == 2,
        "dual_handwheels": len(adjusters) == 2
        and sum(1 for n in visual_names if "dual_handwheels__handwheel" in n) == 2
        and all(f"handwheel_turn_{i}" in joints for i in range(2)),
    }[r.pressure_mechanism]
    ctx.check(
        "category_anchor: pressure_mechanism identity",
        pressure_ok,
        details=f"pressure_mechanism={r.pressure_mechanism} adjusters={len(adjusters)}",
    )

    # Motion evidence: the pressure carriers really open the nip.
    slide = joints["pressure_slide_0"]
    rest = ctx.part_world_aabb(upper[0])
    with ctx.pose({slide: TRAVEL}):
        raised = ctx.part_world_aabb(upper[0])
    ctx.check(
        "the pressure carriers lift the upper roller by the full travel",
        rest is not None
        and raised is not None
        and abs((raised[0][2] - rest[0][2]) - TRAVEL) < 1e-3,
        details=f"rest={rest} raised={raised}",
    )

    # Motion evidence: the crank swings a real arc outboard of the frame.
    crank_joint = joints["crank_rotation"]
    motion_part = (
        _parts_by_role(model, "crank_handle")[0]
        if r.crank_style == "folding_park_crank"
        else cranks[0]
    )
    crank_rest = ctx.part_world_aabb(motion_part)
    with ctx.pose({crank_joint: math.pi / 2.0}):
        crank_quarter = ctx.part_world_aabb(motion_part)
    ctx.check(
        "the hand crank turns about the upper roller axis outboard of the frame",
        crank_rest is not None
        and crank_quarter is not None
        and crank_rest[0][0] > r.half_x - 0.001
        and max(abs(crank_quarter[0][1]), abs(crank_quarter[1][1]))
        > max(abs(crank_rest[0][1]), abs(crank_rest[1][1])) + 0.5 * r.crank_throw,
        details=f"rest={crank_rest} quarter={crank_quarter} half_x={r.half_x}",
    )

    crank_ok = {
        "fixed_bent_crank": len(_parts_by_role(model, "crank_handle")) == 0
        and any("fixed_bent_crank__arm" in n for n in visual_names),
        "folding_park_crank": len(_parts_by_role(model, "crank_handle")) == 1
        and "crank_fold" in joints
        and joints["crank_fold"].articulation_type == ArticulationType.REVOLUTE,
    }[r.crank_style]
    ctx.check(
        "category_anchor: crank_style identity",
        crank_ok,
        details=f"crank_style={r.crank_style}",
    )

    feed_ok = {
        "plain_front_apron": len(_parts_by_role(model, "feed_shelf")) == 0
        and any("plain_front_apron__apron" in n for n in visual_names),
        "fold_down_shelf": len(_parts_by_role(model, "feed_shelf")) == 1
        and "feed_shelf_fold" in joints
        and joints["feed_shelf_fold"].articulation_type == ArticulationType.REVOLUTE,
    }[r.feed_module]
    ctx.check(
        "category_anchor: feed_module identity",
        feed_ok,
        details=f"feed_module={r.feed_module}",
    )

    ctx.check(
        "domain choices recorded on the model",
        model.meta.get("slot_choices") == slot_choices_for_config(r),
    )
    return ctx.report()


TEMPLATE_CORNERS = (
    corner_case(
        "min_two_roller_classic_centre_plain",
        {
            "support_mount": "classic_boss_clamps",
            "pressure_mechanism": "centre_screw",
            "crank_style": "fixed_bent_crank",
            "feed_module": "plain_front_apron",
            "roller_count": 2,
            "roller_length_m": 0.280,
            "roller_radius_m": 0.024,
            "frame_height_m": 0.200,
        },
        reason="smallest two-roller baseline with compact clamps and centre screw",
    ),
    corner_case(
        "max_three_roller_floor_dual_folding_shelf",
        {
            "support_mount": "freestanding_floor_frame",
            "pressure_mechanism": "dual_handwheels",
            "crank_style": "folding_park_crank",
            "feed_module": "fold_down_shelf",
            "roller_count": 3,
            "roller_length_m": 0.420,
            "roller_radius_m": 0.040,
            "frame_height_m": 0.300,
        },
        reason="largest envelope, maximum part count, and both bounded folding joints",
    ),
    corner_case(
        "three_roller_wall_bridge_headroom",
        {
            "support_mount": "wall_bench_bracket",
            "pressure_mechanism": "overhead_screw_bridge",
            "crank_style": "fixed_bent_crank",
            "feed_module": "fold_down_shelf",
            "roller_count": 3,
            "roller_length_m": 0.280,
            "roller_radius_m": 0.040,
            "frame_height_m": 0.200,
        },
        reason="largest roller stack under the shortest request tests derived headroom",
    ),
    corner_case(
        "wide_reinforced_spring_folding",
        {
            "support_mount": "reinforced_table_clamps",
            "pressure_mechanism": "spring_loaded_bridge",
            "crank_style": "folding_park_crank",
            "feed_module": "plain_front_apron",
            "roller_count": 2,
            "roller_length_m": 0.420,
            "roller_radius_m": 0.024,
            "frame_height_m": 0.300,
        },
        reason="widest beam with deep clamps, spring bridge, and parked crank",
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
    "build_picturex_0611_hand_crank_clothes_wringer",
    "build_seeded_picturex_0611_hand_crank_clothes_wringer",
    "run_picturex_0611_hand_crank_clothes_wringer_tests",
]
