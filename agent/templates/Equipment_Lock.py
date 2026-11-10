# SPDX-License-Identifier: Apache-2.0

"""Modular procedural template for ``padlock``.

Follows ``articraft_template_authoring/specs_modular_v1/Equipment_Lock.md``.

A standalone portable padlock: a root ``body`` that carries a release-motion
``shackle`` (a lifting U, a swinging shrouded U, or a sliding straight hasp
bar) plus an access mechanism on the front face (a keyway escutcheon, a hinged
dust cover over the keyway, or a vertical stack of combination dials).

World frame convention (shared by all families):

- +Z is up; the body rests on its base near z = 0.
- The body front face faces -Y; access hardware (keyway / dial window / dust
  cover) lives on that face.
- The shackle legs (or the hasp bar) enter the body top (z = BODY_H).

Two INCOMPATIBLE kinematic spines, derived from Slot A (the body shell):

    keyed family  (rect_brass / laminated_steel / round_discus)
        body authored in BODY frame, shackle in BODY frame, joint origin
        (0,0,0)/+Z; access = keyway escutcheon (static) or keyway + hinged
        dust cover (REVOLUTE -X). Shackle = tall_u (single PRISMATIC +Z) or
        shrouded_u (two-stage PRISMATIC +Z lift -> REVOLUTE +Z swing).
        shrouded_u is gated to rect_brass only.

    combo family  (armored_combo)
        orange octagon shell with a milled front dial window + faceplate +
        bezel + corner rivets + internal dial axles. Shackle authored in the
        LONG-LEG local frame, joint origin (-LEG_X,0,TOP_Z)/+Z. Shackle =
        short_u_revolve (PRISMATIC +Z) or straight_bar_hasp (PRISMATIC +X).
        access = dial_stack, N CONTINUOUS dials about X, ``dial_count`` in
        {3,4,5} is the multiplicity axis.

The compatibility matrix in ``config_from_seed`` / ``resolve_config`` never
samples an illegal cross-spine combination.

Adopted sources (spec Module Source Index):
S1 rec_build-...lock...fa3217d6 (parent A) — rect_brass body, tall_u shackle, keyway.
S2 rec_build-...lock...f96f0b30 (parent B) — armored_combo body, short_u_revolve, dial_stack.
S3 rec_lock_var_laminated_body — 5-plate laminated keyed body + through-rivets.
S4 rec_lock_var_round_disc_body — discus (revolved cylinder) keyed body.
S5 rec_lock_var_shrouded_shackle — raised shoulders + two-stage lift/swing release.
S6 rec_lock_var_straight_bar_shackle — straight sliding hasp bar + guide brackets.
S7 rec_lock_var_keyway_dust_cover — hinged brass dust cover over the keyway.
S8/S9 rec_lock_var_three_dials / five_dials — dial_count = 3 / 5 multiplicity.
"""

from __future__ import annotations

import math
import random
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

import cadquery as cq

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Cylinder,
    MatingContract,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
)

# adopted: S1 fa3217d6 — rect_brass body + tall_u shackle + keyway
# adopted: S2 f96f0b30 — armored_combo body + short_u_revolve + dial_stack
# adopted: S3 laminated_body — laminated plate stack keyed body + through-rivets
# adopted: S4 round_disc_body — discus revolved-cylinder keyed body
# adopted: S5 shrouded_shackle — shoulders + two-stage lift->swing release
# adopted: S6 straight_bar_shackle — straight sliding hasp bar + guide brackets
# adopted: S7 keyway_dust_cover — hinged brass dust cover (REVOLUTE -X)
# adopted: S8/S9 three_dials/five_dials — dial_count multiplicity

__modular__ = True

BodyModule = Literal["rect_brass", "laminated_steel", "round_discus", "armored_combo"]
ShackleModule = Literal["tall_u", "shrouded_u", "short_u_revolve", "straight_bar_hasp"]
AccessModule = Literal["keyway", "keyway_dust_cover", "dial_stack"]
PaletteStyle = Literal[
    "brass_classic",
    "armored_orange",
    "laminated_steel",
    "brushed_discus",
    "blackened_steel",
]

Family = Literal["keyed", "combo"]

BODY_MODULES: tuple[BodyModule, ...] = (
    "rect_brass",
    "laminated_steel",
    "round_discus",
    "armored_combo",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "brass_classic",
    "armored_orange",
    "laminated_steel",
    "brushed_discus",
    "blackened_steel",
)

# Weight the body sampler so each of the 4 shells appears often within 0-49,
# while the combo (which carries the dial multiplicity) stays well represented.
_BODY_WEIGHTS = {
    "rect_brass": 0.30,
    "laminated_steel": 0.22,
    "round_discus": 0.20,
    "armored_combo": 0.28,
}

# Family derivation (spec §9 compatibility matrix).
_FAMILY_OF: dict[BodyModule, Family] = {
    "rect_brass": "keyed",
    "laminated_steel": "keyed",
    "round_discus": "keyed",
    "armored_combo": "combo",
}

# Legal Slot B per family. shrouded_u is further gated to rect_brass only
# (its raised shoulders + shroud bore are only validated on the rect block).
_KEYED_SHACKLES: tuple[ShackleModule, ...] = ("tall_u", "shrouded_u")
_COMBO_SHACKLES: tuple[ShackleModule, ...] = ("short_u_revolve", "straight_bar_hasp")
# Legal Slot C per family.
_KEYED_ACCESS: tuple[AccessModule, ...] = ("keyway", "keyway_dust_cover")
_COMBO_ACCESS: tuple[AccessModule, ...] = ("dial_stack",)

DIAL_COUNTS: tuple[int, ...] = (3, 4, 5)
_DIAL_COUNT_WEIGHTS = (0.30, 0.50, 0.20)  # N=4 most common, N=5 rare tail.

# Palette compatible with a given body (each body keeps a sensible default
# colorway but any palette can be sampled — palette never changes topology).
# We just bias the body's "natural" colorway slightly via config_from_seed.


# --------------------------------------------------------------------------- #
# Palettes (spec §palette colorways).
# --------------------------------------------------------------------------- #

PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "brass_classic": {
        "body": (0.83, 0.66, 0.18, 1.0),
        "shackle": (0.74, 0.76, 0.80, 1.0),
        "chrome": (0.86, 0.88, 0.90, 1.0),
        "slot": (0.07, 0.07, 0.08, 1.0),
        "plate_a": (0.83, 0.66, 0.18, 1.0),
        "plate_b": (0.78, 0.61, 0.16, 1.0),
        "rivet": (0.70, 0.72, 0.75, 1.0),
        "faceplate": (0.10, 0.10, 0.11, 1.0),
        "dial": (0.06, 0.06, 0.07, 1.0),
        "dial_band": (0.30, 0.30, 0.32, 1.0),
        "cover": (0.83, 0.66, 0.18, 1.0),
    },
    "armored_orange": {
        "body": (0.86, 0.40, 0.10, 1.0),
        "shackle": (0.78, 0.80, 0.83, 1.0),
        "chrome": (0.86, 0.88, 0.90, 1.0),
        "slot": (0.06, 0.06, 0.07, 1.0),
        "plate_a": (0.86, 0.40, 0.10, 1.0),
        "plate_b": (0.80, 0.36, 0.09, 1.0),
        "rivet": (0.70, 0.72, 0.75, 1.0),
        "faceplate": (0.10, 0.10, 0.11, 1.0),
        "dial": (0.06, 0.06, 0.07, 1.0),
        "dial_band": (0.30, 0.30, 0.32, 1.0),
        "cover": (0.80, 0.38, 0.10, 1.0),
    },
    "laminated_steel": {
        "body": (0.46, 0.48, 0.52, 1.0),
        "shackle": (0.74, 0.76, 0.80, 1.0),
        "chrome": (0.86, 0.88, 0.90, 1.0),
        "slot": (0.07, 0.07, 0.08, 1.0),
        "plate_a": (0.36, 0.38, 0.42, 1.0),
        "plate_b": (0.46, 0.48, 0.52, 1.0),
        "rivet": (0.58, 0.60, 0.63, 1.0),
        "faceplate": (0.12, 0.12, 0.13, 1.0),
        "dial": (0.10, 0.10, 0.11, 1.0),
        "dial_band": (0.34, 0.34, 0.36, 1.0),
        "cover": (0.50, 0.52, 0.56, 1.0),
    },
    "brushed_discus": {
        "body": (0.72, 0.73, 0.76, 1.0),
        "shackle": (0.74, 0.76, 0.80, 1.0),
        "chrome": (0.86, 0.88, 0.90, 1.0),
        "slot": (0.07, 0.07, 0.08, 1.0),
        "plate_a": (0.72, 0.73, 0.76, 1.0),
        "plate_b": (0.66, 0.67, 0.70, 1.0),
        "rivet": (0.60, 0.62, 0.65, 1.0),
        "faceplate": (0.12, 0.12, 0.13, 1.0),
        "dial": (0.10, 0.10, 0.11, 1.0),
        "dial_band": (0.34, 0.34, 0.36, 1.0),
        "cover": (0.70, 0.71, 0.74, 1.0),
    },
    "blackened_steel": {
        "body": (0.18, 0.19, 0.21, 1.0),
        "shackle": (0.74, 0.76, 0.80, 1.0),
        "chrome": (0.86, 0.88, 0.90, 1.0),
        "slot": (0.05, 0.05, 0.06, 1.0),
        "plate_a": (0.16, 0.17, 0.19, 1.0),
        "plate_b": (0.22, 0.23, 0.25, 1.0),
        "rivet": (0.55, 0.57, 0.60, 1.0),
        "faceplate": (0.08, 0.08, 0.09, 1.0),
        "dial": (0.05, 0.05, 0.06, 1.0),
        "dial_band": (0.28, 0.28, 0.30, 1.0),
        "cover": (0.20, 0.21, 0.23, 1.0),
    },
}

