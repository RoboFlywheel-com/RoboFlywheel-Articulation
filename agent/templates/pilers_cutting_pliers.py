# SPDX-License-Identifier: Apache-2.0

"""Cutting-pliers modular template (0611 / pilers_cutting_pliers).

Sourced from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/pilers_cutting_pliers.md``
and the ``pictureX/0611/Pilers_cutting_pliers`` 5-star pool (1 origin_anchor
``diagonal_cutting_pliers_001`` + 9 single-axis fork variants).

Structure (pattern ``mixed``):

* baseline 3-part / 2-joint chain: ``root_half`` (root) + ``moving_half`` +
  ``spring_clip``. ``plier_pivot`` REVOLUTE (root -> moving, axis +Z) opens the
  jaws; ``clip_swing`` REVOLUTE (moving -> spring_clip, axis +Z) swings the
  visible wire spring on the moving handle.
* ``leverage_mechanism = compound_link`` swaps a 4-part chain
  root -> compound_link -> moving (adding ``compound_link`` part + mimic joint
  ``compound_to_moving``). ``fixed_rivet`` and ``offset_pivot`` keep the
  baseline 3-part chain (``offset_pivot`` just adds decorative washers).

Slots:

* ``cutting_head`` (4): diagonal_cutter (baseline) / flush_cutter / end_cutter /
  heavy_duty_bevel. Each swaps ``jaw_profile`` + ``cutting_edge_profile``
  planar polylines, mirrored across both halves.
* ``leverage_mechanism`` (3): fixed_rivet / offset_pivot / compound_link.
* ``return_spring`` (3): wire_clip (U-wire, baseline) / leaf_spring / torsion_spring.
  Swaps ``spring_wire`` visual on ``spring_clip``; part / joint count unchanged.
* ``handle_form`` (4): straight_dipped (baseline) / long_handle /
  guarded_insulated_grip / two_material_comfort_grip. Swaps
  ``left_grip_profile`` + ``left_blue_profile`` planar polylines.

``palette_style`` (6): pure material rgba axis; does not enter slot_choices
and does not change topology.

Pivot pins are captured-pin geometry (rivet shaft through the moving hub
lap; clip pin through the spring wire loop), so their joints omit
``MatingContract`` and are guarded by broad ``allow_overlap`` between the
two halves plus an elem-scoped allow_overlap between ``clip_pin`` and
``spring_wire``.
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
    Cylinder,
    Mimic,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
    mesh_from_geometry,
    tube_from_spline_points,
)

__modular__ = True

# ---------------------------------------------------------------------------
# Enum axes
# ---------------------------------------------------------------------------
CuttingHead = Literal["diagonal_cutter", "flush_cutter", "end_cutter", "heavy_duty_bevel"]
LeverageMechanism = Literal["fixed_rivet", "offset_pivot", "compound_link"]
ReturnSpring = Literal["wire_clip", "leaf_spring", "torsion_spring"]
HandleForm = Literal[
    "straight_dipped",
    "long_handle",
    "guarded_insulated_grip",
    "two_material_comfort_grip",
]
PaletteStyle = Literal[
    "steel_red_blue",
    "black_orange",
    "chrome_natural",
    "gunmetal_yellow",
    "polished_silver",
    "industrial_green",
]

CUTTING_HEADS: tuple[CuttingHead, ...] = (
    "diagonal_cutter",
    "flush_cutter",
    "end_cutter",
    "heavy_duty_bevel",
)
LEVERAGE_MECHANISMS: tuple[LeverageMechanism, ...] = (
    "fixed_rivet",
    "offset_pivot",
    "compound_link",
)
RETURN_SPRINGS: tuple[ReturnSpring, ...] = (
    "wire_clip",
    "leaf_spring",
    "torsion_spring",
)
HANDLE_FORMS: tuple[HandleForm, ...] = (
    "straight_dipped",
    "long_handle",
    "guarded_insulated_grip",
    "two_material_comfort_grip",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "steel_red_blue",
    "black_orange",
    "chrome_natural",
    "gunmetal_yellow",
    "polished_silver",
    "industrial_green",
)

# Compound-link toggle offset (source: V-L1 model.py L23 ``PIVOT_OFFSET``).
PIVOT_OFFSET = 0.0045

# ---------------------------------------------------------------------------
# Palettes (spec §palette; each provides 5 material rgba keys the builder uses)
# metal covers 3 flavours (steel/chrome/gunmetal), rubber covers 3 flavours
# (red_blue/orange/green). ``chrome_natural`` and ``polished_silver`` keep a
# metal grip (rubber -> dark metallic) to widen the metal palette coverage.
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "steel_red_blue": {
        "forged": (0.66, 0.68, 0.69, 1.0),
        "polished": (0.86, 0.88, 0.89, 1.0),
        "cutting": (0.22, 0.24, 0.25, 1.0),
        "grip": (0.88, 0.025, 0.035, 1.0),
        "inlay": (0.035, 0.12, 0.50, 1.0),
    },
    "black_orange": {
        "forged": (0.18, 0.18, 0.20, 1.0),
        "polished": (0.55, 0.56, 0.58, 1.0),
        "cutting": (0.10, 0.10, 0.12, 1.0),
        "grip": (0.95, 0.42, 0.05, 1.0),
        "inlay": (0.10, 0.10, 0.12, 1.0),
    },
    "chrome_natural": {
        "forged": (0.82, 0.84, 0.87, 1.0),
        "polished": (0.90, 0.91, 0.93, 1.0),
        "cutting": (0.35, 0.37, 0.40, 1.0),
        "grip": (0.30, 0.30, 0.32, 1.0),
        "inlay": (0.55, 0.55, 0.58, 1.0),
    },
    "gunmetal_yellow": {
        "forged": (0.42, 0.44, 0.47, 1.0),
        "polished": (0.60, 0.62, 0.65, 1.0),
        "cutting": (0.20, 0.20, 0.22, 1.0),
        "grip": (0.93, 0.78, 0.10, 1.0),
        "inlay": (0.15, 0.15, 0.17, 1.0),
    },
    "polished_silver": {
        "forged": (0.78, 0.80, 0.82, 1.0),
        "polished": (0.92, 0.93, 0.95, 1.0),
        "cutting": (0.30, 0.32, 0.34, 1.0),
        "grip": (0.20, 0.22, 0.25, 1.0),
        "inlay": (0.72, 0.14, 0.14, 1.0),
    },
    "industrial_green": {
        "forged": (0.55, 0.57, 0.59, 1.0),
        "polished": (0.80, 0.82, 0.84, 1.0),
        "cutting": (0.18, 0.20, 0.22, 1.0),
        "grip": (0.10, 0.42, 0.20, 1.0),
        "inlay": (0.90, 0.85, 0.15, 1.0),
    },
}


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class PilersCuttingPliersConfig:
    cutting_head: CuttingHead | None = None
    leverage_mechanism: LeverageMechanism | None = None
    return_spring: ReturnSpring | None = None
    handle_form: HandleForm | None = None
    palette_style: PaletteStyle = "steel_red_blue"
    overall_len_scale: float = 1.0
    jaw_len_scale: float = 1.0
    grip_girth_scale: float = 1.0
    open_angle_scale: float = 1.0
    name: str = "pilers_cutting_pliers"


@dataclass(frozen=True)
class ResolvedConfig:
    cutting_head: CuttingHead
    leverage_mechanism: LeverageMechanism
    return_spring: ReturnSpring
    handle_form: HandleForm
    palette_style: PaletteStyle
    overall_len_scale: float
    jaw_len_scale: float
    grip_girth_scale: float
    open_angle: float
    open_lower: float
    name: str

    @property
    def is_compound(self) -> bool:
        return self.leverage_mechanism == "compound_link"


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


def config_from_seed(seed: int) -> PilersCuttingPliersConfig:
    rng = random.Random(seed)
    head = rng.choices(CUTTING_HEADS, weights=[5, 3, 3, 3], k=1)[0]
    lev = rng.choices(LEVERAGE_MECHANISMS, weights=[5, 3, 2], k=1)[0]
    ret = rng.choices(RETURN_SPRINGS, weights=[5, 3, 2], k=1)[0]
    hand = rng.choices(HANDLE_FORMS, weights=[5, 3, 3, 3], k=1)[0]
    return PilersCuttingPliersConfig(
        cutting_head=head,
        leverage_mechanism=lev,
        return_spring=ret,
        handle_form=hand,
        palette_style=rng.choice(PALETTE_STYLES),
        overall_len_scale=round(rng.uniform(0.90, 1.15), 4),
        jaw_len_scale=round(rng.uniform(0.90, 1.10), 4),
        grip_girth_scale=round(rng.uniform(0.90, 1.10), 4),
        open_angle_scale=round(rng.uniform(0.80, 1.20), 4),
        name=f"seeded_pilers_cutting_pliers_{seed}",
    )


def resolve_config(config: PilersCuttingPliersConfig | None = None) -> ResolvedConfig:
    cfg = config or PilersCuttingPliersConfig()
    head = _pick(cfg.cutting_head, CUTTING_HEADS)
    lev = _pick(cfg.leverage_mechanism, LEVERAGE_MECHANISMS)
    ret = _pick(cfg.return_spring, RETURN_SPRINGS)
    hand = _pick(cfg.handle_form, HANDLE_FORMS)
    palette = _pick(cfg.palette_style, PALETTE_STYLES)

    overall = _clamp(cfg.overall_len_scale, 0.90, 1.15)
    jaw_len = _clamp(cfg.jaw_len_scale, 0.90, 1.10)
    grip_girth = _clamp(cfg.grip_girth_scale, 0.90, 1.10)
    open_scale = _clamp(cfg.open_angle_scale, 0.80, 1.20)

    # Baseline pivot travel from origin_anchor: lower=-0.070, upper=0.34.
    open_upper = _clamp(0.34 * open_scale, 0.20, 0.42)
    open_lower = _clamp(-0.070 * open_scale, -0.10, -0.03)

    return ResolvedConfig(
        cutting_head=head,
        leverage_mechanism=lev,
        return_spring=ret,
        handle_form=hand,
        palette_style=palette,
        overall_len_scale=overall,
        jaw_len_scale=jaw_len,
        grip_girth_scale=grip_girth,
        open_angle=open_upper,
        open_lower=open_lower,
        name=cfg.name or "pilers_cutting_pliers",
    )


def with_overrides(
    config: PilersCuttingPliersConfig, **kwargs: object
) -> PilersCuttingPliersConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: PilersCuttingPliersConfig | ResolvedConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedConfig) else resolve_config(config)
    return (
        ("cutting_head", r.cutting_head),
        ("leverage_mechanism", r.leverage_mechanism),
        ("return_spring", r.return_spring),
        ("handle_form", r.handle_form),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Geometry helpers (from P0 origin_anchor).
# ---------------------------------------------------------------------------
def _mirror_x(points: list[tuple[float, float]]) -> list[tuple[float, float]]:
    return [(-x, y) for x, y in points]


def _scale_y(points: list[tuple[float, float]], sy: float) -> list[tuple[float, float]]:
    return [(x, y * sy) for x, y in points]


def _scale_all(
    points: list[tuple[float, float]], sx: float, sy: float
) -> list[tuple[float, float]]:
    return [(x * sx, y * sy) for x, y in points]


def _profile_solid(
    points: list[tuple[float, float]],
    thickness: float,
    *,
    corner_radius: float = 0.0,
):
    solid = (
        cq.Workplane("XY")
        .polyline(points)
        .close()
        .extrude(thickness)
        .translate((0.0, 0.0, -thickness / 2.0))
    )
    if corner_radius > 0.0:
        solid = solid.edges("|Z").fillet(corner_radius)
    return solid


def _forged_half(
    tang_points: list[tuple[float, float]],
    jaw_points: list[tuple[float, float]],
    thickness: float,
):
    tang = _profile_solid(tang_points, thickness, corner_radius=0.0012)
    jaw = _profile_solid(jaw_points, thickness, corner_radius=0.0008)
    boss = (
        cq.Workplane("XY").circle(0.012).extrude(thickness).translate((0.0, 0.0, -thickness / 2.0))
    )
    pivot_hole = (
        cq.Workplane("XY")
        .circle(0.00425)
        .extrude(thickness + 0.004)
        .translate((0.0, 0.0, -(thickness + 0.004) / 2.0))
    )
    return tang.union(boss).union(jaw).cut(pivot_hole)


# ---------------------------------------------------------------------------
# Baseline planar profiles (P0 origin_anchor). All polylines use the +Y-jaw
# frame; ``_mirror_x`` mirrors to the -Y half's local frame.
# ---------------------------------------------------------------------------
TANG_PROFILE_BASE = [
    (-0.032, -0.103),
    (-0.040, -0.098),
    (-0.039, -0.075),
    (-0.035, -0.050),
    (-0.030, -0.028),
    (-0.024, -0.014),
    (-0.014, -0.006),
    (-0.010, 0.004),
    (0.008, 0.006),
    (0.006, -0.008),
    (-0.006, -0.020),
    (-0.014, -0.045),
    (-0.023, -0.075),
    (-0.025, -0.099),
]


# ---------------------------------------------------------------------------
# Slot A -- cutting_head. Returns (jaw_profile, cutting_edge_profile,
# cutting_edge_thickness). Jaw points +Y.
# ---------------------------------------------------------------------------
def _diagonal_jaw() -> tuple[list[tuple[float, float]], list[tuple[float, float]], float]:
    jaw = [
        (-0.006, 0.004),
        (0.008, 0.010),
        (0.015, 0.020),
        (0.020, 0.033),
        (0.022, 0.046),
        (0.017, 0.054),
        (0.008, 0.055),
        (0.003, 0.050),
        (0.002, 0.040),
        (0.002, 0.028),
        (0.001, 0.018),
        (-0.004, 0.010),
    ]
    edge = [
        (0.0018, 0.018),
        (0.0030, 0.029),
        (0.0020, 0.040),
        (0.0018, 0.049),
        (0.0048, 0.053),
        (0.0060, 0.045),
        (0.0055, 0.030),
        (0.0045, 0.020),
    ]
    return jaw, edge, 0.0008


def _flush_jaw() -> tuple[list[tuple[float, float]], list[tuple[float, float]], float]:
    jaw = [
        (-0.006, 0.004),
        (0.007, 0.010),
        (0.010, 0.020),
        (0.011, 0.033),
        (0.011, 0.044),
        (0.008, 0.050),
        (0.003, 0.050),
        (0.001, 0.045),
        (0.001, 0.034),
        (0.001, 0.022),
        (-0.001, 0.014),
        (-0.004, 0.010),
    ]
    edge = [
        (0.0015, 0.022),
        (0.0015, 0.035),
        (0.0015, 0.046),
        (0.0018, 0.049),
        (0.0055, 0.050),
        (0.0060, 0.044),
        (0.0055, 0.034),
        (0.0050, 0.024),
    ]
    return jaw, edge, 0.0008


def _end_cutter_jaw() -> tuple[list[tuple[float, float]], list[tuple[float, float]], float]:
    # Wider rounded transverse nipper tip.
    jaw = [
        (-0.006, 0.004),
        (0.007, 0.012),
        (0.014, 0.020),
        (0.020, 0.030),
        (0.024, 0.038),
        (0.023, 0.044),
        (0.019, 0.049),
        (0.013, 0.052),
        (0.007, 0.051),
        (0.003, 0.048),
        (0.002, 0.040),
        (0.002, 0.030),
        (0.001, 0.018),
        (-0.004, 0.010),
    ]
    edge = [
        (0.0018, 0.032),
        (0.0018, 0.042),
        (0.0018, 0.048),
        (0.004, 0.051),
        (0.010, 0.052),
        (0.016, 0.050),
        (0.020, 0.046),
        (0.022, 0.040),
        (0.020, 0.035),
        (0.014, 0.032),
        (0.008, 0.031),
    ]
    return jaw, edge, 0.0008


def _heavy_duty_jaw() -> tuple[list[tuple[float, float]], list[tuple[float, float]], float]:
    jaw = [
        (-0.006, 0.004),
        (0.010, 0.010),
        (0.020, 0.020),
        (0.028, 0.030),
        (0.030, 0.040),
        (0.026, 0.048),
        (0.018, 0.054),
        (0.010, 0.055),
        (0.004, 0.050),
        (0.002, 0.040),
        (0.003, 0.028),
        (0.001, 0.018),
        (-0.004, 0.010),
    ]
    edge = [
        (0.0018, 0.020),
        (0.0035, 0.030),
        (0.0055, 0.038),
        (0.0080, 0.046),
        (0.0110, 0.050),
        (0.0100, 0.045),
        (0.0080, 0.038),
        (0.0060, 0.030),
        (0.0045, 0.022),
    ]
    return jaw, edge, 0.0011


_JAW_BUILDERS = {
    "diagonal_cutter": _diagonal_jaw,
    "flush_cutter": _flush_jaw,
    "end_cutter": _end_cutter_jaw,
    "heavy_duty_bevel": _heavy_duty_jaw,
}


# ---------------------------------------------------------------------------
# Slot D -- handle_form. Returns (grip_profile, inlay_profile). Both are in the
# +Y-jaw half frame (grip sweeps to -Y).
# ---------------------------------------------------------------------------
def _straight_dipped_grip() -> tuple[list[tuple[float, float]], list[tuple[float, float]]]:
    grip = [
        (-0.010, -0.006),
        (-0.024, -0.010),
        (-0.035, -0.020),
        (-0.041, -0.034),
        (-0.040, -0.053),
        (-0.041, -0.079),
        (-0.041, -0.100),
        (-0.037, -0.108),
        (-0.029, -0.109),
        (-0.023, -0.102),
        (-0.021, -0.080),
        (-0.017, -0.053),
        (-0.013, -0.029),
        (-0.007, -0.013),
    ]
    inlay = [
        (-0.0385, -0.036),
        (-0.0400, -0.078),
        (-0.0400, -0.099),
        (-0.0360, -0.1065),
        (-0.0300, -0.1075),
        (-0.0250, -0.100),
        (-0.0230, -0.081),
        (-0.0260, -0.063),
        (-0.0310, -0.045),
    ]
    return grip, inlay


def _long_handle_grip() -> tuple[list[tuple[float, float]], list[tuple[float, float]]]:
    grip = [
        (-0.010, -0.006),
        (-0.024, -0.010),
        (-0.035, -0.020),
        (-0.041, -0.036),
        (-0.041, -0.058),
        (-0.042, -0.088),
        (-0.042, -0.114),
        (-0.038, -0.122),
        (-0.030, -0.125),
        (-0.024, -0.118),
        (-0.022, -0.090),
        (-0.018, -0.060),
        (-0.014, -0.032),
        (-0.007, -0.013),
    ]
    inlay = [
        (-0.0385, -0.038),
        (-0.0400, -0.086),
        (-0.0405, -0.112),
        (-0.0365, -0.120),
        (-0.0305, -0.122),
        (-0.0255, -0.115),
        (-0.0235, -0.090),
        (-0.0270, -0.068),
        (-0.0315, -0.048),
    ]
    return grip, inlay


def _guarded_grip() -> tuple[list[tuple[float, float]], list[tuple[float, float]]]:
    # Add a mid-body finger guard flare (half-width bumps up by ~0.005).
    grip = [
        (-0.010, -0.006),
        (-0.024, -0.010),
        (-0.035, -0.020),
        (-0.041, -0.034),
        (-0.045, -0.048),
        (-0.046, -0.062),
        (-0.045, -0.076),
        (-0.041, -0.090),
        (-0.041, -0.104),
        (-0.037, -0.110),
        (-0.029, -0.111),
        (-0.023, -0.104),
        (-0.023, -0.088),
        (-0.020, -0.070),
        (-0.017, -0.052),
        (-0.013, -0.029),
        (-0.007, -0.013),
    ]
    inlay = [
        (-0.0385, -0.036),
        (-0.0430, -0.058),
        (-0.0430, -0.074),
        (-0.0400, -0.092),
        (-0.0400, -0.102),
        (-0.0360, -0.1085),
        (-0.0300, -0.1095),
        (-0.0250, -0.102),
        (-0.0230, -0.086),
        (-0.0270, -0.068),
        (-0.0310, -0.048),
    ]
    return grip, inlay


def _comfort_grip() -> tuple[list[tuple[float, float]], list[tuple[float, float]]]:
    grip = [
        (-0.010, -0.006),
        (-0.024, -0.010),
        (-0.036, -0.022),
        (-0.042, -0.036),
        (-0.043, -0.058),
        (-0.044, -0.082),
        (-0.044, -0.108),
        (-0.038, -0.116),
        (-0.028, -0.117),
        (-0.022, -0.110),
        (-0.021, -0.084),
        (-0.017, -0.056),
        (-0.013, -0.030),
        (-0.007, -0.013),
    ]
    # Broader, longer comfort inlay.
    inlay = [
        (-0.0405, -0.040),
        (-0.0430, -0.076),
        (-0.0430, -0.104),
        (-0.0385, -0.113),
        (-0.0300, -0.115),
        (-0.0230, -0.108),
        (-0.0210, -0.082),
        (-0.0245, -0.062),
        (-0.0300, -0.044),
    ]
    return grip, inlay


_HANDLE_BUILDERS = {
    "straight_dipped": _straight_dipped_grip,
    "long_handle": _long_handle_grip,
    "guarded_insulated_grip": _guarded_grip,
    "two_material_comfort_grip": _comfort_grip,
}


# ---------------------------------------------------------------------------
# Slot C -- return_spring. Builds the spring_wire visual mesh anchored on
# ``spring_clip``. All three variants share the same part / joint count.
# The wire sits in the spring_clip's local frame; the clip_pin lives at
# (0.030, -0.086, 0.013) in moving_half's frame.
# ---------------------------------------------------------------------------
def _wire_clip_mesh():
    pts = [
        (0.000, 0.000, 0.000),
        (0.001, -0.007, 0.000),
        (-0.001, -0.016, 0.000),
        (-0.006, -0.022, 0.000),
        (-0.011, -0.022, 0.000),
        (-0.014, -0.016, 0.000),
        (-0.014, -0.009, 0.000),
        (-0.011, -0.003, 0.000),
    ]
    return tube_from_spline_points(
        pts,
        radius=0.00115,
        samples_per_segment=16,
        radial_segments=18,
        cap_ends=True,
    )


def _leaf_spring_mesh():
    # Near-straight leaf running along -y with a subtle arc; slightly larger
    # tube radius to read as a leaf strip section.
    pts = [
        (0.000, 0.000, 0.000),
        (-0.001, -0.006, 0.000),
        (-0.002, -0.014, 0.000),
        (-0.003, -0.022, 0.000),
        (-0.004, -0.028, 0.000),
        (-0.003, -0.032, 0.000),
        (0.001, -0.030, 0.000),
        (0.002, -0.024, 0.000),
    ]
    return tube_from_spline_points(
        pts,
        radius=0.0014,
        samples_per_segment=16,
        radial_segments=16,
        cap_ends=True,
    )


def _torsion_spring_mesh():
    # 2.5 helical turns wrapping the clip pin axis (+Z), then a short arm.
    pts: list[tuple[float, float, float]] = []
    coils = 2.5
    coil_r = 0.0032
    z_span = 0.005
    steps = 24
    for i in range(steps + 1):
        t = i / steps
        angle = 2.0 * math.pi * coils * t
        x = coil_r * math.cos(angle) - coil_r  # start near origin
        y = coil_r * math.sin(angle)
        z = -z_span / 2.0 + z_span * t
        pts.append((x, y, z))
    # Trailing arm running along -y away from the coil.
    tail_start = pts[-1]
    pts.append((tail_start[0] - 0.002, tail_start[1] - 0.006, tail_start[2]))
    pts.append((tail_start[0] - 0.004, tail_start[1] - 0.014, tail_start[2]))
    pts.append((tail_start[0] - 0.005, tail_start[1] - 0.020, tail_start[2]))
    return tube_from_spline_points(
        pts,
        radius=0.00105,
        samples_per_segment=14,
        radial_segments=14,
        cap_ends=True,
    )


_SPRING_BUILDERS = {
    "wire_clip": _wire_clip_mesh,
    "leaf_spring": _leaf_spring_mesh,
    "torsion_spring": _torsion_spring_mesh,
}


# ---------------------------------------------------------------------------
# Slot B -- compound_link toggle bar (V-L1 helper).
# ---------------------------------------------------------------------------
def _compound_link_bar(thickness: float):
    bar_profile = [
        (-0.005, 0.006),
        (0.005, 0.006),
        (0.0058, 0.003),
        (0.0058, -0.002),
        (0.005, -0.005),
        (0.0058, -0.011),
        (0.005, -0.015),
        (-0.005, -0.015),
        (-0.0058, -0.011),
        (-0.005, -0.005),
        (-0.0058, -0.002),
        (-0.0058, 0.003),
    ]
    bar = _profile_solid(bar_profile, thickness, corner_radius=0.001)
    boss_top = (
        cq.Workplane("XY").circle(0.007).extrude(thickness).translate((0.0, 0.0, -thickness / 2.0))
    )
    boss_bottom = (
        cq.Workplane("XY")
        .circle(0.007)
        .extrude(thickness)
        .translate((0.0, -2.0 * PIVOT_OFFSET, -thickness / 2.0))
    )
    hole_extra = 0.003
    hole_top = (
        cq.Workplane("XY")
        .circle(0.0038)
        .extrude(thickness + hole_extra)
        .translate((0.0, 0.0, -(thickness + hole_extra) / 2.0))
    )
    hole_bottom = (
        cq.Workplane("XY")
        .circle(0.0038)
        .extrude(thickness + hole_extra)
        .translate((0.0, -2.0 * PIVOT_OFFSET, -(thickness + hole_extra) / 2.0))
    )
    return bar.union(boss_top).union(boss_bottom).cut(hole_top).cut(hole_bottom)


# ---------------------------------------------------------------------------
# Half-emit routine. Emits either the +Y half (s=+1, root) or the -Y half
# (s=-1, moving), with its own local translation for the compound_link
# branch. ``ty`` is added to all visual origins so compound_link's moving
# half can sit at world y=-PIVOT_OFFSET while its geometry is authored in the
# canonical pivot-at-origin frame.
# ---------------------------------------------------------------------------
def _emit_half(
    part,
    r: ResolvedConfig,
    s: int,
    mats: dict,
    *,
    ty: float = 0.0,
    is_root: bool = True,
) -> None:
    jaw_pts, edge_pts, edge_thickness = _JAW_BUILDERS[r.cutting_head]()
    grip_pts, inlay_pts = _HANDLE_BUILDERS[r.handle_form]()

    # Apply jaw / grip scale (mild, keeps clamped ranges).
    jaw_scaled = _scale_all(jaw_pts, 1.0, r.jaw_len_scale)
    edge_scaled = _scale_all(edge_pts, 1.0, r.jaw_len_scale)
    grip_scaled = _scale_all(grip_pts, r.grip_girth_scale, r.overall_len_scale)
    inlay_scaled = _scale_all(inlay_pts, r.grip_girth_scale, r.overall_len_scale)

    # Mirror for the -Y (moving) half.
    if s < 0:
        # We mirror the forged half by CQ (.mirror("YZ")) so its cross-section
        # remains valid; grip / inlay / edge polylines get flipped in x.
        grip_scaled = _mirror_x(grip_scaled)
        inlay_scaled = _mirror_x(inlay_scaled)
        edge_scaled = _mirror_x(edge_scaled)

    forged_z = -0.003 if s > 0 else 0.003
    thickness = 0.006

    forged_solid = _forged_half(TANG_PROFILE_BASE, jaw_scaled, thickness)
    if s < 0:
        forged_solid = forged_solid.mirror("YZ")

    tag = "root" if is_root else "moving"

    part.visual(
        mesh_from_cadquery(forged_solid, f"{tag}_forged_half", tolerance=0.0003),
        origin=Origin(xyz=(0.0, ty, forged_z)),
        material=mats["forged"],
        name="forged_steel", material_class_id=("metal.steel_bare" if r.palette_style in {"steel_red_blue", "chrome_natural", "polished_silver", "industrial_green"} else "metal.blackened_gunmetal"),
    )

    part.visual(
        mesh_from_cadquery(
            _profile_solid(grip_scaled, 0.016, corner_radius=0.0022),
            f"{tag}_red_grip",
            tolerance=0.0003,
        ),
        origin=Origin(xyz=(0.0, ty, forged_z)),
        material=mats["grip"],
        name="red_grip", material_class_id=("rubber.smooth_plain" if r.palette_style in {"steel_red_blue", "black_orange", "gunmetal_yellow", "industrial_green"} else "metal.blackened_gunmetal"),
    )

    part.visual(
        mesh_from_cadquery(
            _profile_solid(inlay_scaled, 0.0164, corner_radius=0.0014),
            f"{tag}_blue_inlay",
            tolerance=0.0003,
        ),
        origin=Origin(xyz=(0.0, ty, forged_z)),
        material=mats["inlay"],
        name="blue_inlay", material_class_id=("rubber.smooth_plain" if r.palette_style in {"steel_red_blue", "black_orange", "gunmetal_yellow", "polished_silver", "industrial_green"} else "metal.chrome_polished"),
    )

    part.visual(
        mesh_from_cadquery(
            _profile_solid(edge_scaled, edge_thickness, corner_radius=0.00025),
            f"{tag}_cutting_edge",
            tolerance=0.0002,
        ),
        origin=Origin(xyz=(0.0, ty, 0.0)),
        material=mats["cutting"],
        name="cutting_edge", material_class_id="metal.steel_bare",
    )


def _emit_pivot_hardware(part, r: ResolvedConfig, mats: dict, *, ty: float = 0.0) -> None:
    """Emits the rivet pin and washers on root_half.

    - ``fixed_rivet``: a rivet pin cylinder only.
    - ``offset_pivot``: rivet pin + front + rear pivot washers (real washer
      geometry that touches the moving forged half in the source pose).
    - ``compound_link``: rivet pin only (the compound bar carries the toggle).
    """
    # The pivot pin needs to physically touch the forged half so it does not
    # register as a disconnected island (the hub carries a 0.00425 m pivot
    # hole). Use a slightly oversized radius (0.0044) so the pin's shell
    # overlaps the surrounding hub material; captured-pin overlap is covered
    # by the broad allow_overlap between the two halves.
    part.visual(
        Cylinder(radius=0.0044, length=0.019),
        origin=Origin(xyz=(0.0, ty, 0.0005)),
        material=mats["polished"],
        name="pivot_pin", material_class_id=("metal.steel_bare" if r.palette_style in {"steel_red_blue", "chrome_natural", "polished_silver", "industrial_green"} else "metal.blackened_gunmetal"),
    )
    if r.leverage_mechanism == "offset_pivot":
        part.visual(
            Cylinder(radius=0.0075, length=0.0015),
            origin=Origin(xyz=(0.0, ty, -0.00675)),
            material=mats["polished"],
            name="pivot_washer_rear", material_class_id=("metal.steel_bare" if r.palette_style in {"steel_red_blue", "chrome_natural", "polished_silver", "industrial_green"} else "metal.blackened_gunmetal"),
        )
        part.visual(
            Cylinder(radius=0.0075, length=0.0015),
            origin=Origin(xyz=(0.0, ty, 0.00675)),
            material=mats["polished"],
            name="pivot_washer_front", material_class_id=("metal.steel_bare" if r.palette_style in {"steel_red_blue", "chrome_natural", "polished_silver", "industrial_green"} else "metal.blackened_gunmetal"),
        )


# ---------------------------------------------------------------------------
# Builders
# ---------------------------------------------------------------------------
def build_pilers_cutting_pliers(
    config: PilersCuttingPliersConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    palette = PALETTES[r.palette_style]
    mats = {
        key: model.material(f"pcp_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in palette.items()
    }

    is_compound = r.is_compound

    # ------------------------------------------------------------------
    # root_half (fixed forged half; +Y jaw side).
    # ------------------------------------------------------------------
    root_half = model.part("root_half")
    _emit_half(root_half, r, s=1, mats=mats, ty=0.0, is_root=True)
    _emit_pivot_hardware(root_half, r, mats, ty=0.0)

    if is_compound:
        # ------------------------------------------------------------------
        # compound_link (V-L1). Two pivot bosses stacked along -y.
        # ------------------------------------------------------------------
        compound_link = model.part("compound_link")
        compound_link.visual(
            mesh_from_cadquery(_compound_link_bar(0.0045), "compound_toggle_bar", tolerance=0.0003),
            origin=Origin(),
            material=mats["forged"],
            name="compound_bar", material_class_id=("metal.steel_bare" if r.palette_style in {"steel_red_blue", "chrome_natural", "polished_silver", "industrial_green"} else "metal.blackened_gunmetal"),
        )

        # moving_half sits with its origin at compound_link's lower boss so
        # the mimic joint chains naturally. In world coordinates the moving
        # half's geometry is +PIVOT_OFFSET in y so the two jaws still meet at
        # y ~= 0 in the source pose (V-L1 L318 pattern).
        moving_half = model.part("moving_half")
        _emit_half(moving_half, r, s=-1, mats=mats, ty=PIVOT_OFFSET, is_root=False)

        model.articulation(
            "plier_pivot",
            ArticulationType.REVOLUTE,
            parent=root_half,
            child=compound_link,
            origin=Origin(xyz=(0.0, PIVOT_OFFSET, 0.0)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(
                effort=300.0,
                velocity=2.0,
                lower=r.open_lower * 0.7,
                upper=r.open_angle * 0.7,
            ),
            meta={"positive_motion": "rotates the compound toggle bar"},
        )

        model.articulation(
            "compound_to_moving",
            ArticulationType.REVOLUTE,
            parent=compound_link,
            child=moving_half,
            origin=Origin(xyz=(0.0, -2.0 * PIVOT_OFFSET, 0.0)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(
                effort=260.0,
                velocity=2.0,
                lower=r.open_lower * 0.85,
                upper=r.open_angle * 0.7,
            ),
            mimic=Mimic(joint="plier_pivot", multiplier=0.85, offset=0.0),
            meta={"positive_motion": "drives the moving half through the compound toggle"},
        )

        # Clip pin lives on moving_half (with the PIVOT_OFFSET Y adjust).
        clip_pin_y = -0.086 + PIVOT_OFFSET
    else:
        # ------------------------------------------------------------------
        # fixed_rivet / offset_pivot: baseline 3-part chain, single REVOLUTE.
        # ------------------------------------------------------------------
        moving_half = model.part("moving_half")
        _emit_half(moving_half, r, s=-1, mats=mats, ty=0.0, is_root=False)

        model.articulation(
            "plier_pivot",
            ArticulationType.REVOLUTE,
            parent=root_half,
            child=moving_half,
            origin=Origin(),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(
                effort=260.0,
                velocity=2.0,
                lower=r.open_lower,
                upper=r.open_angle,
            ),
            meta={"positive_motion": "opens the right handle and separates the cutting jaws"},
        )
        clip_pin_y = -0.086

    # ------------------------------------------------------------------
    # clip_pin (moving_half inline visual) + spring_clip part + clip_swing.
    # ------------------------------------------------------------------
    moving_half.visual(
        Cylinder(radius=0.0023, length=0.005),
        origin=Origin(xyz=(0.030, clip_pin_y, 0.0125)),
        material=mats["polished"],
        name="clip_pin", material_class_id=("metal.steel_bare" if r.palette_style in {"steel_red_blue", "chrome_natural", "polished_silver", "industrial_green"} else "metal.blackened_gunmetal"),
    )

    spring_clip = model.part("spring_clip")
    spring_geom = _SPRING_BUILDERS[r.return_spring]()
    spring_clip.visual(
        mesh_from_geometry(spring_geom, "spring_clip_wire"),
        material=mats["polished"],
        name="spring_wire", material_class_id=("metal.steel_bare" if r.palette_style in {"steel_red_blue", "chrome_natural", "polished_silver", "industrial_green"} else "metal.blackened_gunmetal"),
    )

    model.articulation(
        "clip_swing",
        ArticulationType.REVOLUTE,
        parent=moving_half,
        child=spring_clip,
        origin=Origin(xyz=(0.030, clip_pin_y, 0.013)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=0.8, velocity=4.0, lower=-0.35, upper=0.60),
        meta={"positive_motion": "swings the visible wire clip away from the grip"},
    )

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_pilers_cutting_pliers(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_pilers_cutting_pliers(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def run_pilers_cutting_pliers_tests(
    object_model: ArticulatedObject,
    config: PilersCuttingPliersConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    root_half = object_model.get_part("root_half")
    moving_half = object_model.get_part("moving_half")
    spring_clip = object_model.get_part("spring_clip")
    plier_pivot = object_model.get_articulation("plier_pivot")
    clip_swing = object_model.get_articulation("clip_swing")

    # Broad captured-pin allowances (rivet shaft through the hub lap; the
    # clip pin captured through the spring wire). MatingContract omitted.
    ctx.allow_overlap(
        root_half,
        moving_half,
        reason=(
            "The rivet pin captured through the two forged half-lap hubs is the "
            "cutting pliers's central captured-pin joint."
        ),
    )
    ctx.allow_overlap(
        moving_half,
        spring_clip,
        elem_a="clip_pin",
        elem_b="spring_wire",
        reason=("The visible spring is intentionally captured around its handle pin."),
    )

    if r.is_compound:
        compound_link = object_model.get_part("compound_link")
        ctx.allow_overlap(
            root_half,
            compound_link,
            reason=(
                "The compound toggle bar's upper boss is captured on the root "
                "half's rivet (captured-pin geometry)."
            ),
        )
        ctx.allow_overlap(
            compound_link,
            moving_half,
            reason=(
                "The compound toggle bar's lower boss captures the moving half's "
                "hub (captured-pin geometry)."
            ),
        )
        # 4-part / 3-joint chain when compound_link is chosen.
        ctx.check(
            "compound_link topology has an extra part and joint",
            len(object_model.parts) == 4 and len(object_model.articulations) == 3,
            details=(f"parts={len(object_model.parts)}, joints={len(object_model.articulations)}"),
        )
    else:
        ctx.check(
            "baseline topology is 3-part / 2-joint",
            len(object_model.parts) == 3 and len(object_model.articulations) == 2,
            details=(f"parts={len(object_model.parts)}, joints={len(object_model.articulations)}"),
        )

    # Slot A geometry claim.
    root_ce = ctx.part_element_world_aabb(root_half, elem="cutting_edge")
    ctx.check(
        "cutting_edge visual is present on root_half",
        root_ce is not None,
    )
    if root_ce is not None:
        ce_width = root_ce[1][0] - root_ce[0][0]
        if r.cutting_head == "end_cutter":
            ctx.check(
                "end_cutter has a wide transverse cutting edge band",
                ce_width > 0.014,
                details=f"cutting_edge x-width={ce_width:.4f}",
            )
        elif r.cutting_head == "flush_cutter":
            ctx.check(
                "flush_cutter cutting edge stays narrow",
                ce_width < 0.010,
                details=f"cutting_edge x-width={ce_width:.4f}",
            )

    # Slot D geometry claim: long_handle really extends the grip.
    grip_aabb = ctx.part_element_world_aabb(root_half, elem="red_grip")
    if grip_aabb is not None:
        grip_min_y = grip_aabb[0][1]
        if r.handle_form == "long_handle":
            # Threshold accounts for overall_len_scale down to 0.90:
            # baseline min_y=-0.125 * 0.90 = -0.1125, so -0.112 is the floor.
            ctx.check(
                "long_handle grip reaches further along -y",
                grip_min_y < -0.112,
                details=f"grip min_y={grip_min_y:.4f}",
            )

    # Central pivot joint sanity (axis + range).
    lm = plier_pivot.motion_limits
    ctx.check(
        "plier_pivot is a bounded REVOLUTE about +Z",
        plier_pivot.articulation_type == ArticulationType.REVOLUTE
        and lm is not None
        and lm.upper > 0.0
        and lm.lower < 0.0,
        details=f"limits={lm}",
    )
    ctx.check(
        "clip_swing is a bounded REVOLUTE about +Z",
        clip_swing.articulation_type == ArticulationType.REVOLUTE
        and clip_swing.motion_limits is not None,
        details=f"limits={clip_swing.motion_limits}",
    )

    # ---- Kinematics: opening pose moves cutting_edge apart + grip apart. ----
    rest_edge = ctx.part_element_world_aabb(moving_half, elem="cutting_edge")
    rest_grip = ctx.part_element_world_aabb(moving_half, elem="red_grip")
    with ctx.pose({plier_pivot: lm.upper}):
        open_edge = ctx.part_element_world_aabb(moving_half, elem="cutting_edge")
        open_grip = ctx.part_element_world_aabb(moving_half, elem="red_grip")
    ctx.check(
        "positive plier_pivot separates the cutting edges",
        rest_edge is not None
        and open_edge is not None
        and open_edge[0][0] < rest_edge[0][0] - 0.005,
        details=f"rest_edge={rest_edge}, open_edge={open_edge}",
    )
    ctx.check(
        "positive plier_pivot opens the handles",
        rest_grip is not None
        and open_grip is not None
        and open_grip[1][0] > rest_grip[1][0] + 0.005,
        details=f"rest_grip={rest_grip}, open_grip={open_grip}",
    )

    # clip_swing kinematics.
    rest_clip = ctx.part_world_aabb(spring_clip)
    with ctx.pose({clip_swing: 0.35}):
        swung = ctx.part_world_aabb(spring_clip)
    ctx.check(
        "clip_swing swings the return spring visibly",
        rest_clip is not None
        and swung is not None
        and abs(swung[1][0] - rest_clip[1][0]) + abs(swung[0][1] - rest_clip[0][1]) > 0.001,
        details=f"rest={rest_clip}, swung={swung}",
    )

    # Slot choices metadata reflects the same choices.
    ctx.check(
        "slot_choices metadata is emitted",
        object_model.meta.get("slot_choices") == slot_choices_for_config(r),
        details=f"meta slot_choices={object_model.meta.get('slot_choices')}",
    )

    return ctx.report()


__all__ = [
    "PilersCuttingPliersConfig",
    "ResolvedConfig",
    "config_from_seed",
    "resolve_config",
    "with_overrides",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "build_pilers_cutting_pliers",
    "build_seeded_pilers_cutting_pliers",
    "run_pilers_cutting_pliers_tests",
    "__modular__",
]
