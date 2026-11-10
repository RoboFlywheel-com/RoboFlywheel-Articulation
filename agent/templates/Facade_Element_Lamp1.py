# SPDX-License-Identifier: Apache-2.0

"""Facade wall lantern (carriage sconce) modular procedural template.

slug: wall_lantern   (picture 小类 Facade Element/Lamp1)

A wall-mounted carriage lantern: a decorative mounting plate bolted to a
vertical wall, an arm that sweeps out and curls into a hook, and one or more
lantern heads that hang from the hook(s) by a chain link/loop. The single real
mechanism is the pendulum-style REVOLUTE swing of each lantern head about a
horizontal axis (X) lying in the wall plane (the lantern swings toward / away
from the wall in the Y-Z plane).

Canonical frame (real meters, Z-up):
  - wall plane is X-Z at y = 0; the bracket extends out into +Y away from the
    wall; +Z up.
  - swing axis = X; pivot = the hook eye at (hx, HOOK_Y, HOOK_Z).

Slots (modular topology axes):
  A. arm / suspension : scroll_arm | gooseneck_arm | chain_drop
  B. lantern body/cap : flared_roof_body | caged_cylinder_body | conical_roof_body
  C. head multiplicity: lantern_count N in [1,5]
       N = 1  -> single_arm     : single arm + single hook + one swing
       N >= 2 -> multi_head_bar : horizontal crossarm/bar of width proportional
                  to N with N evenly-spaced symmetric hook eyes; per-head
                  head_scale=f(N) shrinks each head so adjacent glass AABBs
                  don't collide; each head an independent REVOLUTE swing about X.

This template builds the bracket (fixed root) and the N swinging lantern heads
directly (the parallel-children + multiplicity pattern, mirroring
bell_tower_with_swinging_bell). Geometry is adapted verbatim from the 5-star
sources (cadquery lathes / swept tubes), never downgraded to Box/Cylinder.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Literal

import cadquery as cq

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
    mesh_from_geometry,
    tube_from_spline_points,
)

__modular__ = True

ArmChoice = Literal["scroll_arm", "gooseneck_arm", "chain_drop"]
BodyChoice = Literal["flared_roof_body", "caged_cylinder_body", "conical_roof_body"]
PaletteStyle = Literal[
    "galvanized_zinc",
    "warm_galvanized_bronze",
    "black_cast_iron",
    "aged_copper",
    "verdigris_copper",
]

ARM_CHOICES: tuple[ArmChoice, ...] = ("scroll_arm", "gooseneck_arm", "chain_drop")
BODY_CHOICES: tuple[BodyChoice, ...] = (
    "flared_roof_body",
    "caged_cylinder_body",
    "conical_roof_body",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "galvanized_zinc",
    "warm_galvanized_bronze",
    "black_cast_iron",
    "aged_copper",
    "verdigris_copper",
)

# Weighted multiplicity draw (bias toward small N). N in [1,5].
_N_WEIGHTS: list[tuple[int, float]] = [(1, 0.45), (2, 0.30), (3, 0.15), (4, 0.07), (5, 0.03)]

# Tessellation.
TOL = 0.0012
ATOL = 0.2


# --------------------------------------------------------------------------- #
# Palette colorways (per-seed; >= 3). Material name tokens are stable across
# colorways; only the RGBA changes. Every .visual(...) references one of:
#   metal_body, metal_dark, cage, glass, bulb, socket
# --------------------------------------------------------------------------- #

PALETTE_PRESETS: dict[str, dict[str, tuple[float, float, float, float]]] = {
    "galvanized_zinc": {
        "metal_body": (0.66, 0.68, 0.69, 1.0),
        "metal_dark": (0.55, 0.57, 0.59, 1.0),
        "cage": (0.55, 0.40, 0.34, 1.0),
        "glass": (0.62, 0.74, 0.74, 0.45),
        "bulb": (1.0, 0.96, 0.82, 1.0),
        "socket": (0.55, 0.45, 0.22, 1.0),
    },
    "warm_galvanized_bronze": {
        "metal_body": (0.64, 0.65, 0.62, 1.0),
        "metal_dark": (0.52, 0.53, 0.50, 1.0),
        "cage": (0.52, 0.38, 0.32, 1.0),
        "glass": (0.60, 0.72, 0.72, 0.45),
        "bulb": (1.0, 0.96, 0.82, 1.0),
        "socket": (0.55, 0.45, 0.22, 1.0),
    },
    "black_cast_iron": {
        "metal_body": (0.16, 0.17, 0.18, 1.0),
        "metal_dark": (0.22, 0.23, 0.24, 1.0),
        "cage": (0.22, 0.23, 0.24, 1.0),
        "glass": (0.74, 0.58, 0.30, 0.45),
        "bulb": (1.0, 0.96, 0.82, 1.0),
        "socket": (0.55, 0.45, 0.22, 1.0),
    },
    "aged_copper": {
        "metal_body": (0.42, 0.28, 0.18, 1.0),
        "metal_dark": (0.22, 0.23, 0.24, 1.0),
        "cage": (0.22, 0.23, 0.24, 1.0),
        "glass": (0.74, 0.58, 0.30, 0.45),
        "bulb": (1.0, 0.96, 0.82, 1.0),
        "socket": (0.55, 0.45, 0.22, 1.0),
    },
    "verdigris_copper": {
        "metal_body": (0.36, 0.55, 0.48, 1.0),
        "metal_dark": (0.24, 0.36, 0.32, 1.0),
        "cage": (0.22, 0.23, 0.24, 1.0),
        "glass": (0.62, 0.74, 0.74, 0.45),
        "bulb": (1.0, 0.96, 0.82, 1.0),
        "socket": (0.55, 0.45, 0.22, 1.0),
    },
}


# --------------------------------------------------------------------------- #
# Base (unscaled) lantern dimensions — adopted from parent-1 / double_lantern.
# --------------------------------------------------------------------------- #

PLATE_H = 0.230
PLATE_W = 0.120
PLATE_T = 0.014

ARM_R = 0.012

# Hook eye nominal placement (HOOK_Y is scaled by hook_reach_scale in resolve).
HOOK_Y_NOM = 0.235
HOOK_Z = 0.060
HOOK_R = 0.012
HOOK_RING_R = 0.026

LINK_R = 0.034
LINK_TUBE = 0.006

# chain_drop local chain dimensions (alternating ring planes).
CHAIN_LINK_R = 0.018
CHAIN_LINK_TUBE = 0.004
CHAIN_PITCH = 2.0 * CHAIN_LINK_R - CHAIN_LINK_TUBE

FINIAL_R = 0.018
FINIAL_H = 0.030

ROOF_TOP_R = 0.040
ROOF_BOT_R = 0.140
ROOF_H = 0.110

GLASS_R = 0.082
GLASS_H = 0.150

STRAP_N = 6
STRAP_W = 0.012
STRAP_T = 0.006
BAND_N = 3
BAND_T = 0.010
BAND_H = 0.014

BOTTOM_RING_H = 0.018
DRIP_R = 0.014
DRIP_H = 0.022

# caged_cylinder_body extras.
CAP_R = 0.092
CAP_H = 0.016
CAP_LIP_H = 0.010
NECK_R = 0.026
NECK_H = 0.012
BAR_R = 0.006
BAND_RING_R = 0.004
BULB_R = 0.030
BULB_STEM_R = 0.010

# conical_roof_body extras (hollow glass + cone + socket/bulb).
CON_GLASS_R = 0.072
CON_GLASS_H = 0.155
CON_WALL_T = 0.0035
CON_CAP_R = 0.092
CON_COLLAR_H = 0.018
CON_CONE_H = 0.060
CON_APEX_R = 0.006
CON_SOCKET_R = 0.013
CON_SOCKET_H = 0.040
CON_BULB_R = 0.030


# --------------------------------------------------------------------------- #
# Config dataclasses
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class WallLanternConfig:
    arm_choice: ArmChoice = "scroll_arm"
    body_choice: BodyChoice = "flared_roof_body"
    lantern_count: int = 1
    palette_style: PaletteStyle = "galvanized_zinc"

    chain_link_count: int = 5  # candidate-local; only used by chain_drop
    cage_bar_count: int = 8  # candidate-local; only used by caged_cylinder_body

    hook_reach_scale: float = 1.0
    lantern_size_scale: float = 1.0
    swing_range: float = 0.45


@dataclass(frozen=True)
class ResolvedWallLanternConfig:
    arm_choice: ArmChoice
    body_choice: BodyChoice
    lantern_count: int
    palette_style: PaletteStyle
    chain_link_count: int
    cage_bar_count: int

    hook_y: float
    head_scale: float
    swing_range: float

    bar_spacing: float
    hook_xs: list[float]

    palette: dict[str, tuple[float, float, float, float]]


# --------------------------------------------------------------------------- #
# Sampling / resolution
# --------------------------------------------------------------------------- #


def _weighted_n(rng: random.Random) -> int:
    roll = rng.random()
    acc = 0.0
    for n, w in _N_WEIGHTS:
        acc += w
        if roll <= acc:
            return n
    return _N_WEIGHTS[-1][0]


def config_from_seed(seed: int) -> WallLanternConfig:
    """Deterministic procedural sampling for all ordinary seeds (seed 0 too)."""
    rng = random.Random(seed)
    arm_choice = rng.choice(ARM_CHOICES)
    body_choice = rng.choice(BODY_CHOICES)
    lantern_count = _weighted_n(rng)
    palette_style = rng.choice(PALETTE_STYLES)

    chain_link_count = rng.randint(3, 6)
    cage_bar_count = rng.choice((6, 7, 8, 9, 10))

    hook_reach_scale = round(rng.uniform(0.85, 1.15), 4)
    lantern_size_scale = round(rng.uniform(0.85, 1.10), 4)
    swing_range = round(rng.uniform(0.30, 0.45), 4)

    return WallLanternConfig(
        arm_choice=arm_choice,
        body_choice=body_choice,
        lantern_count=lantern_count,
        palette_style=palette_style,
        chain_link_count=chain_link_count,
        cage_bar_count=cage_bar_count,
        hook_reach_scale=hook_reach_scale,
        lantern_size_scale=lantern_size_scale,
        swing_range=swing_range,
    )


def _head_scale(n: int) -> float:
    """Monotonically decreasing per-head scale so adjacent heads don't collide.

    N=1 -> 1.0, N=2 -> ~0.72, decreasing further for 3..5.
    """
    if n <= 1:
        return 1.0
    return min(0.95, 0.72 * 2.0 / n + 0.18)


def resolve_config(config: WallLanternConfig) -> ResolvedWallLanternConfig:
    if str(config.arm_choice) not in ARM_CHOICES:
        raise ValueError(f"Unsupported arm_choice: {config.arm_choice}")
    if str(config.body_choice) not in BODY_CHOICES:
        raise ValueError(f"Unsupported body_choice: {config.body_choice}")
    if str(config.palette_style) not in PALETTE_PRESETS:
        raise ValueError(f"Unsupported palette_style: {config.palette_style}")

    n = max(1, min(5, int(config.lantern_count)))
    hook_reach_scale = max(0.85, min(float(config.hook_reach_scale), 1.15))
    size_scale = max(0.85, min(float(config.lantern_size_scale), 1.10))
    swing_range = max(0.30, min(float(config.swing_range), 0.45))
    chain_link_count = max(1, min(6, int(config.chain_link_count)))
    cage_bar_count = max(6, min(10, int(config.cage_bar_count)))

    hook_y = HOOK_Y_NOM * hook_reach_scale

    head_scale = _head_scale(n) * size_scale

    # Spacing gate uses each body's WIDEST collision radius (the flared roof eave
    # is much wider than the glass and is the real adjacent-head collider; the
    # caged/conical caps are narrower). Adjacent heads must satisfy:
    #   2 * widest_r * head_scale + clearance <= spacing(N).
    if config.body_choice == "flared_roof_body":
        widest_r = ROOF_BOT_R
    elif config.body_choice == "caged_cylinder_body":
        widest_r = CAP_R
    else:  # conical_roof_body
        widest_r = CON_CAP_R
    half = widest_r * head_scale
    clearance = 0.024 * head_scale + 0.012
    min_spacing = 2.0 * half + clearance

    if n == 1:
        hook_xs = [0.0]
        bar_spacing = 0.0
    else:
        # spacing grows with N (bar width proportional to N). Anchor on the
        # double_lantern reference (2 * 0.130 = 0.260 for N=2) but never below
        # the body-aware min_spacing so the wide flared roofs never collide.
        base_spacing = 0.260 if n == 2 else 0.230
        bar_spacing = max(base_spacing, min_spacing)
        start = -0.5 * (n - 1) * bar_spacing
        hook_xs = [start + i * bar_spacing for i in range(n)]

    palette = dict(PALETTE_PRESETS[config.palette_style])

    return ResolvedWallLanternConfig(
        arm_choice=config.arm_choice,
        body_choice=config.body_choice,
        lantern_count=n,
        palette_style=config.palette_style,
        chain_link_count=chain_link_count,
        cage_bar_count=cage_bar_count,
        hook_y=hook_y,
        head_scale=head_scale,
        swing_range=swing_range,
        bar_spacing=bar_spacing,
        hook_xs=hook_xs,
        palette=palette,
    )


# --------------------------------------------------------------------------- #
# Shared cadquery helpers
# --------------------------------------------------------------------------- #


def _lathe_z(prof_rz: list[tuple[float, float]]) -> cq.Workplane:
    """Solid of revolution about the world Z axis (upright lathe).

    `prof_rz` is an ordered (radius, z) half profile. Authored in XY (x=radius,
    y=z), revolved about Y, then rotated +90 about X so revolution axis -> Z.
    """
    pts = [(float(r), float(z)) for (r, z) in prof_rz]
    solid = cq.Workplane("XY").polyline(pts).close().revolve(360.0, (0, 0, 0), (0, 1, 0))
    return solid.rotate((0, 0, 0), (1, 0, 0), 90.0)


def _cq(shape: cq.Workplane, name: str):
    return mesh_from_cadquery(shape, name, tolerance=TOL, angular_tolerance=ATOL)


# --------------------------------------------------------------------------- #
# BRACKET geometry (fixed root)
# --------------------------------------------------------------------------- #


def _wall_plate_shape() -> cq.Workplane:
    """Decorative leaf / fleur-de-lis wall mounting plate (parent-1 silhouette).

    Flat back face is the wall contact at y = 0; the plate stands off in +Y.
    """
    hw = PLATE_W / 2.0
    hh = PLATE_H / 2.0
    pts = [
        (0.0, hh),
        (0.32 * hw, 0.55 * hh),
        (0.95 * hw, 0.62 * hh),
        (0.62 * hw, 0.28 * hh),
        (0.85 * hw, 0.0),
        (0.62 * hw, -0.28 * hh),
        (0.95 * hw, -0.62 * hh),
        (0.32 * hw, -0.55 * hh),
        (0.0, -hh),
        (-0.32 * hw, -0.55 * hh),
        (-0.95 * hw, -0.62 * hh),
        (-0.62 * hw, -0.28 * hh),
        (-0.85 * hw, 0.0),
        (-0.62 * hw, 0.28 * hh),
        (-0.95 * hw, 0.62 * hh),
        (-0.32 * hw, 0.55 * hh),
    ]
    plate = cq.Workplane("XZ").polyline(pts).close().extrude(PLATE_T)
    plate = plate.mirror("XZ")
    try:
        plate = plate.edges("|Y").fillet(0.004)
    except Exception:
        pass
    for z in (0.55 * hh, -0.55 * hh):
        hole = (
            cq.Workplane("XZ")
            .center(0.0, z)
            .circle(0.006)
            .extrude(-(PLATE_T + 0.02))
            .translate((0.0, -0.01, 0.0))
        )
        plate = plate.cut(hole)
    return plate


def _scroll_arm_mesh(hook_y: float):
    """Low S-curve scroll gooseneck tube from plate top to the hook eye."""
    path = [
        (0.0, 0.020, 0.080),
        (0.0, 0.070, 0.140),
        (0.0, hook_y * 0.60, 0.150),
        (0.0, hook_y * 0.87, 0.120),
        (0.0, hook_y, HOOK_Z + 0.020),
    ]
    return tube_from_spline_points(
        path, radius=ARM_R, samples_per_segment=16, radial_segments=16,
        cap_ends=True, up_hint=(1.0, 0.0, 0.0),
    )


def _gooseneck_arm_mesh(hook_y: float):
    """High-arch shepherd's-crook tube (crest ~0.285 above plate center)."""
    path = [
        (0.0, 0.018, 0.095),
        (0.0, 0.035, 0.180),
        (0.0, 0.065, 0.260),
        (0.0, 0.105, 0.285),
        (0.0, hook_y * 0.64, 0.250),
        (0.0, hook_y * 0.83, 0.175),
        (0.0, hook_y, HOOK_Z + 0.022),
    ]
    return tube_from_spline_points(
        path, radius=ARM_R, samples_per_segment=18, radial_segments=16,
        cap_ends=True, up_hint=(1.0, 0.0, 0.0),
    )


