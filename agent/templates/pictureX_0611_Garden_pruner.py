# SPDX-License-Identifier: Apache-2.0

"""Self-contained one-handed garden pruner.

A small rigid ``pivot_frame`` root carries the main pivot boss, its bolt head
and captive nut.  The ``cutting_half`` and the ``counter_half`` are both
REVOLUTE children of that frame on the same main axis and open symmetrically;
q=0 is fully closed.

``head_build`` changes the jaw pair, ``handle_build`` how both handles are built
behind the pivot, ``return_build`` the spring that reopens them (stacked
``spring_stage_count`` times) and ``catch_build`` the locking hardware on the
counter handle.  Every catch mounts at the same station and stays inside the
handle envelope at every pose, so all combinations build.

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
    Sphere,
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

HeadBuild = Literal["bypass_blade", "hooked_beak", "long_bypass", "anvil_insert"]
ReturnBuild = Literal["coil_seat", "torsion_coil", "leaf_spring"]
CatchBuild = Literal["swing_latch", "thumb_slider", "ratchet_pawl", "stop_screw", "rotating_sleeve"]
HandleBuild = Literal["sculpted_grip", "plate_frame"]
PaletteStyle = Literal["red_steel", "orange_grip", "green_grip", "graphite"]

HEAD_BUILDS: tuple[HeadBuild, ...] = ("bypass_blade", "hooked_beak", "long_bypass", "anvil_insert")
RETURN_BUILDS: tuple[ReturnBuild, ...] = ("coil_seat", "torsion_coil", "leaf_spring")
CATCH_BUILDS: tuple[CatchBuild, ...] = (
    "swing_latch",
    "thumb_slider",
    "ratchet_pawl",
    "stop_screw",
    "rotating_sleeve",
)
HANDLE_BUILDS: tuple[HandleBuild, ...] = ("sculpted_grip", "plate_frame")
PALETTE_STYLES: tuple[PaletteStyle, ...] = ("red_steel", "orange_grip", "green_grip", "graphite")

TEMPLATE_DOMAIN = TemplateDomain(
    slots=(
        component_slot("head_build", HEAD_BUILDS),
        component_slot("return_build", RETURN_BUILDS),
        component_slot("catch_build", CATCH_BUILDS),
        component_slot("handle_build", HANDLE_BUILDS),
        multiplicity_slot("spring_stage_count", (1, 2), item_slot="return_build"),
    )
)

PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "red_steel": {
        "steel": (0.62, 0.64, 0.66, 1.0),
        "blade": (0.80, 0.82, 0.84, 1.0),
        "body": (0.72, 0.12, 0.10, 1.0),
        "grip": (0.14, 0.14, 0.15, 1.0),
        "accent": (0.86, 0.72, 0.24, 1.0),
    },
    "orange_grip": {
        "steel": (0.58, 0.60, 0.62, 1.0),
        "blade": (0.78, 0.80, 0.83, 1.0),
        "body": (0.86, 0.44, 0.10, 1.0),
        "grip": (0.18, 0.18, 0.19, 1.0),
        "accent": (0.30, 0.30, 0.32, 1.0),
    },
    "green_grip": {
        "steel": (0.60, 0.62, 0.64, 1.0),
        "blade": (0.79, 0.81, 0.83, 1.0),
        "body": (0.16, 0.42, 0.24, 1.0),
        "grip": (0.86, 0.86, 0.84, 1.0),
        "accent": (0.72, 0.60, 0.20, 1.0),
    },
    "graphite": {
        "steel": (0.44, 0.45, 0.47, 1.0),
        "blade": (0.68, 0.70, 0.72, 1.0),
        "body": (0.22, 0.22, 0.24, 1.0),
        "grip": (0.40, 0.41, 0.43, 1.0),
        "accent": (0.66, 0.68, 0.70, 1.0),
    },
}

PIVOT_R = 0.011          # main pivot boss radius
JAW_T = 0.0035           # jaw plate thickness
HALF_GAP = 0.0009        # running gap between the two halves at the pivot
GRIP_T = 0.016           # handle grip thickness
MOUNT = 0.0004           # intra-part embedment so one part stays one island
CATCH_STATION = 0.42     # catch station along the counter handle
HANDLE_Z = GRIP_T * 0.5 + 0.0016  # each handle steps off the blade plane
MOUNT_Z = -(HANDLE_Z + GRIP_T * 0.5 + 0.0045)  # outer face the catch and spring sit on


@dataclass(frozen=True)
class Config:
    head_build: HeadBuild = "bypass_blade"
    return_build: ReturnBuild = "coil_seat"
    catch_build: CatchBuild = "swing_latch"
    handle_build: HandleBuild = "sculpted_grip"
    spring_stage_count: int = 1
    tool_length_m: float | None = None
    jaw_ratio: float | None = None
    open_angle_rad: float | None = None
    palette_style: PaletteStyle = "red_steel"
    name: str = "pictureX_0611_Garden_pruner"


@dataclass(frozen=True)
class ResolvedConfig:
    head_build: HeadBuild
    return_build: ReturnBuild
    catch_build: CatchBuild
    handle_build: HandleBuild
    spring_stage_count: int
    palette_style: PaletteStyle
    palette: dict[str, tuple[float, float, float, float]]
    tool_length_m: float
    jaw_ratio: float
    open_angle_rad: float
    handle_length_m: float
    jaw_length_m: float
    spring_station_m: float
    spring_travel_m: float
    catch_station_m: float
    half_offset_m: float
    name: str


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(value)))


def config_from_seed(seed: int) -> Config:
    rng = random.Random(int(seed) ^ 0x0F76_4416)
    choices = TEMPLATE_DOMAIN.sample(rng)
    return Config(
        head_build=choices["head_build"],
        return_build=choices["return_build"],
        catch_build=choices["catch_build"],
        handle_build=choices["handle_build"],
        spring_stage_count=choices["spring_stage_count"],
        tool_length_m=round(rng.uniform(0.180, 0.260), 4),
        jaw_ratio=round(rng.uniform(0.24, 0.38), 4),
        open_angle_rad=round(rng.uniform(0.42, 0.72), 4),
        palette_style=rng.choice(PALETTE_STYLES),
        name=f"garden_pruner_seed_{int(seed)}",
    )


def resolve_config(config: Config) -> ResolvedConfig:
    TEMPLATE_DOMAIN.validate(
        {
            "head_build": config.head_build,
            "return_build": config.return_build,
            "catch_build": config.catch_build,
            "handle_build": config.handle_build,
            "spring_stage_count": config.spring_stage_count,
        }
    )
    if config.palette_style not in PALETTES:
        raise ValueError(f"unsupported palette_style: {config.palette_style}")
    if config.tool_length_m is not None and not 0.180 <= float(config.tool_length_m) <= 0.260:
        raise ValueError("tool_length_m must be in [0.180, 0.260]")
    if config.jaw_ratio is not None and not 0.24 <= float(config.jaw_ratio) <= 0.38:
        raise ValueError("jaw_ratio must be in [0.24, 0.38]")
    if config.open_angle_rad is not None and not 0.42 <= float(config.open_angle_rad) <= 0.72:
        raise ValueError("open_angle_rad must be in [0.42, 0.72]")

    length = (
        _clamp(config.tool_length_m, 0.180, 0.260) if config.tool_length_m is not None else 0.215
    )
    ratio = _clamp(config.jaw_ratio, 0.24, 0.38) if config.jaw_ratio is not None else 0.30
    open_angle = (
        _clamp(config.open_angle_rad, 0.42, 0.72)
        if config.open_angle_rad is not None
        else 0.55
    )

    handle_len = length * (1.0 - ratio)
    jaw_len = length * ratio
    spring_station = handle_len * 0.30
    spring_travel = 2.0 * spring_station * math.sin(open_angle)
    catch_station = handle_len * CATCH_STATION
    half_offset = JAW_T * 0.5 + HALF_GAP

    return ResolvedConfig(
        head_build=config.head_build,
        return_build=config.return_build,
        catch_build=config.catch_build,
        handle_build=config.handle_build,
        spring_stage_count=int(config.spring_stage_count),
        palette_style=config.palette_style,
        palette=dict(PALETTES[config.palette_style]),
        tool_length_m=length,
        jaw_ratio=ratio,
        open_angle_rad=open_angle,
        handle_length_m=handle_len,
        jaw_length_m=jaw_len,
        spring_station_m=spring_station,
        spring_travel_m=spring_travel,
        catch_station_m=catch_station,
        half_offset_m=half_offset,
        name=config.name,
    )


def slot_choices_for_config(config: Config | ResolvedConfig) -> tuple[tuple[str, object], ...]:
    return (
        ("head_build", config.head_build),
        ("return_build", config.return_build),
        ("catch_build", config.catch_build),
        ("handle_build", config.handle_build),
        ("spring_stage_count", config.spring_stage_count),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, object], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# --- helpers ----------------------------------------------------------------
def _materials(model: ArticulatedObject, r: ResolvedConfig) -> dict[str, str]:
    mats: dict[str, str] = {}
    for key, rgba in r.palette.items():
        model.material(f"gp_{r.palette_style}_{key}", rgba=rgba)
        mats[key] = f"gp_{r.palette_style}_{key}"
    return mats


def _bar(part, p0, p1, width: float, thick: float, material: str, name: str) -> None:
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    length = math.hypot(dx, dy)
    yaw = math.atan2(dy, dx)
    part.visual(
        Box((length, width, thick)),
        origin=Origin(
            xyz=((p0[0] + p1[0]) * 0.5, (p0[1] + p1[1]) * 0.5, 0.0), rpy=(0.0, 0.0, yaw)
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


# --- pivot frame ------------------------------------------------------------
def _build_frame(model: ArticulatedObject, r: ResolvedConfig, mats: dict[str, str]):
    frame = model.part("pivot_frame", meta={"role": "pivot_frame"})
    span = 2.0 * (r.half_offset_m + JAW_T) + 0.004
    frame.visual(
        Cylinder(radius=0.0042, length=span),
        origin=Origin(),
        material=mats["steel"],
        name="pivot_bolt", material_class_id=("metal.steel_bare" if r.palette_style in {"red_steel", "orange_grip", "green_grip"} else "metal.blackened_gunmetal"),
    )
    frame.visual(
        Cylinder(radius=0.0095, length=0.0045),
        origin=Origin(xyz=(0.0, 0.0, span * 0.5 - 0.001)),
        material=mats["steel"],
        name="pivot_bolt_head", material_class_id=("metal.steel_bare" if r.palette_style in {"red_steel", "orange_grip", "green_grip"} else "metal.blackened_gunmetal"),
    )
    frame.visual(
        mesh_from_geometry(
            ExtrudeGeometry(
                [
                    (0.0095 * math.cos(a), 0.0095 * math.sin(a))
                    for a in (2.0 * math.pi * i / 6.0 for i in range(6))
                ],
                0.0050,
                center=True,
            ),
            "pivot_nut_mesh",
        ),
        origin=Origin(xyz=(0.0, 0.0, -(span * 0.5 - 0.001))),
        material=mats["steel"],
        name="pivot_nut", material_class_id=("metal.steel_bare" if r.palette_style in {"red_steel", "orange_grip", "green_grip"} else "metal.blackened_gunmetal"),
    )
    return frame


# --- handle candidates ------------------------------------------------------
def _handle_build_sculpted_grip_build(half, r, mats, side: float, tag: str) -> None:
    hz = side * HANDLE_Z
    """Bezier-ish sculpted handle: a swelling palm belly on a curved core."""
    L = r.handle_length_m
    profile = [
        (-0.004, 0.013 * side),
        (-L * 0.30, 0.019 * side),
        (-L * 0.62, 0.021 * side),
        (-L * 0.92, 0.014 * side),
        (-L, 0.006 * side),
        (-L, -0.004 * side),
        (-L * 0.60, -0.006 * side),
        (-0.004, -0.009 * side),
    ]
    half.visual(
        mesh_from_geometry(
            ExtrudeGeometry(profile, GRIP_T, center=True), f"sculpted_handle_mesh_{tag}"
        ),
        origin=Origin(xyz=(0.0, 0.0, hz)),
        material=mats["body"],
        name=f"handle_build__sculpted_grip__handle_core_{tag}", material_class_id="metal.paint_coated",
    )
    half.visual(
        Box((0.030, 0.020, abs(hz) + GRIP_T * 0.5)),
        origin=Origin(xyz=(-0.012, 0.004 * side, hz * 0.5)),
        material=mats["body"],
        name=f"handle_build__sculpted_grip__handle_web_{tag}", material_class_id="metal.paint_coated",
    )
    for i in range(4):
        x = -L * (0.34 + 0.16 * i)
        half.visual(
            Box((0.006, 0.026, GRIP_T + 0.0016)),
            origin=Origin(xyz=(x, 0.006 * side, hz)),
            material=mats["grip"],
            name=f"handle_build__sculpted_grip__grip_rib_{tag}_{i}", material_class_id="rubber.directional_grooved",
        )


def _handle_build_plate_frame_build(half, r, mats, side: float, tag: str) -> None:
    hz = side * HANDLE_Z
    """Plate-built core with a separate moulded grip shell wrapped over it."""
    L = r.handle_length_m
    half.visual(
        Box((0.030, 0.020, abs(hz) + 0.0055)),
        origin=Origin(xyz=(-0.012, 0.004 * side, hz * 0.5)),
        material=mats["steel"],
        name=f"handle_build__plate_frame__handle_web_{tag}", material_class_id=("metal.steel_bare" if r.palette_style in {"red_steel", "orange_grip", "green_grip"} else "metal.blackened_gunmetal"),
    )
    half.visual(
        Box((L - 0.004, 0.020, 0.0055)),
        origin=Origin(xyz=(-(L + 0.004) * 0.5, 0.004 * side, hz)),
        material=mats["steel"],
        name=f"handle_build__plate_frame__handle_plate_{tag}", material_class_id=("metal.steel_bare" if r.palette_style in {"red_steel", "orange_grip", "green_grip"} else "metal.blackened_gunmetal"),
    )
    half.visual(
        Box((L * 0.66, 0.030, GRIP_T)),
        origin=Origin(xyz=(-L * 0.60, 0.004 * side, hz)),
        material=mats["body"],
        name=f"handle_build__plate_frame__grip_shell_{tag}", material_class_id="plastic.opaque_glossy_molded",
    )
    half.visual(
        Box((L * 0.66 - 0.010, 0.010, GRIP_T + 0.0018)),
        origin=Origin(xyz=(-L * 0.60, 0.014 * side, hz)),
        material=mats["grip"],
        name=f"handle_build__plate_frame__grip_pad_{tag}", material_class_id="rubber.smooth_plain",
    )
    half.visual(
        Box((0.014, 0.030, GRIP_T + 0.002)),
        origin=Origin(xyz=(-L * 0.94, 0.004 * side, hz)),
        material=mats["grip"],
        name=f"handle_build__plate_frame__butt_cap_{tag}", material_class_id="rubber.smooth_plain",
    )


_HANDLE_BUILDERS = {
    "sculpted_grip": _handle_build_sculpted_grip_build,
    "plate_frame": _handle_build_plate_frame_build,
}


# --- head candidates --------------------------------------------------------
def _tang(half, r, mats, tag: str) -> None:
    """Fixed tang section every jaw and handle meets at."""
    half.visual(
        Cylinder(radius=PIVOT_R, length=JAW_T),
        origin=Origin(),
        material=mats["steel"],
        name=f"tang_boss_{tag}", material_class_id=("metal.steel_bare" if r.palette_style in {"red_steel", "orange_grip", "green_grip"} else "metal.blackened_gunmetal"),
    )


def _head_build_bypass_blade_build(model, r, mats, cutting, counter):
    J = r.jaw_length_m
    cutting.visual(
        mesh_from_geometry(
            ExtrudeGeometry(
                [(0.006, 0.010), (J * 0.55, 0.014), (J, 0.002), (J * 0.5, -0.007), (0.006, -0.008)],
                JAW_T,
                center=True,
            ),
            "bypass_blade_mesh",
        ),
        material=mats["blade"],
        name="head_build__bypass_blade__blade", material_class_id="metal.stainless_matte",
    )
    _bar(cutting, (0.010, -0.006), (J * 0.92, -0.001), 0.004, JAW_T + 0.0012,
         mats["accent"], "head_build__bypass_blade__cutting_edge")
    counter.visual(
        mesh_from_geometry(
            ExtrudeGeometry(
                [(0.006, -0.010), (J * 0.52, -0.014), (J * 0.90, -0.002), (0.006, 0.007)],
                JAW_T,
                center=True,
            ),
            "bypass_counter_mesh",
        ),
        material=mats["steel"],
        name="head_build__bypass_blade__counter_jaw", material_class_id=("metal.steel_bare" if r.palette_style in {"red_steel", "orange_grip", "green_grip"} else "metal.blackened_gunmetal"),
    )


def _head_build_hooked_beak_build(model, r, mats, cutting, counter):
    J = r.jaw_length_m
    cutting.visual(
        mesh_from_geometry(
            ExtrudeGeometry(
                [(0.006, 0.009), (J * 0.60, 0.013), (J, 0.000), (J * 0.45, -0.008), (0.006, -0.008)],
                JAW_T,
                center=True,
            ),
            "beak_blade_mesh",
        ),
        material=mats["blade"],
        name="head_build__hooked_beak__blade", material_class_id="metal.stainless_matte",
    )
    counter.visual(
        mesh_from_geometry(
            ExtrudeGeometry(
                [
                    (0.006, -0.010),
                    (J * 0.55, -0.017),
                    (J * 0.95, -0.010),
                    (J * 0.80, 0.004),
                    (J * 0.45, -0.003),
                    (0.006, 0.006),
                ],
                JAW_T,
                center=True,
            ),
            "beak_hook_mesh",
        ),
        material=mats["steel"],
        name="head_build__hooked_beak__hook_jaw", material_class_id=("metal.steel_bare" if r.palette_style in {"red_steel", "orange_grip", "green_grip"} else "metal.blackened_gunmetal"),
    )
    _bar(counter, (J * 0.70, -0.012), (J * 0.92, -0.006), 0.005, JAW_T + 0.0012,
         mats["accent"], "head_build__hooked_beak__hook_tip")


def _head_build_long_bypass_build(model, r, mats, cutting, counter):
    J = r.jaw_length_m * 1.25
    cutting.visual(
        mesh_from_geometry(
            ExtrudeGeometry(
                [(0.006, 0.008), (J * 0.60, 0.010), (J, 0.001), (J * 0.5, -0.005), (0.006, -0.007)],
                JAW_T * 0.85,
                center=True,
            ),
            "long_blade_mesh",
        ),
        material=mats["blade"],
        name="head_build__long_bypass__blade", material_class_id="metal.stainless_matte",
    )
    _bar(cutting, (0.010, -0.004), (J * 0.96, 0.000), 0.0035, JAW_T + 0.0012,
         mats["accent"], "head_build__long_bypass__cutting_edge")
    counter.visual(
        mesh_from_geometry(
            ExtrudeGeometry(
                [(0.006, -0.009), (J * 0.50, -0.011), (J * 0.86, -0.002), (0.006, 0.006)],
                JAW_T,
                center=True,
            ),
            "long_counter_mesh",
        ),
        material=mats["steel"],
        name="head_build__long_bypass__counter_jaw", material_class_id=("metal.steel_bare" if r.palette_style in {"red_steel", "orange_grip", "green_grip"} else "metal.blackened_gunmetal"),
    )


def _head_build_anvil_insert_build(model, r, mats, cutting, counter):
    J = r.jaw_length_m
    cutting.visual(
        mesh_from_geometry(
            ExtrudeGeometry(
                [(0.006, 0.010), (J * 0.55, 0.013), (J * 0.94, 0.002), (0.006, -0.008)],
                JAW_T,
                center=True,
            ),
            "anvil_blade_mesh",
        ),
        material=mats["blade"],
        name="head_build__anvil_insert__blade", material_class_id="metal.stainless_matte",
    )
    counter.visual(
        mesh_from_geometry(
            ExtrudeGeometry(
                [(0.006, -0.011), (J * 0.60, -0.015), (J * 0.92, -0.004), (0.006, 0.006)],
                JAW_T,
                center=True,
            ),
            "anvil_jaw_mesh",
        ),
        material=mats["steel"],
        name="head_build__anvil_insert__counter_jaw", material_class_id=("metal.steel_bare" if r.palette_style in {"red_steel", "orange_grip", "green_grip"} else "metal.blackened_gunmetal"),
    )
    # The replaceable insert sits in a seat cut into the counter jaw.
    counter.visual(
        Box((J * 0.34, 0.007, JAW_T + 0.0022)),
        origin=Origin(xyz=(J * 0.60, -0.006, 0.0)),
        material=mats["accent"],
        name="head_build__anvil_insert__anvil_insert", material_class_id=("metal.brass_polished" if r.palette_style in {"red_steel", "green_grip", "graphite"} else "metal.blackened_gunmetal"),
    )
    counter.visual(
        Cylinder(radius=0.0022, length=JAW_T + 0.0026),
        origin=Origin(xyz=(J * 0.60, -0.006, 0.0)),
        material=mats["steel"],
        name="head_build__anvil_insert__insert_screw", material_class_id=("metal.steel_bare" if r.palette_style in {"red_steel", "orange_grip", "green_grip"} else "metal.blackened_gunmetal"),
    )


_HEAD_BUILDERS = {
    "bypass_blade": _head_build_bypass_blade_build,
    "hooked_beak": _head_build_hooked_beak_build,
    "long_bypass": _head_build_long_bypass_build,
    "anvil_insert": _head_build_anvil_insert_build,
}


# --- return spring candidates -----------------------------------------------
# Every return spring is a child of the COUNTER half at the spring station, and
# is mimicked to the cutting half so it follows the handles instead of being
# posed into them.
def _build_return(model: ArticulatedObject, r: ResolvedConfig, mats, counter) -> list:
    stages = []
    kind = r.return_build
    for stage in range(r.spring_stage_count):
        spring = model.part(
            f"return_build__{kind}__return_spring_{stage}",
            meta={"role": "return_spring", "index": stage},
        )
        pitch = 0.011
        if kind == "coil_seat":
            spring.visual(
                Cylinder(radius=0.0040, length=0.020),
                origin=Origin(xyz=(0.0, 0.010, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
                material=mats["steel"],
                name=f"return_build__coil_seat__coil_body_{stage}", material_class_id=("metal.steel_bare" if r.palette_style in {"red_steel", "orange_grip", "green_grip"} else "metal.blackened_gunmetal"),
            )
            spring.visual(
                Box((0.012, 0.005, 0.008)),
                origin=Origin(xyz=(0.0, 0.0005, 0.0)),
                material=mats["accent"],
                name=f"return_build__coil_seat__seat_cup_{stage}", material_class_id="metal.paint_coated",
            )
            spring.visual(
                Box((0.012, 0.005, 0.008)),
                origin=Origin(xyz=(0.0, 0.0195, 0.0)),
                material=mats["accent"],
                name=f"return_build__coil_seat__seat_head_{stage}", material_class_id="metal.paint_coated",
            )
        elif kind == "torsion_coil":
            spring.visual(
                Cylinder(radius=0.0075, length=0.008),
                origin=Origin(xyz=(0.0, 0.010, 0.0)),
                material=mats["steel"],
                name=f"return_build__torsion_coil__coil_ring_{stage}", material_class_id=("metal.steel_bare" if r.palette_style in {"red_steel", "orange_grip", "green_grip"} else "metal.blackened_gunmetal"),
            )
            _bar(spring, (0.0, 0.008), (0.026, 0.014), 0.0026, 0.008,
                 mats["steel"], f"return_build__torsion_coil__leg_a_{stage}")
            _bar(spring, (0.0, 0.008), (0.024, -0.004), 0.0026, 0.008,
                 mats["steel"], f"return_build__torsion_coil__leg_b_{stage}")
            spring.visual(
                Cylinder(radius=0.0030, length=0.008),
                origin=Origin(xyz=(0.0, 0.010, 0.0)),
                material=mats["steel"],
                name=f"return_build__torsion_coil__coil_core_{stage}", material_class_id=("metal.steel_bare" if r.palette_style in {"red_steel", "orange_grip", "green_grip"} else "metal.blackened_gunmetal"),
            )
        else:  # leaf_spring
            # A bowed leaf built from overlapping straight segments, so the
            # whole leaf stays one connected island.
            pts = [
                (0.014 * math.sin(math.pi * (i / 5.0)), 0.020 * (i / 5.0))
                for i in range(6)
            ]
            for i in range(5):
                _bar(
                    spring,
                    pts[i],
                    pts[i + 1],
                    0.010,
                    0.008,
                    mats["steel"],
                    f"return_build__leaf_spring__leaf_seg_{stage}_{i}",
                )
            spring.visual(
                Box((0.010, 0.005, 0.008)),
                origin=Origin(xyz=(0.0, 0.0008, 0.0)),
                material=mats["accent"],
                name=f"return_build__leaf_spring__leaf_root_{stage}", material_class_id="metal.paint_coated",
            )
        _axis_joint(
            model,
            name=f"counter_to_return_spring_{stage}",
            parent=counter,
            child=spring,
            point=(-r.spring_station_m - pitch * stage, 0.004, MOUNT_Z),
            axis=(0.0, 0.0, 1.0),
            radial=(1.0, 0.0, 0.0),
            child_axis=(0.0, 0.0, 1.0),
            child_radial=(1.0, 0.0, 0.0),
            lower=-1.0,
            upper=1.0,
            effort=2.0,
            velocity=3.0,
            mimic=Mimic(joint="frame_to_cutting_half", multiplier=-1.0, offset=0.0),
            meta={"positive_motion": "the spring follows the closing handles"},
        )
        stages.append(spring)
    return stages


# --- locking catch candidates ------------------------------------------------
def _build_catch(model: ArticulatedObject, r: ResolvedConfig, mats, counter):
    kind = r.catch_build
    catch = model.part(
        f"catch_build__{kind}__locking_catch", meta={"role": "locking_catch"}
    )
    station = -r.catch_station_m
    if kind == "swing_latch":
        _bar(catch, (0.0, 0.0), (0.026, 0.0), 0.005, 0.0055,
             mats["accent"], "catch_build__swing_latch__latch_arm")
        catch.visual(
            Box((0.006, 0.010, 0.0055)),
            origin=Origin(xyz=(0.026, 0.004, 0.0)),
            material=mats["accent"],
            name="catch_build__swing_latch__latch_hook", material_class_id="metal.paint_coated",
        )
        catch.visual(
            Cylinder(radius=0.0032, length=0.010),
            origin=Origin(),
            material=mats["steel"],
            name="catch_build__swing_latch__latch_boss", material_class_id=("metal.steel_bare" if r.palette_style in {"red_steel", "orange_grip", "green_grip"} else "metal.blackened_gunmetal"),
        )
        _axis_joint(
            model,
            name="counter_to_locking_catch",
            parent=counter,
            child=catch,
            point=(station, 0.010, MOUNT_Z),
            axis=(0.0, 0.0, 1.0),
            radial=(1.0, 0.0, 0.0),
            child_axis=(0.0, 0.0, 1.0),
            child_radial=(1.0, 0.0, 0.0),
            lower=0.0,
            upper=1.25,
            effort=3.0,
            velocity=2.0,
            meta={"positive_motion": "swings the latch hook clear of the other half"},
        )
    elif kind == "ratchet_pawl":
        _bar(catch, (0.0, 0.0), (0.022, 0.0), 0.005, 0.0050,
             mats["accent"], "catch_build__ratchet_pawl__pawl_arm")
        for i in range(3):
            catch.visual(
                Box((0.004, 0.004, 0.0050)),
                origin=Origin(xyz=(0.014 + 0.005 * i, 0.004, 0.0)),
                material=mats["steel"],
                name=f"catch_build__ratchet_pawl__pawl_tooth_{i}", material_class_id=("metal.steel_bare" if r.palette_style in {"red_steel", "orange_grip", "green_grip"} else "metal.blackened_gunmetal"),
            )
        catch.visual(
            Cylinder(radius=0.0032, length=0.010),
            origin=Origin(),
            material=mats["steel"],
            name="catch_build__ratchet_pawl__pawl_boss", material_class_id=("metal.steel_bare" if r.palette_style in {"red_steel", "orange_grip", "green_grip"} else "metal.blackened_gunmetal"),
        )
        _axis_joint(
            model,
            name="counter_to_locking_catch",
            parent=counter,
            child=catch,
            point=(station, 0.010, MOUNT_Z),
            axis=(0.0, 0.0, 1.0),
            radial=(1.0, 0.0, 0.0),
            child_axis=(0.0, 0.0, 1.0),
            child_radial=(1.0, 0.0, 0.0),
            lower=0.0,
            upper=0.75,
            effort=2.0,
            velocity=2.5,
            meta={"positive_motion": "lifts the pawl off its sector"},
        )
    elif kind == "rotating_sleeve":
        catch.visual(
            Cylinder(radius=0.013, length=0.026),
            origin=Origin(xyz=(-0.013, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["grip"],
            name="catch_build__rotating_sleeve__sleeve_body", material_class_id="rubber.smooth_plain",
        )
        for i in range(4):
            a = 2.0 * math.pi * i / 4.0
            catch.visual(
                Box((0.024, 0.004, 0.004)),
                origin=Origin(
                    xyz=(-0.013, 0.0125 * math.cos(a), 0.0125 * math.sin(a)),
                    rpy=(a, 0.0, 0.0),
                ),
                material=mats["accent"],
                name=f"catch_build__rotating_sleeve__sleeve_rib_{i}", material_class_id="plastic.opaque_glossy_molded",
            )
        catch.visual(
            Cylinder(radius=0.0055, length=0.010),
            origin=Origin(xyz=(0.0035, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["steel"],
            name="catch_build__rotating_sleeve__sleeve_stem", material_class_id=("metal.steel_bare" if r.palette_style in {"red_steel", "orange_grip", "green_grip"} else "metal.blackened_gunmetal"),
        )
        _axis_joint(
            model,
            name="counter_to_locking_catch",
            parent=counter,
            child=catch,
            point=(-r.handle_length_m - 0.0005, 0.004, -HANDLE_Z),
            axis=(1.0, 0.0, 0.0),
            radial=(0.0, 0.0, 1.0),
            child_axis=(1.0, 0.0, 0.0),
            child_radial=(0.0, 0.0, 1.0),
            lower=-math.pi,
            upper=math.pi,
            effort=1.5,
            velocity=4.0,
            meta={"positive_motion": "turns the grip knob on the handle axis"},
        )
    else:
        # thumb_slider and stop_screw are both prismatic hardware in the handle.
        travel = 0.012 if kind == "thumb_slider" else 0.009
        catch.visual(
            Box((0.020, 0.008, 0.007)),
            origin=Origin(xyz=(0.010, 0.0, 0.0)),
            material=mats["accent"],
            name=f"catch_build__{kind}__slider_body", material_class_id="plastic.opaque_glossy_molded",
        )
        catch.visual(
            Box((0.007, 0.012, 0.008)),
            origin=Origin(xyz=(0.019, 0.0, 0.0)),
            material=mats["steel"],
            name=f"catch_build__{kind}__slider_head", material_class_id=("metal.steel_bare" if r.palette_style in {"red_steel", "orange_grip", "green_grip"} else "metal.blackened_gunmetal"),
        )
        if kind == "thumb_slider":
            catch.visual(
                Box((0.006, 0.006, 0.008)),
                origin=Origin(xyz=(0.004, 0.0, -0.006)),
                material=mats["grip"],
                name="catch_build__thumb_slider__thumb_pad", material_class_id="rubber.smooth_plain",
            )
        else:
            catch.visual(
                Cylinder(radius=0.0034, length=0.010),
                origin=Origin(xyz=(0.004, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
                material=mats["steel"],
                name="catch_build__stop_screw__screw_shank", material_class_id=("metal.steel_bare" if r.palette_style in {"red_steel", "orange_grip", "green_grip"} else "metal.blackened_gunmetal"),
            )
        # Guide channel let into the counter handle.
        for cheek, sz in enumerate((-1.0, 1.0)):
            counter.visual(
                Box((0.034, 0.010, 0.005)),
                origin=Origin(xyz=(station + 0.014, 0.0, MOUNT_Z + sz * 0.0063)),
                material=mats["steel"],
                name=f"catch_guide_cheek_{cheek}", material_class_id=("metal.steel_bare" if r.palette_style in {"red_steel", "orange_grip", "green_grip"} else "metal.blackened_gunmetal"),
            )
        counter.visual(
            Box((0.034, 0.005, 0.018)),
            origin=Origin(xyz=(station + 0.014, -0.0063, MOUNT_Z)),
            material=mats["steel"],
            name="catch_guide_back", material_class_id=("metal.steel_bare" if r.palette_style in {"red_steel", "orange_grip", "green_grip"} else "metal.blackened_gunmetal"),
        )
        model.articulation(
            "counter_to_locking_catch",
            ArticulationType.PRISMATIC,
            parent=counter,
            child=catch,
            origin=Origin(xyz=(station, 0.0, MOUNT_Z)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(lower=0.0, upper=travel, effort=6.0, velocity=0.4),
            meta={"positive_motion": f"drives the {kind} forward in its channel"},
        )
    return catch


# --- assembly ---------------------------------------------------------------
def build_picturex_0611_garden_pruner(
    config: Config | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config or Config())
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={
            "category": "pictureX_0611_Garden_pruner",
            "slot_choices": slot_choices_for_config(r),
            "mechanism": "single-pivot scissor pair with a return spring and a catch",
        },
    )
    mats = _materials(model, r)
    frame = _build_frame(model, r, mats)

    cutting = model.part(
        f"head_build__{r.head_build}__cutting_half", meta={"role": "cutting_half"}
    )
    counter = model.part(
        f"head_build__{r.head_build}__counter_half", meta={"role": "counter_half"}
    )
    _tang(cutting, r, mats, "cut")
    _tang(counter, r, mats, "cnt")
    _HEAD_BUILDERS[r.head_build](model, r, mats, cutting, counter)
    _HANDLE_BUILDERS[r.handle_build](cutting, r, mats, 1.0, "cut")
    _HANDLE_BUILDERS[r.handle_build](counter, r, mats, -1.0, "cnt")

    for name, child, side, sense in (
        ("frame_to_cutting_half", cutting, 1.0, 1.0),
        ("frame_to_counter_half", counter, -1.0, -1.0),
    ):
        _axis_joint(
            model,
            name=name,
            parent=frame,
            child=child,
            point=(0.0, 0.0, side * r.half_offset_m),
            axis=(0.0, 0.0, 1.0),
            radial=(1.0, 0.0, 0.0),
            child_axis=(0.0, 0.0, 1.0),
            child_radial=(1.0, 0.0, 0.0),
            lower=0.0 if sense > 0 else -r.open_angle_rad,
            upper=r.open_angle_rad if sense > 0 else 0.0,
            effort=25.0,
            velocity=2.0,
            meta={"positive_motion": f"opens the {name.split('_to_')[1]} about the main pivot"},
        )

    _build_return(model, r, mats, counter)
    _build_catch(model, r, mats, counter)

    model.meta["risk_poses"] = (
        {"frame_to_cutting_half": 0.0, "frame_to_counter_half": 0.0},
        {
            "frame_to_cutting_half": r.open_angle_rad,
            "frame_to_counter_half": -r.open_angle_rad,
        },
    )
    model.meta["coupled_joint_pairs"] = (
        ("frame_to_cutting_half", "frame_to_counter_half"),
    )
    return model


def build_seeded_picturex_0611_garden_pruner(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_picturex_0611_garden_pruner(config_from_seed(seed), assets=assets)


# --- authored tests ---------------------------------------------------------
def _parts_by_role(model: ArticulatedObject, role: str):
    return [p for p in model.parts if p.meta.get("role") == role]


def run_picturex_0611_garden_pruner_tests(
    model: ArticulatedObject, config: Config
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)

    frames = _parts_by_role(model, "pivot_frame")
    cuts = _parts_by_role(model, "cutting_half")
    counters = _parts_by_role(model, "counter_half")
    springs = _parts_by_role(model, "return_spring")
    catches = _parts_by_role(model, "locking_catch")
    joints = {j.name: j for j in model.articulations}
    cut_joint = joints.get("frame_to_cutting_half")
    cnt_joint = joints.get("frame_to_counter_half")

    ctx.check(
        "category_anchor: both halves turn on the one main pivot",
        len(frames) == 1
        and len(cuts) == 1
        and len(counters) == 1
        and bool(model.root_parts())
        and model.root_parts()[0].name == "pivot_frame"
        and all(
            j is not None
            and j.articulation_type == ArticulationType.REVOLUTE
            and j.parent == "pivot_frame"
            and tuple(round(abs(v), 6) for v in j.axis) == (0.0, 0.0, 1.0)
            and j.motion_limits is not None
            and abs(abs(j.motion_limits.upper - j.motion_limits.lower) - r.open_angle_rad) < 1e-6
            for j in (cut_joint, cnt_joint)
        ),
        details=f"halves={len(cuts)}/{len(counters)} open={r.open_angle_rad}",
    )

    # Decisive motion evidence, read from primitive elements only.
    tip_elem = {
        "bypass_blade": "head_build__bypass_blade__cutting_edge",
        "hooked_beak": "head_build__hooked_beak__hook_tip",
        "long_bypass": "head_build__long_bypass__cutting_edge",
        "anvil_insert": "head_build__anvil_insert__insert_screw",
    }[r.head_build]
    tip_part = cuts[0] if r.head_build in ("bypass_blade", "long_bypass") else counters[0]
    closed_tip = ctx.part_element_world_aabb(tip_part, elem=tip_elem)
    with ctx.pose({cut_joint: r.open_angle_rad, cnt_joint: -r.open_angle_rad}):
        open_tip = ctx.part_element_world_aabb(tip_part, elem=tip_elem)
        open_spring = ctx.part_world_aabb(springs[0]) if springs else None
    closed_spring = ctx.part_world_aabb(springs[0]) if springs else None
    ctx.check(
        "category_anchor: the jaws close and the spring reopens them",
        len(springs) == r.spring_stage_count
        and closed_tip is not None
        and open_tip is not None
        and abs(open_tip[1][1] - closed_tip[1][1]) > r.jaw_length_m * 0.10
        and closed_spring is not None
        and open_spring is not None
        and (
            abs(open_spring[0][0] - closed_spring[0][0])
            + abs(open_spring[0][1] - closed_spring[0][1])
        )
        > 1e-4,
        details=(
            f"springs={len(springs)} tip={closed_tip}->{open_tip} "
            f"spring={closed_spring}->{open_spring}"
        ),
    )

    visual_names = {v.name or "" for p in model.parts for v in p.visuals}
    head_marker = {
        "bypass_blade": "bypass_blade__cutting_edge",
        "hooked_beak": "hooked_beak__hook_tip",
        "long_bypass": "long_bypass__cutting_edge",
        "anvil_insert": "anvil_insert__anvil_insert",
    }[r.head_build]
    ctx.check(
        "category_anchor: head_build identity",
        any(head_marker in n for n in visual_names),
        details=f"head_build={r.head_build}",
    )

    handle_marker = {
        "sculpted_grip": "sculpted_grip__grip_rib_",
        "plate_frame": "plate_frame__grip_shell_",
    }[r.handle_build]
    ctx.check(
        "category_anchor: handle_build identity",
        any(handle_marker in n for n in visual_names),
        details=f"handle_build={r.handle_build}",
    )

    return_marker = {
        "coil_seat": "coil_seat__seat_cup_",
        "torsion_coil": "torsion_coil__coil_ring_",
        "leaf_spring": "leaf_spring__leaf_root_",
    }[r.return_build]
    ctx.check(
        "category_anchor: return_build identity",
        any(return_marker in n for n in visual_names) and len(springs) == r.spring_stage_count,
        details=f"return_build={r.return_build} stages={len(springs)}",
    )

    catch_marker = {
        "swing_latch": "swing_latch__latch_hook",
        "thumb_slider": "thumb_slider__thumb_pad",
        "ratchet_pawl": "ratchet_pawl__pawl_tooth_",
        "stop_screw": "stop_screw__screw_shank",
        "rotating_sleeve": "rotating_sleeve__sleeve_rib_",
    }[r.catch_build]
    ctx.check(
        "category_anchor: catch_build identity",
        len(catches) == 1 and any(catch_marker in n for n in visual_names),
        details=f"catch_build={r.catch_build}",
    )

    ctx.check(
        "jaw, handle and spring stations are consistent",
        r.jaw_length_m > 0.040
        and r.handle_length_m > 0.100
        and 0.0 < r.spring_station_m < r.catch_station_m < r.handle_length_m
        and r.spring_travel_m > 0.010,
        details=(
            f"jaw={r.jaw_length_m} handle={r.handle_length_m} "
            f"spring={r.spring_station_m} catch={r.catch_station_m}"
        ),
    )

    ctx.check(
        "domain choices recorded on the model",
        model.meta.get("slot_choices") == slot_choices_for_config(r),
    )
    return ctx.report()


TEMPLATE_CORNERS = (
    corner_case(
        "smallest_widest_jaw_two_stage",
        {
            "head_build": "long_bypass",
            "return_build": "coil_seat",
            "catch_build": "thumb_slider",
            "handle_build": "plate_frame",
            "spring_stage_count": 2,
            "tool_length_m": 0.180,
            "jaw_ratio": 0.38,
            "open_angle_rad": 0.72,
        },
        reason="shortest tool with the longest jaw, widest opening and a stacked spring",
    ),
    corner_case(
        "largest_shortest_jaw_single",
        {
            "head_build": "anvil_insert",
            "return_build": "leaf_spring",
            "catch_build": "ratchet_pawl",
            "handle_build": "sculpted_grip",
            "spring_stage_count": 1,
            "tool_length_m": 0.260,
            "jaw_ratio": 0.24,
            "open_angle_rad": 0.42,
        },
        reason="longest handles with the shortest jaw and the tightest opening",
    ),
    corner_case(
        "torsion_sleeve_wide_open",
        {
            "head_build": "hooked_beak",
            "return_build": "torsion_coil",
            "catch_build": "rotating_sleeve",
            "handle_build": "plate_frame",
            "spring_stage_count": 2,
            "tool_length_m": 0.260,
            "jaw_ratio": 0.38,
            "open_angle_rad": 0.72,
        },
        reason="largest envelope: two torsion stages at the pivot with a turning grip sleeve",
    ),
    corner_case(
        "tight_stop_screw",
        {
            "head_build": "bypass_blade",
            "return_build": "coil_seat",
            "catch_build": "stop_screw",
            "handle_build": "sculpted_grip",
            "spring_stage_count": 1,
            "tool_length_m": 0.180,
            "jaw_ratio": 0.24,
            "open_angle_rad": 0.42,
        },
        reason="smallest tool with the shortest jaw and the stop screw at full travel",
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
    "build_picturex_0611_garden_pruner",
    "build_seeded_picturex_0611_garden_pruner",
    "run_picturex_0611_garden_pruner_tests",
]