# Natural per-body colorway (biased — palette is still freely re-sampled).
_BODY_DEFAULT_PALETTE: dict[BodyModule, PaletteStyle] = {
    "rect_brass": "brass_classic",
    "laminated_steel": "laminated_steel",
    "round_discus": "brushed_discus",
    "armored_combo": "armored_orange",
}


# =========================================================================== #
# Nominal dimensions (meters). Keyed and combo families have separate constants.
# =========================================================================== #

# --- Keyed (rect / laminated) body ------------------------------------------
K_BODY_W = 0.045          # width (X)
K_BODY_D = 0.019          # depth (Y)
K_BODY_H = 0.058          # height (Z)
K_BODY_EDGE_FILLET = 0.0045
K_LEG_OFFSET = 0.0135     # half-distance between the two shackle legs (X)
K_BAR_R = 0.0058          # shackle round-bar radius
K_BORE_R = K_BAR_R - 0.0004
K_LEG_SEAT_DEPTH = 0.016
# tall_u arch + leg geometry (parent A).
K_ARCH_RISE = 0.072       # arch top above body top
# discus body
DISC_RADIUS = 0.032
DISC_THICKNESS = 0.026
DISC_LEG_OFFSET = 0.012
DISC_BAR_R = 0.0048
DISC_BORE_R = DISC_BAR_R - 0.0004
DISC_LEG_SEAT_DEPTH = 0.018
DISC_ARCH_RISE = 0.035

# Laminated plate stack.
NUM_PLATES = 5
PLATE_GAP = 0.00008
NUM_RIVETS = 4
RIVET_HEAD_R = 0.0025
RIVET_HEAD_H = 0.0006
RIVET_SHAFT_R = 0.0018
RIVET_EMBED = 0.0003
# Rivets sit on the solid central web BETWEEN the two leg bores (x=±K_LEG_OFFSET,
# bore radius ~0.0054 occupies |x| in [0.008, 0.019]); x=±0.006 keeps every
# rivet shaft inside solid plate material at every Z so it never lands in a
# bored-out leg channel (which would float as a disconnected island).
RIVET_XZ = [(-0.006, 0.012), (0.006, 0.012), (-0.006, 0.046), (0.006, 0.046)]

# Keyway escutcheon (shared keyed access geometry).
DISC_T = 0.0016
SLOT_T = 0.0006
DISC_EMBED = 0.0005

# Shroud (raised protective shoulders) — rect body only.
SHOULDER_H = 0.020
SHOULDER_W = 0.016
SHOULDER_FILLET_V = 0.003
SHOULDER_FILLET_TOP = 0.002
SHACKLE_SWING = 2.05      # ~117 deg swing about the retained long leg

# Dust cover.
COVER_W = 0.017
COVER_H = 0.017
COVER_T = 0.0012
COVER_FILLET = 0.003
BRACKET_W = 0.014
BRACKET_H = 0.006
BARREL_R = 0.0012
BARREL_LEN = 0.013
COVER_OPEN_ANGLE = 2.1

# --- Combo (armored) body ---------------------------------------------------
C_BODY_W = 0.052          # width (X)
C_BODY_T = 0.020          # thickness (Y, front-back)
C_BODY_H = 0.074          # height (Z)
C_CHAMF = 0.012
ORANGE_LIP = 0.0030
C_WIRE_R = 0.0042         # shackle bar radius
C_SHACKLE_SPAN = 0.030    # center-to-center between legs
C_SHACKLE_CLEAR = 0.022   # clear height of U opening above body
C_LONG_LEG_BURY = 0.026
C_SHORT_LEG_BURY = 0.013
C_SHACKLE_TRAVEL = 0.018
C_LEG_X = C_SHACKLE_SPAN / 2.0
C_TOP_Z = C_BODY_H

# Dials.
DIAL_R = 0.0055
DIAL_W = 0.016
DIAL_GAP = 0.0008
DIAL_PITCH_NOM = 2.0 * DIAL_R + DIAL_GAP
DIAL_AXLE_Y = 0.0060
AXLE_R = 0.0034
POCKET_CLEAR = 0.0008

# Hasp bar (combo, straight_bar_hasp).
HASP_BAR_L = 0.066
HASP_BAR_W = 0.012
HASP_BAR_H = 0.005
HASP_TRAVEL = 0.022
HASP_GUIDE_SPAN = 0.030


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
class PadlockConfig:
    """Public config sampled by ``config_from_seed`` or supplied directly."""

    body_module: BodyModule = "rect_brass"
    shackle_module: ShackleModule = "tall_u"
    access_module: AccessModule = "keyway"
    dial_count: int = 4
    palette_style: PaletteStyle = "brass_classic"
    body_height_scale: float = 1.0
    shackle_clear_scale: float = 1.0
    dial_pitch_scale: float = 1.0
    name: str = "reference_padlock"


@dataclass(frozen=True)
class ResolvedPadlockConfig:
    body_module: BodyModule
    shackle_module: ShackleModule
    access_module: AccessModule
    family: Family
    dial_count: int
    palette_style: PaletteStyle
    body_height_scale: float
    shackle_clear_scale: float
    dial_pitch_scale: float
    name: str
    palette: dict[str, tuple[float, float, float, float]]
    # derived combo dial-stack geometry
    dial_pitch: float
    dial_zs: tuple[float, ...]
    dial_stack_cz: float
    pocket_z_lo: float
    pocket_z_hi: float


def config_from_seed(seed: int) -> PadlockConfig:
    """Deterministic per-seed procedural sampling (seed 0 is not special).

    Samples body_module -> derives family -> picks a legal shackle/access in
    that family -> (if dial_stack) weighted dial_count -> palette + scales.
    The compatibility matrix is honored here so no illegal cross-spine combo
    is ever produced.
    """
    rng = random.Random(seed)

    bodies = list(_BODY_WEIGHTS.keys())
    body: BodyModule = rng.choices(bodies, weights=[_BODY_WEIGHTS[b] for b in bodies], k=1)[0]
    family = _FAMILY_OF[body]

    if family == "keyed":
        # shrouded_u only validated on rect_brass; gate it out for other bodies.
        if body == "rect_brass":
            shackle: ShackleModule = rng.choices(("tall_u", "shrouded_u"), weights=(0.55, 0.45), k=1)[0]
        else:
            shackle = "tall_u"
        access: AccessModule = rng.choices(
            ("keyway", "keyway_dust_cover"), weights=(0.55, 0.45), k=1
        )[0]
        dial_count = 4  # ignored (N/A for keyed)
    else:  # combo
        shackle = rng.choices(
            ("short_u_revolve", "straight_bar_hasp"), weights=(0.55, 0.45), k=1
        )[0]
        access = "dial_stack"
        dial_count = rng.choices(DIAL_COUNTS, weights=_DIAL_COUNT_WEIGHTS, k=1)[0]

    # Palette: bias toward the body's natural colorway but allow any style.
    if rng.random() < 0.55:
        palette: PaletteStyle = _BODY_DEFAULT_PALETTE[body]
    else:
        palette = rng.choice(PALETTE_STYLES)

    body_height_scale = round(rng.uniform(0.90, 1.12), 4)
    shackle_clear_scale = round(rng.uniform(0.85, 1.15), 4)
    dial_pitch_scale = round(rng.uniform(0.95, 1.08), 4)

    return PadlockConfig(
        body_module=body,
        shackle_module=shackle,
        access_module=access,
        dial_count=dial_count,
        palette_style=palette,
        body_height_scale=body_height_scale,
        shackle_clear_scale=shackle_clear_scale,
        dial_pitch_scale=dial_pitch_scale,
        name=f"seeded_padlock_{seed}",
    )