def _branch_mesh(x_target: float, hook_y: float, split_y: float, split_z: float):
    """One fork/crossarm branch sweeping from the trunk split to a hook eye."""
    path = [
        (split_y * 0.0 + 0.0, split_y, split_z) if False else (0.0, split_y, split_z),
        (x_target * 0.45, max(split_y, hook_y * 0.55), split_z - 0.002),
        (x_target * 0.80, hook_y * 0.77, HOOK_Z + 0.07),
        (x_target, hook_y, HOOK_Z + 0.025),
    ]
    return tube_from_spline_points(
        path, radius=ARM_R * 0.9, samples_per_segment=16, radial_segments=14,
        cap_ends=True, up_hint=(1.0, 0.0, 0.0),
    )


def _trunk_mesh(hook_y: float):
    """Trunk of the arm rising from the plate to the fork/crossarm split."""
    path = [
        (0.0, 0.020, 0.080),
        (0.0, 0.060, 0.130),
        (0.0, 0.090, 0.150),
    ]
    return tube_from_spline_points(
        path, radius=ARM_R, samples_per_segment=16, radial_segments=16,
        cap_ends=True, up_hint=(1.0, 0.0, 0.0),
    )


def _crossarm_mesh(half_width: float, split_y: float, split_z: float):
    """Horizontal crossarm bar spanning the hook xs (width proportional to N)."""
    pts = [
        (-half_width, split_y, split_z),
        (0.0, split_y, split_z),
        (half_width, split_y, split_z),
    ]
    return tube_from_spline_points(
        pts, radius=ARM_R * 1.05, samples_per_segment=12, radial_segments=14,
        cap_ends=True, up_hint=(0.0, 0.0, 1.0),
    )


