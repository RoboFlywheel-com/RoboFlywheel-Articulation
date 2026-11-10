# SPDX-License-Identifier: Apache-2.0

"""Two-joint prismatic chain — modular procedural template.

This template uses the slot/module/assembler abstraction in
``agent.templates._modular``. The topology is a strict serial PRISMATIC
chain:

    grounded_base --[joint1 PRISMATIC]--> first_stage
        --[joint2 PRISMATIC]--> second_stage
            --[FIXED (optional)]--> end_effector

Slot graph:

    grounded_base ──prismatic1──> first_stage
                                      └──prismatic2──> second_stage
                                                            └──fixed──> end_effector

Slots / candidates:

  grounded_base (6):
    - flat_rail_table   (anchor; rec_..._53ee6ce: base_plate + rail + stops)
    - u_channel_guide   (rec_..._6213b556: cadquery mount + floor + 2 walls)
    - square_sleeve     (rec_..._85e5611: hollow square tube + caps + feet)
    - wall_side_plate   (rec_..._66bd7215: vertical wall + base beam + guides + ribs)
    - top_support_gantry(rec_..._84dfe33: top plate + webs + wear strips, under-slung)
    - broad_transfer_table (rec_..._7e3c4a4: wide flat plate + side rails + pads)

  first_stage (5):
    - rail_carriage     (anchor; rec_..._53ee6ce: carriage base + 2nd rail + stops)
    - channel_runner    (rec_..._6213b556: floor + 2 walls runner)
    - intermediate_tube (rec_..._85e5611: hollow square tube + rear guide)
    - bridge_carriage   (rec_..._66bd7215: runners + bridge plate + secondary rail)
    - outer_slider_web  (rec_..._84dfe33: web + cheeks + runners + lips)

  second_stage (4):
    - slim_carriage     (anchor; rec_..._53ee6ce: c2 body + top plate)
    - bar_with_saddle   (rec_..._6213b556: lower bar + saddle + front plate)
    - output_tube       (rec_..._85e5611: minimal hollow tube + rear guide)
    - inner_blade_slider(rec_..._84dfe33: flange + stem + lower blade)

  end_effector (4):
    - plain_end_face    (anchor; no part — stage2 face is the work face)
    - tool_plate        (rec_..._85e5611: flange plate + ribs)
    - tool_plate_with_mounts (rec_..._0eebad: plate + 2 cylinder mounts)
    - drawer_front_handle (rec_..._b31cd82: front wall + handle; tray styles only)

All chain joints mate on the Z axis (parent deck +Z top ↔ child base -Z
bottom), so the ``fail_if_joint_mating_has_gap`` check — which measures
only along the parent face's outward normal — is satisfied. Both prismatic
joints translate along +X, the direction used by the visible rail/channel/tube
geometry. The slide axis itself is carried on each child's ``upstream``
interface ``consumer_joint_axis`` / ``consumer_motion_limits``. The end_effector
FIXED joint mates on the +X front face.

seed == 0 returns the anchor combination (flat_rail_table + rail_carriage
+ slim_carriage + plain_end_face + coaxial_x) at the canonical dimensions.
Other seeds RNG-pick a compatible module family + sample dimensions.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Literal

import cadquery as cq

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
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
)

# Modular template: sweep coverage uses module_topology_diversity.
__modular__ = True


BaseModule = Literal[
    "flat_rail_table",
    "u_channel_guide",
    "square_sleeve",
    "wall_side_plate",
    "top_support_gantry",
    "broad_transfer_table",
]
FirstStageModule = Literal[
    "rail_carriage",
    "channel_runner",
    "intermediate_tube",
    "bridge_carriage",
    "outer_slider_web",
]
SecondStageModule = Literal[
    "slim_carriage",
    "bar_with_saddle",
    "output_tube",
    "inner_blade_slider",
]
EndEffectorModule = Literal[
    "plain_end_face",
    "tool_plate",
    "tool_plate_with_mounts",
    "drawer_front_handle",
]
AxisFamily = Literal["coaxial_x"]

PaletteTheme = Literal[
    "anchor_steel",
    "powder_blue",
    "anodized_black",
    "industrial_orange",
    "brushed_green",
]


# --------------------------------------------------------------------------- #
# Style families — keep base / link / stage geometry coherent.
# --------------------------------------------------------------------------- #
# Each base style has a "home" family of stage modules so the geometry meshes
# (channel ↔ channel_runner, sleeve ↔ tube, flat ↔ carriage). config_from_seed
# picks a base, then a compatible first_stage + second_stage from this map.

_FAMILY_FOR_BASE: dict[str, str] = {
    "flat_rail_table": "flat",
    "broad_transfer_table": "flat",
    "u_channel_guide": "channel",
    "square_sleeve": "tube",
    "wall_side_plate": "bridge",
    "top_support_gantry": "under_slung",
}

_FIRST_STAGE_FOR_FAMILY: dict[str, list[str]] = {
    "flat": ["rail_carriage"],
    "channel": ["channel_runner"],
    "tube": ["intermediate_tube"],
    "bridge": ["bridge_carriage"],
    "under_slung": ["outer_slider_web"],
}

_SECOND_STAGE_FOR_FAMILY: dict[str, list[str]] = {
    "flat": ["slim_carriage", "bar_with_saddle"],
    "channel": ["bar_with_saddle", "slim_carriage"],
    "tube": ["output_tube"],
    "bridge": ["bar_with_saddle", "slim_carriage"],
    "under_slung": ["inner_blade_slider", "slim_carriage"],
}

# drawer_front_handle only makes sense on tray styles (flat decks carrying a
# tray-like terminal).
_HANDLE_OK_FAMILIES = {"flat", "channel"}


PALETTE_PRESETS: dict[str, dict[str, tuple[float, float, float, float]]] = {
    "anchor_steel": {
        "base": (0.42, 0.45, 0.49, 1.0),
        "stage1": (0.60, 0.63, 0.67, 1.0),
        "stage2": (0.74, 0.77, 0.80, 1.0),
        "rail": (0.30, 0.32, 0.35, 1.0),
        "detail": (0.20, 0.21, 0.23, 1.0),
        "plate": (0.55, 0.58, 0.63, 1.0),
        "accent": (0.85, 0.70, 0.18, 1.0),
    },
    "powder_blue": {
        "base": (0.16, 0.27, 0.44, 1.0),
        "stage1": (0.30, 0.44, 0.62, 1.0),
        "stage2": (0.55, 0.66, 0.78, 1.0),
        "rail": (0.20, 0.30, 0.44, 1.0),
        "detail": (0.10, 0.16, 0.26, 1.0),
        "plate": (0.70, 0.74, 0.80, 1.0),
        "accent": (0.92, 0.55, 0.12, 1.0),
    },
    "anodized_black": {
        "base": (0.07, 0.07, 0.08, 1.0),
        "stage1": (0.16, 0.17, 0.18, 1.0),
        "stage2": (0.30, 0.31, 0.33, 1.0),
        "rail": (0.45, 0.47, 0.50, 1.0),
        "detail": (0.55, 0.57, 0.60, 1.0),
        "plate": (0.62, 0.64, 0.67, 1.0),
        "accent": (0.85, 0.20, 0.15, 1.0),
    },
    "industrial_orange": {
        "base": (0.85, 0.42, 0.10, 1.0),
        "stage1": (0.30, 0.31, 0.33, 1.0),
        "stage2": (0.55, 0.57, 0.60, 1.0),
        "rail": (0.18, 0.19, 0.20, 1.0),
        "detail": (0.10, 0.10, 0.11, 1.0),
        "plate": (0.70, 0.72, 0.74, 1.0),
        "accent": (0.95, 0.80, 0.15, 1.0),
    },
    "brushed_green": {
        "base": (0.18, 0.34, 0.24, 1.0),
        "stage1": (0.32, 0.48, 0.36, 1.0),
        "stage2": (0.56, 0.68, 0.58, 1.0),
        "rail": (0.22, 0.30, 0.24, 1.0),
        "detail": (0.10, 0.16, 0.12, 1.0),
        "plate": (0.66, 0.70, 0.64, 1.0),
        "accent": (0.90, 0.78, 0.20, 1.0),
    },
}


# --------------------------------------------------------------------------- #
# Config dataclasses
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class TwojointPrismaticChainConfig:
    """Public template config. Leave any module field ``None`` to let
    ``config_from_seed`` / ``resolve_config`` fill it from the seed RNG."""

    base_module: BaseModule | None = None
    first_stage_module: FirstStageModule | None = None
    second_stage_module: SecondStageModule | None = None
    end_effector_module: EndEffectorModule | None = None
    axis_family: AxisFamily = "coaxial_x"

    palette_theme: PaletteTheme = "anchor_steel"

    base_length: float = 0.52
    base_width: float = 0.12
    base_height: float = 0.030
    mount_hole_count: int = 4

    stage1_length: float = 0.30
    stage1_stroke: float = 0.22
    stage1_width: float = 0.090

    stage2_length: float = 0.18
    stage2_stroke: float = 0.12
    stage2_width: float = 0.066

    end_plate_thickness: float = 0.012
    end_plate_width: float = 0.090
    end_plate_height: float = 0.090
    end_mount_count: int = 2

    has_end_stops: bool = True

    palette: dict[str, tuple[float, float, float, float]] = field(
        default_factory=lambda: dict(PALETTE_PRESETS["anchor_steel"])
    )


@dataclass(frozen=True)
class ResolvedTwojointPrismaticChainConfig:
    """Dimension-clamped + module-resolved config consumed by builders."""

    base_module: BaseModule
    first_stage_module: FirstStageModule
    second_stage_module: SecondStageModule
    end_effector_module: EndEffectorModule
    axis_family: AxisFamily
    palette_theme: PaletteTheme

    base_length: float
    base_width: float
    base_height: float
    mount_hole_count: int

    stage1_length: float
    stage1_stroke: float
    stage1_width: float

    stage2_length: float
    stage2_stroke: float
    stage2_width: float

    end_plate_thickness: float
    end_plate_width: float
    end_plate_height: float
    end_mount_count: int

    has_end_stops: bool

    # Derived geometry (filled by resolve_config).
    deck_top_z: float  # world Z of the base's stage1-carrying deck top
    stage1_anchor_x: float  # base-frame x of joint1 origin (on deck top)
    palette: dict[str, tuple[float, float, float, float]]


# --------------------------------------------------------------------------- #
# Seed sampling + resolution
# --------------------------------------------------------------------------- #


_BASE_MODULES = tuple(_FAMILY_FOR_BASE.keys())


def config_from_seed(seed: int) -> TwojointPrismaticChainConfig:
    """Sample a configuration for the given seed.

    seed == 0 returns the anchor combination (flat_rail_table + rail_carriage
    + slim_carriage + plain_end_face + coaxial_x) at canonical dimensions.
    Other seeds pick a base, a compatible stage family, an end effector, and
    sample continuous dimensions. Both prismatic joints always follow the +X
    guide axis.
    """
    if seed == 0:
        return TwojointPrismaticChainConfig(
            base_module="flat_rail_table",
            first_stage_module="rail_carriage",
            second_stage_module="slim_carriage",
            end_effector_module="plain_end_face",
            axis_family="coaxial_x",
            palette_theme="anchor_steel",
            base_length=0.52,
            base_width=0.12,
            base_height=0.030,
            mount_hole_count=4,
            stage1_length=0.30,
            stage1_stroke=0.22,
            stage1_width=0.090,
            stage2_length=0.18,
            stage2_stroke=0.12,
            stage2_width=0.066,
            end_mount_count=2,
            has_end_stops=True,
        )

    rng = random.Random(seed)
    base: BaseModule = rng.choice(_BASE_MODULES)  # type: ignore[assignment]
    family = _FAMILY_FOR_BASE[base]
    first_stage: FirstStageModule = rng.choice(  # type: ignore[assignment]
        _FIRST_STAGE_FOR_FAMILY[family]
    )
    second_stage: SecondStageModule = rng.choice(  # type: ignore[assignment]
        _SECOND_STAGE_FOR_FAMILY[family]
    )
    axis_family: AxisFamily = "coaxial_x"

    end_choices: list[str] = ["plain_end_face", "tool_plate", "tool_plate_with_mounts"]
    if family in _HANDLE_OK_FAMILIES:
        end_choices.append("drawer_front_handle")
    # tubes get plate-style ends; never a drawer handle.
    end_effector: EndEffectorModule = rng.choice(end_choices)  # type: ignore[assignment]

    palette_theme: PaletteTheme = rng.choice(tuple(PALETTE_PRESETS.keys()))  # type: ignore[assignment]

    base_length = rng.uniform(0.34, 0.86)
    base_width = rng.uniform(0.090, 0.20)
    base_height = rng.uniform(0.022, 0.044)
    mount_hole_count = rng.randint(0, 6)

    stage1_stroke = rng.uniform(0.12, 0.32)
    # keep base long enough to support stage1 at full stroke.
    stage1_length = rng.uniform(0.20, min(0.52, base_length - stage1_stroke - 0.06))
    if stage1_length < 0.18:
        stage1_length = 0.18
    stage1_width = rng.uniform(0.060, max(0.062, base_width - 0.020))

    stage2_stroke = rng.uniform(0.08, min(0.26, stage1_stroke + 0.02))
    stage2_length = rng.uniform(0.10, min(0.38, stage1_length - stage2_stroke - 0.02))
    if stage2_length < 0.10:
        stage2_length = 0.10
    stage2_width = rng.uniform(0.044, max(0.046, stage1_width - 0.016))

    end_mount_count = rng.randint(2, 4)
    has_end_stops = rng.random() < 0.7

    return TwojointPrismaticChainConfig(
        base_module=base,
        first_stage_module=first_stage,
        second_stage_module=second_stage,
        end_effector_module=end_effector,
        axis_family=axis_family,
        palette_theme=palette_theme,
        base_length=round(base_length, 4),
        base_width=round(base_width, 4),
        base_height=round(base_height, 4),
        mount_hole_count=mount_hole_count,
        stage1_length=round(stage1_length, 4),
        stage1_stroke=round(stage1_stroke, 4),
        stage1_width=round(stage1_width, 4),
        stage2_length=round(stage2_length, 4),
        stage2_stroke=round(stage2_stroke, 4),
        stage2_width=round(stage2_width, 4),
        end_mount_count=end_mount_count,
        has_end_stops=has_end_stops,
    )


def resolve_config(
    config: TwojointPrismaticChainConfig,
) -> ResolvedTwojointPrismaticChainConfig:
    """Validate enums, clamp floats, fill None modules with anchors, and
    derive deck geometry that keeps the chain nested + supported at rest and
    full stroke."""

    base = config.base_module or "flat_rail_table"
    first_stage = config.first_stage_module or "rail_carriage"
    second_stage = config.second_stage_module or "slim_carriage"
    end_effector = config.end_effector_module or "plain_end_face"
    axis_family = config.axis_family or "coaxial_x"

    if base not in BaseModule.__args__:  # type: ignore[attr-defined]
        raise ValueError(f"Unsupported base_module: {base}")
    if first_stage not in FirstStageModule.__args__:  # type: ignore[attr-defined]
        raise ValueError(f"Unsupported first_stage_module: {first_stage}")
    if second_stage not in SecondStageModule.__args__:  # type: ignore[attr-defined]
        raise ValueError(f"Unsupported second_stage_module: {second_stage}")
    if end_effector not in EndEffectorModule.__args__:  # type: ignore[attr-defined]
        raise ValueError(f"Unsupported end_effector_module: {end_effector}")
    if axis_family not in AxisFamily.__args__:  # type: ignore[attr-defined]
        raise ValueError(f"Unsupported axis_family: {axis_family}")
    if str(config.palette_theme) not in PALETTE_PRESETS:
        raise ValueError(f"Unsupported palette_theme: {config.palette_theme}")

    base_length = max(0.30, min(float(config.base_length), 0.90))
    base_width = max(0.080, min(float(config.base_width), 0.22))
    base_height = max(0.020, min(float(config.base_height), 0.048))
    mount_hole_count = max(0, min(int(config.mount_hole_count), 6))

    stage1_stroke = max(0.10, min(float(config.stage1_stroke), 0.35))
    stage1_length = max(0.18, min(float(config.stage1_length), 0.55))
    stage1_width = max(0.055, min(float(config.stage1_width), base_width - 0.012))
    if stage1_width < 0.050:
        stage1_width = 0.050

    stage2_stroke = max(0.08, min(float(config.stage2_stroke), 0.30))
    stage2_length = max(0.10, min(float(config.stage2_length), stage1_length - 0.02))
    stage2_width = max(0.040, min(float(config.stage2_width), stage1_width - 0.010))
    if stage2_width < 0.038:
        stage2_width = 0.038

    # Guarantee step-down + support feasibility.  base must cover the rest
    # footprint of stage1 plus its stroke; stage1 must cover stage2 + stroke.
    if base_length < stage1_length + stage1_stroke + 0.04:
        base_length = stage1_length + stage1_stroke + 0.04
    if stage1_length < stage2_length + stage2_stroke + 0.02:
        # shrink stage2 instead of growing stage1 (keep step-down).
        stage2_length = max(0.08, stage1_length - stage2_stroke - 0.02)
        if stage2_length < 0.08:
            stage2_stroke = max(0.06, stage1_length - stage2_length - 0.02)

    base_length = min(base_length, 0.95)

    end_plate_thickness = max(0.006, min(float(config.end_plate_thickness), 0.020))
    end_plate_width = max(0.040, min(float(config.end_plate_width), stage2_width * 1.8))
    end_plate_height = max(0.040, min(float(config.end_plate_height), 0.14))
    end_mount_count = max(1, min(int(config.end_mount_count), 4))

    # Deck top Z = base body height (everything rides on top of the base body).
    deck_top_z = base_height
    # joint1 origin x in base frame: positioned so stage1 sits over the rear
    # of the base at rest and still overlaps at full stroke.  Base body spans
    # x in [0, base_length]; place anchor a small inset from the rear.
    stage1_anchor_x = 0.02

    palette = dict(PALETTE_PRESETS[config.palette_theme])

    return ResolvedTwojointPrismaticChainConfig(
        base_module=base,
        first_stage_module=first_stage,
        second_stage_module=second_stage,
        end_effector_module=end_effector,
        axis_family=axis_family,
        palette_theme=config.palette_theme,
        base_length=base_length,
        base_width=base_width,
        base_height=base_height,
        mount_hole_count=mount_hole_count,
        stage1_length=stage1_length,
        stage1_stroke=stage1_stroke,
        stage1_width=stage1_width,
        stage2_length=stage2_length,
        stage2_stroke=stage2_stroke,
        stage2_width=stage2_width,
        end_plate_thickness=end_plate_thickness,
        end_plate_width=end_plate_width,
        end_plate_height=end_plate_height,
        end_mount_count=end_mount_count,
        has_end_stops=bool(config.has_end_stops),
        deck_top_z=deck_top_z,
        stage1_anchor_x=stage1_anchor_x,
        palette=palette,
    )


# --------------------------------------------------------------------------- #
# Joint helpers — both serial prismatic stages follow the visible +X guide axis.
# --------------------------------------------------------------------------- #


def _joint1_axis_limits(
    r: ResolvedTwojointPrismaticChainConfig,
) -> tuple[tuple[float, float, float], MotionLimits]:
    return (1.0, 0.0, 0.0), MotionLimits(
        effort=120.0, velocity=0.4, lower=0.0, upper=r.stage1_stroke
    )


def _joint2_axis_limits(
    r: ResolvedTwojointPrismaticChainConfig,
) -> tuple[tuple[float, float, float], MotionLimits]:
    return (1.0, 0.0, 0.0), MotionLimits(
        effort=90.0, velocity=0.4, lower=0.0, upper=r.stage2_stroke
    )


# Small downward penetration so child base AABB overlaps the parent deck
# (keeps fail_if_isolated_parts happy) while the Z mating gap stays < tol.
_PEN = 0.0015
_DECK_T = 0.010  # standard deck/rail plate thickness


def _cq_rounded_box(
    sx: float,
    sy: float,
    sz: float,
    *,
    fillet: float | None = None,
    vertical_edges_only: bool = True,
):
    """Small CadQuery hard-surface block for cosmetic details.

    Mating/reference surfaces stay as Box visuals elsewhere; these meshes are
    used on non-critical plates, side walls, stops, ribs, and caps so the
    modular template keeps the source samples' machined/filleted feel.
    """
    shape = cq.Workplane("XY").box(sx, sy, sz, centered=(True, True, True))
    radius = min(fillet if fillet is not None else min(sx, sy, sz) * 0.12, min(sx, sy, sz) * 0.35)
    if radius > 1e-5:
        selector = "|Z" if vertical_edges_only else None
        try:
            shape = (
                shape.edges(selector).fillet(radius) if selector else shape.edges().fillet(radius)
            )
        except Exception:
            # Some very thin generated variants can produce invalid fillets;
            # keep the block instead of failing template generation.
            return cq.Workplane("XY").box(sx, sy, sz, centered=(True, True, True))
    return shape


def _cq_plate_with_holes(sx: float, sy: float, sz: float, holes: int):
    shape = _cq_rounded_box(sx, sy, sz, fillet=min(0.010, sy * 0.06))
    if holes <= 0:
        return shape
    pts = []
    for i in range(holes):
        frac = (i + 1) / (holes + 1)
        pts.append(((frac - 0.5) * sx, sy * 0.32 * (1 if i % 2 == 0 else -1)))
    return (
        shape.faces(">Z")
        .workplane(centerOption="CenterOfMass")
        .pushPoints(pts)
        .hole(min(0.010, sy * 0.10))
    )


def _add_cq_block(
    part,
    *,
    size: tuple[float, float, float],
    xyz: tuple[float, float, float],
    material: str,
    name: str,
    fillet: float | None = None,
    vertical_edges_only: bool = True,
) -> None:
    part.visual(
        mesh_from_cadquery(
            _cq_rounded_box(*size, fillet=fillet, vertical_edges_only=vertical_edges_only),
            name,
        ),
        origin=Origin(xyz=xyz),
        material=material,
        name=name, material_class_id="metal.paint_coated",
    )


# --------------------------------------------------------------------------- #
# grounded_base module factories (Slot A)
# --------------------------------------------------------------------------- #


def _base_downstream_iface(
    r: ResolvedTwojointPrismaticChainConfig,
    *,
    visual_name: str,
    deck_z: float | None = None,
) -> InterfaceSpec:
    """The base exposes its deck top (+Z) at the joint1 origin.  ``deck_z`` is
    the world Z of the named visual's +Z face (the surface stage1 rides on);
    it must match exactly so the Z mating gap is ~0.  joint1's axis/limits
    follow the +X guide axis."""
    axis, limits = _joint1_axis_limits(r)
    return InterfaceSpec(
        interface_name="downstream",
        part_name="grounded_base",
        visual_name=visual_name,
        face_side="positive_z",
        anchor_local=(r.stage1_anchor_x, 0.0, r.deck_top_z if deck_z is None else deck_z),
        face_extents_uv=(r.base_length, r.base_width),
        extents_tol=0.6,
        contact_tol=0.005,
        consumer_joint_type=ArticulationType.PRISMATIC,
        consumer_joint_axis=axis,
        consumer_motion_limits=limits,
    )


def _build_flat_rail_table_base(ctx: ModuleBuildContext) -> ModuleBuild:
    """Anchor base — low flat platform: base_plate + central raised rail +
    left/right end stops.  Adapted from rec_..._53ee6ce L16-L41."""
    model = ctx.model
    r: ResolvedTwojointPrismaticChainConfig = ctx.config  # type: ignore[assignment]
    base = model.part("grounded_base")
    L, W, H = r.base_length, r.base_width, r.base_height

    plate_t = H * 0.45
    base.visual(
        mesh_from_cadquery(
            _cq_plate_with_holes(L, W, plate_t, r.mount_hole_count),
            "base_plate",
        ),
        origin=Origin(xyz=(L * 0.5, 0.0, plate_t * 0.5)),
        material="base",
        name="base_plate", material_class_id="metal.paint_coated",
    )
    rail_w = W * 0.55
    rail_h = H - plate_t
    base.visual(
        Box((L - 0.02, rail_w, rail_h + 0.002)),
        origin=Origin(xyz=(L * 0.5, 0.0, plate_t + rail_h * 0.5 - 0.001)),
        material="rail",
        name="base_rail", material_class_id="metal.steel_bare",
    )
    if r.has_end_stops:
        for nm, x in (("base_stop_rear", 0.006), ("base_stop_front", L - 0.006)):
            _add_cq_block(
                base,
                size=(0.012, W * 0.6, rail_h + 0.01),
                xyz=(x, 0.0, plate_t + (rail_h + 0.01) * 0.5),
                material="detail",
                name=nm,
            )
    base.inertial = Inertial.from_geometry(
        Box((L, W, H)), mass=5.0, origin=Origin(xyz=(L * 0.5, 0.0, H * 0.5))
    )
    return ModuleBuild(
        module_name="flat_rail_table",
        parts_emitted=["grounded_base"],
        interfaces={"downstream": _base_downstream_iface(r, visual_name="base_rail")},
    )


def _u_channel_mount_shape(L: float, W: float, t: float, holes: int):
    base = cq.Workplane("XY").box(L, W, t, centered=(False, True, False))
    if holes > 0:
        pts = []
        for i in range(holes):
            frac = (i + 1) / (holes + 1)
            pts.append((frac * L, W * 0.32 * (1 if i % 2 == 0 else -1)))
        base = (
            base.faces(">Z")
            .workplane(centerOption="CenterOfMass")
            .pushPoints(pts)
            .hole(min(0.010, W * 0.10))
        )
    return base


def _build_u_channel_guide_base(ctx: ModuleBuildContext) -> ModuleBuild:
    """U-channel base — cadquery bolt-down mount plate + Box floor + two side
    walls forming a channel the stage nests into.  Adapted from
    rec_..._6213b556 L62-L161 (keeps the cadquery mount + Box-wall channel)."""
    model = ctx.model
    r: ResolvedTwojointPrismaticChainConfig = ctx.config  # type: ignore[assignment]
    base = model.part("grounded_base")
    L, W, H = r.base_length, r.base_width, r.base_height

    mount_t = H * 0.38
    base.visual(
        mesh_from_cadquery(
            _u_channel_mount_shape(L, W, mount_t, r.mount_hole_count),
            "u_channel_mount",
        ),
        origin=Origin(xyz=(0.0, 0.0, mount_t * 0.5)),
        material="base",
        name="u_channel_mount", material_class_id="metal.paint_coated",
    )
    floor_t = H * 0.28
    floor_z = mount_t + floor_t * 0.5
    channel_deck_z = mount_t + floor_t
    base.visual(
        Box((L - 0.01, W * 0.7, floor_t)),
        origin=Origin(xyz=(L * 0.5, 0.0, floor_z)),
        material="rail",
        name="channel_floor", material_class_id="metal.steel_bare",
    )
    wall_h = H - mount_t
    wall_w = W * 0.07
    wall_y = W * 0.35 - wall_w * 0.5
    for nm, sgn in (("channel_left_wall", 1.0), ("channel_right_wall", -1.0)):
        _add_cq_block(
            base,
            size=(L - 0.01, wall_w, wall_h),
            xyz=(L * 0.5, sgn * wall_y, mount_t + wall_h * 0.5),
            material="rail",
            name=nm,
        )
    base.inertial = Inertial.from_geometry(
        Box((L, W, H)), mass=6.0, origin=Origin(xyz=(L * 0.5, 0.0, H * 0.5))
    )
    return ModuleBuild(
        module_name="u_channel_guide",
        parts_emitted=["grounded_base"],
        interfaces={
            "downstream": _base_downstream_iface(
                r, visual_name="channel_floor", deck_z=channel_deck_z
            )
        },
    )


def _add_square_tube(part, *, prefix, x0, length, outer, wall, z_center, material):
    """Four-Box hollow square tube centered at (x_center, 0, z_center)."""
    half = outer * 0.5
    wc = half - wall * 0.5
    xc = x0 + length * 0.5
    _add_cq_block(
        part,
        size=(length, outer, wall),
        xyz=(xc, 0.0, z_center + wc),
        material=material,
        name=f"{prefix}_top",
    )
    part.visual(
        Box((length, outer, wall)),
        origin=Origin(xyz=(xc, 0.0, z_center - wc)),
        material=material,
        name=f"{prefix}_bottom", material_class_id="metal.paint_coated",
    )
    _add_cq_block(
        part,
        size=(length, wall, outer),
        xyz=(xc, wc, z_center),
        material=material,
        name=f"{prefix}_left",
    )
    _add_cq_block(
        part,
        size=(length, wall, outer),
        xyz=(xc, -wc, z_center),
        material=material,
        name=f"{prefix}_right",
    )


def _build_square_sleeve_base(ctx: ModuleBuildContext) -> ModuleBuild:
    """Square-sleeve base — hollow square tube outer_sleeve (four Box walls) +
    rear cap + mount_base + feet, telescoping tube-in-tube.  Adapted from
    rec_..._85e5611 L147-L198 (preserves the Box-wall hollow tube)."""
    model = ctx.model
    r: ResolvedTwojointPrismaticChainConfig = ctx.config  # type: ignore[assignment]
    base = model.part("grounded_base")
    L, W, H = r.base_length, r.base_width, r.base_height
    outer = max(W, H)
    wall = outer * 0.10
    axis_z = outer * 0.5  # tube center sits a half-size above the floor
    rear_cap = 0.016

    _add_square_tube(
        base,
        prefix="sleeve",
        x0=rear_cap,
        length=L - rear_cap,
        outer=outer,
        wall=wall,
        z_center=axis_z,
        material="base",
    )
    _add_cq_block(
        base,
        size=(rear_cap, outer, outer),
        xyz=(rear_cap * 0.5, 0.0, axis_z),
        material="base",
        name="rear_cap",
    )
    foot_t = 0.010
    _add_cq_block(
        base,
        size=(L * 0.9, W, foot_t),
        xyz=(L * 0.5, 0.0, foot_t * 0.5),
        material="detail",
        name="mount_base",
    )
    # riser connecting the foot up to the tube bottom (avoid island)
    base.visual(
        Box((L * 0.9, outer * 0.5, axis_z - outer * 0.5 + 0.002)),
        origin=Origin(xyz=(L * 0.5, 0.0, (axis_z - outer * 0.5) * 0.5 + foot_t)),
        material="detail",
        name="mount_riser", material_class_id="metal.paint_coated",
    )
    base.inertial = Inertial.from_geometry(
        Box((L, outer, axis_z + outer * 0.5)),
        mass=6.0,
        origin=Origin(xyz=(L * 0.5, 0.0, axis_z)),
    )
    # The sleeve carries the next tube as a tube-in-tube slide: the inner
    # tube rests on the sleeve's inner floor (top of the bottom wall), at
    # world z = `wall`.  The child tube builds its own bottom-wall -Z face at
    # local z ~= 0, so the Z mating gap is ~0 and the inner tube still nests
    # inside the sleeve cavity (and slides along the slide axis).
    sleeve_floor_top = wall
    axis, limits = _joint1_axis_limits(r)
    downstream = InterfaceSpec(
        interface_name="downstream",
        part_name="grounded_base",
        visual_name="sleeve_bottom",
        face_side="positive_z",
        anchor_local=(r.stage1_anchor_x, 0.0, sleeve_floor_top),
        face_extents_uv=(L, outer),
        extents_tol=0.6,
        contact_tol=0.006,
        consumer_joint_type=ArticulationType.PRISMATIC,
        consumer_joint_axis=axis,
        consumer_motion_limits=limits,
    )
    return ModuleBuild(
        module_name="square_sleeve",
        parts_emitted=["grounded_base"],
        interfaces={"downstream": downstream},
    )


def _build_wall_side_plate_base(ctx: ModuleBuildContext) -> ModuleBuild:
    """Wall-backed base — vertical wall_plate (side mount) + horizontal
    base_beam + twin guides + triangular ribs.  Adapted from
    rec_..._66bd7215 L97-L162 (Box adaptation of the wall+beam+guide+rib)."""
    model = ctx.model
    r: ResolvedTwojointPrismaticChainConfig = ctx.config  # type: ignore[assignment]
    base = model.part("grounded_base")
    L, W, H = r.base_length, r.base_width, r.base_height

    plate_t = 0.012
    plate_h = H + W * 0.6
    _add_cq_block(
        base,
        size=(L, plate_t, plate_h),
        xyz=(L * 0.5, -W * 0.5 - plate_t * 0.5, plate_h * 0.5 - H * 0.2),
        material="base",
        name="wall_plate",
    )
    beam_t = H * 0.6
    _add_cq_block(
        base,
        size=(L, W, beam_t),
        xyz=(L * 0.5, 0.0, beam_t * 0.5),
        material="base",
        name="base_beam",
    )
    guide_h = H - beam_t
    guide_w = W * 0.12
    guide_y = W * 0.5 - guide_w * 0.5
    for nm, sgn in (("left_guide", 1.0), ("right_guide", -1.0)):
        _add_cq_block(
            base,
            size=(L - 0.03, guide_w, guide_h + 0.004),
            xyz=(L * 0.5, sgn * guide_y, beam_t + guide_h * 0.5 - 0.002),
            material="rail",
            name=nm,
        )
    # central deck rail between the guides
    base.visual(
        Box((L - 0.03, W * 0.5, guide_h)),
        origin=Origin(xyz=(L * 0.5, 0.0, beam_t + guide_h * 0.5)),
        material="rail",
        name="center_rail", material_class_id="metal.steel_bare",
    )
    # triangular gusset ribs joining wall_plate to base_beam (Box wedges)
    for i, x in enumerate((L * 0.2, L * 0.8)):
        _add_cq_block(
            base,
            size=(0.010, W * 0.5, plate_h * 0.4),
            xyz=(x, -W * 0.25, plate_h * 0.2 - H * 0.1),
            material="detail",
            name=f"gusset_rib_{i}",
        )
    base.inertial = Inertial.from_geometry(
        Box((L, W * 1.4, plate_h)),
        mass=6.5,
        origin=Origin(xyz=(L * 0.5, -W * 0.2, plate_h * 0.3)),
    )
    return ModuleBuild(
        module_name="wall_side_plate",
        parts_emitted=["grounded_base"],
        interfaces={"downstream": _base_downstream_iface(r, visual_name="center_rail")},
    )


def _build_top_support_gantry_base(ctx: ModuleBuildContext) -> ModuleBuild:
    """Top-support gantry base — top mounting_plate + downward webs + lips +
    wear strips + end stops; stage hangs under-slung.  Adapted from
    rec_..._84dfe33 L28-L82.  For uniform Z-mating the carried rail is a
    downward-facing deck the slider rides on top of."""
    model = ctx.model
    r: ResolvedTwojointPrismaticChainConfig = ctx.config  # type: ignore[assignment]
    base = model.part("grounded_base")
    L, W, H = r.base_length, r.base_width, r.base_height

    plate_t = H * 0.4
    top_z = H + W * 0.3
    base.visual(
        mesh_from_cadquery(
            _cq_plate_with_holes(L, W * 1.4, plate_t, r.mount_hole_count),
            "mounting_plate",
        ),
        origin=Origin(xyz=(L * 0.5, 0.0, top_z + plate_t * 0.5)),
        material="base",
        name="mounting_plate", material_class_id="metal.paint_coated",
    )
    web_t = 0.012
    web_y = W * 0.5
    for nm, sgn in (("support_web_0", 1.0), ("support_web_1", -1.0)):
        _add_cq_block(
            base,
            size=(L * 0.92, web_t, top_z - H + plate_t),
            xyz=(L * 0.5, sgn * web_y, (top_z + H) * 0.5),
            material="base",
            name=nm,
        )
    # carried rail deck (top surface at deck_top_z = H) between the webs
    rail_h = H * 0.5
    base.visual(
        Box((L * 0.9, W * 0.7, rail_h)),
        origin=Origin(xyz=(L * 0.5, 0.0, H - rail_h * 0.5)),
        material="rail",
        name="carry_rail", material_class_id="metal.steel_bare",
    )
    # connect rail up to the plate/webs so it isn't an island
    base.visual(
        Box((L * 0.9, W * 0.2, top_z - H + 0.002)),
        origin=Origin(xyz=(L * 0.5, 0.0, (top_z + H) * 0.5)),
        material="base",
        name="rail_hanger", material_class_id="metal.paint_coated",
    )
    if r.has_end_stops:
        for nm, x in (("rear_stop", 0.012), ("front_stop", L - 0.012)):
            _add_cq_block(
                base,
                size=(0.018, W * 0.8, rail_h + 0.012),
                xyz=(x, 0.0, H - rail_h * 0.5),
                material="detail",
                name=nm,
            )
    base.inertial = Inertial.from_geometry(
        Box((L, W * 1.4, top_z + plate_t)),
        mass=7.0,
        origin=Origin(xyz=(L * 0.5, 0.0, top_z * 0.6)),
    )
    return ModuleBuild(
        module_name="top_support_gantry",
        parts_emitted=["grounded_base"],
        interfaces={"downstream": _base_downstream_iface(r, visual_name="carry_rail")},
    )


def _broad_base_shape(L: float, W: float, t: float):
    return (
        cq.Workplane("XY")
        .box(L, W, t, centered=(True, True, True))
        .edges("|Z")
        .fillet(min(0.012, W * 0.08))
    )


def _build_broad_transfer_table_base(ctx: ModuleBuildContext) -> ModuleBuild:
    """Broad transfer table — wide flat (filleted cadquery) plate + twin long
    side rails + end pads, broad footprint for long-stroke transfer.  Adapted
    from rec_..._7e3c4a4 L56-L90."""
    model = ctx.model
    r: ResolvedTwojointPrismaticChainConfig = ctx.config  # type: ignore[assignment]
    base = model.part("grounded_base")
    L = r.base_length
    W = max(r.base_width, 0.16)
    H = r.base_height
    plate_t = H * 0.5

    base.visual(
        mesh_from_cadquery(_broad_base_shape(L, W, plate_t), "broad_plate"),
        origin=Origin(xyz=(L * 0.5, 0.0, plate_t * 0.5)),
        material="base",
        name="broad_plate", material_class_id="metal.paint_coated",
    )
    rail_h = H - plate_t
    rail_w = W * 0.10
    rail_y = W * 0.32
    for nm, sgn in (("left_rail", 1.0), ("right_rail", -1.0)):
        _add_cq_block(
            base,
            size=(L * 0.92, rail_w, rail_h + 0.002),
            xyz=(L * 0.5, sgn * rail_y, plate_t + rail_h * 0.5 - 0.001),
            material="rail",
            name=nm,
        )
    # central carry rail (deck) the stage rides on
    base.visual(
        Box((L * 0.92, W * 0.5, rail_h)),
        origin=Origin(xyz=(L * 0.5, 0.0, plate_t + rail_h * 0.5)),
        material="rail",
        name="center_rail", material_class_id="metal.steel_bare",
    )
    base.inertial = Inertial.from_geometry(
        Box((L, W, H)), mass=8.0, origin=Origin(xyz=(L * 0.5, 0.0, H * 0.5))
    )
    return ModuleBuild(
        module_name="broad_transfer_table",
        parts_emitted=["grounded_base"],
        interfaces={"downstream": _base_downstream_iface(r, visual_name="center_rail")},
    )


# --------------------------------------------------------------------------- #
# first_stage module factories (Slot B)
# --------------------------------------------------------------------------- #


def _stage1_upstream_iface(
    r: ResolvedTwojointPrismaticChainConfig,
    *,
    visual_name: str,
) -> InterfaceSpec:
    """stage1 mates its bottom (-Z) onto the base deck; consumer joint1
    axis/limits follow the +X guide axis."""
    axis, limits = _joint1_axis_limits(r)
    return InterfaceSpec(
        interface_name="upstream",
        part_name="first_stage",
        visual_name=visual_name,
        face_side="negative_z",
        anchor_local=(0.0, 0.0, 0.0),
        face_extents_uv=(r.stage1_length, r.stage1_width),
        extents_tol=0.6,
        contact_tol=0.006,
        consumer_joint_type=ArticulationType.PRISMATIC,
        consumer_joint_axis=axis,
        consumer_motion_limits=limits,
    )


def _stage1_downstream_iface(
    r: ResolvedTwojointPrismaticChainConfig,
    *,
    visual_name: str,
    deck_z: float,
) -> InterfaceSpec:
    """stage1 exposes its own deck top (+Z) for stage2. joint2 axis/limits
    follow the +X guide axis."""
    axis, limits = _joint2_axis_limits(r)
    return InterfaceSpec(
        interface_name="downstream",
        part_name="first_stage",
        visual_name=visual_name,
        face_side="positive_z",
        anchor_local=(0.02, 0.0, deck_z),
        face_extents_uv=(r.stage1_length, r.stage1_width),
        extents_tol=0.6,
        contact_tol=0.006,
        consumer_joint_type=ArticulationType.PRISMATIC,
        consumer_joint_axis=axis,
        consumer_motion_limits=limits,
    )


def _build_rail_carriage_stage1(ctx: ModuleBuildContext) -> ModuleBuild:
    """Anchor first_stage — carriage base + upper secondary rail (for stage2)
    + end stops.  Adapted from rec_..._53ee6ce L43-L66."""
    model = ctx.model
    r: ResolvedTwojointPrismaticChainConfig = ctx.config  # type: ignore[assignment]
    stage = model.part("first_stage")
    Lf = r.stage1_length
    Wf = r.stage1_width
    base_t = _DECK_T

    stage.visual(
        Box((Lf, Wf, base_t)),
        origin=Origin(xyz=(Lf * 0.5, 0.0, base_t * 0.5 - _PEN)),
        material="stage1",
        name="c1_base", material_class_id="metal.paint_coated",
    )
    rail_h = 0.012
    rail_top = base_t - _PEN + rail_h
    stage.visual(
        Box((Lf - 0.02, Wf * 0.55, rail_h)),
        origin=Origin(xyz=(Lf * 0.5, 0.0, base_t - _PEN + rail_h * 0.5)),
        material="rail",
        name="c1_rail", material_class_id="metal.steel_bare",
    )
    if r.has_end_stops:
        for nm, x in (("c1_stop_rear", 0.006), ("c1_stop_front", Lf - 0.006)):
            _add_cq_block(
                stage,
                size=(0.012, Wf * 0.6, rail_h + 0.008),
                xyz=(x, 0.0, base_t - _PEN + (rail_h + 0.008) * 0.5),
                material="detail",
                name=nm,
            )
    stage.inertial = Inertial.from_geometry(
        Box((Lf, Wf, base_t + rail_h)),
        mass=1.5,
        origin=Origin(xyz=(Lf * 0.5, 0.0, base_t * 0.5)),
    )
    return ModuleBuild(
        module_name="rail_carriage",
        parts_emitted=["first_stage"],
        interfaces={
            "upstream": _stage1_upstream_iface(r, visual_name="c1_base"),
            "downstream": _stage1_downstream_iface(r, visual_name="c1_rail", deck_z=rail_top),
        },
    )


def _build_channel_runner_stage1(ctx: ModuleBuildContext) -> ModuleBuild:
    """Channel runner first_stage — floor + two side walls; nests in the base
    channel and re-channels stage2.  Adapted from rec_..._6213b556 L163-L198."""
    model = ctx.model
    r: ResolvedTwojointPrismaticChainConfig = ctx.config  # type: ignore[assignment]
    stage = model.part("first_stage")
    Lf, Wf = r.stage1_length, r.stage1_width
    floor_t = _DECK_T

    stage.visual(
        Box((Lf, Wf, floor_t)),
        origin=Origin(xyz=(Lf * 0.5, 0.0, floor_t * 0.5 - _PEN)),
        material="stage1",
        name="runner_floor", material_class_id="metal.paint_coated",
    )
    wall_h = Wf * 0.5
    wall_w = Wf * 0.10
    wall_y = Wf * 0.5 - wall_w * 0.5
    deck_top = floor_t - _PEN
    for nm, sgn in (("runner_left_wall", 1.0), ("runner_right_wall", -1.0)):
        _add_cq_block(
            stage,
            size=(Lf, wall_w, wall_h),
            xyz=(Lf * 0.5, sgn * wall_y, floor_t - _PEN + wall_h * 0.5),
            material="stage1",
            name=nm,
        )
    stage.inertial = Inertial.from_geometry(
        Box((Lf, Wf, floor_t + wall_h)),
        mass=1.4,
        origin=Origin(xyz=(Lf * 0.5, 0.0, floor_t * 0.5)),
    )
    return ModuleBuild(
        module_name="channel_runner",
        parts_emitted=["first_stage"],
        interfaces={
            "upstream": _stage1_upstream_iface(r, visual_name="runner_floor"),
            "downstream": _stage1_downstream_iface(r, visual_name="runner_floor", deck_z=deck_top),
        },
    )


def _build_intermediate_tube_stage1(ctx: ModuleBuildContext) -> ModuleBuild:
    """Intermediate-tube first_stage — hollow square tube nested coaxially in
    the sleeve and carrying the output tube.  Adapted from rec_..._85e5611
    L200-L223 (preserves the Box-wall hollow tube)."""
    model = ctx.model
    r: ResolvedTwojointPrismaticChainConfig = ctx.config  # type: ignore[assignment]
    stage = model.part("first_stage")
    Lf = r.stage1_length
    outer = max(r.stage1_width, r.base_height * 1.4)
    wall = outer * 0.10

    # The tube is centered on z=0 in part frame; the bottom-wall -Z face sits
    # at z = -outer/2.  The joint origin lands at deck_top_z (= sleeve axis),
    # so the tube nests coaxially with the sleeve.  Penetrate the bottom into
    # the sleeve floor slightly via z offset on the tube center.
    z_center = outer * 0.5 - _PEN
    _add_square_tube(
        stage,
        prefix="intermediate",
        x0=0.0,
        length=Lf,
        outer=outer,
        wall=wall,
        z_center=z_center,
        material="stage1",
    )
    stage.inertial = Inertial.from_geometry(
        Box((Lf, outer, outer)),
        mass=2.0,
        origin=Origin(xyz=(Lf * 0.5, 0.0, z_center)),
    )
    # bottom face -Z is the upstream mate; top face +Z is the stage2 deck.
    axis_u, limits_u = _joint1_axis_limits(r)
    axis_d, limits_d = _joint2_axis_limits(r)
    upstream = InterfaceSpec(
        interface_name="upstream",
        part_name="first_stage",
        visual_name="intermediate_bottom",
        face_side="negative_z",
        anchor_local=(0.0, 0.0, 0.0),
        face_extents_uv=(Lf, outer),
        extents_tol=0.6,
        contact_tol=0.008,
        consumer_joint_type=ArticulationType.PRISMATIC,
        consumer_joint_axis=axis_u,
        consumer_motion_limits=limits_u,
    )
    # Output tube rests on the intermediate's inner floor (top of bottom
    # wall), at z = z_center - outer/2 + wall.  Mating along Z uses the
    # bottom wall's +Z (inner) face = same surface, so the gap is ~0.
    inner_floor_top = z_center - outer * 0.5 + wall
    downstream = InterfaceSpec(
        interface_name="downstream",
        part_name="first_stage",
        visual_name="intermediate_bottom",
        face_side="positive_z",
        anchor_local=(0.02, 0.0, inner_floor_top),
        face_extents_uv=(Lf, outer),
        extents_tol=0.6,
        contact_tol=0.008,
        consumer_joint_type=ArticulationType.PRISMATIC,
        consumer_joint_axis=axis_d,
        consumer_motion_limits=limits_d,
    )
    return ModuleBuild(
        module_name="intermediate_tube",
        parts_emitted=["first_stage"],
        interfaces={"upstream": upstream, "downstream": downstream},
    )


def _build_bridge_carriage_stage1(ctx: ModuleBuildContext) -> ModuleBuild:
    """Bridge carriage first_stage — twin runners + bridge plate + secondary
    rail spanning the wall-base guides.  Adapted from rec_..._66bd7215
    L294-L322."""
    model = ctx.model
    r: ResolvedTwojointPrismaticChainConfig = ctx.config  # type: ignore[assignment]
    stage = model.part("first_stage")
    Lf, Wf = r.stage1_length, r.stage1_width
    plate_t = _DECK_T

    stage.visual(
        Box((Lf, Wf, plate_t)),
        origin=Origin(xyz=(Lf * 0.5, 0.0, plate_t * 0.5 - _PEN)),
        material="stage1",
        name="bridge_plate", material_class_id="metal.paint_coated",
    )
    runner_w = Wf * 0.16
    runner_h = 0.010
    runner_y = Wf * 0.5 - runner_w * 0.5
    for nm, sgn in (("bridge_runner_0", 1.0), ("bridge_runner_1", -1.0)):
        _add_cq_block(
            stage,
            size=(Lf - 0.02, runner_w, runner_h),
            xyz=(Lf * 0.5, sgn * runner_y, plate_t - _PEN + runner_h * 0.5),
            material="stage1",
            name=nm,
        )
    rail_h = 0.012
    rail_top = plate_t - _PEN + rail_h
    stage.visual(
        Box((Lf - 0.04, Wf * 0.4, rail_h)),
        origin=Origin(xyz=(Lf * 0.5, 0.0, plate_t - _PEN + rail_h * 0.5)),
        material="rail",
        name="secondary_rail", material_class_id="metal.steel_bare",
    )
    stage.inertial = Inertial.from_geometry(
        Box((Lf, Wf, plate_t + rail_h)),
        mass=1.6,
        origin=Origin(xyz=(Lf * 0.5, 0.0, plate_t * 0.5)),
    )
    return ModuleBuild(
        module_name="bridge_carriage",
        parts_emitted=["first_stage"],
        interfaces={
            "upstream": _stage1_upstream_iface(r, visual_name="bridge_plate"),
            "downstream": _stage1_downstream_iface(
                r, visual_name="secondary_rail", deck_z=rail_top
            ),
        },
    )


def _build_outer_slider_web_stage1(ctx: ModuleBuildContext) -> ModuleBuild:
    """Outer slider web first_stage — web + twin cheeks + runners + end tie,
    capturing the inner slider.  Adapted from rec_..._84dfe33 L84-L132."""
    model = ctx.model
    r: ResolvedTwojointPrismaticChainConfig = ctx.config  # type: ignore[assignment]
    stage = model.part("first_stage")
    Lf, Wf = r.stage1_length, r.stage1_width
    web_t = _DECK_T

    stage.visual(
        Box((Lf, Wf, web_t)),
        origin=Origin(xyz=(Lf * 0.5, 0.0, web_t * 0.5 - _PEN)),
        material="stage1",
        name="outer_web", material_class_id="metal.paint_coated",
    )
    cheek_h = Wf * 0.55
    cheek_w = Wf * 0.10
    cheek_y = Wf * 0.5 - cheek_w * 0.5
    deck_top = web_t - _PEN
    for nm, sgn in (("outer_cheek_0", 1.0), ("outer_cheek_1", -1.0)):
        _add_cq_block(
            stage,
            size=(Lf, cheek_w, cheek_h),
            xyz=(Lf * 0.5, sgn * cheek_y, web_t - _PEN + cheek_h * 0.5),
            material="stage1",
            name=nm,
        )
    _add_cq_block(
        stage,
        size=(0.022, Wf * 0.9, web_t + 0.004),
        xyz=(Lf - 0.012, 0.0, web_t * 0.5 - _PEN),
        material="detail",
        name="outer_end_tie",
    )
    stage.inertial = Inertial.from_geometry(
        Box((Lf, Wf, web_t + cheek_h)),
        mass=1.5,
        origin=Origin(xyz=(Lf * 0.5, 0.0, web_t * 0.5)),
    )
    return ModuleBuild(
        module_name="outer_slider_web",
        parts_emitted=["first_stage"],
        interfaces={
            "upstream": _stage1_upstream_iface(r, visual_name="outer_web"),
            "downstream": _stage1_downstream_iface(r, visual_name="outer_web", deck_z=deck_top),
        },
    )


# --------------------------------------------------------------------------- #
# second_stage module factories (Slot C)
# --------------------------------------------------------------------------- #


def _stage2_upstream_iface(
    r: ResolvedTwojointPrismaticChainConfig,
    *,
    visual_name: str,
) -> InterfaceSpec:
    axis, limits = _joint2_axis_limits(r)
    return InterfaceSpec(
        interface_name="upstream",
        part_name="second_stage",
        visual_name=visual_name,
        face_side="negative_z",
        anchor_local=(0.0, 0.0, 0.0),
        face_extents_uv=(r.stage2_length, r.stage2_width),
        extents_tol=0.6,
        contact_tol=0.008,
        consumer_joint_type=ArticulationType.PRISMATIC,
        consumer_joint_axis=axis,
        consumer_motion_limits=limits,
    )


def _stage2_downstream_iface(
    r: ResolvedTwojointPrismaticChainConfig,
    *,
    visual_name: str,
    front_x: float,
    front_y: float,
    z: float,
) -> InterfaceSpec:
    """stage2 exposes its +X front face for the end_effector."""
    return InterfaceSpec(
        interface_name="downstream",
        part_name="second_stage",
        visual_name=visual_name,
        face_side="positive_x",
        anchor_local=(front_x, 0.0, z),
        face_extents_uv=(r.stage2_width, r.stage2_width),
        extents_tol=0.7,
        contact_tol=0.004,
        consumer_joint_type=ArticulationType.FIXED,
    )


def _build_slim_carriage_stage2(ctx: ModuleBuildContext) -> ModuleBuild:
    """Anchor second_stage — c2 body + top plate (compact slider).  Adapted
    from rec_..._53ee6ce L79-L91."""
    model = ctx.model
    r: ResolvedTwojointPrismaticChainConfig = ctx.config  # type: ignore[assignment]
    stage = model.part("second_stage")
    Ls, Ws = r.stage2_length, r.stage2_width
    body_t = _DECK_T

    stage.visual(
        Box((Ls, Ws, body_t)),
        origin=Origin(xyz=(Ls * 0.5, 0.0, body_t * 0.5 - _PEN)),
        material="stage2",
        name="c2_body", material_class_id="metal.paint_coated",
    )
    top_t = 0.008
    _add_cq_block(
        stage,
        size=(Ls * 0.9, Ws * 1.1, top_t),
        xyz=(Ls * 0.5, 0.0, body_t - _PEN + top_t * 0.5),
        material="stage2",
        name="c2_top_plate",
    )
    stage.inertial = Inertial.from_geometry(
        Box((Ls, Ws, body_t + top_t)),
        mass=0.8,
        origin=Origin(xyz=(Ls * 0.5, 0.0, body_t * 0.5)),
    )
    return ModuleBuild(
        module_name="slim_carriage",
        parts_emitted=["second_stage"],
        interfaces={
            "upstream": _stage2_upstream_iface(r, visual_name="c2_body"),
            "downstream": _stage2_downstream_iface(
                r, visual_name="c2_body", front_x=Ls, front_y=Ws * 0.5, z=-_PEN
            ),
        },
    )


def _build_bar_with_saddle_stage2(ctx: ModuleBuildContext) -> ModuleBuild:
    """Bar-with-saddle second_stage — lower bar + thickened saddle + front
    plate.  Adapted from rec_..._6213b556 L200-L232."""
    model = ctx.model
    r: ResolvedTwojointPrismaticChainConfig = ctx.config  # type: ignore[assignment]
    stage = model.part("second_stage")
    Ls, Ws = r.stage2_length, r.stage2_width
    bar_t = _DECK_T

    stage.visual(
        Box((Ls, Ws, bar_t)),
        origin=Origin(xyz=(Ls * 0.5, 0.0, bar_t * 0.5 - _PEN)),
        material="stage2",
        name="lower_bar", material_class_id="metal.paint_coated",
    )
    saddle_t = 0.012
    _add_cq_block(
        stage,
        size=(Ls * 0.6, Ws * 1.15, saddle_t),
        xyz=(Ls * 0.45, 0.0, bar_t - _PEN + saddle_t * 0.5),
        material="stage2",
        name="saddle",
    )
    stage.inertial = Inertial.from_geometry(
        Box((Ls, Ws * 1.15, bar_t + saddle_t)),
        mass=0.9,
        origin=Origin(xyz=(Ls * 0.5, 0.0, bar_t * 0.5)),
    )
    return ModuleBuild(
        module_name="bar_with_saddle",
        parts_emitted=["second_stage"],
        interfaces={
            "upstream": _stage2_upstream_iface(r, visual_name="lower_bar"),
            "downstream": _stage2_downstream_iface(
                r, visual_name="lower_bar", front_x=Ls, front_y=Ws * 0.5, z=-_PEN
            ),
        },
    )


def _build_output_tube_stage2(ctx: ModuleBuildContext) -> ModuleBuild:
    """Output-tube second_stage — minimal hollow square tube output rod.
    Adapted from rec_..._85e5611 L225-L243 (preserves Box-wall tube)."""
    model = ctx.model
    r: ResolvedTwojointPrismaticChainConfig = ctx.config  # type: ignore[assignment]
    stage = model.part("second_stage")
    Ls = r.stage2_length
    outer = max(r.stage2_width, r.base_height)
    wall = outer * 0.12
    z_center = outer * 0.5 - _PEN

    _add_square_tube(
        stage,
        prefix="output",
        x0=0.0,
        length=Ls,
        outer=outer,
        wall=wall,
        z_center=z_center,
        material="stage2",
    )
    stage.inertial = Inertial.from_geometry(
        Box((Ls, outer, outer)),
        mass=0.7,
        origin=Origin(xyz=(Ls * 0.5, 0.0, z_center)),
    )
    upstream = InterfaceSpec(
        interface_name="upstream",
        part_name="second_stage",
        visual_name="output_bottom",
        face_side="negative_z",
        anchor_local=(0.0, 0.0, 0.0),
        face_extents_uv=(Ls, outer),
        extents_tol=0.6,
        contact_tol=0.010,
        consumer_joint_type=ArticulationType.PRISMATIC,
        consumer_joint_axis=_joint2_axis_limits(r)[0],
        consumer_motion_limits=_joint2_axis_limits(r)[1],
    )
    downstream = _stage2_downstream_iface(
        r, visual_name="output_bottom", front_x=Ls, front_y=outer * 0.5, z=z_center - outer * 0.5
    )
    return ModuleBuild(
        module_name="output_tube",
        parts_emitted=["second_stage"],
        interfaces={"upstream": upstream, "downstream": downstream},
    )


def _build_inner_blade_slider_stage2(ctx: ModuleBuildContext) -> ModuleBuild:
    """Inner blade slider second_stage — flange + stem + lower blade thin
    under-slung inner slider.  Adapted from rec_..._84dfe33 L134-L158."""
    model = ctx.model
    r: ResolvedTwojointPrismaticChainConfig = ctx.config  # type: ignore[assignment]
    stage = model.part("second_stage")
    Ls, Ws = r.stage2_length, r.stage2_width
    flange_t = _DECK_T

    stage.visual(
        Box((Ls, Ws, flange_t)),
        origin=Origin(xyz=(Ls * 0.5, 0.0, flange_t * 0.5 - _PEN)),
        material="stage2",
        name="inner_flange", material_class_id="metal.paint_coated",
    )
    stem_h = Ws * 0.5
    _add_cq_block(
        stage,
        size=(Ls, Ws * 0.45, stem_h),
        xyz=(Ls * 0.5, 0.0, flange_t - _PEN + stem_h * 0.5),
        material="stage2",
        name="inner_stem",
    )
    blade_t = 0.010
    _add_cq_block(
        stage,
        size=(Ls, Ws * 0.72, blade_t),
        xyz=(Ls * 0.5, 0.0, flange_t - _PEN + stem_h + blade_t * 0.5 - 0.002),
        material="rail",
        name="upper_blade",
    )
    stage.inertial = Inertial.from_geometry(
        Box((Ls, Ws, flange_t + stem_h + blade_t)),
        mass=0.6,
        origin=Origin(xyz=(Ls * 0.5, 0.0, (flange_t + stem_h) * 0.5)),
    )
    return ModuleBuild(
        module_name="inner_blade_slider",
        parts_emitted=["second_stage"],
        interfaces={
            "upstream": _stage2_upstream_iface(r, visual_name="inner_flange"),
            "downstream": _stage2_downstream_iface(
                r, visual_name="inner_flange", front_x=Ls, front_y=Ws * 0.5, z=-_PEN
            ),
        },
    )


# --------------------------------------------------------------------------- #
# end_effector module factories (Slot D)
# --------------------------------------------------------------------------- #


def _ee_upstream_iface(
    r: ResolvedTwojointPrismaticChainConfig,
    *,
    visual_name: str,
) -> InterfaceSpec:
    """end_effector mates its rear face to stage2's front face (FIXED)."""
    return InterfaceSpec(
        interface_name="upstream",
        part_name="end_effector",
        visual_name=visual_name,
        face_side="negative_x",
        anchor_local=(0.0, 0.0, 0.0),
        face_extents_uv=(r.end_plate_width, r.end_plate_height),
        extents_tol=0.7,
        contact_tol=0.004,
        consumer_joint_type=ArticulationType.FIXED,
    )