def resolve_config(config: PadlockConfig) -> ResolvedPadlockConfig:
    if config.palette_style not in PALETTES:
        raise ValueError(f"Unsupported palette_style: {config.palette_style}")

    body = _pick(config.body_module, BODY_MODULES)
    family = _FAMILY_OF[body]

    # --- Compatibility matrix projection (defensive — config_from_seed already
    # samples legally, but a hand-built config must also be coerced). ---------
    if family == "keyed":
        shackle = _pick(config.shackle_module, _KEYED_SHACKLES)
        if shackle == "shrouded_u" and body != "rect_brass":
            shackle = "tall_u"  # shroud bore only valid on rect block
        access = _pick(config.access_module, _KEYED_ACCESS)
        dial_count = 4
    else:  # combo
        shackle = _pick(config.shackle_module, _COMBO_SHACKLES)
        access = "dial_stack"
        dial_count = int(config.dial_count)
        if dial_count not in DIAL_COUNTS:
            dial_count = 4

    body_height_scale = _clamp(config.body_height_scale, 0.90, 1.12)
    shackle_clear_scale = _clamp(config.shackle_clear_scale, 0.85, 1.15)
    dial_pitch_scale = _clamp(config.dial_pitch_scale, 0.95, 1.08)

    # --- Combo dial-stack geometry (recomputed for N and pitch scale). -------
    dial_pitch = DIAL_PITCH_NOM * dial_pitch_scale
    body_h = C_BODY_H * body_height_scale

    # Inequality projection: the dial window (first..last dial ± DIAL_R ± clear)
    # must fit inside the usable body height (between the orange lips). If the
    # stack is too tall, shrink the pitch until it fits.
    usable = body_h - 2.0 * ORANGE_LIP - 0.004
    window_h = (dial_count - 1) * dial_pitch + 2.0 * (DIAL_R + POCKET_CLEAR)
    if window_h > usable and dial_count > 1:
        max_pitch = (usable - 2.0 * (DIAL_R + POCKET_CLEAR)) / (dial_count - 1)
        dial_pitch = max(2.0 * DIAL_R + 0.0002, min(dial_pitch, max_pitch))
        window_h = (dial_count - 1) * dial_pitch + 2.0 * (DIAL_R + POCKET_CLEAR)

    dial_stack_cz = body_h * 0.5  # center the stack vertically
    dial_zs = tuple(
        dial_stack_cz + (i - (dial_count - 1) / 2.0) * dial_pitch for i in range(dial_count)
    )
    pocket_z_lo = dial_zs[0] - DIAL_R - POCKET_CLEAR
    pocket_z_hi = dial_zs[-1] + DIAL_R + POCKET_CLEAR

    return ResolvedPadlockConfig(
        body_module=body,
        shackle_module=shackle,
        access_module=access,
        family=family,
        dial_count=dial_count,
        palette_style=config.palette_style,
        body_height_scale=body_height_scale,
        shackle_clear_scale=shackle_clear_scale,
        dial_pitch_scale=dial_pitch_scale,
        name=config.name,
        palette=dict(PALETTES[config.palette_style]),
        dial_pitch=dial_pitch,
        dial_zs=dial_zs,
        dial_stack_cz=dial_stack_cz,
        pocket_z_lo=pocket_z_lo,
        pocket_z_hi=pocket_z_hi,
    )


# =========================================================================== #
# Keyed body geometry (CadQuery).
# =========================================================================== #


def _rect_body_shape(r: ResolvedPadlockConfig, *, shroud: bool) -> cq.Workplane:
    """Brass/blackened rect block; two top bores; optional raised shoulders."""
    h = K_BODY_H * r.body_height_scale
    body = (
        cq.Workplane("XY")
        .box(K_BODY_W, K_BODY_D, h, centered=(True, True, False))
        .edges("|Z")
        .fillet(K_BODY_EDGE_FILLET)
    )
    body = body.edges(">Z or <Z").fillet(0.0018)

    if shroud:
        for sx in (-K_LEG_OFFSET, K_LEG_OFFSET):
            sh = (
                cq.Workplane("XY")
                .box(SHOULDER_W, K_BODY_D * 0.80, SHOULDER_H, centered=(True, True, False))
            )
            sh = sh.edges("|Z").fillet(SHOULDER_FILLET_V)
            sh = sh.edges(">Z").fillet(SHOULDER_FILLET_TOP)
            sh = sh.translate((sx, 0.0, h))
            body = body.union(sh)
        bore_depth = SHOULDER_H + h * 0.66
        for sx in (-K_LEG_OFFSET, K_LEG_OFFSET):
            bore = (
                cq.Workplane("XY")
                .transformed(offset=(sx, 0.0, h + SHOULDER_H + 0.001))
                .circle(K_BORE_R)
                .extrude(-(bore_depth + 0.002))
            )
            body = body.cut(bore)
    else:
        for sx in (-K_LEG_OFFSET, K_LEG_OFFSET):
            body = (
                body.faces(">Z")
                .workplane(centerOption="CenterOfBoundBox")
                .pushPoints([(sx, 0.0)])
                .hole(2.0 * K_BORE_R, depth=h * 0.66)
            )
    return body


def _plate_shape(index: int, r: ResolvedPadlockConfig) -> cq.Workplane:
    """One laminated plate at its Y station; two top bores cut through it."""
    h = K_BODY_H * r.body_height_scale
    plate_t = (K_BODY_D - (NUM_PLATES - 1) * PLATE_GAP) / NUM_PLATES
    y_center = -K_BODY_D / 2.0 + plate_t / 2.0 + index * (plate_t + PLATE_GAP)
    plate = (
        cq.Workplane("XY")
        .box(K_BODY_W, plate_t, h, centered=(True, True, False))
        .edges("|Z")
        .fillet(0.0015)
    )
    plate = plate.edges(">Z or <Z").chamfer(0.00025)
    plate = plate.translate((0.0, y_center, 0.0))
    # Bore the two leg channels at the BODY centerline (y=0), not at this plate's
    # own y-station. The bore radius (K_BORE_R) exceeds a single plate's half
    # thickness, so a bore centered on the plate's y-station reaches past the
    # outer faces and punches a front-to-back window that exposes the shackle
    # legs. Centering every plate's bore on y=0 keeps the channel internal: the
    # front/back plates (|y| > K_BORE_R) stay solid and hide the seated legs,
    # matching the solid rect body's top hole at (sx, 0).
    for sx in (-K_LEG_OFFSET, K_LEG_OFFSET):
        bore = (
            cq.Workplane("XY")
            .center(sx, 0.0)
            .circle(K_BORE_R)
            .extrude(h * 0.66)
            .translate((0.0, 0.0, h - h * 0.66))
        )
        plate = plate.cut(bore)
    return plate


def _rivet_shape(index: int) -> cq.Workplane:
    """Through-rivet: shaft across body depth + domed heads proud of both faces."""
    x, z = RIVET_XZ[index]
    shaft = (
        cq.Workplane("XZ")
        .center(x, z)
        .circle(RIVET_SHAFT_R)
        .extrude(K_BODY_D)
        .translate((0.0, K_BODY_D / 2.0, 0.0))
    )
    front_head = (
        cq.Workplane("XZ")
        .center(x, z)
        .circle(RIVET_HEAD_R)
        .extrude(RIVET_HEAD_H + RIVET_EMBED)
        .translate((0.0, -K_BODY_D / 2.0 + RIVET_EMBED, 0.0))
    )
    back_head = (
        cq.Workplane("XZ")
        .center(x, z)
        .circle(RIVET_HEAD_R)
        .extrude(RIVET_HEAD_H + RIVET_EMBED)
        .translate((0.0, K_BODY_D / 2.0 + RIVET_HEAD_H, 0.0))
    )
    return front_head.union(shaft).union(back_head)


def _disc_body_shape(r: ResolvedPadlockConfig) -> cq.Workplane:
    """Discus round body: revolved cylinder, flat faces ±Y, curved-top bores."""
    thickness = DISC_THICKNESS
    radius = DISC_RADIUS * r.body_height_scale
    body_top = 2.0 * radius
    cyl = (
        cq.Workplane("XY")
        .circle(radius)
        .extrude(thickness)
        .rotate((0, 0, 0), (1, 0, 0), 90)
        .translate((0, thickness / 2.0, radius))
    )
    cyl = cyl.edges().chamfer(0.0018)
    long_bottom = body_top - radius * 1.10
    bore_depth = body_top - long_bottom + 0.005
    for sx in (-DISC_LEG_OFFSET, DISC_LEG_OFFSET):
        bore = (
            cq.Workplane("XY")
            .center(sx, 0.0)
            .circle(DISC_BORE_R)
            .extrude(bore_depth + 0.010)
            .translate((0.0, 0.0, body_top - bore_depth))
        )
        cyl = cyl.cut(bore)
    return cyl


# --- Keyway escutcheon (front-face access, keyed) ---------------------------


def _keyway_disc_shape(front_y: float, center_z: float) -> cq.Workplane:
    disc = cq.Workplane("XZ").circle(0.0072).extrude(DISC_T)
    disc = disc.translate((0.0, front_y + DISC_EMBED, center_z))
    return disc