def _hook_mesh(cx: float, hook_y: float):
    """Downward hook curl in the Y-Z plane at x = cx, centered on the hook eye."""
    cy, cz = hook_y, HOOK_Z
    pts = []
    a0 = math.radians(70.0)
    a1 = math.radians(70.0 + 300.0)
    n = 28
    for i in range(n + 1):
        a = a0 + (a1 - a0) * i / n
        y = cy + HOOK_RING_R * math.cos(a)
        z = cz + HOOK_RING_R * math.sin(a)
        pts.append((cx, y, z))
    return tube_from_spline_points(
        pts, radius=HOOK_R, samples_per_segment=8, radial_segments=14,
        cap_ends=True, up_hint=(1.0, 0.0, 0.0),
    )


def _build_bracket(model: ArticulatedObject, r: ResolvedWallLanternConfig) -> None:
    """Fixed-root bracket: wall plate + arm/crossarm + N hooks.

    N=1 -> single_arm: one scroll/gooseneck arm to a single hook at x=0.
    N>=2 -> multi_head_bar: trunk + horizontal crossarm bar + per-head branch
            + hook at each HOOK_XS[i].
    """
    bracket = model.part("wall_bracket")
    hook_y = r.hook_y
    bracket.visual(_cq(_wall_plate_shape(), "wall_plate"), material="metal_body", name="wall_plate", material_class_id=("metal.steel_galvanized" if r.palette_style in {"galvanized_zinc", "black_cast_iron", "aged_copper", "verdigris_copper"} else "metal.bronze_cast"))

    if r.lantern_count == 1:
        if r.arm_choice == "gooseneck_arm":
            arm = _gooseneck_arm_mesh(hook_y)
        else:
            # scroll_arm and chain_drop both use the low scroll arm.
            arm = _scroll_arm_mesh(hook_y)
        bracket.visual(mesh_from_geometry(arm, "scroll_arm"), material="metal_body", name="scroll_arm", material_class_id=("metal.steel_galvanized" if r.palette_style in {"galvanized_zinc", "black_cast_iron", "aged_copper", "verdigris_copper"} else "metal.bronze_cast"))
        bracket.visual(
            mesh_from_geometry(_hook_mesh(0.0, hook_y), "bracket_hook_0"),
            material="metal_body",
            name="bracket_hook_0", material_class_id=("metal.steel_galvanized" if r.palette_style in {"galvanized_zinc", "black_cast_iron", "aged_copper", "verdigris_copper"} else "metal.bronze_cast"),
        )
    else:
        # Multi-head bar: trunk + crossarm + per-head branch + hook.
        split_y = 0.090
        split_z = 0.150
        bracket.visual(
            mesh_from_geometry(_trunk_mesh(hook_y), "fork_trunk"),
            material="metal_body",
            name="fork_trunk", material_class_id=("metal.steel_galvanized" if r.palette_style in {"galvanized_zinc", "black_cast_iron", "aged_copper", "verdigris_copper"} else "metal.bronze_cast"),
        )
        half_width = max(abs(x) for x in r.hook_xs)
        bracket.visual(
            mesh_from_geometry(_crossarm_mesh(half_width, split_y, split_z), "crossarm"),
            material="metal_body",
            name="crossarm", material_class_id=("metal.steel_galvanized" if r.palette_style in {"galvanized_zinc", "black_cast_iron", "aged_copper", "verdigris_copper"} else "metal.bronze_cast"),
        )
        for i, hx in enumerate(r.hook_xs):
            bracket.visual(
                mesh_from_geometry(_branch_mesh(hx, hook_y, split_y, split_z), f"fork_branch_{i}"),
                material="metal_body",
                name=f"fork_branch_{i}", material_class_id=("metal.steel_galvanized" if r.palette_style in {"galvanized_zinc", "black_cast_iron", "aged_copper", "verdigris_copper"} else "metal.bronze_cast"),
            )
            bracket.visual(
                mesh_from_geometry(_hook_mesh(hx, hook_y), f"bracket_hook_{i}"),
                material="metal_body",
                name=f"bracket_hook_{i}", material_class_id=("metal.steel_galvanized" if r.palette_style in {"galvanized_zinc", "black_cast_iron", "aged_copper", "verdigris_copper"} else "metal.bronze_cast"),
            )


