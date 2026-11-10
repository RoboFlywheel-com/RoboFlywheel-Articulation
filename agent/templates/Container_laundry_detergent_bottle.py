# SPDX-License-Identifier: Apache-2.0

"""Container / laundry detergent bottle — modular procedural template.

Category identity: an upright molded HDPE laundry detergent jug. The hollow
jug body (ROOT) rests on z=0 with its axis along +Z; an integrated side/top
handle or finger scoop is fused into the body mesh; one of several closures
(measuring-cup screw cap, flip-top snap lid, screw-collar pump dispenser) caps
the threaded neck and provides the main articulation. No multiplicity axis —
one jug, one closure.

Three parallel slots (spec ``Container_laundry_detergent_bottle.md``):

  * ``body_shape`` (4) — the ROOT ``body`` mesh: flat-oval jug, round cylinder,
    square-shouldered rectangular prism (2-segment visual + shoulder step),
    waisted ergonomic contour. Oval/round/waist forms are vertical lofts; the
    square form is a filleted box + square shoulder step. All carry a short
    threaded neck and a bored pour mouth.
  * ``handle_grip`` (3) — a body-mesh operation (NOT an independent part):
      - side_loop_handle: +X slab fused into the upper body with an enclosed
        oval finger cut-out (union into the jug shell).
      - recessed_grip: a spherical finger scoop cut into the +X broad face
        (continuous wall, no through hole).
      - top_carry_handle: an inverted-U swept tube arching over the top
        (union; peak rises above the cap/neck).
  * ``closure`` (3, each with >=1 non-fixed joint) — the main mechanism:
      - measuring_cup_cap: CONTINUOUS spin + PRISMATIC lift via a massless
        ``cap_carrier`` link (parent screw-cap pattern); translucent cup.
      - flip_top_cap: REVOLUTE +X flip lid hinged at the rear neck collar
        (body gains a ``_neck_collar`` ring as the hinge seat).
      - pump_dispenser: CONTINUOUS screw collar (``collar_screw``) + PRISMATIC
        press-down actuator (``pump_press``) with a dip tube into the bottle.

Continuous size/proportion variation (height/width/neck/handle/travel scales)
lives in ``resolve_config`` as clamped params, never as slot candidates.

Sources (articraft_data ``picture/Container/laundry detergent bottle`` 5-star
pool): parent ``8f73f587`` (flat-oval jug + side loop + measuring cup), forks
``var_cyl_body``, ``var_square_body``, ``var_waist_body`` (body shapes),
``var_grip_indent``, ``var_top_handle`` (handles), ``var_flip_cap``,
``var_pump_cap`` (closures).

Canonical spec:
``articraft_template_authoring/specs_modular_v1/Container_laundry_detergent_bottle.md``
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, replace
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
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
)

__modular__ = True

# ---------------------------------------------------------------------------
# Slot domains
# ---------------------------------------------------------------------------
BodyShape = Literal[
    "flat_oval_jug",
    "round_cylinder",
    "square_shoulder",
    "waisted_contour",
]
HandleGrip = Literal[
    "side_loop_handle",
    "recessed_grip",
    "top_carry_handle",
]
Closure = Literal[
    "measuring_cup_cap",
    "flip_top_cap",
    "pump_dispenser",
]
PaletteStyle = Literal[
    "tide_orange_blue",
    "gain_green_white",
    "persil_white_red",
    "arm_hammer_yellow",
    "allfree_teal",
    "ecover_amber",
    "purex_purple",
    "downy_pink_twotone",
    "seventh_gen_matte_pearl",
]

BODY_SHAPES: tuple[BodyShape, ...] = (
    "flat_oval_jug",
    "round_cylinder",
    "square_shoulder",
    "waisted_contour",
)
HANDLE_GRIPS: tuple[HandleGrip, ...] = (
    "side_loop_handle",
    "recessed_grip",
    "top_carry_handle",
)
CLOSURES: tuple[Closure, ...] = (
    "measuring_cup_cap",
    "flip_top_cap",
    "pump_dispenser",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "tide_orange_blue",
    "gain_green_white",
    "persil_white_red",
    "arm_hammer_yellow",
    "allfree_teal",
    "ecover_amber",
    "purex_purple",
    "downy_pink_twotone",
    "seventh_gen_matte_pearl",
)

# ---------------------------------------------------------------------------
# Palette: 9 realistic detergent colorways + explicit material-finish dim.
# Each colorway gives body/handle main color (jug_shell + spout), closure color
# (cup/lid/pump), accent (label/badge), and a two-tone closure ring color.
# finish: glossy_hdpe / translucent / opaque_matte / pearlescent.
#   - measuring_cup_cap REQUIRES cap alpha < 1 (translucent cup identity);
#     colorways that are otherwise opaque carry a translucent cap sub-value.
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class _Palette:
    body: tuple[float, float, float, float]
    closure: tuple[float, float, float, float]  # opaque closure (lid / pump head)
    cup: tuple[float, float, float, float]  # measuring-cup cap (alpha < 1)
    accent: tuple[float, float, float, float]  # label / band / badge
    ring: tuple[float, float, float, float]  # two-tone cap ring / pump dark
    finish: str


PALETTES: dict[PaletteStyle, _Palette] = {
    "tide_orange_blue": _Palette(
        body=(0.95, 0.46, 0.07, 1.0),
        closure=(0.30, 0.55, 0.85, 1.0),
        cup=(0.30, 0.55, 0.85, 0.5),
        accent=(0.98, 0.83, 0.10, 1.0),
        ring=(0.10, 0.22, 0.62, 1.0),
        finish="glossy_hdpe",
    ),
    "gain_green_white": _Palette(
        body=(0.30, 0.62, 0.20, 1.0),
        closure=(0.95, 0.95, 0.96, 1.0),
        cup=(0.95, 0.95, 0.96, 0.5),
        accent=(0.10, 0.22, 0.62, 1.0),
        ring=(0.20, 0.42, 0.14, 1.0),
        finish="glossy_hdpe",
    ),
    "persil_white_red": _Palette(
        body=(0.96, 0.96, 0.93, 1.0),
        closure=(0.82, 0.18, 0.18, 1.0),
        cup=(0.82, 0.18, 0.18, 0.5),
        accent=(0.08, 0.16, 0.48, 1.0),
        ring=(0.60, 0.10, 0.10, 1.0),
        finish="glossy_hdpe",
    ),
    "arm_hammer_yellow": _Palette(
        body=(0.97, 0.80, 0.10, 1.0),
        closure=(0.92, 0.92, 0.95, 1.0),
        cup=(0.92, 0.92, 0.95, 0.5),
        accent=(0.78, 0.12, 0.12, 1.0),
        ring=(0.70, 0.58, 0.06, 1.0),
        finish="glossy_hdpe",
    ),
    "allfree_teal": _Palette(
        body=(0.10, 0.65, 0.68, 1.0),
        closure=(0.92, 0.92, 0.93, 1.0),
        cup=(0.85, 0.92, 0.93, 0.5),
        accent=(0.42, 0.18, 0.62, 1.0),
        ring=(0.07, 0.45, 0.48, 1.0),
        finish="glossy_hdpe",
    ),
    "ecover_amber": _Palette(
        body=(0.62, 0.40, 0.12, 0.55),  # translucent amber jug body
        closure=(0.30, 0.55, 0.22, 1.0),
        cup=(0.40, 0.55, 0.30, 0.5),
        accent=(0.55, 0.42, 0.28, 1.0),
        ring=(0.22, 0.40, 0.16, 1.0),
        finish="translucent",
    ),
    "purex_purple": _Palette(
        body=(0.45, 0.20, 0.62, 1.0),
        closure=(0.62, 0.45, 0.82, 1.0),
        cup=(0.62, 0.45, 0.82, 0.5),
        accent=(0.78, 0.80, 0.82, 1.0),
        ring=(0.32, 0.14, 0.46, 1.0),
        finish="glossy_hdpe",
    ),
    "downy_pink_twotone": _Palette(
        body=(0.90, 0.42, 0.58, 1.0),
        closure=(0.95, 0.95, 0.96, 1.0),
        cup=(0.95, 0.90, 0.93, 0.5),
        accent=(0.95, 0.95, 0.96, 1.0),
        ring=(0.62, 0.10, 0.30, 1.0),  # deep berry cap ring (two-tone)
        finish="glossy_hdpe",
    ),
    "seventh_gen_matte_pearl": _Palette(
        body=(0.42, 0.45, 0.48, 1.0),  # matte slate HDPE
        closure=(0.80, 0.82, 0.86, 1.0),  # pearlescent cap
        cup=(0.80, 0.82, 0.86, 0.5),
        accent=(0.16, 0.30, 0.22, 1.0),
        ring=(0.66, 0.68, 0.72, 1.0),
        finish="opaque_matte",
    ),
}


# ---------------------------------------------------------------------------
# Base geometry constants (meters). Heights are at nominal (height_scale == 1).
# These mirror the 5-star source records.
# ---------------------------------------------------------------------------
SHOULDER_Z = 0.175
NECK_BOTTOM_Z = 0.198
NECK_TOP_Z = 0.214
CAP_SEAT_Z = 0.196
NECK_R = 0.0235
# Wall thickness of the molded HDPE shell (used to inset the inner cavity from
# the outer shell, and to set the open neck-bore radius). The bottle is a single
# connected hollow shell: an inner loft (body wall) joined to a through-bore up
# the neck, cut once from the solid so the open inner cavity is visible down the
# open mouth (no solid plug under the neck).
WALL_T = 0.0032  # body-wall thickness
NECK_WALL_T = 0.0028  # neck-ring wall thickness (mouth bore = neck_r - this)
BASE_FLOOR_T = 0.006  # solid base floor under the cavity (so it rests flat)
CAP_HEIGHT = 0.058

# square body base dims
SQ_BODY_W = 0.150
SQ_BODY_D = 0.090
SQ_SHOULDER_W = 0.080
SQ_SHOULDER_D = 0.065

# top-carry handle base geometry
TC_TUBE_R = 0.010
TC_LEG_X = 0.050
TC_LEG_TOP_Z = 0.252
TC_PEAK_Z = 0.290
TC_FOOT_Z = 0.178


@dataclass(frozen=True)
class ContainerLaundryDetergentBottleConfig:
    body_shape: BodyShape = "flat_oval_jug"
    handle_grip: HandleGrip = "side_loop_handle"
    closure: Closure = "measuring_cup_cap"
    palette_style: PaletteStyle = "tide_orange_blue"
    body_height_scale: float = 1.0
    body_width_scale: float = 1.0
    neck_radius_scale: float = 1.0
    handle_size_scale: float = 1.0
    closure_travel_scale: float = 1.0
    name: str = "container_laundry_detergent_bottle"


@dataclass(frozen=True)
class ResolvedContainerLaundryDetergentBottleConfig:
    body_shape: BodyShape
    handle_grip: HandleGrip
    closure: Closure
    palette_style: PaletteStyle
    body_height_scale: float
    body_width_scale: float
    neck_radius_scale: float
    handle_size_scale: float
    closure_travel_scale: float
    # derived geometry
    neck_r: float
    mouth_bore_r: float  # open pour-mouth bore radius (= neck_r - neck wall)
    shoulder_z: float
    neck_bottom_z: float
    neck_top_z: float
    cap_seat_z: float
    cap_height: float
    # closure-fit derived radii
    cap_bore_r: float  # measuring cup inner bore (>= neck_r + clearance)
    cap_outer_r: float
    collar_top_z: float  # flip collar top z (world)
    collar_r: float  # flip collar outer radius
    lid_skirt_inner_r: float
    pump_collar_outer_r: float
    # handle
    handle_peak_z: float  # top_carry arch peak (world z)
    scoop_r: float  # recessed grip sphere radius
    scoop_depth: float  # recessed grip dent depth
    name: str


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


# ---------------------------------------------------------------------------
# Seed / resolve
# ---------------------------------------------------------------------------
def config_from_seed(seed: int) -> ContainerLaundryDetergentBottleConfig:
    """Deterministic procedural sampling (seed 0 is not special)."""
    rng = random.Random(seed)
    return ContainerLaundryDetergentBottleConfig(
        body_shape=rng.choice(BODY_SHAPES),
        handle_grip=rng.choice(HANDLE_GRIPS),
        closure=rng.choice(CLOSURES),
        palette_style=rng.choice(PALETTE_STYLES),
        body_height_scale=round(rng.uniform(0.88, 1.15), 4),
        body_width_scale=round(rng.uniform(0.88, 1.15), 4),
        neck_radius_scale=round(rng.uniform(0.92, 1.08), 4),
        handle_size_scale=round(rng.uniform(0.85, 1.15), 4),
        closure_travel_scale=round(rng.uniform(0.85, 1.10), 4),
        name=f"seeded_container_laundry_detergent_bottle_{seed}",
    )


def resolve_config(
    config: ContainerLaundryDetergentBottleConfig | None = None,
) -> ResolvedContainerLaundryDetergentBottleConfig:
    cfg = config or ContainerLaundryDetergentBottleConfig()
    body_shape = _pick(cfg.body_shape, BODY_SHAPES)
    handle_grip = _pick(cfg.handle_grip, HANDLE_GRIPS)
    closure = _pick(cfg.closure, CLOSURES)
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)

    h_scale = _clamp(cfg.body_height_scale, 0.88, 1.15)
    w_scale = _clamp(cfg.body_width_scale, 0.88, 1.15)
    n_scale = _clamp(cfg.neck_radius_scale, 0.92, 1.08)
    handle_scale = _clamp(cfg.handle_size_scale, 0.85, 1.15)
    travel_scale = _clamp(cfg.closure_travel_scale, 0.85, 1.10)

    # Vertical heights scale uniformly with height_scale so the neck/cap mount
    # rises/falls with the body and the closure follows. (neck does NOT follow
    # width_scale, to preserve cap fit.)
    shoulder_z = SHOULDER_Z * h_scale
    neck_bottom_z = NECK_BOTTOM_Z * h_scale
    neck_top_z = NECK_TOP_Z * h_scale
    cap_seat_z = CAP_SEAT_Z * h_scale

    # Neck radius follows its own scale only (equation drives cap/lid/collar).
    neck_r = _clamp(NECK_R * n_scale, 0.018, 0.030)

    # Open pour mouth: a realistic open opening bored down the neck into the body
    # cavity (NOT a narrow blind hole over a solid plug). The bore hugs the neck
    # wall for a thin molded ring, but is capped at 0.0145 so the on-axis spin
    # closures' centerline joint origins (cap_seat_z) stay within the body's neck
    # ring (fail_if_articulation_origin_far_from_geometry tol=0.015): the nearest
    # body material to the centerline at the seat is this bore wall, so the spin
    # axis (which MUST stay on the bottle centerline for in-place rotation) only
    # anchors to real geometry when the bore radius is inside tolerance.
    mouth_bore_r = _clamp(neck_r - NECK_WALL_T, 0.012, 0.0145)

    # measuring cup bore hugs the neck rim (slight friction interference) so the
    # cup inner wall actually contacts the neck rather than floating off it; the
    # captured-fit overlap is allowed in tests.
    cap_bore_r = neck_r + 0.0006
    cap_outer_r = cap_bore_r + 0.004
    cap_height = CAP_HEIGHT * travel_scale

    # flip collar: a ring slightly wider than the neck; lid skirt wraps it.
    collar_r = neck_r + 0.0035
    collar_top_z = neck_top_z + 0.008
    lid_skirt_inner_r = collar_r + 0.0025

    # pump screw collar.
    pump_collar_outer_r = neck_r + 0.0055

    # top-carry arch peak: scaled by height so it stays above the body top, and
    # raised to clear the pump head when pump_dispenser is selected (compat).
    handle_peak_z = TC_PEAK_Z * h_scale
    # body top (neck top) plus a closure clearance band.
    closure_top_clear = neck_top_z + 0.085  # pump actuator reaches ~here
    if closure == "pump_dispenser":
        handle_peak_z = max(handle_peak_z, closure_top_clear + 0.012)

    # recessed scoop: a shallow spherical dent on the +X face. Both radius and
    # depth are bounded by the body half-width so the cut only dents the wall
    # and never splits the body (which would drop the lower shell from the mesh).
    if body_shape == "round_cylinder":
        body_half = 0.055 * w_scale
    elif body_shape == "waisted_contour":
        body_half = 0.056 * w_scale
    elif body_shape == "square_shoulder":
        body_half = (SQ_BODY_W / 2.0) * w_scale
    else:
        body_half = 0.073 * w_scale
    base_scoop_r = 0.042 * handle_scale
    # scoop sphere radius bounded well below the body half-width so the crater
    # stays a +X-face dent rather than eating the whole cross-section.
    scoop_r = _clamp(base_scoop_r, 0.024, min(0.050, 0.72 * body_half))
    # dent depth capped at ~26% of the body half-width (and <= 14mm).
    scoop_depth = min(0.014 * handle_scale, 0.26 * body_half)

    return ResolvedContainerLaundryDetergentBottleConfig(
        body_shape=body_shape,
        handle_grip=handle_grip,
        closure=closure,
        palette_style=palette_style,
        body_height_scale=h_scale,
        body_width_scale=w_scale,
        neck_radius_scale=n_scale,
        handle_size_scale=handle_scale,
        closure_travel_scale=travel_scale,
        neck_r=neck_r,
        mouth_bore_r=mouth_bore_r,
        shoulder_z=shoulder_z,
        neck_bottom_z=neck_bottom_z,
        neck_top_z=neck_top_z,
        cap_seat_z=cap_seat_z,
        cap_height=cap_height,
        cap_bore_r=cap_bore_r,
        cap_outer_r=cap_outer_r,
        collar_top_z=collar_top_z,
        collar_r=collar_r,
        lid_skirt_inner_r=lid_skirt_inner_r,
        pump_collar_outer_r=pump_collar_outer_r,
        handle_peak_z=handle_peak_z,
        scoop_r=scoop_r,
        scoop_depth=scoop_depth,
        name=cfg.name or "container_laundry_detergent_bottle",
    )


def with_overrides(
    config: ContainerLaundryDetergentBottleConfig, **kwargs: object
) -> ContainerLaundryDetergentBottleConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: ContainerLaundryDetergentBottleConfig
    | ResolvedContainerLaundryDetergentBottleConfig,
) -> tuple[tuple[str, str], ...]:
    r = (
        config
        if isinstance(config, ResolvedContainerLaundryDetergentBottleConfig)
        else resolve_config(config)
    )
    return (
        ("body_shape", r.body_shape),
        ("handle_grip", r.handle_grip),
        ("closure", r.closure),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Body geometry helpers (Slot A). Oval / round / waist are vertical lofts;
# square is box + shoulder step. The mouth is bored down the neck axis.
# All sections scale: z by height_scale, half-widths by width_scale.
# ---------------------------------------------------------------------------
def _occ_fuse(a: cq.Workplane, b: cq.Workplane) -> cq.Workplane:
    """Robust solid union. OCC sometimes returns a null TopoDS_Shape when a
    swept tube grazes a curved/lofted surface; retry by working on the raw
    OCC solids with a fuzzy tolerance, which usually resolves the boolean."""
    try:
        out = a.union(b)
        out.val().wrapped  # touch the result; raises if null
        return out
    except Exception:
        pass
    try:
        sa = a.val()
        sb = b.val()
        fused = sa.fuse(sb, tol=1e-4)
        return cq.Workplane("XY").newObject([fused])
    except Exception:
        # last resort: combine as a compound so the mesh still includes both.
        try:
            return a.add(b).combine(glue=False)
        except Exception:
            return a.add(b)


def _recess_boss(
    r: ResolvedContainerLaundryDetergentBottleConfig,
) -> cq.Workplane | None:
    """A solid sphere (scoop radius + wall margin) at the recessed-grip scoop
    center. Subtracted from the cavity tool so the cavity locally retreats and
    leaves a continuous (locally thickened) wall behind the finger scoop instead
    of the scoop punching a hole through the now-thin hollow wall."""
    if r.handle_grip != "recessed_grip":
        return None
    scoop = _grip_recess_solid(r)
    sb = scoop.val().BoundingBox()
    cx = (sb.xmin + sb.xmax) / 2.0
    cz = (sb.zmin + sb.zmax) / 2.0
    boss_r = r.scoop_r + WALL_T + 0.0015
    return cq.Workplane("XY").transformed(offset=(cx, 0.0, cz)).sphere(boss_r)


def _cavity_tool(
    r: ResolvedContainerLaundryDetergentBottleConfig,
    sections: list[tuple[float, float, float]],
    *,
    circular: bool,
    protect: cq.Workplane | None = None,
) -> cq.Workplane:
    """Single cutting tool that hollows the jug AND bores the open pour mouth.

    It is the union of (a) an inner cavity loft whose sections are the body
    sections inset by ``WALL_T`` — running from a base floor up to just below the
    neck — and (b) a straight through-bore cylinder of the open-mouth radius from
    inside that cavity up past the mouth top. Cutting this ONE tool from the solid
    shell yields one connected hollow shell with the open mouth opening straight
    into the visible inner cavity (no solid plug under the neck)."""
    # The outer shell's lowest section sits at z≈0.004*h_scale; raise the cavity
    # floor a full BASE_FLOOR_T above that so the bottle rests on a real solid base.
    floor_z = 0.004 * r.body_height_scale + BASE_FLOOR_T
    # Inner cavity ceiling: stop a wall-thickness below the neck base so the body
    # cavity tapers up to the neck and the through-bore carries the opening the
    # rest of the way (the two unify into one continuous cavity).
    cavity_top = r.neck_bottom_z - WALL_T
    inner_min = r.mouth_bore_r  # never let the cavity pinch below the bore

    levels: list[tuple[float, float, float]] = []
    for (z, hx, hy) in sections:
        zz = z * r.body_height_scale
        if zz <= floor_z + 0.002 or zz >= cavity_top:
            continue
        sx = max(hx * r.body_width_scale - WALL_T, inner_min)
        sy = max(hy * r.body_width_scale - WALL_T, inner_min)
        levels.append((zz, sx, sy))
    # Anchor a bottom cap section right at the floor and a top section at the
    # cavity ceiling so the inner loft spans the whole interior height.
    if levels:
        bot_sx, bot_sy = levels[0][1], levels[0][2]
    else:
        bot_sx = bot_sy = max(0.045 * r.body_width_scale, inner_min)
    levels.insert(0, (floor_z, bot_sx, bot_sy))
    # Pinch the cavity top toward the bore so it blends into the neck through-bore.
    levels.append((cavity_top, r.mouth_bore_r, r.mouth_bore_r))

    wp = cq.Workplane("XY")
    prev_z = 0.0
    for i, (zz, sx, sy) in enumerate(levels):
        off = zz if i == 0 else zz - prev_z
        wp = wp.workplane(offset=off)
        if circular:
            wp = wp.circle(sx)
        else:
            wp = wp.rect(2.0 * sx, 2.0 * sy)
        prev_z = zz
    # ruled=True (linear between sections) so the inner cavity never bulges past
    # the outer shell at sharp shoulder tapers (a smooth B-spline inner loft
    # overshoots and the cut then engulfs the whole solid).
    cavity = wp.loft(ruled=True)

    # Through-bore: open pour mouth straight down the neck axis. Starts inside the
    # cavity (overlaps the cavity top) and runs up past the neck top so the mouth
    # is fully open. Union with the cavity into ONE clean cutting solid.
    bore_bottom = cavity_top - 0.006
    bore_top = r.neck_top_z + 0.010
    bore = (
        cq.Workplane("XY")
        .workplane(offset=bore_bottom)
        .circle(r.mouth_bore_r)
        .extrude(bore_top - bore_bottom)
    )
    tool = _occ_fuse(cavity, bore)
    if protect is not None:
        try:
            tool = tool.cut(protect)
        except Exception:
            pass
    return tool


def _bore_mouth(
    solid: cq.Workplane,
    r: ResolvedContainerLaundryDetergentBottleConfig,
    sections: list[tuple[float, float, float]],
    *,
    circular: bool,
) -> cq.Workplane:
    """Hollow the body and bore the open pour mouth into the inner cavity."""
    tool = _cavity_tool(r, sections, circular=circular, protect=_recess_boss(r))
    return solid.cut(tool)


def _loft_body(
    r: ResolvedContainerLaundryDetergentBottleConfig,
    sections: list[tuple[float, float, float]],
    *,
    circular: bool,
    fillet: float,
) -> cq.Workplane:
    """Vertical loft of the WHOLE shell (body + necked shoulder + straight neck)
    in a single ``loft`` so the result is one clean solid with no poke-through
    neck union (which OCC silently truncates). The body sections are floored at
    the neck radius, then circular neck-transition + straight-neck sections are
    appended so the loft runs continuously up to the neck top."""
    floor = r.neck_r
    neck_bottom = r.neck_bottom_z
    neck_top = r.neck_top_z + 0.004
    # Promote (z, half_x, half_y) body sections (rect or circle). Keep only the
    # sections strictly below the neck base so the appended circular neck
    # sections don't collide with a coincident-z body section.
    levels: list[tuple[float, float, float, bool]] = []
    for (z, hx, hy) in sections:
        zz = z * r.body_height_scale
        if zz >= neck_bottom - 0.004:
            continue
        sx = max(hx * r.body_width_scale, floor)
        sy = max(hy * r.body_width_scale, floor)
        levels.append((zz, sx, sy, circular))
    # Neck: a short transition into a straight cylinder of radius neck_r, up to
    # the neck top. These are circular regardless of body section type.
    levels.append((neck_bottom, r.neck_r, r.neck_r, True))
    levels.append((neck_top, r.neck_r, r.neck_r, True))

    wp = cq.Workplane("XY")
    prev_z = 0.0
    for i, (zz, sx, sy, circ) in enumerate(levels):
        off = zz if i == 0 else zz - prev_z
        wp = wp.workplane(offset=off)
        if circ:
            wp = wp.circle(sx)
        else:
            wp = wp.rect(2.0 * sx, 2.0 * sy)
        prev_z = zz
    body = wp.loft(ruled=False)
    if not circular:
        try:
            body = body.edges("|Z").fillet(fillet)
        except Exception:
            pass
    return body


def _flat_oval_sections() -> list[tuple[float, float, float]]:
    return [
        (0.004, 0.070, 0.044),
        (0.020, 0.075, 0.048),
        (0.090, 0.075, 0.048),
        (0.150, 0.073, 0.046),
        (0.175, 0.064, 0.040),
        (0.190, 0.040, 0.030),
        (0.198, 0.028, 0.028),
    ]


def _round_sections() -> list[tuple[float, float, float]]:
    BODY_R = 0.055
    return [
        (0.004, 0.050, 0.050),
        (0.020, BODY_R, BODY_R),
        (0.090, BODY_R, BODY_R),
        (0.150, 0.053, 0.053),
        (0.175, 0.044, 0.044),
        (0.190, 0.030, 0.030),
        (0.198, 0.025, 0.025),
    ]


def _waist_sections() -> list[tuple[float, float, float]]:
    return [
        (0.004, 0.072, 0.046),
        (0.020, 0.076, 0.049),
        (0.050, 0.068, 0.043),
        (0.075, 0.056, 0.035),
        (0.095, 0.052, 0.033),
        (0.115, 0.056, 0.035),
        (0.140, 0.068, 0.043),
        (0.160, 0.073, 0.046),
        (0.175, 0.064, 0.040),
        (0.190, 0.040, 0.030),
        (0.198, 0.028, 0.028),
    ]


def _loft_shell(r: ResolvedContainerLaundryDetergentBottleConfig) -> cq.Workplane:
    """The non-square (oval/round/waist) jug shell, hollowed with an open mouth."""
    if r.body_shape == "round_cylinder":
        sections = _round_sections()
        circular = True
        solid = _loft_body(r, sections, circular=True, fillet=0.0)
    elif r.body_shape == "waisted_contour":
        sections = _waist_sections()
        circular = False
        solid = _loft_body(r, sections, circular=False, fillet=0.010)
    else:  # flat_oval_jug
        sections = _flat_oval_sections()
        circular = False
        solid = _loft_body(r, sections, circular=False, fillet=0.012)
    return _bore_mouth(solid, r, sections, circular=circular)


def _square_cavity_tool(
    r: ResolvedContainerLaundryDetergentBottleConfig,
) -> cq.Workplane:
    """Single hollow-out + open-mouth tool for the square body. A stepped inner
    cavity (main-box interior -> shoulder interior) joined to the neck through-bore
    so cutting it from BOTH the main box and the shoulder/neck visual yields one
    continuous interior cavity open down the neck (no solid plug)."""
    w = SQ_BODY_W * r.body_width_scale
    d = SQ_BODY_D * r.body_width_scale
    sw = SQ_SHOULDER_W * r.body_width_scale
    sd = SQ_SHOULDER_D * r.body_width_scale

    floor_z = BASE_FLOOR_T  # square main box starts at z=0, so floor is from 0
    inner_w = max(w - 2.0 * WALL_T, 2.0 * r.mouth_bore_r)
    inner_d = max(d - 2.0 * WALL_T, 2.0 * r.mouth_bore_r)
    s_inner_w = max(sw - 2.0 * WALL_T, 2.0 * r.mouth_bore_r)
    s_inner_d = max(sd - 2.0 * WALL_T, 2.0 * r.mouth_bore_r)
    cavity_top = r.neck_bottom_z - WALL_T

    # Main-box interior, then narrow to the SHOULDER interior BELOW the shoulder
    # base (z=shoulder_z) so that at/above the shoulder step the cavity is already
    # inset from the narrower shoulder walls — otherwise the wider main-box cavity
    # would eat the shoulder's bottom slab and split it off as an island. Pinch to
    # the bore at the cavity top.
    levels = [
        (floor_z, inner_w / 2.0, inner_d / 2.0),
        (r.shoulder_z - 0.016, inner_w / 2.0, inner_d / 2.0),
        (r.shoulder_z - 0.008, s_inner_w / 2.0, s_inner_d / 2.0),
        (cavity_top, r.mouth_bore_r, r.mouth_bore_r),
    ]
    wp = cq.Workplane("XY")
    prev_z = 0.0
    for i, (zz, hx, hy) in enumerate(levels):
        off = zz if i == 0 else zz - prev_z
        wp = wp.workplane(offset=off).rect(2.0 * hx, 2.0 * hy)
        prev_z = zz
    cavity = wp.loft(ruled=True)

    bore_bottom = cavity_top - 0.006
    bore_top = r.neck_top_z + 0.010
    bore = (
        cq.Workplane("XY")
        .workplane(offset=bore_bottom)
        .circle(r.mouth_bore_r)
        .extrude(bore_top - bore_bottom)
    )
    tool = _occ_fuse(cavity, bore)
    boss = _recess_boss(r)
    if boss is not None:
        try:
            tool = tool.cut(boss)
        except Exception:
            pass
    return tool


def _square_main_box(r: ResolvedContainerLaundryDetergentBottleConfig) -> cq.Workplane:
    """Rectangular-prism main body (z=0..shoulder_z), hollowed + open mouth."""
    w = SQ_BODY_W * r.body_width_scale
    d = SQ_BODY_D * r.body_width_scale
    main = cq.Workplane("XY").rect(w, d).extrude(r.shoulder_z)
    try:
        main = main.edges("|Z").fillet(0.006)
    except Exception:
        pass
    main = main.cut(_square_cavity_tool(r))
    return main


def _square_shoulder_neck(
    r: ResolvedContainerLaundryDetergentBottleConfig,
) -> cq.Workplane:
    """Square shoulder step + threaded neck (z=shoulder_z..neck_top), hollowed so
    the mouth opens straight into the body cavity."""
    sw = SQ_SHOULDER_W * r.body_width_scale
    sd = SQ_SHOULDER_D * r.body_width_scale
    # Start the shoulder slightly BELOW the shoulder plane so its bottom slab
    # overlaps the main box top — the two body visuals then share solid material
    # and read as one connected piece (no disconnected-island warning).
    shoulder_base = r.shoulder_z - 0.006
    shoulder_h = r.neck_bottom_z - shoulder_base
    shoulder = (
        cq.Workplane("XY")
        .workplane(offset=shoulder_base)
        .rect(sw, sd)
        .extrude(shoulder_h)
    )
    try:
        shoulder = shoulder.edges("|Z").fillet(0.004)
    except Exception:
        pass
    neck = (
        cq.Workplane("XY")
        .workplane(offset=r.neck_bottom_z)
        .circle(r.neck_r)
        .extrude(r.neck_top_z - r.neck_bottom_z + 0.004)
    )
    shell = shoulder.union(neck)
    shell = shell.cut(_square_cavity_tool(r))
    return shell


# ---------------------------------------------------------------------------
# Handle helpers (Slot B). side_loop / top_carry union into the shell;
# recessed cuts a scoop. All are body-mesh ops (not parts).
# ---------------------------------------------------------------------------
def _side_loop_solid(r: ResolvedContainerLaundryDetergentBottleConfig) -> cq.Workplane:
    """+X side loop slab with an enclosed oval finger cut-out."""
    s = r.handle_size_scale
    # For a round/narrow body the inner edge sits closer in so the slab fuses.
    if r.body_shape == "round_cylinder":
        slab_cx = 0.060 * r.body_width_scale
        slab_w = 0.052 * s
        hole_cx = 0.062 * r.body_width_scale
        hole_a, hole_b = 0.016 * s, 0.048 * s
        fillet = 0.012
    else:
        slab_cx = 0.072 * max(r.body_width_scale, 0.9)
        slab_w = 0.066 * s
        hole_cx = 0.074 * max(r.body_width_scale, 0.9)
        hole_a, hole_b = 0.020 * s, 0.050 * s
        fillet = 0.014
    slab_h = 0.150 * r.body_height_scale
    slab_cz = 0.110 * r.body_height_scale
    slab = (
        cq.Workplane("XZ")
        .transformed(offset=(slab_cx, slab_cz, 0.0))
        .rect(slab_w, slab_h)
        .extrude(0.022, both=True)
    )
    try:
        slab = slab.edges("|Y").fillet(fillet)
    except Exception:
        pass
    hole = (
        cq.Workplane("XZ")
        .transformed(offset=(hole_cx, slab_cz, 0.0))
        .ellipse(hole_a, hole_b)
        .extrude(0.06, both=True)
    )
    slab = slab.cut(hole)
    return slab


def _grip_recess_solid(
    r: ResolvedContainerLaundryDetergentBottleConfig,
) -> cq.Workplane:
    """Spherical finger scoop cut into the +X broad face (continuous wall)."""
    scoop_r = r.scoop_r
    # +X face position in the grip zone.
    if r.body_shape == "round_cylinder":
        face_x = 0.055 * r.body_width_scale
    elif r.body_shape == "waisted_contour":
        face_x = 0.056 * r.body_width_scale
    else:
        face_x = 0.075 * r.body_width_scale
    depth = r.scoop_depth
    cx = face_x + scoop_r - depth
    cz = 0.115 * r.body_height_scale
    scoop = (
        cq.Workplane("XY")
        .transformed(offset=(cx, 0.0, cz))
        .sphere(scoop_r)
    )
    return scoop


def _body_half_x_at(
    r: ResolvedContainerLaundryDetergentBottleConfig, z_unscaled: float
) -> float:
    """Local (unscaled-width) half-x of the body at an unscaled z."""
    if r.body_shape == "square_shoulder":
        return SQ_BODY_W / 2.0
    if r.body_shape == "round_cylinder":
        sections = [(z, hx) for (z, hx, _hy) in _round_sections()]
    elif r.body_shape == "waisted_contour":
        sections = [(z, hx) for (z, hx, _hy) in _waist_sections()]
    else:
        sections = [(z, hx) for (z, hx, _hy) in _flat_oval_sections()]
    if z_unscaled <= sections[0][0]:
        return sections[0][1]
    if z_unscaled >= sections[-1][0]:
        return sections[-1][1]
    for (z0, v0), (z1, v1) in zip(sections, sections[1:]):
        if z0 <= z_unscaled <= z1:
            t = (z_unscaled - z0) / (z1 - z0) if z1 > z0 else 0.0
            return v0 + t * (v1 - v0)
    return sections[-1][1]


def _top_carry_solid(r: ResolvedContainerLaundryDetergentBottleConfig) -> cq.Workplane:
    """Inverted-U carry handle arching over the body top. Built from individually
    valid primitives (two vertical leg cylinders + a revolved half-torus arch)
    and fused — a single tight ``sweep`` of a U-path produces a self-intersecting
    (invalid) solid that downstream booleans silently truncate."""
    s = r.handle_size_scale
    tube_r = TC_TUBE_R * s
    foot_z_unscaled = 0.120
    foot_z = foot_z_unscaled * r.body_height_scale
    half_x_foot = _body_half_x_at(r, foot_z_unscaled) * r.body_width_scale
    leg_x = max(half_x_foot - 0.014, 0.026)
    peak_z = r.handle_peak_z
    # arch radius so the semicircle peak lands at peak_z; legs meet the arch at
    # the arch base z. The legs plunge ~30mm into the body for a robust fuse.
    arch_r = leg_x  # half-torus radius = leg half-span
    arch_base_z = peak_z - arch_r
    foot_bottom = foot_z - 0.030 * r.body_height_scale

    # Two vertical leg cylinders from deep in the body up to the arch base.
    leg_h = arch_base_z - foot_bottom
    legs = None
    for sign in (-1.0, 1.0):
        leg = (
            cq.Workplane("XY")
            .workplane(offset=foot_bottom)
            .center(sign * leg_x, 0.0)
            .circle(tube_r)
            .extrude(leg_h)
        )
        legs = leg if legs is None else legs.union(leg)

    # Half-torus arch: a clean, valid torus (ring radius arch_r, tube radius
    # tube_r) centered at (0,0,arch_base_z) lying in the XZ plane (normal = +Y),
    # then cut to keep only the top half (z >= arch_base_z) — an inverted-U that
    # peaks at arch_base_z + arch_r = peak_z. makeTorus is robust where a tight
    # U-path sweep produces an invalid self-intersecting solid.
    torus = cq.Solid.makeTorus(
        arch_r, tube_r, pnt=cq.Vector(0.0, 0.0, arch_base_z), dir=cq.Vector(0.0, 1.0, 0.0)
    )
    arch = cq.Workplane(obj=torus)
    lower_cut = (
        cq.Workplane("XY")
        .box(4.0 * arch_r + 0.1, 4.0 * tube_r + 0.1, 0.4, centered=(True, True, False))
        .translate((0.0, 0.0, arch_base_z - 0.4))
    )
    arch = arch.cut(lower_cut)
    handle = legs.union(arch)
    return handle


def _neck_collar_solid(
    r: ResolvedContainerLaundryDetergentBottleConfig,
) -> cq.Workplane:
    """Raised collar ring at the neck top — the flip-lid hinge seat."""
    collar = (
        cq.Workplane("XY")
        .workplane(offset=r.neck_top_z)
        .circle(r.collar_r)
        .extrude(r.collar_top_z - r.neck_top_z)
    )
    bore = (
        cq.Workplane("XY")
        .workplane(offset=r.neck_top_z - 0.001)
        .circle(r.neck_r - 0.002)
        .extrude(r.collar_top_z - r.neck_top_z + 0.002)
    )
    return collar.cut(bore)


def _spout_mesh(r: ResolvedContainerLaundryDetergentBottleConfig, *, short: bool):
    """Raised pour spout — a hollow funnel rising off the neck rim. short=True for
    the flip lid (stays below the disc). The spout's OUTER radius matches the neck
    outer radius and its base seats ~16mm below the neck top, so its wall coincides
    with the neck ring (a connected extension of the shell, NOT a ring floating in
    the now-open bore). Its bore keeps the mouth open: full mouth bore at the base
    tapering to a narrower pour lip at the rim."""
    base_z = r.neck_top_z - 0.016
    # Slightly larger than the neck outer radius so the spout flares OVER the neck
    # rim and genuinely overlaps the neck wall (coincident-surface contact alone
    # can read as a disconnected island), keeping it a connected shell extension.
    outer_r = r.neck_r + 0.0015
    lip_r = max(r.mouth_bore_r - 0.0035, 0.011)  # narrowed pour lip (still open)
    spout_h = 0.010 if short else 0.026
    o = cq.Workplane("XY").workplane(offset=base_z).circle(outer_r).extrude(spout_h)
    # Inner bore: open mouth radius at the base tapering to the pour lip at the top,
    # cut clean through the spout (and slightly into the neck ring) so the mouth
    # stays a continuous open channel down into the cavity.
    bore = (
        cq.Workplane("XY")
        .workplane(offset=base_z - 0.004)
        .circle(r.mouth_bore_r)
        .workplane(offset=spout_h + 0.006)
        .circle(lip_r)
        .loft(ruled=True)
    )
    spout = o.cut(bore)
    return mesh_from_cadquery(spout, "pour_spout")


# ---------------------------------------------------------------------------
# Body emission (Slot A + Slot B mesh ops + fixed decorations).
# ---------------------------------------------------------------------------
def _body_half_y_at(
    r: ResolvedContainerLaundryDetergentBottleConfig, z_unscaled: float
) -> float:
    """Local (unscaled-width) half-y of the body's front/back face at a given
    unscaled z, interpolated from the shape's section list. The result is the
    half_y BEFORE width scaling (callers multiply by body_width_scale)."""
    if r.body_shape == "square_shoulder":
        # flat broad face up to shoulder_z; constant half-d.
        return SQ_BODY_D / 2.0
    if r.body_shape == "round_cylinder":
        sections = [(z, hx) for (z, hx, _hy) in _round_sections()]
    elif r.body_shape == "waisted_contour":
        sections = [(z, hy) for (z, _hx, hy) in _waist_sections()]
    else:  # flat_oval_jug
        sections = [(z, hy) for (z, _hx, hy) in _flat_oval_sections()]
    # clamp to range and interpolate.
    if z_unscaled <= sections[0][0]:
        return sections[0][1]
    if z_unscaled >= sections[-1][0]:
        return sections[-1][1]
    for (z0, v0), (z1, v1) in zip(sections, sections[1:]):
        if z0 <= z_unscaled <= z1:
            t = (z_unscaled - z0) / (z1 - z0) if z1 > z0 else 0.0
            return v0 + t * (v1 - v0)
    return sections[-1][1]


def _front_face_y(
    r: ResolvedContainerLaundryDetergentBottleConfig, z_unscaled: float
) -> float:
    """World y of the front (-Y) broad face at the given unscaled z."""
    return -_body_half_y_at(r, z_unscaled) * r.body_width_scale


def _safe_union(a: cq.Workplane, b: cq.Workplane) -> cq.Workplane:
    return _occ_fuse(a, b)


def _emit_body(
    body,
    r: ResolvedContainerLaundryDetergentBottleConfig,
    *,
    body_mat,
    accent_mat,
    ring_mat,
) -> None:
    """Emit the ROOT body: jug shell (+ handle mesh op) + neck + spout + labels.
    For square body, emits 2 shell visuals (main_body + shoulder_neck)."""
    add_collar = r.closure == "flip_top_cap"
    short_spout = r.closure == "flip_top_cap"

    if r.body_shape == "square_shoulder":
        main = _square_main_box(r)
        # handle mesh ops apply to the main box (upper body region).
        if r.handle_grip == "side_loop_handle":
            main = _safe_union(main, _side_loop_solid(r))
        elif r.handle_grip == "recessed_grip":
            main = main.cut(_grip_recess_solid(r))
        elif r.handle_grip == "top_carry_handle":
            main = _safe_union(main, _top_carry_solid(r))
        body.visual(
            mesh_from_cadquery(main, "main_body"), material=body_mat, name="jug_shell", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"tide_orange_blue", "gain_green_white", "persil_white_red", "arm_hammer_yellow", "allfree_teal", "purex_purple", "downy_pink_twotone", "seventh_gen_matte_pearl"} else "plastic.frosted_translucent")
        )
        shoulder = _square_shoulder_neck(r)
        if add_collar:
            shoulder = _safe_union(shoulder, _neck_collar_solid(r))
        body.visual(
            mesh_from_cadquery(shoulder, "shoulder_neck"),
            material=body_mat,
            name="shoulder_neck", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"tide_orange_blue", "gain_green_white", "persil_white_red", "arm_hammer_yellow", "allfree_teal", "purex_purple", "downy_pink_twotone", "seventh_gen_matte_pearl"} else "plastic.frosted_translucent"),
        )
    else:
        shell = _loft_shell(r)
        if r.handle_grip == "side_loop_handle":
            shell = _safe_union(shell, _side_loop_solid(r))
        elif r.handle_grip == "recessed_grip":
            shell = shell.cut(_grip_recess_solid(r))
        elif r.handle_grip == "top_carry_handle":
            shell = _safe_union(shell, _top_carry_solid(r))
        if add_collar:
            shell = _safe_union(shell, _neck_collar_solid(r))
        body.visual(
            mesh_from_cadquery(shell, "jug_shell"), material=body_mat, name="jug_shell", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"tide_orange_blue", "gain_green_white", "persil_white_red", "arm_hammer_yellow", "allfree_teal", "purex_purple", "downy_pink_twotone", "seventh_gen_matte_pearl"} else "plastic.frosted_translucent")
        )

    # Fixed pour spout (random body main color).
    body.visual(_spout_mesh(r, short=short_spout), material=body_mat, name="pour_spout", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"tide_orange_blue", "gain_green_white", "persil_white_red", "arm_hammer_yellow", "allfree_teal", "purex_purple", "downy_pink_twotone", "seventh_gen_matte_pearl"} else "plastic.frosted_translucent"))

    if add_collar:
        # Small hinge riser so the lid hinge has real anchoring hardware.
        riser_h = 0.0035
        body.visual(
            Box((0.012, 0.008, riser_h)),
            origin=Origin(
                xyz=(0.0, -r.collar_r + 0.004, r.collar_top_z + riser_h / 2.0)
            ),
            material=body_mat,
            name="hinge_riser", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"tide_orange_blue", "gain_green_white", "persil_white_red", "arm_hammer_yellow", "allfree_teal", "purex_purple", "downy_pink_twotone", "seventh_gen_matte_pearl"} else "plastic.frosted_translucent"),
        )

    # ---- fixed decorations on the front (-Y) broad face (parent.visual) ----
    # Each label is placed at the local front face for its own z and embedded a
    # couple mm so it always contacts the shell (z-aware so the waist/round
    # narrow zones still touch).
    # Each label is a thick disc/band whose center sits a few mm INSIDE the
    # local nominal face so the proud half stays visible while the inner half
    # overlaps the shell mesh even where the loft/fillet pulls the wall in.
    # bullseye label disc (8mm thick along Y, center 3mm inside face).
    fy_label = _front_face_y(r, 0.095)
    body.visual(
        Cylinder(radius=0.030, length=0.008),
        origin=Origin(
            xyz=(-0.010, fy_label + 0.003, 0.095 * r.body_height_scale),
            rpy=(math.pi / 2.0, 0.0, 0.0),
        ),
        material=accent_mat,
        name="bullseye_label",
        appearance_only=AppearanceOnlySpec(kind="decal"),
    )
    # label band (8mm thick along Y).
    fy_band = _front_face_y(r, 0.060)
    body.visual(
        Box((0.060, 0.008, 0.018)),
        origin=Origin(xyz=(-0.010, fy_band + 0.003, 0.060 * r.body_height_scale)),
        material=ring_mat,
        name="label_band",
        appearance_only=AppearanceOnlySpec(kind="decal"),
    )
    # he badge (6mm thick along Y).
    fy_badge = _front_face_y(r, 0.150)
    body.visual(
        Cylinder(radius=0.014, length=0.006),
        origin=Origin(
            xyz=(-0.012, fy_badge + 0.003, 0.150 * r.body_height_scale),
            rpy=(math.pi / 2.0, 0.0, 0.0),
        ),
        material=ring_mat,
        name="he_badge",
        appearance_only=AppearanceOnlySpec(kind="decal"),
    )

    body.inertial = Inertial.from_geometry(
        Box((0.15, 0.095, 0.21 * r.body_height_scale)),
        mass=1.1,
        origin=Origin(xyz=(0.0, 0.0, 0.095 * r.body_height_scale)),
    )


# ---------------------------------------------------------------------------
# Closure builders (Slot C). Each parents directly to the body.
# ---------------------------------------------------------------------------
def _cap_cup_mesh(r: ResolvedContainerLaundryDetergentBottleConfig):
    """Translucent measuring-cup cap: tapered hollow cup open at the bottom.
    Local frame: open rim near z=0, closed dome at +Z."""
    r_bottom = r.cap_outer_r
    r_top = max(r.cap_outer_r - 0.0035, 0.018)
    # Inner bore at the open rim hugs the neck (== cap_bore_r ~ neck_r+clearance)
    # so the cup wall contacts the neck at rest (no floating cap).
    inner_bottom = r.cap_bore_r
    inner_top = max(r_top - 0.0028, 0.015)
    h = r.cap_height
    outer = (
        cq.Workplane("XY")
        .circle(r_bottom)
        .workplane(offset=h)
        .circle(r_top)
        .loft(ruled=True)
    )
    inner = (
        cq.Workplane("XY")
        .circle(inner_bottom)
        .workplane(offset=h - 0.010)
        .circle(inner_top)
        .loft(ruled=True)
    )
    cap = outer.cut(inner)
    return mesh_from_cadquery(cap, "cap_cup")


def _build_measuring_cup_cap(
    model, body, r: ResolvedContainerLaundryDetergentBottleConfig, *, cup_mat, ring_mat
) -> None:
    """CONTINUOUS spin (body->carrier) + PRISMATIC lift (carrier->cap) via a
    massless cap_carrier (parent screw-cap pattern)."""
    carrier = model.part("cap_carrier")  # NO visuals
    carrier.inertial = Inertial.from_geometry(Box((0.01, 0.01, 0.01)), mass=1e-4)

    cap = model.part("cap")
    cap.visual(_cap_cup_mesh(r), material=cup_mat, name="cap_cup", material_class_id="plastic.frosted_translucent")
    # Off-axis marker tab so rotation about +Z is observable.
    cap.visual(
        Box((0.006, 0.006, 0.010)),
        origin=Origin(xyz=(r.cap_outer_r - 0.003, 0.0, 0.030)),
        material=ring_mat,
        name="cap_marker", material_class_id="plastic.opaque_glossy_molded",
    )
    cap.inertial = Inertial.from_geometry(
        Cylinder(radius=r.cap_outer_r, length=r.cap_height),
        mass=0.03,
        origin=Origin(xyz=(0.0, 0.0, r.cap_height / 2.0)),
    )

    model.articulation(
        "cap_rotate",
        ArticulationType.CONTINUOUS,
        parent=body,
        child=carrier,
        origin=Origin(xyz=(0.0, 0.0, r.cap_seat_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=1.0, velocity=1.0),
    )
    model.articulation(
        "cap_slide",
        ArticulationType.PRISMATIC,
        parent=carrier,
        child=cap,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(
            lower=0.0, upper=r.cap_height, effort=1.0, velocity=1.0
        ),
    )


def _lid_mesh(r: ResolvedContainerLaundryDetergentBottleConfig):
    """Flip-top snap lid. Local frame origin at hinge (rear of collar top); disc
    center at +Y so it caps the mouth when closed (q=0)."""
    lid_radius = r.collar_r + 0.004
    lid_center_y = r.collar_r  # = -HINGE_Y
    lid_thickness = 0.004
    disc_bottom_z = 0.0025
    skirt_height = 0.009
    skirt_inner_r = r.lid_skirt_inner_r
    skirt_outer_r = skirt_inner_r + 0.0035

    disc = (
        cq.Workplane("XY")
        .workplane(offset=disc_bottom_z + lid_thickness)
        .center(0.0, lid_center_y)
        .circle(lid_radius)
        .extrude(-lid_thickness)
    )
    skirt = (
        cq.Workplane("XY")
        .workplane(offset=disc_bottom_z)
        .center(0.0, lid_center_y)
        .circle(skirt_outer_r)
        .circle(skirt_inner_r)
        .extrude(-skirt_height)
    )
    lid = disc.union(skirt)
    # living-hinge tab from origin to disc rear edge.
    tab_length = lid_radius * 0.6
    tab = (
        cq.Workplane("XY")
        .workplane(offset=disc_bottom_z + 0.001)
        .center(0.0, tab_length / 2.0)
        .rect(0.014, tab_length)
        .extrude(0.003)
    )
    lid = lid.union(tab)
    # grip nub.
    nub = (
        cq.Workplane("XY")
        .workplane(offset=disc_bottom_z + lid_thickness - 0.001)
        .center(0.0, lid_center_y + lid_radius * 0.55)
        .circle(0.006)
        .extrude(0.008)
    )
    lid = lid.union(nub)
    return mesh_from_cadquery(lid, "flip_lid")


def _build_flip_top_cap(
    model, body, r: ResolvedContainerLaundryDetergentBottleConfig, *, lid_mat
) -> None:
    """REVOLUTE +X flip lid hinged at the rear of the neck collar."""
    hinge_origin = (0.0, -r.collar_r, r.collar_top_z)
    lid_center_y = r.collar_r
    lid_radius = r.collar_r + 0.004
    lid_thickness = 0.004
    skirt_height = 0.009
    upper = 2.2 * r.closure_travel_scale

    lid = model.part("lid")
    lid.visual(_lid_mesh(r), material=lid_mat, name="flip_lid", material_class_id="plastic.opaque_glossy_molded")
    lid.inertial = Inertial.from_geometry(
        Cylinder(radius=lid_radius, length=lid_thickness + skirt_height),
        mass=0.015,
        origin=Origin(xyz=(0.0, lid_center_y, 0.0025 - skirt_height / 2.0)),
    )
    model.articulation(
        "body_to_lid",
        ArticulationType.REVOLUTE,
        parent=body,
        child=lid,
        origin=Origin(xyz=hinge_origin),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=2.0, velocity=4.0, lower=0.0, upper=upper),
    )


def _pump_housing_mesh(
    r: ResolvedContainerLaundryDetergentBottleConfig, *, collar_h, pump_cyl_h, pump_cyl_r
):
    """Screw collar + pump cylinder as one solid (local frame: collar bottom z=0)."""
    collar_outer_r = r.pump_collar_outer_r
    collar_inner_r = r.neck_r + 0.001
    collar = cq.Workplane("XY").circle(collar_outer_r).extrude(collar_h)
    transition = (
        cq.Workplane("XY")
        .workplane(offset=collar_h - 0.001)
        .circle(collar_outer_r - 0.001)
        .extrude(0.003)
    )
    pump_cyl = (
        cq.Workplane("XY")
        .workplane(offset=collar_h)
        .circle(pump_cyl_r)
        .extrude(pump_cyl_h)
    )
    housing = collar.union(transition).union(pump_cyl)
    bore = cq.Workplane("XY").circle(collar_inner_r).extrude(collar_h - 0.001)
    housing = housing.cut(bore)
    try:
        housing = housing.edges("<Z").fillet(0.002)
    except Exception:
        pass
    return mesh_from_cadquery(housing, "pump_housing")


def _actuator_head_mesh(head_r, head_h):
    head = cq.Workplane("XY").circle(head_r).extrude(head_h)
    try:
        head = head.edges(">Z").fillet(0.003)
    except Exception:
        pass
    return mesh_from_cadquery(head, "actuator_head")


def _build_pump_dispenser(
    model,
    body,
    r: ResolvedContainerLaundryDetergentBottleConfig,
    *,
    pump_mat,
    dark_mat,
    accent_mat,
) -> None:
    """CONTINUOUS screw collar (collar_screw) + PRISMATIC press-down actuator
    (pump_press), with a dip tube into the bottle."""
    collar_h = 0.024
    pump_cyl_h = 0.042
    pump_cyl_r = 0.017
    pump_top_local = collar_h + pump_cyl_h
    collar_outer_r = r.pump_collar_outer_r

    stem_r = 0.007
    stem_length = 0.048
    head_r = 0.022
    head_h = 0.011
    nozzle_length = 0.032
    nozzle_r = 0.004
    dip_r = 0.003
    dip_visible = 0.165 * r.body_height_scale
    dip_embed = 0.025
    dip_total = dip_visible + dip_embed
    stroke = 0.015 * r.closure_travel_scale
    grip_count = 6

    pump_base = model.part("pump_base")
    pump_base.visual(
        _pump_housing_mesh(
            r, collar_h=collar_h, pump_cyl_h=pump_cyl_h, pump_cyl_r=pump_cyl_r
        ),
        material=pump_mat,
        name="pump_housing", material_class_id="plastic.opaque_glossy_molded",
    )
    # collar grip ridges (module-local fixed decoration ring, NOT a multiplicity axis).
    for i in range(grip_count):
        angle = i * (2.0 * math.pi / grip_count)
        rr = collar_outer_r + 0.001
        x = rr * math.cos(angle)
        y = rr * math.sin(angle)
        pump_base.visual(
            Box((0.004, 0.002, collar_h * 0.70)),
            origin=Origin(xyz=(x, y, collar_h * 0.35), rpy=(0.0, 0.0, angle)),
            material=dark_mat,
            name=f"grip_ridge_{i}", material_class_id="plastic.opaque_glossy_molded",
        )
    # dip tube extends down into the bottle through the neck bore.
    dip_center_z = -(dip_visible - dip_embed) / 2.0
    pump_base.visual(
        Cylinder(radius=dip_r, length=dip_total),
        origin=Origin(xyz=(0.0, 0.0, dip_center_z)),
        material=pump_mat,
        name="dip_tube", material_class_id="plastic.opaque_glossy_molded",
    )
    # off-axis collar marker for rotation visibility.
    pump_base.visual(
        Box((0.005, 0.005, 0.008)),
        origin=Origin(xyz=(collar_outer_r + 0.002, 0.0, collar_h * 0.50)),
        material=accent_mat,
        name="collar_marker", material_class_id="plastic.opaque_glossy_molded",
    )
    pump_base.inertial = Inertial.from_geometry(
        Cylinder(radius=collar_outer_r, length=pump_top_local),
        mass=0.06,
        origin=Origin(xyz=(0.0, 0.0, pump_top_local / 2.0)),
    )

    pump_actuator = model.part("pump_actuator")
    pump_actuator.visual(
        _actuator_head_mesh(head_r, head_h), material=accent_mat, name="actuator_head", material_class_id="plastic.opaque_glossy_molded"
    )
    nozzle_cy = -(head_r * 0.40 + nozzle_length / 2.0)
    nozzle_cz = head_h * 0.55
    pump_actuator.visual(
        Cylinder(radius=nozzle_r, length=nozzle_length),
        origin=Origin(xyz=(0.0, nozzle_cy, nozzle_cz), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=pump_mat,
        name="nozzle_spout", material_class_id="plastic.opaque_glossy_molded",
    )
    pump_actuator.visual(
        Cylinder(radius=stem_r, length=stem_length),
        origin=Origin(xyz=(0.0, 0.0, -stem_length / 2.0)),
        material=dark_mat,
        name="actuator_stem", material_class_id="plastic.opaque_glossy_molded",
    )
    pump_actuator.inertial = Inertial.from_geometry(
        Cylinder(radius=head_r, length=head_h + stem_length),
        mass=0.025,
        origin=Origin(xyz=(0.0, 0.0, -(stem_length - head_h) / 2.0)),
    )

    model.articulation(
        "collar_screw",
        ArticulationType.CONTINUOUS,
        parent=body,
        child=pump_base,
        origin=Origin(xyz=(0.0, 0.0, r.cap_seat_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=2.0, velocity=1.0),
    )
    model.articulation(
        "pump_press",
        ArticulationType.PRISMATIC,
        parent=pump_base,
        child=pump_actuator,
        origin=Origin(xyz=(0.0, 0.0, pump_top_local)),
        axis=(0.0, 0.0, -1.0),
        motion_limits=MotionLimits(lower=0.0, upper=stroke, effort=5.0, velocity=0.5),
    )


# ---------------------------------------------------------------------------
# Build entry point
# ---------------------------------------------------------------------------
def build_container_laundry_detergent_bottle(
    config: ContainerLaundryDetergentBottleConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)

    pal = PALETTES[r.palette_style]
    body_mat = model.material(f"ldb_body_{r.palette_style}", rgba=pal.body)
    closure_mat = model.material(f"ldb_closure_{r.palette_style}", rgba=pal.closure)
    cup_mat = model.material(f"ldb_cup_{r.palette_style}", rgba=pal.cup)
    accent_mat = model.material(f"ldb_accent_{r.palette_style}", rgba=pal.accent)
    ring_mat = model.material(f"ldb_ring_{r.palette_style}", rgba=pal.ring)

    # --- ROOT: jug body (Slot A + Slot B mesh ops) ---
    body = model.part("body")
    _emit_body(body, r, body_mat=body_mat, accent_mat=accent_mat, ring_mat=ring_mat)

    # --- closure (Slot C) ---
    if r.closure == "measuring_cup_cap":
        _build_measuring_cup_cap(model, body, r, cup_mat=cup_mat, ring_mat=ring_mat)
    elif r.closure == "flip_top_cap":
        _build_flip_top_cap(model, body, r, lid_mat=closure_mat)
    elif r.closure == "pump_dispenser":
        _build_pump_dispenser(
            model, body, r, pump_mat=closure_mat, dark_mat=ring_mat, accent_mat=accent_mat
        )

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_container_laundry_detergent_bottle(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_container_laundry_detergent_bottle(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests / QC. Captured-fit overlaps (cap skirt over neck, lid over collar, dip
# tube through neck, stem in cylinder) are declared element-scoped so the
# sweep's overlap/island checks pass; each closure's actions are exercised.
# ---------------------------------------------------------------------------
def _ext(aabb):
    mn, mx = aabb
    return (mx[0] - mn[0], mx[1] - mn[1], mx[2] - mn[2])


def run_container_laundry_detergent_bottle_tests(
    object_model: ArticulatedObject,
    config: ContainerLaundryDetergentBottleConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)

    body = object_model.get_part("body")

    # ---- jug body rests on the ground (base near z=0) ----
    aabb = ctx.part_world_aabb(body)
    bext = _ext(aabb)
    ctx.check(
        "jug body rests on the ground (base near z=0)",
        abs(aabb[0][2]) < 0.012,
        details=f"body min z={aabb[0][2]:.4f}",
    )
    ctx.check(
        "jug body has real volume",
        bext[0] > 0.05 and bext[1] > 0.04 and bext[2] > 0.10,
        details=f"body extents={bext}",
    )

    # ---- handle_grip identity ----
    shell_aabb = ctx.part_element_world_aabb(body, elem="jug_shell")
    if r.handle_grip == "side_loop_handle":
        # The side loop reaches well past the body's own +X half-width (the loop
        # grip bar sticks out on +X); compare against the body -X extent so the
        # check is scale-robust for narrow bodies.
        body_minus_x = abs(shell_aabb[0][0]) if shell_aabb is not None else 0.0
        ctx.check(
            "side loop handle extends out on +X past the body footprint",
            shell_aabb is not None and shell_aabb[1][0] > body_minus_x + 0.018,
            details=f"jug_shell x-max={None if shell_aabb is None else shell_aabb[1][0]}, "
            f"body -x extent={body_minus_x:.4f}",
        )
    elif r.handle_grip == "top_carry_handle":
        full_aabb = ctx.part_world_aabb(body)
        ctx.check(
            "top carry handle arches above the cap/neck region",
            full_aabb is not None and full_aabb[1][2] > r.handle_peak_z - 0.010,
            details=f"body z-max={None if full_aabb is None else full_aabb[1][2]}, "
            f"peak={r.handle_peak_z:.4f}",
        )

    # ---- bullseye label on the front face ----
    ctx.expect_contact(
        body,
        body,
        elem_a="bullseye_label",
        elem_b="jug_shell",
        name="bullseye label is on the jug body",
    )

    # ---- closure: actions + captured-fit overlaps ----
    # On the square body the threaded neck lives in the separate "shoulder_neck"
    # visual, so any closure that seats over the neck also overlaps it; declare
    # that captured-fit allowance for the square body's closures.
    is_square = r.body_shape == "square_shoulder"

    if r.closure == "measuring_cup_cap":
        carrier = object_model.get_part("cap_carrier")
        cap = object_model.get_part("cap")
        rotate = object_model.get_articulation("cap_rotate")
        slide = object_model.get_articulation("cap_slide")

        # The measuring cup lifts clear of the neck when unscrewed.
        ctx.allow_isolated_part(
            cap,
            reason="measuring-cup cap slides up off the neck and loses contact with the body",
        )

        ctx.allow_overlap(
            cap,
            body,
            elem_a="cap_cup",
            elem_b="jug_shell",
            reason="The measuring-cup cap screws down over the threaded neck (skirt overlaps neck).",
        )
        ctx.allow_overlap(
            cap,
            body,
            elem_a="cap_cup",
            elem_b="pour_spout",
            reason="The fixed pour spout sits inside the inverted measuring cup when capped.",
        )
        if is_square:
            ctx.allow_overlap(
                cap,
                body,
                elem_a="cap_cup",
                elem_b="shoulder_neck",
                reason="The cup skirt screws down over the square body's neck visual.",
            )
        ctx.check(
            "cap_carrier is massless (no visuals)",
            len(carrier.visuals) == 0,
            details=f"carrier visuals={len(carrier.visuals)}",
        )
        ctx.check(
            "cap_rotate is CONTINUOUS about +Z",
            rotate.articulation_type == ArticulationType.CONTINUOUS
            and abs(rotate.axis[2]) > 0.99,
            details=f"axis={rotate.axis}, type={rotate.articulation_type}",
        )
        # cap is translucent (alpha < 1) — measuring-cup identity.
        mat = cap.get_visual("cap_cup").material
        alpha = mat.rgba[3] if mat is not None and mat.rgba is not None else 1.0
        ctx.check(
            "measuring cup is translucent (alpha < 1)",
            alpha < 1.0,
            details=f"cap rgba={None if mat is None else mat.rgba}",
        )
        # rotation swings the off-axis marker about +Z.
        m0 = ctx.part_element_world_aabb(cap, elem="cap_marker")
        m0c = ((m0[0][0] + m0[1][0]) / 2.0, (m0[0][1] + m0[1][1]) / 2.0)
        with ctx.pose({rotate: math.pi / 2.0}):
            m1 = ctx.part_element_world_aabb(cap, elem="cap_marker")
            m1c = ((m1[0][0] + m1[1][0]) / 2.0, (m1[0][1] + m1[1][1]) / 2.0)
        ctx.check(
            "cap rotation swings the off-axis marker about +Z",
            math.hypot(m1c[0] - m0c[0], m1c[1] - m0c[1]) > 0.015,
            details=f"marker rest={m0c}, quarter-turn={m1c}",
        )
        # slide lifts the cap off the neck.
        rest_z = ctx.part_world_position(cap)[2]
        with ctx.pose({slide: r.cap_height}):
            lifted_z = ctx.part_world_position(cap)[2]
        ctx.check(
            "cap slides up off the neck",
            lifted_z > rest_z + r.cap_height * 0.5,
            details=f"rest_z={rest_z:.4f}, lifted_z={lifted_z:.4f}",
        )
        # decoupled: rotation does not lift.
        with ctx.pose({rotate: math.pi}):
            rot_only_z = ctx.part_world_position(cap)[2]
        ctx.check(
            "rotation is decoupled from lift",
            abs(rot_only_z - rest_z) < 1e-4,
            details=f"rest_z={rest_z:.4f}, rotated_z={rot_only_z:.4f}",
        )

    elif r.closure == "flip_top_cap":
        lid = object_model.get_part("lid")
        hinge = object_model.get_articulation("body_to_lid")
        ctx.allow_overlap(
            lid,
            body,
            elem_a="flip_lid",
            elem_b="jug_shell",
            reason="The flip lid skirt wraps the neck collar / rests on the rim when closed.",
        )
        ctx.allow_overlap(
            lid,
            body,
            elem_a="flip_lid",
            elem_b="pour_spout",
            reason="The closed flip lid caps the short pour spout.",
        )
        if is_square:
            ctx.allow_overlap(
                lid,
                body,
                elem_a="flip_lid",
                elem_b="shoulder_neck",
                reason="The flip lid skirt wraps the square body's neck/collar visual.",
            )
        ctx.check(
            "body_to_lid is REVOLUTE about +X",
            hinge.articulation_type == ArticulationType.REVOLUTE
            and abs(hinge.axis[0]) > 0.99,
            details=f"axis={hinge.axis}, type={hinge.articulation_type}",
        )
        # flip the lid up: top rises.
        top0 = ctx.part_world_aabb(lid)[1][2]
        with ctx.pose({hinge: 1.0}):
            top1 = ctx.part_world_aabb(lid)[1][2]
        ctx.check(
            "body_to_lid flips the lid up (top rises)",
            top1 > top0 + 0.005,
            details=f"closed_top_z={top0:.4f}, open_top_z={top1:.4f}",
        )
        # closed lid sits at the neck/collar top (compare to the collar top, not
        # the whole-body z-max which may include a towering top_carry handle).
        lid_aabb = ctx.part_world_aabb(lid)
        ctx.check(
            "closed lid sits at the neck collar top",
            lid_aabb is not None
            and lid_aabb[1][2] >= r.collar_top_z - 0.005
            and lid_aabb[0][2] <= r.collar_top_z + 0.020,
            details=f"lid z-range=[{lid_aabb[0][2]:.4f},{lid_aabb[1][2]:.4f}], "
            f"collar_top_z={r.collar_top_z:.4f}",
        )
        # lid is opaque (distinct from translucent measuring cup).
        mat = lid.get_visual("flip_lid").material
        ctx.check(
            "flip lid is opaque",
            mat is not None and mat.rgba[3] >= 0.99,
            details=f"lid rgba={None if mat is None else mat.rgba}",
        )

    elif r.closure == "pump_dispenser":
        pump_base = object_model.get_part("pump_base")
        pump_actuator = object_model.get_part("pump_actuator")
        collar_screw = object_model.get_articulation("collar_screw")
        pump_press = object_model.get_articulation("pump_press")

        # The pump head strokes inside the collar, staying in sliding contact
        # with the pump housing along its travel.
        ctx.allow_overlap(
            pump_actuator,
            pump_base,
            reason="pump head strokes in sliding contact inside the pump housing",
        )

        ctx.allow_overlap(
            pump_base,
            body,
            elem_a="pump_housing",
            elem_b="jug_shell",
            reason="The screw collar fits over the threaded neck.",
        )
        ctx.allow_overlap(
            pump_base,
            body,
            elem_a="pump_housing",
            elem_b="pour_spout",
            reason="The pump housing encloses the pour spout under the collar.",
        )
        ctx.allow_overlap(
            pump_base,
            body,
            elem_a="dip_tube",
            elem_b="jug_shell",
            reason="The dip tube passes through the neck bore into the bottle.",
        )
        ctx.allow_overlap(
            pump_actuator,
            pump_base,
            elem_a="actuator_stem",
            elem_b="pump_housing",
            reason="The actuator stem slides inside the pump cylinder bore.",
        )
        if is_square:
            ctx.allow_overlap(
                pump_base,
                body,
                elem_a="pump_housing",
                elem_b="shoulder_neck",
                reason="The screw collar fits over the square body's neck visual.",
            )
            ctx.allow_overlap(
                pump_base,
                body,
                elem_a="dip_tube",
                elem_b="shoulder_neck",
                reason="The dip tube passes through the square body's neck bore.",
            )
        ctx.check(
            "collar_screw is CONTINUOUS about +Z",
            collar_screw.articulation_type == ArticulationType.CONTINUOUS
            and abs(collar_screw.axis[2]) > 0.99,
            details=f"axis={collar_screw.axis}, type={collar_screw.articulation_type}",
        )
        ctx.check(
            "pump_press is PRISMATIC about -Z",
            pump_press.articulation_type == ArticulationType.PRISMATIC
            and pump_press.axis[2] < -0.99,
            details=f"axis={pump_press.axis}, type={pump_press.articulation_type}",
        )
        # press moves the actuator downward.
        rest_z = ctx.part_world_position(pump_actuator)[2]
        with ctx.pose({pump_press: 0.015 * r.closure_travel_scale}):
            pressed_z = ctx.part_world_position(pump_actuator)[2]
        ctx.check(
            "pump press moves actuator downward",
            pressed_z < rest_z - 0.008,
            details=f"rest_z={rest_z:.4f}, pressed_z={pressed_z:.4f}",
        )
        # collar rotation swings the nozzle around +Z.
        nozzle_rest = ctx.part_element_world_aabb(pump_actuator, elem="nozzle_spout")
        with ctx.pose({collar_screw: math.pi / 2.0}):
            nozzle_rot = ctx.part_element_world_aabb(pump_actuator, elem="nozzle_spout")
        rest_cx = (nozzle_rest[0][0] + nozzle_rest[1][0]) / 2.0
        rest_cy = (nozzle_rest[0][1] + nozzle_rest[1][1]) / 2.0
        rot_cx = (nozzle_rot[0][0] + nozzle_rot[1][0]) / 2.0
        rot_cy = (nozzle_rot[0][1] + nozzle_rot[1][1]) / 2.0
        swing = math.hypot(rot_cx - rest_cx, rot_cy - rest_cy)
        ctx.check(
            "collar rotation swings the nozzle around +Z",
            swing > 0.012,
            details=f"swing={swing:.4f}",
        )
        # dip tube extends deep into the bottle.
        dip_aabb = ctx.part_element_world_aabb(pump_base, elem="dip_tube")
        ctx.check(
            "dip tube extends deep into the bottle interior",
            dip_aabb is not None and dip_aabb[0][2] < 0.05,
            details=f"dip_tube z-min={None if dip_aabb is None else dip_aabb[0][2]}",
        )

    # ---- at least one non-fixed closure joint exists ----
    non_fixed = [
        j
        for j in object_model.articulations
        if j.articulation_type != ArticulationType.FIXED
    ]
    ctx.check(
        "at least one non-fixed closure joint exists",
        len(non_fixed) >= 1,
        details=f"non-fixed joints={[j.name for j in non_fixed]}",
    )

    return ctx.report()


object_model = build_container_laundry_detergent_bottle()
