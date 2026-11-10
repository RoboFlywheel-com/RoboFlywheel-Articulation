# SPDX-License-Identifier: Apache-2.0

# ruff: noqa: E501
"""Modular procedural template for category ``worm_gear_and_wheel_assembly``.

A meshing worm-and-wheel transmission: a steel worm (helical thread) drives a
brass toothed wheel about **perpendicular** axes (wheel about Y; worm about X or
Z). Both members carry a real rotational (CONTINUOUS) joint on a fixed
``housing``; the wheel follows the worm via a ``Mimic`` gear ratio. The worm
thread stays tangent-meshing with the wheel teeth across every slot combination
because the center distance is DERIVED
(``center_distance = wheel_tip_radius + thread_outer_radius + mesh_clearance``),
never hardcoded.

Slots (see ``specs_modular_v1/worm_gear_and_wheel_assembly.md``):
- housing_topology: open_pillow_block / enclosed_gearbox / split_housing (① root shell)
- mesh_orientation: top_mesh / vertical_shaft (③ primary form family; also worm joint axis)
- worm_starts: 1 / 2 / 4 thread ribbons (① multiplicity)
- backlash_adjustment: eccentric_bearing (2 joints) / sliding_carriage (3 joints, +PRISMATIC) (②)
- palette_style: 5 metal/brass/cast colorways (⑥)

Geometry policy: lightweight custom mesh (LatheGeometry shaft + triangular
helical ribbon + ExtrudeWithHolesGeometry toothed wheel) — no cadquery — to hold
the ≤12s/seed compile budget. Adapted from the 5-star origins S1
(``rec_...__001_png_c097f6455b834d47b95478b26e163c36``) and S2
(``rec_...__002_png_d1bae7f8a0f645068588a092bf260924``) and their forked anchors.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, replace
from typing import Literal

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    ExtrudeWithHolesGeometry,
    LatheGeometry,
    MatingContract,
    MeshGeometry,
    Mimic,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_geometry,
)

__modular__ = True

HousingTopology = Literal["open_pillow_block", "enclosed_gearbox", "split_housing"]
MeshOrientation = Literal["top_mesh", "vertical_shaft"]
BacklashAdjustment = Literal["eccentric_bearing", "sliding_carriage"]
PaletteStyle = Literal[
    "polished_steel_brass",
    "cast_iron_brass",
    "gunmetal_bronze",
    "machined_steel",
    "blackened_steel_brass",
]

HOUSING_TOPOLOGIES: tuple[HousingTopology, ...] = (
    "open_pillow_block",
    "enclosed_gearbox",
    "split_housing",
)
MESH_ORIENTATIONS: tuple[MeshOrientation, ...] = ("top_mesh", "vertical_shaft")
WORM_STARTS: tuple[int, ...] = (1, 2, 4)
BACKLASH_ADJUSTMENTS: tuple[BacklashAdjustment, ...] = (
    "eccentric_bearing",
    "sliding_carriage",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "polished_steel_brass",
    "cast_iron_brass",
    "gunmetal_bronze",
    "machined_steel",
    "blackened_steel_brass",
)

# Realistic bench-scale worm-and-wheel colorways observed across the 5-star
# sources (S1 polished-steel/brass, S2/S3 cast-iron/brass) plus same-family
# extrapolated metal finishes. Keys drive every ``.visual(..., material=mats[k])``.
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "polished_steel_brass": {
        "brass": (1.00, 0.67, 0.18, 1.0),
        "steel": (0.78, 0.78, 0.82, 1.0),
        "dark": (0.055, 0.050, 0.045, 1.0),
        "housing": (0.33, 0.34, 0.36, 1.0),
        "hardware": (0.82, 0.84, 0.86, 1.0),
    },
    "cast_iron_brass": {
        "brass": (0.92, 0.68, 0.24, 1.0),
        "steel": (0.70, 0.70, 0.66, 1.0),
        "dark": (0.10, 0.10, 0.10, 1.0),
        "housing": (0.15, 0.16, 0.17, 1.0),
        "hardware": (0.56, 0.57, 0.59, 1.0),
    },
    "gunmetal_bronze": {
        "brass": (0.80, 0.55, 0.28, 1.0),
        "steel": (0.62, 0.64, 0.66, 1.0),
        "dark": (0.06, 0.06, 0.07, 1.0),
        "housing": (0.21, 0.23, 0.25, 1.0),
        "hardware": (0.70, 0.71, 0.72, 1.0),
    },
    "machined_steel": {
        "brass": (0.86, 0.72, 0.40, 1.0),
        "steel": (0.75, 0.76, 0.78, 1.0),
        "dark": (0.12, 0.12, 0.13, 1.0),
        "housing": (0.47, 0.48, 0.50, 1.0),
        "hardware": (0.80, 0.82, 0.84, 1.0),
    },
    "blackened_steel_brass": {
        "brass": (0.95, 0.70, 0.22, 1.0),
        "steel": (0.80, 0.81, 0.84, 1.0),
        "dark": (0.030, 0.030, 0.032, 1.0),
        "housing": (0.095, 0.095, 0.105, 1.0),
        "hardware": (0.50, 0.51, 0.52, 1.0),
    },
}

WHEEL_TEETH = 36

# Base (scale=1.0) dimensions, sourced from S1 (L24-L37).
_BASE_TIP = 0.0420
_BASE_ROOT_FRAC = 0.0365 / 0.0420  # tooth depth ratio, keep tooth shape on scale
_BASE_WIDTH = 0.012
_BASE_BORE = 0.0066
_BASE_HUB_R = 0.0165
_BASE_HUB_W = 0.020
_BASE_THREAD_OUTER = 0.0102
_BASE_THREAD_ROOT = 0.0067
_BASE_THREAD_PITCH = 0.00675
_BASE_SHAFT_R = 0.0065
_BASE_THREAD_LEN = 0.054
MESH_CLEARANCE = 0.0012  # thread-crest to tooth-tip running clearance (S1 L37 ~0.35mm, widened for tessellation safety)


@dataclass(frozen=True)
class WormGearAndWheelAssemblyConfig:
    housing_topology: HousingTopology | None = None
    mesh_orientation: MeshOrientation | None = None
    worm_starts: int | None = None
    backlash_adjustment: BacklashAdjustment | None = None
    palette_style: PaletteStyle | None = None
    wheel_size_scale: float = 1.0
    worm_size_scale: float = 1.0
    worm_length_scale: float = 1.0
    name: str = "worm_gear_and_wheel_assembly"


@dataclass(frozen=True)
class ResolvedWormGearAndWheelAssemblyConfig:
    housing_topology: HousingTopology
    mesh_orientation: MeshOrientation
    worm_starts: int
    backlash_adjustment: BacklashAdjustment
    palette_style: PaletteStyle
    name: str
    palette: dict[str, tuple[float, float, float, float]]
    # derived wheel dims
    tip_radius: float
    root_radius: float
    wheel_width: float
    bore_radius: float
    hub_radius: float
    hub_width: float
    # derived worm dims
    thread_outer: float
    thread_root: float
    thread_pitch: float
    shaft_radius: float
    thread_length: float
    shaft_length: float
    # meshing geometry
    center_distance: float
    worm_center: tuple[float, float, float]
    worm_axis: tuple[float, float, float]
    worm_rpy: tuple[float, float, float]
    mesh_dir: tuple[float, float, float]
    mesh_axis: str  # "x" or "z" — axis of the running clearance
    footprint_axes: str  # projection plane for the meshing overlap test
    # housing envelope
    y_back: float
    floor_z: float
    carriage_travel: float


def _clampf(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def _choice(value: str | None, allowed: tuple[str, ...], fallback: str, field: str) -> str:
    if value is None:
        return fallback
    if value not in allowed:
        raise ValueError(f"Unsupported {field}: {value}")
    return value


def config_from_seed(seed: int) -> WormGearAndWheelAssemblyConfig:
    rng = random.Random(seed)
    return WormGearAndWheelAssemblyConfig(
        housing_topology=rng.choice(HOUSING_TOPOLOGIES),
        mesh_orientation=rng.choice(MESH_ORIENTATIONS),
        worm_starts=rng.choice(WORM_STARTS),
        backlash_adjustment=rng.choice(BACKLASH_ADJUSTMENTS),
        palette_style=rng.choice(PALETTE_STYLES),
        wheel_size_scale=round(rng.uniform(0.85, 1.25), 4),
        worm_size_scale=round(rng.uniform(0.90, 1.15), 4),
        worm_length_scale=round(rng.uniform(0.85, 1.25), 4),
        name=f"seeded_worm_gear_and_wheel_assembly_{seed}",
    )


def resolve_config(
    config: WormGearAndWheelAssemblyConfig,
) -> ResolvedWormGearAndWheelAssemblyConfig:
    housing = _choice(
        config.housing_topology, HOUSING_TOPOLOGIES, "open_pillow_block", "housing_topology"
    )
    orientation = _choice(
        config.mesh_orientation, MESH_ORIENTATIONS, "top_mesh", "mesh_orientation"
    )
    starts = config.worm_starts if config.worm_starts in WORM_STARTS else 1
    backlash = _choice(
        config.backlash_adjustment,
        BACKLASH_ADJUSTMENTS,
        "eccentric_bearing",
        "backlash_adjustment",
    )
    palette_style = _choice(
        config.palette_style, PALETTE_STYLES, "polished_steel_brass", "palette_style"
    )

    ws = _clampf(config.wheel_size_scale, 0.85, 1.25)
    ss = _clampf(config.worm_size_scale, 0.90, 1.15)
    ls = _clampf(config.worm_length_scale, 0.85, 1.25)

    # --- wheel dims (equation-locked to keep tooth shape) ---
    tip_radius = _BASE_TIP * ws
    root_radius = tip_radius * _BASE_ROOT_FRAC
    wheel_width = _BASE_WIDTH * ws
    bore_radius = _BASE_BORE * ws
    hub_radius = _BASE_HUB_R * ws
    hub_width = _BASE_HUB_W * ws

    # --- worm dims ---
    thread_outer = _BASE_THREAD_OUTER * ss
    thread_root = _BASE_THREAD_ROOT * ss
    thread_pitch = _BASE_THREAD_PITCH * ss
    shaft_radius = _BASE_SHAFT_R * ss
    thread_length = _BASE_THREAD_LEN * ls
    # inequality: shaft must overhang the thread on both ends for its bearings.
    shaft_length = max(thread_length + 0.060, thread_length + 0.106 * ls)

    # --- meshing geometry (DERIVED, never hardcoded) ---
    center_distance = tip_radius + thread_outer + MESH_CLEARANCE

    if orientation == "top_mesh":
        worm_center = (0.0, 0.0, center_distance)
        worm_axis = (1.0, 0.0, 0.0)
        worm_rpy = (0.0, math.pi / 2.0, 0.0)
        mesh_dir = (0.0, 0.0, 1.0)
        mesh_axis = "z"
        footprint_axes = "xy"
    else:  # vertical_shaft
        worm_center = (center_distance, 0.0, 0.0)
        worm_axis = (0.0, 0.0, 1.0)
        worm_rpy = (0.0, 0.0, 0.0)
        mesh_dir = (1.0, 0.0, 0.0)
        mesh_axis = "x"
        footprint_axes = "yz"

    hub_hw = hub_width / 2.0
    y_back = hub_hw + 0.055
    # floor must clear the lowest point of the rotating envelope (the worm drops to
    # -shaft/2 in the vertical_shaft orientation).
    worm_lowest_z = worm_center[2] - (shaft_length / 2.0 if orientation == "vertical_shaft" else thread_outer)
    floor_z = min(-(tip_radius + 0.020), worm_lowest_z - 0.016)

    # conditional: prismatic backlash travel (only sliding_carriage uses it).
    carriage_travel = 0.005 if backlash == "sliding_carriage" else 0.0

    return ResolvedWormGearAndWheelAssemblyConfig(
        housing_topology=housing,
        mesh_orientation=orientation,
        worm_starts=starts,
        backlash_adjustment=backlash,
        palette_style=palette_style,
        name=config.name or "worm_gear_and_wheel_assembly",
        palette=dict(PALETTES[palette_style]),
        tip_radius=tip_radius,
        root_radius=root_radius,
        wheel_width=wheel_width,
        bore_radius=bore_radius,
        hub_radius=hub_radius,
        hub_width=hub_width,
        thread_outer=thread_outer,
        thread_root=thread_root,
        thread_pitch=thread_pitch,
        shaft_radius=shaft_radius,
        thread_length=thread_length,
        shaft_length=shaft_length,
        center_distance=center_distance,
        worm_center=worm_center,
        worm_axis=worm_axis,
        worm_rpy=worm_rpy,
        mesh_dir=mesh_dir,
        mesh_axis=mesh_axis,
        footprint_axes=footprint_axes,
        y_back=y_back,
        floor_z=floor_z,
        carriage_travel=carriage_travel,
    )


def with_overrides(
    config: WormGearAndWheelAssemblyConfig, **kwargs: object
) -> WormGearAndWheelAssemblyConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: WormGearAndWheelAssemblyConfig | ResolvedWormGearAndWheelAssemblyConfig,
) -> tuple[tuple[str, str], ...]:
    r = (
        config
        if isinstance(config, ResolvedWormGearAndWheelAssemblyConfig)
        else resolve_config(config)
    )
    return (
        ("housing_topology", r.housing_topology),
        ("mesh_orientation", r.mesh_orientation),
        ("worm_starts", f"{r.worm_starts}_start_worm"),
        ("backlash_adjustment", r.backlash_adjustment),
        ("palette_style", r.palette_style),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# --------------------------------------------------------------------------- #
# Geometry helpers (adapted from S1: rec_...__001_png_c097f6455b834d47b95478b26e163c36)
# --------------------------------------------------------------------------- #


def _circle_profile(radius: float, segments: int = 48) -> list[tuple[float, float]]:
    return [
        (
            radius * math.cos(2.0 * math.pi * i / segments),
            radius * math.sin(2.0 * math.pi * i / segments),
        )
        for i in range(segments)
    ]


def _toothed_wheel_profile(
    teeth: int, root_radius: float, tip_radius: float
) -> list[tuple[float, float]]:
    """Involute-like tooth silhouette with flat crests and root lands (S1 L51-L72)."""
    points: list[tuple[float, float]] = []
    tooth_step = 2.0 * math.pi / teeth
    for tooth in range(teeth):
        base = tooth * tooth_step
        for fraction, radius in (
            (0.00, root_radius),
            (0.16, root_radius),
            (0.32, tip_radius),
            (0.50, tip_radius),
            (0.68, tip_radius),
            (0.84, root_radius),
        ):
            angle = base + fraction * tooth_step
            points.append((radius * math.cos(angle), radius * math.sin(angle)))
    return points


def _helical_thread_geometry(
    *,
    length: float,
    pitch: float,
    root_radius: float,
    outer_radius: float,
    ribbon_width: float,
    phase: float = 0.0,
    samples_per_turn: int = 24,
) -> MeshGeometry:
    """Closed triangular helical ridge around local +Z (S1 L75-L119), with a start ``phase``."""
    turns = length / pitch
    samples = max(24, int(turns * samples_per_turn) + 1)
    geom = MeshGeometry()

    left_indices: list[int] = []
    crest_indices: list[int] = []
    right_indices: list[int] = []
    for i in range(samples):
        frac = i / (samples - 1)
        z = -length / 2.0 + frac * length
        angle = phase + 2.0 * math.pi * turns * frac
        c = math.cos(angle)
        s = math.sin(angle)
        left_indices.append(
            geom.add_vertex(root_radius * c, root_radius * s, z - ribbon_width / 2.0)
        )
        crest_indices.append(geom.add_vertex(outer_radius * c, outer_radius * s, z))
        right_indices.append(
            geom.add_vertex(root_radius * c, root_radius * s, z + ribbon_width / 2.0)
        )

    for i in range(samples - 1):
        l0, l1 = left_indices[i], left_indices[i + 1]
        c0, c1 = crest_indices[i], crest_indices[i + 1]
        r0, r1 = right_indices[i], right_indices[i + 1]
        geom.add_face(l0, l1, c1)
        geom.add_face(l0, c1, c0)
        geom.add_face(c0, c1, r1)
        geom.add_face(c0, r1, r0)
        geom.add_face(l0, r0, r1)
        geom.add_face(l0, r1, l1)

    geom.add_face(left_indices[0], crest_indices[0], right_indices[0])
    geom.add_face(left_indices[-1], right_indices[-1], crest_indices[-1])
    return geom


def _box(part, size, xyz, material, name, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(Box(size), origin=Origin(xyz=xyz, rpy=rpy), material=material, name=name, material_class_id="metal.paint_coated")


def _cyl(part, radius, length, xyz, material, name, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=Origin(xyz=xyz, rpy=rpy),
        material=material,
        name=name, material_class_id="metal.steel_bare",
    )


# rpy that lays a default-Z cylinder along an axis
_Y_CYL = (math.pi / 2.0, 0.0, 0.0)
_X_CYL = (0.0, math.pi / 2.0, 0.0)
_Z_CYL = (0.0, 0.0, 0.0)


def _worm_end_points(r: ResolvedWormGearAndWheelAssemblyConfig) -> list[tuple[float, float, float]]:
    """World positions of the two worm shaft-end bearings."""
    half = r.shaft_length / 2.0 - 0.012
    cx, cy, cz = r.worm_center
    ax = r.worm_axis
    return [
        (cx - ax[0] * half, cy - ax[1] * half, cz - ax[2] * half),
        (cx + ax[0] * half, cy + ax[1] * half, cz + ax[2] * half),
    ]


def _worm_collar_rpy(r: ResolvedWormGearAndWheelAssemblyConfig) -> tuple[float, float, float]:
    return _X_CYL if r.mesh_orientation == "top_mesh" else _Z_CYL


# --------------------------------------------------------------------------- #
# Wheel
# --------------------------------------------------------------------------- #


def _build_wheel(model: ArticulatedObject, r: ResolvedWormGearAndWheelAssemblyConfig, mats) -> None:
    wheel = model.part(
        "worm_wheel",
        meta={
            "role": "driven_worm_wheel",
            "teeth": WHEEL_TEETH,
            "central_bore_diameter_m": 2.0 * r.bore_radius,
            "has_set_screw_holes": True,
        },
    )
    wrpy = (-math.pi / 2.0, 0.0, 0.0)
    wheel.visual(
        mesh_from_geometry(
            ExtrudeWithHolesGeometry(
                _toothed_wheel_profile(WHEEL_TEETH, r.root_radius, r.tip_radius),
                [_circle_profile(r.bore_radius, 48)],
                r.wheel_width,
                center=True,
            ),
            "brass_toothed_wheel",
        ),
        origin=Origin(rpy=wrpy),
        material=mats["brass"],
        name="toothed_rim", material_class_id=("metal.brass_polished" if r.palette_style in {"polished_steel_brass", "cast_iron_brass", "machined_steel", "blackened_steel_brass"} else "metal.bronze_cast"),
    )
    wheel.visual(
        mesh_from_geometry(
            ExtrudeWithHolesGeometry(
                _circle_profile(r.hub_radius, 48),
                [_circle_profile(r.bore_radius, 48)],
                r.hub_width,
                center=True,
            ),
            "raised_bored_hub",
        ),
        origin=Origin(rpy=wrpy),
        material=mats["brass"],
        name="bored_hub", material_class_id=("metal.brass_polished" if r.palette_style in {"polished_steel_brass", "cast_iron_brass", "machined_steel", "blackened_steel_brass"} else "metal.bronze_cast"),
    )
    hub_hw = r.hub_width / 2.0
    # dark bore trace (④ host-derived detail)
    wheel.visual(
        Cylinder(radius=r.bore_radius * 0.98, length=0.0010),
        origin=Origin(xyz=(0.0, -hub_hw - 0.0004, 0.0), rpy=_Y_CYL),
        material=mats["dark"],
        name="dark_bore_depth", material_class_id="metal.blackened_gunmetal",
    )
    for i, angle in enumerate((math.radians(42.0), math.radians(222.0))):
        wheel.visual(
            Cylinder(radius=r.hub_radius * 0.09, length=0.0012),
            origin=Origin(
                xyz=(
                    (r.hub_radius * 0.64) * math.cos(angle),
                    -hub_hw - 0.0002,
                    (r.hub_radius * 0.64) * math.sin(angle),
                ),
                rpy=_Y_CYL,
            ),
            material=mats["dark"],
            name=f"set_screw_hole_{i}", material_class_id="metal.blackened_gunmetal",
        )
    # rear axle stub + thrust collar toward +Y housing bearing
    wheel.visual(
        Cylinder(radius=r.bore_radius * 1.5, length=0.045),
        origin=Origin(xyz=(0.0, hub_hw + 0.0225, 0.0), rpy=_Y_CYL),
        material=mats["steel"],
        name="rear_axle_stub", material_class_id=("metal.steel_bare" if r.palette_style in {"polished_steel_brass", "gunmetal_bronze", "machined_steel", "blackened_steel_brass"} else "metal.cast_iron_bare"),
    )
    thrust_face_y = r.y_back - 0.030
    wheel.visual(
        Cylinder(radius=r.hub_radius * 1.6, length=0.006),
        origin=Origin(xyz=(0.0, thrust_face_y - 0.003, 0.0), rpy=_Y_CYL),
        material=mats["steel"],
        name="axle_thrust_collar", material_class_id=("metal.steel_bare" if r.palette_style in {"polished_steel_brass", "gunmetal_bronze", "machined_steel", "blackened_steel_brass"} else "metal.cast_iron_bare"),
    )


# --------------------------------------------------------------------------- #
# Worm
# --------------------------------------------------------------------------- #


def _build_worm(model: ArticulatedObject, r: ResolvedWormGearAndWheelAssemblyConfig, mats) -> None:
    worm = model.part(
        "worm_shaft",
        meta={
            "role": "input_worm",
            "shaft_shape": "long_chamfered_cylinder",
            "has_helical_thread": True,
            "thread_pitch_m": r.thread_pitch,
            "thread_starts": r.worm_starts,
        },
    )
    rpy = r.worm_rpy
    sr = r.shaft_radius
    sl = r.shaft_length
    shaft_profile = [
        (0.0, -sl / 2.0),
        (sr * 0.80, -sl / 2.0),
        (sr, -sl / 2.0 + 0.004),
        (sr, sl / 2.0 - 0.004),
        (sr * 0.80, sl / 2.0),
        (0.0, sl / 2.0),
    ]
    worm.visual(
        mesh_from_geometry(LatheGeometry(shaft_profile, segments=48), "chamfered_worm_shaft"),
        origin=Origin(rpy=rpy),
        material=mats["steel"],
        name="chamfered_shaft", material_class_id=("metal.steel_bare" if r.palette_style in {"polished_steel_brass", "gunmetal_bronze", "machined_steel", "blackened_steel_brass"} else "metal.cast_iron_bare"),
    )
    # N thread ribbons, equally phased (multiplicity axis — same outer radius so
    # meshing geometry is invariant to N).
    for k in range(r.worm_starts):
        phase = 2.0 * math.pi * k / r.worm_starts
        worm.visual(
            mesh_from_geometry(
                _helical_thread_geometry(
                    length=r.thread_length,
                    pitch=r.thread_pitch,
                    root_radius=r.thread_root,
                    outer_radius=r.thread_outer,
                    ribbon_width=0.50 * r.thread_pitch,
                    phase=phase,
                ),
                f"helical_thread_start_{k}",
            ),
            origin=Origin(rpy=rpy),
            material=mats["steel"],
            name=f"helical_thread_{k}", material_class_id=("metal.steel_bare" if r.palette_style in {"polished_steel_brass", "gunmetal_bronze", "machined_steel", "blackened_steel_brass"} else "metal.cast_iron_bare"),
        )
    # dark valley shadow spiral (④ host-derived)
    worm.visual(
        mesh_from_geometry(
            _helical_thread_geometry(
                length=r.thread_length * 0.96,
                pitch=r.thread_pitch,
                root_radius=r.thread_root * 0.99,
                outer_radius=r.thread_root * 1.03,
                ribbon_width=0.0013,
                samples_per_turn=18,
            ),
            "worm_valley_shadow_spiral",
        ),
        origin=Origin(rpy=rpy),
        material=mats["dark"],
        name="valley_shadow", material_class_id="metal.blackened_gunmetal",
    )
    # shaft shoulders flanking the thread
    ax = r.worm_axis
    for i, sgn in enumerate((-1.0, 1.0)):
        off = r.thread_length / 2.0 + 0.002
        worm.visual(
            Cylinder(radius=sr * 1.18, length=0.0035),
            origin=Origin(
                xyz=(ax[0] * sgn * off, ax[1] * sgn * off, ax[2] * sgn * off),
                rpy=_worm_collar_rpy(r),
            ),
            material=mats["steel"],
            name=f"thread_shoulder_{i}", material_class_id=("metal.steel_bare" if r.palette_style in {"polished_steel_brass", "gunmetal_bronze", "machined_steel", "blackened_steel_brass"} else "metal.cast_iron_bare"),
        )


# --------------------------------------------------------------------------- #
# Housing skeleton + topology shells
# --------------------------------------------------------------------------- #


def _worm_radial(r: ResolvedWormGearAndWheelAssemblyConfig) -> float:
    """Max radial extent of the worm assembly (thread crest vs bearing cap)."""
    return max(r.thread_outer, (r.shaft_radius + 0.006) * 1.35)


def _worm_top(r: ResolvedWormGearAndWheelAssemblyConfig) -> float:
    """Highest z reached by the rotating worm envelope."""
    if r.mesh_orientation == "top_mesh":
        return r.center_distance + _worm_radial(r) + 0.006
    return r.shaft_length / 2.0 + 0.008


def _envelope_x(r: ResolvedWormGearAndWheelAssemblyConfig) -> float:
    """Half x-extent of the rotating envelope."""
    if r.mesh_orientation == "top_mesh":
        return r.shaft_length / 2.0 + 0.008
    return r.center_distance + _worm_radial(r)


def _shell_half_x(r: ResolvedWormGearAndWheelAssemblyConfig) -> float:
    """Padded half-x for shell walls / base, clearing the carriage rail travel."""
    return _envelope_x(r) + 0.026


def _shell_top(r: ResolvedWormGearAndWheelAssemblyConfig) -> float:
    return _worm_top(r) + 0.022


def _build_bearing_skeleton(housing, r, mats, *, worm_on_housing: bool) -> None:
    """Base slab + rear support wall + wheel thrust bearing (+ worm bearings when eccentric)."""
    env_x = _shell_half_x(r)
    top_z = _shell_top(r)
    floor_z = r.floor_z
    y_back = r.y_back
    base_w = 2.0 * env_x + 0.02
    base_d = y_back + 0.02
    base_h = 0.012

    # grounded base slab
    _box(
        housing,
        (base_w, base_d, base_h),
        (0.0, base_d / 2.0 - 0.01, floor_z + base_h / 2.0),
        mats["housing"],
        "base_slab",
    )
    # rear support wall (everything cantilevers off it)
    wall_h = top_z - floor_z
    _box(
        housing,
        (base_w * 0.94, 0.014, wall_h),
        (0.0, y_back, floor_z + wall_h / 2.0),
        mats["housing"],
        "rear_wall",
    )
    # wheel thrust bearing collar, embedded into the rear wall
    _cyl(
        housing,
        r.hub_radius * 1.7,
        0.030,
        (0.0, y_back - 0.015, 0.0),
        mats["steel"],
        "wheel_bearing_collar",
        _Y_CYL,
    )
    if worm_on_housing:
        _build_worm_bearings(housing, r, mats, connect_to_rear=True)


def _build_worm_bearings(owner, r, mats, *, connect_to_rear: bool) -> None:
    """Two bearing collars at the worm ends + brackets back to the rear support."""
    col_rpy = _worm_collar_rpy(r)
    col_r = r.shaft_radius + 0.006
    for i, (ex, ey, ez) in enumerate(_worm_end_points(r)):
        _cyl(owner, col_r, 0.020, (ex, ey, ez), mats["steel"], f"worm_bearing_collar_{i}", col_rpy)
        _cyl(
            owner,
            col_r * 1.35,
            0.010,
            (ex, ey, ez),
            mats["hardware"],
            f"worm_bearing_cap_{i}",
            col_rpy,
        )
        if connect_to_rear:
            # bracket from the collar (y≈0) back to the rear wall (y=y_back)
            depth = r.y_back - ey
            _box(
                owner,
                (col_r * 2.0, depth, col_r * 2.0),
                (ex, ey + depth / 2.0, ez),
                mats["housing"],
                f"worm_bearing_bracket_{i}",
            )


def _build_open_pillow_block(housing, r, mats) -> None:
    """Exposed pillow-block frame — minimal side posts, no shell (S1 L141-L178)."""
    floor_z = r.floor_z
    post_h = _shell_top(r) - floor_z - 0.006
    for sgn, tag in ((-1.0, "l"), (1.0, "r")):
        px = sgn * (_shell_half_x(r) - 0.004)
        _box(
            housing,
            (0.014, r.y_back + 0.02, post_h),
            (px, r.y_back / 2.0, floor_z + post_h / 2.0 + 0.006),
            mats["housing"],
            f"pillow_post_{tag}",
        )
        _box(
            housing,
            (0.030, 0.030, 0.012),
            (px, r.y_back - 0.02, floor_z + 0.006),
            mats["hardware"],
            f"pillow_foot_{tag}",
        )


def _build_enclosed_gearbox(housing, r, mats) -> None:
    """Cast box shell around the mechanism, front (-Y) open as a service aperture (S3 L145-L205)."""
    env_x = _shell_half_x(r)
    top_z = _shell_top(r)
    floor_z = r.floor_z
    y_back = r.y_back
    wall = 0.012
    inner_h = top_z - floor_z
    # side walls (outside the rotating envelope in x)
    for sgn, tag in ((-1.0, "l"), (1.0, "r")):
        _box(
            housing,
            (wall, y_back + 0.02, inner_h),
            (sgn * (env_x + wall / 2.0 + 0.004), y_back / 2.0, floor_z + inner_h / 2.0),
            mats["housing"],
            f"gearbox_side_{tag}",
        )
    # top cover (above the worm envelope)
    _box(
        housing,
        (2.0 * env_x + 2.0 * wall + 0.02, y_back + 0.02, wall),
        (0.0, y_back / 2.0, top_z + wall / 2.0),
        mats["housing"],
        "gearbox_top",
    )
    # front lip frames (thin outer-corner posts; stay clear of the worm ends)
    lip_w = min(env_x * 0.20, 0.022)
    for sgn, tag in ((-1.0, "l"), (1.0, "r")):
        _box(
            housing,
            (lip_w, wall, inner_h),
            (sgn * (env_x - lip_w / 2.0 + 0.004), -wall / 2.0, floor_z + inner_h / 2.0),
            mats["housing"],
            f"gearbox_front_lip_{tag}",
        )
    # mounting feet
    for sgn, tag in ((-1.0, "l"), (1.0, "r")):
        _box(
            housing,
            (env_x * 0.5, y_back * 0.7, 0.014),
            (sgn * (env_x * 0.55), y_back * 0.45, floor_z - 0.007),
            mats["housing"],
            f"gearbox_foot_{tag}",
        )


def _build_split_housing(housing, r, mats) -> None:
    """Upper/lower split housing halves with a parting flange + bolt bosses (S4 L145-L260)."""
    env_x = _shell_half_x(r)
    top_z = _shell_top(r)
    floor_z = r.floor_z
    y_back = r.y_back
    wall = 0.012
    part_z = (floor_z + top_z) / 2.0
    # lower half side rails
    for sgn, tag in ((-1.0, "l"), (1.0, "r")):
        _box(
            housing,
            (wall, y_back + 0.02, part_z - floor_z),
            (sgn * (env_x + wall / 2.0 + 0.004), y_back / 2.0, (floor_z + part_z) / 2.0),
            mats["housing"],
            f"lower_side_{tag}",
        )
        # upper half side rails
        _box(
            housing,
            (wall, y_back + 0.02, top_z - part_z),
            (sgn * (env_x + wall / 2.0 + 0.004), y_back / 2.0, (part_z + top_z) / 2.0),
            mats["housing"],
            f"upper_side_{tag}",
        )
        # parting flange plates
        _box(
            housing,
            (0.026, y_back + 0.02, 0.010),
            (sgn * (env_x + wall + 0.014), y_back / 2.0, part_z),
            mats["housing"],
            f"parting_flange_{tag}",
        )
        # clamp bolts through the flange
        for j, fy in enumerate((y_back * 0.25, y_back * 0.75)):
            _cyl(
                housing,
                0.005,
                0.028,
                (sgn * (env_x + wall + 0.014), fy, part_z),
                mats["hardware"],
                f"flange_bolt_{tag}_{j}",
            )
    # top cap of the upper half
    _box(
        housing,
        (2.0 * env_x + 2.0 * wall + 0.02, y_back + 0.02, wall),
        (0.0, y_back / 2.0, top_z + wall / 2.0),
        mats["housing"],
        "split_top_cap",
    )


_HOUSING_SHELLS = {
    "open_pillow_block": _build_open_pillow_block,
    "enclosed_gearbox": _build_enclosed_gearbox,
    "split_housing": _build_split_housing,
}


def _build_housing(model: ArticulatedObject, r, mats) -> None:
    housing = model.part("housing", meta={"role": "fixed_reference_support"})
    worm_on_housing = r.backlash_adjustment == "eccentric_bearing"
    _build_bearing_skeleton(housing, r, mats, worm_on_housing=worm_on_housing)
    _HOUSING_SHELLS[r.housing_topology](housing, r, mats)
    if not worm_on_housing:
        _build_carriage_rail_guides(housing, r, mats)


# --------------------------------------------------------------------------- #
# Sliding worm carriage (backlash_adjustment == sliding_carriage) — S6 L200-L301
# --------------------------------------------------------------------------- #


def _yoke_y(r) -> float:
    """Y of the carriage yoke beam — behind the worm, clear of its rotating envelope."""
    return r.thread_outer + 0.020


def _carriage_rail_center(r) -> tuple[float, float, float]:
    """Where the carriage tongue meets the housing backing plate (behind the worm)."""
    cx, _, cz = r.worm_center
    return (cx, r.y_back - 0.010, cz)


def _build_carriage_rail_guides(housing, r, mats) -> None:
    """Housing-side backing plate the carriage tongue slides against (grandfathered rail).

    Travel is only ``carriage_travel`` (≤5mm), so the plate stays compact — no long
    channel that could reach the wheel bearings or the shell walls.
    """
    rx, ry, rz = _carriage_rail_center(r)
    md = r.mesh_dir
    size = (
        0.040 if md[0] != 0 else 0.030,
        0.014,
        0.040 if md[2] != 0 else 0.030,
    )
    _box(housing, size, (rx, ry, rz), mats["housing"], "rail_backing")


def _build_worm_carriage(model: ArticulatedObject, r, mats) -> None:
    carriage = model.part("worm_carriage", meta={"role": "backlash_slide"})
    col_rpy = _worm_collar_rpy(r)
    col_r = r.shaft_radius + 0.006
    yoke_y = _yoke_y(r)
    ax = r.worm_axis
    for i, (ex, ey, ez) in enumerate(_worm_end_points(r)):
        _cyl(carriage, col_r, 0.020, (ex, ey, ez), mats["steel"], f"worm_bearing_collar_{i}", col_rpy)
        _cyl(
            carriage, col_r * 1.35, 0.010, (ex, ey, ez), mats["hardware"], f"worm_bearing_cap_{i}", col_rpy
        )
        # arm from the collar (y≈0) back to the yoke
        _box(
            carriage,
            (col_r * 2.0, yoke_y, col_r * 2.0),
            (ex, yoke_y / 2.0, ez),
            mats["housing"],
            f"carriage_arm_{i}",
        )
    # yoke beam joining the two arms, spanning the worm length behind the worm
    span = r.shaft_length - 0.020
    yoke_size = (
        span if ax[0] != 0 else 0.018,
        0.016,
        span if ax[2] != 0 else 0.018,
    )
    cx, _, cz = r.worm_center
    _box(carriage, yoke_size, (cx, yoke_y, cz), mats["housing"], "carriage_yoke")
    # rail tongue reaching from the yoke back to the housing backing plate
    rx, ry, rz = _carriage_rail_center(r)
    md = r.mesh_dir
    tongue_size = (
        0.020 if md[0] != 0 else 0.016,
        ry - yoke_y + 0.008,
        0.020 if md[2] != 0 else 0.016,
    )
    _box(
        carriage,
        tongue_size,
        (rx, (yoke_y + ry) / 2.0, rz),
        mats["hardware"],
        "carriage_rail_tongue",
    )


# --------------------------------------------------------------------------- #
# Assembly
# --------------------------------------------------------------------------- #


def build_worm_gear_and_wheel_assembly(
    config: WormGearAndWheelAssemblyConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    cfg = config or WormGearAndWheelAssemblyConfig()
    r = resolve_config(cfg)
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={
            "category": "worm gear and wheel assembly",
            "gear_ratio": {
                "source": "housing_to_worm",
                "driven": "housing_to_wheel",
                "multiplier": -1.0 / WHEEL_TEETH,
            },
        },
    )
    mats = {
        key: model.material(f"wgw_{key}", rgba=r.palette[key])
        for key in ("brass", "steel", "dark", "housing", "hardware")
    }

    _build_housing(model, r, mats)
    housing = model.get_part("housing")
    _build_wheel(model, r, mats)
    _build_worm(model, r, mats)
    wheel = model.get_part("worm_wheel")
    worm = model.get_part("worm_shaft")

    sliding = r.backlash_adjustment == "sliding_carriage"
    if sliding:
        _build_worm_carriage(model, r, mats)
        carriage = model.get_part("worm_carriage")
        # PRISMATIC backlash slide along mesh_dir (worm retreats from the wheel).
        # Grandfathered rail: prismatic origin is gauge freedom, no MatingContract.
        model.articulation(
            "housing_to_carriage",
            ArticulationType.PRISMATIC,
            parent=housing,
            child=carriage,
            # Carriage visuals are authored in world coords; keep the link frame at
            # the world origin (prismatic origin is gauge freedom, exempt from the
            # origin-proximity check) so no double offset is applied.
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
            axis=r.mesh_dir,
            motion_limits=MotionLimits(
                effort=900.0, velocity=0.02, lower=0.0, upper=r.carriage_travel
            ),
            meta={"mechanism": "worm carriage backlash slide"},
        )
        worm_parent = carriage
        worm_joint_name = "carriage_to_worm"
    else:
        worm_parent = housing
        worm_joint_name = "housing_to_worm"

    # Worm spin joint (grandfathered pin-in-collar bearing — no MatingContract).
    worm_joint = model.articulation(
        worm_joint_name,
        ArticulationType.CONTINUOUS,
        parent=worm_parent,
        child=worm,
        origin=Origin(xyz=r.worm_center),
        axis=r.worm_axis,
        motion_limits=MotionLimits(effort=4.0, velocity=24.0),
        meta={"mechanism": "input worm spin"},
    )

    # wheel joint (mimics the worm through the gear ratio)
    model.articulation(
        "housing_to_wheel",
        ArticulationType.CONTINUOUS,
        parent=housing,
        child=wheel,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=6.0, velocity=4.0),
        mimic=Mimic(joint=worm_joint.name, multiplier=-1.0 / WHEEL_TEETH),
        mating=MatingContract(
            "wheel_bearing_collar",
            "negative_y",
            "axle_thrust_collar",
            "positive_y",
            contact_tol=0.0020,
        ),
        meta={"mechanism": "driven wheel spin", "gear_ratio_to_worm": -1.0 / WHEEL_TEETH},
    )

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_worm_gear_and_wheel_assembly(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_worm_gear_and_wheel_assembly(config_from_seed(seed), assets=assets)


# --------------------------------------------------------------------------- #
# Tests
# --------------------------------------------------------------------------- #


def _allow_bearing_overlaps(ctx: TestContext, r) -> None:
    worm_owner = "housing" if r.backlash_adjustment == "eccentric_bearing" else "worm_carriage"
    mount_elem = "worm_bearing_bracket" if r.backlash_adjustment == "eccentric_bearing" else "carriage_arm"
    for i in range(2):
        for elem_a in (f"worm_bearing_collar_{i}", f"worm_bearing_cap_{i}", f"{mount_elem}_{i}"):
            ctx.allow_overlap(
                worm_owner,
                "worm_shaft",
                elem_a=elem_a,
                elem_b="chamfered_shaft",
                reason="worm shaft end rides inside its bearing collar/cap (pin-through-sleeve)",
            )
    ctx.allow_overlap(
        "housing",
        "worm_wheel",
        elem_a="wheel_bearing_collar",
        elem_b="rear_axle_stub",
        reason="wheel axle stub passes through the housing bearing collar",
    )
    if r.backlash_adjustment == "sliding_carriage":
        ctx.allow_overlap(
            "housing",
            "worm_carriage",
            elem_a="rail_backing",
            elem_b="carriage_rail_tongue",
            reason="carriage tongue slides against the housing rail backing plate",
        )


def run_worm_gear_and_wheel_assembly_tests(
    object_model: ArticulatedObject, config: WormGearAndWheelAssemblyConfig
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    _allow_bearing_overlaps(ctx, r)

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)
    ctx.fail_if_joint_mating_has_gap()

    part_names = {p.name for p in object_model.parts}
    ctx.check("housing_present", "housing" in part_names, details=str(sorted(part_names)))
    ctx.check("worm_present", "worm_shaft" in part_names)
    ctx.check("wheel_present", "worm_wheel" in part_names)

    worm = object_model.get_part("worm_shaft")
    wheel = object_model.get_part("worm_wheel")
    worm_joint_name = (
        "housing_to_worm" if r.backlash_adjustment == "eccentric_bearing" else "carriage_to_worm"
    )
    worm_joint = object_model.get_articulation(worm_joint_name)
    wheel_joint = object_model.get_articulation("housing_to_wheel")

    ctx.check(
        "worm_continuous", worm_joint.articulation_type == ArticulationType.CONTINUOUS
    )
    ctx.check(
        "wheel_continuous", wheel_joint.articulation_type == ArticulationType.CONTINUOUS
    )
    ctx.check(
        "axes_perpendicular",
        tuple(round(v, 3) for v in worm_joint.axis) == r.worm_axis
        and tuple(round(v, 3) for v in wheel_joint.axis) == (0.0, 1.0, 0.0),
        details=f"worm={worm_joint.axis}, wheel={wheel_joint.axis}",
    )
    ctx.check(
        "wheel_mimics_worm",
        wheel_joint.mimic is not None and wheel_joint.mimic.joint == worm_joint.name,
    )
    ctx.check(
        "helical_thread_present",
        any(v.name.startswith("helical_thread_") for v in worm.visuals),
    )
    ctx.check(
        "worm_starts_ribbons",
        sum(1 for v in worm.visuals if v.name.startswith("helical_thread_")) == r.worm_starts,
        details=f"expected {r.worm_starts}",
    )
    ctx.check("wheel_has_teeth", any(v.name == "toothed_rim" for v in wheel.visuals))

    if r.backlash_adjustment == "sliding_carriage":
        carriage_joint = object_model.get_articulation("housing_to_carriage")
        ctx.check(
            "carriage_prismatic",
            carriage_joint.articulation_type == ArticulationType.PRISMATIC,
            details=str(carriage_joint.articulation_type),
        )

    # meshing footprint: thread crosses the wheel teeth laterally, tangent along mesh axis.
    ctx.expect_overlap(
        worm,
        wheel,
        axes=r.footprint_axes,
        elem_a="helical_thread_0",
        elem_b="toothed_rim",
        min_overlap=0.004,
        name="worm thread overlaps the wheel teeth in the meshing footprint",
    )
    ctx.expect_gap(
        worm,
        wheel,
        axis=r.mesh_axis,
        positive_elem="helical_thread_0",
        negative_elem="toothed_rim",
        min_gap=0.0,
        max_gap=0.006,
        name="worm thread is tangent to the wheel tooth tips",
    )

    # Rule 5: dynamic motion — spin the worm one full turn, wheel follows, mesh holds.
    with ctx.pose({worm_joint: math.pi * 2.0}):
        ctx.expect_overlap(
            worm,
            wheel,
            axes=r.footprint_axes,
            elem_a="helical_thread_0",
            elem_b="toothed_rim",
            min_overlap=0.002,
            name="meshing footprint remains when the worm spins",
        )
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=48, ignore_fixed=True)

    expected = dict(slot_choices_for_config(r))
    recorded = dict(object_model.meta.get("slot_choices", ()))
    ctx.check("slot_choices_recorded", recorded == expected, details=f"{recorded} vs {expected}")

    return ctx.report()


__all__ = [
    "WormGearAndWheelAssemblyConfig",
    "ResolvedWormGearAndWheelAssemblyConfig",
    "build_worm_gear_and_wheel_assembly",
    "build_seeded_worm_gear_and_wheel_assembly",
    "config_from_seed",
    "resolve_config",
    "run_worm_gear_and_wheel_assembly_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
]
