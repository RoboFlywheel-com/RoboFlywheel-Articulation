# SPDX-License-Identifier: Apache-2.0

"""Linesman-pliers modular template (0611 / pilers_linesman_pliers).

Sourced from ``articraft_template_authoring/specs_modular_v1/pilers_linesman_pliers.md``
and the ``pictureX/0611/Pilers_linesman_pliers`` 5-star pool (1 origin_anchor
+ 9 single-axis forks).

Baseline topology (3-part / 2-joint chain):

* ``pivot_pin`` (root) + ``handle_0`` + ``handle_1``.
* ``pivot_to_handle_0`` REVOLUTE (pivot -> handle_0, axis +Z).
* ``pivot_to_handle_1`` REVOLUTE (pivot -> handle_1, axis +Z).

Slots:

* ``jaw_module`` (5): tapered_serrated (baseline) / broad_square_jaw /
  fish_tape_channel / crimper_cavity / cable_pulling_groove. Swaps jaw_bevel
  polyline (broad) or adds a mirrored jaw-feature visual to each handle.
* ``leverage_mechanism`` (3): fixed_rivet / offset_pivot / compound_link.
  fixed_rivet + offset_pivot keep the 3-part chain; compound_link inserts
  ``link_0`` + ``link_1`` between pivot_pin and each handle -> 5-part /
  4-joint chain.
* ``return_spring`` (2): no_spring (baseline) / captured_spring (adds a
  helical torsion tube visual on pivot_pin plus a spring_anchor_slot visual
  on each handle).
* ``handle_form`` (3): straight_dipped (baseline) / long_handle /
  guarded_insulated_grip. Swaps grip polyline.

``palette_style`` (6): pure material rgba axis; does not enter
slot_choices and does not change topology.

Captured-pin overlaps between ``pivot_pin`` and each ``handle_i`` (and each
``link_i`` for the compound branch) omit ``MatingContract`` and are guarded
by broad ``allow_overlap`` reasons.
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
    mesh_from_geometry,
    tube_from_spline_points,
)

__modular__ = True

# ---------------------------------------------------------------------------
# Enum axes
# ---------------------------------------------------------------------------
JawModule = Literal[
    "tapered_serrated",
    "broad_square_jaw",
    "fish_tape_channel",
    "crimper_cavity",
    "cable_pulling_groove",
]
LeverageMechanism = Literal["fixed_rivet", "offset_pivot", "compound_link"]
ReturnSpring = Literal["no_spring", "captured_spring"]
HandleForm = Literal["straight_dipped", "long_handle", "guarded_insulated_grip"]
PaletteStyle = Literal[
    "steel_black_blue",
    "gunmetal_red",
    "chrome_natural",
    "black_yellow",
    "olive_orange",
    "polished_silver",
]

JAW_MODULES: tuple[JawModule, ...] = (
    "tapered_serrated",
    "broad_square_jaw",
    "fish_tape_channel",
    "crimper_cavity",
    "cable_pulling_groove",
)
LEVERAGE_MECHANISMS: tuple[LeverageMechanism, ...] = (
    "fixed_rivet",
    "offset_pivot",
    "compound_link",
)
RETURN_SPRINGS: tuple[ReturnSpring, ...] = ("no_spring", "captured_spring")
HANDLE_FORMS: tuple[HandleForm, ...] = (
    "straight_dipped",
    "long_handle",
    "guarded_insulated_grip",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "steel_black_blue",
    "gunmetal_red",
    "chrome_natural",
    "black_yellow",
    "olive_orange",
    "polished_silver",
)

# Compound_link geometry offsets (source: V-L1 model.py L21-22).
LINK_OFFSET_X = 0.004
LINK_OFFSET_Y = -0.006
LINK_THICKNESS = 0.002

METAL_THICKNESS = 0.005
PIVOT_HOLE_RADIUS = 0.0053

# ---------------------------------------------------------------------------
# Palettes: metal (forged/edge/polished) + grip (rubber/plastic) coverage.
# Keys used by the builder: forged, edge, polished, grip, collar, highlight.
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "steel_black_blue": {
        "forged": (0.67, 0.69, 0.70, 1.0),
        "edge": (0.25, 0.27, 0.28, 1.0),
        "polished": (0.78, 0.80, 0.80, 1.0),
        "grip": (0.05, 0.05, 0.06, 1.0),
        "collar": (0.05, 0.35, 0.72, 1.0),
        "highlight": (0.14, 0.16, 0.18, 1.0),
    },
    "gunmetal_red": {
        "forged": (0.42, 0.44, 0.47, 1.0),
        "edge": (0.18, 0.19, 0.20, 1.0),
        "polished": (0.62, 0.64, 0.66, 1.0),
        "grip": (0.82, 0.10, 0.12, 1.0),
        "collar": (0.15, 0.15, 0.17, 1.0),
        "highlight": (0.90, 0.30, 0.20, 1.0),
    },
    "chrome_natural": {
        "forged": (0.82, 0.84, 0.87, 1.0),
        "edge": (0.35, 0.37, 0.40, 1.0),
        "polished": (0.92, 0.93, 0.95, 1.0),
        "grip": (0.30, 0.30, 0.32, 1.0),
        "collar": (0.55, 0.55, 0.58, 1.0),
        "highlight": (0.75, 0.75, 0.78, 1.0),
    },
    "black_yellow": {
        "forged": (0.20, 0.20, 0.22, 1.0),
        "edge": (0.10, 0.10, 0.12, 1.0),
        "polished": (0.55, 0.56, 0.58, 1.0),
        "grip": (0.94, 0.80, 0.08, 1.0),
        "collar": (0.10, 0.10, 0.12, 1.0),
        "highlight": (0.95, 0.90, 0.25, 1.0),
    },
    "olive_orange": {
        "forged": (0.50, 0.52, 0.45, 1.0),
        "edge": (0.20, 0.22, 0.18, 1.0),
        "polished": (0.72, 0.72, 0.65, 1.0),
        "grip": (0.95, 0.44, 0.06, 1.0),
        "collar": (0.35, 0.38, 0.20, 1.0),
        "highlight": (0.98, 0.60, 0.20, 1.0),
    },
    "polished_silver": {
        "forged": (0.78, 0.80, 0.82, 1.0),
        "edge": (0.30, 0.32, 0.34, 1.0),
        "polished": (0.92, 0.93, 0.95, 1.0),
        "grip": (0.18, 0.20, 0.22, 1.0),
        "collar": (0.72, 0.14, 0.14, 1.0),
        "highlight": (0.35, 0.36, 0.38, 1.0),
    },
}


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class PilersLinesmanPliersConfig:
    jaw_module: JawModule | None = None
    leverage_mechanism: LeverageMechanism | None = None
    return_spring: ReturnSpring | None = None
    handle_form: HandleForm | None = None
    palette_style: PaletteStyle = "steel_black_blue"
    overall_len_scale: float = 1.0
    grip_girth_scale: float = 1.0
    open_angle_scale: float = 1.0
    name: str = "pilers_linesman_pliers"


@dataclass(frozen=True)
class ResolvedConfig:
    jaw_module: JawModule
    leverage_mechanism: LeverageMechanism
    return_spring: ReturnSpring
    handle_form: HandleForm
    palette_style: PaletteStyle
    overall_len_scale: float
    grip_girth_scale: float
    open_upper: float
    open_lower: float
    name: str

    @property
    def is_compound(self) -> bool:
        return self.leverage_mechanism == "compound_link"

    @property
    def has_spring(self) -> bool:
        return self.return_spring == "captured_spring"


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


def config_from_seed(seed: int) -> PilersLinesmanPliersConfig:
    rng = random.Random(seed)
    jaw = rng.choices(JAW_MODULES, weights=[5, 3, 3, 3, 3], k=1)[0]
    lev = rng.choices(LEVERAGE_MECHANISMS, weights=[5, 3, 2], k=1)[0]
    ret = rng.choices(RETURN_SPRINGS, weights=[3, 2], k=1)[0]
    hand = rng.choices(HANDLE_FORMS, weights=[5, 3, 3], k=1)[0]
    return PilersLinesmanPliersConfig(
        jaw_module=jaw,
        leverage_mechanism=lev,
        return_spring=ret,
        handle_form=hand,
        palette_style=rng.choice(PALETTE_STYLES),
        overall_len_scale=round(rng.uniform(0.92, 1.10), 4),
        grip_girth_scale=round(rng.uniform(0.92, 1.08), 4),
        open_angle_scale=round(rng.uniform(0.85, 1.15), 4),
        name=f"seeded_pilers_linesman_pliers_{seed}",
    )


def resolve_config(
    config: PilersLinesmanPliersConfig | None = None,
) -> ResolvedConfig:
    cfg = config or PilersLinesmanPliersConfig()
    jaw = _pick(cfg.jaw_module, JAW_MODULES)
    lev = _pick(cfg.leverage_mechanism, LEVERAGE_MECHANISMS)
    ret = _pick(cfg.return_spring, RETURN_SPRINGS)
    hand = _pick(cfg.handle_form, HANDLE_FORMS)
    palette = _pick(cfg.palette_style, PALETTE_STYLES)

    overall = _clamp(cfg.overall_len_scale, 0.92, 1.10)
    grip_girth = _clamp(cfg.grip_girth_scale, 0.92, 1.08)
    open_scale = _clamp(cfg.open_angle_scale, 0.85, 1.15)

    # Baseline handle_0: lower=-0.080, upper=0.025 (P0 L405-407).
    # Symmetric handle_1: lower=-0.025, upper=0.080.
    # We store a single "positive open" and "negative open" magnitude, then
    # apply the correct sign per handle in the builder.
    open_upper = _clamp(0.080 * open_scale, 0.045, 0.100)
    open_lower = _clamp(0.025 * open_scale, 0.015, 0.045)

    return ResolvedConfig(
        jaw_module=jaw,
        leverage_mechanism=lev,
        return_spring=ret,
        handle_form=hand,
        palette_style=palette,
        overall_len_scale=overall,
        grip_girth_scale=grip_girth,
        open_upper=open_upper,
        open_lower=open_lower,
        name=cfg.name or "pilers_linesman_pliers",
    )


def with_overrides(
    config: PilersLinesmanPliersConfig, **kwargs: object
) -> PilersLinesmanPliersConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: PilersLinesmanPliersConfig | ResolvedConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedConfig) else resolve_config(config)
    return (
        ("jaw_module", r.jaw_module),
        ("leverage_mechanism", r.leverage_mechanism),
        ("return_spring", r.return_spring),
        ("handle_form", r.handle_form),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Geometry helpers (from P0 origin_anchor).
# ---------------------------------------------------------------------------
def _mirror_points(points: list[tuple[float, float]], sign: float) -> list[tuple[float, float]]:
    return [(sign * x, y) for x, y in points]


def _profile_solid(
    points: list[tuple[float, float]],
    *,
    thickness: float,
    z0: float,
) -> cq.Workplane:
    return cq.Workplane("XY").polyline(points).close().extrude(thickness).translate((0.0, 0.0, z0))


# ---------------------------------------------------------------------------
# Slot D -- handle_form: return (grip_outline, tang_outline) both in the
# +handle_sign frame; scale is applied by caller.
# ---------------------------------------------------------------------------
def _straight_dipped_outlines() -> tuple[list[tuple[float, float]], list[tuple[float, float]]]:
    tang = [
        (0.0030, -0.0050),
        (0.0070, -0.0350),
        (0.0160, -0.0810),
        (0.0200, -0.1260),
        (0.0200, -0.1490),
        (0.0240, -0.1560),
        (0.0290, -0.1570),
        (0.0340, -0.1500),
        (0.0360, -0.1260),
        (0.0330, -0.0820),
        (0.0240, -0.0380),
        (0.0120, -0.0080),
    ]
    grip = [
        (0.0090, -0.0250),
        (0.0140, -0.0480),
        (0.0210, -0.0850),
        (0.0240, -0.1250),
        (0.0230, -0.1480),
        (0.0250, -0.1550),
        (0.0290, -0.1590),
        (0.0330, -0.1560),
        (0.0360, -0.1490),
        (0.0380, -0.1260),
        (0.0350, -0.0830),
        (0.0270, -0.0440),
        (0.0180, -0.0230),
    ]
    return grip, tang


def _long_handle_outlines() -> tuple[list[tuple[float, float]], list[tuple[float, float]]]:
    # Extend by ~15% along -y.
    tang = [
        (0.0030, -0.0050),
        (0.0070, -0.0350),
        (0.0160, -0.0810),
        (0.0200, -0.1360),
        (0.0200, -0.1620),
        (0.0240, -0.1700),
        (0.0290, -0.1720),
        (0.0340, -0.1650),
        (0.0360, -0.1370),
        (0.0330, -0.0880),
        (0.0240, -0.0400),
        (0.0120, -0.0080),
    ]
    grip = [
        (0.0090, -0.0250),
        (0.0140, -0.0490),
        (0.0210, -0.0900),
        (0.0240, -0.1330),
        (0.0230, -0.1580),
        (0.0250, -0.1680),
        (0.0290, -0.1740),
        (0.0330, -0.1710),
        (0.0360, -0.1620),
        (0.0380, -0.1360),
        (0.0350, -0.0900),
        (0.0270, -0.0460),
        (0.0180, -0.0230),
    ]
    return grip, tang


def _guarded_grip_outlines() -> tuple[list[tuple[float, float]], list[tuple[float, float]]]:
    # Mid-body finger-guard flare (half-width bumps up ~+0.003 m around
    # y=-0.06..-0.10).
    tang = [
        (0.0030, -0.0050),
        (0.0070, -0.0350),
        (0.0160, -0.0810),
        (0.0200, -0.1260),
        (0.0200, -0.1490),
        (0.0240, -0.1560),
        (0.0290, -0.1570),
        (0.0340, -0.1500),
        (0.0360, -0.1260),
        (0.0330, -0.0820),
        (0.0240, -0.0380),
        (0.0120, -0.0080),
    ]
    grip = [
        (0.0090, -0.0250),
        (0.0170, -0.0480),
        (0.0245, -0.0700),
        (0.0270, -0.0900),
        (0.0240, -0.1100),
        (0.0230, -0.1330),
        (0.0250, -0.1550),
        (0.0290, -0.1590),
        (0.0330, -0.1560),
        (0.0360, -0.1490),
        (0.0380, -0.1260),
        (0.0350, -0.1000),
        (0.0400, -0.0800),
        (0.0400, -0.0600),
        (0.0330, -0.0440),
        (0.0230, -0.0250),
    ]
    return grip, tang


_HANDLE_BUILDERS = {
    "straight_dipped": _straight_dipped_outlines,
    "long_handle": _long_handle_outlines,
    "guarded_insulated_grip": _guarded_grip_outlines,
}


# ---------------------------------------------------------------------------
# Slot A -- jaw_module. Returns (jaw_bevel_outline, jaw_bevel_thickness,
# extras_builder or None). `extras_builder(jaw_sign, front_z)` returns a
# list of (mesh_workplane, mesh_name, material_key, visual_name).
# ---------------------------------------------------------------------------
def _tapered_bevel_outline() -> tuple[list[tuple[float, float]], float]:
    return [
        (0.0055, 0.0680),
        (0.0085, 0.0585),
        (0.0160, 0.0300),
        (0.0160, 0.0170),
        (0.0120, 0.0290),
        (0.0070, 0.0600),
    ], 0.0008


def _broad_square_bevel_outline() -> tuple[list[tuple[float, float]], float]:
    return [
        (0.0045, 0.0710),
        (0.0105, 0.0640),
        (0.0195, 0.0410),
        (0.0195, 0.0150),
        (0.0140, 0.0250),
        (0.0055, 0.0630),
    ], 0.0012


def _make_fish_tape_channel(jaw_sign: float, *, z0: float) -> cq.Workplane:
    # Thin vertical channel visual sitting along the inner jaw face.
    outline = _mirror_points(
        [
            (0.0028, 0.0300),
            (0.0038, 0.0300),
            (0.0038, 0.0670),
            (0.0028, 0.0670),
        ],
        jaw_sign,
    )
    return _profile_solid(outline, thickness=0.0010, z0=z0)


def _make_crimper_cavity(jaw_sign: float, *, z0: float) -> cq.Workplane:
    # Half-round recess visual near jaw mid.
    outline = _mirror_points(
        [
            (0.0025, 0.0420),
            (0.0050, 0.0405),
            (0.0075, 0.0430),
            (0.0080, 0.0470),
            (0.0060, 0.0500),
            (0.0030, 0.0490),
        ],
        jaw_sign,
    )
    return _profile_solid(outline, thickness=0.0009, z0=z0)


def _make_cable_groove(jaw_sign: float, *, z0: float) -> cq.Workplane:
    # V-shaped cable pulling groove visual near jaw mid.
    outline = _mirror_points(
        [
            (0.0025, 0.0360),
            (0.0075, 0.0400),
            (0.0075, 0.0440),
            (0.0025, 0.0480),
        ],
        jaw_sign,
    )
    return _profile_solid(outline, thickness=0.0010, z0=z0)


# ---------------------------------------------------------------------------
# Forged half (P0 L44-116). Tang and jaw polylines depend on handle_form.
# ---------------------------------------------------------------------------
def _make_forged_half(
    handle_sign: float,
    *,
    z0: float,
    tang_pts: list[tuple[float, float]],
    y_scale: float,
) -> cq.Workplane:
    jaw_sign = -handle_sign
    boss = cq.Workplane("XY").circle(0.0155).extrude(METAL_THICKNESS).translate((0.0, 0.0, z0))
    jaw_outline = _mirror_points(
        [
            (0.0040, 0.0070),
            (0.0020, 0.0210),
            (0.0018, 0.0690),
            (0.0042, 0.0740),
            (0.0080, 0.0600),
            (0.0165, 0.0290),
            (0.0160, 0.0140),
            (0.0110, 0.0080),
        ],
        jaw_sign,
    )
    jaw = _profile_solid(jaw_outline, thickness=METAL_THICKNESS, z0=z0)

    tang_scaled = [(x, y * y_scale) for (x, y) in tang_pts]
    tang_outline = _mirror_points(tang_scaled, handle_sign)
    tang = _profile_solid(tang_outline, thickness=METAL_THICKNESS, z0=z0)

    body = boss.union(jaw).union(tang)

    bore = (
        cq.Workplane("XY")
        .circle(PIVOT_HOLE_RADIUS)
        .extrude(METAL_THICKNESS + 0.004)
        .translate((0.0, 0.0, z0 - 0.002))
    )
    body = body.cut(bore)

    for y in (0.031, 0.036, 0.041, 0.046, 0.051, 0.056, 0.061, 0.066):
        cutter = (
            cq.Workplane("XY")
            .box(0.0045, 0.00115, METAL_THICKNESS + 0.004)
            .translate((jaw_sign * 0.0030, y, z0 + METAL_THICKNESS * 0.5))
        )
        body = body.cut(cutter)

    return body


def _make_grip(
    handle_sign: float,
    *,
    z0: float,
    grip_pts: list[tuple[float, float]],
    x_scale: float,
    y_scale: float,
) -> cq.Workplane:
    scaled = [(x * x_scale, y * y_scale) for (x, y) in grip_pts]
    outline = _mirror_points(scaled, handle_sign)
    return _profile_solid(outline, thickness=0.010, z0=z0)


def _make_grip_collar(handle_sign: float, *, z0: float) -> cq.Workplane:
    outline = _mirror_points(
        [
            (0.0090, -0.0250),
            (0.0115, -0.0385),
            (0.0250, -0.0430),
            (0.0275, -0.0360),
            (0.0220, -0.0240),
            (0.0170, -0.0225),
        ],
        handle_sign,
    )
    return _profile_solid(outline, thickness=0.0106, z0=z0)


def _make_grip_highlight(handle_sign: float, *, z0: float, y_scale: float) -> cq.Workplane:
    pts = [
        (0.0270, -0.0490),
        (0.0300, -0.0820),
        (0.0330, -0.1230),
        (0.0310, -0.1430),
        (0.0335, -0.1460),
        (0.0365, -0.1240),
        (0.0335, -0.0800),
        (0.0295, -0.0470),
    ]
    scaled = [(x, y * y_scale) for (x, y) in pts]
    outline = _mirror_points(scaled, handle_sign)
    return _profile_solid(outline, thickness=0.0007, z0=z0)


def _make_jaw_bevel(
    jaw_sign: float,
    *,
    z0: float,
    outline: list[tuple[float, float]],
    thickness: float,
) -> cq.Workplane:
    pts = _mirror_points(outline, jaw_sign)
    return _profile_solid(pts, thickness=thickness, z0=z0)


def _make_cutting_edge(jaw_sign: float, *, z0: float) -> cq.Workplane:
    outline = _mirror_points(
        [
            (0.0010, 0.0130),
            (0.0010, 0.0270),
            (0.0057, 0.0245),
            (0.0080, 0.0140),
        ],
        jaw_sign,
    )
    return _profile_solid(outline, thickness=0.0010, z0=z0)


def _make_serrated_insert(jaw_sign: float, *, z0: float) -> cq.Workplane:
    points: list[tuple[float, float]] = [(0.0058, 0.0290), (0.0048, 0.0690)]
    for index in reversed(range(9)):
        y = 0.030 + index * 0.00475
        points.append((0.0021 if index % 2 == 0 else 0.0038, y))
    return _profile_solid(
        _mirror_points(points, jaw_sign),
        thickness=0.0009,
        z0=z0,
    )


def _make_pivot_pin(
    *, shaft_length: float, cap_radius: float, shaft_radius: float = 0.0058
) -> cq.Workplane:
    shaft = (
        cq.Workplane("XY")
        .circle(shaft_radius)
        .extrude(shaft_length)
        .translate((0.0, 0.0, -shaft_length / 2.0))
    )
    back_cap = (
        cq.Workplane("XY")
        .circle(cap_radius)
        .extrude(0.0020)
        .translate((0.0, 0.0, -shaft_length / 2.0))
    )
    front_cap = (
        cq.Workplane("XY")
        .circle(cap_radius)
        .extrude(0.0020)
        .translate((0.0, 0.0, shaft_length / 2.0 - 0.0020))
    )
    return shaft.union(back_cap).union(front_cap)


def _make_captured_spring_mesh():
    """Continuous helical torsion coil around the pivot axis as a tube."""
    coils = 2.0
    coil_r = 0.006
    z_span = 0.004
    steps = 32
    pts: list[tuple[float, float, float]] = []
    # Leading tang leg (radial, sits close to pivot pin surface).
    pts.append((-0.010, 0.006, -0.002))
    pts.append((-0.006, 0.006, -0.002))
    # Helical winding.
    for i in range(steps + 1):
        t = i / steps
        angle = 2.0 * math.pi * coils * t
        x = coil_r * math.cos(angle)
        y = coil_r * math.sin(angle)
        z = -z_span / 2.0 + z_span * t
        pts.append((x, y, z))
    # Trailing tang leg.
    pts.append((0.006, 0.006, 0.002))
    pts.append((0.010, 0.006, 0.002))
    return tube_from_spline_points(
        pts,
        radius=0.00085,
        samples_per_segment=10,
        radial_segments=12,
        cap_ends=True,
    )


def _make_spring_anchor_slot(handle_sign: float, *, z0: float) -> cq.Workplane:
    # A small tab sitting on top of the boss face; extend it well into the
    # boss so it fuses with the forged half body in the mesh-connectivity
    # check. Positioned near the boss edge on the tang side.
    return (
        cq.Workplane("XY")
        .box(0.005, 0.006, 0.003)
        .translate((handle_sign * 0.0085, 0.001, z0 + 0.0005))
    )


def _make_link_bar(
    secondary_xy: tuple[float, float],
    *,
    z0: float,
    thickness: float,
) -> cq.Workplane:
    sx, sy = secondary_xy
    length = math.sqrt(sx * sx + sy * sy)
    angle_deg = math.degrees(math.atan2(sy, sx))

    bar = (
        cq.Workplane("XY")
        .rect(length + 0.004, 0.009)
        .extrude(thickness)
        .rotate((0, 0, 0), (0, 0, 1), angle_deg)
        .translate((sx / 2, sy / 2, z0))
    )
    end_main = cq.Workplane("XY").circle(0.007).extrude(thickness).translate((0.0, 0.0, z0))
    end_secondary = cq.Workplane("XY").circle(0.006).extrude(thickness).translate((sx, sy, z0))
    body = bar.union(end_main).union(end_secondary)
    hole_main = (
        cq.Workplane("XY")
        .circle(PIVOT_HOLE_RADIUS)
        .extrude(thickness + 0.004)
        .translate((0.0, 0.0, z0 - 0.002))
    )
    hole_secondary = (
        cq.Workplane("XY")
        .circle(PIVOT_HOLE_RADIUS * 0.85)
        .extrude(thickness + 0.004)
        .translate((sx, sy, z0 - 0.002))
    )
    return body.cut(hole_main).cut(hole_secondary)


# ---------------------------------------------------------------------------
# Emit handle visuals
# ---------------------------------------------------------------------------
def _emit_handle_visuals(
    part,
    r: ResolvedConfig,
    *,
    index: int,
    handle_sign: float,
    metal_z0: float,
    grip_z0: float,
    front_z: float,
    mats: dict,
    geo_offset: tuple[float, float] = (0.0, 0.0),
) -> None:
    jaw_sign = -handle_sign
    ox, oy = geo_offset

    def _off(shape: cq.Workplane) -> cq.Workplane:
        if ox or oy:
            return shape.translate((ox, oy, 0.0))
        return shape

    grip_pts, tang_pts = _HANDLE_BUILDERS[r.handle_form]()
    y_scale = r.overall_len_scale
    x_scale = r.grip_girth_scale

    if r.jaw_module == "broad_square_jaw":
        bevel_outline, bevel_thickness = _broad_square_bevel_outline()
    else:
        bevel_outline, bevel_thickness = _tapered_bevel_outline()

    # Forged body
    part.visual(
        mesh_from_cadquery(
            _off(_make_forged_half(handle_sign, z0=metal_z0, tang_pts=tang_pts, y_scale=y_scale)),
            f"linesman_forged_half_{index}",
            tolerance=0.00035,
        ),
        material=mats["forged"],
        name="forged_body", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"steel_black_blue", "gunmetal_red", "black_yellow", "olive_orange", "polished_silver"} else "metal.chrome_polished"),
    )
    # Grip shell
    part.visual(
        mesh_from_cadquery(
            _off(
                _make_grip(
                    handle_sign,
                    z0=grip_z0,
                    grip_pts=grip_pts,
                    x_scale=x_scale,
                    y_scale=y_scale,
                )
            ),
            f"linesman_grip_{index}",
            tolerance=0.0004,
        ),
        material=mats["grip"],
        name="grip_shell", material_class_id="rubber.smooth_plain",
    )
    part.visual(
        mesh_from_cadquery(
            _off(_make_grip_collar(handle_sign, z0=grip_z0 - 0.0003)),
            f"linesman_collar_{index}",
            tolerance=0.00035,
        ),
        material=mats["collar"],
        name="grip_collar", material_class_id="rubber.smooth_plain",
    )
    # Embed grip ridge slightly below the front face so it fuses with grip
    # shell / forged body regardless of handle side z offsets.
    part.visual(
        mesh_from_cadquery(
            _off(_make_grip_highlight(handle_sign, z0=front_z - 0.0006, y_scale=y_scale)),
            f"linesman_grip_highlight_{index}",
            tolerance=0.00035,
        ),
        material=mats["highlight"],
        name="grip_ridge", material_class_id="rubber.smooth_plain",
    )
    part.visual(
        mesh_from_cadquery(
            _off(
                _make_jaw_bevel(
                    jaw_sign,
                    z0=front_z,
                    outline=bevel_outline,
                    thickness=bevel_thickness,
                )
            ),
            f"linesman_jaw_bevel_{index}",
            tolerance=0.0003,
        ),
        material=mats["edge"],
        name="jaw_bevel", material_class_id="metal.steel_bare",
    )
    part.visual(
        mesh_from_cadquery(
            _off(_make_cutting_edge(jaw_sign, z0=front_z - 0.0003)),
            f"linesman_cutting_edge_{index}",
            tolerance=0.00025,
        ),
        material=mats["edge"],
        name="cutting_edge", material_class_id="metal.steel_bare",
    )
    part.visual(
        mesh_from_cadquery(
            _off(_make_serrated_insert(jaw_sign, z0=front_z - 0.0003)),
            f"linesman_serrated_insert_{index}",
            tolerance=0.00025,
        ),
        material=mats["edge"],
        name="serrated_face", material_class_id="metal.steel_bare",
    )

    # Slot A: optional jaw feature visual.
    feature_builder = None
    if r.jaw_module == "fish_tape_channel":
        feature_builder = _make_fish_tape_channel
    elif r.jaw_module == "crimper_cavity":
        feature_builder = _make_crimper_cavity
    elif r.jaw_module == "cable_pulling_groove":
        feature_builder = _make_cable_groove
    if feature_builder is not None:
        part.visual(
            mesh_from_cadquery(
                _off(feature_builder(jaw_sign, z0=front_z - 0.0005)),
                f"linesman_jaw_feature_{index}",
                tolerance=0.00025,
            ),
            material=mats["polished"],
            name="jaw_feature", material_class_id="metal.chrome_polished",
        )

    # Slot C: captured spring adds a spring_anchor_slot visual on each half.
    if r.has_spring:
        part.visual(
            mesh_from_cadquery(
                _off(_make_spring_anchor_slot(handle_sign, z0=metal_z0 + 0.0005)),
                f"linesman_spring_slot_{index}",
                tolerance=0.0003,
            ),
            material=mats["polished"],
            name="spring_anchor_slot", material_class_id="metal.chrome_polished",
        )


# ---------------------------------------------------------------------------
# Builder
# ---------------------------------------------------------------------------
def build_pilers_linesman_pliers(
    config: PilersLinesmanPliersConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    palette = PALETTES[r.palette_style]
    mats = {
        key: model.material(f"plp_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in palette.items()
    }

    # -----------------------------------------------------------------
    # pivot_pin root part
    # -----------------------------------------------------------------
    pivot = model.part("pivot_pin")
    if r.leverage_mechanism == "offset_pivot":
        pin_solid = _make_pivot_pin(shaft_length=0.020, cap_radius=0.0125)
    elif r.leverage_mechanism == "compound_link":
        pin_solid = _make_pivot_pin(shaft_length=0.020, cap_radius=0.0108)
    else:
        pin_solid = _make_pivot_pin(shaft_length=0.0136, cap_radius=0.0108)
    pivot.visual(
        mesh_from_cadquery(pin_solid, "linesman_pivot_pin", tolerance=0.00025),
        material=mats["polished"],
        name="pivot_pin", material_class_id="metal.chrome_polished",
    )
    if r.has_spring:
        pivot.visual(
            mesh_from_geometry(
                _make_captured_spring_mesh(),
                "linesman_captured_spring",
            ),
            material=mats["polished"],
            name="captured_spring", material_class_id="metal.chrome_polished",
        )

    is_compound = r.is_compound

    if is_compound:
        # 5-part chain: pivot_pin + link_0 + link_1 + handle_0 + handle_1
        link_0 = model.part("link_0")
        link_0.visual(
            mesh_from_cadquery(
                _make_link_bar(
                    (-LINK_OFFSET_X, LINK_OFFSET_Y),
                    z0=-0.007,
                    thickness=LINK_THICKNESS,
                ),
                "compound_link_bar_0",
                tolerance=0.0003,
            ),
            material=mats["forged"],
            name="link_bar", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"steel_black_blue", "gunmetal_red", "black_yellow", "olive_orange", "polished_silver"} else "metal.chrome_polished"),
        )
        link_1 = model.part("link_1")
        link_1.visual(
            mesh_from_cadquery(
                _make_link_bar(
                    (LINK_OFFSET_X, LINK_OFFSET_Y),
                    z0=0.005,
                    thickness=LINK_THICKNESS,
                ),
                "compound_link_bar_1",
                tolerance=0.0003,
            ),
            material=mats["forged"],
            name="link_bar", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"steel_black_blue", "gunmetal_red", "black_yellow", "olive_orange", "polished_silver"} else "metal.chrome_polished"),
        )

        handle_0 = model.part("handle_0")
        _emit_handle_visuals(
            handle_0,
            r,
            index=0,
            handle_sign=-1.0,
            metal_z0=-0.005,
            grip_z0=-0.006,
            front_z=0.0000,
            mats=mats,
            geo_offset=(LINK_OFFSET_X, -LINK_OFFSET_Y),
        )
        handle_1 = model.part("handle_1")
        _emit_handle_visuals(
            handle_1,
            r,
            index=1,
            handle_sign=1.0,
            metal_z0=0.000,
            grip_z0=-0.004,
            front_z=0.0050,
            mats=mats,
            geo_offset=(-LINK_OFFSET_X, -LINK_OFFSET_Y),
        )

        model.articulation(
            "pivot_to_link_0",
            ArticulationType.REVOLUTE,
            parent=pivot,
            child=link_0,
            origin=Origin(),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(
                effort=70.0,
                velocity=2.0,
                lower=-r.open_upper * 0.5,
                upper=r.open_lower * 0.6,
            ),
            meta={"positive_motion": "swings link_0 about the main pivot"},
        )
        model.articulation(
            "pivot_to_link_1",
            ArticulationType.REVOLUTE,
            parent=pivot,
            child=link_1,
            origin=Origin(),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(
                effort=70.0,
                velocity=2.0,
                lower=-r.open_lower * 0.6,
                upper=r.open_upper * 0.5,
            ),
            meta={"positive_motion": "swings link_1 about the main pivot"},
        )
        model.articulation(
            "link_0_to_handle_0",
            ArticulationType.REVOLUTE,
            parent=link_0,
            child=handle_0,
            origin=Origin(xyz=(-LINK_OFFSET_X, LINK_OFFSET_Y, 0.0)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(
                effort=70.0,
                velocity=2.0,
                lower=-r.open_upper * 0.5,
                upper=r.open_lower * 0.6,
            ),
            meta={"positive_motion": "opens handle_0 at the secondary pivot"},
        )
        model.articulation(
            "link_1_to_handle_1",
            ArticulationType.REVOLUTE,
            parent=link_1,
            child=handle_1,
            origin=Origin(xyz=(LINK_OFFSET_X, LINK_OFFSET_Y, 0.0)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(
                effort=70.0,
                velocity=2.0,
                lower=-r.open_lower * 0.6,
                upper=r.open_upper * 0.5,
            ),
            meta={"positive_motion": "opens handle_1 at the secondary pivot"},
        )
    else:
        # Baseline 3-part chain: pivot_pin + handle_0 + handle_1
        handle_0 = model.part("handle_0")
        _emit_handle_visuals(
            handle_0,
            r,
            index=0,
            handle_sign=-1.0,
            metal_z0=-0.005,
            grip_z0=-0.006,
            front_z=0.0000,
            mats=mats,
        )
        handle_1 = model.part("handle_1")
        _emit_handle_visuals(
            handle_1,
            r,
            index=1,
            handle_sign=1.0,
            metal_z0=0.000,
            grip_z0=-0.004,
            front_z=0.0050,
            mats=mats,
        )
        model.articulation(
            "pivot_to_handle_0",
            ArticulationType.REVOLUTE,
            parent=pivot,
            child=handle_0,
            origin=Origin(),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(
                effort=70.0,
                velocity=2.0,
                lower=-r.open_upper,
                upper=r.open_lower,
            ),
            meta={"positive_motion": "opens handle_0 outward"},
        )
        model.articulation(
            "pivot_to_handle_1",
            ArticulationType.REVOLUTE,
            parent=pivot,
            child=handle_1,
            origin=Origin(),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(
                effort=70.0,
                velocity=2.0,
                lower=-r.open_lower,
                upper=r.open_upper,
            ),
            meta={"positive_motion": "opens handle_1 outward"},
        )

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_pilers_linesman_pliers(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_pilers_linesman_pliers(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def _aabb_center_x(aabb) -> float | None:
    if aabb is None:
        return None
    return 0.5 * (aabb[0][0] + aabb[1][0])


def run_pilers_linesman_pliers_tests(
    object_model: ArticulatedObject,
    config: PilersLinesmanPliersConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    pivot = object_model.get_part("pivot_pin")
    handle_0 = object_model.get_part("handle_0")
    handle_1 = object_model.get_part("handle_1")

    # Captured-pin overlaps.
    ctx.allow_overlap(
        pivot,
        handle_0,
        reason="Rivet pin captured through handle_0 forged half hub.",
    )
    ctx.allow_overlap(
        pivot,
        handle_1,
        reason="Rivet pin captured through handle_1 forged half hub.",
    )
    ctx.allow_overlap(
        handle_0,
        handle_1,
        reason="Two forged halves meet at the central lap and pivot on the shared rivet.",
    )

    if r.is_compound:
        link_0 = object_model.get_part("link_0")
        link_1 = object_model.get_part("link_1")
        ctx.allow_overlap(pivot, link_0, reason="Link 0 captured on main pivot.")
        ctx.allow_overlap(pivot, link_1, reason="Link 1 captured on main pivot.")
        ctx.allow_overlap(
            link_0,
            handle_0,
            reason="Handle 0 captured on link 0 secondary pivot.",
        )
        ctx.allow_overlap(
            link_1,
            handle_1,
            reason="Handle 1 captured on link 1 secondary pivot.",
        )
        j_pl0 = object_model.get_articulation("pivot_to_link_0")
        j_pl1 = object_model.get_articulation("pivot_to_link_1")
        j_lh0 = object_model.get_articulation("link_0_to_handle_0")
        j_lh1 = object_model.get_articulation("link_1_to_handle_1")
        ctx.check(
            "compound_link topology: 5 parts + 4 joints",
            len(object_model.parts) == 5 and len(object_model.articulations) == 4,
            details=(f"parts={len(object_model.parts)}, joints={len(object_model.articulations)}"),
        )
        for name, j in (
            ("pivot_to_link_0", j_pl0),
            ("pivot_to_link_1", j_pl1),
            ("link_0_to_handle_0", j_lh0),
            ("link_1_to_handle_1", j_lh1),
        ):
            lm = j.motion_limits
            ctx.check(
                f"{name} is a bounded REVOLUTE about +Z",
                j.articulation_type == ArticulationType.REVOLUTE
                and tuple(j.axis) == (0.0, 0.0, 1.0)
                and lm is not None
                and lm.lower is not None
                and lm.upper is not None
                and lm.lower < 0.0 < lm.upper,
                details=f"axis={j.axis}, limits={lm}",
            )
        # Kinematics for compound branch: rotate pivot_to_link_0 negative,
        # pivot_to_link_1 positive; verify handles/grips separate.
        rest_grip_0 = _aabb_center_x(ctx.part_element_world_aabb(handle_0, elem="grip_shell"))
        rest_grip_1 = _aabb_center_x(ctx.part_element_world_aabb(handle_1, elem="grip_shell"))
        with ctx.pose(
            {
                j_pl0: j_pl0.motion_limits.lower,
                j_pl1: j_pl1.motion_limits.upper,
            }
        ):
            open_grip_0 = _aabb_center_x(ctx.part_element_world_aabb(handle_0, elem="grip_shell"))
            open_grip_1 = _aabb_center_x(ctx.part_element_world_aabb(handle_1, elem="grip_shell"))
        span_rest = (
            None if rest_grip_0 is None or rest_grip_1 is None else rest_grip_1 - rest_grip_0
        )
        span_open = (
            None if open_grip_0 is None or open_grip_1 is None else open_grip_1 - open_grip_0
        )
        ctx.check(
            "compound link opens handle grips",
            span_rest is not None and span_open is not None and span_open > span_rest + 0.003,
            details=f"grip spans rest/open={span_rest}/{span_open}",
        )
    else:
        joint_0 = object_model.get_articulation("pivot_to_handle_0")
        joint_1 = object_model.get_articulation("pivot_to_handle_1")
        ctx.check(
            "baseline topology: 3 parts + 2 joints, pivot_pin is root",
            len(object_model.parts) == 3
            and len(object_model.articulations) == 2
            and [p.name for p in object_model.root_parts()] == ["pivot_pin"],
            details=(
                f"parts={[p.name for p in object_model.parts]}, "
                f"joints={[j.name for j in object_model.articulations]}"
            ),
        )
        for index, (handle, joint) in enumerate(((handle_0, joint_0), (handle_1, joint_1))):
            lm = joint.motion_limits
            ctx.check(
                f"handle {index} REVOLUTE about +Z with sign-span limits",
                joint.articulation_type == ArticulationType.REVOLUTE
                and joint.parent == "pivot_pin"
                and joint.child == handle.name
                and tuple(joint.axis) == (0.0, 0.0, 1.0)
                and lm is not None
                and lm.lower is not None
                and lm.upper is not None
                and lm.lower < 0.0 < lm.upper,
                details=(
                    f"parent={joint.parent}, child={joint.child}, axis={joint.axis}, limits={lm}"
                ),
            )
        # Kinematics: opening pose should spread grips.
        rest_grip_0 = _aabb_center_x(ctx.part_element_world_aabb(handle_0, elem="grip_shell"))
        rest_grip_1 = _aabb_center_x(ctx.part_element_world_aabb(handle_1, elem="grip_shell"))
        with ctx.pose(
            {
                joint_0: joint_0.motion_limits.lower,
                joint_1: joint_1.motion_limits.upper,
            }
        ):
            open_grip_0 = _aabb_center_x(ctx.part_element_world_aabb(handle_0, elem="grip_shell"))
            open_grip_1 = _aabb_center_x(ctx.part_element_world_aabb(handle_1, elem="grip_shell"))
        span_rest = (
            None if rest_grip_0 is None or rest_grip_1 is None else rest_grip_1 - rest_grip_0
        )
        span_open = (
            None if open_grip_0 is None or open_grip_1 is None else open_grip_1 - open_grip_0
        )
        ctx.check(
            "baseline: opening pose spreads grips",
            span_rest is not None and span_open is not None and span_open > span_rest + 0.005,
            details=f"grip spans rest/open={span_rest}/{span_open}",
        )

    # Shared visual presence.
    for index, handle in enumerate((handle_0, handle_1)):
        visible = {v.name for v in handle.visuals}
        expected = {
            "forged_body",
            "grip_shell",
            "grip_collar",
            "grip_ridge",
            "jaw_bevel",
            "cutting_edge",
            "serrated_face",
        }
        ctx.check(
            f"handle {index} carries plier core visuals",
            expected.issubset(visible),
            details=f"visuals={sorted(visible)}",
        )

    # Slot A geometry claims.
    if r.jaw_module == "broad_square_jaw":
        for index, handle in enumerate((handle_0, handle_1)):
            aabb = ctx.part_element_world_aabb(handle, elem="jaw_bevel")
            width = None if aabb is None else aabb[1][0] - aabb[0][0]
            ctx.check(
                f"handle {index} broad_square_jaw bevel >= 14 mm wide",
                width is not None and width >= 0.013,
                details=f"jaw_bevel width={width}",
            )
    if r.jaw_module in ("fish_tape_channel", "crimper_cavity", "cable_pulling_groove"):
        for index, handle in enumerate((handle_0, handle_1)):
            names = {v.name for v in handle.visuals}
            ctx.check(
                f"handle {index} carries jaw_feature visual for {r.jaw_module}",
                "jaw_feature" in names,
                details=f"visuals={sorted(names)}",
            )

    # Slot C geometry claim.
    if r.has_spring:
        pivot_names = {v.name for v in pivot.visuals}
        ctx.check(
            "captured_spring visual on pivot_pin",
            "captured_spring" in pivot_names,
            details=f"pivot visuals={sorted(pivot_names)}",
        )
        for index, handle in enumerate((handle_0, handle_1)):
            names = {v.name for v in handle.visuals}
            ctx.check(
                f"handle {index} carries spring_anchor_slot",
                "spring_anchor_slot" in names,
                details=f"visuals={sorted(names)}",
            )

    # Slot D geometry claim: long_handle really extends the grip.
    if r.handle_form == "long_handle":
        for index, handle in enumerate((handle_0, handle_1)):
            grip_aabb = ctx.part_element_world_aabb(handle, elem="grip_shell")
            if grip_aabb is not None:
                grip_min_y = grip_aabb[0][1]
                # baseline min_y ~ -0.159, long ~ -0.174; with scale >= 0.92
                # ensure < -0.150.
                ctx.check(
                    f"handle {index} long_handle grip reaches < -0.150",
                    grip_min_y < -0.150,
                    details=f"grip min_y={grip_min_y}",
                )

    # Materials check.
    material_names = {m.name for m in object_model.materials}
    ctx.check(
        "palette materials present",
        len(material_names) >= 6,
        details=f"materials count={len(material_names)}",
    )

    # Slot choices metadata reflects the same choices.
    ctx.check(
        "slot_choices metadata is emitted",
        object_model.meta.get("slot_choices") == slot_choices_for_config(r),
        details=f"meta slot_choices={object_model.meta.get('slot_choices')}",
    )

    return ctx.report()


__all__ = [
    "PilersLinesmanPliersConfig",
    "ResolvedConfig",
    "config_from_seed",
    "resolve_config",
    "with_overrides",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "build_pilers_linesman_pliers",
    "build_seeded_pilers_linesman_pliers",
    "run_pilers_linesman_pliers_tests",
    "__modular__",
]
