# SPDX-License-Identifier: Apache-2.0

"""Chain separator modular template (pictureX / 0611 / Chain_separator).

A manual **chain breaker / chain pin press**: a rigid reaction frame carrying ONE
aligned driver that advances along ONE working axis into a chain cradle, so the
reaction path visibly closes ``driver -> chain -> cradle -> frame -> driver``.

Sourced from ``articraft_template_authoring/specs_modular_v1/pictureX_0611_Chain_separator.md``
and the 8-record 5-star pool (1 picture origin + 7 single-axis forks) under
``data/records/rec_picturex_0611__chain_separator__001__png_*`` /
``data/records/rec_picturex0611_chain_separator_fork_*``:

  * S1 = ``rec_picturex_0611__chain_separator__001__png_21cece9ed04f4870b0d43f804d878f13``
  * S2 = ``rec_picturex0611_chain_separator_fork_bench_c_frame_20260714``
  * S3 = ``rec_picturex0611_chain_separator_fork_twin_plate_bridge_20260714``
  * S4 = ``rec_picturex0611_chain_separator_fork_ratchet_socket_drive_20260714``
  * S5 = ``rec_picturex0611_chain_separator_fork_toggle_lever_drive_20260714``
  * S6 = ``rec_picturex0611_chain_separator_fork_rotating_anvil_turret_20260714``
  * S7 = ``rec_picturex0611_chain_separator_fork_adjustable_chain_guide_20260714``
  * S8 = ``rec_picturex0611_chain_separator_fork_mounting_flange_20260714``

Structure (pattern = ``mixed``) — a single root ``frame`` part with parallel
children, one of which (the drive) is itself a serial chain:

  * ``frame_form`` (4, (1)+(3) Primary Form Family): compact_cast_handheld (S1 —
    Planar Boundary Form) / bench_c_frame (S2 — Volumetric Envelope Form) /
    twin_cheek_plates (S3 — Macro Surface Construction) /
    flanged_bench_pedestal (S8 — Planar Boundary + grounded pedestal).
  * ``drive_form`` (3, (2)): screw_tbar (P->R->P, S1) / ratchet_socket (P->R->R,
    S4) / compound_toggle (P + frame-rooted R->R, S5).
  * ``cradle_form`` (3, (1)/(2)/(3)): stepped_ledge_anvil (S1, static) /
    grooved_pad_anvil (S2, static) / rotating_seat_turret (S6, +1 REVOLUTE part).
  * ``chain_guide`` (2, (1)/(2)): none (S1/S2/S8 baseline) /
    sliding_cheek_guide (S7, +1 PRISMATIC part).
  * (6) ``palette_style`` (5 realistic colorways) drives EVERY ``.visual(material=)``.

**Canonical body frame** (spec section 13 — the key decision). S2 proves the drive
is axis-portable: it re-poses S1's byte-identical drive helpers onto
``SPINDLE_AXIS=(0,0,-1)`` / ``BAR_AXIS=(0,1,0)``. This template adopts S2's
convention as the SINGLE root frame for all four frame_forms:

    working axis  a = (0, 0, -1)   driver descends into the cradle
    body normal   b = (0, 1, 0)    T-bar / fold / turret axis
    transverse    h = (1, 0, 0)    guide traverse; throat opens toward +X
    cradle seat   z ~= 0

S1's in-plane profile is re-based into this frame (its ``BAR_AXIS=(0,0,1)`` maps
onto world ``(0,1,0)`` — exactly S2's). One root frame is what makes the
compatibility matrix EMPTY (72/72 combos legal, spec section 9) instead of the
19-combo gated domain a two-frame design would force.

Source-consistency correction (documented, not silent): S1's photo-matched layout
puts its spindle line ~31mm off its own anvil ledges, contradicting its own
``authoritative_features=("aligned_driver",...)``. The canonical layout places the
driver ON the cradle centerline, as the subcategory contract requires. Part tree,
joint topology, per-part visual counts and primitive types are all preserved
(Rule 3); only the layout is made self-consistent.

Rule compliance:
  * Rule 1 — anvil ledges/pads, flange, bolt holes, ribs, gussets, bosses, spacers,
    turret seats and the hanging hole are all ``parent.visual(...)`` / fused host
    geometry. NO FIXED articulation exists in this template.
  * Rule 2 — ``guide_slide`` is the only joint whose geometry is two axis-aligned
    faces in contact; it declares a real ``MatingContract`` (+tangential_containment).
    Every other joint is captured-pin / rod-in-sleeve geometry and OMITS ``mating=``
    under the AUTHORING Rule 2 grandfather (each carries a comment naming the
    captured geometry) — mirroring ``rivet_squeeze`` (omits on all joints) and
    ``tube_cutter`` (omits on its roller/wheel pivots).
  * Rule 3 — ``mesh_from_cadquery`` over polygon + ``threePointArc`` profiles is
    preserved everywhere the sources used it; no Box/Cylinder downgrade of the
    frame silhouette.
  * Rule 7 — NO whole-part ``allow_overlap`` and NO ``allow_isolated_part``
    (the source records use both; this template replaces them with deliberate
    0.1-0.4mm capture interference so the parts genuinely touch).
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
    MatingContract,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    clamp_joint_limits,
    mesh_from_cadquery,
)

__modular__ = True


# ---------------------------------------------------------------------------
# Slot enum types
# ---------------------------------------------------------------------------
FrameForm = Literal[
    "compact_cast_handheld",
    "bench_c_frame",
    "twin_cheek_plates",
    "flanged_bench_pedestal",
]
DriveForm = Literal["screw_tbar", "ratchet_socket", "compound_toggle"]
CradleForm = Literal["stepped_ledge_anvil", "grooved_pad_anvil", "rotating_seat_turret"]
ChainGuide = Literal["none", "sliding_cheek_guide"]
PaletteStyle = Literal[
    "black_blue_enamel",
    "blue_enamel_bench",
    "forged_steel_natural",
    "zinc_hardware",
    "black_rubber_shop",
]

FRAME_FORMS: tuple[FrameForm, ...] = (
    "compact_cast_handheld",
    "bench_c_frame",
    "twin_cheek_plates",
    "flanged_bench_pedestal",
)
DRIVE_FORMS: tuple[DriveForm, ...] = ("screw_tbar", "ratchet_socket", "compound_toggle")
CRADLE_FORMS: tuple[CradleForm, ...] = (
    "stepped_ledge_anvil",
    "grooved_pad_anvil",
    "rotating_seat_turret",
)
CHAIN_GUIDES: tuple[ChainGuide, ...] = ("none", "sliding_cheek_guide")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "black_blue_enamel",
    "blue_enamel_bench",
    "forged_steel_natural",
    "zinc_hardware",
    "black_rubber_shop",
)

# (3) Primary Form Family subtype tags (spec section 8.5 axis 3).
FRAME_FORM_SUBTYPE: dict[FrameForm, str] = {
    "compact_cast_handheld": "planar_boundary_form",
    "bench_c_frame": "volumetric_envelope_form",
    "twin_cheek_plates": "macro_surface_construction",
    "flanged_bench_pedestal": "planar_boundary_form_grounded_pedestal",
}
CRADLE_FORM_SUBTYPE: dict[CradleForm, str] = {
    "stepped_ledge_anvil": "planar_boundary_form",
    "grooved_pad_anvil": "macro_surface_construction",
    "rotating_seat_turret": "volumetric_envelope_form",
}

# ---------------------------------------------------------------------------
# (6) Per-seed colorways. Keys drive EVERY .visual(material=...).
# Material classes: painted (enamel) / metal (machined, forged, zinc) /
# rubber (ratchet overmold grip) => 3 classes >= ceil(0.5 * 5) = 3.
# Sources: S1 L260-L262, S2 L327-L329, S3 L307-L310, S4 L332-L334, S5 L374-L376.
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    # S1 origin: black_cast + bright_blue_steel + machined_steel.
    "black_blue_enamel": {
        "body": (0.035, 0.040, 0.045, 1.0),
        "accent": (0.015, 0.39, 0.72, 1.0),
        "hardware": (0.60, 0.62, 0.55, 1.0),
        "driver": (0.72, 0.75, 0.77, 1.0),
        "grip": (0.10, 0.10, 0.12, 1.0),
        "seat": (0.62, 0.65, 0.68, 1.0),
    },
    # S2 bench fork read as a blue-enamel bench tool with black accents.
    "blue_enamel_bench": {
        "body": (0.020, 0.34, 0.62, 1.0),
        "accent": (0.045, 0.050, 0.055, 1.0),
        "hardware": (0.55, 0.57, 0.60, 1.0),
        "driver": (0.75, 0.77, 0.79, 1.0),
        "grip": (0.055, 0.055, 0.065, 1.0),
        "seat": (0.66, 0.69, 0.71, 1.0),
    },
    # S4 ratchet fork: bare forged / machined steel throughout.
    "forged_steel_natural": {
        "body": (0.46, 0.47, 0.48, 1.0),
        "accent": (0.30, 0.31, 0.32, 1.0),
        "hardware": (0.68, 0.70, 0.72, 1.0),
        "driver": (0.78, 0.80, 0.82, 1.0),
        "grip": (0.10, 0.10, 0.12, 1.0),
        "seat": (0.58, 0.60, 0.62, 1.0),
    },
    # S3 twin-plate fork: zinc-spacer-led galvanized hardware.
    "zinc_hardware": {
        "body": (0.60, 0.62, 0.55, 1.0),
        "accent": (0.44, 0.46, 0.40, 1.0),
        "hardware": (0.72, 0.74, 0.68, 1.0),
        "driver": (0.80, 0.82, 0.84, 1.0),
        "grip": (0.14, 0.14, 0.15, 1.0),
        "seat": (0.52, 0.54, 0.50, 1.0),
    },
    # S5 lever_dark + S4 rubber_grip: black shop tool.
    "black_rubber_shop": {
        "body": (0.070, 0.080, 0.090, 1.0),
        "accent": (0.80, 0.36, 0.06, 1.0),
        "hardware": (0.38, 0.39, 0.40, 1.0),
        "driver": (0.70, 0.72, 0.74, 1.0),
        "grip": (0.045, 0.045, 0.050, 1.0),
        "seat": (0.60, 0.62, 0.64, 1.0),
    },
}


# ---------------------------------------------------------------------------
# Canonical layout constants (meters), scale 1.0. See the module docstring for
# the axis convention. Every value carries a one-line source basis (Contract 3e).
# ---------------------------------------------------------------------------
# Working axis / body normal / transverse (S2 L26-L28, adopted as canonical).
A_AXIS = (0.0, 0.0, -1.0)  # driver advance
B_AXIS = (0.0, 1.0, 0.0)  # body normal: T-bar slide, ratchet fold, turret index
H_AXIS = (1.0, 0.0, 0.0)  # transverse: guide traverse

_BODY_HALF_Y = 0.008  # S1 L66 thickness=0.016 -> half
_CHANNEL_W = 0.010  # chain channel width: S2 L176 groove 0.010 == S3 L47 PLATE_GAP

# C-body stations in the working plane (u=x, v=z). Throat opens toward +X.
_BACK_X0 = -0.046  # rear face of the back column
_BACK_X1 = -0.026  # throat back wall (front face of the column)
_LOWER_ARM_X1 = 0.056  # lower arm front edge
_UPPER_ARM_X1 = 0.040  # upper arm front edge (grip continues beyond)
_LOWER_Z0 = -0.030  # underside of the lower arm
_CRADLE_Z = 0.000  # cradle seat plane == lower arm top == reaction datum
_THROAT_Z1 = 0.030  # throat ceiling == underside of the upper arm
_UPPER_Z1 = 0.052  # top of the upper arm
_GRIP_X1 = 0.160  # S1 L72-L74 grip tip station (rounded product end)

# Driver carriage stations measured along a from the driver_feed joint origin.
# Stack ORDER, primitive types and per-piece radii are S1 L168-L181
# (_spindle_carriage_shape) verbatim; the two stations that bind the driver to
# ANOTHER part (the core-shaft length and the thread station) are derived below,
# because on the canonical centreline they are relations, not free attributes
# (Contract 3e). See `_C_SHAFT_L` and `_thread_band_t` for the derivations.
_C_TENON_T, _C_TENON_R = 0.0135, 0.00500  # r: S1 0.00475 -> +0.3mm capture
_C_TENON_L = 0.0025
_C_SHAFT_T, _C_SHAFT_R = 0.016, 0.0042
_C_THREAD_L, _C_THREAD_R = 0.027, 0.0074
_C_CREST_R = 0.0095  # S1 L176 0.0086 -> interference with the nut bore
_C_CREST_N, _C_CREST_DT, _C_CREST_L = 7, 0.0040, 0.0017  # S1 L174-L177
_C_THRUST_T, _C_THRUST_L, _C_THRUST_R = 0.086, 0.008, 0.0072
_C_NECK_T, _C_NECK_L, _C_NECK_R = 0.094, 0.009, 0.0048
_C_CONE_T, _C_CONE_L = 0.103, 0.014  # S1 L181
_C_CONE_R0, _C_CONE_R1 = 0.0030, 0.0020
_C_TIP_T = _C_CONE_T + _C_CONE_L  # 0.117 — the pin tip

# equation: the core shaft ENDS where the guide neck begins, so the neck -> cone
# step is the only thing that enters the cradle.
# S1 L169 hard-codes the core length as 0.100 (t=0.016..0.116), which runs the
# 8.4mm-diameter core to within 1mm of the tip and BURIES the thrust collar, the
# guide neck and the whole cone pin inside it — S1's spindle has no exposed pin at
# all. That is invisible in S1 only because S1's spindle line misses its own anvil
# ledges by ~31mm (the source-consistency correction in the module docstring). On
# the canonical centreline the core length becomes a relation: an un-derived 0.100
# rams the core straight through the anvil/lower arm at full feed.
_C_SHAFT_L = _C_NECK_T - _C_SHAFT_T  # 0.078

# The thread band stops this far short of the thrust collar (S1 L173-L179 keeps
# the crest band clear of the collar; 0.027 collar + gap must fit before t=0.086).
_THREAD_THRUST_GAP = 0.004
# equation: the thread band's station along a. S1 L173-L177 puts the crests 0.018m
# from the spindle rear because S1's nut sleeve happens to sit there; here the
# tapped boss is fused into the upper arm instead, so the band follows the collar.
_C_THREAD_T = _C_THRUST_T - _THREAD_THRUST_GAP - _C_THREAD_L  # 0.055
_C_CREST_BAND_L = (_C_CREST_N - 1) * _C_CREST_DT + _C_CREST_L  # 0.0257

# Capture interference: every rod/pin in this template sits this far INSIDE its
# bore so the pair genuinely touches. This is what replaces the source records'
# forbidden allow_isolated_part (spec Reject cases 1-2).
_CAPTURE_FIT = 0.0003

# Frame nut boss (S1 L126-L133 sleeve). Its span is derived from the upper arm and
# the thread band (see ResolvedChainSeparatorConfig.nut_boss_z0/z1).
_NUT_BORE_R = 0.0091 - 0.0009  # S1 L139 bore 0.0091 -> 0.0082; the crests bite it
_NUT_WALL = 0.0030  # boss wall thickness outside the casting's clearance bore
_NUT_PROUD = 0.004  # boss top stands this far past the retracted thread band
# equation: the casting's clearance bore must CLEAR the thread crests — only the
# tapped boss engages them. S1 L139 bore 0.0091 vs S1 L176 crest 0.0086 = +0.5mm;
# this template raised the crest to 0.0095 for the nut interference, so a copied
# 0.0091 bore would make the crests bite the casting itself.
_CREST_BORE_CLEAR = 0.0005
_ARM_BORE_R = _C_CREST_R + _CREST_BORE_CLEAR  # 0.0100

# Driver tip rest clearance above the cradle datum -> fixes the joint origin.
# equation: the retracted pin must clear a chain laid on the seat, otherwise the
# tool cannot be loaded. A 1/2"-pitch roller chain (the bicycle/motorcycle chain
# this subcategory separates) stands ~7.1mm from its seated plate edge to the
# rivet head; +3mm to drop it in under the pin by hand.
_CHAIN_STACK_H = 0.0071  # 1/2"-pitch roller chain plate height (ANSI #41)
_CHAIN_LOAD_CLEAR = 0.0030
_TIP_REST_CLEAR = _CHAIN_STACK_H + _CHAIN_LOAD_CLEAR  # 0.0101

_FEED_LOWER = -0.005  # S1 L335
_FEED_UPPER = 0.012  # S2 L412
_FEED_UPPER_TOGGLE = 0.010  # S5 L451
_PIN_RELIEF_R = 0.0035  # relief bore below the seat, > cone base r 0.0030
_RELIEF_MOUTH_UP = 0.002  # the relief bore's mouth stands this far above the seat
_PIN_STOP_CLEAR = 0.0010  # the guide neck stops this far above the relief mouth
_TURRET_TIP_CLEAR = 0.0012  # the pin stops this far above the turret's anvil crown
_TURRET_FLOOR_MIN = 0.0030  # casting left under the turret pocket

# Spindle hub (S1 L185-L221).
_HUB_R, _HUB_L = 0.0115, 0.016
_HUB_AXIAL_BORE_R = 0.0047  # S1 L204; tenon 0.0050 -> +0.3mm capture
_HUB_BAR_BORE_R = 0.0052  # S1 L216
_HUB_CENTER_T = 0.008  # S1 L188 hub center along a from the joint origin

# T-bar (S1 L224-L243).
_BAR_R = 0.0052 + 0.0003  # S1 L239 0.0046 -> 0.0055 for +0.3mm bore capture
_BAR_HALF_L = 0.068  # S1 L227
_BAR_STOP_R = 0.0062  # S1 L241; > bar bore -> retained
_BAR_TRAVEL = 0.030  # S1 L363-L364

# Ratchet head + handle (S4 L200-L309, L443-L445).
_RH_R, _RH_L = 0.013, 0.018  # S4 L51, L207
_RH_KNURL_DR, _RH_KNURL_L = 0.0018, 0.005  # S4 L216
_RH_BOSS_R, _RH_BOSS_L = 0.0055, 0.014  # S4 L224-L228
_RH_NUB_R, _RH_NUB_L = 0.0018, 0.005  # S4 L237
_HANDLE_L, _HANDLE_W, _HANDLE_TH = 0.060, 0.011, 0.006  # S4 L62-L64
_GRIP_L, _GRIP_W, _GRIP_TH = 0.032, 0.014, 0.010  # S4 L65-L67
_FOLD_UPPER = 1.8  # S4 L444
_FOLD_AXIS = (0.0, -1.0, 0.0)  # -b: positive fold lifts the handle off the cradle
_RATCHET_FOLD_CLEAR = 0.0012  # running clearance in the head's fold clevis

# Toggle linkage (S5 L46-L91, L275-L352, L462-L486).
_LEVER_L, _LEVER_W, _LEVER_TH = 0.095, 0.012, 0.006  # S5 L56, L276-L277
_LEVER_GRIP_W = 0.015  # S5 L278
_LEVER_HOLE_R = 0.006  # S5 L309
# equation: the frame boss is captured IN the lever's pivot hole. A hand-written
# 0.0045 sat 1.5mm inside a 0.006 hole and never touched the lever — the lever and
# link hung off the pedestal riser they were grinding through, and the moment that
# riser was pulled out of the swing plane the whole toggle chain floated free.
_LEVER_PIVOT_R = _LEVER_HOLE_R + _CAPTURE_FIT  # 0.0063
_TOGGLE_ATTACH = 0.028  # S5 L57
_LINK_HOLE_R = 0.0035  # S5 L338
# equation: same capture, one joint down the chain (S5 L299-L303 boss in L338 hole).
_TOGGLE_BOSS_R = _LINK_HOLE_R + _CAPTURE_FIT  # 0.0038
_TOGGLE_BOSS_L = 0.010  # S5 L299-L303
_LINK_W, _LINK_TH = 0.010, 0.005  # S5 L322-L323
_LEVER_UPPER = 1.0  # S5 L468
_TOGGLE_LOWER, _TOGGLE_UPPER = -0.4, 0.6  # S5 L484-L485
_TOGGLE_CLEAR = 0.002  # link swept envelope clearance over the frame top face
_LEVER_YOKE_TH = 0.003  # each pedestal cheek carrying the lever pivot pin
_LEVER_YOKE_CLEAR = 0.0012  # running gap between the lever arm and each yoke cheek
_ROD_R = 0.0070  # S5 smooth driver rod
# equation: the guide rings ride INSIDE the nut bore — that engagement is the only
# thing supporting the toggle rod, so the ring radius derives from the bore.
# A hand-written 0.0072 (below the 0.0082 bore) left a 1mm annular GAP and the
# whole driver_carriage part floated free of the frame (fail_if_isolated_parts).
_ROD_RING_R = _NUT_BORE_R + _CAPTURE_FIT  # 0.0085
_ROD_RING_L = 0.004  # S5 ring width

# Anvil turret (S6 L45-L60, L235-L281).
_TURRET_R = 0.013  # S6 L47
_TURRET_BORE_R = 0.0033  # S6 L51
_TURRET_PIN_R = _TURRET_BORE_R + _CAPTURE_FIT  # S6 L50 0.003 -> capture fit in the bore
_TURRET_POCKET_DR = 0.0008  # S6 L49 pocket 0.0138 vs disk 0.013
# NOTE: there is no `_TURRET_CENTER_Z` constant. The disk's centre height is a
# relation (the anvil crown IS the cradle seat plane) and is derived in
# ResolvedChainSeparatorConfig.turret_center_z. A hand-written -0.006 put the crown
# 7mm ABOVE the seat datum, i.e. above the retracted driver tip, so the pin was
# buried in the anvil before the joint even moved.
# S6 L56-L60: three chain-gauge seats at 120deg (1/8" / 3/32" / 11-speed).
_TURRET_NOTCH_SPECS: tuple[tuple[float, float, float], ...] = (
    (math.pi / 2.0, 0.0040, 0.0032),
    (math.pi / 2.0 + 2.0 * math.pi / 3.0, 0.0030, 0.0032),
    (math.pi / 2.0 + 4.0 * math.pi / 3.0, 0.0025, 0.0032),
)

# Cradle footprint stations. These are the SINGLE statement of where each cradle's
# raised anvil features sit on the seat plane (Contract 3c) — consumed by
# `_apply_cradle_cuts` to build them AND by the sliding guide's seat, which has to
# clear them across its whole stroke.
_LEDGE_SPECS: tuple[tuple[float, float, float], ...] = (  # (dx, width, height)
    (-0.011, 0.010, 0.004),  # S1 L112-L123
    (0.011, 0.013, 0.005),
)
_PAD_DX, _PAD_W, _PAD_H = 0.017, 0.010, 0.004  # S2 L197-L209

# Sliding chain guide (S7 L244-L306, L483-L484).
_GUIDE_SEAT_X = 0.0365  # S7 nominal rail-seat station (a lower bound; see guide_seat_x)
_GUIDE_CRADLE_CLEAR = 0.0015  # the guide base clears the anvil features by this much
_GUIDE_BASE_LEN, _GUIDE_BASE_DEPTH, _GUIDE_BASE_H = 0.020, 0.016, 0.005  # S7 L246-L248
_GUIDE_TONGUE_LEN, _GUIDE_TONGUE_H = 0.012, 0.004  # S7 L251-L253
_GUIDE_CHEEK_TH, _GUIDE_CHEEK_H, _GUIDE_CHEEK_D = 0.003, 0.012, 0.014  # S7 L256-L258
_GUIDE_KNOB_R, _GUIDE_KNOB_L = 0.003, 0.004  # S7 L292
_GUIDE_TRAVEL = 0.005  # S7 L483-L484 (0.008) shrunk to fit the derived slot
_GUIDE_SLOT_MARGIN = 0.003

# Bench C-frame extras (S2).
_FOOT_X0, _FOOT_X1 = -0.052, 0.030  # S2 L107-L112 bolting foot
_FOOT_Z0, _FOOT_Z1 = -0.042, -0.030
_FOOT_HALF_Y = 0.034  # S2 L56 BASE_WIDTH/2
_BOLT_R = 0.004  # S2 L57 / S8 L180

# Flanged pedestal extras (S8 L163-L176).
_FLANGE_X0, _FLANGE_X1 = -0.032, 0.052
_FLANGE_Z0, _FLANGE_Z1 = -0.076, -0.030

# Twin cheek plates (S3 L45-L54).
_PLATE_TH = 0.003  # S3 L46

_EPS = 1e-4


# ---------------------------------------------------------------------------
# Config dataclasses
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ChainSeparatorConfig:
    frame_form: FrameForm | None = None
    drive_form: DriveForm | None = None
    cradle_form: CradleForm | None = None
    chain_guide: ChainGuide | None = None
    palette_style: PaletteStyle = "black_blue_enamel"
    overall_scale: float = 1.0
    body_thickness_scale: float = 1.0
    throat_depth_scale: float = 1.0
    handle_len_scale: float = 1.0
    feed_travel_scale: float = 1.0
    name: str = "pictureX_0611_Chain_separator"


@dataclass(frozen=True)
class ResolvedChainSeparatorConfig:
    frame_form: FrameForm
    drive_form: DriveForm
    cradle_form: CradleForm
    chain_guide: ChainGuide
    palette_style: PaletteStyle
    overall_scale: float
    body_thickness_scale: float
    throat_depth_scale: float
    handle_len_scale: float
    feed_travel_scale: float
    # Derived (spec section 7 equations / inequalities).
    body_half_y: float
    cradle_channel_w: float
    turret_thickness: float
    turret_radius: float
    guide_cheek_gap: float
    guide_travel: float
    guide_slot_len: float
    feed_lower: float
    feed_upper: float
    t_bar_travel: float
    name: str

    # --- Layout anchors: the ONLY statement of each shared quantity (Contract 3c).
    @property
    def s(self) -> float:
        return self.overall_scale

    @property
    def back_x0(self) -> float:
        return _BACK_X0 * self.s

    @property
    def back_x1(self) -> float:
        return _BACK_X1 * self.s * self.throat_depth_scale

    @property
    def lower_arm_x1(self) -> float:
        return _LOWER_ARM_X1 * self.s

    @property
    def upper_arm_x1(self) -> float:
        return _UPPER_ARM_X1 * self.s

    @property
    def lower_z0(self) -> float:
        return _LOWER_Z0 * self.s

    @property
    def cradle_z(self) -> float:
        return _CRADLE_Z

    @property
    def throat_z1(self) -> float:
        return _THROAT_Z1 * self.s

    @property
    def upper_z1(self) -> float:
        return _UPPER_Z1 * self.s

    @property
    def grip_x1(self) -> float:
        return _GRIP_X1 * self.s * self.handle_len_scale

    @property
    def throat_half_x(self) -> float:
        """Half-width of the usable throat around the driver axis."""
        return min(abs(self.back_x1), self.upper_arm_x1) * 0.95

    @property
    def tip_rest_z(self) -> float:
        """Height of the driver pin tip at feed=0 — the SINGLE statement of the
        pin<->cradle relation (Contract 3c). Everything on the driver stacks off it."""
        return self.cradle_z + _TIP_REST_CLEAR * self.s

    @property
    def spindle_rear_z(self) -> float:
        """driver_feed joint origin height: set so the pin tip rests at `tip_rest_z`."""
        return self.tip_rest_z + _C_TIP_T * self.s

    @property
    def relief_mouth_z(self) -> float:
        """Mouth of the frame's pin-relief bore — the single statement of "how far
        below the seat the pushed-out chain pin and the driver tip may go".
        Consumed by `_cut_working_bores` AND by the feed_upper inequality."""
        return self.cradle_z + _RELIEF_MOUTH_UP * self.s

    @property
    def thread_band_z1(self) -> float:
        """Top of the driver's thread band at feed=0 (world z)."""
        return self.spindle_rear_z - _C_THREAD_T * self.s

    @property
    def thread_band_z0(self) -> float:
        """Bottom of the driver's thread band at feed=0 (world z)."""
        return self.spindle_rear_z - (_C_THREAD_T + _C_CREST_BAND_L) * self.s

    @property
    def nut_boss_z0(self) -> float:
        """Underside of the tapped nut boss = the REALIZED upper-arm underside, so
        the boss is fused through the whole arm (S1 L126-L133 fuses its sleeve into
        the cast head) and never hangs down into the throat."""
        return self.throat_z1

    @property
    def nut_boss_z1(self) -> float:
        """Top of the tapped nut boss — DERIVED so the boss still houses the thread
        band with the driver fully retracted. The thread<->nut engagement is a
        relation: stating the boss span as its own literal (the old
        `_NUT_T0/_NUT_T1 = 0.030/0.077`) let the boss drift off the arm it is
        supposed to be fused into."""
        return self.thread_band_z1 - self.feed_lower + _NUT_PROUD * self.s

    @property
    def nut_boss_outer_r(self) -> float:
        """Boss outer radius: a real wall outside the casting's clearance bore, so
        the boss has material to fuse into the arm (and, on twin_cheek_plates, to
        bridge both cheeks)."""
        return (_ARM_BORE_R + _NUT_WALL) * self.s

    @property
    def turret_center_z(self) -> float:
        """Anvil turret disk centre — DERIVED so the disk's CROWN sits exactly on
        the cradle seat plane, like every other cradle_form's seat surface
        (Contract 3c: the seat height is one relation, stated once).

        The disk sweeps a full circle about b at every index angle and has no
        through-relief, so its crown is the reaction surface: the chain seats on it
        and `feed_upper` stops the pin just above it (see resolve_config)."""
        return self.cradle_z - self.turret_radius

    @property
    def turret_crown_z(self) -> float:
        """Highest turret material on the driver axis, over the FULL index range."""
        return self.turret_center_z + self.turret_radius

    @property
    def cradle_outboard_x(self) -> float:
        """+x extent of the cradle's raised anvil features at the seat plane — the
        quantity the sliding chain guide must clear across its whole stroke."""
        if self.cradle_form == "stepped_ledge_anvil":
            return max(dx + w / 2.0 for dx, w, _h in _LEDGE_SPECS) * self.s
        if self.cradle_form == "grooved_pad_anvil":
            return (_PAD_DX + _PAD_W / 2.0) * self.s
        # The turret's crown is AT the seat plane; its pocket is the widest thing.
        return self.turret_radius + _TURRET_POCKET_DR * self.s

    @property
    def guide_seat_x(self) -> float:
        """Rail-seat station for the sliding chain guide — DERIVED so the carriage
        clears the REALIZED cradle across its full stroke and still lands on the
        lower arm. `_GUIDE_SEAT_X = 0.0365` was annotated "clear of the anvil", but
        it only was for some cradle_forms: grooved_pad_anvil's outboard pad reaches
        x=0.022, and at the retracted end of the stroke the guide base drove
        straight into it."""
        lo = (
            self.cradle_outboard_x
            + _GUIDE_BASE_LEN * self.s / 2.0
            + self.guide_travel
            + _GUIDE_CRADLE_CLEAR * self.s
        )
        hi = self.lower_arm_x1 - _GUIDE_BASE_LEN * self.s / 2.0 - self.guide_travel
        return min(max(lo, _GUIDE_SEAT_X * self.s), max(hi, lo))

    @property
    def guide_slot_depth_y(self) -> float:
        """Y-extent of the frame's transverse rail slot — the SINGLE statement,
        consumed by `_cut_guide_slot` (the cut) AND `_emit_guide_rail_slot` (the
        mating face). It spans the realized body width, so the slot is real on a
        solid casting and on twin cheek plates alike (their outer faces land at
        +/-body_half_y). A fixed `_GUIDE_BASE_DEPTH * 0.62` left the rail-slot face
        floating in the chain channel between the two plates."""
        return 2.0 * self.body_half_y

    @property
    def toggle_link_len(self) -> float:
        """Toggle link length — stated once (S5 L322-L339); consumed by the link
        geometry AND by the lever pivot height."""
        return max(_TOGGLE_ATTACH * self.s * 0.9, 0.018 * self.s)

    @property
    def lever_pivot_xz(self) -> tuple[float, float]:
        """Toggle lever pivot on the frame — published by EVERY frame_form so
        `compound_toggle` needs no compatibility gate (spec Compatibility Gates 3).

        Height is DERIVED from the link's swept envelope: over lever_pivot
        [0, _LEVER_UPPER] x toggle_joint [_TOGGLE_LOWER, _TOGGLE_UPPER] the link
        hangs lowest at lever=0, toggle=_TOGGLE_LOWER, and it must still clear the
        realized frame top face. A hand-written `upper_z1 + 0.010` sat ~8mm too low
        and swung link_rod straight through the grip at toggle_joint=-0.4."""
        reach = self.toggle_link_len + _LINK_W * self.s * 0.3
        drop = reach * math.sin(-_TOGGLE_LOWER) + (_LINK_W * self.s / 2.0) * math.cos(_TOGGLE_LOWER)
        return (self.upper_arm_x1 * 0.55, self.upper_z1 + drop + _TOGGLE_CLEAR * self.s)


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _aabb_center(aabb):
    """Centre of a world AABB.

    Targeted motion checks must read this, NOT `part_world_position`: that returns
    the part's FRAME origin, which sits on the joint axis and therefore cannot move
    under a revolute pose — every such assertion passes vacuously.
    """
    if aabb is None:
        return None
    return tuple((aabb[0][i] + aabb[1][i]) / 2.0 for i in range(3))


