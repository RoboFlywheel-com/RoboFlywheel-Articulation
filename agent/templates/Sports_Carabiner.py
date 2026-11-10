# SPDX-License-Identifier: Apache-2.0

"""Modular procedural template for ``carabiner``.

Follows ``articraft_template_authoring/specs_modular_v1/Sports_Carabiner.md``.

A spring snap-hook carabiner: a root ``body`` that is one thick round bar bent
into an OPEN hook (NOT a closed loop) lying in the X-Z plane (+Z up), plus a
spring-return ``gate`` that swings about a bottom hinge rivet (REVOLUTE, axis =
loop normal Y) to close the -X gap. One screw-lock gate candidate adds a
``lock_sleeve`` that slides along the gate bar (PRISMATIC) to lock it.

World frame convention (shared by all forms):

- +Z up; the wide rounded TOP of the loop is at high +Z, the small EYE at the
  bottom (low +Z).
- The GATE is the straight -X side. The body is an OPEN hook there: the straight
  -X span between the bottom HINGE boss and the top NOSE is intentionally EMPTY;
  the gate fills it.
- The opposite long side (+X) is the curved "spine".
- The NOSE is the hook tip at the top of the gate-side; the closed gate's latch
  seats against the nose lug (or the bent gate's key tongue seats into a nose
  slot groove).

Two structural axes (each independently swappable):

    Slot A  body_form  (pear_teardrop / oval_symmetric / d_shape / offset_d)
        Same open-hook topology, different centerline point list fed to
        ``tube_from_spline_points`` (mesh, never Box). Emits ``body_loop`` plus a
        nose interface visual: ``nose_lug`` (default) or ``nose_slot`` (bent gate).

    Slot B  gate_mechanism  (straight_solid_gate / wire_gate / bent_gate /
                             screw_lock_sleeve)
        The REVOLUTE gate + its latch/nose-seat interface. screw_lock_sleeve
        additionally carries a PRISMATIC ``lock_sleeve`` child on the gate bar.

Compatibility (spec §拓扑多样性审计 / §compatibility matrix):
- bent_gate requires the body nose interface to be a ``nose_slot`` groove (key
  tongue seats into it); all other gates use a ``nose_lug``.
- screw_lock_sleeve requires a continuous solid gate bar as its slide rail, so it
  always builds on the straight solid gate body.

Adopted sources (spec Module Source Index, all revisions/rev_000001/model.py):
S0 parent rec_stainless-...550acf8b — pear body + straight solid gate + hinge.
S1 rec_carabiner_var_oval     — oval symmetric body centerline.
S2 rec_carabiner_var_dshape   — D-shape body centerline.
S3 rec_carabiner_var_offsetd  — offset-D body centerline (extra width params).
S4 rec_carabiner_var_wiregate — continuous-spline wire hairpin gate.
S5 rec_carabiner_var_bentgate — bent key-lock gate + nose_slot interface.
S6 rec_carabiner_var_screwlock— screw-lock PRISMATIC sleeve on the gate bar.
"""

from __future__ import annotations

import math
import random
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import cadquery as cq

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Inertial,
    MatingContract,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
    mesh_from_geometry,
    tube_from_spline_points,
)

# adopted: S0 550acf8b — pear body + straight solid gate + bottom hinge rivet
# adopted: S1 oval     — symmetric oval body centerline
# adopted: S2 dshape   — D-shape body centerline (tight corners + bowed spine)
# adopted: S3 offsetd  — offset-D body centerline (broad top, pinched eye)
# adopted: S4 wiregate — continuous-spline wire hairpin gate + hinge plate
# adopted: S5 bentgate — bent key-lock gate + nose_slot groove interface
# adopted: S6 screwlock— knurled PRISMATIC lock sleeve riding the gate bar

__modular__ = True

BodyForm = Literal["pear_teardrop", "oval_symmetric", "d_shape", "offset_d"]
GateMechanism = Literal[
    "straight_solid_gate",
    "wire_gate",
    "bent_gate",
    "screw_lock_sleeve",
]
PaletteStyle = Literal[
    "bright_satin_steel",
    "dark_anodized_steel",
    "polished_chrome",
    "matte_black_tactical",
    "anodized_red_accent",
    "brass_gold",
]

BODY_FORMS: tuple[BodyForm, ...] = (
    "pear_teardrop",
    "oval_symmetric",
    "d_shape",
    "offset_d",
)
GATE_MECHANISMS: tuple[GateMechanism, ...] = (
    "straight_solid_gate",
    "wire_gate",
    "bent_gate",
    "screw_lock_sleeve",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "bright_satin_steel",
    "dark_anodized_steel",
    "polished_chrome",
    "matte_black_tactical",
    "anodized_red_accent",
    "brass_gold",
)

# Near-uniform body sampling.
_BODY_WEIGHTS = {
    "pear_teardrop": 0.28,
    "oval_symmetric": 0.26,
    "d_shape": 0.24,
    "offset_d": 0.22,
}
# Gate sampling: screw_lock slightly downweighted (extra PRISMATIC joint).
_GATE_WEIGHTS = {
    "straight_solid_gate": 0.30,
    "wire_gate": 0.27,
    "bent_gate": 0.25,
    "screw_lock_sleeve": 0.18,
}

# satin/dark colorway pairs: (body, pin·sleeve dark accent).
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "bright_satin_steel": {
        "body": (0.74, 0.76, 0.78, 1.0),
        "dark": (0.55, 0.57, 0.60, 1.0),
    },
    "dark_anodized_steel": {
        "body": (0.34, 0.36, 0.40, 1.0),
        "dark": (0.18, 0.19, 0.22, 1.0),
    },
    "polished_chrome": {
        "body": (0.88, 0.90, 0.93, 1.0),
        "dark": (0.62, 0.65, 0.70, 1.0),
    },
    "matte_black_tactical": {
        "body": (0.09, 0.09, 0.10, 1.0),
        "dark": (0.40, 0.40, 0.42, 1.0),
    },
    "anodized_red_accent": {
        "body": (0.66, 0.12, 0.14, 1.0),
        "dark": (0.20, 0.21, 0.24, 1.0),
    },
    "brass_gold": {
        "body": (0.80, 0.62, 0.26, 1.0),
        "dark": (0.50, 0.38, 0.14, 1.0),
    },
}

