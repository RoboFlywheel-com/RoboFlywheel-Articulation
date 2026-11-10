# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

# Modular template: stationary exercise bike.
#
# Frame: +X = front (flywheel / resistance side), -X = rear; +Z = up; +Y = left.
# A grounded static body root carries:
#   - a front resistance flywheel spinning about the side axis (Y, CONTINUOUS),
#   - a crank with two arms 180 deg apart (Y, CONTINUOUS) -> 2 pedals (Y, CONTINUOUS),
#   - a rider station: saddle post + handlebar post (PRISMATIC Z) for upright/spin
#     frames, OR a recumbent seat carriage (PRISMATIC X) + fixed side grips,
#   - N chrome stabilizer feet (FIXED), the widest ground footprint.
# The magnetic resistance form adds a 2nd real joint: a tension knob (REVOLUTE Z).
#
# Slots (structural axes):
#   A frame_type     : upright_shroud / recumbent / spin_tube_frame
#   B resistance_form: front_disc_red_ring / perforated_spoked / magnetic_shroud_knob
#   C handlebar_form : ramhorn_console / straight_bar_no_console / aero_multigrip
#                      (upright/spin only; recumbent derives side_grips + seat_carriage)
#   multiplicity     : stabilizer_foot_count in [2, 6]
#
# Sources (5-star records, all read):
#   S_parent (upright + disc + ramhorn), S_recumbent, S_spin, S_perf, S_mag,
#   S_straight, S_aero, S_feet3, S_feet4.

import math
import random
from dataclasses import dataclass, field
from typing import Literal

import cadquery as cq
from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    BoxGeometry,
    Cylinder,
    CylinderGeometry,
    Inertial,
    KnobGeometry,
    KnobGrip,
    KnobIndicator,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    TorusGeometry,
    mesh_from_cadquery,
    mesh_from_geometry,
    tube_from_spline_points,
)

__modular__ = True


# --------------------------------------------------------------------------- #
# Module enums
# --------------------------------------------------------------------------- #

FrameModule = Literal["upright_shroud", "recumbent", "spin_tube_frame"]
ResistanceModule = Literal[
    "front_disc_red_ring", "perforated_spoked", "magnetic_shroud_knob"
]
HandlebarModule = Literal[
    "ramhorn_console", "straight_bar_no_console", "aero_multigrip"
]
PaletteStyle = Literal[
    "classic_white_red",
    "matte_black_steel",
    "chrome_silver_red",
    "studio_gray_lime",
    "clinical_white_blue",
]

_FRAME_CHOICES: tuple[FrameModule, ...] = (
    "upright_shroud",
    "recumbent",
    "spin_tube_frame",
)
_RESISTANCE_CHOICES: tuple[ResistanceModule, ...] = (
    "front_disc_red_ring",
    "perforated_spoked",
    "magnetic_shroud_knob",
)
_HANDLEBAR_CHOICES: tuple[HandlebarModule, ...] = (
    "ramhorn_console",
    "straight_bar_no_console",
    "aero_multigrip",
)
_PALETTE_CHOICES: tuple[PaletteStyle, ...] = (
    "classic_white_red",
    "matte_black_steel",
    "chrome_silver_red",
    "studio_gray_lime",
    "clinical_white_blue",
)
_FOOT_COUNT_CHOICES: tuple[int, ...] = (2, 3, 4, 5, 6)
_FOOT_COUNT_WEIGHTS: tuple[float, ...] = (0.55, 0.25, 0.12, 0.05, 0.03)


# --------------------------------------------------------------------------- #
# Palette presets — REQUIRED per-seed diversity. Each preset supplies the full
# named-material set; every .visual(...) references a material NAME and the
# per-seed rgba is bound in build_exercise_bike via model.material(name, rgba).
# --------------------------------------------------------------------------- #

Rgba = tuple[float, float, float, float]


def _palette(
    *,
    body: Rgba,
    accent: Rgba,
    gray: Rgba = (0.45, 0.45, 0.48, 1.0),
    dark: Rgba = (0.20, 0.20, 0.22, 1.0),
    chrome: Rgba = (0.78, 0.80, 0.83, 1.0),
    black: Rgba = (0.10, 0.10, 0.11, 1.0),
    seat_pad: Rgba = (0.35, 0.35, 0.38, 1.0),
) -> dict[str, Rgba]:
    return {
        "body": body,
        "accent": accent,
        "gray": gray,
        "dark": dark,
        "chrome": chrome,
        "black": black,
        "seat_pad": seat_pad,
    }


PALETTE_PRESETS: dict[PaletteStyle, dict[str, Rgba]] = {
    "classic_white_red": _palette(
        body=(0.93, 0.93, 0.94, 1.0), accent=(0.82, 0.10, 0.12, 1.0)
    ),
    "matte_black_steel": _palette(
        body=(0.18, 0.19, 0.22, 1.0),
        accent=(0.55, 0.09, 0.10, 1.0),
        gray=(0.30, 0.31, 0.34, 1.0),
        dark=(0.12, 0.12, 0.14, 1.0),
        chrome=(0.60, 0.62, 0.66, 1.0),
    ),
    "chrome_silver_red": _palette(
        body=(0.78, 0.80, 0.83, 1.0),
        accent=(0.82, 0.10, 0.12, 1.0),
        gray=(0.55, 0.56, 0.60, 1.0),
        dark=(0.18, 0.18, 0.20, 1.0),
    ),
    "studio_gray_lime": _palette(
        body=(0.45, 0.45, 0.48, 1.0),
        accent=(0.55, 0.80, 0.15, 1.0),
        gray=(0.55, 0.56, 0.58, 1.0),
    ),
    "clinical_white_blue": _palette(
        body=(0.93, 0.93, 0.94, 1.0),
        accent=(0.12, 0.35, 0.78, 1.0),
        seat_pad=(0.42, 0.43, 0.46, 1.0),
    ),
}


# --------------------------------------------------------------------------- #
# Config dataclasses
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class ExerciseBikeConfig:
    frame_type: FrameModule = "upright_shroud"
    resistance_form: ResistanceModule = "front_disc_red_ring"
    handlebar_form: HandlebarModule = "ramhorn_console"
    palette_style: PaletteStyle = "classic_white_red"
    stabilizer_foot_count: int = 2
    flywheel_radius_scale: float = 1.0
    body_height_scale: float = 1.0
    foot_span_scale: float = 1.0
    crank_arm_len_scale: float = 1.0
    post_travel: float = 0.1


@dataclass(frozen=True)
class ResolvedExerciseBikeConfig:
    frame_type: FrameModule
    resistance_form: ResistanceModule
    handlebar_form: HandlebarModule  # only meaningful for upright/spin
    palette_style: PaletteStyle
    stabilizer_foot_count: int
    flywheel_radius_scale: float
    body_height_scale: float
    foot_span_scale: float
    crank_arm_len_scale: float
    post_travel: float
    is_recumbent: bool = False
    has_handlebar_post: bool = True
    has_tension_knob: bool = False
    palette: dict[str, Rgba] = field(default_factory=dict)


# --------------------------------------------------------------------------- #
# Procedural sampling
# --------------------------------------------------------------------------- #


def config_from_seed(seed: int) -> ExerciseBikeConfig:
    """Deterministic per-seed slot draw; seed 0 is not special."""
    rng = random.Random(seed)
    frame_type = rng.choice(_FRAME_CHOICES)
    resistance_form = rng.choice(_RESISTANCE_CHOICES)
    handlebar_form = rng.choice(_HANDLEBAR_CHOICES)
    palette_style = rng.choice(_PALETTE_CHOICES)
    stabilizer_foot_count = rng.choices(
        _FOOT_COUNT_CHOICES, weights=_FOOT_COUNT_WEIGHTS, k=1
    )[0]
    flywheel_radius_scale = round(rng.uniform(0.85, 1.15), 4)
    body_height_scale = round(rng.uniform(0.9, 1.12), 4)
    foot_span_scale = round(rng.uniform(0.92, 1.12), 4)
    crank_arm_len_scale = round(rng.uniform(0.9, 1.1), 4)
    post_travel = round(rng.uniform(0.06, 0.12), 4)
    return ExerciseBikeConfig(
        frame_type=frame_type,
        resistance_form=resistance_form,
        handlebar_form=handlebar_form,
        palette_style=palette_style,
        stabilizer_foot_count=stabilizer_foot_count,
        flywheel_radius_scale=flywheel_radius_scale,
        body_height_scale=body_height_scale,
        foot_span_scale=foot_span_scale,
        crank_arm_len_scale=crank_arm_len_scale,
        post_travel=post_travel,
    )


def resolve_config(config: ExerciseBikeConfig | None = None) -> ResolvedExerciseBikeConfig:
    """Validate enums, gate illegal combos, clamp/project continuous scales."""
    cfg = config or ExerciseBikeConfig()

    frame_type = cfg.frame_type or "upright_shroud"
    resistance_form = cfg.resistance_form or "front_disc_red_ring"
    handlebar_form = cfg.handlebar_form or "ramhorn_console"
    palette_style = cfg.palette_style or "classic_white_red"

    if frame_type not in _FRAME_CHOICES:
        raise ValueError(f"Unsupported frame_type: {frame_type}")
    if resistance_form not in _RESISTANCE_CHOICES:
        raise ValueError(f"Unsupported resistance_form: {resistance_form}")
    if handlebar_form not in _HANDLEBAR_CHOICES:
        raise ValueError(f"Unsupported handlebar_form: {handlebar_form}")
    if palette_style not in PALETTE_PRESETS:
        raise ValueError(f"Unsupported palette_style: {palette_style}")

    is_recumbent = frame_type == "recumbent"
    has_handlebar_post = not is_recumbent

    # Compatibility gate: magnetic_shroud_knob requires a shell to mount the
    # closed cowl against. spin_tube_frame has no shell -> fall back to the
    # perforated cast wheel (still an open-wheel identity); recumbent keeps it
    # (the beam provides a housing face). Per spec open question: spin falls
    # back rather than building a bespoke bracket.
    has_tension_knob = resistance_form == "magnetic_shroud_knob"
    if resistance_form == "magnetic_shroud_knob" and frame_type == "spin_tube_frame":
        resistance_form = "perforated_spoked"
        has_tension_knob = False

    # Continuous scales — clamp.
    flywheel_radius_scale = max(0.85, min(float(cfg.flywheel_radius_scale), 1.15))
    body_height_scale = max(0.9, min(float(cfg.body_height_scale), 1.12))
    foot_span_scale = max(0.92, min(float(cfg.foot_span_scale), 1.12))
    crank_arm_len_scale = max(0.9, min(float(cfg.crank_arm_len_scale), 1.1))
    post_travel = max(0.06, min(float(cfg.post_travel), 0.12))

    # Recumbent locks body_height_scale (long beam posture does not grow tall).
    if is_recumbent:
        body_height_scale = 1.0

    foot_count = int(cfg.stabilizer_foot_count)
    if foot_count < 2:
        foot_count = 2
    if foot_count > 6:
        foot_count = 6

    return ResolvedExerciseBikeConfig(
        frame_type=frame_type,
        resistance_form=resistance_form,
        handlebar_form=handlebar_form,
        palette_style=palette_style,
        stabilizer_foot_count=foot_count,
        flywheel_radius_scale=flywheel_radius_scale,
        body_height_scale=body_height_scale,
        foot_span_scale=foot_span_scale,
        crank_arm_len_scale=crank_arm_len_scale,
        post_travel=post_travel,
        is_recumbent=is_recumbent,
        has_handlebar_post=has_handlebar_post,
        has_tension_knob=has_tension_knob,
        palette=dict(PALETTE_PRESETS[palette_style]),
    )


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    """Return (slot, module) picks for module_topology_diversity.

    Cockpit is derived: recumbent -> 'recumbent_station'; upright/spin -> the
    sampled handlebar_form. Includes foot_count so multiplicity contributes.
    """
    r = resolve_config(config_from_seed(seed))
    cockpit = "recumbent_station" if r.is_recumbent else r.handlebar_form
    return [
        ("frame_type", r.frame_type),
        ("resistance_form", r.resistance_form),
        ("cockpit", cockpit),
        ("foot_count", f"n{r.stabilizer_foot_count}"),
    ]


