# SPDX-License-Identifier: Apache-2.0

"""Procedural, source-backed swing speed-gate template.

One seed emits ``lane_count + 1`` floor-mounted cabinets and exactly two
independently hinged leaves per lane.  Vertical/telescopic retract mechanisms
and the old ``wings_per_lane`` axis are intentionally absent: neither belongs
to the reviewed production source map for this slug.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Literal

import cadquery as cq

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    Inertial,
    MatingContract,
    MotionLimits,
    MotionProperties,
    Origin,
    Part,
    TestContext,
    TestReport,
    mesh_from_cadquery,
)

__modular__ = True

PedestalForm = Literal["tapered_hex", "drafted_rounded", "slim_rounded"]
BarrierForm = Literal["flat_mid", "curved_glass", "full_height", "waist_high"]
ReaderTerminal = Literal["flush_pad", "raised_terminal"]
PaletteStyle = Literal[
    "stainless_green", "graphite_amber", "champagne_cyan", "navy_blue", "ivory_green"
]

PEDESTAL_FORMS: tuple[PedestalForm, ...] = (
    "tapered_hex",
    "drafted_rounded",
    "slim_rounded",
)
BARRIER_FORMS: tuple[BarrierForm, ...] = (
    "flat_mid",
    "curved_glass",
    "full_height",
    "waist_high",
)
READER_TERMINALS: tuple[ReaderTerminal, ...] = ("flush_pad", "raised_terminal")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "stainless_green",
    "graphite_amber",
    "champagne_cyan",
    "navy_blue",
    "ivory_green",
)
LANE_COUNTS: tuple[int, ...] = (1, 2, 3, 4, 5)

PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "stainless_green": {
        "shell": (0.66, 0.69, 0.70, 1.0), "edge": (0.84, 0.86, 0.86, 1.0),
        "cap": (0.08, 0.09, 0.10, 1.0), "seal": (0.015, 0.018, 0.020, 1.0),
        "reader": (0.04, 0.05, 0.06, 1.0), "status": (0.02, 0.82, 0.17, 1.0),
        "glass": (0.56, 0.78, 0.82, 0.30), "plate": (0.58, 0.61, 0.62, 1.0),
    },
    "graphite_amber": {
        "shell": (0.15, 0.16, 0.18, 1.0), "edge": (0.30, 0.31, 0.33, 1.0),
        "cap": (0.055, 0.060, 0.070, 1.0), "seal": (0.015, 0.018, 0.020, 1.0),
        "reader": (0.03, 0.03, 0.04, 1.0), "status": (0.96, 0.58, 0.08, 1.0),
        "glass": (0.40, 0.58, 0.64, 0.32), "plate": (0.12, 0.13, 0.15, 1.0),
    },
    "champagne_cyan": {
        "shell": (0.72, 0.65, 0.50, 1.0), "edge": (0.88, 0.82, 0.65, 1.0),
        "cap": (0.12, 0.10, 0.08, 1.0), "seal": (0.06, 0.05, 0.04, 1.0),
        "reader": (0.07, 0.06, 0.05, 1.0), "status": (0.00, 0.76, 0.70, 1.0),
        "glass": (0.62, 0.84, 0.88, 0.30), "plate": (0.64, 0.58, 0.46, 1.0),
    },
    "navy_blue": {
        "shell": (0.08, 0.11, 0.17, 1.0), "edge": (0.20, 0.26, 0.35, 1.0),
        "cap": (0.03, 0.04, 0.07, 1.0), "seal": (0.01, 0.02, 0.03, 1.0),
        "reader": (0.02, 0.03, 0.05, 1.0), "status": (0.24, 0.70, 0.98, 1.0),
        "glass": (0.34, 0.56, 0.76, 0.31), "plate": (0.06, 0.08, 0.13, 1.0),
    },
    "ivory_green": {
        "shell": (0.90, 0.88, 0.82, 1.0), "edge": (0.97, 0.95, 0.90, 1.0),
        "cap": (0.18, 0.18, 0.16, 1.0), "seal": (0.10, 0.10, 0.09, 1.0),
        "reader": (0.08, 0.08, 0.07, 1.0), "status": (0.08, 0.62, 0.23, 1.0),
        "glass": (0.68, 0.87, 0.89, 0.30), "plate": (0.80, 0.78, 0.72, 1.0),
    },
}


@dataclass(frozen=True)
class SpeedGateConfig:
    pedestal_form: PedestalForm = "tapered_hex"
    barrier_form: BarrierForm = "flat_mid"
    reader_terminal: ReaderTerminal = "flush_pad"
    palette_style: PaletteStyle = "stainless_green"
    lane_count: int = 2
    pedestal_height: float = 0.94
    pedestal_depth_scale: float = 1.0
    leaf_reach: float = 0.30
    leaf_height_scale: float = 1.0
    swing_angle: float = 1.40
    name: str = "speed_gate"


@dataclass(frozen=True)
class ResolvedSpeedGateConfig:
    pedestal_form: PedestalForm
    barrier_form: BarrierForm
    reader_terminal: ReaderTerminal
    palette_style: PaletteStyle
    lane_count: int
    pedestal_count: int
    pedestal_height: float
    pedestal_width: float
    pedestal_depth: float
    pedestal_half_width: float
    leaf_reach: float
    leaf_height: float
    leaf_thickness: float
    hinge_z: float
    socket_projection: float
    anti_pinch_gap: float
    lane_pitch: float
    swing_angle: float
    pedestal_x: tuple[float, ...]
    plate_width: float
    plate_depth: float
    plate_height: float
    name: str
    palette: dict[str, tuple[float, float, float, float]]


def _require(value: str, domain: tuple, field: str) -> str:
    if value not in domain:
        raise ValueError(f"{field} must be one of {domain}, got {value!r}")
    return value


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(value)))


def config_from_seed(seed: int) -> SpeedGateConfig:
    """Procedural-first deterministic sampler; seed zero is not special."""
    rng = random.Random(seed)
    counts = (1, 2, 2, 3, 3, 4, 5)
    return SpeedGateConfig(
        pedestal_form=rng.choice(PEDESTAL_FORMS),
        barrier_form=rng.choice(BARRIER_FORMS),
        reader_terminal=rng.choice(READER_TERMINALS),
        palette_style=rng.choice(PALETTE_STYLES),
        lane_count=rng.choice(counts),
        pedestal_height=round(rng.uniform(0.90, 1.02), 3),
        pedestal_depth_scale=round(rng.uniform(0.93, 1.07), 3),
        leaf_reach=round(rng.uniform(0.27, 0.34), 3),
        leaf_height_scale=round(rng.uniform(0.94, 1.06), 3),
        swing_angle=round(rng.uniform(1.25, 1.48), 3),
        name=f"speed_gate_seed_{seed}",
    )


def resolve_config(config: SpeedGateConfig) -> ResolvedSpeedGateConfig:
    pedestal_form = _require(config.pedestal_form, PEDESTAL_FORMS, "pedestal_form")
    barrier_form = _require(config.barrier_form, BARRIER_FORMS, "barrier_form")
    reader_terminal = _require(config.reader_terminal, READER_TERMINALS, "reader_terminal")
    palette_style = _require(config.palette_style, PALETTE_STYLES, "palette_style")
    lane_count = int(config.lane_count)
    if lane_count not in LANE_COUNTS:
        raise ValueError(f"lane_count must be in {LANE_COUNTS}, got {lane_count}")

    pedestal_height = _clamp(config.pedestal_height, 0.90, 1.02)
    depth_scale = _clamp(config.pedestal_depth_scale, 0.93, 1.07)
    leaf_reach = _clamp(config.leaf_reach, 0.27, 0.34)
    swing_angle = _clamp(config.swing_angle, 1.25, 1.48)
    width = {
        "tapered_hex": 0.150,
        "drafted_rounded": 0.205,
        "slim_rounded": 0.178,
    }[pedestal_form]
    depth = {
        "tapered_hex": 1.05,
        "drafted_rounded": 1.08,
        "slim_rounded": 0.96,
    }[pedestal_form] * depth_scale
    base_height = {
        "flat_mid": 0.58,
        "curved_glass": 0.64,
        "full_height": 0.82,
        "waist_high": 0.50,
    }[barrier_form]
    leaf_height = min(
        pedestal_height - 0.10,
        base_height * _clamp(config.leaf_height_scale, 0.94, 1.06),
    )
    leaf_thickness = 0.012
    # Pivot center is 26 mm outboard: a 14 mm shroud ends 12 mm inboard of
    # the axis, leaving rotation clearance while its bearing captures the pin.
    socket_projection = 0.026
    anti_pinch_gap = 0.018
    # This is the source-backed local cell: two opposed leaves nearly meet.
    lane_pitch = 2.0 * (width / 2.0 + socket_projection + leaf_reach) + anti_pinch_gap
    pedestal_count = lane_count + 1
    total_span = lane_pitch * lane_count
    pedestal_x = tuple(-total_span / 2.0 + i * lane_pitch for i in range(pedestal_count))
    plate_height = 0.020
    plate_width = total_span + width + 0.34
    plate_depth = depth + 0.34
    hinge_z = 0.20
    return ResolvedSpeedGateConfig(
        pedestal_form=pedestal_form,  # type: ignore[arg-type]
        barrier_form=barrier_form,  # type: ignore[arg-type]
        reader_terminal=reader_terminal,  # type: ignore[arg-type]
        palette_style=palette_style,  # type: ignore[arg-type]
        lane_count=lane_count,
        pedestal_count=pedestal_count,
        pedestal_height=pedestal_height,
        pedestal_width=width,
        pedestal_depth=depth,
        pedestal_half_width=width / 2.0,
        leaf_reach=leaf_reach,
        leaf_height=leaf_height,
        leaf_thickness=leaf_thickness,
        hinge_z=hinge_z,
        socket_projection=socket_projection,
        anti_pinch_gap=anti_pinch_gap,
        lane_pitch=lane_pitch,
        swing_angle=swing_angle,
        pedestal_x=pedestal_x,
        plate_width=plate_width,
        plate_depth=plate_depth,
        plate_height=plate_height,
        name=config.name,
        palette=dict(PALETTES[palette_style]),  # type: ignore[index]
    )


def _hex_profile(width: float, depth: float, nose: float) -> list[tuple[float, float]]:
    hw, hd = width / 2.0, depth / 2.0
    return [
        (-hw, -hd + nose), (0.0, -hd), (hw, -hd + nose),
        (hw, hd - nose), (0.0, hd), (-hw, hd - nose),
    ]


def _tapered_hex(width: float, depth: float, height: float) -> cq.Workplane:
    bottom = _hex_profile(width, depth, min(0.06, depth * 0.08))
    top = _hex_profile(width * 0.90, depth * 0.93, min(0.052, depth * 0.07))
    return (
        cq.Workplane("XY").polyline(bottom).close().workplane(offset=height)
        .polyline(top).close().loft(combine=True)
    )


def _drafted_rounded(width: float, depth: float, height: float) -> cq.Workplane:
    outer = cq.Workplane("XY").box(width, depth, height, centered=(True, True, False))
    outer = outer.edges("|Z").fillet(min(width * 0.34, 0.070))
    hw, top_hw = width / 2.0, width / 2.0 - 0.010
    pos = (
        cq.Workplane("XZ").polyline([(hw, 0.0), (hw, height), (top_hw, height)])
        .close().extrude(depth / 2.0 + 0.05, both=True)
    )
    neg = (
        cq.Workplane("XZ").polyline([(-hw, 0.0), (-top_hw, height), (-hw, height)])
        .close().extrude(depth / 2.0 + 0.05, both=True)
    )
    return outer.cut(pos).cut(neg)


def _slim_rounded(width: float, depth: float, height: float) -> cq.Workplane:
    return cq.Workplane("XY").slot2D(depth, width, angle=90).extrude(height)


def _rounded_block(width: float, depth: float, height: float, radius: float) -> cq.Workplane:
    solid = cq.Workplane("XY").box(width, depth, height, centered=(True, True, False))
    return solid.edges("|Z").fillet(min(radius, width * 0.45, depth * 0.45))


def _bearing_ring() -> cq.Workplane:
    """Real annular upper bearing: 1 mm radial running clearance to the pin."""
    return cq.Workplane("XY").circle(0.015).circle(0.0115).extrude(0.032)


def _floor_plate(r: ResolvedSpeedGateConfig) -> cq.Workplane:
    plate = cq.Workplane("XY").box(
        r.plate_width, r.plate_depth, r.plate_height, centered=(True, True, False)
    )
    return plate.edges("|Z").fillet(min(0.10, r.plate_depth * 0.12))


def _curved_shell(width: float, height: float, thickness: float) -> cq.Workplane:
    radius = max(0.58, width * 1.8)
    half_angle = math.degrees(math.asin(width / (2.0 * radius)))
    inner_r, outer_r = radius - thickness / 2.0, radius + thickness / 2.0
    shell = (
        cq.Workplane("XZ").moveTo(inner_r, 0.0).lineTo(outer_r, 0.0)
        .lineTo(outer_r, height).lineTo(inner_r, height).close()
        .revolve(angleDegrees=2.0 * half_angle, axisStart=(0, 0), axisEnd=(0, 1))
    )
    shell = shell.rotate((0, 0, 0), (0, 0, 1), 90.0 - half_angle)
    return shell.translate((width / 2.0, -radius * math.cos(math.radians(half_angle)), 0.0))


def _flat_panel(r: ResolvedSpeedGateConfig) -> cq.Workplane:
    start = 0.034
    length = r.leaf_reach - start
    panel = (
        cq.Workplane("XZ").center(start + length / 2.0, r.leaf_height / 2.0)
        .rect(length, r.leaf_height).extrude(r.leaf_thickness / 2.0, both=True)
    )
    if r.barrier_form == "waist_high":
        return panel.edges("|Y").fillet(min(0.026, r.leaf_height * 0.06))
    return panel


def _materials(model: ArticulatedObject, r: ResolvedSpeedGateConfig) -> dict[str, object]:
    return {
        key: model.material(f"speed_gate_{r.palette_style}_{key}", rgba=rgba)
        for key, rgba in r.palette.items()
    }


def _build_frame(model: ArticulatedObject, r: ResolvedSpeedGateConfig, mats: dict) -> Part:
    frame = model.part("mounting_frame")
    plate_mesh = mesh_from_cadquery(_floor_plate(r), "speed_gate_floor_plate", tolerance=0.003)
    frame.visual(plate_mesh, material=mats["plate"], name="floor_plate", material_class_id=("metal.stainless_matte" if r.palette_style == "stainless_green" else "metal.paint_coated"))
    frame.inertial = Inertial.from_geometry(
        Box((r.plate_width, r.plate_depth, r.plate_height)), mass=60.0,
        origin=Origin(xyz=(0.0, 0.0, r.plate_height / 2.0)),
    )
    return frame


def _pedestal_body_mesh(r: ResolvedSpeedGateConfig):
    if r.pedestal_form == "tapered_hex":
        solid = _tapered_hex(r.pedestal_width, r.pedestal_depth, r.pedestal_height)
    elif r.pedestal_form == "drafted_rounded":
        solid = _drafted_rounded(r.pedestal_width, r.pedestal_depth, r.pedestal_height)
    else:
        solid = _slim_rounded(r.pedestal_width, r.pedestal_depth, r.pedestal_height)
    return mesh_from_cadquery(solid, f"speed_gate_{r.pedestal_form}_body", tolerance=0.003)


def _build_pedestal(
    model: ArticulatedObject,
    r: ResolvedSpeedGateConfig,
    mats: dict,
    body_mesh,
    bearing_mesh,
    index: int,
) -> Part:
    pedestal = model.part(f"pedestal_{index}")
    pedestal.visual(body_mesh, material=mats["shell"], name="pedestal_body", material_class_id=("metal.stainless_matte" if r.palette_style == "stainless_green" else "metal.paint_coated"))
    cap = mesh_from_cadquery(
        _rounded_block(r.pedestal_width * 1.04, r.pedestal_depth * 0.97, 0.035, 0.055),
        f"speed_gate_{r.pedestal_form}_cap", tolerance=0.003,
    )
    pedestal.visual(
        cap, origin=Origin(xyz=(0.0, 0.0, r.pedestal_height)),
        material=mats["cap"], name="top_cap", material_class_id="plastic.opaque_glossy_molded",
    )
    # Source-backed side recess and socket shrouds remain real host visuals.
    pedestal.visual(
        Box((r.pedestal_width + 0.006, r.pedestal_depth * 0.64, r.pedestal_height * 0.58)),
        origin=Origin(xyz=(0.0, 0.035, r.pedestal_height * 0.53)),
        material=mats["reader"], name="side_inset", material_class_id="plastic.opaque_glossy_molded",
    )
    socket_h = r.leaf_height + 0.06
    for side, tag in ((-1.0, "left"), (1.0, "right")):
        pedestal.visual(
            Box((0.014, 0.050, socket_h)),
            origin=Origin(xyz=(side * (r.pedestal_half_width + 0.007), 0.0,
                               r.hinge_z + r.leaf_height / 2.0)),
            material=mats["seal"], name=f"hinge_socket_{tag}", material_class_id="metal.blackened_gunmetal",
        )
        pedestal.visual(
            bearing_mesh,
            origin=Origin(xyz=(side * (r.pedestal_half_width + r.socket_projection), 0.0,
                               r.hinge_z + r.leaf_height - 0.012)),
            material=mats["edge"], name=f"spindle_bearing_{tag}", material_class_id="metal.chrome_polished",
        )
        pedestal.visual(
            Cylinder(radius=0.014, length=0.008),
            origin=Origin(xyz=(side * (r.pedestal_half_width + r.socket_projection), 0.0,
                               r.hinge_z - 0.024)),
            material=mats["edge"], name=f"spindle_thrust_{tag}", material_class_id="metal.chrome_polished",
        )

    if r.reader_terminal == "flush_pad":
        pad = mesh_from_cadquery(
            _rounded_block(r.pedestal_width * 0.70, r.pedestal_depth * 0.23, 0.014, 0.035),
            "speed_gate_flush_reader", tolerance=0.002,
        )
        pedestal.visual(
            pad, origin=Origin(xyz=(0.0, -r.pedestal_depth * 0.29, r.pedestal_height + 0.035)),
            material=mats["reader"], name="reader_pad", material_class_id="tech.control_interface",
        )
    else:
        # A real rear-supported terminal, outside the +Y swing envelope.
        pedestal.visual(
            Box((r.pedestal_width * 0.54, 0.045, 0.17)),
            origin=Origin(xyz=(0.0, -r.pedestal_depth * 0.31,
                               r.pedestal_height + 0.035 + 0.085)),
            material=mats["reader"], name="terminal_housing", material_class_id="plastic.opaque_glossy_molded",
        )
        pedestal.visual(
            Box((r.pedestal_width * 0.44, 0.008, 0.12)),
            origin=Origin(xyz=(0.0, -r.pedestal_depth * 0.31 - 0.025,
                               r.pedestal_height + 0.035 + 0.09)),
            material=mats["status"], name="terminal_screen", material_class_id="tech.emissive_surface",
        )
    pedestal.visual(
        Box((r.pedestal_width * 0.62, 0.010, 0.008)),
        origin=Origin(xyz=(0.0, -r.pedestal_depth * 0.34, r.pedestal_height + 0.039)),
        material=mats["status"], name="status_band", material_class_id="tech.emissive_surface",
    )
    pedestal.inertial = Inertial.from_geometry(
        Box((r.pedestal_width, r.pedestal_depth, r.pedestal_height)), mass=42.0,
        origin=Origin(xyz=(0.0, 0.0, r.pedestal_height / 2.0)),
    )
    return pedestal


def _build_leaf(
    model: ArticulatedObject,
    r: ResolvedSpeedGateConfig,
    mats: dict,
    name: str,
    panel_mesh,
) -> Part:
    leaf = model.part(name)
    leaf.visual(
        Cylinder(radius=0.0105, length=r.leaf_height + 0.04),
        origin=Origin(xyz=(0.0, 0.0, r.leaf_height / 2.0)),
        material=mats["seal"], name="pivot_spindle", material_class_id="metal.steel_bare",
    )
    leaf.visual(
        Box((0.040, 0.026, r.leaf_height * 0.94)),
        origin=Origin(xyz=(0.030, 0.0, r.leaf_height / 2.0)),
        material=mats["edge"], name="panel_clamp", material_class_id="metal.stainless_matte",
    )
    leaf.visual(panel_mesh, material=mats["glass"], name="barrier_panel", material_class_id="glass.clear_transparent")
    for z, tag in ((0.04, "lower"), (r.leaf_height - 0.04, "upper")):
        leaf.visual(
            Box((0.048, 0.028, 0.038)), origin=Origin(xyz=(0.048, 0.0, z)),
            material=mats["shell"], name=f"{tag}_hinge_bracket", material_class_id=("metal.stainless_matte" if r.palette_style == "stainless_green" else "metal.paint_coated"),
        )
    leaf.inertial = Inertial.from_geometry(
        Box((r.leaf_reach, 0.03, r.leaf_height)), mass=5.5,
        origin=Origin(xyz=(r.leaf_reach / 2.0, 0.0, r.leaf_height / 2.0)),
    )
    return leaf


def _fix_pedestal(
    model: ArticulatedObject, frame: Part, pedestal: Part, r: ResolvedSpeedGateConfig, index: int
) -> None:
    model.articulation(
        f"frame_to_pedestal_{index}", ArticulationType.FIXED,
        parent=frame, child=pedestal,
        origin=Origin(xyz=(r.pedestal_x[index], 0.0, r.plate_height)),
        mating=MatingContract(
            parent_face_geometry="floor_plate", parent_face_side="positive_z",
            child_face_geometry="pedestal_body", child_face_side="negative_z",
            contact_tol=0.004, tangential_containment=True, tangential_tol=0.02,
        ),
    )


def _hinge_leaf(
    model: ArticulatedObject,
    pedestal: Part,
    leaf: Part,
    r: ResolvedSpeedGateConfig,
    name: str,
    side: float,
) -> None:
    side_tag = "right" if side > 0.0 else "left"
    yaw = 0.0 if side > 0.0 else math.pi
    axis_z = 1.0 if side > 0.0 else -1.0
    model.articulation(
        f"{name}_hinge", ArticulationType.REVOLUTE,
        parent=pedestal, child=leaf,
        origin=Origin(
            xyz=(side * (r.pedestal_half_width + r.socket_projection), 0.0, r.hinge_z),
            rpy=(0.0, 0.0, yaw),
        ),
        axis=(0.0, 0.0, axis_z),
        motion_limits=MotionLimits(effort=42.0, velocity=2.0, lower=0.0, upper=r.swing_angle),
        motion_properties=MotionProperties(damping=1.0, friction=0.16),
        mating=MatingContract(
            parent_face_geometry=f"spindle_thrust_{side_tag}",
            parent_face_side="positive_z",
            child_face_geometry="pivot_spindle", child_face_side="negative_z",
            contact_tol=0.001,
        ),
        meta={
            "mechanism": "captured vertical spindle swing",
            "positive_motion": "both opposed leaves open toward +Y passage direction",
        },
    )


def build_speed_gate(
    config: SpeedGateConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config or SpeedGateConfig())
    model = ArticulatedObject(
        name=r.name, assets=assets,
        meta={"category": "speed_gate", "mechanism_profile": "swing", "lane_count": r.lane_count},
    )
    mats = _materials(model, r)
    frame = _build_frame(model, r, mats)
    body_mesh = _pedestal_body_mesh(r)
    bearing_mesh = mesh_from_cadquery(
        _bearing_ring(), "speed_gate_spindle_bearing_ring", tolerance=0.0015
    )
    if r.barrier_form == "curved_glass":
        panel_solid = _curved_shell(r.leaf_reach - 0.034, r.leaf_height, r.leaf_thickness)
        panel_solid = panel_solid.translate((0.034, 0.0, 0.0))
    else:
        panel_solid = _flat_panel(r)
    panel_mesh = mesh_from_cadquery(
        panel_solid, f"speed_gate_{r.barrier_form}_panel", tolerance=0.0025
    )

    pedestals: list[Part] = []
    for index in range(r.pedestal_count):
        pedestal = _build_pedestal(model, r, mats, body_mesh, bearing_mesh, index)
        pedestals.append(pedestal)
        _fix_pedestal(model, frame, pedestal, r, index)

    for lane in range(r.lane_count):
        left_name = f"lane_{lane}_left_leaf"
        right_name = f"lane_{lane}_right_leaf"
        left = _build_leaf(model, r, mats, left_name, panel_mesh)
        right = _build_leaf(model, r, mats, right_name, panel_mesh)
        _hinge_leaf(model, pedestals[lane], left, r, left_name, 1.0)
        _hinge_leaf(model, pedestals[lane + 1], right, r, right_name, -1.0)
    return model


def build_seeded_speed_gate(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_speed_gate(config_from_seed(seed), assets=assets)


def _slot_choices_for_config(config: SpeedGateConfig) -> list[tuple[str, str]]:
    r = resolve_config(config)
    return [
        ("pedestal_form", r.pedestal_form),
        ("mechanism_profile", "swing_revolute"),
        ("barrier_form", r.barrier_form),
        ("reader_terminal", r.reader_terminal),
        ("lane_count", str(r.lane_count)),
        ("palette_style", r.palette_style),
    ]


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    return _slot_choices_for_config(config_from_seed(seed))


def _leaf_specs(r: ResolvedSpeedGateConfig) -> list[tuple[str, int, str]]:
    specs: list[tuple[str, int, str]] = []
    for lane in range(r.lane_count):
        specs.append((f"lane_{lane}_left_leaf", lane, "right"))
        specs.append((f"lane_{lane}_right_leaf", lane + 1, "left"))
    return specs


def run_speed_gate_tests(object_model: ArticulatedObject, config: SpeedGateConfig) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()

    ctx.check(
        "exact N+1 cabinets",
        all(object_model.get_part(f"pedestal_{i}") is not None for i in range(r.pedestal_count)),
        details=f"expected {r.pedestal_count} cabinets",
    )
    joints = [j for j in object_model.joints if j.joint_type == ArticulationType.REVOLUTE]
    ctx.check(
        "exact 2N independent swing joints",
        len(joints) == 2 * r.lane_count and len({j.child for j in joints}) == 2 * r.lane_count,
        details=f"expected={2 * r.lane_count}, actual={len(joints)}",
    )
    ctx.check(
        "bounded multiplicity domain",
        1 <= r.lane_count <= 5 and r.pedestal_count == r.lane_count + 1,
        details=f"N={r.lane_count}, pedestals={r.pedestal_count}",
    )
    ctx.check(
        "constant local-cell spacing equation",
        abs(r.lane_pitch - (2.0 * (r.pedestal_half_width + r.socket_projection + r.leaf_reach)
                            + r.anti_pinch_gap)) < 1e-9,
        details=f"pitch={r.lane_pitch:.4f}",
    )
    for lane in range(r.lane_count):
        left = object_model.get_part(f"lane_{lane}_left_leaf")
        right = object_model.get_part(f"lane_{lane}_right_leaf")
        ctx.expect_gap(
            right, left, axis="x", min_gap=0.014, max_gap=0.022,
            positive_elem="barrier_panel", negative_elem="barrier_panel",
            name=f"lane {lane} closed anti-pinch seam",
        )
        for leaf in (left, right):
            rgba = getattr(leaf.get_visual("barrier_panel").material, "rgba", None)
            ctx.check(
                f"{leaf.name} remains transparent", rgba is not None and rgba[3] < 0.6,
                details=f"rgba={rgba}",
            )

    # Full sampled collision coverage plus explicit closed/mid/max semantics.
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=64, ignore_fixed=True)
    for leaf_name, _host_index, _side_tag in _leaf_specs(r):
        leaf = object_model.get_part(leaf_name)
        joint = object_model.get_articulation(f"{leaf_name}_hinge")
        closed = ctx.part_element_world_aabb(leaf, elem="barrier_panel")
        with ctx.pose({joint: r.swing_angle / 2.0}):
            mid = ctx.part_element_world_aabb(leaf, elem="barrier_panel")
        with ctx.pose({joint: r.swing_angle}):
            opened = ctx.part_element_world_aabb(leaf, elem="barrier_panel")
        closed_y = (closed[0][1] + closed[1][1]) / 2.0 if closed else 0.0
        mid_y = (mid[0][1] + mid[1][1]) / 2.0 if mid else 0.0
        open_y = (opened[0][1] + opened[1][1]) / 2.0 if opened else 0.0
        ctx.check(
            f"{leaf_name} closed-mid-max swing opens toward passage",
            mid_y > closed_y + 0.05 and open_y > mid_y + 0.02,
            details=f"centers_y={(closed_y, mid_y, open_y)}",
        )
    return ctx.report()


__all__ = [
    "SpeedGateConfig", "ResolvedSpeedGateConfig", "PEDESTAL_FORMS", "BARRIER_FORMS",
    "READER_TERMINALS", "PALETTE_STYLES", "LANE_COUNTS", "config_from_seed",
    "resolve_config", "build_speed_gate", "build_seeded_speed_gate", "slot_choices_for_seed",
    "run_speed_gate_tests", "__modular__",
]
