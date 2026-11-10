# SPDX-License-Identifier: Apache-2.0

"""Folding chair — modular procedural template (scissor-fold sit-on chair).

Category identity: a sit-on chair that collapses flat about a single side
crossing pivot. The fixed spine is a TRUE single-DOF scissor fold:

  * ``rear_leg_frame`` (ROOT): rear legs rise forward from the back feet,
    pass through the side crossing pivot, and continue up to become the
    backrest uprights. It carries the stationary rear seat-hinge bar.
  * ``front_leg_frame`` (child of rear, REVOLUTE ``fold_pivot`` about +Y):
    front legs rise back from the front feet, cross at the same pivot, and
    top out at the seat-front rail. Positive q folds the chair flat.
  * ``seat_pan`` (child of rear, REVOLUTE ``seat_hinge`` about +Y, MIMIC of
    ``fold_pivot``): rear edge hinged on the rear bar, front edge riding the
    moving front rail; the mimic keeps the front edge on the rail through
    the whole fold.

Four parallel slots hang on that common skeleton (no multiplicity axis):

  * ``fold_mechanism`` (5) — the skeleton itself; some candidates add a
    second folding child (rear under-frame / collapsing side links).
  * ``seat_back_panel`` (9) — pure visual: swaps the ``seat_pan`` seat
    surface and the backrest panel helper. No new parts/joints (wood_slat is
    part-local slat copies; fabric_bucket uses MeshGeometry).
  * ``frame_style`` (4 -> 2 topology families: tube vs flat_bar) — swaps the
    leg/brace primitive (round tube ↔ flat Box bar) + materials.
  * ``accessory`` (5, incl. ``plain``) — optionally adds one independent
    moving child (tablet arm / reclining backrest / flip-down footrest) or a
    carry-handle bezel cut in the backrest (no new joint).

Continuous size/proportion variation (stool / child / heavy-duty / beach /
tall / narrow) lives in ``resolve_config`` as clamped scale params, never as
slot candidates.

Sources (articraft_data ``picture/Chair/Folding chair`` 5-star pool):
parent ``cc9b62cf`` (scissor + padded + tube + plain), ``fcc91b91`` (v02
rear_legs_fold_under + molded), ``dad421cd`` (v20 collapsing_side +
fabric_bucket), ``93e9880f`` (v18 flat_bar), ``659ae563`` (v08 tablet),
``929d0eb3`` (v13 recline), ``150f16e4`` (v19 footrest), plus the seat-panel
helpers (``5571b31a`` sling, ``8c1cac12`` slat, ``74b2022d`` perforated,
``364067f0`` polycarbonate, ``17cd26af`` canvas, ``0b7e3fd9`` cane,
``1d9acfc6`` handle bezel).

Canonical spec: ``articraft_template_authoring/specs_modular_v1/Chair_Folding_Chair_Chair.md``
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, replace
from typing import Literal

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    BezelGeometry,
    Box,
    Cylinder,
    ExtrudeGeometry,
    Inertial,
    MeshGeometry,
    Mimic,
    MotionLimits,
    Origin,
    PerforatedPanelGeometry,
    TestContext,
    TestReport,
    mesh_from_geometry,
    rounded_rect_profile,
    tube_from_spline_points,
)

__modular__ = True

# ---------------------------------------------------------------------------
# Slot domains
# ---------------------------------------------------------------------------
FoldMechanism = Literal[
    "scissor_cross_brace",
    "reinforced_double_cross_brace",
    "triangular_folding_frame",
    "rear_legs_fold_under",
    "collapsing_side_hinge_links",
]
SeatBackPanel = Literal[
    "padded_pad",
    "molded_plastic",
    "fabric_sling",
    "canvas",
    "perforated_plastic",
    "wood_slat",
    "polycarbonate_translucent",
    "woven_cane",
    "fabric_bucket",
]
FrameStyle = Literal[
    "tubular_steel",
    "aluminum_tube",
    "wood_side_frame",
    "flat_bar_angular",
]
Accessory = Literal[
    "plain",
    "pivoting_tablet_arm",
    "reclining_backrest_2nd_hinge",
    "carry_handle_cutout",
    "flip_down_footrest",
]
MaterialStyle = Literal[
    "steel_gray",
    "black_powder",
    "aluminum",
    "wood",
    "matte_red",
    "green",
    "ripstop_blue",
]

FOLD_MECHANISMS: tuple[FoldMechanism, ...] = (
    "scissor_cross_brace",
    "reinforced_double_cross_brace",
    "triangular_folding_frame",
    "rear_legs_fold_under",
    "collapsing_side_hinge_links",
)
SEAT_BACK_PANELS: tuple[SeatBackPanel, ...] = (
    "padded_pad",
    "molded_plastic",
    "fabric_sling",
    "canvas",
    "perforated_plastic",
    "wood_slat",
    "polycarbonate_translucent",
    "woven_cane",
    "fabric_bucket",
)
FRAME_STYLES: tuple[FrameStyle, ...] = (
    "tubular_steel",
    "aluminum_tube",
    "wood_side_frame",
    "flat_bar_angular",
)
ACCESSORIES: tuple[Accessory, ...] = (
    "plain",
    "pivoting_tablet_arm",
    "reclining_backrest_2nd_hinge",
    "carry_handle_cutout",
    "flip_down_footrest",
)
MATERIAL_STYLES: tuple[MaterialStyle, ...] = (
    "steel_gray",
    "black_powder",
    "aluminum",
    "wood",
    "matte_red",
    "green",
    "ripstop_blue",
)

# Frame primitive families for topology dedup (spec §9): tube vs flat_bar.
_FRAME_PRIMITIVE: dict[FrameStyle, str] = {
    "tubular_steel": "tube",
    "aluminum_tube": "tube",
    "wood_side_frame": "tube",
    "flat_bar_angular": "flat_bar",
}

# ---------------------------------------------------------------------------
# Material palettes. Each palette maps semantic roles -> rgba. ``frame`` is
# the leg/brace metal/wood, ``accent`` the seat-hinge/cross hardware,
# ``seat``/``back`` the panel surfaces, ``rubber`` the feet.
# ---------------------------------------------------------------------------
PALETTES: dict[MaterialStyle, dict[str, tuple[float, float, float, float]]] = {
    "steel_gray": {
        "frame": (0.62, 0.63, 0.65, 1.0),
        "accent": (0.45, 0.46, 0.48, 1.0),
        "seat": (0.74, 0.75, 0.76, 1.0),
        "back": (0.74, 0.75, 0.76, 1.0),
        "rubber": (0.10, 0.10, 0.11, 1.0),
    },
    "black_powder": {
        "frame": (0.09, 0.095, 0.10, 1.0),
        "accent": (0.18, 0.18, 0.19, 1.0),
        "seat": (0.05, 0.055, 0.06, 1.0),
        "back": (0.05, 0.055, 0.06, 1.0),
        "rubber": (0.10, 0.10, 0.11, 1.0),
    },
    "aluminum": {
        "frame": (0.58, 0.60, 0.62, 1.0),
        "accent": (0.40, 0.42, 0.44, 1.0),
        "seat": (0.70, 0.72, 0.74, 1.0),
        "back": (0.70, 0.72, 0.74, 1.0),
        "rubber": (0.10, 0.10, 0.11, 1.0),
    },
    "wood": {
        "frame": (0.52, 0.36, 0.20, 1.0),
        "accent": (0.30, 0.20, 0.11, 1.0),
        "seat": (0.66, 0.48, 0.28, 1.0),
        "back": (0.66, 0.48, 0.28, 1.0),
        "rubber": (0.10, 0.10, 0.11, 1.0),
    },
    "matte_red": {
        "frame": (0.78, 0.06, 0.04, 1.0),
        "accent": (0.16, 0.16, 0.17, 1.0),
        "seat": (0.08, 0.085, 0.09, 1.0),
        "back": (0.08, 0.085, 0.09, 1.0),
        "rubber": (0.10, 0.10, 0.11, 1.0),
    },
    "green": {
        "frame": (0.20, 0.45, 0.24, 1.0),
        "accent": (0.12, 0.28, 0.15, 1.0),
        "seat": (0.24, 0.52, 0.28, 1.0),
        "back": (0.24, 0.52, 0.28, 1.0),
        "rubber": (0.10, 0.10, 0.11, 1.0),
    },
    "ripstop_blue": {
        "frame": (0.58, 0.60, 0.62, 1.0),
        "accent": (0.05, 0.055, 0.06, 1.0),
        "seat": (0.05, 0.16, 0.34, 1.0),
        "back": (0.05, 0.16, 0.34, 1.0),
        "rubber": (0.10, 0.10, 0.11, 1.0),
    },
}

# ---------------------------------------------------------------------------
# Base geometry (parent cc9b62cf, meters). Scaled per-build by the resolved
# config; the named SCALE params only stretch safe proportions, never the
# fold/seat interface semantics.
# ---------------------------------------------------------------------------
_TUBE_R = 0.013
_HALF_W = 0.205  # half frame width -> side rails at y = +/- HALF_W
# Side-view (x, z) key points in the OPEN (usable) pose. +X = front of chair.
_PIVOT = (0.0, 0.255)  # side crossing / scissor pivot in (x, z)
_REAR_FOOT = (-0.18, 0.0)
_BACK_TOP = (-0.05, 0.86)
_SEAT_HINGE = (-0.165, 0.455)  # stationary rear seat-pan hinge
_FRONT_FOOT = (0.20, 0.0)
_SEAT_FRONT = (0.16, 0.45)  # top of front frame; carries the seat front
_SEAT_W = 0.36
_SEAT_DEPTH = 0.42
_SEAT_THICK = 0.045
_BACK_W = 0.42
_BACK_H = 0.24
_BACK_THICK = 0.040
_FOLD_UPPER = 1.28
# Seat-tilt vs fold-angle (seat_hinge mimics fold_pivot by this factor). The
# seat folds DOWN-and-forward, tracking the dropping front rail. Its magnitude
# is bounded by the crossing swept envelope: at full fold the seat rotates
# _SEAT_FOLD_MULT * _FOLD_UPPER rad about the rear hinge, and its underside must
# clear the fixed full-width scissor bolt at the central crossing by >=8mm.
# Solving that clearance (bolt sits ~0.20*seat_height below and 0.165 ahead of
# the hinge; the seat underside strip crossing the bolt's x reaches its lowest z
# there) gives a safe seat angle of ~0.47 rad, well short of the ~0.58 rad where
# the underside first touches the bolt. 0.365 * 1.28 = 0.47 rad keeps that
# margin while still tilting the seat far past the "folds up" QC threshold. The
# ratio is height-scale invariant (bolt and hinge scale together in z about the
# floor), so the margin holds across the whole seat_height_scale range.
_SEAT_FOLD_MULT = 0.365
# flat-bar frame (v18) primitive sizes.
_BAR_THICK_Y = 0.012
_BAR_WIDTH = 0.030
# reclining backrest (v13).
_RECLINE_UPPER = 0.30
# Synchronized full-fold angle of the fold-under legs (mimic of fold_pivot). As
# the legs swing forward they pass THROUGH the collapsing front cross brace's
# folded position at a config-dependent mid angle (~-0.2..-0.35): folding well
# past it (default) clears it on the far side. The exception is the flip-down
# footrest, which drops its loop into that same far-side bundle -- there the
# legs must instead stay rear-tucked, short of the front-brace band. Both stay
# inside the pivot-sleeve swept limit applied at build.
_REAR_UNDER_FOLD_FULL = -0.55
_REAR_UNDER_FOLD_FULL_FOOTREST = -0.18
# Flip-down footrest deploy vs fold-angle (mimic of fold_pivot). A large factor
# over-swings the loop past the folded front legs and back into the rear uprights
# at full fold; kept modest so the loop stows alongside the folding front legs.
_FOOTREST_FOLD_MULT = 0.75
# Collapsing side-link swing vs fold-angle (mimic of fold_pivot). Kept small so
# the U-links stay low as the chair closes; a larger swing raises the link arms
# and front crossbar up into the down-folding seat pan.
_SIDE_LINK_FOLD_MULT = 0.15
# carry-handle slot (v16).
_HANDLE_H = 0.060
_HANDLE_W = 0.150


@dataclass(frozen=True)
class FoldingChairConfig:
    fold_mechanism: FoldMechanism = "scissor_cross_brace"
    seat_back_panel: SeatBackPanel = "padded_pad"
    frame_style: FrameStyle = "tubular_steel"
    accessory: Accessory = "plain"
    material_style: MaterialStyle = "steel_gray"
    seat_height_scale: float = 1.0
    seat_width_scale: float = 1.0
    back_height_scale: float = 1.0
    back_recline_angle: float = 0.0
    name: str = "folding_chair"


@dataclass(frozen=True)
class ResolvedFoldingChairConfig:
    fold_mechanism: FoldMechanism
    seat_back_panel: SeatBackPanel
    frame_style: FrameStyle
    accessory: Accessory
    material_style: MaterialStyle
    seat_height_scale: float
    seat_width_scale: float
    back_height_scale: float
    # Scaled side-view key points (x, z).
    tube_r: float
    half_w: float
    pivot: tuple[float, float]
    rear_foot: tuple[float, float]
    back_top: tuple[float, float]
    seat_hinge: tuple[float, float]
    front_foot: tuple[float, float]
    seat_front: tuple[float, float]
    seat_w: float
    seat_depth: float
    seat_thick: float
    back_w: float
    back_h: float
    back_thick: float
    back_mid_z: float
    fold_upper: float
    seat_fold_mult: float
    back_recline_angle: float
    name: str


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


# ---------------------------------------------------------------------------
# Seed / resolve
# ---------------------------------------------------------------------------
def config_from_seed(seed: int) -> FoldingChairConfig:
    """Deterministic procedural sampling (seed 0 is not special, Contract 4)."""
    rng = random.Random(seed)
    accessory = rng.choice(ACCESSORIES)
    return FoldingChairConfig(
        fold_mechanism=rng.choice(FOLD_MECHANISMS),
        seat_back_panel=rng.choice(SEAT_BACK_PANELS),
        frame_style=rng.choice(FRAME_STYLES),
        accessory=accessory,
        material_style=rng.choice(MATERIAL_STYLES),
        seat_height_scale=round(rng.uniform(0.70, 1.05), 4),
        seat_width_scale=round(rng.uniform(0.80, 1.25), 4),
        back_height_scale=round(rng.uniform(0.55, 1.15), 4),
        # Conditional: only meaningful when accessory=reclining (resolve clamps).
        back_recline_angle=round(rng.uniform(0.0, 0.30), 4),
        name=f"seeded_folding_chair_{seed}",
    )


def resolve_config(config: FoldingChairConfig | None = None) -> ResolvedFoldingChairConfig:
    cfg = config or FoldingChairConfig()
    fold = _pick(cfg.fold_mechanism, FOLD_MECHANISMS)
    seat_panel = _pick(cfg.seat_back_panel, SEAT_BACK_PANELS)
    frame = _pick(cfg.frame_style, FRAME_STYLES)
    accessory = _pick(cfg.accessory, ACCESSORIES)
    material = _pick(cfg.material_style, MATERIAL_STYLES)

    h_scale = _clamp(cfg.seat_height_scale, 0.70, 1.05)
    w_scale = _clamp(cfg.seat_width_scale, 0.80, 1.25)
    b_scale = _clamp(cfg.back_height_scale, 0.55, 1.15)

    # ----- height scale: stretch the vertical (z) key points about the floor.
    # The pivot height, seat hinge, seat front, and backrest top scale together
    # so four feet stay at z~0, the seat stays level, and the mimic coupling
    # (a function of geometry slopes, which are scale-invariant in z about the
    # floor) is preserved.
    def sz(z: float) -> float:
        return z * h_scale

    pivot = (_PIVOT[0], sz(_PIVOT[1]))
    rear_foot = (_REAR_FOOT[0], _REAR_FOOT[1])
    front_foot = (_FRONT_FOOT[0], _FRONT_FOOT[1])
    seat_hinge = (_SEAT_HINGE[0], sz(_SEAT_HINGE[1]))
    seat_front = (_SEAT_FRONT[0], sz(_SEAT_FRONT[1]))
    # Backrest top: base height scaled by seat-height, then the back-height
    # scale stretches the span ABOVE the seat hinge (so a stool keeps a small
    # back, a director chair a tall one) without dropping below the seat. The
    # span has a floor so even a stool keeps a real (small) backrest panel.
    base_back_top_z = sz(_BACK_TOP[1])
    back_span = max(0.22, (base_back_top_z - seat_hinge[1]) * b_scale)
    back_top = (_BACK_TOP[0], seat_hinge[1] + back_span)

    # ----- width scale: stretch y extents and seat/back panel widths.
    half_w = _HALF_W * w_scale
    seat_w = _SEAT_W * w_scale
    back_w = _BACK_W * w_scale

    # Backrest panel height shrinks for short backs but never below the span,
    # and its center sits so the panel bottom stays clear above the seat hinge.
    back_h = min(_BACK_H, back_span - 0.04)
    back_bottom_floor = seat_hinge[1] + 0.075  # clear of the seat plane
    back_mid_z = back_top[1] - back_h / 2.0 - 0.04
    if back_mid_z - back_h / 2.0 < back_bottom_floor:
        back_mid_z = back_bottom_floor + back_h / 2.0

    # ----- recline conditional: ignored unless the accessory is the recliner.
    recline = (
        _clamp(cfg.back_recline_angle, 0.0, _RECLINE_UPPER)
        if accessory == "reclining_backrest_2nd_hinge"
        else 0.0
    )

    return ResolvedFoldingChairConfig(
        fold_mechanism=fold,
        seat_back_panel=seat_panel,
        frame_style=frame,
        accessory=accessory,
        material_style=material,
        seat_height_scale=h_scale,
        seat_width_scale=w_scale,
        back_height_scale=b_scale,
        tube_r=_TUBE_R,
        half_w=half_w,
        pivot=pivot,
        rear_foot=rear_foot,
        back_top=back_top,
        seat_hinge=seat_hinge,
        front_foot=front_foot,
        seat_front=seat_front,
        seat_w=seat_w,
        seat_depth=_SEAT_DEPTH,
        seat_thick=_SEAT_THICK,
        back_w=back_w,
        back_h=back_h,
        back_thick=_BACK_THICK,
        back_mid_z=back_mid_z,
        fold_upper=_FOLD_UPPER,
        seat_fold_mult=_SEAT_FOLD_MULT,
        back_recline_angle=recline,
        name=cfg.name or "folding_chair",
    )


def with_overrides(config: FoldingChairConfig, **kwargs: object) -> FoldingChairConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: FoldingChairConfig | ResolvedFoldingChairConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedFoldingChairConfig) else resolve_config(config)
    return (
        ("fold_mechanism", r.fold_mechanism),
        ("seat_back_panel", r.seat_back_panel),
        # Frame is reported by its topology family (tube vs flat_bar) so the
        # module_topology_diversity gate counts only real structural change.
        ("frame_style", _FRAME_PRIMITIVE[r.frame_style]),
        ("accessory", r.accessory),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Frame primitives — tube family (parent _leg_tube/_cross_tube) and flat_bar
# family (v18 _flat_bar_path/_cross_flat_bar). A FrameKit bundles the two
# emitters so the skeleton builders are frame-style agnostic.
# ---------------------------------------------------------------------------
def _leg_tube(p_xz_list, y: float, radius: float, name: str) -> object:
    pts = [(x, y, z) for (x, z) in p_xz_list]
    geom = tube_from_spline_points(
        pts, radius=radius, samples_per_segment=12, radial_segments=14, cap_ends=True
    )
    return mesh_from_geometry(geom, name)


def _cross_tube(a, b, r: float, name: str) -> object:
    geom = tube_from_spline_points(
        [a, b], radius=r, samples_per_segment=4, radial_segments=12, cap_ends=True
    )
    return mesh_from_geometry(geom, name)


def _flat_bar_between(a, b) -> tuple[Box, Origin]:
    ax, ay, az = a
    bx, by, bz = b
    dx, dz = bx - ax, bz - az
    length = math.sqrt(dx * dx + (by - ay) ** 2 + dz * dz)
    pitch = -math.atan2(dz, dx)
    return Box((length, _BAR_THICK_Y, _BAR_WIDTH)), Origin(
        xyz=((ax + bx) * 0.5, (ay + by) * 0.5, (az + bz) * 0.5),
        rpy=(0.0, pitch, 0.0),
    )


class _FrameKit:
    """Bundles the per-frame-style leg-rail + cross-bar emitters."""

    def __init__(self, r: ResolvedFoldingChairConfig) -> None:
        self.r = r
        self.is_flat = r.frame_style == "flat_bar_angular"

    def leg_rail(self, part, p_xz_list, y: float, *, material: str, name: str) -> None:
        """Emit one continuous side rail through the (x, z) path at offset y."""
        if self.is_flat:
            for i, ((x0, z0), (x1, z1)) in enumerate(zip(p_xz_list, p_xz_list[1:])):
                geom, origin = _flat_bar_between((x0, y, z0), (x1, y, z1))
                part.visual(geom, origin=origin, material=material, name=f"{name}_seg{i}", material_class_id="metal.paint_coated")
        else:
            part.visual(
                _leg_tube(p_xz_list, y, self.r.tube_r, name),
                material=material,
                name=name, material_class_id="metal.paint_coated",
            )

    def cross_bar(
        self, part, x: float, z: float, half_w: float, r: float, *, material, name
    ) -> None:
        """Emit a width-spanning cross bar at (x, z)."""
        if self.is_flat:
            # Extend a touch past the requested half-width so the bar embeds into
            # the side rails. Tubes already do this via their radius; a flat Box
            # spans exactly its length, so an inset brace (half_w passed short of
            # the rail line) would float free as a disconnected island otherwise.
            length = 2.0 * half_w + 0.040
            part.visual(
                Box((0.026, length, 0.020)),
                origin=Origin(xyz=(x, 0.0, z)),
                material=material,
                name=name, material_class_id="metal.paint_coated",
            )
        else:
            part.visual(
                _cross_tube((x, -half_w, z), (x, half_w, z), r, name),
                material=material,
                name=name, material_class_id=("metal.paint_coated" if self.r.frame_style in {"tubular_steel", "aluminum_tube", "flat_bar_angular"} else "wood.natural_generic"),
            )

    def pivot_hub(self, part, x: float, z: float, half_w: float, *, material) -> None:
        """flat_bar frames get a round pivot hub at the scissor crossing."""
        if not self.is_flat:
            return
        for sgn, tag in ((-1.0, "l"), (1.0, "r")):
            part.visual(
                Cylinder(radius=0.026, length=0.022),
                origin=Origin(xyz=(x, sgn * half_w, z), rpy=(math.pi / 2.0, 0.0, 0.0)),
                material=material,
                name=f"{part.name}_pivot_hub_{tag}", material_class_id="metal.blackened_gunmetal",
            )


# ---------------------------------------------------------------------------
# Seat / backrest visual helpers (Slot B). Each returns ONE mesh authored with
# local X=depth/height, Y=width, Z=thickness so the same helper serves both the
# horizontal seat (no rotation) and the backrest (a -90deg pitch maps local
# X->Z height). wood_slat / fabric_bucket / woven_cane override the simple
# helper path (see emit_* below).
# ---------------------------------------------------------------------------
def _pad_mesh(width: float, depth: float, thick: float, name: str) -> object:
    """Padded vinyl (parent): rounded-rect slab + softened top pad."""
    prof = rounded_rect_profile(width, depth, radius=0.030)
    body = ExtrudeGeometry.from_z0(prof, thick - 0.012, cap=True)
    top_prof = rounded_rect_profile(width - 0.012, depth - 0.012, radius=0.032)
    top = ExtrudeGeometry.from_z0(top_prof, 0.018, cap=True).translate(0.0, 0.0, thick - 0.014)
    return mesh_from_geometry(body.merge(top), name)


def _molded_mesh(width: float, depth: float, thick: float, name: str) -> object:
    """Molded plastic (v02): shell + central dish + perimeter lip merge."""
    prof = rounded_rect_profile(width, depth, radius=0.035)
    shell = ExtrudeGeometry.from_z0(prof, thick - 0.010, cap=True)
    dish_prof = rounded_rect_profile(width - 0.060, depth - 0.060, radius=0.026)
    dish = ExtrudeGeometry.from_z0(dish_prof, 0.010, cap=True).translate(0.0, 0.0, thick - 0.014)
    lip_prof = rounded_rect_profile(width - 0.012, depth - 0.012, radius=0.032)
    lip = ExtrudeGeometry.from_z0(lip_prof, 0.007, cap=True).translate(0.0, 0.0, thick - 0.006)
    return mesh_from_geometry(shell.merge(dish).merge(lip), name)


def _sling_mesh(width: float, depth: float, thick: float, name: str) -> object:
    """Fabric sling (v01): thin sewn panel + shallow crown."""
    prof = rounded_rect_profile(width, depth, radius=0.024)
    body = ExtrudeGeometry.from_z0(prof, thick, cap=True)
    inset_prof = rounded_rect_profile(width - 0.030, depth - 0.030, radius=0.018)
    crown = ExtrudeGeometry.from_z0(inset_prof, thick * 0.35, cap=True).translate(
        0.0, 0.0, thick * 0.75
    )
    return mesh_from_geometry(body.merge(crown), name)


def _canvas_mesh(width: float, depth: float, thick: float, name: str) -> object:
    """Canvas (v12): thin panel + raised hem."""
    prof = rounded_rect_profile(width, depth, radius=0.020)
    body = ExtrudeGeometry.from_z0(prof, thick, cap=True)
    hem_prof = rounded_rect_profile(width - 0.010, depth - 0.010, radius=0.018)
    hem = ExtrudeGeometry.from_z0(hem_prof, 0.004, cap=True).translate(0.0, 0.0, thick - 0.001)
    return mesh_from_geometry(body.merge(hem), name)


def _perforated_mesh(width: float, depth: float, thick: float, name: str) -> object:
    """Perforated plastic (v09): real through-hole array + solid rim."""
    geom = PerforatedPanelGeometry(
        (width, depth),
        thick,
        hole_diameter=0.020,
        pitch=(0.042, 0.042),
        frame=0.030,
        corner_radius=0.028,
        stagger=True,
    )
    return mesh_from_geometry(geom, name)


def _poly_mesh(width: float, depth: float, thick: float, name: str) -> object:
    """Translucent polycarbonate (v11): single softened-corner panel."""
    prof = rounded_rect_profile(width, depth, radius=0.035)
    return mesh_from_geometry(ExtrudeGeometry.from_z0(prof, thick, cap=True), name)


def _cane_mesh(depth: float, width: float, thick: float, name: str) -> object:
    """Woven cane (v17): base panel + merged crossing straps + thick rim.

    Matches the other helpers' convention: first arg = local X extent (seat depth
    / backrest height), second arg = local Y extent (frame width). Its internal
    layout uses ``depth`` along X and ``width`` along Y."""
    base_prof = rounded_rect_profile(depth, width, radius=0.025)
    geom = ExtrudeGeometry.from_z0(base_prof, thick, cap=True)
    strip_w = 0.014
    n_y = max(3, int(round(width / 0.060)))
    for j in range(n_y):
        y = -width / 2.0 + 0.045 + (width - 0.090) * j / max(1, n_y - 1)
        strip = ExtrudeGeometry.from_z0(
            rounded_rect_profile(depth - 0.055, strip_w, radius=0.004), 0.006, cap=True
        ).translate(0.0, y, thick - 0.001)
        geom = geom.merge(strip)
    n_x = max(3, int(round(depth / 0.055)))
    for i in range(n_x):
        x = -depth / 2.0 + 0.045 + (depth - 0.090) * i / max(1, n_x - 1)
        strip = ExtrudeGeometry.from_z0(
            rounded_rect_profile(strip_w, width - 0.050, radius=0.004), 0.006, cap=True
        ).translate(x, 0.0, thick + 0.004)
        geom = geom.merge(strip)
    for tx, prof_wh in (
        (depth / 2.0 - 0.015, (0.030, width)),
        (-depth / 2.0 + 0.015, (0.030, width)),
    ):
        rim = ExtrudeGeometry.from_z0(
            rounded_rect_profile(*prof_wh, radius=0.010), thick + 0.010, cap=True
        ).translate(tx, 0.0, -0.002)
        geom = geom.merge(rim)
    for ty in (-width / 2.0 + 0.015, width / 2.0 - 0.015):
        rim = ExtrudeGeometry.from_z0(
            rounded_rect_profile(depth, 0.030, radius=0.010), thick + 0.010, cap=True
        ).translate(0.0, ty, -0.002)
        geom = geom.merge(rim)
    return mesh_from_geometry(geom, name)


def _fabric_bucket_mesh(width: float, depth: float, thick: float, name: str) -> object:
    """Sagging fabric bucket seat (v20): raised perimeter, lower center."""
    nx, ny = 8, 8
    geom = MeshGeometry()
    top: list[list[int]] = []
    bottom: list[list[int]] = []
    for i in range(nx + 1):
        row_t: list[int] = []
        row_b: list[int] = []
        x = -depth / 2.0 + depth * i / nx
        ux = i / nx
        for j in range(ny + 1):
            y = -width / 2.0 + width * j / ny
            uy = j / ny
            side_lift = 0.016 * abs(2.0 * uy - 1.0) ** 1.7
            rf_lift = 0.010 * (abs(2.0 * ux - 1.0) ** 1.4)
            # Shallow sag: a deep bucket center hangs ~30mm below the rigid pads
            # and swept its lowest point straight into the fixed scissor bolt as
            # the seat folds down. Kept just deep enough to still read as a sag.
            sag = -0.020 * math.sin(math.pi * ux) * math.sin(math.pi * uy)
            z = side_lift + rf_lift + sag
            row_t.append(geom.add_vertex(x, y, z + thick / 2.0))
            row_b.append(geom.add_vertex(x, y, z - thick / 2.0))
        top.append(row_t)
        bottom.append(row_b)
    for i in range(nx):
        for j in range(ny):
            a, b, c, d = top[i][j], top[i + 1][j], top[i + 1][j + 1], top[i][j + 1]
            geom.add_face(a, b, c)
            geom.add_face(a, c, d)
            a, b, c, d = bottom[i][j], bottom[i][j + 1], bottom[i + 1][j + 1], bottom[i + 1][j]
            geom.add_face(a, b, c)
            geom.add_face(a, c, d)
    for i in range(nx):
        for j in (0, ny):
            a, b = top[i][j], top[i + 1][j]
            c, d = bottom[i + 1][j], bottom[i][j]
            geom.add_face(a, b, c)
            geom.add_face(a, c, d)
    for j in range(ny):
        for i in (0, nx):
            a, b = top[i][j], top[i][j + 1]
            c, d = bottom[i][j + 1], bottom[i][j]
            geom.add_face(a, b, c)
            geom.add_face(a, c, d)
    return mesh_from_geometry(geom, name)


def _fabric_back_mesh(height: float, width: float, thick: float, name: str) -> object:
    """Cupped fabric backrest (v20): local X=height, Y=width."""
    nx, ny = 6, 8
    geom = MeshGeometry()
    front: list[list[int]] = []
    rear: list[list[int]] = []
    for i in range(nx + 1):
        row_f: list[int] = []
        row_r: list[int] = []
        x = -height / 2.0 + height * i / nx
        ux = i / nx
        for j in range(ny + 1):
            y = -width / 2.0 + width * j / ny
            uy = j / ny
            cup = -0.022 * math.sin(math.pi * ux) * math.sin(math.pi * uy)
            edge = 0.006 * abs(2.0 * uy - 1.0)
            z = cup + edge
            row_f.append(geom.add_vertex(x, y, z + thick / 2.0))
            row_r.append(geom.add_vertex(x, y, z - thick / 2.0))
        front.append(row_f)
        rear.append(row_r)
    for i in range(nx):
        for j in range(ny):
            a, b, c, d = front[i][j], front[i + 1][j], front[i + 1][j + 1], front[i][j + 1]
            geom.add_face(a, b, c)
            geom.add_face(a, c, d)
            a, b, c, d = rear[i][j], rear[i][j + 1], rear[i + 1][j + 1], rear[i + 1][j]
            geom.add_face(a, b, c)
            geom.add_face(a, c, d)
    for i in range(nx):
        for j in (0, ny):
            a, b = front[i][j], front[i + 1][j]
            c, d = rear[i + 1][j], rear[i][j]
            geom.add_face(a, b, c)
            geom.add_face(a, c, d)
    for j in range(ny):
        for i in (0, nx):
            a, b = front[i][j], front[i][j + 1]
            c, d = rear[i][j + 1], rear[i][j]
            geom.add_face(a, b, c)
            geom.add_face(a, c, d)
    return mesh_from_geometry(geom, name)


def _handle_back_mesh(back_h: float, back_w: float, back_thick: float, name: str) -> object:
    """Carry-handle backrest (v16): BezelGeometry with a through hand-slot."""
    geom = BezelGeometry(
        opening_size=(_HANDLE_H, min(_HANDLE_W, back_w - 0.10)),
        outer_size=(back_h, back_w),
        depth=back_thick,
        opening_shape="rounded_rect",
        outer_shape="rounded_rect",
        opening_corner_radius=0.018,
        outer_corner_radius=0.030,
        wall=(0.055, 0.035, 0.070, 0.035),
        center=True,
    )
    return mesh_from_geometry(geom, name)


# Simple single-mesh seat helpers keyed by module name. wood_slat (part-local
# loop), fabric_bucket (MeshGeometry), woven_cane (merge) and carry_handle
# (bezel back only) are handled specially in the emit_* functions.
_SIMPLE_SEAT_HELPERS = {
    "padded_pad": _pad_mesh,
    "molded_plastic": _molded_mesh,
    "fabric_sling": _sling_mesh,
    "canvas": _canvas_mesh,
    "perforated_plastic": _perforated_mesh,
    "polycarbonate_translucent": _poly_mesh,
    "woven_cane": _cane_mesh,
    "fabric_bucket": _fabric_bucket_mesh,
}


def _seat_thick_for(panel: SeatBackPanel, base: float) -> float:
    """Fabric/canvas/sling/cane panels are thin; molded/perforated medium."""
    if panel in ("fabric_sling", "canvas", "fabric_bucket"):
        return 0.008
    if panel in ("woven_cane", "polycarbonate_translucent"):
        return 0.014
    if panel in ("molded_plastic", "perforated_plastic"):
        return 0.030
    return base


def _emit_seat_surface(seat, r: ResolvedFoldingChairConfig, *, seat_mat) -> None:
    """Emit the seat_pan visual(s). Authored about the seat hinge frame so the
    pad extends +X and is horizontal at q=0 (parent L255-265)."""
    panel = r.seat_back_panel
    depth, width = r.seat_depth, r.seat_w
    thick = _seat_thick_for(panel, r.seat_thick)
    center_x = depth / 2.0  # forward of the hinge (local hinge frame at x=0)

    if panel == "wood_slat":
        # Five separate slats + two battens + rear hinge dowel (v03).
        for idx, y in enumerate(_slat_y_positions(5, width)):
            seat.visual(
                Box((depth - 0.020, 0.048, thick)),
                origin=Origin(xyz=(center_x + 0.010, y, -0.020)),
                material=seat_mat,
                name=f"seat_slat_{idx}", material_class_id="wood.natural_generic",
            )
        for x, sx, name in (
            (0.025, 0.060, "rear_seat_batten"),
            (depth - 0.070, 0.050, "front_seat_batten"),
        ):
            seat.visual(
                Box((sx, width + 0.020, 0.018)),
                origin=Origin(xyz=(x, 0.0, -0.040)),
                material=seat_mat,
                name=name, material_class_id="wood.natural_generic",
            )
        # Span the slats but stay inside the frame width so the dowel ends do not
        # poke into the side uprights / triangle braces (kept < frame half-width).
        seat.visual(
            Cylinder(radius=0.010, length=min(width + 0.060, 2.0 * r.half_w - 0.060)),
            origin=Origin(xyz=(0.0, 0.0, -0.022), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=seat_mat,
            name="seat_hinge_dowel", material_class_id="wood.natural_generic",
        )
        return

    z_off = -0.006 if panel in ("fabric_sling", "canvas", "fabric_bucket") else -0.022
    helper = _SIMPLE_SEAT_HELPERS[panel]
    seat.visual(
        helper(depth, width, thick, "seat_pad"),
        origin=Origin(xyz=(center_x, 0.0, z_off)),
        material=seat_mat,
        name="seat_pad", material_class_id=("fabric.upholstery_plain" if r.seat_back_panel in {"padded_pad", "fabric_sling", "canvas", "wood_slat", "woven_cane", "fabric_bucket"} else "plastic.frosted_translucent"),
    )
    # Rear hinge dowel at the seat's local origin so the seat_hinge child origin
    # sits on real hardware (thin panels otherwise leave the origin in air). Kept
    # just inside the frame width so its ends do not poke into the uprights. Its z
    # is set to the pad's actual rear-edge mid-plane so the dowel is solidly
    # embedded in the panel for every helper (thin/lifted fabric otherwise leaves
    # it as a disconnected island); a generous radius bridges the rear-edge band.
    if panel == "fabric_bucket":
        dowel_z = 0.015 + z_off  # rear edge of the bucket mesh is lifted (rf_lift)
    else:
        dowel_z = z_off + thick / 2.0
    # Dowel stays at the seat's local origin so the seat_hinge child origin sits
    # on it. Its z tracks the panel rear-edge mid-plane so it is the nearest
    # geometry to the joint origin for every helper.
    seat.visual(
        Cylinder(radius=0.014, length=min(max(0.12, width - 0.040), 2.0 * r.half_w - 0.060)),
        origin=Origin(xyz=(0.0, 0.0, dowel_z), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=seat_mat,
        name="seat_hinge_dowel", material_class_id=("metal.blackened_gunmetal" if r.seat_back_panel in {"padded_pad", "molded_plastic", "fabric_sling", "canvas", "perforated_plastic", "polycarbonate_translucent", "fabric_bucket"} else "wood.natural_generic"),
    )
    # Bracket bridging the dowel forward into the SOLID panel body: a thin/sagging
    # panel only grazes the dowel at its rear face (too shallow for FCL contact),
    # which would otherwise leave the dowel a disconnected island.
    seat.visual(
        Box((0.060, 0.040, 0.016)),
        origin=Origin(xyz=(0.030, 0.0, dowel_z)),
        material=seat_mat,
        name="seat_hinge_bracket", material_class_id=("metal.blackened_gunmetal" if r.seat_back_panel in {"padded_pad", "molded_plastic", "fabric_sling", "canvas", "perforated_plastic", "polycarbonate_translucent", "fabric_bucket"} else "wood.natural_generic"),
    )
    if panel == "molded_plastic":
        # Integral underside stiffening ribs (v02), a real molded feature.
        for y, tag in ((-0.115, "0"), (0.115, "1")):
            seat.visual(
                Box((0.30, 0.026, 0.018)),
                origin=Origin(xyz=(center_x + 0.010, y, -0.028)),
                material=seat_mat,
                name=f"seat_rib_{tag}", material_class_id="plastic.opaque_glossy_molded",
            )


def _emit_backrest(
    part,
    r: ResolvedFoldingChairConfig,
    *,
    back_mat,
    x0: float = 0.0,
    z0: float = 0.0,
    handle: bool = False,
    vertical_mounts: bool = False,
) -> None:
    """Emit the backrest visual onto ``part`` (rear frame, or the reclining
    backrest part). ``x0``/``z0`` shift the panel into the part's local frame.
    Authored with local X=height, a -90deg pitch maps it to a vertical panel.

    Two width-spanning mount rails (on the upright line at the panel's z-band)
    tie the panel to the uprights so it is supported, not a floating island.
    When ``vertical_mounts`` both rails sit on the (vertical) panel line instead
    of tracking the leaning uprights -- used for the standalone reclining
    backrest part, which has no uprights to catch a trailing lower rail.
    ``handle`` swaps the simple panel for a BezelGeometry carry-handle back.
    """
    panel = r.seat_back_panel
    bh, bw, bt = r.back_h, r.back_w, r.back_thick
    bz = r.back_mid_z - z0
    rpy = (0.0, -math.pi / 2.0, 0.0)

    upr_x_top = _line_x_at_z(r.seat_hinge, r.back_top, r.back_mid_z + bh / 2.0 - 0.012)
    upr_x_bot = _line_x_at_z(r.seat_hinge, r.back_top, r.back_mid_z - bh / 2.0 + 0.012)
    # Both rails on the panel line (vertical) for the standalone backrest, else
    # each on the leaning-upright line so they meet the rear frame uprights.
    mount_top_x = max(upr_x_top, upr_x_bot) if vertical_mounts else upr_x_top
    mount_bot_x = max(upr_x_top, upr_x_bot) if vertical_mounts else upr_x_bot
    part.visual(
        _cross_tube(
            (mount_top_x - x0, -r.half_w, bz + bh / 2.0 - 0.012),
            (mount_top_x - x0, r.half_w, bz + bh / 2.0 - 0.012),
            r.tube_r - 0.003,
            "back_mount_upper",
        ),
        material=back_mat,
        name="back_mount_upper", material_class_id=("metal.paint_coated" if r.frame_style in {"tubular_steel", "aluminum_tube", "flat_bar_angular"} else "wood.natural_generic"),
    )
    part.visual(
        _cross_tube(
            (mount_bot_x - x0, -r.half_w, bz - bh / 2.0 + 0.012),
            (mount_bot_x - x0, r.half_w, bz - bh / 2.0 + 0.012),
            r.tube_r - 0.003,
            "back_mount_lower",
        ),
        material=back_mat,
        name="back_mount_lower", material_class_id=("metal.paint_coated" if r.frame_style in {"tubular_steel", "aluminum_tube", "flat_bar_angular"} else "wood.natural_generic"),
    )
    # Panel center sits on the (more-forward) mount-rail line so the rail is
    # embedded in the panel's rear half: real contact, and the panel never
    # protrudes forward into the seat / tablet zone. When the backrest is a
    # separate moving part, push it forward enough that its (full-width) edges
    # clear the fixed uprights it would otherwise straddle.
    panel_thick = _seat_thick_for(panel, bt)
    panel_x = max(upr_x_top, upr_x_bot) - x0

    if handle:
        part.visual(
            _handle_back_mesh(bh, bw, bt, "backrest_pad"),
            origin=Origin(xyz=(panel_x, 0.0, bz), rpy=rpy),
            material=back_mat,
            name="backrest_pad", material_class_id=("fabric.upholstery_plain" if r.seat_back_panel in {"padded_pad", "fabric_sling", "canvas", "wood_slat", "woven_cane", "fabric_bucket"} else "plastic.frosted_translucent"),
        )
        return

    if panel == "wood_slat":
        for idx, y in enumerate(_slat_y_positions(5, bw)):
            part.visual(
                Box((bt, 0.050, bh)),
                origin=Origin(xyz=(panel_x, y, bz)),
                material=back_mat,
                name=f"back_slat_{idx}", material_class_id="wood.natural_generic",
            )
        return

    if panel == "fabric_bucket":
        part.visual(
            _fabric_back_mesh(bh, bw, 0.008, "backrest_pad"),
            origin=Origin(xyz=(panel_x, 0.0, bz), rpy=rpy),
            material=back_mat,
            name="backrest_pad", material_class_id="fabric.upholstery_plain",
        )
        return

    helper = _SIMPLE_SEAT_HELPERS[panel]
    part.visual(
        helper(bh, bw, panel_thick, "backrest_pad"),
        origin=Origin(xyz=(panel_x, 0.0, bz), rpy=rpy),
        material=back_mat,
        name="backrest_pad", material_class_id=("fabric.upholstery_plain" if r.seat_back_panel in {"padded_pad", "fabric_sling", "canvas", "wood_slat", "woven_cane", "fabric_bucket"} else "plastic.frosted_translucent"),
    )


def _slat_y_positions(count: int, width: float) -> list[float]:
    if count == 1:
        return [0.0]
    usable = width - 0.060
    step = usable / float(count - 1)
    return [-usable / 2.0 + i * step for i in range(count)]


# ---------------------------------------------------------------------------
# Skeleton builders. The rear and front leg frames are emitted with the
# frame-style-aware FrameKit; the fold_mechanism slot may add extra braces.
# ---------------------------------------------------------------------------
def _line_x_at_z(p0: tuple[float, float], p1: tuple[float, float], z: float) -> float:
    """X on the segment p0->p1 at height z (for braces that meet both legs)."""
    (x0, z0), (x1, z1) = p0, p1
    if abs(z1 - z0) < 1e-9:
        return 0.5 * (x0 + x1)
    return x0 + (x1 - x0) * (z - z0) / (z1 - z0)


def _revolute_swept_clear_lower_limit(
    hinge: tuple[float, float],
    tip: tuple[float, float],
    obstacle: tuple[float, float],
    *,
    clear: float,
    hard_min: float,
    step: float = 0.02,
) -> float:
    """Largest-magnitude NEGATIVE (+Y) rotation of a straight member about
    ``hinge`` (open-pose end at ``tip``) that keeps the member's centerline at
    least ``clear`` from a fixed ``obstacle`` point, floored at ``hard_min``.

    Used to bound a fold joint by its own swept envelope so a folding tube never
    drives through fixed pivot hardware (>=8mm margin lives in ``clear``)."""
    hx, hz = hinge
    dx0, dz0 = tip[0] - hx, tip[1] - hz
    length = math.hypot(dx0, dz0)
    if length < 1e-9:
        return hard_min
    px, pz = obstacle[0] - hx, obstacle[1] - hz
    theta = 0.0
    while theta > hard_min:
        c, s = math.cos(theta), math.sin(theta)
        # Rotate the open-pose member direction about +Y.
        ux = (dx0 * c + dz0 * s) / length
        uz = (-dx0 * s + dz0 * c) / length
        t = max(0.0, min(length, px * ux + pz * uz))
        dist = math.hypot(px - t * ux, pz - t * uz)
        if dist < clear:
            return min(0.0, theta + step)
        theta -= step
    return hard_min


def _build_rear_frame(
    rear, r: ResolvedFoldingChairConfig, kit: _FrameKit, *, frame_mat, accent_mat, rubber_mat
) -> None:
    rear_path = [r.rear_foot, r.pivot, r.seat_hinge, r.back_top]
    for sgn, tag in ((-1.0, "l"), (1.0, "r")):
        kit.leg_rail(
            rear,
            [(x, z) for (x, z) in rear_path],
            sgn * r.half_w,
            material=frame_mat,
            name=f"rear_upright_{tag}",
        )
        rear.visual(
            Cylinder(radius=r.tube_r + 0.004, length=0.030),
            origin=Origin(xyz=(r.rear_foot[0], sgn * r.half_w, 0.015)),
            material=rubber_mat,
            name=f"rear_foot_{tag}", material_class_id="rubber.smooth_plain",
        )
    kit.pivot_hub(rear, r.pivot[0], r.pivot[1], r.half_w, material=accent_mat)
    # Scissor pivot bolt: a real width-spanning bolt through the crossing so the
    # fold_pivot origin (centerline of the pivot) sits on hardware, not in air
    # between the two side rails.
    rear.visual(
        Cylinder(radius=r.tube_r + 0.002, length=2.0 * r.half_w + 0.012),
        origin=Origin(xyz=(r.pivot[0], 0.0, r.pivot[1]), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=accent_mat,
        name="scissor_bolt", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"steel_gray", "black_powder", "wood", "matte_red", "green", "ripstop_blue"} else "metal.aluminum_bare"),
    )
    # Top backrest rail.
    kit.cross_bar(
        rear,
        r.back_top[0],
        r.back_top[1],
        r.half_w,
        r.tube_r,
        material=frame_mat,
        name="back_rail_top",
    )
    # Rear seat-hinge bar.
    kit.cross_bar(
        rear,
        r.seat_hinge[0],
        r.seat_hinge[1],
        r.half_w,
        r.tube_r,
        material=accent_mat,
        name="seat_hinge_bar",
    )
    # Lower rear cross brace near the floor, on the rear-leg line so it meets both legs.
    rbz = 0.085
    rbx = _line_x_at_z(r.rear_foot, r.pivot, rbz)
    kit.cross_bar(
        rear,
        rbx,
        rbz,
        r.half_w - 0.01,
        r.tube_r - 0.002,
        material=accent_mat,
        name="rear_cross_brace",
    )

    # reinforced_double: a second high rear cross brace (extra stiffness, j=3).
    if r.fold_mechanism == "reinforced_double_cross_brace":
        ubz = 0.5 * (r.pivot[1] + r.seat_hinge[1])
        ubx = _line_x_at_z(r.pivot, r.seat_hinge, ubz)
        kit.cross_bar(
            rear,
            ubx,
            ubz,
            r.half_w - 0.01,
            r.tube_r - 0.002,
            material=accent_mat,
            name="rear_upper_cross_brace",
        )

    # triangular: diagonal compression strut foot -> seat-hinge bar each side.
    if r.fold_mechanism == "triangular_folding_frame":
        for sgn, tag in ((-1.0, "l"), (1.0, "r")):
            kit.leg_rail(
                rear,
                [(r.rear_foot[0], 0.010), (r.seat_hinge[0], r.seat_hinge[1])],
                sgn * (r.half_w - 0.006),
                material=accent_mat,
                name=f"rear_triangle_brace_{tag}",
            )


def _build_front_frame(
    front, r: ResolvedFoldingChairConfig, kit: _FrameKit, *, frame_mat, accent_mat, rubber_mat
):
    """Front visuals authored in the fold-pivot frame: local = world - pivot."""
    px, pz = r.pivot

    def fp(x: float, z: float) -> tuple[float, float]:
        return (x - px, z - pz)

    front_path = [fp(*r.front_foot), fp(*r.pivot), fp(*r.seat_front)]
    for sgn, tag in ((-1.0, "l"), (1.0, "r")):
        kit.leg_rail(front, front_path, sgn * r.half_w, material=frame_mat, name=f"front_leg_{tag}")
        ffx, ffz = fp(*r.front_foot)
        front.visual(
            Cylinder(radius=r.tube_r + 0.004, length=0.030),
            origin=Origin(xyz=(ffx, sgn * r.half_w, ffz + 0.015)),
            material=rubber_mat,
            name=f"front_foot_{tag}", material_class_id="rubber.smooth_plain",
        )
    kit.pivot_hub(front, 0.0, 0.0, r.half_w, material=accent_mat)
    # Scissor pivot bolt sleeve on the front frame, at its local origin (the
    # world pivot at q=0) so the fold_pivot child-side origin sits on hardware.
    front.visual(
        Cylinder(radius=r.tube_r + 0.001, length=2.0 * r.half_w + 0.006),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=accent_mat,
        name="front_pivot_sleeve", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"steel_gray", "black_powder", "wood", "matte_red", "green", "ripstop_blue"} else "metal.aluminum_bare"),
    )
    sfx, sfz = fp(*r.seat_front)
    kit.cross_bar(front, sfx, sfz, r.half_w, r.tube_r, material=accent_mat, name="seat_front_rail")
    fbz = 0.085
    fbx_world = _line_x_at_z(r.front_foot, r.pivot, fbz)
    lbx, lbz = fp(fbx_world, fbz)
    kit.cross_bar(
        front,
        lbx,
        lbz,
        r.half_w - 0.01,
        r.tube_r - 0.002,
        material=accent_mat,
        name="front_cross_brace",
    )

    if r.fold_mechanism == "reinforced_double_cross_brace":
        ubz = 0.5 * (r.pivot[1] + r.seat_front[1])
        ubx_world = _line_x_at_z(r.pivot, r.seat_front, ubz)
        ux, uz = fp(ubx_world, ubz)
        kit.cross_bar(
            front,
            ux,
            uz,
            r.half_w - 0.01,
            r.tube_r - 0.002,
            material=accent_mat,
            name="front_upper_cross_brace",
        )

    if r.fold_mechanism == "triangular_folding_frame":
        for sgn, tag in ((-1.0, "l"), (1.0, "r")):
            a = fp(r.front_foot[0], 0.010)
            b = fp(*r.seat_front)
            kit.leg_rail(
                front,
                [a, b],
                sgn * (r.half_w - 0.006),
                material=accent_mat,
                name=f"front_triangle_brace_{tag}",
            )


# ---------------------------------------------------------------------------
# Fold-mechanism secondary children (rear_legs_fold_under, collapsing_side).
# ---------------------------------------------------------------------------
def _build_rear_under_frame(
    model, rear, r: ResolvedFoldingChairConfig, *, frame_mat, accent_mat, rubber_mat
) -> None:
    """Inboard rear support legs with own REVOLUTE rear_leg_fold (v02)."""
    shx, shz = r.seat_hinge
    under_half_w = r.half_w - 0.045
    # Welded drop tabs that capture the under-frame hinge sleeve, on the rear part.
    for sgn, tag in ((-1.0, "0"), (1.0, "1")):
        rear.visual(
            _cross_tube(
                (shx, sgn * under_half_w, shz),
                (shx, sgn * under_half_w, shz - 0.040),
                0.006,
                f"rear_hinge_tab_{tag}",
            ),
            material=accent_mat,
            name=f"rear_hinge_tab_{tag}", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"steel_gray", "black_powder", "wood", "matte_red", "green", "ripstop_blue"} else "metal.aluminum_bare"),
        )

    rear_under = model.part("rear_under_frame")

    def up(x: float, z: float) -> tuple[float, float]:
        return (x - shx, z - shz)

    under_path = [up(*r.rear_foot), up(shx, shz)]
    for sgn, tag in ((-1.0, "0"), (1.0, "1")):
        rear_under.visual(
            _leg_tube(under_path, sgn * under_half_w, r.tube_r, f"rear_under_leg_{tag}"),
            material=frame_mat,
            name=f"rear_under_leg_{tag}", material_class_id=("metal.paint_coated" if r.frame_style in {"tubular_steel", "aluminum_tube", "flat_bar_angular"} else "wood.natural_generic"),
        )
        ufx, ufz = up(*r.rear_foot)
        rear_under.visual(
            Cylinder(radius=r.tube_r + 0.004, length=0.030),
            origin=Origin(xyz=(ufx, sgn * under_half_w, ufz + 0.015)),
            material=rubber_mat,
            name=f"rear_under_foot_{tag}", material_class_id="rubber.smooth_plain",
        )
    # Hinge sleeve at the child's local origin (the rear_leg_fold axis) so the
    # joint origin sits on the sleeve hardware on both parent and child sides.
    rear_under.visual(
        _cross_tube(
            (0.0, -under_half_w, 0.0),
            (0.0, under_half_w, 0.0),
            r.tube_r + 0.002,
            "rear_under_hinge",
        ),
        material=accent_mat,
        name="rear_under_hinge", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"steel_gray", "black_powder", "wood", "matte_red", "green", "ripstop_blue"} else "metal.aluminum_bare"),
    )
    bx, bz = up(r.rear_foot[0], 0.075)
    rear_under.visual(
        _cross_tube(
            (bx, -under_half_w, bz), (bx, under_half_w, bz), r.tube_r - 0.002, "rear_under_brace"
        ),
        material=accent_mat,
        name="rear_under_brace", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"steel_gray", "black_powder", "wood", "matte_red", "green", "ripstop_blue"} else "metal.aluminum_bare"),
    )
    rear_under.inertial = Inertial.from_geometry(
        Box((0.20, 2.0 * under_half_w, 0.40)),
        mass=1.2,
        origin=Origin(xyz=(up(*r.rear_foot)[0] * 0.5, 0.0, -0.10)),
    )
    # Bound the fold-under travel by the under-leg's own swept envelope: as the
    # inboard legs swing forward-up they must not drive their tubes through the
    # fixed full-width scissor bolt/pivot sleeve at the crossing (r.pivot). The
    # limit is derived so the leg centerline keeps >=10mm clear of the sleeve
    # (leg radius + sleeve radius + margin), floored so a real fold still occurs.
    fold_under_lower = _revolute_swept_clear_lower_limit(
        r.seat_hinge,
        r.rear_foot,
        r.pivot,
        clear=r.tube_r + (r.tube_r + 0.001) + 0.010,
        hard_min=-1.45,
    )
    # Drive the under-legs as a MIMIC of the main fold so they are never sampled
    # at a shallow angle while the front frame is fully folded: an independent
    # joint let motion QC pose "front fully folded + under-legs barely folded",
    # in which the folded front frame's low cross brace (and the flip-down
    # footrest loop) sweep straight into a still-deployed under-leg. Synchronised
    # folding tucks the legs up out of that swept volume at every sampled pose,
    # and is the physically correct single-action collapse. The synchronized
    # full-fold angle stays inside the swept-clear sleeve limit above.
    target_full = (
        _REAR_UNDER_FOLD_FULL_FOOTREST
        if r.accessory == "flip_down_footrest"
        else _REAR_UNDER_FOLD_FULL
    )
    fold_under_full = max(target_full, fold_under_lower + 0.06)
    model.articulation(
        "rear_leg_fold",
        ArticulationType.REVOLUTE,
        parent=rear,
        child=rear_under,
        origin=Origin(xyz=(shx, 0.0, shz)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=18.0, velocity=2.0, lower=fold_under_full, upper=0.0),
        mimic=Mimic(joint="fold_pivot", multiplier=fold_under_full / r.fold_upper, offset=0.0),
    )


def _build_side_links(model, rear, r: ResolvedFoldingChairConfig, *, accent_mat) -> None:
    """Collapsing U-shaped side links, REVOLUTE mimic of fold_pivot (v20)."""
    # Side-link hinge axis on the rear-leg line (so the pivot bar touches both
    # legs), dropped BELOW the scissor crossing. Its full-width pivot bar + axle
    # would otherwise sit just under the seat plane where the folding seat's
    # underside (esp. the ribbed molded pan) sweeps down through the crossing and
    # grazes them. Below the pivot the seat underside is always well above, so
    # the bar/axle keep >8mm clear across the whole fold; height-scale relative.
    lhz = r.pivot[1] - 0.065
    lhx = (
        _line_x_at_z(r.rear_foot, r.pivot, lhz)
        if lhz < r.pivot[1]
        else _line_x_at_z(r.pivot, r.seat_hinge, lhz)
    )
    link_len = 0.285
    link_drop = -0.045
    # Pivot bar on the rear frame at the side-link hinge axis, so the joint
    # origin sits on rear hardware (mirrors the child axle) and meets both legs.
    rear.visual(
        _cross_tube(
            (lhx, -r.half_w, lhz), (lhx, r.half_w, lhz), r.tube_r - 0.001, "side_link_pivot_bar"
        ),
        material=accent_mat,
        name="side_link_pivot_bar", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"steel_gray", "black_powder", "wood", "matte_red", "green", "ripstop_blue"} else "metal.aluminum_bare"),
    )
    side_links = model.part("side_links")
    # Hinge axle spanning the width at the child local origin so the joint origin
    # sits on real hardware (both parent boss and this axle are on it).
    side_links.visual(
        _cross_tube(
            (0.0, -(r.half_w + 0.014), 0.0),
            (0.0, r.half_w + 0.014, 0.0),
            r.tube_r + 0.001,
            "side_link_axle",
        ),
        material=accent_mat,
        name="side_link_axle", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"steel_gray", "black_powder", "wood", "matte_red", "green", "ripstop_blue"} else "metal.aluminum_bare"),
    )
    for sgn, tag in ((-1.0, "l"), (1.0, "r")):
        side_links.visual(
            _cross_tube(
                (0.0, sgn * (r.half_w + 0.012), 0.0),
                (link_len, sgn * (r.half_w + 0.012), link_drop),
                r.tube_r - 0.002,
                f"side_link_{tag}",
            ),
            material=accent_mat,
            name=f"side_link_{tag}", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"steel_gray", "black_powder", "wood", "matte_red", "green", "ripstop_blue"} else "metal.aluminum_bare"),
        )
        side_links.visual(
            Cylinder(radius=r.tube_r + 0.003, length=0.020),
            origin=Origin(xyz=(0.0, sgn * (r.half_w + 0.012), 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=accent_mat,
            name=f"side_hinge_boss_{tag}", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"steel_gray", "black_powder", "wood", "matte_red", "green", "ripstop_blue"} else "metal.aluminum_bare"),
        )
    side_links.visual(
        _cross_tube(
            (link_len, -r.half_w - 0.012, link_drop),
            (link_len, r.half_w + 0.012, link_drop),
            r.tube_r - 0.003,
            "link_front_crossbar",
        ),
        material=accent_mat,
        name="link_front_crossbar", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"steel_gray", "black_powder", "wood", "matte_red", "green", "ripstop_blue"} else "metal.aluminum_bare"),
    )
    side_links.inertial = Inertial.from_geometry(
        Box((link_len, 2.0 * r.half_w, 0.06)),
        mass=0.6,
        origin=Origin(xyz=(link_len / 2.0, 0.0, link_drop / 2.0)),
    )
    model.articulation(
        "side_link_hinge",
        ArticulationType.REVOLUTE,
        parent=rear,
        child=side_links,
        origin=Origin(xyz=(lhx, 0.0, lhz)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(
            effort=8.0,
            velocity=2.0,
            lower=0.0,
            upper=max(0.05, _SIDE_LINK_FOLD_MULT * r.fold_upper),
        ),
        mimic=Mimic(joint="fold_pivot", multiplier=_SIDE_LINK_FOLD_MULT, offset=0.0),
    )


# ---------------------------------------------------------------------------
# Accessory children (tablet / recline / footrest / handle-cutout / plain).
# ---------------------------------------------------------------------------
def _tablet_steel_mesh(r: ResolvedFoldingChairConfig, name: str) -> object:
    """Connected welded steel: pivot sleeve + board support arm + diagonal."""
    sleeve = tube_from_spline_points(
        [(0.0, 0.0, -0.072), (0.0, 0.0, 0.072)],
        radius=r.tube_r + 0.006,
        samples_per_segment=4,
        radial_segments=14,
        cap_ends=True,
    )
    # Arm + diagonal sweep forward and OUTBOARD (+y) so the parked tablet sits
    # beside the chair (clear of the seat) and swings IN over the lap on deploy.
    arm = tube_from_spline_points(
        [(0.016, 0.002, 0.030), (0.300, 0.170, 0.030)],
        radius=r.tube_r - 0.005,
        samples_per_segment=8,
        radial_segments=12,
        cap_ends=True,
    )
    diagonal = tube_from_spline_points(
        [(0.110, 0.060, 0.030), (0.295, 0.235, 0.030)],
        radius=r.tube_r - 0.004,
        samples_per_segment=8,
        radial_segments=12,
        cap_ends=True,
    )
    return mesh_from_geometry(sleeve.merge(arm).merge(diagonal), name)


def _build_tablet_arm(model, rear, r: ResolvedFoldingChairConfig, *, accent_mat, seat_mat) -> None:
    """Writing tablet on a vertical-axis (+Z) REVOLUTE side pivot (v08).

    The pivot post sits outboard of the right upright and is kept at/below seat
    height (its top below the backrest bottom) so the sleeve never collides with
    the backrest panel regardless of the back-height scale."""
    # Seat-height pivot, outboard of the side rail; sleeve spans hinge ±0.072.
    hinge_z = max(r.seat_hinge[1] - 0.040, 0.30)
    hinge = (r.seat_hinge[0] + 0.020, r.half_w + 0.055, hinge_z)
    for z, tag in ((hinge[2] - 0.085, "lower"), (hinge[2] + 0.085, "upper")):
        rear.visual(
            _cross_tube(
                (hinge[0], r.half_w - 0.004, z),
                (hinge[0], r.half_w + 0.055, z),
                r.tube_r - 0.003,
                f"tablet_{tag}_standoff",
            ),
            material=accent_mat,
            name=f"tablet_{tag}_standoff", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"steel_gray", "black_powder", "wood", "matte_red", "green", "ripstop_blue"} else "metal.aluminum_bare"),
        )
    rear.visual(
        Cylinder(radius=r.tube_r + 0.002, length=0.200),
        origin=Origin(xyz=hinge),
        material=accent_mat,
        name="tablet_pivot_post", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"steel_gray", "black_powder", "wood", "matte_red", "green", "ripstop_blue"} else "metal.aluminum_bare"),
    )
    tablet = model.part("tablet_arm")
    # Solid hinge pin through the sleeve axis (child local origin) so the
    # tablet_pivot origin sits on solid hardware, not the hollow sleeve bore.
    tablet.visual(
        Cylinder(radius=r.tube_r - 0.002, length=0.150),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material=accent_mat,
        name="tablet_hinge_pin", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"steel_gray", "black_powder", "wood", "matte_red", "green", "ripstop_blue"} else "metal.aluminum_bare"),
    )
    tablet.visual(
        _tablet_steel_mesh(r, "tablet_hinge_sleeve"),
        material=accent_mat,
        name="tablet_hinge_sleeve", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"steel_gray", "black_powder", "wood", "matte_red", "green", "ripstop_blue"} else "metal.aluminum_bare"),
    )
    # Board rests on the support arm (arm top at z~0.030+tube_r); its underside
    # touches the arm so it is a supported visual, not a floating island.
    tablet.visual(
        _pad_mesh(0.320, 0.240, 0.024, "tablet_board"),
        origin=Origin(xyz=(0.315, 0.175, 0.034)),
        material=seat_mat,
        name="tablet_board", material_class_id="plastic.opaque_glossy_molded",
    )
    tablet.inertial = Inertial.from_geometry(
        Box((0.34, 0.30, 0.05)), mass=0.8, origin=Origin(xyz=(0.20, 0.12, 0.03))
    )
    model.articulation(
        "tablet_pivot",
        ArticulationType.REVOLUTE,
        parent=rear,
        child=tablet,
        origin=Origin(xyz=hinge),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=8.0, velocity=2.0, lower=0.0, upper=1.35),
    )


def _build_reclining_backrest(
    model, rear, r: ResolvedFoldingChairConfig, *, accent_mat, back_mat
) -> None:
    """Backrest split into its own part on a 2nd REVOLUTE (-Y) hinge (v13)."""
    # Hinge axis at the panel TOP edge, on the rear upright line: the panel hangs
    # from the hinge so its top mount rail lands exactly on the hinge axle (both
    # parent + child hinge hardware sit on the axis, panel is connected, and the
    # joint origin lands on real geometry). Keep the hinge at/below the upright
    # top (back_top) so the rear-side hinge bar welds to the uprights instead of
    # floating above them; drop the panel band to suit when it would over-reach.
    max_bhz = r.back_top[1] - 0.012
    bhz = min(r.back_mid_z + r.back_h / 2.0 - 0.012, max_bhz)
    if bhz < r.back_mid_z + r.back_h / 2.0 - 0.012:
        # Lower the panel so its top edge stays at the (clamped) hinge axis.
        r = replace(r, back_mid_z=bhz - r.back_h / 2.0 + 0.012)
    bhx = _line_x_at_z(r.seat_hinge, r.back_top, bhz)
    # Fixed witness rail on the rear upright line (so it welds to both uprights)
    # behind the moving pad, plus a hinge bar on the rear at the recline axis so
    # the joint origin sits on real parent hardware (welded across the uprights).
    support_z = r.back_mid_z
    support_x = _line_x_at_z(r.seat_hinge, r.back_top, support_z)
    rear.visual(
        _cross_tube(
            (support_x, -r.half_w, support_z),
            (support_x, r.half_w, support_z),
            r.tube_r - 0.004,
            "back_support_rail",
        ),
        material=accent_mat,
        name="back_support_rail", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"steel_gray", "black_powder", "wood", "matte_red", "green", "ripstop_blue"} else "metal.aluminum_bare"),
    )
    rear.visual(
        _cross_tube(
            (bhx, -r.half_w, bhz),
            (bhx, r.half_w, bhz),
            r.tube_r - 0.002,
            "back_recline_bar",
        ),
        material=accent_mat,
        name="back_recline_bar", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"steel_gray", "black_powder", "wood", "matte_red", "green", "ripstop_blue"} else "metal.aluminum_bare"),
    )
    backrest = model.part("backrest")
    # Hinge bar on the backrest at its local origin (the recline axis), concentric
    # with the panel's top mount rail (which _emit_backrest puts at z=0 here).
    backrest.visual(
        _cross_tube(
            (0.0, -r.half_w, 0.0), (0.0, r.half_w, 0.0), r.tube_r - 0.002, "back_recline_axle"
        ),
        material=accent_mat,
        name="back_recline_axle", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"steel_gray", "black_powder", "wood", "matte_red", "green", "ripstop_blue"} else "metal.aluminum_bare"),
    )
    _emit_backrest(backrest, r, back_mat=back_mat, x0=bhx, z0=bhz, vertical_mounts=True)
    # Lock-pin detents at the panel/mount line reaching out past the frame width to
    # engage the rear frame; their inboard end embeds in the top mount rail/axle.
    panel_local_x = (
        max(
            _line_x_at_z(r.seat_hinge, r.back_top, r.back_mid_z + r.back_h / 2.0 - 0.012),
            _line_x_at_z(r.seat_hinge, r.back_top, r.back_mid_z - r.back_h / 2.0 + 0.012),
        )
        - bhx
    )
    for sgn, tag in ((-1.0, "l"), (1.0, "r")):
        backrest.visual(
            _cross_tube(
                (panel_local_x, sgn * (r.half_w - 0.006), -0.006),
                (panel_local_x, sgn * (r.half_w + 0.030), -0.006),
                r.tube_r - 0.004,
                f"lock_pin_{tag}",
            ),
            material=accent_mat,
            name=f"lock_pin_{tag}", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"steel_gray", "black_powder", "wood", "matte_red", "green", "ripstop_blue"} else "metal.aluminum_bare"),
        )
    backrest.inertial = Inertial.from_geometry(
        Box((0.06, r.back_w, r.back_h)), mass=0.9, origin=Origin(xyz=(0.05, 0.0, -r.back_h / 2.0))
    )
    model.articulation(
        "back_recline",
        ArticulationType.REVOLUTE,
        parent=rear,
        child=backrest,
        origin=Origin(xyz=(bhx, 0.0, bhz)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=12.0, velocity=1.2, lower=0.0, upper=_RECLINE_UPPER),
    )


def _build_footrest(
    model, front, r: ResolvedFoldingChairConfig, *, frame_mat, accent_mat, rubber_mat
) -> None:
    """Flip-down U-loop footrest on front legs, REVOLUTE mimic of fold (v19)."""
    px, pz = r.pivot

    def fp(x: float, z: float) -> tuple[float, float]:
        return (x - px, z - pz)

    # Hinge well below the scissor crossing (a fraction of the pivot height) so
    # the front legs are still forward of the rear legs there, even for a low
    # (stool-height) chair where the pivot drops; x derived from the leg line so
    # the rail is welded to both legs (otherwise it floats free of them).
    fh_z = min(0.185, 0.55 * r.pivot[1])
    fh_world = (_line_x_at_z(r.front_foot, r.pivot, fh_z), fh_z)
    fhx, fhz = fp(*fh_world)
    reach, drop = 0.110, 0.075
    # Footrest-bar half-width, kept a clear margin INBOARD of the leg lines. When
    # the chair folds flat the front frame lies along the rear frame, so the
    # moving footrest bar's side rails would graze the rear uprights (at +-half_w)
    # if the loop spanned the full width. Insetting the loop keeps it clear of the
    # rear legs in the collapsed bundle across the width-scale range.
    fw = max(0.100, r.half_w - 0.055)
    tread_w = max(0.075, fw - 0.035)
    # Hinge rail welded across the lower front legs (lives on the front part).
    front.visual(
        _cross_tube(
            (fhx, -r.half_w, fhz), (fhx, r.half_w, fhz), r.tube_r - 0.002, "footrest_hinge_rail"
        ),
        material=accent_mat,
        name="footrest_hinge_rail", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"steel_gray", "black_powder", "wood", "matte_red", "green", "ripstop_blue"} else "metal.aluminum_bare"),
    )
    footrest = model.part("footrest_bar")
    # Hinge axle spanning the loop mouth at the child local origin (the
    # footrest_flip axis) so the joint origin sits on real hardware and closes the
    # open back of the U-loop (otherwise the origin floats in the loop's mouth).
    footrest.visual(
        _cross_tube((0.0, -fw, 0.0), (0.0, fw, 0.0), r.tube_r, "footrest_hinge_axle"),
        material=accent_mat,
        name="footrest_hinge_axle", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"steel_gray", "black_powder", "wood", "matte_red", "green", "ripstop_blue"} else "metal.aluminum_bare"),
    )
    loop = tube_from_spline_points(
        [(0.0, -fw, 0.0), (reach, -fw, -drop), (reach, fw, -drop), (0.0, fw, 0.0)],
        radius=r.tube_r - 0.002,
        samples_per_segment=10,
        radial_segments=12,
        cap_ends=True,
    )
    footrest.visual(
        mesh_from_geometry(loop, "footrest_loop"), material=frame_mat, name="footrest_loop", material_class_id=("metal.paint_coated" if r.frame_style in {"tubular_steel", "aluminum_tube", "flat_bar_angular"} else "wood.natural_generic")
    )
    footrest.visual(
        _cross_tube(
            (reach, -tread_w, -drop), (reach, tread_w, -drop), r.tube_r + 0.002, "footrest_tread"
        ),
        material=rubber_mat,
        name="footrest_tread", material_class_id="rubber.smooth_plain",
    )
    footrest.inertial = Inertial.from_geometry(
        Box((reach, 0.34, drop)), mass=0.5, origin=Origin(xyz=(reach / 2.0, 0.0, -drop / 2.0))
    )
    model.articulation(
        "footrest_flip",
        ArticulationType.REVOLUTE,
        parent=front,
        child=footrest,
        origin=Origin(xyz=(fhx, 0.0, fhz)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(
            effort=8.0, velocity=2.0, lower=0.0, upper=_FOOTREST_FOLD_MULT * r.fold_upper
        ),
        mimic=Mimic(joint="fold_pivot", multiplier=_FOOTREST_FOLD_MULT, offset=0.0),
    )


# ---------------------------------------------------------------------------
# Main build
# ---------------------------------------------------------------------------
def build_folding_chair(
    config: FoldingChairConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)

    pal = PALETTES[r.material_style]
    frame_mat = model.material(f"fc_frame_{r.material_style}", rgba=pal["frame"])
    accent_mat = model.material(f"fc_accent_{r.material_style}", rgba=pal["accent"])
    seat_mat = model.material(f"fc_seat_{r.material_style}", rgba=pal["seat"])
    back_mat = model.material(f"fc_back_{r.material_style}", rgba=pal["back"])
    rubber_mat = model.material(f"fc_rubber_{r.material_style}", rgba=pal["rubber"])

    kit = _FrameKit(r)

    # --- ROOT: rear leg frame ------------------------------------------------
    rear = model.part("rear_leg_frame")
    _build_rear_frame(
        rear, r, kit, frame_mat=frame_mat, accent_mat=accent_mat, rubber_mat=rubber_mat
    )
    # Backrest visual lives on the rear frame UNLESS the recline accessory moves
    # it to its own part.
    handle = r.accessory == "carry_handle_cutout"
    reclining = r.accessory == "reclining_backrest_2nd_hinge"
    if not reclining:
        _emit_backrest(rear, r, back_mat=back_mat, handle=handle)
    rear.inertial = Inertial.from_geometry(
        Box((0.40, 2.0 * r.half_w, r.back_top[1])),
        mass=3.5,
        origin=Origin(xyz=(-0.08, 0.0, r.back_top[1] / 2.0)),
    )

    # --- front leg frame + fold_pivot ---------------------------------------
    front = model.part("front_leg_frame")
    _build_front_frame(
        front, r, kit, frame_mat=frame_mat, accent_mat=accent_mat, rubber_mat=rubber_mat
    )
    front.inertial = Inertial.from_geometry(
        Box((0.40, 2.0 * r.half_w, 0.50)), mass=2.5, origin=Origin(xyz=(0.0, 0.0, 0.0))
    )
    model.articulation(
        "fold_pivot",
        ArticulationType.REVOLUTE,
        parent=rear,
        child=front,
        origin=Origin(xyz=(r.pivot[0], 0.0, r.pivot[1])),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=30.0, velocity=2.0, lower=0.0, upper=r.fold_upper),
    )

    # --- seat pan + seat_hinge (mimic) --------------------------------------
    seat = model.part("seat_pan")
    _emit_seat_surface(seat, r, seat_mat=seat_mat)
    seat.inertial = Inertial.from_geometry(
        Box((r.seat_depth, r.seat_w, 0.06)),
        mass=1.2,
        origin=Origin(xyz=(r.seat_depth / 2.0, 0.0, 0.0)),
    )
    model.articulation(
        "seat_hinge",
        ArticulationType.REVOLUTE,
        parent=rear,
        child=seat,
        origin=Origin(xyz=(r.seat_hinge[0], 0.0, r.seat_hinge[1])),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(
            effort=20.0, velocity=2.0, lower=-0.05, upper=r.seat_fold_mult * r.fold_upper
        ),
        mimic=Mimic(joint="fold_pivot", multiplier=r.seat_fold_mult, offset=0.0),
    )

    # --- fold_mechanism secondary children ----------------------------------
    if r.fold_mechanism == "rear_legs_fold_under":
        _build_rear_under_frame(
            model, rear, r, frame_mat=frame_mat, accent_mat=accent_mat, rubber_mat=rubber_mat
        )
    elif r.fold_mechanism == "collapsing_side_hinge_links":
        _build_side_links(model, rear, r, accent_mat=accent_mat)

    # --- accessory child -----------------------------------------------------
    if r.accessory == "pivoting_tablet_arm":
        _build_tablet_arm(model, rear, r, accent_mat=accent_mat, seat_mat=seat_mat)
    elif reclining:
        _build_reclining_backrest(model, rear, r, accent_mat=accent_mat, back_mat=back_mat)
    elif r.accessory == "flip_down_footrest":
        _build_footrest(
            model, front, r, frame_mat=frame_mat, accent_mat=accent_mat, rubber_mat=rubber_mat
        )

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_folding_chair(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_folding_chair(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests / QC (captured-pin overlaps, fold-action checks). The sweep promotes
# warn-level island checks to fail, so these must declare every legitimate
# crossing/capture overlap.
# ---------------------------------------------------------------------------
def run_folding_chair_tests(
    object_model: ArticulatedObject,
    config: FoldingChairConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    part_names = {p.name for p in object_model.parts}

    rear = object_model.get_part("rear_leg_frame")
    front = object_model.get_part("front_leg_frame")
    seat = object_model.get_part("seat_pan")

    seat_elem = "seat_slat_2" if r.seat_back_panel == "wood_slat" else "seat_pad"

    # ---- captured / crossing overlaps (always present) ----
    ctx.allow_overlap(
        rear, front, reason="Front and rear leg frames cross and share the central scissor pivot."
    )
    ctx.allow_overlap(
        front, seat, reason="Seat pan front edge rests on the front-frame seat-front rail."
    )
    ctx.allow_overlap(
        rear,
        seat,
        elem_a="seat_hinge_bar",
        elem_b=seat_elem,
        reason="Seat pan rear edge is captured on the rear hinge bar.",
    )
    # The seat-pan rear hinge dowel runs concentric with the rear seat-hinge bar.
    if seat_elem != "seat_hinge_dowel":
        ctx.allow_overlap(
            rear,
            seat,
            elem_a="seat_hinge_bar",
            elem_b="seat_hinge_dowel",
            reason="Seat-pan rear hinge dowel is concentric with the rear hinge bar.",
        )
    # The hinge bracket (bridging the dowel into the panel body) wraps the same
    # captured hinge axis as the dowel, so it straddles the rear hinge bar.
    if r.seat_back_panel != "wood_slat":
        ctx.allow_overlap(
            rear,
            seat,
            elem_a="seat_hinge_bar",
            elem_b="seat_hinge_bracket",
            reason="Seat-pan hinge bracket wraps the rear hinge bar at the captured hinge axis.",
        )

    # ---- fold_mechanism secondary children ----
    if r.fold_mechanism == "rear_legs_fold_under":
        rear_under = object_model.get_part("rear_under_frame")
        # The whole inboard under-frame nests around the fixed rear seat-hinge
        # axis (legs + sleeve + tabs all capture the same hinge line), and the
        # seat pad hinges on that same axis -> intentional local captures.
        ctx.allow_overlap(
            rear,
            rear_under,
            reason="Inboard rear folding legs are captured on the rear seat-hinge axis (sleeve, legs, tabs all wrap it).",
        )
        ctx.allow_overlap(
            rear_under,
            seat,
            reason="Rear under-frame hinge sleeve shares the seat-hinge axis the seat pan pivots on.",
        )
        for tab in ("rear_hinge_tab_0", "rear_hinge_tab_1"):
            ctx.allow_overlap(
                rear,
                seat,
                elem_a=tab,
                elem_b=seat_elem,
                reason="Hinge tabs tuck under the seat at the rear edge.",
            )
            ctx.allow_overlap(
                rear,
                seat,
                elem_a=tab,
                elem_b="seat_hinge_dowel",
                reason="Hinge tabs wrap the seat-pan rear hinge dowel at the shared hinge axis.",
            )
    elif r.fold_mechanism == "collapsing_side_hinge_links":
        side_links = object_model.get_part("side_links")
        for sgn_tag in ("l", "r"):
            ctx.allow_overlap(
                rear,
                side_links,
                elem_a=f"rear_upright_{sgn_tag}",
                elem_b=f"side_hinge_boss_{sgn_tag}",
                reason="Side-link hinge boss is pinned through the side of the rear frame.",
            )
        # The flat-bar rear rail is segmented; boss may also straddle a segment.
        ctx.allow_overlap(
            rear,
            side_links,
            reason="Collapsing side links are captured against the rear frame side rails.",
        )
        # The side links run forward alongside the front legs through the scissor
        # region (they pull the rails into a flat bundle as the chair folds).
        ctx.allow_overlap(
            front,
            side_links,
            reason="Collapsing side links cross alongside the front legs through the folding scissor region.",
        )

    # ---- accessory children ----
    if r.accessory == "pivoting_tablet_arm":
        tablet = object_model.get_part("tablet_arm")
        ctx.allow_overlap(
            rear,
            tablet,
            elem_a="tablet_pivot_post",
            elem_b="tablet_hinge_sleeve",
            reason="Tablet-arm hinge sleeve is captured around the welded pivot post.",
        )
        ctx.allow_overlap(
            rear,
            tablet,
            elem_a="tablet_pivot_post",
            elem_b="tablet_hinge_pin",
            reason="Tablet hinge pin runs concentric through the welded pivot post.",
        )
    elif r.accessory == "reclining_backrest_2nd_hinge":
        backrest = object_model.get_part("backrest")
        # The reclining backrest is a moving part mounted within the rear frame:
        # its panel + mount rails nest against the fixed uprights, witness rail
        # and lock pins (the captured 2nd-hinge mounting interface).
        ctx.allow_overlap(
            rear,
            backrest,
            reason="Reclining backrest nests against the fixed rear frame (uprights, witness rail, lock pins) at the captured 2nd-hinge mount.",
        )
    elif r.accessory == "flip_down_footrest":
        footrest = object_model.get_part("footrest_bar")
        # The footrest hinge axle + loop mouth are captured on the hinge rail at
        # the same axis as (and crossing) the front legs.
        ctx.allow_overlap(
            front,
            footrest,
            reason="The flip-down footrest hinge axle/loop are captured around the hinge rail on the front legs.",
        )

    # ---- baseline geometric / connectivity gates ----
    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)

    # ---- structural expectations ----
    ctx.check("rear_leg_frame present", "rear_leg_frame" in part_names)
    ctx.check("front_leg_frame present", "front_leg_frame" in part_names)
    ctx.check("seat_pan present", "seat_pan" in part_names)
    ctx.check(
        "slot_choices recorded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    fold = object_model.get_articulation("fold_pivot")
    seat_hinge = object_model.get_articulation("seat_hinge")
    ctx.check(
        "fold_pivot is REVOLUTE about +Y",
        fold.articulation_type == ArticulationType.REVOLUTE
        and abs(fold.axis[1]) > 0.99
        and abs(fold.axis[0]) < 1e-6
        and abs(fold.axis[2]) < 1e-6,
        details=f"type={fold.articulation_type}, axis={tuple(fold.axis)}",
    )
    ctx.check(
        "seat_hinge mimics fold_pivot (single DOF)",
        seat_hinge.mimic is not None and seat_hinge.mimic.joint == "fold_pivot",
        details=f"mimic={seat_hinge.mimic}",
    )

    # Accessory joint axis sanity (spec reject cases).
    if r.accessory == "pivoting_tablet_arm":
        tp = object_model.get_articulation("tablet_pivot")
        ctx.check(
            "tablet_pivot is REVOLUTE about +Z",
            tp.articulation_type == ArticulationType.REVOLUTE and abs(tp.axis[2]) > 0.99,
            details=f"axis={tuple(tp.axis)}",
        )
    if r.accessory == "reclining_backrest_2nd_hinge":
        ctx.check("backrest split into its own part", "backrest" in part_names)
        br = object_model.get_articulation("back_recline")
        ctx.check(
            "back_recline is REVOLUTE about Y",
            br.articulation_type == ArticulationType.REVOLUTE and abs(br.axis[1]) > 0.99,
            details=f"axis={tuple(br.axis)}",
        )
    if r.accessory == "flip_down_footrest":
        fr = object_model.get_articulation("footrest_flip")
        ctx.check(
            "footrest_flip mimics fold_pivot",
            fr.mimic is not None and fr.mimic.joint == "fold_pivot",
            details=f"mimic={fr.mimic}",
        )

    # Total non-fixed joint count never exceeds 5 (compatibility gate).
    moving = [
        j for j in object_model.articulations if j.articulation_type != ArticulationType.FIXED
    ]
    ctx.check("non-fixed joint count <= 5", len(moving) <= 5, details=f"count={len(moving)}")

    # ---- OPEN pose: seat at sitting height, four feet on the floor ----
    seat_aabb = ctx.part_world_aabb(seat)
    if seat_aabb is not None:
        seat_top = seat_aabb[1][2]
        lo = 0.42 * r.seat_height_scale - 0.04
        hi = 0.52 * r.seat_height_scale + 0.04
        ctx.check(
            "seat at sitting height (open)",
            lo <= seat_top <= hi,
            details=f"seat_top={seat_top:.3f}",
        )
        seat_x_open = seat_aabb[1][0] - seat_aabb[0][0]
        seat_z_open = seat_aabb[1][2] - seat_aabb[0][2]
        ctx.check(
            "seat is horizontal when open",
            seat_x_open > 0.30 and seat_z_open < 0.12,
            details=f"x_open={seat_x_open:.3f}, z_open={seat_z_open:.3f}",
        )

    for part, elem in (
        (rear, "rear_foot_l"),
        (rear, "rear_foot_r"),
        (front, "front_foot_l"),
        (front, "front_foot_r"),
    ):
        fa = ctx.part_element_world_aabb(part, elem=elem)
        if fa is not None:
            ctx.check(
                f"{elem} on the floor (open)", fa[0][2] < 0.012, details=f"bottom={fa[0][2]:.4f}"
            )

    rf = ctx.part_element_world_aabb(rear, elem="rear_foot_l")
    ff = ctx.part_element_world_aabb(front, elem="front_foot_l")
    open_stance = None
    if rf is not None and ff is not None:
        open_stance = ff[1][0] - rf[0][0]
        ctx.check(
            "open stance: front feet ahead of rear feet",
            open_stance > 0.28,
            details=f"{open_stance:.3f}",
        )

    # ---- FOLDED pose: stance collapses, seat tips up ----
    if rf is not None and ff is not None and open_stance is not None and seat_aabb is not None:
        seat_x_open = seat_aabb[1][0] - seat_aabb[0][0]
        seat_z_open = seat_aabb[1][2] - seat_aabb[0][2]
        with ctx.pose({fold: r.fold_upper}):
            ff_f = ctx.part_element_world_aabb(front, elem="front_foot_l")
            seat_f = ctx.part_world_aabb(seat)
        if ff_f is not None:
            folded_stance = ff_f[1][0] - rf[0][0]
            ctx.check(
                "folding brings front feet back toward rear feet",
                folded_stance < open_stance - 0.20,
                details=f"open={open_stance:.3f}, folded={folded_stance:.3f}",
            )
        if seat_f is not None:
            seat_z_folded = seat_f[1][2] - seat_f[0][2]
            seat_x_folded = seat_f[1][0] - seat_f[0][0]
            ctx.check(
                "seat folds up (tilts out of horizontal)",
                seat_z_folded > seat_z_open + 0.10 and seat_x_folded < seat_x_open + 0.02,
                details=f"z_open={seat_z_open:.3f}, z_folded={seat_z_folded:.3f}",
            )

    return ctx.report()


__all__ = (
    "FoldingChairConfig",
    "ResolvedFoldingChairConfig",
    "build_folding_chair",
    "build_seeded_folding_chair",
    "config_from_seed",
    "resolve_config",
    "run_folding_chair_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
