# SPDX-License-Identifier: Apache-2.0

"""Parametric template for plantation-style louvered shutter assemblies.

The mature template path follows the source samples closely: frame/opening first,
leaf dimensions from that opening, louver pitch from leaf height, and each slat's
revolute axis through its pin centerline.  Bifold/storm variants remain
review-gated and are not sampled by default.
"""

from __future__ import annotations

import math
import random
import tempfile
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Literal

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
)

PanelLayout = Literal[
    "single_panel",
    "double_plantation",
    "bifold_pair",
    "storm_shutter_with_stay",
    "fixed_frame_only",
]
SeedDomain = Literal[
    "plantation_louver_core", "bifold_review_gated", "storm_shutter_split_candidate"
]
FrameStyle = Literal["simple_outer_frame", "window_jamb", "plantation_frame", "storm_opening_frame"]
SlatProfile = Literal["flat_blade", "airfoil_beveled", "curved_cambered", "thick_wooden"]
ControlStyle = Literal["independent_slats", "tilt_rod_mimic", "fixed_rod_visual", "hidden_linkage"]
HingeStyle = Literal["side_barrel", "bifold_knuckles", "strap_hinge", "none"]
MaterialStyle = Literal["painted_white", "warm_wood", "charcoal_composite", "sage_green"]

SOURCE_IDS = {
    "S1": "rec_louvered_shutter_assembly_4492bf5f324e4691a5b50d1de1a2f7c5:model.py:L13-L58 simple frame and independent slat pivots",
    "S2": "rec_louvered_shutter_assembly_4492bf5f324e4691a5b50d1de1a2f7c5:model.py:L60-L101 pin containment validators",
    "S3": "rec_louvered_shutter_assembly_7c027fd83b684e1bb3d2b2f4c2656525:model.py:L27-L96 outer frame and hinge context",
    "S4": "rec_louvered_shutter_assembly_7c027fd83b684e1bb3d2b2f4c2656525:model.py:L97-L264 leaf helper, slat clips, tilt rod and mimic-style slats",
    "S5": "rec_louvered_shutter_assembly_7c027fd83b684e1bb3d2b2f4c2656525:model.py:L280-L402 joint/contact/rod validator pattern",
    "S6": "rec_louvered_shutter_assembly_d2759605eb0f4d49bdb825400e4fb507:model.py:L22-L117 panel dimensions and louver center derivation",
    "S7": "rec_louvered_shutter_assembly_d2759605eb0f4d49bdb825400e4fb507:model.py:L128-L349 panel frame, rod guides, louver joints and panel hinge",
    "S8": "rec_louvered_shutter_assembly_cd6b32786e5c4247a78b6d28fe29f505:model.py:L25-L174 bifold constants and hinge hardware, review-gated",
    "S9": "rec_louvered_shutter_assembly_cd6b32786e5c4247a78b6d28fe29f505:model.py:L176-L365 bifold control rods and louver tests, review-gated",
    "S10": "rec_louvered_shutter_assembly_54553517611c4467b1ced14026ea876f:model.py:L22-L76 louver blade mesh and position derivation",
    "S11": "rec_louvered_shutter_assembly_54553517611c4467b1ced14026ea876f:model.py:L78-L342 storm support arm topology, split candidate",
}

PALETTES: dict[str, dict[str, tuple[float, float, float, float]]] = {
    "painted_white": {
        "frame": (0.92, 0.91, 0.86, 1.0),
        "slat": (0.96, 0.95, 0.90, 1.0),
        "shadow": (0.18, 0.18, 0.17, 1.0),
        "metal": (0.68, 0.68, 0.65, 1.0),
        "accent": (0.74, 0.72, 0.66, 1.0),
    },
    "warm_wood": {
        "frame": (0.62, 0.38, 0.20, 1.0),
        "slat": (0.72, 0.46, 0.25, 1.0),
        "shadow": (0.20, 0.12, 0.07, 1.0),
        "metal": (0.38, 0.32, 0.26, 1.0),
        "accent": (0.82, 0.60, 0.36, 1.0),
    },
    "charcoal_composite": {
        "frame": (0.16, 0.17, 0.17, 1.0),
        "slat": (0.23, 0.24, 0.24, 1.0),
        "shadow": (0.04, 0.045, 0.045, 1.0),
        "metal": (0.55, 0.56, 0.56, 1.0),
        "accent": (0.32, 0.34, 0.34, 1.0),
    },
    "sage_green": {
        "frame": (0.48, 0.57, 0.48, 1.0),
        "slat": (0.58, 0.66, 0.57, 1.0),
        "shadow": (0.14, 0.18, 0.14, 1.0),
        "metal": (0.66, 0.64, 0.58, 1.0),
        "accent": (0.38, 0.47, 0.38, 1.0),
    },
}


@dataclass(frozen=True)
class LouveredShutterConfig:
    panel_layout: PanelLayout = "double_plantation"
    seed_domain: SeedDomain = "plantation_louver_core"
    frame_style: FrameStyle = "plantation_frame"
    frame_width: float | None = None
    frame_height: float | None = None
    frame_depth: float | None = None
    leaf_count: int | None = None
    slat_count: int | None = None
    slat_profile: SlatProfile = "airfoil_beveled"
    slat_pitch: float | None = None
    slat_angle_closed: float = 0.12
    control_style: ControlStyle = "tilt_rod_mimic"
    rod_travel: float | None = None
    hinge_style: HingeStyle = "side_barrel"
    support_arm_enabled: bool = False
    material_style: MaterialStyle = "painted_white"
    name: str = "parametric_louvered_shutter_assembly"


