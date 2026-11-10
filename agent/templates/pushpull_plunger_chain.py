# SPDX-License-Identifier: Apache-2.0

# ruff: noqa: E501
"""Design-backed procedural template for category `pushpull_plunger_chain`.

Slots, candidates and evidence live in
`articraft_template_authoring/designs/pushpull_plunger_chain.json`, backed by
`articraft_template_authoring/source_maps/pushpull_plunger_chain.md`
(36 reviewed five-star records).

One clearance ledger owns the mechanism. `stroke` is *solved* from the guide
length and the engagement that has to stay captured - the deleted legacy
template picked a stroke independently and every stage pulled clean out of its
guide on every seed.
"""

from __future__ import annotations

import math
import random
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    AxisInterface,
    Box,
    Cylinder,
    Inertial,
    MotionLimits,
    Origin,
    TemplateDomain,
    TestContext,
    TestReport,
    component_slot,
    corner_case,
    mate_axes,
    multiplicity_slot,
    register_interface_mate,
)

SlideAxis = Literal["horizontal_x", "vertical_z"]
SupportHost = Literal[
    "closed_tube_bushed",
    "open_rail_box",
    "posted_bridge_frame",
    "wall_backplate",
    "bored_solid_block",
    "ground_bed_saddles",
]
GuideSection = Literal["round_bore", "rect_bore_retainer", "four_wall_channel"]
StageModule = Literal["bushed_sleeve_stage", "shoe_railed_stage", "plain_tube_stage"]
PlungerRod = Literal[
    "plain_round_rod", "stepped_lathe_rod", "square_bar", "collared_stop_rod", "shoe_guided_rod"
]
InputEnd = Literal["push_knob", "pull_knob", "thumb_button", "rear_collar_stop"]
OutputMember = Literal[
    "hinged_tab_plate",
    "simple_lever_pad",
    "lever_with_roller",
    "nose_latch_hook",
    "flap_paddle_heel",
    "bar_lever_output_tip",
]
HingeCarrier = Literal["host_mounted", "plunger_carried"]
PaletteStyle = Literal["dark_shop", "zinc_black", "green_bronze", "blue_shop"]

TEMPLATE_DOMAIN = TemplateDomain(
    slots=(
        component_slot("slide_axis", ("horizontal_x", "vertical_z")),
        component_slot(
            "support_host",
            (
                "closed_tube_bushed",
                "open_rail_box",
                "posted_bridge_frame",
                "wall_backplate",
                "bored_solid_block",
                "ground_bed_saddles",
            ),
        ),
        component_slot("guide_section", ("round_bore", "rect_bore_retainer", "four_wall_channel")),
        component_slot(
            "stage_module", ("bushed_sleeve_stage", "shoe_railed_stage", "plain_tube_stage")
        ),
        component_slot(
            "plunger_rod",
            (
                "plain_round_rod",
                "stepped_lathe_rod",
                "square_bar",
                "collared_stop_rod",
                "shoe_guided_rod",
            ),
        ),
        component_slot(
            "input_end", ("push_knob", "pull_knob", "thumb_button", "rear_collar_stop")
        ),
        component_slot(
            "output_member",
            (
                "hinged_tab_plate",
                "simple_lever_pad",
                "lever_with_roller",
                "nose_latch_hook",
                "flap_paddle_heel",
                "bar_lever_output_tip",
            ),
        ),
        component_slot("hinge_carrier", ("host_mounted", "plunger_carried")),
        multiplicity_slot("stage_count", (1, 2, 3), item_slot="stage_module"),
    )
)

PALETTES: dict[str, dict[str, tuple[float, float, float, float]]] = {
    "dark_shop": {
        "frame": (0.22, 0.24, 0.26, 1.0),
        "guide": (0.56, 0.58, 0.60, 1.0),
        "rod": (0.76, 0.78, 0.80, 1.0),
        "accent": (0.78, 0.42, 0.14, 1.0),
        "pin": (0.07, 0.075, 0.08, 1.0),
    },
    "zinc_black": {
        "frame": (0.08, 0.085, 0.09, 1.0),
        "guide": (0.68, 0.70, 0.73, 1.0),
        "rod": (0.12, 0.13, 0.14, 1.0),
        "accent": (0.58, 0.20, 0.14, 1.0),
        "pin": (0.50, 0.52, 0.55, 1.0),
    },
    "green_bronze": {
        "frame": (0.18, 0.32, 0.23, 1.0),
        "guide": (0.63, 0.50, 0.28, 1.0),
        "rod": (0.72, 0.74, 0.70, 1.0),
        "accent": (0.88, 0.58, 0.15, 1.0),
        "pin": (0.10, 0.13, 0.10, 1.0),
    },
    "blue_shop": {
        "frame": (0.10, 0.18, 0.32, 1.0),
        "guide": (0.62, 0.65, 0.70, 1.0),
        "rod": (0.84, 0.86, 0.88, 1.0),
        "accent": (0.90, 0.62, 0.10, 1.0),
        "pin": (0.05, 0.06, 0.07, 1.0),
    },
}

HALF_PI = math.pi / 2.0
# Running clearance between a rod and the bore it slides in. Inside the 1 mm
# part-to-part support band, so the rod always reads as captured.
RUN_CLEAR = 0.0007
# Overlap used when one solid must visibly bite into the one it is mounted on.
BITE = 0.0015


@dataclass(frozen=True)
class Config:
    slide_axis: SlideAxis = "horizontal_x"
    support_host: SupportHost = "closed_tube_bushed"
    guide_section: GuideSection = "round_bore"
    stage_module: StageModule = "bushed_sleeve_stage"
    plunger_rod: PlungerRod = "plain_round_rod"
    input_end: InputEnd = "push_knob"
    output_member: OutputMember = "simple_lever_pad"
    hinge_carrier: HingeCarrier = "host_mounted"
    stage_count: int = 1
    guide_length_m: float = 0.150
    bore_size_m: float = 0.028
    host_scale: float = 1.0
    palette_style: PaletteStyle = "dark_shop"
    name: str = "pushpull_plunger_chain"


@dataclass(frozen=True)
class ResolvedConfig:
    slide_axis: SlideAxis
    support_host: SupportHost
    guide_section: GuideSection
    stage_module: StageModule
    plunger_rod: PlungerRod
    input_end: InputEnd
    output_member: OutputMember
    hinge_carrier: HingeCarrier
    stage_count: int
    palette_style: PaletteStyle
    palette: dict[str, tuple[float, float, float, float]]
    name: str
    # the ledger, one entry per stage
    bore_half: tuple[float, ...]
    rod_half: tuple[float, ...]
    guide_len: tuple[float, ...]
    engage_min: tuple[float, ...]
    stroke: tuple[float, ...]
    rod_len: tuple[float, ...]
    wall: tuple[float, ...]
    # host frame
    host_len: float
    axis_h: float
    host_half: float
    tip_full_s: float
    hinge_s: float
    hinge_local_s: float
    pivot_r: float
    out_reach: float


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(v)))