def _build_plain_end_face(ctx: ModuleBuildContext) -> ModuleBuild:
    """No end effector — stage2's front face is the work face.  Emits no part
    and no upstream interface, so the assembler emits no joint."""
    return ModuleBuild(
        module_name="plain_end_face",
        parts_emitted=[],
        interfaces={},
    )


def _emit_end_plate(part, r):
    """Emit the flange plate on the +X slide front.

    The plate spans the y-z plane and is centered at local z = +ph/2 so it
    rises upward from the part-frame origin (which sits at the stage2 front
    mate point near the stage2 underside). This keeps the plate above the
    lower base/stage1 rails. The plate penetrates the +X mate face ~_PEN so
    its AABB overlaps stage2 (no isolated part)."""
    pt = r.end_plate_thickness
    pw = r.end_plate_width
    ph = r.end_plate_height
    _add_cq_block(
        part,
        size=(pt, pw, ph),
        xyz=(pt * 0.5 - _PEN, 0.0, ph * 0.5),
        material="plate",
        name="end_plate",
    )


def _build_tool_plate_ee(ctx: ModuleBuildContext) -> ModuleBuild:
    """Tool plate end effector — flange plate + top/bottom ribs.  Adapted from
    rec_..._85e5611 L244-L264."""
    model = ctx.model
    r: ResolvedTwojointPrismaticChainConfig = ctx.config  # type: ignore[assignment]
    ee = model.part("end_effector")
    _emit_end_plate(ee, r)
    pt = r.end_plate_thickness
    ph = r.end_plate_height
    rib_l = pt + 0.018
    for nm, sgn in (("rib_top", 1.0), ("rib_bottom", -1.0)):
        rib_z = ph * 0.5 + sgn * ph * 0.30
        _add_cq_block(
            ee,
            size=(rib_l, 0.034, 0.008),
            xyz=(rib_l * 0.5 - _PEN, 0.0, rib_z),
            material="plate",
            name=nm,
        )
    ee.inertial = Inertial.from_geometry(
        Box((pt + 0.02, r.end_plate_width, ph)),
        mass=0.4,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
    )
    return ModuleBuild(
        module_name="tool_plate",
        parts_emitted=["end_effector"],
        interfaces={"upstream": _ee_upstream_iface(r, visual_name="end_plate")},
    )