# --------------------------------------------------------------------------- #
# Shared reference coordinates (upright / spin baseline, from S_parent / S_spin)
# --------------------------------------------------------------------------- #

# Crank core (shared across all frames).
# Real crank arms are ~0.165 m (pedal orbit ~0.33 m). CRANK_ARM_Y is pushed
# outboard so the two crank arms + inboard pedal spindles sweep in Y-planes that
# clear the centred resistance cowl / flywheel (real-bike lateral offset), so the
# pedal orbit never plunges into the housing regardless of crank angle.
CRANK_ARM_LEN = 0.165
CRANK_ARM_Y = 0.155
PEDAL_Y = 0.200

# Flywheel base (radius scaled by flywheel_radius_scale).
FLYWHEEL_R_BASE = 0.165
FLYWHEEL_HALF_W = 0.022

# Upright frame layout.
UP_FLYWHEEL_X = 0.30
UP_FLYWHEEL_Z = 0.30
UP_FLYWHEEL_Y = 0.100
UP_CRANK_X = 0.10
UP_CRANK_Z = 0.250  # bottom bracket ~0.25 m (real BB height); pedal orbit clears ground with the 0.165 crank
UP_SADDLE_BASE_Z = 0.56  # saddle top ~0.75-0.87 m (real riding height)
UP_HBAR_BASE_Z = 0.52
UP_FOOT_FRONT_X = 0.40
UP_FOOT_REAR_X = -0.16
UP_FOOT_LEN = 0.46
UP_BODY_SPAN_Y = 0.40  # extruded teardrop full Y span (+/-0.085 + fillet -> ~0.36)

# Spin frame layout (tube junctions).
SP_BB = (0.08, 0.0, 0.25)  # bottom bracket raised so the 0.165 crank clears the ground
SP_ST_TOP = (-0.06, 0.0, 0.56)
SP_HT_TOP = (0.42, 0.0, 0.64)
SP_FORK_CROWN = (0.56, 0.0, 0.48)
SP_STAY_JUNC = (0.02, 0.0, 0.37)
SP_FORK_L = (0.58, -0.23, 0.035)
SP_FORK_R = (0.58, 0.23, 0.035)
SP_STAY_L = (-0.12, -0.23, 0.035)
SP_STAY_R = (-0.12, 0.23, 0.035)
SP_TUBE_R = 0.022
SP_TUBE_R_THIN = 0.018
SP_FLYWHEEL_X = 0.36
SP_FLYWHEEL_Z = 0.24  # forward flywheel axis linked to the crank by a belt
SP_FLYWHEEL_Y = 0.0  # disc centered on the spin-frame axle
SP_FOOT_SPAN = 0.56  # > fork/stay cross-bar span (+/-0.23) so feet stay widest
SP_FOOT_FRONT_X = SP_FORK_L[0]
SP_FOOT_REAR_X = SP_STAY_L[0]

# Recumbent frame layout.
RC_BEAM_FRONT_X = 0.50
RC_BEAM_REAR_X = -0.56
RC_BEAM_Z_BOT = 0.10
RC_BEAM_Z_TOP = 0.22
RC_BEAM_HALF_W = 0.046
RC_FLYWHEEL_X = 0.38
RC_FLYWHEEL_Z = 0.22
RC_FLYWHEEL_Y = 0.055
RC_CRANK_X = 0.14
RC_CRANK_Z = 0.22  # nudged up so the longer 0.165 crank keeps the forward pedals off the floor
RC_SEAT_X = -0.36
RC_SEAT_RAIL_Z_TOP = RC_BEAM_Z_TOP + 0.010
RC_GRIP_X = -0.28
RC_GRIP_Z = RC_BEAM_Z_TOP
RC_FOOT_FRONT_X = 0.36
RC_FOOT_REAR_X = -0.44
RC_FOOT_LEN = 0.48
RC_BODY_SPAN_Y = RC_BEAM_HALF_W * 2.0


# --------------------------------------------------------------------------- #
# Geometry helpers
# --------------------------------------------------------------------------- #


def _loft(sections) -> cq.Workplane:
    wp = cq.Workplane("XZ")
    prev = 0.0
    for i, s in enumerate(sections):
        y = s[1]
        off = y if i == 0 else y - prev
        if i > 0 or abs(off) > 1e-12:
            wp = wp.workplane(offset=off)
        if s[0] == "circle":
            wp = wp.circle(s[2])
        else:
            wp = wp.rect(s[2], s[3])
        prev = y
    return wp.loft(ruled=False)


def _upright_body_solid(hscale: float) -> cq.Workplane:
    """Molded teardrop shroud (S_parent L77-L110); Z heights scaled by hscale."""
    profile_pts = [
        (0.46, 0.22),
        (0.47, 0.34),
        (0.42, 0.45),
        (0.30, 0.49),
        (0.10, 0.50),
        (-0.05, 0.50),
        (-0.14, 0.46),
        (-0.16, 0.34),
        (-0.12, 0.22),
        (-0.04, 0.14),
        (0.10, 0.11),
        (0.26, 0.12),
        (0.40, 0.15),
    ]
    pts = [(x, z * hscale) for x, z in profile_pts]
    wire = cq.Workplane("XZ").moveTo(*pts[0])
    for p in pts[1:]:
        wire = wire.lineTo(*p)
    base = wire.close().extrude(0.085, both=True)
    try:
        base = base.edges("|Y").fillet(0.03)
    except Exception:
        pass
    return base


def _upright_body_bottom_z(x: float, hscale: float) -> float:
    pts = [
        (0.40, 0.15), (0.26, 0.12), (0.10, 0.11),
        (-0.04, 0.14), (-0.12, 0.22), (-0.16, 0.26),
    ]
    if x >= pts[0][0]:
        z = pts[0][1]
    elif x <= pts[-1][0]:
        z = pts[-1][1]
    else:
        z = 0.14
        for j in range(len(pts) - 1):
            x0, z0 = pts[j]
            x1, z1 = pts[j + 1]
            if x1 <= x <= x0:
                t = (x - x0) / (x1 - x0) if abs(x1 - x0) > 1e-9 else 0.0
                z = z0 + t * (z1 - z0)
                break
    return z * hscale


def _beam_body_solid() -> cq.Workplane:
    """Long low horizontal beam (S_recumbent L66-L97)."""
    bf, bz_bot, bz_top, br = RC_BEAM_FRONT_X, RC_BEAM_Z_BOT, RC_BEAM_Z_TOP, RC_BEAM_REAR_X
    profile_pts = [
        (bf, bz_bot + 0.02),
        (bf + 0.01, bz_bot + 0.06),
        (bf - 0.02, bz_top + 0.02),
        (bf - 0.10, bz_top + 0.01),
        (0.20, bz_top),
        (0.0, bz_top),
        (-0.20, bz_top),
        (-0.40, bz_top + 0.005),
        (br + 0.06, bz_top + 0.01),
        (br + 0.02, bz_top),
        (br, bz_top - 0.02),
        (br, bz_bot + 0.02),
        (br + 0.04, bz_bot),
        (-0.40, bz_bot - 0.005),
        (-0.20, bz_bot),
        (0.0, bz_bot),
        (0.20, bz_bot),
        (bf - 0.10, bz_bot),
        (bf - 0.02, bz_bot + 0.01),
    ]
    wire = cq.Workplane("XZ").moveTo(*profile_pts[0])
    for p in profile_pts[1:]:
        wire = wire.lineTo(*p)
    base = wire.close().extrude(RC_BEAM_HALF_W, both=True)
    try:
        base = base.edges("|Y").fillet(0.014)
    except Exception:
        pass
    return base


def _tube(p1, p2, radius=SP_TUBE_R):
    pts = []
    for i in range(5):
        t = i / 4.0
        pts.append(tuple(a + t * (b - a) for a, b in zip(p1, p2)))
    return tube_from_spline_points(
        pts, radius=radius, samples_per_segment=4, radial_segments=16, cap_ends=True
    )


def _spin_frame_mesh():
    geo = _tube(SP_BB, SP_ST_TOP)
    geo = geo.merge(_tube(SP_ST_TOP, SP_HT_TOP))
    geo = geo.merge(_tube(SP_FORK_CROWN, SP_HT_TOP))
    geo = geo.merge(_tube(SP_FORK_CROWN, SP_FORK_L, SP_TUBE_R_THIN))
    geo = geo.merge(_tube(SP_FORK_CROWN, SP_FORK_R, SP_TUBE_R_THIN))
    geo = geo.merge(_tube(SP_STAY_JUNC, SP_STAY_L, SP_TUBE_R_THIN))
    geo = geo.merge(_tube(SP_STAY_JUNC, SP_STAY_R, SP_TUBE_R_THIN))
    # Front and rear ground cross-stabilizer bars (along Y at z=0.035) tying the
    # fork-leg ends and stay-leg ends together, plus a central skid beam along X
    # at y=0 joining them. These give the frame continuous body geometry at y=0
    # over the full foot X range so the stabilizer feet always mount and connect.
    geo = geo.merge(_tube(SP_FORK_L, SP_FORK_R, SP_TUBE_R_THIN))
    geo = geo.merge(_tube(SP_STAY_L, SP_STAY_R, SP_TUBE_R_THIN))
    skid = BoxGeometry(
        (SP_FORK_L[0] - SP_STAY_L[0] + 0.06, 0.040, 0.030)
    ).translate((SP_FORK_L[0] + SP_STAY_L[0]) / 2.0, 0.0, SP_FORK_L[2])
    geo = geo.merge(skid)
    bb_shell = CylinderGeometry(0.032, 0.070).rotate_x(math.pi / 2.0)
    bb_shell.translate(*SP_BB)
    geo = geo.merge(bb_shell)
    crown_collar = CylinderGeometry(0.028, 0.040).rotate_x(math.pi / 2.0)
    crown_collar.translate(*SP_FORK_CROWN)
    geo = geo.merge(crown_collar)
    seat_collar = CylinderGeometry(0.028, 0.030).rotate_x(math.pi / 2.0)
    seat_collar.translate(*SP_ST_TOP)
    geo = geo.merge(seat_collar)
    axle_len = max(0.22, abs(SP_FLYWHEEL_Y) * 2.0 + 0.08)
    axle = CylinderGeometry(0.012, axle_len).rotate_x(math.pi / 2.0)
    axle.translate(SP_FLYWHEEL_X, 0.0, SP_FLYWHEEL_Z)
    geo = geo.merge(axle)
    return mesh_from_geometry(geo, "frame")


