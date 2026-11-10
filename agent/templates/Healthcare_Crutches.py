# SPDX-License-Identifier: Apache-2.0

"""Walking cane — modular procedural template (slug ``Healthcare_Crutches``).

Identity: a WALKING CANE (single-point / tripod / quad base), NOT an underarm or
forearm crutch. The picture 小类 is named "Crutches" but every 5-star source is a
cane; see ``specs_modular_v1/Healthcare_Crutches.md``.

Slot graph (linear chain, ROOT = base):

    base --[FIXED: base_socket +z ↔ shaft_bottom -z]--> shaft
    shaft --[FIXED: shaft_top +z ↔ handle_socket -z]--> handle

Height mechanism lives INSIDE the shaft module so both cross-slot chain joints are
FIXED and the moving DOF is always the shaft's own joint:

    * telescoping_2piece: internal PRISMATIC (lower_shaft → upper_shaft), grandfathered
      captured tube-in-tube (no mating; element-scoped allow_overlap in tests).
    * folding_4section:   internal REVOLUTE fold_joint_{0..2} (seg_i → seg_{i+1}),
      mimic-coupled via ``coupled_chain`` so the sampled poses are exactly the
      physical (non-self-intersecting) folds.

Slots / candidates (all forked_anchor, real model.py sources — see spec):

    A base   : single_point_base | tripod_base | quad_small_base | quad_wide_base  (③ form family)
    C shaft  : telescoping_2piece | folding_4section  (② joint type; folding gated to single_point)
    B handle : t_derby_handle | crook_handle | offset_handle | fritz_handle  (③ grip planar boundary)

AUTHORING.md §A compliance:
    Rule 1 — height holes / collar lips / pivot bands are ``part.visual(...)`` on the
             part that moves with them, never FIXED greeble parts. Multi-foot feet ARE
             separate ``leg_{i}``/``foot_{i}`` parts (task-required copy logic + source-faithful).
    Rule 2 — every cross-slot joint carries a MatingContract (emitted by the assembler);
             fold joints carry an explicit MatingContract; the telescoping PRISMATIC is a
             captured sliding fit (grandfathered, per AUTHORING Rule 2).
    Rule 3 — LatheGeometry / superellipse_side_loft / tube_from_spline_points / LoftGeometry
             hero meshes kept from the sources; no downgrade to bare Box/Cylinder for the
             ferrule, grips, curved legs, or crook.
    Rule 4 — telescoping height holes are host-derived (sunk flush into the tube surface).
    Rule 5 — non-FIXED templates call fail_if_parts_overlap_in_sampled_poses(...) plus a
             targeted ctx.pose(...) per mechanism (handle rises / cane folds down).
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
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
    Box,
    Cylinder,
    Inertial,
    LatheGeometry,
    LoftGeometry,
    MatingContract,
    MotionLimits,
    Origin,
    Sphere,
    TestContext,
    TestReport,
    coupled_chain,
    mesh_from_geometry,
    rounded_rect_profile,
    superellipse_side_loft,
    tube_from_spline_points,
)

__modular__ = True


# --------------------------------------------------------------------------- #
# Enums + palette
# --------------------------------------------------------------------------- #

BaseForm = Literal["single_point", "tripod", "quad_small", "quad_wide"]
HandleType = Literal["t_derby", "crook", "offset", "fritz"]
ShaftType = Literal["telescoping", "folding"]
PaletteStyle = Literal[
    "anodized_black",
    "bronze_copper",
    "brushed_silver",
    "champagne_gold",
    "chrome_polished",
    "lacquered_wood",
]

BASE_FORMS: tuple[BaseForm, ...] = ("single_point", "tripod", "quad_small", "quad_wide")
HANDLE_TYPES: tuple[HandleType, ...] = ("t_derby", "crook", "offset", "fritz")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "anodized_black",
    "bronze_copper",
    "brushed_silver",
    "champagne_gold",
    "chrome_polished",
    "lacquered_wood",
)

# palette keys: shaft (main tube), shaft_dark (recesses/holes), collar (bright hardware),
# grip (handle), rubber (ferrule/feet), bright (reflection accent).
PALETTE_PRESETS: dict[str, dict[str, tuple[float, float, float, float]]] = {
    "anodized_black": {
        "shaft": (0.11, 0.11, 0.12, 1.0),
        "shaft_dark": (0.05, 0.05, 0.06, 1.0),
        "collar": (0.22, 0.22, 0.24, 1.0),
        "grip": (0.04, 0.04, 0.05, 1.0),
        "rubber": (0.012, 0.012, 0.014, 1.0),
        "bright": (0.38, 0.39, 0.41, 1.0),
    },
    "bronze_copper": {
        "shaft": (0.74, 0.42, 0.22, 1.0),
        "shaft_dark": (0.38, 0.19, 0.10, 1.0),
        "collar": (0.80, 0.62, 0.42, 1.0),
        "grip": (0.05, 0.05, 0.06, 1.0),
        "rubber": (0.010, 0.010, 0.012, 1.0),
        "bright": (0.86, 0.64, 0.42, 1.0),
    },
    "brushed_silver": {
        "shaft": (0.78, 0.80, 0.82, 1.0),
        "shaft_dark": (0.42, 0.44, 0.46, 1.0),
        "collar": (0.70, 0.72, 0.74, 1.0),
        "grip": (0.62, 0.52, 0.38, 1.0),
        "rubber": (0.02, 0.02, 0.02, 1.0),
        "bright": (0.93, 0.94, 0.96, 1.0),
    },
    "champagne_gold": {
        "shaft": (0.83, 0.78, 0.62, 1.0),
        "shaft_dark": (0.52, 0.48, 0.34, 1.0),
        "collar": (0.88, 0.84, 0.68, 1.0),
        "grip": (0.06, 0.06, 0.07, 1.0),
        "rubber": (0.012, 0.012, 0.014, 1.0),
        "bright": (0.95, 0.92, 0.78, 1.0),
    },
    "chrome_polished": {
        "shaft": (0.86, 0.88, 0.90, 1.0),
        "shaft_dark": (0.48, 0.50, 0.52, 1.0),
        "collar": (0.80, 0.82, 0.84, 1.0),
        "grip": (0.05, 0.05, 0.06, 1.0),
        "rubber": (0.012, 0.012, 0.014, 1.0),
        "bright": (0.97, 0.98, 1.0, 1.0),
    },
    "lacquered_wood": {
        "shaft": (0.42, 0.26, 0.14, 1.0),
        "shaft_dark": (0.26, 0.15, 0.07, 1.0),
        "collar": (0.72, 0.60, 0.40, 1.0),
        "grip": (0.55, 0.36, 0.20, 1.0),
        "rubber": (0.02, 0.02, 0.02, 1.0),
        "bright": (0.60, 0.42, 0.24, 1.0),
    },
}

# Shared height model (Contract 3c: single-sourced).
TARGET_TOP_BASE = 0.905     # nominal handle-top height at height_scale = 1.0 (m)
HANDLE_RISE = 0.055         # grip rise above the shaft top (m)
_BASE_TOP: dict[str, float] = {
    "single_point": 0.070,
    "tripod": 0.125,
    "quad_small": 0.060,
    "quad_wide": 0.115,
}
_FOOT_COUNT: dict[str, int] = {
    "single_point": 1,
    "tripod": 3,
    "quad_small": 4,
    "quad_wide": 4,
}
_BASE_MODULE: dict[str, str] = {
    "single_point": "single_point_base",
    "tripod": "tripod_base",
    "quad_small": "quad_small_base",
    "quad_wide": "quad_wide_base",
}
_HANDLE_MODULE: dict[str, str] = {
    "t_derby": "t_derby_handle",
    "crook": "crook_handle",
    "offset": "offset_handle",
    "fritz": "fritz_handle",
}
_SHAFT_MODULE: dict[str, str] = {
    "telescoping": "telescoping_2piece",
    "folding": "folding_4section",
}


# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class WalkingCaneConfig:
    base_form: BaseForm = "single_point"
    handle_type: HandleType = "t_derby"
    shaft_type: ShaftType = "telescoping"
    palette_style: PaletteStyle = "anodized_black"
    height_scale: float = 1.0
    shaft_radius_scale: float = 1.0
    base_span_scale: float = 1.0
    telescope_travel: float = 0.11


@dataclass(frozen=True)
class ResolvedWalkingCaneConfig:
    base_form: BaseForm
    handle_type: HandleType
    shaft_type: ShaftType
    palette_style: PaletteStyle
    height_scale: float
    shaft_radius_scale: float
    base_span_scale: float
    telescope_travel: float
    # module names
    base_module: str
    shaft_module: str
    handle_module: str
    # derived geometry (single-sourced)
    base_top: float
    shaft_rise: float
    lower_tube_len: float
    seg_len: float
    foot_count: int
    palette: dict[str, tuple[float, float, float, float]]


def config_from_seed(seed: int) -> WalkingCaneConfig:
    """Deterministic procedural sampling for every seed (seed 0 not special)."""
    rng = random.Random(seed)

    base_form: BaseForm = rng.choice(BASE_FORMS)
    # Compatibility gate: real folding canes are single-point; multi-foot bases
    # do not fold. Telescoping is available for all base forms.
    if base_form == "single_point":
        shaft_type: ShaftType = rng.choice(("telescoping", "folding"))
    else:
        shaft_type = "telescoping"

    handle_type: HandleType = rng.choice(HANDLE_TYPES)
    palette_style: PaletteStyle = rng.choice(PALETTE_STYLES)

    height_scale = rng.uniform(0.96, 1.05)
    shaft_radius_scale = rng.uniform(0.90, 1.15)
    base_span_scale = rng.uniform(0.85, 1.15)
    telescope_travel = rng.uniform(0.08, 0.14)

    return WalkingCaneConfig(
        base_form=base_form,
        handle_type=handle_type,
        shaft_type=shaft_type,
        palette_style=palette_style,
        height_scale=round(height_scale, 4),
        shaft_radius_scale=round(shaft_radius_scale, 4),
        base_span_scale=round(base_span_scale, 4),
        telescope_travel=round(telescope_travel, 4),
    )


def resolve_config(config: WalkingCaneConfig) -> ResolvedWalkingCaneConfig:
    base_form = str(config.base_form)
    if base_form not in _BASE_TOP:
        raise ValueError(f"Unsupported base_form: {config.base_form}")
    handle_type = str(config.handle_type)
    if handle_type not in _HANDLE_MODULE:
        raise ValueError(f"Unsupported handle_type: {config.handle_type}")
    shaft_type = str(config.shaft_type)
    if shaft_type not in _SHAFT_MODULE:
        raise ValueError(f"Unsupported shaft_type: {config.shaft_type}")
    palette_style = str(config.palette_style)
    if palette_style not in PALETTE_PRESETS:
        raise ValueError(f"Unsupported palette_style: {config.palette_style}")

    # Gate: folding only legal on single_point (degrade illegal combos to telescoping).
    if shaft_type == "folding" and base_form != "single_point":
        shaft_type = "telescoping"

    height_scale = max(0.90, min(float(config.height_scale), 1.10))
    shaft_radius_scale = max(0.85, min(float(config.shaft_radius_scale), 1.20))
    base_span_scale = max(0.80, min(float(config.base_span_scale), 1.20))

    base_top = _BASE_TOP[base_form]
    shaft_rise = max(0.60, TARGET_TOP_BASE * height_scale - base_top - HANDLE_RISE)
    lower_tube_len = shaft_rise * 0.60
    seg_len = shaft_rise / 4.0

    telescope_travel = max(0.06, min(float(config.telescope_travel), 0.5 * lower_tube_len))

    return ResolvedWalkingCaneConfig(
        base_form=base_form,  # type: ignore[arg-type]
        handle_type=handle_type,  # type: ignore[arg-type]
        shaft_type=shaft_type,  # type: ignore[arg-type]
        palette_style=palette_style,  # type: ignore[arg-type]
        height_scale=height_scale,
        shaft_radius_scale=shaft_radius_scale,
        base_span_scale=base_span_scale,
        telescope_travel=telescope_travel,
        base_module=_BASE_MODULE[base_form],
        shaft_module=_SHAFT_MODULE[shaft_type],
        handle_module=_HANDLE_MODULE[handle_type],
        base_top=base_top,
        shaft_rise=shaft_rise,
        lower_tube_len=lower_tube_len,
        seg_len=seg_len,
        foot_count=_FOOT_COUNT[base_form],
        palette=dict(PALETTE_PRESETS[palette_style]),
    )


# --------------------------------------------------------------------------- #
# Geometry helpers (ported from the 5-star sources; primitive types preserved)
# --------------------------------------------------------------------------- #


def _ferrule_mesh(name: str = "ferrule"):
    """Flared rubber ferrule (LatheGeometry) — S1 L51-68."""
    ferrule = LatheGeometry(
        [
            (0.000, 0.000),
            (0.022, 0.000),
            (0.026, 0.006),
            (0.024, 0.014),
            (0.018, 0.026),
            (0.016, 0.050),
            (0.010, 0.056),
            (0.000, 0.056),
        ],
        segments=40,
        closed=True,
    )
    return mesh_from_geometry(ferrule, name)


def _hollow_tube_mesh(outer_radius: float, inner_radius: float, z_min: float, z_max: float, name: str):
    """Revolved thin-wall tube with real central clearance — S1 L31-48."""
    shell = LatheGeometry.from_shell_profiles(
        [(outer_radius, z_min), (outer_radius, z_max)],
        [(inner_radius, z_min), (inner_radius, z_max)],
        segments=40,
        start_cap="flat",
        end_cap="flat",
        lip_samples=4,
    )
    return mesh_from_geometry(shell, name)


def _t_derby_grip_mesh(name: str = "grip"):
    """Ergonomic T/derby grip — superellipse_side_loft, S1 L71-90."""
    grip = superellipse_side_loft(
        [
            (-0.083, 0.000, 0.034, 0.042),
            (-0.052, -0.001, 0.038, 0.048),
            (-0.020, -0.004, 0.043, 0.052),
            (0.000, -0.005, 0.045, 0.054),
            (0.020, -0.004, 0.043, 0.052),
            (0.052, -0.001, 0.038, 0.048),
            (0.083, 0.000, 0.034, 0.042),
        ],
        exponents=3.0,
        segments=44,
        cap=True,
        closed=True,
    )
    grip.rotate_z(-math.pi / 2.0)
    return mesh_from_geometry(grip, name)


def _crook_mesh(name: str = "crook"):
    """Shepherd's-crook handle: swept curved tube — V1 L71-107."""
    R = 0.038
    z_rise = 0.025
    cx, cz = R, z_rise
    points = [(0.0, 0.0, 0.000), (0.0, 0.0, 0.010), (0.0, 0.0, z_rise)]
    sweep_start = math.pi
    sweep_end = -math.radians(25)
    n_arc = 24
    for i in range(1, n_arc + 1):
        t = i / n_arc
        angle = sweep_start + t * (sweep_end - sweep_start)
        x = cx + R * math.cos(angle)
        z = cz + R * math.sin(angle)
        points.append((x, 0.0, z))
    tube = tube_from_spline_points(
        points,
        radius=0.012,
        samples_per_segment=6,
        radial_segments=18,
        cap_ends=True,
        up_hint=(0.0, 1.0, 0.0),
    )
    return mesh_from_geometry(tube, name)


