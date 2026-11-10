# SPDX-License-Identifier: Apache-2.0

"""Fencing-pliers modular template (0611 / pilers_fencing_pliers).

Sourced from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/pilers_fencing_pliers.md``
and the ``picture/0611/Pilers_fencing_pliers`` 5-star pool (9 forked variants
plus the origin-anchor baseline captured in
``rec_0611_pilers_fencing_pliers_var_return_captured_spring``).

Structure (pattern ``mixed``):

* baseline 3-part / 2-joint chain: ``pivot`` (root) + ``hammer_handle`` +
  ``claw_handle``. ``pivot_to_hammer_half`` REVOLUTE (pivot -> hammer, axis +Z)
  and ``pivot_to_claw_half`` REVOLUTE (pivot -> claw, axis +Z) rotate each
  forged half independently around the central pin.
* ``leverage_mechanism = compound_link`` adds ``hammer_link`` + ``claw_link``
  toggle bars pinned on the handles' secondary pivots via two extra REVOLUTE
  joints, yielding a 5-part / 4-joint chain.

Slots:

* ``hammer_claw_form`` (4): default_asymmetric (baseline) / round_hammer_face /
  deep_staple_claw / offset_claw. Swaps ``hammer_head`` + ``striking_face`` +
  ``claw_head`` planar polylines.
* ``jaw_cutter`` (3): jaw_with_cutter (baseline) / broad_serrated_jaw
  (drops both cutter shims) / twin_side_cutters (drops striking_face and
  makes both halves symmetric).
* ``leverage_mechanism`` (2): fixed_rivet (baseline) / compound_link.
* ``handle_form`` (3): straight_dipped (baseline) / long_fencing_handle /
  flared_comfort_grip. Swaps grip ribbon centerlines and widths.
* ``return_spring`` (2): captured_spring (baseline, adds a spiral wire
  visual on the pivot) / no_spring.

``palette_style`` (6): material rgba axis; does not enter slot_choices and
does not change topology.

The pivot pin is captured through the two forged half hubs, so both handle
joints omit ``MatingContract`` and rely on broad ``allow_overlap`` between
the pivot and each handle.
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
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
)

__modular__ = True

# ---------------------------------------------------------------------------
# Enum axes
# ---------------------------------------------------------------------------
HammerClawForm = Literal[
    "default_asymmetric", "round_hammer_face", "deep_staple_claw", "offset_claw"
]
JawCutter = Literal["jaw_with_cutter", "broad_serrated_jaw", "twin_side_cutters"]
LeverageMechanism = Literal["fixed_rivet", "compound_link"]
HandleForm = Literal["straight_dipped", "long_fencing_handle", "flared_comfort_grip"]
ReturnSpring = Literal["captured_spring", "no_spring"]
PaletteStyle = Literal[
    "steel_red_black",
    "black_orange",
    "chrome_natural",
    "gunmetal_yellow",
    "polished_silver",
    "industrial_green",
]

HAMMER_CLAW_FORMS: tuple[HammerClawForm, ...] = (
    "default_asymmetric",
    "round_hammer_face",
    "deep_staple_claw",
    "offset_claw",
)
JAW_CUTTERS: tuple[JawCutter, ...] = (
    "jaw_with_cutter",
    "broad_serrated_jaw",
    "twin_side_cutters",
)
LEVERAGE_MECHANISMS: tuple[LeverageMechanism, ...] = ("fixed_rivet", "compound_link")
HANDLE_FORMS: tuple[HandleForm, ...] = (
    "straight_dipped",
    "long_fencing_handle",
    "flared_comfort_grip",
)
RETURN_SPRINGS: tuple[ReturnSpring, ...] = ("captured_spring", "no_spring")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "steel_red_black",
    "black_orange",
    "chrome_natural",
    "gunmetal_yellow",
    "polished_silver",
    "industrial_green",
)

# ---------------------------------------------------------------------------
# Palettes -- 5 material keys used by every ``.visual(material=mats[...])``.
# ``forged`` covers the main forging; ``polished`` covers the striking face,
# pivot cap and pin heads; ``pivot`` covers the pivot back; ``hardened``
# covers jaw + cutter inserts; ``grip`` covers the red rubber grip sleeve;
# ``rubber`` covers the darker transition sleeve. ``spring`` covers the
# captured return spring visual.
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "steel_red_black": {
        "forged": (0.61, 0.63, 0.64, 1.0),
        "polished": (0.78, 0.80, 0.80, 1.0),
        "pivot": (0.48, 0.50, 0.51, 1.0),
        "hardened": (0.20, 0.22, 0.23, 1.0),
        "grip": (0.91, 0.015, 0.035, 1.0),
        "rubber": (0.025, 0.027, 0.030, 1.0),
        "spring": (0.30, 0.32, 0.33, 1.0),
    },
    "black_orange": {
        "forged": (0.18, 0.19, 0.20, 1.0),
        "polished": (0.55, 0.56, 0.58, 1.0),
        "pivot": (0.30, 0.31, 0.33, 1.0),
        "hardened": (0.10, 0.11, 0.12, 1.0),
        "grip": (0.95, 0.42, 0.05, 1.0),
        "rubber": (0.06, 0.06, 0.07, 1.0),
        "spring": (0.28, 0.30, 0.32, 1.0),
    },
    "chrome_natural": {
        "forged": (0.82, 0.84, 0.87, 1.0),
        "polished": (0.90, 0.91, 0.93, 1.0),
        "pivot": (0.70, 0.72, 0.75, 1.0),
        "hardened": (0.35, 0.37, 0.40, 1.0),
        "grip": (0.30, 0.30, 0.32, 1.0),
        "rubber": (0.16, 0.16, 0.18, 1.0),
        "spring": (0.55, 0.55, 0.58, 1.0),
    },
    "gunmetal_yellow": {
        "forged": (0.42, 0.44, 0.47, 1.0),
        "polished": (0.60, 0.62, 0.65, 1.0),
        "pivot": (0.34, 0.36, 0.39, 1.0),
        "hardened": (0.20, 0.20, 0.22, 1.0),
        "grip": (0.93, 0.78, 0.10, 1.0),
        "rubber": (0.12, 0.12, 0.14, 1.0),
        "spring": (0.34, 0.34, 0.36, 1.0),
    },
    "polished_silver": {
        "forged": (0.78, 0.80, 0.82, 1.0),
        "polished": (0.92, 0.93, 0.95, 1.0),
        "pivot": (0.62, 0.64, 0.66, 1.0),
        "hardened": (0.30, 0.32, 0.34, 1.0),
        "grip": (0.20, 0.22, 0.25, 1.0),
        "rubber": (0.10, 0.11, 0.12, 1.0),
        "spring": (0.50, 0.50, 0.52, 1.0),
    },
    "industrial_green": {
        "forged": (0.55, 0.57, 0.59, 1.0),
        "polished": (0.80, 0.82, 0.84, 1.0),
        "pivot": (0.40, 0.42, 0.44, 1.0),
        "hardened": (0.18, 0.20, 0.22, 1.0),
        "grip": (0.10, 0.42, 0.20, 1.0),
        "rubber": (0.06, 0.10, 0.08, 1.0),
        "spring": (0.30, 0.30, 0.32, 1.0),
    },
}


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class PilersFencingPliersConfig:
    hammer_claw_form: HammerClawForm | None = None
    jaw_cutter: JawCutter | None = None
    leverage_mechanism: LeverageMechanism | None = None
    handle_form: HandleForm | None = None
    return_spring: ReturnSpring | None = None
    palette_style: PaletteStyle = "steel_red_black"
    overall_len_scale: float = 1.0
    head_scale: float = 1.0
    grip_girth_scale: float = 1.0
    open_angle_scale: float = 1.0
    name: str = "pilers_fencing_pliers"


@dataclass(frozen=True)
class ResolvedConfig:
    hammer_claw_form: HammerClawForm
    jaw_cutter: JawCutter
    leverage_mechanism: LeverageMechanism
    handle_form: HandleForm
    return_spring: ReturnSpring
    palette_style: PaletteStyle
    overall_len_scale: float
    head_scale: float
    grip_girth_scale: float
    hammer_upper: float
    hammer_lower: float
    claw_upper: float
    claw_lower: float
    name: str

    @property
    def is_compound(self) -> bool:
        return self.leverage_mechanism == "compound_link"


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


def config_from_seed(seed: int) -> PilersFencingPliersConfig:
    rng = random.Random(seed)
    hc = rng.choices(HAMMER_CLAW_FORMS, weights=[5, 3, 3, 3], k=1)[0]
    jc = rng.choices(JAW_CUTTERS, weights=[5, 3, 3], k=1)[0]
    lev = rng.choices(LEVERAGE_MECHANISMS, weights=[5, 2], k=1)[0]
    hand = rng.choices(HANDLE_FORMS, weights=[5, 3, 3], k=1)[0]
    ret = rng.choices(RETURN_SPRINGS, weights=[5, 2], k=1)[0]
    return PilersFencingPliersConfig(
        hammer_claw_form=hc,
        jaw_cutter=jc,
        leverage_mechanism=lev,
        handle_form=hand,
        return_spring=ret,
        palette_style=rng.choice(PALETTE_STYLES),
        overall_len_scale=round(rng.uniform(0.90, 1.15), 4),
        head_scale=round(rng.uniform(0.90, 1.10), 4),
        grip_girth_scale=round(rng.uniform(0.90, 1.10), 4),
        open_angle_scale=round(rng.uniform(0.80, 1.20), 4),
        name=f"seeded_pilers_fencing_pliers_{seed}",
    )


def resolve_config(config: PilersFencingPliersConfig | None = None) -> ResolvedConfig:
    cfg = config or PilersFencingPliersConfig()
    hc = _pick(cfg.hammer_claw_form, HAMMER_CLAW_FORMS)
    jc = _pick(cfg.jaw_cutter, JAW_CUTTERS)
    lev = _pick(cfg.leverage_mechanism, LEVERAGE_MECHANISMS)
    hand = _pick(cfg.handle_form, HANDLE_FORMS)
    ret = _pick(cfg.return_spring, RETURN_SPRINGS)
    palette = _pick(cfg.palette_style, PALETTE_STYLES)

    overall = _clamp(cfg.overall_len_scale, 0.90, 1.15)
    head = _clamp(cfg.head_scale, 0.90, 1.10)
    grip_girth = _clamp(cfg.grip_girth_scale, 0.90, 1.10)
    open_scale = _clamp(cfg.open_angle_scale, 0.80, 1.20)

    # Baseline pivot travel from V-R1: hammer lower=-0.24 upper=0.12,
    # claw lower=-0.12 upper=0.24. The "close" side of each joint is capped
    # tightly so the two grips never physically cross at simultaneous close
    # poses (sweep tests all axis combinations).
    hammer_upper = _clamp(0.06 * open_scale, 0.03, 0.09)
    hammer_lower = _clamp(-0.24 * open_scale, -0.32, -0.14)
    claw_upper = _clamp(0.24 * open_scale, 0.14, 0.32)
    claw_lower = _clamp(-0.06 * open_scale, -0.09, -0.03)

    return ResolvedConfig(
        hammer_claw_form=hc,
        jaw_cutter=jc,
        leverage_mechanism=lev,
        handle_form=hand,
        return_spring=ret,
        palette_style=palette,
        overall_len_scale=overall,
        head_scale=head,
        grip_girth_scale=grip_girth,
        hammer_upper=hammer_upper,
        hammer_lower=hammer_lower,
        claw_upper=claw_upper,
        claw_lower=claw_lower,
        name=cfg.name or "pilers_fencing_pliers",
    )


def with_overrides(
    config: PilersFencingPliersConfig, **kwargs: object
) -> PilersFencingPliersConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: PilersFencingPliersConfig | ResolvedConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedConfig) else resolve_config(config)
    return (
        ("hammer_claw_form", r.hammer_claw_form),
        ("jaw_cutter", r.jaw_cutter),
        ("leverage_mechanism", r.leverage_mechanism),
        ("handle_form", r.handle_form),
        ("return_spring", r.return_spring),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Geometry helpers (dimensions in millimetres, extruded via ``unit_scale``).
# Ported from V-R1 origin_anchor.
# ---------------------------------------------------------------------------
def _profile(points: list[tuple[float, float]], thickness: float, z0: float) -> cq.Workplane:
    return cq.Workplane("XY").polyline(points).close().extrude(thickness).translate((0.0, 0.0, z0))


def _ribbon(
    centerline: list[tuple[float, float]],
    widths: list[float],
    thickness: float,
    z0: float,
) -> cq.Workplane:
    left: list[tuple[float, float]] = []
    right: list[tuple[float, float]] = []

    for index, ((x, y), width) in enumerate(zip(centerline, widths)):
        if index == 0:
            tx = centerline[1][0] - x
            ty = centerline[1][1] - y
        elif index == len(centerline) - 1:
            tx = x - centerline[index - 1][0]
            ty = y - centerline[index - 1][1]
        else:
            tx = centerline[index + 1][0] - centerline[index - 1][0]
            ty = centerline[index + 1][1] - centerline[index - 1][1]

        length = math.hypot(tx, ty) or 1.0
        nx, ny = -ty / length, tx / length
        half = width * 0.5
        left.append((x + nx * half, y + ny * half))
        right.append((x - nx * half, y - ny * half))

    return _profile(left + list(reversed(right)), thickness, z0)


def _soften_vertical_edges(shape: cq.Workplane, radius: float) -> cq.Workplane:
    try:
        return shape.edges("|Z").fillet(radius)
    except Exception:
        return shape


def _mirror_x(points: list[tuple[float, float]]) -> list[tuple[float, float]]:
    return [(-x, y) for x, y in points]


def _scale_widths(widths: list[float], s: float) -> list[float]:
    return [w * s for w in widths]


def _scale_xy(points: list[tuple[float, float]], s: float) -> list[tuple[float, float]]:
    return [(x * s, y * s) for x, y in points]


# ---------------------------------------------------------------------------
# Captured return spring helper (V-R1 L69-86).
# ---------------------------------------------------------------------------
def _captured_return_spring() -> cq.Workplane:
    centerline: list[tuple[float, float]] = [(-10.0, -36.0), (-9.0, -22.0)]
    start_angle = math.radians(-130.0)
    end_angle = math.radians(310.0)
    samples = 40
    for index in range(samples):
        fraction = index / (samples - 1)
        angle = start_angle + (end_angle - start_angle) * fraction
        radius = 11.7 + 4.8 * fraction
        centerline.append((radius * math.cos(angle), radius * math.sin(angle)))
    centerline.extend([(9.0, -22.0), (10.0, -36.0)])
    return _soften_vertical_edges(
        _ribbon(centerline, [1.9] * len(centerline), 1.1, -0.2),
        0.45,
    )


# ---------------------------------------------------------------------------
# Compound-link toggle bar helper (V-L1 L91-176 style, simplified).
# Length/width in mm; produces a thin bar with two circular bosses along -Y.
# ---------------------------------------------------------------------------
def _compound_link_bar(
    length: float, width: float, thickness: float, boss_radius: float, z0: float
) -> cq.Workplane:
    bar = (
        cq.Workplane("XY")
        .box(width, length, thickness)
        .translate((0.0, -length / 2.0, z0 + thickness / 2.0))
    )
    boss_top = cq.Workplane("XY").circle(boss_radius).extrude(thickness).translate((0.0, 0.0, z0))
    boss_bottom = (
        cq.Workplane("XY").circle(boss_radius).extrude(thickness).translate((0.0, -length, z0))
    )
    return bar.union(boss_top).union(boss_bottom)


# ---------------------------------------------------------------------------
# Slot A -- hammer head + claw head + striking face. All coords in mm.
# Returns (hammer_head_points, claw_head_points, striking_solid_or_None,
# extra_hammer_cuts) where striking_solid=None means emit no striking face.
# For round_hammer_face we build a disk directly; other variants build the
# planar polylines used by ``_profile``.
# ---------------------------------------------------------------------------
_HAMMER_HEAD_BASE: list[tuple[float, float]] = [
    (-9.0, -4.0),
    (-13.0, 18.0),
    (-11.0, 39.0),
    (-5.0, 58.0),
    (4.0, 78.0),
    (13.0, 91.0),
    (29.0, 98.0),
    (50.0, 98.0),
    (68.0, 92.0),
    (76.0, 80.0),
    (77.0, 58.0),
    (72.0, 44.0),
    (56.0, 39.0),
    (42.0, 35.0),
    (29.0, 25.0),
    (20.0, 9.0),
    (10.0, -3.0),
]

_HAMMER_HEAD_ROUND: list[tuple[float, float]] = [
    (-9.0, -4.0),
    (-13.0, 18.0),
    (-11.0, 39.0),
    (-5.0, 58.0),
    (4.0, 78.0),
    (13.0, 91.0),
    (29.0, 98.0),
    (44.0, 101.0),
    (58.0, 97.0),
    (69.0, 89.0),
    (76.0, 78.0),
    (79.0, 66.0),
    (76.0, 54.0),
    (69.0, 45.0),
    (58.0, 40.0),
    (44.0, 36.0),
    (29.0, 25.0),
    (20.0, 9.0),
    (10.0, -3.0),
]

_CLAW_HEAD_BASE: list[tuple[float, float]] = [
    (-10.0, -3.0),
    (-23.0, 10.0),
    (-33.0, 22.0),
    (-40.0, 34.0),
    (-47.0, 44.0),
    (-58.0, 50.0),
    (-68.0, 52.0),
    (-75.0, 57.0),
    (-71.0, 63.0),
    (-61.0, 68.0),
    (-48.0, 67.0),
    (-35.0, 62.0),
    (-25.0, 54.0),
    (-16.0, 45.0),
    (-7.0, 40.0),
    (3.0, 35.0),
    (12.0, 25.0),
    (14.0, 10.0),
    (9.0, -4.0),
]

_CLAW_HEAD_DEEP: list[tuple[float, float]] = [
    (-10.0, -3.0),
    (-24.0, 8.0),
    (-36.0, 18.0),
    (-48.0, 28.0),
    (-60.0, 36.0),
    (-72.0, 42.0),
    (-82.0, 46.0),
    (-88.0, 48.0),
    (-86.0, 56.0),
    (-80.0, 62.0),
    (-68.0, 64.0),
    (-54.0, 64.0),
    (-40.0, 60.0),
    (-26.0, 52.0),
    (-14.0, 42.0),
    (-4.0, 34.0),
    (6.0, 28.0),
    (12.0, 20.0),
    (14.0, 10.0),
    (9.0, -4.0),
]

_CLAW_HEAD_OFFSET: list[tuple[float, float]] = [
    (-10.0, -8.0),
    (-24.0, 4.0),
    (-36.0, 16.0),
    (-46.0, 28.0),
    (-56.0, 38.0),
    (-65.0, 46.0),
    (-73.0, 50.0),
    (-72.0, 58.0),
    (-64.0, 62.0),
    (-52.0, 61.0),
    (-40.0, 56.0),
    (-28.0, 48.0),
    (-16.0, 40.0),
    (-6.0, 34.0),
    (4.0, 28.0),
    (12.0, 18.0),
    (14.0, 6.0),
    (9.0, -8.0),
]

_TWIN_HEAD: list[tuple[float, float]] = [
    (-10.0, -3.0),
    (-12.0, 8.0),
    (-11.0, 22.0),
    (-9.0, 36.0),
    (-6.0, 48.0),
    (-3.0, 55.0),
    (0.0, 57.0),
    (2.0, 55.0),
    (3.0, 46.0),
    (3.0, 34.0),
    (2.0, 20.0),
    (1.0, 8.0),
    (0.0, -3.0),
]


def _hammer_head_points(r: ResolvedConfig) -> list[tuple[float, float]]:
    if r.jaw_cutter == "twin_side_cutters":
        return _TWIN_HEAD
    if r.hammer_claw_form == "round_hammer_face":
        return _HAMMER_HEAD_ROUND
    return _HAMMER_HEAD_BASE


def _claw_head_points(r: ResolvedConfig) -> list[tuple[float, float]]:
    if r.jaw_cutter == "twin_side_cutters":
        # Mirror the symmetric twin head so both halves are symmetric taper.
        return _mirror_x(_TWIN_HEAD)
    if r.hammer_claw_form == "deep_staple_claw":
        return _CLAW_HEAD_DEEP
    if r.hammer_claw_form == "offset_claw":
        return _CLAW_HEAD_OFFSET
    return _CLAW_HEAD_BASE


# ---------------------------------------------------------------------------
# Handle centerlines + widths (mm). All authored in the left-half frame; the
# right (claw) half mirrors x. thickness_mm returns (grip_thickness,
# transition_thickness).
# ---------------------------------------------------------------------------
def _handle_geometry(
    r: ResolvedConfig,
) -> tuple[
    list[tuple[float, float]],  # hammer_centerline (forging spine)
    list[float],  # hammer_widths
    list[tuple[float, float]],  # transition_centerline
    list[float],  # transition_widths
    float,  # transition_thickness
    list[tuple[float, float]],  # grip_centerline
    list[float],  # grip_widths
    float,  # grip_thickness
]:
    hammer_forging_centerline = [
        (-5.0, -3.0),
        (-9.0, -30.0),
        (-15.0, -58.0),
        (-24.0, -88.0),
        (-31.0, -120.0),
        (-34.0, -155.0),
        (-35.0, -190.0),
        (-32.0, -220.0),
    ]
    hammer_forging_widths = [12.0, 11.0, 10.0, 9.5, 9.0, 8.5, 8.0, 7.5]

    transition_centerline = [
        (-12.0, -43.0),
        (-15.0, -57.0),
        (-19.0, -72.0),
        (-22.0, -82.0),
    ]

    if r.handle_form == "flared_comfort_grip":
        transition_widths = [15.0, 17.0, 20.0, 23.0]
        transition_thickness = 9.5
        grip_centerline = [
            (-19.0, -69.0),
            (-25.0, -88.0),
            (-31.0, -120.0),
            (-34.0, -155.0),
            (-35.0, -190.0),
            (-32.0, -220.0),
        ]
        grip_widths = [19.0, 22.0, 25.0, 27.0, 28.0, 26.0]
        grip_thickness = 13.0
    elif r.handle_form == "long_fencing_handle":
        transition_widths = [14.0, 15.0, 16.0, 17.0]
        transition_thickness = 9.0
        grip_centerline = [
            (-19.0, -69.0),
            (-25.0, -88.0),
            (-31.0, -120.0),
            (-34.0, -155.0),
            (-35.0, -190.0),
            (-34.0, -225.0),
            (-31.0, -260.0),
            (-28.0, -290.0),
        ]
        grip_widths = [18.0, 19.0, 19.0, 18.5, 18.0, 17.5, 16.5, 15.0]
        grip_thickness = 11.0
    else:
        transition_widths = [14.0, 15.0, 16.0, 17.0]
        transition_thickness = 9.0
        grip_centerline = [
            (-19.0, -69.0),
            (-25.0, -88.0),
            (-31.0, -120.0),
            (-34.0, -155.0),
            (-35.0, -190.0),
            (-32.0, -220.0),
        ]
        grip_widths = [18.0, 19.0, 19.0, 18.5, 18.0, 16.0]
        grip_thickness = 11.0

    return (
        hammer_forging_centerline,
        hammer_forging_widths,
        transition_centerline,
        transition_widths,
        transition_thickness,
        grip_centerline,
        grip_widths,
        grip_thickness,
    )


# ---------------------------------------------------------------------------
# Slot B jaw / cutter helpers.
# ---------------------------------------------------------------------------
_HAMMER_JAW_BASE: list[tuple[float, float]] = [
    (-17.0, 17.0),
    (-8.0, 21.0),
    (-3.0, 13.0),
    (-8.0, 6.0),
    (-15.0, 8.0),
]
_HAMMER_CUTTER_BASE: list[tuple[float, float]] = [
    (-13.0, 3.0),
    (-6.0, 9.0),
    (-2.0, -1.0),
    (-8.0, -8.0),
]
_CLAW_JAW_BASE: list[tuple[float, float]] = [
    (6.0, 12.0),
    (14.0, 21.0),
    (20.0, 17.0),
    (17.0, 8.0),
    (10.0, 6.0),
]
_CLAW_CUTTER_BASE: list[tuple[float, float]] = [
    (3.0, -1.0),
    (7.0, 9.0),
    (14.0, 3.0),
    (9.0, -8.0),
]

_HAMMER_JAW_SERRATED: list[tuple[float, float]] = [
    (-21.0, 21.0),
    (-6.0, 24.0),
    (-1.0, 16.0),
    (-1.0, 2.0),
    (-8.0, -4.0),
    (-19.0, -2.0),
    (-23.0, 8.0),
]
_CLAW_JAW_SERRATED: list[tuple[float, float]] = [
    (21.0, 21.0),
    (6.0, 24.0),
    (1.0, 16.0),
    (1.0, 2.0),
    (8.0, -4.0),
    (19.0, -2.0),
    (23.0, 8.0),
]

_TWIN_JAW: list[tuple[float, float]] = [
    (-1.0, 10.0),
    (0.0, 22.0),
    (1.0, 36.0),
    (1.5, 48.0),
    (0.5, 54.0),
    (-1.5, 53.0),
    (-2.5, 46.0),
    (-2.5, 34.0),
    (-2.0, 20.0),
    (-2.0, 8.0),
]
_TWIN_CUTTER: list[tuple[float, float]] = [
    (0.0, 14.0),
    (1.0, 26.0),
    (1.5, 40.0),
    (1.0, 50.0),
    (-0.5, 52.0),
    (-1.5, 48.0),
    (-1.5, 38.0),
    (-1.0, 24.0),
    (-1.0, 12.0),
]


# ---------------------------------------------------------------------------
# Emit routines
# ---------------------------------------------------------------------------
def _emit_hammer_half(part, r: ResolvedConfig, mats: dict) -> None:
    (
        forging_cl,
        forging_w,
        trans_cl,
        trans_w,
        trans_th,
        grip_cl,
        grip_w,
        grip_th,
    ) = _handle_geometry(r)

    # Handle spine ribbon (mm, extruded 4 mm; ``unit_scale`` will scale to m).
    hammer_core = _ribbon(forging_cl, forging_w, 4.0, -4.0)

    # Head polyline (scale x/y by r.head_scale).
    head_pts_raw = _hammer_head_points(r)
    head_pts = _scale_xy(head_pts_raw, r.head_scale)
    hammer_head = _profile(head_pts, 4.0, -4.0)

    hammer_forging = hammer_core.union(hammer_head).union(
        cq.Workplane("XY").circle(17.0).extrude(4.0).translate((0.0, 0.0, -4.0))
    )

    if r.jaw_cutter != "twin_side_cutters":
        # Only the asymmetric hammer heads carry wire_slot / keyhole cuts.
        wire_slot = _profile(
            [(-4.5, 83.0), (0.0, 94.0), (4.5, 83.0), (2.2, 75.0), (-2.2, 75.0)],
            12.0,
            -7.0,
        )
        keyhole = (
            cq.Workplane("XY")
            .center(0.0, 64.0)
            .circle(3.6)
            .extrude(12.0)
            .translate((0.0, 0.0, -7.0))
            .union(cq.Workplane("XY").rect(3.2, 13.0).extrude(12.0).translate((0.0, 58.0, -7.0)))
        )
        try:
            hammer_forging = hammer_forging.cut(wire_slot).cut(keyhole)
        except Exception:
            pass

    hammer_forging = _soften_vertical_edges(hammer_forging.clean(), 1.5)
    part.visual(
        mesh_from_cadquery(
            hammer_forging,
            "hammer_forging",
            tolerance=0.20,
            angular_tolerance=0.14,
            unit_scale=0.001,
        ),
        material=mats["forged"],
        name="hammer_forging", material_class_id="metal.steel_bare",
    )

    # Striking face -- only for baseline + round_face; twin_side_cutters skips.
    if r.jaw_cutter != "twin_side_cutters":
        if r.hammer_claw_form == "round_hammer_face":
            strike = (
                cq.Workplane("XY")
                .center(72.0 * r.head_scale, 67.0 * r.head_scale)
                .circle(14.5 * r.head_scale)
                .extrude(5.0)
                .translate((0.0, 0.0, -4.5))
            )
        else:
            strike_pts = _scale_xy(
                [
                    (69.5, 45.0),
                    (75.5, 49.0),
                    (77.0, 58.0),
                    (76.0, 80.0),
                    (70.0, 91.0),
                    (67.5, 84.0),
                    (69.0, 58.0),
                ],
                r.head_scale,
            )
            strike = _profile(strike_pts, 4.4, -4.2)
        strike = _soften_vertical_edges(strike, 0.8)
        part.visual(
            mesh_from_cadquery(
                strike,
                "striking_face",
                tolerance=0.14,
                angular_tolerance=0.12,
                unit_scale=0.001,
            ),
            material=mats["polished"],
            name="striking_face", material_class_id="metal.chrome_polished",
        )

    # Slot B: jaw + cutter emission.
    if r.jaw_cutter == "twin_side_cutters":
        jaw = _profile(_TWIN_JAW, 1.0, -0.7)
        cutter = _profile(_TWIN_CUTTER, 0.8, -0.5)
        part.visual(
            mesh_from_cadquery(jaw, "hammer_jaw", tolerance=0.12, unit_scale=0.001),
            material=mats["hardened"],
            name="hammer_jaw", material_class_id="metal.blackened_gunmetal",
        )
        part.visual(
            mesh_from_cadquery(cutter, "hammer_cutter", tolerance=0.12, unit_scale=0.001),
            material=mats["hardened"],
            name="hammer_cutter", material_class_id="metal.blackened_gunmetal",
        )
    elif r.jaw_cutter == "broad_serrated_jaw":
        jaw = _profile(_HAMMER_JAW_SERRATED, 2.5, -1.0)
        part.visual(
            mesh_from_cadquery(jaw, "hammer_jaw", tolerance=0.12, unit_scale=0.001),
            material=mats["hardened"],
            name="hammer_jaw", material_class_id="metal.blackened_gunmetal",
        )
    else:
        # jaw_with_cutter (baseline)
        jaw = _profile(_HAMMER_JAW_BASE, 1.0, -0.7)
        cutter = _profile(_HAMMER_CUTTER_BASE, 1.0, -0.7)
        part.visual(
            mesh_from_cadquery(jaw, "hammer_jaw", tolerance=0.12, unit_scale=0.001),
            material=mats["hardened"],
            name="hammer_jaw", material_class_id="metal.blackened_gunmetal",
        )
        part.visual(
            mesh_from_cadquery(cutter, "hammer_cutter", tolerance=0.12, unit_scale=0.001),
            material=mats["hardened"],
            name="hammer_cutter", material_class_id="metal.blackened_gunmetal",
        )

    # Transition + grip -- both handle halves get the same silhouette pattern.
    trans_widths = _scale_widths(trans_w, r.grip_girth_scale)
    grip_widths = _scale_widths(grip_w, r.grip_girth_scale)

    # Overall length scale extends grip centerline y-range slightly.
    def _stretch_y(pts, s):
        return [(x, y * s) for x, y in pts]

    grip_cl_scaled = _stretch_y(grip_cl, r.overall_len_scale)

    transition = _soften_vertical_edges(_ribbon(trans_cl, trans_widths, trans_th, -6.5), 2.0)
    grip = _soften_vertical_edges(_ribbon(grip_cl_scaled, grip_widths, grip_th, -7.5), 3.0)
    part.visual(
        mesh_from_cadquery(
            transition,
            "hammer_transition",
            tolerance=0.20,
            angular_tolerance=0.14,
            unit_scale=0.001,
        ),
        material=mats["rubber"],
        name="hammer_transition", material_class_id="rubber.smooth_plain",
    )
    part.visual(
        mesh_from_cadquery(
            grip,
            "hammer_grip",
            tolerance=0.22,
            angular_tolerance=0.14,
            unit_scale=0.001,
        ),
        material=mats["grip"],
        name="hammer_grip", material_class_id="rubber.smooth_plain",
    )


def _emit_claw_half(part, r: ResolvedConfig, mats: dict) -> None:
    (
        forging_cl,
        forging_w,
        trans_cl,
        trans_w,
        trans_th,
        grip_cl,
        grip_w,
        grip_th,
    ) = _handle_geometry(r)

    claw_cl = _mirror_x(forging_cl)
    claw_core = _ribbon(claw_cl, forging_w, 4.0, 0.5)

    head_pts = _scale_xy(_claw_head_points(r), r.head_scale)
    claw_head = _profile(head_pts, 4.0, 0.5)

    claw_forging = claw_core.union(claw_head).union(
        cq.Workplane("XY").circle(17.0).extrude(4.0).translate((0.0, 0.0, 0.5))
    )

    if r.jaw_cutter != "twin_side_cutters":
        # Only the asymmetric claw carries throat + fork_slot cuts.
        if r.hammer_claw_form == "deep_staple_claw":
            throat_center = (-52.0 * r.head_scale, 64.0 * r.head_scale)
            throat_r = 10.0 * r.head_scale
            fork_pts = [(-90.0, 48.0), (-70.0, 54.0), (-90.0, 60.0)]
        else:
            throat_center = (-39.0 * r.head_scale, 43.0 * r.head_scale)
            throat_r = 13.0 * r.head_scale
            fork_pts = [(-78.0, 55.0), (-56.0, 58.5), (-78.0, 62.0)]
        throat = (
            cq.Workplane("XY")
            .center(throat_center[0], throat_center[1])
            .circle(throat_r)
            .extrude(12.0)
            .translate((0.0, 0.0, -3.0))
        )
        fork_slot = _profile(_scale_xy(fork_pts, r.head_scale), 12.0, -3.0)
        try:
            claw_forging = claw_forging.cut(throat).cut(fork_slot)
        except Exception:
            pass

    claw_forging = _soften_vertical_edges(claw_forging.clean(), 1.5)
    part.visual(
        mesh_from_cadquery(
            claw_forging,
            "claw_forging",
            tolerance=0.20,
            angular_tolerance=0.14,
            unit_scale=0.001,
        ),
        material=mats["forged"],
        name="claw_forging", material_class_id="metal.steel_bare",
    )

    # Slot B jaw + cutter.
    if r.jaw_cutter == "twin_side_cutters":
        jaw = _profile(_mirror_x(_TWIN_JAW), 1.0, 4.2)
        cutter = _profile(_mirror_x(_TWIN_CUTTER), 0.8, 4.4)
        part.visual(
            mesh_from_cadquery(jaw, "claw_jaw", tolerance=0.12, unit_scale=0.001),
            material=mats["hardened"],
            name="claw_jaw", material_class_id="metal.blackened_gunmetal",
        )
        part.visual(
            mesh_from_cadquery(cutter, "claw_cutter", tolerance=0.12, unit_scale=0.001),
            material=mats["hardened"],
            name="claw_cutter", material_class_id="metal.blackened_gunmetal",
        )
    elif r.jaw_cutter == "broad_serrated_jaw":
        jaw = _profile(_CLAW_JAW_SERRATED, 2.5, 3.7)
        part.visual(
            mesh_from_cadquery(jaw, "claw_jaw", tolerance=0.12, unit_scale=0.001),
            material=mats["hardened"],
            name="claw_jaw", material_class_id="metal.blackened_gunmetal",
        )
    else:
        jaw = _profile(_CLAW_JAW_BASE, 1.0, 4.2)
        cutter = _profile(_CLAW_CUTTER_BASE, 1.0, 4.2)
        part.visual(
            mesh_from_cadquery(jaw, "claw_jaw", tolerance=0.12, unit_scale=0.001),
            material=mats["hardened"],
            name="claw_jaw", material_class_id="metal.blackened_gunmetal",
        )
        part.visual(
            mesh_from_cadquery(cutter, "claw_cutter", tolerance=0.12, unit_scale=0.001),
            material=mats["hardened"],
            name="claw_cutter", material_class_id="metal.blackened_gunmetal",
        )

    trans_widths = _scale_widths(trans_w, r.grip_girth_scale)
    grip_widths = _scale_widths(grip_w, r.grip_girth_scale)

    # Mirror centerlines for claw side.
    trans_cl_m = _mirror_x(trans_cl)
    grip_cl_m = _mirror_x(grip_cl)
    # Overall length scale.
    grip_cl_m = [(x, y * r.overall_len_scale) for x, y in grip_cl_m]

    transition = _soften_vertical_edges(_ribbon(trans_cl_m, trans_widths, trans_th, -2.0), 2.0)
    grip = _soften_vertical_edges(_ribbon(grip_cl_m, grip_widths, grip_th, -3.0), 3.0)
    part.visual(
        mesh_from_cadquery(
            transition,
            "claw_transition",
            tolerance=0.20,
            angular_tolerance=0.14,
            unit_scale=0.001,
        ),
        material=mats["rubber"],
        name="claw_transition", material_class_id="rubber.smooth_plain",
    )
    part.visual(
        mesh_from_cadquery(
            grip,
            "claw_grip",
            tolerance=0.22,
            angular_tolerance=0.14,
            unit_scale=0.001,
        ),
        material=mats["grip"],
        name="claw_grip", material_class_id="rubber.smooth_plain",
    )


# ---------------------------------------------------------------------------
# Builders
# ---------------------------------------------------------------------------
def build_pilers_fencing_pliers(
    config: PilersFencingPliersConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    palette = PALETTES[r.palette_style]
    mats = {
        key: model.material(f"pfp_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in palette.items()
    }

    # -----------------------------------------------------------------
    # pivot part (root). Holds the through pin + cap + back + optional
    # captured return spring.
    # -----------------------------------------------------------------
    pivot = model.part("pivot")
    pivot.visual(
        Cylinder(radius=0.011, length=0.011),
        origin=Origin(xyz=(0.0, 0.0, 0.00025)),
        material=mats["pivot"],
        name="pivot_pin", material_class_id="metal.steel_bare",
    )
    pivot.visual(
        Cylinder(radius=0.014, length=0.0015),
        origin=Origin(xyz=(0.0, 0.0, 0.00630)),
        material=mats["polished"],
        name="pivot_cap", material_class_id="metal.chrome_polished",
    )
    pivot.visual(
        Cylinder(radius=0.013, length=0.0015),
        origin=Origin(xyz=(0.0, 0.0, -0.00580)),
        material=mats["pivot"],
        name="pivot_back", material_class_id="metal.steel_bare",
    )
    if r.return_spring == "captured_spring":
        pivot.visual(
            mesh_from_cadquery(
                _captured_return_spring(),
                "captured_spring",
                tolerance=0.14,
                angular_tolerance=0.12,
                unit_scale=0.001,
            ),
            material=mats["spring"],
            name="captured_spring", material_class_id="metal.steel_bare",
        )

    # -----------------------------------------------------------------
    # hammer_handle + claw_handle
    # -----------------------------------------------------------------
    hammer_handle = model.part("hammer_handle")
    _emit_hammer_half(hammer_handle, r, mats)

    claw_handle = model.part("claw_handle")
    _emit_claw_half(claw_handle, r, mats)

    model.articulation(
        "pivot_to_hammer_half",
        ArticulationType.REVOLUTE,
        parent=pivot,
        child=hammer_handle,
        origin=Origin(),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(
            effort=180.0,
            velocity=2.0,
            lower=r.hammer_lower,
            upper=r.hammer_upper,
        ),
        meta={"positive_motion": "rotates the hammer half around the central pin"},
    )
    model.articulation(
        "pivot_to_claw_half",
        ArticulationType.REVOLUTE,
        parent=pivot,
        child=claw_handle,
        origin=Origin(),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(
            effort=180.0,
            velocity=2.0,
            lower=r.claw_lower,
            upper=r.claw_upper,
        ),
        meta={"positive_motion": "rotates the claw half around the central pin"},
    )

    if r.is_compound:
        # V-L1: two toggle link bars pinned on each handle's secondary pivot.
        hammer_link = model.part("hammer_link")
        h_bar = _soften_vertical_edges(
            _compound_link_bar(length=28.0, width=8.0, thickness=3.0, boss_radius=5.5, z0=-7.5),
            0.8,
        )
        hammer_link.visual(
            mesh_from_cadquery(
                h_bar,
                "hammer_link_bar",
                tolerance=0.14,
                angular_tolerance=0.12,
                unit_scale=0.001,
            ),
            material=mats["polished"],
            name="hammer_link_bar", material_class_id="metal.chrome_polished",
        )

        claw_link = model.part("claw_link")
        c_bar = _soften_vertical_edges(
            _compound_link_bar(length=28.0, width=8.0, thickness=3.0, boss_radius=5.5, z0=5.0),
            0.8,
        )
        claw_link.visual(
            mesh_from_cadquery(
                c_bar,
                "claw_link_bar",
                tolerance=0.14,
                angular_tolerance=0.12,
                unit_scale=0.001,
            ),
            material=mats["polished"],
            name="claw_link_bar", material_class_id="metal.chrome_polished",
        )

        model.articulation(
            "hammer_compound_link",
            ArticulationType.REVOLUTE,
            parent=hammer_handle,
            child=hammer_link,
            origin=Origin(xyz=(-0.015, 0.012, 0.0)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=50.0, velocity=2.0, lower=-0.35, upper=0.35),
            meta={"positive_motion": "swings the hammer-side compound link"},
        )
        model.articulation(
            "claw_compound_link",
            ArticulationType.REVOLUTE,
            parent=claw_handle,
            child=claw_link,
            origin=Origin(xyz=(0.015, 0.012, 0.0)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=50.0, velocity=2.0, lower=-0.35, upper=0.35),
            meta={"positive_motion": "swings the claw-side compound link"},
        )

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_pilers_fencing_pliers(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_pilers_fencing_pliers(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def run_pilers_fencing_pliers_tests(
    object_model: ArticulatedObject,
    config: PilersFencingPliersConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    pivot = object_model.get_part("pivot")
    hammer = object_model.get_part("hammer_handle")
    claw = object_model.get_part("claw_handle")
    hammer_joint = object_model.get_articulation("pivot_to_hammer_half")
    claw_joint = object_model.get_articulation("pivot_to_claw_half")

    # Captured-pin allowances (pivot pin captured through both forged hubs).
    ctx.allow_overlap(
        pivot,
        hammer,
        elem_a="pivot_pin",
        elem_b="hammer_forging",
        reason="pivot pin is captured through the hammer half hub",
    )
    ctx.allow_overlap(
        pivot,
        claw,
        elem_a="pivot_pin",
        elem_b="claw_forging",
        reason="pivot pin is captured through the claw half hub",
    )
    ctx.allow_overlap(
        pivot,
        hammer,
        elem_a="pivot_cap",
        elem_b="hammer_forging",
        reason="pivot cap sits on top of the hammer half hub",
    )
    ctx.allow_overlap(
        pivot,
        claw,
        elem_a="pivot_cap",
        elem_b="claw_forging",
        reason="pivot cap sits on top of the claw half hub",
    )
    ctx.allow_overlap(
        pivot,
        hammer,
        elem_a="pivot_back",
        elem_b="hammer_forging",
        reason="pivot back sits under the hammer half hub",
    )
    ctx.allow_overlap(
        pivot,
        claw,
        elem_a="pivot_back",
        elem_b="claw_forging",
        reason="pivot back sits under the claw half hub",
    )
    if r.return_spring == "captured_spring":
        ctx.allow_overlap(
            pivot,
            hammer,
            elem_a="captured_spring",
            elem_b="hammer_forging",
            reason="captured return spring wraps around and lays over the hammer forging",
        )
        ctx.allow_overlap(
            pivot,
            claw,
            elem_a="captured_spring",
            elem_b="claw_forging",
            reason="captured return spring wraps around and lays over the claw forging",
        )
    # The two forged half hubs share the central pivot area.
    ctx.allow_overlap(
        hammer,
        claw,
        elem_a="hammer_forging",
        elem_b="claw_forging",
        reason="the two forged hubs share the central pivot bearing area",
    )

    if r.is_compound:
        hammer_link = object_model.get_part("hammer_link")
        claw_link = object_model.get_part("claw_link")
        ctx.allow_overlap(
            hammer,
            hammer_link,
            reason="compound link boss captured on the hammer secondary pivot",
        )
        ctx.allow_overlap(
            claw,
            claw_link,
            reason="compound link boss captured on the claw secondary pivot",
        )
        ctx.check(
            "compound_link topology has 5 parts and 4 joints",
            len(object_model.parts) == 5 and len(object_model.articulations) == 4,
            details=(f"parts={len(object_model.parts)}, joints={len(object_model.articulations)}"),
        )
    else:
        ctx.check(
            "baseline topology is 3 parts and 2 joints",
            len(object_model.parts) == 3 and len(object_model.articulations) == 2,
            details=(f"parts={len(object_model.parts)}, joints={len(object_model.articulations)}"),
        )

    # Pivot hardware visuals.
    def has_visual(part_obj, name: str) -> bool:
        try:
            part_obj.get_visual(name)
            return True
        except Exception:
            return False

    ctx.check(
        "pivot pin, cap, and back exist",
        has_visual(pivot, "pivot_pin")
        and has_visual(pivot, "pivot_cap")
        and has_visual(pivot, "pivot_back"),
        details="pivot must expose pivot_pin, pivot_cap and pivot_back visuals.",
    )
    if r.return_spring == "captured_spring":
        ctx.check(
            "captured return spring visual exists",
            has_visual(pivot, "captured_spring"),
        )
    else:
        ctx.check(
            "no return spring visual on pivot",
            not has_visual(pivot, "captured_spring"),
        )

    # Forging visuals + slot B striking_face / cutter presence.
    ctx.check(
        "both forged halves exist",
        has_visual(hammer, "hammer_forging") and has_visual(claw, "claw_forging"),
    )
    if r.jaw_cutter == "twin_side_cutters":
        ctx.check(
            "twin_side_cutters drops the striking face",
            not has_visual(hammer, "striking_face"),
        )
        ctx.check(
            "twin_side_cutters keeps a cutter shim on both halves",
            has_visual(hammer, "hammer_cutter") and has_visual(claw, "claw_cutter"),
        )
    else:
        ctx.check(
            "asymmetric heads keep the striking face",
            has_visual(hammer, "striking_face"),
        )
        if r.jaw_cutter == "broad_serrated_jaw":
            ctx.check(
                "broad_serrated_jaw drops both cutter shims",
                not has_visual(hammer, "hammer_cutter") and not has_visual(claw, "claw_cutter"),
            )
        else:
            ctx.check(
                "jaw_with_cutter keeps both cutter shims",
                has_visual(hammer, "hammer_cutter") and has_visual(claw, "claw_cutter"),
            )

    ctx.check(
        "both hardened jaws exist",
        has_visual(hammer, "hammer_jaw") and has_visual(claw, "claw_jaw"),
    )
    ctx.check(
        "both grips and transitions exist",
        has_visual(hammer, "hammer_grip")
        and has_visual(claw, "claw_grip")
        and has_visual(hammer, "hammer_transition")
        and has_visual(claw, "claw_transition"),
    )

    # Slot A geometry claim: round_hammer_face has a wide face,
    # deep_staple_claw reaches further along -x.
    if r.hammer_claw_form == "deep_staple_claw" and r.jaw_cutter != "twin_side_cutters":
        claw_box = ctx.part_element_world_aabb(claw, elem="claw_forging")
        if claw_box is not None:
            # head_scale can clamp down to 0.90, so -88 * 0.90 * 0.001 = -0.0792.
            ctx.check(
                "deep_staple_claw reaches further along -x",
                claw_box[0][0] < -0.070,
                details=f"claw_forging min_x={claw_box[0][0]:.4f}",
            )

    # Slot D geometry claim: long_fencing_handle extends grip along -y.
    if r.handle_form == "long_fencing_handle":
        grip_box = ctx.part_element_world_aabb(hammer, elem="hammer_grip")
        if grip_box is not None:
            ctx.check(
                "long_fencing_handle extends grip below -0.245 m",
                grip_box[0][1] < -0.245,
                details=f"hammer_grip min_y={grip_box[0][1]:.4f}",
            )

    # Joint sanity.
    for j, name in ((hammer_joint, "pivot_to_hammer_half"), (claw_joint, "pivot_to_claw_half")):
        lm = j.motion_limits
        ctx.check(
            f"{name} is a bounded REVOLUTE about +Z",
            j.articulation_type == ArticulationType.REVOLUTE
            and lm is not None
            and tuple(j.axis) == (0.0, 0.0, 1.0)
            and lm.upper > 0.0
            and lm.lower < 0.0,
            details=f"limits={lm}, axis={j.axis}",
        )

    # Kinematics: opening the hammer joint shifts the hammer grip in x;
    # opening the claw joint shifts the claw grip in x. The rest-pose grip
    # centres are on either side of the pivot pin.
    rest_hammer_grip = ctx.part_element_world_aabb(hammer, elem="hammer_grip")
    rest_claw_grip = ctx.part_element_world_aabb(claw, elem="claw_grip")

    def _cx(bounds):
        if bounds is None:
            return None
        return 0.5 * (bounds[0][0] + bounds[1][0])

    rest_hx = _cx(rest_hammer_grip)
    rest_cx = _cx(rest_claw_grip)

    with ctx.pose({hammer_joint: hammer_joint.motion_limits.lower}):
        open_hx = _cx(ctx.part_element_world_aabb(hammer, elem="hammer_grip"))
    with ctx.pose({claw_joint: claw_joint.motion_limits.upper}):
        open_cx = _cx(ctx.part_element_world_aabb(claw, elem="claw_grip"))

    ctx.check(
        "hammer joint negative pose swings hammer grip",
        rest_hx is not None and open_hx is not None and abs(open_hx - rest_hx) > 0.005,
        details=f"rest_hx={rest_hx}, open_hx={open_hx}",
    )
    ctx.check(
        "claw joint positive pose swings claw grip",
        rest_cx is not None and open_cx is not None and abs(open_cx - rest_cx) > 0.005,
        details=f"rest_cx={rest_cx}, open_cx={open_cx}",
    )

    ctx.check(
        "slot_choices metadata is emitted",
        object_model.meta.get("slot_choices") == slot_choices_for_config(r),
        details=f"meta slot_choices={object_model.meta.get('slot_choices')}",
    )

    return ctx.report()


__all__ = [
    "PilersFencingPliersConfig",
    "ResolvedConfig",
    "config_from_seed",
    "resolve_config",
    "with_overrides",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "build_pilers_fencing_pliers",
    "build_seeded_pilers_fencing_pliers",
    "run_pilers_fencing_pliers_tests",
    "__modular__",
]