# --------------------------------------------------------------------------- #
# LANTERN body geometry (swinging child). Authored in each head's OWN local
# frame: origin at the pendulum pivot (hook eye). The head hangs straight down.
# Scale factor s = head_scale applies uniformly.
# --------------------------------------------------------------------------- #


def _link_scale(s: float) -> float:
    """Suspension hardware (chain link) scale, clamped to a floor.

    The bracket hook is a FIXED-size visual; the chain link must stay large
    enough to interlink it even when the lantern body is shrunk for high N.
    """
    return max(s, 0.85)


def _suspension(s: float, arm_choice: str, n_links: int) -> dict:
    """Compute the suspension stack: chain link center Z + finial seat Z.

    The chain link geometry uses ``ls = _link_scale(s)`` (clamped) so it always
    grabs the fixed-size hook; the finial/body below use the body scale ``s``.
    """
    ls = _link_scale(s)
    if arm_choice == "chain_drop":
        link0_top_z = -0.018 * ls
        link0_cz = link0_top_z - CHAIN_LINK_R * ls
        link_czs = [link0_cz - i * CHAIN_PITCH * ls for i in range(n_links)]
        last_bot_z = link_czs[-1] - CHAIN_LINK_R * ls
        link_tube = CHAIN_LINK_TUBE * ls
    else:
        link_top_z = -0.018 * ls
        link_cz = link_top_z - LINK_R * ls
        link_czs = [link_cz]
        last_bot_z = link_cz - LINK_R * ls
        link_tube = LINK_TUBE * ls
    # The finial's central neck tip must reach UP into the last link's bottom
    # wire (which spans z in [last_bot_z - tube, last_bot_z + tube]) so the ring
    # solid genuinely pierces the neck (real suspension capture, connected mesh).
    neck_pierce_z = last_bot_z + link_tube * 0.8
    finial_top_z = neck_pierce_z
    finial_base_z = finial_top_z - FINIAL_H * s
    return {
        "link_czs": link_czs,
        "link_scale": ls,
        "finial_base_z": finial_base_z,
        "finial_top_z": finial_top_z,
        "neck_pierce_z": neck_pierce_z,
    }


def _flared_layout(s: float, finial_base_z: float) -> dict[str, float]:
    """Tall flared cone body stack below the finial seat."""
    roof_top_z = finial_base_z + 0.006 * s
    roof_bot_z = roof_top_z - ROOF_H * s
    glass_top_z = roof_top_z - 0.020 * s
    glass_bot_z = glass_top_z - GLASS_H * s
    bottom_ring_top_z = glass_bot_z + 0.004 * s
    bottom_ring_bot_z = bottom_ring_top_z - BOTTOM_RING_H * s
    return {
        "finial_base_z": finial_base_z,
        "roof_bot_z": roof_bot_z,
        "roof_top_z": roof_top_z,
        "glass_bot_z": glass_bot_z,
        "glass_top_z": glass_top_z,
        "bottom_ring_bot_z": bottom_ring_bot_z,
        "bottom_ring_top_z": bottom_ring_top_z,
    }


def _caged_layout(s: float, finial_base_z: float) -> dict[str, float]:
    """Flat disk-cap body stack: cap neck top seats the finial, glass under cap.

    The cap neck rises 6 mm ABOVE the finial base so the cap and finial visuals
    genuinely overlap (connected mesh, not a boundary-only touch).
    """
    neck_h_total = (CAP_H + NECK_H) * s
    cap_bottom_z = finial_base_z - neck_h_total + 0.006 * s
    glass_top_z = cap_bottom_z + 0.004 * s
    glass_bot_z = glass_top_z - GLASS_H * s
    bottom_ring_top_z = glass_bot_z + 0.004 * s
    bottom_ring_bot_z = bottom_ring_top_z - BOTTOM_RING_H * s
    return {
        "finial_base_z": finial_base_z,
        "cap_bottom_z": cap_bottom_z,
        "roof_bot_z": cap_bottom_z,
        "glass_bot_z": glass_bot_z,
        "glass_top_z": glass_top_z,
        "bottom_ring_bot_z": bottom_ring_bot_z,
        "bottom_ring_top_z": bottom_ring_top_z,
    }


def _single_link_shape(s: float, cz: float) -> cq.Workplane:
    link = cq.Workplane("XY").add(cq.Solid.makeTorus(LINK_R * s, LINK_TUBE * s))
    link = link.rotate((0, 0, 0), (1, 0, 0), 90.0)
    return link.translate((0.0, 0.0, cz))


def _chain_link_shape(index: int, s: float, cz: float) -> cq.Workplane:
    """One chain_drop link with alternating ring orientation (XZ / YZ)."""
    link = cq.Workplane("XY").add(cq.Solid.makeTorus(CHAIN_LINK_R * s, CHAIN_LINK_TUBE * s))
    if index % 2 == 0:
        link = link.rotate((0, 0, 0), (1, 0, 0), 90.0)
    else:
        link = link.rotate((0, 0, 0), (0, 1, 0), 90.0)
    return link.translate((0.0, 0.0, cz))


def _finial_shape(s: float, finial_base_z: float) -> cq.Workplane:
    base_r = ROOF_TOP_R * s * 0.6 + 0.008 * s
    finial_r = FINIAL_R * s
    finial_h = FINIAL_H * s
    prof = [
        (0.004 * s, 0.0),
        (base_r, 0.002 * s),
        (base_r, 0.010 * s),
        (finial_r, finial_h * 0.45),
        (finial_r * 0.45, finial_h * 0.80),
        (0.004 * s, finial_h),
        (0.0, finial_h),
        (0.0, 0.0),
    ]
    finial = _lathe_z(prof)
    return finial.translate((0.0, 0.0, finial_base_z))


def _flared_roof_shape(s: float, roof_bot_z: float) -> cq.Workplane:
    roof_bot_r = ROOF_BOT_R * s
    roof_top_r = ROOF_TOP_R * s
    roof_h = ROOF_H * s
    out = [
        (roof_bot_r, 0.0),
        (roof_top_r, roof_h),
        (roof_top_r * 0.6, roof_h + 0.012 * s),
    ]
    inn = [
        (roof_top_r * 0.6 - 0.004 * s, roof_h + 0.012 * s),
        (roof_top_r - 0.004 * s, roof_h),
        (roof_bot_r - 0.010 * s, 0.0),
    ]
    roof = _lathe_z(out + inn)
    return roof.translate((0.0, 0.0, roof_bot_z))


def _glass_shape(s: float, glass_bot_z: float) -> cq.Workplane:
    glass = cq.Workplane("XY").circle(GLASS_R * s).extrude(GLASS_H * s)
    return glass.translate((0.0, 0.0, glass_bot_z))


def _strap_cage_shape(s: float, layout: dict) -> cq.Workplane:
    glass_r = GLASS_R * s
    glass_h = GLASS_H * s
    glass_bot_z = layout["glass_bot_z"]
    strap_w = STRAP_W * s
    strap_t = STRAP_T * s
    band_t = BAND_T * s
    band_h = BAND_H * s
    cage = None
    strap_h = glass_h + 0.010 * s
    rr = glass_r + strap_t / 2.0 - 0.001 * s
    for i in range(STRAP_N):
        a = 2.0 * math.pi * i / STRAP_N
        strap = (
            cq.Workplane("XY")
            .box(strap_t, strap_w, strap_h, centered=(True, True, True))
            .translate((rr, 0.0, 0.0))
            .rotate((0, 0, 0), (0, 0, 1), math.degrees(a))
            .translate((0.0, 0.0, glass_bot_z + glass_h / 2.0))
        )
        cage = strap if cage is None else cage.union(strap)
    band_zs = [
        glass_bot_z + glass_h - 0.012 * s,
        glass_bot_z + glass_h / 2.0,
        glass_bot_z + 0.012 * s,
    ]
    for z in band_zs[:BAND_N]:
        ring = (
            cq.Workplane("XY")
            .circle(glass_r + band_t)
            .circle(glass_r - 0.001 * s)
            .extrude(band_h)
            .translate((0.0, 0.0, z - band_h / 2.0))
        )
        cage = ring if cage is None else cage.union(ring)
    return cage