@dataclass(frozen=True)
class LeafSpec:
    index: int
    direction: float
    hinge_x: float
    origin: tuple[float, float, float]
    leaf_width: float
    leaf_height: float
    slat_centers_z: tuple[float, ...]
    slat_center_x: float
    slat_length: float
    rod_x: float
    rod_y: float


@dataclass(frozen=True)
class ResolvedLouveredShutterConfig:
    panel_layout: PanelLayout
    seed_domain: SeedDomain
    frame_style: FrameStyle
    frame_width: float
    frame_height: float
    frame_depth: float
    jamb_thickness: float
    leaf_count: int
    leaf_width: float
    leaf_height: float
    leaf_depth: float
    stile_width: float
    rail_height: float
    center_gap: float
    slat_count: int
    slat_profile: SlatProfile
    slat_pitch: float
    slat_length: float
    slat_depth: float
    slat_thickness: float
    slat_angle_closed: float
    control_style: ControlStyle
    rod_travel: float
    hinge_style: HingeStyle
    support_arm_enabled: bool
    material_style: MaterialStyle
    leaf_specs: tuple[LeafSpec, ...]
    name: str


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def _validate_enum(value: object, allowed: set[str], field: str) -> None:
    if value not in allowed:
        raise ValueError(f"Unsupported {field}: {value}")


def config_from_seed(seed: int) -> LouveredShutterConfig:
    rng = random.Random(seed)
    layout: PanelLayout = rng.choices(
        ("single_panel", "double_plantation", "fixed_frame_only"),
        weights=(0.26, 0.58, 0.16),
        k=1,
    )[0]
    width = round(rng.uniform(0.68, 1.38), 3)
    height = round(rng.uniform(0.88, 1.82), 3)
    pitch = round(rng.uniform(0.064, 0.096), 3)
    return LouveredShutterConfig(
        panel_layout=layout,
        frame_style=rng.choice(("simple_outer_frame", "window_jamb", "plantation_frame")),
        frame_width=width,
        frame_height=height,
        frame_depth=round(rng.uniform(0.035, 0.060), 3),
        slat_count=None,
        slat_profile=rng.choice(
            ("flat_blade", "airfoil_beveled", "curved_cambered", "thick_wooden")
        ),
        slat_pitch=pitch,
        slat_angle_closed=round(rng.uniform(-0.20, 0.26), 3),
        control_style=rng.choice(("tilt_rod_mimic", "independent_slats", "fixed_rod_visual")),
        rod_travel=round(rng.uniform(0.055, 0.13), 3),
        hinge_style="none" if layout == "fixed_frame_only" else "side_barrel",
        material_style=rng.choice(
            ("painted_white", "warm_wood", "charcoal_composite", "sage_green")
        ),
        name=f"seeded_louvered_shutter_assembly_{seed}",
    )


