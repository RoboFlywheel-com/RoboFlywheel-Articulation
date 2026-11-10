# SPDX-License-Identifier: Apache-2.0

# ruff: noqa: E501
"""Self-contained piano bench template (TEMPLATE_DOMAIN).

Rebuilt from the twelve `piano_bench` source assets (three origin anchors plus
nine single-axis fork variants).  The recognizable identity is a wide bench seat
carried on a grounded frame with a **real height-adjustment mechanism**:

  * ``support_frame``  — grounded leg family (slot ``support_frame``) that always
    presents the same frame-top plane and the same transverse drive axis.
  * ``seat``           — PRISMATIC +Z height carriage carrying the seat board and,
    for the storage candidate, the rabbeted storage box.
  * ``height_control`` — one or two REVOLUTE rotary controls (handwheel, spindle
    wheel, or twin side knobs) plus the candidate's lifting linkage.
  * ``seat_lid``       — REVOLUTE −X rear-edge storage lid (storage candidate only).

Height adjustment is the category's core mechanism, so every reachable
configuration carries at least two movable joints: one rotary control and the
seat lift.  The previous template made the storage lid the only articulation
source, so seeds sampling the no-lid candidate exported rigid bodies; that is
structurally impossible here and is also gated mechanically by preflight
(`rigid_candidate_no_movable_joint`) and the sweep/export rigid-seed check.

Every revolute/prismatic joint is built from ``mate_axes`` and registered with
``register_interface_mate``.  No source runtime, snapshot, or other template is
imported; geometry uses only the SDK.
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
    AxisInterface,
    Box,
    Cylinder,
    MotionLimits,
    MotionProperties,
    Origin,
    TemplateDomain,
    TestContext,
    TestReport,
    component_slot,
    corner_case,
    mate_axes,
    register_interface_mate,
)

__modular__ = True

# ---------------------------------------------------------------------------
# Slot value spaces
# ---------------------------------------------------------------------------
SupportFrame = Literal["four_leg_apron", "twin_pedestal", "folding_x_frame"]
SeatForm = Literal["rectangle_padded", "round_stool"]
HeightMechanism = Literal[
    "side_handwheel_yoke", "central_spindle", "twin_side_knobs", "scissor_lift"
]
Storage = Literal["plain_apron", "hinged_lid_box"]
PaletteStyle = Literal["black_lacquer", "walnut_vinyl", "ebony_leather", "grey_steel"]

SUPPORT_FRAMES: tuple[SupportFrame, ...] = (
    "four_leg_apron",
    "twin_pedestal",
    "folding_x_frame",
)
SEAT_FORMS: tuple[SeatForm, ...] = ("rectangle_padded", "round_stool")
HEIGHT_MECHANISMS: tuple[HeightMechanism, ...] = (
    "side_handwheel_yoke",
    "central_spindle",
    "twin_side_knobs",
    "scissor_lift",
)
STORAGES: tuple[Storage, ...] = ("plain_apron", "hinged_lid_box")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "black_lacquer",
    "walnut_vinyl",
    "ebony_leather",
    "grey_steel",
)

TEMPLATE_DOMAIN = TemplateDomain(
    slots=(
        component_slot("support_frame", SUPPORT_FRAMES, role="grounded bench leg family"),
        component_slot("seat_form", SEAT_FORMS, role="seat plan form and cushion"),
        component_slot(
            "height_mechanism", HEIGHT_MECHANISMS, role="rotary height-adjustment mechanism"
        ),
        component_slot("storage", STORAGES, role="under-seat storage construction"),
    )
)

# ---------------------------------------------------------------------------
# Palettes
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "black_lacquer": {
        "frame": (0.030, 0.031, 0.035, 1.0),
        "frame_edge": (0.075, 0.077, 0.082, 1.0),
        "cushion": (0.045, 0.046, 0.050, 1.0),
    },
    "walnut_vinyl": {
        "frame": (0.255, 0.150, 0.085, 1.0),
        "frame_edge": (0.350, 0.215, 0.125, 1.0),
        "cushion": (0.115, 0.085, 0.070, 1.0),
    },
    "ebony_leather": {
        "frame": (0.055, 0.048, 0.045, 1.0),
        "frame_edge": (0.105, 0.092, 0.085, 1.0),
        "cushion": (0.135, 0.100, 0.075, 1.0),
    },
    "grey_steel": {
        "frame": (0.230, 0.235, 0.240, 1.0),
        "frame_edge": (0.320, 0.325, 0.330, 1.0),
        "cushion": (0.090, 0.092, 0.098, 1.0),
    },
}
_HARDWARE: dict[str, tuple[float, float, float, float]] = {
    "steel": (0.420, 0.435, 0.445, 1.0),
    "dark_steel": (0.135, 0.140, 0.148, 1.0),
    "rubber": (0.022, 0.022, 0.025, 1.0),
    "felt": (0.085, 0.088, 0.092, 1.0),
}

# ---------------------------------------------------------------------------
# Shared construction constants (world metres, +Z up, +Y rear, X width).
# Every support candidate builds up to the same frame-top plane and the same
# transverse drive axis, so every height mechanism mounts identically.
# ---------------------------------------------------------------------------
BOARD_T = 0.018          # seat board thickness
CUSHION_T = 0.058        # cushion stack above the board
SEAT_STACK = BOARD_T + CUSHION_T
RAIL_T = 0.034           # frame top rail section
RAIL_DROP = 0.052        # drive axis clears the RAIL_T top rail plus the shaft radius
LEG_SECTION = 0.044      # nominal square leg section
FOOT_T = 0.012
WALL_T = 0.018           # storage box wall
SEAT_CLEAR = 0.006       # gap between frame top and the seat underside at lift=0
MECH_CLEAR = 0.022       # linkage pivot drop: clears the drive shaft above it
ARM_SWING = 0.42         # yoke / scissor travel (rad), from source 002
KNOB_TRAVEL = 18.0       # rotary control travel (rad), from source 002
SPINDLE_TRAVEL = 24.0    # central spindle travel (rad)

GUIDE_X = 0.045          # seat guide-post half-track (inboard of every mechanism)
GUIDE_POST = 0.026       # square guide-post section
GUIDE_PLATE_T = 0.010    # frame guide-plate thickness
GUIDE_POST_LEN = 0.140   # post length: stays engaged across the whole travel

SIDES: tuple[tuple[str, float], ...] = (("0", -1.0), ("1", 1.0))


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, float(value)))


def _pick(value, choices):
    return value if value in choices else choices[0]


# ---------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------
def _box(part, size, xyz, material, name, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(Box(size), origin=Origin(xyz=xyz, rpy=rpy), material=material, name=name, material_class_id="metal.generic_plain")


def _cyl(part, radius, length, xyz, material, name, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=Origin(xyz=xyz, rpy=rpy),
        material=material,
        name=name, material_class_id="metal.generic_plain",
    )


def _beam(part, p0, p1, section, material, name) -> None:
    """One straight box beam spanning p0..p1 (used for splayed/crossed legs).

    The box's local +Z is aligned with the full 3-D span, so a beam that leans in
    Y (the crossed X legs) keeps its real endpoints instead of being emitted as an
    over-long vertical box.
    """
    dx, dy, dz = (p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2])
    length = math.sqrt(dx * dx + dy * dy + dz * dz)
    mid = ((p0[0] + p1[0]) / 2.0, (p0[1] + p1[1]) / 2.0, (p0[2] + p1[2]) / 2.0)
    pitch = math.acos(max(-1.0, min(1.0, dz / length))) if length > 1e-9 else 0.0
    yaw = math.atan2(dy, dx) if (abs(dx) > 1e-12 or abs(dy) > 1e-12) else 0.0
    part.visual(
        Box((section, section, length)),
        origin=Origin(xyz=mid, rpy=(0.0, pitch, yaw)),
        material=material,
        name=name, material_class_id="metal.generic_plain",
    )


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Config:
    support_frame: SupportFrame = "four_leg_apron"
    seat_form: SeatForm = "rectangle_padded"
    height_mechanism: HeightMechanism = "side_handwheel_yoke"
    storage: Storage = "plain_apron"
    seat_width_m: float = 0.560
    seat_depth_m: float = 0.320
    seat_height_m: float = 0.470
    lift_travel_m: float = 0.055
    leg_taper_ratio: float = 0.78
    storage_depth_m: float = 0.115
    lid_open_rad: float = 1.35
    palette_style: PaletteStyle = "black_lacquer"
    name: str = "piano_bench"


@dataclass(frozen=True)
class ResolvedConfig:
    support_frame: SupportFrame
    seat_form: SeatForm
    height_mechanism: HeightMechanism
    storage: Storage
    seat_width_m: float
    seat_depth_m: float
    seat_height_m: float
    lift_travel_m: float
    leg_taper_ratio: float
    storage_depth_m: float
    lid_open_rad: float
    palette_style: PaletteStyle
    name: str

    # -- derived plan profile (one descriptor drives frame top, box and lid) --
    @property
    def is_round(self) -> bool:
        return self.seat_form == "round_stool"

    @property
    def plan_depth(self) -> float:
        """Round seats derive depth from the diameter; rectangles keep their own."""
        return self.seat_width_m if self.is_round else self.seat_depth_m

    @property
    def half_width(self) -> float:
        return 0.5 * self.seat_width_m

    @property
    def half_depth(self) -> float:
        return 0.5 * self.plan_depth

    @property
    def has_storage(self) -> bool:
        return self.storage == "hinged_lid_box"

    @property
    def box_height(self) -> float:
        return self.storage_depth_m if self.has_storage else 0.0

    @property
    def frame_top_z(self) -> float:
        """Frame-top plane: the seat stack and storage box grow downward from
        the requested seat height, so seat_height_m stays the real sitting height."""
        return self.seat_height_m - SEAT_STACK - self.box_height - SEAT_CLEAR

    @property
    def drive_axis_z(self) -> float:
        return self.frame_top_z - RAIL_DROP

    @property
    def rail_half_x(self) -> float:
        """Frame-top rail half-span, inset from the seat plan profile."""
        return max(0.12, self.half_width - 0.035)

    @property
    def rail_half_y(self) -> float:
        return max(0.075, self.half_depth - 0.035)

    @property
    def control_x(self) -> float:
        """Rotary controls sit just outboard of the frame-top rail."""
        return self.rail_half_x + 0.030

    @property
    def arm_reach(self) -> float:
        return 0.5 * self.rail_half_x


def config_from_seed(seed: int) -> Config:
    choices = TEMPLATE_DOMAIN.sample(seed)
    rng = random.Random(int(seed) ^ 0x0611_9BE7)
    return Config(
        support_frame=choices["support_frame"],
        seat_form=choices["seat_form"],
        height_mechanism=choices["height_mechanism"],
        storage=choices["storage"],
        seat_width_m=round(rng.uniform(0.44, 0.62), 4),
        seat_depth_m=round(rng.uniform(0.28, 0.36), 4),
        seat_height_m=round(rng.uniform(0.42, 0.52), 4),
        lift_travel_m=round(rng.uniform(0.040, 0.090), 4),
        leg_taper_ratio=round(rng.uniform(0.55, 1.0), 4),
        storage_depth_m=round(rng.uniform(0.09, 0.16), 4),
        lid_open_rad=round(rng.uniform(1.15, 1.45), 4),
        palette_style=rng.choice(PALETTE_STYLES),
        name=f"piano_bench_seed_{seed}",
    )


def resolve_config(config: Config | None = None) -> ResolvedConfig:
    cfg = config or Config()
    TEMPLATE_DOMAIN.validate(
        {
            "support_frame": cfg.support_frame,
            "seat_form": cfg.seat_form,
            "height_mechanism": cfg.height_mechanism,
            "storage": cfg.storage,
        }
    )
    return ResolvedConfig(
        support_frame=_pick(cfg.support_frame, SUPPORT_FRAMES),
        seat_form=_pick(cfg.seat_form, SEAT_FORMS),
        height_mechanism=_pick(cfg.height_mechanism, HEIGHT_MECHANISMS),
        storage=_pick(cfg.storage, STORAGES),
        seat_width_m=_clamp(cfg.seat_width_m, 0.44, 0.62),
        seat_depth_m=_clamp(cfg.seat_depth_m, 0.28, 0.36),
        seat_height_m=_clamp(cfg.seat_height_m, 0.42, 0.52),
        lift_travel_m=_clamp(cfg.lift_travel_m, 0.040, 0.090),
        leg_taper_ratio=_clamp(cfg.leg_taper_ratio, 0.55, 1.0),
        storage_depth_m=_clamp(cfg.storage_depth_m, 0.09, 0.16),
        lid_open_rad=_clamp(cfg.lid_open_rad, 1.15, 1.45),
        palette_style=_pick(cfg.palette_style, PALETTE_STYLES),
        name=cfg.name or "piano_bench",
    )


def slot_choices_for_config(config) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedConfig) else resolve_config(config)
    return (
        ("support_frame", r.support_frame),
        ("seat_form", r.seat_form),
        ("height_mechanism", r.height_mechanism),
        ("storage", r.storage),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Axis-mated joint helper (revolute / prismatic, registered for QC)
# ---------------------------------------------------------------------------
def _axis_joint(
    model, *, name, parent, child, point, axis, articulation_type, limits, radial, meta=None
):
    provider = AxisInterface(name=f"{name}.provider", point=point, axis=axis, radial=radial)
    consumer = AxisInterface(
        name=f"{name}.consumer", point=(0.0, 0.0, 0.0), axis=axis, radial=radial
    )
    mate = mate_axes(provider, consumer)
    model.articulation(
        name,
        articulation_type,
        parent=parent,
        child=child,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=limits,
        motion_properties=MotionProperties(damping=0.35, friction=0.20),
        meta=meta or {},
    )
    register_interface_mate(model, name, mate)


# ===========================================================================
# Shared frame top (constant identity layer across every support candidate)
# ===========================================================================
def _emit_frame_top(frame, r: ResolvedConfig, mats) -> None:
    """Frame-top rails plus the transverse drive-axis boss pair.

    The rail ring follows the seat plan profile: a rectangular seat yields the
    front/rear ledge pair of source 002, a round seat yields a circular top ring
    derived from the same radius.  This is the host adaptation that lets every
    seat form combine with every support candidate without a compatibility gate.
    """
    edge = mats["frame_edge"]
    steel = mats["steel"]
    top_z = r.frame_top_z - 0.5 * RAIL_T

    if r.is_round:
        # A rim ring, not a disc: the centre stays open for the seat guide posts
        # and the mechanism (003 model.py:L52-L55 open sleeves).
        segments = 12
        seg_len = 2.0 * math.pi * r.rail_half_x / segments * 1.08
        for index in range(segments):
            theta = 2.0 * math.pi * index / segments
            frame.visual(
                Box((RAIL_T, seg_len, RAIL_T)),
                origin=Origin(
                    xyz=(r.rail_half_x * math.cos(theta), r.rail_half_x * math.sin(theta), top_z),
                    rpy=(0.0, 0.0, theta),
                ),
                material=edge,
                name=f"support_frame__top_ring_{index}", material_class_id=("wood.polished_varnished" if r.palette_style in {"black_lacquer", "walnut_vinyl", "ebony_leather"} else "metal.brushed_silver"),
            )
    else:
        for tag, sy in (("front", -1.0), ("rear", 1.0)):
            _box(
                frame,
                (2.0 * r.rail_half_x, RAIL_T, RAIL_T),
                (0.0, sy * r.rail_half_y, top_z),
                edge,
                f"support_frame__top_ledge_{tag}",
            )
        for idx, sx in SIDES:
            _box(
                frame,
                (RAIL_T, 2.0 * r.rail_half_y - RAIL_T, RAIL_T),
                (sx * r.rail_half_x, 0.0, top_z),
                edge,
                f"support_frame__top_side_{idx}",
            )

    # Drive-axis bearing bosses: the shared mechanism mount on every candidate.
    for idx, sx in SIDES:
        _box(
            frame,
            (0.026, 0.030, 0.036),
            (sx * (r.rail_half_x - 0.020), 0.0, r.drive_axis_z + 0.010),
            steel,
            f"support_frame__drive_boss_{idx}",
        )
    stub_inner = GUIDE_X + 0.5 * GUIDE_POST + 0.017
    stub_len = (r.rail_half_x - 0.020) - stub_inner
    for idx, sx in SIDES:
        _cyl(
            frame,
            0.007,
            stub_len,
            (sx * (stub_inner + 0.5 * stub_len), 0.0, r.drive_axis_z),
            steel,
            f"support_frame__drive_shaft_{idx}",
            rpy=(0.0, math.pi / 2.0, 0.0),
        )

    # Bilateral guide plates for the seat posts (003 model.py:L52-L55 sleeve
    # voids, 001 model.py:L135-L147 guide tubes).  Their inner faces abut the
    # post faces, so the seat stays supported and guided across the whole lift.
    plate_z = r.frame_top_z - 0.060
    for tag, sy in (("front", -1.0), ("rear", 1.0)):
        _box(
            frame,
            (2.0 * r.rail_half_x, 0.020, 0.020),
            (0.0, sy * 0.028, r.frame_top_z - 0.030),
            steel,
            f"support_frame__guide_rail_{tag}",
        )
    for idx, sx in SIDES:
        for face_index, face in ((0, -1.0), (1, 1.0)):
            _box(
                frame,
                (GUIDE_PLATE_T, GUIDE_POST + 0.014, 0.080),
                (
                    sx * GUIDE_X + face * (0.5 * GUIDE_POST + 0.5 * GUIDE_PLATE_T),
                    0.0,
                    plate_z,
                ),
                steel,
                f"support_frame__guide_plate_{idx}_{face_index}",
            )


# ===========================================================================
# support_frame candidates
# ===========================================================================
def _support_frame_four_leg_apron_build(frame, r: ResolvedConfig, mats) -> None:
    """002 model.py:L88-L164 — four square legs, four aprons, corner blocks, feet.

    `leg_taper_ratio` reproduces the lofted taper of 001 model.py:L26-L40 as a
    stepped section: the upper shoulder keeps the apron seat, the lower shaft
    narrows toward the foot.
    """
    body = mats["frame"]
    edge = mats["frame_edge"]
    rubber = mats["rubber"]
    lx = r.rail_half_x - 0.5 * LEG_SECTION
    ly = r.rail_half_y - 0.5 * LEG_SECTION
    apron_h = 0.070
    apron_z = r.frame_top_z - RAIL_T - 0.5 * apron_h
    shoulder_h = 0.075
    shaft_top = apron_z - 0.5 * apron_h
    shaft_h = shaft_top - FOOT_T
    lower_section = LEG_SECTION * r.leg_taper_ratio

    for index, (sx, sy) in enumerate(((-1.0, -1.0), (1.0, -1.0), (-1.0, 1.0), (1.0, 1.0))):
        x, y = sx * lx, sy * ly
        _box(
            frame,
            (LEG_SECTION, LEG_SECTION, shoulder_h),
            (x, y, shaft_top - 0.5 * shoulder_h),
            body,
            f"support_frame__four_leg_apron__shoulder_{index}",
        )
        _box(
            frame,
            (lower_section, lower_section, shaft_h),
            (x, y, FOOT_T + 0.5 * shaft_h),
            body,
            f"support_frame__four_leg_apron__leg_{index}",
        )
        _box(
            frame,
            (lower_section + 0.006, lower_section + 0.006, FOOT_T),
            (x, y, 0.5 * FOOT_T),
            rubber,
            f"support_frame__four_leg_apron__foot_{index}",
        )

    for tag, sy in (("front", -1.0), ("rear", 1.0)):
        _box(
            frame,
            (2.0 * lx, 0.030, apron_h),
            (0.0, sy * ly, apron_z),
            body,
            f"support_frame__four_leg_apron__apron_{tag}",
        )
    for idx, sx in SIDES:
        _box(
            frame,
            (0.030, 2.0 * ly, apron_h),
            (sx * lx, 0.0, apron_z),
            body,
            f"support_frame__four_leg_apron__apron_side_{idx}",
        )
    for index, (sx, sy) in enumerate(((-1.0, -1.0), (1.0, -1.0), (-1.0, 1.0), (1.0, 1.0))):
        _box(
            frame,
            (0.042, 0.038, 0.030),
            (sx * (lx - 0.020), sy * (ly - 0.016), apron_z + 0.5 * apron_h + 0.015),
            edge,
            f"support_frame__four_leg_apron__corner_block_{index}",
        )


def _support_frame_twin_pedestal_build(frame, r: ResolvedConfig, mats) -> None:
    """003 model.py:L36-L56, L101-L121 — twin pedestal columns on long feet,
    tied by an upper and a lower H rail, with rubber pads under each foot."""
    body = mats["frame"]
    edge = mats["frame_edge"]
    rubber = mats["rubber"]
    px = max(0.075, r.rail_half_x - 0.095)
    foot_len = min(2.0 * r.rail_half_y, r.plan_depth - 0.020)
    column_h = r.frame_top_z - RAIL_T - 0.034
    cap_z = column_h + 0.017

    for idx, sx in SIDES:
        x = sx * px
        _box(
            frame,
            (0.058, foot_len, 0.034),
            (x, 0.0, 0.017 + FOOT_T),
            body,
            f"support_frame__twin_pedestal__foot_rail_{idx}",
        )
        _box(
            frame,
            (0.052, 0.052, column_h - 0.034 - FOOT_T),
            (x, 0.0, FOOT_T + 0.034 + 0.5 * (column_h - 0.034 - FOOT_T)),
            body,
            f"support_frame__twin_pedestal__column_{idx}",
        )
        _box(
            frame,
            (0.056, 0.056, 0.034),
            (x, 0.0, cap_z),
            edge,
            f"support_frame__twin_pedestal__column_cap_{idx}",
        )
        for sy_index, sy in ((0, -1.0), (1, 1.0)):
            _box(
                frame,
                (0.050, 0.042, FOOT_T),
                (x, sy * (0.5 * foot_len - 0.030), 0.5 * FOOT_T),
                rubber,
                f"support_frame__twin_pedestal__foot_pad_{idx}_{sy_index}",
            )

    # Upper tie: stub brackets stop clear of the seat guide-post corridor.
    bracket_inner = GUIDE_X + 0.5 * GUIDE_POST + 0.017
    bracket_len = max(0.02, px - bracket_inner)
    for idx, sx in SIDES:
        _box(
            frame,
            (bracket_len, 0.042, 0.040),
            (sx * (bracket_inner + 0.5 * bracket_len), 0.0, r.frame_top_z - 0.145),
            body,
            f"support_frame__twin_pedestal__upper_bracket_{idx}",
        )
    # Through tie at foot level: it joins the two pedestals without crossing the
    # seat guide-post corridor or the central spindle column above it.
    _box(
        frame,
        (2.0 * px, 0.038, 0.034),
        (0.0, 0.0, FOOT_T + 0.017),
        body,
        "support_frame__twin_pedestal__lower_rail",
    )


def _support_frame_folding_x_frame_build(frame, r: ResolvedConfig, mats) -> None:
    """var_support_folding_x_frame model.py:L89-L216 — crossed X leg pairs per
    side, tied by a centre stretcher, with floor runners under the leg tips."""
    body = mats["frame"]
    edge = mats["frame_edge"]
    rubber = mats["rubber"]
    top_y = r.rail_half_y - 0.020
    foot_y = min(r.half_depth + 0.030, r.rail_half_y + 0.070)
    top_z = r.frame_top_z - 0.5 * RAIL_T
    section = 0.030

    for idx, sx in SIDES:
        x = sx * (r.rail_half_x - 0.026)
        _beam(
            frame,
            (x, -foot_y, FOOT_T),
            (x, top_y, top_z),
            section,
            body,
            f"support_frame__folding_x_frame__leg_a_{idx}",
        )
        _beam(
            frame,
            (x, foot_y, FOOT_T),
            (x, -top_y, top_z),
            section,
            body,
            f"support_frame__folding_x_frame__leg_b_{idx}",
        )
        _cyl(
            frame,
            0.011,
            0.040,
            (x, 0.0, 0.5 * (FOOT_T + top_z)),
            mats["steel"],
            f"support_frame__folding_x_frame__cross_pin_{idx}",
            rpy=(0.0, math.pi / 2.0, 0.0),
        )
        _box(
            frame,
            (0.044, 2.0 * foot_y, 0.020),
            (x, 0.0, FOOT_T + 0.010),
            edge,
            f"support_frame__folding_x_frame__runner_{idx}",
        )
        for sy_index, sy in ((0, -1.0), (1, 1.0)):
            _box(
                frame,
                (0.048, 0.052, FOOT_T),
                (x, sy * (foot_y - 0.030), 0.5 * FOOT_T),
                rubber,
                f"support_frame__folding_x_frame__foot_pad_{idx}_{sy_index}",
            )

    for idx, sx in SIDES:
        _box(
            frame,
            (0.056, 2.0 * top_y, RAIL_T),
            (sx * (r.rail_half_x - 0.013), 0.0, r.frame_top_z - 0.5 * RAIL_T),
            edge,
            f"support_frame__folding_x_frame__top_rail_{idx}",
        )

    stretcher_inner = GUIDE_X + 0.5 * GUIDE_POST + 0.017
    stretcher_len = max(0.02, (r.rail_half_x - 0.026) - stretcher_inner)
    for idx, sx in SIDES:
        _box(
            frame,
            (stretcher_len, 0.034, 0.030),
            (
                sx * (stretcher_inner + 0.5 * stretcher_len),
                0.0,
                0.5 * (FOOT_T + top_z),
            ),
            body,
            f"support_frame__folding_x_frame__stretcher_{idx}",
        )


_SUPPORT_BUILDERS = {
    "four_leg_apron": _support_frame_four_leg_apron_build,
    "twin_pedestal": _support_frame_twin_pedestal_build,
    "folding_x_frame": _support_frame_folding_x_frame_build,
}


# ===========================================================================
# seat_form candidates + shared cushion
# ===========================================================================
def _emit_cushion(part, r: ResolvedConfig, mats, base_z: float, prefix: str) -> None:
    """Crowned upholstered cushion (002 model.py:L21-L37 `_padded_cushion`).

    The two-stage crown is preserved for both plan forms; the round form uses the
    same stack on a circular profile (round_stool model.py:L59-L70).
    """
    cushion = mats["cushion"]
    lower_t = 0.036
    crown_t = CUSHION_T - lower_t
    if r.is_round:
        part.visual(
            Cylinder(radius=r.half_width - 0.004, length=lower_t),
            origin=Origin(xyz=(0.0, 0.0, base_z + 0.5 * lower_t)),
            material=cushion,
            name=f"{prefix}__cushion_lower", material_class_id=("leather.smooth_plain" if r.palette_style in {"black_lacquer", "ebony_leather"} else "fabric.upholstery_plain"),
        )
        part.visual(
            Cylinder(radius=r.half_width - 0.020, length=crown_t),
            origin=Origin(xyz=(0.0, 0.0, base_z + lower_t + 0.5 * crown_t)),
            material=cushion,
            name=f"{prefix}__cushion_crown", material_class_id=("leather.smooth_plain" if r.palette_style in {"black_lacquer", "ebony_leather"} else "fabric.upholstery_plain"),
        )
    else:
        _box(
            part,
            (r.seat_width_m - 0.008, r.plan_depth - 0.008, lower_t),
            (0.0, 0.0, base_z + 0.5 * lower_t),
            cushion,
            f"{prefix}__cushion_lower",
        )
        _box(
            part,
            (r.seat_width_m - 0.040, r.plan_depth - 0.030, crown_t),
            (0.0, 0.0, base_z + lower_t + 0.5 * crown_t),
            cushion,
            f"{prefix}__cushion_crown",
        )
    # Edge welt: source 003 model.py:L153-L171 reads the seat as upholstered.
    part.visual(
        Box((r.seat_width_m - 0.016, 0.010, 0.007))
        if not r.is_round
        else Cylinder(radius=r.half_width - 0.002, length=0.007),
        origin=Origin(
            xyz=(0.0, -(r.half_depth - 0.012) if not r.is_round else 0.0, base_z + lower_t)
        ),
        material=mats["frame_edge"],
        name=f"{prefix}__welt", material_class_id=("wood.polished_varnished" if r.palette_style in {"black_lacquer", "walnut_vinyl", "ebony_leather"} else "metal.brushed_silver"),
    )


def _emit_seat_guides(seat, r: ResolvedConfig, mats) -> None:
    """Two square guide posts hanging under the seat board.

    They run between the frame guide plates for the entire lift travel, so the
    seat is a guided carriage rather than a floating board (003 model.py:L175-L181
    inner posts, 001 model.py:L247-L260 guide rods).
    """
    for idx, sx in SIDES:
        _box(
            seat,
            (GUIDE_POST, GUIDE_POST, GUIDE_POST_LEN),
            (sx * GUIDE_X, 0.0, -0.5 * GUIDE_POST_LEN),
            mats["dark_steel"],
            f"seat__guide_post_{idx}",
        )


def _seat_form_rectangle_padded_build(seat, r: ResolvedConfig, mats, base_z: float) -> None:
    """002 model.py:L193-L219 — rectangular seat board with underside roller tracks."""
    body = mats["frame"]
    steel = mats["dark_steel"]
    _box(
        seat,
        (r.seat_width_m, r.plan_depth, BOARD_T),
        (0.0, 0.0, base_z + 0.5 * BOARD_T),
        body,
        "seat_form__rectangle_padded__board",
    )
    for tag, sy in (("front", -1.0), ("rear", 1.0)):
        _box(
            seat,
            (0.34 * r.seat_width_m, 0.012, 0.010),
            (0.0, sy * (r.half_depth - 0.038), base_z - 0.005),
            steel,
            f"seat_form__rectangle_padded__roller_track_{tag}",
        )


def _seat_form_round_stool_build(seat, r: ResolvedConfig, mats, base_z: float) -> None:
    """round_stool model.py:L59-L90, L138-L213 — circular board and pad."""
    body = mats["frame"]
    steel = mats["dark_steel"]
    seat.visual(
        Cylinder(radius=r.half_width, length=BOARD_T),
        origin=Origin(xyz=(0.0, 0.0, base_z + 0.5 * BOARD_T)),
        material=body,
        name="seat_form__round_stool__board", material_class_id=("wood.polished_varnished" if r.palette_style in {"black_lacquer", "walnut_vinyl", "ebony_leather"} else "metal.paint_coated"),
    )
    seat.visual(
        Cylinder(radius=0.34 * r.seat_width_m, length=0.010),
        origin=Origin(xyz=(0.0, 0.0, base_z - 0.005)),
        material=steel,
        name="seat_form__round_stool__hub_plate", material_class_id="metal.blackened_gunmetal",
    )


_SEAT_BUILDERS = {
    "rectangle_padded": _seat_form_rectangle_padded_build,
    "round_stool": _seat_form_round_stool_build,
}


# ===========================================================================
# storage candidates
# ===========================================================================
def _storage_plain_apron_build(model, seat, r: ResolvedConfig, mats) -> None:
    """002 model.py:L193-L219 — no storage bay; the cushion rides the seat board."""
    _emit_cushion(seat, r, mats, BOARD_T, "storage__plain_apron")


def _storage_hinged_lid_box_build(model, seat, r: ResolvedConfig, mats) -> None:
    """var_storage_hinged_seat_lid model.py:L76-L134, L279-L344, L366-L421.

    A rabbeted box grows on the seat board and the lid becomes the seating
    surface.  Box and lid share the seat plan profile, so a round seat yields a
    round box and a round lid instead of the combination being excluded.
    """
    body = mats["frame"]
    edge = mats["frame_edge"]
    felt = mats["felt"]
    steel = mats["dark_steel"]
    wall_h = r.box_height
    wall_z = BOARD_T + 0.5 * wall_h
    rim_z = BOARD_T + wall_h

    if r.is_round:
        seat.visual(
            Cylinder(radius=r.half_width, length=wall_h),
            origin=Origin(xyz=(0.0, 0.0, wall_z)),
            material=body,
            name="storage__hinged_lid_box__box_shell", material_class_id=("wood.polished_varnished" if r.palette_style in {"black_lacquer", "walnut_vinyl", "ebony_leather"} else "metal.paint_coated"),
        )
        seat.visual(
            Cylinder(radius=r.half_width - WALL_T, length=wall_h - 0.010),
            origin=Origin(xyz=(0.0, 0.0, wall_z - 0.005)),
            material=felt,
            name="storage__hinged_lid_box__lining", material_class_id="fabric.felt",
        )
    else:
        for tag, sy in (("front", -1.0), ("rear", 1.0)):
            _box(
                seat,
                (r.seat_width_m, WALL_T, wall_h),
                (0.0, sy * (r.half_depth - 0.5 * WALL_T), wall_z),
                body,
                f"storage__hinged_lid_box__wall_{tag}",
            )
        for idx, sx in SIDES:
            _box(
                seat,
                (WALL_T, r.plan_depth - 2.0 * WALL_T, wall_h),
                (sx * (r.half_width - 0.5 * WALL_T), 0.0, wall_z),
                body,
                f"storage__hinged_lid_box__wall_side_{idx}",
            )
        _box(
            seat,
            (r.seat_width_m - 2.0 * WALL_T, r.plan_depth - 2.0 * WALL_T, 0.004),
            (0.0, 0.0, BOARD_T + 0.002),
            felt,
            "storage__hinged_lid_box__lining",
        )
    # Rabbet shelf: its top face is the seating plane the closed lid rests on.
    seat.visual(
        Cylinder(radius=r.half_width - 0.006, length=0.006)
        if r.is_round
        else Box((r.seat_width_m - 0.012, r.plan_depth - 0.012, 0.006)),
        origin=Origin(xyz=(0.0, 0.0, rim_z - 0.003)),
        material=edge,
        name="storage__hinged_lid_box__rabbet_shelf", material_class_id=("wood.polished_varnished" if r.palette_style in {"black_lacquer", "walnut_vinyl", "ebony_leather"} else "metal.brushed_silver"),
    )
    # Hinge saddle behind the rear wall: it carries the lid barrel from below at
    # every pose (the barrel itself is coaxial with the hinge, so it never sweeps).
    _box(
        seat,
        (0.72 * r.seat_width_m, 0.026, 0.012),
        (0.0, r.half_depth + 0.004, rim_z - 0.012),
        steel,
        "storage__hinged_lid_box__hinge_saddle",
    )

    # The lid is a quarter-plane about its hinge: its rear edge is the axis and
    # its underside is the axis plane, so opening sweeps only upward and forward.
    lid = model.part("seat_lid", meta={"role": "seat_lid", "candidate": "hinged_lid_box"})
    lid_centre_y = -(r.half_depth + 0.008)
    if r.is_round:
        lid.visual(
            Cylinder(radius=r.half_width, length=BOARD_T),
            origin=Origin(xyz=(0.0, lid_centre_y, 0.5 * BOARD_T)),
            material=body,
            name="storage__hinged_lid_box__lid_board", material_class_id=("wood.polished_varnished" if r.palette_style in {"black_lacquer", "walnut_vinyl", "ebony_leather"} else "metal.paint_coated"),
        )
    else:
        _box(
            lid,
            (r.seat_width_m, r.plan_depth + 0.008, BOARD_T),
            (0.0, -0.5 * (r.plan_depth + 0.008), 0.5 * BOARD_T),
            body,
            "storage__hinged_lid_box__lid_board",
        )
    _cyl(
        lid,
        0.006,
        0.72 * r.seat_width_m,
        (0.0, 0.0, 0.0),
        steel,
        "storage__hinged_lid_box__hinge_barrel",
        rpy=(0.0, math.pi / 2.0, 0.0),
    )
    _box(
        lid,
        (0.70 * r.seat_width_m, 0.030, 0.004),
        (0.0, -0.009, 0.002),
        steel,
        "storage__hinged_lid_box__hinge_leaf",
    )

    # The lid carries the cushion: with storage the lid is the seating surface.
    # Its cushion is emitted about the lid's own plan centre.
    lid_cushion_r = ResolvedConfig(**{**r.__dict__})
    _emit_cushion_on_lid(lid, lid_cushion_r, mats)

    _axis_joint(
        model,
        name="lid_hinge",
        parent=seat.name,
        child=lid.name,
        point=(0.0, r.half_depth + 0.008, rim_z),
        axis=(-1.0, 0.0, 0.0),
        articulation_type=ArticulationType.REVOLUTE,
        limits=MotionLimits(effort=12.0, velocity=1.8, lower=0.0, upper=r.lid_open_rad),
        radial=(0.0, 0.0, 1.0),
        meta={"mechanism": "rear storage-seat hinge"},
    )


def _emit_cushion_on_lid(lid, r: ResolvedConfig, mats) -> None:
    """Cushion stack on the lid, offset to the lid's plan centre."""
    cushion = mats["cushion"]
    lower_t = 0.036
    crown_t = CUSHION_T - lower_t
    cy = -(r.half_depth + 0.008)
    if r.is_round:
        lid.visual(
            Cylinder(radius=r.half_width - 0.012, length=lower_t),
            origin=Origin(xyz=(0.0, cy, BOARD_T + 0.5 * lower_t)),
            material=cushion,
            name="storage__hinged_lid_box__cushion_lower", material_class_id=("leather.smooth_plain" if r.palette_style in {"black_lacquer", "ebony_leather"} else "fabric.upholstery_plain"),
        )
        lid.visual(
            Cylinder(radius=r.half_width - 0.028, length=crown_t),
            origin=Origin(xyz=(0.0, cy, BOARD_T + lower_t + 0.5 * crown_t)),
            material=cushion,
            name="storage__hinged_lid_box__cushion_crown", material_class_id=("leather.smooth_plain" if r.palette_style in {"black_lacquer", "ebony_leather"} else "fabric.upholstery_plain"),
        )
    else:
        _box(
            lid,
            (r.seat_width_m - 0.018, r.plan_depth - 0.010, lower_t),
            (0.0, cy, BOARD_T + 0.5 * lower_t),
            cushion,
            "storage__hinged_lid_box__cushion_lower",
        )
        _box(
            lid,
            (r.seat_width_m - 0.050, r.plan_depth - 0.032, crown_t),
            (0.0, cy, BOARD_T + lower_t + 0.5 * crown_t),
            cushion,
            "storage__hinged_lid_box__cushion_crown",
        )


