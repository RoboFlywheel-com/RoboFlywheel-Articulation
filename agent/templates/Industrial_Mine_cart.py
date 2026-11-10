# SPDX-License-Identifier: Apache-2.0

"""Industrial / Mine cart -- modular procedural template.

An industrial mine cart / rail skip: a low riveted-iron ``chassis`` (root) rolling
on 2 or 3 flanged ``wheelset`` axles (each CONTINUOUS roll), carrying a sheet-metal
/ cast-iron ``tub`` load body that dumps its ore -- by tipping about a REVOLUTE
trunnion (end-tip over +X, or side-tip over +Y) or by a vertical PRISMATIC
skip-hoist up guide columns. The identity feature is the raised end hoop carrying a
release mechanism (gravity latch hook REVOLUTE, or sliding bolt PRISMATIC); some
skips add a hinged tailgate door at the dump lip.

Slot graph (pattern = mixed: root + 3 parallel-children slots + an optional track
that takes over as root + 2 multiplicity axes ``wheelset_count`` /
``strap_band_count``):

    rail_track (root when track != none; sleepers/stringers + rails)
        \\-- cart_travel PRISMATIC along the rails
            chassis (root when track == none; riveted iron frame)
                |-- tip_mechanism  (end_tip / side_tip / hoist_lift; emits tub + defining joint)
                |-- latch          (gravity_hook / sliding_bolt; emits release + end hoop)
                \\-- wheels         (two_wheelsets / three_wheelsets; N rolling wheelsets)

The ``track`` slot (none / sleeper_rail / stringer_strap / steel_tie) opens a
dependent ``track_shape`` slot (straight / curved) that only exists when a track is
laid. A track lifts the whole cart by the profile's derived ``rail_top`` so the wheel
treads seat on the rail heads; ``none`` keeps the wheels on the ground plane.

Adapted per AUTHORING.md #A/#B from the confirmed 5-star Mine cart pool
(spec: specs_modular_v1/Industrial_Mine_cart.md). The tub shells are built as hand
``MeshGeometry`` lofts / a half-cylinder arc (same lofted-shell / trough primitive
family the cadquery sources use, Rule 3-preserving) to hold the <=20 s/seed compile
budget, exactly like Urban_Environment_Tipping_Barrow._lofted_tub_mesh.

The chaldron rim carries a ``rim_profile`` axis: ``saddle`` reproduces the origin
母本's longitudinal rim cut (dips at mid length, sweeps up at both ends), ``flat``
keeps the level rim the flat-panel sources use. The identity hoop is the sources'
single arch plate standing on the frame beam -- not a pair of loose rods, which on
the side-tip skeleton read as a stray length of rail track parked across the deck.

Sources (model.py:Lx-Ly in the spec Module Source Index):
  S1  origin 母本 rec_a-...c584b5ab  -- chassis, chaldron tub REVOLUTE end-tip,
      gravity hook latch, 2 spoked wheelsets, all test semantics.
  S2  form_box_tub          -- upright rectangular box tub.
  S3  form_trapezoid_tub    -- flat-panel trapezoidal V-tipper.
  S4  form_ubucket_tub      -- half-cylinder rolled trough skip.
  S5  form_disc_wheels      -- solid cast disc plate wheel (WheelFace).
  S6  joint_prismatic_lift  -- vertical PRISMATIC skip-hoist on guide columns.
  S7  joint_slide_bolt_latch-- sliding bolt PRISMATIC latch.
  S8  mult_strap_bands_four -- strap_band_count multiplicity.
  S9  mult_wheelsets_three  -- 3 rolling wheelsets.
  S10 skel_side_tip_mount   -- longitudinal side-tipping pivot.
  S11 skel_tailgate_door    -- hinged end-discharge door.
  S12 rec_a-dark-...6e20849c -- rail_track root (sleepers + I-rails), cart_travel
      PRISMATIC, and the "tread seated on the rail head" vertical datum. Unlike
      S1-S11 this is an UNRATED workbench record, and it is the only one in the pool
      that models a track at all; `steel_tie`, `stringer_strap` and the `curved`
      layout are world_knowledge_extrapolation on top of it (spec: 外推记录).

Coordinate frame: Z-up, floor z=0, +X along the track toward the tip/dump end,
+Y lateral. Tub authored centered on world (0,0), then seated so the tip joint
origin lies in the pivot-lug geometry (origin honesty).
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Literal

from agent.templates._modular import (
    InterfaceSpec,
    ModuleBuild,
    ModuleBuildContext,
    SlotSpec,
    assemble,
)
from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    Inertial,
    MeshGeometry,
    MotionLimits,
    Origin,
    SphereGeometry,
    TestContext,
    TestReport,
    WheelFace,
    WheelGeometry,
    WheelHub,
    WheelRim,
    WheelSpokes,
    mesh_from_geometry,
)

# Modular template: sweep coverage uses module_topology_diversity.
__modular__ = True


TipMechanism = Literal["end_tip", "side_tip", "hoist_lift"]
TubForm = Literal["chaldron", "box", "trapezoid", "ubucket"]
RimProfile = Literal["flat", "saddle"]
LatchModule = Literal["gravity_hook", "sliding_bolt"]
WheelModule = Literal["two_wheelsets", "three_wheelsets"]
WheelForm = Literal["spoked", "disc"]
TrackModule = Literal["none", "sleeper_rail", "stringer_strap", "steel_tie"]
TrackShape = Literal["straight", "curved"]
MineCartPalette = Literal[
    "rust_iron",
    "weathered_steel",
    "painted_green",
    "coal_black",
    "galvanized",
    "oxide_red",
]


# --------------------------------------------------------------------------- #
# Canonical dimensions (origin 母本 rec_a-...c584b5ab), world frame.
# --------------------------------------------------------------------------- #

WHEEL_RADIUS = 0.24
AXLE_X = 0.40           # rear/front axle X for 2-wheelset carts
WHEEL_Y = 0.33          # wheel lateral offset
AXLE_LEN = 0.88

FRAME_Z = 0.44          # side/end beam center height
DECK_TOP = 0.50         # top of frame deck (tub rests above)
TUB_BASE_Z = 0.655      # outer bottom of the tub
TUB_TOP_Z0 = 1.26       # nominal tub rim (before height scale)

TIP_PIVOT_END = (0.45, 0.0, 0.62)
TIP_PIVOT_SIDE = (0.0, 0.44, 0.62)

WALL_T = 0.035

# --- identity stirrup hoop (S1 build_hoop L129-L147 / S10 build_hoop L133-L151) --- #
# The sources cut the hoop as ONE flat iron plate: a rounded-top outer rectangle
# minus a rounded-top inner rectangle, i.e. a U-shaped arch with two flat legs
# standing on the frame beam. Two loose rods plus a crossbar are NOT the same
# component (MECHANICAL_PRIORS §1: keep the source's characteristic profile), and
# on the side-tip skeleton they read as a stray length of rail track parked on the
# deck instead of a stirrup arch, so the hoop is built as the plate arch here.
HOOP_PLATE_T = 0.035        # plate thickness (S1 L135 extrude 0.035)
HOOP_LEG_W = 0.06           # leg width = (outer - inner) half-span (S1 L134/L142)
HOOP_FOOT_EMBED = 0.04      # legs sink into the frame beam top for a real load path

HOOP_END_X = -0.775         # plate mid-plane, lapping the -X end beam (x -0.78..-0.70)
HOOP_END_HALF = 0.20        # outer half-span across Y (S1 L134 rect 0.40 wide)
HOOP_END_TOP = 1.10         # crown top (S1: 0.795 + 0.61/2)
HOOP_SIDE_HALF = 0.18       # outer half-span along X (S10 L138 rect 0.36 wide)
HOOP_SIDE_TOP = 0.94        # crown top (S10: 0.715 + 0.45/2)

CATCH_LUG_HALF = (0.0725, 0.04, 0.03)   # half extents of the tub catch lug

# --------------------------------------------------------------------------- #
# Rail track (S12 rec_a-dark-...6e20849c: `rail_track` root, sleepers + I-rails,
# `cart_travel` PRISMATIC, wheel treads seated on the rail heads).
# --------------------------------------------------------------------------- #

TRACK_GAUGE_Y = WHEEL_Y     # rail centreline half-gauge == the wheel plane
CART_HALF_LEN = 0.93        # buffer-head to buffer-head half length
TRACK_END_MARGIN = 0.16     # rail left beyond the cart at full travel
TRACK_ARC_SPAN = 0.50       # curved layout: total arc angle over the track length (rad)
TRACK_RAIL_SEAT = 0.035     # max lateral wheel/rail-head offset tolerated on a curve

# Each profile is (tie block, tie pitch, optional longitudinal stringer, rail layers
# stacked upward as (lateral width, height)). `rail_top` is derived from the stack,
# so each track type gives the cart its own ride height.
TRACK_PROFILES: dict[str, dict] = {
    # S12 L36-L38, L154-L185: wooden sleepers + flat-bottom I-rail (foot/web/head).
    "sleeper_rail": {
        "tie_material": "tie_wood",
        "tie": (0.20, 1.00, 0.06),
        "tie_pitch": 0.30,
        "stringer": None,
        "rail_layers": ((0.090, 0.022), (0.024, 0.055), (0.050, 0.028)),
    },
    # Extrapolated: pressed steel ties under a light flat-bottom rail (no tall web).
    "steel_tie": {
        "tie_material": "tie_steel",
        "tie": (0.14, 1.04, 0.05),
        "tie_pitch": 0.36,
        "stringer": None,
        "rail_layers": ((0.076, 0.018), (0.046, 0.042)),
    },
    # Extrapolated: early tramway road — longitudinal timber stringers carrying a
    # flat iron strap rail, with sparse transverse ties holding the gauge.
    "stringer_strap": {
        "tie_material": "tie_wood",
        "tie": (0.16, 0.96, 0.04),
        "tie_pitch": 0.62,
        "stringer": (0.13, 0.09),
        "rail_layers": ((0.075, 0.016),),
    },
}


# The rail head is always the LAST layer, so the tread datum is name-addressable
# whatever the section profile is.
RAIL_LAYER_NAMES: dict[int, tuple[str, ...]] = {
    1: ("rail_head",),
    2: ("rail_foot", "rail_head"),
    3: ("rail_foot", "rail_web", "rail_head"),
}


def _track_rail_top(track_module: str) -> float:
    prof = TRACK_PROFILES[track_module]
    z = prof["tie"][2]
    if prof["stringer"] is not None:
        z += prof["stringer"][1]
    return z + sum(h for (_w, h) in prof["rail_layers"])

# Chaldron saddle rim (S1 L36-L47, L76-L79, L107): the origin 母本 cuts the rolled
# rim with a longitudinal cylinder of radius SADDLE_R centred at SADDLE_CZ, so the
# rim dips in the middle and sweeps up at both ends. The flat-panel forms
# (box / trapezoid / ubucket sources) keep a level rim.
SADDLE_R_NOMINAL = 1.6
SADDLE_DIP_FRACTION = 0.55  # cap the dip at this share of the rim-to-mid-station gap


# --------------------------------------------------------------------------- #
# Palettes (>=5 colorways; shared token set so every .visual resolves).
# tokens: body (tub shell), frame (chassis frame), iron (hardware/hoop/rivets),
# wheel (wheelsets).
# --------------------------------------------------------------------------- #

PALETTES: dict[str, dict[str, tuple[float, float, float, float]]] = {
    "rust_iron": {
        "body": (0.455, 0.235, 0.125, 1.0),
        "frame": (0.40, 0.205, 0.11, 1.0),
        "iron": (0.135, 0.125, 0.12, 1.0),
        "wheel": (0.115, 0.11, 0.105, 1.0),
        "tie_wood": (0.42, 0.29, 0.18, 1.0),
        "tie_steel": (0.32, 0.33, 0.34, 1.0),
        "rail": (0.55, 0.53, 0.50, 1.0),
    },
    "weathered_steel": {
        "body": (0.50, 0.51, 0.53, 1.0),
        "frame": (0.40, 0.41, 0.43, 1.0),
        "iron": (0.16, 0.17, 0.18, 1.0),
        "wheel": (0.22, 0.23, 0.24, 1.0),
        "tie_wood": (0.46, 0.36, 0.26, 1.0),
        "tie_steel": (0.34, 0.35, 0.37, 1.0),
        "rail": (0.60, 0.61, 0.63, 1.0),
    },
    "painted_green": {
        "body": (0.19, 0.42, 0.24, 1.0),
        "frame": (0.15, 0.33, 0.19, 1.0),
        "iron": (0.10, 0.11, 0.10, 1.0),
        "wheel": (0.12, 0.13, 0.12, 1.0),
        "tie_wood": (0.44, 0.31, 0.19, 1.0),
        "tie_steel": (0.30, 0.32, 0.31, 1.0),
        "rail": (0.58, 0.60, 0.60, 1.0),
    },
    "coal_black": {
        "body": (0.14, 0.14, 0.15, 1.0),
        "frame": (0.10, 0.10, 0.11, 1.0),
        "iron": (0.05, 0.05, 0.06, 1.0),
        "wheel": (0.06, 0.06, 0.07, 1.0),
        "tie_wood": (0.30, 0.22, 0.15, 1.0),
        "tie_steel": (0.22, 0.23, 0.24, 1.0),
        "rail": (0.48, 0.49, 0.51, 1.0),
    },
    "galvanized": {
        "body": (0.70, 0.72, 0.74, 1.0),
        "frame": (0.60, 0.62, 0.64, 1.0),
        "iron": (0.34, 0.35, 0.37, 1.0),
        "wheel": (0.40, 0.41, 0.43, 1.0),
        "tie_wood": (0.50, 0.39, 0.28, 1.0),
        "tie_steel": (0.44, 0.46, 0.48, 1.0),
        "rail": (0.68, 0.70, 0.72, 1.0),
    },
    "oxide_red": {
        "body": (0.55, 0.20, 0.14, 1.0),
        "frame": (0.44, 0.17, 0.12, 1.0),
        "iron": (0.16, 0.11, 0.10, 1.0),
        "wheel": (0.13, 0.10, 0.09, 1.0),
        "tie_wood": (0.40, 0.27, 0.17, 1.0),
        "tie_steel": (0.33, 0.30, 0.29, 1.0),
        "rail": (0.54, 0.51, 0.49, 1.0),
    },
}
PALETTE_NAMES = tuple(PALETTES.keys())


# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class IndustrialMineCartConfig:
    tip_mechanism: TipMechanism = "end_tip"
    tub_form: TubForm = "chaldron"
    rim_profile: RimProfile = "saddle"
    latch_module: LatchModule = "gravity_hook"
    wheel_module: WheelModule = "two_wheelsets"
    wheel_form: WheelForm = "spoked"
    track_module: TrackModule = "none"
    track_shape: TrackShape = "straight"
    palette_style: MineCartPalette = "rust_iron"

    has_tailgate: bool = False
    strap_band_count: int = 2
    cart_travel: float = 0.24   # PRISMATIC travel along the track (m, per side)

    tub_height_scale: float = 1.0
    tub_len_scale: float = 1.0
    wheel_radius_scale: float = 1.0
    tip_upper: float = 0.6      # REVOLUTE tip range (rad)
    lift_travel: float = 0.50   # PRISMATIC hoist range (m)
    latch_range: float = 1.0    # gravity hook REVOLUTE range (rad)
    bolt_travel: float = 0.18   # sliding bolt PRISMATIC range (m)


@dataclass(frozen=True)
class ResolvedIndustrialMineCartConfig:
    tip_mechanism: TipMechanism
    tub_form: TubForm
    rim_profile: RimProfile
    latch_module: LatchModule
    wheel_module: WheelModule
    wheel_form: WheelForm
    track_module: TrackModule
    track_shape: TrackShape
    palette_style: str

    has_tailgate: bool
    strap_band_count: int
    wheelset_count: int

    tub_height_scale: float
    tub_len_scale: float
    wheel_radius_scale: float
    tip_upper: float
    lift_travel: float
    latch_range: float
    bolt_travel: float

    # Derived / single-sourced (Contract 3c).
    discharge: str                 # "end" | "side"
    axle_z: float                  # wheel center height = wheel radius (ground contact)
    wheel_radius: float
    tub_top_z: float               # rim height at the tub ends (max station)
    rim_min_z: float               # rim height at the saddle dip (== tub_top_z when flat)
    saddle_radius: float           # longitudinal rim arc radius (0.0 when flat)
    axle_positions: tuple[float, ...]
    tip_pivot: tuple[float, float, float]
    latch_pivot: tuple[float, float, float]
    latch_engage_z: float          # height at which the release toe/bolt holds the catch lug
    hoop_plane: float              # stirrup-plate mid-plane (x for end, y for side discharge)
    hoop_half_span: float          # plate outer half-span across its lateral axis
    hoop_foot_z: float             # leg feet height inside the frame beam
    hoop_top: float                # crown top, trimmed to clear the widest shell station

    rail_top: float                # rail head top in world z (0.0 with no track)
    track_len: float               # rail length along the centreline
    track_radius: float            # curved layout arc radius (0.0 when straight/absent)
    cart_travel: float             # cart_travel PRISMATIC range per side (m)

    palette: dict[str, tuple[float, float, float, float]]


def config_from_seed(seed: int) -> IndustrialMineCartConfig:
    """Deterministic procedural sampling.

    seed 0 is pinned to the origin 母本 combination (end_tip + chaldron with the
    saddle rim + gravity_hook + two_wheelsets spoked, 2 bands, rust_iron) as a
    documented regression anchor; every other seed is fully procedural.
    """
    if seed == 0:
        return IndustrialMineCartConfig()

    rng = random.Random(seed)

    tip_mechanism: TipMechanism = rng.choice(("end_tip", "side_tip", "hoist_lift"))
    tub_form: TubForm = rng.choice(("chaldron", "box", "trapezoid", "ubucket"))
    wheel_module: WheelModule = rng.choices(
        ("two_wheelsets", "three_wheelsets"), weights=(0.6, 0.4)
    )[0]
    wheel_form: WheelForm = rng.choice(("spoked", "disc"))

    # latch: sliding_bolt reads on the transverse end hoop; on side-tip the -Y
    # side latch is a swinging hook (gated in resolve_config).
    latch_module: LatchModule = rng.choice(("gravity_hook", "sliding_bolt"))

    # tailgate only makes sense at the +X dump lip of an end-tip flat-walled tub.
    eligible_tailgate = tip_mechanism == "end_tip" and tub_form in ("box", "trapezoid")
    has_tailgate = eligible_tailgate and rng.random() < 0.45

    strap_band_count = rng.choices((2, 4), weights=(0.6, 0.4))[0]
    palette_style = rng.choice(PALETTE_NAMES)

    tub_height_scale = round(rng.uniform(0.90, 1.15), 4)
    tub_len_scale = round(rng.uniform(0.90, 1.12), 4)
    wheel_radius_scale = round(rng.uniform(0.92, 1.05), 4)
    tip_upper = round(rng.uniform(0.45, 0.70), 4)
    lift_travel = round(rng.uniform(0.35, 0.55), 4)
    latch_range = round(rng.uniform(0.80, 1.10), 4)
    bolt_travel = round(rng.uniform(0.14, 0.20), 4)

    # ③ rim profile: only the curved chaldron shell carries the source's
    # saddle-cut rim; the flat-panel forms keep a level rim (gated in
    # resolve_config). Drawn last so the older seeds' other axes are untouched.
    rim_profile: RimProfile = rng.choice(("flat", "saddle"))

    # Track slot + its dependent shape slot. Drawn last so every earlier axis of an
    # existing seed keeps the value it had before the track slot existed.
    track_module: TrackModule = rng.choices(
        ("none", "sleeper_rail", "stringer_strap", "steel_tie"),
        weights=(0.42, 0.26, 0.16, 0.16),
    )[0]
    track_shape: TrackShape = rng.choices(("straight", "curved"), weights=(0.65, 0.35))[0]
    cart_travel = round(rng.uniform(0.18, 0.30), 4)

    return IndustrialMineCartConfig(
        tip_mechanism=tip_mechanism,
        tub_form=tub_form,
        rim_profile=rim_profile,
        latch_module=latch_module,
        wheel_module=wheel_module,
        wheel_form=wheel_form,
        track_module=track_module,
        track_shape=track_shape,
        palette_style=palette_style,
        has_tailgate=has_tailgate,
        strap_band_count=strap_band_count,
        cart_travel=cart_travel,
        tub_height_scale=tub_height_scale,
        tub_len_scale=tub_len_scale,
        wheel_radius_scale=wheel_radius_scale,
        tip_upper=tip_upper,
        lift_travel=lift_travel,
        latch_range=latch_range,
        bolt_travel=bolt_travel,
    )


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(float(v), hi))


def resolve_config(config: IndustrialMineCartConfig) -> ResolvedIndustrialMineCartConfig:
    if str(config.tip_mechanism) not in {"end_tip", "side_tip", "hoist_lift"}:
        raise ValueError(f"Unsupported tip_mechanism: {config.tip_mechanism}")
    if str(config.tub_form) not in {"chaldron", "box", "trapezoid", "ubucket"}:
        raise ValueError(f"Unsupported tub_form: {config.tub_form}")
    if str(config.rim_profile) not in {"flat", "saddle"}:
        raise ValueError(f"Unsupported rim_profile: {config.rim_profile}")
    if str(config.wheel_module) not in {"two_wheelsets", "three_wheelsets"}:
        raise ValueError(f"Unsupported wheel_module: {config.wheel_module}")
    if str(config.wheel_form) not in {"spoked", "disc"}:
        raise ValueError(f"Unsupported wheel_form: {config.wheel_form}")
    if str(config.track_module) not in {"none", *TRACK_PROFILES}:
        raise ValueError(f"Unsupported track_module: {config.track_module}")
    if str(config.track_shape) not in {"straight", "curved"}:
        raise ValueError(f"Unsupported track_shape: {config.track_shape}")
    if str(config.palette_style) not in PALETTES:
        raise ValueError(f"Unsupported palette_style: {config.palette_style}")

    # The deep narrow half-pipe (ubucket) can't seat on the shallow longitudinal
    # side-bearer pivot, so ubucket always end-tips (compatibility gate).
    tip_mechanism: TipMechanism = config.tip_mechanism
    if tip_mechanism == "side_tip" and config.tub_form == "ubucket":
        tip_mechanism = "end_tip"

    discharge = "side" if tip_mechanism == "side_tip" else "end"

    # Latch gating: the horizontal sliding bolt only fits the end-tip -X hoop; a
    # side-tip -Y hoop and a vertical hoist both take the swinging gravity hook
    # (a fixed bolt would foul the side dump / block the vertical lift).
    latch_module: LatchModule = config.latch_module
    if latch_module not in ("gravity_hook", "sliding_bolt"):
        latch_module = "gravity_hook"
    if tip_mechanism != "end_tip" and latch_module == "sliding_bolt":
        latch_module = "gravity_hook"

    # Tailgate gating: end-tip + flat-walled forms only.
    has_tailgate = bool(config.has_tailgate) and (
        tip_mechanism == "end_tip" and config.tub_form in ("box", "trapezoid")
    )

    wheelset_count = 3 if config.wheel_module == "three_wheelsets" else 2
    strap_band_count = 4 if int(config.strap_band_count) >= 4 else 2

    tub_height_scale = _clamp(config.tub_height_scale, 0.90, 1.15)
    tub_len_scale = _clamp(config.tub_len_scale, 0.90, 1.12)
    wheel_radius_scale = _clamp(config.wheel_radius_scale, 0.92, 1.05)
    tip_upper = _clamp(config.tip_upper, 0.45, 0.70)
    lift_travel = _clamp(config.lift_travel, 0.35, 0.55)
    latch_range = _clamp(config.latch_range, 0.80, 1.10)
    bolt_travel = _clamp(config.bolt_travel, 0.14, 0.20)

    wheel_radius = WHEEL_RADIUS * wheel_radius_scale
    if wheelset_count == 3:
        # Three axles must fit across the short canonical frame (end headstock
        # beams at x=+/-0.74, inner faces +/-0.70) without the three wheelsets
        # overlapping each other. That needs both adjacent-gap > 2R and
        # outer-edge (axle + R) inside the beam -> 3R < ~0.69. Real 3-axle mine
        # cars ride on smaller wheels, so cap R and use a 0.46 axle pitch:
        #   wheel-wheel gap = 0.46 - 2*0.215 = 0.030;  end-beam gap = 0.695 - 0.675 = 0.020.
        wheel_radius = min(wheel_radius, 0.215)
        axle_positions = (-0.46, 0.0, 0.46)
    else:
        axle_positions = (-AXLE_X, AXLE_X)
    axle_z = wheel_radius  # ground contact
    tub_top_z = TUB_BASE_Z + (TUB_TOP_Z0 - TUB_BASE_Z) * tub_height_scale

    # Saddle rim (③): only the curved chaldron shell; the flat-panel prototypes
    # keep the level rim their own sources use.
    rim_profile: RimProfile = config.rim_profile if config.tub_form == "chaldron" else "flat"
    rim_min_z = tub_top_z
    saddle_radius = 0.0
    if rim_profile == "saddle":
        # Rim arc through (+/-half_len, tub_top_z) and (0, tub_top_z - dip). The
        # nominal dip reproduces the source cylinder (R=1.6 centred 1.6 above the
        # rim ends); it is then capped so the dip never reaches the mid station,
        # which would fold the rim into the flared lower wall.
        half_len = 0.5 * _profile_at(config.tub_form, tub_len_scale, tub_top_z, tub_top_z)[0]
        mid_z = TUB_BASE_Z + 0.62 * (tub_top_z - TUB_BASE_Z)
        nominal_dip = SADDLE_R_NOMINAL - math.sqrt(
            max(SADDLE_R_NOMINAL * SADDLE_R_NOMINAL - half_len * half_len, 0.0)
        )
        dip = min(nominal_dip, SADDLE_DIP_FRACTION * (tub_top_z - mid_z))
        dip = max(dip, 0.02)
        saddle_radius = (half_len * half_len + dip * dip) / (2.0 * dip)
        rim_min_z = tub_top_z - dip

    tip_pivot = TIP_PIVOT_SIDE if discharge == "side" else TIP_PIVOT_END

    # The stirrup hoop plane, its latch pin and the tub catch lug are ONE
    # mechanism, so all three are derived here instead of drifting apart: the hook
    # hangs off the crown and its toe holds a lug on the tub wall.
    # Both releases hold the lug low on the wall, where the sources put it: the
    # hook's toe hangs off the crown pin (S1 L377-L388) and the bolt slides in a
    # keeper carried up from the end beam (S7 L52 BOLT_ORIGIN z=0.75, L309-L315).
    latch_engage_z = DECK_TOP + 0.25

    if discharge == "side":
        # The side hoop stands just clear of the widest thing it reaches — the shell
        # flare AND the catch lug proud of it (S10 L134-L135 puts it "outside the tub
        # flare"); the tub is free to overhang it higher up, where the hoop has ended.
        hoop_foot_z = FRAME_Z - 0.02
        hoop_half_span = HOOP_SIDE_HALF
        span = [hoop_foot_z + (HOOP_SIDE_TOP - hoop_foot_z) * i / 8.0 for i in range(9)]
        need = max(_half_at(config.tub_form, tub_len_scale, tub_top_z, z)[1] for z in span)
        need = max(need,
                   _half_at(config.tub_form, tub_len_scale, tub_top_z, latch_engage_z)[1]
                   + 0.02 + CATCH_LUG_HALF[1])
        hoop_plane = -max(need + 0.05, 0.50)
        hoop_top = HOOP_SIDE_TOP
        latch_pivot = (0.0, hoop_plane - 0.025, hoop_top - 0.06)
    else:
        hoop_foot_z = DECK_TOP - HOOP_FOOT_EMBED
        hoop_half_span = HOOP_END_HALF
        hoop_plane = HOOP_END_X
        # A long, low chaldron flares past the frame end, so trim the crown to the
        # last station that still clears the plate's inner face instead of burying
        # a fixed-height arch in the tub wall.
        clear_to = abs(hoop_plane) - 0.5 * HOOP_PLATE_T - 0.012
        hoop_top = HOOP_END_TOP
        floor_top = hoop_foot_z + 0.40
        while (hoop_top > floor_top
               and _half_at(config.tub_form, tub_len_scale, tub_top_z, hoop_top)[0] > clear_to):
            hoop_top -= 0.01
        latch_pivot = (hoop_plane - 0.025, 0.0, hoop_top - 0.16)

    # --- track slot + its dependent shape slot ---------------------------------
    # `track_shape` only exists when a track is laid; with `none` it collapses to
    # `straight` internally and is reported as "n/a" in slot_choices.
    track_module: TrackModule = config.track_module
    track_shape: TrackShape = config.track_shape if track_module != "none" else "straight"
    if track_module == "none":
        rail_top = 0.0
        track_len = 0.0
        track_radius = 0.0
        cart_travel = 0.0
    else:
        rail_top = _track_rail_top(track_module)
        travel = _clamp(config.cart_travel, 0.18, 0.30)
        track_len = 2.0 * (CART_HALF_LEN + travel + TRACK_END_MARGIN)
        if track_shape == "curved":
            # The wheelsets are rigid and square to the frame (a mine cart has no
            # steering bogie), so on a curve the rail walks sideways out from under
            # the tread by station^2 / 2R. Size the arc so the OUTERMOST wheel still
            # rides its rail head at every pose the travel joint can reach, then
            # shorten the travel to whatever that radius supports.
            track_radius = _clamp(track_len / TRACK_ARC_SPAN, 3.0, 6.0)
            ax_max = max(abs(a) for a in axle_positions)
            reach = math.sqrt(2.0 * TRACK_RAIL_SEAT * track_radius)
            cart_travel = _clamp(reach - ax_max, 0.08, travel)
        else:
            track_radius = 0.0
            cart_travel = travel

    return ResolvedIndustrialMineCartConfig(
        tip_mechanism=tip_mechanism,
        tub_form=config.tub_form,
        rim_profile=rim_profile,
        latch_module=latch_module,
        wheel_module=config.wheel_module,
        wheel_form=config.wheel_form,
        track_module=track_module,
        track_shape=track_shape,
        palette_style=config.palette_style,
        has_tailgate=has_tailgate,
        strap_band_count=strap_band_count,
        wheelset_count=wheelset_count,
        tub_height_scale=tub_height_scale,
        tub_len_scale=tub_len_scale,
        wheel_radius_scale=wheel_radius_scale,
        tip_upper=tip_upper,
        lift_travel=lift_travel,
        latch_range=latch_range,
        bolt_travel=bolt_travel,
        discharge=discharge,
        axle_z=axle_z,
        wheel_radius=wheel_radius,
        tub_top_z=tub_top_z,
        rim_min_z=rim_min_z,
        saddle_radius=saddle_radius,
        axle_positions=axle_positions,
        tip_pivot=tip_pivot,
        latch_pivot=latch_pivot,
        latch_engage_z=latch_engage_z,
        hoop_plane=hoop_plane,
        hoop_half_span=hoop_half_span,
        hoop_foot_z=hoop_foot_z,
        hoop_top=hoop_top,
        rail_top=rail_top,
        track_len=track_len,
        track_radius=track_radius,
        cart_travel=cart_travel,
        palette=dict(PALETTES[config.palette_style]),
    )


# --------------------------------------------------------------------------- #
# Tub shell profile + lofted-mesh geometry (Rule 3: lofted-shell / trough family,
# hand-built as MeshGeometry to hold the compile budget).
# --------------------------------------------------------------------------- #


def _lerp(t: float, a: float, b: float) -> float:
    return a + (b - a) * t


def _profile_at(tub_form: str, len_scale: float, top_z: float,
                z: float) -> tuple[float, float, float]:
    """Outer (length, width, corner_r) of the vertical-wall tub at world height z.

    Encodes the ③ Primary Form Family for chaldron/box/trapezoid (ubucket is a
    separate half-cylinder builder). ``t`` in [0,1] over the tub body height.
    Kept parameter-explicit so ``resolve_config`` can derive the rim arc and the
    hoop stand-off from the same single source of shell truth (Contract 3c)."""
    s = len_scale
    t = _clamp((z - TUB_BASE_Z) / max(top_z - TUB_BASE_Z, 1e-6), 0.0, 1.0)
    if tub_form == "box":
        return (1.10 * s, 0.80 * s, 0.05)
    if tub_form == "trapezoid":
        return (_lerp(t, 1.04, 1.24) * s, _lerp(t, 0.64, 0.90) * s, 0.03)
    # chaldron: strongly flared + rounded, mid bulge.
    if t <= 0.62:
        tt = t / 0.62
        return (_lerp(tt, 0.95, 1.24) * s, _lerp(tt, 0.62, 0.84) * s, _lerp(tt, 0.10, 0.13))
    tt = (t - 0.62) / 0.38
    return (_lerp(tt, 1.24, 1.52) * s, _lerp(tt, 0.84, 1.04) * s, _lerp(tt, 0.13, 0.16))


def _half_at(tub_form: str, len_scale: float, top_z: float, z: float) -> tuple[float, float]:
    """Outer half-length, half-width of the tub wall at height z (host-derived
    datum for strap bands, rivets, lugs and the hoop stand-off)."""
    if tub_form == "ubucket":
        R = 0.40 * len_scale
        cz = TUB_BASE_Z + R
        dz = _clamp(abs(z - cz), 0.0, R)
        hy = math.sqrt(max(R * R - dz * dz, 0.0))
        return (0.60 * len_scale, hy)
    length, width, _c = _profile_at(tub_form, len_scale, top_z, z)
    return (0.5 * length, 0.5 * width)


def _tub_profile(r: ResolvedIndustrialMineCartConfig, z: float) -> tuple[float, float, float]:
    return _profile_at(r.tub_form, r.tub_len_scale, r.tub_top_z, z)


def _tub_half(r: ResolvedIndustrialMineCartConfig, z: float) -> tuple[float, float]:
    return _half_at(r.tub_form, r.tub_len_scale, r.tub_top_z, z)


def _rim_z(r: ResolvedIndustrialMineCartConfig, x: float) -> float:
    """World height of the rolled rim at longitudinal station x.

    ``flat`` returns the level rim; ``saddle`` returns the source's longitudinal
    arc (S1 L76-L79) so the rim dips at mid length and sweeps up at both ends."""
    if r.rim_profile != "saddle" or r.saddle_radius <= 0.0:
        return r.tub_top_z
    R = r.saddle_radius
    half_len = 0.5 * _tub_profile(r, r.tub_top_z)[0]
    xx = _clamp(abs(x), 0.0, half_len)
    return r.tub_top_z - (
        math.sqrt(max(R * R - xx * xx, 0.0)) - math.sqrt(max(R * R - half_len * half_len, 0.0))
    )


def _ring(mesh: MeshGeometry, lo: list[int], hi: list[int]) -> None:
    n = len(lo)
    for i in range(n):
        j = (i + 1) % n
        mesh.add_face(lo[i], lo[j], hi[j])
        mesh.add_face(lo[i], hi[j], hi[i])


def _cap(mesh: MeshGeometry, loop: list[int], *, reverse: bool) -> None:
    cx = sum(mesh.vertices[i][0] for i in loop) / len(loop)
    cy = sum(mesh.vertices[i][1] for i in loop) / len(loop)
    cz = sum(mesh.vertices[i][2] for i in loop) / len(loop)
    c = mesh.add_vertex(cx, cy, cz)
    for i in range(len(loop)):
        j = (i + 1) % len(loop)
        if reverse:
            mesh.add_face(c, loop[j], loop[i])
        else:
            mesh.add_face(c, loop[i], loop[j])


PROFILE_CORNER_SEGMENTS = 6
PROFILE_SIDE_SEGMENTS = 12


def _rect_pts(length: float, width: float, corner: float) -> list[tuple[float, float]]:
    """CCW rounded-rect outline with the straight runs subdivided.

    ``rounded_rect_profile`` emits each straight side as a single segment, which is
    fine for a level loft but turns the saddle rim's long edges back into a straight
    chord. Sampling the sides keeps the index count fixed across stations (so every
    loft ring still pairs up) while letting the rim actually curve."""
    hl = 0.5 * length
    hw = 0.5 * width
    c = max(0.01, min(corner, 0.45 * min(length, width)))
    cs = PROFILE_CORNER_SEGMENTS
    ss = PROFILE_SIDE_SEGMENTS
    arcs = (
        ((hl - c, -hw + c), -0.5 * math.pi, 0.0),
        ((hl - c, hw - c), 0.0, 0.5 * math.pi),
        ((-hl + c, hw - c), 0.5 * math.pi, math.pi),
        ((-hl + c, -hw + c), math.pi, 1.5 * math.pi),
    )
    pts: list[tuple[float, float]] = []
    for k, ((cx, cy), a0, a1) in enumerate(arcs):
        for i in range(cs + 1):
            a = a0 + (a1 - a0) * i / cs
            pts.append((cx + c * math.cos(a), cy + c * math.sin(a)))
        # Straight run to the next arc's start.
        (nx, ny), na0, _na1 = arcs[(k + 1) % 4]
        end = (nx + c * math.cos(na0), ny + c * math.sin(na0))
        start = pts[-1]
        for i in range(1, ss):
            t = i / ss
            pts.append((start[0] + (end[0] - start[0]) * t,
                        start[1] + (end[1] - start[1]) * t))
    return pts


def _rect_loop(mesh: MeshGeometry, length: float, width: float, corner: float, z: float) -> list[int]:
    return [mesh.add_vertex(px, py, z) for (px, py) in _rect_pts(length, width, corner)]


def _rim_ring(r: ResolvedIndustrialMineCartConfig, *, d_len: float = 0.0, d_wid: float = 0.0,
              d_corner: float = 0.0) -> list[tuple[float, float, float]]:
    """Realized top ring of the shell loft, in world coordinates.

    ``flat`` is a level ring at ``tub_top_z``. ``saddle`` drops each station to
    ``_rim_z(x)`` and re-samples the shell section at that lower height, which is
    what the source's longitudinal cylinder cut produces: the rim dips at mid
    length and the flare (hence the plan-view width) shrinks with it. This is the
    single source for both the loft ring and the rim-rivet row, so the studs cannot
    drift off a rim they no longer describe."""
    length, width, corner = _tub_profile(r, r.tub_top_z)
    base = _rect_pts(length + d_len, width + d_wid, corner + d_corner)
    if r.rim_profile != "saddle":
        return [(px, py, r.tub_top_z) for (px, py) in base]
    ring: list[tuple[float, float, float]] = []
    for i, (px, _py) in enumerate(base):
        z = _rim_z(r, px)
        length_z, width_z, corner_z = _tub_profile(r, z)
        pts = _rect_pts(length_z + d_len, width_z + d_wid, corner_z + d_corner)
        qx, qy = pts[i]
        ring.append((qx, qy, z))
    return ring


def _rim_loop(mesh: MeshGeometry, r: ResolvedIndustrialMineCartConfig, *,
              d_len: float = 0.0, d_wid: float = 0.0, d_corner: float = 0.0) -> list[int]:
    return [mesh.add_vertex(x, y, z)
            for (x, y, z) in _rim_ring(r, d_len=d_len, d_wid=d_wid, d_corner=d_corner)]


def _build_vertical_tub_mesh(r: ResolvedIndustrialMineCartConfig, name: str) -> MeshGeometry:
    """Lofted hollow sheet-metal shell (outer + inner wall + floor + rolled rim)
    for chaldron / box / trapezoid, authored centered on world (0,0)."""
    mesh = MeshGeometry()
    floor_t = 0.04
    top = r.tub_top_z

    if r.tub_form == "chaldron":
        zs = [TUB_BASE_Z, TUB_BASE_Z + 0.62 * (top - TUB_BASE_Z)]
    else:
        zs = [TUB_BASE_Z]

    outer = []
    for z in zs:
        length, width, corner = _tub_profile(r, z)
        outer.append(_rect_loop(mesh, length, width, corner, z))
    outer.append(_rim_loop(mesh, r))
    inner = []
    for z in zs:
        length, width, corner = _tub_profile(r, max(z, TUB_BASE_Z + floor_t))
        inner.append(_rect_loop(mesh, max(0.10, length - 2 * WALL_T),
                                max(0.08, width - 2 * WALL_T),
                                max(0.01, corner - WALL_T),
                                max(z, TUB_BASE_Z + floor_t)))
    inner.append(_rim_loop(mesh, r, d_len=-2 * WALL_T, d_wid=-2 * WALL_T, d_corner=-WALL_T))
    # Outer wall.
    for i in range(len(outer) - 1):
        _ring(mesh, outer[i], outer[i + 1])
    # Inner wall (reversed normals).
    for i in range(len(inner) - 1):
        _ring(mesh, inner[i + 1], inner[i])
    # Rolled rim (outer top -> inner top).
    _ring(mesh, outer[-1], inner[-1])
    # Floor caps.
    _cap(mesh, outer[0], reverse=True)
    _cap(mesh, inner[0], reverse=False)
    return mesh


def _build_ubucket_mesh(r: ResolvedIndustrialMineCartConfig, name: str) -> MeshGeometry:
    """Half-cylinder U-section rolled trough (bucket skip): outer + inner arc
    surfaces, top rim strips, solid semicircular end plates. Open along the top."""
    mesh = MeshGeometry()
    s = r.tub_len_scale
    R = 0.40 * s
    Ri = R - WALL_T
    L = 1.20 * s
    cz = TUB_BASE_Z + R
    n = 16
    angs = [(-math.pi / 2.0) + math.pi * i / n for i in range(n + 1)]

    def arc(radius: float, x: float) -> list[int]:
        return [mesh.add_vertex(x, radius * math.sin(a), cz - radius * math.cos(a)) for a in angs]

    ox0, ox1 = arc(R, -L / 2.0), arc(R, L / 2.0)
    ix0, ix1 = arc(Ri, -L / 2.0), arc(Ri, L / 2.0)
    # Outer surface.
    for i in range(n):
        mesh.add_face(ox0[i], ox0[i + 1], ox1[i + 1])
        mesh.add_face(ox0[i], ox1[i + 1], ox1[i])
    # Inner surface (reversed).
    for i in range(n):
        mesh.add_face(ix0[i], ix1[i + 1], ix0[i + 1])
        mesh.add_face(ix0[i], ix1[i], ix1[i + 1])
    # Top rim strips at the two open edges (y=+/-R).
    for a_end, b_end in ((0, 0), (n, n)):
        mesh.add_face(ox0[a_end], ix0[a_end], ix1[b_end])
        mesh.add_face(ox0[a_end], ix1[b_end], ox1[b_end])
    # Solid semicircular end plates (fan from centerline).
    for xarc in (ox0, ox1):
        c = mesh.add_vertex(mesh.vertices[xarc[0]][0], 0.0, cz)
        for i in range(n):
            mesh.add_face(c, xarc[i], xarc[i + 1])
    return mesh


def _build_tub_shell(r: ResolvedIndustrialMineCartConfig, seat: tuple[float, float, float]):
    if r.tub_form == "ubucket":
        m = _build_ubucket_mesh(r, "tub_shell")
    else:
        m = _build_vertical_tub_mesh(r, "tub_shell")
    m.translate(-seat[0], -seat[1], -seat[2])
    return mesh_from_geometry(m, "tub_shell_mesh")


# --------------------------------------------------------------------------- #
# Tub decoration: strap bands + rivets (Rule 4 host-conformal, derive order
# ③ form -> ⑤ scale -> ④ decoration).
# --------------------------------------------------------------------------- #


def _rivet_row(points: list[tuple[float, float, float]], radius: float = 0.012) -> MeshGeometry:
    merged = MeshGeometry()
    for x, y, z in points:
        dome = SphereGeometry(radius, width_segments=8, height_segments=6)
        dome.translate(x, y, z)
        merged.merge(dome)
    return merged


def _band_z_centers(r: ResolvedIndustrialMineCartConfig) -> list[float]:
    n = r.strap_band_count
    lo = TUB_BASE_Z + 0.10
    # Bands must stay on the wall, so the top band clears the LOWEST rim station
    # (the saddle dip), not the rim ends.
    hi = r.rim_min_z - 0.16
    if n == 1:
        return [(lo + hi) / 2.0]
    return [lo + (hi - lo) * i / (n - 1) for i in range(n)]


def _band_x_centers(r: ResolvedIndustrialMineCartConfig) -> list[float]:
    n = r.strap_band_count
    L = 1.20 * r.tub_len_scale
    lo, hi = -0.32 * L, 0.32 * L
    if n == 1:
        return [0.0]
    return [lo + (hi - lo) * i / (n - 1) for i in range(n)]


def _emit_bands_and_rivets(part, r: ResolvedIndustrialMineCartConfig,
                           seat: tuple[float, float, float]) -> None:
    sx, sy, sz = seat
    proud = 0.018
    bw = 0.055

    if r.tub_form == "ubucket":
        R = 0.40 * r.tub_len_scale
        cz = TUB_BASE_Z + R
        n_arc = 12
        angs = [(-math.pi / 2.0) + math.pi * i / n_arc for i in range(n_arc + 1)]
        for bi, xc in enumerate(_band_x_centers(r)):
            band = MeshGeometry()
            def arc(radius: float, x: float):
                return [band.add_vertex(x, radius * math.sin(a), cz - radius * math.cos(a)) for a in angs]
            olo, ohi = arc(R + proud, xc - bw / 2), arc(R + proud, xc + bw / 2)
            ilo, ihi = arc(R - 0.02, xc - bw / 2), arc(R - 0.02, xc + bw / 2)
            for i in range(n_arc):
                band.add_face(olo[i], olo[i + 1], ohi[i + 1]); band.add_face(olo[i], ohi[i + 1], ohi[i])
                band.add_face(ilo[i], ihi[i + 1], ilo[i + 1]); band.add_face(ilo[i], ihi[i], ihi[i + 1])
                # radial edge walls tying outer<->inner (closed box-section ring,
                # so the band is one connected solid straddling the shell wall).
                band.add_face(olo[i], ilo[i], ilo[i + 1]); band.add_face(olo[i], ilo[i + 1], olo[i + 1])
                band.add_face(ohi[i], ihi[i + 1], ihi[i]); band.add_face(ohi[i], ohi[i + 1], ihi[i + 1])
            # arc-end caps.
            for a_end in (0, n_arc):
                band.add_face(olo[a_end], ohi[a_end], ihi[a_end]); band.add_face(olo[a_end], ihi[a_end], ilo[a_end])
            band.translate(-sx, -sy, -sz)
            part.visual(mesh_from_geometry(band, f"strap_band_mesh_{bi}"),
                        material="iron", name=f"strap_band_{bi}", material_class_id="metal.steel_bare")
            rivets = []
            for a in angs[1:-1:2]:
                rivets.append((xc, (R + proud) * math.sin(a) - sy, cz - (R + proud) * math.cos(a) - sz))
            part.visual(mesh_from_geometry(_rivet_row([(x - sx, y, z) for (x, y, z) in rivets], 0.011),
                        f"band_rivets_mesh_{bi}"), material="iron", name=f"band_rivets_{bi}", material_class_id="metal.steel_bare")
        # Rim rivets along the two open top edges.
        rim = []
        for x in [(-0.32 + 0.08 * i) * (1.20 * r.tub_len_scale) for i in range(9)]:
            rim.append((x - sx, R - sy, cz - sz))
            rim.append((x - sx, -R - sy, cz - sz))
        part.visual(mesh_from_geometry(_rivet_row(rim, 0.011), "rim_rivets_mesh"),
                    material="iron", name="rim_rivets", material_class_id="metal.steel_bare")
        return

    # Vertical-wall forms: horizontal hoop bands at z centers.
    for bi, zc in enumerate(_band_z_centers(r)):
        length, width, corner = _tub_profile(r, zc)
        band = MeshGeometry()
        z_lo, z_hi = zc - bw / 2, zc + bw / 2
        o_lo = _rect_loop(band, length + 2 * proud, width + 2 * proud, corner + proud, z_lo)
        o_hi = _rect_loop(band, length + 2 * proud, width + 2 * proud, corner + proud, z_hi)
        i_lo = _rect_loop(band, length - 0.012, width - 0.012, max(0.01, corner - 0.006), z_lo)
        i_hi = _rect_loop(band, length - 0.012, width - 0.012, max(0.01, corner - 0.006), z_hi)
        _ring(band, o_lo, o_hi)
        _ring(band, i_hi, i_lo)
        _ring(band, o_hi, i_hi)
        _ring(band, i_lo, o_lo)
        band.translate(-sx, -sy, -sz)
        part.visual(mesh_from_geometry(band, f"strap_band_mesh_{bi}"),
                    material="iron", name=f"strap_band_{bi}", material_class_id="metal.steel_bare")
        hy = width / 2 + proud
        hx = length / 2 + proud
        rivets = []
        for x in [(-0.4 + 0.1 * i) * length for i in range(9)]:
            rivets.append((x, hy, zc)); rivets.append((x, -hy, zc))
        for y in (-0.20 * width, 0.0, 0.20 * width):
            rivets.append((hx, y, zc)); rivets.append((-hx, y, zc))
        part.visual(mesh_from_geometry(_rivet_row([(x - sx, y - sy, z - sz) for (x, y, z) in rivets], 0.011),
                    f"band_rivets_mesh_{bi}"), material="iron", name=f"band_rivets_{bi}", material_class_id="metal.steel_bare")

    # Rim rivets along the top edge. They are sampled from the realized rim ring and
    # inset half a wall thickness, so a saddle rim carries its stud row down into the
    # dip and up over the ends with it and never floats off the shell (Rule 4).
    rim = []
    ring = _rim_ring(r)
    for k in range(0, len(ring), 5):
        x, y, z = ring[k]
        norm = math.hypot(x, y) or 1.0
        inset = 0.5 * WALL_T / norm
        rim.append((x * (1.0 - inset), y * (1.0 - inset), z - 0.006))
    part.visual(mesh_from_geometry(_rivet_row([(x - sx, y - sy, z - sz) for (x, y, z) in rim], 0.011),
                "rim_rivets_mesh"), material="iron", name="rim_rivets", material_class_id="metal.steel_bare")


# --------------------------------------------------------------------------- #
# Slot E -- track (new root when present) + its dependent track_shape slot
# --------------------------------------------------------------------------- #


def _track_centreline(r: ResolvedIndustrialMineCartConfig,
                      samples: int) -> list[tuple[float, float, float]]:
    """``samples`` stations (x, y, yaw) evenly spaced along the track centreline.

    Straight is the source layout. Curved lays the same centreline on an arc whose
    midpoint is under the cart, so the cart itself never moves: it sits at the
    tangent point and the track sweeps away from it in both directions."""
    half = 0.5 * r.track_len
    out: list[tuple[float, float, float]] = []
    for i in range(samples):
        s = -half + r.track_len * i / max(samples - 1, 1)
        if r.track_radius <= 0.0:
            out.append((s, 0.0, 0.0))
        else:
            th = s / r.track_radius
            out.append((r.track_radius * math.sin(th),
                        r.track_radius * (1.0 - math.cos(th)),
                        th))
    return out


def _offset_line(stations: list[tuple[float, float, float]],
                 lateral: float) -> list[tuple[float, float, float]]:
    """Shift a centreline sideways by ``lateral`` along each station's normal."""
    return [(x - lateral * math.sin(yaw), y + lateral * math.cos(yaw), yaw)
            for (x, y, yaw) in stations]