# ---- flywheel sub-meshes (shared, radius-scaled) ----


def _disc_mesh(fr: float):
    disc = CylinderGeometry(fr * 0.86, FLYWHEEL_HALF_W * 2.0 * 0.7).rotate_x(math.pi / 2.0)
    hub = CylinderGeometry(0.040, FLYWHEEL_HALF_W * 2.0 * 1.1).rotate_x(math.pi / 2.0)
    disc.merge(hub)
    return mesh_from_geometry(disc, "flywheel_disc")


def _ring_mesh(major_r: float):
    ring = TorusGeometry(
        major_r, 0.012, radial_segments=18, tubular_segments=64
    ).rotate_x(math.pi / 2.0)
    return mesh_from_geometry(ring, "flywheel_red_ring")


def _marker_mesh(marker_r: float):
    marker = CylinderGeometry(0.012, FLYWHEEL_HALF_W * 2.0 * 1.2).rotate_x(math.pi / 2.0)
    marker.translate(marker_r, 0.0, 0.0)
    return mesh_from_geometry(marker, "flywheel_marker")


# ---- perforated cast-wheel sub-meshes ----

N_SPOKES = 8


def _rim_mesh(fr: float):
    rim_outer = fr * 0.98
    rim_inner = fr * 0.84
    rim = (
        cq.Workplane("XZ")
        .circle(rim_outer)
        .circle(rim_inner)
        .extrude(FLYWHEEL_HALF_W, both=True)
    )
    return mesh_from_cadquery(rim, "flywheel_rim")


def _hub_mesh():
    hub = CylinderGeometry(0.034, FLYWHEEL_HALF_W * 2.2).rotate_x(math.pi / 2.0)
    return mesh_from_geometry(hub, "flywheel_hub")


def _spoke_arm_geometry(fr: float):
    rim_inner = fr * 0.84
    hub_r = 0.034
    spoke_len = rim_inner - hub_r
    mid_r = hub_r + spoke_len / 2.0
    geo = BoxGeometry((spoke_len, FLYWHEEL_HALF_W * 1.6, 0.024))
    geo.translate(mid_r, 0.0, 0.0)
    return geo


def _shroud_pod_mesh(hx: float, hz: float, wx: float, wy: float, wz: float):
    pod = cq.Workplane("XY").box(wx, wy, wz, centered=(True, True, True))
    try:
        pod = pod.edges("|Z").fillet(0.055)
    except Exception:
        pass
    try:
        pod = pod.edges("#Z").fillet(0.035)
    except Exception:
        pass
    pod = pod.translate((hx, 0.0, hz))
    return mesh_from_cadquery(pod, "resistance_housing")


def _foot_tube_mesh(length_y: float):
    tube = CylinderGeometry(0.018, length_y).rotate_x(math.pi / 2.0)
    return mesh_from_geometry(tube, "stabilizer_tube")


def _spin_belt_drive_mesh():
    """Side-mounted belt linking the crank pulley to the forward flywheel."""
    belt_y = -0.075
    crank_r = 0.052
    fly_r = 0.128
    cx, _, cz = SP_BB
    fx, _, fz = SP_FLYWHEEL_X, SP_FLYWHEEL_Y, SP_FLYWHEEL_Z

    geo = _tube((cx, belt_y, cz + crank_r), (fx, belt_y, fz + fly_r), radius=0.006)
    geo = geo.merge(_tube((cx, belt_y, cz - crank_r), (fx, belt_y, fz - fly_r), radius=0.006))

    crank_pulley = CylinderGeometry(crank_r, 0.014).rotate_x(math.pi / 2.0)
    crank_pulley.translate(cx, belt_y, cz)
    geo = geo.merge(crank_pulley)

    fly_pulley = CylinderGeometry(fly_r, 0.014).rotate_x(math.pi / 2.0)
    fly_pulley.translate(fx, belt_y, fz)
    geo = geo.merge(fly_pulley)
    return mesh_from_geometry(geo, "belt_drive")


def _spin_flywheel_axle_support_mesh():
    """Static bearing yokes that carry both ends of the flywheel axle."""
    fx, fz = SP_FLYWHEEL_X, SP_FLYWHEEL_Z
    bearing_y = 0.105
    base_z = SP_FORK_L[2] + 0.018
    geo = None
    for side in (-1.0, 1.0):
        y = side * bearing_y
        block = BoxGeometry((0.050, 0.028, 0.070)).translate(fx, y, fz)
        foot_front = (fx + 0.085, side * 0.018, base_z)
        foot_rear = (fx - 0.085, side * 0.018, base_z)
        leg_front = _tube((fx, y, fz - 0.020), foot_front, radius=0.010)
        leg_rear = _tube((fx, y, fz - 0.020), foot_rear, radius=0.010)
        front_mount = BoxGeometry((0.050, 0.030, 0.026)).translate(*foot_front)
        rear_mount = BoxGeometry((0.050, 0.030, 0.026)).translate(*foot_rear)
        geo = block if geo is None else geo.merge(block)
        geo = geo.merge(leg_front)
        geo = geo.merge(leg_rear)
        geo = geo.merge(front_mount)
        geo = geo.merge(rear_mount)
    return mesh_from_geometry(geo, "flywheel_axle_support")


# ---- handlebar sub-meshes ----


def _ramhorn_mesh():
    pts = [
        (0.0, -0.34, 0.02),
        (0.04, -0.28, -0.02),
        (0.05, -0.16, -0.05),
        (0.02, -0.06, -0.03),
        (0.0, 0.0, 0.0),
        (0.02, 0.06, -0.03),
        (0.05, 0.16, -0.05),
        (0.04, 0.28, -0.02),
        (0.0, 0.34, 0.02),
    ]
    bar = tube_from_spline_points(pts, radius=0.016, samples_per_segment=14, radial_segments=14)
    return mesh_from_geometry(bar, "handlebar_tube")


def _straight_bar_mesh():
    bar = CylinderGeometry(0.014, 0.50).rotate_x(math.pi / 2.0)
    return mesh_from_geometry(bar, "handlebar_bar")


def _grip_mesh():
    grip = CylinderGeometry(0.019, 0.10).rotate_x(math.pi / 2.0)
    return mesh_from_geometry(grip, "handlebar_grip")


def _crossbar_mesh():
    bar = CylinderGeometry(0.014, 0.44).rotate_x(math.pi / 2.0)
    return mesh_from_geometry(bar, "crossbar")


def _side_grip_sleeve_mesh():
    grip = CylinderGeometry(0.020, 0.10).rotate_x(math.pi / 2.0)
    return mesh_from_geometry(grip, "side_grip")


def _aero_extension_mesh():
    pts = [
        (0.0, 0.0, 0.0),
        (0.07, 0.0, 0.004),
        (0.16, 0.0, 0.007),
        (0.24, 0.0, 0.003),
        (0.28, 0.0, -0.010),
    ]
    bar = tube_from_spline_points(pts, radius=0.012, samples_per_segment=10, radial_segments=12)
    return mesh_from_geometry(bar, "aero_extension")


def _forearm_pad_mesh():
    pad = cq.Workplane("XY").box(0.070, 0.044, 0.014, centered=(True, True, True))
    try:
        pad = pad.edges("|Z").fillet(0.006)
    except Exception:
        pass
    return mesh_from_cadquery(pad, "forearm_pad")


def _saddle_mesh():
    pad = _loft(
        [
            ("rect", -0.075, 0.060, 0.045),
            ("rect", -0.030, 0.110, 0.060),
            ("rect", 0.030, 0.150, 0.060),
            ("rect", 0.075, 0.130, 0.050),
        ]
    )
    return mesh_from_cadquery(pad, "saddle_pad")


def _bucket_seat_mesh():
    wp = cq.Workplane("YZ")
    sections = [
        (0.12, 0.14, 0.014),
        (0.08, 0.15, 0.018),
        (0.04, 0.16, 0.022),
        (0.0, 0.17, 0.025),
        (-0.04, 0.17, 0.028),
        (-0.08, 0.16, 0.030),
        (-0.12, 0.15, 0.026),
    ]
    prev_x = sections[0][0]
    for i, (x, hw, hh) in enumerate(sections):
        dx = x - prev_x
        if i > 0:
            wp = wp.workplane(offset=dx)
        wp = wp.rect(2.0 * hw, 2.0 * hh)
        prev_x = x
    seat_pan = wp.loft(ruled=False)
    try:
        seat_pan = seat_pan.edges("|X").fillet(0.008)
    except Exception:
        pass
    return seat_pan


def _backrest_mesh():
    wp = cq.Workplane("XY")
    sections = [
        (0.0, 0.13, 0.018),
        (0.05, 0.12, 0.020),
        (0.10, 0.11, 0.022),
        (0.16, 0.10, 0.023),
        (0.22, 0.09, 0.022),
        (0.26, 0.085, 0.020),
    ]
    prev_z = sections[0][0]
    for i, (z, hw, hh) in enumerate(sections):
        dz = z - prev_z
        if i > 0:
            wp = wp.workplane(offset=dz)
        wp = wp.rect(2.0 * hw, 2.0 * hh)
        prev_z = z
    backrest = wp.loft(ruled=False)
    try:
        backrest = backrest.edges("|Z").fillet(0.007)
    except Exception:
        pass
    return backrest


def _recumbent_side_grip_mesh(side: float):
    pts = [
        (0.0, 0.0, 0.0),
        (0.02, side * 0.04, 0.03),
        (0.0, side * 0.07, 0.08),
        (-0.04, side * 0.08, 0.13),
        (-0.06, side * 0.08, 0.17),
    ]
    bar = tube_from_spline_points(pts, radius=0.013, samples_per_segment=12, radial_segments=12)
    return mesh_from_geometry(bar, "grip_bar")