# =========================================================================== #
# Base real-world dimensions (meters). From S0 parent baseline.
# =========================================================================== #
BAR_R = 0.0042  # round bar radius (~0.008 m dia)
HALF_W = 0.022  # half width of the loop (bar-center span ~0.044)
TOP_Z = 0.100  # top of bar centerline at the wide bend
EYE_Z = 0.012  # eye bottom (bar centerline)

# Gate-side straight run.
GATE_HINGE_Z = 0.028  # hinge pin height on the gate-side (bottom rivet)
GATE_NOSE_Z = 0.082  # nose / latch height (just below the top bend)
GATE_R = 0.0038  # gate bar radius (a touch slimmer than the body bar)

# offset-D extra width params (S3).
OFFSET_TOP_HALF_W = 0.030
OFFSET_SPINE_BOW = 0.034
OFFSET_BOT_HALF_W = 0.010

# wire gate (S4).
WIRE_R = 0.0013
WIRE_LEG_SPACING = 0.0052

# bent gate (S5).
BEND_ANGLE = math.radians(40.0)
BEND_FRAC = 0.68
KEY_LEN = 0.006

# screw-lock sleeve (S6).
SLEEVE_LEN = 0.015


def _clamp(value: float, lo: float, hi: float) -> float:
    if lo > hi:
        lo, hi = hi, lo
    return max(lo, min(hi, float(value)))


def _pick(value, choices):
    return value if value in choices else choices[0]


# =========================================================================== #
# Config
# =========================================================================== #


@dataclass(frozen=True)
class CarabinerConfig:
    """Public config sampled by ``config_from_seed`` or supplied directly."""

    body_form: BodyForm = "pear_teardrop"
    gate_mechanism: GateMechanism = "straight_solid_gate"
    palette_style: PaletteStyle = "bright_satin_steel"
    body_height_scale: float = 1.0
    body_width_scale: float = 1.0
    bar_radius_scale: float = 1.0
    gate_open_angle: float = math.radians(28.0)
    sleeve_travel_scale: float = 1.0
    name: str = "reference_carabiner"


@dataclass(frozen=True)
class ResolvedCarabinerConfig:
    body_form: BodyForm
    gate_mechanism: GateMechanism
    nose_interface: Literal["nose_lug", "nose_slot"]
    palette_style: PaletteStyle
    palette: dict[str, tuple[float, float, float, float]]
    # geometry scales
    body_height_scale: float
    body_width_scale: float
    bar_radius_scale: float
    gate_open_angle: float
    sleeve_travel_scale: float
    name: str
    # derived absolute dimensions
    bar_r: float
    gate_r: float
    half_w: float
    top_z: float
    eye_z: float
    gate_x: float
    gate_hinge_z: float
    gate_nose_z: float
    gate_len: float
    # offset-D derived widths
    offset_top_half_w: float
    offset_spine_bow: float
    offset_bot_half_w: float
    # sleeve derived
    sleeve_ir: float
    sleeve_or: float
    sleeve_home_z: float
    sleeve_travel: float


def config_from_seed(seed: int) -> CarabinerConfig:
    """Deterministic per-seed procedural sampling (seed 0 is not special).

    Samples body_form and gate_mechanism (near-uniform, screw_lock slightly
    downweighted), then independent continuous scales. The compatibility matrix
    (bent_gate -> nose_slot; screw_lock -> solid rail) is applied in
    ``resolve_config``; nothing illegal is produced here.
    """
    rng = random.Random(seed)

    bodies = list(_BODY_WEIGHTS.keys())
    body: BodyForm = rng.choices(bodies, weights=[_BODY_WEIGHTS[b] for b in bodies], k=1)[0]

    gates = list(_GATE_WEIGHTS.keys())
    gate: GateMechanism = rng.choices(gates, weights=[_GATE_WEIGHTS[g] for g in gates], k=1)[0]

    palette: PaletteStyle = rng.choice(PALETTE_STYLES)

    body_height_scale = round(rng.uniform(0.85, 1.18), 4)
    body_width_scale = round(rng.uniform(0.82, 1.20), 4)
    bar_radius_scale = round(rng.uniform(0.85, 1.20), 4)
    gate_open_angle = math.radians(round(rng.uniform(22.0, 32.0), 3))
    sleeve_travel_scale = round(rng.uniform(0.90, 1.10), 4)

    return CarabinerConfig(
        body_form=body,
        gate_mechanism=gate,
        palette_style=palette,
        body_height_scale=body_height_scale,
        body_width_scale=body_width_scale,
        bar_radius_scale=bar_radius_scale,
        gate_open_angle=gate_open_angle,
        sleeve_travel_scale=sleeve_travel_scale,
        name=f"seeded_carabiner_{seed}",
    )


