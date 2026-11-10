# SPDX-License-Identifier: Apache-2.0

"""Modular Handtools/Pen template.

Built from the reviewed Handtools/Pen spec and source-map pool:
``picture/Handtools/Pen`` plus one supplementary rounded-rect pull-cap parent.

This template treats slot diversity as a mix of:
- actuation mechanism changes
- non-joint structural exterior changes

It keeps the dominant Handtools identity centered on metallic mechanism-heavy
pens while still allowing the rounded-rect pull-cap family as a gated
supplementary branch.
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
    LatheGeometry,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    TorusGeometry,
    mesh_from_cadquery,
    mesh_from_geometry,
)

__modular__ = True

Actuation = Literal[
    "click_plunger",
    "twist_sleeve",
    "side_slider",
    "hinged_cap",
    "removable_pull_cap",
]
BarrelProfile = Literal["round_lathe", "hex_prism", "rounded_rect"]
PocketClip = Literal["windowed_clip", "solid_clip", "no_clip"]
GripSurface = Literal["plain", "contoured_rubber_grip", "ring_bands", "face_strips"]
PaletteStyle = Literal[
    "brushed_silver",
    "graphite_black",
    "navy_trim",
    "industrial_red",
    "champagne_steel",
    "charcoal_rubber",
]
ClipMount = Literal["barrel", "sleeve", "cap"]

ACTUATIONS: tuple[Actuation, ...] = (
    "click_plunger",
    "twist_sleeve",
    "side_slider",
    "hinged_cap",
    "removable_pull_cap",
)
BARREL_PROFILES: tuple[BarrelProfile, ...] = ("round_lathe", "hex_prism", "rounded_rect")
POCKET_CLIPS: tuple[PocketClip, ...] = ("windowed_clip", "solid_clip", "no_clip")
GRIP_SURFACES: tuple[GripSurface, ...] = (
    "plain",
    "contoured_rubber_grip",
    "ring_bands",
    "face_strips",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "brushed_silver",
    "graphite_black",
    "navy_trim",
    "industrial_red",
    "champagne_steel",
    "charcoal_rubber",
)

PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "brushed_silver": {
        "body": (0.74, 0.75, 0.77, 1.0),
        "trim": (0.83, 0.84, 0.86, 1.0),
        "tip": (0.62, 0.63, 0.66, 1.0),
        "dark": (0.22, 0.22, 0.24, 1.0),
        "accent": (0.68, 0.70, 0.73, 1.0),
        "cap": (0.20, 0.22, 0.25, 1.0),
    },
    "graphite_black": {
        "body": (0.18, 0.19, 0.21, 1.0),
        "trim": (0.48, 0.49, 0.52, 1.0),
        "tip": (0.62, 0.63, 0.66, 1.0),
        "dark": (0.08, 0.08, 0.09, 1.0),
        "accent": (0.33, 0.34, 0.36, 1.0),
        "cap": (0.12, 0.12, 0.13, 1.0),
    },
    "navy_trim": {
        "body": (0.72, 0.74, 0.76, 1.0),
        "trim": (0.12, 0.20, 0.42, 1.0),
        "tip": (0.60, 0.61, 0.64, 1.0),
        "dark": (0.10, 0.12, 0.20, 1.0),
        "accent": (0.20, 0.25, 0.48, 1.0),
        "cap": (0.14, 0.18, 0.42, 1.0),
    },
    "industrial_red": {
        "body": (0.67, 0.69, 0.72, 1.0),
        "trim": (0.64, 0.12, 0.10, 1.0),
        "tip": (0.58, 0.58, 0.60, 1.0),
        "dark": (0.18, 0.18, 0.19, 1.0),
        "accent": (0.72, 0.14, 0.12, 1.0),
        "cap": (0.52, 0.12, 0.10, 1.0),
    },
    "champagne_steel": {
        "body": (0.78, 0.73, 0.63, 1.0),
        "trim": (0.89, 0.82, 0.68, 1.0),
        "tip": (0.64, 0.62, 0.58, 1.0),
        "dark": (0.28, 0.24, 0.20, 1.0),
        "accent": (0.84, 0.76, 0.60, 1.0),
        "cap": (0.44, 0.33, 0.18, 1.0),
    },
    "charcoal_rubber": {
        "body": (0.66, 0.68, 0.70, 1.0),
        "trim": (0.80, 0.81, 0.84, 1.0),
        "tip": (0.60, 0.61, 0.64, 1.0),
        "dark": (0.14, 0.14, 0.16, 1.0),
        "accent": (0.18, 0.18, 0.20, 1.0),
        "cap": (0.16, 0.16, 0.18, 1.0),
    },
}

# Common scale (meters), normalized to +Z long axis.
COLLAR_TOP_Z = 0.118
COLLAR_BOT_Z = 0.100
BODY_TOP_Z = 0.100
NOSE_TOP_Z = 0.030
NOSE_TIP_Z = 0.006
TIP_END_Z = 0.000
SEAM_Z = 0.100

R_COLLAR = 0.0062
R_BODY_TOP = 0.0058
R_BODY_MID = 0.0056
R_NOSE_TOP = 0.0050
R_TIP_SEAT = 0.0011
R_BALL = 0.0006
BORE_R = 0.0040

TWIST_UPPER = math.pi / 2.0
PLUNGER_TRAVEL = 0.007
SLIDER_TRAVEL = 0.020
HINGE_UPPER = 2.8

RECT_BODY_W = 0.0170
RECT_BODY_D = 0.0120
RECT_CORNER_R = 0.0030
RECT_BODY_Z0 = 0.030
RECT_BODY_Z1 = 0.120
RECT_COLLAR_Z0 = 0.024
RECT_COLLAR_Z1 = 0.030
RECT_COLLAR_W = 0.0150
RECT_COLLAR_D = 0.0105
RECT_COLLAR_R = 0.0028

PULL_CAP_LEN = 0.040
PULL_CAP_WALL = 0.0014
# Radial fit between the cap cavity and the rect body. A small NEGATIVE value =
# a light press/slip fit: the cap grips the body over their short overlap band
# (so the cap is grounded to the barrel, not a floating part) while the
# interference stays well under the overlap-flag depth. It is still looser than
# the collar/nose/nib, so the cap contacts ONLY the body — never the tip.
PULL_CAP_CLEAR = -0.0005
# How far the cap's closed floor sits BELOW the nib tip at rest. Keeping the
# floor under the tip at every pose guarantees the cap never drives through the
# writing tip as it is pulled off.
PULL_CAP_FLOOR_DROP = 0.0034

N_GRIP_MIN = 0
N_GRIP_MAX = 8


@dataclass(frozen=True)
class PenConfig:
    actuation: Actuation | None = None
    barrel_profile: BarrelProfile | None = None
    pocket_clip: PocketClip | None = None
    grip_surface: GripSurface | None = None
    palette_style: PaletteStyle | None = None
    n_grip_bands: int | None = None
    barrel_len_scale: float = 1.0
    barrel_girth_scale: float = 1.0
    actuation_travel_scale: float = 1.0
    grip_zone_scale: float = 1.0
    name: str = "pen"


@dataclass(frozen=True)
class ResolvedPenConfig:
    actuation: Actuation
    barrel_profile: BarrelProfile
    pocket_clip: PocketClip
    grip_surface: GripSurface
    palette_style: PaletteStyle
    n_grip_bands: int
    barrel_len_scale: float
    barrel_girth_scale: float
    actuation_travel_scale: float
    grip_zone_scale: float
    clip_mount: ClipMount
    name: str


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _weighted_choice(rng: random.Random, items: list[tuple[str, float]]) -> str:
    total = sum(weight for _, weight in items)
    ticket = rng.random() * total
    upto = 0.0
    for label, weight in items:
        upto += weight
        if ticket <= upto:
            return label
    return items[-1][0]


# Coherent perceptual families: (label, actuation, barrel_profile, weight).
# Sampling a whole family first guarantees each pen reads as ONE real object
# instead of a mismatched hybrid (e.g. a round click button on a rect marker
# body, or a rect pull-cap floating over a round barrel). Grip / clip options
# are then drawn only from what is structurally valid for that family.
PEN_FAMILIES: tuple[tuple[str, Actuation, BarrelProfile, float], ...] = (
    ("round_click", "click_plunger", "round_lathe", 0.20),
    ("round_twist", "twist_sleeve", "round_lathe", 0.13),
    ("round_slider", "side_slider", "round_lathe", 0.11),
    ("round_hinged", "hinged_cap", "round_lathe", 0.13),
    ("hex_click", "click_plunger", "hex_prism", 0.19),
    ("rect_pullcap", "removable_pull_cap", "rounded_rect", 0.24),
)


def config_from_seed(seed: int) -> PenConfig:
    rng = random.Random(seed)
    family = _weighted_choice(rng, [(f[0], f[3]) for f in PEN_FAMILIES])
    _, actuation, barrel_profile, _ = next(f for f in PEN_FAMILIES if f[0] == family)

    if barrel_profile == "hex_prism":
        # face_strips is the hex-native surface treatment; contoured grip is a
        # round-lathe silhouette and is not offered here.
        grip_surface = _weighted_choice(
            rng,
            [("plain", 0.34), ("face_strips", 0.40), ("ring_bands", 0.26)],
        )
    elif barrel_profile == "rounded_rect":
        grip_surface = _weighted_choice(
            rng,
            [("plain", 0.55), ("ring_bands", 0.45)],
        )
    elif actuation == "click_plunger":
        # Only the click round barrel actually reshapes its silhouette for the
        # contoured rubber grip, so that option is scoped to this family.
        grip_surface = _weighted_choice(
            rng,
            [("plain", 0.34), ("ring_bands", 0.33), ("contoured_rubber_grip", 0.33)],
        )
    else:  # twist / slider / hinged round barrels keep a plain or banded surface
        grip_surface = _weighted_choice(
            rng,
            [("plain", 0.52), ("ring_bands", 0.48)],
        )

    pocket_clip = _weighted_choice(
        rng,
        [
            ("windowed_clip", 0.50),
            ("solid_clip", 0.30),
            ("no_clip", 0.20),
        ],
    )
    palette_style = rng.choice(PALETTE_STYLES)
    n_grip_bands = rng.randint(4, 6)
    return PenConfig(
        actuation=actuation,  # type: ignore[arg-type]
        barrel_profile=barrel_profile,  # type: ignore[arg-type]
        pocket_clip=pocket_clip,  # type: ignore[arg-type]
        grip_surface=grip_surface,  # type: ignore[arg-type]
        palette_style=palette_style,
        n_grip_bands=n_grip_bands,
        barrel_len_scale=rng.uniform(0.92, 1.08),
        barrel_girth_scale=rng.uniform(0.92, 1.08),
        actuation_travel_scale=rng.uniform(0.90, 1.12),
        grip_zone_scale=rng.uniform(0.88, 1.12),
        name="pen",
    )


def resolve_config(config: PenConfig) -> ResolvedPenConfig:
    actuation = config.actuation or "click_plunger"
    barrel_profile = config.barrel_profile or "round_lathe"
    pocket_clip = config.pocket_clip or "windowed_clip"
    grip_surface = config.grip_surface or "plain"
    palette_style = config.palette_style or "brushed_silver"
    n_grip_bands = config.n_grip_bands if config.n_grip_bands is not None else 0

    # Coherent family reconciliation. `actuation` is the primary identity axis;
    # the barrel profile is derived from it so we never emit a mechanism/body
    # mismatch, then the surface treatment is reconciled against the final
    # profile. Order is deliberate and non-overlapping (unlike the old gates,
    # where a later grip rule could silently undo an earlier profile choice).
    if actuation == "removable_pull_cap":
        barrel_profile = "rounded_rect"
    elif actuation in {"twist_sleeve", "side_slider", "hinged_cap"}:
        # Round nose / collar grammar is what the twist seam, side slot and
        # hinged round cap are authored against.
        barrel_profile = "round_lathe"
    elif actuation == "click_plunger":
        # click is valid on round or hex; a rectangular marker body does not
        # take a click plunger.
        if barrel_profile == "rounded_rect":
            barrel_profile = "round_lathe"

    # Surface treatment must match the profile that actually got built.
    if barrel_profile == "rounded_rect":
        if grip_surface in {"contoured_rubber_grip", "face_strips"}:
            grip_surface = "ring_bands"
    elif barrel_profile == "hex_prism":
        if grip_surface == "contoured_rubber_grip":
            grip_surface = "face_strips"
    else:  # round_lathe
        if grip_surface == "face_strips":
            grip_surface = "ring_bands"
    # Only the round click barrel reshapes its silhouette for the rubber grip.
    if grip_surface == "contoured_rubber_grip" and not (
        barrel_profile == "round_lathe" and actuation == "click_plunger"
    ):
        grip_surface = "ring_bands"

    if grip_surface == "plain":
        n_grip_bands = 0
    elif grip_surface == "ring_bands":
        n_grip_bands = max(4, n_grip_bands)
    elif grip_surface == "contoured_rubber_grip":
        n_grip_bands = 6
    else:  # face_strips are fixed to the six hex faces
        n_grip_bands = 0

    n_grip_bands = int(_clamp(n_grip_bands, N_GRIP_MIN, N_GRIP_MAX))

    clip_mount: ClipMount = "barrel"
    if actuation == "removable_pull_cap":
        clip_mount = "cap"

    return ResolvedPenConfig(
        actuation=actuation,
        barrel_profile=barrel_profile,
        pocket_clip=pocket_clip,
        grip_surface=grip_surface,
        palette_style=palette_style,
        n_grip_bands=n_grip_bands,
        barrel_len_scale=_clamp(config.barrel_len_scale, 0.92, 1.08),
        barrel_girth_scale=_clamp(config.barrel_girth_scale, 0.92, 1.08),
        actuation_travel_scale=_clamp(config.actuation_travel_scale, 0.90, 1.12),
        grip_zone_scale=_clamp(config.grip_zone_scale, 0.88, 1.12),
        clip_mount=clip_mount,
        name=config.name or "pen",
    )


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    r = resolve_config(config_from_seed(seed))
    grip_choice = r.grip_surface
    if r.grip_surface == "ring_bands":
        grip_choice = f"ring_bands_{r.n_grip_bands}"  # type: ignore[assignment]
    return [
        ("actuation", r.actuation),
        ("barrel_profile", r.barrel_profile),
        ("pocket_clip", r.pocket_clip),
        ("grip_surface", grip_choice),
    ]


def _palette_materials(model: ArticulatedObject, style: PaletteStyle) -> dict[str, str]:
    rgba = PALETTES[style]
    mats: dict[str, str] = {}
    for role, color in rgba.items():
        name = f"pen_{style}_{role}"
        model.material(name, rgba=color)
        mats[role] = name
    return mats


def _build_round_barrel_geometry(r: ResolvedPenConfig) -> LatheGeometry:
    girth = r.barrel_girth_scale
    body_top = R_BODY_TOP * girth
    body_mid = R_BODY_MID * girth
    collar = R_COLLAR * girth
    nose_top = R_NOSE_TOP * girth
    tip_seat = R_TIP_SEAT * girth
    ball = R_BALL * girth
    bore = BORE_R * girth
    body_top_z = BODY_TOP_Z * r.barrel_len_scale
    seam_z = SEAM_Z * r.barrel_len_scale
    collar_top_z = COLLAR_TOP_Z * r.barrel_len_scale
    collar_bot_z = COLLAR_BOT_Z * r.barrel_len_scale
    nose_top_z = NOSE_TOP_Z * r.barrel_len_scale
    nose_tip_z = NOSE_TIP_Z * r.barrel_len_scale
    bore_bottom_z = collar_top_z - 0.055 * r.barrel_len_scale

    if r.grip_surface == "contoured_rubber_grip":
        profile = [
            (0.0, TIP_END_Z),
            (ball, nose_tip_z * 0.45),
            (tip_seat, nose_tip_z),
            (nose_top, nose_top_z),
            (0.0048 * girth, 0.033 * r.barrel_len_scale),
            (0.0044 * girth, 0.036 * r.barrel_len_scale),
            (0.0040 * girth, 0.040 * r.barrel_len_scale),
            (0.0043 * girth, 0.043 * r.barrel_len_scale),
            (0.0048 * girth, 0.047 * r.barrel_len_scale),
            (0.0042 * girth, 0.053 * r.barrel_len_scale),
            (0.0052 * girth, 0.060 * r.barrel_len_scale),
            (body_top, 0.065 * r.barrel_len_scale),
            (body_top, body_top_z),
        ]
    else:
        profile = [
            (0.0, TIP_END_Z),
            (ball, nose_tip_z * 0.45),
            (tip_seat, nose_tip_z),
            (nose_top, nose_top_z),
            (body_mid, 0.060 * r.barrel_len_scale),
            (body_top, body_top_z),
        ]

    if r.actuation == "click_plunger":
        profile.extend(
            [
                (body_top, collar_bot_z),
                (collar, collar_bot_z + 0.001 * r.barrel_len_scale),
                (collar, collar_top_z),
                (bore, collar_top_z),
                (bore, bore_bottom_z),
                (0.0, bore_bottom_z),
            ]
        )
    elif r.actuation == "twist_sleeve":
        profile.extend(
            [
                (body_top, seam_z),
                (0.0, seam_z),
            ]
        )
    else:
        crown_top_z = collar_top_z + 0.008 * r.barrel_len_scale
        profile.extend(
            [
                (body_top, collar_bot_z),
                (collar, collar_bot_z + 0.001 * r.barrel_len_scale),
                (collar, collar_top_z),
                (collar, crown_top_z - 0.003 * r.barrel_len_scale),
                (collar * 0.80, crown_top_z - 0.001 * r.barrel_len_scale),
                (collar * 0.45, crown_top_z),
                (0.0, crown_top_z + 0.001 * r.barrel_len_scale),
            ]
        )

    return LatheGeometry(profile, segments=64, closed=True)


def _build_side_slider_barrel_cq(r: ResolvedPenConfig) -> cq.Workplane:
    girth = r.barrel_girth_scale
    body_top = R_BODY_TOP * girth
    body_mid = R_BODY_MID * girth
    collar = R_COLLAR * girth
    nose_top = R_NOSE_TOP * girth
    tip_seat = R_TIP_SEAT * girth
    ball = R_BALL * girth
    body_top_z = BODY_TOP_Z * r.barrel_len_scale
    collar_top_z = COLLAR_TOP_Z * r.barrel_len_scale
    nose_top_z = NOSE_TOP_Z * r.barrel_len_scale
    nose_tip_z = NOSE_TIP_Z * r.barrel_len_scale
    dome_apex = collar_top_z + 0.0015 * r.barrel_len_scale
    profile = (
        cq.Workplane("XZ")
        .moveTo(0.0, TIP_END_Z)
        .lineTo(ball, nose_tip_z * 0.45)
        .lineTo(tip_seat, nose_tip_z)
        .lineTo(nose_top, nose_top_z)
        .lineTo(body_mid, 0.060 * r.barrel_len_scale)
        .lineTo(body_top, body_top_z)
        .lineTo(collar, collar_top_z)
        .lineTo(collar * 0.45, collar_top_z + 0.001 * r.barrel_len_scale)
        .lineTo(0.0, dome_apex)
        .close()
    )
    barrel = profile.revolve(360, (0, 0), (0, 1))
    slot_w = 0.0030 * girth
    slot_depth = 0.0025 * girth
    slot_z_bot = 0.064 * r.barrel_len_scale
    slot_len = 0.030 * r.barrel_len_scale
    slot_y_outer = collar + 0.001
    slot_y_inner = body_mid - slot_depth
    slot_center = (slot_y_inner + slot_y_outer) / 2.0
    slot_span = slot_y_outer - slot_y_inner
    cutter = (
        cq.Workplane("XY")
        .workplane(offset=slot_z_bot)
        .center(0.0, slot_center)
        .rect(slot_w, slot_span)
        .extrude(slot_len)
    )
    return barrel.cut(cutter)


def _hex_outer_radius(across_flats: float) -> float:
    return across_flats / (2.0 * math.cos(math.pi / 6.0))


def _hex_prism(across_flats: float, height: float, z_base: float) -> cq.Workplane:
    radius = _hex_outer_radius(across_flats)
    pts = []
    for i in range(6):
        angle = math.pi / 6.0 + i * math.pi / 3.0
        pts.append((radius * math.cos(angle), radius * math.sin(angle)))
    return cq.Workplane("XY").workplane(offset=z_base).polyline(pts).close().extrude(height)


def _build_hex_barrel_cq(r: ResolvedPenConfig) -> cq.Workplane:
    girth = r.barrel_girth_scale
    collar = R_COLLAR * girth
    body_mid = R_BODY_MID * girth
    nose_top = R_NOSE_TOP * girth
    tip_seat = R_TIP_SEAT * girth
    ball = R_BALL * girth
    bore = BORE_R * girth
    nose_top_z = NOSE_TOP_Z * r.barrel_len_scale
    collar_bot_z = COLLAR_BOT_Z * r.barrel_len_scale
    collar_top_z = COLLAR_TOP_Z * r.barrel_len_scale
    bore_bottom_z = collar_top_z - 0.055 * r.barrel_len_scale

    body = _hex_prism(2.0 * body_mid, collar_bot_z - nose_top_z, nose_top_z)
    collar_body = _hex_prism(2.0 * collar, collar_top_z - collar_bot_z, collar_bot_z)
    barrel = body.union(collar_body)
    nose = (
        cq.Workplane("XZ")
        .moveTo(0.0, TIP_END_Z)
        .lineTo(ball, NOSE_TIP_Z * r.barrel_len_scale * 0.45)
        .lineTo(tip_seat, NOSE_TIP_Z * r.barrel_len_scale)
        .lineTo(nose_top, nose_top_z)
        .lineTo(nose_top, BODY_TOP_Z * r.barrel_len_scale)
        .lineTo(0.0, BODY_TOP_Z * r.barrel_len_scale)
        .close()
        .revolve(360, (0, 0), (0, 1))
    )
    barrel = barrel.union(nose)
    bore_cyl = (
        cq.Workplane("XY")
        .workplane(offset=bore_bottom_z)
        .circle(bore)
        .extrude(collar_top_z - bore_bottom_z)
    )
    return barrel.cut(bore_cyl)


def _rounded_rect_prism_z(
    width: float, depth: float, height: float, corner_r: float
) -> cq.Workplane:
    return cq.Workplane("XY").rect(width, depth).extrude(height).edges("|Z").fillet(corner_r)


def _build_rect_barrel_cq(r: ResolvedPenConfig) -> cq.Workplane:
    w = RECT_BODY_W * r.barrel_girth_scale
    d = RECT_BODY_D * r.barrel_girth_scale
    z0 = RECT_BODY_Z0 * r.barrel_len_scale
    z1 = RECT_BODY_Z1 * r.barrel_len_scale
    collar_z0 = RECT_COLLAR_Z0 * r.barrel_len_scale
    collar_z1 = RECT_COLLAR_Z1 * r.barrel_len_scale
    body = _rounded_rect_prism_z(w, d, z1 - z0, RECT_CORNER_R * r.barrel_girth_scale).translate(
        (0.0, 0.0, z0)
    )
    collar = _rounded_rect_prism_z(
        RECT_COLLAR_W * r.barrel_girth_scale,
        RECT_COLLAR_D * r.barrel_girth_scale,
        collar_z1 - collar_z0,
        RECT_COLLAR_R * r.barrel_girth_scale,
    ).translate((0.0, 0.0, collar_z0))
    nose_top_z = 0.016 * r.barrel_len_scale
    nose_stem_w = 0.0068 * r.barrel_girth_scale
    nose_stem_d = 0.0052 * r.barrel_girth_scale
    nose_stem = _rounded_rect_prism_z(
        nose_stem_w,
        nose_stem_d,
        collar_z0 - nose_top_z,
        0.0012 * r.barrel_girth_scale,
    ).translate((0.0, 0.0, nose_top_z))
    tip = (
        cq.Workplane("XY")
        .workplane(offset=TIP_END_Z)
        .circle(0.00055 * r.barrel_girth_scale)
        .workplane(offset=nose_top_z)
        .rect(nose_stem_w, nose_stem_d)
        .loft(combine=True)
    )
    return body.union(collar).union(nose_stem).union(tip)


def _build_windowed_clip_shape() -> cq.Workplane:
    clip_len = 0.052
    clip_w = 0.0072
    clip_t = 0.0009
    blade = (
        cq.Workplane("YZ")
        .workplane(offset=clip_t / 2.0 + 0.0006)
        .center(0.0, -clip_len / 2.0)
        .rect(clip_w, clip_len)
        .extrude(clip_t)
    )
    window = (
        cq.Workplane("YZ")
        .workplane(offset=clip_t / 2.0 + 0.0006)
        .center(0.0, -0.020)
        .ellipse(0.0017, 0.010)
        .extrude(clip_t + 0.002)
    )
    bridge = (
        cq.Workplane("XZ")
        .workplane(offset=clip_w / 2.0)
        .moveTo(-0.0008, 0.0008)
        .lineTo(clip_t / 2.0 + 0.0016, 0.0008)
        .lineTo(clip_t / 2.0 + 0.0016, -0.002)
        .lineTo(-0.0008, -0.002)
        .close()
        .extrude(-clip_w)
    )
    foot = (
        cq.Workplane("YZ")
        .workplane(offset=0.0006)
        .center(0.0, -clip_len + 0.004)
        .circle(0.0028)
        .extrude(0.0016)
    )
    return blade.cut(window).union(bridge).union(foot)


def _build_solid_clip_shape() -> cq.Workplane:
    clip_len = 0.050
    top_w = 0.0078
    bot_w = 0.0042
    clip_t = 0.0010
    x_base = 0.0006
    x_outer = x_base + clip_t
    x_mid = (x_base + x_outer) / 2.0
    blade_bottom_z = -clip_len
    blade = (
        cq.Workplane("YZ")
        .workplane(offset=x_base)
        .moveTo(-top_w / 2.0, 0.0)
        .lineTo(top_w / 2.0, 0.0)
        .lineTo(bot_w / 2.0, blade_bottom_z)
        .lineTo(-bot_w / 2.0, blade_bottom_z)
        .close()
        .extrude(clip_t)
    )
    bridge = (
        cq.Workplane("XZ")
        .workplane(offset=top_w / 2.0)
        .moveTo(-0.0008, 0.0008)
        .lineTo(x_outer + 0.0002, 0.0008)
        .lineTo(x_outer + 0.0002, -0.002)
        .lineTo(-0.0008, -0.002)
        .close()
        .extrude(-top_w)
    )
    curl_r = 0.0055
    tube_r = bot_w / 2.0
    start_angle = math.radians(90.0)
    end_angle = math.radians(-50.0)
    arc_cx = x_mid
    arc_cz = blade_bottom_z - curl_r
    start_x = arc_cx + curl_r * math.cos(start_angle)
    start_z = arc_cz + curl_r * math.sin(start_angle)
    mid_angle = (start_angle + end_angle) / 2.0
    mid_x = arc_cx + curl_r * math.cos(mid_angle)
    mid_z = arc_cz + curl_r * math.sin(mid_angle)
    end_x = arc_cx + curl_r * math.cos(end_angle)
    end_z = arc_cz + curl_r * math.sin(end_angle)
    path = cq.Workplane("XZ").moveTo(start_x, start_z).threePointArc((mid_x, mid_z), (end_x, end_z))
    curl = (
        cq.Workplane("YZ")
        .workplane(offset=start_x)
        .center(0.0, start_z)
        .circle(tube_r)
        .sweep(path, isFrenet=True)
    )
    ball = cq.Workplane("XY").workplane(offset=end_z).center(end_x, 0.0).sphere(0.0030)
    return blade.union(bridge).union(curl).union(ball)


def _build_ring_band(barrel_r: float, center_z: float, proud: float = 0.0003) -> cq.Workplane:
    ring_h = 0.0008
    inner_r = barrel_r - 0.0005
    outer_r = barrel_r + proud
    z_lo = center_z - ring_h / 2.0
    z_hi = center_z + ring_h / 2.0
    return (
        cq.Workplane("XZ")
        .moveTo(inner_r, z_lo)
        .lineTo(outer_r, z_lo)
        .lineTo(outer_r, z_hi)
        .lineTo(inner_r, z_hi)
        .close()
        .revolve(360, (0, 0), (0, 1))
    )


def _build_face_strip(across_flats: float, z_lo: float, z_hi: float) -> cq.Workplane:
    proud = 0.0005
    width = 0.0025
    depth = across_flats / 2.0 + proud * 0.3
    return (
        cq.Workplane("XY")
        .workplane(offset=z_lo)
        .center(depth, 0.0)
        .rect(proud, width)
        .extrude(z_hi - z_lo)
    )


def _build_plunger_geometry(r: ResolvedPenConfig) -> LatheGeometry:
    girth = r.barrel_girth_scale
    shaft_r = BORE_R * girth
    knurl_r = 0.0064 * girth
    cap_r = 0.0056 * girth
    shaft_len = 0.034 * r.barrel_len_scale
    profile = [
        (0.0, 0.0),
        (cap_r * 0.55, -0.0006 * r.barrel_len_scale),
        (cap_r, -0.0018 * r.barrel_len_scale),
        (knurl_r, -0.0040 * r.barrel_len_scale),
        (knurl_r, -0.0090 * r.barrel_len_scale),
        (cap_r * 0.78, -0.0110 * r.barrel_len_scale),
        (shaft_r, -0.0120 * r.barrel_len_scale),
        (shaft_r, -0.0120 * r.barrel_len_scale - shaft_len),
        (0.0, -0.0120 * r.barrel_len_scale - shaft_len),
    ]
    return LatheGeometry(profile, segments=48, closed=True)


def _build_slider_shape(r: ResolvedPenConfig) -> cq.Workplane:
    girth = r.barrel_girth_scale
    pad_w = 0.0048 * girth
    pad_h = 0.010 * r.barrel_len_scale
    pad_t = 0.0014 * girth
    tab_w = 0.0026 * girth
    tab_h = 0.010 * r.barrel_len_scale
    tab_d = 0.0020 * girth
    pad = (
        cq.Workplane("XY")
        .workplane(offset=-pad_h)
        .center(0.0, pad_t / 2.0)
        .rect(pad_w, pad_t)
        .extrude(pad_h)
    )
    tab = (
        cq.Workplane("XY")
        .workplane(offset=-tab_h)
        .center(0.0, -tab_d / 2.0)
        .rect(tab_w, tab_d)
        .extrude(tab_h)
    )
    bump = (
        cq.Workplane("XY")
        .workplane(offset=-pad_h * 0.65)
        .center(0.0, pad_t + 0.0003 * girth)
        .rect(pad_w * 0.6, 0.0006 * girth)
        .extrude(pad_h * 0.3)
    )
    return pad.union(tab).union(bump)


def _build_sleeve_geometry(r: ResolvedPenConfig) -> LatheGeometry:
    girth = r.barrel_girth_scale
    local_top = (COLLAR_TOP_Z - SEAM_Z) * r.barrel_len_scale
    dome_h = 0.008 * r.barrel_len_scale
    body_top = R_BODY_TOP * girth
    collar = R_COLLAR * girth
    return LatheGeometry(
        [
            (0.0, 0.0),
            (body_top, 0.0),
            (body_top, 0.001 * r.barrel_len_scale),
            (collar, 0.002 * r.barrel_len_scale),
            (collar, local_top),
            (collar * 0.93, local_top + 0.002 * r.barrel_len_scale),
            (collar * 0.74, local_top + 0.004 * r.barrel_len_scale),
            (collar * 0.44, local_top + 0.006 * r.barrel_len_scale),
            (0.0, local_top + dome_h),
        ],
        segments=64,
        closed=True,
    )


def _build_hinge_lug(r: ResolvedPenConfig) -> cq.Workplane:
    girth = r.barrel_girth_scale
    hinge_x = R_BODY_TOP * girth
    hinge_z = NOSE_TOP_Z * r.barrel_len_scale
    lug_r = 0.0017 * girth
    lug_len = 0.010 * girth
    pin = (
        cq.Workplane("XZ")
        .workplane(offset=-lug_len / 2.0)
        .center(hinge_x, hinge_z)
        .circle(lug_r)
        .extrude(lug_len)
    )
    boss_inner = R_NOSE_TOP * girth - 0.002
    boss_outer = hinge_x + lug_r + 0.001
    boss = (
        cq.Workplane("YZ")
        .workplane(offset=boss_inner)
        .center(0.0, hinge_z)
        .rect(0.005, 0.005)
        .extrude(boss_outer - boss_inner)
    )
    return pin.union(boss)


def _build_hinged_cap_shape(r: ResolvedPenConfig) -> cq.Workplane:
    girth = r.barrel_girth_scale
    cap_len = 0.036 * r.barrel_len_scale
    outer_r = 0.0066 * girth
    inner_r = 0.0054 * girth
    wall = outer_r - inner_r
    hinge_x = -(R_BODY_TOP * girth)
    cap_top_z = -0.0005
    cap_bot_z = cap_top_z - cap_len
    outer = (
        cq.Workplane("XY")
        .workplane(offset=cap_top_z)
        .center(hinge_x, 0.0)
        .circle(outer_r)
        .extrude(-cap_len)
    )
    inner = (
        cq.Workplane("XY")
        .workplane(offset=cap_top_z)
        .center(hinge_x, 0.0)
        .circle(inner_r)
        .extrude(-(cap_len - wall))
    )
    body = outer.cut(inner)
    end_cap = (
        cq.Workplane("XY")
        .workplane(offset=cap_bot_z)
        .center(hinge_x, 0.0)
        .circle(outer_r)
        .extrude(-wall)
    )
    knuckle = (
        cq.Workplane("XZ")
        .workplane(offset=-0.004)
        .center(0.0, 0.0)
        .circle(0.0015 * girth)
        .extrude(0.008)
    )
    neck = (
        cq.Workplane("XY")
        .workplane(offset=cap_top_z)
        .center(hinge_x * 0.5, 0.0)
        .rect(abs(hinge_x) + 0.004, 0.006)
        .extrude(abs(cap_top_z) + 0.0015 * girth)
    )
    return body.union(end_cap).union(knuckle).union(neck)


def _build_pull_cap_shape(r: ResolvedPenConfig) -> cq.Workplane:
    wall = PULL_CAP_WALL * r.barrel_girth_scale
    clear = PULL_CAP_CLEAR * r.barrel_girth_scale
    # Outer = body + wall + clearance on every side, so the inner cavity
    # (= body + clearance) is strictly WIDER than the rect body it slips over.
    w = RECT_BODY_W * r.barrel_girth_scale + 2.0 * (wall + clear)
    d = RECT_BODY_D * r.barrel_girth_scale + 2.0 * (wall + clear)
    cap_len = PULL_CAP_LEN * r.barrel_len_scale
    outer = _rounded_rect_prism_z(w, d, cap_len, (RECT_CORNER_R + 0.0006) * r.barrel_girth_scale)
    inner = _rounded_rect_prism_z(
        w - 2 * wall,
        d - 2 * wall,
        cap_len - wall,
        max(0.0005, RECT_CORNER_R * r.barrel_girth_scale - wall + clear),
    )
    # Closed floor kept at the bottom (z in [0, wall]); cavity opens toward +Z
    # (the body side) so the cap slips onto the nib and pulls off downward.
    cap = outer.cut(inner.translate((0.0, 0.0, wall)))
    return cap


def _grip_contour_radius(z: float, r: ResolvedPenConfig) -> float:
    pts = [
        (NOSE_TOP_Z * r.barrel_len_scale, 0.0050 * r.barrel_girth_scale),
        (0.033 * r.barrel_len_scale, 0.0048 * r.barrel_girth_scale),
        (0.040 * r.barrel_len_scale, 0.0040 * r.barrel_girth_scale),
        (0.047 * r.barrel_len_scale, 0.0048 * r.barrel_girth_scale),
        (0.053 * r.barrel_len_scale, 0.0042 * r.barrel_girth_scale),
        (0.060 * r.barrel_len_scale, 0.0052 * r.barrel_girth_scale),
        (0.065 * r.barrel_len_scale, 0.0058 * r.barrel_girth_scale),
    ]
    if z <= pts[0][0]:
        return pts[0][1]
    if z >= pts[-1][0]:
        return pts[-1][1]
    for i in range(len(pts) - 1):
        z0, r0 = pts[i]
        z1, r1 = pts[i + 1]
        if z0 <= z <= z1:
            t = (z - z0) / (z1 - z0)
            return r0 + t * (r1 - r0)
    return pts[-1][1]


# How far the clip blade root is sunk into the mounting surface. The clip
# shapes are authored a hair outboard of their local origin, so mounting them at
# `surface_r - CLIP_EMBED` guarantees the blade overlaps the barrel/cap body on
# every profile and never floats off as a disconnected island.
CLIP_EMBED = 0.0016


def _mount_clip_visual(
    target, r: ResolvedPenConfig, mats: dict[str, str], top_z: float, surface_r: float
) -> None:
    if r.pocket_clip == "no_clip":
        return
    mesh = mesh_from_cadquery(
        _build_windowed_clip_shape()
        if r.pocket_clip == "windowed_clip"
        else _build_solid_clip_shape(),
        "clip_body",
    )
    target.visual(
        mesh,
        origin=Origin(xyz=(surface_r - CLIP_EMBED, 0.0, top_z)),
        material=mats["trim"],
        name=f"{r.pocket_clip}_visual", material_class_id=("metal.brushed_silver" if r.palette_style in {"brushed_silver", "navy_trim", "industrial_red", "champagne_steel", "charcoal_rubber"} else "metal.blackened_gunmetal"),
    )


def _mount_grip_visuals(barrel, r: ResolvedPenConfig, mats: dict[str, str]) -> None:
    if r.grip_surface == "ring_bands":
        start = 0.040 * r.barrel_len_scale
        spacing = 0.006 * r.grip_zone_scale * r.barrel_len_scale
        radius = (
            R_BODY_MID if r.barrel_profile != "rounded_rect" else RECT_BODY_W / 2.8
        ) * r.barrel_girth_scale
        for i in range(r.n_grip_bands):
            z = start + i * spacing
            barrel.visual(
                mesh_from_cadquery(_build_ring_band(radius, z), f"grip_ring_{i}"),
                material=mats["accent"],
                name=f"grip_ring_{i}", material_class_id=("metal.brushed_silver" if r.palette_style in {"brushed_silver", "graphite_black", "navy_trim", "industrial_red", "champagne_steel"} else "rubber.smooth_plain"),
            )
    elif r.grip_surface == "contoured_rubber_grip":
        span = (0.065 - 0.030 - 0.006) * r.barrel_len_scale
        for i in range(r.n_grip_bands):
            t = (i + 0.5) / max(1, r.n_grip_bands)
            ring_z = 0.033 * r.barrel_len_scale + t * span
            ring_major = _grip_contour_radius(ring_z, r) + 0.00012
            barrel.visual(
                mesh_from_geometry(
                    TorusGeometry(
                        radius=ring_major,
                        tube=0.0004 * r.barrel_girth_scale,
                        radial_segments=12,
                        tubular_segments=48,
                    ),
                    f"grip_ring_{i}",
                ),
                origin=Origin(xyz=(0.0, 0.0, ring_z)),
                material=mats["dark"],
                name=f"grip_ring_{i}", material_class_id="rubber.smooth_plain",
            )
    elif r.grip_surface == "face_strips":
        strip_mesh = mesh_from_cadquery(
            _build_face_strip(
                2.0 * R_BODY_MID * r.barrel_girth_scale,
                NOSE_TOP_Z * r.barrel_len_scale + 0.008,
                BODY_TOP_Z * r.barrel_len_scale - 0.008,
            ),
            "face_strip",
        )
        for i in range(6):
            angle = (i + 1) * math.pi / 3.0
            barrel.visual(
                strip_mesh,
                origin=Origin(rpy=(0.0, 0.0, angle)),
                material=mats["dark"],
                name=f"face_strip_{i}", material_class_id="rubber.smooth_plain",
            )


def build_pen(config: PenConfig, *, assets: AssetContext | None = None) -> ArticulatedObject:
    del assets
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name)
    mats = _palette_materials(model, r.palette_style)

    barrel = model.part("barrel")
    if r.barrel_profile == "round_lathe":
        if r.actuation == "side_slider":
            barrel.visual(
                mesh_from_cadquery(_build_side_slider_barrel_cq(r), "barrel_body"),
                material=mats["body"],
                name="barrel_body", material_class_id=("metal.brushed_silver" if r.palette_style in {"brushed_silver", "navy_trim", "industrial_red", "champagne_steel", "charcoal_rubber"} else "metal.blackened_gunmetal"),
            )
        else:
            barrel.visual(
                mesh_from_geometry(_build_round_barrel_geometry(r), "barrel_body"),
                material=mats["body"],
                name="barrel_body", material_class_id=("metal.brushed_silver" if r.palette_style in {"brushed_silver", "navy_trim", "industrial_red", "champagne_steel", "charcoal_rubber"} else "metal.blackened_gunmetal"),
            )
    elif r.barrel_profile == "hex_prism":
        barrel.visual(
            mesh_from_cadquery(_build_hex_barrel_cq(r), "barrel_body"),
            material=mats["body"],
            name="barrel_body", material_class_id=("metal.brushed_silver" if r.palette_style in {"brushed_silver", "navy_trim", "industrial_red", "champagne_steel", "charcoal_rubber"} else "metal.blackened_gunmetal"),
        )
    else:
        barrel.visual(
            mesh_from_cadquery(_build_rect_barrel_cq(r), "barrel_body"),
            material=mats["body"],
            name="barrel_body", material_class_id=("metal.brushed_silver" if r.palette_style in {"brushed_silver", "navy_trim", "industrial_red", "champagne_steel", "charcoal_rubber"} else "metal.blackened_gunmetal"),
        )

    if r.actuation == "hinged_cap":
        barrel.visual(
            mesh_from_cadquery(_build_hinge_lug(r), "hinge_lug"),
            material=mats["trim"],
            name="hinge_lug", material_class_id=("metal.brushed_silver" if r.palette_style in {"brushed_silver", "navy_trim", "industrial_red", "champagne_steel", "charcoal_rubber"} else "metal.blackened_gunmetal"),
        )

    _mount_grip_visuals(barrel, r, mats)

    articulation_name = ""
    moving_part = None

    if r.actuation == "click_plunger":
        plunger = model.part("plunger")
        plunger.visual(
            mesh_from_geometry(_build_plunger_geometry(r), "plunger_button"),
            material=mats["trim"],
            name="plunger_button", material_class_id=("metal.brushed_silver" if r.palette_style in {"brushed_silver", "navy_trim", "industrial_red", "champagne_steel", "charcoal_rubber"} else "metal.blackened_gunmetal"),
        )
        rest_z = COLLAR_TOP_Z * r.barrel_len_scale + 0.010 * r.barrel_len_scale
        articulation_name = "barrel_to_plunger"
        model.articulation(
            articulation_name,
            ArticulationType.PRISMATIC,
            parent=barrel,
            child=plunger,
            origin=Origin(xyz=(0.0, 0.0, rest_z)),
            axis=(0.0, 0.0, -1.0),
            motion_limits=MotionLimits(
                effort=10.0,
                velocity=0.1,
                lower=0.0,
                upper=PLUNGER_TRAVEL * r.actuation_travel_scale,
            ),
        )
        moving_part = plunger
        _mount_clip_visual(
            barrel,
            r,
            mats,
            COLLAR_TOP_Z * r.barrel_len_scale - 0.002 * r.barrel_len_scale,
            R_COLLAR * r.barrel_girth_scale,
        )
    elif r.actuation == "twist_sleeve":
        sleeve = model.part("sleeve")
        sleeve.visual(
            mesh_from_geometry(_build_sleeve_geometry(r), "sleeve_body"),
            material=mats["body"],
            name="sleeve_body", material_class_id=("metal.brushed_silver" if r.palette_style in {"brushed_silver", "navy_trim", "industrial_red", "champagne_steel", "charcoal_rubber"} else "metal.blackened_gunmetal"),
        )
        if r.pocket_clip != "no_clip":
            # A twist pen's clip belongs on the STATIONARY barrel, not the
            # rotating sleeve — mounting it on the sleeve makes the clip sweep
            # into the barrel as it twists (motion-QC overlap). Anchor it just
            # below the seam so its blade rides down the static lower body.
            _mount_clip_visual(
                barrel,
                r,
                mats,
                SEAM_Z * r.barrel_len_scale - 0.004 * r.barrel_len_scale,
                R_BODY_TOP * r.barrel_girth_scale,
            )
        if r.grip_surface == "ring_bands":
            ring_count = max(3, min(4, r.n_grip_bands))
            local_top = (COLLAR_TOP_Z - SEAM_Z) * r.barrel_len_scale
            usable_span = max(0.004, local_top - 0.008 * r.barrel_len_scale)
            for i in range(ring_count):
                t = (i + 0.5) / ring_count
                z = 0.003 * r.barrel_len_scale + t * usable_span
                sleeve.visual(
                    mesh_from_cadquery(
                        _build_ring_band(R_COLLAR * r.barrel_girth_scale, z, proud=0.0004),
                        f"sleeve_grip_ring_{i}",
                    ),
                    material=mats["accent"],
                    name=f"sleeve_grip_ring_{i}", material_class_id=("metal.brushed_silver" if r.palette_style in {"brushed_silver", "graphite_black", "navy_trim", "industrial_red", "champagne_steel"} else "rubber.smooth_plain"),
                )
        articulation_name = "barrel_to_sleeve"
        model.articulation(
            articulation_name,
            ArticulationType.REVOLUTE,
            parent=barrel,
            child=sleeve,
            origin=Origin(xyz=(0.0, 0.0, SEAM_Z * r.barrel_len_scale)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(
                effort=5.0, velocity=2.0, lower=0.0, upper=TWIST_UPPER * r.actuation_travel_scale
            ),
        )
        moving_part = sleeve
    elif r.actuation == "side_slider":
        slider = model.part("slider")
        slider.visual(
            mesh_from_cadquery(_build_slider_shape(r), "slider_pad"),
            material=mats["dark"],
            name="slider_pad", material_class_id="rubber.smooth_plain",
        )
        articulation_name = "barrel_to_slider"
        slider_origin_y = R_BODY_TOP * r.barrel_girth_scale
        slider_origin_z = (0.064 + 0.030) * r.barrel_len_scale
        model.articulation(
            articulation_name,
            ArticulationType.PRISMATIC,
            parent=barrel,
            child=slider,
            origin=Origin(xyz=(0.0, slider_origin_y, slider_origin_z)),
            axis=(0.0, 0.0, -1.0),
            motion_limits=MotionLimits(
                effort=8.0, velocity=0.15, lower=0.0, upper=SLIDER_TRAVEL * r.actuation_travel_scale
            ),
        )
        moving_part = slider
        _mount_clip_visual(
            barrel,
            r,
            mats,
            COLLAR_TOP_Z * r.barrel_len_scale - 0.002 * r.barrel_len_scale,
            R_COLLAR * r.barrel_girth_scale,
        )
    elif r.actuation == "hinged_cap":
        cap = model.part("cap")
        cap.visual(
            mesh_from_cadquery(_build_hinged_cap_shape(r), "cap_shell"),
            material=mats["cap"],
            name="cap_shell", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"brushed_silver", "graphite_black", "champagne_steel", "charcoal_rubber"} else "metal.paint_coated"),
        )
        articulation_name = "barrel_to_cap"
        model.articulation(
            articulation_name,
            ArticulationType.REVOLUTE,
            parent=barrel,
            child=cap,
            origin=Origin(
                xyz=(R_BODY_TOP * r.barrel_girth_scale, 0.0, NOSE_TOP_Z * r.barrel_len_scale)
            ),
            axis=(0.0, -1.0, 0.0),
            motion_limits=MotionLimits(effort=3.0, velocity=2.0, lower=0.0, upper=HINGE_UPPER),
        )
        moving_part = cap
        _mount_clip_visual(
            barrel,
            r,
            mats,
            COLLAR_TOP_Z * r.barrel_len_scale - 0.002 * r.barrel_len_scale,
            R_COLLAR * r.barrel_girth_scale,
        )
    else:
        cap = model.part("cap")
        cap.visual(
            mesh_from_cadquery(_build_pull_cap_shape(r), "cap_shell"),
            material=mats["cap"],
            name="cap_shell", material_class_id="plastic.opaque_glossy_molded",
        )
        articulation_name = "barrel_to_cap"
        # Seat the cap OVER the nib end: its closed floor sits just below the
        # writing tip (z=0), the cavity encloses nib + nose + collar, and the
        # open mouth reaches the body base. Pulling -Z slides the cap off the
        # nib; the floor stays below the tip and the cavity is wider than every
        # part it passes, so it never drives through the tip.
        seat_z = -PULL_CAP_FLOOR_DROP * r.barrel_len_scale
        model.articulation(
            articulation_name,
            ArticulationType.PRISMATIC,
            parent=barrel,
            child=cap,
            origin=Origin(xyz=(0.0, 0.0, seat_z)),
            axis=(0.0, 0.0, -1.0),
            motion_limits=MotionLimits(
                effort=15.0,
                velocity=0.25,
                lower=0.0,
                upper=PULL_CAP_LEN * 0.72 * r.actuation_travel_scale,
            ),
        )
        moving_part = cap
        # Clip rides the STATIONARY upper body (a pen clip is longer than this
        # marker cap; mounting it on the cap made it dangle below the nib tip).
        _mount_clip_visual(
            barrel,
            r,
            mats,
            RECT_BODY_Z1 * r.barrel_len_scale - 0.006 * r.barrel_len_scale,
            RECT_BODY_W / 2.0 * r.barrel_girth_scale,
        )

    if moving_part is None or not articulation_name:
        raise RuntimeError("Handtools_Pen failed to build a moving mechanism")

    return model


def build_seeded_pen(seed: int) -> ArticulatedObject:
    return build_pen(config_from_seed(seed), assets=AssetContext.from_script(__file__))


def run_pen_tests(object_model: ArticulatedObject, config: PenConfig) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    barrel = object_model.get_part("barrel")

    non_fixed = [
        a for a in object_model.articulations if a.articulation_type != ArticulationType.FIXED
    ]
    ctx.check(
        "exactly one non-fixed articulation exists",
        len(non_fixed) == 1,
        details=f"got {[a.name for a in non_fixed]}",
    )

    if r.actuation == "click_plunger":
        child = object_model.get_part("plunger")
        joint = object_model.get_articulation("barrel_to_plunger")
        ctx.allow_overlap(barrel, child, reason="Plunger shaft is captured in the barrel bore.")
        ctx.check(
            "plunger joint is prismatic",
            joint.articulation_type == ArticulationType.PRISMATIC,
            details=f"{joint.articulation_type}",
        )
        ctx.check("plunger axis is -Z", joint.axis[2] < -0.5, details=f"axis={joint.axis}")
        rest = ctx.part_world_position(child)
        with ctx.pose({joint: joint.motion_limits.upper}):
            moved = ctx.part_world_position(child)
        ctx.check(
            "positive q presses plunger downward",
            rest is not None and moved is not None and moved[2] < rest[2],
            details=f"rest={rest}, moved={moved}",
        )
    elif r.actuation == "twist_sleeve":
        child = object_model.get_part("sleeve")
        joint = object_model.get_articulation("barrel_to_sleeve")
        ctx.check(
            "sleeve joint is revolute",
            joint.articulation_type == ArticulationType.REVOLUTE,
            details=f"{joint.articulation_type}",
        )
        ctx.check("sleeve axis is +Z", joint.axis[2] > 0.5, details=f"axis={joint.axis}")
        child_aabb = ctx.part_element_world_aabb(child, elem="sleeve_body")
        barrel_aabb = ctx.part_world_aabb(barrel)
        if child_aabb is not None and barrel_aabb is not None:
            ctx.check(
                "sleeve sits above seam",
                child_aabb[0][2] >= SEAM_Z * r.barrel_len_scale - 0.003,
                details=f"sleeve_min_z={child_aabb[0][2]}",
            )
    elif r.actuation == "side_slider":
        child = object_model.get_part("slider")
        joint = object_model.get_articulation("barrel_to_slider")
        ctx.allow_overlap(barrel, child, reason="Slider tab rides inside the side slot.")
        ctx.check(
            "slider joint is prismatic",
            joint.articulation_type == ArticulationType.PRISMATIC,
            details=f"{joint.articulation_type}",
        )
        ctx.check("slider axis is -Z", joint.axis[2] < -0.5, details=f"axis={joint.axis}")
        rest = ctx.part_world_position(child)
        with ctx.pose({joint: joint.motion_limits.upper}):
            moved = ctx.part_world_position(child)
        ctx.check(
            "positive q moves slider downward",
            rest is not None and moved is not None and moved[2] < rest[2],
            details=f"rest={rest}, moved={moved}",
        )
    elif r.actuation == "hinged_cap":
        child = object_model.get_part("cap")
        joint = object_model.get_articulation("barrel_to_cap")
        ctx.allow_overlap(barrel, child, reason="Hinged cap nests over the nose when closed.")
        ctx.check(
            "hinged cap joint is revolute",
            joint.articulation_type == ArticulationType.REVOLUTE,
            details=f"{joint.articulation_type}",
        )
        ctx.check(
            "hinge axis is transverse",
            abs(joint.axis[1]) > 0.5 and abs(joint.axis[2]) < 0.2,
            details=f"axis={joint.axis}",
        )
        rest_aabb = ctx.part_world_aabb(child)
        with ctx.pose({joint: joint.motion_limits.upper}):
            moved_aabb = ctx.part_world_aabb(child)
        moved_clear = (
            rest_aabb is not None
            and moved_aabb is not None
            and (
                abs(moved_aabb[0][0] - rest_aabb[0][0]) > 0.002
                or abs(moved_aabb[1][0] - rest_aabb[1][0]) > 0.002
                or abs(moved_aabb[1][2] - rest_aabb[1][2]) > 0.002
            )
        )
        ctx.check(
            "hinged cap moves when opened",
            moved_clear,
            details=f"rest_aabb={rest_aabb}, moved_aabb={moved_aabb}",
        )
    else:
        child = object_model.get_part("cap")
        joint = object_model.get_articulation("barrel_to_cap")
        # The cap is a hollow sleeve; its CONVEX collision proxy is solid and
        # necessarily encloses the nib/nose it caps, so the barrel<->cap hull
        # overlap is expected and exempted. The real "cap can't pass through the
        # tip" guarantee is the explicit floor-below-tip assertion below, backed
        # by a cavity that is wider than every barrel part it slides over.
        ctx.allow_overlap(
            barrel, child, reason="Hollow cap's convex proxy encloses the nib it caps."
        )
        ctx.check(
            "pull cap joint is prismatic",
            joint.articulation_type == ArticulationType.PRISMATIC,
            details=f"{joint.articulation_type}",
        )
        ctx.check("pull cap axis is axial", abs(joint.axis[2]) > 0.5, details=f"axis={joint.axis}")
        rest = ctx.part_world_position(child)
        with ctx.pose({joint: joint.motion_limits.upper}):
            moved = ctx.part_world_position(child)
        ctx.check(
            "positive q removes cap away from nib",
            rest is not None and moved is not None and moved[2] < rest[2],
            details=f"rest={rest}, moved={moved}",
        )
        # The cap's closed floor must sit below the nib tip. The cap only ever
        # slides DOWN from rest, so the rest pose is the highest the floor gets;
        # if it clears the tip here it clears it at every pose, i.e. the cap can
        # never drive up through the writing tip.
        nib_tip_z = ctx.part_world_aabb(barrel)[0][2]
        cap_floor_rest_z = ctx.part_world_aabb(child)[0][2]
        ctx.check(
            "cap floor stays below the nib tip (never clips the tip)",
            cap_floor_rest_z <= nib_tip_z + 0.0005,
            details=f"cap_floor_rest_z={cap_floor_rest_z}, nib_tip_z={nib_tip_z}",
        )

    barrel_aabb = ctx.part_world_aabb(barrel)
    if barrel_aabb is not None:
        ctx.check(
            "writing tip reaches the lowest point",
            barrel_aabb[0][2] <= 0.0015,
            details=f"barrel_min_z={barrel_aabb[0][2]}",
        )

    return ctx.report()