def _bottom_ring_shape(s: float, bot_z: float) -> cq.Workplane:
    glass_r = GLASS_R * s
    bottom_ring_r = glass_r + 0.006 * s
    bottom_ring_h = BOTTOM_RING_H * s
    drip_r = DRIP_R * s
    drip_h = DRIP_H * s
    ring = (
        cq.Workplane("XY")
        .circle(bottom_ring_r)
        .circle(glass_r - 0.004 * s)
        .extrude(bottom_ring_h)
        .translate((0.0, 0.0, bot_z))
    )
    floor = (
        cq.Workplane("XY")
        .circle(bottom_ring_r)
        .extrude(0.008 * s)
        .translate((0.0, 0.0, bot_z - 0.008 * s))
    )
    body = ring.union(floor)
    drip_prof = [
        (drip_r, 0.0),
        (drip_r * 0.5, -drip_h * 0.6),
        (0.002 * s, -drip_h),
        (0.0, -drip_h),
        (0.0, 0.0),
    ]
    drip = _lathe_z(drip_prof)
    drip = drip.translate((0.0, 0.0, bot_z - 0.008 * s))
    return body.union(drip)


# --- caged_cylinder_body specific (flat disk cap + round bars + bulb). ----- #


def _cap_disk_shape(s: float, layout: dict) -> cq.Workplane:
    """Flat cylindrical disk cap with central neck collar + downward edge lip.

    The disk sits at the glass TOP (a flat lid), unlike the tall flared cone
    whose eave drops far below. The neck collar rises above to seat the finial.
    """
    cap_bot_z = layout["cap_bottom_z"]  # cap underside (neck rises above to seat finial)
    cap_r = CAP_R * s
    cap_h = CAP_H * s
    lip_h = CAP_LIP_H * s
    neck_r = NECK_R * s
    neck_h = NECK_H * s
    cap = cq.Workplane("XY").circle(cap_r).extrude(cap_h)
    lip = (
        cq.Workplane("XY")
        .circle(cap_r)
        .circle(cap_r - 0.008 * s)
        .extrude(lip_h)
        .translate((0.0, 0.0, -lip_h))
    )
    neck = (
        cq.Workplane("XY")
        .circle(neck_r)
        .circle(neck_r - 0.006 * s)
        .extrude(cap_h + neck_h)
    )
    roof = cap.union(lip).union(neck)
    return roof.translate((0.0, 0.0, cap_bot_z))


def _cage_bar_shape(index: int, n_bars: int, s: float, layout: dict) -> cq.Workplane:
    glass_r = GLASS_R * s
    glass_h = GLASS_H * s
    bar_r = BAR_R * s
    bar_h = glass_h + 0.008 * s
    a = 2.0 * math.pi * index / n_bars
    # Bar center embeds slightly into the glass surface (riveted cage) so the
    # bar AABB genuinely overlaps the glass on both axes, not merely tangent.
    rr = glass_r + bar_r * 0.35
    bar = (
        cq.Workplane("XY")
        .circle(bar_r)
        .extrude(bar_h)
        .translate((rr, 0.0, 0.0))
        .rotate((0, 0, 0), (0, 0, 1), math.degrees(a))
        .translate((0.0, 0.0, layout["glass_bot_z"] - 0.004 * s))
    )
    return bar


def _cage_band_shape(index: int, s: float, layout: dict) -> cq.Workplane:
    glass_r = GLASS_R * s
    glass_h = GLASS_H * s
    bar_r = BAR_R * s
    band_ring_r = BAND_RING_R * s
    glass_bot_z = layout["glass_bot_z"]
    band_zs = [
        glass_bot_z + glass_h - 0.010 * s,
        glass_bot_z + glass_h * 0.5,
        glass_bot_z + 0.010 * s,
    ]
    z = band_zs[index]
    outer_r = glass_r + bar_r * 2 + 0.002 * s
    inner_r = glass_r - 0.002 * s
    band = (
        cq.Workplane("XY")
        .circle(outer_r)
        .circle(inner_r)
        .extrude(band_ring_r * 2)
        .translate((0.0, 0.0, z - band_ring_r))
    )
    return band


def _bulb_shape(s: float, layout: dict) -> cq.Workplane:
    """Lathe bulb (globe + socket stem) seated into the bottom ring floor."""
    bottom_ring_bot_z = layout["bottom_ring_bot_z"]
    glass_top_z = layout["glass_top_z"]
    bulb_r = BULB_R * s
    stem_r = BULB_STEM_R * s
    mount_base_local = bottom_ring_bot_z - 0.002 * s
    bulb_cz = (bottom_ring_bot_z + glass_top_z) * 0.5
    globe_base = bulb_cz - bulb_r + 0.002 * s
    stem_top_local = globe_base - 0.003 * s
    globe_top_local = bulb_cz + bulb_r
    prof = [
        (0.002 * s, mount_base_local),
        (stem_r * 1.4, mount_base_local),
        (stem_r * 1.4, mount_base_local + 0.005 * s),
        (stem_r, mount_base_local + 0.008 * s),
        (stem_r, stem_top_local),
        (bulb_r * 0.75, stem_top_local + 0.003 * s),
        (bulb_r, bulb_cz),
        (bulb_r * 0.85, bulb_cz + bulb_r * 0.65),
        (bulb_r * 0.4, globe_top_local - 0.002 * s),
        (0.002 * s, globe_top_local),
        (0.002 * s, mount_base_local),
    ]
    return _lathe_z(prof)


# --- conical_roof_body specific (hollow glass + cone + socket/bulb). ------- #


def _conical_layout(s: float, neck_pierce_z: float) -> dict[str, float]:
    """Conical-roof body stack below the chain seat (rebased to canonical frame).

    The conical body has NO separate finial: the cap's stem/ball finial at the
    cone apex IS the suspension capture. The cone apex sits at neck_pierce_z so
    the cap stem pierces the last chain link (connected mesh). The collar / glass
    / base-ring hang below; socket+bulb inside.
    """
    cone_apex_z = neck_pierce_z
    collar_top_z = cone_apex_z - CON_CONE_H * s
    glass_top_z = collar_top_z - CON_COLLAR_H * s
    glass_bot_z = glass_top_z - CON_GLASS_H * s
    base_ring_top_z = glass_bot_z + 0.004 * s
    base_ring_bot_z = base_ring_top_z - 0.014 * s
    return {
        "neck_pierce_z": neck_pierce_z,
        "glass_top_z": glass_top_z,
        "glass_bot_z": glass_bot_z,
        "collar_top_z": collar_top_z,
        "cone_apex_z": cone_apex_z,
        "roof_bot_z": glass_top_z,
        "bottom_ring_bot_z": base_ring_bot_z,
        "base_ring_bot_z": base_ring_bot_z,
        "base_ring_top_z": base_ring_top_z,
    }