# --------------------------------------------------------------------------- #
# Frame geometry adapter — per-frame layout for the shared core.
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class FrameLayout:
    flywheel_xyz: tuple[float, float, float]
    crank_xyz: tuple[float, float, float]
    saddle_origin: tuple[float, float, float]
    hbar_origin: tuple[float, float, float]
    foot_front_x: float
    foot_rear_x: float
    foot_len: float
    body_span_y: float
    # function (x) -> body-bottom z for foot leg tops
    body_bottom_z: object
    foot_origin_z: float  # z of the FIXED foot articulation origin (frame frame)


def _frame_layout(r: ResolvedExerciseBikeConfig) -> FrameLayout:
    h = r.body_height_scale
    if r.frame_type == "upright_shroud":
        return FrameLayout(
            flywheel_xyz=(UP_FLYWHEEL_X, UP_FLYWHEEL_Y, UP_FLYWHEEL_Z * h),
            crank_xyz=(UP_CRANK_X, 0.0, UP_CRANK_Z),
            saddle_origin=(0.06, 0.0, UP_SADDLE_BASE_Z * h),
            hbar_origin=(-0.10, 0.0, UP_HBAR_BASE_Z * h),
            foot_front_x=UP_FOOT_FRONT_X,
            foot_rear_x=UP_FOOT_REAR_X,
            foot_len=UP_FOOT_LEN,
            body_span_y=UP_BODY_SPAN_Y,
            body_bottom_z=lambda x: _upright_body_bottom_z(x, h),
            foot_origin_z=0.0,
        )
    if r.frame_type == "spin_tube_frame":
        return FrameLayout(
            # Frame mesh uses fixed SP_* constants (not h-scaled); the flywheel
            # axle the wheel mounts on is structural, so its z must match.
            flywheel_xyz=(SP_FLYWHEEL_X, SP_FLYWHEEL_Y, SP_FLYWHEEL_Z),
            crank_xyz=(SP_BB[0], 0.0, SP_BB[2]),
            # Posts insert at the fixed frame collars (seat/head tube tops), which
            # are NOT h-scaled, so the body collars stay connected to the frame.
            saddle_origin=(SP_ST_TOP[0], 0.0, SP_ST_TOP[2]),
            hbar_origin=(SP_HT_TOP[0], 0.0, SP_HT_TOP[2]),
            foot_front_x=SP_FOOT_FRONT_X,
            foot_rear_x=SP_FOOT_REAR_X,
            foot_len=SP_FOOT_SPAN,
            body_span_y=SP_FOOT_SPAN - 0.04,
            # tube frame: fork/stay legs terminate at z=0.035, where the feet mount
            body_bottom_z=lambda x: SP_FORK_L[2],
            foot_origin_z=0.035,
        )
    # recumbent
    return FrameLayout(
        flywheel_xyz=(RC_FLYWHEEL_X, RC_FLYWHEEL_Y, RC_FLYWHEEL_Z),
        crank_xyz=(RC_CRANK_X, 0.0, RC_CRANK_Z),
        saddle_origin=(RC_SEAT_X, 0.0, RC_SEAT_RAIL_Z_TOP),
        hbar_origin=(0.0, 0.0, 0.0),
        foot_front_x=RC_FOOT_FRONT_X,
        foot_rear_x=RC_FOOT_REAR_X,
        foot_len=RC_FOOT_LEN,
        body_span_y=RC_BODY_SPAN_Y,
        body_bottom_z=lambda x: RC_BEAM_Z_BOT,
        foot_origin_z=RC_BEAM_Z_BOT,
    )


# --------------------------------------------------------------------------- #
# Body root builders
# --------------------------------------------------------------------------- #


def _build_body_upright(model, r, mats, lay):
    body = model.part("body")
    body.visual(
        mesh_from_cadquery(_upright_body_solid(r.body_height_scale), "body_shroud"),
        material=mats["body"],
        name="body_shroud", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"classic_white_red", "studio_gray_lime", "clinical_white_blue"} else "metal.paint_coated"),
    )
    cx, _, cz = lay.crank_xyz
    boss = CylinderGeometry(0.030, 0.20).rotate_x(math.pi / 2.0)
    boss.translate(cx, 0.0, cz)
    body.visual(mesh_from_geometry(boss, "crank_boss"), material=mats["dark"], name="crank_boss", material_class_id="metal.blackened_gunmetal")
    body.inertial = Inertial.from_geometry(
        Box((0.62, 0.18, 0.40)), mass=14.0,
        origin=Origin(xyz=(0.16, 0.0, 0.30 * r.body_height_scale)),
    )
    return body


def _build_body_spin(model, r, mats, lay):
    body = model.part("body")
    body.visual(_spin_frame_mesh(), material=mats["body"], name="frame", material_class_id=("metal.paint_coated" if r.palette_style in {"classic_white_red", "matte_black_steel", "studio_gray_lime", "clinical_white_blue"} else "metal.chrome_polished"))
    body.visual(_spin_belt_drive_mesh(), material=mats["black"], name="belt_drive", material_class_id="rubber.smooth_plain")
    body.visual(
        _spin_flywheel_axle_support_mesh(),
        material=mats["dark"],
        name="flywheel_axle_support", material_class_id="metal.blackened_gunmetal",
    )
    body.inertial = Inertial.from_geometry(
        Box((0.50, 0.46, 0.55)), mass=12.0, origin=Origin(xyz=(0.10, 0.0, 0.30)),
    )
    return body


def _build_body_recumbent(model, r, mats, lay):
    body = model.part("body")
    body.visual(mesh_from_cadquery(_beam_body_solid(), "body_beam"), material=mats["body"], name="body_beam", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"classic_white_red", "studio_gray_lime", "clinical_white_blue"} else "metal.paint_coated"))
    # Flywheel housing boss on beam front.
    fr = FLYWHEEL_R_BASE * r.flywheel_radius_scale
    fw_housing = CylinderGeometry(fr * 0.40, RC_BEAM_HALF_W * 2.2).rotate_x(math.pi / 2.0)
    fw_housing.translate(RC_FLYWHEEL_X, 0.0, RC_FLYWHEEL_Z)
    body.visual(mesh_from_geometry(fw_housing, "flywheel_housing"), material=mats["dark"], name="flywheel_housing", material_class_id="metal.blackened_gunmetal")
    # Flywheel axle stub.
    axle_len = RC_FLYWHEEL_Y - RC_BEAM_HALF_W + 0.01
    axle = CylinderGeometry(0.012, axle_len).rotate_x(math.pi / 2.0)
    axle.translate(RC_FLYWHEEL_X, RC_BEAM_HALF_W + axle_len / 2.0 - 0.01, RC_FLYWHEEL_Z)
    body.visual(mesh_from_geometry(axle, "flywheel_axle"), material=mats["chrome"], name="flywheel_axle", material_class_id="metal.chrome_polished")
    # Crank boss.
    boss = CylinderGeometry(0.026, RC_BEAM_HALF_W * 2.4).rotate_x(math.pi / 2.0)
    boss.translate(RC_CRANK_X, 0.0, RC_CRANK_Z)
    body.visual(mesh_from_geometry(boss, "crank_boss"), material=mats["dark"], name="crank_boss", material_class_id="metal.blackened_gunmetal")
    # Seat rail.
    rail = BoxGeometry((0.28, 0.044, 0.010))
    rail.translate(RC_SEAT_X + 0.02, 0.0, RC_BEAM_Z_TOP + 0.005)
    body.visual(mesh_from_geometry(rail, "seat_rail"), material=mats["dark"], name="seat_rail", material_class_id="metal.blackened_gunmetal")
    body.inertial = Inertial.from_geometry(
        Box(((RC_BEAM_FRONT_X - RC_BEAM_REAR_X), RC_BEAM_HALF_W * 2.0, RC_BEAM_Z_TOP - RC_BEAM_Z_BOT + 0.02)),
        mass=16.0,
        origin=Origin(xyz=((RC_BEAM_FRONT_X + RC_BEAM_REAR_X) / 2.0, 0.0, (RC_BEAM_Z_BOT + RC_BEAM_Z_TOP) / 2.0)),
    )
    return body


_BODY_FACTORIES = {
    "upright_shroud": _build_body_upright,
    "spin_tube_frame": _build_body_spin,
    "recumbent": _build_body_recumbent,
}


# --------------------------------------------------------------------------- #
# Stabilizer feet multiplicity
# --------------------------------------------------------------------------- #


FOOT_MIN_SPACING = 0.062  # min X gap between adjacent feet (cap dia ~0.048 + clearance)


def _foot_x_positions(n, front_x, rear_x, crank_x, sweep_clear):
    """Return n foot X positions over [rear_x, front_x] that (a) avoid the crank
    pedal-sweep band [crank_x +- sweep_clear] and (b) keep adjacent feet at least
    FOOT_MIN_SPACING apart. Feet are split between the front and rear allowed
    segments in proportion to their length; each segment then spreads its share
    evenly. This gives a real front-row / rear-row stabilizer stance instead of a
    continuous fan that would bunch up or sit under the bottom bracket."""
    lo, hi = (rear_x, front_x) if front_x >= rear_x else (front_x, rear_x)
    band_lo = crank_x - sweep_clear
    band_hi = crank_x + sweep_clear
    segs = []
    if band_lo - lo >= 0.02:
        segs.append((lo, min(band_lo, hi)))
    if hi - band_hi >= 0.02:
        segs.append((max(band_hi, lo), hi))
    if not segs:  # band swallows the span; fall back to the full span
        segs = [(lo, hi)]

    if n == 1:
        a, b = max(segs, key=lambda s: s[1] - s[0])
        return [(a + b) / 2.0]

    total = sum(b - a for a, b in segs) or 1.0
    # Per-segment capacity at the minimum spacing (so feet never collide).
    caps = [max(1, int((b - a) / FOOT_MIN_SPACING) + 1) for a, b in segs]
    # Apportion feet to segments by length, then clamp to capacity and push any
    # overflow to the other segment(s).
    counts = [max(1, round(n * (b - a) / total)) for a, b in segs]
    while sum(counts) > n:
        counts[counts.index(max(counts))] -= 1
    while sum(counts) < n:
        counts[counts.index(min(counts))] += 1
    # Resolve capacity overflow.
    for _ in range(n):
        over = [i for i, (c, cap) in enumerate(zip(counts, caps)) if c > cap]
        if not over:
            break
        room = [i for i, (c, cap) in enumerate(zip(counts, caps)) if c < cap]
        if not room:
            break  # not enough total capacity; fall through (rare; span too short)
        counts[over[0]] -= 1
        counts[room[0]] += 1

    xs = []
    for (a, b), c in zip(segs, counts):
        if c <= 0:
            continue
        if c == 1:
            xs.append((a + b) / 2.0)
            continue
        seg_len = b - a
        # Clamp spacing so c feet fit; centre the row in the segment.
        spacing = min(FOOT_MIN_SPACING, seg_len / (c - 1))
        row_len = spacing * (c - 1)
        start = a + (seg_len - row_len) / 2.0
        for k in range(c):
            xs.append(start + k * spacing)
    xs.sort(reverse=True)  # foot_0 = front
    return xs


