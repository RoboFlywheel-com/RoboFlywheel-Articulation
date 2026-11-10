# SPDX-License-Identifier: Apache-2.0

"""Playground seesaw modular template.

Reviewed spec:
``articraft_template_authoring/specs_modular_v1/Playground_Seesaw.md``.

A playground seesaw is a long balance beam that rocks about a single horizontal
pivot carried by a static central support, with opposed seats that swap height
when the beam tilts. The template composes three replaceable slots plus two
multiplicity axes:

- Slot A ``beam_form``: flat plank, tube truss, curved banana, heavy steel tube,
  compact short beam.
- Slot B ``pivot_mechanism``: central revolute teeter, central spring (prismatic)
  + revolute stack, locking-pin revolute.
- Slot C ``support_base``: crossed arched tube legs, splayed round-post legs,
  triangular A-frame, ground pedestal + cast bracket.
- Multiplicity 1 ``seat_count`` (seats per beam, in {2, 4, 6}).
- Multiplicity 2 ``beam_count`` (independent rocking beams, in {1, 2}).

The beam pivot revolute is always the primary non-fixed joint; the spring
mechanism adds a second non-fixed (prismatic) joint stacked below it.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Literal

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    Inertial,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
)

__modular__ = True


BeamForm = Literal[
    "flat_plank_beam",
    "tube_truss_beam",
    "curved_banana_beam",
    "heavy_steel_beam",
    "compact_short_beam",
]
PivotMechanism = Literal[
    "central_revolute_teeter",
    "spring_prismatic_revolute",
    "locking_pin_revolute",
]
SupportBase = Literal[
    "arched_tube_legs",
    "round_post_legs",
    "triangular_a_frame",
    "pedestal_bracket",
]
PaletteTheme = Literal["mustard_galvanized", "sky_blue_yellow", "gloss_red_gray", "park_green"]

BEAM_FORMS: tuple[BeamForm, ...] = (
    "flat_plank_beam",
    "tube_truss_beam",
    "curved_banana_beam",
    "heavy_steel_beam",
    "compact_short_beam",
)
PIVOT_MECHANISMS: tuple[PivotMechanism, ...] = (
    "central_revolute_teeter",
    "spring_prismatic_revolute",
    "locking_pin_revolute",
)
SUPPORT_BASES: tuple[SupportBase, ...] = (
    "arched_tube_legs",
    "round_post_legs",
    "triangular_a_frame",
    "pedestal_bracket",
)
SEAT_COUNTS: tuple[int, ...] = (2, 4, 6)
SEAT_COUNT_WEIGHTS: tuple[float, ...] = (0.70, 0.22, 0.08)
BEAM_COUNTS: tuple[int, ...] = (1, 2)
BEAM_COUNT_WEIGHTS: tuple[float, ...] = (0.70, 0.30)

# Bases that can carry two stacked pivot axles (crossed twin beams).
TWIN_CAPABLE_BASES: tuple[SupportBase, ...] = (
    "arched_tube_legs",
    "round_post_legs",
    "triangular_a_frame",
)

PALETTES: dict[PaletteTheme, dict[str, tuple[float, float, float, float]]] = {
    "mustard_galvanized": {
        "beam": (0.74, 0.53, 0.12, 1.0),
        "base": (0.55, 0.58, 0.56, 1.0),
        "axle": (0.42, 0.25, 0.13, 1.0),
        "seat": (0.60, 0.45, 0.28, 1.0),
        "handle": (0.70, 0.66, 0.58, 1.0),
        "rubber": (0.08, 0.08, 0.08, 1.0),
        "spring": (0.48, 0.50, 0.52, 1.0),
    },
    "sky_blue_yellow": {
        "beam": (0.87, 0.74, 0.12, 1.0),
        "base": (0.33, 0.62, 0.84, 1.0),
        "axle": (0.42, 0.21, 0.13, 1.0),
        "seat": (0.42, 0.21, 0.13, 1.0),
        "handle": (0.87, 0.74, 0.12, 1.0),
        "rubber": (0.07, 0.07, 0.07, 1.0),
        "spring": (0.50, 0.52, 0.54, 1.0),
    },
    "gloss_red_gray": {
        "beam": (0.88, 0.20, 0.06, 1.0),
        "base": (0.78, 0.78, 0.79, 1.0),
        "axle": (0.09, 0.09, 0.10, 1.0),
        "seat": (0.34, 0.36, 0.38, 1.0),
        "handle": (0.34, 0.36, 0.38, 1.0),
        "rubber": (0.06, 0.06, 0.06, 1.0),
        "spring": (0.52, 0.54, 0.56, 1.0),
    },
    "park_green": {
        "beam": (0.20, 0.36, 0.23, 1.0),
        "base": (0.62, 0.65, 0.66, 1.0),
        "axle": (0.10, 0.11, 0.12, 1.0),
        "seat": (0.58, 0.39, 0.20, 1.0),
        "handle": (0.70, 0.72, 0.73, 1.0),
        "rubber": (0.035, 0.035, 0.035, 1.0),
        "spring": (0.50, 0.52, 0.54, 1.0),
    },
}


@dataclass(frozen=True)
class SeesawConfig:
    beam_form: BeamForm = "flat_plank_beam"
    pivot_mechanism: PivotMechanism = "central_revolute_teeter"
    support_base: SupportBase = "arched_tube_legs"
    beam_count: int = 1
    seat_count: int = 2
    ground_pads: bool = False
    palette_theme: PaletteTheme = "mustard_galvanized"
    beam_length: float = 2.8
    pivot_z: float = 0.60
    tilt: float = 0.33
    asym_offset: float = 0.0
    name: str = "playground_seesaw"
    palette: dict[str, tuple[float, float, float, float]] = field(default_factory=dict)


@dataclass(frozen=True)
class ResolvedSeesawConfig:
    beam_form: BeamForm
    pivot_mechanism: PivotMechanism
    support_base: SupportBase
    beam_count: int
    seat_count: int
    ground_pads: bool
    palette_theme: PaletteTheme
    beam_length: float
    pivot_z: float
    tilt: float
    asym_offset: float
    seat_drop: float
    seat_x: float
    spring_travel: float
    yaw: float
    name: str
    palette: dict[str, tuple[float, float, float, float]]


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, float(value)))


def _weighted_choice(rng: random.Random, items: tuple, weights: tuple[float, ...]):
    return rng.choices(list(items), weights=list(weights), k=1)[0]


# ---------------------------------------------------------------------------
# Sampling
# ---------------------------------------------------------------------------
def config_from_seed(seed: int) -> SeesawConfig:
    rng = random.Random(seed * 7919 + 31)

    beam_form: BeamForm = rng.choice(BEAM_FORMS)
    pivot_mechanism: PivotMechanism = rng.choice(PIVOT_MECHANISMS)
    support_base: SupportBase = rng.choice(SUPPORT_BASES)
    seat_count = _weighted_choice(rng, SEAT_COUNTS, SEAT_COUNT_WEIGHTS)
    beam_count = _weighted_choice(rng, BEAM_COUNTS, BEAM_COUNT_WEIGHTS)
    palette_theme: PaletteTheme = rng.choice(tuple(PALETTES.keys()))

    if beam_form == "compact_short_beam":
        beam_length = rng.uniform(2.0, 2.4)
    elif beam_form == "heavy_steel_beam":
        beam_length = rng.uniform(2.6, 3.2)
    else:
        beam_length = rng.uniform(2.4, 3.1)

    pivot_z = rng.uniform(0.34, 0.82)
    tilt = rng.uniform(0.26, 0.40)
    asym_offset = rng.uniform(0.0, 0.10) if rng.random() < 0.30 else 0.0

    return SeesawConfig(
        beam_form=beam_form,
        pivot_mechanism=pivot_mechanism,
        support_base=support_base,
        beam_count=beam_count,
        seat_count=seat_count,
        ground_pads=rng.random() < 0.45,
        palette_theme=palette_theme,
        beam_length=beam_length,
        pivot_z=pivot_z,
        tilt=tilt,
        asym_offset=asym_offset,
        name=f"seeded_playground_seesaw_{seed}",
    )


def resolve_config(config: SeesawConfig) -> ResolvedSeesawConfig:
    beam_form = config.beam_form if config.beam_form in BEAM_FORMS else "flat_plank_beam"
    pivot_mechanism = (
        config.pivot_mechanism
        if config.pivot_mechanism in PIVOT_MECHANISMS
        else "central_revolute_teeter"
    )
    support_base = (
        config.support_base if config.support_base in SUPPORT_BASES else "arched_tube_legs"
    )

    seat_count = int(config.seat_count) if config.seat_count in SEAT_COUNTS else 2
    beam_count = int(config.beam_count) if config.beam_count in BEAM_COUNTS else 1

    # --- compatibility gating -------------------------------------------------
    # A single central pedestal/bracket carries exactly one beam axle.
    if support_base == "pedestal_bracket":
        beam_count = 1
    # The central spring stack sits under one beam only.
    if pivot_mechanism == "spring_prismatic_revolute":
        beam_count = 1
    # The curved banana beam reads best on a single central support.
    if beam_form == "curved_banana_beam":
        beam_count = 1
        if support_base in ("round_post_legs", "triangular_a_frame"):
            support_base = "pedestal_bracket"

    beam_length = _clamp(config.beam_length, 2.0, 3.2)
    pivot_z = _clamp(config.pivot_z, 0.30, 0.85)
    tilt = _clamp(config.tilt, 0.20, 0.42)
    asym_offset = _clamp(config.asym_offset, 0.0, 0.10)

    half = beam_length / 2.0
    seat_x = half - 0.18  # seat center inset from the beam tip

    # Ground-clearance inequality: at full tilt the lowered beam tip must stay
    # above the ground. Approx tip drop below the pivot = seat_x * sin(tilt)
    # plus the static seat drop. Reduce tilt if the tip would punch through.
    seat_drop = _clamp(0.10 + 0.18 * (pivot_z - 0.30), 0.06, 0.30)
    clearance = 0.04
    while seat_x * math.sin(tilt) + seat_drop + asym_offset > pivot_z - clearance and tilt > 0.18:
        tilt -= 0.01
    tilt = max(tilt, 0.18)

    # Seat fan needs room along the beam; collapse to 2 if too short.
    if seat_count > 2 and beam_length < 2.5:
        seat_count = 2

    spring_travel = 0.06 if pivot_mechanism == "spring_prismatic_revolute" else 0.0
    yaw = math.radians(11.0) if beam_count == 2 else 0.0

    palette_theme = (
        config.palette_theme if config.palette_theme in PALETTES else "mustard_galvanized"
    )
    palette = dict(PALETTES[palette_theme])
    palette.update(config.palette or {})

    return ResolvedSeesawConfig(
        beam_form=beam_form,
        pivot_mechanism=pivot_mechanism,
        support_base=support_base,
        beam_count=beam_count,
        seat_count=seat_count,
        ground_pads=bool(config.ground_pads),
        palette_theme=palette_theme,
        beam_length=beam_length,
        pivot_z=pivot_z,
        tilt=tilt,
        asym_offset=asym_offset,
        seat_drop=seat_drop,
        seat_x=seat_x,
        spring_travel=spring_travel,
        yaw=yaw,
        name=config.name,
        palette=palette,
    )


# ---------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------
def _mat(model: ArticulatedObject, key: str, rgba: tuple[float, float, float, float]):
    return model.material(key, rgba=rgba)


def _segment_pose(
    start: tuple[float, float, float], end: tuple[float, float, float]
) -> tuple[Origin, float]:
    dx, dy, dz = end[0] - start[0], end[1] - start[1], end[2] - start[2]
    length = math.sqrt(dx * dx + dy * dy + dz * dz)
    if length <= 1e-9:
        return Origin(xyz=start), 1e-6
    yaw = math.atan2(dy, dx)
    pitch = math.acos(max(-1.0, min(1.0, dz / length)))
    mid = ((start[0] + end[0]) * 0.5, (start[1] + end[1]) * 0.5, (start[2] + end[2]) * 0.5)
    return Origin(xyz=mid, rpy=(0.0, pitch, yaw)), length


def _add_tube(part, name: str, start, end, radius: float, material) -> None:
    origin, length = _segment_pose(start, end)
    part.visual(Cylinder(radius=radius, length=length), origin=origin, material=material, name=name, material_class_id="metal.paint_coated")


# ---------------------------------------------------------------------------
# Support base (static)
# ---------------------------------------------------------------------------
def _pivot_heights(r: ResolvedSeesawConfig) -> tuple[float, ...]:
    """Per-beam pivot heights; twin beams stack so they clear each other."""
    if r.beam_count == 1:
        return (r.pivot_z,)
    # Twin crossed beams stack with enough vertical gap that the lower beam's
    # top clears the upper beam's downward-hanging pivot sleeve.
    gap = _beam_top_z(r) + (_beam_top_z(r) - 0.03) + 0.06
    return (r.pivot_z, r.pivot_z + gap)


def _build_base(model: ArticulatedObject, r: ResolvedSeesawConfig):
    base_mat = _mat(model, "base_steel", r.palette["base"])
    axle_mat = _mat(model, "axle_steel", r.palette["axle"])
    rubber = _mat(model, "ground_rubber", r.palette["rubber"])

    base = model.part("base")
    base.inertial = Inertial.from_geometry(
        Box((0.9, 0.9, r.pivot_z + 0.2)),
        mass=60.0,
        origin=Origin(xyz=(0.0, 0.0, (r.pivot_z + 0.2) * 0.5)),
    )

    heights = _pivot_heights(r)
    foot_y = 0.34
    axle_len = 0.22

    if r.support_base == "pedestal_bracket":
        ped_h = max(0.12, r.pivot_z - 0.10)
        base.visual(
            Cylinder(radius=0.09, length=ped_h),
            origin=Origin(xyz=(0.0, 0.0, ped_h / 2.0)),
            material=base_mat,
            name="ground_pedestal", material_class_id="metal.paint_coated",
        )
        base.visual(
            Box((0.17, 0.15, 0.20)),
            origin=Origin(xyz=(0.0, 0.0, r.pivot_z - 0.04)),
            material=axle_mat,
            name="pivot_bracket", material_class_id="metal.cast_iron_bare",
        )
    elif r.support_base == "arched_tube_legs":
        for bi, pz in enumerate(heights):
            for si, side in enumerate((1.0, -1.0)):
                _add_tube(
                    base,
                    f"arch_{bi}_{si}",
                    (side * 0.40, side * foot_y, 0.02),
                    (0.0, side * 0.04, pz),
                    0.024,
                    base_mat,
                )
    elif r.support_base == "round_post_legs":
        for bi, pz in enumerate(heights):
            for si, side in enumerate((1.0, -1.0)):
                _add_tube(
                    base,
                    f"leg_{bi}_{si}",
                    (0.0, side * foot_y, 0.02),
                    (0.0, side * 0.05, pz),
                    0.028,
                    base_mat,
                )
    else:  # triangular_a_frame
        for bi, pz in enumerate(heights):
            for si, side in enumerate((1.0, -1.0)):
                _add_tube(
                    base,
                    f"aframe_{bi}_{si}",
                    (side * 0.30, side * foot_y, 0.02),
                    (0.0, 0.0, pz),
                    0.026,
                    base_mat,
                )
            # Cross brace tying the two converging legs at mid height. Legs at
            # z = pz*0.45 sit near (±0.165, ±0.187); span the brace across both.
            _add_tube(
                base,
                f"aframe_cross_{bi}",
                (-0.18, -0.20, pz * 0.45),
                (0.18, 0.20, pz * 0.45),
                0.022,
                base_mat,
            )

    # Pivot axle bolt (or bracket pin) at each pivot height, axis along beam yaw.
    for bi, pz in enumerate(heights):
        ay = -r.yaw if bi == 1 else r.yaw
        # axle runs perpendicular to the beam (rotate by yaw about Z then lay on Y)
        base.visual(
            Cylinder(radius=0.03, length=axle_len),
            origin=Origin(xyz=(0.0, 0.0, pz), rpy=(math.pi / 2.0, 0.0, ay)),
            material=axle_mat,
            name=f"pivot_axle_{bi}", material_class_id="metal.steel_bare",
        )

    if r.ground_pads and r.support_base != "pedestal_bracket":
        # Pads sit under the leg feet so they touch the base legs (not floating).
        foot_x = (
            0.40
            if r.support_base == "arched_tube_legs"
            else (0.30 if r.support_base == "triangular_a_frame" else 0.0)
        )
        for si, side in enumerate((1.0, -1.0)):
            base.visual(
                Box((max(0.18, 2 * foot_x + 0.16), 0.18, 0.05)),
                origin=Origin(xyz=(0.0, side * foot_y, 0.03)),
                material=rubber,
                name=f"ground_pad_{si}", material_class_id="rubber.smooth_plain",
            )
    elif r.ground_pads:  # pedestal: a single ring pad under the column foot
        base.visual(
            Cylinder(radius=0.13, length=0.04),
            origin=Origin(xyz=(0.0, 0.0, 0.02)),
            material=rubber,
            name="ground_pad_0", material_class_id="rubber.smooth_plain",
        )

    return base


# ---------------------------------------------------------------------------
# Beam form geometry (authored in the beam-local frame, pivot at origin)
# ---------------------------------------------------------------------------
def _beam_body(part, r: ResolvedSeesawConfig, beam_mat, axle_mat) -> None:
    half = r.beam_length / 2.0
    form = r.beam_form

    # Pivot sleeve captured on the base axle. Centered at the beam-local origin
    # (so the revolute origin coincides with it), sized to reach up into the beam
    # body above it (no floating island).
    sleeve_r = _beam_top_z(r) - 0.03  # reaches the beam-body bottom
    part.visual(
        Cylinder(radius=sleeve_r, length=0.07),
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=axle_mat,
        name="pivot_sleeve", material_class_id="metal.steel_bare",
    )

    if form == "flat_plank_beam":
        part.visual(
            Box((r.beam_length, 0.10, 0.05)),
            origin=Origin(xyz=(0.0, 0.0, 0.06)),
            material=beam_mat,
            name="beam_body", material_class_id="wood.painted_clean",
        )
    elif form == "compact_short_beam":
        part.visual(
            Box((r.beam_length, 0.09, 0.045)),
            origin=Origin(xyz=(0.0, 0.0, 0.055)),
            material=beam_mat,
            name="beam_body", material_class_id="wood.painted_clean",
        )
    elif form == "heavy_steel_beam":
        part.visual(
            Cylinder(radius=0.06, length=r.beam_length),
            origin=Origin(xyz=(0.0, 0.0, 0.08), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=beam_mat,
            name="beam_body", material_class_id="metal.paint_coated",
        )
    elif form == "tube_truss_beam":
        # Main top tube + two diagonal braces meeting near the sleeve.
        part.visual(
            Cylinder(radius=0.025, length=r.beam_length),
            origin=Origin(xyz=(0.0, 0.0, 0.10), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=beam_mat,
            name="beam_body", material_class_id="metal.paint_coated",
        )
        for si, side in enumerate((1.0, -1.0)):
            _add_tube(
                part,
                f"brace_{si}",
                (side * 0.05, 0.0, 0.02),
                (side * 0.55, 0.0, 0.10),
                0.016,
                beam_mat,
            )
    else:  # curved_banana_beam (segmented straight tubes approximating a dip)
        n = 8
        prev = None
        for k in range(n + 1):
            x = -half + r.beam_length * k / n
            z = 0.06 + 0.16 * (x / half) ** 2  # dip at center, rise at ends
            cur = (x, 0.0, z)
            if prev is not None:
                _add_tube(part, f"banana_seg_{k}", prev, cur, 0.05, beam_mat)
            prev = cur


# ---------------------------------------------------------------------------
# Seat multiplicity (parent visuals on the beam part)
# ---------------------------------------------------------------------------
def _beam_top_z(r: ResolvedSeesawConfig) -> float:
    if r.beam_form in ("flat_plank_beam", "compact_short_beam"):
        return 0.085
    if r.beam_form == "heavy_steel_beam":
        return 0.14
    return 0.125


def _beam_top_at_x(r: ResolvedSeesawConfig, x: float) -> float:
    """Beam-body top surface z at station x (handles the curved banana dip)."""
    half = r.beam_length / 2.0
    if r.beam_form == "curved_banana_beam":
        center = 0.06 + 0.16 * (x / half) ** 2
        return center + 0.05  # + tube radius
    return _beam_top_z(r)


def _beam_half_width(r: ResolvedSeesawConfig) -> float:
    """Half Y-extent of the beam body geometry."""
    if r.beam_form == "flat_plank_beam":
        return 0.05
    if r.beam_form == "compact_short_beam":
        return 0.045
    if r.beam_form == "heavy_steel_beam":
        return 0.06
    if r.beam_form == "curved_banana_beam":
        return 0.05
    return 0.025  # tube_truss main tube


def _add_seats(part, r: ResolvedSeesawConfig, beam_mat, seat_mat, handle_mat, rubber) -> None:
    """Emit seat_count seats: half at +X end, half at -X end, fanned across Y."""
    per_end = r.seat_count // 2
    # lateral fan offsets centered on 0
    if per_end == 1:
        ys = (0.0,)
    else:
        spread = 0.13
        ys = tuple((j - (per_end - 1) / 2.0) * spread for j in range(per_end))

    body_half_w = _beam_half_width(r)  # half Y-extent of the beam body
    i = 0
    for end_sign in (1.0, -1.0):
        end_drop = r.asym_offset if end_sign > 0 else 0.0
        for dy in ys:
            sx = end_sign * r.seat_x
            top_at = _beam_top_at_x(r, sx)  # body top at this station
            seat_z = top_at + 0.06 - end_drop
            # Support post bridging the beam body up to the seat. It spans from
            # inside the beam body (touching it, including the lateral fan dy)
            # to the seat underside, so neither floats.
            # First a lateral foot rail embedded in the beam if the seat is
            # fanned out beyond the beam body width.
            if abs(dy) > body_half_w - 0.02:
                _add_tube(
                    part,
                    f"seat_rail_{i}",
                    (sx, 0.0, top_at - 0.04),
                    (sx, dy, top_at - 0.01),
                    0.018,
                    beam_mat,
                )
            _add_tube(
                part,
                f"seat_post_{i}",
                (sx, dy, top_at - 0.04),
                (sx, dy, seat_z),
                0.018,
                beam_mat,
            )
            part.visual(
                Box((0.26, 0.22, 0.030)),
                origin=Origin(xyz=(sx, dy, seat_z)),
                material=seat_mat,
                name=f"seat_{i}", material_class_id="plastic.opaque_glossy_molded",
            )
            # raised lip on the seat (overlaps the seat plate)
            part.visual(
                Box((0.26, 0.22, 0.020)),
                origin=Origin(xyz=(sx, dy, seat_z + 0.020)),
                material=seat_mat,
                name=f"seat_lip_{i}", material_class_id="plastic.opaque_glossy_molded",
            )
            # upright grab handle just inboard of the seat, rooted in the beam
            hx = end_sign * (r.seat_x - 0.26)
            h_top_at = _beam_top_at_x(r, hx)
            if abs(dy) > body_half_w - 0.02:
                # lateral rail rooting the handle into the on-axis beam body
                _add_tube(
                    part,
                    f"handle_rail_{i}",
                    (hx, 0.0, h_top_at - 0.05),
                    (hx, dy, h_top_at - 0.01),
                    0.014,
                    beam_mat,
                )
            _add_tube(
                part,
                f"handle_{i}",
                (hx, dy, h_top_at - 0.10),
                (hx, dy, h_top_at + 0.26),
                0.012,
                handle_mat,
            )
            part.visual(
                Cylinder(radius=0.012, length=0.16),
                origin=Origin(xyz=(hx, dy, h_top_at + 0.25), rpy=(math.pi / 2.0, 0.0, 0.0)),
                material=handle_mat,
                name=f"handle_bar_{i}", material_class_id="metal.paint_coated",
            )
            # rubber bumper under the beam tip (one per outer seat row), hung
            # off the seat post so it overlaps connected geometry.
            if abs(dy) >= (max(ys) - 1e-6) and r.beam_form != "curved_banana_beam":
                part.visual(
                    Box((0.12, 0.09, 0.07)),
                    origin=Origin(xyz=(sx, dy, top_at - 0.07)),
                    material=rubber,
                    name=f"bumper_{i}", material_class_id="rubber.smooth_plain",
                )
            i += 1


# ---------------------------------------------------------------------------
# Per-beam assembly + pivot mechanism
# ---------------------------------------------------------------------------
def _build_beam(model: ArticulatedObject, r: ResolvedSeesawConfig, b: int, pivot_z: float) -> None:
    beam_mat = _mat(model, f"beam_{b}_paint", r.palette["beam"])
    axle_mat = _mat(model, f"beam_{b}_axle", r.palette["axle"])
    seat_mat = _mat(model, f"beam_{b}_seat", r.palette["seat"])
    handle_mat = _mat(model, f"beam_{b}_handle", r.palette["handle"])
    rubber = _mat(model, f"beam_{b}_rubber", r.palette["rubber"])
    spring_mat = _mat(model, f"beam_{b}_spring", r.palette["spring"])

    yaw = -r.yaw if b == 1 else r.yaw
    limits = MotionLimits(effort=200.0, velocity=2.5, lower=-r.tilt, upper=r.tilt)

    beam = model.part(f"beam_{b}")
    _beam_body(beam, r, beam_mat, axle_mat)
    _add_seats(beam, r, beam_mat, seat_mat, handle_mat, rubber)

    if r.pivot_mechanism == "spring_prismatic_revolute":
        # base -> spring_hub (prismatic Z) -> beam (revolute Y)
        hub = model.part(f"spring_hub_{b}")
        hub.visual(
            Cylinder(radius=0.07, length=0.04),
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
            material=spring_mat,
            name="hub_plate", material_class_id="metal.stainless_matte",
        )
        # coil spring (approximated as a short fat cylinder) below the hub
        hub.visual(
            Cylinder(radius=0.045, length=max(0.08, pivot_z - 0.12)),
            origin=Origin(xyz=(0.0, 0.0, -(max(0.08, pivot_z - 0.12)) / 2.0 - 0.02)),
            material=spring_mat,
            name="coil_spring", material_class_id="metal.stainless_matte",
        )
        model.articulation(
            f"beam_{b}_spring",
            ArticulationType.PRISMATIC,
            parent="base",
            child=hub,
            origin=Origin(xyz=(0.0, 0.0, pivot_z)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(
                effort=400.0, velocity=0.5, lower=-r.spring_travel, upper=0.0
            ),
        )
        model.articulation(
            f"beam_{b}_pivot",
            ArticulationType.REVOLUTE,
            parent=hub,
            child=beam,
            origin=Origin(rpy=(0.0, 0.0, yaw)),
            axis=(0.0, 1.0, 0.0),
            motion_limits=limits,
        )
    else:
        if r.pivot_mechanism == "locking_pin_revolute":
            # visible locking-pin / axle-cap boss on the base bracket cheeks
            base = model.get_part("base")
            cap_mat = _mat(model, f"beam_{b}_cap", r.palette["axle"])
            for si, side in enumerate((1.0, -1.0)):
                base.visual(
                    Cylinder(radius=0.03, length=0.02),
                    origin=Origin(xyz=(0.0, side * 0.12, pivot_z), rpy=(math.pi / 2.0, 0.0, yaw)),
                    material=cap_mat,
                    name=f"axle_cap_{b}_{si}", material_class_id="metal.steel_bare",
                )
            limits = MotionLimits(
                effort=200.0, velocity=2.0, lower=-min(r.tilt, 0.30), upper=min(r.tilt, 0.30)
            )
        model.articulation(
            f"beam_{b}_pivot",
            ArticulationType.REVOLUTE,
            parent="base",
            child=beam,
            origin=Origin(xyz=(0.0, 0.0, pivot_z), rpy=(0.0, 0.0, yaw)),
            axis=(0.0, 1.0, 0.0),
            motion_limits=limits,
        )


# ---------------------------------------------------------------------------
# Top-level build
# ---------------------------------------------------------------------------
def build_seesaw(
    config: SeesawConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config or SeesawConfig())
    model = ArticulatedObject(name=r.name, assets=assets)
    _build_base(model, r)
    for b, pz in enumerate(_pivot_heights(r)):
        _build_beam(model, r, b, pz)
    model.meta["template_slug"] = "playground_seesaw"
    model.meta["beam_form"] = r.beam_form
    model.meta["pivot_mechanism"] = r.pivot_mechanism
    model.meta["support_base"] = r.support_base
    model.meta["beam_count"] = r.beam_count
    model.meta["seat_count"] = r.seat_count
    return model


def build_seeded_seesaw(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_seesaw(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Slot choices (topology signature)
# ---------------------------------------------------------------------------
def slot_choices_for_config(config: SeesawConfig) -> list[tuple[str, str]]:
    r = resolve_config(config)
    choices: list[tuple[str, str]] = [
        ("beam_form", r.beam_form),
        ("pivot_mechanism", r.pivot_mechanism),
        ("support_base", r.support_base),
        ("beam_count", f"{r.beam_count}_beams"),
        ("seat_count", f"{r.seat_count}_seats"),
        ("ground_pads", "pads" if r.ground_pads else "no_pads"),
    ]
    return choices


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def run_seesaw_tests(object_model: ArticulatedObject, config: SeesawConfig) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    parts = {part.name for part in object_model.parts}
    joints = {joint.name: joint for joint in object_model.articulations}
    base = object_model.get_part("base")

    # Captured-pin overlaps: each beam sleeve wraps its base axle; spring hubs
    # are captured at the bracket/spring stack.
    for b in range(r.beam_count):
        beam = object_model.get_part(f"beam_{b}")
        ctx.allow_overlap(
            beam,
            base,
            reason="Beam pivot sleeve and base axle/bracket intentionally nest at the shared pivot.",
        )
        hub = next((p for p in object_model.parts if p.name == f"spring_hub_{b}"), None)
        if hub is not None:
            ctx.allow_overlap(
                hub,
                base,
                reason="Spring hub plate is captured on the central bracket/spring stack.",
            )
            ctx.allow_overlap(
                beam,
                hub,
                reason="Beam pivot sleeve rides on the spring hub pivot.",
            )

    ctx.check_model_valid()

    # Base present and static.
    ctx.check("base_present", "base" in parts)
    base_aabb = ctx.part_world_aabb(base)
    ctx.check(
        "base_feet_on_ground",
        base_aabb is not None and -0.02 <= base_aabb[0][2] <= 0.06,
        details=f"base aabb={base_aabb}",
    )

    ctx.check("beam_count_matches", sum(1 for n in parts if n.startswith("beam_")) == r.beam_count)

    for b in range(r.beam_count):
        beam_name = f"beam_{b}"
        ctx.check(f"{beam_name}_present", beam_name in parts)
        pivot = joints.get(f"{beam_name}_pivot")
        ctx.check(f"{beam_name}_has_pivot", pivot is not None)
        if pivot is None:
            continue
        # Primary non-fixed joint is a revolute about a horizontal axis.
        ctx.check(
            f"{beam_name}_pivot_is_revolute",
            pivot.joint_type == ArticulationType.REVOLUTE,
            details=str(pivot.joint_type),
        )
        ax = pivot.axis
        ctx.check(
            f"{beam_name}_pivot_axis_horizontal",
            abs(ax[2]) < 1e-6 and (abs(ax[1]) > 0.5 or abs(ax[0]) > 0.5),
            details=f"axis={ax}",
        )
        lim = pivot.motion_limits
        ctx.check(
            f"{beam_name}_pivot_has_rock_range",
            lim is not None
            and lim.lower is not None
            and lim.upper is not None
            and lim.upper > 0.15
            and lim.lower < -0.15,
            details=f"limits=({None if lim is None else lim.lower}, "
            f"{None if lim is None else lim.upper})",
        )

        # All seat_count seats + handles exist for this beam.
        beam = object_model.get_part(beam_name)
        for i in range(r.seat_count):
            seat = ctx.part_element_world_aabb(beam, elem=f"seat_{i}")
            handle = ctx.part_element_world_aabb(beam, elem=f"handle_{i}")
            ctx.check(
                f"{beam_name}_seat_{i}_present",
                seat is not None and handle is not None,
                details=f"seat={seat}, handle={handle}",
            )

        # Opposed seats swap height when the beam rocks.
        seat0_rest = ctx.part_element_world_aabb(beam, elem="seat_0")
        last = r.seat_count - 1
        seatN_rest = ctx.part_element_world_aabb(beam, elem=f"seat_{last}")
        with ctx.pose({pivot: lim.upper}):
            seat0_up = ctx.part_element_world_aabb(beam, elem="seat_0")
            seatN_up = ctx.part_element_world_aabb(beam, elem=f"seat_{last}")
            beam_posed = ctx.part_world_aabb(beam)
            ctx.check(
                f"{beam_name}_seats_swap_height",
                seat0_rest is not None
                and seat0_up is not None
                and seatN_rest is not None
                and seatN_up is not None
                and (seat0_up[0][2] - seat0_rest[0][2]) * (seatN_up[0][2] - seatN_rest[0][2]) < 0,
                details=f"seat0 {seat0_rest}->{seat0_up}, seatN {seatN_rest}->{seatN_up}",
            )
            ctx.check(
                f"{beam_name}_clears_ground_at_tilt",
                beam_posed is not None and beam_posed[0][2] > -0.02,
                details=f"beam aabb={beam_posed}",
            )

    # Spring variant: the prismatic compression joint exists and is non-fixed.
    if r.pivot_mechanism == "spring_prismatic_revolute":
        spring = joints.get("beam_0_spring")
        ctx.check(
            "spring_prismatic_present",
            spring is not None and spring.joint_type == ArticulationType.PRISMATIC,
            details=str(None if spring is None else spring.joint_type),
        )

    return ctx.report()


__all__ = [
    "SeesawConfig",
    "ResolvedSeesawConfig",
    "build_seesaw",
    "build_seeded_seesaw",
    "config_from_seed",
    "resolve_config",
    "run_seesaw_tests",
    "slot_choices_for_seed",
    "slot_choices_for_config",
    "__modular__",
]
