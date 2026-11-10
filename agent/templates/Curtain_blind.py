# SPDX-License-Identifier: Apache-2.0

"""Window blind (Curtain/blind) modular template.

Sourced from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/Curtain_blind.md`` and the
``picture/Curtain/blind`` 5-star sample pool (2 parents + 6 fork variants),
all synced under ``data/records/``.

Identity: a window blind hangs from a single root ``headrail`` (the only root
part); a repeated shade layer (slats / vanes / folds / cells, or a single
roller sheet) hangs below it and opens/closes via lift / tilt / traverse.

Slot graph (pattern = ``mixed``: headrail root + parallel shade panel; the
shade panel slot copies its sub-parts via a multiplicity axis):

  * Slot A ``shade_topology`` (5): horizontal_venetian / vertical_vanes /
    roller_shade / roman_folds / cellular_honeycomb. Each is a structurally
    distinct part-tree + joint-topology ported from its own 5-star source:
      - venetian (S1, parent A): headrail + bottom_rail lift master +
        N (slat_carrier + slat blade): PRISMATIC lift mimic + REVOLUTE tilt
        mimic (lift + tilt double DOF).
      - vertical (S2, parent B): headrail + carrier_train(s) traverse +
        N vane (REVOLUTE Z tilt mimic). No lift / no bottom rail.
      - roller (S3): headrail + hollow CadQuery roller_tube (REVOLUTE X) +
        bottom_bar (independent PRISMATIC lift) + single mesh sheet. Fixed 1.
      - roman (S4): headrail + bottom_rail lift + N sinusoidal-bulge mesh fold
        (PRISMATIC lift mimic, no tilt).
      - cellular (S5): headrail + bottom_rail lift + N hex ExtrudeGeometry cell
        (shared mesh asset, PRISMATIC lift mimic, no tilt).
  * Slot C ``traverse_policy`` (2): single_stack (all) / center_split_vertical
    (vertical only — splits the vane set into left/right carrier trains that
    traverse outward, leaving a center gap; S8).
  * Slot B count axis (conditional multiplicity): slat_count [12,40] (venetian
    only) / vane_count [12,28] even when split (vertical only) / fold_count
    [4,9] (roman) / cell_count [16,40] (cellular) / 1 (roller). N is encoded
    into ``slot_choices_for_seed`` as ``("count", f"n{N}")`` so the
    ``module_topology_diversity`` gate counts it.

Three hard rules:
  1. Non-moving decorations (ladder tapes, cord strips, cord guides, cord lock,
     pull cords, tassels, tilt wand, brackets, end caps, chain boss) are
     ``headrail.visual(...)`` — never FIXED parts.
  2. Every non-FIXED joint that creates a separate child part anchors to real
     visible parent geometry; captured-pin / sliding-rail / lift-carrier joints
     whose two faces are not axis-aligned-in-contact omit ``MatingContract``
     (grandfathered) and rely on the flat articulation-origin baseline +
     element-scoped allow_overlap (mirroring each source's run_tests).
  3. Geometry derived from the 5-star sources: lathe/Box slats, CadQuery hollow
     roller tube, sinusoidal-bulge fold mesh, hex ExtrudeGeometry cell — no
     downgrade to crude placeholders.

Per-seed palette: ``palette_style`` (5 colorways from the spec) is sampled per
seed and drives every ``.visual(material=...)``.
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
    ExtrudeGeometry,
    MeshGeometry,
    Mimic,
    MotionLimits,
    Origin,
    Sphere,
    TestContext,
    TestReport,
    mesh_from_cadquery,
    mesh_from_geometry,
)

__modular__ = True

ShadeTopology = Literal[
    "horizontal_venetian",
    "vertical_vanes",
    "roller_shade",
    "roman_folds",
    "cellular_honeycomb",
]
TraversePolicy = Literal["single_stack", "center_split_vertical"]
PaletteStyle = Literal[
    "wood_dark",
    "wood_natural",
    "white_pvc",
    "grey_fabric",
    "cream_cellular",
]

SHADE_TOPOLOGIES: tuple[ShadeTopology, ...] = (
    "horizontal_venetian",
    "vertical_vanes",
    "roller_shade",
    "roman_folds",
    "cellular_honeycomb",
)
# Slightly weight the two parents (venetian/vertical) up; all 5 reachable.
_TOPOLOGY_WEIGHTS = (2.4, 2.0, 1.0, 1.3, 1.3)

PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "wood_dark",
    "wood_natural",
    "white_pvc",
    "grey_fabric",
    "cream_cellular",
)

# palette_style -> material rgba tokens (measured from the 5-star sources).
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "wood_dark": {
        "rail": (0.20, 0.135, 0.09, 1.0),
        "shade": (0.23, 0.155, 0.105, 1.0),
        "accent": (0.72, 0.60, 0.44, 1.0),
        "cord": (0.66, 0.55, 0.40, 1.0),
        "tassel": (0.23, 0.155, 0.105, 1.0),
    },
    "wood_natural": {
        "rail": (0.55, 0.42, 0.30, 1.0),
        "shade": (0.93, 0.89, 0.82, 1.0),
        "accent": (0.88, 0.82, 0.72, 1.0),
        "cord": (0.88, 0.82, 0.72, 1.0),
        "tassel": (0.52, 0.40, 0.28, 1.0),
    },
    "white_pvc": {
        "rail": (0.38, 0.24, 0.15, 1.0),
        "shade": (0.93, 0.89, 0.82, 1.0),
        "accent": (0.62, 0.62, 0.65, 1.0),
        "cord": (0.66, 0.55, 0.40, 1.0),
        "tassel": (0.50, 0.50, 0.53, 1.0),
    },
    "grey_fabric": {
        "rail": (0.78, 0.79, 0.80, 1.0),
        "shade": (0.45, 0.45, 0.46, 1.0),
        "accent": (0.72, 0.73, 0.74, 1.0),
        "cord": (0.72, 0.73, 0.74, 1.0),
        "tassel": (0.05, 0.05, 0.055, 1.0),
    },
    "cream_cellular": {
        "rail": (0.20, 0.135, 0.09, 1.0),
        "shade": (0.91, 0.86, 0.76, 1.0),
        "accent": (0.66, 0.55, 0.40, 1.0),
        "cord": (0.66, 0.55, 0.40, 1.0),
        "tassel": (0.23, 0.155, 0.105, 1.0),
    },
}

# ---------------------------------------------------------------------------
# Multiplicity domains (count axis). Per spec §8: test biased small, product
# full range; small N dominates the per-N weighted draw.
# ---------------------------------------------------------------------------
SLAT_MIN, SLAT_MAX = 12, 40
VANE_MIN, VANE_MAX = 12, 28
FOLD_MIN, FOLD_MAX = 4, 9
CELL_MIN, CELL_MAX = 16, 40

# ---------------------------------------------------------------------------
# Base real-world dimensions (meters). Scaled per build by width/drop scale.
# ---------------------------------------------------------------------------
# Horizontal family (venetian / roman / cellular): vertical lift + tilt spine.
_H_BLIND_WIDTH = 0.80
_H_HEADRAIL_DEPTH = 0.062
_H_HEADRAIL_HEIGHT = 0.060
_H_HEADRAIL_Z = 1.27  # center; spans 1.24 .. 1.30
_H_TOP_SHADE_Z = 1.215  # top sub-part center when lowered
_H_BOTTOM_RAIL_Z = 0.068
_H_TAPE_STATIONS = (-0.20, 0.20)
_H_RAIL_GATHER_GAP = 0.006

# Vertical family: horizontal traverse + Z tilt spine.
_V_VANE_WIDTH = 0.089
_V_VANE_THICKNESS = 0.0025
_V_VANE_DROP = 2.0
_V_VANE_STAGGER = 0.0017
_V_RAIL_DEPTH = 0.045
_V_RAIL_HEIGHT = 0.045
_V_RAIL_BOTTOM_Z = 2.080
_V_STEM_BOTTOM_Z = 2.056
_V_TILT_LIMIT = 1.5708
_V_TRAVERSE_LIMIT = 0.045
_V_SPLIT_TRAVERSE_LIMIT = 0.050
_V_CHAIN_X = -0.78
_V_CHAIN_Y = -0.035
_V_CHAIN_TOP_Z = 2.066
_V_CHAIN_LENGTH = 1.16

# Roller.
_R_ROLLER_RADIUS = 0.022
_R_ROLLER_WALL = 0.004
_R_ROLLER_Z = 1.214
_R_SHADE_THICK = 0.003
_R_SHADE_BOTTOM_Z = 0.080
_R_BOTTOM_BAR_DEPTH = 0.032
_R_BOTTOM_BAR_HEIGHT = 0.020
_R_WRAP_THICK = 0.006
_R_SHADE_TRAVEL = 0.55

_VENETIAN_TILT_LIMIT = 1.3


# ---------------------------------------------------------------------------
# Config dataclasses
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class WindowBlindConfig:
    shade_topology: ShadeTopology | None = None
    traverse_policy: TraversePolicy | None = None
    count: int | None = None
    palette_style: PaletteStyle = "wood_dark"
    blind_width_scale: float = 1.0
    drop_scale: float = 1.0
    name: str = "window_blind"


@dataclass(frozen=True)
class ResolvedWindowBlindConfig:
    shade_topology: ShadeTopology
    traverse_policy: TraversePolicy
    count: int
    palette_style: PaletteStyle
    blind_width_scale: float
    drop_scale: float
    name: str


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


def _count_domain(topology: ShadeTopology) -> tuple[int, int]:
    if topology == "horizontal_venetian":
        return SLAT_MIN, SLAT_MAX
    if topology == "vertical_vanes":
        return VANE_MIN, VANE_MAX
    if topology == "roman_folds":
        return FOLD_MIN, FOLD_MAX
    if topology == "cellular_honeycomb":
        return CELL_MIN, CELL_MAX
    return 1, 1  # roller_shade: fixed single sheet


def _draw_count(rng: random.Random, topology: ShadeTopology) -> int:
    """Per-N weighted integer draw: small N dominates, dense tail is rare."""
    lo, hi = _count_domain(topology)
    if lo == hi:
        return lo
    values = tuple(range(lo, hi + 1))
    nominal = {
        "horizontal_venetian": 30,
        "vertical_vanes": 20,
        "roman_folds": 6,
        "cellular_honeycomb": 30,
    }[topology]
    span = hi - lo
    weights = []
    for n in values:
        # Triangular-ish weight peaking near nominal, tail toward hi downweighted.
        d = abs(n - nominal) / span
        w = max(0.08, 1.0 - 1.3 * d)
        if n > nominal:
            w *= 0.5  # high-density end rarer
        weights.append(w)
    return rng.choices(values, weights=weights, k=1)[0]


def config_from_seed(seed: int) -> WindowBlindConfig:
    rng = random.Random(seed)
    topology = rng.choices(SHADE_TOPOLOGIES, weights=_TOPOLOGY_WEIGHTS, k=1)[0]

    # Slot C: center_split only valid with vertical vanes; else single_stack.
    if topology == "vertical_vanes" and rng.random() < 0.45:
        traverse_policy: TraversePolicy = "center_split_vertical"
    else:
        traverse_policy = "single_stack"

    count = _draw_count(rng, topology)
    # center_split needs an even vane_count (left/right split evenly).
    if traverse_policy == "center_split_vertical" and count % 2 == 1:
        count = min(count + 1, VANE_MAX)
        if count % 2 == 1:
            count -= 1

    return WindowBlindConfig(
        shade_topology=topology,
        traverse_policy=traverse_policy,
        count=count,
        palette_style=rng.choice(PALETTE_STYLES),
        blind_width_scale=round(rng.uniform(0.85, 1.20), 4),
        drop_scale=round(rng.uniform(0.80, 1.15), 4),
        name=f"seeded_window_blind_{seed}",
    )


def resolve_config(config: WindowBlindConfig | None = None) -> ResolvedWindowBlindConfig:
    cfg = config or WindowBlindConfig()
    topology = _pick(cfg.shade_topology, SHADE_TOPOLOGIES)
    traverse_policy = _pick(cfg.traverse_policy, ("single_stack", "center_split_vertical"))
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)

    # Compatibility matrix: center_split strictly bound to vertical_vanes.
    if topology != "vertical_vanes":
        traverse_policy = "single_stack"

    lo, hi = _count_domain(topology)
    nominal = {
        "horizontal_venetian": 30,
        "vertical_vanes": 20,
        "roller_shade": 1,
        "roman_folds": 6,
        "cellular_honeycomb": 30,
    }[topology]
    count = int(cfg.count) if cfg.count is not None else nominal
    count = int(_clamp(count, lo, hi))
    if traverse_policy == "center_split_vertical" and count % 2 == 1:
        count = min(count + 1, hi)
        if count % 2 == 1:
            count -= 1

    width_scale = _clamp(cfg.blind_width_scale, 0.85, 1.20)
    drop_scale = _clamp(cfg.drop_scale, 0.80, 1.15)

    return ResolvedWindowBlindConfig(
        shade_topology=topology,
        traverse_policy=traverse_policy,
        count=count,
        palette_style=palette_style,
        blind_width_scale=width_scale,
        drop_scale=drop_scale,
        name=cfg.name or "window_blind",
    )


def with_overrides(config: WindowBlindConfig, **kwargs: object) -> WindowBlindConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: WindowBlindConfig | ResolvedWindowBlindConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedWindowBlindConfig) else resolve_config(config)
    return (
        ("shade_topology", r.shade_topology),
        ("traverse_policy", r.traverse_policy),
        ("count", f"n{r.count}"),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ===========================================================================
# Geometry helpers (ported from the 5-star sources)
# ===========================================================================
def _roman_fold_panel(
    width: float, height: float, depth: float, thickness: float = 0.004, n_curve: int = 14
) -> MeshGeometry:
    """Sinusoidal-bulge roman fold panel (source S4 _roman_fold_panel L103-152).

    Width along X, height along Z, forward bulge along +Y. Front face has a
    smooth sinusoidal bulge (the visible fold rib); back face flat; two end caps.
    """
    mesh = MeshGeometry()
    hw, hh = width / 2.0, height / 2.0

    profile: list[tuple[float, float]] = []
    for i in range(n_curve + 1):
        t = i / n_curve
        z = hh * (1.0 - 2.0 * t)
        y = depth * math.sin(t * math.pi)
        profile.append((y, z))
    profile.append((-thickness, -hh))
    profile.append((-thickness, hh))

    n = len(profile)
    for y, z in profile:
        mesh.add_vertex(-hw, y, z)
    for y, z in profile:
        mesh.add_vertex(hw, y, z)
    for i in range(n):
        j = (i + 1) % n
        mesh.add_face(i, j, n + j)
        mesh.add_face(i, n + j, n + i)
    lc = mesh.add_vertex(-hw, -thickness / 2.0, 0.0)
    for i in range(n):
        j = (i + 1) % n
        mesh.add_face(lc, j, i)
    rc = mesh.add_vertex(hw, -thickness / 2.0, 0.0)
    for i in range(n):
        j = (i + 1) % n
        mesh.add_face(rc, n + i, n + j)
    return mesh


def _honeycomb_cell(width: float, depth: float, height: float):
    """Hexagonal-cross-section prism along X (source S5 make_honeycomb_cell L98-122)."""
    hw = depth * 0.30
    hd = depth * 0.50
    hh = height * 0.50
    profile = [
        (-hw, hh),
        (hw, hh),
        (hd, 0.0),
        (hw, -hh),
        (-hw, -hh),
        (-hd, 0.0),
    ]
    geom = ExtrudeGeometry(profile, width, cap=True, center=True)
    geom.rotate(axis=(1.0, 1.0, 1.0), angle=2.0 * math.pi / 3.0)
    return geom


def _roller_tube_solid(radius: float, wall: float, length: float):
    """Hollow CadQuery roller tube along Z (rotated to X by visual origin)."""
    outer = radius
    inner = radius - wall
    half_len = length / 2.0
    return (
        cq.Workplane("XY")
        .transformed(offset=(0.0, 0.0, -half_len))
        .circle(outer)
        .circle(inner)
        .extrude(length)
    )


def _roller_sheet_solid(width: float, thick: float, height: float):
    return cq.Workplane("XY").box(width, thick, height)


def _roller_ridge_solid(width: float, depth: float):
    return cq.Workplane("XY").box(width, depth, 0.008)


# ===========================================================================
# Shared headrail control decorations (Rule 1: all headrail visuals)
# ===========================================================================
def _add_horizontal_cord_lock(headrail, mats, *, with_tassels=True):
    """Cord lock + two pull cords + tassels on the front-right of the headrail."""
    # Cord lock + its dangling pull cords/tassels sit in FRONT (+y) of the shade
    # so the raised bottom rail (front face reaches y=0.035) and the deepest slat
    # (front y=0.040) pass behind them: the tassel back face at y=0.043 clears
    # both. All are headrail visuals (one rigid part), so the forward offset is
    # purely a clearance move.
    headrail.visual(
        Box((0.07, 0.024, 0.030)),
        origin=Origin(xyz=(0.32, 0.041, 1.252)),
        material=mats["rail"],
        name="cord_lock", material_class_id="plastic.opaque_glossy_molded",
    )
    for cord_x, idx in ((0.305, 0), (0.335, 1)):
        cord_top = 1.260
        cord_bottom = 0.500
        headrail.visual(
            Cylinder(radius=0.0022, length=cord_top - cord_bottom),
            origin=Origin(xyz=(cord_x, 0.051, 0.5 * (cord_top + cord_bottom))),
            material=mats["cord"],
            name=f"lift_cord_{idx}", material_class_id="fabric.thread_yarn",
        )
        if with_tassels:
            headrail.visual(
                Cylinder(radius=0.008, length=0.055),
                origin=Origin(xyz=(cord_x, 0.051, 0.475)),
                material=mats["tassel"],
                name=f"cord_tassel_{idx}", material_class_id="plastic.opaque_glossy_molded",
            )


# ===========================================================================
# Slot A / horizontal lift stack (venetian / roman / cellular share this spine)
# ===========================================================================
def _horizontal_geom(
    r: ResolvedWindowBlindConfig,
    count: int,
    sub_height: float,
    stack_pitch: float,
    support_y_half: float = 0.0,
    end_clearance: float = 0.0,
):
    """Derive lift geometry for a horizontal (lift) shade with `count` sub-parts.

    Returns (open_pitch, top_z, headrail_size, bottom_rail_size, rail_travel,
    down_z(i), up_z(i)) helpers. bottom-led gather, stack tops just under rail.

    ``end_clearance`` is extra vertical head/foot room reserved at BOTH ends of
    the stack so a sub-part that ROTATES (venetian slat tilt) cannot sweep its
    swung half-extent into the headrail box (top slat) or bottom rail (bottom
    slat) at either lift extreme. Single source: callers derive it from the
    tilted half-height (0.5·depth·sin θ + 0.5·thickness·cos θ) and pass it once;
    non-tilting shades (roman / cellular) leave it 0.
    """
    width = _H_BLIND_WIDTH * r.blind_width_scale
    headrail_size = (width, _H_HEADRAIL_DEPTH, _H_HEADRAIL_HEIGHT)
    sub_width = width - 0.02

    # Bottom rail depth (Y) spans under both support stations so the ladder
    # tapes / cord strips / guides always land on it (geometric support path
    # for fail_if_isolated_parts), regardless of slat depth.
    rail_depth = max(0.055, 2.0 * support_y_half + 0.014)
    rail_height = 0.022
    bottom_rail_size = (sub_width, rail_depth, rail_height)
    headrail_bottom_z = _H_HEADRAIL_Z - 0.5 * _H_HEADRAIL_HEIGHT  # 1.240
    sub_half = 0.5 * sub_height

    # The shade is sized to its window: the TOP sub-part hangs just under the
    # headrail, the bottom rail floats down to whatever depth the N sub-parts
    # need. This keeps tall/dense stacks (9 folds, 40 cells) physically valid —
    # a bigger blind is simply a taller window, not an overlapping stack.
    top_z = headrail_bottom_z - sub_half - 0.02 - end_clearance  # top lowered center

    nseg = max(count - 1, 1)
    # The blind covers a real window (~1.1 m drop, scaled). Pitch = drop / N,
    # clamped so adjacent sub-parts never overlap vertically (>= sub height +
    # gap) and never exceed a sensible max. For many thin slats the pitch is
    # small but the total drop stays ~window height; for a few tall folds the
    # pitch is large (non-overlapping) and the drop grows with N.
    min_open_pitch = max(stack_pitch + 0.004, sub_height + 0.006)
    max_open_pitch = max(0.105, sub_height + 0.060)
    target_drop = 1.10 * r.drop_scale
    open_pitch = _clamp(target_drop / nseg, min_open_pitch, max_open_pitch)
    # Bottom sub-part lowered center, then the bottom rail just below it.
    bottom_down_z = top_z - nseg * open_pitch
    clearance = sub_half + _H_RAIL_GATHER_GAP + 0.5 * rail_height + end_clearance
    bottom_rail_z = bottom_down_z - (sub_half + 0.014 + end_clearance + 0.5 * rail_height)

    # Gathered stack: tight stack_pitch spacing, tops just under the headrail.
    stack_top_z = top_z + 0.010

    def down_z(i: int) -> float:
        return top_z - (i - 1) * open_pitch

    def up_z(i: int) -> float:
        return stack_top_z - (i - 1) * stack_pitch

    rail_up_z = up_z(count) - clearance
    rail_travel = rail_up_z - bottom_rail_z

    return {
        "width": width,
        "sub_width": sub_width,
        "headrail_size": headrail_size,
        "bottom_rail_size": bottom_rail_size,
        "top_z": top_z,
        "bottom_rail_z": bottom_rail_z,
        "open_pitch": open_pitch,
        "rail_travel": rail_travel,
        "down_z": down_z,
        "up_z": up_z,
    }


def _build_horizontal_headrail(model, r, mats, geom, *, support_kind: str, tape_y: float = 0.0280):
    """Headrail box + vertical support strips/guides + cord lock (Rule 1 visuals).

    support_kind: 'tape' (venetian ladder tape), 'strip' (roman cord strip),
    'guide' (cellular cord guide). ``tape_y`` places the front/rear ladder tape
    so the slat edge embeds it 0.5 mm regardless of slat depth. Returns the
    headrail part.
    """
    headrail = model.part("headrail")
    headrail.visual(
        Box(geom["headrail_size"]),
        origin=Origin(xyz=(0.0, 0.0, _H_HEADRAIL_Z)),
        material=mats["rail"],
        name="headrail_box", material_class_id=("metal.paint_coated" if r.palette_style in {"wood_dark", "wood_natural", "grey_fabric", "cream_cellular"} else "plastic.opaque_glossy_molded"),
    )

    bottom_rail_z = geom["bottom_rail_z"]
    # Vertical support stations span headrail bottom down into bottom rail range.
    sup_top_z = _H_HEADRAIL_Z
    sup_bottom_z = bottom_rail_z - 0.006
    sup_len = sup_top_z - sup_bottom_z
    sup_mid_z = 0.5 * (sup_top_z + sup_bottom_z)

    # Center lift-cord spine at x=0 running the full drop. Every per-sub-part
    # lift joint origin (at x=0, z=down_z(i)) lands on this headrail geometry,
    # so the articulation-origin baseline (tol=0.015) is satisfied. It is a real
    # blind element (the central pull cord) and a Rule-1 headrail visual.
    headrail.visual(
        Cylinder(radius=0.0022, length=sup_len),
        origin=Origin(xyz=(0.0, 0.0, sup_mid_z)),
        material=mats["cord"],
        name="center_lift_cord", material_class_id="fabric.thread_yarn",
    )

    for station_x, side in zip(_H_TAPE_STATIONS, ("a", "b")):
        if support_kind == "tape":
            # Ladder tapes: front + rear strips straddling the slat edge so the
            # slat embeds each tape ~0.5 mm (physical-contact support).
            for ty, face in ((tape_y, "front"), (-tape_y, "rear")):
                headrail.visual(
                    Box((0.024, 0.002, sup_len)),
                    origin=Origin(xyz=(station_x, ty, sup_mid_z)),
                    material=mats["accent"],
                    name=f"ladder_tape_{side}_{face}", material_class_id="fabric.webbing",
                )
        elif support_kind == "strip":
            headrail.visual(
                Box((0.006, 0.002, sup_len)),
                origin=Origin(xyz=(station_x, -0.0045, sup_mid_z)),
                material=mats["accent"],
                name=f"lift_cord_strip_{side}", material_class_id="fabric.webbing",
            )
        else:  # guide
            headrail.visual(
                Cylinder(radius=0.002, length=sup_len),
                origin=Origin(xyz=(station_x, 0.0, sup_mid_z)),
                material=mats["accent"],
                name=f"cord_guide_{side}", material_class_id="fabric.thread_yarn",
            )

    _add_horizontal_cord_lock(headrail, mats)

    # Tilt wand only meaningful for venetian; added by venetian builder.
    return headrail


def _build_horizontal_bottom_rail(model, headrail, r, mats, geom):
    bottom_rail = model.part("bottom_rail")
    bottom_rail.visual(
        Box(geom["bottom_rail_size"]),
        origin=Origin(),
        material=mats["rail"],
        name="bottom_rail_bar", material_class_id=("metal.paint_coated" if r.palette_style in {"wood_dark", "wood_natural", "grey_fabric", "cream_cellular"} else "plastic.opaque_glossy_molded"),
    )
    model.articulation(
        "lift",
        ArticulationType.PRISMATIC,
        parent=headrail,
        child=bottom_rail,
        origin=Origin(xyz=(0.0, 0.0, geom["bottom_rail_z"])),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=80.0, velocity=0.5, lower=0.0, upper=geom["rail_travel"]),
    )
    return bottom_rail


def _emit_lift_mimic(model, headrail, child, geom, i, name):
    """Emit a PRISMATIC lift carrier joint mimicking master `lift`, bottom-led."""
    disp = geom["up_z"](i) - geom["down_z"](i)
    lift_mult = disp / geom["rail_travel"]
    model.articulation(
        name,
        ArticulationType.PRISMATIC,
        parent=headrail,
        child=child,
        origin=Origin(xyz=(0.0, 0.0, geom["down_z"](i))),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=20.0, velocity=0.5, lower=0.0, upper=disp),
        mimic=Mimic(joint="lift", multiplier=lift_mult, offset=0.0),
    )


def _build_venetian(model, r, mats):
    # Thin aluminium-style slat. A slat tilted to θ=±_VENETIAN_TILT_LIMIT
    # presents a body whose surfaces are only sub_height thick perpendicular to
    # its plane; two adjacent slats stacked Δz apart clear as solids only when
    # Δz·cos θ > sub_height. At θ=1.3 (cos≈0.27) a 3 mm slat would need a 12 mm
    # stack pitch (tall gathered stack → short stroke), so the slat is thinned
    # to 1.5 mm — realistic for a metal venetian — which the derived stack pitch
    # below then packs safely.
    sub_height = 0.0015  # slat thickness (Z)
    # Sparser blinds use wider (deeper) slats, denser blinds narrower — matches
    # the slat_12 (0.080) / parent (0.055) / slat_40 (0.040) 5-star endpoints.
    slat_depth = _clamp(0.040 + (40 - r.count) / (40 - 12) * 0.040, 0.040, 0.080)
    # Ladder tape stays under the headrail box (y within the box half-depth) so
    # its top is buried in the box (intra-part connectivity) while the (wider)
    # slat still embeds it for physical-contact support.
    box_half_depth = 0.5 * _H_HEADRAIL_DEPTH
    tape_y = min(0.5 * slat_depth, box_half_depth - 0.003)
    # A slat tilted to ±_VENETIAN_TILT_LIMIT swings its (deep) profile through
    # this vertical half-extent about the slat center. Reserve it as head/foot
    # clearance so the top slat can't rotate up into the headrail box and the
    # bottom slat can't rotate down into the bottom rail at either lift extreme.
    tilt_reach = (
        0.5 * slat_depth * math.sin(_VENETIAN_TILT_LIMIT)
        + 0.5 * sub_height * math.cos(_VENETIAN_TILT_LIMIT)
        + 0.002
    )
    # Gathered (raised) stack pitch derived so fully-tilted neighbouring slats
    # keep a ~2 mm face gap (single source for the no-interpenetration rule):
    # pitch·cos θ − sub_height ≥ 0.002. Spacing is monotonic between open_pitch
    # (>= this) and this pitch, so the guarantee holds through the whole lift.
    stack_pitch = (sub_height + 0.002) / math.cos(_VENETIAN_TILT_LIMIT)
    geom = _horizontal_geom(
        r, r.count, sub_height, stack_pitch, support_y_half=tape_y, end_clearance=tilt_reach
    )
    headrail = _build_horizontal_headrail(
        model,
        r,
        mats,
        geom,
        support_kind="tape",
        tape_y=tape_y,
    )

    # Tilt wand on the front-left of the headrail (Rule 1 visual). Held clear in
    # FRONT (+y) of the slat stack and the raised bottom rail: the deepest slat
    # reaches y=0.040 and the widest rail front y=0.035, so the wand back face
    # (y=0.044) clears both — the hook bridges it back to the headrail box.
    headrail.visual(
        Box((0.018, 0.031, 0.024)),
        origin=Origin(xyz=(-0.34, 0.0405, 1.250)),
        material=mats["rail"],
        name="wand_hook", material_class_id=("metal.paint_coated" if r.palette_style in {"wood_dark", "wood_natural", "grey_fabric", "cream_cellular"} else "plastic.opaque_glossy_molded"),
    )
    headrail.visual(
        Cylinder(radius=0.006, length=0.550),
        origin=Origin(xyz=(-0.34, 0.050, 0.980)),
        material=mats["cord"],
        name="tilt_wand", material_class_id="plastic.opaque_glossy_molded",
    )

    _build_horizontal_bottom_rail(model, headrail, r, mats, geom)

    tilt_limits = MotionLimits(
        effort=2.0, velocity=2.0, lower=-_VENETIAN_TILT_LIMIT, upper=_VENETIAN_TILT_LIMIT
    )
    for i in range(1, r.count + 1):
        carrier = model.part(f"slat_carrier_{i:02d}")  # invisible lift stage
        _emit_lift_mimic(model, headrail, carrier, geom, i, f"slat_lift_{i:02d}")

        blade = model.part(f"slat_{i:02d}")
        blade.visual(
            Box((geom["sub_width"], slat_depth, sub_height)),
            origin=Origin(),
            material=mats["shade"],
            name=f"slat_{i:02d}_blade", material_class_id=("metal.paint_coated" if r.palette_style in {"wood_dark", "wood_natural", "grey_fabric", "cream_cellular"} else "plastic.opaque_glossy_molded"),
        )
        tilt_name = "slat_tilt" if i == 1 else f"slat_tilt_{i:02d}"
        model.articulation(
            tilt_name,
            ArticulationType.REVOLUTE,
            parent=carrier,
            child=blade,
            origin=Origin(),
            axis=(1.0, 0.0, 0.0),
            motion_limits=tilt_limits,
            mimic=None if i == 1 else Mimic(joint="slat_tilt", multiplier=1.0, offset=0.0),
        )
    return {"geom": geom, "headrail": headrail}


def _build_roman(model, r, mats):
    fold_height = 0.155
    sub_height = fold_height
    # A raised roman shade piles its soft fabric into folds that DRAPE over the
    # immediately-lower fold — legitimate neighbouring stacking contact. A rigid
    # fold-bulge mesh cannot fold flat, so gather the stack at HALF the fold
    # height (+margin): adjacent folds overlap (the drape, allow_overlap'd in
    # run_tests), but fold i and fold i+2 sit >= fold_height apart and never
    # interpenetrate — bounding the contact to immediate neighbours instead of
    # the old 0.030 pitch that buried every fold inside ~5 of its neighbours.
    stack_pitch = 0.5 * fold_height + 0.006
    geom = _horizontal_geom(r, r.count, sub_height, stack_pitch)
    headrail = _build_horizontal_headrail(model, r, mats, geom, support_kind="strip")
    _build_horizontal_bottom_rail(model, headrail, r, mats, geom)

    fold_mesh = mesh_from_geometry(
        _roman_fold_panel(geom["sub_width"], fold_height, 0.032, 0.004),
        "roman_fold_panel",
    )
    for i in range(1, r.count + 1):
        fold = model.part(f"fold_{i}")
        fold.visual(
            fold_mesh,
            origin=Origin(),
            material=mats["shade"],
            name=f"fold_panel_{i}", material_class_id="fabric.quilted_pleated",
        )
        _emit_lift_mimic(model, headrail, fold, geom, i, f"fold_lift_{i}")
    return {"geom": geom, "headrail": headrail}


def _build_cellular(model, r, mats):
    cell_height = 0.028
    sub_height = cell_height
    # A honeycomb cell is a RIGID hex prism here (real fabric cells collapse
    # flat when raised; a rigid mesh cannot). So the gathered stack pitch must
    # be ~cell_height: cells STACK bottom-up and kiss, never pass through each
    # other. Pitch = cell_height - 0.003 leaves a 3 mm fabric-squish residual
    # (< overlap gate tol 0.005), instead of the old 0.008 pitch that buried
    # each 28 mm cell 20 mm inside its neighbour. Compression room per cell is
    # still open_pitch(>=0.034) - 0.025 = 9 mm, keeping lift stroke > 0.3.
    stack_pitch = cell_height - 0.003
    geom = _horizontal_geom(r, r.count, sub_height, stack_pitch)
    headrail = _build_horizontal_headrail(model, r, mats, geom, support_kind="guide")
    _build_horizontal_bottom_rail(model, headrail, r, mats, geom)

    # Shared mesh asset: one hex geometry reused by all N cell visuals.
    cell_mesh = mesh_from_geometry(
        _honeycomb_cell(geom["sub_width"], 0.035, cell_height),
        "honeycomb_cell",
    )
    for i in range(1, r.count + 1):
        cell = model.part(f"cell_{i:02d}")
        cell.visual(
            cell_mesh,
            origin=Origin(),
            material=mats["shade"],
            name=f"cell_{i:02d}_body", material_class_id="fabric.sheer",
        )
        _emit_lift_mimic(model, headrail, cell, geom, i, f"cell_lift_{i:02d}")
    return {"geom": geom, "headrail": headrail}


# ===========================================================================
# Slot A / roller_shade (single sheet; independent roller + lift drivers)
# ===========================================================================
def _build_roller(model, r, mats):
    width = _H_BLIND_WIDTH * r.blind_width_scale
    headrail_size = (width, _H_HEADRAIL_DEPTH, _H_HEADRAIL_HEIGHT)
    headrail_bottom_z = _H_HEADRAIL_Z - 0.5 * _H_HEADRAIL_HEIGHT
    # drop_scale lowers the bottom bar (longer window); the deployed sheet always
    # spans from the bottom bar up to the headrail bottom so the bar stays
    # connected to the grounded body at rest (fail_if_isolated_parts).
    base_drop = headrail_bottom_z - _R_SHADE_BOTTOM_Z
    shade_bottom_z = headrail_bottom_z - base_drop * r.drop_scale
    shade_height = (headrail_bottom_z - shade_bottom_z) + 0.0015  # just meets rail
    roller_length = width - 0.04
    shade_width = width - 0.06
    # Roller axis just below the headrail box so the roller joint origin sits on
    # the box (articulation-origin baseline, tol=0.015). Tube top embeds the box.
    roller_z = headrail_bottom_z - 0.010

    headrail = model.part("headrail")
    headrail.visual(
        Box(headrail_size),
        origin=Origin(xyz=(0.0, 0.0, _H_HEADRAIL_Z)),
        material=mats["rail"],
        name="headrail_box", material_class_id=("metal.paint_coated" if r.palette_style in {"wood_dark", "wood_natural", "grey_fabric", "cream_cellular"} else "plastic.opaque_glossy_molded"),
    )
    # Mounting brackets above each end (Rule 1 visuals).
    for i, sx in enumerate((-1, 1)):
        bx = sx * (width / 2.0 - 0.020)
        headrail.visual(
            Box((0.040, 0.070, 0.035)),
            origin=Origin(xyz=(bx, 0.0, _H_HEADRAIL_Z + 0.047)),
            material=mats["accent"],
            name=f"bracket_{i}", material_class_id="metal.paint_coated",
        )
    # Center pull cord running down (just behind the shade) from inside the
    # headrail box to the bottom bar rest position, so the shade_lift joint
    # origin (at x=0, z=shade_bottom_z) lands on real headrail geometry, and the
    # cord top is buried in the box (intra-part connectivity). Real lift cord.
    cord_top_z = _H_HEADRAIL_Z
    cord_len = cord_top_z - shade_bottom_z + 0.010
    headrail.visual(
        Cylinder(radius=0.0022, length=cord_len),
        origin=Origin(xyz=(0.0, -0.006, cord_top_z - 0.5 * cord_len)),
        material=mats["cord"],
        name="center_lift_cord", material_class_id="fabric.thread_yarn",
    )
    _add_horizontal_cord_lock(headrail, mats)

    # Roller tube: hollow CadQuery shell along X.
    roller_tube = model.part("roller_tube")
    tube_mesh = mesh_from_cadquery(
        _roller_tube_solid(_R_ROLLER_RADIUS, _R_ROLLER_WALL, roller_length),
        "roller_tube_shell",
    )
    roller_tube.visual(
        tube_mesh,
        origin=Origin(rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["accent"],
        name="tube_shell", material_class_id="metal.aluminum_bare",
    )
    ridge_mesh = mesh_from_cadquery(
        _roller_ridge_solid(shade_width, _R_WRAP_THICK),
        "wound_shade_ridge",
    )
    roller_tube.visual(
        ridge_mesh,
        origin=Origin(xyz=(0.0, -(_R_ROLLER_RADIUS + _R_WRAP_THICK / 2.0 - 0.001), 0.0)),
        material=mats["shade"],
        name="shade_ridge", material_class_id=("fabric.plain_flat_weave" if r.palette_style in {"wood_dark", "wood_natural", "grey_fabric", "cream_cellular"} else "plastic.frosted_translucent"),
    )
    for i, sx in enumerate((-1, 1)):
        cx = sx * (roller_length / 2.0 + 0.003)
        roller_tube.visual(
            Cylinder(radius=_R_ROLLER_RADIUS + 0.004, length=0.008),
            origin=Origin(xyz=(cx, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["accent"],
            name=f"tube_bearing_{i}", material_class_id="plastic.opaque_glossy_molded",
        )
    # Solid central spindle along the tube axis so the roller joint origin
    # (at the tube center, child frame (0,0,0)) sits on real solid geometry —
    # the hollow shell alone leaves the axis in a void (dist_child > tol).
    roller_tube.visual(
        Cylinder(radius=_R_ROLLER_RADIUS - _R_ROLLER_WALL + 0.001, length=roller_length),
        origin=Origin(rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["accent"],
        name="tube_spindle", material_class_id="metal.steel_bare",
    )
    model.articulation(
        "roller",
        ArticulationType.REVOLUTE,
        parent=headrail,
        child=roller_tube,
        origin=Origin(xyz=(0.0, 0.0, roller_z)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=5.0, velocity=2.0, lower=0.0, upper=2.0 * math.pi),
    )

    # Bottom bar + shade sheet (independent PRISMATIC lift).
    bottom_bar = model.part("bottom_bar")
    bottom_bar.visual(
        Box((roller_length + 0.02, _R_BOTTOM_BAR_DEPTH, _R_BOTTOM_BAR_HEIGHT)),
        origin=Origin(),
        material=mats["rail"],
        name="bottom_bar_weight", material_class_id=("metal.paint_coated" if r.palette_style in {"wood_dark", "wood_natural", "grey_fabric", "cream_cellular"} else "plastic.opaque_glossy_molded"),
    )
    shade_mesh = mesh_from_cadquery(
        _roller_sheet_solid(shade_width, _R_SHADE_THICK, shade_height),
        "shade_panel",
    )
    bottom_bar.visual(
        shade_mesh,
        origin=Origin(xyz=(0.0, 0.0, shade_height / 2.0)),
        material=mats["shade"],
        name="shade_panel", material_class_id=("fabric.plain_flat_weave" if r.palette_style in {"wood_dark", "wood_natural", "grey_fabric", "cream_cellular"} else "plastic.frosted_translucent"),
    )
    model.articulation(
        "shade_lift",
        ArticulationType.PRISMATIC,
        parent=headrail,
        child=bottom_bar,
        origin=Origin(xyz=(0.0, 0.0, shade_bottom_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=40.0, velocity=0.5, lower=0.0, upper=_R_SHADE_TRAVEL),
    )
    return {
        "headrail": headrail,
        "shade_height": shade_height,
        "headrail_bottom_z": headrail_bottom_z,
    }


# ===========================================================================
# Slot A / vertical_vanes (+ Slot C center_split)
# ===========================================================================
def _vertical_layout(r: ResolvedWindowBlindConfig):
    count = r.count
    # Vane bottom = STEM_BOTTOM - 0.018 - drop; cap so it clears the floor.
    max_drop = (_V_STEM_BOTTOM_Z - 0.018) - 0.05
    vane_drop = min(_V_VANE_DROP * r.drop_scale, max_drop)
    # Pitch keeps >=10mm side overlap; rail long enough to hold all vanes + cap.
    vane_pitch = _V_VANE_WIDTH - 0.014  # 14mm overlap nominal
    rail_length = (count - 1) * vane_pitch + _V_VANE_WIDTH + 0.10
    rail_length *= 1.0  # already includes margin
    rail_length = max(rail_length, 0.6) * 1.0
    rail_length *= r.blind_width_scale
    # Re-derive pitch so the vane set fits within the scaled rail with end margin.
    usable = rail_length - _V_VANE_WIDTH - 0.10
    vane_pitch = min(vane_pitch, usable / max(count - 1, 1)) if count > 1 else vane_pitch
    first_x = -0.5 * (count - 1) * vane_pitch
    return {
        "count": count,
        "vane_drop": vane_drop,
        "vane_pitch": vane_pitch,
        "rail_length": rail_length,
        "first_x": first_x,
    }


def _vane_x(lay, index: int) -> float:
    return lay["first_x"] + (index - 1) * lay["vane_pitch"]


def _vane_y_offset(index: int) -> float:
    return _V_VANE_STAGGER if index % 2 == 1 else -_V_VANE_STAGGER


def _build_vertical_headrail(model, r, mats, lay):
    rail_length = lay["rail_length"]
    headrail = model.part("headrail")
    headrail.visual(
        Box((rail_length, _V_RAIL_DEPTH, _V_RAIL_HEIGHT)),
        origin=Origin(xyz=(0.0, 0.0, _V_RAIL_BOTTOM_Z + 0.5 * _V_RAIL_HEIGHT)),
        material=mats["rail"],
        name="rail_body", material_class_id=("metal.paint_coated" if r.palette_style in {"wood_dark", "wood_natural", "grey_fabric", "cream_cellular"} else "plastic.opaque_glossy_molded"),
    )
    headrail.visual(
        Box((rail_length, _V_RAIL_DEPTH + 0.010, 0.008)),
        origin=Origin(xyz=(0.0, 0.0, _V_RAIL_BOTTOM_Z + _V_RAIL_HEIGHT + 0.004)),
        material=mats["rail"],
        name="top_lip", material_class_id=("metal.paint_coated" if r.palette_style in {"wood_dark", "wood_natural", "grey_fabric", "cream_cellular"} else "plastic.opaque_glossy_molded"),
    )
    for side, sign in (("end_cap_0", -1.0), ("end_cap_1", 1.0)):
        headrail.visual(
            Box((0.012, _V_RAIL_DEPTH + 0.007, _V_RAIL_HEIGHT + 0.010)),
            origin=Origin(
                xyz=(
                    sign * (0.5 * rail_length - 0.004),
                    0.0,
                    _V_RAIL_BOTTOM_Z + 0.5 * _V_RAIL_HEIGHT,
                )
            ),
            material=mats["rail"],
            name=side, material_class_id=("metal.paint_coated" if r.palette_style in {"wood_dark", "wood_natural", "grey_fabric", "cream_cellular"} else "plastic.opaque_glossy_molded"),
        )
    chain_x = -0.5 * rail_length + 0.03
    headrail.visual(
        Box((0.012, 0.028, 0.014)),
        origin=Origin(xyz=(chain_x, -0.030, 2.073)),
        material=mats["rail"],
        name="chain_boss", material_class_id=("metal.paint_coated" if r.palette_style in {"wood_dark", "wood_natural", "grey_fabric", "cream_cellular"} else "plastic.opaque_glossy_molded"),
    )
    return headrail, chain_x


def _build_carrier_train_visuals(part, lay, mats, indices, reach_center=False):
    xs = [_vane_x(lay, i) for i in indices]
    lo, hi = xs[0] - 0.012, xs[-1] + 0.012
    if reach_center:
        # Split half-trains: extend the spacer rail to the centerline (x=0) so
        # the train geometry contains its traverse joint origin (at x=0) for the
        # articulation-origin baseline, and the two halves meet at center closed.
        lo = min(lo, 0.0)
        hi = max(hi, 0.0)
    cx = 0.5 * (lo + hi)
    sl = hi - lo
    part.visual(
        Box((sl, 0.006, 0.005)),
        origin=Origin(xyz=(cx, 0.0, -0.0105)),
        material=mats["accent"],
        name="spacer_rail", material_class_id="plastic.opaque_glossy_molded",
    )
    for i in indices:
        x = _vane_x(lay, i)
        part.visual(
            Box((0.016, 0.028, 0.016)),
            origin=Origin(xyz=(x, 0.0, -0.008)),
            material=mats["accent"],
            name=f"carrier_{i:02d}", material_class_id="plastic.opaque_glossy_molded",
        )
        part.visual(
            Cylinder(radius=0.0035, length=0.008),
            origin=Origin(xyz=(x, 0.0, -0.020)),
            material=mats["accent"],
            name=f"carrier_stem_{i:02d}", material_class_id="plastic.opaque_glossy_molded",
        )


def _build_vane_part(model, parent_train, lay, mats, i):
    x = _vane_x(lay, i)
    y_off = _vane_y_offset(i)
    vane = model.part(f"vane_{i:02d}")
    vane.visual(
        Box((0.020, 0.007, 0.018)),
        origin=Origin(xyz=(0.0, y_off, -0.009)),
        material=mats["accent"],
        name="hanger_clip", material_class_id="plastic.opaque_glossy_molded",
    )
    vane.visual(
        Box((_V_VANE_WIDTH, _V_VANE_THICKNESS, lay["vane_drop"])),
        origin=Origin(xyz=(0.0, y_off, -0.018 - 0.5 * lay["vane_drop"])),
        material=mats["shade"],
        name="vane_strip", material_class_id="fabric.plain_flat_weave",
    )
    joint = model.articulation(
        f"vane_{i:02d}_tilt",
        ArticulationType.REVOLUTE,
        parent=parent_train,
        child=vane,
        origin=Origin(xyz=(x, 0.0, _V_STEM_BOTTOM_Z - _V_RAIL_BOTTOM_Z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(
            effort=4.0, velocity=2.0, lower=-_V_TILT_LIMIT, upper=_V_TILT_LIMIT
        ),
        mimic=None if i == 1 else Mimic(joint="vane_01_tilt", multiplier=1.0, offset=0.0),
    )
    return joint


def _add_control_chain(model, headrail, mats, chain_x):
    chain = model.part("control_chain")
    chain.visual(
        Cylinder(radius=0.002, length=_V_CHAIN_LENGTH),
        origin=Origin(xyz=(0.0, 0.0, -0.5 * _V_CHAIN_LENGTH)),
        material=mats["cord"],
        name="chain_cord", material_class_id="fabric.thread_yarn",
    )
    chain.visual(
        Cylinder(radius=0.0085, length=0.055),
        origin=Origin(xyz=(0.0, 0.0, -_V_CHAIN_LENGTH - 0.0275)),
        material=mats["tassel"],
        name="tassel_body", material_class_id="plastic.opaque_glossy_molded",
    )
    chain.visual(
        Sphere(radius=0.0085),
        origin=Origin(xyz=(0.0, 0.0, -_V_CHAIN_LENGTH - 0.055)),
        material=mats["tassel"],
        name="tassel_tip", material_class_id="plastic.opaque_glossy_molded",
    )
    model.articulation(
        "control_chain_swing",
        ArticulationType.REVOLUTE,
        parent=headrail,
        child=chain,
        origin=Origin(xyz=(chain_x, _V_CHAIN_Y, _V_CHAIN_TOP_Z)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=1.0, velocity=2.0, lower=-0.25, upper=0.25),
    )


def _build_vertical(model, r, mats):
    lay = _vertical_layout(r)
    headrail, chain_x = _build_vertical_headrail(model, r, mats, lay)
    count = lay["count"]

    if r.traverse_policy == "center_split_vertical":
        half = count // 2
        left_indices = range(1, half + 1)
        right_indices = range(half + 1, count + 1)
        left_train = model.part("left_carrier_train")
        _build_carrier_train_visuals(left_train, lay, mats, left_indices, reach_center=True)
        model.articulation(
            "left_traverse",
            ArticulationType.PRISMATIC,
            parent=headrail,
            child=left_train,
            origin=Origin(xyz=(0.0, 0.0, _V_RAIL_BOTTOM_Z)),
            axis=(-1.0, 0.0, 0.0),
            motion_limits=MotionLimits(
                effort=60.0, velocity=0.3, lower=0.0, upper=_V_SPLIT_TRAVERSE_LIMIT
            ),
        )
        right_train = model.part("right_carrier_train")
        _build_carrier_train_visuals(right_train, lay, mats, right_indices, reach_center=True)
        model.articulation(
            "right_traverse",
            ArticulationType.PRISMATIC,
            parent=headrail,
            child=right_train,
            origin=Origin(xyz=(0.0, 0.0, _V_RAIL_BOTTOM_Z)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(
                effort=60.0, velocity=0.3, lower=0.0, upper=_V_SPLIT_TRAVERSE_LIMIT
            ),
        )
        for i in range(1, count + 1):
            train = left_train if i <= half else right_train
            _build_vane_part(model, train, lay, mats, i)
    else:
        carrier_train = model.part("carrier_train")
        _build_carrier_train_visuals(carrier_train, lay, mats, range(1, count + 1))
        model.articulation(
            "vane_set_traverse",
            ArticulationType.PRISMATIC,
            parent=headrail,
            child=carrier_train,
            origin=Origin(xyz=(0.0, 0.0, _V_RAIL_BOTTOM_Z)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(
                effort=60.0, velocity=0.3, lower=-_V_TRAVERSE_LIMIT, upper=_V_TRAVERSE_LIMIT
            ),
        )
        for i in range(1, count + 1):
            _build_vane_part(model, carrier_train, lay, mats, i)

    _add_control_chain(model, headrail, mats, chain_x)
    return {"lay": lay, "headrail": headrail}


# ===========================================================================
# Top-level build
# ===========================================================================
_BUILDERS = {
    "horizontal_venetian": _build_venetian,
    "vertical_vanes": _build_vertical,
    "roller_shade": _build_roller,
    "roman_folds": _build_roman,
    "cellular_honeycomb": _build_cellular,
}


def build_window_blind(
    config: WindowBlindConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    pal = PALETTES[r.palette_style]
    mats = {
        key: model.material(f"wb_{key}_{r.palette_style}", rgba=pal[key])
        for key in ("rail", "shade", "accent", "cord", "tassel")
    }
    info = _BUILDERS[r.shade_topology](model, r, mats)
    model.meta["slot_choices"] = slot_choices_for_config(r)
    model.meta["build_info_keys"] = sorted(info.keys())
    return model


def build_seeded_window_blind(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_window_blind(config_from_seed(seed), assets=assets)


# ===========================================================================
# Tests
# ===========================================================================
def run_window_blind_tests(
    object_model: ArticulatedObject,
    config: WindowBlindConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    topology = r.shade_topology

    headrail = object_model.get_part("headrail")

    # ---- captured/embed overlaps per topology (element-scoped) -------------
    if topology == "horizontal_venetian":
        for i in range(1, r.count + 1):
            blade = object_model.get_part(f"slat_{i:02d}")
            ctx.allow_overlap(
                headrail,
                blade,
                elem_a="center_lift_cord",
                elem_b=f"slat_{i:02d}_blade",
                reason="central lift cord threads through the slat (captured)",
            )
            for side in ("a", "b"):
                for face in ("front", "rear"):
                    ctx.allow_overlap(
                        headrail,
                        blade,
                        elem_a=f"ladder_tape_{side}_{face}",
                        elem_b=f"slat_{i:02d}_blade",
                        reason="slat edge straddles ladder tape (0.5mm physical contact)",
                    )
    elif topology == "roman_folds":
        for i in range(1, r.count + 1):
            fold = object_model.get_part(f"fold_{i}")
            ctx.allow_overlap(
                headrail,
                fold,
                elem_a="center_lift_cord",
                elem_b=f"fold_panel_{i}",
                reason="central lift cord threads through the fold (captured)",
            )
            for side in ("a", "b"):
                ctx.allow_overlap(
                    headrail,
                    fold,
                    elem_a=f"lift_cord_strip_{side}",
                    elem_b=f"fold_panel_{i}",
                    reason="fold back face embeds the lift cord strip (0.5mm)",
                )
        # Gathered soft-fold drape: each raised fold nests over the immediately
        # lower one. Scoped to ADJACENT pairs only — non-adjacent folds stay
        # >= fold_height apart (stack_pitch derivation) and must not overlap.
        for i in range(1, r.count):
            ctx.allow_overlap(
                object_model.get_part(f"fold_{i}"),
                object_model.get_part(f"fold_{i + 1}"),
                elem_a=f"fold_panel_{i}",
                elem_b=f"fold_panel_{i + 1}",
                reason="raised roman folds drape over the adjacent lower fold",
            )
    elif topology == "cellular_honeycomb":
        for i in range(1, r.count + 1):
            cell = object_model.get_part(f"cell_{i:02d}")
            ctx.allow_overlap(
                headrail,
                cell,
                elem_a="center_lift_cord",
                elem_b=f"cell_{i:02d}_body",
                reason="central lift cord threads through the cell (captured)",
            )
            for side in ("a", "b"):
                ctx.allow_overlap(
                    headrail,
                    cell,
                    elem_a=f"cord_guide_{side}",
                    elem_b=f"cell_{i:02d}_body",
                    reason="cell passes around cord guide (slight embed)",
                )
    elif topology == "vertical_vanes":
        if r.traverse_policy == "center_split_vertical":
            half = r.count // 2
            for i in range(1, r.count):
                if i == half:
                    continue
                a = object_model.get_part(f"vane_{i:02d}")
                b = object_model.get_part(f"vane_{i + 1:02d}")
                ctx.allow_overlap(
                    a,
                    b,
                    elem_a="vane_strip",
                    elem_b="vane_strip",
                    reason="closed adjacent vanes overlap sideways (front/back stagger)",
                )
        else:
            for i in range(1, r.count):
                a = object_model.get_part(f"vane_{i:02d}")
                b = object_model.get_part(f"vane_{i + 1:02d}")
                ctx.allow_overlap(
                    a,
                    b,
                    elem_a="vane_strip",
                    elem_b="vane_strip",
                    reason="closed adjacent vanes overlap sideways (front/back stagger)",
                )
    elif topology == "roller_shade":
        roller_tube = object_model.get_part("roller_tube")
        bottom_bar = object_model.get_part("bottom_bar")
        # The roller tube nests up inside the headrail channel; every tube
        # element may seat into the box bottom.
        for elem in (
            "tube_shell",
            "tube_spindle",
            "shade_ridge",
            "tube_bearing_0",
            "tube_bearing_1",
        ):
            ctx.allow_overlap(
                headrail,
                roller_tube,
                elem_a="headrail_box",
                elem_b=elem,
                reason="roller tube nests up into the headrail channel (mounted tube)",
            )
        ctx.allow_overlap(
            headrail,
            bottom_bar,
            elem_a="center_lift_cord",
            elem_b="bottom_bar_weight",
            reason="central lift cord terminates inside the bottom bar",
        )
        ctx.allow_overlap(
            headrail,
            bottom_bar,
            elem_a="center_lift_cord",
            elem_b="shade_panel",
            reason="central lift cord runs just behind the shade sheet (captured)",
        )

    # The center lift cord runs into the bottom rail (horizontal topologies).
    if topology in ("horizontal_venetian", "roman_folds", "cellular_honeycomb"):
        bottom_rail = object_model.get_part("bottom_rail")
        ctx.allow_overlap(
            headrail,
            bottom_rail,
            elem_a="center_lift_cord",
            elem_b="bottom_rail_bar",
            reason="central lift cord terminates inside the bottom rail",
        )

    # ---- baseline gates ----------------------------------------------------
    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_joint_mating_has_gap()

    # ---- root + slot_choices ----------------------------------------------
    ctx.check("headrail_is_present", headrail is not None, details="missing headrail root")
    ctx.check(
        "slot_choices_recorded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    # ---- topology-specific structural + motion checks ----------------------
    if topology in ("horizontal_venetian", "roman_folds", "cellular_honeycomb"):
        _check_horizontal(ctx, object_model, r, topology)
    elif topology == "vertical_vanes":
        _check_vertical(ctx, object_model, r)
    else:
        _check_roller(ctx, object_model, r)

    return ctx.report()


def _check_horizontal(ctx, object_model, r, topology):
    headrail = object_model.get_part("headrail")
    bottom_rail = object_model.get_part("bottom_rail")
    lift = object_model.get_articulation("lift")

    if topology == "horizontal_venetian":
        sub_parts = [object_model.get_part(f"slat_{i:02d}") for i in range(1, r.count + 1)]
        lift_names = [f"slat_lift_{i:02d}" for i in range(1, r.count + 1)]
    elif topology == "roman_folds":
        sub_parts = [object_model.get_part(f"fold_{i}") for i in range(1, r.count + 1)]
        lift_names = [f"fold_lift_{i}" for i in range(1, r.count + 1)]
    else:
        sub_parts = [object_model.get_part(f"cell_{i:02d}") for i in range(1, r.count + 1)]
        lift_names = [f"cell_lift_{i:02d}" for i in range(1, r.count + 1)]

    ctx.check(
        "sub_part_count",
        all(s is not None for s in sub_parts),
        details=f"expected {r.count} sub-parts",
    )

    ctx.check(
        "lift_driver_prismatic_vertical",
        tuple(lift.axis) == (0.0, 0.0, 1.0)
        and lift.articulation_type == ArticulationType.PRISMATIC
        and lift.mimic is None,
        details=f"lift axis={lift.axis} type={lift.articulation_type}",
    )
    ctx.check(
        "lift_stroke_substantial",
        lift.motion_limits is not None and lift.motion_limits.upper > 0.3,
        details=f"lift travel={lift.motion_limits.upper if lift.motion_limits else 0:.3f}",
    )

    followers = [object_model.get_articulation(n) for n in lift_names]
    mults = [a.mimic.multiplier for a in followers if a.mimic is not None]
    ok_chain = (
        len(mults) == r.count
        and all(a.mimic is not None and a.mimic.joint == "lift" for a in followers)
        and all(0.0 < mm <= 1.0 for mm in mults)
        and all(mults[k] < mults[k + 1] for k in range(len(mults) - 1))
    )
    ctx.check(
        "lift_mimic_bottom_leads",
        ok_chain,
        details=f"mults(top->bottom)={[round(m, 3) for m in mults]}",
    )

    if topology == "horizontal_venetian":
        tilt = object_model.get_articulation("slat_tilt")
        ctx.check(
            "tilt_axis_long_horizontal_x",
            tuple(tilt.axis) == (1.0, 0.0, 0.0),
            details=f"tilt axis={tilt.axis}",
        )
        tilt_followers = [a for a in object_model.articulations if a.name.startswith("slat_tilt_")]
        ok_tilt = len(tilt_followers) == r.count - 1 and all(
            a.mimic is not None
            and a.mimic.joint == "slat_tilt"
            and abs(a.mimic.multiplier - 1.0) < 1e-9
            and abs(a.mimic.offset) < 1e-9
            for a in tilt_followers
        )
        ctx.check(
            "tilt_followers_mimic_1to1", ok_tilt, details=f"{len(tilt_followers)} tilt followers"
        )
    else:
        tilt_joints = [a for a in object_model.articulations if "tilt" in a.name]
        ctx.check(
            "no_tilt_articulations",
            len(tilt_joints) == 0,
            details=f"found {len(tilt_joints)} tilt joints",
        )

    headrail_box = headrail.get_visual("headrail_box")
    headrail_box_aabb = ctx.part_element_world_aabb(headrail, elem=headrail_box)

    # Lowered pose: bottom rail below lowest sub-part; headrail above top.
    with ctx.pose({lift: 0.0}):
        ctx.expect_gap(
            sub_parts[-1], bottom_rail, axis="z", min_gap=0.008, name="bottom_rail_below_lowest"
        )
        ctx.expect_gap(
            headrail,
            sub_parts[0],
            axis="z",
            min_gap=0.008,
            positive_elem=headrail_box,
            name="headrail_above_top",
        )

    # Raised pose: bottom-led gather under headrail.
    travel = float(lift.motion_limits.upper)
    z_low = [ctx.part_world_position(s)[2] for s in sub_parts]
    with ctx.pose({lift: travel}):
        z_high = [ctx.part_world_position(s)[2] for s in sub_parts]
        rises = [zr - zl for zr, zl in zip(z_high, z_low)]
        ctx.check(
            "all_rise_on_lift", all(rr > 1e-4 for rr in rises), details=f"min rise={min(rises):.4f}"
        )
        ctx.check(
            "lower_leads_gather",
            all(rises[k] < rises[k + 1] for k in range(len(rises) - 1)),
            details=f"rises={[round(rr, 3) for rr in rises]}",
        )
        top_aabb = ctx.part_world_aabb(sub_parts[0])
        ctx.check(
            "gathered_under_headrail",
            top_aabb is not None
            and headrail_box_aabb is not None
            and top_aabb[1][2] < headrail_box_aabb[0][2] + 1e-4,
            details=f"top={None if top_aabb is None else top_aabb[1][2]:.3f}",
        )

    # Venetian slats tilt: at BOTH lift extremes the fully-tilted top slat must
    # stay below the headrail box and the fully-tilted bottom slat above the
    # bottom rail (the end_clearance reservation). Guards the tilt-sweep 穿模.
    if topology == "horizontal_venetian":
        tilt = object_model.get_articulation("slat_tilt")
        t_max = float(tilt.motion_limits.upper)
        for lift_val, label in ((0.0, "lowered"), (travel, "raised")):
            with ctx.pose({lift: lift_val, tilt: t_max}):
                top_a = ctx.part_world_aabb(sub_parts[0])
                bot_a = ctx.part_world_aabb(sub_parts[-1])
                rail_a = ctx.part_world_aabb(bottom_rail)
                ctx.check(
                    f"tilted_top_clears_headrail_{label}",
                    top_a is not None
                    and headrail_box_aabb is not None
                    and top_a[1][2] < headrail_box_aabb[0][2] + 1e-4,
                    details=f"slat_top={None if top_a is None else round(top_a[1][2], 4)}",
                )
                ctx.check(
                    f"tilted_bottom_clears_rail_{label}",
                    bot_a is not None and rail_a is not None and bot_a[0][2] > rail_a[1][2] - 1e-4,
                    details=f"slat_bot={None if bot_a is None else round(bot_a[0][2], 4)}"
                    f" rail_top={None if rail_a is None else round(rail_a[1][2], 4)}",
                )


def _check_vertical(ctx, object_model, r):
    headrail = object_model.get_part("headrail")
    vanes = [object_model.get_part(f"vane_{i:02d}") for i in range(1, r.count + 1)]
    driver = object_model.get_articulation("vane_01_tilt")
    swing = object_model.get_articulation("control_chain_swing")

    ctx.check("vane_count", all(v is not None for v in vanes), details=f"expected {r.count} vanes")
    ctx.check(
        "driver_tilt_axis_vertical_z",
        tuple(driver.axis) == (0.0, 0.0, 1.0)
        and driver.articulation_type == ArticulationType.REVOLUTE,
        details=f"axis={driver.axis}",
    )
    bad = []
    for i in range(2, r.count + 1):
        j = object_model.get_articulation(f"vane_{i:02d}_tilt")
        m = j.mimic
        if (
            m is None
            or m.joint != "vane_01_tilt"
            or abs(m.multiplier - 1.0) > 1e-9
            or abs(m.offset) > 1e-9
        ):
            bad.append(j.name)
    ctx.check("follower_vanes_mimic_1to1", not bad, details=f"bad={bad}")

    # Mounting chain + hang.
    if r.traverse_policy == "center_split_vertical":
        left_train = object_model.get_part("left_carrier_train")
        right_train = object_model.get_part("right_carrier_train")
        left_trav = object_model.get_articulation("left_traverse")
        right_trav = object_model.get_articulation("right_traverse")
        half = r.count // 2
        ctx.expect_contact(vanes[0], left_train, contact_tol=0.0005, name="left vane hangs on stem")
        ctx.expect_contact(
            vanes[-1], right_train, contact_tol=0.0005, name="right vane hangs on stem"
        )
        ctx.expect_contact(left_train, headrail, contact_tol=0.0005, name="left train rides rail")
        ctx.expect_contact(right_train, headrail, contact_tol=0.0005, name="right train rides rail")
        # Fully open: center gap.
        with ctx.pose({left_trav: _V_SPLIT_TRAVERSE_LIMIT, right_trav: _V_SPLIT_TRAVERSE_LIMIT}):
            ctx.expect_gap(
                vanes[half],
                vanes[half - 1],
                axis="x",
                min_gap=0.06,
                name="center_split_gap_when_open",
            )
    else:
        carrier_train = object_model.get_part("carrier_train")
        traverse = object_model.get_articulation("vane_set_traverse")
        ctx.expect_contact(vanes[0], carrier_train, contact_tol=0.0005, name="vane_01 hangs on stem")
        ctx.expect_contact(
            vanes[-1], carrier_train, contact_tol=0.0005, name="last vane hangs on stem"
        )
        ctx.expect_contact(
            carrier_train, headrail, contact_tol=0.0005, name="carrier train rides rail"
        )
        rest = ctx.part_world_position(carrier_train)
        with ctx.pose({traverse: _V_TRAVERSE_LIMIT}):
            moved = ctx.part_world_position(carrier_train)
        ctx.check(
            "traverse_slides_set",
            rest is not None and moved is not None and moved[0] > rest[0] + 0.5 * _V_TRAVERSE_LIMIT,
            details=f"rest={rest}, moved={moved}",
        )

    mid = vanes[r.count // 2]
    ctx.expect_gap(headrail, mid, axis="z", min_gap=0.005, name="vanes hang below headrail")
    vane_aabb = ctx.part_world_aabb(mid)
    ctx.check(
        "vanes_clear_floor",
        vane_aabb is not None and vane_aabb[0][2] > 0.0,
        details=f"min_z={None if vane_aabb is None else vane_aabb[0][2]}",
    )

    # Tilt: driver + a follower turn edge-on at +90.
    with ctx.pose({driver: _V_TILT_LIMIT}):
        for probe in (vanes[0], mid):
            aabb = ctx.part_world_aabb(probe)
            depth = None if aabb is None else aabb[1][1] - aabb[0][1]
            ctx.check(
                f"{probe.name}_turns_edge_on",
                depth is not None and depth > 0.080,
                details=f"depth={depth}",
            )

    # Chain swing.
    rest_chain = ctx.part_world_aabb(object_model.get_part("control_chain"))
    with ctx.pose({swing: 0.25}):
        swung_chain = ctx.part_world_aabb(object_model.get_part("control_chain"))
    ctx.check(
        "chain_swings",
        rest_chain is not None
        and swung_chain is not None
        and swung_chain[1][1] > rest_chain[1][1] + 0.10,
        details="control chain swings about boss",
    )


def _check_roller(ctx, object_model, r):
    headrail = object_model.get_part("headrail")
    roller_tube = object_model.get_part("roller_tube")
    bottom_bar = object_model.get_part("bottom_bar")
    roller = object_model.get_articulation("roller")
    shade_lift = object_model.get_articulation("shade_lift")

    ctx.check(
        "roller_tube_has_shell",
        roller_tube.get_visual("tube_shell") is not None,
        details="missing tube_shell",
    )
    ctx.check(
        "shade_panel_exists",
        bottom_bar.get_visual("shade_panel") is not None,
        details="missing shade_panel",
    )
    ctx.check(
        "roller_axis_horizontal_x",
        tuple(roller.axis) == (1.0, 0.0, 0.0)
        and roller.articulation_type == ArticulationType.REVOLUTE,
        details=f"roller axis={roller.axis}",
    )
    ctx.check(
        "roller_full_turn",
        roller.motion_limits is not None and abs(roller.motion_limits.upper - 2.0 * math.pi) < 0.01,
        details=f"limits={roller.motion_limits}",
    )
    ctx.check(
        "shade_lift_independent_prismatic_z",
        shade_lift.articulation_type == ArticulationType.PRISMATIC
        and tuple(shade_lift.axis) == (0.0, 0.0, 1.0)
        and shade_lift.mimic is None,
        details=f"shade_lift axis={shade_lift.axis} mimic={shade_lift.mimic}",
    )
    ctx.check(
        "shade_lift_travel_substantial",
        shade_lift.motion_limits is not None and shade_lift.motion_limits.upper > 0.30,
        details=f"travel={shade_lift.motion_limits.upper if shade_lift.motion_limits else 0:.3f}",
    )

    ctx.expect_contact(roller_tube, headrail, name="roller_tube_supported_by_headrail")

    lift_max = float(shade_lift.motion_limits.upper)
    bar_rest = ctx.part_world_position(bottom_bar)[2]
    with ctx.pose({shade_lift: lift_max}):
        bar_raised = ctx.part_world_position(bottom_bar)[2]
        ctx.check(
            "bottom_bar_rises",
            bar_raised > bar_rest + 0.20,
            details=f"rest={bar_rest:.3f} raised={bar_raised:.3f}",
        )


__all__ = (
    "WindowBlindConfig",
    "ResolvedWindowBlindConfig",
    "build_window_blind",
    "build_seeded_window_blind",
    "config_from_seed",
    "resolve_config",
    "run_window_blind_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