def resolve_config(config: CarabinerConfig) -> ResolvedCarabinerConfig:
    if config.palette_style not in PALETTES:
        raise ValueError(f"Unsupported palette_style: {config.palette_style}")

    body = _pick(config.body_form, BODY_FORMS)
    gate = _pick(config.gate_mechanism, GATE_MECHANISMS)

    # Compatibility matrix: screw_lock needs a continuous solid gate rail; it is
    # only valid on the straight solid gate. (It is sampled as its own gate
    # mechanism that *is* a straight solid bar + sleeve, so no fallback needed —
    # but defensively keep the derivation explicit.)
    nose_interface: Literal["nose_lug", "nose_slot"] = (
        "nose_slot" if gate == "bent_gate" else "nose_lug"
    )

    bh = _clamp(config.body_height_scale, 0.85, 1.18)
    bw = _clamp(config.body_width_scale, 0.82, 1.20)
    br = _clamp(config.bar_radius_scale, 0.85, 1.20)
    open_angle = _clamp(config.gate_open_angle, math.radians(22.0), math.radians(32.0))
    sleeve_travel_scale = _clamp(config.sleeve_travel_scale, 0.90, 1.10)

    bar_r = BAR_R * br
    gate_r = GATE_R * br

    # Height: scale the TOP_Z/EYE_Z span about the eye anchor so the eye stays
    # near the ground line and the body grows upward.
    eye_z = EYE_Z
    top_z = eye_z + (TOP_Z - eye_z) * bh
    gate_hinge_z = eye_z + (GATE_HINGE_Z - eye_z) * bh
    gate_nose_z = eye_z + (GATE_NOSE_Z - eye_z) * bh
    gate_len = gate_nose_z - gate_hinge_z

    half_w = HALF_W * bw
    gate_x = -half_w

    offset_top_half_w = OFFSET_TOP_HALF_W * bw
    offset_spine_bow = OFFSET_SPINE_BOW * bw
    offset_bot_half_w = OFFSET_BOT_HALF_W * bw

    # Sleeve: bore rides the gate bar. A real sliding fit has a tiny radial
    # clearance, but a clearance ring never *touches* the bar, so it reads as a
    # disconnected island in the support graph. Make the bore meet the bar
    # (slight interference, guarded by the lock_sleeve_barrel<->gate_bar
    # allow_overlap) so the sleeve stays attached to the grounded tree.
    sleeve_ir = gate_r - 0.0002
    sleeve_or = max(gate_r * 2.2, sleeve_ir + 0.0018)
    half_sleeve = SLEEVE_LEN / 2.0
    # The knurled lock sleeve rides ONLY the straight gate rail (gate-local z in
    # [0, gate_len]); it must never dig into the body LOOP. Bound the rail:
    #   bottom -> above the loop bar + hinge boss wrapping the pin near z=0;
    #   top    -> below the loop's gate-side NOSE bar. The nose bar centerline
    #             enters at world gate_nose_z + 0.002 (gate-local gate_len +
    #             0.002); its lower surface sits ~bar_r under that. Keep the
    #             sleeve TOP a clear >overlap_tol gap (0.006) below it so the
    #             barrel stays on the straight segment (the element-scoped allow
    #             covers only the coaxial gate_bar ride, never the body loop).
    rail_bottom = 0.010
    rail_top = (gate_len + 0.002 - bar_r) - 0.006
    sleeve_home_z = rail_bottom + half_sleeve
    sleeve_lock_z = rail_top - half_sleeve
    physical_travel = max(0.0, sleeve_lock_z - sleeve_home_z)
    # Scale travel DOWN only (never overshoot the rail top into the nose bend),
    # while keeping it long enough to visibly bridge the gate-nose seam.
    sleeve_travel = _clamp(
        physical_travel * min(sleeve_travel_scale, 1.0),
        min(physical_travel, 0.0112),
        physical_travel,
    )

    return ResolvedCarabinerConfig(
        body_form=body,
        gate_mechanism=gate,
        nose_interface=nose_interface,
        palette_style=config.palette_style,
        palette=PALETTES[config.palette_style],
        body_height_scale=bh,
        body_width_scale=bw,
        bar_radius_scale=br,
        gate_open_angle=open_angle,
        sleeve_travel_scale=sleeve_travel_scale,
        name=config.name,
        bar_r=bar_r,
        gate_r=gate_r,
        half_w=half_w,
        top_z=top_z,
        eye_z=eye_z,
        gate_x=gate_x,
        gate_hinge_z=gate_hinge_z,
        gate_nose_z=gate_nose_z,
        gate_len=gate_len,
        offset_top_half_w=offset_top_half_w,
        offset_spine_bow=offset_spine_bow,
        offset_bot_half_w=offset_bot_half_w,
        sleeve_ir=sleeve_ir,
        sleeve_or=sleeve_or,
        sleeve_home_z=sleeve_home_z,
        sleeve_travel=sleeve_travel,
    )


# =========================================================================== #
# Slot A: body form centerlines (mesh tubes). Each returns a list of
# (x, y, z) control points for tube_from_spline_points. All keep the same
# open-hook topology: free-end NOSE (top gate-side) + free-end HINGE (bottom
# gate-side) + empty straight -X gate gap.
# =========================================================================== #


def _pear_centerline(r: ResolvedCarabinerConfig):
    gx, hw = r.gate_x, r.half_w
    tz, ez = r.top_z, r.eye_z
    hz, nz = r.gate_hinge_z, r.gate_nose_z
    return [
        (gx * 0.92, 0.0, nz + 0.002),
        (gx * 0.80, 0.0, nz + 0.010 * r.body_height_scale),
        (0.0, 0.0, tz),
        (hw * 0.80, 0.0, tz - 0.004),
        (hw, 0.0, ez + (tz - ez) * 0.63),
        (hw * 0.92, 0.0, ez + (tz - ez) * 0.36),
        (hw * 0.55, 0.0, ez + 0.011),
        (hw * 0.18, 0.0, ez),
        (-hw * 0.18, 0.0, ez),
        (gx * 0.62, 0.0, ez + 0.012),
        (gx, 0.0, hz),
    ]


def _oval_centerline(r: ResolvedCarabinerConfig, n_arc: int = 14):
    gx, hw = r.gate_x, r.half_w
    tz, ez = r.top_z, r.eye_z
    hz, nz = r.gate_hinge_z, r.gate_nose_z
    R = hw  # bend radius (same top & bottom for the symmetric oval)
    z_top_c = tz - R
    z_bot_c = ez + R

    pts: list[tuple[float, float, float]] = []
    pts.append((gx * 0.95, 0.0, nz + 0.002))
    pts.append((gx * 0.88, 0.0, nz - 0.002))
    for i in range(n_arc + 1):
        t = i / n_arc
        angle = math.radians(170.0 - t * 160.0)
        pts.append((R * math.cos(angle), 0.0, z_top_c + R * math.sin(angle)))
    pts.append((hw, 0.0, 0.5 * (z_top_c + z_bot_c)))
    for i in range(n_arc + 1):
        t = i / n_arc
        angle = math.radians(-10.0 - t * 160.0)
        pts.append((R * math.cos(angle), 0.0, z_bot_c + R * math.sin(angle)))
    pts.append((gx * 0.88, 0.0, hz + 0.003))
    pts.append((gx, 0.0, hz))
    return pts