def _pick(value, choices):
    return value if value in choices else choices[0]


def config_from_seed(seed: int) -> ChainSeparatorConfig:
    """Deterministic procedural sampling for EVERY ordinary seed (Contract 4).

    seed=0 is not special. No compatibility gate can reject a draw (the domain
    has zero deny rows — spec section 9), so no retry loop is needed.
    """
    rng = random.Random(seed)
    return ChainSeparatorConfig(
        frame_form=rng.choices(FRAME_FORMS, weights=[5, 4, 4, 3], k=1)[0],
        drive_form=rng.choices(DRIVE_FORMS, weights=[5, 4, 4], k=1)[0],
        cradle_form=rng.choices(CRADLE_FORMS, weights=[5, 4, 4], k=1)[0],
        chain_guide=rng.choices(CHAIN_GUIDES, weights=[5, 3], k=1)[0],
        palette_style=rng.choice(PALETTE_STYLES),
        overall_scale=round(rng.uniform(0.88, 1.14), 4),
        body_thickness_scale=round(rng.uniform(0.88, 1.18), 4),
        throat_depth_scale=round(rng.uniform(0.90, 1.15), 4),
        handle_len_scale=round(rng.uniform(0.90, 1.15), 4),
        feed_travel_scale=round(rng.uniform(0.85, 1.15), 4),
        name=f"seeded_pictureX_0611_Chain_separator_{seed}",
    )