def config_from_seed(seed: int) -> Config:
    rng = random.Random(int(seed) ^ 0x5055_5348_5055_4C4C)
    ch = TEMPLATE_DOMAIN.sample(rng)
    return Config(
        slide_axis=ch["slide_axis"],
        support_host=ch["support_host"],
        guide_section=ch["guide_section"],
        stage_module=ch["stage_module"],
        plunger_rod=ch["plunger_rod"],
        input_end=ch["input_end"],
        output_member=ch["output_member"],
        hinge_carrier=ch["hinge_carrier"],
        stage_count=ch["stage_count"],
        guide_length_m=round(rng.uniform(0.10, 0.26), 4),
        bore_size_m=round(rng.uniform(0.020, 0.042), 4),
        host_scale=round(rng.uniform(0.88, 1.25), 4),
        palette_style=rng.choice(tuple(PALETTES)),
        name=f"pushpull_plunger_chain_seed_{int(seed)}",
    )


def resolve_config(config: Config) -> ResolvedConfig:
    TEMPLATE_DOMAIN.validate(
        {
            "slide_axis": config.slide_axis,
            "support_host": config.support_host,
            "guide_section": config.guide_section,
            "stage_module": config.stage_module,
            "plunger_rod": config.plunger_rod,
            "input_end": config.input_end,
            "output_member": config.output_member,
            "hinge_carrier": config.hinge_carrier,
            "stage_count": config.stage_count,
        }
    )
    if config.palette_style not in PALETTES:
        raise ValueError(f"unsupported palette_style: {config.palette_style}")

    n = int(config.stage_count)
    g0 = _clamp(config.guide_length_m, 0.10, 0.26)
    b0 = _clamp(config.bore_size_m, 0.020, 0.042) / 2.0
    scale = _clamp(config.host_scale, 0.88, 1.25)

    bore_half: list[float] = []
    rod_half: list[float] = []
    guide_len: list[float] = []
    engage_min: list[float] = []
    stroke: list[float] = []
    rod_len: list[float] = []
    wall: list[float] = []
    bh, gl = b0, g0
    for _k in range(n):
        rh = bh - RUN_CLEAR
        if rh <= 0.0035:
            raise ValueError("bore is too small for another nested stage")
        em = max(0.018, bh * 2.4)
        if gl <= em + 0.006:
            raise ValueError("guide is too short to keep the stage captured")
        # Binding `stroke_from_guide_engagement`: the law the old template broke.
        st = _clamp(gl - em, 0.006, gl * 0.62)
        bore_half.append(bh)
        rod_half.append(rh)
        guide_len.append(gl)
        engage_min.append(em)
        stroke.append(st)
        rod_len.append(gl + st + rh * 1.6)
        wall.append(max(0.0035, bh * 0.34))
        # The nest has to still leave a usable bore at the deepest stage, so the
        # shrink is gentle enough for the smallest declared bore at N=3.
        bh = max(rh * 0.78, 0.0055)
        gl = gl * 0.82

    host_len = (guide_len[0] + max(guide_len[0] * 0.35, 0.05)) * scale
    host_half = max(bore_half[0] * 2.6, 0.030) * scale
    axis_h = host_half + max(0.012, bore_half[0] * 0.9)

    # Where the last stage's tip sits at full extension, in host coordinates.
    tip = 0.0
    for k in range(n):
        tip += stroke[k]
        if k < n - 1:
            tip += rod_len[k]
    tip += rod_len[n - 1]
    tip_full_s = tip

    pivot_r = max(0.008, bore_half[0] * 0.55)
    out_reach = max(0.030, bore_half[0] * 3.4)
    # Binding `hinge_from_output_reach`: the pivot sits where the driven face is
    # actually swept by the stroke.
    # Ahead of the fully extended tip: a collar or bushing riding the rod would
    # otherwise sweep straight through the pivot station.
    hinge_s = tip_full_s + pivot_r * 0.5
    local = 0.0
    for k in range(n - 1):
        local += rod_len[k]
    hinge_local_s = hinge_s - local - sum(stroke[: n - 1])
    # the carried fork has to be on the rod, not past its end
    hinge_local_s = _clamp(hinge_local_s, guide_len[n - 1] + pivot_r * 2.0, rod_len[n - 1] - pivot_r * 1.2)

    return ResolvedConfig(
        slide_axis=config.slide_axis,
        support_host=config.support_host,
        guide_section=config.guide_section,
        stage_module=config.stage_module,
        plunger_rod=config.plunger_rod,
        input_end=config.input_end,
        output_member=config.output_member,
        hinge_carrier=config.hinge_carrier,
        stage_count=n,
        palette_style=config.palette_style,
        palette=PALETTES[config.palette_style],
        name=config.name or "pushpull_plunger_chain",
        bore_half=tuple(bore_half),
        rod_half=tuple(rod_half),
        guide_len=tuple(guide_len),
        engage_min=tuple(engage_min),
        stroke=tuple(stroke),
        rod_len=tuple(rod_len),
        wall=tuple(wall),
        host_len=host_len,
        axis_h=axis_h,
        host_half=host_half,
        tip_full_s=tip_full_s,
        hinge_s=hinge_s,
        hinge_local_s=hinge_local_s,
        pivot_r=pivot_r,
        out_reach=out_reach,
    )


def slot_choices_for_config(config: Config | ResolvedConfig) -> dict[str, object]:
    r = config if isinstance(config, ResolvedConfig) else resolve_config(config)
    return {
        "slide_axis": r.slide_axis,
        "support_host": r.support_host,
        "guide_section": r.guide_section,
        "stage_module": r.stage_module,
        "plunger_rod": r.plunger_rod,
        "input_end": r.input_end,
        "output_member": r.output_member,
        "hinge_carrier": r.hinge_carrier,
        "stage_count": r.stage_count,
    }


def slot_choices_for_seed(seed: int) -> dict[str, object]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# slide-relative frame: (s along the slide, u and v lateral)
# ---------------------------------------------------------------------------


def _horiz(r: ResolvedConfig) -> bool:
    return r.slide_axis == "horizontal_x"


def _v(r: ResolvedConfig, s: float, u: float, vv: float) -> tuple[float, float, float]:
    return (s, u, vv) if _horiz(r) else (u, vv, s)


def _sz(r: ResolvedConfig, ls: float, lu: float, lv: float) -> tuple[float, float, float]:
    return (ls, lu, lv) if _horiz(r) else (lu, lv, ls)


def _slide_vec(r: ResolvedConfig) -> tuple[float, float, float]:
    return (1.0, 0.0, 0.0) if _horiz(r) else (0.0, 0.0, 1.0)


def _hinge_vec(r: ResolvedConfig) -> tuple[float, float, float]:
    return (0.0, 1.0, 0.0) if _horiz(r) else (1.0, 0.0, 0.0)


def _rod_rpy(r: ResolvedConfig) -> tuple[float, float, float]:
    """rpy laying a Cylinder along the slide axis."""

    return (0.0, HALF_PI, 0.0) if _horiz(r) else (0.0, 0.0, 0.0)


def _hinge_rpy(r: ResolvedConfig) -> tuple[float, float, float]:
    return (HALF_PI, 0.0, 0.0) if _horiz(r) else (0.0, HALF_PI, 0.0)


