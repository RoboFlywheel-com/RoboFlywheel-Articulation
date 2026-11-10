# SPDX-License-Identifier: Apache-2.0

"""Needle-nose pliers modular template (0611 / pilers_needle_nose_pliers).

Sourced from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/pilers_needle_nose_pliers.md``
and the ``pictureX/0611/Pilers_needle_nose_pliers`` 5-star pool (1 origin_anchor
``needle_nose_pliers_001`` + variants).

Structure (pattern ``mixed``):

* 3-part / 2-joint chain: ``pivot_pin`` (root, captured rivet) +
  ``plier_half_0`` (+x jaw) + ``plier_half_1`` (-x jaw).
* Two REVOLUTE joints ``pivot_to_half_0`` (axis (0,0,-1)) and
  ``pivot_to_half_1`` (axis (0,0,+1)) from pivot_pin to each half.

Slots:

* ``jaw_form`` (4): straight_needle / extra_fine / bent_45 / half_round.
* ``jaw_module`` (3): plain / side_cutter / wire_looping_groove.
* ``return_spring`` (2): none / leaf_spring (adds an inner leaf visual on both halves).
* ``handle_form`` (3): standard / long_reach / guarded_insulated_grip.

``palette_style`` (5): pure material rgba axis; does not enter slot_choices
and does not change topology.
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
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
)

__modular__ = True

# ---------------------------------------------------------------------------
# Constants (from P0 origin_anchor).
# ---------------------------------------------------------------------------
PIVOT_RADIUS = 0.0125
PIVOT_BORE_RADIUS = 0.0034
HALF_THICKNESS = 0.0032
REAR_Z = -0.0034
FRONT_Z = 0.0002
JAW_LENGTH = 0.071
HANDLE_END_Y = -0.124

LONG_JAW_TIP_END = 0.081
LONG_HANDLE_END_Y = -0.169

# ---------------------------------------------------------------------------
# Enum axes
# ---------------------------------------------------------------------------
JawForm = Literal["straight_needle", "extra_fine", "bent_45", "half_round"]
JawModule = Literal["plain", "side_cutter", "wire_looping_groove"]
ReturnSpring = Literal["none", "leaf_spring"]
HandleForm = Literal["standard", "long_reach", "guarded_insulated_grip"]
PaletteStyle = Literal[
    "steel_yellow",
    "matte_black_yellow",
    "chrome_natural",
    "gunmetal_orange",
    "polished_red",
]

JAW_FORMS: tuple[JawForm, ...] = (
    "straight_needle",
    "extra_fine",
    "bent_45",
    "half_round",
)
JAW_MODULES: tuple[JawModule, ...] = ("plain", "side_cutter", "wire_looping_groove")
RETURN_SPRINGS: tuple[ReturnSpring, ...] = ("none", "leaf_spring")
HANDLE_FORMS: tuple[HandleForm, ...] = (
    "standard",
    "long_reach",
    "guarded_insulated_grip",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "steel_yellow",
    "matte_black_yellow",
    "chrome_natural",
    "gunmetal_orange",
    "polished_red",
)

# ---------------------------------------------------------------------------
# Palettes: keys used by builder:
#   forged / tang / grip / rivet / spring
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "steel_yellow": {
        "forged": (0.68, 0.69, 0.68, 1.0),
        "tang": (0.24, 0.25, 0.25, 1.0),
        "grip": (1.00, 0.72, 0.00, 1.0),
        "rivet": (0.76, 0.77, 0.75, 1.0),
        "spring": (0.82, 0.83, 0.82, 1.0),
    },
    "matte_black_yellow": {
        "forged": (0.20, 0.20, 0.22, 1.0),
        "tang": (0.10, 0.10, 0.12, 1.0),
        "grip": (0.98, 0.78, 0.05, 1.0),
        "rivet": (0.50, 0.51, 0.52, 1.0),
        "spring": (0.75, 0.76, 0.78, 1.0),
    },
    "chrome_natural": {
        "forged": (0.85, 0.86, 0.88, 1.0),
        "tang": (0.55, 0.55, 0.58, 1.0),
        "grip": (0.30, 0.30, 0.32, 1.0),
        "rivet": (0.90, 0.90, 0.92, 1.0),
        "spring": (0.80, 0.80, 0.82, 1.0),
    },
    "gunmetal_orange": {
        "forged": (0.42, 0.44, 0.47, 1.0),
        "tang": (0.16, 0.16, 0.18, 1.0),
        "grip": (0.95, 0.42, 0.05, 1.0),
        "rivet": (0.60, 0.62, 0.64, 1.0),
        "spring": (0.78, 0.78, 0.80, 1.0),
    },
    "polished_red": {
        "forged": (0.78, 0.80, 0.82, 1.0),
        "tang": (0.30, 0.30, 0.32, 1.0),
        "grip": (0.82, 0.10, 0.08, 1.0),
        "rivet": (0.90, 0.90, 0.92, 1.0),
        "spring": (0.83, 0.83, 0.84, 1.0),
    },
}


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class PilersNeedleNosePliersConfig:
    jaw_form: JawForm | None = None
    jaw_module: JawModule | None = None
    return_spring: ReturnSpring | None = None
    handle_form: HandleForm | None = None
    palette_style: PaletteStyle = "steel_yellow"
    overall_len_scale: float = 1.0
    jaw_len_scale: float = 1.0
    grip_girth_scale: float = 1.0
    open_angle_scale: float = 1.0
    name: str = "pilers_needle_nose_pliers"


@dataclass(frozen=True)
class ResolvedConfig:
    jaw_form: JawForm
    jaw_module: JawModule
    return_spring: ReturnSpring
    handle_form: HandleForm
    palette_style: PaletteStyle
    overall_len_scale: float
    jaw_len_scale: float
    grip_girth_scale: float
    open_upper: float
    open_lower: float
    name: str


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _pick(v, choices):
    return v if v in choices else choices[0]


def config_from_seed(seed: int) -> PilersNeedleNosePliersConfig:
    rng = random.Random(seed)
    jf = rng.choices(JAW_FORMS, weights=[5, 3, 3, 3], k=1)[0]
    jm = rng.choices(JAW_MODULES, weights=[5, 3, 3], k=1)[0]
    rs = rng.choices(RETURN_SPRINGS, weights=[5, 3], k=1)[0]
    hf = rng.choices(HANDLE_FORMS, weights=[5, 3, 3], k=1)[0]
    return PilersNeedleNosePliersConfig(
        jaw_form=jf,
        jaw_module=jm,
        return_spring=rs,
        handle_form=hf,
        palette_style=rng.choice(PALETTE_STYLES),
        overall_len_scale=round(rng.uniform(0.92, 1.10), 4),
        jaw_len_scale=round(rng.uniform(0.92, 1.08), 4),
        grip_girth_scale=round(rng.uniform(0.92, 1.10), 4),
        open_angle_scale=round(rng.uniform(0.80, 1.20), 4),
        name=f"seeded_pilers_needle_nose_pliers_{seed}",
    )


def resolve_config(
    config: PilersNeedleNosePliersConfig | None = None,
) -> ResolvedConfig:
    cfg = config or PilersNeedleNosePliersConfig()
    jf = _pick(cfg.jaw_form, JAW_FORMS)
    jm = _pick(cfg.jaw_module, JAW_MODULES)
    rs = _pick(cfg.return_spring, RETURN_SPRINGS)
    hf = _pick(cfg.handle_form, HANDLE_FORMS)
    palette = _pick(cfg.palette_style, PALETTE_STYLES)

    overall = _clamp(cfg.overall_len_scale, 0.92, 1.10)
    jaw_len = _clamp(cfg.jaw_len_scale, 0.92, 1.08)
    grip_girth = _clamp(cfg.grip_girth_scale, 0.92, 1.10)
    open_scale = _clamp(cfg.open_angle_scale, 0.80, 1.20)

    # Baseline joint range from P0: lower=-0.025, upper=0.28.
    open_upper = _clamp(0.28 * open_scale, 0.20, 0.34)
    open_lower = _clamp(-0.025 * open_scale, -0.04, -0.015)

    return ResolvedConfig(
        jaw_form=jf,
        jaw_module=jm,
        return_spring=rs,
        handle_form=hf,
        palette_style=palette,
        overall_len_scale=overall,
        jaw_len_scale=jaw_len,
        grip_girth_scale=grip_girth,
        open_upper=open_upper,
        open_lower=open_lower,
        name=cfg.name or "pilers_needle_nose_pliers",
    )


def with_overrides(
    config: PilersNeedleNosePliersConfig, **kwargs: object
) -> PilersNeedleNosePliersConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: PilersNeedleNosePliersConfig | ResolvedConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedConfig) else resolve_config(config)
    return (
        ("jaw_form", r.jaw_form),
        ("jaw_module", r.jaw_module),
        ("return_spring", r.return_spring),
        ("handle_form", r.handle_form),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Geometry helpers (from P0 origin_anchor).
# ---------------------------------------------------------------------------
def _polygon_prism(points, z0: float, thickness: float) -> cq.Workplane:
    return cq.Workplane("XY").polyline(points).close().extrude(thickness).translate((0.0, 0.0, z0))


def _disk_prism(x: float, y: float, radius: float, z0: float, thickness: float):
    return (
        cq.Workplane("XY").center(x, y).circle(radius).extrude(thickness).translate((0.0, 0.0, z0))
    )


def _tapered_path(points, radii, z0: float, thickness: float) -> cq.Workplane:
    body = _disk_prism(points[0][0], points[0][1], radii[0], z0, thickness)
    for index, ((x0, y0), (x1, y1)) in enumerate(zip(points, points[1:])):
        r0 = radii[index]
        r1 = radii[index + 1]
        dx = x1 - x0
        dy = y1 - y0
        length = math.hypot(dx, dy)
        if length < 1e-9:
            continue
        nx = -dy / length
        ny = dx / length
        bridge = _polygon_prism(
            [
                (x0 + nx * r0, y0 + ny * r0),
                (x1 + nx * r1, y1 + ny * r1),
                (x1 - nx * r1, y1 - ny * r1),
                (x0 - nx * r0, y0 - ny * r0),
            ],
            z0,
            thickness,
        )
        body = body.union(bridge)
        body = body.union(_disk_prism(x1, y1, r1, z0, thickness))
    return body


def _cut_pivot_bore(shape: cq.Workplane) -> cq.Workplane:
    cutter = (
        cq.Workplane("XY").circle(PIVOT_BORE_RADIUS).extrude(0.012).translate((0.0, 0.0, -0.006))
    )
    return shape.cut(cutter)


def _build_forged_head(side: int, z0: float) -> cq.Workplane:
    s = float(side)
    jaw = _polygon_prism(
        [
            (s * 0.0014, 0.0030),
            (s * 0.0102, 0.0030),
            (s * 0.0086, 0.0140),
            (s * 0.0065, 0.0310),
            (s * 0.0041, 0.0520),
            (s * 0.0023, JAW_LENGTH),
            (s * 0.0010, JAW_LENGTH),
            (s * 0.00115, 0.0500),
            (s * 0.00125, 0.0260),
            (s * 0.00135, 0.0100),
        ],
        z0,
        HALF_THICKNESS,
    )
    pivot = _disk_prism(0.0, 0.0, PIVOT_RADIUS, z0, HALF_THICKNESS)
    shoulder = _tapered_path(
        [
            (0.0, -0.002),
            (-s * 0.007, -0.013),
            (-s * 0.014, -0.027),
        ],
        [0.0070, 0.0060, 0.0048],
        z0,
        HALF_THICKNESS,
    )
    shape = pivot.union(jaw).union(shoulder)

    # Fine inward-facing notches make the long gripping faces visibly serrated.
    for index in range(10):
        y = 0.013 + index * 0.0037
        inner_x = s * (0.00130 - index * 0.000012)
        notch = _polygon_prism(
            [
                (inner_x - s * 0.0007, y - 0.00045),
                (inner_x + s * 0.00072, y),
                (inner_x - s * 0.0007, y + 0.00045),
            ],
            z0 - 0.0002,
            HALF_THICKNESS + 0.0004,
        )
        shape = shape.cut(notch)
    return _cut_pivot_bore(shape)


def _build_dark_tang(side: int, z0: float, handle_end_y: float) -> cq.Workplane:
    s = float(side)
    tang = _tapered_path(
        [
            (-s * 0.002, -0.006),
            (-s * 0.014, -0.027),
            (-s * 0.027, -0.050),
            (-s * 0.040, -0.078),
            (-s * 0.043, -0.105),
            (-s * 0.037, handle_end_y),
        ],
        [0.0062, 0.0050, 0.0047, 0.0044, 0.0040, 0.0035],
        z0,
        HALF_THICKNESS,
    )
    return _cut_pivot_bore(tang)


# ---------------------------------------------------------------------------
# Slot D handle_form: builds grip solid.
# ---------------------------------------------------------------------------
def _build_grip_standard(side: int, z0: float, girth: float) -> cq.Workplane:
    s = float(side)
    g = girth
    return _tapered_path(
        [
            (-s * 0.016, -0.031),
            (-s * 0.028, -0.052),
            (-s * 0.041, -0.079),
            (-s * 0.044, -0.105),
            (-s * 0.037, HANDLE_END_Y),
        ],
        [0.0067 * g, 0.0070 * g, 0.0071 * g, 0.0067 * g, 0.0060 * g],
        z0 - 0.0008,
        HALF_THICKNESS + 0.0016,
    )


def _build_grip_long_reach(side: int, z0: float, girth: float) -> cq.Workplane:
    s = float(side)
    g = girth
    return _tapered_path(
        [
            (-s * 0.016, -0.031),
            (-s * 0.028, -0.052),
            (-s * 0.041, -0.079),
            (-s * 0.044, -0.105),
            (-s * 0.042, -0.138),
            (-s * 0.037, LONG_HANDLE_END_Y),
        ],
        [0.0067 * g, 0.0070 * g, 0.0071 * g, 0.0067 * g, 0.0062 * g, 0.0055 * g],
        z0 - 0.0008,
        HALF_THICKNESS + 0.0016,
    )


def _build_grip_guarded(side: int, z0: float, girth: float) -> cq.Workplane:
    s = float(side)
    g = girth
    guard = _tapered_path(
        [
            (-s * 0.016, -0.031),
            (-s * 0.020, -0.038),
            (-s * 0.024, -0.044),
        ],
        [0.0085 * g, 0.0093 * g, 0.0080 * g],
        z0 - 0.0014,
        HALF_THICKNESS + 0.0028,
    )
    body = _tapered_path(
        [
            (-s * 0.024, -0.044),
            (-s * 0.028, -0.052),
            (-s * 0.041, -0.079),
            (-s * 0.044, -0.105),
            (-s * 0.037, HANDLE_END_Y),
        ],
        [0.0075 * g, 0.0074 * g, 0.0075 * g, 0.0071 * g, 0.0064 * g],
        z0 - 0.0010,
        HALF_THICKNESS + 0.0020,
    )
    return guard.union(body)


def _handle_end_y(handle: HandleForm) -> float:
    return LONG_HANDLE_END_Y if handle == "long_reach" else HANDLE_END_Y


def _grip_builder(handle: HandleForm):
    return {
        "standard": _build_grip_standard,
        "long_reach": _build_grip_long_reach,
        "guarded_insulated_grip": _build_grip_guarded,
    }[handle]


# ---------------------------------------------------------------------------
# Slot A jaw_form + Slot B jaw_module: build jaw_tip solid.
# Slot A determines base shape; Slot B may replace it entirely (side_cutter
# / wire_looping_groove alter the tip in fundamental ways that swallow the
# fine-form axis). Compatibility: when B in {side_cutter, wire_looping_groove},
# jaw_form still varies overall_length via jaw_len_scale but the tip's local
# form is dominated by module.
# ---------------------------------------------------------------------------
def _jaw_tip_y_extent(handle: HandleForm) -> float:
    """Return jaw_tip max y based on handle_form (long_reach extends jaw tip)."""
    return LONG_JAW_TIP_END if handle == "long_reach" else JAW_LENGTH


def _build_jaw_tip_straight(side: int, z0: float, y_end: float) -> cq.Workplane:
    s = float(side)
    return _polygon_prism(
        [
            (s * 0.0010, 0.0675),
            (s * 0.00245, 0.0675),
            (s * 0.00230, y_end),
            (s * 0.0010, y_end),
        ],
        z0,
        HALF_THICKNESS,
    )


def _build_jaw_tip_extra_fine(side: int, z0: float, y_end: float) -> cq.Workplane:
    s = float(side)
    # Multi-segment taper down to 0.0010 half-width at tip.
    return _polygon_prism(
        [
            (s * 0.0010, 0.063),
            (s * 0.0020, 0.063),
            (s * 0.0017, 0.066),
            (s * 0.0014, 0.069),
            (s * 0.0012, y_end),
            (s * 0.0010, y_end),
        ],
        z0,
        HALF_THICKNESS,
    )


def _build_jaw_tip_bent45(side: int, z0: float, y_end: float) -> cq.Workplane:
    s = float(side)
    bend_start_y = min(0.058, y_end - 0.012)
    bend_length = 0.015
    dy = bend_length * math.cos(math.pi / 4)
    dx = bend_length * math.sin(math.pi / 4) * s
    return _polygon_prism(
        [
            (s * 0.0010, 0.055),
            (s * 0.0025, 0.055),
            (s * 0.0025, bend_start_y),
            (s * 0.0025 + dx, bend_start_y + dy),
            (s * 0.0010 + dx, bend_start_y + dy),
            (s * 0.0010, bend_start_y),
        ],
        z0,
        HALF_THICKNESS,
    )


def _build_jaw_tip_half_round(side: int, z0: float, y_end: float) -> cq.Workplane:
    s = float(side)
    y0, y1 = 0.0675, y_end
    length = y1 - y0
    z_mid = z0 + HALF_THICKNESS * 0.5
    r = HALF_THICKNESS * 0.5
    ix = s * 0.00100

    cyl = cq.Workplane("XY").center(ix, 0.0).circle(r).extrude(length)
    cyl = cyl.rotate((0, 0, 0), (1, 0, 0), -90)
    cyl = cyl.translate((0.0, y0, z_mid))

    cut_cx = ix - s * r * 2.0
    cut_box = (
        cq.Workplane("XY")
        .transformed(offset=(cut_cx, (y0 + y1) * 0.5, z_mid))
        .box(r * 4.0, length * 2.0, HALF_THICKNESS * 3.0)
    )
    return cyl.cut(cut_box)


_JAW_FORM_BUILDERS = {
    "straight_needle": _build_jaw_tip_straight,
    "extra_fine": _build_jaw_tip_extra_fine,
    "bent_45": _build_jaw_tip_bent45,
    "half_round": _build_jaw_tip_half_round,
}


def _build_jaw_tip_side_cutter(side: int, z0: float, y_end: float) -> cq.Workplane:
    s = float(side)
    strip = _polygon_prism(
        [
            (s * 0.0042, 0.006),
            (s * 0.0042, 0.008),
            (s * 0.0038, 0.011),
            (s * 0.0024, 0.018),
            (s * 0.0018, 0.030),
            (s * 0.0016, 0.045),
            (s * 0.0015, 0.058),
            (s * 0.00245, 0.0675),
            (s * 0.00230, y_end),
            (s * 0.0010, y_end),
            (s * 0.0010, 0.0675),
            (s * 0.00115, 0.050),
            (s * 0.00125, 0.026),
            (s * 0.00135, 0.010),
            (s * 0.0014, 0.006),
        ],
        z0,
        HALF_THICKNESS,
    )
    groove = _polygon_prism(
        [
            (s * 0.0014, 0.0074),
            (s * 0.0019, 0.0074),
            (s * 0.0014, 0.0096),
        ],
        z0 - 0.0001,
        HALF_THICKNESS + 0.0002,
    )
    return strip.cut(groove)


def _build_jaw_tip_wire_looping_groove(side: int, z0: float, y_end: float):
    s = float(side)
    tip = _polygon_prism(
        [
            (s * 0.0010, 0.0675),
            (s * 0.00245, 0.0675),
            (s * 0.00230, y_end),
            (s * 0.0010, y_end),
        ],
        z0,
        HALF_THICKNESS,
    )
    groove_y = min(0.0690, y_end - 0.002)
    groove_r = 0.0007
    inner_x = s * 0.0010
    groove_cutter = (
        cq.Workplane("XY")
        .center(inner_x, groove_y)
        .circle(groove_r)
        .extrude(HALF_THICKNESS + 0.0004)
        .translate((0.0, 0.0, z0 - 0.0002))
    )
    return tip.cut(groove_cutter)


def _build_jaw_tip(
    jaw_form: JawForm,
    jaw_module: JawModule,
    side: int,
    z0: float,
    y_end: float,
) -> cq.Workplane:
    """Build the jaw_tip visual solid.

    jaw_module dominates when set (side_cutter / wire_looping_groove). Otherwise
    jaw_form controls the local tip form.
    """
    if jaw_module == "side_cutter":
        return _build_jaw_tip_side_cutter(side, z0, y_end)
    if jaw_module == "wire_looping_groove":
        return _build_jaw_tip_wire_looping_groove(side, z0, y_end)
    return _JAW_FORM_BUILDERS[jaw_form](side, z0, y_end)


# ---------------------------------------------------------------------------
# Slot C return_spring
# ---------------------------------------------------------------------------
def _build_leaf_spring(side: int, z0: float) -> cq.Workplane:
    s = float(side)
    return _tapered_path(
        [
            (-s * 0.002, -0.015),
            (-s * 0.010, -0.033),
            (-s * 0.019, -0.052),
            (-s * 0.025, -0.066),
        ],
        [0.0020, 0.0022, 0.0020, 0.0015],
        z0,
        0.0005,
    )


# ---------------------------------------------------------------------------
# Rivet
# ---------------------------------------------------------------------------
def _build_rivet() -> cq.Workplane:
    shaft = cq.Workplane("XY").circle(0.0028).extrude(0.0068).translate((0.0, 0.0, -0.0034))
    rear_head = cq.Workplane("XY").circle(0.0062).extrude(0.0015).translate((0.0, 0.0, -0.0049))
    front_head = cq.Workplane("XY").circle(0.0066).extrude(0.0015).translate((0.0, 0.0, 0.0034))
    return shaft.union(rear_head).union(front_head)


# ---------------------------------------------------------------------------
# Half emitter
# ---------------------------------------------------------------------------
def _emit_half(
    part,
    r: ResolvedConfig,
    side: int,
    z0: float,
    mats: dict,
) -> None:
    handle_end = _handle_end_y(r.handle_form)
    y_end = _jaw_tip_y_extent(r.handle_form) * r.jaw_len_scale
    # Guard: keep y_end > 0.0675 so jaw_tip stays connected to forged head.
    y_end = max(y_end, 0.0685)

    part.visual(
        mesh_from_cadquery(
            _build_forged_head(side, z0),
            f"needle_pliers_half_{max(side, 0)}_head_{side}",
            tolerance=0.00022,
            angular_tolerance=0.08,
        ),
        material=mats["forged"],
        name="forged_head", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"steel_yellow", "matte_black_yellow", "gunmetal_orange"} else "metal.chrome_polished"),
    )
    part.visual(
        mesh_from_cadquery(
            _build_dark_tang(side, z0, handle_end),
            f"needle_pliers_half_{max(side, 0)}_tang_{side}",
            tolerance=0.00028,
            angular_tolerance=0.08,
        ),
        material=mats["tang"],
        name="handle_tang", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"steel_yellow", "matte_black_yellow", "gunmetal_orange", "polished_red"} else "metal.steel_bare"),
    )
    grip_builder = _grip_builder(r.handle_form)
    part.visual(
        mesh_from_cadquery(
            grip_builder(side, z0, r.grip_girth_scale),
            f"needle_pliers_half_{max(side, 0)}_grip_{side}",
            tolerance=0.00028,
            angular_tolerance=0.08,
        ),
        material=mats["grip"],
        name="grip", material_class_id="plastic.opaque_glossy_molded",
    )
    part.visual(
        mesh_from_cadquery(
            _build_jaw_tip(r.jaw_form, r.jaw_module, side, z0, y_end),
            f"needle_pliers_half_{max(side, 0)}_tip_{side}",
            tolerance=0.00018,
            angular_tolerance=0.08,
        ),
        material=mats["forged"],
        name="jaw_tip", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"steel_yellow", "matte_black_yellow", "gunmetal_orange"} else "metal.chrome_polished"),
    )
    if r.return_spring == "leaf_spring":
        part.visual(
            mesh_from_cadquery(
                _build_leaf_spring(side, z0),
                f"needle_pliers_half_{max(side, 0)}_leaf_{side}",
                tolerance=0.00020,
                angular_tolerance=0.08,
            ),
            material=mats["spring"],
            name="leaf_spring", material_class_id="metal.steel_bare",
        )


# ---------------------------------------------------------------------------
# Builders
# ---------------------------------------------------------------------------
def build_pilers_needle_nose_pliers(
    config: PilersNeedleNosePliersConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    palette = PALETTES[r.palette_style]
    mats = {
        key: model.material(f"pnn_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in palette.items()
    }

    pivot_pin = model.part(
        "pivot_pin",
        meta={"role": "captured_rivet", "axis": "z"},
    )
    pivot_pin.visual(
        mesh_from_cadquery(
            _build_rivet(),
            "needle_pliers_pivot_rivet",
            tolerance=0.00025,
            angular_tolerance=0.08,
        ),
        material=mats["rivet"],
        name="rivet", material_class_id=("metal.steel_bare" if r.palette_style in {"steel_yellow", "matte_black_yellow", "gunmetal_orange"} else "metal.chrome_polished"),
    )

    half_0 = model.part(
        "plier_half_0",
        meta={
            "serration_count": 10,
            "jaw_side": "positive_x",
            "handle_side": "negative_x",
        },
    )
    _emit_half(half_0, r, side=+1, z0=REAR_Z, mats=mats)

    half_1 = model.part(
        "plier_half_1",
        meta={
            "serration_count": 10,
            "jaw_side": "negative_x",
            "handle_side": "positive_x",
        },
    )
    _emit_half(half_1, r, side=-1, z0=FRONT_Z, mats=mats)

    model.articulation(
        "pivot_to_half_0",
        ArticulationType.REVOLUTE,
        parent=pivot_pin,
        child=half_0,
        origin=Origin(),
        axis=(0.0, 0.0, -1.0),
        motion_limits=MotionLimits(
            effort=65.0,
            velocity=2.5,
            lower=r.open_lower,
            upper=r.open_upper,
        ),
        meta={"positive_motion": "opens positive-x jaw outward"},
    )
    model.articulation(
        "pivot_to_half_1",
        ArticulationType.REVOLUTE,
        parent=pivot_pin,
        child=half_1,
        origin=Origin(),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(
            effort=65.0,
            velocity=2.5,
            lower=r.open_lower,
            upper=r.open_upper,
        ),
        meta={"positive_motion": "opens negative-x jaw outward"},
    )

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_pilers_needle_nose_pliers(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_pilers_needle_nose_pliers(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def run_pilers_needle_nose_pliers_tests(
    object_model: ArticulatedObject,
    config: PilersNeedleNosePliersConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    pivot_pin = object_model.get_part("pivot_pin")
    half_0 = object_model.get_part("plier_half_0")
    half_1 = object_model.get_part("plier_half_1")
    joint_0 = object_model.get_articulation("pivot_to_half_0")
    joint_1 = object_model.get_articulation("pivot_to_half_1")

    # Captured-rivet allow-overlap between pivot pin and each half.
    ctx.allow_overlap(
        pivot_pin,
        half_0,
        reason=(
            "The captured rivet pin threads through the plier_half_0 pivot hub;"
            " the hub bore is intentionally slightly smaller than the shaft."
        ),
    )
    ctx.allow_overlap(
        pivot_pin,
        half_1,
        reason=(
            "The captured rivet pin threads through the plier_half_1 pivot hub;"
            " the hub bore is intentionally slightly smaller than the shaft."
        ),
    )
    # Two forged halves overlap at the pivot hub z-lap.
    ctx.allow_overlap(
        half_0,
        half_1,
        reason=(
            "The two forged plier halves are z-lapped at the pivot hub, which is"
            " the pliers' central captured-pin joint."
        ),
    )

    # Topology
    ctx.check(
        "3-part / 2-joint chain",
        len(object_model.parts) == 3 and len(object_model.articulations) == 2,
        details=(
            f"parts={[p.name for p in object_model.parts]}, "
            f"joints={[j.name for j in object_model.articulations]}"
        ),
    )
    ctx.check(
        "pivot_pin is the only root",
        [p.name for p in object_model.root_parts()] == ["pivot_pin"],
    )
    ctx.check(
        "opposed pivot axes",
        tuple(joint_0.axis) == (0.0, 0.0, -1.0) and tuple(joint_1.axis) == (0.0, 0.0, 1.0),
    )
    lm0 = joint_0.motion_limits
    lm1 = joint_1.motion_limits
    ctx.check(
        "revolute limits realistic",
        lm0 is not None
        and lm1 is not None
        and lm0.lower < 0.0 < lm0.upper
        and lm1.lower < 0.0 < lm1.upper,
        details=f"lm0={lm0}, lm1={lm1}",
    )

    # Rivet retains halves.
    ctx.expect_contact(
        pivot_pin,
        half_0,
        elem_a="rivet",
        elem_b="forged_head",
        contact_tol=0.0005,
        name="rear half is retained by rivet head",
    )
    ctx.expect_contact(
        pivot_pin,
        half_1,
        elem_a="rivet",
        elem_b="forged_head",
        contact_tol=0.0005,
        name="front half is retained by rivet head",
    )

    # Slot A / B geometry claims.
    tip0 = ctx.part_element_world_aabb(half_0, elem="jaw_tip")
    tip1 = ctx.part_element_world_aabb(half_1, elem="jaw_tip")
    ctx.check(
        "jaw_tip visuals present on both halves",
        tip0 is not None and tip1 is not None,
    )
    if tip0 is not None and r.jaw_module == "side_cutter":
        # Side cutter widens near the pivot: strip x extent > 0.003 vs baseline
        # straight tip ~0.0014 wide.
        tip_width_x = tip0[1][0] - tip0[0][0]
        ctx.check(
            "side_cutter jaw_tip has widened base near pivot",
            tip_width_x > 0.0028,
            details=f"tip0 x-width={tip_width_x:.4f}",
        )
    if tip0 is not None and r.jaw_form == "bent_45" and r.jaw_module == "plain":
        # bent tip extends outward on +x.
        ctx.check(
            "bent_45 jaw_tip extends outward on positive-x half",
            tip0[1][0] > 0.007,
            details=f"tip0 max_x={tip0[1][0]:.4f}",
        )

    # Slot D geometry claim.
    grip0 = ctx.part_element_world_aabb(half_0, elem="grip")
    if grip0 is not None and r.handle_form == "long_reach":
        ctx.check(
            "long_reach grip reaches further along -y",
            grip0[0][1] < -0.160,
            details=f"grip0 min_y={grip0[0][1]:.4f}",
        )
    if grip0 is not None and r.handle_form == "guarded_insulated_grip":
        # Guard flare near y ~ -0.038 widens grip: max half-width > 0.008.
        gw = grip0[1][0] - grip0[0][0]
        ctx.check(
            "guarded_insulated_grip shows a wider flared section",
            gw > 0.014,
            details=f"grip0 x-width={gw:.4f}",
        )

    # Slot C geometry claim.
    if r.return_spring == "leaf_spring":
        leaf0 = ctx.part_element_world_aabb(half_0, elem="leaf_spring")
        leaf1 = ctx.part_element_world_aabb(half_1, elem="leaf_spring")
        ctx.check(
            "leaf_spring visuals present on both halves",
            leaf0 is not None and leaf1 is not None,
        )

    # Kinematics: each pivot independently opens its own half's jaw_tip.
    def elem_cx(part, elem: str):
        box = ctx.part_element_world_aabb(part, elem=elem)
        if box is None:
            return None
        return 0.5 * (box[0][0] + box[1][0])

    half_0_rest = elem_cx(half_0, "jaw_tip")
    half_1_rest = elem_cx(half_1, "jaw_tip")
    # Use the joint's actual upper limit (scaled by open_angle_scale) so seeds
    # with reduced angle range still open enough to register the motion check.
    open_pose = min(lm0.upper if lm0 else 0.25, 0.25)
    with ctx.pose({joint_0: open_pose}):
        half_0_open = elem_cx(half_0, "jaw_tip")
        half_1_stationary = elem_cx(half_1, "jaw_tip")
    with ctx.pose({joint_1: open_pose}):
        half_1_open = elem_cx(half_1, "jaw_tip")
        half_0_stationary = elem_cx(half_0, "jaw_tip")

    ctx.check(
        "positive pivot_to_half_0 opens positive-x jaw",
        half_0_rest is not None and half_0_open is not None and half_0_open > half_0_rest + 0.006,
        details=f"rest={half_0_rest}, open={half_0_open}",
    )
    ctx.check(
        "half_1 stays still when only joint_0 moves",
        half_1_rest is not None
        and half_1_stationary is not None
        and abs(half_1_stationary - half_1_rest) < 0.0001,
    )
    ctx.check(
        "positive pivot_to_half_1 opens negative-x jaw",
        half_1_rest is not None and half_1_open is not None and half_1_open < half_1_rest - 0.006,
        details=f"rest={half_1_rest}, open={half_1_open}",
    )
    ctx.check(
        "half_0 stays still when only joint_1 moves",
        half_0_rest is not None
        and half_0_stationary is not None
        and abs(half_0_stationary - half_0_rest) < 0.0001,
    )

    ctx.check(
        "slot_choices metadata is emitted",
        object_model.meta.get("slot_choices") == slot_choices_for_config(r),
    )

    return ctx.report()


__all__ = [
    "PilersNeedleNosePliersConfig",
    "ResolvedConfig",
    "config_from_seed",
    "resolve_config",
    "with_overrides",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "build_pilers_needle_nose_pliers",
    "build_seeded_pilers_needle_nose_pliers",
    "run_pilers_needle_nose_pliers_tests",
    "__modular__",
]
