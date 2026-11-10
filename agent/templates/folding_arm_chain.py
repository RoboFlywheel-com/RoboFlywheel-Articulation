# SPDX-License-Identifier: Apache-2.0

"""Modular procedural template for folding arm chains.

The reviewed modular spec for ``folding_arm_chain`` identifies two real 5-star
subfamilies: planar stacked pierced-plate stays, and side-mounted clevis/fork
chains. This implementation keeps that split explicit in ``axis_family`` and
only samples combinations that have compatible hinge interfaces.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, replace
from typing import Literal

import cadquery as cq

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    ExtrudeWithHolesGeometry,
    MatingContract,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
    mesh_from_geometry,
    rounded_rect_profile,
)

__modular__ = True

RootSupport = Literal[
    "compact_service_plate",
    "four_bolt_flat_foot",
    "bridge_hanger_clevis",
    "underslung_top_bracket",
    "hatch_base_lug",
    "low_profile_root_plate",
]
ChainMultiplicity = Literal[
    "two_link_service_chain",
    "three_link_stay_chain",
    "four_flat_bar_chain",
    "four_link_end_bracket_chain",
    "five_link_slot_stack_chain",
]
LinkProfile = Literal[
    "slotted_flat_bar",
    "forked_bar_link",
    "tapered_bridge_link",
    "rounded_side_plate_link",
    "boxed_distal_yoke",
    "twin_strap_inspection_link",
]
TerminalModule = Literal[
    "service_plate",
    "tool_plate",
    "integral_end_pad",
    "triangular_end_shoe",
    "hook_tab",
    "heavy_end_bracket",
]
AxisFamily = Literal["z_planar_stack", "y_clevis_stack", "heavy_twin_strap"]
MaterialStyle = Literal["dark_service", "raw_fixture", "bronze_bushed", "safety_yellow"]

ROOTS: tuple[RootSupport, ...] = (
    "compact_service_plate",
    "four_bolt_flat_foot",
    "bridge_hanger_clevis",
    "underslung_top_bracket",
    "hatch_base_lug",
    "low_profile_root_plate",
)
CHAINS: tuple[ChainMultiplicity, ...] = (
    "two_link_service_chain",
    "three_link_stay_chain",
    "four_flat_bar_chain",
    "four_link_end_bracket_chain",
    "five_link_slot_stack_chain",
)
LINK_PROFILES: tuple[LinkProfile, ...] = (
    "slotted_flat_bar",
    "forked_bar_link",
    "tapered_bridge_link",
    "rounded_side_plate_link",
    "boxed_distal_yoke",
    "twin_strap_inspection_link",
)
TERMINALS: tuple[TerminalModule, ...] = (
    "service_plate",
    "tool_plate",
    "integral_end_pad",
    "triangular_end_shoe",
    "hook_tab",
    "heavy_end_bracket",
)
AXIS_FAMILIES: tuple[AxisFamily, ...] = ("z_planar_stack", "y_clevis_stack", "heavy_twin_strap")
MATERIAL_STYLES: tuple[MaterialStyle, ...] = (
    "dark_service",
    "raw_fixture",
    "bronze_bushed",
    "safety_yellow",
)

_AXIS_COMPAT: dict[AxisFamily, dict[str, tuple[str, ...]]] = {
    "z_planar_stack": {
        "roots": ("compact_service_plate", "four_bolt_flat_foot", "low_profile_root_plate"),
        "chains": (
            "two_link_service_chain",
            "four_flat_bar_chain",
            "four_link_end_bracket_chain",
            "five_link_slot_stack_chain",
        ),
        "profiles": ("slotted_flat_bar", "twin_strap_inspection_link"),
        "terminals": (
            "service_plate",
            "tool_plate",
            "integral_end_pad",
            "triangular_end_shoe",
            "heavy_end_bracket",
        ),
    },
    "y_clevis_stack": {
        "roots": ("bridge_hanger_clevis", "underslung_top_bracket", "hatch_base_lug"),
        "chains": ("three_link_stay_chain", "two_link_service_chain"),
        "profiles": (
            "forked_bar_link",
            "tapered_bridge_link",
            "rounded_side_plate_link",
            "boxed_distal_yoke",
        ),
        "terminals": ("integral_end_pad", "hook_tab", "service_plate", "triangular_end_shoe"),
    },
    "heavy_twin_strap": {
        "roots": ("low_profile_root_plate", "four_bolt_flat_foot"),
        "chains": ("four_link_end_bracket_chain", "four_flat_bar_chain"),
        "profiles": ("twin_strap_inspection_link", "slotted_flat_bar"),
        "terminals": ("heavy_end_bracket", "tool_plate", "triangular_end_shoe"),
    },
}

_CHAIN_COUNTS: dict[ChainMultiplicity, int] = {
    "two_link_service_chain": 2,
    "three_link_stay_chain": 3,
    "four_flat_bar_chain": 4,
    "four_link_end_bracket_chain": 4,
    "five_link_slot_stack_chain": 5,
}

_PALETTES: dict[MaterialStyle, dict[str, tuple[float, float, float, float]]] = {
    "dark_service": {
        "base": (0.06, 0.065, 0.07, 1.0),
        "link": (0.13, 0.14, 0.15, 1.0),
        "accent": (0.40, 0.42, 0.42, 1.0),
        "pin": (0.72, 0.70, 0.64, 1.0),
        "pad": (0.015, 0.016, 0.016, 1.0),
    },
    "raw_fixture": {
        "base": (0.32, 0.34, 0.35, 1.0),
        "link": (0.58, 0.60, 0.59, 1.0),
        "accent": (0.18, 0.19, 0.20, 1.0),
        "pin": (0.76, 0.77, 0.74, 1.0),
        "pad": (0.06, 0.06, 0.06, 1.0),
    },
    "bronze_bushed": {
        "base": (0.22, 0.23, 0.24, 1.0),
        "link": (0.52, 0.43, 0.28, 1.0),
        "accent": (0.76, 0.56, 0.25, 1.0),
        "pin": (0.84, 0.78, 0.62, 1.0),
        "pad": (0.05, 0.04, 0.03, 1.0),
    },
    "safety_yellow": {
        "base": (0.18, 0.19, 0.20, 1.0),
        "link": (0.88, 0.62, 0.12, 1.0),
        "accent": (0.08, 0.08, 0.08, 1.0),
        "pin": (0.70, 0.72, 0.72, 1.0),
        "pad": (0.02, 0.02, 0.018, 1.0),
    },
}


@dataclass(frozen=True)
class FoldingArmChainConfig:
    root_support: RootSupport | None = None
    chain_multiplicity: ChainMultiplicity | None = None
    link_profile: LinkProfile | None = None
    terminal_module: TerminalModule | None = None
    axis_family: AxisFamily | None = None
    material_style: MaterialStyle = "dark_service"
    reach: float = 0.78
    link_width: float = 0.070
    plate_thickness: float = 0.010
    hinge_radius: float = 0.020
    joint_limit_scale: float = 1.0
    name: str = "folding_arm_chain"


@dataclass(frozen=True)
class ResolvedFoldingArmChainConfig:
    root_support: RootSupport
    chain_multiplicity: ChainMultiplicity
    link_profile: LinkProfile
    terminal_module: TerminalModule
    axis_family: AxisFamily
    material_style: MaterialStyle
    link_count: int
    lengths: tuple[float, ...]
    link_width: float
    link_height: float
    plate_thickness: float
    hinge_radius: float
    root_origin: tuple[float, float, float]
    joint_axis: tuple[float, float, float]
    joint_limits: tuple[float, float]
    moving_terminal: bool
    name: str


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


# Maximum cumulative same-sign fold (radians) of the WHOLE serial chain before a
# distal link curls back through the ~360 deg loop into the root/base envelope near
# the origin. A serial revolute chain anchored at the origin only returns near its
# anchor as the accumulated turning approaches 2*pi; keeping the worst-case sum of
# every joint's magnitude below this budget guarantees the arc stays clear of the
# base for ALL motion-QC pose combinations (the max |cumulative turn| over any combo
# is the all-same-sign sum). ~239 deg leaves generous chord clearance vs the small
# base footprint even for the shortest links.
_FOLD_TURN_BUDGET = 4.18
# Terminal hinge is limited to this fraction of a chain-joint limit (see the terminal
# articulation below); it contributes the same fraction to the cumulative fold.
_TERMINAL_LIMIT_FRAC = 0.72


def _safe_joint_limit(
    base_limit: float,
    link_count: int,
    moving_terminal: bool,
    scale: float,
) -> float:
    """Single-source symmetric per-joint limit (Contract 3c).

    The returned magnitude ``A`` is shared by every chain revolute joint; the
    optional terminal hinge uses ``A * _TERMINAL_LIMIT_FRAC``. The cap enforces
    ``A * (link_count + _TERMINAL_LIMIT_FRAC[if terminal]) <= _FOLD_TURN_BUDGET`` so
    the fully-folded stack cannot wrap back into the base, independent of ``scale``.
    """
    fold_segments = link_count + (_TERMINAL_LIMIT_FRAC if moving_terminal else 0.0)
    cap = _FOLD_TURN_BUDGET / fold_segments
    return min(base_limit * scale, cap)


def _pick(value, choices):
    return value if value in choices else choices[0]


def _axis_for_choices(
    root: RootSupport | None,
    chain: ChainMultiplicity | None,
    profile: LinkProfile | None,
    terminal: TerminalModule | None,
    requested: AxisFamily | None,
) -> AxisFamily:
    candidates = list(AXIS_FAMILIES) if requested not in AXIS_FAMILIES else [requested]
    for axis in candidates:
        compat = _AXIS_COMPAT[axis]
        if root and root not in compat["roots"]:
            continue
        if chain and chain not in compat["chains"]:
            continue
        if profile and profile not in compat["profiles"]:
            continue
        if terminal and terminal not in compat["terminals"]:
            continue
        return axis
    if profile in (
        "forked_bar_link",
        "tapered_bridge_link",
        "rounded_side_plate_link",
        "boxed_distal_yoke",
    ):
        return "y_clevis_stack"
    if root in ("bridge_hanger_clevis", "underslung_top_bracket", "hatch_base_lug"):
        return "y_clevis_stack"
    if chain == "five_link_slot_stack_chain":
        return "z_planar_stack"
    if chain == "four_link_end_bracket_chain" or profile == "twin_strap_inspection_link":
        return "heavy_twin_strap"
    return "z_planar_stack"


def config_from_seed(seed: int) -> FoldingArmChainConfig:
    rng = random.Random(seed)
    axis = rng.choices(
        AXIS_FAMILIES,
        weights=(0.42, 0.38, 0.20),
        k=1,
    )[0]
    compat = _AXIS_COMPAT[axis]
    return FoldingArmChainConfig(
        axis_family=axis,
        root_support=rng.choice(compat["roots"]),
        chain_multiplicity=rng.choice(compat["chains"]),
        link_profile=rng.choice(compat["profiles"]),
        terminal_module=rng.choice(compat["terminals"]),
        material_style=rng.choice(MATERIAL_STYLES),
        reach=rng.uniform(0.48, 1.08),
        link_width=rng.uniform(0.052, 0.092),
        plate_thickness=rng.uniform(0.007, 0.014),
        hinge_radius=rng.uniform(0.015, 0.027),
        joint_limit_scale=rng.uniform(0.78, 1.18),
        name=f"seeded_folding_arm_chain_{seed}",
    )


def resolve_config(config: FoldingArmChainConfig | None = None) -> ResolvedFoldingArmChainConfig:
    cfg = config or FoldingArmChainConfig()
    axis = _axis_for_choices(
        cfg.root_support,
        cfg.chain_multiplicity,
        cfg.link_profile,
        cfg.terminal_module,
        cfg.axis_family,
    )
    compat = _AXIS_COMPAT[axis]
    root = _pick(cfg.root_support, compat["roots"])
    chain = _pick(cfg.chain_multiplicity, compat["chains"])
    profile = _pick(cfg.link_profile, compat["profiles"])
    terminal = _pick(cfg.terminal_module, compat["terminals"])
    if chain == "five_link_slot_stack_chain":
        profile = "slotted_flat_bar"
    material_style = _pick(cfg.material_style, MATERIAL_STYLES)

    link_count = _CHAIN_COUNTS[chain]
    reach = _clamp(cfg.reach, 0.42, 1.16)
    width = _clamp(cfg.link_width, 0.046, 0.100)
    plate_t = _clamp(cfg.plate_thickness, 0.0065, 0.016)
    hinge_r = _clamp(cfg.hinge_radius, 0.013, 0.030)
    height = max(width * 0.58, 0.044) if axis != "z_planar_stack" else max(width * 0.30, 0.026)
    weights = [1.0 * (0.91**i) for i in range(link_count)]
    min_len = max(width * 2.9, 0.145)
    lengths = tuple(max(min_len, reach * w / sum(weights)) for w in weights)
    actual = sum(lengths)
    if actual > reach * 1.18:
        scale = reach / actual
        lengths = tuple(max(min_len * 0.94, length * scale) for length in lengths)

    if axis == "z_planar_stack":
        root_origin = (0.0, 0.0, 0.028)
        joint_axis = (0.0, 0.0, 1.0)
        base_limit = 2.35
    else:
        root_origin = (0.0, 0.0, 0.105)
        joint_axis = (0.0, 1.0, 0.0)
        base_limit = 1.72
    if axis == "heavy_twin_strap":
        base_limit = 1.95

    scale = _clamp(cfg.joint_limit_scale, 0.70, 1.25)
    moving_terminal = chain != "five_link_slot_stack_chain" and terminal in (
        "service_plate",
        "tool_plate",
        "triangular_end_shoe",
        "heavy_end_bracket",
    )
    joint_limit = _safe_joint_limit(base_limit, link_count, moving_terminal, scale)

    return ResolvedFoldingArmChainConfig(
        root_support=root,
        chain_multiplicity=chain,
        link_profile=profile,
        terminal_module=terminal,
        axis_family=axis,
        material_style=material_style,
        link_count=link_count,
        lengths=lengths,
        link_width=width,
        link_height=height,
        plate_thickness=plate_t,
        hinge_radius=hinge_r,
        root_origin=root_origin,
        joint_axis=joint_axis,
        joint_limits=(-joint_limit, joint_limit),
        moving_terminal=moving_terminal,
        name=cfg.name or "folding_arm_chain",
    )


def with_overrides(config: FoldingArmChainConfig, **kwargs: object) -> FoldingArmChainConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: FoldingArmChainConfig | ResolvedFoldingArmChainConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedFoldingArmChainConfig) else resolve_config(config)
    return (
        ("root_support", r.root_support),
        ("chain_multiplicity", r.chain_multiplicity),
        ("link_profile", r.link_profile),
        ("terminal_module", r.terminal_module),
        ("axis_family", r.axis_family),
        ("material_style", r.material_style),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


def _circle_profile(
    cx: float,
    cy: float,
    radius: float,
    segments: int = 32,
) -> list[tuple[float, float]]:
    return [
        (
            cx + radius * math.cos(2.0 * math.pi * i / segments),
            cy - radius * math.sin(2.0 * math.pi * i / segments),
        )
        for i in range(segments)
    ]


def _shift(
    profile: list[tuple[float, float]], dx: float, dy: float = 0.0
) -> list[tuple[float, float]]:
    return [(x + dx, y + dy) for x, y in profile]


def _capsule_profile(
    length: float, radius: float, segments_per_end: int = 18
) -> list[tuple[float, float]]:
    points: list[tuple[float, float]] = []
    for i in range(segments_per_end + 1):
        angle = -0.5 * math.pi + math.pi * i / segments_per_end
        points.append((length + radius * math.cos(angle), radius * math.sin(angle)))
    for i in range(segments_per_end + 1):
        angle = 0.5 * math.pi + math.pi * i / segments_per_end
        points.append((radius * math.cos(angle), radius * math.sin(angle)))
    return points


def _plate_mesh(
    *,
    length: float,
    radius: float,
    thickness: float,
    name: str,
    holes: bool = True,
):
    hole_profiles = []
    if holes:
        hole_r = min(radius * 0.42, thickness * 1.8)
        hole_profiles = [_circle_profile(0.0, 0.0, hole_r), _circle_profile(length, 0.0, hole_r)]
    return mesh_from_geometry(
        ExtrudeWithHolesGeometry(
            _capsule_profile(length, radius), hole_profiles, thickness, center=True
        ),
        name,
    )


def _cadquery_slot_link_mesh(
    *,
    length: float,
    width: float,
    thickness: float,
    hole_radius: float,
    name: str,
):
    shape = (
        cq.Workplane("XY")
        .slot2D(length, width)
        .extrude(thickness / 2.0, both=True)
        .faces(">Z")
        .workplane()
        .pushPoints([(-length / 2.0, 0.0)])
        .hole(hole_radius * 2.05)
    )
    return mesh_from_cadquery(shape.translate((length / 2.0, 0.0, 0.0)), name)


def _rounded_rect_mesh(
    *,
    width: float,
    height: float,
    radius: float,
    thickness: float,
    name: str,
    holes: list[tuple[float, float, float]] | None = None,
):
    hole_profiles = [_circle_profile(x, y, r) for x, y, r in (holes or [])]
    return mesh_from_geometry(
        ExtrudeWithHolesGeometry(
            rounded_rect_profile(
                width, height, min(radius, width * 0.48, height * 0.48), corner_segments=8
            ),
            hole_profiles,
            thickness,
            center=True,
        ),
        name,
    )


def _box(part, size, xyz, material, name, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(Box(size), origin=Origin(xyz=xyz, rpy=rpy), material=material, name=name, material_class_id="metal.generic_plain")


def _cyl(part, radius, length, xyz, material, name, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=Origin(xyz=xyz, rpy=rpy),
        material=material,
        name=name, material_class_id="metal.generic_plain",
    )


def _mat(model: ArticulatedObject, r: ResolvedFoldingArmChainConfig, key: str):
    return model.material(f"folding_arm_{key}", rgba=_PALETTES[r.material_style][key])


def _build_base(model: ArticulatedObject, r: ResolvedFoldingArmChainConfig, mats):
    base = model.part("base")
    w = r.link_width
    t = r.plate_thickness
    root_x, _, root_z = r.root_origin

    if r.axis_family in ("z_planar_stack", "heavy_twin_strap"):
        if r.root_support == "compact_service_plate":
            base.visual(
                _rounded_rect_mesh(
                    width=0.205,
                    height=max(0.125, w * 1.55),
                    radius=0.018,
                    thickness=t * 1.22,
                    name="compact_service_base_plate",
                    holes=[
                        (-0.060, -0.035, 0.006),
                        (-0.060, 0.035, 0.006),
                        (0.025, -0.035, 0.006),
                        (0.025, 0.035, 0.006),
                    ],
                ),
                origin=Origin(xyz=(-0.062, 0.0, t * 0.60)),
                material=mats["base"],
                name="base_plate", material_class_id=("metal.paint_coated" if r.material_style in {"dark_service", "bronze_bushed", "safety_yellow"} else "metal.steel_bare"),
            )
        elif r.root_support == "four_bolt_flat_foot":
            _box(
                base,
                (0.255, max(0.145, w * 1.8), t * 1.25),
                (-0.078, 0.0, t * 0.60),
                mats["base"],
                "base_plate",
            )
        else:
            base.visual(
                _rounded_rect_mesh(
                    width=0.300,
                    height=max(0.170, w * 2.25),
                    radius=0.026,
                    thickness=t * 1.30,
                    name="broad_low_profile_root_plate",
                    holes=[
                        (-0.090, -0.052, 0.006),
                        (-0.090, 0.052, 0.006),
                        (0.055, -0.052, 0.006),
                        (0.055, 0.052, 0.006),
                    ],
                ),
                origin=Origin(xyz=(-0.110, 0.0, t * 0.65)),
                material=mats["base"],
                name="mounting_plate", material_class_id=("metal.paint_coated" if r.material_style in {"dark_service", "bronze_bushed", "safety_yellow"} else "metal.steel_bare"),
            )
        for idx, y in enumerate((-w * 0.50, w * 0.50)):
            _cyl(
                base,
                max(0.006, w * 0.095),
                t * 0.55,
                (-0.085, y, t * 1.16),
                mats["pin"],
                f"anchor_bolt_{idx}",
            )
            _cyl(
                base,
                max(0.006, w * 0.095),
                t * 0.55,
                (0.028, y, t * 1.16),
                mats["pin"],
                f"anchor_bolt_{idx + 2}",
            )
        _box(
            base,
            (0.064, w * 1.05, max(0.012, root_z - t * 1.12)),
            (-0.006, 0.0, (root_z + t * 1.12) * 0.5),
            mats["base"],
            "root_pedestal",
        )
        _cyl(
            base,
            r.hinge_radius * 1.12,
            t * 0.72,
            (root_x, 0.0, root_z - t * 0.55),
            mats["pin"],
            "root_boss",
        )
        _box(
            base, (0.030, w * 0.95, t * 0.80), (-0.015, 0.0, root_z), mats["accent"], "root_socket"
        )
    else:
        _box(
            base,
            (0.185, max(0.145, w * 1.7), 0.024),
            (-0.075, 0.0, 0.012),
            mats["base"],
            "wall_foot",
        )
        if r.root_support == "bridge_hanger_clevis":
            _box(base, (0.145, 0.030, 0.140), (-0.045, 0.0, 0.088), mats["base"], "bridge_spine")
            cheek_h = 0.095
        elif r.root_support == "underslung_top_bracket":
            _box(base, (0.210, 0.030, 0.030), (-0.060, 0.0, 0.162), mats["base"], "top_hanger_bar")
            _box(base, (0.045, 0.030, 0.132), (-0.002, 0.0, 0.086), mats["base"], "hanging_web")
            cheek_h = 0.085
        else:
            _box(base, (0.150, 0.030, 0.105), (-0.050, 0.0, 0.074), mats["base"], "hatch_lug_web")
            cheek_h = 0.080
        lane = w * 0.47
        for side, y in (("pos", lane), ("neg", -lane)):
            _box(
                base,
                (0.058, w * 0.22, cheek_h),
                (-0.002, y, root_z),
                mats["base"],
                f"root_cheek_{side}",
            )
            _cyl(
                base,
                r.hinge_radius * 0.56,
                w * 0.26,
                (root_x, y, root_z),
                mats["pin"],
                f"root_bushing_{side}",
                (math.pi / 2.0, 0.0, 0.0),
            )
        _box(base, (0.033, w * 1.18, 0.030), (-0.016, 0.0, root_z), mats["accent"], "root_socket")
        _cyl(
            base,
            r.hinge_radius * 0.45,
            w * 1.18,
            (root_x, 0.0, root_z),
            mats["pin"],
            "root_pin",
            (math.pi / 2.0, 0.0, 0.0),
        )

    return base


def _add_link_interfaces(
    part, r: ResolvedFoldingArmChainConfig, *, length: float, z_offset: float
) -> None:
    w = r.link_width
    depth = max(0.024, r.hinge_radius * 0.95)
    if r.axis_family == "z_planar_stack" or r.axis_family == "heavy_twin_strap":
        _box(
            part,
            (depth, w * 0.76, r.plate_thickness * 0.70),
            (depth * 0.5, 0.0, z_offset),
            None,
            "proximal_hub",
        )
        _box(
            part,
            (depth, w * 0.76, r.plate_thickness * 0.70),
            (length - depth * 0.5, 0.0, z_offset),
            None,
            "distal_socket",
        )
    else:
        _box(
            part,
            (depth, w * 0.62, r.link_height * 0.52),
            (depth * 0.5, 0.0, z_offset),
            None,
            "proximal_hub",
        )
        _box(
            part,
            (depth, w * 0.62, r.link_height * 0.52),
            (length - depth * 0.5, 0.0, z_offset),
            None,
            "distal_socket",
        )


def _add_planar_flat_bar(
    part, r: ResolvedFoldingArmChainConfig, mats, *, length: float, index: int
) -> None:
    radius = r.link_width * (0.44 if r.link_profile == "slotted_flat_bar" else 0.38)
    t = r.plate_thickness
    z = 0.0
    if r.link_profile == "twin_strap_inspection_link":
        lane = r.link_width * 0.45
        mesh = _plate_mesh(
            length=length,
            radius=r.link_width * 0.24,
            thickness=t,
            name=f"link_{index}_twin_strap_plate",
        )
        for side, y in (("pos", lane), ("neg", -lane)):
            part.visual(
                mesh, origin=Origin(xyz=(0.0, y, z)), material=mats["link"], name=f"strap_{side}", material_class_id=("metal.paint_coated" if r.material_style in {"dark_service", "bronze_bushed", "safety_yellow"} else "metal.steel_bare")
            )
            _box(
                part,
                (max(length - 0.090, 0.050), 0.004, t * 0.55),
                (length * 0.5, y, z + t * 0.62),
                mats["accent"],
                f"raised_rib_{side}",
            )
            for x, end in ((0.0, "prox"), (length, "dist")):
                _cyl(
                    part,
                    r.hinge_radius * 0.36,
                    t * 0.50,
                    (x, y, z + t * 0.56),
                    mats["pin"],
                    f"{end}_bushing_{side}",
                )
        span = 2.0 * lane + r.link_width * 0.25
        for frac in (0.31, 0.66):
            _box(
                part,
                (0.032, span, t),
                (length * frac, 0.0, z),
                mats["link"],
                f"strap_tie_{frac:.2f}",
            )
        _box(
            part,
            (length * 0.34, span - 0.022, t * 0.70),
            (length * 0.52, 0.0, z + t * 0.60),
            mats["accent"],
            "inspection_cover",
        )
    else:
        if r.chain_multiplicity == "five_link_slot_stack_chain":
            mesh = _cadquery_slot_link_mesh(
                length=length,
                width=radius * 2.0,
                thickness=t,
                hole_radius=min(radius * 0.42, t * 1.8),
                name=f"link_{index}_cadquery_slot_plate",
            )
        else:
            mesh = _plate_mesh(
                length=length, radius=radius, thickness=t, name=f"link_{index}_slotted_plate"
            )
        part.visual(
            mesh, origin=Origin(xyz=(0.0, 0.0, z)), material=mats["link"], name="slotted_plate", material_class_id=("metal.paint_coated" if r.material_style in {"dark_service", "bronze_bushed", "safety_yellow"} else "metal.steel_bare")
        )
        _box(
            part,
            (max(length - 0.115, 0.045), r.link_width * 0.24, t * 0.52),
            (length * 0.5, 0.0, z + t * 0.75),
            mats["accent"],
            "center_cover_rib",
        )
        for x, end in ((0.0, "prox"), (length, "dist")):
            if r.chain_multiplicity == "five_link_slot_stack_chain" and end == "prox":
                continue
            _cyl(
                part,
                r.hinge_radius * 0.72,
                t * 0.60,
                (x, 0.0, z + t * 0.72),
                mats["pin"],
                f"{end}_pin_boss",
            )
    _add_link_interfaces(part, r, length=length, z_offset=z)


def _add_clevis_link(
    part, r: ResolvedFoldingArmChainConfig, mats, *, length: float, index: int
) -> None:
    w = r.link_width
    h = r.link_height
    body_len = max(length - w * 0.95, w * 1.6)
    if r.link_profile == "rounded_side_plate_link":
        lane = w * 0.39
        mesh = _plate_mesh(
            length=length,
            radius=w * 0.22,
            thickness=max(0.006, r.plate_thickness * 0.82),
            name=f"link_{index}_rounded_side_plate",
        )
        for side, y in (("pos", lane), ("neg", -lane)):
            part.visual(
                mesh,
                origin=Origin(xyz=(0.0, y, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
                material=mats["link"],
                name=f"rounded_side_plate_{side}", material_class_id=("metal.paint_coated" if r.material_style in {"dark_service", "bronze_bushed", "safety_yellow"} else "metal.steel_bare"),
            )
        _box(
            part,
            (body_len * 0.82, w * 0.22, h * 0.22),
            (body_len * 0.52, 0.0, 0.0),
            mats["accent"],
            "center_spacer_web",
        )
        _box(
            part, (0.036, w * 0.96, h * 0.24), (length * 0.56, 0.0, 0.0), mats["link"], "cross_tie"
        )
    elif r.link_profile == "boxed_distal_yoke":
        _box(
            part,
            (body_len, w * 0.46, h * 0.52),
            (body_len * 0.5, 0.0, 0.0),
            mats["link"],
            "boxed_main_beam",
        )
        fork_start = max(length - w * 0.78, body_len * 0.65)
        _box(
            part,
            (w * 0.58, w * 0.54, h * 0.42),
            (length - w * 0.74, 0.0, 0.0),
            mats["link"],
            "boxed_yoke_transition",
        )
        _box(
            part,
            (length - fork_start, w * 0.92, h * 0.28),
            ((fork_start + length) * 0.5, 0.0, h * 0.20),
            mats["link"],
            "distal_yoke_top_bridge",
        )
        for side, y in (("pos", w * 0.39), ("neg", -w * 0.39)):
            _box(
                part,
                (length - fork_start, w * 0.20, h * 0.72),
                ((fork_start + length) * 0.5, y, 0.0),
                mats["link"],
                f"distal_yoke_cheek_{side}",
            )
    elif r.link_profile == "tapered_bridge_link":
        _box(
            part,
            (body_len * 0.42, w * 0.50, h * 0.62),
            (body_len * 0.21, 0.0, 0.0),
            mats["link"],
            "wide_root_web",
        )
        _box(
            part,
            (body_len * 0.36, w * 0.40, h * 0.48),
            (body_len * 0.58, 0.0, 0.0),
            mats["link"],
            "tapered_mid_web",
        )
        _box(
            part,
            (body_len * 0.28, w * 0.31, h * 0.38),
            (body_len * 0.90, 0.0, 0.0),
            mats["link"],
            "narrow_tip_web",
        )
        _box(
            part,
            (w * 0.84, w * 0.96, h * 0.42),
            (length - w * 0.68, 0.0, 0.0),
            mats["link"],
            "tapered_clevis_transition",
        )
        for side, y in (("pos", w * 0.39), ("neg", -w * 0.39)):
            _box(
                part,
                (w * 0.48, w * 0.18, h * 0.76),
                (length - w * 0.24, y, 0.0),
                mats["link"],
                f"tapered_clevis_{side}",
            )
    else:
        _box(
            part,
            (body_len, w * 0.42, h * 0.46),
            (body_len * 0.5, 0.0, 0.0),
            mats["link"],
            "central_box_bar",
        )
        _cyl(
            part,
            h * 0.32,
            w * 0.44,
            (0.0, 0.0, 0.0),
            mats["link"],
            "proximal_round_eye",
            (math.pi / 2.0, 0.0, 0.0),
        )
        for side, y in (("pos", w * 0.40), ("neg", -w * 0.40)):
            _box(
                part,
                (w * 0.70, w * 0.18, h * 0.70),
                (length - w * 0.35, y, 0.0),
                mats["link"],
                f"distal_fork_cheek_{side}",
            )
        _box(
            part,
            (w * 1.12, w * 0.96, h * 0.28),
            (length - w * 0.48, 0.0, -h * 0.18),
            mats["accent"],
            "fork_bridge",
        )

    for x, end in ((0.0, "prox"), (length, "dist")):
        _cyl(
            part,
            r.hinge_radius * 0.55,
            w * 1.05,
            (x, 0.0, 0.0),
            mats["pin"],
            f"{end}_cross_pin",
            (math.pi / 2.0, 0.0, 0.0),
        )
        _cyl(
            part,
            r.hinge_radius * 0.70,
            w * 0.18,
            (x, w * 0.56, 0.0),
            mats["accent"],
            f"{end}_outer_boss_pos",
            (math.pi / 2.0, 0.0, 0.0),
        )
        _cyl(
            part,
            r.hinge_radius * 0.70,
            w * 0.18,
            (x, -w * 0.56, 0.0),
            mats["accent"],
            f"{end}_outer_boss_neg",
            (math.pi / 2.0, 0.0, 0.0),
        )
    _add_link_interfaces(part, r, length=length, z_offset=0.0)


def _add_terminal_visuals(
    part, r: ResolvedFoldingArmChainConfig, mats, *, offset_x: float, local: bool
) -> None:
    w = r.link_width
    t = r.plate_thickness
    z = 0.0
    if local:
        _box(
            part,
            (max(0.025, w * 0.38), w * 0.68, max(t, r.link_height * 0.34)),
            (max(0.012, w * 0.19), 0.0, z),
            mats["link"],
            "proximal_hub",
        )
        base_x = max(0.035, w * 0.54)
        _box(
            part,
            (base_x + w * 0.24, w * 0.50, max(t, r.link_height * 0.30)),
            ((base_x + w * 0.24) * 0.5, 0.0, z),
            mats["link"],
            "terminal_neck",
        )
    else:
        base_x = offset_x + max(0.035, w * 0.54)
        _box(
            part,
            (base_x - offset_x + 0.010, w * 0.44, max(t, r.link_height * 0.30)),
            ((base_x + offset_x) * 0.5, 0.0, z),
            mats["link"],
            "terminal_neck",
        )

    if r.terminal_module == "service_plate":
        part.visual(
            _rounded_rect_mesh(
                width=max(0.125, w * 1.85),
                height=max(0.090, w * 1.20),
                radius=0.012,
                thickness=t,
                name="terminal_service_plate_mesh",
                holes=[(-0.040, 0.0, 0.006), (0.035, -0.026, 0.0045), (0.035, 0.026, 0.0045)],
            ),
            origin=Origin(xyz=(base_x + w * 0.25, 0.0, z)),
            material=mats["accent"],
            name="service_mount_plate", material_class_id=("metal.paint_coated" if r.material_style in {"dark_service", "bronze_bushed", "safety_yellow"} else "metal.blackened_gunmetal"),
        )
        _box(
            part,
            (w * 0.85, w * 0.62, t * 0.75),
            (base_x + w * 0.55, 0.0, z + t * 0.72),
            mats["pad"],
            "rubber_service_pad",
        )
    elif r.terminal_module == "tool_plate":
        _box(
            part,
            (w * 1.45, w * 1.15, max(t, r.link_height * 0.42)),
            (base_x + w * 0.42, 0.0, z),
            mats["accent"],
            "tool_mount_block",
        )
        for y in (-w * 0.34, w * 0.34):
            _cyl(
                part,
                w * 0.070,
                t * 0.55,
                (base_x + w * 0.70, y, z + t * 0.72),
                mats["pin"],
                f"tool_bolt_{y:.2f}",
            )
    elif r.terminal_module == "triangular_end_shoe":
        outline = [(0.0, 0.0), (w * 1.36, -w * 0.58), (w * 1.36, w * 0.58)]
        mesh = mesh_from_geometry(
            ExtrudeWithHolesGeometry(
                outline,
                [_circle_profile(w * 0.42, 0.0, min(w * 0.10, 0.008))],
                t,
                center=True,
            ),
            "triangular_end_shoe_mesh",
        )
        part.visual(
            mesh,
            origin=Origin(xyz=(base_x, 0.0, z)),
            material=mats["accent"],
            name="triangular_plate", material_class_id=("metal.paint_coated" if r.material_style in {"dark_service", "bronze_bushed", "safety_yellow"} else "metal.blackened_gunmetal"),
        )
        _box(
            part,
            (w * 0.68, w * 0.82, t * 0.55),
            (base_x + w * 1.15, 0.0, z + t * 0.72),
            mats["pad"],
            "shoe_rubber_pad",
        )
    elif r.terminal_module == "hook_tab":
        _box(
            part,
            (w * 1.00, w * 0.38, r.link_height * 0.38),
            (base_x + w * 0.45, 0.0, z),
            mats["accent"],
            "hook_tongue",
        )
        _box(
            part,
            (w * 0.24, w * 0.38, r.link_height * 0.95),
            (base_x + w * 0.92, 0.0, z + r.link_height * 0.28),
            mats["accent"],
            "hook_lip",
        )
        _box(
            part,
            (w * 0.50, w * 0.46, r.link_height * 0.34),
            (base_x + w * 0.68, 0.0, z - r.link_height * 0.22),
            mats["pad"],
            "hook_pad",
        )
    elif r.terminal_module == "heavy_end_bracket":
        _box(
            part,
            (w * 1.22, w * 1.34, r.link_height * 0.54),
            (base_x + w * 0.52, 0.0, z),
            mats["accent"],
            "heavy_end_block",
        )
        for side, y in (("pos", w * 0.54), ("neg", -w * 0.54)):
            _box(
                part,
                (w * 0.85, w * 0.18, r.link_height * 0.96),
                (base_x + w * 0.78, y, z),
                mats["accent"],
                f"heavy_end_fork_{side}",
            )
    else:
        _box(
            part,
            (w * 0.96, w * 0.76, max(t, r.link_height * 0.28)),
            (base_x + w * 0.34, 0.0, z),
            mats["accent"],
            "integral_pad_carrier",
        )
        _box(
            part,
            (w * 0.72, w * 0.58, max(t, r.link_height * 0.30)),
            (base_x + w * 0.62, 0.0, z + max(t * 0.45, r.link_height * 0.12)),
            mats["pad"],
            "rubber_end_pad",
        )


def _build_link(
    model: ArticulatedObject,
    r: ResolvedFoldingArmChainConfig,
    mats,
    *,
    index: int,
    length: float,
    is_last: bool,
):
    part = model.part(f"link_{index + 1}")
    if r.axis_family in ("z_planar_stack", "heavy_twin_strap"):
        _add_planar_flat_bar(part, r, mats, length=length, index=index)
    else:
        _add_clevis_link(part, r, mats, length=length, index=index)
    if is_last and not r.moving_terminal:
        _add_terminal_visuals(part, r, mats, offset_x=length, local=False)
    return part


def _build_terminal_part(model: ArticulatedObject, r: ResolvedFoldingArmChainConfig, mats):
    terminal = model.part("terminal")
    _add_terminal_visuals(terminal, r, mats, offset_x=0.0, local=True)
    return terminal


def build_folding_arm_chain(
    config: FoldingArmChainConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {key: _mat(model, r, key) for key in ("base", "link", "accent", "pin", "pad")}

    base = _build_base(model, r, mats)
    links = [
        _build_link(model, r, mats, index=i, length=length, is_last=(i == r.link_count - 1))
        for i, length in enumerate(r.lengths)
    ]

    parent = base
    for i, link in enumerate(links):
        joint_name = "base_to_link_1" if i == 0 else f"link_{i}_to_link_{i + 1}"
        origin = r.root_origin if i == 0 else (r.lengths[i - 1], 0.0, 0.0)
        parent_face = "root_socket" if i == 0 else "distal_socket"
        model.articulation(
            joint_name,
            ArticulationType.REVOLUTE,
            parent=parent,
            child=link,
            origin=Origin(xyz=origin),
            axis=r.joint_axis,
            motion_limits=MotionLimits(
                lower=r.joint_limits[0],
                upper=r.joint_limits[1],
                effort=max(6.0, 18.0 - i * 1.8),
                velocity=1.35 + i * 0.15,
            ),
            mating=MatingContract(
                parent_face, "positive_x", "proximal_hub", "negative_x", contact_tol=0.003
            ),
        )
        parent = link

    if r.moving_terminal:
        terminal = _build_terminal_part(model, r, mats)
        model.articulation(
            "last_link_to_terminal",
            ArticulationType.REVOLUTE,
            parent=links[-1],
            child=terminal,
            origin=Origin(xyz=(r.lengths[-1], 0.0, 0.0)),
            axis=r.joint_axis,
            motion_limits=MotionLimits(
                lower=r.joint_limits[0] * _TERMINAL_LIMIT_FRAC,
                upper=r.joint_limits[1] * _TERMINAL_LIMIT_FRAC,
                effort=7.5,
                velocity=1.2,
            ),
            mating=MatingContract(
                "distal_socket", "positive_x", "proximal_hub", "negative_x", contact_tol=0.003
            ),
        )

    model.meta["slot_choices"] = slot_choices_for_config(r)
    model.meta["multiplicity"] = r.chain_multiplicity
    model.meta["link_count"] = r.link_count
    model.meta["axis_family"] = r.axis_family
    return model


def build_seeded_folding_arm_chain(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_folding_arm_chain(config_from_seed(seed), assets=assets)


def _allow_expected_overlaps(
    ctx: TestContext,
    model: ArticulatedObject,
    r: ResolvedFoldingArmChainConfig,
) -> None:
    ctx.allow_overlap(
        model.get_part("base"),
        model.get_part("link_1"),
        reason="root pin/bushing is intentionally captured through the first link hub",
    )
    for i in range(1, r.link_count):
        ctx.allow_overlap(
            model.get_part(f"link_{i}"),
            model.get_part(f"link_{i + 1}"),
            reason="adjacent folding-arm hinge bosses intentionally share the captured pivot volume",
        )
    if r.moving_terminal:
        ctx.allow_overlap(
            model.get_part(f"link_{r.link_count}"),
            model.get_part("terminal"),
            reason="terminal hinge pin intentionally passes through the last link end bushing",
        )


def _aabb_center(aabb) -> tuple[float, float, float]:
    return (
        (aabb[0][0] + aabb[1][0]) * 0.5,
        (aabb[0][1] + aabb[1][1]) * 0.5,
        (aabb[0][2] + aabb[1][2]) * 0.5,
    )


def run_folding_arm_chain_tests(
    object_model: ArticulatedObject,
    config: FoldingArmChainConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    _allow_expected_overlaps(ctx, object_model, r)
    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.fail_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.024)
    ctx.fail_if_joint_mating_has_gap()

    expected_parts = {"base"} | {f"link_{i}" for i in range(1, r.link_count + 1)}
    if r.moving_terminal:
        expected_parts.add("terminal")
    got_parts = {part.name for part in object_model.parts}
    ctx.check(
        "identity_parts_present", expected_parts.issubset(got_parts), details=str(sorted(got_parts))
    )

    expected_joints = r.link_count + (1 if r.moving_terminal else 0)
    ctx.check(
        "joint_multiplicity",
        len(object_model.joints) == expected_joints,
        details=f"got={len(object_model.joints)} expected={expected_joints}",
    )
    for i in range(r.link_count):
        name = "base_to_link_1" if i == 0 else f"link_{i}_to_link_{i + 1}"
        joint = object_model.get_articulation(name)
        ctx.check(f"{name}_is_revolute", joint.articulation_type == ArticulationType.REVOLUTE)
        ctx.check(f"{name}_axis", tuple(joint.axis) == r.joint_axis, details=str(joint.axis))
        ctx.check(f"{name}_mating_contract", joint.mating is not None)
    if r.moving_terminal:
        joint = object_model.get_articulation("last_link_to_terminal")
        ctx.check("terminal_joint_revolute", joint.articulation_type == ArticulationType.REVOLUTE)
        ctx.check("terminal_joint_axis", tuple(joint.axis) == r.joint_axis)
        ctx.check("terminal_joint_mating_contract", joint.mating is not None)

    choices = dict(slot_choices_for_config(r))
    ctx.check(
        "slot_choices_recorded",
        dict(object_model.meta.get("slot_choices", ())) == choices,
        details=str(object_model.meta.get("slot_choices")),
    )
    ctx.check(
        "multiplicity_recorded", object_model.meta.get("multiplicity") == r.chain_multiplicity
    )

    terminal_part_name = "terminal" if r.moving_terminal else f"link_{r.link_count}"
    terminal_part = object_model.get_part(terminal_part_name)
    rest = ctx.part_world_aabb(terminal_part)
    pose = {}
    for i in range(r.link_count):
        joint_name = "base_to_link_1" if i == 0 else f"link_{i}_to_link_{i + 1}"
        joint = object_model.get_articulation(joint_name)
        pose[joint] = r.joint_limits[0] * (0.14 + 0.035 * i)
    if r.moving_terminal:
        pose[object_model.get_articulation("last_link_to_terminal")] = r.joint_limits[1] * 0.18
    with ctx.pose(pose):
        moved = ctx.part_world_aabb(terminal_part)
    if rest and moved:
        rest_c = _aabb_center(rest)
        moved_c = _aabb_center(moved)
        delta = math.sqrt(sum((moved_c[i] - rest_c[i]) ** 2 for i in range(3)))
        ctx.check("terminal_moves_under_fold_pose", delta > 0.012, details=f"delta={delta:.4f}")

    # Lock the fold-budget invariant: the worst-case same-sign stack (the largest
    # cumulative turn the motion-QC sampler can command) must stay under the wrap
    # budget so no distal link curls back through the base envelope.
    fold_segments = r.link_count + (_TERMINAL_LIMIT_FRAC if r.moving_terminal else 0.0)
    cumulative_fold = abs(r.joint_limits[1]) * fold_segments
    ctx.check(
        "fold_budget_respected",
        cumulative_fold <= _FOLD_TURN_BUDGET + 1e-6,
        details=f"cumulative_fold={cumulative_fold:.4f} budget={_FOLD_TURN_BUDGET:.4f}",
    )

    # Directly verify the two worst folds (every chain joint at its lower, then upper
    # limit, terminal folded with them) do not drive any non-adjacent part -- notably a
    # distal link -- into the base. allow_overlaps above still cover the captured pivots.
    for tag, bound in (("lower", r.joint_limits[0]), ("upper", r.joint_limits[1])):
        extreme = {}
        for i in range(r.link_count):
            joint_name = "base_to_link_1" if i == 0 else f"link_{i}_to_link_{i + 1}"
            extreme[object_model.get_articulation(joint_name)] = bound
        if r.moving_terminal:
            term_joint = object_model.get_articulation("last_link_to_terminal")
            extreme[term_joint] = bound * _TERMINAL_LIMIT_FRAC
        with ctx.pose(extreme):
            ctx.fail_if_parts_overlap_in_current_pose(
                name=f"no_overlap_at_full_fold_{tag}",
            )

    return ctx.report()


__all__ = (
    "FoldingArmChainConfig",
    "ResolvedFoldingArmChainConfig",
    "build_folding_arm_chain",
    "build_seeded_folding_arm_chain",
    "config_from_seed",
    "resolve_config",
    "run_folding_arm_chain_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