def _build_stabilizer_feet(model, r, mats, body, lay):
    n = r.stabilizer_foot_count
    flen = lay.foot_len * r.foot_span_scale
    ground_cap_z = 0.022
    # Keep feet clear of the crank's pedal-sweep X band: a foot landing under the
    # bottom bracket would be struck by the rotating pedal/crank. Distribute the
    # feet evenly over the front-to-rear span but EXCLUDE the crank band, so feet
    # never collide with the crank/pedals and never stack on the band edge.
    crank_x = lay.crank_xyz[0]
    # Crank arms/hub are thin in X (~+/-0.026) at y=0; the pedal platforms sit far
    # out in Y and never reach the thin y=0 feet. So the exclusion only needs to
    # clear the crank body itself plus the foot collar half-width.
    sweep_clear = 0.026 + 0.022 + 0.02
    foot_xs = _foot_x_positions(
        n, lay.foot_front_x, lay.foot_rear_x, crank_x, sweep_clear
    )
    for i in range(n):
        fx = foot_xs[i]
        foot = model.part(f"stabilizer_foot_{i}")
        # The FIXED joint origin is anchored on the BODY underside at (fx, 0,
        # mount_world_z) so parent_distance ~ 0. The child frame origin (0,0,0)
        # coincides with that mount point; the ground tube sits a fixed drop
        # below it. tube_local_z is the child-frame z of the cross tube (always
        # negative, i.e. below the mount), so the leg spans the origin and the
        # ground tube reaches down to z=ground_cap_z in world.
        mount_world_z = lay.body_bottom_z(fx)
        origin_z = mount_world_z
        tube_local_z = ground_cap_z - mount_world_z
        foot.visual(
            _foot_tube_mesh(flen),
            origin=Origin(xyz=(0.0, 0.0, tube_local_z)),
            material=mats["chrome"],
            name="stabilizer_tube", material_class_id="metal.chrome_polished",
        )
        # Vertical down-leg from the ground tube up to the body mount. It spans
        # the child-frame origin (z=0, the FIXED joint anchor) up to ~+0.01 so the
        # articulation origin lands inside the child geometry.
        leg_top_local = 0.01
        leg_bot_local = tube_local_z
        leg_len = max(leg_top_local - leg_bot_local, 0.04)
        leg = CylinderGeometry(0.020, leg_len)
        leg.translate(0.0, 0.0, leg_bot_local + leg_len / 2.0)
        foot.visual(mesh_from_geometry(leg, "foot_leg"), material=mats["chrome"], name="foot_leg", material_class_id="metal.chrome_polished")
        # Mount collar straddling the child-frame origin (the FIXED joint anchor)
        # so a collision surface passes within tol of (0,0,0): a thin (Z) plate
        # whose faces sit ~0.01 either side of the origin -> child_distance ~0.
        mount = BoxGeometry((0.044, 0.044, 0.020)).translate(0.0, 0.0, 0.0)
        foot.visual(mesh_from_geometry(mount, "foot_mount"), material=mats["chrome"], name="foot_mount", material_class_id="metal.chrome_polished")
        # End caps + ground pads.
        for cy in (flen / 2.0, -flen / 2.0):
            side = "l" if cy > 0 else "r"
            cap = CylinderGeometry(0.024, 0.030).rotate_x(math.pi / 2.0)
            cap.translate(0.0, cy - math.copysign(0.012, cy), tube_local_z)
            foot.visual(mesh_from_geometry(cap, f"foot_cap_{side}"), material=mats["black"], name=f"foot_cap_{side}", material_class_id="plastic.opaque_generic")
            pad = BoxGeometry((0.040, 0.050, 0.022)).translate(
                0.0, cy - math.copysign(0.006, cy), tube_local_z - 0.011
            )
            foot.visual(mesh_from_geometry(pad, f"foot_pad_{side}"), material=mats["black"], name=f"foot_pad_{side}", material_class_id="rubber.smooth_plain")
        foot.inertial = Inertial.from_geometry(
            Box((0.05, flen, max(leg_len, 0.1))), mass=1.5,
            origin=Origin(xyz=(0.0, 0.0, leg_bot_local + leg_len / 2.0)),
        )
        model.articulation(
            f"body_to_stabilizer_foot_{i}",
            ArticulationType.FIXED,
            parent=body,
            child=foot,
            origin=Origin(xyz=(fx, 0.0, origin_z)),
        )


# --------------------------------------------------------------------------- #
# Resistance flywheel + optional tension knob
# --------------------------------------------------------------------------- #


def _build_flywheel(model, r, mats, body, lay):
    fr = FLYWHEEL_R_BASE * r.flywheel_radius_scale
    flywheel = model.part("flywheel")

    if r.resistance_form == "front_disc_red_ring":
        flywheel.visual(_disc_mesh(fr), material=mats["gray"], name="flywheel_disc", material_class_id="metal.cast_iron_bare")
        # Anchor the accent ring on the disc rim (disc radius = fr*0.86) so the
        # torus tube straddles the solid disc (no floating island at any scale).
        flywheel.visual(_ring_mesh(fr * 0.86), material=mats["accent"], name="flywheel_red_ring", material_class_id="metal.paint_coated")
        flywheel.visual(_marker_mesh(fr * 0.55), material=mats["dark"], name="flywheel_marker", material_class_id="metal.paint_coated")
    elif r.resistance_form == "perforated_spoked":
        flywheel.visual(_rim_mesh(fr), material=mats["gray"], name="flywheel_rim", material_class_id="metal.cast_iron_bare")
        flywheel.visual(_hub_mesh(), material=mats["gray"], name="flywheel_hub", material_class_id="metal.cast_iron_bare")
        spoke_mesh = mesh_from_geometry(_spoke_arm_geometry(fr), "spoke_arm")
        for i in range(N_SPOKES):
            angle_i = i * (2.0 * math.pi / N_SPOKES)
            flywheel.visual(
                spoke_mesh, origin=Origin(rpy=(0.0, angle_i, 0.0)),
                material=mats["gray"], name=f"spoke_{i}", material_class_id="metal.aluminum_bare",
            )
        # Centre the accent ring on the rim's inner edge so its tube straddles
        # the solid rim annulus AND the spoke outer tips (no floating island).
        rim_major = fr * 0.84
        flywheel.visual(_ring_mesh(rim_major), material=mats["accent"], name="flywheel_red_ring", material_class_id="metal.paint_coated")
        marker_r = 0.034 + (fr * 0.84 - 0.034) * 0.50
        flywheel.visual(_marker_mesh(marker_r), material=mats["dark"], name="flywheel_marker", material_class_id="metal.paint_coated")
    else:  # magnetic_shroud_knob: hidden mass disc behind a body cowl + knob
        disc = CylinderGeometry(fr * 0.82, FLYWHEEL_HALF_W * 2.0).rotate_x(math.pi / 2.0)
        hub = CylinderGeometry(0.038, FLYWHEEL_HALF_W * 2.0 * 1.2).rotate_x(math.pi / 2.0)
        disc.merge(hub)
        flywheel.visual(mesh_from_geometry(disc, "flywheel_mass"), material=mats["gray"], name="flywheel_mass", material_class_id="metal.cast_iron_bare")
        flywheel.visual(_marker_mesh(fr * 0.55), material=mats["dark"], name="flywheel_marker", material_class_id="metal.paint_coated")

    # Axle spindle along the spin (Y) axis through the child-frame origin. Its
    # cylindrical wall (radius 0.013 < tol 0.015) keeps the joint origin inside
    # the child collision geometry (child_distance ~ 0).
    axle = CylinderGeometry(0.013, FLYWHEEL_HALF_W * 2.0 * 1.4).rotate_x(math.pi / 2.0)
    flywheel.visual(mesh_from_geometry(axle, "flywheel_axle"), material=mats["dark"], name="flywheel_axle", material_class_id="metal.blackened_gunmetal")

    flywheel.inertial = Inertial.from_geometry(
        Cylinder(fr, 2.0 * FLYWHEEL_HALF_W), mass=4.0,
    )
    fx, fy, fz = lay.flywheel_xyz
    model.articulation(
        "body_to_flywheel",
        ArticulationType.CONTINUOUS,
        parent=body,
        child=flywheel,
        origin=Origin(xyz=(fx, fy, fz)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=2.0, velocity=20.0),
    )


def _build_resistance_housing(model, r, mats, body, lay):
    """Magnetic cowl: a static body visual covering the hidden flywheel mass."""
    fx, _, fz = lay.flywheel_xyz
    housing_z = fz + 0.02
    wx, wy, wz = 0.36, 0.24, 0.40
    body.visual(
        _shroud_pod_mesh(fx, housing_z, wx, wy, wz),
        material=mats["body"],
        name="resistance_housing", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"classic_white_red", "studio_gray_lime", "clinical_white_blue"} else "metal.paint_coated"),
    )
    seam = CylinderGeometry(0.095, 0.008).rotate_x(math.pi / 2.0)
    seam.translate(fx, 0.0, housing_z - wz / 2.0 + 0.004)
    body.visual(mesh_from_geometry(seam, "housing_seam"), material=mats["dark"], name="housing_seam", material_class_id="plastic.opaque_generic")
    return housing_z + wz / 2.0  # housing top z