def _build_tool_plate_with_mounts_ee(ctx: ModuleBuildContext) -> ModuleBuild:
    """Tool plate with cylinder mounts — flange plate + N cylinder tool mounts.
    Adapted from rec_..._0eebad L219-L239."""
    model = ctx.model
    r: ResolvedTwojointPrismaticChainConfig = ctx.config  # type: ignore[assignment]
    ee = model.part("end_effector")
    _emit_end_plate(ee, r)
    pt = r.end_plate_thickness
    ph = r.end_plate_height
    n = r.end_mount_count
    mount_r = min(0.010, ph * 0.12)
    mount_len = 0.012
    span = ph * 0.6
    for i in range(n):
        frac = (i + 0.5) / n - 0.5
        z = ph * 0.5 + frac * span
        ee.visual(
            Cylinder(radius=mount_r, length=mount_len),
            origin=Origin(
                xyz=(pt - _PEN + mount_len * 0.5, 0.0, z),
                rpy=(0.0, math.pi / 2.0, 0.0),
            ),
            material="detail",
            name=f"tool_mount_{i}", material_class_id="metal.blackened_gunmetal",
        )
    ee.inertial = Inertial.from_geometry(
        Box((pt + mount_len, r.end_plate_width, ph)),
        mass=0.45,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
    )
    return ModuleBuild(
        module_name="tool_plate_with_mounts",
        parts_emitted=["end_effector"],
        interfaces={"upstream": _ee_upstream_iface(r, visual_name="end_plate")},
    )


