# SPDX-License-Identifier: Apache-2.0

"""Ring binder (3-ring office/school binder) — modular procedural template.

The picture folder is named "ring-blinder"; the real object is a **3-ring
binder**: two hinged cover boards on a center spine, plus a metal multi-ring
mechanism (2-4 stations) that opens/closes to clamp punched sheets.

Mixed parallel topology on a fixed `spine` root:

* Chassis (always): spine + front_cover + back_cover (revolute) + paper_stack.
  A single structural family across all 8 samples (no second cover-board form) —
  a fixed root, not a slot.
* Slot A ``ring_mechanism``  — single_moving (B) / split_dual (A); lever style
  co-varies with the mechanism and is folded into each module.
* Slot B ``ring_form``       — round / dring / slant (③ ring cross section;
  dring/slant gated to single_moving).
* Slot C ``mechanism_mount`` — spine / back_cover (① mechanism root).
* Slot D ``handle_or_grip``  — none / folding_spine (① carry handle).
* Slot E ``closure``         — none / foldover_strap (② closure).
* Multiplicity N ring stations ∈ {2, 3, 4}.

Sources (all 5-star, verified PASS):
  origin B  rec_workspace__3_ring_binder__002_...  (single_moving, round, spine)
  origin A  rec_workspace__3_ring_binder__001_...  (split_dual, round, spine)
  forks     rec_ring_blinder_var_{ring_dring,ring_slant,mount_back_cover,n2,
            handle_spine,closure_strap}

Rule 1: every non-articulating detail (creases, sleeves, pockets, saddles,
rivets, standoffs, lips, hinge rods) is a ``parent.visual(...)`` — the only
parts are the ones that hinge/open. Rule 2: every moving child parents to a real
board/plate visual; captured hinge overlaps are element-scoped ``allow_overlap``.
Rule 3: part tree / joint topology / mesh primitives (tube_from_spline_points,
connected-arc MeshGeometry, rounded-panel ExtrudeGeometry) are taken verbatim
from the declared sources — only literals, the ring point lists, board dims, and
the N-station tuple are parameterized.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Iterable, Literal

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    ExtrudeGeometry,
    Inertial,
    MeshGeometry,
    MotionLimits,
    Origin,
    Part,
    TestContext,
    TestReport,
    mesh_from_geometry,
    rounded_rect_profile,
    tube_from_spline_points,
)

from agent.templates._modular import mount_fixed

__modular__ = True


RingMechanism = Literal["single_moving", "split_dual"]
RingForm = Literal["round", "dring", "slant"]
MechanismMount = Literal["spine", "back_cover"]
HandleGrip = Literal["none", "folding_spine"]
Closure = Literal["none", "foldover_strap"]
PaletteTheme = Literal["white_plastic", "black_vinyl", "colored_poly"]

MECHANISM_MODULES: tuple[RingMechanism, ...] = ("single_moving", "split_dual")
RING_FORM_MODULES: tuple[RingForm, ...] = ("round", "dring", "slant")
MOUNT_MODULES: tuple[MechanismMount, ...] = ("spine", "back_cover")
HANDLE_MODULES: tuple[HandleGrip, ...] = ("none", "folding_spine")
CLOSURE_MODULES: tuple[Closure, ...] = ("none", "foldover_strap")
RING_COUNTS: tuple[int, ...] = (2, 3, 4)

# Source-faithful ring-station tuples per N (n2 fork / origin B / origin A).
RING_Y_BY_N: dict[int, tuple[float, ...]] = {
    2: (-0.045, 0.045),
    3: (-0.105, 0.0, 0.105),
    4: (-0.117, -0.039, 0.039, 0.117),
}

# --- Fixed metal-mechanism hardware constants (standardized part; see spec §7). #
BOARD_T = 0.006
PLATE_W = 0.060
PLATE_L = 0.262
PLATE_Z = 0.005  # single_moving plate center z in child frame (bottom at BOARD_T/2)
FIXED_HINGE_X = -0.012
MOVING_HINGE_X = 0.020
RING_TIP_X = 0.003
RING_TIP_Z = 0.058
LEVER_PIVOT_Z = 0.0215
LEVER_Y = (-0.126, 0.126)


PALETTES: dict[str, dict[str, tuple[float, float, float, float]]] = {
    "white_plastic": {
        "board": (0.93, 0.94, 0.92, 1.0),
        "edge": (0.64, 0.66, 0.64, 1.0),
        "pocket": (0.86, 0.92, 0.96, 0.36),
        "metal": (0.72, 0.70, 0.64, 1.0),
        "dark_metal": (0.40, 0.40, 0.36, 1.0),
        "page": (0.97, 0.97, 0.94, 1.0),
        "strap": (0.12, 0.22, 0.50, 1.0),
        "catch": (0.10, 0.10, 0.10, 1.0),
    },
    "black_vinyl": {
        "board": (0.02, 0.02, 0.02, 1.0),
        "edge": (0.0, 0.0, 0.0, 1.0),
        "pocket": (0.85, 0.90, 1.0, 0.35),
        "metal": (0.78, 0.72, 0.60, 1.0),
        "dark_metal": (0.28, 0.27, 0.24, 1.0),
        "page": (0.92, 0.90, 0.82, 1.0),
        "strap": (0.15, 0.15, 0.15, 1.0),
        "catch": (0.05, 0.05, 0.05, 1.0),
    },
    "colored_poly": {
        "board": (0.16, 0.42, 0.66, 1.0),
        "edge": (0.10, 0.28, 0.48, 1.0),
        "pocket": (0.90, 0.95, 1.0, 0.30),
        "metal": (0.75, 0.75, 0.72, 1.0),
        "dark_metal": (0.30, 0.30, 0.30, 1.0),
        "page": (0.96, 0.96, 0.92, 1.0),
        "strap": (0.85, 0.35, 0.10, 1.0),
        "catch": (0.10, 0.10, 0.10, 1.0),
    },
}


@dataclass(frozen=True)
class RingBlinderConfig:
    ring_mechanism: RingMechanism | None = None
    ring_form: RingForm | None = None
    mechanism_mount: MechanismMount | None = None
    handle: HandleGrip | None = None
    closure: Closure | None = None
    ring_count: int | None = None
    palette_theme: PaletteTheme = "white_plastic"
    binder_h: float = 0.310
    cover_w: float = 0.255
    spine_w: float = 0.060
    palette: dict[str, tuple[float, float, float, float]] = field(
        default_factory=lambda: dict(PALETTES["white_plastic"])
    )


@dataclass(frozen=True)
class ResolvedRingBlinderConfig:
    ring_mechanism: RingMechanism
    ring_form: RingForm
    mechanism_mount: MechanismMount
    handle: HandleGrip
    closure: Closure
    ring_count: int
    palette_theme: PaletteTheme
    binder_h: float
    cover_w: float
    spine_w: float
    ring_y: tuple[float, ...]
    palette: dict[str, tuple[float, float, float, float]]


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(v)))


def config_from_seed(seed: int) -> RingBlinderConfig:
    """Deterministic procedural sampling for every seed (seed 0 is NOT special).

    Order: board dims (independent) -> slot enums -> ring_form gate
    (split_dual forces round) -> weighted N. All clamping / the fit inequality
    is resolved in resolve_config.
    """
    rng = random.Random(seed)
    binder_h = rng.uniform(0.290, 0.340)
    cover_w = rng.uniform(0.230, 0.280)
    spine_w = rng.uniform(0.056, 0.090)

    ring_mechanism: RingMechanism = rng.choice(MECHANISM_MODULES)
    # Slot B ③: dring/slant are only source-backed on the single_moving tube
    # halves; the split-dual bank is connected round arcs (origin A) — gate.
    if ring_mechanism == "split_dual":
        ring_form: RingForm = "round"
    else:
        ring_form = rng.choice(RING_FORM_MODULES)
    mechanism_mount: MechanismMount = rng.choice(MOUNT_MODULES)
    handle: HandleGrip = rng.choice(HANDLE_MODULES)
    closure: Closure = rng.choice(CLOSURE_MODULES)
    # Weighted N: small N frequent, N=4 rarer (spec §8).
    ring_count = rng.choices(RING_COUNTS, weights=(0.25, 0.50, 0.25), k=1)[0]

    return RingBlinderConfig(
        ring_mechanism=ring_mechanism,
        ring_form=ring_form,
        mechanism_mount=mechanism_mount,
        handle=handle,
        closure=closure,
        ring_count=ring_count,
        palette_theme=rng.choice(tuple(PALETTES.keys())),  # type: ignore[arg-type]
        binder_h=round(binder_h, 4),
        cover_w=round(cover_w, 4),
        spine_w=round(spine_w, 4),
    )


def resolve_config(config: RingBlinderConfig) -> ResolvedRingBlinderConfig:
    ring_mechanism = config.ring_mechanism or "single_moving"
    ring_form = config.ring_form or "round"
    mechanism_mount = config.mechanism_mount or "spine"
    handle = config.handle or "none"
    closure = config.closure or "none"
    ring_count = int(config.ring_count or 3)
    for value, pool, label in (
        (ring_mechanism, MECHANISM_MODULES, "ring_mechanism"),
        (ring_form, RING_FORM_MODULES, "ring_form"),
        (mechanism_mount, MOUNT_MODULES, "mechanism_mount"),
        (handle, HANDLE_MODULES, "handle"),
        (closure, CLOSURE_MODULES, "closure"),
    ):
        if value not in pool:
            raise ValueError(f"Unsupported {label}: {value!r}")
    if config.palette_theme not in PALETTES:
        raise ValueError(f"Unsupported palette_theme: {config.palette_theme!r}")
    ring_count = max(2, min(ring_count, 4))
    # Compatibility gate: dring/slant are single_moving only.
    if ring_mechanism == "split_dual":
        ring_form = "round"

    # Board dims (⑤). binder_h must contain the fixed mechanism (PLATE_L) plus a
    # margin, else the plate would run off the spine (inequality, spec §7).
    binder_h = _clamp(config.binder_h, 0.290, 0.340)
    binder_h = max(binder_h, PLATE_L + 0.020)
    cover_w = _clamp(config.cover_w, 0.230, 0.280)
    spine_w = _clamp(config.spine_w, 0.056, 0.090)

    return ResolvedRingBlinderConfig(
        ring_mechanism=ring_mechanism,
        ring_form=ring_form,
        mechanism_mount=mechanism_mount,
        handle=handle,
        closure=closure,
        ring_count=ring_count,
        palette_theme=config.palette_theme,
        binder_h=binder_h,
        cover_w=cover_w,
        spine_w=spine_w,
        ring_y=RING_Y_BY_N[ring_count],
        palette=dict(PALETTES[config.palette_theme]),
    )


# --------------------------------------------------------------------------- #
# Mesh helpers                                                                 #
# --------------------------------------------------------------------------- #


def _rounded_panel(name: str, width: float, height: float, thickness: float, radius: float):
    """Rounded-rectangle board (origin B rounded_panel_mesh)."""
    return mesh_from_geometry(
        ExtrudeGeometry(
            rounded_rect_profile(width, height, radius, corner_segments=8),
            thickness,
            cap=True,
            center=True,
        ),
        name,
    )


def _ring_tube(name: str, points):
    """Thin metal ring tube along a polyline (origin B ring_tube)."""
    return mesh_from_geometry(
        tube_from_spline_points(
            points,
            radius=0.0021,
            samples_per_segment=14,
            radial_segments=18,
            cap_ends=True,
            up_hint=(0.0, 1.0, 0.0),
        ),
        name,
    )


def _fixed_ring_points(form: RingForm, y: float) -> list[tuple[float, float, float]]:
    """Fixed-half ring path per ③ ring_form (origin B / ring_dring / ring_slant)."""
    if form == "dring":
        return [
            (FIXED_HINGE_X, y, 0.0175),
            (FIXED_HINGE_X, y, 0.038),
            (FIXED_HINGE_X, y, RING_TIP_Z),
        ]
    if form == "slant":
        return [
            (FIXED_HINGE_X, y, 0.0175),
            (FIXED_HINGE_X - 0.007, y, 0.031),
            (FIXED_HINGE_X - 0.011, y, 0.046),
            (RING_TIP_X, y, RING_TIP_Z),
        ]
    return [  # round (origin B)
        (FIXED_HINGE_X, y, 0.0175),
        (FIXED_HINGE_X - 0.004, y, 0.031),
        (FIXED_HINGE_X - 0.0025, y, 0.047),
        (RING_TIP_X, y, RING_TIP_Z),
    ]


def _moving_ring_points(form: RingForm, y: float) -> list[tuple[float, float, float]]:
    """Moving-half ring path per ③ ring_form (in ring_halves child frame)."""
    tip = (RING_TIP_X - MOVING_HINGE_X, y, RING_TIP_Z - 0.0175)
    if form == "dring":
        return [
            (0.0, y, 0.0),
            (0.015, y, 0.008),
            (0.016, y, 0.022),
            (0.002, y, 0.036),
            tip,
        ]
    if form == "slant":
        return [
            (0.0, y, 0.0),
            (0.005, y, 0.013),
            (-0.006, y, 0.030),
            tip,
        ]
    return [  # round (origin B)
        (0.0, y, 0.0),
        (0.0035, y, 0.014),
        (0.0030, y, 0.034),
        tip,
    ]


Vec3 = tuple[float, float, float]


def _normalize(v: Vec3) -> Vec3:
    length = math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])
    if length <= 1e-9:
        return (1.0, 0.0, 0.0)
    return (v[0] / length, v[1] / length, v[2] / length)


def _cross(a: Vec3, b: Vec3) -> Vec3:
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _tube(geom: MeshGeometry, path: Iterable[Vec3], radius: float, *, sides: int = 10) -> None:
    """Append a rounded metal tube following a polyline (origin A _tube)."""
    pts = list(path)
    if len(pts) < 2:
        return
    rings: list[list[int]] = []
    for i, p in enumerate(pts):
        if i == 0:
            tangent = _normalize((pts[1][0] - p[0], pts[1][1] - p[1], pts[1][2] - p[2]))
        elif i == len(pts) - 1:
            tangent = _normalize((p[0] - pts[i - 1][0], p[1] - pts[i - 1][1], p[2] - pts[i - 1][2]))
        else:
            tangent = _normalize(
                (
                    pts[i + 1][0] - pts[i - 1][0],
                    pts[i + 1][1] - pts[i - 1][1],
                    pts[i + 1][2] - pts[i - 1][2],
                )
            )
        ref = (0.0, 1.0, 0.0)
        if abs(tangent[1]) > 0.85:
            ref = (0.0, 0.0, 1.0)
        n = _normalize(_cross(tangent, ref))
        b = _normalize(_cross(tangent, n))
        ring: list[int] = []
        for j in range(sides):
            ang = 2.0 * math.pi * j / sides
            ox = n[0] * math.cos(ang) * radius + b[0] * math.sin(ang) * radius
            oy = n[1] * math.cos(ang) * radius + b[1] * math.sin(ang) * radius
            oz = n[2] * math.cos(ang) * radius + b[2] * math.sin(ang) * radius
            ring.append(geom.add_vertex(p[0] + ox, p[1] + oy, p[2] + oz))
        rings.append(ring)
    for i in range(len(rings) - 1):
        for j in range(sides):
            a = rings[i][j]
            bb = rings[i][(j + 1) % sides]
            c = rings[i + 1][(j + 1) % sides]
            d = rings[i + 1][j]
            geom.add_face(a, bb, c)
            geom.add_face(a, c, d)
    start_center = geom.add_vertex(*pts[0])
    end_center = geom.add_vertex(*pts[-1])
    for j in range(sides):
        geom.add_face(start_center, rings[0][(j + 1) % sides], rings[0][j])
        geom.add_face(end_center, rings[-1][j], rings[-1][(j + 1) % sides])


def _ring_bank_geometry(side: int, ring_y: tuple[float, ...]) -> MeshGeometry:
    """Connected half-rings on a common hinge rail (origin A _ring_bank_geometry),
    parameterized by the N-station tuple ring_y."""
    geom = MeshGeometry()
    tube_r = 0.00165
    ring_r = 0.025
    center_x = 0.0
    center_z = 0.038
    pivot_x = side * 0.014
    pivot_z = 0.020
    rail_half = max(abs(y) for y in ring_y) + 0.015
    _tube(geom, [(0.0, -rail_half, 0.0), (0.0, rail_half, 0.0)], 0.0022, sides=12)
    if side < 0:
        angles = [math.radians(a) for a in range(230, 90, -8)]
        top_offset = -0.0022
    else:
        angles = [math.radians(a) for a in range(-50, 90, 8)]
        top_offset = 0.0022
    for y in ring_y:
        points: list[Vec3] = []
        for theta in angles:
            x = center_x + ring_r * math.cos(theta) + (
                top_offset if abs(theta - math.pi / 2) < 0.06 else 0.0
            )
            z = center_z + ring_r * math.sin(theta)
            points.append((x - pivot_x, y, z - pivot_z))
        _tube(geom, [(0.0, y, 0.0), points[0]], tube_r, sides=10)
        _tube(geom, points, tube_r, sides=10)
    return geom


# --------------------------------------------------------------------------- #
# Chassis (always present)                                                     #
# --------------------------------------------------------------------------- #


def _build_chassis(model: ArticulatedObject, r: ResolvedRingBlinderConfig) -> None:
    cw, bh, sw, bt = r.cover_w, r.binder_h, r.spine_w, BOARD_T
    sleeve_w = max(0.020, sw - 0.012)

    spine = model.part("spine")
    spine.visual(
        _rounded_panel("spine_board_mesh", sw, bh, bt, 0.007),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material="board",
        name="spine_board", material_class_id="plastic.opaque_generic",
    )
    for x, nm in ((-sw / 2, "front_crease"), (sw / 2, "back_crease")):
        spine.visual(
            Box((0.0022, bh - 0.020, 0.0012)),
            origin=Origin(xyz=(x, 0.0, bt / 2 + 0.0006)),
            material="edge",
            name=nm, material_class_id="plastic.opaque_generic",
        )
    spine.visual(
        Box((sleeve_w, bh - 0.034, 0.0016)),
        origin=Origin(xyz=(0.0, 0.0, bt / 2 + 0.0008)),
        material="pocket",
        name="inner_spine_sleeve", material_class_id="plastic.clear_rigid",
    )
    spine.inertial = Inertial.from_geometry(
        Box((sw, bh, bt)), mass=0.12, origin=Origin(xyz=(0.0, 0.0, 0.0))
    )

    front_cover = model.part("front_cover")
    front_cover.visual(
        _rounded_panel("front_cover_mesh", cw, bh, bt, 0.009),
        origin=Origin(xyz=(-cw / 2, 0.0, 0.0)),
        material="board",
        name="front_board", material_class_id="plastic.opaque_generic",
    )
    front_cover.visual(
        Box((cw - 0.030, bh - 0.040, 0.0012)),
        origin=Origin(xyz=(-cw / 2 - 0.004, 0.0, bt / 2 + 0.0006)),
        material="pocket",
        name="front_clear_pocket", material_class_id="plastic.clear_rigid",
    )
    front_cover.visual(
        Box((0.004, bh - 0.030, 0.0020)),
        origin=Origin(xyz=(-0.006, 0.0, bt / 2 + 0.0010)),
        material="edge",
        name="front_fold_reinforcement", material_class_id="plastic.opaque_generic",
    )
    front_cover.visual(
        Box((0.0010, bh - 0.030, bt)),
        origin=Origin(xyz=(-0.0005, 0.0, 0.0)),
        material="board",
        name="front_hinge_web", material_class_id="plastic.opaque_generic",
    )
    if r.closure == "foldover_strap":
        front_cover.visual(
            Box((0.012, 0.028, 0.010)),
            origin=Origin(xyz=(-cw, 0.0, bt / 2 + 0.004)),
            material="edge",
            name="strap_hinge_lug", material_class_id="plastic.opaque_generic",
        )
        front_cover.visual(
            Cylinder(radius=0.002, length=0.034),
            origin=Origin(xyz=(-cw, 0.0, bt / 2 + 0.004), rpy=(math.pi / 2, 0.0, 0.0)),
            material="dark_metal",
            name="strap_hinge_pin", material_class_id="metal.blackened_gunmetal",
        )
    front_cover.inertial = Inertial.from_geometry(
        Box((cw, bh, bt)), mass=0.20, origin=Origin(xyz=(-cw / 2, 0.0, 0.0))
    )

    back_cover = model.part("back_cover")
    back_cover.visual(
        _rounded_panel("back_cover_mesh", cw, bh, bt, 0.009),
        origin=Origin(xyz=(cw / 2, 0.0, 0.0)),
        material="board",
        name="back_board", material_class_id="plastic.opaque_generic",
    )
    back_cover.visual(
        Box((cw - 0.035, bh - 0.045, 0.0012)),
        origin=Origin(xyz=(cw / 2 + 0.006, 0.0, bt / 2 + 0.0006)),
        material="pocket",
        name="back_clear_pocket", material_class_id="plastic.clear_rigid",
    )
    back_cover.visual(
        Box((0.004, bh - 0.030, 0.0020)),
        origin=Origin(xyz=(0.006, 0.0, bt / 2 + 0.0010)),
        material="edge",
        name="back_fold_reinforcement", material_class_id="plastic.opaque_generic",
    )
    back_cover.visual(
        Box((0.0010, bh - 0.030, bt)),
        origin=Origin(xyz=(0.0005, 0.0, 0.0)),
        material="board",
        name="back_hinge_web", material_class_id="plastic.opaque_generic",
    )
    back_cover.inertial = Inertial.from_geometry(
        Box((cw, bh, bt)), mass=0.20, origin=Origin(xyz=(cw / 2, 0.0, 0.0))
    )

    model.articulation(
        "spine_to_front_cover",
        ArticulationType.REVOLUTE,
        parent=spine,
        child=front_cover,
        origin=Origin(xyz=(-sw / 2, 0.0, 0.0)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=6.0, velocity=2.5, lower=0.0, upper=1.5),
    )
    model.articulation(
        "spine_to_back_cover",
        ArticulationType.REVOLUTE,
        parent=spine,
        child=back_cover,
        origin=Origin(xyz=(sw / 2, 0.0, 0.0)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=6.0, velocity=2.5, lower=0.0, upper=1.5),
    )

    # Retained paper stack (functional context), FIXED on the back cover. Its
    # spine-side near edge must clear the ring-mechanism plate footprint (which,
    # when back-cover-mounted, lands on this same board); holes stay connected to
    # the block. Placement is single-sourced through `mount_fixed` so the FIXED
    # joint origin lands on real board+paper geometry (origin honesty).
    if r.mechanism_mount == "back_cover":
        plate_far = 0.064 if r.ring_mechanism == "single_moving" else 0.051
        paper_near = plate_far + 0.008
        hole_x = paper_near + 0.008
    else:
        paper_near = 0.023
        hole_x = 0.027
    paper_h = min(0.250, bh - 0.050)
    paper_w = max(0.060, cw - paper_near - 0.012)
    paper_cx = paper_near + paper_w / 2
    paper_stack = model.part("paper_stack")
    paper_stack.visual(
        Box((paper_w, paper_h, 0.006)),
        origin=Origin(xyz=(paper_cx, 0.0, bt / 2 + 0.003)),
        material="page",
        name="paper_stack_block", material_class_id="paper.plain_sheet",
    )
    for i, y in enumerate(r.ring_y):
        paper_stack.visual(
            Cylinder(radius=0.0060, length=0.0070),
            origin=Origin(xyz=(hole_x, y, bt / 2 + 0.004)),
            material="board",
            name=f"reinforced_hole_{i}", material_class_id="plastic.opaque_generic",
        )
    paper_stack.inertial = Inertial.from_geometry(
        Box((paper_w, paper_h, 0.006)),
        mass=0.10,
        origin=Origin(xyz=(paper_cx, 0.0, bt / 2 + 0.003)),
    )
    mount_fixed(
        model,
        joint_name="back_cover_to_paper_stack",
        parent="back_cover",
        child="paper_stack",
        parent_anchor=(hole_x, 0.0, bt / 2),
        child_anchor=(hole_x, 0.0, bt / 2),
    )


def _mount_origin(r: ResolvedRingBlinderConfig) -> tuple[str, Origin]:
    """Parent part + FIXED origin for the ring-mechanism plate.

    Both plates author their bottom face flush with the board top (world z =
    BOARD_T/2), so the FIXED origin z is 0 and lands on the board (origin honesty).
    """
    if r.mechanism_mount == "back_cover":
        return "back_cover", Origin(xyz=(PLATE_W / 2 + 0.004, 0.0, 0.0))
    return "spine", Origin()


# --------------------------------------------------------------------------- #
# Slot A — ring_mechanism: single_moving (origin B)                            #
# --------------------------------------------------------------------------- #


def _build_single_moving(model: ArticulatedObject, r: ResolvedRingBlinderConfig) -> None:
    ring_y = r.ring_y
    ring_bar = model.part("ring_bar")
    ring_bar.visual(
        Box((PLATE_W, PLATE_L, 0.004)),
        origin=Origin(xyz=(0.0, 0.0, PLATE_Z)),
        material="metal",
        name="metal_plate", material_class_id="metal.stainless_matte",
    )
    ring_bar.visual(
        Box((0.018, PLATE_L - 0.018, 0.005)),
        origin=Origin(xyz=(0.0, 0.0, PLATE_Z + 0.0035)),
        material="metal",
        name="raised_spine_channel", material_class_id="metal.stainless_matte",
    )
    ring_bar.visual(
        Cylinder(radius=0.0030, length=PLATE_L - 0.018),
        origin=Origin(xyz=(FIXED_HINGE_X, 0.0, 0.0175), rpy=(-math.pi / 2, 0.0, 0.0)),
        material="dark_metal",
        name="fixed_hinge_rod", material_class_id="metal.blackened_gunmetal",
    )
    for i, y in enumerate(ring_y):
        ring_bar.visual(
            Box((0.012, 0.015, 0.006)),
            origin=Origin(xyz=(FIXED_HINGE_X, y, 0.0115)),
            material="metal",
            name=f"fixed_saddle_{i}", material_class_id="metal.stainless_matte",
        )
        ring_bar.visual(
            Box((0.011, 0.015, 0.0075)),
            origin=Origin(xyz=(MOVING_HINGE_X, y, 0.01075)),
            material="metal",
            name=f"moving_saddle_{i}", material_class_id="metal.stainless_matte",
        )
        ring_bar.visual(
            Cylinder(radius=0.0034, length=0.0018),
            origin=Origin(xyz=(0.0, y + 0.020, 0.0105)),
            material="dark_metal",
            name=f"rivet_{i}", material_class_id="metal.blackened_gunmetal",
        )
        ring_bar.visual(
            _ring_tube(f"fixed_ring_half_{i}_mesh", _fixed_ring_points(r.ring_form, y)),
            material="metal",
            name=f"fixed_ring_half_{i}", material_class_id="metal.stainless_matte",
        )
    ring_bar.visual(
        Cylinder(radius=0.0085, length=0.011),
        origin=Origin(xyz=(0.0, 0.0, 0.0150)),
        material="metal",
        name="lever_center_standoff", material_class_id="metal.stainless_matte",
    )
    for nm, y in (("lower_lever_standoff", LEVER_Y[0]), ("upper_lever_standoff", LEVER_Y[1])):
        ring_bar.visual(
            Box((0.014, 0.018, 0.011)),
            origin=Origin(xyz=(0.0, y, 0.0150)),
            material="metal",
            name=nm, material_class_id="metal.stainless_matte",
        )
    ring_bar.inertial = Inertial.from_geometry(
        Box((PLATE_W, PLATE_L, 0.02)), mass=0.15, origin=Origin(xyz=(0.0, 0.0, 0.010))
    )

    parent_name, mount = _mount_origin(r)
    model.articulation(
        f"{parent_name}_to_ring_bar",
        ArticulationType.FIXED,
        parent=model.get_part(parent_name),
        child=ring_bar,
        origin=mount,
    )

    ring_halves = model.part("ring_halves")
    ring_halves.visual(
        Cylinder(radius=0.0030, length=PLATE_L - 0.018),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(-math.pi / 2, 0.0, 0.0)),
        material="dark_metal",
        name="moving_hinge_rod", material_class_id="metal.blackened_gunmetal",
    )
    for i, y in enumerate(ring_y):
        ring_halves.visual(
            Box((0.008, 0.013, 0.008)),
            origin=Origin(xyz=(0.0, y, 0.0025)),
            material="metal",
            name=f"moving_lug_{i}", material_class_id="metal.stainless_matte",
        )
        ring_halves.visual(
            _ring_tube(f"moving_ring_half_{i}_mesh", _moving_ring_points(r.ring_form, y)),
            material="metal",
            name=f"moving_ring_half_{i}", material_class_id="metal.stainless_matte",
        )
    ring_halves.inertial = Inertial.from_geometry(
        Box((0.03, PLATE_L - 0.018, 0.05)), mass=0.05, origin=Origin(xyz=(0.0, 0.0, 0.025))
    )
    model.articulation(
        "ring_bar_to_ring_halves",
        ArticulationType.REVOLUTE,
        parent=ring_bar,
        child=ring_halves,
        origin=Origin(xyz=(MOVING_HINGE_X, 0.0, 0.0175)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=3.0, velocity=3.0, lower=0.0, upper=0.62),
    )

    # Linked cam-strip lever (co-varies with single_moving; origin B lever_tabs).
    lever_tabs = model.part("lever_tabs")
    lever_tabs.visual(
        Box((0.011, PLATE_L - 0.018, 0.0022)),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material="dark_metal",
        name="lever_linkage", material_class_id="metal.blackened_gunmetal",
    )
    for i, y in enumerate(LEVER_Y):
        lever_tabs.visual(
            Box((0.026, 0.020, 0.0032)),
            origin=Origin(xyz=(0.0, y, 0.0065), rpy=(0.26 if y > 0 else -0.26, 0.0, 0.0)),
            material="metal",
            name=f"lever_tab_{i}", material_class_id="metal.stainless_matte",
        )
        lever_tabs.visual(
            Cylinder(radius=0.0025, length=0.012),
            origin=Origin(xyz=(0.0, y * 0.96, 0.003), rpy=(0.0, math.pi / 2, 0.0)),
            material="dark_metal",
            name=f"lever_pivot_pin_{i}", material_class_id="metal.blackened_gunmetal",
        )
    lever_tabs.inertial = Inertial.from_geometry(
        Box((0.03, PLATE_L - 0.018, 0.01)), mass=0.02, origin=Origin(xyz=(0.0, 0.0, 0.004))
    )
    model.articulation(
        "ring_bar_to_lever_tabs",
        ArticulationType.REVOLUTE,
        parent=ring_bar,
        child=lever_tabs,
        origin=Origin(xyz=(0.0, 0.0, LEVER_PIVOT_Z)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(
            effort=1.8, velocity=4.0, lower=-math.radians(5.0), upper=math.radians(5.0)
        ),
    )


# --------------------------------------------------------------------------- #
# Slot A — ring_mechanism: split_dual (origin A)                              #
# --------------------------------------------------------------------------- #


def _build_split_dual(model: ArticulatedObject, r: ResolvedRingBlinderConfig) -> None:
    ring_y = r.ring_y
    plate_base_z = BOARD_T / 2  # plate bottom flush with the board top face
    ring_plate = model.part("ring_plate")
    ring_plate.visual(
        Box((0.034, PLATE_L + 0.006, 0.004)),
        origin=Origin(xyz=(0.0, 0.0, plate_base_z + 0.002)),
        material="metal",
        name="metal_plate", material_class_id="metal.stainless_matte",
    )
    ring_plate.visual(
        Box((0.008, PLATE_L - 0.006, 0.003)),
        origin=Origin(xyz=(0.0, 0.0, plate_base_z + 0.0055)),
        material="dark_metal",
        name="center_raised_rib", material_class_id="metal.blackened_gunmetal",
    )
    for idx, x in enumerate((-0.014, 0.014)):
        ring_plate.visual(
            Box((0.005, PLATE_L - 0.006, 0.0138)),
            origin=Origin(xyz=(x, 0.0, plate_base_z + 0.0109)),
            material="dark_metal",
            name=f"ring_hinge_saddle_{idx}", material_class_id="metal.blackened_gunmetal",
        )
    for idx, y in enumerate(LEVER_Y):
        ring_plate.visual(
            Box((0.026, 0.011, 0.010)),
            origin=Origin(xyz=(0.0, y, plate_base_z + 0.009)),
            material="metal",
            name=f"lever_bracket_{idx}", material_class_id="metal.stainless_matte",
        )
        ring_plate.visual(
            Cylinder(radius=0.0045, length=0.030),
            origin=Origin(xyz=(0.0, y, plate_base_z + 0.0135), rpy=(0.0, math.pi / 2, 0.0)),
            material="metal",
            name=f"lever_pin_boss_{idx}", material_class_id="metal.stainless_matte",
        )
    ring_plate.inertial = Inertial.from_geometry(
        Box((0.034, PLATE_L, 0.02)), mass=0.15, origin=Origin(xyz=(0.0, 0.0, plate_base_z + 0.01))
    )

    parent_name, mount = _mount_origin(r)
    model.articulation(
        f"{parent_name}_to_ring_plate",
        ArticulationType.FIXED,
        parent=model.get_part(parent_name),
        child=ring_plate,
        origin=mount,
    )

    for side, arm_name, joint_name, axis in (
        (-1, "ring_arm_0", "plate_to_ring_arm_0", (0.0, -1.0, 0.0)),
        (1, "ring_arm_1", "plate_to_ring_arm_1", (0.0, 1.0, 0.0)),
    ):
        arm = model.part(arm_name)
        arm.visual(
            mesh_from_geometry(_ring_bank_geometry(side, ring_y), f"{arm_name}_bank"),
            origin=Origin(),
            material="metal",
            name=f"{arm_name}_halves", material_class_id="metal.stainless_matte",
        )
        arm.inertial = Inertial.from_geometry(
            Box((0.05, 2 * (max(abs(y) for y in ring_y) + 0.015), 0.05)),
            mass=0.04,
            origin=Origin(xyz=(0.0, 0.0, 0.02)),
        )
        model.articulation(
            joint_name,
            ArticulationType.REVOLUTE,
            parent=ring_plate,
            child=arm,
            origin=Origin(xyz=(side * 0.014, 0.0, plate_base_z + 0.020)),
            axis=axis,
            motion_limits=MotionLimits(effort=1.0, velocity=3.0, lower=0.0, upper=0.55),
        )

    for idx, y in enumerate(LEVER_Y):
        lever = model.part(f"lever_{idx}")
        sgn = 1.0 if y > 0 else -1.0
        lever.visual(
            Cylinder(radius=0.0030, length=0.026),
            origin=Origin(rpy=(0.0, math.pi / 2, 0.0)),
            material="metal",
            name="lever_pin", material_class_id="metal.stainless_matte",
        )
        lever.visual(
            Box((0.012, 0.008, 0.006)),
            origin=Origin(xyz=(0.0, sgn * 0.005, 0.002)),
            material="metal",
            name="lever_neck", material_class_id="metal.stainless_matte",
        )
        lever.visual(
            Box((0.018, 0.033, 0.004)),
            origin=Origin(xyz=(0.0, sgn * 0.020, 0.0048), rpy=(sgn * 0.22, 0.0, 0.0)),
            material="metal",
            name="lever_tab", material_class_id="metal.stainless_matte",
        )
        lever.visual(
            Cylinder(radius=0.0065, length=0.002),
            origin=Origin(xyz=(0.0, sgn * 0.034, 0.010), rpy=(math.pi / 2, 0.0, 0.0)),
            material="metal",
            name="rounded_thumb_end", material_class_id="metal.stainless_matte",
        )
        lever.inertial = Inertial.from_geometry(
            Box((0.02, 0.04, 0.012)), mass=0.01, origin=Origin(xyz=(0.0, sgn * 0.02, 0.005))
        )
        model.articulation(
            f"plate_to_lever_{idx}",
            ArticulationType.REVOLUTE,
            parent=ring_plate,
            child=lever,
            origin=Origin(xyz=(0.0, y, plate_base_z + 0.021)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=0.4, velocity=4.0, lower=-0.55, upper=0.55),
        )


# --------------------------------------------------------------------------- #
# Slot D — handle · Slot E — closure (optional parallel add-ons)               #
# --------------------------------------------------------------------------- #


def _build_folding_spine_handle(model: ArticulatedObject, r: ResolvedRingBlinderConfig) -> None:
    reach = 0.022
    span_y = 0.100
    arm_t = 0.008
    lug_w = lug_d = 0.014
    lug_t = 0.008
    spine = model.get_part("spine")
    handle = model.part("spine_handle")
    for i, y_off in enumerate((-span_y / 2, span_y / 2)):
        handle.visual(
            Box((lug_w, lug_d, lug_t)),
            origin=Origin(xyz=(0.0, y_off, -lug_t / 2)),
            material="dark_metal",
            name=f"handle_lug_{i}", material_class_id="metal.blackened_gunmetal",
        )
    for i, y_off in enumerate((-span_y / 2, span_y / 2)):
        handle.visual(
            Box((reach, arm_t, arm_t)),
            origin=Origin(xyz=(reach / 2, y_off, -lug_t / 2)),
            material="edge",
            name=f"handle_arm_{i}", material_class_id="plastic.opaque_generic",
        )
    handle.visual(
        Box((arm_t, span_y - arm_t, arm_t)),
        origin=Origin(xyz=(reach, 0.0, -lug_t / 2)),
        material="edge",
        name="handle_grab_bar", material_class_id="plastic.opaque_generic",
    )
    handle.inertial = Inertial.from_geometry(
        Box((reach + arm_t, span_y, lug_t)), mass=0.05, origin=Origin(xyz=(reach / 2, 0.0, 0.0))
    )
    model.articulation(
        "spine_to_handle",
        ArticulationType.REVOLUTE,
        parent=spine,
        child=handle,
        origin=Origin(xyz=(0.0, 0.0, -BOARD_T / 2)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=3.0, velocity=2.0, lower=0.0, upper=math.pi / 2),
    )


def _build_foldover_strap(model: ArticulatedObject, r: ResolvedRingBlinderConfig) -> None:
    strap_len = 0.130
    strap_w = 0.040
    strap_t = 0.003
    front_cover = model.get_part("front_cover")
    strap = model.part("closure_strap")
    strap.visual(
        Box((strap_len, strap_w, strap_t)),
        origin=Origin(xyz=(-strap_len / 2, 0.0, 0.0)),
        material="strap",
        name="strap_body", material_class_id="plastic.opaque_generic",
    )
    strap.visual(
        Cylinder(radius=0.004, length=0.026),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2, 0.0, 0.0)),
        material="catch",
        name="strap_hinge_loop", material_class_id="plastic.opaque_generic",
    )
    strap.visual(
        Box((0.020, 0.034, 0.005)),
        origin=Origin(xyz=(-strap_len + 0.010, 0.0, 0.0)),
        material="catch",
        name="strap_catch_tab", material_class_id="plastic.opaque_generic",
    )
    strap.inertial = Inertial.from_geometry(
        Box((strap_len, strap_w, strap_t)), mass=0.02, origin=Origin(xyz=(-strap_len / 2, 0.0, 0.0))
    )
    model.articulation(
        "front_cover_to_closure_strap",
        ArticulationType.REVOLUTE,
        parent=front_cover,
        child=strap,
        origin=Origin(xyz=(-r.cover_w, 0.0, BOARD_T / 2 + 0.004)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=1.0, velocity=4.0, lower=0.0, upper=2.5),
    )


# --------------------------------------------------------------------------- #
# Build                                                                        #
# --------------------------------------------------------------------------- #


def build_ring_blinder(
    config: RingBlinderConfig, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name="ring_blinder", assets=assets)
    for material, rgba in r.palette.items():
        model.material(material, rgba=rgba)

    _build_chassis(model, r)
    if r.ring_mechanism == "single_moving":
        _build_single_moving(model, r)
    else:
        _build_split_dual(model, r)
    if r.handle == "folding_spine":
        _build_folding_spine_handle(model, r)
    if r.closure == "foldover_strap":
        _build_foldover_strap(model, r)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_ring_blinder(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_ring_blinder(config_from_seed(seed), assets=assets)


def slot_choices_for_config(r: ResolvedRingBlinderConfig) -> list[tuple[str, str]]:
    return [
        ("ring_mechanism", r.ring_mechanism),
        ("ring_form", r.ring_form),
        ("mechanism_mount", r.mechanism_mount),
        ("handle_or_grip", r.handle),
        ("closure", r.closure),
        ("ring_count", f"n{r.ring_count}"),
    ]


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    return slot_choices_for_config(resolve_config(config_from_seed(seed)))


# --------------------------------------------------------------------------- #
# Tests                                                                        #
# --------------------------------------------------------------------------- #


def _visual_names(part: Part) -> set[str]:
    return {v.name for v in part.visuals if v.name is not None}


def _has_visual(part: Part, name: str) -> bool:
    return name in _visual_names(part)


def _allow(ctx: TestContext, a: Part, b: Part, *, elem_a: str, elem_b: str, reason: str) -> None:
    if _has_visual(a, elem_a) and _has_visual(b, elem_b):
        ctx.allow_overlap(a, b, elem_a=elem_a, elem_b=elem_b, reason=reason)


def _declare_overlaps(ctx: TestContext, model: ArticulatedObject, r: ResolvedRingBlinderConfig) -> None:
    names = {p.name for p in model.parts}
    n = r.ring_count
    if r.ring_mechanism == "single_moving" and {"ring_bar", "ring_halves"} <= names:
        ring_bar = model.get_part("ring_bar")
        ring_halves = model.get_part("ring_halves")
        for i in range(n):
            _allow(
                ctx, ring_bar, ring_halves,
                elem_a=f"moving_saddle_{i}", elem_b="moving_hinge_rod",
                reason="moving hinge rod is captured in the moving saddle bearing",
            )
            _allow(
                ctx, ring_bar, ring_halves,
                elem_a=f"moving_saddle_{i}", elem_b=f"moving_lug_{i}",
                reason="moving ring lug rides in the moving saddle bearing",
            )
            _allow(
                ctx, ring_bar, ring_halves,
                elem_a=f"fixed_ring_half_{i}", elem_b=f"moving_ring_half_{i}",
                reason="fixed and moving ring halves meet tip-to-tip at the closed ring",
            )
        if "lever_tabs" in names:
            lever_tabs = model.get_part("lever_tabs")
            _allow(
                ctx, ring_bar, lever_tabs,
                elem_a="lever_center_standoff", elem_b="lever_linkage",
                reason="linked lever strip rocks on the center standoff pivot",
            )
            _allow(
                ctx, ring_bar, lever_tabs,
                elem_a="raised_spine_channel", elem_b="lever_linkage",
                reason="linked lever cam strip rides just over the raised ring channel it actuates",
            )
            for i, side in ((0, "lower"), (1, "upper")):
                _allow(
                    ctx, ring_bar, lever_tabs,
                    elem_a=f"{side}_lever_standoff", elem_b=f"lever_tab_{i}",
                    reason="lever end tab rocks on its standoff pivot",
                )
                _allow(
                    ctx, ring_bar, lever_tabs,
                    elem_a=f"{side}_lever_standoff", elem_b=f"lever_pivot_pin_{i}",
                    reason="lever pivot pin is captured in its end standoff bearing",
                )
    if r.ring_mechanism == "split_dual" and "ring_plate" in names:
        plate = model.get_part("ring_plate")
        for arm_name in ("ring_arm_0", "ring_arm_1"):
            if arm_name in names:
                arm = model.get_part(arm_name)
                for idx in range(2):
                    _allow(
                        ctx, plate, arm,
                        elem_a=f"ring_hinge_saddle_{idx}", elem_b=f"{arm_name}_halves",
                        reason="ring bank hinge rail is captured under the plate hinge saddle",
                    )
        for idx in range(2):
            lever_name = f"lever_{idx}"
            if lever_name in names:
                lever = model.get_part(lever_name)
                _allow(
                    ctx, plate, lever,
                    elem_a=f"lever_pin_boss_{idx}", elem_b="lever_pin",
                    reason="lever pin is captured in the plate lever pin boss",
                )
                _allow(
                    ctx, plate, lever,
                    elem_a=f"lever_bracket_{idx}", elem_b="lever_pin",
                    reason="lever pin rides in the plate lever bracket",
                )
    if r.handle == "folding_spine" and "spine_handle" in names:
        for i in range(2):
            _allow(
                ctx, model.get_part("spine"), model.get_part("spine_handle"),
                elem_a="spine_board", elem_b=f"handle_lug_{i}",
                reason="folding handle lug pivots against the outer spine face (captured hinge)",
            )
    if r.closure == "foldover_strap" and "closure_strap" in names:
        fc = model.get_part("front_cover")
        back_cover = model.get_part("back_cover")
        strap = model.get_part("closure_strap")
        for elem_b, ec in (
            ("strap_hinge_loop", "hinge loop wraps the front-cover hinge lug"),
            ("strap_body", "strap root seats against the front-cover hinge lug"),
        ):
            _allow(ctx, fc, strap, elem_a="strap_hinge_lug", elem_b=elem_b,
                   reason=f"closure {ec}")
        _allow(ctx, fc, strap, elem_a="strap_hinge_pin", elem_b="strap_hinge_loop",
               reason="closure strap hinge loop is captured on the front-cover hinge pin")
        # Sequenced closure: the strap only folds fully over a CLOSED binder; in
        # the open display pose its full-fold travel sweeps through the flat back
        # cover / pages (AUTHORING §C sequenced-mechanism allowance, full travel kept).
        seq = "fold-over strap closes over the shut binder; its full travel passes the flat back cover in the open pose"
        for strap_elem in ("strap_body", "strap_catch_tab"):
            for bc_elem in ("back_board", "back_clear_pocket"):
                _allow(ctx, strap, back_cover, elem_a=strap_elem, elem_b=bc_elem, reason=seq)
            if "paper_stack" in names:
                _allow(ctx, strap, model.get_part("paper_stack"),
                       elem_a=strap_elem, elem_b="paper_stack_block", reason=seq)


def run_ring_blinder_tests(
    object_model: ArticulatedObject, config: RingBlinderConfig
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    _declare_overlaps(ctx, object_model, r)

    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)
    ctx.fail_if_joint_mating_has_gap()

    names = {p.name for p in object_model.parts}
    spine = object_model.get_part("spine")
    front_cover = object_model.get_part("front_cover")
    back_cover = object_model.get_part("back_cover")

    # Identity: covers share the spine hinge line.
    ctx.expect_contact(
        front_cover, spine, elem_a="front_board", elem_b="spine_board",
        contact_tol=0.001, name="front cover shares the spine hinge line",
    )
    ctx.expect_contact(
        back_cover, spine, elem_a="back_board", elem_b="spine_board",
        contact_tol=0.001, name="back cover shares the spine hinge line",
    )

    # Ring mechanism present with the right topology + at least one opening joint.
    if r.ring_mechanism == "single_moving":
        ctx.check("single_moving_parts", {"ring_bar", "ring_halves"} <= names)
        ring_joint = object_model.get_articulation("ring_bar_to_ring_halves")
        ctx.check(
            "ring_open_joint_revolute_y",
            ring_joint.articulation_type == ArticulationType.REVOLUTE
            and tuple(ring_joint.axis) == (0.0, 1.0, 0.0),
        )
        ring_halves = object_model.get_part("ring_halves")
        mid = r.ring_count // 2
        closed = ctx.part_element_world_aabb(ring_halves, elem=f"moving_ring_half_{mid}")
        with ctx.pose({ring_joint: 0.60}):
            opened = ctx.part_element_world_aabb(ring_halves, elem=f"moving_ring_half_{mid}")
        ctx.check(
            "ring halves swing outward to open",
            closed is not None and opened is not None and opened[1][0] > closed[1][0] + 0.015,
            details=f"closed={closed}, opened={opened}",
        )
        lever_joint = object_model.get_articulation("ring_bar_to_lever_tabs")
        lever_tabs = object_model.get_part("lever_tabs")
        rest = ctx.part_world_aabb(lever_tabs)
        with ctx.pose({lever_joint: math.radians(5.0)}):
            moved = ctx.part_world_aabb(lever_tabs)
        ctx.check(
            "lever tabs rock on a revolute pivot",
            rest is not None and moved is not None and abs(moved[1][2] - rest[1][2]) > 0.001,
            details=f"rest={rest}, moved={moved}",
        )
    else:
        ctx.check("split_dual_parts", {"ring_plate", "ring_arm_0", "ring_arm_1"} <= names)
        arm0 = object_model.get_part("ring_arm_0")
        arm1 = object_model.get_part("ring_arm_1")
        j0 = object_model.get_articulation("plate_to_ring_arm_0")
        j1 = object_model.get_articulation("plate_to_ring_arm_1")
        ctx.check(
            "both arms revolute",
            j0.articulation_type == ArticulationType.REVOLUTE
            and j1.articulation_type == ArticulationType.REVOLUTE,
        )
        cl0 = ctx.part_world_aabb(arm0)
        cl1 = ctx.part_world_aabb(arm1)
        with ctx.pose({j0: 0.50, j1: 0.50}):
            op0 = ctx.part_world_aabb(arm0)
            op1 = ctx.part_world_aabb(arm1)
        ctx.check(
            "split ring halves open outward on both sides",
            None not in (cl0, cl1, op0, op1)
            and op0[0][0] < cl0[0][0] - 0.004
            and op1[1][0] > cl1[1][0] + 0.004,
            details=f"cl0={cl0}, op0={op0}, cl1={cl1}, op1={op1}",
        )

    # Mount topology: back-cover mount follows the back cover when it hinges.
    plate_part = "ring_bar" if r.ring_mechanism == "single_moving" else "ring_plate"
    if r.mechanism_mount == "back_cover":
        back_hinge = object_model.get_articulation("spine_to_back_cover")
        rest_z = ctx.part_world_position(object_model.get_part(plate_part))
        with ctx.pose({back_hinge: 1.2}):
            open_z = ctx.part_world_position(object_model.get_part(plate_part))
        ctx.check(
            "back-mounted mechanism follows the back cover hinge",
            rest_z is not None and open_z is not None and open_z[2] > rest_z[2] + 0.010,
            details=f"rest={rest_z}, open={open_z}",
        )

    # Covers fold up from the flat-open binder.
    front_hinge = object_model.get_articulation("spine_to_front_cover")
    fr = ctx.part_world_aabb(front_cover)
    with ctx.pose({front_hinge: 1.25}):
        fc = ctx.part_world_aabb(front_cover)
    ctx.check(
        "front cover hinges upward",
        fr is not None and fc is not None and fc[1][2] > fr[1][2] + 0.15,
        details=f"rest={fr}, folded={fc}",
    )

    # Optional add-ons.
    if r.handle == "folding_spine":
        handle = object_model.get_part("spine_handle")
        hj = object_model.get_articulation("spine_to_handle")
        rest_bar = ctx.part_element_world_aabb(handle, elem="handle_grab_bar")
        with ctx.pose({hj: math.pi / 2}):
            dep_bar = ctx.part_element_world_aabb(handle, elem="handle_grab_bar")
        ctx.check(
            "folding spine handle swings out from the spine",
            rest_bar is not None and dep_bar is not None and dep_bar[1][2] < rest_bar[1][2] - 0.008,
            details=f"rest={rest_bar}, deployed={dep_bar}",
        )
    if r.closure == "foldover_strap":
        strap = object_model.get_part("closure_strap")
        sj = object_model.get_articulation("front_cover_to_closure_strap")
        rest_s = ctx.part_world_aabb(strap)
        with ctx.pose({sj: 1.5}):
            fold_s = ctx.part_world_aabb(strap)
        ctx.check(
            "closure strap folds up across the opening face",
            rest_s is not None and fold_s is not None and fold_s[1][2] > rest_s[1][2] + 0.04,
            details=f"rest={rest_s}, folded={fold_s}",
        )

    # Rule 5 — no 穿模 anywhere across the joint envelopes.
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=40, ignore_fixed=True)
    return ctx.report()


__all__ = [
    "Closure",
    "HandleGrip",
    "MechanismMount",
    "PaletteTheme",
    "ResolvedRingBlinderConfig",
    "RingBlinderConfig",
    "RingForm",
    "RingMechanism",
    "__modular__",
    "build_ring_blinder",
    "build_seeded_ring_blinder",
    "config_from_seed",
    "resolve_config",
    "run_ring_blinder_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
]
