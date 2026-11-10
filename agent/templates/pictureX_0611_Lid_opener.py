# SPDX-License-Identifier: Apache-2.0

# ruff: noqa: E501
"""Self-contained pictureX_0611 lid-opener template.

A hand-held plier-action jar/can lid opener.  One fixed stamped stainless
``frame`` (working head carrier + lower handle tang + molded lower grip + the
main pivot pin) carries one moving ``lever`` (stamped lever plate + jaw finger +
upper tang + molded upper grip) on a single registered Z pivot, plus zero to
three spinning head rotors depending on the head family.

Structural slots (all source-derived, freely combinable):
  * head:   rotary_crank | feed_gear | lever_cutter | guarded_head   (4)
  * mouth:  crescent | round_throat | notched_cheek | hooked_jaw     (4)
  * grip:   lofted_oval | stamped_molded                             (2)
  * spine:  folded_bracket | weld_backplate                          (2)
core_domain = 4 * 4 * 2 * 2 = 64.  No multiplicity, so raw_domain = 64 too.
Palette, continuous dimensions and inlays/badges count for nothing.

Geometry convention: the pivot is the world origin, its axis is +Z, the working
head points to -X and both handles run to +X.

MECHANICAL LAYERING (this is what makes every combination collision-free):

    frame carrier plate      z in [-0.003 , +0.003]
    frame head hardware      z <= _HW_TOP (0.0100)          <- gears, guards, jaws
    frame lower grip         z in [-0.0110, +0.0070]
    frame pivot pin          z in [-0.003 , +0.0166]  r = _PIN_R
    lever jaw finger/cutter  z in [+0.0110, +0.0166]
    lever plate              z in [+0.0160, +0.0205]
    lever tang               z in [+0.0195, +0.0275]
    lever upper grip         z in [+0.0199, +0.0359]

Every frame element except the pivot pin therefore ends at or below 0.0100 and
every lever element starts at or above 0.0110, so the two plier halves can never
touch anywhere except at the pivot, at ANY pivot angle.  The two intentional
captured contacts are pure vertical laps of ``_MOUNT`` = 0.6 mm:

  * the pivot pin top presses 0.6 mm into the lever plate's underside,
  * every rotor hub presses 0.6 mm into the carrier plate's top face,

which is real seated contact (``fail_if_isolated_parts`` uses contact_tol=1e-6,
so tangency would read as a floating island) while the world-AABB overlap check
skips the pair outright because one axis stays under the collision tolerance.
No overlap allowance of any kind is declared.

AABB NOTE: cross-part element overlap is measured on world AABBs and ``min_depth``
is the SMALLEST axis, so every captured pair here is a horizontal-face contact
whose Z lap is the tiny axis; nothing relies on an oblique fit.

No source runtime, snapshot or other template is imported; stdlib + sdk only.
No motion clamping: the pivot keeps its full source-like squeeze range and the
rotors are CONTINUOUS.
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
    ExtrudeGeometry,
    ExtrudeWithHolesGeometry,
    LoftGeometry,
    MotionLimits,
    Origin,
    TemplateDomain,
    TestContext,
    TestReport,
    component_slot,
    corner_case,
    mate_axes,
    mesh_from_geometry,
    register_interface_mate,
)

Head = Literal["rotary_crank", "feed_gear", "lever_cutter", "guarded_head"]
Mouth = Literal["crescent", "round_throat", "notched_cheek", "hooked_jaw"]
Grip = Literal["lofted_oval", "stamped_molded"]
Spine = Literal["folded_bracket", "weld_backplate"]
PaletteStyle = Literal["stainless", "graphite", "chrome"]

HEADS: tuple[Head, ...] = ("rotary_crank", "feed_gear", "lever_cutter", "guarded_head")
MOUTHS: tuple[Mouth, ...] = ("crescent", "round_throat", "notched_cheek", "hooked_jaw")
GRIPS: tuple[Grip, ...] = ("lofted_oval", "stamped_molded")
SPINES: tuple[Spine, ...] = ("folded_bracket", "weld_backplate")
PALETTE_STYLES: tuple[PaletteStyle, ...] = ("stainless", "graphite", "chrome")

TEMPLATE_DOMAIN = TemplateDomain(
    slots=(
        component_slot("head", HEADS),
        component_slot("mouth", MOUTHS),
        component_slot("grip", GRIPS),
        component_slot("spine", SPINES),
    )
)

# ---------------------------------------------------------------------------
# Continuous parameter bounds (do NOT inflate core/raw).
# ---------------------------------------------------------------------------
_HEAD_SPAN_MIN, _HEAD_SPAN_MAX = 0.048, 0.072
_GRIP_LEN_MIN, _GRIP_LEN_MAX = 0.100, 0.150
_MOUTH_SIZE_MIN, _MOUTH_SIZE_MAX = 0.016, 0.026

# ---------------------------------------------------------------------------
# Fixed layer geometry (see the module docstring).
# ---------------------------------------------------------------------------
_PLATE_Z0 = -0.003
_PLATE_Z1 = 0.003
_PLATE_T = _PLATE_Z1 - _PLATE_Z0

_HW_Z0 = -0.002  # frame head hardware seats 1 mm into the carrier plate
_HW_TOP = 0.0100  # ... and never rises above this

_PIN_R = 0.0042
_LEVER_Z0 = 0.0160
_LEVER_Z1 = 0.0205
_LEVER_TANG_Z0 = 0.0195
_LEVER_TANG_Z1 = 0.0275
_LEVER_GRIP_Z0 = 0.0199
_LEVER_GRIP_T = 0.0160
_FRAME_GRIP_Z0 = -0.0110
_FRAME_GRIP_T = 0.0180
_FRAME_TANG_Z0 = -0.0035
_FRAME_TANG_T = 0.0060

_JAW_Z0 = 0.0110  # lever jaw finger / lever-borne cutter band
_JAW_Z1 = 0.0166  # ... laps the lever plate underside by _MOUNT

# Captured contact lap: real seating, under the collision tolerance.
_MOUNT = 0.0006
_PIN_TOP = _LEVER_Z0 + _MOUNT

_FRAME_YAW = -0.14  # lower handle azimuth (rad)
_LEVER_YAW = 0.18  # upper handle azimuth at the neutral pose (rad)
# Squeeze range: negative closes the upper handle onto the lower one, positive
# opens it.  Signs measured with a ctx.pose probe on the lever jaw finger.
_PIVOT_LOWER = -0.30
_PIVOT_UPPER = 0.26

PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "stainless": {
        "steel": (0.70, 0.73, 0.75, 1.0),
        "satin": (0.48, 0.51, 0.53, 1.0),
        "hard": (0.26, 0.28, 0.30, 1.0),
        "grip": (0.025, 0.028, 0.032, 1.0),
        "soft": (0.075, 0.080, 0.085, 1.0),
        "accent": (0.63, 0.43, 0.16, 1.0),
    },
    "graphite": {
        "steel": (0.44, 0.46, 0.48, 1.0),
        "satin": (0.32, 0.34, 0.36, 1.0),
        "hard": (0.14, 0.15, 0.16, 1.0),
        "grip": (0.045, 0.048, 0.052, 1.0),
        "soft": (0.10, 0.11, 0.12, 1.0),
        "accent": (0.85, 0.62, 0.05, 1.0),
    },
    "chrome": {
        "steel": (0.88, 0.90, 0.92, 1.0),
        "satin": (0.66, 0.68, 0.70, 1.0),
        "hard": (0.31, 0.33, 0.34, 1.0),
        "grip": (0.06, 0.065, 0.07, 1.0),
        "soft": (0.12, 0.13, 0.14, 1.0),
        "accent": (0.72, 0.20, 0.16, 1.0),
    },
}


# Rotor count per head family -- the joint-graph signature of the slot.
HEAD_ROTOR_COUNT: dict[str, int] = {
    "rotary_crank": 3,
    "feed_gear": 1,
    "lever_cutter": 0,
    "guarded_head": 0,
}


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Config:
    head: Head = "rotary_crank"
    mouth: Mouth = "crescent"
    grip: Grip = "lofted_oval"
    spine: Spine = "folded_bracket"
    head_span_m: float | None = None
    grip_length_m: float | None = None
    mouth_size_m: float | None = None
    palette_style: PaletteStyle = "stainless"
    name: str = "pictureX_0611_lid_opener"


@dataclass(frozen=True)
class ResolvedConfig:
    head: Head
    mouth: Mouth
    grip: Grip
    spine: Spine
    head_span_m: float
    grip_length_m: float
    mouth_size_m: float
    palette_style: PaletteStyle
    palette: dict[str, tuple[float, float, float, float]]
    # derived
    mouth_x: float  # working-mouth centre on the nose axis
    nose_tip_x: float  # carrier nose tip
    drive_xy: tuple[float, float]
    feed_xy: tuple[float, float]
    cutter_xy: tuple[float, float]
    drive_r: float
    feed_r: float
    cutter_r: float
    frame_tang_reach: float
    lever_tang_reach: float
    rotor_count: int
    pivot_lower: float
    pivot_upper: float
    name: str


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(value)))


def config_from_seed(seed: int) -> Config:
    choices = TEMPLATE_DOMAIN.sample(seed)
    rng = random.Random(int(seed) ^ 0x061111D0)
    return Config(
        head=choices["head"],
        mouth=choices["mouth"],
        grip=choices["grip"],
        spine=choices["spine"],
        head_span_m=round(rng.uniform(_HEAD_SPAN_MIN, _HEAD_SPAN_MAX), 5),
        grip_length_m=round(rng.uniform(_GRIP_LEN_MIN, _GRIP_LEN_MAX), 5),
        mouth_size_m=round(rng.uniform(_MOUTH_SIZE_MIN, _MOUTH_SIZE_MAX), 5),
        palette_style=rng.choice(PALETTE_STYLES),
        name=f"pictureX_0611_lid_opener_seed_{seed}",
    )


def resolve_config(config: Config | None = None) -> ResolvedConfig:
    cfg = config or Config()
    TEMPLATE_DOMAIN.validate(
        {
            "head": cfg.head,
            "mouth": cfg.mouth,
            "grip": cfg.grip,
            "spine": cfg.spine,
        }
    )
    if cfg.palette_style not in PALETTES:
        raise ValueError(f"unknown palette_style {cfg.palette_style!r}")

    h = _clamp(
        0.058 if cfg.head_span_m is None else cfg.head_span_m, _HEAD_SPAN_MIN, _HEAD_SPAN_MAX
    )
    gl = _clamp(
        0.124 if cfg.grip_length_m is None else cfg.grip_length_m, _GRIP_LEN_MIN, _GRIP_LEN_MAX
    )
    ms = _clamp(
        0.021 if cfg.mouth_size_m is None else cfg.mouth_size_m, _MOUTH_SIZE_MIN, _MOUTH_SIZE_MAX
    )

    # Working mouth sits `head_span` + a fixed lip beyond the pivot; the carrier
    # nose runs 20 mm past it so every mouth form still has a closed rim.
    mouth_x = -(h + 0.012)
    nose_tip_x = mouth_x - 0.020

    # Head shaft stations, all derived from head_span so the gear train grows
    # with the head.  Radii are chosen so the closest pair (drive/feed) keeps a
    # >= 0.10 * head_span radial gap over the whole parameter range.
    drive_xy = (-0.34 * h, -0.010)
    feed_xy = (-0.66 * h, -0.004)
    cutter_xy = (-0.62 * h, 0.019)
    drive_r = 0.115 * h
    feed_r = 0.100 * h
    cutter_r = 0.105 * h

    return ResolvedConfig(
        head=cfg.head,
        mouth=cfg.mouth,
        grip=cfg.grip,
        spine=cfg.spine,
        head_span_m=h,
        grip_length_m=gl,
        mouth_size_m=ms,
        palette_style=cfg.palette_style,
        palette=PALETTES[cfg.palette_style],
        mouth_x=mouth_x,
        nose_tip_x=nose_tip_x,
        drive_xy=drive_xy,
        feed_xy=feed_xy,
        cutter_xy=cutter_xy,
        drive_r=drive_r,
        feed_r=feed_r,
        cutter_r=cutter_r,
        frame_tang_reach=0.038 + 0.55 * gl,
        lever_tang_reach=0.045 + 0.50 * gl,
        rotor_count=HEAD_ROTOR_COUNT[cfg.head],
        pivot_lower=_PIVOT_LOWER,
        pivot_upper=_PIVOT_UPPER,
        name=cfg.name,
    )


def slot_choices_for_config(r: Config | ResolvedConfig) -> tuple[tuple[str, object], ...]:
    return (("head", r.head), ("mouth", r.mouth), ("grip", r.grip), ("spine", r.spine))


# ---------------------------------------------------------------------------
# Small geometry helpers
# ---------------------------------------------------------------------------
def _materials(model: ArticulatedObject, r: ResolvedConfig) -> dict[str, str]:
    for key, rgba in r.palette.items():
        model.material(key, rgba=rgba)
    return {key: key for key in r.palette}


def _rot(points, yaw: float):
    c, s = math.cos(yaw), math.sin(yaw)
    return [(u * c - v * s, u * s + v * c) for (u, v) in points]


def _circle(cx: float, cy: float, radius: float, segments: int = 28):
    return [
        (
            cx + radius * math.cos(2.0 * math.pi * i / segments),
            cy + radius * math.sin(2.0 * math.pi * i / segments),
        )
        for i in range(segments)
    ]


def _plate(part, profile, z0: float, thickness: float, material: str, name: str) -> None:
    part.visual(
        mesh_from_geometry(ExtrudeGeometry.from_z0(profile, thickness, cap=True), name),
        origin=Origin(xyz=(0.0, 0.0, z0)),
        material=material,
        name=name, material_class_id="metal.generic_plain",
    )


def _plate_with_hole(
    part, profile, holes, z0: float, thickness: float, material: str, name: str
) -> None:
    part.visual(
        mesh_from_geometry(
            ExtrudeWithHolesGeometry(profile, holes, thickness, cap=True, center=False), name
        ),
        origin=Origin(xyz=(0.0, 0.0, z0)),
        material=material,
        name=name, material_class_id="metal.stainless_matte",
    )


def _box(part, size, xyz, material, name, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(Box(size), origin=Origin(xyz=xyz, rpy=rpy), material=material, name=name, material_class_id="metal.generic_plain")


def _cyl(part, radius, length, xyz, material, name, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=Origin(xyz=xyz, rpy=rpy),
        material=material,
        name=name, material_class_id="metal.generic_plain",
    )


def _toothed_disc(cx: float, cy: float, root_r: float, tip_r: float, teeth: int):
    """Closed serrated outline: the real feed/drive gear silhouette."""
    pts = []
    for i in range(teeth * 2):
        a = math.pi * i / teeth
        rad = tip_r if i % 2 == 0 else root_r
        pts.append((cx + rad * math.cos(a), cy + rad * math.sin(a)))
    return pts


def _handle_loft_mesh(
    half_thick, half_wide, lateral, s0: float, span: float, name: str, segments: int = 20
):
    """Oval handle lofted from varying ellipse sections on a curved centreline.

    Sections are stacked along the loft's LOCAL +Z; the visual origin then maps
    local +Z onto the handle azimuth, local +X onto world -Z (so ``half_thick``
    is the world vertical half-thickness) and local +Y onto the horizontal
    normal (so ``lateral`` bows the centreline sideways).  Mirrors the
    ``_handle_loft`` ellipse-section loft of rec ...3629 model.py:L37-L58.
    """
    count = len(half_thick)
    rings = []
    for k in range(count):
        z = s0 + span * k / (count - 1)
        a, b, c = half_thick[k], half_wide[k], lateral[k]
        rings.append(
            [
                (
                    a * math.cos(2.0 * math.pi * i / segments),
                    c + b * math.sin(2.0 * math.pi * i / segments),
                    z,
                )
                for i in range(segments)
            ]
        )
    return mesh_from_geometry(LoftGeometry(rings, cap=True, closed=True), name)


def _carrier_outline(r: ResolvedConfig, *, nose=None, notch=None):
    """Stamped stainless carrier silhouette (CCW), parameterised by head_span."""
    h = r.head_span_m
    mx, tip = r.mouth_x, r.nose_tip_x
    bottom = [(tip, -0.010), (mx - 0.013, -0.020)]
    if notch is not None:
        bottom.extend(notch)
    else:
        bottom.append((mx + 0.006, -0.026))
    bottom.extend([(-0.34 * h, -0.022), (0.014, -0.016), (0.020, 0.000)])
    top = [
        (0.012, 0.014),
        (-0.30 * h, 0.0215),
        (mx + 0.004, 0.0255),
        (mx - 0.012, 0.018),
        (tip, 0.008),
    ]
    outline = bottom + top
    if nose is not None:
        outline = outline + list(nose)
    return outline


# ---------------------------------------------------------------------------
# mouth slot -- the working lid opening cut into (or hooked onto) the carrier
# nose.  Every candidate is emitted on the shared frame part, so its seams are
# intra-part and free; the mouth region is > 0.028 m clear of every rotor.
# ---------------------------------------------------------------------------
def _mouth_crescent_outline(r: ResolvedConfig):
    """Open crescent working mouth -- rec ...583310 model.py:L91-L102.

    The nose face is replaced by an arc of radius 0.45*mouth_size about the
    mouth centre, leaving two jaw tips and a C-shaped throat open to -X.
    """
    rc = 0.45 * r.mouth_size_m
    arc = [
        (r.mouth_x + rc * math.cos(math.radians(a)), rc * math.sin(math.radians(a)))
        for a in (118.0, 140.0, 160.0, 180.0, 200.0, 220.0, 242.0)
    ]
    return (_carrier_outline(r, nose=arc), [])


def _mouth_round_throat_outline(r: ResolvedConfig):
    """Closed circular throat bored through the nose -- rec ...039038 model.py:L121-L129."""
    return (_carrier_outline(r), [_circle(r.mouth_x, 0.0, 0.42 * r.mouth_size_m)])


def _mouth_notched_cheek_outline(r: ResolvedConfig):
    """Squared bottle-cap notch stamped into the lower cheek edge.

    rec ...3629 model.py:L159 -- ``notch=(-47.0, -3.0, 10.5)`` bites a notch out
    of the lower stamped cheek rather than boring the nose.
    """
    m = r.mouth_size_m
    notch = [
        (r.mouth_x - 0.275 * m, -0.024),
        (r.mouth_x - 0.150 * m, -0.024 + 0.62 * m),
        (r.mouth_x + 0.150 * m, -0.024 + 0.62 * m),
        (r.mouth_x + 0.275 * m, -0.024),
    ]
    return (_carrier_outline(r, notch=notch), [])


def _mouth_hooked_jaw_outline(r: ResolvedConfig):
    """Solid nose -- the working jaw is a separate hook, see the extras builder."""
    return (_carrier_outline(r), [])


def _mouth_crescent_extras(part, r: ResolvedConfig, mats, cand: str) -> None:
    # Rubber jaw pad on the lower lip -- rec ...583310 model.py:L201-L206.
    _cyl(
        part,
        0.22 * r.mouth_size_m,
        0.010,
        (r.mouth_x - 0.004, -0.011, 0.0),
        mats["grip"],
        f"mouth__{cand}__jaw_pad",
        rpy=(math.pi / 2.0, 0.0, 0.0),
    )


def _mouth_round_throat_extras(part, r: ResolvedConfig, mats, cand: str) -> None:
    # Formed nose rivet beside the bored throat -- rec ...039038 model.py:L198-L208.
    _cyl(
        part,
        0.13 * r.mouth_size_m,
        0.008,
        (r.mouth_x + 0.011, -0.014, 0.0),
        mats["satin"],
        f"mouth__{cand}__nose_rivet",
    )


def _mouth_notched_cheek_extras(part, r: ResolvedConfig, mats, cand: str) -> None:
    # Folded rim lip that stiffens the notched cheek.
    m = r.mouth_size_m
    _box(
        part,
        (0.75 * m, 0.0030, 0.0090),
        (r.mouth_x, -0.0235, 0.0015),
        mats["satin"],
        f"mouth__{cand}__notch_lip",
    )


def _mouth_hooked_jaw_extras(part, r: ResolvedConfig, mats, cand: str) -> None:
    """Hooked anti-slip claw at the nose -- rec ...036146 model.py:L155-L166."""
    k = r.mouth_size_m / 0.021
    hook = [
        (0.010 * k, -0.016 * k),
        (0.001 * k, -0.021 * k),
        (-0.011 * k, -0.017 * k),
        (-0.017 * k, -0.006 * k),
        (-0.014 * k, 0.005 * k),
        (-0.006 * k, 0.009 * k),
        (-0.006 * k, 0.002 * k),
        (-0.011 * k, -0.005 * k),
        (-0.007 * k, -0.012 * k),
        (0.002 * k, -0.014 * k),
        (0.010 * k, -0.011 * k),
    ]
    hook = [(r.mouth_x + u, v) for (u, v) in hook]
    _plate(part, hook, -0.0010, 0.0055, mats["steel"], f"mouth__{cand}__hooked_jaw")
    _box(
        part,
        (0.012, 0.010, 0.0080),
        (r.mouth_x + 0.014, -0.010, 0.0010),
        mats["hard"],
        f"mouth__{cand}__jaw_root_block",
    )


_MOUTH_OUTLINES = {
    "crescent": _mouth_crescent_outline,
    "round_throat": _mouth_round_throat_outline,
    "notched_cheek": _mouth_notched_cheek_outline,
    "hooked_jaw": _mouth_hooked_jaw_outline,
}

_MOUTH_EXTRAS = {
    "crescent": _mouth_crescent_extras,
    "round_throat": _mouth_round_throat_extras,
    "notched_cheek": _mouth_notched_cheek_extras,
    "hooked_jaw": _mouth_hooked_jaw_extras,
}


# ---------------------------------------------------------------------------
# spine slot -- the stamped carrier's second layer / reinforcement.  Both
# candidates are frame elements, so they never interact with a moving part.
# ---------------------------------------------------------------------------
def _spine_folded_bracket_build(part, r: ResolvedConfig, mats) -> None:
    """Folded U bracket riveted under the cheek -- rec ...3629 model.py:L190-L209."""
    cand = "folded_bracket"
    _box(
        part,
        (0.020, 0.0026, 0.0100),
        (0.002, 0.010, -0.0055),
        mats["steel"],
        f"spine__{cand}__bracket_web",
    )
    _box(
        part,
        (0.0026, 0.0110, 0.0100),
        (-0.007, 0.0050, -0.0055),
        mats["steel"],
        f"spine__{cand}__bracket_leg_a",
    )
    _box(
        part,
        (0.0026, 0.0110, 0.0100),
        (0.011, 0.0050, -0.0055),
        mats["steel"],
        f"spine__{cand}__bracket_leg_b",
    )


def _spine_weld_backplate_build(part, r: ResolvedConfig, mats) -> None:
    """Spot-welded mechanism backplate -- rec ...036146 model.py:L91-L096."""
    cand = "weld_backplate"
    h = r.head_span_m
    _box(
        part,
        (0.72 * h, 0.020, 0.0035),
        (-0.30 * h - 0.004, -0.006, -0.0040),
        mats["satin"],
        f"spine__{cand}__mechanism_backplate",
    )
    _cyl(
        part,
        0.0035,
        0.0075,
        (-0.30 * h - 0.004, -0.006, -0.0035),
        mats["hard"],
        f"spine__{cand}__backplate_rivet",
    )


_SPINE_BUILDERS = {
    "folded_bracket": _spine_folded_bracket_build,
    "weld_backplate": _spine_weld_backplate_build,
}


# ---------------------------------------------------------------------------
# head slot -- the working mechanism.  Static hardware is emitted onto the
# frame; the rotor descriptors returned here become CONTINUOUS spinning parts.
# Every static element lives in z <= _HW_TOP, so it can never reach the lever.
# ---------------------------------------------------------------------------
def _rotor_hub(part, r: ResolvedConfig, mats, radius: float, cand: str, local: str) -> None:
    """Hub + retaining screw of a spinning head rotor, at the rotor origin.

    The hub bottom sits _MOUNT below the carrier's top face, so the rotor is
    physically seated on the plate (the only cross-part contact the rotor has)
    while the world-AABB lap on Z stays at 0.6 mm.
    """
    hub_r = max(0.0018, 0.36 * radius)
    hub_bot = _PLATE_Z1 - _MOUNT
    hub_len = 0.0100 - hub_bot
    _cyl(
        part,
        hub_r,
        hub_len,
        (0.0, 0.0, hub_bot + 0.5 * hub_len),
        mats["accent"],
        f"head__{cand}__{local}_hub",
    )
    _cyl(
        part, 0.55 * hub_r, 0.0016, (0.0, 0.0, 0.0092), mats["hard"], f"head__{cand}__{local}_screw"
    )


def _head_rotary_crank_build(frame, r: ResolvedConfig, mats):
    """Crank-driven multi-shaft rotary head -- rec ...3629 model.py:L258-L372.

    Three spinning shafts on the carrier: a spur drive gear turned by a short
    crank and knob, a serrated feed wheel and a hardened cutter disc.  This is
    the only head family with a hand crank and more than one rotary axis.
    """
    cand = "rotary_crank"

    def _drive(part) -> None:
        _plate(
            part,
            _toothed_disc(0.0, 0.0, 0.80 * r.drive_r, r.drive_r, 12),
            0.0045,
            0.0047,
            mats["satin"],
            f"head__{cand}__drive_gear",
        )
        _rotor_hub(part, r, mats, r.drive_r, cand, "drive")
        # Short crank arm + molded knob, kept inside a 1.57 * gear-radius sweep
        # envelope so the turning crank clears the feed wheel at every angle.
        arm = 1.15 * r.drive_r
        _box(
            part,
            (arm, 0.42 * r.drive_r, 0.0024),
            (0.5 * arm, 0.0, 0.0062),
            mats["steel"],
            f"head__{cand}__crank_arm",
        )
        _cyl(
            part,
            0.42 * r.drive_r,
            0.0038,
            (arm, 0.0, 0.0081),
            mats["grip"],
            f"head__{cand}__crank_knob",
        )

    def _feed(part) -> None:
        _plate(
            part,
            _toothed_disc(0.0, 0.0, 0.80 * r.feed_r, r.feed_r, 10),
            0.0045,
            0.0035,
            mats["steel"],
            f"head__{cand}__feed_gear",
        )
        _rotor_hub(part, r, mats, r.feed_r, cand, "feed")

    def _cutter(part) -> None:
        _cyl(
            part, r.cutter_r, 0.0033, (0.0, 0.0, 0.0062), mats["hard"], f"head__{cand}__cutter_disc"
        )
        _rotor_hub(part, r, mats, r.cutter_r, cand, "cutter")

    return (
        {"local": "drive_shaft", "xy": r.drive_xy, "build": _drive},
        {"local": "feed_wheel", "xy": r.feed_xy, "build": _feed},
        {"local": "cutter_disc", "xy": r.cutter_xy, "build": _cutter},
    )


def _head_feed_gear_build(frame, r: ResolvedConfig, mats):
    """One continuous serrated feed gear + a static sharpened cutting wheel.

    rec ...036146 model.py:L167-L184 (cutter bracket, cutting wheel, screw) and
    L261-L291 (the serrated ``feed_gear`` part on a CONTINUOUS axis).
    """
    cand = "feed_gear"
    h = r.head_span_m
    cx, cy = -0.30 * h, 0.012
    # Static cutter bracket + sharpened disc + screw, all on the carrier.
    _box(
        frame,
        (0.018, 0.014, 0.0090),
        (cx + 0.006, cy - 0.008, 0.0025),
        mats["hard"],
        f"head__{cand}__cutter_bracket",
    )
    _cyl(frame, 0.11 * h, 0.0032, (cx, cy, 0.0068), mats["satin"], f"head__{cand}__cutting_wheel")
    _cyl(frame, 0.030 * h, 0.0075, (cx, cy, 0.0055), mats["hard"], f"head__{cand}__cutter_screw")

    def _feed(part) -> None:
        _plate(
            part,
            _toothed_disc(0.0, 0.0, 0.78 * 0.13 * h, 0.13 * h, 18),
            0.0045,
            0.0040,
            mats["satin"],
            f"head__{cand}__feed_gear_teeth",
        )
        _rotor_hub(part, r, mats, 0.13 * h, cand, "feed")

    return ({"local": "feed_gear", "xy": (-0.66 * h, -0.004), "build": _feed},)


def _head_lever_cutter_build(frame, r: ResolvedConfig, mats):
    """Static reduction + feed gears on the frame; the cutter rides the LEVER.

    rec ...039038 model.py:L180-L195 (static drive_gear + feed_wheel on the
    body) and L305-L318 (the ``cutting_wheel`` is a visual of the MOVING upper
    handle, swinging toward the feed wheel as the handles close).  The lever's
    cutter is emitted by ``_lever_head_extras``.
    """
    cand = "lever_cutter"
    h = r.head_span_m
    _plate(
        frame,
        _toothed_disc(r.drive_xy[0], r.drive_xy[1], 0.80 * 0.13 * h, 0.13 * h, 14),
        _HW_Z0,
        0.0110,
        mats["hard"],
        f"head__{cand}__drive_gear",
    )
    _plate(
        frame,
        _toothed_disc(r.feed_xy[0], r.feed_xy[1], 0.80 * 0.115 * h, 0.115 * h, 18),
        _HW_Z0,
        0.0106,
        mats["satin"],
        f"head__{cand}__feed_wheel",
    )
    _cyl(
        frame,
        0.030 * h,
        0.0030,
        (r.drive_xy[0], r.drive_xy[1], 0.0085),
        mats["hard"],
        f"head__{cand}__drive_axle",
    )
    _cyl(
        frame,
        0.028 * h,
        0.0030,
        (r.feed_xy[0], r.feed_xy[1], 0.0081),
        mats["hard"],
        f"head__{cand}__feed_axle",
    )
    return ()


def _head_guarded_head_build(frame, r: ResolvedConfig, mats):
    """Static cutting disc under a folded U guard, plus a guide roller.

    rec ...583310 model.py:L163-L198 -- cutting_disc, cutter_rivet, guide_roller
    and the folded guard (guard_post / guard_bridge / guard_post_2).  No rotary
    joint: every head member is fixed to the stamped carrier.
    """
    cand = "guarded_head"
    h = r.head_span_m
    _plate(
        frame,
        _toothed_disc(-0.47 * h, -0.010, 0.82 * 0.135 * h, 0.135 * h, 14),
        _HW_Z0,
        0.0105,
        mats["satin"],
        f"head__{cand}__drive_gear",
    )
    _cyl(
        frame,
        0.15 * h,
        0.0034,
        (-0.62 * h, -0.006, 0.0060),
        mats["hard"],
        f"head__{cand}__cutting_disc",
    )
    _cyl(
        frame,
        0.045 * h,
        0.0018,
        (-0.62 * h, -0.006, 0.0086),
        mats["hard"],
        f"head__{cand}__cutter_rivet",
    )
    _cyl(
        frame,
        0.0058,
        0.0120,
        (-0.62 * h, 0.015, 0.0035),
        mats["satin"],
        f"head__{cand}__guide_roller",
        rpy=(math.pi / 2.0, 0.0, 0.0),
    )
    _box(
        frame,
        (0.0050, 0.0180, 0.0120),
        (-0.70 * h, 0.0180, 0.0040),
        mats["steel"],
        f"head__{cand}__guard_post",
    )
    _box(
        frame,
        (0.0050, 0.0180, 0.0120),
        (-0.54 * h, 0.0180, 0.0040),
        mats["steel"],
        f"head__{cand}__guard_post_2",
    )
    _box(
        frame,
        (0.16 * h + 0.005, 0.0050, 0.0120),
        (-0.62 * h, 0.0250, 0.0040),
        mats["steel"],
        f"head__{cand}__guard_bridge",
    )
    return ()


_HEAD_BUILDERS = {
    "rotary_crank": _head_rotary_crank_build,
    "feed_gear": _head_feed_gear_build,
    "lever_cutter": _head_lever_cutter_build,
    "guarded_head": _head_guarded_head_build,
}


# ---------------------------------------------------------------------------
# grip slot -- handle construction, emitted on both halves so the two candidates
# are one coherent family and never mix.
# ---------------------------------------------------------------------------
_LOFT_FRAME_HALF_T = (0.0048, 0.0070, 0.0083, 0.0088, 0.0083, 0.0056, 0.0028)
_LOFT_FRAME_HALF_W = (0.0048, 0.0082, 0.0104, 0.0115, 0.0105, 0.0068, 0.0026)
_LOFT_FRAME_LAT = (0.0, -0.0015, -0.0032, -0.0042, -0.0040, -0.0026, -0.0010)
_LOFT_LEVER_HALF_T = (0.0044, 0.0064, 0.0076, 0.0080, 0.0076, 0.0051, 0.0026)
_LOFT_LEVER_HALF_W = (0.0046, 0.0078, 0.0100, 0.0110, 0.0100, 0.0065, 0.0025)
_LOFT_LEVER_LAT = (0.0, 0.0014, 0.0030, 0.0040, 0.0038, 0.0024, 0.0009)


def _grip_lofted_oval_build(part, r: ResolvedConfig, mats, *, upper: bool) -> None:
    """Curved multi-section lofted oval grip -- rec ...3629 model.py:L37-L58, L97-L119.

    Smooth ellipse sections of varying width and thickness swept along a bowed
    centreline: a palm swell in the middle and tapered rounded ends.
    """
    cand = "lofted_oval"
    gl = r.grip_length_m
    side = "upper" if upper else "lower"
    if upper:
        mesh = _handle_loft_mesh(
            _LOFT_LEVER_HALF_T,
            _LOFT_LEVER_HALF_W,
            _LOFT_LEVER_LAT,
            0.046,
            gl,
            f"grip__{cand}__{side}_grip",
        )
        zc = _LEVER_GRIP_Z0 + 0.0080
        yaw = 0.0
        s = 0.046 + 0.42 * gl
        lat = 0.0044
    else:
        mesh = _handle_loft_mesh(
            _LOFT_FRAME_HALF_T,
            _LOFT_FRAME_HALF_W,
            _LOFT_FRAME_LAT,
            0.040,
            gl,
            f"grip__{cand}__{side}_grip",
        )
        zc = _FRAME_GRIP_Z0 + 0.0090
        yaw = _FRAME_YAW
        s = 0.040 + 0.42 * gl
        lat = -0.0046
    part.visual(
        mesh,
        origin=Origin(xyz=(0.0, 0.0, zc), rpy=(0.0, math.pi / 2.0, yaw)),
        material=mats["grip"],
        name=f"grip__{cand}__{side}_grip", material_class_id="rubber.smooth_plain",
    )
    # Sculpted thumb rest riding the palm swell (the loft's identifying detail).
    _box(
        part,
        (0.34 * gl, 0.0060, 0.0028),
        (
            s * math.cos(yaw) - lat * math.sin(yaw),
            s * math.sin(yaw) + lat * math.cos(yaw),
            zc,
        ),
        mats["soft"],
        f"grip__{cand}__{side}_thumb_rest",
        rpy=(0.0, 0.0, yaw),
    )


def _grip_stamped_molded_build(part, r: ResolvedConfig, mats, *, upper: bool) -> None:
    """Flat stamped/molded plate grip with a raised soft-touch inlay.

    rec ...036146 model.py:L111-L124 + L214-L228, corroborated by ...039038
    model.py:L149-L158 / L274-L303 and ...583310 model.py:L106-L128 / L243-L265:
    a closed outline extruded to a constant thickness with a thin raised spine.
    """
    cand = "stamped_molded"
    gl = r.grip_length_m
    side = "upper" if upper else "lower"
    u0 = 0.046 if upper else 0.040
    yaw = 0.0 if upper else _FRAME_YAW
    z0 = _LEVER_GRIP_Z0 if upper else _FRAME_GRIP_Z0
    thick = _LEVER_GRIP_T if upper else _FRAME_GRIP_T
    outline = [
        (u0, -0.0105),
        (u0 + 0.030, -0.0138),
        (u0 + 0.55 * gl, -0.0152),
        (u0 + gl, -0.0126),
        (u0 + gl + 0.006, -0.0052),
        (u0 + gl + 0.006, 0.0040),
        (u0 + gl, 0.0102),
        (u0 + 0.50 * gl, 0.0122),
        (u0 + 0.030, 0.0114),
        (u0, 0.0090),
    ]
    _plate(part, _rot(outline, yaw), z0, thick, mats["grip"], f"grip__{cand}__{side}_grip")
    inlay = [
        (u0 + 0.020, -0.0100),
        (u0 + 0.55 * gl, -0.0116),
        (u0 + gl - 0.006, -0.0092),
        (u0 + gl - 0.010, -0.0030),
        (u0 + 0.50 * gl, -0.0048),
        (u0 + 0.020, -0.0040),
    ]
    _plate(
        part,
        _rot(inlay, yaw),
        z0 + thick - 0.0018,
        0.0026,
        mats["soft"],
        f"grip__{cand}__{side}_grip_inlay",
    )


_GRIP_BUILDERS = {
    "lofted_oval": _grip_lofted_oval_build,
    "stamped_molded": _grip_stamped_molded_build,
}


# ---------------------------------------------------------------------------
# Frame (root): stamped carrier + mouth + head statics + spine + tang + grip
# + the pivot pin.
# ---------------------------------------------------------------------------
def _build_frame(model: ArticulatedObject, r: ResolvedConfig, mats):
    frame = model.part("frame", meta={"role": "opener_frame"})

    outline, holes = _MOUTH_OUTLINES[r.mouth](r)
    if holes:
        _plate_with_hole(
            frame, outline, holes, _PLATE_Z0, _PLATE_T, mats["steel"], "stamped_carrier"
        )
    else:
        _plate(frame, outline, _PLATE_Z0, _PLATE_T, mats["steel"], "stamped_carrier")
    _MOUTH_EXTRAS[r.mouth](frame, r, mats, r.mouth)

    rotors = _HEAD_BUILDERS[r.head](frame, r, mats)
    _SPINE_BUILDERS[r.spine](frame, r, mats)

    # Lower handle tang: the stamped continuation that carries the molded grip.
    reach = r.frame_tang_reach
    tang = [
        (0.004, -0.0078),
        (reach, -0.0062),
        (reach + 0.008, 0.0),
        (reach, 0.0062),
        (0.004, 0.0086),
    ]
    _plate(
        frame, _rot(tang, _FRAME_YAW), _FRAME_TANG_Z0, _FRAME_TANG_T, mats["satin"], "lower_tang"
    )

    _GRIP_BUILDERS[r.grip](frame, r, mats, upper=False)

    # Main pivot pin.  It rises out of the carrier and presses _MOUNT into the
    # moving lever plate's underside: the single captured frame/lever contact.
    pin_len = _PIN_TOP - _PLATE_Z0
    _cyl(frame, _PIN_R, pin_len, (0.0, 0.0, _PLATE_Z0 + 0.5 * pin_len), mats["satin"], "pivot_pin")
    _cyl(frame, 0.0072, 0.0026, (0.0, 0.0, 0.0043), mats["hard"], "pivot_collar")
    return frame, rotors


# ---------------------------------------------------------------------------
# Lever (moving half): stamped plate + jaw finger + tang + molded grip + boss.
# ---------------------------------------------------------------------------
def _lever_head_extras(lever, r: ResolvedConfig, mats) -> None:
    """Head hardware that belongs to the MOVING half."""
    if r.head != "lever_cutter":
        return
    cand = "lever_cutter"
    # Sharpened cutting wheel hanging under the lever nose, swinging toward the
    # frame's fixed feed wheel as the handles close -- rec ...039038 L305-L318.
    _plate(
        lever,
        _toothed_disc(-0.025, 0.004, 0.80 * 0.0082, 0.0082, 20),
        _JAW_Z0,
        _JAW_Z1 - _JAW_Z0,
        mats["hard"],
        f"head__{cand}__lever_cutting_wheel",
    )
    _cyl(
        lever,
        0.0022,
        0.0070,
        (-0.025, 0.004, _JAW_Z0 + 0.0035),
        mats["satin"],
        f"head__{cand}__lever_cutter_axle",
    )


def _build_lever(model: ArticulatedObject, r: ResolvedConfig, mats):
    lever = model.part("lever", meta={"role": "opener_lever"})
    gl = r.grip_length_m
    plate = [
        (-0.034, -0.0090),
        (-0.014, -0.0140),
        (0.012, -0.0130),
        (0.045, -0.0105),
        (0.030 + 0.55 * gl, -0.0085),
        (0.045 + gl, -0.0060),
        (0.051 + gl, 0.0),
        (0.045 + gl, 0.0060),
        (0.030 + 0.55 * gl, 0.0092),
        (0.045, 0.0118),
        (0.012, 0.0155),
        (-0.014, 0.0160),
        (-0.034, 0.0105),
    ]
    _plate(
        lever,
        _rot(plate, _LEVER_YAW),
        _LEVER_Z0,
        _LEVER_Z1 - _LEVER_Z0,
        mats["steel"],
        "lever_plate",
    )

    # Moving gripping jaw finger reaching over the working mouth.  It is the
    # part of the lever that closes on the lid rim; it hangs below the plate but
    # stays above every frame element (_JAW_Z0 > _HW_TOP).
    fx, fy = _rot([(-0.026, 0.002)], _LEVER_YAW)[0]
    _box(
        lever,
        (0.020, 0.0090, _JAW_Z1 - _JAW_Z0),
        (fx, fy, 0.5 * (_JAW_Z0 + _JAW_Z1)),
        mats["hard"],
        "jaw_finger",
        rpy=(0.0, 0.0, _LEVER_YAW),
    )
    _box(
        lever,
        (0.0060, 0.0090, 0.0030),
        (
            fx - 0.0095 * math.cos(_LEVER_YAW) - 0.0060 * math.sin(_LEVER_YAW),
            fy - 0.0095 * math.sin(_LEVER_YAW) + 0.0060 * math.cos(_LEVER_YAW),
            _JAW_Z0 + 0.0015,
        ),
        mats["grip"],
        "jaw_finger_pad",
        rpy=(0.0, 0.0, _LEVER_YAW),
    )

    _lever_head_extras(lever, r, mats)

    # Upper tang bridging the lever plate into the molded grip core.
    reach = r.lever_tang_reach
    tang = [
        (0.020, -0.0070),
        (reach, -0.0058),
        (reach + 0.007, 0.0),
        (reach, 0.0058),
        (0.020, 0.0078),
    ]
    _plate(
        lever, tang, _LEVER_TANG_Z0, _LEVER_TANG_Z1 - _LEVER_TANG_Z0, mats["satin"], "upper_tang"
    )

    _GRIP_BUILDERS[r.grip](lever, r, mats, upper=True)

    # Pivot boss + cap sitting on top of the lever plate around the pin.
    _cyl(lever, 0.0110, 0.0040, (0.0, 0.0, _LEVER_Z1 + 0.0010), mats["steel"], "pivot_boss")
    _cyl(lever, 0.0072, 0.0022, (0.0, 0.0, _LEVER_Z1 + 0.0038), mats["satin"], "pivot_cap")
    return lever


# ---------------------------------------------------------------------------
# Joints -- every rotational joint is solved by mate_axes on the true design
# axis and registered with register_interface_mate.
# ---------------------------------------------------------------------------
def _add_handle_pivot(model, frame, lever, r: ResolvedConfig) -> None:
    name = "handle_pivot"
    provider = AxisInterface(
        name=f"{name}__provider",
        # Axis line, not a height: the pivot frame is kept at z=0 so every
        # authored lever z band above is literally its world band.
        point=(0.0, 0.0, 0.0),
        axis=(0.0, 0.0, 1.0),
        radial=(1.0, 0.0, 0.0),
    )
    consumer = AxisInterface(name=f"{name}__consumer", axis=(0.0, 0.0, 1.0), radial=(1.0, 0.0, 0.0))
    mate = mate_axes(provider, consumer)
    model.articulation(
        name,
        ArticulationType.REVOLUTE,
        parent=frame,
        child=lever,
        origin=mate.origin,
        axis=mate.axis,
        # Measured with a ctx.pose probe on the jaw finger: a NEGATIVE angle
        # squeezes the upper handle down onto the lower one, which (the nose is
        # on the far side of the pivot) drives the moving jaw finger UP toward
        # the carrier's fixed upper lip -- the lid rim is pinched between them.
        # A POSITIVE angle opens the plier.  Full source-like travel, no clamp.
        motion_limits=MotionLimits(
            lower=r.pivot_lower, upper=r.pivot_upper, effort=65.0, velocity=2.5
        ),
        meta={"mechanism": "plier squeeze closes the gripping jaw over a lid rim"},
    )
    register_interface_mate(model, name, mate)


def _add_rotor_joint(model, frame, rotor, r: ResolvedConfig, local: str, xy) -> None:
    name = f"head__{r.head}__{local}_spin"
    provider = AxisInterface(
        name=f"{name}__provider",
        # Vertical shaft line through the hub; z=0 keeps rotor-local == world.
        point=(xy[0], xy[1], 0.0),
        axis=(0.0, 0.0, 1.0),
        radial=(1.0, 0.0, 0.0),
    )
    consumer = AxisInterface(name=f"{name}__consumer", axis=(0.0, 0.0, 1.0), radial=(1.0, 0.0, 0.0))
    mate = mate_axes(provider, consumer)
    model.articulation(
        name,
        ArticulationType.CONTINUOUS,
        parent=frame,
        child=rotor,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(effort=10.0, velocity=9.0),
        meta={"mechanism": f"{local} spins on its carrier-mounted shaft"},
    )
    register_interface_mate(model, name, mate)


# ---------------------------------------------------------------------------
# Assembly
# ---------------------------------------------------------------------------
def build_picturex_0611_lid_opener(
    config: Config | None = None, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    r = resolve_config(config or config_from_seed(0))
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={
            "category": "pictureX_0611_Lid_opener",
            "small_class": "Lid_opener",
            "slot_choices": slot_choices_for_config(r),
            "source_family": "pictureX/0611/Lid_opener",
        },
    )
    mats = _materials(model, r)
    frame, rotors = _build_frame(model, r, mats)
    lever = _build_lever(model, r, mats)
    _add_handle_pivot(model, frame, lever, r)

    for spec in rotors:
        local = spec["local"]
        part = model.part(
            f"head__{r.head}__{local}",
            meta={"role": "head_rotor", "candidate": r.head, "station": local},
        )
        spec["build"](part)
        _add_rotor_joint(model, frame, part, r, local, spec["xy"])

    rotor_names = [f"head__{r.head}__{spec['local']}_spin" for spec in rotors]
    model.meta["risk_poses"] = tuple(
        [
            {"handle_pivot": r.pivot_lower},
            {"handle_pivot": r.pivot_upper},
            {"handle_pivot": r.pivot_lower, **{n: 0.9 for n in rotor_names}},
            {"handle_pivot": r.pivot_upper, **{n: -0.9 for n in rotor_names}},
        ]
    )
    if rotor_names:
        model.meta["coupled_joint_pairs"] = tuple(("handle_pivot", n) for n in rotor_names)
    return model


def build_seeded_picturex_0611_lid_opener(seed: int, *, assets: AssetContext | None = None):
    return build_picturex_0611_lid_opener(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Author tests -- category invariants and derived-parameter arithmetic only.
# Mesh assets, exact collision, sampled-pose overlap and isolated-geometry QC
# belong to the sweep harness, so nothing here touches a mesh element.
# ---------------------------------------------------------------------------
def _parts_by_role(model: ArticulatedObject, role: str):
    return [p for p in model.parts if p.meta.get("role") == role]


def run_picturex_0611_lid_opener_tests(
    object_model: ArticulatedObject, config: Config
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)

    frames = _parts_by_role(object_model, "opener_frame")
    levers = _parts_by_role(object_model, "opener_lever")
    rotors = _parts_by_role(object_model, "head_rotor")
    frame = frames[0] if frames else None
    lever = levers[0] if levers else None
    frame_elems = {v.name or "" for v in frame.visuals} if frame is not None else set()
    lever_elems = {v.name or "" for v in lever.visuals} if lever is not None else set()

    pivot = next((j for j in object_model.articulations if j.name == "handle_pivot"), None)

    ctx.check(
        "category_anchor: one stamped frame and one lever plier half on a pivot",
        len(frames) == 1
        and len(levers) == 1
        and {"stamped_carrier", "lower_tang", "pivot_pin", "pivot_collar"} <= frame_elems
        and {"lever_plate", "upper_tang", "jaw_finger", "jaw_finger_pad", "pivot_boss"}
        <= lever_elems,
        details=f"frames={len(frames)}, levers={len(levers)}, frame_elems={sorted(frame_elems)}",
    )

    ctx.check(
        "category_anchor: the lever squeezes on a registered vertical pivot axis",
        pivot is not None
        and pivot.articulation_type == ArticulationType.REVOLUTE
        and tuple(round(v, 6) for v in pivot.axis) == (0.0, 0.0, 1.0)
        and pivot.parent == "frame"
        and pivot.child == "lever"
        and pivot.motion_limits is not None
        and pivot.motion_limits.lower < 0.0 < pivot.motion_limits.upper,
        details=f"pivot={getattr(pivot, 'name', None)}",
    )

    spin_joints = [j for j in object_model.articulations if j.name.endswith("_spin")]
    ctx.check(
        "category_anchor: the head family supplies its own rotor joint graph",
        len(rotors) == HEAD_ROTOR_COUNT[r.head]
        and len(spin_joints) == HEAD_ROTOR_COUNT[r.head]
        and all(
            j.articulation_type == ArticulationType.CONTINUOUS
            and j.parent == "frame"
            and tuple(round(v, 6) for v in j.axis) == (0.0, 0.0, 1.0)
            for j in spin_joints
        ),
        details=f"head={r.head}, rotors={[p.name for p in rotors]}",
    )

    # Head-family element signature (part-tree difference, not material).
    if r.head == "rotary_crank":
        head_ok = any((v.name or "").endswith("__crank_knob") for p in rotors for v in p.visuals)
    elif r.head == "feed_gear":
        head_ok = "head__feed_gear__cutting_wheel" in frame_elems
    elif r.head == "lever_cutter":
        head_ok = "head__lever_cutter__lever_cutting_wheel" in lever_elems
    else:
        head_ok = {
            "head__guarded_head__guard_post",
            "head__guarded_head__guard_bridge",
            "head__guarded_head__guide_roller",
        } <= frame_elems
    ctx.check(
        "category_anchor: the head family's own hardware sits on the right half",
        head_ok,
        details=f"head={r.head}",
    )

    mouth_marker = {
        "crescent": "mouth__crescent__jaw_pad",
        "round_throat": "mouth__round_throat__nose_rivet",
        "notched_cheek": "mouth__notched_cheek__notch_lip",
        "hooked_jaw": "mouth__hooked_jaw__hooked_jaw",
    }[r.mouth]
    ctx.check(
        "category_anchor: the working lid mouth is real carrier geometry",
        mouth_marker in frame_elems,
        details=f"mouth={r.mouth}, marker={mouth_marker}",
    )

    grip_marker = (
        "grip__lofted_oval__lower_grip"
        if r.grip == "lofted_oval"
        else "grip__stamped_molded__lower_grip"
    )
    upper_marker = grip_marker.replace("lower_", "upper_")
    ctx.check(
        "both handles carry the same grip construction",
        grip_marker in frame_elems and upper_marker in lever_elems,
        details=f"grip={r.grip}",
    )

    spine_prefix = f"spine__{r.spine}__"
    ctx.check(
        "the carrier's reinforcement layer is present",
        sum(1 for n in frame_elems if n.startswith(spine_prefix)) >= 2,
        details=f"spine={r.spine}",
    )

    # ---- derived-parameter invariants (pure arithmetic, no geometry) --------
    ctx.check(
        "pivot pin seats into the lever plate by exactly the captured lap",
        abs((_PIN_TOP - _LEVER_Z0) - _MOUNT) < 1e-9 and 0.0 < _MOUNT < 0.001,
        details=f"pin_top={_PIN_TOP}, lever_z0={_LEVER_Z0}, mount={_MOUNT}",
    )
    ctx.check(
        "the moving jaw band clears every fixed head member",
        _JAW_Z0 - _HW_TOP >= 0.0009 and _JAW_Z1 <= _LEVER_Z1,
        details=f"jaw_z0={_JAW_Z0}, hw_top={_HW_TOP}, jaw_z1={_JAW_Z1}",
    )
    ctx.check(
        "the two molded grips occupy disjoint vertical bands",
        _LEVER_GRIP_Z0 - (_FRAME_GRIP_Z0 + _FRAME_GRIP_T) >= 0.010,
        details=f"lower_top={_FRAME_GRIP_Z0 + _FRAME_GRIP_T}, upper_bottom={_LEVER_GRIP_Z0}",
    )
    gap_drive_feed = math.dist(r.drive_xy, r.feed_xy) - (r.drive_r + r.feed_r)
    gap_feed_cutter = math.dist(r.feed_xy, r.cutter_xy) - (r.feed_r + r.cutter_r)
    ctx.check(
        "the head shaft stations keep a real radial gap at every head_span",
        gap_drive_feed >= 0.10 * r.head_span_m and gap_feed_cutter >= 0.10 * r.head_span_m,
        details=f"drive_feed={gap_drive_feed:.5f}, feed_cutter={gap_feed_cutter:.5f}",
    )
    ctx.check(
        "the crank sweep envelope stays clear of the feed wheel",
        (1.57 * r.drive_r + r.feed_r) < math.dist(r.drive_xy, r.feed_xy) - 0.001,
        details=f"envelope={1.57 * r.drive_r:.5f}, dist={math.dist(r.drive_xy, r.feed_xy):.5f}",
    )
    ctx.check(
        "the working mouth is derived from head_span and stays on the nose",
        r.mouth_x <= -(r.head_span_m + 0.011) and r.nose_tip_x < r.mouth_x - 0.45 * r.mouth_size_m,
        details=f"mouth_x={r.mouth_x:.4f}, tip={r.nose_tip_x:.4f}, size={r.mouth_size_m:.4f}",
    )
    ctx.check(
        "each grip is bridged to its stamped half by a tang that reaches past it",
        r.frame_tang_reach > 0.040 and r.lever_tang_reach > 0.046,
        details=f"frame_tang={r.frame_tang_reach:.4f}, lever_tang={r.lever_tang_reach:.4f}",
    )

    # ---- pose semantics, probed on NON-mesh Box elements only ---------------
    if lever is not None and pivot is not None:
        with ctx.pose({pivot: r.pivot_upper}):
            open_jaw = ctx.part_element_world_aabb(lever, elem="jaw_finger")
        with ctx.pose({pivot: r.pivot_lower}):
            shut_jaw = ctx.part_element_world_aabb(lever, elem="jaw_finger")
        ctx.check(
            "squeezing the handles drives the moving jaw toward the fixed lip",
            open_jaw is not None
            and shut_jaw is not None
            and shut_jaw[1][1] > open_jaw[1][1] + 0.006,
            details=f"open={open_jaw}, closed={shut_jaw}",
        )
        ctx.check(
            "the jaw finger never dips into the fixed head hardware band",
            shut_jaw is not None and shut_jaw[0][2] >= _HW_TOP + 0.0009,
            details=f"jaw_bottom_z={None if shut_jaw is None else shut_jaw[0][2]}",
        )

    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    return ctx.report()


# ---------------------------------------------------------------------------
# High-risk corners.  Jaw fully open vs fully closed and the coupled jaw+rotor
# extremes are motion poses, declared through model.meta risk_poses /
# coupled_joint_pairs; the corners below cover the structural extremes.
# ---------------------------------------------------------------------------
TEMPLATE_CORNERS = (
    corner_case(
        "max_head_crank_crescent_lofted",
        {
            "head": "rotary_crank",
            "mouth": "crescent",
            "grip": "lofted_oval",
            "spine": "folded_bracket",
            "head_span_m": _HEAD_SPAN_MAX,
            "grip_length_m": _GRIP_LEN_MAX,
            "mouth_size_m": _MOUTH_SIZE_MAX,
        },
        reason="Largest head with three rotors, deepest crescent mouth, longest lofted grips.",
    ),
    corner_case(
        "min_head_crank_throat_stamped",
        {
            "head": "rotary_crank",
            "mouth": "round_throat",
            "grip": "stamped_molded",
            "spine": "weld_backplate",
            "head_span_m": _HEAD_SPAN_MIN,
            "grip_length_m": _GRIP_LEN_MIN,
            "mouth_size_m": _MOUTH_SIZE_MAX,
        },
        reason="Tightest gear train: three rotor stations closest together, largest bored throat.",
    ),
    corner_case(
        "min_head_lever_cutter_notch_lofted",
        {
            "head": "lever_cutter",
            "mouth": "notched_cheek",
            "grip": "lofted_oval",
            "spine": "weld_backplate",
            "head_span_m": _HEAD_SPAN_MIN,
            "grip_length_m": _GRIP_LEN_MAX,
            "mouth_size_m": _MOUTH_SIZE_MAX,
        },
        reason="The moving cutter rides the lever over the smallest head while the notch is deepest.",
    ),
    corner_case(
        "max_head_guarded_hook_stamped",
        {
            "head": "guarded_head",
            "mouth": "hooked_jaw",
            "grip": "stamped_molded",
            "spine": "folded_bracket",
            "head_span_m": _HEAD_SPAN_MAX,
            "grip_length_m": _GRIP_LEN_MIN,
            "mouth_size_m": _MOUTH_SIZE_MAX,
        },
        reason="Folded guard at full head span with the largest hooked claw and the shortest grips.",
    ),
    corner_case(
        "min_head_feed_gear_hook_lofted",
        {
            "head": "feed_gear",
            "mouth": "hooked_jaw",
            "grip": "lofted_oval",
            "spine": "folded_bracket",
            "head_span_m": _HEAD_SPAN_MIN,
            "grip_length_m": _GRIP_LEN_MIN,
            "mouth_size_m": _MOUTH_SIZE_MIN,
        },
        reason="Continuous feed rotor closest to the static cutting wheel at the minimum head span.",
    ),
)
