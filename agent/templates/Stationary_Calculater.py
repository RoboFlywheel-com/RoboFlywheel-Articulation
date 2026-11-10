# SPDX-License-Identifier: Apache-2.0

"""Pocket calculator modular template.

Sourced from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/Stationary_Calculater.md`` and the
``picture/Stationary/Calculater`` 5-star sample pool (1 parent + 5 single-axis
fork variants: keygrid / flip_cover / stand / round / tilt_display).

Structure (pattern = ``mixed``): a single root ``body`` chassis carries a set of
**parallel children** plus a **keypad multiplicity** axis:

  * ``shape_family`` (2): rectangular rounded slab + rounded-square keys, or
    elliptical pill slab + circular-disc keys. footprint and key-cap primitive
    vary together. (parent S0 vs round S4)
  * ``display_mount`` (2): fixed flush LCD inlined as a body visual, or a
    tilt-up LCD hinged at its bottom edge (REVOLUTE +X). (parent S0 vs S5)
  * ``keypad_cover`` (2, optional): none, or a hinged flip cover over the keypad
    (REVOLUTE -X). (parent S0 vs S2)
  * ``rear_support`` (2, optional): none, or a fold-out rear kickstand
    (REVOLUTE +X) nesting in a back-face recess. (parent S0 vs S3)
  * keypad **multiplicity**: an ``n_cols × n_rows`` regular grid of press keys
    (each PRISMATIC -Z), optional tall ``+`` key spanning two rows when
    ``n_cols >= 5``. Encoded in slot_choices as ``grid_{c}x{r}[_tallplus]`` so
    the ``module_topology_diversity`` gate sees distinct key topologies. (clean
    ``for i in range(n)`` emission from keygrid S1)

The solar-cell window is always a fixed body visual (no FIXED decoration part).
All articulated children use captured-pin / seated geometry, so their joints omit
``MatingContract`` (grandfathered) and rely on the flat articulation-origin
baseline + broad ``allow_overlap`` for the captured hinge hardware, mirroring
shopping_bucket's bail pivot treatment.
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
    clamp_joint_limits,
    mesh_from_cadquery,
    min_clearance_at_pose,
)

__modular__ = True

ShapeFamily = Literal["rectangular_square", "oval_disc"]
DisplayMount = Literal["fixed_flush_lcd", "tilt_up_hinged"]
KeypadCover = Literal["none", "flip_cover_hinged"]
RearSupport = Literal["none", "fold_out_kickstand"]
MaterialStyle = Literal["slate_cream", "black_grey", "silver_blue"]

SHAPE_FAMILIES: tuple[ShapeFamily, ...] = ("rectangular_square", "oval_disc")
DISPLAY_MOUNTS: tuple[DisplayMount, ...] = ("fixed_flush_lcd", "tilt_up_hinged")
KEYPAD_COVERS: tuple[KeypadCover, ...] = ("none", "flip_cover_hinged")
REAR_SUPPORTS: tuple[RearSupport, ...] = ("none", "fold_out_kickstand")
MATERIAL_STYLES: tuple[MaterialStyle, ...] = ("slate_cream", "black_grey", "silver_blue")

# Keypad grid multiplicity domain (spec §8).
N_COLS_MIN, N_COLS_MAX = 3, 6
N_ROWS_MIN, N_ROWS_MAX = 4, 6

PALETTES: dict[MaterialStyle, dict[str, tuple[float, float, float, float]]] = {
    "slate_cream": {
        "body": (0.42, 0.47, 0.58, 1.0),
        "display": (0.08, 0.07, 0.06, 1.0),
        "solar": (0.10, 0.09, 0.08, 1.0),
        "key": (0.92, 0.86, 0.74, 1.0),
        "accent": (0.86, 0.80, 0.68, 1.0),
        "cover": (0.28, 0.30, 0.36, 0.9),
    },
    "black_grey": {
        "body": (0.16, 0.16, 0.18, 1.0),
        "display": (0.06, 0.10, 0.07, 1.0),
        "solar": (0.05, 0.05, 0.06, 1.0),
        "key": (0.78, 0.79, 0.81, 1.0),
        "accent": (0.90, 0.55, 0.18, 1.0),
        "cover": (0.10, 0.11, 0.13, 0.9),
    },
    "silver_blue": {
        "body": (0.70, 0.72, 0.75, 1.0),
        "display": (0.07, 0.09, 0.11, 1.0),
        "solar": (0.08, 0.08, 0.10, 1.0),
        "key": (0.30, 0.42, 0.62, 1.0),
        "accent": (0.18, 0.28, 0.46, 1.0),
        "cover": (0.52, 0.55, 0.60, 0.9),
    },
}

# ---------------------------------------------------------------------------
# Base real-world dimensions (meters). Scaled per-build by body_scale.
# Baselines from parent 14e5e957 (rectangular) and round variant (elliptical).
# ---------------------------------------------------------------------------
_RECT_W = 0.075  # rectangular body width (X)
_RECT_L = 0.135  # rectangular body length (Y, portrait)
_OVAL_RX = 0.050  # elliptical body semi-axis X
_OVAL_RY = 0.078  # elliptical body semi-axis Y
_BODY_T = 0.012  # body thickness (Z) — not scaled (real slab thickness)
_CORNER_R = 0.006

_DISPLAY_W = 0.058
_DISPLAY_L = 0.030
_DISPLAY_Y = 0.040
_DISPLAY_DEPTH = 0.0022
_DISPLAY_INSET = 0.004

_SOLAR_W = 0.030
_SOLAR_L = 0.011
_SOLAR_Y = 0.058
_SOLAR_DEPTH = 0.0018

# Key press mechanism — real mechanical sizes, never scaled.
_KEY_TRAVEL = 0.0015
_KEY_PROUD = 0.0026
_WELL_DEPTH = 0.0020
_WELL_CLEAR = 0.0010

# Flip cover.
_COVER_T = 0.0018

# --- Two-hinged-panel motion budget (display + keypad cover share the upper
# body region; Contract 3c/3d single source). The tilt display hinges just
# above the keypad, the flip cover hinges at the keypad top edge — two
# independently-sampled panels whose arcs can collide when both open. The
# cover is capped so it opens toward vertical (stands up over the keypad) and
# never folds back over the +Y display region; when a tilt display is present
# the limit is additionally solver-clamped against the worst-case (fully
# tilted) display so the poses the solver clears match the poses the gate
# samples. ``_COVER_HINGE_DROP`` pushes the cover hinge below the display
# hinge to open a real (~6 mm) base gap between the two pivots.
_DISPLAY_TILT_MAX = 0.85  # rad, tilt-up LCD upper limit
_COVER_MAX_OPEN = 1.90  # rad, flip cover declared upper (opens past vertical)
_COVER_HINGE_DROP = 0.002  # cover hinge sits this far below the keypad top edge
_COVER_CLEAR_MARGIN = 0.005  # keep the open cover >= 5 mm from the tilted display

# Kickstand.
_KICK_W = 0.025
_KICK_L = 0.050
_KICK_T = 0.0020
_KICK_CORNER_R = 0.0020
_RECESS_CLEAR = 0.0010


@dataclass(frozen=True)
class CalculatorConfig:
    shape_family: ShapeFamily | None = None
    display_mount: DisplayMount | None = None
    keypad_cover: KeypadCover | None = None
    rear_support: RearSupport | None = None
    n_cols: int | None = None
    n_rows: int | None = None
    has_tall_plus: bool | None = None
    material_style: MaterialStyle = "slate_cream"
    body_scale: float = 1.0
    key_pitch_scale: float = 1.0
    cover_reach_scale: float = 1.0
    kickstand_len_scale: float = 1.0
    name: str = "calculator"


@dataclass(frozen=True)
class ResolvedCalculatorConfig:
    shape_family: ShapeFamily
    display_mount: DisplayMount
    keypad_cover: KeypadCover
    rear_support: RearSupport
    n_cols: int
    n_rows: int
    has_tall_plus: bool
    material_style: MaterialStyle
    # Concrete geometry (scaled).
    hx: float  # footprint half-extent X
    hy: float  # footprint half-extent Y
    body_t: float
    corner_r: float
    face_z: float
    display_w: float
    display_l: float
    display_y: float
    display_depth: float
    display_inset: float
    solar_w: float
    solar_l: float
    solar_y: float
    solar_depth: float
    key_pitch_scale: float
    cover_reach_scale: float
    kickstand_len_scale: float
    name: str

    @property
    def is_oval(self) -> bool:
        return self.shape_family == "oval_disc"


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


def config_from_seed(seed: int) -> CalculatorConfig:
    rng = random.Random(seed)
    # Weighted procedural sampling: optional appendages and the oval shape are
    # rarer, small keypads more common (spec §9 sampler policy).
    shape = rng.choices(SHAPE_FAMILIES, weights=[7, 3], k=1)[0]
    display = rng.choices(DISPLAY_MOUNTS, weights=[6, 4], k=1)[0]
    cover = rng.choices(KEYPAD_COVERS, weights=[6, 4], k=1)[0]
    support = rng.choices(REAR_SUPPORTS, weights=[6, 4], k=1)[0]
    n_cols = rng.choices([3, 4, 5, 6], weights=[2, 4, 3, 1], k=1)[0]
    n_rows = rng.choices([4, 5, 6], weights=[4, 4, 2], k=1)[0]
    tall = (n_cols >= 5) and (rng.random() < 0.45)
    return CalculatorConfig(
        shape_family=shape,
        display_mount=display,
        keypad_cover=cover,
        rear_support=support,
        n_cols=n_cols,
        n_rows=n_rows,
        has_tall_plus=tall,
        material_style=rng.choice(MATERIAL_STYLES),
        body_scale=round(rng.uniform(0.92, 1.12), 4),
        key_pitch_scale=round(rng.uniform(0.90, 1.10), 4),
        cover_reach_scale=round(rng.uniform(0.85, 1.05), 4),
        kickstand_len_scale=round(rng.uniform(0.85, 1.10), 4),
        name=f"seeded_calculator_{seed}",
    )


def resolve_config(
    config: CalculatorConfig | None = None,
) -> ResolvedCalculatorConfig:
    cfg = config or CalculatorConfig()
    shape = _pick(cfg.shape_family, SHAPE_FAMILIES)
    display = _pick(cfg.display_mount, DISPLAY_MOUNTS)
    cover = _pick(cfg.keypad_cover, KEYPAD_COVERS)
    support = _pick(cfg.rear_support, REAR_SUPPORTS)
    material_style = _pick(cfg.material_style, MATERIAL_STYLES)

    n_cols = int(_clamp(cfg.n_cols if cfg.n_cols is not None else 4, N_COLS_MIN, N_COLS_MAX))
    n_rows = int(_clamp(cfg.n_rows if cfg.n_rows is not None else 5, N_ROWS_MIN, N_ROWS_MAX))
    # has_tall_plus gated to scientific layouts (n_cols >= 5); spec §7 conditional.
    has_tall_plus = bool(cfg.has_tall_plus) and n_cols >= 5

    s = _clamp(cfg.body_scale, 0.92, 1.12)
    key_pitch_scale = _clamp(cfg.key_pitch_scale, 0.90, 1.10)
    cover_reach_scale = _clamp(cfg.cover_reach_scale, 0.85, 1.05)
    kickstand_len_scale = _clamp(cfg.kickstand_len_scale, 0.85, 1.10)

    if shape == "oval_disc":
        hx = _OVAL_RX * s
        hy = _OVAL_RY * s
    else:
        hx = _RECT_W * s / 2.0
        hy = _RECT_L * s / 2.0

    return ResolvedCalculatorConfig(
        shape_family=shape,
        display_mount=display,
        keypad_cover=cover,
        rear_support=support,
        n_cols=n_cols,
        n_rows=n_rows,
        has_tall_plus=has_tall_plus,
        material_style=material_style,
        hx=hx,
        hy=hy,
        body_t=_BODY_T,
        corner_r=_CORNER_R,
        face_z=_BODY_T,
        display_w=_DISPLAY_W * s,
        display_l=_DISPLAY_L * s,
        display_y=_DISPLAY_Y * s,
        display_depth=_DISPLAY_DEPTH,
        display_inset=_DISPLAY_INSET,
        solar_w=_SOLAR_W * s,
        solar_l=_SOLAR_L * s,
        solar_y=_SOLAR_Y * s,
        solar_depth=_SOLAR_DEPTH,
        key_pitch_scale=key_pitch_scale,
        cover_reach_scale=cover_reach_scale,
        kickstand_len_scale=kickstand_len_scale,
        name=cfg.name or "calculator",
    )


def with_overrides(config: CalculatorConfig, **kwargs: object) -> CalculatorConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: CalculatorConfig | ResolvedCalculatorConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedCalculatorConfig) else resolve_config(config)
    grid = f"grid_{r.n_cols}x{r.n_rows}" + ("_tallplus" if r.has_tall_plus else "")
    return (
        ("shape_family", r.shape_family),
        ("display_mount", r.display_mount),
        ("keypad_cover", r.keypad_cover),
        ("rear_support", r.rear_support),
        ("keypad", grid),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Footprint + keypad layout
# ---------------------------------------------------------------------------
def _half_width_at_y(r: ResolvedCalculatorConfig, y: float) -> float:
    """Footprint half-extent in X at a given Y (ellipse narrows toward poles)."""
    if r.is_oval:
        t = 1.0 - (y / r.hy) ** 2
        return r.hx * math.sqrt(t) if t > 0.0 else 0.0
    return r.hx


def _keypad_bounds(r: ResolvedCalculatorConfig) -> tuple[float, float]:
    """(keypad_top, keypad_bottom) Y band for the key grid, below the display."""
    top = r.display_y - r.display_l / 2.0 - 0.004
    bottom = (-r.hy * 0.78) if r.is_oval else (-r.hy + 0.008)
    return top, bottom


@dataclass(frozen=True)
class _KeySpec:
    kid: str
    cx: float
    cy: float
    w: float  # X footprint (disc: 2*radius)
    ly: float  # Y footprint (disc: 2*radius)
    is_accent: bool


def _keypad_layout(r: ResolvedCalculatorConfig):
    """Return (cols_x, rows_y, key_dim, pitch_x, pitch_y) for the regular grid."""
    top, bottom = _keypad_bounds(r)
    rows_y = [top - (i + 0.5) * (top - bottom) / r.n_rows for i in range(r.n_rows)]
    avail_half = min(_half_width_at_y(r, y) for y in rows_y) * 0.84
    cols_x = [-avail_half + (j + 0.5) * (2.0 * avail_half / r.n_cols) for j in range(r.n_cols)]
    pitch_x = 2.0 * avail_half / r.n_cols
    pitch_y = (top - bottom) / r.n_rows
    # Key footprint kept strictly below the cell pitch so neighbors never touch.
    key_dim = min(pitch_x, pitch_y) * 0.74 * r.key_pitch_scale
    key_dim = min(key_dim, min(pitch_x, pitch_y) * 0.90)
    return cols_x, rows_y, key_dim, pitch_x, pitch_y


def _keypad_specs(r: ResolvedCalculatorConfig) -> list[_KeySpec]:
    cols_x, rows_y, key_dim, _pitch_x, _pitch_y = _keypad_layout(r)
    specs: list[_KeySpec] = []
    # The accent column (operator keys) is the rightmost column.
    accent_col = r.n_cols - 1
    skip: set[tuple[int, int]] = set()
    if r.has_tall_plus:
        skip = {(r.n_rows - 2, accent_col), (r.n_rows - 1, accent_col)}
    k = 0
    for i in range(r.n_rows):
        for j in range(r.n_cols):
            if (i, j) in skip:
                continue
            specs.append(
                _KeySpec(
                    kid=f"key_{k}",
                    cx=cols_x[j],
                    cy=rows_y[i],
                    w=key_dim,
                    ly=key_dim,
                    is_accent=(j == accent_col) or (i == 0),
                )
            )
            k += 1
    if r.has_tall_plus:
        cy = (rows_y[r.n_rows - 2] + rows_y[r.n_rows - 1]) / 2.0
        tall_l = abs(rows_y[r.n_rows - 2] - rows_y[r.n_rows - 1]) + key_dim
        specs.append(
            _KeySpec(
                kid=f"key_{k}",
                cx=cols_x[accent_col],
                cy=cy,
                w=key_dim,
                ly=tall_l,
                is_accent=True,
            )
        )
    return specs


# ---------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------
def _rounded_box(width: float, length: float, height: float, radius: float):
    return (
        cq.Workplane("XY")
        .box(width, length, height, centered=(True, True, False))
        .edges("|Z")
        .fillet(min(radius, 0.49 * min(width, length)))
    )


def _kickstand_geom(r: ResolvedCalculatorConfig) -> tuple[float, float, float]:
    """(kick_w, kick_l, hinge_y) for the rear support, clamped to the footprint."""
    kick_l = _KICK_L * r.kickstand_len_scale
    hinge_y = r.hy * 0.55
    # Keep the stowed leg + recess inside the footprint.
    kick_l = min(kick_l, hinge_y + r.hy - 0.006)
    half_at = _half_width_at_y(r, hinge_y - kick_l / 2.0)
    kick_w = min(_KICK_W, 2.0 * half_at * 0.7)
    return kick_w, kick_l, hinge_y


def _cover_geom(r: ResolvedCalculatorConfig):
    """Flip-cover dimensions + hinge placement (covers the keypad region only)."""
    top, bottom = _keypad_bounds(r)
    # Drop the cover hinge below the keypad top edge so its pivot sits clear of
    # the tilt-display hinge (which is ~4 mm above `top`); this opens the base
    # gap between the two panels' pivots (single source: _COVER_HINGE_DROP).
    hinge_y = top - _COVER_HINGE_DROP
    cover_l = (hinge_y - bottom) * r.cover_reach_scale
    half_at = _half_width_at_y(r, (hinge_y + bottom) / 2.0)
    cover_w = 2.0 * half_at * 0.84
    hinge_z = r.face_z + _KEY_PROUD + _COVER_T + 0.0003
    return cover_w, cover_l, hinge_y, hinge_z


def _build_body_mesh(r: ResolvedCalculatorConfig, *, assets):
    """Root body shell: slab + display/solar recesses + key wells, plus the
    hinge hardware unioned in for whichever optional mechanisms are present."""
    if r.is_oval:
        body = cq.Workplane("XY").ellipse(r.hx, r.hy).extrude(r.body_t)
        try:
            body = body.edges(">Z").fillet(0.001)
        except Exception:
            pass
    else:
        body = _rounded_box(2.0 * r.hx, 2.0 * r.hy, r.body_t, r.corner_r)
        # Cosmetic molded bezel groove around the perimeter (rect only).
        groove = (
            cq.Workplane("XY")
            .workplane(offset=r.face_z)
            .rect(2.0 * r.hx - 0.005, 2.0 * r.hy - 0.005)
            .rect(2.0 * r.hx - 0.008, 2.0 * r.hy - 0.008)
            .extrude(-0.0006)
        )
        body = body.cut(groove)

    # Display recess (rectangular for both shapes).
    body = body.cut(
        cq.Workplane("XY")
        .workplane(offset=r.face_z)
        .center(0.0, r.display_y)
        .rect(r.display_w, r.display_l)
        .extrude(-r.display_depth)
    )
    # Solar-cell window recess.
    body = body.cut(
        cq.Workplane("XY")
        .workplane(offset=r.face_z)
        .center(0.0, r.solar_y)
        .rect(r.solar_w, r.solar_l)
        .extrude(-r.solar_depth)
    )

    # Key wells.
    for spec in _keypad_specs(r):
        if r.is_oval:
            radius = spec.w / 2.0
            well = (
                cq.Workplane("XY")
                .workplane(offset=r.face_z)
                .center(spec.cx, spec.cy)
                .circle(radius + _WELL_CLEAR)
                .extrude(-_WELL_DEPTH)
            )
        else:
            well = (
                cq.Workplane("XY")
                .workplane(offset=r.face_z)
                .center(spec.cx, spec.cy)
                .rect(spec.w + 2.0 * _WELL_CLEAR, spec.ly + 2.0 * _WELL_CLEAR)
                .extrude(-_WELL_DEPTH)
            )
        body = body.cut(well)

    # Tilt-display hinge barrel at the bottom edge of the display recess.
    if r.display_mount == "tilt_up_hinged":
        hinge_y = r.display_y - r.display_l / 2.0
        hinge_z = r.face_z - r.display_depth
        barrel_len = r.display_w - r.display_inset + 0.004
        barrel = (
            cq.Workplane("YZ", origin=(-barrel_len / 2.0, hinge_y, hinge_z))
            .circle(0.0012)
            .extrude(barrel_len)
        )
        body = body.union(barrel)

    # Flip-cover hinge brackets + barrel along the keypad top edge.
    if r.keypad_cover == "flip_cover_hinged":
        cover_w, _cover_l, hinge_y, hinge_z = _cover_geom(r)
        bracket_h = hinge_z - r.face_z + 0.002
        bracket_x = cover_w / 2.0 - 0.006
        for sign in (-1.0, 1.0):
            bracket = (
                cq.Workplane("XY")
                .workplane(offset=r.face_z - 0.001)
                .center(sign * bracket_x, hinge_y)
                .box(0.006, 0.008, bracket_h + 0.001, centered=(True, True, False))
            )
            body = body.union(bracket)
        barrel = (
            cq.Workplane("YZ", origin=(-cover_w / 2.0, hinge_y, hinge_z))
            .circle(0.002)
            .extrude(cover_w)
        )
        body = body.union(barrel)

    # Rear kickstand recess (a shallow pocket cut into the back face, z=0..t).
    if r.rear_support == "fold_out_kickstand":
        kick_w, kick_l, hinge_y = _kickstand_geom(r)
        recess_cy = hinge_y - kick_l / 2.0
        body = body.cut(
            cq.Workplane("XY")
            .workplane(offset=0.0)
            .center(0.0, recess_cy)
            .rect(kick_w + 2.0 * _RECESS_CLEAR, kick_l + 2.0 * _RECESS_CLEAR)
            .extrude(_KICK_T)
        )

    return mesh_from_cadquery(body, "body_shell", assets=assets)


def _build_display_panel_mesh(r: ResolvedCalculatorConfig, *, hinged: bool, assets):
    pw = r.display_w - r.display_inset
    pl = r.display_l - r.display_inset
    if hinged:
        # Hinge edge at part-frame y=0; panel extends in +Y, sits on z=0.
        panel = (
            cq.Workplane("XY")
            .center(0.0, pl / 2.0)
            .box(pw, pl, 0.0016, centered=(True, True, False))
            .edges("|Z")
            .fillet(0.002)
        )
    else:
        panel = _rounded_box(pw, pl, 0.0016, 0.002)
    return mesh_from_cadquery(panel, "lcd", assets=assets)


def _build_solar_panel_mesh(r: ResolvedCalculatorConfig, *, assets):
    panel = _rounded_box(r.solar_w - 0.003, r.solar_l - 0.003, 0.0012, 0.0015)
    return mesh_from_cadquery(panel, "solar_cell", assets=assets)


def _build_key_mesh(r: ResolvedCalculatorConfig, spec: _KeySpec, *, assets):
    height = _KEY_PROUD + _WELL_DEPTH
    if r.is_oval:
        radius = spec.w / 2.0
        if spec.ly > spec.w + 1e-6:
            # Tall disc key: a stadium (capsule) footprint spanning two rows.
            key = (
                cq.Workplane("XY")
                .slot2D(spec.ly, 2.0 * radius, 90.0)
                .extrude(height)
                .edges(">Z")
                .fillet(min(0.0006, radius * 0.25))
            )
        else:
            key = (
                cq.Workplane("XY")
                .circle(radius)
                .extrude(height)
                .edges(">Z")
                .fillet(min(0.0006, radius * 0.25))
            )
    else:
        key = (
            cq.Workplane("XY")
            .box(spec.w, spec.ly, height, centered=(True, True, False))
            .edges("|Z")
            .fillet(min(spec.w, spec.ly) * 0.28)
            .edges(">Z")
            .fillet(0.0006)
        )
    return mesh_from_cadquery(key, spec.kid, assets=assets)


def _build_cover_mesh(r: ResolvedCalculatorConfig, *, assets):
    cover_w, cover_l, _hinge_y, _hinge_z = _cover_geom(r)
    cover = (
        cq.Workplane("XY")
        .box(cover_w, cover_l, _COVER_T, centered=(True, True, False))
        .edges("|Z")
        .fillet(0.003)
        # Hinge edge (y=+cover_l/2) -> y=0; top surface -> z=0.
        .translate((0.0, -cover_l / 2.0, -_COVER_T))
    )
    return mesh_from_cadquery(cover, "cover_panel", assets=assets)


def _build_kickstand_mesh(r: ResolvedCalculatorConfig, *, assets):
    kick_w, kick_l, _hinge_y = _kickstand_geom(r)
    kick = (
        cq.Workplane("XY")
        .box(kick_w, kick_l, _KICK_T, centered=(True, True, False))
        .edges("|Z")
        .fillet(_KICK_CORNER_R)
        # Hinge edge at y=0; leg extends in -Y, thickness z=0..t.
        .translate((0.0, -kick_l / 2.0, 0.0))
    )
    return mesh_from_cadquery(kick, "kickstand_leg", assets=assets)


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def _emit_keypad(model, r, body, mats, *, assets) -> list[str]:
    specs = _keypad_specs(r)
    # Cache key meshes by footprint so identical keys reuse geometry.
    cache: dict[tuple, object] = {}
    names: list[str] = []
    height = _KEY_PROUD + _WELL_DEPTH
    for spec in specs:
        ck = (round(spec.w, 5), round(spec.ly, 5))
        mesh = cache.get(ck)
        if mesh is None:
            mesh = _build_key_mesh(r, spec, assets=assets)
            cache[ck] = mesh
        key = model.part(spec.kid)
        mat = mats["accent"] if spec.is_accent else mats["key"]
        key.visual(mesh, material=mat, name="key_cap", material_class_id="plastic.opaque_glossy_molded")
        key.inertial = Inertial.from_geometry(
            Box((spec.w, spec.ly, height)),
            mass=0.0015,
            origin=Origin(xyz=(0.0, 0.0, height / 2.0)),
        )
        # PRISMATIC press: joint frame at the well floor, axis -Z presses down.
        model.articulation(
            f"body_to_{spec.kid}",
            ArticulationType.PRISMATIC,
            parent=body,
            child=key,
            origin=Origin(xyz=(spec.cx, spec.cy, r.face_z - _WELL_DEPTH)),
            axis=(0.0, 0.0, -1.0),
            motion_limits=MotionLimits(effort=3.0, velocity=0.05, lower=0.0, upper=_KEY_TRAVEL),
        )
        names.append(spec.kid)
    return names


def _emit_display(model, r, body, mats, *, assets) -> list[str]:
    if r.display_mount == "fixed_flush_lcd":
        # Inline flush LCD as a body visual (no FIXED decoration part).
        body.visual(
            _build_display_panel_mesh(r, hinged=False, assets=assets),
            material=mats["display"],
            name="lcd", material_class_id="tech.control_interface",
            origin=Origin(xyz=(0.0, r.display_y, r.face_z - r.display_depth)),
        )
        return []
    # Tilt-up hinged LCD part.
    hinge_y = r.display_y - r.display_l / 2.0
    hinge_z = r.face_z - r.display_depth
    display = model.part("display")
    display.visual(
        _build_display_panel_mesh(r, hinged=True, assets=assets),
        material=mats["display"],
        name="lcd", material_class_id="tech.control_interface",
    )
    display.inertial = Inertial.from_geometry(
        Box((r.display_w, r.display_l, 0.0016)),
        mass=0.01,
        origin=Origin(xyz=(0.0, r.display_l / 2.0, 0.0008)),
    )
    model.articulation(
        "body_to_display",
        ArticulationType.REVOLUTE,
        parent=body,
        child=display,
        origin=Origin(xyz=(0.0, hinge_y, hinge_z)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=2.0, velocity=1.5, lower=0.0, upper=_DISPLAY_TILT_MAX),
    )
    return ["display"]


def _emit_cover(model, r, body, mats, *, assets) -> list[str]:
    if r.keypad_cover != "flip_cover_hinged":
        return []
    cover_w, cover_l, hinge_y, hinge_z = _cover_geom(r)
    cover = model.part("keypad_cover")
    cover.visual(_build_cover_mesh(r, assets=assets), material=mats["cover"], name="cover_panel", material_class_id="plastic.frosted_translucent")
    cover.inertial = Inertial.from_geometry(
        Box((cover_w, cover_l, _COVER_T)),
        mass=0.012,
        origin=Origin(xyz=(0.0, -cover_l / 2.0, -_COVER_T / 2.0)),
    )
    # REVOLUTE about -X: positive q lifts the free edge (opens the cover). At
    # q=0 the cover lies flat over the keypad. The declared upper caps the cover
    # at "opens toward vertical" so it never folds back over the display region.
    model.articulation(
        "body_to_cover",
        ArticulationType.REVOLUTE,
        parent=body,
        child=cover,
        origin=Origin(xyz=(0.0, hinge_y, hinge_z)),
        axis=(-1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=2.0, velocity=4.0, lower=0.0, upper=_COVER_MAX_OPEN),
    )
    # Two-hinged-panel clearance (Contract 3d): when a tilt-up display shares the
    # upper body region, solve the cover's travel against the WORST-CASE (fully
    # tilted) display so the cover arc can never sweep into the display arc. The
    # display tilts up-and-back (+Y/+Z) monotonically, so holding it at its upper
    # limit is the closest approach for every lower display angle — the solved
    # cover limit therefore clears the display across its whole range. The gate
    # samples exactly these poses, so limit == gate (single source).
    if r.display_mount == "tilt_up_hinged":
        clamp_joint_limits(
            model,
            "body_to_cover",
            margin=_COVER_CLEAR_MARGIN,
            keepout=["display"],
            base_pose={"body_to_display": _DISPLAY_TILT_MAX},
        )
    return ["keypad_cover"]


def _emit_kickstand(model, r, body, mats, *, assets) -> list[str]:
    if r.rear_support != "fold_out_kickstand":
        return []
    _kick_w, _kick_l, hinge_y = _kickstand_geom(r)
    kick = model.part("kickstand")
    kick.visual(
        _build_kickstand_mesh(r, assets=assets), material=mats["cover"], name="kickstand_leg", material_class_id="plastic.opaque_glossy_molded"
    )
    kick.inertial = Inertial.from_geometry(
        Box((_kick_w, _kick_l, _KICK_T)),
        mass=0.005,
        origin=Origin(xyz=(0.0, -_kick_l / 2.0, _KICK_T / 2.0)),
    )
    # REVOLUTE about +X at the back face: positive q swings the free end below
    # the back face (-Z) to prop the calculator; q=0 stows flat in the recess.
    model.articulation(
        "body_to_kickstand",
        ArticulationType.REVOLUTE,
        parent=body,
        child=kick,
        origin=Origin(xyz=(0.0, hinge_y, 0.0)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=2.0, velocity=1.0, lower=0.0, upper=0.60),
    )
    return ["kickstand"]


def build_calculator(
    config: CalculatorConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    palette = PALETTES[r.material_style]
    mats = {
        key: model.material(f"calc_{key}_{r.material_style}", rgba=palette[key])
        for key in ("body", "display", "solar", "key", "accent", "cover")
    }

    # Root body shell (carries inlined solar + flush display visuals).
    body = model.part("body")
    body.visual(_build_body_mesh(r, assets=assets), material=mats["body"], name="body_shell", material_class_id="plastic.opaque_glossy_molded")
    body.visual(
        _build_solar_panel_mesh(r, assets=assets),
        material=mats["solar"],
        name="solar_cell", material_class_id="tech.solar_cell",
        origin=Origin(xyz=(0.0, r.solar_y, r.face_z - r.solar_depth)),
    )
    body.inertial = Inertial.from_geometry(
        Box((2.0 * r.hx, 2.0 * r.hy, r.body_t)),
        mass=0.09,
        origin=Origin(xyz=(0.0, 0.0, r.body_t / 2.0)),
    )

    _emit_display(model, r, body, mats, assets=assets)
    _emit_keypad(model, r, body, mats, assets=assets)
    _emit_cover(model, r, body, mats, assets=assets)
    _emit_kickstand(model, r, body, mats, assets=assets)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_calculator(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_calculator(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def run_calculator_tests(
    object_model: ArticulatedObject,
    config: CalculatorConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    body = object_model.get_part("body")

    # --- Captured-pin / seated allowances for the articulated children. ---
    if r.display_mount == "tilt_up_hinged":
        ctx.allow_overlap(
            body,
            object_model.get_part("display"),
            reason=(
                "tilt-up LCD panel seats in the display recess and its hinge edge "
                "wraps the body hinge barrel (captured-pin pivot)."
            ),
        )
    if r.keypad_cover == "flip_cover_hinged":
        ctx.allow_overlap(
            body,
            object_model.get_part("keypad_cover"),
            reason=(
                "flip cover hinge edge captures the body bracket+barrel hardware "
                "(captured-pin pivot); closed cover rests just above the key caps."
            ),
        )
    if r.rear_support == "fold_out_kickstand":
        ctx.allow_overlap(
            body,
            object_model.get_part("kickstand"),
            reason="stowed kickstand leg nests flush inside the rear-face recess.",
        )

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    # Joints omit MatingContract (captured-pin / seated geometry, grandfathered);
    # the flat 0.015 m articulation-origin baseline runs in the compiler and all
    # origins sit on real hardware (well floor / hinge barrel / recess / back face).
    ctx.fail_if_joint_mating_has_gap()

    # --- Keypad: regular grid of prismatic press keys. ---
    specs = _keypad_specs(r)
    expected_keys = r.n_cols * r.n_rows - (1 if r.has_tall_plus else 0)
    ctx.check(
        "keypad emits the expected number of keys",
        len(specs) == expected_keys,
        details=f"emitted={len(specs)} expected={expected_keys}",
    )
    for spec in specs:
        j = object_model.get_articulation(f"body_to_{spec.kid}")
        ctx.check(
            f"{spec.kid} is PRISMATIC pressing along -Z",
            j.articulation_type == ArticulationType.PRISMATIC and round(j.axis[2], 3) == -1.0,
            details=f"type={j.articulation_type} axis={tuple(round(c, 3) for c in j.axis)}",
        )

    # --- A key presses straight down by its stroke. ---
    k0 = object_model.get_part("key_0")
    j0 = object_model.get_articulation("body_to_key_0")
    rest = ctx.part_world_position(k0)
    with ctx.pose({j0: _KEY_TRAVEL}):
        pressed = ctx.part_world_position(k0)
    if rest is not None and pressed is not None:
        drop = rest[2] - pressed[2]
        ctx.check(
            "pressing key_0 moves it down by the stroke",
            abs(drop - _KEY_TRAVEL) < 1e-4 and drop > 0.0,
            details=f"drop={drop:.5f} expected={_KEY_TRAVEL:.5f}",
        )

    # --- Keys are captured in the body face (proud at rest, base sunk in well). ---
    k0_aabb = ctx.part_world_aabb(k0)
    if k0_aabb is not None:
        ctx.check(
            "key_0 rises above the body face and sinks into its well",
            k0_aabb[1][2] > r.face_z - 0.0005 and k0_aabb[0][2] < r.face_z - 0.0005,
            details=f"z=[{k0_aabb[0][2]:.4f},{k0_aabb[1][2]:.4f}] face={r.face_z:.4f}",
        )

    # --- Display mount topology. ---
    if r.display_mount == "tilt_up_hinged":
        jd = object_model.get_articulation("body_to_display")
        ctx.check(
            "tilt display is REVOLUTE about +X",
            jd.articulation_type == ArticulationType.REVOLUTE and round(jd.axis[0], 3) == 1.0,
            details=f"type={jd.articulation_type} axis={tuple(round(c, 3) for c in jd.axis)}",
        )
        disp = object_model.get_part("display")
        with ctx.pose({jd: 0.0}):
            a0 = ctx.part_world_aabb(disp)
        with ctx.pose({jd: 0.7}):
            a1 = ctx.part_world_aabb(disp)
        if a0 is not None and a1 is not None:
            ctx.check(
                "tilting the display lifts its top edge",
                a1[1][2] > a0[1][2] + 0.003,
                details=f"flat_top={a0[1][2]:.4f} tilted_top={a1[1][2]:.4f}",
            )
    else:
        ctx.check(
            "flush display is inlined as a body visual (no display part)",
            "display" not in {p.name for p in object_model.parts}
            and "lcd" in {v.name for v in body.visuals},
            details=str([v.name for v in body.visuals]),
        )

    # --- Solar window is always a fixed body visual. ---
    ctx.check(
        "solar window is a body visual",
        "solar_cell" in {v.name for v in body.visuals},
        details=str([v.name for v in body.visuals]),
    )

    # --- Optional flip cover. ---
    if r.keypad_cover == "flip_cover_hinged":
        jc = object_model.get_articulation("body_to_cover")
        ctx.check(
            "flip cover is REVOLUTE about -X",
            jc.articulation_type == ArticulationType.REVOLUTE and round(jc.axis[0], 3) == -1.0,
            details=f"type={jc.articulation_type} axis={tuple(round(c, 3) for c in jc.axis)}",
        )
        cover = object_model.get_part("keypad_cover")
        with ctx.pose({jc: 0.0}):
            c0 = ctx.part_world_aabb(cover)
        with ctx.pose({jc: 1.5}):
            c1 = ctx.part_world_aabb(cover)
        if c0 is not None and c1 is not None:
            ctx.check(
                "opening the cover raises it",
                (c1[0][2] + c1[1][2]) / 2.0 > (c0[0][2] + c0[1][2]) / 2.0 + 0.004,
                details=f"closed_zc={(c0[0][2] + c0[1][2]) / 2.0:.4f} open_zc={(c1[0][2] + c1[1][2]) / 2.0:.4f}",
            )
        # Two-hinged-panel guard (Contract 3d): the fully open cover must clear a
        # fully tilted display. Mirrors the motion-QC worst-case pose so the
        # solved limit and the gate can't disagree; regression cover for the
        # display<->keypad_cover 穿模 census failure.
        if r.display_mount == "tilt_up_hinged":
            clear = min_clearance_at_pose(
                object_model,
                joint="body_to_cover",
                joint_positions={
                    "body_to_display": _DISPLAY_TILT_MAX,
                    "body_to_cover": jc.motion_limits.upper,
                },
                keepout=["display"],
            )
            ctx.check(
                "open cover clears the tilted display",
                clear >= _COVER_CLEAR_MARGIN - 1e-4,
                details=(
                    f"clearance={clear:.5f} margin={_COVER_CLEAR_MARGIN:.5f} "
                    f"cover_upper={jc.motion_limits.upper:.4f}"
                ),
            )

    # --- Optional rear kickstand. ---
    if r.rear_support == "fold_out_kickstand":
        jk = object_model.get_articulation("body_to_kickstand")
        ctx.check(
            "kickstand is REVOLUTE about +X",
            jk.articulation_type == ArticulationType.REVOLUTE and round(jk.axis[0], 3) == 1.0,
            details=f"type={jk.articulation_type} axis={tuple(round(c, 3) for c in jk.axis)}",
        )
        kick = object_model.get_part("kickstand")
        with ctx.pose({jk: 0.0}):
            s0 = ctx.part_world_aabb(kick)
        with ctx.pose({jk: 0.60}):
            s1 = ctx.part_world_aabb(kick)
        if s0 is not None and s1 is not None:
            ctx.check(
                "deploying the kickstand swings its free end below the back face",
                s1[0][2] < s0[0][2] - 0.005 and s1[0][2] < -0.003,
                details=f"stowed_zmin={s0[0][2]:.4f} deployed_zmin={s1[0][2]:.4f}",
            )

    # --- Body silhouette: portrait slab resting near z=0. ---
    body_aabb = ctx.part_world_aabb(body)
    if body_aabb is not None:
        (bx0, by0, bz0), (bx1, by1, bz1) = body_aabb
        ctx.check(
            "body is a portrait thin slab",
            (by1 - by0) > (bx1 - bx0) and bz0 < 0.01,
            details=f"ext_x={bx1 - bx0:.4f} ext_y={by1 - by0:.4f} z_min={bz0:.4f}",
        )

    # --- slot_choices recorded. ---
    ctx.check(
        "slot_choices_recorded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    return ctx.report()


__all__ = (
    "CalculatorConfig",
    "ResolvedCalculatorConfig",
    "build_calculator",
    "build_seeded_calculator",
    "config_from_seed",
    "resolve_config",
    "run_calculator_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
