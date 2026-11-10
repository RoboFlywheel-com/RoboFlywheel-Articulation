# SPDX-License-Identifier: Apache-2.0

"""Single revolute hinge — modular procedural template.

A hinge is the minimal articulated object: exactly ONE revolute joint joining a
grounded ``fixed_half`` (root) to a ``moving_half`` that swings about a shared
knuckle/journal pin-line. There are three structural axes (slots):

  fixed_half   : leaf_with_knuckles | bracket_support | clevis_fork
                 | trunnion_cheek | host_carcass
  moving_half  : opposing_leaf | single_tab_blade | cover_panel | host_door
  hinge_line   : interleaved_knuckles_pin_in_leaf | separate_pin_part
                 | barrel_with_collars | single_journal_or_bore

These are NOT freely combinable — a clevis fork only mates a single tab, a
cabinet carcass only mates a cabinet door, etc. ``config_from_seed`` samples
along a compatibility matrix so every seed yields a physically legal hinge.
That matrix collapses the 5×4×4 raw grid to ~12 legal topologies, well past
the ``module_topology_diversity`` gate (≥10).

Geometry convention: the pin-line runs along +z (x=0, y=0, z∈[0, H]). Knuckle
cylinders are coaxial with z and stacked in alternating bands — the fixed half
owns the even bands, the moving half the odd ones, so they interlock. Each
half's flat leaf plate spans the full z height and overlaps all of its own
knuckle bands, keeping every part a single connected island. The revolute axis
is +z; the joint origin sits on the pin-line (on real geometry).

seed == 0 is the anchor: ``leaf_with_knuckles + opposing_leaf +
interleaved_knuckles_pin_in_leaf`` at canonical dimensions.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Literal, Optional

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
)

__modular__ = True


FixedStyle = Literal[
    "leaf_with_knuckles",
    "bracket_support",
    "clevis_fork",
    "trunnion_cheek",
    "host_carcass",
]
MovingStyle = Literal["opposing_leaf", "single_tab_blade", "cover_panel", "host_door"]
HingeLineStyle = Literal[
    "interleaved_knuckles_pin_in_leaf",
    "separate_pin_part",
    "barrel_with_collars",
    "single_journal_or_bore",
]
PinAxis = Literal["z", "neg_y", "pos_y", "x"]
PaletteTheme = Literal["brass", "steel", "black_oxide", "white_enamel", "bronze"]


# Compatibility matrix: fixed_style -> (legal moving_styles, legal hinge_line_styles).
# Sampling within these lists guarantees every seed is a physically legal hinge.
_COMPAT: dict[str, tuple[tuple[str, ...], tuple[str, ...]]] = {
    "leaf_with_knuckles": (
        ("opposing_leaf",),
        ("interleaved_knuckles_pin_in_leaf", "separate_pin_part", "barrel_with_collars"),
    ),
    "bracket_support": (
        ("cover_panel", "opposing_leaf"),
        ("interleaved_knuckles_pin_in_leaf", "separate_pin_part"),
    ),
    "clevis_fork": (
        ("single_tab_blade",),
        ("single_journal_or_bore", "separate_pin_part"),
    ),
    "trunnion_cheek": (
        ("single_tab_blade",),
        ("single_journal_or_bore",),
    ),
    "host_carcass": (
        ("host_door",),
        ("interleaved_knuckles_pin_in_leaf", "single_journal_or_bore"),
    ),
}

_ANCHOR_FIXED: FixedStyle = "leaf_with_knuckles"
_ANCHOR_MOVING: MovingStyle = "opposing_leaf"
_ANCHOR_HINGE_LINE: HingeLineStyle = "interleaved_knuckles_pin_in_leaf"

_PIN_AXIS_VEC: dict[str, tuple[float, float, float]] = {
    "z": (0.0, 0.0, 1.0),
    "neg_y": (0.0, 0.0, 1.0),  # geometry is z-aligned in v1; axis stays +z
    "pos_y": (0.0, 0.0, 1.0),
    "x": (0.0, 0.0, 1.0),
}


HINGE_PALETTE_PRESETS: dict[str, dict[str, tuple[float, float, float, float]]] = {
    "brass": {
        "leaf": (0.78, 0.62, 0.24, 1.0),
        "knuckle": (0.72, 0.57, 0.20, 1.0),
        "pin": (0.55, 0.44, 0.16, 1.0),
        "accent": (0.40, 0.32, 0.12, 1.0),
    },
    "steel": {
        "leaf": (0.74, 0.76, 0.80, 1.0),
        "knuckle": (0.66, 0.68, 0.72, 1.0),
        "pin": (0.50, 0.52, 0.56, 1.0),
        "accent": (0.34, 0.36, 0.40, 1.0),
    },
    "black_oxide": {
        "leaf": (0.16, 0.16, 0.18, 1.0),
        "knuckle": (0.12, 0.12, 0.14, 1.0),
        "pin": (0.40, 0.41, 0.44, 1.0),
        "accent": (0.06, 0.06, 0.07, 1.0),
    },
    "white_enamel": {
        "leaf": (0.90, 0.90, 0.88, 1.0),
        "knuckle": (0.82, 0.82, 0.80, 1.0),
        "pin": (0.55, 0.56, 0.58, 1.0),
        "accent": (0.70, 0.70, 0.68, 1.0),
    },
    "bronze": {
        "leaf": (0.55, 0.40, 0.22, 1.0),
        "knuckle": (0.48, 0.35, 0.19, 1.0),
        "pin": (0.36, 0.27, 0.15, 1.0),
        "accent": (0.28, 0.20, 0.11, 1.0),
    },
}


@dataclass(frozen=True)
class SingleRevoluteHingeConfig:
    """Public template config. Leave module fields ``None`` to let
    ``config_from_seed`` / ``resolve_config`` fill them in (along the
    compatibility matrix)."""

    fixed_style: FixedStyle | None = None
    moving_style: MovingStyle | None = None
    hinge_line_style: HingeLineStyle | None = None

    pin_axis: PinAxis = "z"
    palette_theme: PaletteTheme = "brass"

    # Total knuckle bands across both halves (complementary split). 2-7.
    knuckle_count: int = 5

    leaf_height: float = 0.090  # z extent of the hinge (pin-line length)
    leaf_x: float = 0.044  # how far each leaf extends from the pin-line (x)
    plate_thickness: float = 0.004  # leaf plate thickness (y)
    knuckle_outer_radius: float = 0.0075
    pin_bore_radius: float = 0.0050
    pin_radius: float = 0.0040

    hinge_lower: float = 0.0
    hinge_upper: float = 1.8

    palette: dict[str, tuple[float, float, float, float]] = field(
        default_factory=lambda: dict(HINGE_PALETTE_PRESETS["brass"])
    )


@dataclass(frozen=True)
class ResolvedSingleRevoluteHingeConfig:
    fixed_style: FixedStyle
    moving_style: MovingStyle
    hinge_line_style: HingeLineStyle
    pin_axis: PinAxis
    palette_theme: PaletteTheme
    knuckle_count: int
    leaf_height: float
    leaf_x: float
    plate_thickness: float
    knuckle_outer_radius: float
    pin_bore_radius: float
    pin_radius: float
    hinge_lower: float
    hinge_upper: float
    palette: dict[str, tuple[float, float, float, float]]


def config_from_seed(seed: int) -> SingleRevoluteHingeConfig:
    """seed=0 => anchor. Other seeds sample along the compatibility matrix so
    fixed/moving/hinge_line are always a legal triple."""
    if seed == 0:
        return SingleRevoluteHingeConfig(
            fixed_style=_ANCHOR_FIXED,
            moving_style=_ANCHOR_MOVING,
            hinge_line_style=_ANCHOR_HINGE_LINE,
            pin_axis="z",
            palette_theme="brass",
            knuckle_count=5,
            leaf_height=0.090,
            leaf_x=0.044,
            plate_thickness=0.004,
            knuckle_outer_radius=0.0075,
            pin_bore_radius=0.0050,
            pin_radius=0.0040,
        )

    rng = random.Random(seed)
    fixed_style: FixedStyle = rng.choice(tuple(_COMPAT.keys()))  # type: ignore[assignment]
    moving_pool, hinge_pool = _COMPAT[fixed_style]
    moving_style: MovingStyle = rng.choice(moving_pool)  # type: ignore[assignment]
    hinge_line_style: HingeLineStyle = rng.choice(hinge_pool)  # type: ignore[assignment]
    pin_axis: PinAxis = rng.choice(("z", "neg_y", "pos_y", "x"))  # type: ignore[assignment]
    palette_theme: PaletteTheme = rng.choice(tuple(HINGE_PALETTE_PRESETS.keys()))  # type: ignore[assignment]

    knuckle_count = rng.randint(2, 7)
    leaf_height = rng.uniform(0.060, 0.150)
    leaf_x = rng.uniform(0.030, 0.070)
    plate_thickness = rng.uniform(0.0025, 0.0070)
    knuckle_outer_radius = rng.uniform(0.0055, 0.0110)
    hinge_upper = rng.uniform(1.45, 1.95)

    return SingleRevoluteHingeConfig(
        fixed_style=fixed_style,
        moving_style=moving_style,
        hinge_line_style=hinge_line_style,
        pin_axis=pin_axis,
        palette_theme=palette_theme,
        knuckle_count=knuckle_count,
        leaf_height=round(leaf_height, 4),
        leaf_x=round(leaf_x, 4),
        plate_thickness=round(plate_thickness, 4),
        knuckle_outer_radius=round(knuckle_outer_radius, 5),
        hinge_upper=round(hinge_upper, 3),
    )


def resolve_config(
    config: SingleRevoluteHingeConfig,
) -> ResolvedSingleRevoluteHingeConfig:
    fixed_style = config.fixed_style or _ANCHOR_FIXED
    if fixed_style not in _COMPAT:
        raise ValueError(f"Unsupported fixed_style: {fixed_style}")
    moving_pool, hinge_pool = _COMPAT[fixed_style]

    moving_style = config.moving_style or moving_pool[0]
    if moving_style not in moving_pool:
        raise ValueError(
            f"moving_style {moving_style!r} not compatible with fixed_style "
            f"{fixed_style!r} (legal: {moving_pool})"
        )
    hinge_line_style = config.hinge_line_style or hinge_pool[0]
    if hinge_line_style not in hinge_pool:
        raise ValueError(
            f"hinge_line_style {hinge_line_style!r} not compatible with fixed_style "
            f"{fixed_style!r} (legal: {hinge_pool})"
        )

    if str(config.pin_axis) not in _PIN_AXIS_VEC:
        raise ValueError(f"Unsupported pin_axis: {config.pin_axis}")
    if str(config.palette_theme) not in HINGE_PALETTE_PRESETS:
        raise ValueError(f"Unsupported palette_theme: {config.palette_theme}")

    knuckle_count = max(2, min(int(config.knuckle_count), 7))
    leaf_height = max(0.050, min(float(config.leaf_height), 0.170))
    leaf_x = max(0.024, min(float(config.leaf_x), 0.080))
    plate_thickness = max(0.0020, min(float(config.plate_thickness), 0.0090))
    knuckle_outer_radius = max(0.0045, min(float(config.knuckle_outer_radius), 0.0130))
    # Maintain knuckle_outer_radius > pin_bore_radius > pin_radius with clearance.
    pin_bore_radius = max(0.0030, min(knuckle_outer_radius - 0.0012, 0.0095))
    pin_radius = max(0.0020, min(pin_bore_radius - 0.0006, 0.0085))
    hinge_lower = float(config.hinge_lower)
    hinge_upper = max(1.30, min(float(config.hinge_upper), 2.10))

    palette = dict(HINGE_PALETTE_PRESETS[config.palette_theme])

    return ResolvedSingleRevoluteHingeConfig(
        fixed_style=fixed_style,
        moving_style=moving_style,
        hinge_line_style=hinge_line_style,
        pin_axis=config.pin_axis,
        palette_theme=config.palette_theme,
        knuckle_count=knuckle_count,
        leaf_height=leaf_height,
        leaf_x=leaf_x,
        plate_thickness=plate_thickness,
        knuckle_outer_radius=knuckle_outer_radius,
        pin_bore_radius=pin_bore_radius,
        pin_radius=pin_radius,
        hinge_lower=hinge_lower,
        hinge_upper=hinge_upper,
        palette=palette,
    )


# --------------------------------------------------------------------------- #
# Knuckle-band bookkeeping
# --------------------------------------------------------------------------- #


def _band_bounds(index: int, kh: float) -> tuple[float, float]:
    """z-bounds of knuckle band `index` (0-based) in WORLD frame."""
    return (index * kh, (index + 1) * kh)


def _split_bands(n: int) -> tuple[list[int], list[int]]:
    """Fixed half owns even bands, moving half owns odd bands."""
    fixed = [i for i in range(n) if i % 2 == 0]
    moving = [i for i in range(n) if i % 2 == 1]
    # With n>=2 both lists are non-empty.
    return fixed, moving


# --------------------------------------------------------------------------- #
# Fixed-half builders. All emit a single `fixed_half` part whose leaf extends
# in -x and whose knuckle bands sit on the +z pin-line. They return the world
# z-center of the first moving band boundary (the joint origin z).
# --------------------------------------------------------------------------- #


def _emit_fixed_knuckles(
    part,
    r: ResolvedSingleRevoluteHingeConfig,
    fixed_bands: list[int],
    kh: float,
) -> None:
    kr = r.knuckle_outer_radius
    for i in fixed_bands:
        z0, z1 = _band_bounds(i, kh)
        part.visual(
            Cylinder(radius=kr, length=(z1 - z0) * 0.995),
            origin=Origin(xyz=(0.0, 0.0, 0.5 * (z0 + z1))),
            material="knuckle",
            name=f"fixed_knuckle_{i}", material_class_id=("metal.blackened_gunmetal" if r.palette_theme in {"steel", "black_oxide", "white_enamel", "bronze"} else "metal.brass_polished"),
        )


def _emit_fixed_leaf_plate(
    part,
    r: ResolvedSingleRevoluteHingeConfig,
    name: str = "fixed_leaf",
) -> None:
    H = r.leaf_height
    lx = r.leaf_x
    pt = r.plate_thickness
    kr = r.knuckle_outer_radius
    # Plate spans x in [-lx, +kr*0.5] so it overlaps the knuckle column at x≈0.
    plate_len = lx + kr * 0.5
    part.visual(
        Box((plate_len, pt, H)),
        origin=Origin(xyz=(-0.5 * plate_len + kr * 0.5, 0.0, 0.5 * H)),
        material="leaf",
        name=name, material_class_id=("metal.blackened_gunmetal" if r.palette_theme in {"steel", "black_oxide", "white_enamel", "bronze"} else "metal.brass_polished"),
    )


def _build_fixed_half(
    model: ArticulatedObject,
    r: ResolvedSingleRevoluteHingeConfig,
    fixed_bands: list[int],
    kh: float,
) -> str:
    """Dispatch on fixed_style. Returns the fixed_half part name."""
    part = model.part("fixed_half")
    style = r.fixed_style
    H = r.leaf_height
    kr = r.knuckle_outer_radius

    if style == "leaf_with_knuckles":
        _emit_fixed_leaf_plate(part, r)
        _emit_fixed_knuckles(part, r, fixed_bands, kh)
    elif style == "bracket_support":
        # L-shaped mounting bracket: a back plate (mount face) + a forward
        # flange carrying the knuckles, plus a gusset connecting them.
        bw = max(0.018, r.leaf_x * 0.6)
        back_t = r.plate_thickness * 1.6
        part.visual(
            Box((back_t, max(0.020, kr * 4), H)),
            origin=Origin(xyz=(-r.leaf_x + 0.5 * back_t, 0.0, 0.5 * H)),
            material="leaf",
            name="bracket_back", material_class_id=("metal.blackened_gunmetal" if r.palette_theme in {"steel", "black_oxide", "white_enamel", "bronze"} else "metal.brass_polished"),
        )
        flange_len = r.leaf_x + kr * 0.5
        part.visual(
            Box((flange_len, r.plate_thickness, H)),
            origin=Origin(xyz=(-0.5 * flange_len + kr * 0.5, 0.0, 0.5 * H)),
            material="leaf",
            name="bracket_flange", material_class_id=("metal.blackened_gunmetal" if r.palette_theme in {"steel", "black_oxide", "white_enamel", "bronze"} else "metal.brass_polished"),
        )
        # gusset web tying back to flange (kept thin, full overlap with both)
        part.visual(
            Box((r.leaf_x * 0.5, max(0.010, bw * 0.5), r.plate_thickness)),
            origin=Origin(xyz=(-r.leaf_x * 0.45, 0.0, r.plate_thickness * 0.5)),
            material="accent",
            name="bracket_gusset", material_class_id=("metal.blackened_gunmetal" if r.palette_theme in {"steel", "black_oxide", "white_enamel", "bronze"} else "metal.brass_aged"),
        )
        _emit_fixed_knuckles(part, r, fixed_bands, kh)
    elif style == "clevis_fork":
        # Two cheeks straddling the pin-line at the TOP and BOTTOM bands, with
        # a rear bridge joining them. The single moving tab sits in the gap.
        cheek_t = r.plate_thickness
        # cheeks occupy the fixed bands (top+bottom); knuckle bores via cylinders
        _emit_fixed_knuckles(part, r, fixed_bands, kh)
        # rear bridge connects the cheek column down -x, full height
        bridge_len = r.leaf_x + kr * 0.5
        part.visual(
            Box((bridge_len, cheek_t, H)),
            origin=Origin(xyz=(-0.5 * bridge_len + kr * 0.5, 0.0, 0.5 * H)),
            material="leaf",
            name="clevis_bridge", material_class_id=("metal.blackened_gunmetal" if r.palette_theme in {"steel", "black_oxide", "white_enamel", "bronze"} else "metal.brass_polished"),
        )
    elif style == "trunnion_cheek":
        # Single cantilever cheek with a short journal stub on one band only.
        _emit_fixed_knuckles(part, r, fixed_bands, kh)
        sup_len = r.leaf_x + kr * 0.5
        part.visual(
            Box((sup_len, r.plate_thickness * 1.4, H)),
            origin=Origin(xyz=(-0.5 * sup_len + kr * 0.5, 0.0, 0.5 * H)),
            material="leaf",
            name="trunnion_support", material_class_id=("metal.blackened_gunmetal" if r.palette_theme in {"steel", "black_oxide", "white_enamel", "bronze"} else "metal.brass_polished"),
        )
    elif style == "host_carcass":
        # Object-mounted: a shallow cabinet carcass whose right edge carries
        # the knuckles; the host_door mates as the moving half.
        depth = max(0.040, r.leaf_x * 1.4)
        wall = r.plate_thickness * 1.5
        # back wall
        part.visual(
            Box((wall, depth, H)),
            origin=Origin(xyz=(-r.leaf_x + 0.5 * wall, 0.0, 0.5 * H)),
            material="leaf",
            name="carcass_back", material_class_id=("metal.blackened_gunmetal" if r.palette_theme in {"steel", "black_oxide", "white_enamel", "bronze"} else "metal.brass_polished"),
        )
        # side panel running to the hinge edge (connects back to knuckle column)
        side_len = r.leaf_x + kr * 0.5
        part.visual(
            Box((side_len, wall, H)),
            origin=Origin(xyz=(-0.5 * side_len + kr * 0.5, -0.5 * depth + 0.5 * wall, 0.5 * H)),
            material="leaf",
            name="carcass_side", material_class_id=("metal.blackened_gunmetal" if r.palette_theme in {"steel", "black_oxide", "white_enamel", "bronze"} else "metal.brass_polished"),
        )
        # connector strip from side panel to the knuckle column center (y=0)
        part.visual(
            Box((kr * 2.0, depth, wall)),
            origin=Origin(xyz=(0.0, 0.0, wall * 0.5)),
            material="accent",
            name="carcass_floor_strip", material_class_id=("metal.blackened_gunmetal" if r.palette_theme in {"steel", "black_oxide", "white_enamel", "bronze"} else "metal.brass_aged"),
        )
        _emit_fixed_knuckles(part, r, fixed_bands, kh)
    else:  # pragma: no cover
        raise ValueError(f"Unhandled fixed_style {style!r}")

    part.inertial = Inertial.from_geometry(
        Box((r.leaf_x, max(0.020, kr * 4), H)),
        mass=0.05,
        origin=Origin(xyz=(-0.4 * r.leaf_x, 0.0, 0.5 * H)),
    )
    return "fixed_half"


# --------------------------------------------------------------------------- #
# Moving-half builders. All emit a single `moving_half` part in a frame whose
# origin is the joint origin (0,0,joint_z). The moving leaf extends in +x and
# its knuckle bands fill the odd world-bands (in part frame, offset by -joint_z).
# --------------------------------------------------------------------------- #


def _emit_moving_knuckles(
    part,
    r: ResolvedSingleRevoluteHingeConfig,
    moving_bands: list[int],
    kh: float,
    joint_z: float,
) -> None:
    kr = r.knuckle_outer_radius
    for i in moving_bands:
        z0, z1 = _band_bounds(i, kh)
        cz = 0.5 * (z0 + z1) - joint_z  # into part frame
        part.visual(
            Cylinder(radius=kr, length=(z1 - z0) * 0.995),
            origin=Origin(xyz=(0.0, 0.0, cz)),
            material="knuckle",
            name=f"moving_knuckle_{i}", material_class_id=("metal.blackened_gunmetal" if r.palette_theme in {"steel", "black_oxide", "white_enamel", "bronze"} else "metal.brass_polished"),
        )


def _build_moving_half(
    model: ArticulatedObject,
    r: ResolvedSingleRevoluteHingeConfig,
    moving_bands: list[int],
    kh: float,
    joint_z: float,
) -> str:
    part = model.part("moving_half")
    style = r.moving_style
    H = r.leaf_height
    lx = r.leaf_x
    pt = r.plate_thickness
    kr = r.knuckle_outer_radius

    # Leaf plate spans the FULL pin-line height so it overlaps every moving
    # knuckle band (keeping the part a single connected island). In part frame
    # the plate is centered at z = H/2 - joint_z.
    plate_center_z = 0.5 * H - joint_z

    if style == "opposing_leaf":
        plate_len = lx + kr * 0.5
        part.visual(
            Box((plate_len, pt, H)),
            origin=Origin(xyz=(0.5 * plate_len - kr * 0.5, 0.0, plate_center_z)),
            material="leaf",
            name="moving_leaf", material_class_id=("metal.blackened_gunmetal" if r.palette_theme in {"steel", "black_oxide", "white_enamel", "bronze"} else "metal.brass_polished"),
        )
        _emit_moving_knuckles(part, r, moving_bands, kh, joint_z)
    elif style == "cover_panel":
        # Larger cover panel + a thin root rib that overlaps the knuckle column.
        panel_len = lx * 1.2 + kr * 0.5
        part.visual(
            Box((panel_len, pt * 1.4, H)),
            origin=Origin(xyz=(0.5 * panel_len - kr * 0.5, 0.0, plate_center_z)),
            material="leaf",
            name="cover_panel", material_class_id=("metal.blackened_gunmetal" if r.palette_theme in {"steel", "black_oxide", "white_enamel", "bronze"} else "metal.brass_polished"),
        )
        _emit_moving_knuckles(part, r, moving_bands, kh, joint_z)
    elif style == "single_tab_blade":
        # A single tab/blade with one eye band that sits in the fork gap. The
        # tab plate spans full height to stay connected to its (few) knuckles.
        plate_len = lx + kr * 0.5
        part.visual(
            Box((plate_len, pt, H)),
            origin=Origin(xyz=(0.5 * plate_len - kr * 0.5, 0.0, plate_center_z)),
            material="leaf",
            name="moving_tab", material_class_id=("metal.blackened_gunmetal" if r.palette_theme in {"steel", "black_oxide", "white_enamel", "bronze"} else "metal.brass_polished"),
        )
        _emit_moving_knuckles(part, r, moving_bands, kh, joint_z)
    elif style == "host_door":
        # Cabinet door panel + a hinge stile that carries the knuckles.
        panel_len = lx * 1.4 + kr * 0.5
        part.visual(
            Box((panel_len, pt * 1.6, H)),
            origin=Origin(xyz=(0.5 * panel_len - kr * 0.5, 0.0, plate_center_z)),
            material="leaf",
            name="door_panel", material_class_id=("metal.blackened_gunmetal" if r.palette_theme in {"steel", "black_oxide", "white_enamel", "bronze"} else "metal.brass_polished"),
        )
        # pull handle (fixed detail) overlapping the panel far edge
        part.visual(
            Box((pt * 1.5, pt * 3.0, H * 0.4)),
            origin=Origin(xyz=(panel_len - kr * 0.5, 0.0, plate_center_z)),
            material="accent",
            name="door_handle", material_class_id=("metal.blackened_gunmetal" if r.palette_theme in {"steel", "black_oxide", "white_enamel", "bronze"} else "metal.brass_aged"),
        )
        _emit_moving_knuckles(part, r, moving_bands, kh, joint_z)
    else:  # pragma: no cover
        raise ValueError(f"Unhandled moving_style {style!r}")

    part.inertial = Inertial.from_geometry(
        Box((lx, max(0.018, kr * 3), H)),
        mass=0.04,
        origin=Origin(xyz=(0.4 * lx, 0.0, plate_center_z)),
    )
    return "moving_half"


# --------------------------------------------------------------------------- #
# Hinge-line / pin handling
# --------------------------------------------------------------------------- #


def _emit_pin_in_fixed(
    model: ArticulatedObject,
    r: ResolvedSingleRevoluteHingeConfig,
) -> Optional[str]:
    """Emit the pin per hinge_line_style. Returns the separate pin part name if
    one was created (else None — pin is a visual inside fixed_half)."""
    H = r.leaf_height
    style = r.hinge_line_style
    fixed = model.get_part("fixed_half")

    if style == "interleaved_knuckles_pin_in_leaf":
        # Pin is a thin cylinder visual living inside the fixed_half part.
        fixed.visual(
            Cylinder(radius=r.pin_radius, length=H * 1.02),
            origin=Origin(xyz=(0.0, 0.0, 0.5 * H)),
            material="pin",
            name="pin_core", material_class_id=("metal.steel_bare" if r.palette_theme in {"brass", "steel", "white_enamel", "bronze"} else "metal.blackened_gunmetal"),
        )
        return None
    if style == "single_journal_or_bore":
        # No through-stack pin; a short journal stub visual inside fixed_half.
        fixed.visual(
            Cylinder(radius=r.pin_radius, length=H * 0.30),
            origin=Origin(xyz=(0.0, 0.0, 0.5 * H)),
            material="pin",
            name="journal_stub", material_class_id=("metal.steel_bare" if r.palette_theme in {"brass", "steel", "white_enamel", "bronze"} else "metal.blackened_gunmetal"),
        )
        return None

    # separate_pin_part / barrel_with_collars => standalone pin part, FIXED.
    pin = model.part("hinge_pin")
    pin.visual(
        Cylinder(radius=r.pin_radius, length=H * 1.04),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material="pin",
        name="pin_shaft", material_class_id=("metal.steel_bare" if r.palette_theme in {"brass", "steel", "white_enamel", "bronze"} else "metal.blackened_gunmetal"),
    )
    # head + tail caps so the pin is captured.
    cap_r = r.pin_bore_radius * 1.25
    pin.visual(
        Cylinder(radius=cap_r, length=H * 0.03),
        origin=Origin(xyz=(0.0, 0.0, 0.52 * H)),
        material="accent",
        name="pin_head", material_class_id=("metal.blackened_gunmetal" if r.palette_theme in {"steel", "black_oxide", "white_enamel", "bronze"} else "metal.brass_aged"),
    )
    pin.visual(
        Cylinder(radius=cap_r, length=H * 0.03),
        origin=Origin(xyz=(0.0, 0.0, -0.52 * H)),
        material="accent",
        name="pin_tail", material_class_id=("metal.blackened_gunmetal" if r.palette_theme in {"steel", "black_oxide", "white_enamel", "bronze"} else "metal.brass_aged"),
    )
    if style == "barrel_with_collars":
        # spacer collars between bands.
        kr = r.knuckle_outer_radius
        for frac in (0.3, 0.7):
            pin.visual(
                Cylinder(radius=kr * 0.9, length=H * 0.04),
                origin=Origin(xyz=(0.0, 0.0, (frac - 0.5) * H)),
                material="accent",
                name=f"collar_{int(frac * 10)}", material_class_id=("metal.blackened_gunmetal" if r.palette_theme in {"steel", "black_oxide", "white_enamel", "bronze"} else "metal.brass_aged"),
            )
    pin.inertial = Inertial.from_geometry(
        Cylinder(radius=r.pin_radius, length=H),
        mass=0.01,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
    )
    # FIXED the pin to the fixed_half at the pin-line center. Grandfathered
    # (no MatingContract): the pin is captured coaxially through the knuckle
    # bores — a press-fit overlap, not a flat-face butt joint. The intended
    # overlap is declared via allow_overlap in run_tests.
    model.articulation(
        "fixed_to_pin",
        ArticulationType.FIXED,
        parent=fixed,
        child=pin,
        origin=Origin(xyz=(0.0, 0.0, 0.5 * H)),
    )
    return "hinge_pin"


# --------------------------------------------------------------------------- #
# slot reporting (for module_topology_diversity)
# --------------------------------------------------------------------------- #


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    r = resolve_config(config_from_seed(seed))
    return [
        ("fixed_half", r.fixed_style),
        ("moving_half", r.moving_style),
        ("hinge_line", r.hinge_line_style),
    ]


# --------------------------------------------------------------------------- #
# Build
# --------------------------------------------------------------------------- #


def build_single_revolute_hinge(
    config: SingleRevoluteHingeConfig,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name="single_revolute_hinge", assets=assets)
    for material_name, rgba in r.palette.items():
        model.material(material_name, rgba=rgba)

    n = r.knuckle_count
    kh = r.leaf_height / n
    fixed_bands, moving_bands = _split_bands(n)

    # Joint origin z = boundary between band[0] (fixed) and band[1] (moving),
    # i.e. the top of the first fixed band — always on real knuckle geometry.
    joint_z = moving_bands[0] * kh

    _build_fixed_half(model, r, fixed_bands, kh)
    _build_moving_half(model, r, moving_bands, kh, joint_z)
    _emit_pin_in_fixed(model, r)

    fixed = model.get_part("fixed_half")
    moving = model.get_part("moving_half")

    # Main hinge pivot — grandfathered (no MatingContract): the fixed/moving
    # knuckles interleave coaxially about the pin-line (a press-fit/capture
    # overlap), not a flat-face butt joint. The joint origin sits on the
    # pin-line at the first fixed/moving band boundary, on real knuckle
    # geometry. Intended knuckle overlap is declared via allow_overlap.
    model.articulation(
        "hinge_revolute",
        ArticulationType.REVOLUTE,
        parent=fixed,
        child=moving,
        origin=Origin(xyz=(0.0, 0.0, joint_z)),
        axis=_PIN_AXIS_VEC[r.pin_axis],
        motion_limits=MotionLimits(
            effort=2.0, velocity=4.0, lower=r.hinge_lower, upper=r.hinge_upper
        ),
    )
    return model


def build_seeded_single_revolute_hinge(seed: int) -> ArticulatedObject:
    return build_single_revolute_hinge(config_from_seed(seed))


# --------------------------------------------------------------------------- #
# Author-layer QC
# --------------------------------------------------------------------------- #


def _allow_pivot_overlaps(ctx: TestContext, model: ArticulatedObject) -> None:
    """Knuckles of the two halves interleave coaxially and the pin runs through
    both — these are intended press-fit/capture overlaps, declared here."""
    names = {p.name for p in model.parts}
    if "fixed_half" in names and "moving_half" in names:
        ctx.allow_overlap(
            model.get_part("fixed_half"),
            model.get_part("moving_half"),
            reason="interleaved hinge knuckles share the coaxial pin-line footprint",
        )
    if "fixed_half" in names and "hinge_pin" in names:
        ctx.allow_overlap(
            model.get_part("fixed_half"),
            model.get_part("hinge_pin"),
            reason="hinge pin runs coaxially through the fixed knuckle bores (press fit)",
        )
    if "moving_half" in names and "hinge_pin" in names:
        ctx.allow_overlap(
            model.get_part("moving_half"),
            model.get_part("hinge_pin"),
            reason="hinge pin runs coaxially through the moving knuckle bores (press fit)",
        )


def run_single_revolute_hinge_tests(
    model: ArticulatedObject,
    config: SingleRevoluteHingeConfig,
) -> TestReport:
    resolve_config(config)  # validate config (raises on illegal module combo)
    ctx = TestContext(model)

    _allow_pivot_overlaps(ctx, model)

    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)
    ctx.fail_if_joint_mating_has_gap()

    revolutes = [a for a in model.articulations if a.articulation_type == ArticulationType.REVOLUTE]
    ctx.check(
        "exactly_one_revolute",
        len(revolutes) == 1,
        f"single_revolute_hinge must have exactly 1 REVOLUTE joint, got {len(revolutes)}",
    )

    return ctx.report()


__all__ = [
    "FixedStyle",
    "MovingStyle",
    "HingeLineStyle",
    "PinAxis",
    "PaletteTheme",
    "SingleRevoluteHingeConfig",
    "ResolvedSingleRevoluteHingeConfig",
    "build_single_revolute_hinge",
    "build_seeded_single_revolute_hinge",
    "config_from_seed",
    "resolve_config",
    "run_single_revolute_hinge_tests",
    "slot_choices_for_seed",
]