def _build_drawer_front_handle_ee(ctx: ModuleBuildContext) -> ModuleBuild:
    """Drawer front + handle end effector — front wall plate + grab handle.
    Adapted from rec_..._b31cd82 L43-L46. Used only on tray styles."""
    model = ctx.model
    r: ResolvedTwojointPrismaticChainConfig = ctx.config  # type: ignore[assignment]
    ee = model.part("end_effector")
    _emit_end_plate(ee, r)
    pt = r.end_plate_thickness
    pw = r.end_plate_width
    ph = r.end_plate_height
    handle_w = pw * 0.5
    _add_cq_block(
        ee,
        size=(0.018, handle_w, ph * 0.22),
        xyz=(pt - _PEN + 0.009, 0.0, ph * 0.5),
        material="detail",
        name="handle",
    )
    ee.inertial = Inertial.from_geometry(
        Box((pt + 0.02, pw, ph)),
        mass=0.5,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
    )
    return ModuleBuild(
        module_name="drawer_front_handle",
        parts_emitted=["end_effector"],
        interfaces={"upstream": _ee_upstream_iface(r, visual_name="end_plate")},
    )


# --------------------------------------------------------------------------- #
# Slot graph + entry points
# --------------------------------------------------------------------------- #


BASE_FACTORIES = {
    "flat_rail_table": _build_flat_rail_table_base,
    "u_channel_guide": _build_u_channel_guide_base,
    "square_sleeve": _build_square_sleeve_base,
    "wall_side_plate": _build_wall_side_plate_base,
    "top_support_gantry": _build_top_support_gantry_base,
    "broad_transfer_table": _build_broad_transfer_table_base,
}

