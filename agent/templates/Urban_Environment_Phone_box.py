# SPDX-License-Identifier: Apache-2.0

"""phone_box — British K6 red telephone kiosk, modular procedural template.

Category identity: a glazed walk-in K6-style telephone kiosk — a near-square
upright enclosed cell on a low plinth, four corner pilasters, regular
multi-pane mullion glazing walls (rows x cols multiplicity), a "TELEPHONE"
frieze band near the top, and a crown roof (domed / flat / pediment). The ONE
defining moving part is a vertical-hinge (+Z) REVOLUTE door / bi-fold leaves /
side access panel.

Sourced from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/Urban_Environment_Phone_box.md`` (10 five-star
records: 1 parent + 9 converged variant forks).

Pattern = ``mixed``: a single ``kiosk_body`` root part carries fixed visuals
(plinth, corner pilasters, kick panels, glazed mullion walls, frieze band, and
the crown roof — Rule 1, all parent ``.visual(...)``) plus ONE category-defining
REVOLUTE door/leaf/panel child (bi-fold adds a ``Mimic`` follower leaf).

Coordinate convention: +Z up, width along X, depth along Y. The front face
(where the door is) is +X. Plinth bottom sits at z=0; the kiosk stands upright.

Slots (all orthogonal, any combination legal):
  * Slot A ``roof`` (3): domed_k6 (CadQuery lathe/revolve ogee dome — NOT a Box
    downgrade) / flat_slab (overhang slab) / pediment (hand-built MeshGeometry
    triangular-prism gable).
  * Slot B ``door`` (3): single_hinge (1 REVOLUTE) / bifold (driver REVOLUTE +
    Mimic follower REVOLUTE) / open_side (front walk-in doorway + side access
    panel REVOLUTE on +Y).
  * Slot C ``glaze`` (3): sparse 2x4 / medium 3x6 / dense 4x8 mullion grid,
    loop-emitted multiplicity.
  * Slot D ``foot`` (2): square one-person / wide two-person footprint.

3 hard rules honoured:
  1. Mullions, frieze sign band, glazing bars, crown emblems are parent
     ``.visual(...)`` (NOT FIXED-joint parts).
  2. The door/leaf/panel REVOLUTE declares a MatingContract OR is grandfathered
     with element-scoped ``allow_overlap`` (hinge stile lapping the pilaster).
  3. Domed roof is a real CadQuery lathe (``revolve``); pediment is hand-built
     ``MeshGeometry`` — never a crude Box downgrade.

palette_style (>=6 colorways) is sampled per seed and drives every
``.visual(..., material=...)``.
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
    Cylinder,
    MeshGeometry,
    Mimic,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
    mesh_from_geometry,
)

__modular__ = True

# ---------------------------------------------------------------------------
# Slot enums
# ---------------------------------------------------------------------------
RoofChoice = Literal["roof_domed_k6", "roof_flat_slab", "roof_pediment"]
DoorChoice = Literal["door_single_hinge", "door_bifold", "door_open_side"]
GlazeChoice = Literal["glaze_sparse_2x4", "glaze_medium_3x6", "glaze_dense_4x8"]
FootChoice = Literal["foot_square_1person", "foot_wide_2person"]
PaletteStyle = Literal[
    "classic_red",
    "air_force_blue",
    "municipal_green",
    "noir_black",
    "polished_silver",
    "royal_post_red",
]

ROOF_CHOICES: tuple[RoofChoice, ...] = (
    "roof_domed_k6",
    "roof_flat_slab",
    "roof_pediment",
)
DOOR_CHOICES: tuple[DoorChoice, ...] = (
    "door_single_hinge",
    "door_bifold",
    "door_open_side",
)
GLAZE_CHOICES: tuple[GlazeChoice, ...] = (
    "glaze_sparse_2x4",
    "glaze_medium_3x6",
    "glaze_dense_4x8",
)
FOOT_CHOICES: tuple[FootChoice, ...] = (
    "foot_square_1person",
    "foot_wide_2person",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "classic_red",
    "air_force_blue",
    "municipal_green",
    "noir_black",
    "polished_silver",
    "royal_post_red",
)

# Palette keys: body (pilasters/plinth/frieze frame), trim (kick/bars/roof trim),
# glass, hardware (handle/hinge), accent (frieze text / crown emblem / finial).
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "classic_red": {
        "body": (0.66, 0.07, 0.07, 1.0),
        "trim": (0.50, 0.05, 0.05, 1.0),
        "glass": (0.30, 0.40, 0.42, 0.34),
        "hardware": (0.82, 0.82, 0.84, 1.0),
        "accent": (0.92, 0.86, 0.40, 1.0),
    },
    "air_force_blue": {
        "body": (0.18, 0.28, 0.42, 1.0),
        "trim": (0.12, 0.20, 0.32, 1.0),
        "glass": (0.40, 0.52, 0.58, 0.32),
        "hardware": (0.80, 0.81, 0.83, 1.0),
        "accent": (0.86, 0.88, 0.92, 1.0),
    },
    "municipal_green": {
        "body": (0.10, 0.32, 0.20, 1.0),
        "trim": (0.07, 0.24, 0.15, 1.0),
        "glass": (0.36, 0.48, 0.46, 0.32),
        "hardware": (0.78, 0.79, 0.80, 1.0),
        "accent": (0.90, 0.86, 0.46, 1.0),
    },
    "noir_black": {
        "body": (0.07, 0.07, 0.08, 1.0),
        "trim": (0.03, 0.03, 0.04, 1.0),
        "glass": (0.10, 0.13, 0.18, 0.42),
        "hardware": (0.55, 0.56, 0.58, 1.0),
        "accent": (0.80, 0.66, 0.24, 1.0),
    },
    "polished_silver": {
        "body": (0.70, 0.71, 0.73, 1.0),
        "trim": (0.55, 0.56, 0.58, 1.0),
        "glass": (0.58, 0.66, 0.72, 0.30),
        "hardware": (0.40, 0.41, 0.43, 1.0),
        "accent": (0.30, 0.31, 0.33, 1.0),
    },
    "royal_post_red": {
        "body": (0.74, 0.10, 0.12, 1.0),
        "trim": (0.10, 0.10, 0.11, 1.0),
        "glass": (0.32, 0.42, 0.44, 0.34),
        "hardware": (0.85, 0.85, 0.87, 1.0),
        "accent": (0.95, 0.90, 0.50, 1.0),
    },
}

# ---------------------------------------------------------------------------
# Base dimensions (meters). Width = X, depth = Y, height = Z.
# ---------------------------------------------------------------------------
_PLINTH_H = 0.10  # low plinth height
_PLINTH_OVER = 0.04  # plinth oversize beyond body footprint (per side)
_POST = 0.085  # corner pilaster half-section (square post)
_FRIEZE_H = 0.16  # "TELEPHONE" frieze band height
_WALL_T = 0.045  # glazed wall mullion-plane thickness (Y/X of wall web)
_GLASS_T = 0.010  # glazing pane thickness
_BAR_D = 0.024  # mullion / glazing bar face width
_BAR_PROUD = 0.012  # how far bars stand proud of glass plane
_GLASS_INSET = 0.030  # glass plane inset from outer face
_DOOR_GAP = 0.010  # running clearance between door leaf and opening
_LEAF_VGAP = 0.012  # vertical clearance of the leaf from plinth top / frieze

_HANDLE_LEN = 0.16
_HANDLE_R = 0.011

# Outboard-most leaf element edge (the proud glazing bar) measured from the leaf
# glass plane. The hinge axis is placed ON this face so the entire leaf swings
# INBOARD (away from the +X/+Y corner pilaster) instead of sweeping its proud
# material into the pilaster as it opens. Single-sourced (Contract 3c): every
# leaf visual is shifted by ``-_LEAF_OUTBOARD`` and every hinge is offset
# outboard by ``+_LEAF_OUTBOARD`` to keep the closed door flush with the wall.
_LEAF_OUTBOARD = _GLASS_T / 2.0 + _BAR_PROUD + _BAR_D / 2.0

# Bi-fold concertina kinematics. The follower mirrors the driver (Mimic
# multiplier -2) and folds back toward it. Two finite-thickness leaves would
# otherwise concertina flat into the SAME slot (gross body-into-body 穿模,
# ~0.34 m) AND the follower's far tip would wrap back onto the driver's body
# hinge. Two derived guards prevent both, geometrically (no masking):
#   * ``_BIFOLD_FOLD_OFFSET`` staggers the follower INBOARD by one full leaf
#     thickness — frame wall + the proud glazing-bar depth of BOTH facing
#     leaves (``_WALL_T + _LEAF_OUTBOARD``) — so the folded pair stacks in two
#     clear parallel planes like a real knuckle.
#   * ``_BIFOLD_DRIVE_CAP`` limits the fold to a quarter turn so the follower
#     never wraps its far tip back into the driver near the body hinge.
# Only the thin butt-jointed knuckle members then lap (element-scoped allow).
_BIFOLD_FOLD_OFFSET = _WALL_T + _LEAF_OUTBOARD
_BIFOLD_DRIVE_CAP = math.radians(45.0)
_BIFOLD_SEAM_GAP = 0.012
_BIFOLD_MIMIC = -2.0
# The fold axis sits in the staggered gap BETWEEN the two leaf planes (a bifold
# hinge pin is never coplanar with either leaf face). A real knuckle barrel on
# the OUTER leaf reaches inboard from its free stile to the pin line so the fold
# axis passes through genuine outer-leaf hardware instead of floating in the
# seam. The barrel is coaxial with the +Z fold axis → rotation-invariant; it
# only laps the inner leaf's coaxial seam members (declared allow_overlap).
_KNUCKLE_R = 0.016


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _pick(value, choices):
    return value if value in choices else choices[0]


# ===========================================================================
# Config
# ===========================================================================
@dataclass(frozen=True)
class PhoneBoxConfig:
    roof_choice: RoofChoice | None = None
    door_choice: DoorChoice | None = None
    glaze_choice: GlazeChoice | None = None
    foot_choice: FootChoice | None = None
    palette_style: PaletteStyle = "classic_red"
    box_w: float = 0.92
    box_d: float = 0.92
    body_top: float = 2.00
    window_bottom: float = 0.62
    open_angle: float = math.radians(95.0)
    name: str = "phone_box"


@dataclass(frozen=True)
class ResolvedPhoneBoxConfig:
    roof_choice: RoofChoice
    door_choice: DoorChoice
    glaze_choice: GlazeChoice
    foot_choice: FootChoice
    palette_style: PaletteStyle
    # Multiplicity (glazing grid).
    cols: int  # base column count (narrow faces / door)
    rows: int  # row count
    wide_cols: int  # wider-face column count (derived from span)
    # Concrete dims.
    box_w: float
    box_d: float
    body_top: float
    window_bottom: float
    roof_h: float
    open_angle: float
    name: str


_GLAZE_DIMS: dict[GlazeChoice, tuple[int, int]] = {
    "glaze_sparse_2x4": (2, 4),
    "glaze_medium_3x6": (3, 6),
    "glaze_dense_4x8": (4, 8),
}
_ROOF_H: dict[RoofChoice, float] = {
    "roof_domed_k6": 0.36,
    "roof_flat_slab": 0.08,
    "roof_pediment": 0.36,
}


def config_from_seed(seed: int) -> PhoneBoxConfig:
    rng = random.Random(seed)
    # Slot A roof — domed K6 dominant (the iconic form), flat + pediment less so.
    roof: RoofChoice = rng.choices(ROOF_CHOICES, weights=(0.46, 0.27, 0.27), k=1)[0]
    # Slot B door — single hinge dominant, bi-fold + open-side meaningful tails.
    door: DoorChoice = rng.choices(DOOR_CHOICES, weights=(0.50, 0.27, 0.23), k=1)[0]
    # Slot C glazing — small N high frequency (medium + sparse ~70%, dense ~30%).
    glaze: GlazeChoice = rng.choices(GLAZE_CHOICES, weights=(0.34, 0.40, 0.26), k=1)[0]
    # Slot D footprint — square one-person dominant.
    foot: FootChoice = rng.choices(FOOT_CHOICES, weights=(0.66, 0.34), k=1)[0]

    box_w = round(rng.uniform(0.86, 0.98), 4)
    if foot == "foot_wide_2person":
        box_d = round(rng.uniform(1.20, 1.40), 4)
    else:
        box_d = round(rng.uniform(0.86, 0.98), 4)
    body_top = round(rng.uniform(1.95, 2.25), 4)
    window_bottom = round(rng.uniform(0.55, 0.68), 4)
    open_angle = round(rng.uniform(math.radians(85.0), math.radians(105.0)), 5)

    return PhoneBoxConfig(
        roof_choice=roof,
        door_choice=door,
        glaze_choice=glaze,
        foot_choice=foot,
        palette_style=rng.choice(PALETTE_STYLES),
        box_w=box_w,
        box_d=box_d,
        body_top=body_top,
        window_bottom=window_bottom,
        open_angle=open_angle,
        name=f"seeded_phone_box_{seed}",
    )


def resolve_config(config: PhoneBoxConfig | None = None) -> ResolvedPhoneBoxConfig:
    cfg = config or PhoneBoxConfig()
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)
    roof = _pick(cfg.roof_choice, ROOF_CHOICES)
    door = _pick(cfg.door_choice, DOOR_CHOICES)
    glaze = _pick(cfg.glaze_choice, GLAZE_CHOICES)
    foot = _pick(cfg.foot_choice, FOOT_CHOICES)

    cols, rows = _GLAZE_DIMS[glaze]

    # --- Continuous dims with inequality projection. ---
    box_w = _clamp(cfg.box_w, 0.86, 0.98)
    if foot == "foot_wide_2person":
        box_d = _clamp(cfg.box_d, 1.20, 1.40)
    else:
        box_d = _clamp(cfg.box_d, 0.86, 0.98)

    body_top = _clamp(cfg.body_top, 1.95, 2.25)
    # Flat slab compensates with a slightly taller body to keep ~2.4-2.6m total.
    if roof == "roof_flat_slab":
        body_top = _clamp(body_top + 0.18, 1.95, 2.40)

    # window_bottom must leave >= 0.8 m of glazing band below the frieze.
    window_bottom = _clamp(cfg.window_bottom, 0.45, 0.68)
    if window_bottom + 0.8 > body_top - _FRIEZE_H:
        window_bottom = _clamp(body_top - _FRIEZE_H - 0.8, 0.40, window_bottom)

    roof_h = _ROOF_H[roof]
    open_angle = _clamp(cfg.open_angle, math.radians(80.0), math.radians(110.0))

    # Wide-face column count derives from span (wider face -> more columns).
    wide_cols = cols
    if foot == "foot_wide_2person":
        wide_cols = cols + 2  # spec: BACK_COLS up to +2 on the wide face

    return ResolvedPhoneBoxConfig(
        roof_choice=roof,
        door_choice=door,
        glaze_choice=glaze,
        foot_choice=foot,
        palette_style=palette_style,
        cols=cols,
        rows=rows,
        wide_cols=wide_cols,
        box_w=box_w,
        box_d=box_d,
        body_top=body_top,
        window_bottom=window_bottom,
        roof_h=roof_h,
        open_angle=open_angle,
        name=cfg.name or "phone_box",
    )


def with_overrides(config: PhoneBoxConfig, **kwargs: object) -> PhoneBoxConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: PhoneBoxConfig | ResolvedPhoneBoxConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedPhoneBoxConfig) else resolve_config(config)
    return (
        ("roof", r.roof_choice),
        ("door", r.door_choice),
        ("glaze", r.glaze_choice),
        ("foot", r.foot_choice),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ===========================================================================
# Geometry helpers
# ===========================================================================
def _box_solid(w: float, d: float, h: float, center=(0.0, 0.0, 0.0)) -> cq.Workplane:
    """Axis-aligned box centered at ``center``."""
    return cq.Workplane("XY").transformed(offset=center).box(w, d, h)


def _domed_roof_solid(radius: float, height: float) -> cq.Workplane:
    """K6 ogee dome via CadQuery lathe (revolve) — Rule 3, NOT a Box stack.

    Profile drawn on the XY workplane (local x = radius, local y = height),
    revolved 360 about the Y axis, then rotated so the dome axis stands along
    +Z with its base at z=0."""
    eps = max(0.015, radius * 0.04)  # small top-cap radius avoids axis-edge degeneracy
    prof = (
        cq.Workplane("XY")
        .moveTo(eps, height)
        .lineTo(radius * 0.50, height * 0.86)
        .lineTo(radius * 0.85, height * 0.46)
        .lineTo(radius, height * 0.06)
        .lineTo(radius, 0.0)
        .lineTo(eps, 0.0)
        .close()
    )
    sol = prof.revolve(360, (0.0, 0.0, 0.0), (0.0, 1.0, 0.0))
    return sol.rotate((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), 90.0)


def _pediment_prism_mesh(half_w: float, depth: float, rise: float) -> MeshGeometry:
    """Hand-built triangular-prism gable (Rule 3) — ridge runs along Y.

    Base spans X in [-half_w, half_w], Y in [-depth/2, depth/2] at z=0; ridge at
    x=0, z=rise. 6 vertices, 8 faces (2 triangular gables + 2 sloped rects +
    1 base rect)."""
    g = MeshGeometry()
    hw, hd, rz = half_w, depth / 2.0, rise
    # vertices: front gable (y=+hd): 0 left, 1 right, 2 ridge; back (y=-hd): 3,4,5
    v = [
        (-hw, hd, 0.0),  # 0
        (hw, hd, 0.0),  # 1
        (0.0, hd, rz),  # 2
        (-hw, -hd, 0.0),  # 3
        (hw, -hd, 0.0),  # 4
        (0.0, -hd, rz),  # 5
    ]
    idx = [g.add_vertex(*p) for p in v]
    a, b, c, d, e, f = idx
    # front gable triangle, back gable triangle (outward normals)
    g.add_face(a, b, c)
    g.add_face(f, e, d)
    # left slope (a-c-f-d), right slope (b-e-c-f) split into triangles
    g.add_face(a, c, f)
    g.add_face(a, f, d)
    g.add_face(b, e, c)
    g.add_face(c, e, f)
    # base (a-d-e-b)
    g.add_face(a, d, e)
    g.add_face(a, e, b)
    return g


# ===========================================================================
# Glazed mullion grid (loop-emitted multiplicity, Rule 1 parent visuals)
# ===========================================================================
def _emit_glazed_grid(
    part,
    mats,
    *,
    prefix: str,
    cols: int,
    rows: int,
    span: float,
    z0: float,
    z1: float,
    plane_coord: float,
    normal_axis: str,
    bar_proud_sign: float,
) -> None:
    """Loop-emit one glazed mullion grid onto ``part`` as parent visuals.

    The grid lies in a vertical plane. ``span`` runs along the in-plane
    horizontal axis (X for +/-Y walls, Y for +/-X walls). ``plane_coord`` is the
    fixed normal-axis coordinate of the glass plane. Emits 1 glass pane +
    (cols+1) vbars + (rows+1) hbars, named ``{prefix}_glass``,
    ``{prefix}_vbar_{c}``, ``{prefix}_hbar_{r}``."""
    h = z1 - z0
    zc = (z0 + z1) / 2.0
    sc = 0.0  # in-plane horizontal center
    bar_n = plane_coord + bar_proud_sign * (_GLASS_T / 2.0 + _BAR_PROUD)

    def _at(in_plane_h: float, z: float):
        """Map (in-plane horizontal, z) -> world xyz given the wall orientation."""
        if normal_axis == "y":
            return (in_plane_h, plane_coord, z)
        return (plane_coord, in_plane_h, z)

    def _bar_at(in_plane_h: float, z: float):
        if normal_axis == "y":
            return (in_plane_h, bar_n, z)
        return (bar_n, in_plane_h, z)

    def _hsize(sx: float, sz: float):
        """Box size given in-plane horizontal extent sx and vertical sz."""
        if normal_axis == "y":
            return (sx, _GLASS_T, sz)
        return (_GLASS_T, sx, sz)

    def _bar_hsize(sx: float, sz: float):
        if normal_axis == "y":
            return (sx, _BAR_D, sz)
        return (_BAR_D, sx, sz)

    # glass pane
    part.visual(
        Box(_hsize(span, h)),
        origin=Origin(xyz=_at(sc, zc)),
        material=mats["glass"],
        name=f"{prefix}_glass", material_class_id="glass.clear_transparent",
    )
    # vertical bars (cols+1)
    for c in range(cols + 1):
        x = -span / 2.0 + c * (span / cols)
        part.visual(
            Box(_bar_hsize(_BAR_D, h)),
            origin=Origin(xyz=_bar_at(x, zc)),
            material=mats["trim"],
            name=f"{prefix}_vbar_{c}", material_class_id="metal.paint_coated",
        )
    # horizontal bars (rows+1)
    for rr in range(rows + 1):
        z = z0 + rr * (h / rows)
        part.visual(
            Box(_bar_hsize(span, _BAR_D)),
            origin=Origin(xyz=_bar_at(sc, z)),
            material=mats["trim"],
            name=f"{prefix}_hbar_{rr}", material_class_id="metal.paint_coated",
        )


# ===========================================================================
# Body (root) — plinth + pilasters + kick + glazed walls + frieze + roof
# ===========================================================================
def _emit_body(model, r: ResolvedPhoneBoxConfig, mats, *, assets):
    body = model.part("kiosk_body")
    bw, bd = r.box_w, r.box_d
    bt = r.body_top
    wb = r.window_bottom
    door = r.door_choice

    half_w, half_d = bw / 2.0, bd / 2.0
    frieze_bot = bt - _FRIEZE_H

    # --- Plinth (oversized base slab). ---
    pw = bw + 2 * _PLINTH_OVER
    pd = bd + 2 * _PLINTH_OVER
    body.visual(
        mesh_from_cadquery(
            _box_solid(pw, pd, _PLINTH_H, center=(0.0, 0.0, _PLINTH_H / 2.0)),
            "plinth",
            assets=assets,
        ),
        material=mats["trim"],
        name="plinth", material_class_id="metal.paint_coated",
    )

    # --- 4 corner pilasters (square posts running full height). ---
    post_top = bt
    for sx in (-1, 1):
        for sy in (-1, 1):
            cx = sx * (half_w - _POST / 2.0)
            cy = sy * (half_d - _POST / 2.0)
            body.visual(
                mesh_from_cadquery(
                    _box_solid(
                        _POST,
                        _POST,
                        post_top - _PLINTH_H,
                        center=(cx, cy, _PLINTH_H + (post_top - _PLINTH_H) / 2.0),
                    ),
                    f"pilaster_{sx}_{sy}",
                    assets=assets,
                ),
                material=mats["body"],
                name=f"pilaster_{'p' if sx > 0 else 'm'}{'p' if sy > 0 else 'm'}", material_class_id="metal.paint_coated",
            )

    # --- Kick panels + glazed walls on the 3 closed faces. ---
    # Open-side: front (+X) is a walk-in doorway (no kick/glass), the +Y side
    # becomes the moving access panel face (its wall is the panel, not fixed).
    open_side = door == "door_open_side"

    # Helper to build a fixed wall (kick + glazed grid) on one face.
    def _fixed_wall(face: str):
        if face == "+x":
            cols = r.cols
            span = bd - 2 * _POST
            plane = half_w - _GLASS_INSET
            normal, proud = "x", 1.0
            kick_center = (half_w - _WALL_T / 2.0, 0.0, 0.0)
            kick_size = (_WALL_T, span, 0.0)
            prefix = "win_front"
        elif face == "-x":
            cols = r.cols
            span = bd - 2 * _POST
            plane = -(half_w - _GLASS_INSET)
            normal, proud = "x", -1.0
            kick_center = (-(half_w - _WALL_T / 2.0), 0.0, 0.0)
            kick_size = (_WALL_T, span, 0.0)
            prefix = "win_back"
        elif face == "+y":
            cols = r.wide_cols
            span = bw - 2 * _POST
            plane = half_d - _GLASS_INSET
            normal, proud = "y", 1.0
            kick_center = (0.0, half_d - _WALL_T / 2.0, 0.0)
            kick_size = (span, _WALL_T, 0.0)
            prefix = "win_right"
        else:  # -y
            cols = r.wide_cols
            span = bw - 2 * _POST
            plane = -(half_d - _GLASS_INSET)
            normal, proud = "y", -1.0
            kick_center = (0.0, -(half_d - _WALL_T / 2.0), 0.0)
            kick_size = (span, _WALL_T, 0.0)
            prefix = "win_left"

        # kick panel (solid below the glazing band)
        kx, ky, _ = kick_center
        body.visual(
            Box((kick_size[0] or _WALL_T, kick_size[1] or _WALL_T, wb - _PLINTH_H)),
            origin=Origin(xyz=(kx, ky, _PLINTH_H + (wb - _PLINTH_H) / 2.0)),
            material=mats["body"],
            name=f"kick_{prefix}", material_class_id="metal.paint_coated",
        )
        _emit_glazed_grid(
            body,
            mats,
            prefix=prefix,
            cols=cols,
            rows=r.rows,
            span=span,
            z0=wb,
            z1=frieze_bot,
            plane_coord=plane,
            normal_axis=normal,
            bar_proud_sign=proud,
        )

    # back (-X) always fixed
    _fixed_wall("-x")
    if open_side:
        # front +X is open doorway: emit only jamb posts (already covered by
        # pilasters) — no kick/glass. -Y fixed, +Y becomes the moving panel.
        _fixed_wall("-y")
    else:
        # single-hinge / bi-fold: the front (+X) IS the door opening (no fixed
        # wall there); the two side faces stay fixed glazed walls.
        _fixed_wall("+y")
        _fixed_wall("-y")

    # --- Frieze band (4 faces) with "TELEPHONE" accent sign greebles. ---
    for face, (cx, cy, sx, sy, sign) in {
        "+x": (half_w - _WALL_T / 2.0, 0.0, _WALL_T, bd, "x"),
        "-x": (-(half_w - _WALL_T / 2.0), 0.0, _WALL_T, bd, "x"),
        "+y": (0.0, half_d - _WALL_T / 2.0, bw, _WALL_T, "y"),
        "-y": (0.0, -(half_d - _WALL_T / 2.0), bw, _WALL_T, "y"),
    }.items():
        body.visual(
            Box((sx, sy, _FRIEZE_H)),
            origin=Origin(xyz=(cx, cy, frieze_bot + _FRIEZE_H / 2.0)),
            material=mats["body"],
            name=f"frieze_{face}", material_class_id="metal.paint_coated",
        )
        # accent "TELEPHONE" sign plate (cosmetic greeble, not multiplicity)
        if sign == "x":
            plate = (0.012, bd * 0.7, _FRIEZE_H * 0.5)
            px = cx + (1.0 if cx > 0 else -1.0) * (_WALL_T / 2.0 + 0.006)
            porg = (px, 0.0, frieze_bot + _FRIEZE_H / 2.0)
        else:
            plate = (bw * 0.7, 0.012, _FRIEZE_H * 0.5)
            py = cy + (1.0 if cy > 0 else -1.0) * (_WALL_T / 2.0 + 0.006)
            porg = (0.0, py, frieze_bot + _FRIEZE_H / 2.0)
        body.visual(
            Box(plate),
            origin=Origin(xyz=porg),
            material=mats["accent"],
            name=f"signtext_{face}", material_class_id="metal.precious_gold",
        )

    # --- Crown roof (Slot A) sits on the frieze top. ---
    _emit_roof(body, r, mats, roof_base=bt, assets=assets)

    return body, half_w, half_d, frieze_bot


def _emit_roof(body, r: ResolvedPhoneBoxConfig, mats, *, roof_base: float, assets):
    bw, bd = r.box_w, r.box_d
    choice = r.roof_choice
    over = 0.05  # eaves overhang per side

    # cornice slab (shared base under all roof forms)
    cw, cd = bw + 2 * over, bd + 2 * over
    cornice_h = 0.06
    body.visual(
        mesh_from_cadquery(
            _box_solid(cw, cd, cornice_h, center=(0.0, 0.0, roof_base + cornice_h / 2.0)),
            "roof_cornice",
            assets=assets,
        ),
        material=mats["trim"],
        name="roof_cornice", material_class_id="metal.paint_coated",
    )
    top = roof_base + cornice_h

    if choice == "roof_domed_k6":
        radius = max(cw, cd) / 2.0
        dome = _domed_roof_solid(radius, r.roof_h)
        body.visual(
            mesh_from_cadquery(
                dome.translate((0.0, 0.0, top)),
                "roof_dome",
                assets=assets,
                tolerance=0.004,
                angular_tolerance=0.3,
            ),
            material=mats["body"],
            name="roof_dome", material_class_id="metal.paint_coated",
        )
        # gold crown emblem cap
        body.visual(
            Box((0.07, 0.07, 0.05)),
            origin=Origin(xyz=(0.0, 0.0, top + r.roof_h + 0.02)),
            material=mats["accent"],
            name="crown_emblem", material_class_id="metal.precious_gold",
        )
    elif choice == "roof_flat_slab":
        slab_h = r.roof_h
        body.visual(
            mesh_from_cadquery(
                _box_solid(
                    cw + 0.04,
                    cd + 0.04,
                    slab_h,
                    center=(0.0, 0.0, top + slab_h / 2.0),
                ),
                "roof_slab",
                assets=assets,
            ),
            material=mats["body"],
            name="roof_slab", material_class_id="metal.paint_coated",
        )
    else:  # roof_pediment
        half_w = cw / 2.0
        ped = _pediment_prism_mesh(half_w, cd, r.roof_h)
        body.visual(
            mesh_from_geometry(ped, "pediment"),
            origin=Origin(xyz=(0.0, 0.0, top)),
            material=mats["body"],
            name="pediment", material_class_id="metal.paint_coated",
        )
        # ridge cap finials (accent) at both gable ends
        for sy in (-1, 1):
            body.visual(
                Cylinder(radius=0.022, length=0.07),
                origin=Origin(xyz=(0.0, sy * cd / 2.0, top + r.roof_h)),
                material=mats["accent"],
                name=f"gable_finial_{'p' if sy > 0 else 'm'}", material_class_id="metal.precious_gold",
            )


# ===========================================================================
# Door leaf builders (Rule 1 visuals; child of body via REVOLUTE)
# ===========================================================================
def _build_leaf_part(
    model,
    r: ResolvedPhoneBoxConfig,
    mats,
    *,
    name: str,
    leaf_w: float,
    leaf_h: float,
    d_cols: int,
    d_rows: int,
    with_handle: bool,
    assets,
):
    """Build a hinged leaf part authored in a local frame: hinge stile at local
    y=0 (on the +X face the leaf swings about +Z), body extends -Y, z 0..leaf_h.

    The leaf glass plane sits at local x=0; visuals must contain (0,0,0) so the
    chain joint origin (on the hinge) is inside the AABB."""
    leaf = model.part(name)
    # frame ring (perimeter) — slab with center cut, on the X-thin plane.
    # x0 shifts the whole leaf inboard so its OUTBOARD-most element edge lands on
    # the hinge axis (local x=0); the leaf then swings clear of the pilaster.
    x0 = -_LEAF_OUTBOARD
    z0, z1 = 0.0, leaf_h
    # vertical stiles + top/bottom rails as boxes (perimeter frame)
    stile_w = _BAR_D * 1.4
    # hinge stile at y=0, free stile at y=-leaf_w
    for yy, tag in ((0.0, "hinge"), (-leaf_w, "free")):
        leaf.visual(
            Box((_WALL_T, stile_w, leaf_h)),
            origin=Origin(xyz=(x0, yy, leaf_h / 2.0)),
            material=mats["body"],
            name=f"{name}_stile_{tag}", material_class_id="metal.paint_coated",
        )
    for zz, tag in ((z0, "bot"), (z1, "top")):
        leaf.visual(
            Box((_WALL_T, leaf_w, stile_w)),
            origin=Origin(xyz=(x0, -leaf_w / 2.0, zz)),
            material=mats["body"],
            name=f"{name}_rail_{tag}", material_class_id="metal.paint_coated",
        )
    # kick panel (solid lower portion)
    kick_h = r.window_bottom - _PLINTH_H
    leaf.visual(
        Box((_WALL_T, leaf_w, kick_h)),
        origin=Origin(xyz=(x0, -leaf_w / 2.0, kick_h / 2.0)),
        material=mats["body"],
        name=f"{name}_kick", material_class_id="metal.paint_coated",
    )
    # glazed grid (loop-emitted) above the kick
    _emit_glazed_grid_leaf(
        leaf,
        mats,
        name=name,
        cols=d_cols,
        rows=d_rows,
        leaf_w=leaf_w,
        z0=kick_h,
        z1=leaf_h,
        x0=x0,
    )
    if with_handle:
        # Mount the handle ON the free stile so it always has a support contact
        # (embed it slightly into the stile face rather than floating off the
        # glass plane).
        hy = -leaf_w + stile_w / 2.0
        handle_x = x0 + _WALL_T / 2.0 + _HANDLE_R - 0.004
        leaf.visual(
            Cylinder(radius=_HANDLE_R, length=_HANDLE_LEN),
            origin=Origin(xyz=(handle_x, hy, leaf_h * 0.45)),
            material=mats["hardware"],
            name=f"{name}_handle", material_class_id="metal.chrome_polished",
        )
    return leaf


def _emit_glazed_grid_leaf(
    leaf,
    mats,
    *,
    name: str,
    cols: int,
    rows: int,
    leaf_w: float,
    z0: float,
    z1: float,
    x0: float = 0.0,
):
    """Loop-emit the door/leaf glazing in the leaf-local frame (glass plane at
    x=x0, proud bars at x0+bar_x; span along -Y in [-leaf_w, 0]). ``x0`` shifts
    the grid inboard so the proud bar outer edge lands on the hinge axis."""
    h = z1 - z0
    zc = (z0 + z1) / 2.0
    yc = -leaf_w / 2.0
    bar_x = x0 + _GLASS_T / 2.0 + _BAR_PROUD
    # glass
    leaf.visual(
        Box((_GLASS_T, leaf_w, h)),
        origin=Origin(xyz=(x0, yc, zc)),
        material=mats["glass"],
        name=f"{name}_glass", material_class_id="glass.clear_transparent",
    )
    for c in range(cols + 1):
        y = -c * (leaf_w / cols)
        leaf.visual(
            Box((_BAR_D, _BAR_D, h)),
            origin=Origin(xyz=(bar_x, y, zc)),
            material=mats["trim"],
            name=f"{name}_vbar_{c}", material_class_id="metal.paint_coated",
        )
    for rr in range(rows + 1):
        z = z0 + rr * (h / rows)
        leaf.visual(
            Box((_BAR_D, leaf_w, _BAR_D)),
            origin=Origin(xyz=(bar_x, yc, z)),
            material=mats["trim"],
            name=f"{name}_hbar_{rr}", material_class_id="metal.paint_coated",
        )


# ===========================================================================
# Build
# ===========================================================================
def build_phone_box(
    config: PhoneBoxConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        key: model.material(f"phone_box_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in PALETTES[r.palette_style].items()
    }

    body, half_w, half_d, frieze_bot = _emit_body(model, r, mats, assets=assets)

    # --- Slot B: the defining REVOLUTE door / leaves / panel. ---
    if r.door_choice == "door_single_hinge":
        _attach_single_door(model, r, mats, body, half_w, half_d, frieze_bot, assets=assets)
    elif r.door_choice == "door_bifold":
        _attach_bifold(model, r, mats, body, half_w, half_d, frieze_bot, assets=assets)
    else:  # door_open_side
        _attach_open_side_panel(model, r, mats, body, half_w, half_d, frieze_bot, assets=assets)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_phone_box(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_phone_box(config_from_seed(seed), assets=assets)


def _door_span(r: ResolvedPhoneBoxConfig) -> float:
    """Door opening clear width on the front (+X) face along Y."""
    return r.box_d - 2 * _POST - 2 * _DOOR_GAP


def _attach_single_door(model, r, mats, body, half_w, half_d, frieze_bot, *, assets):
    leaf_w = _door_span(r)
    leaf_h = frieze_bot - _PLINTH_H - 2 * _LEAF_VGAP
    leaf = _build_leaf_part(
        model,
        r,
        mats,
        name="door",
        leaf_w=leaf_w,
        leaf_h=leaf_h,
        d_cols=r.cols,
        d_rows=max(1, r.rows - 1),
        with_handle=True,
        assets=assets,
    )
    # Hinge at the +Y front corner. The axis is offset OUTBOARD by _LEAF_OUTBOARD
    # so it passes through the leaf's outboard face: the leaf then swings inboard
    # (-X) and never sweeps its proud material into the +Y corner pilaster. This
    # also lands the closed door's outer bars flush with the wall glazing plane.
    hinge_x = half_w - _GLASS_INSET + _LEAF_OUTBOARD
    hinge_y = half_d - _POST - _DOOR_GAP
    model.articulation(
        "body_to_door",
        ArticulationType.REVOLUTE,
        parent=body,
        child=leaf,
        origin=Origin(xyz=(hinge_x, hinge_y, _PLINTH_H + _LEAF_VGAP)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=20.0, velocity=1.5, lower=0.0, upper=r.open_angle),
    )


def _attach_bifold(model, r, mats, body, half_w, half_d, frieze_bot, *, assets):
    span = _door_span(r)
    seam_gap = _BIFOLD_SEAM_GAP  # reveal between the two leaves at the V-fold
    leaf_w = (span - seam_gap) / 2.0
    leaf_h = frieze_bot - _PLINTH_H - 2 * _LEAF_VGAP
    d_cols = max(1, r.cols - 1)
    fold_offset = _BIFOLD_FOLD_OFFSET
    drive_angle = min(r.open_angle, _BIFOLD_DRIVE_CAP)
    outer = _build_leaf_part(
        model,
        r,
        mats,
        name="outer_leaf",
        leaf_w=leaf_w,
        leaf_h=leaf_h,
        d_cols=d_cols,
        d_rows=max(1, r.rows - 1),
        with_handle=False,
        assets=assets,
    )
    inner = _build_leaf_part(
        model,
        r,
        mats,
        name="inner_leaf",
        leaf_w=leaf_w,
        leaf_h=leaf_h,
        d_cols=d_cols,
        d_rows=max(1, r.rows - 1),
        with_handle=True,
        assets=assets,
    )
    # Knuckle strap on the OUTER leaf, single-sourced to the fold pin. ``ax``/
    # ``ay`` are the SAME coordinates fed to the ``outer_to_inner_leaf`` origin
    # below, so the fold axis lands on real outer-leaf hardware by construction
    # (its inboard face IS the pin line). The strap stays OUTBOARD of the pin
    # (x >= ax), so it only coplanar-abuts the inner leaf's outboard face
    # (which lands exactly on the pin) instead of penetrating the bar grid.
    ax = -fold_offset
    ay = -(leaf_w + seam_gap)
    free_stile_inboard_x = -_LEAF_OUTBOARD - _WALL_T / 2.0
    strap_x_hi = free_stile_inboard_x + 0.008  # bite into the free stile
    strap_x_lo = ax  # inboard face on the pin line
    outer.visual(
        Box((strap_x_hi - strap_x_lo, _KNUCKLE_R * 2.0, leaf_h)),
        origin=Origin(xyz=(0.5 * (strap_x_lo + strap_x_hi), ay, leaf_h / 2.0)),
        material=mats["hardware"],
        name="outer_leaf_knuckle_web", material_class_id="metal.stainless_matte",
    )
    hinge_x = half_w - _GLASS_INSET + _LEAF_OUTBOARD
    hinge_y = half_d - _POST - _DOOR_GAP
    model.articulation(
        "body_to_outer_leaf",
        ArticulationType.REVOLUTE,
        parent=body,
        child=outer,
        origin=Origin(xyz=(hinge_x, hinge_y, _PLINTH_H + _LEAF_VGAP)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=20.0, velocity=1.5, lower=0.0, upper=drive_angle),
    )
    # Follower leaf hinges at the outer leaf's free edge (local y=-leaf_w),
    # mirroring the driver via Mimic so the pair V-folds and lies flush at q=0.
    model.articulation(
        "outer_to_inner_leaf",
        ArticulationType.REVOLUTE,
        parent=outer,
        child=inner,
        origin=Origin(xyz=(ax, ay, 0.0)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(
            effort=20.0,
            velocity=1.5,
            lower=min(0.0, _BIFOLD_MIMIC * drive_angle),
            upper=max(0.0, _BIFOLD_MIMIC * drive_angle),
        ),
        mimic=Mimic(joint="body_to_outer_leaf", multiplier=_BIFOLD_MIMIC),
    )


def _attach_open_side_panel(model, r, mats, body, half_w, half_d, frieze_bot, *, assets):
    # Access panel on the +Y side; hinge at the -X back edge, leaf swings to +X,
    # opening faces +Y.
    leaf_w = r.box_w - 2 * _POST - 2 * _DOOR_GAP
    leaf_h = frieze_bot - _PLINTH_H - 2 * _LEAF_VGAP
    panel = _build_leaf_part(
        model,
        r,
        mats,
        name="access_panel",
        leaf_w=leaf_w,
        leaf_h=leaf_h,
        d_cols=r.cols,
        d_rows=max(1, r.rows - 1),
        with_handle=True,
        assets=assets,
    )
    # Rotate the leaf-local frame so its X-thin plane lies on the +Y face: the
    # leaf was authored in the +X-face frame (glass plane normal +X, body -Y).
    # We mount it via a joint whose child frame is rotated +90 about Z so the
    # leaf's -Y body axis -> +X world and its +X normal -> +Y world.
    # Panel outboard normal is +Y (after the +90 Z child rotation the leaf's
    # local +X maps to world +Y). Offset the hinge OUTBOARD in +Y by
    # _LEAF_OUTBOARD so the panel swings inboard (-Y) and clears the +Y corner
    # pilaster, symmetric with the front door.
    hinge_x = -(half_w - _POST - _DOOR_GAP)
    hinge_y = half_d - _GLASS_INSET + _LEAF_OUTBOARD
    model.articulation(
        "body_to_panel",
        ArticulationType.REVOLUTE,
        parent=body,
        child=panel,
        origin=Origin(
            xyz=(hinge_x, hinge_y, _PLINTH_H + _LEAF_VGAP), rpy=(0.0, 0.0, math.pi / 2.0)
        ),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=20.0, velocity=1.5, lower=0.0, upper=r.open_angle),
    )


# ===========================================================================
# Tests / allowances
# ===========================================================================
def run_phone_box_tests(model: ArticulatedObject, config) -> TestReport:
    r = config if isinstance(config, ResolvedPhoneBoxConfig) else resolve_config(config)
    ctx = TestContext(model)

    # The hinge stile AND the free stile of every moving leaf lap ONLY the two
    # corner pilasters on that leaf's own face (the leaf is captured between
    # them). Scoping to the face pilasters — not all four — keeps a stray lap on
    # a far pilaster (a genuine 穿模) catchable instead of blanket-allowed. The
    # rails / kick / glass / bars are NOT allowed: the outboard-face hinge makes
    # them swing clear of the pilaster by construction.
    leaf_names = {
        "door_single_hinge": ["door"],
        "door_bifold": ["outer_leaf", "inner_leaf"],
        "door_open_side": ["access_panel"],
    }[r.door_choice]
    # Front (+X) door/leaves are captured between the two +X pilasters (pp, pm);
    # the +Y access panel between the two +Y pilasters (pp, mp).
    face_pilasters = ("pp", "mp") if r.door_choice == "door_open_side" else ("pp", "pm")
    for leaf_name in leaf_names:
        for stile in (f"{leaf_name}_stile_hinge", f"{leaf_name}_stile_free"):
            for sx in face_pilasters:
                ctx.allow_overlap(
                    "kiosk_body",
                    leaf_name,
                    elem_a=f"pilaster_{sx}",
                    elem_b=stile,
                    reason="door leaf stile laps the corner pilaster (captured hinge / jamb)",
                )

    if r.door_choice == "door_bifold":
        # The fold joint between the two leaves is a captured hinge: the seam
        # members of the inner leaf's HINGE edge (hinge stile + first vbar +
        # kick) lap the seam members of the outer leaf's FREE edge (free stile +
        # last vbar + kick) at the V-fold knuckle. ``_BIFOLD_FOLD_OFFSET`` (leaf
        # stagger) + ``_BIFOLD_DRIVE_CAP`` (partial fold) keep the two leaf
        # BODIES from concertina-ing into the same slot, so only these butt
        # jointed knuckle members lap — element-scoped captured hardware, not a
        # blanket part-pair allow that would mask a body-into-body 穿模.
        d_cols = max(1, r.cols - 1)
        outer_seam = [
            "outer_leaf_stile_free",
            f"outer_leaf_vbar_{d_cols}",
            "outer_leaf_kick",
            "outer_leaf_knuckle_web",
        ]
        inner_seam = [
            "inner_leaf_stile_hinge",
            "inner_leaf_vbar_0",
            "inner_leaf_kick",
        ]
        for ea in outer_seam:
            for eb in inner_seam:
                ctx.allow_overlap(
                    "outer_leaf",
                    "inner_leaf",
                    elem_a=ea,
                    elem_b=eb,
                    reason="bi-fold fold-joint captured hinge seam between leaves",
                )

        # As the pair folds, the inner leaf's outboard frame bars (rails +
        # horizontal muntins) sweep across the outer leaf's knuckle strap that
        # bridges its free stile to the fold pin — a captured-hinge lap on the
        # thin strap only. Scoped to the strap and to frame bars (glass and the
        # off-seam muntins stay unmasked so a leaf-into-leaf 穿模 is still caught).
        inner_bars = ["inner_leaf_rail_bot", "inner_leaf_rail_top"] + [
            f"inner_leaf_hbar_{rr}" for rr in range(max(1, r.rows - 1) + 1)
        ]
        for eb in inner_bars:
            ctx.allow_overlap(
                "outer_leaf",
                "inner_leaf",
                elem_a="outer_leaf_knuckle_web",
                elem_b=eb,
                reason="inner-leaf frame bar laps the outer knuckle strap during the fold (captured hinge)",
            )

        # Anti-phantom guard: the fold axis must pass through real outer-leaf
        # hardware (the knuckle strap), never float in the staggered seam gap.
        fold = model.get_articulation("outer_to_inner_leaf")
        fax, fay = float(fold.origin.xyz[0]), float(fold.origin.xyz[1])
        outer_part = model.get_part("outer_leaf")
        axis_on_hw = False
        for v in outer_part.visuals:
            geom = v.geometry
            vx, vy = float(v.origin.xyz[0]), float(v.origin.xyz[1])
            size = getattr(geom, "size", None)
            radius = getattr(geom, "radius", None)
            if size is not None and len(size) == 3:
                if (
                    abs(fax - vx) <= float(size[0]) * 0.5 + 0.015
                    and abs(fay - vy) <= float(size[1]) * 0.5 + 0.015
                ):
                    axis_on_hw = True
                    break
            elif radius is not None:
                if ((fax - vx) ** 2 + (fay - vy) ** 2) ** 0.5 <= float(radius) + 0.015:
                    axis_on_hw = True
                    break
        ctx.check(
            "fold_axis_on_outer_leaf_hardware",
            axis_on_hw,
            details=f"fold axis=({fax:.3f},{fay:.3f})",
        )

    return ctx.report()
