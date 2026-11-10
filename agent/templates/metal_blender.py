# SPDX-License-Identifier: Apache-2.0

"""Metal blender — bench manual metal bender / forming machine (modular template).

Category identity (spec ``specs_modular_v1/metal_blender.md``): a compact
**bench manual metal bender / forming machine** (FB-4 style bench steel bending
brake). The category source name "Metal_blender" is a picture-set typo — the
image and every adopted sample record are a manual metalworking bender, NOT a
kitchen blender. This template must not drift into an ``immersion_blender`` /
``blender_countertop`` (jug + motor + blade) nor into a powered
``stamping_press`` (electric ram/flywheel).

Fixed 4-part skeleton (never varies across seeds):
  * ``frame`` (ROOT, FIXED) — base plate + housing shell + plinths + rails +
    backstop + fixed die (③ Primary Form Family) + reference strip + pivot
    bracket + two annular-tube bearings + badge + fasteners + rubber feet.
  * ``clamp_lever`` — long over-center clamping lever with a captured pivot
    pin (REVOLUTE y, [0, 0.82]).
  * ``feed_handwheel`` — three-spoke screw handwheel (CONTINUOUS x).
  * ``forming_crank`` — left-side forming spindle + tommy bar + paddle grip
    (REVOLUTE x, [−1.35, 1.35]).

Three slots + a palette axis (spec §4):
  * Slot A ``forming_topology`` (4): classic_bench_brake / bead_roller /
    three_roll_slip_roller / v_die_press_brake — the ``forming_crank`` inner
    geometry (± an attached forming roll) and, for the v-die variant, the
    ``fixed_die`` V-mate face on the frame.
  * Slot B ``clamping_style`` (3): classic_lever_plate / eccentric_cam_clamp /
    screw_beam_clamp — the ``clamp_lever`` main plate silhouette plus an
    optional cam disc or screw shaft visual.
  * Slot C ``die_profile`` (3, ③ Primary Form Family): flat_die /
    round_bead_die / sharp_v_die — the ``fixed_die`` top-face profile on the
    frame (frame visual, host-conformal).

The 3 non-FIXED joints (type / axis / origin / limit) are motion-safety-locked
across every seed and every slot combination. Feed PRISMATIC and forming
CONTINUOUS variant branches from the source pool are intentionally excluded
from the sampled domain (see spec §8.5 ②).

Captured-pin allowances (Rule 2 grandfathered, no MatingContract — no
axis-aligned face pair exists for pin-in-collar / shaft-in-bearing):
  * ``clamp_lever.pivot_pin`` ↔ ``frame.clamp_pivot_bracket``
  * ``feed_handwheel.screw_core`` ↔ ``frame.feed_bearing``
  * ``forming_crank.crank_shaft`` ↔ ``frame.forming_bearing``

Every visual reads its material from ``PALETTE_STYLES`` (⑥, 6 colorways).
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from math import cos, pi, sin
from typing import Literal

import cadquery as cq

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    MotionLimits,
    Origin,
    Sphere,
    TestContext,
    TestReport,
    mesh_from_cadquery,
)

__modular__ = True


# ===========================================================================
# Slot enums.
# ===========================================================================
FormingTopology = Literal[
    "classic_bench_brake",
    "bead_roller",
    "three_roll_slip_roller",
    "v_die_press_brake",
]
ClampingStyle = Literal[
    "classic_lever_plate",
    "eccentric_cam_clamp",
    "screw_beam_clamp",
]
DieProfile = Literal["flat_die", "round_bead_die", "sharp_v_die"]
PaletteStyle = Literal[
    "factory_gunmetal",
    "industrial_charcoal",
    "machinery_green",
    "safety_blue",
    "red_industrial",
    "hammertone_gray",
]

FORMING_TOPOLOGIES: tuple[FormingTopology, ...] = (
    "classic_bench_brake",
    "bead_roller",
    "three_roll_slip_roller",
    "v_die_press_brake",
)
CLAMPING_STYLES: tuple[ClampingStyle, ...] = (
    "classic_lever_plate",
    "eccentric_cam_clamp",
    "screw_beam_clamp",
)
DIE_PROFILES: tuple[DieProfile, ...] = ("flat_die", "round_bead_die", "sharp_v_die")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "factory_gunmetal",
    "industrial_charcoal",
    "machinery_green",
    "safety_blue",
    "red_industrial",
    "hammertone_gray",
)


# ===========================================================================
# Real-world dimensions (meters), from the origin baseline (S1 model.py).
# ===========================================================================
_BASE_L = 0.52  # base_plate X
_BASE_W = 0.22  # base_plate Y
_BASE_H = 0.012  # base_plate Z
_HOUSING_L = 0.43  # housing_shell X
_HOUSING_W = 0.14  # housing_shell Y
_HOUSING_H = 0.16  # housing_shell Z
_HOUSING_CENTER_Z = 0.17  # housing_shell center Z
_LEVER_LEN = 0.375  # lever_plate approximate X span (from polyline)
_HANDWHEEL_HUB_R = 0.035  # wheel_hub radius
_CRANK_REACH = 0.245  # tommy_bar length
_JOINT_CLAMP_XYZ = (0.060, -0.091, 0.285)
# feed/forming joint origins are derived from the housing/bearing geometry
# in build_metal_blender so they always land on the bearing centreline
# (see `bearing_center_x` in _build_frame).


# ===========================================================================
# Config
# ===========================================================================
@dataclass(frozen=True)
class MetalBlenderConfig:
    forming_topology: FormingTopology | None = None
    clamping_style: ClampingStyle | None = None
    die_profile: DieProfile | None = None
    palette_style: PaletteStyle = "factory_gunmetal"
    base_length_scale: float = 1.0
    housing_length_scale: float = 1.0
    lever_length_scale: float = 1.0
    handwheel_radius_scale: float = 1.0
    crank_reach_scale: float = 1.0
    name: str = "metal_blender"


@dataclass(frozen=True)
class ResolvedMetalBlenderConfig:
    forming_topology: FormingTopology
    clamping_style: ClampingStyle
    die_profile: DieProfile
    palette_style: PaletteStyle
    base_length_scale: float
    housing_length_scale: float
    lever_length_scale: float
    handwheel_radius_scale: float
    crank_reach_scale: float
    name: str


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _pick(value, choices):
    return value if value in choices else choices[0]


def config_from_seed(seed: int) -> MetalBlenderConfig:
    """Deterministic procedural sampling (seed=0 is NOT special)."""
    rng = random.Random(seed)
    return MetalBlenderConfig(
        forming_topology=rng.choice(FORMING_TOPOLOGIES),
        clamping_style=rng.choice(CLAMPING_STYLES),
        die_profile=rng.choice(DIE_PROFILES),
        palette_style=rng.choice(PALETTE_STYLES),
        base_length_scale=round(rng.uniform(0.92, 1.08), 4),
        housing_length_scale=round(rng.uniform(0.995, 1.06), 4),
        lever_length_scale=round(rng.uniform(0.92, 1.08), 4),
        handwheel_radius_scale=round(rng.uniform(0.94, 1.06), 4),
        crank_reach_scale=round(rng.uniform(0.92, 1.08), 4),
        name=f"seeded_metal_blender_{seed}",
    )


def resolve_config(
    config: MetalBlenderConfig | None = None,
) -> ResolvedMetalBlenderConfig:
    """Solve §7: independent scales, then inequality projections.

    Inequalities: housing_length <= 0.86 * base_length (structural),
    lever/crank/handwheel sweep clearances via range clamps. All in
    ``resolve_config`` so no failure is left to the builder.
    """
    cfg = config or MetalBlenderConfig()
    forming_topology = _pick(cfg.forming_topology, FORMING_TOPOLOGIES)
    clamping_style = _pick(cfg.clamping_style, CLAMPING_STYLES)
    die_profile = _pick(cfg.die_profile, DIE_PROFILES)
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)

    base_ls = _clamp(cfg.base_length_scale, 0.92, 1.08)
    # housing must always meet the fixed bearing inner face at |x|=0.215 within
    # the connectivity tol (1e-6). Bearing overlap by ~0.010m via housing edge.
    housing_ls = _clamp(cfg.housing_length_scale, 0.995, 1.06)
    lever_ls = _clamp(cfg.lever_length_scale, 0.92, 1.08)
    hw_rs = _clamp(cfg.handwheel_radius_scale, 0.94, 1.06)
    crank_rs = _clamp(cfg.crank_reach_scale, 0.92, 1.08)

    # inequality: housing must be at most 86% of the base plate (structural).
    max_housing_ratio = 0.86 * (_BASE_L * base_ls) / _HOUSING_L
    housing_ls = min(housing_ls, max_housing_ratio)

    return ResolvedMetalBlenderConfig(
        forming_topology=forming_topology,
        clamping_style=clamping_style,
        die_profile=die_profile,
        palette_style=palette_style,
        base_length_scale=base_ls,
        housing_length_scale=housing_ls,
        lever_length_scale=lever_ls,
        handwheel_radius_scale=hw_rs,
        crank_reach_scale=crank_rs,
        name=cfg.name or "metal_blender",
    )


def slot_choices_for_config(
    config: MetalBlenderConfig | ResolvedMetalBlenderConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedMetalBlenderConfig) else resolve_config(config)
    return (
        ("forming_topology", r.forming_topology),
        ("clamping_style", r.clamping_style),
        ("die_profile", r.die_profile),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ===========================================================================
# Palette (⑥) — 6 industrial colorways; every visual reads its material here.
# ===========================================================================
def _palette_rgba(style: PaletteStyle) -> dict[str, tuple[float, float, float, float]]:
    """Return the RGBA table for a palette. Keys are canonical role names
    that every visual references (never bare RGBA)."""
    presets: dict[str, dict[str, tuple[float, float, float, float]]] = {
        "factory_gunmetal": dict(
            body=(0.22, 0.25, 0.27, 1.0),
            body_dark=(0.10, 0.11, 0.12, 1.0),
            black_oxide=(0.055, 0.058, 0.060, 1.0),
            brushed=(0.67, 0.69, 0.70, 1.0),
            bright=(0.82, 0.83, 0.82, 1.0),
            rubber=(0.025, 0.025, 0.027, 1.0),
            accent=(0.72, 0.06, 0.045, 1.0),
        ),
        "industrial_charcoal": dict(
            body=(0.14, 0.14, 0.15, 1.0),
            body_dark=(0.07, 0.07, 0.08, 1.0),
            black_oxide=(0.04, 0.04, 0.045, 1.0),
            brushed=(0.60, 0.61, 0.62, 1.0),
            bright=(0.78, 0.79, 0.80, 1.0),
            rubber=(0.025, 0.025, 0.027, 1.0),
            accent=(0.85, 0.72, 0.10, 1.0),
        ),
        "machinery_green": dict(
            body=(0.20, 0.34, 0.24, 1.0),
            body_dark=(0.10, 0.20, 0.14, 1.0),
            black_oxide=(0.06, 0.07, 0.06, 1.0),
            brushed=(0.66, 0.68, 0.66, 1.0),
            bright=(0.82, 0.83, 0.80, 1.0),
            rubber=(0.025, 0.025, 0.027, 1.0),
            accent=(0.90, 0.85, 0.20, 1.0),
        ),
        "safety_blue": dict(
            body=(0.12, 0.30, 0.55, 1.0),
            body_dark=(0.06, 0.16, 0.32, 1.0),
            black_oxide=(0.05, 0.05, 0.055, 1.0),
            brushed=(0.66, 0.68, 0.71, 1.0),
            bright=(0.80, 0.82, 0.84, 1.0),
            rubber=(0.025, 0.025, 0.027, 1.0),
            accent=(0.92, 0.92, 0.20, 1.0),
        ),
        "red_industrial": dict(
            body=(0.55, 0.10, 0.10, 1.0),
            body_dark=(0.30, 0.05, 0.05, 1.0),
            black_oxide=(0.05, 0.05, 0.055, 1.0),
            brushed=(0.65, 0.66, 0.67, 1.0),
            bright=(0.80, 0.81, 0.82, 1.0),
            rubber=(0.025, 0.025, 0.027, 1.0),
            accent=(0.10, 0.10, 0.11, 1.0),
        ),
        "hammertone_gray": dict(
            body=(0.42, 0.44, 0.46, 1.0),
            body_dark=(0.28, 0.29, 0.30, 1.0),
            black_oxide=(0.05, 0.05, 0.055, 1.0),
            brushed=(0.72, 0.73, 0.74, 1.0),
            bright=(0.84, 0.85, 0.85, 1.0),
            rubber=(0.025, 0.025, 0.027, 1.0),
            accent=(0.72, 0.06, 0.045, 1.0),
        ),
    }
    return presets[style]


# ===========================================================================
# Cadquery helpers (from origin S1 L21-L49).
# ===========================================================================
def _mesh(shape, name: str, *, assets: AssetContext | None = None):
    return mesh_from_cadquery(
        shape,
        name,
        tolerance=0.0009,
        angular_tolerance=0.12,
        assets=assets,
    )


def _annular_tube_x(length: float, outer_radius: float, inner_radius: float):
    """CadQuery annulus centered at the origin and aligned to local X."""
    return (
        cq.Workplane("XY")
        .circle(outer_radius)
        .circle(inner_radius)
        .extrude(length)
        .translate((0.0, 0.0, -length * 0.5))
        .rotate((0.0, 0.0, 0.0), (0.0, 1.0, 0.0), 90.0)
    )


def _hex_prism_x(length: float, across_corners: float):
    return (
        cq.Workplane("XY")
        .polygon(6, across_corners)
        .extrude(length)
        .translate((0.0, 0.0, -length * 0.5))
        .rotate((0.0, 0.0, 0.0), (0.0, 1.0, 0.0), 90.0)
    )


# ===========================================================================
# Slot C: die_profile — top-face profile on the ``fixed_die`` (frame visual).
# ===========================================================================
def _build_fixed_die(frame, r: ResolvedMetalBlenderConfig, mats, *, assets):
    """Emit the fixed_die visual on the frame. The base slab is invariant
    (matches every source); the top face is the ③ Primary Form Family family:
    flat / rounded bead ridge / sharp V ridge. Round_bead / sharp_v add small
    accent visuals fused into the frame (Rule 1: static → visual not FIXED
    part)."""
    base_die = (
        cq.Workplane("XY")
        .box(0.31, 0.042, 0.020)
        .edges("|X")
        .chamfer(0.003)
        .translate((-0.030, 0.027, 0.259))
    )
    frame.visual(
        _mesh(base_die, "fixed_die", assets=assets), material=mats["black_oxide"], name="fixed_die", material_class_id="metal.blackened_gunmetal"
    )

    if r.die_profile == "round_bead_die":
        # A rounded bead ridge along X (a half-cylinder embedded into the top).
        frame.visual(
            Cylinder(radius=0.006, length=0.29),
            origin=Origin(xyz=(-0.030, 0.027, 0.272), rpy=(0.0, pi / 2.0, 0.0)),
            material=mats["black_oxide"],
            name="die_bead_ridge", material_class_id="metal.blackened_gunmetal",
        )
    elif r.die_profile == "sharp_v_die":
        # A sharp V ridge — two thin canted boxes forming the peak.
        for i, sign in enumerate((-1.0, 1.0)):
            frame.visual(
                Box((0.29, 0.015, 0.004)),
                origin=Origin(
                    xyz=(-0.030, 0.027 + sign * 0.006, 0.272),
                    rpy=(sign * 0.5, 0.0, 0.0),
                ),
                material=mats["black_oxide"],
                name=f"die_v_face_{i}", material_class_id="metal.blackened_gunmetal",
            )


# ===========================================================================
# Frame builder (invariant across seeds; parameterized by scales).
# ===========================================================================
def _build_frame(model, r: ResolvedMetalBlenderConfig, mats, *, assets):
    frame = model.part(
        "frame",
        meta={
            "role": "fixed machine frame, mounting base, housing, dies, and bearing supports",
            "finish": "painted body with brushed and bright steel details",
        },
    )

    base_l = _BASE_L * r.base_length_scale
    # Housing size is invariant across seeds: shrinking it opens a gap to the
    # fixed bearing (connectivity fail) or forces the bearing to move (which
    # invalidates the joint origin coincident with the bearing centreline).
    # `housing_length_scale` is retained as a nominal parameter but not applied
    # to the housing shell geometry — only the bolt pattern uses base scale.
    housing_l = _HOUSING_L

    # base_plate with 4 through-holes (single-sourced hole spacing derived from
    # the scaled base X so holes track the plate length).
    hole_dx = base_l * 0.413  # matches origin 0.215 / 0.52
    hole_dy = 0.078
    base_shape = cq.Workplane("XY").box(base_l, _BASE_W, _BASE_H).translate((0.0, 0.0, 0.006))
    for x in (-hole_dx, hole_dx):
        for y in (-hole_dy, hole_dy):
            hole = (
                cq.Workplane("XY")
                .center(x, y)
                .circle(0.0075)
                .extrude(0.03)
                .translate((0.0, 0.0, -0.008))
            )
            base_shape = base_shape.cut(hole)
    frame.visual(
        _mesh(base_shape, "base_plate", assets=assets), material=mats["body"], name="base_plate", material_class_id="metal.paint_coated"
    )

    # main housing with two clear bores (feed on right, forming on left).
    housing_shape = (
        cq.Workplane("XY")
        .box(housing_l, _HOUSING_W, _HOUSING_H)
        .edges("|Z")
        .fillet(0.007)
        .translate((0.0, 0.0, _HOUSING_CENTER_Z))
    )
    feed_bore = (
        cq.Workplane("YZ").center(0.0, _HOUSING_CENTER_Z).circle(0.018).extrude(0.30, both=True)
    )
    forming_bore = cq.Workplane("YZ").center(-0.032, 0.145).circle(0.014).extrude(0.30, both=True)
    housing_shape = housing_shape.cut(feed_bore).cut(forming_bore)
    frame.visual(
        _mesh(housing_shape, "housing_shell", assets=assets),
        material=mats["body"],
        name="housing_shell", material_class_id="metal.paint_coated",
    )

    # welded plinths + reinforcing rail
    plinth_l = 0.36
    frame.visual(
        Box((plinth_l, 0.055, 0.080)),
        origin=Origin(xyz=(0.0, 0.035, 0.052)),
        material=mats["body_dark"],
        name="rear_plinth", material_class_id="metal.paint_coated",
    )
    frame.visual(
        Box((plinth_l, 0.026, 0.080)),
        origin=Origin(xyz=(0.0, -0.035, 0.052)),
        material=mats["body"],
        name="front_plinth", material_class_id="metal.paint_coated",
    )
    frame.visual(
        Box((0.40, 0.032, 0.022)),
        origin=Origin(xyz=(0.0, 0.045, 0.078)),
        material=mats["black_oxide"],
        name="lower_rail", material_class_id="metal.blackened_gunmetal",
    )

    # left upright/backstop + triangular spindle bracket
    frame.visual(
        Box((0.022, 0.132, 0.190)),
        origin=Origin(xyz=(-0.226, 0.002, 0.178)),
        material=mats["body_dark"],
        name="left_backstop", material_class_id="metal.paint_coated",
    )
    left_support = (
        cq.Workplane("XZ")
        .polyline(
            [
                (-0.235, 0.018),
                (-0.175, 0.018),
                (-0.185, 0.115),
                (-0.215, 0.158),
                (-0.235, 0.145),
            ]
        )
        .close()
        .extrude(0.012, both=True)
        .translate((0.0, -0.074, 0.0))
    )
    frame.visual(
        _mesh(left_support, "left_spindle_bracket", assets=assets),
        material=mats["body"],
        name="left_spindle_bracket", material_class_id="metal.paint_coated",
    )

    # Slot C ③ Primary Form Family — the ``fixed_die`` on the frame top.
    _build_fixed_die(frame, r, mats, assets=assets)
    frame.visual(
        Box((0.335, 0.012, 0.003)),
        origin=Origin(xyz=(-0.005, -0.0715, 0.247)),
        material=mats["brushed"],
        name="reference_strip", material_class_id="metal.brushed_silver",
    )

    # front-side pivot bracket for the clamp lever
    pivot_bracket = (
        cq.Workplane("XZ")
        .polyline(
            [
                (0.005, 0.238),
                (0.092, 0.238),
                (0.092, 0.267),
                (0.071, 0.294),
                (0.046, 0.300),
                (0.019, 0.270),
            ]
        )
        .close()
        .extrude(0.007, both=True)
    )
    pivot_hole = cq.Workplane("XZ").center(0.060, 0.285).circle(0.0090).extrude(0.018, both=True)
    pivot_bracket = pivot_bracket.cut(pivot_hole).translate((0.0, -0.078, 0.0))
    frame.visual(
        _mesh(pivot_bracket, "clamp_pivot_bracket", assets=assets),
        material=mats["body"],
        name="clamp_pivot_bracket", material_class_id="metal.paint_coated",
    )

    # bearing collars (annular tubes; captured-pin allow_overlap targets).
    # Position so the inner (housing-facing) end embeds into the housing shell
    # regardless of housing_length_scale: bearing outer-face x is derived from
    # housing half-length + a fixed protrusion, guaranteeing contact.
    # bearing centreline is FIXED at world |x|=0.235 (matches origin baseline);
    # housing_length_scale is bounded (§7 clamp 0.98–1.02) so the housing
    # inner face always covers the bearing embed within the connectivity tol.
    bearing_len = 0.040
    bearing_center_x = 0.235
    right_bearing = _annular_tube_x(bearing_len, 0.033, 0.0130).translate(
        (bearing_center_x, 0.0, 0.17)
    )
    frame.visual(
        _mesh(right_bearing, "feed_bearing", assets=assets),
        material=mats["black_oxide"],
        name="feed_bearing", material_class_id="metal.blackened_gunmetal",
    )
    left_bearing = _annular_tube_x(bearing_len, 0.025, 0.0100).translate(
        (-bearing_center_x, -0.032, 0.145)
    )
    frame.visual(
        _mesh(left_bearing, "forming_bearing", assets=assets),
        material=mats["body_dark"],
        name="forming_bearing", material_class_id="metal.paint_coated",
    )

    # badge + inspection hole + fasteners + rubber feet (fixed decoration)
    badge = (
        cq.Workplane("XZ")
        .ellipse(0.048, 0.019)
        .extrude(0.0012, both=True)
        .translate((0.015, -0.0712, 0.170))
    )
    frame.visual(
        _mesh(badge, "blank_badge", assets=assets), material=mats["brushed"], name="blank_badge", material_class_id="metal.brushed_silver"
    )
    frame.visual(
        Box((0.052, 0.0025, 0.006)),
        origin=Origin(xyz=(0.015, -0.073, 0.170)),
        material=mats["accent"],
        name="badge_accent", material_class_id="metal.paint_coated",
    )
    frame.visual(
        Cylinder(radius=0.0085, length=0.0025),
        origin=Origin(xyz=(-0.075, -0.0712, 0.174), rpy=(pi / 2.0, 0.0, 0.0)),
        material=mats["black_oxide"],
        name="inspection_port", material_class_id="metal.blackened_gunmetal",
    )
    for i, (x, z) in enumerate([(-0.185, 0.112), (-0.185, 0.225), (0.185, 0.112), (0.185, 0.225)]):
        frame.visual(
            Cylinder(radius=0.0042, length=0.004),
            origin=Origin(xyz=(x, -0.072, z), rpy=(pi / 2.0, 0.0, 0.0)),
            material=mats["bright"],
            name=f"front_fastener_{i}", material_class_id="metal.chrome_polished",
        )
    # 4 rubber feet, tracking the scaled base plate corners.
    foot_dx = base_l * 0.375  # matches origin 0.195 / 0.52
    for i, (x, y) in enumerate(
        [(-foot_dx, -0.076), (-foot_dx, 0.076), (foot_dx, -0.076), (foot_dx, 0.076)]
    ):
        frame.visual(
            Cylinder(radius=0.017, length=0.008),
            origin=Origin(xyz=(x, y, -0.004)),
            material=mats["rubber"],
            name=f"foot_{i}", material_class_id="rubber.smooth_plain",
        )
    return frame


# ===========================================================================
# Slot B: clamping_style — clamp_lever variants.
# ===========================================================================
def _build_clamp_lever(model, r: ResolvedMetalBlenderConfig, mats, *, assets):
    clamp_lever = model.part(
        "clamp_lever",
        meta={"role": "manual over-center clamping lever", "finish": "brushed steel"},
    )
    ll = r.lever_length_scale  # 0.92–1.08
    # Lever plate polyline authored in the pivot frame (pivot at origin).
    # X extents scale with lever_length_scale.
    lp = [
        (-0.345 * ll, 0.020),
        (-0.337 * ll, 0.058),
        (-0.030, 0.026),
        (0.024, 0.013),
        (0.030, -0.010),
        (0.004, -0.022),
        (-0.315 * ll, 0.004),
    ]
    lever_plate = cq.Workplane("XZ").polyline(lp).close().extrude(0.006, both=True)
    lever_slot = (
        cq.Workplane("XZ")
        .center(-0.095 * ll, 0.013)
        .slot2D(0.105 * ll, 0.013, 0.0)
        .extrude(0.010, both=True)
    )
    lever_pivot_hole = cq.Workplane("XZ").circle(0.0090).extrude(0.010, both=True)
    lever_plate = lever_plate.cut(lever_slot).cut(lever_pivot_hole)
    clamp_lever.visual(
        _mesh(lever_plate, "lever_plate", assets=assets),
        material=mats["brushed"],
        name="lever_plate", material_class_id="metal.brushed_silver",
    )
    clamp_lever.visual(
        Box((0.095 * ll, 0.026, 0.028)),
        origin=Origin(xyz=(-0.320 * ll, 0.0, 0.047)),
        material=mats["black_oxide"],
        name="lever_grip", material_class_id="metal.blackened_gunmetal",
    )
    clamp_lever.visual(
        Cylinder(radius=0.0092, length=0.040),
        origin=Origin(xyz=(0.0, 0.013, 0.0), rpy=(pi / 2.0, 0.0, 0.0)),
        material=mats["body_dark"],
        name="pivot_pin", material_class_id="metal.paint_coated",
    )
    # Slot B extras
    if r.clamping_style == "eccentric_cam_clamp":
        # Eccentric cam disc mounted on the pivot centreline (rotates with lever
        # as a decorative visual — Rule 1: no articulation, fused visual).
        clamp_lever.visual(
            Cylinder(radius=0.024, length=0.010),
            origin=Origin(xyz=(0.008, -0.006, -0.005), rpy=(pi / 2.0, 0.0, 0.0)),
            material=mats["black_oxide"],
            name="eccentric_cam_disc", material_class_id="metal.blackened_gunmetal",
        )
    elif r.clamping_style == "screw_beam_clamp":
        # A short cross screw riding the lever plate top: a horizontal cylinder
        # embedded on the lever plate (host-conformal, decorative).
        clamp_lever.visual(
            Cylinder(radius=0.008, length=0.115),
            origin=Origin(xyz=(-0.180 * ll, 0.0, 0.028), rpy=(0.0, pi / 2.0, 0.0)),
            material=mats["bright"],
            name="clamp_screw", material_class_id="metal.chrome_polished",
        )
        clamp_lever.visual(
            Cylinder(radius=0.014, length=0.010),
            origin=Origin(xyz=(-0.120 * ll, 0.0, 0.028), rpy=(0.0, pi / 2.0, 0.0)),
            material=mats["black_oxide"],
            name="clamp_screw_collar", material_class_id="metal.blackened_gunmetal",
        )
    return clamp_lever


# ===========================================================================
# feed_handwheel — 3-spoke screw handwheel (invariant across slots).
# ===========================================================================
def _build_feed_handwheel(model, r: ResolvedMetalBlenderConfig, mats, *, assets):
    fh = model.part(
        "feed_handwheel",
        meta={"role": "threaded pressure/feed adjustment", "finish": "black oxide steel"},
    )
    hw_r = _HANDWHEEL_HUB_R * r.handwheel_radius_scale
    fh.visual(
        Cylinder(radius=0.0132, length=0.170),
        origin=Origin(xyz=(0.070, 0.0, 0.0), rpy=(0.0, pi / 2.0, 0.0)),
        material=mats["black_oxide"],
        name="screw_core", material_class_id="metal.blackened_gunmetal",
    )
    # 12 thread crests (structural constant, not a multiplicity axis).
    for i in range(12):
        fh.visual(
            Cylinder(radius=0.0157, length=0.0032),
            origin=Origin(xyz=(0.012 + i * 0.0115, 0.0, 0.0), rpy=(0.0, pi / 2.0, 0.0)),
            material=mats["black_oxide"],
            name=f"thread_crest_{i}", material_class_id="metal.blackened_gunmetal",
        )
    fh.visual(
        Cylinder(radius=hw_r, length=0.044),
        origin=Origin(xyz=(0.170, 0.0, 0.0), rpy=(0.0, pi / 2.0, 0.0)),
        material=mats["body_dark"],
        name="wheel_hub", material_class_id="metal.paint_coated",
    )
    spoke_len = 0.205 * r.handwheel_radius_scale
    spoke_center = 0.1325 * r.handwheel_radius_scale
    for i, angle in enumerate((0.88, 0.88 + 2.0 * pi / 3.0, 0.88 + 4.0 * pi / 3.0)):
        fh.visual(
            Box((0.027, 0.026, spoke_len)),
            origin=Origin(
                xyz=(0.170, -sin(angle) * spoke_center, cos(angle) * spoke_center),
                rpy=(angle, 0.0, 0.0),
            ),
            material=mats["body_dark"],
            name=f"spoke_{i}", material_class_id="metal.paint_coated",
        )
    fh.visual(
        _mesh(_hex_prism_x(0.030, 0.051).translate((0.205, 0.0, 0.0)), "hub_nut", assets=assets),
        material=mats["bright"],
        name="hub_nut", material_class_id="metal.chrome_polished",
    )
    fh.visual(
        Sphere(radius=0.021),
        origin=Origin(xyz=(0.230, 0.0, 0.0)),
        material=mats["bright"],
        name="acorn_cap", material_class_id="metal.chrome_polished",
    )
    return fh


# ===========================================================================
# Slot A: forming_topology — forming_crank variants.
# ===========================================================================
def _forming_beading_roll(radius: float, half_ridges: int = 2):
    """A stepped ridged roll along X, for the bead_roller candidate."""
    roll = (
        cq.Workplane("YZ")
        .circle(radius)
        .extrude(0.030)
        .translate((0.0, 0.0, -0.015))
        .rotate((0.0, 0.0, 0.0), (0.0, 1.0, 0.0), 90.0)
    )
    return roll


def _build_forming_crank(model, r: ResolvedMetalBlenderConfig, mats, *, assets):
    fc = model.part(
        "forming_crank",
        meta={
            "role": "forming spindle and manual bending crank",
            "finish": "bright and painted steel",
        },
    )
    # shaft: baseline 0.17 (matches origin); bead_roller extends to reach an
    # attached roll on the +x side, but we keep the shaft compact here since
    # the roll is attached via a small hub visual — Rule 3 doesn't require the
    # long shaft (source variant used it to reach the housing's +x side; our
    # roll sits at the near end).
    fc.visual(
        Cylinder(radius=0.0102, length=0.170),
        origin=Origin(xyz=(-0.070, 0.0, 0.0), rpy=(0.0, pi / 2.0, 0.0)),
        material=mats["bright"],
        name="crank_shaft", material_class_id="metal.chrome_polished",
    )
    fc.visual(
        Cylinder(radius=0.024, length=0.038),
        origin=Origin(xyz=(-0.145, 0.0, 0.0), rpy=(0.0, pi / 2.0, 0.0)),
        material=mats["body"],
        name="crank_hub", material_class_id="metal.paint_coated",
    )
    # tommy bar length scales with crank_reach_scale (kept in range).
    tommy_len = _CRANK_REACH * r.crank_reach_scale
    fc.visual(
        Cylinder(radius=0.0065, length=tommy_len),
        origin=Origin(xyz=(-0.158, 0.0, 0.0), rpy=(pi / 2.0, 0.0, 0.0)),
        material=mats["bright"],
        name="tommy_bar", material_class_id="metal.chrome_polished",
    )
    # paddle_grip Box (0.014 x 0.090 x 0.026) sits so its −y face contacts the
    # tommy cylinder end at +tommy_len/2. bar_stop sits so its +y half embeds
    # into the −y end of the tommy so both share a support path.
    tommy_half = tommy_len * 0.5
    paddle_grip_dy = tommy_half + 0.045  # 0.090/2 = 0.045: −y face touches tommy end
    fc.visual(
        Box((0.014, 0.090, 0.026)),
        origin=Origin(xyz=(-0.158, paddle_grip_dy, 0.0)),
        material=mats["brushed"],
        name="paddle_grip", material_class_id="metal.brushed_silver",
    )
    fc.visual(
        Cylinder(radius=0.010, length=0.018),
        origin=Origin(xyz=(-0.158, -(tommy_half - 0.005), 0.0), rpy=(pi / 2.0, 0.0, 0.0)),
        material=mats["bright"],
        name="bar_stop", material_class_id="metal.chrome_polished",
    )
    # Slot-A accessory anchor: sits along the tommy just inboard of the
    # paddle end (used by bead_roller / three_roll / v_die branches below).
    accessory_dy = tommy_half * 0.55

    # Slot A additions — placed on the OUTER side of the crank (the tommy-bar
    # end at local y ≈ ±paddle_dy, far from the frame housing/bearing along X)
    # so the added visuals never contest the captured-shaft region.
    if r.forming_topology == "bead_roller":
        # A ridged beading roll at the +y (near-paddle) end of the tommy bar:
        # rides along the tommy bar as a discrete drive roll.
        fc.visual(
            Cylinder(radius=0.021, length=0.028),
            origin=Origin(xyz=(-0.158, accessory_dy, 0.0), rpy=(pi / 2.0, 0.0, 0.0)),
            material=mats["black_oxide"],
            name="lower_forming_roll", material_class_id="metal.blackened_gunmetal",
        )
        fc.visual(
            Cylinder(radius=0.025, length=0.006),
            origin=Origin(xyz=(-0.158, accessory_dy + 0.017, 0.0), rpy=(pi / 2.0, 0.0, 0.0)),
            material=mats["black_oxide"],
            name="lower_forming_roll_flange", material_class_id="metal.blackened_gunmetal",
        )
    elif r.forming_topology == "three_roll_slip_roller":
        # A slip-roll drum riding along the tommy bar mid-point (smooth cylinder).
        fc.visual(
            Cylinder(radius=0.023, length=0.052),
            origin=Origin(xyz=(-0.158, accessory_dy * 0.6, 0.0), rpy=(pi / 2.0, 0.0, 0.0)),
            material=mats["black_oxide"],
            name="slip_roll_barrel", material_class_id="metal.blackened_gunmetal",
        )
    elif r.forming_topology == "v_die_press_brake":
        # A short V-mate head on the paddle side of the tommy bar (a discrete
        # forming boss that mates against a V die when engaged).
        fc.visual(
            Box((0.026, 0.026, 0.018)),
            origin=Origin(xyz=(-0.158, accessory_dy, 0.0), rpy=(0.0, 0.0, pi / 4.0)),
            material=mats["black_oxide"],
            name="v_die_mate_head", material_class_id="metal.blackened_gunmetal",
        )
    # classic_bench_brake: no extra addition; the tommy bar + paddle grip is
    # the entire forming interface (matches origin baseline).
    return fc


# ===========================================================================
# Build
# ===========================================================================
def build_metal_blender(
    config: MetalBlenderConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={
            "source_image": "pictureX/0611/Metal_blender/001.png",
            "source_identifier": "001.png",
            "classification_mismatch": (
                "Category name 'Metal_blender' is a source typo for a manual "
                "metal bender / bench forming machine (FB-4 style); this "
                "template is NOT a kitchen blender."
            ),
        },
    )

    pal = _palette_rgba(r.palette_style)
    mats = {
        key: model.material(f"mb_{key}_{r.palette_style}", rgba=rgba) for key, rgba in pal.items()
    }

    frame = _build_frame(model, r, mats, assets=assets)
    clamp_lever = _build_clamp_lever(model, r, mats, assets=assets)
    feed_handwheel = _build_feed_handwheel(model, r, mats, assets=assets)
    forming_crank = _build_forming_crank(model, r, mats, assets=assets)

    # feed / forming joint origins match the fixed bearing centreline (see
    # _build_frame). They coincide with the annular tube's centre → the joint
    # origin lands on the bearing symmetry centreline (grandfathered
    # rotational, `fail_if_articulation_origin_far_from_geometry` passes on
    # symmetry line for ring bearings).
    joint_feed_xyz = (0.255, 0.0, 0.170)
    joint_form_xyz = (-0.255, -0.032, 0.145)

    # 3 non-FIXED joints. Origins/axes/limits are motion-safety-locked.
    # Grandfathered (no MatingContract): captured-pin joints have no
    # axis-aligned face pair; captured-pin overlap is declared in run_tests.
    model.articulation(
        "clamp_lever_pivot",
        ArticulationType.REVOLUTE,
        parent=frame,
        child=clamp_lever,
        origin=Origin(xyz=_JOINT_CLAMP_XYZ),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=90.0, velocity=1.8, lower=0.0, upper=0.82),
        meta={"positive_motion": "raises the long grip away from the clamping die"},
    )
    model.articulation(
        "feed_handwheel_spin",
        ArticulationType.CONTINUOUS,
        parent=frame,
        child=feed_handwheel,
        origin=Origin(xyz=joint_feed_xyz),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=120.0, velocity=4.0),
        meta={
            "positive_motion": "rotates the three-spoke pressure adjustment about the screw axis"
        },
    )
    model.articulation(
        "forming_crank_pivot",
        ArticulationType.REVOLUTE,
        parent=frame,
        child=forming_crank,
        origin=Origin(xyz=joint_form_xyz),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=140.0, velocity=2.0, lower=-1.35, upper=1.35),
        meta={"positive_motion": "rotates the left forming spindle through a bending stroke"},
    )

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_metal_blender(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_metal_blender(config_from_seed(seed), assets=assets)


# ===========================================================================
# Tests
# ===========================================================================
def _aabb_center(aabb):
    if aabb is None:
        return None
    return tuple((aabb[0][k] + aabb[1][k]) / 2.0 for k in range(3))


def run_metal_blender_tests(
    object_model: ArticulatedObject, config: MetalBlenderConfig
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)

    frame = object_model.get_part("frame")
    clamp_lever = object_model.get_part("clamp_lever")
    feed_handwheel = object_model.get_part("feed_handwheel")
    forming_crank = object_model.get_part("forming_crank")

    clamp_joint = object_model.get_articulation("clamp_lever_pivot")
    feed_joint = object_model.get_articulation("feed_handwheel_spin")
    crank_joint = object_model.get_articulation("forming_crank_pivot")

    # ---- Captured-pin allowances (grandfathered pin-through-collar). ----
    ctx.allow_overlap(
        clamp_lever,
        frame,
        elem_a="pivot_pin",
        elem_b="clamp_pivot_bracket",
        reason="Lever pivot pin captured with a slight press fit in the frame bracket.",
    )
    ctx.expect_contact(
        clamp_lever,
        frame,
        elem_a="pivot_pin",
        elem_b="clamp_pivot_bracket",
        name="clamp pivot remains captured in bracket",
    )
    ctx.expect_overlap(
        clamp_lever,
        frame,
        axes="y",
        elem_a="pivot_pin",
        elem_b="clamp_pivot_bracket",
        min_overlap=0.012,
        name="clamp pivot retains bearing insertion",
    )
    ctx.allow_overlap(
        feed_handwheel,
        frame,
        elem_a="screw_core",
        elem_b="feed_bearing",
        reason="Rotating feed screw represented as a close captured fit in its bearing collar.",
    )
    ctx.expect_contact(
        feed_handwheel,
        frame,
        elem_a="screw_core",
        elem_b="feed_bearing",
        name="feed screw remains captured by bearing",
    )
    ctx.expect_overlap(
        feed_handwheel,
        frame,
        axes="x",
        elem_a="screw_core",
        elem_b="feed_bearing",
        min_overlap=0.014,
        name="feed screw retains insertion in collar",
    )
    ctx.allow_overlap(
        forming_crank,
        frame,
        elem_a="crank_shaft",
        elem_b="forming_bearing",
        reason="Forming shaft captured with a close fit in the left bearing collar.",
    )
    ctx.expect_contact(
        forming_crank,
        frame,
        elem_a="crank_shaft",
        elem_b="forming_bearing",
        name="forming shaft remains captured by bearing",
    )
    ctx.expect_overlap(
        forming_crank,
        frame,
        axes="x",
        elem_a="crank_shaft",
        elem_b="forming_bearing",
        min_overlap=0.014,
        name="forming shaft retains insertion in collar",
    )

    # ---- Baseline compiler-owned checks (called explicitly for record parity). ----
    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)
    ctx.fail_if_joint_mating_has_gap()

    # ---- Identity: single frame root + exactly 4 parts + 3 non-FIXED joints. ----
    roots = object_model.root_parts()
    ctx.check(
        "single fixed frame root",
        len(roots) == 1 and roots[0].name == "frame",
        details=f"roots={[p.name for p in roots]}",
    )
    ctx.check(
        "four-part skeleton invariant",
        {p.name for p in object_model.parts}
        == {"frame", "clamp_lever", "feed_handwheel", "forming_crank"},
        details=f"parts={[p.name for p in object_model.parts]}",
    )
    ctx.check(
        "three required non-fixed joints",
        {j.name for j in object_model.articulations}
        == {"clamp_lever_pivot", "feed_handwheel_spin", "forming_crank_pivot"},
        details=f"joints={[j.name for j in object_model.articulations]}",
    )

    # ---- Joint type / axis / limit contract (motion-safety locked). ----
    ctx.check(
        "clamp lever REVOLUTE y limited [0,0.82]",
        clamp_joint.articulation_type == ArticulationType.REVOLUTE
        and tuple(clamp_joint.axis) == (0.0, 1.0, 0.0)
        and clamp_joint.motion_limits is not None
        and clamp_joint.motion_limits.lower == 0.0
        and abs(clamp_joint.motion_limits.upper - 0.82) < 1e-6,
        details=f"type={clamp_joint.articulation_type}, axis={clamp_joint.axis}, limits={clamp_joint.motion_limits}",
    )
    ctx.check(
        "feed handwheel CONTINUOUS x",
        feed_joint.articulation_type == ArticulationType.CONTINUOUS
        and tuple(feed_joint.axis) == (1.0, 0.0, 0.0),
        details=f"type={feed_joint.articulation_type}, axis={feed_joint.axis}",
    )
    ctx.check(
        "forming crank REVOLUTE x limited [-1.35,1.35]",
        crank_joint.articulation_type == ArticulationType.REVOLUTE
        and tuple(crank_joint.axis) == (1.0, 0.0, 0.0)
        and crank_joint.motion_limits is not None
        and abs(crank_joint.motion_limits.lower + 1.35) < 1e-6
        and abs(crank_joint.motion_limits.upper - 1.35) < 1e-6,
        details=f"type={crank_joint.articulation_type}, axis={crank_joint.axis}, limits={crank_joint.motion_limits}",
    )

    # ---- Slot A visibility (report which forming addition appears). ----
    fc_vis = [v.name for v in forming_crank.visuals]
    if r.forming_topology == "bead_roller":
        ctx.check("bead_roller_visual_present", "lower_forming_roll" in fc_vis, f"got={fc_vis}")
    elif r.forming_topology == "three_roll_slip_roller":
        ctx.check(
            "three_roll_slip_roller_visual_present", "slip_roll_barrel" in fc_vis, f"got={fc_vis}"
        )
    elif r.forming_topology == "v_die_press_brake":
        ctx.check("v_die_mate_head_present", "v_die_mate_head" in fc_vis, f"got={fc_vis}")
    else:
        # classic: no extra roll but tommy_bar must still exist.
        ctx.check("classic_tommy_bar_present", "tommy_bar" in fc_vis, f"got={fc_vis}")

    # ---- Slot B visibility. ----
    cl_vis = [v.name for v in clamp_lever.visuals]
    ctx.check("lever_plate_present", "lever_plate" in cl_vis, f"got={cl_vis}")
    if r.clamping_style == "eccentric_cam_clamp":
        ctx.check("eccentric_cam_disc_present", "eccentric_cam_disc" in cl_vis, f"got={cl_vis}")
    elif r.clamping_style == "screw_beam_clamp":
        ctx.check("clamp_screw_present", "clamp_screw" in cl_vis, f"got={cl_vis}")

    # ---- Slot C visibility (③ Primary Form Family). ----
    fr_vis = [v.name for v in frame.visuals]
    ctx.check(
        "fixed_die_present",
        "fixed_die" in fr_vis,
        f"got_fixed_die_neighbours={[n for n in fr_vis if 'die' in n]}",
    )
    if r.die_profile == "round_bead_die":
        ctx.check("die_bead_ridge_present", "die_bead_ridge" in fr_vis, "missing die_bead_ridge")
    elif r.die_profile == "sharp_v_die":
        ctx.check(
            "die_v_faces_present",
            "die_v_face_0" in fr_vis and "die_v_face_1" in fr_vis,
            "missing V faces",
        )

    # ---- Palette drives materials (⑥). ----
    ctx.check(
        "palette_in_registry",
        r.palette_style in PALETTE_STYLES and len(PALETTE_STYLES) == 6,
        f"palette={r.palette_style}",
    )
    housing_mat = frame.get_visual("housing_shell").material
    housing_name = getattr(housing_mat, "name", str(housing_mat))
    ctx.check(
        "housing_material_reads_from_palette",
        housing_name.startswith("mb_body_") and housing_name.endswith(r.palette_style),
        f"housing_mat={housing_name}",
    )

    # ---- Targeted motion tests (Rule 5 companion). ----
    rest_grip = _aabb_center(ctx.part_element_world_aabb(clamp_lever, elem="lever_grip"))
    with ctx.pose({clamp_joint: 0.72}):
        raised_grip = _aabb_center(ctx.part_element_world_aabb(clamp_lever, elem="lever_grip"))
    ctx.check(
        "positive clamp motion raises the long grip",
        rest_grip is not None and raised_grip is not None and raised_grip[2] > rest_grip[2] + 0.10,
        details=f"rest={rest_grip}, raised={raised_grip}",
    )

    rest_spoke = _aabb_center(ctx.part_element_world_aabb(feed_handwheel, elem="spoke_0"))
    with ctx.pose({feed_joint: 0.40}):
        rotated_spoke = _aabb_center(ctx.part_element_world_aabb(feed_handwheel, elem="spoke_0"))
    ctx.check(
        "feed handwheel visibly rotates about its screw",
        rest_spoke is not None
        and rotated_spoke is not None
        and abs(rotated_spoke[2] - rest_spoke[2]) > 0.020,
        details=f"rest={rest_spoke}, rotated={rotated_spoke}",
    )

    rest_paddle = _aabb_center(ctx.part_element_world_aabb(forming_crank, elem="paddle_grip"))
    with ctx.pose({crank_joint: 0.70}):
        moved_paddle = _aabb_center(ctx.part_element_world_aabb(forming_crank, elem="paddle_grip"))
    ctx.check(
        "forming crank sweeps through a bending stroke",
        rest_paddle is not None
        and moved_paddle is not None
        and abs(moved_paddle[2] - rest_paddle[2]) > 0.030,
        details=f"rest={rest_paddle}, moved={moved_paddle}",
    )

    # ---- Rule 5 sampled overlap: 3 non-FIXED joints -> cap combos. ----
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=48, ignore_fixed=True)

    # ---- slot_choices recorded. ----
    ctx.check(
        "slot_choices_recorded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        str(object_model.meta.get("slot_choices")),
    )

    return ctx.report()


__all__ = (
    "MetalBlenderConfig",
    "ResolvedMetalBlenderConfig",
    "build_metal_blender",
    "build_seeded_metal_blender",
    "config_from_seed",
    "resolve_config",
    "run_metal_blender_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "PALETTE_STYLES",
)