def _box(part, name, size, xyz, mat, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(Box(size), origin=Origin(xyz=xyz, rpy=rpy), material=mat, name=name, material_class_id="metal.paint_coated")


def _cyl(part, name, radius, length, xyz, mat, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(
        Cylinder(radius=radius, length=length), origin=Origin(xyz=xyz, rpy=rpy), material=mat, name=name, material_class_id="metal.stainless_matte"
    )


# ---------------------------------------------------------------------------
# guide_section - the bore walls, drawn around the slide axis over [s0, s0+len]
# ---------------------------------------------------------------------------


def _ring_bars(part, r, mats, prefix, s_at, inner, thick, length, mat, segments: int = 8) -> None:
    """A ring built from `segments` bars so the bore stays genuinely open.

    An annular mesh is collided as its convex hull, which would fill the bore.
    The source records build their sleeves from real walls for the same reason.
    """

    radius = inner + thick * 0.5
    chord = 2.0 * math.pi * radius / segments * 1.25
    for i in range(segments):
        ang = 2.0 * math.pi * i / segments
        cu, cv = radius * math.cos(ang), radius * math.sin(ang)
        # The bar's thickness axis has to point radially, which is the local
        # frame rotated a quarter turn behind the station angle.
        spin = ang - HALF_PI
        rpy = (spin, 0.0, 0.0) if _horiz(r) else (0.0, 0.0, spin)
        _box(part, f"{prefix}_{i}", _sz(r, length, chord, thick), _v(r, s_at, cu, cv), mat, rpy=rpy)


def _frame(part, r, mats, prefix, s_at, inner: float, thick: float, length: float, mat) -> None:
    """Four bars around the bore, leaving the opening clear."""

    span = 2.0 * (inner + thick)
    for i, (du, dv) in enumerate(((0, 1), (0, -1), (1, 0), (-1, 0))):
        size = _sz(r, length, span if du == 0 else thick, thick if du == 0 else span)
        _box(part, f"{prefix}_{i}", size,
             _v(r, s_at, du * (inner + thick * 0.5), dv * (inner + thick * 0.5)), mat)


def _guide_section_round_bore_build(part, r, mats, s0, length, half, wall, tag) -> None:
    """Octagonal sleeve: a round housing built from eight real staves."""

    p = f"guide_section__round_bore__{tag}"
    _ring_bars(part, r, mats, f"{p}__stave", s0 + length * 0.5, half, wall, length, mats["guide"], segments=8)
    for i, sb in enumerate((s0 + wall * 1.2, s0 + length - wall * 1.2)):
        _ring_bars(part, r, mats, f"{p}__bushing_{i}", sb, half, wall * 1.9, wall * 2.0, mats["accent"], segments=8)


def _guide_section_rect_bore_retainer_build(part, r, mats, s0, length, half, wall, tag) -> None:
    """Rectangular sleeve closed by four-bar retainer frames at both ends."""

    p = f"guide_section__rect_bore_retainer__{tag}"
    _frame(part, r, mats, f"{p}__tube", s0 + length * 0.5, half, wall, length, mats["guide"])
    for i, sb in enumerate((s0 + wall * 1.4, s0 + length - wall * 1.4)):
        _frame(part, r, mats, f"{p}__retainer_{i}", sb, half + wall * 0.9, wall * 1.6, wall * 2.4, mats["accent"])


def _guide_section_four_wall_channel_build(part, r, mats, s0, length, half, wall, tag) -> None:
    """Floor, roof, sill and brow: a heavy asymmetric machined channel."""

    p = f"guide_section__four_wall_channel__{tag}"
    cs = s0 + length * 0.5
    deep, thin = wall * 1.7, wall * 0.85
    span = 2.0 * (half + deep)
    for i, (du, dv, t) in enumerate(((0, 1, thin), (0, -1, deep), (1, 0, wall), (-1, 0, wall))):
        size = _sz(r, length, span if du == 0 else t, t if du == 0 else span)
        _box(part, f"{p}__wall_{i}", size,
             _v(r, cs, du * (half + t * 0.5), dv * (half + t * 0.5)), mats["guide"])
    _box(part, f"{p}__front_sill", _sz(r, wall * 2.4, span, deep),
         _v(r, s0 + length - wall * 1.2, 0.0, -(half + deep * 0.5)), mats["frame"])


_SECTION_BUILDERS = {
    "round_bore": _guide_section_round_bore_build,
    "rect_bore_retainer": _guide_section_rect_bore_retainer_build,
    "four_wall_channel": _guide_section_four_wall_channel_build,
}


def _shell_outer(r: ResolvedConfig, k: int) -> float:
    """Outer half-size of the guide's continuous shell.

    Bushings and retainer frames stand proud of it at a couple of stations, so
    anything that clamps along the guide has to seat on this, not on the maximum.
    """

    extra = {"round_bore": 1.0, "rect_bore_retainer": 1.0, "four_wall_channel": 1.7}[r.guide_section]
    return r.bore_half[k] + r.wall[k] * extra


def _guide_outer(r: ResolvedConfig, k: int) -> float:
    """Outer half-size of guide `k`, whatever section is active."""

    extra = {"round_bore": 1.9, "rect_bore_retainer": 2.5, "four_wall_channel": 1.7}[r.guide_section]
    return r.bore_half[k] + r.wall[k] * extra


# ---------------------------------------------------------------------------
# slide_axis - the grounding structure under (or beneath) the bore
# ---------------------------------------------------------------------------


def _slide_axis_horizontal_x_build(part, r, mats) -> None:
    p = "slide_axis__horizontal_x"
    t = max(0.008, r.host_half * 0.22)
    _box(part, f"{p}__base_plate", _sz(r, r.host_len, r.host_half * 2.2, t),
         _v(r, r.host_len * 0.5 - r.host_len * 0.12, 0.0, -r.axis_h + t * 0.5), mats["frame"])
    top = -_guide_outer(r, 0) + BITE
    bottom = -r.axis_h + t - BITE
    if top > bottom:
        for i, s in enumerate((r.host_len * 0.12, r.host_len * 0.72)):
            _box(part, f"{p}__pedestal_{i}", _sz(r, r.host_half * 0.9, r.host_half * 1.4, top - bottom),
                 _v(r, s, 0.0, (top + bottom) * 0.5), mats["frame"])


def _slide_axis_vertical_z_build(part, r, mats) -> None:
    """Upright sleeve on a bored base ring, as the vertical source record has it.

    The base is a ring, not a slab: the rod and its rear knob run down through
    it, so a solid plate would sit exactly where the input feature travels.
    """

    p = "slide_axis__vertical_z"
    t = max(0.010, r.host_half * 0.26)
    o0 = _guide_outer(r, 0)
    clear = max(o0, r.rod_half[0] * 2.6) + BITE
    _ring_bars(part, r, mats, f"{p}__base_ring", -t * 0.35, clear, r.host_half * 1.1, t * 1.5, mats["frame"], segments=8)
    # radial gussets tie the ring back to the sleeve
    for i, (du, dv) in enumerate(((1, 0), (-1, 0), (0, 1), (0, -1))):
        span = clear - o0 + r.wall[0] * 2.0
        _box(part, f"{p}__gusset_{i}",
             _sz(r, t * 1.6, span if du else r.wall[0] * 2.2, r.wall[0] * 2.2 if du else span),
             _v(r, t * 0.55, du * (o0 + span * 0.5 - r.wall[0]), dv * (o0 + span * 0.5 - r.wall[0])),
             mats["frame"])
    _ring_bars(part, r, mats, f"{p}__clamp_ring", t * 0.35, o0 - BITE, r.wall[0] * 1.8 + BITE, t * 0.9, mats["frame"])


_AXIS_BUILDERS = {
    "horizontal_x": _slide_axis_horizontal_x_build,
    "vertical_z": _slide_axis_vertical_z_build,
}


# ---------------------------------------------------------------------------
# support_host - structure tying the ground to the guide
# ---------------------------------------------------------------------------


def _support_host_closed_tube_bushed_build(part, r, mats) -> None:
    p = "support_host__closed_tube_bushed"
    o = _shell_outer(r, 0)
    for i, sb in enumerate((r.guide_len[0] * 0.2, r.guide_len[0] * 0.8)):
        _ring_bars(part, r, mats, f"{p}__saddle_{i}", sb, o - BITE, (o + r.wall[0] * 1.4) - (o - BITE), r.wall[0] * 2.6, mats["frame"])


def _support_host_open_rail_box_build(part, r, mats) -> None:
    p = "support_host__open_rail_box"
    o = _shell_outer(r, 0)
    for i, (du, dv) in enumerate(((1, 0), (-1, 0))):
        _box(part, f"{p}__rail_{i}", _sz(r, r.guide_len[0], r.wall[0] * 1.8, o * 2.1),
             _v(r, r.guide_len[0] * 0.5, du * (o + r.wall[0] * 0.7), dv * 0.0), mats["frame"])


def _support_host_posted_bridge_frame_build(part, r, mats) -> None:
    p = "support_host__posted_bridge_frame"
    o = _shell_outer(r, 0)
    for i, sb in enumerate((r.guide_len[0] * 0.08, r.guide_len[0] * 0.92)):
        _frame(part, r, mats, f"{p}__post_{i}", sb, o - BITE, r.wall[0] * 1.8, r.wall[0] * 2.4, mats["frame"])
    _box(part, f"{p}__top_bridge", _sz(r, r.guide_len[0] * 0.9, o * 1.8, r.wall[0] * 2.0),
         _v(r, r.guide_len[0] * 0.5, 0.0, o + r.wall[0]), mats["frame"])


def _support_host_wall_backplate_build(part, r, mats) -> None:
    """Wall pad and saddle. The pad is bored so the rod's rear passes through."""

    p = "support_host__wall_backplate"
    o = _shell_outer(r, 0)
    t = max(0.008, r.host_half * 0.20)
    clear = max(o, r.rod_half[0] * 2.6) + BITE
    _ring_bars(part, r, mats, f"{p}__wall_pad", -t * 0.35, clear, r.host_half * 1.2, t * 1.5, mats["frame"], segments=8)
    for i, (du, dv) in enumerate(((1, 0), (-1, 0), (0, 1), (0, -1))):
        span = clear - o + r.wall[0] * 2.0
        _box(part, f"{p}__pad_gusset_{i}",
             _sz(r, t * 1.6, span if du else r.wall[0] * 2.2, r.wall[0] * 2.2 if du else span),
             _v(r, t * 0.55, du * (o + span * 0.5 - r.wall[0]), dv * (o + span * 0.5 - r.wall[0])),
             mats["frame"])
    _box(part, f"{p}__tube_saddle", _sz(r, r.guide_len[0] * 0.7, o * 1.6, r.wall[0] * 2.2),
         _v(r, r.guide_len[0] * 0.4, 0.0, -(o + r.wall[0])), mats["frame"])


def _support_host_bored_solid_block_build(part, r, mats) -> None:
    p = "support_host__bored_solid_block"
    o = _shell_outer(r, 0)
    for i, (du, dv) in enumerate(((1, 0), (-1, 0), (0, 1), (0, -1))):
        _box(part, f"{p}__flank_{i}",
             _sz(r, r.guide_len[0] * 0.86, r.wall[0] * 2.6 if du else o * 2.6,
                 o * 2.6 if du else r.wall[0] * 2.6),
             _v(r, r.guide_len[0] * 0.5, du * (o + r.wall[0] * 0.9), dv * (o + r.wall[0] * 0.9)),
             mats["frame"])


def _support_host_ground_bed_saddles_build(part, r, mats) -> None:
    p = "support_host__ground_bed_saddles"
    o = _shell_outer(r, 0)
    for i, sb in enumerate((r.guide_len[0] * 0.16, r.guide_len[0] * 0.84)):
        _frame(part, r, mats, f"{p}__saddle_web_{i}", sb, o - BITE, r.wall[0] * 1.7, r.wall[0] * 3.0, mats["frame"])
        _ring_bars(part, r, mats, f"{p}__clamp_ring_{i}", sb, o - BITE, (o + r.wall[0] * 1.7) - (o - BITE), r.wall[0] * 1.8, mats["accent"])


_HOST_BUILDERS = {
    "closed_tube_bushed": _support_host_closed_tube_bushed_build,
    "open_rail_box": _support_host_open_rail_box_build,
    "posted_bridge_frame": _support_host_posted_bridge_frame_build,
    "wall_backplate": _support_host_wall_backplate_build,
    "bored_solid_block": _support_host_bored_solid_block_build,
    "ground_bed_saddles": _support_host_ground_bed_saddles_build,
}


# ---------------------------------------------------------------------------
# plunger_rod - the shank running in the bore, authored from the stage origin
# ---------------------------------------------------------------------------


def _running_bands(part, r: ResolvedConfig, mats, k: int) -> None:
    """Bearing bands sized to the bore, always inside guide `k`.

    A stepped or shoe-guided shank is narrower than the bore, so without these
    the stage has nothing touching its guide and reads as floating.
    """

    rh = r.rod_half[k]
    inside = r.engage_min[k]
    width = min(r.wall[k] * 2.2, inside * 0.30)
    for i, f in enumerate((0.26, 0.74)):
        _cyl(part, f"plunger_rod__running_band__s{k}_{i}", rh, width,
             _v(r, inside * f, 0.0, 0.0), mats["accent"], rpy=_rod_rpy(r))


def _plunger_rod_plain_round_rod_build(part, r, mats, k) -> None:
    p = f"plunger_rod__plain_round_rod__s{k}"
    ln, rh = r.rod_len[k], r.rod_half[k]
    _cyl(part, f"{p}__shank", rh, ln, _v(r, ln * 0.5, 0.0, 0.0), mats["rod"], rpy=_rod_rpy(r))


def _plunger_rod_stepped_lathe_rod_build(part, r, mats, k) -> None:
    p = f"plunger_rod__stepped_lathe_rod__s{k}"
    ln, rh = r.rod_len[k], r.rod_half[k]
    _cyl(part, f"{p}__shank", rh, ln * 0.62, _v(r, ln * 0.31, 0.0, 0.0), mats["rod"], rpy=_rod_rpy(r))
    _cyl(part, f"{p}__land", rh * 1.12, ln * 0.12, _v(r, ln * 0.62, 0.0, 0.0), mats["rod"], rpy=_rod_rpy(r))
    _cyl(part, f"{p}__nose", rh * 0.74, ln * 0.34, _v(r, ln * 0.83, 0.0, 0.0), mats["rod"], rpy=_rod_rpy(r))


def _plunger_rod_square_bar_build(part, r, mats, k) -> None:
    p = f"plunger_rod__square_bar__s{k}"
    ln, rh = r.rod_len[k], r.rod_half[k] * 0.82
    _box(part, f"{p}__bar", _sz(r, ln, rh * 2.0, rh * 2.0), _v(r, ln * 0.5, 0.0, 0.0), mats["rod"])


def _plunger_rod_collared_stop_rod_build(part, r, mats, k) -> None:
    p = f"plunger_rod__collared_stop_rod__s{k}"
    ln, rh = r.rod_len[k], r.rod_half[k]
    _cyl(part, f"{p}__shank", rh * 0.86, ln, _v(r, ln * 0.5, 0.0, 0.0), mats["rod"], rpy=_rod_rpy(r))
    _cyl(part, f"{p}__guide_collar", rh, r.wall[k] * 2.4, _v(r, ln * 0.30, 0.0, 0.0), mats["rod"], rpy=_rod_rpy(r))
    _cyl(part, f"{p}__stop_collar", rh, r.wall[k] * 2.0, _v(r, r.wall[k] * 1.2, 0.0, 0.0), mats["accent"], rpy=_rod_rpy(r))


def _plunger_rod_shoe_guided_rod_build(part, r, mats, k) -> None:
    p = f"plunger_rod__shoe_guided_rod__s{k}"
    ln, rh = r.rod_len[k], r.rod_half[k]
    _cyl(part, f"{p}__shank", rh * 0.80, ln, _v(r, ln * 0.5, 0.0, 0.0), mats["rod"], rpy=_rod_rpy(r))
    _box(part, f"{p}__slide_shoe", _sz(r, ln * 0.72, rh * 1.4, rh * 0.5),
         _v(r, ln * 0.45, 0.0, -rh * 0.55), mats["rod"])


_ROD_BUILDERS = {
    "plain_round_rod": _plunger_rod_plain_round_rod_build,
    "stepped_lathe_rod": _plunger_rod_stepped_lathe_rod_build,
    "square_bar": _plunger_rod_square_bar_build,
    "collared_stop_rod": _plunger_rod_collared_stop_rod_build,
    "shoe_guided_rod": _plunger_rod_shoe_guided_rod_build,
}


# ---------------------------------------------------------------------------
# stage_module - what a repeated stage adds on top of its rod
# ---------------------------------------------------------------------------


def _free_span(r: ResolvedConfig, k: int) -> tuple[float, float]:
    """Rod length that is never inside guide `k`, at any joint value.

    A collar wider than the bore has to live here - the sources put their drive
    collars and bushings ahead of the guide mouth for exactly this reason.
    """

    return r.guide_len[k] + r.wall[k], r.rod_len[k]


def _stage_module_bushed_sleeve_stage_build(part, r, mats, k, carries) -> None:
    p = f"stage_module__bushed_sleeve_stage__s{k}"
    rh = r.rod_half[k]
    f0, f1 = _free_span(r, k)
    for i, f in enumerate((0.28, 0.68)):
        _cyl(part, f"{p}__bushing_{i}", rh * 1.22, r.wall[k] * 2.2,
             _v(r, f0 + (f1 - f0) * f, 0.0, 0.0), mats["accent"], rpy=_rod_rpy(r))  # rides on its own rod
    if not carries:
        return
    o = _guide_outer(r, k + 1)
    s = r.rod_len[k]
    _cyl(part, f"{p}__stop_collar", o + r.wall[k] * 1.2, r.wall[k] * 2.0,
         _v(r, s - r.wall[k], 0.0, 0.0), mats["accent"], rpy=_rod_rpy(r))


def _stage_module_shoe_railed_stage_build(part, r, mats, k, carries) -> None:
    p = f"stage_module__shoe_railed_stage__s{k}"
    rh = r.rod_half[k]
    f0, f1 = _free_span(r, k)
    _box(part, f"{p}__slide_shoe", _sz(r, (f1 - f0) * 0.7, rh * 2.0, rh * 0.8),
         _v(r, (f0 + f1) * 0.5, 0.0, -rh * 1.05), mats["pin"])
    if not carries:
        return
    o = _guide_outer(r, k + 1)
    s0, s1 = r.rod_len[k] - r.wall[k] * 2.0, r.rod_len[k] + r.guide_len[k + 1]
    _box(part, f"{p}__under_bridge", _sz(r, s1 - s0, o * 1.4, r.wall[k] * 1.8),
         _v(r, (s0 + s1) * 0.5, 0.0, -(o + r.wall[k] * 0.6)), mats["pin"])


def _stage_module_plain_tube_stage_build(part, r, mats, k, carries) -> None:
    p = f"stage_module__plain_tube_stage__s{k}"
    rh = r.rod_half[k]
    f0, f1 = _free_span(r, k)
    _cyl(part, f"{p}__mid_collar", rh * 1.30, r.wall[k] * 3.4,
         _v(r, (f0 + f1) * 0.5, 0.0, 0.0), mats["guide"], rpy=_rod_rpy(r))


_STAGE_BUILDERS = {
    "bushed_sleeve_stage": _stage_module_bushed_sleeve_stage_build,
    "shoe_railed_stage": _stage_module_shoe_railed_stage_build,
    "plain_tube_stage": _stage_module_plain_tube_stage_build,
}


# ---------------------------------------------------------------------------
# input_end - the rear feature of the first plunger
# ---------------------------------------------------------------------------


def _input_stem(part, r, mats, back: float) -> None:
    """Bridges the rod's rear face to the input feature standing behind it."""

    rh = r.rod_half[0]
    _box(part, "input_end__rear_stem", _sz(r, abs(back) + BITE * 2.0, rh * 1.1, rh * 1.1),
         _v(r, back * 0.5, 0.0, 0.0), mats["rod"])


def _input_end_push_knob_build(part, r, mats) -> None:
    rh, back = r.rod_half[0], -r.stroke[0] - r.host_half * 0.45
    _input_stem(part, r, mats, back)
    _cyl(part, "input_end__push_knob__knob", rh * 2.3, rh * 2.0,
         _v(r, back - rh * 1.0 + BITE, 0.0, 0.0), mats["accent"], rpy=_rod_rpy(r))


def _input_end_pull_knob_build(part, r, mats) -> None:
    rh, back = r.rod_half[0], -r.stroke[0] - r.host_half * 0.45
    _input_stem(part, r, mats, back)
    _cyl(part, "input_end__pull_knob__knob", rh * 1.9, rh * 3.0,
         _v(r, back - rh * 1.5 + BITE, 0.0, 0.0), mats["accent"], rpy=_rod_rpy(r))


def _input_end_thumb_button_build(part, r, mats) -> None:
    rh, back = r.rod_half[0], -r.stroke[0] - r.host_half * 0.45
    _input_stem(part, r, mats, back)
    _cyl(part, "input_end__thumb_button__neck", rh * 0.7, rh * 1.6,
         _v(r, back - rh * 0.6, 0.0, 0.0), mats["rod"], rpy=_rod_rpy(r))
    _cyl(part, "input_end__thumb_button__button", rh * 1.7, rh * 0.9,
         _v(r, back - rh * 1.6, 0.0, 0.0), mats["accent"], rpy=_rod_rpy(r))


def _input_end_rear_collar_stop_build(part, r, mats) -> None:
    rh, back = r.rod_half[0], -r.stroke[0] - r.host_half * 0.45
    _input_stem(part, r, mats, back)
    _cyl(part, "input_end__rear_collar_stop__collar", rh * 1.5, rh * 1.2,
         _v(r, back - rh * 0.6 + BITE, 0.0, 0.0), mats["pin"], rpy=_rod_rpy(r))


_INPUT_BUILDERS = {
    "push_knob": _input_end_push_knob_build,
    "pull_knob": _input_end_pull_knob_build,
    "thumb_button": _input_end_thumb_button_build,
    "rear_collar_stop": _input_end_rear_collar_stop_build,
}


# ---------------------------------------------------------------------------
# output_member - always exactly one revolute, authored around its own pivot
# ---------------------------------------------------------------------------


def _drive_up(r: ResolvedConfig) -> float:
    """How far a member may reach back up toward the bore before it fouls it."""

    return max(r.pivot_r * 1.2, abs(_pivot_v(r)) - _rod_under(r) - 0.0009)


def _hub(part, r, mats, name) -> None:
    """The hinge hub spans the clevis it sits in, so it is always carried."""

    _cyl(part, name, r.pivot_r, 2.0 * _clevis_half(r) - 2.0 * RUN_CLEAR,
         (0.0, 0.0, 0.0), mats["guide"], rpy=_hinge_rpy(r))


def _output_member_hinged_tab_plate_build(part, r, mats) -> None:
    p = "output_member__hinged_tab_plate"
    _hub(part, r, mats, f"{p}__barrel")
    t = max(0.003, r.pivot_r * 0.45)
    _box(part, f"{p}__tab_plate", _sz(r, t, _member_u(r) * 2.0, r.out_reach),
         _v(r, t * 0.5 - BITE, 0.0, r.out_reach * 0.42), mats["accent"])


def _output_member_simple_lever_pad_build(part, r, mats) -> None:
    p = "output_member__simple_lever_pad"
    _hub(part, r, mats, f"{p}__hub")
    w, top = r.pivot_r * 1.5, _drive_up(r)
    _box(part, f"{p}__arm", _sz(r, w, w, max(top - w, w)), _v(r, 0.0, 0.0, (top - w) * 0.5), mats["accent"])
    _box(part, f"{p}__drive_pad", _sz(r, w * 1.6, min(w * 1.8, _member_u(r) * 2.0), w), _v(r, 0.0, 0.0, top - w * 0.5), mats["accent"])


def _output_member_lever_with_roller_build(part, r, mats) -> None:
    p = "output_member__lever_with_roller"
    _hub(part, r, mats, f"{p}__hub")
    w = r.pivot_r * 1.2
    _box(part, f"{p}__lower_arm", _sz(r, w, w, r.out_reach * 0.9), _v(r, 0.0, 0.0, _drive_up(r) * 0.48), mats["accent"])
    _cyl(part, f"{p}__contact_roller", r.pivot_r * 1.1, r.pivot_r * 2.2,
         _v(r, 0.0, 0.0, _drive_up(r) * 0.90), mats["pin"], rpy=_hinge_rpy(r))
    _box(part, f"{p}__output_horn", _sz(r, w, w, r.out_reach * 0.6), _v(r, 0.0, 0.0, -r.out_reach * 0.32), mats["accent"])


def _output_member_nose_latch_hook_build(part, r, mats) -> None:
    p = "output_member__nose_latch_hook"
    _hub(part, r, mats, f"{p}__eye")
    w = r.pivot_r * 1.3
    _box(part, f"{p}__leaf", _sz(r, r.out_reach, min(w * 1.6, _member_u(r) * 2.0), w), _v(r, r.out_reach * 0.44, 0.0, 0.0), mats["accent"])
    _box(part, f"{p}__hook", _sz(r, w * 1.4, w * 1.6, r.out_reach * 0.5),
         _v(r, r.out_reach * 0.82, 0.0, _drive_up(r) * 0.30), mats["accent"])


def _output_member_flap_paddle_heel_build(part, r, mats) -> None:
    p = "output_member__flap_paddle_heel"
    _hub(part, r, mats, f"{p}__barrel")
    w = r.pivot_r * 1.4
    _box(part, f"{p}__heel", _sz(r, r.out_reach * 0.5, w * 1.8, w * 1.5), _v(r, r.out_reach * 0.24, 0.0, 0.0), mats["accent"])
    top = _drive_up(r)
    _box(part, f"{p}__paddle", _sz(r, max(0.003, w * 0.5), _member_u(r) * 2.0, max(top * 0.95, w)),
         _v(r, 0.0, 0.0, top * 0.475), mats["accent"])


def _output_member_bar_lever_output_tip_build(part, r, mats) -> None:
    p = "output_member__bar_lever_output_tip"
    _hub(part, r, mats, f"{p}__bushing")
    w, top = r.pivot_r * 1.4, _drive_up(r)
    _box(part, f"{p}__bar", _sz(r, w, min(w * 1.3, _member_u(r) * 2.0), max(top - w * 0.7, w)), _v(r, 0.0, 0.0, (top - w * 0.7) * 0.5), mats["guide"])
    _box(part, f"{p}__output_tip", _sz(r, w * 2.0, min(w * 1.8, _member_u(r) * 2.0), w * 1.4), _v(r, 0.0, 0.0, top - w * 0.7), mats["accent"])


_OUTPUT_BUILDERS = {
    "hinged_tab_plate": _output_member_hinged_tab_plate_build,
    "simple_lever_pad": _output_member_simple_lever_pad_build,
    "lever_with_roller": _output_member_lever_with_roller_build,
    "nose_latch_hook": _output_member_nose_latch_hook_build,
    "flap_paddle_heel": _output_member_flap_paddle_heel_build,
    "bar_lever_output_tip": _output_member_bar_lever_output_tip_build,
}


def _rod_under(r: ResolvedConfig) -> float:
    """How far below the bore axis the deepest rod/stage feature reaches."""

    return max(r.bore_half[0], r.rod_half[0] * 1.55, r.rod_half[-1] * 1.55)


def _pivot_v(r: ResolvedConfig) -> float:
    """The hinge sits off the bore axis, below it.

    On the axis the hub would be inside the rod that is supposed to drive it;
    the sources all hang the pivot beside the bore and let the member reach back
    across it.
    """

    return -(_rod_under(r) + r.pivot_r * 1.6 + r.out_reach * 0.15)


def _clevis_half(r: ResolvedConfig) -> float:
    """Half the clevis gap.

    It stays inside the guide's own width: the cheeks have to reach the guide to
    be carried at all, and the guide is narrower than a full-width member would
    be. The member is sized to fit between them instead.
    """

    return max(r.pivot_r * 1.35, r.rod_half[-1] * 1.25, _guide_outer(r, 0) * 0.62)


def _member_u(r: ResolvedConfig) -> float:
    """Half-width available to the output member between the clevis cheeks."""

    return max(r.pivot_r * 0.6, _clevis_half(r) - r.pivot_r * 0.55)


def _hinge_carrier_host_mounted_build(part, r, mats, local_s) -> None:
    """Clevis cheeks and pin rising from the host, outboard of the bore."""

    p = "hinge_carrier__host_mounted"
    o = _guide_outer(r, 0)
    d = _clevis_half(r)
    pv = _pivot_v(r)
    # The cheeks themselves run back to the guide. A centre bracket would sit in
    # the corridor the member has to reach up through.
    b0 = min(r.guide_len[0] * 0.75, local_s - r.pivot_r * 1.4)
    b1 = local_s + r.pivot_r * 1.4
    top = -o + BITE
    bot = pv - r.pivot_r * 1.3
    for i, sign in enumerate((-1.0, 1.0)):
        _box(part, f"{p}__cheek_{i}", _sz(r, b1 - b0, r.pivot_r * 0.9, top - bot),
             _v(r, (b0 + b1) * 0.5, sign * d, (top + bot) * 0.5), mats["frame"])
        _box(part, f"{p}__cheek_tie_{i}", _sz(r, b1 - b0, r.pivot_r * 0.9, r.pivot_r * 1.2),
             _v(r, (b0 + b1) * 0.5, sign * d, top - r.pivot_r * 0.6), mats["frame"])
    # The hub is not bored, so the pin reads through its protruding ends.
    stub = r.pivot_r * 1.4
    for i, sign in enumerate((-1.0, 1.0)):
        _cyl(part, f"{p}__pivot_pin_{i}", r.pivot_r * 0.55, stub,
             _v(r, local_s, sign * (d + stub * 0.5), pv), mats["pin"], rpy=_hinge_rpy(r))


def _hinge_carrier_plunger_carried_build(part, r, mats, local_s) -> None:
    """Fork and pin ride on the last plunger, so the hinge translates with it."""

    p = "hinge_carrier__plunger_carried"
    d = _clevis_half(r)
    pv = _pivot_v(r)
    _box(part, f"{p}__fork_bridge", _sz(r, r.pivot_r * 1.4, d * 2.0, abs(pv) + r.pivot_r),
         _v(r, local_s - r.pivot_r * 2.8, 0.0, pv * 0.5), mats["rod"])
    for i, sign in enumerate((-1.0, 1.0)):
        _box(part, f"{p}__fork_cheek_{i}", _sz(r, r.pivot_r * 4.2, r.pivot_r * 0.9, abs(pv) + r.pivot_r),
             _v(r, local_s - r.pivot_r * 1.2, sign * d, pv * 0.5), mats["rod"])
    stub = r.pivot_r * 1.4
    for i, sign in enumerate((-1.0, 1.0)):
        _cyl(part, f"{p}__hinge_pin_{i}", r.pivot_r * 0.55, stub,
             _v(r, local_s, sign * (d + stub * 0.5), pv), mats["pin"], rpy=_hinge_rpy(r))


_CARRIER_BUILDERS = {
    "host_mounted": _hinge_carrier_host_mounted_build,
    "plunger_carried": _hinge_carrier_plunger_carried_build,
}


# ---------------------------------------------------------------------------
# assembly
# ---------------------------------------------------------------------------


def _joint(model, name, kind, parent, child, point, axis, limits) -> None:
    provider = AxisInterface(name=f"{name}.provider", point=point, axis=axis, radial=(0.0, 0.0, 1.0))
    consumer = AxisInterface(name=f"{name}.consumer", point=(0.0, 0.0, 0.0), axis=axis, radial=(0.0, 0.0, 1.0))
    mate = mate_axes(provider, consumer)
    model.articulation(
        name, kind, parent=parent, child=child, origin=mate.origin, axis=mate.axis, motion_limits=limits
    )
    register_interface_mate(model, name, mate)


def _meshes_materialized(model: ArticulatedObject) -> bool:
    """False while the preflight probe stands in for real mesh assets."""

    for part in model.parts:
        for visual in getattr(part, "visuals", []):
            filename = getattr(getattr(visual, "geometry", None), "filename", None)
            if filename and "__preflight_probe__" in str(filename):
                return False
    return True


def build_pushpull_plunger_chain(
    config: Config | None = None, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    config = config or Config()
    r = resolve_config(config)
    if assets is None:
        assets = AssetContext(Path(tempfile.mkdtemp(prefix="articraft-pushpull-plunger-chain-")))
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {k: model.material(f"ppc_{k}_{r.palette_style}", rgba=v) for k, v in r.palette.items()}
    model.meta["module_slots"] = slot_choices_for_config(r)

    slide = _slide_vec(r)
    n = r.stage_count

    # --- grounded host ----------------------------------------------------
    host = model.part("support_host")
    host.meta["role"] = "support_host"
    _AXIS_BUILDERS[r.slide_axis](host, r, mats)
    _HOST_BUILDERS[r.support_host](host, r, mats)
    _SECTION_BUILDERS[r.guide_section](host, r, mats, 0.0, r.guide_len[0], r.bore_half[0], r.wall[0], "g0")
    if r.hinge_carrier == "host_mounted":
        _CARRIER_BUILDERS["host_mounted"](host, r, mats, r.hinge_s)
    host.inertial = Inertial.from_geometry(
        Box(_sz(r, max(r.host_len, 0.03), max(r.host_half * 2.0, 0.03), max(r.host_half * 2.0, 0.03))),
        mass=3.0,
        origin=Origin(xyz=_v(r, r.host_len * 0.4, 0.0, 0.0)),
    )

    # --- stages -----------------------------------------------------------
    stages = []
    for k in range(n):
        stage = model.part(f"plunger_{k}")
        stage.meta["role"] = "plunger"
        _ROD_BUILDERS[r.plunger_rod](stage, r, mats, k)
        _running_bands(stage, r, mats, k)
        carries = k < n - 1
        _STAGE_BUILDERS[r.stage_module](stage, r, mats, k, carries)
        if carries:
            _SECTION_BUILDERS[r.guide_section](
                stage, r, mats, r.rod_len[k], r.guide_len[k + 1], r.bore_half[k + 1], r.wall[k + 1], f"g{k + 1}"
            )
            # collar bridging the rod front to the guide it carries
            _cyl(stage, f"stage_module__carrier_collar__s{k}", r.rod_half[k] * 1.15, r.wall[k] * 3.0,
                 _v(r, r.rod_len[k] - r.wall[k] * 1.0, 0.0, 0.0), mats["pin"], rpy=_rod_rpy(r))
        if k == 0:
            _INPUT_BUILDERS[r.input_end](stage, r, mats)
        if k == n - 1 and r.hinge_carrier == "plunger_carried":
            _CARRIER_BUILDERS["plunger_carried"](stage, r, mats, r.hinge_local_s)
        stage.inertial = Inertial.from_geometry(
            Box(_sz(r, max(r.rod_len[k], 0.02), max(r.rod_half[k] * 2.0, 0.01), max(r.rod_half[k] * 2.0, 0.01))),
            mass=max(0.08, 0.6 - 0.15 * k),
            origin=Origin(xyz=_v(r, r.rod_len[k] * 0.5, 0.0, 0.0)),
        )
        stages.append(stage)

    # --- output member ----------------------------------------------------
    member = model.part("output_member")
    member.meta["role"] = "output_member"
    _OUTPUT_BUILDERS[r.output_member](member, r, mats)
    member.inertial = Inertial.from_geometry(
        Box(_sz(r, max(r.out_reach, 0.02), max(r.out_reach, 0.02), max(r.out_reach, 0.02))),
        mass=0.12,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
    )

    # --- joints -----------------------------------------------------------
    _joint(
        model, "slide_0", ArticulationType.PRISMATIC, host, stages[0],
        _v(r, 0.0, 0.0, 0.0), slide,
        MotionLimits(effort=180.0, velocity=0.25, lower=0.0, upper=r.stroke[0]),
    )
    for k in range(1, n):
        _joint(
            model, f"slide_{k}", ArticulationType.PRISMATIC, stages[k - 1], stages[k],
            _v(r, r.rod_len[k - 1], 0.0, 0.0), slide,
            MotionLimits(effort=140.0 - 20.0 * k, velocity=0.25, lower=0.0, upper=r.stroke[k]),
        )
    hinge_parent = host if r.hinge_carrier == "host_mounted" else stages[n - 1]
    hinge_point = _v(
        r, r.hinge_s if r.hinge_carrier == "host_mounted" else r.hinge_local_s, 0.0, _pivot_v(r)
    )
    _joint(
        model, "output_hinge", ArticulationType.REVOLUTE, hinge_parent, member,
        hinge_point, _hinge_vec(r),
        MotionLimits(effort=18.0, velocity=2.0, lower=0.0, upper=0.85),
    )
    return model


def build_seeded_pushpull_plunger_chain(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_pushpull_plunger_chain(config_from_seed(seed), assets=assets)


def run_pushpull_plunger_chain_tests(model: ArticulatedObject, config: Config | None = None) -> TestReport:
    r = resolve_config(config or Config())
    ctx = TestContext(model)
    host = model.get_part("support_host")
    member = model.get_part("output_member")
    ctx.check_model_valid()

    meshes_ready = _meshes_materialized(model)
    if meshes_ready:
        ctx.fail_if_isolated_parts()
        ctx.warn_if_part_contains_disconnected_geometry_islands()
        ctx.fail_if_parts_overlap_in_current_pose()

    slides = [model.get_articulation(f"slide_{k}") for k in range(r.stage_count)]
    hinge = model.get_articulation("output_hinge")

    ctx.check(
        "category_anchor: the stage chain slides along one shared axis",
        all(j.articulation_type == ArticulationType.PRISMATIC for j in slides)
        and len({tuple(round(v, 6) for v in j.axis) for j in slides}) == 1,
        f"axes were {[tuple(j.axis) for j in slides]}",
    )
    ctx.check(
        "category_anchor: the output member turns on a real hinge",
        hinge.articulation_type == ArticulationType.REVOLUTE and member is not None,
        f"hinge was {hinge.articulation_type}",
    )
    # The law the deleted template broke: every stage must still be held by its
    # guide at full extension.
    held = all(r.guide_len[k] - r.stroke[k] >= r.engage_min[k] - 1e-9 for k in range(r.stage_count))
    ctx.check(
        "category_anchor: every plunger stays captured in its guide over the whole stroke",
        held,
        f"guide={r.guide_len} stroke={r.stroke} engage_min={r.engage_min}",
    )
    ctx.check(
        "category_anchor: the driving plunger reaches the output member",
        r.tip_full_s >= r.hinge_s - r.out_reach,
        f"tip_full={r.tip_full_s:.4f} hinge={r.hinge_s:.4f} reach={r.out_reach:.4f}",
    )

    if meshes_ready:
        for k in range(r.stage_count):
            parent = host if k == 0 else model.get_part(f"plunger_{k - 1}")
            ctx.expect_contact(
                model.get_part(f"plunger_{k}"), parent, contact_tol=0.0015,
                name=f"plunger_{k} is carried by its guide",
            )
        with ctx.pose({j: r.stroke[i] for i, j in enumerate(slides)}):
            ctx.fail_if_isolated_parts(name="all stages stay captured at full extension")
    return ctx.report()


TEMPLATE_CORNERS = (
    corner_case(
        "three_stage_shortest_guide_biggest_bore",
        {"slide_axis": "horizontal_x", "support_host": "ground_bed_saddles", "guide_section": "round_bore",
         "stage_module": "bushed_sleeve_stage", "plunger_rod": "stepped_lathe_rod", "input_end": "push_knob",
         "output_member": "lever_with_roller", "hinge_carrier": "host_mounted", "stage_count": 3,
         "guide_length_m": 0.10, "bore_size_m": 0.042, "host_scale": 0.88},
        reason="tightest capture: shortest guide, largest bore, deepest nesting",
    ),
    corner_case(
        "three_stage_vertical_rect_bore",
        {"slide_axis": "vertical_z", "support_host": "wall_backplate", "guide_section": "rect_bore_retainer",
         "stage_module": "shoe_railed_stage", "plunger_rod": "square_bar", "input_end": "thumb_button",
         "output_member": "flap_paddle_heel", "hinge_carrier": "plunger_carried", "stage_count": 3,
         "guide_length_m": 0.10, "bore_size_m": 0.042, "host_scale": 1.25},
        reason="same capture edge on the vertical rectangular-bore stack with a carried hinge",
    ),
    corner_case(
        "single_stage_longest_thinnest",
        {"slide_axis": "horizontal_x", "support_host": "bored_solid_block", "guide_section": "four_wall_channel",
         "stage_module": "plain_tube_stage", "plunger_rod": "shoe_guided_rod", "input_end": "rear_collar_stop",
         "output_member": "nose_latch_hook", "hinge_carrier": "plunger_carried", "stage_count": 1,
         "guide_length_m": 0.26, "bore_size_m": 0.020, "host_scale": 1.25},
        reason="longest stroke on the smallest bore with a rod-carried latch",
    ),
    corner_case(
        "two_stage_open_rail_bar_lever",
        {"slide_axis": "horizontal_x", "support_host": "open_rail_box", "guide_section": "round_bore",
         "stage_module": "shoe_railed_stage", "plunger_rod": "collared_stop_rod", "input_end": "pull_knob",
         "output_member": "bar_lever_output_tip", "hinge_carrier": "host_mounted", "stage_count": 2,
         "guide_length_m": 0.26, "bore_size_m": 0.020, "host_scale": 0.88},
        reason="longest carried stage against a host-mounted bar lever",
    ),
)

__all__ = [
    "Config",
    "ResolvedConfig",
    "TEMPLATE_CORNERS",
    "TEMPLATE_DOMAIN",
    "build_pushpull_plunger_chain",
    "build_seeded_pushpull_plunger_chain",
    "config_from_seed",
    "resolve_config",
    "run_pushpull_plunger_chain_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
]