def _conical_cap_shape(s: float, layout: dict) -> cq.Workplane:
    """Conical aged-copper roof: flared collar + straight cone + stem/ball finial."""
    cap_r = CON_CAP_R * s
    collar_h = CON_COLLAR_H * s
    cone_h = CON_CONE_H * s
    apex_r = CON_APEX_R * s
    collar_z0 = layout["glass_top_z"]
    collar_z1 = collar_z0 + collar_h
    cone_apex_z = collar_z1 + cone_h
    bead_r = cap_r + 0.004 * s
    bead_h = 0.005 * s
    prof = [
        (0.0, collar_z0),
        (cap_r, collar_z0),
        (cap_r, collar_z1 - 0.002 * s),
        (bead_r, collar_z1),
        (bead_r, collar_z1 + bead_h),
        (cap_r - 0.002 * s, collar_z1 + bead_h + 0.002 * s),
        (apex_r, cone_apex_z),
        (0.0, cone_apex_z),
    ]
    cap = (
        cq.Workplane("XZ")
        .polyline([(rr, z) for rr, z in prof])
        .close()
        .revolve(360.0, (0, 0, 0), (0, 1, 0))
    )
    stem_bot_z = cone_apex_z - 0.010 * s
    stem_top_z = cone_apex_z + 0.012 * s
    stem = (
        cq.Workplane("XY")
        .workplane(offset=stem_bot_z)
        .circle(0.003 * s)
        .extrude(stem_top_z - stem_bot_z)
    )
    ball = cq.Workplane("XY").workplane(offset=stem_top_z + 0.004 * s).sphere(0.005 * s)
    return cap.union(stem).union(ball)


def _conical_glass_shape(s: float, layout: dict) -> cq.Workplane:
    glass_r = CON_GLASS_R * s
    glass_h = CON_GLASS_H * s
    wall_t = CON_WALL_T * s
    bot_z = layout["glass_bot_z"]
    outer = cq.Workplane("XY").workplane(offset=bot_z).circle(glass_r).extrude(glass_h)
    inner = (
        cq.Workplane("XY")
        .workplane(offset=bot_z - 0.001 * s)
        .circle(glass_r - wall_t)
        .extrude(glass_h + 0.002 * s)
    )
    return outer.cut(inner)


def _conical_base_ring_shape(s: float, layout: dict) -> cq.Workplane:
    cap_r = CON_CAP_R * s
    bot_z = layout["base_ring_bot_z"]
    ring = (
        cq.Workplane("XY")
        .workplane(offset=bot_z)
        .circle(cap_r)
        .extrude(0.014 * s)
    )
    try:
        ring = ring.edges("<Z").chamfer(0.004 * s)
    except Exception:
        pass
    # Closed floor plate so the socket has something to seat into.
    floor = (
        cq.Workplane("XY")
        .workplane(offset=bot_z)
        .circle(cap_r)
        .extrude(0.006 * s)
    )
    return ring.union(floor)


def _conical_cage_shape(s: float, layout: dict) -> cq.Workplane:
    """Wrought-iron cage: 2 ring bands + 4 vertical straps around the glass."""
    glass_r = CON_GLASS_R * s
    glass_h = CON_GLASS_H * s
    glass_bot_z = layout["glass_bot_z"]
    strap_w = 0.008 * s
    strap_t = 0.005 * s
    band_t = 0.006 * s
    band_h = 0.010 * s
    cage = None
    rr = glass_r + strap_t / 2.0
    strap_h = glass_h + 0.006 * s
    for i in range(4):
        a = 2.0 * math.pi * i / 4
        strap = (
            cq.Workplane("XY")
            .box(strap_t, strap_w, strap_h, centered=(True, True, True))
            .translate((rr, 0.0, 0.0))
            .rotate((0, 0, 0), (0, 0, 1), math.degrees(a))
            .translate((0.0, 0.0, glass_bot_z + glass_h / 2.0))
        )
        cage = strap if cage is None else cage.union(strap)
    for z in (glass_bot_z + glass_h - 0.014 * s, glass_bot_z + 0.014 * s):
        ring = (
            cq.Workplane("XY")
            .circle(glass_r + band_t)
            .circle(glass_r - 0.001 * s)
            .extrude(band_h)
            .translate((0.0, 0.0, z - band_h / 2.0))
        )
        cage = ring if cage is None else cage.union(ring)
    return cage


def _conical_socket_bulb_shape(s: float, layout: dict) -> cq.Workplane:
    """Socket stem + LED bulb globe inside the glass, seated on the base floor."""
    socket_r = CON_SOCKET_R * s
    socket_h = CON_SOCKET_H * s
    bulb_r = CON_BULB_R * s
    floor_top_z = layout["base_ring_bot_z"] + 0.006 * s
    socket_bot = floor_top_z - 0.002 * s
    socket_top = socket_bot + socket_h
    globe_cz = socket_top + bulb_r * 0.7
    prof = [
        (0.002 * s, socket_bot),
        (socket_r, socket_bot),
        (socket_r, socket_top),
        (bulb_r * 0.7, socket_top + 0.002 * s),
        (bulb_r, globe_cz),
        (bulb_r * 0.8, globe_cz + bulb_r * 0.6),
        (bulb_r * 0.35, globe_cz + bulb_r * 0.95),
        (0.002 * s, globe_cz + bulb_r),
        (0.002 * s, socket_bot),
    ]
    return _lathe_z(prof)


# --------------------------------------------------------------------------- #
# Per-head lantern builders. Each emits visuals onto one `lantern_{i}` part in
# its own local frame (pivot at origin) and returns the visual-name list.
# --------------------------------------------------------------------------- #


def _emit_chain(part, r: ResolvedWallLanternConfig, s: float, susp: dict) -> None:
    """Emit the suspension chain link(s). Names: chain_link_0..k-1.

    Links use the clamped suspension scale so they always grab the fixed hook.
    """
    czs = susp["link_czs"]
    ls = susp["link_scale"]
    if r.arm_choice == "chain_drop":
        for k, cz in enumerate(czs):
            part.visual(
                _cq(_chain_link_shape(k, ls, cz), f"chain_link_{k}"),
                material="metal_dark",
                name=f"chain_link_{k}", material_class_id=("metal.steel_galvanized" if r.palette_style in {"galvanized_zinc", "black_cast_iron", "aged_copper", "verdigris_copper"} else "metal.bronze_cast"),
            )
    else:
        part.visual(
            _cq(_single_link_shape(ls, czs[0]), "chain_link"),
            material="metal_dark",
            name="chain_link_0", material_class_id=("metal.steel_galvanized" if r.palette_style in {"galvanized_zinc", "black_cast_iron", "aged_copper", "verdigris_copper"} else "metal.bronze_cast"),
        )


def _emit_flared_body(part, r: ResolvedWallLanternConfig, s: float) -> None:
    susp = _suspension(s, r.arm_choice, r.chain_link_count)
    layout = _flared_layout(s, susp["finial_base_z"])
    _emit_chain(part, r, s, susp)
    part.visual(_cq(_finial_shape(s, layout["finial_base_z"]), "finial"), material="metal_body", name="finial", material_class_id=("metal.steel_galvanized" if r.palette_style in {"galvanized_zinc", "black_cast_iron", "aged_copper", "verdigris_copper"} else "metal.bronze_cast"))
    part.visual(_cq(_flared_roof_shape(s, layout["roof_bot_z"]), "roof"), material="metal_body", name="roof", material_class_id=("metal.steel_galvanized" if r.palette_style in {"galvanized_zinc", "black_cast_iron", "aged_copper", "verdigris_copper"} else "metal.bronze_cast"))
    part.visual(_cq(_glass_shape(s, layout["glass_bot_z"]), "glass"), material="glass", name="glass", material_class_id=("glass.clear_transparent" if r.palette_style in {"galvanized_zinc", "verdigris_copper"} else "glass.smoked_tinted"))
    part.visual(_cq(_strap_cage_shape(s, layout), "cage"), material="cage", name="cage", material_class_id=("metal.bronze_cast" if r.palette_style in {"galvanized_zinc", "warm_galvanized_bronze", "aged_copper", "verdigris_copper"} else "metal.cast_iron_bare"))
    part.visual(
        _cq(_bottom_ring_shape(s, layout["bottom_ring_bot_z"]), "bottom_ring"),
        material="cage",
        name="bottom_ring", material_class_id=("metal.bronze_cast" if r.palette_style in {"galvanized_zinc", "warm_galvanized_bronze", "aged_copper", "verdigris_copper"} else "metal.cast_iron_bare"),
    )


