# SPDX-License-Identifier: Apache-2.0

"""Adjustable / movable wrench modular template (crescent / pipe / monkey / quick-adjust).

NOTE on the slug name: "wrench" here = an **adjustable / movable wrench** (a
long handle + a head with a FIXED jaw and a MOVABLE jaw that slides open/closed,
driven by a rotary / pivoting driver). It is NOT a rigid open-end / box-end /
combination spanner (0 moving joints — a documented reject case), nor a socket /
ratchet wrench, nor pliers. IDENTITY HARD CONSTRAINT: every output keeps >=1
non-fixed joint — the ``movable_jaw`` PRISMATIC slide.

Sourced from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/Handtools_Wrench.md`` and the
``picture/Handtools/Wrench`` 5-star sample pool (2 parents + 3 head/handle fork
variants + 3 cross-spine handle variants), all synced under ``data/records/``.

Structure (pattern = ``parallel_children``): a single root part carries the
movable jaw (PRISMATIC child) + a driver child (worm / nut CONTINUOUS, or thumb
lever REVOLUTE), and inlines the fixed jaw / housing / handle as root visuals.
There are TWO kinematic spines, chosen by ``head_mechanism``:

  * crescent spine — root ``wrench_body`` is authored in-place in the world XY
    plane (long axis +X, z_min~=0 via Z_LIFT). Heads: worm_rack_crescent,
    monkey_head, thumb_slide.
  * pipe spine — root ``head_frame`` is authored in a "tool frame" (tool +Z =
    long axis, tool +X = mouth) then laid flat by ``_lay()`` / ``LAY_RPY`` so
    tool z -> world +X. Head: screw_nut_pipe (KnobGeometry knurled adjust nut).

Two named slots:

  * ``head_mechanism`` (4): worm_rack_crescent (parent A) / screw_nut_pipe
    (parent B, KnobGeometry nut) / monkey_head (square parallel jaws, slide -Y)
    / thumb_slide (REVOLUTE quick-adjust lever). This is the part/joint topology
    axis; it also derives the spine + root type.
  * ``handle`` (3): flat_steel / tapered_wood / tubular. ORTHOGONAL to the head
    (3 cross-spine 5-star sources prove every handle mounts to both spines). The
    template rebases the handle's anchor frame onto the chosen head's spine
    (crescent = revolve/extrude in place along +X; pipe = author in tool frame
    then ``_lay()``). The handle introduces NO new joint.

Combos = crescent heads (3) x handle (3) + pipe head (1) x handle (3) = 12 >= 10.

Rule 1 ("不动就不是 part") is upheld: rack teeth, grip ridges, knurl grooves,
ferrules, butt caps and hex rings are all root / driver ``part.visual(...)``
loops or inlined geometry, never FIXED-joint decoration parts. The only separate
parts are ``movable_jaw`` (PRISMATIC) and the driver (``worm_screw`` CONTINUOUS,
``adjust_nut`` CONTINUOUS, or ``thumb_lever`` REVOLUTE) — all genuinely move.
Rule 2 / grandfathering: the jaw-shank-in-slot, worm-in-pocket, nut-around-bar
and lever-on-boss fits are captured overlaps that cannot be modeled as two
axis-aligned faces in contact, so their joints omit ``MatingContract`` and rely
on the flat 0.015 m articulation-origin baseline + element-scoped
``allow_overlap`` (mirroring each source sample's run_tests).
Rule 3: all geometry is adapted from the declared 5-star CadQuery / KnobGeometry
sources; ``mesh_from_cadquery`` / ``mesh_from_geometry`` primitives are
preserved, never downgraded to crude Box/Cylinder placeholders.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, replace
from typing import Literal

import cadquery as cq

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    Inertial,
    KnobGeometry,
    KnobGrip,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
    mesh_from_geometry,
)

__modular__ = True

HeadMechanism = Literal["worm_rack_crescent", "screw_nut_pipe", "monkey_head", "thumb_slide"]
Handle = Literal["flat_steel", "tapered_wood", "tubular"]
Spine = Literal["crescent", "pipe"]
PaletteStyle = Literal[
    "bright_chrome_steel",
    "black_oxide_steel",
    "blue_japanned_steel",
    "red_wood_handle",
    "galvanized_tube",
    "dark_machined_steel",
]

HEAD_MECHANISMS: tuple[HeadMechanism, ...] = (
    "worm_rack_crescent",
    "screw_nut_pipe",
    "monkey_head",
    "thumb_slide",
)
HANDLES: tuple[Handle, ...] = ("flat_steel", "tapered_wood", "tubular")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "bright_chrome_steel",
    "black_oxide_steel",
    "blue_japanned_steel",
    "red_wood_handle",
    "galvanized_tube",
    "dark_machined_steel",
)

# Heads that ride the crescent (in-place) spine vs the pipe (lay-down) spine.
CRESCENT_HEADS: tuple[HeadMechanism, ...] = ("worm_rack_crescent", "monkey_head", "thumb_slide")
PIPE_HEADS: tuple[HeadMechanism, ...] = ("screw_nut_pipe",)

# Palette gating (spec §7 / §compatibility): red wood handle only on tapered_wood,
# galvanized tube colorway only on tubular; the four steel colorways are generic.
WOOD_ONLY_PALETTE: PaletteStyle = "red_wood_handle"
TUBE_ONLY_PALETTE: PaletteStyle = "galvanized_tube"
GENERIC_PALETTES: tuple[PaletteStyle, ...] = (
    "bright_chrome_steel",
    "black_oxide_steel",
    "blue_japanned_steel",
    "dark_machined_steel",
)


# ---------------------------------------------------------------------------
# Per-seed palettes (spec §palette). Keys: steel (main body/head) / steel_dark
# (machined movable jaw) / knurl (worm/nut driver) / accent (lever oxide / blue
# jaw) / wood (grip) / brass (ferrule) / butt (steel butt cap) / grip (rubber
# grip ridges). EVERY .visual material is driven off this dict so the swept pool
# is colorful (module_topology_diversity only counts structure).
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "bright_chrome_steel": {
        "steel": (0.74, 0.75, 0.77, 1.0),
        "steel_dark": (0.58, 0.59, 0.62, 1.0),
        "knurl": (0.50, 0.51, 0.54, 1.0),
        "accent": (0.62, 0.63, 0.66, 1.0),
        "wood": (0.52, 0.32, 0.15, 1.0),
        "brass": (0.72, 0.58, 0.28, 1.0),
        "butt": (0.40, 0.41, 0.44, 1.0),
        "grip": (0.20, 0.20, 0.22, 1.0),
    },
    "black_oxide_steel": {
        "steel": (0.20, 0.21, 0.23, 1.0),
        "steel_dark": (0.13, 0.14, 0.16, 1.0),
        "knurl": (0.30, 0.31, 0.34, 1.0),
        "accent": (0.38, 0.40, 0.42, 1.0),
        "wood": (0.42, 0.26, 0.13, 1.0),
        "brass": (0.55, 0.45, 0.24, 1.0),
        "butt": (0.10, 0.10, 0.12, 1.0),
        "grip": (0.07, 0.07, 0.08, 1.0),
    },
    "blue_japanned_steel": {
        "steel": (0.62, 0.64, 0.68, 1.0),
        "steel_dark": (0.42, 0.47, 0.58, 1.0),
        "knurl": (0.48, 0.49, 0.52, 1.0),
        "accent": (0.30, 0.36, 0.50, 1.0),
        "wood": (0.52, 0.32, 0.15, 1.0),
        "brass": (0.72, 0.58, 0.28, 1.0),
        "butt": (0.28, 0.32, 0.44, 1.0),
        "grip": (0.18, 0.18, 0.20, 1.0),
    },
    "red_wood_handle": {
        "steel": (0.72, 0.73, 0.76, 1.0),
        "steel_dark": (0.45, 0.46, 0.49, 1.0),
        "knurl": (0.58, 0.59, 0.62, 1.0),
        "accent": (0.50, 0.52, 0.55, 1.0),
        "wood": (0.74, 0.13, 0.11, 1.0),  # red painted handle
        "brass": (0.72, 0.58, 0.28, 1.0),
        "butt": (0.38, 0.38, 0.40, 1.0),
        "grip": (0.62, 0.49, 0.31, 1.0),  # bare wood worn band
    },
    "galvanized_tube": {
        "steel": (0.66, 0.68, 0.71, 1.0),
        "steel_dark": (0.50, 0.51, 0.54, 1.0),
        "knurl": (0.58, 0.59, 0.62, 1.0),
        "accent": (0.74, 0.13, 0.11, 1.0),  # red-painted tube accent
        "wood": (0.52, 0.32, 0.15, 1.0),
        "brass": (0.70, 0.72, 0.75, 1.0),
        "butt": (0.38, 0.38, 0.40, 1.0),
        "grip": (0.18, 0.18, 0.20, 1.0),
    },
    "dark_machined_steel": {
        "steel": (0.34, 0.35, 0.38, 1.0),
        "steel_dark": (0.24, 0.25, 0.27, 1.0),
        "knurl": (0.30, 0.31, 0.34, 1.0),
        "accent": (0.40, 0.42, 0.45, 1.0),
        "wood": (0.46, 0.28, 0.14, 1.0),
        "brass": (0.60, 0.50, 0.26, 1.0),
        "butt": (0.18, 0.18, 0.20, 1.0),
        "grip": (0.12, 0.12, 0.14, 1.0),
    },
}


# ===========================================================================
# Base real-world dimensions (meters).
# ===========================================================================
# --- Crescent spine (parent A / monkeyhead / thumbslide / cross-spine wood &
#     tube). Long axis along world +X; head at +X, butt at -X. ---
C_HANDLE_LEN = 0.235  # flat handle / grip span along X
C_HANDLE_W = 0.026  # handle width (Y)
C_HANDLE_T = 0.0085  # handle thickness (Z)

C_RING_R_OUTER = 0.024  # box-ring butt outer radius
C_RING_HEX_AF = 0.020  # hex through-hole across-flats
C_RING_HALF_T = 0.009  # ring half-thickness (Z)

C_HEAD_T = 0.013  # head plate thickness (Z)
C_HEAD_TILT_DEG = 15.0  # head/slide tilt from the handle axis (about Z)

# Crescent head-local landmarks (slide axis = local +x, mouth opens toward +y).
C_FIXED_JAW_FACE_X = 0.058
C_MOUTH_X0 = 0.012
C_MOUTH_FLOOR_Y = 0.004
C_SLOT_X0 = 0.002
C_SLOT_X1 = 0.048
C_SLOT_Y0 = -0.009
C_SLOT_Y1 = 0.007
C_JAW_NOMINAL_GAP = 0.008
C_JAW_TRAVEL = 0.018
C_JAW_ORIGIN_LX = C_FIXED_JAW_FACE_X - C_JAW_NOMINAL_GAP

# Crescent movable jaw (own frame: gripping face at local x = 0).
C_JAW_BLOCK_LEN = 0.016
C_JAW_BLOCK_TOP = 0.034
# Shank is sized to lightly EMBED into the head slot walls so the captured
# slide is a real physical contact (not a 1 mm-clearance floating rail that
# fail_if_isolated_parts would flag). Slot is x[0.002,0.048] y[-0.009,0.007]
# z[-HEAD_T/2,HEAD_T/2]; the shank straddles the slot Y/Z walls with a small
# intentional overlap (declared via allow_overlap), matching the captured fit.
C_SHANK_X0, C_SHANK_X1 = -0.026, -0.004
C_SHANK_Y0, C_SHANK_Y1 = -0.0095, 0.0075
C_SHANK_HALF_T = 0.0066

C_WORM_R = 0.008
C_WORM_HALF_LEN = 0.009
C_WORM_LCX = 0.025
C_WORM_LCY = -0.0135

# Thumb-lever (thumb_slide) landmarks. The pivot boss sits on the solid lobe
# BELOW the slide slot (slot y_min = -0.009) so the boss fuses with full plate
# material; the lever tab still reaches up into the slot to push the jaw shank.
C_LEVER_PIVOT_LX = 0.012
C_LEVER_PIVOT_LY = -0.013
C_LEVER_ARM_LEN = 0.025
C_LEVER_PAD_LEN = 0.010
C_LEVER_PAD_HW = 0.0065
C_LEVER_ARM_HW = 0.0045
C_LEVER_T = 0.004
C_PIVOT_BOSS_R = 0.003
C_PIVOT_BOSS_H = 0.005
C_LEVER_TAB_TIP_Y = 0.014
C_LEVER_TRAVEL = 0.50

# Monkey head (square block, parallel jaws, slide -Y).
M_HEAD_X0_OFF = -0.006
M_HEAD_LEN = 0.050
M_HEAD_Y_BOT = -0.042
M_HEAD_Y_TOP = 0.050
M_HEAD_T = 0.014
M_FIXED_JAW_FACE_Y = 0.034
M_CUT_BACK = 0.020
M_CUT_FRONT = 0.004
M_CUT_Y_BOT = -0.036
M_CUT_Y_TOP = M_FIXED_JAW_FACE_Y
M_JAW_SHOE_H = 0.006
M_JAW_SHOE_XW = 0.027
M_JAW_SHANK_H = 0.016
M_JAW_SHANK_XW = 0.014
M_SHANK_HALF_T = 0.005
M_JAW_FACE_Y_REST = 0.004
M_JAW_TRAVEL = 0.016
M_WORM_R = 0.007
M_WORM_HALF_LEN = 0.006
M_RACK_N = 5
M_RACK_TOOTH_DX = 0.003
M_RACK_TOOTH_DY = 0.002
M_RACK_TOOTH_DZ = 0.003

# Crescent grip ridge count (monkey grip ridges; module-local, not a slot axis).
C_GRIP_RIDGE_COUNT_DEFAULT = 7

# Crescent wood-grip / ferrule / butt / tang (cross-spine wood).
CW_GRIP_MAX_R = 0.014
CW_GRIP_BUTT_R = 0.006
CW_GRIP_HEAD_R = 0.0085
CW_FERRULE_LEN = 0.014
CW_FERRULE_R = 0.0105
CW_BUTT_CAP_LEN = 0.006
CW_BUTT_CAP_R = 0.0075
CW_TANG_R = 0.003

# Crescent tubular shank (cross-spine tube).
CT_SHANK_R = 0.013
CT_SHANK_WALL = 0.002
CT_FERRULE_R = 0.0145
CT_FERRULE_LEN = 0.010

# --- Pipe spine (parent B / tubularshank / pipe_flatsteel). Authored in the
#     tool frame (tool +Z = long axis, tool +X = mouth) then laid flat. ---
P_SHANK_W = 0.022
P_SHANK_T = 0.016
P_SHANK_BOTTOM = 0.040
P_SHANK_TOP = 0.235
P_FRAME_BODY_W = 0.058
P_FRAME_BODY_T = 0.030
P_FRAME_BODY_BOTTOM = P_SHANK_TOP - 0.006
P_FRAME_BODY_TOP = 0.300
P_WINDOW_W = 0.028
P_WINDOW_H = 0.029
P_WINDOW_Z = 0.262
P_SLOT_HALF_T = 0.009
P_SLOT_Z0 = 0.268
P_SLOT_Z1 = 0.312
P_HOOK_T_HALF = 0.013
P_HOOK_TEETH_FACE = 0.329
P_HOOK_TOOTH_H = 0.0045
P_HOOK_TEETH_TIP = P_HOOK_TEETH_FACE - P_HOOK_TOOTH_H
P_JAW_HEAD_Z0 = 0.010
P_JAW_HEAD_Z1 = 0.030
P_JAW_TEETH_FACE = 0.029
P_JAW_TOOTH_H = 0.0045
P_JAW_BAR_TOP = 0.024
P_JAW_TRAVEL = 0.024

# Pipe tapered-wood handle (parent B lathe revolve).
P_HANDLE_TOP = P_SHANK_BOTTOM
P_HANDLE_BOTTOM = -0.085
P_HANDLE_MAX_R = 0.0165

# Pipe tubular handle (tubularshank).
P_TUBE_OR = 0.014
P_TUBE_IR = 0.011
P_TUBE_BOTTOM = -0.090
P_GRIP_RIB_R = 0.0155
P_GRIP_RIB_LEN = 0.006
P_GRIP_RIB_COUNT_DEFAULT = 6
P_TUBE_BUTT_R = 0.016
P_TUBE_BUTT_LEN = 0.006

# Pipe flat steel handle (pipe_flatsteel cross-spine).
P_FLAT_HANDLE_T = 0.010
P_FLAT_HANDLE_W_TOP = 0.026
P_FLAT_HANDLE_W_RING = 0.020
P_FLAT_RING_OD = 0.034
P_FLAT_RING_AF = 0.019

# Pipe nut (KnobGeometry knurled). MEMORY: KnobGeometry BoltPattern needs
# all-positive — we use plain KnobGrip(knurled) (no bolt pattern), which is safe.
P_NUT_DIAMETER = 0.024
P_NUT_GRIP_COUNT = 30

P_LAY_RPY = (math.pi / 2, 0.0, math.pi / 2)


# ===========================================================================
# Config dataclasses
# ===========================================================================
@dataclass(frozen=True)
class WrenchConfig:
    head_mechanism: HeadMechanism | None = None
    handle: Handle | None = None
    palette_style: PaletteStyle = "bright_chrome_steel"
    handle_len_scale: float = 1.0
    handle_girth_scale: float = 1.0
    head_scale: float = 1.0
    jaw_travel_scale: float = 1.0
    driver_open_scale: float = 1.0  # only thumb_slide (lever REVOLUTE upper)
    grip_count: int = 6
    name: str = "wrench"


@dataclass(frozen=True)
class ResolvedWrenchConfig:
    head_mechanism: HeadMechanism
    handle: Handle
    spine: Spine
    palette_style: PaletteStyle
    handle_len_scale: float
    handle_girth_scale: float
    head_scale: float
    jaw_travel: float  # PRISMATIC upper (clamped)
    lever_travel: float  # REVOLUTE upper (thumb_slide only)
    grip_count: int
    name: str


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


def _spine_of(head: HeadMechanism) -> Spine:
    return "crescent" if head in CRESCENT_HEADS else "pipe"


def config_from_seed(seed: int) -> WrenchConfig:
    rng = random.Random(seed)
    head = rng.choice(HEAD_MECHANISMS)
    handle = rng.choice(HANDLES)  # orthogonal to head (3 cross-spine sources)
    # Palette gating: wood colorway only with tapered_wood, tube colorway only
    # with tubular; otherwise pick from the four generic steel colorways.
    if handle == "tapered_wood":
        palette = rng.choice(GENERIC_PALETTES + (WOOD_ONLY_PALETTE,))
    elif handle == "tubular":
        palette = rng.choice(GENERIC_PALETTES + (TUBE_ONLY_PALETTE,))
    else:
        palette = rng.choice(GENERIC_PALETTES)
    return WrenchConfig(
        head_mechanism=head,
        handle=handle,
        palette_style=palette,
        handle_len_scale=round(rng.uniform(0.88, 1.12), 4),
        handle_girth_scale=round(rng.uniform(0.90, 1.10), 4),
        head_scale=round(rng.uniform(0.92, 1.10), 4),
        jaw_travel_scale=round(rng.uniform(0.85, 1.10), 4),
        driver_open_scale=round(rng.uniform(0.85, 1.10), 4),
        grip_count=rng.randint(4, 8),
        name=f"seeded_wrench_{seed}",
    )


def resolve_config(config: WrenchConfig | None = None) -> ResolvedWrenchConfig:
    cfg = config or WrenchConfig()
    head = _pick(cfg.head_mechanism, HEAD_MECHANISMS)
    handle = _pick(cfg.handle, HANDLES)
    spine = _spine_of(head)

    # Palette gating: degrade an incompatible palette to a generic steel one.
    palette = _pick(cfg.palette_style, PALETTE_STYLES)
    if palette == WOOD_ONLY_PALETTE and handle != "tapered_wood":
        palette = "bright_chrome_steel"
    if palette == TUBE_ONLY_PALETTE and handle != "tubular":
        palette = "bright_chrome_steel"

    handle_len_scale = _clamp(cfg.handle_len_scale, 0.88, 1.12)
    handle_girth_scale = _clamp(cfg.handle_girth_scale, 0.90, 1.10)
    head_scale = _clamp(cfg.head_scale, 0.92, 1.10)
    jaw_travel_scale = _clamp(cfg.jaw_travel_scale, 0.85, 1.10)
    driver_open_scale = _clamp(cfg.driver_open_scale, 0.85, 1.10)
    grip_count = int(_clamp(cfg.grip_count, 4, 8))

    # Per-spine base jaw travel; scale stays within the source captured range so
    # the shank never leaves the slot/channel over full travel (spec §7).
    if spine == "crescent":
        base_travel = M_JAW_TRAVEL if head == "monkey_head" else C_JAW_TRAVEL
    else:
        base_travel = P_JAW_TRAVEL
    jaw_travel = base_travel * jaw_travel_scale

    lever_travel = C_LEVER_TRAVEL * (driver_open_scale if head == "thumb_slide" else 1.0)
    lever_travel = _clamp(lever_travel, 0.30, 0.70)

    return ResolvedWrenchConfig(
        head_mechanism=head,
        handle=handle,
        spine=spine,
        palette_style=palette,
        handle_len_scale=handle_len_scale,
        handle_girth_scale=handle_girth_scale,
        head_scale=head_scale,
        jaw_travel=jaw_travel,
        lever_travel=lever_travel,
        grip_count=grip_count,
        name=cfg.name or "wrench",
    )


def with_overrides(config: WrenchConfig, **kwargs: object) -> WrenchConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: WrenchConfig | ResolvedWrenchConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedWrenchConfig) else resolve_config(config)
    return (
        ("head_mechanism", r.head_mechanism),
        ("handle", r.handle),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ===========================================================================
# Shared geometry helpers
# ===========================================================================
def _hex_profile(across_flats: float) -> list[tuple[float, float]]:
    """Flat-top hexagon profile (across-flats given), centered at origin."""
    r = across_flats / math.sqrt(3.0)
    pts: list[tuple[float, float]] = []
    for i in range(6):
        a = math.pi / 6.0 + i * math.pi / 3.0
        pts.append((r * math.cos(a), r * math.sin(a)))
    return pts


# Crescent head outline (head-local XY), shared by worm / thumb / cross-spine
# wood & tube. A wide lens/teardrop plate ~2.7x the handle width.
_CRESCENT_HEAD_PROFILE: list[tuple[float, float]] = [
    (-0.012, -0.013),
    (0.022, -0.035),
    (0.048, -0.035),
    (0.070, -0.016),
    (0.0775, 0.004),
    (0.073, 0.020),
    (0.062, 0.0355),
    (0.010, 0.0355),
    (-0.012, 0.013),
]


def _scaled_profile(profile, s: float):
    return [(x * s, y * s) for (x, y) in profile]


def _build_crescent_head_local(*, with_boss: bool, head_scale: float) -> cq.Workplane:
    """Crescent head plate in head-local frame (slide along +x). worm pocket +
    optional thumb-lever pivot boss. Adapted from parent A `_build_head_local`."""
    hs = head_scale
    plate = (
        cq.Workplane("XY")
        .polyline(_scaled_profile(_CRESCENT_HEAD_PROFILE, hs))
        .close()
        .extrude(C_HEAD_T * 0.5, both=True)
    )
    try:
        plate = plate.edges("|Z").fillet(0.0015)
    except Exception:
        pass

    # Jaw mouth.
    mouth = (
        cq.Workplane("XY")
        .center((C_MOUTH_X0 + C_FIXED_JAW_FACE_X) * 0.5 * hs, (C_MOUTH_FLOOR_Y + 0.065) * 0.5 * hs)
        .rect((C_FIXED_JAW_FACE_X - C_MOUTH_X0) * hs, (0.065 - C_MOUTH_FLOOR_Y) * hs)
        .extrude(C_HEAD_T, both=True)
    )
    plate = plate.cut(mouth)

    # Slide slot for the movable jaw rack shank (fully enclosed).
    slot = (
        cq.Workplane("XY")
        .center((C_SLOT_X0 + C_SLOT_X1) * 0.5 * hs, (C_SLOT_Y0 + C_SLOT_Y1) * 0.5 * hs)
        .rect((C_SLOT_X1 - C_SLOT_X0) * hs, (C_SLOT_Y1 - C_SLOT_Y0) * hs)
        .extrude(C_HEAD_T, both=True)
    )
    plate = plate.cut(slot)

    # Worm pocket: bore along slide axis; breaks through both faces (windows) and
    # breaches the slot bottom so the rim meshes the rack.
    pocket = (
        cq.Workplane("YZ")
        .workplane(offset=(C_WORM_LCX - C_WORM_HALF_LEN - 0.002) * hs)
        .center(C_WORM_LCY * hs, 0.0)
        .circle(C_WORM_R + 0.0015)
        .extrude(2.0 * (C_WORM_HALF_LEN + 0.002))
    )
    plate = plate.cut(pocket)

    if with_boss:
        # Pivot post for the thumb lever. It runs through the full plate
        # thickness on the solid lobe (below the slot) and rises above the top
        # face, fusing volumetrically with the head (no face-only island).
        boss = (
            cq.Workplane("XY")
            .workplane(offset=-C_HEAD_T * 0.5 - 0.001)
            .center(C_LEVER_PIVOT_LX * hs, C_LEVER_PIVOT_LY * hs)
            .circle(C_PIVOT_BOSS_R)
            .extrude(C_HEAD_T + C_PIVOT_BOSS_H + 0.001)
        )
        plate = plate.union(boss, clean=True)
    return plate


def _build_monkey_head_local(*, head_scale: float) -> cq.Workplane:
    """Monkey-wrench rectangular head block with cutout + worm pocket.
    Adapted from monkeyhead `_build_head_frame`. Authored at world X/Y about
    the head junction (HEAD_X0..HEAD_X1)."""
    hs = head_scale
    head_x0 = _crescent_handle_x1() + M_HEAD_X0_OFF
    head_x1 = head_x0 + M_HEAD_LEN * hs
    # Scale the cutout walls with hs too, so the channel X-width stays
    # 0.026*hs and the (0.027*hs) jaw shoe always overlaps the channel
    # shoulders by ~1 mm (captured T-slot fit) at every head scale.
    cut_x0 = head_x0 + M_CUT_BACK * hs
    cut_x1 = head_x1 - M_CUT_FRONT * hs
    y_bot = M_HEAD_Y_BOT * hs
    y_top = M_HEAD_Y_TOP * hs
    cut_y_bot = M_CUT_Y_BOT * hs
    cut_y_top = M_CUT_Y_TOP * hs

    plate = (
        cq.Workplane("XY")
        .center((head_x0 + head_x1) * 0.5, (y_bot + y_top) * 0.5)
        .rect(head_x1 - head_x0, y_top - y_bot)
        .extrude(M_HEAD_T * 0.5, both=True)
    )
    try:
        plate = plate.edges("|Z").fillet(0.002)
    except Exception:
        pass

    cutout = (
        cq.Workplane("XY")
        .center((cut_x0 + cut_x1) * 0.5, (cut_y_bot + cut_y_top) * 0.5)
        .rect(cut_x1 - cut_x0, cut_y_top - cut_y_bot)
        .extrude(M_HEAD_T, both=True)
    )
    plate = plate.cut(cutout)

    # Worm pocket: bore along X through the back wall.
    worm_cy = M_JAW_FACE_Y_REST - M_JAW_SHOE_H - M_JAW_SHANK_H * 0.5
    pocket_start = _crescent_handle_x1()
    pocket_end = cut_x0 + 0.004
    pocket = (
        cq.Workplane("YZ")
        .workplane(offset=pocket_start)
        .center(worm_cy, 0.0)
        .circle(M_WORM_R + 0.001)
        .extrude(pocket_end - pocket_start)
    )
    plate = plate.cut(pocket)
    return plate, head_x0, head_x1, cut_x0, cut_x1


def _crescent_handle_x0() -> float:
    return C_RING_R_OUTER * 0.55


def _crescent_handle_x1() -> float:
    # Head anchor X (handle/head junction). Note: handle length scaling is folded
    # into the handle builders; the head junction stays at the nominal location so
    # head-local landmarks remain valid. Handle length scale moves the BUTT, not
    # the head.
    return _crescent_handle_x0() + C_HANDLE_LEN


def _build_crescent_worm() -> cq.Workplane:
    """Knurled worm thumb-wheel: short cylinder along local X. Parent A."""
    wheel = cq.Workplane("YZ").circle(C_WORM_R).extrude(C_WORM_HALF_LEN, both=True)
    grooves = cq.Workplane("YZ")
    for i in range(16):
        a = i * (2.0 * math.pi / 16.0)
        slot = (
            cq.Workplane("YZ")
            .center(C_WORM_R * math.cos(a), C_WORM_R * math.sin(a))
            .circle(0.0008)
            .extrude(C_WORM_HALF_LEN + 0.0005, both=True)
        )
        grooves = grooves.add(slot)
    try:
        wheel = wheel.cut(grooves.combine())
    except Exception:
        pass
    return wheel


def _build_monkey_worm() -> cq.Workplane:
    """Knurled worm thumb-wheel (monkey): short cylinder along X. monkeyhead."""
    wheel = cq.Workplane("YZ").circle(M_WORM_R).extrude(M_WORM_HALF_LEN, both=True)
    grooves = cq.Workplane("YZ")
    for i in range(14):
        a = i * (2.0 * math.pi / 14.0)
        slot = (
            cq.Workplane("YZ")
            .center(M_WORM_R * math.cos(a), M_WORM_R * math.sin(a))
            .circle(0.0008)
            .extrude(M_WORM_HALF_LEN + 0.0005, both=True)
        )
        grooves = grooves.add(slot)
    try:
        wheel = wheel.cut(grooves.combine())
    except Exception:
        pass
    return wheel


def _build_crescent_movable_jaw(*, with_rack: bool, head_scale: float = 1.0) -> cq.Workplane:
    """Crescent movable jaw: jaw block + enclosed rack shank (+ optional rack
    teeth). Adapted from parent A / thumbslide `_build_movable_jaw`. The shank
    Y-extent tracks head_scale so it always lightly embeds into the (scaled) head
    slide-slot walls and stays captured (no isolated-jaw island when head grows)."""
    hs = head_scale
    block = (
        cq.Workplane("XY")
        .moveTo(0.0, C_MOUTH_FLOOR_Y)
        .lineTo(0.0, C_JAW_BLOCK_TOP)
        .lineTo(-0.010, C_JAW_BLOCK_TOP)
        .lineTo(-C_JAW_BLOCK_LEN, 0.024)
        .lineTo(-C_JAW_BLOCK_LEN, C_MOUTH_FLOOR_Y)
        .close()
        .extrude(0.006, both=True)
    )
    try:
        block = block.edges("|Z").fillet(0.0012)
    except Exception:
        pass

    # Shank Y center/extent follow the slot so it stays an embedded captured rail.
    sy0, sy1 = C_SHANK_Y0 * hs, C_SHANK_Y1 * hs
    shank = (
        cq.Workplane("XY")
        .center((C_SHANK_X0 + C_SHANK_X1) * 0.5, (sy0 + sy1) * 0.5)
        .rect(C_SHANK_X1 - C_SHANK_X0, sy1 - sy0)
        .extrude(C_SHANK_HALF_T, both=True)
    )
    jaw = block.union(shank)

    if with_rack:
        rack = None
        # Rack teeth sit on the shank underside; track the (scaled) shank y0 so
        # they stay fused to the shank (a fixed y would float when head grows).
        rack_y = sy0 - 0.00075
        for i in range(5):
            x = -0.008 - i * 0.004
            tooth = (
                cq.Workplane("XY")
                .center(x, rack_y)
                .rect(0.002, 0.002)
                .extrude(0.004, both=True)
            )
            rack = tooth if rack is None else rack.union(tooth)
        if rack is not None:
            try:
                jaw = jaw.union(rack)
            except Exception:
                pass
    return jaw


def _build_monkey_movable_jaw(*, head_scale: float) -> cq.Workplane:
    """Monkey movable jaw: shoe block + shank + rack teeth (own frame: gripping
    face at local y = 0). Adapted from monkeyhead `_build_movable_jaw`. The shoe
    width tracks head_scale so the jaw spans the (scaled) head cutout channel and
    stays captured (no isolated-jaw island when the head grows)."""
    hs = head_scale
    shoe_xw = M_JAW_SHOE_XW * hs
    shank_xw = M_JAW_SHANK_XW * hs
    shoe = (
        cq.Workplane("XY")
        .center(0.0, -M_JAW_SHOE_H * 0.5)
        .rect(shoe_xw, M_JAW_SHOE_H)
        .extrude(M_HEAD_T * 0.5 - 0.001, both=True)
    )
    try:
        shoe = shoe.edges("|Z").fillet(0.001)
    except Exception:
        pass

    shank = (
        cq.Workplane("XY")
        .center(0.0, -M_JAW_SHOE_H - M_JAW_SHANK_H * 0.5)
        .rect(shank_xw, M_JAW_SHANK_H)
        .extrude(M_SHANK_HALF_T, both=True)
    )
    jaw = shoe.union(shank)

    rack_y_start = -M_JAW_SHOE_H - M_JAW_SHANK_H * 0.8
    for i in range(M_RACK_N):
        ty = rack_y_start + i * (M_JAW_SHANK_H * 0.6 / max(M_RACK_N - 1, 1))
        tooth = (
            cq.Workplane("XY")
            .center(-shank_xw * 0.5 - M_RACK_TOOTH_DX * 0.5, ty)
            .rect(M_RACK_TOOTH_DX, M_RACK_TOOTH_DY)
            .extrude(M_RACK_TOOTH_DZ, both=True)
        )
        try:
            jaw = jaw.union(tooth)
        except Exception:
            pass
    return jaw


def _build_thumb_lever() -> cq.Workplane:
    """Thumb lever: engagement tab + arm + pad, pivot at origin. thumbslide."""
    tab_hw = 0.003
    pts: list[tuple[float, float]] = [
        (-tab_hw, C_LEVER_TAB_TIP_Y),
        (tab_hw + 0.001, C_LEVER_TAB_TIP_Y),
        (C_LEVER_ARM_HW, 0.003),
        (C_LEVER_ARM_HW, -C_LEVER_ARM_LEN + 0.002),
        (C_LEVER_PAD_HW, -C_LEVER_ARM_LEN),
        (C_LEVER_PAD_HW, -C_LEVER_ARM_LEN - C_LEVER_PAD_LEN),
        (-C_LEVER_PAD_HW, -C_LEVER_ARM_LEN - C_LEVER_PAD_LEN),
        (-C_LEVER_PAD_HW, -C_LEVER_ARM_LEN),
        (-C_LEVER_ARM_HW, -C_LEVER_ARM_LEN + 0.002),
        (-C_LEVER_ARM_HW, 0.003),
        (-tab_hw - 0.001, C_LEVER_TAB_TIP_Y - 0.001),
    ]
    body = cq.Workplane("XY").polyline(pts).close().extrude(C_LEVER_T)
    try:
        body = body.edges("|Z").fillet(0.001)
    except Exception:
        pass
    bore = cq.Workplane("XY").circle(C_PIVOT_BOSS_R + 0.0005).extrude(C_LEVER_T * 3, both=True)
    body = body.cut(bore)
    return body


# --- Crescent handle builders (rebased to world +X, fused into wrench_body). ---
def _crescent_handle_geom_flat(r: ResolvedWrenchConfig) -> cq.Workplane:
    """Flat steel handle (crescent): box ring butt + tapered flat bar.
    Parent A inline handle + ring. Returns geometry centered at z=0 (caller
    lifts). Length scale moves the butt back; width scale widens the bar."""
    x1 = _crescent_handle_x1()
    girth = r.handle_girth_scale
    handle_w = C_HANDLE_W * girth
    handle_t = C_HANDLE_T * girth
    x0 = x1 - C_HANDLE_LEN * r.handle_len_scale
    ring_cx = x0 - C_RING_R_OUTER * 0.45

    ring = (
        cq.Workplane("XY")
        .center(ring_cx, 0.0)
        .circle(C_RING_R_OUTER)
        .extrude(C_RING_HALF_T, both=True)
    )
    hole = (
        cq.Workplane("XY")
        .center(ring_cx, 0.0)
        .polyline(_hex_profile(C_RING_HEX_AF))
        .close()
        .extrude(C_RING_HALF_T * 1.4, both=True)
    )
    ring = ring.cut(hole)

    handle = (
        cq.Workplane("XY")
        .moveTo(x0, -handle_w * 0.42)
        .lineTo(x0, handle_w * 0.42)
        .lineTo(x1, handle_w * 0.5)
        .lineTo(x1, -handle_w * 0.5)
        .close()
        .extrude(handle_t * 0.5, both=True)
        .edges("|Z")
        .fillet(0.003)
    )
    return ring.union(handle)


def _crescent_handle_z_lift(r: ResolvedWrenchConfig) -> float:
    """World Z lift so the lowest handle element rests at z=0 for this handle."""
    if r.handle == "flat_steel":
        return C_RING_HALF_T + 0.0005
    if r.handle == "tapered_wood":
        return CW_GRIP_MAX_R * r.handle_girth_scale + 0.001
    return CT_FERRULE_R * r.handle_girth_scale  # tubular


# ===========================================================================
# Pipe-spine lay-down helper (tool frame -> lying-flat world).
# ===========================================================================
def _pipe_ground_lift(r: ResolvedWrenchConfig) -> float:
    """Tool-Y offset so the lowest world-Z element rests at z=0. The frame body
    (thickest in tool Y) or the round wood/tube handle governs."""
    frame_half = P_FRAME_BODY_T / 2.0
    if r.handle == "tapered_wood":
        return max(frame_half, P_HANDLE_MAX_R * r.handle_girth_scale)
    if r.handle == "tubular":
        return max(frame_half, P_TUBE_BUTT_R * r.handle_girth_scale)
    return frame_half  # flat_steel: frame body governs


def _pipe_lay(r: ResolvedWrenchConfig, x: float, y: float, z: float) -> tuple[float, float, float]:
    """Map a tool-frame point to the lying-flat world (tool z -> world +X)."""
    return (z, x, y + _pipe_ground_lift(r))


# ===========================================================================
# Pipe head + driver + handle geometry (adapted from parent B / pipe_flatsteel).
# ===========================================================================
def _add_teeth_x(
    wp: cq.Workplane,
    *,
    x0: float,
    x1: float,
    z_face: float,
    y_half: float,
    tooth_h: float,
    n_teeth: int,
    pointing_z: float,
) -> cq.Workplane:
    """Union a row of triangular teeth along X onto a jaw face at z=z_face."""
    span = x1 - x0
    pitch = span / n_teeth
    result = wp
    for i in range(n_teeth):
        xc = x0 + (i + 0.5) * pitch
        tooth = (
            cq.Workplane("XZ")
            .moveTo(xc - pitch * 0.31, z_face)
            .lineTo(xc, z_face + pointing_z * tooth_h)
            .lineTo(xc + pitch * 0.31, z_face)
            .close()
            .extrude(y_half, both=True)
        )
        result = result.union(tooth)
    return result


def _build_pipe_head_frame_geometry(head_scale: float) -> cq.Workplane:
    """Pipe head: housing + shank + nut window + jaw channel + serrated hook.
    Adapted from parent B `build_head_frame_geometry`. head_scale widens the
    housing/hook block; the window/channel/teeth stay native for fit."""
    hw = P_FRAME_BODY_W * head_scale
    frame = (
        cq.Workplane("XY")
        .box(hw, P_FRAME_BODY_T, P_FRAME_BODY_TOP - P_FRAME_BODY_BOTTOM, centered=(True, True, False))
        .translate((0, 0, P_FRAME_BODY_BOTTOM))
        .edges("|Z")
        .fillet(0.004)
    )
    frame = frame.translate((0.006, 0, 0))

    shank = (
        cq.Workplane("XY")
        .box(P_SHANK_W, P_SHANK_T, P_SHANK_TOP - P_SHANK_BOTTOM + 0.012, centered=(True, True, False))
        .translate((-0.004, 0, P_SHANK_BOTTOM))
        .edges("|Z")
        .fillet(0.003)
    )
    groove = (
        cq.Workplane("XY")
        .box(0.006, 0.010, 0.090, centered=(True, True, False))
        .translate((-0.004 + P_SHANK_W / 2 - 0.002, 0, P_SHANK_BOTTOM + 0.030))
    )
    shank = shank.cut(groove)
    head = frame.union(shank)

    window = (
        cq.Workplane("XY")
        .box(P_WINDOW_W, P_FRAME_BODY_T + 0.02, P_WINDOW_H, centered=True)
        .translate((0.006, 0, P_WINDOW_Z))
    )
    head = head.cut(window)

    slot = (
        cq.Workplane("XY")
        .box(0.050, 2 * P_SLOT_HALF_T, P_SLOT_Z1 - P_SLOT_Z0, centered=(False, True, False))
        .translate((-0.002, 0, P_SLOT_Z0))
    )
    head = head.cut(slot)

    hook = (
        cq.Workplane("XZ")
        .moveTo(-0.022, 0.292)
        .lineTo(-0.022, 0.350)
        .lineTo(0.008, 0.362)
        .lineTo(0.040, 0.356)
        .lineTo(0.058, 0.340)
        .lineTo(0.056, 0.326)
        .lineTo(0.016, 0.328)
        .close()
        .extrude(P_HOOK_T_HALF, both=True)
    )
    head = head.union(hook)
    head = _add_teeth_x(
        head, x0=0.020, x1=0.052, z_face=P_HOOK_TEETH_FACE,
        y_half=P_HOOK_T_HALF - 0.002, tooth_h=P_HOOK_TOOTH_H, n_teeth=6, pointing_z=-1.0,
    )
    return head


def _build_pipe_movable_jaw_geometry() -> cq.Workplane:
    """Pipe movable jaw: screw bar + forward toothed head (teeth up). Parent B."""
    bar = (
        cq.Workplane("XY")
        .box(0.013, 0.011, P_JAW_BAR_TOP + 0.085, centered=(True, True, False))
        .translate((0.004, 0, -0.085))
        .edges("|Z")
        .fillet(0.002)
    )
    head = (
        cq.Workplane("XY")
        .box(0.046, 2 * (P_SLOT_HALF_T - 0.001), P_JAW_HEAD_Z1 - P_JAW_HEAD_Z0, centered=(True, True, False))
        .translate((0.031, 0, P_JAW_HEAD_Z0))
        .edges("|Z")
        .fillet(0.002)
    )
    jaw = bar.union(head)
    jaw = _add_teeth_x(
        jaw, x0=0.016, x1=0.050, z_face=P_JAW_TEETH_FACE,
        y_half=P_SLOT_HALF_T - 0.003, tooth_h=P_JAW_TOOTH_H, n_teeth=6, pointing_z=1.0,
    )
    return jaw


def _build_pipe_ferrule_geom() -> cq.Workplane:
    prof = [(0.0, 0.0), (0.013, 0.0), (0.0145, 0.006), (0.0135, 0.026), (0.0, 0.026)]
    return (
        cq.Workplane("XZ")
        .polyline([(rr, z) for (rr, z) in prof])
        .close()
        .revolve(360, (0, 0, 0), (0, 1, 0))
    )


def _build_pipe_wood_handle_geom(girth: float) -> cq.Workplane:
    z_top = P_HANDLE_TOP
    z_bottom = P_HANDLE_BOTTOM + 0.006
    mr = P_HANDLE_MAX_R * girth
    pts = [
        (0.0, z_top),
        (0.0125 * girth, z_top),
        (0.0150 * girth, z_top - 0.025),
        (mr, z_top - 0.060),
        (0.0150 * girth, z_top - 0.095),
        (0.0105 * girth, z_bottom + 0.006),
        (0.0, z_bottom),
    ]
    return (
        cq.Workplane("XZ")
        .polyline([(rr, z) for (rr, z) in pts])
        .close()
        .revolve(360, (0, 0, 0), (0, 1, 0))
    )


def _build_pipe_worn_band_geom(girth: float) -> cq.Workplane:
    z_top = P_HANDLE_TOP - 0.072
    z_bottom = P_HANDLE_BOTTOM + 0.020
    pts = [
        (0.0, z_top),
        (0.0150 * girth, z_top),
        (0.0130 * girth, z_bottom),
        (0.0, z_bottom),
    ]
    return (
        cq.Workplane("XZ")
        .polyline([(rr, z) for (rr, z) in pts])
        .close()
        .revolve(360, (0, 0, 0), (0, 1, 0))
    )


def _build_pipe_butt_cap_geom(girth: float) -> cq.Workplane:
    z0 = P_HANDLE_BOTTOM + 0.012
    z1 = P_HANDLE_BOTTOM
    pts = [(0.0, z0), (0.0105 * girth, z0), (0.0075 * girth, z1 + 0.006), (0.0, z1)]
    return (
        cq.Workplane("XZ")
        .polyline([(rr, z) for (rr, z) in pts])
        .close()
        .revolve(360, (0, 0, 0), (0, 1, 0))
    )


def _build_pipe_tube_handle_geom(girth: float) -> cq.Workplane:
    """Hollow round tube + end butt cap (tubularshank)."""
    o_r = P_TUBE_OR * girth
    i_r = P_TUBE_IR * girth
    z_top = P_HANDLE_TOP
    z_bot = P_TUBE_BOTTOM + P_TUBE_BUTT_LEN
    # Annular tube cross-section revolved about the X axis.
    tube_prof = (
        cq.Workplane("XZ")
        .moveTo(i_r, z_bot)
        .lineTo(o_r, z_bot)
        .lineTo(o_r, z_top)
        .lineTo(i_r, z_top)
        .close()
    )
    tube = tube_prof.revolve(360, (0, 0, 0), (0, 1, 0))
    # Solid butt cap disc at the bottom.
    butt = (
        cq.Workplane("XZ")
        .moveTo(0.0, P_TUBE_BOTTOM)
        .lineTo(P_TUBE_BUTT_R * girth, P_TUBE_BOTTOM)
        .lineTo(P_TUBE_BUTT_R * girth, P_TUBE_BOTTOM + P_TUBE_BUTT_LEN)
        .lineTo(0.0, P_TUBE_BOTTOM + P_TUBE_BUTT_LEN)
        .close()
        .revolve(360, (0, 0, 0), (0, 1, 0))
    )
    return tube.union(butt)


def _build_pipe_grip_rib_geom(z_center: float, girth: float) -> cq.Workplane:
    """A single annular grip rib around the tube (tubularshank grip ribs)."""
    rib = (
        cq.Workplane("XZ")
        .moveTo(P_TUBE_OR * girth, z_center - P_GRIP_RIB_LEN / 2.0)
        .lineTo(P_GRIP_RIB_R * girth, z_center - P_GRIP_RIB_LEN / 2.0)
        .lineTo(P_GRIP_RIB_R * girth, z_center + P_GRIP_RIB_LEN / 2.0)
        .lineTo(P_TUBE_OR * girth, z_center + P_GRIP_RIB_LEN / 2.0)
        .close()
        .revolve(360, (0, 0, 0), (0, 1, 0))
    )
    return rib


def _build_pipe_flat_handle_geom(r: ResolvedWrenchConfig) -> cq.Workplane:
    """Flat forged steel handle (pipe spine): tapered bar + hex ring at butt.
    Adapted from pipe_flatsteel `build_flat_handle_geometry`."""
    girth = r.handle_girth_scale
    half_t = P_FLAT_HANDLE_T * girth / 2.0
    cx = -0.004
    z_top = P_HANDLE_TOP
    # Length scale stretches the bar downward (butt away from the head).
    z_handle_bottom = P_HANDLE_BOTTOM * r.handle_len_scale
    z_bar_end = z_handle_bottom + 0.024
    z_ring_c = z_handle_bottom + 0.014
    w_top = P_FLAT_HANDLE_W_TOP * girth
    w_ring = P_FLAT_HANDLE_W_RING * girth

    bar = (
        cq.Workplane("XZ")
        .moveTo(cx - w_top / 2, z_top)
        .lineTo(cx + w_top / 2, z_top)
        .lineTo(cx + w_ring / 2, z_bar_end)
        .lineTo(cx - w_ring / 2, z_bar_end)
        .close()
        .extrude(half_t, both=True)
    )
    ring_outer = (
        cq.Workplane("XZ")
        .circle(P_FLAT_RING_OD / 2)
        .extrude(half_t, both=True)
        .translate((cx, 0.0, z_ring_c))
    )
    hex_d = P_FLAT_RING_AF / (math.sqrt(3.0) / 2.0)
    hex_cut = (
        cq.Workplane("XZ")
        .polygon(6, hex_d)
        .extrude(half_t + 0.002, both=True)
        .translate((cx, 0.0, z_ring_c))
    )
    ring = ring_outer.cut(hex_cut)
    handle = bar.union(ring)

    n_grooves = 4
    groove_span = z_top - z_bar_end - 0.030
    for i in range(n_grooves):
        z_g = z_top - 0.018 - i * (groove_span / (n_grooves - 1))
        groove = (
            cq.Workplane("XY")
            .box(w_ring + 0.004, 0.0008, 0.0018, centered=True)
            .translate((cx, half_t - 0.0004, z_g))
        )
        handle = handle.cut(groove)
    return handle


# ===========================================================================
# CRESCENT-SPINE root builder (wrench_body, in-place).
# ===========================================================================
def _build_crescent_root(model, r, mats, *, assets) -> tuple:
    """Build the crescent-spine root `wrench_body`: handle (per `r.handle`,
    rebased to world +X) fused with the tilted/square head. Returns
    (body_part, root_visual_name, tilt, z_lift, head_x1, slide_origin_args).

    The head shape depends on the head_mechanism (worm/thumb = lens crescent,
    monkey = rectangular). The handle shape depends on r.handle."""
    head = r.head_mechanism
    z_lift = _crescent_handle_z_lift(r)
    x1 = _crescent_handle_x1()
    tilt = math.radians(C_HEAD_TILT_DEG)

    body = model.part("wrench_body")
    root_visual = "body_shell"

    if head == "monkey_head":
        head_local, head_x0, head_x1, cut_x0, cut_x1 = _build_monkey_head_local(head_scale=r.head_scale)
        head_geom = head_local
    else:
        with_boss = head == "thumb_slide"
        head_local = _build_crescent_head_local(with_boss=with_boss, head_scale=r.head_scale)
        head_geom = (
            head_local
            .rotate((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), C_HEAD_TILT_DEG)
            .translate((x1, 0.0, 0.0))
        )

    # --- Handle geometry (rebased to world +X per r.handle). ---
    if r.handle == "flat_steel":
        # Flat steel + hex ring, fused with the head into one shell.
        handle_geom = _crescent_handle_geom_flat(r)
        body_geom = handle_geom.union(head_geom).translate((0.0, 0.0, z_lift))
        body.visual(
            mesh_from_cadquery(body_geom, "wrench_body_flat", assets=assets),
            material=mats["steel"],
            name=root_visual, material_class_id=("metal.chrome_polished" if r.palette_style in {"bright_chrome_steel", "blue_japanned_steel", "red_wood_handle", "galvanized_tube", "dark_machined_steel"} else "metal.blackened_gunmetal"),
        )
    elif r.handle == "tapered_wood":
        # Steel core (ring + tang + head) + wood grip + brass ferrule + steel
        # butt, all separate root visuals. Cross-spine wood (crescent_wood).
        core, grip, ferrule, cap = _crescent_wood_handle_geoms(r, head_geom)
        body.visual(
            mesh_from_cadquery(core.translate((0.0, 0.0, z_lift)), "wrench_body_core", assets=assets),
            material=mats["steel"], name=root_visual, material_class_id=("metal.chrome_polished" if r.palette_style in {"bright_chrome_steel", "blue_japanned_steel", "red_wood_handle", "galvanized_tube", "dark_machined_steel"} else "metal.blackened_gunmetal"),
        )
        body.visual(
            mesh_from_cadquery(grip.translate((0.0, 0.0, z_lift)), "wrench_wood_grip", assets=assets),
            material=mats["wood"], name="wood_grip", material_class_id=("wood.polished_varnished" if r.palette_style in {"bright_chrome_steel", "black_oxide_steel", "blue_japanned_steel", "galvanized_tube", "dark_machined_steel"} else "wood.painted_clean"),
        )
        body.visual(
            mesh_from_cadquery(ferrule.translate((0.0, 0.0, z_lift)), "wrench_ferrule", assets=assets),
            material=mats["brass"], name="ferrule_collar", material_class_id="metal.brass_polished",
        )
        body.visual(
            mesh_from_cadquery(cap.translate((0.0, 0.0, z_lift)), "wrench_butt_cap", assets=assets),
            material=mats["butt"], name="butt_cap", material_class_id=("metal.steel_bare" if r.palette_style in {"bright_chrome_steel", "blue_japanned_steel", "red_wood_handle", "galvanized_tube", "dark_machined_steel"} else "metal.blackened_gunmetal"),
        )
    else:  # tubular
        shank = _crescent_tubular_shank_geom(r)
        body_geom = shank.union(head_geom).translate((0.0, 0.0, z_lift))
        body.visual(
            mesh_from_cadquery(body_geom, "wrench_body_tube", assets=assets),
            material=mats["steel"],
            name=root_visual, material_class_id=("metal.chrome_polished" if r.palette_style in {"bright_chrome_steel", "blue_japanned_steel", "red_wood_handle", "galvanized_tube", "dark_machined_steel"} else "metal.blackened_gunmetal"),
        )

    body.inertial = Inertial.from_geometry(
        Box((0.30, 0.08, max(0.02, 2.0 * z_lift))),
        mass=0.45,
        origin=Origin(xyz=(x1 * 0.4, 0.0, z_lift)),
    )
    return body, root_visual, tilt, z_lift, x1


def _crescent_wood_handle_geoms(r: ResolvedWrenchConfig, head_geom: cq.Workplane):
    """Steel core (ring + tang + head), wood grip, brass ferrule, steel butt.
    Adapted from crescent_wood. Length scale moves the butt back; girth scales
    radii. All returned in body frame at z=0 (caller lifts)."""
    x1 = _crescent_handle_x1()
    girth = r.handle_girth_scale
    grip_x0 = x1 - C_HANDLE_LEN * r.handle_len_scale
    grip_x1 = x1
    ring_cx = grip_x0 - C_RING_R_OUTER * 0.35

    ring = (
        cq.Workplane("XY")
        .center(ring_cx, 0.0)
        .circle(C_RING_R_OUTER)
        .extrude(C_RING_HALF_T, both=True)
    )
    hole = (
        cq.Workplane("XY")
        .center(ring_cx, 0.0)
        .polyline(_hex_profile(C_RING_HEX_AF))
        .close()
        .extrude(C_RING_HALF_T * 1.4, both=True)
    )
    ring = ring.cut(hole)

    # Hidden steel tang running from ring through grip and well INTO the head
    # (reach past x1 so a down-scaled head still fuses with the tang; the head
    # neck back-edge moves toward +x as head_scale shrinks).
    tang = (
        cq.Workplane("YZ")
        .workplane(offset=ring_cx)
        .circle(CW_TANG_R)
        .extrude(grip_x1 - ring_cx + 0.030)
    )
    core = ring.union(tang).union(head_geom)

    # Wood grip lathe revolve along world +X.
    gmax = CW_GRIP_MAX_R * girth
    gbutt = CW_GRIP_BUTT_R * girth
    ghead = CW_GRIP_HEAD_R * girth
    hlen = grip_x1 - grip_x0
    profile = [
        (grip_x0, 0.0),
        (grip_x0 + 0.004, gbutt * 0.6),
        (grip_x0 + 0.012, gbutt),
        (grip_x0 + hlen * 0.13, gbutt + 0.003),
        (grip_x0 + hlen * 0.24, gmax * 0.80),
        (grip_x0 + hlen * 0.37, gmax * 0.95),
        (grip_x0 + hlen * 0.48, gmax),
        (grip_x0 + hlen * 0.61, gmax * 0.97),
        (grip_x0 + hlen * 0.74, gmax * 0.88),
        (grip_x0 + hlen * 0.87, ghead + 0.002),
        (grip_x1 - 0.005, ghead),
        (grip_x1, ghead),
        (grip_x1, 0.0),
    ]
    grip = (
        cq.Workplane("XY")
        .spline(profile)
        .close()
        .revolve(360, (grip_x0, 0.0), (grip_x1, 0.0))
    )

    ferrule_x0 = grip_x1 - CW_FERRULE_LEN
    ferrule = (
        cq.Workplane("YZ")
        .workplane(offset=ferrule_x0)
        .circle(CW_FERRULE_R * girth)
        .extrude(CW_FERRULE_LEN)
    )
    try:
        ferrule = ferrule.edges("|X").chamfer(0.0008)
    except Exception:
        pass

    cap = (
        cq.Workplane("YZ")
        .workplane(offset=grip_x0)
        .circle(CW_BUTT_CAP_R * girth)
        .extrude(CW_BUTT_CAP_LEN)
    )
    try:
        cap = cap.edges("|X").chamfer(0.0006)
    except Exception:
        pass
    return core, grip, ferrule, cap


def _crescent_tubular_shank_geom(r: ResolvedWrenchConfig) -> cq.Workplane:
    """Round hollow tube shank + end ferrule ring (crescent_tubular). Length
    scale moves the butt back; girth scales radii. In body frame at z=0."""
    x1 = _crescent_handle_x1()
    girth = r.handle_girth_scale
    s_r = CT_SHANK_R * girth
    s_ir = (CT_SHANK_R - CT_SHANK_WALL) * girth
    fer_r = CT_FERRULE_R * girth
    x0 = (x1 - C_HANDLE_LEN * r.handle_len_scale) + CT_FERRULE_LEN + 0.003

    tube_profile = (
        cq.Workplane("XZ")
        .moveTo(x0, s_ir)
        .lineTo(x1, s_ir)
        .lineTo(x1, s_r)
        .lineTo(x0, s_r)
        .close()
    )
    tube = tube_profile.revolve(360, (0, 0), (x1 + 1, 0))
    ferrule_profile = (
        cq.Workplane("XZ")
        .moveTo(x0 - CT_FERRULE_LEN, s_ir)
        .lineTo(x0, s_ir)
        .lineTo(x0, fer_r)
        .lineTo(x0 - CT_FERRULE_LEN, fer_r)
        .close()
    )
    ferrule = ferrule_profile.revolve(360, (0, 0), (x0 + 1, 0))
    return tube.union(ferrule)


# ===========================================================================
# CRESCENT-SPINE driver/jaw emit (worm_rack / monkey / thumb).
# ===========================================================================
def _emit_crescent_mechanism(model, r, body, mats, *, assets) -> list[str]:
    head = r.head_mechanism
    z_lift = _crescent_handle_z_lift(r)
    x1 = _crescent_handle_x1()
    emitted: list[str] = []

    if head == "monkey_head":
        # Square head: jaw slides along -Y; worm spins about +X.
        _, head_x0, head_x1, cut_x0, cut_x1 = _build_monkey_head_local(head_scale=r.head_scale)
        movable = model.part("movable_jaw")
        movable.visual(
            mesh_from_cadquery(_build_monkey_movable_jaw(head_scale=r.head_scale), "monkey_jaw", assets=assets),
            material=mats["steel_dark"], name="jaw_shell", material_class_id=("metal.steel_bare" if r.palette_style in {"bright_chrome_steel", "blue_japanned_steel", "red_wood_handle", "galvanized_tube", "dark_machined_steel"} else "metal.blackened_gunmetal"),
        )
        movable.inertial = Inertial.from_geometry(
            Box((M_JAW_SHOE_XW * r.head_scale, M_JAW_SHOE_H + M_JAW_SHANK_H, M_HEAD_T)),
            mass=0.05, origin=Origin(xyz=(0.0, -M_JAW_SHOE_H, 0.0)),
        )
        jaw_origin_x = (cut_x0 + cut_x1) * 0.5
        model.articulation(
            "jaw_slide", ArticulationType.PRISMATIC, parent=body, child=movable,
            origin=Origin(xyz=(jaw_origin_x, M_JAW_FACE_Y_REST, z_lift)),
            axis=(0.0, -1.0, 0.0),
            motion_limits=MotionLimits(effort=120.0, velocity=0.05, lower=0.0, upper=r.jaw_travel),
        )
        emitted.append("movable_jaw")

        worm = model.part("worm_screw")
        worm.visual(
            mesh_from_cadquery(_build_monkey_worm(), "monkey_worm", assets=assets),
            material=mats["knurl"], name="worm_wheel", material_class_id=("metal.steel_bare" if r.palette_style in {"bright_chrome_steel", "blue_japanned_steel", "red_wood_handle", "galvanized_tube", "dark_machined_steel"} else "metal.blackened_gunmetal"),
        )
        worm.inertial = Inertial.from_geometry(
            Cylinder(radius=M_WORM_R, length=2.0 * M_WORM_HALF_LEN), mass=0.01,
            origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        )
        worm_cy = M_JAW_FACE_Y_REST - M_JAW_SHOE_H - M_JAW_SHANK_H * 0.5
        worm_cx = x1 + 0.010
        model.articulation(
            "worm_turn", ArticulationType.CONTINUOUS, parent=body, child=worm,
            origin=Origin(xyz=(worm_cx, worm_cy, z_lift)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=2.0, velocity=10.0),
        )
        emitted.append("worm_screw")
        return emitted

    # worm_rack_crescent or thumb_slide: tilted lens head, slide along local -x.
    tilt = math.radians(C_HEAD_TILT_DEG)
    c, s = math.cos(tilt), math.sin(tilt)
    with_rack = head == "worm_rack_crescent"
    movable = model.part("movable_jaw")
    movable.visual(
        mesh_from_cadquery(_build_crescent_movable_jaw(with_rack=with_rack, head_scale=r.head_scale), "crescent_jaw", assets=assets),
        material=mats["steel_dark"], name="jaw_shell", material_class_id=("metal.steel_bare" if r.palette_style in {"bright_chrome_steel", "blue_japanned_steel", "red_wood_handle", "galvanized_tube", "dark_machined_steel"} else "metal.blackened_gunmetal"),
    )
    movable.inertial = Inertial.from_geometry(
        Box((C_JAW_BLOCK_LEN + 0.026, C_JAW_BLOCK_TOP, C_HEAD_T)),
        mass=0.05, origin=Origin(xyz=(-0.008, 0.014, 0.0)),
    )
    model.articulation(
        "jaw_slide", ArticulationType.PRISMATIC, parent=body, child=movable,
        origin=Origin(
            xyz=(x1 + C_JAW_ORIGIN_LX * c, C_JAW_ORIGIN_LX * s, z_lift),
            rpy=(0.0, 0.0, tilt),
        ),
        axis=(-1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=120.0, velocity=0.05, lower=0.0, upper=r.jaw_travel),
    )
    emitted.append("movable_jaw")

    if head == "worm_rack_crescent":
        worm = model.part("worm_screw")
        worm.visual(
            mesh_from_cadquery(_build_crescent_worm(), "crescent_worm", assets=assets),
            material=mats["knurl"], name="worm_wheel", material_class_id=("metal.steel_bare" if r.palette_style in {"bright_chrome_steel", "blue_japanned_steel", "red_wood_handle", "galvanized_tube", "dark_machined_steel"} else "metal.blackened_gunmetal"),
        )
        worm.inertial = Inertial.from_geometry(
            Cylinder(radius=C_WORM_R, length=2.0 * C_WORM_HALF_LEN), mass=0.01,
            origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        )
        model.articulation(
            "worm_turn", ArticulationType.CONTINUOUS, parent=body, child=worm,
            origin=Origin(
                xyz=(x1 + C_WORM_LCX * c - C_WORM_LCY * s, C_WORM_LCX * s + C_WORM_LCY * c, z_lift),
                rpy=(0.0, 0.0, tilt),
            ),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=2.0, velocity=10.0),
        )
        emitted.append("worm_screw")
    else:  # thumb_slide: REVOLUTE lever about Z on the head face boss
        lever = model.part("thumb_lever")
        lever.visual(
            mesh_from_cadquery(_build_thumb_lever(), "thumb_lever", assets=assets),
            material=mats["accent"], name="lever_shell", material_class_id=("metal.steel_bare" if r.palette_style in {"bright_chrome_steel", "black_oxide_steel", "red_wood_handle", "dark_machined_steel"} else "metal.paint_coated"),
        )
        # Grip ridges on the thumb pad (Rule 1: inline lever visuals, no joint).
        ridge_w = C_LEVER_PAD_HW * 1.50
        n_ridges = r.grip_count
        for i in range(n_ridges):
            y_pos = -(C_LEVER_ARM_LEN + (i + 0.5) * (C_LEVER_PAD_LEN / n_ridges))
            ridge_geom = cq.Workplane("XY").rect(ridge_w, 0.0015).extrude(0.0008).translate((0.0, y_pos, C_LEVER_T))
            lever.visual(
                mesh_from_cadquery(ridge_geom, f"grip_ridge_{i}", assets=assets),
                material=mats["grip"], name=f"grip_ridge_{i}", material_class_id="rubber.directional_grooved",
            )
        lever.inertial = Inertial.from_geometry(
            Box((2.0 * C_LEVER_PAD_HW, C_LEVER_ARM_LEN + C_LEVER_PAD_LEN, C_LEVER_T)),
            mass=0.02, origin=Origin(xyz=(0.0, -C_LEVER_ARM_LEN * 0.5, C_LEVER_T / 2.0)),
        )
        model.articulation(
            "lever_pivot", ArticulationType.REVOLUTE, parent=body, child=lever,
            origin=Origin(
                xyz=(
                    x1 + C_LEVER_PIVOT_LX * c - C_LEVER_PIVOT_LY * s,
                    C_LEVER_PIVOT_LX * s + C_LEVER_PIVOT_LY * c,
                    z_lift + C_HEAD_T * 0.5,
                ),
                rpy=(0.0, 0.0, tilt),
            ),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=15.0, velocity=3.0, lower=0.0, upper=r.lever_travel),
        )
        emitted.append("thumb_lever")
    return emitted


# ===========================================================================
# PIPE-SPINE root + driver/jaw emit (screw_nut_pipe).
# ===========================================================================
def _build_pipe_root(model, r, mats, *, assets) -> tuple:
    """Build the pipe-spine root `head_frame` (laid flat) + the handle (per
    r.handle, authored in tool frame then `_lay()`)."""
    head_frame = model.part("head_frame")
    root_visual = "frame_steel"
    head_frame.visual(
        mesh_from_cadquery(_build_pipe_head_frame_geometry(r.head_scale), "head_frame_steel", assets=assets),
        origin=Origin(xyz=_pipe_lay(r, 0.0, 0.0, 0.0), rpy=P_LAY_RPY),
        material=mats["steel"], name=root_visual, material_class_id=("metal.chrome_polished" if r.palette_style in {"bright_chrome_steel", "blue_japanned_steel", "red_wood_handle", "galvanized_tube", "dark_machined_steel"} else "metal.blackened_gunmetal"),
    )

    if r.handle == "flat_steel":
        head_frame.visual(
            mesh_from_cadquery(_build_pipe_flat_handle_geom(r), "flat_handle_steel", assets=assets),
            origin=Origin(xyz=_pipe_lay(r, 0.0, 0.0, 0.0), rpy=P_LAY_RPY),
            material=mats["steel"], name="flat_handle", material_class_id=("metal.chrome_polished" if r.palette_style in {"bright_chrome_steel", "blue_japanned_steel", "red_wood_handle", "galvanized_tube", "dark_machined_steel"} else "metal.blackened_gunmetal"),
        )
    elif r.handle == "tapered_wood":
        head_frame.visual(
            mesh_from_cadquery(_build_pipe_ferrule_geom(), "pipe_ferrule", assets=assets),
            origin=Origin(xyz=_pipe_lay(r, -0.004, 0.0, P_HANDLE_TOP), rpy=P_LAY_RPY),
            material=mats["butt"], name="ferrule", material_class_id=("metal.steel_bare" if r.palette_style in {"bright_chrome_steel", "blue_japanned_steel", "red_wood_handle", "galvanized_tube", "dark_machined_steel"} else "metal.blackened_gunmetal"),
        )
        head_frame.visual(
            mesh_from_cadquery(_build_pipe_wood_handle_geom(r.handle_girth_scale), "pipe_wood", assets=assets),
            origin=Origin(xyz=_pipe_lay(r, -0.004, 0.0, 0.0), rpy=P_LAY_RPY),
            material=mats["wood"], name="handle_body", material_class_id=("wood.polished_varnished" if r.palette_style in {"bright_chrome_steel", "black_oxide_steel", "blue_japanned_steel", "galvanized_tube", "dark_machined_steel"} else "wood.painted_clean"),
        )
        head_frame.visual(
            mesh_from_cadquery(_build_pipe_worn_band_geom(r.handle_girth_scale), "pipe_worn", assets=assets),
            origin=Origin(xyz=_pipe_lay(r, -0.004, 0.0, 0.0), rpy=P_LAY_RPY),
            material=mats["grip"], name="handle_worn", material_class_id=("rubber.smooth_plain" if r.palette_style in {"bright_chrome_steel", "black_oxide_steel", "blue_japanned_steel", "galvanized_tube", "dark_machined_steel"} else "wood.rustic_weathered"),
        )
        head_frame.visual(
            mesh_from_cadquery(_build_pipe_butt_cap_geom(r.handle_girth_scale), "pipe_butt", assets=assets),
            origin=Origin(xyz=_pipe_lay(r, -0.004, 0.0, 0.0), rpy=P_LAY_RPY),
            material=mats["butt"], name="butt_cap", material_class_id=("metal.steel_bare" if r.palette_style in {"bright_chrome_steel", "blue_japanned_steel", "red_wood_handle", "galvanized_tube", "dark_machined_steel"} else "metal.blackened_gunmetal"),
        )
    else:  # tubular
        head_frame.visual(
            mesh_from_cadquery(_build_pipe_tube_handle_geom(r.handle_girth_scale), "pipe_tube", assets=assets),
            origin=Origin(xyz=_pipe_lay(r, -0.004, 0.0, 0.0), rpy=P_LAY_RPY),
            material=mats["steel"], name="handle_tube", material_class_id=("metal.chrome_polished" if r.palette_style in {"bright_chrome_steel", "blue_japanned_steel", "red_wood_handle", "galvanized_tube", "dark_machined_steel"} else "metal.blackened_gunmetal"),
        )
        # Grip ribs evenly spaced along the tube (Rule 1: inline visuals).
        n_ribs = r.grip_count
        z0 = P_TUBE_BOTTOM + 0.020
        z1 = P_HANDLE_TOP - 0.030
        for i in range(n_ribs):
            zc = z0 + (z1 - z0) * (i / max(n_ribs - 1, 1))
            head_frame.visual(
                mesh_from_cadquery(_build_pipe_grip_rib_geom(zc, r.handle_girth_scale), f"grip_rib_{i}", assets=assets),
                origin=Origin(xyz=_pipe_lay(r, -0.004, 0.0, 0.0), rpy=P_LAY_RPY),
                material=mats["grip"], name=f"grip_rib_{i}", material_class_id="rubber.directional_grooved",
            )

    head_frame.inertial = Inertial.from_geometry(
        Box((0.40, 0.06, 0.05)),
        mass=0.55, origin=Origin(xyz=(0.18, 0.0, 0.025)),
    )
    return head_frame, root_visual


def _emit_pipe_mechanism(model, r, head_frame, mats, *, assets) -> list[str]:
    movable_jaw = model.part("movable_jaw")
    movable_jaw.visual(
        mesh_from_cadquery(_build_pipe_movable_jaw_geometry(), "movable_jaw_steel", assets=assets),
        material=mats["steel_dark"], name="jaw_steel", material_class_id=("metal.steel_bare" if r.palette_style in {"bright_chrome_steel", "blue_japanned_steel", "red_wood_handle", "galvanized_tube", "dark_machined_steel"} else "metal.blackened_gunmetal"),
    )
    movable_jaw.inertial = Inertial.from_geometry(
        Box((0.05, 0.02, 0.13)), mass=0.06, origin=Origin(xyz=(0.02, 0.0, -0.03)),
    )

    adjust_nut = model.part("adjust_nut")
    nut_knob = KnobGeometry(
        diameter=P_NUT_DIAMETER,
        height=P_WINDOW_W - 0.001,
        body_style="cylindrical",
        grip=KnobGrip(style="knurled", count=P_NUT_GRIP_COUNT, depth=0.0008, helix_angle_deg=18.0),
    )
    adjust_nut.visual(
        mesh_from_geometry(nut_knob, "adjust_nut_knurled"),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material=mats["knurl"], name="nut_knurled", material_class_id=("metal.steel_bare" if r.palette_style in {"bright_chrome_steel", "blue_japanned_steel", "red_wood_handle", "galvanized_tube", "dark_machined_steel"} else "metal.blackened_gunmetal"),
    )
    adjust_nut.inertial = Inertial.from_geometry(
        Cylinder(radius=P_NUT_DIAMETER / 2.0, length=P_WINDOW_W), mass=0.02,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
    )

    model.articulation(
        "frame_to_jaw", ArticulationType.PRISMATIC, parent=head_frame, child=movable_jaw,
        origin=Origin(xyz=_pipe_lay(r, 0.0, 0.0, P_WINDOW_Z), rpy=P_LAY_RPY),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=120.0, velocity=0.05, lower=0.0, upper=r.jaw_travel),
    )
    model.articulation(
        "frame_to_nut", ArticulationType.CONTINUOUS, parent=head_frame, child=adjust_nut,
        origin=Origin(xyz=_pipe_lay(r, 0.004, 0.0, P_WINDOW_Z), rpy=P_LAY_RPY),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=8.0, velocity=10.0),
    )
    return ["movable_jaw", "adjust_nut"]


# ===========================================================================
# Build
# ===========================================================================
def build_wrench(
    config: WrenchConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        key: model.material(f"wrench_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in PALETTES[r.palette_style].items()
    }

    if r.spine == "crescent":
        body, _root_visual, _tilt, _z_lift, _x1 = _build_crescent_root(model, r, mats, assets=assets)
        _emit_crescent_mechanism(model, r, body, mats, assets=assets)
    else:
        head_frame, _root_visual = _build_pipe_root(model, r, mats, assets=assets)
        _emit_pipe_mechanism(model, r, head_frame, mats, assets=assets)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_wrench(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_wrench(config_from_seed(seed), assets=assets)


# ===========================================================================
# Tests
# ===========================================================================
def run_wrench_tests(
    object_model: ArticulatedObject,
    config: WrenchConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)

    root_name = "wrench_body" if r.spine == "crescent" else "head_frame"
    root = object_model.get_part(root_name)
    movable = object_model.get_part("movable_jaw")

    # -------------------------------------------------------------------
    # Captured-fit allowances (element-scoped, grandfathered joints).
    # -------------------------------------------------------------------
    if r.spine == "crescent":
        # The crescent steel shell/core visual is always named "body_shell"
        # (for the wood handle it is the steel core that carries the head).
        shell_elem = "body_shell"
        ctx.allow_overlap(
            movable, root, elem_a="jaw_shell", elem_b=shell_elem,
            reason="The movable-jaw shank rides captured inside the head's slide slot (prismatic fit).",
        )
        if r.head_mechanism in ("worm_rack_crescent", "monkey_head"):
            worm = object_model.get_part("worm_screw")
            ctx.allow_overlap(
                movable, worm, elem_a="jaw_shell", elem_b="worm_wheel",
                reason="The worm thumb-wheel meshes the jaw rack teeth to drive the slide.",
            )
            ctx.allow_overlap(
                worm, root, elem_a="worm_wheel", elem_b=shell_elem,
                reason="The worm thumb-wheel is captured inside the head's pocket bore.",
            )
            if r.head_mechanism == "monkey_head":
                # The worm is fully enclosed in the back-wall pocket (radial clearance).
                ctx.allow_isolated_part(
                    worm,
                    reason="The worm thumb-wheel is captured inside the head pocket bore with small radial clearance.",
                )
        elif r.head_mechanism == "thumb_slide":
            lever = object_model.get_part("thumb_lever")
            ctx.allow_overlap(
                lever, root, elem_a="lever_shell", elem_b=shell_elem,
                reason="The lever bore fits over the head's pivot boss pin (captured pin joint).",
            )
            ctx.allow_overlap(
                lever, movable, elem_a="lever_shell", elem_b="jaw_shell",
                reason="The lever engagement tab sweeps into the slot to push the jaw shank.",
            )
            ctx.allow_coplanar_surfaces(
                root, lever,
                reason="The thumb lever sits flush on the head face and pivots on the boss pin.",
            )
    else:  # pipe
        nut = object_model.get_part("adjust_nut")
        ctx.allow_overlap(
            nut, root, elem_a="nut_knurled", elem_b="frame_steel",
            reason="The knurled adjusting nut is captured inside the frame window.",
        )
        ctx.allow_overlap(
            nut, movable, elem_a="nut_knurled", elem_b="jaw_steel",
            reason="The nut threads onto the jaw screw bar and intentionally encircles it.",
        )
        ctx.allow_overlap(
            movable, root, elem_a="jaw_steel", elem_b="frame_steel",
            reason="The movable jaw bar slides inside the housing channel and nut window.",
        )

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_joint_mating_has_gap()

    # -------------------------------------------------------------------
    # slot_choices recorded.
    # -------------------------------------------------------------------
    ctx.check(
        "slot_choices recorded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    # -------------------------------------------------------------------
    # Single root + correct root identity.
    # -------------------------------------------------------------------
    roots = object_model.root_parts()
    ctx.check(
        "single root part with the expected name for the spine",
        len(roots) == 1 and roots[0].name == root_name,
        details=f"roots={[p.name for p in roots]} expected={root_name}",
    )

    # -------------------------------------------------------------------
    # IDENTITY: movable jaw PRISMATIC (>=1 non-fixed joint).
    # -------------------------------------------------------------------
    slide_name = "jaw_slide" if r.spine == "crescent" else "frame_to_jaw"
    slide = object_model.get_articulation(slide_name)
    ctx.check(
        "movable jaw has a PRISMATIC slide (adjustable-wrench identity)",
        slide.articulation_type == ArticulationType.PRISMATIC,
        details=f"type={slide.articulation_type}",
    )

    # Driver joint topology + axes.
    if r.head_mechanism == "worm_rack_crescent":
        ctx.check("jaw slides along the head-local slide axis (-X)",
                  slide.axis[0] < -0.99 and abs(slide.axis[2]) < 0.01, details=f"axis={tuple(slide.axis)}")
        worm_turn = object_model.get_articulation("worm_turn")
        ctx.check("worm driver is CONTINUOUS about the slide axis (+X)",
                  worm_turn.articulation_type == ArticulationType.CONTINUOUS
                  and abs(worm_turn.axis[0]) > 0.99 and abs(worm_turn.axis[2]) < 0.01,
                  details=f"type={worm_turn.articulation_type} axis={tuple(worm_turn.axis)}")
    elif r.head_mechanism == "monkey_head":
        ctx.check("monkey jaw slides along -Y (square parallel jaws)",
                  abs(slide.axis[1]) > 0.99 and abs(slide.axis[0]) < 0.01, details=f"axis={tuple(slide.axis)}")
        worm_turn = object_model.get_articulation("worm_turn")
        ctx.check("monkey worm driver is CONTINUOUS about +X",
                  worm_turn.articulation_type == ArticulationType.CONTINUOUS
                  and abs(worm_turn.axis[0]) > 0.99, details=f"type={worm_turn.articulation_type} axis={tuple(worm_turn.axis)}")
    elif r.head_mechanism == "thumb_slide":
        ctx.check("thumb jaw slides along the head-local slide axis (-X)",
                  slide.axis[0] < -0.99 and abs(slide.axis[2]) < 0.01, details=f"axis={tuple(slide.axis)}")
        lever_pivot = object_model.get_articulation("lever_pivot")
        ctx.check("thumb lever driver is REVOLUTE about Z",
                  lever_pivot.articulation_type == ArticulationType.REVOLUTE
                  and abs(lever_pivot.axis[2]) > 0.99, details=f"type={lever_pivot.articulation_type} axis={tuple(lever_pivot.axis)}")
    else:  # screw_nut_pipe
        jx, jy, jz = slide.axis
        ctx.check("pipe jaw slides along the tool long axis (world +X = joint +Z)",
                  abs(jz) > 0.99 and abs(jx) < 0.01 and abs(jy) < 0.01, details=f"axis={tuple(slide.axis)}")
        nut_joint = object_model.get_articulation("frame_to_nut")
        ctx.check("pipe nut driver is CONTINUOUS collinear with the slide axis",
                  nut_joint.articulation_type == ArticulationType.CONTINUOUS
                  and tuple(nut_joint.axis) == tuple(slide.axis),
                  details=f"type={nut_joint.articulation_type} axis={tuple(nut_joint.axis)}")

    # -------------------------------------------------------------------
    # Lies flat, long along X (category identity / proportion).
    # -------------------------------------------------------------------
    part_aabbs = [a for a in (ctx.part_world_aabb(p) for p in object_model.parts) if a is not None]
    if part_aabbs:
        mins = [min(a[0][i] for a in part_aabbs) for i in range(3)]
        maxs = [max(a[1][i] for a in part_aabbs) for i in range(3)]
        x_extent = maxs[0] - mins[0]
        z_extent = maxs[2] - mins[2]
        ctx.check("wrench rests near the ground (z_min ~ 0)", mins[2] < 0.006, details=f"z_min={mins[2]:.4f}")
        ctx.check("wrench is long and slender along X",
                  x_extent > 0.26 and x_extent > 2.5 * z_extent,
                  details=f"x_extent={x_extent:.3f} z_extent={z_extent:.3f}")

    # -------------------------------------------------------------------
    # Handle identity present (per-handle visual exists on the root).
    # -------------------------------------------------------------------
    root_visual_names = {v.name for v in root.visuals}
    if r.spine == "crescent":
        if r.handle == "tapered_wood":
            ctx.check("wood grip + ferrule present on crescent root",
                      "wood_grip" in root_visual_names and "ferrule_collar" in root_visual_names,
                      details=str(sorted(root_visual_names)))
        else:
            ctx.check("crescent root body shell present", "body_shell" in root_visual_names,
                      details=str(sorted(root_visual_names)))
    else:
        if r.handle == "flat_steel":
            ctx.check("flat handle present on pipe root", "flat_handle" in root_visual_names,
                      details=str(sorted(root_visual_names)))
        elif r.handle == "tapered_wood":
            ctx.check("wood handle present on pipe root", "handle_body" in root_visual_names,
                      details=str(sorted(root_visual_names)))
        else:
            ctx.check("tube handle present on pipe root", "handle_tube" in root_visual_names,
                      details=str(sorted(root_visual_names)))

    # -------------------------------------------------------------------
    # Rest pose is closed (small gap), and the slide opens it.
    # -------------------------------------------------------------------
    rest_pos = ctx.part_world_position(movable)
    with ctx.pose({slide: r.jaw_travel}):
        open_pos = ctx.part_world_position(movable)
    if rest_pos is not None and open_pos is not None:
        moved = max(abs(open_pos[i] - rest_pos[i]) for i in range(3))
        ctx.check(
            "advancing the prismatic slide visibly moves the movable jaw",
            moved > 0.5 * r.jaw_travel,
            details=f"rest={rest_pos} open={open_pos} travel={r.jaw_travel:.4f}",
        )

    # Driver actuates (poses cleanly).
    if r.head_mechanism in ("worm_rack_crescent", "monkey_head"):
        worm_turn = object_model.get_articulation("worm_turn")
        with ctx.pose({worm_turn: 1.0}):
            ctx.check("worm driver poses under rotation",
                      ctx.part_world_aabb(object_model.get_part("worm_screw")) is not None,
                      details="worm pose")
    elif r.head_mechanism == "thumb_slide":
        lever_pivot = object_model.get_articulation("lever_pivot")
        lr = ctx.part_world_aabb(object_model.get_part("thumb_lever"))
        with ctx.pose({lever_pivot: r.lever_travel}):
            lp = ctx.part_world_aabb(object_model.get_part("thumb_lever"))
        ctx.check("thumb lever sweeps under rotation",
                  lr is not None and lp is not None
                  and (abs(lr[0][1] - lp[0][1]) > 0.001 or abs(lr[1][0] - lp[1][0]) > 0.001),
                  details=f"rest={lr} push={lp}")
    else:  # pipe nut spins in place
        nut_joint = object_model.get_articulation("frame_to_nut")
        nut = object_model.get_part("adjust_nut")
        n0 = ctx.part_world_position(nut)
        with ctx.pose({nut_joint: math.pi / 2}):
            n1 = ctx.part_world_position(nut)
        if n0 is not None and n1 is not None:
            ctx.check("pipe nut spins in place (no translation)",
                      max(abs(n1[i] - n0[i]) for i in range(3)) < 5e-4,
                      details=f"rest={n0} spun={n1}")

    return ctx.report()


__all__ = (
    "WrenchConfig",
    "ResolvedWrenchConfig",
    "build_wrench",
    "build_seeded_wrench",
    "config_from_seed",
    "resolve_config",
    "run_wrench_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