def resolve_config(
    config: ChainSeparatorConfig | None = None,
) -> ResolvedChainSeparatorConfig:
    """The single legalization entry: enum validation, clamping, and every
    `equation` / `inequality` / `conditional` from spec section 7."""
    cfg = config or ChainSeparatorConfig()
    frame_form = _pick(cfg.frame_form, FRAME_FORMS)
    drive_form = _pick(cfg.drive_form, DRIVE_FORMS)
    cradle_form = _pick(cfg.cradle_form, CRADLE_FORMS)
    chain_guide = _pick(cfg.chain_guide, CHAIN_GUIDES)
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)

    overall = _clamp(cfg.overall_scale, 0.88, 1.14)
    thickness = _clamp(cfg.body_thickness_scale, 0.88, 1.18)
    throat = _clamp(cfg.throat_depth_scale, 0.90, 1.15)
    handle = _clamp(cfg.handle_len_scale, 0.90, 1.15)
    feed_s = _clamp(cfg.feed_travel_scale, 0.85, 1.15)

    # equation: body_half_y
    body_half_y = _BODY_HALF_Y * thickness * overall
    # equation: cradle_channel_w — the SINGLE source of truth consumed by the
    # turret thickness and the guide cheek gap (spec section 7 / Contract 3c).
    cradle_channel_w = _CHANNEL_W * thickness * overall
    # inequality: the channel must leave >= 2.5mm of wall on each side to carry
    # the turret pin / anvil pads.
    cradle_channel_w = min(cradle_channel_w, 2.0 * body_half_y - 0.005)
    cradle_channel_w = max(cradle_channel_w, 0.004)

    # equation: turret thickness derives from the channel (dissolves the
    # twin_cheek_plates x rotating_seat_turret gate — spec Compatibility Gates 1).
    turret_thickness = max(cradle_channel_w - 0.0012, 0.0025)
    # inequality: turret fits inside the throat.
    throat_half_x = min(abs(_BACK_X1 * overall * throat), _UPPER_ARM_X1 * overall) * 0.95
    turret_radius = min(_TURRET_R * overall, throat_half_x - 0.0015)
    # inequality: the disk hangs a full diameter below the seat (its crown IS the
    # seat plane), so its pocket must still leave `_TURRET_FLOOR_MIN` of casting
    # under it in the lower arm.
    turret_depth_budget = (_CRADLE_Z - _LOWER_Z0 * overall) - _TURRET_FLOOR_MIN
    turret_radius = min(turret_radius, turret_depth_budget / 2.0 - _TURRET_POCKET_DR * overall)
    turret_radius = max(turret_radius, 0.006)

    # equation: the guide cheeks straddle the same channel.
    guide_cheek_gap = cradle_channel_w
    # equation: guide slot length (fixes S7's slot < travel defect).
    guide_travel = _GUIDE_TRAVEL * overall
    guide_slot_len = _GUIDE_BASE_LEN * overall + 2.0 * guide_travel + _GUIDE_SLOT_MARGIN * overall
    # inequality: the tongue never leaves its slot.
    max_travel = (guide_slot_len - _GUIDE_TONGUE_LEN * overall) / 2.0 - 0.0005
    guide_travel = min(guide_travel, max(max_travel, 0.001))

    # equation + conditional: feed travel. Every bound below is a RELATION between
    # the driver's pin profile and the cradle it drives into (Contract 3e).
    feed_lower = _FEED_LOWER * overall
    feed_upper = _FEED_UPPER * feed_s * overall
    if drive_form == "compound_toggle":
        feed_upper = min(feed_upper, _FEED_UPPER_TOGGLE * overall)

    # inequality: ONLY the cone pin may enter the frame's pin-relief bore. The
    # guide neck behind it (r=_C_NECK_R) is wider than the bore (_PIN_RELIEF_R), so
    # the neck must stop above the relief mouth. The neck's lower face sits at
    # t=_C_CONE_T, i.e. (_TIP_REST_CLEAR + _C_TIP_T - _C_CONE_T) above the datum.
    neck_rest_z = (_TIP_REST_CLEAR + _C_TIP_T - _C_CONE_T) * overall
    relief_mouth_z = _RELIEF_MOUTH_UP * overall
    feed_upper = min(feed_upper, neck_rest_z - relief_mouth_z - _PIN_STOP_CLEAR * overall)

    # conditional: a rotating turret anvil sweeps SOLID through the throat at every
    # index angle and has no through-relief, so it — not the frame's relief bore —
    # is the reaction surface. The pin stops just above the anvil crown, exactly as
    # a real chain tool's pin stops on the anvil face once the rivet is pressed out
    # into the seat notch. The turret's crown is derived onto the seat datum
    # (turret_center_z), so this bound is `_TIP_REST_CLEAR - _TURRET_TIP_CLEAR`.
    if cradle_form == "rotating_seat_turret":
        turret_crown_z = _CRADLE_Z  # == turret_center_z + turret_radius, by construction
        feed_upper = min(
            feed_upper,
            _TIP_REST_CLEAR * overall - turret_crown_z - _TURRET_TIP_CLEAR * overall,
        )

    # inequality: the thread band must still be inside the nut boss at full feed
    # (the boss's underside is the arm underside == _THROAT_Z1).
    band_bottom_rest_z = (_TIP_REST_CLEAR + _C_TIP_T - _C_THREAD_T - _C_CREST_BAND_L) * overall
    feed_upper = min(feed_upper, band_bottom_rest_z - _THROAT_Z1 * overall)

    t_bar_travel = _BAR_TRAVEL * handle * overall

    return ResolvedChainSeparatorConfig(
        frame_form=frame_form,
        drive_form=drive_form,
        cradle_form=cradle_form,
        chain_guide=chain_guide,
        palette_style=palette_style,
        overall_scale=overall,
        body_thickness_scale=thickness,
        throat_depth_scale=throat,
        handle_len_scale=handle,
        feed_travel_scale=feed_s,
        body_half_y=body_half_y,
        cradle_channel_w=cradle_channel_w,
        turret_thickness=turret_thickness,
        turret_radius=turret_radius,
        guide_cheek_gap=guide_cheek_gap,
        guide_travel=guide_travel,
        guide_slot_len=guide_slot_len,
        feed_lower=feed_lower,
        feed_upper=feed_upper,
        t_bar_travel=t_bar_travel,
        name=cfg.name or "pictureX_0611_Chain_separator",
    )


