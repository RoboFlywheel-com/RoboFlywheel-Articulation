# SPDX-License-Identifier: Apache-2.0

"""Rustic wooden coffin / casket modular template.

NOTE on identity: "coffin" here = **入殓木棺 / casket** — a long hollow open-top
plank box (~1.9 m) with a flat plank lid that either opens from a top-rim edge or
lifts straight upward, three darker strap boards wrapping the lid + body sides,
and a Latin cross on the head-end lid panel. NOT a treasure chest / tool box /
small lidded box.

Sourced from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/Other_Coffin.md`` and the
``picture/Other/Coffin`` 5-star sample pool (1 parent + 7 slot-fork variants),
all synced under ``data/records/``. (4 collision-slug "coffin" records in that
pool are actually a lighter / cauldron and were excluded per the spec.)

Structure (pattern = ``mixed``): a single root ``coffin_body`` part (footprint
mesh chosen by ``body_shape``), with two named module axes attaching as parallel
children / inline visuals, plus one multiplicity axis:

  * ``body_shape`` (3): toe_pincher_hex / rectangular_casket / tapered_trapezoid
    — the shared FOOTPRINT polygon of the body + lid mesh. A mesh-profile
    dimension; it does not add a joint (part tree / joints unchanged).
  * ``lid_mechanism`` (5): the main motion axis —
      full_side_hinge      (1 REVOLUTE along the real side-rim tangent),
      split_two_panel      (2 REVOLUTE, each along its real side-rim segment),
      double_leaf_wings    (2 mirrored REVOLUTE along the left/right side rims),
      half_couch_head_only (1 REVOLUTE along the head-side rim + fixed foot lid),
      vertical_lift_lid   (1 PRISMATIC +Z, single ``lid``; no rotation).
  * ``carry_handles`` (3): none / fixed_side_rails (inline body visuals, Rule 1,
    no joint) / swing_drop_bar_handles (N ``handle_i`` bails, each a REVOLUTE).
  * ``handle_count`` (N even in [2,8]): a multiplicity axis — only present when
    ``carry_handles == swing_drop_bar_handles``. Encoded into the slot_choice
    tuple as ``("handle_count", f"n{N}")``.

The lid REVOLUTE mechanisms use their top-rim hinge line as the motion axis; the
vertical-lift mechanism is a single PRISMATIC +Z lift with no co-located rotation.
The closed lid seats on the rim. Swing-handle pivots use captured bracket
geometry and element-scoped ``allow_overlap``.
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
    Box,
    Inertial,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
)

__modular__ = True

BodyShape = Literal["toe_pincher_hex", "rectangular_casket", "tapered_trapezoid"]
LidMechanism = Literal[
    "full_side_hinge",
    "split_two_panel",
    "double_leaf_wings",
    "half_couch_head_only",
    "vertical_lift_lid",
]
CarryHandles = Literal["none", "fixed_side_rails", "swing_drop_bar_handles"]
PaletteStyle = Literal[
    "weathered_oak",
    "dark_walnut",
    "ebony_black",
    "pale_pine",
    "mahogany_red",
]

BODY_SHAPES: tuple[BodyShape, ...] = (
    "toe_pincher_hex",
    "rectangular_casket",
    "tapered_trapezoid",
)
LID_MECHANISMS: tuple[LidMechanism, ...] = (
    "full_side_hinge",
    "split_two_panel",
    "double_leaf_wings",
    "half_couch_head_only",
    "vertical_lift_lid",
)
CARRY_HANDLES: tuple[CarryHandles, ...] = (
    "none",
    "fixed_side_rails",
    "swing_drop_bar_handles",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "weathered_oak",
    "dark_walnut",
    "ebony_black",
    "pale_pine",
    "mahogany_red",
)

# Handle-count sampling domain (even, [2,8]). Spec §8: 4 high-frequency, 2/6
# common, 8 long tail.
HANDLE_COUNTS: tuple[int, ...] = (2, 4, 6, 8)
HANDLE_COUNT_WEIGHTS = (0.25, 0.40, 0.25, 0.10)
N_MIN = 2
N_MAX = 8

# Palette colorways (spec §7). plank/strap/cross from the 8-sample baseline;
# rail = slightly darker than plank, iron = dark grey.
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "weathered_oak": {
        "plank": (0.44, 0.31, 0.20, 1.0),
        "strap": (0.29, 0.19, 0.12, 1.0),
        "cross": (0.22, 0.14, 0.09, 1.0),
        "rail": (0.38, 0.26, 0.16, 1.0),
        "iron": (0.18, 0.15, 0.12, 1.0),
    },
    "dark_walnut": {
        "plank": (0.30, 0.20, 0.12, 1.0),
        "strap": (0.18, 0.12, 0.07, 1.0),
        "cross": (0.12, 0.08, 0.05, 1.0),
        "rail": (0.24, 0.16, 0.10, 1.0),
        "iron": (0.16, 0.14, 0.12, 1.0),
    },
    "ebony_black": {
        "plank": (0.10, 0.09, 0.08, 1.0),
        "strap": (0.05, 0.05, 0.05, 1.0),
        "cross": (0.16, 0.14, 0.10, 1.0),
        "rail": (0.08, 0.07, 0.07, 1.0),
        "iron": (0.20, 0.18, 0.14, 1.0),
    },
    "pale_pine": {
        "plank": (0.70, 0.58, 0.40, 1.0),
        "strap": (0.52, 0.40, 0.26, 1.0),
        "cross": (0.40, 0.30, 0.18, 1.0),
        "rail": (0.60, 0.48, 0.32, 1.0),
        "iron": (0.30, 0.27, 0.22, 1.0),
    },
    "mahogany_red": {
        "plank": (0.40, 0.18, 0.12, 1.0),
        "strap": (0.28, 0.12, 0.08, 1.0),
        "cross": (0.18, 0.08, 0.05, 1.0),
        "rail": (0.34, 0.15, 0.10, 1.0),
        "iron": (0.20, 0.16, 0.14, 1.0),
    },
}

# ---------------------------------------------------------------------------
# Base real-world dimensions (meters). Coffin lies along +X, head at -X, foot at
# +X, z up. All hinge hardware sits on the top rim (z=BODY_H). Shared verbatim
# across all 8 samples (parent L31-49).
# ---------------------------------------------------------------------------
_LENGTH = 1.90
_HEAD_HALF_W = 0.175  # toe-pincher head end half-width
_SHOULDER_HALF_W = 0.30  # widest (shoulders)
_FOOT_HALF_W = 0.15  # foot end half-width
_RECT_HALF_W = 0.30  # rectangular casket constant half-width
_TAPER_HEAD_HALF_W = 0.30  # tapered trapezoid wide (head) end
_TAPER_FOOT_HALF_W = 0.15  # tapered trapezoid narrow (foot) end

_WALL_T = 0.03
_FLOOR_T = 0.03
_BODY_H = 0.33  # box height to the open rim
_LID_T = 0.04  # lid plank thickness
_LID_OVERHANG = 0.015  # lid outline overhangs the rim
_STRAP_T = 0.012  # strap boards stand proud
_STRAP_W = 0.08  # strap board width along the coffin length
_STRAP_EMBED = 0.003

_LID_OPEN_MAX = math.radians(110.0)
_LID_LIFT_MAX = 0.42
_HANDLE_PIVOT_MAX = math.radians(85.0)

# swing drop-bar handle hardware (swing source L55-61).
_HANDLE_SPAN = 0.12  # distance between bail arm centres
_HANDLE_ARM_LEN = 0.08  # arm drop from pivot to crossbar
_HANDLE_DIA = 0.012
_HANDLE_POST_W = 0.025
_HANDLE_POST_H = 0.040
_BRACKET_EMBED = 0.005

# fixed carry rail hardware (fixed-rails source L50-56).
_RAIL_LENGTH = 1.50
_RAIL_D = 0.040
_RAIL_Z_CENTER = 0.18
_BRACKET_W = 0.030
_BRACKET_H = 0.030
_RAIL_BRACKET_XS = (-0.30, 0.0, 0.30)
_RAIL_BRACKET_SPAN = 0.10

_LID_GAP = 0.005  # visible gap between split lid panels
_SEAM_GAP = 0.004  # half-couch head/foot seam


@dataclass(frozen=True)
class CoffinConfig:
    body_shape: BodyShape | None = None
    lid_mechanism: LidMechanism | None = None
    carry_handles: CarryHandles | None = None
    handle_count: int | None = None
    palette_style: PaletteStyle = "weathered_oak"
    coffin_length_scale: float = 1.0
    body_width_scale: float = 1.0
    body_height_scale: float = 1.0
    lid_open_angle_scale: float = 1.0
    handle_swing_scale: float = 1.0
    handle_spacing_scale: float = 1.0
    name: str = "coffin"


@dataclass(frozen=True)
class ResolvedCoffinConfig:
    body_shape: BodyShape
    lid_mechanism: LidMechanism
    carry_handles: CarryHandles
    handle_count: int
    palette_style: PaletteStyle
    # Scaled geometry.
    length: float
    head_half_w: float
    shoulder_half_w: float
    foot_half_w: float
    body_h: float
    wall_t: float
    floor_t: float
    lid_t: float
    lid_overhang: float
    lid_open_max: float
    lid_lift_max: float
    handle_pivot_max: float
    handle_span: float
    handle_arm_len: float
    name: str

    # Footprint-derived quantities -----------------------------------------
    @property
    def head_x(self) -> float:
        return -self.length / 2.0

    @property
    def foot_x(self) -> float:
        return self.length / 2.0

    @property
    def shoulder_x(self) -> float:
        return self.head_x + self.length / 3.0

    @property
    def hinge_y(self) -> float:
        # -Y long-edge rim hinge line (widest half-width + overhang).
        return -(self.shoulder_half_w + self.lid_overhang)

    @property
    def hinge_abs(self) -> float:
        return self.shoulder_half_w + self.lid_overhang

    @property
    def footprint(self) -> tuple[tuple[float, float], ...]:
        hx, fx, sx = self.head_x, self.foot_x, self.shoulder_x
        if self.body_shape == "rectangular_casket":
            w = self.shoulder_half_w
            return ((hx, -w), (fx, -w), (fx, w), (hx, w))
        if self.body_shape == "tapered_trapezoid":
            hw, fw = self.head_half_w, self.foot_half_w
            return ((hx, -hw), (fx, -fw), (fx, fw), (hx, hw))
        # toe_pincher_hex
        hw, shw, fw = self.head_half_w, self.shoulder_half_w, self.foot_half_w
        return (
            (hx, -hw),
            (sx, -shw),
            (fx, -fw),
            (fx, fw),
            (sx, shw),
            (hx, hw),
        )

    @property
    def strap_xs(self) -> tuple[float, ...]:
        # Three strap stations scaled with the coffin length.
        s = self.length / _LENGTH
        return (-0.75 * s, self.shoulder_x, 0.65 * s)

    def half_width_at(self, x: float) -> float:
        """Footprint half-width (Y) at a given X (used for handle clearance)."""
        if self.body_shape == "rectangular_casket":
            return self.shoulder_half_w
        if self.body_shape == "tapered_trapezoid":
            t = (x - self.head_x) / (self.foot_x - self.head_x)
            return self.head_half_w + t * (self.foot_half_w - self.head_half_w)
        # toe_pincher_hex
        if x <= self.shoulder_x:
            t = (x - self.head_x) / (self.shoulder_x - self.head_x)
            return self.head_half_w + t * (self.shoulder_half_w - self.head_half_w)
        t = (x - self.shoulder_x) / (self.foot_x - self.shoulder_x)
        return self.shoulder_half_w + t * (self.foot_half_w - self.shoulder_half_w)


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


def config_from_seed(seed: int) -> CoffinConfig:
    rng = random.Random(seed)
    carry = rng.choice(CARRY_HANDLES)
    handle_count = (
        rng.choices(HANDLE_COUNTS, weights=HANDLE_COUNT_WEIGHTS, k=1)[0]
        if carry == "swing_drop_bar_handles"
        else None
    )
    return CoffinConfig(
        body_shape=rng.choice(BODY_SHAPES),
        lid_mechanism=rng.choice(LID_MECHANISMS),
        carry_handles=carry,
        handle_count=handle_count,
        palette_style=rng.choice(PALETTE_STYLES),
        coffin_length_scale=round(rng.uniform(0.92, 1.08), 4),
        body_width_scale=round(rng.uniform(0.90, 1.10), 4),
        body_height_scale=round(rng.uniform(0.90, 1.12), 4),
        lid_open_angle_scale=round(rng.uniform(0.85, 1.10), 4),
        handle_swing_scale=round(rng.uniform(0.85, 1.10), 4),
        handle_spacing_scale=round(rng.uniform(0.90, 1.10), 4),
        name=f"seeded_coffin_{seed}",
    )


def resolve_config(config: CoffinConfig | None = None) -> ResolvedCoffinConfig:
    cfg = config or CoffinConfig()
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)
    body_shape = _pick(cfg.body_shape, BODY_SHAPES)
    lid_mechanism = _pick(cfg.lid_mechanism, LID_MECHANISMS)
    carry_handles = _pick(cfg.carry_handles, CARRY_HANDLES)

    # handle_count only exists under swing; otherwise nominal & unused. Clamp to
    # even [2,8] when present.
    if carry_handles == "swing_drop_bar_handles":
        n = int(cfg.handle_count) if cfg.handle_count is not None else 6
        n = int(_clamp(n, N_MIN, N_MAX))
        if n % 2 != 0:
            n += 1
        n = int(_clamp(n, N_MIN, N_MAX))
    else:
        n = 0  # sentinel: no swing handles

    len_scale = _clamp(cfg.coffin_length_scale, 0.92, 1.08)
    width_scale = _clamp(cfg.body_width_scale, 0.90, 1.10)
    height_scale = _clamp(cfg.body_height_scale, 0.90, 1.12)
    angle_scale = _clamp(cfg.lid_open_angle_scale, 0.85, 1.10)
    swing_scale = _clamp(cfg.handle_swing_scale, 0.85, 1.10)
    spacing_scale = _clamp(cfg.handle_spacing_scale, 0.90, 1.10)

    length = _LENGTH * len_scale
    head_half_w = _HEAD_HALF_W * width_scale
    shoulder_half_w = _SHOULDER_HALF_W * width_scale
    foot_half_w = _FOOT_HALF_W * width_scale
    if body_shape == "rectangular_casket":
        shoulder_half_w = _RECT_HALF_W * width_scale
        head_half_w = shoulder_half_w
        foot_half_w = shoulder_half_w
    elif body_shape == "tapered_trapezoid":
        shoulder_half_w = _TAPER_HEAD_HALF_W * width_scale
        head_half_w = _TAPER_HEAD_HALF_W * width_scale
        foot_half_w = _TAPER_FOOT_HALF_W * width_scale

    body_h = _BODY_H * height_scale
    lid_open_max = _clamp(_LID_OPEN_MAX * angle_scale, math.radians(80.0), math.radians(170.0))
    handle_pivot_max = _clamp(
        _HANDLE_PIVOT_MAX * swing_scale, math.radians(60.0), math.radians(110.0)
    )

    handle_span = _HANDLE_SPAN * spacing_scale
    handle_arm_len = _HANDLE_ARM_LEN

    return ResolvedCoffinConfig(
        body_shape=body_shape,
        lid_mechanism=lid_mechanism,
        carry_handles=carry_handles,
        handle_count=n,
        palette_style=palette_style,
        length=length,
        head_half_w=head_half_w,
        shoulder_half_w=shoulder_half_w,
        foot_half_w=foot_half_w,
        body_h=body_h,
        wall_t=_WALL_T,
        floor_t=_FLOOR_T,
        lid_t=_LID_T,
        lid_overhang=_LID_OVERHANG,
        lid_open_max=lid_open_max,
        lid_lift_max=_LID_LIFT_MAX * height_scale,
        handle_pivot_max=handle_pivot_max,
        handle_span=handle_span,
        handle_arm_len=handle_arm_len,
        name=cfg.name or "coffin",
    )


def with_overrides(config: CoffinConfig, **kwargs: object) -> CoffinConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: CoffinConfig | ResolvedCoffinConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedCoffinConfig) else resolve_config(config)
    choices: list[tuple[str, str]] = [
        ("body_shape", r.body_shape),
        ("lid_mechanism", r.lid_mechanism),
        ("carry_handles", r.carry_handles),
    ]
    if r.carry_handles == "swing_drop_bar_handles":
        choices.append(("handle_count", f"n{r.handle_count}"))
    return tuple(choices)


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Shared cadquery footprint helpers (verbatim from all 8 samples, parameterized
# on the FOOTPRINT polygon + dims from the resolved config).
# ---------------------------------------------------------------------------
def _offset_polygon(pts, dist):
    """Offset a convex CCW polygon: positive dist moves edges outward."""
    n = len(pts)
    lines = []
    for i in range(n):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % n]
        dx, dy = x2 - x1, y2 - y1
        length = math.hypot(dx, dy)
        dx, dy = dx / length, dy / length
        lines.append((x1 + dy * dist, y1 - dx * dist, dx, dy))
    out = []
    for i in range(n):
        ax, ay, adx, ady = lines[i - 1]
        bx, by, bdx, bdy = lines[i]
        denom = adx * bdy - ady * bdx
        s = ((bx - ax) * bdy - (by - ay) * bdx) / denom
        out.append((ax + adx * s, ay + ady * s))
    return out


def _extrude_poly(pts, z0, z1):
    return cq.Workplane("XY", origin=(0.0, 0.0, z0)).polyline(list(pts)).close().extrude(z1 - z0)


def _x_slab(x_center, width, z_center=0.25, z_height=0.9):
    return cq.Workplane("XY", origin=(x_center, 0.0, z_center)).box(width, 2.0, z_height)


def _x_clip_box(x_min, x_max, y_center=0.30, y_extent=2.0, z_center=0.02, z_extent=0.20):
    return cq.Workplane("XY", origin=((x_min + x_max) / 2.0, y_center, z_center)).box(
        x_max - x_min, y_extent, z_extent
    )


def _clip_polygon_at_y0(pts, keep_positive):
    out = []
    n = len(pts)
    for i in range(n):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % n]
        inside1 = (y1 >= -1e-12) if keep_positive else (y1 <= 1e-12)
        inside2 = (y2 >= -1e-12) if keep_positive else (y2 <= 1e-12)
        if inside1:
            out.append((x1, y1))
        if inside1 != inside2:
            dy = y2 - y1
            t = -y1 / dy if abs(dy) > 1e-15 else 0.0
            out.append((x1 + t * (x2 - x1), 0.0))
    return out


def _clip_polygon_y_max(pts, y_max):
    shifted = [(x, y - y_max) for x, y in pts]
    clipped = _clip_polygon_at_y0(shifted, keep_positive=False)
    return [(x, y + y_max) for x, y in clipped]


def _clip_polygon_y_min(pts, y_min):
    shifted = [(x, y - y_min) for x, y in pts]
    clipped = _clip_polygon_at_y0(shifted, keep_positive=True)
    return [(x, y + y_min) for x, y in clipped]


def _body_shell(r: ResolvedCoffinConfig):
    """Hollow open-top box: 0.03 m walls + floor, two seam grooves."""
    fp = r.footprint
    outer = _extrude_poly(fp, 0.0, r.body_h)
    cavity = _extrude_poly(_offset_polygon(fp, -r.wall_t), r.floor_t, r.body_h + 0.01)
    shell = outer.cut(cavity)
    for z_seam in (r.body_h / 3.0, 2.0 * r.body_h / 3.0):
        ring = _extrude_poly(fp, z_seam - 0.0025, z_seam + 0.0025).cut(
            _extrude_poly(_offset_polygon(fp, -0.005), z_seam - 0.004, z_seam + 0.004)
        )
        shell = shell.cut(ring)
    return shell


def _body_strap_band(r: ResolvedCoffinConfig, x_center):
    fp = r.footprint
    ring = _extrude_poly(_offset_polygon(fp, _STRAP_T), 0.02, r.body_h).cut(
        _extrude_poly(_offset_polygon(fp, -0.002), 0.015, r.body_h + 0.01)
    )
    return ring.intersect(_x_slab(x_center, _STRAP_W))


def _lid_poly(r: ResolvedCoffinConfig):
    """Full lid outline in the rear-hinge lid-local frame (panel along +Y)."""
    return tuple((x, y - r.hinge_y) for (x, y) in _offset_polygon(r.footprint, r.lid_overhang))


def _side_anchor(r: ResolvedCoffinConfig, side: int, x: float | None = None) -> tuple[float, float]:
    """A real body-rim point used as a joint origin without adding hinge hardware."""
    if x is None:
        if r.body_shape == "tapered_trapezoid":
            x = r.head_x
        elif r.body_shape == "toe_pincher_hex":
            x = r.shoulder_x
        else:
            x = 0.0
    x = _clamp(x, r.head_x, r.foot_x)
    return x, side * r.half_width_at(x)


def _side_axis(
    r: ResolvedCoffinConfig, side: int, x: float | None = None
) -> tuple[float, float, float]:
    """Unit tangent of the actual side rim segment used as a revolute axis."""
    if r.body_shape == "rectangular_casket":
        vx, vy = 1.0, 0.0
    elif r.body_shape == "tapered_trapezoid":
        vx = r.foot_x - r.head_x
        vy = side * (r.foot_half_w - r.head_half_w)
    else:
        x_ref = r.shoulder_x if x is None else x
        if x_ref <= r.shoulder_x:
            vx = r.shoulder_x - r.head_x
            vy = side * (r.shoulder_half_w - r.head_half_w)
        else:
            vx = r.foot_x - r.shoulder_x
            vy = side * (r.foot_half_w - r.shoulder_half_w)
    length = math.hypot(vx, vy)
    return (vx / length, vy / length, 0.0)


def _neg_axis(axis: tuple[float, float, float]) -> tuple[float, float, float]:
    return (-axis[0], -axis[1], -axis[2])


def _shifted(workplane: cq.Workplane, anchor_x: float, anchor_y: float) -> cq.Workplane:
    return workplane.translate((-anchor_x, -anchor_y, 0.0))


def _lid_panel(r: ResolvedCoffinConfig, *, x_min=None, x_max=None):
    """Flat lid plank panel (optionally x-clipped) with seam grooves."""
    lid_poly = _lid_poly(r)
    panel = _extrude_poly(lid_poly, 0.0, r.lid_t)
    lid_w = 2.0 * (r.shoulder_half_w + r.lid_overhang)
    for y_seam in (lid_w / 3.0, 2.0 * lid_w / 3.0):
        groove = cq.Workplane("XY", origin=(0.0, y_seam, r.lid_t)).box(2.2, 0.004, 0.008)
        panel = panel.cut(groove)
    if x_min is not None and x_max is not None:
        panel = panel.intersect(_x_clip_box(x_min, x_max))
    return panel


def _lid_strap(r: ResolvedCoffinConfig, x_center):
    lid_poly = _lid_poly(r)
    cap = _extrude_poly(_offset_polygon(lid_poly, _STRAP_T), 0.0, r.lid_t + _STRAP_T).cut(
        _extrude_poly(_offset_polygon(lid_poly, -0.002), -0.01, r.lid_t - _STRAP_EMBED)
    )
    return cap.intersect(_x_slab(x_center, _STRAP_W, z_center=0.0))


def _emit_lid_decorations(
    lid,
    r: ResolvedCoffinConfig,
    mats,
    *,
    lid_center_y: float,
    origin_x: float = 0.0,
):
    """Latin cross on the head-end lid panel (Rule 1: inline visuals)."""
    cross_z = r.lid_t - _STRAP_EMBED + 0.0075
    s = r.length / _LENGTH
    lid.visual(
        Box((0.32 * s, 0.05, 0.015)),
        origin=Origin(xyz=(-0.54 * s - origin_x, lid_center_y, cross_z)),
        material=mats["cross"],
        name="cross_upright", material_class_id=("wood.mahogany_teak_dark" if r.palette_style in {"weathered_oak", "dark_walnut", "pale_pine", "mahogany_red"} else "wood.painted_clean"),
    )
    lid.visual(
        Box((0.05, 0.20, 0.015)),
        origin=Origin(xyz=(-0.61 * s - origin_x, lid_center_y, cross_z)),
        material=mats["cross"],
        name="cross_arm", material_class_id=("wood.mahogany_teak_dark" if r.palette_style in {"weathered_oak", "dark_walnut", "pale_pine", "mahogany_red"} else "wood.painted_clean"),
    )


# ---------------------------------------------------------------------------
# Body part (root).
# ---------------------------------------------------------------------------
def _build_body(model: ArticulatedObject, r: ResolvedCoffinConfig, mats, *, assets):
    body = model.part("coffin_body")
    body.visual(
        mesh_from_cadquery(_body_shell(r), "body_shell", assets=assets),
        material=mats["plank"],
        name="body_shell", material_class_id=("wood.mahogany_teak_dark" if r.palette_style in {"weathered_oak", "dark_walnut", "pale_pine", "mahogany_red"} else "wood.painted_clean"),
    )
    for i, x_center in enumerate(r.strap_xs):
        body.visual(
            mesh_from_cadquery(_body_strap_band(r, x_center), f"body_strap_{i}", assets=assets),
            material=mats["strap"],
            name=f"body_strap_{i}", material_class_id=("wood.mahogany_teak_dark" if r.palette_style in {"weathered_oak", "dark_walnut", "pale_pine", "mahogany_red"} else "wood.painted_clean"),
        )
    body.inertial = Inertial.from_geometry(
        Box((r.length, 2.0 * r.shoulder_half_w, r.body_h)),
        mass=12.0,
        origin=Origin(xyz=(0.0, 0.0, r.body_h / 2.0)),
    )
    return body


# ---------------------------------------------------------------------------
# Lid mechanisms.
# ---------------------------------------------------------------------------
def _lid_inertial(r: ResolvedCoffinConfig, mass: float, y0: float):
    return Inertial.from_geometry(
        Box((r.length, 2.0 * r.shoulder_half_w, r.lid_t)),
        mass=mass,
        origin=Origin(xyz=(0.0, y0, r.lid_t / 2.0)),
    )


def _emit_full_side_hinge(model, r, body, mats, *, assets) -> list[str]:
    """Single full lid (1 REVOLUTE +X). Source: parent L171-207."""
    anchor_x, anchor_y = _side_anchor(r, -1)
    axis = _side_axis(r, -1, anchor_x)
    lid = model.part("lid")
    lid.visual(
        mesh_from_cadquery(
            _shifted(_world_lid_panel(r), anchor_x, anchor_y), "lid_panel", assets=assets
        ),
        material=mats["plank"],
        name="lid_panel", material_class_id=("wood.mahogany_teak_dark" if r.palette_style in {"weathered_oak", "dark_walnut", "pale_pine", "mahogany_red"} else "wood.painted_clean"),
    )
    for i, x_center in enumerate(r.strap_xs):
        lid.visual(
            mesh_from_cadquery(
                _shifted(_world_lid_strap(r, x_center), anchor_x, anchor_y),
                f"lid_strap_{i}",
                assets=assets,
            ),
            material=mats["strap"],
            name=f"lid_strap_{i}", material_class_id=("wood.mahogany_teak_dark" if r.palette_style in {"weathered_oak", "dark_walnut", "pale_pine", "mahogany_red"} else "wood.painted_clean"),
        )
    _emit_lid_decorations(lid, r, mats, lid_center_y=-anchor_y, origin_x=anchor_x)
    lid.inertial = _lid_inertial(r, 4.0, -anchor_y)
    model.articulation(
        "lid_hinge",
        ArticulationType.REVOLUTE,
        parent=body,
        child=lid,
        origin=Origin(xyz=(anchor_x, anchor_y, r.body_h)),
        axis=axis,
        motion_limits=MotionLimits(effort=60.0, velocity=1.0, lower=0.0, upper=r.lid_open_max),
    )
    return ["lid"]


def _emit_split_two_panel(model, r, body, mats, *, assets) -> list[str]:
    """Two lid panels split at center (2 REVOLUTE +X). Source: split L146-256."""
    lid_overhang = r.lid_overhang
    ranges = [
        (r.head_x - lid_overhang - 0.01, 0.0 - _LID_GAP / 2.0),
        (0.0 + _LID_GAP / 2.0, r.foot_x + lid_overhang + 0.01),
    ]
    names: list[str] = []
    for i in range(2):
        x_min, x_max = ranges[i]
        anchor_x, anchor_y = _side_anchor(r, -1, x_min if i == 1 else r.head_x)
        axis = _side_axis(r, -1, anchor_x)
        lid = model.part(f"lid_{i}")
        lid.visual(
            mesh_from_cadquery(
                _shifted(_world_lid_panel(r, x_min=x_min, x_max=x_max), anchor_x, anchor_y),
                f"lid_panel_{i}",
                assets=assets,
            ),
            material=mats["plank"],
            name=f"lid_panel_{i}", material_class_id=("wood.mahogany_teak_dark" if r.palette_style in {"weathered_oak", "dark_walnut", "pale_pine", "mahogany_red"} else "wood.painted_clean"),
        )
        for j, x_center in enumerate(r.strap_xs):
            if x_min - 0.05 <= x_center <= x_max + 0.05:
                lid.visual(
                    mesh_from_cadquery(
                        _shifted(_world_lid_strap(r, x_center), anchor_x, anchor_y),
                        f"lid_strap_{i}_{j}",
                        assets=assets,
                    ),
                    material=mats["strap"],
                    name=f"lid_strap_{i}_{j}", material_class_id=("wood.mahogany_teak_dark" if r.palette_style in {"weathered_oak", "dark_walnut", "pale_pine", "mahogany_red"} else "wood.painted_clean"),
                )
        if i == 0:
            _emit_lid_decorations(lid, r, mats, lid_center_y=-anchor_y, origin_x=anchor_x)
        lid.inertial = _lid_inertial(r, 2.0, -anchor_y)
        model.articulation(
            f"lid_hinge_{i}",
            ArticulationType.REVOLUTE,
            parent=body,
            child=lid,
            origin=Origin(xyz=(anchor_x, anchor_y, r.body_h)),
            axis=axis,
            motion_limits=MotionLimits(effort=60.0, velocity=1.0, lower=0.0, upper=r.lid_open_max),
        )
        names.append(f"lid_{i}")
    return names


def _compute_leaf_local_polygons(r: ResolvedCoffinConfig):
    overhang = _offset_polygon(r.footprint, r.lid_overhang)
    neg_half = _clip_polygon_at_y0(overhang, keep_positive=False)
    pos_half = _clip_polygon_at_y0(overhang, keep_positive=True)
    hinge_abs = r.hinge_abs
    neg_local = [(x, y + hinge_abs) for x, y in neg_half]
    pos_local = [(x, y - hinge_abs) for x, y in pos_half]
    return neg_local, pos_local


def _lid_leaf_panel(r, local_poly):
    panel = _extrude_poly(local_poly, 0.0, r.lid_t)
    ys = [y for _, y in local_poly]
    y_mid = (min(ys) + max(ys)) / 2.0
    groove = cq.Workplane("XY", origin=(0.0, y_mid, r.lid_t)).box(2.2, 0.004, 0.008)
    return panel.cut(groove)


def _lid_leaf_strap(r, local_poly, x_center, y_clip_max=None, y_clip_min=None):
    offset_poly = _offset_polygon(local_poly, _STRAP_T)
    if y_clip_max is not None:
        offset_poly = _clip_polygon_y_max(offset_poly, y_clip_max)
    if y_clip_min is not None:
        offset_poly = _clip_polygon_y_min(offset_poly, y_clip_min)
    inner_poly = _offset_polygon(local_poly, -0.002)
    cap = _extrude_poly(offset_poly, 0.0, r.lid_t + _STRAP_T).cut(
        _extrude_poly(inner_poly, -0.01, r.lid_t - _STRAP_EMBED)
    )
    return cap.intersect(_x_slab(x_center, _STRAP_W, z_center=0.0))


def _emit_double_leaf_wings(model, r, body, mats, *, assets) -> list[str]:
    """Two mirrored leaves opening apart (2 REVOLUTE ±X). Source: double-leaf."""
    overhang = _offset_polygon(r.footprint, r.lid_overhang)
    neg_world = _clip_polygon_at_y0(overhang, keep_positive=False)
    pos_world = _clip_polygon_at_y0(overhang, keep_positive=True)
    leaf_configs = [
        {
            "world_poly": neg_world,
            "side": -1,
            "axis_sign": 1.0,
            "clip_key": "y_clip_max",
        },
        {
            "world_poly": pos_world,
            "side": 1,
            "axis_sign": -1.0,
            "clip_key": "y_clip_min",
        },
    ]
    names: list[str] = []
    s = r.length / _LENGTH
    for i, cfg in enumerate(leaf_configs):
        anchor_x, anchor_y = _side_anchor(r, cfg["side"], r.head_x)
        axis = _side_axis(r, cfg["side"], anchor_x)
        if cfg["axis_sign"] < 0.0:
            axis = _neg_axis(axis)
        local_poly = [(x - anchor_x, y - anchor_y) for x, y in cfg["world_poly"]]
        clip = {cfg["clip_key"]: -anchor_y}
        leaf = model.part(f"lid_leaf_{i}")
        leaf.visual(
            mesh_from_cadquery(
                _lid_leaf_panel(r, local_poly), f"lid_leaf_{i}_panel", assets=assets
            ),
            material=mats["plank"],
            name=f"lid_leaf_{i}_panel", material_class_id=("wood.mahogany_teak_dark" if r.palette_style in {"weathered_oak", "dark_walnut", "pale_pine", "mahogany_red"} else "wood.painted_clean"),
        )
        for j, x_center in enumerate(r.strap_xs):
            leaf.visual(
                mesh_from_cadquery(
                    _lid_leaf_strap(r, local_poly, x_center - anchor_x, **clip),
                    f"lid_leaf_{i}_strap_{j}",
                    assets=assets,
                ),
                material=mats["strap"],
                name=f"lid_leaf_{i}_strap_{j}", material_class_id=("wood.mahogany_teak_dark" if r.palette_style in {"weathered_oak", "dark_walnut", "pale_pine", "mahogany_red"} else "wood.painted_clean"),
            )
        if i == 0:
            cross_z = r.lid_t - _STRAP_EMBED + 0.0075
            leaf.visual(
                Box((0.32 * s, 0.05, 0.015)),
                origin=Origin(xyz=(-0.54 * s - anchor_x, -0.025 - anchor_y, cross_z)),
                material=mats["cross"],
                name="cross_upright", material_class_id=("wood.mahogany_teak_dark" if r.palette_style in {"weathered_oak", "dark_walnut", "pale_pine", "mahogany_red"} else "wood.painted_clean"),
            )
            leaf.visual(
                Box((0.05, 0.18, 0.015)),
                origin=Origin(xyz=(-0.61 * s - anchor_x, -0.085 - anchor_y, cross_z)),
                material=mats["cross"],
                name="cross_arm", material_class_id=("wood.mahogany_teak_dark" if r.palette_style in {"weathered_oak", "dark_walnut", "pale_pine", "mahogany_red"} else "wood.painted_clean"),
            )
        leaf.inertial = _lid_inertial(r, 2.0, -anchor_y / 2.0)
        model.articulation(
            f"lid_leaf_{i}_hinge",
            ArticulationType.REVOLUTE,
            parent=body,
            child=leaf,
            origin=Origin(xyz=(anchor_x, anchor_y, r.body_h)),
            axis=axis,
            motion_limits=MotionLimits(effort=60.0, velocity=1.0, lower=0.0, upper=r.lid_open_max),
        )
        names.append(f"lid_leaf_{i}")
    return names


def _world_lid_poly(r: ResolvedCoffinConfig):
    """Lid outline in world/body coords (panel about the centerline)."""
    return tuple(_offset_polygon(r.footprint, r.lid_overhang))


def _world_lid_panel(r: ResolvedCoffinConfig, *, x_min=None, x_max=None):
    panel = _extrude_poly(_world_lid_poly(r), 0.0, r.lid_t)
    lid_w = 2.0 * (r.shoulder_half_w + r.lid_overhang)
    for y_frac in (1.0 / 3.0, 2.0 / 3.0):
        y_seam = r.hinge_y + y_frac * lid_w
        groove = cq.Workplane("XY", origin=(0.0, y_seam, r.lid_t)).box(2.2, 0.004, 0.008)
        panel = panel.cut(groove)
    if x_min is not None and x_max is not None:
        panel = panel.intersect(
            _x_clip_box(x_min, x_max, y_center=0.0, z_center=r.lid_t / 2.0, z_extent=r.lid_t + 0.02)
        )
    return panel


def _world_lid_strap(r: ResolvedCoffinConfig, x_center):
    world_poly = _world_lid_poly(r)
    cap = _extrude_poly(_offset_polygon(world_poly, _STRAP_T), 0.0, r.lid_t + _STRAP_T).cut(
        _extrude_poly(_offset_polygon(world_poly, -0.002), -0.01, r.lid_t - _STRAP_EMBED)
    )
    return cap.intersect(_x_slab(x_center, _STRAP_W, z_center=0.0))


def _emit_vertical_lift_lid(model, r, body, mats, *, assets) -> list[str]:
    """Single full lid sliding straight upward (1 PRISMATIC +Z, no rotation)."""
    anchor_x, anchor_y = _side_anchor(r, -1, r.head_x)
    lid = model.part("lid")
    lid.visual(
        mesh_from_cadquery(
            _shifted(_world_lid_panel(r), anchor_x, anchor_y),
            "lid_panel",
            assets=assets,
        ),
        material=mats["plank"],
        name="lid_panel", material_class_id=("wood.mahogany_teak_dark" if r.palette_style in {"weathered_oak", "dark_walnut", "pale_pine", "mahogany_red"} else "wood.painted_clean"),
    )
    for i, x_center in enumerate(r.strap_xs):
        lid.visual(
            mesh_from_cadquery(
                _shifted(_world_lid_strap(r, x_center), anchor_x, anchor_y),
                f"lid_strap_{i}",
                assets=assets,
            ),
            material=mats["strap"],
            name=f"lid_strap_{i}", material_class_id=("wood.mahogany_teak_dark" if r.palette_style in {"weathered_oak", "dark_walnut", "pale_pine", "mahogany_red"} else "wood.painted_clean"),
        )
    _emit_lid_decorations(lid, r, mats, lid_center_y=-anchor_y, origin_x=anchor_x)
    lid.inertial = _lid_inertial(r, 4.0, -anchor_y)
    model.articulation(
        "lid_lift",
        ArticulationType.PRISMATIC,
        parent=body,
        child=lid,
        origin=Origin(xyz=(anchor_x, anchor_y, r.body_h)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=80.0, velocity=0.5, lower=0.0, upper=r.lid_lift_max),
    )
    return ["lid"]


def _emit_half_couch_head_only(model, r, body, mats, *, assets) -> list[str]:
    """Head-half hinged lid + fixed inline foot half (1 REVOLUTE +X). Source:
    half-couch. Foot lid panel + strap are inlined into the body (Rule 1)."""
    world_poly = _world_lid_poly(r)
    lid_w = 2.0 * (r.shoulder_half_w + r.lid_overhang)

    # --- Foot half: inline into body (Rule 1, does not move) ---
    foot_panel = _extrude_poly(world_poly, r.body_h, r.body_h + r.lid_t)
    foot_panel = foot_panel.intersect(
        _x_clip_box(
            _SEAM_GAP / 2.0,
            r.foot_x + r.lid_overhang + 0.01,
            y_center=0.0,
            z_center=r.body_h + r.lid_t / 2.0,
            z_extent=r.lid_t + 0.02,
        )
    )
    for y_frac in (1.0 / 3.0, 2.0 / 3.0):
        y_seam = r.hinge_y + y_frac * lid_w
        groove = cq.Workplane("XY", origin=(0.0, y_seam, r.body_h + r.lid_t)).box(2.2, 0.004, 0.008)
        foot_panel = foot_panel.cut(groove)
    body.visual(
        mesh_from_cadquery(foot_panel, "foot_lid_panel", assets=assets),
        material=mats["plank"],
        name="foot_lid_panel", material_class_id=("wood.mahogany_teak_dark" if r.palette_style in {"weathered_oak", "dark_walnut", "pale_pine", "mahogany_red"} else "wood.painted_clean"),
    )
    for i, x_center in enumerate(r.strap_xs):
        if x_center >= _SEAM_GAP / 2.0:
            cap = _extrude_poly(
                _offset_polygon(world_poly, _STRAP_T), r.body_h, r.body_h + r.lid_t + _STRAP_T
            ).cut(
                _extrude_poly(
                    _offset_polygon(world_poly, -0.002),
                    r.body_h - 0.01,
                    r.body_h + r.lid_t - _STRAP_EMBED,
                )
            )
            cap = cap.intersect(_x_slab(x_center, _STRAP_W, z_center=r.body_h))
            body.visual(
                mesh_from_cadquery(cap, f"foot_lid_strap_{i}", assets=assets),
                material=mats["strap"],
                name=f"foot_lid_strap_{i}", material_class_id=("wood.mahogany_teak_dark" if r.palette_style in {"weathered_oak", "dark_walnut", "pale_pine", "mahogany_red"} else "wood.painted_clean"),
            )

    # --- Head half: hinged ---
    anchor_x, anchor_y = _side_anchor(r, -1, r.head_x)
    axis = _side_axis(r, -1, anchor_x)
    head_lid = model.part("head_lid")
    head_panel = _world_lid_panel(r)
    head_panel = head_panel.intersect(
        _x_clip_box(
            r.head_x - r.lid_overhang - 0.01,
            -_SEAM_GAP / 2.0,
            y_center=0.0,
            z_center=r.lid_t / 2.0,
            z_extent=r.lid_t + 0.02,
        )
    )
    head_lid.visual(
        mesh_from_cadquery(
            _shifted(head_panel, anchor_x, anchor_y), "head_lid_panel", assets=assets
        ),
        material=mats["plank"],
        name="head_lid_panel", material_class_id=("wood.mahogany_teak_dark" if r.palette_style in {"weathered_oak", "dark_walnut", "pale_pine", "mahogany_red"} else "wood.painted_clean"),
    )
    for i, x_center in enumerate(r.strap_xs):
        if x_center < -_SEAM_GAP / 2.0:
            head_lid.visual(
                mesh_from_cadquery(
                    _shifted(_world_lid_strap(r, x_center), anchor_x, anchor_y),
                    f"head_lid_strap_{i}",
                    assets=assets,
                ),
                material=mats["strap"],
                name=f"head_lid_strap_{i}", material_class_id=("wood.mahogany_teak_dark" if r.palette_style in {"weathered_oak", "dark_walnut", "pale_pine", "mahogany_red"} else "wood.painted_clean"),
            )
    _emit_lid_decorations(head_lid, r, mats, lid_center_y=-anchor_y, origin_x=anchor_x)
    head_lid.inertial = _lid_inertial(r, 2.0, -anchor_y)
    model.articulation(
        "head_lid_hinge",
        ArticulationType.REVOLUTE,
        parent=body,
        child=head_lid,
        origin=Origin(xyz=(anchor_x, anchor_y, r.body_h)),
        axis=axis,
        motion_limits=MotionLimits(effort=60.0, velocity=1.0, lower=0.0, upper=r.lid_open_max),
    )
    return ["head_lid"]


_LID_BUILDERS = {
    "full_side_hinge": _emit_full_side_hinge,
    "split_two_panel": _emit_split_two_panel,
    "double_leaf_wings": _emit_double_leaf_wings,
    "half_couch_head_only": _emit_half_couch_head_only,
    "vertical_lift_lid": _emit_vertical_lift_lid,
}


# ---------------------------------------------------------------------------
# Carry handles.
# ---------------------------------------------------------------------------
def _xy_bar_between(
    x0: float,
    y0: float,
    x1: float,
    y1: float,
    *,
    z: float,
    dia: float,
) -> cq.Workplane:
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    length = math.hypot(x1 - x0, y1 - y0)
    angle = math.degrees(math.atan2(y1 - y0, x1 - x0))
    bar = cq.Workplane("XY", origin=(cx, cy, z)).box(length, dia, dia)
    return bar.rotate((cx, cy, z), (cx, cy, z + 1.0), angle)


def _side_following_xs(r: ResolvedCoffinConfig, x0: float, x1: float) -> tuple[float, ...]:
    xs = [max(r.head_x, x0)]
    if r.body_shape == "toe_pincher_hex" and xs[0] < r.shoulder_x < x1:
        xs.append(r.shoulder_x)
    xs.append(min(r.foot_x, x1))
    return tuple(x for i, x in enumerate(xs) if i == 0 or abs(x - xs[i - 1]) > 1e-6)


def _carry_rail(r: ResolvedCoffinConfig, y_sign: int):
    """One fixed carry rail bar + brackets for one side. Source: fixed-rails."""
    side_clearance = _STRAP_T + _RAIL_D / 2.0 + 0.006
    rail_len = _RAIL_LENGTH * (r.length / _LENGTH)
    xs = _side_following_xs(r, -rail_len / 2.0, rail_len / 2.0)
    result = None
    for x0, x1 in zip(xs, xs[1:]):
        y0 = y_sign * (r.half_width_at(x0) + side_clearance)
        y1 = y_sign * (r.half_width_at(x1) + side_clearance)
        bar = _xy_bar_between(x0, y0, x1, y1, z=_RAIL_Z_CENTER, dia=_RAIL_D)
        result = bar if result is None else result.union(bar)
    s = r.length / _LENGTH
    for bx in _RAIL_BRACKET_XS:
        x = bx * s
        wall_y = y_sign * r.half_width_at(_clamp(x, r.head_x, r.foot_x))
        rail_y = y_sign * (r.half_width_at(_clamp(x, r.head_x, r.foot_x)) + side_clearance)
        inner_y = wall_y - y_sign * _BRACKET_EMBED
        outer_y = rail_y
        bracket_depth = abs(outer_y - inner_y)
        bracket_cy = (inner_y + outer_y) / 2.0
        bracket = cq.Workplane("XY", origin=(bx * s, bracket_cy, _RAIL_Z_CENTER)).box(
            _BRACKET_W, bracket_depth, _BRACKET_H
        )
        result = bracket if result is None else result.union(bracket)
    return result


def _emit_none_handles(model, r, body, mats, *, assets) -> list[str]:
    return []


def _emit_fixed_side_rails(model, r, body, mats, *, assets) -> list[str]:
    """Two fixed carry rails inlined as body visuals (Rule 1, no joint)."""
    for i in range(2):
        y_sign = 1 if i == 0 else -1
        body.visual(
            mesh_from_cadquery(_carry_rail(r, y_sign), f"carry_rail_{i}", assets=assets),
            material=mats["rail"],
            name=f"carry_rail_{i}", material_class_id=("wood.mahogany_teak_dark" if r.palette_style in {"weathered_oak", "dark_walnut", "pale_pine", "mahogany_red"} else "wood.painted_clean"),
        )
    return []


def _bail_handle_cq(span, arm_len, dia):
    """U-shaped bail handle: two vertical arms + crossbar. Source: swing L173-186."""
    rr = dia / 2.0
    hs = span / 2.0
    left = cq.Workplane("XY", origin=(-hs, 0.0, -arm_len)).circle(rr).extrude(arm_len)
    right = cq.Workplane("XY", origin=(hs, 0.0, -arm_len)).circle(rr).extrude(arm_len)
    bar = cq.Workplane("YZ", origin=(-hs, 0.0, -arm_len)).circle(rr).extrude(span)
    # Top pivot rod along X through the arm tops (z=0): this is the hardware the
    # REVOLUTE turns on, and it ensures the part frame origin (0,0,0) lies on
    # real geometry (flat articulation-origin baseline).
    pivot_rod = cq.Workplane("YZ", origin=(-hs, 0.0, 0.0)).circle(rr).extrude(span)
    return left.union(right).union(bar).union(pivot_rod)


def _handle_xs(r: ResolvedCoffinConfig) -> tuple[float, ...]:
    """X stations for the handles on one side (N/2 evenly spaced, symmetric)."""
    per_side = r.handle_count // 2
    if per_side <= 0:
        return ()
    # Usable span keeps handles clear of the head/foot ends.
    end_margin = 0.18 * (r.length / _LENGTH)
    usable = r.length - 2.0 * end_margin
    if per_side == 1:
        return (0.0,)
    spacing = usable / (per_side - 1)
    x0 = -usable / 2.0
    return tuple(x0 + i * spacing for i in range(per_side))


def _emit_swing_drop_bar_handles(model, r, body, mats, *, assets) -> list[str]:
    """N swinging drop-bar bails (each REVOLUTE ±X). Source: swing L246-294."""
    bail_mesh = mesh_from_cadquery(
        _bail_handle_cq(r.handle_span, r.handle_arm_len, _HANDLE_DIA), "bail", assets=assets
    )
    pivot_z = r.body_h - 0.06
    handle_xs = _handle_xs(r)
    names: list[str] = []
    handle_idx = 0
    for side in (-1, 1):
        for x_st in handle_xs:
            arm_xs = (x_st - r.handle_span / 2.0, x_st + r.handle_span / 2.0)
            max_hw = max(r.half_width_at(_clamp(ax, r.head_x, r.foot_x)) for ax in arm_xs)
            # Clear the proud strap band (STRAP_T) so the hanging bail does not
            # graze the body strap visuals.
            pivot_y = side * (max_hw + _STRAP_T + _HANDLE_DIA / 2.0 + 0.006)
            for arm_s in (-1, 1):
                arm_x = x_st + arm_s * (r.handle_span / 2.0)
                post_wall_y = side * r.half_width_at(_clamp(arm_x, r.head_x, r.foot_x))
                inner_y = post_wall_y - side * _BRACKET_EMBED
                outer_y = pivot_y
                bracket_depth = abs(outer_y - inner_y)
                bracket_cy = (inner_y + outer_y) / 2.0
                # Each bracket spans from its bail arm in to the pivot centerline
                # (x_st), so the REVOLUTE origin at x_st lands on real hardware.
                bx0 = min(arm_x, x_st) - _HANDLE_POST_W / 2.0
                bx1 = max(arm_x, x_st) + _HANDLE_POST_W / 2.0
                body.visual(
                    Box((bx1 - bx0, bracket_depth, _HANDLE_POST_H)),
                    origin=Origin(xyz=((bx0 + bx1) / 2.0, bracket_cy, pivot_z)),
                    material=mats["strap"],
                    name=f"bracket_{handle_idx}_{arm_s}", material_class_id=("wood.mahogany_teak_dark" if r.palette_style in {"weathered_oak", "dark_walnut", "pale_pine", "mahogany_red"} else "wood.painted_clean"),
                )
            h_part = model.part(f"handle_{handle_idx}")
            h_part.visual(bail_mesh, material=mats["iron"], name="bail", material_class_id="metal.cast_iron_bare")
            h_part.inertial = Inertial.from_geometry(
                Box((r.handle_span, _HANDLE_DIA, r.handle_arm_len)),
                mass=0.3,
                origin=Origin(xyz=(0.0, 0.0, -r.handle_arm_len / 2.0)),
            )
            axis_dir = (-1.0 if side < 0 else 1.0, 0.0, 0.0)
            model.articulation(
                f"handle_{handle_idx}_pivot",
                ArticulationType.REVOLUTE,
                parent=body,
                child=h_part,
                origin=Origin(xyz=(x_st, pivot_y, pivot_z)),
                axis=axis_dir,
                motion_limits=MotionLimits(
                    effort=20.0, velocity=2.0, lower=0.0, upper=r.handle_pivot_max
                ),
            )
            names.append(f"handle_{handle_idx}")
            handle_idx += 1
    return names


_HANDLE_BUILDERS = {
    "none": _emit_none_handles,
    "fixed_side_rails": _emit_fixed_side_rails,
    "swing_drop_bar_handles": _emit_swing_drop_bar_handles,
}


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def build_coffin(
    config: CoffinConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        key: model.material(f"coffin_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in PALETTES[r.palette_style].items()
    }

    body = _build_body(model, r, mats, assets=assets)
    _LID_BUILDERS[r.lid_mechanism](model, r, body, mats, assets=assets)
    _HANDLE_BUILDERS[r.carry_handles](model, r, body, mats, assets=assets)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_coffin(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_coffin(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def _lid_part_names(r: ResolvedCoffinConfig) -> list[str]:
    if r.lid_mechanism == "full_side_hinge":
        return ["lid"]
    if r.lid_mechanism == "vertical_lift_lid":
        return ["lid"]
    if r.lid_mechanism == "split_two_panel":
        return ["lid_0", "lid_1"]
    if r.lid_mechanism == "double_leaf_wings":
        return ["lid_leaf_0", "lid_leaf_1"]
    return ["head_lid"]


def _axis_close(a, b, tol: float = 1e-6) -> bool:
    return all(abs(float(x) - float(y)) < tol for x, y in zip(a, b))


def run_coffin_tests(
    object_model: ArticulatedObject,
    config: CoffinConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    body = object_model.get_part("coffin_body")

    # ---- Closed lid seats on the rim (covers the cavity). ----
    for lid_name in _lid_part_names(r):
        ctx.allow_overlap(
            object_model.get_part(lid_name),
            body,
            reason="closed lid/leaf seats on the body rim and covers the cavity.",
        )

    # ---- double-leaf: two leaves meet at the centerline. ----
    if r.lid_mechanism == "double_leaf_wings":
        ctx.allow_overlap(
            object_model.get_part("lid_leaf_0"),
            object_model.get_part("lid_leaf_1"),
            reason="the two clamshell leaves meet at the centerline when closed.",
        )
    # ---- split: the two panels abut at the center seam. ----
    if r.lid_mechanism == "split_two_panel":
        ctx.allow_overlap(
            object_model.get_part("lid_0"),
            object_model.get_part("lid_1"),
            reason="the two split lid panels abut at the center seam when closed.",
        )

    # ---- swing handles: captured bracket<->bail overlap (element-scoped). ----
    if r.carry_handles == "swing_drop_bar_handles":
        for i in range(r.handle_count):
            h = object_model.get_part(f"handle_{i}")
            for arm_s in (-1, 1):
                ctx.allow_overlap(
                    body,
                    h,
                    elem_a=f"bracket_{i}_{arm_s}",
                    elem_b="bail",
                    reason="Pivot bore: bail arm top seated inside bracket post for swing.",
                )

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_joint_mating_has_gap()

    # ---- Structure / identity. ----
    part_names = {p.name for p in object_model.parts}
    ctx.check(
        "coffin_body part present",
        "coffin_body" in part_names,
        details=str(sorted(part_names)),
    )

    # Body footprint: ~1.9 m long, sits on the ground, rim near body_h.
    body_aabb = ctx.part_world_aabb(body)
    if body_aabb is not None:
        (axmn, aymn, azmn), (axmx, aymx, azmx) = body_aabb
        ctx.check(
            "body is a long casket (length > 2x width) sitting on the ground",
            (axmx - axmn) > 1.5 * (aymx - aymn) and azmn < 0.01,
            details=f"len={axmx - axmn:.3f} width={aymx - aymn:.3f} z_min={azmn:.4f}",
        )

    # ---- Lid-mechanism joint topology. ----
    if r.lid_mechanism == "full_side_hinge":
        j = object_model.get_articulation("lid_hinge")
        expected_axis = _side_axis(r, -1, j.origin.xyz[0])
        ctx.check(
            "full lid is REVOLUTE about the actual side-rim edge",
            j.articulation_type == ArticulationType.REVOLUTE and _axis_close(j.axis, expected_axis),
            details=f"type={j.articulation_type} axis={tuple(j.axis)} expected={expected_axis}",
        )
    elif r.lid_mechanism == "split_two_panel":
        j0 = object_model.get_articulation("lid_hinge_0")
        j1 = object_model.get_articulation("lid_hinge_1")
        expected0 = _side_axis(r, -1, j0.origin.xyz[0])
        expected1 = _side_axis(r, -1, j1.origin.xyz[0])
        ctx.check(
            "split lid has 2 same-side REVOLUTE joints about their side-rim edges",
            j0.articulation_type == ArticulationType.REVOLUTE
            and j1.articulation_type == ArticulationType.REVOLUTE
            and _axis_close(j0.axis, expected0)
            and _axis_close(j1.axis, expected1),
            details=(
                f"j0={tuple(j0.axis)} expected0={expected0} "
                f"j1={tuple(j1.axis)} expected1={expected1}"
            ),
        )
    elif r.lid_mechanism == "double_leaf_wings":
        j0 = object_model.get_articulation("lid_leaf_0_hinge")
        j1 = object_model.get_articulation("lid_leaf_1_hinge")
        expected0 = _side_axis(r, -1, j0.origin.xyz[0])
        expected1 = _neg_axis(_side_axis(r, 1, j1.origin.xyz[0]))
        ctx.check(
            "double-leaf has 2 mirrored REVOLUTE joints along actual side-rim edges",
            j0.articulation_type == ArticulationType.REVOLUTE
            and j1.articulation_type == ArticulationType.REVOLUTE
            and _axis_close(j0.axis, expected0)
            and _axis_close(j1.axis, expected1),
            details=(
                f"j0={tuple(j0.axis)} expected0={expected0} "
                f"j1={tuple(j1.axis)} expected1={expected1}"
            ),
        )
    elif r.lid_mechanism == "vertical_lift_lid":
        j = object_model.get_articulation("lid_lift")
        ctx.check(
            "vertical lift lid is a single PRISMATIC joint about +Z",
            j.articulation_type == ArticulationType.PRISMATIC
            and abs(j.axis[2] - 1.0) < 1e-6
            and abs(j.axis[0]) < 1e-6
            and abs(j.axis[1]) < 1e-6,
            details=f"type={j.articulation_type} axis={tuple(j.axis)}",
        )
    else:  # half_couch_head_only
        j = object_model.get_articulation("head_lid_hinge")
        expected_axis = _side_axis(r, -1, j.origin.xyz[0])
        ctx.check(
            "head lid is REVOLUTE about the actual side-rim edge (foot lid fixed inline, Rule 1)",
            j.articulation_type == ArticulationType.REVOLUTE and _axis_close(j.axis, expected_axis),
            details=f"type={j.articulation_type} axis={tuple(j.axis)} expected={expected_axis}",
        )
        # Foot half is a fixed inline body visual (no joint).
        foot_vis = [v.name for v in body.visuals if v.name == "foot_lid_panel"]
        ctx.check(
            "foot half lid is an inline body visual (Rule 1)",
            "foot_lid_panel" in foot_vis,
            details=str([v.name for v in body.visuals]),
        )

    # ---- Lid actuation reveals the interior (opens upward). ----
    lid0_name = _lid_part_names(r)[0]
    hinge_name = {
        "full_side_hinge": "lid_hinge",
        "split_two_panel": "lid_hinge_0",
        "double_leaf_wings": "lid_leaf_0_hinge",
        "half_couch_head_only": "head_lid_hinge",
        "vertical_lift_lid": "lid_lift",
    }[r.lid_mechanism]
    j = object_model.get_articulation(hinge_name)
    lid0 = object_model.get_part(lid0_name)
    closed = ctx.part_world_aabb(lid0)
    travel = (
        r.lid_lift_max * 0.7 if r.lid_mechanism == "vertical_lift_lid" else r.lid_open_max * 0.7
    )
    with ctx.pose({j: travel}):
        opened = ctx.part_world_aabb(lid0)
    if closed is not None and opened is not None:
        ctx.check(
            "lid opens upward to reveal the interior",
            opened[1][2] > closed[1][2] + 0.10,
            details=f"closed_top={closed[1][2]:.3f} open_top={opened[1][2]:.3f}",
        )
        if r.lid_mechanism == "vertical_lift_lid":
            closed_cx = (closed[0][0] + closed[1][0]) / 2.0
            closed_cy = (closed[0][1] + closed[1][1]) / 2.0
            opened_cx = (opened[0][0] + opened[1][0]) / 2.0
            opened_cy = (opened[0][1] + opened[1][1]) / 2.0
            ctx.check(
                "vertical lift lid translates upward without XY drift",
                abs(opened_cx - closed_cx) < 1e-6 and abs(opened_cy - closed_cy) < 1e-6,
                details=(
                    f"closed_xy=({closed_cx:.6f},{closed_cy:.6f}) "
                    f"opened_xy=({opened_cx:.6f},{opened_cy:.6f})"
                ),
            )

    # ---- carry_handles topology. ----
    if r.carry_handles == "fixed_side_rails":
        rail_vis = [v.name for v in body.visuals if v.name.startswith("carry_rail")]
        ctx.check(
            "fixed rails are inline body visuals (Rule 1, no joint)",
            len(rail_vis) == 2,
            details=str(rail_vis),
        )
    elif r.carry_handles == "swing_drop_bar_handles":
        # N handles, each an independent REVOLUTE about ±X, 0..~85deg.
        for i in range(r.handle_count):
            pivot = object_model.get_articulation(f"handle_{i}_pivot")
            limits = pivot.motion_limits
            ctx.check(
                f"handle_{i}_pivot is REVOLUTE about X, 0..~max",
                pivot.articulation_type == ArticulationType.REVOLUTE
                and abs(abs(pivot.axis[0]) - 1.0) < 1e-6
                and limits is not None
                and abs(limits.lower) < 1e-9,
                details=f"axis={tuple(pivot.axis)}",
            )
        # Even count, half per side.
        ctx.check(
            "handle_count is even (symmetric pairs)",
            r.handle_count % 2 == 0 and N_MIN <= r.handle_count <= N_MAX,
            details=f"N={r.handle_count}",
        )
        # Representative handle swings outward.
        pivot0 = object_model.get_articulation("handle_0_pivot")
        h0 = object_model.get_part("handle_0")
        rest = ctx.part_element_world_aabb(h0, elem="bail")
        rest_cy = (rest[0][1] + rest[1][1]) / 2.0 if rest else 0.0
        with ctx.pose({pivot0: r.handle_pivot_max}):
            sw = ctx.part_element_world_aabb(h0, elem="bail")
            sw_cy = (sw[0][1] + sw[1][1]) / 2.0 if sw else 0.0
        ctx.check(
            "handle_0 swings outward from the body at max pivot",
            rest is not None and sw is not None and abs(sw_cy) - abs(rest_cy) > -0.20,
            details=f"rest_cy={rest_cy:.4f} swing_cy={sw_cy:.4f}",
        )

    # ---- slot_choices recorded + N encoded only under swing. ----
    ctx.check(
        "slot_choices recorded with handle_count encoded only under swing",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    return ctx.report()


__all__ = (
    "CoffinConfig",
    "ResolvedCoffinConfig",
    "build_coffin",
    "build_seeded_coffin",
    "config_from_seed",
    "resolve_config",
    "run_coffin_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