def _swan_neck_mesh(name: str = "swan_neck"):
    """S-curved offset neck — V2 L72-89."""
    neck = tube_from_spline_points(
        [
            (0.000, 0.000, 0.012),
            (0.000, 0.000, 0.032),
            (0.008, 0.000, 0.048),
            (0.022, 0.000, 0.058),
            (0.036, 0.000, 0.063),
            (0.044, 0.000, 0.064),
        ],
        radius=0.0110,
        samples_per_segment=16,
        radial_segments=18,
        cap_ends=True,
    )
    return mesh_from_geometry(neck, name)


def _offset_grip_mesh(name: str = "grip"):
    """Contoured foam grip for the offset handle — V2 L92-111 (spans local X)."""
    grip = superellipse_side_loft(
        [
            (-0.054, 0.000, 0.030, 0.034),
            (-0.034, -0.001, 0.033, 0.040),
            (-0.012, -0.003, 0.035, 0.044),
            (0.000, -0.004, 0.036, 0.046),
            (0.012, -0.003, 0.035, 0.044),
            (0.034, -0.001, 0.033, 0.040),
            (0.054, 0.000, 0.030, 0.034),
        ],
        exponents=3.0,
        segments=44,
        cap=True,
        closed=True,
    )
    return mesh_from_geometry(grip, name)


