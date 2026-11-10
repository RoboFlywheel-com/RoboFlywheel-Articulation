# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import math
import random
import tempfile
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Literal

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
)

# ---------------------------------------------------------------------------
# Discrete parameter literals
# ---------------------------------------------------------------------------

TubeCrossSection = Literal["rectangular", "round", "hex"]
BoomOrientation = Literal["horizontal", "angled", "vertical"]
BaseStyle = Literal[
    "plate",
    "wall_bracket",
    "pedestal",
    "clamp",
    "saddle_cheek",
    "trunnion_yoke",
    "sleeve_socket",
]
EndEffectorStyle = Literal["none", "hook", "light", "camera", "plate", "clamp", "lug"]
Decoration = Literal["none", "warning_stripe", "bolts", "fake_cylinder"]
MaterialStyle = Literal[
    "metal", "black_polymer", "safety_yellow", "safety_orange", "industrial_blue"
]

# ---------------------------------------------------------------------------
# Spine constants (the outer-stage envelope is the spine).
# ---------------------------------------------------------------------------

OUTER_STAGE_LENGTH_MIN = 1.20
OUTER_STAGE_LENGTH_MAX = 2.00

# Per-stage length ratio bucket: 0.6-0.9 uniform per stage (spec).
LENGTH_RATIO_MIN = 0.60
LENGTH_RATIO_MAX = 0.90

# Overlap ratio: fraction of inner stage length retained inside its parent at
# full extension.  spec range 0.15-0.4.
OVERLAP_RATIO_MIN = 0.15
OVERLAP_RATIO_MAX = 0.40

# HOME offset: fraction of parent length used as the joint origin x-offset, so
# at q=0 the child rests partially tucked into the parent rather than rear-
# flush.  73% of dataset 5-star samples use a HOME offset > 0.
HOME_OFFSET_MIN = 0.0
HOME_OFFSET_MAX = 0.20

# Section shrink factor between stages (uniform per stage).
SECTION_SHRINK_MIN = 0.74
SECTION_SHRINK_MAX = 0.86

# Cross-section nominal sizes (parametrised by cross-section type).  The outer
# stage section dimensions seed the spine; inner stages derive from these.
RECT_SECTION_RANGES: tuple[tuple[float, float], tuple[float, float]] = (
    (0.18, 0.32),  # outer y (width)
    (0.16, 0.26),  # outer z (height)
)
ROUND_SECTION_RANGE: tuple[float, float] = (0.085, 0.150)
HEX_SECTION_RANGE: tuple[float, float] = (0.085, 0.140)  # apothem (radius to edge)

# Orientation rpy applied at the FIXED base_bracket -> outer_stage articulation.
ORIENTATION_RPY: dict[BoomOrientation, tuple[float, float, float]] = {
    "horizontal": (0.0, 0.0, 0.0),
    # Vertical: rotate the entire boom so local +X aligns with world +Z.
    "vertical": (0.0, -math.pi / 2.0, 0.0),
    # Angled: 45 degrees above horizontal.
    "angled": (0.0, -math.pi / 4.0, 0.0),
}

# Per-stage paint palettes.  ``stages`` is read by index ``i`` for the i-th
# stage and wraps around when stage_count exceeds the palette length.  This
# matches the dataset's 89% convention of giving each stage its own colour.
MATERIAL_PALETTES: dict[
    MaterialStyle,
    dict[str, object],
] = {
    "metal": {
        "stages": (
            (0.78, 0.80, 0.82, 1.0),  # light steel outer
            (0.66, 0.68, 0.70, 1.0),  # brushed steel
            (0.54, 0.56, 0.58, 1.0),  # darker steel
            (0.42, 0.44, 0.46, 1.0),  # carbon steel
            (0.34, 0.36, 0.40, 1.0),  # dark steel tip
        ),
        "fitting": (0.30, 0.32, 0.36, 1.0),
        "accent": (0.20, 0.22, 0.25, 1.0),
    },
    "black_polymer": {
        "stages": (
            (0.16, 0.16, 0.18, 1.0),
            (0.22, 0.22, 0.24, 1.0),
            (0.12, 0.12, 0.14, 1.0),
            (0.18, 0.18, 0.20, 1.0),
            (0.10, 0.10, 0.12, 1.0),
        ),
        "fitting": (0.08, 0.08, 0.10, 1.0),
        "accent": (0.32, 0.32, 0.34, 1.0),
    },
    "safety_yellow": {
        "stages": (
            (0.94, 0.78, 0.10, 1.0),  # bright yellow outer
            (0.88, 0.70, 0.06, 1.0),  # muted yellow
            (0.78, 0.62, 0.04, 1.0),  # dark yellow
            (0.66, 0.54, 0.10, 1.0),  # olive yellow
            (0.63, 0.66, 0.70, 1.0),  # steel tip
        ),
        "fitting": (0.20, 0.20, 0.22, 1.0),
        "accent": (0.12, 0.12, 0.14, 1.0),
    },
    "safety_orange": {
        "stages": (
            (0.94, 0.50, 0.08, 1.0),
            (0.86, 0.42, 0.06, 1.0),
            (0.76, 0.36, 0.06, 1.0),
            (0.64, 0.30, 0.10, 1.0),
            (0.50, 0.50, 0.52, 1.0),  # steel tip
        ),
        "fitting": (0.22, 0.22, 0.24, 1.0),
        "accent": (0.14, 0.14, 0.16, 1.0),
    },
    "industrial_blue": {
        "stages": (
            (0.20, 0.36, 0.62, 1.0),
            (0.18, 0.32, 0.56, 1.0),
            (0.14, 0.28, 0.50, 1.0),
            (0.12, 0.24, 0.44, 1.0),
            (0.55, 0.58, 0.62, 1.0),
        ),
        "fitting": (0.18, 0.20, 0.24, 1.0),
        "accent": (0.10, 0.10, 0.12, 1.0),
    },
}


# ---------------------------------------------------------------------------
# Config dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class TelescopingBoomConfig:
    stage_count: int = 3
    tube_cross_section: TubeCrossSection = "rectangular"
    boom_orientation: BoomOrientation = "horizontal"
    base_style: BaseStyle = "plate"
    end_effector: EndEffectorStyle = "none"
    decoration: Decoration = "none"
    material_style: MaterialStyle = "metal"

    # Spine - if None they are filled in resolve_config from defaults.
    outer_stage_length: float | None = None
    outer_section: tuple[float, ...] | None = None  # rect: (y,z); round/hex: (r,)
    # Per-stage length_ratio sampled uniformly in [0.6, 0.9] (bucket class).
    length_ratios: tuple[float, ...] | None = None
    # Per-stage section shrink factor sampled in [SECTION_SHRINK_MIN, MAX].
    section_shrinks: tuple[float, ...] | None = None
    overlap_ratio: float = 0.25
    # Per-stage HOME offset fraction (length == stage_count - 1).  Each entry
    # is the fraction of the corresponding parent length used as the joint
    # origin x-offset, so at q=0 the child rests partially tucked inside the
    # parent rather than rear-flush.  When None, resolved to a sampled tuple.
    home_offsets: tuple[float, ...] | None = None
    # Optional cosmetic flourishes.  When True, the chosen base style is
    # augmented with reinforcement plates (doublers) and/or extra hardware.
    base_with_doublers: bool = False
    # Per-stage wear-pad shoes (only meaningful for rectangular cross-section).
    add_wear_pads: bool = False
    # Add a small rear cap and a front wear cap on every stage instead of just
    # the outer stage.
    per_stage_caps: bool = False

    name: str = "reference_telescoping_boom"


@dataclass(frozen=True)
class ResolvedTelescopingBoomConfig:
    stage_count: int
    tube_cross_section: TubeCrossSection
    boom_orientation: BoomOrientation
    base_style: BaseStyle
    end_effector: EndEffectorStyle
    decoration: Decoration
    material_style: MaterialStyle
    outer_stage_length: float
    outer_section: tuple[float, ...]
    length_ratios: tuple[float, ...]
    section_shrinks: tuple[float, ...]
    overlap_ratio: float
    home_offsets: tuple[float, ...]  # length == stage_count - 1
    base_with_doublers: bool
    add_wear_pads: bool
    per_stage_caps: bool
    # Derived per-stage values (length, section tuple), indexed 0..stage_count-1
    stage_lengths: tuple[float, ...]
    stage_sections: tuple[tuple[float, ...], ...]
    name: str


# ---------------------------------------------------------------------------
# Seed-based config sampler
# ---------------------------------------------------------------------------


def _sample_outer_section(rng: random.Random, cross_section: TubeCrossSection) -> tuple[float, ...]:
    if cross_section == "rectangular":
        wy = round(rng.uniform(*RECT_SECTION_RANGES[0]), 3)
        wz = round(rng.uniform(*RECT_SECTION_RANGES[1]), 3)
        return (wy, wz)
    if cross_section == "round":
        r = round(rng.uniform(*ROUND_SECTION_RANGE), 3)
        return (r,)
    # hex - apothem (radius from center to flat face)
    r = round(rng.uniform(*HEX_SECTION_RANGE), 3)
    return (r,)