def _swept_bar_mesh(path: list[tuple[float, float, float]], *, width: float,
                    height: float, z_bottom: float) -> MeshGeometry:
    """Rectangular bar of ``width`` x ``height`` swept along ``path``.

    One mesh per rail layer keeps a curved rail a single continuous solid instead
    of a chain of dozens of Box visuals (compile budget + collision breadth)."""
    mesh = MeshGeometry()
    rings: list[list[int]] = []
    for (x, y, yaw) in path:
        nx, ny = -math.sin(yaw), math.cos(yaw)
        ax, ay = x - 0.5 * width * nx, y - 0.5 * width * ny
        bx, by = x + 0.5 * width * nx, y + 0.5 * width * ny
        rings.append([
            mesh.add_vertex(ax, ay, z_bottom),
            mesh.add_vertex(bx, by, z_bottom),
            mesh.add_vertex(bx, by, z_bottom + height),
            mesh.add_vertex(ax, ay, z_bottom + height),
        ])
    for k in range(len(rings) - 1):
        lo, hi = rings[k], rings[k + 1]
        for i in range(4):
            j = (i + 1) % 4
            mesh.add_face(lo[i], lo[j], hi[j])
            mesh.add_face(lo[i], hi[j], hi[i])
    for loop, reverse in ((rings[0], True), (rings[-1], False)):
        _cap(mesh, loop, reverse=reverse)
    return mesh