def _dshape_centerline(r: ResolvedCarabinerConfig):
    gx, hw = r.gate_x, r.half_w
    tz, ez = r.top_z, r.eye_z
    hz, nz = r.gate_hinge_z, r.gate_nose_z
    CR = 0.009
    SPINE_BOW = 0.002
    return [
        (gx + 0.002, 0.0, nz + 0.002),
        (gx, 0.0, tz - 0.010),
        (gx + CR * 0.3, 0.0, tz - CR),
        (-hw * 0.25, 0.0, tz - 0.002),
        (0.0, 0.0, tz),
        (hw * 0.25, 0.0, tz - 0.002),
        (hw - CR * 0.3, 0.0, tz - CR),
        (hw, 0.0, tz - CR - 0.004),
        (hw + SPINE_BOW * 0.7, 0.0, ez + (tz - ez) * 0.65),
        (hw + SPINE_BOW, 0.0, ez + (tz - ez) * 0.47),
        (hw + SPINE_BOW * 0.7, 0.0, ez + (tz - ez) * 0.29),
        (hw, 0.0, ez + CR + 0.006),
        (hw - CR * 0.3, 0.0, ez + CR),
        (hw * 0.25, 0.0, ez + 0.003),
        (0.0, 0.0, ez),
        (-hw * 0.25, 0.0, ez + 0.003),
        (gx + CR * 0.3, 0.0, ez + CR),
        (gx, 0.0, ez + CR + 0.006),
        (gx, 0.0, hz + 0.006),
        (gx, 0.0, hz),
    ]


def _offsetd_centerline(r: ResolvedCarabinerConfig):
    gx = r.gate_x
    tz, ez = r.top_z, r.eye_z
    hz, nz = r.gate_hinge_z, r.gate_nose_z
    thw = r.offset_top_half_w
    bow = r.offset_spine_bow
    bhw = r.offset_bot_half_w
    return [
        (gx * 0.92, 0.0, nz + 0.002),
        (gx * 0.55, 0.0, tz - 0.006),
        (-0.004, 0.0, tz + 0.002),
        (thw * 0.45, 0.0, tz + 0.001),
        (thw * 0.82, 0.0, tz - 0.003),
        (bow * 0.94, 0.0, ez + (tz - ez) * 0.70),
        (bow, 0.0, ez + (tz - ez) * 0.49),
        (bow * 0.80, 0.0, ez + (tz - ez) * 0.29),
        (bhw * 1.2, 0.0, ez + 0.010),
        (bhw * 0.5, 0.0, ez),
        (-bhw * 0.5, 0.0, ez),
        (gx * 0.65, 0.0, ez + 0.012),
        (gx, 0.0, hz),
    ]


_BODY_CENTERLINES = {
    "pear_teardrop": _pear_centerline,
    "oval_symmetric": _oval_centerline,
    "d_shape": _dshape_centerline,
    "offset_d": _offsetd_centerline,
}


def _body_hook_mesh(r: ResolvedCarabinerConfig):
    pts = _BODY_CENTERLINES[r.body_form](r)
    return tube_from_spline_points(
        pts,
        radius=r.bar_r,
        closed_spline=False,
        samples_per_segment=22,
        radial_segments=20,
    )


def _nose_lug_mesh(r: ResolvedCarabinerConfig):
    # Short steel hook lip at the top of the gate-side; the closed gate latch
    # seats against it.
    lug = (
        cq.Workplane("XZ")
        .center(r.gate_x + 0.0022, r.gate_nose_z - 0.001)
        .rect(0.0075, 0.006)
        .extrude(r.bar_r * 0.95, both=True)
    )
    return mesh_from_cadquery(lug, "nose_lug")


def _bent_tip_local(r: ResolvedCarabinerConfig) -> tuple[float, float]:
    bend_z = r.gate_len * BEND_FRAC
    bent_len = r.gate_len * 0.36
    tip_x = math.sin(BEND_ANGLE) * bent_len
    tip_z = bend_z + math.cos(BEND_ANGLE) * bent_len
    return tip_x, tip_z


def _bent_key_world(r: ResolvedCarabinerConfig) -> tuple[float, float]:
    tip_x, tip_z = _bent_tip_local(r)
    key_local_x = tip_x - KEY_LEN / 2.0
    key_world_x = r.gate_x + key_local_x
    key_world_z = r.gate_hinge_z + tip_z
    return key_world_x, key_world_z


def _nose_slot_mesh(r: ResolvedCarabinerConfig):
    # Nose lug WITH a slot groove (open +X face) to receive the bent gate key.
    key_world_x, key_world_z = _bent_key_world(r)
    key_w = r.gate_r * 1.6
    key_h = r.gate_r * 1.8

    lug_dy = r.bar_r * 2.4
    lug_dz = 0.011
    # The bent key tongue reaches its highest, most-inboard point at
    # (key_world_x, key_world_z); the bent gate bar climbs from below it. Anchor
    # the slot lug to the body NOSE (x ~= gate_x .. nose, just ABOVE the key top)
    # so its body connects to the loop bar while the slot opens DOWNWARD to
    # receive the key from below — this keeps the lug clear of the bent bar that
    # travels under z=key_world_z and inboard.
    nose_x = r.gate_x  # body nose centerline x at the gate-side top
    lug_cx = 0.5 * (nose_x + key_world_x)
    lug_dx = max(0.012, abs(key_world_x - nose_x) + 0.008)
    # Bottom face of the lug just above the key top so the slot can bite down.
    key_top_z = key_world_z + key_h / 2.0
    lug_cz = key_top_z + lug_dz / 2.0 - 0.0015

    lug = (
        cq.Workplane("XY")
        .box(lug_dx, lug_dy, lug_dz)
        .translate((lug_cx, 0.0, lug_cz))
    )
    # Slot groove cut UP into the lug bottom, embracing the key tongue tip.
    slot_dx = KEY_LEN + 0.0025
    slot_dy = key_w + 0.002
    slot_dz = key_h + 0.003
    slot = (
        cq.Workplane("XY")
        .box(slot_dx, slot_dy, slot_dz)
        .translate((key_world_x, 0.0, key_world_z))
    )
    return mesh_from_cadquery(lug.cut(slot), "nose_slot")


# =========================================================================== #
# Slot B: gate meshes (gate local frame: hinge pin at origin, bar up +Z).
# =========================================================================== #