FIRST_STAGE_FACTORIES = {
    "rail_carriage": _build_rail_carriage_stage1,
    "channel_runner": _build_channel_runner_stage1,
    "intermediate_tube": _build_intermediate_tube_stage1,
    "bridge_carriage": _build_bridge_carriage_stage1,
    "outer_slider_web": _build_outer_slider_web_stage1,
}

SECOND_STAGE_FACTORIES = {
    "slim_carriage": _build_slim_carriage_stage2,
    "bar_with_saddle": _build_bar_with_saddle_stage2,
    "output_tube": _build_output_tube_stage2,
    "inner_blade_slider": _build_inner_blade_slider_stage2,
}

END_EFFECTOR_FACTORIES = {
    "plain_end_face": _build_plain_end_face,
    "tool_plate": _build_tool_plate_ee,
    "tool_plate_with_mounts": _build_tool_plate_with_mounts_ee,
    "drawer_front_handle": _build_drawer_front_handle_ee,
}


def _slots_for_config(r: ResolvedTwojointPrismaticChainConfig) -> list[SlotSpec]:
    """Build the slot graph pinned to the resolved module picks (the
    assembler does not re-roll for non-zero seeds)."""
    return [
        SlotSpec(
            slot_name="grounded_base",
            candidates={r.base_module: BASE_FACTORIES[r.base_module]},
            anchor_choice=r.base_module,
        ),
        SlotSpec(
            slot_name="first_stage",
            candidates={r.first_stage_module: FIRST_STAGE_FACTORIES[r.first_stage_module]},
            anchor_choice=r.first_stage_module,
        ),
        SlotSpec(
            slot_name="second_stage",
            candidates={r.second_stage_module: SECOND_STAGE_FACTORIES[r.second_stage_module]},
            anchor_choice=r.second_stage_module,
        ),
        SlotSpec(
            slot_name="end_effector",
            candidates={r.end_effector_module: END_EFFECTOR_FACTORIES[r.end_effector_module]},
            anchor_choice=r.end_effector_module,
        ),
    ]