def _build_track(ctx: ModuleBuildContext) -> ModuleBuild:
    model = ctx.model
    r: ResolvedIndustrialMineCartConfig = ctx.config  # type: ignore[assignment]
    chassis = model.get_part("chassis")
    if r.track_module == "none":
        # No track: the chassis stays the root and the wheels ride the ground plane.
        return ModuleBuild(module_name="none", parts_emitted=[],
                           interfaces={"downstream": _chassis_downstream()})

    prof = TRACK_PROFILES[r.track_module]
    track = model.part("rail_track")
    tie_x, tie_y, tie_z = prof["tie"]

    n_ties = max(3, int(round(r.track_len / prof["tie_pitch"])) + 1)
    for i, (x, y, yaw) in enumerate(_track_centreline(r, n_ties)):
        track.visual(Box((tie_x, tie_y, tie_z)),
                     origin=Origin(xyz=(x, y, 0.5 * tie_z), rpy=(0.0, 0.0, yaw)),
                     material=prof["tie_material"], name=f"sleeper_{i}", material_class_id="wood.rustic_weathered")

    rail_samples = 2 if r.track_radius <= 0.0 else 15
    centre = _track_centreline(r, rail_samples)
    for j, side in enumerate((1.0, -1.0)):
        line = _offset_line(centre, side * TRACK_GAUGE_Y)
        z = tie_z
        # Every layer is sunk `lap` into the one below for connectivity but keeps its
        # nominal TOP, so the last layer's top is exactly `rail_top` -- the datum the
        # wheel treads are seated on.
        lap = 0.006
        if prof["stringer"] is not None:
            s_w, s_h = prof["stringer"]
            track.visual(mesh_from_geometry(
                _swept_bar_mesh(line, width=s_w, height=s_h + lap, z_bottom=z - lap),
                f"stringer_mesh_{j}"), material=prof["tie_material"], name=f"stringer_{j}", material_class_id="wood.rustic_weathered")
            z += s_h
        names = RAIL_LAYER_NAMES[len(prof["rail_layers"])]
        for k, (w, h) in enumerate(prof["rail_layers"]):
            track.visual(mesh_from_geometry(
                _swept_bar_mesh(line, width=w, height=h + lap, z_bottom=z - lap),
                f"{names[k]}_mesh_{j}"), material="rail", name=f"{names[k]}_{j}", material_class_id="metal.steel_bare")
            z += h

    track.inertial = Inertial.from_geometry(
        Box((r.track_len, tie_y, r.rail_top)), mass=80.0,
        origin=Origin(xyz=(0.0, 0.0, 0.5 * r.rail_top)),
    )
    # The cart rides the track (S12 L250-L258). The prismatic axis is the arc's
    # tangent at the cart, and the travel was sized in resolve_config so the wheels
    # stay on the rail heads over the whole stroke.
    model.articulation(
        "cart_travel", ArticulationType.PRISMATIC, parent=track, child=chassis,
        origin=Origin(xyz=(0.0, 0.0, r.rail_top)), axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=300.0, velocity=1.5,
                                   lower=-r.cart_travel, upper=r.cart_travel),
    )
    return ModuleBuild(module_name=r.track_module, parts_emitted=["rail_track"],
                       internal_articulations=["cart_travel"],
                       interfaces={"downstream": _chassis_downstream()})