def _keyway_slot_shape(front_y: float, center_z: float) -> cq.Workplane:
    disc_front_y = front_y - DISC_T + DISC_EMBED
    slot = cq.Workplane("XZ").moveTo(0.0, 0.0028).rect(0.0017, 0.0075).extrude(SLOT_T)
    keyhole = cq.Workplane("XZ").moveTo(0.0, 0.0028).circle(0.0017).extrude(SLOT_T)
    keyway = slot.union(keyhole)
    keyway = keyway.translate((0.0, disc_front_y + SLOT_T * 0.5, center_z))
    return keyway


def _hinge_bracket_shape(front_y: float, hinge_y: float, hinge_z: float) -> cq.Workplane:
    """Dust-cover hinge bracket: mounting plate embedded in front + pin barrel."""
    plate_inner_y = front_y + 0.002
    mount_depth = plate_inner_y - hinge_y
    plate = cq.Workplane("XZ").rect(BRACKET_W, BRACKET_H).extrude(mount_depth)
    plate = plate.edges("|Y").fillet(0.0008)
    plate = plate.translate((0.0, hinge_y + mount_depth, hinge_z))
    barrel = (
        cq.Workplane("YZ")
        .circle(BARREL_R)
        .extrude(BARREL_LEN)
        .translate((-BARREL_LEN / 2.0, 0.0, 0.0))
    )
    barrel = barrel.translate((0.0, hinge_y, hinge_z))
    return plate.union(barrel)


def _dust_cover_shape() -> cq.Workplane:
    """Dust cover flap authored in its local frame (origin at hinge top center)."""
    flap = cq.Workplane("XZ").rect(COVER_W, COVER_H).extrude(COVER_T)
    flap = flap.edges("|Y").fillet(COVER_FILLET)
    flap = flap.translate((0.0, 0.0, -COVER_H / 2.0))
    lip = cq.Workplane("XZ").rect(COVER_W * 0.5, 0.002).extrude(COVER_T + 0.001)
    lip = lip.edges("|Y").fillet(0.0005)
    lip = lip.translate((0.0, 0.0, -COVER_H - 0.001))
    return flap.union(lip)


# --- Keyed shackles ---------------------------------------------------------


def _tall_u_shackle_shape(r: ResolvedPadlockConfig) -> tuple[cq.Workplane, float]:
    """Tall U in BODY frame (parent A): long + short leg + half-torus arch.

    Returns (shape, long_leg_bottom_z) so the joint origin can be anchored on the
    lowest real shackle geometry (it sits inside the body bore).
    """
    h = K_BODY_H * r.body_height_scale
    arch_top = h + K_ARCH_RISE * r.shackle_clear_scale
    arch_center_z = arch_top - K_LEG_OFFSET
    short_leg_bottom = h - K_LEG_SEAT_DEPTH
    long_leg_bottom = h - (h * 0.62)

    torus_solid = cq.Solid.makeTorus(K_LEG_OFFSET, K_BAR_R)
    arch = cq.Workplane(obj=torus_solid).rotate((0, 0, 0), (1, 0, 0), 90.0)
    arch = arch.translate((0.0, 0.0, arch_center_z))
    half_box = (
        cq.Workplane("XY")
        .box(4.0 * K_LEG_OFFSET, 4.0 * K_BAR_R, 2.0 * (arch_top + K_LEG_OFFSET))
        .translate((0.0, 0.0, arch_center_z + (arch_top + K_LEG_OFFSET)))
    )
    arch = arch.intersect(half_box)

    long_len = arch_center_z - long_leg_bottom
    long_leg = (
        cq.Workplane("XY")
        .center(-K_LEG_OFFSET, 0.0)
        .circle(K_BAR_R)
        .extrude(long_len)
        .translate((0.0, 0.0, long_leg_bottom))
    )
    short_len = arch_center_z - short_leg_bottom
    short_leg = (
        cq.Workplane("XY")
        .center(K_LEG_OFFSET, 0.0)
        .circle(K_BAR_R)
        .extrude(short_len)
        .translate((0.0, 0.0, short_leg_bottom))
    )
    shackle = long_leg.union(short_leg).union(arch)
    shackle = shackle.edges("<Z").fillet(K_BAR_R * 0.45)
    return shackle, long_leg_bottom


def _disc_tall_u_shackle_shape(r: ResolvedPadlockConfig) -> tuple[cq.Workplane, float]:
    """Tall U sized for the discus body (own bore spacing/bar radius/top).

    Returns (shape, long_leg_bottom_z) so the caller can anchor the joint origin
    on the lowest real shackle geometry.
    """
    radius = DISC_RADIUS * r.body_height_scale
    body_top = 2.0 * radius
    arch_top = body_top + DISC_ARCH_RISE * r.shackle_clear_scale
    arch_center_z = arch_top - DISC_LEG_OFFSET
    short_leg_bottom = body_top - DISC_LEG_SEAT_DEPTH
    long_leg_bottom = body_top - radius * 1.05

    torus_solid = cq.Solid.makeTorus(DISC_LEG_OFFSET, DISC_BAR_R)
    arch = cq.Workplane(obj=torus_solid).rotate((0, 0, 0), (1, 0, 0), 90.0)
    arch = arch.translate((0.0, 0.0, arch_center_z))
    half_box = (
        cq.Workplane("XY")
        .box(4.0 * DISC_LEG_OFFSET, 4.0 * DISC_BAR_R, 2.0 * (arch_top + DISC_LEG_OFFSET))
        .translate((0.0, 0.0, arch_center_z + (arch_top + DISC_LEG_OFFSET)))
    )
    arch = arch.intersect(half_box)
    long_leg = (
        cq.Workplane("XY")
        .center(-DISC_LEG_OFFSET, 0.0)
        .circle(DISC_BAR_R)
        .extrude(arch_center_z - long_leg_bottom)
        .translate((0.0, 0.0, long_leg_bottom))
    )
    short_leg = (
        cq.Workplane("XY")
        .center(DISC_LEG_OFFSET, 0.0)
        .circle(DISC_BAR_R)
        .extrude(arch_center_z - short_leg_bottom)
        .translate((0.0, 0.0, short_leg_bottom))
    )
    shackle = long_leg.union(short_leg).union(arch)
    shackle = shackle.edges("<Z").fillet(DISC_BAR_R * 0.45)
    return shackle, long_leg_bottom


def _shrouded_u_shackle_shape(r: ResolvedPadlockConfig) -> cq.Workplane:
    """Short shrouded U authored around the retained long-leg axis (shifted +X)."""
    h = K_BODY_H * r.body_height_scale
    arch_top = h + SHOULDER_H + 0.003 + K_LEG_OFFSET
    arch_center_z = arch_top - K_LEG_OFFSET
    short_leg_bottom = h - K_LEG_SEAT_DEPTH
    long_leg_bottom = h * 0.26

    torus_solid = cq.Solid.makeTorus(K_LEG_OFFSET, K_BAR_R)
    arch = cq.Workplane(obj=torus_solid).rotate((0, 0, 0), (1, 0, 0), 90.0)
    arch = arch.translate((0.0, 0.0, arch_center_z))
    half_box = (
        cq.Workplane("XY")
        .box(4.0 * K_LEG_OFFSET, 4.0 * K_BAR_R, 2.0 * (arch_top + K_LEG_OFFSET))
        .translate((0.0, 0.0, arch_center_z + (arch_top + K_LEG_OFFSET)))
    )
    arch = arch.intersect(half_box)
    long_len = arch_center_z - long_leg_bottom
    long_leg = (
        cq.Workplane("XY")
        .center(-K_LEG_OFFSET, 0.0)
        .circle(K_BAR_R)
        .extrude(long_len)
        .translate((0.0, 0.0, long_leg_bottom))
    )
    short_len = arch_center_z - short_leg_bottom
    short_leg = (
        cq.Workplane("XY")
        .center(K_LEG_OFFSET, 0.0)
        .circle(K_BAR_R)
        .extrude(short_len)
        .translate((0.0, 0.0, short_leg_bottom))
    )
    shackle = long_leg.union(short_leg).union(arch)
    shackle = shackle.edges("<Z").fillet(K_BAR_R * 0.45)
    return shackle.translate((K_LEG_OFFSET, 0.0, 0.0)), long_leg_bottom


# =========================================================================== #
# Combo body geometry (CadQuery).
# =========================================================================== #


def _orange_body_shell(r: ResolvedPadlockConfig) -> cq.Workplane:
    hw = C_BODY_W / 2.0
    h = C_BODY_H * r.body_height_scale
    chamf = C_CHAMF
    pts = [
        (-hw, chamf),
        (-hw + chamf, 0.0),
        (hw - chamf, 0.0),
        (hw, chamf),
        (hw, h - chamf),
        (hw - chamf, h),
        (-hw + chamf, h),
        (-hw, h - chamf),
    ]
    shell = (
        cq.Workplane("XZ")
        .polyline(pts)
        .close()
        .extrude(C_BODY_T)
        .translate((0.0, C_BODY_T / 2.0, 0.0))
    )
    shell = shell.edges("|Y").fillet(0.0035)
    return shell


