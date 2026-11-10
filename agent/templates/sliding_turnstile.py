# SPDX-License-Identifier: Apache-2.0

"""Horizontal-retract sliding turnstile modular template.

The category has one honest motion spine: N lanes, N+1 hollow drive pedestals,
and two independently prismatic glass leaves per lane.  Static pedestal,
reader, guide, trim and foundation geometry is fused into ``floor_anchor``;
only complete gate leaves are separate moving parts.

Accepted sources and exact spans are recorded in
``articraft_template_authoring/specs_modular_v1/sliding_turnstile.md``.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Literal

import cadquery as cq

from sdk import (
    AppearanceOnlySpec,
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
    TestContext,
    TestReport,
    mesh_from_cadquery,
)

__modular__ = True


PedestalForm = Literal["capsule_hollow", "slim_capsule_hollow", "round_hollow"]
BarrierForm = Literal["rectangular", "waist_high", "full_height", "sloped_shoulder"]
ReaderModule = Literal["flush_sensor", "raised_biometric"]
PaletteStyle = Literal[
    "stainless_blue",
    "graphite_teal",
    "bronze_smoke",
    "white_green",
]

PEDESTAL_FORMS: tuple[PedestalForm, ...] = (
    "capsule_hollow",
    "slim_capsule_hollow",
    "round_hollow",
)
BARRIER_FORMS: tuple[BarrierForm, ...] = (
    "rectangular",
    "waist_high",
    "full_height",
    "sloped_shoulder",
)
READER_MODULES: tuple[ReaderModule, ...] = ("flush_sensor", "raised_biometric")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "stainless_blue",
    "graphite_teal",
    "bronze_smoke",
    "white_green",
)

LANE_COUNT_MIN = 2
LANE_COUNT_MAX = 6
LANE_COUNTS = tuple(range(LANE_COUNT_MIN, LANE_COUNT_MAX + 1))
LANE_COUNT_WEIGHTS = (0.30, 0.25, 0.20, 0.15, 0.10)

BODY_BOTTOM = 0.04
BODY_TOP = 0.96
CAP_TOP = 1.02
BASE_HOST_WIDTH = 0.34
CAPSULE_DEPTH = 0.82
SLIM_DEPTH = 0.68
ROUND_DIAMETER = 0.36
BASE_REACH = 0.295
HIDDEN_LENGTH = 0.018
CENTER_GAP = 0.020
PANEL_THICKNESS = 0.012
TRACK_Y = (-0.055, 0.055)
MOUTH_WIDTH = 0.036
GUIDE_THICKNESS = 0.004
# The named upper guide meets the 2 mm shoe-bearing face exactly: contact is
# structural, but there is no represented penetration and therefore no
# collision allowance.  The opposite guide retains 1 mm running clearance.
GUIDE_RUNNING_GAP = 0.001
SHOE_DEPTH = 0.018
SHOE_WIDTH = 0.026
SHELL_WALL = 0.025


PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "stainless_blue": {
        "floor": (0.08, 0.09, 0.10, 1.0),
        "shell": (0.62, 0.65, 0.66, 1.0),
        "cap": (0.78, 0.80, 0.81, 1.0),
        "trim": (0.88, 0.90, 0.91, 1.0),
        "guide": (0.035, 0.045, 0.055, 1.0),
        "glass": (0.68, 0.88, 0.94, 0.30),
        "reader": (0.055, 0.065, 0.075, 1.0),
        "screen": (0.02, 0.08, 0.13, 0.97),
        "status": (0.12, 0.88, 0.38, 1.0),
    },
    "graphite_teal": {
        "floor": (0.06, 0.07, 0.08, 1.0),
        "shell": (0.16, 0.18, 0.20, 1.0),
        "cap": (0.25, 0.28, 0.30, 1.0),
        "trim": (0.42, 0.47, 0.49, 1.0),
        "guide": (0.02, 0.025, 0.03, 1.0),
        "glass": (0.35, 0.82, 0.84, 0.34),
        "reader": (0.07, 0.08, 0.09, 1.0),
        "screen": (0.01, 0.08, 0.09, 0.97),
        "status": (0.12, 0.95, 0.78, 1.0),
    },
    "bronze_smoke": {
        "floor": (0.12, 0.095, 0.06, 1.0),
        "shell": (0.53, 0.39, 0.22, 1.0),
        "cap": (0.68, 0.52, 0.30, 1.0),
        "trim": (0.82, 0.66, 0.40, 1.0),
        "guide": (0.09, 0.065, 0.04, 1.0),
        "glass": (0.48, 0.44, 0.40, 0.34),
        "reader": (0.14, 0.11, 0.08, 1.0),
        "screen": (0.05, 0.035, 0.025, 0.97),
        "status": (0.94, 0.66, 0.18, 1.0),
    },
    "white_green": {
        "floor": (0.52, 0.54, 0.55, 1.0),
        "shell": (0.90, 0.92, 0.92, 1.0),
        "cap": (0.97, 0.98, 0.98, 1.0),
        "trim": (0.70, 0.74, 0.75, 1.0),
        "guide": (0.14, 0.16, 0.17, 1.0),
        "glass": (0.73, 0.92, 0.84, 0.29),
        "reader": (0.18, 0.20, 0.20, 1.0),
        "screen": (0.03, 0.09, 0.065, 0.97),
        "status": (0.20, 0.90, 0.42, 1.0),
    },
}


@dataclass(frozen=True)
class SlidingTurnstileConfig:
    pedestal_form: PedestalForm | None = None
    barrier_form: BarrierForm | None = None
    reader_module: ReaderModule | None = None
    palette_style: PaletteStyle | None = None
    lane_count: int | None = None
    lane_pitch_scale: float = 1.0
    host_height_scale: float = 1.0
    leaf_reach_scale: float = 1.0
    name: str = "sliding_turnstile"


@dataclass(frozen=True)
class BarrierDescriptor:
    form: BarrierForm
    bottom_z: float
    root_top_z: float
    tip_top_z: float
    shoulder_run: float
    reach: float
    hidden_length: float = HIDDEN_LENGTH
    thickness: float = PANEL_THICKNESS

    @property
    def total_length(self) -> float:
        return self.reach + self.hidden_length

    @property
    def root_spine_bottom(self) -> float:
        return self.bottom_z + 0.018

    @property
    def root_spine_top(self) -> float:
        return self.root_top_z - 0.018

    @property
    def root_spine_height(self) -> float:
        return self.root_spine_top - self.root_spine_bottom

    @property
    def root_spine_center_z(self) -> float:
        return (self.root_spine_bottom + self.root_spine_top) * 0.5

    @property
    def shoe_center_z(self) -> float:
        return max(self.bottom_z + 0.20, 0.26)


@dataclass(frozen=True)
class ResolvedSlidingTurnstileConfig:
    pedestal_form: PedestalForm
    barrier_form: BarrierForm
    reader_module: ReaderModule
    palette_style: PaletteStyle
    lane_count: int
    lane_pitch: float
    host_width: float
    host_depth: float
    host_height: float
    wall: float
    descriptor: BarrierDescriptor
    palette: dict[str, tuple[float, float, float, float]] = field(default_factory=dict)
    name: str = "sliding_turnstile"


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, float(value)))


def _choice(value, choices, default):
    return value if value in choices else default


def config_from_seed(seed: int) -> SlidingTurnstileConfig:
    """Unbounded deterministic procedural sampler; seed 0 is ordinary."""
    rng = random.Random(seed)
    pedestal_form = rng.choice(PEDESTAL_FORMS)
    allowed_barriers: tuple[BarrierForm, ...]
    if pedestal_form == "round_hollow":
        allowed_barriers = ("rectangular",)
    else:
        allowed_barriers = BARRIER_FORMS
    return SlidingTurnstileConfig(
        pedestal_form=pedestal_form,
        barrier_form=rng.choice(allowed_barriers),
        reader_module=rng.choice(READER_MODULES),
        palette_style=rng.choice(PALETTE_STYLES),
        lane_count=rng.choices(LANE_COUNTS, weights=LANE_COUNT_WEIGHTS, k=1)[0],
        lane_pitch_scale=round(rng.uniform(0.96, 1.08), 4),
        host_height_scale=round(rng.uniform(0.96, 1.06), 4),
        leaf_reach_scale=round(rng.uniform(0.94, 1.05), 4),
        name=f"seeded_sliding_turnstile_{seed}",
    )


def _barrier_descriptor(form: BarrierForm, reach: float) -> BarrierDescriptor:
    if form == "waist_high":
        return BarrierDescriptor(form, 0.42, 0.98, 0.98, 0.0, reach)
    if form == "full_height":
        return BarrierDescriptor(form, 0.06, 1.67, 1.67, 0.0, reach)
    if form == "sloped_shoulder":
        return BarrierDescriptor(form, 0.42, 1.67, 1.39, 0.140, reach)
    return BarrierDescriptor(form, 0.42, 1.67, 1.67, 0.0, reach)


def resolve_config(
    config: SlidingTurnstileConfig | None = None,
) -> ResolvedSlidingTurnstileConfig:
    cfg = config or SlidingTurnstileConfig()
    pedestal_form = _choice(cfg.pedestal_form, PEDESTAL_FORMS, "capsule_hollow")
    barrier_form = _choice(cfg.barrier_form, BARRIER_FORMS, "rectangular")
    reader_module = _choice(cfg.reader_module, READER_MODULES, "flush_sensor")
    palette_style = _choice(cfg.palette_style, PALETTE_STYLES, "stainless_blue")

    # Compatibility gate: the accepted round probe proves only the standard
    # leaf.  Do not silently expose the unchecked round×nonstandard product.
    if pedestal_form == "round_hollow" and barrier_form != "rectangular":
        raise ValueError(
            "round_hollow is gated to rectangular until a host-specific "
            "mouth/chord/swept-clearance probe accepts this barrier form"
        )

    lane_count = int(cfg.lane_count if cfg.lane_count is not None else 2)
    lane_count = int(_clamp(lane_count, LANE_COUNT_MIN, LANE_COUNT_MAX))
    reach = BASE_REACH * _clamp(cfg.leaf_reach_scale, 0.94, 1.05)
    height_scale = _clamp(cfg.host_height_scale, 0.96, 1.06)
    host_height = (BODY_TOP - BODY_BOTTOM) * height_scale

    if pedestal_form == "round_hollow":
        host_width = ROUND_DIAMETER
        host_depth = ROUND_DIAMETER
        wall = 0.014
    else:
        wall = SHELL_WALL if pedestal_form == "capsule_hollow" else 0.020
        # The cavity length is a relation: it grows just enough to contain the
        # resolved leaf at max travel instead of tuning travel to the shell.
        host_width = max(BASE_HOST_WIDTH, reach + HIDDEN_LENGTH + wall + 0.004)
        host_depth = CAPSULE_DEPTH if pedestal_form == "capsule_hollow" else SLIM_DEPTH

    lane_pitch_nominal = host_width + 2.0 * reach + CENTER_GAP
    lane_pitch = lane_pitch_nominal * _clamp(cfg.lane_pitch_scale, 0.96, 1.08)
    # Keep the true anti-pinch gap even at the low scale boundary.
    lane_pitch = max(lane_pitch, lane_pitch_nominal)

    descriptor = _barrier_descriptor(barrier_form, reach)
    usable_retract = host_width - wall - 0.002
    if descriptor.total_length > usable_retract:
        raise ValueError(
            f"leaf total length {descriptor.total_length:.4f} exceeds usable "
            f"host retract span {usable_retract:.4f}"
        )
    if 2.0 * abs(TRACK_Y[1]) < SHOE_DEPTH + 2.0 * GUIDE_THICKNESS + 0.020:
        raise ValueError("dual tracks do not have positive sibling clearance")

    return ResolvedSlidingTurnstileConfig(
        pedestal_form=pedestal_form,
        barrier_form=barrier_form,
        reader_module=reader_module,
        palette_style=palette_style,
        lane_count=lane_count,
        lane_pitch=lane_pitch,
        host_width=host_width,
        host_depth=host_depth,
        host_height=host_height,
        wall=wall,
        descriptor=descriptor,
        palette=dict(PALETTES[palette_style]),
        name=cfg.name or "sliding_turnstile",
    )


def slot_choices_for_config(
    config: SlidingTurnstileConfig | ResolvedSlidingTurnstileConfig,
) -> list[tuple[str, str]]:
    r = config if isinstance(config, ResolvedSlidingTurnstileConfig) else resolve_config(config)
    return [
        ("pedestal_form", r.pedestal_form),
        ("barrier_form", r.barrier_form),
        ("reader_module", r.reader_module),
        ("lane_count", f"n{r.lane_count}"),
        ("palette_style", r.palette_style),
    ]


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    return slot_choices_for_config(config_from_seed(seed))


def _capsule(width: float, depth: float, height: float, *, slim: bool = False):
    if slim:
        cap_rx = width * 0.5
        cap_ry = width * 0.38
        straight = max(depth - 2.0 * cap_ry, 0.002)
        body = cq.Workplane("XY").rect(width, straight).extrude(height)
        for sign in (-1.0, 1.0):
            body = body.union(
                cq.Workplane("XY")
                .center(0.0, sign * straight * 0.5)
                .ellipse(cap_rx, cap_ry)
                .extrude(height)
            )
        return body
    straight = max(depth - width, 0.002)
    body = cq.Workplane("XY").rect(width, straight).extrude(height)
    for sign in (-1.0, 1.0):
        body = body.union(
            cq.Workplane("XY")
            .center(0.0, sign * straight * 0.5)
            .circle(width * 0.5)
            .extrude(height)
        )
    return body


def _host_solid(
    r: ResolvedSlidingTurnstileConfig,
    width: float,
    depth: float,
    height: float,
):
    if r.pedestal_form == "round_hollow":
        return cq.Workplane("XY").circle(width * 0.5).extrude(height)
    return _capsule(
        width,
        depth,
        height,
        slim=r.pedestal_form == "slim_capsule_hollow",
    )


def _translated(shape, z: float):
    return shape.translate((0.0, 0.0, z))


def _body_top(r: ResolvedSlidingTurnstileConfig) -> float:
    """Resolved shell top shared by every host-dependent consumer."""
    return BODY_BOTTOM + r.host_height


def _cap_top(r: ResolvedSlidingTurnstileConfig) -> float:
    """Resolved cap top; the nominal 60 mm cap height stays invariant."""
    return _body_top(r) + (CAP_TOP - BODY_TOP)


def _pedestal_shell_wp(
    r: ResolvedSlidingTurnstileConfig,
    tracks: tuple[tuple[int, float], ...],
):
    body_top = _body_top(r)
    outer = _translated(_host_solid(r, r.host_width, r.host_depth, r.host_height), BODY_BOTTOM)
    inner_w = r.host_width - 2.0 * r.wall
    inner_d = r.host_depth - 2.0 * r.wall
    inner_bottom = (
        BODY_BOTTOM + 0.010
        if r.descriptor.form == "full_height"
        else BODY_BOTTOM + r.wall
    )
    inner = _translated(
        _host_solid(r, inner_w, inner_d, body_top - inner_bottom + 0.020),
        inner_bottom,
    )
    shell = outer.cut(inner)
    cut_bottom = max(BODY_BOTTOM + 0.004, r.descriptor.bottom_z - 0.014)
    cut_height = body_top - cut_bottom + 0.018
    for side_sign, track_y in tracks:
        mouth = (
            cq.Workplane("XY")
            .box(2.0 * r.wall + 0.030, MOUTH_WIDTH, cut_height)
            .translate(
                (
                    side_sign * (r.host_width * 0.5 - r.wall * 0.5),
                    track_y,
                    cut_bottom + cut_height * 0.5,
                )
            )
        )
        shell = shell.cut(mouth)
    return shell


def _top_cap_wp(
    r: ResolvedSlidingTurnstileConfig,
    tracks: tuple[tuple[int, float], ...],
):
    body_top = _body_top(r)
    cap_h = _cap_top(r) - body_top
    cap = _translated(_host_solid(r, r.host_width, r.host_depth, cap_h), body_top)
    for _, track_y in tracks:
        slot = (
            cq.Workplane("XY")
            .box(r.host_width + 0.040, MOUTH_WIDTH, cap_h + 0.020)
            .translate((0.0, track_y, body_top + cap_h * 0.5))
        )
        cap = cap.cut(slot)
    return cap


def _trim_ring_wp(
    r: ResolvedSlidingTurnstileConfig,
    tracks: tuple[tuple[int, float], ...],
):
    z0 = _body_top(r) - 0.035
    h = 0.008
    outer = _translated(_host_solid(r, r.host_width + 0.002, r.host_depth + 0.002, h), z0)
    inner = _translated(_host_solid(r, r.host_width - 0.012, r.host_depth - 0.012, h + 0.006), z0 - 0.003)
    ring = outer.cut(inner)
    for _, track_y in tracks:
        ring = ring.cut(
            cq.Workplane("XY")
            .box(r.host_width + 0.040, MOUTH_WIDTH + 0.002, h + 0.018)
            .translate((0.0, track_y, z0 + h * 0.5))
        )
    return ring


def _foot_wp(r: ResolvedSlidingTurnstileConfig):
    return _host_solid(r, r.host_width + 0.020, r.host_depth + 0.020, BODY_BOTTOM)


def _panel_points(d: BarrierDescriptor, direction: int) -> list[tuple[float, float]]:
    root_x = -direction * d.hidden_length
    tip_x = direction * d.reach
    if d.form == "sloped_shoulder":
        shoulder_x = direction * (d.reach - d.shoulder_run)
        if direction > 0:
            return [
                (root_x, d.bottom_z),
                (tip_x, d.bottom_z),
                (tip_x, d.tip_top_z),
                (shoulder_x, d.root_top_z),
                (root_x, d.root_top_z),
            ]
        return [
            (root_x, d.bottom_z),
            (root_x, d.root_top_z),
            (shoulder_x, d.root_top_z),
            (tip_x, d.tip_top_z),
            (tip_x, d.bottom_z),
        ]
    if direction > 0:
        return [
            (root_x, d.bottom_z),
            (tip_x, d.bottom_z),
            (tip_x, d.root_top_z),
            (root_x, d.root_top_z),
        ]
    return [
        (root_x, d.bottom_z),
        (root_x, d.root_top_z),
        (tip_x, d.root_top_z),
        (tip_x, d.bottom_z),
    ]


def _panel_wp(d: BarrierDescriptor, direction: int):
    panel = (
        cq.Workplane("XZ")
        .polyline(_panel_points(d, direction))
        .close()
        .extrude(d.thickness * 0.5, both=True)
    )
    try:
        panel = panel.edges("|Y").fillet(0.014)
    except Exception:
        # OCC can reject a fillet at a very short sloped shoulder after scale
        # projection; the sourced polygon primitive remains intact.
        pass
    return panel


def _track_layout(lane_count: int) -> list[tuple[tuple[int, float], ...]]:
    result: list[tuple[tuple[int, float], ...]] = []
    for host_i in range(lane_count + 1):
        tracks: list[tuple[int, float]] = []
        if host_i > 0:
            tracks.append((-1, TRACK_Y[(host_i - 1) % 2]))
        if host_i < lane_count:
            tracks.append((1, TRACK_Y[host_i % 2]))
        result.append(tuple(tracks))
    return result


def _host_x_positions(r: ResolvedSlidingTurnstileConfig) -> list[float]:
    return [
        (i - r.lane_count * 0.5) * r.lane_pitch
        for i in range(r.lane_count + 1)
    ]


def _reader_y(r: ResolvedSlidingTurnstileConfig) -> float:
    if r.pedestal_form == "round_hollow":
        return -0.130
    return -r.host_depth * 0.5 + 0.120


def _emit_reader(root, r: ResolvedSlidingTurnstileConfig, mats, x: float, index: int) -> None:
    y = _reader_y(r)
    cap_top = _cap_top(r)
    if r.reader_module == "flush_sensor":
        root.visual(
            Cylinder(radius=0.034, length=0.006),
            origin=Origin(xyz=(x, y, cap_top - 0.001)),
            material=mats["reader"],
            name=f"reader_{index}_flush_pad", material_class_id="tech.control_interface",
        )
        root.visual(
            Box((0.048, 0.014, 0.008)),
            origin=Origin(xyz=(x, y - 0.018, cap_top + 0.002)),
            material=mats["status"],
            name=f"reader_{index}_status_strip", appearance_only=AppearanceOnlySpec(kind="overlay"),
        )
        return

    plinth_w = 0.100 if r.pedestal_form == "round_hollow" else 0.145
    plinth_d = 0.050 if r.pedestal_form == "round_hollow" else 0.090
    plinth_h = 0.040
    body_w = plinth_w * 0.90
    body_d = plinth_d * 0.78
    body_h = 0.150
    root.visual(
        Box((plinth_w, plinth_d, plinth_h)),
        origin=Origin(xyz=(x, y, cap_top + plinth_h * 0.5 - 0.001)),
        material=mats["reader"],
        name=f"reader_{index}_plinth", material_class_id="metal.paint_coated",
    )
    body_z = cap_top + plinth_h + body_h * 0.5 - 0.002
    root.visual(
        Box((body_w, body_d, body_h)),
        origin=Origin(xyz=(x, y, body_z)),
        material=mats["reader"],
        name=f"reader_{index}_body", material_class_id="metal.paint_coated",
    )
    front_y = y - body_d * 0.5 - 0.001
    root.visual(
        Box((body_w * 0.72, 0.006, body_h * 0.50)),
        origin=Origin(xyz=(x, front_y, body_z + 0.006)),
        material=mats["screen"],
        name=f"reader_{index}_biometric_screen", material_class_id="tech.control_interface",
    )
    root.visual(
        Cylinder(radius=0.007, length=0.006),
        origin=Origin(xyz=(x, front_y - 0.001, body_z + body_h * 0.36), rpy=(1.5708, 0.0, 0.0)),
        material=mats["guide"],
        name=f"reader_{index}_camera_aperture", material_class_id="glass.smoked_tinted",
    )
    root.visual(
        Box((0.040, 0.006, 0.009)),
        origin=Origin(xyz=(x, front_y, body_z - body_h * 0.34)),
        material=mats["status"],
        name=f"reader_{index}_status_light", appearance_only=AppearanceOnlySpec(kind="emission", emission_strength=1.0),
    )


def _emit_root(
    model: ArticulatedObject,
    r: ResolvedSlidingTurnstileConfig,
    mats,
    assets,
):
    root = model.part("floor_anchor", meta={"role": "foundation and hollow drive hosts"})
    host_x = _host_x_positions(r)
    tracks_by_host = _track_layout(r.lane_count)
    plate_w = r.lane_count * r.lane_pitch + r.host_width + 0.12
    plate_d = r.host_depth + 0.16
    root.visual(
        Box((plate_w, plate_d, 0.024)),
        origin=Origin(xyz=(0.0, 0.0, -0.012)),
        material=mats["floor"],
        name="installation_plate", material_class_id="metal.paint_coated",
    )

    mesh_cache: dict[tuple[tuple[int, float], ...], tuple[object, object, object]] = {}
    foot_mesh = mesh_from_cadquery(
        _foot_wp(r),
        f"{r.pedestal_form}_foot",
        tolerance=0.0018,
        angular_tolerance=0.15,
        assets=assets,
    )
    # Each rail crosses the cavity and embeds 5 mm into both side walls.  The
    # active mouth removes one local wall patch, while the opposite endpoint
    # remains physically seated in the shell instead of merely sharing a
    # coincident tessellated face.
    inner_span = r.host_width - 2.0 * r.wall + 0.010
    rail_z = r.descriptor.shoe_center_z
    rail_h = min(0.34, max(0.20, r.descriptor.root_spine_height * 0.42))

    for host_i, (x, tracks) in enumerate(zip(host_x, tracks_by_host)):
        if tracks not in mesh_cache:
            mesh_cache[tracks] = (
                mesh_from_cadquery(
                    _pedestal_shell_wp(r, tracks),
                    f"{r.pedestal_form}_shell_{len(mesh_cache)}",
                    tolerance=0.0018,
                    angular_tolerance=0.15,
                    assets=assets,
                ),
                mesh_from_cadquery(
                    _top_cap_wp(r, tracks),
                    f"{r.pedestal_form}_cap_{len(mesh_cache)}",
                    tolerance=0.0018,
                    angular_tolerance=0.15,
                    assets=assets,
                ),
                mesh_from_cadquery(
                    _trim_ring_wp(r, tracks),
                    f"{r.pedestal_form}_trim_{len(mesh_cache)}",
                    tolerance=0.0015,
                    angular_tolerance=0.15,
                    assets=assets,
                ),
            )
        shell_mesh, cap_mesh, trim_mesh = mesh_cache[tracks]
        root.visual(foot_mesh, origin=Origin(xyz=(x, 0.0, 0.0)), material=mats["floor"], name=f"pedestal_{host_i}_foot", material_class_id="metal.paint_coated")
        root.visual(shell_mesh, origin=Origin(xyz=(x, 0.0, 0.0)), material=mats["shell"], name=f"pedestal_{host_i}_shell", material_class_id=("metal.paint_coated" if r.palette_style in {"stainless_blue", "graphite_teal", "white_green"} else "metal.bronze_cast"))
        root.visual(cap_mesh, origin=Origin(xyz=(x, 0.0, 0.0)), material=mats["cap"], name=f"pedestal_{host_i}_top_cap", material_class_id=("metal.paint_coated" if r.palette_style in {"graphite_teal", "bronze_smoke", "white_green"} else "metal.aluminum_bare"))
        root.visual(trim_mesh, origin=Origin(xyz=(x, 0.0, 0.0)), material=mats["trim"], name=f"pedestal_{host_i}_trim_ring", material_class_id=("metal.paint_coated" if r.palette_style in {"stainless_blue", "graphite_teal", "white_green"} else "metal.brass_polished"))

        for track_i, (_, track_y) in enumerate(tracks):
            for y_sign, side_name in ((-1, "lower"), (1, "upper")):
                rail_y = track_y + y_sign * (
                    SHOE_DEPTH * 0.5 + GUIDE_RUNNING_GAP + GUIDE_THICKNESS * 0.5
                )
                root.visual(
                    Box((inner_span, GUIDE_THICKNESS, rail_h)),
                    origin=Origin(xyz=(x, rail_y, rail_z)),
                    material=mats["guide"],
                    name=f"pedestal_{host_i}_track_{track_i}_guide_{side_name}", material_class_id="metal.blackened_gunmetal",
                )

        # Service seam is host-conformal and stays below all mouth bottoms.
        root.visual(
            Box((r.host_width * 0.52, 0.006, 0.022)),
            origin=Origin(xyz=(x, -r.host_depth * 0.5 + 0.002, 0.24)),
            material=mats["guide"],
            name=f"pedestal_{host_i}_service_seam", material_class_id="metal.blackened_gunmetal",
        )
        _emit_reader(root, r, mats, x, host_i)

    root.inertial = Inertial.from_geometry(
        Box((plate_w, plate_d, BODY_BOTTOM + r.host_height)),
        mass=120.0 + 25.0 * r.lane_count,
        origin=Origin(xyz=(0.0, 0.0, (BODY_BOTTOM + r.host_height) * 0.5)),
    )
    return root, host_x, tracks_by_host


def _gate_track_index(
    tracks: tuple[tuple[int, float], ...],
    side_sign: int,
    track_y: float,
) -> int:
    for idx, (candidate_side, candidate_y) in enumerate(tracks):
        if candidate_side == side_sign and abs(candidate_y - track_y) < 1e-9:
            return idx
    raise ValueError("gate track descriptor missing from host")


def _emit_gates(
    model: ArticulatedObject,
    root,
    r: ResolvedSlidingTurnstileConfig,
    mats,
    assets,
    host_x: list[float],
    tracks_by_host: list[tuple[tuple[int, float], ...]],
) -> list[str]:
    panel_meshes = {
        direction: mesh_from_cadquery(
            _panel_wp(r.descriptor, direction),
            f"{r.barrier_form}_panel_{'pos' if direction > 0 else 'neg'}",
            tolerance=0.0012,
            angular_tolerance=0.12,
            assets=assets,
        )
        for direction in (-1, 1)
    }
    names: list[str] = []
    for lane in range(r.lane_count):
        track_y = TRACK_Y[lane % 2]
        for side, (host_i, direction) in enumerate(((lane, 1), (lane + 1, -1))):
            name = f"gate_{lane}_{side}"
            names.append(name)
            gate = model.part(
                name,
                meta={
                    "role": "complete horizontally retracting barrier leaf",
                    "barrier_form": r.barrier_form,
                    "host_index": host_i,
                },
            )
            gate.visual(panel_meshes[direction], material=mats["glass"], name="glass", material_class_id="glass.smoked_tinted")
            gate.visual(
                Box((0.028, 0.020, r.descriptor.root_spine_height)),
                origin=Origin(
                    xyz=(
                        -direction * 0.006,
                        0.0,
                        r.descriptor.root_spine_center_z,
                    )
                ),
                material=mats["trim"],
                name="root_spine", material_class_id=("metal.paint_coated" if r.palette_style in {"stainless_blue", "graphite_teal", "white_green"} else "metal.brass_aged"),
            )
            gate.visual(
                Box((SHOE_WIDTH, SHOE_DEPTH, min(0.30, r.descriptor.root_spine_height * 0.52))),
                origin=Origin(xyz=(-direction * 0.004, 0.0, r.descriptor.shoe_center_z)),
                material=mats["trim"],
                name="drive_shoe", material_class_id="metal.steel_bare",
            )
            gate.visual(
                Box((SHOE_WIDTH * 0.82, 0.002, min(0.26, r.descriptor.root_spine_height * 0.45))),
                origin=Origin(
                    xyz=(
                        -direction * 0.004,
                        SHOE_DEPTH * 0.5,
                        r.descriptor.shoe_center_z,
                    )
                ),
                material=mats["trim"],
                name="shoe_bearing", material_class_id="metal.steel_bare",
            )
            gate.inertial = Inertial.from_geometry(
                Box((r.descriptor.total_length, 0.030, r.descriptor.root_top_z - r.descriptor.bottom_z)),
                mass=9.0,
                origin=Origin(
                    xyz=(
                        direction * (r.descriptor.reach - r.descriptor.hidden_length) * 0.5,
                        0.0,
                        (r.descriptor.bottom_z + r.descriptor.root_top_z) * 0.5,
                    )
                ),
            )

            side_sign = direction
            track_index = _gate_track_index(tracks_by_host[host_i], side_sign, track_y)
            joint_x = host_x[host_i] + direction * r.host_width * 0.5
            parent_guide = f"pedestal_{host_i}_track_{track_index}_guide_upper"
            limits = MotionLimits(
                effort=180.0,
                velocity=0.65,
                lower=0.0,
                upper=r.descriptor.reach,
            )
            model.articulation(
                f"{name}_slide",
                ArticulationType.PRISMATIC,
                parent=root,
                child=gate,
                origin=Origin(xyz=(joint_x, track_y, 0.0)),
                axis=(-float(direction), 0.0, 0.0),
                motion_limits=limits,
                motion_properties=MotionProperties(damping=18.0, friction=5.0),
                mating=MatingContract(
                    parent_face_geometry=parent_guide,
                    parent_face_side="negative_y",
                    child_face_geometry="shoe_bearing",
                    child_face_side="positive_y",
                    contact_tol=0.0025,
                ),
                meta={
                    "mechanism": "horizontal retract into hollow dual-guide host",
                    "positive_motion": "retracts from lane toward host cavity",
                },
            )
    return names


def build_sliding_turnstile(
    config: SlidingTurnstileConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={
            "category": "sliding_turnstile",
            "mechanism_profile": "horizontal_retract",
            "lane_count": r.lane_count,
        },
    )
    mats = {
        key: model.material(f"{r.palette_style}_{key}", rgba=rgba)
        for key, rgba in r.palette.items()
    }
    root, host_x, tracks_by_host = _emit_root(model, r, mats, assets)
    _emit_gates(model, root, r, mats, assets, host_x, tracks_by_host)
    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_sliding_turnstile(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_sliding_turnstile(config_from_seed(seed), assets=assets)


def run_sliding_turnstile_tests(
    object_model: ArticulatedObject,
    config: SlidingTurnstileConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    part_names = {part.name for part in object_model.parts}
    joints = [
        joint
        for joint in object_model.articulations
        if joint.articulation_type != ArticulationType.FIXED
    ]
    gate_names = [f"gate_{lane}_{side}" for lane in range(r.lane_count) for side in range(2)]
    root = object_model.get_part("floor_anchor")

    ctx.check(
        "single grounded root",
        len(object_model.root_parts()) == 1 and object_model.root_parts()[0].name == "floor_anchor",
        details=f"roots={[p.name for p in object_model.root_parts()]}",
    )
    ctx.check(
        "host and gate multiplicity follows N",
        all(name in part_names for name in gate_names)
        and len(part_names) == 1 + 2 * r.lane_count
        and len(joints) == 2 * r.lane_count,
        details=f"N={r.lane_count}, parts={sorted(part_names)}, joints={[j.name for j in joints]}",
    )
    ctx.check(
        "horizontal retract only",
        all(
            joint.articulation_type == ArticulationType.PRISMATIC
            and tuple(round(float(v), 6) for v in joint.axis) in {(-1.0, 0.0, 0.0), (1.0, 0.0, 0.0)}
            for joint in joints
        ),
        details=str([(j.name, j.articulation_type, j.axis) for j in joints]),
    )

    root_visual_names = {visual.name for visual in root.visuals}
    for host_i, tracks in enumerate(_track_layout(r.lane_count)):
        ctx.check(
            f"pedestal {host_i} is a complete hollow host",
            {
                f"pedestal_{host_i}_foot",
                f"pedestal_{host_i}_shell",
                f"pedestal_{host_i}_top_cap",
                f"pedestal_{host_i}_trim_ring",
            }.issubset(root_visual_names),
        )
        ctx.check(
            f"pedestal {host_i} track cardinality",
            len(tracks) == (1 if host_i in (0, r.lane_count) else 2)
            and all(
                f"pedestal_{host_i}_track_{track_i}_guide_{side_name}" in root_visual_names
                for track_i in range(len(tracks))
                for side_name in ("lower", "upper")
            ),
            details=f"tracks={tracks}",
        )
        if 0 < host_i < r.lane_count:
            ctx.check(
                f"pedestal {host_i} uses two separated depth tracks",
                abs(tracks[1][1] - tracks[0][1])
                >= SHOE_DEPTH + 2.0 * GUIDE_THICKNESS + 0.020,
                details=f"tracks={tracks}",
            )

        reader_prefix = f"reader_{host_i}_"
        reader_names = {name for name in root_visual_names if name.startswith(reader_prefix)}
        if r.reader_module == "raised_biometric":
            required = {
                f"reader_{host_i}_plinth",
                f"reader_{host_i}_body",
                f"reader_{host_i}_biometric_screen",
                f"reader_{host_i}_camera_aperture",
                f"reader_{host_i}_status_light",
            }
        else:
            required = {f"reader_{host_i}_flush_pad", f"reader_{host_i}_status_strip"}
        ctx.check(
            f"pedestal {host_i} reader module is complete",
            required.issubset(reader_names),
            details=f"reader_visuals={sorted(reader_names)}",
        )

    for name in gate_names:
        gate = object_model.get_part(name)
        visual_names = {visual.name for visual in gate.visuals}
        ctx.check(
            f"{name} is a complete moving leaf",
            {"glass", "root_spine", "drive_shoe", "shoe_bearing"}.issubset(visual_names),
            details=f"visuals={sorted(visual_names)}",
        )
        glass_bounds = ctx.part_element_world_aabb(gate, elem="glass")
        ctx.check(
            f"{name} uses the selected barrier profile",
            glass_bounds is not None
            and glass_bounds[1][2] - glass_bounds[0][2]
            >= r.descriptor.tip_top_z - r.descriptor.bottom_z - 0.006,
            details=f"form={r.barrier_form}, bounds={glass_bounds}",
        )

    # Closed-pose pairs retain a real anti-pinch gap.
    for lane in range(r.lane_count):
        ctx.expect_gap(
            object_model.get_part(f"gate_{lane}_1"),
            object_model.get_part(f"gate_{lane}_0"),
            axis="x",
            min_gap=0.014,
            name=f"lane {lane} closed center gap",
        )

    closed_positions = {
        name: ctx.part_world_position(object_model.get_part(name)) for name in gate_names
    }
    pose_mid = {joint: r.descriptor.reach * 0.5 for joint in joints}
    pose_max = {joint: r.descriptor.reach for joint in joints}
    with ctx.pose(pose_mid):
        for lane in range(r.lane_count):
            ctx.expect_gap(
                object_model.get_part(f"gate_{lane}_1"),
                object_model.get_part(f"gate_{lane}_0"),
                axis="x",
                min_gap=r.descriptor.reach * 0.80,
                name=f"lane {lane} opens at mid travel",
            )

    with ctx.pose(pose_max):
        max_positions = {
            name: ctx.part_world_position(object_model.get_part(name)) for name in gate_names
        }
        for lane in range(r.lane_count):
            ctx.expect_gap(
                object_model.get_part(f"gate_{lane}_1"),
                object_model.get_part(f"gate_{lane}_0"),
                axis="x",
                min_gap=2.0 * r.descriptor.reach - 0.030,
                name=f"lane {lane} clears at max travel",
            )

    for lane in range(r.lane_count):
        for side, expected_sign in ((0, -1.0), (1, 1.0)):
            name = f"gate_{lane}_{side}"
            closed = closed_positions[name]
            opened = max_positions[name]
            delta_x = None if closed is None or opened is None else opened[0] - closed[0]
            ctx.check(
                f"{name} retracts toward its own host",
                delta_x is not None and expected_sign * delta_x >= r.descriptor.reach - 0.002,
                details=f"closed={closed}, max={opened}, delta_x={delta_x}",
            )

    # Rule 5: every joint is sampled at 0/mid/max.  The guide/bearing face is
    # modeled as exact zero-penetration contact, so no collision allowance is
    # needed at either element or whole-part scope.
    ctx.fail_if_parts_overlap_in_sampled_poses(
        max_pose_samples=min(128, max(32, 1 + 4 * len(joints))),
        ignore_fixed=True,
    )
    return ctx.report()


def run_tests(
    object_model: ArticulatedObject,
    config: SlidingTurnstileConfig,
) -> TestReport:
    return run_sliding_turnstile_tests(object_model, config)


Config = SlidingTurnstileConfig
build = build_sliding_turnstile
build_seeded = build_seeded_sliding_turnstile


__all__ = [
    "SlidingTurnstileConfig",
    "ResolvedSlidingTurnstileConfig",
    "config_from_seed",
    "resolve_config",
    "slot_choices_for_seed",
    "slot_choices_for_config",
    "build_sliding_turnstile",
    "build_seeded_sliding_turnstile",
    "run_sliding_turnstile_tests",
    "run_tests",
    "Config",
    "build",
    "build_seeded",
    "__modular__",
]