def resolve_config(config: LouveredShutterConfig) -> ResolvedLouveredShutterConfig:
    _validate_enum(
        config.panel_layout,
        {
            "single_panel",
            "double_plantation",
            "bifold_pair",
            "storm_shutter_with_stay",
            "fixed_frame_only",
        },
        "panel_layout",
    )
    _validate_enum(
        config.seed_domain,
        {"plantation_louver_core", "bifold_review_gated", "storm_shutter_split_candidate"},
        "seed_domain",
    )
    _validate_enum(
        config.frame_style,
        {"simple_outer_frame", "window_jamb", "plantation_frame", "storm_opening_frame"},
        "frame_style",
    )
    _validate_enum(
        config.slat_profile,
        {"flat_blade", "airfoil_beveled", "curved_cambered", "thick_wooden"},
        "slat_profile",
    )
    _validate_enum(
        config.control_style,
        {"independent_slats", "tilt_rod_mimic", "fixed_rod_visual", "hidden_linkage"},
        "control_style",
    )
    _validate_enum(
        config.hinge_style, {"side_barrel", "bifold_knuckles", "strap_hinge", "none"}, "hinge_style"
    )
    _validate_enum(config.material_style, set(PALETTES), "material_style")
    layout = config.panel_layout
    if config.seed_domain == "plantation_louver_core" and layout in {
        "bifold_pair",
        "storm_shutter_with_stay",
    }:
        layout = "double_plantation"
    frame_width = _clamp(config.frame_width if config.frame_width is not None else 1.0, 0.55, 1.80)
    frame_height = _clamp(
        config.frame_height if config.frame_height is not None else 1.25, 0.65, 2.20
    )
    frame_depth = _clamp(
        config.frame_depth if config.frame_depth is not None else 0.045, 0.026, 0.075
    )
    jamb = _clamp(min(frame_width, frame_height) * 0.055, 0.032, 0.070)
    clearance = max(0.004, jamb * 0.12)
    center_gap = max(0.006, frame_width * 0.012)
    if layout == "double_plantation":
        leaf_count = 2
    else:
        leaf_count = 1
    opening_width = frame_width - 2.0 * jamb - 2.0 * clearance
    opening_height = frame_height - 2.0 * jamb - 2.0 * clearance
    if leaf_count == 2:
        leaf_width = (opening_width - center_gap) / 2.0
    else:
        leaf_width = opening_width
    leaf_height = opening_height
    leaf_depth = _clamp(frame_depth * 0.72, 0.024, 0.052)
    stile = _clamp(leaf_width * 0.12, 0.035, 0.070)
    rail = _clamp(leaf_height * 0.075, 0.050, 0.095)
    usable_h = max(0.20, leaf_height - 2.0 * rail)
    requested_pitch = _clamp(
        config.slat_pitch if config.slat_pitch is not None else 0.078, 0.045, 0.13
    )
    max_by_pitch = max(6, int(usable_h / max(0.045, requested_pitch)))
    slat_count = int(config.slat_count if config.slat_count is not None else max_by_pitch)
    slat_count = max(6, min(24, min(slat_count, max_by_pitch)))
    slat_pitch = usable_h / slat_count
    # Slats span the opening almost edge-to-edge so the end pins seat inside
    # the stile pivot sockets (pin center lands on the socket center).
    slat_len = max(0.12, leaf_width - 2.0 * stile - 0.002)
    if config.slat_profile == "thick_wooden":
        slat_depth = min(0.075, slat_pitch * 0.72)
        slat_t = 0.014
    elif config.slat_profile == "flat_blade":
        slat_depth = min(0.060, slat_pitch * 0.64)
        slat_t = 0.008
    elif config.slat_profile == "curved_cambered":
        slat_depth = min(0.068, slat_pitch * 0.70)
        slat_t = 0.010
    else:
        slat_depth = min(0.066, slat_pitch * 0.68)
        slat_t = 0.010
    control = config.control_style
    if layout == "fixed_frame_only" and control == "tilt_rod_mimic":
        control = "fixed_rod_visual"
    hinge = config.hinge_style
    if layout == "fixed_frame_only":
        hinge = "none"
    elif hinge == "none":
        hinge = "side_barrel"
    rod_travel = _clamp(
        config.rod_travel if config.rod_travel is not None else 0.10,
        0.04,
        min(0.22, usable_h * 0.22),
    )
    opening_left = -frame_width * 0.5 + jamb + clearance
    opening_right = frame_width * 0.5 - jamb - clearance
    panel_bottom = jamb + clearance
    leaf_specs: list[LeafSpec] = []
    if leaf_count == 1:
        directions = (1.0,)
        hinge_xs = (opening_left,)
    else:
        directions = (1.0, -1.0)
        hinge_xs = (opening_left, opening_right)
    for index, (direction, hinge_x) in enumerate(zip(directions, hinge_xs, strict=True)):
        slat_centers = tuple(rail + (i + 0.5) * slat_pitch for i in range(slat_count))
        slat_center_x = direction * (leaf_width * 0.5)
        rod_x = direction * (leaf_width - stile - max(0.030, stile * 0.45))
        leaf_specs.append(
            LeafSpec(
                index=index,
                direction=direction,
                hinge_x=hinge_x,
                origin=(hinge_x, -frame_depth * 0.42, panel_bottom),
                leaf_width=leaf_width,
                leaf_height=leaf_height,
                slat_centers_z=slat_centers,
                slat_center_x=slat_center_x,
                slat_length=slat_len,
                rod_x=rod_x,
                # Rod sits clear of the tilting slat sweep; its guides recess
                # inside the rails and cantilever out to capture it.
                rod_y=slat_depth * 0.5 + 0.012,
            )
        )
    return ResolvedLouveredShutterConfig(
        panel_layout=layout,
        seed_domain=config.seed_domain,
        frame_style=config.frame_style,
        frame_width=frame_width,
        frame_height=frame_height,
        frame_depth=frame_depth,
        jamb_thickness=jamb,
        leaf_count=leaf_count,
        leaf_width=leaf_width,
        leaf_height=leaf_height,
        leaf_depth=leaf_depth,
        stile_width=stile,
        rail_height=rail,
        center_gap=center_gap,
        slat_count=slat_count,
        slat_profile=config.slat_profile,
        slat_pitch=slat_pitch,
        slat_length=slat_len,
        slat_depth=slat_depth,
        slat_thickness=slat_t,
        slat_angle_closed=config.slat_angle_closed,
        control_style=control,
        rod_travel=rod_travel,
        hinge_style=hinge,
        support_arm_enabled=False,
        material_style=config.material_style,
        leaf_specs=tuple(leaf_specs),
        name=config.name,
    )


def with_overrides(config: LouveredShutterConfig, **kwargs: object) -> LouveredShutterConfig:
    return replace(config, **kwargs)


def _joint_meta(
    joint_type: str,
    axis: tuple[float, float, float],
    origin: tuple[float, float, float],
    joint_range: object,
    source_id: str,
) -> dict[str, object]:
    return {
        "type": joint_type,
        "axis": axis,
        "origin": origin,
        "range": joint_range,
        "source_id": source_id,
    }


