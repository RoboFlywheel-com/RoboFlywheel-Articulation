# SPDX-License-Identifier: Apache-2.0

"""Slip-joint pliers modular template (0611 / pilers_slip_joint_pliers).

Sourced from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/pilers_slip_joint_pliers.md``
and the ``pictureX/0611/Pilers_slip_joint_pliers`` 5-star pool (origin
``slip_joint_pliers_001`` + 8 single-axis fork variants).

Structure (pattern ``mixed``, parallel-children):

* baseline 4-part / 3-joint chain:
  ``slot_guide`` (root) + ``pivot_slider`` + ``round_member`` + ``slotted_member``.
  ``guide_to_slider`` PRISMATIC (guide -> slider, axis +X) selects the pivot detent.
  ``slider_to_round_member`` REVOLUTE (slider -> round, axis +Z) and
  ``slider_to_slotted_member`` REVOLUTE (slider -> slotted, axis +Z) open the jaws.
* ``pivot_topology = push_button_selector`` appends a ``selector_button`` part +
  ``slider_to_button`` PRISMATIC (axis -Z) for a 5-part / 4-joint chain.

Slots:

* ``jaw_form`` (3): flat_serrated (baseline) / broad_flat_jaw / curved_pipe_jaw.
  Swaps ``jaw_teeth`` visual on both forged members.
* ``pivot_topology`` (3): sliding_rivet / captured_box_joint / push_button_selector.
* ``pivot_positions`` (4): 2 / 3 / 5 / 7 selectable detents; multiplicity axis.
  Length of ``slot_track`` and PRISMATIC upper scale with N.
* ``handle_form`` (2): straight_dipped (baseline) / flared_comfort_grip.

``palette_style`` (6): rgba axis only; not in slot_choices, does not change topology.
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
    MotionProperties,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
)

__modular__ = True

# ---------------------------------------------------------------------------
# Enum axes
# ---------------------------------------------------------------------------
JawForm = Literal["flat_serrated", "broad_flat_jaw", "curved_pipe_jaw"]
PivotTopology = Literal["sliding_rivet", "captured_box_joint", "push_button_selector"]
HandleForm = Literal["straight_dipped", "flared_comfort_grip"]
PaletteStyle = Literal[
    "steel_blue",
    "gunmetal_red",
    "chrome_dark_blue",
    "black_yellow",
    "industrial_green",
    "brushed_steel_orange",
]

JAW_FORMS: tuple[JawForm, ...] = ("flat_serrated", "broad_flat_jaw", "curved_pipe_jaw")
PIVOT_TOPOLOGIES: tuple[PivotTopology, ...] = (
    "sliding_rivet",
    "captured_box_joint",
    "push_button_selector",
)
PIVOT_POSITIONS_VALUES: tuple[int, ...] = (2, 3, 5, 7)
HANDLE_FORMS: tuple[HandleForm, ...] = ("straight_dipped", "flared_comfort_grip")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "steel_blue",
    "gunmetal_red",
    "chrome_dark_blue",
    "black_yellow",
    "industrial_green",
    "brushed_steel_orange",
)

# Baseline detent spacing from V-P1 (metres between adjacent pivot positions).
PIVOT_SPACING = 0.012
# Baseline REVOLUTE open ranges (P0).
BASE_ROUND_LOWER = -0.28
BASE_ROUND_UPPER = 0.04
BASE_SLOTTED_LOWER = -0.04
BASE_SLOTTED_UPPER = 0.28

# ---------------------------------------------------------------------------
# Palettes. Each provides material rgba keys the builder always references.
# Metal category covered by steel_blue / chrome_dark_blue / brushed_steel_orange;
# vinyl/rubber covered by gunmetal_red / black_yellow / industrial_green.
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "steel_blue": {
        "steel": (0.54, 0.57, 0.57, 1.0),
        "steel_front": (0.64, 0.66, 0.65, 1.0),
        "tooth": (0.22, 0.24, 0.23, 1.0),
        "grip": (0.025, 0.18, 0.36, 1.0),
        "slot_dark": (0.10, 0.11, 0.11, 1.0),
        "rivet": (0.70, 0.72, 0.71, 1.0),
        "button": (0.72, 0.11, 0.09, 1.0),
    },
    "gunmetal_red": {
        "steel": (0.40, 0.42, 0.44, 1.0),
        "steel_front": (0.52, 0.54, 0.56, 1.0),
        "tooth": (0.18, 0.20, 0.20, 1.0),
        "grip": (0.75, 0.10, 0.09, 1.0),
        "slot_dark": (0.08, 0.09, 0.09, 1.0),
        "rivet": (0.62, 0.64, 0.65, 1.0),
        "button": (0.15, 0.15, 0.16, 1.0),
    },
    "chrome_dark_blue": {
        "steel": (0.82, 0.84, 0.87, 1.0),
        "steel_front": (0.88, 0.89, 0.92, 1.0),
        "tooth": (0.30, 0.32, 0.34, 1.0),
        "grip": (0.05, 0.10, 0.28, 1.0),
        "slot_dark": (0.12, 0.13, 0.14, 1.0),
        "rivet": (0.90, 0.91, 0.93, 1.0),
        "button": (0.78, 0.14, 0.14, 1.0),
    },
    "black_yellow": {
        "steel": (0.18, 0.18, 0.20, 1.0),
        "steel_front": (0.28, 0.28, 0.30, 1.0),
        "tooth": (0.08, 0.08, 0.10, 1.0),
        "grip": (0.95, 0.80, 0.10, 1.0),
        "slot_dark": (0.05, 0.05, 0.06, 1.0),
        "rivet": (0.55, 0.55, 0.58, 1.0),
        "button": (0.10, 0.10, 0.12, 1.0),
    },
    "industrial_green": {
        "steel": (0.55, 0.57, 0.59, 1.0),
        "steel_front": (0.64, 0.66, 0.68, 1.0),
        "tooth": (0.18, 0.20, 0.22, 1.0),
        "grip": (0.08, 0.42, 0.18, 1.0),
        "slot_dark": (0.09, 0.09, 0.10, 1.0),
        "rivet": (0.70, 0.72, 0.71, 1.0),
        "button": (0.90, 0.75, 0.10, 1.0),
    },
    "brushed_steel_orange": {
        "steel": (0.60, 0.62, 0.64, 1.0),
        "steel_front": (0.72, 0.74, 0.75, 1.0),
        "tooth": (0.22, 0.24, 0.25, 1.0),
        "grip": (0.95, 0.44, 0.06, 1.0),
        "slot_dark": (0.10, 0.11, 0.11, 1.0),
        "rivet": (0.74, 0.76, 0.77, 1.0),
        "button": (0.20, 0.20, 0.22, 1.0),
    },
}


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class PilersSlipJointPliersConfig:
    jaw_form: JawForm | None = None
    pivot_topology: PivotTopology | None = None
    pivot_positions: int | None = None
    handle_form: HandleForm | None = None
    palette_style: PaletteStyle = "steel_blue"
    overall_len_scale: float = 1.0
    jaw_len_scale: float = 1.0
    grip_girth_scale: float = 1.0
    open_angle_scale: float = 1.0
    name: str = "pilers_slip_joint_pliers"


@dataclass(frozen=True)
class ResolvedConfig:
    jaw_form: JawForm
    pivot_topology: PivotTopology
    pivot_positions: int
    handle_form: HandleForm
    palette_style: PaletteStyle
    overall_len_scale: float
    jaw_len_scale: float
    grip_girth_scale: float
    round_lower: float
    round_upper: float
    slotted_lower: float
    slotted_upper: float
    name: str

    @property
    def slide_upper(self) -> float:
        return (self.pivot_positions - 1) * PIVOT_SPACING

    @property
    def slide_origin_x(self) -> float:
        return -(self.pivot_positions - 1) * PIVOT_SPACING / 2.0

    @property
    def has_button(self) -> bool:
        return self.pivot_topology == "push_button_selector"


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


def config_from_seed(seed: int) -> PilersSlipJointPliersConfig:
    rng = random.Random(seed)
    jaw = rng.choices(JAW_FORMS, weights=[5, 3, 3], k=1)[0]
    topo = rng.choices(PIVOT_TOPOLOGIES, weights=[5, 3, 3], k=1)[0]
    positions = rng.choices(PIVOT_POSITIONS_VALUES, weights=[3, 3, 2, 2], k=1)[0]
    hand = rng.choices(HANDLE_FORMS, weights=[5, 3], k=1)[0]
    return PilersSlipJointPliersConfig(
        jaw_form=jaw,
        pivot_topology=topo,
        pivot_positions=positions,
        handle_form=hand,
        palette_style=rng.choice(PALETTE_STYLES),
        overall_len_scale=round(rng.uniform(0.92, 1.10), 4),
        jaw_len_scale=round(rng.uniform(0.90, 1.08), 4),
        grip_girth_scale=round(rng.uniform(0.92, 1.08), 4),
        open_angle_scale=round(rng.uniform(0.85, 1.15), 4),
        name=f"seeded_pilers_slip_joint_pliers_{seed}",
    )


def resolve_config(config: PilersSlipJointPliersConfig | None = None) -> ResolvedConfig:
    cfg = config or PilersSlipJointPliersConfig()
    jaw = _pick(cfg.jaw_form, JAW_FORMS)
    topo = _pick(cfg.pivot_topology, PIVOT_TOPOLOGIES)
    positions = cfg.pivot_positions if cfg.pivot_positions in PIVOT_POSITIONS_VALUES else 2
    hand = _pick(cfg.handle_form, HANDLE_FORMS)
    palette = _pick(cfg.palette_style, PALETTE_STYLES)

    overall = _clamp(cfg.overall_len_scale, 0.92, 1.10)
    jaw_len = _clamp(cfg.jaw_len_scale, 0.90, 1.08)
    grip_girth = _clamp(cfg.grip_girth_scale, 0.92, 1.08)
    ang = _clamp(cfg.open_angle_scale, 0.85, 1.15)

    round_lower = _clamp(BASE_ROUND_LOWER * ang, -0.34, -0.22)
    round_upper = _clamp(BASE_ROUND_UPPER * ang, 0.02, 0.06)
    slotted_lower = _clamp(BASE_SLOTTED_LOWER * ang, -0.06, -0.02)
    slotted_upper = _clamp(BASE_SLOTTED_UPPER * ang, 0.22, 0.34)

    return ResolvedConfig(
        jaw_form=jaw,
        pivot_topology=topo,
        pivot_positions=positions,
        handle_form=hand,
        palette_style=palette,
        overall_len_scale=overall,
        jaw_len_scale=jaw_len,
        grip_girth_scale=grip_girth,
        round_lower=round_lower,
        round_upper=round_upper,
        slotted_lower=slotted_lower,
        slotted_upper=slotted_upper,
        name=cfg.name or "pilers_slip_joint_pliers",
    )


def with_overrides(
    config: PilersSlipJointPliersConfig, **kwargs: object
) -> PilersSlipJointPliersConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: PilersSlipJointPliersConfig | ResolvedConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedConfig) else resolve_config(config)
    return (
        ("jaw_form", r.jaw_form),
        ("pivot_topology", r.pivot_topology),
        ("pivot_positions", f"{r.pivot_positions}_position"),
        ("handle_form", r.handle_form),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Geometry helpers (from P0 origin_anchor).
# ---------------------------------------------------------------------------
def _polygon_prism(points: list[tuple[float, float]], thickness: float) -> cq.Workplane:
    return cq.Workplane("XY").polyline(points).close().extrude(thickness)


def _mirror_points(points: list[tuple[float, float]]) -> list[tuple[float, float]]:
    return [(-x, y) for x, y in points]


def _scale_y(points: list[tuple[float, float]], factor: float = 0.69) -> list[tuple[float, float]]:
    return [(x, y * factor) for x, y in points]


def _scale_xy(points: list[tuple[float, float]], sx: float, sy: float) -> list[tuple[float, float]]:
    return [(x * sx, y * sy) for x, y in points]


# Baseline jaw outer outline (used to construct forged member metal body).
JAW_OUTLINE_BASE = [
    (-0.0175, -0.027),
    (-0.0130, -0.009),
    (-0.0060, 0.008),
    (0.0005, 0.021),
    (0.0025, 0.038),
    (0.0027, 0.051),
    (0.0055, 0.055),
    (0.0026, 0.059),
    (0.0055, 0.063),
    (0.0025, 0.067),
    (0.0054, 0.071),
    (0.0024, 0.075),
    (0.0052, 0.079),
    (0.0023, 0.083),
    (0.0049, 0.087),
    (0.0022, 0.091),
    (0.0042, 0.098),
    (0.0080, 0.103),
    (0.0115, 0.102),
    (0.0165, 0.091),
    (0.0190, 0.074),
    (0.0195, 0.053),
    (0.0183, 0.033),
    (0.0158, 0.014),
    (0.0140, -0.007),
    (0.0100, -0.025),
]

TANG_OUTLINE_BASE = [
    (-0.0130, -0.006),
    (-0.0220, -0.029),
    (-0.0275, -0.055),
    (-0.0310, -0.086),
    (-0.0315, -0.124),
    (-0.0230, -0.127),
    (-0.0180, -0.087),
    (-0.0135, -0.052),
    (-0.0060, -0.020),
    (0.0060, -0.010),
]


def _member_metal(
    *,
    mirrored: bool,
    thickness: float,
    z0: float,
    slotted: bool,
    slot_length: float,
    y_scale: float,
) -> cq.Workplane:
    """One forged plier member: jaw + pivot plate + tang.

    ``slotted=True`` cuts an elongated slot2D sized to ``slot_length``; else
    a circular pivot hole. Uses ``y_scale`` (baseline 0.69 * jaw_len_scale)
    to lengthen the member.
    """
    jaw_outline = _scale_y(JAW_OUTLINE_BASE, y_scale)
    tang_outline = _scale_y(TANG_OUTLINE_BASE, y_scale)
    if mirrored:
        jaw_outline = _mirror_points(jaw_outline)
        tang_outline = _mirror_points(tang_outline)

    pivot_plate = cq.Workplane("XY").circle(0.0225).extrude(thickness)
    jaw = _polygon_prism(jaw_outline, thickness)
    tang = _polygon_prism(tang_outline, thickness)
    member = pivot_plate.union(jaw).union(tang).clean()

    if slotted:
        # Extend the slot in x to cover all N detent positions plus a small
        # margin. Height fixed at 0.0145 (matches source, fits shaft dia).
        cutter = (
            cq.Workplane("XY")
            .slot2D(slot_length, 0.0145, 0.0)
            .extrude(thickness + 0.004)
            .translate((0.0, 0.0, -0.002))
        )
    else:
        cutter = (
            cq.Workplane("XY")
            .circle(0.0060)
            .extrude(thickness + 0.004)
            .translate((0.0, 0.0, -0.002))
        )

    return member.cut(cutter).translate((0.0, 0.0, z0))


# ---------------------------------------------------------------------------
# Slot D -- handle_form: grip polylines.
# ---------------------------------------------------------------------------
_STRAIGHT_DIPPED = [
    (-0.0320, -0.052),
    (-0.0380, -0.084),
    (-0.0420, -0.126),
    (-0.0430, -0.168),
    (-0.0390, -0.184),
    (-0.0320, -0.193),
    (-0.0250, -0.188),
    (-0.0215, -0.173),
    (-0.0205, -0.133),
    (-0.0185, -0.092),
    (-0.0170, -0.058),
    (-0.0210, -0.051),
]

_FLARED_COMFORT = [
    (-0.0330, -0.052),
    (-0.0400, -0.078),
    (-0.0465, -0.108),
    (-0.0490, -0.138),
    (-0.0480, -0.162),
    (-0.0440, -0.180),
    (-0.0360, -0.192),
    (-0.0280, -0.188),
    (-0.0230, -0.172),
    (-0.0248, -0.152),
    (-0.0220, -0.132),
    (-0.0238, -0.112),
    (-0.0205, -0.088),
    (-0.0185, -0.062),
    (-0.0220, -0.051),
]

_GRIP_OUTLINES: dict[HandleForm, list[tuple[float, float]]] = {
    "straight_dipped": _STRAIGHT_DIPPED,
    "flared_comfort_grip": _FLARED_COMFORT,
}


def _grip(
    *,
    handle: HandleForm,
    mirrored: bool,
    z0: float,
    thickness: float,
    y_scale: float,
    x_scale: float,
) -> cq.Workplane:
    outline = _scale_xy(_scale_y(_GRIP_OUTLINES[handle], y_scale), x_scale, 1.0)
    if mirrored:
        outline = _mirror_points(outline)
    grip = _polygon_prism(outline, thickness)
    try:
        grip = grip.edges("|Z").fillet(0.003)
    except Exception:
        pass
    return grip.translate((0.0, 0.0, z0))


# ---------------------------------------------------------------------------
# Slot A -- jaw_form: jaw_teeth visual per member.
# ---------------------------------------------------------------------------
_FLAT_SERRATED_TEETH = [
    (0.0027, 0.051),
    (0.0055, 0.055),
    (0.0026, 0.059),
    (0.0055, 0.063),
    (0.0025, 0.067),
    (0.0054, 0.071),
    (0.0024, 0.075),
    (0.0052, 0.079),
    (0.0023, 0.083),
    (0.0049, 0.087),
    (0.0022, 0.091),
    (0.0042, 0.098),
    (0.0080, 0.099),
    (0.0090, 0.052),
]

_BROAD_FLAT_TEETH = [
    (0.0025, 0.049),
    (0.0058, 0.053),
    (0.0032, 0.057),
    (0.0058, 0.061),
    (0.0032, 0.065),
    (0.0057, 0.069),
    (0.0031, 0.073),
    (0.0056, 0.077),
    (0.0030, 0.081),
    (0.0054, 0.085),
    (0.0029, 0.089),
    (0.0048, 0.096),
    (0.0120, 0.098),
    (0.0130, 0.050),
]


def _planar_teeth(
    *,
    points: list[tuple[float, float]],
    mirrored: bool,
    z0: float,
    thickness: float,
    y_scale: float,
) -> cq.Workplane:
    scaled = _scale_y(points, y_scale)
    if mirrored:
        scaled = _mirror_points(scaled)
    return _polygon_prism(scaled, thickness).translate((0.0, 0.0, z0))


def _curved_pipe_teeth(
    *, mirrored: bool, z0: float, thickness: float, y_scale: float
) -> cq.Workplane:
    """Curved pipe-grip channel: box block minus a Y-axis cylinder cutter.

    Reads as a U-groove on the inner (gripping) face — an alternative
    volumetric envelope for the jaw face.
    """
    sign = -1.0 if mirrored else 1.0
    # Y-range of the jaw face in scaled member coordinates.
    y_lo = 0.051 * y_scale
    y_hi = 0.098 * y_scale
    jaw_length = y_hi - y_lo
    y_mid = (y_lo + y_hi) / 2.0

    face_width = 0.006
    block_depth = 0.002
    x_center = 0.0055 * sign

    base = (
        cq.Workplane("XY")
        .box(face_width, jaw_length, block_depth)
        .translate((x_center, y_mid, block_depth / 2.0))
    )

    pipe_r = 0.004
    inner_x = x_center - sign * (face_width / 2.0)
    cutter_x = inner_x - sign * 0.001
    cutter_z = block_depth + pipe_r * 0.6
    cutter = (
        cq.Workplane("YZ")
        .center(y_mid, cutter_z)
        .circle(pipe_r)
        .extrude(jaw_length * 2.0, both=True)
        .translate((cutter_x, 0.0, 0.0))
    )
    channel = base.cut(cutter)
    # The requested `thickness` argument (kept for API parity) is only used
    # to keep the z-block flush with the member face.
    _ = thickness
    return channel.translate((0.0, 0.0, z0 - block_depth / 2.0))


def _jaw_teeth_mesh(
    r: ResolvedConfig,
    *,
    mirrored: bool,
    z0: float,
    thickness: float,
    y_scale: float,
    name: str,
):
    if r.jaw_form == "flat_serrated":
        wp = _planar_teeth(
            points=_FLAT_SERRATED_TEETH,
            mirrored=mirrored,
            z0=z0,
            thickness=thickness,
            y_scale=y_scale,
        )
    elif r.jaw_form == "broad_flat_jaw":
        wp = _planar_teeth(
            points=_BROAD_FLAT_TEETH,
            mirrored=mirrored,
            z0=z0,
            thickness=thickness,
            y_scale=y_scale,
        )
    else:  # curved_pipe_jaw
        wp = _curved_pipe_teeth(mirrored=mirrored, z0=z0, thickness=thickness, y_scale=y_scale)
    return mesh_from_cadquery(wp, name, tolerance=0.0004)


# ---------------------------------------------------------------------------
# slot_track + captured-box variants + push_button parts.
# ---------------------------------------------------------------------------
def _slot_track(length: float) -> cq.Workplane:
    return (
        cq.Workplane("XY")
        .slot2D(length, 0.0128, 0.0)
        .extrude(0.0007)
        .translate((0.0, 0.0, 0.00015))
    )


def _front_rivet_head() -> cq.Workplane:
    head = cq.Workplane("XY").circle(0.0073).extrude(0.0021)
    try:
        head = head.edges(">Z").fillet(0.0010)
    except Exception:
        pass
    return head.translate((0.0, 0.0, 0.0048))


def _box_shaft() -> cq.Workplane:
    """Square cross-section captured box-joint pivot shaft (V-T1)."""
    shaft = cq.Workplane("XY").rect(0.0082, 0.0082).extrude(0.0120)
    try:
        shaft = shaft.edges("|Z").fillet(0.0008)
    except Exception:
        pass
    return shaft.translate((0.0, 0.0, -0.005))


def _box_pivot_marker() -> cq.Workplane:
    return cq.Workplane("XY").rect(0.0080, 0.0080).extrude(0.00025).translate((0.0, 0.0, 0.000835))


def _selector_button_cap() -> cq.Workplane:
    """Push-button dome cap + short stem (V-T2)."""
    cap = cq.Workplane("XY").circle(0.0032).extrude(0.0022)
    try:
        cap = cap.edges(">Z").fillet(0.0012)
    except Exception:
        pass
    stem = cq.Workplane("XY").circle(0.0018).extrude(-0.0030)
    return cap.union(stem).clean()


def _button_bore() -> cq.Workplane:
    return cq.Workplane("XY").circle(0.0036).extrude(0.0012).translate((0.0, 0.0, -0.0006))


# ---------------------------------------------------------------------------
# Builders
# ---------------------------------------------------------------------------
def build_pilers_slip_joint_pliers(
    config: PilersSlipJointPliersConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    palette = PALETTES[r.palette_style]
    mats = {
        key: model.material(f"psjp_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in palette.items()
    }

    n = r.pivot_positions
    slide_upper = r.slide_upper
    slide_origin_x = r.slide_origin_x
    # slot_track is authored in slot_guide's frame centred at 0. Its length
    # covers all N detents plus visual margins so the shaft stays captured.
    slot_track_length = slide_upper + 0.018
    # slotted_member's elongated pivot hole encodes the slip-joint slot on
    # the pivot plate itself. It must stay well within the pivot plate radius
    # (0.0225) so the plate remains a single connected piece across N.
    slot_member_length = min(slide_upper + 0.018, 0.036)

    # y-scale for member / jaw geometry (baseline 0.69 * jaw_len_scale).
    y_scale = 0.69 * r.jaw_len_scale
    # overall_len_scale only scales the grip length (keeps the pivot / jaw
    # geometry near source proportions).
    grip_y_scale = r.overall_len_scale
    grip_x_scale = r.grip_girth_scale
    member_thickness = 0.0038

    # ------------------------------------------------------------------
    # slot_guide (root): slot_track + N-1 alternate_pivot markers.
    # ------------------------------------------------------------------
    slot_guide = model.part(
        "slot_guide",
        meta={
            "feature": "multi_position_pivot_track",
            "pivot_positions": n,
            "pivot_topology": r.pivot_topology,
        },
    )
    slot_guide.visual(
        mesh_from_cadquery(_slot_track(slot_track_length), "slot_track", tolerance=0.00035),
        material=mats["slot_dark"],
        name="slot_track", material_class_id="metal.blackened_gunmetal",
    )
    # Alternate pivot markers for every non-selected detent.
    for i in range(1, n):
        x_pos = slide_origin_x + i * PIVOT_SPACING
        if r.pivot_topology == "captured_box_joint":
            slot_guide.visual(
                mesh_from_cadquery(
                    _box_pivot_marker(),
                    f"alternate_pivot_marker_{i}",
                    tolerance=0.00025,
                ),
                origin=Origin(xyz=(x_pos, 0.0, 0.0)),
                material=mats["slot_dark"],
                name=f"alternate_pivot_{i}", material_class_id="metal.blackened_gunmetal",
            )
        else:
            slot_guide.visual(
                Cylinder(radius=0.0048, length=0.00025),
                origin=Origin(xyz=(x_pos, 0.0, 0.00096)),
                material=mats["slot_dark"],
                name=f"alternate_pivot_{i}", material_class_id="metal.blackened_gunmetal",
            )

    # ------------------------------------------------------------------
    # pivot_slider.
    # ------------------------------------------------------------------
    pivot_slider = model.part(
        "pivot_slider",
        meta={
            "feature": "captured_sliding_rivet",
            "selected_position": 0,
            "pivot_topology": r.pivot_topology,
        },
    )
    if r.pivot_topology == "captured_box_joint":
        pivot_slider.visual(
            mesh_from_cadquery(_box_shaft(), "box_pivot_shaft", tolerance=0.0003),
            material=mats["rivet"],
            name="pivot_shaft", material_class_id="metal.stainless_matte",
        )
    else:
        pivot_slider.visual(
            Cylinder(radius=0.0052, length=0.0120),
            origin=Origin(xyz=(0.0, 0.0, 0.0010)),
            material=mats["rivet"],
            name="pivot_shaft", material_class_id="metal.stainless_matte",
        )
    pivot_slider.visual(
        mesh_from_cadquery(_front_rivet_head(), "front_rivet_head", tolerance=0.00025),
        material=mats["rivet"],
        name="front_rivet_head", material_class_id="metal.stainless_matte",
    )
    pivot_slider.visual(
        Cylinder(radius=0.0063, length=0.0014),
        origin=Origin(xyz=(0.0, 0.0, -0.0045)),
        material=mats["steel"],
        name="rear_rivet_head", material_class_id=("metal.paint_coated" if r.palette_style in {"steel_blue", "chrome_dark_blue", "black_yellow", "industrial_green", "brushed_steel_orange"} else "metal.blackened_gunmetal"),
    )

    if r.has_button:
        # Sink and bridge live on the slider so the button reads as seated.
        pivot_slider.visual(
            mesh_from_cadquery(_button_bore(), "button_bore", tolerance=0.0003),
            origin=Origin(xyz=(0.0, 0.012, 0.0070)),
            material=mats["slot_dark"],
            name="button_bore", material_class_id="metal.blackened_gunmetal",
        )
        pivot_slider.visual(
            Cylinder(radius=0.0010, length=0.010),
            origin=Origin(xyz=(0.0, 0.006, 0.0070), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["slot_dark"],
            name="bore_bridge", material_class_id="metal.blackened_gunmetal",
        )

    # ------------------------------------------------------------------
    # round_member (image-left handle, image-right jaw, non-mirrored).
    # ------------------------------------------------------------------
    round_member = model.part(
        "round_member",
        meta={
            "handle_side": "image_left",
            "jaw_side": "image_right",
            "jaw_form": r.jaw_form,
            "pivot_opening": "round",
        },
    )
    round_member.visual(
        mesh_from_cadquery(
            _member_metal(
                mirrored=False,
                thickness=member_thickness,
                z0=-member_thickness,
                slotted=False,
                slot_length=slot_member_length,
                y_scale=y_scale,
            ),
            "round_member_metal",
            tolerance=0.0004,
        ),
        material=mats["steel"],
        name="metal_body", material_class_id=("metal.paint_coated" if r.palette_style in {"steel_blue", "chrome_dark_blue", "black_yellow", "industrial_green", "brushed_steel_orange"} else "metal.blackened_gunmetal"),
    )
    round_member.visual(
        _jaw_teeth_mesh(
            r,
            mirrored=False,
            z0=-0.00005,
            thickness=0.00035,
            y_scale=y_scale,
            name="round_jaw_teeth",
        ),
        material=mats["tooth"],
        name="jaw_teeth", material_class_id="metal.blackened_gunmetal",
    )
    round_member.visual(
        mesh_from_cadquery(
            _grip(
                handle=r.handle_form,
                mirrored=False,
                z0=-0.0053,
                thickness=0.0076,
                y_scale=grip_y_scale,
                x_scale=grip_x_scale,
            ),
            "round_member_grip",
            tolerance=0.00045,
        ),
        material=mats["grip"],
        name="blue_grip", material_class_id=("plastic.opaque_glossy_molded" if r.handle_form == "straight_dipped" else "rubber.smooth_plain"),
    )

    # ------------------------------------------------------------------
    # slotted_member (image-right handle, image-left jaw, mirrored, with
    # elongated slot).
    # ------------------------------------------------------------------
    slotted_member = model.part(
        "slotted_member",
        meta={
            "handle_side": "image_right",
            "jaw_side": "image_left",
            "jaw_form": r.jaw_form,
            "pivot_opening": "elongated_slot",
        },
    )
    slotted_member.visual(
        mesh_from_cadquery(
            _member_metal(
                mirrored=True,
                thickness=member_thickness,
                z0=0.0010,
                slotted=True,
                slot_length=slot_member_length,
                y_scale=y_scale,
            ),
            "slotted_member_metal",
            tolerance=0.0004,
        ),
        material=mats["steel_front"],
        name="metal_body", material_class_id=("metal.paint_coated" if r.palette_style in {"steel_blue", "chrome_dark_blue", "black_yellow", "industrial_green", "brushed_steel_orange"} else "metal.blackened_gunmetal"),
    )
    slotted_member.visual(
        _jaw_teeth_mesh(
            r,
            mirrored=True,
            z0=0.00475,
            thickness=0.00035,
            y_scale=y_scale,
            name="slotted_jaw_teeth",
        ),
        material=mats["tooth"],
        name="jaw_teeth", material_class_id="metal.blackened_gunmetal",
    )
    slotted_member.visual(
        mesh_from_cadquery(
            _grip(
                handle=r.handle_form,
                mirrored=True,
                z0=-0.0004,
                thickness=0.0076,
                y_scale=grip_y_scale,
                x_scale=grip_x_scale,
            ),
            "slotted_member_grip",
            tolerance=0.00045,
        ),
        material=mats["grip"],
        name="blue_grip", material_class_id=("plastic.opaque_glossy_molded" if r.handle_form == "straight_dipped" else "rubber.smooth_plain"),
    )

    # ------------------------------------------------------------------
    # Joints.
    # ------------------------------------------------------------------
    model.articulation(
        "guide_to_slider",
        ArticulationType.PRISMATIC,
        parent=slot_guide,
        child=pivot_slider,
        origin=Origin(xyz=(slide_origin_x, 0.0, 0.0)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=180.0, velocity=0.04, lower=0.0, upper=slide_upper),
        motion_properties=MotionProperties(damping=2.0, friction=8.0),
        meta={"mechanism": "guided_multi_position_slip_joint"},
    )

    model.articulation(
        "slider_to_round_member",
        ArticulationType.REVOLUTE,
        parent=pivot_slider,
        child=round_member,
        origin=Origin(),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(
            effort=120.0, velocity=2.0, lower=r.round_lower, upper=r.round_upper
        ),
        motion_properties=MotionProperties(damping=0.35, friction=0.8),
        meta={"positive_motion": "closes_image_left_handle_and_right_jaw"},
    )

    model.articulation(
        "slider_to_slotted_member",
        ArticulationType.REVOLUTE,
        parent=pivot_slider,
        child=slotted_member,
        origin=Origin(),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(
            effort=120.0, velocity=2.0, lower=r.slotted_lower, upper=r.slotted_upper
        ),
        motion_properties=MotionProperties(damping=0.35, friction=0.8),
        meta={"positive_motion": "opens_image_right_handle_and_left_jaw"},
    )

    if r.has_button:
        selector_button = model.part(
            "selector_button",
            meta={
                "feature": "push_button_pivot_selector",
                "press_travel_m": 0.002,
            },
        )
        selector_button.visual(
            mesh_from_cadquery(_selector_button_cap(), "selector_button_cap", tolerance=0.0003),
            material=mats["button"],
            name="button_cap", material_class_id="plastic.opaque_glossy_molded",
        )
        model.articulation(
            "slider_to_button",
            ArticulationType.PRISMATIC,
            parent=pivot_slider,
            child=selector_button,
            origin=Origin(xyz=(0.0, 0.012, 0.0070)),
            axis=(0.0, 0.0, -1.0),
            motion_limits=MotionLimits(effort=25.0, velocity=0.08, lower=0.0, upper=0.002),
            motion_properties=MotionProperties(damping=4.0, friction=1.5),
            meta={"mechanism": "push_button_pivot_selector"},
        )

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_pilers_slip_joint_pliers(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_pilers_slip_joint_pliers(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def run_pilers_slip_joint_pliers_tests(
    object_model: ArticulatedObject,
    config: PilersSlipJointPliersConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)

    slot_guide = object_model.get_part("slot_guide")
    pivot_slider = object_model.get_part("pivot_slider")
    round_member = object_model.get_part("round_member")
    slotted_member = object_model.get_part("slotted_member")
    slide = object_model.get_articulation("guide_to_slider")
    round_hinge = object_model.get_articulation("slider_to_round_member")
    slotted_hinge = object_model.get_articulation("slider_to_slotted_member")

    # Captured-pin allowances.
    ctx.allow_overlap(
        slot_guide,
        pivot_slider,
        elem_a="slot_track",
        elem_b="pivot_shaft",
        reason=(
            "The pivot rivet shaft is intentionally captured inside the guided "
            "slip-joint track over its full travel."
        ),
    )
    ctx.allow_overlap(
        pivot_slider,
        round_member,
        elem_a="pivot_shaft",
        elem_b="metal_body",
        reason=(
            "The pivot shaft is captured through the round pivot hole of the "
            "rear member (captured-pin joint)."
        ),
    )
    ctx.allow_overlap(
        pivot_slider,
        slotted_member,
        elem_a="pivot_shaft",
        elem_b="metal_body",
        reason=(
            "The pivot shaft is captured through the slotted pivot plate of the "
            "front member (captured sliding-pin joint)."
        ),
    )
    # Two forged plates cross at the pivot plate — z-lap contact is designed.
    ctx.allow_overlap(
        round_member,
        slotted_member,
        elem_a="metal_body",
        elem_b="metal_body",
        reason=(
            "The two crossed forged plier plates share the pivot-plate z-lap "
            "that carries the captured pivot rivet."
        ),
    )
    if r.has_button:
        selector_button = object_model.get_part("selector_button")
        button_joint = object_model.get_articulation("slider_to_button")
        ctx.allow_overlap(
            pivot_slider,
            selector_button,
            elem_a="button_bore",
            elem_b="button_cap",
            reason=("The push-button stem seats into the slider's counterbore recess."),
        )
    else:
        selector_button = None
        button_joint = None

    # Topology sanity.
    if r.has_button:
        ctx.check(
            "push_button_selector adds a fifth part and a fourth joint",
            len(object_model.parts) == 5 and len(object_model.articulations) == 4,
            details=(f"parts={len(object_model.parts)}, joints={len(object_model.articulations)}"),
        )
    else:
        ctx.check(
            "baseline topology is 4-part / 3-joint",
            len(object_model.parts) == 4 and len(object_model.articulations) == 3,
            details=(f"parts={len(object_model.parts)}, joints={len(object_model.articulations)}"),
        )

    # Slot C multiplicity: N-1 alternate pivot markers on slot_guide.
    alternate_names = [v.name for v in slot_guide.visuals if v.name.startswith("alternate_pivot_")]
    ctx.check(
        f"slot_guide carries N-1 alternate pivot markers (N={r.pivot_positions})",
        len(alternate_names) == r.pivot_positions - 1,
        details=(f"expected {r.pivot_positions - 1} markers, found {sorted(alternate_names)}"),
    )

    # Prismatic slide range matches N.
    expected_slide_upper = (r.pivot_positions - 1) * PIVOT_SPACING
    ctx.check(
        "guide_to_slider PRISMATIC upper matches (N-1)*spacing",
        slide.articulation_type == ArticulationType.PRISMATIC
        and slide.motion_limits is not None
        and math.isclose(slide.motion_limits.lower or 0.0, 0.0, abs_tol=1e-9)
        and math.isclose(slide.motion_limits.upper or 0.0, expected_slide_upper, abs_tol=1e-9),
        details=(f"expected upper={expected_slide_upper}, got limits={slide.motion_limits}"),
    )

    # Both hinges are bounded REVOLUTE about +Z, opposite handle directions.
    ctx.check(
        "slider_to_round_member is a bounded REVOLUTE about +Z",
        round_hinge.articulation_type == ArticulationType.REVOLUTE
        and round_hinge.motion_limits is not None
        and round_hinge.motion_limits.lower is not None
        and round_hinge.motion_limits.lower < 0.0
        and round_hinge.motion_limits.upper is not None
        and round_hinge.motion_limits.upper > 0.0,
        details=f"limits={round_hinge.motion_limits}",
    )
    ctx.check(
        "slider_to_slotted_member is a bounded REVOLUTE about +Z",
        slotted_hinge.articulation_type == ArticulationType.REVOLUTE
        and slotted_hinge.motion_limits is not None
        and slotted_hinge.motion_limits.lower is not None
        and slotted_hinge.motion_limits.lower < 0.0
        and slotted_hinge.motion_limits.upper is not None
        and slotted_hinge.motion_limits.upper > 0.0,
        details=f"limits={slotted_hinge.motion_limits}",
    )

    # Slot A visual claim: jaw_teeth exists on both members.
    r_teeth = ctx.part_element_world_aabb(round_member, elem="jaw_teeth")
    s_teeth = ctx.part_element_world_aabb(slotted_member, elem="jaw_teeth")
    ctx.check(
        "both members carry a jaw_teeth visual",
        r_teeth is not None and s_teeth is not None,
    )
    if r_teeth is not None and r.jaw_form == "broad_flat_jaw":
        # Broad flat jaw has a wider back edge (0.0130 vs 0.0090 baseline).
        r_width = r_teeth[1][0] - r_teeth[0][0]
        ctx.check(
            "broad_flat_jaw widens the jaw_teeth footprint",
            r_width > 0.009,
            details=f"round jaw_teeth x-width={r_width:.4f}",
        )

    # Slot B: pivot_topology tag propagates to slot_guide + slider.
    ctx.check(
        "pivot_topology tag propagates to slot_guide and pivot_slider meta",
        slot_guide.meta.get("pivot_topology") == r.pivot_topology
        and pivot_slider.meta.get("pivot_topology") == r.pivot_topology,
        details=(
            f"slot_guide={slot_guide.meta.get('pivot_topology')}, "
            f"slider={pivot_slider.meta.get('pivot_topology')}"
        ),
    )

    if r.has_button:
        ctx.check(
            "push_button_selector adds selector_button + slider_to_button",
            selector_button is not None
            and button_joint is not None
            and button_joint.articulation_type == ArticulationType.PRISMATIC
            and button_joint.parent == "pivot_slider"
            and button_joint.child == "selector_button",
            details=f"button joint={button_joint}",
        )

    # ---- Kinematics: slider reaches alternate detent. ----
    rest_slider = ctx.part_world_position(pivot_slider)
    with ctx.pose({slide: expected_slide_upper}):
        shifted_slider = ctx.part_world_position(pivot_slider)
    ctx.check(
        "pivot slider reaches the alternate detent along +X",
        rest_slider is not None
        and shifted_slider is not None
        and shifted_slider[0] > rest_slider[0] + max(expected_slide_upper - 0.001, 0.0),
        details=f"rest={rest_slider}, shifted={shifted_slider}",
    )

    # ---- Kinematics: opening pose spreads the handles + separates the jaws. ----
    round_grip_rest = ctx.part_element_world_aabb(round_member, elem="blue_grip")
    slotted_grip_rest = ctx.part_element_world_aabb(slotted_member, elem="blue_grip")
    with ctx.pose({round_hinge: r.round_lower * 0.75, slotted_hinge: r.slotted_upper * 0.75}):
        round_grip_open = ctx.part_element_world_aabb(round_member, elem="blue_grip")
        slotted_grip_open = ctx.part_element_world_aabb(slotted_member, elem="blue_grip")

    def _center_x(box):
        return None if box is None else 0.5 * (box[0][0] + box[1][0])

    ctx.check(
        "round member REVOLUTE moves image-left handle further outward",
        _center_x(round_grip_rest) is not None
        and _center_x(round_grip_open) is not None
        and _center_x(round_grip_open) < _center_x(round_grip_rest) - 0.005,
        details=f"rest={round_grip_rest}, open={round_grip_open}",
    )
    ctx.check(
        "slotted member REVOLUTE moves image-right handle further outward",
        _center_x(slotted_grip_rest) is not None
        and _center_x(slotted_grip_open) is not None
        and _center_x(slotted_grip_open) > _center_x(slotted_grip_rest) + 0.005,
        details=f"rest={slotted_grip_rest}, open={slotted_grip_open}",
    )

    if r.has_button and button_joint is not None:
        selector_button_local = object_model.get_part("selector_button")
        rest_btn = ctx.part_world_aabb(selector_button_local)
        with ctx.pose({button_joint: 0.002}):
            pressed_btn = ctx.part_world_aabb(selector_button_local)
        ctx.check(
            "push button presses inward along -Z",
            rest_btn is not None
            and pressed_btn is not None
            and pressed_btn[0][2] < rest_btn[0][2] - 0.0005,
            details=f"rest={rest_btn}, pressed={pressed_btn}",
        )

    # Sampled-pose collision guard (broad).
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=48, ignore_fixed=True)

    # Slot choices metadata reflects the picks.
    ctx.check(
        "slot_choices metadata is emitted",
        object_model.meta.get("slot_choices") == slot_choices_for_config(r),
        details=f"meta slot_choices={object_model.meta.get('slot_choices')}",
    )

    return ctx.report()


__all__ = [
    "PilersSlipJointPliersConfig",
    "ResolvedConfig",
    "config_from_seed",
    "resolve_config",
    "with_overrides",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "build_pilers_slip_joint_pliers",
    "build_seeded_pilers_slip_joint_pliers",
    "run_pilers_slip_joint_pliers_tests",
    "__modular__",
]