def _emit_caged_body(part, r: ResolvedWallLanternConfig, s: float) -> None:
    susp = _suspension(s, r.arm_choice, r.chain_link_count)
    layout = _caged_layout(s, susp["finial_base_z"])
    _emit_chain(part, r, s, susp)
    part.visual(_cq(_finial_shape(s, layout["finial_base_z"]), "finial"), material="metal_body", name="finial", material_class_id=("metal.steel_galvanized" if r.palette_style in {"galvanized_zinc", "black_cast_iron", "aged_copper", "verdigris_copper"} else "metal.bronze_cast"))
    part.visual(_cq(_cap_disk_shape(s, layout), "roof_cap"), material="metal_body", name="roof", material_class_id=("metal.steel_galvanized" if r.palette_style in {"galvanized_zinc", "black_cast_iron", "aged_copper", "verdigris_copper"} else "metal.bronze_cast"))
    part.visual(_cq(_glass_shape(s, layout["glass_bot_z"]), "glass"), material="glass", name="glass", material_class_id=("glass.clear_transparent" if r.palette_style in {"galvanized_zinc", "verdigris_copper"} else "glass.smoked_tinted"))
    n_bars = r.cage_bar_count
    for k in range(n_bars):
        part.visual(
            _cq(_cage_bar_shape(k, n_bars, s, layout), f"bar_{k}"),
            material="cage",
            name=f"bar_{k}", material_class_id=("metal.bronze_cast" if r.palette_style in {"galvanized_zinc", "warm_galvanized_bronze", "aged_copper", "verdigris_copper"} else "metal.cast_iron_bare"),
        )
    for k in range(BAND_N):
        part.visual(
            _cq(_cage_band_shape(k, s, layout), f"band_{k}"),
            material="cage",
            name=f"band_{k}", material_class_id=("metal.bronze_cast" if r.palette_style in {"galvanized_zinc", "warm_galvanized_bronze", "aged_copper", "verdigris_copper"} else "metal.cast_iron_bare"),
        )
    part.visual(_cq(_bulb_shape(s, layout), "bulb"), material="bulb", name="bulb", material_class_id="glass.frosted_smooth")
    part.visual(
        _cq(_bottom_ring_shape(s, layout["bottom_ring_bot_z"]), "bottom_ring"),
        material="cage",
        name="bottom_ring", material_class_id=("metal.bronze_cast" if r.palette_style in {"galvanized_zinc", "warm_galvanized_bronze", "aged_copper", "verdigris_copper"} else "metal.cast_iron_bare"),
    )


def _emit_conical_body(part, r: ResolvedWallLanternConfig, s: float) -> None:
    susp = _suspension(s, r.arm_choice, r.chain_link_count)
    layout = _conical_layout(s, susp["neck_pierce_z"])
    _emit_chain(part, r, s, susp)
    part.visual(_cq(_conical_cap_shape(s, layout), "conical_roof"), material="metal_body", name="roof", material_class_id=("metal.steel_galvanized" if r.palette_style in {"galvanized_zinc", "black_cast_iron", "aged_copper", "verdigris_copper"} else "metal.bronze_cast"))
    part.visual(
        _cq(_conical_glass_shape(s, layout), "lantern_glass"), material="glass", name="glass", material_class_id=("glass.clear_transparent" if r.palette_style in {"galvanized_zinc", "verdigris_copper"} else "glass.smoked_tinted")
    )
    part.visual(_cq(_conical_cage_shape(s, layout), "lantern_cage"), material="cage", name="cage", material_class_id=("metal.bronze_cast" if r.palette_style in {"galvanized_zinc", "warm_galvanized_bronze", "aged_copper", "verdigris_copper"} else "metal.cast_iron_bare"))
    part.visual(
        _cq(_conical_base_ring_shape(s, layout), "base_ring"), material="cage", name="bottom_ring", material_class_id=("metal.bronze_cast" if r.palette_style in {"galvanized_zinc", "warm_galvanized_bronze", "aged_copper", "verdigris_copper"} else "metal.cast_iron_bare")
    )
    part.visual(
        _cq(_conical_socket_bulb_shape(s, layout), "socket_bulb"),
        material="socket",
        name="bulb", material_class_id="metal.brass_aged",
    )


def _emit_lantern_body(part, r: ResolvedWallLanternConfig, s: float) -> None:
    if r.body_choice == "flared_roof_body":
        _emit_flared_body(part, r, s)
    elif r.body_choice == "caged_cylinder_body":
        _emit_caged_body(part, r, s)
    else:
        _emit_conical_body(part, r, s)


# --------------------------------------------------------------------------- #
# Model assembly
# --------------------------------------------------------------------------- #


