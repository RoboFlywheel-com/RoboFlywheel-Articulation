# SPDX-License-Identifier: Apache-2.0

"""Commercial front-load steel DUMPSTER (garbage_bin) modular template.

garbage_bin = a floor-standing, truck-liftable commercial front-load steel
dumpster / bin (NOT a household wheelie bin or street trashcan). Core identity
(spec ``articraft_template_authoring/specs_modular_v1/Urban_Environment_Garbage_bin.md`` §核心身份):

  (a) a steel rectangular corrugated dumpster body (tapered or upright),
  (b) a REVOLUTE rear-hinged steel lid as the defining main joint, and
  (c) at least one truck-lift interface (fork pockets / trunnion / lift bar).

Structure (pattern = ``parallel_children``): a single root ``body`` chassis part
holds four named slot axes as parallel children / inline visuals:

  * ``body_profile`` (Slot B, 2): sloped_front_load_tapered / rectangular_upright
    — the body shell + ribs + rim (all inline body visuals on the root).
  * ``lid_closure`` (Slot A, 5): the main mechanism. rear_hinged_slat_lid /
    lid_slat_count / twin_split_lids (2 mirrored half lids) / domed_flat_lid /
    slot_top_lid (fixed deck + inward-swing flap). All but slot_top hinge a full
    REVOLUTE lid about -Y at the rear-top edge; slot_top hinges a flap about +Y.
  * ``mobility`` (Slot C, 3): fixed_corner_feet (inline feet, 0 wheels) /
    four_caster_mobile (4 CONTINUOUS roll wheels) / two_caster_tilt (2 front
    CONTINUOUS roll wheels + 2 rear fixed feet).
  * ``lift_interface`` (Slot D, 2): fork_pockets_plus_side_trunnions (inline
    pockets) / continuous_trunnion_lift_bar (inline lift bars + cradle brackets).

Multiplicity axes (each loop-emitted): lid_slats (``lid_slat_count``),
lid_count (twin), caster_count (mobility), lift_bracket_count (lift bar).

Joint policy (3 HARD RULES): the only real joints are the lid hinge (REVOLUTE)
and the caster wheels (CONTINUOUS); feet / pockets / trunnions / lift bar /
ribs / rim are inline body visuals (Rule 1 — decorations are parent.visual, no
FIXED-joint parts). Every non-FIXED joint declares a MatingContract pinning real
visuals on both sides. Coordinate convention: +Z up, feet at z=0, front=+X,
rear=-X, centerline y=0, ``WALL_TOP_Z = FOOT_H + BODY_H`` is the rim plane.
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
    Box,
    Cylinder,
    Inertial,
    MatingContract,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
)

__modular__ = True

LidClosure = Literal[
    "rear_hinged_slat_lid",
    "lid_slat_count",
    "twin_split_lids",
    "domed_flat_lid",
    "slot_top_lid",
]
BodyProfile = Literal["sloped_front_load_tapered", "rectangular_upright"]
Mobility = Literal["fixed_corner_feet", "four_caster_mobile", "two_caster_tilt"]
LiftInterface = Literal[
    "fork_pockets_plus_side_trunnions", "continuous_trunnion_lift_bar"
]
PaletteStyle = Literal[
    "weathered_green",
    "municipal_blue",
    "rust_brown",
    "galvanized_steel",
    "hazard_red",
    "charcoal_black",
]

LID_CLOSURES: tuple[LidClosure, ...] = (
    "rear_hinged_slat_lid",
    "lid_slat_count",
    "twin_split_lids",
    "domed_flat_lid",
    "slot_top_lid",
)
BODY_PROFILES: tuple[BodyProfile, ...] = (
    "sloped_front_load_tapered",
    "rectangular_upright",
)
MOBILITIES: tuple[Mobility, ...] = (
    "fixed_corner_feet",
    "four_caster_mobile",
    "two_caster_tilt",
)
LIFT_INTERFACES: tuple[LiftInterface, ...] = (
    "fork_pockets_plus_side_trunnions",
    "continuous_trunnion_lift_bar",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "weathered_green",
    "municipal_blue",
    "rust_brown",
    "galvanized_steel",
    "hazard_red",
    "charcoal_black",
)

# Lid closures that carry the slat-multiplicity axis.
SLAT_LID_CLOSURES: tuple[LidClosure, ...] = (
    "rear_hinged_slat_lid",
    "lid_slat_count",
    "twin_split_lids",
)

SLAT_MIN, SLAT_MAX = 4, 16
SLAT_WEIGHTS_RANGE = tuple(range(SLAT_MIN, SLAT_MAX + 1))
# Mid-band (8-12) high-frequency, endpoints rare (spec §轴1).
SLAT_WEIGHTS = (1, 2, 4, 7, 9, 9, 9, 7, 4, 2, 2, 1, 1)  # len == 13

BRACKET_MIN, BRACKET_MAX = 2, 4
BRACKET_WEIGHTS = (7, 2, 1)  # 2 high-freq, 3-4 rare

PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "weathered_green": {
        "body": (0.16, 0.34, 0.22, 1.0),
        "lid": (0.13, 0.29, 0.19, 1.0),
        "steel": (0.42, 0.43, 0.40, 1.0),
        "dark": (0.08, 0.09, 0.08, 1.0),
        "rubber": (0.06, 0.06, 0.07, 1.0),
    },
    "municipal_blue": {
        "body": (0.13, 0.27, 0.45, 1.0),
        "lid": (0.10, 0.22, 0.38, 1.0),
        "steel": (0.48, 0.50, 0.53, 1.0),
        "dark": (0.07, 0.09, 0.12, 1.0),
        "rubber": (0.06, 0.06, 0.07, 1.0),
    },
    "rust_brown": {
        "body": (0.40, 0.24, 0.15, 1.0),
        "lid": (0.34, 0.20, 0.12, 1.0),
        "steel": (0.45, 0.38, 0.32, 1.0),
        "dark": (0.14, 0.09, 0.06, 1.0),
        "rubber": (0.06, 0.06, 0.07, 1.0),
    },
    "galvanized_steel": {
        "body": (0.60, 0.62, 0.64, 1.0),
        "lid": (0.55, 0.57, 0.59, 1.0),
        "steel": (0.70, 0.72, 0.74, 1.0),
        "dark": (0.22, 0.23, 0.24, 1.0),
        "rubber": (0.07, 0.07, 0.08, 1.0),
    },
    "hazard_red": {
        "body": (0.55, 0.13, 0.11, 1.0),
        "lid": (0.46, 0.10, 0.09, 1.0),
        "steel": (0.46, 0.45, 0.44, 1.0),
        "dark": (0.16, 0.05, 0.05, 1.0),
        "rubber": (0.06, 0.06, 0.07, 1.0),
    },
    "charcoal_black": {
        "body": (0.14, 0.15, 0.16, 1.0),
        "lid": (0.10, 0.11, 0.12, 1.0),
        "steel": (0.40, 0.41, 0.43, 1.0),
        "dark": (0.04, 0.04, 0.05, 1.0),
        "rubber": (0.06, 0.06, 0.07, 1.0),
    },
}

# ---------------------------------------------------------------------------
# Base real-world dimensions (meters). Commercial ~2-4 cubic yard dumpster.
# Long axis (width) along Y, depth (truck-approach) along X, height along Z.
# feet at z=0; lid rear-hinges on the -X top edge.
# ---------------------------------------------------------------------------
_BODY_W = 1.80  # width (Y span) of the body at the rim
_BODY_D_BOT = 1.02  # bottom depth (X span)
_BODY_H = 1.16  # wall height (z from FOOT_H to WALL_TOP_Z)
_WALL_T = 0.020
_FOOT_H = 0.10
_FOOT_SIZE = 0.12
_RIM_T = 0.030  # rim bar cross-section
_LID_OVER = 0.030  # lid overhang past the rear edge to the hinge line
_LID_THK = 0.030  # lid skin / slat thickness band
_HANDLE_R = 0.018
_WHEEL_R = 0.075
_WHEEL_W = 0.05
_FORK_PLATE = 0.10  # caster mounting-plate / fork height drop

_LID_OPEN = math.radians(105.0)
_FLAP_OPEN = math.radians(85.0)


@dataclass(frozen=True)
class GarbageBinConfig:
    lid_closure: LidClosure | None = None
    body_profile: BodyProfile | None = None
    mobility: Mobility | None = None
    lift_interface: LiftInterface | None = None
    palette_style: PaletteStyle = "weathered_green"
    lid_slat_count: int | None = None
    lift_bracket_count: int | None = None
    rib_count_side: int = 9
    rib_count_end: int = 5
    body_width_scale: float = 1.0
    body_height_scale: float = 1.0
    body_depth_scale: float = 1.0
    taper_ratio: float = 1.16
    lid_open_upper: float = _LID_OPEN
    name: str = "garbage_bin"


@dataclass(frozen=True)
class ResolvedGarbageBinConfig:
    lid_closure: LidClosure
    body_profile: BodyProfile
    mobility: Mobility
    lift_interface: LiftInterface
    palette_style: PaletteStyle
    lid_slat_count: int
    lid_count: int
    caster_count: int
    lift_bracket_count: int
    rib_count_side: int
    rib_count_end: int
    # Concrete geometry.
    body_w: float  # width (Y)
    body_d_bot: float  # bottom depth (X)
    body_d_top: float  # top depth (X), >= bottom for tapered
    body_h: float  # wall height
    wall_t: float
    foot_h: float
    wall_top_z: float  # = foot_h + body_h
    lid_open: float
    flap_open: float
    name: str

    @property
    def palette(self) -> dict[str, tuple[float, float, float, float]]:
        return PALETTES[self.palette_style]


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


def config_from_seed(seed: int) -> GarbageBinConfig:
    rng = random.Random(seed)
    return GarbageBinConfig(
        lid_closure=rng.choice(LID_CLOSURES),
        body_profile=rng.choice(BODY_PROFILES),
        mobility=rng.choice(MOBILITIES),
        lift_interface=rng.choice(LIFT_INTERFACES),
        palette_style=rng.choice(PALETTE_STYLES),
        lid_slat_count=rng.choices(SLAT_WEIGHTS_RANGE, weights=SLAT_WEIGHTS, k=1)[0],
        lift_bracket_count=rng.choices((2, 3, 4), weights=BRACKET_WEIGHTS, k=1)[0],
        rib_count_side=rng.randint(6, 12),
        rib_count_end=rng.randint(3, 7),
        body_width_scale=round(rng.uniform(0.85, 1.20), 4),
        body_height_scale=round(rng.uniform(0.85, 1.25), 4),
        body_depth_scale=round(rng.uniform(0.85, 1.20), 4),
        taper_ratio=round(rng.uniform(1.10, 1.22), 4),
        lid_open_upper=round(rng.uniform(math.radians(90), math.radians(110)), 4),
        name=f"seeded_garbage_bin_{seed}",
    )


def resolve_config(
    config: GarbageBinConfig | None = None,
) -> ResolvedGarbageBinConfig:
    cfg = config or GarbageBinConfig()
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)
    lid_closure = _pick(cfg.lid_closure, LID_CLOSURES)
    body_profile = _pick(cfg.body_profile, BODY_PROFILES)
    mobility = _pick(cfg.mobility, MOBILITIES)
    lift_interface = _pick(cfg.lift_interface, LIFT_INTERFACES)

    # --- Conditional multiplicity gating (spec §Multiplicity). ---
    # lid_count = 2 only for twin_split_lids.
    lid_count = 2 if lid_closure == "twin_split_lids" else 1

    # slat count valid only for slat lids; clamp into range.
    slat = cfg.lid_slat_count if cfg.lid_slat_count is not None else 11
    slat = int(_clamp(slat, SLAT_MIN, SLAT_MAX))
    if lid_closure not in SLAT_LID_CLOSURES:
        slat = 0  # domed / slot_top expose no slat axis

    # caster count is decided by mobility enum.
    caster_count = {
        "fixed_corner_feet": 0,
        "four_caster_mobile": 4,
        "two_caster_tilt": 2,
    }[mobility]

    # lift bracket count valid only for the continuous lift bar.
    bracket = cfg.lift_bracket_count if cfg.lift_bracket_count is not None else 2
    bracket = int(_clamp(bracket, BRACKET_MIN, BRACKET_MAX))
    if lift_interface != "continuous_trunnion_lift_bar":
        bracket = 0

    rib_side = int(_clamp(cfg.rib_count_side, 6, 12))
    rib_end = int(_clamp(cfg.rib_count_end, 3, 7))

    width_scale = _clamp(cfg.body_width_scale, 0.85, 1.20)
    height_scale = _clamp(cfg.body_height_scale, 0.85, 1.25)
    depth_scale = _clamp(cfg.body_depth_scale, 0.85, 1.20)

    body_w = _BODY_W * width_scale
    body_d_bot = _BODY_D_BOT * depth_scale
    body_h = _BODY_H * height_scale

    if body_profile == "sloped_front_load_tapered":
        taper = _clamp(cfg.taper_ratio, 1.10, 1.22)
    else:
        taper = 1.0
    body_d_top = body_d_bot * taper

    # Caster modes lift the chassis so the body floor clears the wheel tops
    # (wheel top = 2*WHEEL_R); feet mode uses the short fixed-foot height.
    if caster_count > 0:
        foot_h = 2.0 * _WHEEL_R + 0.012
    else:
        foot_h = _FOOT_H
    wall_top_z = foot_h + body_h

    lid_open = _clamp(cfg.lid_open_upper, math.radians(90), math.radians(110))

    return ResolvedGarbageBinConfig(
        lid_closure=lid_closure,
        body_profile=body_profile,
        mobility=mobility,
        lift_interface=lift_interface,
        palette_style=palette_style,
        lid_slat_count=slat,
        lid_count=lid_count,
        caster_count=caster_count,
        lift_bracket_count=bracket,
        rib_count_side=rib_side,
        rib_count_end=rib_end,
        body_w=body_w,
        body_d_bot=body_d_bot,
        body_d_top=body_d_top,
        body_h=body_h,
        wall_t=_WALL_T,
        foot_h=foot_h,
        wall_top_z=wall_top_z,
        lid_open=lid_open,
        flap_open=_FLAP_OPEN,
        name=cfg.name or "garbage_bin",
    )


def with_overrides(config: GarbageBinConfig, **kwargs: object) -> GarbageBinConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: GarbageBinConfig | ResolvedGarbageBinConfig,
) -> tuple[tuple[str, str], ...]:
    r = (
        config
        if isinstance(config, ResolvedGarbageBinConfig)
        else resolve_config(config)
    )
    choices = [
        ("lid_closure", r.lid_closure),
        ("body_profile", r.body_profile),
        ("mobility", r.mobility),
        ("lift_interface", r.lift_interface),
    ]
    # Multiplicity axes encoded as topology-distinguishing choices.
    if r.lid_closure in SLAT_LID_CLOSURES:
        choices.append(("lid_slats", f"n{r.lid_slat_count}"))
    if r.lid_count == 2:
        choices.append(("lid_count", "n2"))
    choices.append(("caster_count", f"n{r.caster_count}"))
    if r.lift_interface == "continuous_trunnion_lift_bar":
        choices.append(("lift_brackets", f"n{r.lift_bracket_count}"))
    return tuple(choices)


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Body chassis (root). Slot B body_profile + ribs + rim + Slot C/D inline
# visuals. All inline visuals (Rule 1).
# ---------------------------------------------------------------------------
def _depth_at_z(r: ResolvedGarbageBinConfig, z: float) -> float:
    """Body depth (X span) at height z (linear taper from bottom to top)."""
    frac = (z - r.foot_h) / r.body_h
    frac = max(0.0, min(1.0, frac))
    return r.body_d_bot + (r.body_d_top - r.body_d_bot) * frac


def _build_body_shell(body, r: ResolvedGarbageBinConfig, mats) -> None:
    """4 tapered walls + floor (hollow box). Walls as thin Box panels whose
    X-position/length follow the taper at mid-height (a single slab per wall is
    a faithful corrugated-steel-panel reduction; ribs add the corrugation)."""
    w = r.body_w
    h = r.body_h
    z_mid = r.foot_h + h / 2.0
    d_mid = _depth_at_z(r, z_mid)

    # Floor.
    body.visual(
        Box((r.body_d_bot, w, r.wall_t)),
        origin=Origin(xyz=(0.0, 0.0, r.foot_h + r.wall_t / 2.0)),
        material=mats["body"],
        name="body_floor", material_class_id=("rust.painted_weathered" if r.palette_style == "weathered_green" else "metal.steel_galvanized"),
    )
    # Long side walls (span X over depth, thin in Y) at +/- width/2.
    for s, tag in ((1.0, "left"), (-1.0, "right")):
        body.visual(
            Box((d_mid, r.wall_t, h)),
            origin=Origin(xyz=(0.0, s * (w / 2.0 - r.wall_t / 2.0), z_mid)),
            material=mats["body"],
            name=f"side_wall_{tag}", material_class_id=("rust.painted_weathered" if r.palette_style == "weathered_green" else "metal.steel_galvanized"),
        )
    # End walls (front +X, rear -X), thin in X, span Y.
    for s, tag in ((1.0, "front"), (-1.0, "rear")):
        x_face = s * (d_mid / 2.0 - r.wall_t / 2.0)
        body.visual(
            Box((r.wall_t, w, h)),
            origin=Origin(xyz=(x_face, 0.0, z_mid)),
            material=mats["body"],
            name=f"end_wall_{tag}", material_class_id=("rust.painted_weathered" if r.palette_style == "weathered_green" else "metal.steel_galvanized"),
        )


def _build_ribs(body, r: ResolvedGarbageBinConfig, mats) -> None:
    """Vertical corrugation ribs on each wall (per-wall for-i loop). Coarse
    Box ribs (kept modest for mesh perf)."""
    w = r.body_w
    h = r.body_h
    z_mid = r.foot_h + h / 2.0
    rib_h = h * 0.86
    rib_t = 0.012
    rib_w = 0.05
    # Long side walls (ribs spaced along X).
    d_mid = _depth_at_z(r, z_mid)
    for s, tag in ((1.0, "left"), (-1.0, "right")):
        y = s * (w / 2.0)
        n = r.rib_count_side
        for i in range(n):
            frac = (i + 0.5) / n
            x = -d_mid / 2.0 + frac * d_mid
            body.visual(
                Box((rib_w, rib_t, rib_h)),
                origin=Origin(xyz=(x, y, z_mid)),
                material=mats["body"],
                name=f"rib_side_{tag}_{i}", material_class_id=("rust.painted_weathered" if r.palette_style == "weathered_green" else "metal.steel_galvanized"),
            )
    # End walls (ribs spaced along Y).
    for s, tag in ((1.0, "front"), (-1.0, "rear")):
        x_face = s * (d_mid / 2.0)
        n = r.rib_count_end
        for i in range(n):
            frac = (i + 0.5) / n
            y = -w / 2.0 + frac * w
            body.visual(
                Box((rib_t, rib_w, rib_h)),
                origin=Origin(xyz=(x_face, y, z_mid)),
                material=mats["body"],
                name=f"rib_end_{tag}_{i}", material_class_id=("rust.painted_weathered" if r.palette_style == "weathered_green" else "metal.steel_galvanized"),
            )


def _build_rim(body, r: ResolvedGarbageBinConfig, mats) -> None:
    """4 rim bars framing the mouth at the top edge."""
    w = r.body_w
    d_top = r.body_d_top
    z = r.wall_top_z - _RIM_T / 2.0
    # Side rims (along X).
    for s, tag in ((1.0, "left"), (-1.0, "right")):
        body.visual(
            Box((d_top, _RIM_T, _RIM_T)),
            origin=Origin(xyz=(0.0, s * (w / 2.0 - _RIM_T / 2.0), z)),
            material=mats["steel"],
            name=f"rim_side_{tag}", material_class_id=("metal.steel_galvanized" if r.palette_style in {"weathered_green", "municipal_blue", "galvanized_steel", "hazard_red", "charcoal_black"} else "metal.steel_rusted"),
        )
    # End rims (along Y).
    for s, tag in ((1.0, "front"), (-1.0, "rear")):
        body.visual(
            Box((_RIM_T, w, _RIM_T)),
            origin=Origin(xyz=(s * (d_top / 2.0 - _RIM_T / 2.0), 0.0, z)),
            material=mats["steel"],
            name=f"rim_end_{tag}", material_class_id=("metal.steel_galvanized" if r.palette_style in {"weathered_green", "municipal_blue", "galvanized_steel", "hazard_red", "charcoal_black"} else "metal.steel_rusted"),
        )


def _build_feet(body, r: ResolvedGarbageBinConfig, mats, corners) -> None:
    """Fixed corner feet (inline visuals) at the given (sx, sy) corners."""
    d = r.body_d_bot
    w = r.body_w
    for (sx, sy) in corners:
        x = sx * (d / 2.0 - _FOOT_SIZE / 2.0)
        y = sy * (w / 2.0 - _FOOT_SIZE / 2.0)
        body.visual(
            Box((_FOOT_SIZE, _FOOT_SIZE, r.foot_h)),
            origin=Origin(xyz=(x, y, r.foot_h / 2.0)),
            material=mats["steel"],
            name=f"foot_{'F' if sx > 0 else 'R'}_{'L' if sy > 0 else 'R'}", material_class_id=("metal.steel_galvanized" if r.palette_style in {"weathered_green", "municipal_blue", "galvanized_steel", "hazard_red", "charcoal_black"} else "metal.steel_rusted"),
        )


# ---------------------------------------------------------------------------
# Slot D: lift_interface (inline body visuals).
# ---------------------------------------------------------------------------
def _build_fork_pockets(body, r: ResolvedGarbageBinConfig, mats) -> None:
    """Front fork pockets + 2 side trunnion pockets (inline visuals)."""
    w = r.body_w
    z_pocket = r.foot_h + 0.10
    pocket_w = 0.22
    pocket_h = 0.16
    x_front = _depth_at_z(r, z_pocket) / 2.0
    for i, sy in enumerate((0.42, -0.42)):
        body.visual(
            Box((0.16, pocket_w, pocket_h)),
            origin=Origin(xyz=(x_front + 0.05, sy * w, z_pocket)),
            material=mats["dark"],
            name=f"fork_pocket_{i}", material_class_id="metal.blackened_gunmetal",
        )
    # Side trunnion pockets (short).
    z_tr = r.foot_h + r.body_h * 0.62
    for i, sy in enumerate((1.0, -1.0)):
        body.visual(
            Box((0.18, 0.10, 0.14)),
            origin=Origin(xyz=(0.0, sy * (w / 2.0 + 0.03), z_tr)),
            material=mats["steel"],
            name=f"trunnion_pocket_{i}", material_class_id=("metal.steel_galvanized" if r.palette_style in {"weathered_green", "municipal_blue", "galvanized_steel", "hazard_red", "charcoal_black"} else "metal.steel_rusted"),
        )


def _build_lift_bar(body, r: ResolvedGarbageBinConfig, mats) -> None:
    """Front fork pockets (kept) + a continuous lift bar each side along X with
    per-frac cradle brackets (multiplicity = lift_bracket_count)."""
    w = r.body_w
    # Keep front fork pockets (common to both lift interfaces).
    z_pocket = r.foot_h + 0.10
    x_front = _depth_at_z(r, z_pocket) / 2.0
    for i, sy in enumerate((0.42, -0.42)):
        body.visual(
            Box((0.16, 0.22, 0.16)),
            origin=Origin(xyz=(x_front + 0.05, sy * w, z_pocket)),
            material=mats["dark"],
            name=f"fork_pocket_{i}", material_class_id="metal.blackened_gunmetal",
        )
    z_bar = r.foot_h + r.body_h * 0.60
    bar_len = r.body_d_bot * 0.86
    standoff = 0.05
    n = r.lift_bracket_count
    fracs = [(-0.5 + (i + 0.5) / n) for i in range(n)]
    for si, sy in enumerate((1.0, -1.0)):
        y_bar = sy * (w / 2.0 + standoff)
        # The lift bar: a cylinder rod along X.
        body.visual(
            Cylinder(radius=0.028, length=bar_len),
            origin=Origin(xyz=(0.0, y_bar, z_bar), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["steel"],
            name=f"lift_bar_{si}", material_class_id=("metal.steel_galvanized" if r.palette_style in {"weathered_green", "municipal_blue", "galvanized_steel", "hazard_red", "charcoal_black"} else "metal.steel_rusted"),
        )
        # Cradle brackets along the bar (mounting plate against the wall).
        for bi, frac in enumerate(fracs):
            x = frac * bar_len
            y_plate = sy * (w / 2.0 - 0.01)
            body.visual(
                Box((0.07, standoff + 0.04, 0.10)),
                origin=Origin(xyz=(x, y_plate + sy * standoff / 2.0, z_bar)),
                material=mats["steel"],
                name=f"lift_bracket_{si}_{bi}", material_class_id=("metal.steel_galvanized" if r.palette_style in {"weathered_green", "municipal_blue", "galvanized_steel", "hazard_red", "charcoal_black"} else "metal.steel_rusted"),
            )


# ---------------------------------------------------------------------------
# Slot C: mobility casters (CONTINUOUS roll wheels).
# ---------------------------------------------------------------------------
def _emit_caster(
    model,
    body,
    r: ResolvedGarbageBinConfig,
    mats,
    *,
    idx: int,
    cx: float,
    cy: float,
) -> None:
    """One swivel caster: inline fork/mounting plate (on body) + a wheel child
    part with a CONTINUOUS roll joint about Y at the axle center (z=WHEEL_R)."""
    # Inline mounting plate (under the body floor) + fork dropping to the axle.
    # The fork spans from the axle (z=WHEEL_R) up to the chassis floor bottom
    # (z=foot_h) so it connects the wheel to the body without poking the floor.
    plate_z = r.foot_h
    fork_bot = _WHEEL_R
    fork_top = r.foot_h
    fork_h = max(0.02, fork_top - fork_bot)
    body.visual(
        Box((0.10, 0.10, 0.02)),
        origin=Origin(xyz=(cx, cy, plate_z - 0.01)),
        material=mats["steel"],
        name=f"caster_plate_{idx}", material_class_id=("metal.steel_galvanized" if r.palette_style in {"weathered_green", "municipal_blue", "galvanized_steel", "hazard_red", "charcoal_black"} else "metal.steel_rusted"),
    )
    body.visual(
        Box((0.05, 0.085, fork_h)),
        origin=Origin(xyz=(cx, cy, fork_bot + fork_h / 2.0)),
        material=mats["steel"],
        name=f"caster_fork_{idx}", material_class_id=("metal.steel_galvanized" if r.palette_style in {"weathered_green", "municipal_blue", "galvanized_steel", "hazard_red", "charcoal_black"} else "metal.steel_rusted"),
    )
    # Wheel child part: a tire cylinder, axis rotated to lie along Y.
    wheel = model.part(f"wheel_{idx}")
    wheel.visual(
        Cylinder(radius=_WHEEL_R, length=_WHEEL_W),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["rubber"],
        name=f"wheel_tire_{idx}", material_class_id=("rubber.worn_cracked" if r.palette_style in {"weathered_green", "rust_brown"} else "rubber.smooth_plain"),
    )
    wheel.visual(
        Cylinder(radius=_WHEEL_R * 0.45, length=_WHEEL_W + 0.006),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["steel"],
        name=f"wheel_hub_{idx}", material_class_id=("metal.steel_galvanized" if r.palette_style in {"weathered_green", "municipal_blue", "galvanized_steel", "hazard_red", "charcoal_black"} else "metal.steel_rusted"),
    )
    wheel.inertial = Inertial.from_geometry(
        Cylinder(radius=_WHEEL_R, length=_WHEEL_W),
        mass=2.0,
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
    )
    model.articulation(
        f"body_to_wheel_{idx}",
        ArticulationType.CONTINUOUS,
        parent=body,
        child=wheel,
        origin=Origin(xyz=(cx, cy, _WHEEL_R)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=60.0, velocity=30.0),
    )


def _build_mobility(model, body, r: ResolvedGarbageBinConfig, mats) -> list[str]:
    d = r.body_d_bot
    w = r.body_w
    cx_off = d / 2.0 - 0.10
    cy_off = w / 2.0 - 0.10
    all_corners = [(1.0, 1.0), (1.0, -1.0), (-1.0, 1.0), (-1.0, -1.0)]
    if r.mobility == "fixed_corner_feet":
        _build_feet(body, r, mats, all_corners)
        return []
    if r.mobility == "four_caster_mobile":
        names = []
        for idx, (sx, sy) in enumerate(all_corners):
            _emit_caster(
                model, body, r, mats,
                idx=idx, cx=sx * cx_off, cy=sy * cy_off,
            )
            names.append(f"wheel_{idx}")
        return names
    # two_caster_tilt: front two corners get casters, rear two get feet.
    names = []
    front_corners = [(1.0, 1.0), (1.0, -1.0)]
    rear_corners = [(-1.0, 1.0), (-1.0, -1.0)]
    for idx, (sx, sy) in enumerate(front_corners):
        _emit_caster(
            model, body, r, mats,
            idx=idx, cx=sx * (cx_off + 0.04), cy=sy * cy_off,
        )
        names.append(f"wheel_{idx}")
    _build_feet(body, r, mats, rear_corners)
    return names


# ---------------------------------------------------------------------------
# Slot A: lid_closure. Slat / dome lids hinge about -Y at rear-top edge.
# ---------------------------------------------------------------------------
def _hinge_origin(r: ResolvedGarbageBinConfig) -> tuple[float, float, float]:
    # Hinge sits ON the rear rim bar (rim_end_rear spans x in
    # [-d_top/2, -d_top/2 + RIM_T]); place it at the rim's outer face so the
    # joint origin lands on real parent geometry (within tol).
    return (-r.body_d_top / 2.0 + _RIM_T / 2.0, 0.0, r.wall_top_z + 0.004)


def _emit_slat_lid_part(
    model,
    r: ResolvedGarbageBinConfig,
    mats,
    *,
    part_name: str,
    lid_w: float,
    y_off: float,
    n_slats: int,
    hinge_origin: tuple[float, float, float],
) -> None:
    """Build a single slat lid part authored in the hinge pivot frame.

    The lid spans depth (X) from the rear hinge line forward over the mouth.
    A single base skin connects all slats into one piece (never floating).
    Part-local frame: pivot at origin; lid body extends +X (toward front).
    """
    hx, hy, hz = hinge_origin
    lid_depth = r.body_d_top + _LID_OVER + 0.04
    lid = model.part(part_name)
    # Base skin (thin plate) tying everything together. Top face at z=0 (pivot),
    # so the skin sits just under the pivot line; slats sit on top of it.
    skin_z = -_LID_THK / 2.0
    lid.visual(
        Box((lid_depth, lid_w, _LID_THK * 0.45)),
        origin=Origin(xyz=(lid_depth / 2.0 - 0.02, y_off, skin_z)),
        material=mats["lid"],
        name=f"{part_name}_skin", material_class_id=("rust.painted_weathered" if r.palette_style == "weathered_green" else "metal.steel_galvanized"),
    )
    # Slats running along X, distributed across the lid width (Y).
    gap = 0.012
    pitch = (lid_w - gap) / max(1, n_slats)
    slat_w = pitch * 0.78
    y0 = y_off - (lid_w - pitch) / 2.0
    for i in range(n_slats):
        y = y0 + i * pitch
        lid.visual(
            Box((lid_depth - 0.04, slat_w, _LID_THK * 0.7)),
            origin=Origin(xyz=(lid_depth / 2.0 - 0.02, y, skin_z + _LID_THK * 0.35)),
            material=mats["lid"],
            name=f"{part_name}_slat_{i}", material_class_id=("rust.painted_weathered" if r.palette_style == "weathered_green" else "metal.steel_galvanized"),
        )
    # Front lift handle along the front edge.
    lid.visual(
        Cylinder(radius=_HANDLE_R, length=lid_w * 0.5),
        origin=Origin(
            xyz=(lid_depth - 0.05, y_off, skin_z + _LID_THK * 0.7),
            rpy=(math.pi / 2.0, 0.0, 0.0),
        ),
        material=mats["steel"],
        name=f"{part_name}_handle", material_class_id=("metal.steel_galvanized" if r.palette_style in {"weathered_green", "municipal_blue", "galvanized_steel", "hazard_red", "charcoal_black"} else "metal.steel_rusted"),
    )
    lid.inertial = Inertial.from_geometry(
        Box((lid_depth, lid_w, _LID_THK)),
        mass=8.0,
        origin=Origin(xyz=(lid_depth / 2.0, y_off, 0.0)),
    )
    model.articulation(
        f"body_to_{part_name}",
        ArticulationType.REVOLUTE,
        parent="body",
        child=lid,
        origin=Origin(xyz=(hx, hy, hz)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(
            effort=40.0, velocity=2.0, lower=0.0, upper=r.lid_open
        ),
        mating=MatingContract(
            parent_face_geometry="rim_end_rear",
            parent_face_side="positive_z",
            child_face_geometry=f"{part_name}_skin",
            child_face_side="negative_z",
            contact_tol=0.03,
        ),
    )


def _build_rear_hinged_slat_lid(model, r, mats) -> list[str]:
    n = r.lid_slat_count if r.lid_slat_count > 0 else 11
    _emit_slat_lid_part(
        model, r, mats,
        part_name="lid",
        lid_w=r.body_w + 0.02,
        y_off=0.0,
        n_slats=n,
        hinge_origin=_hinge_origin(r),
    )
    return ["lid"]


def _build_twin_split_lids(model, r, mats) -> list[str]:
    n_half = max(2, (r.lid_slat_count if r.lid_slat_count > 0 else 11) // 2)
    half_w = (r.body_w + 0.02) / 2.0 - 0.006
    names = []
    for j, sy in enumerate((-1.0, 1.0)):  # lid_0: y<0, lid_1: y>0
        _emit_slat_lid_part(
            model, r, mats,
            part_name=f"lid_{j}",
            lid_w=half_w,
            y_off=sy * (r.body_w / 4.0),
            n_slats=n_half,
            hinge_origin=_hinge_origin(r),
        )
        names.append(f"lid_{j}")
    return names


def _build_domed_flat_lid(model, r, mats) -> list[str]:
    hx, hy, hz = _hinge_origin(r)
    lid_depth = r.body_d_top + _LID_OVER + 0.04
    lid_w = r.body_w + 0.02
    lid = model.part("lid")
    skin_z = -_LID_THK / 2.0
    # Thin shell plate.
    lid.visual(
        Box((lid_depth, lid_w, _LID_THK * 0.45)),
        origin=Origin(xyz=(lid_depth / 2.0 - 0.02, 0.0, skin_z)),
        material=mats["lid"],
        name="lid_skin", material_class_id=("rust.painted_weathered" if r.palette_style == "weathered_green" else "metal.steel_galvanized"),
    )
    # Domed cap approximated by a few stacked shrinking slabs (a low-poly dome
    # crown; preserves a domed silhouette without a heavy cosine mesh).
    layers = 3
    for k in range(layers):
        frac = (k + 1) / (layers + 1)
        lid.visual(
            Box((lid_depth * (1.0 - 0.18 * frac), lid_w * (1.0 - 0.18 * frac), _LID_THK * 0.5)),
            origin=Origin(
                xyz=(lid_depth / 2.0 - 0.02, 0.0, skin_z + _LID_THK * 0.4 * (k + 1))
            ),
            material=mats["lid"],
            name=f"lid_dome_{k}", material_class_id=("rust.painted_weathered" if r.palette_style == "weathered_green" else "metal.steel_galvanized"),
        )
    lid.visual(
        Cylinder(radius=_HANDLE_R, length=lid_w * 0.5),
        origin=Origin(
            xyz=(lid_depth - 0.05, 0.0, skin_z + _LID_THK * 0.6),
            rpy=(math.pi / 2.0, 0.0, 0.0),
        ),
        material=mats["steel"],
        name="lid_handle", material_class_id=("metal.steel_galvanized" if r.palette_style in {"weathered_green", "municipal_blue", "galvanized_steel", "hazard_red", "charcoal_black"} else "metal.steel_rusted"),
    )
    lid.inertial = Inertial.from_geometry(
        Box((lid_depth, lid_w, _LID_THK * 2.0)),
        mass=10.0,
        origin=Origin(xyz=(lid_depth / 2.0, 0.0, 0.0)),
    )
    model.articulation(
        "body_to_lid",
        ArticulationType.REVOLUTE,
        parent="body",
        child=lid,
        origin=Origin(xyz=(hx, hy, hz)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(
            effort=45.0, velocity=2.0, lower=0.0, upper=r.lid_open
        ),
        mating=MatingContract(
            parent_face_geometry="rim_end_rear",
            parent_face_side="positive_z",
            child_face_geometry="lid_skin",
            child_face_side="negative_z",
            contact_tol=0.03,
        ),
    )
    return ["lid"]


def _build_slot_top_lid(model, r, mats) -> list[str]:
    """Fixed delivery deck (inline body visuals) + inward-swinging flap."""
    body = model.get_part("body")
    w = r.body_w
    d_top = r.body_d_top
    deck_t = 0.028
    deck_z = r.wall_top_z + deck_t / 2.0
    slot_d = d_top * 0.42  # opening size along X
    slot_w = w * 0.55
    # 4 deck panels framing a central slot (front/rear panels span X-gap,
    # side panels span Y-gap). All inline on body.
    # Front + rear deck panels.
    for s, tag in ((1.0, "front"), (-1.0, "rear")):
        panel_d = (d_top - slot_d) / 2.0
        x = s * (slot_d / 2.0 + panel_d / 2.0)
        body.visual(
            Box((panel_d, w, deck_t)),
            origin=Origin(xyz=(x, 0.0, deck_z)),
            material=mats["lid"],
            name=f"deck_{tag}", material_class_id=("rust.painted_weathered" if r.palette_style == "weathered_green" else "metal.steel_galvanized"),
        )
    # Side deck panels (over the slot's Y region).
    for s, tag in ((1.0, "left"), (-1.0, "right")):
        panel_w = (w - slot_w) / 2.0
        y = s * (slot_w / 2.0 + panel_w / 2.0)
        body.visual(
            Box((slot_d, panel_w, deck_t)),
            origin=Origin(xyz=(0.0, y, deck_z)),
            material=mats["lid"],
            name=f"deck_side_{tag}", material_class_id=("rust.painted_weathered" if r.palette_style == "weathered_green" else "metal.steel_galvanized"),
        )
    # Slot lip around the opening.
    body.visual(
        Box((slot_d + 0.04, 0.03, deck_t + 0.01)),
        origin=Origin(xyz=(0.0, slot_w / 2.0, deck_z + 0.005)),
        material=mats["steel"],
        name="slot_lip", material_class_id=("metal.steel_galvanized" if r.palette_style in {"weathered_green", "municipal_blue", "galvanized_steel", "hazard_red", "charcoal_black"} else "metal.steel_rusted"),
    )
    # Inward-swinging flap: hinged at the slot rear edge, swings about +Y so a
    # positive q drops the front edge down into the box.
    hinge_x = -slot_d / 2.0
    hinge_z = r.wall_top_z + deck_t
    flap = model.part("flap")
    flap_depth = slot_d - 0.01
    # Flap frame + slats (authored with pivot at part origin, body extends +X).
    flap.visual(
        Box((flap_depth, slot_w - 0.01, 0.012)),
        origin=Origin(xyz=(flap_depth / 2.0, 0.0, -0.006)),
        material=mats["lid"],
        name="flap_skin", material_class_id=("rust.painted_weathered" if r.palette_style == "weathered_green" else "metal.steel_galvanized"),
    )
    n_slat = 4
    pitch = (slot_w - 0.02) / n_slat
    for i in range(n_slat):
        y = -(slot_w - 0.02) / 2.0 + (i + 0.5) * pitch
        flap.visual(
            Box((flap_depth - 0.02, pitch * 0.7, 0.014)),
            origin=Origin(xyz=(flap_depth / 2.0, y, 0.0)),
            material=mats["lid"],
            name=f"flap_slat_{i}", material_class_id=("rust.painted_weathered" if r.palette_style == "weathered_green" else "metal.steel_galvanized"),
        )
    flap.inertial = Inertial.from_geometry(
        Box((flap_depth, slot_w, 0.014)),
        mass=2.0,
        origin=Origin(xyz=(flap_depth / 2.0, 0.0, 0.0)),
    )
    model.articulation(
        "body_to_flap",
        ArticulationType.REVOLUTE,
        parent="body",
        child=flap,
        origin=Origin(xyz=(hinge_x, 0.0, hinge_z)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(
            effort=10.0, velocity=2.0, lower=0.0, upper=r.flap_open
        ),
        mating=MatingContract(
            parent_face_geometry="deck_rear",
            parent_face_side="positive_x",
            child_face_geometry="flap_skin",
            child_face_side="negative_x",
            contact_tol=0.05,
        ),
    )
    return ["flap"]


_LID_BUILDERS = {
    "rear_hinged_slat_lid": _build_rear_hinged_slat_lid,
    "lid_slat_count": _build_rear_hinged_slat_lid,  # same topology, slat-N driven
    "twin_split_lids": _build_twin_split_lids,
    "domed_flat_lid": _build_domed_flat_lid,
    "slot_top_lid": _build_slot_top_lid,
}


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def build_garbage_bin(
    config: GarbageBinConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        key: model.material(f"garbage_bin_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in PALETTES[r.palette_style].items()
    }

    body = model.part("body")
    _build_body_shell(body, r, mats)
    _build_ribs(body, r, mats)
    _build_rim(body, r, mats)
    body.inertial = Inertial.from_geometry(
        Box((r.body_d_bot, r.body_w, r.body_h)),
        mass=80.0,
        origin=Origin(xyz=(0.0, 0.0, r.foot_h + r.body_h / 2.0)),
    )

    # Slot D lift interface (inline visuals on body).
    if r.lift_interface == "fork_pockets_plus_side_trunnions":
        _build_fork_pockets(body, r, mats)
    else:
        _build_lift_bar(body, r, mats)

    # Slot C mobility (feet inline OR caster wheel child parts).
    _build_mobility(model, body, r, mats)

    # Slot A lid closure (main mechanism).
    _LID_BUILDERS[r.lid_closure](model, r, mats)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_garbage_bin(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_garbage_bin(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def _lid_part_names(r: ResolvedGarbageBinConfig) -> list[str]:
    if r.lid_closure == "twin_split_lids":
        return ["lid_0", "lid_1"]
    if r.lid_closure == "slot_top_lid":
        return ["flap"]
    return ["lid"]


def run_garbage_bin_tests(
    object_model: ArticulatedObject,
    config: GarbageBinConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    body = object_model.get_part("body")
    part_names = {p.name for p in object_model.parts}
    joints = {j.name: j for j in object_model.articulations}

    # ---- Overlap allowances (element-scoped where possible). ----
    # Lid(s) seat on the rim when closed.
    for lid_name in _lid_part_names(r):
        ctx.allow_overlap(
            object_model.get_part(lid_name), body,
            reason="closed lid/flap seats on the body rim / deck hardware.",
        )
    if r.lid_closure == "twin_split_lids":
        ctx.allow_overlap(
            object_model.get_part("lid_0"), object_model.get_part("lid_1"),
            reason="the two half lids meet at the centerline parting when closed.",
        )
    # Caster wheels captured in their forks (the fork yoke straddles the tire
    # and the hub journal rides the fork).
    for idx in range(r.caster_count):
        ctx.allow_overlap(
            object_model.get_part(f"wheel_{idx}"), body,
            elem_a=f"wheel_hub_{idx}", elem_b=f"caster_fork_{idx}",
            reason="the wheel hub journal rides inside the caster fork.",
        )
        ctx.allow_overlap(
            object_model.get_part(f"wheel_{idx}"), body,
            elem_a=f"wheel_tire_{idx}", elem_b=f"caster_fork_{idx}",
            reason="the caster fork yoke straddles the upper arc of the tire.",
        )
        ctx.allow_overlap(
            object_model.get_part(f"wheel_{idx}"), body,
            elem_a=f"wheel_tire_{idx}", elem_b=f"caster_plate_{idx}",
            reason="the caster swivel plate caps the top of the tire arc.",
        )

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_joint_mating_has_gap()

    # ---- Identity / structure checks. ----
    ctx.check("body root present", "body" in part_names, details=str(sorted(part_names)))

    # (a) dumpster body volume + the whole assembly touches the ground (feet
    # in feet mode, wheels in caster mode reach z~0).
    aabb = ctx.part_world_aabb(body)
    z_mins = []
    for p in object_model.parts:
        pa = ctx.part_world_aabb(p)
        if pa is not None:
            z_mins.append(pa[0][2])
    if z_mins:
        ctx.check(
            "assembly rests on the ground (feet/wheels z~0)",
            min(z_mins) < 0.03,
            details=f"z_min={min(z_mins):.4f}",
        )
    if aabb is not None:
        (axmn, aymn, azmn), (axmx, aymx, azmx) = aabb
        ctx.check(
            "commercial dumpster width (Y span >= 1.3 m)",
            (aymx - aymn) > 1.3,
            details=f"width={aymx - aymn:.3f}",
        )

    # (b) REVOLUTE rear-hinged lid is the defining joint.
    if r.lid_closure == "slot_top_lid":
        j = joints.get("body_to_flap")
        ctx.check(
            "slot_top flap is REVOLUTE about +Y (inward swing)",
            j is not None
            and j.articulation_type == ArticulationType.REVOLUTE
            and j.axis[1] > 0.99,
            details=None if j is None else f"type={j.articulation_type} axis={tuple(j.axis)}",
        )
    else:
        lid_joint_names = [n for n in joints if n.startswith("body_to_lid")]
        ctx.check(
            "at least one REVOLUTE lid hinge present",
            len(lid_joint_names) >= 1,
            details=str(lid_joint_names),
        )
        for n in lid_joint_names:
            j = joints[n]
            ctx.check(
                f"{n} is REVOLUTE about -Y at rear-top edge",
                j.articulation_type == ArticulationType.REVOLUTE
                and abs(j.axis[1]) > 0.99
                and j.origin.xyz[0] < 0.0,
                details=f"type={j.articulation_type} axis={tuple(j.axis)} ox={j.origin.xyz[0]:.3f}",
            )
        if r.lid_closure == "twin_split_lids":
            ctx.check(
                "twin lids: two independent REVOLUTE hinges",
                len(lid_joint_names) == 2,
                details=str(lid_joint_names),
            )

    # (c) truck-lift interface present.
    fork_visuals = [v.name for v in body.visuals if v.name.startswith("fork_pocket")]
    lift_bar_visuals = [v.name for v in body.visuals if v.name.startswith("lift_bar")]
    trunnion_visuals = [
        v.name for v in body.visuals if v.name.startswith("trunnion_pocket")
    ]
    ctx.check(
        "truck-lift interface present (fork pockets / trunnions / lift bar)",
        bool(fork_visuals or lift_bar_visuals or trunnion_visuals),
        details=f"fork={fork_visuals} bar={lift_bar_visuals} trun={trunnion_visuals}",
    )

    # ---- Slat lids: slats connected by a base skin (never floating). ----
    if r.lid_closure in SLAT_LID_CLOSURES:
        for lid_name in _lid_part_names(r):
            lid = object_model.get_part(lid_name)
            skin = [v.name for v in lid.visuals if v.name.endswith("_skin")]
            slats = [v.name for v in lid.visuals if "_slat_" in v.name]
            ctx.check(
                f"{lid_name}: slats present + connected by a base skin",
                len(skin) >= 1 and len(slats) >= 1,
                details=f"skin={skin} n_slats={len(slats)}",
            )

    # ---- Mobility: caster wheels are CONTINUOUS roll about Y at axle. ----
    wheel_joints = [n for n in joints if n.startswith("body_to_wheel_")]
    ctx.check(
        "caster count matches mobility enum",
        len(wheel_joints) == r.caster_count,
        details=f"wheels={wheel_joints} expected={r.caster_count}",
    )
    for n in wheel_joints:
        j = joints[n]
        ctx.check(
            f"{n} is CONTINUOUS roll about Y at axle (z=WHEEL_R)",
            j.articulation_type == ArticulationType.CONTINUOUS
            and abs(j.axis[1]) > 0.99
            and abs(j.origin.xyz[2] - _WHEEL_R) < 0.02,
            details=f"type={j.articulation_type} axis={tuple(j.axis)} z={j.origin.xyz[2]:.3f}",
        )

    # ---- Lid actuation opens upward (slat/dome) or inward-down (flap). ----
    if r.lid_closure == "slot_top_lid":
        j = object_model.get_articulation("body_to_flap")
        flap = object_model.get_part("flap")
        closed = ctx.part_world_aabb(flap)
        with ctx.pose({j: r.flap_open * 0.8}):
            opened = ctx.part_world_aabb(flap)
        if closed is not None and opened is not None:
            ctx.check(
                "flap swings inward-down (front edge drops)",
                opened[0][2] < closed[0][2] - 0.02,
                details=f"closed_zmin={closed[0][2]:.3f} open_zmin={opened[0][2]:.3f}",
            )
    else:
        lid_name = _lid_part_names(r)[0]
        jn = f"body_to_{lid_name}"
        j = object_model.get_articulation(jn)
        lid = object_model.get_part(lid_name)
        closed = ctx.part_world_aabb(lid)
        with ctx.pose({j: r.lid_open * 0.7}):
            opened = ctx.part_world_aabb(lid)
        if closed is not None and opened is not None:
            ctx.check(
                "lid front edge lifts up when opened",
                opened[1][2] > closed[1][2] + 0.05,
                details=f"closed_top={closed[1][2]:.3f} open_top={opened[1][2]:.3f}",
            )

    # ---- slot_choices recorded. ----
    ctx.check(
        "slot_choices recorded on model.meta",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    return ctx.report()


__all__ = (
    "GarbageBinConfig",
    "ResolvedGarbageBinConfig",
    "build_garbage_bin",
    "build_seeded_garbage_bin",
    "config_from_seed",
    "resolve_config",
    "run_garbage_bin_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