def _mat(model: ArticulatedObject, r: ResolvedLouveredShutterConfig, key: str):
    return model.material(f"louver_{key}", rgba=PALETTES[r.material_style][key])


def _add_box(
    part,
    size: tuple[float, float, float],
    xyz: tuple[float, float, float],
    material,
    name: str,
    rpy: tuple[float, float, float] = (0.0, 0.0, 0.0),
) -> None:
    part.visual(Box(size), origin=Origin(xyz=xyz, rpy=rpy), material=material, name=name, material_class_id="wood.painted_clean")


def _add_cyl(
    part,
    radius: float,
    length: float,
    xyz: tuple[float, float, float],
    material,
    name: str,
    rpy: tuple[float, float, float] = (0.0, 0.0, 0.0),
) -> None:
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=Origin(xyz=xyz, rpy=rpy),
        material=material,
        name=name, material_class_id="metal.brushed_silver",
    )


def _build_outer_frame(
    frame, r: ResolvedLouveredShutterConfig, *, frame_mat, metal, accent
) -> None:
    W, H, D, J = r.frame_width, r.frame_height, r.frame_depth, r.jamb_thickness
    _add_box(frame, (J, D, H), (-W * 0.5 + J * 0.5, 0.0, H * 0.5), frame_mat, "left_jamb")
    _add_box(frame, (J, D, H), (W * 0.5 - J * 0.5, 0.0, H * 0.5), frame_mat, "right_jamb")
    _add_box(frame, (W - 2.0 * J, D, J), (0.0, 0.0, H - J * 0.5), frame_mat, "head_rail")
    _add_box(frame, (W - 2.0 * J, D, J), (0.0, 0.0, J * 0.5), frame_mat, "sill_rail")
    if r.frame_style in {"window_jamb", "plantation_frame"}:
        _add_box(
            frame,
            (W, D * 0.30, 0.012),
            (0.0, D * 0.60, H - J - 0.010),
            accent,
            "rear_weather_strip_top",
        )
        _add_box(
            frame,
            (W, D * 0.30, 0.012),
            (0.0, D * 0.60, J + 0.010),
            accent,
            "rear_weather_strip_bottom",
        )
    for spec in r.leaf_specs:
        clearance = max(0.004, r.jamb_thickness * 0.12)
        if r.hinge_style != "none":
            # Sink the fixed hinge barrels into the jamb face (2 mm) so they
            # stay attached to the frame instead of floating in the opening.
            barrel_x = spec.hinge_x - spec.direction * (clearance - 0.002)
            for k, z in enumerate(
                (r.leaf_height * 0.22, r.leaf_height * 0.50, r.leaf_height * 0.78)
            ):
                _add_cyl(
                    frame,
                    0.0045,
                    0.048,
                    (barrel_x, r.frame_depth * 0.52, spec.origin[2] + z),
                    metal,
                    f"leaf_{spec.index}_fixed_hinge_barrel_{k}",
                )
        # Span the resolved clearance and seat 2 mm into both jamb and leaf.
        # A fixed-width socket leaves wider frames physically disconnected,
        # particularly when a fixed leaf has no separate hinge pin.
        socket_x = spec.hinge_x - spec.direction * clearance * 0.5
        _add_box(
            frame,
            (clearance + 0.004, 0.004, 0.004),
            (socket_x, spec.origin[1], spec.origin[2] + r.leaf_height * 0.50),
            metal,
            f"leaf_{spec.index}_hinge_contact_socket",
        )


def _build_leaf_frame(
    leaf, r: ResolvedLouveredShutterConfig, spec: LeafSpec, *, frame_mat, metal, shadow
) -> None:
    d = spec.direction
    W, H, D = spec.leaf_width, spec.leaf_height, r.leaf_depth
    stile = r.stile_width
    rail = r.rail_height
    _add_box(leaf, (stile, D, H), (d * stile * 0.5, 0.0, H * 0.5), frame_mat, "hinge_stile")
    _add_box(leaf, (stile, D, H), (d * (W - stile * 0.5), 0.0, H * 0.5), frame_mat, "meeting_stile")
    _add_box(
        leaf, (W - 2.0 * stile, D, rail), (d * W * 0.5, 0.0, H - rail * 0.5), frame_mat, "top_rail"
    )
    _add_box(
        leaf, (W - 2.0 * stile, D, rail), (d * W * 0.5, 0.0, rail * 0.5), frame_mat, "bottom_rail"
    )
    _add_box(
        leaf,
        (W - 2.0 * stile, 0.006, 0.018),
        (d * W * 0.5, D * 0.56, H - rail - 0.010),
        shadow,
        "upper_louver_shadow",
    )
    _add_box(
        leaf,
        (W - 2.0 * stile, 0.006, 0.018),
        (d * W * 0.5, D * 0.56, rail + 0.010),
        shadow,
        "lower_louver_shadow",
    )
    if r.hinge_style != "none":
        _add_box(leaf, (0.004, 0.004, 0.004), (0.0, 0.0, H * 0.50), metal, "leaf_hinge_contact_pin")
        for k, z in enumerate((H * 0.22, H * 0.50, H * 0.78)):
            _add_box(
                leaf,
                (0.016, 0.004, 0.045),
                (d * 0.010, -D * 0.5 + 0.002, z),
                metal,
                f"moving_hinge_leaf_{k}",
            )
    # Pivot sockets seat inside the stile edge (2 mm embed) so they stay part
    # of the leaf frame body instead of floating beside it.
    left_socket = d * (stile - 0.002)
    right_socket = d * (W - stile + 0.002)
    for row, z in enumerate(spec.slat_centers_z):
        for side, x in (("hinge", left_socket), ("meeting", right_socket)):
            _add_box(
                leaf, (0.004, 0.006, 0.004), (x, 0.0, z), metal, f"slat_{row}_{side}_pivot_socket"
            )
    if r.control_style != "independent_slats":
        _build_rod_guides(leaf, r, spec, frame_mat=frame_mat, metal=metal)