_STORAGE_BUILDERS = {
    "plain_apron": _storage_plain_apron_build,
    "hinged_lid_box": _storage_hinged_lid_box_build,
}


# ===========================================================================
# height_mechanism candidates
# ===========================================================================
def _emit_rotary_control(model, frame, r: ResolvedConfig, mats, *, index: str, sx: float, style: str):
    """One rotary control part on the transverse drive axis.

    `style` picks the source grip form: handwheel disk (002 model.py:L226-L239),
    plain side knob (twin_side_knobs model.py:L44-L78), or the gear-driven wheel
    of the central spindle (central_spindle model.py:L173-L202).
    """
    body = mats["frame"]
    edge = mats["frame_edge"]
    steel = mats["steel"]
    name = f"height_control_{index}"
    part = model.part(name, meta={"role": "height_control", "candidate": r.height_mechanism})
    radius = 0.036 if style == "handwheel" else 0.030
    part.visual(
        Cylinder(radius=radius, length=0.024),
        origin=Origin(xyz=(sx * 0.014, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=body,
        name=f"height_mechanism__{r.height_mechanism}__{name}_disk", material_class_id=("wood.polished_varnished" if r.palette_style in {"black_lacquer", "walnut_vinyl", "ebony_leather"} else "metal.paint_coated"),
    )
    part.visual(
        Cylinder(radius=0.014, length=0.014),
        origin=Origin(xyz=(sx * 0.004, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=edge,
        name=f"height_mechanism__{r.height_mechanism}__{name}_hub", material_class_id=("wood.polished_varnished" if r.palette_style in {"black_lacquer", "walnut_vinyl", "ebony_leather"} else "metal.brushed_silver"),
    )
    # The shaft reaches inward until it abuts the frame drive boss outer face:
    # control_x - (rail_half_x - 0.020 + 0.013) = 0.037 by construction.
    part.visual(
        Cylinder(radius=0.007, length=0.050),
        origin=Origin(xyz=(-sx * 0.012, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=steel,
        name=f"height_mechanism__{r.height_mechanism}__{name}_shaft", material_class_id="metal.steel_bare",
    )
    _axis_joint(
        model,
        name=f"{name}_turn",
        parent=frame.name,
        child=name,
        point=(sx * r.control_x, 0.0, r.drive_axis_z),
        axis=(1.0, 0.0, 0.0),
        articulation_type=ArticulationType.REVOLUTE,
        limits=MotionLimits(effort=16.0, velocity=5.0, lower=0.0, upper=KNOB_TRAVEL),
        radial=(0.0, 0.0, 1.0),
        meta={"mechanism": "height-adjustment rotary control"},
    )
    return part


def _emit_lift_link(model, frame, r: ResolvedConfig, mats, *, index: str, sx: float, tag: str):
    """One lifting link swinging in the gap between the frame top and the seat.

    At q=0 the link hangs `ARM_SWING` below horizontal and rises to horizontal at
    the upper limit, so its tip never reaches the seat underside (002
    model.py:L40-L67 two-rail yoke; scissor_lift model.py:L56-L90 crossed pair).
    The frame carries a real pivot mount whose top face abuts the pivot pin.
    """
    body = mats["frame"]
    steel = mats["steel"]
    edge = mats["frame_edge"]
    name = f"{tag}_{index}"
    part = model.part(name, meta={"role": "lift_linkage", "candidate": r.height_mechanism})
    reach = 0.40 * r.rail_half_x
    span = min(2.0 * r.rail_half_y - 0.130, r.plan_depth - 0.160)
    pivot_x = sx * (r.rail_half_x - 0.055)
    pivot_z = r.drive_axis_z - MECH_CLEAR
    tip = (-sx * reach * math.cos(ARM_SWING), -reach * math.sin(ARM_SWING))

    for y_index, sy in ((0, -1.0), (1, 1.0)):
        _beam(
            part,
            (0.0, sy * 0.5 * span, 0.0),
            (tip[0], sy * 0.5 * span, tip[1]),
            0.014,
            body,
            f"height_mechanism__{r.height_mechanism}__{name}_link_{y_index}",
        )
    part.visual(
        Cylinder(radius=0.009, length=span + 0.028),
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=steel,
        name=f"height_mechanism__{r.height_mechanism}__{name}_pivot_pin", material_class_id="metal.steel_bare",
    )
    for y_index, sy in ((0, -1.0), (1, 1.0)):
        part.visual(
            Cylinder(radius=0.008, length=0.026),
            origin=Origin(
                xyz=(tip[0], sy * 0.5 * span, tip[1]), rpy=(math.pi / 2.0, 0.0, 0.0)
            ),
            material=steel,
            name=f"height_mechanism__{r.height_mechanism}__{name}_roller_{y_index}", material_class_id="metal.steel_bare",
        )

    # Frame pivot mount: its top face abuts the pin, so the linkage is supported
    # rather than floating (002 model.py:L262-L281 frame pivot bosses).
    # The mount sits outboard of the inward-swinging link and its top face is
    # tangent to the pin, so the linkage is carried without any overlap.
    _box(
        frame,
        (0.060, span + 0.030, 0.018),
        (pivot_x + sx * 0.030, 0.0, pivot_z - 0.018),
        edge,
        f"support_frame__pivot_mount_{tag}_{index}",
    )
    # Hanger carrying the mount up to the frame guide rails, so the mount is part
    # of the frame body on every support candidate.
    hanger_top = r.frame_top_z - 0.025
    hanger_bottom = pivot_z - 0.009
    _box(
        frame,
        (0.040, 0.044, hanger_top - hanger_bottom),
        (pivot_x + sx * 0.030, 0.0, 0.5 * (hanger_top + hanger_bottom)),
        edge,
        f"support_frame__pivot_hanger_{tag}_{index}",
    )

    _axis_joint(
        model,
        name=f"{name}_pivot",
        parent=frame.name,
        child=name,
        point=(pivot_x, 0.0, pivot_z),
        axis=(0.0, sx, 0.0),
        articulation_type=ArticulationType.REVOLUTE,
        limits=MotionLimits(effort=320.0, velocity=0.25, lower=0.0, upper=ARM_SWING),
        radial=(1.0, 0.0, 0.0),
        meta={"mechanism": "seat lifting linkage"},
    )
    return part


def _height_mechanism_side_handwheel_yoke_build(model, frame, r: ResolvedConfig, mats) -> None:
    """002 model.py:L40-L67, L221-L239, L241-L281 — one side handwheel plus a
    paired two-rail lifting yoke on each side of the frame."""
    _emit_rotary_control(model, frame, r, mats, index="0", sx=-1.0, style="handwheel")
    for idx, sx in SIDES:
        _emit_lift_link(model, frame, r, mats, index=idx, sx=sx, tag="lift_arm")


def _height_mechanism_central_spindle_build(model, frame, r: ResolvedConfig, mats) -> None:
    """central_spindle model.py:L40-L72, L173-L202, L251-L253, L270-L307 — a
    central threaded rod turning in a fixed nut, driven through a bevel-gear
    housing from the side wheel."""
    steel = mats["steel"]
    edge = mats["frame_edge"]
    _emit_rotary_control(model, frame, r, mats, index="0", sx=-1.0, style="handwheel")

    # Frame-side support: platform, captive nut and the bevel-gear housing.
    # Platform stays inboard of the seat guide posts (|x| <= 0.030 < GUIDE_X).
    _box(
        frame,
        (0.060, 0.110, 0.016),
        (0.0, 0.0, r.drive_axis_z),
        edge,
        "height_mechanism__central_spindle__platform",
    )
    _cyl(
        frame,
        0.020,
        0.030,
        (0.0, 0.0, r.drive_axis_z + 0.007),
        steel,
        "height_mechanism__central_spindle__captive_nut",
    )
    _box(
        frame,
        (0.052, 0.048, 0.046),
        (-(GUIDE_X + 0.5 * GUIDE_POST + 0.030), 0.0, r.drive_axis_z),
        steel,
        "height_mechanism__central_spindle__gear_housing",
    )

    # The rod hangs below the captive nut, so it never reaches the seat stack.
    spindle = model.part("spindle", meta={"role": "lift_linkage", "candidate": "central_spindle"})
    rod_len = min(0.090 + r.lift_travel_m, max(0.045, r.drive_axis_z - 0.068))
    spindle.visual(
        Cylinder(radius=0.011, length=rod_len),
        origin=Origin(xyz=(0.0, 0.0, -0.5 * rod_len)),
        material=steel,
        name="height_mechanism__central_spindle__rod", material_class_id="metal.steel_bare",
    )
    for index in range(4):
        spindle.visual(
            Cylinder(radius=0.014, length=0.004),
            origin=Origin(xyz=(0.0, 0.0, -0.020 - index * (rod_len - 0.030) / 3.0)),
            material=steel,
            name=f"height_mechanism__central_spindle__thread_ridge_{index}", material_class_id="metal.steel_bare",
        )
    spindle.visual(
        Cylinder(radius=0.019, length=0.012),
        origin=Origin(xyz=(0.0, 0.0, -0.006)),
        material=edge,
        name="height_mechanism__central_spindle__top_collar", material_class_id=("wood.polished_varnished" if r.palette_style in {"black_lacquer", "walnut_vinyl", "ebony_leather"} else "metal.brushed_silver"),
    )
    _axis_joint(
        model,
        name="spindle_turn",
        parent=frame.name,
        child=spindle.name,
        point=(0.0, 0.0, r.drive_axis_z - 0.008),
        axis=(0.0, 0.0, 1.0),
        articulation_type=ArticulationType.REVOLUTE,
        limits=MotionLimits(effort=90.0, velocity=3.0, lower=0.0, upper=SPINDLE_TRAVEL),
        radial=(1.0, 0.0, 0.0),
        meta={"mechanism": "central lifting spindle"},
    )


def _height_mechanism_twin_side_knobs_build(model, frame, r: ResolvedConfig, mats) -> None:
    """twin_side_knobs model.py:L44-L78, L179-L205, L234-L251, L253-L290 — two
    opposed side knobs on one transverse screw with a pair of lift nuts."""
    steel = mats["steel"]
    for idx, sx in SIDES:
        _emit_rotary_control(model, frame, r, mats, index=idx, sx=sx, style="knob")
    for idx, sx in SIDES:
        _box(
            frame,
            (0.038, 0.028, 0.026),
            (sx * 0.082, 0.0, r.drive_axis_z),
            steel,
            f"height_mechanism__twin_side_knobs__lift_nut_{idx}",
        )
    _box(
        frame,
        (0.040, 0.044, 0.026),
        (0.0, 0.0, r.drive_axis_z + 0.013),
        steel,
        "height_mechanism__twin_side_knobs__centre_bearing",
    )
    # Central screw segment between the seat guide posts, with its thread collars.
    _cyl(
        frame,
        0.007,
        2.0 * (GUIDE_X - 0.5 * GUIDE_POST - 0.004),
        (0.0, 0.0, r.drive_axis_z),
        steel,
        "height_mechanism__twin_side_knobs__centre_screw",
        rpy=(0.0, math.pi / 2.0, 0.0),
    )
    for index in range(4):
        _cyl(
            frame,
            0.009,
            0.004,
            (-0.021 + index * 0.014, 0.0, r.drive_axis_z),
            steel,
            f"height_mechanism__twin_side_knobs__thread_collar_{index}",
            rpy=(0.0, math.pi / 2.0, 0.0),
        )


def _height_mechanism_scissor_lift_build(model, frame, r: ResolvedConfig, mats) -> None:
    """scissor_lift model.py:L56-L90, L189-L208, L224-L229, L252-L297 — a crossed
    scissor pair on frame pivot mounts with lower-tip guide rails."""
    edge = mats["frame_edge"]
    _emit_rotary_control(model, frame, r, mats, index="0", sx=-1.0, style="handwheel")
    for idx, sx in SIDES:
        _emit_lift_link(model, frame, r, mats, index=idx, sx=sx, tag="scissor")
        _box(
            frame,
            (0.030, 0.030, 0.040),
            (sx * (r.rail_half_x - 0.055), 0.0, r.drive_axis_z - MECH_CLEAR - 0.047),
            edge,
            f"height_mechanism__scissor_lift__mount_post_{idx}",
        )


_HEIGHT_BUILDERS = {
    "side_handwheel_yoke": _height_mechanism_side_handwheel_yoke_build,
    "central_spindle": _height_mechanism_central_spindle_build,
    "twin_side_knobs": _height_mechanism_twin_side_knobs_build,
    "scissor_lift": _height_mechanism_scissor_lift_build,
}


# ===========================================================================
# Assembly
# ===========================================================================
def build_piano_bench(
    config: Config | None = None, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets, meta={"category": "piano_bench"})
    palette = dict(PALETTES[r.palette_style])
    palette.update(_HARDWARE)
    mats = {key: model.material(f"bench_{r.palette_style}_{key}", rgba=rgba) for key, rgba in palette.items()}

    frame = model.part(
        "support_frame", meta={"role": "support_frame", "candidate": r.support_frame}
    )
    _SUPPORT_BUILDERS[r.support_frame](frame, r, mats)
    _emit_frame_top(frame, r, mats)

    seat = model.part("seat", meta={"role": "seat", "candidate": r.seat_form})
    _SEAT_BUILDERS[r.seat_form](seat, r, mats, 0.0)
    _emit_seat_guides(seat, r, mats)

    _axis_joint(
        model,
        name="seat_lift",
        parent=frame.name,
        child=seat.name,
        point=(0.0, 0.0, r.frame_top_z + SEAT_CLEAR),
        axis=(0.0, 0.0, 1.0),
        articulation_type=ArticulationType.PRISMATIC,
        limits=MotionLimits(effort=1200.0, velocity=0.03, lower=0.0, upper=r.lift_travel_m),
        radial=(1.0, 0.0, 0.0),
        meta={"mechanism": "screw-driven seat height lift"},
    )

    _STORAGE_BUILDERS[r.storage](model, seat, r, mats)
    _HEIGHT_BUILDERS[r.height_mechanism](model, frame, r, mats)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_piano_bench(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_piano_bench(config_from_seed(seed), assets=assets)


# ===========================================================================
# Tests
# ===========================================================================
def run_piano_bench_tests(object_model: ArticulatedObject, config: Config) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)

    frame = object_model.get_part("support_frame")
    seat = object_model.get_part("seat")
    lift = object_model.get_articulation("seat_lift")

    movable = [
        joint
        for joint in object_model.articulations
        if joint.articulation_type
        in (ArticulationType.REVOLUTE, ArticulationType.PRISMATIC, ArticulationType.CONTINUOUS)
    ]
    controls = [
        joint
        for joint in object_model.articulations
        if joint.name.startswith("height_control_") and joint.name.endswith("_turn")
    ]

    # ---- Category anchors (named author checks). ----
    ctx.check(
        "category_anchor: bench seat rides a prismatic height lift",
        lift.parent == "support_frame"
        and lift.child == "seat"
        and lift.articulation_type == ArticulationType.PRISMATIC
        and abs(lift.axis[2]) > 0.99
        and lift.motion_limits is not None
        and lift.motion_limits.upper is not None
        and lift.motion_limits.upper >= 0.040,
        details=f"lift={lift.parent}->{lift.child}, axis={lift.axis}, limits={lift.motion_limits}",
    )
    expected_controls = 2 if r.height_mechanism == "twin_side_knobs" else 1
    ctx.check(
        "category_anchor: height mechanism provides a real rotary control",
        len(controls) == expected_controls
        and all(
            joint.parent == "support_frame"
            and joint.articulation_type == ArticulationType.REVOLUTE
            and abs(joint.axis[0]) > 0.99
            for joint in controls
        ),
        details=f"controls={[(j.name, j.parent, j.axis) for j in controls]}, expected={expected_controls}",
    )
    ctx.check(
        "category_anchor: every seed is articulated",
        len(movable) >= 2,
        details=f"movable joints={[(j.name, str(j.articulation_type)) for j in movable]}",
    )

    # ---- Identity geometry: a wide bench seat over a grounded frame. ----
    ctx.check(
        "seat is a wide bench-scale surface",
        r.seat_width_m >= 0.44 and r.plan_depth >= 0.28,
        details=f"width={r.seat_width_m}, plan_depth={r.plan_depth}",
    )
    # The frame top must clear the mechanism envelope it carries: the drive axis
    # sits RAIL_DROP below it, the pivot mounts another MECH_CLEAR + 0.027 below,
    # and the seat guide plates reach 0.10 m down.  0.15 m keeps the lowest plate
    # clear of the floor for every seat height / storage depth combination.
    ctx.check(
        "frame top clears the mechanism envelope and stays below the seat",
        r.frame_top_z >= 0.15 and r.frame_top_z < r.seat_height_m,
        details=f"frame_top_z={r.frame_top_z:.4f}, seat_height={r.seat_height_m:.4f}, box={r.box_height:.4f}",
    )
    ctx.check(
        "support candidate emits its own leg family",
        any(v.name.startswith(f"support_frame__{r.support_frame}__") for v in frame.visuals),
        details=f"frame visuals={[v.name for v in frame.visuals][:8]}",
    )
    ctx.check(
        "seat candidate emits its own board",
        any(v.name.startswith(f"seat_form__{r.seat_form}__") for v in seat.visuals),
        details=f"seat visuals={[v.name for v in seat.visuals][:8]}",
    )

    # ---- Host adaptation: the frame top follows the seat plan profile. ----
    if r.is_round:
        ctx.check(
            "round seat is carried by a circular top ring",
            sum(1 for v in frame.visuals if v.name.startswith("support_frame__top_ring_")) == 12
            and r.rail_half_x <= r.half_width,
            details=f"rail_half_x={r.rail_half_x:.4f} <= half_width={r.half_width:.4f}",
        )
    else:
        ctx.check(
            "rectangular seat is carried by the front/rear ledge pair",
            all(
                any(v.name == f"support_frame__top_ledge_{tag}" for v in frame.visuals)
                for tag in ("front", "rear")
            )
            and r.rail_half_y <= r.half_depth,
            details=f"rail_half_y={r.rail_half_y:.4f} <= half_depth={r.half_depth:.4f}",
        )

    # ---- Height lift raises the seat by the full travel. ----
    rest = ctx.part_world_position(seat)
    with ctx.pose({lift: lift.motion_limits.upper}):
        raised = ctx.part_world_position(seat)
    ctx.check(
        "height lift raises the seat by the full travel",
        rest is not None
        and raised is not None
        and abs((raised[2] - rest[2]) - lift.motion_limits.upper) < 0.004,
        details=f"rest_z={rest[2] if rest else None}, raised_z={raised[2] if raised else None}",
    )

    # ---- Rotary controls spin in place on the drive axis. ----
    for joint in controls:
        part = object_model.get_part(joint.child)
        before = ctx.part_world_position(part)
        with ctx.pose({joint: 1.5}):
            after = ctx.part_world_position(part)
        ctx.check(
            f"{joint.child} spins in place",
            before is not None
            and after is not None
            and max(abs(before[k] - after[k]) for k in range(3)) < 1e-6,
            details=f"before={before}, after={after}",
        )

    # ---- Storage candidate. ----
    if r.has_storage:
        lid = object_model.get_part("seat_lid")
        hinge = object_model.get_articulation("lid_hinge")
        ctx.check(
            "storage lid hinges on the rear rim about -X",
            hinge.parent == "seat"
            and hinge.child == "seat_lid"
            and hinge.articulation_type == ArticulationType.REVOLUTE
            and hinge.axis[0] < -0.99
            and hinge.motion_limits is not None
            and hinge.motion_limits.upper is not None
            and hinge.motion_limits.upper >= 1.15,
            details=f"hinge={hinge.axis}, limits={hinge.motion_limits}",
        )
        closed = ctx.part_world_aabb(lid)
        with ctx.pose({hinge: hinge.motion_limits.upper}):
            opened = ctx.part_world_aabb(lid)
        ctx.check(
            "storage lid opens upward",
            closed is not None and opened is not None and opened[1][2] > closed[1][2] + 0.15,
            details=f"closed={closed}, opened={opened}",
        )
        ctx.check(
            "storage box and lid share the seat plan profile",
            any(v.name == "storage__hinged_lid_box__rabbet_shelf" for v in seat.visuals)
            and any(v.name == "storage__hinged_lid_box__lid_board" for v in lid.visuals),
            details=f"lid visuals={[v.name for v in lid.visuals]}",
        )
    else:
        ctx.check(
            "plain seat carries the cushion directly",
            any(v.name.startswith("storage__plain_apron__cushion") for v in seat.visuals),
            details=f"seat visuals={[v.name for v in seat.visuals]}",
        )

    # ---- Compiler-owned baseline (collision / pose QC is harness-owned). ----
    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()

    return ctx.report()


# ===========================================================================
# High-risk cross-slot corners
# ===========================================================================
TEMPLATE_CORNERS = (
    corner_case(
        "round_seat_four_leg_deep_storage",
        {
            "support_frame": "four_leg_apron",
            "seat_form": "round_stool",
            "height_mechanism": "side_handwheel_yoke",
            "storage": "hinged_lid_box",
            "seat_width_m": 0.44,
            "seat_depth_m": 0.28,
            "seat_height_m": 0.42,
            "lift_travel_m": 0.090,
            "leg_taper_ratio": 0.55,
            "storage_depth_m": 0.16,
            "lid_open_rad": 1.45,
        },
        reason="narrowest round seat on the rectangular four-leg host with the deepest storage box and maximum lift",
    ),
    corner_case(
        "widest_duet_x_frame_scissor",
        {
            "support_frame": "folding_x_frame",
            "seat_form": "rectangle_padded",
            "height_mechanism": "scissor_lift",
            "storage": "hinged_lid_box",
            "seat_width_m": 0.62,
            "seat_depth_m": 0.36,
            "seat_height_m": 0.52,
            "lift_travel_m": 0.090,
            "leg_taper_ratio": 1.0,
            "storage_depth_m": 0.16,
            "lid_open_rad": 1.45,
        },
        reason="widest duet seat with storage on the crossed X frame while both scissor links sweep",
    ),
    corner_case(
        "twin_pedestal_round_twin_knobs_min",
        {
            "support_frame": "twin_pedestal",
            "seat_form": "round_stool",
            "height_mechanism": "twin_side_knobs",
            "storage": "plain_apron",
            "seat_width_m": 0.44,
            "seat_depth_m": 0.28,
            "seat_height_m": 0.42,
            "lift_travel_m": 0.040,
            "leg_taper_ratio": 0.55,
            "storage_depth_m": 0.09,
            "lid_open_rad": 1.15,
        },
        reason="smallest round stool on twin pedestals with two side knobs at minimum travel",
    ),
    corner_case(
        "central_spindle_max_lift_widest",
        {
            "support_frame": "twin_pedestal",
            "seat_form": "rectangle_padded",
            "height_mechanism": "central_spindle",
            "storage": "hinged_lid_box",
            "seat_width_m": 0.62,
            "seat_depth_m": 0.36,
            "seat_height_m": 0.52,
            "lift_travel_m": 0.090,
            "leg_taper_ratio": 1.0,
            "storage_depth_m": 0.16,
            "lid_open_rad": 1.45,
        },
        reason="longest spindle rod at maximum travel under the widest storage seat",
    ),
)


__all__ = [
    "TEMPLATE_DOMAIN",
    "TEMPLATE_CORNERS",
    "SupportFrame",
    "SeatForm",
    "HeightMechanism",
    "Storage",
    "PaletteStyle",
    "Config",
    "ResolvedConfig",
    "config_from_seed",
    "resolve_config",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "build_piano_bench",
    "build_seeded_piano_bench",
    "run_piano_bench_tests",
]