# --------------------------------------------------------------------------- #
# Slot A -- chassis (root)
# --------------------------------------------------------------------------- #


CRADLE_RAKE = 0.15          # brace pitch (rad); source rakes them up to the bolster
CRADLE_BRACE_Z0 = 0.565     # nominal cradle height (S1 L228)
CRADLE_BRACE_Z_MIN = 0.42   # below this a raked brace no longer laps the beam/bolster


def _cradle_brace_z(r: ResolvedIndustrialMineCartConfig, sx: float) -> float | None:
    """Height for the cradle-brace pair on the ``sx`` side, or None if the tipping
    tub sweeps through the whole available band.

    The tub rotates about the trunnion, which sits only ~35 mm under its floor, so
    on the discharge side the leading floor corner drops well below the deck. The
    brace is placed under that swept minimum rather than at a fixed height."""
    z_half = 0.25 * math.sin(CRADLE_RAKE) + 0.02 * math.cos(CRADLE_RAKE)
    if r.tip_mechanism == "hoist_lift":
        return CRADLE_BRACE_Z0                      # the skip only ever rises
    pivot = r.tip_pivot
    # Outermost floor corner on the dipping side, in the pivot's frame. A side-tip
    # rotates across Y, so both X pairs see the same (worst) Y-side envelope.
    if r.discharge == "side":
        lateral = _tub_half(r, TUB_BASE_Z)[1] - pivot[1]
    else:
        lateral = sx * _tub_half(r, TUB_BASE_Z)[0] - pivot[0]
    z_rel = TUB_BASE_Z - pivot[2]
    swept = min(
        pivot[2] - lateral * math.sin(q) + z_rel * math.cos(q)
        for q in [r.tip_upper * i / 12.0 for i in range(13)]
    )
    cz = min(CRADLE_BRACE_Z0, swept - z_half - 0.012)
    return cz if cz >= CRADLE_BRACE_Z_MIN else None