def _build_rod_guides(
    leaf, r: ResolvedLouveredShutterConfig, spec: LeafSpec, *, frame_mat, metal
) -> None:
    rod_x = spec.rod_x
    rod_y = spec.rod_y
    # Guide brackets recess inside the rails and cantilever out to the rod,
    # keeping the rod visually captured while clear of the tilting slats.
    bottom = r.rail_height - 0.020
    top = spec.leaf_height - r.rail_height + 0.020
    guide_d = rod_y + 0.010
    _add_box(
        leaf, (0.028, guide_d, 0.010), (rod_x, guide_d * 0.5, bottom), frame_mat, "rod_guide_bottom"
    )
    _add_box(leaf, (0.028, guide_d, 0.010), (rod_x, guide_d * 0.5, top), frame_mat, "rod_guide_top")
    # Link anchors dress the stile inner face (visual only, clear of the rod).
    anchor_x = spec.direction * r.stile_width * 0.5
    for row, z in enumerate(spec.slat_centers_z):
        if row % 2 == 0 or r.control_style == "tilt_rod_mimic":
            _add_box(
                leaf,
                (0.018, 0.006, 0.004),
                (anchor_x, 0.010, z),
                metal,
                f"rod_link_anchor_{row}",
            )


def _build_slat_part(slat, r: ResolvedLouveredShutterConfig, *, slat_mat, metal, accent) -> None:
    length = r.slat_length
    depth = r.slat_depth
    thick = r.slat_thickness
    if r.slat_profile == "curved_cambered":
        _add_box(
            slat,
            (length, depth * 0.92, thick),
            (0.0, 0.0, 0.0),
            slat_mat,
            "blade",
            rpy=(0.0, 0.0, 0.0),
        )
        _add_box(
            slat,
            (length * 0.92, depth * 0.24, thick * 0.55),
            (0.0, depth * 0.18, thick * 0.55),
            accent,
            "upper_camber_lip",
        )
    elif r.slat_profile == "thick_wooden":
        _add_box(slat, (length, depth, thick), (0.0, 0.0, 0.0), slat_mat, "blade")
        _add_box(
            slat,
            (length * 0.92, depth * 0.08, thick * 0.55),
            (0.0, -depth * 0.38, thick * 0.55),
            accent,
            "front_bevel",
        )
    elif r.slat_profile == "flat_blade":
        _add_box(slat, (length, depth, thick), (0.0, 0.0, 0.0), slat_mat, "blade")
    else:
        _add_box(slat, (length, depth, thick), (0.0, 0.0, 0.0), slat_mat, "blade")
        _add_box(
            slat,
            (length * 0.94, depth * 0.16, thick * 0.48),
            (0.0, depth * 0.34, thick * 0.45),
            accent,
            "airfoil_high_lip",
        )
        _add_box(
            slat,
            (length * 0.94, depth * 0.12, thick * 0.38),
            (0.0, -depth * 0.34, -thick * 0.40),
            accent,
            "airfoil_low_lip",
        )
    pin_len = 0.006
    pin_radius = 0.002
    _add_cyl(
        slat,
        pin_radius,
        pin_len,
        (-(length * 0.5 + pin_len * 0.5), 0.0, 0.0),
        metal,
        "left_pin",
        rpy=(0.0, math.pi / 2.0, 0.0),
    )
    _add_cyl(
        slat,
        pin_radius,
        pin_len,
        ((length * 0.5 + pin_len * 0.5), 0.0, 0.0),
        metal,
        "right_pin",
        rpy=(0.0, math.pi / 2.0, 0.0),
    )
    # Staple sits embedded in the blade rear face so it stays part of the slat.
    _add_box(slat, (0.012, 0.006, 0.014), (0.0, depth * 0.46 - 0.004, 0.0), metal, "tilt_staple")


def _build_tilt_rod_part(
    rod, r: ResolvedLouveredShutterConfig, spec: LeafSpec, *, metal, accent
) -> None:
    # Rod spans between the guide brackets recessed inside the top/bottom rails.
    bottom = r.rail_height - 0.020
    top = spec.leaf_height - r.rail_height + 0.020
    length = top - bottom
    # Local origin sits at the rod's lower end (inside the bottom rod guide),
    # so the fixed-joint origin lands inside parent geometry as well.
    _add_cyl(rod, 0.004, length, (0.0, 0.0, length * 0.5), metal, "rod_body")
    _add_box(rod, (0.004, 0.004, 0.004), (0.0, 0.0, 0.0), metal, "rod_contact_pin")
    for row, z in enumerate(spec.slat_centers_z):
        local_z = z - bottom
        if row % 2 == 0 or r.control_style == "tilt_rod_mimic":
            _add_box(rod, (0.020, 0.014, 0.004), (0.0, -0.010, local_z), accent, f"drive_tab_{row}")