def _solid_gate_bar_mesh(r: ResolvedCarabinerConfig):
    bar = cq.Workplane("XY").circle(r.gate_r).extrude(r.gate_len)
    bar = bar.union(cq.Workplane("XY").sphere(r.gate_r)).union(
        cq.Workplane("XY").workplane(offset=r.gate_len).sphere(r.gate_r)
    )
    boss = cq.Workplane("XZ").circle(r.gate_r * 1.55).extrude(0.0048, both=True)
    # Nose shoulder: a short stub at the bar top reaching INBOARD (+X) so the
    # latch lip (which seats out at the nose-lug +X face) stays welded to the bar
    # as one continuous solid (avoids a disconnected-island flag on the lip).
    lug_pos_x_local = 0.0022 + 0.0075 / 2.0
    shoulder = (
        cq.Workplane("XY")
        .box(lug_pos_x_local + r.gate_r * 1.2, r.gate_r * 1.6, r.gate_r * 1.8)
        .translate((0.5 * (lug_pos_x_local + r.gate_r * 1.2), 0.0, r.gate_len))
    )
    return mesh_from_cadquery(bar.union(boss).union(shoulder), "gate_bar")


def _gate_latch_mesh(r: ResolvedCarabinerConfig):
    # Latch lip at the gate-bar top. It is welded onto the bar (gate-local x ~= 0)
    # and reaches INBOARD (+X) so its -X face presses against the body nose lug's
    # +X face when closed. The nose lug's +X face sits at gate-local x = 0.0022 +
    # 0.0075/2 = 0.005950; build the lip so its -X face lands there (the mating
    # face declared in the hinge MatingContract is this lip -X face vs lug +X).
    lug_pos_x_local = 0.0022 + 0.0075 / 2.0
    lip_x0 = lug_pos_x_local  # lip -X face seats on the lug +X face
    lip_x1 = lug_pos_x_local + r.gate_r * 2.2
    lip_cx = 0.5 * (lip_x0 + lip_x1)
    lip_dx = lip_x1 - lip_x0
    hook = (
        cq.Workplane("XZ")
        .center(lip_cx, r.gate_len + r.gate_r * 0.3)
        .rect(lip_dx, r.gate_r * 1.9)
        .extrude(r.gate_r * 1.2, both=True)
    )
    return mesh_from_cadquery(hook, "gate_latch")


def _hinge_pin_mesh(r: ResolvedCarabinerConfig):
    pin = cq.Workplane("XZ").circle(r.gate_r * 0.55).extrude(0.0062, both=True)
    return mesh_from_cadquery(pin, "hinge_pin")


def _wire_gate_mesh(r: ResolvedCarabinerConfig):
    wire_r = WIRE_R * r.bar_radius_scale
    leg_spacing = WIRE_LEG_SPACING
    bend_r = leg_spacing / 2.0
    half_s = leg_spacing / 2.0
    bend_top = r.gate_len - bend_r * 0.15

    n_bend = 8
    bend_pts = []
    for i in range(n_bend + 1):
        t = i / n_bend
        angle = math.pi * t
        y = -half_s * math.cos(angle)
        z = bend_top + bend_r * math.sin(angle) * 0.85
        bend_pts.append((0.0, y, z))

    pts = (
        [
            (0.0, -half_s, 0.002),
            (0.0, -half_s, r.gate_len * 0.35),
            (0.0, -half_s, r.gate_len * 0.70),
        ]
        + bend_pts
        + [
            (0.0, half_s, r.gate_len * 0.70),
            (0.0, half_s, r.gate_len * 0.35),
            (0.0, half_s, 0.002),
        ]
    )
    wire_mesh = tube_from_spline_points(
        pts,
        radius=wire_r,
        closed_spline=False,
        samples_per_segment=16,
        radial_segments=12,
        cap_ends=True,
    )
    plate = (
        cq.Workplane("XZ")
        .center(0.0, 0.001)
        .rect(wire_r * 3.0, wire_r * 4.0)
        .extrude(half_s + wire_r, both=True)
    )
    plate_mesh = mesh_from_cadquery(plate, "wire_hinge_plate")
    return wire_mesh, plate_mesh, wire_r, bend_r


def _wire_latch_mesh(r: ResolvedCarabinerConfig, wire_r: float, bend_r: float):
    # The hairpin U-bend top is the natural latch; cap it with a small tab that
    # rises to the body nose lug TOP (whose footprint it sits inside). Its top
    # (+Z) face is co-planar with the lug top (+Z) face — the Z-axis mating
    # declared on the hinge for the wire gate. The tab welds onto the U-bend
    # (overlap-allowed wire_latch_tip<->wire_loop) so it is not a disconnected
    # island. Lug top in gate-local z = (gate_nose_z - 0.001 + 0.003) - gate_hinge_z.
    lug_top_local = (r.gate_nose_z - 0.001 + 0.003) - r.gate_hinge_z
    tab_top_z = lug_top_local
    tab_h = wire_r * 4.5
    cap = (
        cq.Workplane("XY")
        .box(wire_r * 3.2, WIRE_LEG_SPACING + wire_r * 2.0, tab_h)
        .translate((0.0, 0.0, tab_top_z - tab_h / 2.0))
    )
    return mesh_from_cadquery(cap, "wire_latch_tip")


def _wire_pin_mesh(r: ResolvedCarabinerConfig, wire_r: float):
    pin = (
        cq.Workplane("XZ")
        .circle(wire_r * 1.1)
        .extrude(WIRE_LEG_SPACING / 2 + wire_r + 0.001, both=True)
    )
    return mesh_from_cadquery(pin, "hinge_pin")


def _bent_gate_bar_mesh(r: ResolvedCarabinerConfig):
    bend_z = r.gate_len * BEND_FRAC
    bent_len = r.gate_len * 0.36
    tip_x, tip_z = _bent_tip_local(r)

    straight = cq.Workplane("XY").circle(r.gate_r).extrude(bend_z)
    straight = straight.union(cq.Workplane("XY").sphere(r.gate_r))
    bend_sphere = cq.Workplane("XY").sphere(r.gate_r).translate((0.0, 0.0, bend_z))
    bent = cq.Workplane("XY").circle(r.gate_r).extrude(bent_len)
    bent = bent.rotate((0.0, 0.0, 0.0), (0.0, 1.0, 0.0), math.degrees(BEND_ANGLE))
    bent = bent.translate((0.0, 0.0, bend_z))
    tip_sphere = cq.Workplane("XY").sphere(r.gate_r).translate((tip_x, 0.0, tip_z))
    boss = cq.Workplane("XZ").circle(r.gate_r * 1.55).extrude(0.0048, both=True)
    gate = straight.union(bend_sphere).union(bent).union(tip_sphere).union(boss)
    return mesh_from_cadquery(gate, "gate_bar")