def _fritz_grip_mesh(name: str = "grip"):
    """Anatomical Fritz palm grip: forward-elongated superellipse (spans local X,
    no rotate → extends front-to-back), adapted from V3's front-to-back palm form."""
    grip = superellipse_side_loft(
        [
            (-0.030, 0.000, 0.021, 0.017),
            (-0.008, -0.002, 0.024, 0.020),
            (0.016, -0.003, 0.024, 0.020),
            (0.044, -0.002, 0.022, 0.017),
            (0.072, 0.000, 0.015, 0.013),
        ],
        exponents=3.2,
        segments=44,
        cap=True,
        closed=True,
    )
    return mesh_from_geometry(grip, name)


def _rounded_plate_mesh(x_size: float, y_size: float, thickness: float, name: str):
    """Rounded rectangular base plate (LoftGeometry) — S3 plate, mesh not Box."""
    radius = min(x_size, y_size) * 0.14

    def section(z: float):
        return [(px, py, z) for px, py in rounded_rect_profile(x_size, y_size, radius=radius)]

    geom = LoftGeometry([section(-thickness / 2.0), section(thickness / 2.0)], cap=True, closed=True)
    return mesh_from_geometry(geom, name)


def _cyl_between(start: tuple[float, float, float], end: tuple[float, float, float]) -> tuple[float, Origin]:
    """(length, Origin) for a Cylinder spanning start→end — S2 L34-43."""
    vx, vy, vz = end[0] - start[0], end[1] - start[1], end[2] - start[2]
    length = math.sqrt(vx * vx + vy * vy + vz * vz)
    yaw = math.atan2(vy, vx)
    pitch = math.acos(max(-1.0, min(1.0, vz / length))) if length > 1e-9 else 0.0
    mid = ((start[0] + end[0]) * 0.5, (start[1] + end[1]) * 0.5, (start[2] + end[2]) * 0.5)
    return length, Origin(xyz=mid, rpy=(0.0, pitch, yaw))