def config_from_seed(seed: int) -> TelescopingBoomConfig:
    rng = random.Random(seed)
    # Dataset distribution (n=44) is 3 (15), 4 (17), 5 (12); no 2-stage booms.
    stage_count = rng.choices((3, 4, 5), weights=(0.35, 0.40, 0.25), k=1)[0]
    # Dataset is overwhelmingly rectangular (~57%); hex effectively absent so
    # downweight it heavily and put the rest on round / rectangular.
    cross_section: TubeCrossSection = rng.choices(
        ("rectangular", "round", "hex"),
        weights=(0.65, 0.30, 0.05),
        k=1,
    )[0]
    orientation: BoomOrientation = rng.choices(
        ("horizontal", "angled", "vertical"),
        weights=(0.55, 0.30, 0.15),
        k=1,
    )[0]
    # Dataset weighting: saddle_cheek mount (cheek brackets + saddle) appears
    # in >50% of 5-star samples; wall_bracket / trunnion_yoke / sleeve_socket
    # fill out the rest of the mount typology in dataset prompts
    # ("wall-backed", "trunnion-collar column", "socket sleeve").
    base_style: BaseStyle = rng.choices(
        (
            "plate",
            "wall_bracket",
            "pedestal",
            "clamp",
            "saddle_cheek",
            "trunnion_yoke",
            "sleeve_socket",
        ),
        weights=(0.12, 0.18, 0.07, 0.12, 0.30, 0.11, 0.10),
        k=1,
    )[0]
    # Dataset has zero hook end-effectors; faceplate/lug/camera/clamp dominate.
    end_effector: EndEffectorStyle = rng.choices(
        ("none", "hook", "light", "camera", "plate", "clamp", "lug"),
        weights=(0.16, 0.02, 0.08, 0.18, 0.22, 0.14, 0.20),
        k=1,
    )[0]
    decoration: Decoration = rng.choices(
        ("none", "warning_stripe", "bolts", "fake_cylinder"),
        weights=(0.40, 0.25, 0.20, 0.15),
        k=1,
    )[0]
    material_style: MaterialStyle = rng.choices(
        ("metal", "black_polymer", "safety_yellow", "safety_orange", "industrial_blue"),
        weights=(0.30, 0.18, 0.24, 0.16, 0.12),
        k=1,
    )[0]
    outer_stage_length = round(rng.uniform(OUTER_STAGE_LENGTH_MIN, OUTER_STAGE_LENGTH_MAX), 3)
    outer_section = _sample_outer_section(rng, cross_section)
    # Per-stage length_ratio (bucket class + continuous range): for each child
    # stage i in 1..stage_count-1 sample a fresh ratio in [0.6, 0.9].
    length_ratios = tuple(
        round(rng.uniform(LENGTH_RATIO_MIN, LENGTH_RATIO_MAX), 3) for _ in range(stage_count - 1)
    )
    section_shrinks = tuple(
        round(rng.uniform(SECTION_SHRINK_MIN, SECTION_SHRINK_MAX), 3)
        for _ in range(stage_count - 1)
    )
    overlap_ratio = round(rng.uniform(OVERLAP_RATIO_MIN, OVERLAP_RATIO_MAX), 3)
    # Per-stage HOME offset.  73% of dataset uses a non-zero HOME so weight
    # accordingly: 25% chance of zero (rears flush) and 75% chance of a random
    # offset in [HOME_OFFSET_MIN, HOME_OFFSET_MAX].
    home_offsets = tuple(
        0.0 if rng.random() < 0.25 else round(rng.uniform(HOME_OFFSET_MIN, HOME_OFFSET_MAX), 3)
        for _ in range(stage_count - 1)
    )
    base_with_doublers = rng.random() < 0.45  # ~25% in dataset but cheap to add
    add_wear_pads = (cross_section == "rectangular") and (rng.random() < 0.55)
    per_stage_caps = rng.random() < 0.50
    return TelescopingBoomConfig(
        stage_count=stage_count,
        tube_cross_section=cross_section,
        boom_orientation=orientation,
        base_style=base_style,
        end_effector=end_effector,
        decoration=decoration,
        material_style=material_style,
        outer_stage_length=outer_stage_length,
        outer_section=outer_section,
        length_ratios=length_ratios,
        section_shrinks=section_shrinks,
        overlap_ratio=overlap_ratio,
        home_offsets=home_offsets,
        base_with_doublers=base_with_doublers,
        add_wear_pads=add_wear_pads,
        per_stage_caps=per_stage_caps,
        name=f"seeded_telescoping_boom_{seed}",
    )


# ---------------------------------------------------------------------------
# resolve_config: spine -> derived per-stage geometry
# ---------------------------------------------------------------------------


def _validate_section(cross_section: TubeCrossSection, section: tuple[float, ...]) -> None:
    if cross_section == "rectangular":
        if len(section) != 2:
            raise ValueError(f"rectangular cross-section requires (y, z); got {section!r}")
        if section[0] <= 0.0 or section[1] <= 0.0:
            raise ValueError(f"rectangular section dims must be positive, got {section!r}")
    else:
        if len(section) != 1:
            raise ValueError(f"{cross_section} cross-section requires (radius,); got {section!r}")
        if section[0] <= 0.0:
            raise ValueError(f"{cross_section} radius must be positive, got {section!r}")


def _shrink_section(
    cross_section: TubeCrossSection, section: tuple[float, ...], shrink: float
) -> tuple[float, ...]:
    if cross_section == "rectangular":
        return (section[0] * shrink, section[1] * shrink)
    return (section[0] * shrink,)


def _normalize_section(
    cross_section: TubeCrossSection, section: tuple[float, ...]
) -> tuple[float, ...]:
    """Reconcile ``outer_section``'s shape with ``tube_cross_section``.

    Raw overrides can swap the cross-section type without re-deriving the
    section dims; convert between the (y, z) and (radius,) representations by
    matching mean half-extents so the envelope stays close to the sampled size.
    Degenerate shapes fall back to the deterministic default section.
    """
    if cross_section == "rectangular":
        if len(section) == 2:
            return section
        if len(section) == 1:
            r = section[0]
            return (2.0 * r, 1.75 * r)
    else:
        if len(section) == 1:
            return section
        if len(section) == 2:
            y, z = section
            return ((y + z) / 4.0,)
    return _sample_outer_section(random.Random(0), cross_section)


def _fit_per_stage(values: tuple[float, ...], needed: int, pad: float) -> tuple[float, ...]:
    """Reconcile a per-stage tuple's length with ``stage_count - 1``.

    Raw overrides can replace ``stage_count`` without re-deriving the dependent
    per-stage tuples; truncate extras and pad missing entries with ``pad`` so
    the spine stays self-consistent.
    """
    if len(values) >= needed:
        return values[:needed]
    return values + tuple(pad for _ in range(needed - len(values)))


def resolve_config(config: TelescopingBoomConfig) -> ResolvedTelescopingBoomConfig:
    if config.stage_count not in {3, 4, 5}:
        raise ValueError(f"stage_count must be in {{3,4,5}}, got {config.stage_count}")
    if config.tube_cross_section not in {"rectangular", "round", "hex"}:
        raise ValueError(f"Unsupported tube_cross_section: {config.tube_cross_section}")
    if config.boom_orientation not in ORIENTATION_RPY:
        raise ValueError(f"Unsupported boom_orientation: {config.boom_orientation}")
    if config.base_style not in {
        "plate",
        "wall_bracket",
        "pedestal",
        "clamp",
        "saddle_cheek",
        "trunnion_yoke",
        "sleeve_socket",
    }:
        raise ValueError(f"Unsupported base_style: {config.base_style}")
    if config.end_effector not in {"none", "hook", "light", "camera", "plate", "clamp", "lug"}:
        raise ValueError(f"Unsupported end_effector: {config.end_effector}")
    if config.decoration not in {"none", "warning_stripe", "bolts", "fake_cylinder"}:
        raise ValueError(f"Unsupported decoration: {config.decoration}")
    if config.material_style not in MATERIAL_PALETTES:
        raise ValueError(f"Unsupported material_style: {config.material_style}")
    if not (OVERLAP_RATIO_MIN - 1e-9 <= config.overlap_ratio <= OVERLAP_RATIO_MAX + 1e-9):
        raise ValueError(
            f"overlap_ratio must be in [{OVERLAP_RATIO_MIN}, {OVERLAP_RATIO_MAX}]; "
            f"got {config.overlap_ratio}"
        )

    outer_length = (
        config.outer_stage_length
        if config.outer_stage_length is not None
        else (OUTER_STAGE_LENGTH_MIN + OUTER_STAGE_LENGTH_MAX) * 0.5
    )
    if outer_length < 0.30:
        raise ValueError(f"outer_stage_length too small: {outer_length}")

    if config.outer_section is None:
        rng_default = random.Random(0)
        outer_section = _sample_outer_section(rng_default, config.tube_cross_section)
    else:
        outer_section = _normalize_section(
            config.tube_cross_section, tuple(float(v) for v in config.outer_section)
        )
    _validate_section(config.tube_cross_section, outer_section)

    # Per-stage length ratios.  Need exactly stage_count - 1 values; raw
    # overrides can change stage_count alone, so re-fit the tuple's length.
    if config.length_ratios is None:
        length_ratios = tuple(
            (LENGTH_RATIO_MIN + LENGTH_RATIO_MAX) * 0.5 for _ in range(config.stage_count - 1)
        )
    else:
        length_ratios = _fit_per_stage(
            tuple(float(v) for v in config.length_ratios),
            config.stage_count - 1,
            (LENGTH_RATIO_MIN + LENGTH_RATIO_MAX) * 0.5,
        )
        for lr in length_ratios:
            if not (LENGTH_RATIO_MIN - 1e-9 <= lr <= LENGTH_RATIO_MAX + 1e-9):
                raise ValueError(
                    f"length_ratio entries must be in "
                    f"[{LENGTH_RATIO_MIN}, {LENGTH_RATIO_MAX}]; got {lr}"
                )

    if config.section_shrinks is None:
        section_shrinks = tuple(
            (SECTION_SHRINK_MIN + SECTION_SHRINK_MAX) * 0.5 for _ in range(config.stage_count - 1)
        )
    else:
        section_shrinks = _fit_per_stage(
            tuple(float(v) for v in config.section_shrinks),
            config.stage_count - 1,
            (SECTION_SHRINK_MIN + SECTION_SHRINK_MAX) * 0.5,
        )
        for s in section_shrinks:
            if not (SECTION_SHRINK_MIN - 1e-9 <= s <= SECTION_SHRINK_MAX + 1e-9):
                raise ValueError(
                    f"section_shrinks entries must be in "
                    f"[{SECTION_SHRINK_MIN}, {SECTION_SHRINK_MAX}]; got {s}"
                )

    # Derive per-stage lengths and sections.  Stage 0 is the outer; subsequent
    # stages shrink by the per-edge ratio.
    stage_lengths_list: list[float] = [outer_length]
    stage_sections_list: list[tuple[float, ...]] = [outer_section]
    for i, lr in enumerate(length_ratios):
        prev_len = stage_lengths_list[-1]
        new_len = prev_len * lr
        if new_len < 0.18:
            # Numeric guard: do not allow a stage shorter than 18 cm because
            # overlap math then collapses.
            raise ValueError(
                f"derived stage {i + 1} length too small ({new_len:.3f}m); "
                f"increase length_ratio or outer_stage_length."
            )
        stage_lengths_list.append(new_len)
        prev_section = stage_sections_list[-1]
        new_section = _shrink_section(config.tube_cross_section, prev_section, section_shrinks[i])
        # Validate that inner section dims are strictly smaller than outer.
        for old, new in zip(prev_section, new_section):
            if new >= old - 1e-6:
                raise ValueError(
                    f"inner stage {i + 1} section {new_section} not strictly smaller than "
                    f"parent {prev_section}"
                )
        if new_section[0] < 0.03:
            raise ValueError(
                f"stage {i + 1} section too small ({new_section}); "
                f"raise section_shrinks or outer_section."
            )
        stage_sections_list.append(new_section)

    # Resolve home_offsets: default to all-zero if missing; clamp values to the
    # allowed range and to the per-stage physical limit
    # (home_offset_x + overlap_ratio*inner_length <= parent_length).
    if config.home_offsets is None:
        home_offsets = tuple(0.0 for _ in range(config.stage_count - 1))
    else:
        home_offsets = _fit_per_stage(
            tuple(float(v) for v in config.home_offsets), config.stage_count - 1, 0.0
        )
    # Clamp HOME offsets so the joint upper stays positive
    # (upper = (1 - home_offset_frac) * parent_length - overlap_ratio * inner_length).
    clamped_home_offsets: list[float] = []
    for i, frac in enumerate(home_offsets):
        if frac < 0.0 - 1e-9:
            raise ValueError(f"home_offsets[{i}]={frac} must be >= 0")
        # Reserve at least 0.05 m of joint travel after the overlap retention.
        parent_len = stage_lengths_list[i]
        inner_len = stage_lengths_list[i + 1]
        max_frac = max(
            0.0,
            min(HOME_OFFSET_MAX, 1.0 - (config.overlap_ratio * inner_len + 0.05) / parent_len),
        )
        clamped_home_offsets.append(min(frac, max_frac))

    return ResolvedTelescopingBoomConfig(
        stage_count=config.stage_count,
        tube_cross_section=config.tube_cross_section,
        boom_orientation=config.boom_orientation,
        base_style=config.base_style,
        end_effector=config.end_effector,
        decoration=config.decoration,
        material_style=config.material_style,
        outer_stage_length=outer_length,
        outer_section=outer_section,
        length_ratios=length_ratios,
        section_shrinks=section_shrinks,
        overlap_ratio=config.overlap_ratio,
        home_offsets=tuple(clamped_home_offsets),
        base_with_doublers=bool(config.base_with_doublers),
        add_wear_pads=bool(config.add_wear_pads),
        per_stage_caps=bool(config.per_stage_caps),
        stage_lengths=tuple(stage_lengths_list),
        stage_sections=tuple(stage_sections_list),
        name=config.name,
    )


