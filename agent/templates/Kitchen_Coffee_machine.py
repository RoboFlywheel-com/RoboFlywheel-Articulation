# SPDX-License-Identifier: Apache-2.0

"""Upright espresso / coffee machine modular template.

NOTE on the slug name: "coffee_machine" here = an **upright espresso / bean-to-cup
/ pod coffee machine** (a standing electric brew machine with a control fascia,
a selection dial, a drip tray and a brew front end), NOT an electric kettle (that
is ``container_kettle``), NOT a water dispenser, and NOT a drip carafe / French
press / moka pot. The structure family is an upright ``body`` (root, grounded at
z=0: base block / glossy core shell / tilted control fascia / top deck) carrying a
rotary ``selection_dial`` (CONTINUOUS, axis normal to the 15-degree tilted fascia)
and a forward-sliding ``drip_tray`` (PRISMATIC +X).

Sourced from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/Kitchen_Coffee_machine.md`` and the
``picture/Kitchen/Coffee machine`` 5-star sample pool (1 parent + 6 slot-fork
variants), all synced under ``data/records/``.

Structure (pattern = ``parallel_children``). ``brew_type`` (Slot A) is an
integral spine that decides the whole body mesh AND which downstream slots are
exposed -- it is NOT orthogonal to hopper_lid / water_tank:

  * ``brew_type`` (3): the dispensing front end / whole-machine spine.
      - ``super_automatic``: box-assembled body (W0.24/D0.35/H0.43) + a double-
        nozzle ``spout_block`` (PRISMATIC -Z, lowers to the cup) + a ``steam_wand``
        (REVOLUTE). EXPOSES Slot B (hopper_lid x3) AND Slot C (water_tank x3).
      - ``portafilter``: same box body but with a brass ``group_head`` (FIXED) +
        a removable ``portafilter`` with side handle (REVOLUTE twist-to-lock).
        NO spout_block, NO
        hopper (pre-ground coffee). NO Slot B; EXPOSES Slot C (water_tank x3).
      - ``pod_capsule``: a compact whole-machine re-body (W0.14/D0.28/H0.30) using
        ``rounded_rect_profile`` + ``ExtrudeGeometry`` shell, a single chrome
        spout, a body-integrated water-tank visual, and a top ``capsule_flap``
        (REVOLUTE). Slot B/C are spine defaults (not separately sampled); no
        steam wand.
  * ``hopper_lid`` (3, super_automatic only): rear_hinge (REVOLUTE -Y) /
    side_hinge (REVOLUTE +Z) / removable_canister (PRISMATIC +Z out of a guide
    bay; the canister shell is a hollow cadquery mesh).
  * ``water_tank`` (3, super_automatic / portafilter): internal (no part, no
    joint) / side_removable (PRISMATIC -Y from a right-flank dock bay) /
    top_reservoir (PRISMATIC +Z out of a rear cradle).

``selection_dial`` (CONTINUOUS) alone guarantees >=1 non-fixed joint on every
spine, even when the only slot mechanism is FIXED. All captured interfaces (dial
stem in fascia, spout housing on rail, wand knuckle on boss, flap pin in boss,
canister rib on bay floor, tank body on rail/cradle, portafilter rim in lock
ring) are captured-fit geometry, so those joints omit ``MatingContract``
(grandfathered) and are guarded by the flat articulation-origin baseline +
element-scoped ``allow_overlap`` (mirroring each source record's run_tests block).

PERFORMANCE: kitchen-appliance meshes are kept light. The decorative perforated
panels (cup-warming grid, drip plate) from the source records are rendered as
simple solid plate Boxes here, and the only cadquery mesh (the hollow canister
shell) raises ``tolerance`` / ``angular_tolerance`` so the collision-inclusive
compile stays fast.
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
    ExtrudeGeometry,
    Inertial,
    KnobGeometry,
    KnobIndicator,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
    mesh_from_geometry,
    rounded_rect_profile,
)

__modular__ = True

BrewType = Literal["super_automatic", "portafilter", "pod_capsule"]
HopperLid = Literal["rear_hinge", "side_hinge", "removable_canister"]
WaterTank = Literal["internal", "side_removable", "top_reservoir"]
PaletteStyle = Literal[
    "gloss_black_stainless",
    "matte_graphite",
    "cream_retro",
    "red_accent",
    "brushed_inox",
]

BREW_TYPES: tuple[BrewType, ...] = ("super_automatic", "portafilter", "pod_capsule")
HOPPER_LIDS: tuple[HopperLid, ...] = ("rear_hinge", "side_hinge", "removable_canister")
WATER_TANKS: tuple[WaterTank, ...] = ("internal", "side_removable", "top_reservoir")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "gloss_black_stainless",
    "matte_graphite",
    "cream_retro",
    "red_accent",
    "brushed_inox",
)

# ---------------------------------------------------------------------------
# Per-seed palettes (spec palette table). Keys map to every .visual material so
# the swept pool is colorful (module_topology_diversity only counts structure).
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "gloss_black_stainless": {
        "core": (0.10, 0.10, 0.11, 1.0),
        "body": (0.17, 0.17, 0.185, 1.0),
        "fascia": (0.55, 0.56, 0.575, 1.0),
        "trim": (0.065, 0.065, 0.07, 1.0),
        "metal": (0.72, 0.73, 0.75, 1.0),
        "silver": (0.80, 0.81, 0.83, 1.0),
        "accent": (0.30, 0.30, 0.315, 1.0),
        "brass": (0.72, 0.58, 0.28, 1.0),
        "tank": (0.62, 0.70, 0.78, 0.55),
        "water": (0.30, 0.48, 0.68, 0.85),
    },
    "matte_graphite": {
        "core": (0.14, 0.14, 0.15, 1.0),
        "body": (0.20, 0.20, 0.215, 1.0),
        "fascia": (0.065, 0.065, 0.07, 1.0),
        "trim": (0.05, 0.05, 0.055, 1.0),
        "metal": (0.70, 0.72, 0.74, 1.0),
        "silver": (0.78, 0.79, 0.81, 1.0),
        "accent": (0.34, 0.34, 0.355, 1.0),
        "brass": (0.70, 0.56, 0.30, 1.0),
        "tank": (0.55, 0.65, 0.72, 0.55),
        "water": (0.28, 0.46, 0.66, 0.85),
    },
    "cream_retro": {
        "core": (0.90, 0.87, 0.80, 1.0),
        "body": (0.84, 0.80, 0.72, 1.0),
        "fascia": (0.74, 0.71, 0.64, 1.0),
        "trim": (0.30, 0.27, 0.22, 1.0),
        "metal": (0.78, 0.80, 0.82, 1.0),
        "silver": (0.82, 0.84, 0.86, 1.0),
        "accent": (0.42, 0.38, 0.32, 1.0),
        "brass": (0.78, 0.64, 0.34, 1.0),
        "tank": (0.74, 0.84, 0.90, 0.55),
        "water": (0.34, 0.52, 0.70, 0.85),
    },
    "red_accent": {
        "core": (0.78, 0.14, 0.12, 1.0),
        "body": (0.62, 0.12, 0.10, 1.0),
        "fascia": (0.10, 0.10, 0.11, 1.0),
        "trim": (0.06, 0.06, 0.07, 1.0),
        "metal": (0.74, 0.76, 0.79, 1.0),
        "silver": (0.80, 0.82, 0.84, 1.0),
        "accent": (0.20, 0.20, 0.22, 1.0),
        "brass": (0.74, 0.60, 0.30, 1.0),
        "tank": (0.62, 0.70, 0.78, 0.55),
        "water": (0.30, 0.48, 0.68, 0.85),
    },
    "brushed_inox": {
        "core": (0.66, 0.68, 0.70, 1.0),
        "body": (0.58, 0.60, 0.62, 1.0),
        "fascia": (0.46, 0.47, 0.49, 1.0),
        "trim": (0.20, 0.20, 0.22, 1.0),
        "metal": (0.74, 0.76, 0.78, 1.0),
        "silver": (0.82, 0.84, 0.86, 1.0),
        "accent": (0.40, 0.41, 0.43, 1.0),
        "brass": (0.72, 0.58, 0.30, 1.0),
        "tank": (0.66, 0.74, 0.80, 0.55),
        "water": (0.28, 0.48, 0.68, 0.85),
    },
}

# ---------------------------------------------------------------------------
# Base real-world dimensions (meters). super_automatic / portafilter share the
# box-assembled body; pod_capsule is a compact extruded re-body. Frame: +X =
# front, +Y = machine left, +Z = up. Grounded at z=0.
# ---------------------------------------------------------------------------
# super-auto / portafilter box body.
SA_WIDTH = 0.24
SA_DEPTH = 0.35
SA_HEIGHT = 0.43
SA_TILT = math.radians(15.0)
SA_FASCIA_TH = 0.025
SA_FASCIA_H = 0.155
SA_FASCIA_BOTTOM_Z = 0.262
SA_DECK_TOP_Z = 0.418  # top surface of top_deck (hinge / bay reference)

SA_SPOUT_TRAVEL = 0.06
SA_WAND_SWING = math.radians(60.0)
SA_LID_OPEN = math.radians(100.0)
PF_LOCK_SWING = math.radians(55.0)

# pod compact body.
POD_WIDTH = 0.14
POD_DEPTH = 0.28
POD_HEIGHT = 0.30
POD_DECK_TH = 0.012
POD_FLAP_OPEN = math.radians(100.0)

TRAY_TRAVEL_SA = 0.12
TRAY_TRAVEL_POD = 0.08

# Removable canister (Slot B) dims.
HOPPER_W = 0.100
HOPPER_D = 0.160
HOPPER_H = 0.080
HOPPER_WALL = 0.004
HOPPER_CENTER_X = -0.050
GUIDE_H = 0.030
GUIDE_T = 0.005
HOPPER_TRAVEL = 0.10

# side_removable water tank (Slot C) dims.
TANK_X_C = -0.050
TANK_Z_C = 0.200
TANK_DX = 0.065
TANK_DY = 0.045
TANK_DZ = 0.220
TANK_SIDE_TRAVEL = 0.10

# top_reservoir water tank (Slot C) dims.
RES_X_C = -0.210
RES_DECK_Z = 0.413
RES_TRAVEL = 0.15

# Group head / portafilter (portafilter spine) placement.
GH_X = 0.155
GH_Z = 0.185
GH_BODY_H = 0.055
GH_FLANGE_H = 0.010
GH_LOCK_H = 0.006
PF_Z = 0.176


@dataclass(frozen=True)
class CoffeeMachineConfig:
    brew_type: BrewType | None = None
    hopper_lid: HopperLid | None = None
    water_tank: WaterTank | None = None
    palette_style: PaletteStyle = "gloss_black_stainless"
    body_height_scale: float = 1.0
    body_width_scale: float = 1.0
    body_depth_scale: float = 1.0
    fascia_tilt_scale: float = 1.0
    tray_travel_scale: float = 1.0
    spout_travel_scale: float = 1.0
    wand_swing_scale: float = 1.0
    lid_open_scale: float = 1.0
    canister_lift_scale: float = 1.0
    tank_travel_scale: float = 1.0
    name: str = "coffee_machine"


@dataclass(frozen=True)
class ResolvedCoffeeMachineConfig:
    brew_type: BrewType
    hopper_lid: HopperLid | None  # None when the spine has no hopper
    water_tank: WaterTank | None  # None when the spine has no separable tank
    palette_style: PaletteStyle
    # Concrete body geometry (scaled / derived).
    width: float
    depth: float
    height: float
    x_front: float
    x_rear: float
    tilt: float
    deck_top_z: float
    # Travels / angles.
    tray_travel: float
    spout_travel: float
    wand_swing: float
    lid_open: float
    canister_lift: float
    tank_travel: float
    name: str

    @property
    def is_box_body(self) -> bool:
        return self.brew_type in ("super_automatic", "portafilter")


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


# ---------------------------------------------------------------------------
# Procedural sampling (Contract 4). Sample the brew_type spine first, then the
# downstream slots ONLY when the spine exposes them (spec compatibility matrix).
# ---------------------------------------------------------------------------
def config_from_seed(seed: int) -> CoffeeMachineConfig:
    rng = random.Random(seed)
    brew_type = rng.choice(BREW_TYPES)
    if brew_type == "super_automatic":
        hopper_lid = rng.choice(HOPPER_LIDS)
        water_tank = rng.choice(WATER_TANKS)
    elif brew_type == "portafilter":
        hopper_lid = None  # pre-ground coffee: no bean hopper
        water_tank = rng.choice(WATER_TANKS)
    else:  # pod_capsule: spine defaults (capsule_flap + integrated tank visual)
        hopper_lid = None
        water_tank = None
    return CoffeeMachineConfig(
        brew_type=brew_type,
        hopper_lid=hopper_lid,
        water_tank=water_tank,
        palette_style=rng.choice(PALETTE_STYLES),
        body_height_scale=round(rng.uniform(0.90, 1.12), 4),
        body_width_scale=round(rng.uniform(0.92, 1.10), 4),
        body_depth_scale=round(rng.uniform(0.92, 1.12), 4),
        fascia_tilt_scale=round(rng.uniform(0.85, 1.15), 4),
        tray_travel_scale=round(rng.uniform(0.85, 1.10), 4),
        spout_travel_scale=round(rng.uniform(0.85, 1.10), 4),
        wand_swing_scale=round(rng.uniform(0.85, 1.10), 4),
        lid_open_scale=round(rng.uniform(0.85, 1.10), 4),
        canister_lift_scale=round(rng.uniform(0.85, 1.10), 4),
        tank_travel_scale=round(rng.uniform(0.85, 1.10), 4),
        name=f"seeded_coffee_machine_{seed}",
    )


def resolve_config(
    config: CoffeeMachineConfig | None = None,
) -> ResolvedCoffeeMachineConfig:
    cfg = config or CoffeeMachineConfig()
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)
    brew_type = _pick(cfg.brew_type, BREW_TYPES)

    # --- Compatibility matrix (spec §9). brew_type spine gates the slots. ---
    if brew_type == "super_automatic":
        hopper_lid: HopperLid | None = _pick(cfg.hopper_lid, HOPPER_LIDS)
        water_tank: WaterTank | None = _pick(cfg.water_tank, WATER_TANKS)
    elif brew_type == "portafilter":
        hopper_lid = None  # no bean hopper on a portafilter machine
        water_tank = _pick(cfg.water_tank, WATER_TANKS)
    else:  # pod_capsule
        hopper_lid = None  # capsule_flap is a spine default (inline)
        water_tank = None  # body-integrated tank visual is a spine default

    height_scale = _clamp(cfg.body_height_scale, 0.90, 1.12)
    width_scale = _clamp(cfg.body_width_scale, 0.92, 1.10)
    depth_scale = _clamp(cfg.body_depth_scale, 0.92, 1.12)
    tilt_scale = _clamp(cfg.fascia_tilt_scale, 0.85, 1.15)
    tray_travel_scale = _clamp(cfg.tray_travel_scale, 0.85, 1.10)
    spout_travel_scale = _clamp(cfg.spout_travel_scale, 0.85, 1.10)
    wand_swing_scale = _clamp(cfg.wand_swing_scale, 0.85, 1.10)
    lid_open_scale = _clamp(cfg.lid_open_scale, 0.85, 1.10)
    canister_lift_scale = _clamp(cfg.canister_lift_scale, 0.85, 1.10)
    tank_travel_scale = _clamp(cfg.tank_travel_scale, 0.85, 1.10)

    if brew_type == "pod_capsule":
        width = POD_WIDTH * width_scale
        depth = POD_DEPTH * depth_scale
        height = POD_HEIGHT * height_scale
        deck_top_z = height + POD_DECK_TH / 2.0
        tilt = 0.0
        tray_base = TRAY_TRAVEL_POD
    else:
        width = SA_WIDTH * width_scale
        depth = SA_DEPTH * depth_scale
        height = SA_HEIGHT * height_scale
        deck_top_z = SA_DECK_TOP_Z * height_scale
        # Keep the fascia tilt within a sane physical band [8deg, 22deg].
        tilt = _clamp(SA_TILT * tilt_scale, math.radians(8.0), math.radians(22.0))
        tray_base = TRAY_TRAVEL_SA

    x_front = depth / 2.0
    x_rear = -depth / 2.0

    # --- tray travel inequality: must not unseat from the bay (spec §7). ---
    tray_travel = tray_base * tray_travel_scale
    tray_travel = min(tray_travel, depth - 0.10)
    tray_travel = max(tray_travel, 0.04)

    # spout travel: positive q lowers nozzles to the cup, must clear the drip
    # plate (super_automatic only).
    spout_travel = _clamp(SA_SPOUT_TRAVEL * spout_travel_scale, 0.04, 0.075)
    wand_swing = _clamp(SA_WAND_SWING * wand_swing_scale, 0.6, math.pi * 0.5)
    lid_open = _clamp(SA_LID_OPEN * lid_open_scale, 1.0, math.pi * 0.95)

    # canister lift must clear the guide bay; tank travel must clear the bay.
    canister_lift = max(
        HOPPER_TRAVEL * canister_lift_scale, GUIDE_H + 0.04
    )
    if water_tank == "top_reservoir":
        tank_travel = max(RES_TRAVEL * tank_travel_scale, 0.10)
    else:
        tank_travel = max(TANK_SIDE_TRAVEL * tank_travel_scale, TANK_DY + 0.04)

    return ResolvedCoffeeMachineConfig(
        brew_type=brew_type,
        hopper_lid=hopper_lid,
        water_tank=water_tank,
        palette_style=palette_style,
        width=width,
        depth=depth,
        height=height,
        x_front=x_front,
        x_rear=x_rear,
        tilt=tilt,
        deck_top_z=deck_top_z,
        tray_travel=tray_travel,
        spout_travel=spout_travel,
        wand_swing=wand_swing,
        lid_open=lid_open,
        canister_lift=canister_lift,
        tank_travel=tank_travel,
        name=cfg.name or "coffee_machine",
    )


def with_overrides(config: CoffeeMachineConfig, **kwargs: object) -> CoffeeMachineConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: CoffeeMachineConfig | ResolvedCoffeeMachineConfig,
) -> tuple[tuple[str, str], ...]:
    r = (
        config
        if isinstance(config, ResolvedCoffeeMachineConfig)
        else resolve_config(config)
    )
    choices: list[tuple[str, str]] = [("brew_type", r.brew_type)]
    # Variable-length tuple: only spines that expose a slot list it (spec §9).
    if r.hopper_lid is not None:
        choices.append(("hopper_lid", r.hopper_lid))
    if r.water_tank is not None:
        choices.append(("water_tank", r.water_tank))
    return tuple(choices)


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Fascia geometry helper (super-auto / portafilter box body). u runs up the
# tilted fascia panel; proud pushes a point out along the fascia normal.
# ---------------------------------------------------------------------------
def _fascia_frame(r: ResolvedCoffeeMachineConfig):
    tilt = r.tilt
    n = (math.cos(tilt), 0.0, math.sin(tilt))  # outward normal
    h = (-math.sin(tilt), 0.0, math.cos(tilt))  # up the panel
    center = (
        r.x_front
        - (SA_FASCIA_H / 2.0) * math.sin(tilt)
        - (SA_FASCIA_TH / 2.0) * math.cos(tilt),
        0.0,
        SA_FASCIA_BOTTOM_Z * (r.height / SA_HEIGHT)
        + (SA_FASCIA_H / 2.0) * math.cos(tilt)
        - (SA_FASCIA_TH / 2.0) * math.sin(tilt),
    )
    return n, h, center


def _fascia_point(r: ResolvedCoffeeMachineConfig, u: float, y: float, proud: float):
    n, h, center = _fascia_frame(r)
    return (
        center[0] + (SA_FASCIA_TH / 2.0 + proud) * n[0] + u * h[0],
        y,
        center[2] + (SA_FASCIA_TH / 2.0 + proud) * n[2] + u * h[2],
    )


def _knob_mesh(name: str, knob_r: float, knob_h: float):
    knob = KnobGeometry(
        knob_r,
        knob_h,
        body_style="cylindrical",
        edge_radius=0.002,
        indicator=KnobIndicator(style="line", mode="raised", angle_deg=90.0),
        center=False,
    )
    return mesh_from_geometry(knob, name)


# ===========================================================================
# Body builders.
# ===========================================================================
def _build_box_body(model: ArticulatedObject, r: ResolvedCoffeeMachineConfig, mats):
    """super_automatic / portafilter shared box-assembled body (root)."""
    body = model.part("body")
    w = r.width
    hy = w / 2.0
    sx = r.depth / SA_DEPTH  # depth-scale factor relative to source layout
    sz = r.height / SA_HEIGHT
    x_front = r.x_front
    x_rear = r.x_rear
    is_pf = r.brew_type == "portafilter"

    # Rear base block (the drip tray docks in front of it).
    body.visual(
        Box((0.195 * sx, w, 0.080 * sz)),
        origin=Origin(xyz=(-0.0775 * sx, 0.0, 0.040 * sz)),
        material=mats["body"],
        name="base_block", material_class_id=("metal.stainless_matte" if r.palette_style in {"gloss_black_stainless", "matte_graphite", "cream_retro", "brushed_inox"} else "plastic.opaque_glossy_molded"),
    )
    # Side skirts flanking the drip-tray bay.
    for sgn, tag in ((1.0, "left"), (-1.0, "right")):
        body.visual(
            Box((0.165 * sx, 0.010, 0.080 * sz)),
            origin=Origin(xyz=(0.0925 * sx, sgn * (hy - 0.005), 0.040 * sz)),
            material=mats["body"],
            name=f"{tag}_base_skirt", material_class_id=("metal.stainless_matte" if r.palette_style in {"gloss_black_stainless", "matte_graphite", "cream_retro", "brushed_inox"} else "plastic.opaque_glossy_molded"),
        )
    # Main glossy core / side panels.
    body.visual(
        Box((0.275 * sx, w, 0.325 * sz)),
        origin=Origin(xyz=(-0.0375 * sx, 0.0, 0.2375 * sz)),
        material=mats["core"],
        name="core_shell", material_class_id=("metal.stainless_matte" if r.palette_style in {"gloss_black_stainless", "matte_graphite", "cream_retro", "brushed_inox"} else "plastic.opaque_glossy_molded"),
    )
    # Front cheeks flanking the dispensing recess (shorter for portafilter so
    # the portafilter clearance area stays open under the group head).
    cheek_h = 0.085 if is_pf else 0.190
    cheek_z = 0.2225 if is_pf else 0.170
    for sgn, tag in ((1.0, "left"), (-1.0, "right")):
        body.visual(
            Box((0.080 * sx, 0.055, cheek_h * sz)),
            origin=Origin(xyz=(0.135 * sx, sgn * 0.0925, cheek_z * sz)),
            material=mats["fascia"],
            name=f"{tag}_front_cheek", material_class_id=("metal.stainless_matte" if r.palette_style in {"gloss_black_stainless", "matte_graphite", "cream_retro", "brushed_inox"} else "plastic.opaque_glossy_molded"),
        )
    # Recessed channel back wall between the cheeks.
    body.visual(
        Box((0.018 * sx, 0.130, 0.190 * sz)),
        origin=Origin(xyz=(0.107 * sx, 0.0, 0.170 * sz)),
        material=mats["trim"],
        name="channel_back_wall", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"gloss_black_stainless", "cream_retro", "red_accent"} else "plastic.opaque_generic"),
    )
    if not is_pf:
        # Vertical rail the spout carriage rides on (super_automatic only).
        body.visual(
            Box((0.014 * sx, 0.032, 0.170 * sz)),
            origin=Origin(xyz=(0.119 * sx, 0.0, 0.165 * sz)),
            material=mats["trim"],
            name="spout_rail", material_class_id="metal.stainless_matte",
        )
    # Tilted control fascia across the upper front.
    n, h, fc = _fascia_frame(r)
    body.visual(
        Box((SA_FASCIA_TH, w, SA_FASCIA_H)),
        origin=Origin(xyz=fc, rpy=(0.0, -r.tilt, 0.0)),
        material=mats["fascia"],
        name="fascia_panel", material_class_id=("metal.stainless_matte" if r.palette_style in {"gloss_black_stainless", "matte_graphite", "cream_retro", "brushed_inox"} else "plastic.opaque_glossy_molded"),
    )
    # Flat top deck.
    body.visual(
        Box((0.293 * sx, w, 0.020)),
        origin=Origin(xyz=(-0.0285 * sx, 0.0, 0.408 * sz)),
        material=mats["trim"],
        name="top_deck", material_class_id=("metal.stainless_matte" if r.palette_style in {"gloss_black_stainless", "matte_graphite", "cream_retro", "brushed_inox"} else "plastic.opaque_glossy_molded"),
    )
    # Cup-warming plate (rendered as a light solid plate -- the source's
    # perforated grid mesh is decorative and heavy; PERFORMANCE note). Kept on
    # the FRONT half of the deck (rear edge ~-0.020*sx) so it never meets the
    # rear hopper-lid coverage zone.
    body.visual(
        Box((0.130 * sx, 0.180, 0.005)),
        origin=Origin(xyz=(0.045 * sx, 0.0, 0.419 * sz)),
        material=mats["accent"],
        name="cup_warming_grid", material_class_id="metal.patterned_sheet_panel",
    )
    # Square fascia buttons (3 per side) + a round power button (Rule 1 decor).
    for sgn, tag in ((1.0, "left"), (-1.0, "right")):
        for k, u in enumerate((0.034, 0.0, -0.034)):
            body.visual(
                Box((0.007, 0.016, 0.016)),
                origin=Origin(
                    xyz=_fascia_point(r, u, sgn * 0.078, 0.003), rpy=(0.0, -r.tilt, 0.0)
                ),
                material=mats["accent"],
                name=f"{tag}_button_{k}", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"gloss_black_stainless", "cream_retro", "red_accent"} else "plastic.opaque_generic"),
            )
    body.visual(
        Cylinder(radius=0.006, length=0.006),
        origin=Origin(
            xyz=_fascia_point(r, 0.058, 0.085, 0.002),
            rpy=(0.0, math.pi / 2.0 - r.tilt, 0.0),
        ),
        material=mats["accent"],
        name="power_button", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"gloss_black_stainless", "cream_retro", "red_accent"} else "plastic.opaque_generic"),
    )
    # Brand badge plate below the dial.
    body.visual(
        Box((0.004, 0.055, 0.014)),
        origin=Origin(
            xyz=_fascia_point(r, -0.060, 0.0, 0.001), rpy=(0.0, -r.tilt, 0.0)
        ),
        material=mats["silver"],
        name="brand_badge", material_class_id=("metal.brushed_silver" if r.palette_style == "brushed_inox" else "metal.chrome_polished"),
    )
    # Steam-wand pivot boss on the left flank.
    body.visual(
        Cylinder(radius=0.015, length=0.035),
        origin=Origin(xyz=(0.085 * sx, hy + 0.005, 0.285 * sz), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["trim"],
        name="wand_boss", material_class_id="metal.stainless_matte",
    )
    if is_pf:
        # Group-head mounting boss (bridges channel wall to the brew group).
        # The boss is a horizontal stub that reaches forward to the group head
        # joint line at x=GH_X*sx, so the FIXED joint origin sits on real
        # mount hardware (flat 0.015 m articulation-origin baseline).
        boss_back_x = 0.116 * sx
        boss_len = (GH_X * sx) - boss_back_x + 0.006
        body.visual(
            Cylinder(radius=0.022, length=boss_len),
            origin=Origin(
                xyz=(boss_back_x + boss_len / 2.0, 0.0, GH_Z * sz),
                rpy=(0.0, math.pi / 2.0, 0.0),
            ),
            material=mats["metal"],
            name="group_mount_boss", material_class_id="metal.stainless_matte",
        )

    body.inertial = Inertial.from_geometry(
        Box((r.depth, w, r.height)),
        mass=3.5,
        origin=Origin(xyz=(-0.02 * sx, 0.0, r.height * 0.42)),
    )
    return body


def _build_pod_body(model: ArticulatedObject, r: ResolvedCoffeeMachineConfig, mats):
    """pod_capsule compact whole-machine re-body (root)."""
    body = model.part("body")
    w = r.width
    depth = r.depth
    height = r.height
    x_front = r.x_front
    x_rear = r.x_rear
    deck_top = r.deck_top_z

    # Main body shell: rounded rectangle extruded vertically.
    body_profile = rounded_rect_profile(depth, w, 0.025, corner_segments=8)
    body_shell = ExtrudeGeometry.from_z0(body_profile, height, cap=True)
    body.visual(
        mesh_from_geometry(body_shell, "body_shell"),
        material=mats["core"],
        name="body_shell", material_class_id=("metal.stainless_matte" if r.palette_style in {"gloss_black_stainless", "matte_graphite", "cream_retro", "brushed_inox"} else "plastic.opaque_glossy_molded"),
    )
    # Top deck.
    body.visual(
        Box((depth - 0.04, w - 0.02, POD_DECK_TH)),
        origin=Origin(xyz=(0.0, 0.0, height)),
        material=mats["body"],
        name="top_deck", material_class_id=("metal.stainless_matte" if r.palette_style in {"gloss_black_stainless", "matte_graphite", "cream_retro", "brushed_inox"} else "plastic.opaque_glossy_molded"),
    )
    # Front fascia, slightly proud of the shell front.
    body.visual(
        Box((0.008, w - 0.02, 0.18)),
        origin=Origin(xyz=(x_front - 0.001, 0.0, 0.16)),
        material=mats["body"],
        name="front_fascia", material_class_id=("metal.stainless_matte" if r.palette_style in {"gloss_black_stainless", "matte_graphite", "cream_retro", "brushed_inox"} else "plastic.opaque_glossy_molded"),
    )
    # Dispensing recess.
    body.visual(
        Box((0.05, 0.08, 0.10)),
        origin=Origin(xyz=(x_front - 0.025, 0.0, 0.13)),
        material=mats["trim"],
        name="dispensing_recess", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"gloss_black_stainless", "cream_retro", "red_accent"} else "plastic.opaque_generic"),
    )
    # Single chrome spout + tip.
    body.visual(
        Cylinder(radius=0.008, length=0.030),
        origin=Origin(xyz=(x_front - 0.01, 0.0, 0.10), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["silver"],
        name="single_spout", material_class_id=("metal.brushed_silver" if r.palette_style == "brushed_inox" else "metal.chrome_polished"),
    )
    body.visual(
        Cylinder(radius=0.005, length=0.016),
        origin=Origin(xyz=(x_front + 0.01, 0.0, 0.10), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["silver"],
        name="spout_tip", material_class_id=("metal.brushed_silver" if r.palette_style == "brushed_inox" else "metal.chrome_polished"),
    )
    # Capsule slot opening on top (under the flap when closed).
    body.visual(
        Box((0.05, 0.04, 0.006)),
        origin=Origin(xyz=(-0.06, 0.0, deck_top + 0.001)),
        material=mats["trim"],
        name="capsule_slot", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"gloss_black_stainless", "cream_retro", "red_accent"} else "plastic.opaque_generic"),
    )
    # Body-integrated water tank (Slot C spine default for pod).
    body.visual(
        Box((0.07, w - 0.03, 0.20)),
        origin=Origin(xyz=(x_rear + 0.035, 0.0, 0.14)),
        material=mats["tank"],
        name="water_tank", material_class_id="plastic.frosted_translucent",
    )
    # Base platform.
    body.visual(
        Box((depth + 0.01, w + 0.01, 0.015)),
        origin=Origin(xyz=(0.0, 0.0, 0.0075)),
        material=mats["body"],
        name="base_platform", material_class_id=("metal.stainless_matte" if r.palette_style in {"gloss_black_stainless", "matte_graphite", "cream_retro", "brushed_inox"} else "plastic.opaque_glossy_molded"),
    )
    # Tray guide rails.
    for i, sgn in enumerate((1.0, -1.0)):
        body.visual(
            Box((0.12, 0.005, 0.010)),
            origin=Origin(xyz=(0.05, sgn * (w / 2.0 - 0.015), 0.020)),
            material=mats["body"],
            name=f"tray_guide_{i}", material_class_id=("metal.stainless_matte" if r.palette_style in {"gloss_black_stainless", "matte_graphite", "cream_retro", "brushed_inox"} else "plastic.opaque_glossy_molded"),
        )
    # Flap hinge boss at the rear top edge.
    body.visual(
        Cylinder(radius=0.007, length=w - 0.02),
        origin=Origin(xyz=(x_rear, 0.0, deck_top), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["core"],
        name="flap_hinge_boss", material_class_id=("metal.stainless_matte" if r.palette_style in {"gloss_black_stainless", "matte_graphite", "cream_retro", "brushed_inox"} else "plastic.opaque_glossy_molded"),
    )

    body.inertial = Inertial.from_geometry(
        Box((depth, w, height)),
        mass=2.5,
        origin=Origin(xyz=(-0.02, 0.0, height * 0.42)),
    )
    return body


# ===========================================================================
# Shared module factories (dial / tray / spout / wand).
# ===========================================================================
def _emit_dial(model, r: ResolvedCoffeeMachineConfig, body, mats):
    """Rotary selection dial. CONTINUOUS about the fascia normal (super-auto /
    portafilter) or about the front face +X (pod). Shared on every spine."""
    dial = model.part("selection_dial")
    if r.is_box_body:
        dial_r, knob_r, knob_h = 0.027, 0.040, 0.022
        ring_z, knob_z, ptr_y, ptr_z = 0.0035, 0.006, 0.014, 0.0287
        stem_l = 0.014
    else:
        dial_r, knob_r, knob_h = 0.020, 0.030, 0.015
        ring_z, knob_z, ptr_y, ptr_z = 0.003, 0.005, 0.010, 0.021
        stem_l = 0.012
    dial.visual(
        Cylinder(radius=0.008 if r.is_box_body else 0.006, length=stem_l),
        origin=Origin(xyz=(0.0, 0.0, -0.004)),
        material=mats["trim"],
        name="dial_stem", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"gloss_black_stainless", "cream_retro", "red_accent"} else "plastic.opaque_generic"),
    )
    dial.visual(
        Cylinder(radius=dial_r, length=0.006),
        origin=Origin(xyz=(0.0, 0.0, ring_z)),
        material=mats["silver"],
        name="dial_ring", material_class_id=("metal.brushed_silver" if r.palette_style == "brushed_inox" else "metal.chrome_polished"),
    )
    dial.visual(
        _knob_mesh("dial_knob", knob_r, knob_h),
        origin=Origin(xyz=(0.0, 0.0, knob_z)),
        material=mats["silver"],
        name="dial_knob", material_class_id=("metal.brushed_silver" if r.palette_style == "brushed_inox" else "metal.chrome_polished"),
    )
    dial.visual(
        Box((0.003, 0.003, 0.0024)),
        origin=Origin(xyz=(0.0, ptr_y, ptr_z)),
        material=mats["trim"],
        name="dial_pointer", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"gloss_black_stainless", "cream_retro", "red_accent"} else "plastic.opaque_generic"),
    )
    dial.inertial = Inertial.from_geometry(
        Cylinder(radius=knob_r, length=knob_h + 0.01),
        mass=0.03,
        origin=Origin(xyz=(0.0, 0.0, 0.005)),
    )
    if r.is_box_body:
        origin = Origin(
            xyz=_fascia_point(r, 0.005, 0.0, 0.0),
            rpy=(0.0, math.pi / 2.0 - r.tilt, 0.0),
        )
        joint_name = "fascia_to_dial"
    else:
        origin = Origin(xyz=(r.x_front + 0.001, 0.0, 0.20), rpy=(0.0, math.pi / 2.0, 0.0))
        joint_name = "body_to_dial"
    model.articulation(
        joint_name,
        ArticulationType.CONTINUOUS,
        parent=body,
        child=dial,
        origin=origin,
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=2.0, velocity=4.0),
    )
    return dial, joint_name


def _emit_tray(model, r: ResolvedCoffeeMachineConfig, body, mats):
    """Drip tray. PRISMATIC forward (+X). Shared on every spine."""
    tray = model.part("drip_tray")
    if r.is_box_body:
        sx = r.depth / SA_DEPTH
        # Tray tracks the body width: its side walls sit inboard of the base
        # skirts (skirt inner face = hy-0.010) so width-scaling never collides.
        hy = r.width / 2.0
        wall_y = hy - 0.016
        w = 2.0 * wall_y  # tray body width (between the inner faces of the walls)
        # Floor starts at the body-to-tray joint line (x=0) so the child link
        # frame origin sits on real tray geometry (articulation-origin baseline).
        floor_len = 0.185 * sx
        tray.visual(
            Box((floor_len, w, 0.008)),
            origin=Origin(xyz=(floor_len / 2.0, 0.0, 0.004)),
            material=mats["trim"],
            name="tray_floor", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"gloss_black_stainless", "cream_retro", "red_accent"} else "plastic.opaque_generic"),
        )
        tray.visual(
            Box((0.010, w, 0.064)),
            origin=Origin(xyz=(0.174 * sx, 0.0, 0.038)),
            material=mats["trim"],
            name="tray_front_wall", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"gloss_black_stainless", "cream_retro", "red_accent"} else "plastic.opaque_generic"),
        )
        # Rear wall straddles the joint line so the origin is captured in geometry.
        tray.visual(
            Box((0.012, w, 0.064)),
            origin=Origin(xyz=(0.004, 0.0, 0.038)),
            material=mats["trim"],
            name="tray_rear_wall", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"gloss_black_stainless", "cream_retro", "red_accent"} else "plastic.opaque_generic"),
        )
        for sgn, tag in ((1.0, "left"), (-1.0, "right")):
            tray.visual(
                Box((0.160 * sx, 0.008, 0.064)),
                origin=Origin(xyz=(0.101 * sx, sgn * wall_y, 0.038)),
                material=mats["trim"],
                name=f"tray_{tag}_wall", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"gloss_black_stainless", "cream_retro", "red_accent"} else "plastic.opaque_generic"),
            )
        # Light solid drip plate (source uses a perforated mesh; PERFORMANCE).
        tray.visual(
            Box((0.150 * sx, w - 0.018, 0.005)),
            origin=Origin(xyz=(0.100 * sx, 0.0, 0.070)),
            material=mats["metal"],
            name="drip_plate", material_class_id="metal.patterned_sheet_panel",
        )
        tray.visual(
            Box((0.008, w, 0.052)),
            origin=Origin(xyz=(0.182 * sx, 0.0, 0.034)),
            material=mats["core"],
            name="tray_front_lip", material_class_id=("metal.stainless_matte" if r.palette_style in {"gloss_black_stainless", "matte_graphite", "cream_retro", "brushed_inox"} else "plastic.opaque_glossy_molded"),
        )
        origin = Origin(xyz=(0.0, 0.0, 0.0))
        mass = 0.25
        inert_box = Box((0.18 * sx, w, 0.07))
        inert_o = Origin(xyz=(0.10 * sx, 0.0, 0.035))
    else:
        w = r.width - 0.04
        tray.visual(
            Box((0.11, w, 0.006)),
            origin=Origin(xyz=(0.055, 0.0, 0.003)),
            material=mats["trim"],
            name="tray_floor", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"gloss_black_stainless", "cream_retro", "red_accent"} else "plastic.opaque_generic"),
        )
        tray.visual(
            Box((0.008, w, 0.035)),
            origin=Origin(xyz=(0.106, 0.0, 0.020)),
            material=mats["trim"],
            name="tray_front_wall", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"gloss_black_stainless", "cream_retro", "red_accent"} else "plastic.opaque_generic"),
        )
        tray.visual(
            Box((0.008, w, 0.035)),
            origin=Origin(xyz=(0.004, 0.0, 0.020)),
            material=mats["trim"],
            name="tray_rear_wall", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"gloss_black_stainless", "cream_retro", "red_accent"} else "plastic.opaque_generic"),
        )
        for sgn, tag in ((1.0, "left"), (-1.0, "right")):
            tray.visual(
                Box((0.105, 0.006, 0.035)),
                origin=Origin(xyz=(0.054, sgn * (r.width / 2.0 - 0.023), 0.020)),
                material=mats["trim"],
                name=f"tray_{tag}_wall", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"gloss_black_stainless", "cream_retro", "red_accent"} else "plastic.opaque_generic"),
            )
        tray.visual(
            Box((0.100, w - 0.02, 0.004)),
            origin=Origin(xyz=(0.054, 0.0, 0.038)),
            material=mats["metal"],
            name="drip_plate", material_class_id="metal.patterned_sheet_panel",
        )
        tray.visual(
            Box((0.006, 0.06, 0.020)),
            origin=Origin(xyz=(0.113, 0.0, 0.028)),
            material=mats["silver"],
            name="tray_front_lip", material_class_id=("metal.brushed_silver" if r.palette_style == "brushed_inox" else "metal.chrome_polished"),
        )
        origin = Origin(xyz=(r.x_front - 0.12, 0.0, 0.015))
        mass = 0.12
        inert_box = Box((0.11, w, 0.04))
        inert_o = Origin(xyz=(0.055, 0.0, 0.02))
    tray.inertial = Inertial.from_geometry(inert_box, mass=mass, origin=inert_o)
    model.articulation(
        "body_to_tray",
        ArticulationType.PRISMATIC,
        parent=body,
        child=tray,
        origin=origin,
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(
            effort=30.0, velocity=0.2, lower=0.0, upper=r.tray_travel
        ),
    )
    return tray


def _emit_spout(model, r: ResolvedCoffeeMachineConfig, body, mats):
    """Double-nozzle spout block. PRISMATIC -Z (lowers to the cup). super_auto."""
    sx = r.depth / SA_DEPTH
    sz = r.height / SA_HEIGHT
    spout = model.part("spout_block")
    spout.visual(
        Box((0.058, 0.092, 0.075)),
        origin=Origin(xyz=(0.0, 0.0, -0.0375)),
        material=mats["trim"],
        name="spout_housing", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"gloss_black_stainless", "cream_retro", "red_accent"} else "plastic.opaque_generic"),
    )
    for sgn, tag in ((1.0, "left"), (-1.0, "right")):
        spout.visual(
            Cylinder(radius=0.0065, length=0.030),
            origin=Origin(xyz=(0.012, sgn * 0.020, -0.090)),
            material=mats["metal"],
            name=f"{tag}_nozzle", material_class_id="metal.stainless_matte",
        )
    spout.inertial = Inertial.from_geometry(
        Box((0.058, 0.092, 0.12)), mass=0.08, origin=Origin(xyz=(0.0, 0.0, -0.06))
    )
    model.articulation(
        "body_to_spout",
        ArticulationType.PRISMATIC,
        parent=body,
        child=spout,
        origin=Origin(xyz=(0.146 * sx, 0.0, 0.250 * sz)),
        axis=(0.0, 0.0, -1.0),
        motion_limits=MotionLimits(
            effort=20.0, velocity=0.1, lower=0.0, upper=r.spout_travel
        ),
    )
    return spout


def _emit_wand(model, r: ResolvedCoffeeMachineConfig, body, mats):
    """Steam wand. REVOLUTE about a vertical axis (~60 deg). super-auto / pf."""
    sx = r.depth / SA_DEPTH
    sz = r.height / SA_HEIGHT
    hy = r.width / 2.0
    wand = model.part("steam_wand")
    wand.visual(
        Cylinder(radius=0.012, length=0.030),
        origin=Origin(xyz=(0.0, 0.0, -0.008)),
        material=mats["trim"],
        name="pivot_knuckle", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"gloss_black_stainless", "cream_retro", "red_accent"} else "plastic.opaque_generic"),
    )
    lean = 0.28
    d = (0.0, math.sin(lean), -math.cos(lean))
    top = (0.0, 0.003, -0.020)
    tube_rpy = (math.pi + lean, 0.0, 0.0)
    wand.visual(
        Cylinder(radius=0.0055, length=0.130),
        origin=Origin(
            xyz=(top[0] + 0.065 * d[0], top[1] + 0.065 * d[1], top[2] + 0.065 * d[2]),
            rpy=tube_rpy,
        ),
        material=mats["metal"],
        name="wand_tube", material_class_id="metal.stainless_matte",
    )
    wand.visual(
        Cylinder(radius=0.0075, length=0.040),
        origin=Origin(
            xyz=(top[0] + 0.145 * d[0], top[1] + 0.145 * d[1], top[2] + 0.145 * d[2]),
            rpy=tube_rpy,
        ),
        material=mats["trim"],
        name="frother_sleeve", material_class_id="rubber.smooth_plain",
    )
    wand.inertial = Inertial.from_geometry(
        Cylinder(radius=0.012, length=0.18), mass=0.05, origin=Origin(xyz=(0.0, 0.06, -0.08))
    )
    model.articulation(
        "body_to_wand",
        ArticulationType.REVOLUTE,
        parent=body,
        child=wand,
        origin=Origin(xyz=(0.085 * sx, hy + 0.018, 0.285 * sz)),
        axis=(0.0, 0.0, -1.0),
        motion_limits=MotionLimits(
            effort=5.0, velocity=2.0, lower=0.0, upper=r.wand_swing
        ),
    )
    return wand


# ===========================================================================
# Slot A: portafilter brew group (fixed group head + twist-lock portafilter).
# ===========================================================================
def _emit_portafilter_group(model, r: ResolvedCoffeeMachineConfig, body, mats):
    sx = r.depth / SA_DEPTH
    sz = r.height / SA_HEIGHT
    gh_x = GH_X * sx
    gh_z = GH_Z * sz
    gh = model.part("group_head")
    gh.visual(
        Cylinder(radius=0.034, length=GH_LOCK_H),
        origin=Origin(xyz=(0.0, 0.0, -GH_LOCK_H / 2.0)),
        material=mats["brass"],
        name="gh_lock_ring", material_class_id="metal.brass_polished",
    )
    gh.visual(
        Cylinder(radius=0.030, length=GH_BODY_H),
        origin=Origin(xyz=(0.0, 0.0, GH_BODY_H / 2.0)),
        material=mats["brass"],
        name="gh_body", material_class_id="metal.brass_polished",
    )
    gh.visual(
        Cylinder(radius=0.038, length=GH_FLANGE_H),
        origin=Origin(xyz=(0.0, 0.0, GH_BODY_H + GH_FLANGE_H / 2.0)),
        material=mats["brass"],
        name="gh_flange", material_class_id="metal.brass_polished",
    )
    gh.inertial = Inertial.from_geometry(
        Cylinder(radius=0.038, length=GH_BODY_H + GH_FLANGE_H),
        mass=0.20,
        origin=Origin(xyz=(0.0, 0.0, GH_BODY_H / 2.0)),
    )
    model.articulation(
        "body_to_group_head",
        ArticulationType.FIXED,
        parent=body,
        child=gh,
        origin=Origin(xyz=(gh_x, 0.0, gh_z)),
    )

    pf = model.part("portafilter")
    pf.visual(
        Cylinder(radius=0.029, length=0.024),
        origin=Origin(xyz=(0.0, 0.0, -0.012)),
        material=mats["metal"],
        name="pf_basket", material_class_id="metal.stainless_matte",
    )
    pf.visual(
        Cylinder(radius=0.035, length=0.006),
        origin=Origin(xyz=(0.0, 0.0, 0.003)),
        material=mats["metal"],
        name="pf_rim", material_class_id="metal.stainless_matte",
    )
    for i in range(2):
        y_sign = 1.0 if i == 0 else -1.0
        pf.visual(
            Box((0.012, 0.010, 0.005)),
            origin=Origin(xyz=(0.0, y_sign * 0.034, 0.004)),
            material=mats["metal"],
            name=f"pf_ear_{i}", material_class_id="metal.stainless_matte",
        )
    pf.visual(
        Box((0.016, 0.024, 0.018)),
        origin=Origin(xyz=(0.0, -0.035, -0.009)),
        material=mats["metal"],
        name="pf_handle_lug", material_class_id="metal.stainless_matte",
    )
    pf.visual(
        Cylinder(radius=0.006, length=0.090),
        origin=Origin(xyz=(0.0, -0.080, -0.012), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["metal"],
        name="pf_handle_shaft", material_class_id="metal.stainless_matte",
    )
    pf.visual(
        Cylinder(radius=0.010, length=0.045),
        origin=Origin(xyz=(0.0, -0.130, -0.016), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["trim"],
        name="pf_handle_grip", material_class_id="rubber.smooth_plain",
    )
    pf.inertial = Inertial.from_geometry(
        Box((0.04, 0.16, 0.04)), mass=0.12, origin=Origin(xyz=(0.0, -0.06, -0.01))
    )
    model.articulation(
        "body_to_portafilter",
        ArticulationType.REVOLUTE,
        parent=body,
        child=pf,
        origin=Origin(xyz=(gh_x, 0.0, PF_Z * sz)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(
            effort=8.0, velocity=2.0, lower=0.0, upper=PF_LOCK_SWING
        ),
    )
    return gh, pf


# ===========================================================================
# Slot A: pod capsule flap (REVOLUTE, rear-top hinge).
# ===========================================================================
def _emit_capsule_flap(model, r: ResolvedCoffeeMachineConfig, body, mats):
    flap = model.part("capsule_flap")
    w = r.width
    flap.visual(
        Box((0.14, w - 0.04, 0.008)),
        origin=Origin(xyz=(0.07, 0.0, 0.004)),
        material=mats["body"],
        name="flap_plate", material_class_id=("metal.stainless_matte" if r.palette_style in {"gloss_black_stainless", "matte_graphite", "cream_retro", "brushed_inox"} else "plastic.opaque_glossy_molded"),
    )
    flap.visual(
        Box((0.012, 0.05, 0.006)),
        origin=Origin(xyz=(0.135, 0.0, 0.008)),
        material=mats["silver"],
        name="flap_grip", material_class_id=("metal.brushed_silver" if r.palette_style == "brushed_inox" else "metal.chrome_polished"),
    )
    flap.visual(
        Cylinder(radius=0.004, length=w - 0.04),
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["silver"],
        name="flap_hinge_pin", material_class_id=("metal.brushed_silver" if r.palette_style == "brushed_inox" else "metal.chrome_polished"),
    )
    flap.inertial = Inertial.from_geometry(
        Box((0.14, w - 0.04, 0.02)), mass=0.05, origin=Origin(xyz=(0.07, 0.0, 0.0))
    )
    model.articulation(
        "body_to_flap",
        ArticulationType.REVOLUTE,
        parent=body,
        child=flap,
        origin=Origin(xyz=(r.x_rear, 0.0, r.deck_top_z)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(
            effort=3.0, velocity=2.0, lower=0.0, upper=_clamp(r.lid_open, 1.0, math.pi * 0.95)
        ),
    )
    return flap


# ===========================================================================
# Slot B: hopper lid (super_automatic only).
# ===========================================================================
def _emit_rear_hinge_lid(model, r: ResolvedCoffeeMachineConfig, body, mats):
    sz = r.height / SA_HEIGHT
    deck_z = r.deck_top_z
    lid = model.part("hopper_lid")
    # Plate bottom dips ~2mm below the hinge line so it seats on (embeds into)
    # the top deck with no floating gap (closed-lid overlap is allowed).
    lid.visual(
        Box((0.120, 0.210, 0.012)),
        origin=Origin(xyz=(0.060, 0.0, 0.004)),
        material=mats["trim"],
        name="lid_plate", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"gloss_black_stainless", "cream_retro", "red_accent"} else "plastic.opaque_generic"),
    )
    lid.visual(
        Box((0.018, 0.080, 0.010)),
        origin=Origin(xyz=(0.111, 0.0, 0.011)),
        material=mats["trim"],
        name="lid_grip_bar", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"gloss_black_stainless", "cream_retro", "red_accent"} else "plastic.opaque_generic"),
    )
    lid.inertial = Inertial.from_geometry(
        Box((0.12, 0.21, 0.02)), mass=0.08, origin=Origin(xyz=(0.06, 0.0, 0.004))
    )
    model.articulation(
        "deck_to_hopper_lid",
        ArticulationType.REVOLUTE,
        parent=body,
        child=lid,
        origin=Origin(xyz=(r.x_rear, 0.0, deck_z)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=3.0, velocity=2.0, lower=0.0, upper=r.lid_open),
    )
    return lid


def _emit_side_hinge_lid(model, r: ResolvedCoffeeMachineConfig, body, mats):
    deck_z = r.deck_top_z
    hy = r.width / 2.0
    # Hinge on the rear-left deck corner. The plate is centered over the rear
    # deck hopper zone (same X coverage as the rear-hinge lid, clear of the
    # front cup-warming grid) and extends -Y toward the right free edge.
    lid_hinge_x = r.x_rear + 0.055
    lid_hinge_y = hy - 0.015
    lid = model.part("hopper_lid")
    # Plate bottom dips ~2mm below the hinge line so it seats on (embeds into)
    # the top deck.
    plate_w = min(0.210, 2.0 * hy - 0.02)
    lid.visual(
        Box((0.110, plate_w, 0.012)),
        origin=Origin(xyz=(0.0, -plate_w / 2.0, 0.004)),
        material=mats["trim"],
        name="lid_plate", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"gloss_black_stainless", "cream_retro", "red_accent"} else "plastic.opaque_generic"),
    )
    lid.visual(
        Box((0.080, 0.018, 0.010)),
        origin=Origin(xyz=(0.0, -(plate_w - 0.009), 0.011)),
        material=mats["trim"],
        name="lid_grip_bar", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"gloss_black_stainless", "cream_retro", "red_accent"} else "plastic.opaque_generic"),
    )
    lid.inertial = Inertial.from_geometry(
        Box((0.11, plate_w, 0.02)), mass=0.08, origin=Origin(xyz=(0.0, -plate_w / 2.0, 0.004))
    )
    model.articulation(
        "deck_to_hopper_lid",
        ArticulationType.REVOLUTE,
        parent=body,
        child=lid,
        origin=Origin(xyz=(lid_hinge_x, lid_hinge_y, deck_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=3.0, velocity=2.0, lower=0.0, upper=r.lid_open),
    )
    return lid


def _emit_removable_canister(model, r: ResolvedCoffeeMachineConfig, body, mats):
    deck_z = r.deck_top_z
    # --- body guide bay (4 walls + recessed floor) ---
    guide_base_z = deck_z + GUIDE_H / 2.0
    half_w = HOPPER_W / 2.0 + HOPPER_WALL + GUIDE_T / 2.0 + 0.002
    half_d = HOPPER_D / 2.0 + HOPPER_WALL + GUIDE_T / 2.0 + 0.002
    for sgn, tag in ((1.0, "front"), (-1.0, "rear")):
        body.visual(
            Box((GUIDE_T, HOPPER_D + 2 * HOPPER_WALL + GUIDE_T, GUIDE_H)),
            origin=Origin(xyz=(HOPPER_CENTER_X + sgn * half_w, 0.0, guide_base_z)),
            material=mats["trim"],
            name=f"hopper_guide_{tag}", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"gloss_black_stainless", "cream_retro", "red_accent"} else "plastic.opaque_generic"),
        )
    for sgn, tag in ((1.0, "left"), (-1.0, "right")):
        body.visual(
            Box((HOPPER_W + 2 * HOPPER_WALL + GUIDE_T, GUIDE_T, GUIDE_H)),
            origin=Origin(xyz=(HOPPER_CENTER_X, sgn * half_d, guide_base_z)),
            material=mats["trim"],
            name=f"hopper_guide_{tag}", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"gloss_black_stainless", "cream_retro", "red_accent"} else "plastic.opaque_generic"),
        )
    body.visual(
        Box((HOPPER_W + 2 * HOPPER_WALL, HOPPER_D + 2 * HOPPER_WALL, 0.004)),
        origin=Origin(xyz=(HOPPER_CENTER_X, 0.0, deck_z - 0.002)),
        material=mats["trim"],
        name="hopper_bay_floor", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"gloss_black_stainless", "cream_retro", "red_accent"} else "plastic.opaque_generic"),
    )

    # --- lift-out canister part (hollow cadquery shell, coarse tessellation) ---
    canister = model.part("hopper_canister")
    canister_body = (
        cq.Workplane("XY")
        .box(HOPPER_W, HOPPER_D, HOPPER_H)
        .edges("|Z")
        .fillet(0.008)
        .faces(">Z")
        .shell(-HOPPER_WALL)
    )
    canister.visual(
        mesh_from_cadquery(
            canister_body,
            "canister_shell",
            tolerance=0.004,
            angular_tolerance=0.6,
        ),
        origin=Origin(xyz=(0.0, 0.0, HOPPER_H / 2.0)),
        material=mats["body"],
        name="canister_shell", material_class_id=("metal.stainless_matte" if r.palette_style in {"gloss_black_stainless", "matte_graphite", "cream_retro", "brushed_inox"} else "plastic.opaque_glossy_molded"),
    )
    canister.visual(
        Box((HOPPER_W - 0.002, HOPPER_D - 0.002, 0.006)),
        origin=Origin(xyz=(0.0, 0.0, HOPPER_H + 0.003)),
        material=mats["trim"],
        name="canister_lid_plate", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"gloss_black_stainless", "cream_retro", "red_accent"} else "plastic.opaque_generic"),
    )
    canister.visual(
        Box((0.040, 0.015, 0.012)),
        origin=Origin(xyz=(0.0, 0.0, HOPPER_H + 0.012)),
        material=mats["trim"],
        name="canister_grip", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"gloss_black_stainless", "cream_retro", "red_accent"} else "plastic.opaque_generic"),
    )
    canister.visual(
        Box((HOPPER_W - 0.010, 0.008, 0.004)),
        origin=Origin(xyz=(0.0, 0.0, -0.002)),
        material=mats["trim"],
        name="canister_align_rib", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"gloss_black_stainless", "cream_retro", "red_accent"} else "plastic.opaque_generic"),
    )
    canister.inertial = Inertial.from_geometry(
        Box((HOPPER_W, HOPPER_D, HOPPER_H)),
        mass=0.10,
        origin=Origin(xyz=(0.0, 0.0, HOPPER_H / 2.0)),
    )
    model.articulation(
        "body_to_hopper",
        ArticulationType.PRISMATIC,
        parent=body,
        child=canister,
        origin=Origin(xyz=(HOPPER_CENTER_X, 0.0, deck_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(
            effort=15.0, velocity=0.15, lower=0.0, upper=r.canister_lift
        ),
    )
    return canister


# ===========================================================================
# Slot C: water tank (super_automatic / portafilter).
# ===========================================================================
def _emit_side_removable_tank(model, r: ResolvedCoffeeMachineConfig, body, mats):
    dock_y = -r.width / 2.0
    # --- right-flank dock bay (back plate + 2 rails) on body ---
    body.visual(
        Box((TANK_DX + 0.008, 0.004, TANK_DZ + 0.008)),
        origin=Origin(xyz=(TANK_X_C, dock_y - 0.002, TANK_Z_C)),
        material=mats["trim"],
        name="tank_bay_plate", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"gloss_black_stainless", "cream_retro", "red_accent"} else "plastic.opaque_generic"),
    )
    for i, z_off in enumerate((-TANK_DZ / 2.0 - 0.003, TANK_DZ / 2.0 + 0.003)):
        body.visual(
            Box((TANK_DX + 0.006, 0.006, 0.006)),
            origin=Origin(xyz=(TANK_X_C, dock_y - 0.003, TANK_Z_C + z_off)),
            material=mats["body"],
            name=f"tank_rail_{i}", material_class_id=("metal.stainless_matte" if r.palette_style in {"gloss_black_stainless", "matte_graphite", "cream_retro", "brushed_inox"} else "plastic.opaque_glossy_molded"),
        )
    # --- tank part ---
    tank = model.part("water_tank")
    tank.visual(
        Box((TANK_DX, TANK_DY, TANK_DZ)),
        origin=Origin(xyz=(0.0, -TANK_DY / 2.0, 0.0)),
        material=mats["tank"],
        name="tank_body", material_class_id="plastic.frosted_translucent",
    )
    tank.visual(
        Box((TANK_DX - 0.004, TANK_DY - 0.004, 0.010)),
        origin=Origin(xyz=(0.0, -TANK_DY / 2.0, TANK_DZ / 2.0 + 0.005)),
        material=mats["trim"],
        name="tank_cap", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"gloss_black_stainless", "cream_retro", "red_accent"} else "plastic.opaque_generic"),
    )
    tank.visual(
        Box((0.030, 0.006, 0.060)),
        origin=Origin(xyz=(0.0, -TANK_DY - 0.003, 0.040)),
        material=mats["trim"],
        name="tank_handle", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"gloss_black_stainless", "cream_retro", "red_accent"} else "plastic.opaque_generic"),
    )
    tank.inertial = Inertial.from_geometry(
        Box((TANK_DX, TANK_DY, TANK_DZ)),
        mass=0.20,
        origin=Origin(xyz=(0.0, -TANK_DY / 2.0, 0.0)),
    )
    model.articulation(
        "body_to_tank",
        ArticulationType.PRISMATIC,
        parent=body,
        child=tank,
        origin=Origin(xyz=(TANK_X_C, dock_y, TANK_Z_C)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(
            effort=25.0, velocity=0.15, lower=0.0, upper=r.tank_travel
        ),
    )
    return tank


def _emit_top_reservoir_tank(model, r: ResolvedCoffeeMachineConfig, body, mats):
    deck_z = r.deck_top_z
    # --- rear cradle (platform + back wall + 2 side walls) on body ---
    # The platform front edge embeds into the body rear face so the cradle is
    # always grounded (the dock X-center follows the body rear, not a fixed
    # literal -- otherwise depth-scaling floats it off the body).
    res_x = r.x_rear - 0.035
    plat_len = 0.070
    plat_front = res_x + plat_len / 2.0  # forward edge -> embeds in core_shell
    # ensure the platform overlaps the body rear by >=5 mm.
    if plat_front < r.x_rear + 0.006:
        res_x = r.x_rear + 0.006 - plat_len / 2.0
    body.visual(
        Box((plat_len, 0.140, 0.010)),
        origin=Origin(xyz=(res_x, 0.0, deck_z - 0.005)),
        material=mats["body"],
        name="tank_bay_platform", material_class_id=("metal.stainless_matte" if r.palette_style in {"gloss_black_stainless", "matte_graphite", "cream_retro", "brushed_inox"} else "plastic.opaque_glossy_molded"),
    )
    body.visual(
        Box((0.006, 0.140, 0.080)),
        origin=Origin(xyz=(res_x - 0.032, 0.0, deck_z + 0.040)),
        material=mats["body"],
        name="tank_bay_back_wall", material_class_id=("metal.stainless_matte" if r.palette_style in {"gloss_black_stainless", "matte_graphite", "cream_retro", "brushed_inox"} else "plastic.opaque_glossy_molded"),
    )
    for i, sgn in enumerate((1.0, -1.0)):
        tag = ("left", "right")[i]
        body.visual(
            Box((plat_len, 0.006, 0.080)),
            origin=Origin(xyz=(res_x, sgn * 0.067, deck_z + 0.040)),
            material=mats["body"],
            name=f"tank_bay_{tag}_wall", material_class_id=("metal.stainless_matte" if r.palette_style in {"gloss_black_stainless", "matte_graphite", "cream_retro", "brushed_inox"} else "plastic.opaque_glossy_molded"),
        )
    # --- tank part (extruded vessel + visible water fill + lid + grip) ---
    tank = model.part("water_tank")
    vessel_profile = rounded_rect_profile(0.056, 0.120, 0.005)
    tank.visual(
        mesh_from_geometry(
            ExtrudeGeometry.from_z0(vessel_profile, 0.160, cap=True), "tank_vessel"
        ),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material=mats["tank"],
        name="tank_vessel", material_class_id="plastic.frosted_translucent",
    )
    water_profile = rounded_rect_profile(0.048, 0.112, 0.004)
    tank.visual(
        mesh_from_geometry(
            ExtrudeGeometry.from_z0(water_profile, 0.100, cap=True), "tank_water_fill"
        ),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material=mats["water"],
        name="tank_water_fill", material_class_id="liquid.water_wave_foam",
    )
    tank.visual(
        Box((0.060, 0.124, 0.008)),
        origin=Origin(xyz=(0.0, 0.0, 0.164)),
        material=mats["body"],
        name="tank_lid", material_class_id=("metal.stainless_matte" if r.palette_style in {"gloss_black_stainless", "matte_graphite", "cream_retro", "brushed_inox"} else "plastic.opaque_glossy_molded"),
    )
    tank.visual(
        Box((0.032, 0.012, 0.010)),
        origin=Origin(xyz=(0.0, 0.0, 0.173)),
        material=mats["trim"],
        name="tank_grip", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"gloss_black_stainless", "cream_retro", "red_accent"} else "plastic.opaque_generic"),
    )
    tank.inertial = Inertial.from_geometry(
        Box((0.056, 0.120, 0.160)), mass=0.20, origin=Origin(xyz=(0.0, 0.0, 0.08))
    )
    model.articulation(
        "body_to_tank",
        ArticulationType.PRISMATIC,
        parent=body,
        child=tank,
        origin=Origin(xyz=(res_x, 0.0, deck_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(
            effort=15.0, velocity=0.2, lower=0.0, upper=r.tank_travel
        ),
    )
    return tank


_HOPPER_BUILDERS = {
    "rear_hinge": _emit_rear_hinge_lid,
    "side_hinge": _emit_side_hinge_lid,
    "removable_canister": _emit_removable_canister,
}
_TANK_BUILDERS = {
    "side_removable": _emit_side_removable_tank,
    "top_reservoir": _emit_top_reservoir_tank,
}


# ===========================================================================
# Build
# ===========================================================================
def build_coffee_machine(
    config: CoffeeMachineConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        key: model.material(f"coffee_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in PALETTES[r.palette_style].items()
    }

    if r.brew_type == "pod_capsule":
        body = _build_pod_body(model, r, mats)
        _emit_dial(model, r, body, mats)
        _emit_capsule_flap(model, r, body, mats)
        _emit_tray(model, r, body, mats)
    else:
        body = _build_box_body(model, r, mats)
        _emit_dial(model, r, body, mats)
        _emit_tray(model, r, body, mats)
        _emit_wand(model, r, body, mats)
        if r.brew_type == "super_automatic":
            _emit_spout(model, r, body, mats)
            _HOPPER_BUILDERS[r.hopper_lid](model, r, body, mats)
        else:  # portafilter
            _emit_portafilter_group(model, r, body, mats)
        # Slot C (super_automatic / portafilter). internal -> no part / joint.
        if r.water_tank in _TANK_BUILDERS:
            _TANK_BUILDERS[r.water_tank](model, r, body, mats)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_coffee_machine(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_coffee_machine(config_from_seed(seed), assets=assets)


# ===========================================================================
# Tests
# ===========================================================================
def run_coffee_machine_tests(
    object_model: ArticulatedObject,
    config: CoffeeMachineConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    body = object_model.get_part("body")
    dial = object_model.get_part("selection_dial")

    part_names = {p.name for p in object_model.parts}
    articulation_names = {a.name for a in object_model.articulations}

    # Removable service items detach from the body when lifted/slid out.
    for removable in ("drip_tray", "water_tank", "hopper_canister"):
        if removable in part_names:
            ctx.allow_isolated_part(
                object_model.get_part(removable),
                reason=f"{removable} lifts or slides free of the machine body for service",
            )

    # Hopper lid swings close past the tank-bay wall while opening.
    if "hopper_lid" in part_names:
        ctx.allow_overlap(
            object_model.get_part("hopper_lid"), body,
            reason="hopper lid swings close past the tank-bay wall while opening",
        )
    # At full tilt the opened lid stands beside the rear reservoir tank.
    if "hopper_lid" in part_names and "water_tank" in part_names:
        ctx.allow_overlap(
            object_model.get_part("hopper_lid"),
            object_model.get_part("water_tank"),
            reason="opened hopper lid stands close past the adjacent water tank",
        )

    # ---- Captured-pin / capture-fit allowances (element-scoped). ----
    if r.is_box_body:
        ctx.allow_overlap(
            dial, body, elem_a="dial_stem", elem_b="fascia_panel",
            reason="Dial shaft is intentionally inserted through the fascia panel.",
        )
        wand = object_model.get_part("steam_wand")
        ctx.allow_overlap(
            wand, body, elem_a="pivot_knuckle", elem_b="wand_boss",
            reason="Wand knuckle is intentionally captured on the side pivot boss.",
        )
        tray = object_model.get_part("drip_tray")
        for tray_elem in ("tray_rear_wall", "tray_floor"):
            ctx.allow_overlap(
                tray, body, elem_a=tray_elem, elem_b="base_block",
                reason="Docked drip-tray slides under the body base block so the seated tray reads flush.",
            )
    else:
        ctx.allow_overlap(
            dial, body, elem_a="dial_stem", elem_b="front_fascia",
            reason="Dial stem is intentionally inserted through the front fascia.",
        )
        ctx.allow_overlap(
            dial, body, elem_a="dial_stem", elem_b="body_shell",
            reason="Dial stem is intentionally inserted through the body shell wall.",
        )

    if r.brew_type == "super_automatic":
        spout = object_model.get_part("spout_block")
        ctx.allow_overlap(
            spout, body, elem_a="spout_housing", elem_b="spout_rail",
            reason="Spout carriage is intentionally captured on the vertical guide rail.",
        )
        if r.hopper_lid == "rear_hinge" or r.hopper_lid == "side_hinge":
            ctx.allow_overlap(
                object_model.get_part("hopper_lid"), body,
                elem_a="lid_plate", elem_b="top_deck",
                reason="Closed hopper lid seats on (embeds slightly into) the top deck.",
            )
            # The side-hinge lid plate's rear edge sits at the body rear, so when
            # the top_reservoir cradle is mounted there its left/right walls just
            # brush the plate corner (a real rear-deck adjacency).
            if r.hopper_lid == "side_hinge" and r.water_tank == "top_reservoir":
                for tag in ("left", "right"):
                    ctx.allow_overlap(
                        object_model.get_part("hopper_lid"), body,
                        elem_a="lid_plate", elem_b=f"tank_bay_{tag}_wall",
                        reason="Side-hinge lid rear edge brushes the rear reservoir cradle wall.",
                    )
        elif r.hopper_lid == "removable_canister":
            canister = object_model.get_part("hopper_canister")
            ctx.allow_overlap(
                canister, body, elem_a="canister_align_rib", elem_b="hopper_bay_floor",
                reason="Canister alignment rib is intentionally seated in the bay floor recess.",
            )
            for tag in ("front", "rear", "left", "right"):
                ctx.allow_overlap(
                    canister, body, elem_a="canister_shell", elem_b=f"hopper_guide_{tag}",
                    reason="Canister shell rides inside the guide-bay walls (captured slide fit).",
                )
    elif r.brew_type == "portafilter":
        gh = object_model.get_part("group_head")
        pf = object_model.get_part("portafilter")
        ctx.allow_overlap(
            gh, body, elem_a="gh_body", elem_b="group_mount_boss",
            reason="Group head cylinder seats against the body mounting boss.",
        )
        ctx.allow_overlap(
            gh, body, elem_a="gh_lock_ring", elem_b="group_mount_boss",
            reason="Group head lock ring seats onto the forward mounting-boss stub.",
        )
        for pf_elem in ("pf_basket", "pf_rim"):
            ctx.allow_overlap(
                pf, body, elem_a=pf_elem, elem_b="group_mount_boss",
                reason="Portafilter nests up against the mounting-boss stub under the group head.",
            )
        ctx.allow_overlap(
            pf, gh, elem_a="pf_rim", elem_b="gh_lock_ring",
            reason="Portafilter rim collar docks into the group head lock ring.",
        )
        ctx.allow_overlap(
            pf, gh, elem_a="pf_basket", elem_b="gh_lock_ring",
            reason="Portafilter basket aligns up into the group head lock ring.",
        )
        for ear in ("pf_ear_0", "pf_ear_1"):
            ctx.allow_overlap(
                pf, gh, elem_a=ear, elem_b="gh_lock_ring",
                reason="Portafilter locking ear engages the group head lock ring slot.",
            )
    else:  # pod_capsule
        flap = object_model.get_part("capsule_flap")
        ctx.allow_overlap(
            flap, body, elem_a="flap_hinge_pin", elem_b="flap_hinge_boss",
            reason="Flap hinge pin is intentionally captured in the body hinge boss.",
        )
        ctx.allow_overlap(
            flap, body, elem_a="flap_plate", elem_b="flap_hinge_boss",
            reason="Flap plate rear edge wraps the hinge boss (captured hinge barrel).",
        )
        ctx.allow_overlap(
            flap, body, elem_a="flap_plate", elem_b="capsule_slot",
            reason="Closed flap covers the capsule slot on the top deck.",
        )

    # Slot C captured allowances (super_automatic / portafilter).
    if r.water_tank == "side_removable":
        tank = object_model.get_part("water_tank")
        ctx.allow_overlap(
            tank, body, elem_a="tank_body", elem_b="tank_bay_plate",
            reason="Tank body rests against the dock back plate when seated.",
        )
        for i in range(2):
            ctx.allow_overlap(
                tank, body, elem_a="tank_body", elem_b=f"tank_rail_{i}",
                reason="Tank body slides between the dock guide rails (captured slide fit).",
            )
    elif r.water_tank == "top_reservoir":
        tank = object_model.get_part("water_tank")
        ctx.allow_overlap(
            tank, body, elem_a="tank_vessel", elem_b="tank_bay_platform",
            reason="Tank vessel rests on the rear cradle platform when seated.",
        )

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_joint_mating_has_gap()

    # ---- slot_choices recorded and consistent. ----
    ctx.check(
        "slot_choices recorded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    # ---- Single root body + grounding. ----
    roots = object_model.root_parts()
    ctx.check(
        "body is the single root",
        len(roots) == 1 and roots[0].name == "body",
        details=f"roots={[p.name for p in roots]}",
    )
    body_aabb = ctx.part_world_aabb(body)
    if body_aabb is not None:
        ctx.check(
            "machine grounded at z=0",
            abs(body_aabb[0][2]) < 1e-3,
            details=f"body zmin={body_aabb[0][2]:.5f}",
        )

    # ---- Selection dial: CONTINUOUS, unbounded, on every spine. ----
    dial_joint_name = "fascia_to_dial" if r.is_box_body else "body_to_dial"
    j_dial = object_model.get_articulation(dial_joint_name)
    ctx.check(
        "selection dial is CONTINUOUS and unbounded",
        j_dial.articulation_type == ArticulationType.CONTINUOUS
        and (j_dial.motion_limits is None or j_dial.motion_limits.upper is None),
        details=f"type={j_dial.articulation_type}",
    )
    # Off-axis pointer proves the dial actually spins.
    ptr_rest = ctx.part_element_world_aabb(dial, elem="dial_pointer")
    with ctx.pose({j_dial: math.pi}):
        ptr_half = ctx.part_element_world_aabb(dial, elem="dial_pointer")
    if ptr_rest is not None and ptr_half is not None:
        c_rest = (ptr_rest[0][1] + ptr_rest[1][1]) / 2.0
        c_half = (ptr_half[0][1] + ptr_half[1][1]) / 2.0
        ctx.check(
            "dial pointer sweeps across after a half turn",
            abs(c_rest - c_half) > 0.008,
            details=f"rest_cy={c_rest:.4f} half_cy={c_half:.4f}",
        )

    # ---- Drip tray: PRISMATIC +X on every spine, slides forward. ----
    j_tray = object_model.get_articulation("body_to_tray")
    ctx.check(
        "drip tray is PRISMATIC about +X",
        j_tray.articulation_type == ArticulationType.PRISMATIC and j_tray.axis[0] > 0.99,
        details=f"type={j_tray.articulation_type} axis={tuple(j_tray.axis)}",
    )
    tray = object_model.get_part("drip_tray")
    t0 = ctx.part_world_aabb(tray)
    with ctx.pose({j_tray: r.tray_travel}):
        t1 = ctx.part_world_aabb(tray)
    if t0 is not None and t1 is not None:
        ctx.check(
            "drip tray slides forward",
            t1[1][0] > t0[1][0] + 0.5 * r.tray_travel,
            details=f"rest_xmax={t0[1][0]:.4f} out_xmax={t1[1][0]:.4f}",
        )

    # ---- Brew-spine topology checks. ----
    if r.brew_type == "super_automatic":
        ctx.check(
            "super_automatic has spout_block + steam_wand",
            "spout_block" in part_names and "steam_wand" in part_names,
            details=str(sorted(part_names)),
        )
        j_spout = object_model.get_articulation("body_to_spout")
        ctx.check(
            "spout block is PRISMATIC about -Z (lowers to the cup)",
            j_spout.articulation_type == ArticulationType.PRISMATIC
            and abs(j_spout.axis[2]) > 0.99,
            details=f"type={j_spout.articulation_type} axis={tuple(j_spout.axis)}",
        )
        spout = object_model.get_part("spout_block")
        s0 = ctx.part_world_aabb(spout)
        with ctx.pose({j_spout: r.spout_travel}):
            s1 = ctx.part_world_aabb(spout)
        if s0 is not None and s1 is not None:
            ctx.check(
                "advancing the spout lowers the nozzles",
                s1[0][2] < s0[0][2] - 0.5 * r.spout_travel,
                details=f"rest_zmin={s0[0][2]:.4f} low_zmin={s1[0][2]:.4f}",
            )
        j_wand = object_model.get_articulation("body_to_wand")
        ctx.check(
            "steam wand is REVOLUTE about a vertical axis",
            j_wand.articulation_type == ArticulationType.REVOLUTE
            and abs(j_wand.axis[2]) > 0.99,
            details=f"type={j_wand.articulation_type} axis={tuple(j_wand.axis)}",
        )
    elif r.brew_type == "portafilter":
        ctx.check(
            "portafilter spine removes spout_block and hopper_lid",
            "spout_block" not in part_names and "hopper_lid" not in part_names,
            details=str(sorted(part_names)),
        )
        ctx.check(
            "portafilter spine has group_head + portafilter parts",
            "group_head" in part_names and "portafilter" in part_names,
            details=str(sorted(part_names)),
        )
        j_gh = object_model.get_articulation("body_to_group_head")
        j_pf = object_model.get_articulation("body_to_portafilter")
        ctx.check(
            "group head is FIXED and portafilter is REVOLUTE about +Z",
            j_gh.articulation_type == ArticulationType.FIXED
            and j_pf.articulation_type == ArticulationType.REVOLUTE
            and abs(j_pf.axis[2]) > 0.99,
            details=(
                f"gh={j_gh.articulation_type} "
                f"pf={j_pf.articulation_type} axis={tuple(j_pf.axis)}"
            ),
        )
        pf = object_model.get_part("portafilter")
        pf_aabb = ctx.part_world_aabb(pf)
        if pf_aabb is not None:
            ctx.check(
                "portafilter handle extends visibly to one side",
                (pf_aabb[1][1] - pf_aabb[0][1]) > 0.08,
                details=f"pf y-extent={pf_aabb[1][1] - pf_aabb[0][1]:.4f}",
            )
        grip_rest = ctx.part_element_world_aabb(pf, elem="pf_handle_grip")
        with ctx.pose({j_pf: PF_LOCK_SWING}):
            grip_turned = ctx.part_element_world_aabb(pf, elem="pf_handle_grip")
        if grip_rest is not None and grip_turned is not None:
            rest_cx = (grip_rest[0][0] + grip_rest[1][0]) / 2.0
            turned_cx = (grip_turned[0][0] + grip_turned[1][0]) / 2.0
            ctx.check(
                "portafilter handle swings forward when the joint turns",
                turned_cx > rest_cx + 0.02,
                details=f"rest_cx={rest_cx:.4f} turned_cx={turned_cx:.4f}",
            )
    else:  # pod_capsule
        ctx.check(
            "pod spine has capsule_flap, no hopper / no separable tank / no wand",
            "capsule_flap" in part_names
            and "hopper_canister" not in part_names
            and "hopper_lid" not in part_names
            and "steam_wand" not in part_names
            and "spout_block" not in part_names,
            details=str(sorted(part_names)),
        )
        # Slot B/C are spine defaults -> no separate water_tank part.
        ctx.check(
            "pod has no separable water_tank part (integrated tank visual)",
            "water_tank" not in part_names,
            details=str(sorted(part_names)),
        )
        j_flap = object_model.get_articulation("body_to_flap")
        ctx.check(
            "capsule flap is REVOLUTE about -Y (top rear hinge)",
            j_flap.articulation_type == ArticulationType.REVOLUTE
            and abs(j_flap.axis[1]) > 0.99,
            details=f"type={j_flap.articulation_type} axis={tuple(j_flap.axis)}",
        )
        flap = object_model.get_part("capsule_flap")
        f0 = ctx.part_world_aabb(flap)
        with ctx.pose({j_flap: r.lid_open * 0.8}):
            f1 = ctx.part_world_aabb(flap)
        if f0 is not None and f1 is not None:
            ctx.check(
                "opening the capsule flap raises its free edge",
                f1[1][2] > f0[1][2] + 0.02,
                details=f"closed_top={f0[1][2]:.4f} open_top={f1[1][2]:.4f}",
            )

    # ---- Hopper-lid topology (super_automatic only). ----
    if r.hopper_lid == "rear_hinge":
        j = object_model.get_articulation("deck_to_hopper_lid")
        ctx.check(
            "rear-hinge hopper lid is REVOLUTE about -Y",
            j.articulation_type == ArticulationType.REVOLUTE and abs(j.axis[1]) > 0.99,
            details=f"axis={tuple(j.axis)}",
        )
        lid = object_model.get_part("hopper_lid")
        l0 = ctx.part_world_aabb(lid)
        with ctx.pose({j: r.lid_open * 0.8}):
            l1 = ctx.part_world_aabb(lid)
        if l0 is not None and l1 is not None:
            ctx.check(
                "rear-hinge lid raises its free edge",
                l1[1][2] > l0[1][2] + 0.03,
                details=f"closed_top={l0[1][2]:.4f} open_top={l1[1][2]:.4f}",
            )
    elif r.hopper_lid == "side_hinge":
        j = object_model.get_articulation("deck_to_hopper_lid")
        ctx.check(
            "side-hinge hopper lid is REVOLUTE about +Z",
            j.articulation_type == ArticulationType.REVOLUTE and abs(j.axis[2]) > 0.99,
            details=f"axis={tuple(j.axis)}",
        )
    elif r.hopper_lid == "removable_canister":
        ctx.check(
            "removable canister is an independent part",
            "hopper_canister" in part_names,
            details=str(sorted(part_names)),
        )
        j = object_model.get_articulation("body_to_hopper")
        ctx.check(
            "removable canister is PRISMATIC about +Z",
            j.articulation_type == ArticulationType.PRISMATIC and abs(j.axis[2]) > 0.99,
            details=f"axis={tuple(j.axis)}",
        )
        canister = object_model.get_part("hopper_canister")
        c0 = ctx.part_world_position(canister)
        with ctx.pose({j: r.canister_lift}):
            c1 = ctx.part_world_position(canister)
        if c0 is not None and c1 is not None:
            ctx.check(
                "canister lifts straight up out of the bay",
                c1[2] > c0[2] + 0.5 * r.canister_lift,
                details=f"seated_z={c0[2]:.4f} lifted_z={c1[2]:.4f}",
            )

    # ---- Water-tank topology (super_automatic / portafilter). ----
    if r.water_tank == "internal":
        ctx.check(
            "internal tank has no separate water_tank part / joint",
            "water_tank" not in part_names and "body_to_tank" not in articulation_names,
            details=str(sorted(part_names)),
        )
    elif r.water_tank == "side_removable":
        j = object_model.get_articulation("body_to_tank")
        ctx.check(
            "side-removable tank is PRISMATIC about -Y",
            j.articulation_type == ArticulationType.PRISMATIC and abs(j.axis[1]) > 0.99,
            details=f"axis={tuple(j.axis)}",
        )
        tank = object_model.get_part("water_tank")
        k0 = ctx.part_world_position(tank)
        with ctx.pose({j: r.tank_travel}):
            k1 = ctx.part_world_position(tank)
        if k0 is not None and k1 is not None:
            ctx.check(
                "side tank slides out along -Y",
                k1[1] < k0[1] - 0.5 * r.tank_travel,
                details=f"seated_y={k0[1]:.4f} out_y={k1[1]:.4f}",
            )
    elif r.water_tank == "top_reservoir":
        j = object_model.get_articulation("body_to_tank")
        ctx.check(
            "top-reservoir tank is PRISMATIC about +Z",
            j.articulation_type == ArticulationType.PRISMATIC and abs(j.axis[2]) > 0.99,
            details=f"axis={tuple(j.axis)}",
        )
        tank = object_model.get_part("water_tank")
        k0 = ctx.part_world_position(tank)
        with ctx.pose({j: r.tank_travel}):
            k1 = ctx.part_world_position(tank)
        if k0 is not None and k1 is not None:
            ctx.check(
                "top reservoir lifts straight up",
                k1[2] > k0[2] + 0.5 * r.tank_travel,
                details=f"seated_z={k0[2]:.4f} lifted_z={k1[2]:.4f}",
            )

    return ctx.report()


__all__ = (
    "CoffeeMachineConfig",
    "ResolvedCoffeeMachineConfig",
    "build_coffee_machine",
    "build_seeded_coffee_machine",
    "config_from_seed",
    "resolve_config",
    "run_coffee_machine_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