def with_overrides(config: ChainSeparatorConfig, **kwargs: object) -> ChainSeparatorConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: ChainSeparatorConfig | ResolvedChainSeparatorConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedChainSeparatorConfig) else resolve_config(config)
    return (
        ("frame_form", r.frame_form),
        ("drive_form", r.drive_form),
        ("cradle_form", r.cradle_form),
        ("chain_guide", r.chain_guide),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Shared cadquery helpers (spec section 13).
# ---------------------------------------------------------------------------
def _fuse_all(shapes: list[cq.Shape]) -> cq.Shape:
    """S1 L58-L62 / S2 L71-L75 — verbatim."""
    result = shapes[0]
    for shape in shapes[1:]:
        result = result.fuse(shape)
    return result


def _along_a(t: float, base_z: float = 0.0) -> cq.Vector:
    """Point at distance `t` along the working axis a=(0,0,-1) from `base_z`.

    Canonical restatement of S1 L46-L55 `_point_along(SPINDLE_AXIS, t, start)`.
    Drive geometry is authored in the JOINT-LOCAL frame (from local 0 along a) —
    NOT in world coordinates. This is the fix for S2's double-offset defect
    (spec Reject case 3), where world-space starts plus a joint origin at
    SPINDLE_REAR floated the carriage ~0.15m off the frame.
    """
    return cq.Vector(0.0, 0.0, base_z - t)


def _c_body_profile(r: ResolvedChainSeparatorConfig) -> list[tuple[float, float]]:
    """The canonical C-body outline in the working plane (u=x, v=z).

    Adapted from S1 L82-L95 (cast head polygon) re-based into the canonical frame
    (module docstring): the throat notch C-D-E-F opens toward +X, the driver axis
    is u=0, and the cradle datum is v=0.
    """
    return [
        (r.back_x0, r.lower_z0),  # A rear bottom
        (r.lower_arm_x1, r.lower_z0),  # B lower arm front bottom
        (r.lower_arm_x1, r.cradle_z),  # C lower arm front top
        (r.back_x1, r.cradle_z),  # D throat floor, back  <- throat notch
        (r.back_x1, r.throat_z1),  # E throat ceiling, back
        (r.upper_arm_x1, r.throat_z1),  # F upper arm front bottom
    ]


def _silhouette_shape(r: ResolvedChainSeparatorConfig, half_y: float) -> cq.Workplane:
    """S1's sculpted planar silhouette: C-body polygon + integral grip with a
    rounded product end (2x threePointArc) + oval hanging hole.

    Source: S1 L65-L102 (`_frame_shape` handle L68-L79, head L82-L95, hanging
    hole L99-L102) + L149-L157 (stiffener rib). Shared by
    compact_cast_handheld / flanged_bench_pedestal / twin_cheek_plates.
    Built on the "XZ" workplane: local (u,v) -> world (u, 0, v), extruded +/-Y.
    """
    prof = _c_body_profile(r)
    gx1 = r.grip_x1
    grip_lo = r.throat_z1 - 0.004 * r.s  # grip underside, slightly below the arm face
    grip_hi = r.upper_z1 - 0.002 * r.s
    arc_mid_x = gx1 + 0.008 * r.s
    arc_mid_z = (grip_lo + grip_hi) / 2.0

    wp = cq.Workplane("XZ").moveTo(prof[0][0], prof[0][1])
    for pt in prof[1:]:
        wp = wp.lineTo(pt[0], pt[1])
    # Integral grip: underside out to the rounded end (S1 L69-L74).
    wp = (
        wp.lineTo(r.upper_arm_x1 + 0.018 * r.s, grip_lo)
        .lineTo(gx1 - 0.014 * r.s, grip_lo)
        .threePointArc((arc_mid_x, arc_mid_z), (gx1 - 0.014 * r.s, grip_hi))
        .threePointArc(
            ((gx1 + r.upper_arm_x1) / 2.0, grip_hi + 0.004 * r.s),
            (r.upper_arm_x1 + 0.018 * r.s, r.upper_z1),
        )
        .lineTo(r.back_x0, r.upper_z1)
        .close()
    )
    body = wp.extrude(half_y, both=True)

    # (4) Oval hanging hole at the far end of the integral grip (S1 L99-L102).
    # Host-conformal: its station rides the REALIZED grip length (Rule 4).
    hole = (
        cq.Workplane("XZ")
        .center(gx1 - 0.020 * r.s, (grip_lo + grip_hi) / 2.0)
        .ellipse(0.0080 * r.s, 0.0048 * r.s)
        .extrude(half_y * 3.0, both=True)
    )
    body = body.cut(hole)
    return body


def _v_notch_solid(
    radius: float,
    angle: float,
    width: float,
    depth: float,
    thickness: float,
    *,
    overcut: float = 0.002,
) -> cq.Workplane:
    """Triangular-prism solid for cutting V-notch pockets or building seat inserts.

    S6 L82-L109 verbatim in shape, re-based to the canonical frame: the turret
    disk lies in the XZ plane and indexes about b=(0,1,0), so the notch is built
    on "XZ" and extruded along Y. Shared by the pockets AND the inserts (one
    helper, per the spec's compile budget).

    `overcut` pushes the prism's outer edge past the disk rim. It is a CUTTING
    allowance (S6 L96 hard-codes 0.002 for both uses): the pocket wants it so the
    cut breaks cleanly through the rim, the press-fit insert must NOT have it or
    the hardened seat stands proud of the anvil crown the chain rests on — and, on
    the canonical centreline, proud of the driver pin's rest height.
    """
    cos_a, sin_a = math.cos(angle), math.sin(angle)
    px, py = -sin_a, cos_a
    outer_cx = (radius + overcut) * cos_a
    outer_cy = (radius + overcut) * sin_a
    inner_x = (radius - depth) * cos_a
    inner_y = (radius - depth) * sin_a
    return (
        cq.Workplane("XZ")
        .moveTo(outer_cx - (width / 2.0) * px, outer_cy - (width / 2.0) * py)
        .lineTo(outer_cx + (width / 2.0) * px, outer_cy + (width / 2.0) * py)
        .lineTo(inner_x, inner_y)
        .close()
        .extrude(thickness / 2.0 + 0.0005, both=True)
    )


def _cut_working_bores(
    body: cq.Workplane,
    r: ResolvedChainSeparatorConfig,
    half_y: float,
    *,
    relief: bool = True,
) -> cq.Workplane:
    """Drill the coaxial driver passage through the upper arm and the pin relief
    bore below the seat. S1 L138-L145 (real clearance bore, so the carriage runs
    inside a hole instead of occupying the casting's solid volume).

    `relief=False` for twin_cheek_plates: there the CHANNEL between the two plates
    already is the pin relief (S3 L47 PLATE_GAP == the chain channel), and drilling
    a relief bore through a ~3mm cheek plate — thinner than the bore itself —
    severs the plate's lower arm from its back column instead of making a hole.
    """
    bore = cq.Solid.makeCylinder(
        _ARM_BORE_R * r.s,
        (r.upper_z1 - r.throat_z1) + 0.020 * r.s,
        cq.Vector(0.0, 0.0, r.throat_z1 - 0.006 * r.s),
        cq.Vector(0.0, 0.0, 1.0),
    )
    body = body.cut(cq.Workplane(obj=bore))
    if relief:
        # The pin-relief bore: a real through-hole under the seat so the pushed-out
        # chain pin (and the cone tip behind it) has somewhere to go. Its mouth
        # height is single-sourced on `relief_mouth_z`, which also bounds feed_upper.
        relief_bottom = r.lower_z0 - 0.002 * r.s
        relief_bore = cq.Solid.makeCylinder(
            _PIN_RELIEF_R * r.s,
            r.relief_mouth_z - relief_bottom,
            cq.Vector(0.0, 0.0, relief_bottom),
            cq.Vector(0.0, 0.0, 1.0),
        )
        body = body.cut(cq.Workplane(obj=relief_bore))
    return body


def _cut_guide_slot(body: cq.Workplane, r: ResolvedChainSeparatorConfig) -> cq.Workplane:
    """Transverse rail slot in the lower arm top (S7 L121-L130). Length derived
    (spec section 7) so the tongue stays captured across the full stroke."""
    slot = (
        cq.Workplane("XY")
        .box(
            r.guide_slot_len,
            r.guide_slot_depth_y,
            _GUIDE_TONGUE_H * r.s + 0.001,
            centered=(True, True, True),
        )
        .translate((r.guide_seat_x, 0.0, r.cradle_z - _GUIDE_TONGUE_H * r.s / 2.0 + 0.0005))
    )
    return body.cut(slot)


def _cut_turret_pocket(body: cq.Workplane, r: ResolvedChainSeparatorConfig) -> cq.Workplane:
    """Machined pocket the turret disk indexes inside (S6 L159-L197). The pocket
    is only `cradle_channel_w` wide, so `2*body_half_y - channel` of wall remains
    on each side to carry the pivot pin — this is what lets the SAME turret work
    on a solid casting and between twin cheek plates."""
    pocket = cq.Solid.makeCylinder(
        r.turret_radius + _TURRET_POCKET_DR * r.s,
        r.cradle_channel_w,
        cq.Vector(0.0, -r.cradle_channel_w / 2.0, r.turret_center_z),
        cq.Vector(0.0, 1.0, 0.0),
    )
    return body.cut(cq.Workplane(obj=pocket))


# ---------------------------------------------------------------------------
# Slot A — frame_form. Every candidate publishes the SAME anchor contract
# (spec section 13), which is what makes the compatibility matrix empty.
# ---------------------------------------------------------------------------
def _emit_frame_compact(frame, r: ResolvedChainSeparatorConfig, mats) -> None:
    """(3) Planar Boundary Form — S1 L65-L158. One continuous sculpted casting."""
    body = _silhouette_shape(r, r.body_half_y)
    body = _apply_cradle_cuts(body, r)
    body = _cut_working_bores(body, r, r.body_half_y)
    if r.chain_guide == "sliding_cheek_guide":
        body = _cut_guide_slot(body, r)
    if r.cradle_form == "rotating_seat_turret":
        body = _cut_turret_pocket(body, r)
    frame.visual(
        mesh_from_cadquery(body, "chain_breaker_frame", tolerance=0.0006),
        material=mats["body"],
        name="frame_casting", material_class_id=("metal.paint_coated" if r.palette_style in {"black_blue_enamel", "blue_enamel_bench", "forged_steel_natural", "zinc_hardware"} else "metal.blackened_gunmetal"),
    )
    # (4) Stiffener wedge at the head/grip transition (S1 L149-L157). Host-
    # conformal: it rides the realized arm face.
    frame.visual(
        Box((0.022 * r.s, r.body_half_y * 1.4, 0.006 * r.s)),
        origin=Origin(xyz=(r.upper_arm_x1 * 0.9, 0.0, r.upper_z1 - 0.003 * r.s)),
        material=mats["accent"],
        name="stiffener_rib", material_class_id=("metal.paint_coated" if r.palette_style in {"black_blue_enamel", "blue_enamel_bench", "zinc_hardware", "black_rubber_shop"} else "metal.steel_bare"),
    )


def _emit_frame_flanged(frame, r: ResolvedChainSeparatorConfig, mats) -> None:
    """(3) Planar Boundary Form + grounded pedestal — S8 L159-L216."""
    body = _silhouette_shape(r, r.body_half_y)
    # Bench-mounting flange fused below the head (S8 L163-L176).
    flange = (
        cq.Workplane("XZ")
        .moveTo(_FLANGE_X0 * r.s, _FLANGE_Z1 * r.s)
        .lineTo(_FLANGE_X1 * r.s, _FLANGE_Z1 * r.s)
        .lineTo(_FLANGE_X1 * r.s, _FLANGE_Z0 * r.s)
        .lineTo(_FLANGE_X0 * r.s, _FLANGE_Z0 * r.s)
        .close()
        .extrude(r.body_half_y, both=True)
    )
    body = body.union(flange)
    # (4) Four bolt holes through the flange (S8 L178-L194) — host-conformal:
    # the ring positions derive from the REALIZED flange corners (Rule 4).
    fz_lo, fz_hi = _FLANGE_Z0 * r.s, _FLANGE_Z1 * r.s
    fx_lo, fx_hi = _FLANGE_X0 * r.s, _FLANGE_X1 * r.s
    for bx in (fx_lo + 0.014 * r.s, fx_hi - 0.014 * r.s):
        for bz in (fz_lo + 0.012 * r.s, fz_hi - 0.012 * r.s):
            hole = cq.Solid.makeCylinder(
                _BOLT_R * r.s,
                r.body_half_y * 4.0,
                cq.Vector(bx, -r.body_half_y * 2.0, bz),
                cq.Vector(0.0, 1.0, 0.0),
            )
            body = body.cut(cq.Workplane(obj=hole))
    # (4) Two cast gussets tying the head walls into the flange (S8 L196-L215).
    for gx, sign in ((_FLANGE_X0 * r.s, 1.0), (_FLANGE_X1 * r.s, -1.0)):
        gusset = (
            cq.Workplane("XZ")
            .moveTo(gx, fz_hi)
            .lineTo(gx + sign * 0.016 * r.s, fz_hi)
            .lineTo(gx, fz_hi + 0.014 * r.s)
            .close()
            .extrude(r.body_half_y, both=True)
        )
        body = body.union(gusset)
    body = _apply_cradle_cuts(body, r)
    body = _cut_working_bores(body, r, r.body_half_y)
    if r.chain_guide == "sliding_cheek_guide":
        body = _cut_guide_slot(body, r)
    if r.cradle_form == "rotating_seat_turret":
        body = _cut_turret_pocket(body, r)
    frame.visual(
        mesh_from_cadquery(body, "flanged_frame", tolerance=0.0006),
        material=mats["body"],
        name="frame_casting", material_class_id=("metal.paint_coated" if r.palette_style in {"black_blue_enamel", "blue_enamel_bench", "forged_steel_natural", "zinc_hardware"} else "metal.blackened_gunmetal"),
    )
    frame.visual(
        Box((0.022 * r.s, r.body_half_y * 1.4, 0.006 * r.s)),
        origin=Origin(xyz=(r.upper_arm_x1 * 0.9, 0.0, r.upper_z1 - 0.003 * r.s)),
        material=mats["accent"],
        name="stiffener_rib", material_class_id=("metal.paint_coated" if r.palette_style in {"black_blue_enamel", "blue_enamel_bench", "zinc_hardware", "black_rubber_shop"} else "metal.steel_bare"),
    )


def _emit_frame_bench_c(frame, r: ResolvedChainSeparatorConfig, mats) -> None:
    """(3) Volumetric Envelope Form — S2 L78-L221. Boxed column + arms + foot."""
    hy = r.body_half_y
    col_x0, col_x1 = r.back_x0, r.back_x1
    parts: list[cq.Shape] = []
    # Back column (S2 L81-L86).
    parts.append(
        cq.Solid.makeBox(
            col_x1 - col_x0,
            hy * 2.0,
            r.upper_z1 - r.lower_z0,
            pnt=cq.Vector(col_x0, -hy, r.lower_z0),
        )
    )
    # Upper arm (S2 L89-L95).
    parts.append(
        cq.Solid.makeBox(
            r.upper_arm_x1 - col_x1,
            hy * 2.0,
            r.upper_z1 - r.throat_z1,
            pnt=cq.Vector(col_x1, -hy, r.throat_z1),
        )
    )
    # Lower arm (S2 L98-L104).
    parts.append(
        cq.Solid.makeBox(
            r.lower_arm_x1 - col_x1,
            hy * 2.0,
            r.cradle_z - r.lower_z0,
            pnt=cq.Vector(col_x1, -hy, r.lower_z0),
        )
    )
    # Flat bolting foot (S2 L107-L112) — wider in Y than the body.
    foot_hy = min(_FOOT_HALF_Y * r.s, hy * 3.2)
    parts.append(
        cq.Solid.makeBox(
            (_FOOT_X1 - _FOOT_X0) * r.s,
            foot_hy * 2.0,
            (_FOOT_Z1 - _FOOT_Z0) * r.s,
            pnt=cq.Vector(_FOOT_X0 * r.s, -foot_hy, _FOOT_Z0 * r.s),
        )
    )
    body = cq.Workplane(obj=_fuse_all(parts))
    # Gussets at the arm/column junctions (S2 L117-L135).
    for z_ref, sign in ((r.throat_z1, -1.0), (r.cradle_z, 1.0)):
        gusset = (
            cq.Workplane("XZ")
            .moveTo(col_x1, z_ref)
            .lineTo(col_x1 + 0.020 * r.s, z_ref)
            .lineTo(col_x1, z_ref + sign * 0.020 * r.s)
            .close()
            .extrude(hy, both=True)
        )
        body = body.union(gusset)
    # (4) Four bolt holes through the foot (S2 L138-L151) — host-conformal.
    for bx in (_FOOT_X0 * r.s + 0.012 * r.s, _FOOT_X1 * r.s - 0.012 * r.s):
        for by in (-foot_hy + 0.010 * r.s, foot_hy - 0.010 * r.s):
            hole = cq.Solid.makeCylinder(
                _BOLT_R * r.s,
                (_FOOT_Z1 - _FOOT_Z0) * r.s + 0.006 * r.s,
                cq.Vector(bx, by, _FOOT_Z0 * r.s - 0.003 * r.s),
                cq.Vector(0.0, 0.0, 1.0),
            )
            body = body.cut(cq.Workplane(obj=hole))
    body = _apply_cradle_cuts(body, r)
    body = _cut_working_bores(body, r, hy)
    if r.chain_guide == "sliding_cheek_guide":
        body = _cut_guide_slot(body, r)
    if r.cradle_form == "rotating_seat_turret":
        body = _cut_turret_pocket(body, r)
    frame.visual(
        mesh_from_cadquery(body, "cframe_body", tolerance=0.0006),
        material=mats["body"],
        name="frame_casting", material_class_id=("metal.paint_coated" if r.palette_style in {"black_blue_enamel", "blue_enamel_bench", "forged_steel_natural", "zinc_hardware"} else "metal.blackened_gunmetal"),
    )
    # (4) Three cast ribs on the back column (S2 L212-L219) — host-conformal:
    # each rib's z station is a fraction of the REALIZED column height.
    for i in range(3):
        rib_z = r.lower_z0 + (r.upper_z1 - r.lower_z0) * (0.30 + 0.20 * i)
        frame.visual(
            Box((0.004 * r.s, hy * 2.0 + 0.003 * r.s, 0.006 * r.s)),
            origin=Origin(xyz=((col_x0 + col_x1) / 2.0, 0.0, rib_z)),
            material=mats["accent"],
            name=f"cast_rib_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"black_blue_enamel", "blue_enamel_bench", "zinc_hardware", "black_rubber_shop"} else "metal.steel_bare"),
        )


def _emit_frame_twin_plates(frame, r: ResolvedChainSeparatorConfig, mats) -> None:
    """(3) Macro Surface Construction — S3 L45-L212, L331-L347.

    The solid casting becomes TWO thin cheek plates + a discrete spacer set
    bridging the chain channel. All plates and spacers are `frame` visuals
    (Rule 1: they do not articulate) — S3 does exactly this.
    """
    plate_th = _PLATE_TH * r.s * r.body_thickness_scale
    gap = r.cradle_channel_w
    # Plate centers straddle the channel; outer face lands at +/- body_half_y.
    y_centers = (-(gap / 2.0 + plate_th / 2.0), +(gap / 2.0 + plate_th / 2.0))
    for i, yc in enumerate(y_centers):
        plate = _silhouette_shape(r, plate_th / 2.0)
        plate = _apply_cradle_cuts(plate, r)
        # relief=False: the channel between the plates IS the pin relief here.
        plate = _cut_working_bores(plate, r, plate_th / 2.0, relief=False)
        if r.chain_guide == "sliding_cheek_guide":
            plate = _cut_guide_slot(plate, r)
        plate = plate.translate((0.0, yc, 0.0))
        frame.visual(
            mesh_from_cadquery(plate, f"cheek_plate_{i}", tolerance=0.0006),
            material=mats["body"],
            name=f"cheek_plate_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"black_blue_enamel", "blue_enamel_bench", "forged_steel_natural", "zinc_hardware"} else "metal.blackened_gunmetal"),
        )
    # Bridge spacers (S3 L154-L212). Each spans the gap and embeds slightly into
    # both plates, so the frame part has NO disconnected geometry islands.
    span = gap + plate_th
    # Transition rib at the head/grip junction (S3 L163-L169).
    frame.visual(
        Box((0.020 * r.s, span, 0.008 * r.s)),
        origin=Origin(xyz=(r.upper_arm_x1 * 0.9, 0.0, r.upper_z1 - 0.005 * r.s)),
        material=mats["hardware"],
        name="spacer_transition", material_class_id=("metal.stainless_matte" if r.palette_style in {"black_blue_enamel", "blue_enamel_bench", "forged_steel_natural", "zinc_hardware"} else "metal.blackened_gunmetal"),
    )
    # Two cylindrical bridge pins along the grip (S3 L173-L179).
    for i, fx in enumerate((0.45, 0.80)):
        px = r.upper_arm_x1 + (r.grip_x1 - r.upper_arm_x1) * fx
        frame.visual(
            Cylinder(radius=0.004 * r.s, length=span),
            origin=Origin(
                xyz=(px, 0.0, (r.throat_z1 + r.upper_z1) / 2.0),
                rpy=(math.pi / 2.0, 0.0, 0.0),
            ),
            material=mats["hardware"],
            name=f"spacer_pin_{i}", material_class_id=("metal.stainless_matte" if r.palette_style in {"black_blue_enamel", "blue_enamel_bench", "forged_steel_natural", "zinc_hardware"} else "metal.blackened_gunmetal"),
        )
    # Rear bridge tying the two plates behind the throat.
    frame.visual(
        Box((abs(r.back_x1 - r.back_x0) * 0.8, span, 0.012 * r.s)),
        origin=Origin(xyz=((r.back_x0 + r.back_x1) / 2.0, 0.0, (r.lower_z0 + r.upper_z1) / 2.0)),
        material=mats["hardware"],
        name="spacer_rear_bridge", material_class_id=("metal.stainless_matte" if r.palette_style in {"black_blue_enamel", "blue_enamel_bench", "forged_steel_natural", "zinc_hardware"} else "metal.blackened_gunmetal"),
    )
    # Anvil bridge blocks in the cradle area (S3 L197-L210) — they also give the
    # lower arm its cross-tie.
    for i, bx in enumerate((-0.016, 0.020)):
        frame.visual(
            Box((0.012 * r.s, span, 0.010 * r.s)),
            origin=Origin(xyz=(bx * r.s, 0.0, r.lower_z0 + 0.008 * r.s)),
            material=mats["hardware"],
            name=f"spacer_anvil_{i}", material_class_id=("metal.stainless_matte" if r.palette_style in {"black_blue_enamel", "blue_enamel_bench", "forged_steel_natural", "zinc_hardware"} else "metal.blackened_gunmetal"),
        )


def _emit_nut_boss(frame, r: ResolvedChainSeparatorConfig, mats) -> None:
    """The tapped nut boss — a SEPARATE named visual (not fused into the casting)
    so the thread-flank contact is genuinely element-scoped (Rule 7).

    Source: S1 L126-L133 (the short sleeve physically fused into the cast head),
    re-stationed along a so the carriage's thread crests engage its bore.
    Its bore (`_NUT_BORE_R`) is UNDER the crest radius: that interference is what
    makes `driver_carriage` genuinely touch the frame, replacing the source
    records' forbidden `allow_isolated_part` (spec Reject cases 1-2).

    Span is DERIVED (`nut_boss_z0/z1`): fused through the realized upper arm and
    tall enough to still hold the thread band at full retract.
    """
    z0 = r.nut_boss_z0
    z1 = r.nut_boss_z1
    outer_r = r.nut_boss_outer_r
    boss = cq.Workplane(
        obj=cq.Solid.makeCylinder(outer_r, z1 - z0, cq.Vector(0.0, 0.0, z0), cq.Vector(0, 0, 1))
    )
    bore = cq.Workplane(
        obj=cq.Solid.makeCylinder(
            _NUT_BORE_R * r.s,
            (z1 - z0) + 0.006 * r.s,
            cq.Vector(0.0, 0.0, z0 - 0.003 * r.s),
            cq.Vector(0, 0, 1),
        )
    )
    frame.visual(
        mesh_from_cadquery(boss.cut(bore), "spindle_nut_boss", tolerance=0.0004),
        material=mats["hardware"],
        name="spindle_nut_boss", material_class_id=("metal.stainless_matte" if r.palette_style in {"black_blue_enamel", "blue_enamel_bench", "forged_steel_natural", "zinc_hardware"} else "metal.blackened_gunmetal"),
    )


def _emit_lever_boss(frame, r: ResolvedChainSeparatorConfig, mats) -> None:
    """Toggle lever pivot boss — part of the anchor contract EVERY frame_form
    publishes (spec Compatibility Gates 3), so `compound_toggle` needs no gate."""
    px, pz = r.lever_pivot_xz
    frame.visual(
        Cylinder(radius=_LEVER_PIVOT_R * r.s, length=r.body_half_y * 2.2),
        origin=Origin(xyz=(px, 0.0, pz), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["hardware"],
        name="lever_pivot_boss", material_class_id=("metal.stainless_matte" if r.palette_style in {"black_blue_enamel", "blue_enamel_bench", "forged_steel_natural", "zinc_hardware"} else "metal.blackened_gunmetal"),
    )
    # Yoke tying the pin down onto the realized arm top (no floating island). It is
    # TWO cheeks straddling the lever's swing plane, not one full-width column: the
    # lever's hub is a rounded tail of radius _LEVER_W/2 swept about the pivot —
    # wider than the pin it captures — so a column spanning the lever's own plane
    # stands permanently inside that swept circle and the lever grinds through its
    # own pedestal. The pin passes through both cheeks and carries the lever
    # between them, which is what a real lever pedestal is.
    cheek_th = _LEVER_YOKE_TH * r.s
    cheek_off = _LEVER_TH * r.s / 2.0 + _LEVER_YOKE_CLEAR * r.s + cheek_th / 2.0
    for i, sign in enumerate((-1.0, 1.0)):
        frame.visual(
            Box((_LEVER_PIVOT_R * 2.0 * r.s, cheek_th, abs(pz - r.upper_z1) + 0.002 * r.s)),
            origin=Origin(xyz=(px, sign * cheek_off, (pz + r.upper_z1) / 2.0)),
            material=mats["hardware"],
            name=f"lever_boss_riser_{i}", material_class_id=("metal.stainless_matte" if r.palette_style in {"black_blue_enamel", "blue_enamel_bench", "forged_steel_natural", "zinc_hardware"} else "metal.blackened_gunmetal"),
        )


def _emit_turret_pin(frame, r: ResolvedChainSeparatorConfig, mats) -> None:
    """Frame pivot pin the anvil turret indexes on (S6 L159-L197).

    Spans the FULL body width, so both pocket walls (or both cheek plates) carry
    it. Its radius is 0.3mm OVER the turret bore -> real capture contact.
    """
    frame.visual(
        Cylinder(radius=_TURRET_PIN_R * r.s, length=r.body_half_y * 2.0),
        origin=Origin(xyz=(0.0, 0.0, r.turret_center_z), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["hardware"],
        name="turret_pivot_pin", material_class_id=("metal.stainless_matte" if r.palette_style in {"black_blue_enamel", "blue_enamel_bench", "forged_steel_natural", "zinc_hardware"} else "metal.blackened_gunmetal"),
    )


def _emit_guide_rail_slot(frame, r: ResolvedChainSeparatorConfig, mats) -> None:
    """The rail-slot ceiling the guide tongue mates against.

    This is the ONE interface in the template that is two axis-aligned faces in
    contact, so `guide_slide` declares a real MatingContract against this visual
    (Rule 2). Source: S7 L121-L130 (frame transverse rail slot).
    """
    frame.visual(
        Box(
            (
                r.guide_slot_len,
                r.guide_slot_depth_y,
                0.0025 * r.s,
            )
        ),
        origin=Origin(
            xyz=(
                r.guide_seat_x,
                0.0,
                r.cradle_z - _GUIDE_TONGUE_H * r.s - 0.00125 * r.s,
            )
        ),
        material=mats["hardware"],
        name="guide_rail_slot", material_class_id=("metal.stainless_matte" if r.palette_style in {"black_blue_enamel", "blue_enamel_bench", "forged_steel_natural", "zinc_hardware"} else "metal.blackened_gunmetal"),
    )


_FRAME_EMITTERS = {
    "compact_cast_handheld": _emit_frame_compact,
    "bench_c_frame": _emit_frame_bench_c,
    "twin_cheek_plates": _emit_frame_twin_plates,
    "flanged_bench_pedestal": _emit_frame_flanged,
}


# ---------------------------------------------------------------------------
# Slot C — cradle_form. The two static candidates are (3) form variants emitted
# as frame HOST GEOMETRY (Rule 1); only the turret adds a part.
# ---------------------------------------------------------------------------
def _apply_cradle_cuts(body: cq.Workplane, r: ResolvedChainSeparatorConfig) -> cq.Workplane:
    """Cradle geometry cut into / fused onto the frame body before the bores.

    stepped_ledge_anvil : S1 L112-L123 — two stepped ledges flanking the axis.
    grooved_pad_anvil   : S2 L172-L209 — a seating groove + rounded root + pads.
    rotating_seat_turret: the seat is the turret; the frame only gets the pocket.
    """
    if r.cradle_form == "stepped_ledge_anvil":
        # (3) Planar Boundary: asymmetric stepped ledges (S1 L112-L123 sizes).
        for dx, w, h in _LEDGE_SPECS:
            pad = (
                cq.Workplane("XY")
                .box(w * r.s, r.cradle_channel_w * 1.9, h * r.s, centered=(True, True, True))
                .translate((dx * r.s, 0.0, r.cradle_z + h * r.s / 2.0))
            )
            body = body.union(pad)
    elif r.cradle_form == "grooved_pad_anvil":
        # (3) Macro Surface: a seating groove milled into the throat floor with a
        # cylindrical rounded root (S2 L180-L194), flanked by two raised pads
        # spanning the full body width (S2 L197-L209).
        groove_d = 0.008 * r.s
        groove = (
            cq.Workplane("XY")
            .box(
                0.028 * r.s,
                r.cradle_channel_w,
                groove_d + 0.002 * r.s,
                centered=(True, True, True),
            )
            .translate((0.0, 0.0, r.cradle_z - groove_d / 2.0 + 0.001 * r.s))
        )
        body = body.cut(groove)
        root = cq.Solid.makeCylinder(
            r.cradle_channel_w / 2.0,
            0.028 * r.s,
            cq.Vector(-0.014 * r.s, 0.0, r.cradle_z - groove_d),
            cq.Vector(1.0, 0.0, 0.0),
        )
        body = body.cut(cq.Workplane(obj=root))
        for dx in (-_PAD_DX, _PAD_DX):
            pad = (
                cq.Workplane("XY")
                .box(
                    _PAD_W * r.s,
                    r.cradle_channel_w * 2.6,
                    _PAD_H * r.s,
                    centered=(True, True, True),
                )
                .translate((dx * r.s, 0.0, r.cradle_z + _PAD_H * r.s / 2.0))
            )
            body = body.union(pad)
    return body


def _emit_anvil_turret(model, frame, r: ResolvedChainSeparatorConfig, mats):
    """(1)+(2) rotating three-seat anvil turret — S6 L235-L281, L453-L478, L523-L541.

    A real indexing body (bored disk + 3 press-fit V-seat inserts), not a marker.
    Thickness DERIVES from `cradle_channel_w` (never restated — Contract 3c), so
    the same turret fits a solid casting and the twin-plate channel alike.
    """
    turret = model.part(
        "anvil_turret",
        meta={"role": "indexed three-seat anvil turret", "seat_count": 3},
    )
    th = r.turret_thickness
    disk = cq.Workplane("XZ").circle(r.turret_radius).extrude(th / 2.0, both=True)
    bore = cq.Workplane("XZ").circle(_TURRET_BORE_R * r.s).extrude(th, both=True)
    disk = disk.cut(bore)
    for angle, width, depth in _TURRET_NOTCH_SPECS:
        disk = disk.cut(
            _v_notch_solid(r.turret_radius, angle, width * r.s * 1.04, depth * r.s * 1.04, th)
        )
    turret.visual(
        mesh_from_cadquery(disk, "turret_disk", tolerance=0.0004),
        material=mats["accent"],
        name="turret_disk", material_class_id=("metal.paint_coated" if r.palette_style in {"black_blue_enamel", "blue_enamel_bench", "zinc_hardware", "black_rubber_shop"} else "metal.steel_bare"),
    )
    # Three hardened V-seat inserts press-fit into their pockets (S6 L267-L281).
    # Same-part visuals -> the press fit needs no cross-part allowance.
    # overcut=0: the insert finishes FLUSH with the disk rim, so the anvil crown is
    # a single continuous surface at the seat datum.
    for i, (angle, width, depth) in enumerate(_TURRET_NOTCH_SPECS):
        insert = _v_notch_solid(
            r.turret_radius,
            angle,
            width * r.s * 1.06,
            depth * r.s * 1.06,
            th - 0.0006,
            overcut=0.0,
        )
        turret.visual(
            mesh_from_cadquery(insert, f"seat_insert_{i}", tolerance=0.0004),
            material=mats["seat"],
            name=f"seat_insert_{i}", material_class_id=("metal.stainless_matte" if r.palette_style in {"black_blue_enamel", "blue_enamel_bench", "zinc_hardware", "black_rubber_shop"} else "metal.steel_bare"),
        )
    # Captured-pin joint (turret bore around the frame's turret_pivot_pin):
    # NOT two axis-aligned faces -> omits MatingContract per Rule 2 grandfather.
    model.articulation(
        "turret_index",
        ArticulationType.REVOLUTE,
        parent=frame,
        child=turret,
        origin=Origin(xyz=(0.0, 0.0, r.turret_center_z)),
        axis=B_AXIS,
        motion_limits=MotionLimits(effort=12.0, velocity=3.0, lower=0.0, upper=2.0 * math.pi),
        meta={
            "mechanism": "three chain-gauge seats index to the throat",
            "captured": True,
        },
    )
    return turret


# ---------------------------------------------------------------------------
# Slot D — chain_guide.
# ---------------------------------------------------------------------------
def _emit_guide_carriage(model, frame, r: ResolvedChainSeparatorConfig, mats):
    """(1)+(2) sliding chain-width guide — S7 L244-L306, L372-L383, L473-L490.

    A complete moving solid: base plate + rail tongue + two straddling cheeks +
    lock knob (Rule 6). Authored in the joint-local frame; the tongue's top face
    sits AT local z=0 so it mates against the frame's `guide_rail_slot`.
    """
    guide = model.part("guide_carriage", meta={"role": "sliding chain-width guide"})
    base_h = _GUIDE_BASE_H * r.s
    tongue_h = _GUIDE_TONGUE_H * r.s
    # Rail tongue: local origin at its TOP face -> the MatingContract face.
    guide.visual(
        Box((_GUIDE_TONGUE_LEN * r.s, _GUIDE_BASE_DEPTH * r.s * 0.58, tongue_h)),
        origin=Origin(xyz=(0.0, 0.0, -tongue_h / 2.0)),
        material=mats["hardware"],
        name="rail_tongue", material_class_id=("metal.stainless_matte" if r.palette_style in {"black_blue_enamel", "blue_enamel_bench", "forged_steel_natural", "zinc_hardware"} else "metal.blackened_gunmetal"),
    )
    # Base plate resting on the arm top, carrying the cheeks. It seats directly on
    # the tongue's top face (local z=0) — the old `tongue_h/2 + base_h/2` station
    # left the base floating half a tongue-height above the tongue.
    guide.visual(
        Box((_GUIDE_BASE_LEN * r.s, _GUIDE_BASE_DEPTH * r.s, base_h)),
        origin=Origin(xyz=(0.0, 0.0, base_h / 2.0 - 0.0002)),
        material=mats["driver"],
        name="guide_base", material_class_id=("metal.stainless_matte" if r.palette_style in {"black_blue_enamel", "blue_enamel_bench", "zinc_hardware", "black_rubber_shop"} else "metal.steel_bare"),
    )
    # Two cheeks straddling the chain channel — gap DERIVES from the frame's
    # cradle_channel_w (Contract 3c; dissolves the guide x frame gate).
    cheek_off = r.guide_cheek_gap / 2.0 + _GUIDE_CHEEK_TH * r.s / 2.0
    for i, sign in enumerate((-1.0, 1.0)):
        guide.visual(
            Box((_GUIDE_CHEEK_D * r.s, _GUIDE_CHEEK_TH * r.s, _GUIDE_CHEEK_H * r.s)),
            origin=Origin(
                xyz=(
                    0.0,
                    sign * cheek_off,
                    base_h + _GUIDE_CHEEK_H * r.s / 2.0 - 0.0004,
                )
            ),
            material=mats["driver"],
            name=f"guide_cheek_{i}", material_class_id=("metal.stainless_matte" if r.palette_style in {"black_blue_enamel", "blue_enamel_bench", "zinc_hardware", "black_rubber_shop"} else "metal.steel_bare"),
        )
    # (4) Lock knob (S7 L291-L296).
    guide.visual(
        Cylinder(radius=_GUIDE_KNOB_R * r.s, length=_GUIDE_KNOB_L * r.s),
        origin=Origin(
            xyz=(
                _GUIDE_BASE_LEN * r.s / 2.0 - 0.001 * r.s,
                0.0,
                base_h / 2.0,
            ),
            rpy=(0.0, math.pi / 2.0, 0.0),
        ),
        material=mats["accent"],
        name="lock_knob", material_class_id=("metal.paint_coated" if r.palette_style in {"black_blue_enamel", "blue_enamel_bench", "zinc_hardware", "black_rubber_shop"} else "metal.steel_bare"),
    )
    # The ONLY joint with two axis-aligned faces in contact -> REAL MatingContract.
    model.articulation(
        "guide_slide",
        ArticulationType.PRISMATIC,
        parent=frame,
        child=guide,
        # The tongue's local frame puts its TOP face at z=0 and its mating
        # (negative_z) face at z=-tongue_h, so the joint origin must sit at the
        # cradle datum for that face to land on the rail slot's floor. Placing the
        # origin at `cradle_z - tongue_h` dropped the tongue a whole tongue-height
        # below the slot -> `fail_if_joint_mating_has_gap`.
        origin=Origin(xyz=(r.guide_seat_x, 0.0, r.cradle_z)),
        axis=H_AXIS,
        motion_limits=MotionLimits(
            effort=60.0, velocity=0.05, lower=-r.guide_travel, upper=r.guide_travel
        ),
        mating=MatingContract(
            parent_face_geometry="guide_rail_slot",
            parent_face_side="positive_z",
            child_face_geometry="rail_tongue",
            child_face_side="negative_z",
            contact_tol=0.0025,
            tangential_containment=True,
            tangential_tol=0.006,
        ),
        meta={"mechanism": "chain guide traverses across the driver axis", "captured": True},
    )
    return guide


# ---------------------------------------------------------------------------
# Slot B — drive_form. Geometry is authored in the JOINT-LOCAL frame (from local
# 0 along a), never in world coordinates (spec Reject case 3).
# ---------------------------------------------------------------------------
def _rod_ring_stations(r: ResolvedChainSeparatorConfig) -> tuple[float, float]:
    """Stations along `a` for the toggle rod's two guide rings — DERIVED so BOTH
    rings stay inside the nut boss's bore across the whole stroke. That ring<->bore
    engagement is the only thing supporting the rod, so where the rings sit is a
    relation to the boss, not a literal (Contract 3e).
    """
    t_lo = (r.spindle_rear_z - r.nut_boss_z1) / r.s
    t_hi = (r.spindle_rear_z - r.nut_boss_z0) / r.s
    # A ring at station t occupies world z [rear - (t+L)s - d, rear - t*s - d]; it
    # must stay within [nut_boss_z0, nut_boss_z1] for every d in [feed_lower, feed_upper].
    lo = t_lo + max(-r.feed_lower, 0.0) / r.s
    hi = t_hi - _ROD_RING_L - max(r.feed_upper, 0.0) / r.s
    if hi <= lo:  # degenerate window: put both rings at its centre
        mid = (lo + hi) / 2.0
        return (mid, mid)
    return (lo, hi)


def _carriage_shape(r: ResolvedChainSeparatorConfig) -> cq.Workplane:
    """Threaded spindle carriage — S1 L161-L182 verbatim in structure.

    tenon + shaft + thread-crest collar + thrust collar + guide neck + cone pin.
    Shared by `screw_tbar` and `ratchet_socket` (spec compile budget).
    """
    s = r.s
    a = cq.Vector(*A_AXIS)
    pieces: list[cq.Shape] = []
    pieces.append(
        cq.Solid.makeCylinder(_C_TENON_R * s, _C_TENON_L * s, _along_a(_C_TENON_T * s), a)
    )
    pieces.append(
        cq.Solid.makeCylinder(_C_SHAFT_R * s, _C_SHAFT_L * s, _along_a(_C_SHAFT_T * s), a)
    )
    pieces.append(
        cq.Solid.makeCylinder(_C_THREAD_R * s, _C_THREAD_L * s, _along_a(_C_THREAD_T * s), a)
    )
    # Exposed machine-thread crests (S1 L174-L177) — closely spaced connected
    # crests, not a smooth generic cylinder. These are what engage the nut bore.
    for i in range(_C_CREST_N):
        t = (_C_THREAD_T + i * _C_CREST_DT) * s
        pieces.append(cq.Solid.makeCylinder(_C_CREST_R * s, _C_CREST_L * s, _along_a(t), a))
    pieces.append(
        cq.Solid.makeCylinder(_C_THRUST_R * s, _C_THRUST_L * s, _along_a(_C_THRUST_T * s), a)
    )
    pieces.append(cq.Solid.makeCylinder(_C_NECK_R * s, _C_NECK_L * s, _along_a(_C_NECK_T * s), a))
    pieces.append(
        cq.Solid.makeCone(_C_CONE_R0 * s, _C_CONE_R1 * s, _C_CONE_L * s, _along_a(_C_CONE_T * s), a)
    )
    return cq.Workplane(obj=_fuse_all(pieces))


def _driver_rod_shape(r: ResolvedChainSeparatorConfig) -> cq.Workplane:
    """Smooth driver rod with guide rings + toggle pin — S5 L222-L273.

    The toggle variant replaces the screw with a plain rod; the guide rings ride
    the nut bore (that is what keeps the rod supported and in contact).
    """
    s = r.s
    a = cq.Vector(*A_AXIS)
    pieces: list[cq.Shape] = []
    pieces.append(cq.Solid.makeCylinder(_ROD_R * s, _C_SHAFT_L * s, _along_a(_C_SHAFT_T * s), a))
    # Guide rings genuinely interfering with the nut bore -> real support contact.
    # `_ROD_RING_R` derives from `_NUT_BORE_R` and the stations derive from the
    # boss span, so the rings cannot drift out of the bore they ride in.
    for t in _rod_ring_stations(r):
        pieces.append(cq.Solid.makeCylinder(_ROD_RING_R * s, _ROD_RING_L * s, _along_a(t * s), a))
    pieces.append(
        cq.Solid.makeCylinder(_C_THRUST_R * s, _C_THRUST_L * s, _along_a(_C_THRUST_T * s), a)
    )
    pieces.append(cq.Solid.makeCylinder(_C_NECK_R * s, _C_NECK_L * s, _along_a(_C_NECK_T * s), a))
    pieces.append(
        cq.Solid.makeCone(_C_CONE_R0 * s, _C_CONE_R1 * s, _C_CONE_L * s, _along_a(_C_CONE_T * s), a)
    )
    return cq.Workplane(obj=_fuse_all(pieces))


def _emit_driver_carriage(model, frame, r: ResolvedChainSeparatorConfig, mats):
    """`driver_carriage` + the PRISMATIC `driver_feed` joint (all Slot B)."""
    carriage = model.part(
        "driver_carriage",
        meta={"role": "captured translating driver", "aligned_driver": True},
    )
    if r.drive_form == "compound_toggle":
        shape = _driver_rod_shape(r)
        name = "driver_rod"
    else:
        shape = _carriage_shape(r)
        name = "spindle_thread"
    carriage.visual(
        mesh_from_cadquery(shape, "driver_carriage", tolerance=0.0004),
        material=mats["driver"],
        name=name, material_class_id=("metal.stainless_matte" if r.palette_style in {"black_blue_enamel", "blue_enamel_bench", "zinc_hardware", "black_rubber_shop"} else "metal.steel_bare"),
    )
    if r.drive_form == "compound_toggle":
        # Toggle pin pressed through the rod's upper end (S5 L236-L245). Its station
        # is derived onto the rod core (t just past `_C_SHAFT_T`) so it is carried by
        # the rod instead of floating 9mm off it as a per-part geometry island; it
        # still stands proud in +y, which is what makes it readable.
        carriage.visual(
            Cylinder(radius=0.0028 * r.s, length=r.body_half_y * 1.6),
            origin=Origin(
                xyz=(0.0, r.body_half_y * 0.8, -(_C_SHAFT_T + 0.006) * r.s),
                rpy=(math.pi / 2.0, 0.0, 0.0),
            ),
            material=mats["hardware"],
            name="toggle_pin", material_class_id=("metal.stainless_matte" if r.palette_style in {"black_blue_enamel", "blue_enamel_bench", "forged_steel_natural", "zinc_hardware"} else "metal.blackened_gunmetal"),
        )
    # Captured screw feed: the thread crests run inside the frame's tapped nut
    # boss. Rod-in-sleeve geometry (not two axis-aligned faces) -> omits
    # MatingContract per the Rule 2 grandfather; support + contact come from the
    # 0.4mm thread-flank interference declared in run_tests.
    model.articulation(
        "driver_feed",
        ArticulationType.PRISMATIC,
        parent=frame,
        child=carriage,
        origin=Origin(xyz=(0.0, 0.0, r.spindle_rear_z)),
        axis=A_AXIS,
        motion_limits=MotionLimits(
            effort=900.0, velocity=0.025, lower=r.feed_lower, upper=r.feed_upper
        ),
        meta={"mechanism": "captured screw feed toward the cradle", "captured": True},
    )
    return carriage


def _emit_screw_tbar(model, carriage, r: ResolvedChainSeparatorConfig, mats):
    """(2) screw + T-bar: P -> R -> P — S1 L185-L243, L338-L370."""
    s = r.s
    hub = model.part(
        "spindle_hub",
        meta={"role": "drilled spindle head", "axial_bore_radius": _HUB_AXIAL_BORE_R},
    )
    # Hub authored centered on its own joint origin.
    a = cq.Vector(*A_AXIS)
    body = cq.Workplane(
        obj=cq.Solid.makeCylinder(_HUB_R * s, _HUB_L * s, cq.Vector(0.0, 0.0, _HUB_L * s / 2.0), a)
    )
    axial = cq.Workplane(
        obj=cq.Solid.makeCylinder(
            _HUB_AXIAL_BORE_R * s, _HUB_L * s * 2.0, cq.Vector(0.0, 0.0, _HUB_L * s), a
        )
    )
    bar_bore = cq.Workplane(
        obj=cq.Solid.makeCylinder(
            _HUB_BAR_BORE_R * s,
            _HUB_R * s * 4.0,
            cq.Vector(0.0, -_HUB_R * s * 2.0, 0.0),
            cq.Vector(*B_AXIS),
        )
    )
    hub.visual(
        mesh_from_cadquery(body.cut(axial).cut(bar_bore), "spindle_hub", tolerance=0.0004),
        material=mats["accent"],
        name="hub_body", material_class_id=("metal.paint_coated" if r.palette_style in {"black_blue_enamel", "blue_enamel_bench", "zinc_hardware", "black_rubber_shop"} else "metal.steel_bare"),
    )
    # Captured concentric pivot (hub bore around the carriage tenon) -> omits
    # MatingContract per Rule 2 grandfather (pin-through-sleeve).
    model.articulation(
        "spindle_turn",
        ArticulationType.REVOLUTE,
        parent=carriage,
        child=hub,
        origin=Origin(xyz=(0.0, 0.0, -_HUB_CENTER_T * s)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(
            effort=45.0, velocity=5.0, lower=-2.0 * math.pi, upper=2.0 * math.pi
        ),
        meta={
            "mechanism": "T-bar rotates the spindle about the working axis",
            "captured": True,
        },
    )

    t_bar = model.part("t_bar", meta={"role": "sliding T-bar handle", "count": 1})
    half = _BAR_HALF_L * s * r.handle_len_scale
    t_bar.visual(
        Cylinder(radius=_BAR_R * s, length=half * 2.0),
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["accent"],
        name="bar_shaft", material_class_id=("metal.paint_coated" if r.palette_style in {"black_blue_enamel", "blue_enamel_bench", "zinc_hardware", "black_rubber_shop"} else "metal.steel_bare"),
    )
    # Enlarged end stops: larger than the hub bore, so the bar is retained
    # (S1 L240-L242, L456-L463).
    for i, sign in enumerate((-1.0, 1.0)):
        t_bar.visual(
            Cylinder(radius=_BAR_STOP_R * s, length=0.006 * s),
            origin=Origin(xyz=(0.0, sign * half, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["accent"],
            name=f"bar_stop_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"black_blue_enamel", "blue_enamel_bench", "zinc_hardware", "black_rubber_shop"} else "metal.steel_bare"),
        )
    # Captured pin-in-bore -> omits MatingContract per Rule 2 grandfather.
    model.articulation(
        "t_bar_slide",
        ArticulationType.PRISMATIC,
        parent=hub,
        child=t_bar,
        origin=Origin(),
        axis=B_AXIS,
        motion_limits=MotionLimits(
            effort=80.0, velocity=0.15, lower=-r.t_bar_travel, upper=r.t_bar_travel
        ),
        meta={"mechanism": "bar slides through the drilled transverse bore", "captured": True},
    )
    return hub, t_bar


def _ratchet_fold_reach_back(r: ResolvedChainSeparatorConfig) -> float:
    """How far the folding handle sweeps BACK toward the head axis, i.e. how deep
    the fold clevis must be milled into the barrel.

    The bar rotates about the pivot on the rim. A bar point (px, pz) in the fold
    frame lands at world x = pivot_x + px*cos(t) - pz*sin(t) and z = px*sin(t) +
    pz*cos(t); only |z| <= _RH_L/2 can touch the barrel. Both the bar's LENGTH
    (px, via cos<0 past 90deg) and its in-plane HALF-WIDTH (pz, via sin) push it
    inward, and the half-width term dominates — sizing the clevis off the
    centreline alone leaves the bar's corner buried in the barrel.
    """
    s = r.s
    half_w = _HANDLE_W * s / 2.0  # bar half-width in the fold plane
    head_half_h = _RH_L * s / 2.0
    hl = _HANDLE_L * s * r.handle_len_scale
    worst = 0.0
    steps = 32
    for i in range(steps + 1):
        t = _FOLD_UPPER * i / steps
        ct, st = math.cos(t), math.sin(t)
        for pz in (-half_w, half_w):
            # deepest px still inside the barrel's height at this angle
            if abs(st) <= 1e-9:
                px_max = hl
            else:
                px_max = min(hl, max((head_half_h - pz * ct) / st, 0.0))
            for px in (0.0, px_max):
                if abs(px * st + pz * ct) > head_half_h + 1e-9:
                    continue
                worst = max(worst, -(px * ct - pz * st))
    return worst


def _emit_ratchet_socket(model, carriage, r: ResolvedChainSeparatorConfig, mats):
    """(2) ratchet drive: P -> R -> R — S4 L200-L309, L423-L450."""
    s = r.s
    a = cq.Vector(*A_AXIS)
    head = model.part("ratchet_head", meta={"role": "indexed ratchet/socket drive head"})
    pieces: list[cq.Shape] = []
    pieces.append(
        cq.Solid.makeCylinder(_RH_R * s, _RH_L * s, cq.Vector(0.0, 0.0, _RH_L * s / 2.0), a)
    )
    # (4) Knurled grip band. S4 L213-L219 FUSES it into the head solid before any
    # cutting; keeping it a separate `Cylinder` visual (as this template did) both
    # departs from the source construction and puts a ring 1.8mm PROUD of the rim
    # permanently through the handle's fold path, where no cut can reach it.
    # Host-conformal: it rides the realized head radius, stationed on the upper
    # barrel so the band reads as a grip rather than a collar at the pivot.
    pieces.append(
        cq.Solid.makeCylinder(
            (_RH_R + _RH_KNURL_DR) * s,
            _RH_KNURL_L * s,
            cq.Vector(0.0, 0.0, _RH_L * s * 0.28 + _RH_KNURL_L * s / 2.0),
            a,
        )
    )
    result = _fuse_all(pieces)
    axial = cq.Solid.makeCylinder(
        _HUB_AXIAL_BORE_R * s, _RH_L * s * 2.0, cq.Vector(0.0, 0.0, _RH_L * s), a
    )
    result = result.cut(axial)
    # Fold clevis: a real slot milled through the barrel at the pivot so the folding
    # handle has somewhere to GO. Without it the handle's root sweeps back into the
    # solid barrel once the fold passes 90deg (S4 L444 folds to 1.8 rad) — S4 never
    # sees this because it declares a whole-part handle<->head allowance.
    # Depth derives from how far the rotating bar reaches back toward the head axis,
    # but is bounded so the clevis never breaks into the socket bore; whatever fold
    # the bounded clevis cannot clear is solved off by clamp_joint_limits below.
    slot_x0 = max(
        _RH_R * s - _ratchet_fold_reach_back(r) - _RATCHET_FOLD_CLEAR * s,
        (_HUB_AXIAL_BORE_R + _NUT_WALL / 2.0) * s,
    )
    slot_x1 = (_RH_R + _RH_KNURL_DR) * s + 0.002 * s
    slot_hy = _HANDLE_TH * s / 2.0 + _RATCHET_FOLD_CLEAR * s
    clevis = cq.Solid.makeBox(
        slot_x1 - slot_x0,
        slot_hy * 2.0,
        _RH_L * s + 0.002 * s,
        pnt=cq.Vector(slot_x0, -slot_hy, -(_RH_L * s + 0.002 * s) / 2.0),
    )
    result = result.cut(clevis)
    head.visual(
        mesh_from_cadquery(cq.Workplane(obj=result), "ratchet_head", tolerance=0.0004),
        material=mats["driver"],
        name="head_body", material_class_id=("metal.stainless_matte" if r.palette_style in {"black_blue_enamel", "blue_enamel_bench", "zinc_hardware", "black_rubber_shop"} else "metal.steel_bare"),
    )
    # Pivot boss carrying the folding handle (S4 L221-L229).
    # equation: the pivot sits ON the head's rim. S4 L56-L60 puts it at exactly
    # `HANDLE_PERP * RATCHET_HEAD_RADIUS` from the head axis; a hand-written
    # `0.55 * _RH_R` buried the pivot inside the head, so `handle_bar` grew out of
    # the middle of `head_body` and rammed it 6.4mm in the CLOSED pose.
    boss_x = _RH_R * s
    head.visual(
        Cylinder(radius=_RH_BOSS_R * s, length=_RH_BOSS_L * s),
        origin=Origin(xyz=(boss_x, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["hardware"],
        name="pivot_boss", material_class_id=("metal.stainless_matte" if r.palette_style in {"black_blue_enamel", "blue_enamel_bench", "forged_steel_natural", "zinc_hardware"} else "metal.blackened_gunmetal"),
    )
    # (4) Direction-selector nub (S4 L231-L241).
    head.visual(
        Cylinder(radius=_RH_NUB_R * s, length=_RH_NUB_L * s),
        origin=Origin(xyz=(-boss_x, 0.0, _RH_L * s * 0.30), rpy=(0.0, 0.0, 0.0)),
        material=mats["accent"],
        name="selector_nub", material_class_id=("metal.paint_coated" if r.palette_style in {"black_blue_enamel", "blue_enamel_bench", "zinc_hardware", "black_rubber_shop"} else "metal.steel_bare"),
    )
    model.articulation(
        "spindle_turn",
        ArticulationType.REVOLUTE,
        parent=carriage,
        child=head,
        origin=Origin(xyz=(0.0, 0.0, -_HUB_CENTER_T * s)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(
            effort=45.0, velocity=5.0, lower=-2.0 * math.pi, upper=2.0 * math.pi
        ),
        meta={
            "mechanism": "ratchet head rotates about the working axis",
            "captured": True,
        },
    )

    handle = model.part("ratchet_handle", meta={"role": "folding ratchet handle"})
    hl = _HANDLE_L * s * r.handle_len_scale
    # Authored in the fold-joint local frame: bar extends +X from the pivot.
    # S4 L62-L67 measures WIDTH in its tool plane and THICKNESS out of plane; the
    # canonical frame's tool plane is XZ and its out-of-plane normal is b=+Y, so the
    # re-base puts _HANDLE_TH on y and _HANDLE_W on z (they were swapped, which laid
    # the flat bar on its side).
    handle.visual(
        Box((hl, _HANDLE_TH * s, _HANDLE_W * s)),
        origin=Origin(xyz=(hl / 2.0, 0.0, 0.0)),
        material=mats["driver"],
        name="handle_bar", material_class_id=("metal.stainless_matte" if r.palette_style in {"black_blue_enamel", "blue_enamel_bench", "zinc_hardware", "black_rubber_shop"} else "metal.steel_bare"),
    )
    # (4) Rubber overmold grip at the far end (S4 L298-L309) — rides the realized
    # handle length.
    handle.visual(
        Box((_GRIP_L * s, _GRIP_TH * s, _GRIP_W * s)),
        origin=Origin(xyz=(hl - _GRIP_L * s / 2.0, 0.0, 0.0)),
        material=mats["grip"],
        name="handle_grip", material_class_id="rubber.smooth_plain",
    )
    # Captured pin-through-lug (head pivot_boss through the handle's drilled
    # rounded end) -> omits MatingContract per Rule 2 grandfather.
    # Axis is -b, NOT +b: with +b a positive fold swings the handle DOWN into the
    # spindle and the frame (S4's fold stows the handle back along the spindle, away
    # from the work). -b lifts it toward the spindle rear, which is free air.
    model.articulation(
        "ratchet_fold",
        ArticulationType.REVOLUTE,
        parent=head,
        child=handle,
        origin=Origin(xyz=(boss_x, 0.0, 0.0)),
        axis=_FOLD_AXIS,
        motion_limits=MotionLimits(effort=20.0, velocity=2.0, lower=0.0, upper=_FOLD_UPPER),
        meta={
            "mechanism": "handle folds about the body normal, stowing along the spindle rear",
            "opens_toward": "+z (away from the cradle)",
            "captured": True,
        },
    )
    # Contract 3d: the fold is clearance-dependent, so SOLVE it instead of
    # hand-deriving trig. The handle folds until it meets its own head — a real
    # hard stop — so the realized upper is whatever the milled clevis clears.
    # The pivot capture (handle root on the head's boss) is invariant to the fold
    # value and is exempted element-scoped, so it cannot mask a real sweep hit.
    # margin must sit UNDER the clevis's milled running clearance
    # (`_RATCHET_FOLD_CLEAR`), which is the constant the handle rides on for the
    # whole fold; a margin above it reads the running fit itself as a collision and
    # solves the joint to zero travel.
    clamp_joint_limits(
        model,
        "ratchet_fold",
        margin=_RATCHET_FOLD_CLEAR * 0.4,
        keepout=["ratchet_head"],
        allowed_pairs=[
            ("ratchet_head", "ratchet_handle", "pivot_boss", "handle_bar"),
            ("ratchet_head", "ratchet_handle", "pivot_boss", "handle_grip"),
        ],
        scan_steps=14,
    )
    return head, handle


def _emit_compound_toggle(model, frame, carriage, r: ResolvedChainSeparatorConfig, mats):
    """(2)+(1) compound toggle: the lever is a child of the FRAME, not the
    carriage — a genuinely different kinematic graph. S5 L275-L352, L457-L488.

    Open-chain expression (the link's far end is not pinned back to the carriage),
    matching S5 and keeping the model URDF-legal.
    """
    s = r.s
    px, pz = r.lever_pivot_xz
    lever = model.part("toggle_lever", meta={"role": "toggle lever arm", "length": _LEVER_L * s})
    ll = _LEVER_L * s * r.handle_len_scale
    # Profiled arm with a widened grip end + arc tip (S5 L281-L294), authored in
    # the pivot-local frame and extending +X.
    arm = (
        cq.Workplane("XZ")
        .moveTo(0.0, -_LEVER_W * s / 2.0)
        .lineTo(ll - 0.022 * s, -_LEVER_W * s / 2.0)
        .lineTo(ll - 0.016 * s, -_LEVER_GRIP_W * s / 2.0)
        .lineTo(ll - 0.006 * s, -_LEVER_GRIP_W * s / 2.0)
        .threePointArc((ll, 0.0), (ll - 0.006 * s, _LEVER_GRIP_W * s / 2.0))
        .lineTo(ll - 0.016 * s, _LEVER_GRIP_W * s / 2.0)
        .lineTo(ll - 0.022 * s, _LEVER_W * s / 2.0)
        .lineTo(0.0, _LEVER_W * s / 2.0)
        .threePointArc((-_LEVER_W * s / 2.0, 0.0), (0.0, -_LEVER_W * s / 2.0))
        .close()
        .extrude(_LEVER_TH * s / 2.0, both=True)
    )
    # Pivot hole clearing the frame boss (S5 L307-L310).
    hole = cq.Workplane("XZ").circle(_LEVER_HOLE_R * s).extrude(_LEVER_TH * s * 2.0, both=True)
    arm = arm.cut(hole)
    lever.visual(
        mesh_from_cadquery(arm, "toggle_lever_arm", tolerance=0.0004),
        material=mats["accent"],
        name="lever_arm", material_class_id=("metal.paint_coated" if r.palette_style in {"black_blue_enamel", "blue_enamel_bench", "zinc_hardware", "black_rubber_shop"} else "metal.steel_bare"),
    )
    # Toggle attachment boss the link pivots on (S5 L299-L305).
    lever.visual(
        Cylinder(radius=_TOGGLE_BOSS_R * s, length=_TOGGLE_BOSS_L * s),
        origin=Origin(xyz=(_TOGGLE_ATTACH * s, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["hardware"],
        name="toggle_boss", material_class_id=("metal.stainless_matte" if r.palette_style in {"black_blue_enamel", "blue_enamel_bench", "forged_steel_natural", "zinc_hardware"} else "metal.blackened_gunmetal"),
    )
    # Captured pin-through-hole (lever hole over the frame's lever_pivot_boss)
    # -> omits MatingContract per Rule 2 grandfather.
    model.articulation(
        "lever_pivot",
        ArticulationType.REVOLUTE,
        parent=frame,
        child=lever,
        origin=Origin(xyz=(px, 0.0, pz)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=120.0, velocity=4.0, lower=0.0, upper=_LEVER_UPPER),
        meta={"mechanism": "toggle lever pivots on the frame boss", "captured": True},
    )

    link = model.part("toggle_link", meta={"role": "toggle connecting rod"})
    link_len = max(_TOGGLE_ATTACH * s * 0.9, 0.018 * s)
    rod = (
        cq.Workplane("XZ")
        .moveTo(0.0, -_LINK_W * s / 2.0)
        .lineTo(link_len, -_LINK_W * s / 2.0)
        .threePointArc((link_len + _LINK_W * s * 0.3, 0.0), (link_len, _LINK_W * s / 2.0))
        .lineTo(0.0, _LINK_W * s / 2.0)
        .threePointArc((-_LINK_W * s * 0.3, 0.0), (0.0, -_LINK_W * s / 2.0))
        .close()
        .extrude(_LINK_TH * s / 2.0, both=True)
    )
    pin_hole = cq.Workplane("XZ").circle(_LINK_HOLE_R * s).extrude(_LINK_TH * s * 2.0, both=True)
    rod = rod.cut(pin_hole)
    link.visual(
        mesh_from_cadquery(rod, "toggle_link_rod", tolerance=0.0004),
        material=mats["driver"],
        name="link_rod", material_class_id=("metal.stainless_matte" if r.palette_style in {"black_blue_enamel", "blue_enamel_bench", "zinc_hardware", "black_rubber_shop"} else "metal.steel_bare"),
    )
    # Captured pin-through-hole (link hole over the lever's toggle_boss)
    # -> omits MatingContract per Rule 2 grandfather.
    model.articulation(
        "toggle_joint",
        ArticulationType.REVOLUTE,
        parent=lever,
        child=link,
        origin=Origin(xyz=(_TOGGLE_ATTACH * s, _TOGGLE_BOSS_L * s * 0.35, 0.0)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(
            effort=60.0, velocity=3.0, lower=_TOGGLE_LOWER, upper=_TOGGLE_UPPER
        ),
        meta={"mechanism": "toggle link pivots on the lever boss", "captured": True},
    )
    return lever, link


# ---------------------------------------------------------------------------
# Builder
# ---------------------------------------------------------------------------
def build_pictureX_0611_Chain_separator(
    config: ChainSeparatorConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={
            "authoritative_features": (
                "rigid_reaction_frame",
                "aligned_driver",
                "chain_cradle",
                "visible_reaction_path",
            ),
            "frame_form_subtype": FRAME_FORM_SUBTYPE[r.frame_form],
            "cradle_form_subtype": CRADLE_FORM_SUBTYPE[r.cradle_form],
        },
    )
    palette = PALETTES[r.palette_style]
    mats = {
        key: model.material(f"chain_separator_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in palette.items()
    }

    # --- Slot A: root frame (publishes the shared anchor contract) ---
    frame = model.part(
        "frame",
        meta={
            "construction": r.frame_form,
            "form_subtype": FRAME_FORM_SUBTYPE[r.frame_form],
            "dominant_color": r.palette_style,
        },
    )
    _FRAME_EMITTERS[r.frame_form](frame, r, mats)
    _emit_nut_boss(frame, r, mats)
    if r.drive_form == "compound_toggle":
        _emit_lever_boss(frame, r, mats)
    if r.cradle_form == "rotating_seat_turret":
        _emit_turret_pin(frame, r, mats)
    if r.chain_guide == "sliding_cheek_guide":
        _emit_guide_rail_slot(frame, r, mats)
    frame.inertial = Inertial.from_geometry(
        Box((0.10 * r.s, r.body_half_y * 2.0, 0.08 * r.s)),
        mass=0.32,
        origin=Origin(xyz=(0.0, 0.0, 0.01 * r.s)),
    )

    # --- Slot B: drive ---
    carriage = _emit_driver_carriage(model, frame, r, mats)
    if r.drive_form == "screw_tbar":
        _emit_screw_tbar(model, carriage, r, mats)
    elif r.drive_form == "ratchet_socket":
        _emit_ratchet_socket(model, carriage, r, mats)
    else:
        _emit_compound_toggle(model, frame, carriage, r, mats)

    # --- Slot C: cradle (static forms are host geometry; only the turret adds a part) ---
    if r.cradle_form == "rotating_seat_turret":
        _emit_anvil_turret(model, frame, r, mats)

    # --- Slot D: guide ---
    if r.chain_guide == "sliding_cheek_guide":
        _emit_guide_carriage(model, frame, r, mats)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_pictureX_0611_Chain_separator(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_pictureX_0611_Chain_separator(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def run_pictureX_0611_Chain_separator_tests(
    object_model: ArticulatedObject,
    config: ChainSeparatorConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    frame = object_model.get_part("frame")
    carriage = object_model.get_part("driver_carriage")
    feed = object_model.get_articulation("driver_feed")

    # --- Element-scoped intentional contacts (Rule 7). Every allowance names an
    # exact element pair and a physical reason. NO whole-part allowance and NO
    # allow_isolated_part anywhere (the source records use both; the template
    # replaces them with real capture interference — spec Reject cases 1-2).
    driver_elem = "driver_rod" if r.drive_form == "compound_toggle" else "spindle_thread"
    if r.drive_form == "compound_toggle":
        ctx.allow_overlap(
            frame,
            carriage,
            elem_a="spindle_nut_boss",
            elem_b=driver_elem,
            reason=(
                "Rod-in-bore bearing: the rod's two guide rings are "
                f"{_CAPTURE_FIT * 1000:.1f}mm over the nut boss's bore and ride inside "
                "it across the whole stroke — that IS the support contact carrying "
                "the toggle rod (S5 L222-L273 rings in the S1 L126-L145 sleeve/bore)."
            ),
        )
    else:
        ctx.allow_overlap(
            frame,
            carriage,
            elem_a="spindle_nut_boss",
            elem_b=driver_elem,
            reason=(
                "Thread-flank contact: the spindle's crests are "
                f"{(_C_CREST_R - _NUT_BORE_R) * 1000:.1f}mm over the tapped nut boss's "
                "bore, which IS the screw engagement (S1 L173-L177 crests inside the "
                "S1 L126-L145 sleeve/bore)."
            ),
        )

    if r.drive_form == "screw_tbar":
        hub = object_model.get_part("spindle_hub")
        t_bar = object_model.get_part("t_bar")
        ctx.allow_overlap(
            carriage,
            hub,
            elem_a=driver_elem,
            elem_b="hub_body",
            reason=(
                "The spindle hub is captured concentrically around the silver spindle "
                "tenon (S1 L497-L512 expect_overlap idiom)."
            ),
        )
        ctx.allow_overlap(
            hub,
            t_bar,
            elem_a="hub_body",
            elem_b="bar_shaft",
            reason="The T-bar is captured in the hub's drilled transverse bore (S1 L212-L221).",
        )
        ctx.expect_overlap(
            carriage,
            hub,
            axes="xy",
            elem_a=driver_elem,
            elem_b="hub_body",
            min_overlap=0.0038,
            name="drilled hub remains captured on the spindle",
        )
    elif r.drive_form == "ratchet_socket":
        head = object_model.get_part("ratchet_head")
        handle = object_model.get_part("ratchet_handle")
        ctx.allow_overlap(
            carriage,
            head,
            elem_a=driver_elem,
            elem_b="head_body",
            reason="The ratchet head is captured concentrically around the spindle tenon (S4 L608-L654).",
        )
        ctx.allow_overlap(
            head,
            handle,
            elem_a="pivot_boss",
            elem_b="handle_bar",
            reason="The handle's drilled rounded end is captured on the head pivot boss (S4 L221-L258).",
        )
    else:
        lever = object_model.get_part("toggle_lever")
        link = object_model.get_part("toggle_link")
        ctx.allow_overlap(
            frame,
            lever,
            elem_a="lever_pivot_boss",
            elem_b="lever_arm",
            reason="The lever's pivot hole is captured on the frame boss (S5 L205-L214, L307-L310).",
        )
        ctx.allow_overlap(
            lever,
            link,
            elem_a="toggle_boss",
            elem_b="link_rod",
            reason="The link's pin hole is captured on the lever's toggle boss (S5 L299-L339).",
        )

    if r.cradle_form == "rotating_seat_turret":
        turret = object_model.get_part("anvil_turret")
        ctx.allow_overlap(
            frame,
            turret,
            elem_a="turret_pivot_pin",
            elem_b="turret_disk",
            reason=(
                "The turret disk's central bore is captured on the frame pivot pin "
                "(pin-in-bore bearing; S6 L50-L51, L250-L257)."
            ),
        )

    if r.chain_guide == "sliding_cheek_guide":
        guide = object_model.get_part("guide_carriage")
        ctx.allow_overlap(
            frame,
            guide,
            elem_a="guide_rail_slot",
            elem_b="rail_tongue",
            reason="The guide tongue rides the frame's rail slot (close-fit rail contact; S7 L121-L130).",
        )

    # --- Model integrity (compiler baseline) ---
    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_joint_mating_has_gap()
    # Rule 5: dynamic overlap across every non-FIXED joint (<=5 joints => 48
    # covers {0, lower, upper, mid} per joint plus the lever x toggle combos).
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=48, ignore_fixed=True)

    # --- Structural contract ---
    expected = {"frame", "driver_carriage"}
    if r.drive_form == "screw_tbar":
        expected |= {"spindle_hub", "t_bar"}
    elif r.drive_form == "ratchet_socket":
        expected |= {"ratchet_head", "ratchet_handle"}
    else:
        expected |= {"toggle_lever", "toggle_link"}
    if r.cradle_form == "rotating_seat_turret":
        expected |= {"anvil_turret"}
    if r.chain_guide == "sliding_cheek_guide":
        expected |= {"guide_carriage"}
    actual = {p.name for p in object_model.parts}
    ctx.check(
        "part set matches the resolved slot choices",
        actual == expected,
        details=f"expected={sorted(expected)}, actual={sorted(actual)}",
    )
    ctx.check(
        "frame is the sole connected hierarchy root",
        [p.name for p in object_model.root_parts()] == ["frame"],
        details=f"roots={[p.name for p in object_model.root_parts()]}",
    )
    # Rule 1: static detail is host visuals — no FIXED articulation exists.
    ctx.check(
        "no FIXED articulation (static detail is host visuals)",
        all(j.articulation_type != ArticulationType.FIXED for j in object_model.articulations),
        details=f"types={[str(j.articulation_type) for j in object_model.articulations]}",
    )

    # --- Category identity: aligned driver + cradle reaction path ---
    ctx.check(
        "driver_feed is PRISMATIC along the working axis a=(0,0,-1)",
        feed.articulation_type == ArticulationType.PRISMATIC
        and tuple(round(c, 6) for c in feed.axis) == A_AXIS
        and feed.motion_limits is not None
        and feed.motion_limits.upper > 0.003,
        details=f"axis={feed.axis}, limits={feed.motion_limits}",
    )
    ctx.check(
        "driver axis is collinear with the cradle centerline (aligned driver)",
        abs(feed.origin.xyz[0]) < 1e-9 and abs(feed.origin.xyz[1]) < 1e-9,
        details=f"driver_feed origin={feed.origin.xyz}",
    )

    # --- Joint semantics per slot ---
    if r.drive_form == "screw_tbar":
        turn = object_model.get_articulation("spindle_turn")
        slide = object_model.get_articulation("t_bar_slide")
        ctx.check(
            "spindle_turn REVOLUTE +/-2pi and t_bar_slide PRISMATIC on the body normal",
            turn.articulation_type == ArticulationType.REVOLUTE
            and abs(turn.motion_limits.upper - 2.0 * math.pi) < 1e-6
            and slide.articulation_type == ArticulationType.PRISMATIC
            and tuple(round(c, 6) for c in slide.axis) == B_AXIS,
            details=f"turn={turn.motion_limits}, slide axis={slide.axis}",
        )
        t_bar = object_model.get_part("t_bar")
        hub = object_model.get_part("spindle_hub")
        ctx.check(
            "T-bar end stops are larger than the hub bore (retained)",
            _BAR_STOP_R > _HUB_BAR_BORE_R,
            details=f"stop_r={_BAR_STOP_R}, bar_bore_r={_HUB_BAR_BORE_R}",
        )
        # Targeted semantics: the bar slides along the body normal only.
        rest = ctx.part_world_position(t_bar)
        with ctx.pose({slide: slide.motion_limits.upper}):
            moved = ctx.part_world_position(t_bar)
        if rest is not None and moved is not None:
            ctx.check(
                "t_bar_slide translates purely along the body normal",
                abs(moved[0] - rest[0]) < 1e-6
                and abs((moved[1] - rest[1]) - slide.motion_limits.upper) < 1e-6
                and abs(moved[2] - rest[2]) < 1e-6,
                details=f"rest={rest}, moved={moved}",
            )
        # Targeted semantics: turning the spindle does not translate the hub.
        hub_rest = _aabb_center(ctx.part_world_aabb(hub))
        with ctx.pose({turn: math.pi}):
            hub_turned = _aabb_center(ctx.part_world_aabb(hub))
        if hub_rest is not None and hub_turned is not None:
            ctx.check(
                "spindle_turn is captive rotation (no hub translation)",
                max(abs(a - b) for a, b in zip(hub_rest, hub_turned)) < 5e-4,
                details=f"rest={hub_rest}, turned={hub_turned}",
            )
    elif r.drive_form == "ratchet_socket":
        fold = object_model.get_articulation("ratchet_fold")
        ctx.check(
            "ratchet_fold is REVOLUTE about the body-normal line with a real fold range",
            fold.articulation_type == ArticulationType.REVOLUTE
            and tuple(round(c, 6) for c in fold.axis) == _FOLD_AXIS
            and fold.motion_limits.lower == 0.0
            and fold.motion_limits.upper > 1.0,
            details=f"fold={fold.motion_limits}, axis={fold.axis}",
        )
        handle = object_model.get_part("ratchet_handle")
        # clamp_joint_limits() solved the realized fold against the head's clevis;
        # drive to whatever it kept rather than to a hard-coded 1.8.
        fold_max = fold.motion_limits.upper
        rest = _aabb_center(ctx.part_world_aabb(handle))
        with ctx.pose({fold: fold_max}):
            folded = _aabb_center(ctx.part_world_aabb(handle))
        if rest is not None and folded is not None:
            # Rule 5 targeted semantics: folding must STOW the handle back along the
            # spindle rear (+z, away from the cradle), not swing it into the frame.
            ctx.check(
                "ratchet_fold lifts the handle away from the cradle (stows along the spindle)",
                (folded[2] - rest[2]) > 0.004 and folded[0] < rest[0],
                details=f"rest={rest}, folded={folded}, fold_max={fold_max:.4f}",
            )
        ctx.check(
            "ratchet_fold keeps a real solved fold range",
            fold_max > 0.5,
            details=f"solved upper={fold_max:.4f} (declared candidate {_FOLD_UPPER})",
        )
    else:
        lever_j = object_model.get_articulation("lever_pivot")
        toggle_j = object_model.get_articulation("toggle_joint")
        ctx.check(
            "compound toggle: lever is a child of the FRAME and the link a child of the lever",
            lever_j.parent == "frame"
            and lever_j.child == "toggle_lever"
            and toggle_j.parent == "toggle_lever"
            and toggle_j.child == "toggle_link"
            and lever_j.articulation_type == ArticulationType.REVOLUTE
            and toggle_j.articulation_type == ArticulationType.REVOLUTE,
            details=f"lever {lever_j.parent}->{lever_j.child}, toggle {toggle_j.parent}->{toggle_j.child}",
        )
        lever = object_model.get_part("toggle_lever")
        rest = _aabb_center(ctx.part_world_aabb(lever))
        with ctx.pose({lever_j: lever_j.motion_limits.upper}):
            closed = _aabb_center(ctx.part_world_aabb(lever))
        if rest is not None and closed is not None:
            # Rule 5 targeted semantics: the lever arm really SWINGS up about the
            # frame boss (the pivot stays captive, the arm sweeps toward +z).
            ctx.check(
                "lever_pivot swings the arm up about the captive frame boss",
                (closed[2] - rest[2]) > 0.004 and closed[0] < rest[0],
                details=f"rest={rest}, closed={closed}",
            )

    if r.cradle_form == "rotating_seat_turret":
        ti = object_model.get_articulation("turret_index")
        ctx.check(
            "turret_index is REVOLUTE about the body normal over a full turn",
            ti.articulation_type == ArticulationType.REVOLUTE
            and tuple(round(c, 6) for c in ti.axis) == B_AXIS
            and ti.motion_limits.lower == 0.0
            and abs(ti.motion_limits.upper - 2.0 * math.pi) < 1e-6,
            details=f"axis={ti.axis}, limits={ti.motion_limits}",
        )
        turret = object_model.get_part("anvil_turret")
        ctx.check(
            "turret carries three chain-gauge seat inserts",
            len([v for v in turret.visuals if v.name.startswith("seat_insert_")]) == 3,
            details=f"visuals={[v.name for v in turret.visuals]}",
        )
        # Targeted semantics: indexing to seat 1 rotates the disk on its pin without
        # walking it out of the pocket (a bored disk turning about its own centre
        # keeps its AABB centre; drift here would mean the origin/axis is wrong).
        t_rest = _aabb_center(ctx.part_world_aabb(turret))
        with ctx.pose({ti: 2.0 * math.pi / 3.0}):
            t_idx = _aabb_center(ctx.part_world_aabb(turret))
        if t_rest is not None and t_idx is not None:
            ctx.check(
                "turret indexing is captive rotation (no translation)",
                max(abs(a - b) for a, b in zip(t_rest, t_idx)) < 5e-4,
                details=f"rest={t_rest}, indexed={t_idx}",
            )
        # The anvil crown IS the cradle seat plane, and the pin stops above it.
        ctx.check(
            "turret anvil crown sits on the cradle seat datum and the pin stops above it",
            abs(r.turret_crown_z - r.cradle_z) < 1e-9
            and (r.tip_rest_z - r.feed_upper) > r.turret_crown_z,
            details=(
                f"crown_z={r.turret_crown_z}, seat={r.cradle_z}, "
                f"pin_min_z={r.tip_rest_z - r.feed_upper}"
            ),
        )
        # Contract 3c: thickness derives from the frame's channel, never restated.
        ctx.check(
            "turret thickness derives from the frame's cradle channel",
            abs(r.turret_thickness - (r.cradle_channel_w - 0.0012)) < 1e-9
            or r.turret_thickness == 0.0025,
            details=f"turret_th={r.turret_thickness}, channel={r.cradle_channel_w}",
        )

    if r.chain_guide == "sliding_cheek_guide":
        gs = object_model.get_articulation("guide_slide")
        ctx.check(
            "guide_slide is PRISMATIC across the driver axis with a real MatingContract",
            gs.articulation_type == ArticulationType.PRISMATIC
            and tuple(round(c, 6) for c in gs.axis) == H_AXIS
            and gs.mating is not None,
            details=f"axis={gs.axis}, mating={gs.mating}",
        )
        guide = object_model.get_part("guide_carriage")
        rest = ctx.part_world_position(guide)
        with ctx.pose({gs: gs.motion_limits.upper}):
            moved = ctx.part_world_position(guide)
        if rest is not None and moved is not None:
            ctx.check(
                "guide_slide translates purely across the driver axis",
                abs((moved[0] - rest[0]) - gs.motion_limits.upper) < 1e-6
                and abs(moved[1] - rest[1]) < 1e-6
                and abs(moved[2] - rest[2]) < 1e-6,
                details=f"rest={rest}, moved={moved}",
            )
        # Inequality: the tongue never leaves its slot.
        ctx.check(
            "guide travel keeps the tongue captured in the derived slot",
            r.guide_travel <= (r.guide_slot_len - _GUIDE_TONGUE_LEN * r.s) / 2.0 + 1e-9,
            details=f"travel={r.guide_travel}, slot={r.guide_slot_len}",
        )

    # --- Targeted driver semantics: the pin advances toward the cradle ---
    rest_pos = ctx.part_world_position(carriage)
    with ctx.pose({feed: feed.motion_limits.upper}):
        fed_pos = ctx.part_world_position(carriage)
    if rest_pos is not None and fed_pos is not None:
        ctx.check(
            "driver advances along -Z into the cradle only",
            abs(fed_pos[0] - rest_pos[0]) < 1e-6
            and abs(fed_pos[1] - rest_pos[1]) < 1e-6
            and (rest_pos[2] - fed_pos[2]) > 0.003,
            details=f"rest={rest_pos}, fed={fed_pos}",
        )

    # --- (6) palette diversity ---
    ctx.check(
        "materials carry the palette style tag",
        any(r.palette_style in m.name for m in object_model.materials),
        details=f"materials={[m.name for m in object_model.materials]}",
    )

    # --- slot_choices recorded and consistent ---
    ctx.check(
        "slot_choices_recorded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )
    return ctx.report()


__all__ = (
    "ChainSeparatorConfig",
    "ResolvedChainSeparatorConfig",
    "build_pictureX_0611_Chain_separator",
    "build_seeded_pictureX_0611_Chain_separator",
    "config_from_seed",
    "resolve_config",
    "run_pictureX_0611_Chain_separator_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
    "PALETTE_STYLES",
    "PALETTES",
)