def build_wall_lantern(
    config: WallLanternConfig,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name="wall_lantern", assets=assets)
    for material_name, rgba in r.palette.items():
        model.material(material_name, rgba=rgba)

    _build_bracket(model, r)
    bracket = model.get_part("wall_bracket")

    s = r.head_scale
    n = r.lantern_count
    for i, hx in enumerate(r.hook_xs):
        name = "lantern" if n == 1 else f"lantern_{i}"
        lantern = model.part(name)
        _emit_lantern_body(lantern, r, s)

        swing_name = "lantern_swing" if n == 1 else f"lantern_swing_{i}"
        model.articulation(
            swing_name,
            ArticulationType.REVOLUTE,
            parent=bracket,
            child=lantern,
            origin=Origin(xyz=(hx, r.hook_y, HOOK_Z)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(
                effort=8.0, velocity=2.0, lower=-r.swing_range, upper=r.swing_range
            ),
        )

    return model


def build_seeded_wall_lantern(seed: int) -> ArticulatedObject:
    return build_wall_lantern(config_from_seed(seed))


# --------------------------------------------------------------------------- #
# Slot-choice reporting (module_topology_diversity gate)
# --------------------------------------------------------------------------- #


def slot_choices_for_config(config: WallLanternConfig) -> list[tuple[str, str]]:
    r = resolve_config(config)
    return [
        ("arm", r.arm_choice),
        ("body", r.body_choice),
        ("multiplicity", f"{r.lantern_count}_head"),
    ]


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    return slot_choices_for_config(config_from_seed(seed))


# --------------------------------------------------------------------------- #
# Author tests
# --------------------------------------------------------------------------- #


def _lantern_names(r: ResolvedWallLanternConfig) -> list[str]:
    if r.lantern_count == 1:
        return ["lantern"]
    return [f"lantern_{i}" for i in range(r.lantern_count)]


def _hook_name(r: ResolvedWallLanternConfig, i: int) -> str:
    return f"bracket_hook_{i}"


def _declare_capture_overlaps(ctx, model, r: ResolvedWallLanternConfig) -> None:
    """Element-scoped intentional interlinks: chain link <-> hook, link <-> finial.

    Declared for EVERY head up front (avoid masked unmask chains)."""
    bracket = model.get_part("wall_bracket")
    names = _lantern_names(r)
    for i, lname in enumerate(names):
        lantern = model.get_part(lname)
        hook_elem = _hook_name(r, i)
        # The top chain link(s) interlink the hook curl for this head. For a
        # multi-link chain_drop chain both the first and second links can brush
        # the hook curl (a short chain captured on the hook).
        top_links = ["chain_link_0"]
        if r.arm_choice == "chain_drop":
            top_links = [f"chain_link_{k}" for k in range(min(2, r.chain_link_count))]
        for cl in top_links:
            ctx.allow_overlap(
                lantern,
                bracket,
                elem_a=cl,
                elem_b=hook_elem,
                reason=f"Top chain link {cl} of head {i} interlinks the hook curl "
                f"(real chain-link capture).",
            )
        # At small head_scale the finial / cap neck is drawn up close to the
        # hook curl (the link captures the finial right under the hook); allow
        # the small intentional brush.
        finial_elem = "finial" if r.body_choice != "conical_roof_body" else "roof"
        ctx.allow_overlap(
            lantern,
            bracket,
            elem_a=finial_elem,
            elem_b=hook_elem,
            reason=f"Finial/cap neck of head {i} is captured just under the hook "
            f"curl (suspension capture brush).",
        )
        # finial / cap neck captured by the bottom-most link of this head.
        last_link = (
            "chain_link_0"
            if r.arm_choice != "chain_drop"
            else f"chain_link_{r.chain_link_count - 1}"
        )
        ctx.allow_overlap(
            lantern,
            lantern,
            elem_a=last_link,
            elem_b="finial" if r.body_choice != "conical_roof_body" else "roof",
            reason=f"Finial/cap neck {i} threads through the bottom chain link "
            f"(suspension capture).",
        )
        # chain_drop: adjacent links interlock.
        if r.arm_choice == "chain_drop":
            for k in range(r.chain_link_count - 1):
                ctx.allow_overlap(
                    lantern,
                    lantern,
                    elem_a=f"chain_link_{k}",
                    elem_b=f"chain_link_{k + 1}",
                    reason=f"Adjacent chain links {k}/{k+1} interlock (real chain).",
                )
        # caged body: bulb socket seats into the bottom-ring floor.
        if r.body_choice == "caged_cylinder_body":
            ctx.allow_overlap(
                lantern,
                lantern,
                elem_a="bulb",
                elem_b="bottom_ring",
                reason=f"Bulb socket {i} seats into the bottom ring floor.",
            )
        if r.body_choice == "conical_roof_body":
            ctx.allow_overlap(
                lantern,
                lantern,
                elem_a="bulb",
                elem_b="bottom_ring",
                reason=f"Socket {i} seats into the base ring floor.",
            )


def run_wall_lantern_tests(model: ArticulatedObject, config: WallLanternConfig) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)

    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    _declare_capture_overlaps(ctx, model, r)
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)
    ctx.fail_if_joint_mating_has_gap()

    bracket = model.get_part("wall_bracket")
    names = _lantern_names(r)

    # Wall plate mounts at the wall plane (y near 0).
    plate_aabb = ctx.part_element_world_aabb(bracket, elem="wall_plate")
    ctx.check(
        "wall plate mounts at the wall plane",
        plate_aabb is not None and plate_aabb[0][1] <= 0.003 and plate_aabb[1][1] <= PLATE_T + 0.01,
        details=f"plate_aabb={plate_aabb}",
    )

    glass_aabbs: list = []
    for i, lname in enumerate(names):
        lantern = model.get_part(lname)
        swing_name = "lantern_swing" if r.lantern_count == 1 else f"lantern_swing_{i}"
        swing = model.get_articulation(swing_name)

        # Joint identity: REVOLUTE about X at this head's hook eye.
        ctx.check(
            f"swing_{i} is revolute",
            str(swing.articulation_type).lower().endswith("revolute"),
            details=f"type={swing.articulation_type}",
        )
        ax = tuple(round(c, 6) for c in swing.axis)
        ctx.check(
            f"swing_{i} axis is X",
            abs(ax[0]) > 0.99 and abs(ax[1]) < 1e-6 and abs(ax[2]) < 1e-6,
            details=f"axis={ax}",
        )
        jo = swing.origin.xyz
        ctx.check(
            f"swing_{i} pivot at hook eye {i}",
            abs(jo[0] - r.hook_xs[i]) < 1e-4
            and abs(jo[1] - r.hook_y) < 1e-4
            and abs(jo[2] - HOOK_Z) < 1e-4,
            details=f"origin={jo}",
        )

        # Body geometry relationships: roof above glass, ring below glass.
        roof_aabb = ctx.part_element_world_aabb(lantern, elem="roof")
        glass_aabb = ctx.part_element_world_aabb(lantern, elem="glass")
        ring_aabb = ctx.part_element_world_aabb(lantern, elem="bottom_ring")
        glass_aabbs.append(glass_aabb)
        ctx.check(
            f"roof_{i} above glass_{i}",
            roof_aabb is not None and glass_aabb is not None and roof_aabb[1][2] > glass_aabb[1][2],
        )
        ctx.check(
            f"bottom_ring_{i} below glass_{i}",
            ring_aabb is not None
            and glass_aabb is not None
            and ring_aabb[0][2] < glass_aabb[0][2] + 0.004,
        )
        # Cage wraps the glass. The caged_cylinder body has discrete round bars
        # (bar_0..) instead of a single unioned `cage` visual; the flared and
        # conical bodies have one `cage`. Check whichever this body has.
        cage_elem = "bar_0" if r.body_choice == "caged_cylinder_body" else "cage"
        ctx.expect_overlap(
            lantern,
            lantern,
            axes="xy",
            elem_a=cage_elem,
            elem_b="glass",
            min_overlap=0.0,
            name=f"cage_{i} wraps glass_{i}",
        )
        # Roof/cap eave covers the glass.
        ctx.expect_within(
            lantern,
            lantern,
            axes="xy",
            inner_elem="glass",
            outer_elem="roof",
            margin=0.001,
            name=f"glass_{i} sits under roof_{i} eave",
        )

        # Mechanism: positive swing moves the head bottom outward in Y and up.
        rest_ring = ctx.part_element_world_aabb(lantern, elem="bottom_ring")
        with ctx.pose({swing: r.swing_range}):
            swung_ring = ctx.part_element_world_aabb(lantern, elem="bottom_ring")
        if rest_ring is not None and swung_ring is not None:
            rest_yc = (rest_ring[0][1] + rest_ring[1][1]) / 2.0
            swung_yc = (swung_ring[0][1] + swung_ring[1][1]) / 2.0
            rest_zc = (rest_ring[0][2] + rest_ring[1][2]) / 2.0
            swung_zc = (swung_ring[0][2] + swung_ring[1][2]) / 2.0
            ctx.check(
                f"swing_{i} moves head outward in Y",
                abs(swung_yc - rest_yc) > 0.02,
                details=f"rest_yc={rest_yc}, swung_yc={swung_yc}",
            )
            ctx.check(
                f"swing_{i} raises head (pendulum arc)",
                swung_zc > rest_zc + 0.003,
                details=f"rest_zc={rest_zc}, swung_zc={swung_zc}",
            )

    # Multi-head: adjacent glass AABBs do not collide in X.
    if r.lantern_count >= 2:
        for i in range(r.lantern_count - 1):
            a = glass_aabbs[i]
            b = glass_aabbs[i + 1]
            if a is None or b is None:
                continue
            gap = b[0][0] - a[1][0]
            ctx.check(
                f"heads {i}/{i+1} glass do not collide in X",
                gap > -0.001,
                details=f"gap={gap}",
            )

    return ctx.report()


__all__ = [
    "ArmChoice",
    "BodyChoice",
    "PaletteStyle",
    "WallLanternConfig",
    "ResolvedWallLanternConfig",
    "config_from_seed",
    "resolve_config",
    "build_wall_lantern",
    "build_seeded_wall_lantern",
    "slot_choices_for_seed",
    "slot_choices_for_config",
    "run_wall_lantern_tests",
]