def _box_inertial(part, size: tuple[float, float, float], mass: float, z_center: float) -> None:
    part.inertial = Inertial.from_geometry(
        Box(size), mass=mass, origin=Origin(xyz=(0.0, 0.0, z_center))
    )


# --------------------------------------------------------------------------- #
# Slot A — base modules (ROOT). downstream face = "base_socket" (+z).
# --------------------------------------------------------------------------- #


def _base_downstream(base_top: float) -> InterfaceSpec:
    return InterfaceSpec(
        interface_name="base_top",
        part_name="base",
        visual_name="base_socket",
        face_side="positive_z",
        anchor_local=(0.0, 0.0, base_top),
        face_extents_uv=(0.0, 0.0),
        contact_tol=0.0025,
    )


def _emit_base_socket(base, base_top: float, radius: float) -> None:
    """Short metal socket collar at the base top where the shaft seats."""
    base.visual(
        Cylinder(radius=radius, length=0.030),
        origin=Origin(xyz=(0.0, 0.0, base_top - 0.015)),
        material="collar",
        name="base_socket", material_class_id="metal.chrome_polished",
    )


def _build_single_point_base(ctx: ModuleBuildContext) -> ModuleBuild:
    r: ResolvedWalkingCaneConfig = ctx.config
    base = ctx.model.part("base")
    base.visual(_ferrule_mesh("ferrule"), material="rubber", name="ferrule", material_class_id="rubber.smooth_plain")
    _emit_base_socket(base, r.base_top, radius=0.015)
    _box_inertial(base, (0.05, 0.05, r.base_top), 0.10, r.base_top * 0.5)
    return ModuleBuild(
        module_name="single_point_base",
        parts_emitted=["base"],
        interfaces={"downstream": _base_downstream(r.base_top)},
    )


def _build_tripod_base(ctx: ModuleBuildContext) -> ModuleBuild:
    r: ResolvedWalkingCaneConfig = ctx.config
    span = r.base_span_scale
    base = ctx.model.part("base")
    hub_z0, hub_z1 = 0.070, 0.100
    hub_radius = 0.026
    base.visual(
        Cylinder(radius=hub_radius, length=hub_z1 - hub_z0),
        origin=Origin(xyz=(0.0, 0.0, (hub_z0 + hub_z1) / 2.0)),
        material="collar",
        name="hub_body", material_class_id="metal.chrome_polished",
    )
    base.visual(
        Sphere(radius=hub_radius),
        origin=Origin(xyz=(0.0, 0.0, hub_z0 + 0.012)),
        material="collar",
        name="hub_dome", material_class_id="metal.chrome_polished",
    )
    _emit_base_socket(base, r.base_top, radius=0.015)
    _box_inertial(base, (0.06, 0.06, r.base_top), 0.30, r.base_top * 0.5)

    foot_radius = 0.115 * span
    attach_z = 0.088
    parts = ["base"]
    joints = []
    ferrule = _ferrule_mesh("leg_ferrule")
    for i in range(3):
        angle = math.pi / 2.0 + i * 2.0 * math.pi / 3.0
        cx, cy = math.cos(angle), math.sin(angle)
        attach = (hub_radius * cx, hub_radius * cy, attach_z)
        foot = (foot_radius * cx, foot_radius * cy, 0.032)
        end_local = (foot[0] - attach[0], foot[1] - attach[1], foot[2] - attach[2])
        leg = ctx.model.part(f"leg_{i}")
        length, tube_origin = _cyl_between((0.0, 0.0, 0.0), end_local)
        leg.visual(Cylinder(radius=0.0058, length=length), origin=tube_origin, material="shaft", name="leg_tube", material_class_id="metal.aluminum_bare")
        leg.visual(
            ferrule,
            origin=Origin(xyz=(end_local[0], end_local[1], end_local[2] - 0.016)),
            material="rubber",
            name="leg_ferrule", material_class_id="rubber.smooth_plain",
        )
        _box_inertial(leg, (0.02, 0.02, foot_radius), 0.05, end_local[2] * 0.5)
        ctx.model.articulation(
            f"base_to_leg_{i}",
            ArticulationType.FIXED,
            parent=base,
            child=leg,
            origin=Origin(xyz=attach),
        )
        parts.append(f"leg_{i}")
        joints.append(f"base_to_leg_{i}")
    return ModuleBuild(
        module_name="tripod_base",
        parts_emitted=parts,
        internal_articulations=joints,
        interfaces={"downstream": _base_downstream(r.base_top)},
    )


def _build_quad_small_base(ctx: ModuleBuildContext) -> ModuleBuild:
    r: ResolvedWalkingCaneConfig = ctx.config
    span = r.base_span_scale
    base = ctx.model.part("base")
    plate_x, plate_y = 0.180 * span, 0.120 * span
    plate_thickness = 0.010
    foot_height = 0.025
    plate_center_z = foot_height + plate_thickness / 2.0
    base.visual(
        _rounded_plate_mesh(plate_x, plate_y, plate_thickness, "plate_body"),
        origin=Origin(xyz=(0.0, 0.0, plate_center_z)),
        material="shaft_dark",
        name="plate_body", material_class_id="metal.blackened_gunmetal",
    )
    _emit_base_socket(base, r.base_top, radius=0.016)
    _box_inertial(base, (plate_x, plate_y, r.base_top), 0.35, r.base_top * 0.5)

    fx, fy = 0.070 * span, 0.045 * span
    parts = ["base"]
    joints = []
    for i, (sx, sy) in enumerate(((-1, -1), (1, -1), (-1, 1), (1, 1))):
        foot = ctx.model.part(f"foot_{i}")
        foot.visual(
            Cylinder(radius=0.012, length=0.016),
            origin=Origin(xyz=(0.0, 0.0, -0.007)),
            material="rubber",
            name="foot_plug", material_class_id="rubber.smooth_plain",
        )
        foot.visual(
            Cylinder(radius=0.019, length=0.014),
            origin=Origin(xyz=(0.0, 0.0, -0.018)),
            material="rubber",
            name="foot_pad", material_class_id="rubber.smooth_plain",
        )
        _box_inertial(foot, (0.03, 0.03, 0.03), 0.03, -0.015)
        ctx.model.articulation(
            f"base_to_foot_{i}",
            ArticulationType.FIXED,
            parent=base,
            child=foot,
            origin=Origin(xyz=(sx * fx, sy * fy, foot_height + 0.001)),
        )
        parts.append(f"foot_{i}")
        joints.append(f"base_to_foot_{i}")
    return ModuleBuild(
        module_name="quad_small_base",
        parts_emitted=parts,
        internal_articulations=joints,
        interfaces={"downstream": _base_downstream(r.base_top)},
    )