def _build_tension_knob(model, r, mats, body, lay, housing_top_z):
    fx, _, _ = lay.flywheel_xyz
    knob_z = housing_top_z + 0.002
    tension_knob = model.part("tension_knob")
    knob_mesh = KnobGeometry(
        0.040, 0.022, body_style="domed", top_diameter=0.032,
        grip=KnobGrip(style="fluted", count=16, depth=0.0012),
        indicator=KnobIndicator(style="line", mode="engraved", depth=0.0008),
        center=False,
    )
    tension_knob.visual(mesh_from_geometry(knob_mesh, "tension_knob_cap"), material=mats["dark"], name="tension_knob_cap", material_class_id="plastic.patterned_textured")
    tab = BoxGeometry((0.024, 0.006, 0.010)).translate(0.024, 0.0, 0.008)
    tension_knob.visual(mesh_from_geometry(tab, "knob_pointer_tab"), material=mats["accent"], name="knob_pointer_tab", material_class_id="plastic.opaque_glossy_molded")
    shaft = CylinderGeometry(0.008, 0.010)
    shaft.translate(0.0, 0.0, -0.005)
    tension_knob.visual(mesh_from_geometry(shaft, "knob_shaft"), material=mats["chrome"], name="knob_shaft", material_class_id="metal.chrome_polished")
    tension_knob.inertial = Inertial.from_geometry(
        Cylinder(0.022, 0.024), mass=0.08, origin=Origin(xyz=(0.0, 0.0, 0.011)),
    )
    model.articulation(
        "body_to_tension_knob",
        ArticulationType.REVOLUTE,
        parent=body,
        child=tension_knob,
        origin=Origin(xyz=(fx, 0.0, knob_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=2.0, velocity=3.0, lower=0.0, upper=2.6),
    )


# --------------------------------------------------------------------------- #
# Crank + pedals (shared core)
# --------------------------------------------------------------------------- #


def _build_crank_pedals(model, r, mats, body, lay):
    arm_len = CRANK_ARM_LEN * r.crank_arm_len_scale
    crank = model.part("crank")
    # Bottom-bracket spindle along the spin (Y) axis through the child origin.
    # Radius 0.013 < tol 0.015 so its wall keeps the joint origin inside the
    # child collision geometry (child_distance ~ 0).
    hub = CylinderGeometry(0.013, 2.0 * CRANK_ARM_Y).rotate_x(math.pi / 2.0)
    crank_geo = hub
    for sgn, ay in ((1.0, CRANK_ARM_Y), (-1.0, -CRANK_ARM_Y)):
        arm = BoxGeometry((0.026, 0.022, arm_len)).translate(0.0, ay, sgn * arm_len / 2.0)
        crank_geo = crank_geo.merge(arm)
    crank.visual(mesh_from_geometry(crank_geo, "crank_body"), material=mats["dark"], name="crank_body", material_class_id="metal.blackened_gunmetal")
    crank.inertial = Inertial.from_geometry(Box((0.06, 0.24, 0.18)), mass=1.2)
    cx, _, cz = lay.crank_xyz
    # Bottom-bracket spindle on the BODY at the crank joint origin. A thin
    # (radius 0.013 < tol 0.015) co-axial stub keeps the joint origin inside the
    # parent collision geometry (parent_distance ~ 0) regardless of frame form.
    bb_stub = CylinderGeometry(0.013, 2.0 * CRANK_ARM_Y * 1.15).rotate_x(math.pi / 2.0)
    bb_stub.translate(cx, 0.0, cz)
    body.visual(mesh_from_geometry(bb_stub, "crank_spindle"), material=mats["chrome"], name="crank_spindle", material_class_id="metal.chrome_polished")
    model.articulation(
        "body_to_crank",
        ArticulationType.CONTINUOUS,
        parent=body,
        child=crank,
        origin=Origin(xyz=(cx, 0.0, cz)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=4.0, velocity=12.0),
    )

    pedal_specs = (
        ("left_pedal", CRANK_ARM_Y, arm_len, PEDAL_Y),
        ("right_pedal", -CRANK_ARM_Y, -arm_len, -PEDAL_Y),
    )
    for pname, tip_y, tip_z, plat_y in pedal_specs:
        pedal = model.part(pname)
        out = plat_y - tip_y
        plat = BoxGeometry((0.090, 0.060, 0.014)).translate(0.0, out, 0.0)
        spindle = CylinderGeometry(0.009, abs(out) + 0.02).rotate_x(math.pi / 2.0)
        spindle.translate(0.0, out / 2.0, 0.0)
        plat = plat.merge(spindle)
        ridge = BoxGeometry((0.012, 0.060, 0.020)).translate(0.034, out, 0.006)
        plat = plat.merge(ridge)
        pedal.visual(mesh_from_geometry(plat, "pedal_tread"), material=mats["dark"], name="pedal_tread", material_class_id="rubber.directional_grooved")
        pedal.inertial = Inertial.from_geometry(
            Box((0.09, 0.06, 0.03)), mass=0.25, origin=Origin(xyz=(0.0, out, 0.0))
        )
        model.articulation(
            f"crank_to_{pname}",
            ArticulationType.CONTINUOUS,
            parent=crank,
            child=pedal,
            origin=Origin(xyz=(0.0, tip_y, tip_z)),
            axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(effort=1.0, velocity=8.0),
        )


# --------------------------------------------------------------------------- #
# Rider station: saddle post + handlebar post (upright/spin)
# --------------------------------------------------------------------------- #


def _post_collar_geo(r, x, y, z):
    """Body-side insertion collar for a PRISMATIC post.

    Thin in X/Y (0.026 -> inradius 0.013 < tol 0.015) so the joint origin sits
    inside the parent collision geometry. On the upright shroud the saddle/handle
    posts insert well above the moulded body top, so the collar is a tall seat
    tube that bridges from just above the insertion origin down into the shroud
    body (no floating island). On the tube frames the frame already carries its
    own seat/head collars, so a short collar at the origin is enough.
    """
    if r.frame_type == "upright_shroud":
        col_top = z + 0.04
        col_bot = 0.42 * r.body_height_scale  # reaches below the shroud top (~0.50*h)
        col_h = max(col_top - col_bot, 0.10)
        return BoxGeometry((0.026, 0.026, col_h)).translate(x, y, (col_top + col_bot) / 2.0)
    return BoxGeometry((0.026, 0.026, 0.10)).translate(x, y, z)


def _build_saddle_post(model, r, mats, body, lay):
    saddle_post = model.part("saddle_post")
    saddle_post.visual(
        Cylinder(radius=0.018, length=0.34),
        origin=Origin(xyz=(0.0, 0.0, -0.02)),
        material=mats["chrome"],
        name="saddle_post_tube", material_class_id="metal.chrome_polished",
    )
    saddle_post.visual(
        _saddle_mesh(),
        origin=Origin(xyz=(0.0, 0.0, 0.16)),
        material=mats["seat_pad"],
        name="saddle_pad", material_class_id="leather.smooth_plain",
    )
    saddle_post.inertial = Inertial.from_geometry(
        Box((0.16, 0.16, 0.40)), mass=1.6, origin=Origin(xyz=(0.0, 0.0, 0.08))
    )
    # Seat-tube collar on the BODY at the post insertion origin, so the PRISMATIC
    # joint origin sits inside the parent collision geometry (parent_distance ~ 0).
    # Thin in X/Y (0.026 -> inradius 0.013 < tol 0.015).
    sx, sy, sz = lay.saddle_origin
    seat_collar = _post_collar_geo(r, sx, sy, sz)
    body.visual(mesh_from_geometry(seat_collar, "seat_collar"), material=mats["dark"], name="seat_collar", material_class_id="metal.blackened_gunmetal")
    model.articulation(
        "body_to_saddle_post",
        ArticulationType.PRISMATIC,
        parent=body,
        child=saddle_post,
        origin=Origin(xyz=lay.saddle_origin),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=60.0, velocity=0.1, lower=0.0, upper=r.post_travel),
    )


def _build_handlebar_ramhorn(model, r, mats, hbar_post):
    hbar_post.visual(
        # Shrunk + centred over the stem (local x=0) so the console never
        # overhangs forward onto the saddle. Its front edge stays ~0.028 m behind
        # the saddle-pad rear edge for the whole (frame-independent) X range, so
        # raising the saddle post can never drive the pad into the console.
        Box((0.12, 0.12, 0.022)),
        origin=Origin(xyz=(0.0, 0.0, 0.36), rpy=(0.0, -0.6, 0.0)),
        material=mats["body"], name="console_pad", material_class_id="plastic.opaque_glossy_molded",
    )
    hbar_post.visual(Box((0.05, 0.06, 0.05)), origin=Origin(xyz=(0.0, 0.0, 0.36)), material=mats["dark"], name="handlebar_clamp", material_class_id="metal.blackened_gunmetal")
    hbar_post.visual(_ramhorn_mesh(), origin=Origin(xyz=(0.0, 0.0, 0.40)), material=mats["accent"], name="handlebar_tube", material_class_id="metal.paint_coated")


def _build_handlebar_straight(model, r, mats, hbar_post):
    hbar_post.visual(Box((0.05, 0.06, 0.05)), origin=Origin(xyz=(0.0, 0.0, 0.36)), material=mats["dark"], name="handlebar_clamp", material_class_id="metal.blackened_gunmetal")
    hbar_post.visual(_straight_bar_mesh(), origin=Origin(xyz=(0.0, 0.0, 0.39)), material=mats["dark"], name="handlebar_bar", material_class_id="metal.blackened_gunmetal")
    for i in range(2):
        gy = -0.20 + i * 0.40
        hbar_post.visual(_grip_mesh(), origin=Origin(xyz=(0.0, gy, 0.39)), material=mats["black"], name=f"grip_{i}", material_class_id="rubber.smooth_plain")


def _build_handlebar_aero(model, r, mats, hbar_post):
    hbar_post.visual(
        # Shrunk + centred over the stem (local x=0) so the console never
        # overhangs forward onto the saddle. Its front edge stays ~0.028 m behind
        # the saddle-pad rear edge for the whole (frame-independent) X range, so
        # raising the saddle post can never drive the pad into the console.
        Box((0.12, 0.12, 0.022)),
        origin=Origin(xyz=(0.0, 0.0, 0.36), rpy=(0.0, -0.6, 0.0)),
        material=mats["body"], name="console_pad", material_class_id="plastic.opaque_glossy_molded",
    )
    hbar_post.visual(Box((0.05, 0.06, 0.06)), origin=Origin(xyz=(0.0, 0.0, 0.36)), material=mats["dark"], name="handlebar_clamp", material_class_id="metal.blackened_gunmetal")
    cockpit_z = 0.395
    hbar_post.visual(_crossbar_mesh(), origin=Origin(xyz=(0.0, 0.0, cockpit_z)), material=mats["accent"], name="crossbar", material_class_id="metal.paint_coated")
    for i in range(2):
        side = 1.0 if i == 0 else -1.0
        hbar_post.visual(_side_grip_sleeve_mesh(), origin=Origin(xyz=(0.0, side * 0.20, cockpit_z)), material=mats["dark"], name=f"side_grip_{i}", material_class_id="rubber.smooth_plain")
    aero_y = 0.07
    for i in range(2):
        side = 1.0 if i == 0 else -1.0
        y_off = side * aero_y
        hbar_post.visual(_aero_extension_mesh(), origin=Origin(xyz=(0.0, y_off, cockpit_z)), material=mats["accent"], name=f"aero_extension_{i}", material_class_id="metal.paint_coated")
        hbar_post.visual(_forearm_pad_mesh(), origin=Origin(xyz=(0.01, y_off, cockpit_z - 0.012)), material=mats["dark"], name=f"forearm_pad_{i}", material_class_id="fabric.upholstery_plain")


