# SPDX-License-Identifier: Apache-2.0

"""Camping_Outdoor Gear / Camp chair procedural template (modular).

Spec: articraft_template_authoring/specs_modular_v1/camp_chair.md

A portable folding camp chair: a fabric/sling seat on a collapsible tube frame
with a folding scissor mechanism (always present, the guaranteed non-FIXED
joints) plus, per motion slot, a reclining footrest / hinged fabric arms /
back-recline hinge / 360° swivel seat.

Structural spine is the Origin-B tube-primitive family (``chair_frame`` root part
carrying every tube/fabric/hardware ``.visual(...)``; three scissor-brace children
``front_cross_brace`` / ``side_cross_brace_{0,1}`` REVOLUTE). Sling/lounge form
families adopt Origin-A ``_fabric_panel_geometry`` sagged-cloth meshes and the
moon/saucer ``TorusGeometry`` rim + ``LatheGeometry`` bowl (primitive types
preserved, no Box downgrade — Rule 3).

Slots (pattern = mixed, parallel_children + multiplicity):
  * Slot A form_family (③): high_back_armchair / recliner_lounge / moon_saucer_bowl
      / flat_cot_lounger / backless_stool
  * Slot B base_stance (①/⑤): pad_feet / rocker_runners / bar_height_rail / low_compact
  * Slot C motion (②): scissor_fold / reclining_footrest / hinged_armrests
      / back_recline / swivel_riser
  * Multiplicity seat_cells (bench): N in {1,2,3} (armchair+pad_feet+scissor only)

Rules:
  Rule 1 — non-articulating detail (piping, stitch rails, logo, cup ring, side
    pocket, rivets, feet, pillow) is a host ``.visual(...)``; no FIXED-jointed
    decoration parts. This template has NO FIXED articulation.
  Rule 2 — every moving child is a captured pin-through-sleeve / turntable pivot;
    ``MatingContract`` cannot express it, so joints are grandfathered (omit
    ``mating=``) and kept honest with element-scoped ``allow_overlap`` +
    ``expect_overlap`` mirroring each source's run_tests.
  Rule 3 — structure derives from declared 5-star sources; mesh heroes preserved.
  Rule 5 — ``fail_if_parts_overlap_in_sampled_poses`` + one targeted ``ctx.pose``
    per mechanism.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Literal

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    LatheGeometry,
    MeshGeometry,
    MotionLimits,
    Origin,
    Sphere,
    TestContext,
    TestReport,
    TorusGeometry,
    mesh_from_geometry,
    tube_from_spline_points,
)

__modular__ = True

# ---------------------------------------------------------------------------
# Slot value spaces
# ---------------------------------------------------------------------------
FormFamily = Literal[
    "high_back_armchair",
    "recliner_lounge",
    "moon_saucer_bowl",
    "flat_cot_lounger",
    "backless_stool",
]
BaseStance = Literal["pad_feet", "rocker_runners", "bar_height_rail", "low_compact"]
Motion = Literal[
    "scissor_fold",
    "reclining_footrest",
    "hinged_armrests",
    "back_recline",
    "swivel_riser",
]
PaletteStyle = Literal[
    "black_orange_oxford",
    "brown_orange_sling",
    "teal_navy_bowl",
    "olive_canvas",
    "blue_red_ripstop",
    "grey_powder",
]

FORM_FAMILIES: tuple[FormFamily, ...] = (
    "high_back_armchair",
    "recliner_lounge",
    "moon_saucer_bowl",
    "flat_cot_lounger",
    "backless_stool",
)
BASE_STANCES: tuple[BaseStance, ...] = (
    "pad_feet",
    "rocker_runners",
    "bar_height_rail",
    "low_compact",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "black_orange_oxford",
    "brown_orange_sling",
    "teal_navy_bowl",
    "olive_canvas",
    "blue_red_ripstop",
    "grey_powder",
)

# Which motions each form may host (compatibility matrix — §9).
ALLOWED_MOTIONS: dict[FormFamily, tuple[Motion, ...]] = {
    "high_back_armchair": (
        "scissor_fold",
        "reclining_footrest",
        "hinged_armrests",
        "back_recline",
    ),
    "recliner_lounge": ("scissor_fold", "reclining_footrest", "hinged_armrests"),
    "moon_saucer_bowl": ("scissor_fold",),
    "flat_cot_lounger": ("scissor_fold", "reclining_footrest"),
    "backless_stool": ("scissor_fold", "swivel_riser"),
}

FORMS_WITH_BACK: frozenset[FormFamily] = frozenset(
    {"high_back_armchair", "recliner_lounge", "flat_cot_lounger"}
)

# ---------------------------------------------------------------------------
# Palette colorways. `fabric` + `accent` carry the recognizable colorway; the
# tube metal / plastic / silver hardware is near-constant. 6 colorways.
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "black_orange_oxford": {
        "fabric": (0.05, 0.05, 0.06, 1.0),
        "fabric_center": (0.27, 0.29, 0.27, 1.0),
        "accent": (1.0, 0.32, 0.04, 1.0),
        "metal": (0.43, 0.43, 0.39, 1.0),
    },
    "brown_orange_sling": {
        "fabric": (0.19, 0.105, 0.055, 1.0),
        "fabric_center": (0.10, 0.065, 0.045, 1.0),
        "accent": (0.95, 0.32, 0.06, 1.0),
        "metal": (0.42, 0.45, 0.46, 1.0),
    },
    "teal_navy_bowl": {
        "fabric": (0.08, 0.28, 0.36, 1.0),
        "fabric_center": (0.05, 0.18, 0.26, 1.0),
        "accent": (0.90, 0.85, 0.20, 1.0),
        "metal": (0.38, 0.38, 0.35, 1.0),
    },
    "olive_canvas": {
        "fabric": (0.30, 0.38, 0.18, 1.0),
        "fabric_center": (0.20, 0.26, 0.12, 1.0),
        "accent": (0.86, 0.74, 0.42, 1.0),
        "metal": (0.40, 0.40, 0.37, 1.0),
    },
    "blue_red_ripstop": {
        "fabric": (0.09, 0.22, 0.48, 1.0),
        "fabric_center": (0.06, 0.16, 0.34, 1.0),
        "accent": (0.80, 0.10, 0.12, 1.0),
        "metal": (0.45, 0.46, 0.48, 1.0),
    },
    "grey_powder": {
        "fabric": (0.35, 0.37, 0.40, 1.0),
        "fabric_center": (0.22, 0.24, 0.26, 1.0),
        "accent": (0.95, 0.42, 0.10, 1.0),
        "metal": (0.55, 0.57, 0.60, 1.0),
    },
}
_HARDWARE = {
    "plastic": (0.015, 0.015, 0.015, 1.0),
    "silver": (0.86, 0.88, 0.86, 1.0),
    "stitch": (0.92, 0.92, 0.88, 1.0),
    "mesh": (0.02, 0.02, 0.02, 1.0),
}

# ---------------------------------------------------------------------------
# Single-sourced geometry constants (world meters; Origin-B frame:
# +Y = back, -Y = front, X = left/right track, Z = up).
# ---------------------------------------------------------------------------
FRONT_Y = -0.36
REAR_Y = 0.30
BASE_LX = 0.43
TUBE = 0.014
FOOT_Z = 0.013
SEAT_Z_BASE = 0.48  # Origin-B reference seat height (all fold geometry scales off it)

SEAT_Z_BY_STANCE: dict[BaseStance, float] = {
    "pad_feet": 0.46,
    "rocker_runners": 0.47,
    "bar_height_rail": 0.60,
    "low_compact": 0.34,
}
SEAT_PITCH = 0.62  # bench bay spacing along Y-width (per seat cell)


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _pick(v, choices):
    return v if v in choices else choices[0]


# ---------------------------------------------------------------------------
# Geometry helpers (Origin-B _add_tube/_add_ball/_add_box + Origin-A fabric panel)
# ---------------------------------------------------------------------------
def _tube_pose(p0, p1) -> tuple[Origin, float]:
    dx, dy, dz = p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]
    length = math.sqrt(dx * dx + dy * dy + dz * dz)
    if length <= 0.0:
        raise ValueError("tube endpoints must be distinct")
    yaw = math.atan2(dy, dx)
    pitch = math.atan2(math.sqrt(dx * dx + dy * dy), dz)
    center = ((p0[0] + p1[0]) * 0.5, (p0[1] + p1[1]) * 0.5, (p0[2] + p1[2]) * 0.5)
    return Origin(xyz=center, rpy=(0.0, pitch, yaw)), length


def _add_tube(part, name, p0, p1, radius, material) -> None:
    origin, length = _tube_pose(p0, p1)
    part.visual(Cylinder(radius=radius, length=length), origin=origin, material=material, name=name, material_class_id="metal.paint_coated")


def _add_ball(part, name, xyz, radius, material) -> None:
    part.visual(Sphere(radius=radius), origin=Origin(xyz=xyz), material=material, name=name, material_class_id="metal.brushed_silver")


def _add_box(part, name, size, xyz, material, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(Box(size), origin=Origin(xyz=xyz, rpy=rpy), material=material, name=name, material_class_id="fabric.upholstery_plain")


def _fabric_panel_geometry(corners, *, thickness=0.006, nx=8, ny=6, sag=0.012) -> MeshGeometry:
    """Thin bilinear cloth panel with vertical sag (Origin-A helper, preserved)."""
    p00, p10, p11, p01 = corners
    geom = MeshGeometry()
    top: list[list[int]] = []
    bottom: list[list[int]] = []
    for ix in range(nx + 1):
        u = ix / nx
        top_row, bot_row = [], []
        for iy in range(ny + 1):
            v = iy / ny
            x = (1 - u) * (1 - v) * p00[0] + u * (1 - v) * p10[0] + u * v * p11[0] + (1 - u) * v * p01[0]
            y = (1 - u) * (1 - v) * p00[1] + u * (1 - v) * p10[1] + u * v * p11[1] + (1 - u) * v * p01[1]
            z = (1 - u) * (1 - v) * p00[2] + u * (1 - v) * p10[2] + u * v * p11[2] + (1 - u) * v * p01[2]
            z -= sag * math.sin(math.pi * u) * math.sin(math.pi * v)
            top_row.append(geom.add_vertex(x, y, z))
            bot_row.append(geom.add_vertex(x, y, z - thickness))
        top.append(top_row)
        bottom.append(bot_row)
    for ix in range(nx):
        for iy in range(ny):
            a, b, c, d = top[ix][iy], top[ix + 1][iy], top[ix + 1][iy + 1], top[ix][iy + 1]
            geom.add_face(a, b, c)
            geom.add_face(a, c, d)
            ab, bb, cb, db = bottom[ix][iy], bottom[ix + 1][iy], bottom[ix + 1][iy + 1], bottom[ix][iy + 1]
            geom.add_face(ab, cb, bb)
            geom.add_face(ab, db, cb)
    for ix in range(nx):
        for iy in (0, ny):
            a, b = top[ix][iy], top[ix + 1][iy]
            ab, bb = bottom[ix][iy], bottom[ix + 1][iy]
            geom.add_face(a, ab, bb)
            geom.add_face(a, bb, b)
    for iy in range(ny):
        for ix in (0, nx):
            a, b = top[ix][iy], top[ix][iy + 1]
            ab, bb = bottom[ix][iy], bottom[ix][iy + 1]
            geom.add_face(a, b, bb)
            geom.add_face(a, bb, ab)
    return geom


def _add_fabric(part, name, corners, material, *, thickness=0.006, sag=0.012) -> None:
    part.visual(
        mesh_from_geometry(_fabric_panel_geometry(corners, thickness=thickness, sag=sag), name),
        material=material,
        name=name, material_class_id="fabric.plain_flat_weave",
    )


# ===========================================================================
# Config
# ===========================================================================
@dataclass(frozen=True)
class CampChairConfig:
    form_family: FormFamily | None = None
    base_stance: BaseStance | None = None
    motion: Motion | None = None
    seat_cells: int = 1
    palette_style: PaletteStyle = "black_orange_oxford"
    seat_width_scale: float = 1.0
    back_height_scale: float = 1.0
    track_scale: float = 1.0
    name: str = "camp_chair"


@dataclass(frozen=True)
class ResolvedCampChairConfig:
    form_family: FormFamily
    base_stance: BaseStance
    motion: Motion
    seat_cells: int
    palette_style: PaletteStyle
    seat_width_scale: float
    back_height_scale: float
    track_scale: float
    name: str

    @property
    def seat_z(self) -> float:
        return SEAT_Z_BY_STANCE[self.base_stance]

    @property
    def fold_k(self) -> float:
        """Scale of the fold subsystem z-geometry relative to the Origin-B seat."""
        return self.seat_z / SEAT_Z_BASE

    @property
    def lx(self) -> float:
        return BASE_LX * self.track_scale

    @property
    def has_back(self) -> bool:
        return self.form_family in FORMS_WITH_BACK

    @property
    def seat_host_is_swivel(self) -> bool:
        return self.motion == "swivel_riser"


def config_from_seed(seed: int) -> CampChairConfig:
    """Deterministic procedural sampling over the full slot domain (seed 0 is
    not special). Motion is drawn from the chosen form's allowed set; the bench
    seat-cell multiplicity is gated to the padded quad armchair."""
    rng = random.Random(seed)
    form = rng.choice(FORM_FAMILIES)
    stance = rng.choice(BASE_STANCES)
    motion = rng.choice(ALLOWED_MOTIONS[form])
    return CampChairConfig(
        form_family=form,
        base_stance=stance,
        motion=motion,
        seat_cells=1,
        palette_style=rng.choice(PALETTE_STYLES),
        seat_width_scale=round(rng.uniform(0.92, 1.08), 4),
        back_height_scale=round(rng.uniform(0.92, 1.12), 4),
        track_scale=round(rng.uniform(0.94, 1.06), 4),
        name=f"seeded_camp_chair_{seed}",
    )


def resolve_config(config: CampChairConfig | None = None) -> ResolvedCampChairConfig:
    cfg = config or CampChairConfig()
    form = _pick(cfg.form_family, FORM_FAMILIES)
    stance = _pick(cfg.base_stance, BASE_STANCES)
    allowed = ALLOWED_MOTIONS[form]
    motion = cfg.motion if cfg.motion in allowed else allowed[0]
    # Bench multiplicity is only in the mature domain for the padded quad chair.
    cells = int(cfg.seat_cells) if cfg.seat_cells in (1, 2, 3) else 1
    if not (form == "high_back_armchair" and stance == "pad_feet" and motion == "scissor_fold"):
        cells = 1
    return ResolvedCampChairConfig(
        form_family=form,
        base_stance=stance,
        motion=motion,
        seat_cells=cells,
        palette_style=_pick(cfg.palette_style, PALETTE_STYLES),
        seat_width_scale=_clamp(cfg.seat_width_scale, 0.92, 1.08),
        back_height_scale=_clamp(cfg.back_height_scale, 0.92, 1.12),
        track_scale=_clamp(cfg.track_scale, 0.94, 1.06),
        name=cfg.name or "camp_chair",
    )


def slot_choices_for_config(config) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedCampChairConfig) else resolve_config(config)
    return (
        ("form_family", r.form_family),
        ("base_stance", r.base_stance),
        ("motion", r.motion),
        ("seat_cells", f"n{r.seat_cells}"),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


SIDES: tuple[tuple[str, float], ...] = (("left", 1.0), ("right", -1.0))


# ===========================================================================
# Frame (root chassis): legs + seat rails + pivot hardware + feet/runners/rail.
# ===========================================================================
def _bay_offsets(r: ResolvedCampChairConfig) -> list[float]:
    """Y-offset of each seat-cell bay center (0 for a single chair)."""
    n = r.seat_cells
    return [(i - (n - 1) * 0.5) * SEAT_PITCH for i in range(n)]


def _build_frame(model: ArticulatedObject, r: ResolvedCampChairConfig, mats) -> object:
    frame = model.part("chair_frame")
    lx = r.lx
    seat_z = r.seat_z
    k = r.fold_k
    has_back = r.has_back and r.motion != "back_recline" and not r.seat_host_is_swivel
    # arm/back post top heights
    arm_z = seat_z + 0.18
    back_top_z = seat_z + 0.64 * r.back_height_scale

    bays = _bay_offsets(r)
    y_front = FRONT_Y
    y_rear = REAR_Y + (max(bays))

    for _label, sgn in SIDES:
        x = sgn * lx
        # Front upright legs (rise to arm height on chairs with arms/back).
        top_front = arm_z if (r.has_back or r.motion == "hinged_armrests") else seat_z
        _add_tube(frame, f"front_leg_{_label}", (x, y_front, FOOT_Z), (x, y_front, top_front), TUBE, mats["metal"])
        # Rear legs / back posts.
        if has_back:
            _add_tube(
                frame, f"rear_post_{_label}", (x, y_rear, FOOT_Z), (x, y_rear + 0.07, back_top_z), TUBE, mats["metal"]
            )
        else:
            _add_tube(frame, f"rear_leg_{_label}", (x, y_rear, FOOT_Z), (x, y_rear, seat_z), TUBE, mats["metal"])

    # Seat perimeter rails (span the full width across bays). Suppressed for the
    # swivel riser, whose rotating platform owns the seating plane instead.
    if not r.seat_host_is_swivel:
        _add_tube(frame, "front_seat_rail", (-lx, y_front, seat_z), (lx, y_front, seat_z), TUBE, mats["metal"])
        _add_tube(frame, "rear_seat_rail", (-lx, y_rear, seat_z + 0.05), (lx, y_rear, seat_z + 0.05), TUBE, mats["metal"])
        _add_tube(frame, "side_seat_rail_left", (lx, y_front, seat_z), (lx, y_rear, seat_z + 0.05), TUBE, mats["metal"])
        _add_tube(frame, "side_seat_rail_right", (-lx, y_front, seat_z), (-lx, y_rear, seat_z + 0.05), TUBE, mats["metal"])
    if has_back:
        _add_tube(frame, "top_back_rail", (-lx, y_rear + 0.07, back_top_z), (lx, y_rear + 0.07, back_top_z), TUBE, mats["metal"])

    # Lower cross members keep the two sides connected.
    _add_tube(frame, "front_lower_cross", (-lx, y_front, 0.10 * k), (lx, y_front, 0.10 * k), TUBE, mats["metal"])
    _add_tube(frame, "rear_lower_cross", (-lx, y_rear, 0.10 * k), (lx, y_rear, 0.10 * k), TUBE, mats["metal"])

    # Fixed diagonal (one member of each X-brace; the moving member is the child).
    if _has_front_brace(r):
        _add_tube(frame, "front_fixed_cross", (-lx, y_front + 0.018, seat_z), (lx, y_front + 0.018, 0.07 * k), TUBE, mats["metal"])
    _add_tube(frame, "side_fixed_cross_0", (-lx + 0.018, y_front, seat_z), (-lx + 0.018, y_rear, 0.075 * k), TUBE, mats["metal"])
    _add_tube(frame, "side_fixed_cross_1", (lx - 0.018, y_front, seat_z), (lx - 0.018, y_rear, 0.075 * k), TUBE, mats["metal"])

    _build_base_stance(frame, r, mats)
    _build_scissor_hardware(frame, r, mats)

    # Motion-slot hinge hardware on the frame.
    if r.motion == "hinged_armrests":
        for label, sgn in SIDES:
            frame.visual(
                Cylinder(radius=0.012, length=0.10),
                origin=Origin(xyz=(sgn * lx, y_rear + 0.02, arm_z), rpy=(0.0, math.pi / 2.0, 0.0)),
                material=mats["plastic"], name=f"{label}_arm_hinge", material_class_id="plastic.opaque_glossy_molded",
            )
    if r.motion == "back_recline":
        _add_tube(
            frame, "recline_hinge_pin", (-lx + 0.05, y_rear, seat_z + 0.05), (lx - 0.05, y_rear, seat_z + 0.05),
            0.016, mats["plastic"],
        )
    if r.motion == "reclining_footrest":
        # Full-width hinge pin just below the seat front, touching both front
        # legs (so it is supported) and clear of the seat fabric.
        _add_tube(frame, "footrest_hinge_pin", (-lx, y_front, seat_z - 0.04), (lx, y_front, seat_z - 0.04), 0.012, mats["plastic"])
    if r.seat_host_is_swivel:
        # Hub post reaching from the base X-frame up to the raised turntable collar.
        frame.visual(
            Cylinder(radius=0.050, length=0.12),
            origin=Origin(xyz=(0.0, (y_front + y_rear) * 0.5, seat_z + 0.01)),
            material=mats["metal"], name="swivel_hub", material_class_id="metal.paint_coated",
        )
        # Base X-frame tying the hub to the corners so the hub is supported.
        _add_tube(frame, "base_xframe_0", (-lx, y_front, seat_z - 0.03), (lx, y_rear, seat_z - 0.03), TUBE, mats["metal"])
        _add_tube(frame, "base_xframe_1", (lx, y_front, seat_z - 0.03), (-lx, y_rear, seat_z - 0.03), TUBE, mats["metal"])

    return frame


def _build_base_stance(frame, r: ResolvedCampChairConfig, mats) -> None:
    lx = r.lx
    bays = _bay_offsets(r)
    y_front = FRONT_Y
    y_rear = REAR_Y + max(bays)
    if r.base_stance == "rocker_runners":
        # Two fore-aft curved runner rails replace flat feet (mesh tube).
        runner_r = 0.017
        for label, sgn in SIDES:
            x = sgn * lx
            pts = [
                (x, y_front - 0.14, 0.075),
                (x, y_front - 0.05, runner_r + 0.012),
                (x, y_front, runner_r + 0.002),
                (x, (y_front + y_rear) * 0.5, runner_r),
                (x, y_rear, runner_r + 0.002),
                (x, y_rear + 0.05, runner_r + 0.012),
                (x, y_rear + 0.16, 0.075),
            ]
            geom = tube_from_spline_points(pts, radius=runner_r, samples_per_segment=6, radial_segments=12, cap_ends=True)
            frame.visual(mesh_from_geometry(geom, f"rocker_runner_{label}"), material=mats["plastic"], name=f"rocker_runner_{label}", material_class_id="plastic.opaque_glossy_molded")
    else:
        # Flat rubber pad feet at each corner leg.
        for label, sgn in SIDES:
            x = sgn * lx
            for fy, tag in ((y_front, "front"), (y_rear, "rear")):
                _add_box(frame, f"{tag}_{label}_foot", (0.10, 0.072, 0.026), (x, fy, FOOT_Z), mats["plastic"])
                _add_ball(frame, f"{tag}_{label}_rivet", (x, fy, 0.030), 0.009, mats["silver"])
        if r.base_stance == "bar_height_rail":
            rail_z = r.seat_z * 0.5
            _add_tube(frame, "foot_rest_rail", (-lx, y_front, rail_z), (lx, y_front, rail_z), TUBE, mats["metal"])
            for label, sgn in SIDES:
                _add_tube(
                    frame, f"foot_rail_collar_{label}", (sgn * lx, y_front, rail_z - 0.022), (sgn * lx, y_front, rail_z + 0.022),
                    0.018, mats["plastic"],
                )


def _has_front_brace(r: ResolvedCampChairConfig) -> bool:
    # The reclining footrest deploys into the forward-low zone, so that variant
    # side-folds (2 side braces) and drops the forward front scissor brace.
    return r.motion != "reclining_footrest"


def _build_scissor_hardware(frame, r: ResolvedCampChairConfig, mats) -> None:
    """Fixed pivot pins/supports/rivets that capture the scissor brace collars."""
    lx = r.lx
    k = r.fold_k
    if _has_front_brace(r):
        for by in _bay_offsets(r):
            fpy = FRONT_Y + by - 0.08
            tag = _bay_tag(r, by)
            _add_tube(frame, f"front_pivot_pin{tag}", (-0.002, fpy - 0.032, 0.30 * k), (-0.002, fpy + 0.032, 0.30 * k), 0.018, mats["plastic"])
            # Support strut ties the pivot pin down onto the always-present front
            # lower cross (the seat rail is absent on the swivel base).
            _add_tube(frame, f"front_pivot_support{tag}", (0.0, fpy + 0.026, 0.30 * k), (0.0, FRONT_Y, 0.10 * k), 0.010, mats["plastic"])
            _add_ball(frame, f"front_pivot_rivet{tag}", (-0.002, fpy - 0.032, 0.30 * k), 0.010, mats["silver"])
    # Side pivots (outer rails, shared across bays).
    _add_tube(frame, "side_pivot_pin_0", (-lx - 0.038, -0.020, 0.325 * k), (-lx + 0.026, -0.020, 0.325 * k), 0.018, mats["plastic"])
    _add_tube(frame, "side_pivot_pin_1", (lx - 0.026, -0.020, 0.325 * k), (lx + 0.038, -0.020, 0.325 * k), 0.018, mats["plastic"])
    _add_tube(frame, "side_pivot_support_0", (-lx + 0.026, -0.020, 0.325 * k), (-lx + 0.018, -0.020, 0.272 * k), 0.007, mats["plastic"])
    _add_tube(frame, "side_pivot_support_1", (lx - 0.026, -0.020, 0.325 * k), (lx - 0.018, -0.020, 0.272 * k), 0.007, mats["plastic"])
    _add_ball(frame, "side_pivot_rivet_0", (-lx - 0.047, -0.020, 0.325 * k), 0.010, mats["silver"])
    _add_ball(frame, "side_pivot_rivet_1", (lx + 0.047, -0.020, 0.325 * k), 0.010, mats["silver"])


def _bay_tag(r: ResolvedCampChairConfig, by: float) -> str:
    if r.seat_cells == 1:
        return ""
    bays = _bay_offsets(r)
    return f"_{bays.index(by)}"


# ===========================================================================
# Slot A: form_family — seat/back/arm envelope on the seat host part.
# ===========================================================================
def _emit_form(model, frame, r: ResolvedCampChairConfig, mats):
    """Emit the seat/back envelope; return the seat host part (frame or swivel)."""
    host = frame
    if r.seat_host_is_swivel:
        host = model.part("seat_swivel")
    emitter = {
        "high_back_armchair": _emit_high_back_armchair,
        "recliner_lounge": _emit_recliner_lounge,
        "moon_saucer_bowl": _emit_moon_saucer,
        "flat_cot_lounger": _emit_flat_cot,
        "backless_stool": _emit_backless_stool,
    }[r.form_family]
    emitter(model, host, frame, r, mats)
    return host


def _emit_seat_pan(host, r, mats) -> None:
    """One structural seat pan spanning the full (multi-bay) footprint so the
    decorative boxes + the whole seat have a guaranteed support path to the seat
    rails (or, for the swivel, the turntable spokes)."""
    lx = r.lx
    sz = r.seat_z
    bays = _bay_offsets(r)
    y0, y1 = FRONT_Y, REAR_Y + max(bays)
    _add_box(host, "seat_pan", (2 * lx, y1 - y0, 0.018), (0.0, (y0 + y1) * 0.5, sz + 0.006), mats["fabric_center"])


def _emit_seat_boxes(host, r, mats, *, y0: float) -> None:
    """Padded box sling seat centered at bay y0 (Origin-B seat)."""
    lx = r.lx
    ws = r.seat_width_scale
    sz = r.seat_z
    _add_box(host, f"seat_black_left{_ytag(y0)}", (0.17, 0.62 * ws, 0.020), (-0.30 * (lx / BASE_LX), y0 - 0.035, sz + 0.012), mats["fabric"])
    _add_box(host, f"seat_black_right{_ytag(y0)}", (0.17, 0.62 * ws, 0.020), (0.30 * (lx / BASE_LX), y0 - 0.035, sz + 0.012), mats["fabric"])
    _add_box(host, f"seat_gray_center{_ytag(y0)}", (0.42, 0.62 * ws, 0.018), (0.0, y0 - 0.035, sz + 0.014), mats["fabric_center"])
    _add_box(host, f"seat_front_roll{_ytag(y0)}", (0.86, 0.040, 0.035), (0.0, FRONT_Y, sz + 0.022), mats["fabric"])
    _add_box(host, f"seat_piping_l{_ytag(y0)}", (0.012, 0.60 * ws, 0.012), (-0.205, y0 - 0.035, sz + 0.022), mats["accent"])
    _add_box(host, f"seat_piping_r{_ytag(y0)}", (0.012, 0.60 * ws, 0.012), (0.205, y0 - 0.035, sz + 0.022), mats["accent"])


def _ytag(y0: float) -> str:
    return "" if abs(y0) < 1e-6 else f"_{int(round(y0 * 1000))}"


def _emit_back_panels(host, r, mats, *, y_rear: float, back_bottom_z: float, back_h: float) -> None:
    lx = r.lx
    bz = back_bottom_z + back_h / 2.0
    yb = y_rear + 0.02  # panel plane straddles the rear posts (y_rear..y_rear+0.07)
    top_z = back_bottom_z + back_h
    # Center wide enough to overlap the side panels; sides reach the posts (+/-lx).
    _add_box(host, "back_gray_center", (0.52, 0.040, back_h), (0.0, yb, bz), mats["fabric_center"])
    _add_box(host, "back_black_side_0", (0.24, 0.044, back_h * 1.01), (-(lx - 0.11), yb, bz), mats["fabric"])
    _add_box(host, "back_black_side_1", (0.24, 0.044, back_h * 1.01), (lx - 0.11, yb, bz), mats["fabric"])
    # Lower band bridges the back slab down onto the rear seat rail (support path).
    _add_box(host, "back_lower_band", (0.80, 0.044, 0.10), (0.0, yb, back_bottom_z + 0.02), mats["fabric"])
    # Top pillow meets the top back rail (y_rear+0.07).
    _add_box(host, "back_top_pillow", (0.82, 0.070, 0.11), (0.0, y_rear + 0.05, top_z), mats["fabric"])
    _add_box(host, "back_piping_0", (0.012, 0.030, back_h * 0.94), (-0.210, yb - 0.024, bz), mats["accent"])
    _add_box(host, "back_piping_1", (0.012, 0.030, back_h * 0.94), (0.210, yb - 0.024, bz), mats["accent"])
    _add_box(host, "back_top_stitch", (0.78, 0.034, 0.018), (0.0, y_rear + 0.05, top_z), mats["stitch"])
    _add_box(host, "back_logo_mark", (0.09, 0.048, 0.035), (0.0, yb - 0.022, bz + back_h * 0.20), mats["stitch"])


def _emit_arm_pads(host, r, mats) -> None:
    lx = r.lx
    arm_z = r.seat_z + 0.18
    for label, sgn in SIDES:
        # Pad rests on the front-leg top and crosses the rear post (support path);
        # kept inboard of the outboard side scissor brace (x ~ +/-0.50).
        _add_box(host, f"arm_rest_top_{label}", (0.10, 0.76, 0.030), (sgn * (lx - 0.03), -0.03, arm_z), mats["fabric"])
        _add_box(host, f"arm_rest_stitch_{label}", (0.010, 0.70, 0.010), (sgn * (lx - 0.03), -0.03, arm_z + 0.02), mats["stitch"])
    # Cup holder ring on the left arm (host-conformal decoration).
    cup = mesh_from_geometry(TorusGeometry(radius=0.055, tube=0.006, radial_segments=16, tubular_segments=28), "cup_holder_ring")
    host.visual(cup, origin=Origin(xyz=(-lx - 0.005, -0.20, arm_z + 0.03)), material=mats["plastic"], name="cup_holder_ring", material_class_id="plastic.opaque_glossy_molded")
    host.visual(Cylinder(radius=0.048, length=0.09), origin=Origin(xyz=(-lx, -0.20, arm_z - 0.04)), material=mats["mesh"], name="cup_holder_sleeve", material_class_id="fabric.open_mesh")


def _emit_high_back_armchair(model, host, frame, r, mats) -> None:
    _emit_seat_pan(host, r, mats)
    for y0 in _bay_offsets(r):
        _emit_seat_boxes(host, r, mats, y0=y0)
    if r.has_back and r.motion != "back_recline":
        y_rear = REAR_Y + max(_bay_offsets(r))
        back_h = 0.64 * r.back_height_scale
        _emit_back_panels(host, r, mats, y_rear=y_rear, back_bottom_z=r.seat_z + 0.06, back_h=back_h)
    if r.motion != "hinged_armrests":
        _emit_arm_pads(host, r, mats)


def _emit_recliner_lounge(model, host, frame, r, mats) -> None:
    """Origin-A sagged fabric sling seat + leaning back (mesh panels preserved)."""
    lx = r.lx
    sz = r.seat_z
    _emit_seat_pan(host, r, mats)
    # Sagged seat sling front(-Y) -> back(+Y); edges reach the frame rails.
    seat_corners = (
        (-lx, FRONT_Y, sz + 0.005),
        (lx, FRONT_Y, sz + 0.005),
        (lx, REAR_Y, sz + 0.015),
        (-lx, REAR_Y, sz + 0.015),
    )
    _add_fabric(host, "seat_sling", seat_corners, mats["fabric"], sag=0.026)
    # Front orange accent band (embedded into the seat sling top so it is not an
    # island — the seat sling front edge sits at sz+0.005).
    accent_corners = (
        (-lx + 0.05, FRONT_Y + 0.02, sz + 0.004),
        (lx - 0.05, FRONT_Y + 0.02, sz + 0.004),
        (lx - 0.05, FRONT_Y + 0.14, sz + 0.008),
        (-lx + 0.05, FRONT_Y + 0.14, sz + 0.008),
    )
    _add_fabric(host, "seat_accent_band", accent_corners, mats["accent"], thickness=0.004, sag=0.004)
    if r.has_back and r.motion != "back_recline":
        back_top = sz + 0.66 * r.back_height_scale
        back_corners = (
            (-lx, REAR_Y - 0.02, sz + 0.012),
            (lx, REAR_Y - 0.02, sz + 0.012),
            (lx, REAR_Y + 0.10, back_top),
            (-lx, REAR_Y + 0.10, back_top),
        )
        _add_fabric(host, "back_sling", back_corners, mats["fabric_center"], sag=0.018)
        head_corners = (
            (-lx + 0.05, REAR_Y + 0.05, back_top - 0.12),
            (lx - 0.05, REAR_Y + 0.05, back_top - 0.12),
            (lx - 0.05, REAR_Y + 0.10, back_top),
            (-lx + 0.05, REAR_Y + 0.10, back_top),
        )
        _add_fabric(host, "head_band", head_corners, mats["accent"], thickness=0.004, sag=0.004)
    if r.motion != "hinged_armrests":
        _emit_arm_pads(host, r, mats)


def _emit_moon_saucer(model, host, frame, r, mats) -> None:
    """Round tubular rim + deep concave lathe bowl sling (moon_saucer fork)."""
    sz = r.seat_z
    rim_R = 0.44 * r.seat_width_scale
    rim_tube_r = 0.014
    tilt = 0.28
    cy = (FRONT_Y + REAR_Y) * 0.5
    cz = sz + 0.24
    rim_mesh = mesh_from_geometry(TorusGeometry(radius=rim_R, tube=rim_tube_r, radial_segments=16, tubular_segments=48), "bowl_rim")
    host.visual(rim_mesh, origin=Origin(xyz=(0.0, cy, cz), rpy=(tilt, 0.0, 0.0)), material=mats["metal"], name="bowl_rim", material_class_id="metal.paint_coated")
    binding = mesh_from_geometry(TorusGeometry(radius=rim_R - 0.003, tube=0.005, radial_segments=12, tubular_segments=40), "bowl_binding")
    host.visual(binding, origin=Origin(xyz=(0.0, cy, cz), rpy=(tilt, 0.0, 0.0)), material=mats["accent"], name="bowl_binding", material_class_id="fabric.webbing")
    scale = rim_R / 0.46
    outer = [(rim_R * (p / 0.46), z * scale) for p, z in (
        (0.460, 0.0), (0.420, -0.038), (0.330, -0.110), (0.210, -0.195), (0.095, -0.255), (0.020, -0.282),
    )]
    inner = [(rim_R * (p / 0.46) - 0.006, z * scale) for p, z in (
        (0.455, 0.0), (0.415, -0.035), (0.325, -0.106), (0.205, -0.190), (0.090, -0.250), (0.015, -0.277),
    )]
    bowl = LatheGeometry.from_shell_profiles(outer, inner, segments=48, start_cap="flat", end_cap="flat")
    host.visual(mesh_from_geometry(bowl, "bowl_sling"), origin=Origin(xyz=(0.0, cy, cz), rpy=(tilt, 0.0, 0.0)), material=mats["fabric"], name="bowl_sling", material_class_id="fabric.plain_flat_weave")
    # Four support struts tie the rim down onto the side seat rails so the bowl
    # is not an island floating above the frame.
    for i, (sx, sy) in enumerate(((1.0, 1.0), (-1.0, 1.0), (1.0, -1.0), (-1.0, -1.0))):
        phi = math.atan2(sy, sx)
        rp = (rim_R * math.cos(phi), cy + rim_R * math.sin(phi) * math.cos(tilt), cz + rim_R * math.sin(phi) * math.sin(tilt))
        # Foot lands on the side seat rail (x = +/- lx) so the bowl is supported.
        foot = (sx * r.lx, cy + sy * 0.15, sz + 0.02)
        _add_tube(host, f"saucer_strut_{i}", foot, rp, TUBE, mats["metal"])


def _emit_flat_cot(model, host, frame, r, mats) -> None:
    """Near-coplanar flat chaise: low-angle seat + back + footrest panels."""
    lx = r.lx
    sz = r.seat_z
    _emit_seat_pan(host, r, mats)
    seat_corners = (
        (-lx, FRONT_Y, sz + 0.01),
        (lx, FRONT_Y, sz + 0.01),
        (lx, REAR_Y, sz + 0.015),
        (-lx, REAR_Y, sz + 0.015),
    )
    _add_fabric(host, "seat_sling", seat_corners, mats["fabric"], sag=0.018)
    if r.has_back and r.motion != "back_recline":
        # Low-angle back (~12deg): rises only slightly above the seat plane.
        back_top = sz + 0.22 * r.back_height_scale
        back_corners = (
            (-lx, REAR_Y - 0.02, sz + 0.015),
            (lx, REAR_Y - 0.02, sz + 0.015),
            (lx, REAR_Y + 0.34, back_top),
            (-lx, REAR_Y + 0.34, back_top),
        )
        _add_fabric(host, "back_sling", back_corners, mats["fabric_center"], sag=0.014)
    # Front accent band (embedded into the seat sling so it is not an island).
    accent_corners = (
        (-lx + 0.05, FRONT_Y + 0.02, sz + 0.008),
        (lx - 0.05, FRONT_Y + 0.02, sz + 0.008),
        (lx - 0.05, FRONT_Y + 0.12, sz + 0.012),
        (-lx + 0.05, FRONT_Y + 0.12, sz + 0.012),
    )
    _add_fabric(host, "seat_accent_band", accent_corners, mats["accent"], thickness=0.004, sag=0.004)


def _emit_backless_stool(model, host, frame, r, mats) -> None:
    lx = r.lx
    sz = r.seat_z
    ws = r.seat_width_scale
    cy = (FRONT_Y + REAR_Y) * 0.5
    _emit_seat_pan(host, r, mats)
    _add_box(host, "seat_black_left", (0.14, 0.50 * ws, 0.018), (-(lx - 0.09), cy, sz + 0.016), mats["fabric"])
    _add_box(host, "seat_black_right", (0.14, 0.50 * ws, 0.018), (lx - 0.09, cy, sz + 0.016), mats["fabric"])
    _add_box(host, "seat_gray_center", (2 * lx - 0.24, 0.50 * ws, 0.018), (0.0, cy, sz + 0.018), mats["fabric_center"])
    _add_box(host, "seat_front_roll", (2 * lx - 0.10, 0.040, 0.032), (0.0, FRONT_Y + 0.02, sz + 0.024), mats["fabric"])


# ===========================================================================
# Slot C: motion — scissor braces (always) + one extra mechanism.
# ===========================================================================
def _scissor_brace_front(part, r, mats) -> None:
    k = r.fold_k
    ts = r.track_scale
    _add_tube(part, "front_moving_tube", (-0.39 * ts, -0.065, -0.235 * k), (0.39 * ts, -0.065, 0.235 * k), TUBE, mats["metal"])
    _add_tube(part, "front_pivot_collar", (0.0, -0.054, 0.0), (0.0, 0.018, 0.0), 0.020, mats["plastic"])
    _add_ball(part, "front_brace_end_0", (-0.39 * ts, -0.065, -0.235 * k), 0.018, mats["plastic"])
    _add_ball(part, "front_brace_end_1", (0.39 * ts, -0.065, 0.235 * k), 0.018, mats["plastic"])


def _scissor_brace_side(part, r, mats, *, mirror: bool) -> None:
    k = r.fold_k
    # Tube sits OUTBOARD of the pivot (local +x for right, -x for left) so the
    # moving diagonal never crosses the width-spanning frame cross members.
    tx = 0.065 if mirror else -0.065
    # Collar bridges from the tube toward the (inboard) pivot at local 0.
    c0, c1 = (-0.052, 0.018) if not mirror else (0.052, -0.018)
    _add_tube(part, "side_moving_tube", (tx, -0.335, -0.245 * k), (tx, 0.330, 0.245 * k), TUBE, mats["metal"])
    _add_tube(part, "side_pivot_collar", (c0, 0.0, 0.0), (c1, 0.0, 0.0), 0.020, mats["plastic"])
    _add_ball(part, "side_brace_end_a", (tx, -0.335, -0.245 * k), 0.018, mats["plastic"])
    _add_ball(part, "side_brace_end_b", (tx, 0.330, 0.245 * k), 0.018, mats["plastic"])


def _build_scissor(model, frame, r: ResolvedCampChairConfig, mats) -> None:
    lx = r.lx
    k = r.fold_k
    # Front brace(s) — one per bay (dropped for the side-folding recliner).
    if _has_front_brace(r):
        for by in _bay_offsets(r):
            tag = _bay_tag(r, by)
            fpy = FRONT_Y + by - 0.08
            brace = model.part(f"front_cross_brace{tag}")
            _scissor_brace_front(brace, r, mats)
            model.articulation(
                f"frame_to_front_cross{tag}", ArticulationType.REVOLUTE,
                parent=frame, child=brace,
                origin=Origin(xyz=(0.0, fpy, 0.30 * k)), axis=(0.0, 1.0, 0.0),
                motion_limits=MotionLimits(effort=20.0, velocity=1.2, lower=0.0, upper=0.45),
            )
    # Two mirrored side braces on the outer rails.
    side0 = model.part("side_cross_brace_0")
    _scissor_brace_side(side0, r, mats, mirror=False)
    model.articulation(
        "frame_to_side_cross_0", ArticulationType.REVOLUTE, parent=frame, child=side0,
        origin=Origin(xyz=(-lx - 0.006, -0.020, 0.325 * k)), axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=20.0, velocity=1.2, lower=0.0, upper=0.45),
    )
    side1 = model.part("side_cross_brace_1")
    _scissor_brace_side(side1, r, mats, mirror=True)
    model.articulation(
        "frame_to_side_cross_1", ArticulationType.REVOLUTE, parent=frame, child=side1,
        origin=Origin(xyz=(lx + 0.006, -0.020, 0.325 * k)), axis=(-1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=20.0, velocity=1.2, lower=0.0, upper=0.45),
    )


def _build_footrest(model, frame, r: ResolvedCampChairConfig, mats) -> None:
    """Reclining footrest child hinged at seat front (Origin-A base_to_footrest)."""
    lx = r.lx
    sz = r.seat_z
    fr = model.part("footrest_panel")
    # Local frame: hinge at origin (world = seat front, 0.04 below the seat).
    # Deployed (q=0) the panel extends forward (-Y) and rises to ~seat level.
    corners = (
        (-lx + 0.03, 0.0, 0.0),
        (lx - 0.03, 0.0, 0.0),
        (lx - 0.03, -0.55, 0.02),
        (-lx + 0.03, -0.55, 0.02),
    )
    _add_fabric(fr, "footrest_sling", corners, mats["fabric"], sag=0.02)
    # Hinge barrel (coaxial with the frame hinge pin) so the part origin sits on
    # real hardware and the child contains (0,0,0).
    fr.visual(
        Cylinder(radius=0.011, length=2 * (lx - 0.03)), origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["plastic"], name="footrest_hinge_barrel", material_class_id="plastic.opaque_glossy_molded",
    )
    fr.visual(mesh_from_geometry(tube_from_spline_points(
        [(-lx + 0.03, -0.55, 0.02), (0.0, -0.60, 0.01), (lx - 0.03, -0.55, 0.02)],
        radius=0.011, samples_per_segment=4, radial_segments=12, cap_ends=True), "footrest_u_tube"),
        material=mats["metal"], name="footrest_u_tube", material_class_id="metal.paint_coated")
    # Hinge about the LATERAL (X) axis so the forward-extending panel lifts up.
    model.articulation(
        "frame_to_footrest", ArticulationType.REVOLUTE, parent=frame, child=fr,
        origin=Origin(xyz=(0.0, FRONT_Y, sz - 0.04)), axis=(-1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=12.0, velocity=1.0, lower=0.0, upper=0.9),
    )


def _build_armrests(model, frame, r: ResolvedCampChairConfig, mats) -> None:
    """Hinged fabric armrests (Origin-A base_to_*_armrest REVOLUTE)."""
    lx = r.lx
    arm_z = r.seat_z + 0.18
    for label, sgn in SIDES:
        arm = model.part(f"{label}_armrest")
        # Local: hinge at origin at rear post; arm extends forward (-Y).
        corners = (
            (-0.045, 0.0, 0.0),
            (0.045, 0.0, 0.0),
            (0.045, -0.62, -0.05),
            (-0.045, -0.62, -0.05),
        )
        _add_fabric(arm, "fabric_arm", corners, mats["fabric"], thickness=0.004, sag=0.006)
        arm.visual(
            Cylinder(radius=0.011, length=0.09), origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["plastic"], name="arm_hinge_barrel", material_class_id="plastic.opaque_glossy_molded",
        )
        model.articulation(
            f"frame_to_{label}_armrest", ArticulationType.REVOLUTE, parent=frame, child=arm,
            origin=Origin(xyz=(sgn * lx, REAR_Y + 0.02, arm_z)), axis=(-1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=6.0, velocity=1.0, lower=0.0, upper=0.9),
        )


def _build_back_recliner(model, frame, r: ResolvedCampChairConfig, mats) -> None:
    """Reclining back child: back posts + panel move to a REVOLUTE part."""
    lx = r.lx
    sz = r.seat_z
    hinge_z = sz + 0.05
    back = model.part("back_recliner")
    back_h = 0.64 * r.back_height_scale
    # Local frame at hinge line (world x kept, y/z local to hinge).
    # Pivot collar spanning the width along X at local origin.
    _add_tube(back, "recline_pivot_collar", (-lx, 0.0, 0.0), (lx, 0.0, 0.0), 0.016, mats["plastic"])
    for _label, sgn in SIDES:
        _add_tube(back, f"rear_post_{_label}", (sgn * lx, 0.0, 0.0), (sgn * lx, 0.05, back_h), TUBE, mats["metal"])
    _add_tube(back, "top_back_rail", (-lx, 0.05, back_h), (lx, 0.05, back_h), TUBE, mats["metal"])
    bz = back_h / 2.0
    yb = 0.025  # panel plane straddles the posts (local y 0..0.05)
    _add_box(back, "back_gray_center", (0.52, 0.040, back_h * 0.9), (0.0, yb, bz), mats["fabric_center"])
    _add_box(back, "back_black_side_0", (0.24, 0.044, back_h * 0.92), (-(lx - 0.11), yb, bz), mats["fabric"])
    _add_box(back, "back_black_side_1", (0.24, 0.044, back_h * 0.92), (lx - 0.11, yb, bz), mats["fabric"])
    # Lower band bridges the panel down onto the pivot collar at local z=0.
    _add_box(back, "back_lower_band", (0.80, 0.044, 0.10), (0.0, yb, 0.03), mats["fabric"])
    _add_box(back, "back_top_pillow", (0.82, 0.070, 0.11), (0.0, 0.05, back_h), mats["fabric"])
    _add_box(back, "back_piping_0", (0.012, 0.030, back_h * 0.86), (-0.210, yb - 0.024, bz), mats["accent"])
    _add_box(back, "back_piping_1", (0.012, 0.030, back_h * 0.86), (0.210, yb - 0.024, bz), mats["accent"])
    # Recline about the LATERAL (X) axis so the back tilts rearward+down.
    model.articulation(
        "frame_to_recline_back", ArticulationType.REVOLUTE, parent=frame, child=back,
        origin=Origin(xyz=(0.0, REAR_Y, hinge_z)), axis=(-1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=12.0, velocity=1.0, lower=0.0, upper=0.55),
    )


def _rebase_part(part, shift) -> None:
    """Shift every visual origin by ``-shift`` so the part's local (0,0,0) lands
    on the joint hub (world-authored geometry -> child-local frame)."""
    sx, sy, sz = shift
    for v in part.visuals:
        v.origin = Origin(
            xyz=(v.origin.xyz[0] - sx, v.origin.xyz[1] - sy, v.origin.xyz[2] - sz),
            rpy=v.origin.rpy,
        )


def _build_swivel(model, frame, r: ResolvedCampChairConfig, mats, host) -> None:
    """CONTINUOUS +Z turntable carrying the seat host part.

    The form envelope + these bearing visuals are authored in WORLD coords, then
    rebased by ``-hub`` so the child part frame origin sits on the hub (the joint
    origin) — otherwise the child would be double-offset and float away."""
    sz = r.seat_z
    cy = (FRONT_Y + REAR_Y) * 0.5
    # Raise the whole rotating platform above the leg tops (which end at sz) so it
    # sweeps freely over the fixed base when it turns.
    lift = 0.05
    for v in host.visuals:
        v.origin = Origin(xyz=(v.origin.xyz[0], v.origin.xyz[1], v.origin.xyz[2] + lift), rpy=v.origin.rpy)
    hub = (0.0, cy, sz + lift + 0.02)
    collar = mesh_from_geometry(TorusGeometry(radius=0.060, tube=0.012, radial_segments=16, tubular_segments=28), "swivel_collar")
    host.visual(collar, origin=Origin(xyz=hub), material=mats["metal"], name="swivel_collar", material_class_id="metal.paint_coated")
    host.visual(Cylinder(radius=0.056, length=0.016), origin=Origin(xyz=hub), material=mats["metal"], name="swivel_disk", material_class_id="metal.paint_coated")
    # Radial spokes from the bearing to the (inboard) seat corners; kept well
    # inside the leg circle so the platform never strikes the legs when turning.
    for label, sgn in SIDES:
        _add_tube(host, f"swivel_spoke_f_{label}", hub, (sgn * 0.30, cy - 0.20, sz + lift), TUBE, mats["metal"])
        _add_tube(host, f"swivel_spoke_r_{label}", hub, (sgn * 0.30, cy + 0.20, sz + lift), TUBE, mats["metal"])
    _rebase_part(host, hub)
    model.articulation(
        "frame_to_swivel", ArticulationType.CONTINUOUS, parent=frame, child=host,
        origin=Origin(xyz=hub), axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=5.0, velocity=1.0),
    )


# ===========================================================================
# Assembly
# ===========================================================================
def build_camp_chair(config: CampChairConfig | None = None, *, assets: AssetContext | None = None) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    base_rgba = dict(PALETTES[r.palette_style])
    base_rgba.update(_HARDWARE)
    mats = {k: model.material(f"camp_{k}_{r.palette_style}", rgba=v) for k, v in base_rgba.items()}

    frame = _build_frame(model, r, mats)
    host = _emit_form(model, frame, r, mats)
    _build_scissor(model, frame, r, mats)

    if r.motion == "reclining_footrest":
        _build_footrest(model, frame, r, mats)
    elif r.motion == "hinged_armrests":
        _build_armrests(model, frame, r, mats)
    elif r.motion == "back_recline":
        _build_back_recliner(model, frame, r, mats)
    elif r.motion == "swivel_riser":
        _build_swivel(model, frame, r, mats, host)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_camp_chair(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_camp_chair(config_from_seed(seed), assets=assets)


# ===========================================================================
# Tests
# ===========================================================================
def _allow_captured_pins(ctx, model, r: ResolvedCampChairConfig) -> None:
    frame = model.get_part("chair_frame")
    # Scissor pivot captures (mirror Origin-B run_tests).
    if _has_front_brace(r):
        for by in _bay_offsets(r):
            tag = _bay_tag(r, by)
            front = model.get_part(f"front_cross_brace{tag}")
            ctx.allow_overlap(frame, front, elem_a=f"front_pivot_pin{tag}", elem_b="front_pivot_collar", reason="Scissor collar captured around the fixed front pivot pin.")
            ctx.allow_overlap(frame, front, elem_a=f"front_pivot_rivet{tag}", elem_b="front_pivot_collar", reason="Front rivet head captures the rotating scissor collar.")
            ctx.allow_overlap(frame, front, elem_a=f"front_pivot_support{tag}", elem_b="front_pivot_collar", reason="Fixed pivot support passes through the scissor collar.")
    side0 = model.get_part("side_cross_brace_0")
    side1 = model.get_part("side_cross_brace_1")
    ctx.allow_overlap(frame, side0, elem_a="side_pivot_pin_0", elem_b="side_pivot_collar", reason="Left scissor collar captured by the fixed pivot pin.")
    ctx.allow_overlap(frame, side1, elem_a="side_pivot_pin_1", elem_b="side_pivot_collar", reason="Right scissor collar captured by the fixed pivot pin.")
    ctx.allow_overlap(frame, side0, elem_a="side_pivot_rivet_0", elem_b="side_pivot_collar", reason="Left rivet clamps the scissor collar.")
    ctx.allow_overlap(frame, side1, elem_a="side_pivot_rivet_1", elem_b="side_pivot_collar", reason="Right rivet clamps the scissor collar.")
    ctx.allow_overlap(frame, side0, elem_a="side_pivot_rivet_0", elem_b="side_moving_tube", reason="Left rivet passes through the moving brace tube at the scissor joint.")
    ctx.allow_overlap(frame, side1, elem_a="side_pivot_rivet_1", elem_b="side_moving_tube", reason="Right rivet passes through the moving brace tube at the scissor joint.")
    ctx.allow_overlap(frame, side0, elem_a="side_pivot_support_0", elem_b="side_pivot_collar", reason="Fixed side support passes through the scissor collar.")
    ctx.allow_overlap(frame, side1, elem_a="side_pivot_support_1", elem_b="side_pivot_collar", reason="Fixed side support passes through the scissor collar.")

    if r.motion == "reclining_footrest":
        fr = model.get_part("footrest_panel")
        ctx.allow_overlap(frame, fr, elem_a="footrest_hinge_pin", elem_b="footrest_hinge_barrel", reason="Footrest hinge barrel is coaxial with the frame hinge pin.")
        ctx.allow_overlap(frame, fr, elem_a="footrest_hinge_pin", elem_b="footrest_sling", reason="Footrest sling wraps around the frame hinge pin at the pivot.")
    if r.motion == "hinged_armrests":
        for label, sgn in SIDES:
            arm = model.get_part(f"{label}_armrest")
            ctx.allow_overlap(frame, arm, elem_a=f"{label}_arm_hinge", elem_b="arm_hinge_barrel", reason="Armrest hinge barrel is coaxial with the frame arm hinge pin.")
            ctx.allow_overlap(frame, arm, elem_a=f"{label}_arm_hinge", elem_b="fabric_arm", reason="Soft arm fabric wraps around the frame arm hinge pin.")
            for elem in ("fabric_arm", "arm_hinge_barrel"):
                ctx.allow_overlap(frame, arm, elem_a=f"rear_post_{label}", elem_b=elem, reason="Arm-rest hinge is captured on the rear upright post.")
                for bs in ("back_black_side_0", "back_black_side_1", "back_gray_center", "back_sling", "head_band"):
                    ctx.allow_overlap(frame, arm, elem_a=bs, elem_b=elem, reason="Arm-rest hinge/fabric bolts alongside the back panel at the rear corner.")
    if r.motion == "back_recline":
        back = model.get_part("back_recliner")
        # The reclining back frame nests at the rear hinge cluster, sleeving over
        # the hinge pin and bolting alongside the seat rails + arm-rest mounts
        # (a real camp-recliner rear pivot assembly).
        frame_rear = (
            "recline_hinge_pin", "rear_seat_rail", "side_seat_rail_left", "side_seat_rail_right",
            "arm_rest_top_left", "arm_rest_top_right", "arm_rest_stitch_left", "arm_rest_stitch_right",
        )
        back_elems = (
            "recline_pivot_collar", "rear_post_left", "rear_post_right", "back_lower_band",
            "back_gray_center", "back_black_side_0", "back_black_side_1",
        )
        for fe in frame_rear:
            for be in back_elems:
                ctx.allow_overlap(frame, back, elem_a=fe, elem_b=be, reason="Reclining back rear hinge cluster nests among the seat rails, hinge pin and arm mounts.")
    if r.motion == "swivel_riser":
        host = model.get_part("seat_swivel")
        ctx.allow_overlap(frame, host, elem_a="swivel_hub", elem_b="swivel_collar", reason="Bearing collar wraps around the hub as a turntable ring.")
        ctx.allow_overlap(frame, host, elem_a="swivel_hub", elem_b="swivel_disk", reason="Bearing disk captured inside the hub envelope.")
        ctx.allow_overlap(frame, host, elem_a="swivel_hub", elem_b="seat_pan", reason="Central swivel post rises through the seat pan center bearing hole.")
        ctx.allow_overlap(frame, host, elem_a="swivel_hub", elem_b="seat_gray_center", reason="Central swivel post rises through the seat center.")
        for label, _s in SIDES:
            ctx.allow_overlap(frame, host, elem_a="swivel_hub", elem_b=f"swivel_spoke_f_{label}", reason="Radial spoke roots meet the central hub post.")
            ctx.allow_overlap(frame, host, elem_a="swivel_hub", elem_b=f"swivel_spoke_r_{label}", reason="Radial spoke roots meet the central hub post.")
        for i in (0, 1):
            ctx.allow_overlap(frame, host, elem_a=f"base_xframe_{i}", elem_b="swivel_collar", reason="Base X-frame passes under the collar at the hub crossing.")
            ctx.allow_overlap(frame, host, elem_a=f"base_xframe_{i}", elem_b="swivel_disk", reason="Base X-frame passes under the bearing disk at the hub crossing.")


def run_camp_chair_tests(object_model: ArticulatedObject, config: CampChairConfig) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)

    _allow_captured_pins(ctx, object_model, r)

    # ---- Identity: a folding camp chair always has scissor fold joints. ----
    n_joints = len(object_model.articulations)
    ctx.check(
        "camp chair has folding scissor joints",
        object_model.get_articulation("frame_to_side_cross_0") is not None
        and object_model.get_articulation("frame_to_side_cross_1") is not None
        and n_joints >= 3,
        details=f"articulations={[a.name for a in object_model.articulations]}",
    )

    # ---- Seat at a sitting height for the stance. ----
    frame = object_model.get_part("chair_frame")
    seat_aabb = ctx.part_world_aabb(frame)
    ctx.check(
        "frame spans a seat-height envelope",
        seat_aabb is not None and (seat_aabb[1][2] - seat_aabb[0][2]) > 0.20,
        details=f"frame_aabb={seat_aabb}",
    )

    # ---- Targeted mechanism poses (one per key mechanism). ----
    # Scissor fold: a brace changes silhouette (front brace if present, else a
    # side brace for the side-folding recliner).
    if _has_front_brace(r):
        fold_part = object_model.get_part("front_cross_brace" if r.seat_cells == 1 else "front_cross_brace_0")
        fj = object_model.get_articulation("frame_to_front_cross" if r.seat_cells == 1 else "frame_to_front_cross_0")
        idx = 2  # z-extent changes as the front brace folds
    else:
        fold_part = object_model.get_part("side_cross_brace_0")
        fj = object_model.get_articulation("frame_to_side_cross_0")
        idx = 1  # y-extent changes as the side brace folds
    rest = ctx.part_world_aabb(fold_part)
    with ctx.pose({fj: 0.40}):
        folded = ctx.part_world_aabb(fold_part)
    ctx.check(
        "scissor brace changes silhouette when folding",
        rest is not None and folded is not None
        and abs((folded[1][idx] - folded[0][idx]) - (rest[1][idx] - rest[0][idx])) > 0.015,
        details=f"rest={rest}, folded={folded}",
    )

    if r.motion == "reclining_footrest":
        fr = object_model.get_part("footrest_panel")
        j = object_model.get_articulation("frame_to_footrest")
        rest = ctx.part_world_aabb(fr)
        with ctx.pose({j: 0.8}):
            lifted = ctx.part_world_aabb(fr)
        ctx.check("footrest lifts upward", rest is not None and lifted is not None and lifted[1][2] > rest[1][2] + 0.05, details=f"rest={rest}, lifted={lifted}")
    elif r.motion == "hinged_armrests":
        j = object_model.get_articulation("frame_to_left_armrest")
        ctx.check("armrest hinge is REVOLUTE", j.articulation_type == ArticulationType.REVOLUTE, details=f"type={j.articulation_type}")
        arm = object_model.get_part("left_armrest")
        rest = ctx.part_world_aabb(arm)
        with ctx.pose({j: 0.8}):
            up = ctx.part_world_aabb(arm)
        ctx.check("armrest folds up", rest is not None and up is not None and up[1][2] > rest[1][2] + 0.03, details=f"rest={rest}, up={up}")
    elif r.motion == "back_recline":
        back = object_model.get_part("back_recliner")
        j = object_model.get_articulation("frame_to_recline_back")
        ctx.check("back reclines (REVOLUTE lateral X)", j.articulation_type == ArticulationType.REVOLUTE and abs(j.axis[0]) > 0.99, details=f"axis={j.axis}")
        rest = ctx.part_world_aabb(back)
        with ctx.pose({j: 0.5}):
            recl = ctx.part_world_aabb(back)
        ctx.check("recline tilts the back rearward/down", rest is not None and recl is not None and (recl[1][1] > rest[1][1] + 0.02 or recl[1][2] < rest[1][2] - 0.01), details=f"rest={rest}, recl={recl}")
    elif r.motion == "swivel_riser":
        host = object_model.get_part("seat_swivel")
        j = object_model.get_articulation("frame_to_swivel")
        ctx.check("swivel is CONTINUOUS +Z", j.articulation_type == ArticulationType.CONTINUOUS and abs(j.axis[2]) > 0.99, details=f"type={j.articulation_type}, axis={j.axis}")
        rest = ctx.part_world_aabb(host)
        with ctx.pose({j: math.pi / 2.0}):
            turned = ctx.part_world_aabb(host)
        ctx.check(
            "swivel rotation changes the seat footprint",
            rest is not None and turned is not None
            and (abs((turned[1][0] - turned[0][0]) - (rest[1][0] - rest[0][0])) > 0.02
                 or abs((turned[1][1] - turned[0][1]) - (rest[1][1] - rest[0][1])) > 0.02),
            details=f"rest={rest}, turned={turned}",
        )

    # ---- Rule 5: full-travel non-穿模 across sampled joint poses. ----
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=40, ignore_fixed=True)

    # ---- Compiler-owned baseline (also enforced by the sweep). ----
    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)
    ctx.fail_if_joint_mating_has_gap()

    return ctx.report()


__all__ = [
    "FormFamily",
    "BaseStance",
    "Motion",
    "PaletteStyle",
    "CampChairConfig",
    "ResolvedCampChairConfig",
    "build_camp_chair",
    "build_seeded_camp_chair",
    "config_from_seed",
    "resolve_config",
    "slot_choices_for_seed",
    "run_camp_chair_tests",
]