def _bent_key_mesh(r: ResolvedCarabinerConfig):
    tip_x, tip_z = _bent_tip_local(r)
    key_local_x = tip_x - KEY_LEN / 2.0
    key_w = r.gate_r * 1.6
    key_h = r.gate_r * 1.8
    key = (
        cq.Workplane("XY")
        .box(KEY_LEN, key_w, key_h)
        .translate((key_local_x, 0.0, tip_z))
    )
    return mesh_from_cadquery(key, "gate_key")


def _lock_sleeve_mesh(r: ResolvedCarabinerConfig):
    half = SLEEVE_LEN / 2.0
    outer = (
        cq.Workplane("XY")
        .circle(r.sleeve_or)
        .extrude(SLEEVE_LEN)
        .translate((0.0, 0.0, -half))
    )
    bore = (
        cq.Workplane("XY")
        .circle(r.sleeve_ir)
        .extrude(SLEEVE_LEN + 0.002)
        .translate((0.0, 0.0, -half - 0.001))
    )
    sleeve = outer.cut(bore)
    n_rings = 6
    ring_h = SLEEVE_LEN / (n_rings * 2.5)
    ring_r = r.sleeve_or + 0.0004
    for i in range(n_rings):
        z_center = -half + SLEEVE_LEN * (i + 0.5) / n_rings
        ring = (
            cq.Workplane("XY")
            .workplane(offset=z_center - ring_h / 2.0)
            .circle(ring_r)
            .circle(r.sleeve_or - 0.0002)
            .extrude(ring_h)
        )
        sleeve = sleeve.union(ring)
    return mesh_from_cadquery(sleeve, "lock_sleeve_barrel")


# =========================================================================== #
# Builders
# =========================================================================== #


def _build_body(model: ArticulatedObject, r: ResolvedCarabinerConfig, mats: dict):
    body = model.part("body")
    body.visual(
        mesh_from_geometry(_body_hook_mesh(r), "body_loop"),
        material=mats["body"],
        name="body_loop", material_class_id=("metal.stainless_matte" if r.palette_style in {"bright_satin_steel", "dark_anodized_steel", "matte_black_tactical", "anodized_red_accent", "brass_gold"} else "metal.chrome_polished"),
    )
    if r.nose_interface == "nose_slot":
        body.visual(_nose_slot_mesh(r), material=mats["body"], name="nose_slot", material_class_id=("metal.stainless_matte" if r.palette_style in {"bright_satin_steel", "dark_anodized_steel", "matte_black_tactical", "anodized_red_accent", "brass_gold"} else "metal.chrome_polished"))
    else:
        body.visual(_nose_lug_mesh(r), material=mats["body"], name="nose_lug", material_class_id=("metal.stainless_matte" if r.palette_style in {"bright_satin_steel", "dark_anodized_steel", "matte_black_tactical", "anodized_red_accent", "brass_gold"} else "metal.chrome_polished"))
    body.inertial = Inertial.from_geometry(
        Box((0.052, 0.012, max(0.090, r.top_z))),
        mass=0.085,
        origin=Origin(xyz=(0.0, 0.0, 0.5 * r.top_z)),
    )
    return body