_HANDLEBAR_FACTORIES = {
    "ramhorn_console": _build_handlebar_ramhorn,
    "straight_bar_no_console": _build_handlebar_straight,
    "aero_multigrip": _build_handlebar_aero,
}


def _build_handlebar_post(model, r, mats, body, lay):
    hbar_post = model.part("handlebar_post")
    # Tube spans the child origin (z=0, the insertion datum) but its lower end is
    # raised so it clears the front flywheel on the spin frame, while still
    # inserting deep enough to stay retained in the body head column.
    hbar_post.visual(
        Cylinder(radius=0.020, length=0.44),
        origin=Origin(xyz=(0.0, 0.0, 0.14)),
        material=mats["chrome"],
        name="handlebar_post_tube", material_class_id="metal.chrome_polished",
    )
    _HANDLEBAR_FACTORIES[r.handlebar_form](model, r, mats, hbar_post)
    hbar_post.inertial = Inertial.from_geometry(
        Box((0.34, 0.70, 0.60)), mass=2.2, origin=Origin(xyz=(0.04, 0.0, 0.24))
    )
    # Head-column collar on the BODY at the post insertion origin, so the
    # PRISMATIC joint origin sits inside the parent collision geometry
    # (parent_distance ~ 0). Thin in X/Y (0.026 -> inradius 0.013 < tol 0.015).
    hx, hy, hz = lay.hbar_origin
    head_collar = _post_collar_geo(r, hx, hy, hz)
    body.visual(mesh_from_geometry(head_collar, "head_collar"), material=mats["dark"], name="head_collar", material_class_id="metal.blackened_gunmetal")
    model.articulation(
        "body_to_handlebar_post",
        ArticulationType.PRISMATIC,
        parent=body,
        child=hbar_post,
        origin=Origin(xyz=lay.hbar_origin),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=60.0, velocity=0.1, lower=0.0, upper=r.post_travel),
    )


# --------------------------------------------------------------------------- #
# Recumbent rider station: seat carriage (prismatic X) + side grips (fixed)
# --------------------------------------------------------------------------- #


def _build_seat_carriage(model, r, mats, body, lay):
    seat_carriage = model.part("seat_carriage")
    carriage_plate = BoxGeometry((0.16, 0.060, 0.014)).translate(0.0, 0.0, 0.007)
    seat_carriage.visual(mesh_from_geometry(carriage_plate, "carriage_plate"), material=mats["dark"], name="carriage_plate", material_class_id="metal.blackened_gunmetal")
    seat_post_h = 0.08
    seat_post = CylinderGeometry(0.020, seat_post_h)
    seat_post.translate(0.02, 0.0, 0.014 + seat_post_h / 2.0)
    seat_carriage.visual(mesh_from_geometry(seat_post, "seat_post"), material=mats["chrome"], name="seat_post", material_class_id="metal.chrome_polished")
    seat_carriage.visual(
        mesh_from_cadquery(_bucket_seat_mesh(), "bucket_seat"),
        origin=Origin(xyz=(0.0, 0.0, 0.014 + seat_post_h + 0.01)),
        material=mats["seat_pad"], name="bucket_seat", material_class_id="fabric.upholstery_plain",
    )
    bracket_h = 0.26
    bracket = CylinderGeometry(0.012, bracket_h)
    bracket.translate(-0.10, 0.0, 0.014 + bracket_h / 2.0)
    seat_carriage.visual(mesh_from_geometry(bracket, "backrest_bracket"), material=mats["chrome"], name="backrest_bracket", material_class_id="metal.chrome_polished")
    seat_carriage.visual(
        mesh_from_cadquery(_backrest_mesh(), "backrest_pad"),
        origin=Origin(xyz=(-0.10, 0.0, 0.014 + 0.04)),
        material=mats["seat_pad"], name="backrest_pad", material_class_id="fabric.upholstery_plain",
    )
    seat_carriage.inertial = Inertial.from_geometry(
        Box((0.22, 0.20, 0.30)), mass=3.5, origin=Origin(xyz=(0.0, 0.0, 0.12)),
    )
    model.articulation(
        "body_to_seat_carriage",
        ArticulationType.PRISMATIC,
        parent=body,
        child=seat_carriage,
        origin=Origin(xyz=(RC_SEAT_X, 0.0, RC_SEAT_RAIL_Z_TOP)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=60.0, velocity=0.1, lower=-0.06, upper=0.06),
    )

    for i, side in enumerate((1.0, -1.0)):
        grip = model.part(f"side_grip_{i}")
        stub_len = 0.04
        stub = CylinderGeometry(0.011, stub_len).rotate_x(math.pi / 2.0)
        stub.translate(0.0, side * stub_len / 2.0, 0.0)
        grip.visual(mesh_from_geometry(stub, "grip_stub"), material=mats["chrome"], name="grip_stub", material_class_id="metal.chrome_polished")
        grip.visual(_recumbent_side_grip_mesh(side), origin=Origin(xyz=(0.0, side * stub_len, 0.0)), material=mats["accent"], name=f"grip_bar_{i}", material_class_id="metal.paint_coated")
        grip.inertial = Inertial.from_geometry(
            Box((0.12, 0.10, 0.18)), mass=0.4, origin=Origin(xyz=(0.0, side * 0.05, 0.06))
        )
        model.articulation(
            f"body_to_side_grip_{i}",
            ArticulationType.FIXED,
            parent=body,
            child=grip,
            origin=Origin(xyz=(RC_GRIP_X, side * RC_BEAM_HALF_W, RC_GRIP_Z)),
        )


# --------------------------------------------------------------------------- #
# Top-level builder
# --------------------------------------------------------------------------- #


def build_exercise_bike(
    config: ExerciseBikeConfig,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name="exercise_bike", assets=assets)
    for name, rgba in r.palette.items():
        model.material(name, rgba=rgba)
    mats = {name: name for name in r.palette}

    lay = _frame_layout(r)

    body = _BODY_FACTORIES[r.frame_type](model, r, mats, lay)
    _build_stabilizer_feet(model, r, mats, body, lay)

    housing_top_z = None
    if r.has_tension_knob:
        housing_top_z = _build_resistance_housing(model, r, mats, body, lay)
    _build_flywheel(model, r, mats, body, lay)
    if r.has_tension_knob:
        _build_tension_knob(model, r, mats, body, lay, housing_top_z)

    _build_crank_pedals(model, r, mats, body, lay)

    if r.is_recumbent:
        _build_seat_carriage(model, r, mats, body, lay)
    else:
        _build_saddle_post(model, r, mats, body, lay)
        _build_handlebar_post(model, r, mats, body, lay)

    return model


def build_seeded_exercise_bike(seed: int) -> ArticulatedObject:
    return build_exercise_bike(config_from_seed(seed))


# --------------------------------------------------------------------------- #
# Tests
# --------------------------------------------------------------------------- #


def _ext(aabb):
    mn, mx = aabb
    return (mx[0] - mn[0], mx[1] - mn[1], mx[2] - mn[2])


def _aabb_disjoint(a, b, tol: float = 0.001) -> bool:
    """True if two world AABBs are separated on at least one axis (no overlap)."""
    (amn, amx), (bmn, bmx) = a, b
    return any(amx[i] <= bmn[i] + tol or bmx[i] <= amn[i] + tol for i in range(3))