# ---------------------------------------------------------------------------
# Cross-section builders.  Each adds geometry to a stage part along local +X
# from x=0 (rear) to x=stage_length (front).  The "section" tuple semantics
# depend on cross-section type.  These are visual-only and produce a stable
# nested set of named visuals.
# ---------------------------------------------------------------------------


def _wall_thickness(min_section_dim: float) -> float:
    """Wall thickness used for hollow tubes; floors at 6 mm."""
    return max(0.006, min_section_dim * 0.07)


def _build_rect_stage(
    stage_part,
    *,
    section: tuple[float, ...],
    length: float,
    material,
    prefix: str,
) -> None:
    """Hollow rectangular tube: 4 thin plates (top, bottom, left web, right web).

    The cavity (length, y - 2*wall, z - 2*wall) is open along the full +X length
    so the next inner stage can be visually seen sliding through it.
    """
    y, z = section
    wall = _wall_thickness(min(y, z))
    inner_z = max(0.0, z - 2.0 * wall)
    # Bottom plate (at -z face).
    stage_part.visual(
        Box((length, y, wall)),
        origin=Origin(xyz=(length / 2.0, 0.0, -z / 2.0 + wall / 2.0)),
        material=material,
        name=f"{prefix}_bottom_plate", material_class_id="metal.paint_coated",
    )
    # Top plate (at +z face).
    stage_part.visual(
        Box((length, y, wall)),
        origin=Origin(xyz=(length / 2.0, 0.0, +z / 2.0 - wall / 2.0)),
        material=material,
        name=f"{prefix}_top_plate", material_class_id="metal.paint_coated",
    )
    # Right web (at +y face).
    stage_part.visual(
        Box((length, wall, inner_z)),
        origin=Origin(xyz=(length / 2.0, +y / 2.0 - wall / 2.0, 0.0)),
        material=material,
        name=f"{prefix}_right_web", material_class_id="metal.paint_coated",
    )
    # Left web (at -y face).
    stage_part.visual(
        Box((length, wall, inner_z)),
        origin=Origin(xyz=(length / 2.0, -y / 2.0 + wall / 2.0, 0.0)),
        material=material,
        name=f"{prefix}_left_web", material_class_id="metal.paint_coated",
    )


def _build_round_stage(
    stage_part,
    *,
    section: tuple[float, ...],
    length: float,
    material,
    prefix: str,
) -> None:
    """Hollow round tube approximated by 16 thin tangential face plates.

    Each face is a Box(length, wall_thickness, face_width) rotated about the
    boom axis so the wall thickness is in the radial direction and the face
    width is tangent to the cylinder.  16 faces are visually indistinguishable
    from a smooth cylinder at typical render scales but leave the cavity open
    for the inner stage to be visible.
    """
    (radius,) = section
    n_sides = 16
    wall = _wall_thickness(radius)
    face_width = 2.0 * radius * math.tan(math.pi / n_sides)
    for k in range(n_sides):
        theta = (2.0 * math.pi / n_sides) * k
        cy = radius * math.cos(theta)
        cz = radius * math.sin(theta)
        # After rpy=(theta, 0, 0): local +Y points radially outward at angle
        # theta, local +Z points tangentially.  So Box(length, wall, width)
        # has wall along radial and width along tangent.
        stage_part.visual(
            Box((length, wall, face_width)),
            origin=Origin(xyz=(length / 2.0, cy, cz), rpy=(theta, 0.0, 0.0)),
            material=material,
            name=f"{prefix}_round_face_{k}", material_class_id="metal.paint_coated",
        )


def _build_hex_stage(
    stage_part,
    *,
    section: tuple[float, ...],
    length: float,
    material,
    prefix: str,
) -> None:
    """Hollow hexagonal tube: 6 tangential face plates around the boom axis.

    ``section[0]`` is the apothem (centre-to-flat radius).  Each face is a
    Box(length, wall, face_width) with face_width tangent to the hex (the
    side length 2 * apothem * tan(pi/6)) and wall in the radial direction.
    Previous versions placed the face_width along the radial direction by
    mistake, producing 6 radial fins instead of a closed hex tube.
    """
    (apothem,) = section
    face_width = 2.0 * apothem * math.tan(math.pi / 6.0)
    wall = _wall_thickness(apothem)
    for k in range(6):
        theta = (math.pi / 3.0) * k
        cy = apothem * math.cos(theta)
        cz = apothem * math.sin(theta)
        stage_part.visual(
            Box((length, wall, face_width)),
            origin=Origin(xyz=(length / 2.0, cy, cz), rpy=(theta, 0.0, 0.0)),
            material=material,
            name=f"{prefix}_hex_face_{k}", material_class_id="metal.paint_coated",
        )


CROSS_SECTION_BUILDERS = {
    "rectangular": _build_rect_stage,
    "round": _build_round_stage,
    "hex": _build_hex_stage,
}


def _section_bbox_yz(
    cross_section: TubeCrossSection, section: tuple[float, ...]
) -> tuple[float, float]:
    """Return half-extents (half_y, half_z) of the bounding box of one stage
    section in its local frame, i.e. the maximum |y| and |z| of any visual.

    With hollow construction, each face plate has its CENTRE at the section's
    nominal radius (apothem) and extends ``wall/2`` further outward, so the
    AABB grows by ``wall/2`` in the radial direction.
    """
    if cross_section == "rectangular":
        return (section[0] * 0.5, section[1] * 0.5)
    if cross_section == "round":
        wall = _wall_thickness(section[0])
        return (section[0] + wall * 0.5, section[0] + wall * 0.5)
    # hex: outer circumscribed radius = apothem / cos(pi/6); plus wall growth.
    wall = _wall_thickness(section[0])
    outer = section[0] / math.cos(math.pi / 6.0) + wall * 0.5
    return (outer, outer)