def _build_quad_wide_base(ctx: ModuleBuildContext) -> ModuleBuild:
    r: ResolvedWalkingCaneConfig = ctx.config
    span = r.base_span_scale
    base = ctx.model.part("base")
    hub_z0, hub_z1 = 0.070, 0.090
    hub_radius = 0.040
    base.visual(
        Cylinder(radius=hub_radius, length=hub_z1 - hub_z0),
        origin=Origin(xyz=(0.0, 0.0, (hub_z0 + hub_z1) / 2.0)),
        material="collar",
        name="hub_body", material_class_id="metal.chrome_polished",
    )
    _emit_base_socket(base, r.base_top, radius=0.016)
    _box_inertial(base, (0.16, 0.12, r.base_top), 0.40, r.base_top * 0.5)

    # Wide splayed 4-leg base offset to one side (S4 tip layout).
    tips = [
        (0.085 * span, 0.083 * span),
        (0.085 * span, -0.083 * span),
        (-0.135 * span, 0.083 * span),
        (-0.135 * span, -0.083 * span),
    ]
    attach_z = 0.078
    parts = ["base"]
    joints = []
    ferrule = _ferrule_mesh("leg_ferrule")
    for i, (tx, ty) in enumerate(tips):
        leg = ctx.model.part(f"leg_{i}")
        span_r = math.hypot(tx, ty)
        sx = tx / span_r * hub_radius
        sy = ty / span_r * hub_radius
        mid_x = (sx + tx) * 0.52
        mid_y = (sy + ty) * 0.52
        # local frame: attach at (0,0,0) on the hub perimeter, foot at tip.
        pts = [
            (sx - sx, sy - sy, 0.000),
            (mid_x - sx, mid_y - sy, -0.026),
            (tx - sx, ty - sy, -attach_z + 0.020),
        ]
        leg_tube = tube_from_spline_points(
            pts, radius=0.006, samples_per_segment=14, radial_segments=16, cap_ends=True
        )
        leg.visual(mesh_from_geometry(leg_tube, f"leg_{i}_tube"), material="shaft", name="leg_tube", material_class_id="metal.aluminum_bare")
        leg.visual(
            ferrule,
            origin=Origin(xyz=(tx - sx, ty - sy, -attach_z + 0.004)),
            material="rubber",
            name="leg_ferrule", material_class_id="rubber.smooth_plain",
        )
        _box_inertial(leg, (0.04, 0.04, attach_z), 0.06, -attach_z * 0.4)
        ctx.model.articulation(
            f"base_to_leg_{i}",
            ArticulationType.FIXED,
            parent=base,
            child=leg,
            origin=Origin(xyz=(sx, sy, attach_z)),
        )
        parts.append(f"leg_{i}")
        joints.append(f"base_to_leg_{i}")
    return ModuleBuild(
        module_name="quad_wide_base",
        parts_emitted=parts,
        internal_articulations=joints,
        interfaces={"downstream": _base_downstream(r.base_top)},
    )


# --------------------------------------------------------------------------- #
# Slot C — shaft modules. upstream face = tube bottom (-z); downstream = tube top (+z).
# --------------------------------------------------------------------------- #


def _build_telescoping(ctx: ModuleBuildContext) -> ModuleBuild:
    r: ResolvedWalkingCaneConfig = ctx.config
    srs = r.shaft_radius_scale
    rise = r.shaft_rise
    L_lower = r.lower_tube_len
    travel = r.telescope_travel

    inner_r = 0.0085 * srs
    r_out = 0.0120 * srs
    # Lower-tube bore hugs the inner sliding tube so the two shaft parts stay in
    # contact (connectivity): a 0.2mm sliding-fit overlap along the nested span,
    # allow-listed in run_tests. Without this the inner tube floats in the bore.
    r_in = inner_r - 0.0002

    lower = ctx.model.part("lower_shaft")
    lower.visual(
        _hollow_tube_mesh(r_out, r_in, 0.0, L_lower, "lower_tube"),
        material="shaft",
        name="lower_tube", material_class_id="metal.aluminum_bare",
    )
    # Collar ring at the top of the lower tube. Bore embeds onto the tube outer
    # wall (touches lower_tube for intra-part connectivity) while still clearing
    # the thinner inner sliding tube.
    collar_r_out = 0.017 * srs
    collar_r_in = r_out - 0.0010
    lower.visual(
        _hollow_tube_mesh(collar_r_out, collar_r_in, L_lower - 0.050, L_lower + 0.006, "collar_shell"),
        material="collar",
        name="collar_shell", material_class_id="metal.chrome_polished",
    )
    lower.visual(
        _hollow_tube_mesh(collar_r_out + 0.001, collar_r_in, L_lower - 0.050, L_lower - 0.044, "collar_lip"),
        material="shaft_dark",
        name="collar_lip", material_class_id="metal.blackened_gunmetal",
    )
    # Host-conformal flush height-adjustment holes (Rule 4) sunk into the tube.
    for i in range(5):
        z = L_lower * 0.45 + i * 0.035
        lower.visual(
            Cylinder(radius=0.0035, length=0.0016),
            origin=Origin(xyz=(r_out - 0.0008, 0.0, z), rpy=(0.0, math.pi / 2.0, 0.0)),
            material="shaft_dark",
            name=f"height_hole_{i}", material_class_id="metal.blackened_gunmetal",
        )
    _box_inertial(lower, (0.05, 0.05, L_lower), 0.30, L_lower * 0.5)

    # Upper sliding member.
    z_ph = L_lower - 0.02          # prismatic home origin (parent frame)
    z_lo = -0.20                   # inner-tube bottom in upper frame (rest insertion 0.22)
    z_hi = rise - z_ph             # inner-tube top → handle mount at world `rise`
    upper = ctx.model.part("upper_shaft")
    upper.visual(
        Cylinder(radius=inner_r, length=z_hi - z_lo),
        origin=Origin(xyz=(0.0, 0.0, (z_hi + z_lo) / 2.0)),
        material="bright",
        name="inner_tube", material_class_id="metal.chrome_polished",
    )
    upper.visual(
        Cylinder(radius=0.010 * srs, length=0.012),
        origin=Origin(xyz=(0.0, 0.0, z_hi - 0.006)),
        material="collar",
        name="top_ferrule", material_class_id="metal.chrome_polished",
    )
    _box_inertial(upper, (0.03, 0.03, z_hi - z_lo), 0.20, (z_hi + z_lo) / 2.0)

    ctx.model.articulation(
        "telescope_slide",
        ArticulationType.PRISMATIC,
        parent=lower,
        child=upper,
        origin=Origin(xyz=(0.0, 0.0, z_ph)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=60.0, velocity=0.15, lower=0.0, upper=travel),
        # Grandfathered: captured tube-in-tube sliding fit (no axis-aligned mating face).
    )

    upstream = InterfaceSpec(
        interface_name="shaft_bottom",
        part_name="lower_shaft",
        visual_name="lower_tube",
        face_side="negative_z",
        anchor_local=(0.0, 0.0, 0.0),
        consumer_joint_type=ArticulationType.FIXED,
    )
    downstream = InterfaceSpec(
        interface_name="shaft_top",
        part_name="upper_shaft",
        visual_name="top_ferrule",
        face_side="positive_z",
        anchor_local=(0.0, 0.0, z_hi),
        contact_tol=0.0025,
    )
    return ModuleBuild(
        module_name="telescoping_2piece",
        parts_emitted=["lower_shaft", "upper_shaft"],
        internal_articulations=["telescope_slide"],
        interfaces={"upstream": upstream, "downstream": downstream},
    )