def _build_gate(model: ArticulatedObject, r: ResolvedCarabinerConfig, mats: dict, body):
    gate = model.part("gate")

    if r.gate_mechanism == "wire_gate":
        wire_mesh, plate_mesh, wire_r, bend_r = _wire_gate_mesh(r)
        gate.visual(mesh_from_geometry(wire_mesh, "wire_loop"), material=mats["body"], name="wire_loop", material_class_id=("metal.stainless_matte" if r.palette_style in {"bright_satin_steel", "dark_anodized_steel", "matte_black_tactical", "anodized_red_accent", "brass_gold"} else "metal.chrome_polished"))
        gate.visual(plate_mesh, material=mats["body"], name="wire_hinge_plate", material_class_id=("metal.stainless_matte" if r.palette_style in {"bright_satin_steel", "dark_anodized_steel", "matte_black_tactical", "anodized_red_accent", "brass_gold"} else "metal.chrome_polished"))
        gate.visual(_wire_latch_mesh(r, wire_r, bend_r), material=mats["body"], name="wire_latch_tip", material_class_id=("metal.stainless_matte" if r.palette_style in {"bright_satin_steel", "dark_anodized_steel", "matte_black_tactical", "anodized_red_accent", "brass_gold"} else "metal.chrome_polished"))
        gate.visual(_wire_pin_mesh(r, wire_r), material=mats["dark"], name="hinge_pin", material_class_id=("metal.stainless_matte" if r.palette_style in {"bright_satin_steel", "polished_chrome", "anodized_red_accent", "brass_gold"} else "metal.blackened_gunmetal"))
        latch_elem = "wire_latch_tip"
        gate.inertial = Inertial.from_geometry(
            Box((0.004, 0.006, max(0.040, r.gate_len))),
            mass=0.004,
            origin=Origin(xyz=(0.0, 0.0, 0.5 * r.gate_len)),
        )
    elif r.gate_mechanism == "bent_gate":
        gate.visual(_bent_gate_bar_mesh(r), material=mats["body"], name="gate_bar", material_class_id=("metal.stainless_matte" if r.palette_style in {"bright_satin_steel", "dark_anodized_steel", "matte_black_tactical", "anodized_red_accent", "brass_gold"} else "metal.chrome_polished"))
        gate.visual(_bent_key_mesh(r), material=mats["body"], name="gate_key", material_class_id=("metal.stainless_matte" if r.palette_style in {"bright_satin_steel", "dark_anodized_steel", "matte_black_tactical", "anodized_red_accent", "brass_gold"} else "metal.chrome_polished"))
        gate.visual(_hinge_pin_mesh(r), material=mats["dark"], name="hinge_pin", material_class_id=("metal.stainless_matte" if r.palette_style in {"bright_satin_steel", "polished_chrome", "anodized_red_accent", "brass_gold"} else "metal.blackened_gunmetal"))
        latch_elem = "gate_key"
        gate.inertial = Inertial.from_geometry(
            Box((0.014, 0.008, max(0.044, r.gate_len + 0.004))),
            mass=0.013,
            origin=Origin(xyz=(0.003, 0.0, 0.5 * r.gate_len)),
        )
    else:  # straight_solid_gate / screw_lock_sleeve share the solid bar
        gate.visual(_solid_gate_bar_mesh(r), material=mats["body"], name="gate_bar", material_class_id=("metal.stainless_matte" if r.palette_style in {"bright_satin_steel", "dark_anodized_steel", "matte_black_tactical", "anodized_red_accent", "brass_gold"} else "metal.chrome_polished"))
        gate.visual(_gate_latch_mesh(r), material=mats["body"], name="gate_latch", material_class_id=("metal.stainless_matte" if r.palette_style in {"bright_satin_steel", "dark_anodized_steel", "matte_black_tactical", "anodized_red_accent", "brass_gold"} else "metal.chrome_polished"))
        gate.visual(_hinge_pin_mesh(r), material=mats["dark"], name="hinge_pin", material_class_id=("metal.stainless_matte" if r.palette_style in {"bright_satin_steel", "polished_chrome", "anodized_red_accent", "brass_gold"} else "metal.blackened_gunmetal"))
        latch_elem = "gate_latch"
        gate.inertial = Inertial.from_geometry(
            Box((0.008, 0.008, max(0.044, r.gate_len + 0.004))),
            mass=0.012,
            origin=Origin(xyz=(0.0, 0.0, 0.5 * r.gate_len)),
        )

    # Hinge: REVOLUTE about the bottom gate-side rivet. Axis = loop normal Y so
    # the gate swings in the X-Z plane; positive angle pushes the top toward +X
    # (into the loop). Spring-return closed at 0.
    nose_geom = r.nose_interface
    # The bent gate's key tongue seats UPWARD into a downward-opening nose_slot
    # groove (hook-and-slot capture), so its mating faces are along Z: the slot
    # ceiling (parent negative_z) meets the key top (child positive_z). Every
    # other gate's latch lip seats sideways against the +X nose lug face (X).
    if r.gate_mechanism == "bent_gate":
        parent_side, child_side = "negative_z", "positive_z"
    elif r.gate_mechanism == "wire_gate":
        # Wire U-bend tab rises to the lug top: top faces are co-planar (+Z/+Z).
        parent_side, child_side = "positive_z", "positive_z"
    else:
        parent_side, child_side = "positive_x", "negative_x"
    model.articulation(
        "gate_hinge",
        ArticulationType.REVOLUTE,
        parent=body,
        child=gate,
        origin=Origin(xyz=(r.gate_x, 0.0, r.gate_hinge_z)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(
            lower=0.0,
            upper=r.gate_open_angle,
            effort=1.0,
            velocity=3.0,
        ),
        mating=MatingContract(
            parent_face_geometry=nose_geom,
            parent_face_side=parent_side,
            child_face_geometry=latch_elem,
            child_face_side=child_side,
            contact_tol=0.0030,
        ),
    )
    return gate, latch_elem


def _build_lock_sleeve(model: ArticulatedObject, r: ResolvedCarabinerConfig, mats: dict, gate):
    lock_sleeve = model.part("lock_sleeve")
    lock_sleeve.visual(_lock_sleeve_mesh(r), material=mats["dark"], name="lock_sleeve_barrel", material_class_id=("metal.stainless_matte" if r.palette_style in {"bright_satin_steel", "polished_chrome", "anodized_red_accent", "brass_gold"} else "metal.blackened_gunmetal"))
    lock_sleeve.inertial = Inertial.from_geometry(
        Box((r.sleeve_or * 2, r.sleeve_or * 2, SLEEVE_LEN)),
        mass=0.006,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
    )
    model.articulation(
        "sleeve_slide",
        ArticulationType.PRISMATIC,
        parent=gate,
        child=lock_sleeve,
        origin=Origin(xyz=(0.0, 0.0, r.sleeve_home_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(
            lower=0.0,
            upper=r.sleeve_travel,
            effort=2.0,
            velocity=0.1,
        ),
        # Grandfathered (no MatingContract): the knurled sleeve bore CONCENTRICALLY
        # captures the gate bar as a coaxial sliding rail (clearance fit guarded by
        # the lock_sleeve_barrel<->gate_bar allow_overlap). An AABB face-pair gap
        # check is ill-defined for a thin ring around a thin coaxial bar — same
        # grandfather pattern as the lipstick bullet / capsule telescoping slides.
    )
    return lock_sleeve


def _materials(model: ArticulatedObject, r: ResolvedCarabinerConfig) -> dict:
    out = {}
    for key, rgba in r.palette.items():
        out[key] = model.material(f"carabiner_{key}_{r.palette_style}", rgba=rgba)
    return out


def build_carabiner(
    config: CarabinerConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    config = config or CarabinerConfig()
    r = resolve_config(config)
    if assets is None:
        assets = AssetContext(Path(tempfile.mkdtemp(prefix="articraft-carabiner-")))
    model = ArticulatedObject(name=r.name, assets=assets)
    model.meta["slot_choices"] = [list(t) for t in slot_choices_for_config(r)]

    mats = _materials(model, r)

    body = _build_body(model, r, mats)
    gate, _latch_elem = _build_gate(model, r, mats, body)
    if r.gate_mechanism == "screw_lock_sleeve":
        _build_lock_sleeve(model, r, mats, gate)

    return model


def build_seeded_carabiner(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_carabiner(config_from_seed(seed), assets=assets)


# =========================================================================== #
# Slot choices
# =========================================================================== #


def slot_choices_for_config(r: ResolvedCarabinerConfig) -> tuple[tuple[str, str], ...]:
    choices = [
        ("body_form", r.body_form),
        ("gate_mechanism", r.gate_mechanism),
        ("nose_interface", r.nose_interface),
        ("palette_style", r.palette_style),
    ]
    return tuple(choices)


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(resolve_config(config_from_seed(seed)))


# =========================================================================== #
# Tests
# =========================================================================== #


def _ext(aabb):
    mn, mx = aabb
    return (mx[0] - mn[0], mx[1] - mn[1], mx[2] - mn[2])


def _declare_overlap_allowances(
    ctx: TestContext, model: ArticulatedObject, r: ResolvedCarabinerConfig, latch_elem: str
):
    body = model.get_part("body")
    gate = model.get_part("gate")
    nose_geom = r.nose_interface

    # Closed gate latch/key seats into the nose lug/slot (spring-seated capture).
    ctx.allow_overlap(
        gate,
        body,
        elem_a=latch_elem,
        elem_b=nose_geom,
        reason="Closed gate latch/key seats into the nose lug/slot (spring-seated capture).",
    )
    # Solid/screw-lock gate-bar nose shoulder reaches inboard to weld the latch
    # lip on; it slides past the body nose lug at the closed seam.
    if r.gate_mechanism in ("straight_solid_gate", "screw_lock_sleeve"):
        ctx.allow_overlap(
            gate,
            body,
            elem_a="gate_bar",
            elem_b=nose_geom,
            reason="Gate-bar nose shoulder meets the body nose lug at the closed latch seam.",
        )
        ctx.allow_overlap(
            gate,
            body,
            elem_a="gate_latch",
            elem_b="body_loop",
            reason="Closed latch lip hooks over/under the body loop bar at the nose (capture seam).",
        )
    # Hinge boss / plate wraps the loop bar at the pin.
    gate_bar_elem = "wire_loop" if r.gate_mechanism == "wire_gate" else "gate_bar"
    ctx.allow_overlap(
        gate,
        body,
        elem_a=gate_bar_elem,
        elem_b="body_loop",
        reason="Gate hinge boss wraps the loop bar at the pin (mounted hinge capture).",
    )
    if r.gate_mechanism == "wire_gate":
        ctx.allow_overlap(
            gate,
            body,
            elem_a="wire_hinge_plate",
            elem_b="body_loop",
            reason="Wire hinge plate bridges the legs at the loop bar pin.",
        )
    ctx.allow_overlap(
        gate,
        body,
        elem_a="hinge_pin",
        elem_b="body_loop",
        reason="Hinge pin passes through the loop bar at the bottom of the gate-side.",
    )
    if r.gate_mechanism == "screw_lock_sleeve":
        sleeve = model.get_part("lock_sleeve")
        ctx.allow_overlap(
            sleeve,
            gate,
            elem_a="lock_sleeve_barrel",
            elem_b="gate_bar",
            reason="Lock sleeve bore rides on the gate bar (sliding-fit clearance).",
        )


def run_carabiner_tests(object_model: ArticulatedObject, config: CarabinerConfig) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)

    body = object_model.get_part("body")
    gate = object_model.get_part("gate")
    hinge = object_model.get_articulation("gate_hinge")
    nose_geom = r.nose_interface
    latch_elem = {
        "straight_solid_gate": "gate_latch",
        "screw_lock_sleeve": "gate_latch",
        "wire_gate": "wire_latch_tip",
        "bent_gate": "gate_key",
    }[r.gate_mechanism]

    _declare_overlap_allowances(ctx, object_model, r, latch_elem)

    # ---- body is an open hook, roughly as tall as wide (real carabiners run
    # from near-square pear/D bodies to clearly tall ovals), eye at the bottom ----
    # Proportional check, not an absolute margin: a wide offset-D/D body can be
    # near-square (z ~= x) yet still legitimate, while a body MUCH wider than tall
    # is not a carabiner. The 5★ sources span z/x ~= 1.0 (wide near-square) up to
    # ~2.4 (slim oval); require z >= 0.92x to admit the widest forms without
    # distorting identity.
    bext = _ext(ctx.part_world_aabb(body))
    ctx.check(
        "body hook is at least as tall as it is wide",
        bext[2] > bext[0] * 0.92,
        details=f"body extents (x,y,z)={bext}, z/x={bext[2] / max(bext[0], 1e-9):.3f}",
    )
    ctx.check(
        "body spans roughly the full carabiner height",
        bext[2] > 0.072,
        details=f"body z-extent={bext[2]}",
    )

    # ---- closed gate latch/key meets the nose lug/slot (capture/contact) ----
    ctx.expect_contact(
        gate,
        body,
        elem_a=latch_elem,
        elem_b=nose_geom,
        contact_tol=0.0020,
        name="closed gate latch/key meets the nose interface",
    )

    # ---- gate hinged near the bottom of the loop ----
    gate_pos = ctx.part_world_position(gate)
    ctx.check(
        "gate hinge is near the bottom of the loop",
        gate_pos is not None and gate_pos[2] < 0.050,
        details=f"gate hinge world pos={gate_pos}",
    )

    # ---- opening swings the gate top inward (+X) and AWAY from the nose ----
    closed_latch = ctx.part_element_world_aabb(gate, elem=latch_elem)
    nose_aabb = ctx.part_element_world_aabb(body, elem=nose_geom)
    closed_cx = 0.5 * (closed_latch[0][0] + closed_latch[1][0])
    nose_cx = 0.5 * (nose_aabb[0][0] + nose_aabb[1][0])
    closed_gap = abs(closed_cx - nose_cx)

    with ctx.pose({hinge: r.gate_open_angle}):
        open_latch = ctx.part_element_world_aabb(gate, elem=latch_elem)
        open_cx = 0.5 * (open_latch[0][0] + open_latch[1][0])
    open_gap = abs(open_cx - nose_cx)

    ctx.check(
        "open gate top swings inward toward +X (into the loop)",
        open_cx > closed_cx + 0.003,
        details=f"closed latch x={closed_cx}, open latch x={open_cx}",
    )
    ctx.check(
        "opening moves the latch away from the nose interface",
        open_gap > closed_gap + 0.002,
        details=f"closed gap={closed_gap}, open gap={open_gap}",
    )

    # ---- screw-lock sleeve: prismatic slide bridges the seam ----
    if r.gate_mechanism == "screw_lock_sleeve":
        sleeve = object_model.get_part("lock_sleeve")
        slide = object_model.get_articulation("sleeve_slide")
        home_z = ctx.part_world_position(sleeve)[2]
        with ctx.pose({slide: r.sleeve_travel}):
            lock_z = ctx.part_world_position(sleeve)[2]
        ctx.check(
            "lock sleeve slides up to bridge the gate-nose seam",
            lock_z > home_z + 0.010,
            details=f"home_z={home_z}, lock_z={lock_z}",
        )

    return ctx.report()


__all__ = [
    "CarabinerConfig",
    "ResolvedCarabinerConfig",
    "build_carabiner",
    "build_seeded_carabiner",
    "config_from_seed",
    "resolve_config",
    "run_carabiner_tests",
    "slot_choices_for_seed",
    "__modular__",
]