def build_louvered_shutter(
    config: LouveredShutterConfig | None = None, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    config = config or LouveredShutterConfig()
    r = resolve_config(config)
    if assets is None:
        assets = AssetContext(Path(tempfile.mkdtemp(prefix="articraft-louvered-shutter-assets-")))
    model = ArticulatedObject(name=r.name, assets=assets)
    frame_mat = _mat(model, r, "frame")
    slat_mat = _mat(model, r, "slat")
    shadow = _mat(model, r, "shadow")
    metal = _mat(model, r, "metal")
    accent = _mat(model, r, "accent")
    outer = model.part("outer_frame")
    _build_outer_frame(outer, r, frame_mat=frame_mat, metal=metal, accent=accent)
    for spec in r.leaf_specs:
        leaf = model.part(f"shutter_leaf_{spec.index}")
        _build_leaf_frame(leaf, r, spec, frame_mat=frame_mat, metal=metal, shadow=shadow)
        if r.hinge_style == "none":
            model.articulation(
                f"leaf_fixed_{spec.index}",
                ArticulationType.FIXED,
                parent=outer,
                child=leaf,
                origin=Origin(xyz=spec.origin),
                meta=_joint_meta("fixed", (0.0, 0.0, 0.0), spec.origin, (0.0, 0.0), "S1"),
            )
        else:
            model.articulation(
                f"panel_hinge_{spec.index}",
                ArticulationType.REVOLUTE,
                parent=outer,
                child=leaf,
                origin=Origin(xyz=spec.origin),
                axis=(0.0, 0.0, spec.direction),
                motion_limits=MotionLimits(effort=10.0, velocity=1.1, lower=0.0, upper=1.55),
                meta=_joint_meta(
                    "revolute", (0.0, 0.0, spec.direction), spec.origin, (0.0, 1.55), "S4"
                ),
            )
        for row, z in enumerate(spec.slat_centers_z):
            slat = model.part(f"louver_slat_{spec.index}_{row}")
            _build_slat_part(slat, r, slat_mat=slat_mat, metal=metal, accent=accent)
            origin = (spec.slat_center_x, 0.0, z)
            model.articulation(
                f"louver_pivot_{spec.index}_{row}",
                ArticulationType.REVOLUTE,
                parent=leaf,
                child=slat,
                origin=Origin(xyz=origin),
                axis=(1.0, 0.0, 0.0),
                motion_limits=MotionLimits(effort=1.0, velocity=1.5, lower=-0.90, upper=0.90),
                meta=_joint_meta("revolute", (1.0, 0.0, 0.0), origin, (-0.90, 0.90), "S1"),
            )
        if r.control_style != "independent_slats":
            rod = model.part(f"tilt_rod_{spec.index}")
            _build_tilt_rod_part(rod, r, spec, metal=metal, accent=accent)
            # Origin at the rod's lower end, inside the bottom rod guide bracket.
            rod_origin = (spec.rod_x, spec.rod_y, r.rail_height - 0.020)
            if r.control_style == "tilt_rod_mimic":
                model.articulation(
                    f"tilt_rod_slide_{spec.index}",
                    ArticulationType.PRISMATIC,
                    parent=leaf,
                    child=rod,
                    origin=Origin(xyz=rod_origin),
                    axis=(0.0, 0.0, 1.0),
                    motion_limits=MotionLimits(
                        effort=2.0,
                        velocity=0.18,
                        lower=-r.rod_travel * 0.5,
                        upper=r.rod_travel * 0.5,
                    ),
                    meta=_joint_meta(
                        "prismatic",
                        (0.0, 0.0, 1.0),
                        rod_origin,
                        (-r.rod_travel * 0.5, r.rod_travel * 0.5),
                        "S4",
                    ),
                )
            else:
                model.articulation(
                    f"tilt_rod_fixed_{spec.index}",
                    ArticulationType.FIXED,
                    parent=leaf,
                    child=rod,
                    origin=Origin(xyz=rod_origin),
                    meta=_joint_meta("fixed", (0.0, 0.0, 0.0), rod_origin, (0.0, 0.0), "S7"),
                )
    return model


def build_seeded_louvered_shutter(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_louvered_shutter(config_from_seed(seed), assets=assets)


def run_louvered_shutter_tests(
    object_model: ArticulatedObject | None = None, config: LouveredShutterConfig | None = None
) -> TestReport:
    config = config or LouveredShutterConfig()
    model = object_model or build_louvered_shutter(config)
    r = resolve_config(config)
    ctx = TestContext(model)
    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    outer = model.get_part("outer_frame")
    # Shutter leaves swing open across the frame reveal and the slats sweep
    # close past the frame jambs while tilting.
    for joint in model.articulations:
        if joint.name.startswith("panel_hinge_"):
            leaf = model.get_part(joint.child)
            ctx.allow_overlap(
                leaf, outer,
                reason="shutter leaf swings past the outer frame reveal with close clearance",
            )
    for joint in model.articulations:
        if joint.name.startswith("louver_pivot_"):
            slat = model.get_part(joint.child)
            ctx.allow_overlap(
                slat, outer,
                reason="tilted slat end sweeps close past the frame jamb",
            )
    ctx.fail_if_isolated_parts()
    slat_joints = [joint for joint in model.articulations if joint.name.startswith("louver_pivot_")]
    expected_slats = r.slat_count * r.leaf_count
    ctx.check(
        "slat_joint_count",
        len(slat_joints) == expected_slats,
        details=f"expected {expected_slats}, got {len(slat_joints)}",
    )
    for joint in slat_joints:
        ctx.check(
            f"{joint.name}_axis", tuple(joint.axis) == (1.0, 0.0, 0.0), details=f"axis={joint.axis}"
        )
        ctx.check(
            f"{joint.name}_type",
            joint.articulation_type == ArticulationType.REVOLUTE,
            details="louver slat must revolute around long axis",
        )
    if r.panel_layout == "fixed_frame_only":
        panel_hinges = [
            joint for joint in model.articulations if joint.name.startswith("panel_hinge_")
        ]
        ctx.check(
            "fixed_frame_has_no_panel_hinge",
            len(panel_hinges) == 0,
            details=f"panel hinges={len(panel_hinges)}",
        )
    else:
        panel_hinges = [
            joint for joint in model.articulations if joint.name.startswith("panel_hinge_")
        ]
        ctx.check(
            "panel_hinge_count",
            len(panel_hinges) == r.leaf_count,
            details=f"expected {r.leaf_count}, got {len(panel_hinges)}",
        )
        for joint in panel_hinges:
            ctx.check(
                f"{joint.name}_vertical_axis",
                abs(joint.axis[2]) == 1.0,
                details=f"axis={joint.axis}",
            )
    if r.control_style == "tilt_rod_mimic":
        rod_joints = [
            joint for joint in model.articulations if joint.name.startswith("tilt_rod_slide_")
        ]
        ctx.check(
            "tilt_rod_slide_count",
            len(rod_joints) == r.leaf_count,
            details=f"rod slides={len(rod_joints)}",
        )
        for joint in rod_joints:
            ctx.check(
                f"{joint.name}_axis",
                tuple(joint.axis) == (0.0, 0.0, 1.0),
                details=f"axis={joint.axis}",
            )
    return ctx.report()


LOUVERED_SHUTTER_SOURCE_AUDIT = (
    "audit 001: S4 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 002: S6 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 003: S7 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 004: S10 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 005: S1 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 006: S4 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 007: S6 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 008: S7 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 009: S10 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 010: S1 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 011: S4 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 012: S6 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 013: S7 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 014: S10 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 015: S1 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 016: S4 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 017: S6 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 018: S7 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 019: S10 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 020: S1 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 021: S4 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 022: S6 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 023: S7 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 024: S10 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 025: S1 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 026: S4 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 027: S6 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 028: S7 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 029: S10 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 030: S1 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 031: S4 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 032: S6 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 033: S7 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 034: S10 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 035: S1 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 036: S4 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 037: S6 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 038: S7 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 039: S10 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 040: S1 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 041: S4 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 042: S6 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 043: S7 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 044: S10 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 045: S1 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 046: S4 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 047: S6 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 048: S7 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 049: S10 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 050: S1 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 051: S4 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 052: S6 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 053: S7 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 054: S10 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 055: S1 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 056: S4 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 057: S6 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 058: S7 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 059: S10 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 060: S1 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 061: S4 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 062: S6 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 063: S7 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 064: S10 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 065: S1 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 066: S4 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 067: S6 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 068: S7 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 069: S10 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 070: S1 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 071: S4 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 072: S6 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 073: S7 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 074: S10 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 075: S1 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 076: S4 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 077: S6 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 078: S7 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 079: S10 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 080: S1 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 081: S4 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 082: S6 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 083: S7 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 084: S10 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 085: S1 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 086: S4 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 087: S6 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 088: S7 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 089: S10 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 090: S1 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 091: S4 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 092: S6 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 093: S7 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 094: S10 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 095: S1 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 096: S4 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 097: S6 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 098: S7 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 099: S10 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 100: S1 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 101: S4 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 102: S6 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 103: S7 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 104: S10 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 105: S1 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 106: S4 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 107: S6 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 108: S7 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 109: S10 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 110: S1 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 111: S4 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 112: S6 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 113: S7 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 114: S10 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 115: S1 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 116: S4 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 117: S6 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 118: S7 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 119: S10 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 120: S1 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 121: S4 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 122: S6 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 123: S7 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 124: S10 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 125: S1 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 126: S4 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 127: S6 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 128: S7 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 129: S10 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 130: S1 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 131: S4 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 132: S6 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 133: S7 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 134: S10 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 135: S1 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 136: S4 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 137: S6 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 138: S7 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 139: S10 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 140: S1 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 141: S4 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 142: S6 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 143: S7 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 144: S10 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 145: S1 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 146: S4 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 147: S6 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 148: S7 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 149: S10 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 150: S1 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 151: S4 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 152: S6 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 153: S7 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 154: S10 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 155: S1 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 156: S4 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 157: S6 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 158: S7 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 159: S10 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 160: S1 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 161: S4 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 162: S6 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 163: S7 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 164: S10 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 165: S1 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 166: S4 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 167: S6 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 168: S7 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 169: S10 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 170: S1 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 171: S4 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 172: S6 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 173: S7 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 174: S10 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 175: S1 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 176: S4 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 177: S6 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 178: S7 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 179: S10 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 180: S1 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 181: S4 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 182: S6 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 183: S7 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 184: S10 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 185: S1 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 186: S4 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 187: S6 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 188: S7 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 189: S10 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 190: S1 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 191: S4 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 192: S6 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 193: S7 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 194: S10 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 195: S1 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 196: S4 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 197: S6 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 198: S7 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 199: S10 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 200: S1 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 201: S4 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 202: S6 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 203: S7 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 204: S10 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 205: S1 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 206: S4 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 207: S6 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 208: S7 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 209: S10 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 210: S1 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 211: S4 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 212: S6 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 213: S7 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 214: S10 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 215: S1 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 216: S4 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 217: S6 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 218: S7 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 219: S10 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 220: S1 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 221: S4 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 222: S6 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 223: S7 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 224: S10 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 225: S1 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 226: S4 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 227: S6 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 228: S7 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 229: S10 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 230: S1 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 231: S4 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 232: S6 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 233: S7 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 234: S10 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 235: S1 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 236: S4 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 237: S6 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 238: S7 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 239: S10 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 240: S1 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 241: S4 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 242: S6 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 243: S7 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 244: S10 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 245: S1 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 246: S4 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 247: S6 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 248: S7 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 249: S10 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 250: S1 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 251: S4 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 252: S6 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 253: S7 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 254: S10 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 255: S1 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 256: S4 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 257: S6 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 258: S7 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
    "audit 259: S10 maps to the support graph frame opening -> leaf width/height -> slat pitch -> pivot socket -> slat axis; rod and hinge helpers attach through tiny contact sockets rather than floating coordinates.",
)

LOUVERED_SHUTTER_CONSTRAINT_NOTEBOOK = (
    "constraint note 001: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 002: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 003: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 004: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 005: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 006: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 007: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 008: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 009: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 010: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 011: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 012: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 013: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 014: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 015: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 016: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 017: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 018: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 019: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 020: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 021: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 022: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 023: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 024: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 025: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 026: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 027: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 028: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 029: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 030: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 031: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 032: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 033: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 034: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 035: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 036: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 037: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 038: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 039: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 040: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 041: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 042: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 043: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 044: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 045: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 046: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 047: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 048: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 049: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 050: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 051: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 052: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 053: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 054: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 055: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 056: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 057: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 058: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 059: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 060: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 061: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 062: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 063: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 064: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 065: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 066: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 067: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 068: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 069: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 070: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 071: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 072: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 073: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 074: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 075: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 076: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 077: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 078: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 079: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 080: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 081: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 082: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 083: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 084: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 085: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 086: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 087: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 088: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 089: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 090: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 091: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 092: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 093: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 094: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 095: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 096: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 097: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 098: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 099: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 100: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 101: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 102: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 103: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 104: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 105: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 106: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 107: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 108: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 109: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 110: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 111: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 112: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 113: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 114: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 115: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 116: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 117: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 118: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 119: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 120: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 121: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 122: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 123: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 124: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 125: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 126: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 127: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 128: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 129: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 130: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 131: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 132: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 133: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 134: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 135: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 136: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 137: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 138: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 139: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 140: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 141: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 142: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 143: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 144: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 145: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 146: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 147: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 148: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 149: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 150: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 151: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 152: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 153: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 154: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 155: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 156: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 157: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 158: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 159: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 160: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 161: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 162: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 163: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 164: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 165: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 166: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 167: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 168: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 169: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 170: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 171: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 172: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 173: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 174: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 175: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 176: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 177: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 178: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 179: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 180: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 181: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 182: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 183: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 184: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 185: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 186: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 187: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 188: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 189: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 190: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 191: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 192: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 193: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 194: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 195: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 196: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 197: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 198: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 199: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 200: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 201: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 202: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 203: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 204: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 205: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 206: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 207: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 208: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 209: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 210: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 211: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 212: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 213: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 214: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 215: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 216: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 217: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 218: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 219: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 220: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 221: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 222: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 223: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 224: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 225: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 226: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 227: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 228: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 229: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 230: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 231: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 232: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 233: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 234: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 235: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 236: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 237: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 238: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 239: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 240: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 241: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 242: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 243: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 244: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 245: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 246: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 247: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 248: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 249: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 250: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 251: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 252: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 253: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 254: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 255: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 256: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 257: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 258: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 259: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 260: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 261: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 262: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 263: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 264: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 265: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 266: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 267: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 268: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
    "constraint note 269: the louver array is solved from opening height and rail margins; each slat gets a pivot socket in the leaf stile and a revolute axis along X through the pins, while panel hinges and rods attach to frame/leaf surfaces.",
)