def _build_folding(ctx: ModuleBuildContext) -> ModuleBuild:
    r: ResolvedWalkingCaneConfig = ctx.config
    srs = r.shaft_radius_scale
    seg_len = r.seg_len
    r_out = 0.0110 * srs
    r_in = 0.0090 * srs

    parts = []
    joints = []
    seg_parts = []
    for i in range(4):
        seg = ctx.model.part(f"shaft_seg_{i}")
        seg.visual(_hollow_tube_mesh(r_out, r_in, 0.0, seg_len, f"tube_{i}"), material="shaft", name=f"tube_{i}", material_class_id="metal.aluminum_bare")
        if i < 3:
            band_h = 0.010
            seg.visual(
                Cylinder(radius=r_out + 0.002, length=band_h),
                origin=Origin(xyz=(0.0, 0.0, seg_len - band_h / 2.0 - 0.004)),
                material="shaft_dark",
                name=f"pivot_band_{i}", material_class_id="metal.blackened_gunmetal",
            )
        _box_inertial(seg, (0.03, 0.03, seg_len), 0.08, seg_len * 0.5)
        parts.append(f"shaft_seg_{i}")
        seg_parts.append(seg)

    for i in range(3):
        ctx.model.articulation(
            f"fold_joint_{i}",
            ArticulationType.REVOLUTE,
            parent=seg_parts[i],
            child=seg_parts[i + 1],
            origin=Origin(xyz=(0.0, 0.0, seg_len)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=8.0, velocity=2.0, lower=0.0, upper=math.pi),
            mating=MatingContract(
                parent_face_geometry=f"tube_{i}",
                parent_face_side="positive_z",
                child_face_geometry=f"tube_{i + 1}",
                child_face_side="negative_z",
                contact_tol=0.0030,
            ),
        )
        joints.append(f"fold_joint_{i}")

    upstream = InterfaceSpec(
        interface_name="shaft_bottom",
        part_name="shaft_seg_0",
        visual_name="tube_0",
        face_side="negative_z",
        anchor_local=(0.0, 0.0, 0.0),
        consumer_joint_type=ArticulationType.FIXED,
    )
    downstream = InterfaceSpec(
        interface_name="shaft_top",
        part_name="shaft_seg_3",
        visual_name="tube_3",
        face_side="positive_z",
        anchor_local=(0.0, 0.0, seg_len),
        contact_tol=0.0030,
    )
    return ModuleBuild(
        module_name="folding_4section",
        parts_emitted=parts,
        internal_articulations=joints,
        interfaces={"upstream": upstream, "downstream": downstream},
    )


# --------------------------------------------------------------------------- #
# Slot B — handle modules. upstream face = "socket_flare" (-z, at part origin).
# --------------------------------------------------------------------------- #


def _handle_upstream() -> InterfaceSpec:
    return InterfaceSpec(
        interface_name="handle_socket",
        part_name="handle",
        visual_name="socket_flare",
        face_side="negative_z",
        anchor_local=(0.0, 0.0, 0.0),
        consumer_joint_type=ArticulationType.FIXED,
        contact_tol=0.0030,
    )


def _emit_socket_flare(handle, radius: float = 0.018) -> None:
    handle.visual(
        Cylinder(radius=radius, length=0.012),
        origin=Origin(xyz=(0.0, 0.0, 0.006)),
        material="grip",
        name="socket_flare", material_class_id="plastic.opaque_glossy_molded",
    )


def _build_t_derby_handle(ctx: ModuleBuildContext) -> ModuleBuild:
    handle = ctx.model.part("handle")
    _emit_socket_flare(handle, radius=0.020)
    handle.visual(
        Cylinder(radius=0.016, length=0.048),
        origin=Origin(xyz=(0.0, 0.0, 0.028)),
        material="grip",
        name="neck", material_class_id="plastic.opaque_glossy_molded",
    )
    handle.visual(_t_derby_grip_mesh("grip"), origin=Origin(xyz=(0.0, 0.0, 0.052)), material="grip", name="grip", material_class_id="plastic.opaque_glossy_molded")
    _box_inertial(handle, (0.06, 0.18, 0.07), 0.18, 0.04)
    return ModuleBuild(module_name="t_derby_handle", parts_emitted=["handle"], interfaces={"upstream": _handle_upstream()})


