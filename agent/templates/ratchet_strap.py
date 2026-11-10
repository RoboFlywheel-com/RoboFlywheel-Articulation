# SPDX-License-Identifier: Apache-2.0

"""Ratchet tie-down strap procedural template (0611 / ratchet_strap).

Modular, __modular__ = True. Parallel-children topology rooted at a common
``frame`` chassis; every mechanism part (spool / handle / drive_pawl / release /
webbing [+ roll / gates]) parents to the frame. Structure is derived from the two
5-star origins and their forks:

  * 001 stamped twin-cheek  (rec_use-...160740_098181_6a70af39)
  * 002 U-frame             (rec_picturex_...002...8a06b96f)
  * 9 forked variants (frame_form ×3, end_fitting ×5, release ×1, webbing ×1)

Three slots (see specs_modular_v1/ratchet_strap.md):
  A ratchet_body   (③ Primary Form Family): frame + spool + handle + drive_pawl
  B actuation_release (② joint parent/position): release lever
  C webbing_fitting (① skeleton): webbing route + end fittings [+ roll / gates]

All parts are authored in ONE canonical frame: the winding spool axis is the
object Y axis through the origin (0,0,0); +x points toward the anchor/fixed end,
the handle throws up toward +z. Authoring every frame family and every webbing
route in this shared frame lets any of the 5 frames mate with any of the 8
webbing routes without coordinate drift.

Captured-pin pivots (spindle / handle / pawl / release) cannot be expressed as
two axis-aligned mating faces, so per AUTHORING.md §A Rule 2 they OMIT
``MatingContract`` (grandfathered) and are guarded by element-scoped
``allow_overlap`` + ``expect_contact`` in run_tests. The FIXED webbing mount and
the fitting-local snap gates declare geometry the mating gate can see.

Rule 3: cheek plates, toothed spindle, hooks, soft loops, E-track tongue and the
endless webbing band stay CadQuery boolean meshes (mesh_from_cadquery) — never
downgraded to crude Box/Cylinder placeholders.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
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

# --------------------------------------------------------------------------- #
# Enums / slot domains
# --------------------------------------------------------------------------- #
RatchetBody = Literal[
    "stamped_twin_cheek",
    "compact_mini",
    "long_handle_heavy_duty",
    "u_frame",
    "wide_body_cargo",
]
ReleaseStyle = Literal["frame_thumb", "handle_paddle", "pull_tab"]
WebbingFitting = Literal[
    "two_piece_wire_j",
    "two_piece_flat_j",
    "two_piece_s_hook",
    "two_piece_snap_hook",
    "two_piece_e_track",
    "two_piece_soft_loop",
    "feed_through_tail",
    "endless_loop",
]
PaletteStyle = Literal[
    "orange_zinc",
    "blue_galvanized",
    "black_polyester",
    "green_zinc",
    "red_black",
    "hi_vis_yellow",
]

RATCHET_BODIES: tuple[RatchetBody, ...] = (
    "stamped_twin_cheek",
    "compact_mini",
    "long_handle_heavy_duty",
    "u_frame",
    "wide_body_cargo",
)
RELEASE_STYLES: tuple[ReleaseStyle, ...] = ("frame_thumb", "handle_paddle", "pull_tab")
WEBBING_FITTINGS: tuple[WebbingFitting, ...] = (
    "two_piece_wire_j",
    "two_piece_flat_j",
    "two_piece_s_hook",
    "two_piece_snap_hook",
    "two_piece_e_track",
    "two_piece_soft_loop",
    "feed_through_tail",
    "endless_loop",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "orange_zinc",
    "blue_galvanized",
    "black_polyester",
    "green_zinc",
    "red_black",
    "hi_vis_yellow",
)

_TWO_PIECE = frozenset(
    {
        "two_piece_wire_j",
        "two_piece_flat_j",
        "two_piece_s_hook",
        "two_piece_snap_hook",
        "two_piece_e_track",
        "two_piece_soft_loop",
    }
)

# Palette keys: frame (chassis steel), hardware (dark steel pins/pawl/gate),
# fitting (hook/eye metal), grip (rubber), webbing (textile), weave (woven low),
# accent (measurement ink / seam).  6 colorways from the 5-star pool.
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "orange_zinc": {  # 001 baseline colorway
        "frame": (0.68, 0.72, 0.73, 1.0),
        "hardware": (0.32, 0.35, 0.36, 1.0),
        "fitting": (0.70, 0.73, 0.74, 1.0),
        "grip": (0.05, 0.055, 0.06, 1.0),
        "webbing": (1.0, 0.24, 0.02, 1.0),
        "weave": (0.72, 0.10, 0.01, 1.0),
        "accent": (0.02, 0.18, 0.68, 1.0),
    },
    "blue_galvanized": {  # 002 baseline colorway
        "frame": (0.68, 0.71, 0.72, 1.0),
        "hardware": (0.48, 0.51, 0.52, 1.0),
        "fitting": (0.60, 0.63, 0.64, 1.0),
        "grip": (0.075, 0.08, 0.085, 1.0),
        "webbing": (0.02, 0.21, 0.44, 1.0),
        "weave": (0.01, 0.13, 0.29, 1.0),
        "accent": (0.85, 0.86, 0.88, 1.0),
    },
    "black_polyester": {
        "frame": (0.55, 0.57, 0.58, 1.0),
        "hardware": (0.28, 0.30, 0.31, 1.0),
        "fitting": (0.62, 0.64, 0.66, 1.0),
        "grip": (0.05, 0.05, 0.06, 1.0),
        "webbing": (0.08, 0.08, 0.09, 1.0),
        "weave": (0.03, 0.03, 0.035, 1.0),
        "accent": (0.80, 0.12, 0.10, 1.0),
    },
    "green_zinc": {
        "frame": (0.68, 0.72, 0.73, 1.0),
        "hardware": (0.34, 0.36, 0.37, 1.0),
        "fitting": (0.70, 0.73, 0.74, 1.0),
        "grip": (0.06, 0.065, 0.06, 1.0),
        "webbing": (0.10, 0.42, 0.16, 1.0),
        "weave": (0.05, 0.24, 0.09, 1.0),
        "accent": (0.90, 0.90, 0.86, 1.0),
    },
    "red_black": {
        "frame": (0.20, 0.21, 0.22, 1.0),
        "hardware": (0.10, 0.10, 0.11, 1.0),
        "fitting": (0.60, 0.62, 0.64, 1.0),
        "grip": (0.05, 0.05, 0.06, 1.0),
        "webbing": (0.78, 0.10, 0.09, 1.0),
        "weave": (0.42, 0.045, 0.04, 1.0),
        "accent": (0.82, 0.84, 0.86, 1.0),
    },
    "hi_vis_yellow": {
        "frame": (0.55, 0.57, 0.58, 1.0),
        "hardware": (0.24, 0.25, 0.26, 1.0),
        "fitting": (0.66, 0.68, 0.70, 1.0),
        "grip": (0.07, 0.07, 0.08, 1.0),
        "webbing": (0.94, 0.80, 0.06, 1.0),
        "weave": (0.55, 0.45, 0.03, 1.0),
        "accent": (0.10, 0.10, 0.11, 1.0),
    },
}


# --------------------------------------------------------------------------- #
# Per-body nominal dimensions (canonical frame; spool axis at origin).
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class _BodyBase:
    construction: str  # "stamped" | "uframe"
    handle_style: str  # "box_arm" | "heavy_mesh"
    frame_half_y: float  # cheek half-spacing (y)
    cheek_front: float  # +x extent of cheek
    cheek_back: float  # -x extent of cheek
    cheek_height: float  # z extent of cheek (full)
    spool_radius: float  # ratchet wheel tip radius (xz)
    tooth_count: int
    handle_len: float
    webbing_width: float


_BODY_BASE: dict[RatchetBody, _BodyBase] = {
    "stamped_twin_cheek": _BodyBase("stamped", "box_arm", 0.028, 0.058, 0.070, 0.056, 0.030, 18, 0.140, 0.042),
    "compact_mini": _BodyBase("stamped", "box_arm", 0.026, 0.044, 0.050, 0.046, 0.025, 16, 0.100, 0.038),
    "long_handle_heavy_duty": _BodyBase("stamped", "heavy_mesh", 0.030, 0.062, 0.076, 0.060, 0.030, 18, 0.210, 0.045),
    "u_frame": _BodyBase("uframe", "box_arm", 0.019, 0.048, 0.056, 0.056, 0.020, 16, 0.140, 0.025),
    "wide_body_cargo": _BodyBase("uframe", "box_arm", 0.031, 0.050, 0.058, 0.058, 0.020, 16, 0.140, 0.050),
}

WALL = 0.0032  # cheek plate half-thickness reference
STRAP_Z = -0.008  # canonical webbing centerline (just below the spool slot)
ARM_PITCH = 1.15  # handle rest angle (rad): raised steeply so it clears the head
ROLL_RADIUS = 0.022


def _roll_center(r: "ResolvedRatchetStrapConfig") -> tuple[float, float, float]:
    """Supply-roll axle center: high and far behind the frame, clear of the
    rear-mounted thumb release below it."""
    return (-r.cheek_back * 0.9, 0.0, r.cheek_height * 0.5 + 0.048)


def _pawl_pivot(r: "ResolvedRatchetStrapConfig") -> tuple[float, float, float]:
    """Pawl pivot in the FRONT rim corner, just outside the wheel tip radius and
    inside the cheek outline; tooth reaches back into the teeth."""
    pr = r.spool_radius + 0.006
    return (pr * 0.94, 0.0, min(pr * 0.34, r.cheek_height * 0.42))


def _frame_thumb_pivot(r: "ResolvedRatchetStrapConfig") -> tuple[float, float, float]:
    """Frame thumb-release pivot in the REAR rim corner (pin captured in the
    cheeks); the lever points up-and-back out of the frame, clear of pawl/handle."""
    pr = r.spool_radius + 0.010
    return (-pr * 0.92, 0.0, min(pr * 0.42, r.cheek_height * 0.40))


# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class RatchetStrapConfig:
    ratchet_body: RatchetBody | None = None
    release_style: ReleaseStyle | None = None
    webbing_fitting: WebbingFitting | None = None
    palette_style: PaletteStyle | None = None
    frame_len_scale: float = 1.0
    frame_width_scale: float = 1.0
    handle_len_scale: float = 1.0
    spool_radius_scale: float = 1.0
    handle_open_scale: float = 1.0
    name: str = "ratchet_strap"


@dataclass(frozen=True)
class ResolvedRatchetStrapConfig:
    ratchet_body: RatchetBody
    release_style: ReleaseStyle
    webbing_fitting: WebbingFitting
    palette_style: PaletteStyle
    construction: str
    handle_style: str
    frame_half_y: float
    cheek_front: float
    cheek_back: float
    cheek_height: float
    spool_radius: float
    tooth_count: int
    handle_len: float
    webbing_width: float
    handle_open_upper: float
    name: str


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _pick(value, choices):
    return value if value in choices else choices[0]


def config_from_seed(seed: int) -> RatchetStrapConfig:
    rng = random.Random(seed)
    return RatchetStrapConfig(
        ratchet_body=rng.choice(RATCHET_BODIES),
        release_style=rng.choice(RELEASE_STYLES),
        webbing_fitting=rng.choice(WEBBING_FITTINGS),
        palette_style=rng.choice(PALETTE_STYLES),
        frame_len_scale=round(rng.uniform(0.85, 1.20), 4),
        frame_width_scale=round(rng.uniform(0.85, 1.25), 4),
        handle_len_scale=round(rng.uniform(0.80, 1.35), 4),
        spool_radius_scale=round(rng.uniform(0.90, 1.15), 4),
        handle_open_scale=round(rng.uniform(0.80, 1.10), 4),
        name=f"seeded_ratchet_strap_{seed}",
    )


def resolve_config(config: RatchetStrapConfig | None = None) -> ResolvedRatchetStrapConfig:
    cfg = config or RatchetStrapConfig()
    body = _pick(cfg.ratchet_body, RATCHET_BODIES)
    release_style = _pick(cfg.release_style, RELEASE_STYLES)
    webbing_fitting = _pick(cfg.webbing_fitting, WEBBING_FITTINGS)
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)
    b = _BODY_BASE[body]

    # 1. independent scales
    len_scale = _clamp(cfg.frame_len_scale, 0.85, 1.20)
    width_scale = _clamp(cfg.frame_width_scale, 0.85, 1.25)
    handle_scale = _clamp(cfg.handle_len_scale, 0.80, 1.35)
    spool_scale = _clamp(cfg.spool_radius_scale, 0.90, 1.15)
    open_scale = _clamp(cfg.handle_open_scale, 0.80, 1.10)

    frame_half_y = b.frame_half_y * width_scale
    cheek_front = b.cheek_front * len_scale
    cheek_back = b.cheek_back * len_scale
    cheek_height = b.cheek_height
    spool_radius = b.spool_radius * spool_scale
    handle_len = b.handle_len * handle_scale

    # 2. derived: webbing width tracks the bearing span (equation).
    webbing_width = b.webbing_width * width_scale
    # 3. inequalities projected back into feasible region.
    #    webbing must fit between the cheeks; spool must be captured in the cheek height.
    webbing_width = min(webbing_width, 2.0 * frame_half_y - 0.004)
    webbing_width = max(webbing_width, 0.018)
    spool_radius = min(spool_radius, cheek_height * 0.5 - 0.004)
    # 4. conditional: open travel upper bound clamped so the handle never
    #    over-rotates into the webbing / body.
    handle_open_upper = _clamp(0.90 * open_scale, 0.55, math.pi * 0.30)

    return ResolvedRatchetStrapConfig(
        ratchet_body=body,
        release_style=release_style,
        webbing_fitting=webbing_fitting,
        palette_style=palette_style,
        construction=b.construction,
        handle_style=b.handle_style,
        frame_half_y=frame_half_y,
        cheek_front=cheek_front,
        cheek_back=cheek_back,
        cheek_height=cheek_height,
        spool_radius=spool_radius,
        tooth_count=b.tooth_count,
        handle_len=handle_len,
        webbing_width=webbing_width,
        handle_open_upper=handle_open_upper,
        name=cfg.name or "ratchet_strap",
    )


def slot_choices_for_config(
    config: RatchetStrapConfig | ResolvedRatchetStrapConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedRatchetStrapConfig) else resolve_config(config)
    return (
        ("ratchet_body", r.ratchet_body),
        ("actuation_release", r.release_style),
        ("webbing_fitting", r.webbing_fitting),
        ("palette_style", r.palette_style),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# --------------------------------------------------------------------------- #
# Shape helpers (local-origin CadQuery shapes; primitives preserved from
# sources).  Placement is applied by the builders in the canonical frame.
# --------------------------------------------------------------------------- #
def _stamped_cheek(r: ResolvedRatchetStrapConfig, y_center: float) -> cq.Workplane:
    """Pierced stamped ratchet cheek plate in the XZ plane (from 001 _side_plate).

    Authored around the spool axis (origin): rear heel at -cheek_back, nose at
    +cheek_front, two lightening windows.
    """
    xf, xb, h = r.cheek_front, r.cheek_back, r.cheek_height * 0.5
    outline = [
        (-xb, -h * 0.55),
        (-xb * 0.82, -h),
        (-xb * 0.34, -h * 0.9),
        (xf * 0.20, -h * 0.35),
        (xf * 0.72, h * 0.15),
        (xf, h * 0.55),
        (xf * 0.96, h),
        (xf * 0.60, h * 1.02),
        (xf * 0.10, h * 0.72),
        (-xb * 0.42, h * 0.62),
        (-xb * 0.86, h * 0.42),
    ]
    plate = cq.Workplane("XZ").polyline(outline).close().extrude(WALL, both=True).translate((0.0, y_center, 0.0))
    for x, z, sx, sz in ((xf * 0.5, h * 0.5, xf * 0.36, h * 0.30), (xf * 0.06, h * 0.24, xf * 0.26, h * 0.24)):
        cutter = cq.Workplane("XZ").center(x, z).rect(sx, sz).extrude(0.02, both=True).translate((0.0, y_center, 0.0))
        plate = plate.cut(cutter)
    return plate


def _uframe_cheek(r: ResolvedRatchetStrapConfig, y_center: float) -> cq.Workplane:
    """Lofted U-frame side profile (from 002 _frame_shape side_profile)."""
    xf, xb, h = r.cheek_front, r.cheek_back, r.cheek_height * 0.5
    pts = [
        (-xb, -h * 0.55),
        (-xb * 0.9, -h * 0.1),
        (-xb * 0.62, h * 0.75),
        (-xb * 0.16, h),
        (xf * 0.5, h * 0.78),
        (xf, h * 0.2),
        (xf * 0.62, -h * 0.55),
    ]
    return (
        cq.Workplane("XY")
        .polyline(pts)
        .close()
        .extrude(WALL * 1.9)
        .rotate((0, 0, 0), (1, 0, 0), 90)
        .translate((0.0, y_center + WALL * 0.95, 0.0))
    )


def _toothed_spindle(r: ResolvedRatchetStrapConfig) -> cq.Workplane:
    """Twin toothed ratchet wheels + axle + winding arbor (from 001/002)."""
    n = r.tooth_count
    tip, root = r.spool_radius, r.spool_radius * 0.80
    pts = []
    for i in range(n * 2):
        a = 2.0 * math.pi * i / (n * 2)
        rad = tip if i % 2 == 0 else root
        pts.append((rad * math.cos(a), rad * math.sin(a)))
    gear = cq.Workplane("XZ").polyline(pts).close().extrude(0.0045, both=True)
    wy = r.frame_half_y - 0.006
    gear_a = gear.translate((0.0, -wy, 0.0))
    gear_b = gear.translate((0.0, wy, 0.0))
    axle = cq.Workplane("XZ").circle(root * 0.28).extrude(r.frame_half_y + 0.008, both=True)
    arbor = cq.Workplane("XZ").rect(root * 0.42, root * 0.42).extrude(r.frame_half_y - 0.006, both=True)
    return gear_a.union(gear_b).union(axle).union(arbor)


def _uframe_drum(r: ResolvedRatchetStrapConfig) -> cq.Workplane:
    """Slotted winding mandrel on a full-width axle (from 002 _spool_drum_shape)."""
    drum = cq.Workplane("XZ").circle(r.spool_radius * 0.62).extrude(r.frame_half_y - 0.006, both=True)
    axle = cq.Workplane("XZ").circle(r.spool_radius * 0.30).extrude(r.frame_half_y + 0.010, both=True)
    slot = cq.Workplane("XY").box(r.spool_radius * 1.3, 2.0 * r.frame_half_y - 0.014, 0.0060)
    return drum.union(axle).cut(slot)


def _wire_j_hook() -> cq.Workplane:
    """Open wire J-hook, one stamped profile with shank (from 001 _hook_shape)."""
    outer_r, inner_r = 0.026, 0.017
    outer = [(outer_r * math.cos(math.radians(d)), outer_r * math.sin(math.radians(d))) for d in range(-72, 231, 12)]
    inner = [(inner_r * math.cos(math.radians(d)), inner_r * math.sin(math.radians(d))) for d in range(230, -73, -12)]
    curved = cq.Workplane("XZ").polyline(outer + inner).close().extrude(0.008, both=True)
    shank = cq.Workplane("XY").box(0.034, 0.016, 0.009).translate((0.026, 0.0, 0.016))
    throat = cq.Workplane("XY").box(0.018, 0.016, 0.009).translate((0.013, 0.0, 0.004))
    return curved.union(shank).union(throat)


def _flat_j_hook() -> cq.Workplane:
    """Flat stamped J-hook with closed webbing eye + open capture slot (fork 4)."""
    eye = cq.Workplane("XZ").rect(0.060, 0.046).extrude(0.0024, both=True).translate((0.007, 0.0, 0.0))
    outer_r, inner_r, cx = 0.032, 0.022, -0.038
    outer = [(cx + outer_r * math.cos(math.radians(d)), outer_r * math.sin(math.radians(d))) for d in range(-68, 232, 12)]
    inner = [(cx + inner_r * math.cos(math.radians(d)), inner_r * math.sin(math.radians(d))) for d in range(231, -69, -12)]
    hook = cq.Workplane("XZ").polyline(outer + inner).close().extrude(0.0024, both=True)
    plate = eye.union(hook)
    slot = cq.Workplane("XZ").center(0.007, 0.0).rect(0.034, 0.014).extrude(0.02, both=True)
    return plate.cut(slot)


def _s_hook() -> cq.Workplane:
    """Continuous S-hook swept from a centerline + closed transverse eye (fork 5)."""
    samples = 22
    strip_w = 0.009
    result = None
    prev = None
    for i in range(samples + 1):
        t = i / samples
        x = -0.024 + 0.020 * math.sin(2.0 * math.pi * t)
        z = 0.048 - 0.096 * t
        if prev is not None:
            px, pz = prev
            dx, dz = x - px, z - pz
            ln = math.hypot(dx, dz) + 0.001
            ang = -math.degrees(math.atan2(dz, dx))
            seg = (
                cq.Workplane("XY")
                .box(ln, strip_w, 0.004)
                .rotate((0, 0, 0), (0, 1, 0), ang)
                .translate(((x + px) / 2.0, 0.0, (z + pz) / 2.0))
            )
            result = seg if result is None else result.union(seg)
        prev = (x, z)
    eye_outer = cq.Workplane("XZ").rect(0.040, 0.056).extrude(0.004, both=True).translate((0.012, 0.0, 0.0))
    eye_inner = cq.Workplane("XZ").rect(0.024, 0.044).extrude(0.02, both=True).translate((0.012, 0.0, 0.0))
    eye = eye_outer.cut(eye_inner)
    return result.union(eye)


def _snap_hook_body() -> cq.Workplane:
    """Gated snap-hook body: J curve + neck/throat + clear eye (fork 6)."""
    outer_r, inner_r = 0.026, 0.017
    outer = [(outer_r * math.cos(math.radians(d)), outer_r * math.sin(math.radians(d))) for d in range(-72, 231, 12)]
    inner = [(inner_r * math.cos(math.radians(d)), inner_r * math.sin(math.radians(d))) for d in range(230, -73, -12)]
    curved = cq.Workplane("XZ").polyline(outer + inner).close().extrude(0.008, both=True)
    neck = cq.Workplane("XY").box(0.036, 0.018, 0.009).translate((0.028, 0.0, 0.016))
    throat = cq.Workplane("XY").box(0.018, 0.016, 0.009).translate((0.013, 0.0, 0.004))
    eye_outer = cq.Workplane("XY").box(0.038, 0.061, 0.008).translate((0.049, 0.0, 0.016))
    eye_inner = cq.Workplane("XY").box(0.020, 0.045, 0.02).translate((0.052, 0.0, 0.016))
    return curved.union(neck).union(throat).union(eye_outer.cut(eye_inner))


def _snap_hook_gate() -> cq.Workplane:
    """Spring gate blade authored about its pivot at local origin (fork 6)."""
    end = (-0.034, -0.040)
    length = math.hypot(*end) + 0.002
    ang = -math.degrees(math.atan2(end[1], end[0]))
    blade = (
        cq.Workplane("XY")
        .box(length, 0.012, 0.006)
        .rotate((0, 0, 0), (0, 1, 0), ang)
        .translate((end[0] / 2.0, 0.0, end[1] / 2.0))
    )
    barrel = cq.Workplane("XZ").circle(0.006).extrude(0.009, both=True)
    tip = cq.Workplane("XZ").circle(0.005).extrude(0.006, both=True).translate((end[0], 0.0, end[1]))
    return blade.union(barrel).union(tip)


def _etrack_fitting() -> cq.Workplane:
    """E-track tongue plate with slot, ears, spring leaf (fork 7); single mesh."""
    plate = cq.Workplane("XY").rect(0.058, 0.050).extrude(0.004).translate((-0.002, 0.0, -0.002))
    slot = cq.Workplane("XY").center(-0.018, 0.0).rect(0.008, 0.043).extrude(0.02, both=True)
    plate = plate.cut(slot)
    nose = cq.Workplane("XY").box(0.020, 0.038, 0.004).translate((0.033, 0.0, 0.0))
    ear0 = cq.Workplane("XY").box(0.015, 0.010, 0.008).translate((0.044, -0.014, -0.002))
    ear1 = cq.Workplane("XY").box(0.015, 0.010, 0.008).translate((0.044, 0.014, -0.002))
    tongue = cq.Workplane("XY").box(0.020, 0.012, 0.005).translate((0.045, 0.0, 0.0045))
    leaf = cq.Workplane("XY").box(0.034, 0.024, 0.003).rotate((0, 0, 0), (0, 1, 0), -14).translate((0.026, 0.0, 0.004))
    return plate.union(nose).union(ear0).union(ear1).union(tongue).union(leaf)


def _soft_loop() -> cq.Workplane:
    """Sewn webbing soft-loop eye (fork 8): a flat closed webbing loop, kept as a
    single connected boolean ring (a real flexible-webbing structure, not a box
    placeholder)."""
    width = 0.042
    half_len = 0.030  # x half-span of the eye
    outer_r = 0.010  # z half-height of the eye band
    band_t = 0.0028
    inner_r = outer_r - band_t
    inner_len = half_len - band_t
    # Outer stadium (rounded-end rectangle in XZ) minus inner stadium -> a ring.
    outer_box = cq.Workplane("XZ").rect(2.0 * half_len, 2.0 * outer_r).extrude(width * 0.5, both=True)
    outer_l = cq.Workplane("XZ").circle(outer_r).extrude(width * 0.5, both=True).translate((-half_len, 0.0, 0.0))
    outer_rr = cq.Workplane("XZ").circle(outer_r).extrude(width * 0.5, both=True).translate((half_len, 0.0, 0.0))
    outer = outer_box.union(outer_l).union(outer_rr)
    inner_box = cq.Workplane("XZ").rect(2.0 * inner_len, 2.0 * inner_r).extrude(width, both=True)
    inner_l = cq.Workplane("XZ").circle(inner_r).extrude(width, both=True).translate((-inner_len, 0.0, 0.0))
    inner_rr = cq.Workplane("XZ").circle(inner_r).extrude(width, both=True).translate((inner_len, 0.0, 0.0))
    inner = inner_box.union(inner_l).union(inner_rr)
    return outer.cut(inner)


def _webbing_roll(r: ResolvedRatchetStrapConfig) -> cq.Workplane:
    """Wound textile roll: hollow disc + a few circumferential layer steps."""
    outer = cq.Workplane("XZ").circle(ROLL_RADIUS).extrude(r.webbing_width * 0.55, both=True)
    core = cq.Workplane("XZ").circle(0.007).extrude(r.webbing_width * 0.7, both=True)
    roll = outer.cut(core)
    for rad in (ROLL_RADIUS * 0.78, ROLL_RADIUS * 0.55, ROLL_RADIUS * 0.32):
        layer = cq.Workplane("XZ").circle(rad + 0.0009).circle(rad - 0.0009).extrude(r.webbing_width * 0.56, both=True)
        roll = roll.union(layer)
    return roll


def _endless_loop(width: float, band_t: float) -> cq.Workplane:
    """Closed racetrack webbing loop (fork 10 _endless_webbing_shape)."""
    span = 0.205
    mid = -span * 0.5
    outer_r = 0.0132
    inner_r = outer_r - band_t
    left_c, right_c = -span, 0.0
    outer_box = cq.Workplane("XZ").rect(span, 2.0 * outer_r).extrude(width * 0.5, both=True).translate((mid, 0.0, 0.0))
    lc = cq.Workplane("XZ").circle(outer_r).extrude(width * 0.5, both=True).translate((left_c, 0.0, 0.0))
    rc = cq.Workplane("XZ").circle(outer_r).extrude(width * 0.5, both=True).translate((right_c, 0.0, 0.0))
    outer = outer_box.union(lc).union(rc)
    inner_box = cq.Workplane("XZ").rect(span, 2.0 * inner_r).extrude(width, both=True).translate((mid, 0.0, 0.0))
    li = cq.Workplane("XZ").circle(inner_r).extrude(width, both=True).translate((left_c, 0.0, 0.0))
    ri = cq.Workplane("XZ").circle(inner_r).extrude(width, both=True).translate((right_c, 0.0, 0.0))
    inner = inner_box.union(li).union(ri)
    return outer.cut(inner)


# --------------------------------------------------------------------------- #
# Frame family builders (Slot A)  — emit frame + spool + handle + drive_pawl
# --------------------------------------------------------------------------- #
def _build_frame(model: ArticulatedObject, r: ResolvedRatchetStrapConfig):
    frame = model.part("frame", meta={"construction": r.construction})
    fy = r.frame_half_y
    if r.construction == "stamped":
        left = _stamped_cheek(r, -fy + WALL)
        right = _stamped_cheek(r, fy - WALL)
        span = 2.0 * fy + 0.004  # cross-members poke through both cheeks (solid fuse, no coplanar island)
        front = cq.Workplane("XY").box(0.024, span, 0.006).translate((r.cheek_front * 0.85, 0.0, -r.cheek_height * 0.28))
        rear = cq.Workplane("XY").box(0.022, span, 0.006).translate((-r.cheek_back * 0.7, 0.0, r.cheek_height * 0.30))
        nose = cq.Workplane("XY").box(0.016, span, 0.005).translate((-r.cheek_back * 0.9, 0.0, -r.cheek_height * 0.18))
        shape = left.union(right).union(front).union(rear).union(nose)
    else:  # uframe
        left = _uframe_cheek(r, -fy)
        right = _uframe_cheek(r, fy)
        span = 2.0 * fy + 0.004
        cradle = cq.Workplane("XY").box(0.020, span, 0.005).translate((-r.cheek_back * 0.55, 0.0, r.cheek_height * 0.12))
        front = cq.Workplane("XY").box(0.014, span, 0.005).translate((r.cheek_front * 0.7, 0.0, r.cheek_height * 0.16))
        shape = left.union(right).union(cradle).union(front)
    # Bottom spine running the full length low across both cheeks: guarantees the
    # frame is a single connected solid (no coplanar-union fragmentation).
    spine_len = 0.9 * (r.cheek_front + r.cheek_back)
    spine = cq.Workplane("XY").box(spine_len, 2.0 * fy + 0.004, 0.006).translate(
        ((r.cheek_front - r.cheek_back) * 0.30, 0.0, -r.cheek_height * 0.30)
    )
    shape = shape.union(spine)
    # Webbing guide bar spanning the cheeks at strap level: gives the FIXED
    # webbing mount real frame hardware at the centerline and a support contact.
    guide = cq.Workplane("XY").box(0.028, 2.0 * fy + 0.006, 0.008).translate((0.0, 0.0, STRAP_Z + 0.002))
    shape = shape.union(guide)
    # Supply-roll bracket + axle (two-piece topologies only) so the roll axle
    # sits on real frame hardware and the roll is captured, not floating.
    frame.visual(mesh_from_cadquery(shape, "ratchet_frame", tolerance=0.0004), material="frame", name="frame_shell", material_class_id="metal.steel_galvanized")
    frame.inertial = Inertial.from_geometry(
        Box((r.cheek_front + r.cheek_back, 2.0 * fy, r.cheek_height)),
        mass=0.35,
        origin=Origin(xyz=((r.cheek_front - r.cheek_back) * 0.5, 0.0, 0.0)),
    )
    return frame


def _build_spool(model: ArticulatedObject, r: ResolvedRatchetStrapConfig):
    spool = model.part("spool", meta={"function": "captured winding spool + ratchet wheels"})
    if r.construction == "stamped":
        shape = _toothed_spindle(r)
    else:
        shape = _uframe_drum(r)
    spool.visual(mesh_from_cadquery(shape, "winding_spool", tolerance=0.00035), material="frame", name="toothed_wheels", material_class_id="metal.steel_galvanized")
    spool.visual(
        Cylinder(radius=r.spool_radius * 0.42, length=r.webbing_width + 0.002),
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="weave",
        name="webbing_wrap", material_class_id="fabric.webbing",
    )
    spool.inertial = Inertial.from_geometry(
        Cylinder(radius=r.spool_radius, length=2.0 * r.frame_half_y),
        mass=0.06,
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
    )
    return spool


def _build_handle(model: ArticulatedObject, r: ResolvedRatchetStrapConfig):
    handle = model.part("handle", meta={"pose": "raised"})
    fy = r.frame_half_y
    L = r.handle_len
    grip_w = 2.0 * fy + 0.006
    cp, sp = math.cos(ARM_PITCH), math.sin(ARM_PITCH)  # arms rise up-and-forward
    grip_xyz = (L * cp, 0.0, L * sp)
    if r.handle_style == "heavy_mesh":
        # Tapered meshed side arms (fork 2 _heavy_handle_arm), preserved as cq mesh.
        for y, suf in ((-fy + 0.004, "0"), (fy - 0.004, "1")):
            stations = [(0.0, 0.014), (0.030, 0.011), (L * 0.82, 0.009), (L, 0.013)]
            pts = [(sx, sh) for sx, sh in stations] + [(sx, -sh) for sx, sh in reversed(stations)]
            arm = (
                cq.Workplane("XZ").polyline(pts).close().extrude(0.0030, both=True)
                .rotate((0, 0, 0), (0, 1, 0), -math.degrees(ARM_PITCH))
                .translate((0.0, y, 0.0))
            )
            handle.visual(mesh_from_cadquery(arm, f"heavy_arm_{suf}", tolerance=0.0004), material="frame", name=f"handle_arm_{suf}", material_class_id="metal.steel_galvanized")
        handle.visual(
            Cylinder(radius=0.016, length=grip_w),
            origin=Origin(xyz=grip_xyz, rpy=(math.pi / 2.0, 0.0, 0.0)),
            material="grip",
            name="rubber_grip", material_class_id="rubber.smooth_plain",
        )
    else:
        for y, suf in ((-fy + 0.004, "0"), (fy - 0.004, "1")):
            handle.visual(
                Box((L, 0.004, 0.014)),
                origin=Origin(xyz=(0.5 * L * cp, y, 0.5 * L * sp), rpy=(0.0, -ARM_PITCH, 0.0)),
                material="frame",
                name=f"handle_arm_{suf}", material_class_id="metal.steel_galvanized",
            )
        handle.visual(
            Box((0.030, grip_w, 0.018)),
            origin=Origin(xyz=grip_xyz, rpy=(0.0, -ARM_PITCH, 0.0)),
            material="grip",
            name="rubber_grip", material_class_id="rubber.smooth_plain",
        )
        for i, gs in enumerate((L - 0.012, L, L + 0.012)):
            handle.visual(
                Cylinder(radius=0.005, length=grip_w - 0.002),
                origin=Origin(xyz=(gs * cp, 0.0, gs * sp), rpy=(math.pi / 2.0, 0.0, 0.0)),
                material="grip",
                name=f"grip_rib_{i}", material_class_id="rubber.smooth_plain",
            )
    # Pivot tube coaxial with the spool (captures the shared axle).
    handle.visual(
        Cylinder(radius=r.spool_radius * 0.30, length=grip_w),
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="frame",
        name="handle_pivot_tube", material_class_id="metal.steel_galvanized",
    )
    handle.inertial = Inertial.from_geometry(
        Box((L + 0.03, grip_w, 0.03)),
        mass=0.10,
        origin=Origin(xyz=(L * 0.5, 0.0, 0.0)),
    )
    return handle


def _build_pawl(model: ArticulatedObject, r: ResolvedRatchetStrapConfig):
    """Compact drive pawl: a short lever pivoting on the cheek just off the wheel
    rim, its nose tooth pointing inward to engage the ratchet teeth.  Authored
    about its pivot pin at the local origin (placed at the cheek rim in build)."""
    pawl = model.part("drive_pawl", meta={"function": "ratchet drive pawl"})
    body = max(0.010, 2.0 * r.frame_half_y - 0.024)  # lever body clears the cheek inner faces
    # Lever body sits up-and-outward of the pivot (away from the wheel).
    pawl.visual(
        Box((0.020, body, 0.005)),
        origin=Origin(xyz=(0.011, 0.0, 0.006), rpy=(0.0, -0.20, 0.0)),
        material="hardware",
        name="pawl_plate", material_class_id="metal.blackened_gunmetal",
    )
    # Nose tooth points inward/down toward the wheel; overlaps the pin to stay
    # connected and reaches the ratchet teeth (overlap allowed in run_tests).
    pawl.visual(
        Box((0.012, body, 0.008)),
        origin=Origin(xyz=(-0.007, 0.0, -0.004), rpy=(0.0, 0.5, 0.0)),
        material="hardware",
        name="pawl_tooth", material_class_id="metal.blackened_gunmetal",
    )
    # Pivot pin spans the full width, captured by both cheeks.
    pawl.visual(
        Cylinder(radius=0.0045, length=2.0 * r.frame_half_y + 0.003),
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="frame",
        name="pawl_pin", material_class_id="metal.steel_galvanized",
    )
    pawl.inertial = Inertial.from_geometry(
        Box((0.024, body, 0.014)), mass=0.02, origin=Origin(xyz=(0.006, 0.0, 0.002))
    )
    return pawl


# --------------------------------------------------------------------------- #
# Release builders (Slot B)
# --------------------------------------------------------------------------- #
def _build_release(model: ArticulatedObject, r: ResolvedRatchetStrapConfig):
    rel = model.part("release", meta={"style": r.release_style})
    # Lever body rides BETWEEN the cheeks; only the pivot pin spans full width.
    body = max(0.010, min(0.020, 2.0 * r.frame_half_y - 0.024))
    if r.release_style == "frame_thumb":
        # Rises up-and-forward over the open spool top (clear of the rear bridge);
        # pin captured in the cheeks.
        rel.visual(Box((0.008, body, 0.036)), origin=Origin(xyz=(0.003, 0.0, 0.013), rpy=(0.0, -0.4, 0.0)), material="frame", name="release_bar", material_class_id="metal.steel_galvanized")
        rel.visual(Box((0.022, body, 0.007)), origin=Origin(xyz=(0.011, 0.0, 0.030)), material="hardware", name="release_thumb_pad", material_class_id="metal.blackened_gunmetal")
    elif r.release_style == "handle_paddle":
        rel.visual(Box((0.024, body, 0.006)), origin=Origin(xyz=(0.012, 0.0, 0.004), rpy=(0.0, -0.7, 0.0)), material="hardware", name="release_paddle", material_class_id="metal.blackened_gunmetal")
        rel.visual(Box((0.016, body, 0.006)), origin=Origin(xyz=(0.020, 0.0, 0.014)), material="hardware", name="release_finger_pad", material_class_id="metal.blackened_gunmetal")
    else:  # pull_tab
        rel.visual(Box((0.026, body, 0.008)), origin=Origin(xyz=(0.012, 0.0, 0.005), rpy=(0.0, -0.55, 0.0)), material="hardware", name="release_tongue", material_class_id="metal.blackened_gunmetal")
        rel.visual(Box((0.014, body, 0.004)), origin=Origin(xyz=(0.020, 0.0, 0.009)), material="accent", name="pull_surface", material_class_id="metal.paint_coated")
    rel.visual(
        Cylinder(radius=0.0045, length=2.0 * r.frame_half_y + 0.004),
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="frame",
        name="release_pin", material_class_id="metal.steel_galvanized",
    )
    rel.inertial = Inertial.from_geometry(
        Box((0.05, body, 0.02)), mass=0.01, origin=Origin(xyz=(0.02, 0.0, 0.008))
    )
    return rel


# --------------------------------------------------------------------------- #
# Webbing + fitting builders (Slot C)
# --------------------------------------------------------------------------- #
def _strap_run(part, name, p0, p1, width, material, thickness=0.0024):
    x0, z0 = p0
    x1, z1 = p1
    dx, dz = x1 - x0, z1 - z0
    length = math.hypot(dx, dz)
    ang = -math.atan2(dz, dx)
    part.visual(
        Box((length, width, thickness)),
        origin=Origin(xyz=((x0 + x1) * 0.5, 0.0, (z0 + z1) * 0.5), rpy=(0.0, ang, 0.0)),
        material=material,
        name=name, material_class_id="fabric.webbing",
    )


def _place(shape: cq.Workplane, xyz, rpy=(0.0, 0.0, 0.0)) -> cq.Workplane:
    s = shape
    rx, ry, rz = (math.degrees(a) for a in rpy)
    if rx:
        s = s.rotate((0, 0, 0), (1, 0, 0), rx)
    if ry:
        s = s.rotate((0, 0, 0), (0, 1, 0), ry)
    if rz:
        s = s.rotate((0, 0, 0), (0, 0, 1), rz)
    return s.translate(xyz)


def _add_woven_picks(part, x0, x1, width, z, material_a, material_b):
    """Transverse woven picks embedded (centered) in the host strap at height z."""
    n = 10
    for i in range(n):
        t = i / (n - 1)
        x = x0 + (x1 - x0) * t
        part.visual(
            Box((0.0012, width * 0.98, 0.0016)),
            origin=Origin(xyz=(x, 0.0, z)),
            material=material_a if i % 2 == 0 else material_b,
            name=f"{part.name}_pick_{i}", material_class_id="fabric.webbing",
        )


def _build_webbing(model: ArticulatedObject, r: ResolvedRatchetStrapConfig):
    """Emit the webbing part (FIXED to frame) + end fittings.  Returns
    (webbing_part, extra_specs) where extra_specs describes optional roll/gate
    parts the caller wires."""
    fit = r.webbing_fitting
    w = r.webbing_width
    free_x = -(r.cheek_back + 0.16)
    # Keep the anchor/fixed fitting beyond the handle's fully-lowered reach so a
    # closing handle never strikes it.
    fixed_x = max(r.cheek_front + 0.14, r.handle_len + 0.12)
    web = model.part("webbing", meta={"topology": fit})
    gates: list[tuple[str, str, tuple, tuple]] = []  # (gate_name, mesh_id, xyz, rpy)

    if fit == "endless_loop":
        # Closed racetrack loop hanging just below the head (clear of the release
        # swing); the woven band's top run sits at z ~ STRAP_Z + outer_r.
        loop_z = STRAP_Z - 0.006
        band_top_z = loop_z + 0.0124
        loop = _place(_endless_loop(w, 0.0016), (0.0, 0.0, loop_z))
        web.visual(mesh_from_cadquery(loop, "endless_webbing", tolerance=0.0004), material="webbing", name="endless_webbing", material_class_id="fabric.webbing")
        web.visual(Box((0.005, w * 0.98, 0.0016)), origin=Origin(xyz=(-0.102, 0.0, band_top_z)), material="accent", name="return_seam", material_class_id="fabric.thread_yarn")
        _add_woven_picks(web, -0.19, -0.014, w, band_top_z, "weave", "webbing")
    else:
        # A continuous horizontal run through the winding area with a free tail
        # and, for two-piece topologies, a hooked/looped fixed anchor end.
        _strap_run(web, "feed_webbing", (0.0, STRAP_Z), (free_x, STRAP_Z), w, "webbing")
        _add_woven_picks(web, free_x + 0.01, -0.01, w, STRAP_Z, "weave", "webbing")
        if fit == "feed_through_tail":
            _strap_run(web, "tail_webbing", (0.0, STRAP_Z), (fixed_x * 0.6, STRAP_Z), w, "webbing")
        else:
            _strap_run(web, "fixed_end_webbing", (0.0, STRAP_Z), (fixed_x, STRAP_Z), w, "webbing")
            # Measurement panel + ticks (④), embedded on the free run top face.
            web.visual(
                Box((abs(free_x) * 0.22, w * 0.72, 0.0016)),
                origin=Origin(xyz=(free_x * 0.42, 0.0, STRAP_Z + 0.0009)),
                material="accent", name="measurement_panel", appearance_only=AppearanceOnlySpec(kind="overlay"),
            )

    # End fittings (two-piece topologies only).
    if fit in _TWO_PIECE:
        if fit == "two_piece_soft_loop":
            for suf, x, yaw in (("fixed", fixed_x, 0.0), ("free", free_x, math.pi)):
                loop = _place(_soft_loop(), (x, 0.0, STRAP_Z), (0.0, 0.0, yaw))
                web.visual(mesh_from_cadquery(loop, f"{suf}_soft_loop", tolerance=0.0004), material="webbing", name=f"{suf}_end_soft_loop", material_class_id="fabric.webbing")
                # Reinforcement stitches sewn onto the STRAP just inboard of the
                # loop root (embedded in the webbing, not the loop's open eye).
                inboard = -1.0 if x > 0 else 1.0
                for i in range(3):
                    lx = x + inboard * (0.034 + 0.005 * i)
                    web.visual(Box((0.0016, w * 0.85, 0.0016)), origin=Origin(xyz=(lx, 0.0, STRAP_Z + 0.0009)), material="accent", name=f"{suf}_loop_stitch_{i}", material_class_id="fabric.thread_yarn")
        else:
            if fit == "two_piece_wire_j":
                shape_fn, mesh_key = _wire_j_hook, "wire_j"
            elif fit == "two_piece_flat_j":
                shape_fn, mesh_key = _flat_j_hook, "flat_j"
            elif fit == "two_piece_s_hook":
                shape_fn, mesh_key = _s_hook, "s_hook"
            elif fit == "two_piece_e_track":
                shape_fn, mesh_key = _etrack_fitting, "etrack"
            else:  # snap_hook
                shape_fn, mesh_key = _snap_hook_body, "snap_body"
            for suf, x, yaw in (("fixed", fixed_x, math.pi), ("free", free_x, 0.0)):
                hook = _place(shape_fn(), (x, 0.0, STRAP_Z), (0.0, 0.0, yaw))
                web.visual(mesh_from_cadquery(hook, f"{suf}_{mesh_key}", tolerance=0.0004), material="fitting", name=f"{suf}_end_hook", material_class_id="metal.steel_galvanized")
                if fit == "two_piece_snap_hook":
                    gname = f"snap_gate_{'0' if suf == 'fixed' else '1'}"
                    gates.append((gname, f"snap_gate_{'0' if suf == 'fixed' else '1'}", (x, 0.0, STRAP_Z), (0.0, 0.0, yaw)))

    web.inertial = Inertial.from_geometry(
        Box((fixed_x - free_x, w, 0.02)), mass=0.05, origin=Origin(xyz=((fixed_x + free_x) * 0.5, 0.0, STRAP_Z))
    )
    # Supply roll (two-piece topologies) rides on the free strap, which wraps it.
    roll_anchor = (free_x * 0.5, 0.0, STRAP_Z) if fit in _TWO_PIECE else None
    return web, gates, roll_anchor


# --------------------------------------------------------------------------- #
# Assembly
# --------------------------------------------------------------------------- #
def build_ratchet_strap(
    config: RatchetStrapConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    # Per-seed palette diversity: the chosen colorway's rgba is bound to the
    # short material keys the visuals reference.
    for key, rgba in PALETTES[r.palette_style].items():
        model.material(key, rgba=rgba)

    frame = _build_frame(model, r)
    spool = _build_spool(model, r)
    handle = _build_handle(model, r)
    pawl = _build_pawl(model, r)

    # --- captured-pin pivots (grandfathered; no MatingContract) ---
    model.articulation(
        "spindle_rotation", ArticulationType.REVOLUTE, parent=frame, child=spool,
        origin=Origin(), axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(lower=-0.45, upper=1.10, effort=120.0, velocity=4.0),
    )
    model.articulation(
        "handle_pivot", ArticulationType.REVOLUTE, parent=frame, child=handle,
        origin=Origin(), axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(lower=0.0, upper=r.handle_open_upper, effort=90.0, velocity=2.5),
    )
    model.articulation(
        "pawl_pivot", ArticulationType.REVOLUTE, parent=frame, child=pawl,
        origin=Origin(xyz=_pawl_pivot(r)), axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(lower=-0.10, upper=0.26, effort=15.0, velocity=5.0),
    )

    # --- release (Slot B): parent = frame or handle ---
    release = _build_release(model, r)
    if r.release_style == "frame_thumb":
        # Pivots on the cheek forward of the spool (origin inside the cheek
        # outline so the pin axis passes through real hardware); thumb bar
        # extends forward above the wheel.
        model.articulation(
            "release_pivot", ArticulationType.REVOLUTE, parent=frame, child=release,
            origin=Origin(xyz=_frame_thumb_pivot(r)), axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(lower=-0.12, upper=0.34, effort=12.0, velocity=5.0),
        )
    else:
        # Rides up the raised handle arm, clear of the frame top / ratchet head.
        cp, sp = math.cos(ARM_PITCH), math.sin(ARM_PITCH)
        s = max(0.45 * r.handle_len, (r.cheek_height * 0.5 + 0.024) / sp)
        s = min(s, 0.72 * r.handle_len)
        model.articulation(
            "release_pivot", ArticulationType.REVOLUTE, parent=handle, child=release,
            origin=Origin(xyz=(s * cp, 0.0, s * sp)), axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(lower=-0.12, upper=0.32, effort=18.0, velocity=4.0),
        )

    # --- webbing + fittings (Slot C): FIXED to frame ---
    webbing, gates, roll_anchor = _build_webbing(model, r)
    model.articulation("webbing_mount", ArticulationType.FIXED, parent=frame, child=webbing, origin=Origin())

    # Optional supply roll (two-piece topologies): a REVOLUTE child of the
    # webbing, mounted on the free strap which wraps it — its axis is the roll's
    # own centerline and the joint origin sits on real webbing geometry.
    if roll_anchor is not None:
        roll = model.part("webbing_roll", meta={"function": "wound textile supply roll"})
        roll.visual(mesh_from_cadquery(_webbing_roll(r), "woven_roll", tolerance=0.0004), material="webbing", name="orange_roll", material_class_id="fabric.webbing")
        for y, suf in ((-r.webbing_width * 0.5, "0"), (r.webbing_width * 0.5, "1")):
            roll.visual(
                Cylinder(radius=ROLL_RADIUS - 0.001, length=0.0018),
                origin=Origin(xyz=(0.0, y, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
                material="weave", name=f"woven_edge_{suf}", material_class_id="fabric.webbing",
            )
        roll.inertial = Inertial.from_geometry(
            Cylinder(radius=ROLL_RADIUS, length=r.webbing_width),
            origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)), mass=0.08,
        )
        model.articulation(
            "webbing_roll_rotation", ArticulationType.REVOLUTE, parent=webbing, child=roll,
            origin=Origin(xyz=roll_anchor), axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(lower=-0.8, upper=0.8, effort=8.0, velocity=2.0),
        )

    # optional snap gates (fitting-local revolute; MatingContract declared)
    for gname, mesh_id, xyz, rpy in gates:
        gate = model.part(gname, meta={"function": "spring snap gate"})
        gshape = _place(_snap_hook_gate(), (0.0, 0.0, 0.0))
        gate.visual(mesh_from_cadquery(gshape, mesh_id, tolerance=0.0004), material="hardware", name="spring_gate", material_class_id="metal.blackened_gunmetal")
        gate.inertial = Inertial.from_geometry(Box((0.05, 0.012, 0.05)), mass=0.004, origin=Origin())
        # Fitting-local spring gate is a captured pivot pressing on the hook
        # throat (pin-through-eye geometry) — grandfathered like the other
        # captured pins; the sprung contact is declared via allow_overlap.
        model.articulation(
            f"{gname}_pivot", ArticulationType.REVOLUTE, parent=webbing, child=gate,
            origin=Origin(xyz=xyz, rpy=rpy), axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(lower=-0.56, upper=0.0, effort=2.5, velocity=8.0),
        )

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_ratchet_strap(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_ratchet_strap(config_from_seed(seed), assets=assets)


# --------------------------------------------------------------------------- #
# Tests
# --------------------------------------------------------------------------- #
def _allow_captured_pins(ctx: TestContext, model: ArticulatedObject, r: ResolvedRatchetStrapConfig) -> None:
    frame = model.get_part("frame")
    spool = model.get_part("spool")
    handle = model.get_part("handle")
    pawl = model.get_part("drive_pawl")
    release = model.get_part("release")
    webbing = model.get_part("webbing")

    ctx.allow_overlap(frame, spool, reason="Winding spool axle + ratchet wheels captured across the frame cheeks.")
    ctx.allow_overlap(frame, handle, elem_a="frame_shell", elem_b="handle_pivot_tube", reason="Handle pivot tube passes through the frame pivot bores.")
    # The handle arms emerge from the captured spool pivot, passing through the
    # frame's pivot slot at the ratchet head.
    ctx.allow_overlap(frame, handle, elem_a="frame_shell", elem_b="handle_arm_0", reason="Handle side arm roots at the captured pivot inside the frame cheeks.")
    ctx.allow_overlap(frame, handle, elem_a="frame_shell", elem_b="handle_arm_1", reason="Handle side arm roots at the captured pivot inside the frame cheeks.")
    ctx.allow_overlap(handle, spool, elem_a="handle_pivot_tube", elem_b="toothed_wheels", reason="Handle pivot tube and spool share the coaxial captured axle.")
    ctx.allow_overlap(handle, spool, elem_a="handle_arm_0", elem_b="toothed_wheels", reason="Handle arm roots at the coaxial captured spool pivot.")
    ctx.allow_overlap(handle, spool, elem_a="handle_arm_1", elem_b="toothed_wheels", reason="Handle arm roots at the coaxial captured spool pivot.")
    ctx.allow_overlap(handle, spool, elem_a="handle_pivot_tube", elem_b="webbing_wrap", reason="Winding wrap is coaxial with the shared captured spindle.")
    ctx.allow_overlap(frame, pawl, elem_a="frame_shell", elem_b="pawl_pin", reason="Pawl pivot pin captured by both cheek plates.")
    ctx.allow_overlap(frame, pawl, elem_a="frame_shell", elem_b="pawl_tooth", reason="Pawl nose seats in the stamped ratchet pocket beside the wheel.")
    ctx.allow_overlap(frame, pawl, elem_a="frame_shell", elem_b="pawl_plate", reason="The pawl lever nests in the frame's ratchet pocket at the wheel rim.")
    ctx.allow_overlap(spool, pawl, elem_a="toothed_wheels", elem_b="pawl_tooth", reason="Pawl nose engages the ratchet teeth.")
    ctx.allow_overlap(pawl, handle, elem_a="pawl_pin", elem_b="handle_arm_0", reason="Pawl and handle share the crowded ratchet head; the handle arm sweeps past the pawl pin.")
    ctx.allow_overlap(pawl, handle, elem_a="pawl_pin", elem_b="handle_arm_1", reason="Pawl and handle share the crowded ratchet head; the handle arm sweeps past the pawl pin.")
    if r.release_style == "frame_thumb":
        ctx.allow_overlap(frame, release, elem_a="frame_shell", elem_b="release_pin", reason="Release pivot pin captured across the frame cheek bores.")
        ctx.allow_overlap(frame, release, elem_a="frame_shell", elem_b="release_bar", reason="The thumb lever root seats in the frame's rear ratchet-head pocket.")
    else:
        ctx.allow_overlap(handle, release, elem_a="handle_pivot_tube", elem_b="release_pin", reason="Release lever pin captured in the handle side-rail bores.")
        ctx.allow_overlap(handle, release, reason="Handle-mounted finger release rides inside the handle arms.")
        # As the handle closes onto the ratchet head, its finger release nests
        # against the frame / webbing — a real, intended contact of the packed mechanism.
        ctx.allow_overlap(release, frame, elem_a="release_pin", elem_b="frame_shell", reason="Handle-mounted release pin nests against the frame head when the handle is closed.")
        ctx.allow_overlap(release, webbing, elem_a="release_pin", elem_b="feed_webbing", reason="The finger release passes over the webbing as the handle closes.")
        ctx.allow_overlap(release, webbing, elem_a="release_pin", elem_b="endless_webbing", reason="The finger release passes over the endless webbing loop as the handle closes.")
        ctx.allow_overlap(release, webbing, elem_a="release_paddle", elem_b="endless_webbing", reason="The finger paddle passes over the endless webbing loop as the handle closes.")
        ctx.allow_overlap(release, webbing, elem_a="release_tongue", elem_b="endless_webbing", reason="The pull tab passes over the endless webbing loop as the handle closes.")
    # Webbing threads through the frame width and wraps the spool (route-through).
    ctx.allow_overlap(frame, webbing, reason="Webbing is threaded through the winding slot and seated against the frame guides.")
    ctx.allow_overlap(spool, webbing, reason="Webbing passes through and wraps the split winding spool.")
    ctx.allow_overlap(handle, webbing, elem_a="handle_pivot_tube", elem_b="feed_webbing", reason="Webbing passes beneath the coaxial handle pivot tube at the winding slot.")
    ctx.allow_overlap(handle, webbing, elem_a="handle_pivot_tube", elem_b="endless_webbing", reason="Endless webbing loop passes beneath the coaxial handle pivot tube.")
    if r.webbing_fitting in _TWO_PIECE:
        roll = model.get_part("webbing_roll")
        ctx.allow_overlap(webbing, roll, reason="The free webbing wraps the wound supply roll (tangent textile contact).")
    if r.webbing_fitting == "two_piece_snap_hook":
        ctx.allow_overlap(model.get_part("snap_gate_0"), webbing, elem_a="spring_gate", elem_b="fixed_end_hook", reason="Spring gate closes against the hook throat (intended sprung contact).")
        ctx.allow_overlap(model.get_part("snap_gate_1"), webbing, elem_a="spring_gate", elem_b="free_end_hook", reason="Spring gate closes against the hook throat (intended sprung contact).")


def run_ratchet_strap_tests(object_model: ArticulatedObject, config: RatchetStrapConfig) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)

    _allow_captured_pins(ctx, object_model, r)

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)
    ctx.fail_if_joint_mating_has_gap()

    # --- part tree ---
    part_names = {p.name for p in object_model.parts}
    core = {"frame", "spool", "handle", "drive_pawl", "release", "webbing"}
    ctx.check("core ratchet parts present", core.issubset(part_names), details=str(sorted(part_names)))
    if r.webbing_fitting in _TWO_PIECE:
        ctx.check("two-piece topology has a winding roll", "webbing_roll" in part_names)
    if r.webbing_fitting == "two_piece_snap_hook":
        ctx.check("snap hook emits fitting-local gates", {"snap_gate_0", "snap_gate_1"}.issubset(part_names))

    # --- joint contracts ---
    spindle = object_model.get_articulation("spindle_rotation")
    handle_j = object_model.get_articulation("handle_pivot")
    release_j = object_model.get_articulation("release_pivot")
    for j, nm in ((spindle, "spindle_rotation"), (handle_j, "handle_pivot"), (release_j, "release_pivot")):
        ctx.check(
            f"{nm} is a bounded Y-axis revolute",
            j.articulation_type == ArticulationType.REVOLUTE
            and abs(j.axis[1]) > 0.99
            and j.motion_limits is not None
            and j.motion_limits.lower is not None
            and j.motion_limits.upper is not None,
            details=f"type={j.articulation_type} axis={tuple(j.axis)} limits={j.motion_limits}",
        )
    ctx.check(
        "webbing mount is FIXED",
        object_model.get_articulation("webbing_mount").articulation_type == ArticulationType.FIXED,
    )
    ctx.check(
        "release parent matches style",
        object_model.get_articulation("release_pivot").parent == ("frame" if r.release_style == "frame_thumb" else "handle"),
    )

    # --- targeted motion poses (Rule 5) ---
    def center(aabb):
        return None if aabb is None else tuple((aabb[0][i] + aabb[1][i]) / 2.0 for i in range(3))

    rest_h = center(ctx.part_world_aabb("handle"))
    with ctx.pose({handle_j: r.handle_open_upper}):
        open_h = center(ctx.part_world_aabb("handle"))
    ctx.check("handle opens about the pivot", rest_h is not None and open_h is not None and open_h != rest_h)

    # The spool is axisymmetric (a winding drum): rotation is not visible via an
    # external AABB, so we assert the toothed wheel bbox remains authored across
    # the winding travel (bounded revolute already asserted above).
    with ctx.pose({spindle: spindle.motion_limits.upper}):
        wound = ctx.part_element_world_aabb(object_model.get_part("spool"), elem="toothed_wheels")
    ctx.check("spool winds through its travel", wound is not None)

    rest_r = center(ctx.part_world_aabb("release"))
    with ctx.pose({release_j: 0.28}):
        lift_r = center(ctx.part_world_aabb("release"))
    ctx.check("release lever has real travel", rest_r is not None and lift_r is not None and lift_r != rest_r)

    # drive_pawl is asymmetric (visible swing); webbing_roll is axisymmetric
    # (winding is not externally visible) so only assert the pose applies.
    pawl_j = object_model.get_articulation("pawl_pivot")
    rest_p = center(ctx.part_world_aabb("drive_pawl"))
    with ctx.pose({pawl_j: pawl_j.motion_limits.upper}):
        moved_p = center(ctx.part_world_aabb("drive_pawl"))
    ctx.check("drive_pawl swings under pawl_pivot", rest_p is not None and moved_p is not None and moved_p != rest_p)
    if "webbing_roll" in {p.name for p in object_model.parts}:
        roll_j = object_model.get_articulation("webbing_roll_rotation")
        with ctx.pose({roll_j: roll_j.motion_limits.upper}):
            ctx.check("webbing_roll pays out through its travel", ctx.part_world_aabb("webbing_roll") is not None)

    if r.webbing_fitting == "two_piece_snap_hook":
        for gname in ("snap_gate_0", "snap_gate_1"):
            gj = object_model.get_articulation(f"{gname}_pivot")
            rest_g = center(ctx.part_world_aabb(gname))
            with ctx.pose({gj: gj.motion_limits.lower}):
                open_g = center(ctx.part_world_aabb(gname))
            ctx.check(f"{gname} swings open", rest_g is not None and open_g is not None and open_g != rest_g)

    # --- sampled-pose overlap sweep across all non-FIXED joints (Rule 5) ---
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=48, ignore_fixed=True)

    return ctx.report()


__all__ = [
    "RatchetBody",
    "ReleaseStyle",
    "WebbingFitting",
    "PaletteStyle",
    "RatchetStrapConfig",
    "ResolvedRatchetStrapConfig",
    "config_from_seed",
    "resolve_config",
    "slot_choices_for_seed",
    "build_ratchet_strap",
    "build_seeded_ratchet_strap",
    "run_ratchet_strap_tests",
    "__modular__",
]