def _chassis_downstream() -> InterfaceSpec:
    return InterfaceSpec(
        interface_name="downstream",
        part_name="chassis",
        visual_name="center_plank_0",
        face_side="positive_z",
        anchor_local=(0.0, 0.0, DECK_TOP),
        contact_tol=0.006,
    )


def _build_chassis(ctx: ModuleBuildContext) -> ModuleBuild:
    model = ctx.model
    r: ResolvedIndustrialMineCartConfig = ctx.config  # type: ignore[assignment]
    chassis = model.part("chassis")

    chassis.inertial = Inertial.from_geometry(
        Box((1.7, 1.0, 0.5)), mass=40.0, origin=Origin(xyz=(0.0, 0.0, 0.35)),
    )

    for i, sy in enumerate((1.0, -1.0)):
        chassis.visual(Box((1.56, 0.08, 0.12)), origin=Origin(xyz=(0.0, sy * 0.44, FRAME_Z)),
                       material="frame", name=f"side_frame_beam_{i}", material_class_id="metal.paint_coated")
    for i, sx in enumerate((-1.0, 1.0)):
        chassis.visual(Box((0.08, 0.96, 0.12)), origin=Origin(xyz=(sx * 0.74, 0.0, FRAME_Z)),
                       material="frame", name=f"end_frame_beam_{i}", material_class_id="metal.paint_coated")

    # Center / inter-axle planks (N=3 grows a second plank pair).
    if r.wheelset_count == 3:
        for i, px in enumerate((-0.24, 0.24)):
            chassis.visual(Box((0.16, 0.88, 0.05)), origin=Origin(xyz=(px, 0.0, DECK_TOP + 0.025)),
                           material="frame", name=f"center_plank_{i}", material_class_id="metal.paint_coated")
    else:
        chassis.visual(Box((0.16, 0.88, 0.05)), origin=Origin(xyz=(0.0, 0.0, DECK_TOP - 0.025)),
                       material="frame", name="center_plank_0", material_class_id="metal.paint_coated")

    # Saddle bolsters carrying the tub: span to the side beams (y=+/-0.44) so
    # they self-connect to the frame; top ~0.625, below the tub floor (0.655) and
    # the lowest ubucket wrap-band arc (z~0.637).
    for i, sx in enumerate((-1.0, 1.0)):
        chassis.visual(Box((0.12, 0.92, 0.15)), origin=Origin(xyz=(sx * 0.22, 0.0, 0.55)),
                       material="frame", name=f"saddle_bolster_{i}", material_class_id="metal.paint_coated")
    # Raked cradle braces from the end beams up to the bolsters (S1 L221-L232):
    # the real load path that carries the tub cradle back into the headstocks. The
    # tipping tub's leading floor corner sweeps DOWN past the deck, so each pair
    # rides at the height its own side's swept envelope leaves free.
    brace = 0
    for sx in (-1.0, 1.0):
        cz = _cradle_brace_z(r, sx)
        if cz is None:
            continue
        for sy in (-1.0, 1.0):
            chassis.visual(Box((0.50, 0.05, 0.04)),
                           origin=Origin(xyz=(sx * 0.49, sy * 0.20, cz),
                                         rpy=(0.0, sx * CRADLE_RAKE, 0.0)),
                           material="frame", name=f"cradle_brace_{brace}", material_class_id="metal.paint_coated")
            brace += 1
    # Axleboxes per wheelset: pedestals that span from just under the axle
    # journal (z=axle_z) up into the side frame beam (z 0.38-0.50), so they stay
    # connected to the frame for the full wheel-radius range (incl. the smaller
    # 3-axle wheels). Height tracks axle_z rather than being a fixed box.
    box_idx = 0
    box_top = FRAME_Z + 0.02  # reaches into the side beam
    for ax in r.axle_positions:
        box_bottom = r.axle_z - 0.03
        box_h = box_top - box_bottom
        box_cz = 0.5 * (box_bottom + box_top)
        for sy in (1.0, -1.0):
            chassis.visual(Box((0.12, 0.06, box_h)), origin=Origin(xyz=(ax, sy * 0.445, box_cz)),
                           material="iron", name=f"axlebox_{box_idx}", material_class_id="metal.cast_iron_bare")
            box_idx += 1
    # Dumb buffers on both headstocks.
    buf = 0
    for sx in (-1.0, 1.0):
        for sy in (1.0, -1.0):
            chassis.visual(Box((0.13, 0.12, 0.13)), origin=Origin(xyz=(sx * 0.835, sy * 0.30, FRAME_Z)),
                           material="frame", name=f"buffer_block_{buf}", material_class_id="metal.cast_iron_bare")
            chassis.visual(Box((0.03, 0.15, 0.15)), origin=Origin(xyz=(sx * 0.915, sy * 0.30, FRAME_Z)),
                           material="frame", name=f"buffer_head_{buf}", material_class_id="metal.cast_iron_bare")
            buf += 1

    return ModuleBuild(module_name="frame", parts_emitted=["chassis"],
                       interfaces={"downstream": _chassis_downstream()})


# --------------------------------------------------------------------------- #
# Slot B -- tip_mechanism (emits tub + defining joint + chassis mount hardware)
# --------------------------------------------------------------------------- #


def _emit_tub_common(tub, r, seat) -> None:
    tub.visual(_build_tub_shell(r, seat), material="body", name="tub_shell", material_class_id="metal.paint_coated")
    _emit_bands_and_rivets(tub, r, seat)
    tub.inertial = Inertial.from_geometry(
        Box((1.3 * r.tub_len_scale, 0.9 * r.tub_len_scale, (r.tub_top_z - TUB_BASE_Z) + 0.1)),
        mass=10.0,
        origin=Origin(xyz=(0.0 - seat[0], 0.0 - seat[1],
                           (TUB_BASE_Z + 0.5 * (r.tub_top_z - TUB_BASE_Z)) - seat[2])),
    )


def _catch_lug_span(r: ResolvedIndustrialMineCartConfig) -> tuple[float, float]:
    """(inner_face, outer_face) of the catch lug along the discharge axis.

    The lug bites 30 mm into the shell wall and stands proud of it, but it is
    clamped to stop short of the hoop plate: a full-length ``ubucket`` otherwise
    pushes its lug past the headstock and straight into the stirrup arch (and, on a
    hoist, drags it through the crown on the way up)."""
    axis = 1 if r.discharge == "side" else 0
    half = _tub_half(r, r.latch_engage_z)[axis]
    proud = CATCH_LUG_HALF[axis]
    clear_of_hoop = abs(r.hoop_plane) - 0.5 * HOOP_PLATE_T - 0.008
    outer = -min(half + 0.02 + proud, clear_of_hoop)
    inner = -max(half - 0.03, -outer - 0.16)
    return (inner, outer)


def _emit_catch_lug(tub, r, seat) -> tuple[float, float, float]:
    """Catch lug on the discharge-facing wall (world), returns its world center.

    Its height is the resolved ``latch_engage_z``, so the release toe/bolt really
    holds the lug at rest instead of hanging past it."""
    sx, sy, sz = seat
    z = r.latch_engage_z
    inner, outer = _catch_lug_span(r)
    length = max(0.06, inner - outer)
    centre = 0.5 * (inner + outer)
    if r.discharge == "side":
        world = (0.0, centre, z)
        dims = (2 * CATCH_LUG_HALF[0], length, 2 * CATCH_LUG_HALF[2])
    else:
        world = (centre, 0.0, z)
        dims = (length, 2 * CATCH_LUG_HALF[1], 2 * CATCH_LUG_HALF[2])
    tub.visual(Box(dims),
               origin=Origin(xyz=(world[0] - sx, world[1] - sy, world[2] - sz)),
               material="iron", name="catch_lug", material_class_id="metal.cast_iron_bare")
    return world


def _build_end_or_side_tip(ctx: ModuleBuildContext) -> ModuleBuild:
    model = ctx.model
    r: ResolvedIndustrialMineCartConfig = ctx.config  # type: ignore[assignment]
    chassis = model.get_part("chassis")
    pivot = r.tip_pivot
    seat = pivot

    # --- chassis-side trunnion hardware ---
    if r.discharge == "side":
        chassis.visual(Box((1.20, 0.06, 0.06)), origin=Origin(xyz=(0.0, 0.44, 0.528)),
                       material="frame", name="trunnion_bolster", material_class_id="metal.paint_coated")
        for i, sx in enumerate((-1.0, 1.0)):
            chassis.visual(Box((0.04, 0.07, 0.095)), origin=Origin(xyz=(sx * 0.40, 0.44, 0.5975)),
                           material="iron", name=f"trunnion_bracket_{i}", material_class_id="metal.cast_iron_bare")
        chassis.visual(Cylinder(radius=0.022, length=0.80),
                       origin=Origin(xyz=pivot, rpy=(0.0, math.pi / 2.0, 0.0)),
                       material="iron", name="tip_pivot_pin", material_class_id="metal.steel_bare")
        tip_axis = (-1.0, 0.0, 0.0)
    else:
        # Bolster raised to clear the tallest scaled +X wheel (bottom 0.515 above
        # 2*wheel_radius<=0.504), tied down to the side beams by gusset posts that
        # stand outboard of the wheel (y=+/-0.44) so nothing fouls the wheel.
        chassis.visual(Box((0.10, 0.96, 0.06)), origin=Origin(xyz=(pivot[0], 0.0, 0.545)),
                       material="frame", name="trunnion_bolster", material_class_id="metal.paint_coated")
        for i, sy in enumerate((1.0, -1.0)):
            chassis.visual(Box((0.08, 0.07, 0.11)), origin=Origin(xyz=(pivot[0], sy * 0.44, 0.50)),
                           material="frame", name=f"trunnion_gusset_{i}", material_class_id="metal.paint_coated")
        for i, sy in enumerate((1.0, -1.0)):
            chassis.visual(Box((0.07, 0.04, 0.11)), origin=Origin(xyz=(pivot[0], sy * 0.33, 0.60)),
                           material="iron", name=f"trunnion_bracket_{i}", material_class_id="metal.cast_iron_bare")
        chassis.visual(Cylinder(radius=0.022, length=0.72),
                       origin=Origin(xyz=pivot, rpy=(math.pi / 2.0, 0.0, 0.0)),
                       material="iron", name="tip_pivot_pin", material_class_id="metal.steel_bare")
        tip_axis = (0.0, 1.0, 0.0)

    # --- tub part ---
    tub = model.part("tub")
    _emit_tub_common(tub, r, seat)

    # Pivot lugs: sized/placed so the tip axis passes through each lug AABB (tub-side
    # origin honesty) while the inboard face overlaps the shell wall (connectivity).
    # seat==pivot, so tub-local (0,0,0) is the pivot; lug local frame straddles it.
    if r.discharge == "side":
        for i, sx in enumerate((-1.0, 1.0)):
            tub.visual(Box((0.10, 0.16, 0.14)), origin=Origin(xyz=(sx * 0.25, -0.065, 0.0)),
                       material="iron", name=f"pivot_lug_{i}", material_class_id="metal.cast_iron_bare")
    elif r.tub_form == "ubucket":
        # The narrow half-pipe only has material near its centerline low down, so
        # the lugs hang near y=0 to bridge the trough bottom down to the pin.
        for i, sy in enumerate((1.0, -1.0)):
            tub.visual(Box((0.12, 0.10, 0.14)), origin=Origin(xyz=(0.0, sy * 0.07, 0.0)),
                       material="iron", name=f"pivot_lug_{i}", material_class_id="metal.cast_iron_bare")
    else:
        for i, sy in enumerate((1.0, -1.0)):
            tub.visual(Box((0.10, 0.06, 0.14)), origin=Origin(xyz=(0.0, sy * 0.28, 0.0)),
                       material="iron", name=f"pivot_lug_{i}", material_class_id="metal.cast_iron_bare")

    _emit_catch_lug(tub, r, seat)

    model.articulation(
        "tub_tip", ArticulationType.REVOLUTE, parent=chassis, child=tub,
        origin=Origin(xyz=pivot), axis=tip_axis,
        motion_limits=MotionLimits(effort=400.0, velocity=0.8, lower=0.0, upper=r.tip_upper),
    )

    parts = ["tub"]
    joints = ["tub_tip"]
    if r.has_tailgate:
        _emit_tailgate(model, r, tub, seat)
        parts.append("end_door")
        joints.append("door_hinge")

    return ModuleBuild(module_name=r.tip_mechanism, parts_emitted=parts,
                       internal_articulations=joints,
                       interfaces={"downstream": _chassis_downstream()})