def run_exercise_bike_tests(model: ArticulatedObject, config: ExerciseBikeConfig) -> TestReport:
    r = resolve_config(config)
    lay = _frame_layout(r)
    ctx = TestContext(model)

    body = model.get_part("body")
    flywheel = model.get_part("flywheel")
    crank = model.get_part("crank")
    left_pedal = model.get_part("left_pedal")
    feet = [model.get_part(f"stabilizer_foot_{i}") for i in range(r.stabilizer_foot_count)]

    fly_joint = model.get_articulation("body_to_flywheel")
    crank_joint = model.get_articulation("body_to_crank")
    lpedal_joint = model.get_articulation("crank_to_left_pedal")

    body_shroud_elem = "body_beam" if r.is_recumbent else ("frame" if r.frame_type == "spin_tube_frame" else "body_shroud")

    # ---- Intentional captured/seated overlaps ----
    ctx.allow_overlap(
        crank, body,
        reason="Crank hub passes through the body and seats on the dark crank boss; intentional mounting.",
    )
    ctx.allow_overlap(
        flywheel, body,
        reason="Flywheel is seated on its axle against the body; intentional rotary mounting.",
    )
    ctx.allow_overlap(
        left_pedal, crank,
        reason="Left pedal spindle is intentionally captured on the crank arm tip.",
    )
    ctx.allow_overlap(
        model.get_part("right_pedal"), crank,
        reason="Right pedal spindle is intentionally captured on the crank arm tip.",
    )
    for foot in feet:
        ctx.allow_overlap(
            foot, body,
            reason="Stabilizer foot leg + mount collar intentionally seat into the body "
            "(shroud/beam/frame and any resistance housing) at the FIXED joint anchor.",
        )

    # ---- Flywheel spins about the side (Y) axis: off-axis marker revolves ----
    m0 = ctx.part_element_world_aabb(flywheel, elem="flywheel_marker")
    mc0 = ((m0[0][0] + m0[1][0]) / 2.0, (m0[0][2] + m0[1][2]) / 2.0)
    with ctx.pose({fly_joint: math.pi / 2.0}):
        m1 = ctx.part_element_world_aabb(flywheel, elem="flywheel_marker")
        mc1 = ((m1[0][0] + m1[1][0]) / 2.0, (m1[0][2] + m1[1][2]) / 2.0)
    ctx.check(
        "flywheel marker revolves about the side axis",
        abs(mc1[1] - mc0[1]) > 0.04 and abs(mc1[0] - mc0[0]) > 0.04,
        details=f"marker XZ rest={mc0}, quarter-turn={mc1}",
    )

    if r.frame_type == "spin_tube_frame":
        ctx.check(
            "spin flywheel is centered on the frame axle",
            abs(SP_FLYWHEEL_Y) < 1e-9,
            details=f"flywheel_y={SP_FLYWHEEL_Y}",
        )
        fx, fy, fz = lay.flywheel_xyz
        cx, cy, cz = lay.crank_xyz
        ctx.check(
            "spin flywheel is belt-linked ahead of the crank",
            fx > cx + 0.20 and abs(fy - cy) < 1e-9 and abs(fz - cz) < 0.04,
            details=f"flywheel={lay.flywheel_xyz}, crank={lay.crank_xyz}",
        )
        belt_aabb = ctx.part_element_world_aabb(body, elem="belt_drive")
        ctx.check(
            "spin belt drive spans the crank-to-flywheel distance",
            belt_aabb[0][0] <= cx - 0.04 and belt_aabb[1][0] >= fx + 0.10,
            details=f"belt_x=({belt_aabb[0][0]:.3f}, {belt_aabb[1][0]:.3f}), crank_x={cx}, flywheel_x={fx}",
        )
        support_aabb = ctx.part_element_world_aabb(body, elem="flywheel_axle_support")
        ctx.check(
            "spin flywheel axle has static bearing supports on both sides",
            support_aabb[0][1] < -0.10
            and support_aabb[1][1] > 0.10
            and support_aabb[0][0] < fx < support_aabb[1][0]
            and support_aabb[0][2] < fz < support_aabb[1][2],
            details=f"support={support_aabb}, flywheel_axis=({fx}, {fy}, {fz})",
        )
        ctx.check(
            "spin flywheel axle support feet land on the lower frame",
            support_aabb[0][2] <= SP_FORK_L[2] + 0.012,
            details=f"support_min_z={support_aabb[0][2]:.4f}, frame_low_z={SP_FORK_L[2]:.4f}",
        )

    # ---- Crank rotation revolves the pedal mount ----
    p0 = ctx.part_world_position(left_pedal)
    with ctx.pose({crank_joint: math.pi / 2.0}):
        p1 = ctx.part_world_position(left_pedal)
    ctx.check(
        "crank rotation revolves the pedal about the crank axis",
        p0 is not None and p1 is not None
        and (abs(p1[0] - p0[0]) > 0.03 or abs(p1[2] - p0[2]) > 0.03),
        details=f"left pedal rest={p0}, crank quarter-turn={p1}",
    )

    # ---- Pedal spins on its own spindle ----
    e0 = _ext(ctx.part_world_aabb(left_pedal))
    with ctx.pose({lpedal_joint: math.pi / 2.0}):
        e1 = _ext(ctx.part_world_aabb(left_pedal))
    ctx.check(
        "left pedal spins on its spindle",
        abs(e1[0] - e0[0]) > 0.01 or abs(e1[2] - e0[2]) > 0.01,
        details=f"pedal extents rest={e0}, spun={e1}",
    )

    # ---- Pedal orbit clears the resistance housing (magnetic cowl) ----
    # The crank arms + pedals sweep in Y-planes outboard of the centred cowl, so
    # even when a pedal swings fully forward (crank quarter-turn) into the
    # housing's X/Z shadow it stays laterally clear. Regression guard for the
    # pedal->resistance_housing 穿模 that appeared when the cowl reached into the
    # pedal orbit.
    if r.has_tension_knob:
        housing_aabb = ctx.part_element_world_aabb(body, elem="resistance_housing")
        right_pedal = model.get_part("right_pedal")
        clear = True
        worst = None
        for ang in (math.pi / 2.0, -math.pi / 2.0):
            with ctx.pose({crank_joint: ang}):
                for ped in (left_pedal, right_pedal):
                    pa = ctx.part_world_aabb(ped)
                    if not _aabb_disjoint(housing_aabb, pa):
                        clear = False
                        worst = (ang, ped.name, pa)
        ctx.check(
            "pedals clear the resistance housing through the crank sweep",
            clear,
            details=f"housing={housing_aabb}, collision={worst}",
        )

    # ---- Rider station: PRISMATIC + retained insertion ----
    if r.is_recumbent:
        seat_carriage = model.get_part("seat_carriage")
        seat_joint = model.get_articulation("body_to_seat_carriage")
        ctx.allow_overlap(
            seat_carriage, body,
            elem_a="carriage_plate", elem_b="seat_rail",
            reason="Carriage plate rides on the dark seat rail; intentional sliding contact.",
        )
        sc0 = ctx.part_world_position(seat_carriage)
        with ctx.pose({seat_joint: 0.06}):
            sc1 = ctx.part_world_position(seat_carriage)
        ctx.check(
            "seat carriage slides along X (recumbent rail)",
            sc0 is not None and sc1 is not None and abs(sc1[0] - sc0[0]) > 0.04,
            details=f"carriage rest={sc0}, slid={sc1}",
        )
        # Side grips are fixed.
        for i in range(2):
            grip = model.get_part(f"side_grip_{i}")
            gj = model.get_articulation(f"body_to_side_grip_{i}")
            ctx.check(
                f"side_grip_{i} is FIXED",
                gj.articulation_type == ArticulationType.FIXED,
                details=f"type={gj.articulation_type}",
            )
        # No saddle_post / handlebar_post on recumbent (mutual exclusion).
        part_names = {p.name for p in model.parts}
        ctx.check(
            "recumbent has no front handlebar post or saddle post",
            "handlebar_post" not in part_names and "saddle_post" not in part_names,
            details=f"parts={sorted(part_names)}",
        )
    else:
        saddle_post = model.get_part("saddle_post")
        hbar_post = model.get_part("handlebar_post")
        saddle_joint = model.get_articulation("body_to_saddle_post")
        hbar_joint = model.get_articulation("body_to_handlebar_post")
        ctx.allow_overlap(
            saddle_post, body,
            reason="Saddle post slides inside the body's seat tube/collar; intentional insertion.",
        )
        ctx.allow_overlap(
            hbar_post, body,
            reason="Handlebar post slides inside the body's head column/collar; intentional insertion.",
        )
        s0 = ctx.part_world_position(saddle_post)
        with ctx.pose({saddle_joint: r.post_travel}):
            s1 = ctx.part_world_position(saddle_post)
        ctx.check(
            "saddle post raises the seat",
            s0 is not None and s1 is not None and s1[2] > s0[2] + r.post_travel * 0.7,
            details=f"saddle rest_z={s0}, raised_z={s1}",
        )
        ctx.expect_overlap(
            saddle_post, body, axes="z",
            elem_a="saddle_post_tube", elem_b=body_shroud_elem,
            min_overlap=0.02, name="saddle post retained in seat tube",
        )
        h0 = ctx.part_world_position(hbar_post)
        with ctx.pose({hbar_joint: r.post_travel}):
            h1 = ctx.part_world_position(hbar_post)
        ctx.check(
            "handlebar post raises",
            h0 is not None and h1 is not None and h1[2] > h0[2] + r.post_travel * 0.7,
            details=f"hbar rest_z={h0}, raised_z={h1}",
        )
        # Saddle pad clears the console pad at MAX saddle travel (worst case;
        # handlebar left at rest = console lowest). Regression guard for the
        # saddle_pad->console_pad clash on tall upright setups: the console is
        # shrunk + centred over the stem so its front edge stays behind the
        # saddle-pad rear edge for the whole post travel.
        if r.handlebar_form in ("ramhorn_console", "aero_multigrip"):
            console_aabb = ctx.part_element_world_aabb(hbar_post, elem="console_pad")
            with ctx.pose({saddle_joint: r.post_travel}):
                saddle_aabb = ctx.part_element_world_aabb(saddle_post, elem="saddle_pad")
            ctx.check(
                "saddle pad clears the console pad at full saddle height",
                _aabb_disjoint(saddle_aabb, console_aabb),
                details=f"saddle@max={saddle_aabb}, console={console_aabb}",
            )

    # ---- Tension knob (magnetic only): REVOLUTE Z, pointer tab rotates ----
    if r.has_tension_knob:
        tension_knob = model.get_part("tension_knob")
        knob_joint = model.get_articulation("body_to_tension_knob")
        ctx.check(
            "tension knob is REVOLUTE",
            knob_joint.articulation_type == ArticulationType.REVOLUTE,
            details=f"type={knob_joint.articulation_type}",
        )
        ctx.allow_overlap(
            tension_knob, body,
            reason="Tension knob shaft seats into the resistance housing top; intentional mounting.",
        )
        ctx.allow_overlap(
            flywheel, body,
            elem_a="flywheel_mass", elem_b="resistance_housing",
            reason="The hidden flywheel mass rotates inside the closed resistance cowl.",
        )
        tab0 = ctx.part_element_world_aabb(tension_knob, elem="knob_pointer_tab")
        c0 = ((tab0[0][0] + tab0[1][0]) / 2.0, (tab0[0][1] + tab0[1][1]) / 2.0)
        with ctx.pose({knob_joint: 1.5}):
            tab1 = ctx.part_element_world_aabb(tension_knob, elem="knob_pointer_tab")
            c1 = ((tab1[0][0] + tab1[1][0]) / 2.0, (tab1[0][1] + tab1[1][1]) / 2.0)
        ctx.check(
            "tension knob pointer tab rotates about Z",
            abs(c1[0] - c0[0]) > 0.005 or abs(c1[1] - c0[1]) > 0.005,
            details=f"tab XY rest={c0}, rotated={c1}",
        )

    # ---- Stabilizer feet: ground footprint, widest, named with i, FIXED ----
    foot_aabbs = [ctx.part_world_aabb(f) for f in feet]
    foot_min_z = min(a[0][2] for a in foot_aabbs)
    fly_aabb = ctx.part_world_aabb(flywheel)
    ctx.check(
        "stabilizer feet rest at the ground plane (lowest parts)",
        foot_min_z <= fly_aabb[0][2] + 0.02 and foot_min_z < 0.05,
        details=f"foot_min_z={foot_min_z}, flywheel_min_z={fly_aabb[0][2]}",
    )
    foot_span_y = max(a[1][1] for a in foot_aabbs) - min(a[0][1] for a in foot_aabbs)
    body_span_y = _ext(ctx.part_world_aabb(body))[1]
    ctx.check(
        "feet are the widest footprint",
        foot_span_y >= body_span_y - 0.01,
        details=f"foot_span_y={foot_span_y}, body_span_y={body_span_y}",
    )
    # Foot count + naming + FIXED.
    ctx.check(
        "stabilizer foot count matches config",
        len(feet) == r.stabilizer_foot_count,
        details=f"n_feet={len(feet)}, expected={r.stabilizer_foot_count}",
    )
    for i in range(r.stabilizer_foot_count):
        fj = model.get_articulation(f"body_to_stabilizer_foot_{i}")
        ctx.check(
            f"stabilizer_foot_{i} is FIXED",
            fj.articulation_type == ArticulationType.FIXED,
            details=f"type={fj.articulation_type}",
        )
    # Front foot forward of rear foot (when N>=2).
    if r.stabilizer_foot_count >= 2:
        front_cx = (foot_aabbs[0][0][0] + foot_aabbs[0][1][0]) / 2.0
        rear_cx = (foot_aabbs[-1][0][0] + foot_aabbs[-1][1][0]) / 2.0
        ctx.check(
            "front foot is forward of rear foot",
            front_cx > rear_cx,
            details=f"front_cx={front_cx}, rear_cx={rear_cx}",
        )

    return ctx.report()