def _shackle_bores(r: ResolvedPadlockConfig) -> cq.Workplane:
    body_top = C_BODY_H * r.body_height_scale
    bore_r = C_WIRE_R + 0.0006
    bores = None
    for sx in (-1.0, 1.0):
        b = (
            cq.Workplane("XY", origin=(sx * C_LEG_X, 0.0, body_top))
            .cylinder(0.030, bore_r, centered=(True, True, False))
            .translate((0.0, 0.0, -0.030))
        )
        bores = b if bores is None else bores.union(b)
    return bores


def _dial_pocket_cutter(r: ResolvedPadlockConfig) -> cq.Workplane:
    pocket_hx = DIAL_W / 2.0 + POCKET_CLEAR
    pocket_y_back = DIAL_AXLE_Y - DIAL_R - POCKET_CLEAR
    pocket_y_front = 0.014
    return (
        cq.Workplane("XY")
        .box(
            2.0 * pocket_hx,
            pocket_y_front - pocket_y_back,
            r.pocket_z_hi - r.pocket_z_lo,
            centered=(True, True, True),
        )
        .translate(
            (
                0.0,
                (pocket_y_front + pocket_y_back) / 2.0,
                (r.pocket_z_hi + r.pocket_z_lo) / 2.0,
            )
        )
    )


def _hasp_guide_channel(r: ResolvedPadlockConfig) -> cq.Workplane:
    body_top = C_BODY_H * r.body_height_scale
    channel_w = HASP_BAR_W + 0.002
    channel_l = C_BODY_W + 0.006
    channel_d = 0.0015
    return (
        cq.Workplane("XY", origin=(0.0, 0.0, body_top - channel_d))
        .box(channel_l, channel_w, channel_d + 0.001, centered=(True, True, False))
    )


def _build_combo_body_mesh(r: ResolvedPadlockConfig) -> object:
    # The combo body always carries the front dial window (access = dial_stack);
    # the straight_bar_hasp shackle additionally cuts a top guide channel.
    shell = _orange_body_shell(r)
    shell = shell.cut(_shackle_bores(r))
    shell = shell.cut(_dial_pocket_cutter(r))
    if r.shackle_module == "straight_bar_hasp":
        shell = shell.cut(_hasp_guide_channel(r))
    return shell


def _black_faceplate(r: ResolvedPadlockConfig) -> cq.Workplane:
    hw = C_BODY_W / 2.0
    h = C_BODY_H * r.body_height_scale
    inset = ORANGE_LIP + 0.0005
    plate_hw = hw - inset
    plate_top = h - inset
    plate_bot = inset
    plate_thk = 0.004
    front_y = C_BODY_T / 2.0
    plate = (
        cq.Workplane("XY")
        .box(2.0 * plate_hw, plate_thk, plate_top - plate_bot, centered=(True, True, True))
        .translate((0.0, front_y - plate_thk / 2.0, (plate_top + plate_bot) / 2.0))
    )
    plate = plate.edges("|Y").fillet(0.0035)
    plate = plate.cut(_dial_pocket_cutter(r))
    return plate


def _dial_window_frame(r: ResolvedPadlockConfig) -> cq.Workplane:
    pocket_hx = DIAL_W / 2.0 + POCKET_CLEAR
    win_w = 2.0 * pocket_hx
    win_h = r.pocket_z_hi - r.pocket_z_lo
    cz = (r.pocket_z_lo + r.pocket_z_hi) / 2.0
    front0 = C_BODY_T / 2.0
    front1 = front0 + 0.0020
    outer = (
        cq.Workplane("XY")
        .box(win_w + 0.006, (front1 - front0) + 0.003, win_h + 0.006, centered=(True, True, True))
        .translate((0.0, (front0 - 0.003 + front1) / 2.0, cz))
    )
    inner = (
        cq.Workplane("XY")
        .box(win_w, 0.012, win_h, centered=(True, True, True))
        .translate((0.0, (front0 + front1) / 2.0, cz))
    )
    return outer.cut(inner)


def _corner_rivets(r: ResolvedPadlockConfig) -> cq.Workplane:
    hw = C_BODY_W / 2.0 - ORANGE_LIP - 0.005
    h = C_BODY_H * r.body_height_scale
    z_top = h - ORANGE_LIP - 0.006
    z_bot = ORANGE_LIP + 0.006
    rivets = None
    for sx in (-1.0, 1.0):
        for sz in (z_bot, z_top):
            rr = (
                cq.Workplane("XZ", origin=(sx * hw, C_BODY_T / 2.0, sz))
                .cylinder(0.0015, 0.0016, direct=(0, 1, 0), centered=(True, True, False))
            )
            rivets = rr if rivets is None else rivets.union(rr)
    return rivets


def _build_dial_axles(r: ResolvedPadlockConfig) -> object:
    axle_half = (DIAL_W + 0.012) / 2.0
    axles = None
    for cz in r.dial_zs:
        a = (
            cq.Workplane("YZ", origin=(0.0, DIAL_AXLE_Y, cz))
            .circle(AXLE_R)
            .extrude(axle_half, both=True)
        )
        axles = a if axles is None else axles.union(a)
    return axles


def _build_hasp_guide_brackets(r: ResolvedPadlockConfig) -> object:
    """Two top guide brackets retaining the sliding hasp bar.

    Each bracket = a top plate above the bar + two pillars that embed deep into
    the (scaled) body top so the bracket is solidly carried by ``body_shell``
    (no floating island). A thin saddle bridge along the bar axis joins the two
    brackets into one connected element so the single ``hasp_brackets`` visual is
    not two disconnected islands.
    """
    body_top = C_BODY_H * r.body_height_scale
    plate_w = 0.012
    plate_l = HASP_BAR_W + 0.008
    plate_h = 0.002
    plate_z = body_top + HASP_BAR_H
    pillar_size = 0.003
    embed = 0.004  # how far the pillar reaches down into the body
    brackets = None
    for sx in (-1.0, 1.0):
        bx = sx * (HASP_GUIDE_SPAN / 2.0)
        b = (
            cq.Workplane("XY", origin=(bx, 0.0, plate_z))
            .box(plate_w, plate_l, plate_h, centered=(True, True, False))
        )
        for sy in (-1.0, 1.0):
            pillar_y = sy * (HASP_BAR_W / 2.0 + pillar_size / 2.0 + 0.0005)
            # pillar from (body_top - embed) up to the bottom of the plate.
            pillar_bot = body_top - embed
            pillar_h = plate_z - pillar_bot
            pillar = (
                cq.Workplane("XY", origin=(bx, pillar_y, pillar_bot))
                .box(pillar_size, pillar_size, pillar_h, centered=(True, True, False))
            )
            b = b.union(pillar)
        brackets = b if brackets is None else brackets.union(b)
    # Saddle bridge joining the two top plates so the visual is one island.
    bridge = (
        cq.Workplane("XY", origin=(0.0, 0.0, plate_z))
        .box(HASP_GUIDE_SPAN, plate_l, plate_h, centered=(True, True, False))
    )
    return brackets.union(bridge)


# --- Combo shackles ---------------------------------------------------------


def _short_u_shackle_shape(r: ResolvedPadlockConfig) -> object:
    """Short U authored in the LONG-LEG local frame (parent B)."""
    arch_top = C_SHACKLE_CLEAR * r.shackle_clear_scale + C_WIRE_R
    span = C_SHACKLE_SPAN
    crown_cy = arch_top - span / 2.0
    long_leg = (
        cq.Workplane("XY", origin=(0.0, 0.0, -C_LONG_LEG_BURY))
        .circle(C_WIRE_R)
        .extrude(C_LONG_LEG_BURY + crown_cy)
    )
    short_leg = (
        cq.Workplane("XY", origin=(span, 0.0, -C_SHORT_LEG_BURY))
        .circle(C_WIRE_R)
        .extrude(C_SHORT_LEG_BURY + crown_cy)
    )
    crown = (
        cq.Workplane("XY", origin=(0.0, 0.0, crown_cy))
        .circle(C_WIRE_R)
        .revolve(180.0, (span / 2.0, 0.0), (span / 2.0, 1.0))
    )
    return long_leg.union(crown).union(short_leg)


def _build_hasp_bar_mesh() -> object:
    """Straight hasp bar, bottom at z=0 (joint origin places it on body top)."""
    bar = cq.Workplane("XY").box(HASP_BAR_L, HASP_BAR_W, HASP_BAR_H, centered=(True, True, False))
    bar = bar.edges("|Z").fillet(0.004)
    notch_w = 0.007
    notch_h = HASP_BAR_W * 0.45
    notch = (
        cq.Workplane("XY", origin=(HASP_BAR_L / 2.0 - 0.004, 0.0, HASP_BAR_H / 2.0))
        .box(notch_w, notch_h, HASP_BAR_H + 0.002, centered=(True, True, True))
    )
    bar = bar.cut(notch)
    return bar


