# SPDX-License-Identifier: Apache-2.0

"""Cauldron — modular procedural template (traditional cast-iron cooking pot).

Category identity: a thick-walled hollow cast-iron cooking cauldron. A hollow
revolved/lathed pot body (round belly / straight cylinder / wide shallow bowl)
carries an openable lid (lift-off PRISMATIC / rear-hinged REVOLUTE flip /
clamp-locking PRISMATIC + 2 toggle REVOLUTE) plus a handle/suspension feature
(swing bail REVOLUTE / two fixed side-loop ears / a three-legged tripod stand
the pot pendulum-hangs from). Optional cast-iron feet (N in {0, 3, 4}) circle
the pot bottom.

Three named slots + one multiplicity axis (spec ``Other_Other_cauldron.md``):

  * ``pot_form`` (3) — the ROOT ``pot_body`` mesh: rounded_belly (revolved
    bulbous wall + pedestal foot), straight_cylindrical (lathe drum), or
    wide_shallow_bowl (lathe cazo). Mesh-helper dimension; same lid/handle
    interface (rim top).
  * ``lid_mechanism`` (3) — the openable lid (>=1 non-fixed joint each):
      - lift_off_dome: PRISMATIC +Z lift-off lid.
      - hinged_flip: REVOLUTE +X rear-hinge flip lid (pot hinge lug + lid strap).
      - clamp_locking: PRISMATIC +Z lid + 2 mirrored toggle clamp REVOLUTE arms.
  * ``handle_suspension`` (3) — the grip/hang feature:
      - swing_bail: REVOLUTE +X bail loop on the lid.
      - side_loop_ears: two FIXED cast ears on the pot wall (no bail; lid moves).
      - tripod_stand: ROOT SWAP — ``tripod_hub`` becomes root with 3 FIXED legs;
        the pot REVOLUTE-pendulum-hangs from a hook via a bail arch.

  * ``leg_count`` (N in {0, 3, 4}) — cast-iron pot-bottom feet, inline pot
    visuals (Rule 1, no joint), equiangular. Gated to 0 when tripod_stand
    (the tripod's own 3 legs carry the load). Encoded in slot_choices as
    ``("leg_count", f"n{N}")``.

Continuous size/proportion/travel variation lives in ``resolve_config`` as
clamped params, never as slot candidates.

Sources (articraft_data ``picture/Other/cauldron`` 5-star pool):
  S1 parent ``f944b57b`` (rounded belly + lift-off dome + swing bail),
  S2 ``26cd72d3`` (straight cylindrical + tab legs),
  S3 ``cef6bfac`` (wide shallow bowl + revolved legs),
  S4 ``8d43806f`` (hinged flip lid), S5 ``607ffa31`` (clamp locking),
  S6 ``09d73153`` (side loop ears + FIXED legs),
  S7 ``2de73386`` (tripod stand — root swap + pendulum + bail-on-hook).

Canonical spec: ``articraft_template_authoring/specs_modular_v1/Other_Other_cauldron.md``
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
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
    mesh_from_geometry,
    tube_from_spline_points,
)

__modular__ = True

# ---------------------------------------------------------------------------
# Slot domains
# ---------------------------------------------------------------------------
PotForm = Literal["rounded_belly", "straight_cylindrical", "wide_shallow_bowl"]
LidMechanism = Literal["lift_off_dome", "hinged_flip", "clamp_locking"]
HandleSuspension = Literal["swing_bail", "side_loop_ears", "tripod_stand"]
PaletteStyle = Literal[
    "matte_black_cast_iron",
    "weathered_rust_iron",
    "seasoned_graphite",
    "enamel_red",
    "enamel_blue",
    "polished_pewter",
]

POT_FORMS: tuple[PotForm, ...] = (
    "rounded_belly",
    "straight_cylindrical",
    "wide_shallow_bowl",
)
LID_MECHANISMS: tuple[LidMechanism, ...] = (
    "lift_off_dome",
    "hinged_flip",
    "clamp_locking",
)
HANDLE_SUSPENSIONS: tuple[HandleSuspension, ...] = (
    "swing_bail",
    "side_loop_ears",
    "tripod_stand",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "matte_black_cast_iron",
    "weathered_rust_iron",
    "seasoned_graphite",
    "enamel_red",
    "enamel_blue",
    "polished_pewter",
)

# leg_count sampling domain (discrete {0, 3, 4}; weighted small per spec §8:
# N=0 high-frequency, N=3 common, N=4 long tail).
LEG_COUNTS: tuple[int, ...] = (0, 3, 4)
LEG_COUNT_WEIGHTS: tuple[float, ...] = (0.50, 0.35, 0.15)


# ---------------------------------------------------------------------------
# Material palettes. Each colorway resolves to the same named slots driving
# every .visual(material=...): body iron, lid casting, dark hardware, accent
# (wrought hardware / hooks / bail), foot iron.
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "matte_black_cast_iron": {
        "body": (0.10, 0.10, 0.11, 1.0),
        "lid": (0.13, 0.13, 0.14, 1.0),
        "dark": (0.08, 0.08, 0.09, 1.0),
        "accent": (0.17, 0.15, 0.13, 1.0),
        "foot": (0.09, 0.09, 0.10, 1.0),
    },
    "weathered_rust_iron": {
        "body": (0.40, 0.21, 0.11, 1.0),
        "lid": (0.45, 0.25, 0.14, 1.0),
        "dark": (0.28, 0.15, 0.09, 1.0),
        "accent": (0.34, 0.18, 0.10, 1.0),
        "foot": (0.30, 0.16, 0.09, 1.0),
    },
    "seasoned_graphite": {
        "body": (0.20, 0.21, 0.23, 1.0),
        "lid": (0.24, 0.25, 0.27, 1.0),
        "dark": (0.14, 0.15, 0.17, 1.0),
        "accent": (0.30, 0.31, 0.33, 1.0),
        "foot": (0.17, 0.18, 0.20, 1.0),
    },
    "enamel_red": {
        "body": (0.66, 0.12, 0.10, 1.0),
        "lid": (0.74, 0.16, 0.13, 1.0),
        "dark": (0.18, 0.18, 0.19, 1.0),
        "accent": (0.20, 0.20, 0.21, 1.0),
        "foot": (0.16, 0.16, 0.17, 1.0),
    },
    "enamel_blue": {
        "body": (0.13, 0.27, 0.50, 1.0),
        "lid": (0.16, 0.32, 0.58, 1.0),
        "dark": (0.10, 0.16, 0.26, 1.0),
        "accent": (0.20, 0.20, 0.21, 1.0),
        "foot": (0.12, 0.18, 0.30, 1.0),
    },
    "polished_pewter": {
        "body": (0.60, 0.61, 0.63, 1.0),
        "lid": (0.66, 0.67, 0.69, 1.0),
        "dark": (0.44, 0.45, 0.47, 1.0),
        "accent": (0.72, 0.73, 0.75, 1.0),
        "foot": (0.50, 0.51, 0.53, 1.0),
    },
}


# ---------------------------------------------------------------------------
# Base real-world dimensions (meters). Scaled per-build by resolve_config.
# Shared rim / lid interface across all pot_forms.
# ---------------------------------------------------------------------------
# rounded_belly (parent f944b57b)
_POT_FOOT_R = 0.100
_POT_FOOT_H = 0.042
_POT_BELLY_R = 0.225
_POT_RIM_Z = 0.310
_POT_RIM_OUTER_R = 0.140
_POT_RIM_INNER_R = 0.128

# straight_cylindrical (26cd72d3)
_CYL_R = 0.175
_CYL_WALL = 0.012
_CYL_BOTTOM_T = 0.010
_CYL_SHOULDER_Z = 0.282

# wide_shallow_bowl (cef6bfac)
_BOWL_BOTTOM_R = 0.120
_BOWL_RIM_Z = 0.175
_BOWL_RIM_R = 0.250
_BOWL_WALL = 0.010

# lid (shared)
_LID_R = 0.150
_LID_APEX_Z = 0.060
_LID_LIP_R = 0.124
_LID_LIP_INNER_R = 0.118
_LID_LIP_DEPTH = 0.008

# handle boss (swing bail)
_BOSS_X = 0.033
_BOSS_SIZE = (0.016, 0.018, 0.020)
_BOSS_Z = 0.064
_PIVOT_Z = 0.068
_LOOP_R = 0.030
_LOOP_ROD_R = 0.006
_PIN_R = 0.005
_PIN_X0 = 0.026
_PIN_X1 = 0.040

# motion limits (nominal, scaled in resolve)
_LID_LIFT = 0.12
_HANDLE_UP = 1.5708
_LID_OPEN = 2.0
_CLAMP_OPEN = 1.80
_SWING_LIMIT = 0.40

# legs (inline pot-bottom feet)
_LEG_H = 0.045
_LEG_TOP_R = 0.018
_LEG_BOT_R = 0.014


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


def _snap_leg_count(n: int) -> int:
    """Snap any external leg_count to the nearest legal {0, 3, 4}."""
    if n in LEG_COUNTS:
        return n
    return min(LEG_COUNTS, key=lambda c: abs(c - n))


# ---------------------------------------------------------------------------
# Config dataclasses
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class CauldronConfig:
    pot_form: PotForm = "rounded_belly"
    lid_mechanism: LidMechanism = "lift_off_dome"
    handle_suspension: HandleSuspension = "swing_bail"
    leg_count: int = 0
    palette_style: PaletteStyle = "matte_black_cast_iron"
    pot_width_scale: float = 1.0
    pot_height_scale: float = 1.0
    rim_radius_scale: float = 1.0
    lid_open_scale: float = 1.0
    lid_travel_scale: float = 1.0
    leg_height_scale: float = 1.0
    swing_limit_scale: float = 1.0
    name: str = "cauldron"


@dataclass(frozen=True)
class ResolvedCauldronConfig:
    pot_form: PotForm
    lid_mechanism: LidMechanism
    handle_suspension: HandleSuspension
    leg_count: int
    palette_style: PaletteStyle
    pot_width_scale: float
    pot_height_scale: float
    rim_radius_scale: float
    lid_open_scale: float
    lid_travel_scale: float
    leg_height_scale: float
    swing_limit_scale: float
    # derived geometry
    width_s: float  # radial (belly/cyl/rim) scale
    height_s: float  # height scale
    rim_r: float  # base rim-radius driver (RIM_OUTER_R * rim_radius_scale)
    rim_z: float  # world z of pot mouth rim top (lid mount plane)
    lid_r: float  # lid outer radius
    lid_lip_r: float  # locating lip outer radius
    rim_anchor_r: float  # radius of the rim-wall anchor (real pot+lid material)
    lid_apex_z: float  # dome apex above seat plane
    leg_h: float  # per-leg height (scaled)
    lid_lift: float  # prismatic lid travel
    lid_open: float  # hinged-flip upper
    clamp_open: float  # clamp-arm upper
    handle_up: float  # bail upper
    swing_limit: float  # tripod pendulum half-angle
    name: str

    @property
    def is_tripod(self) -> bool:
        return self.handle_suspension == "tripod_stand"


# ---------------------------------------------------------------------------
# Seed / resolve
# ---------------------------------------------------------------------------
def config_from_seed(seed: int) -> CauldronConfig:
    """Deterministic procedural sampling (seed 0 is not special)."""
    rng = random.Random(seed)
    pot_form = rng.choice(POT_FORMS)
    lid_mechanism = rng.choice(LID_MECHANISMS)
    handle_suspension = rng.choice(HANDLE_SUSPENSIONS)
    # Compatibility gates for tripod_stand (root swap + pot pendulum-hung from a
    # bail on a hook between three splayed legs):
    #  - leg_count -> 0 (the tripod's own 3 legs carry the load; pot feet would
    #    double-support / float in the air).
    #  - lid_mechanism != clamp_locking (the rim toggle clamp arms collide with
    #    the bail arch / bail ears that occupy the same rim line).
    #  - pot_form != wide_shallow_bowl (the wide lid overhang fouls the splayed
    #    tripod legs).
    if handle_suspension == "tripod_stand":
        leg_count = 0
        # The pendulum bail arch + bail ears occupy the rim line, so only the
        # straight-up lift-off lid is compatible (hinge lug / clamp arms collide
        # with the bail). Downgrade other lids to lift_off_dome.
        lid_mechanism = "lift_off_dome"
        if pot_form == "wide_shallow_bowl":
            pot_form = "rounded_belly"
    else:
        leg_count = rng.choices(LEG_COUNTS, weights=LEG_COUNT_WEIGHTS, k=1)[0]
    # A rear hinge on a very wide, very shallow cazo lid is impractical (the lug
    # sits far outside the low wall and cannot embed); downgrade to lift-off.
    if pot_form == "wide_shallow_bowl" and lid_mechanism == "hinged_flip":
        lid_mechanism = "lift_off_dome"
    return CauldronConfig(
        pot_form=pot_form,
        lid_mechanism=lid_mechanism,
        handle_suspension=handle_suspension,
        leg_count=leg_count,
        palette_style=rng.choice(PALETTE_STYLES),
        pot_width_scale=round(rng.uniform(0.88, 1.15), 4),
        pot_height_scale=round(rng.uniform(0.85, 1.18), 4),
        rim_radius_scale=round(rng.uniform(0.92, 1.10), 4),
        lid_open_scale=round(rng.uniform(0.85, 1.10), 4),
        lid_travel_scale=round(rng.uniform(0.85, 1.10), 4),
        leg_height_scale=round(rng.uniform(0.85, 1.15), 4),
        swing_limit_scale=round(rng.uniform(0.80, 1.15), 4),
        name=f"seeded_cauldron_{seed}",
    )


def resolve_config(config: CauldronConfig | None = None) -> ResolvedCauldronConfig:
    cfg = config or CauldronConfig()
    pot_form = _pick(cfg.pot_form, POT_FORMS)
    lid_mechanism = _pick(cfg.lid_mechanism, LID_MECHANISMS)
    handle_suspension = _pick(cfg.handle_suspension, HANDLE_SUSPENSIONS)
    palette = _pick(cfg.palette_style, PALETTE_STYLES)

    # leg_count: snap to {0,3,4}; gate to 0 when tripod (double-support).
    leg_count = _snap_leg_count(int(cfg.leg_count))
    # Tripod compatibility gates (see config_from_seed): no pot feet, no clamp
    # lid (fouls bail), no wide bowl (fouls splayed legs).
    if handle_suspension == "tripod_stand":
        leg_count = 0
        lid_mechanism = "lift_off_dome"
        if pot_form == "wide_shallow_bowl":
            pot_form = "rounded_belly"
    if pot_form == "wide_shallow_bowl" and lid_mechanism == "hinged_flip":
        lid_mechanism = "lift_off_dome"

    width_s = _clamp(cfg.pot_width_scale, 0.88, 1.15)
    height_s = _clamp(cfg.pot_height_scale, 0.85, 1.18)
    rim_s = _clamp(cfg.rim_radius_scale, 0.92, 1.10)
    open_s = _clamp(cfg.lid_open_scale, 0.85, 1.10)
    travel_s = _clamp(cfg.lid_travel_scale, 0.85, 1.10)
    leg_h_s = _clamp(cfg.leg_height_scale, 0.85, 1.15)
    swing_s = _clamp(cfg.swing_limit_scale, 0.80, 1.15)

    # Rim / lid interface (single-sourced from the ACTUAL pot mouth). EVERY pot
    # mesh scales its mouth rim with width_s (belly/cyl use _POT_RIM_*_R *
    # width_s, bowl uses _BOWL_RIM_R * width_s), so the lid/lip/anchor MUST follow
    # width_s too — sizing them off the independent rim_radius_scale let a
    # wide-short pot (width_s >> rim_s) grow a mouth the lid could neither cover
    # nor seat on (6 mm gap -> floating/isolated lid + uncovered mouth).
    # rim_radius_scale now only modulates the lid's own radius (its overhang),
    # floored so the lid always stays proud of and seats on the mouth.
    if pot_form == "wide_shallow_bowl":
        rim_z = _BOWL_RIM_Z * height_s
        mouth_outer_r = _BOWL_RIM_R * width_s
        mouth_inner_r = (_BOWL_RIM_R - _BOWL_WALL) * width_s
        base_lid_r = mouth_outer_r + 0.010
        lid_apex_z = 0.035
    elif pot_form == "straight_cylindrical":
        rim_z = _POT_RIM_Z * height_s
        mouth_outer_r = _POT_RIM_OUTER_R * width_s
        mouth_inner_r = _POT_RIM_INNER_R * width_s
        base_lid_r = _LID_R * width_s * rim_s
        lid_apex_z = _LID_APEX_Z
    else:  # rounded_belly
        rim_z = _POT_RIM_Z * height_s
        mouth_outer_r = _POT_RIM_OUTER_R * width_s
        mouth_inner_r = _POT_RIM_INNER_R * width_s
        base_lid_r = _LID_R * width_s * rim_s
        lid_apex_z = _LID_APEX_Z

    rim_r = mouth_outer_r
    # Inequality (1): lid outer proud of the mouth outer radius (covers + seats).
    lid_r = max(base_lid_r, mouth_outer_r + 0.008)
    # Inequality (2): lip outer just inside the inner mouth radius — it nests in
    # the mouth AND its top edge meets the dome underside near the rim (where the
    # dome casting is at z~0), so the lip is never a floating island.
    lid_lip_r = max(mouth_inner_r - 0.004, 0.05)
    # Rim-wall anchor: the lid prismatic origin sits on the OUTER rim edge — the
    # pot rim wall material is there below (rim_inner..rim_outer) and the lid
    # dome skirt overhangs down past it (lid_r >= rim_outer) above — so both
    # parent and child geometry contain the origin (not the hollow centerline).
    rim_anchor_r = max(mouth_outer_r + 0.001, 0.05)

    leg_h = _LEG_H * leg_h_s

    # Lid travel. For the tripod-hung pot the lift-off lid rises toward the
    # overhead suspension bail, so cap the travel at the geometric ceiling
    # (single-sourced helper) with a small positive floor so the lid still
    # visibly slides off the mouth.
    lid_lift = _LID_LIFT * travel_s
    if handle_suspension == "tripod_stand":
        max_lift = _tripod_max_lid_lift(rim_z, lid_apex_z, height_s)
        lid_lift = _clamp(lid_lift, 0.030, max(0.035, max_lift))

    return ResolvedCauldronConfig(
        pot_form=pot_form,
        lid_mechanism=lid_mechanism,
        handle_suspension=handle_suspension,
        leg_count=leg_count,
        palette_style=palette,
        pot_width_scale=width_s,
        pot_height_scale=height_s,
        rim_radius_scale=rim_s,
        lid_open_scale=open_s,
        lid_travel_scale=travel_s,
        leg_height_scale=leg_h_s,
        swing_limit_scale=swing_s,
        width_s=width_s,
        height_s=height_s,
        rim_r=rim_r,
        rim_z=rim_z,
        lid_r=lid_r,
        lid_lip_r=lid_lip_r,
        rim_anchor_r=rim_anchor_r,
        lid_apex_z=lid_apex_z,
        leg_h=leg_h,
        lid_lift=lid_lift,
        lid_open=_clamp(_LID_OPEN * open_s, 0.5, math.pi * 0.95),
        clamp_open=_clamp(_CLAMP_OPEN * open_s, 0.5, math.pi * 0.95),
        handle_up=_clamp(_HANDLE_UP * open_s, 0.8, math.pi * 0.95),
        # Cap the pendulum half-angle at 0.40 rad: beyond that the swinging pot +
        # lid reach the (widened) splayed tripod legs. Derived clearance ceiling
        # rather than the old open 0.7.
        swing_limit=_clamp(_SWING_LIMIT * swing_s, 0.2, 0.40),
        name=cfg.name or "cauldron",
    )


def with_overrides(config: CauldronConfig, **kwargs: object) -> CauldronConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: CauldronConfig | ResolvedCauldronConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedCauldronConfig) else resolve_config(config)
    return (
        ("pot_form", r.pot_form),
        ("lid_mechanism", r.lid_mechanism),
        ("handle_suspension", r.handle_suspension),
        ("leg_count", f"n{r.leg_count}"),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Pot body geometry (Slot A). Each form is a revolved/lathed thick-walled
# hollow open vessel; the lid/handle interface is the rim top at z=rim_z.
# `pz` is the local-frame z-offset of the pot (0 for grounded root; for tripod
# the pot is authored with its origin at the bail apex, so pz = -bail_apex).
# ---------------------------------------------------------------------------
def _belly_pot_solid(r: ResolvedCauldronConfig, *, filled: bool) -> cq.Workplane:
    """Rounded-belly revolved pot + integral pedestal foot (parent _pot_solid)."""
    ws = r.width_s
    hs = r.height_s
    foot_r = _POT_FOOT_R * ws
    foot_h = _POT_FOOT_H * hs
    rim_z = r.rim_z
    rim_or = _POT_RIM_OUTER_R * ws

    def sx(x: float) -> float:
        return x * ws

    def sz(z: float) -> float:
        return z * hs

    wp = (
        cq.Workplane("XZ")
        .moveTo(0.0, 0.0)
        .lineTo(foot_r, 0.0)
        .lineTo(foot_r, foot_h)
        .lineTo(sx(0.085), sz(0.046))
        .spline(
            [
                (sx(0.150), sz(0.075)),
                (sx(0.210), sz(0.135)),
                (sx(_POT_BELLY_R), sz(0.185)),
                (sx(0.205), sz(0.250)),
                (sx(0.155), sz(0.295)),
                (rim_or, rim_z),
            ],
            includeCurrent=True,
        )
    )
    if filled:
        return wp.lineTo(0.0, rim_z).close().revolve(360.0, (0, -1, 0), (0, 1, 0))
    rim_ir = _POT_RIM_INNER_R * ws
    # The inner wall returns to a small inner radius (not pinched to the axis),
    # then a flat floor line crosses to the axis — this avoids a zero-radius
    # spline terminus that tessellates into a degenerate single-triangle island.
    profile = (
        wp.lineTo(rim_ir, rim_z)
        .spline(
            [
                (sx(0.142), sz(0.293)),
                (sx(0.193), sz(0.250)),
                (sx(0.213), sz(0.185)),
                (sx(0.198), sz(0.135)),
                (sx(0.138), sz(0.078)),
                (sx(0.070), sz(0.052)),
                (sx(0.020), sz(0.046)),
            ],
            includeCurrent=True,
        )
        .lineTo(0.0, sz(0.046))
        .close()
    )
    return profile.revolve(360.0, (0, -1, 0), (0, 1, 0))


def _belly_outer_r_at(r: ResolvedCauldronConfig, local_z: float) -> float:
    """Approximate belly outer radius at a belly-local height (for bail-ear
    placement on the wall). Interpolates the scaled outer profile control pts.
    """
    ws, hs = r.width_s, r.height_s
    # (height, radius) control points of the outer belly profile (source).
    pts = [
        (0.046, 0.085),
        (0.075, 0.150),
        (0.135, 0.210),
        (0.185, _POT_BELLY_R),
        (0.250, 0.205),
        (0.295, 0.155),
        (_POT_RIM_Z, _POT_RIM_OUTER_R),
    ]
    zs = [p[0] * hs for p in pts]
    rs = [p[1] * ws for p in pts]
    if local_z <= zs[0]:
        return rs[0]
    if local_z >= zs[-1]:
        return rs[-1]
    for k in range(len(zs) - 1):
        if zs[k] <= local_z <= zs[k + 1]:
            t = (local_z - zs[k]) / (zs[k + 1] - zs[k])
            return rs[k] + t * (rs[k + 1] - rs[k])
    return rs[-1]


def _cyl_pot_solid(r: ResolvedCauldronConfig, *, filled: bool) -> cq.Workplane:
    """Straight cylindrical stockpot lathe profile (26cd72d3 _pot_solid)."""
    ws = r.width_s
    bottom_z = r.leg_h if r.leg_count >= 1 else 0.0
    cyl_r = _CYL_R * ws
    rim_z = r.rim_z
    rim_or = _POT_RIM_OUTER_R * ws
    shoulder_z = _CYL_SHOULDER_Z * r.height_s + bottom_z * (1.0 - r.height_s)
    # keep shoulder strictly below the rim and above the bottom+floor
    shoulder_z = _clamp(shoulder_z, bottom_z + _CYL_BOTTOM_T + 0.02, rim_z - 0.005)

    wp = (
        cq.Workplane("XZ")
        .moveTo(0.0, bottom_z)
        .lineTo(cyl_r, bottom_z)
        .lineTo(cyl_r, shoulder_z)
        .lineTo(rim_or, rim_z)
    )
    if filled:
        return wp.lineTo(0.0, rim_z).close().revolve(360.0, (0, -1, 0), (0, 1, 0))
    cyl_ir = (_CYL_R - _CYL_WALL) * ws
    rim_ir = _POT_RIM_INNER_R * ws
    profile = (
        wp.lineTo(rim_ir, rim_z)
        .lineTo(cyl_ir, shoulder_z)
        .lineTo(cyl_ir, bottom_z + _CYL_BOTTOM_T)
        .lineTo(0.0, bottom_z + _CYL_BOTTOM_T)
        .close()
    )
    return profile.revolve(360.0, (0, -1, 0), (0, 1, 0))


def _bowl_pot_solid(r: ResolvedCauldronConfig, *, filled: bool) -> cq.Workplane:
    """Wide shallow bowl / cazo lathe profile (cef6bfac _bowl_solid)."""
    ws = r.width_s
    bottom_z = r.leg_h if r.leg_count >= 1 else 0.0
    rim_z = r.rim_z
    bot_r = _BOWL_BOTTOM_R * ws
    rim_r = _BOWL_RIM_R * ws

    def sx(x: float) -> float:
        return x * ws

    def lz(frac: float) -> float:
        # interpolate a height between bottom_z and rim_z by the source fraction
        return bottom_z + (rim_z - bottom_z) * frac

    wp = (
        cq.Workplane("XZ")
        .moveTo(bot_r, bottom_z)
        .spline(
            [
                (sx(0.155), lz(0.15)),
                (sx(0.195), lz(0.40)),
                (sx(0.228), lz(0.85)),
                (rim_r, rim_z),
            ],
            includeCurrent=True,
        )
    )
    if filled:
        return (
            wp.lineTo(0.0, rim_z)
            .lineTo(0.0, bottom_z)
            .close()
            .revolve(360.0, (0, -1, 0), (0, 1, 0))
        )
    inner_rim_r = (_BOWL_RIM_R - _BOWL_WALL) * ws
    inner_bot_r = (_BOWL_BOTTOM_R - _BOWL_WALL) * ws
    inner_bot_z = bottom_z + _BOWL_WALL
    profile = (
        wp.lineTo(inner_rim_r, rim_z)
        .spline(
            [
                (sx(0.218), lz(0.85)),
                (sx(0.185), lz(0.40)),
                (sx(0.145), lz(0.15)),
                (inner_bot_r, inner_bot_z),
            ],
            includeCurrent=True,
        )
        .lineTo(0.0, inner_bot_z)
        .lineTo(0.0, bottom_z)
        .close()
    )
    return profile.revolve(360.0, (0, -1, 0), (0, 1, 0))


def _pot_solid(r: ResolvedCauldronConfig, *, filled: bool = False) -> cq.Workplane:
    if r.pot_form == "straight_cylindrical":
        return _cyl_pot_solid(r, filled=filled)
    if r.pot_form == "wide_shallow_bowl":
        return _bowl_pot_solid(r, filled=filled)
    return _belly_pot_solid(r, filled=filled)


def _leg_solid(r: ResolvedCauldronConfig) -> cq.Workplane:
    """One tapered cast-iron leg, revolved (axisymmetric -> no rpy needed).

    Extends downward from z=0 to z=-leg_h so feet land at the pot-bottom plane.
    """
    top_r = _LEG_TOP_R
    bot_r = _LEG_BOT_R
    profile = (
        cq.Workplane("XZ")
        .moveTo(top_r, 0.0)
        .lineTo(bot_r, -r.leg_h)
        .lineTo(0.0, -r.leg_h)
        .lineTo(0.0, 0.0)
        .close()
    )
    return profile.revolve(360.0, (0, -1, 0), (0, 1, 0))


def _pot_bottom_z(r: ResolvedCauldronConfig) -> float:
    """Local z of the pot wall bottom (where feet attach), in the pot frame."""
    if r.leg_count >= 1 and r.pot_form in ("straight_cylindrical", "wide_shallow_bowl"):
        return r.leg_h
    return 0.0


def _leg_placement_r(r: ResolvedCauldronConfig) -> float:
    """Radial placement of the feet around the pot bottom."""
    if r.pot_form == "wide_shallow_bowl":
        return _BOWL_BOTTOM_R * r.width_s * 0.65
    if r.pot_form == "straight_cylindrical":
        return _CYL_R * r.width_s * 0.78
    return _POT_FOOT_R * r.width_s * 0.78


def _emit_pot(pot, r: ResolvedCauldronConfig, *, pz: float, body_mat, foot_mat) -> None:
    """Emit the pot shell + inline cast feet (Rule 1) at z-offset pz."""
    # Finer tessellation keeps the thin revolved wall a single connected mesh
    # (coarse tolerance can shatter the rim/floor into disconnected slivers).
    pot.visual(
        mesh_from_cadquery(_pot_solid(r), "pot_shell", tolerance=0.0004, angular_tolerance=0.05),
        origin=Origin(xyz=(0.0, 0.0, pz)),
        material=body_mat,
        name="pot_shell", material_class_id=("metal.cast_iron_bare" if r.palette_style in {"matte_black_cast_iron", "weathered_rust_iron", "seasoned_graphite", "polished_pewter"} else "ceramic.porcelain_glazed_plain"),
    )
    if r.leg_count >= 1:
        # Inline cast feet at the pot bottom, equiangular, absolute placement.
        leg_mesh = mesh_from_cadquery(_leg_solid(r), "cauldron_leg")
        place_r = _leg_placement_r(r)
        bottom_z = _pot_bottom_z(r)
        for i in range(r.leg_count):
            theta = 2.0 * math.pi * i / r.leg_count
            x = place_r * math.cos(theta)
            y = place_r * math.sin(theta)
            pot.visual(
                leg_mesh,
                origin=Origin(xyz=(x, y, bottom_z + pz)),
                material=foot_mat,
                name=f"leg_{i}", material_class_id=("metal.cast_iron_bare" if r.palette_style in {"matte_black_cast_iron", "seasoned_graphite", "enamel_red", "enamel_blue", "polished_pewter"} else "rust.heavy_corrosion"),
            )


# ---------------------------------------------------------------------------
# Lid geometry helpers (shared across mechanisms).
# ---------------------------------------------------------------------------
def _bail_pivot_dz(r: ResolvedCauldronConfig) -> float:
    """Z of the swing-bail pivot axle above the dome seat plane (dome-local z=0).

    Single-sourced (Contract 3c): the pivot, the pivot bosses, and the loop all
    reference this. The dome apex casting rises to ~``lid_apex_z`` at the center;
    the semicircular loop rod (radius ``_LOOP_ROD_R``) hangs its underside at
    ``pivot_dz - _LOOP_ROD_R`` where it passes near the axle. Placing the pivot
    at ``lid_apex_z + _LOOP_ROD_R + 0.010`` keeps that underside ~10 mm above the
    dome apex so the loop never pierces the dome at any ``handle_pivot`` angle
    (was ``lid_apex_z + 0.004`` -> the rod dipped ~2-3 mm into the apex, a real
    mesh contact that the flat-lid AABB pre-filter masked but the flipped hinged
    lid unmasked).
    """
    return r.lid_apex_z + _LOOP_ROD_R + 0.010


def _tripod_max_lid_lift(rim_z: float, lid_apex_z: float, height_s: float) -> float:
    """Geometric ceiling on the tripod lift-off lid travel.

    The suspension bail_rod apex is pinned at the hook contact (pot-frame z=0);
    the pot rim sits ``bail_apex_z - rim_z`` below it. A lift-off lid rises by
    ``lid_lift`` and its dome apex reaches ``rim_z + pz + lid_apex_z + lid_lift``
    (pz = -bail_apex_z). The lowest overhead obstacle is the hook cradle, which
    dips ``_HOOK_DROP + _HOOK_HANG_Z`` below the pot origin; keeping the lifted
    dome apex a further 10 mm below that bounds the travel so the lid never lifts
    up into the overhead hook / suspension bail.
    """
    bail_apex_z = _BAIL_APEX_FRAC * height_s
    hook_reach_below_origin = _HOOK_DROP + _HOOK_HANG_Z
    return bail_apex_z - rim_z - lid_apex_z - hook_reach_below_origin - 0.010


def _lid_dome_solid(r: ResolvedCauldronConfig) -> cq.Workplane:
    """Domed lid disc: stepped overhanging rim, hollow cast underside.

    Built at local z=0 (seat plane). Scales radially with lid_r, apex with
    lid_apex_z (parent _lid_solid silhouette).
    """
    lr = r.lid_r
    apex = r.lid_apex_z
    # source silhouette radii scaled relative to base 0.150 lid
    s = lr / _LID_R
    return (
        cq.Workplane("XZ")
        .moveTo(lr, 0.0)
        .lineTo(lr, 0.014)
        .lineTo(0.126 * s, 0.020)
        .spline(
            [(0.105 * s, 0.5 * apex + 0.002), (0.060 * s, apex - 0.008), (0.0, apex)],
            includeCurrent=True,
        )
        .lineTo(0.0, 0.034 * (apex / _LID_APEX_Z))
        .spline(
            [(0.060 * s, 0.027), (0.100 * s, 0.014), (0.120 * s, 0.0)],
            includeCurrent=True,
        )
        .close()
        .revolve(360.0, (0, -1, 0), (0, 1, 0))
    )


def _lid_lip_solid(r: ResolvedCauldronConfig) -> cq.Workplane:
    """Locating lip ring that drops into the mouth opening (parent _lid_lip).

    The ring rises from below the seat plane up to ~0.6*apex so it always
    merges into the hollow dome underside (one connected lid casting), even for
    the shallow wide-bowl dome, and hangs below the seat to drop into the mouth.
    """
    lip_r = r.lid_lip_r
    inner = max(lip_r - 0.006, 0.020)
    top_z = max(0.6 * r.lid_apex_z, 0.012)
    return (
        cq.Workplane("XY")
        .workplane(offset=top_z)
        .circle(lip_r)
        .circle(inner)
        .extrude(-(top_z + _LID_LIP_DEPTH))
    )


def _handle_solid(r: ResolvedCauldronConfig) -> cq.Workplane:
    """Semicircular bail loop + a continuous pivot axle along X (parent _handle).

    The pin ends are joined into one continuous axle through the loop center so
    real rod material sits at the local origin (0,0,0) = the pivot joint origin,
    keeping the captured-pin pivot within the articulation-origin tolerance.
    """
    loop = (
        cq.Workplane("XZ")
        .moveTo(_LOOP_R, 0.0)
        .circle(_LOOP_ROD_R)
        .revolve(180.0, (0, -1, 0), (0, 1, 0))
    )
    axle = cq.Workplane("YZ").workplane(offset=-_PIN_X1).circle(_PIN_R).extrude(2.0 * _PIN_X1)
    return loop.union(axle)


# --- hinged_flip hardware ----------------------------------------------------
def _hinge_geom(r: ResolvedCauldronConfig) -> dict[str, float]:
    barrel_r = 0.007
    barrel_len = 0.042
    # Stand the rear hinge barrel 30 mm proud of the lid edge (was 15 mm). At
    # 15 mm the opening dome edge / hinge strap grazed the pot-side hinge lug and
    # the bulging belly wall on wide-short pots; 30 mm keeps the swing arc clear.
    hinge_y = -(r.lid_r + 0.030)
    hinge_z_offset = 0.010
    hinge_z = r.rim_z + hinge_z_offset
    return {
        "barrel_r": barrel_r,
        "barrel_len": barrel_len,
        "hinge_y": hinge_y,
        "hinge_z": hinge_z,
        "lid_offset_y": -hinge_y,
        "lid_offset_z": r.rim_z - hinge_z,
    }


def _back_wall_outer_r(r: ResolvedCauldronConfig, local_z: float) -> float:
    """Pot outer wall radius at the back, at a pot-local height (hinged_flip is
    gated to belly/cyl only, so bowl is never asked)."""
    if r.pot_form == "straight_cylindrical":
        return _CYL_R * r.width_s
    return _belly_outer_r_at(r, local_z)


def _hinge_lug_solid(r: ResolvedCauldronConfig) -> cq.Workplane:
    """Pot-side hinge lug: a vertical post at the barrel that drops down the back
    of the pot to where the wall is wide enough to embed it (so it is supported,
    not floating), plus the horizontal barrel the lid strap wraps (8d43806f).

    The plate spans in Y from the barrel (proud of the lid edge) inward to embed
    ~6 mm into the back pot wall, so it always bridges barrel->wall (never a
    floating island) no matter how far the barrel stands off the lid edge.
    """
    g = _hinge_geom(r)
    lug_w = 0.042
    # Drop the post low enough that the (widening) pot wall reaches its y.
    lug_bottom_z = max(r.rim_z * 0.55, 0.05)
    lug_top_z = g["hinge_z"] + g["barrel_r"] + 0.003
    lug_h = lug_top_z - lug_bottom_z
    lug_cz = (lug_top_z + lug_bottom_z) / 2.0
    # Bridge from the barrel (outer) to ~6 mm inside the back wall (inner). Wall
    # radius taken at the widest (lowest) point in the post's z-span.
    wall_r = _back_wall_outer_r(r, lug_bottom_z)
    y_barrel = g["hinge_y"]
    y_embed = -(wall_r - 0.006)
    lug_lo = min(y_barrel, y_embed)
    lug_hi = max(y_barrel, y_embed)
    if lug_hi - lug_lo < 0.016:
        lug_hi = lug_lo + 0.016
    lug_cy = (lug_lo + lug_hi) / 2.0
    lug_d = lug_hi - lug_lo
    plate = cq.Workplane("XY").workplane(offset=lug_cz).center(0.0, lug_cy).box(lug_w, lug_d, lug_h)
    barrel = (
        cq.Workplane("YZ")
        .workplane(offset=-g["barrel_len"] / 2.0)
        .center(g["hinge_y"], g["hinge_z"])
        .circle(g["barrel_r"])
        .extrude(g["barrel_len"])
    )
    return plate.union(barrel)


def _hinge_strap_solid(r: ResolvedCauldronConfig) -> cq.Workplane:
    g = _hinge_geom(r)
    strap_w = 0.030
    strap_t = 0.005
    wrap_ir = g["barrel_r"] - 0.001
    wrap_or = g["barrel_r"] + strap_t + 0.001
    # Plate reaches from the wrap (y=0) past the dome near edge so it visibly
    # merges into the dome underside (no floating island), even for a wide lid.
    dome_near_y = g["lid_offset_y"] - r.lid_r
    plate_len = max(0.055, dome_near_y + 0.030)
    wrap = (
        cq.Workplane("YZ")
        .workplane(offset=-strap_w / 2.0)
        .circle(wrap_or)
        .circle(wrap_ir)
        .extrude(strap_w)
    )
    plate_cz = g["lid_offset_z"] + strap_t / 2.0
    plate_cy = plate_len / 2.0
    plate = (
        cq.Workplane("XY")
        .workplane(offset=plate_cz)
        .center(0.0, plate_cy)
        .box(strap_w, plate_len, strap_t)
    )
    return wrap.union(plate)


# --- clamp_locking hardware --------------------------------------------------
_CLAMP_LUG_BASE_Z = 0.012
_CLAMP_LUG_H = 0.022
_CLAMP_PIVOT_Z = _CLAMP_LUG_BASE_Z + _CLAMP_LUG_H * 0.55
_CLAMP_ARM_W = 0.014
_CLAMP_ARM_T = 0.005
_CLAMP_ARM_L = 0.032
_CLAMP_HOOK_D = 0.016
_CLAMP_HOOK_H = 0.006
_CLAMP_PIVOT_R = 0.006


def _clamp_lug_solid(r: ResolvedCauldronConfig) -> cq.Workplane:
    return (
        cq.Workplane("XY")
        .rect(0.024, 0.018)
        .workplane(offset=_CLAMP_LUG_H)
        .rect(0.018, 0.013)
        .loft()
    )


def _clamp_arm_solid(r: ResolvedCauldronConfig) -> cq.Workplane:
    bar = cq.Workplane("XY").rect(_CLAMP_ARM_W, _CLAMP_ARM_T).extrude(-_CLAMP_ARM_L)
    boss_len = _CLAMP_ARM_W + 0.006
    boss = (
        cq.Workplane("YZ")
        .circle(_CLAMP_PIVOT_R)
        .extrude(boss_len)
        .translate((-boss_len / 2.0, 0.0, 0.0))
    )
    hook = (
        cq.Workplane("XZ")
        .workplane(offset=-(_CLAMP_ARM_T / 2.0))
        .center(0.0, -(_CLAMP_ARM_L - _CLAMP_HOOK_H / 2.0))
        .rect(_CLAMP_ARM_W, _CLAMP_HOOK_H)
        .extrude(-_CLAMP_HOOK_D)
    )
    return bar.union(boss).union(hook)


# --- side_loop_ears hardware -------------------------------------------------
_EAR_ARCH_R = 0.035
_EAR_ROD_R = 0.007
_EAR_PAD_W = 0.018
_EAR_PAD_H = 0.024
_EAR_PAD_D = 0.006


def _ear_solid(r: ResolvedCauldronConfig) -> cq.Workplane:
    """Half-torus side-loop ear with a backing mount plate (09d73153 _ear_solid).

    The arch lies in the YZ plane protruding +Y; a single backing plate spans
    both feet (z = -R..+R) at y = -pad_d..0 so (a) real material sits at the
    local origin (0,0,0) = the FIXED-joint origin and (b) the plate face at
    y in [-pad_d, 0] embeds into the pot wall (one connected piece).
    """
    profile = cq.Workplane("XZ").moveTo(_EAR_ARCH_R, 0.0).circle(_EAR_ROD_R)
    half_torus = profile.revolve(180.0, (0, -1, 0), (0, 1, 0))
    rotated = half_torus.rotate((0, 0, 0), (0, 1, 0), 90.0)
    # Continuous backing plate from lower foot to upper foot, centered on z=0,
    # straddling the local origin so the joint origin sits on real material.
    plate_h = 2.0 * _EAR_ARCH_R + _EAR_PAD_H
    backing = (
        cq.Workplane("XZ")
        .workplane(offset=-_EAR_PAD_D)
        .center(0.0, 0.0)
        .rect(_EAR_PAD_W, plate_h)
        .extrude(_EAR_PAD_D)
    )
    return rotated.union(backing)


def _interp_piecewise(points: list[tuple[float, float]], x: float) -> tuple[float, float]:
    """Return interpolated y and local dy/dx for monotonic piecewise points."""
    if x <= points[0][0]:
        a, b = points[0], points[1]
    elif x >= points[-1][0]:
        a, b = points[-2], points[-1]
    else:
        a, b = points[0], points[-1]
        for i in range(len(points) - 1):
            if points[i][0] <= x <= points[i + 1][0]:
                a, b = points[i], points[i + 1]
                break
    dx = b[0] - a[0]
    slope = 0.0 if abs(dx) < 1e-9 else (b[1] - a[1]) / dx
    t = 0.0 if abs(dx) < 1e-9 else (x - a[0]) / dx
    return a[1] + t * (b[1] - a[1]), slope


def _bowl_outer_radius_and_slope(r: ResolvedCauldronConfig, frac: float) -> tuple[float, float]:
    bottom_z = r.leg_h if r.leg_count >= 1 else 0.0
    wall_h = max(r.rim_z - bottom_z, 0.001)
    pts = [
        (0.0, _BOWL_BOTTOM_R * r.width_s),
        (0.15, 0.155 * r.width_s),
        (0.40, 0.195 * r.width_s),
        (0.85, 0.228 * r.width_s),
        (1.0, _BOWL_RIM_R * r.width_s),
    ]
    radius, dr_dfrac = _interp_piecewise(pts, frac)
    return radius, dr_dfrac / wall_h


def _ear_mount(r: ResolvedCauldronConfig) -> dict[str, float]:
    """Mount point of the ears on the pot wall (±Y).

    The ear origin sits so the backing plate (which spans y=-pad_d..0 in the
    ear frame) embeds ~3 mm into the wall: mount_r = wall_outer_r - embed, so
    the plate's outer face (y=0 -> world mount_r) is inside the wall surface
    and the inner face is deeper still, guaranteeing pad↔wall contact.
    """
    embed = 0.003
    tilt_roll = 0.0
    if r.pot_form == "wide_shallow_bowl":
        # Mount on the actual flared bowl profile and rotate the ear so its
        # backing plate follows the sloped wall instead of hanging vertically.
        bottom_z = r.leg_h if r.leg_count >= 1 else 0.0
        mount_frac = 0.58
        wall_r, dr_dz = _bowl_outer_radius_and_slope(r, mount_frac)
        mount_z = bottom_z + (r.rim_z - bottom_z) * mount_frac
        tilt_roll = -math.atan(dr_dz)
    elif r.pot_form == "straight_cylindrical":
        wall_r = _CYL_R * r.width_s
        mount_z = r.rim_z * 0.70
    else:  # rounded_belly: mount near the widest belly
        wall_r = _POT_BELLY_R * r.width_s * 0.94
        mount_z = r.rim_z * 0.60
    return {"mount_r": wall_r - embed, "mount_z": mount_z, "tilt_roll": tilt_roll}


# --- tripod hardware ---------------------------------------------------------
_HUB_R = 0.030
_HUB_H = 0.045
_HOOK_DROP = 0.300
_HOOK_ROD_R = 0.005
_HOOK_CRADLE_X = 0.012
# Leg splay half-angle from vertical. Widened from 0.50 -> 0.72 so the splayed
# leg cone is broad enough at the lid/upper-pot height (near the narrow apex of
# the cone) that the pendulum-swinging pot + lid clear all three legs by a solid
# margin across the full ``swing_limit`` range (see _tripod_leg_solid geometry).
_TRIPOD_LEG_SPLAY = 0.720
_TRIPOD_LEG_GROUND_Z = -1.30
_TRIPOD_LEG_TOP_R = 0.011
_TRIPOD_LEG_BOT_R = 0.018
_BAIL_EAR_Z = 0.280
_BAIL_SPAN_R = 0.180
_BAIL_ROD_R = 0.005
# Tripod suspension-bail apex height above the pot origin (== the hook contact).
# Single-sourced so resolve_config can derive the tripod lid-lift ceiling from
# the same value build_cauldron uses to place the bail apex / pot origin.
_BAIL_APEX_FRAC = 0.480
_HOOK_HANG_X = _HOOK_CRADLE_X
_HOOK_HANG_Z = -_HOOK_DROP + _HOOK_ROD_R + _BAIL_ROD_R + 0.001


def _tripod_leg_length() -> float:
    return (abs(_TRIPOD_LEG_GROUND_Z) - _HUB_H / 2) / math.cos(_TRIPOD_LEG_SPLAY)


def _hub_solid() -> cq.Workplane:
    return cq.Workplane("XY").workplane(offset=-_HUB_H / 2).circle(_HUB_R).extrude(_HUB_H)


def _tripod_leg_solid() -> cq.Workplane:
    leg_len = _tripod_leg_length()
    return (
        cq.Workplane("XY")
        .circle(_TRIPOD_LEG_TOP_R)
        .workplane(offset=-leg_len)
        .circle(_TRIPOD_LEG_BOT_R)
        .loft()
    )


def _hook_mesh():
    """Tripod J-hook with a real cradle below the bail contact point.

    The hook centerline dips below ``_HOOK_HANG_Z`` so the bail rod sits on top
    of the crook instead of sharing the same centerline as the hook bottom.
    """
    return mesh_from_geometry(
        tube_from_spline_points(
            [
                (0.0, 0.0, -_HUB_H / 2),
                (0.0, 0.0, -0.08),
                (0.0, 0.0, -0.16),
                (0.0, 0.0, -_HOOK_DROP + 0.060),
                (0.0, 0.0, -_HOOK_DROP + 0.030),
                (0.004, 0.0, -_HOOK_DROP + 0.012),
                (_HOOK_CRADLE_X, 0.0, -_HOOK_DROP),
                (0.022, 0.0, -_HOOK_DROP + 0.006),
                (0.027, 0.0, -_HOOK_DROP + 0.026),
            ],
            radius=_HOOK_ROD_R,
            samples_per_segment=12,
            radial_segments=12,
            cap_ends=True,
        ),
        "hook_tube",
    )


def _bail_mesh(bail_apex_z: float, *, span: float, ear_z: float, lid_clear_z: float):
    """Bail arch from the two ears (±span at ear_z) up to the hook apex (0,0,0)
    in the pot frame). Mid control points scale with the ear span."""
    m = span / _BAIL_SPAN_R
    outside_span = span + 0.018
    shoulder_z = max(lid_clear_z, ear_z * 0.45)
    return mesh_from_geometry(
        tube_from_spline_points(
            [
                (0.0, -span, ear_z),
                (0.0, -outside_span, ear_z * 0.72),
                (0.0, -outside_span, shoulder_z),
                (0.0, -0.085 * m, max(lid_clear_z, ear_z * 0.10)),
                (0.0, 0.0, 0.0),
                (0.0, 0.085 * m, max(lid_clear_z, ear_z * 0.10)),
                (0.0, outside_span, shoulder_z),
                (0.0, outside_span, ear_z * 0.72),
                (0.0, span, ear_z),
            ],
            radius=_BAIL_ROD_R,
            samples_per_segment=16,
            radial_segments=12,
            cap_ends=True,
        ),
        "bail_arch",
    )


# ---------------------------------------------------------------------------
# Lid + handle builders. `pot` is the part the lid mounts on; `pz` is the
# pot's local z offset (0 grounded; -bail_apex for tripod-hung pot).
# ---------------------------------------------------------------------------
def _build_lid(
    model,
    pot,
    r: ResolvedCauldronConfig,
    *,
    pz: float,
    lid_mat,
    dark_mat,
    accent_mat,
    with_bail: bool,
) -> None:
    """Emit the lid part + lid_mechanism joints + (optional) swing bail."""
    lid = model.part("lid")

    if r.lid_mechanism == "hinged_flip":
        g = _hinge_geom(r)
        # pot-side hinge lug.
        pot.visual(
            mesh_from_cadquery(_hinge_lug_solid(r), "hinge_lug"),
            origin=Origin(xyz=(0.0, 0.0, pz)),
            material=accent_mat,
            name="hinge_lug", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"matte_black_cast_iron", "seasoned_graphite", "enamel_red", "enamel_blue", "polished_pewter"} else "rust.heavy_corrosion"),
        )
        # lid dome offset so it caps the mouth when closed (lid frame at hinge).
        lid.visual(
            mesh_from_cadquery(_lid_dome_solid(r), "lid_dome"),
            origin=Origin(xyz=(0.0, g["lid_offset_y"], g["lid_offset_z"])),
            material=lid_mat,
            name="lid_dome", material_class_id=("metal.cast_iron_bare" if r.palette_style in {"matte_black_cast_iron", "weathered_rust_iron", "seasoned_graphite", "polished_pewter"} else "ceramic.porcelain_glazed_plain"),
        )
        lid.visual(
            mesh_from_cadquery(_hinge_strap_solid(r), "hinge_strap"),
            material=accent_mat,
            name="hinge_strap", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"matte_black_cast_iron", "seasoned_graphite", "enamel_red", "enamel_blue", "polished_pewter"} else "rust.heavy_corrosion"),
        )
        if with_bail:
            _emit_bosses(lid, r, oy=g["lid_offset_y"], oz=g["lid_offset_z"], mat=lid_mat)
        model.articulation(
            "lid_hinge",
            ArticulationType.REVOLUTE,
            parent=pot,
            child=lid,
            origin=Origin(xyz=(0.0, g["hinge_y"], g["hinge_z"] + pz)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=60.0, velocity=1.0, lower=0.0, upper=r.lid_open),
        )
        if with_bail:
            _emit_bail(
                model,
                lid,
                r,
                pivot_oz=_bail_pivot_dz(r) + g["lid_offset_z"],
                pivot_oy=g["lid_offset_y"],
                dark_mat=dark_mat,
            )
        return

    # lift_off_dome and clamp_locking both use a PRISMATIC +Z lid at the rim.
    # The joint origin intentionally lives on the real rim material instead of
    # the hollow centerline, so the lid visuals are offset back to keep the dome
    # concentric with the pot mouth in the closed pose.
    lid_center_x = -r.rim_anchor_r
    lid.visual(
        mesh_from_cadquery(_lid_dome_solid(r), "lid_dome"),
        origin=Origin(xyz=(lid_center_x, 0.0, 0.0)),
        material=lid_mat,
        name="lid_dome", material_class_id=("metal.cast_iron_bare" if r.palette_style in {"matte_black_cast_iron", "weathered_rust_iron", "seasoned_graphite", "polished_pewter"} else "ceramic.porcelain_glazed_plain"),
    )
    lid.visual(
        mesh_from_cadquery(_lid_lip_solid(r), "lid_lip"),
        origin=Origin(xyz=(lid_center_x, 0.0, 0.0)),
        material=lid_mat,
        name="lid_lip", material_class_id=("metal.cast_iron_bare" if r.palette_style in {"matte_black_cast_iron", "weathered_rust_iron", "seasoned_graphite", "polished_pewter"} else "ceramic.porcelain_glazed_plain"),
    )
    if with_bail:
        _emit_bosses(lid, r, ox=lid_center_x, oy=0.0, oz=0.0, mat=lid_mat)

    # Anchor the prismatic origin on the rim wall (real pot rim + lid lip
    # material) rather than the hollow mouth center; +Z axis still lifts the
    # lid straight up.
    model.articulation(
        "lid_lift",
        ArticulationType.PRISMATIC,
        parent=pot,
        child=lid,
        origin=Origin(xyz=(r.rim_anchor_r, 0.0, r.rim_z + pz)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=60.0, velocity=0.5, lower=0.0, upper=r.lid_lift),
    )
    if with_bail:
        _emit_bail(
            model,
            lid,
            r,
            pivot_ox=lid_center_x,
            pivot_oz=_bail_pivot_dz(r),
            pivot_oy=0.0,
            dark_mat=dark_mat,
        )

    if r.lid_mechanism == "clamp_locking":
        _emit_clamps(model, lid, r, ox=lid_center_x, lid_mat=lid_mat, dark_mat=dark_mat)


def _emit_bosses(
    lid,
    r: ResolvedCauldronConfig,
    *,
    ox: float = 0.0,
    oy: float,
    oz: float,
    mat,
) -> None:
    """Two cast pivot bosses straddling the dome apex for the bail pins.

    Each boss is a tall post that bridges from inside the dome apex casting (base
    embedded ~10 mm below the apex, no floating island) up to the raised bail
    pivot axle at ``_bail_pivot_dz`` so the captured axle sits in real boss
    material. Height is derived so the same boss works for tall and shallow domes.
    """
    pivot_dz = _bail_pivot_dz(r)
    base_z = r.lid_apex_z - 0.010  # embed into the dome apex casting
    top_z = pivot_dz + _BOSS_SIZE[2] / 2.0  # wrap over the pivot axle
    boss_h = top_z - base_z
    boss_cz = (base_z + top_z) / 2.0 + oz
    for i, sign in enumerate((+1, -1)):
        lid.visual(
            Box((_BOSS_SIZE[0], _BOSS_SIZE[1], boss_h)),
            origin=Origin(xyz=(ox + sign * _BOSS_X, oy, boss_cz)),
            material=mat,
            name=f"handle_boss_{i}", material_class_id=("metal.cast_iron_bare" if r.palette_style in {"matte_black_cast_iron", "weathered_rust_iron", "seasoned_graphite", "polished_pewter"} else "ceramic.porcelain_glazed_plain"),
        )


def _emit_bail(
    model,
    lid,
    r: ResolvedCauldronConfig,
    *,
    pivot_oz,
    pivot_oy,
    dark_mat,
    pivot_ox: float = 0.0,
) -> None:
    handle = model.part("loop_handle")
    handle.visual(
        mesh_from_cadquery(_handle_solid(r), "handle_loop"),
        material=dark_mat,
        name="handle_loop", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"matte_black_cast_iron", "seasoned_graphite", "enamel_red", "enamel_blue", "polished_pewter"} else "rust.heavy_corrosion"),
    )
    model.articulation(
        "handle_pivot",
        ArticulationType.REVOLUTE,
        parent=lid,
        child=handle,
        origin=Origin(xyz=(pivot_ox, pivot_oy, pivot_oz)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=5.0, velocity=2.0, lower=0.0, upper=r.handle_up),
    )


def _emit_clamps(
    model,
    lid,
    r: ResolvedCauldronConfig,
    *,
    ox: float,
    lid_mat,
    dark_mat,
) -> None:
    """Two mirrored toggle-clamp arms (REVOLUTE) at the lid rim ±Y lugs."""
    clamp_r = r.lid_r + 0.004
    lug_cy = r.lid_r - 0.002
    arm_mesh = mesh_from_cadquery(_clamp_arm_solid(r), "clamp_arm")
    lug_mesh = mesh_from_cadquery(_clamp_lug_solid(r), "clamp_lug")
    for i in range(2):
        sign = 1 - 2 * i
        lid.visual(
            lug_mesh,
            origin=Origin(xyz=(ox, sign * lug_cy, _CLAMP_LUG_BASE_Z)),
            material=lid_mat,
            name=f"clamp_lug_{i}", material_class_id=("metal.cast_iron_bare" if r.palette_style in {"matte_black_cast_iron", "weathered_rust_iron", "seasoned_graphite", "polished_pewter"} else "ceramic.porcelain_glazed_plain"),
        )
        clamp = model.part(f"clamp_{i}")
        clamp.visual(arm_mesh, material=dark_mat, name=f"clamp_arm_{i}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"matte_black_cast_iron", "seasoned_graphite", "enamel_red", "enamel_blue", "polished_pewter"} else "rust.heavy_corrosion"))
        model.articulation(
            f"clamp_pivot_{i}",
            ArticulationType.REVOLUTE,
            parent=lid,
            child=clamp,
            origin=Origin(
                xyz=(ox, sign * clamp_r, _CLAMP_PIVOT_Z),
                rpy=(0.0, 0.0, i * math.pi),
            ),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=8.0, velocity=2.0, lower=0.0, upper=r.clamp_open),
        )


def _emit_ears(model, pot, r: ResolvedCauldronConfig, *, pz: float, body_mat) -> None:
    """Two FIXED cast side-loop ears mirrored on ±Y of the pot wall."""
    m = _ear_mount(r)
    # Place the two ears on the ±X axis (rotating the +Y-protruding ear by ∓90°
    # about Z) so they stay clear of a -Y rear hinge lug and the bail line.
    for i in range(2):
        ear = model.part(f"ear_{i}")
        ear.visual(
            mesh_from_cadquery(_ear_solid(r), f"ear_body_{i}"),
            material=body_mat,
            name=f"ear_body_{i}", material_class_id=("metal.cast_iron_bare" if r.palette_style in {"matte_black_cast_iron", "weathered_rust_iron", "seasoned_graphite", "polished_pewter"} else "ceramic.porcelain_glazed_plain"),
        )
        sign = 1 if i == 0 else -1
        spin = -math.pi / 2 if i == 0 else math.pi / 2
        model.articulation(
            f"pot_to_ear_{i}",
            ArticulationType.FIXED,
            parent=pot,
            child=ear,
            origin=Origin(
                xyz=(sign * m["mount_r"], 0.0, m["mount_z"] + pz),
                rpy=(m["tilt_roll"], 0.0, spin),
            ),
        )


# ---------------------------------------------------------------------------
# Build entry point
# ---------------------------------------------------------------------------
def build_cauldron(
    config: CauldronConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)

    pal = PALETTES[r.palette_style]
    body_mat = model.material(f"cdr_body_{r.palette_style}", rgba=pal["body"])
    lid_mat = model.material(f"cdr_lid_{r.palette_style}", rgba=pal["lid"])
    dark_mat = model.material(f"cdr_dark_{r.palette_style}", rgba=pal["dark"])
    accent_mat = model.material(f"cdr_accent_{r.palette_style}", rgba=pal["accent"])
    foot_mat = model.material(f"cdr_foot_{r.palette_style}", rgba=pal["foot"])

    # Only the swing_bail suspension puts a movable bail loop on the LID. The
    # tripod-hung pot carries its OWN fixed suspension bail_rod arch over the
    # lid; adding a second swinging loop on the lid there would foul the
    # suspension bail and the hook, so the tripod lid is a plain lift-off lid.
    with_bail = r.handle_suspension == "swing_bail"

    if r.is_tripod:
        # ---- ROOT SWAP: tripod_hub is root; pot pendulum-hangs from a hook ----
        bail_apex_z = _BAIL_APEX_FRAC * r.height_s
        pz = -bail_apex_z  # pot authored with origin at the bail apex

        hub = model.part("tripod_hub")
        hub.visual(
            mesh_from_cadquery(_hub_solid(), "hub_body"), material=accent_mat, name="hub_body", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"matte_black_cast_iron", "seasoned_graphite", "enamel_red", "enamel_blue", "polished_pewter"} else "rust.heavy_corrosion")
        )
        hub.visual(_hook_mesh(), material=accent_mat, name="hook", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"matte_black_cast_iron", "seasoned_graphite", "enamel_red", "enamel_blue", "polished_pewter"} else "rust.heavy_corrosion"))

        for i in range(3):
            leg = model.part(f"leg_{i}")
            leg.visual(
                mesh_from_cadquery(_tripod_leg_solid(), f"leg_shaft_{i}"),
                material=accent_mat,
                name=f"leg_shaft_{i}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"matte_black_cast_iron", "seasoned_graphite", "enamel_red", "enamel_blue", "polished_pewter"} else "rust.heavy_corrosion"),
            )
            azimuth = 2.0 * math.pi * i / 3
            model.articulation(
                f"hub_to_leg_{i}",
                ArticulationType.FIXED,
                parent=hub,
                child=leg,
                origin=Origin(xyz=(0.0, 0.0, -_HUB_H / 2), rpy=(0.0, _TRIPOD_LEG_SPLAY, azimuth)),
            )

        # pot body (hung) + bail ears + bail rod. The bail ears must sit on the
        # belly wall: place them at the scaled belly outer radius at ear height
        # so the ear box embeds into the wall (no floating island), and span the
        # bail to match.
        pot = model.part("pot_body")
        _emit_pot(pot, r, pz=pz, body_mat=body_mat, foot_mat=foot_mat)
        ear_local_z = _BAIL_EAR_Z * r.height_s  # belly-local ear height
        ear_dz = ear_local_z + pz  # pot-frame z of the ear
        belly_r_at_ear = _belly_outer_r_at(r, ear_local_z)
        bail_span = belly_r_at_ear  # ears + bail anchored on the wall
        ear_size = (0.020, 0.044, 0.028)
        pot.visual(
            Box(ear_size),
            origin=Origin(xyz=(0.0, -bail_span, ear_dz)),
            material=body_mat,
            name="bail_ear_0", material_class_id=("metal.cast_iron_bare" if r.palette_style in {"matte_black_cast_iron", "weathered_rust_iron", "seasoned_graphite", "polished_pewter"} else "ceramic.porcelain_glazed_plain"),
        )
        pot.visual(
            Box(ear_size),
            origin=Origin(xyz=(0.0, bail_span, ear_dz)),
            material=body_mat,
            name="bail_ear_1", material_class_id=("metal.cast_iron_bare" if r.palette_style in {"matte_black_cast_iron", "weathered_rust_iron", "seasoned_graphite", "polished_pewter"} else "ceramic.porcelain_glazed_plain"),
        )
        # Bail inner shoulders must clear the FULLY-LIFTED lid dome, not just the
        # closed dome, so include lid_lift in the clearance height.
        lid_clear_z = r.rim_z + pz + r.lid_apex_z + r.lid_lift + 0.020
        pot.visual(
            _bail_mesh(bail_apex_z, span=bail_span, ear_z=ear_dz, lid_clear_z=lid_clear_z),
            material=accent_mat,
            name="bail_rod", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"matte_black_cast_iron", "seasoned_graphite", "enamel_red", "enamel_blue", "polished_pewter"} else "rust.heavy_corrosion"),
        )

        model.articulation(
            "hub_to_pot",
            ArticulationType.REVOLUTE,
            parent=hub,
            child=pot,
            origin=Origin(xyz=(_HOOK_HANG_X, 0.0, _HOOK_HANG_Z)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(
                effort=20.0, velocity=1.0, lower=-r.swing_limit, upper=r.swing_limit
            ),
        )

        _build_lid(
            model,
            pot,
            r,
            pz=pz,
            lid_mat=lid_mat,
            dark_mat=dark_mat,
            accent_mat=accent_mat,
            with_bail=with_bail,
        )
    else:
        # ---- ROOT: pot_body ----
        pot = model.part("pot_body")
        _emit_pot(pot, r, pz=0.0, body_mat=body_mat, foot_mat=foot_mat)

        _build_lid(
            model,
            pot,
            r,
            pz=0.0,
            lid_mat=lid_mat,
            dark_mat=dark_mat,
            accent_mat=accent_mat,
            with_bail=with_bail,
        )

        if r.handle_suspension == "side_loop_ears":
            _emit_ears(model, pot, r, pz=0.0, body_mat=body_mat)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_cauldron(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_cauldron(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests / QC. Captured-fit overlaps (lip in mouth, strap on barrel, clamp boss
# in lug + hook on rim, bail pin in boss, ear pad in wall, bail rod on hook,
# tripod leg apex convergence) are declared element-scoped so island/overlap
# checks pass; every mechanism action is exercised.
# ---------------------------------------------------------------------------
def _ext(aabb):
    mn, mx = aabb
    return (mx[0] - mn[0], mx[1] - mn[1], mx[2] - mn[2])


def _center_xy(aabb):
    mn, mx = aabb
    return ((mn[0] + mx[0]) / 2.0, (mn[1] + mx[1]) / 2.0)


def run_cauldron_tests(
    object_model: ArticulatedObject,
    config: CauldronConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)

    pot = object_model.get_part("pot_body")
    lid = object_model.get_part("lid")
    pot_shell = pot.get_visual("pot_shell")
    lid_dome = lid.get_visual("lid_dome")

    ctx.allow_isolated_part(
        lid,
        reason="lid lifts off the pot mouth and loses body contact when opened",
    )
    if any(p.name == "loop_handle" for p in object_model.parts):
        ctx.allow_isolated_part(
            object_model.get_part("loop_handle"),
            reason="loop handle rides on the lid and loses body contact when the lid lifts off",
        )

    # ---- pot is genuinely hollow (cauldron identity) ----
    hollow_vol = float(_pot_solid(r).val().Volume())
    filled_vol = float(_pot_solid(r, filled=True).val().Volume())
    ctx.check(
        "pot body is hollow with an open mouth (thin revolved/lathed wall)",
        0.0 < hollow_vol < 0.40 * filled_vol,
        details=f"wall_volume={hollow_vol:.5f}, filled_volume={filled_vol:.5f}",
    )

    # ---- pot reads as a vessel of real size ----
    pot_aabb = ctx.part_world_aabb(pot)
    pext = _ext(pot_aabb)
    ctx.check(
        "pot body has real vessel volume",
        pext[0] > 0.15 and pext[2] > 0.05,
        details=f"pot extents={pext}",
    )

    # ---- inline cast feet present + reach the bottom plane ----
    if r.leg_count >= 1 and not r.is_tripod:
        for i in range(r.leg_count):
            leg_v = pot.get_visual(f"leg_{i}")
            ctx.check(
                f"cast foot leg_{i} is an inline pot visual (Rule 1, no joint)",
                leg_v is not None,
                details=f"leg_{i} visual missing",
            )

    # ============================================================ lid mechanism
    if r.lid_mechanism == "lift_off_dome":
        lid_lip = lid.get_visual("lid_lip")
        lid_lift = object_model.get_articulation("lid_lift")
        ctx.allow_overlap(
            lid,
            pot,
            elem_a=lid_lip,
            elem_b=pot_shell,
            reason="Lid locating lip nests inside the open pot mouth; the pot is "
            "hollow and the lip keeps radial clearance to the inner rim wall.",
        )
        ctx.allow_overlap(
            lid,
            pot,
            elem_a=lid_dome,
            elem_b=pot_shell,
            reason="Lift-off lid dome rim seats flush on the pot mouth rim "
            "(coincident seating faces). The prismatic joint only lifts the lid "
            "UP (lower=0), so this pair can never sink deeper than the rest touch; "
            "it is normally AABB-masked but the tripod pendulum swing unmasks it.",
        )
        ctx.check(
            "lid_lift is PRISMATIC about +Z",
            lid_lift.articulation_type == ArticulationType.PRISMATIC
            and abs(lid_lift.axis[2]) > 0.99,
            details=f"axis={lid_lift.axis}, type={lid_lift.articulation_type}",
        )
        pot_cx, pot_cy = _center_xy(ctx.part_element_world_aabb(pot, elem=pot_shell))
        lid_cx, lid_cy = _center_xy(ctx.part_element_world_aabb(lid, elem=lid_dome))
        ctx.check(
            "closed lift-off lid is concentric with the pot mouth",
            abs(lid_cx - pot_cx) < 0.006 and abs(lid_cy - pot_cy) < 0.006,
            details=f"pot_center=({pot_cx:.4f}, {pot_cy:.4f}), "
            f"lid_center=({lid_cx:.4f}, {lid_cy:.4f})",
        )
        rest_z = ctx.part_world_position(lid)[2]
        with ctx.pose({lid_lift: r.lid_lift}):
            up_z = ctx.part_world_position(lid)[2]
        ctx.check(
            "lid_lift slides the lid straight up off the mouth",
            up_z > rest_z + r.lid_lift * 0.5,
            details=f"rest_z={rest_z:.4f}, lifted_z={up_z:.4f}",
        )

    elif r.lid_mechanism == "hinged_flip":
        hinge_strap = lid.get_visual("hinge_strap")
        hinge_lug = pot.get_visual("hinge_lug")
        lid_hinge = object_model.get_articulation("lid_hinge")
        ctx.allow_overlap(
            lid,
            pot,
            elem_a=hinge_strap,
            elem_b=hinge_lug,
            reason="Hinge strap wrap fits around the pot hinge barrel; intentional "
            "captured-pivot embedding (~1 mm radial interference).",
        )
        ctx.allow_overlap(
            pot,
            pot,
            elem_a=hinge_lug,
            elem_b=pot_shell,
            reason="Hinge lug bracket is cast onto the rim, embedding into the pot wall.",
        )
        ctx.check(
            "lid_hinge is REVOLUTE about +X",
            lid_hinge.articulation_type == ArticulationType.REVOLUTE
            and abs(lid_hinge.axis[0]) > 0.99,
            details=f"axis={lid_hinge.axis}, type={lid_hinge.articulation_type}",
        )
        top0 = ctx.part_element_world_aabb(lid, elem=lid_dome)[1][2]
        with ctx.pose({lid_hinge: r.lid_open}):
            top1 = ctx.part_element_world_aabb(lid, elem=lid_dome)[1][2]
        ctx.check(
            "lid_hinge flips the lid open (dome top rises)",
            top1 > top0 + 0.05,
            details=f"closed_top_z={top0:.4f}, open_top_z={top1:.4f}",
        )

    elif r.lid_mechanism == "clamp_locking":
        lid_lip = lid.get_visual("lid_lip")
        lid_lift = object_model.get_articulation("lid_lift")
        ctx.allow_overlap(
            lid,
            pot,
            elem_a=lid_lip,
            elem_b=pot_shell,
            reason="Lid locating lip nests inside the open pot mouth (clamp lid).",
        )
        ctx.allow_overlap(
            lid,
            pot,
            elem_a=lid_dome,
            elem_b=pot_shell,
            reason="Clamp lid dome rim seats flush on the pot mouth rim "
            "(coincident seating faces); the prismatic joint only lifts UP so the "
            "pair never sinks deeper than the rest touch.",
        )
        ctx.check(
            "lid_lift is PRISMATIC about +Z",
            lid_lift.articulation_type == ArticulationType.PRISMATIC
            and abs(lid_lift.axis[2]) > 0.99,
            details=f"axis={lid_lift.axis}",
        )
        pot_cx, pot_cy = _center_xy(ctx.part_element_world_aabb(pot, elem=pot_shell))
        lid_cx, lid_cy = _center_xy(ctx.part_element_world_aabb(lid, elem=lid_dome))
        ctx.check(
            "closed clamp lid is concentric with the pot mouth",
            abs(lid_cx - pot_cx) < 0.006 and abs(lid_cy - pot_cy) < 0.006,
            details=f"pot_center=({pot_cx:.4f}, {pot_cy:.4f}), "
            f"lid_center=({lid_cx:.4f}, {lid_cy:.4f})",
        )
        for i in range(2):
            clamp = object_model.get_part(f"clamp_{i}")
            clamp_pivot = object_model.get_articulation(f"clamp_pivot_{i}")
            clamp_arm = clamp.get_visual(f"clamp_arm_{i}")
            lug = lid.get_visual(f"clamp_lug_{i}")
            ctx.allow_overlap(
                clamp,
                lid,
                elem_a=clamp_arm,
                elem_b=lug,
                reason=f"Clamp {i} pivot boss is captured inside the lid mounting lug bore.",
            )
            ctx.allow_overlap(
                clamp,
                pot,
                elem_a=clamp_arm,
                elem_b=pot_shell,
                reason=f"Clamp {i} hook lip engages the pot rim flange (latch contact).",
            )
            ctx.allow_overlap(
                lid,
                lid,
                elem_a=lug,
                elem_b=lid_dome,
                reason=f"Clamp {i} mounting lug is cast onto the lid rim, merging the dome.",
            )
            ctx.check(
                f"clamp_pivot_{i} is REVOLUTE about +X",
                clamp_pivot.articulation_type == ArticulationType.REVOLUTE
                and abs(clamp_pivot.axis[0]) > 0.99,
                details=f"axis={clamp_pivot.axis}",
            )
            rest_aabb = ctx.part_world_aabb(clamp)
            with ctx.pose({clamp_pivot: r.clamp_open}):
                open_aabb = ctx.part_world_aabb(clamp)
            ctx.check(
                f"clamp_{i} swings up/out when unlocked",
                open_aabb[1][2] > rest_aabb[1][2] + 0.004,
                details=f"rest={rest_aabb}, open={open_aabb}",
            )

    # ---- swing bail (present only for swing_bail; the tripod lid is plain) ----
    has_bail = r.handle_suspension == "swing_bail"
    if has_bail:
        handle = object_model.get_part("loop_handle")
        handle_pivot = object_model.get_articulation("handle_pivot")
        handle_loop = handle.get_visual("handle_loop")
        boss_0 = lid.get_visual("handle_boss_0")
        boss_1 = lid.get_visual("handle_boss_1")
        ctx.allow_overlap(
            handle,
            lid,
            elem_a=handle_loop,
            elem_b=boss_0,
            reason="Handle pivot axle is intentionally captured inside the cast lid boss.",
        )
        ctx.allow_overlap(
            handle,
            lid,
            elem_a=handle_loop,
            elem_b=boss_1,
            reason="Handle pivot axle is intentionally captured inside the cast lid boss.",
        )
        ctx.check(
            "handle_pivot is REVOLUTE about +X",
            handle_pivot.articulation_type == ArticulationType.REVOLUTE
            and abs(handle_pivot.axis[0]) > 0.99,
            details=f"axis={handle_pivot.axis}",
        )
        flat_aabb = ctx.part_world_aabb(handle)
        with ctx.pose({handle_pivot: r.handle_up}):
            up_aabb = ctx.part_world_aabb(handle)
        ctx.check(
            "bail folds from flat to upright (top rises)",
            up_aabb[1][2] > flat_aabb[1][2] + 0.02,
            details=f"flat={flat_aabb}, up={up_aabb}",
        )

    # ============================================================ handle / suspension
    if r.handle_suspension == "swing_bail":
        pass  # bail handled above

    elif r.handle_suspension == "side_loop_ears":
        for i in range(2):
            ear_part = object_model.get_part(f"ear_{i}")
            ear_elem = ear_part.get_visual(f"ear_body_{i}")
            pot_to_ear = object_model.get_articulation(f"pot_to_ear_{i}")
            ctx.allow_overlap(
                ear_part,
                pot,
                elem_a=ear_elem,
                elem_b=pot_shell,
                reason="Ear mounting pads are intentionally embedded into the pot wall "
                "as cast-on features typical of cast-iron cookware.",
            )
            ctx.check(
                f"pot_to_ear_{i} is FIXED",
                pot_to_ear.articulation_type == ArticulationType.FIXED,
                details=f"type={pot_to_ear.articulation_type}",
            )
            if r.pot_form == "wide_shallow_bowl":
                ctx.check(
                    f"ear_{i} backing follows the flared bowl wall",
                    pot_to_ear.origin.rpy[0] < -0.15,
                    details=f"rpy={pot_to_ear.origin.rpy}",
                )
            ctx.expect_contact(
                ear_part,
                pot,
                contact_tol=0.013,
                name=f"ear_{i} contacts the pot wall at the mounting surface",
            )

    elif r.is_tripod:
        hub = object_model.get_part("tripod_hub")
        hub_body = hub.get_visual("hub_body")
        hook = hub.get_visual("hook")
        bail_rod = pot.get_visual("bail_rod")
        hub_to_pot = object_model.get_articulation("hub_to_pot")
        legs = [object_model.get_part(f"leg_{i}") for i in range(3)]

        # Captured / convergence overlaps.
        ctx.allow_overlap(
            pot,
            hub,
            elem_a=bail_rod,
            elem_b=hook,
            reason="Bail rod rests on the hook cradle; local contact at the hanging point.",
        )
        for i in range(3):
            shaft = legs[i].get_visual(f"leg_shaft_{i}")
            ctx.allow_overlap(
                hub,
                legs[i],
                elem_a=hub_body,
                elem_b=shaft,
                reason=f"Leg {i} top is forged into the hub at the splay junction.",
            )
            ctx.allow_overlap(
                legs[i],
                hub,
                elem_a=shaft,
                elem_b=hook,
                reason=f"Leg {i} passes near the hanging hook rod at the apex convergence.",
            )
        for i in range(3):
            for j in range(i + 1, 3):
                ctx.allow_overlap(
                    legs[i],
                    legs[j],
                    elem_a=legs[i].get_visual(f"leg_shaft_{i}"),
                    elem_b=legs[j].get_visual(f"leg_shaft_{j}"),
                    reason=f"Legs {i} and {j} converge at the forged hub apex.",
                )

        hub_pos = ctx.part_world_position(hub)
        ctx.check(
            "tripod hub is the root at the world origin (apex)",
            abs(hub_pos[2]) < 0.01,
            details=f"hub_pos={hub_pos}",
        )
        # pot hangs below the hub.
        pot_pos = ctx.part_world_position(pot)
        ctx.check(
            "pot hangs below the hub on the hook",
            pot_pos[2] < hub_pos[2] - 0.15,
            details=f"pot_pos={pot_pos}, hub_pos={hub_pos}",
        )
        ctx.check(
            "bail apex hangs on the hook cradle above the hook bottom",
            abs(hub_to_pot.origin.xyz[0] - _HOOK_HANG_X) < 0.001
            and abs(hub_to_pot.origin.xyz[2] - _HOOK_HANG_Z) < 0.001
            and hub_to_pot.origin.xyz[2] > -_HOOK_DROP + _HOOK_ROD_R,
            details=f"origin={hub_to_pot.origin.xyz}, hook_bottom_z={-_HOOK_DROP:.4f}",
        )
        # legs reach well below the pot.
        for i in range(3):
            leg_aabb = ctx.part_world_aabb(legs[i])
            ctx.check(
                f"tripod leg_{i} foot is below the pot foot (ground contact)",
                leg_aabb[0][2] < pot_aabb[0][2] - 0.20,
                details=f"leg_min_z={leg_aabb[0][2]:.3f}",
            )
        ctx.check(
            "hub_to_pot is REVOLUTE about +X (pendulum)",
            hub_to_pot.articulation_type == ArticulationType.REVOLUTE
            and abs(hub_to_pot.axis[0]) > 0.99,
            details=f"axis={hub_to_pot.axis}",
        )
        rest_aabb = ctx.part_world_aabb(pot)
        rest_cy = (rest_aabb[0][1] + rest_aabb[1][1]) / 2.0
        with ctx.pose({hub_to_pot: r.swing_limit}):
            swung_aabb = ctx.part_world_aabb(pot)
            swung_cy = (swung_aabb[0][1] + swung_aabb[1][1]) / 2.0
        ctx.check(
            "pot swings laterally on the hook (pendulum)",
            swung_cy > rest_cy + 0.02,
            details=f"rest_cy={rest_cy:.4f}, swung_cy={swung_cy:.4f}",
        )

    # ---- at least one non-fixed joint exists ----
    non_fixed = [
        j for j in object_model.articulations if j.articulation_type != ArticulationType.FIXED
    ]
    ctx.check(
        "at least one non-fixed (lid/handle/pendulum) joint exists",
        len(non_fixed) >= 1,
        details=f"non-fixed joints={[j.name for j in non_fixed]}",
    )

    return ctx.report()


__all__ = [
    "CauldronConfig",
    "ResolvedCauldronConfig",
    "config_from_seed",
    "resolve_config",
    "build_cauldron",
    "build_seeded_cauldron",
    "slot_choices_for_seed",
    "run_cauldron_tests",
    "__modular__",
]