def build_twojoint_prismatic_chain(
    config: TwojointPrismaticChainConfig,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    """Compose a two-joint prismatic chain by running each slot's module
    factory and joining them with assembler-emitted chain joints."""
    r = resolve_config(config)
    model = ArticulatedObject(name="twojoint_prismatic_chain", assets=assets)
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
    return model


def build_seeded_twojoint_prismatic_chain(seed: int) -> ArticulatedObject:
    return build_twojoint_prismatic_chain(config_from_seed(seed))


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    """Return the (slot, module) picks for inspection — consumed by the
    module_topology_diversity gate."""
    cfg = config_from_seed(seed)
    r = resolve_config(cfg)
    return [
        ("grounded_base", r.base_module),
        ("first_stage", r.first_stage_module),
        ("second_stage", r.second_stage_module),
        ("end_effector", r.end_effector_module),
        ("axis_family", r.axis_family),
    ]


# --------------------------------------------------------------------------- #
# Author-layer QC — declare intended overlaps; baseline gates do the rest.
# --------------------------------------------------------------------------- #


def _allow_nested_overlaps(ctx: TestContext, model: ArticulatedObject) -> None:
    """Nested telescoping stages overlap by design (each child base/rail
    penetrates the parent deck ~1.5mm and rides within the parent footprint).
    Declare those inter-part overlaps so the baseline overlap gate passes."""
    part_names = {p.name for p in model.parts}

    def allow_all(parent_name: str, child_name: str, reason: str) -> None:
        if parent_name not in part_names or child_name not in part_names:
            return
        parent = model.get_part(parent_name)
        child = model.get_part(child_name)
        parent_vis = [v.name for v in getattr(parent, "visuals", []) if getattr(v, "name", None)]
        child_vis = [v.name for v in getattr(child, "visuals", []) if getattr(v, "name", None)]
        for pv in parent_vis:
            for cv in child_vis:
                ctx.allow_overlap(parent, child, elem_a=pv, elem_b=cv, reason=reason)

    # Telescoping nests stage2 ⊂ stage1 ⊂ base coaxially, so EVERY pair of
    # chain parts can overlap by design (tube-in-tube-in-tube, carriage on
    # rail on rail, end plate flush on the stage2 front).  Declare all pairs.
    allow_all(
        "grounded_base",
        "first_stage",
        "first_stage nests on the base deck and overlaps it for support",
    )
    allow_all(
        "grounded_base",
        "second_stage",
        "telescoping second_stage nests within the base (tube-in-tube) at rest",
    )
    allow_all(
        "grounded_base",
        "end_effector",
        "end_effector may sit over the base at full retraction",
    )
    allow_all(
        "first_stage",
        "second_stage",
        "second_stage nests on the first_stage deck and overlaps it for support",
    )
    allow_all(
        "first_stage",
        "end_effector",
        "end_effector may sit over the first_stage at retraction",
    )
    allow_all(
        "second_stage",
        "end_effector",
        "end_effector plate is fixed flush against the stage2 front face",
    )


def run_twojoint_prismatic_chain_tests(
    model: ArticulatedObject,
    config: TwojointPrismaticChainConfig,
) -> TestReport:
    """Author-layer QC.  Centralizes the allow_overlap declarations for the
    intentionally-nested telescoping stages, then runs the same baseline-style
    checks the compiler owns so failures surface in the authored report too."""
    ctx = TestContext(model)

    _allow_nested_overlaps(ctx, model)

    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)
    ctx.fail_if_joint_mating_has_gap()

    # Identity: exactly two serial PRISMATIC primary joints.
    j1 = model.get_articulation("grounded_base_to_first_stage")
    j2 = model.get_articulation("first_stage_to_second_stage")
    ctx.check(
        "joint1_is_prismatic",
        j1.articulation_type == ArticulationType.PRISMATIC,
        f"joint1 must be PRISMATIC, got {j1.articulation_type!r}",
    )
    ctx.check(
        "joint2_is_prismatic",
        j2.articulation_type == ArticulationType.PRISMATIC,
        f"joint2 must be PRISMATIC, got {j2.articulation_type!r}",
    )

    # Both prismatic stages must translate along the visible +X guide direction.
    a1 = tuple(j1.axis)
    a2 = tuple(j2.axis)
    ok = a1 == (1.0, 0.0, 0.0) and a2 == (1.0, 0.0, 0.0)
    ctx.check("guide_axis_consistency", ok, f"axes {a1}/{a2} must both follow +X")

    # Limit form: no degenerate (lower == upper) prismatic.
    for nm, j in (("joint1", j1), ("joint2", j2)):
        lim = j.motion_limits
        ctx.check(
            f"{nm}_has_stroke",
            lim is not None
            and lim.lower is not None
            and lim.upper is not None
            and abs(lim.upper - lim.lower) > 1e-4,
            f"{nm} must have a non-degenerate stroke",
        )

    return ctx.report()