def _add_rear_cap(
    stage_part,
    *,
    cross_section: TubeCrossSection,
    section: tuple[float, ...],
    material,
    name: str,
) -> None:
    """Close the rear (x=0) face of a stage's hollow tube with a thin cap."""
    cap_t = 0.010
    if cross_section == "rectangular":
        y, z = section
        stage_part.visual(
            Box((cap_t, y, z)),
            origin=Origin(xyz=(cap_t / 2.0, 0.0, 0.0)),
            material=material,
            name=name, material_class_id="metal.blackened_gunmetal",
        )
    elif cross_section == "round":
        (radius,) = section
        wall = _wall_thickness(radius)
        stage_part.visual(
            Cylinder(radius=radius + wall * 0.5, length=cap_t),
            origin=Origin(xyz=(cap_t / 2.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=material,
            name=name, material_class_id="metal.blackened_gunmetal",
        )
    else:  # hex
        (apothem,) = section
        wall = _wall_thickness(apothem)
        outer_radius = apothem / math.cos(math.pi / 6.0) + wall * 0.5
        stage_part.visual(
            Cylinder(radius=outer_radius, length=cap_t),
            origin=Origin(xyz=(cap_t / 2.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=material,
            name=name, material_class_id="metal.blackened_gunmetal",
        )


def _add_rear_guide_bushing(
    stage_part,
    *,
    cross_section: TubeCrossSection,
    parent_section: tuple[float, ...],
    material,
    name: str,
) -> None:
    """Add a rear slide bushing on an inner stage that reaches out to the PARENT
    tube's inner wall.

    Hollow stages shrink by more than one wall thickness per nesting level, so a
    child tube floats coaxially inside its parent with a few-mm radial clearance
    and never physically touches it at the retracted rest pose (the parent's
    front locking collar only engages once the boom extends).  A real telescoping
    boom carries a slide bearing / guide bushing at the inner-tube rear that
    always rides against the parent bore; this bushing sits just inside the
    child rear (x >= 0, always nested inside the parent) and overlaps the parent
    bore wall by ~3 mm so the stages stay a single grounded, connected body
    across the whole travel range.
    """
    bush_len = 0.04
    # Seat the bushing a little forward of the tube rear so it clears the base
    # bracket's rear mount seat (which reaches ~7 mm into the outer stage) while
    # still riding well inside the parent bore at the retracted rest pose.
    x_center = 0.030 + bush_len / 2.0
    grip = 0.003  # radial bite into the parent bore wall (guarantees contact)
    if cross_section == "rectangular":
        py, pz = parent_section
        pw = _wall_thickness(min(py, pz))
        stage_part.visual(
            Box((bush_len, py - 2.0 * pw + 2.0 * grip, pz - 2.0 * pw + 2.0 * grip)),
            origin=Origin(xyz=(x_center, 0.0, 0.0)),
            material=material,
            name=name, material_class_id="metal.bronze_cast",
        )
    elif cross_section == "round":
        # Round/hex face plates are centred on the nominal radius, so the bore
        # inner surface sits at ``r - wall/2`` (not ``r - wall``).
        (pr,) = parent_section
        pw = _wall_thickness(pr)
        stage_part.visual(
            Cylinder(radius=pr - pw / 2.0 + grip, length=bush_len),
            origin=Origin(xyz=(x_center, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=material,
            name=name, material_class_id="metal.bronze_cast",
        )
    else:  # hex
        (pa,) = parent_section
        pw = _wall_thickness(pa)
        stage_part.visual(
            Cylinder(radius=pa - pw / 2.0 + grip, length=bush_len),
            origin=Origin(xyz=(x_center, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=material,
            name=name, material_class_id="metal.bronze_cast",
        )


def _add_front_cap(
    stage_part,
    *,
    cross_section: TubeCrossSection,
    section: tuple[float, ...],
    length: float,
    material,
    name: str,
) -> None:
    """Close the FRONT (x=length) face of a stage's hollow tube with a mounting
    spigot. Provides real weld material at the tube tip AND protrudes forward
    into the end-effector's mounting region so the two are in physical contact
    (EE builders offset their geometry a short way forward, which would otherwise
    leave the EE a floating, support-disconnected island). The EE<->stage overlap
    is a declared allowance.
    """
    cap_t = 0.028
    # Protrude ~16 mm past the tube front to reach the largest EE rear offset.
    x_center = length + 0.016 - cap_t / 2.0
    if cross_section == "rectangular":
        y, z = section
        stage_part.visual(
            Box((cap_t, y, z)),
            origin=Origin(xyz=(x_center, 0.0, 0.0)),
            material=material,
            name=name, material_class_id="metal.blackened_gunmetal",
        )
    elif cross_section == "round":
        (radius,) = section
        wall = _wall_thickness(radius)
        stage_part.visual(
            Cylinder(radius=radius + wall * 0.5, length=cap_t),
            origin=Origin(xyz=(x_center, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=material,
            name=name, material_class_id="metal.blackened_gunmetal",
        )
    else:  # hex
        (apothem,) = section
        wall = _wall_thickness(apothem)
        outer_radius = apothem / math.cos(math.pi / 6.0) + wall * 0.5
        stage_part.visual(
            Cylinder(radius=outer_radius, length=cap_t),
            origin=Origin(xyz=(x_center, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=material,
            name=name, material_class_id="metal.blackened_gunmetal",
        )


def _add_base_mount_seat(
    base_part,
    *,
    half_y: float,
    half_z: float,
    z_center: float,
    material,
) -> None:
    """Add a rear mounting bulkhead centred on the boom axis at the weld plane.

    Side-gripping base fittings (cheeks, yoke arms, clamp struts) leave no
    material on the boom axis and stand off the tube walls, so the base would be
    physically disconnected from the outer stage. This backing bulkhead bridges
    the side arms, puts real material on the axis, and seats forward just far
    enough to overlap the outer stage rear (~2 mm) so the base bracket actually
    captures and stays in contact with the boom rear.  The overlap is kept small
    (< the 5 mm overlap tolerance) because at a tucked rest pose the first inner
    stage's rear is coincident with the outer rear.
    """
    seat_t = 0.020
    base_part.visual(
        Box((seat_t, 2.0 * half_y, 2.0 * half_z)),
        origin=Origin(xyz=(-seat_t / 2.0 + 0.002, 0.0, z_center)),
        material=material,
        name="boom_mount_seat", material_class_id="metal.paint_coated",
    )


# ---------------------------------------------------------------------------
# Base bracket builders.
# ---------------------------------------------------------------------------


def _build_base_plate(
    base_part,
    *,
    section_half_extent: float,
    material,
    fitting_material,
) -> None:
    """Flat baseplate (XY plane) supporting the boom from below."""
    plate_t = 0.03
    plate_size = max(0.42, section_half_extent * 4.5)
    base_part.visual(
        Box((plate_size, plate_size, plate_t)),
        origin=Origin(xyz=(0.0, 0.0, -section_half_extent - plate_t / 2.0 - 0.01)),
        material=material,
        name="base_plate", material_class_id="metal.paint_coated",
    )
    # Hub seat that captures the outer stage rear cap.
    hub_t = 0.06
    base_part.visual(
        Box((hub_t, section_half_extent * 2.4, section_half_extent * 2.4)),
        origin=Origin(xyz=(-hub_t / 2.0, 0.0, 0.0)),
        material=fitting_material,
        name="base_hub_seat", material_class_id="metal.blackened_gunmetal",
    )
    # Anchor bolts (visual-only).
    for sx, sy in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
        base_part.visual(
            Cylinder(radius=0.012, length=0.04),
            origin=Origin(
                xyz=(
                    sx * (plate_size * 0.40),
                    sy * (plate_size * 0.40),
                    -section_half_extent - plate_t - 0.01,
                ),
            ),
            material=fitting_material,
            name=f"base_bolt_{'r' if sx > 0 else 'l'}{'f' if sy > 0 else 'b'}", material_class_id="metal.steel_bare",
        )


def _build_base_wall_bracket(
    base_part,
    *,
    section_half_extent: float,
    material,
    fitting_material,
) -> None:
    """Wall mount plate behind the boom."""
    plate_t = 0.024
    plate_w = max(0.40, section_half_extent * 4.2)
    plate_h = max(0.40, section_half_extent * 4.2)
    base_part.visual(
        Box((plate_t, plate_w, plate_h)),
        origin=Origin(xyz=(-plate_t / 2.0 - 0.02, 0.0, 0.0)),
        material=material,
        name="wall_plate", material_class_id="metal.paint_coated",
    )
    base_part.visual(
        Box((0.08, section_half_extent * 2.4, section_half_extent * 2.4)),
        origin=Origin(xyz=(-0.04, 0.0, 0.0)),
        material=fitting_material,
        name="bracket_collar", material_class_id="metal.blackened_gunmetal",
    )
    for y, label in ((-plate_w * 0.36, "left"), (plate_w * 0.36, "right")):
        for z, vlabel in ((-plate_h * 0.36, "bottom"), (plate_h * 0.36, "top")):
            base_part.visual(
                Cylinder(radius=0.011, length=0.032),
                origin=Origin(xyz=(-plate_t - 0.018, y, z), rpy=(0.0, math.pi / 2.0, 0.0)),
                material=fitting_material,
                name=f"wall_bolt_{label}_{vlabel}", material_class_id="metal.steel_bare",
            )


def _build_base_pedestal(
    base_part,
    *,
    section_half_extent: float,
    material,
    fitting_material,
) -> None:
    column_h = 0.45
    column_r = max(0.06, section_half_extent * 1.1)
    base_part.visual(
        Cylinder(radius=column_r, length=column_h),
        origin=Origin(xyz=(-0.05, 0.0, -section_half_extent - column_h / 2.0 - 0.005)),
        material=material,
        name="pedestal_column", material_class_id="metal.paint_coated",
    )
    foot_t = 0.025
    foot_size = column_r * 2.6
    base_part.visual(
        Box((foot_size, foot_size, foot_t)),
        origin=Origin(
            # Embed 3 mm into the column foot so it stays welded (was 5 mm below).
            xyz=(-0.05, 0.0, -section_half_extent - column_h - foot_t / 2.0 + 0.003),
        ),
        material=fitting_material,
        name="pedestal_foot", material_class_id="metal.paint_coated",
    )
    # Trunnion collar around outer stage rear.
    base_part.visual(
        Cylinder(radius=section_half_extent * 1.3, length=0.10),
        origin=Origin(xyz=(0.02, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=fitting_material,
        name="pedestal_collar", material_class_id="metal.blackened_gunmetal",
    )


def _build_base_clamp(
    base_part,
    *,
    section_half_extent: float,
    material,
    fitting_material,
) -> None:
    """Two semi-cylindrical halves clamped around the rear of the outer stage."""
    clamp_t = 0.06
    half_h = section_half_extent + 0.05
    base_part.visual(
        Box((clamp_t, section_half_extent * 2.6, 0.02)),
        origin=Origin(xyz=(-clamp_t / 2.0, 0.0, half_h)),
        material=material,
        name="clamp_upper_half", material_class_id="metal.paint_coated",
    )
    base_part.visual(
        Box((clamp_t, section_half_extent * 2.6, 0.02)),
        origin=Origin(xyz=(-clamp_t / 2.0, 0.0, -half_h)),
        material=material,
        name="clamp_lower_half", material_class_id="metal.paint_coated",
    )
    for sy, label in ((1, "right"), (-1, "left")):
        base_part.visual(
            Box((clamp_t, 0.02, half_h * 2.0)),
            origin=Origin(xyz=(-clamp_t / 2.0, sy * section_half_extent * 1.20, 0.0)),
            material=fitting_material,
            name=f"clamp_{label}_strut", material_class_id="metal.steel_bare",
        )
        # Bolt heads
        for sz, vlabel in ((1, "top"), (-1, "bottom")):
            base_part.visual(
                Cylinder(radius=0.012, length=0.035),
                origin=Origin(
                    xyz=(
                        -clamp_t / 2.0,
                        sy * section_half_extent * 1.20,
                        sz * (half_h - 0.02),
                    ),
                    rpy=(math.pi / 2.0, 0.0, 0.0),
                ),
                material=fitting_material,
                name=f"clamp_bolt_{label}_{vlabel}", material_class_id="metal.steel_bare",
            )
    # Axis bulkhead bridging the two clamp struts (weld seat for the boom rear).
    _add_base_mount_seat(
        base_part,
        half_y=section_half_extent * 1.28,
        half_z=section_half_extent * 1.10,
        z_center=0.0,
        material=fitting_material,
    )
    # Mounting tongue extending behind.  Runs forward far enough to overlap the
    # axis bulkhead above (was floating a few mm behind it as a disconnected
    # island).
    base_part.visual(
        Box((0.16, section_half_extent * 2.2, 0.04)),
        origin=Origin(xyz=(-0.09, 0.0, 0.0)),
        material=material,
        name="clamp_mount_tongue", material_class_id="metal.paint_coated",
    )


def _build_base_saddle_cheek(
    base_part,
    *,
    section_half_extent: float,
    material,
    fitting_material,
) -> None:
    """The dataset's most common root pattern: a flat base plate + two vertical
    cheek brackets that hug the outer stage rear + a small saddle plate that
    sits under the boom (sometimes with a rear stop spine).
    """
    plate_t = 0.028
    plate_size = max(0.50, section_half_extent * 5.0)
    cheek_t = 0.014
    cheek_h = section_half_extent * 2.4 + 0.06
    rear_offset_x = -0.05
    base_part.visual(
        Box((plate_size, plate_size, plate_t)),
        origin=Origin(
            xyz=(rear_offset_x, 0.0, -section_half_extent - plate_t / 2.0 - 0.008),
        ),
        material=material,
        name="base_plate", material_class_id="metal.paint_coated",
    )
    # Left and right cheeks: vertical plates straddling the outer stage rear.
    for sy, side in ((+1.0, "left"), (-1.0, "right")):
        base_part.visual(
            Box((plate_size * 0.55, cheek_t, cheek_h)),
            origin=Origin(
                xyz=(
                    rear_offset_x - plate_size * 0.10,
                    sy * (section_half_extent + cheek_t / 2.0 + 0.005),
                    section_half_extent * 0.05,
                ),
            ),
            material=material,
            name=f"{side}_cheek", material_class_id="metal.paint_coated",
        )
    # Saddle plate that sits under the boom.
    saddle_w = section_half_extent * 2.0 + 0.04
    base_part.visual(
        Box((plate_size * 0.55, saddle_w, 0.014)),
        origin=Origin(
            xyz=(rear_offset_x - plate_size * 0.05, 0.0, -section_half_extent - 0.012),
        ),
        material=fitting_material,
        name="saddle", material_class_id="metal.steel_bare",
    )
    # Small rear spine (acts as a back stop).  It rises from the base plate up
    # past the boom axis; its bottom is dropped to embed 4 mm into the base plate
    # (otherwise it floats a few mm above it as a disconnected island).
    spine_top_z = -section_half_extent * 0.20 + cheek_h * 0.55 / 2.0
    spine_bottom_z = -section_half_extent - plate_t / 2.0 - 0.008 - 0.004
    base_part.visual(
        Box((0.024, saddle_w * 0.75, spine_top_z - spine_bottom_z)),
        origin=Origin(
            xyz=(
                rear_offset_x - plate_size * 0.38,
                0.0,
                (spine_top_z + spine_bottom_z) / 2.0,
            ),
        ),
        material=fitting_material,
        name="rear_spine", material_class_id="metal.steel_bare",
    )
    # Axis bulkhead bridging the two cheeks (weld seat for the boom rear).
    _add_base_mount_seat(
        base_part,
        half_y=section_half_extent + 0.020,
        half_z=section_half_extent * 1.20,
        z_center=section_half_extent * 0.05,
        material=fitting_material,
    )


def _add_base_doublers(
    base_part,
    *,
    section_half_extent: float,
    material,
) -> None:
    """Add gusset/doubler reinforcement plates near the boom-to-base junction."""
    doubler_t = 0.010
    doubler_h = section_half_extent * 1.4
    doubler_l = 0.32
    for sy, side in ((+1.0, "left"), (-1.0, "right")):
        base_part.visual(
            Box((doubler_l, doubler_t, doubler_h)),
            origin=Origin(
                xyz=(
                    doubler_l / 2.0 - 0.04,
                    sy * (section_half_extent + doubler_t / 2.0 + 0.014),
                    -section_half_extent * 0.30,
                ),
            ),
            material=material,
            name=f"{side}_root_doubler", material_class_id="metal.paint_coated",
        )


def _build_base_trunnion_yoke(
    base_part,
    *,
    section_half_extent: float,
    material,
    fitting_material,
) -> None:
    """Squat column with a U-shaped yoke at top whose two cheek plates straddle
    the boom rear from left and right (image 1 idiom).  The yoke is closed at
    the very top with a thin cross brace.
    """
    plate_t = 0.024
    plate_size = max(0.32, section_half_extent * 4.6)
    column_h = max(0.18, section_half_extent * 2.2)
    column_w_y = max(0.14, section_half_extent * 3.0)
    column_w_z = max(0.10, section_half_extent * 1.6)
    column_origin_x = -0.05
    # Ground plate.
    base_part.visual(
        Box((plate_size, plate_size, plate_t)),
        origin=Origin(
            xyz=(
                column_origin_x,
                0.0,
                # Embed 3 mm into the column foot so the ground plate stays
                # welded to it (was floating 5 mm below the column).
                -section_half_extent - column_h - plate_t / 2.0 + 0.003,
            ),
        ),
        material=material,
        name="ground_plate", material_class_id="metal.paint_coated",
    )
    # Tapered column body (just a box; visually reads as a stout pillar).
    base_part.visual(
        Box((column_w_z, column_w_y, column_h)),
        origin=Origin(
            xyz=(column_origin_x, 0.0, -section_half_extent - column_h / 2.0),
        ),
        material=material,
        name="column", material_class_id="metal.paint_coated",
    )
    # Two yoke cheek plates that hug the boom sides and extend ABOVE the boom.
    yoke_t = 0.020
    yoke_height = section_half_extent * 2.2 + 0.06
    yoke_length = column_w_z + 0.040
    yoke_z = section_half_extent * 0.05
    for sy, side in ((+1.0, "left"), (-1.0, "right")):
        base_part.visual(
            Box((yoke_length, yoke_t, yoke_height)),
            origin=Origin(
                xyz=(
                    column_origin_x,
                    sy * (section_half_extent + yoke_t / 2.0 + 0.006),
                    yoke_z,
                ),
            ),
            material=material,
            name=f"yoke_{side}_cheek", material_class_id="metal.paint_coated",
        )
    # Cross brace closing the U, seated just below the cheek tops so it embeds
    # into both cheeks (previously it hovered ~1.6 mm above them).
    cheek_top_z = yoke_z + yoke_height / 2.0
    yoke_top_z = cheek_top_z - 0.005
    base_part.visual(
        Box((yoke_length * 0.60, section_half_extent * 2.6, 0.018)),
        origin=Origin(xyz=(column_origin_x, 0.0, yoke_top_z)),
        material=fitting_material,
        name="yoke_top_brace", material_class_id="metal.steel_bare",
    )
    # Axis bulkhead bridging the two yoke cheeks (weld seat for the boom rear).
    _add_base_mount_seat(
        base_part,
        half_y=section_half_extent + 0.022,
        half_z=section_half_extent * 1.20,
        z_center=yoke_z,
        material=fitting_material,
    )


def _build_base_sleeve_socket(
    base_part,
    *,
    section_half_extent: float,
    material,
    fitting_material,
) -> None:
    """Short boxy housing with a U-channel slot the boom passes through
    (image 3 idiom): a base plate, a stout housing behind the boom rear, and
    two side walls extending forward to form a forward-opening U.  The top of
    the housing is closed by a thin cap, leaving a visible internal recess.
    """
    plate_t = 0.024
    plate_size = max(0.32, section_half_extent * 4.4)
    housing_back_d = max(0.10, section_half_extent * 1.8)
    housing_y = max(0.18, section_half_extent * 3.0)
    housing_z = max(0.16, section_half_extent * 2.8)
    side_d = housing_back_d + 0.06
    # Base plate.
    base_part.visual(
        Box((plate_size, plate_size, plate_t)),
        origin=Origin(
            xyz=(
                -housing_back_d / 2.0,
                0.0,
                # Embed 3 mm into the housing so the ground plate stays welded to
                # it (was floating 5 mm below the housing bottom).
                -housing_z / 2.0 - plate_t / 2.0 + 0.003,
            ),
        ),
        material=material,
        name="ground_plate", material_class_id="metal.paint_coated",
    )
    # Back wall behind the boom rear.
    base_part.visual(
        Box((housing_back_d, housing_y, housing_z)),
        origin=Origin(xyz=(-housing_back_d / 2.0, 0.0, 0.0)),
        material=material,
        name="housing_back", material_class_id="metal.paint_coated",
    )
    # Left / right side walls forming a U-shape opening toward +X.
    wall_t = 0.020
    for sy, side in ((+1.0, "left"), (-1.0, "right")):
        base_part.visual(
            Box((side_d, wall_t, housing_z)),
            origin=Origin(
                xyz=(
                    -housing_back_d / 2.0 + 0.030,
                    sy * (housing_y / 2.0 - wall_t / 2.0),
                    0.0,
                ),
            ),
            material=material,
            name=f"housing_side_{side}", material_class_id="metal.paint_coated",
        )
    # Top closure: a cap with a small inset that reads as the "saddle inset".
    cap_z = housing_z / 2.0 + 0.006
    base_part.visual(
        Box((side_d, housing_y, 0.012)),
        origin=Origin(
            xyz=(-housing_back_d / 2.0 + 0.030, 0.0, cap_z),
        ),
        material=material,
        name="housing_top_cap", material_class_id="metal.paint_coated",
    )
    # Small inset stripe on top (a decorative recess hint).
    base_part.visual(
        Box((side_d * 0.55, housing_y * 0.55, 0.006)),
        origin=Origin(
            xyz=(-housing_back_d / 2.0 + 0.030, 0.0, cap_z + 0.008),
        ),
        material=fitting_material,
        name="housing_top_inset", material_class_id="metal.blackened_gunmetal",
    )


BASE_STYLE_BUILDERS = {
    "plate": _build_base_plate,
    "wall_bracket": _build_base_wall_bracket,
    "pedestal": _build_base_pedestal,
    "clamp": _build_base_clamp,
    "saddle_cheek": _build_base_saddle_cheek,
    "trunnion_yoke": _build_base_trunnion_yoke,
    "sleeve_socket": _build_base_sleeve_socket,
}


# ---------------------------------------------------------------------------
# End effector builders.  Each adds geometry to the innermost stage part at
# its FRONT face (x = stage_length).  All are visual-only attachments; the
# FIXED articulation between innermost stage and end_effector is created at
# the build level using a separate part if the end_effector is not 'none'.
# ---------------------------------------------------------------------------


def _build_ee_hook(part, *, half_extent: float, material) -> None:
    part.visual(
        Cylinder(radius=0.012, length=0.10),
        origin=Origin(xyz=(0.05, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=material,
        name="hook_shank", material_class_id="metal.steel_bare",
    )
    part.visual(
        Cylinder(radius=0.012, length=0.08),
        origin=Origin(xyz=(0.10, 0.0, -0.04)),
        material=material,
        name="hook_curve_a", material_class_id="metal.steel_bare",
    )
    part.visual(
        Cylinder(radius=0.012, length=0.06),
        origin=Origin(xyz=(0.07, 0.0, -0.08), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=material,
        name="hook_curve_b", material_class_id="metal.steel_bare",
    )


def _build_ee_light(part, *, half_extent: float, material) -> None:
    part.visual(
        Cylinder(radius=half_extent * 0.6 + 0.04, length=0.05),
        origin=Origin(xyz=(0.04, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=material,
        name="lamp_housing", material_class_id="plastic.opaque_glossy_molded",
    )
    part.visual(
        Cylinder(radius=half_extent * 0.55 + 0.03, length=0.02),
        origin=Origin(xyz=(0.075, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=material,
        name="lamp_lens", material_class_id="tech.emissive_surface",
    )


def _build_ee_camera(part, *, half_extent: float, material) -> None:
    part.visual(
        Box((0.07, 0.10, 0.07)),
        origin=Origin(xyz=(0.045, 0.0, 0.0)),
        material=material,
        name="camera_body", material_class_id="plastic.opaque_glossy_molded",
    )
    part.visual(
        Cylinder(radius=0.022, length=0.03),
        origin=Origin(xyz=(0.085, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=material,
        name="camera_lens", material_class_id="glass.clear_transparent",
    )


def _build_ee_plate(part, *, half_extent: float, material) -> None:
    part.visual(
        Box((0.014, max(0.16, half_extent * 2.8), max(0.16, half_extent * 2.8))),
        origin=Origin(xyz=(0.018, 0.0, 0.0)),
        material=material,
        name="tip_plate", material_class_id="metal.steel_bare",
    )


def _build_ee_clamp(part, *, half_extent: float, material) -> None:
    part.visual(
        Box((0.05, max(0.10, half_extent * 1.6), 0.02)),
        origin=Origin(xyz=(0.04, 0.0, max(0.04, half_extent * 0.7))),
        material=material,
        name="clamp_jaw_upper", material_class_id="metal.steel_bare",
    )
    part.visual(
        Box((0.05, max(0.10, half_extent * 1.6), 0.02)),
        origin=Origin(xyz=(0.04, 0.0, -max(0.04, half_extent * 0.7))),
        material=material,
        name="clamp_jaw_lower", material_class_id="metal.steel_bare",
    )
    part.visual(
        Box((0.02, 0.02, max(0.10, half_extent * 1.6))),
        origin=Origin(xyz=(0.015, 0.0, 0.0)),
        material=material,
        name="clamp_pivot", material_class_id="metal.steel_bare",
    )


def _build_ee_lug(part, *, half_extent: float, material) -> None:
    """Pair of mounting lugs (a small back plate + two short cylinder eyes)."""
    back_plate_t = 0.012
    eye_radius = max(0.018, half_extent * 0.45)
    eye_length = 0.030
    eye_offset_y = max(0.030, half_extent * 1.1)
    back_plate_h = max(0.12, half_extent * 2.3)
    # Back plate must reach out to the eyes (they sit at ±eye_offset_y) so the
    # supporting tabs actually land on it instead of overhanging into space.
    back_plate_w = max(0.10, (eye_offset_y + 0.012) * 2.0)
    part.visual(
        Box((back_plate_t, back_plate_w, back_plate_h)),
        origin=Origin(xyz=(back_plate_t / 2.0, 0.0, 0.0)),
        material=material,
        name="lug_back_plate", material_class_id="metal.steel_bare",
    )
    # Two parallel lug eyes projecting forward along +X.
    for sy, side in ((+1.0, "left"), (-1.0, "right")):
        # Cylindrical eye (axis along Y, parallel to the boom side).
        part.visual(
            Cylinder(radius=eye_radius, length=eye_length),
            origin=Origin(
                xyz=(back_plate_t + 0.020, sy * eye_offset_y, 0.0),
                rpy=(math.pi / 2.0, 0.0, 0.0),
            ),
            material=material,
            name=f"lug_eye_{side}", material_class_id="metal.steel_bare",
        )
        # Tab bridging the eye back into the back plate (starts inside the plate
        # at x~0.004 and runs forward under the eye) so nothing floats free.
        tab_x0 = 0.004
        tab_x1 = back_plate_t + 0.020 + 0.020
        part.visual(
            Box((tab_x1 - tab_x0, 0.010, eye_radius * 1.6)),
            origin=Origin(xyz=((tab_x0 + tab_x1) / 2.0, sy * eye_offset_y, 0.0)),
            material=material,
            name=f"lug_tab_{side}", material_class_id="metal.steel_bare",
        )


END_EFFECTOR_BUILDERS = {
    "hook": _build_ee_hook,
    "light": _build_ee_light,
    "camera": _build_ee_camera,
    "plate": _build_ee_plate,
    "clamp": _build_ee_clamp,
    "lug": _build_ee_lug,
}


def _add_wear_pad_shoes(
    stage_part,
    *,
    cross_section: TubeCrossSection,
    section: tuple[float, ...],
    length: float,
    pad_material,
    stage_index: int,
) -> None:
    """Slide pads on a rectangular stage's bottom that ride against the parent
    interior.  Only emit for rectangular cross-section (dataset idiom is
    overwhelmingly rectangular).
    """
    if cross_section != "rectangular":
        return
    if length <= 0.16:
        return
    y, z = section
    pad_y_extent = max(0.020, y * 0.16)
    pad_x_extent = max(0.06, min(0.18, length * 0.13))
    pad_thickness = 0.012
    # Place near rear and front of the stage at left/right of bottom.
    pad_y_offset = y * 0.30
    # Embed the pad 3 mm into the bottom plate so it stays welded to the stage
    # (a slide shoe bolted through the tube wall), not floating just below it.
    pad_z = -z / 2.0 - pad_thickness / 2.0 + 0.003
    for x_frac, where in ((0.18, "rear"), (0.78, "front")):
        x_center = length * x_frac
        for sy, side in ((+1.0, "left"), (-1.0, "right")):
            stage_part.visual(
                Box((pad_x_extent, pad_y_extent, pad_thickness)),
                origin=Origin(xyz=(x_center, sy * pad_y_offset, pad_z)),
                material=pad_material,
                name=f"stage_{stage_index}_pad_{where}_{side}", material_class_id="plastic.opaque_generic",
            )


def _add_front_wear_cap(
    parent_part,
    *,
    cross_section: TubeCrossSection,
    parent_section: tuple[float, ...],
    parent_length: float,
    material,
    name: str,
) -> None:
    """Two narrow strips wrapping the parent's front opening top edges.

    Mirrors the dataset's ``front_wear_cap_left/right`` idiom: a small flange
    at the front of each top strip.  For round/hex sections we approximate
    with a thin ring just outside the parent's front face.
    """
    cap_axial = 0.045
    if cross_section == "rectangular":
        y, z = parent_section
        wall = _wall_thickness(min(y, z))
        roof_strip_w = max(0.020, y * 0.20)
        z_top = z / 2.0 - wall + 0.010
        for sy, side in ((+1.0, "left"), (-1.0, "right")):
            parent_part.visual(
                Box((cap_axial, roof_strip_w, 0.010)),
                origin=Origin(
                    xyz=(
                        parent_length - cap_axial / 2.0,
                        sy * (y / 2.0 - roof_strip_w / 2.0),
                        z_top,
                    ),
                ),
                material=material,
                name=f"{name}_{side}", material_class_id="plastic.opaque_generic",
            )
    else:
        # round / hex: thin external ring at the parent's front.
        if cross_section == "round":
            radius = parent_section[0]
        else:
            apothem = parent_section[0]
            radius = apothem / math.cos(math.pi / 6.0)
        parent_part.visual(
            Cylinder(radius=radius + 0.010, length=0.010),
            origin=Origin(
                xyz=(parent_length - 0.005, 0.0, 0.0),
                rpy=(0.0, math.pi / 2.0, 0.0),
            ),
            material=material,
            name=f"{name}_ring", material_class_id="plastic.opaque_generic",
        )


# ---------------------------------------------------------------------------
# Decoration (parent.visual on the parent stage, no separate part).
# ---------------------------------------------------------------------------


def _add_locking_collar(
    parent_part,
    *,
    cross_section: TubeCrossSection,
    parent_section: tuple[float, ...],
    child_section: tuple[float, ...],
    x_position: float,
    material,
    name: str,
) -> None:
    """A small collar visual at the joint plane between two stages.  Attached
    as a parent.visual on the parent stage (no part, no joint).
    """
    half_p_y, half_p_z = _section_bbox_yz(cross_section, parent_section)
    half_c_y, half_c_z = _section_bbox_yz(cross_section, child_section)
    collar_t = 0.012
    if cross_section == "rectangular":
        # ring formed by 4 thin walls around the child section, at x_position
        gap = 0.004
        # Top/bottom strips:
        parent_part.visual(
            Box((collar_t, half_p_y * 2.0, gap + 0.006)),
            origin=Origin(xyz=(x_position, 0.0, half_c_z + gap / 2.0 + 0.003)),
            material=material,
            name=f"{name}_top", material_class_id="metal.blackened_gunmetal",
        )
        parent_part.visual(
            Box((collar_t, half_p_y * 2.0, gap + 0.006)),
            origin=Origin(xyz=(x_position, 0.0, -half_c_z - gap / 2.0 - 0.003)),
            material=material,
            name=f"{name}_bottom", material_class_id="metal.blackened_gunmetal",
        )
        parent_part.visual(
            Box((collar_t, gap + 0.006, half_p_z * 2.0)),
            origin=Origin(xyz=(x_position, half_c_y + gap / 2.0 + 0.003, 0.0)),
            material=material,
            name=f"{name}_right", material_class_id="metal.blackened_gunmetal",
        )
        parent_part.visual(
            Box((collar_t, gap + 0.006, half_p_z * 2.0)),
            origin=Origin(xyz=(x_position, -half_c_y - gap / 2.0 - 0.003, 0.0)),
            material=material,
            name=f"{name}_left", material_class_id="metal.blackened_gunmetal",
        )
    elif cross_section == "round":
        parent_part.visual(
            Cylinder(radius=half_p_y + 0.006, length=collar_t),
            origin=Origin(xyz=(x_position, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=material,
            name=name, material_class_id="metal.blackened_gunmetal",
        )
    else:  # hex
        # Approximate as a slightly larger Cylinder collar.
        parent_part.visual(
            Cylinder(radius=half_p_y + 0.006, length=collar_t),
            origin=Origin(xyz=(x_position, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=material,
            name=name, material_class_id="metal.blackened_gunmetal",
        )


def _add_decoration(
    stage_part,
    *,
    cross_section: TubeCrossSection,
    section: tuple[float, ...],
    length: float,
    stage_index: int,
    decoration: Decoration,
    material,
) -> None:
    if decoration == "none":
        return
    half_y, half_z = _section_bbox_yz(cross_section, section)
    if decoration == "warning_stripe":
        # 3 thin stripes equally spaced along the stage.
        for k in range(3):
            x = length * (0.20 + 0.30 * k)
            # Straddle the tube surface (centre on the outer face) so the stripe
            # is embedded into the wall, not floating a hair above it.
            stage_part.visual(
                Box((0.04, half_y * 2.05, 0.008)),
                origin=Origin(xyz=(x, 0.0, half_z)),
                material=material,
                name=f"warning_stripe_{stage_index}_{k}_top", material_class_id="metal.paint_coated",
            )
            stage_part.visual(
                Box((0.04, half_y * 2.05, 0.008)),
                origin=Origin(xyz=(x, 0.0, -half_z)),
                material=material,
                name=f"warning_stripe_{stage_index}_{k}_bottom", material_class_id="metal.paint_coated",
            )
    elif decoration == "bolts":
        # bolt rivets along the top edge at 5 stations.  Centre each rivet ON the
        # tube's outer surface so it is embedded into the wall (round/hex vertices
        # sit at half_z) rather than floating a hair above it.
        for k in range(5):
            x = length * (0.10 + 0.18 * k)
            stage_part.visual(
                Cylinder(radius=0.006, length=0.016),
                origin=Origin(xyz=(x, 0.0, half_z)),
                material=material,
                name=f"bolt_{stage_index}_{k}", material_class_id="metal.steel_bare",
            )
    else:  # fake_cylinder - a hydraulic ram running parallel to the stage
        ram_r = max(0.014, min(half_y, half_z) * 0.20)
        # Seat the ram so its underside bites 3 mm into the tube wall (it rests
        # on the boom side instead of floating a couple cm above it).
        stage_part.visual(
            Cylinder(radius=ram_r, length=length * 0.55),
            origin=Origin(
                xyz=(length * 0.45, 0.0, half_z + ram_r - 0.003),
                rpy=(0.0, math.pi / 2.0, 0.0),
            ),
            material=material,
            name=f"fake_hydraulic_cylinder_{stage_index}", material_class_id="metal.chrome_polished",
        )


# ---------------------------------------------------------------------------
# Build helpers
# ---------------------------------------------------------------------------


def _stage_name(i: int, stage_count: int) -> str:
    if i == 0:
        return "outer_stage"
    if i == stage_count - 1:
        return "inner_stage"
    return f"middle_stage_{i}"


def _joint_name(parent_i: int, child_i: int, stage_count: int) -> str:
    parent = _stage_name(parent_i, stage_count)
    child = _stage_name(child_i, stage_count)
    return f"{parent}_to_{child}"


def build_telescoping_boom(
    config: TelescopingBoomConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    config = config or TelescopingBoomConfig()
    resolved = resolve_config(config)
    if assets is None:
        assets = AssetContext(Path(tempfile.mkdtemp(prefix="articraft-telescoping-boom-assets-")))
    model = ArticulatedObject(name=resolved.name, assets=assets)

    palette = MATERIAL_PALETTES[resolved.material_style]
    stage_palette: tuple[tuple[float, float, float, float], ...] = palette["stages"]  # type: ignore[assignment]
    fitting_rgba: tuple[float, float, float, float] = palette["fitting"]  # type: ignore[assignment]
    accent_rgba: tuple[float, float, float, float] = palette["accent"]  # type: ignore[assignment]
    # One material per stage (cycle the palette if stage_count exceeds it).
    stage_materials = []
    for i in range(resolved.stage_count):
        rgba = stage_palette[i % len(stage_palette)]
        stage_materials.append(
            model.material(f"boom_stage_{i}_{resolved.material_style}", rgba=rgba)
        )
    fitting_mat = model.material(f"boom_fitting_{resolved.material_style}", rgba=fitting_rgba)
    pad_mat = model.material(f"boom_wear_pad_{resolved.material_style}", rgba=accent_rgba)
    decor_mat = model.material(
        f"boom_decor_{resolved.material_style}", rgba=(0.96, 0.82, 0.10, 1.0)
    )

    # ----- base_bracket -----
    base_part = model.part("base_bracket")
    outer_half_y, outer_half_z = _section_bbox_yz(
        resolved.tube_cross_section, resolved.outer_section
    )
    base_half_extent = max(outer_half_y, outer_half_z)
    BASE_STYLE_BUILDERS[resolved.base_style](
        base_part,
        section_half_extent=base_half_extent,
        material=fitting_mat,
        fitting_material=stage_materials[0],
    )
    if resolved.base_with_doublers:
        _add_base_doublers(
            base_part,
            section_half_extent=base_half_extent,
            material=stage_materials[0],
        )

    # ----- stages -----
    stage_parts = []
    for i in range(resolved.stage_count):
        part = model.part(_stage_name(i, resolved.stage_count))
        stage_parts.append(part)
        sec = resolved.stage_sections[i]
        length = resolved.stage_lengths[i]
        material = stage_materials[i]
        CROSS_SECTION_BUILDERS[resolved.tube_cross_section](
            part,
            section=sec,
            length=length,
            material=material,
            prefix=_stage_name(i, resolved.stage_count),
        )
        # Rear cap: always on outer; optionally on every stage when
        # ``per_stage_caps`` is set (uses the HOME offset to keep caps from
        # clipping with each other at q=0).
        if i == 0 or resolved.per_stage_caps:
            _add_rear_cap(
                part,
                cross_section=resolved.tube_cross_section,
                section=sec,
                material=fitting_mat,
                name=f"{_stage_name(i, resolved.stage_count)}_rear_cap",
            )
        # Rear slide bushing on every inner stage: reaches out to the parent
        # bore so the nested stages stay in physical contact (a single grounded
        # body) even at the retracted rest pose, where the parent front collar
        # has not yet engaged the child.
        if i >= 1:
            _add_rear_guide_bushing(
                part,
                cross_section=resolved.tube_cross_section,
                parent_section=resolved.stage_sections[i - 1],
                material=fitting_mat,
                name=f"{_stage_name(i, resolved.stage_count)}_rear_bushing",
            )
        # Wear-pad shoes on inner stages (i >= 1) — only emit for rectangular
        # cross-section to mirror the dataset idiom.
        if i >= 1 and resolved.add_wear_pads:
            _add_wear_pad_shoes(
                part,
                cross_section=resolved.tube_cross_section,
                section=sec,
                length=length,
                pad_material=pad_mat,
                stage_index=i,
            )
        # Add decoration (visual-only on this stage).
        _add_decoration(
            part,
            cross_section=resolved.tube_cross_section,
            section=sec,
            length=length,
            stage_index=i,
            decoration=resolved.decoration,
            material=decor_mat,
        )
        # Locking collar at the FRONT face of THIS stage (i.e. at the joint
        # plane between this stage and the next).  Visual-only; lives on the
        # parent (this) stage.  Skip on the innermost stage.
        if i < resolved.stage_count - 1:
            child_sec = resolved.stage_sections[i + 1]
            _add_locking_collar(
                part,
                cross_section=resolved.tube_cross_section,
                parent_section=sec,
                child_section=child_sec,
                x_position=length - 0.020,
                material=fitting_mat,
                name=f"locking_collar_{i}",
            )
            if resolved.per_stage_caps:
                _add_front_wear_cap(
                    part,
                    cross_section=resolved.tube_cross_section,
                    parent_section=sec,
                    parent_length=length,
                    material=fitting_mat,
                    name=f"front_wear_cap_{i}",
                )

    # ----- articulations -----
    # FIXED articulation: base_bracket -> outer_stage.  The orientation rpy is
    # applied here so the whole boom rotates as a unit.
    model.articulation(
        "base_bracket_to_outer_stage",
        ArticulationType.FIXED,
        parent=base_part,
        child=stage_parts[0],
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=ORIENTATION_RPY[resolved.boom_orientation]),
    )

    # PRISMATIC articulations between consecutive stages, all axis=(1,0,0)
    # along the boom's local X axis -> collinear in world frame after the
    # FIXED rpy is applied at the base.
    for i in range(resolved.stage_count - 1):
        parent = stage_parts[i]
        child = stage_parts[i + 1]
        # HOME offset (X): the joint origin sits ``home_x`` into the parent
        # along +X.  At q=0 the child rear is therefore at x=home_x in the
        # parent frame, mirroring the dataset's 73% convention of a tucked
        # rest pose.  Travel is reduced by the HOME offset so the retained
        # overlap at q=upper is still exactly ``overlap_ratio * inner_length``.
        parent_length = resolved.stage_lengths[i]
        inner_length = resolved.stage_lengths[i + 1]
        home_x = resolved.home_offsets[i] * parent_length
        upper = parent_length - home_x - resolved.overlap_ratio * inner_length
        # Numeric guard: leave a small minimum travel even in degenerate cases.
        upper = max(0.05, upper)
        model.articulation(
            _joint_name(i, i + 1, resolved.stage_count),
            ArticulationType.PRISMATIC,
            parent=parent,
            child=child,
            origin=Origin(xyz=(home_x, 0.0, 0.0)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(
                effort=1200.0 - 200.0 * i,
                velocity=0.5,
                lower=0.0,
                upper=upper,
            ),
        )

    # ----- end effector -----
    if resolved.end_effector != "none":
        ee = model.part("end_effector")
        innermost_section = resolved.stage_sections[-1]
        innermost_half_y, innermost_half_z = _section_bbox_yz(
            resolved.tube_cross_section, innermost_section
        )
        innermost_half_extent = max(innermost_half_y, innermost_half_z)
        END_EFFECTOR_BUILDERS[resolved.end_effector](
            ee,
            half_extent=innermost_half_extent,
            material=fitting_mat,
        )
        # FIXED articulation at the FRONT face of the innermost stage.
        innermost_length = resolved.stage_lengths[-1]
        # Close the innermost tube's open front with a mounting flange so the
        # end-effector welds to real material at the tip (the hollow rim alone
        # leaves the weld origin an inner-radius away from any wall).
        _add_front_cap(
            stage_parts[-1],
            cross_section=resolved.tube_cross_section,
            section=innermost_section,
            length=innermost_length,
            material=fitting_mat,
            name="inner_stage_front_cap",
        )
        model.articulation(
            "inner_stage_to_end_effector",
            ArticulationType.FIXED,
            parent=stage_parts[-1],
            child=ee,
            origin=Origin(xyz=(innermost_length, 0.0, 0.0)),
        )

    return model


# ---------------------------------------------------------------------------
# Validator
# ---------------------------------------------------------------------------


def run_telescoping_boom_tests(
    object_model: ArticulatedObject, config: TelescopingBoomConfig
) -> TestReport:
    resolved = resolve_config(config)
    ctx = TestContext(object_model)

    base_part = object_model.get_part("base_bracket")
    stage_parts = [
        object_model.get_part(_stage_name(i, resolved.stage_count))
        for i in range(resolved.stage_count)
    ]

    # Allow the proxy-overlap pattern between nested stages. All stages are
    # coaxial and slide through one another (and through each other's locking
    # collars) as the boom extends/retracts, so every stage pair may overlap,
    # not just adjacent ones.
    for i in range(resolved.stage_count):
        for j in range(i + 1, resolved.stage_count):
            ctx.allow_overlap(
                stage_parts[i],
                stage_parts[j],
                reason=(
                    "Coaxial telescoping stages are intentionally represented as "
                    "sliding through one another (parent stage proxy)."
                ),
            )
    # Allow base bracket overlap with the stages: it captures the boom rear, and
    # at the retracted pose the inner stages nest back into that same capture
    # zone (socket housing / cheeks), just as the outer stage sits in it.
    for stage in stage_parts:
        ctx.allow_overlap(
            base_part,
            stage,
            reason="Base bracket captures the boom rear; inner stages nest into that capture zone.",
        )
    # The end-effector rides the innermost stage tip, so it slides coaxially with
    # the boom and may nest inside any parent stage proxy across the travel range.
    if resolved.end_effector != "none":
        ee_part = object_model.get_part("end_effector")
        for stage in stage_parts:
            ctx.allow_overlap(
                ee_part,
                stage,
                reason=(
                    "End-effector rides the innermost stage tip and nests inside the "
                    "parent stage proxies across the boom travel range."
                ),
            )

    # 1. Joint count = stage_count - 1 (prismatic)
    prismatic_joints = [
        j for j in object_model.articulations if j.articulation_type == ArticulationType.PRISMATIC
    ]
    ctx.check(
        "prismatic_joint_count_equals_stage_count_minus_one",
        len(prismatic_joints) == resolved.stage_count - 1,
        details=(f"prismatic_joints={len(prismatic_joints)}, expected={resolved.stage_count - 1}"),
    )

    # 2. Joint type: all stage joints are prismatic, base->outer is FIXED,
    #    inner->end_effector is FIXED (if present).
    expected_prismatic_names = {
        _joint_name(i, i + 1, resolved.stage_count) for i in range(resolved.stage_count - 1)
    }
    for jname in expected_prismatic_names:
        joint = object_model.get_articulation(jname)
        ctx.check(
            f"{jname}_is_prismatic",
            joint.articulation_type == ArticulationType.PRISMATIC,
            details=f"got {joint.articulation_type}",
        )

    # 3. Axis collinearity: every prismatic joint has axis (1, 0, 0) and rpy=0
    #    in the parent frame, so when projected to world they are collinear.
    for joint in prismatic_joints:
        ax = tuple(joint.axis)
        ctx.check(
            f"{joint.name}_axis_along_local_x",
            (abs(ax[0] - 1.0) < 1e-6 and abs(ax[1]) < 1e-6 and abs(ax[2]) < 1e-6),
            details=f"axis={ax}",
        )
        # Joint origin YZ offsets must be zero so the joint axis line is the
        # parent's x axis itself.  Together with axis=(1,0,0) this means the
        # boom axes are collinear in world frame.  X offsets are allowed
        # (HOME offset == fraction of parent length tucked at q=0).
        oyz = (joint.origin.xyz[1], joint.origin.xyz[2])
        ctx.check(
            f"{joint.name}_origin_on_parent_x_axis",
            abs(oyz[0]) < 1e-6 and abs(oyz[1]) < 1e-6,
            details=f"origin.xyz={joint.origin.xyz}",
        )
        # rpy must be zero -> child frame rotation matches parent frame.
        rpy = tuple(joint.origin.rpy)
        ctx.check(
            f"{joint.name}_origin_rpy_zero",
            all(abs(v) < 1e-6 for v in rpy),
            details=f"rpy={rpy}",
        )

    # Collinearity in the BOOM frame is already enforced by the per-joint
    # ``origin_on_parent_x_axis`` check (origin.xyz[1]==xyz[2]==0).  We do not
    # measure world-frame yz distance between consecutive stage origins
    # because the HOME offset along the boom axis legitimately translates the
    # child stage in world yz when ``boom_orientation`` is angled or vertical.

    # 4. Nesting: inner stage section is strictly smaller than outer (yz
    #    AABB).  Use part_world_aabb at rest.
    for i in range(resolved.stage_count - 1):
        outer_aabb = ctx.part_world_aabb(stage_parts[i])
        inner_aabb = ctx.part_world_aabb(stage_parts[i + 1])
        if outer_aabb is None or inner_aabb is None:
            ctx.fail(
                f"stage_{i}_aabb_available",
                "could not measure stage AABB for nesting check",
            )
            continue
        # Determine in-world the two non-X axes.  In any orientation, the
        # boom's local YZ map to two world axes that exclude the boom-axis.
        # We compare the *short* axes of the stage AABB.  Equivalently,
        # measure the two smallest extents of each AABB.
        outer_extents = sorted(outer_aabb[1][k] - outer_aabb[0][k] for k in range(3))
        inner_extents = sorted(inner_aabb[1][k] - inner_aabb[0][k] for k in range(3))
        # Two smallest extents of inner must be < two smallest of outer.
        ctx.check(
            f"stage_{i + 1}_section_smaller_than_stage_{i}",
            inner_extents[0] < outer_extents[0] - 1e-4
            and inner_extents[1] < outer_extents[1] - 1e-4,
            details=f"outer={outer_extents}, inner={inner_extents}",
        )

    # 5. Travel limit honours overlap_ratio.  Accounting for the HOME offset
    #    on the joint origin, at q=upper the child rear sits at
    #    home_x + upper in the parent frame and must keep exactly
    #    ``overlap_ratio * inner_length`` of itself inside the parent.  So
    #    expected upper = parent_length - home_x - overlap_ratio * inner_length.
    for i in range(resolved.stage_count - 1):
        joint = object_model.get_articulation(_joint_name(i, i + 1, resolved.stage_count))
        upper = joint.motion_limits.upper if joint.motion_limits else 0.0
        parent_length = resolved.stage_lengths[i]
        inner_length = resolved.stage_lengths[i + 1]
        home_x = float(joint.origin.xyz[0])
        expected_upper = max(0.05, parent_length - home_x - resolved.overlap_ratio * inner_length)
        ctx.check(
            f"{joint.name}_travel_honours_overlap_ratio",
            abs(upper - expected_upper) < max(0.05, expected_upper * 0.10),
            details=(
                f"upper={upper:.4f}, expected~{expected_upper:.4f} "
                f"(parent_length={parent_length:.3f}, inner_length={inner_length:.3f}, "
                f"home_x={home_x:.3f}, overlap_ratio={resolved.overlap_ratio})"
            ),
        )
        # The child rear at q=upper must stay strictly inside parent's body.
        ctx.check(
            f"{joint.name}_upper_keeps_inner_inside_parent",
            home_x + upper < parent_length - 1e-6,
            details=(
                f"home_x+upper={home_x + upper:.4f} must be < "
                f"parent_length={parent_length:.4f} so inner rear stays inside parent."
            ),
        )

    # 6. Endpoint: end_effector is attached at the front of the innermost
    #    stage via FIXED articulation.
    if resolved.end_effector != "none":
        ee_joint = object_model.get_articulation("inner_stage_to_end_effector")
        ctx.check(
            "end_effector_is_fixed",
            ee_joint.articulation_type == ArticulationType.FIXED,
            details=f"got {ee_joint.articulation_type}",
        )
        ctx.check(
            "end_effector_parent_is_innermost_stage",
            ee_joint.parent == stage_parts[-1].name,
            details=f"parent={ee_joint.parent}",
        )
        innermost_length = resolved.stage_lengths[-1]
        ctx.check(
            "end_effector_at_innermost_front",
            abs(ee_joint.origin.xyz[0] - innermost_length) < 1e-4
            and abs(ee_joint.origin.xyz[1]) < 1e-4
            and abs(ee_joint.origin.xyz[2]) < 1e-4,
            details=f"origin.xyz={ee_joint.origin.xyz}, expected x={innermost_length}",
        )

    # 7. No floating: base, all stages, and end_effector (if any) connected.
    expected_part_names = {"base_bracket"} | {
        _stage_name(i, resolved.stage_count) for i in range(resolved.stage_count)
    }
    if resolved.end_effector != "none":
        expected_part_names.add("end_effector")
    actual_parts = {p.name for p in object_model.parts}
    ctx.check(
        "all_expected_parts_present",
        expected_part_names.issubset(actual_parts),
        details=(
            f"missing={expected_part_names - actual_parts}, extra={actual_parts - expected_part_names}"
        ),
    )

    # Identity: outer stage must carry its hollow tube geometry (plates, webs,
    # or polygon face plates).  After the hollow-tube refactor, we no longer
    # emit a single ``_tube`` visual; instead each stage is built from multiple
    # plate / face visuals.
    outer_visual_names = {v.name for v in stage_parts[0].visuals if v.name is not None}
    if resolved.tube_cross_section == "rectangular":
        ctx.check(
            "outer_stage_has_hollow_rect_walls",
            any(name.endswith("_top_plate") for name in outer_visual_names)
            and any(name.endswith("_bottom_plate") for name in outer_visual_names),
            details=f"visuals={sorted(outer_visual_names)}",
        )
    elif resolved.tube_cross_section == "round":
        ctx.check(
            "outer_stage_has_round_faces",
            sum(1 for name in outer_visual_names if "_round_face_" in name) >= 8,
            details=f"visuals={sorted(outer_visual_names)}",
        )
    else:
        ctx.check(
            "outer_stage_has_hex_faces",
            sum(1 for name in outer_visual_names if "_hex_face_" in name) >= 6,
            details=f"visuals={sorted(outer_visual_names)}",
        )

    # base part naming: must include 'base', 'support', or 'bracket'.
    base_name = base_part.name
    ctx.check(
        "base_part_name_recognisable",
        any(token in base_name for token in ("base", "support", "bracket")),
        details=f"base_name={base_name}",
    )

    # 8. Decisive pose check: at full extension of the *first* stage joint,
    #    verify the child stage origin moves forward in its parent's local x.
    if resolved.stage_count >= 2:
        first_joint = object_model.get_articulation(_joint_name(0, 1, resolved.stage_count))
        upper = first_joint.motion_limits.upper if first_joint.motion_limits else 0.0
        rest_pos = ctx.part_world_position(stage_parts[1])
        with ctx.pose({first_joint: upper}):
            ext_pos = ctx.part_world_position(stage_parts[1])
        if rest_pos is not None and ext_pos is not None and upper > 0.0:
            moved = math.sqrt(sum((ext_pos[k] - rest_pos[k]) ** 2 for k in range(3)))
            ctx.check(
                f"{first_joint.name}_actually_translates",
                moved > min(0.04, upper * 0.5),
                details=f"rest={rest_pos}, ext={ext_pos}, moved={moved:.3f}",
            )

    return ctx.report()


# ---------------------------------------------------------------------------
# Seeded entry point + override helper (mirrors ferris_wheel API).
# ---------------------------------------------------------------------------


def build_seeded_telescoping_boom(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_telescoping_boom(config_from_seed(seed), assets=assets)


def with_overrides(config: TelescopingBoomConfig, **kwargs: object) -> TelescopingBoomConfig:
    return replace(config, **kwargs)