def _build_crook_handle(ctx: ModuleBuildContext) -> ModuleBuild:
    handle = ctx.model.part("handle")
    _emit_socket_flare(handle, radius=0.016)
    handle.visual(_crook_mesh("grip"), origin=Origin(xyz=(0.0, 0.0, 0.008)), material="grip", name="grip", material_class_id="plastic.opaque_glossy_molded")
    _box_inertial(handle, (0.10, 0.04, 0.10), 0.14, 0.05)
    return ModuleBuild(module_name="crook_handle", parts_emitted=["handle"], interfaces={"upstream": _handle_upstream()})


def _build_offset_handle(ctx: ModuleBuildContext) -> ModuleBuild:
    handle = ctx.model.part("handle")
    _emit_socket_flare(handle, radius=0.019)
    # swan_neck mesh already starts at local z=0.012 (= socket top); no extra z offset.
    handle.visual(_swan_neck_mesh("swan_neck"), origin=Origin(xyz=(0.0, 0.0, 0.0)), material="grip", name="swan_neck", material_class_id="plastic.opaque_glossy_molded")
    handle.visual(_offset_grip_mesh("grip"), origin=Origin(xyz=(0.044, 0.0, 0.064)), material="grip", name="grip", material_class_id="plastic.opaque_glossy_molded")
    _box_inertial(handle, (0.12, 0.11, 0.10), 0.19, 0.05)
    return ModuleBuild(module_name="offset_handle", parts_emitted=["handle"], interfaces={"upstream": _handle_upstream()})


def _build_fritz_handle(ctx: ModuleBuildContext) -> ModuleBuild:
    handle = ctx.model.part("handle")
    _emit_socket_flare(handle, radius=0.017)
    handle.visual(
        Cylinder(radius=0.012, length=0.034),
        origin=Origin(xyz=(0.0, 0.0, 0.020)),
        material="grip",
        name="neck", material_class_id="plastic.opaque_glossy_molded",
    )
    handle.visual(_fritz_grip_mesh("grip"), origin=Origin(xyz=(0.0, 0.0, 0.032)), material="grip", name="grip", material_class_id="plastic.opaque_glossy_molded")
    _box_inertial(handle, (0.11, 0.05, 0.06), 0.16, 0.04)
    return ModuleBuild(module_name="fritz_handle", parts_emitted=["handle"], interfaces={"upstream": _handle_upstream()})


# --------------------------------------------------------------------------- #
# Assembly
# --------------------------------------------------------------------------- #

_BASE_FACTORIES = {
    "single_point_base": _build_single_point_base,
    "tripod_base": _build_tripod_base,
    "quad_small_base": _build_quad_small_base,
    "quad_wide_base": _build_quad_wide_base,
}
_SHAFT_FACTORIES = {
    "telescoping_2piece": _build_telescoping,
    "folding_4section": _build_folding,
}
_HANDLE_FACTORIES = {
    "t_derby_handle": _build_t_derby_handle,
    "crook_handle": _build_crook_handle,
    "offset_handle": _build_offset_handle,
    "fritz_handle": _build_fritz_handle,
}


def _slots_for_config(r: ResolvedWalkingCaneConfig) -> list[SlotSpec]:
    return [
        SlotSpec("base", {r.base_module: _BASE_FACTORIES[r.base_module]}, anchor_choice=r.base_module),
        SlotSpec("shaft", {r.shaft_module: _SHAFT_FACTORIES[r.shaft_module]}, anchor_choice=r.shaft_module),
        SlotSpec("handle", {r.handle_module: _HANDLE_FACTORIES[r.handle_module]}, anchor_choice=r.handle_module),
    ]


def build_walking_cane(config: WalkingCaneConfig, *, assets: AssetContext | None = None) -> ArticulatedObject:
    r = resolve_config(config)
    palette = r.palette
    model = ArticulatedObject(name="walking_cane", assets=assets)
    for material_name, rgba in palette.items():
        model.material(material_name, rgba=rgba)

    assemble(
        model,
        slots=_slots_for_config(r),
        rng=random.Random(0),
        palette=palette,
        config=r,
        seed=0,
        selection_mode="procedural",
    )

    # Folding: couple the fold chain to one driver so sampled poses are the
    # physical (non-self-intersecting) folds. Run AFTER assembly so the solver
    # sees the whole model (base, handle) when clamping the driver's range.
    if r.shaft_type == "folding":
        coupled_chain(
            model,
            driver="fold_joint_0",
            followers=["fold_joint_1", "fold_joint_2"],
            allowed_pairs=[
                ("shaft_seg_0", "shaft_seg_1"),
                ("shaft_seg_1", "shaft_seg_2"),
                ("shaft_seg_2", "shaft_seg_3"),
            ],
        )
    return model


def build_seeded_walking_cane(seed: int) -> ArticulatedObject:
    return build_walking_cane(config_from_seed(seed))


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    r = resolve_config(config_from_seed(seed))
    return [("base", r.base_module), ("shaft", r.shaft_module), ("handle", r.handle_module)]


# --------------------------------------------------------------------------- #
# Tests
# --------------------------------------------------------------------------- #


def _part_names(model: ArticulatedObject) -> set[str]:
    return {p.name for p in model.parts}