def _build_hoist_lift(ctx: ModuleBuildContext) -> ModuleBuild:
    model = ctx.model
    r: ResolvedIndustrialMineCartConfig = ctx.config  # type: ignore[assignment]
    chassis = model.get_part("chassis")
    seat = (0.0, 0.0, 0.0)  # tub authored in world; part frame = world (prismatic)

    col_x = 0.45
    col_y = 0.64  # outboard of the widest tub rim (chaldron half-width ~0.58)
    # One transverse bearer carries both columns at its ends (S6 L262-L269 ties the
    # columns together; here the tie sits low, under the tub floor, where the rising
    # skip can never reach it). Without it the columns read as two loose poles
    # floating outboard of the frame. It clears the tallest scaled wheel (top
    # 2*0.252) and is posted down onto both side beams, outboard of the wheel faces.
    bearer_z = 0.545
    chassis.visual(Box((0.10, 2 * col_y + 0.10, 0.06)),
                   origin=Origin(xyz=(col_x, 0.0, bearer_z)),
                   material="frame", name="guide_bearer", material_class_id="metal.paint_coated")
    for i, sy in enumerate((1.0, -1.0)):
        chassis.visual(Box((0.10, 0.06, 0.15)),
                       origin=Origin(xyz=(col_x, sy * 0.455, 0.50)),
                       material="frame", name=f"guide_bearer_post_{i}", material_class_id="metal.paint_coated")
    col_bot = bearer_z - 0.015
    # Columns run tall enough that the slider (rest top ~0.80) stays on the column
    # over the full hoist travel, and no taller: crown = slider top + travel + head.
    col_top = 0.80 + r.lift_travel + 0.09
    col_h = col_top - col_bot
    column_radius = 0.028
    for i, sy in enumerate((1.0, -1.0)):
        chassis.visual(Cylinder(radius=column_radius, length=col_h),
                       origin=Origin(xyz=(col_x, sy * col_y, col_bot + col_h / 2)),
                       material="iron", name=f"guide_column_{i}", material_class_id="metal.steel_bare")
        chassis.visual(Box((0.09, 0.09, 0.05)),
                       origin=Origin(xyz=(col_x, sy * col_y, col_top - 0.02)),
                       material="iron", name=f"guide_head_cap_{i}", material_class_id="metal.cast_iron_bare")
        chassis.visual(Box((0.08, 0.05, 0.10)),
                       origin=Origin(xyz=(col_x, sy * col_y, col_bot + 0.06)),
                       material="iron", name=f"guide_base_bracket_{i}", material_class_id="metal.cast_iron_bare")

    tub = model.part("tub")
    _emit_tub_common(tub, r, seat)
    # Guide shoes bridge from the tub wall out to each column. Each shoe is a
    # four-sided collar with a real through-opening around the column, rather than
    # the old solid block that made the guide rod pass through moving material.
    # The inboard edge is still derived from the actual shell half-width so narrow
    # forms remain connected to the tub over the full lift stroke.
    slider_z = 0.72
    shell_hy = _tub_half(r, slider_z)[1]
    inner_y = shell_hy - 0.03           # bite into the shell wall (connectivity)
    shoe_outer_y = col_y + 0.06
    shoe_x = 0.12
    shoe_z = 0.16
    bore_half = column_radius + 0.0008  # visible bore; <=1 mm support gap per side
    bore_lo = col_y - bore_half
    bore_hi = col_y + bore_half
    cheek_x = 0.5 * (shoe_x - 2.0 * bore_half)
    for i, sy in enumerate((1.0, -1.0)):
        # Radial inner/outer bridges plus two longitudinal cheeks form one
        # connected rectangular collar. The empty center is the guide-column bore.
        for suffix, y0, y1 in (
            ("inner", inner_y, bore_lo),
            ("outer", bore_hi, shoe_outer_y),
        ):
            tub.visual(
                Box((shoe_x, y1 - y0, shoe_z)),
                origin=Origin(xyz=(col_x, sy * 0.5 * (y0 + y1), slider_z)),
                material="iron",
                name=f"slider_block_{i}_{suffix}", material_class_id="metal.cast_iron_bare",
            )
        for cheek in (-1.0, 1.0):
            tub.visual(
                Box((cheek_x, 2.0 * bore_half, shoe_z)),
                origin=Origin(
                    xyz=(
                        col_x + cheek * (0.5 * shoe_x - 0.5 * cheek_x),
                        sy * col_y,
                        slider_z,
                    )
                ),
                material="iron",
                name=f"slider_block_{i}_cheek_{0 if cheek < 0.0 else 1}", material_class_id="metal.cast_iron_bare",
            )
    _emit_catch_lug(tub, r, seat)

    model.articulation(
        "tub_lift", ArticulationType.PRISMATIC, parent=chassis, child=tub,
        origin=Origin(xyz=(0.0, 0.0, 0.0)), axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=4000.0, velocity=0.3, lower=0.0, upper=r.lift_travel),
    )
    return ModuleBuild(module_name="hoist_lift", parts_emitted=["tub"],
                       internal_articulations=["tub_lift"],
                       interfaces={"downstream": _chassis_downstream()})


def _emit_tailgate(model, r: ResolvedIndustrialMineCartConfig, tub, seat) -> None:
    """Hinged end-discharge door hung from the +X top rim (child of tub). The door
    panel hangs just outside the (uncut) end wall and swings out to discharge."""
    sx, sy, sz = seat
    hx = _tub_half(r, r.tub_top_z)[0]  # +X rim half-length (widest station)
    hinge_world = (hx + 0.01, 0.0, r.tub_top_z - 0.03)
    door = model.part("end_door")
    door_h, door_w, door_t = 0.42, 0.56, 0.03
    # The proud strap bands (+X face out to hx+0.018) and their rivets (out to
    # hx+0.029) stand off the flat +X end wall of box/trapezoid tubs. The door
    # panel must clear them, so it hangs at a fixed +X gap from the hinge; the
    # hinge knuckles are lengthened along +X to bridge the rim (allowed shell
    # overlap) out to the panel, keeping the end_door a single connected part.
    panel_gap = 0.045
    # Door local: hinge/pin at part origin; panel hangs straight down at +X gap.
    door.visual(Box((door_t, door_w, door_h)),
                origin=Origin(xyz=(panel_gap + door_t / 2, 0.0, -door_h / 2)),
                material="body", name="door_panel", material_class_id="metal.paint_coated")
    knuckle_len = panel_gap + 0.055
    for i, syb in enumerate((1.0, -1.0)):
        door.visual(Box((knuckle_len, 0.05, 0.05)),
                    origin=Origin(xyz=(0.5 * knuckle_len - 0.02, syb * 0.20, 0.0)),
                    material="iron", name=f"door_hinge_knuckle_{i}", material_class_id="metal.cast_iron_bare")
    door.visual(Cylinder(radius=0.010, length=0.46), origin=Origin(xyz=(-0.01, 0.0, 0.0), rpy=(math.pi / 2, 0, 0)),
                material="iron", name="door_hinge_pin", material_class_id="metal.steel_bare")
    model.articulation(
        "door_hinge", ArticulationType.REVOLUTE, parent=tub, child=door,
        origin=Origin(xyz=(hinge_world[0] - sx, hinge_world[1] - sy, hinge_world[2] - sz)),
        axis=(0.0, -1.0, 0.0),  # positive q swings the panel bottom out (+X) to discharge
        motion_limits=MotionLimits(effort=100.0, velocity=1.5, lower=0.0, upper=1.2),
    )


# --------------------------------------------------------------------------- #
# Slot C -- latch (release mechanism + end hoop)
# --------------------------------------------------------------------------- #


def _arch_plate_mesh(*, half_span: float, leg_w: float, v_bot: float, v_top: float,
                     thickness: float, normal_axis: str, plane_at: float,
                     arc_segments: int = 12) -> MeshGeometry:
    """One flat iron stirrup plate: two straight legs closed by a rolled crown.

    This is the sources' hoop primitive (S1 ``build_hoop`` L129-L147, S10 L133-L151:
    a rounded-top outer rectangle minus a rounded-top inner rectangle, extruded
    35 mm). ``normal_axis='x'`` gives the -X end hoop (plate lateral span along Y),
    ``'y'`` gives the -Y side hoop (lateral span along X). Local (u, v) = (lateral,
    height); the slab straddles ``plane_at`` on the normal axis."""
    r_out = half_span
    r_in = max(0.02, half_span - leg_w)
    v_c = v_top - r_out
    n = max(4, int(arc_segments))

    def path(radius: float) -> list[tuple[float, float]]:
        pts = [(radius, v_bot)]
        for i in range(n + 1):
            a = math.pi * i / n
            pts.append((radius * math.cos(a), v_c + radius * math.sin(a)))
        pts.append((-radius, v_bot))
        return pts

    outer2d = path(r_out)
    inner2d = path(r_in)
    half_t = 0.5 * thickness

    mesh = MeshGeometry()

    def add(u: float, v: float, sign: float) -> int:
        if normal_axis == "x":
            return mesh.add_vertex(plane_at + sign * half_t, u, v)
        return mesh.add_vertex(u, plane_at + sign * half_t, v)

    o_lo = [add(u, v, -1.0) for (u, v) in outer2d]
    o_hi = [add(u, v, +1.0) for (u, v) in outer2d]
    i_lo = [add(u, v, -1.0) for (u, v) in inner2d]
    i_hi = [add(u, v, +1.0) for (u, v) in inner2d]

    m = len(outer2d)
    for k in range(m - 1):
        # Two plate faces.
        mesh.add_face(o_hi[k], i_hi[k], i_hi[k + 1])
        mesh.add_face(o_hi[k], i_hi[k + 1], o_hi[k + 1])
        mesh.add_face(o_lo[k], i_lo[k + 1], i_lo[k])
        mesh.add_face(o_lo[k], o_lo[k + 1], i_lo[k + 1])
        # Outer and inner edge walls.
        mesh.add_face(o_lo[k], o_hi[k], o_hi[k + 1])
        mesh.add_face(o_lo[k], o_hi[k + 1], o_lo[k + 1])
        mesh.add_face(i_lo[k], i_hi[k + 1], i_hi[k])
        mesh.add_face(i_lo[k], i_lo[k + 1], i_hi[k + 1])
    # Foot caps at both leg bottoms.
    for k in (0, m - 1):
        mesh.add_face(o_lo[k], o_hi[k], i_hi[k])
        mesh.add_face(o_lo[k], i_hi[k], i_lo[k])
    return mesh


def _emit_hoop(chassis, r: ResolvedIndustrialMineCartConfig) -> tuple[float, float, float]:
    """Raised end/side stirrup hoop (identity feature), built as the sources' flat
    arch plate and standing on the frame beam. Returns the latch hinge pivot."""
    half_span, v_bot, v_top = r.hoop_half_span, r.hoop_foot_z, r.hoop_top
    normal_axis = "y" if r.discharge == "side" else "x"
    chassis.visual(
        mesh_from_geometry(
            _arch_plate_mesh(half_span=half_span, leg_w=HOOP_LEG_W, v_bot=v_bot, v_top=v_top,
                             thickness=HOOP_PLATE_T, normal_axis=normal_axis,
                             plane_at=r.hoop_plane),
            "latch_hoop_mesh"),
        material="iron", name="latch_hoop", material_class_id="metal.cast_iron_bare")

    if r.discharge == "side":
        # The side plate stands outboard of the side beam, so cantilever feet carry
        # its legs back onto the beam (S10 L305-L311 hoop_mount_{i}).
        foot_inner = -0.44
        foot_outer = r.hoop_plane - 0.02
        for i, sx in enumerate((-1.0, 1.0)):
            chassis.visual(Box((0.16, abs(foot_outer - foot_inner), 0.10)),
                           origin=Origin(xyz=(sx * 0.15, 0.5 * (foot_inner + foot_outer), 0.45)),
                           material="frame", name=f"hoop_mount_{i}", material_class_id="metal.paint_coated")
    return r.latch_pivot


def _emit_latch_mount(chassis, r: ResolvedIndustrialMineCartConfig, name: str) -> None:
    """Mount plate bolted to the hoop crown, bringing the latch hardware down to
    ``latch_pivot`` (S1 L295-L300)."""
    v_top = r.hoop_top
    pz = r.latch_pivot[2]
    height = max(0.10, (v_top - 0.02) - (pz - 0.04))
    cz = 0.5 * ((pz - 0.04) + (v_top - 0.02))
    if r.discharge == "side":
        chassis.visual(Box((0.10, 0.024, height)),
                       origin=Origin(xyz=(0.0, r.hoop_plane - 0.006, cz)),
                       material="iron", name=name, material_class_id="metal.cast_iron_bare")
    else:
        chassis.visual(Box((0.024, 0.10, height)),
                       origin=Origin(xyz=(r.hoop_plane - 0.006, 0.0, cz)),
                       material="iron", name=name, material_class_id="metal.cast_iron_bare")


def _release_reach(r: ResolvedIndustrialMineCartConfig, from_plane: float) -> float:
    """Length the toe/bolt must span from ``from_plane`` to bite the catch lug.

    The lug rides the shell wall, so its stand-off moves with ``tub_form`` and the
    continuous scales; the release member is sized from that datum instead of a
    fixed length that would either float short or spear the tub."""
    return max(0.06, _catch_lug_span(r)[1] + 0.012 - from_plane)


def _build_gravity_hook(ctx: ModuleBuildContext) -> ModuleBuild:
    model = ctx.model
    r: ResolvedIndustrialMineCartConfig = ctx.config  # type: ignore[assignment]
    chassis = model.get_part("chassis")
    pivot = _emit_hoop(chassis, r)
    _emit_latch_mount(chassis, r, "latch_mount_plate")

    drop = r.latch_pivot[2] - r.latch_engage_z
    bar_h = drop + 0.04
    latch = model.part("latch_hook")
    latch.visual(Box((0.05, 0.05, bar_h)), origin=Origin(xyz=(0.0, 0.0, -0.5 * bar_h)),
                 material="iron", name="hook_bar", material_class_id="metal.cast_iron_bare")

    if r.discharge == "side":
        chassis.visual(Cylinder(radius=0.014, length=0.30),
                       origin=Origin(xyz=pivot, rpy=(0.0, math.pi / 2, 0.0)),
                       material="iron", name="latch_pin", material_class_id="metal.steel_bare")
        for i, sx in enumerate((-1.0, 1.0)):
            chassis.visual(Box((0.03, 0.05, 0.09)),
                           origin=Origin(xyz=(sx * 0.05, pivot[1], pivot[2])),
                           material="iron", name=f"latch_hinge_ear_{i}", material_class_id="metal.cast_iron_bare")
        hook_axis = (-1.0, 0.0, 0.0)
        reach = _release_reach(r, pivot[1] + 0.015)
        latch.visual(Box((0.05, reach, 0.04)),
                     origin=Origin(xyz=(0.0, 0.015 + 0.5 * reach, -drop)),
                     material="iron", name="latch_toe", material_class_id="metal.cast_iron_bare")
    else:
        chassis.visual(Cylinder(radius=0.014, length=0.30),
                       origin=Origin(xyz=pivot, rpy=(math.pi / 2, 0.0, 0.0)),
                       material="iron", name="latch_pin", material_class_id="metal.steel_bare")
        for i, sy in enumerate((-1.0, 1.0)):
            chassis.visual(Box((0.05, 0.03, 0.09)),
                           origin=Origin(xyz=(pivot[0], sy * 0.05, pivot[2])),
                           material="iron", name=f"latch_hinge_ear_{i}", material_class_id="metal.cast_iron_bare")
        hook_axis = (0.0, 1.0, 0.0)
        reach = _release_reach(r, pivot[0] + 0.015)
        latch.visual(Box((reach, 0.05, 0.04)),
                     origin=Origin(xyz=(0.015 + 0.5 * reach, 0.0, -drop)),
                     material="iron", name="latch_toe", material_class_id="metal.cast_iron_bare")

    model.articulation(
        "latch_pivot", ArticulationType.REVOLUTE, parent=chassis, child=latch,
        origin=Origin(xyz=pivot), axis=hook_axis,
        motion_limits=MotionLimits(effort=20.0, velocity=2.0, lower=0.0, upper=r.latch_range),
    )
    return ModuleBuild(module_name="gravity_hook", parts_emitted=["latch_hook"],
                       internal_articulations=["latch_pivot"],
                       interfaces={"downstream": _chassis_downstream()})