def _build_dial_mesh() -> object:
    """Single knurled combination dial; spin axis is local X."""
    wheel = cq.Workplane("YZ").circle(DIAL_R).extrude(DIAL_W / 2.0, both=True)
    n_teeth = 28
    cutter = None
    groove_depth = 0.0006
    for i in range(n_teeth):
        a = 2.0 * math.pi * i / n_teeth
        gy = (DIAL_R - groove_depth / 2.0) * math.cos(a)
        gz = (DIAL_R - groove_depth / 2.0) * math.sin(a)
        g = (
            cq.Workplane("YZ", origin=(0.0, gy, gz))
            .rect(0.0006, 0.0012)
            .extrude(DIAL_W / 2.0 + 0.0002, both=True)
            .rotate((0, 0, 0), (1, 0, 0), math.degrees(a))
        )
        cutter = g if cutter is None else cutter.union(g)
    wheel = wheel.cut(cutter)
    flat = (
        cq.Workplane("YZ", origin=(0.0, 0.0, DIAL_R + 0.0006))
        .rect(2.0 * DIAL_R, 0.0024)
        .extrude(DIAL_W / 2.0 + 0.0005, both=True)
    )
    wheel = wheel.cut(flat)
    bore = cq.Workplane("YZ", origin=(0.0, 0.0, 0.0)).circle(0.0040).extrude(DIAL_W, both=True)
    wheel = wheel.cut(bore)
    return wheel


# =========================================================================== #
# Body builders (dispatch on body_module).
# =========================================================================== #


def _build_keyed_body(model: ArticulatedObject, r: ResolvedPadlockConfig, mats: dict):
    body = model.part("body")
    shroud = r.shackle_module == "shrouded_u"

    if r.body_module == "rect_brass":
        body.visual(
            mesh_from_cadquery(_rect_body_shape(r, shroud=shroud), "body_shell"),
            material=mats["body"],
            name="body_shell", material_class_id="metal.brass_polished",
        )
        front_y = -K_BODY_D / 2.0
        # Keyway sits at mid-body height on the front face (the rect body base is
        # at z=0; centering the escutcheon keeps it on the body, not below ground).
        center_z = K_BODY_H * r.body_height_scale * 0.5
    elif r.body_module == "laminated_steel":
        for i in range(NUM_PLATES):
            body.visual(
                mesh_from_cadquery(_plate_shape(i, r), f"plate_{i}"),
                material=mats["plate_a"] if i % 2 == 0 else mats["plate_b"],
                name=f"plate_{i}", material_class_id="metal.steel_bare",
            )
        for i in range(NUM_RIVETS):
            body.visual(
                mesh_from_cadquery(_rivet_shape(i), f"rivet_{i}"),
                material=mats["rivet"],
                name=f"rivet_{i}", material_class_id="metal.stainless_matte",
            )
        front_y = -K_BODY_D / 2.0
        center_z = K_BODY_H * r.body_height_scale * 0.5
    else:  # round_discus
        body.visual(
            mesh_from_cadquery(_disc_body_shape(r), "body_shell"),
            material=mats["body"],
            name="body_shell", material_class_id="metal.brushed_silver",
        )
        front_y = -DISC_THICKNESS / 2.0
        center_z = DISC_RADIUS * r.body_height_scale  # keyway on circular front center

    # Keyway escutcheon (always present in keyed access modules).
    body.visual(
        mesh_from_cadquery(_keyway_disc_shape(front_y, center_z), "keyway_disc"),
        material=mats["chrome"],
        name="keyway_disc", material_class_id="metal.chrome_polished",
    )
    body.visual(
        mesh_from_cadquery(_keyway_slot_shape(front_y, center_z), "keyway_slot"),
        material=mats["slot"],
        name="keyway_slot", material_class_id="metal.blackened_gunmetal",
    )

    if r.access_module == "keyway_dust_cover":
        hinge_y = (front_y - DISC_T + DISC_EMBED) - 0.0003
        hinge_z = center_z + 0.0028 + 0.0072 + 0.0012
        body.visual(
            mesh_from_cadquery(
                _hinge_bracket_shape(front_y, hinge_y, hinge_z), "hinge_bracket"
            ),
            material=mats["chrome"],
            name="hinge_bracket", material_class_id="metal.chrome_polished",
        )

    return body, front_y, center_z


def _build_combo_body(model: ArticulatedObject, r: ResolvedPadlockConfig, mats: dict):
    body = model.part("body")
    body.visual(
        mesh_from_cadquery(_build_combo_body_mesh(r), "body_shell"),
        material=mats["body"],
        name="body_shell", material_class_id="metal.paint_coated",
    )
    # Combo access is always the dial stack: faceplate + bezel + rivets + axles.
    body.visual(
        mesh_from_cadquery(_black_faceplate(r), "faceplate"),
        material=mats["faceplate"],
        name="faceplate", material_class_id="metal.blackened_gunmetal",
    )
    body.visual(
        mesh_from_cadquery(_dial_window_frame(r), "dial_frame"),
        material=mats["dial"],
        name="dial_frame", material_class_id="metal.blackened_gunmetal",
    )
    body.visual(
        mesh_from_cadquery(_corner_rivets(r), "rivets"),
        material=mats["rivet"],
        name="rivets", material_class_id="metal.stainless_matte",
    )
    body.visual(
        mesh_from_cadquery(_build_dial_axles(r), "dial_axles"),
        material=mats["rivet"],
        name="dial_axles", material_class_id="metal.stainless_matte",
    )
    # straight_bar_hasp adds top guide brackets that retain the sliding bar.
    if r.shackle_module == "straight_bar_hasp":
        body.visual(
            mesh_from_cadquery(_build_hasp_guide_brackets(r), "hasp_brackets"),
            material=mats["rivet"],
            name="hasp_brackets", material_class_id="metal.stainless_matte",
        )
    return body


# =========================================================================== #
# Shackle / access builders.
# =========================================================================== #


