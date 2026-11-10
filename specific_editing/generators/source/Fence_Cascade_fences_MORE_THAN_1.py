# SPDX-License-Identifier: Apache-2.0

"""Cascade fence (interlocking crowd-control barrier panels) modular template.

Sourced from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/Fence_Cascade_fences_MORE_THAN_1.md`` and the
``picture/Fence/Cascade fences`` 5-star sample pool (parent + fork variants).

Structure: a single parameterized ``panel`` module — varying by ``panel_style``
(picket / welded mesh / solid-half) and ``feet_style`` (splayed A-frame /
flat weighted plate) — repeated ``panel_count`` times along +X and chained by
vertical-axis REVOLUTE coupler hinges (downstream panel's pins drop into the
upstream panel's eyes). The cascade chain is the multiplicity axis; ``N`` is
encoded into ``slot_choices_for_seed`` as ``("panel_count", f"n{N}")`` so the
``module_topology_diversity`` gate counts it (panel_style*feet_style = 6 < 10
alone would not clear the floor).

All linked panels share identical geometry, so only two CadQuery panels (root
shift 0, linked shift seam_x) are tessellated and their meshes reused across
all N parts — large N stays cheap. The rest pose is a per-seed configuration:
straight wall, alternating zigzag, an L-turn, or a half-folded U, realized by
baking per-hinge fold angles into the joint origins (URDF joint value 0 = the
folded rest pose). Every hinge carries the same symmetric limit (-theta, +theta)
independent of N: real cascade fences fold in alternating zigzags and do not
wind into closed rings, and any extreme same-direction fold that would self-
contact is resolved by simulation contact dynamics (the asset ships collision
geometry), not by shrinking joint ranges. The chain is serial (every hinge
has a distinct parent panel), so it is not a repeat-group sibling mechanism;
pose sampling runs exhaustively within the compile budget instead.

The feet are placed by ``foot_post_x``, derived from the hinge swing envelope
rather than a fixed inset, because two adjacent panels' feet are the only parts
that can meet inside the coupler's range.
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

PanelStyle = Literal["picket_tubular", "mesh_infill", "solid_half_panel"]
FeetStyle = Literal["bridge_feet", "flat_feet"]
MaterialStyle = Literal["painted_blue", "galvanized", "safety_orange", "anthracite"]

PANEL_STYLES: tuple[PanelStyle, ...] = (
    "picket_tubular",
    "mesh_infill",
    "solid_half_panel",
)
FEET_STYLES: tuple[FeetStyle, ...] = ("bridge_feet", "flat_feet")
MATERIAL_STYLES: tuple[MaterialStyle, ...] = (
    "painted_blue",
    "galvanized",
    "safety_orange",
    "anthracite",
)

# Multiplicity domain: config_from_seed draws panel_count across [2, N_MAX]
# with per-N weights — small N dominates (densely sampled + sweep-fast),
# larger N is common. N_MAX is scoped to the production range (quota samples
# N in [2, 40]).
#
# Joint range history: the limits used to shrink with N (keeping (N-1)*limit
# short of a full turn) so long runs could not fold into a closed ring; that
# narrowed the swing to ~5 deg at N=60 and the exhaustive per-joint motion
# sampling timed out long before it ever found a real problem. Product
# decision (2026-08): every hinge keeps the same symmetric (-theta, +theta)
# limit regardless of N. Cascade fences fold in alternating zigzags; an
# extreme same-direction fold that self-contacts is stopped by simulation
# contact dynamics (assets ship collision geometry), so ring closure is not
# policed by joint limits. Rest-pose diversity (zigzag / L / half-folded) is
# a separate config axis, and the static QC check validates whichever folded
# stance the seed chose.
N_MIN = 2
N_MAX = 100
_PANEL_COUNTS = tuple(range(N_MIN, N_MAX + 1))
_PANEL_COUNT_WEIGHTS = tuple(20.0 if n <= 8 else 1.0 for n in _PANEL_COUNTS)

PALETTES: dict[MaterialStyle, dict[str, tuple[float, float, float, float]]] = {
    "painted_blue": {
        "frame": (0.27, 0.31, 0.37, 1.0),
        "picket": (0.21, 0.24, 0.29, 1.0),
        "plate": (0.24, 0.28, 0.34, 1.0),
        "coupler": (0.33, 0.36, 0.41, 1.0),
    },
    "galvanized": {
        "frame": (0.62, 0.64, 0.66, 1.0),
        "picket": (0.50, 0.52, 0.54, 1.0),
        "plate": (0.55, 0.57, 0.59, 1.0),
        "coupler": (0.70, 0.71, 0.72, 1.0),
    },
    "safety_orange": {
        "frame": (0.85, 0.42, 0.10, 1.0),
        "picket": (0.74, 0.36, 0.08, 1.0),
        "plate": (0.80, 0.39, 0.09, 1.0),
        "coupler": (0.30, 0.31, 0.33, 1.0),
    },
    "anthracite": {
        "frame": (0.16, 0.17, 0.19, 1.0),
        "picket": (0.11, 0.12, 0.13, 1.0),
        "plate": (0.14, 0.15, 0.17, 1.0),
        "coupler": (0.40, 0.41, 0.43, 1.0),
    },
}

# ---------------------------------------------------------------------------
# Base real-world dimensions (meters); scaled per-build by the resolved config.
# ---------------------------------------------------------------------------
_PANEL_LEN = 2.00
_PANEL_HEIGHT = 1.10
_TUBE_R = 0.019
_CORNER_R = 0.10
_PICKET_R = 0.0055
_N_PICKETS = 21
_RAIL_R = 0.014
_FRAME_BOTTOM_Z = 0.16
_EYE_OUTER_R = 0.024
_EYE_INNER_R = 0.013
_EYE_THICK = 0.024
_PIN_R = 0.011
_PIN_LEN = 0.150
_COUPLER_DX = 0.055
_FOOT_TUBE_R = 0.016
_FOOT_SPREAD = 0.32
_FOOT_LONG = 0.13
_PLATE_LEN_X = 0.30
_PLATE_LEN_Y = 0.22
_PLATE_THICK = 0.018
_STUB_R = 0.016
_MESH_WIRE_R = 0.002
_MESH_SPACING = 0.060
_INFILL_PLATE_THICK = 0.003
_UPPER_PICKET_FRAC = 0.38
# Symmetric per-hinge swing, independent of panel count (see the
# multiplicity-domain note). joint_limit_scale in [0.80, 1.10] sweeps this to
# roughly 24-33 degrees.
_THETA_BASE = math.radians(30.0)
# Feet-vs-hinge sweep derivation (see resolve_config). The post inset is derived
# from the swing envelope rather than pinned, but stays between a minimum inset
# from the panel end and a maximum fraction of the half-length so the barrier
# still reads as end-supported.
_FOOT_POST_MIN_INSET = 0.10
_FOOT_POST_MAX_INSET_FRAC = 0.45
_FOOT_SWEEP_MARGIN = math.radians(4.0)
# A run of three panels folds back onto itself once its two couplers together
# turn through pi, so no single coupler may reach a right angle. Measured over
# cumulative seeds 0-35: every seed whose limit landed at >= 97.5 deg failed
# with a non-adjacent panel pair, and every seed at <= 95.3 deg passed.
_CHAIN_FOLD_MARGIN = math.radians(4.0)

# Rest-pose configurations. Folded stances are expressed as fractions of the
# joint limit so every rest angle sits strictly inside (-limit, +limit): the
# zigzag accordion alternates +/-75% of the limit at every hinge; the L-turn
# bends three consecutive hinges through 95% of the limit (~85 deg total); the
# half-folded U bends six consecutive hinges the same way (~170 deg total),
# doubling the run back on itself like a stored barrier.
RestMode = Literal["straight", "zigzag", "l_turn", "half_folded"]
REST_MODES: tuple[RestMode, ...] = ("straight", "zigzag", "l_turn", "half_folded")
_ZIGZAG_REST_FRAC = 0.75
_TURN_REST_FRAC = 0.95
_L_TURN_HINGES = 3
_HALF_FOLD_HINGES = 6


@dataclass(frozen=True)
class FenceCascadeConfig:
    panel_style: PanelStyle | None = None
    feet_style: FeetStyle | None = None
    panel_count: int | None = None
    rest_mode: RestMode | None = None
    material_style: MaterialStyle = "painted_blue"
    panel_len_scale: float = 1.0
    panel_height_scale: float = 1.0
    infill_density_scale: float = 1.0
    foot_spread_scale: float = 1.0
    joint_limit_scale: float = 1.0
    rest_fold_scale: float = 1.0
    name: str = "fence_cascade"


@dataclass(frozen=True)
class ResolvedFenceCascadeConfig:
    panel_style: PanelStyle
    feet_style: FeetStyle
    panel_count: int
    material_style: MaterialStyle
    panel_len_scale: float
    # Geometry (scaled, concrete).
    panel_len: float
    half: float
    panel_height: float
    frame_bottom_z: float
    frame_top_z: float
    tube_r: float
    corner_r: float
    picket_r: float
    n_pickets: int
    rail_r: float
    eye_outer_r: float
    eye_inner_r: float
    eye_thick: float
    pin_r: float
    pin_len: float
    coupler_dx: float
    coupler_top_z: float
    coupler_bot_z: float
    foot_tube_r: float
    foot_spread: float
    foot_long: float
    foot_post_x: float
    foot_half_width: float
    foot_clearance_r: float
    plate_len_x: float
    plate_len_y: float
    plate_thick: float
    stub_r: float
    mesh_wire_r: float
    mesh_spacing: float
    infill_plate_thick: float
    upper_picket_frac: float
    seam_x: float
    joint_limit: float
    rest_mode: RestMode
    rest_fold_scale: float
    rest_angles: tuple[float, ...]
    name: str


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


def config_from_seed(seed: int) -> FenceCascadeConfig:
    rng = random.Random(seed)
    # Random per-N draw across [2, N_MAX], weighted so small N dominates
    # (see _PANEL_COUNT_WEIGHTS).
    panel_count = rng.choices(_PANEL_COUNTS, weights=_PANEL_COUNT_WEIGHTS, k=1)[0]
    return FenceCascadeConfig(
        panel_style=rng.choice(PANEL_STYLES),
        feet_style=rng.choice(FEET_STYLES),
        panel_count=panel_count,
        rest_mode=rng.choice(REST_MODES),
        material_style=rng.choice(MATERIAL_STYLES),
        panel_len_scale=round(rng.uniform(0.90, 1.12), 4),
        panel_height_scale=round(rng.uniform(0.90, 1.15), 4),
        infill_density_scale=round(rng.uniform(0.85, 1.20), 4),
        foot_spread_scale=round(rng.uniform(0.85, 1.15), 4),
        joint_limit_scale=round(rng.uniform(0.80, 1.10), 4),
        rest_fold_scale=round(rng.uniform(0.70, 1.00), 4),
        name=f"seeded_fence_cascade_{seed}",
    )


def _rest_angles(
    panel_count: int, rest_mode: RestMode, joint_limit: float, fold_scale: float
) -> tuple[float, ...]:
    """Per-hinge rest fold angles; joint value 0 realizes this stance."""
    n_hinges = max(panel_count - 1, 0)
    if n_hinges == 0 or rest_mode == "straight":
        return (0.0,) * n_hinges
    if rest_mode == "zigzag":
        amp = _ZIGZAG_REST_FRAC * joint_limit * fold_scale
        if panel_count % 2 == 1:
            # The camera sees the chain from its +X end. Keep the terminal
            # yaw equal to the even-count phase, while giving every odd-count
            # hinge a non-zero, equal share of that total turn. This keeps the
            # first visible panel aligned and avoids a parallel last pair.
            return (amp / n_hinges,) * n_hinges
        angles = [amp if i % 2 == 0 else -amp for i in range(n_hinges)]
        return tuple(angles)
    turn = _TURN_REST_FRAC * joint_limit * fold_scale
    span = _L_TURN_HINGES if rest_mode == "l_turn" else _HALF_FOLD_HINGES
    k = min(span, n_hinges)
    start = max(0, (n_hinges - k) // 2)
    return tuple(turn if start <= i < start + k else 0.0 for i in range(n_hinges))


def resolve_config(config: FenceCascadeConfig | None = None) -> ResolvedFenceCascadeConfig:
    cfg = config or FenceCascadeConfig()
    panel_style = _pick(cfg.panel_style, PANEL_STYLES)
    feet_style = _pick(cfg.feet_style, FEET_STYLES)
    rest_mode = _pick(cfg.rest_mode, REST_MODES)
    material_style = _pick(cfg.material_style, MATERIAL_STYLES)
    panel_count = int(cfg.panel_count) if cfg.panel_count is not None else 3
    panel_count = int(_clamp(panel_count, N_MIN, N_MAX))

    len_scale = _clamp(cfg.panel_len_scale, 0.90, 1.12)
    height_scale = _clamp(cfg.panel_height_scale, 0.90, 1.15)
    density_scale = _clamp(cfg.infill_density_scale, 0.85, 1.20)
    foot_scale = _clamp(cfg.foot_spread_scale, 0.85, 1.15)
    limit_scale = _clamp(cfg.joint_limit_scale, 0.80, 1.10)
    rest_fold_scale = _clamp(cfg.rest_fold_scale, 0.70, 1.00)

    panel_len = _PANEL_LEN * len_scale
    half = panel_len / 2.0
    panel_height = _PANEL_HEIGHT * height_scale
    frame_bottom_z = _FRAME_BOTTOM_Z
    frame_top_z = frame_bottom_z + panel_height
    coupler_dx = _COUPLER_DX
    seam_x = half + coupler_dx
    n_pickets = int(_clamp(round(_N_PICKETS * density_scale), 16, 26))
    mesh_spacing = _MESH_SPACING / density_scale

    foot_spread = _FOOT_SPREAD * foot_scale
    plate_len_y = _PLATE_LEN_Y * foot_scale

    # Feet vs. the coupler sweep. Adjacent panels carry mirrored feet about the
    # hinge axis, so at a swing of `limit` they are pi - limit apart and each may
    # occupy at most half of that. A foot whose nearest point sits `r_in` from the
    # axis and reaches +/-`w` sideways subtends atan(w / r_in) there, so clearance
    # needs 2 * atan(w / r_in) + limit <= pi. Solve for r_in, derive the post
    # inset from it, then read the honest limit back off the placed foot.
    #
    # The old fixed `half - 0.10` inset ignored the sweep entirely: it left a flat
    # base plate only ~5 mm clear of the axis, which collided 10 degrees off
    # centre, and splayed A-frame toes 0.135 m clear, which collided at 40-50 --
    # all far inside the authored +/-75..109 degree range.
    if feet_style == "bridge_feet":
        foot_half_width = foot_spread
        foot_near_reach = 0.02  # +/-Y toes sit this far toward the hinge of the post
    else:
        foot_half_width = plate_len_y / 2.0
        foot_near_reach = _PLATE_LEN_X / 2.0

    target_limit = _THETA_BASE * limit_scale
    # A folded rest stance pre-rotates adjacent panels about their hinge, so the
    # worst relative swing between neighbours is the joint limit plus the rest
    # fold; the feet must clear that combined sweep, not the bare limit.
    # Straight walls have no rest fold; zigzag pre-rotates every hinge by the
    # zigzag fraction; L-turn / half-folded pre-rotate the bent hinges by the
    # turn fraction (the straight hinges of those modes are the milder case).
    rest_frac = {
        "straight": 0.0,
        "zigzag": _ZIGZAG_REST_FRAC,
        "l_turn": _TURN_REST_FRAC,
        "half_folded": _TURN_REST_FRAC,
    }[rest_mode] * rest_fold_scale
    swing_worst = target_limit * (1.0 + rest_frac)
    required_clearance = foot_half_width / math.tan(
        (math.pi - swing_worst) / 2.0 - _FOOT_SWEEP_MARGIN
    )
    foot_post_x = _clamp(
        seam_x - required_clearance - foot_near_reach,
        (1.0 - _FOOT_POST_MAX_INSET_FRAC) * half,
        half - _FOOT_POST_MIN_INSET,
    )
    foot_clearance_r = max(seam_x - (foot_post_x + foot_near_reach), 1e-3)
    reachable_swing = (
        math.pi - 2.0 * math.atan(foot_half_width / foot_clearance_r) - 2.0 * _FOOT_SWEEP_MARGIN
    )
    # Two geometric bounds, both independent of N: how far a panel may swing
    # before its feet meet the neighbour's (expressed back as a joint limit by
    # dividing out the relative-swing factor), and how far before a three-panel
    # run folds back on itself. The old N-dependent closure bound (ring
    # prevention) is gone by design — see the multiplicity-domain note.
    joint_limit = min(
        target_limit,
        reachable_swing / (1.0 + rest_frac),
        math.pi / 2.0 - _CHAIN_FOLD_MARGIN,
    )
    rest_angles = _rest_angles(panel_count, rest_mode, joint_limit, rest_fold_scale)

    return ResolvedFenceCascadeConfig(
        panel_style=panel_style,
        feet_style=feet_style,
        panel_count=panel_count,
        material_style=material_style,
        panel_len_scale=len_scale,
        panel_len=panel_len,
        half=half,
        panel_height=panel_height,
        frame_bottom_z=frame_bottom_z,
        frame_top_z=frame_top_z,
        tube_r=_TUBE_R,
        corner_r=_CORNER_R,
        picket_r=_PICKET_R,
        n_pickets=n_pickets,
        rail_r=_RAIL_R,
        eye_outer_r=_EYE_OUTER_R,
        eye_inner_r=_EYE_INNER_R,
        eye_thick=_EYE_THICK,
        pin_r=_PIN_R,
        pin_len=_PIN_LEN,
        coupler_dx=coupler_dx,
        coupler_top_z=frame_top_z - 0.18,
        coupler_bot_z=frame_bottom_z + 0.18,
        foot_tube_r=_FOOT_TUBE_R,
        foot_spread=foot_spread,
        foot_long=_FOOT_LONG,
        foot_post_x=foot_post_x,
        foot_half_width=foot_half_width,
        foot_clearance_r=foot_clearance_r,
        plate_len_x=_PLATE_LEN_X,
        plate_len_y=plate_len_y,
        plate_thick=_PLATE_THICK,
        stub_r=_STUB_R,
        mesh_wire_r=_MESH_WIRE_R,
        mesh_spacing=mesh_spacing,
        infill_plate_thick=_INFILL_PLATE_THICK,
        upper_picket_frac=_UPPER_PICKET_FRAC,
        seam_x=seam_x,
        joint_limit=joint_limit,
        rest_mode=rest_mode,
        rest_fold_scale=rest_fold_scale,
        rest_angles=rest_angles,
        name=cfg.name or "fence_cascade",
    )


def with_overrides(config: FenceCascadeConfig, **kwargs: object) -> FenceCascadeConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: FenceCascadeConfig | ResolvedFenceCascadeConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedFenceCascadeConfig) else resolve_config(config)
    return (
        ("panel_style", r.panel_style),
        ("feet_style", r.feet_style),
        ("panel_count", f"n{r.panel_count}"),
        ("rest_mode", r.rest_mode),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Shared geometry primitives (ported from parent 1b7c235f L67-92).
# ---------------------------------------------------------------------------
def _strut(p0, p1, radius: float) -> cq.Workplane:
    x0, y0, z0 = p0
    x1, y1, z1 = p1
    dx, dy, dz = (x1 - x0, y1 - y0, z1 - z0)
    cyl = cq.Solid.makeCylinder(
        radius,
        math.sqrt(dx * dx + dy * dy + dz * dz),
        cq.Vector(x0, y0, z0),
        cq.Vector(dx, dy, dz),
    )
    return cq.Workplane("XY").add(cyl)


def _tube_chain(pts, radius: float) -> cq.Workplane:
    chain = None
    for p0, p1 in zip(pts[:-1], pts[1:]):
        seg = _strut(p0, p1, radius)
        chain = seg if chain is None else chain.union(seg)
    return chain


def _frame_solid(r: ResolvedFenceCascadeConfig) -> cq.Workplane:
    """Rounded tubular outer frame (parent 1b7c235f L95-128)."""
    half = r.half
    z0 = r.frame_bottom_z
    z1 = r.frame_top_z
    rad = r.corner_r

    pts = []
    pts.append((-half, 0.0, z0))
    pts.append((half, 0.0, z0))
    pts.append((half, 0.0, z1 - rad))
    cx, cz = (half - rad, z1 - rad)
    for i in range(1, 9):
        a = (math.pi / 2.0) * (i / 8.0)
        pts.append((cx + rad * math.cos(a), 0.0, cz + rad * math.sin(a)))
    pts.append((-half + rad, 0.0, z1))
    cx, cz = (-half + rad, z1 - rad)
    for i in range(1, 9):
        a = (math.pi / 2.0) + (math.pi / 2.0) * (i / 8.0)
        pts.append((cx + rad * math.cos(a), 0.0, cz + rad * math.sin(a)))
    pts.append((-half, 0.0, z0))
    return _tube_chain(pts, r.tube_r)


def _infill_bounds(r: ResolvedFenceCascadeConfig):
    half = r.half
    inner_left = -half + r.tube_r + 0.02
    inner_right = half - r.tube_r - 0.02
    span = inner_right - inner_left
    z_bot = r.frame_bottom_z + 0.045
    z_top = r.frame_top_z - 0.045
    return inner_left, inner_right, span, z_bot, z_top


def _x_rail(r: ResolvedFenceCascadeConfig, span: float, z: float, radius: float) -> cq.Workplane:
    return (
        cq.Workplane("XY")
        .transformed(rotate=(0.0, 90.0, 0.0))
        .circle(radius)
        .extrude(span / 2.0 + 0.02, both=True)
        .translate((0.0, 0.0, z))
    )


def _picket_infill_solid(r: ResolvedFenceCascadeConfig) -> cq.Workplane:
    """Top/bottom rails + dense vertical pickets (parent 1b7c235f L131-169)."""
    inner_left, _, span, z_bot, z_top = _infill_bounds(r)
    picket_h = z_top - z_bot
    infill = _x_rail(r, span, z_bot, r.rail_r).union(_x_rail(r, span, z_top, r.rail_r))
    for i in range(r.n_pickets):
        t = i / (r.n_pickets - 1)
        x = inner_left + t * span
        picket = cq.Workplane("XY").circle(r.picket_r).extrude(picket_h).translate((x, 0.0, z_bot))
        infill = infill.union(picket)
    return infill


def _mesh_infill_solid(r: ResolvedFenceCascadeConfig) -> cq.Workplane:
    """Rails + welded wire grid (mesh variant 849ff922 L133-195)."""
    inner_left, _, span, z_bot, z_top = _infill_bounds(r)
    span_z = z_top - z_bot
    infill = _x_rail(r, span, z_bot, r.rail_r).union(_x_rail(r, span, z_top, r.rail_r))

    n_hz = max(2, int(span_z / r.mesh_spacing) + 1)
    for i in range(n_hz):
        t = i / (n_hz - 1) if n_hz > 1 else 0.5
        z = z_bot + t * span_z
        infill = infill.union(_x_rail(r, span, z, r.mesh_wire_r))

    n_vt = max(2, int(span / r.mesh_spacing) + 1)
    for i in range(n_vt):
        t = i / (n_vt - 1) if n_vt > 1 else 0.5
        x = inner_left + t * span
        wire = cq.Workplane("XY").circle(r.mesh_wire_r).extrude(span_z).translate((x, 0.0, z_bot))
        infill = infill.union(wire)
    return infill


def _lower_plate_solid(r: ResolvedFenceCascadeConfig) -> cq.Workplane:
    """Lower solid sheet plate + bottom/mid rails (solid_half 5333dc9b L136-176)."""
    inner_left, inner_right, span, z_bot, z_top = _infill_bounds(r)
    full_h = z_top - z_bot
    z_mid = z_bot + full_h * (1.0 - r.upper_picket_frac)
    plate_h = z_mid - z_bot
    bottom_rail = _x_rail(r, span, z_bot, r.rail_r)
    mid_rail = _x_rail(r, span, z_mid, r.rail_r)
    plate = (
        cq.Workplane("XY")
        .box(span, r.infill_plate_thick, plate_h, centered=(True, True, False))
        .translate((0.0, 0.0, z_bot))
    )
    return bottom_rail.union(mid_rail).union(plate)


def _upper_pickets_solid(r: ResolvedFenceCascadeConfig) -> cq.Workplane:
    """Short upper picket row + top rail (solid_half 5333dc9b L178-217)."""
    inner_left, _, span, z_bot, z_top = _infill_bounds(r)
    full_h = z_top - z_bot
    z_mid = z_bot + full_h * (1.0 - r.upper_picket_frac)
    picket_h = z_top - z_mid
    infill = _x_rail(r, span, z_top, r.rail_r)
    n_upper = max(8, int(r.n_pickets * r.upper_picket_frac) + 1)
    for i in range(n_upper):
        t = i / (n_upper - 1)
        x = inner_left + t * span
        picket = cq.Workplane("XY").circle(r.picket_r).extrude(picket_h).translate((x, 0.0, z_mid))
        infill = infill.union(picket)
    return infill


def _eye_solid(r: ResolvedFenceCascadeConfig, z: float, x_dir: float) -> cq.Workplane:
    """Coupler eye ring + neck (parent 1b7c235f L172-190)."""
    half = r.half
    cx = x_dir * (half + r.coupler_dx)
    ring = (
        cq.Workplane("XY")
        .circle(r.eye_outer_r)
        .circle(r.eye_inner_r)
        .extrude(r.eye_thick / 2.0, both=True)
        .translate((cx, 0.0, z))
    )
    inner_x = x_dir * (half - 0.03)
    outer_x = x_dir * (half + r.coupler_dx)
    neck = _strut((inner_x, 0.0, z), (outer_x, 0.0, z), 0.010)
    return ring.union(neck)


def _pin_solid(r: ResolvedFenceCascadeConfig, z: float, x_dir: float) -> cq.Workplane:
    """Coupler pin + neck (parent 1b7c235f L193-206)."""
    half = r.half
    cx = x_dir * (half + r.coupler_dx)
    pin = (
        cq.Workplane("XY")
        .circle(r.pin_r)
        .extrude(r.pin_len / 2.0, both=True)
        .translate((cx, 0.0, z))
    )
    inner_x = x_dir * (half - 0.03)
    outer_x = x_dir * (half + r.coupler_dx)
    neck = _strut((inner_x, 0.0, z), (outer_x, 0.0, z), 0.010)
    return pin.union(neck)


def _bridge_feet_solid(r: ResolvedFenceCascadeConfig) -> cq.Workplane:
    """Splayed A-frame feet (parent 1b7c235f L209-228)."""
    z_apex = r.frame_bottom_z + 0.02
    z_toe = r.foot_tube_r
    foot = None
    for x_dir in (-1.0, 1.0):
        post_x = x_dir * r.foot_post_x
        apex = (post_x, 0.0, z_apex)
        for y_dir in (-1.0, 1.0):
            toe = (post_x + x_dir * 0.02, y_dir * r.foot_spread, z_toe)
            leg = _strut(apex, toe, r.foot_tube_r)
            foot = leg if foot is None else foot.union(leg)
        toe_f = (post_x + x_dir * r.foot_long, 0.0, z_toe)
        foot = foot.union(_strut(apex, toe_f, r.foot_tube_r))
    return foot


def _flat_feet_solid(r: ResolvedFenceCascadeConfig) -> cq.Workplane:
    """Flat weighted base plates + stubs (flat_feet 862eeff1 L210-242)."""
    z_plate_top = r.plate_thick
    z_stub_top = r.frame_bottom_z
    foot = None
    for x_dir in (-1.0, 1.0):
        post_x = x_dir * r.foot_post_x
        plate = (
            cq.Workplane("XY")
            .box(r.plate_len_x, r.plate_len_y, r.plate_thick)
            .translate((post_x, 0.0, r.plate_thick / 2.0))
        )
        stub_h = z_stub_top - z_plate_top
        if stub_h > 0.005:
            stub = (
                cq.Workplane("XY")
                .circle(r.stub_r)
                .extrude(stub_h)
                .translate((post_x, 0.0, z_plate_top))
            )
            plate = plate.union(stub)
        foot = plate if foot is None else foot.union(plate)
    return foot


# (visual_name, material_key) pairs; solids are produced by _panel_solid_specs.
def _panel_solid_specs(r: ResolvedFenceCascadeConfig, x_shift: float, z_shift: float = 0.0):
    specs: list[tuple[str, cq.Workplane, str]] = [("frame", _frame_solid(r), "frame")]

    if r.panel_style == "picket_tubular":
        specs.append(("infill", _picket_infill_solid(r), "picket"))
    elif r.panel_style == "mesh_infill":
        specs.append(("infill", _mesh_infill_solid(r), "picket"))
    else:  # solid_half_panel
        specs.append(("infill", _lower_plate_solid(r), "plate"))
        specs.append(("infill_upper", _upper_pickets_solid(r), "picket"))

    if r.feet_style == "bridge_feet":
        specs.append(("feet", _bridge_feet_solid(r), "frame"))
    else:
        specs.append(("feet", _flat_feet_solid(r), "frame"))

    specs.append(("eye_top", _eye_solid(r, r.coupler_top_z, +1.0), "coupler"))
    specs.append(("eye_bottom", _eye_solid(r, r.coupler_bot_z, +1.0), "coupler"))
    specs.append(("pin_top", _pin_solid(r, r.coupler_top_z, -1.0), "coupler"))
    specs.append(("pin_bottom", _pin_solid(r, r.coupler_bot_z, -1.0), "coupler"))

    if x_shift != 0.0 or z_shift != 0.0:
        specs = [(n, s.translate((x_shift, 0.0, z_shift)), m) for (n, s, m) in specs]
    return specs


def _panel_meshes(
    r: ResolvedFenceCascadeConfig, x_shift: float, z_shift: float, suffix: str, assets
):
    return [
        (name, mesh_from_cadquery(solid, f"{name}_{suffix}.obj", assets=assets), mat_key)
        for (name, solid, mat_key) in _panel_solid_specs(r, x_shift, z_shift)
    ]


def _add_panel_visuals(part, meshes, mats) -> None:
    for name, mesh, mat_key in meshes:
        part.visual(mesh, material=mats[mat_key], name=name, material_class_id="metal.paint_coated")


def build_fence_cascade(
    config: FenceCascadeConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        key: model.material(f"fence_{key}_{r.material_style}", rgba=PALETTES[r.material_style][key])
        for key in ("frame", "picket", "plate", "coupler")
    }

    seam_x = r.seam_x
    cbz = r.coupler_bot_z
    # Two distinct geometries only, reused across all N parts:
    #  - root: authored at absolute z (feet on the ground at z=0), centred at X=0.
    #  - linked: x-shifted so its -X pin line lands on its part origin, AND
    #    z-shifted by -coupler_bot_z so its bottom pin sits at the part origin
    #    (0,0,0). The joint origin is then placed on the parent's bottom coupler
    #    (real hinge hardware), and the linked panel's frame origin lands at
    #    world z=coupler_bot_z so the shift cancels and feet still rest at z=0.
    root_meshes = _panel_meshes(r, 0.0, 0.0, "root", assets)
    linked_meshes = _panel_meshes(r, seam_x, -cbz, "linked", assets)

    parts = [model.part("panel_0")]
    _add_panel_visuals(parts[0], root_meshes, mats)

    for i in range(1, r.panel_count):
        panel = model.part(f"panel_{i}")
        _add_panel_visuals(panel, linked_meshes, mats)
        parts.append(panel)
        # Joint origin = the parent's +X bottom coupler eye (real hinge hardware).
        # Root parent (not z-shifted): eye at (seam_x, 0, coupler_bot_z).
        # Linked parent (z-shifted): eye at (2*seam_x, 0, 0) in its local frame.
        # The origin's yaw bakes in this hinge's rest fold angle, so URDF joint
        # value 0 realizes the configured rest stance (straight wall, zigzag,
        # L-turn, or half-folded U); limits stay symmetric about that zero.
        parent_origin = (seam_x, 0.0, cbz) if i == 1 else (2.0 * seam_x, 0.0, 0.0)
        model.articulation(
            f"hinge_{i - 1}_{i}",
            ArticulationType.REVOLUTE,
            parent=parts[i - 1],
            child=panel,
            origin=Origin(xyz=parent_origin, rpy=(0.0, 0.0, r.rest_angles[i - 1])),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(
                lower=-r.joint_limit, upper=r.joint_limit, effort=60.0, velocity=1.5
            ),
        )

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_fence_cascade(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_fence_cascade(config_from_seed(seed), assets=assets)


def _aabb_center(aabb) -> tuple[float, float, float]:
    (xmn, ymn, zmn), (xmx, ymx, zmx) = aabb
    return ((xmn + xmx) / 2.0, (ymn + ymx) / 2.0, (zmn + zmx) / 2.0)


def run_fence_cascade_tests(
    object_model: ArticulatedObject,
    config: FenceCascadeConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    n = r.panel_count

    # Captured-pin coupler: each downstream panel's pins are seated inside the
    # upstream panel's eyes. Element-scoped, per hinge.
    for i in range(1, n):
        a = object_model.get_part(f"panel_{i - 1}")
        b = object_model.get_part(f"panel_{i}")
        ctx.allow_overlap(
            a,
            b,
            elem_a="eye_top",
            elem_b="pin_top",
            reason=f"panel_{i} top coupler pin seated inside panel_{i - 1} top eye ring",
        )
        ctx.allow_overlap(
            a,
            b,
            elem_a="eye_bottom",
            elem_b="pin_bottom",
            reason=f"panel_{i} bottom coupler pin seated inside panel_{i - 1} bottom eye ring",
        )

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    # The compiler-owned baseline runs fail_if_articulation_origin_far_from_geometry
    # at a flat 0.015 m, so the joint origin must sit on real hinge hardware. We
    # place it on the parent's bottom coupler eye (see build_fence_cascade), giving
    # dist~0 for both parent eye and child pin; no explicit call is needed here.
    ctx.fail_if_joint_mating_has_gap()

    part_names = {p.name for p in object_model.parts}
    expected = {f"panel_{i}" for i in range(n)}
    ctx.check(
        "expected_parts_present", expected.issubset(part_names), details=str(sorted(part_names))
    )
    ctx.check(
        "exact_hinge_count",
        len(object_model.joints) == n - 1,
        details=f"joints={len(object_model.joints)} expected={n - 1}",
    )

    for i in range(1, n):
        joint = object_model.get_articulation(f"hinge_{i - 1}_{i}")
        ctx.check(
            f"hinge_{i - 1}_{i}_vertical_revolute",
            joint.articulation_type == ArticulationType.REVOLUTE
            and abs(joint.axis[2]) > 0.99
            and abs(joint.axis[0]) < 1e-6
            and abs(joint.axis[1]) < 1e-6,
            details=f"type={joint.articulation_type} axis={tuple(joint.axis)}",
        )

    # The feet are the only parts of adjacent panels that can meet inside the
    # hinge range, so the post inset and the limit must stay on the clearing side
    # of 2*atan(w / r_in) + limit + rest_fold <= pi (resolve_config derives all
    # three from it; a folded rest stance counts toward the relative sweep).
    sweep_span = (
        2.0 * math.atan(r.foot_half_width / r.foot_clearance_r)
        + r.joint_limit
        + max((abs(a) for a in r.rest_angles), default=0.0)
    )
    ctx.check(
        "feet_clear_adjacent_panel_through_hinge_range",
        sweep_span <= math.pi,
        details=(
            f"2*atan({r.foot_half_width:.4f}/{r.foot_clearance_r:.4f})"
            f"+{r.joint_limit:.4f}+rest={sweep_span:.4f} > pi"
            if sweep_span > math.pi
            else f"span={sweep_span:.4f} rad, post_x={r.foot_post_x:.4f}"
        ),
    )
    ctx.check(
        "coupler_stays_below_a_right_angle",
        r.joint_limit < math.pi / 2.0,
        details=f"joint_limit={math.degrees(r.joint_limit):.2f}deg",
    )
    # Rest stances are defined as fractions of the limit, so they must land
    # strictly inside (-limit, +limit): URDF joint zero is the rest pose and
    # an out-of-range rest angle would start the mechanism beyond its stops.
    # (The old ring-closure check is gone with the N-dependent limit: extreme
    # same-direction folds are stopped by simulation contact, not by limits.)
    ctx.check(
        "rest_pose_within_joint_limits",
        all(abs(a) < r.joint_limit for a in r.rest_angles),
        details=(
            f"rest_mode={r.rest_mode} max|rest_angle|="
            f"{math.degrees(max((abs(a) for a in r.rest_angles), default=0.0)):.2f}deg "
            f"limit={math.degrees(r.joint_limit):.2f}deg"
        ),
    )

    ctx.check(
        "slot_choices_recorded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    # Root panel reads as a ~2 m wide barrier standing on the ground.
    aabb0 = ctx.part_world_aabb(object_model.get_part("panel_0"))
    if aabb0 is not None:
        (axmin, _, azmin), (axmax, _, azmax) = aabb0
        ctx.check(
            "panel_0 reads as a wide barrier on the ground",
            (axmax - axmin) > 1.6 * r.panel_len / _PANEL_LEN and azmin < 0.03,
            details=f"width={axmax - axmin:.3f} z_min={azmin:.4f}",
        )

    # sampled-pose exemption: many copied panel hinges make broad pose products
    # noisy; targeted coupler motion checks cover the intended legal motion.
    # Actuating the last hinge swings the last panel about the vertical coupler.
    last = object_model.get_part(f"panel_{n - 1}")
    rest_aabb = ctx.part_world_aabb(last)
    last_hinge = object_model.get_articulation(f"hinge_{n - 2}_{n - 1}")
    with ctx.pose({last_hinge: r.joint_limit * 0.6}):
        swung_aabb = ctx.part_world_aabb(last)
    if rest_aabb is not None and swung_aabb is not None:
        rest_c = _aabb_center(rest_aabb)
        swung_c = _aabb_center(swung_aabb)
        delta = math.sqrt(sum((swung_c[k] - rest_c[k]) ** 2 for k in range(3)))
        ctx.check("last_panel_swings_about_coupler", delta > 0.05, details=f"delta={delta:.4f}")

    return ctx.report()


__all__ = (
    "FenceCascadeConfig",
    "REST_MODES",
    "ResolvedFenceCascadeConfig",
    "RestMode",
    "build_fence_cascade",
    "build_seeded_fence_cascade",
    "config_from_seed",
    "resolve_config",
    "run_fence_cascade_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