def _allow_structural_overlaps(ctx: TestContext, model: ArticulatedObject, r: ResolvedWalkingCaneConfig) -> None:
    names = _part_names(model)
    base = model.get_part("base")
    # Leg/foot roots socket into the base hub/plate (radial contact isn't modeled
    # by MatingContract) — scope the overlap to those elements.
    if r.base_form in ("tripod", "quad_wide"):
        for i in range(r.foot_count):
            if f"leg_{i}" in names:
                leg = model.get_part(f"leg_{i}")
                ctx.allow_overlap(
                    base, leg, elem_a="hub_body", elem_b="leg_tube",
                    reason="Each splayed leg is socketed into the base hub casting.",
                )
                if r.base_form == "tripod":
                    ctx.allow_overlap(
                        base, leg, elem_a="hub_dome", elem_b="leg_tube",
                        reason="Each splayed leg is socketed into the rounded tripod hub.",
                    )
    elif r.base_form == "quad_small":
        for i in range(r.foot_count):
            if f"foot_{i}" in names:
                ctx.allow_overlap(
                    base, model.get_part(f"foot_{i}"), elem_a="plate_body", elem_b="foot_plug",
                    reason="Each rubber foot plug seats into the base plate underside.",
                )

    if r.shaft_type == "telescoping":
        lower = model.get_part("lower_shaft")
        upper = model.get_part("upper_shaft")
        ctx.allow_overlap(
            lower, upper, elem_a="lower_tube", elem_b="inner_tube",
            reason="The inner tube is a captured sliding member nested in the lower telescoping sleeve.",
        )
    else:
        for i in range(3):
            if f"shaft_seg_{i}" in names and f"shaft_seg_{i + 1}" in names:
                a = model.get_part(f"shaft_seg_{i}")
                b = model.get_part(f"shaft_seg_{i + 1}")
                ctx.allow_overlap(
                    a, b, elem_a=f"tube_{i}", elem_b=f"tube_{i + 1}",
                    reason="Adjacent folding segments share a captured fold knuckle and nest when folded.",
                )
                # The pivot-band knuckle on seg_i sweeps against seg_{i+1}'s tube base
                # while folding — a real captured hinge, not a body clash.
                ctx.allow_overlap(
                    a, b, elem_a=f"pivot_band_{i}", elem_b=f"tube_{i + 1}",
                    reason="The fold-hinge pivot band and the next segment's tube share the captured knuckle.",
                )


def _articulation_of_type(model: ArticulatedObject, atype: ArticulationType):
    return [a for a in model.articulations if a.articulation_type == atype]


def run_walking_cane_tests(model: ArticulatedObject, config: WalkingCaneConfig) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)

    _allow_structural_overlaps(ctx, model, r)

    # Baseline-equivalent checks (deduped against compiler baseline).
    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)
    ctx.fail_if_joint_mating_has_gap()

    names = _part_names(model)
    handle = model.get_part("handle")

    # Identity 1: walking-cane height at rest.
    handle_aabb = ctx.part_world_aabb(handle)
    top = handle_aabb[1][2] if handle_aabb is not None else None
    ctx.check(
        "walking_cane_rest_height",
        top is not None and 0.80 <= top <= 1.02,
        details=f"handle top z={top!r} (expected 0.80–1.02 m)",
    )

    # Identity 2: base foot count matches the declared form.
    if r.base_form == "single_point":
        ctx.check("single_point_has_no_foot_loop", "leg_0" not in names and "foot_0" not in names)
    elif r.base_form in ("tripod", "quad_wide"):
        leg_names = [f"leg_{i}" for i in range(r.foot_count)]
        ctx.check(
            f"{r.base_form}_has_{r.foot_count}_legs",
            all(n in names for n in leg_names),
            details=str(leg_names),
        )
    else:  # quad_small
        foot_names = [f"foot_{i}" for i in range(r.foot_count)]
        ctx.check(
            "quad_small_has_4_feet",
            all(n in names for n in foot_names),
            details=str(foot_names),
        )

    # Identity 3: exactly one non-FIXED motion spine exists.
    prismatic = _articulation_of_type(model, ArticulationType.PRISMATIC)
    revolute = _articulation_of_type(model, ArticulationType.REVOLUTE)
    if r.shaft_type == "telescoping":
        ctx.check("telescoping_has_prismatic", len(prismatic) == 1 and len(revolute) == 0)
    else:
        ctx.check("folding_has_revolute_folds", len(revolute) == 3 and len(prismatic) == 0)

    # Motion (Rule 5): targeted pose per mechanism.
    if r.shaft_type == "telescoping" and prismatic:
        slide = prismatic[0]
        limits = slide.motion_limits
        rest = ctx.part_world_position(handle)
        with ctx.pose({slide: limits.upper}):
            extended = ctx.part_world_position(handle)
        ctx.check(
            "telescoping_raises_handle",
            rest is not None and extended is not None and extended[2] > rest[2] + 0.8 * limits.upper,
            details=f"rest={rest}, extended={extended}, travel={limits.upper}",
        )
    elif r.shaft_type == "folding" and revolute:
        driver = model.get_articulation("fold_joint_0")
        upper = driver.motion_limits.upper if driver.motion_limits else 0.0
        rest_top_aabb = ctx.part_world_aabb(handle)
        seg1 = model.get_part("shaft_seg_1")
        rest_seg1 = ctx.part_world_aabb(seg1)
        with ctx.pose({driver: upper}):
            folded_top_aabb = ctx.part_world_aabb(handle)
            folded_seg1 = ctx.part_world_aabb(seg1)
        rest_top = rest_top_aabb[1][2] if rest_top_aabb else None
        folded_top = folded_top_aabb[1][2] if folded_top_aabb else None
        ctx.check(
            "folding_collapses_height",
            rest_top is not None and folded_top is not None and folded_top < rest_top - 0.03,
            details=f"straight_top={rest_top}, folded_top={folded_top}, driver_upper={upper}",
        )
        # seg_1 pivots off vertical: its horizontal (y) extent grows when folded.
        rest_y = (rest_seg1[1][1] - rest_seg1[0][1]) if rest_seg1 else None
        fold_y = (folded_seg1[1][1] - folded_seg1[0][1]) if folded_seg1 else None
        ctx.check(
            "folding_pivots_segment_off_vertical",
            rest_y is not None and fold_y is not None and fold_y > rest_y + 0.02,
            details=f"rest_y={rest_y}, fold_y={fold_y}",
        )

    # Full sampled-pose overlap sweep (mimic followers keep folds on the coupled path).
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=64, ignore_fixed=True)

    return ctx.report()


__all__ = [
    "WalkingCaneConfig",
    "ResolvedWalkingCaneConfig",
    "config_from_seed",
    "resolve_config",
    "build_walking_cane",
    "build_seeded_walking_cane",
    "slot_choices_for_seed",
    "run_walking_cane_tests",
]