def _build_keyed_shackle(model: ArticulatedObject, r: ResolvedPadlockConfig, mats: dict, body):
    """tall_u (single PRISMATIC) or shrouded_u (PRISMATIC lift -> REVOLUTE swing).

    The keyed shackle is authored in the BODY frame, so its lowest geometry (the
    long-leg bottom) sits well above z=0. We anchor the joint origin on that
    long-leg bottom so it lies inside both body and shackle geometry (baseline
    ``fail_if_articulation_origin_far_from_geometry``); a prismatic/revolute
    joint's motion is unaffected by where the origin sits along/around the axis.
    """
    if r.shackle_module == "tall_u":
        if r.body_module == "round_discus":
            shape, long_leg_bottom = _disc_tall_u_shackle_shape(r)
            travel = DISC_LEG_SEAT_DEPTH + 0.008
        else:
            shape, long_leg_bottom = _tall_u_shackle_shape(r)
            travel = K_LEG_SEAT_DEPTH + 0.006
        # Shift the shape down by long_leg_bottom so its lowest geometry sits at
        # local z=0 (joint-origin contract). The joint origin in the body frame
        # is then placed at z=long_leg_bottom, so the rendered world position is
        # unchanged, and the child AABB contains (0,0,0).
        shape = shape.translate((0.0, 0.0, -long_leg_bottom))
        shackle = model.part("shackle")
        shackle.visual(
            mesh_from_cadquery(shape, "shackle_bar"),
            material=mats["shackle"],
            name="shackle_bar", material_class_id="metal.stainless_matte",
        )
        model.articulation(
            "body_to_shackle",
            ArticulationType.PRISMATIC,
            parent=body,
            child=shackle,
            origin=Origin(xyz=(0.0, 0.0, long_leg_bottom)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(lower=0.0, upper=travel, effort=60.0, velocity=0.1),
        )
        return travel
    else:  # shrouded_u: two-stage (rect_brass only)
        shape, long_leg_bottom = _shrouded_u_shackle_shape(r)
        # The shrouded shape is authored around the retained long-leg axis at
        # x=0 (already shifted +K_LEG_OFFSET). Shift it down so its lowest
        # geometry is at local z=0 for the joint-origin contract.
        shape = shape.translate((0.0, 0.0, -long_leg_bottom))
        shackle_lift = model.part("shackle_lift")
        shackle = model.part("shackle")
        shackle.visual(
            mesh_from_cadquery(shape, "shackle_bar"),
            material=mats["shackle"],
            name="shackle_bar", material_class_id="metal.stainless_matte",
        )
        travel = SHOULDER_H + K_LEG_SEAT_DEPTH + 0.004
        # Lift joint: child shackle_lift is an empty kinematic frame; anchor its
        # origin at the retained long-leg position on the long-leg bottom z.
        model.articulation(
            "body_to_shackle",
            ArticulationType.PRISMATIC,
            parent=body,
            child=shackle_lift,
            origin=Origin(xyz=(-K_LEG_OFFSET, 0.0, long_leg_bottom)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(lower=0.0, upper=travel, effort=60.0, velocity=0.1),
        )
        # Swing joint: origin at the retained long-leg axis (shackle local x=0,
        # z=0 after the down-shift), so the child AABB contains the origin.
        model.articulation(
            "shackle_rotate",
            ArticulationType.REVOLUTE,
            parent=shackle_lift,
            child=shackle,
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(lower=0.0, upper=SHACKLE_SWING, effort=8.0, velocity=1.5),
        )
        return travel


def _build_combo_shackle(model: ArticulatedObject, r: ResolvedPadlockConfig, mats: dict, body):
    """short_u_revolve (PRISMATIC +Z) or straight_bar_hasp (PRISMATIC +X)."""
    body_top = C_BODY_H * r.body_height_scale
    if r.shackle_module == "short_u_revolve":
        shackle = model.part("shackle")
        shackle.visual(
            mesh_from_cadquery(_short_u_shackle_shape(r), "shackle_bar"),
            material=mats["shackle"],
            name="shackle_bar", material_class_id="metal.stainless_matte",
        )
        model.articulation(
            "body_to_shackle",
            ArticulationType.PRISMATIC,
            parent=body,
            child=shackle,
            origin=Origin(xyz=(-C_LEG_X, 0.0, body_top)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(
                lower=0.0, upper=C_SHACKLE_TRAVEL, effort=20.0, velocity=0.2
            ),
        )
        return C_SHACKLE_TRAVEL
    else:  # straight_bar_hasp
        hasp = model.part("hasp_bar")
        hasp.visual(
            mesh_from_cadquery(_build_hasp_bar_mesh(), "hasp_bar"),
            material=mats["shackle"],
            name="hasp_bar", material_class_id="metal.stainless_matte",
        )
        model.articulation(
            "body_to_hasp",
            ArticulationType.PRISMATIC,
            parent=body,
            child=hasp,
            origin=Origin(xyz=(0.0, 0.0, body_top)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(lower=0.0, upper=HASP_TRAVEL, effort=15.0, velocity=0.3),
        )
        return HASP_TRAVEL


def _build_dust_cover(
    model: ArticulatedObject, r: ResolvedPadlockConfig, mats: dict, body, front_y, center_z
):
    hinge_y = (front_y - DISC_T + DISC_EMBED) - 0.0003
    hinge_z = center_z + 0.0028 + 0.0072 + 0.0012
    dust_cover = model.part("dust_cover")
    dust_cover.visual(
        mesh_from_cadquery(_dust_cover_shape(), "cover_flap"),
        material=mats["cover"],
        name="cover_flap", material_class_id="metal.brass_polished",
    )
    model.articulation(
        "body_to_dust_cover",
        ArticulationType.REVOLUTE,
        parent=body,
        child=dust_cover,
        origin=Origin(xyz=(0.0, hinge_y, hinge_z)),
        axis=(-1.0, 0.0, 0.0),
        motion_limits=MotionLimits(lower=0.0, upper=COVER_OPEN_ANGLE, effort=2.0, velocity=2.0),
        mating=MatingContract(
            parent_face_geometry="hinge_bracket",
            parent_face_side="negative_y",
            child_face_geometry="cover_flap",
            child_face_side="positive_y",
            contact_tol=0.0030,
        ),
    )


def _build_dial_stack(model: ArticulatedObject, r: ResolvedPadlockConfig, mats: dict, body):
    for idx in range(r.dial_count):
        cz = r.dial_zs[idx]
        dial = model.part(f"dial_{idx + 1}")
        dial.visual(
            mesh_from_cadquery(_build_dial_mesh(), f"dial_{idx + 1}_wheel"),
            material=mats["dial"],
            name=f"dial_{idx + 1}_wheel", material_class_id="metal.blackened_gunmetal",
        )
        dial.visual(
            Cylinder(radius=DIAL_R * 0.985, length=DIAL_W * 0.42),
            origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["dial_band"],
            name=f"dial_{idx + 1}_band", material_class_id="metal.brushed_silver",
        )
        model.articulation(
            f"dial_{idx + 1}",
            ArticulationType.CONTINUOUS,
            parent=body,
            child=dial,
            origin=Origin(xyz=(0.0, DIAL_AXLE_Y, cz)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=1.0, velocity=4.0),
        )


# =========================================================================== #
# Materials + top-level build.
# =========================================================================== #


def _materials(model: ArticulatedObject, r: ResolvedPadlockConfig) -> dict:
    out = {}
    for key, rgba in r.palette.items():
        out[key] = model.material(f"padlock_{key}_{r.palette_style}", rgba=rgba)
    return out


def build_padlock(
    config: PadlockConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    config = config or PadlockConfig()
    r = resolve_config(config)
    if assets is None:
        assets = AssetContext(Path(tempfile.mkdtemp(prefix="articraft-padlock-")))
    model = ArticulatedObject(name=r.name, assets=assets)
    model.meta["slot_choices"] = [list(t) for t in slot_choices_for_config(r)]

    mats = _materials(model, r)

    if r.family == "keyed":
        body, front_y, center_z = _build_keyed_body(model, r, mats)
        _build_keyed_shackle(model, r, mats, body)
        if r.access_module == "keyway_dust_cover":
            _build_dust_cover(model, r, mats, body, front_y, center_z)
    else:  # combo
        body = _build_combo_body(model, r, mats)
        _build_combo_shackle(model, r, mats, body)
        if r.access_module == "dial_stack":
            _build_dial_stack(model, r, mats, body)

    return model


def build_seeded_padlock(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_padlock(config_from_seed(seed), assets=assets)


# --------------------------------------------------------------------------- #
# Slot choices.
# --------------------------------------------------------------------------- #


def slot_choices_for_config(r: ResolvedPadlockConfig) -> tuple[tuple[str, str], ...]:
    choices = [
        ("body_module", r.body_module),
        ("shackle_module", r.shackle_module),
        ("access_module", r.access_module),
    ]
    if r.access_module == "dial_stack":
        choices.append(("dial_count", f"dials_{r.dial_count}"))
    choices.append(("palette_style", r.palette_style))
    return tuple(choices)


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(resolve_config(config_from_seed(seed)))


# =========================================================================== #
# Tests.
# =========================================================================== #


def _declare_overlap_allowances(ctx: TestContext, model: ArticulatedObject, r: ResolvedPadlockConfig):
    parts = {p.name for p in model.parts}
    body = model.get_part("body")

    if r.family == "keyed":
        shackle = model.get_part("shackle")
        if r.body_module == "laminated_steel":
            for i in range(NUM_PLATES):
                ctx.allow_overlap(
                    body, shackle, elem_a=f"plate_{i}", elem_b="shackle_bar",
                    reason="Shackle legs seat inside the laminated plate stack bores.",
                )
            for i in range(NUM_RIVETS):
                ctx.allow_overlap(
                    body, shackle, elem_a=f"rivet_{i}", elem_b="shackle_bar",
                    reason="Through-rivet shafts can intersect the seated shackle legs.",
                )
        else:
            ctx.allow_overlap(
                body, shackle, elem_a="body_shell", elem_b="shackle_bar",
                reason="Shackle legs are intentionally seated inside the body bores when locked.",
            )
        if r.access_module == "keyway_dust_cover":
            cover = model.get_part("dust_cover")
            ctx.allow_overlap(
                body, cover, elem_a="keyway_disc", elem_b="cover_flap",
                reason="Closed dust cover shrouds the keyway disc (intentional cover).",
            )
            ctx.allow_overlap(
                body, cover, elem_a="hinge_bracket", elem_b="cover_flap",
                reason="Dust cover hangs from the hinge bracket barrel (captured pivot).",
            )
    else:  # combo
        if r.shackle_module == "short_u_revolve":
            shackle = model.get_part("shackle")
            ctx.allow_overlap(
                body, shackle, elem_a="body_shell", elem_b="shackle_bar",
                reason="Shackle legs ride inside the body bores (seated/captured fit).",
            )
        else:  # straight_bar_hasp
            hasp = model.get_part("hasp_bar")
            ctx.allow_overlap(
                body, hasp, elem_a="body_shell", elem_b="hasp_bar",
                reason="Hasp bar rides in the body guide channel (sliding fit).",
            )
            ctx.allow_overlap(
                body, hasp, elem_a="hasp_brackets", elem_b="hasp_bar",
                reason="Guide brackets retain the hasp bar (sliding fit).",
            )
        if r.access_module == "dial_stack":
            for idx in range(r.dial_count):
                dial = model.get_part(f"dial_{idx + 1}")
                ctx.allow_overlap(
                    body, dial, elem_a="dial_axles", elem_b=f"dial_{idx + 1}_wheel",
                    reason=f"Dial {idx + 1} is captured on its body axle inside the window pocket.",
                )
                ctx.allow_overlap(
                    body, dial, elem_a="body_shell", elem_b=f"dial_{idx + 1}_wheel",
                    reason=f"Dial {idx + 1} nests inside the body window pocket.",
                )


def run_padlock_tests(object_model: ArticulatedObject, config: PadlockConfig) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    _declare_overlap_allowances(ctx, object_model, r)

    part_names = {p.name for p in object_model.parts}
    joint_names = {a.name for a in object_model.articulations}
    body = object_model.get_part("body")

    # --- Identity: body is the single root --------------------------------- #
    ctx.check(
        "body present as root",
        "body" in part_names,
        details=str(sorted(part_names)),
    )

    body_aabb = ctx.part_world_aabb(body)
    assert body_aabb is not None
    body_top_z = body_aabb[1][2]

    # --- Family-specific release joint + retained insertion ----------------- #
    if r.shackle_module == "straight_bar_hasp":
        hasp = object_model.get_part("hasp_bar")
        joint = object_model.get_articulation("body_to_hasp")
        ctx.check(
            "hasp release joint is PRISMATIC along +X",
            joint.articulation_type == ArticulationType.PRISMATIC
            and abs(joint.axis[0]) > 0.99
            and abs(joint.axis[2]) < 0.01,
            details=f"type={joint.articulation_type}, axis={joint.axis}",
        )
        rest_pos = ctx.part_world_position(hasp)
        with ctx.pose({joint: HASP_TRAVEL}):
            open_pos = ctx.part_world_position(hasp)
        ctx.check(
            "hasp slides by the joint travel along X",
            rest_pos is not None and open_pos is not None
            and abs((open_pos[0] - rest_pos[0]) - HASP_TRAVEL) < 1e-4,
            details=f"rest_x={rest_pos[0]:.4f}, open_x={open_pos[0]:.4f}",
        )
        ctx.expect_overlap(
            hasp, body, axes="xy", min_overlap=0.003,
            name="hasp bar retained by the body guide at full travel",
        )
    else:
        shackle = object_model.get_part("shackle")
        joint = object_model.get_articulation("body_to_shackle")
        ctx.check(
            "shackle release joint is PRISMATIC along +Z",
            joint.articulation_type == ArticulationType.PRISMATIC
            and abs(joint.axis[2]) > 0.99
            and abs(joint.axis[0]) < 0.01 and abs(joint.axis[1]) < 0.01,
            details=f"type={joint.articulation_type}, axis={joint.axis}",
        )
        # Shackle arches above the body.
        sh_aabb = ctx.part_world_aabb(shackle)
        assert sh_aabb is not None
        ctx.check(
            "shackle arches above the body top",
            sh_aabb[1][2] > body_top_z + 0.010,
            details=f"shackle_top={sh_aabb[1][2]:.4f}, body_top={body_top_z:.4f}",
        )
        # Spans both legs in X (reads as a U).
        ctx.check(
            "shackle spans both legs in X",
            (sh_aabb[1][0] - sh_aabb[0][0]) > 0.018,
            details=f"x_span={sh_aabb[1][0] - sh_aabb[0][0]:.4f}",
        )
        # Lifting raises the shackle; long leg stays inserted.
        rest_bottom = ctx.part_world_aabb(shackle)[0][2]
        travel = joint.motion_limits.upper
        with ctx.pose({joint: travel}):
            lifted_bottom = ctx.part_world_aabb(shackle)[0][2]
        ctx.check(
            "lifting raises the shackle upward",
            lifted_bottom > rest_bottom + 0.4 * travel,
            details=f"rest_bottom={rest_bottom:.4f}, lifted_bottom={lifted_bottom:.4f}",
        )
        with ctx.pose({joint: travel}):
            ctx.expect_overlap(
                shackle, body, axes="z", min_overlap=0.002,
                elem_a="shackle_bar",
                elem_b="body_shell" if r.body_module != "laminated_steel" else "plate_2",
                name="long leg stays inserted at full travel (retained insertion)",
            )

    # --- Shrouded two-stage release ----------------------------------------- #
    if r.shackle_module == "shrouded_u":
        ctx.check(
            "shrouded shackle has a two-stage lift->swing joint chain",
            "shackle_lift" in part_names and "shackle_rotate" in joint_names,
            details=f"parts={sorted(part_names)}, joints={sorted(joint_names)}",
        )
        swing = object_model.get_articulation("shackle_rotate")
        ctx.check(
            "shackle_rotate is REVOLUTE about +Z",
            swing.articulation_type == ArticulationType.REVOLUTE
            and abs(swing.axis[2]) > 0.99,
            details=f"type={swing.articulation_type}, axis={swing.axis}",
        )

    # --- Keyed access: keyway escutcheon ----------------------------------- #
    if r.family == "keyed":
        body_shell_elem = "plate_2" if r.body_module == "laminated_steel" else "body_shell"
        shell_bb = ctx.part_element_world_aabb(body, elem=body_shell_elem)
        disc_bb = ctx.part_element_world_aabb(body, elem="keyway_disc")
        slot_bb = ctx.part_element_world_aabb(body, elem="keyway_slot")
        assert shell_bb is not None and disc_bb is not None and slot_bb is not None
        ctx.check(
            "keyway disc proud of the front face",
            disc_bb[0][1] < shell_bb[0][1] + 0.001,
            details=f"disc_front_y={disc_bb[0][1]:.4f}, shell_front_y={shell_bb[0][1]:.4f}",
        )
        ctx.check(
            "key slot proud of the keyway disc",
            slot_bb[0][1] < disc_bb[0][1] + 0.0001,
            details=f"slot_front_y={slot_bb[0][1]:.4f}, disc_front_y={disc_bb[0][1]:.4f}",
        )

    # --- Dust cover hinge --------------------------------------------------- #
    if r.access_module == "keyway_dust_cover":
        cover = object_model.get_part("dust_cover")
        cj = object_model.get_articulation("body_to_dust_cover")
        ctx.check(
            "dust cover is REVOLUTE about -X",
            cj.articulation_type == ArticulationType.REVOLUTE
            and abs(cj.axis[0] + 1.0) < 0.01,
            details=f"type={cj.articulation_type}, axis={cj.axis}",
        )
        rest = ctx.part_world_aabb(cover)
        with ctx.pose({cj: COVER_OPEN_ANGLE}):
            opened = ctx.part_world_aabb(cover)
        ctx.check(
            "opening the dust cover swings the flap outward/up",
            rest is not None and opened is not None
            and (opened[0][1] < rest[0][1] - 0.002 or opened[1][2] > rest[1][2] + 0.002),
            details=f"rest={rest}, opened={opened}",
        )

    # --- Dial stack: N dials, stacked, rotate ------------------------------ #
    if r.access_module == "dial_stack":
        dials = [object_model.get_part(f"dial_{i + 1}") for i in range(r.dial_count)]
        zs = []
        for i in range(r.dial_count):
            dj = object_model.get_articulation(f"dial_{i + 1}")
            ctx.check(
                f"dial_{i + 1} is CONTINUOUS about horizontal X",
                dj.articulation_type == ArticulationType.CONTINUOUS
                and abs(dj.axis[0]) > 0.99,
                details=f"type={dj.articulation_type}, axis={dj.axis}",
            )
            p = ctx.part_world_position(dials[i])
            zs.append(p[2] if p else None)
        ctx.check(
            f"{r.dial_count} dials stacked vertically in increasing Z order",
            all(z is not None for z in zs)
            and all(zs[i] < zs[i + 1] for i in range(r.dial_count - 1)),
            details=f"dial_z={zs}",
        )
        # First dial rim protrudes past the faceplate front.
        front_face_y = C_BODY_T / 2.0
        d0 = ctx.part_world_aabb(dials[0])
        ctx.check(
            "dial rims protrude past the front face window",
            d0 is not None and d0[1][1] >= front_face_y - 1e-3,
            details=f"dial_front_y={d0[1][1] if d0 else None}, face_y={front_face_y}",
        )
        # Rotating a dial spins it.
        dj0 = object_model.get_articulation("dial_1")
        rim_rest = ctx.part_element_world_aabb(dials[0], elem="dial_1_wheel")
        with ctx.pose({dj0: math.pi / 2.0}):
            rim_turn = ctx.part_element_world_aabb(dials[0], elem="dial_1_wheel")
        ctx.check(
            "dial_1 rotates about its axle",
            rim_rest is not None and rim_turn is not None
            and (abs(rim_turn[1][1] - rim_rest[1][1]) > 1e-4
                 or abs(rim_turn[1][2] - rim_rest[1][2]) > 1e-4),
            details=f"rest_max={rim_rest[1] if rim_rest else None}, turn_max={rim_turn[1] if rim_turn else None}",
        )

    # --- Ground contact ----------------------------------------------------- #
    all_parts = list(object_model.parts)
    aabbs = [ctx.part_world_aabb(p) for p in all_parts if ctx.part_world_aabb(p) is not None]
    lo_z = min(a[0][2] for a in aabbs)
    ctx.check(
        "padlock rests near the ground plane",
        -0.006 <= lo_z <= 0.012,
        details=f"min_z={lo_z:.4f}",
    )

    return ctx.report()


__all__ = [
    "PadlockConfig",
    "ResolvedPadlockConfig",
    "build_padlock",
    "build_seeded_padlock",
    "config_from_seed",
    "resolve_config",
    "run_padlock_tests",
    "slot_choices_for_seed",
    "__modular__",
]
