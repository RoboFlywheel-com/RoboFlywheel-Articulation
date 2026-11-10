# SPDX-License-Identifier: Apache-2.0

"""Self-contained vertical hydraulic bottle/ram jack template.

One rigid ``jack_frame`` root carries the painted cylinder shell, the
horizontal hand-pump body, the manifold and the routed hydraulic hose.
``ram_stage_count`` nested telescopic ``ram_stage`` tubes extend upward out of
that bore -- stage 0 is a PRISMATIC (+z) child of the frame and stage ``i`` is a
PRISMATIC (+z) child of stage ``i-1``.  Every stage keeps a real guide land
inside the next larger bore over its whole stroke, so no stage becomes an
isolated part at full extension.  A ``head_fitting`` rides the topmost stage, a
``pump_handle`` swings in a real two-eared clevis, and a ``release_valve`` knob
screws on the pump body.

Four component slots vary without touching the mechanism: ``ram_stage`` (stage
tube form), ``head_fitting`` (load interface), ``pump_drive`` (bare lever versus
air-over-hydraulic module) and ``base_mount`` (base footprint, which derives the
frame's floor lift).  No source-replay import, no motion clamping, no whole-part
overlap allowance.
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
    LatheGeometry,
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
    tube_from_spline_points,
)

RamStage = Literal["chrome_rod", "stepped_ram"]
HeadFitting = Literal["flat_saddle", "screw_extension", "grooved_cradle"]
PumpDrive = Literal["lever_pump", "air_over_hydraulic"]
BaseMount = Literal["flat_pad", "flanged_bolt", "channel_skid"]
PaletteStyle = Literal["safety_yellow", "signal_red", "works_blue", "graphite"]

RAM_STAGES: tuple[RamStage, ...] = ("chrome_rod", "stepped_ram")
HEAD_FITTINGS: tuple[HeadFitting, ...] = ("flat_saddle", "screw_extension", "grooved_cradle")
PUMP_DRIVES: tuple[PumpDrive, ...] = ("lever_pump", "air_over_hydraulic")
BASE_MOUNTS: tuple[BaseMount, ...] = ("flat_pad", "flanged_bolt", "channel_skid")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "safety_yellow",
    "signal_red",
    "works_blue",
    "graphite",
)


TEMPLATE_DOMAIN = TemplateDomain(
    slots=(
        component_slot("ram_stage", RAM_STAGES),
        component_slot("head_fitting", HEAD_FITTINGS),
        component_slot("pump_drive", PUMP_DRIVES),
        component_slot("base_mount", BASE_MOUNTS),
        multiplicity_slot("ram_stage_count", (1, 2, 3), item_slot="ram_stage"),
    )
)


PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "safety_yellow": {
        "paint": (0.94, 0.74, 0.09, 1.0),
        "dark": (0.10, 0.10, 0.11, 1.0),
        "chrome": (0.78, 0.81, 0.84, 1.0),
        "steel": (0.30, 0.32, 0.34, 1.0),
        "rubber": (0.05, 0.05, 0.06, 1.0),
        "label": (0.93, 0.90, 0.72, 1.0),
    },
    "signal_red": {
        "paint": (0.72, 0.13, 0.11, 1.0),
        "dark": (0.10, 0.09, 0.09, 1.0),
        "chrome": (0.80, 0.82, 0.85, 1.0),
        "steel": (0.34, 0.34, 0.36, 1.0),
        "rubber": (0.06, 0.05, 0.05, 1.0),
        "label": (0.94, 0.92, 0.86, 1.0),
    },
    "works_blue": {
        "paint": (0.13, 0.28, 0.55, 1.0),
        "dark": (0.08, 0.10, 0.14, 1.0),
        "chrome": (0.76, 0.79, 0.83, 1.0),
        "steel": (0.29, 0.32, 0.37, 1.0),
        "rubber": (0.05, 0.05, 0.07, 1.0),
        "label": (0.90, 0.92, 0.94, 1.0),
    },
    "graphite": {
        "paint": (0.22, 0.23, 0.24, 1.0),
        "dark": (0.07, 0.07, 0.08, 1.0),
        "chrome": (0.82, 0.84, 0.86, 1.0),
        "steel": (0.42, 0.44, 0.46, 1.0),
        "rubber": (0.05, 0.05, 0.05, 1.0),
        "label": (0.88, 0.88, 0.86, 1.0),
    },
}


# Fixed manufacturing cross-sections (surface detail, not core/raw).
BASE_T = 0.018          # base plate thickness
SHELL_WALL = 0.010      # cylinder shell wall
STAGE_WALL = 0.006      # telescopic stage tube wall
# Radial running clearance between a stage and the bore it slides in.  It is
# under the 1 mm assembly-gap tolerance, so QC reads the stage as journalled
# (supported) rather than as an isolated part, without any penetration.
CLEAR = 0.0008
# Sub-millimetre mount lap: a fitting laps its host by less than the collision
# tolerance so QC reads real contact without an overlap allowance.
MOUNT = 0.0006
CLEVIS_HALF = 0.018     # clevis ear centre offset in y
CLEVIS_EAR_T = 0.011    # clevis ear thickness in y
# Stage proportions.  Length 0.85*H leaves 0.30*H of guide land engaged at full
# stroke (0.55*H); the 0.82 ratio per stage keeps each inner stage genuinely
# nested inside its host at full retraction.
STAGE_LEN_FRAC = 0.85
STAGE_STROKE_FRAC = 0.55
STAGE_RATIO = 0.82


@dataclass(frozen=True)
class Config:
    ram_stage: RamStage = "chrome_rod"
    head_fitting: HeadFitting = "flat_saddle"
    pump_drive: PumpDrive = "lever_pump"
    base_mount: BaseMount = "flat_pad"
    ram_stage_count: int = 1
    body_height_m: float | None = None
    bore_radius_m: float | None = None
    pump_reach_m: float | None = None
    palette_style: PaletteStyle = "safety_yellow"
    name: str = "pictureX_0611_hydraulic_jack1"


@dataclass(frozen=True)
class ResolvedConfig:
    ram_stage: RamStage
    head_fitting: HeadFitting
    pump_drive: PumpDrive
    base_mount: BaseMount
    ram_stage_count: int
    palette_style: PaletteStyle
    palette: dict[str, tuple[float, float, float, float]]
    body_height_m: float
    bore_radius_m: float
    pump_reach_m: float
    base_lift_m: float
    base_top_z: float
    shell_top_z: float
    shell_inner_r: float
    stage_outer_r: tuple[float, ...]
    stage_len: tuple[float, ...]
    stage_stroke: tuple[float, ...]
    pump_r: float
    pump_x0: float
    pump_x1: float
    pump_axis_z: float
    clevis_x: float
    clevis_z: float
    handle_len: float
    base_x0: float
    base_x1: float
    base_y_half: float
    name: str


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(value)))


def config_from_seed(seed: int) -> Config:
    rng = random.Random(int(seed) ^ 0x11D2_0AC1)
    choices = TEMPLATE_DOMAIN.sample(rng)
    return Config(
        ram_stage=choices["ram_stage"],
        head_fitting=choices["head_fitting"],
        pump_drive=choices["pump_drive"],
        base_mount=choices["base_mount"],
        ram_stage_count=choices["ram_stage_count"],
        body_height_m=round(rng.uniform(0.150, 0.240), 4),
        bore_radius_m=round(rng.uniform(0.036, 0.056), 4),
        pump_reach_m=round(rng.uniform(0.150, 0.230), 4),
        palette_style=rng.choice(PALETTE_STYLES),
        name=f"hydraulic_jack1_seed_{int(seed)}",
    )


_BASE_LIFT = {"flat_pad": 0.0, "flanged_bolt": 0.0, "channel_skid": 0.014}


def resolve_config(config: Config) -> ResolvedConfig:
    TEMPLATE_DOMAIN.validate(
        {
            "ram_stage": config.ram_stage,
            "head_fitting": config.head_fitting,
            "pump_drive": config.pump_drive,
            "base_mount": config.base_mount,
            "ram_stage_count": config.ram_stage_count,
        }
    )
    if config.palette_style not in PALETTES:
        raise ValueError(f"unsupported palette_style: {config.palette_style}")
    if config.body_height_m is not None and not 0.150 <= float(config.body_height_m) <= 0.240:
        raise ValueError("body_height_m must be in [0.150, 0.240]")
    if config.bore_radius_m is not None and not 0.036 <= float(config.bore_radius_m) <= 0.056:
        raise ValueError("bore_radius_m must be in [0.036, 0.056]")
    if config.pump_reach_m is not None and not 0.150 <= float(config.pump_reach_m) <= 0.230:
        raise ValueError("pump_reach_m must be in [0.150, 0.230]")

    height = _clamp(config.body_height_m, 0.150, 0.240) if config.body_height_m is not None else 0.190
    bore = _clamp(config.bore_radius_m, 0.036, 0.056) if config.bore_radius_m is not None else 0.046
    reach = _clamp(config.pump_reach_m, 0.150, 0.230) if config.pump_reach_m is not None else 0.190

    lift = _BASE_LIFT[config.base_mount]
    base_top = lift + BASE_T
    shell_top = base_top + height
    shell_inner = bore - SHELL_WALL

    n = int(config.ram_stage_count)
    outer: list[float] = []
    lengths: list[float] = []
    strokes: list[float] = []
    free_bore = shell_inner
    for i in range(n):
        r_out = free_bore - CLEAR
        outer.append(r_out)
        free_bore = r_out - STAGE_WALL
        lengths.append(STAGE_LEN_FRAC * height * (STAGE_RATIO**i))
        strokes.append(STAGE_STROKE_FRAC * height * (STAGE_RATIO**i))

    pump_r = bore * 0.62
    pump_axis_z = base_top + pump_r + 0.006
    pump_x0 = bore + 0.008
    pump_x1 = pump_x0 + reach
    clevis_x = pump_x1 - 0.010
    clevis_z = pump_axis_z + pump_r + 0.030
    handle_len = 0.90 * reach + 0.10
    base_x0 = -(bore + 0.014)
    base_x1 = pump_x1 + 0.026
    base_y_half = max(bore + 0.016, pump_r + 0.014, CLEVIS_HALF + 0.014)

    return ResolvedConfig(
        ram_stage=config.ram_stage,
        head_fitting=config.head_fitting,
        pump_drive=config.pump_drive,
        base_mount=config.base_mount,
        ram_stage_count=n,
        palette_style=config.palette_style,
        palette=dict(PALETTES[config.palette_style]),
        body_height_m=height,
        bore_radius_m=bore,
        pump_reach_m=reach,
        base_lift_m=lift,
        base_top_z=base_top,
        shell_top_z=shell_top,
        shell_inner_r=shell_inner,
        stage_outer_r=tuple(outer),
        stage_len=tuple(lengths),
        stage_stroke=tuple(strokes),
        pump_r=pump_r,
        pump_x0=pump_x0,
        pump_x1=pump_x1,
        pump_axis_z=pump_axis_z,
        clevis_x=clevis_x,
        clevis_z=clevis_z,
        handle_len=handle_len,
        base_x0=base_x0,
        base_x1=base_x1,
        base_y_half=base_y_half,
        name=config.name,
    )


def slot_choices_for_config(config: Config | ResolvedConfig) -> tuple[tuple[str, object], ...]:
    return (
        ("ram_stage", config.ram_stage),
        ("head_fitting", config.head_fitting),
        ("pump_drive", config.pump_drive),
        ("base_mount", config.base_mount),
        ("ram_stage_count", config.ram_stage_count),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, object], ...]:
    return slot_choices_for_config(config_from_seed(seed))


def _materials(model: ArticulatedObject, r: ResolvedConfig) -> dict[str, str]:
    mats: dict[str, str] = {}
    for key, rgba in r.palette.items():
        model.material(f"jack1_{r.palette_style}_{key}", rgba=rgba)
        mats[key] = f"jack1_{r.palette_style}_{key}"
    return mats


def _tube(name: str, outer_r: float, inner_r: float, z0: float, z1: float, segments: int = 28):
    """A real hollow tube: a revolved shell, not a capped solid cylinder."""
    return mesh_from_geometry(
        LatheGeometry.from_shell_profiles(
            [(outer_r, z0), (outer_r, z1)],
            [(inner_r, z0), (inner_r, z1)],
            segments=segments,
        ),
        name,
    )


def _y_cyl(part, name: str, radius: float, length: float, xyz, material: str) -> None:
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=Origin(xyz=xyz, rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=material,
        name=name, material_class_id="metal.chrome_polished",
    )


def _x_cyl(part, name: str, radius: float, length: float, xyz, material: str) -> None:
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=Origin(xyz=xyz, rpy=(0.0, math.pi / 2.0, 0.0)),
        material=material,
        name=name, material_class_id="metal.paint_coated",
    )


def _rev_axis_joint(
    model: ArticulatedObject,
    *,
    name: str,
    parent,
    child,
    point: tuple[float, float, float],
    axis: tuple[float, float, float],
    provider_radial: tuple[float, float, float],
    consumer_radial: tuple[float, float, float],
    lower: float,
    upper: float,
    effort: float,
    velocity: float,
) -> None:
    provider = AxisInterface(name=f"{name}__provider", point=point, axis=axis, radial=provider_radial)
    consumer = AxisInterface(name=f"{name}__consumer", axis=axis, radial=consumer_radial)
    mate = mate_axes(provider, consumer)
    model.articulation(
        name,
        ArticulationType.REVOLUTE,
        parent=parent,
        child=child,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(lower=lower, upper=upper, effort=effort, velocity=velocity),
    )
    register_interface_mate(model, name, mate)


# --- base mount candidates (frame footprint) --------------------------------
def _base_mount_flat_pad_build(frame, r: ResolvedConfig, mats: dict[str, str]) -> None:
    cx = 0.5 * (r.base_x0 + r.base_x1)
    frame.visual(
        Box((r.base_x1 - r.base_x0, 2.0 * r.base_y_half, BASE_T)),
        origin=Origin(xyz=(cx, 0.0, r.base_lift_m + BASE_T * 0.5)),
        material=mats["dark"],
        name="base_mount__flat_pad__plate", material_class_id="metal.blackened_gunmetal",
    )
    # Rolled-edge rim: the pressed pad of a bottle jack is not a bare slab.
    for i, sy in enumerate((-1.0, 1.0)):
        frame.visual(
            Box((r.base_x1 - r.base_x0, 0.008, 0.008)),
            origin=Origin(xyz=(cx, sy * (r.base_y_half - 0.004), r.base_lift_m + BASE_T + 0.003)),
            material=mats["dark"],
            name=f"base_mount__flat_pad__rim_{i}", material_class_id="metal.blackened_gunmetal",
        )


def _base_mount_flanged_bolt_build(frame, r: ResolvedConfig, mats: dict[str, str]) -> None:
    cx = 0.5 * (r.base_x0 + r.base_x1)
    half_y = r.base_y_half + 0.016
    frame.visual(
        Box((r.base_x1 - r.base_x0 + 0.024, 2.0 * half_y, BASE_T)),
        origin=Origin(xyz=(cx, 0.0, r.base_lift_m + BASE_T * 0.5)),
        material=mats["dark"],
        name="base_mount__flanged_bolt__plate", material_class_id="metal.blackened_gunmetal",
    )
    index = 0
    for sx in (r.base_x0 - 0.001, r.base_x1 + 0.001):
        for sy in (-(half_y - 0.013), half_y - 0.013):
            frame.visual(
                Cylinder(radius=0.010, length=BASE_T + 0.010),
                origin=Origin(xyz=(sx, sy, r.base_lift_m + (BASE_T + 0.010) * 0.5)),
                material=mats["steel"],
                name=f"base_mount__flanged_bolt__boss_{index}", material_class_id="metal.steel_bare",
            )
            frame.visual(
                Cylinder(radius=0.006, length=0.006),
                origin=Origin(xyz=(sx, sy, r.base_lift_m + BASE_T + 0.011)),
                material=mats["chrome"],
                name=f"base_mount__flanged_bolt__head_{index}", material_class_id="metal.chrome_polished",
            )
            index += 1


def _base_mount_channel_skid_build(frame, r: ResolvedConfig, mats: dict[str, str]) -> None:
    cx = 0.5 * (r.base_x0 + r.base_x1)
    length = r.base_x1 - r.base_x0
    frame.visual(
        Box((length, 2.0 * r.base_y_half, BASE_T)),
        origin=Origin(xyz=(cx, 0.0, r.base_lift_m + BASE_T * 0.5)),
        material=mats["dark"],
        name="base_mount__channel_skid__plate", material_class_id="metal.blackened_gunmetal",
    )
    for i, sy in enumerate((-1.0, 1.0)):
        y = sy * (r.base_y_half - 0.012)
        frame.visual(
            Box((length * 0.94, 0.020, r.base_lift_m + MOUNT)),
            origin=Origin(xyz=(cx, y, (r.base_lift_m + MOUNT) * 0.5)),
            material=mats["steel"],
            name=f"base_mount__channel_skid__skid_{i}", material_class_id="metal.steel_bare",
        )
        # Channel webs: the skid is a folded section, not a solid bar.
        frame.visual(
            Box((length * 0.94, 0.006, 0.010)),
            origin=Origin(xyz=(cx, y + sy * 0.010, r.base_lift_m - 0.005)),
            material=mats["steel"],
            name=f"base_mount__channel_skid__web_{i}", material_class_id="metal.steel_bare",
        )
    # Front toe plate: the skid variant reaches under a low load edge.
    frame.visual(
        Box((0.036, 2.0 * r.base_y_half * 0.7, 0.010)),
        origin=Origin(xyz=(r.base_x0 - 0.017, 0.0, r.base_lift_m + 0.005)),
        material=mats["steel"],
        name="base_mount__channel_skid__toe_plate", material_class_id="metal.steel_bare",
    )


_BASE_MOUNT_BUILDERS = {
    "flat_pad": _base_mount_flat_pad_build,
    "flanged_bolt": _base_mount_flanged_bolt_build,
    "channel_skid": _base_mount_channel_skid_build,
}


# --- frame ------------------------------------------------------------------
def _build_frame(model: ArticulatedObject, r: ResolvedConfig, mats: dict[str, str]):
    frame = model.part("jack_frame", meta={"role": "jack_frame"})
    _BASE_MOUNT_BUILDERS[r.base_mount](frame, r, mats)

    # Hydraulic cylinder: a real hollow shell whose bore carries the ram.
    frame.visual(
        _tube("ram_cylinder_shell", r.bore_radius_m, r.shell_inner_r, 0.0, r.body_height_m, 32),
        origin=Origin(xyz=(0.0, 0.0, r.base_top_z - MOUNT)),
        material=mats["paint"],
        name="cylinder_shell", material_class_id="metal.paint_coated",
    )
    # Closed bottom cap (the oil reservoir floor) so the shell is not an open pipe.
    frame.visual(
        Cylinder(radius=r.shell_inner_r + MOUNT, length=0.010),
        origin=Origin(xyz=(0.0, 0.0, r.base_top_z + 0.004)),
        material=mats["dark"],
        name="cylinder_floor", material_class_id="metal.blackened_gunmetal",
    )
    frame.visual(
        _tube("ram_top_collar", r.bore_radius_m + 0.006, r.shell_inner_r + 0.002, 0.0, 0.016, 32),
        origin=Origin(xyz=(0.0, 0.0, r.shell_top_z - 0.016)),
        material=mats["paint"],
        name="top_collar", material_class_id="metal.paint_coated",
    )
    # The seal lip closes onto the outermost stage with a 0.4 mm running gap:
    # real sealing contact under the 1 mm tolerance, never a ring cut into the ram.
    frame.visual(
        _tube(
            "ram_wiper_seal",
            r.shell_inner_r + 0.0015,
            r.stage_outer_r[0] + 0.0004,
            0.0,
            0.006,
            24,
        ),
        origin=Origin(xyz=(0.0, 0.0, r.shell_top_z - 0.004)),
        material=mats["rubber"],
        name="wiper_seal", material_class_id="rubber.smooth_plain",
    )
    # Instruction plate on the shell face (image-specific, unreadable surface).
    frame.visual(
        Box((0.030, 0.0025, r.body_height_m * 0.42)),
        origin=Origin(
            xyz=(0.0, -(r.bore_radius_m - 0.001), r.base_top_z + r.body_height_m * 0.48)
        ),
        material=mats["label"],
        name="instruction_plate", material_class_id="paper.plain_sheet",
    )

    # Horizontal hand-pump body sitting on the base plate.
    pr = r.pump_r
    _x_cyl(
        frame,
        "pump_body",
        pr,
        r.pump_x1 - r.pump_x0,
        (0.5 * (r.pump_x0 + r.pump_x1), 0.0, r.pump_axis_z),
        mats["paint"],
    )
    _x_cyl(frame, "pump_end_block", pr + 0.003, 0.016, (r.pump_x1 + 0.006, 0.0, r.pump_axis_z), mats["dark"])
    frame.visual(
        Box((r.pump_x1 - r.pump_x0 - 0.010, 2.0 * pr * 0.72, r.pump_axis_z - r.base_top_z + MOUNT)),
        origin=Origin(
            xyz=(
                0.5 * (r.pump_x0 + r.pump_x1),
                0.0,
                0.5 * (r.base_top_z + r.pump_axis_z) - MOUNT * 0.5,
            )
        ),
        material=mats["dark"],
        name="pump_foot", material_class_id="metal.blackened_gunmetal",
    )
    # Neck tying the pump body back into the cylinder shell.  It lands in the
    # shell WALL (from bore_radius - 3 mm outward) and never crosses the bore,
    # which is swept by the ram over its whole stroke.
    neck_x0 = r.bore_radius_m - 0.003
    neck_x1 = r.pump_x0 + 0.006
    frame.visual(
        Box((neck_x1 - neck_x0, 0.026, 0.020)),
        origin=Origin(xyz=(0.5 * (neck_x0 + neck_x1), 0.0, r.base_top_z + 0.028)),
        material=mats["steel"],
        name="pump_neck", material_class_id="metal.steel_bare",
    )
    frame.visual(
        Cylinder(radius=0.007, length=0.010),
        origin=Origin(xyz=(r.pump_x0 + 0.030, 0.0, r.pump_axis_z + pr - 0.002)),
        material=mats["dark"],
        name="filler_plug", material_class_id="metal.blackened_gunmetal",
    )

    # Pump-handle clevis: two ears leaving a real gap for the handle boss.
    for i, sy in enumerate((-1.0, 1.0)):
        frame.visual(
            Box((0.030, CLEVIS_EAR_T, r.clevis_z - r.pump_axis_z + 0.028)),
            origin=Origin(
                xyz=(
                    r.clevis_x,
                    sy * CLEVIS_HALF,
                    0.5 * (r.pump_axis_z + r.clevis_z + 0.028) - 0.014,
                )
            ),
            material=mats["dark"],
            name=f"clevis_ear_{i}", material_class_id="metal.blackened_gunmetal",
        )
        _y_cyl(
            frame,
            f"clevis_bolt_{i}",
            0.0075,
            0.004,
            (r.clevis_x, sy * (CLEVIS_HALF + CLEVIS_EAR_T * 0.5 + 0.001), r.clevis_z),
            mats["chrome"],
        )
    frame.visual(
        Box((0.040, 2.0 * CLEVIS_HALF, 0.012)),
        origin=Origin(xyz=(r.clevis_x, 0.0, r.pump_axis_z + pr + 0.004)),
        material=mats["dark"],
        name="clevis_bridge", material_class_id="metal.blackened_gunmetal",
    )

    # Manifold, coupling and routed high-pressure hose (image 001 identity).
    manifold_x = -(r.bore_radius_m + 0.010)
    frame.visual(
        Box((0.024, 0.026, 0.022)),
        origin=Origin(xyz=(manifold_x + 0.006, 0.0, r.base_top_z + 0.030)),
        material=mats["steel"],
        name="ram_manifold", material_class_id="metal.steel_bare",
    )
    _x_cyl(frame, "ram_coupling", 0.008, 0.020, (manifold_x - 0.006, 0.0, r.base_top_z + 0.030), mats["chrome"])
    _y_cyl(
        frame,
        "pump_coupling",
        0.008,
        0.018,
        (r.pump_x0 + 0.048, -(pr + 0.006), r.pump_axis_z),
        mats["chrome"],
    )
    hose_points = [
        (r.pump_x0 + 0.048, -(pr + 0.012), r.pump_axis_z),
        (r.pump_x0 + 0.030, -(pr + 0.045), r.pump_axis_z - 0.004),
        (r.bore_radius_m * 0.4, -(pr + 0.060), r.base_top_z + 0.034),
        (manifold_x - 0.030, -(pr + 0.040), r.base_top_z + 0.032),
        (manifold_x - 0.014, -0.004, r.base_top_z + 0.030),
    ]
    frame.visual(
        mesh_from_geometry(
            tube_from_spline_points(
                hose_points,
                radius=0.0055,
                samples_per_segment=8,
                radial_segments=12,
                cap_ends=True,
            ),
            "hydraulic_hose",
        ),
        material=mats["rubber"],
        name="hydraulic_hose", material_class_id="rubber.smooth_plain",
    )
    return frame


# --- ram stage candidates ---------------------------------------------------
def _ram_stage_chrome_rod_build(
    part, r: ResolvedConfig, mats: dict[str, str], index: int, innermost: bool
) -> None:
    length = r.stage_len[index]
    ro = r.stage_outer_r[index]
    if innermost:
        part.visual(
            Cylinder(radius=ro, length=length),
            origin=Origin(xyz=(0.0, 0.0, -length * 0.5)),
            material=mats["chrome"],
            name=f"ram_stage__chrome_rod__rod_{index}", material_class_id="metal.chrome_polished",
        )
    else:
        part.visual(
            _tube(f"chrome_rod_tube_{index}", ro, ro - STAGE_WALL, -length, 0.0, 28),
            material=mats["chrome"],
            name=f"ram_stage__chrome_rod__tube_{index}", material_class_id="metal.chrome_polished",
        )
    # Guide land at the bottom: the running fit that keeps the stage journalled.
    # It stands 0.5 mm proud of the stage, inside the CLEAR running gap, so it
    # bears on the host bore without cutting into it.
    part.visual(
        _tube(f"chrome_rod_land_{index}", ro + 0.0005, ro - STAGE_WALL * 0.5, 0.0, 0.010, 24),
        origin=Origin(xyz=(0.0, 0.0, -length + 0.002)),
        material=mats["steel"],
        name=f"ram_stage__chrome_rod__land_{index}", material_class_id="metal.steel_bare",
    )


def _ram_stage_stepped_ram_build(
    part, r: ResolvedConfig, mats: dict[str, str], index: int, innermost: bool
) -> None:
    length = r.stage_len[index]
    ro = r.stage_outer_r[index]
    # The turned-down neck only reduces the OUTER profile.  The bore stays at
    # ro - STAGE_WALL over the whole stage, or the next stage nested inside it
    # would run straight through the neck wall.
    neck_r = ro - 0.0025
    bore_r = ro - STAGE_WALL
    step_z = -length * 0.36
    if innermost:
        part.visual(
            Cylinder(radius=neck_r, length=-step_z),
            origin=Origin(xyz=(0.0, 0.0, step_z * 0.5)),
            material=mats["chrome"],
            name=f"ram_stage__stepped_ram__neck_{index}", material_class_id="metal.chrome_polished",
        )
        part.visual(
            Cylinder(radius=ro, length=length + step_z),
            origin=Origin(xyz=(0.0, 0.0, step_z - (length + step_z) * 0.5)),
            material=mats["chrome"],
            name=f"ram_stage__stepped_ram__barrel_{index}", material_class_id="metal.chrome_polished",
        )
    else:
        part.visual(
            _tube(f"stepped_neck_{index}", neck_r, bore_r, step_z, 0.0, 28),
            material=mats["chrome"],
            name=f"ram_stage__stepped_ram__neck_{index}", material_class_id="metal.chrome_polished",
        )
        part.visual(
            _tube(f"stepped_barrel_{index}", ro, bore_r, -length, step_z, 28),
            material=mats["chrome"],
            name=f"ram_stage__stepped_ram__barrel_{index}", material_class_id="metal.chrome_polished",
        )
    # Machined shoulder collar at the step: the stepped ram's identifying feature.
    # It stays inside the host bore (0.5 mm proud, under the CLEAR running gap).
    part.visual(
        _tube(f"stepped_shoulder_{index}", ro + 0.0005, neck_r - 0.0008, 0.0, 0.007, 24),
        origin=Origin(xyz=(0.0, 0.0, step_z - 0.0035)),
        material=mats["steel"],
        name=f"ram_stage__stepped_ram__shoulder_{index}", material_class_id="metal.steel_bare",
    )
    part.visual(
        _tube(f"stepped_stop_{index}", ro + 0.0005, ro - STAGE_WALL * 0.5, 0.0, 0.012, 24),
        origin=Origin(xyz=(0.0, 0.0, -length + 0.002)),
        material=mats["steel"],
        name=f"ram_stage__stepped_ram__stop_land_{index}", material_class_id="metal.steel_bare",
    )


_RAM_STAGE_BUILDERS = {
    "chrome_rod": _ram_stage_chrome_rod_build,
    "stepped_ram": _ram_stage_stepped_ram_build,
}


def _head_radius(r: ResolvedConfig) -> float:
    return r.stage_outer_r[-1] + 0.012


# --- head fitting candidates ------------------------------------------------
def _head_fitting_flat_saddle_build(part, r: ResolvedConfig, mats: dict[str, str]) -> None:
    rad = _head_radius(r)
    part.visual(
        Cylinder(radius=rad, length=0.012),
        origin=Origin(xyz=(0.0, 0.0, 0.006 - MOUNT)),
        material=mats["chrome"],
        name="head_fitting__flat_saddle__disc", material_class_id="metal.chrome_polished",
    )
    part.visual(
        _tube("saddle_knurl", rad + 0.0015, rad - 0.004, 0.0, 0.006, 24),
        origin=Origin(xyz=(0.0, 0.0, 0.004 - MOUNT)),
        material=mats["steel"],
        name="head_fitting__flat_saddle__knurl", material_class_id="metal.steel_bare",
    )
    part.visual(
        Cylinder(radius=rad - 0.005, length=0.003),
        origin=Origin(xyz=(0.0, 0.0, 0.0125 - MOUNT)),
        material=mats["dark"],
        name="head_fitting__flat_saddle__face", material_class_id="metal.blackened_gunmetal",
    )


def _head_fitting_screw_extension_build(part, r: ResolvedConfig, mats: dict[str, str]) -> None:
    rad = _head_radius(r)
    stud_len = 0.040 + r.body_height_m * 0.08
    stud_r = rad * 0.52
    part.visual(
        Cylinder(radius=stud_r, length=stud_len + MOUNT),
        origin=Origin(xyz=(0.0, 0.0, (stud_len - MOUNT) * 0.5)),
        material=mats["chrome"],
        name="head_fitting__screw_extension__stud", material_class_id="metal.chrome_polished",
    )
    # Thread ribs: the extension screw reads as threaded, not as a bare pin.
    # Their bore is inside the stud radius, so every rib is one solid with it.
    ribs = 6
    for i in range(ribs):
        z = stud_len * (0.12 + 0.72 * i / max(1, ribs - 1))
        part.visual(
            _tube(f"screw_thread_{i}", stud_r + 0.0015, stud_r - 0.0015, 0.0, 0.0025, 20),
            origin=Origin(xyz=(0.0, 0.0, z)),
            material=mats["chrome"],
            name=f"head_fitting__screw_extension__thread_{i}", material_class_id="metal.chrome_polished",
        )
    part.visual(
        Box((rad * 1.7, rad * 1.7, 0.014)),
        origin=Origin(xyz=(0.0, 0.0, stud_len * 0.30)),
        material=mats["steel"],
        name="head_fitting__screw_extension__collar", material_class_id="metal.steel_bare",
    )
    # The pad must overlap the stud top, not sit a MOUNT above it: the
    # same-part island check runs at 1e-6 m, not at the assembly tolerance.
    part.visual(
        Cylinder(radius=rad, length=0.010),
        origin=Origin(xyz=(0.0, 0.0, stud_len - 0.004)),
        material=mats["dark"],
        name="head_fitting__screw_extension__pad", material_class_id="metal.blackened_gunmetal",
    )


def _head_fitting_grooved_cradle_build(part, r: ResolvedConfig, mats: dict[str, str]) -> None:
    rad = _head_radius(r)
    width = rad * 2.6
    part.visual(
        Box((width, width * 0.72, 0.012)),
        origin=Origin(xyz=(0.0, 0.0, 0.006 - MOUNT)),
        material=mats["steel"],
        name="head_fitting__grooved_cradle__base", material_class_id="metal.steel_bare",
    )
    # Vee groove formed by two inward-tilted cheeks that meet at the groove
    # root, plus raised side lips.  Each cheek's lower end is placed INSIDE the
    # base plate (its rotated bottom lands at y=0, z=0.006), so the whole cradle
    # is one connected solid under the 1e-6 m island check.
    tilt = 0.55
    cheek_len = width * 0.40
    half = cheek_len * 0.5
    dy = half * math.sin(tilt)
    z_c = 0.006 + half * math.cos(tilt)
    top_y = cheek_len * math.sin(tilt)
    top_z = 0.006 + cheek_len * math.cos(tilt)
    for i, sy in enumerate((-1.0, 1.0)):
        part.visual(
            Box((width, 0.010, cheek_len)),
            # Rotating about +x sends the cheek's far end toward -y, so the tilt
            # sign is the OPPOSITE of the side: that puts each cheek's lower end
            # at the groove root (y=0) and its top out at sy*top_y, where the lip
            # sits.  With the sign the other way the lips floated off the cheeks.
            origin=Origin(xyz=(0.0, sy * dy, z_c), rpy=(-sy * tilt, 0.0, 0.0)),
            material=mats["steel"],
            name=f"head_fitting__grooved_cradle__cheek_{i}", material_class_id="metal.steel_bare",
        )
        part.visual(
            Box((width, 0.012, 0.012)),
            origin=Origin(xyz=(0.0, sy * top_y, top_z)),
            material=mats["dark"],
            name=f"head_fitting__grooved_cradle__lip_{i}", material_class_id="metal.blackened_gunmetal",
        )


_HEAD_BUILDERS = {
    "flat_saddle": _head_fitting_flat_saddle_build,
    "screw_extension": _head_fitting_screw_extension_build,
    "grooved_cradle": _head_fitting_grooved_cradle_build,
}


def _build_ram(model: ArticulatedObject, frame, r: ResolvedConfig, mats: dict[str, str]) -> None:
    builder = _RAM_STAGE_BUILDERS[r.ram_stage]
    n = r.ram_stage_count
    parent = frame
    for i in range(n):
        stage = model.part(
            f"ram_stage__{r.ram_stage}__stage_{i}",
            meta={"role": "ram_stage", "index": i},
        )
        builder(stage, r, mats, i, innermost=(i == n - 1))
        joint = "frame_to_ram_stage_0" if i == 0 else f"ram_stage_{i - 1}_to_ram_stage_{i}"
        origin_z = r.shell_top_z if i == 0 else 0.0
        model.articulation(
            joint,
            ArticulationType.PRISMATIC,
            parent=parent,
            child=stage,
            origin=Origin(xyz=(0.0, 0.0, origin_z)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(
                lower=0.0, upper=r.stage_stroke[i], effort=90000.0, velocity=0.03
            ),
            meta={"positive_motion": "extends the ram stage upward"},
        )
        parent = stage

    head = model.part(
        f"head_fitting__{r.head_fitting}__head",
        meta={"role": "head_fitting"},
    )
    _HEAD_BUILDERS[r.head_fitting](head, r, mats)
    if r.head_fitting == "screw_extension":
        _rev_axis_joint(
            model,
            name="ram_head_to_fitting",
            parent=parent,
            child=head,
            point=(0.0, 0.0, 0.0),
            axis=(0.0, 0.0, 1.0),
            provider_radial=(1.0, 0.0, 0.0),
            consumer_radial=(1.0, 0.0, 0.0),
            lower=-math.pi,
            upper=math.pi,
            effort=60.0,
            velocity=2.0,
        )
    else:
        model.articulation(
            "ram_head_to_fitting",
            ArticulationType.FIXED,
            parent=parent,
            child=head,
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
        )


# --- pump drive candidates --------------------------------------------------
def _pump_drive_lever_pump_build(part, frame, r: ResolvedConfig, mats: dict[str, str]) -> None:
    _y_cyl(part, "pump_drive__lever_pump__pivot_boss", 0.0085,
           2.0 * (CLEVIS_HALF - CLEVIS_EAR_T * 0.5 + MOUNT), (0.0, 0.0, 0.0), mats["chrome"])
    # The bar leaves the clevis up and outboard (+x), clear of the cylinder.
    length = r.handle_len
    ang = math.radians(38.0)
    cx = length * 0.5 * math.cos(ang)
    cz = length * 0.5 * math.sin(ang)
    part.visual(
        Box((length, 0.016, 0.013)),
        origin=Origin(xyz=(cx, 0.0, cz), rpy=(0.0, -ang, 0.0)),
        material=mats["paint"],
        name="pump_drive__lever_pump__bar", material_class_id="metal.paint_coated",
    )
    grip = length * 0.34
    gx = (length - grip * 0.5) * math.cos(ang)
    gz = (length - grip * 0.5) * math.sin(ang)
    part.visual(
        Box((grip, 0.026, 0.023)),
        origin=Origin(xyz=(gx, 0.0, gz), rpy=(0.0, -ang, 0.0)),
        material=mats["rubber"],
        name="pump_drive__lever_pump__grip", material_class_id="rubber.smooth_plain",
    )


def _pump_drive_air_over_hydraulic_build(part, frame, r: ResolvedConfig, mats: dict[str, str]) -> None:
    _y_cyl(part, "pump_drive__air_over_hydraulic__pivot_boss", 0.0085,
           2.0 * (CLEVIS_HALF - CLEVIS_EAR_T * 0.5 + MOUNT), (0.0, 0.0, 0.0), mats["chrome"])
    # Short trigger lever instead of a long hand bar.
    length = r.handle_len * 0.46
    ang = math.radians(30.0)
    cx = length * 0.5 * math.cos(ang)
    cz = length * 0.5 * math.sin(ang)
    part.visual(
        Box((length, 0.020, 0.015)),
        origin=Origin(xyz=(cx, 0.0, cz), rpy=(0.0, -ang, 0.0)),
        material=mats["dark"],
        name="pump_drive__air_over_hydraulic__trigger", material_class_id="metal.blackened_gunmetal",
    )
    part.visual(
        Box((length * 0.34, 0.028, 0.024)),
        origin=Origin(
            xyz=((length - length * 0.17) * math.cos(ang), 0.0, (length - length * 0.17) * math.sin(ang)),
            rpy=(0.0, -ang, 0.0),
        ),
        material=mats["rubber"],
        name="pump_drive__air_over_hydraulic__trigger_boot", material_class_id="rubber.smooth_plain",
    )
    # Host adaptation: the air motor can and its inlet mount on the pump body.
    can_r = r.pump_r * 0.86
    can_x = r.pump_x0 + r.pump_reach_m * 0.42
    can_z = r.pump_axis_z + r.pump_r + can_r - 0.004
    frame.visual(
        Cylinder(radius=can_r, length=r.pump_reach_m * 0.34),
        origin=Origin(xyz=(can_x, 0.0, can_z), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["dark"],
        name="pump_drive__air_over_hydraulic__air_motor_can", material_class_id="metal.blackened_gunmetal",
    )
    frame.visual(
        _tube("air_motor_band", can_r + 0.0018, can_r - 0.002, 0.0, 0.010, 24),
        origin=Origin(xyz=(can_x, 0.0, can_z), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["chrome"],
        name="pump_drive__air_over_hydraulic__air_motor_band", material_class_id="metal.chrome_polished",
    )
    frame.visual(
        Cylinder(radius=0.009, length=0.024),
        origin=Origin(
            xyz=(can_x - r.pump_reach_m * 0.20, 0.0, can_z),
            rpy=(0.0, math.pi / 2.0, 0.0),
        ),
        material=mats["chrome"],
        name="pump_drive__air_over_hydraulic__air_inlet", material_class_id="metal.chrome_polished",
    )


_PUMP_BUILDERS = {
    "lever_pump": _pump_drive_lever_pump_build,
    "air_over_hydraulic": _pump_drive_air_over_hydraulic_build,
}


def _build_pump_and_valve(model: ArticulatedObject, frame, r: ResolvedConfig, mats: dict[str, str]) -> None:
    handle = model.part(
        f"pump_drive__{r.pump_drive}__pump_handle",
        meta={"role": "pump_handle"},
    )
    _PUMP_BUILDERS[r.pump_drive](handle, frame, r, mats)
    _rev_axis_joint(
        model,
        name="frame_to_pump_handle",
        parent=frame,
        child=handle,
        point=(r.clevis_x, 0.0, r.clevis_z),
        axis=(0.0, 1.0, 0.0),
        provider_radial=(1.0, 0.0, 0.0),
        consumer_radial=(1.0, 0.0, 0.0),
        lower=-0.34,
        upper=0.34,
        effort=300.0,
        velocity=2.2,
    )

    valve = model.part("release_valve", meta={"role": "release_valve"})
    # Seat the valve joint on the pump-body skin, not clear of it: at
    # -(pump_r + 4 mm) the knob floated 4.6 mm off the frame and read as an
    # isolated part.  A 0.6 mm lap is real screwed-in contact.
    valve_y = -(r.pump_r - MOUNT)
    _y_cyl(valve, "valve_body", 0.012, 0.016, (0.0, -0.008 - MOUNT, 0.0), mats["dark"])
    _y_cyl(valve, "valve_cap", 0.006, 0.006, (0.0, -0.019 - MOUNT, 0.0), mats["chrome"])
    valve.visual(
        Box((0.020, 0.003, 0.0025)),
        origin=Origin(xyz=(0.0, -0.0225 - MOUNT, 0.0)),
        material=mats["steel"],
        name="valve_slot", material_class_id="metal.steel_bare",
    )
    _rev_axis_joint(
        model,
        name="frame_to_release_valve",
        parent=frame,
        child=valve,
        point=(r.pump_x1 - 0.044, valve_y, r.pump_axis_z),
        axis=(0.0, 1.0, 0.0),
        provider_radial=(0.0, 0.0, 1.0),
        consumer_radial=(0.0, 0.0, 1.0),
        lower=-0.80,
        upper=0.80,
        effort=4.0,
        velocity=4.0,
    )


# --- assembly ---------------------------------------------------------------
def build_picturex_0611_hydraulic_jack1(
    config: Config | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config or Config())
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={
            "category": "pictureX_0611_hydraulic_jack1",
            "slot_choices": slot_choices_for_config(r),
            "mechanism": "vertical telescopic hydraulic ram + lever hand pump",
        },
    )
    mats = _materials(model, r)
    frame = _build_frame(model, r, mats)
    _build_ram(model, frame, r, mats)
    _build_pump_and_valve(model, frame, r, mats)

    stage_joints = ["frame_to_ram_stage_0"] + [
        f"ram_stage_{i - 1}_to_ram_stage_{i}" for i in range(1, r.ram_stage_count)
    ]
    model.meta["risk_poses"] = (
        {name: 0.0 for name in stage_joints}
        | {"frame_to_pump_handle": 0.0, "frame_to_release_valve": 0.0},
        {name: r.stage_stroke[i] for i, name in enumerate(stage_joints)}
        | {"frame_to_pump_handle": 0.34, "frame_to_release_valve": 0.80},
        {name: r.stage_stroke[i] for i, name in enumerate(stage_joints)}
        | {"frame_to_pump_handle": -0.34, "frame_to_release_valve": -0.80},
    )
    model.meta["coupled_joint_pairs"] = tuple(
        (stage_joints[i], stage_joints[i + 1]) for i in range(len(stage_joints) - 1)
    ) + (("frame_to_ram_stage_0", "frame_to_pump_handle"),)
    return model


def build_seeded_picturex_0611_hydraulic_jack1(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_picturex_0611_hydraulic_jack1(config_from_seed(seed), assets=assets)


# --- authored tests ---------------------------------------------------------
def _parts_by_role(model: ArticulatedObject, role: str):
    return [p for p in model.parts if p.meta.get("role") == role]


def run_picturex_0611_hydraulic_jack1_tests(
    model: ArticulatedObject, config: Config
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)

    frames = _parts_by_role(model, "jack_frame")
    stages = _parts_by_role(model, "ram_stage")
    heads = _parts_by_role(model, "head_fitting")
    handles = _parts_by_role(model, "pump_handle")
    valves = _parts_by_role(model, "release_valve")

    joints = {j.name: j for j in model.articulations}
    stage_joints = [joints.get("frame_to_ram_stage_0")] + [
        joints.get(f"ram_stage_{i - 1}_to_ram_stage_{i}") for i in range(1, r.ram_stage_count)
    ]
    handle_joint = joints.get("frame_to_pump_handle")
    valve_joint = joints.get("frame_to_release_valve")

    def _is_pris_z(j) -> bool:
        return (
            j is not None
            and j.articulation_type == ArticulationType.PRISMATIC
            and tuple(round(v, 6) for v in j.axis) == (0.0, 0.0, 1.0)
            and j.motion_limits is not None
            and j.motion_limits.upper > j.motion_limits.lower
        )

    def _is_rev_y(j) -> bool:
        return (
            j is not None
            and j.articulation_type == ArticulationType.REVOLUTE
            and tuple(round(abs(v), 6) for v in j.axis) == (0.0, 1.0, 0.0)
            and j.motion_limits is not None
            and j.motion_limits.upper > j.motion_limits.lower
        )

    ctx.check(
        "category_anchor: vertical hydraulic ram jack mechanism",
        len(frames) == 1
        and len(heads) == 1
        and len(handles) == 1
        and len(valves) == 1
        and bool(model.root_parts())
        and model.root_parts()[0].name == "jack_frame"
        and all(_is_pris_z(j) for j in stage_joints)
        and stage_joints[0].parent == "jack_frame"
        and _is_rev_y(handle_joint)
        and handle_joint.parent == "jack_frame"
        and _is_rev_y(valve_joint)
        and valve_joint.parent == "jack_frame",
        details=(
            f"frames={len(frames)} heads={len(heads)} handles={len(handles)} "
            f"valves={len(valves)} stage_joints={[j.name if j else None for j in stage_joints]}"
        ),
    )

    # Every stage must keep real guide-land engagement inside its host bore at
    # full stroke: length - stroke is the engaged land depth.
    engagement = [
        r.stage_len[i] - r.stage_stroke[i] for i in range(r.ram_stage_count)
    ]
    nested = all(
        r.stage_outer_r[i] + CLEAR <= r.stage_outer_r[i - 1] - STAGE_WALL + 1e-9
        for i in range(1, r.ram_stage_count)
    )
    ctx.check(
        "category_anchor: telescopic ram stages stay journalled",
        len(stages) == r.ram_stage_count
        # The land still inside the host bore at full stroke must be a real
        # fraction of that stage's own length, for every stage size.
        and all(e > 0.25 * r.stage_len[i] for i, e in enumerate(engagement))
        and nested
        and all(
            stage_joints[i].parent
            == ("jack_frame" if i == 0 else stages[i - 1].name)
            for i in range(r.ram_stage_count)
        ),
        details=f"stages={len(stages)} engagement={engagement} nested={nested}",
    )

    visual_names = {v.name or "" for p in model.parts for v in p.visuals}
    stage_ok = {
        "chrome_rod": any("chrome_rod__land" in n for n in visual_names),
        "stepped_ram": any("stepped_ram__shoulder" in n for n in visual_names),
    }[r.ram_stage]
    ctx.check("category_anchor: ram_stage identity", stage_ok, details=f"ram_stage={r.ram_stage}")

    head_ok = {
        "flat_saddle": any("flat_saddle__knurl" in n for n in visual_names),
        "screw_extension": any("screw_extension__thread" in n for n in visual_names),
        "grooved_cradle": any("grooved_cradle__cheek" in n for n in visual_names),
    }[r.head_fitting]
    ctx.check(
        "category_anchor: head_fitting identity", head_ok, details=f"head_fitting={r.head_fitting}"
    )

    pump_ok = {
        "lever_pump": any("lever_pump__grip" in n for n in visual_names),
        "air_over_hydraulic": any("air_over_hydraulic__air_motor_can" in n for n in visual_names),
    }[r.pump_drive]
    ctx.check("category_anchor: pump_drive identity", pump_ok, details=f"pump_drive={r.pump_drive}")

    base_ok = {
        "flat_pad": any("flat_pad__rim" in n for n in visual_names),
        "flanged_bolt": any("flanged_bolt__boss" in n for n in visual_names),
        "channel_skid": any("channel_skid__skid" in n for n in visual_names),
    }[r.base_mount]
    ctx.check("category_anchor: base_mount identity", base_ok, details=f"base_mount={r.base_mount}")

    # Motion evidence: the ram lifts the head fitting by the full summed stroke.
    head_part = heads[0]
    rest = ctx.part_world_aabb(head_part)
    pose = {j: j.motion_limits.upper for j in stage_joints}
    with ctx.pose(pose):
        lifted = ctx.part_world_aabb(head_part)
    total = sum(r.stage_stroke)
    ctx.check(
        "ram extension lifts the head fitting by the summed stroke",
        rest is not None
        and lifted is not None
        and abs((lifted[0][2] - rest[0][2]) - total) < 1e-3,
        details=f"rest={rest} lifted={lifted} total_stroke={total}",
    )

    # Motion evidence: the pump lever really swings, and stays clear of the body.
    rest_h = ctx.part_world_aabb(handles[0])
    with ctx.pose({handle_joint: handle_joint.motion_limits.upper}):
        up_h = ctx.part_world_aabb(handles[0])
    with ctx.pose({handle_joint: handle_joint.motion_limits.lower}):
        down_h = ctx.part_world_aabb(handles[0])
    # A positive rotation about +y swings a +x arm downward, so the two limits
    # are checked by separation rather than by which one is named "upper".
    ctx.check(
        "pump handle swings through a real arc outboard of the cylinder",
        all(b is not None for b in (rest_h, up_h, down_h))
        and abs(up_h[1][2] - down_h[1][2]) > 0.02
        and min(up_h[0][0], down_h[0][0], rest_h[0][0]) > r.bore_radius_m
        and min(up_h[0][2], down_h[0][2], rest_h[0][2]) > 0.0,
        details=f"rest={rest_h} up={up_h} down={down_h}",
    )

    ctx.check(
        "domain choices recorded on the model",
        model.meta.get("slot_choices") == slot_choices_for_config(r),
    )
    return ctx.report()


TEMPLATE_CORNERS = (
    corner_case(
        "min_body_single_stage_flat",
        {
            "ram_stage": "chrome_rod",
            "head_fitting": "flat_saddle",
            "pump_drive": "lever_pump",
            "base_mount": "flat_pad",
            "ram_stage_count": 1,
            "body_height_m": 0.150,
            "bore_radius_m": 0.036,
            "pump_reach_m": 0.150,
        },
        reason="smallest bore and body with a single stage — tightest nesting and shortest pump",
    ),
    corner_case(
        "max_body_triple_stage_screw",
        {
            "ram_stage": "stepped_ram",
            "head_fitting": "screw_extension",
            "pump_drive": "air_over_hydraulic",
            "base_mount": "channel_skid",
            "ram_stage_count": 3,
            "body_height_m": 0.240,
            "bore_radius_m": 0.056,
            "pump_reach_m": 0.230,
        },
        reason="maximum envelope, three nested stages plus the screw extension — tallest reach",
    ),
    corner_case(
        "min_bore_triple_stage_cradle",
        {
            "ram_stage": "stepped_ram",
            "head_fitting": "grooved_cradle",
            "pump_drive": "lever_pump",
            "base_mount": "flanged_bolt",
            "ram_stage_count": 3,
            "body_height_m": 0.240,
            "bore_radius_m": 0.036,
            "pump_reach_m": 0.150,
        },
        reason="smallest bore with the most stages — the thinnest admissible innermost rod",
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
    "build_picturex_0611_hydraulic_jack1",
    "build_seeded_picturex_0611_hydraulic_jack1",
    "run_picturex_0611_hydraulic_jack1_tests",
]