def _build_sliding_bolt(ctx: ModuleBuildContext) -> ModuleBuild:
    model = ctx.model
    r: ResolvedIndustrialMineCartConfig = ctx.config  # type: ignore[assignment]
    chassis = model.get_part("chassis")
    # sliding_bolt is gated to end discharge in resolve_config.
    _emit_hoop(chassis, r)
    bolt_origin = (r.hoop_plane - 0.025, 0.0, r.latch_engage_z)
    # Brackets carrying the keeper up from the end frame beam (S7 L308-L315), so the
    # bolt runs at the catch-lug height instead of hanging off the hoop crown. They
    # FLANK the bolt line rather than sitting on it: a long tub (max-scale ubucket)
    # pushes its catch lug right back to the headstock, and a bracket on the
    # centreline would be speared by it.
    bracket_h = bolt_origin[2] - (FRAME_Z - 0.03)
    for i, sy in enumerate((1.0, -1.0)):
        chassis.visual(Box((0.035, 0.028, bracket_h)),
                       origin=Origin(xyz=(r.hoop_plane, sy * 0.062,
                                          bolt_origin[2] - 0.5 * bracket_h)),
                       material="iron", name=f"bolt_mount_bracket_{i}", material_class_id="metal.cast_iron_bare")
    keeper_len = 0.07
    chassis.visual(Box((keeper_len, 0.11, 0.06)), origin=Origin(xyz=bolt_origin),
                   material="iron", name="guide_keeper", material_class_id="metal.cast_iron_bare")
    for i, sy in enumerate((1.0, -1.0)):
        chassis.visual(Box((0.08, 0.015, 0.08)),
                       origin=Origin(xyz=(bolt_origin[0], sy * 0.045, bolt_origin[2])),
                       material="iron", name=f"bolt_guide_rail_{i}", material_class_id="metal.steel_bare")

    # The bolt must still bite the keeper at full retraction, so its nose reaches
    # at least travel - keeper/2 past the origin as well as into the catch lug.
    reach = max(_release_reach(r, bolt_origin[0] - 0.01),
                r.bolt_travel - 0.5 * keeper_len + 0.02 + 0.01)
    latch = model.part("latch_hook")
    latch.visual(Box((reach, 0.04, 0.035)), origin=Origin(xyz=(-0.01 + 0.5 * reach, 0.0, 0.0)),
                 material="iron", name="bolt_bar", material_class_id="metal.steel_bare")
    latch.visual(Box((0.05, 0.07, 0.06)), origin=Origin(xyz=(-0.02, 0.0, 0.0)),
                 material="iron", name="bolt_head", material_class_id="metal.steel_bare")
    model.articulation(
        "latch_pivot", ArticulationType.PRISMATIC, parent=chassis, child=latch,
        origin=Origin(xyz=bolt_origin), axis=(-1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=20.0, velocity=0.5, lower=0.0, upper=r.bolt_travel),
    )
    return ModuleBuild(module_name="sliding_bolt", parts_emitted=["latch_hook"],
                       internal_articulations=["latch_pivot"],
                       interfaces={"downstream": _chassis_downstream()})


# --------------------------------------------------------------------------- #
# Slot D -- wheels (multiplicity + wheel form)
# --------------------------------------------------------------------------- #


def _wheel_mesh(r: ResolvedIndustrialMineCartConfig):
    R = r.wheel_radius
    rim = WheelRim(inner_radius=R * 0.79, flange_height=0.018, flange_thickness=0.012)
    hub = WheelHub(radius=0.06, width=0.09, cap_style="domed")
    if r.wheel_form == "disc":
        geo = WheelGeometry(R, 0.07, rim=rim, hub=hub,
                            face=WheelFace(dish_depth=0.004, front_inset=0.002, rear_inset=0.002))
        return mesh_from_geometry(geo, "disc_wheel")
    geo = WheelGeometry(R, 0.07, rim=rim, hub=hub,
                        spokes=WheelSpokes(style="straight", count=8, thickness=0.022))
    return mesh_from_geometry(geo, "spoked_wheel")


def _build_wheelsets(ctx: ModuleBuildContext) -> ModuleBuild:
    model = ctx.model
    r: ResolvedIndustrialMineCartConfig = ctx.config  # type: ignore[assignment]
    chassis = model.get_part("chassis")
    wheel_mesh = _wheel_mesh(r)

    parts, joints = [], []
    for i, ax in enumerate(r.axle_positions):
        ws = model.part(f"wheelset_{i}")
        ws.visual(Cylinder(radius=0.032, length=AXLE_LEN), origin=Origin(rpy=(math.pi / 2, 0, 0)),
                  material="wheel", name="axle", material_class_id="metal.steel_bare")
        for j, sy in enumerate((1.0, -1.0)):
            ws.visual(wheel_mesh, origin=Origin(xyz=(0.0, sy * WHEEL_Y, 0.0), rpy=(0.0, 0.0, sy * math.pi / 2)),
                      material="wheel", name=f"wheel_{j}", material_class_id="metal.cast_iron_bare")
            if r.wheel_form == "disc":
                # Solid cast web spanning hub->rim: reads as a disc plate wheel and
                # bridges the WheelGeometry rim/hub mesh components (connectivity).
                ws.visual(Cylinder(radius=r.wheel_radius * 0.80, length=0.05),
                          origin=Origin(xyz=(0.0, sy * WHEEL_Y, 0.0), rpy=(math.pi / 2, 0, 0)),
                          material="wheel", name=f"wheel_web_{j}", material_class_id="metal.cast_iron_bare")
        ws.inertial = Inertial.from_geometry(
            Cylinder(radius=r.wheel_radius, length=AXLE_LEN), mass=6.0,
            origin=Origin(rpy=(math.pi / 2, 0, 0)),
        )
        jn = f"wheelset_{i}_roll"
        model.articulation(
            jn, ArticulationType.CONTINUOUS, parent=chassis, child=ws,
            origin=Origin(xyz=(ax, 0.0, r.axle_z)), axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(effort=150.0, velocity=10.0),
        )
        parts.append(ws.name)
        joints.append(jn)

    return ModuleBuild(module_name=r.wheel_module, parts_emitted=parts,
                       internal_articulations=joints,
                       interfaces={"downstream": _chassis_downstream()})


# --------------------------------------------------------------------------- #
# Factory registries + assembly
# --------------------------------------------------------------------------- #

TIP_FACTORIES = {
    "end_tip": _build_end_or_side_tip,
    "side_tip": _build_end_or_side_tip,
    "hoist_lift": _build_hoist_lift,
}
LATCH_FACTORIES = {
    "gravity_hook": _build_gravity_hook,
    "sliding_bolt": _build_sliding_bolt,
}
WHEEL_FACTORIES = {
    "two_wheelsets": _build_wheelsets,
    "three_wheelsets": _build_wheelsets,
}


TRACK_FACTORIES = {name: _build_track for name in ("none", *TRACK_PROFILES)}


def _slots_for_config(r: ResolvedIndustrialMineCartConfig) -> list[SlotSpec]:
    return [
        SlotSpec(slot_name="chassis", candidates={"frame": _build_chassis}, anchor_choice="frame"),
        # Track runs right after the chassis: when present it becomes the model root
        # and parents the chassis through `cart_travel`.
        SlotSpec(slot_name="track",
                 candidates={r.track_module: TRACK_FACTORIES[r.track_module]},
                 anchor_choice=r.track_module),
        SlotSpec(slot_name="tip_mechanism",
                 candidates={r.tip_mechanism: TIP_FACTORIES[r.tip_mechanism]},
                 anchor_choice=r.tip_mechanism),
        SlotSpec(slot_name="latch",
                 candidates={r.latch_module: LATCH_FACTORIES[r.latch_module]},
                 anchor_choice=r.latch_module),
        SlotSpec(slot_name="wheels",
                 candidates={r.wheel_module: WHEEL_FACTORIES[r.wheel_module]},
                 anchor_choice=r.wheel_module),
    ]


def build_industrial_mine_cart(
    config: IndustrialMineCartConfig,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name="industrial_mine_cart", assets=assets)
    for material_name, rgba in r.palette.items():
        model.material(material_name, rgba=rgba)

    assemble(
        model,
        slots=_slots_for_config(r),
        rng=random.Random(0),
        palette=r.palette,
        config=r,
        seed=0,
        selection_mode="anchor_choices",
    )
    return model


def build_seeded_industrial_mine_cart(seed: int) -> ArticulatedObject:
    return build_industrial_mine_cart(config_from_seed(seed))


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    r = resolve_config(config_from_seed(seed))
    return [
        ("tip_mechanism", r.tip_mechanism),
        ("tub_form", r.tub_form),
        ("rim_profile", r.rim_profile),
        ("latch", r.latch_module),
        ("wheels", r.wheel_module),
        ("wheel_form", r.wheel_form),
        ("track", r.track_module),
        ("track_shape", r.track_shape if r.track_module != "none" else "n/a"),
        ("strap_band_count", f"bands_{r.strap_band_count}"),
        ("tailgate", "end_door" if r.has_tailgate else "none"),
    ]


# --------------------------------------------------------------------------- #
# Author-layer QC
# --------------------------------------------------------------------------- #


def _declare_overlaps(ctx: TestContext, model: ArticulatedObject,
                      r: ResolvedIndustrialMineCartConfig) -> None:
    parts = {p.name for p in model.parts}
    chassis = model.get_part("chassis")

    def _ov(child: str, *, elem_a: str, elem_b: str, reason: str) -> None:
        if child in parts:
            ctx.allow_overlap(chassis, model.get_part(child), elem_a=elem_a, elem_b=elem_b, reason=reason)

    # Tub captured on the trunnion pin. Hoist guide shoes now have real bores, so
    # they need no overlap allowance against the columns.
    if r.tip_mechanism != "hoist_lift":
        # Captured trunnion assembly: the pin / bolster / brackets sit at the pivot
        # right under and between the tub floor, lugs and low wrap-bands. Allow the
        # element-scoped pivot-region overlaps (Rule 2 captured-pivot exception).
        tub = model.get_part("tub")
        tub_near = ["tub_shell", "pivot_lug_0", "pivot_lug_1"]
        tub_near += [v.name for v in tub.visuals
                     if v.name.startswith(("strap_band_", "band_rivets_"))]
        chassis_pivot = ["tip_pivot_pin", "trunnion_bolster",
                         "trunnion_bracket_0", "trunnion_bracket_1"]
        if r.discharge == "side":
            chassis_pivot += ["saddle_bolster_0", "saddle_bolster_1"]
        for ce in chassis_pivot:
            for te in tub_near:
                _ov("tub", elem_a=ce, elem_b=te,
                    reason="Captured trunnion assembly at the tip pivot (pin/bolster/brackets meet the tub floor, lugs and straps).")

    # Latch captured on the pin / keeper.
    if "latch_hook" in parts:
        if r.latch_module == "sliding_bolt":
            _ov("latch_hook", elem_a="guide_keeper", elem_b="bolt_bar",
                reason="Sliding bolt passes through the guide keeper channel.")
            _ov("latch_hook", elem_a="guide_keeper", elem_b="bolt_head",
                reason="Bolt head seats against the guide keeper at the latch end.")
            for i in (0, 1):
                _ov("latch_hook", elem_a=f"bolt_mount_bracket_{i}", elem_b="bolt_head",
                    reason="Bolt head passes between the two keeper brackets.")
            _ov("latch_hook", elem_a="bolt_guide_rail_0", elem_b="bolt_bar",
                reason="Bolt slides between its two guide rails.")
            _ov("latch_hook", elem_a="bolt_guide_rail_1", elem_b="bolt_bar",
                reason="Bolt slides between its two guide rails.")
            _ov("latch_hook", elem_a="latch_hoop", elem_b="bolt_bar",
                reason="Retracted bolt passes back through the stirrup hoop opening.")
        else:
            _ov("latch_hook", elem_a="latch_pin", elem_b="hook_bar",
                reason="Latch hinge pin captured inside the hook bar.")
            _ov("latch_hook", elem_a="latch_mount_plate", elem_b="hook_bar",
                reason="Hook bar pivots on the pin against the latch mount plate.")
            _ov("latch_hook", elem_a="latch_hinge_ear_0", elem_b="hook_bar",
                reason="Hook bar runs between the two hinge ears on the pin.")
            _ov("latch_hook", elem_a="latch_hinge_ear_1", elem_b="hook_bar",
                reason="Hook bar runs between the two hinge ears on the pin.")
            _ov("latch_hook", elem_a="latch_hoop", elem_b="hook_bar",
                reason="Hook bar swings inside the stirrup hoop opening.")
            _ov("latch_hook", elem_a="latch_hoop", elem_b="latch_toe",
                reason="Release toe swings past the stirrup hoop leg on its way clear.")

    # Latch bolt engages the tub catch lug + end wall at rest (retention); it
    # draws clear when the joint opens (verified by the release pose test).
    if "latch_hook" in parts and "tub" in parts:
        latch = model.get_part("latch_hook")
        tub = model.get_part("tub")
        release_elem = "bolt_bar" if r.latch_module == "sliding_bolt" else "latch_toe"
        engaged = {"catch_lug", "tub_shell"}
        engaged |= {v.name for v in tub.visuals
                    if v.name.startswith(("strap_band_", "band_rivets_")) or v.name == "rim_rivets"}
        for elem_b in engaged:
            ctx.allow_overlap(latch, tub, elem_a=release_elem, elem_b=elem_b,
                              reason="Release toe/bolt engages the tub end wall / straps to retain the tub; it draws clear when opened.")

    # Wheel axle journals seated in axleboxes.
    for i in range(r.wheelset_count):
        for k in (2 * i, 2 * i + 1):
            _ov(f"wheelset_{i}", elem_a=f"axlebox_{k}", elem_b="axle",
                reason="Axle journal seated inside the axlebox pedestal.")

    # Tailgate hinge pin captured in the tub end wall / door knuckles.
    if "end_door" in parts:
        tub = model.get_part("tub")
        door = model.get_part("end_door")
        for kn in ("door_hinge_knuckle_0", "door_hinge_knuckle_1", "door_hinge_pin"):
            ctx.allow_overlap(tub, door, elem_a="tub_shell", elem_b=kn,
                              reason="Door hinge knuckle/pin seated against the tub +X rim.")
        ctx.allow_overlap(tub, door, elem_a="tub_shell", elem_b="door_panel",
                          reason="Closed door panel seats against the (uncut) +X end wall; swings clear when opened.")


