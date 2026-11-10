# SPDX-License-Identifier: Apache-2.0

"""Modular template for pictureX/0611 crimping_tool (manual ratcheting terminal crimper).

Spec: articraft_template_authoring/specs_modular_v1/pictureX_0611_crimping_tool.md

Slot graph (mixed: parallel children + multiplicity):
  skeleton   : open_v_compound (S1) / layered_ratchet_frame (S2) / inline_press_frame (S3)
  die_head   : integral_fixed_die / cassette_die / turret_die   (open_v family)
               single_hex_die / profile_station_die             (layered family)
               connector_press_head / four_indent_head          (inline family)
  controls   : lever_release_star_dial / paddle_release_disc_dial (open_v + inline)
               handle_pawl_release                                (layered)

Sources (5-star pool, read in full; line refs in factory docstrings):
  S1 rec_picturex_0611__crimping_tool__001__png_b1dc55ef9a464866b3da68627196df5e
  S2 rec_picturex_0611__crimping_tool__002__png_bb7fbd8e74a44490a20087674b984a06
  S3 rec_picturex_0611__crimping_tool__003__png_5ac1472bfeda42a5b4e6a2b4aa673fbc
  S4 rec_picturex0611_crimping_tool_fork_single_hex_die_20260714
  S5 rec_picturex0611_crimping_tool_fork_six_station_die_20260714
  S6 rec_picturex0611_crimping_tool_fork_interchangeable_cassette_20260714
  S7 rec_picturex0611_crimping_tool_fork_rotating_turret_die_20260714
  S8 rec_picturex0611_crimping_tool_fork_four_indent_head_20260714

Canonical frame: the tool lies in the world XY plane, plate lamination along Z,
every articulation axis is (0,0,+-1). S1/S6/S7 were authored as X/Z silhouettes
with thickness along Y; their profiles are remapped (x,z)->(x,y) with thickness
offsets along Z, preserving the extruded-polyline/disc primitive family (Rule 3).

Scale contract (all motion is about z, so in-plane similarity about the pivot is
an exact motion-preserving transform):
  handle_scale : in-plane stretch of the grip/handle zone away from the pivot.
  head_scale   : in-plane scaling of head-zone geometry about the main pivot
                 (layered / inline / open_v head parts; z layout untouched).
  jaw_open_scale : shrinks (never widens) the main pivot travel.
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
    MatingContract,
    Mimic,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
)
from agent.templates._modular import InterfaceSpec

__modular__ = True

Skeleton = Literal["open_v_compound", "layered_ratchet_frame", "inline_press_frame"]
DieHead = Literal[
    "integral_fixed_die",
    "cassette_die",
    "turret_die",
    "single_hex_die",
    "profile_station_die",
    "connector_press_head",
    "four_indent_head",
]
Controls = Literal[
    "lever_release_star_dial",
    "paddle_release_disc_dial",
    "handle_pawl_release",
]
PaletteStyle = Literal[
    "safety_orange", "workshop_blue", "blue_red_pro", "red_black", "yellow_black"
]

SKELETONS: tuple[Skeleton, ...] = (
    "open_v_compound",
    "layered_ratchet_frame",
    "inline_press_frame",
)
HEADS_BY_SKELETON: dict[Skeleton, tuple[DieHead, ...]] = {
    "open_v_compound": ("integral_fixed_die", "cassette_die", "turret_die"),
    "layered_ratchet_frame": ("single_hex_die", "profile_station_die"),
    "inline_press_frame": ("connector_press_head", "four_indent_head"),
}
CONTROLS_BY_SKELETON: dict[Skeleton, tuple[Controls, ...]] = {
    "open_v_compound": ("lever_release_star_dial", "paddle_release_disc_dial"),
    "layered_ratchet_frame": ("handle_pawl_release",),
    "inline_press_frame": ("paddle_release_disc_dial", "lever_release_star_dial"),
}
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "safety_orange", "workshop_blue", "blue_red_pro", "red_black", "yellow_black"
)

# palette keys: steel (frame plates), die (hardened die faces), pin (pivot
# hardware), grip (molded grip), accent (rubber inset / accent strip), dark.
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    # S1 colorway (safety orange / black oxide / satin pivots)
    "safety_orange": {
        "steel": (0.055, 0.060, 0.064, 1.0),
        "die": (0.24, 0.26, 0.27, 1.0),
        "pin": (0.43, 0.45, 0.46, 1.0),
        "grip": (0.96, 0.23, 0.035, 1.0),
        "accent": (0.025, 0.028, 0.030, 1.0),
        "dark": (0.018, 0.022, 0.024, 1.0),
    },
    # S2 colorway (bright blue vinyl / black oxide / zinc pins)
    "workshop_blue": {
        "steel": (0.035, 0.045, 0.050, 1.0),
        "die": (0.018, 0.022, 0.024, 1.0),
        "pin": (0.70, 0.73, 0.75, 1.0),
        "grip": (0.015, 0.36, 0.82, 1.0),
        "accent": (0.35, 0.38, 0.40, 1.0),
        "dark": (0.02, 0.02, 0.02, 1.0),
    },
    # S3 colorway (molded blue grip + red accents, hardened edges)
    "blue_red_pro": {
        "steel": (0.055, 0.060, 0.065, 1.0),
        "die": (0.68, 0.70, 0.72, 1.0),
        "pin": (0.77, 0.79, 0.80, 1.0),
        "grip": (0.015, 0.22, 0.82, 1.0),
        "accent": (0.88, 0.025, 0.025, 1.0),
        "dark": (0.025, 0.028, 0.030, 1.0),
    },
    # color-only extrapolations (axis 6): common pro-tool colorways
    "red_black": {
        "steel": (0.045, 0.048, 0.052, 1.0),
        "die": (0.30, 0.32, 0.33, 1.0),
        "pin": (0.62, 0.64, 0.66, 1.0),
        "grip": (0.76, 0.09, 0.06, 1.0),
        "accent": (0.03, 0.03, 0.03, 1.0),
        "dark": (0.02, 0.022, 0.024, 1.0),
    },
    "yellow_black": {
        "steel": (0.050, 0.053, 0.056, 1.0),
        "die": (0.26, 0.28, 0.29, 1.0),
        "pin": (0.58, 0.60, 0.62, 1.0),
        "grip": (0.93, 0.74, 0.05, 1.0),
        "accent": (0.04, 0.04, 0.04, 1.0),
        "dark": (0.02, 0.02, 0.02, 1.0),
    },
}


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class PictureX0611CrimpingToolConfig:
    skeleton: Skeleton = "open_v_compound"
    die_head: DieHead = "integral_fixed_die"
    controls: Controls = "lever_release_star_dial"
    palette_style: PaletteStyle = "safety_orange"
    die_station_count: int = 5     # layered profile_station_die: 3..6 (single_hex -> 1)
    nest_pair_count: int = 3       # open_v integral/cassette die nest pairs: 2..4
    turret_nest_count: int = 4     # turret_die rim nests: 3..5
    scallop_count: int = 4         # inline grip finger scallops: 3..5 (axis-4 count)
    handle_scale: float = 1.0
    head_scale: float = 1.0
    grip_thickness_scale: float = 1.0
    jaw_open_scale: float = 1.0
    name: str = "picturex_0611_crimping_tool"


@dataclass(frozen=True)
class ResolvedPictureX0611CrimpingToolConfig:
    skeleton: Skeleton
    die_head: DieHead
    controls: Controls
    palette_style: PaletteStyle
    die_station_count: int
    nest_pair_count: int
    turret_nest_count: int
    scallop_count: int
    handle_scale: float
    head_scale: float
    grip_thickness_scale: float
    jaw_open_scale: float
    name: str


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def resolve_config(
    config: PictureX0611CrimpingToolConfig,
) -> ResolvedPictureX0611CrimpingToolConfig:
    skeleton = config.skeleton if config.skeleton in SKELETONS else "open_v_compound"
    legal_heads = HEADS_BY_SKELETON[skeleton]
    die_head = config.die_head if config.die_head in legal_heads else legal_heads[0]
    legal_controls = CONTROLS_BY_SKELETON[skeleton]
    controls = config.controls if config.controls in legal_controls else legal_controls[0]
    palette = (
        config.palette_style if config.palette_style in PALETTE_STYLES else "safety_orange"
    )
    return ResolvedPictureX0611CrimpingToolConfig(
        skeleton=skeleton,
        die_head=die_head,
        controls=controls,
        palette_style=palette,
        die_station_count=int(_clamp(config.die_station_count, 3, 6)),
        nest_pair_count=int(_clamp(config.nest_pair_count, 2, 4)),
        turret_nest_count=int(_clamp(config.turret_nest_count, 3, 5)),
        scallop_count=int(_clamp(config.scallop_count, 3, 5)),
        handle_scale=_clamp(config.handle_scale, 0.90, 1.15),
        head_scale=_clamp(config.head_scale, 0.92, 1.10),
        grip_thickness_scale=_clamp(config.grip_thickness_scale, 0.90, 1.12),
        jaw_open_scale=_clamp(config.jaw_open_scale, 0.85, 1.0),
        name=config.name,
    )


def config_from_seed(seed: int) -> PictureX0611CrimpingToolConfig:
    rng = random.Random(seed)
    skeleton: Skeleton = rng.choices(SKELETONS, weights=(0.36, 0.32, 0.32))[0]
    if skeleton == "open_v_compound":
        die_head: DieHead = rng.choices(
            ("integral_fixed_die", "cassette_die", "turret_die"), weights=(0.4, 0.3, 0.3)
        )[0]
        controls: Controls = rng.choices(
            ("lever_release_star_dial", "paddle_release_disc_dial"), weights=(0.6, 0.4)
        )[0]
    elif skeleton == "layered_ratchet_frame":
        die_head = rng.choices(
            ("profile_station_die", "single_hex_die"), weights=(0.8, 0.2)
        )[0]
        controls = "handle_pawl_release"
    else:
        die_head = rng.choices(
            ("connector_press_head", "four_indent_head"), weights=(0.55, 0.45)
        )[0]
        controls = rng.choices(
            ("paddle_release_disc_dial", "lever_release_star_dial"), weights=(0.6, 0.4)
        )[0]
    return PictureX0611CrimpingToolConfig(
        skeleton=skeleton,
        die_head=die_head,
        controls=controls,
        palette_style=rng.choice(PALETTE_STYLES),
        die_station_count=rng.choices((3, 4, 5, 6), weights=(0.16, 0.16, 0.42, 0.26))[0],
        nest_pair_count=rng.choices((2, 3, 4), weights=(0.25, 0.5, 0.25))[0],
        turret_nest_count=rng.choices((3, 4, 5), weights=(0.25, 0.5, 0.25))[0],
        scallop_count=rng.choice((3, 4, 5)),
        handle_scale=round(rng.uniform(0.90, 1.15), 4),
        head_scale=round(rng.uniform(0.92, 1.10), 4),
        grip_thickness_scale=round(rng.uniform(0.90, 1.12), 4),
        jaw_open_scale=round(rng.uniform(0.85, 1.0), 4),
        name=f"picturex_0611_crimping_tool_seed_{seed}",
    )


def slot_choices_for_config(
    config: PictureX0611CrimpingToolConfig,
) -> list[tuple[str, str]]:
    r = resolve_config(config)
    choices = [
        ("skeleton", r.skeleton),
        ("die_head", r.die_head),
        ("controls", r.controls),
    ]
    if r.die_head == "profile_station_die":
        choices.append(("die_station_count", str(r.die_station_count)))
    elif r.die_head == "single_hex_die":
        choices.append(("die_station_count", "1"))
    elif r.die_head in ("integral_fixed_die", "cassette_die"):
        choices.append(("nest_pair_count", str(r.nest_pair_count)))
    elif r.die_head == "turret_die":
        choices.append(("turret_nest_count", str(r.turret_nest_count)))
    choices.append(("palette_style", r.palette_style))
    return choices


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# cadquery helpers (primitive families from the sources; Rule 3)
# ---------------------------------------------------------------------------
def _poly_c(pts, thickness: float, zc: float):
    """S1-family plate: closed polyline extruded symmetrically, centered at zc (mm)."""
    solid = cq.Workplane("XY").polyline(pts).close().extrude(thickness / 2.0, both=True)
    return solid.translate((0.0, 0.0, zc))


def _disc_c(radius: float, thickness: float, x: float, y: float, zc: float):
    return (
        cq.Workplane("XY")
        .center(x, y)
        .circle(radius)
        .extrude(thickness / 2.0, both=True)
        .translate((0.0, 0.0, zc))
    )


def _star_poly(radius_outer: float, radius_inner: float, points: int, thickness: float):
    """S1 L40-L46 star wheel profile."""
    profile = []
    for i in range(points * 2):
        a = math.pi / 2.0 + i * math.pi / points
        r = radius_outer if i % 2 == 0 else radius_inner
        profile.append((r * math.cos(a), r * math.sin(a)))
    return cq.Workplane("XY").polyline(profile).close().extrude(thickness / 2.0, both=True)


def _poly_b(pts, thickness: float, z0: float = 0.0, fillet: float = 0.0):
    """S2/S3-family plate: closed polyline extruded from z0 upward."""
    shape = cq.Workplane("XY").polyline(pts).close().extrude(thickness).translate((0, 0, z0))
    if fillet:
        try:
            shape = shape.edges("|Z").fillet(fillet)
        except Exception:
            pass
    return shape


def _capsule(length, width, thickness, *, x0=0.0, z0=0.0, angle=0.0):
    """S2 L30-L40 rounded bar."""
    r = width / 2.0
    body = cq.Workplane("XY").box(length, width, thickness, centered=(True, True, False))
    body = body.translate((x0 + length / 2.0, 0.0, z0))
    for x in (x0, x0 + length):
        end = cq.Workplane("XY").circle(r).extrude(thickness).translate((x, 0.0, z0))
        body = body.union(end)
    if angle:
        body = body.rotate((0, 0, 0), (0, 0, 1), math.degrees(angle))
    return body


def _cut_round_holes(shape, holes, z0=-0.02, depth=0.05):
    for x, y, radius in holes:
        cutter = cq.Workplane("XY").center(x, y).circle(radius).extrude(depth).translate((0, 0, z0))
        shape = shape.cut(cutter)
    return shape


def _rounded_bar(x0, x1, y0, y1, thickness, z0=0.0):
    """S3 L41-L66 rounded grip bar (mm)."""
    radius = (y1 - y0) * 0.5
    core = cq.Workplane("XY").box(x1 - x0 - 2.0 * radius, y1 - y0, thickness)
    core = core.translate(((x0 + x1) * 0.5, (y0 + y1) * 0.5, z0 + thickness * 0.5))
    for x in (x0 + radius, x1 - radius):
        end = (
            cq.Workplane("XY")
            .center(x, (y0 + y1) * 0.5)
            .circle(radius)
            .extrude(thickness)
            .translate((0.0, 0.0, z0))
        )
        core = core.union(end)
    return core


def _vis_mm(part, solid, name: str, material) -> None:
    """mm-frame cadquery visual (S1/S3 style, coarse tessellation per budget)."""
    part.visual(
        mesh_from_cadquery(solid, name, tolerance=0.12, angular_tolerance=0.12, unit_scale=0.001),
        material=material,
        name=name, material_class_id="metal.generic_plain",
    )


def _vis_m(part, solid, name: str, material, tol: float = 0.0007) -> None:
    """meter-frame cadquery visual (S2 style)."""
    part.visual(
        mesh_from_cadquery(solid, name, tolerance=tol),
        material=material,
        name=name, material_class_id="metal.generic_plain",
    )


def _lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


# --- S1 open_v silhouettes (mm, XZ source remapped to XY) -------------------
# Hoisted to module scope so the splay derivation below and the builders read
# ONE copy of each outline (Contract 3c: shared quantities are single-sourced).
_S1_FIXED_SHANK = [
    (-10, -12), (4, -30), (11, -92), (20, -165), (31, -213),
    (43, -224), (50, -216), (43, -185), (35, -118), (29, -57),
    (30, -8), (23, 34), (25, 63), (13, 76), (-2, 67), (-7, 34),
]  # S1 L105-L117
_S1_FIXED_GRIP = [
    (9, -55), (20, -68), (29, -119), (37, -177), (48, -216),
    (43, -229), (31, -226), (20, -198), (12, -145), (4, -84),
]  # S1 L124-L133
_S1_FIXED_INSET = [
    (20, -83), (27, -112), (34, -165), (42, -208), (38, -217),
    (31, -207), (23, -171), (16, -118), (13, -92),
]  # S1 L135-L145
_S1_FIXED_STOP = [(3, -42), (15, -46), (18, -57), (7, -61), (0, -52)]  # S1 L146-L154
_S1_MOV_SHANK = [
    (7, 8), (-8, -6), (-18, -54), (-31, -112), (-47, -176),
    (-58, -218), (-68, -225), (-75, -217), (-65, -184),
    (-51, -121), (-35, -60), (-17, -13), (-7, 17),
]  # S1 L188-L202
_S1_MOV_GRIP = [
    (-14, -50), (-26, -67), (-40, -120), (-54, -179), (-66, -219),
    (-61, -231), (-48, -228), (-38, -202), (-25, -148), (-9, -79),
]  # S1 L204-L213
_S1_MOV_INSET = [
    (-25, -82), (-34, -112), (-47, -166), (-59, -210), (-55, -220),
    (-48, -210), (-38, -173), (-27, -121), (-20, -91),
]  # S1 L215-L224
_S1_MOV_STOP = [(-17, -37), (-5, -41), (-2, -52), (-14, -57), (-22, -48)]  # S1 L255-L262

# S1 L271 main closing stroke. Load-bearing: S1 L478-L487 asserts the dies sit
# 0-3mm apart at exactly this value, so it is the die-closure stroke, not a free
# knob. Both the joint limit and the splay derivation read this one copy.
_OPEN_V_STROKE = 0.42

# --- open_v die working planes (mm, pre-head_scale) -------------------------
# The closing stroke is fixed by S1, so every open_v head must present its nest
# faces on the SAME two planes or the stroke lands wrong: a fixed-side face
# further toward -x is rammed, one further toward +x never closes. Single-
# sourcing them here is what keeps the cassette/turret heads honest against the
# integral head they share the stroke with (Contract 3c).
# Fixed side: the -x edge of the S1 fixed die block (its (-3,68) vertex, S1
# L52), where the half-nests are cut open. Emitted by _open_v_fixed_die.
_OPEN_V_DIE_FACE_X_MM = -3.0
# Moving side: the +x edge of the S1 moving die block (its (2,67) vertex, S1
# L68), in die_carrier-local coords. Emitted by _open_v_moving_die. The carrier
# chain (main pivot q, then the -1.78q mimic) carries this vertex to world
# x ~= _OPEN_V_DIE_FACE_X_MM - 1.9mm at full stroke -- S1's crimp gap. Measured,
# not assumed: at head_scale=1.0 it lands at x=-4.85mm against a fixed face at
# x=-3.01mm.
_OPEN_V_MOVING_DIE_FACE_X_MM = 2.0
# Angular slack still held between the two handles at the fully closed pose.
_V_SPLAY_MARGIN_RAD = 0.04
# The forged handles bend away from the shank waist over this span (mm below the
# pivot), so the splay ramps in instead of kinking the shank at y=0.
_V_BEND_RAMP_MM = 40.0

# --- S7 turret proportions (S7 L54-L61, L99-L126) ---------------------------
_TURRET_NEST_ORBIT_MM = 16.0     # S7 _TURRET_RADIUS_MM: centre -> nest centre
_TURRET_NEST_HALF_MM = 5.5       # S7 nest block is 11x11 -> half width
_TURRET_BODY_RADIUS_MM = 21.0    # S7 _TURRET_BODY_RADIUS_MM
_TURRET_BORE_RADIUS_MM = 3.5     # S7 _TURRET_BORE_RADIUS_MM
_TURRET_THICKNESS_MM = 11.0      # S7 _TURRET_BODY_THICKNESS_MM

# The turret REPLACES the fixed die block (S7 L51-L52 "Replaces the parent's
# fixed die block"), so its ACTIVE nest -- the one at station pi, facing -x --
# must present its working face on the same plane the fixed die presents, or the
# S1 stroke lands wrong. The nest's outward face sits (orbit + half) from the
# turret axis, which pins the axis rather than leaving it free:
_TURRET_CENTER_X_MM = _OPEN_V_DIE_FACE_X_MM + _TURRET_NEST_ORBIT_MM + _TURRET_NEST_HALF_MM
_TURRET_CENTER_Y_MM = 72.0       # S7 L516 pivot height on the shank head

# The +x silhouette of the moving die block (the front chain of
# _open_v_moving_die's outline, S1 L68). Everything the cartridge wraps derives
# its front wall from this chain, so the wall clears whatever the die clears.
_OPEN_V_DIE_FRONT_CHAIN = [(-23, 38), (-2, 43), (_OPEN_V_MOVING_DIE_FACE_X_MM, 67), (-5, 79)]
# Cartridge wall thickness behind the die face it carries.
_CASSETTE_WALL_MM = 1.0


def _cassette_shell_outline():
    """S6 L88-L92 cartridge shell, front wall derived from the die's silhouette.

    S6 drew a straight front edge from (5,34) to (6,84): 4mm proud of the die
    face at x=2, and its TOP corner swings on a longer radius about the main
    pivot than the die's working vertex does, so "set the shell back from the die
    plane" is not enough -- that corner is what buries 8.1mm into the fixed die
    block at full stroke. Following the die's own front chain instead makes the
    shell a real cartridge wall that clears whatever the die clears, by
    construction, at every head_scale and jaw_open_scale (Contract 3e: derived,
    not a constant tuned until the sweep goes green).
    """
    front = [(x - _CASSETTE_WALL_MM, y) for x, y in _OPEN_V_DIE_FRONT_CHAIN]
    return [(-30, 34)] + front + [(-2, 88), (-30, 84), (-35, 58)]


# Hoisted so the cartridge and the carrier that receives it read ONE copy of
# where the cartridge begins (Contract 3c).
_S6_CASSETTE_SHELL = _cassette_shell_outline()
# The cartridge's tail edge: the carrier plate is cut back to here so a removable
# cartridge and the plate never occupy the same steel.
_CASSETTE_TAIL_Y_MM = min(y for _, y in _S6_CASSETTE_SHELL)
# Running clearance for a cartridge that is meant to slide out.
_CASSETTE_SLIDE_CLEARANCE_MM = 0.3
# S7 froze this axis at x=10mm, putting the nest face at 10-21.5 = -11.5mm, i.e.
# 8.5mm BEHIND the die plane: the moving die then sails past the nest it is
# supposed to crimp into and buries ~9.7mm into the wheel rim at full stroke.
# S7 never caught it because its own run_tests only samples the authored (open)
# pose, where the dies are 4.5mm apart -- the same blind spot _open_v_splay
# documents for S1's handles. Rule 5/6 make it this template's problem, so the
# axis is derived from the die plane above instead of copied from S7.


def _polar_gap(fixed_zone, moving_zone) -> float:
    """Angular gap (rad) about the pivot between the fixed- and moving-side
    handle geometry: how far the moving handle can swing before they meet."""
    return min(math.atan2(y, x) for x, y in fixed_zone) - max(
        math.atan2(y, x) for x, y in moving_zone
    )


def _open_v_splay(hs: float, stroke: float) -> float:
    """Half-angle each open_v handle is bent away from the V centreline.

    S1 drew a ~17-degree V but declares a 0.42 rad (24-degree) closing stroke
    (S1 L271), so its own handles interpenetrate near full close -- the source
    only survives because the compiler's motion gate skips adjacent
    parent/child pairs, and S1 L489-L501 never checks the handle pair. The
    stroke itself is load-bearing and must be kept: S1 L478-L487 ties q=0.42 to
    the dies closing to 0-3mm. So the rest V angle is what gets corrected here:
    open it until the declared stroke plus a margin actually fits.

    Derived, not tuned (Contract 3e): the gap is measured off the same grip /
    inset / stop outlines the builder emits, so it co-varies with handle_scale
    and jaw_open_scale. The forged shanks are excluded -- they are laminated in
    disjoint z bands (fixed z=[-7.5,-2.5]mm vs moving z=[2.5,7.5]mm) and
    provably never touch; the 13mm-thick grips share a z band and are the real
    constraint.
    """
    fixed_zone = [
        (x, y * hs)
        for pts in (_S1_FIXED_GRIP, _S1_FIXED_INSET, _S1_FIXED_STOP)
        for x, y in pts
        if y < 0.0
    ]
    moving_zone = [
        (x, y * hs)
        for pts in (_S1_MOV_GRIP, _S1_MOV_INSET, _S1_MOV_STOP)
        for x, y in pts
        if y < 0.0
    ]
    deficit = stroke + _V_SPLAY_MARGIN_RAD - _polar_gap(fixed_zone, moving_zone)
    return max(0.0, deficit) / 2.0


def _hzw(pts, hs: float, ds: float, splay: float = 0.0):
    """open_v shank warp: handle zone (y<0) stretches along -y by handle_scale
    and bends away from the V centreline by `splay` (signed: +y for the fixed
    handle, -y for the moving one); head zone (y>=0) scales in-plane by
    head_scale about the pivot (origin).

    The bend ramps in over `_V_BEND_RAMP_MM` so the shank leaves the pivot
    straight and curves into the grip, as a forged handle does.
    """
    out = []
    for x, y in pts:
        if y < 0.0:
            yy = y * hs
            a = splay * min(1.0, abs(yy) / _V_BEND_RAMP_MM)
            ca, sa = math.cos(a), math.sin(a)
            out.append((x * ca - yy * sa, x * sa + yy * ca))
        else:
            out.append((x * ds, y * ds))
    return out


def _sc(pts, s: float):
    return [(x * s, y * s) for x, y in pts]


def _clamp_front_x(pts, front_mm: float):
    """Clamp a die_carrier-frame outline so no vertex leads the moving die's
    working face. Used by the cassette cartridge, whose shell would otherwise
    reach the fixed die before the die it carries does."""
    return [(min(x, front_mm), y) for x, y in pts]


def _die_front_x(y_mm: float) -> float:
    """The moving die's +x silhouette at height y (mm, pre-head_scale).

    Outside the die block's own y-span the chain holds its end value: nothing the
    cartridge adds beyond the die's reach may lead the die.
    """
    chain = _OPEN_V_DIE_FRONT_CHAIN
    if y_mm <= chain[0][1]:
        return chain[0][0]
    if y_mm >= chain[-1][1]:
        return chain[-1][0]
    for (x0, y0), (x1, y1) in zip(chain, chain[1:]):
        if y0 <= y_mm <= y1:
            return x0 + (x1 - x0) * (y_mm - y0) / (y1 - y0)
    return chain[-1][0]


# ---------------------------------------------------------------------------
# Skeleton A: open_v_compound (S1 L84-L348, remapped XZ->XY)
# ---------------------------------------------------------------------------
def _build_skeleton_open_v(model, r, mats) -> dict:
    hs, ds = r.handle_scale, r.head_scale
    # Rest V opening derived from the declared stroke (see _open_v_splay). The
    # fixed handle bends toward +angle, the moving handle toward -angle, so the
    # pair opens by 2*splay about the pivot.
    splay = _open_v_splay(hs, _OPEN_V_STROKE * r.jaw_open_scale)

    fixed_body = model.part(
        "fixed_body", meta={"role": "fixed shank, fixed jaw and control mounts"}
    )
    # S1 L105-L117 fixed forged shank silhouette (mm), thickness 5 centered z=-5.
    shank_pts = _hzw(_S1_FIXED_SHANK, hs, ds, splay)
    _vis_mm(fixed_body, _poly_c(shank_pts, 5.0, -5.0), "fixed_shank", mats["steel"])
    # S1 L124-L133 orange grip shell (handle zone).
    grip_pts = _hzw(_S1_FIXED_GRIP, hs, ds, splay)
    _vis_mm(fixed_body, _poly_c(grip_pts, 13.0, -1.0), "fixed_grip", mats["grip"])
    # S1 L135-L145 rubber inset (axis-4 decoration derived from the grip outline).
    inset_pts = _hzw(_S1_FIXED_INSET, hs, ds, splay)
    _vis_mm(fixed_body, _poly_c(inset_pts, 3.0, 6.2), "fixed_rubber_inset", mats["accent"])
    # S1 L146-L154 handle stop pad.
    stop_pts = _hzw(_S1_FIXED_STOP, hs, ds, splay)
    _vis_mm(fixed_body, _poly_c(stop_pts, 10.0, -0.5), "fixed_handle_stop", mats["grip"])
    # S1 L157-L171 rivet heads + main pivot shaft (standardized hardware: unscaled radii).
    for name, x, y, rad in (
        ("main_pivot_rivet", 0.0, 0.0, 7.2),
        ("jaw_pivot_rivet", 10.0 * ds, 34.0 * ds, 5.2),
        ("ratchet_pivot_rivet", 22.0 * ds, -12.0, 4.2),
    ):
        _vis_mm(fixed_body, _disc_c(rad, 3.2, x, y, -8.8), name, mats["pin"])
    _vis_mm(fixed_body, _disc_c(5.4, 5.0, 0.0, 0.0, 0.0), "main_pivot_shaft", mats["pin"])
    # S1 L172-L181 control pivot shafts (control-mount anchors).
    rel_xy = (21.0 * ds, -13.0)
    dial_xy = (20.0 * ds, 18.0 * ds)
    _vis_mm(fixed_body, _disc_c(3.2, 1.5, rel_xy[0], rel_xy[1], -8.25), "release_pivot_shaft", mats["pin"])
    _vis_mm(fixed_body, _disc_c(2.6, 1.9, dial_xy[0], dial_xy[1], -8.25), "dial_pivot_shaft", mats["pin"])

    moving_handle = model.part(
        "moving_handle", meta={"role": "moving handle and drive shank"}
    )
    # S1 L188-L202 moving forged shank.
    mov_pts = _hzw(_S1_MOV_SHANK, hs, ds, -splay)
    _vis_mm(moving_handle, _poly_c(mov_pts, 5.0, 5.0), "moving_shank", mats["steel"])
    mov_grip_pts = _hzw(_S1_MOV_GRIP, hs, ds, -splay)
    _vis_mm(moving_handle, _poly_c(mov_grip_pts, 13.0, 1.0), "moving_grip", mats["grip"])
    mov_inset_pts = _hzw(_S1_MOV_INSET, hs, ds, -splay)
    _vis_mm(moving_handle, _poly_c(mov_inset_pts, 3.0, -6.2), "moving_rubber_inset", mats["accent"])
    _vis_mm(moving_handle, _disc_c(6.3, 3.2, 0.0, 0.0, 8.8), "moving_main_rivet", mats["pin"])
    # S1 L236-L253 carrier mount lug + pivot shaft.
    lug_pts = _sc([(-7, -3), (-13, 2), (-23, 22), (-20, 31), (-12, 28), (-4, 8)], ds)
    _vis_mm(moving_handle, _poly_c(lug_pts, 5.0, 5.0), "carrier_mount_lug", mats["steel"])
    _vis_mm(
        moving_handle, _disc_c(4.4, 4.9, -18.0 * ds, 26.0 * ds, 0.25),
        "carrier_pivot_shaft", mats["pin"],
    )
    mov_stop_pts = _hzw(_S1_MOV_STOP, hs, ds, -splay)
    _vis_mm(moving_handle, _poly_c(mov_stop_pts, 10.0, 0.5), "moving_handle_stop", mats["grip"])

    # S1 L264-L273: main closing pivot. Positive q closes the pictured open V.
    # Mating: the fixed main_pivot_shaft top face (z=+2.5mm) seats the moving
    # shank bottom face (z=+2.5mm) as adjacent laminations.
    # Axis sign: S1 authored the silhouette in XZ with axis (0,-1,0); this
    # template remaps (x,z)->(x,y), i.e. a Y<->Z swap, which is a REFLECTION
    # (det=-1). A rotation axis is an axial vector, so it takes an extra sign
    # flip under the mirror: source -Y -> +z here (not -z). Verified against S1:
    # the moving tip at (-68,-225)mm sweeps to x=+29.7mm, toward the fixed grip
    # (x in [4,48]mm) -- the closing direction. Same rule for every S1/S6/S7
    # joint below; S2/S3/S8 were authored natively in XY and are NOT flipped.
    model.articulation(
        "main_closing_pivot",
        ArticulationType.REVOLUTE,
        parent=fixed_body,
        child=moving_handle,
        origin=Origin(),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(
            lower=0.0, upper=_OPEN_V_STROKE * r.jaw_open_scale, effort=220.0, velocity=1.4
        ),
        mating=MatingContract(
            parent_face_geometry="main_pivot_shaft",
            parent_face_side="positive_z",
            child_face_geometry="moving_shank",
            child_face_side="negative_z",
            contact_tol=0.0012,
        ),
        meta={"function": "closes the two long handles from the open-V pose"},
    )

    # S1 L276-L318: central die carrier (moving jaw), mimic-coupled to the handle.
    die_carrier = model.part("die_carrier", meta={"role": "moving jaw / crimp die carrier"})
    carrier_pts = _sc([(-4, -4), (9, 3), (14, 30), (4, 54), (-18, 50), (-25, 23), (-17, 1)], ds)
    carrier_thick = 10.0 if r.die_head == "cassette_die" else 4.0  # S6 L330 thickened carrier
    carrier_plate = _poly_c(carrier_pts, carrier_thick, 0.0)
    if r.die_head == "cassette_die":
        # A removable cartridge and the plate cannot occupy the same steel. S6
        # left the plate solid and let the cartridge intersect it through its
        # full 10mm ("Y offsets place them inside the thickened carrier plate so
        # they read as one piece" -- S6 L337); a whole-part overlap waiver was
        # hiding that here. Cut the plate back to the cartridge's tail edge so
        # the cartridge occupies the jaw's business end and the plate is the
        # backing that carries it (Contract 3c: _CASSETTE_TAIL_Y_MM is the one
        # copy of where the cartridge starts). The rails below do the capture.
        keep_y = (_CASSETTE_TAIL_Y_MM - _CASSETTE_SLIDE_CLEARANCE_MM) * ds
        carrier_plate = carrier_plate.cut(
            cq.Workplane("XY")
            .box(400.0, 400.0, 80.0, centered=(True, False, True))
            .translate((0.0, keep_y, 0.0))
        )
    _vis_mm(die_carrier, carrier_plate, "die_carrier_plate", mats["steel"])
    _vis_mm(die_carrier, _disc_c(5.0, 3.0, 0.0, 0.0, 3.4 if carrier_thick < 5 else 6.0),
            "carrier_pivot_rivet", mats["pin"])
    _vis_mm(die_carrier, _disc_c(3.8, 4.4, 6.0 * ds, 6.0 * ds, 4.2 if carrier_thick < 5 else 7.0),
            "drive_pivot_shaft", mats["pin"])
    model.articulation(
        "handle_to_die_carrier",
        ArticulationType.REVOLUTE,
        parent=moving_handle,
        child=die_carrier,
        origin=Origin(xyz=(-0.018 * ds, 0.026 * ds, 0.0)),
        # S1 source axis (0,+1,0) -> mirrored to -z (see main_closing_pivot note).
        # Multiplier stays +1.78: source net carrier spin is +0.78q about +Y_s,
        # which the mirror maps to -0.78q about +z_t = (+q from the handle) +
        # (-1.78q here). Joint values are unchanged by the mirror, so the source
        # limits [0, 0.76] carry over verbatim.
        axis=(0.0, 0.0, -1.0),
        motion_limits=MotionLimits(lower=0.0, upper=0.76, effort=180.0, velocity=1.2),
        mimic=Mimic(joint="main_closing_pivot", multiplier=1.78, offset=0.0),
        meta={"function": "compound jaw correction coupled to the closing handle"},
    )

    # S1 L321-L348: asymmetric outer drive link (visible compound toggle).
    drive_link = model.part("drive_link", meta={"role": "asymmetric compound linkage plate"})
    link_pts = _sc([(-2, -7), (14, -5), (37, -18), (48, -8), (43, 8), (18, 13), (0, 7)], ds)
    link_z = 8.0 if carrier_thick < 5 else 9.0
    _vis_mm(drive_link, _poly_c(link_pts, 3.2, link_z), "asymmetric_link_plate", mats["steel"])
    _vis_mm(drive_link, _disc_c(4.8, 2.4, 0.0, 0.0, link_z + 2.8), "link_rivet", mats["pin"])
    model.articulation(
        "carrier_to_drive_link",
        ArticulationType.REVOLUTE,
        parent=die_carrier,
        child=drive_link,
        origin=Origin(xyz=(0.006 * ds, 0.006 * ds, 0.0)),
        axis=(0.0, 0.0, -1.0),  # S1 source axis (0,+1,0), mirrored (see above).
        motion_limits=MotionLimits(lower=-0.22, upper=0.18, effort=120.0, velocity=1.8),
        meta={"function": "visible compound toggle link motion"},
    )

    return {
        "release_mount": InterfaceSpec(
            interface_name="release_mount",
            part_name="fixed_body",
            visual_name="release_pivot_shaft",
            face_side="negative_z",
            anchor_local=(rel_xy[0] / 1000.0, rel_xy[1] / 1000.0, -0.009),
        ),
        "dial_mount": InterfaceSpec(
            interface_name="dial_mount",
            part_name="fixed_body",
            visual_name="dial_pivot_shaft",
            face_side="negative_z",
            anchor_local=(dial_xy[0] / 1000.0, dial_xy[1] / 1000.0, -0.0089),
        ),
        "fixed_body": fixed_body,
        "moving_handle": moving_handle,
        "die_carrier": die_carrier,
        "carrier_thick": carrier_thick,
    }


# Minimum lip of die steel left standing between two adjacent nests.
_OPEN_V_NEST_WEB_MM = 1.2


def _nest_radius_scale(y0: float, y1: float, r0: float, r1: float, n: int) -> float:
    """How much the nest ladder must shrink so N nests fit the die block's face.

    The ladder's span and end radii are S1's (L55-L63), but the pitch is not free
    once N grows: two adjacent nests whose radii sum past the pitch merge and cut
    the block's front lip clean through. At N=4 the S1 radii sum to 9.1mm against
    an 8mm pitch, which severs the fixed die into two solids at EVERY head_scale
    (an island, not a near-miss). Nest radius is therefore a relation between
    neighbouring nests and the block face, not a frozen constant (Contract 3e).

    Never enlarges past the source: at the S1 anchor N=3 this returns exactly 1.0,
    so the anchor geometry is bit-identical and only the extrapolated N=4 shrinks.
    """
    if n < 2:
        return 1.0
    pitch = (y1 - y0) / (n - 1)
    worst = max(
        _lerp(r0, r1, i / (n - 1)) + _lerp(r0, r1, (i + 1) / (n - 1))
        for i in range(n - 1)
    )
    if worst <= 0.0:
        return 1.0
    return min(1.0, (pitch - _OPEN_V_NEST_WEB_MM) / worst)


# open_v die-nest cutter shared by integral / cassette heads (S1 L49-L81).
def _open_v_fixed_die(ds: float, n_pairs: int):
    # The (_OPEN_V_DIE_FACE_X_MM, 68) vertex IS the fixed working face: every
    # open_v head derives its own working plane from that one constant.
    block = _poly_c(
        _sc([(0, 48), (24, 52), (29, 82), (20, 96), (0, 93), (_OPEN_V_DIE_FACE_X_MM, 68)], ds),
        11.0, -1.5,
    )
    k = _nest_radius_scale(60.0, 84.0, 4.8, 3.3, n_pairs)
    for i in range(n_pairs):
        t = i / max(1, n_pairs - 1) if n_pairs > 1 else 0.5
        y = _lerp(60.0, 84.0, t) * ds
        rad = _lerp(4.8, 3.3, t) * k * ds
        cutter = cq.Workplane("XY").center(-1.5 * ds, y).circle(rad).extrude(9.0, both=True)
        block = block.cut(cutter)
    return block


def _open_v_moving_die(ds: float, n_pairs: int):
    # The (_OPEN_V_MOVING_DIE_FACE_X_MM, 67) vertex IS the moving working face;
    # the cassette shell derives its front boundary from that one constant so it
    # can never lead the die into the fixed block.
    block = _poly_c(
        _sc(
            [(-23, 38), (-2, 43), (_OPEN_V_MOVING_DIE_FACE_X_MM, 67), (-5, 79), (-27, 76), (-31, 56)],
            ds,
        ),
        9.0, 1.0,
    )
    k = _nest_radius_scale(49.0, 70.0, 4.4, 3.0, n_pairs)
    for i in range(n_pairs):
        t = i / max(1, n_pairs - 1) if n_pairs > 1 else 0.5
        y = _lerp(49.0, 70.0, t) * ds
        rad = _lerp(4.4, 3.0, t) * k * ds
        cutter = cq.Workplane("XY").center(0.5 * ds, y).circle(rad).extrude(8.0, both=True)
        block = block.cut(cutter)
    return block


def _build_head_integral(model, r, mats, sk) -> None:
    """S1 L49-L81 + L119-L123 + L289-L293: opposed multi-nest die pair as
    non-articulating visuals on fixed_body / die_carrier (Rule 1)."""
    ds = r.head_scale
    _vis_mm(sk["fixed_body"], _open_v_fixed_die(ds, r.nest_pair_count), "fixed_crimp_die", mats["die"])
    _vis_mm(sk["die_carrier"], _open_v_moving_die(ds, r.nest_pair_count), "moving_crimp_die", mats["die"])


def _cassette_cartridge_solid(ds: float, n_pairs: int):
    """The removable cartridge, in die_carrier-local mm coords (S6 L84-L110).

    Single-sourced (Contract 3c): the die_carrier mills its receiving pocket with
    this exact solid, so the pocket and the cartridge can never drift apart.
    """
    # Shell wall follows the die's front silhouette (see _cassette_shell_outline).
    shell = _poly_c(_sc(_S6_CASSETTE_SHELL, ds), 4.0, 3.5)
    # Rail tongues sit in the die's shadow: clamp them behind the die's front at
    # their own y-band rather than to S6's flat x=3, which leads the die by 5mm.
    rail_front = _die_front_x(41.0) - _CASSETTE_WALL_MM
    rail_pts = _clamp_front_x([(-28, 36), (3, 36), (3, 41), (-28, 41)], rail_front)
    rail_a = _poly_c(_sc(rail_pts, ds), 2.0, 6.5)
    rail_b = _poly_c(_sc(rail_pts, ds), 2.0, -4.5)
    notch = _poly_c(_sc([(-10, 82), (-3, 82), (-3, 88), (-10, 88)], ds), 6.0, 3.5)
    body = shell.union(rail_a).union(rail_b).union(notch)
    return body.union(_open_v_moving_die(ds, n_pairs))


def _build_head_cassette(model, r, mats, sk) -> None:
    """S6 L84-L127 + L328-L456: removable die cassette captured in carrier rails
    plus a spring latch lever."""
    ds = r.head_scale
    _vis_mm(sk["fixed_body"], _open_v_fixed_die(ds, r.nest_pair_count), "fixed_crimp_die", mats["die"])

    # Rail guides on the carrier face (S6 L337-L348); extended to the latch boss
    # height so the latch pivot is seated on real carrier hardware, and rooted
    # back to y=20mm so they grow out of the plate that survives the tail cut
    # instead of cantilevering off its 1mm edge. These straddle the cartridge's
    # tongues in z, which is the actual capture -- see the element-scoped
    # allowances in run_tests.
    for i, z_off in enumerate((3.8, -3.8)):
        _vis_mm(
            sk["die_carrier"],
            _poly_c(_sc([(-26, 20), (3, 20), (3, 84), (-26, 84)], ds), 2.0, z_off),
            f"cassette_rail_{i}",
            mats["steel"],
        )

    # Removable die cartridge (S6 L84-L110 + L407-L428). FIXED articulation is
    # legitimate here: the cassette is a physically separate cartridge captured
    # in the carrier rails (a composed sub-assembly, not fused decoration).
    cassette = model.part("die_cassette", meta={"role": "removable die cartridge"})
    anchor = (-0.012 * ds, 0.045 * ds, 0.0)  # on the rail span and inside the shell footprint
    ax_mm, ay_mm = anchor[0] * 1000.0, anchor[1] * 1000.0
    body = _cassette_cartridge_solid(ds, r.nest_pair_count)
    _vis_mm(cassette, body.translate((-ax_mm, -ay_mm, 0.0)), "cassette_body", mats["pin"])
    model.articulation(
        "carrier_to_cassette",
        ArticulationType.FIXED,
        parent=sk["die_carrier"],
        child=cassette,
        origin=Origin(xyz=anchor),
        meta={"function": "die cassette captured in carrier rails by the spring latch"},
    )

    # Spring latch lever (S6 L113-L127 + L431-L456).
    latch = model.part("cassette_latch", meta={"role": "cassette retention latch"})
    lever = _poly_c(
        _sc([(0, 0), (5, -1), (14, -7), (16, -13), (12, -15), (7, -11), (-1, -5), (-3, -2)], ds),
        2.5, 0.5,
    )
    bump = cq.Workplane("XY").center(12.0 * ds, -9.0 * ds).circle(1.8).extrude(1.25, both=True).translate((0, 0, 0.5))
    _vis_mm(latch, lever.union(bump), "latch_lever_body", mats["accent"])
    _vis_mm(latch, _disc_c(2.2, 3.0, 0.0, 0.0, 0.5), "latch_pivot_pin", mats["pin"])
    model.articulation(
        "carrier_to_latch",
        ArticulationType.REVOLUTE,
        parent=sk["die_carrier"],
        child=latch,
        origin=Origin(xyz=(-0.007 * ds, 0.082 * ds, 0.0)),
        axis=(0.0, 0.0, -1.0),  # S6 L453 source axis (0,+1,0), mirrored (XZ->XY swap).
        motion_limits=MotionLimits(lower=-0.35, upper=0.55, effort=6.0, velocity=5.0),
        meta={"function": "spring latch pivots to capture or release the die cassette"},
    )


def _build_head_turret(model, r, mats, sk) -> None:
    """S7 L49-L126 + L476-L524: indexed rotating die turret on the fixed shank."""
    ds = r.head_scale
    n = r.turret_nest_count
    _vis_mm(sk["die_carrier"], _open_v_moving_die(ds, 3), "moving_crimp_die", mats["die"])

    # Single-sourced turret axis (see _TURRET_CENTER_X_MM): the boss, the pivot
    # shaft, the wheel and the index joint all read this one point, so the mount
    # travels with the axis instead of being re-stated three times.
    cx, cy = _TURRET_CENTER_X_MM, _TURRET_CENTER_Y_MM

    # Mount boss + pivot shaft on the fixed shank head (S7 L183-L193, L252-L257).
    # S7's boss outline, restated relative to the axis it mounts. Its -x lobe is
    # stretched back to the shank centreline so the pad still lands on real shank
    # hardware once the axis moves outboard (it overlaps the shank head across
    # x=[8.5,16.7]mm at the axis height).
    boss_pts = _sc(
        [(cx - 18.5, cy - 10), (cx + 8, cy - 8), (cx + 10, cy),
         (cx + 8, cy + 8), (cx - 18.5, cy + 10), (cx - 21.5, cy)],
        ds,
    )
    _vis_mm(sk["fixed_body"], _poly_c(boss_pts, 9.0, -3.0), "turret_mount_boss", mats["steel"])
    _vis_mm(sk["fixed_body"], _disc_c(3.8, 14.0, cx * ds, cy * ds, 0.0), "turret_pivot_shaft", mats["pin"])

    turret = model.part("die_turret", meta={"role": "indexed die selection turret"})
    body_r, bore_r, thick = _TURRET_BODY_RADIUS_MM * ds, _TURRET_BORE_RADIUS_MM, _TURRET_THICKNESS_MM
    wheel = cq.Workplane("XY").circle(body_r).circle(bore_r).extrude(thick / 2.0, both=True)
    for i in range(n):
        mid = math.pi - (i + 0.5) * 2.0 * math.pi / n
        hx, hy = 12.0 * ds * math.cos(mid), 12.0 * ds * math.sin(mid)
        wheel = wheel.cut(
            cq.Workplane("XY").center(hx, hy).circle(3.2).extrude(thick, both=True)
        )
        station = math.pi - i * 2.0 * math.pi / n
        dx = (body_r - 1.0) * math.cos(station)
        dy = (body_r - 1.0) * math.sin(station)
        wheel = wheel.cut(
            cq.Workplane("XY").center(dx, dy).circle(1.6).extrude(thick, both=True)
        )
    _vis_mm(turret, wheel, "turret_wheel", mats["die"])
    _vis_mm(turret, _disc_c(5.0, 2.8, 0.0, 0.0, 0.0), "turret_retaining_rivet", mats["pin"])

    # Rim nest blocks: shared construction, rotated per station (S7 L99-L126).
    # The cavity is cut on the block's -x face at -_TURRET_NEST_HALF_MM, so the
    # station-pi nest opens exactly on the working plane _TURRET_CENTER_X_MM was
    # solved for.
    half, orbit = _TURRET_NEST_HALF_MM * ds, _TURRET_NEST_ORBIT_MM * ds
    for i in range(n):
        t = i / max(1, n - 1)
        cav = _lerp(4.8, 2.8, t) * ds
        nest = cq.Workplane("XY").rect(2.0 * half, 2.0 * half).extrude(thick / 2.0, both=True)
        nest = nest.cut(
            cq.Workplane("XY").center(-half, 0.0).circle(cav).extrude(thick + 2.0, both=True)
        )
        station = math.pi - i * 2.0 * math.pi / n
        nest = nest.rotate((0, 0, 0), (0, 0, 1), math.degrees(station - math.pi))
        nest = nest.translate((orbit * math.cos(station), orbit * math.sin(station), 0.0))
        _vis_mm(turret, nest, f"nest_{i}", mats["die"])

    model.articulation(
        "turret_index",
        ArticulationType.REVOLUTE,
        parent=sk["fixed_body"],
        child=turret,
        origin=Origin(xyz=(cx * ds / 1000.0, cy * ds / 1000.0, 0.0)),
        axis=(0.0, 0.0, 1.0),  # S7 L516 source axis (0,-1,0), mirrored (XZ->XY swap).
        motion_limits=MotionLimits(
            lower=0.0, upper=2.0 * math.pi * (n - 1) / n, effort=12.0, velocity=3.0
        ),
        meta={"function": "rotates the turret wheel to select the crimp nest size"},
    )


# ---------------------------------------------------------------------------
# Skeleton B: layered_ratchet_frame (S2 L114-L237; jaw geometry from die slot)
# ---------------------------------------------------------------------------
def _layered_side_plate(ds: float):
    """S2 L92-L111 open-window cheek plate."""
    pts = _sc(
        [
            (-0.119, -0.016), (-0.112, -0.031), (-0.090, -0.041), (-0.020, -0.036),
            (0.020, -0.018), (0.023, 0.014), (-0.018, 0.035), (-0.092, 0.041), (-0.113, 0.027),
        ],
        ds,
    )
    plate = _poly_b(pts, 0.004, z0=-0.008, fillet=0.0025)
    plate = _cut_round_holes(
        plate,
        [(0.0, 0.0, 0.0050), (-0.044 * ds, -0.022 * ds, 0.0033),
         (-0.045 * ds, 0.023 * ds, 0.0033), (-0.093 * ds, 0.0, 0.0030)],
    )
    window = (
        cq.Workplane("XY")
        .box(0.026, 0.014, 0.020, centered=(True, True, False))
        .translate((-0.025 * ds, 0.0, -0.012))
    )
    return plate.cut(window)


_LAYERED_JAW_ROOT_EDGE = ((-0.114, 0.004), (0.014, 0.006))  # S2 L50-L52 jaw root edge
# How far the pivot boss bites into the jaw root, so the seat is real contact
# rather than a tangency that rounds the wrong way.
_LAYERED_JAW_SEAT_EMBED_M = 0.0005


def _layered_jaw_root_y(ds: float) -> float:
    """Where the jaw plate's root edge crosses the pivot axis (x=0), in metres.

    The upper jaw is a separate part pivoting on the main axis, and this is the
    ONLY place its geometry comes near the grounded body -- the die pin rides in
    a clearance slot 2.5mm wider than itself, so it cannot seat the jaw. The
    pivot boss radius is derived from this (see _build_skeleton_layered): the
    outline scales with head_scale while standardized pin/boss radii do not, so
    a frozen boss radius seats the jaw only near head_scale=1.0 and lets it float
    above ~1.003 (Contract 3e).
    """
    (x0, y0), (x1, y1) = _LAYERED_JAW_ROOT_EDGE
    return (y0 + (y1 - y0) * (0.0 - x0) / (x1 - x0)) * ds


def _layered_jaw_outline(upper: bool, ds: float):
    """S2 L50-L89 / S4 L63-L98 jaw plate silhouette."""
    if upper:
        pts = [(-0.114, 0.004), (-0.120, 0.015), (-0.111, 0.032), (-0.092, 0.041),
               (-0.025, 0.036), (0.010, 0.020), (0.014, 0.006)]
    else:
        pts = [(-0.114, -0.004), (-0.120, -0.015), (-0.111, -0.032), (-0.092, -0.041),
               (-0.025, -0.036), (0.010, -0.020), (0.014, -0.006)]
    plate = _poly_b(_sc(pts, ds), 0.004, z0=0.0, fillet=0.0015)
    sign = 1.0 if upper else -1.0
    # pivot clearance slot: widened vs source pin r0.0045 so the mimic-driven
    # die swing (up to ~0.15 rad about the main pivot) clears the fixed pin.
    plate = _cut_round_holes(plate, [(0.0, sign * 0.014 * ds, 0.0070)])
    if upper:
        plate = _cut_round_holes(plate, [(-0.082 * ds, 0.026 * ds, 0.0032)])
    return plate


def _layered_apply_stations(plate, upper: bool, ds: float, n: int):
    """Regular-pitch die stations (S5 L50-L80): round pockets then stepped reliefs."""
    sign = 1.0 if upper else -1.0
    pitch = 0.018 * ds
    x0 = -0.098 * ds
    n_rect = 2 if n >= 5 else 1
    n_round = n - n_rect
    for i in range(n):
        x = x0 + i * pitch
        if i < n_round:
            t = i / max(1, n_round - 1) if n_round > 1 else 0.0
            rad = _lerp(0.0065, 0.0040, t) * ds
            plate = _cut_round_holes(plate, [(x, sign * 0.004 * ds, rad)])
        else:
            t = (i - n_round) / max(1, n_rect - 1) if n_rect > 1 else 0.0
            w = _lerp(0.010, 0.008, t) * ds
            d = _lerp(0.0040, 0.0032, t) * ds
            y = sign * (0.004 * ds + d / 2.0)
            relief = (
                cq.Workplane("XY")
                .box(w, d, 0.020, centered=(True, True, False))
                .translate((x, y, -0.008))
            )
            plate = plate.cut(relief)
    return plate


def _layered_apply_hex(plate, upper: bool, ds: float):
    """S4 L50-L60 single centered hexagonal die station."""
    sign = 1.0 if upper else -1.0
    af = 0.0055 * ds
    circumscribed_d = af * 2.0 / math.sqrt(3.0)
    cutter = (
        cq.Workplane("XY")
        .center(-0.065 * ds, sign * 0.004 * ds)
        .polygon(6, circumscribed_d)
        .extrude(0.012)
        .translate((0, 0, -0.004))
    )
    return plate.cut(cutter)


def _build_skeleton_layered(model, r, mats) -> dict:
    hs, ds = r.handle_scale, r.head_scale

    fixed_body = model.part("fixed_body", meta={"role": "root handle and lower cheek plate"})
    shank_len = 0.174 * hs
    root_shank = _capsule(shank_len, 0.016, 0.006, x0=-0.004, z0=-0.007, angle=-0.16)
    root_shank = root_shank.union(_layered_side_plate(ds))
    _vis_m(fixed_body, root_shank, "fixed_shank", mats["steel"])
    grip_w = 0.022 * r.grip_thickness_scale
    grip_len = max(0.08, (shank_len - 0.004) - 0.043)  # grip caps the shank end (derived)
    _vis_m(fixed_body, _capsule(grip_len, grip_w, 0.008, x0=0.043, z0=-0.008, angle=-0.16),
           "fixed_grip", mats["grip"])
    # Pivot hardware (S2 L146-L179).
    fixed_body.visual(Cylinder(radius=0.0046, length=0.020), origin=Origin(xyz=(0.0, 0.0, 0.002)),
                      material=mats["pin"], name="main_pivot_pin", material_class_id="metal.stainless_matte")
    fixed_body.visual(Cylinder(radius=0.0066, length=0.0016), origin=Origin(xyz=(0.0, 0.0, -0.0088)),
                      material=mats["pin"], name="main_pivot_head", material_class_id="metal.stainless_matte")
    # thrust washer: single-sourced pivot seat bridging cheek plate and moving
    # shank; its +z face is the MatingContract seat for the moving handle, and
    # its rim is what seats the upper_die jaw (the only contact that grounds it).
    # Radius derives from the jaw root so the seat survives head_scale rather
    # than holding by 0.019mm at head_scale=1.0 and floating above ~1.003.
    washer_r = _layered_jaw_root_y(ds) + _LAYERED_JAW_SEAT_EMBED_M
    fixed_body.visual(Cylinder(radius=washer_r, length=0.009), origin=Origin(xyz=(0.0, 0.0, 0.0005)),
                      material=mats["pin"], name="pivot_thrust_washer", material_class_id="metal.stainless_matte")
    for y, name in ((-0.014 * ds, "lower_die_pin"), (0.014 * ds, "upper_die_pin")):
        fixed_body.visual(Cylinder(radius=0.0045, length=0.014), origin=Origin(xyz=(0.0, y, -0.001)),
                          material=mats["pin"], name=name, material_class_id="metal.stainless_matte")
        fixed_body.visual(Cylinder(radius=0.0062, length=0.0015), origin=Origin(xyz=(0.0, y, -0.00875)),
                          material=mats["pin"], name=f"{name}_head", material_class_id="metal.stainless_matte")

    moving_handle = model.part("moving_handle", meta={"role": "upper handle / ratchet shank"})
    mov_len = 0.172 * hs
    moving_core = _capsule(mov_len, 0.015, 0.005, x0=-0.003, z0=0.005)
    moving_core = _cut_round_holes(
        moving_core, [(0.0, 0.0, 0.0046), (0.036, 0.0, 0.0032), (0.058, -0.001, 0.0028)]
    )
    _vis_m(moving_handle, moving_core, "moving_shank", mats["steel"])
    mov_grip_len = max(0.08, (mov_len - 0.003) - 0.043)
    _vis_m(moving_handle, _capsule(mov_grip_len, grip_w, 0.008, x0=0.043, z0=0.004),
           "moving_grip", mats["grip"])
    moving_handle.visual(Cylinder(radius=0.0032, length=0.005), origin=Origin(xyz=(0.036, 0.0, 0.0125)),
                         material=mats["pin"], name="linkage_pivot_pin", material_class_id="metal.stainless_matte")
    moving_handle.visual(Cylinder(radius=0.0028, length=0.005), origin=Origin(xyz=(0.058, -0.001, 0.0125)),
                         material=mats["pin"], name="release_pivot_pin", material_class_id="metal.stainless_matte")

    model.articulation(
        "main_closing_pivot",
        ArticulationType.REVOLUTE,
        parent=fixed_body,
        child=moving_handle,
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, 0.0, 0.17)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(
            effort=320.0, velocity=2.5,
            lower=-0.12 * r.jaw_open_scale, upper=0.22 * r.jaw_open_scale,
        ),
        mating=MatingContract(
            parent_face_geometry="pivot_thrust_washer",
            parent_face_side="positive_z",
            child_face_geometry="moving_shank",
            child_face_side="negative_z",
            contact_tol=0.0012,
        ),
        meta={"function": "negative motion closes the jaws, positive opens the handles"},
    )
    return {
        "fixed_body": fixed_body,
        "moving_handle": moving_handle,
        "release_mount": None,  # layered controls ride the moving-shank pins
        "dial_mount": None,
    }


def _build_head_layered(model, r, mats, sk, *, hex_single: bool) -> None:
    """S2/S4/S5 jaw plates: lower jaw folds into fixed_body (it never moves);
    the upper jaw is a REVOLUTE mimic-driven part with the locator tab fused in
    (S2 L279-L300, Rule 1)."""
    ds = r.head_scale
    lower = _layered_jaw_outline(False, ds)
    upper = _layered_jaw_outline(True, ds)
    if hex_single:
        lower = _layered_apply_hex(lower, False, ds)
        upper = _layered_apply_hex(upper, True, ds)
        profiles = 1
    else:
        n = r.die_station_count
        lower = _layered_apply_stations(lower, False, ds, n)
        upper = _layered_apply_stations(upper, True, ds, n)
        profiles = n
    _vis_m(sk["fixed_body"], lower.translate((0, 0, -0.004)), "lower_crimp_profiles",
           mats["dark"], tol=0.00055)

    upper_die = model.part("upper_die", meta={"profiles": profiles, "layer": "upper"})
    _vis_m(upper_die, upper, "upper_crimp_profiles", mats["dark"], tol=0.00055)
    # Locator tab (S2 L279-L300) fused into the upper die: it does not
    # articulate relative to the die plate.
    locator_tab = (
        cq.Workplane("XY").rect(0.024, 0.010).extrude(0.002)
        .translate((-0.073 * ds, 0.026 * ds, 0.004))
    )
    locator_tab = locator_tab.union(
        cq.Workplane("XY").center(-0.082 * ds, 0.026 * ds).circle(0.0027).extrude(0.008)
        .translate((0, 0, -0.003))
    )
    _vis_m(upper_die, locator_tab, "locator_stop", mats["pin"], tol=0.0004)

    model.articulation(
        "die_pivot",
        ArticulationType.REVOLUTE,
        parent=sk["fixed_body"],
        child=upper_die,
        origin=Origin(),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=500.0, velocity=1.5, lower=-0.15, upper=0.07),
        mimic=Mimic(joint="main_closing_pivot", multiplier=-0.65, offset=0.0),
        meta={"function": "upper die closes against the lower profiles (compound action)"},
    )


def _build_controls_pawl(model, r, mats, sk) -> None:
    """S2 L241-L275: ratchet bridge link + manual release pawl on the moving shank."""
    link = model.part("ratchet_link", meta={"role": "compound ratchet bridge"})
    link_shape = _capsule(0.050, 0.010, 0.003, x0=0.0, z0=0.0, angle=2.86)
    link_shape = _cut_round_holes(link_shape, [(0.0, 0.0, 0.00315)])
    _vis_m(link, link_shape, "ratchet_bridge", mats["accent"], tol=0.00045)
    model.articulation(
        "linkage_pivot",
        ArticulationType.REVOLUTE,
        parent=sk["moving_handle"],
        child=link,
        origin=Origin(xyz=(0.036, 0.0, 0.015)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=80.0, velocity=4.0, lower=-0.16, upper=0.14),
    )

    pawl = model.part("release_pawl", meta={"role": "manual ratchet release"})
    pawl_shape = _capsule(0.027, 0.007, 0.003, x0=0.0, z0=0.0, angle=2.42)
    pawl_shape = _cut_round_holes(pawl_shape, [(0.0, 0.0, 0.0027)])
    _vis_m(pawl, pawl_shape, "release_lever", mats["steel"], tol=0.00045)
    model.articulation(
        "release_pivot",
        ArticulationType.REVOLUTE,
        parent=sk["moving_handle"],
        child=pawl,
        origin=Origin(xyz=(0.058, -0.001, 0.015)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=12.0, velocity=5.0, lower=-0.24, upper=0.20),
    )


# ---------------------------------------------------------------------------
# Skeleton C: inline_press_frame (S3 L92-L399 / S8 L117-L322)
# ---------------------------------------------------------------------------
def _inline_head_warp(pts, ds: float):
    """In-plane scale about the main pivot (62,8) mm for head-zone points; the
    handle zone (x>111) stretches away from x=111 by handle_scale separately."""
    return [(62.0 + (x - 62.0) * ds, 8.0 + (y - 8.0) * ds) for x, y in pts]


def _build_skeleton_inline(model, r, mats) -> dict:
    hs, ds = r.handle_scale, r.head_scale
    gts = r.grip_thickness_scale

    def warp(pts):
        out = []
        for x, y in pts:
            if x > 111.0:
                x = 111.0 + (x - 111.0) * hs
            else:
                x, y = 62.0 + (x - 62.0) * ds, 8.0 + (y - 8.0) * ds
            out.append((x, y))
        return out

    fixed_body = model.part("fixed_body", meta={"role": "layered head plate and lower shank"})
    main_outline = warp(
        [(10, -30), (4, -25), (1, -15), (2, 13), (8, 25), (22, 30), (72, 30), (92, 23),
         (111, 11), (285, -14), (290, -21), (286, -29), (273, -32), (111, -22), (87, -28), (35, -32)]
    )
    _vis_mm(fixed_body, _poly_b(main_outline, 4.2, 0.0), "fixed_shank", mats["steel"])
    # Raised second head layer (S3 L128-L142).
    hx, hy = 62.0 + (57.5 - 62.0) * ds, 8.0 + (0.5 - 8.0) * ds
    upper_head = (
        cq.Workplane("XY").box(103.0 * ds, 47.0 * ds, 3.2).translate((hx, hy, 5.8))
        .union(
            cq.Workplane("XY")
            .center(62.0 + (16.0 - 62.0) * ds, 8.0 * (1 - ds))
            .circle(24.0 * ds).extrude(3.2).translate((0, 0, 4.2))
        )
    )
    _vis_mm(fixed_body, upper_head, "raised_head_layer", mats["steel"])
    # Hardened cutting + stripping edges (S3 L175-L198): retained functional
    # identity features of this frame family.
    _vis_mm(fixed_body, _poly_b(_inline_head_warp([(24, -24), (52, -21), (57, -12), (26, -13)], ds), 4.6, 7.4),
            "cutting_jaw_support", mats["steel"])
    _vis_mm(fixed_body, _poly_b(_inline_head_warp([(31, -18), (54, -16), (54, -13), (31, -15)], ds), 1.1, 12.0),
            "cutting_blade", mats["die"])
    _vis_mm(fixed_body, _poly_b(_inline_head_warp([(45, 18), (64, 18), (62, 21), (47, 21)], ds), 1.5, 10.5),
            "stripping_blade", mats["die"])
    sx, sy = 62.0 + (54.0 - 62.0) * ds, 8.0 + (17.0 - 8.0) * ds
    fixed_body.visual(Box((0.020 * ds, 0.008 * ds, 0.006)),
                      origin=Origin(xyz=(sx / 1000.0, sy / 1000.0, 0.009)),
                      material=mats["steel"], name="stripper_support", material_class_id="metal.steel_bare")

    # Lower grip with finger scallops (axis-4 decoration count, S3 L200-L216;
    # scallops are boolean-cut from the final grip bar so they conform to it).
    gx0, gx1 = 106.0, 111.0 + (292.0 - 111.0) * hs
    gy0, gy1 = -10.0 - 25.0 * gts, -10.0
    grip_bar = _rounded_bar(gx0, gx1, gy0, gy1, 8.5, 2.5)
    for i in range(r.scallop_count):
        t = (i + 1.0) / (r.scallop_count + 1.0)
        cx = _lerp(gx0 + 0.45 * (gx1 - gx0), gx1 - 0.06 * (gx1 - gx0), t)
        grip_bar = grip_bar.cut(cq.Workplane("XY").center(cx, gy0).circle(4.0).extrude(12.0))
    _vis_mm(fixed_body, grip_bar, "fixed_grip", mats["grip"])
    _vis_mm(fixed_body, _poly_b([(106, -10), (106 + 44 * hs, -8), (106 + 39 * hs, -14), (110, -18)], 3.0, 11.0),
            "fixed_red_accent", mats["accent"])

    # Main pivot pin + cap + fasteners + control bosses (S3 L219-L257).
    fixed_body.visual(Cylinder(radius=0.005, length=0.014), origin=Origin(xyz=(0.062, 0.008, 0.0112)),
                      material=mats["pin"], name="main_pivot_pin", material_class_id="metal.stainless_matte")
    fixed_body.visual(Cylinder(radius=0.007, length=0.001), origin=Origin(xyz=(0.062, 0.008, 0.0175)),
                      material=mats["pin"], name="main_pivot_cap", material_class_id="metal.stainless_matte")
    for name, x, y, rad, z, length in (
        ("nose_rivet", 62.0 + (18 - 62.0) * ds, 8.0 + (13 - 8.0) * ds, 3.6, 9.0, 4.0),
        ("nose_screw", 62.0 + (24 - 62.0) * ds, 8.0 + (-19 - 8.0) * ds, 2.8, 12.0, 3.0),
        ("shank_rivet", 105.0, -11.0, 2.7, 11.0, 3.0),
    ):
        fixed_body.visual(Cylinder(radius=rad / 1000.0, length=length / 1000.0),
                          origin=Origin(xyz=(x / 1000.0, y / 1000.0, z / 1000.0)),
                          material=mats["pin"], name=name, material_class_id="metal.stainless_matte")
    rel_xy = (0.143, -0.002)
    dial_xy = (0.127, 0.0)
    fixed_body.visual(Cylinder(radius=0.0055, length=0.0078),
                      origin=Origin(xyz=(rel_xy[0], rel_xy[1], 0.0081)),
                      material=mats["steel"], name="ratchet_boss", material_class_id="metal.steel_bare")
    fixed_body.visual(Cylinder(radius=0.006, length=0.0078),
                      origin=Origin(xyz=(dial_xy[0], dial_xy[1], 0.0081)),
                      material=mats["steel"], name="adjustment_boss", material_class_id="metal.steel_bare")

    # Upper handle (S3 L259-L292). Local frame origin = main pivot.
    moving_handle = model.part("moving_handle", meta={"role": "upper handle shank"})

    def warp_local(pts):
        out = []
        for x, y in pts:
            if x > 64.0:
                x = 64.0 * ds + (x - 64.0) * hs
                y = y * 1.0
            else:
                x, y = x * ds, y * ds
            out.append((x, y))
        return out

    upper_shank = _poly_b(
        warp_local([(-9, -9), (12, -10), (40, -1), (68, 10), (218, 10), (225, 17),
                    (220, 25), (62, 24), (27, 14), (-7, 8)]),
        4.0, 5.0,
    )
    upper_shank = upper_shank.cut(cq.Workplane("XY").circle(5.7).extrude(12.0))
    _vis_mm(moving_handle, upper_shank, "moving_shank", mats["steel"])
    ux0, ux1 = 64.0 * ds, 64.0 * ds + (226.0 - 64.0) * hs
    _vis_mm(moving_handle, _rounded_bar(ux0, ux1, 9.0, 9.0 + 22.0 * gts, 8.0, 8.0),
            "moving_grip", mats["grip"])
    _vis_mm(moving_handle, _poly_b(
        [(ux0 + 1, 25), (ux1 - 8, 25), (ux1 - 2, 30), (ux1 - 7, 34), (ux0 + 14, 33), (ux0 - 2, 28)],
        3.2, 16.0), "moving_red_accent", mats["accent"])

    model.articulation(
        "main_closing_pivot",
        ArticulationType.REVOLUTE,
        parent=fixed_body,
        child=moving_handle,
        origin=Origin(xyz=(0.062, 0.008, 0.0)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(
            effort=180.0, velocity=1.3, lower=0.0,
            upper=math.radians(12.0) * r.jaw_open_scale,
        ),
        mating=MatingContract(
            parent_face_geometry="fixed_shank",
            parent_face_side="positive_z",
            child_face_geometry="moving_shank",
            child_face_side="negative_z",
            contact_tol=0.0015,
        ),
        meta={"positive_motion": "opens the handles by the small ratcheting range"},
    )
    return {
        "fixed_body": fixed_body,
        "moving_handle": moving_handle,
        "release_mount": InterfaceSpec(
            interface_name="release_mount",
            part_name="fixed_body",
            visual_name="ratchet_boss",
            face_side="positive_z",
            anchor_local=(rel_xy[0], rel_xy[1], 0.012),
        ),
        "dial_mount": InterfaceSpec(
            interface_name="dial_mount",
            part_name="fixed_body",
            visual_name="adjustment_boss",
            face_side="positive_z",
            anchor_local=(dial_xy[0], dial_xy[1], 0.012),
        ),
    }


def _build_head_connector_press(model, r, mats, sk) -> None:
    """S3 L145-L171 + L296-L313 + L367-L381: modular-connector die frame with a
    mimic-driven press carrier. The three cavities (8P/6P/aux) are the fixed
    identity of this head family (not a sampled N)."""
    ds = r.head_scale
    fixed_body = sk["fixed_body"]
    fx, fy = 62.0 + (87.5 - 62.0) * ds, 8.0 + (7.0 - 8.0) * ds
    die_frame = cq.Workplane("XY").box(67.0 * ds, 24.0 * ds, 5.2).translate((fx, fy, 10.0))
    cav = [(69.5, 17.0, 10.0), (91.5, 20.0, 12.0), (113.0, 12.0, 8.0)]
    for cx, w, h in cav:
        wx = 62.0 + (cx - 62.0) * ds
        die_frame = die_frame.cut(
            cq.Workplane("XY").box(w * ds, h * ds, 8.0).translate((wx, fy, 10.0))
        )
    _vis_mm(fixed_body, die_frame, "die_frame", mats["steel"])
    for name, cx, w, h in (("rj45_cavity", 91.5, 18.0, 10.0), ("rj11_cavity", 69.5, 15.0, 8.0),
                           ("aux_cavity", 113.0, 10.0, 6.0)):
        wx = 62.0 + (cx - 62.0) * ds
        fixed_body.visual(Box((w * ds / 1000.0, h * ds / 1000.0, 0.0012)),
                          origin=Origin(xyz=(wx / 1000.0, fy / 1000.0, 0.0080)),
                          material=mats["dark"], name=name, material_class_id="metal.blackened_gunmetal")

    press = model.part("press_plate", meta={"function": "moving press carrier", "cavity_count": 3})
    press_shape = _poly_b(_sc([(2, 2), (54, 2), (60, 8), (53, 15), (6, 14), (-4, 8)], ds), 3.0, 14.0)
    press_shape = press_shape.cut(cq.Workplane("XY").circle(5.7).extrude(20.0))
    _vis_mm(press, press_shape, "press_carrier", mats["steel"])
    for idx, (x, w) in enumerate(((18.0, 13.0), (38.0, 16.0), (54.0, 9.0))):
        press.visual(Box((w * ds / 1000.0, 0.004 * ds, 0.002)),
                     origin=Origin(xyz=(x * ds / 1000.0, 0.001 * ds, 0.018)),
                     material=mats["die"], name=f"press_tooth_{idx}", material_class_id="metal.steel_bare")
    model.articulation(
        "press_motion",
        ArticulationType.REVOLUTE,
        parent=sk["fixed_body"],
        child=press,
        origin=Origin(xyz=(0.062, 0.008, 0.0)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(
            effort=120.0, velocity=1.3, lower=0.0,
            upper=math.radians(8.4) * r.jaw_open_scale,
        ),
        mimic=Mimic(joint="main_closing_pivot", multiplier=0.70, offset=0.0),
    )


def _build_head_four_indent(model, r, mats, sk) -> None:
    """S8 L69-L91 + L166-L203 + L324-L423: radial die head with four guided
    indenters converging on a central terminal bore. N=4 is the mechanism
    identity ('four-indent'), not a sampled multiplicity axis."""
    ds = r.head_scale
    fixed_body = sk["fixed_body"]
    cx, cy = 62.0 + (85.0 - 62.0) * ds, 8.0 + (5.0 - 8.0) * ds
    head_z0 = 7.0

    head = cq.Workplane("XY").circle(20.0 * ds).circle(4.0 * ds).extrude(10.0)
    for angle_deg in (0, 90, 180, 270):
        slot = cq.Workplane("XY").center(12.0 * ds, 0).rect(16.0 * ds, 7.0 * ds).extrude(10.0)
        slot = slot.rotate((0, 0, 0), (0, 0, 1), angle_deg)
        head = head.cut(slot)
    _vis_mm(fixed_body, head.translate((cx, cy, head_z0)), "radial_die_head", mats["steel"])
    fixed_body.visual(Cylinder(radius=0.004 * ds, length=0.010),
                      origin=Origin(xyz=(cx / 1000.0, cy / 1000.0, 0.012)),
                      material=mats["dark"], name="terminal_bore", material_class_id="metal.blackened_gunmetal")
    # Guide walls flanking each indenter slot (S8 L184-L203).
    for angle_deg, dx, dy in ((0, 1, 0), (90, 0, 1), (180, -1, 0), (270, 0, -1)):
        for side in (-1, 1):
            if dx != 0:
                wall = cq.Workplane("XY").box(14.0 * ds, 1.2, 10.0).translate(
                    (cx + dx * 13.0 * ds, cy + side * 4.2 * ds, head_z0 + 5.0))
            else:
                wall = cq.Workplane("XY").box(1.2, 14.0 * ds, 10.0).translate(
                    (cx + side * 4.2 * ds, cy + dy * 13.0 * ds, head_z0 + 5.0))
            _vis_mm(fixed_body, wall, f"guide_wall_{angle_deg}_{side}", mats["steel"])
    for name, x, y in (("head_screw_0", 74.0, -7.0), ("head_screw_1", 96.0, 17.0)):
        wx, wy = 62.0 + (x - 62.0) * ds, 8.0 + (y - 8.0) * ds
        fixed_body.visual(Cylinder(radius=0.0028, length=0.012),
                          origin=Origin(xyz=(wx / 1000.0, wy / 1000.0, 0.010)),
                          material=mats["pin"], name=name, material_class_id="metal.stainless_matte")

    # Four pivoting indenter arms, mimic-coupled so they converge as the
    # handles crimp (S8 L326-L423).
    pivot_r = 0.019 * ds
    arm_len = 14.0 * ds
    indenter_upper = math.radians(14.0)
    main_upper = math.radians(12.0) * r.jaw_open_scale
    mimic_multiplier = -indenter_upper / main_upper
    mimic_offset = indenter_upper
    indenter_defs = (
        (0, (1, 0), (0, 1)),
        (1, (0, 1), (-1, 0)),
        (2, (-1, 0), (0, -1)),
        (3, (0, -1), (1, 0)),
    )
    for idx, radial_dir, arm_dir in indenter_defs:
        indenter = model.part(f"indenter_{idx}", meta={"function": f"radial indenter die {idx}"})
        adx, ady = arm_dir
        half = arm_len * 0.5
        arm_shape = (
            cq.Workplane("XY")
            .center(adx * half, ady * half)
            .box(max(arm_len * abs(adx), 4.0), max(arm_len * abs(ady), 4.0), 5.0)
        )
        die_block = cq.Workplane("XY").center(adx * arm_len, ady * arm_len).box(6.0 * ds, 6.0 * ds, 5.0)
        arm_shape = arm_shape.union(die_block)
        arm_shape = arm_shape.union(cq.Workplane("XY").circle(3.5).extrude(6.0))
        _vis_mm(indenter, arm_shape, "indenter_body", mats["die"])

        jx = cx / 1000.0 + pivot_r * radial_dir[0]
        jy = cy / 1000.0 + pivot_r * radial_dir[1]
        fixed_body.visual(Cylinder(radius=0.0025, length=0.012),
                          origin=Origin(xyz=(jx, jy, 0.011)),
                          material=mats["pin"], name=f"indenter_pivot_pin_{idx}", material_class_id="metal.stainless_matte")
        model.articulation(
            f"indenter_motion_{idx}",
            ArticulationType.REVOLUTE,
            parent=fixed_body,
            child=indenter,
            origin=Origin(xyz=(jx, jy, 0.012)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=80.0, velocity=1.0, lower=0.0, upper=indenter_upper),
            mimic=Mimic(joint="main_closing_pivot", multiplier=mimic_multiplier, offset=mimic_offset),
        )


# ---------------------------------------------------------------------------
# Controls (normalized local frame: base plane z=0, body extends dir*z)
# ---------------------------------------------------------------------------
def _mount_params(iface: InterfaceSpec) -> tuple[float, float, float, float]:
    ax, ay, az = iface.anchor_local
    direction = 1.0 if iface.face_side == "positive_z" else -1.0
    return ax, ay, az, direction


def _build_controls_star(model, r, mats, sk) -> None:
    """S1 L350-L398: forged thumb release lever + CONTINUOUS star pressure wheel,
    pivoting on the root control shafts/bosses."""
    rx, ry, rz, rdir = _mount_params(sk["release_mount"])
    release = model.part("ratchet_release", meta={"role": "thumb release lever"})
    lever_pts = [(-3, -3), (5, -4), (16, -20), (12, -31), (6, -29), (8, -16), (-5, 4)]
    lever = _poly_c(lever_pts, 3.0, rdir * 1.5)
    _vis_mm(release, lever, "release_lever", mats["die"])
    _vis_mm(release, _disc_c(3.7, 2.0, 0.0, 0.0, rdir * 4.0), "release_rivet", mats["pin"])
    model.articulation(
        "release_pivot",
        ArticulationType.REVOLUTE,
        parent=sk["fixed_body"],
        child=release,
        origin=Origin(xyz=(rx, ry, rz)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(lower=-0.28, upper=0.22, effort=8.0, velocity=4.0),
    )

    dx, dy, dz, ddir = _mount_params(sk["dial_mount"])
    dial = model.part("pressure_dial", meta={"role": "star pressure adjuster"})
    _vis_mm(dial, _star_poly(8.2, 5.7, 8, 3.2).translate((0.0, 0.0, ddir * 1.6)),
            "pressure_star_wheel", mats["die"])
    # captured spindle: pokes back through the base plane into the root boss.
    _vis_mm(dial, _disc_c(2.5, 5.0, 0.0, 0.0, 0.0), "dial_hub", mats["pin"])
    model.articulation(
        "dial_rotation",
        ArticulationType.CONTINUOUS,
        parent=sk["fixed_body"],
        child=dial,
        origin=Origin(xyz=(dx, dy, dz)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=4.0, velocity=5.0),
    )


def _build_controls_paddle(model, r, mats, sk) -> None:
    """S3 L315-L350 + L382-L399: paddle release lever + disc adjustment dial on
    the root bosses (Box/Cylinder primitives per source)."""
    rx, ry, rz, rdir = _mount_params(sk["release_mount"])
    release = model.part("ratchet_release", meta={"role": "release paddle"})
    release.visual(Cylinder(radius=0.0043, length=0.003),
                   origin=Origin(xyz=(0.0, 0.0, rdir * 0.0015)),
                   material=mats["pin"], name="release_pivot_hub", material_class_id="metal.stainless_matte")
    release.visual(Box((0.026, 0.006, 0.003)),
                   origin=Origin(xyz=(0.012, -0.001, rdir * 0.003)),
                   material=mats["dark"], name="release_paddle", material_class_id="plastic.opaque_generic")
    release.visual(Cylinder(radius=0.004, length=0.005),
                   origin=Origin(xyz=(0.024, -0.001, rdir * 0.003)),
                   material=mats["dark"], name="release_tip", material_class_id="plastic.opaque_generic")
    model.articulation(
        "release_pivot",
        ArticulationType.REVOLUTE,
        parent=sk["fixed_body"],
        child=release,
        origin=Origin(xyz=(rx, ry, rz)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=4.0, velocity=4.0, lower=-0.25, upper=0.32),
    )

    dx, dy, dz, ddir = _mount_params(sk["dial_mount"])
    dial = model.part("pressure_dial", meta={"role": "rotating adjustment dial"})
    dial.visual(Cylinder(radius=0.006, length=0.004),
                origin=Origin(xyz=(0.0, 0.0, ddir * 0.002)),
                material=mats["dark"], name="adjustment_dial", material_class_id="plastic.opaque_generic")
    dial.visual(Box((0.009, 0.002, 0.0015)),
                origin=Origin(xyz=(0.0015, 0.0, ddir * 0.0045)),
                material=mats["pin"], name="dial_index", material_class_id="metal.stainless_matte")
    model.articulation(
        "dial_rotation",
        ArticulationType.REVOLUTE,
        parent=sk["fixed_body"],
        child=dial,
        origin=Origin(xyz=(dx, dy, dz)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=2.0, velocity=3.0, lower=-math.pi, upper=math.pi),
    )


# ---------------------------------------------------------------------------
# Assembly
# ---------------------------------------------------------------------------
_HEAD_BUILDERS = {
    "integral_fixed_die": _build_head_integral,
    "cassette_die": _build_head_cassette,
    "turret_die": _build_head_turret,
    "single_hex_die": lambda m, r, mats, sk: _build_head_layered(m, r, mats, sk, hex_single=True),
    "profile_station_die": lambda m, r, mats, sk: _build_head_layered(m, r, mats, sk, hex_single=False),
    "connector_press_head": _build_head_connector_press,
    "four_indent_head": _build_head_four_indent,
}
_SKELETON_BUILDERS = {
    "open_v_compound": _build_skeleton_open_v,
    "layered_ratchet_frame": _build_skeleton_layered,
    "inline_press_frame": _build_skeleton_inline,
}
_CONTROLS_BUILDERS = {
    "lever_release_star_dial": _build_controls_star,
    "paddle_release_disc_dial": _build_controls_paddle,
    "handle_pawl_release": _build_controls_pawl,
}


def build_picturex_0611_crimping_tool(
    config: PictureX0611CrimpingToolConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config or PictureX0611CrimpingToolConfig())
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={
            "subcategory": "crimping_tool",
            "object_class": "manual ratcheting terminal crimping tool",
            "slot_choices": slot_choices_for_config(
                PictureX0611CrimpingToolConfig(
                    skeleton=r.skeleton, die_head=r.die_head, controls=r.controls,
                    palette_style=r.palette_style,
                    die_station_count=r.die_station_count,
                    nest_pair_count=r.nest_pair_count,
                    turret_nest_count=r.turret_nest_count,
                    scallop_count=r.scallop_count,
                    handle_scale=r.handle_scale, head_scale=r.head_scale,
                    grip_thickness_scale=r.grip_thickness_scale,
                    jaw_open_scale=r.jaw_open_scale, name=r.name,
                )
            ),
            "palette_style": r.palette_style,
        },
    )
    palette = PALETTES[r.palette_style]
    mats = {k: model.material(f"{r.palette_style}_{k}", rgba=v) for k, v in palette.items()}

    sk = _SKELETON_BUILDERS[r.skeleton](model, r, mats)
    _HEAD_BUILDERS[r.die_head](model, r, mats, sk)
    _CONTROLS_BUILDERS[r.controls](model, r, mats, sk)
    return model


def build_seeded_picturex_0611_crimping_tool(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_picturex_0611_crimping_tool(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def _aabb_center(bounds):
    if bounds is None:
        return None
    lo, hi = bounds
    return tuple((lo[i] + hi[i]) * 0.5 for i in range(3))


def _x_gap(a, b) -> float | None:
    """Signed x separation between two AABBs (positive = apart)."""
    if a is None or b is None:
        return None
    (a_lo, a_hi), (b_lo, b_hi) = a, b
    return max(b_lo[0] - a_hi[0], a_lo[0] - b_hi[0])


def _y_gap(a, b) -> float | None:
    if a is None or b is None:
        return None
    (a_lo, a_hi), (b_lo, b_hi) = a, b
    return max(b_lo[1] - a_hi[1], a_lo[1] - b_hi[1])


def run_picturex_0611_crimping_tool_tests(
    object_model: ArticulatedObject, config: PictureX0611CrimpingToolConfig
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    part_names = {p.name for p in object_model.parts}
    joint_names = {j.name for j in object_model.articulations}

    fixed = object_model.get_part("fixed_body")
    moving = object_model.get_part("moving_handle")
    main = object_model.get_articulation("main_closing_pivot")

    # -- category identity: two-handle compound crimper with a release path --
    ctx.check("two handles exist", {"fixed_body", "moving_handle"}.issubset(part_names))
    ctx.check(
        "main closing pivot is revolute with travel",
        main is not None
        and main.articulation_type == ArticulationType.REVOLUTE
        and main.motion_limits is not None,
    )
    fixed_visuals = {v.name for v in fixed.visuals}
    moving_visuals = {v.name for v in moving.visuals}
    ctx.check(
        "both handles carry molded grips",
        "fixed_grip" in fixed_visuals and "moving_grip" in moving_visuals,
        details=f"fixed={sorted(fixed_visuals)}, moving={sorted(moving_visuals)}",
    )
    ctx.check(
        "release mechanism present",
        ("ratchet_release" in part_names) or ("release_pawl" in part_names),
    )
    ctx.check(
        "slot choices recorded",
        dict(object_model.meta.get("slot_choices", ())).get("skeleton") == r.skeleton,
        details=str(object_model.meta.get("slot_choices")),
    )

    # -- skeleton-specific allowances (captured pins / rail captures) --
    if r.skeleton == "open_v_compound":
        carrier = object_model.get_part("die_carrier")
        ctx.allow_overlap(
            moving, carrier, elem_a="carrier_pivot_shaft", elem_b="die_carrier_plate",
            reason="carrier plate bore rides the pivot shaft on the moving shank (captured pin)",
        )
        if "pressure_dial" in part_names:
            ctx.allow_overlap(
                fixed, object_model.get_part("pressure_dial"),
                elem_a="fixed_shank", elem_b="dial_hub",
                reason="dial spindle is captured through the fixed shank plate (spindle-in-cup)",
            )
    if r.skeleton == "inline_press_frame" and "pressure_dial" in part_names:
        ctx.allow_overlap(
            fixed, object_model.get_part("pressure_dial"),
            elem_a="adjustment_boss", elem_b="dial_hub",
            reason="dial spindle is captured inside the adjustment boss (spindle-in-cup)",
        )

    # -- head-specific structure + allowances + targeted poses --
    if r.die_head in ("integral_fixed_die", "cassette_die", "turret_die"):
        carrier = object_model.get_part("die_carrier")
        ctx.check(
            "compound linkage joints present",
            {"handle_to_die_carrier", "carrier_to_drive_link"}.issubset(joint_names),
        )
        moving_die_part = carrier
        moving_die_elem = "moving_crimp_die"
        if r.die_head == "cassette_die":
            cassette = object_model.get_part("die_cassette")
            latch = object_model.get_part("cassette_latch")
            ctx.check("cassette + latch parts exist", cassette is not None and latch is not None)
            # Rule 7: exact element pairs only. The two pairs below are the real
            # captured contacts (rail tongue in its groove, detent bump in its
            # notch); a whole-part waiver here would also have hidden the shell
            # ramming the fixed die, which is the actual defect this seed had.
            for rail in ("cassette_rail_0", "cassette_rail_1"):
                ctx.allow_overlap(
                    carrier, cassette, elem_a=rail, elem_b="cassette_body",
                    reason="cassette rail tongue is captured in this carrier rail groove",
                )
            ctx.allow_overlap(
                carrier, latch, elem_a="cassette_rail_0", elem_b="latch_lever_body",
                reason="latch lever pivots against the carrier rail boss",
            )
            ctx.allow_overlap(
                cassette, latch, elem_a="cassette_body", elem_b="latch_lever_body",
                reason="latch detent bump engages the cassette retention notch through its swing",
            )
            moving_die_part = cassette
            moving_die_elem = "cassette_body"
            latch_rest = ctx.part_world_aabb(latch)
            with ctx.pose({"carrier_to_latch": 0.55}):
                latch_open = ctx.part_world_aabb(latch)
            ctx.check(
                "latch lever swings to release the cassette",
                latch_rest is not None and latch_open is not None
                and abs(latch_open[0][0] - latch_rest[0][0]) > 0.002,
                details=f"rest={latch_rest}, open={latch_open}",
            )
        if r.die_head == "turret_die":
            turret = object_model.get_part("die_turret")
            n = r.turret_nest_count
            ctx.check(
                "turret carries indexed nests",
                all(turret.get_visual(f"nest_{i}") is not None for i in range(n)),
            )
            # Only the three contacts below are real. Three more were declared
            # against the pre-fix turret (nest<->turret_pivot_shaft,
            # nest<->fixed_shank, and nest<->moving_crimp_die "crimp die faces
            # meet at full stroke") and are gone: with the axis derived from the
            # die plane the moving die now STOPS ~1.8mm short of the active nest
            # -- that pair is a crimp gap, not a captured contact, so waiving it
            # would only mask the next regression. Verified by sweeping the
            # collision finder with allowances off across N=3..5 x head_scale
            # 0.92..1.10 at full stroke: those pairs never touch.
            ctx.allow_overlap(
                turret, fixed, elem_a="turret_wheel", elem_b="turret_pivot_shaft",
                reason="turret wheel bore (r3.5) rides the larger fixed pivot shaft (r3.8) it is captured on",
            )
            ctx.allow_overlap(
                turret, fixed, elem_a="turret_wheel", elem_b="turret_mount_boss",
                reason="wheel hub envelops the raised mount pad it indexes on (pad sits inside the wheel's z band)",
            )
            for i in range(n):
                ctx.allow_overlap(
                    turret, fixed, elem_a=f"nest_{i}", elem_b="turret_mount_boss",
                    reason="rim nest blocks sweep across the mounting boss while indexing",
                )
            nest0_rest = ctx.part_element_world_aabb(turret, elem="nest_0")
            with ctx.pose({"turret_index": 2.0 * math.pi / n}):
                nest0_rot = ctx.part_element_world_aabb(turret, elem="nest_0")
            ctx.check(
                "turret indexing moves nest_0 out of the active station",
                nest0_rest is not None and nest0_rot is not None
                and abs(nest0_rot[0][0] - nest0_rest[0][0]) > 0.004,
                details=f"rest={nest0_rest}, rotated={nest0_rot}",
            )
            fixed_die_aabb = ctx.part_element_world_aabb(turret, elem="nest_0")
        else:
            fixed_die_aabb = ctx.part_element_world_aabb(fixed, elem="fixed_crimp_die")
            ctx.check("fixed die block present", fixed_die_aabb is not None)

        # closing stroke: the moving die approaches the fixed die side.
        upper = main.motion_limits.upper
        gap_rest = _x_gap(
            fixed_die_aabb, ctx.part_element_world_aabb(moving_die_part, elem=moving_die_elem)
        )
        moving_rest = ctx.part_world_aabb(moving)
        with ctx.pose({main: upper}):
            gap_closed = _x_gap(
                fixed_die_aabb, ctx.part_element_world_aabb(moving_die_part, elem=moving_die_elem)
            )
            moving_closed = ctx.part_world_aabb(moving)
        ctx.check(
            "closing stroke drives the moving die toward the fixed die",
            gap_rest is not None and gap_closed is not None and gap_closed < gap_rest - 0.010,
            details=f"gap_rest={gap_rest}, gap_closed={gap_closed}",
        )
        ctx.check(
            "moving handle sweeps toward the fixed handle",
            moving_rest is not None and moving_closed is not None
            and moving_closed[1][0] > moving_rest[1][0] + 0.03,
            details=f"rest={moving_rest}, closed={moving_closed}",
        )

    elif r.die_head in ("single_hex_die", "profile_station_die"):
        upper_die = object_model.get_part("upper_die")
        ctx.check("upper die part exists", upper_die is not None)
        ctx.check(
            "die pivot mimics the handle",
            object_model.get_articulation("die_pivot") is not None
            and object_model.get_articulation("die_pivot").mimic is not None,
        )
        ctx.check(
            "opposed die layers present",
            fixed.get_visual("lower_crimp_profiles") is not None
            and upper_die.get_visual("upper_crimp_profiles") is not None,
        )
        ctx.allow_overlap(
            fixed, moving, elem_a="main_pivot_pin", elem_b="moving_shank",
            reason="main pivot pin is captured through the moving shank clearance hole",
        )
        lower_aabb = ctx.part_element_world_aabb(fixed, elem="lower_crimp_profiles")
        upper_rest = ctx.part_element_world_aabb(upper_die, elem="upper_crimp_profiles")
        with ctx.pose({main: main.motion_limits.lower}):
            upper_closed = ctx.part_element_world_aabb(upper_die, elem="upper_crimp_profiles")
        gr, gc = _y_gap(lower_aabb, upper_rest), _y_gap(lower_aabb, upper_closed)
        ctx.check(
            "compound action closes the upper die onto the lower profiles",
            gr is not None and gc is not None and gc < gr - 0.001,
            details=f"gap_rest={gr}, gap_closed={gc}",
        )

    elif r.die_head == "connector_press_head":
        press = object_model.get_part("press_plate")
        ctx.check("press plate exists with teeth",
                  press is not None and press.get_visual("press_tooth_0") is not None)
        ctx.check(
            "press motion mimics the handle",
            object_model.get_articulation("press_motion") is not None
            and object_model.get_articulation("press_motion").mimic is not None,
        )
        ctx.allow_overlap(
            fixed, press, elem_a="main_pivot_cap", elem_b="press_carrier",
            reason="retaining cap seats the press carrier on the main pivot pin",
        )
        press_rest = ctx.part_world_aabb(press)
        with ctx.pose({main: main.motion_limits.upper}):
            press_open = ctx.part_world_aabb(press)
        ctx.check(
            "press carrier follows the handle opening",
            press_rest is not None and press_open is not None
            and press_open[1][1] > press_rest[1][1] + 0.001,
            details=f"rest={press_rest}, open={press_open}",
        )

    elif r.die_head == "four_indent_head":
        for i in range(4):
            ind = object_model.get_part(f"indenter_{i}")
            ctx.check(f"indenter_{i} exists", ind is not None)
            ctx.allow_overlap(
                fixed, ind, elem_a="radial_die_head", elem_b="indenter_body",
                reason="indenter arm pivots inside its radial die head guide slot",
            )
            ctx.allow_overlap(
                fixed, ind, elem_a=f"indenter_pivot_pin_{i}", elem_b="indenter_body",
                reason="indenter pivot pin is captured through the arm boss",
            )
            for wall_angle in (0, 90, 180, 270):
                for side in (-1, 1):
                    ctx.allow_overlap(
                        fixed, ind, elem_a=f"guide_wall_{wall_angle}_{side}", elem_b="indenter_body",
                        reason="indenter arm slides between its guide walls (rail capture)",
                    )
        ind0 = object_model.get_part("indenter_0")
        rest = _aabb_center(ctx.part_world_aabb(ind0))
        with ctx.pose({main: main.motion_limits.upper}):
            opened = _aabb_center(ctx.part_world_aabb(ind0))
        ctx.check(
            "indenters retract as the handles open (mimic coupling)",
            rest is not None and opened is not None
            and (abs(opened[0] - rest[0]) + abs(opened[1] - rest[1])) > 0.0008,
            details=f"rest={rest}, open={opened}",
        )

    # -- controls checks --
    if r.controls == "lever_release_star_dial":
        dial_joint = object_model.get_articulation("dial_rotation")
        ctx.check(
            "star pressure dial is continuous",
            dial_joint is not None
            and dial_joint.articulation_type == ArticulationType.CONTINUOUS,
        )
    elif r.controls == "paddle_release_disc_dial":
        ctx.check(
            "adjustment dial revolute present",
            object_model.get_articulation("dial_rotation") is not None,
        )
    else:
        ctx.check(
            "ratchet bridge + pawl on the moving shank",
            {"ratchet_link", "release_pawl"}.issubset(part_names),
        )
    release_joint = object_model.get_articulation("release_pivot")
    ctx.check("release pivot exists", release_joint is not None)
    rel_part = object_model.get_part(
        "release_pawl" if r.controls == "handle_pawl_release" else "ratchet_release"
    )
    rel_rest = _aabb_center(ctx.part_world_aabb(rel_part))
    with ctx.pose({release_joint: release_joint.motion_limits.upper}):
        rel_moved = _aabb_center(ctx.part_world_aabb(rel_part))
    ctx.check(
        "release lever articulates",
        rel_rest is not None and rel_moved is not None
        and (abs(rel_moved[0] - rel_rest[0]) + abs(rel_moved[1] - rel_rest[1])) > 0.0005,
        details=f"rest={rel_rest}, moved={rel_moved}",
    )

    # Rule 5: full-travel sampled collision check (mimics follow their drivers).
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=64, ignore_fixed=True)
    return ctx.report()


# short aliases used by the sweep registry stem
build_seeded_crimping_tool = build_seeded_picturex_0611_crimping_tool

__all__ = [
    "PictureX0611CrimpingToolConfig",
    "ResolvedPictureX0611CrimpingToolConfig",
    "config_from_seed",
    "resolve_config",
    "slot_choices_for_seed",
    "slot_choices_for_config",
    "build_picturex_0611_crimping_tool",
    "build_seeded_picturex_0611_crimping_tool",
    "run_picturex_0611_crimping_tool_tests",
]