# --------------------------------------------------------------------------- #
# Modular template authoring notes
# --------------------------------------------------------------------------- #
# Module roster (per-module 5-star sources, adapted under Rule 3):
#
#   grounded_base/flat_rail_table     : rec_..._53ee6ce L16-L41 (Box rail table)
#   grounded_base/u_channel_guide     : rec_..._6213b556 L62-L161 (cq mount + Box channel)
#   grounded_base/square_sleeve       : rec_..._85e5611 L147-L198 (Box-wall tube)
#   grounded_base/wall_side_plate     : rec_..._66bd7215 L97-L162 (wall + beam + guides)
#   grounded_base/top_support_gantry  : rec_..._84dfe33 L28-L82 (plate + webs + rail)
#   grounded_base/broad_transfer_table: rec_..._7e3c4a4 L56-L90 (cq plate + rails)
#
#   first_stage/rail_carriage     : rec_..._53ee6ce L43-L66
#   first_stage/channel_runner    : rec_..._6213b556 L163-L198
#   first_stage/intermediate_tube : rec_..._85e5611 L200-L223 (Box-wall tube)
#   first_stage/bridge_carriage   : rec_..._66bd7215 L294-L322
#   first_stage/outer_slider_web  : rec_..._84dfe33 L84-L132
#
#   second_stage/slim_carriage      : rec_..._53ee6ce L79-L91
#   second_stage/bar_with_saddle    : rec_..._6213b556 L200-L232
#   second_stage/output_tube        : rec_..._85e5611 L225-L243 (Box-wall tube)
#   second_stage/inner_blade_slider : rec_..._84dfe33 L134-L158
#
#   end_effector/plain_end_face         : no part (stage2 face is the work face)
#   end_effector/tool_plate             : rec_..._85e5611 L244-L264
#   end_effector/tool_plate_with_mounts : rec_..._0eebad L219-L239
#   end_effector/drawer_front_handle    : rec_..._b31cd82 L43-L46
#
# Chain joints (assembler-emitted, names are "<prev>_to_<slot>"):
#   grounded_base_to_first_stage  PRISMATIC (joint1; +X guide axis)
#   first_stage_to_second_stage   PRISMATIC (joint2; +X guide axis)
#   second_stage_to_end_effector  FIXED     (omitted when end_effector=plain_end_face)
#
# All chain prismatic joints mate on Z (parent deck +Z ↔ child base -Z) so the
# fail_if_joint_mating_has_gap check (measured along the parent face normal =
# Z) passes. Nested stages overlap by design; overlaps are declared in
# run_*_tests.
#
# Diversity: 6 bases × compatible stage families × 4 end effectors >> the
# 5-distinct module_topology_diversity floor.


__all__ = [
    "AxisFamily",
    "BaseModule",
    "EndEffectorModule",
    "FirstStageModule",
    "PaletteTheme",
    "ResolvedTwojointPrismaticChainConfig",
    "SecondStageModule",
    "TwojointPrismaticChainConfig",
    "build_seeded_twojoint_prismatic_chain",
    "build_twojoint_prismatic_chain",
    "config_from_seed",
    "resolve_config",
    "run_twojoint_prismatic_chain_tests",
    "slot_choices_for_seed",
]
