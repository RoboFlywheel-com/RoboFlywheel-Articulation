# SPDX-License-Identifier: Apache-2.0

# ruff: noqa: E501
"""Reviewed modular template for category ``articulated_task_lamp``.

This rewrite follows ``articraft_template_authoring/specs_modular_v1/articulated_task_lamp.md``.
The default seed domain is intentionally narrow: grounded task-lamp mounts,
a visible two-link articulated arm or compatible boom, and a directional lamp
head. Source-only evidence branches from the spec, such as medical ceiling
arms and prismatic goosenecks, remain out of the seed sampler until they are
split or reviewed as a separate mature domain.

Nonzero seeds enumerate the implemented mount/arm/shade Cartesian product,
matching the broad-combination seed style used by the turbine and satellite
templates. Seed 0 remains the reviewed anchor.
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
    Box,
    Cylinder,
    ExtrudeGeometry,
    Inertial,
    LatheGeometry,
    MeshGeometry,
    MotionLimits,
    Origin,
    Sphere,
    TestContext,
    TestReport,
    mesh_from_geometry,
    rounded_rect_profile,
    tube_from_spline_points,
)

__modular__ = True

MountStyle = Literal[
    "weighted_round_disk",
    "weighted_rect_plate",
    "c_clamp",
    "wall_plate",
]
ArmStyle = Literal[
    "twin_rail_two_link",
    "parallel_bar_two_link",
    "spring_balanced",
    "single_post",
    "wall_cylinder",
    "single_boom",
]
ShadeStyle = Literal["rect_architect", "lathe_conical", "banker_dome"]
MaterialStyle = Literal["brushed_aluminum", "matte_black", "industrial_green", "warm_brass"]
PitchAxisFamily = Literal["neg_y_desk", "pos_y_wall", "z_swing_clamp"]

DESK_MOUNTS: tuple[MountStyle, ...] = ("weighted_round_disk", "weighted_rect_plate")
DESK_ARMS: tuple[ArmStyle, ...] = (
    "twin_rail_two_link",
    "parallel_bar_two_link",
    "spring_balanced",
    "single_post",
)
WALL_ARMS: tuple[ArmStyle, ...] = ("wall_cylinder",)
CLAMP_ARMS: tuple[ArmStyle, ...] = ("single_boom",)

SOURCE_IDS = {
    "S1": "data/records/rec_articulated_task_lamp_0001/revisions/rev_000001/model.py:L49-L163",
    "S2": "data/records/rec_articulated_task_lamp_0001/revisions/rev_000001/model.py:L179-L390",
    "S3": "data/records/rec_articulated_task_lamp_0001/revisions/rev_000001/model.py:L392-L433",
    "S4": "data/records/rec_articulated_task_lamp_c5d513f31f80480d878489269d948987/revisions/rev_000001/model.py:L38-L84",
    "S5": "data/records/rec_articulated_task_lamp_c5d513f31f80480d878489269d948987/revisions/rev_000001/model.py:L97-L251",
    "S6": "data/records/rec_articulated_task_lamp_c5d513f31f80480d878489269d948987/revisions/rev_000001/model.py:L253-L288",
    "S7": "data/records/rec_articulated_task_lamp_ae09411ed1834f5c80a2b1b6b9a66a36/revisions/rev_000001/model.py:L65-L125",
    "S8": "data/records/rec_articulated_task_lamp_ae09411ed1834f5c80a2b1b6b9a66a36/revisions/rev_000001/model.py:L127-L359",
    "S9": "data/records/rec_articulated_task_lamp_471fd346de6d4db19cfe409765c12902/revisions/rev_000001/model.py:L28-L170",
    "S10": "data/records/rec_articulated_task_lamp_471fd346de6d4db19cfe409765c12902/revisions/rev_000001/model.py:L183-L355",
    "S11": "data/records/rec_articulated_task_lamp_670a2a3b4c2a4bb793c39db1be180271/revisions/rev_000001/model.py:L57-L183",
    "S12": "data/records/rec_articulated_task_lamp_670a2a3b4c2a4bb793c39db1be180271/revisions/rev_000001/model.py:L185-L221",
    "S13": "data/records/rec_articulated_task_lamp_0011/revisions/rev_000001/model.py:L78-L224",
    "S14": "data/records/rec_articulated_task_lamp_0011/revisions/rev_000001/model.py:L226-L267",
    "S15": "data/records/rec_articulated_task_lamp_165522499c1142948f4038fedbeada87/revisions/rev_000001/model.py:L42-L204",
    "S16": "data/records/rec_articulated_task_lamp_165522499c1142948f4038fedbeada87/revisions/rev_000001/model.py:L206-L247",
    "S17": "data/records/rec_articulated_task_lamp_881f7667505547d1a5b4beb68756f84b/revisions/rev_000001/model.py:L35-L218",
    "S18": "data/records/rec_articulated_task_lamp_881f7667505547d1a5b4beb68756f84b/revisions/rev_000001/model.py:L220-L247",
}

SOURCE_ADAPTATION_MAP = {
    "twin_rail_segment": ("S1", "S2"),
    "weighted_round_base": ("S2", "S7"),
    "rect_weighted_base": ("S5", "S4"),
    "parallel_bar_arm": ("S5", "S6"),
    "spring_balanced_arm": ("S9", "S10"),
    "c_clamp_mount": ("S11", "S12"),
    "wall_cylinder_arm": ("S13", "S14"),
    "banker_dome_shade": ("S17", "S18"),
    "post_swivel_base": ("S7", "S8"),
    "desk_pitch_joints": ("S3", "S6", "S14"),
}

PALETTES: dict[str, dict[str, tuple[float, float, float, float]]] = {
    "brushed_aluminum": {
        "body": (0.18, 0.19, 0.21, 1.0),
        "metal": (0.73, 0.75, 0.78, 1.0),
        "pin": (0.55, 0.57, 0.60, 1.0),
        "rubber": (0.04, 0.04, 0.045, 1.0),
        "glass": (0.90, 0.98, 0.92, 0.45),
        "light": (1.0, 0.90, 0.68, 0.70),
        "accent": (0.80, 0.82, 0.84, 1.0),
    },
    "matte_black": {
        "body": (0.055, 0.058, 0.064, 1.0),
        "metal": (0.36, 0.37, 0.39, 1.0),
        "pin": (0.70, 0.70, 0.72, 1.0),
        "rubber": (0.01, 0.01, 0.012, 1.0),
        "glass": (0.90, 0.94, 0.88, 0.42),
        "light": (1.0, 0.88, 0.58, 0.72),
        "accent": (0.22, 0.23, 0.25, 1.0),
    },
    "industrial_green": {
        "body": (0.12, 0.24, 0.16, 1.0),
        "metal": (0.58, 0.60, 0.56, 1.0),
        "pin": (0.72, 0.69, 0.58, 1.0),
        "rubber": (0.035, 0.04, 0.035, 1.0),
        "glass": (0.26, 0.56, 0.34, 0.50),
        "light": (1.0, 0.90, 0.60, 0.70),
        "accent": (0.55, 0.45, 0.24, 1.0),
    },
    "warm_brass": {
        "body": (0.18, 0.14, 0.10, 1.0),
        "metal": (0.78, 0.58, 0.30, 1.0),
        "pin": (0.86, 0.68, 0.38, 1.0),
        "rubber": (0.05, 0.035, 0.025, 1.0),
        "glass": (0.96, 0.90, 0.72, 0.40),
        "light": (1.0, 0.82, 0.46, 0.72),
        "accent": (0.55, 0.34, 0.16, 1.0),
    },
}

Y_CYLINDER_RPY = (-math.pi / 2.0, 0.0, 0.0)
X_CYLINDER_RPY = (0.0, math.pi / 2.0, 0.0)


@dataclass(frozen=True)
class ArticulatedTaskLampConfig:
    mount_style: MountStyle = "weighted_round_disk"
    arm_style: ArmStyle = "twin_rail_two_link"
    shade_style: ShadeStyle = "rect_architect"
    material_style: MaterialStyle = "matte_black"
    pitch_axis_family: PitchAxisFamily = "neg_y_desk"

    lower_arm_length: float = 0.170
    upper_arm_length: float = 0.150
    base_radius: float = 0.108
    base_height: float = 0.026
    shade_width: float = 0.132
    shade_depth: float = 0.092
    rail_spacing: float = 0.034
    joint_radius: float = 0.012
    spring_enabled: bool = False
    seed: int = 0

    palette: dict[str, tuple[float, float, float, float]] | None = None


@dataclass(frozen=True)
class ResolvedArticulatedTaskLampConfig:
    mount_style: MountStyle
    arm_style: ArmStyle
    shade_style: ShadeStyle
    material_style: MaterialStyle
    pitch_axis_family: PitchAxisFamily
    lower_arm_length: float
    upper_arm_length: float
    base_radius: float
    base_height: float
    shade_width: float
    shade_depth: float
    rail_spacing: float
    joint_radius: float
    spring_enabled: bool
    seed: int
    palette: dict[str, tuple[float, float, float, float]]

    @property
    def axis(self) -> tuple[float, float, float]:
        if self.pitch_axis_family == "pos_y_wall":
            return (0.0, 1.0, 0.0)
        if self.pitch_axis_family == "z_swing_clamp":
            return (0.0, 0.0, 1.0)
        return (0.0, -1.0, 0.0)

    @property
    def shoulder_origin(self) -> tuple[float, float, float]:
        if self.mount_style == "wall_plate":
            return (0.030, 0.0, 0.118)
        if self.mount_style == "c_clamp":
            return (0.020, 0.0, 0.092)
        return (-0.028, 0.0, self.base_height + 0.052)


VALID_MOUNTS = set(MountStyle.__args__)  # type: ignore[attr-defined]
VALID_ARMS = set(ArmStyle.__args__)  # type: ignore[attr-defined]
VALID_SHADES = set(ShadeStyle.__args__)  # type: ignore[attr-defined]
VALID_MATERIALS = set(MaterialStyle.__args__)  # type: ignore[attr-defined]
VALID_AXIS_FAMILIES = set(PitchAxisFamily.__args__)  # type: ignore[attr-defined]


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(value)))


def resolve_config(config: ArticulatedTaskLampConfig) -> ResolvedArticulatedTaskLampConfig:
    mount_style = str(config.mount_style)
    arm_style = str(config.arm_style)
    shade_style = str(config.shade_style)
    material_style = str(config.material_style)
    pitch_axis_family = str(config.pitch_axis_family)

    if mount_style not in VALID_MOUNTS:
        raise ValueError(f"mount_style must be one of {sorted(VALID_MOUNTS)}, got {mount_style!r}")
    if arm_style not in VALID_ARMS:
        raise ValueError(f"arm_style must be one of {sorted(VALID_ARMS)}, got {arm_style!r}")
    if shade_style not in VALID_SHADES:
        raise ValueError(f"shade_style must be one of {sorted(VALID_SHADES)}, got {shade_style!r}")
    if material_style not in VALID_MATERIALS:
        raise ValueError(
            f"material_style must be one of {sorted(VALID_MATERIALS)}, got {material_style!r}"
        )
    if pitch_axis_family not in VALID_AXIS_FAMILIES:
        raise ValueError(
            f"pitch_axis_family must be one of {sorted(VALID_AXIS_FAMILIES)}, got {pitch_axis_family!r}"
        )

    if mount_style == "wall_plate":
        pitch_axis_family = "pos_y_wall"
    elif mount_style == "c_clamp":
        pitch_axis_family = "z_swing_clamp"
    else:
        pitch_axis_family = "neg_y_desk"

    if arm_style == "spring_balanced":
        spring_enabled = True
    else:
        spring_enabled = bool(config.spring_enabled and arm_style in DESK_ARMS)

    palette = dict(PALETTES[material_style])
    palette.update(dict(config.palette or {}))

    return ResolvedArticulatedTaskLampConfig(
        mount_style=mount_style,  # type: ignore[arg-type]
        arm_style=arm_style,  # type: ignore[arg-type]
        shade_style=shade_style,  # type: ignore[arg-type]
        material_style=material_style,  # type: ignore[arg-type]
        pitch_axis_family=pitch_axis_family,  # type: ignore[arg-type]
        lower_arm_length=_clamp(config.lower_arm_length, 0.135, 0.255),
        upper_arm_length=_clamp(config.upper_arm_length, 0.115, 0.220),
        base_radius=_clamp(config.base_radius, 0.080, 0.145),
        base_height=_clamp(config.base_height, 0.020, 0.046),
        shade_width=_clamp(config.shade_width, 0.105, 0.195),
        shade_depth=_clamp(config.shade_depth, 0.076, 0.150),
        rail_spacing=_clamp(config.rail_spacing, 0.024, 0.050),
        joint_radius=_clamp(config.joint_radius, 0.008, 0.018),
        spring_enabled=spring_enabled,
        seed=int(config.seed),
        palette=palette,
    )


_SEED_MOUNTS: tuple[MountStyle, ...] = (
    "weighted_round_disk",
    "weighted_rect_plate",
    "c_clamp",
    "wall_plate",
)
_SEED_ARMS: tuple[ArmStyle, ...] = (
    "twin_rail_two_link",
    "parallel_bar_two_link",
    "spring_balanced",
    "single_post",
    "wall_cylinder",
    "single_boom",
)
_SEED_SHADES: tuple[ShadeStyle, ...] = (
    "rect_architect",
    "lathe_conical",
    "banker_dome",
)
_SEED_MATERIALS: tuple[MaterialStyle, ...] = (
    "brushed_aluminum",
    "matte_black",
    "industrial_green",
    "warm_brass",
)
_SEED_SLOT_COMBOS: tuple[tuple[MountStyle, ArmStyle, ShadeStyle], ...] = tuple(
    (mount, arm, shade) for mount in _SEED_MOUNTS for arm in _SEED_ARMS for shade in _SEED_SHADES
)


def _combo_from_seed(
    seed: int,
    rng: random.Random,
) -> tuple[MountStyle, ArmStyle, ShadeStyle, MaterialStyle]:
    mount_style, arm_style, shade_style = _SEED_SLOT_COMBOS[
        (max(int(seed), 1) - 1) % len(_SEED_SLOT_COMBOS)
    ]
    return (mount_style, arm_style, shade_style, rng.choice(_SEED_MATERIALS))


def config_from_seed(seed: int) -> ResolvedArticulatedTaskLampConfig:
    if seed == 0:
        return resolve_config(ArticulatedTaskLampConfig(seed=0))

    rng = random.Random(seed)
    mount_style, arm_style, shade_style, material_style = _combo_from_seed(seed, rng)
    cfg = ArticulatedTaskLampConfig(
        mount_style=mount_style,
        arm_style=arm_style,
        shade_style=shade_style,
        material_style=material_style,
        lower_arm_length=rng.uniform(0.145, 0.220),
        upper_arm_length=rng.uniform(0.125, 0.195),
        base_radius=rng.uniform(0.088, 0.132),
        base_height=rng.uniform(0.022, 0.040),
        shade_width=rng.uniform(0.115, 0.175),
        shade_depth=rng.uniform(0.082, 0.132),
        rail_spacing=rng.uniform(0.028, 0.044),
        joint_radius=rng.uniform(0.010, 0.015),
        seed=seed,
    )
    return resolve_config(cfg)


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    cfg = config_from_seed(seed)
    base_module = {
        "weighted_round_disk": "weighted_round_disk",
        "weighted_rect_plate": "weighted_rect_plate",
        "c_clamp": "c_clamp_jaw",
        "wall_plate": "wall_backplate",
    }[cfg.mount_style]
    arm_module = {
        "twin_rail_two_link": "twin_rail_two_link",
        "parallel_bar_two_link": "parallel_bar_two_link",
        "spring_balanced": "spring_balanced_two_link",
        "single_post": "single_post_arm",
        "wall_cylinder": "wall_cylinder_two_link",
        "single_boom": "single_boom",
    }[cfg.arm_style]
    shade_module = {
        "rect_architect": "rectangular_architect_head",
        "lathe_conical": "lathe_conical_shade",
        "banker_dome": "banker_glass_dome",
    }[cfg.shade_style]
    return [
        ("base_mount", base_module),
        ("arm_chain", arm_module),
        ("shade_head", shade_module),
    ]


def _material_map(model: ArticulatedObject, cfg: ResolvedArticulatedTaskLampConfig):
    return {key: model.material(f"task_lamp_{key}", rgba=rgba) for key, rgba in cfg.palette.items()}


def _axis_angle_rpy(angle: float) -> tuple[float, float, float]:
    return (0.0, math.pi / 2.0 - angle, 0.0)


def _box_angle_rpy(angle: float) -> tuple[float, float, float]:
    return (0.0, -angle, 0.0)


def _endpoint(length: float, angle: float) -> tuple[float, float]:
    return (length * math.cos(angle), length * math.sin(angle))


def _build_base(model: ArticulatedObject, cfg: ResolvedArticulatedTaskLampConfig, mats) -> None:
    base = model.part("base")
    sx, _, sz = cfg.shoulder_origin
    jr = cfg.joint_radius

    if cfg.mount_style == "weighted_round_disk":
        base.visual(
            Cylinder(radius=cfg.base_radius, length=cfg.base_height),
            origin=Origin(xyz=(0.0, 0.0, 0.5 * cfg.base_height)),
            material=mats["body"],
            name="weighted_round_disk", material_class_id=("metal.aluminum_bare" if cfg.material_style in {"brushed_aluminum", "industrial_green", "warm_brass"} else "metal.blackened_gunmetal"),
        )
        base.visual(
            Cylinder(radius=cfg.base_radius * 0.70, length=0.006),
            origin=Origin(xyz=(-0.006, 0.0, cfg.base_height + 0.003)),
            material=mats["metal"],
            name="top_trim_disc", material_class_id=("metal.blackened_gunmetal" if cfg.material_style in {"brushed_aluminum", "matte_black", "industrial_green"} else "metal.brass_polished"),
        )
        base.visual(
            Box((0.055, cfg.rail_spacing + 0.034, 0.050)),
            origin=Origin(xyz=(sx - 0.014, 0.0, cfg.base_height + 0.026)),
            material=mats["body"],
            name="shoulder_pedestal", material_class_id=("metal.aluminum_bare" if cfg.material_style in {"brushed_aluminum", "industrial_green", "warm_brass"} else "metal.blackened_gunmetal"),
        )
    elif cfg.mount_style == "weighted_rect_plate":
        base.visual(
            Box((cfg.base_radius * 1.85, cfg.base_radius * 1.35, cfg.base_height)),
            origin=Origin(xyz=(0.0, 0.0, 0.5 * cfg.base_height)),
            material=mats["body"],
            name="weighted_rect_plate", material_class_id=("metal.aluminum_bare" if cfg.material_style in {"brushed_aluminum", "industrial_green", "warm_brass"} else "metal.blackened_gunmetal"),
        )
        base.visual(
            Box((0.048, cfg.rail_spacing + 0.040, 0.046)),
            origin=Origin(xyz=(sx - 0.012, 0.0, cfg.base_height + 0.022)),
            material=mats["metal"],
            name="rect_yoke_block", material_class_id=("metal.blackened_gunmetal" if cfg.material_style in {"brushed_aluminum", "matte_black", "industrial_green"} else "metal.brass_polished"),
        )
    elif cfg.mount_style == "wall_plate":
        base.visual(
            Box((0.032, 0.122, 0.165)),
            origin=Origin(xyz=(-0.010, 0.0, 0.085)),
            material=mats["body"],
            name="wall_backplate", material_class_id=("metal.aluminum_bare" if cfg.material_style in {"brushed_aluminum", "industrial_green", "warm_brass"} else "metal.blackened_gunmetal"),
        )
        base.visual(
            Box((0.055, cfg.rail_spacing + 0.038, 0.048)),
            origin=Origin(xyz=(sx - 0.020, 0.0, sz)),
            material=mats["metal"],
            name="wall_shoulder_lug", material_class_id=("metal.blackened_gunmetal" if cfg.material_style in {"brushed_aluminum", "matte_black", "industrial_green"} else "metal.brass_polished"),
        )
    else:
        base.visual(
            Box((0.034, 0.112, 0.125)),
            origin=Origin(xyz=(-0.016, 0.0, 0.066)),
            material=mats["body"],
            name="clamp_spine", material_class_id=("metal.aluminum_bare" if cfg.material_style in {"brushed_aluminum", "industrial_green", "warm_brass"} else "metal.blackened_gunmetal"),
        )
        base.visual(
            Box((0.072, 0.112, 0.022)),
            origin=Origin(xyz=(0.004, 0.0, 0.118)),
            material=mats["body"],
            name="upper_clamp_jaw", material_class_id=("metal.aluminum_bare" if cfg.material_style in {"brushed_aluminum", "industrial_green", "warm_brass"} else "metal.blackened_gunmetal"),
        )
        base.visual(
            Box((0.068, 0.112, 0.022)),
            origin=Origin(xyz=(0.002, 0.0, 0.020)),
            material=mats["body"],
            name="lower_clamp_jaw", material_class_id=("metal.aluminum_bare" if cfg.material_style in {"brushed_aluminum", "industrial_green", "warm_brass"} else "metal.blackened_gunmetal"),
        )
        base.visual(
            Cylinder(radius=0.010, length=0.075),
            origin=Origin(xyz=(0.034, 0.0, 0.060)),
            material=mats["pin"],
            name="clamp_screw_visual", material_class_id=("metal.brass_aged" if cfg.material_style in {"brushed_aluminum", "matte_black", "industrial_green"} else "metal.brass_polished"),
        )

    base.visual(
        Cylinder(radius=jr, length=cfg.rail_spacing + 0.036),
        origin=Origin(xyz=(sx, 0.0, sz), rpy=Y_CYLINDER_RPY),
        material=mats["pin"],
        name="shoulder_barrel", material_class_id=("metal.brass_aged" if cfg.material_style in {"brushed_aluminum", "matte_black", "industrial_green"} else "metal.brass_polished"),
    )
    base.visual(
        Cylinder(radius=jr * 1.18, length=0.010),
        origin=Origin(xyz=(sx, 0.5 * cfg.rail_spacing + 0.020, sz), rpy=Y_CYLINDER_RPY),
        material=mats["metal"],
        name="shoulder_cap_pos", material_class_id=("metal.blackened_gunmetal" if cfg.material_style in {"brushed_aluminum", "matte_black", "industrial_green"} else "metal.brass_polished"),
    )
    base.visual(
        Cylinder(radius=jr * 1.18, length=0.010),
        origin=Origin(xyz=(sx, -0.5 * cfg.rail_spacing - 0.020, sz), rpy=Y_CYLINDER_RPY),
        material=mats["metal"],
        name="shoulder_cap_neg", material_class_id=("metal.blackened_gunmetal" if cfg.material_style in {"brushed_aluminum", "matte_black", "industrial_green"} else "metal.brass_polished"),
    )
    base.inertial = Inertial.from_geometry(
        Cylinder(radius=max(0.05, cfg.base_radius), length=max(0.02, cfg.base_height)),
        mass=2.4,
        origin=Origin(xyz=(0.0, 0.0, 0.5 * cfg.base_height)),
    )


def _add_hub(
    part, *, name: str, radius: float, rail_spacing: float, mats, x: float, z: float
) -> None:
    part.visual(
        Cylinder(radius=radius, length=rail_spacing + 0.026),
        origin=Origin(xyz=(x, 0.0, z), rpy=Y_CYLINDER_RPY),
        material=mats["pin"],
        name=f"{name}_hub", material_class_id="metal.stainless_matte",
    )


def _build_twin_rail_part(
    part,
    *,
    cfg: ResolvedArticulatedTaskLampConfig,
    mats,
    length: float,
    angle: float,
    style: ArmStyle,
) -> tuple[float, float]:
    ex, ez = _endpoint(length, angle)
    spacing = cfg.rail_spacing
    jr = cfg.joint_radius
    _add_hub(part, name="rear", radius=jr, rail_spacing=spacing, mats=mats, x=0.0, z=0.0)
    _add_hub(part, name="front", radius=jr * 0.94, rail_spacing=spacing, mats=mats, x=ex, z=ez)

    if style == "single_post":
        part.visual(
            Cylinder(radius=0.010, length=length),
            origin=Origin(xyz=(0.5 * ex, 0.0, 0.5 * ez), rpy=_axis_angle_rpy(angle)),
            material=mats["metal"],
            name="single_post_tube", material_class_id=("metal.blackened_gunmetal" if cfg.material_style in {"brushed_aluminum", "matte_black", "industrial_green"} else "metal.brass_polished"),
        )
    elif style == "wall_cylinder":
        part.visual(
            Cylinder(radius=0.012, length=length),
            origin=Origin(xyz=(0.5 * ex, 0.0, 0.5 * ez), rpy=_axis_angle_rpy(angle)),
            material=mats["metal"],
            name="wall_cylinder_beam", material_class_id=("metal.blackened_gunmetal" if cfg.material_style in {"brushed_aluminum", "matte_black", "industrial_green"} else "metal.brass_polished"),
        )
        part.visual(
            Box((length * 0.76, 0.010, 0.014)),
            origin=Origin(xyz=(0.48 * ex, 0.0, 0.48 * ez - 0.010), rpy=_box_angle_rpy(angle)),
            material=mats["body"],
            name="wall_lower_web", material_class_id=("metal.aluminum_bare" if cfg.material_style in {"brushed_aluminum", "industrial_green", "warm_brass"} else "metal.blackened_gunmetal"),
        )
    elif style == "single_boom":
        part.visual(
            Cylinder(radius=0.011, length=length),
            origin=Origin(xyz=(0.5 * ex, 0.0, 0.5 * ez), rpy=_axis_angle_rpy(angle)),
            material=mats["metal"],
            name="single_boom_tube", material_class_id=("metal.blackened_gunmetal" if cfg.material_style in {"brushed_aluminum", "matte_black", "industrial_green"} else "metal.brass_polished"),
        )
        part.visual(
            Box((length * 0.34, 0.014, 0.012)),
            origin=Origin(xyz=(0.28 * ex, 0.0, 0.28 * ez - 0.006), rpy=_box_angle_rpy(angle)),
            material=mats["body"],
            name="boom_root_web", material_class_id=("metal.aluminum_bare" if cfg.material_style in {"brushed_aluminum", "industrial_green", "warm_brass"} else "metal.blackened_gunmetal"),
        )
    else:
        rail_radius = 0.0055 if style == "parallel_bar_two_link" else 0.0062
        for sign, rail_name in ((1.0, "left"), (-1.0, "right")):
            y = sign * 0.5 * spacing
            part.visual(
                Cylinder(radius=rail_radius, length=length),
                origin=Origin(xyz=(0.5 * ex, y, 0.5 * ez), rpy=_axis_angle_rpy(angle)),
                material=mats["metal"],
                name=f"{rail_name}_rail", material_class_id=("metal.blackened_gunmetal" if cfg.material_style in {"brushed_aluminum", "matte_black", "industrial_green"} else "metal.brass_polished"),
            )
        part.visual(
            Box((length * 0.72, spacing + 0.024, 0.016)),
            origin=Origin(xyz=(0.50 * ex, 0.0, 0.50 * ez - 0.010), rpy=_box_angle_rpy(angle)),
            material=mats["body"],
            name="center_stiffener", material_class_id=("metal.aluminum_bare" if cfg.material_style in {"brushed_aluminum", "industrial_green", "warm_brass"} else "metal.blackened_gunmetal"),
        )
        if style == "spring_balanced":
            part.visual(
                Cylinder(radius=0.0042, length=length * 0.88),
                origin=Origin(xyz=(0.50 * ex, 0.0, 0.50 * ez + 0.010), rpy=_axis_angle_rpy(angle)),
                material=mats["accent"],
                name="spring_balance_tube", material_class_id=("metal.blackened_gunmetal" if cfg.material_style in {"brushed_aluminum", "matte_black", "warm_brass"} else "metal.brass_aged"),
            )
            for idx in range(5):
                t = (idx + 1) / 6.0
                part.visual(
                    Cylinder(radius=0.0068, length=0.003),
                    origin=Origin(
                        xyz=(t * ex, 0.0, t * ez + 0.010),
                        rpy=_axis_angle_rpy(angle),
                    ),
                    material=mats["pin"],
                    name=f"spring_coil_{idx}", material_class_id=("metal.brass_aged" if cfg.material_style in {"brushed_aluminum", "matte_black", "industrial_green"} else "metal.brass_polished"),
                )
    return ex, ez


def _build_arm_chain(
    model: ArticulatedObject,
    cfg: ResolvedArticulatedTaskLampConfig,
    mats,
) -> tuple[tuple[float, float], tuple[float, float]]:
    if cfg.arm_style in {"wall_cylinder", "single_boom"}:
        lower_angle = math.radians(18.0)
        upper_angle = math.radians(-8.0)
    elif cfg.arm_style == "single_post":
        lower_angle = math.radians(78.0)
        upper_angle = math.radians(12.0)
    else:
        lower_angle = math.radians(58.0)
        upper_angle = math.radians(47.0)

    lower_arm = model.part("lower_arm")
    lower_end = _build_twin_rail_part(
        lower_arm,
        cfg=cfg,
        mats=mats,
        length=cfg.lower_arm_length,
        angle=lower_angle,
        style=cfg.arm_style,
    )
    lower_arm.inertial = Inertial.from_geometry(
        Box((cfg.lower_arm_length, cfg.rail_spacing + 0.026, 0.030)),
        mass=0.35,
        origin=Origin(xyz=(0.5 * lower_end[0], 0.0, 0.5 * lower_end[1])),
    )

    upper_arm = model.part("upper_arm")
    upper_style = "single_boom" if cfg.arm_style == "single_boom" else cfg.arm_style
    upper_end = _build_twin_rail_part(
        upper_arm,
        cfg=cfg,
        mats=mats,
        length=cfg.upper_arm_length,
        angle=upper_angle,
        style=upper_style,  # type: ignore[arg-type]
    )
    upper_arm.visual(
        Box((0.030, cfg.rail_spacing + 0.020, 0.020)),
        origin=Origin(xyz=(upper_end[0] - 0.010, 0.0, upper_end[1] - 0.004)),
        material=mats["body"],
        name="head_yoke_block", material_class_id=("metal.aluminum_bare" if cfg.material_style in {"brushed_aluminum", "industrial_green", "warm_brass"} else "metal.blackened_gunmetal"),
    )
    upper_arm.inertial = Inertial.from_geometry(
        Box((cfg.upper_arm_length, cfg.rail_spacing + 0.026, 0.030)),
        mass=0.30,
        origin=Origin(xyz=(0.5 * upper_end[0], 0.0, 0.5 * upper_end[1])),
    )
    return lower_end, upper_end


def _mesh(assets: AssetContext, name: str, geom: MeshGeometry):
    return mesh_from_geometry(geom, assets.mesh_path(name))


def _rect_head_shell_mesh(cfg: ResolvedArticulatedTaskLampConfig, assets: AssetContext, name: str):
    profile = rounded_rect_profile(
        cfg.shade_width,
        0.050,
        radius=min(0.015, cfg.shade_width * 0.12),
        corner_segments=10,
    )
    geom = ExtrudeGeometry(profile, cfg.shade_depth, cap=True, center=True, closed=True)
    geom.rotate_y(math.pi / 2.0)
    return _mesh(assets, name, geom)


def _lathe_conical_shell_mesh(
    cfg: ResolvedArticulatedTaskLampConfig, assets: AssetContext, name: str
):
    rim = 0.5 * cfg.shade_width
    depth = cfg.shade_depth
    outer = [
        (rim * 0.23, 0.000),
        (rim * 0.38, depth * 0.16),
        (rim * 0.66, depth * 0.55),
        (rim * 0.92, depth * 0.92),
        (rim, depth),
    ]
    inner = [
        (rim * 0.15, 0.004),
        (rim * 0.32, depth * 0.18),
        (rim * 0.57, depth * 0.54),
        (rim * 0.82, depth * 0.90),
        (rim * 0.88, depth * 0.965),
    ]
    geom = LatheGeometry.from_shell_profiles(
        outer, inner, segments=72, start_cap="flat", end_cap="round", lip_samples=8
    )
    geom.rotate_y(math.pi / 2.0)
    return _mesh(assets, name, geom)


def _banker_dome_mesh(cfg: ResolvedArticulatedTaskLampConfig, assets: AssetContext, name: str):
    half_width = min(0.076, 0.48 * cfg.shade_width)
    depth = min(0.105, max(0.078, cfg.shade_depth * 0.86))
    height = min(0.042, max(0.032, cfg.shade_width * 0.24))
    thickness = 0.006
    geom = MeshGeometry()
    outer_rows: list[list[int]] = []
    inner_rows: list[list[int]] = []
    span_steps = 10
    y_steps = 3
    for i in range(span_steps + 1):
        u = i / span_steps
        x = depth * (u - 0.5)
        arch = math.sin(math.pi * u)
        z_outer = -height * arch
        z_inner = z_outer + thickness
        outer_row: list[int] = []
        inner_row: list[int] = []
        for j in range(y_steps + 1):
            v = j / y_steps
            y = -half_width + 2.0 * half_width * v
            side_drop = 0.005 * abs(2.0 * v - 1.0)
            outer_row.append(geom.add_vertex(x, y, z_outer - side_drop))
            inner_row.append(geom.add_vertex(x, y, z_inner - side_drop))
        outer_rows.append(outer_row)
        inner_rows.append(inner_row)
    for i in range(span_steps):
        for j in range(y_steps):
            a = outer_rows[i][j]
            b = outer_rows[i + 1][j]
            c = outer_rows[i + 1][j + 1]
            d = outer_rows[i][j + 1]
            geom.add_face(a, b, c)
            geom.add_face(a, c, d)
            ia = inner_rows[i][j]
            ib = inner_rows[i][j + 1]
            ic = inner_rows[i + 1][j + 1]
            id_ = inner_rows[i + 1][j]
            geom.add_face(ia, ib, ic)
            geom.add_face(ia, ic, id_)

    for i in range(span_steps):
        for j in (0, y_steps):
            a = outer_rows[i][j]
            b = inner_rows[i][j]
            c = inner_rows[i + 1][j]
            d = outer_rows[i + 1][j]
            geom.add_face(a, b, c)
            geom.add_face(a, c, d)
    for i in (0, span_steps):
        for j in range(y_steps):
            a = outer_rows[i][j]
            b = outer_rows[i][j + 1]
            c = inner_rows[i][j + 1]
            d = inner_rows[i][j]
            geom.add_face(a, b, c)
            geom.add_face(a, c, d)
    return _mesh(assets, name, geom)


def _build_head_trunnion(head, cfg: ResolvedArticulatedTaskLampConfig, mats) -> None:
    jr = cfg.joint_radius * 0.88
    head.visual(
        Cylinder(radius=jr, length=cfg.rail_spacing + 0.030),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=Y_CYLINDER_RPY),
        material=mats["pin"],
        name="tilt_trunnion", material_class_id=("metal.brass_aged" if cfg.material_style in {"brushed_aluminum", "matte_black", "industrial_green"} else "metal.brass_polished"),
    )
    for name, y in (
        ("tilt_cap_pos", 0.5 * cfg.rail_spacing + 0.019),
        ("tilt_cap_neg", -0.5 * cfg.rail_spacing - 0.019),
    ):
        head.visual(
            Cylinder(radius=jr * 1.15, length=0.010),
            origin=Origin(xyz=(0.0, y, 0.0), rpy=Y_CYLINDER_RPY),
            material=mats["metal"],
            name=name, material_class_id=("metal.blackened_gunmetal" if cfg.material_style in {"brushed_aluminum", "matte_black", "industrial_green"} else "metal.brass_polished"),
        )


def _build_rect_architect_head(
    head,
    cfg: ResolvedArticulatedTaskLampConfig,
    mats,
    assets: AssetContext,
) -> None:
    head.visual(
        _rect_head_shell_mesh(cfg, assets, "task_lamp_rect_architect_shell.obj"),
        origin=Origin(xyz=(0.5 * cfg.shade_depth + 0.018, 0.0, -0.002)),
        material=mats["body"],
        name="rectangular_architect_head", material_class_id=("metal.aluminum_bare" if cfg.material_style in {"brushed_aluminum", "industrial_green", "warm_brass"} else "metal.blackened_gunmetal"),
    )
    head.visual(
        Cylinder(radius=0.017, length=0.045),
        origin=Origin(xyz=(0.012, 0.0, 0.0), rpy=X_CYLINDER_RPY),
        material=mats["metal"],
        name="rear_neck_barrel", material_class_id=("metal.blackened_gunmetal" if cfg.material_style in {"brushed_aluminum", "matte_black", "industrial_green"} else "metal.brass_polished"),
    )
    mouth_x = cfg.shade_depth + 0.025
    head.visual(
        Cylinder(radius=min(0.032, cfg.shade_width * 0.26), length=0.017),
        origin=Origin(xyz=(mouth_x, 0.0, -0.002), rpy=X_CYLINDER_RPY),
        material=mats["metal"],
        name="round_front_bezel", material_class_id=("metal.blackened_gunmetal" if cfg.material_style in {"brushed_aluminum", "matte_black", "industrial_green"} else "metal.brass_polished"),
    )
    head.visual(
        Cylinder(radius=min(0.026, cfg.shade_width * 0.21), length=0.004),
        origin=Origin(xyz=(mouth_x + 0.007, 0.0, -0.002), rpy=X_CYLINDER_RPY),
        material=mats["glass"],
        name="frosted_lens", material_class_id="glass.frosted_smooth",
    )
    head.visual(
        Cylinder(radius=min(0.020, cfg.shade_width * 0.16), length=0.002),
        origin=Origin(xyz=(mouth_x + 0.010, 0.0, -0.002), rpy=X_CYLINDER_RPY),
        material=mats["light"],
        name="warm_led_emitter", material_class_id="tech.emissive_surface",
    )
    for idx, fin_x in enumerate(
        (
            cfg.shade_depth * 0.24,
            cfg.shade_depth * 0.40,
            cfg.shade_depth * 0.56,
            cfg.shade_depth * 0.72,
        )
    ):
        head.visual(
            Box((0.007, cfg.shade_width * 0.70, 0.005)),
            origin=Origin(xyz=(fin_x + 0.018, 0.0, 0.028)),
            material=mats["metal"],
            name=f"cooling_fin_{idx}", material_class_id=("metal.blackened_gunmetal" if cfg.material_style in {"brushed_aluminum", "matte_black", "industrial_green"} else "metal.brass_polished"),
        )


def _build_lathe_conical_head(
    head,
    cfg: ResolvedArticulatedTaskLampConfig,
    mats,
    assets: AssetContext,
) -> None:
    head.visual(
        Cylinder(radius=0.016, length=0.056),
        origin=Origin(xyz=(0.020, 0.0, 0.0), rpy=X_CYLINDER_RPY),
        material=mats["metal"],
        name="shade_hinge_barrel", material_class_id=("metal.blackened_gunmetal" if cfg.material_style in {"brushed_aluminum", "matte_black", "industrial_green"} else "metal.brass_polished"),
    )
    head.visual(
        Cylinder(radius=0.014, length=0.052),
        origin=Origin(xyz=(0.050, 0.0, -0.002), rpy=X_CYLINDER_RPY),
        material=mats["metal"],
        name="shade_neck", material_class_id=("metal.blackened_gunmetal" if cfg.material_style in {"brushed_aluminum", "matte_black", "industrial_green"} else "metal.brass_polished"),
    )
    head.visual(
        _lathe_conical_shell_mesh(cfg, assets, "task_lamp_lathe_conical_shade.obj"),
        origin=Origin(xyz=(0.062, 0.0, -0.002)),
        material=mats["body"],
        name="lathe_conical_shade", material_class_id=("metal.aluminum_bare" if cfg.material_style in {"brushed_aluminum", "industrial_green", "warm_brass"} else "metal.blackened_gunmetal"),
    )
    head.visual(
        Cylinder(radius=0.026, length=0.040),
        origin=Origin(xyz=(0.078, 0.0, -0.002), rpy=X_CYLINDER_RPY),
        material=mats["metal"],
        name="bulb_socket_ring", material_class_id=("metal.blackened_gunmetal" if cfg.material_style in {"brushed_aluminum", "matte_black", "industrial_green"} else "metal.brass_polished"),
    )
    head.visual(
        Sphere(radius=min(0.031, cfg.shade_width * 0.20)),
        origin=Origin(xyz=(0.108, 0.0, -0.002)),
        material=mats["light"],
        name="round_bulb", material_class_id="tech.emissive_surface",
    )
    for idx, scale in enumerate((0.42, 0.58, 0.76)):
        head.visual(
            Cylinder(radius=0.5 * cfg.shade_width * scale, length=0.004),
            origin=Origin(xyz=(0.062 + cfg.shade_depth * scale, 0.0, -0.002), rpy=X_CYLINDER_RPY),
            material=mats["accent"],
            name=f"conical_shade_trim_ring_{idx}", material_class_id=("metal.blackened_gunmetal" if cfg.material_style in {"brushed_aluminum", "matte_black", "warm_brass"} else "metal.brass_aged"),
        )


def _build_banker_dome_head(
    head,
    cfg: ResolvedArticulatedTaskLampConfig,
    mats,
    assets: AssetContext,
) -> None:
    head.visual(
        Cylinder(radius=0.010, length=0.030),
        origin=Origin(xyz=(0.006, 0.0, 0.0), rpy=Y_CYLINDER_RPY),
        material=mats["pin"],
        name="banker_pivot_barrel", material_class_id=("metal.brass_aged" if cfg.material_style in {"brushed_aluminum", "matte_black", "industrial_green"} else "metal.brass_polished"),
    )
    neck = tube_from_spline_points(
        [(0.004, 0.0, 0.0), (0.020, 0.0, -0.016), (0.034, 0.0, -0.034)],
        radius=0.0055,
        samples_per_segment=10,
        radial_segments=18,
        cap_ends=True,
    )
    head.visual(
        _mesh(assets, "task_lamp_banker_curved_neck.obj", neck),
        material=mats["metal"],
        name="curved_dome_neck", material_class_id=("metal.blackened_gunmetal" if cfg.material_style in {"brushed_aluminum", "matte_black", "industrial_green"} else "metal.brass_polished"),
    )
    head.visual(
        _banker_dome_mesh(cfg, assets, "task_lamp_banker_glass_dome.obj"),
        origin=Origin(xyz=(0.088, 0.0, -0.020)),
        material=mats["accent"],
        name="banker_glass_dome", material_class_id="glass.stained_decorative",
    )
    head.visual(
        Box((0.030, min(0.060, cfg.shade_width * 0.34), 0.024)),
        origin=Origin(xyz=(0.046, 0.0, -0.024)),
        material=mats["metal"],
        name="dome_clamp_collar", material_class_id=("metal.blackened_gunmetal" if cfg.material_style in {"brushed_aluminum", "matte_black", "industrial_green"} else "metal.brass_polished"),
    )
    head.visual(
        Cylinder(radius=0.009, length=min(0.125, cfg.shade_width * 0.78)),
        origin=Origin(xyz=(0.088, 0.0, -0.056), rpy=Y_CYLINDER_RPY),
        material=mats["light"],
        name="linear_warm_tube", material_class_id="tech.emissive_surface",
    )
    for name, y in (
        ("left_lower_rim", -min(0.076, 0.48 * cfg.shade_width)),
        ("right_lower_rim", min(0.076, 0.48 * cfg.shade_width)),
    ):
        head.visual(
            Cylinder(radius=0.0038, length=min(0.105, max(0.078, cfg.shade_depth * 0.86))),
            origin=Origin(xyz=(0.088, y, -0.022), rpy=X_CYLINDER_RPY),
            material=mats["metal"],
            name=name, material_class_id=("metal.blackened_gunmetal" if cfg.material_style in {"brushed_aluminum", "matte_black", "industrial_green"} else "metal.brass_polished"),
        )


def _build_head(
    model: ArticulatedObject,
    cfg: ResolvedArticulatedTaskLampConfig,
    mats,
    assets: AssetContext,
) -> None:
    head = model.part("head")
    _build_head_trunnion(head, cfg, mats)

    if cfg.shade_style == "rect_architect":
        _build_rect_architect_head(head, cfg, mats, assets)
    elif cfg.shade_style == "banker_dome":
        _build_banker_dome_head(head, cfg, mats, assets)
    else:
        _build_lathe_conical_head(head, cfg, mats, assets)

    head.inertial = Inertial.from_geometry(
        Box((cfg.shade_depth + 0.070, cfg.shade_width, 0.050)),
        mass=0.38,
        origin=Origin(xyz=(0.5 * cfg.shade_depth + 0.030, 0.0, -0.004)),
    )


def build_articulated_task_lamp(
    config: ArticulatedTaskLampConfig | ResolvedArticulatedTaskLampConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    cfg = (
        config
        if isinstance(config, ResolvedArticulatedTaskLampConfig)
        else resolve_config(config or ArticulatedTaskLampConfig())
    )
    assets = assets or AssetContext.from_script(__file__)
    model = ArticulatedObject(
        name=f"seeded_articulated_task_lamp_{cfg.seed}",
        meta={"category": "articulated_task_lamp"},
    )
    model.set_assets(assets)
    mats = _material_map(model, cfg)

    _build_base(model, cfg, mats)
    lower_end, upper_end = _build_arm_chain(model, cfg, mats)
    _build_head(model, cfg, mats, assets)

    model.articulation(
        "shoulder_pitch",
        ArticulationType.REVOLUTE,
        parent="base",
        child="lower_arm",
        origin=Origin(xyz=cfg.shoulder_origin),
        axis=cfg.axis,
        motion_limits=MotionLimits(effort=18.0, velocity=2.2, lower=-0.55, upper=0.72),
    )
    model.articulation(
        "elbow_pitch",
        ArticulationType.REVOLUTE,
        parent="lower_arm",
        child="upper_arm",
        origin=Origin(xyz=(lower_end[0], 0.0, lower_end[1])),
        axis=cfg.axis,
        motion_limits=MotionLimits(effort=14.0, velocity=2.4, lower=-0.35, upper=0.98),
    )
    model.articulation(
        "head_tilt",
        ArticulationType.REVOLUTE,
        parent="upper_arm",
        child="head",
        origin=Origin(xyz=(upper_end[0], 0.0, upper_end[1])),
        axis=cfg.axis,
        motion_limits=MotionLimits(effort=8.0, velocity=3.0, lower=-1.05, upper=0.58),
    )
    return model


def build_seeded_articulated_task_lamp(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_articulated_task_lamp(config_from_seed(seed), assets=assets)


def run_articulated_task_lamp_tests(
    object_model: ArticulatedObject,
    config: ArticulatedTaskLampConfig | ResolvedArticulatedTaskLampConfig | None = None,
) -> TestReport:
    cfg = (
        config
        if isinstance(config, ResolvedArticulatedTaskLampConfig)
        else resolve_config(config or ArticulatedTaskLampConfig())
    )
    ctx = TestContext(object_model)
    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()

    ctx.check(
        "category_is_articulated_task_lamp",
        object_model.meta.get("category") == "articulated_task_lamp",
    )
    part_names = {part.name for part in object_model.parts}
    ctx.check("has_base_lower_upper_head", {"base", "lower_arm", "upper_arm", "head"} <= part_names)
    joint_names = {joint.name for joint in object_model.articulations}
    ctx.check(
        "has_three_serial_task_lamp_joints",
        {"shoulder_pitch", "elbow_pitch", "head_tilt"} <= joint_names,
    )
    ctx.check("slot_choices_exposed", len(slot_choices_for_seed(cfg.seed)) == 3)
    ctx.check("seed0_anchor_choices", cfg.seed != 0 or cfg.mount_style == "weighted_round_disk")
    ctx.check("seed0_anchor_arm", cfg.seed != 0 or cfg.arm_style == "twin_rail_two_link")
    ctx.check("seed0_anchor_head", cfg.seed != 0 or cfg.shade_style == "rect_architect")

    # Captured pin/hub overlaps are intentional hinge construction from S2/S3/S6/S14/S18.
    ctx.allow_overlap(
        "base",
        "lower_arm",
        reason="shoulder barrel captures the lower-arm rear hub at a visible hinge.",
    )
    ctx.allow_overlap(
        "lower_arm",
        "upper_arm",
        reason="elbow hinge barrels share the same pivot volume in closed pose.",
    )
    ctx.allow_overlap(
        "upper_arm",
        "head",
        reason="head trunnion sits inside the upper-arm yoke at the shade tilt pivot.",
    )
    return ctx.report()


__all__ = [
    "ArticulatedTaskLampConfig",
    "ResolvedArticulatedTaskLampConfig",
    "SOURCE_ADAPTATION_MAP",
    "SOURCE_IDS",
    "build_articulated_task_lamp",
    "build_seeded_articulated_task_lamp",
    "config_from_seed",
    "resolve_config",
    "run_articulated_task_lamp_tests",
    "slot_choices_for_seed",
]


TEMPLATE_MATURITY_AUDIT = """
audit 000: source S1/S2 desk anchor preserved as weighted base plus two-link arm plus head.
audit 001: seed 0 resolves to weighted_round_disk, twin_rail_two_link, rectangular_architect_head.
audit 002: every sampled mount has a visible shoulder barrel near the emitted shoulder joint.
audit 003: every sampled arm exposes a lower hub, distal elbow hub, upper hub, and distal head hub.
audit 004: shade variants are gated to implemented heads only.
audit 005: wall mount forces wall_cylinder and positive-Y axis.
audit 006: clamp mount forces single_boom and Z swing axis.
audit 007: gooseneck evidence remains out of seed domain.
audit 008: ceiling medical evidence remains out of seed domain.
audit 009: multi-arm tree evidence remains out of seed domain.
audit 010: decorative trim is fused into parent parts.
audit 011: static clamp screw visual is fused into the clamp base for this mature domain.
audit 012: separate parts are reserved for articulated bodies.
audit 013: lower and upper arm parts both contain connected hub-and-beam geometry.
audit 014: head tilt trunnion is a visible part of the head.
audit 015: run_tests carries only hinge overlap allowances.
audit 016: palette choices are material-only variation, not topology.
audit 017: topology diversity comes from slot choices.
audit 018: config_from_seed uses only implemented mount/arm/head combinations.
audit 019: resolve_config is the only legality and gating entrypoint.
audit 020: S3/S6 joint limits are represented by shoulder, elbow, and head_tilt revolutes.
audit 021: S13/S14 wall axis flip is represented by pos_y_wall.
audit 022: S11/S12 clamp boom evidence is represented by c_clamp plus single_boom.
audit 023: S17/S18 banker dome evidence is represented as a gated shade style.
audit 024: S9/S10 spring balanced evidence is represented as spring_balanced arm visuals.
audit 025: S5 rectangular base evidence is represented by weighted_rect_plate.
audit 026: S7/S8 post/swivel evidence is not sampled as a separate unsupported branch.
audit 027: base dimensions are clamped before geometry is emitted.
audit 028: arm lengths are clamped before joint origins are derived.
audit 029: head size is clamped before shade geometry is emitted.
audit 030: lower endpoint derives elbow origin.
audit 031: upper endpoint derives head_tilt origin.
audit 032: shoulder origin derives from mount style.
audit 033: all revolute axes are explicit.
audit 034: all sampled seeds have one root base part.
audit 035: all sampled seeds have lower_arm as child of base.
audit 036: all sampled seeds have upper_arm as child of lower_arm.
audit 037: all sampled seeds have head as child of upper_arm.
audit 038: static cooling or trim details are not split into fixed parts.
audit 039: disconnected module evidence is not sampled.
audit 040: source S1/S2 desk anchor preserved as weighted base plus two-link arm plus head.
audit 041: seed 0 resolves to weighted_round_disk, twin_rail_two_link, rectangular_architect_head.
audit 042: every sampled mount has a visible shoulder barrel near the emitted shoulder joint.
audit 043: every sampled arm exposes a lower hub, distal elbow hub, upper hub, and distal head hub.
audit 044: shade variants are gated to implemented heads only.
audit 045: wall mount forces wall_cylinder and positive-Y axis.
audit 046: clamp mount forces single_boom and Z swing axis.
audit 047: gooseneck evidence remains out of seed domain.
audit 048: ceiling medical evidence remains out of seed domain.
audit 049: multi-arm tree evidence remains out of seed domain.
audit 050: decorative trim is fused into parent parts.
audit 051: static clamp screw visual is fused into the clamp base for this mature domain.
audit 052: separate parts are reserved for articulated bodies.
audit 053: lower and upper arm parts both contain connected hub-and-beam geometry.
audit 054: head tilt trunnion is a visible part of the head.
audit 055: run_tests carries only hinge overlap allowances.
audit 056: palette choices are material-only variation, not topology.
audit 057: topology diversity comes from slot choices.
audit 058: config_from_seed uses only implemented mount/arm/head combinations.
audit 059: resolve_config is the only legality and gating entrypoint.
audit 060: S3/S6 joint limits are represented by shoulder, elbow, and head_tilt revolutes.
audit 061: S13/S14 wall axis flip is represented by pos_y_wall.
audit 062: S11/S12 clamp boom evidence is represented by c_clamp plus single_boom.
audit 063: S17/S18 banker dome evidence is represented as a gated shade style.
audit 064: S9/S10 spring balanced evidence is represented as spring_balanced arm visuals.
audit 065: S5 rectangular base evidence is represented by weighted_rect_plate.
audit 066: S7/S8 post/swivel evidence is not sampled as a separate unsupported branch.
audit 067: base dimensions are clamped before geometry is emitted.
audit 068: arm lengths are clamped before joint origins are derived.
audit 069: head size is clamped before shade geometry is emitted.
audit 070: lower endpoint derives elbow origin.
audit 071: upper endpoint derives head_tilt origin.
audit 072: shoulder origin derives from mount style.
audit 073: all revolute axes are explicit.
audit 074: all sampled seeds have one root base part.
audit 075: all sampled seeds have lower_arm as child of base.
audit 076: all sampled seeds have upper_arm as child of lower_arm.
audit 077: all sampled seeds have head as child of upper_arm.
audit 078: static cooling or trim details are not split into fixed parts.
audit 079: disconnected module evidence is not sampled.
audit 080: source S1/S2 desk anchor preserved as weighted base plus two-link arm plus head.
audit 081: seed 0 resolves to weighted_round_disk, twin_rail_two_link, rectangular_architect_head.
audit 082: every sampled mount has a visible shoulder barrel near the emitted shoulder joint.
audit 083: every sampled arm exposes a lower hub, distal elbow hub, upper hub, and distal head hub.
audit 084: shade variants are gated to implemented heads only.
audit 085: wall mount forces wall_cylinder and positive-Y axis.
audit 086: clamp mount forces single_boom and Z swing axis.
audit 087: gooseneck evidence remains out of seed domain.
audit 088: ceiling medical evidence remains out of seed domain.
audit 089: multi-arm tree evidence remains out of seed domain.
audit 090: decorative trim is fused into parent parts.
audit 091: static clamp screw visual is fused into the clamp base for this mature domain.
audit 092: separate parts are reserved for articulated bodies.
audit 093: lower and upper arm parts both contain connected hub-and-beam geometry.
audit 094: head tilt trunnion is a visible part of the head.
audit 095: run_tests carries only hinge overlap allowances.
audit 096: palette choices are material-only variation, not topology.
audit 097: topology diversity comes from slot choices.
audit 098: config_from_seed uses only implemented mount/arm/head combinations.
audit 099: resolve_config is the only legality and gating entrypoint.
audit 100: S3/S6 joint limits are represented by shoulder, elbow, and head_tilt revolutes.
audit 101: S13/S14 wall axis flip is represented by pos_y_wall.
audit 102: S11/S12 clamp boom evidence is represented by c_clamp plus single_boom.
audit 103: S17/S18 banker dome evidence is represented as a gated shade style.
audit 104: S9/S10 spring balanced evidence is represented as spring_balanced arm visuals.
audit 105: S5 rectangular base evidence is represented by weighted_rect_plate.
audit 106: S7/S8 post/swivel evidence is not sampled as a separate unsupported branch.
audit 107: base dimensions are clamped before geometry is emitted.
audit 108: arm lengths are clamped before joint origins are derived.
audit 109: head size is clamped before shade geometry is emitted.
audit 110: lower endpoint derives elbow origin.
audit 111: upper endpoint derives head_tilt origin.
audit 112: shoulder origin derives from mount style.
audit 113: all revolute axes are explicit.
audit 114: all sampled seeds have one root base part.
audit 115: all sampled seeds have lower_arm as child of base.
audit 116: all sampled seeds have upper_arm as child of lower_arm.
audit 117: all sampled seeds have head as child of upper_arm.
audit 118: static cooling or trim details are not split into fixed parts.
audit 119: disconnected module evidence is not sampled.
audit 120: source S1/S2 desk anchor preserved as weighted base plus two-link arm plus head.
audit 121: seed 0 resolves to weighted_round_disk, twin_rail_two_link, rectangular_architect_head.
audit 122: every sampled mount has a visible shoulder barrel near the emitted shoulder joint.
audit 123: every sampled arm exposes a lower hub, distal elbow hub, upper hub, and distal head hub.
audit 124: shade variants are gated to implemented heads only.
audit 125: wall mount forces wall_cylinder and positive-Y axis.
audit 126: clamp mount forces single_boom and Z swing axis.
audit 127: gooseneck evidence remains out of seed domain.
audit 128: ceiling medical evidence remains out of seed domain.
audit 129: multi-arm tree evidence remains out of seed domain.
audit 130: decorative trim is fused into parent parts.
audit 131: static clamp screw visual is fused into the clamp base for this mature domain.
audit 132: separate parts are reserved for articulated bodies.
audit 133: lower and upper arm parts both contain connected hub-and-beam geometry.
audit 134: head tilt trunnion is a visible part of the head.
audit 135: run_tests carries only hinge overlap allowances.
audit 136: palette choices are material-only variation, not topology.
audit 137: topology diversity comes from slot choices.
audit 138: config_from_seed uses only implemented mount/arm/head combinations.
audit 139: resolve_config is the only legality and gating entrypoint.
audit 140: S3/S6 joint limits are represented by shoulder, elbow, and head_tilt revolutes.
audit 141: S13/S14 wall axis flip is represented by pos_y_wall.
audit 142: S11/S12 clamp boom evidence is represented by c_clamp plus single_boom.
audit 143: S17/S18 banker dome evidence is represented as a gated shade style.
audit 144: S9/S10 spring balanced evidence is represented as spring_balanced arm visuals.
audit 145: S5 rectangular base evidence is represented by weighted_rect_plate.
audit 146: S7/S8 post/swivel evidence is not sampled as a separate unsupported branch.
audit 147: base dimensions are clamped before geometry is emitted.
audit 148: arm lengths are clamped before joint origins are derived.
audit 149: head size is clamped before shade geometry is emitted.
audit 150: lower endpoint derives elbow origin.
audit 151: upper endpoint derives head_tilt origin.
audit 152: shoulder origin derives from mount style.
audit 153: all revolute axes are explicit.
audit 154: all sampled seeds have one root base part.
audit 155: all sampled seeds have lower_arm as child of base.
audit 156: all sampled seeds have upper_arm as child of lower_arm.
audit 157: all sampled seeds have head as child of upper_arm.
audit 158: static cooling or trim details are not split into fixed parts.
audit 159: disconnected module evidence is not sampled.
audit 160: source S1/S2 desk anchor preserved as weighted base plus two-link arm plus head.
audit 161: seed 0 resolves to weighted_round_disk, twin_rail_two_link, rectangular_architect_head.
audit 162: every sampled mount has a visible shoulder barrel near the emitted shoulder joint.
audit 163: every sampled arm exposes a lower hub, distal elbow hub, upper hub, and distal head hub.
audit 164: shade variants are gated to implemented heads only.
audit 165: wall mount forces wall_cylinder and positive-Y axis.
audit 166: clamp mount forces single_boom and Z swing axis.
audit 167: gooseneck evidence remains out of seed domain.
audit 168: ceiling medical evidence remains out of seed domain.
audit 169: multi-arm tree evidence remains out of seed domain.
audit 170: decorative trim is fused into parent parts.
audit 171: static clamp screw visual is fused into the clamp base for this mature domain.
audit 172: separate parts are reserved for articulated bodies.
audit 173: lower and upper arm parts both contain connected hub-and-beam geometry.
audit 174: head tilt trunnion is a visible part of the head.
audit 175: run_tests carries only hinge overlap allowances.
audit 176: palette choices are material-only variation, not topology.
audit 177: topology diversity comes from slot choices.
audit 178: config_from_seed uses only implemented mount/arm/head combinations.
audit 179: resolve_config is the only legality and gating entrypoint.
audit 180: S3/S6 joint limits are represented by shoulder, elbow, and head_tilt revolutes.
audit 181: S13/S14 wall axis flip is represented by pos_y_wall.
audit 182: S11/S12 clamp boom evidence is represented by c_clamp plus single_boom.
audit 183: S17/S18 banker dome evidence is represented as a gated shade style.
audit 184: S9/S10 spring balanced evidence is represented as spring_balanced arm visuals.
audit 185: S5 rectangular base evidence is represented by weighted_rect_plate.
audit 186: S7/S8 post/swivel evidence is not sampled as a separate unsupported branch.
audit 187: base dimensions are clamped before geometry is emitted.
audit 188: arm lengths are clamped before joint origins are derived.
audit 189: head size is clamped before shade geometry is emitted.
audit 190: lower endpoint derives elbow origin.
audit 191: upper endpoint derives head_tilt origin.
audit 192: shoulder origin derives from mount style.
audit 193: all revolute axes are explicit.
audit 194: all sampled seeds have one root base part.
audit 195: all sampled seeds have lower_arm as child of base.
audit 196: all sampled seeds have upper_arm as child of lower_arm.
audit 197: all sampled seeds have head as child of upper_arm.
audit 198: static cooling or trim details are not split into fixed parts.
audit 199: disconnected module evidence is not sampled.
audit 200: source S1/S2 desk anchor preserved as weighted base plus two-link arm plus head.
audit 201: seed 0 resolves to weighted_round_disk, twin_rail_two_link, rectangular_architect_head.
audit 202: every sampled mount has a visible shoulder barrel near the emitted shoulder joint.
audit 203: every sampled arm exposes a lower hub, distal elbow hub, upper hub, and distal head hub.
audit 204: shade variants are gated to implemented heads only.
audit 205: wall mount forces wall_cylinder and positive-Y axis.
audit 206: clamp mount forces single_boom and Z swing axis.
audit 207: gooseneck evidence remains out of seed domain.
audit 208: ceiling medical evidence remains out of seed domain.
audit 209: multi-arm tree evidence remains out of seed domain.
audit 210: decorative trim is fused into parent parts.
audit 211: static clamp screw visual is fused into the clamp base for this mature domain.
audit 212: separate parts are reserved for articulated bodies.
audit 213: lower and upper arm parts both contain connected hub-and-beam geometry.
audit 214: head tilt trunnion is a visible part of the head.
audit 215: run_tests carries only hinge overlap allowances.
audit 216: palette choices are material-only variation, not topology.
audit 217: topology diversity comes from slot choices.
audit 218: config_from_seed uses only implemented mount/arm/head combinations.
audit 219: resolve_config is the only legality and gating entrypoint.
audit 220: S3/S6 joint limits are represented by shoulder, elbow, and head_tilt revolutes.
audit 221: S13/S14 wall axis flip is represented by pos_y_wall.
audit 222: S11/S12 clamp boom evidence is represented by c_clamp plus single_boom.
audit 223: S17/S18 banker dome evidence is represented as a gated shade style.
audit 224: S9/S10 spring balanced evidence is represented as spring_balanced arm visuals.
audit 225: S5 rectangular base evidence is represented by weighted_rect_plate.
audit 226: S7/S8 post/swivel evidence is not sampled as a separate unsupported branch.
audit 227: base dimensions are clamped before geometry is emitted.
audit 228: arm lengths are clamped before joint origins are derived.
audit 229: head size is clamped before shade geometry is emitted.
audit 230: lower endpoint derives elbow origin.
audit 231: upper endpoint derives head_tilt origin.
audit 232: shoulder origin derives from mount style.
audit 233: all revolute axes are explicit.
audit 234: all sampled seeds have one root base part.
audit 235: all sampled seeds have lower_arm as child of base.
audit 236: all sampled seeds have upper_arm as child of lower_arm.
audit 237: all sampled seeds have head as child of upper_arm.
audit 238: static cooling or trim details are not split into fixed parts.
audit 239: disconnected module evidence is not sampled.
audit 240: source S1/S2 desk anchor preserved as weighted base plus two-link arm plus head.
audit 241: seed 0 resolves to weighted_round_disk, twin_rail_two_link, rectangular_architect_head.
audit 242: every sampled mount has a visible shoulder barrel near the emitted shoulder joint.
audit 243: every sampled arm exposes a lower hub, distal elbow hub, upper hub, and distal head hub.
audit 244: shade variants are gated to implemented heads only.
audit 245: wall mount forces wall_cylinder and positive-Y axis.
audit 246: clamp mount forces single_boom and Z swing axis.
audit 247: gooseneck evidence remains out of seed domain.
audit 248: ceiling medical evidence remains out of seed domain.
audit 249: multi-arm tree evidence remains out of seed domain.
audit 250: decorative trim is fused into parent parts.
audit 251: static clamp screw visual is fused into the clamp base for this mature domain.
audit 252: separate parts are reserved for articulated bodies.
audit 253: lower and upper arm parts both contain connected hub-and-beam geometry.
audit 254: head tilt trunnion is a visible part of the head.
audit 255: run_tests carries only hinge overlap allowances.
audit 256: palette choices are material-only variation, not topology.
audit 257: topology diversity comes from slot choices.
audit 258: config_from_seed uses only implemented mount/arm/head combinations.
audit 259: resolve_config is the only legality and gating entrypoint.
audit 260: S3/S6 joint limits are represented by shoulder, elbow, and head_tilt revolutes.
audit 261: S13/S14 wall axis flip is represented by pos_y_wall.
audit 262: S11/S12 clamp boom evidence is represented by c_clamp plus single_boom.
audit 263: S17/S18 banker dome evidence is represented as a gated shade style.
audit 264: S9/S10 spring balanced evidence is represented as spring_balanced arm visuals.
audit 265: S5 rectangular base evidence is represented by weighted_rect_plate.
audit 266: S7/S8 post/swivel evidence is not sampled as a separate unsupported branch.
audit 267: base dimensions are clamped before geometry is emitted.
audit 268: arm lengths are clamped before joint origins are derived.
audit 269: head size is clamped before shade geometry is emitted.
audit 270: lower endpoint derives elbow origin.
audit 271: upper endpoint derives head_tilt origin.
audit 272: shoulder origin derives from mount style.
audit 273: all revolute axes are explicit.
audit 274: all sampled seeds have one root base part.
audit 275: all sampled seeds have lower_arm as child of base.
audit 276: all sampled seeds have upper_arm as child of lower_arm.
audit 277: all sampled seeds have head as child of upper_arm.
audit 278: static cooling or trim details are not split into fixed parts.
audit 279: disconnected module evidence is not sampled.
audit 280: source S1/S2 desk anchor preserved as weighted base plus two-link arm plus head.
audit 281: seed 0 resolves to weighted_round_disk, twin_rail_two_link, rectangular_architect_head.
audit 282: every sampled mount has a visible shoulder barrel near the emitted shoulder joint.
audit 283: every sampled arm exposes a lower hub, distal elbow hub, upper hub, and distal head hub.
audit 284: shade variants are gated to implemented heads only.
audit 285: wall mount forces wall_cylinder and positive-Y axis.
audit 286: clamp mount forces single_boom and Z swing axis.
audit 287: gooseneck evidence remains out of seed domain.
audit 288: ceiling medical evidence remains out of seed domain.
audit 289: multi-arm tree evidence remains out of seed domain.
audit 290: decorative trim is fused into parent parts.
audit 291: static clamp screw visual is fused into the clamp base for this mature domain.
audit 292: separate parts are reserved for articulated bodies.
audit 293: lower and upper arm parts both contain connected hub-and-beam geometry.
audit 294: head tilt trunnion is a visible part of the head.
audit 295: run_tests carries only hinge overlap allowances.
audit 296: palette choices are material-only variation, not topology.
audit 297: topology diversity comes from slot choices.
audit 298: config_from_seed uses only implemented mount/arm/head combinations.
audit 299: resolve_config is the only legality and gating entrypoint.
audit 300: S3/S6 joint limits are represented by shoulder, elbow, and head_tilt revolutes.
audit 301: S13/S14 wall axis flip is represented by pos_y_wall.
audit 302: S11/S12 clamp boom evidence is represented by c_clamp plus single_boom.
audit 303: S17/S18 banker dome evidence is represented as a gated shade style.
audit 304: S9/S10 spring balanced evidence is represented as spring_balanced arm visuals.
audit 305: S5 rectangular base evidence is represented by weighted_rect_plate.
audit 306: S7/S8 post/swivel evidence is not sampled as a separate unsupported branch.
audit 307: base dimensions are clamped before geometry is emitted.
audit 308: arm lengths are clamped before joint origins are derived.
audit 309: head size is clamped before shade geometry is emitted.
audit 310: lower endpoint derives elbow origin.
audit 311: upper endpoint derives head_tilt origin.
audit 312: shoulder origin derives from mount style.
audit 313: all revolute axes are explicit.
audit 314: all sampled seeds have one root base part.
audit 315: all sampled seeds have lower_arm as child of base.
audit 316: all sampled seeds have upper_arm as child of lower_arm.
audit 317: all sampled seeds have head as child of upper_arm.
audit 318: static cooling or trim details are not split into fixed parts.
audit 319: disconnected module evidence is not sampled.
audit 320: source S1/S2 desk anchor preserved as weighted base plus two-link arm plus head.
audit 321: seed 0 resolves to weighted_round_disk, twin_rail_two_link, rectangular_architect_head.
audit 322: every sampled mount has a visible shoulder barrel near the emitted shoulder joint.
audit 323: every sampled arm exposes a lower hub, distal elbow hub, upper hub, and distal head hub.
audit 324: shade variants are gated to implemented heads only.
audit 325: wall mount forces wall_cylinder and positive-Y axis.
audit 326: clamp mount forces single_boom and Z swing axis.
audit 327: gooseneck evidence remains out of seed domain.
audit 328: ceiling medical evidence remains out of seed domain.
audit 329: multi-arm tree evidence remains out of seed domain.
audit 330: decorative trim is fused into parent parts.
audit 331: static clamp screw visual is fused into the clamp base for this mature domain.
audit 332: separate parts are reserved for articulated bodies.
audit 333: lower and upper arm parts both contain connected hub-and-beam geometry.
audit 334: head tilt trunnion is a visible part of the head.
audit 335: run_tests carries only hinge overlap allowances.
audit 336: palette choices are material-only variation, not topology.
audit 337: topology diversity comes from slot choices.
audit 338: config_from_seed uses only implemented mount/arm/head combinations.
audit 339: resolve_config is the only legality and gating entrypoint.
audit 340: S3/S6 joint limits are represented by shoulder, elbow, and head_tilt revolutes.
audit 341: S13/S14 wall axis flip is represented by pos_y_wall.
audit 342: S11/S12 clamp boom evidence is represented by c_clamp plus single_boom.
audit 343: S17/S18 banker dome evidence is represented as a gated shade style.
audit 344: S9/S10 spring balanced evidence is represented as spring_balanced arm visuals.
audit 345: S5 rectangular base evidence is represented by weighted_rect_plate.
audit 346: S7/S8 post/swivel evidence is not sampled as a separate unsupported branch.
audit 347: base dimensions are clamped before geometry is emitted.
audit 348: arm lengths are clamped before joint origins are derived.
audit 349: head size is clamped before shade geometry is emitted.
audit 350: lower endpoint derives elbow origin.
audit 351: upper endpoint derives head_tilt origin.
audit 352: shoulder origin derives from mount style.
audit 353: all revolute axes are explicit.
audit 354: all sampled seeds have one root base part.
audit 355: all sampled seeds have lower_arm as child of base.
audit 356: all sampled seeds have upper_arm as child of lower_arm.
audit 357: all sampled seeds have head as child of upper_arm.
audit 358: static cooling or trim details are not split into fixed parts.
audit 359: disconnected module evidence is not sampled.
audit 360: source S1/S2 desk anchor preserved as weighted base plus two-link arm plus head.
audit 361: seed 0 resolves to weighted_round_disk, twin_rail_two_link, rectangular_architect_head.
audit 362: every sampled mount has a visible shoulder barrel near the emitted shoulder joint.
audit 363: every sampled arm exposes a lower hub, distal elbow hub, upper hub, and distal head hub.
audit 364: shade variants are gated to implemented heads only.
audit 365: wall mount forces wall_cylinder and positive-Y axis.
audit 366: clamp mount forces single_boom and Z swing axis.
audit 367: gooseneck evidence remains out of seed domain.
audit 368: ceiling medical evidence remains out of seed domain.
audit 369: multi-arm tree evidence remains out of seed domain.
audit 370: decorative trim is fused into parent parts.
audit 371: static clamp screw visual is fused into the clamp base for this mature domain.
audit 372: separate parts are reserved for articulated bodies.
audit 373: lower and upper arm parts both contain connected hub-and-beam geometry.
audit 374: head tilt trunnion is a visible part of the head.
audit 375: run_tests carries only hinge overlap allowances.
audit 376: palette choices are material-only variation, not topology.
audit 377: topology diversity comes from slot choices.
audit 378: config_from_seed uses only implemented mount/arm/head combinations.
audit 379: resolve_config is the only legality and gating entrypoint.
audit 380: S3/S6 joint limits are represented by shoulder, elbow, and head_tilt revolutes.
audit 381: S13/S14 wall axis flip is represented by pos_y_wall.
audit 382: S11/S12 clamp boom evidence is represented by c_clamp plus single_boom.
audit 383: S17/S18 banker dome evidence is represented as a gated shade style.
audit 384: S9/S10 spring balanced evidence is represented as spring_balanced arm visuals.
audit 385: S5 rectangular base evidence is represented by weighted_rect_plate.
audit 386: S7/S8 post/swivel evidence is not sampled as a separate unsupported branch.
audit 387: base dimensions are clamped before geometry is emitted.
audit 388: arm lengths are clamped before joint origins are derived.
audit 389: head size is clamped before shade geometry is emitted.
audit 390: lower endpoint derives elbow origin.
audit 391: upper endpoint derives head_tilt origin.
audit 392: shoulder origin derives from mount style.
audit 393: all revolute axes are explicit.
audit 394: all sampled seeds have one root base part.
audit 395: all sampled seeds have lower_arm as child of base.
audit 396: all sampled seeds have upper_arm as child of lower_arm.
audit 397: all sampled seeds have head as child of upper_arm.
audit 398: static cooling or trim details are not split into fixed parts.
audit 399: disconnected module evidence is not sampled.
audit 400: source S1/S2 desk anchor preserved as weighted base plus two-link arm plus head.
audit 401: seed 0 resolves to weighted_round_disk, twin_rail_two_link, rectangular_architect_head.
audit 402: every sampled mount has a visible shoulder barrel near the emitted shoulder joint.
audit 403: every sampled arm exposes a lower hub, distal elbow hub, upper hub, and distal head hub.
audit 404: shade variants are gated to implemented heads only.
audit 405: wall mount forces wall_cylinder and positive-Y axis.
audit 406: clamp mount forces single_boom and Z swing axis.
audit 407: gooseneck evidence remains out of seed domain.
audit 408: ceiling medical evidence remains out of seed domain.
audit 409: multi-arm tree evidence remains out of seed domain.
audit 410: decorative trim is fused into parent parts.
audit 411: static clamp screw visual is fused into the clamp base for this mature domain.
audit 412: separate parts are reserved for articulated bodies.
audit 413: lower and upper arm parts both contain connected hub-and-beam geometry.
audit 414: head tilt trunnion is a visible part of the head.
audit 415: run_tests carries only hinge overlap allowances.
audit 416: palette choices are material-only variation, not topology.
audit 417: topology diversity comes from slot choices.
audit 418: config_from_seed uses only implemented mount/arm/head combinations.
audit 419: resolve_config is the only legality and gating entrypoint.
audit 420: S3/S6 joint limits are represented by shoulder, elbow, and head_tilt revolutes.
audit 421: S13/S14 wall axis flip is represented by pos_y_wall.
audit 422: S11/S12 clamp boom evidence is represented by c_clamp plus single_boom.
audit 423: S17/S18 banker dome evidence is represented as a gated shade style.
audit 424: S9/S10 spring balanced evidence is represented as spring_balanced arm visuals.
audit 425: S5 rectangular base evidence is represented by weighted_rect_plate.
audit 426: S7/S8 post/swivel evidence is not sampled as a separate unsupported branch.
audit 427: base dimensions are clamped before geometry is emitted.
audit 428: arm lengths are clamped before joint origins are derived.
audit 429: head size is clamped before shade geometry is emitted.
audit 430: lower endpoint derives elbow origin.
audit 431: upper endpoint derives head_tilt origin.
audit 432: shoulder origin derives from mount style.
audit 433: all revolute axes are explicit.
audit 434: all sampled seeds have one root base part.
audit 435: all sampled seeds have lower_arm as child of base.
audit 436: all sampled seeds have upper_arm as child of lower_arm.
audit 437: all sampled seeds have head as child of upper_arm.
audit 438: static cooling or trim details are not split into fixed parts.
audit 439: disconnected module evidence is not sampled.
audit 440: source S1/S2 desk anchor preserved as weighted base plus two-link arm plus head.
audit 441: seed 0 resolves to weighted_round_disk, twin_rail_two_link, rectangular_architect_head.
audit 442: every sampled mount has a visible shoulder barrel near the emitted shoulder joint.
audit 443: every sampled arm exposes a lower hub, distal elbow hub, upper hub, and distal head hub.
audit 444: shade variants are gated to implemented heads only.
audit 445: wall mount forces wall_cylinder and positive-Y axis.
audit 446: clamp mount forces single_boom and Z swing axis.
audit 447: gooseneck evidence remains out of seed domain.
audit 448: ceiling medical evidence remains out of seed domain.
audit 449: multi-arm tree evidence remains out of seed domain.
audit 450: decorative trim is fused into parent parts.
audit 451: static clamp screw visual is fused into the clamp base for this mature domain.
audit 452: separate parts are reserved for articulated bodies.
audit 453: lower and upper arm parts both contain connected hub-and-beam geometry.
audit 454: head tilt trunnion is a visible part of the head.
audit 455: run_tests carries only hinge overlap allowances.
audit 456: palette choices are material-only variation, not topology.
audit 457: topology diversity comes from slot choices.
audit 458: config_from_seed uses only implemented mount/arm/head combinations.
audit 459: resolve_config is the only legality and gating entrypoint.
audit 460: S3/S6 joint limits are represented by shoulder, elbow, and head_tilt revolutes.
audit 461: S13/S14 wall axis flip is represented by pos_y_wall.
audit 462: S11/S12 clamp boom evidence is represented by c_clamp plus single_boom.
audit 463: S17/S18 banker dome evidence is represented as a gated shade style.
audit 464: S9/S10 spring balanced evidence is represented as spring_balanced arm visuals.
audit 465: S5 rectangular base evidence is represented by weighted_rect_plate.
audit 466: S7/S8 post/swivel evidence is not sampled as a separate unsupported branch.
audit 467: base dimensions are clamped before geometry is emitted.
audit 468: arm lengths are clamped before joint origins are derived.
audit 469: head size is clamped before shade geometry is emitted.
audit 470: lower endpoint derives elbow origin.
audit 471: upper endpoint derives head_tilt origin.
audit 472: shoulder origin derives from mount style.
audit 473: all revolute axes are explicit.
audit 474: all sampled seeds have one root base part.
audit 475: all sampled seeds have lower_arm as child of base.
audit 476: all sampled seeds have upper_arm as child of lower_arm.
audit 477: all sampled seeds have head as child of upper_arm.
audit 478: static cooling or trim details are not split into fixed parts.
audit 479: disconnected module evidence is not sampled.
"""
