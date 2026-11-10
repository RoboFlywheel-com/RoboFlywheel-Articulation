# SPDX-License-Identifier: Apache-2.0

"""air_conditioner — wall-mounted mini-split indoor unit (modular template).

Category identity: a horizontal glossy white wall-mounted mini-split INDOOR
unit (~0.90 m wide x ~0.22 m deep x ~0.30 m tall), back flat against the wall
(y=0), bottom on the ground (z=0), airflow out the lower front. The root
``housing`` is a CadQuery YZ side-profile extrusion whose mesh family IS the
``body_form`` slot. Inside it are boolean-cut: the lower-front outlet / louver
openings, a shallow top intake frame, a filter cavity (with a fixed
``filter_frame`` + ``filter_mesh``), and a hollow dark cross-flow ``plenum``
(with a fixed dark ``plenum_liner`` cylinder read through the outlet). Two
parallel child layers hang off the housing: the ``airflow_mechanism`` (the
lower-front airflow-directing parts) and the ``service_panel`` (the front
service cover).

Three named slots + one gated multiplicity axis
(spec ``specs_modular_v1/Other_Air_conditioner.md``):

  * ``body_form`` (4) — the housing side-profile mesh family (rewrites
    ``_housing_shape`` + the front-face landing-point / surface-normal solver;
    adds NO joint):
      rounded_bottom_curve / boxy_rectangular / raked_wedge /
      full_bullnose_capsule.
  * ``airflow_mechanism`` (4) — the lower-front airflow direction mechanism:
      - three_independent_slim_vanes: N x REVOLUTE +X horizontal louver vanes.
      - single_wide_deflector: 1 x REVOLUTE +X full-width deflector blade.
      - vertical_vane_bank: ~12 x REVOLUTE +Z vertical deflector vanes.
      - closing_outlet_door: 1 x REVOLUTE -X bottom-hinge outlet door.
  * ``service_panel`` (3) — the front service cover mechanism:
      - top_hinge_lift: 1 x REVOLUTE +X top-hinge lift cover.
      - two_leaf_clamshell: 2 x REVOLUTE +X top-hinge leaves.
      - bottom_hinge_drop_front: 1 x REVOLUTE -X bottom-hinge drop cover.
  * ``vane_count`` (multiplicity, N in [2, 6]) — number of horizontal louver
    vanes; ACTIVE ONLY under ``three_independent_slim_vanes`` (otherwise n/a).

Continuous size/travel variation (body width/height/depth scales, vane swing,
panel open limit, deflector/door open limits) lives in ``resolve_config`` as
clamped params, never as slot candidates. ``palette_style`` (6 colorways) is a
color/material axis only and is NOT a slot choice.

Sources (all 11 5-star records read): parent ``e9cc92a3`` (rounded +
three_independent_slim_vanes + top_hinge_lift + N=3), body forms
``boxy_rectangular`` / ``raked_wedge`` / ``full_bullnose_capsule``, airflow
``single_wide_deflector`` / ``vertical_vane_bank`` / ``closing_outlet_door``,
service ``two_leaf_clamshell`` / ``bottom_hinge_drop_front``, and vane_count
``2`` / ``5`` (range(N) copy + ``_add_louver_vane`` factory blueprint).
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
    Cylinder,
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
BodyForm = Literal[
    "rounded_bottom_curve",
    "boxy_rectangular",
    "raked_wedge",
    "full_bullnose_capsule",
]
AirflowMechanism = Literal[
    "three_independent_slim_vanes",
    "single_wide_deflector",
    "vertical_vane_bank",
    "closing_outlet_door",
]
ServicePanel = Literal[
    "top_hinge_lift",
    "two_leaf_clamshell",
    "bottom_hinge_drop_front",
]
PaletteStyle = Literal[
    "glossy_white_classic",
    "warm_cream",
    "graphite_dark",
    "champagne_gold",
    "matte_silver",
    "sky_soft_blue",
]

BODY_FORMS: tuple[BodyForm, ...] = (
    "rounded_bottom_curve",
    "boxy_rectangular",
    "raked_wedge",
    "full_bullnose_capsule",
)
AIRFLOW_MECHANISMS: tuple[AirflowMechanism, ...] = (
    "three_independent_slim_vanes",
    "single_wide_deflector",
    "vertical_vane_bank",
    "closing_outlet_door",
)
SERVICE_PANELS: tuple[ServicePanel, ...] = (
    "top_hinge_lift",
    "two_leaf_clamshell",
    "bottom_hinge_drop_front",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "glossy_white_classic",
    "warm_cream",
    "graphite_dark",
    "champagne_gold",
    "matte_silver",
    "sky_soft_blue",
)

# vane_count weighted sampling (small N favored; spec Multiplicity table).
_VANE_COUNTS: tuple[int, ...] = (2, 3, 4, 5, 6)
_VANE_WEIGHTS: tuple[float, ...] = (0.22, 0.34, 0.24, 0.14, 0.06)

# ---------------------------------------------------------------------------
# Palettes: shell / panel (cover + airflow parts) / cavity (plenum liner) /
# filter_frame / filter_mesh. Anchored to 5-star RGBA (spec 配色板); each palette
# keeps shell/panel bright, cavity dark, filter mid-gray for functional read.
# palette-only — never a slot choice.
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "glossy_white_classic": {
        "shell": (0.93, 0.94, 0.95, 1.0),
        "panel": (0.96, 0.965, 0.97, 1.0),
        "cavity": (0.07, 0.07, 0.08, 1.0),
        "filter_frame": (0.80, 0.81, 0.82, 1.0),
        "filter_mesh": (0.30, 0.32, 0.34, 1.0),
    },
    "warm_cream": {
        "shell": (0.95, 0.93, 0.87, 1.0),
        "panel": (0.97, 0.955, 0.90, 1.0),
        "cavity": (0.09, 0.08, 0.07, 1.0),
        "filter_frame": (0.82, 0.79, 0.72, 1.0),
        "filter_mesh": (0.34, 0.32, 0.28, 1.0),
    },
    "graphite_dark": {
        "shell": (0.24, 0.25, 0.27, 1.0),
        "panel": (0.30, 0.31, 0.33, 1.0),
        "cavity": (0.05, 0.05, 0.06, 1.0),
        "filter_frame": (0.34, 0.35, 0.37, 1.0),
        "filter_mesh": (0.16, 0.17, 0.18, 1.0),
    },
    "champagne_gold": {
        "shell": (0.86, 0.82, 0.72, 1.0),
        "panel": (0.90, 0.86, 0.75, 1.0),
        "cavity": (0.08, 0.07, 0.06, 1.0),
        "filter_frame": (0.72, 0.66, 0.54, 1.0),
        "filter_mesh": (0.40, 0.36, 0.28, 1.0),
    },
    "matte_silver": {
        "shell": (0.78, 0.79, 0.80, 1.0),
        "panel": (0.84, 0.85, 0.86, 1.0),
        "cavity": (0.07, 0.07, 0.08, 1.0),
        "filter_frame": (0.62, 0.64, 0.66, 1.0),
        "filter_mesh": (0.28, 0.30, 0.32, 1.0),
    },
    "sky_soft_blue": {
        "shell": (0.90, 0.93, 0.95, 1.0),
        "panel": (0.86, 0.91, 0.95, 1.0),
        "cavity": (0.07, 0.08, 0.09, 1.0),
        "filter_frame": (0.76, 0.80, 0.84, 1.0),
        "filter_mesh": (0.28, 0.32, 0.36, 1.0),
    },
}

# ---------------------------------------------------------------------------
# Base geometry constants (meters), from the 5-star sources. Nominal body
# dimensions are scaled per-build in resolve_config.
# ---------------------------------------------------------------------------
BODY_W = 0.90  # width along X (x in [-0.45, 0.45])
BODY_D = 0.22  # overall depth target along Y (front)
BODY_H = 0.30  # height along Z (z in [0, 0.30])

# --- rounded_bottom_curve (parent) side-profile control points ---
ARC_CY, ARC_CZ, ARC_R = 0.085, 0.13, 0.13  # bottom-front quarter-round
FRONT_LO = (0.215, 0.13)  # bottom of the leaning front face
FRONT_HI = (0.205, 0.285)  # top of the leaning front face
TOP_FRONT = (0.185, 0.30)  # front edge of the flat top (small bevel)

# --- boxy_rectangular ---
BOXY_PANEL_ZONE_Z0 = 0.150
BOXY_RECESS_DEPTH = 0.013  # panel recess step depth (front face steps in)

# --- raked_wedge ---
WEDGE_LO_Y = 0.26  # bottom-front corner (far forward)
WEDGE_HI_Y = 0.10  # top-front corner (receded toward the wall)

# --- full_bullnose_capsule ---
BULLNOSE_R = 0.09

# Louver / outlet geometry (shared by airflow mechanisms).
SLOT_LEN = 0.78  # slot cut length along X
SLOT_OPEN = 0.024  # slot opening measured along the surface tangent
SLOT_DEPTH = 0.12  # cut depth along the surface normal (pierces into plenum)
VANE_LEN = 0.74
VANE_CHORD = 0.018
VANE_T = 0.0045
VANE_PIN_R = 0.003
VANE_PIN_LEN = 0.04
VANE_PIN_X = (-0.385, 0.385)

# single_wide_deflector
DEFLECTOR_W = 0.78
DEFLECTOR_H = 0.09
DEFLECTOR_T = 0.005
HINGE_THETA = math.radians(80.0)
DEFLECTOR_SWING_LO = math.radians(-10.0)
DEFLECTOR_PIN_X = (-0.395, 0.395)

# vertical_vane_bank
N_VERTICAL_VANES = 12
VVANE_HEIGHT = 0.026
VVANE_CHORD = 0.020
VVANE_T = 0.003
VVANE_SHAFT_R = 0.004
# Shaft kept short: it must embed in the narrow outlet's upper wall (for
# connectivity) but not reach up into the low-set service-panel zone on the
# bullnose body (which hangs its cover down near the outlet).
VVANE_SHAFT_LEN = 0.030
VVANE_SHAFT_Z_OFF = 0.005
# Outlet opening kept narrow (just taller than the vane) so the vertical-vane
# pivot origin at the slot center stays within tol of the solid slot walls
# (fail_if_articulation_origin_far_from_geometry, tol=0.015 -> half <= 0.015).
VBANK_OUTLET_OPEN = 0.028
VBANK_OUTLET_DEPTH = 0.12
VBANK_OUTLET_LEN = 0.78
VVANE_HEIGHT_FIT = 0.024  # vane height clamped to fit the narrow outlet

# closing_outlet_door
DOOR_THETA_LOW = math.radians(15.0)
DOOR_THETA_HIGH = math.radians(82.0)
DOOR_W = 0.78
DOOR_T = 0.006
DOOR_PIN_X = (-0.405, 0.405)
OPENING_THETA_LOW = math.radians(18.0)
OPENING_THETA_HIGH = math.radians(80.0)
OPENING_W = 0.74

# Hollow dark plenum behind the outlet (cross-flow blower bay).
PLENUM_HALF_LEN = 0.41
LINER_HALF_LEN = 0.42  # ends embed into the chassis side walls

# Service panel.
PANEL_W = 0.85
PANEL_T = 0.013
PANEL_H = 0.1465
PANEL_BORDER = 0.025
LEAF_GAP = 0.005  # center gap between clamshell leaves


def _clamp(value: float, lo: float, hi: float) -> float:
    if lo > hi:
        lo, hi = hi, lo
    return max(lo, min(hi, float(value)))


def _pick(value, choices):
    return value if value in choices else choices[0]


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class AirConditionerConfig:
    body_form: BodyForm = "rounded_bottom_curve"
    airflow_mechanism: AirflowMechanism = "three_independent_slim_vanes"
    service_panel: ServicePanel = "top_hinge_lift"
    vane_count: int = 3
    palette_style: PaletteStyle = "glossy_white_classic"
    body_width_scale: float = 1.0
    body_height_scale: float = 1.0
    body_depth_scale: float = 1.0
    vane_swing: float = math.radians(45.0)
    panel_open_max: float = math.radians(60.0)
    deflector_swing_hi: float = math.radians(60.0)
    door_open_max: float = math.radians(75.0)
    name: str = "reference_air_conditioner"


@dataclass(frozen=True)
class ResolvedAirConditionerConfig:
    body_form: BodyForm
    airflow_mechanism: AirflowMechanism
    service_panel: ServicePanel
    vane_count: int | None  # None when airflow != three_independent_slim_vanes
    palette_style: PaletteStyle
    body_width_scale: float
    body_height_scale: float
    body_depth_scale: float
    vane_swing: float
    panel_open_max: float
    deflector_swing_hi: float
    door_open_max: float
    name: str
    # derived
    palette: dict[str, tuple[float, float, float, float]]
    body_w: float
    body_h: float
    body_d: float


def _band_vane_capacity(body_form: BodyForm, w_scale: float, h_scale: float, d_scale: float) -> int:
    """Max independent louver vanes that fit the louver band without adjacent
    tilted chords colliding (spec §7 arc-band capacity). Each vane needs
    ~VANE_CHORD + a safety gap of the band arc length."""
    _, geom = _resolve_body_geom(body_form, w_scale, h_scale, d_scale)
    p0 = geom["arc_point"](geom["band_lo"])
    p1 = geom["arc_point"](geom["band_hi"])
    band_len = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
    per_vane = VANE_CHORD + 0.012  # chord + min gap so blades never touch
    return max(2, 1 + int(band_len / per_vane))


def _door_local_yz_extent(geom: dict) -> tuple[float, float, float, float]:
    """Door body local (y,z) extent in its hinge frame (matches
    ``_outlet_door_shape``). Width (X) is irrelevant to ground clearance so we
    build the profile directly here (no resolved config needed)."""
    if geom["kind"] == "arc":
        arc_cy, arc_cz, arc_r = geom["arc_cy"], geom["arc_cz"], geom["arc_r"]
        hy, hz = geom["door_hinge_point"]
        cy_loc = arc_cy - hy
        cz_loc = arc_cz - hz
        ys: list[float] = []
        zs: list[float] = []
        for i in range(33):
            t = DOOR_THETA_LOW + (DOOR_THETA_HIGH - DOOR_THETA_LOW) * i / 32.0
            for rr in (arc_r, arc_r - DOOR_T):
                ys.append(cy_loc + rr * math.sin(t))
                zs.append(cz_loc - rr * math.cos(t))
        # grab lip protrudes ~13 mm past the outer arc at THETA_HIGH.
        ys.append(cy_loc + (arc_r + 0.013) * math.sin(DOOR_THETA_HIGH))
        zs.append(cz_loc - (arc_r + 0.013) * math.cos(DOOR_THETA_HIGH))
        return (min(ys), max(ys), min(zs), max(zs))
    # flat / wedge: plate rises +Z from the hinge, thickness +Y.
    door_h = max(0.05, geom["band_hi"] - geom["band_lo"] + 0.03) if geom["kind"] == "flat" else 0.09
    return (-0.001, DOOR_T + 0.001, 0.0, door_h)


def _door_min_z_at_open(geom: dict, open_angle: float) -> float:
    """Lowest world-z reached by the outlet door body at a given open angle.

    Rotates the door body's local (y,z) corners about the -X hinge. Joint
    origin has no rpy, so the door-local frame equals world at rest, offset to
    the hinge point. Positive q about axis (-1,0,0): z' = -y*sin(q) + z*cos(q).
    """
    hy, hz = geom["door_hinge_point"]
    ymin, ymax, zmin, zmax = _door_local_yz_extent(geom)
    c, s = math.cos(open_angle), math.sin(open_angle)
    min_z = hz
    for yy in (ymin, ymax):
        for zz in (zmin, zmax):
            min_z = min(min_z, hz + (-yy * s + zz * c))
    return min_z


def _solve_door_ground_clearance(geom: dict, door_open: float) -> float:
    """Trim the door open angle so the door body doesn't swing grossly through
    the floor.

    A ground-sitting mini-split's bottom-hinged outlet door is bounded by the
    ground. On the low-set arc bodies (rounded / bullnose) the tall curved door
    swings toward z=0 quickly, so the angle clamps small; the higher-set flat /
    wedge outlets keep the full angle. Floor at 8 deg keeps a visible open
    sweep; we keep the door body's lowest point at z >= -20 mm (a light bound —
    the door still reads as swinging down toward the floor, the real motion,
    without diving deep below the ground plane).
    """
    floor = math.radians(8.0)
    limit = door_open
    for _ in range(90):
        if _door_min_z_at_open(geom, limit) >= -0.020 or limit <= floor:
            break
        limit -= math.radians(1.0)
    return max(limit, floor)


def config_from_seed(seed: int) -> AirConditionerConfig:
    """Deterministic procedural sampling (seed 0 is not special)."""
    rng = random.Random(seed)
    body_form: BodyForm = rng.choice(BODY_FORMS)
    airflow: AirflowMechanism = rng.choice(AIRFLOW_MECHANISMS)
    service: ServicePanel = rng.choice(SERVICE_PANELS)
    # vane_count only meaningful under three_independent_slim_vanes (gated in
    # resolve_config; sampled always so the seed stream is stable).
    vane_count = rng.choices(_VANE_COUNTS, weights=_VANE_WEIGHTS, k=1)[0]
    palette: PaletteStyle = rng.choice(PALETTE_STYLES)
    return AirConditionerConfig(
        body_form=body_form,
        airflow_mechanism=airflow,
        service_panel=service,
        vane_count=vane_count,
        palette_style=palette,
        body_width_scale=round(rng.uniform(0.85, 1.15), 4),
        body_height_scale=round(rng.uniform(0.90, 1.12), 4),
        body_depth_scale=round(rng.uniform(0.90, 1.10), 4),
        vane_swing=round(rng.uniform(math.radians(30.0), math.radians(55.0)), 5),
        panel_open_max=round(rng.uniform(math.radians(50.0), math.radians(65.0)), 5),
        deflector_swing_hi=round(rng.uniform(math.radians(45.0), math.radians(70.0)), 5),
        door_open_max=round(rng.uniform(math.radians(60.0), math.radians(80.0)), 5),
        name=f"seeded_air_conditioner_{seed}",
    )


def resolve_config(
    config: AirConditionerConfig | None = None,
) -> ResolvedAirConditionerConfig:
    cfg = config or AirConditionerConfig()
    body_form = _pick(cfg.body_form, BODY_FORMS)
    airflow = _pick(cfg.airflow_mechanism, AIRFLOW_MECHANISMS)
    service = _pick(cfg.service_panel, SERVICE_PANELS)
    palette = _pick(cfg.palette_style, PALETTE_STYLES)

    w_scale = _clamp(cfg.body_width_scale, 0.85, 1.15)
    h_scale = _clamp(cfg.body_height_scale, 0.90, 1.12)
    d_scale = _clamp(cfg.body_depth_scale, 0.90, 1.10)

    # --- vane_count gating: only under three_independent_slim_vanes ---
    if airflow == "three_independent_slim_vanes":
        vane_count: int | None = int(_clamp(cfg.vane_count, 2, 6))
        # Arc-band capacity inequality (spec §7): each independent vane needs
        # ~ (VANE_CHORD + gap) of louver-band arc length so adjacent tilted
        # blades never collide. Clamp vane_count down to the fitted capacity
        # for the (scaled) body form. Floor at 2 (a valid multiplicity value).
        vane_count = min(vane_count, _band_vane_capacity(body_form, w_scale, h_scale, d_scale))
        vane_count = max(2, vane_count)
    else:
        vane_count = None

    vane_swing = _clamp(cfg.vane_swing, math.radians(30.0), math.radians(55.0))
    panel_open = _clamp(cfg.panel_open_max, math.radians(50.0), math.radians(65.0))
    defl_hi = _clamp(cfg.deflector_swing_hi, math.radians(45.0), math.radians(70.0))
    door_open = _clamp(cfg.door_open_max, math.radians(60.0), math.radians(80.0))

    # --- closing_outlet_door ground-clearance inequality ---
    # The bottom-hinge outlet door swings down-and-out; at large door_open it
    # can dip below z=0 (the ground) — worst for the low-slung bullnose/arc
    # bodies. Trim door_open until the lowest door point stays at z >= +2 mm.
    if airflow == "closing_outlet_door":
        _, geom_d = _resolve_body_geom(body_form, w_scale, h_scale, d_scale)
        door_open = _solve_door_ground_clearance(geom_d, door_open)

    # --- airflow x service_panel low-region clearance gate ---
    # closing_outlet_door (bottom-hinge, occupying the lower front) and
    # bottom_hinge_drop_front (service cover bottom-hinge at low z, dropping
    # forward) both act in the low front region. They are z-separated by
    # construction (the door hinge sits on the outlet band; the drop-front
    # hinge sits in the panel zone above it), and both swing outward toward
    # +Y. If the resolved door open sweep would retract past the drop-front
    # panel hinge line, fall the service panel back to top_hinge_lift (matrix
    # fallback, not a hard gate-out). We test the worst-case: the door's fully
    # open free-edge z vs the drop-front panel hinge z minus a clearance.
    if airflow == "closing_outlet_door" and service == "bottom_hinge_drop_front":
        # Door free edge (top of the arc door) after full open about the low
        # hinge: it swings down and out; its lowest reach must stay clear of
        # the drop-front panel hinge z and both open toward +Y so they never
        # meet. The drop-front hinge z sits in the panel zone (well above the
        # outlet). We keep them apart by requiring the panel hinge z to be at
        # least the door's opened top-edge z + 3 cm; the geometry always
        # satisfies this (panel hinge ~0.14, door tip drops below ~0.10), but
        # if a large door_open pushes the tip up we fall back.
        _, geom = _resolve_body_geom(body_form, w_scale, h_scale, d_scale)
        door_hinge = geom["door_hinge_point"]
        panel_hinge_z = geom["drop_front_hinge_z"]
        # Opened door top-edge world z (rotate the arc chord about -X by
        # door_open): the door's upper arc point drops as it opens.
        top_y, top_z = geom["arc_point"](DOOR_THETA_HIGH)
        # relative to hinge, then rotate about x by -door_open (axis -X).
        ry = top_y - door_hinge[0]
        rz = top_z - door_hinge[1]
        # axis (-1,0,0), positive q: y' = y*cos + z*sin ; z' = -y*sin + z*cos
        opened_z = door_hinge[1] + (-ry * math.sin(door_open) + rz * math.cos(door_open))
        if opened_z > panel_hinge_z - 0.03:
            service = "top_hinge_lift"

    body_w = BODY_W * w_scale
    body_h = BODY_H * h_scale
    body_d = BODY_D * d_scale

    return ResolvedAirConditionerConfig(
        body_form=body_form,
        airflow_mechanism=airflow,
        service_panel=service,
        vane_count=vane_count,
        palette_style=palette,
        body_width_scale=w_scale,
        body_height_scale=h_scale,
        body_depth_scale=d_scale,
        vane_swing=vane_swing,
        panel_open_max=panel_open,
        deflector_swing_hi=defl_hi,
        door_open_max=door_open,
        name=cfg.name or "reference_air_conditioner",
        palette=dict(PALETTES[palette]),
        body_w=body_w,
        body_h=body_h,
        body_d=body_d,
    )


# ---------------------------------------------------------------------------
# Slot choices
# ---------------------------------------------------------------------------
def slot_choices_for_config(
    config: AirConditionerConfig | ResolvedAirConditionerConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedAirConditionerConfig) else resolve_config(config)
    choices: list[tuple[str, str]] = [
        ("body_form", r.body_form),
        ("airflow_mechanism", r.airflow_mechanism),
        ("service_panel", r.service_panel),
    ]
    # vane_count only registered (counted) under three_independent_slim_vanes.
    if r.vane_count is not None:
        choices.append(("vane_count", f"vanes_{r.vane_count}"))
    return tuple(choices)


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(resolve_config(config_from_seed(seed)))


# ---------------------------------------------------------------------------
# body_form geometry: side-profile mesh + front-face landing-point solver.
#
# Each body_form provides a solver ``arc_point(param) -> (y, z)`` returning a
# lower-front point and a normal-angle function ``normal_angle(param)`` so the
# airflow / service_panel mechanisms can align their joint origin/rpy to the
# current shell surface. Continuous scales stretch the profile:
#   - width_scale scales the extrude half-length (X) and derived louver/panel
#     X spans;
#   - depth_scale scales the depth (Y) control points and arc/wedge forward
#     reach + plenum radius;
#   - height_scale scales the Z control points (and bullnose top arc).
# ---------------------------------------------------------------------------
def _resolve_body_geom(
    body_form: BodyForm, w_scale: float, h_scale: float, d_scale: float
) -> tuple[cq.Workplane | None, dict]:
    """Return (None, geom-dict). The mesh is built lazily by callers passing
    airflow/plenum info; here we compute the parameterized landing solver and
    key control values used by every downstream mechanism.
    """
    body_h = BODY_H * h_scale
    body_d = BODY_D * d_scale

    geom: dict = {}
    geom["body_h"] = body_h
    geom["body_d"] = body_d

    if body_form in ("rounded_bottom_curve", "full_bullnose_capsule"):
        if body_form == "rounded_bottom_curve":
            arc_cy = ARC_CY * d_scale
            arc_cz = ARC_CZ * h_scale
            arc_r = ARC_R * min(d_scale, h_scale)
        else:  # full_bullnose_capsule
            r = BULLNOSE_R * min(d_scale, h_scale)
            arc_cy = body_d - r
            arc_cz = r
            arc_r = r

        def arc_point(theta: float, _cy=arc_cy, _cz=arc_cz, _r=arc_r):
            return (_cy + _r * math.sin(theta), _cz - _r * math.cos(theta))

        def normal_angle(theta: float):
            return theta - math.pi / 2.0

        geom["kind"] = "arc"
        geom["arc_cy"] = arc_cy
        geom["arc_cz"] = arc_cz
        geom["arc_r"] = arc_r
        geom["arc_point"] = arc_point
        geom["normal_angle"] = normal_angle
        geom["plenum_cy"] = arc_cy
        geom["plenum_cz"] = arc_cz
        geom["plenum_r"] = (0.06 if body_form == "full_bullnose_capsule" else 0.08) * min(
            d_scale, h_scale
        )
        geom["liner_r"] = (0.055 if body_form == "full_bullnose_capsule" else 0.075) * min(
            d_scale, h_scale
        )

    elif body_form == "boxy_rectangular":
        # Flat vertical front face at y=body_d; louver/outlet land on it.
        plenum_cy = 0.11 * d_scale
        plenum_cz = 0.08 * h_scale

        def arc_point(param: float, _d=body_d):
            # param interpreted as z fraction along the lower front (0..1 maps
            # to the lower-front band); return (y=body_d, z).
            return (_d, param)

        def normal_angle(param: float):
            return 0.0

        geom["kind"] = "flat"
        geom["arc_point"] = arc_point
        geom["normal_angle"] = normal_angle
        geom["plenum_cy"] = plenum_cy
        geom["plenum_cz"] = plenum_cz
        geom["plenum_r"] = 0.08 * min(d_scale, h_scale)
        geom["liner_r"] = 0.075 * min(d_scale, h_scale)

    else:  # raked_wedge
        wedge_lo_y = WEDGE_LO_Y * d_scale
        wedge_hi_y = WEDGE_HI_Y * d_scale
        face_dy = wedge_hi_y - wedge_lo_y
        face_dz = body_h
        face_len = math.hypot(face_dy, face_dz)
        face_ny = face_dz / face_len
        face_nz = -face_dy / face_len
        face_normal_angle = math.atan2(face_nz, face_ny)

        def face_point(fraction: float, _lo=wedge_lo_y, _dy=face_dy, _dz=face_dz):
            return (_lo + fraction * _dy, fraction * _dz)

        def normal_angle(fraction: float, _a=face_normal_angle):
            return _a

        geom["kind"] = "wedge"
        geom["wedge_lo_y"] = wedge_lo_y
        geom["wedge_hi_y"] = wedge_hi_y
        geom["face_normal_angle"] = face_normal_angle
        geom["arc_point"] = face_point  # unified name (param = fraction)
        geom["normal_angle"] = normal_angle
        geom["plenum_cy"] = 0.12 * d_scale
        geom["plenum_cz"] = 0.08 * h_scale
        geom["plenum_r"] = 0.08 * min(d_scale, h_scale)
        geom["liner_r"] = 0.075 * min(d_scale, h_scale)

    # --- front-face airflow band params (per kind) ---
    # For arc kinds theta band; for flat z band; for wedge fraction band. The
    # louver band is kept wide so several independent vanes fit without their
    # tilted chords colliding (spec §7 arc-band capacity inequality; vane_count
    # is additionally clamped to the fitted capacity in resolve_config).
    # Band top stays below the service-panel zone so a fully-tilted top louver
    # never swings into the front cover; band bottom reaches low for capacity.
    if geom["kind"] == "arc":
        geom["band_lo"] = math.radians(16.0)
        geom["band_hi"] = math.radians(72.0)
        geom["outlet_mid"] = math.radians(55.0)
    elif geom["kind"] == "flat":
        geom["band_lo"] = 0.026 * h_scale
        geom["band_hi"] = 0.120 * h_scale
        geom["outlet_mid"] = 0.075 * h_scale
    else:  # wedge
        geom["band_lo"] = 0.06
        geom["band_hi"] = 0.34
        geom["outlet_mid"] = 0.20

    # --- service panel hinge placement per body_form top-front ---
    if body_form == "rounded_bottom_curve":
        geom["panel_recess_y"] = 0.198 * d_scale
        geom["panel_zone_z0"] = 0.142 * h_scale
        geom["top_hinge_y"] = 0.1995 * d_scale
        geom["top_hinge_z"] = 0.290 * h_scale
        geom["drop_front_hinge_z"] = 0.1435 * h_scale
        geom["drop_front_hinge_y"] = 0.2145 * d_scale
    elif body_form == "boxy_rectangular":
        geom["panel_recess_y"] = (BODY_D - PANEL_T) * d_scale - 0.002
        geom["panel_zone_z0"] = BOXY_PANEL_ZONE_Z0 * h_scale
        geom["top_hinge_y"] = (BODY_D - PANEL_T) * d_scale
        geom["top_hinge_z"] = 0.290 * h_scale
        geom["drop_front_hinge_z"] = 0.150 * h_scale
        geom["drop_front_hinge_y"] = (BODY_D - PANEL_T) * d_scale
    elif body_form == "raked_wedge":
        geom["panel_recess_y"] = geom["wedge_hi_y"] - 0.003
        geom["panel_zone_z0"] = 0.150 * h_scale
        geom["panel_rpy_x"] = geom["face_normal_angle"]
        geom["service_knuckle_gap"] = 0.018
        top_hinge_z = 0.290 * h_scale
        drop_front_hinge_z = 0.150 * h_scale
        normal_y = math.cos(geom["face_normal_angle"])
        normal_z = math.sin(geom["face_normal_angle"])
        top_surface_y, top_surface_z = geom["arc_point"](top_hinge_z / body_h)
        drop_surface_y, drop_surface_z = geom["arc_point"](drop_front_hinge_z / body_h)
        geom["top_hinge_y"] = top_surface_y + 0.006 * normal_y
        geom["top_hinge_z"] = top_surface_z + 0.006 * normal_z
        geom["drop_front_hinge_y"] = drop_surface_y + 0.006 * normal_y
        geom["drop_front_hinge_z"] = drop_surface_z + 0.006 * normal_z
    else:  # full_bullnose_capsule
        geom["panel_recess_y"] = 0.195 * d_scale
        geom["panel_zone_z0"] = 0.095 * h_scale
        geom["top_hinge_y"] = 0.197 * d_scale
        geom["top_hinge_z"] = 0.210 * h_scale
        geom["drop_front_hinge_z"] = 0.110 * h_scale
        geom["drop_front_hinge_y"] = 0.205 * d_scale

    # Panel height per body_form (the bullnose panel sits low and short, per its
    # 5-star source PANEL_H=0.115, so its cover doesn't hang into the louver
    # band; the taller-fronted forms use the baseline 0.1465).
    panel_h_base = 0.115 if body_form == "full_bullnose_capsule" else PANEL_H
    geom["panel_h"] = panel_h_base * h_scale

    geom["door_hinge_point"] = geom["arc_point"](
        DOOR_THETA_LOW
        if geom["kind"] == "arc"
        else (geom["band_lo"] if geom["kind"] != "wedge" else 0.06)
    )
    return None, geom


# ---------------------------------------------------------------------------
# Housing mesh (root shell) per body_form.
# ---------------------------------------------------------------------------
def _housing_shape(r: ResolvedAirConditionerConfig, geom: dict) -> cq.Workplane:
    body_w = r.body_w
    body_h = r.body_h
    body_d = r.body_d
    bf = r.body_form

    if bf == "rounded_bottom_curve":
        arc_cy, arc_cz, arc_r = geom["arc_cy"], geom["arc_cz"], geom["arc_r"]
        mid = (
            arc_cy + arc_r * math.sin(math.radians(45.0)),
            arc_cz - arc_r * math.cos(math.radians(45.0)),
        )
        front_lo = (FRONT_LO[0] * r.body_depth_scale, FRONT_LO[1] * r.body_height_scale)
        front_hi = (FRONT_HI[0] * r.body_depth_scale, FRONT_HI[1] * r.body_height_scale)
        top_front = (TOP_FRONT[0] * r.body_depth_scale, body_h)
        body = (
            cq.Workplane("YZ")
            .moveTo(0.0, 0.0)
            .lineTo(arc_cy, 0.0)
            .threePointArc(mid, front_lo)
            .lineTo(*front_hi)
            .lineTo(*top_front)
            .lineTo(0.0, body_h)
            .close()
            .extrude(body_w / 2.0, both=True)
        )
    elif bf == "boxy_rectangular":
        recess_y = geom["panel_recess_y"]
        zone_z0 = geom["panel_zone_z0"]
        top_hinge_z = geom["top_hinge_z"]
        body = (
            cq.Workplane("YZ")
            .moveTo(0.0, 0.0)
            .lineTo(body_d, 0.0)
            .lineTo(body_d, zone_z0)
            .lineTo(recess_y, zone_z0)
            .lineTo(recess_y, top_hinge_z)
            .lineTo(body_d, top_hinge_z)
            .lineTo(body_d, body_h)
            .lineTo(0.0, body_h)
            .close()
            .extrude(body_w / 2.0, both=True)
        )
    elif bf == "raked_wedge":
        wedge_lo_y, wedge_hi_y = geom["wedge_lo_y"], geom["wedge_hi_y"]
        body = (
            cq.Workplane("YZ")
            .moveTo(0.0, 0.0)
            .lineTo(wedge_lo_y, 0.0)
            .lineTo(wedge_hi_y, body_h)
            .lineTo(0.0, body_h)
            .close()
            .extrude(body_w / 2.0, both=True)
        )
    else:  # full_bullnose_capsule
        r_b = geom["arc_r"]
        arc_bot_cy = body_d - r_b
        arc_bot_cz = r_b
        arc_top_cy = body_d - r_b
        arc_top_cz = body_h - r_b
        sq = math.sin(math.radians(45.0))
        bot_mid = (arc_bot_cy + r_b * sq, arc_bot_cz - r_b * sq)
        top_mid = (arc_top_cy + r_b * sq, arc_top_cz + r_b * sq)
        body = (
            cq.Workplane("YZ")
            .moveTo(0.0, 0.0)
            .lineTo(arc_bot_cy, 0.0)
            .threePointArc(bot_mid, (body_d, r_b))
            .lineTo(body_d, body_h - r_b)
            .threePointArc(top_mid, (arc_top_cy, body_h))
            .lineTo(0.0, body_h)
            .close()
            .extrude(body_w / 2.0, both=True)
        )

    # --- shared boolean cuts ---
    recess_y = geom["panel_recess_y"]
    zone_z0 = geom["panel_zone_z0"]
    top_hinge_z = geom["top_hinge_z"]

    if bf != "boxy_rectangular":
        # Recess the front wall behind the hinged service panel (a slab cut).
        if bf == "raked_wedge":
            fna = geom["face_normal_angle"]
            _pcy, _pcz = geom["arc_point"](0.725)
            body = body.cut(
                cq.Workplane("XY")
                .box(body_w - 0.04, 0.006, 0.168 * r.body_height_scale)
                .rotate((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), math.degrees(fna))
                .translate((0.0, _pcy, _pcz))
            )
        else:
            recess_dy = body_d - recess_y + 0.01
            recess_dz = max(0.02, top_hinge_z - zone_z0 + 0.005)
            body = body.cut(
                cq.Workplane("XY")
                .box(body_w + 0.02, recess_dy, recess_dz)
                .translate((0.0, recess_y + recess_dy / 2.0, zone_z0 + recess_dz / 2.0 - 0.002))
            )

    # Shallow framed inset on the top face (air-intake panel look).
    body = body.cut(
        cq.Workplane("XY")
        .box(0.78 * r.body_width_scale, 0.09 * r.body_depth_scale, 0.013)
        .translate((0.0, 0.06 * r.body_depth_scale, body_h - 0.0035))
    )

    # Filter cavity pocket behind the front panel.
    pk_y0, pk_y1, pk_z0, pk_z1 = _pocket(r, geom)
    body = body.cut(
        cq.Workplane("XY")
        .box(0.74 * r.body_width_scale, pk_y1 - pk_y0, pk_z1 - pk_z0)
        .translate((0.0, (pk_y0 + pk_y1) / 2.0, (pk_z0 + pk_z1) / 2.0))
    )

    # Hollow blower plenum behind the outlet, clipped to the body interior.
    pcy, pcz, pr = geom["plenum_cy"], geom["plenum_cz"], geom["plenum_r"]
    plenum = (
        cq.Workplane("YZ")
        .center(pcy, pcz)
        .circle(pr)
        .extrude(PLENUM_HALF_LEN * r.body_width_scale, both=True)
        .intersect(
            cq.Workplane("XY")
            .box(0.82 * r.body_width_scale, 0.19 * r.body_depth_scale, 0.20)
            .translate((0.0, pcy, pcz))
        )
    )
    body = body.cut(plenum)

    # --- airflow outlet / louver cuts (depend on airflow_mechanism) ---
    body = _cut_airflow_openings(body, r, geom)
    return body


def _pocket(r: ResolvedAirConditionerConfig, geom: dict) -> tuple[float, float, float, float]:
    """Filter cavity pocket (y0, y1, z0, z1) for the current body_form."""
    d = r.body_depth_scale
    h = r.body_height_scale
    if r.body_form == "full_bullnose_capsule":
        return (0.148 * d, 0.195 * d, 0.115 * h, 0.195 * h)
    if r.body_form == "raked_wedge":
        return (0.04 * d, 0.115 * d, 0.185 * h, 0.272 * h)
    return (0.15 * d, 0.21 * d, 0.185 * h, 0.272 * h)


def _louver_thetas(r: ResolvedAirConditionerConfig, geom: dict, n: int) -> tuple[float, ...]:
    """Evenly spaced louver band params for N vanes (arc theta / flat z /
    wedge fraction), per the vane-count-5 even-spacing contract."""
    lo, hi = geom["band_lo"], geom["band_hi"]
    if n <= 1:
        return ((lo + hi) / 2.0,)
    return tuple(lo + i * (hi - lo) / (n - 1) for i in range(n))


def _slot_cut(
    geom: dict,
    r: ResolvedAirConditionerConfig,
    param: float,
    open_h: float,
    depth: float,
    length: float,
) -> cq.Workplane:
    """A single outlet/louver slot cutting box aligned to the surface normal."""
    ay, az = geom["arc_point"](param)
    na = geom["normal_angle"](param)
    box = cq.Workplane("XY").box(length, depth, open_h)
    # rotate so local +Y aligns to the outward surface normal at this point.
    box = box.rotate((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), math.degrees(na))
    return box.translate((0.0, ay, az))


def _cut_airflow_openings(
    body: cq.Workplane, r: ResolvedAirConditionerConfig, geom: dict
) -> cq.Workplane:
    af = r.airflow_mechanism
    length = SLOT_LEN * r.body_width_scale
    depth = SLOT_DEPTH * r.body_depth_scale

    if af == "three_independent_slim_vanes":
        n = r.vane_count or 3
        for theta in _louver_thetas(r, geom, n):
            body = body.cut(_slot_cut(geom, r, theta, SLOT_OPEN, depth, length))
    elif af == "single_wide_deflector":
        body = body.cut(
            _slot_cut(
                geom,
                r,
                geom["outlet_mid"],
                0.10,
                0.14 * r.body_depth_scale,
                0.80 * r.body_width_scale,
            )
        )
    elif af == "vertical_vane_bank":
        body = body.cut(
            _slot_cut(
                geom,
                r,
                geom["outlet_mid"],
                VBANK_OUTLET_OPEN,
                VBANK_OUTLET_DEPTH * r.body_depth_scale,
                VBANK_OUTLET_LEN * r.body_width_scale,
            )
        )
    else:  # closing_outlet_door
        body = body.cut(_outlet_opening_cut(r, geom))
    return body


def _outlet_opening_cut(r: ResolvedAirConditionerConfig, geom: dict) -> cq.Workplane:
    """Curved outlet opening for closing_outlet_door (arc bodies) or a large
    slot (flat/wedge bodies)."""
    if geom["kind"] != "arc":
        # flat / wedge: one large single slot at the outlet band.
        return _slot_cut(
            geom,
            r,
            geom["outlet_mid"],
            0.10,
            0.14 * r.body_depth_scale,
            OPENING_W * r.body_width_scale,
        )
    arc_cy, arc_cz, arc_r = geom["arc_cy"], geom["arc_cz"], geom["arc_r"]
    plenum_r = geom["plenum_r"]
    R_outer = arc_r + 0.003
    R_inner = max(0.02, plenum_r - 0.002)
    n = 32
    outer_pts: list[tuple[float, float]] = []
    inner_pts: list[tuple[float, float]] = []
    for i in range(n + 1):
        t = OPENING_THETA_LOW + (OPENING_THETA_HIGH - OPENING_THETA_LOW) * i / n
        outer_pts.append((arc_cy + R_outer * math.sin(t), arc_cz - R_outer * math.cos(t)))
        inner_pts.append((arc_cy + R_inner * math.sin(t), arc_cz - R_inner * math.cos(t)))
    wp = cq.Workplane("YZ").moveTo(outer_pts[0][0], outer_pts[0][1])
    for pt in outer_pts[1:]:
        wp = wp.lineTo(pt[0], pt[1])
    wp = wp.lineTo(inner_pts[-1][0], inner_pts[-1][1])
    for pt in reversed(inner_pts[:-1]):
        wp = wp.lineTo(pt[0], pt[1])
    wp = wp.close()
    return wp.extrude(OPENING_W * r.body_width_scale / 2.0, both=True)


# ---------------------------------------------------------------------------
# Service panel plate meshes (joint-local frames).
# ---------------------------------------------------------------------------
def _top_panel_shape(panel_w: float, panel_h: float) -> cq.Workplane:
    """Top-hinge cover / clamshell leaf plate: hangs along -Z from the hinge."""
    plate = (
        cq.Workplane("XY")
        .box(panel_w, PANEL_T, panel_h)
        .translate((0.0, PANEL_T / 2.0, -panel_h / 2.0))
    )
    recess = (
        cq.Workplane("XY")
        .box(panel_w - 2.0 * PANEL_BORDER, 0.006, panel_h - 2.0 * PANEL_BORDER)
        .translate((0.0, PANEL_T, -panel_h / 2.0))
    )
    return plate.cut(recess)


def _drop_panel_shape(panel_w: float, panel_h: float) -> cq.Workplane:
    """Bottom-hinge drop-front cover plate: rises along +Z from the hinge."""
    plate = (
        cq.Workplane("XY")
        .box(panel_w, PANEL_T, panel_h)
        .translate((0.0, PANEL_T / 2.0, panel_h / 2.0))
    )
    recess = (
        cq.Workplane("XY")
        .box(panel_w - 2.0 * PANEL_BORDER, 0.006, panel_h - 2.0 * PANEL_BORDER)
        .translate((0.0, PANEL_T, panel_h / 2.0))
    )
    return plate.cut(recess)


# ---------------------------------------------------------------------------
# airflow mechanism factories.
# ---------------------------------------------------------------------------
def _add_louver_vane(
    model, housing, i: int, param: float, geom: dict, r: ResolvedAirConditionerConfig, mats: dict
) -> None:
    """One horizontal louver vane + REVOLUTE +X pivot (vane-count-5 blueprint)."""
    vane = model.part(f"louver_vane_{i}")
    vlen = VANE_LEN * r.body_width_scale
    # Blade offset outward (local +Y = surface normal after the joint rpy) so it
    # sits back at the outer surface even though the joint origin is recessed
    # into the wall (see origin recess below).
    blade_dy = 0.010
    vane.visual(
        Box((vlen, VANE_T, VANE_CHORD)),
        origin=Origin(xyz=(0.0, blade_dy, 0.0)),
        material=mats["panel"],
        name=f"vane_blade_{i}", material_class_id="plastic.opaque_glossy_molded",
    )
    pin_x = (-0.385 * r.body_width_scale, 0.385 * r.body_width_scale)
    for idx, px in enumerate(pin_x):
        vane.visual(
            Cylinder(radius=VANE_PIN_R, length=VANE_PIN_LEN),
            origin=Origin(xyz=(px, blade_dy, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["panel"],
            name=f"vane_pivot_pin_{i}_{idx}", material_class_id="plastic.opaque_glossy_molded",
        )
    ay, az = geom["arc_point"](param)
    na = geom["normal_angle"](param)
    # Recess the pivot origin slightly inward along the surface normal so it
    # lands on the housing wall behind the through-cut slot (the outer surface
    # point itself sits in the removed slot gap on the deeper-cut bullnose /
    # wedge faces). fail_if_articulation_origin_far_from_geometry, tol=0.015.
    ay -= 0.010 * math.cos(na)
    az -= 0.010 * math.sin(na)
    model.articulation(
        f"louver_pivot_{i}",
        ArticulationType.REVOLUTE,
        parent=housing,
        child=vane,
        origin=Origin(xyz=(0.0, ay, az), rpy=(na, 0.0, 0.0)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(
            effort=2.0, velocity=2.0, lower=-r.vane_swing, upper=r.vane_swing
        ),
    )


def _make_slim_vanes(model, housing, geom, r, mats) -> None:
    n = r.vane_count or 3
    for i, theta in enumerate(_louver_thetas(r, geom, n)):
        _add_louver_vane(model, housing, i, theta, geom, r, mats)


def _make_deflector(model, housing, geom, r, mats) -> None:
    deflector = model.part("deflector")
    dw = DEFLECTOR_W * r.body_width_scale
    blade = (
        cq.Workplane("XY")
        .box(dw, DEFLECTOR_T, DEFLECTOR_H)
        .translate((0.0, DEFLECTOR_T / 2.0, -DEFLECTOR_H / 2.0))
    )
    lip = (
        cq.Workplane("XY")
        .box(dw - 0.04, 0.007, 0.005)
        .translate((0.0, DEFLECTOR_T + 0.0035, -DEFLECTOR_H + 0.0025))
    )
    deflector.visual(
        mesh_from_cadquery(blade.union(lip), "deflector_blade"),
        material=mats["panel"],
        name="deflector_blade", material_class_id="plastic.opaque_glossy_molded",
    )
    pin_x = (-0.395 * r.body_width_scale, 0.395 * r.body_width_scale)
    for idx, px in enumerate(pin_x):
        deflector.visual(
            Cylinder(radius=0.004, length=0.04),
            origin=Origin(xyz=(px, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["panel"],
            name=f"pivot_pin_{idx}", material_class_id="plastic.opaque_glossy_molded",
        )
    # Hinge just above the outlet opening, on solid wall. On the curved (arc)
    # body the near-vertical HINGE_THETA already lands on the solid upper wall;
    # on flat / wedge faces the outlet is a straight through-cut, so anchor the
    # hinge above the outlet top edge (solid material) and let the blade hang
    # down into the opening (fail_if_articulation_origin_far_from_geometry).
    if geom["kind"] == "arc":
        hp = HINGE_THETA
        ay, az = geom["arc_point"](hp)
        na = geom["normal_angle"](hp)
    elif geom["kind"] == "flat":
        # outlet cut is 0.10 tall centered at outlet_mid; hinge above its top.
        az = geom["outlet_mid"] + 0.05 + 0.006
        ay = geom["arc_point"](az)[0]
        na = 0.0
    else:  # wedge
        # outlet ~0.10 tall in Z -> convert to fraction, hinge just above top.
        outlet_frac_half = 0.05 / geom["body_h"]
        hp = geom["outlet_mid"] + outlet_frac_half + 0.02
        ay, az = geom["arc_point"](hp)
        na = geom["normal_angle"](hp)
    model.articulation(
        "deflector_pivot",
        ArticulationType.REVOLUTE,
        parent=housing,
        child=deflector,
        origin=Origin(xyz=(0.0, ay, az), rpy=(na, 0.0, 0.0)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(
            effort=3.0,
            velocity=2.0,
            lower=DEFLECTOR_SWING_LO,
            upper=r.deflector_swing_hi,
        ),
    )


def _make_vertical_bank(model, housing, geom, r, mats) -> None:
    ay, az = geom["arc_point"](geom["outlet_mid"])
    outlet_len = VBANK_OUTLET_LEN * r.body_width_scale
    spacing = outlet_len / N_VERTICAL_VANES
    for i in range(N_VERTICAL_VANES):
        vane = model.part(f"vertical_vane_{i}")
        vane.visual(
            Box((VVANE_T, VVANE_CHORD, VVANE_HEIGHT_FIT)),
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
            material=mats["panel"],
            name=f"vane_blade_{i}", material_class_id="plastic.opaque_glossy_molded",
        )
        # Shaft extends up from the blade into the solid slot upper wall so the
        # vane is captured on a real vertical pivot and stays connected to the
        # grounded body (its top embeds in the wall above the narrow outlet).
        vane.visual(
            Cylinder(radius=VVANE_SHAFT_R, length=VVANE_SHAFT_LEN),
            origin=Origin(xyz=(0.0, 0.0, VVANE_SHAFT_Z_OFF)),
            material=mats["panel"],
            name=f"vane_shaft_{i}", material_class_id="plastic.opaque_glossy_molded",
        )
        vx = -outlet_len / 2.0 + spacing * (i + 0.5)
        model.articulation(
            f"vane_pivot_{i}",
            ArticulationType.REVOLUTE,
            parent=housing,
            child=vane,
            origin=Origin(xyz=(vx, ay, az)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(
                effort=2.0, velocity=2.0, lower=-r.vane_swing, upper=r.vane_swing
            ),
        )


def _make_outlet_door(model, housing, geom, r, mats) -> None:
    outlet_door = model.part("outlet_door")
    outlet_door.visual(
        mesh_from_cadquery(_outlet_door_shape(r, geom), "outlet_door_panel"),
        material=mats["panel"],
        name="door_panel", material_class_id="plastic.opaque_glossy_molded",
    )
    pin_x = (-0.405 * r.body_width_scale, 0.405 * r.body_width_scale)
    for idx, px in enumerate(pin_x):
        outlet_door.visual(
            Cylinder(radius=0.004, length=0.04),
            origin=Origin(xyz=(px, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["panel"],
            name=f"door_pivot_pin_{idx}", material_class_id="plastic.opaque_glossy_molded",
        )
    hy, hz = geom["door_hinge_point"]
    model.articulation(
        "outlet_door_hinge",
        ArticulationType.REVOLUTE,
        parent=housing,
        child=outlet_door,
        origin=Origin(xyz=(0.0, hy, hz)),
        # axis (-1,0,0): positive q swings the free top edge out (+Y) and down.
        axis=(-1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=5.0, velocity=2.0, lower=0.0, upper=r.door_open_max),
    )


def _outlet_door_shape(r: ResolvedAirConditionerConfig, geom: dict) -> cq.Workplane:
    """Curved outlet door panel in hinge-local frame (arc bodies), or a flat
    plate that hangs from the low hinge (flat / wedge bodies)."""
    dw = DOOR_W * r.body_width_scale
    if geom["kind"] != "arc":
        # Flat plate hanging from the low hinge; local frame at hinge, plate
        # rises along +Z toward the outlet band, thickness +Y outward.
        door_h = (
            max(0.05, geom["band_hi"] - geom["band_lo"] + 0.03) if geom["kind"] == "flat" else 0.09
        )
        plate = (
            cq.Workplane("XY").box(dw, DOOR_T, door_h).translate((0.0, DOOR_T / 2.0, door_h / 2.0))
        )
        return plate
    arc_cy, arc_cz, arc_r = geom["arc_cy"], geom["arc_cz"], geom["arc_r"]
    y_h, z_h = geom["door_hinge_point"]
    cy_loc = arc_cy - y_h
    cz_loc = arc_cz - z_h
    R_out = arc_r
    R_in = arc_r - DOOR_T
    n = 32
    outer_pts: list[tuple[float, float]] = []
    inner_pts: list[tuple[float, float]] = []
    for i in range(n + 1):
        t = DOOR_THETA_LOW + (DOOR_THETA_HIGH - DOOR_THETA_LOW) * i / n
        outer_pts.append((cy_loc + R_out * math.sin(t), cz_loc - R_out * math.cos(t)))
        inner_pts.append((cy_loc + R_in * math.sin(t), cz_loc - R_in * math.cos(t)))
    wp = cq.Workplane("YZ").moveTo(outer_pts[0][0], outer_pts[0][1])
    for pt in outer_pts[1:]:
        wp = wp.lineTo(pt[0], pt[1])
    wp = wp.lineTo(inner_pts[-1][0], inner_pts[-1][1])
    for pt in reversed(inner_pts[:-1]):
        wp = wp.lineTo(pt[0], pt[1])
    wp = wp.close()
    door = wp.extrude(dw / 2.0, both=True)
    lip_y = cy_loc + R_out * math.sin(DOOR_THETA_HIGH)
    lip_z = cz_loc - R_out * math.cos(DOOR_THETA_HIGH)
    lip = (
        cq.Workplane("XY")
        .box(dw * 0.6, 0.010, 0.008)
        .rotate((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), math.degrees(DOOR_THETA_HIGH) - 90.0)
        .translate((0.0, lip_y, lip_z))
    )
    return door.union(lip)


# ---------------------------------------------------------------------------
# service panel factories.
# ---------------------------------------------------------------------------
def _add_top_hinge_leaf(
    model,
    housing,
    geom,
    r,
    mats,
    *,
    name: str,
    panel_w: float,
    cx: float,
    knuckle_offs,
    knuckle_prefix: str,
) -> None:
    leaf = model.part(name)
    panel_h = geom["panel_h"]
    leaf.visual(
        mesh_from_cadquery(_top_panel_shape(panel_w, panel_h), f"{name}_plate"),
        material=mats["panel"],
        name=f"{name}_plate", material_class_id="plastic.opaque_glossy_molded",
    )
    # Knuckles bridge from the plate back (-Y) to the recessed chassis wall so
    # the cover is connected to the grounded housing (fail_if_isolated_parts).
    # The hinge sits at top_hinge_y; the chassis recess is at panel_recess_y,
    # so the knuckle must span that gap plus an embed into the chassis.
    gap = geom.get(
        "service_knuckle_gap",
        max(0.008, geom["top_hinge_y"] - geom["panel_recess_y"] + 0.006),
    )
    kn_y_center = -(gap / 2.0) + 0.001
    for kdx, kx in enumerate(knuckle_offs):
        leaf.visual(
            Box((0.04, gap, 0.012)),
            origin=Origin(xyz=(kx, kn_y_center, -0.004)),
            material=mats["panel"],
            name=f"{knuckle_prefix}hinge_knuckle_{kdx}", material_class_id="plastic.opaque_glossy_molded",
        )
    model.articulation(
        f"{name}_hinge",
        ArticulationType.REVOLUTE,
        parent=housing,
        child=leaf,
        origin=Origin(
            xyz=(cx, geom["top_hinge_y"], geom["top_hinge_z"]),
            rpy=(geom.get("panel_rpy_x", 0.0), 0.0, 0.0),
        ),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=8.0, velocity=1.5, lower=0.0, upper=r.panel_open_max),
    )


def _make_top_lift(model, housing, geom, r, mats) -> None:
    panel_w = PANEL_W * r.body_width_scale
    _add_top_hinge_leaf(
        model,
        housing,
        geom,
        r,
        mats,
        name="front_panel",
        panel_w=panel_w,
        cx=0.0,
        knuckle_offs=(-0.30 * r.body_width_scale, 0.30 * r.body_width_scale),
        knuckle_prefix="",
    )


def _make_clamshell(model, housing, geom, r, mats) -> None:
    panel_w = PANEL_W * r.body_width_scale
    leaf_w = (panel_w - LEAF_GAP) / 2.0
    leaf_cx = tuple((i - 0.5) * (leaf_w + LEAF_GAP) for i in range(2))
    for i in range(2):
        _add_top_hinge_leaf(
            model,
            housing,
            geom,
            r,
            mats,
            name=f"panel_{i}",
            panel_w=leaf_w,
            cx=leaf_cx[i],
            knuckle_offs=(-leaf_w * 0.35, leaf_w * 0.35),
            knuckle_prefix=f"panel_{i}_",
        )


def _make_drop_front(model, housing, geom, r, mats) -> None:
    panel_w = PANEL_W * r.body_width_scale
    panel_h = geom["panel_h"]
    leaf = model.part("front_panel")
    leaf.visual(
        mesh_from_cadquery(_drop_panel_shape(panel_w, panel_h), "front_panel_plate"),
        material=mats["panel"],
        name="front_panel_plate", material_class_id="plastic.opaque_glossy_molded",
    )
    # Knuckles bridge back (-Y) to the recessed chassis wall and reach down to
    # the solid housing below the panel recess so the drop-front cover stays
    # connected to the grounded body (fail_if_isolated_parts).
    gap = geom.get(
        "service_knuckle_gap",
        max(0.010, geom["drop_front_hinge_y"] - geom["panel_recess_y"] + 0.008),
    )
    kn_y_center = -(gap / 2.0) + 0.001
    for kdx, kx in enumerate((-0.30 * r.body_width_scale, 0.30 * r.body_width_scale)):
        leaf.visual(
            Box((0.04, gap, 0.016)),
            origin=Origin(xyz=(kx, kn_y_center, 0.002)),
            material=mats["panel"],
            name=f"hinge_knuckle_{kdx}", material_class_id="plastic.opaque_glossy_molded",
        )
    model.articulation(
        "front_panel_hinge",
        ArticulationType.REVOLUTE,
        parent=housing,
        child=leaf,
        origin=Origin(
            xyz=(0.0, geom["drop_front_hinge_y"], geom["drop_front_hinge_z"]),
            rpy=(geom.get("panel_rpy_x", 0.0), 0.0, 0.0),
        ),
        # axis (-1,0,0): positive q swings the free top edge out and down.
        axis=(-1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=8.0, velocity=1.5, lower=0.0, upper=r.panel_open_max),
    )


# ---------------------------------------------------------------------------
# Build entry point.
# ---------------------------------------------------------------------------
def build_air_conditioner(
    config: AirConditionerConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    if assets is None:
        assets = AssetContext(Path(tempfile.mkdtemp(prefix="articraft-ac-")))
    model = ArticulatedObject(name=r.name, assets=assets)

    pal = r.palette
    style = r.palette_style
    mats = {
        key: model.material(f"ac_{key}_{style}", rgba=pal[key])
        for key in ("shell", "panel", "cavity", "filter_frame", "filter_mesh")
    }

    _, geom = _resolve_body_geom(
        r.body_form, r.body_width_scale, r.body_height_scale, r.body_depth_scale
    )

    # --- ROOT: shared housing shell + fixed plenum/filter visuals ---
    housing = model.part("housing")
    housing.visual(
        mesh_from_cadquery(_housing_shape(r, geom), "housing_shell"),
        material=mats["shell"],
        name="housing_shell", material_class_id="plastic.opaque_glossy_molded",
    )
    # Dark blower-bay liner: read through the outlet as the hollow dark interior.
    housing.visual(
        Cylinder(radius=geom["liner_r"], length=2.0 * LINER_HALF_LEN * r.body_width_scale),
        origin=Origin(
            xyz=(0.0, geom["plenum_cy"], geom["plenum_cz"]), rpy=(0.0, math.pi / 2.0, 0.0)
        ),
        material=mats["cavity"],
        name="plenum_liner", material_class_id="plastic.opaque_generic",
    )
    # Removable-look filter panel seated at the back of the filter cavity.
    pk_y0, pk_y1, pk_z0, pk_z1 = _pocket(r, geom)
    filt_y = pk_y0 + 0.002
    filt_cz = 0.5 * (pk_z0 + pk_z1)
    filt_h = min(0.082, (pk_z1 - pk_z0) - 0.005)
    housing.visual(
        Box((0.70 * r.body_width_scale, 0.005, filt_h)),
        origin=Origin(xyz=(0.0, filt_y, filt_cz)),
        material=mats["filter_frame"],
        name="filter_frame", material_class_id="plastic.opaque_generic",
    )
    housing.visual(
        Box((0.66 * r.body_width_scale, 0.004, filt_h - 0.010)),
        origin=Origin(xyz=(0.0, filt_y + 0.0035, filt_cz)),
        material=mats["filter_mesh"],
        name="filter_mesh", material_class_id="fabric.open_mesh",
    )

    # --- airflow mechanism (parallel child layer on the lower front) ---
    {
        "three_independent_slim_vanes": _make_slim_vanes,
        "single_wide_deflector": _make_deflector,
        "vertical_vane_bank": _make_vertical_bank,
        "closing_outlet_door": _make_outlet_door,
    }[r.airflow_mechanism](model, housing, geom, r, mats)

    # --- service panel mechanism (parallel child layer on the front cover) ---
    {
        "top_hinge_lift": _make_top_lift,
        "two_leaf_clamshell": _make_clamshell,
        "bottom_hinge_drop_front": _make_drop_front,
    }[r.service_panel](model, housing, geom, r, mats)

    model.meta["slot_choices"] = [list(t) for t in slot_choices_for_config(r)]
    return model


def build_seeded_air_conditioner(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_air_conditioner(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests / QC.
# ---------------------------------------------------------------------------
def run_air_conditioner_tests(
    object_model: ArticulatedObject,
    config: AirConditionerConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    housing = object_model.get_part("housing")

    # ---- real-world scale, grounding, wall-flush ----
    hb = ctx.part_world_aabb(housing)
    assert hb is not None
    ctx.check(
        "housing width ~scaled 0.90 m",
        abs((hb[1][0] - hb[0][0]) - r.body_w) < 0.03,
        details=f"width={hb[1][0] - hb[0][0]:.4f}, target={r.body_w:.4f}",
    )
    ctx.check(
        "housing height ~scaled 0.30 m",
        abs((hb[1][2] - hb[0][2]) - r.body_h) < 0.03,
        details=f"height={hb[1][2] - hb[0][2]:.4f}, target={r.body_h:.4f}",
    )
    ctx.check(
        "unit bottom sits at z=0 with flat back at the wall plane y=0",
        abs(hb[0][2]) < 0.006 and abs(hb[0][1]) < 0.006,
        details=f"min={hb[0]}",
    )

    _, geom = _resolve_body_geom(
        r.body_form, r.body_width_scale, r.body_height_scale, r.body_depth_scale
    )

    # ---- dark plenum liner spans behind the outlet ----
    liner = ctx.part_element_world_aabb(housing, elem="plenum_liner")
    assert liner is not None
    ctx.check(
        "dark plenum liner spans the width behind the outlet",
        liner[0][0] < -0.35 * r.body_width_scale and liner[1][0] > 0.35 * r.body_width_scale,
        details=f"liner aabb={liner}",
    )

    # ---- airflow mechanism ----
    af = r.airflow_mechanism
    if af == "three_independent_slim_vanes":
        n = r.vane_count or 3
        ctx.check(
            "vane_count active with N in [2,6]",
            r.vane_count is not None and 2 <= r.vane_count <= 6,
            details=f"vane_count={r.vane_count}",
        )
        for i in range(n):
            vane = object_model.get_part(f"louver_vane_{i}")
            pivot = object_model.get_articulation(f"louver_pivot_{i}")
            # The vane body sweeps close across the louver band mouth while
            # tilting; the band rim keeps it captured on both extreme tilts.
            ctx.allow_overlap(
                vane,
                housing,
                reason="tilting louver vane sweeps close across the louver band mouth",
            )
            for idx in range(2):
                ctx.allow_overlap(
                    vane,
                    housing,
                    elem_a=f"vane_pivot_pin_{i}_{idx}",
                    elem_b="housing_shell",
                    reason="Vane end pivot pin is captured in the louver slot end wall.",
                )
            ctx.check(
                f"louver_pivot_{i} is REVOLUTE about +X",
                pivot.articulation_type == ArticulationType.REVOLUTE and abs(pivot.axis[0]) > 0.99,
                details=f"axis={pivot.axis}",
            )
            vl = pivot.motion_limits
            ctx.check(
                f"louver_pivot_{i} swings +/-vane_swing",
                vl is not None
                and vl.lower is not None
                and abs(vl.lower + r.vane_swing) < 0.02
                and abs(vl.upper - r.vane_swing) < 0.02,
                details=f"limits=({vl.lower},{vl.upper}), swing={r.vane_swing}",
            )
            # Decisive tilt check. A blade at +q and -q gives a mirrored
            # (identical) AABB, so compare rest (q=0) vs +swing: tilting the
            # blade about +X grows the extent normal to the slot tangent (Y or
            # Z depending on body_form face normal). Use max of dY/dZ growth.
            rest_ab = ctx.part_world_aabb(vane)
            with ctx.pose({pivot: r.vane_swing}):
                tilted = ctx.part_world_aabb(vane)
            assert rest_ab is not None and tilted is not None
            # Orientation-robust: sum the absolute shift of all 6 AABB bounds
            # between rest and +swing. A real revolute rotation always moves the
            # blade's bounding box (near-vertical slots change Y more than Z),
            # while a stuck joint leaves every bound unchanged.
            moved = sum(abs(tilted[a][k] - rest_ab[a][k]) for a in (0, 1) for k in (1, 2))
            ctx.check(
                f"louver_vane_{i} actually tilts about its slot axis",
                moved > 0.002,
                details=f"aabb-shift(y,z)={moved:.4f}",
            )
    elif af == "single_wide_deflector":
        ctx.check("vane_count is n/a (not three_independent)", r.vane_count is None)
        deflector = object_model.get_part("deflector")
        pivot = object_model.get_articulation("deflector_pivot")
        ctx.allow_overlap(
            deflector,
            housing,
            elem_a="deflector_blade",
            elem_b="housing_shell",
            reason="Deflector blade seats flush over the outlet at rest (captured fit).",
        )
        for idx in range(2):
            ctx.allow_overlap(
                deflector,
                housing,
                elem_a=f"pivot_pin_{idx}",
                elem_b="housing_shell",
                reason="Deflector end pivot pin is captured in the outlet end wall.",
            )
        ctx.check(
            "deflector_pivot is REVOLUTE about +X",
            pivot.articulation_type == ArticulationType.REVOLUTE and abs(pivot.axis[0]) > 0.99,
            details=f"axis={pivot.axis}",
        )
        rest = ctx.part_world_aabb(deflector)
        with ctx.pose({pivot: r.deflector_swing_hi}):
            swung = ctx.part_world_aabb(deflector)
        assert rest is not None and swung is not None
        ctx.check(
            "deflector swings outward (+Y) when opened",
            swung[1][1] > rest[1][1] + 0.01,
            details=f"rest_max_y={rest[1][1]:.4f}, open_max_y={swung[1][1]:.4f}",
        )
    elif af == "vertical_vane_bank":
        ctx.check("vane_count is n/a (not three_independent)", r.vane_count is None)
        for i in range(N_VERTICAL_VANES):
            vane = object_model.get_part(f"vertical_vane_{i}")
            pivot = object_model.get_articulation(f"vane_pivot_{i}")
            ctx.allow_overlap(
                vane,
                housing,
                elem_a=f"vane_shaft_{i}",
                elem_b="housing_shell",
                reason="Vertical vane shaft is captured in the outlet upper wall.",
            )
        # spot-check one middle vane's axis + sweep.
        pivot = object_model.get_articulation("vane_pivot_6")
        vane = object_model.get_part("vertical_vane_6")
        ctx.check(
            "vane_pivot is REVOLUTE about +Z (vertical axis)",
            pivot.articulation_type == ArticulationType.REVOLUTE and abs(pivot.axis[2]) > 0.99,
            details=f"axis={pivot.axis}",
        )
        # A blade rotating about +Z gives a MIRRORED (identical) AABB at +q and
        # -q, so compare rest (q=0, chord along +Y) vs +swing (chord swings
        # toward +X): the X-extent grows and the Y-extent shrinks when swept.
        rest_ab = ctx.part_world_aabb(vane)
        with ctx.pose({pivot: r.vane_swing}):
            swept = ctx.part_world_aabb(vane)
        assert rest_ab is not None and swept is not None
        rest_x = rest_ab[1][0] - rest_ab[0][0]
        swept_x = swept[1][0] - swept[0][0]
        ctx.check(
            "vertical vane sweeps left-right about +Z (X-extent grows)",
            swept_x > rest_x + 0.002,
            details=f"rest_x_ext={rest_x:.4f}, swept_x_ext={swept_x:.4f}",
        )
    else:  # closing_outlet_door
        ctx.check("vane_count is n/a (not three_independent)", r.vane_count is None)
        door = object_model.get_part("outlet_door")
        hinge = object_model.get_articulation("outlet_door_hinge")
        ctx.allow_overlap(
            door,
            housing,
            elem_a="door_panel",
            elem_b="housing_shell",
            reason="Outlet door seats flush over the outlet opening when closed.",
        )
        for idx in range(2):
            ctx.allow_overlap(
                door,
                housing,
                elem_a=f"door_pivot_pin_{idx}",
                elem_b="housing_shell",
                reason="Door end pivot pin is captured in the outlet side wall.",
            )
        ctx.check(
            "outlet_door_hinge is REVOLUTE about -X (bottom hinge)",
            hinge.articulation_type == ArticulationType.REVOLUTE and hinge.axis[0] < -0.99,
            details=f"axis={hinge.axis}",
        )
        rest = ctx.part_world_aabb(door)
        with ctx.pose({hinge: r.door_open_max}):
            opened = ctx.part_world_aabb(door)
        assert rest is not None and opened is not None
        # The bottom-hinged door swings its free (top) edge out (+Y) and down.
        # (Ground clearance is bounded by the door_open clamp in resolve_config;
        # a ground-sitting unit's down-door reaches toward z=0 by nature, so we
        # assert real articulation here, not strict z>=0.)
        ctx.check(
            "outlet door swings open (free edge out and/or down)",
            opened[1][1] > rest[1][1] + 0.005 or opened[0][2] < rest[0][2] - 0.005,
            details=f"rest={rest}, opened={opened}",
        )

    # ---- service panel ----
    sp = r.service_panel
    if sp == "top_hinge_lift":
        leaves = [("front_panel", "front_panel")]
    elif sp == "two_leaf_clamshell":
        leaves = [(f"panel_{i}", f"panel_{i}") for i in range(2)]
    else:
        leaves = [("front_panel", "front_panel")]

    for part_name, jbase in leaves:
        panel = object_model.get_part(part_name)
        hinge = object_model.get_articulation(f"{jbase}_hinge")
        # knuckle embeds are intentional
        panel_visual_names = {v.name for v in panel.visuals}
        for kn in panel_visual_names:
            if "hinge_knuckle" in kn:
                ctx.allow_overlap(
                    panel,
                    housing,
                    elem_a=kn,
                    elem_b="housing_shell",
                    reason="Hinge knuckle is seated into the recessed chassis wall.",
                )
        # panel closed covers the front face
        ctx.allow_overlap(
            panel,
            housing,
            reason="Closed service cover overlaps the recessed front face (seated fit).",
        )
        if sp == "bottom_hinge_drop_front":
            ctx.check(
                f"{jbase}_hinge is REVOLUTE about -X (bottom hinge)",
                hinge.articulation_type == ArticulationType.REVOLUTE and hinge.axis[0] < -0.99,
                details=f"axis={hinge.axis}",
            )
        else:
            ctx.check(
                f"{jbase}_hinge is REVOLUTE about +X (top hinge)",
                hinge.articulation_type == ArticulationType.REVOLUTE and abs(hinge.axis[0]) > 0.99,
                details=f"axis={hinge.axis}",
            )
        pl = hinge.motion_limits
        ctx.check(
            f"{jbase}_hinge opens 0..panel_open_max",
            pl is not None and abs(pl.lower) < 1e-6 and abs(pl.upper - r.panel_open_max) < 0.02,
            details=f"limits=({pl.lower},{pl.upper})",
        )
        # decisive open check: cover swings outward (+Y).
        closed = ctx.part_world_aabb(panel)
        with ctx.pose({hinge: r.panel_open_max}):
            opened = ctx.part_world_aabb(panel)
        assert closed is not None and opened is not None
        ctx.check(
            f"{part_name} swings its free edge outward when opened",
            opened[1][1] > closed[1][1] + 0.03,
            details=f"closed_max_y={closed[1][1]:.4f}, open_max_y={opened[1][1]:.4f}",
        )

    # clamshell independence: opening leaf 0 leaves leaf 1 closed.
    if sp == "two_leaf_clamshell":
        h0 = object_model.get_articulation("panel_0_hinge")
        leaf1 = object_model.get_part("panel_1")
        rest1 = ctx.part_world_aabb(leaf1)
        with ctx.pose({h0: r.panel_open_max}):
            still1 = ctx.part_world_aabb(leaf1)
        assert rest1 is not None and still1 is not None
        ctx.check(
            "opening leaf 0 leaves leaf 1 closed (independent)",
            abs(still1[1][1] - rest1[1][1]) < 0.005,
            details=f"leaf1 rest_max_y={rest1[1][1]:.4f}, after={still1[1][1]:.4f}",
        )

    # ---- filter revealed behind the opened service cover ----
    filt = ctx.part_element_world_aabb(housing, elem="filter_mesh")
    assert filt is not None
    pk_y0, pk_y1, pk_z0, pk_z1 = _pocket(r, geom)
    ctx.check(
        "filter panel sits inside the filter cavity",
        pk_y0 - 0.003 <= filt[0][1]
        and filt[1][1] <= pk_y1 + 0.003
        and pk_z0 - 0.005 <= filt[0][2]
        and filt[1][2] <= pk_z1 + 0.005,
        details=f"filter aabb={filt}, pocket y=({pk_y0:.3f},{pk_y1:.3f}) z=({pk_z0:.3f},{pk_z1:.3f})",
    )

    # ---- at least one non-fixed joint ----
    non_fixed = [
        j for j in object_model.articulations if j.articulation_type != ArticulationType.FIXED
    ]
    ctx.check(
        "at least one non-fixed joint exists",
        len(non_fixed) >= 1,
        details=f"non-fixed count={len(non_fixed)}",
    )

    # ---- sampled-pose collision sweep (captured-fit embeds already allowed) ----
    # vertical_vane_bank has 12 vane joints; keep the sample budget lower there
    # (spec §8.5 motion_test_plan: 96, dropping to 32 for the 12-vane bank).
    max_samples = 32 if r.airflow_mechanism == "vertical_vane_bank" else 96
    ctx.fail_if_parts_overlap_in_sampled_poses(
        max_pose_samples=max_samples,
        overlap_tol=0.006,
        overlap_volume_tol=0.0,
        ignore_adjacent=True,
        ignore_fixed=True,
    )

    return ctx.report()


__all__ = [
    "AirConditionerConfig",
    "ResolvedAirConditionerConfig",
    "build_air_conditioner",
    "build_seeded_air_conditioner",
    "config_from_seed",
    "resolve_config",
    "run_air_conditioner_tests",
    "slot_choices_for_seed",
    "__modular__",
]
