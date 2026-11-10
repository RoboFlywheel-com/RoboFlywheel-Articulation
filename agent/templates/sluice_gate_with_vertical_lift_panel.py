# SPDX-License-Identifier: Apache-2.0

"""Modular procedural template for sluice gates with vertical-lift panels.

Spec: ``articraft_template_authoring/specs_modular_v1/sluice_gate_with_vertical_lift_panel.md``.

Slot graph (mixed: PRISMATIC z lift chain + CONTINUOUS hoist branch + optional
gated REVOLUTE child, with optional FIXED operator_housing and separate
guide_rail intermediates)::

    [Slot1 frame] (root, FIXED ground)
      ├── PRISMATIC z (plate_lift) ──► [Slot2 lift_panel]
      ├── [optional FIXED] ──► guide_rail_0 / guide_rail_1   (only `separate_rails_portal`)
      ├── [optional FIXED] ──► operator_housing              (only housing-bearing hoists)
      │     └── CONTINUOUS (handwheel_spin) ──► [Slot3 handwheel|crank_wheel]
      ├── CONTINUOUS (handwheel_spin, direct) ──► [Slot3 ...] (direct-mount hoists)
      └── [optional REVOLUTE] ──► [Slot4 gated_child]
            parent = operator_housing for housing-bearing combos, else frame

Identity invariant (every seed):
  * Exactly one PRISMATIC `(0,0,1)` joint ``frame → lift_panel``.
  * Exactly one CONTINUOUS joint driving ``handwheel|crank_wheel``.
  * Optionally one REVOLUTE joint for the gated child.
  * 0..2 extra FIXED joints for separate rails / operator_housing.

All controlled local scales (panel/frame/wheel/housing sizes, ranges) are
clamped + derived in ``resolve_config`` so cross-module mating (sill seal,
guide-channel capture, top-cap clearance, hub-on-bearing contact) holds
regardless of which module the seed samples.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, replace
from typing import Literal, Optional

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    ExtrudeGeometry,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_geometry,
    rounded_rect_profile,
    section_loft,
)

__modular__ = True


# --------------------------------------------------------------------------
# Slot module enums (topology axes; NOT palette/material)
# --------------------------------------------------------------------------

FrameStyle = Literal[
    "masonry_two_pier",
    "steel_portal_two_post",
    "separate_rails_portal",
    "cadquery_profiled_block",
]
PanelStyle = Literal[
    "planar_slab",
    "ribbed_stiffened_plate",
    "cadquery_profiled_panel",
]
HoistStyle = Literal[
    "gearbox_handwheel_via_housing",
    "large_crank_wheel_direct",
    "direct_handwheel_on_frame",
    "cadquery_handwheel_via_housing",
]
GatedChild = Literal[
    "locking_pawl_revolute",
    "latch_arm_revolute",
    "inspection_door_revolute",
    "gearbox_cover_top_flap",
    "none",
]
MaterialStyle = Literal[
    "concrete_steel",
    "painted_blue",
    "cast_iron",
    "warning_yellow",
]

FRAME_MODULES: tuple[FrameStyle, ...] = (
    "masonry_two_pier",
    "steel_portal_two_post",
    "separate_rails_portal",
    "cadquery_profiled_block",
)
PANEL_MODULES: tuple[PanelStyle, ...] = (
    "planar_slab",
    "ribbed_stiffened_plate",
    "cadquery_profiled_panel",
)
HOIST_MODULES: tuple[HoistStyle, ...] = (
    "gearbox_handwheel_via_housing",
    "large_crank_wheel_direct",
    "direct_handwheel_on_frame",
    "cadquery_handwheel_via_housing",
)
GATED_MODULES: tuple[GatedChild, ...] = (
    "locking_pawl_revolute",
    "latch_arm_revolute",
    "inspection_door_revolute",
    "gearbox_cover_top_flap",
    "none",
)
MATERIAL_STYLES: tuple[MaterialStyle, ...] = (
    "concrete_steel",
    "painted_blue",
    "cast_iron",
    "warning_yellow",
)

# Hoists that emit a FIXED `operator_housing` intermediate; handwheel parent
# becomes the housing. The other two attach handwheel/crank directly to frame.
HOUSING_HOISTS: tuple[HoistStyle, ...] = (
    "gearbox_handwheel_via_housing",
    "cadquery_handwheel_via_housing",
)


PALETTES: dict[MaterialStyle, dict[str, tuple[float, float, float, float]]] = {
    "concrete_steel": {
        "concrete": (0.68, 0.68, 0.66, 1.0),
        "steel": (0.50, 0.53, 0.56, 1.0),
        "dark_steel": (0.24, 0.26, 0.28, 1.0),
        "plate": (0.22, 0.30, 0.38, 1.0),
        "accent": (0.84, 0.66, 0.16, 1.0),
        "rubber": (0.10, 0.10, 0.11, 1.0),
    },
    "painted_blue": {
        "concrete": (0.62, 0.63, 0.62, 1.0),
        "steel": (0.30, 0.42, 0.62, 1.0),
        "dark_steel": (0.14, 0.20, 0.32, 1.0),
        "plate": (0.18, 0.34, 0.58, 1.0),
        "accent": (0.92, 0.62, 0.10, 1.0),
        "rubber": (0.08, 0.08, 0.10, 1.0),
    },
    "cast_iron": {
        "concrete": (0.55, 0.55, 0.55, 1.0),
        "steel": (0.20, 0.20, 0.22, 1.0),
        "dark_steel": (0.10, 0.10, 0.11, 1.0),
        "plate": (0.18, 0.18, 0.20, 1.0),
        "accent": (0.78, 0.10, 0.10, 1.0),
        "rubber": (0.08, 0.08, 0.09, 1.0),
    },
    "warning_yellow": {
        "concrete": (0.66, 0.65, 0.60, 1.0),
        "steel": (0.50, 0.50, 0.50, 1.0),
        "dark_steel": (0.24, 0.24, 0.24, 1.0),
        "plate": (0.86, 0.66, 0.14, 1.0),
        "accent": (0.10, 0.10, 0.11, 1.0),
        "rubber": (0.08, 0.08, 0.09, 1.0),
    },
}


# --------------------------------------------------------------------------
# Config
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class SluiceGateWithVerticalLiftPanelConfig:
    frame_style: Optional[FrameStyle] = None
    panel_style: Optional[PanelStyle] = None
    hoist_style: Optional[HoistStyle] = None
    gated_child: Optional[GatedChild] = None
    material_style: Optional[MaterialStyle] = None
    # Controlled local scales (clamped in resolve_config).
    pier_thickness_scale: float = 1.0
    guide_capture_scale: float = 1.0
    wheel_radius_scale: float = 1.0
    housing_height_scale: float = 1.0
    panel_rib_spacing_scale: float = 1.0
    panel_travel_scale: float = 0.88
    gated_child_range_scale: float = 1.0
    # Core dimensions (clamped to spec ranges in resolve_config).
    panel_w: float = 1.10
    panel_h: float = 1.60
    panel_thickness: float = 0.055
    name: str = "sluice_gate_with_vertical_lift_panel"


@dataclass(frozen=True)
class ResolvedSluiceGateWithVerticalLiftPanelConfig:
    frame_style: FrameStyle
    panel_style: PanelStyle
    hoist_style: HoistStyle
    gated_child: GatedChild
    material_style: MaterialStyle
    # core dims
    panel_w: float
    panel_h: float
    panel_thickness: float
    panel_travel: float
    pier_thickness: float
    pier_spacing: float
    guide_capture: float
    sill_thickness: float
    sill_top_z: float  # top of sill = closed-pose panel-bottom z
    frame_height: float  # top of lintel / top_cap
    lintel_thickness: float
    panel_top_yoke_size: float
    # hoist + housing
    has_housing: bool
    housing_w: float
    housing_d: float
    housing_h: float
    wheel_radius: float
    wheel_axis: tuple[float, float, float]
    # gated child
    has_gated_child: bool
    gated_axis: tuple[float, float, float]
    gated_range_lower: float
    gated_range_upper: float
    # panel detail
    panel_rib_count: int
    panel_edge_bar_thickness: float
    # palette
    palette: dict[str, tuple[float, float, float, float]]
    name: str


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(v)))


def _gate_choice(value, allowed: tuple, rng: random.Random):
    if value is not None and value in allowed:
        return value
    return rng.choice(allowed)


def _gated_compat(hoist: HoistStyle) -> tuple[GatedChild, ...]:
    if hoist in HOUSING_HOISTS:
        return (
            "locking_pawl_revolute",
            "inspection_door_revolute",
            "gearbox_cover_top_flap",
            "latch_arm_revolute",
            "none",
        )
    # direct-mount hoist has no housing for a top-flap cover.
    return (
        "locking_pawl_revolute",
        "latch_arm_revolute",
        "inspection_door_revolute",
        "none",
    )


def _weighted_gated_pick(rng: random.Random, allowed: tuple[GatedChild, ...]) -> GatedChild:
    weights = {
        "locking_pawl_revolute": 0.30,
        "latch_arm_revolute": 0.18,
        "inspection_door_revolute": 0.26,
        "gearbox_cover_top_flap": 0.22,
        "none": 0.04,
    }
    pool = [(g, weights[g]) for g in allowed]
    total = sum(w for _, w in pool)
    r = rng.uniform(0.0, total)
    acc = 0.0
    for g, w in pool:
        acc += w
        if r <= acc:
            return g
    return pool[-1][0]


def config_from_seed(seed: int) -> SluiceGateWithVerticalLiftPanelConfig:
    """Deterministic procedural sampling. seed=0 is not special."""
    rng = random.Random(seed * 7919 + 31)
    frame = rng.choice(FRAME_MODULES)
    panel = rng.choice(PANEL_MODULES)
    hoist = rng.choice(HOIST_MODULES)
    gated = _weighted_gated_pick(rng, _gated_compat(hoist))
    panel_w = round(rng.uniform(0.60, 2.20), 4)
    panel_h = round(rng.uniform(0.90, 2.60), 4)
    if panel == "planar_slab":
        panel_thickness = round(rng.uniform(0.040, 0.065), 4)
    elif panel == "ribbed_stiffened_plate":
        panel_thickness = round(rng.uniform(0.050, 0.085), 4)
    else:
        panel_thickness = round(rng.uniform(0.070, 0.110), 4)
    return SluiceGateWithVerticalLiftPanelConfig(
        frame_style=frame,
        panel_style=panel,
        hoist_style=hoist,
        gated_child=gated,
        material_style=rng.choice(MATERIAL_STYLES),
        pier_thickness_scale=round(rng.uniform(0.88, 1.12), 4),
        guide_capture_scale=round(rng.uniform(0.90, 1.20), 4),
        wheel_radius_scale=round(rng.uniform(0.90, 1.15), 4),
        housing_height_scale=round(rng.uniform(0.90, 1.10), 4),
        panel_rib_spacing_scale=round(rng.uniform(0.90, 1.10), 4),
        panel_travel_scale=round(rng.uniform(0.82, 0.94), 4),
        gated_child_range_scale=round(rng.uniform(0.88, 1.12), 4),
        panel_w=panel_w,
        panel_h=panel_h,
        panel_thickness=panel_thickness,
        name=f"seeded_sluice_{seed}",
    )


def resolve_config(
    config: SluiceGateWithVerticalLiftPanelConfig,
) -> ResolvedSluiceGateWithVerticalLiftPanelConfig:
    rng = random.Random(0x51C1CE ^ (hash(config.name) & 0xFFFFFFFF))
    frame: FrameStyle = config.frame_style or "steel_portal_two_post"
    panel: PanelStyle = config.panel_style or "planar_slab"
    hoist: HoistStyle = config.hoist_style or "direct_handwheel_on_frame"
    gated = _gate_choice(config.gated_child, _gated_compat(hoist), rng)
    material: MaterialStyle = (
        config.material_style if config.material_style in MATERIAL_STYLES else "concrete_steel"
    )

    panel_w = _clamp(config.panel_w, 0.55, 2.40)
    panel_h = _clamp(config.panel_h, 0.85, 2.80)
    panel_thickness = _clamp(config.panel_thickness, 0.035, 0.16)

    pts = _clamp(config.pier_thickness_scale, 0.85, 1.15)
    if frame == "masonry_two_pier":
        pier_thickness = 0.52 * pts
    elif frame == "steel_portal_two_post":
        pier_thickness = 0.16 * pts
    elif frame == "separate_rails_portal":
        pier_thickness = 0.18 * pts
    else:  # cadquery_profiled_block
        pier_thickness = 0.36 * pts

    gcs = _clamp(config.guide_capture_scale, 0.85, 1.25)
    guide_capture = _clamp(0.085 * gcs + 0.5 * panel_thickness, 0.06, 0.18)

    pier_spacing = panel_w + 2.0 * guide_capture

    sill_thickness = (
        0.24
        if frame == "masonry_two_pier"
        else 0.18
        if frame == "cadquery_profiled_block"
        else 0.16
    )
    sill_top_z = sill_thickness
    lintel_thickness = 0.18 if frame == "masonry_two_pier" else 0.14

    pts_t = _clamp(config.panel_travel_scale, 0.80, 0.95)
    panel_travel = _clamp(panel_h * pts_t, 0.15, 2.30)
    panel_top_yoke_size = max(0.05, min(0.14, panel_w * 0.10))
    # frame_height must clear the yoke top when the panel is fully lifted:
    # yoke top world z = sill_top + panel_travel + panel_h + yoke*0.85 + 0.03
    # crossbeam bottom = frame_height - lintel - 0.10
    # Require yoke_top + 0.04 < crossbeam_bottom → frame_height ≥ ...
    yoke_top_at_open = panel_travel + panel_h + panel_top_yoke_size * 0.9 + 0.04
    frame_height = sill_top_z + yoke_top_at_open + 0.18 + lintel_thickness
    panel_rib_count = 0 if panel == "planar_slab" else (3 if panel_h < 1.6 else 4)
    panel_edge_bar_thickness = max(0.045, 0.6 * guide_capture)

    wrs = _clamp(config.wheel_radius_scale, 0.85, 1.20)
    if hoist == "direct_handwheel_on_frame":
        wheel_radius = _clamp(0.16 * wrs, 0.10, 0.22)
    elif hoist == "gearbox_handwheel_via_housing":
        wheel_radius = _clamp(0.22 * wrs, 0.14, 0.30)
    elif hoist == "cadquery_handwheel_via_housing":
        wheel_radius = _clamp(0.25 * wrs, 0.16, 0.32)
    else:  # large_crank_wheel_direct
        wheel_radius = _clamp(0.34 * wrs, 0.26, 0.40)

    if hoist == "large_crank_wheel_direct":
        wheel_axis = (1.0, 0.0, 0.0)
    else:
        wheel_axis = (0.0, 1.0, 0.0)

    has_housing = hoist in HOUSING_HOISTS
    hhs = _clamp(config.housing_height_scale, 0.85, 1.15)
    if has_housing:
        # Housing must be tall enough that the wheel hub sits above the
        # gearbox top, with rim_bottom (sz - wheel_radius) above the
        # gearbox top — and wide enough that the wheel support post
        # (placed at sx + 0.02) lies inside the housing X footprint.
        # sx = gearbox_half_w + wheel_radius + 0.08 = housing_w*0.275 + wr + 0.08.
        # We need housing_w/2 > sx + 0.10 (post half-width + buffer):
        #   housing_w/2 > housing_w*0.275 + wr + 0.18
        #   0.225 * housing_w > wr + 0.18
        #   housing_w > (wr + 0.18) / 0.225  ≈  4.44 * wr + 0.80
        housing_h = _clamp(wheel_radius * 1.4 + 0.30 * hhs, 0.32, 0.78)
        min_w_for_wheel = 4.5 * wheel_radius + 0.85
        housing_w = max(pier_spacing * 0.55, min_w_for_wheel, 0.55)
        housing_d = 0.34
    else:
        housing_h = 0.0
        housing_w = 0.0
        housing_d = 0.0

    has_gated_child = gated != "none"
    gcs_r = _clamp(config.gated_child_range_scale, 0.85, 1.15)
    if gated == "locking_pawl_revolute":
        gated_axis = (0.0, 1.0, 0.0)
        lo, hi = -0.55 * gcs_r, 0.45 * gcs_r
    elif gated == "latch_arm_revolute":
        gated_axis = (0.0, 1.0, 0.0)
        lo, hi = -0.20 * gcs_r, 0.65 * gcs_r
    elif gated == "inspection_door_revolute":
        gated_axis = (0.0, 0.0, 1.0)
        lo, hi = 0.0, 1.25 * gcs_r
    elif gated == "gearbox_cover_top_flap":
        gated_axis = (0.0, 1.0, 0.0)
        lo, hi = 0.0, 1.05 * gcs_r
    else:
        gated_axis = (0.0, 1.0, 0.0)
        lo, hi = 0.0, 0.0

    return ResolvedSluiceGateWithVerticalLiftPanelConfig(
        frame_style=frame,
        panel_style=panel,
        hoist_style=hoist,
        gated_child=gated,
        material_style=material,
        panel_w=panel_w,
        panel_h=panel_h,
        panel_thickness=panel_thickness,
        panel_travel=panel_travel,
        pier_thickness=pier_thickness,
        pier_spacing=pier_spacing,
        guide_capture=guide_capture,
        sill_thickness=sill_thickness,
        sill_top_z=sill_top_z,
        frame_height=frame_height,
        lintel_thickness=lintel_thickness,
        panel_top_yoke_size=panel_top_yoke_size,
        has_housing=has_housing,
        housing_w=housing_w,
        housing_d=housing_d,
        housing_h=housing_h,
        wheel_radius=wheel_radius,
        wheel_axis=wheel_axis,
        has_gated_child=has_gated_child,
        gated_axis=gated_axis,
        gated_range_lower=lo,
        gated_range_upper=hi,
        panel_rib_count=panel_rib_count,
        panel_edge_bar_thickness=panel_edge_bar_thickness,
        palette=PALETTES[material],
        name=config.name or "sluice_gate_with_vertical_lift_panel",
    )


def with_overrides(
    config: SluiceGateWithVerticalLiftPanelConfig, **kwargs
) -> SluiceGateWithVerticalLiftPanelConfig:
    return replace(config, **kwargs)


# --------------------------------------------------------------------------
# Small helpers
# --------------------------------------------------------------------------


def _mat(model: ArticulatedObject, r: ResolvedSluiceGateWithVerticalLiftPanelConfig, key: str):
    return model.material(f"sluice_{r.material_style}_{key}", rgba=r.palette[key])


def _box(part, size, xyz, material, name, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(Box(size), origin=Origin(xyz=xyz, rpy=rpy), material=material, name=name, material_class_id="metal.generic_plain")


def _cyl(part, radius, length, xyz, material, name, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=Origin(xyz=xyz, rpy=rpy),
        material=material,
        name=name, material_class_id="metal.steel_bare",
    )


def _rrect_panel_mesh(name: str, w: float, h: float, t: float, *, corner: float = 0.04):
    """Rounded rectangle (in X-Y) extruded along Z into a slab of thickness t."""
    cr = max(0.005, min(corner, min(w, h) * 0.20))
    return mesh_from_geometry(
        ExtrudeGeometry(rounded_rect_profile(w, h, cr), t, center=True),
        name,
    )


def _ring_mesh(name: str, r_out: float, r_in: float, thickness: float, *, segments: int = 32):
    """Annular ring via section_loft — used for cadquery_handwheel torus rim."""

    def loop(z):
        pts = []
        for i in range(segments + 1):
            a = 2.0 * math.pi * i / segments
            pts.append((r_out * math.cos(a), r_out * math.sin(a), z))
        for i in range(segments, -1, -1):
            a = 2.0 * math.pi * i / segments
            pts.append((r_in * math.cos(a), r_in * math.sin(a), z))
        return pts

    return mesh_from_geometry(
        section_loft([loop(-thickness * 0.5), loop(thickness * 0.5)]),
        name,
    )


# --------------------------------------------------------------------------
# Slot 1 — frame factories (always emit the `frame` root part).
# --------------------------------------------------------------------------


def _emit_sill_and_lintel(frame, r, mats, *, frame_material) -> None:
    full_w = r.pier_spacing + 2.0 * r.pier_thickness
    # Sill (closed-pose panel-bottom seat).
    _box(
        frame,
        (full_w, 0.42, r.sill_thickness),
        (0.0, 0.0, r.sill_top_z * 0.5),
        frame_material,
        "sill",
    )
    # Raised seal ridge centered just below sill_top_z so panel.bottom_seal
    # (which sits at z=0..0.05 in panel-local frame; PRISMATIC origin at
    # sill_top_z so seal sits at world z=sill_top_z..sill_top_z+0.05 closed).
    # Place ridge top at sill_top_z so panel seal sits on top of it.
    _box(
        frame,
        (r.pier_spacing, 0.18, 0.04),
        (0.0, 0.0, r.sill_top_z - 0.02),
        mats["dark_steel"],
        "seal_ridge",
    )
    # Lintel / top_cap.
    _box(
        frame,
        (full_w, 0.36, r.lintel_thickness),
        (0.0, 0.0, r.frame_height - r.lintel_thickness * 0.5),
        frame_material,
        "lintel",
    )
    # Top crossbeam (hoist seat) between piers, just below the lintel.
    _box(
        frame,
        (r.pier_spacing + 2.0 * r.pier_thickness * 0.5, 0.24, 0.10),
        (0.0, 0.0, r.frame_height - r.lintel_thickness - 0.05),
        mats["steel"],
        "top_crossbeam",
    )


def _emit_baked_guides(frame, r, mats) -> None:
    """Guide channels baked as `frame` visuals, sitting between panel edge
    and pier inner face (X span = guide_capture). They embed lightly into
    the pier and capture the panel edge_bar."""
    pier_inner = r.pier_spacing * 0.5
    panel_half = r.panel_w * 0.5
    chan_w = max(0.04, pier_inner - panel_half)
    chan_h = r.panel_h + r.panel_travel + 0.10
    for sx, lx in ((-1, "left"), (1, "right")):
        x_center = sx * (panel_half + chan_w * 0.5)
        _box(
            frame,
            (chan_w, 0.18, chan_h),
            (x_center, 0.0, r.sill_top_z + chan_h * 0.5),
            mats["dark_steel"],
            f"guide_channel_{lx}",
        )
        _box(
            frame,
            (chan_w * 0.55, 0.05, chan_h),
            (x_center, 0.10, r.sill_top_z + chan_h * 0.5),
            mats["dark_steel"],
            f"guide_retainer_{lx}",
        )


def _build_masonry_two_pier(model, r, mats):
    frame = model.part("frame")
    pier_w = r.pier_thickness
    pier_h = r.frame_height - r.sill_top_z - r.lintel_thickness * 0.5
    pier_cz = r.sill_top_z + pier_h * 0.5
    pier_inner = r.pier_spacing * 0.5
    for sx, lx in ((-1, "left"), (1, "right")):
        x = sx * (pier_inner + pier_w * 0.5)
        _box(frame, (pier_w, 0.42, pier_h), (x, 0.0, pier_cz), mats["concrete"], f"pier_{lx}")
        for i in range(3):
            z = r.sill_top_z + 0.18 + i * (pier_h - 0.36) / 2.0
            _cyl(
                frame,
                0.012,
                0.05,
                (x, 0.21, z),
                mats["dark_steel"],
                f"pier_{lx}_bolt_{i}",
                (math.pi * 0.5, 0.0, 0.0),
            )
    _emit_sill_and_lintel(frame, r, mats, frame_material=mats["concrete"])
    _emit_baked_guides(frame, r, mats)
    return frame


def _build_steel_portal_two_post(model, r, mats):
    frame = model.part("frame")
    post_w = r.pier_thickness
    post_h = r.frame_height - r.sill_top_z - r.lintel_thickness * 0.5
    post_cz = r.sill_top_z + post_h * 0.5
    pier_inner = r.pier_spacing * 0.5
    for sx, lx in ((-1, "left"), (1, "right")):
        x = sx * (pier_inner + post_w * 0.5)
        _box(frame, (post_w, 0.22, post_h), (x, 0.0, post_cz), mats["steel"], f"post_{lx}")
        _box(
            frame,
            (0.05, 0.05, post_h * 0.32),
            (x + sx * 0.04, 0.13, r.sill_top_z + post_h * 0.18),
            mats["dark_steel"],
            f"brace_{lx}",
        )
    _emit_sill_and_lintel(frame, r, mats, frame_material=mats["steel"])
    _emit_baked_guides(frame, r, mats)
    return frame


def _build_separate_rails_portal(model, r, mats):
    """Like steel_portal but the guide channels are independent FIXED parts."""
    frame = model.part("frame")
    post_w = r.pier_thickness
    post_h = r.frame_height - r.sill_top_z - r.lintel_thickness * 0.5
    post_cz = r.sill_top_z + post_h * 0.5
    pier_inner = r.pier_spacing * 0.5
    for sx, lx in ((-1, "left"), (1, "right")):
        x = sx * (pier_inner + post_w * 0.5)
        _box(frame, (post_w, 0.22, post_h), (x, 0.0, post_cz), mats["steel"], f"post_{lx}")
    _emit_sill_and_lintel(frame, r, mats, frame_material=mats["steel"])
    # No baked guides; rails are separate parts (see _build_separate_rails).
    return frame


def _build_separate_rails(model, r, mats, frame):
    """Two FIXED guide_rail parts. Joint origin sits on the post inner face
    (real frame geometry); rail visuals extend inward toward the panel edge
    and lightly embed into the post for visible support."""
    pier_inner = r.pier_spacing * 0.5
    panel_half = r.panel_w * 0.5
    rail_w = max(0.04, pier_inner - panel_half)
    chan_h = r.panel_h + r.panel_travel + 0.10
    for sx, lx in ((-1, "left"), (1, "right")):
        rail = model.part(f"guide_rail_{lx}")
        # Joint origin on the post inner face (frame visual: post_{lx}).
        x_world = sx * pier_inner
        z_world = r.sill_top_z + chan_h * 0.5
        # Rail body sits in the channel just inward of the joint origin
        # (toward panel center): in part-local X, that's the -sx direction.
        inner_offset = -sx * rail_w * 0.5
        _box(rail, (rail_w, 0.18, chan_h), (inner_offset, 0.0, 0.0), mats["dark_steel"], "rail_web")
        _box(
            rail,
            (rail_w * 0.55, 0.05, chan_h),
            (inner_offset, 0.10, 0.0),
            mats["dark_steel"],
            "rail_retainer",
        )
        # Top/bottom flanges anchored onto the post inner face (origin side).
        _box(
            rail,
            (rail_w * 1.4, 0.18, 0.08),
            (sx * 0.02, -0.04, chan_h * 0.5 - 0.04),
            mats["steel"],
            "rail_top_flange",
        )
        _box(
            rail,
            (rail_w * 1.4, 0.18, 0.08),
            (sx * 0.02, -0.04, -chan_h * 0.5 + 0.04),
            mats["steel"],
            "rail_bottom_flange",
        )
        model.articulation(
            f"frame_to_guide_rail_{lx}",
            ArticulationType.FIXED,
            parent=frame,
            child=rail,
            origin=Origin(xyz=(x_world, 0.0, z_world)),
        )


def _build_cadquery_profiled_block(model, r, mats):
    """Profiled-block frame: piers and lintel use rounded-rect ExtrudeGeometry
    meshes (preserving the cq sample's profiled-headwall character) without
    blocking the channel where the lift_panel slides."""
    frame = model.part("frame")
    pier_w = r.pier_thickness
    pier_h = r.frame_height - r.sill_top_z - r.lintel_thickness * 0.5
    pier_cz = r.sill_top_z + pier_h * 0.5
    pier_inner = r.pier_spacing * 0.5
    # Each pier rendered as a profiled mesh slab (X-Z rounded rect extruded
    # in Y by pier depth).
    for sx, lx in ((-1, "left"), (1, "right")):
        x = sx * (pier_inner + pier_w * 0.5)
        frame.visual(
            _rrect_panel_mesh(f"pier_block_{lx}", pier_w, pier_h, 0.42, corner=0.08),
            origin=Origin(xyz=(x, 0.0, pier_cz), rpy=(math.pi * 0.5, 0.0, 0.0)),
            material=mats["concrete"],
            name=f"pier_block_{lx}", material_class_id="concrete.formed_patterned",
        )
        # Dark accent on pier inner face.
        _box(
            frame,
            (pier_w * 0.4, 0.30, pier_h * 0.94),
            (x - sx * pier_w * 0.30, -0.04, pier_cz),
            mats["dark_steel"],
            f"pier_face_{lx}",
        )
    _emit_sill_and_lintel(frame, r, mats, frame_material=mats["concrete"])
    _emit_baked_guides(frame, r, mats)
    return frame


FRAME_FACTORIES = {
    "masonry_two_pier": _build_masonry_two_pier,
    "steel_portal_two_post": _build_steel_portal_two_post,
    "separate_rails_portal": _build_separate_rails_portal,
    "cadquery_profiled_block": _build_cadquery_profiled_block,
}


# --------------------------------------------------------------------------
# Slot 2 — lift_panel factories.
# Panel-local frame: origin at (0,0,0) = panel center-bottom (the bottom_seal
# sits centered around z=0). The PRISMATIC joint origin is on the sill top
# (sill_top_z) so closed-pose panel bottom rests on the seal ridge with a
# tiny embed.
# --------------------------------------------------------------------------


def _emit_panel_edge_bars(panel, r, mats) -> None:
    eb = r.panel_edge_bar_thickness
    h = r.panel_h
    for sx, lx in ((-1, "left"), (1, "right")):
        x = sx * (r.panel_w * 0.5 + eb * 0.5 - 0.006)  # slight embed into main plate
        _box(panel, (eb, 0.08, h), (x, 0.0, h * 0.5), mats["dark_steel"], f"edge_bar_{lx}")


def _emit_panel_yoke(panel, r, mats) -> None:
    yk = r.panel_top_yoke_size
    # Yoke base embeds 1 cm into main_plate top for visible support contact.
    _box(
        panel,
        (yk, 0.10, yk * 0.7 + 0.02),
        (0.0, 0.0, r.panel_h + yk * 0.35 - 0.01),
        mats["dark_steel"],
        "yoke",
    )
    _box(
        panel,
        (yk * 1.6, 0.08, 0.06),
        (0.0, 0.015, r.panel_h + yk * 0.75),
        mats["dark_steel"],
        "yoke_cap",
    )


def _emit_panel_seal(panel, r, mats) -> None:
    _box(panel, (r.panel_w * 0.98, 0.10, 0.04), (0.0, 0.0, 0.020), mats["rubber"], "bottom_seal")


def _build_planar_slab(model, r, mats):
    panel = model.part("lift_panel")
    _box(
        panel,
        (r.panel_w, r.panel_thickness, r.panel_h),
        (0.0, 0.0, r.panel_h * 0.5),
        mats["plate"],
        "main_plate",
    )
    _emit_panel_seal(panel, r, mats)
    _emit_panel_edge_bars(panel, r, mats)
    _emit_panel_yoke(panel, r, mats)
    return panel


def _build_ribbed_stiffened_plate(model, r, mats):
    panel = model.part("lift_panel")
    _box(
        panel,
        (r.panel_w, r.panel_thickness, r.panel_h),
        (0.0, 0.0, r.panel_h * 0.5),
        mats["plate"],
        "main_plate",
    )
    n = r.panel_rib_count
    if n > 0:
        for i in range(n):
            z = r.panel_h * (i + 1) / (n + 1)
            _box(
                panel,
                (r.panel_w * 0.92, 0.08, 0.06),
                (0.0, 0.04, z),
                mats["dark_steel"],
                f"rib_h_{i}",
            )
    _box(
        panel,
        (0.06, 0.08, r.panel_h * 0.86),
        (0.0, 0.04, r.panel_h * 0.5),
        mats["dark_steel"],
        "rib_v_center",
    )
    _emit_panel_seal(panel, r, mats)
    _emit_panel_edge_bars(panel, r, mats)
    _emit_panel_yoke(panel, r, mats)
    return panel


def _build_cadquery_profiled_panel(model, r, mats):
    panel = model.part("lift_panel")
    # Profile (panel_w × panel_h) extruded by panel_thickness in Z, then
    # rotated 90° about X so the thickness axis becomes Y in panel frame.
    panel.visual(
        _rrect_panel_mesh("profiled_main", r.panel_w, r.panel_h, r.panel_thickness, corner=0.05),
        origin=Origin(xyz=(0.0, 0.0, r.panel_h * 0.5), rpy=(math.pi * 0.5, 0.0, 0.0)),
        material=mats["plate"],
        name="main_plate", material_class_id=("metal.paint_coated" if r.material_style in {"concrete_steel", "painted_blue", "warning_yellow"} else "metal.cast_iron_bare"),
    )
    for i in range(3):
        z = r.panel_h * (i + 1) / 4.0
        # Reinforcement band sits on +y face of panel (mostly embedded by half).
        _box(
            panel,
            (r.panel_w * 0.96, 0.05, 0.04),
            (0.0, r.panel_thickness * 0.5 - 0.010, z),
            mats["dark_steel"],
            f"band_{i}",
        )
    _emit_panel_seal(panel, r, mats)
    _emit_panel_edge_bars(panel, r, mats)
    _emit_panel_yoke(panel, r, mats)
    return panel


PANEL_FACTORIES = {
    "planar_slab": _build_planar_slab,
    "ribbed_stiffened_plate": _build_ribbed_stiffened_plate,
    "cadquery_profiled_panel": _build_cadquery_profiled_panel,
}


# --------------------------------------------------------------------------
# Slot 3 — hoist factories.
# --------------------------------------------------------------------------


# Local-frame anchor inside operator_housing where the handwheel shaft mounts.
# Placed BEYOND the gearbox_body's +x edge so the wheel rim doesn't intersect it.
def _housing_shaft_anchor(r) -> tuple[float, float, float]:
    """Hub center in housing-local frame (origin = lintel top, z grows up).
    Placed so:
      * sx > gearbox_half_w + wheel_radius + buf → rim never enters gearbox X
      * sz in upper-mid of housing (clear of crossbeam, near gearbox top)
    """
    gearbox_half_w = r.housing_w * 0.275
    sx = gearbox_half_w + r.wheel_radius + 0.08
    sz = r.housing_h * 0.70
    return (sx, 0.04, sz)


def _build_operator_housing(model, r, mats, frame):
    """Operator_housing built around its own origin sitting on the lintel top.
    The FIXED joint origin is placed AT the lintel top in frame coordinates
    so the joint origin sits on real frame geometry."""
    housing = model.part("operator_housing")
    hw, hd, hh = r.housing_w, r.housing_d, r.housing_h
    # Crossbeam: bottom at z=0 (lintel top), extends upward 0.10.
    _box(housing, (hw, hd, 0.10), (0.0, 0.0, 0.05), mats["steel"], "crossbeam")
    # Gearbox body: above crossbeam, occupies most of housing height.
    _box(
        housing,
        (hw * 0.55, hd * 0.82, hh * 0.62),
        (0.0, 0.04, 0.10 + hh * 0.31),
        mats["dark_steel"],
        "gearbox_body",
    )
    # Bonnet / decorative cover at the front-lower section.
    _box(
        housing,
        (0.22, 0.16, 0.30),
        (0.0, -hd * 0.30, 0.10 + hh * 0.20),
        mats["dark_steel"],
        "bonnet",
    )
    # Wheel support: vertical post from crossbeam top (z=0.10) up to shaft
    # height, offset in +Y so it sits behind the rim plane (rim center at
    # sy, thickness ~24mm; post at sy+0.09 with depth 0.06 keeps a clean gap).
    sx, sy, sz = _housing_shaft_anchor(r)
    post_z0 = 0.05  # embed into crossbeam top (crossbeam spans z=0..0.10)
    post_z1 = sz + 0.04
    post_cx = sx + 0.02
    post_cy = sy + 0.09
    _box(
        housing,
        (0.10, 0.06, post_z1 - post_z0),
        (post_cx, post_cy, (post_z0 + post_z1) * 0.5),
        mats["dark_steel"],
        "wheel_support_post",
    )
    # shaft_boss bridges from the post forward through the rim plane to the
    # hub origin (cylinder along Y).
    boss_len = 0.18
    _cyl(
        housing,
        0.045,
        boss_len,
        (sx, post_cy - boss_len * 0.5 + 0.02, sz),
        mats["steel"],
        "shaft_boss",
        (math.pi * 0.5, 0.0, 0.0),
    )
    # Pawl bracket on the opposite side from the wheel (used by gated child
    # when present). Bracket sits just outboard of the gearbox -X face; the
    # pawl_bridge connector embeds back into the gearbox to keep the bracket
    # part of the housing's single connected island.
    bracket_cz = 0.10 + hh * 0.40
    bracket_cx = -hw * 0.32
    _box(
        housing,
        (0.10, 0.10, 0.22),
        (bracket_cx, 0.06, bracket_cz),
        mats["dark_steel"],
        "pawl_bracket",
    )
    # Bridge spans from gearbox edge (-hw*0.275 + small embed) out to the
    # bracket center — gives bracket a visible support path.
    bridge_x0 = -hw * 0.20
    bridge_x1 = bracket_cx + 0.02
    _box(
        housing,
        (max(0.18, bridge_x0 - bridge_x1), 0.14, 0.06),
        ((bridge_x0 + bridge_x1) * 0.5, 0.06, bracket_cz - 0.06),
        mats["dark_steel"],
        "pawl_bridge",
    )
    # FIXED to frame: housing bottom origin sits ON the lintel top so the
    # joint origin (in frame frame) lies on real frame geometry.
    model.articulation(
        "frame_to_operator_housing",
        ArticulationType.FIXED,
        parent=frame,
        child=housing,
        origin=Origin(xyz=(0.0, 0.0, r.frame_height)),
    )
    return housing


def _make_handwheel_part(model, name, r, mats, *, with_torus_rim: bool, spokes: int):
    """Handwheel/crank built around its own origin (hub center).
    Rim sits in the X-Z plane (axis along Y) by default; rotation to match the
    actual wheel_axis is handled by the joint origin's rpy when needed."""
    wheel = model.part(name)
    rim_r = r.wheel_radius
    tube_r = max(0.012, rim_r * 0.05)
    # Hub at origin.
    _cyl(
        wheel,
        max(0.030, rim_r * 0.18),
        0.08,
        (0.0, 0.0, 0.0),
        mats["steel"],
        "hub",
        (math.pi * 0.5, 0.0, 0.0),
    )
    # Shaft extends along Y (axis).
    _cyl(wheel, 0.018, 0.18, (0.0, -0.10, 0.0), mats["steel"], "shaft", (math.pi * 0.5, 0.0, 0.0))
    # Rim: always box-segmented (24 segs for torus-style, 18 for primitive).
    seg_n = 24 if with_torus_rim else 18
    seg_len = 2.0 * math.pi * rim_r / seg_n
    seg_thickness = tube_r * (2.4 if with_torus_rim else 2.0)
    for i in range(seg_n):
        a = 2.0 * math.pi * i / seg_n
        _box(
            wheel,
            (seg_thickness, seg_thickness, seg_len * 1.05),
            (rim_r * math.cos(a), 0.0, rim_r * math.sin(a)),
            mats["accent"],
            f"rim_seg_{i}",
            (0.0, -a, 0.0),
        )
    # Spokes (in X-Z plane).
    for i in range(spokes):
        a = i * math.pi / spokes
        _box(
            wheel,
            (rim_r * 2.0, 0.020, 0.030),
            (0.0, 0.0, 0.0),
            mats["steel"],
            f"spoke_{i}",
            (0.0, a, 0.0),
        )
    # Grip knob on the rim.
    _box(
        wheel,
        (0.035, 0.03, 0.035),
        (rim_r * 0.70, 0.005, rim_r * 0.70),
        mats["dark_steel"],
        "grip_stem",
    )
    return wheel


def _build_hoist_gearbox_handwheel_via_housing(model, r, mats, frame):
    housing = _build_operator_housing(model, r, mats, frame)
    wheel = _make_handwheel_part(model, "handwheel", r, mats, with_torus_rim=False, spokes=3)
    sx, sy, sz = _housing_shaft_anchor(r)
    model.articulation(
        "handwheel_spin",
        ArticulationType.CONTINUOUS,
        parent=housing,
        child=wheel,
        origin=Origin(xyz=(sx, sy, sz)),
        axis=r.wheel_axis,
        motion_limits=MotionLimits(effort=50.0, velocity=8.0),
    )
    return housing, wheel


def _build_hoist_cadquery_handwheel_via_housing(model, r, mats, frame):
    housing = _build_operator_housing(model, r, mats, frame)
    wheel = _make_handwheel_part(model, "handwheel", r, mats, with_torus_rim=True, spokes=4)
    sx, sy, sz = _housing_shaft_anchor(r)
    model.articulation(
        "handwheel_spin",
        ArticulationType.CONTINUOUS,
        parent=housing,
        child=wheel,
        origin=Origin(xyz=(sx, sy, sz)),
        axis=r.wheel_axis,
        motion_limits=MotionLimits(effort=60.0, velocity=6.0),
    )
    return housing, wheel


def _build_hoist_large_crank_wheel_direct(model, r, mats, frame):
    """Large crank wheel directly on frame. Pedestal lifts the hub above the
    lintel by at least wheel_radius so the rim doesn't cross the lintel."""
    hub_z = r.frame_height + r.wheel_radius + 0.10
    pedestal_h = hub_z - r.frame_height
    _box(
        frame,
        (0.36, 0.24, pedestal_h),
        (0.0, 0.0, r.frame_height + pedestal_h * 0.5),
        mats["dark_steel"],
        "crank_bearing_block",
    )
    _cyl(
        frame,
        0.05,
        0.12,
        (0.0, 0.0, hub_z),
        mats["steel"],
        "crank_shaft_boss",
        (math.pi * 0.5, 0.0, 0.0),
    )
    wheel = _make_handwheel_part(model, "crank_wheel", r, mats, with_torus_rim=True, spokes=4)
    model.articulation(
        "handwheel_spin",
        ArticulationType.CONTINUOUS,
        parent=frame,
        child=wheel,
        origin=Origin(xyz=(0.0, 0.0, hub_z)),
        axis=r.wheel_axis,
        motion_limits=MotionLimits(effort=80.0, velocity=5.0),
    )
    return None, wheel


def _build_hoist_direct_handwheel_on_frame(model, r, mats, frame):
    hub_z = r.frame_height + r.wheel_radius + 0.06
    pedestal_h = hub_z - r.frame_height
    _box(
        frame,
        (0.26, 0.20, pedestal_h),
        (0.0, 0.0, r.frame_height + pedestal_h * 0.5),
        mats["dark_steel"],
        "handwheel_pedestal",
    )
    _cyl(
        frame,
        0.05,
        0.10,
        (0.0, 0.04, hub_z),
        mats["steel"],
        "handwheel_boss",
        (math.pi * 0.5, 0.0, 0.0),
    )
    wheel = _make_handwheel_part(model, "handwheel", r, mats, with_torus_rim=False, spokes=3)
    model.articulation(
        "handwheel_spin",
        ArticulationType.CONTINUOUS,
        parent=frame,
        child=wheel,
        origin=Origin(xyz=(0.0, 0.04, hub_z)),
        axis=r.wheel_axis,
        motion_limits=MotionLimits(effort=45.0, velocity=6.0),
    )
    return None, wheel


HOIST_FACTORIES = {
    "gearbox_handwheel_via_housing": _build_hoist_gearbox_handwheel_via_housing,
    "cadquery_handwheel_via_housing": _build_hoist_cadquery_handwheel_via_housing,
    "large_crank_wheel_direct": _build_hoist_large_crank_wheel_direct,
    "direct_handwheel_on_frame": _build_hoist_direct_handwheel_on_frame,
}


# --------------------------------------------------------------------------
# Slot 4 — gated REVOLUTE child.
# Each factory builds its child part around its own origin (the joint origin
# coincides with that local (0,0,0)) and emits the REVOLUTE joint to either
# operator_housing (when present) or frame.
# --------------------------------------------------------------------------


def _build_locking_pawl(model, r, mats, parent_part, *, on_housing: bool):
    pawl = model.part("locking_pawl")
    # Pivot barrel at part origin.
    _cyl(
        pawl, 0.014, 0.05, (0.0, 0.0, 0.0), mats["steel"], "pivot_barrel", (math.pi * 0.5, 0.0, 0.0)
    )
    _box(pawl, (0.04, 0.022, 0.06), (-0.012, 0.0, -0.024), mats["dark_steel"], "pawl_root")
    _box(
        pawl,
        (0.025, 0.022, 0.16),
        (-0.020, 0.0, -0.085),
        mats["dark_steel"],
        "pawl_arm",
        (0.0, -0.18, 0.0),
    )
    _box(
        pawl,
        (0.032, 0.028, 0.034),
        (-0.034, 0.0, -0.158),
        mats["dark_steel"],
        "pawl_tooth",
        (0.0, -0.18, 0.0),
    )
    _box(
        pawl,
        (0.020, 0.020, 0.08),
        (0.026, 0.0, 0.042),
        mats["dark_steel"],
        "pawl_handle",
        (0.0, 0.45, 0.0),
    )
    if on_housing:
        origin_xyz = (-r.housing_w * 0.32, 0.06, 0.10 + r.housing_h * 0.40)
    else:
        # Pedestal extends from the lintel top up to above the joint origin
        # so it's both connected to the frame body and supports the pawl.
        _box(
            parent_part,
            (0.14, 0.10, 0.36),
            (-r.pier_spacing * 0.32, 0.10, r.frame_height + 0.18),
            mats["dark_steel"],
            "pawl_pedestal",
        )
        origin_xyz = (-r.pier_spacing * 0.32, 0.10, r.frame_height + 0.22)
    model.articulation(
        "pawl_pivot",
        ArticulationType.REVOLUTE,
        parent=parent_part,
        child=pawl,
        origin=Origin(xyz=origin_xyz),
        axis=r.gated_axis,
        motion_limits=MotionLimits(
            effort=12.0,
            velocity=2.5,
            lower=r.gated_range_lower,
            upper=r.gated_range_upper,
        ),
    )
    return pawl


def _build_latch_arm(model, r, mats, parent_part, *, on_housing: bool):
    latch = model.part("latch_arm")
    _cyl(
        latch,
        0.014,
        0.05,
        (0.0, 0.0, 0.0),
        mats["steel"],
        "pivot_barrel",
        (math.pi * 0.5, 0.0, 0.0),
    )
    _box(latch, (0.028, 0.022, 0.12), (0.0, 0.0, -0.06), mats["dark_steel"], "arm")
    _box(latch, (0.06, 0.03, 0.04), (-0.018, 0.0, -0.12), mats["dark_steel"], "hook")
    # Counterweight protrudes well in -X direction (outboard of the housing
    # gearbox body, on the bracket side) at hinge height.
    _cyl(
        latch,
        0.022,
        0.05,
        (-0.090, 0.0, 0.025),
        mats["dark_steel"],
        "counterweight",
        (math.pi * 0.5, 0.0, 0.0),
    )
    # Bridge box visual joins the pivot to the counterweight along -X so
    # the counterweight is connected to the pivot_barrel within latch_arm.
    _box(
        latch, (0.090, 0.022, 0.022), (-0.045, 0.0, 0.025), mats["dark_steel"], "counterweight_arm"
    )
    if on_housing:
        # Latch hinge sits INSIDE the pawl_bracket — joint origin lies on
        # real housing geometry. Counterweight protrudes in -X (away from
        # gearbox center) so it stays outboard of the gearbox body.
        origin_xyz = (-r.housing_w * 0.32, 0.06, 0.10 + r.housing_h * 0.40)
    else:
        _box(
            parent_part,
            (0.12, 0.10, 0.34),
            (-r.pier_spacing * 0.32, 0.10, r.frame_height + 0.17),
            mats["dark_steel"],
            "latch_pedestal",
        )
        origin_xyz = (-r.pier_spacing * 0.32, 0.10, r.frame_height + 0.22)
    model.articulation(
        "latch_pivot",
        ArticulationType.REVOLUTE,
        parent=parent_part,
        child=latch,
        origin=Origin(xyz=origin_xyz),
        axis=r.gated_axis,
        motion_limits=MotionLimits(
            effort=10.0,
            velocity=2.0,
            lower=r.gated_range_lower,
            upper=r.gated_range_upper,
        ),
    )
    return latch


def _build_inspection_door(model, r, mats, parent_part, *, on_housing: bool):
    door = model.part("inspection_door")
    door_w = 0.24 if on_housing else 0.28
    door_h = 0.22 if on_housing else 0.30
    door_t = 0.012
    _cyl(door, 0.018, door_h * 0.9, (0.0, 0.0, 0.0), mats["dark_steel"], "hinge_barrel")
    # Door panel sits in front of the hinge (+Y). Small offset keeps the
    # panel touching the hinge_barrel (visible connectivity within the
    # door part); the panel partially embeds into the gearbox front face
    # — allowed via element-scoped allow_overlap.
    panel_dy = 0.014
    _box(door, (door_w, door_t, door_h), (door_w * 0.5, panel_dy, 0.0), mats["plate"], "door_panel")
    # Short stem bridging the door panel to the protruding handle so the
    # handle is geometrically connected to the panel within the part.
    _box(
        door,
        (0.020, 0.040, 0.020),
        (door_w * 0.85, panel_dy + 0.025, 0.0),
        mats["dark_steel"],
        "handle_stem",
    )
    _box(
        door,
        (0.04, 0.05, 0.03),
        (door_w * 0.85, panel_dy + 0.045, 0.0),
        mats["dark_steel"],
        "door_handle",
    )
    if on_housing:
        # Hinge embeds into the gearbox front face (both in -X to be on the
        # bracket side of gearbox, and in -Y by 25 mm so the joint origin
        # is unambiguously inside housing geometry).
        gearbox_edge_x = -r.housing_w * 0.275
        front_y = 0.04 + r.housing_d * 0.41 - 0.025
        origin_xyz = (gearbox_edge_x + 0.010, front_y, 0.10 + r.housing_h * 0.40)
    else:
        # Door above lintel; mount extends down through the lintel for
        # visible support (small embed allowed via element-scoped overlap).
        door_center_z = r.frame_height + door_h * 0.5 + 0.03
        mount_h = door_h * 1.3  # taller than door so bottom embeds into lintel
        _box(
            parent_part,
            (0.12, 0.10, mount_h),
            (r.pier_spacing * 0.32, 0.14, door_center_z - 0.04),
            mats["dark_steel"],
            "door_mount",
        )
        origin_xyz = (r.pier_spacing * 0.32 - 0.04, 0.18, door_center_z)
    model.articulation(
        "door_hinge",
        ArticulationType.REVOLUTE,
        parent=parent_part,
        child=door,
        origin=Origin(xyz=origin_xyz),
        axis=r.gated_axis,
        motion_limits=MotionLimits(
            effort=20.0,
            velocity=2.0,
            lower=r.gated_range_lower,
            upper=r.gated_range_upper,
        ),
    )
    return door


def _build_gearbox_cover_top_flap(model, r, mats, parent_part, *, on_housing: bool):
    cover = model.part("gearbox_cover")
    # Cover sits above gearbox_body top. Hinge axis (0,1,0); cover at rest
    # extends in -x direction (toward pawl_bracket side, NOT over wheel).
    # Cover is positioned slightly ABOVE its hinge so it rests just above the
    # gearbox top surface (not pressing into it).
    flap_w = r.housing_w * 0.30 if on_housing else 0.22
    flap_d = r.housing_d * 0.50 if on_housing else 0.18
    flap_t = 0.012
    # Hinge at part origin; cover_panel center coplanar with hinge so its
    # bottom face dips slightly into gearbox top (allow_overlap registered).
    _cyl(
        cover,
        0.012,
        flap_d,
        (0.0, 0.0, 0.0),
        mats["dark_steel"],
        "hinge_barrel",
        (math.pi * 0.5, 0.0, 0.0),
    )
    _box(cover, (flap_w, flap_d, flap_t), (-flap_w * 0.5, 0.0, 0.0), mats["plate"], "cover_panel")
    _box(
        cover,
        (0.04, 0.05, 0.025),
        (-flap_w * 0.85, 0.0, 0.010),  # embeds into cover_panel for contact
        mats["dark_steel"],
        "cover_handle",
    )
    if on_housing:
        # Gearbox top face in housing-local frame = 0.10 + hh*0.62 (origin at
        # lintel top). Hinge sits a hair above; cover panel rests on top.
        gearbox_top_z = 0.10 + r.housing_h * 0.62
        gearbox_half_w = r.housing_w * 0.275
        origin_xyz = (-gearbox_half_w + 0.005, 0.04, gearbox_top_z + 0.004)
    else:
        origin_xyz = (-r.pier_spacing * 0.30, 0.10, r.frame_height + 0.12)
    model.articulation(
        "cover_hinge",
        ArticulationType.REVOLUTE,
        parent=parent_part,
        child=cover,
        origin=Origin(xyz=origin_xyz),
        axis=r.gated_axis,
        motion_limits=MotionLimits(
            effort=8.0,
            velocity=2.0,
            lower=r.gated_range_lower,
            upper=r.gated_range_upper,
        ),
    )
    return cover


GATED_FACTORIES = {
    "locking_pawl_revolute": _build_locking_pawl,
    "latch_arm_revolute": _build_latch_arm,
    "inspection_door_revolute": _build_inspection_door,
    "gearbox_cover_top_flap": _build_gearbox_cover_top_flap,
}


# --------------------------------------------------------------------------
# Top-level builder
# --------------------------------------------------------------------------


def slot_choices_for_config(config) -> tuple[tuple[str, str], ...]:
    r = (
        config
        if isinstance(config, ResolvedSluiceGateWithVerticalLiftPanelConfig)
        else resolve_config(config)
    )
    return (
        ("frame", r.frame_style),
        ("panel", r.panel_style),
        ("hoist", r.hoist_style),
        ("gated_child", r.gated_child),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


def build_sluice_gate_with_vertical_lift_panel(
    config: SluiceGateWithVerticalLiftPanelConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    cfg = config or SluiceGateWithVerticalLiftPanelConfig()
    r = resolve_config(cfg)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {k: _mat(model, r, k) for k in r.palette}

    # Slot 1 — frame (root).
    frame = FRAME_FACTORIES[r.frame_style](model, r, mats)

    # Optional separate rails (only `separate_rails_portal`).
    if r.frame_style == "separate_rails_portal":
        _build_separate_rails(model, r, mats, frame)

    # Slot 2 — lift_panel (PRISMATIC z).
    panel = PANEL_FACTORIES[r.panel_style](model, r, mats)
    model.articulation(
        "plate_lift",
        ArticulationType.PRISMATIC,
        parent=frame,
        child=panel,
        origin=Origin(xyz=(0.0, 0.0, r.sill_top_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(
            effort=2000.0,
            velocity=0.18,
            lower=0.0,
            upper=r.panel_travel,
        ),
    )

    # Slot 3 — hoist (CONTINUOUS + optional FIXED operator_housing).
    housing, _wheel = HOIST_FACTORIES[r.hoist_style](model, r, mats, frame)

    # Slot 4 — gated child (REVOLUTE).
    if r.has_gated_child:
        on_housing = housing is not None and r.has_housing
        parent_for_gated = housing if on_housing else frame
        GATED_FACTORIES[r.gated_child](model, r, mats, parent_for_gated, on_housing=on_housing)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_sluice_gate_with_vertical_lift_panel(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_sluice_gate_with_vertical_lift_panel(config_from_seed(seed), assets=assets)


# --------------------------------------------------------------------------
# Tests
# --------------------------------------------------------------------------


def _allow(ctx, model, pa, pb, ea, eb, reason):
    try:
        part_a = model.get_part(pa)
        part_b = model.get_part(pb)
    except Exception:
        return
    ctx.allow_overlap(part_a, part_b, elem_a=ea, elem_b=eb, reason=reason)


def _register_intentional_overlaps(ctx, model, r) -> None:
    """Element-scoped allowances: panel-in-guide captured, seal closure,
    hub/shaft on bearing, pawl pivot in bracket."""
    # Panel edge_bars ride inside guide channels (baked or separate).
    if r.frame_style != "separate_rails_portal":
        for lx in ("left", "right"):
            _allow(
                ctx,
                model,
                "frame",
                "lift_panel",
                f"guide_channel_{lx}",
                f"edge_bar_{lx}",
                "panel edge_bar in baked guide channel",
            )
            _allow(
                ctx,
                model,
                "frame",
                "lift_panel",
                f"guide_retainer_{lx}",
                f"edge_bar_{lx}",
                "panel edge_bar held by guide retainer",
            )
    else:
        for lx in ("left", "right"):
            for rail_elem in ("rail_web", "rail_retainer", "rail_top_flange", "rail_bottom_flange"):
                _allow(
                    ctx,
                    model,
                    f"guide_rail_{lx}",
                    "lift_panel",
                    rail_elem,
                    f"edge_bar_{lx}",
                    f"panel edge_bar in separate rail {rail_elem}",
                )
                _allow(
                    ctx,
                    model,
                    "frame",
                    f"guide_rail_{lx}",
                    f"post_{lx}",
                    rail_elem,
                    f"rail {rail_elem} anchored into post",
                )
    # Panel bottom_seal contacts sill seal_ridge.
    _allow(
        ctx,
        model,
        "frame",
        "lift_panel",
        "seal_ridge",
        "bottom_seal",
        "panel seal compresses against sill ridge in closed pose",
    )

    # Hoist hub/shaft engagement.
    wheel_part = "crank_wheel" if r.hoist_style == "large_crank_wheel_direct" else "handwheel"
    spoke_count = (
        4 if r.hoist_style in ("large_crank_wheel_direct", "cadquery_handwheel_via_housing") else 3
    )
    # Rim is always segmented: 24 segs for large/cadquery, 18 for direct.
    has_torus_rim = r.hoist_style in ("large_crank_wheel_direct", "cadquery_handwheel_via_housing")
    rim_seg_n = 24 if has_torus_rim else 18
    rim_elems = [f"rim_seg_{i}" for i in range(rim_seg_n)]
    wheel_elems_through_boss = (
        ["hub", "shaft", "grip_stem"] + [f"spoke_{i}" for i in range(spoke_count)] + rim_elems
    )
    if r.has_housing:
        for elem_a in ("wheel_support_post", "shaft_boss"):
            for elem_b in wheel_elems_through_boss:
                _allow(
                    ctx,
                    model,
                    "operator_housing",
                    wheel_part,
                    elem_a,
                    elem_b,
                    f"handwheel {elem_b} captured at {elem_a}",
                )
        # Housing crossbeam on lintel top (FIXED joint already; mark overlap
        # safe in case the lintel/crossbeam visuals graze).
        _allow(
            ctx,
            model,
            "frame",
            "operator_housing",
            "lintel",
            "crossbeam",
            "housing crossbeam seats on lintel",
        )
        _allow(
            ctx,
            model,
            "frame",
            "operator_housing",
            "top_crossbeam",
            "crossbeam",
            "housing crossbeam seats on frame top crossbeam",
        )
    else:
        if r.hoist_style == "large_crank_wheel_direct":
            anchors = ("crank_bearing_block", "crank_shaft_boss", "top_crossbeam")
        else:
            anchors = ("handwheel_pedestal", "handwheel_boss", "top_crossbeam")
        for elem_a in anchors:
            for elem_b in wheel_elems_through_boss:
                _allow(
                    ctx,
                    model,
                    "frame",
                    wheel_part,
                    elem_a,
                    elem_b,
                    f"{wheel_part} {elem_b} captured at frame {elem_a}",
                )

    # Gated child pivot overlap with its mount.
    if r.has_gated_child:
        gc = r.gated_child
        if gc == "locking_pawl_revolute":
            pawl_elems = ("pivot_barrel", "pawl_root", "pawl_arm", "pawl_tooth", "pawl_handle")
            if r.has_housing:
                for elem_a in ("pawl_bracket", "pawl_bridge"):
                    for elem_b in pawl_elems:
                        _allow(
                            ctx,
                            model,
                            "operator_housing",
                            "locking_pawl",
                            elem_a,
                            elem_b,
                            f"pawl {elem_b} captured at {elem_a}",
                        )
            else:
                for elem_b in pawl_elems:
                    _allow(
                        ctx,
                        model,
                        "frame",
                        "locking_pawl",
                        "pawl_pedestal",
                        elem_b,
                        f"pawl {elem_b} captured at frame pedestal",
                    )
        elif gc == "latch_arm_revolute":
            if r.has_housing:
                for elem_b in ("pivot_barrel", "arm", "counterweight", "counterweight_arm", "hook"):
                    _allow(
                        ctx,
                        model,
                        "operator_housing",
                        "latch_arm",
                        "pawl_bracket",
                        elem_b,
                        f"latch {elem_b} captured at bracket",
                    )
                    _allow(
                        ctx,
                        model,
                        "operator_housing",
                        "latch_arm",
                        "pawl_bridge",
                        elem_b,
                        f"latch {elem_b} captured at bridge",
                    )
            else:
                for elem_b in ("pivot_barrel", "arm", "counterweight", "counterweight_arm", "hook"):
                    _allow(
                        ctx,
                        model,
                        "frame",
                        "latch_arm",
                        "latch_pedestal",
                        elem_b,
                        f"latch {elem_b} captured at pedestal",
                    )
        elif gc == "inspection_door_revolute":
            if r.has_housing:
                for elem_b in ("hinge_barrel", "door_panel", "handle_stem", "door_handle"):
                    _allow(
                        ctx,
                        model,
                        "operator_housing",
                        "inspection_door",
                        "gearbox_body",
                        elem_b,
                        f"door {elem_b} hinges on housing side",
                    )
            else:
                for elem_b in ("hinge_barrel", "door_panel"):
                    _allow(
                        ctx,
                        model,
                        "frame",
                        "inspection_door",
                        "door_mount",
                        elem_b,
                        f"door {elem_b} hinges on frame mount",
                    )
        elif gc == "gearbox_cover_top_flap":
            _allow(
                ctx,
                model,
                "operator_housing",
                "gearbox_cover",
                "gearbox_body",
                "hinge_barrel",
                "cover hinge on gearbox top",
            )
            _allow(
                ctx,
                model,
                "operator_housing",
                "gearbox_cover",
                "gearbox_body",
                "cover_panel",
                "cover rests on gearbox top",
            )


def run_sluice_gate_with_vertical_lift_panel_tests(
    object_model: ArticulatedObject,
    config: SluiceGateWithVerticalLiftPanelConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    _register_intentional_overlaps(ctx, object_model, r)
    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)
    ctx.fail_if_joint_mating_has_gap()

    part_names = {p.name for p in object_model.parts}
    ctx.check("frame_present", "frame" in part_names, details=str(sorted(part_names)))
    ctx.check("lift_panel_present", "lift_panel" in part_names, details=str(sorted(part_names)))

    plate_lift = object_model.get_articulation("plate_lift")
    ctx.check(
        "plate_lift_prismatic_z",
        plate_lift.articulation_type == ArticulationType.PRISMATIC
        and tuple(plate_lift.axis) == (0.0, 0.0, 1.0),
        details=f"{plate_lift.articulation_type} axis={plate_lift.axis}",
    )
    lim = plate_lift.motion_limits
    ctx.check(
        "plate_lift_range",
        lim is not None and lim.lower == 0.0 and 0.15 <= lim.upper <= 2.5,
        details=f"limits={lim}",
    )

    hoist_joint = object_model.get_articulation("handwheel_spin")
    ctx.check(
        "hoist_continuous",
        hoist_joint.articulation_type == ArticulationType.CONTINUOUS,
        details=f"{hoist_joint.articulation_type}",
    )

    if r.has_housing:
        hj = object_model.get_articulation("frame_to_operator_housing")
        ctx.check(
            "housing_fixed",
            hj.articulation_type == ArticulationType.FIXED,
            details=f"{hj.articulation_type}",
        )

    if r.frame_style == "separate_rails_portal":
        for lx in ("left", "right"):
            j = object_model.get_articulation(f"frame_to_guide_rail_{lx}")
            ctx.check(
                f"guide_rail_{lx}_fixed",
                j.articulation_type == ArticulationType.FIXED,
                details=f"{j.articulation_type}",
            )

    # Pose sweep at PRISMATIC upper.
    if lim is not None and lim.upper is not None:
        with ctx.pose({plate_lift: lim.upper}):
            ctx.fail_if_parts_overlap_in_current_pose(name="panel_open_no_overlap")
            ctx.fail_if_isolated_parts(name="panel_open_no_floating")

    return ctx.report()


__all__ = [
    "SluiceGateWithVerticalLiftPanelConfig",
    "ResolvedSluiceGateWithVerticalLiftPanelConfig",
    "build_sluice_gate_with_vertical_lift_panel",
    "build_seeded_sluice_gate_with_vertical_lift_panel",
    "config_from_seed",
    "resolve_config",
    "run_sluice_gate_with_vertical_lift_panel_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
]