def _center(aabb):
    if aabb is None:
        return None
    return [(aabb[0][i] + aabb[1][i]) / 2.0 for i in range(3)]


def _expect_tip(ctx, model, r) -> None:
    if r.tip_mechanism == "hoist_lift":
        lift = model.get_articulation("tub_lift")
        ctx.check("hoist lift is prismatic", lift.articulation_type == ArticulationType.PRISMATIC)
        tub = model.get_part("tub")
        chassis = model.get_part("chassis")

        def _guide_shoes_clear() -> tuple[bool, list[str]]:
            conflicts: list[str] = []
            for i in (0, 1):
                column = ctx.part_element_world_aabb(chassis, elem=f"guide_column_{i}")
                for suffix in ("inner", "outer", "cheek_0", "cheek_1"):
                    elem = f"slider_block_{i}_{suffix}"
                    shoe = ctx.part_element_world_aabb(tub, elem=elem)
                    if column is None or shoe is None:
                        conflicts.append(f"missing:{elem}")
                        continue
                    penetration = [
                        min(column[1][axis], shoe[1][axis])
                        - max(column[0][axis], shoe[0][axis])
                        for axis in range(3)
                    ]
                    if min(penetration) > 0.0:
                        conflicts.append(elem)
            return not conflicts, conflicts

        clear_at_rest, rest_conflicts = _guide_shoes_clear()
        rest = _center(ctx.part_world_aabb(tub))
        with ctx.pose({lift: r.lift_travel}):
            raised = _center(ctx.part_world_aabb(tub))
            clear_at_top, top_conflicts = _guide_shoes_clear()
        ok = rest and raised and (raised[2] - rest[2]) > 0.20 and abs(raised[0] - rest[0]) < 0.02
        ctx.check("hoist raises the tub vertically", bool(ok), details=f"rest={rest}, raised={raised}")
        ctx.check(
            "guide shoes have open bores around columns through full lift travel",
            clear_at_rest and clear_at_top,
            details=f"rest conflicts={rest_conflicts}, raised conflicts={top_conflicts}",
        )
        return

    tip = model.get_articulation("tub_tip")
    ctx.check("tub tip is revolute", tip.articulation_type == ArticulationType.REVOLUTE)
    axis = tuple(tip.axis)
    if r.discharge == "side":
        ctx.check("side tip axis is longitudinal X", abs(axis[0]) > 0.9, details=str(axis))
    else:
        ctx.check("end tip axis is transverse Y", abs(axis[1]) > 0.9, details=str(axis))
    tub = model.get_part("tub")
    rest = _center(ctx.part_element_world_aabb(tub, elem="catch_lug"))
    with ctx.pose({tip: r.tip_upper}):
        tipped = _center(ctx.part_element_world_aabb(tub, elem="catch_lug"))
    ok = rest and tipped and (tipped[2] - rest[2]) > 0.08
    ctx.check("tipping raises the discharge-end catch lug", bool(ok), details=f"rest={rest}, tipped={tipped}")


def _expect_latch(ctx, model, r) -> None:
    latch = model.get_articulation("latch_pivot")
    latch_part = model.get_part("latch_hook")
    if r.latch_module == "sliding_bolt":
        ctx.check("sliding bolt is prismatic", latch.articulation_type == ArticulationType.PRISMATIC)
        elem = "bolt_bar"
        val = r.bolt_travel
    else:
        ctx.check("gravity hook is revolute", latch.articulation_type == ArticulationType.REVOLUTE)
        elem = "latch_toe"
        val = r.latch_range
    rest = _center(ctx.part_element_world_aabb(latch_part, elem=elem))
    with ctx.pose({latch: val}):
        moved = _center(ctx.part_element_world_aabb(latch_part, elem=elem))
    d = 0.0 if (rest is None or moved is None) else math.dist(rest, moved)
    ctx.check("latch releases (toe/bolt moves clear)", d > 0.05, details=f"disp={d:.4f}")


def _expect_hoop_and_release(ctx, model, r) -> None:
    """Identity checks for the stirrup hoop and the release engagement.

    These are the two things the rod-and-crossbar hoop got wrong: the arch must be
    ONE plate rising off the frame beam at the discharge-facing end (not a pair of
    loose posts standing in the middle of the deck), and the release member must
    actually hold the catch lug at rest, then let go when the joint opens."""
    chassis = model.get_part("chassis")
    hoop = ctx.part_element_world_aabb(chassis, elem="latch_hoop")
    ctx.check("stirrup hoop present as one arch plate", hoop is not None)
    if hoop is not None:
        lo, hi = hoop
        # The whole cart rides `rail_top` above world zero when a track is laid, so
        # chassis-frame datums are compared in the lifted frame.
        ctx.check("hoop stands on the frame beam and arches above it",
                  lo[2] <= DECK_TOP + r.rail_top and hi[2] >= 0.80 + r.rail_top,
                  details=f"hoop aabb={hoop}, ride lift={r.rail_top:.4f}")
        if r.discharge == "side":
            reads_outboard = lo[1] < -0.45
        else:
            reads_outboard = lo[0] < -0.70
        ctx.check("hoop sits at the discharge-facing end of the frame", reads_outboard,
                  details=f"discharge={r.discharge}, hoop aabb={hoop}")
        thin = min(hi[0] - lo[0], hi[1] - lo[1])
        ctx.check("hoop is a flat plate, not a rod cage", thin <= 2.0 * HOOP_PLATE_T,
                  details=f"thinnest span={thin:.4f}")

    latch = model.get_part("latch_hook")
    tub = model.get_part("tub")
    elem = "bolt_bar" if r.latch_module == "sliding_bolt" else "latch_toe"
    member = ctx.part_element_world_aabb(latch, elem=elem)
    lug = ctx.part_element_world_aabb(tub, elem="catch_lug")
    if member is not None and lug is not None:
        overlap = [min(member[1][i], lug[1][i]) - max(member[0][i], lug[0][i]) for i in range(3)]
        ctx.check("release member holds the catch lug at rest", min(overlap) > 0.0,
                  details=f"{elem}={member}, catch_lug={lug}, overlap={overlap}")
    joint = model.get_articulation("latch_pivot")
    with ctx.pose({joint: r.bolt_travel if r.latch_module == "sliding_bolt" else r.latch_range}):
        released = ctx.part_element_world_aabb(latch, elem=elem)
    if released is not None and lug is not None:
        gaps = [max(released[1][i], lug[1][i]) - min(released[0][i], lug[0][i])
                - ((released[1][i] - released[0][i]) + (lug[1][i] - lug[0][i])) for i in range(3)]
        ctx.check("release member draws clear of the catch lug when opened", max(gaps) > 0.0,
                  details=f"released={released}, catch_lug={lug}")


def _expect_rim(ctx, model, r) -> None:
    """The saddle rim is a ③ form realization, so it must be geometrically real:
    the rim ends stand above the dipped middle by the derived amount."""
    if r.rim_profile != "saddle":
        ctx.check("flat rim keeps a level top", abs(r.rim_min_z - r.tub_top_z) < 1e-9,
                  details=f"rim_min_z={r.rim_min_z}, tub_top_z={r.tub_top_z}")
        return
    dip = r.tub_top_z - r.rim_min_z
    ctx.check("saddle rim dips at mid length", dip > 0.02, details=f"dip={dip:.4f}")
    ctx.check("saddle dip stays above the mid station",
              r.rim_min_z > TUB_BASE_Z + 0.62 * (r.tub_top_z - TUB_BASE_Z),
              details=f"rim_min_z={r.rim_min_z:.4f}")
    tub = model.get_part("tub")
    shell = ctx.part_element_world_aabb(tub, elem="tub_shell")
    ctx.check("shell top matches the raised rim ends", shell is not None
              and abs(shell[1][2] - (r.tub_top_z + r.rail_top)) < 0.02,
              details=f"shell aabb={shell}, tub_top_z={r.tub_top_z}, ride lift={r.rail_top:.4f}")


def _expect_track(ctx, model, r) -> None:
    """Track slot + its dependent shape slot.

    With `none` there must be no track part at all and the cart must be the root.
    With a track laid, the rail heads carry the wheels, the gauge must match the
    wheel plane, and `cart_travel` must move the whole cart along the rails."""
    parts = {p.name for p in model.parts}
    if r.track_module == "none":
        ctx.check("no track part when the track slot is none", "rail_track" not in parts)
        ctx.check("no cart_travel joint without a track",
                  all(a.name != "cart_travel" for a in model.articulations))
        return

    ctx.check("track part present", "rail_track" in parts)
    track = model.get_part("rail_track")
    head = ctx.part_element_world_aabb(track, elem="rail_head_0")
    ctx.check("rail head present and its top is the ride datum",
              head is not None and abs(head[1][2] - r.rail_top) <= 0.006,
              details=f"rail_head_0={head}, rail_top={r.rail_top:.4f}")
    # Each rail must pass under its own wheel plane. On a curve the rail sweeps away
    # in +Y, so its AABB centre is NOT the gauge -- what matters is that the wheel
    # plane falls inside the rail's lateral span.
    for j, side in enumerate((1.0, -1.0)):
        h = ctx.part_element_world_aabb(track, elem=f"rail_head_{j}")
        plane = side * TRACK_GAUGE_Y
        ctx.check(f"rail_head_{j} runs under its wheel plane",
                  h is not None and h[0][1] - 0.002 <= plane <= h[1][1] + 0.002,
                  details=f"rail_head_{j}={h}, wheel plane y={plane}")
    if r.track_shape == "curved":
        # Rigid wheelsets cannot steer, so the derived radius has to keep the
        # outermost tread on its head over the whole travel stroke.
        station = max(abs(a) for a in r.axle_positions) + r.cart_travel
        offset = station * station / (2.0 * r.track_radius)
        ctx.check("curve radius keeps the outer wheel on the rail head",
                  offset <= TRACK_RAIL_SEAT + 1e-6,
                  details=f"outer station={station:.4f}, lateral offset={offset:.4f}, "
                          f"limit={TRACK_RAIL_SEAT}, radius={r.track_radius:.3f}")
    aabb = ctx.part_world_aabb(track)
    ctx.check("track is laid on the ground", aabb is not None and abs(aabb[0][2]) <= 0.005,
              details=f"track aabb={aabb}")

    travel = model.get_articulation("cart_travel")
    ctx.check("cart_travel is prismatic along the track",
              travel.articulation_type == ArticulationType.PRISMATIC
              and abs(tuple(travel.axis)[0]) > 0.9,
              details=f"type={travel.articulation_type}, axis={tuple(travel.axis)}")
    chassis = model.get_part("chassis")
    rest = _center(ctx.part_world_aabb(chassis))
    with ctx.pose({travel: r.cart_travel}):
        rolled = _center(ctx.part_world_aabb(chassis))
    ok = rest and rolled and (rolled[0] - rest[0]) > 0.5 * r.cart_travel
    ctx.check("cart_travel rolls the cart along the rails", bool(ok),
              details=f"rest={rest}, rolled={rolled}, travel={r.cart_travel:.4f}")
    if aabb is not None and rolled is not None:
        ctx.check("cart stays on the track at full travel",
                  rolled[0] + CART_HALF_LEN <= aabb[1][0] + 0.01,
                  details=f"cart nose={rolled[0] + CART_HALF_LEN:.4f}, rail end={aabb[1][0]:.4f}")

    # The dependent shape slot has to be geometrically real, not just a label.
    if aabb is not None:
        bulge = (aabb[1][1] - aabb[0][1]) - TRACK_PROFILES[r.track_module]["tie"][1]
        if r.track_shape == "curved":
            ctx.check("curved track sweeps away from the cart", bulge > 0.05,
                      details=f"lateral bulge={bulge:.4f}, radius={r.track_radius:.3f}")
        else:
            ctx.check("straight track stays on one line", abs(bulge) <= 0.02,
                      details=f"lateral bulge={bulge:.4f}")


def _expect_wheels(ctx, model, r) -> None:
    names = [f"wheelset_{i}" for i in range(r.wheelset_count)]
    present = [n for n in names if any(p.name == n for p in model.parts)]
    ctx.check("wheelset count matches", len(present) == r.wheelset_count,
              details=f"wheelsets={present} expected={r.wheelset_count}")
    # With no track the wheels ride the ground plane; with a track they ride the
    # rail heads, which is the same datum lifted by rail_top.
    ride = r.rail_top
    for n in present:
        aabb = ctx.part_world_aabb(model.get_part(n))
        if aabb is not None:
            ctx.check(f"{n} rides the running surface", abs(aabb[0][2] - ride) <= 0.03,
                      details=f"{n} aabb={aabb}, running surface z={ride:.4f}")


def run_industrial_mine_cart_tests(
    model: ArticulatedObject,
    config: IndustrialMineCartConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)

    _declare_overlaps(ctx, model, r)

    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.020)
    ctx.fail_if_joint_mating_has_gap()

    _expect_tip(ctx, model, r)
    _expect_latch(ctx, model, r)
    _expect_hoop_and_release(ctx, model, r)
    _expect_rim(ctx, model, r)
    _expect_track(ctx, model, r)
    _expect_wheels(ctx, model, r)

    # Rule 5: dynamic collision across sampled joint poses.
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=64, ignore_fixed=True)

    return ctx.report()


__all__ = [
    "IndustrialMineCartConfig",
    "ResolvedIndustrialMineCartConfig",
    "TipMechanism",
    "TubForm",
    "RimProfile",
    "LatchModule",
    "WheelModule",
    "WheelForm",
    "TrackModule",
    "TrackShape",
    "MineCartPalette",
    "build_industrial_mine_cart",
    "build_seeded_industrial_mine_cart",
    "config_from_seed",
    "resolve_config",
    "run_industrial_mine_cart_tests",
    "slot_choices_for_seed",
]
