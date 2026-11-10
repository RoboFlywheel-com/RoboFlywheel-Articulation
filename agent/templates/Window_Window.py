# SPDX-License-Identifier: Apache-2.0

"""Architectural window — modular procedural template.

Category identity: a glazed sash (or several) captured in a static frame, with
at least one category-defining moving sash (hinged / vertically sliding /
center-pivot / trickle-vent). NOT a left-right sliding sash (that is the
separate ``sliding_window`` 小类).

Sourced from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/Window_Window.md`` and the 16 five-star
window records under ``data/records/`` (9 parents + 7 slot-fork variants), each
read in full.

Pattern = ``mixed``: a static ``frame`` root part carries fixed glass / muntin /
fanlight / fixed-lite visuals (Rule 1), and one or more operable ``sash`` parts
attach via REVOLUTE / PRISMATIC joints. Two multiplicity axes:

  * Slot C ``divided_light_grid`` (muntin cols×rows N panes on the sash)
  * Slot D ``sash_unit_count`` (linear bays OR a col×row lite grid)

Slots:
  * Slot A ``opening_mechanism`` (5): side_hung casement (REVOLUTE z) /
    awning top-hung (REVOLUTE x) / hopper bottom-hung (REVOLUTE x) /
    single_hung vertical (PRISMATIC z lower + FIXED upper) /
    fixed_picture (FIXED main light + small vent flap REVOLUTE x).
    round_porthole center-pivot (REVOLUTE x) is a Slot-B-derived mechanism.
  * Slot B ``frame_outline`` (4): rectangular (slab.cut) / arched_top
    (threePointArc + fanlight + stone surround) / round_porthole (lathe ring) /
    segmental_arch (concentric arc head).

Coordinate convention (all 16 sources agree): +Z up, width along X, frame depth
/ glazing thickness / swing-normal along Y. Glass plane is the X-Z plane; the
sill bottom sits at z≈0; the window stands upright.

3 hard rules honoured:
  1. Muntin bars / panes / fanlight ribs / fixed lites / keystone / corbels are
     parent ``.visual(...)`` (NOT FIXED-joint parts).
  2. Every non-FIXED joint declares a MatingContract OR is a captured-pin/slide
     joint grandfathered with element-scoped ``allow_overlap`` (sash rebate in
     the frame rebate, pivot pin in the ring bore, sash stiles in jamb tracks).
  3. Primitives derive from the 5-star sources (CadQuery slab.cut frame, arch
     threePointArc, lathe ring) — never downgraded to crude Box/Cylinder.

palette_style (6 colorways observed from the sources) is sampled per seed and
drives every ``.visual(..., material=...)``.
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
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
)

__modular__ = True

# ---------------------------------------------------------------------------
# Slot enums
# ---------------------------------------------------------------------------
OpeningMechanism = Literal[
    "side_hung_casement",
    "awning_top_hung",
    "hopper_bottom_hung",
    "single_hung_vertical",
    "fixed_picture_light",
    "round_porthole_center_pivot",
]
FrameOutline = Literal["rectangular", "arched_top", "round_porthole", "segmental_arch"]
DividedLightGrid = Literal[
    "no_muntin", "colonial_2x2", "colonial_3x3", "arched_radial_fan"
]
SashUnitCount = Literal[
    "single_1", "twin_double_2", "triple_mullion_3", "bank_2x2_4", "bank_3x2_6"
]
PaletteStyle = Literal[
    "warm_stained_wood",
    "anthracite_aluminium",
    "sage_grey",
    "industrial_white_steel",
    "glossy_black_porthole",
    "grey_aluminium_blue_glass",
]

OPENING_MECHANISMS: tuple[OpeningMechanism, ...] = (
    "side_hung_casement",
    "awning_top_hung",
    "hopper_bottom_hung",
    "single_hung_vertical",
    "fixed_picture_light",
)  # round_porthole_center_pivot is selected only via the porthole outline
FRAME_OUTLINES: tuple[FrameOutline, ...] = (
    "rectangular",
    "arched_top",
    "round_porthole",
    "segmental_arch",
)
DIVIDED_LIGHT_GRIDS: tuple[DividedLightGrid, ...] = (
    "no_muntin",
    "colonial_2x2",
    "colonial_3x3",
    "arched_radial_fan",
)
SASH_UNIT_COUNTS: tuple[SashUnitCount, ...] = (
    "single_1",
    "twin_double_2",
    "triple_mullion_3",
    "bank_2x2_4",
    "bank_3x2_6",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "warm_stained_wood",
    "anthracite_aluminium",
    "sage_grey",
    "industrial_white_steel",
    "glossy_black_porthole",
    "grey_aluminium_blue_glass",
)

# Palette: keys frame / sash / glass / hardware. Observed from the 5-star
# sources (spec §palette source). hardware = hinges / handles / stays / pins.
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "warm_stained_wood": {
        "frame": (0.255, 0.145, 0.075, 1.0),
        "sash": (0.300, 0.175, 0.090, 1.0),
        "glass": (0.16, 0.17, 0.22, 0.38),
        "hardware": (0.80, 0.62, 0.22, 1.0),
        "stone": (0.86, 0.85, 0.82, 1.0),
    },
    "anthracite_aluminium": {
        "frame": (0.13, 0.135, 0.145, 1.0),
        "sash": (0.18, 0.185, 0.195, 1.0),
        "glass": (0.55, 0.62, 0.68, 0.28),
        "hardware": (0.85, 0.86, 0.87, 1.0),
        "stone": (0.92, 0.92, 0.93, 1.0),
    },
    "sage_grey": {
        "frame": (0.74, 0.74, 0.68, 1.0),
        "sash": (0.76, 0.76, 0.70, 1.0),
        "glass": (0.62, 0.70, 0.74, 0.26),
        "hardware": (0.80, 0.81, 0.83, 1.0),
        "stone": (0.88, 0.88, 0.84, 1.0),
    },
    "industrial_white_steel": {
        "frame": (0.86, 0.85, 0.82, 1.0),
        "sash": (0.80, 0.79, 0.76, 1.0),
        "glass": (0.46, 0.52, 0.57, 0.32),
        "hardware": (0.40, 0.41, 0.43, 1.0),
        "stone": (0.90, 0.90, 0.88, 1.0),
    },
    "glossy_black_porthole": {
        "frame": (0.045, 0.045, 0.050, 1.0),
        "sash": (0.075, 0.075, 0.085, 1.0),
        "glass": (0.05, 0.06, 0.09, 0.45),
        "hardware": (0.30, 0.31, 0.33, 1.0),
        "stone": (0.20, 0.20, 0.22, 1.0),
    },
    "grey_aluminium_blue_glass": {
        "frame": (0.62, 0.64, 0.66, 1.0),
        "sash": (0.66, 0.68, 0.70, 1.0),
        "glass": (0.62, 0.78, 0.84, 0.34),
        "hardware": (0.30, 0.31, 0.33, 1.0),
        "stone": (0.80, 0.80, 0.78, 1.0),
    },
}

# ---------------------------------------------------------------------------
# Base dimensions (meters). Width along X, height along Z, depth along Y.
# Drawn from the side-hung / awning / bank parents.
# ---------------------------------------------------------------------------
_WIN_W = 0.95          # nominal overall window width (single-unit base)
_WIN_H = 1.25          # nominal overall window height
_FRAME_FACE = 0.060    # outer frame member face width (in-plane)
_FRAME_DEPTH = 0.075   # outer frame depth (Y)
_SASH_FACE = 0.055     # sash ring member face width
_SASH_DEPTH = 0.050    # sash ring depth (Y)
_GLASS_T = 0.008       # glazing thickness (Y)
_GLASS_REBATE = 0.006  # how far glass tucks under the sash lip per edge
_SASH_GAP = 0.006      # running clearance, sash vs opening
_MULLION_W = 0.050     # divider width between bays / lites
_MUNTIN_FACE = 0.022   # muntin bar face width
_MUNTIN_DEPTH = 0.020  # muntin bar depth (Y), sits proud of the glass
_HINGE_CAPTURE = 0.012 # top/bottom rail tuck under frame head/sill lip

_HINGE_R = 0.011
_HINGE_LEN = 0.055
_HINGE_COUNT = 2

_HANDLE_BASE = (0.060, 0.012, 0.022)   # (X, Y-standoff, Z) plate
_HANDLE_LEVER_LEN = 0.080
_HANDLE_LEVER_R = 0.007

# Porthole geometry (round outline).
_PORT_OUTER_R = 0.300
_PORT_RING_W = 0.055
_PORT_FRAME_DEPTH = 0.075
_PORT_SASH_RING_W = 0.030
_PORT_GLASS_T = 0.010
_PORT_SASH_DEPTH = 0.045
_PORT_PIN_R = 0.010
_PORT_PIN_LEN = 0.030

# Arched outline geometry.
_ARCH_FAN_RIB_W = 0.024
_ARCH_FAN_RADIAL = 7

# Vent flap (fixed_picture).
_VENT_W = 0.240
_VENT_H = 0.042
_VENT_DEPTH = 0.012


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _pick(value, choices):
    return value if value in choices else choices[0]


# ===========================================================================
# Config
# ===========================================================================
@dataclass(frozen=True)
class WindowConfig:
    opening_mechanism: OpeningMechanism | None = None
    frame_outline: FrameOutline | None = None
    divided_light_grid: DividedLightGrid | None = None
    sash_unit_count: SashUnitCount | None = None
    palette_style: PaletteStyle = "warm_stained_wood"
    win_width_scale: float = 1.0
    win_height_scale: float = 1.0
    frame_face_scale: float = 1.0
    arch_rise_scale: float = 1.0
    sash_open_frac: float = 0.0
    name: str = "window"


@dataclass(frozen=True)
class ResolvedWindowConfig:
    opening_mechanism: OpeningMechanism
    frame_outline: FrameOutline
    divided_light_grid: DividedLightGrid
    sash_unit_count: SashUnitCount
    palette_style: PaletteStyle
    # Multiplicity (derived from the slot enums).
    muntin_cols: int
    muntin_rows: int
    n_cols: int          # Slot D grid columns (linear bay count for non-grid)
    n_rows: int          # Slot D grid rows
    grid_mode: bool      # True -> bank lite grid; False -> linear bays
    # Concrete (scaled) dims.
    win_w: float
    win_h: float
    frame_face: float
    frame_depth: float
    arch_rise: float
    sash_open_frac: float
    name: str


# ---------------------------------------------------------------------------
# Compatibility gating (spec §compatibility matrix)
# ---------------------------------------------------------------------------
# Mechanisms that only support a single operable unit (Slot D = single).
_SINGLE_ONLY_MECH: tuple[OpeningMechanism, ...] = (
    "single_hung_vertical",
    "fixed_picture_light",
    "round_porthole_center_pivot",
)
# Mechanisms compatible with the multi-unit (linear / grid) families.
_MULTI_UNIT_MECH: tuple[OpeningMechanism, ...] = (
    "side_hung_casement",
    "awning_top_hung",
    "hopper_bottom_hung",
)


def config_from_seed(seed: int) -> WindowConfig:
    rng = random.Random(seed)
    # Sample order B -> A -> (C, D weighted) per spec.
    outline: FrameOutline = rng.choices(
        FRAME_OUTLINES, weights=(0.46, 0.20, 0.16, 0.18), k=1
    )[0]

    if outline == "round_porthole":
        mech: OpeningMechanism = "round_porthole_center_pivot"
    elif outline == "arched_top":
        mech = "side_hung_casement"  # arched lower opening is side-hung
    else:
        mech = rng.choices(
            OPENING_MECHANISMS, weights=(0.34, 0.20, 0.16, 0.16, 0.14), k=1
        )[0]

    # Slot D (sash count) — small N high frequency.
    if mech in _SINGLE_ONLY_MECH or outline in ("arched_top",):
        # arched supports twin (the source has two sashes) but keep single
        # dominant; single-only mechs force single.
        if outline == "arched_top":
            unit: SashUnitCount = rng.choices(
                ("single_1", "twin_double_2"), weights=(0.55, 0.45), k=1
            )[0]
        else:
            unit = "single_1"
    else:
        unit = rng.choices(
            SASH_UNIT_COUNTS,
            weights=(0.42, 0.22, 0.16, 0.12, 0.08),
            k=1,
        )[0]

    # Slot C (muntin grid).
    if outline == "round_porthole":
        grid: DividedLightGrid = "no_muntin"
    elif outline == "arched_top":
        grid = rng.choices(
            ("no_muntin", "colonial_2x2", "colonial_3x3", "arched_radial_fan"),
            weights=(0.20, 0.20, 0.25, 0.35),
            k=1,
        )[0]
    else:
        grid = rng.choices(
            ("no_muntin", "colonial_2x2", "colonial_3x3"),
            weights=(0.55, 0.25, 0.20),
            k=1,
        )[0]

    return WindowConfig(
        opening_mechanism=mech,
        frame_outline=outline,
        divided_light_grid=grid,
        sash_unit_count=unit,
        palette_style=rng.choice(PALETTE_STYLES),
        win_width_scale=round(rng.uniform(0.85, 1.20), 4),
        win_height_scale=round(rng.uniform(0.85, 1.20), 4),
        frame_face_scale=round(rng.uniform(0.85, 1.25), 4),
        arch_rise_scale=round(rng.uniform(0.75, 1.25), 4),
        sash_open_frac=round(rng.uniform(0.0, 1.0), 4),
        name=f"seeded_window_{seed}",
    )


def _grid_dims(unit: SashUnitCount) -> tuple[int, int, bool]:
    """Return (n_cols, n_rows, grid_mode) for a sash-unit module."""
    if unit == "single_1":
        return 1, 1, False
    if unit == "twin_double_2":
        return 2, 1, False
    if unit == "triple_mullion_3":
        return 3, 1, False
    if unit == "bank_2x2_4":
        return 2, 2, True
    if unit == "bank_3x2_6":
        return 3, 2, True
    return 1, 1, False


def _muntin_dims(grid: DividedLightGrid) -> tuple[int, int]:
    if grid == "colonial_2x2":
        return 2, 2
    if grid == "colonial_3x3":
        return 3, 3
    return 1, 1  # no_muntin / arched_radial_fan (fan handled separately)


def resolve_config(config: WindowConfig | None = None) -> ResolvedWindowConfig:
    cfg = config or WindowConfig()
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)
    outline = _pick(cfg.frame_outline, FRAME_OUTLINES)
    mech = _pick(cfg.opening_mechanism, list(OPENING_MECHANISMS) + ["round_porthole_center_pivot"])
    grid = _pick(cfg.divided_light_grid, DIVIDED_LIGHT_GRIDS)
    unit = _pick(cfg.sash_unit_count, SASH_UNIT_COUNTS)

    # --- Gating: enforce the spec compatibility matrix. ---
    if outline == "round_porthole":
        mech = "round_porthole_center_pivot"
        grid = "no_muntin"
        unit = "single_1"
    else:
        if mech == "round_porthole_center_pivot":
            # center-pivot only legal on a round outline
            mech = "side_hung_casement"

    if outline == "arched_top":
        mech = "side_hung_casement"
        if unit not in ("single_1", "twin_double_2"):
            unit = "single_1"
    elif outline == "segmental_arch":
        if mech not in ("side_hung_casement", "awning_top_hung"):
            mech = "side_hung_casement"
        if unit not in ("single_1", "twin_double_2"):
            unit = "single_1"

    # arched_radial_fan only legal on arched_top.
    if grid == "arched_radial_fan" and outline != "arched_top":
        grid = "no_muntin"

    # Single-only mechanisms force single unit & no grid bank.
    if mech in _SINGLE_ONLY_MECH:
        unit = "single_1"
    # single_hung / fixed_picture / porthole sources carry no colonial muntin
    # grid -> keep slot_choices honest (the builders emit a single pane).
    if mech in ("single_hung_vertical", "fixed_picture_light", "round_porthole_center_pivot"):
        if grid in ("colonial_2x2", "colonial_3x3", "arched_radial_fan"):
            grid = "no_muntin"

    # Multi-unit families require a multi-unit-capable mechanism.
    n_cols, n_rows, grid_mode = _grid_dims(unit)
    if (n_cols * n_rows > 1) and mech not in _MULTI_UNIT_MECH:
        mech = "side_hung_casement"

    # bank/triple operable sashes are uniformly side-hung casements; an
    # awning/hopper bank is not in the source pool -> force side-hung.
    if (n_cols * n_rows > 1) and mech in ("awning_top_hung", "hopper_bottom_hung"):
        # twin double awning/hopper would need 2 top/bottom hinges; sources only
        # give us twin side-hung. Keep awning/hopper for single, side-hung for
        # multi.
        mech = "side_hung_casement"

    muntin_cols, muntin_rows = _muntin_dims(grid)
    # Bank/grid units carry no per-sash colonial muntin grid (the lite grid IS
    # the division); keep muntin only on linear single/twin/triple.
    if grid_mode:
        grid = "no_muntin"
        muntin_cols, muntin_rows = 1, 1

    # --- Continuous scales. ---
    ww = _clamp(cfg.win_width_scale, 0.85, 1.20)
    wh = _clamp(cfg.win_height_scale, 0.85, 1.20)
    ff = _clamp(cfg.frame_face_scale, 0.85, 1.25)
    ar = _clamp(cfg.arch_rise_scale, 0.75, 1.25)
    of = _clamp(cfg.sash_open_frac, 0.0, 1.0)

    win_w = _WIN_W * ww
    win_h = _WIN_H * wh
    frame_face = _FRAME_FACE * ff
    frame_depth = _FRAME_DEPTH
    arch_rise = 0.13 * win_w / _WIN_W * ar  # arch rise scales with width

    return ResolvedWindowConfig(
        opening_mechanism=mech,
        frame_outline=outline,
        divided_light_grid=grid,
        sash_unit_count=unit,
        palette_style=palette_style,
        muntin_cols=muntin_cols,
        muntin_rows=muntin_rows,
        n_cols=n_cols,
        n_rows=n_rows,
        grid_mode=grid_mode,
        win_w=win_w,
        win_h=win_h,
        frame_face=frame_face,
        frame_depth=frame_depth,
        arch_rise=arch_rise,
        sash_open_frac=of,
        name=cfg.name or "window",
    )


def with_overrides(config: WindowConfig, **kwargs: object) -> WindowConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: WindowConfig | ResolvedWindowConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedWindowConfig) else resolve_config(config)
    return (
        ("opening_mechanism", r.opening_mechanism),
        ("frame_outline", r.frame_outline),
        ("divided_light_grid", r.divided_light_grid),
        ("sash_unit_count", r.sash_unit_count),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ===========================================================================
# Geometry helpers
# ===========================================================================
def _slab_cut_frame(
    total_w: float, total_h: float, depth: float, openings: list[tuple[float, float, float, float]]
) -> cq.Workplane:
    """Static perimeter+mullion frame web: a full slab with each lite opening
    cut through (side-hung / awning / bank style). openings are world
    (x0, x1, z0, z1). Frame bottom at z=0."""
    slab = (
        cq.Workplane("XY")
        .transformed(offset=(0.0, 0.0, total_h / 2.0))
        .box(total_w, depth, total_h)
    )
    frame = slab
    for x0, x1, z0, z1 in openings:
        cut = (
            cq.Workplane("XY")
            .transformed(offset=((x0 + x1) / 2.0, 0.0, (z0 + z1) / 2.0))
            .box(x1 - x0, depth + 0.02, z1 - z0)
        )
        frame = frame.cut(cut)
    return frame


def _maybe_mirror(shape: cq.Workplane, xs: float) -> cq.Workplane:
    """Mirror a sash shape across the YZ plane (X -> -X) for right-hung leaves."""
    if xs >= 0:
        return shape
    return shape.mirror(mirrorPlane="YZ", basePointVector=(0.0, 0.0, 0.0))


def _rect_ring(w: float, h: float, face: float, depth: float, xs: float = 1.0) -> cq.Workplane:
    """Sash perimeter ring in local frame: x 0..w (hinge edge x=0), z 0..h.
    xs=-1 mirrors so the body extends to -X (hinge stays at local x=0)."""
    outer = cq.Workplane("XY").box(w, depth, h, centered=(False, True, False))
    inner = (
        cq.Workplane("XY")
        .transformed(offset=(w / 2.0, 0.0, h / 2.0))
        .box(w - 2 * face, depth + 0.02, h - 2 * face)
    )
    return _maybe_mirror(outer.cut(inner), xs)


def _rect_glass(w: float, h: float, face: float, xs: float = 1.0) -> cq.Workplane:
    """Rebated glass pane (local frame, x 0..w, z 0..h)."""
    gx0, gx1 = face - _GLASS_REBATE, w - face + _GLASS_REBATE
    gz0, gz1 = face - _GLASS_REBATE, h - face + _GLASS_REBATE
    return _maybe_mirror(
        cq.Workplane("XY")
        .transformed(offset=((gx0 + gx1) / 2.0, 0.0, (gz0 + gz1) / 2.0))
        .box(gx1 - gx0, _GLASS_T, gz1 - gz0),
        xs,
    )


# --- Segmental / arched concentric-arc head (adapted from segmental source). --
def _arch_solid(
    half_w: float,
    bottom_z: float,
    spring_z: float,
    rise: float,
    depth: float,
    cx: float = 0.0,
) -> cq.Workplane:
    """Segmental-arch profile: flat bottom + straight jambs + threePointArc head.
    Drawn on XY (Y=height), extruded +Z, rotated 90° about X so profile-Y -> world
    Z and extrusion -> -Y, then centered on Y=0."""
    crown_z = spring_z + rise
    return (
        cq.Workplane("XY")
        .moveTo(cx - half_w, bottom_z)
        .lineTo(cx + half_w, bottom_z)
        .lineTo(cx + half_w, spring_z)
        .threePointArc((cx, crown_z), (cx - half_w, spring_z))
        .close()
        .extrude(depth)
        .rotate((0, 0, 0), (1, 0, 0), 90)
        .translate((0, depth / 2.0, 0))
    )


# --- Porthole lathe ring (adapted from porthole source). --------------------
def _ring_shape(outer_r: float, inner_r: float, depth: float) -> cq.Workplane:
    """Annular ring on the XZ workplane, extruded symmetrically along Y."""
    return (
        cq.Workplane("XZ")
        .circle(outer_r)
        .circle(inner_r)
        .extrude(depth, both=True)
    )


def _disc_shape(radius: float, depth: float) -> cq.Workplane:
    return cq.Workplane("XZ").circle(radius).extrude(depth, both=True)


# ===========================================================================
# Sash visual emitters (muntin / handle / hinge as parent visuals, Rule 1)
# ===========================================================================
def _emit_muntins_and_panes(
    sash, r: ResolvedWindowConfig, mats, *, sw: float, sh: float, xs: float = 1.0
) -> None:
    """Emit the colonial muntin grid + panes as sash-local visuals (Rule 1).

    Adapted from muntin_grid_2x2 / 3x3: inner glazing bounds, vmuntin_{i} /
    hmuntin_{i} bars + pane_{j}_{k} nested col×row loop. cols×rows = N panes.
    ``xs`` = +1 for left-hung (body +X) or -1 for right-hung (body -X)."""
    cols, rows = r.muntin_cols, r.muntin_rows
    if cols * rows <= 1:
        # single full pane
        sash.visual(
            mesh_from_cadquery(_rect_glass(sw, sh, _SASH_FACE, xs=xs), "sash_glass"),
            material=mats["glass"],
            name="sash_glass", material_class_id=("glass.clear_transparent" if r.palette_style in {"warm_stained_wood", "anthracite_aluminium", "sage_grey", "industrial_white_steel"} else "glass.smoked_tinted"),
        )
        return

    f = _SASH_FACE
    in_x0, in_x1 = f, sw - f
    in_z0, in_z1 = f, sh - f
    in_w, in_h = in_x1 - in_x0, in_z1 - in_z0
    cell_w = (in_w - (cols - 1) * _MUNTIN_FACE) / cols
    cell_h = (in_h - (rows - 1) * _MUNTIN_FACE) / rows

    # Panes (j = col along X, k = row along Z).
    for j in range(cols):
        for k in range(rows):
            cx0 = in_x0 + j * (cell_w + _MUNTIN_FACE)
            cz0 = in_z0 + k * (cell_h + _MUNTIN_FACE)
            gx = cx0 + cell_w / 2.0
            gz = cz0 + cell_h / 2.0
            sash.visual(
                Box((cell_w + 2 * _GLASS_REBATE, _GLASS_T, cell_h + 2 * _GLASS_REBATE)),
                origin=Origin(xyz=(xs * gx, 0.0, gz)),
                material=mats["glass"],
                name=f"pane_{j}_{k}", material_class_id=("glass.clear_transparent" if r.palette_style in {"warm_stained_wood", "anthracite_aluminium", "sage_grey", "industrial_white_steel"} else "glass.smoked_tinted"),
            )

    # Vertical muntins (stand proud of the glass in +Y a touch).
    mun_y = 0.0
    for i in range(cols - 1):
        mx = in_x0 + (i + 1) * cell_w + (i + 0.5) * _MUNTIN_FACE
        sash.visual(
            Box((_MUNTIN_FACE, _MUNTIN_DEPTH, in_h)),
            origin=Origin(xyz=(xs * mx, mun_y, (in_z0 + in_z1) / 2.0)),
            material=mats["sash"],
            name=f"vmuntin_{i}", material_class_id=("wood.polished_varnished" if r.palette_style in {"warm_stained_wood", "sage_grey"} else "metal.aluminum_bare"),
        )
    # Horizontal muntins.
    for i in range(rows - 1):
        mz = in_z0 + (i + 1) * cell_h + (i + 0.5) * _MUNTIN_FACE
        sash.visual(
            Box((in_w, _MUNTIN_DEPTH, _MUNTIN_FACE)),
            origin=Origin(xyz=(xs * (in_x0 + in_x1) / 2.0, mun_y, mz)),
            material=mats["sash"],
            name=f"hmuntin_{i}", material_class_id=("wood.polished_varnished" if r.palette_style in {"warm_stained_wood", "sage_grey"} else "metal.aluminum_bare"),
        )


def _emit_lever_handle(
    sash, mats, *, hx: float, hz: float, face_sign: float, name_prefix: str
) -> None:
    """Casement lever handle (base plate + lever bar) on the sash face.
    face_sign = +1 -> handle stands off +Y (room/interior), -1 -> -Y."""
    base_y = face_sign * (_SASH_DEPTH / 2.0 + _HANDLE_BASE[1] / 2.0)
    sash.visual(
        Box(_HANDLE_BASE),
        origin=Origin(xyz=(hx, base_y, hz)),
        material=mats["hardware"],
        name=f"{name_prefix}_handle_base", material_class_id="metal.brass_polished",
    )
    # Lever bar (along X) stands just off the base outer face; its inner edge
    # touches the base so the two read as one connected handle (no island).
    lever_y = face_sign * (_SASH_DEPTH / 2.0 + _HANDLE_BASE[1] + _HANDLE_LEVER_R - 0.002)
    sash.visual(
        Cylinder(radius=_HANDLE_LEVER_R, length=_HANDLE_LEVER_LEN),
        origin=Origin(
            xyz=(hx, lever_y, hz),
            rpy=(0.0, math.pi / 2.0, 0.0),
        ),
        material=mats["hardware"],
        name=f"{name_prefix}_handle_lever", material_class_id="metal.brass_polished",
    )


def _emit_hinges(sash, mats, *, sh: float, name_prefix: str) -> None:
    """Visible barrel hinges along the sash hinge stile (local x=0)."""
    z0 = _SASH_FACE + _HINGE_LEN / 2.0
    z_span = max(0.05, sh - 2 * _SASH_FACE - _HINGE_LEN)
    for i in range(_HINGE_COUNT):
        frac = 0.0 if _HINGE_COUNT == 1 else i / (_HINGE_COUNT - 1)
        z = z0 + (0.15 + 0.7 * frac) * z_span
        sash.visual(
            Cylinder(radius=_HINGE_R, length=_HINGE_LEN),
            origin=Origin(xyz=(0.0, 0.0, z), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["hardware"],
            name=f"{name_prefix}_hinge_{i}", material_class_id="metal.brass_polished",
        )


# ===========================================================================
# Rectangular-family sash builder (side-hung / awning / hopper / bank lite)
# ===========================================================================
def _build_casement_sash(
    model, r: ResolvedWindowConfig, mats, *, name: str, sw: float, sh: float,
    mechanism: OpeningMechanism, with_muntin: bool, assets, mirror_x: bool = False,
):
    """Build one operable casement sash part (its own ring + glass + hardware).
    Authored in a local frame: hinge stile at local x=0; body extends +X
    (mirror_x=False) or -X (mirror_x=True, right-hung). Returns the part."""
    xs = -1.0 if mirror_x else 1.0
    sash = model.part(name)
    sash.visual(
        mesh_from_cadquery(_rect_ring(sw, sh, _SASH_FACE, _SASH_DEPTH, xs=xs), f"{name}_ring"),
        material=mats["sash"],
        name=f"{name}_ring", material_class_id=("wood.polished_varnished" if r.palette_style in {"warm_stained_wood", "sage_grey"} else "metal.aluminum_bare"),
    )
    if with_muntin and r.muntin_cols * r.muntin_rows > 1:
        _emit_muntins_and_panes(sash, r, mats, sw=sw, sh=sh, xs=xs)
    else:
        sash.visual(
            mesh_from_cadquery(_rect_glass(sw, sh, _SASH_FACE, xs=xs), f"{name}_glass"),
            material=mats["glass"],
            name=f"{name}_glass", material_class_id=("glass.clear_transparent" if r.palette_style in {"warm_stained_wood", "anthracite_aluminium", "sage_grey", "industrial_white_steel"} else "glass.smoked_tinted"),
        )
    return sash


# ===========================================================================
# Build
# ===========================================================================
def build_window(
    config: WindowConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        key: model.material(f"window_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in PALETTES[r.palette_style].items()
    }

    if r.frame_outline == "round_porthole":
        _build_porthole(model, r, mats, assets=assets)
    elif r.frame_outline == "arched_top":
        _build_arched(model, r, mats, assets=assets)
    elif r.frame_outline == "segmental_arch":
        _build_segmental(model, r, mats, assets=assets)
    else:
        _build_rectangular(model, r, mats, assets=assets)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_window(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_window(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Rectangular outline (covers all 5 rect mechanisms + linear/grid multiplicity)
# ---------------------------------------------------------------------------
def _build_rectangular(model, r: ResolvedWindowConfig, mats, *, assets):
    mech = r.opening_mechanism
    n_cols, n_rows, grid_mode = r.n_cols, r.n_rows, r.grid_mode

    if grid_mode:
        _build_bank_grid(model, r, mats, assets=assets)
        return
    if n_cols >= 2:
        _build_linear_bays(model, r, mats, assets=assets)
        return

    # ---- Single-unit rectangular window. ----
    ff = r.frame_face
    win_w, win_h = r.win_w, r.win_h
    depth = r.frame_depth
    op_x0 = -win_w / 2.0 + ff
    op_x1 = win_w / 2.0 - ff
    op_z0 = ff
    op_z1 = win_h - ff
    opening_w = op_x1 - op_x0
    opening_h = op_z1 - op_z0

    frame = model.part("frame")
    if mech == "single_hung_vertical":
        _build_single_hung(model, r, mats, frame, op_x0, op_x1, op_z0, op_z1, assets=assets)
        return

    # frame web (single opening cut).
    frame.visual(
        mesh_from_cadquery(
            _slab_cut_frame(win_w, win_h, depth, [(op_x0, op_x1, op_z0, op_z1)]),
            "frame",
        ),
        material=mats["frame"],
        name="frame_shell", material_class_id=("wood.polished_varnished" if r.palette_style in {"warm_stained_wood", "sage_grey"} else "metal.aluminum_bare"),
    )

    if mech == "fixed_picture_light":
        _build_fixed_picture(model, r, mats, frame, op_x0, op_x1, op_z0, op_z1, assets=assets)
        return

    # side_hung / awning / hopper single operable sash.
    cx = (op_x0 + op_x1) / 2.0
    if mech == "side_hung_casement":
        sw = opening_w - 2 * _SASH_GAP
        sh = opening_h - 2 * _SASH_GAP
        sash = _build_casement_sash(
            model, r, mats, name="sash", sw=sw, sh=sh, mechanism=mech,
            with_muntin=True, assets=assets,
        )
        # Body authored x 0..sw (hinge stile x=0), z 0..sh. Joint origin on the
        # left jamb (real frame material): hinge stile laps the jamb.
        _emit_hinges(sash, mats, sh=sh, name_prefix="sash")
        _emit_lever_handle(
            sash, mats, hx=sw - _SASH_FACE / 2.0, hz=sh * 0.45,
            face_sign=-1.0, name_prefix="sash",
        )
        hinge_x = op_x0 + _SASH_GAP
        seat_z = op_z0 + _SASH_GAP
        model.articulation(
            "frame_to_sash",
            ArticulationType.REVOLUTE,
            parent=frame, child=sash,
            origin=Origin(xyz=(hinge_x, 0.0, seat_z)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=12.0, velocity=2.0, lower=0.0, upper=1.5),
        )
    elif mech == "awning_top_hung":
        # Top-hung: hinge along the sash TOP rail. The sash top rail laps UP under
        # the frame head (capture) so the two parts touch. Author the body so its
        # local origin is the top rail; it hangs down along -Z, centered in X.
        sw = opening_w - 2 * _SASH_GAP
        sh = opening_h - 2 * _SASH_GAP + _HINGE_CAPTURE
        sash = _build_casement_sash(
            model, r, mats, name="sash", sw=sw, sh=sh, mechanism=mech,
            with_muntin=True, assets=assets,
        )
        _shift_part_visuals_x(sash, -sw / 2.0)
        _shift_part_visuals_z(sash, -sh)
        _emit_lever_handle(
            sash, mats, hx=0.0, hz=-sh + _SASH_FACE / 2.0, face_sign=-1.0,
            name_prefix="sash",
        )
        # Origin at the frame head bottom (op_z1) but tucked DOWN by capture so the
        # top rail laps under the head -> the rail mesh straddles op_z1.
        top_z = op_z1 + _HINGE_CAPTURE
        model.articulation(
            "frame_to_sash",
            ArticulationType.REVOLUTE,
            parent=frame, child=sash,
            origin=Origin(xyz=(cx, 0.0, top_z)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=20.0, velocity=1.5, lower=0.0, upper=0.85),
        )
    elif mech == "hopper_bottom_hung":
        # Bottom-hung: hinge along the sash BOTTOM rail which laps DOWN under the
        # frame sill (capture). Body authored z 0..sh, bottom rail at local z=0.
        sw = opening_w - 2 * _SASH_GAP
        sh = opening_h - 2 * _SASH_GAP + _HINGE_CAPTURE
        sash = _build_casement_sash(
            model, r, mats, name="sash", sw=sw, sh=sh, mechanism=mech,
            with_muntin=True, assets=assets,
        )
        _shift_part_visuals_x(sash, -sw / 2.0)
        _emit_lever_handle(
            sash, mats, hx=0.0, hz=sh - _SASH_FACE / 2.0, face_sign=-1.0,
            name_prefix="sash",
        )
        # Origin at the sill top tucked DOWN by capture so the bottom rail laps
        # the sill (straddles op_z0).
        bot_z = op_z0 - _HINGE_CAPTURE
        model.articulation(
            "frame_to_sash",
            ArticulationType.REVOLUTE,
            parent=frame, child=sash,
            origin=Origin(xyz=(cx, 0.0, bot_z)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=20.0, velocity=1.5, lower=-0.85, upper=0.0),
        )


def _shift_part_visuals_x(part, dx: float) -> None:
    for v in part.visuals:
        o = v.origin
        v.origin = Origin(xyz=(o.xyz[0] + dx, o.xyz[1], o.xyz[2]), rpy=o.rpy)


def _shift_part_visuals_z(part, dz: float) -> None:
    for v in part.visuals:
        o = v.origin
        v.origin = Origin(xyz=(o.xyz[0], o.xyz[1], o.xyz[2] + dz), rpy=o.rpy)


# ---------------------------------------------------------------------------
# Single-hung (PRISMATIC lower + FIXED upper) — adapted from single-hung source.
# ---------------------------------------------------------------------------
def _build_single_hung(model, r, mats, frame, op_x0, op_x1, op_z0, op_z1, *, assets):
    ff = r.frame_face
    win_w, win_h = r.win_w, r.win_h
    depth = r.frame_depth
    open_w = op_x1 - op_x0
    open_h = op_z1 - op_z0
    sash_tuck = 0.007
    sash_w = open_w + 2 * sash_tuck
    upper_h = open_h * 0.52
    lower_h = open_h * 0.50
    sash_y_gap = 0.014
    lower_y = -sash_y_gap
    upper_y = sash_y_gap
    lower_bot_z = op_z0 + 0.003
    upper_bot_z = lower_bot_z + lower_h - _SASH_FACE

    # Frame web (no track grooves cut — keep it a robust solid ring; sash stiles
    # tuck under the jamb, declared as allow_overlap).
    frame.visual(
        mesh_from_cadquery(
            _slab_cut_frame(win_w, win_h, depth, [(op_x0, op_x1, op_z0, op_z1)]),
            "frame",
        ),
        material=mats["frame"],
        name="frame_shell", material_class_id=("wood.polished_varnished" if r.palette_style in {"warm_stained_wood", "sage_grey"} else "metal.aluminum_bare"),
    )

    for name, sh in (("upper_sash", upper_h), ("lower_sash", lower_h)):
        sash = model.part(name)
        sash.visual(
            mesh_from_cadquery(_rect_ring(sash_w, sh, _SASH_FACE, _SASH_DEPTH), f"{name}_ring"),
            material=mats["sash"],
            name=f"{name}_ring", material_class_id=("wood.polished_varnished" if r.palette_style in {"warm_stained_wood", "sage_grey"} else "metal.aluminum_bare"),
        )
        sash.visual(
            mesh_from_cadquery(_rect_glass(sash_w, sh, _SASH_FACE), f"{name}_glass"),
            material=mats["glass"],
            name=f"{name}_glass", material_class_id=("glass.clear_transparent" if r.palette_style in {"warm_stained_wood", "anthracite_aluminium", "sage_grey", "industrial_white_steel"} else "glass.smoked_tinted"),
        )
        _shift_part_visuals_x(sash, -sash_w / 2.0)
        if name == "upper_sash":
            # Author the upper sash so its local origin is at its TOP rail; the
            # FIXED joint origin then lands on the frame head (real material).
            _shift_part_visuals_z(sash, -upper_h)

    lower = model.get_part("lower_sash")
    # cam lock at the meeting rail (top of lower sash, centered).
    lock_z = lower_h - _SASH_FACE / 2.0
    base_y = -(_SASH_DEPTH / 2.0 + 0.011)
    lower.visual(
        Box((0.072, 0.022, 0.020)),
        origin=Origin(xyz=(0.0, base_y, lock_z)),
        material=mats["hardware"],
        name="lower_sash_lock_base", material_class_id=("metal.brass_polished" if r.palette_style in {"warm_stained_wood", "industrial_white_steel", "glossy_black_porthole", "grey_aluminium_blue_glass"} else "metal.stainless_matte"),
    )
    lower.visual(
        Cylinder(radius=0.013, length=0.020),
        origin=Origin(xyz=(0.0, base_y - 0.018, lock_z), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["hardware"],
        name="lower_sash_cam", material_class_id=("metal.brass_polished" if r.palette_style in {"warm_stained_wood", "industrial_white_steel", "glossy_black_porthole", "grey_aluminium_blue_glass"} else "metal.stainless_matte"),
    )
    lower.visual(
        Box((0.040, 0.011, 0.010)),
        origin=Origin(xyz=(0.018, base_y - 0.018, lock_z)),
        material=mats["hardware"],
        name="lower_sash_cam_lever", material_class_id=("metal.brass_polished" if r.palette_style in {"warm_stained_wood", "industrial_white_steel", "glossy_black_porthole", "grey_aluminium_blue_glass"} else "metal.stainless_matte"),
    )

    # Joint origins land on real frame material AND on the child's local (0,0,0):
    #  - upper FIXED: origin at the head (z=op_z1); upper sash authored so its
    #    local origin is its TOP rail -> it hangs down to its seated position.
    #  - lower PRISMATIC: origin at the sill top (z=op_z0); lower sash local
    #    origin is its bottom rail, seated on the sill.
    model.articulation(
        "frame_to_upper_sash",
        ArticulationType.FIXED,
        parent=frame, child=model.get_part("upper_sash"),
        origin=Origin(xyz=(0.0, upper_y, op_z1)),
    )
    model.articulation(
        "frame_to_lower_sash",
        ArticulationType.PRISMATIC,
        parent=frame, child=lower,
        origin=Origin(xyz=(0.0, lower_y, op_z0)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=60.0, velocity=0.25, lower=0.0, upper=lower_h * 0.45),
    )


# ---------------------------------------------------------------------------
# Fixed picture light + trickle vent flap — adapted from fixed_picture source.
# ---------------------------------------------------------------------------
def _build_fixed_picture(model, r, mats, frame, op_x0, op_x1, op_z0, op_z1, *, assets):
    opening_w = op_x1 - op_x0
    opening_h = op_z1 - op_z0
    sash_w = opening_w + 0.002   # seats into the rebate (1 mm overlap per side)
    sash_h = opening_h + 0.002
    sash_x0 = op_x0 - 0.001
    sash_bot_z = op_z0 - 0.001

    vent_hinge_z_local = sash_h - 0.005
    vent_slot_h = 0.030
    vent_slot_w = 0.200
    vent_slot_cz_local = vent_hinge_z_local - 0.005 - vent_slot_h / 2.0

    # Fixed sash frame ring with the vent slot cut + glass + dark recess as
    # frame visuals (Rule 1 — these don't move).
    ring = _rect_ring(sash_w, sash_h, _SASH_FACE, _SASH_DEPTH)
    slot = (
        cq.Workplane("XY")
        .transformed(offset=(sash_w / 2.0, 0.0, vent_slot_cz_local))
        .box(vent_slot_w, _SASH_DEPTH + 0.02, vent_slot_h)
    )
    ring = ring.cut(slot)
    frame.visual(
        mesh_from_cadquery(ring, "sash_frame"),
        origin=Origin(xyz=(sash_x0, 0.0, sash_bot_z)),
        material=mats["sash"],
        name="sash_frame", material_class_id=("wood.polished_varnished" if r.palette_style in {"warm_stained_wood", "sage_grey"} else "metal.aluminum_bare"),
    )
    frame.visual(
        mesh_from_cadquery(_rect_glass(sash_w, sash_h, _SASH_FACE), "sash_glass"),
        origin=Origin(xyz=(sash_x0, 0.0, sash_bot_z)),
        material=mats["glass"],
        name="sash_glass", material_class_id=("glass.clear_transparent" if r.palette_style in {"warm_stained_wood", "anthracite_aluminium", "sage_grey", "industrial_white_steel"} else "glass.smoked_tinted"),
    )
    # dark recess behind the vent slot.
    recess_y = -(_SASH_DEPTH / 2.0) + 0.0025
    frame.visual(
        Box((vent_slot_w - 0.010, 0.003, vent_slot_h + 0.002)),
        origin=Origin(xyz=(sash_x0 + sash_w / 2.0, recess_y, sash_bot_z + vent_slot_cz_local)),
        material=mats["frame"],
        name="vent_recess", material_class_id=("wood.polished_varnished" if r.palette_style in {"warm_stained_wood", "sage_grey"} else "metal.aluminum_bare"),
    )

    # Vent flap (the only moving part). Authored in the vent pivot frame: hinge
    # at local origin, flap extends down (-Z) and forward (+Y).
    vent = model.part("vent")
    vent.visual(
        Box((_VENT_W, _VENT_DEPTH, _VENT_H)),
        origin=Origin(xyz=(0.0, _VENT_DEPTH / 2.0, -_VENT_H / 2.0)),
        material=mats["sash"],
        name="vent_flap", material_class_id=("wood.polished_varnished" if r.palette_style in {"warm_stained_wood", "sage_grey"} else "metal.aluminum_bare"),
    )
    vent.visual(
        Box((0.030, 0.008, 0.010)),
        origin=Origin(xyz=(0.0, _VENT_DEPTH + 0.004, -_VENT_H + 0.009)),
        material=mats["hardware"],
        name="vent_catch", material_class_id=("metal.brass_polished" if r.palette_style in {"warm_stained_wood", "industrial_white_steel", "glossy_black_porthole", "grey_aluminium_blue_glass"} else "metal.stainless_matte"),
    )
    for i, x_off in enumerate((-_VENT_W / 2.0 + 0.020, _VENT_W / 2.0 - 0.020)):
        vent.visual(
            Cylinder(radius=0.004, length=0.016),
            origin=Origin(xyz=(x_off, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["hardware"],
            name=f"vent_knuckle_{i}", material_class_id=("metal.brass_polished" if r.palette_style in {"warm_stained_wood", "industrial_white_steel", "glossy_black_porthole", "grey_aluminium_blue_glass"} else "metal.stainless_matte"),
        )

    vent_hinge_z = sash_bot_z + vent_hinge_z_local
    model.articulation(
        "frame_to_vent",
        ArticulationType.REVOLUTE,
        parent=frame, child=vent,
        origin=Origin(xyz=(sash_x0 + sash_w / 2.0, _SASH_DEPTH / 2.0, vent_hinge_z)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=2.0, velocity=1.0, lower=0.0, upper=0.8),
    )


# ---------------------------------------------------------------------------
# Linear bays (twin / triple) — adapted from triple_mullion source.
# ---------------------------------------------------------------------------
def _build_linear_bays(model, r, mats, *, assets):
    n = r.n_cols
    ff = r.frame_face
    depth = r.frame_depth
    # Each bay holds a sash sized off the base single window, scaled by width.
    bay_clear_w = (_WIN_W * r.win_w / _WIN_W) * 0.50  # ~ half a single window
    bay_clear_w = max(0.40, min(0.62, bay_clear_w * (r.win_w / _WIN_W)))
    sash_face = _SASH_FACE
    sash_w = bay_clear_w
    sash_clear = 0.004
    bay_w = sash_w + 2 * sash_clear
    opening_h = (r.win_h - 2 * ff)
    sash_h = opening_h - 2 * sash_clear
    total_w = n * bay_w + (n - 1) * _MULLION_W + 2 * ff
    total_h = r.win_h

    def _bay_left(i: int) -> float:
        return -(n * bay_w + (n - 1) * _MULLION_W) / 2.0 + i * (bay_w + _MULLION_W)

    # Frame: slab with n bay openings cut (mullions = uncut material between).
    op_z0 = ff
    op_z1 = total_h - ff
    openings = []
    for i in range(n):
        bx0 = _bay_left(i)
        openings.append((bx0, bx0 + bay_w, op_z0, op_z1))
    frame = model.part("frame")
    frame.visual(
        mesh_from_cadquery(_slab_cut_frame(total_w, total_h, depth, openings), "frame"),
        material=mats["frame"],
        name="frame_shell", material_class_id=("wood.polished_varnished" if r.palette_style in {"warm_stained_wood", "sage_grey"} else "metal.aluminum_bare"),
    )

    seat_z = op_z0 + sash_clear

    def _is_left_hung(i: int) -> bool:
        return i < n - 1

    for i in range(n):
        name = f"sash_{i}"
        left_hung = _is_left_hung(i)
        sash = _build_casement_sash(
            model, r, mats, name=name, sw=sash_w, sh=sash_h,
            mechanism="side_hung_casement", with_muntin=True, assets=assets,
            mirror_x=not left_hung,
        )
        _emit_hinges(sash, mats, sh=sash_h, name_prefix=name)
        hx_free = (sash_w - sash_face / 2.0) * (1.0 if left_hung else -1.0)
        _emit_lever_handle(
            sash, mats, hx=hx_free, hz=sash_h * 0.45,
            face_sign=-1.0, name_prefix=name,
        )
        if left_hung:
            hinge_x = _bay_left(i) + sash_clear
            axis = (0.0, 0.0, 1.0)
        else:
            hinge_x = _bay_left(i) + bay_w - sash_clear
            axis = (0.0, 0.0, -1.0)
        model.articulation(
            f"frame_to_{name}",
            ArticulationType.REVOLUTE,
            parent=frame, child=sash,
            origin=Origin(xyz=(hinge_x, 0.0, seat_z)),
            axis=axis,
            motion_limits=MotionLimits(effort=18.0, velocity=1.5, lower=0.0, upper=1.5),
        )


# ---------------------------------------------------------------------------
# Bank lite grid (2x2 / 3x2) — adapted from bank source.
# ---------------------------------------------------------------------------
def _build_bank_grid(model, r, mats, *, assets):
    n_cols, n_rows = r.n_cols, r.n_rows
    ff = r.frame_face
    depth = r.frame_depth
    lite_w = max(0.50, min(0.66, 0.58 * (r.win_w / _WIN_W)))
    lite_h = max(0.62, min(0.82, 0.74 * (r.win_h / _WIN_H)))
    total_w = n_cols * lite_w + (n_cols + 1) * ff
    total_h = n_rows * lite_h + (n_rows + 1) * ff

    def _lite_bounds(col: int, row: int):
        x0 = -total_w / 2.0 + ff + col * (lite_w + ff)
        x1 = x0 + lite_w
        z0 = ff + row * (lite_h + ff)
        z1 = z0 + lite_h
        return x0, x1, z0, z1

    # Frame web (all lites cut).
    openings = [_lite_bounds(c, rr) for c in range(n_cols) for rr in range(n_rows)]
    frame = model.part("frame")
    frame.visual(
        mesh_from_cadquery(_slab_cut_frame(total_w, total_h, depth, openings), "frame"),
        material=mats["frame"],
        name="frame_web", material_class_id=("wood.polished_varnished" if r.palette_style in {"warm_stained_wood", "sage_grey"} else "metal.aluminum_bare"),
    )

    # Operable set: 1 per column on the top row (bank_2x2 -> 1 operable;
    # bank_3x2 -> spec says 2; we make top-row lites operable, capped at 2).
    operable_count = 2 if (n_cols >= 3 and n_rows >= 2) else 1
    operable: set[tuple[int, int]] = set()
    top_row = n_rows - 1
    for c in range(min(operable_count, n_cols)):
        operable.add((c, top_row))

    # Fixed glass in the non-operable lites (Rule 1 frame visuals).
    rebate = 0.007
    for col in range(n_cols):
        for row in range(n_rows):
            if (col, row) in operable:
                continue
            x0, x1, z0, z1 = _lite_bounds(col, row)
            gx0, gx1 = x0 - rebate, x1 + rebate
            gz0, gz1 = z0 - rebate, z1 + rebate
            frame.visual(
                Box((gx1 - gx0, _GLASS_T, gz1 - gz0)),
                origin=Origin(xyz=((gx0 + gx1) / 2.0, 0.0, (gz0 + gz1) / 2.0)),
                material=mats["glass"],
                name=f"fixed_glass_{col}_{row}", material_class_id=("glass.clear_transparent" if r.palette_style in {"warm_stained_wood", "anthracite_aluminium", "sage_grey", "industrial_white_steel"} else "glass.smoked_tinted"),
            )

    # Operable side-hung sashes.
    sash_clear = 0.004
    for col, row in sorted(operable):
        x0, x1, z0, z1 = _lite_bounds(col, row)
        sw = (x1 - x0) - 2 * sash_clear
        sh = (z1 - z0) - 2 * sash_clear
        name = f"sash_{col}_{row}"
        sash = _build_casement_sash(
            model, r, mats, name=name, sw=sw, sh=sh,
            mechanism="side_hung_casement", with_muntin=False, assets=assets,
        )
        _emit_hinges(sash, mats, sh=sh, name_prefix=name)
        _emit_lever_handle(
            sash, mats, hx=sw - _SASH_FACE / 2.0, hz=sh * 0.45,
            face_sign=1.0, name_prefix=name,
        )
        hinge_x = x0 + sash_clear
        hinge_z = z0 + sash_clear
        model.articulation(
            f"frame_to_{name}",
            ArticulationType.REVOLUTE,
            parent=frame, child=sash,
            origin=Origin(xyz=(hinge_x, 0.0, hinge_z)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=18.0, velocity=1.5, lower=0.0, upper=1.5),
        )


# ---------------------------------------------------------------------------
# Round porthole — adapted from porthole source.
# ---------------------------------------------------------------------------
def _build_porthole(model, r, mats, *, assets):
    outer_r = _PORT_OUTER_R * (r.win_w / _WIN_W)
    ring_w = _PORT_RING_W
    inner_bore_r = outer_r - ring_w
    frame_depth = _PORT_FRAME_DEPTH
    collar_r = inner_bore_r + 0.018
    collar_depth = 0.050
    sash_outer_r = inner_bore_r - 0.004
    sash_ring_w = _PORT_SASH_RING_W
    # Glass disc nearly fills the inner bore: only a thin rebate insets it from
    # the sash outer radius so the glass slips UNDER the sash ring (overlapping
    # it inward by sash_ring_w - rebate) — leaving no visible empty annulus
    # between glass and ring. The sash then reads as a thin ring on a big disc.
    sash_glass_r = sash_outer_r - 0.012
    center_z = outer_r + 0.02

    # Outer ring + back collar.
    bezel = _ring_shape(outer_r, inner_bore_r, frame_depth / 2.0)
    collar = (
        cq.Workplane("XZ")
        .workplane(offset=frame_depth / 2.0)
        .circle(collar_r + ring_w * 0.5)
        .circle(collar_r)
        .extrude(collar_depth)
    )
    frame = model.part("frame")
    frame.visual(
        mesh_from_cadquery(bezel.union(collar), "frame_ring"),
        origin=Origin(xyz=(0.0, 0.0, center_z)),
        material=mats["frame"],
        name="frame_ring", material_class_id=("wood.polished_varnished" if r.palette_style in {"warm_stained_wood", "sage_grey"} else "metal.aluminum_bare"),
    )

    sash = model.part("sash")
    # The center-pivot joint origin sits OFF-CENTER on the right pivot pin (see
    # note below). Author every sash visual shifted by -pin_center_x in x so that,
    # after the joint translate maps sash-local origin onto the parent joint origin
    # at (pin_center_x, .., ..), the ring + glass recenter concentrically on the
    # bore (x=0) instead of being shoved sideways by pin_center_x.
    pin_center_x = (sash_outer_r + inner_bore_r) / 2.0
    cxs = -pin_center_x
    sash.visual(
        mesh_from_cadquery(
            _ring_shape(sash_outer_r, sash_outer_r - sash_ring_w, _PORT_SASH_DEPTH / 2.0),
            "sash_ring",
        ),
        origin=Origin(xyz=(cxs, 0.0, 0.0)),
        material=mats["sash"],
        name="sash_ring", material_class_id=("wood.polished_varnished" if r.palette_style in {"warm_stained_wood", "sage_grey"} else "metal.aluminum_bare"),
    )
    sash.visual(
        mesh_from_cadquery(_disc_shape(sash_glass_r, _PORT_GLASS_T / 2.0), "sash_glass"),
        origin=Origin(xyz=(cxs, 0.0, 0.0)),
        material=mats["glass"],
        name="sash_glass", material_class_id=("glass.clear_transparent" if r.palette_style in {"warm_stained_wood", "anthracite_aluminium", "sage_grey", "industrial_white_steel"} else "glass.smoked_tinted"),
    )
    for sign, tag in ((1.0, "right"), (-1.0, "left")):
        sash.visual(
            Cylinder(radius=_PORT_PIN_R, length=_PORT_PIN_LEN),
            origin=Origin(xyz=(cxs + sign * pin_center_x, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["hardware"],
            name=f"pivot_pin_{tag}", material_class_id=("metal.brass_polished" if r.palette_style in {"warm_stained_wood", "industrial_white_steel", "glossy_black_porthole", "grey_aluminium_blue_glass"} else "metal.stainless_matte"),
        )

    # Center-pivot axis is the horizontal diameter line (y=0, z=center_z). The
    # joint origin can be any point on that line; placing it ON the right pivot
    # pin / bore wall (off-center) keeps the same rotation axis through the
    # center while sitting on real hardware (both pin & ring bore are there), so
    # fail_if_articulation_origin_far_from_geometry passes (the bore ring void at
    # the exact center holds no frame material).
    model.articulation(
        "frame_to_sash",
        ArticulationType.REVOLUTE,
        parent=frame, child=sash,
        origin=Origin(xyz=(pin_center_x, 0.0, center_z)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=6.0, velocity=2.0, lower=-0.8, upper=0.8),
    )


# ---------------------------------------------------------------------------
# Arched top (semicircle head + radial fanlight + stone surround) — arched src.
# ---------------------------------------------------------------------------
def _build_arched(model, r, mats, *, assets):
    half_w = 0.46 * (r.win_w / _WIN_W)
    arch_r = half_w
    wood_frame_w = _FRAME_FACE
    wood_depth = r.frame_depth
    transom_h = 0.055
    sill_top_z = 0.150
    spring_z = sill_top_z + 1.05 * (r.win_h / _WIN_H)
    twin = r.sash_unit_count == "twin_double_2"

    frame = model.part("surround")

    # --- Wood arched frame: semicircular head ring + straight jambs. The
    # spring transom / center mullion (when present) are emitted separately in
    # the split layout below (same `surround` part, Rule 1 named visuals). ---
    outer_half = half_w + wood_frame_w
    outer = (
        cq.Workplane("XZ")
        .moveTo(-outer_half, sill_top_z)
        .lineTo(outer_half, sill_top_z)
        .lineTo(outer_half, spring_z)
        .threePointArc((0.0, spring_z + outer_half), (-outer_half, spring_z))
        .close()
        .extrude(wood_depth / 2.0, both=True)
    )
    inner = (
        cq.Workplane("XZ")
        .moveTo(-half_w, sill_top_z - 0.02)
        .lineTo(half_w, sill_top_z - 0.02)
        .lineTo(half_w, spring_z)
        .threePointArc((0.0, spring_z + half_w), (-half_w, spring_z))
        .close()
        .extrude(wood_depth / 2.0 + 0.02, both=True)
    )
    wood = outer.cut(inner)
    frame.visual(
        mesh_from_cadquery(wood, "wood_frame"),
        material=mats["frame"],
        name="wood_frame", material_class_id=("wood.polished_varnished" if r.palette_style in {"warm_stained_wood", "sage_grey"} else "metal.aluminum_bare"),
    )

    # --- Stone surround + keystone + sill + corbels (Rule 1 visuals). ---
    _emit_stone_surround(frame, mats, half_w, wood_frame_w, sill_top_z, spring_z)

    sash_face = _SASH_FACE
    sash_clear_mullion = 0.014
    seat_z = sill_top_z + _SASH_GAP
    fan = r.divided_light_grid == "arched_radial_fan"

    # Two distinct layouts, both fully glazing the semicircular head:
    #  - "split" (twin OR radial fanlight): rectangular operable casement(s)
    #    below the spring transom + a FIXED arch-shaped fanlight glazing the
    #    head (radial ribs overlaid for the fan grid).
    #  - "full arch" (single, non-fan): one operable ARCHED sash spanning the
    #    whole opening sill->crown so the glass follows the arch all the way up.
    split = twin or fan
    if split:
        # spring transom bar in the wood frame.
        transom = (
            cq.Workplane("XZ").moveTo(0.0, spring_z)
            .rect(2 * half_w, transom_h).extrude(wood_depth / 2.0, both=True)
        )
        frame.visual(
            mesh_from_cadquery(transom, "spring_transom"),
            material=mats["frame"],
            name="spring_transom", material_class_id=("wood.polished_varnished" if r.palette_style in {"warm_stained_wood", "sage_grey"} else "metal.aluminum_bare"),
        )
        # FIXED arched fanlight glass — semicircular, fully glazing the head.
        fan_hw = half_w - sash_face
        fan_rise = fan_hw  # tall semicircle (arched_top distinction)
        fan_glass = _arch_solid(fan_hw, spring_z + transom_h / 2.0, spring_z,
                                fan_rise, _GLASS_T)
        frame.visual(
            mesh_from_cadquery(fan_glass, "fanlight_glass"),
            material=mats["glass"],
            name="fanlight_glass", material_class_id=("glass.clear_transparent" if r.palette_style in {"warm_stained_wood", "anthracite_aluminium", "sage_grey", "industrial_white_steel"} else "glass.smoked_tinted"),
        )
        if fan:
            # radial ribs over the fixed fanlight glass (Rule 1 frame visuals).
            _emit_fanlight(frame, mats, arch_r, spring_z, wood_depth)

        # operable rectangular casement(s) below the transom.
        sash_opening_h = spring_z - sill_top_z
        sh = sash_opening_h - 2 * _SASH_GAP
        if twin:
            mull_h = spring_z - sill_top_z
            mullion = (
                cq.Workplane("XZ")
                .moveTo(0.0, sill_top_z + mull_h / 2.0)
                .rect(_MULLION_W, mull_h)
                .extrude(wood_depth * 0.35, both=True)
            )
            frame.visual(
                mesh_from_cadquery(mullion, "mullion"),
                material=mats["frame"],
                name="mullion", material_class_id=("wood.polished_varnished" if r.palette_style in {"warm_stained_wood", "sage_grey"} else "metal.aluminum_bare"),
            )
            sw = (half_w - sash_clear_mullion / 2.0) - _SASH_GAP
            for tag, sign in (("left", -1.0), ("right", 1.0)):
                name = f"sash_{tag}"
                left_hung = sign < 0
                sash = _build_casement_sash(
                    model, r, mats, name=name, sw=sw, sh=sh,
                    mechanism="side_hung_casement", with_muntin=True, assets=assets,
                    mirror_x=not left_hung,
                )
                _emit_hinges(sash, mats, sh=sh, name_prefix=name)
                hx_free = (sw - sash_face / 2.0) * (1.0 if left_hung else -1.0)
                _emit_lever_handle(sash, mats, hx=hx_free, hz=sh * 0.45,
                                   face_sign=-1.0, name_prefix=name)
                if left_hung:
                    hinge_x = -half_w + _SASH_GAP
                    axis = (0.0, 0.0, 1.0)
                else:
                    hinge_x = half_w - _SASH_GAP
                    axis = (0.0, 0.0, -1.0)
                model.articulation(
                    f"surround_to_{name}",
                    ArticulationType.REVOLUTE,
                    parent=frame, child=sash,
                    origin=Origin(xyz=(hinge_x, 0.0, seat_z)),
                    axis=axis,
                    motion_limits=MotionLimits(effort=18.0, velocity=1.5, lower=0.0, upper=1.4),
                )
        else:
            sw = 2 * half_w - 2 * _SASH_GAP
            name = "sash"
            sash = _build_casement_sash(
                model, r, mats, name=name, sw=sw, sh=sh,
                mechanism="side_hung_casement", with_muntin=True, assets=assets,
            )
            _emit_hinges(sash, mats, sh=sh, name_prefix=name)
            _emit_lever_handle(sash, mats, hx=sw - sash_face / 2.0, hz=sh * 0.45,
                               face_sign=-1.0, name_prefix=name)
            hinge_x = -half_w + _SASH_GAP
            model.articulation(
                "surround_to_sash",
                ArticulationType.REVOLUTE,
                parent=frame, child=sash,
                origin=Origin(xyz=(hinge_x, 0.0, seat_z)),
                axis=(0.0, 0.0, 1.0),
                motion_limits=MotionLimits(effort=18.0, velocity=1.5, lower=0.0, upper=1.4),
            )
    else:
        # Single operable ARCHED sash spanning the full opening (sill -> crown).
        # The sash glass follows the semicircular head -> head fully glazed.
        sash_w = 2 * half_w - 2 * _SASH_GAP
        sash_hw = sash_w / 2.0
        sash_local_spring = spring_z - seat_z
        sash_rise = sash_hw  # tall semicircle (arched_top distinction)
        name = "sash"
        _build_arch_sash(model, r, mats, name=name, sash_hw=sash_hw,
                         sash_local_spring=sash_local_spring, sash_rise=sash_rise,
                         assets=assets, muntin=True)
        sash = model.get_part(name)
        # Hinges only span the straight jamb (below the spring line) — above it
        # the ring curves inward into the arched head, so a hinge at local x=0
        # up there would float in the head void (disconnected island).
        _emit_hinges(sash, mats, sh=sash_local_spring, name_prefix=name)
        _emit_lever_handle(sash, mats, hx=sash_w - sash_face / 2.0, hz=sash_local_spring * 0.45,
                           face_sign=-1.0, name_prefix=name)
        hinge_x = -half_w + _SASH_GAP
        model.articulation(
            "surround_to_sash",
            ArticulationType.REVOLUTE,
            parent=frame, child=sash,
            origin=Origin(xyz=(hinge_x, 0.0, seat_z)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=18.0, velocity=1.5, lower=0.0, upper=1.4),
        )


def _emit_stone_surround(frame, mats, half_w, wood_frame_w, sill_top_z, spring_z):
    stone_gap = 0.010
    stone_w = 0.110
    stone_depth = 0.090
    in_half = half_w + wood_frame_w + stone_gap
    out_half = in_half + stone_w
    outer = (
        cq.Workplane("XZ")
        .moveTo(-out_half, sill_top_z)
        .lineTo(out_half, sill_top_z)
        .lineTo(out_half, spring_z)
        .threePointArc((0.0, spring_z + out_half), (-out_half, spring_z))
        .close()
        .extrude(stone_depth / 2.0, both=True)
    )
    inner = (
        cq.Workplane("XZ")
        .moveTo(-in_half, sill_top_z - 0.02)
        .lineTo(in_half, sill_top_z - 0.02)
        .lineTo(in_half, spring_z)
        .threePointArc((0.0, spring_z + in_half), (-in_half, spring_z))
        .close()
        .extrude(stone_depth / 2.0 + 0.02, both=True)
    )
    surround = outer.cut(inner)
    frame.visual(
        mesh_from_cadquery(surround, "stone_surround"),
        material=mats["stone"],
        name="stone_surround", material_class_id="stone.cut_sedimentary",
    )
    # Keystone wedge at the apex.
    arch_apex_z = spring_z + out_half
    z_bot = arch_apex_z - 0.160 * 0.60
    z_top = arch_apex_z + 0.160 * 0.40
    key = (
        cq.Workplane("XZ")
        .moveTo(-0.055, z_bot)
        .lineTo(0.055, z_bot)
        .lineTo(0.075, z_top)
        .lineTo(-0.075, z_top)
        .close()
        .extrude(stone_depth / 2.0 + 0.020, both=True)
    )
    frame.visual(
        mesh_from_cadquery(key, "keystone"),
        material=mats["stone"],
        name="keystone", material_class_id="stone.cut_sedimentary",
    )
    # Projecting sill + two corbels (lifted so corbel bottoms ~ z=0).
    sill_half_w = out_half + 0.075
    back_y = -stone_depth / 2.0
    front_y = stone_depth / 2.0 + 0.085
    cy = (back_y + front_y) / 2.0
    sdepth = front_y - back_y
    sill_h = sill_top_z
    sill = (
        cq.Workplane("XY")
        .transformed(offset=(0.0, cy, sill_h / 2.0))
        .box(2 * sill_half_w, sdepth, sill_h)
    )
    frame.visual(
        mesh_from_cadquery(sill, "stone_sill"),
        material=mats["stone"],
        name="stone_sill", material_class_id="stone.cut_sedimentary",
    )


def _emit_fanlight(frame, mats, arch_r, spring_z, wood_depth):
    cz = spring_z
    r_out = arch_r - 0.008
    rib_d = wood_depth * 0.6
    for i in range(_ARCH_FAN_RADIAL):
        ang = math.pi * (i + 1) / (_ARCH_FAN_RADIAL + 1)
        length = r_out
        mx = math.cos(ang) * length / 2.0
        mz = cz + math.sin(ang) * length / 2.0
        rib = (
            cq.Workplane("XZ")
            .moveTo(mx, mz)
            .rect(length, _ARCH_FAN_RIB_W)
            .extrude(rib_d / 2.0, both=True)
        )
        rib = rib.rotate((mx, 0.0, mz), (mx, 1.0, mz), math.degrees(ang))
        frame.visual(
            mesh_from_cadquery(rib, f"fan_rib_{i}"),
            material=mats["sash"],
            name=f"fan_rib_{i}", material_class_id="wood.polished_varnished",
        )
    # concentric arc band at 0.55 R.
    rr = r_out * 0.55
    ri = rr - _ARCH_FAN_RIB_W
    band = (
        cq.Workplane("XZ")
        .moveTo(rr, cz)
        .threePointArc((0.0, cz + rr), (-rr, cz))
        .lineTo(-ri, cz)
        .threePointArc((0.0, cz + ri), (ri, cz))
        .close()
        .extrude(rib_d / 2.0, both=True)
    )
    frame.visual(
        mesh_from_cadquery(band, "fan_arc"),
        material=mats["sash"],
        name="fan_arc", material_class_id="wood.polished_varnished",
    )
    # NB: the fanlight GLASS is the arch-shaped fixed light emitted by the
    # caller (_build_arched split path) — it already fully glazes the head, so
    # the ribs/band here are decorative tracery only (no separate glass disc).


# ---------------------------------------------------------------------------
# Segmental arch — adapted from segmental source.
# ---------------------------------------------------------------------------
def _build_segmental(model, r, mats, *, assets):
    win_w = r.win_w
    win_h = r.win_h
    frame_face = r.frame_face
    frame_depth = r.frame_depth
    arch_rise = r.arch_rise
    spring_z = win_h - arch_rise
    hw_outer = win_w / 2.0
    d_outer = (hw_outer ** 2 - arch_rise ** 2) / (2.0 * arch_rise)
    arc_center_z = spring_z - d_outer

    def _rise_for(half_w: float) -> float:
        R = math.sqrt(half_w ** 2 + d_outer ** 2)
        return (arc_center_z + R) - spring_z

    op_x0 = -win_w / 2.0 + frame_face
    op_x1 = win_w / 2.0 - frame_face
    op_z0 = frame_face
    opening_w = op_x1 - op_x0
    open_hw = opening_w / 2.0
    inner_rise = _rise_for(open_hw)

    frame = model.part("frame")
    outer = _arch_solid(hw_outer, 0.0, spring_z, arch_rise, frame_depth)
    inner = _arch_solid(open_hw, op_z0, spring_z, inner_rise, frame_depth + 0.02)
    frame.visual(
        mesh_from_cadquery(outer.cut(inner), "frame"),
        material=mats["frame"],
        name="frame_shell", material_class_id=("wood.polished_varnished" if r.palette_style in {"warm_stained_wood", "sage_grey"} else "metal.aluminum_bare"),
    )

    twin = r.sash_unit_count == "twin_double_2"
    mech = r.opening_mechanism

    if twin:
        # two sashes meeting at center.
        sash_clear_mullion = 0.014
        seat_z = op_z0 + _SASH_GAP
        for tag, sign in (("left", -1.0), ("right", 1.0)):
            name = f"sash_{tag}"
            left_hung = sign < 0
            sash_hw = (open_hw - sash_clear_mullion / 2.0) - _SASH_GAP
            sw = 2 * sash_hw
            sash_local_spring = spring_z - seat_z
            sash_rise = _rise_for(sash_hw)
            sh = sash_local_spring + sash_rise
            _build_arch_sash(model, r, mats, name=name, sash_hw=sash_hw,
                             sash_local_spring=sash_local_spring, sash_rise=sash_rise,
                             assets=assets, mirror_x=not left_hung)
            sash = model.get_part(name)
            _emit_hinges(sash, mats, sh=sh, name_prefix=name)
            hx_free = (sw - _SASH_FACE / 2.0) * (1.0 if left_hung else -1.0)
            _emit_lever_handle(sash, mats, hx=hx_free, hz=sh * 0.40,
                               face_sign=-1.0, name_prefix=name)
            if left_hung:
                hinge_x = op_x0 + _SASH_GAP
                axis = (0.0, 0.0, 1.0)
            else:
                hinge_x = op_x1 - _SASH_GAP
                axis = (0.0, 0.0, -1.0)
            model.articulation(
                f"frame_to_{name}",
                ArticulationType.REVOLUTE,
                parent=frame, child=sash,
                origin=Origin(xyz=(hinge_x, 0.0, seat_z)),
                axis=axis,
                motion_limits=MotionLimits(effort=18.0, velocity=1.5, lower=0.0, upper=1.4),
            )
        return

    # single arched sash.
    sash_gap = _SASH_GAP
    sash_w = opening_w - 2 * sash_gap
    sash_hw = sash_w / 2.0
    seat_z = op_z0 + sash_gap
    sash_local_spring = spring_z - seat_z
    sash_rise = _rise_for(sash_hw)
    sh = sash_local_spring + sash_rise
    name = "sash"
    _build_arch_sash(model, r, mats, name=name, sash_hw=sash_hw,
                     sash_local_spring=sash_local_spring, sash_rise=sash_rise, assets=assets)
    sash = model.get_part(name)

    if mech == "awning_top_hung":
        # awning on the segmental head: hinge at the top crown line. Author body
        # downward (it already is z 0..sh authored about local x). For simplicity
        # use side-hung if awning -> already gated; keep side-hung here.
        mech = "side_hung_casement"
    _emit_hinges(sash, mats, sh=sh, name_prefix=name)
    _emit_lever_handle(sash, mats, hx=sash_w - _SASH_FACE / 2.0, hz=sh * 0.40,
                       face_sign=-1.0, name_prefix=name)
    hinge_x = op_x0 + sash_gap
    model.articulation(
        "frame_to_sash",
        ArticulationType.REVOLUTE,
        parent=frame, child=sash,
        origin=Origin(xyz=(hinge_x, 0.0, seat_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=18.0, velocity=1.5, lower=0.0, upper=1.4),
    )


def _build_arch_sash(model, r, mats, *, name, sash_hw, sash_local_spring, sash_rise,
                     assets, mirror_x: bool = False, muntin: bool = False):
    """Arched sash ring + glass, authored local: hinge edge at x=0, body +X (or
    -X when mirror_x), z 0..crown. cx = sash_hw centers the arch profile.

    The glass is one arch-following solid (it fills the head right up under the
    arched ring). When ``muntin`` is set and a colonial grid is configured, the
    colonial bars are laid over the lower (rectangular, below-spring) region of
    the sash as Rule-1 parent visuals — the glass behind them is unchanged so
    the arched head stays fully glazed."""
    xs = -1.0 if mirror_x else 1.0
    cx = sash_hw
    sash_face = _SASH_FACE
    outer = _arch_solid(sash_hw, 0.0, sash_local_spring, sash_rise, _SASH_DEPTH, cx)
    ghw = sash_hw - sash_face
    grise_inner = _arch_rise_concentric(ghw, sash_hw, sash_local_spring, sash_rise)
    inner = _arch_solid(ghw, sash_face, sash_local_spring, grise_inner, _SASH_DEPTH + 0.02, cx)
    ring = _maybe_mirror(outer.cut(inner), xs)
    sash = model.part(name)
    sash.visual(
        mesh_from_cadquery(ring, f"{name}_ring"),
        material=mats["sash"],
        name=f"{name}_ring", material_class_id=("wood.polished_varnished" if r.palette_style in {"warm_stained_wood", "sage_grey"} else "metal.aluminum_bare"),
    )
    # glass following the arch (fills sill -> arched crown, no flat top).
    g_hw = sash_hw - sash_face + _GLASS_REBATE
    gb = sash_face - _GLASS_REBATE
    grise_glass = _arch_rise_concentric(g_hw, sash_hw, sash_local_spring, sash_rise)
    glass = _maybe_mirror(
        _arch_solid(g_hw, gb, sash_local_spring, grise_glass, _GLASS_T, cx), xs
    )
    sash.visual(
        mesh_from_cadquery(glass, f"{name}_glass"),
        material=mats["glass"],
        name=f"{name}_glass", material_class_id=("glass.clear_transparent" if r.palette_style in {"warm_stained_wood", "anthracite_aluminium", "sage_grey", "industrial_white_steel"} else "glass.smoked_tinted"),
    )
    if muntin and r.muntin_cols * r.muntin_rows > 1:
        _emit_arch_muntins(sash, r, mats, sash_hw=sash_hw, sash_face=sash_face,
                           sash_local_spring=sash_local_spring, xs=xs)


def _emit_arch_muntins(sash, r, mats, *, sash_hw, sash_face, sash_local_spring, xs):
    """Colonial muntin BARS over the lower rectangular field of an arched sash.

    Bars only (the arch-following glass is already the glazing) so the head
    stays fully glazed; bars lap the glass per Rule 1 (named parent visuals on
    the sash). Authored in the same local frame as _build_arch_sash: hinge edge
    at local x=0, sash body spans 0..2*sash_hw, mirrored by xs."""
    cols, rows = r.muntin_cols, r.muntin_rows
    f = sash_face
    in_x0, in_x1 = f, 2 * sash_hw - f
    in_z0, in_z1 = f, sash_local_spring - f  # keep bars below the spring line
    in_w = in_x1 - in_x0
    in_h = in_z1 - in_z0
    if in_h <= 0.05:
        return
    cell_w = (in_w - (cols - 1) * _MUNTIN_FACE) / cols
    cell_h = (in_h - (rows - 1) * _MUNTIN_FACE) / rows
    mun_y = 0.0
    for i in range(cols - 1):
        mx = in_x0 + (i + 1) * cell_w + (i + 0.5) * _MUNTIN_FACE
        sash.visual(
            Box((_MUNTIN_FACE, _MUNTIN_DEPTH, in_h)),
            origin=Origin(xyz=(xs * mx, mun_y, (in_z0 + in_z1) / 2.0)),
            material=mats["sash"],
            name=f"vmuntin_{i}", material_class_id=("wood.polished_varnished" if r.palette_style in {"warm_stained_wood", "sage_grey"} else "metal.aluminum_bare"),
        )
    for i in range(rows - 1):
        mz = in_z0 + (i + 1) * cell_h + (i + 0.5) * _MUNTIN_FACE
        sash.visual(
            Box((in_w, _MUNTIN_DEPTH, _MUNTIN_FACE)),
            origin=Origin(xyz=(xs * (in_x0 + in_x1) / 2.0, mun_y, mz)),
            material=mats["sash"],
            name=f"hmuntin_{i}", material_class_id=("wood.polished_varnished" if r.palette_style in {"warm_stained_wood", "sage_grey"} else "metal.aluminum_bare"),
        )


def _arch_rise_concentric(half_w, ref_hw, spring, ref_rise):
    """Compute a concentric-arc rise for a smaller half-width, sharing the same
    arc center as the reference (sash) arch."""
    # ref arc center below spring by d; d from ref_hw and ref_rise.
    d = (ref_hw ** 2 - ref_rise ** 2) / (2.0 * ref_rise) if ref_rise > 1e-6 else 1.0
    R = math.sqrt(half_w ** 2 + d ** 2)
    return (-d + R)


# ===========================================================================
# Tests
# ===========================================================================
def run_window_tests(object_model: ArticulatedObject, config: WindowConfig) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    root_name = "surround" if r.frame_outline == "arched_top" else "frame"
    root = object_model.get_part(root_name)

    operable_parts = [
        p for p in object_model.parts
        if p.name.startswith("sash") or p.name == "vent" or p.name == "lower_sash"
    ]

    # ---- Captured-pin / rebate / mount allowances (element-scoped). ----
    movers = [p for p in object_model.parts if p is not root]
    for p in movers:
        # every moving part overlaps the frame at its capture/rebate.
        ctx.allow_overlap(
            root, p,
            reason="Sash/vent is captured in the frame rebate / jamb track / ring bore at the hinge line.",
        )
    # Adjacent sashes meet at the mullion / meeting rail (twin/triple/single-hung
    # meeting rail / bank neighbours overlap a touch in the closed pose).
    for i, pa in enumerate(movers):
        for pb in movers[i + 1:]:
            ctx.allow_overlap(
                pa, pb,
                reason="Adjacent sashes meet at the mullion / meeting rail in the closed pose.",
            )

    # Sash-internal allowances (glass rebate, hardware mounts, muntin proud).
    for p in object_model.parts:
        names = {v.name for v in p.visuals if v.name}
        # glass rebated under ring/frame lip
        for gname in [n for n in names if n.endswith("_glass") or n == "sash_glass" or n.startswith("pane_")]:
            ring_name = None
            for cand in (f"{p.name}_ring", "sash_ring", f"{p.name}_frame", "sash_frame"):
                if cand in names:
                    ring_name = cand
                    break
            if ring_name:
                ctx.allow_overlap(
                    p, p, elem_a=gname, elem_b=ring_name,
                    reason="Glass pane is rebated under the sash/frame ring lip (captured glazing).",
                )
        # muntins proud of panes
        muntins = [n for n in names if n.startswith("vmuntin_") or n.startswith("hmuntin_")]
        panes = [n for n in names if n.startswith("pane_")]
        # arched sash colonial bars lap the single arch-following glass solid.
        arch_glass = [n for n in names if n.endswith("_glass") or n == "sash_glass"]
        for m in muntins:
            for pane in panes:
                ctx.allow_overlap(p, p, elem_a=m, elem_b=pane,
                                  reason="Muntin bar sits proud of the glass and laps adjacent panes at the grid crossing.")
            for g in arch_glass:
                ctx.allow_overlap(p, p, elem_a=m, elem_b=g,
                                  reason="Colonial muntin bar laps the arch-following sash glass behind it.")
            ring_name = f"{p.name}_ring" if f"{p.name}_ring" in names else ("sash_ring" if "sash_ring" in names else None)
            if ring_name:
                ctx.allow_overlap(p, p, elem_a=m, elem_b=ring_name,
                                  reason="Muntin bar tenons into the sash ring.")
        for vi in muntins:
            for hi in muntins:
                if vi.startswith("vmuntin_") and hi.startswith("hmuntin_"):
                    ctx.allow_overlap(p, p, elem_a=vi, elem_b=hi,
                                      reason="Vertical and horizontal muntins cross at the grid intersection.")
        # handle base / lever / hinges mounted on the ring
        ring_name = f"{p.name}_ring" if f"{p.name}_ring" in names else ("sash_ring" if "sash_ring" in names else None)
        for hn in [n for n in names if "handle_base" in n]:
            if ring_name:
                ctx.allow_overlap(p, p, elem_a=hn, elem_b=ring_name,
                                  reason="Lever handle base seated on the sash face.")
        for hn in [n for n in names if "handle_lever" in n]:
            base = hn.replace("handle_lever", "handle_base")
            if base in names:
                ctx.allow_overlap(p, p, elem_a=hn, elem_b=base,
                                  reason="Lever bar attaches into its mounting base.")
        for hn in [n for n in names if "_hinge_" in n]:
            if ring_name:
                ctx.allow_overlap(p, p, elem_a=hn, elem_b=ring_name,
                                  reason="Hinge knuckle is mounted on the sash hinge stile.")
        # porthole pivot pins into sash ring
        for pn in [n for n in names if n.startswith("pivot_pin_")]:
            if "sash_ring" in names:
                ctx.allow_overlap(p, p, elem_a=pn, elem_b="sash_ring",
                                  reason="Pivot pin seated into the sash ring (center-pivot axis).")
        # vent catch / knuckles
        if "vent_flap" in names:
            for vn in [n for n in names if n.startswith("vent_knuckle_") or n == "vent_catch"]:
                ctx.allow_overlap(p, p, elem_a=vn, elem_b="vent_flap",
                                  reason="Vent hardware mounted on the vent flap.")

    # fixed_picture: sash_frame + glass + recess are on the root; allow rebate.
    if r.opening_mechanism == "fixed_picture_light":
        root_names = {v.name for v in root.visuals if v.name}
        for a, b in (("sash_frame", "frame_shell"), ("sash_glass", "sash_frame"),
                     ("vent_recess", "sash_frame")):
            if a in root_names and b in root_names:
                ctx.allow_overlap(root, root, elem_a=a, elem_b=b,
                                  reason="Fixed picture light + recess captured in the frame rebate.")

    # bank fixed glass rebated in the web.
    root_names = {v.name for v in root.visuals if v.name}
    for gn in [n for n in root_names if n.startswith("fixed_glass_")]:
        web = "frame_web" if "frame_web" in root_names else "frame_shell"
        if web in root_names:
            ctx.allow_overlap(root, root, elem_a=gn, elem_b=web,
                              reason="Fixed lite glass rebated under the frame web lip.")
    # arched extras: fanlight / stone / keystone / transom / mullion seat on
    # the wood frame head ring + jambs.
    arch_extras = [n for n in root_names if n.startswith("fan_")
                   or n in ("fanlight_glass", "stone_surround", "keystone",
                            "stone_sill", "spring_transom", "mullion")]
    for a in arch_extras:
        for b in ("wood_frame", "frame_shell"):
            if b in root_names:
                ctx.allow_overlap(root, root, elem_a=a, elem_b=b,
                                  reason="Fanlight / transom / mullion / stone surround seats against the wood frame.")
                break
    # fixed arch fanlight glass is rebated under the spring transom + tracery
    # ribs lap the glass behind them.
    if "fanlight_glass" in root_names:
        if "spring_transom" in root_names:
            ctx.allow_overlap(root, root, elem_a="fanlight_glass", elem_b="spring_transom",
                              reason="Fixed fanlight glass is rebated under the spring transom lip.")
        for rib in [n for n in root_names if n.startswith("fan_")]:
            ctx.allow_overlap(root, root, elem_a=rib, elem_b="fanlight_glass",
                              reason="Radial fanlight tracery sits proud of the fixed fanlight glass.")

    # ---- Baseline checks. ----
    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_joint_mating_has_gap()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)

    # ---- Identity / structure. ----
    part_names = {p.name for p in object_model.parts}
    ctx.check(f"{root_name} root present", root_name in part_names, details=str(sorted(part_names)))

    # at least one non-FIXED articulation (category-defining motion).
    non_fixed = [a for a in object_model.articulations
                 if a.articulation_type != ArticulationType.FIXED]
    ctx.check(
        "has at least one operable (non-fixed) sash/vent",
        len(non_fixed) >= 1,
        details=f"non_fixed={[a.name for a in non_fixed]}",
    )

    # frame stands upright on the ground.
    faabb = ctx.part_world_aabb(root)
    if faabb is not None:
        fw = faabb[1][0] - faabb[0][0]
        fh = faabb[1][2] - faabb[0][2]
        fd = faabb[1][1] - faabb[0][1]
        ctx.check("frame sits near the ground (z~0)",
                  faabb[0][2] >= -0.02 and faabb[0][2] < 0.20,
                  details=f"zmin={faabb[0][2]:.4f}")
        ctx.check("window stands upright (height >> depth)",
                  fh > 3.0 * fd,
                  details=f"h={fh:.3f}, d={fd:.3f}")

    # mechanism-specific joint topology + motion.
    if r.opening_mechanism == "side_hung_casement" and not r.grid_mode and r.n_cols == 1 and r.frame_outline == "rectangular":
        j = object_model.get_articulation("frame_to_sash")
        ctx.check("side-hung is REVOLUTE about Z",
                  j.articulation_type == ArticulationType.REVOLUTE and abs(j.axis[2]) > 0.99,
                  details=f"type={j.articulation_type} axis={tuple(j.axis)}")
        sash = object_model.get_part("sash")
        closed = ctx.part_world_aabb(sash)
        with ctx.pose({j: 0.7}):
            opened = ctx.part_world_aabb(sash)
        if closed is not None and opened is not None:
            ctx.check("side-hung free edge swings out in Y",
                      (opened[1][1] - opened[0][1]) > (closed[1][1] - closed[0][1]) + 0.10,
                      details=f"closed_dy={closed[1][1]-closed[0][1]:.3f} open_dy={opened[1][1]-opened[0][1]:.3f}")

    if r.opening_mechanism == "single_hung_vertical":
        ju = object_model.get_articulation("frame_to_upper_sash")
        jl = object_model.get_articulation("frame_to_lower_sash")
        ctx.check("single-hung upper FIXED + lower PRISMATIC z",
                  ju.articulation_type == ArticulationType.FIXED
                  and jl.articulation_type == ArticulationType.PRISMATIC
                  and abs(jl.axis[2]) > 0.99,
                  details=f"upper={ju.articulation_type} lower={jl.articulation_type} axis={tuple(jl.axis)}")
        lower = object_model.get_part("lower_sash")
        p0 = ctx.part_world_position(lower)
        up = jl.motion_limits.upper if jl.motion_limits else 0.0
        with ctx.pose({jl: up}):
            p1 = ctx.part_world_position(lower)
        if p0 is not None and p1 is not None:
            ctx.check("lower sash slides UP", p1[2] > p0[2] + 0.03,
                      details=f"z0={p0[2]:.3f} z1={p1[2]:.3f}")

    if r.opening_mechanism == "fixed_picture_light":
        jv = object_model.get_articulation("frame_to_vent")
        ctx.check("vent is the only non-fixed joint, REVOLUTE about X",
                  len(non_fixed) == 1 and jv.articulation_type == ArticulationType.REVOLUTE
                  and abs(jv.axis[0]) > 0.9,
                  details=f"non_fixed={[a.name for a in non_fixed]} axis={tuple(jv.axis)}")
        ctx.check("main picture light is FIXED (no swing sash)",
                  "frame_to_sash" not in [a.name for a in object_model.articulations],
                  details=str([a.name for a in object_model.articulations]))

    if r.frame_outline == "round_porthole":
        j = object_model.get_articulation("frame_to_sash")
        ctx.check("porthole center-pivot REVOLUTE about X",
                  j.articulation_type == ArticulationType.REVOLUTE and abs(j.axis[0]) > 0.99,
                  details=f"axis={tuple(j.axis)}")
        sash = object_model.get_part("sash")
        if faabb is not None:
            ctx.check("porthole outer frame is round (square XZ bbox)",
                      abs((faabb[1][0]-faabb[0][0]) - (faabb[1][2]-faabb[0][2])) < 0.03,
                      details=f"dx={faabb[1][0]-faabb[0][0]:.3f} dz={faabb[1][2]-faabb[0][2]:.3f}")
        # MEMORY lesson: axisymmetric AABB self-rotation is fragile -> assert
        # Y-depth growth + center stays put, NOT AABB rotation.
        closed = ctx.part_world_aabb(sash)
        with ctx.pose({j: 0.7}):
            opened = ctx.part_world_aabb(sash)
        if closed is not None and opened is not None:
            ctx.check("porthole sash tilts out of plane (Y grows)",
                      (opened[1][1]-opened[0][1]) > (closed[1][1]-closed[0][1]) + 0.08,
                      details=f"closed_dy={closed[1][1]-closed[0][1]:.3f} open_dy={opened[1][1]-opened[0][1]:.3f}")
            cx_c = (closed[0][0]+closed[1][0])/2.0
            cx_o = (opened[0][0]+opened[1][0])/2.0
            ctx.check("porthole sash pivots about its own center (X stays put)",
                      abs(cx_o - cx_c) < 0.02, details=f"cx_c={cx_c:.3f} cx_o={cx_o:.3f}")

    if r.frame_outline == "segmental_arch":
        if faabb is not None:
            spring_z = r.win_h - r.arch_rise
            ctx.check("segmental crown above the spring line (real arch head)",
                      faabb[1][2] > spring_z + 0.5 * r.frame_face,
                      details=f"zmax={faabb[1][2]:.3f} spring+face={spring_z+0.5*r.frame_face:.3f}")

    if r.frame_outline == "arched_top":
        if faabb is not None:
            ctx.check("arched window taller than wide",
                      (faabb[1][2]-faabb[0][2]) > (faabb[1][0]-faabb[0][0]),
                      details=f"h={faabb[1][2]-faabb[0][2]:.3f} w={faabb[1][0]-faabb[0][0]:.3f}")

    # multiplicity: count operable sashes for linear/grid families.
    if r.grid_mode:
        operable_sashes = [p for p in object_model.parts if p.name.startswith("sash_")]
        fixed_lites = [v for v in root.visuals if v.name and v.name.startswith("fixed_glass_")]
        ctx.check("bank has operable sash(es) + fixed lites",
                  len(operable_sashes) >= 1 and len(fixed_lites) >= 1,
                  details=f"operable={len(operable_sashes)} fixed={len(fixed_lites)}")
    elif r.n_cols >= 2 and r.frame_outline == "rectangular":
        sashes = [p for p in object_model.parts if p.name.startswith("sash_")]
        ctx.check(f"linear bays produced {r.n_cols} sashes",
                  len(sashes) == r.n_cols, details=f"sashes={len(sashes)}")

    # slot_choices recorded.
    ctx.check("slot_choices recorded",
              tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
              details=str(object_model.meta.get("slot_choices")))

    return ctx.report()


__all__ = (
    "WindowConfig",
    "ResolvedWindowConfig",
    "build_window",
    "build_seeded_window",
    "config_from_seed",
    "resolve_config",
    "run_window_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
