# SPDX-License-Identifier: Apache-2.0

"""Cartridge caulking gun (handheld sealant dispenser) modular template.

NOTE on the slug: ``caulking_gun`` here = a **handheld cartridge sealant /
caulk extrusion gun** (a cradle/frame holding a fixed cartridge, a squeeze
trigger, and a plunger rod that advances to extrude caulk), NOT a hot-glue gun
(no heated rod / power switch / chrome cone) and NOT a pressurized grease gun
(no hose / pump). Sourced from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/Handtools_Handtools_caulking_gun.md`` and the
``picture/Handtools/caulking gun`` 5-star pool (2 parents + 6 slot-fork
variants), all synced under ``data/records/``.

Structure (pattern = ``parallel_children``): a single root frame part holds the
main shell geometry and grip visual; three children parent directly to it:

  * ``cartridge`` (FIXED consumable, Rule 1 — seated, never articulates), or for
    ``sausage_tube`` a ``front_cap`` part (threaded nose cap that carries the
    nozzle in place of a rigid cartridge).
  * ``plunger`` (PRISMATIC +X — advances to extrude the caulk).
  * ``trigger`` (REVOLUTE +Y — the squeeze lever).

There are TWO coordinate families in the 5-star pool (spec §9):

  * **A family** — root part ``barrel_body``; geometry is authored about the
    barrel axis at z=0 then lifted by ``AXIS_Z`` so the rear-cap rim rests on
    the ground. The trigger pivot sits HIGH (axis + ~0.085). Short plunger
    travel (~0.060). Cradles: half_barrel / closed_barrel / sausage_tube. Grip:
    bracket_wing. Plungers: ratchet_jhook / ring_pull.
  * **B family** — root part ``frame``; geometry is authored directly at the
    barrel axis z=0 (no lift), grip hangs below. Trigger pivot sits LOW
    (~-0.040) or on TOP (inline). Long plunger travel (~0.180). Cradles:
    skeleton_halfpipe / rib_cage. Grips: pistol_grip / d_ring_loop /
    inline_handle. Plunger: thumb_plate.

``rib_cage`` carries a module-local ``rib_count`` multiplicity axis (N in
[3, 6], N=4 baseline) — N evenly-angled longitudinal ``rib_rod_{i}`` steel
visuals emitted via a shared geometry helper (Rule 1: non-moving visuals on the
frame, no per-rib joint). N is encoded into the slot_choice tuple as
``("rib_count", f"n{N}")``.

Compatibility gating (spec §9, first version = same-family-first): a cradle's
family pins the grip + plunger to the same family, so trigger pivots stay on
real hinge hardware and plunger travel stays in-bore. All hinge / shaft / seated
fits are captured geometry, so those joints omit ``MatingContract``
(grandfathered) and are guarded by the flat 0.015 m articulation-origin baseline
+ element-scoped ``allow_overlap`` (mirroring each source's run_tests block).
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
    Inertial,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
    mesh_from_geometry,
    tube_from_spline_points,
)

__modular__ = True

Cradle = Literal[
    "half_barrel",
    "closed_barrel",
    "sausage_tube",
    "skeleton_halfpipe",
    "rib_cage",
]
Grip = Literal["bracket_wing", "pistol_grip", "d_ring_loop", "inline_handle"]
PlungerDrive = Literal["ratchet_jhook", "thumb_plate", "ring_pull"]
PaletteStyle = Literal[
    "gunmetal_pro",
    "red_consumer",
    "blue_silicone",
    "aluminum_sausage",
    "industrial_grey",
]

CRADLES: tuple[Cradle, ...] = (
    "half_barrel",
    "closed_barrel",
    "sausage_tube",
    "skeleton_halfpipe",
    "rib_cage",
)
GRIPS: tuple[Grip, ...] = ("bracket_wing", "pistol_grip", "d_ring_loop", "inline_handle")
PLUNGER_DRIVES: tuple[PlungerDrive, ...] = ("ratchet_jhook", "thumb_plate", "ring_pull")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "gunmetal_pro",
    "red_consumer",
    "blue_silicone",
    "aluminum_sausage",
    "industrial_grey",
)

# Coordinate family per cradle (spec §9).
A_FAMILY_CRADLES: tuple[Cradle, ...] = ("half_barrel", "closed_barrel", "sausage_tube")
B_FAMILY_CRADLES: tuple[Cradle, ...] = ("skeleton_halfpipe", "rib_cage")

# Same-family grip / plunger pools (first-version gating).
A_GRIPS: tuple[Grip, ...] = ("bracket_wing",)
B_GRIPS: tuple[Grip, ...] = ("pistol_grip", "d_ring_loop", "inline_handle")
A_PLUNGERS: tuple[PlungerDrive, ...] = ("ratchet_jhook", "ring_pull")
B_PLUNGERS: tuple[PlungerDrive, ...] = ("thumb_plate",)

# rib_count multiplicity domain (spec §8). Weighted small (4 high, 3/5 common,
# 6 long tail).
N_RIB_MIN, N_RIB_MAX = 3, 6
RIB_COUNT_WEIGHTS = (0.25, 0.45, 0.20, 0.10)  # for N = 3, 4, 5, 6

# Family-base plunger travel (spec §7): A short, B long.
_A_TRAVEL = 0.060
_B_TRAVEL = 0.180
_A_TRIG_OPEN = 0.55
_B_TRIG_OPEN = 0.50

# Palettes (4-6 colorways drawn from the 8 source records, spec §7).
# Keys: shell, cap, cartridge, label, collar, nozzle, rod, tip, grip.
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "gunmetal_pro": {
        "shell": (0.27, 0.28, 0.30, 1.0),
        "cap": (0.10, 0.10, 0.11, 1.0),
        "cartridge": (0.90, 0.90, 0.88, 1.0),
        "label": (0.20, 0.34, 0.62, 1.0),
        "collar": (0.10, 0.10, 0.11, 1.0),
        "nozzle": (0.10, 0.10, 0.11, 1.0),
        "rod": (0.74, 0.76, 0.80, 1.0),
        "tip": (0.93, 0.93, 0.92, 1.0),
        "grip": (0.10, 0.10, 0.11, 1.0),
    },
    "red_consumer": {
        "shell": (0.84, 0.15, 0.15, 1.0),
        "cap": (0.55, 0.10, 0.10, 1.0),
        "cartridge": (0.32, 0.42, 0.52, 1.0),
        "label": (0.20, 0.34, 0.62, 1.0),
        "collar": (0.78, 0.18, 0.18, 1.0),
        "nozzle": (0.92, 0.92, 0.90, 1.0),
        "rod": (0.55, 0.56, 0.58, 1.0),
        "tip": (0.92, 0.92, 0.90, 1.0),
        "grip": (0.78, 0.16, 0.16, 1.0),
    },
    "blue_silicone": {
        "shell": (0.30, 0.31, 0.34, 1.0),
        "cap": (0.12, 0.12, 0.13, 1.0),
        "cartridge": (0.32, 0.46, 0.60, 1.0),
        "label": (0.18, 0.30, 0.44, 1.0),
        "collar": (0.22, 0.34, 0.46, 1.0),
        "nozzle": (0.92, 0.92, 0.90, 1.0),
        "rod": (0.60, 0.62, 0.66, 1.0),
        "tip": (0.92, 0.92, 0.90, 1.0),
        "grip": (0.16, 0.16, 0.18, 1.0),
    },
    "aluminum_sausage": {
        "shell": (0.68, 0.70, 0.72, 1.0),
        "cap": (0.35, 0.36, 0.38, 1.0),
        "cartridge": (0.78, 0.78, 0.76, 1.0),
        "label": (0.42, 0.44, 0.48, 1.0),
        "collar": (0.35, 0.36, 0.38, 1.0),
        "nozzle": (0.12, 0.12, 0.13, 1.0),
        "rod": (0.74, 0.76, 0.80, 1.0),
        "tip": (0.93, 0.93, 0.92, 1.0),
        "grip": (0.16, 0.16, 0.18, 1.0),
    },
    "industrial_grey": {
        "shell": (0.42, 0.43, 0.45, 1.0),
        "cap": (0.22, 0.22, 0.24, 1.0),
        "cartridge": (0.36, 0.46, 0.56, 1.0),
        "label": (0.24, 0.34, 0.46, 1.0),
        "collar": (0.34, 0.35, 0.37, 1.0),
        "nozzle": (0.92, 0.92, 0.90, 1.0),
        "rod": (0.62, 0.64, 0.68, 1.0),
        "tip": (0.92, 0.92, 0.90, 1.0),
        "grip": (0.42, 0.43, 0.45, 1.0),
    },
}


# ===========================================================================
# Base real-world dimensions (meters). A standard ~300 ml cartridge gun.
# A-family numbers from parent A (24ba16de); B-family from parent B (ff090a9c).
# ===========================================================================
# --- A family (barrel_body root; authored about z=0, lifted by AXIS_Z). ---
_A_TUBE_R = 0.0245  # cartridge outer radius
_A_TUBE_LEN = 0.215  # cartridge body length (X)
_A_ROD_R = 0.0042
_A_HOOK_R = 0.0038
_A_HOOK_CURVE_R = 0.0075
_A_HOOK_TAIL = 0.016
_A_RING_R = 0.013  # ring-pull major radius
_A_RING_WIRE_R = 0.003

# --- B family (frame root; authored at z=0). ---
_B_BARREL_R = 0.027  # cradle inner radius
_B_BARREL_LEN = 0.260
_B_CART_R = 0.0255
_B_CART_LEN = 0.250
_B_CRADLE_WALL = 0.0035
_B_ROD_LEN = 0.230
_B_RIB_ROD_R = 0.003
_B_RIB_ARC_START_DEG = 210.0
_B_RIB_ARC_END_DEG = 330.0


@dataclass(frozen=True)
class CaulkingGunConfig:
    cradle: Cradle | None = None
    grip: Grip | None = None
    plunger_drive: PlungerDrive | None = None
    rib_count: int | None = None
    palette_style: PaletteStyle = "gunmetal_pro"
    barrel_len_scale: float = 1.0
    barrel_girth_scale: float = 1.0
    plunger_travel_scale: float = 1.0
    trigger_open_angle_scale: float = 1.0
    grip_drop_scale: float = 1.0
    rib_thickness_scale: float = 1.0
    name: str = "caulking_gun"


@dataclass(frozen=True)
class ResolvedCaulkingGunConfig:
    cradle: Cradle
    grip: Grip
    plunger_drive: PlungerDrive
    rib_count: int  # meaningful only for cradle == rib_cage
    palette_style: PaletteStyle
    # Family-derived geometry (scaled).
    family: Literal["A", "B"]
    tube_r: float
    tube_len: float
    rod_len: float
    plunger_travel: float
    trigger_open: float
    grip_drop_scale: float
    rib_rod_r: float
    name: str

    @property
    def is_a_family(self) -> bool:
        return self.family == "A"


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


def _family_of(cradle: Cradle) -> Literal["A", "B"]:
    return "A" if cradle in A_FAMILY_CRADLES else "B"


def config_from_seed(seed: int) -> CaulkingGunConfig:
    rng = random.Random(seed)
    cradle = rng.choice(CRADLES)
    family = _family_of(cradle)
    if family == "A":
        grip = rng.choice(A_GRIPS)
        plunger = rng.choice(A_PLUNGERS)
    else:
        grip = rng.choice(B_GRIPS)
        plunger = rng.choice(B_PLUNGERS)
    rib_count = (
        rng.choices((3, 4, 5, 6), weights=RIB_COUNT_WEIGHTS, k=1)[0]
        if cradle == "rib_cage"
        else 4
    )
    return CaulkingGunConfig(
        cradle=cradle,
        grip=grip,
        plunger_drive=plunger,
        rib_count=rib_count,
        palette_style=rng.choice(PALETTE_STYLES),
        barrel_len_scale=round(rng.uniform(0.90, 1.12), 4),
        barrel_girth_scale=round(rng.uniform(0.92, 1.10), 4),
        plunger_travel_scale=round(rng.uniform(0.85, 1.10), 4),
        trigger_open_angle_scale=round(rng.uniform(0.85, 1.10), 4),
        grip_drop_scale=round(rng.uniform(0.90, 1.10), 4),
        rib_thickness_scale=round(rng.uniform(0.85, 1.15), 4),
        name=f"seeded_caulking_gun_{seed}",
    )


def resolve_config(config: CaulkingGunConfig | None = None) -> ResolvedCaulkingGunConfig:
    cfg = config or CaulkingGunConfig()
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)

    cradle = _pick(cfg.cradle, CRADLES)
    family = _family_of(cradle)

    # --- Compatibility gating (spec §9, same-family-first). ---
    grip = _pick(cfg.grip, GRIPS)
    plunger = _pick(cfg.plunger_drive, PLUNGER_DRIVES)
    if family == "A":
        if grip not in A_GRIPS:
            grip = A_GRIPS[0]
        if plunger not in A_PLUNGERS:
            plunger = A_PLUNGERS[0]
    else:
        if grip not in B_GRIPS:
            grip = B_GRIPS[0]
        if plunger not in B_PLUNGERS:
            plunger = B_PLUNGERS[0]

    rib_count = int(cfg.rib_count) if cfg.rib_count is not None else 4
    rib_count = int(_clamp(rib_count, N_RIB_MIN, N_RIB_MAX))

    len_scale = _clamp(cfg.barrel_len_scale, 0.90, 1.12)
    girth_scale = _clamp(cfg.barrel_girth_scale, 0.92, 1.10)
    travel_scale = _clamp(cfg.plunger_travel_scale, 0.85, 1.10)
    angle_scale = _clamp(cfg.trigger_open_angle_scale, 0.85, 1.10)
    grip_drop_scale = _clamp(cfg.grip_drop_scale, 0.90, 1.10)
    rib_thickness_scale = _clamp(cfg.rib_thickness_scale, 0.85, 1.15)

    if family == "A":
        tube_r = _A_TUBE_R * girth_scale
        tube_len = _A_TUBE_LEN * len_scale
        rod_len = 0.0  # A rod is derived per-build from rod front/back
        base_travel = _A_TRAVEL
        base_open = _A_TRIG_OPEN
    else:
        tube_r = _B_CART_R * girth_scale
        tube_len = _B_CART_LEN * len_scale
        rod_len = _B_ROD_LEN * len_scale
        base_travel = _B_TRAVEL
        base_open = _B_TRIG_OPEN

    # Plunger travel clamp: keep below the available cartridge stroke so the
    # push disc never exits the cartridge bore (spec §7 inequality #2).
    plunger_travel = base_travel * travel_scale
    plunger_travel = min(plunger_travel, 0.80 * tube_len)

    trigger_open = base_open * angle_scale

    rib_rod_r = _B_RIB_ROD_R * rib_thickness_scale
    # rib clearance: N ribs across the lower 120 deg arc must not collide
    # (spec §7 inequality #4). arc len = R * (120 deg). cap rib_r if needed.
    if cradle == "rib_cage":
        arc_len = (_B_BARREL_R) * math.radians(_B_RIB_ARC_END_DEG - _B_RIB_ARC_START_DEG)
        max_total = 0.85 * arc_len
        if rib_count * (2.0 * rib_rod_r) > max_total:
            rib_rod_r = max(0.0018, max_total / (2.0 * rib_count))

    return ResolvedCaulkingGunConfig(
        cradle=cradle,
        grip=grip,
        plunger_drive=plunger,
        rib_count=rib_count,
        palette_style=palette_style,
        family=family,
        tube_r=tube_r,
        tube_len=tube_len,
        rod_len=rod_len,
        plunger_travel=plunger_travel,
        trigger_open=trigger_open,
        grip_drop_scale=grip_drop_scale,
        rib_rod_r=rib_rod_r,
        name=cfg.name or "caulking_gun",
    )


def with_overrides(config: CaulkingGunConfig, **kwargs: object) -> CaulkingGunConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: CaulkingGunConfig | ResolvedCaulkingGunConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedCaulkingGunConfig) else resolve_config(config)
    choices: list[tuple[str, str]] = [
        ("cradle", r.cradle),
        ("grip", r.grip),
        ("plunger_drive", r.plunger_drive),
    ]
    if r.cradle == "rib_cage":
        choices.append(("rib_count", f"n{r.rib_count}"))
    return tuple(choices)


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ===========================================================================
# A-FAMILY geometry (barrel_body root; authored about barrel axis z=0).
# Per-build derived X positions live on a small namespace built from the
# resolved config so all helpers share consistent dimensions.
# ===========================================================================
@dataclass(frozen=True)
class _ADims:
    tube_r: float
    tube_len: float
    tube_x0: float
    tube_x1: float
    barrel_r_out: float
    barrel_r_in: float
    barrel_x0: float
    barrel_x1: float
    barrel_len: float
    front_collar_r_out: float
    front_collar_r_in: float
    front_collar_t: float
    front_collar_x: float
    rear_cap_r: float
    rear_cap_t: float
    rear_cap_x: float
    nozzle_base_r: float
    nozzle_len: float
    nozzle_x0: float
    tip_len: float
    rod_r: float
    rod_push_r: float
    rod_push_t: float
    rod_front_x: float
    rod_back_x: float
    frame_rise: float
    frame_t: float
    frame_w_x: float
    frame_x: float
    pivot_z: float
    pivot_x: float
    pin_r: float
    pin_len: float
    axis_z: float
    frame_half_w: float
    slot_half_w: float
    slot_depth: float


def _a_dims(r: ResolvedCaulkingGunConfig) -> _ADims:
    sausage = r.cradle == "sausage_tube"
    tube_r = r.tube_r
    tube_len = r.tube_len
    tube_x0 = 0.0
    tube_x1 = tube_x0 + tube_len
    barrel_r_out = tube_r + 0.006
    barrel_r_in = tube_r + 0.0015
    barrel_x0 = tube_x0 - 0.006
    barrel_x1 = tube_x1 - 0.010
    front_collar_r_out = barrel_r_out + 0.004
    front_collar_r_in = tube_r + 0.001
    front_collar_t = 0.012
    front_collar_x = barrel_x1 - 0.004
    rear_cap_r = barrel_r_out + 0.006
    rear_cap_t = 0.016
    rear_cap_x = barrel_x0 - rear_cap_t / 2.0
    nozzle_base_r = tube_r * 0.62
    nozzle_len = 0.030
    nozzle_x0 = tube_x1
    tip_len = 0.022
    rod_r = _A_ROD_R
    # For sausage_tube there is no rigid cartridge, so the push disc must seal
    # against the barrel bore (= tube_r) for contact; otherwise it rides inside
    # the cartridge (slightly smaller, captured).
    rod_push_r = tube_r if sausage else tube_r - 0.001
    rod_push_t = 0.005
    rod_front_x = tube_x0 + 0.018
    rod_back_x = rear_cap_x - 0.095
    frame_rise = 0.085
    frame_t = 0.010
    frame_w_x = 0.038
    frame_x = rear_cap_x - frame_w_x / 2.0 + 0.002
    pivot_z = frame_rise
    pivot_x = frame_x
    pin_r = 0.0035
    pin_len = 0.030
    axis_z = rear_cap_r
    frame_half_w = rod_r + 0.0025 + frame_t
    slot_half_w = 0.006
    slot_depth = 0.010
    return _ADims(
        tube_r=tube_r, tube_len=tube_len, tube_x0=tube_x0, tube_x1=tube_x1,
        barrel_r_out=barrel_r_out, barrel_r_in=barrel_r_in, barrel_x0=barrel_x0,
        barrel_x1=barrel_x1, barrel_len=barrel_x1 - barrel_x0,
        front_collar_r_out=front_collar_r_out, front_collar_r_in=front_collar_r_in,
        front_collar_t=front_collar_t, front_collar_x=front_collar_x,
        rear_cap_r=rear_cap_r, rear_cap_t=rear_cap_t, rear_cap_x=rear_cap_x,
        nozzle_base_r=nozzle_base_r, nozzle_len=nozzle_len, nozzle_x0=nozzle_x0,
        tip_len=tip_len, rod_r=rod_r, rod_push_r=rod_push_r, rod_push_t=rod_push_t,
        rod_front_x=rod_front_x, rod_back_x=rod_back_x, frame_rise=frame_rise,
        frame_t=frame_t, frame_w_x=frame_w_x, frame_x=frame_x, pivot_z=pivot_z,
        pivot_x=pivot_x, pin_r=pin_r, pin_len=pin_len, axis_z=axis_z,
        frame_half_w=frame_half_w, slot_half_w=slot_half_w, slot_depth=slot_depth,
    )


def _a_barrel_cradle(d: _ADims) -> cq.Workplane:
    """Half-barrel: lower half-cylinder open trough (half_barrel cradle)."""
    outer = (
        cq.Workplane("YZ").workplane(offset=d.barrel_x0).circle(d.barrel_r_out).extrude(d.barrel_len)
    )
    inner = (
        cq.Workplane("YZ").workplane(offset=d.barrel_x0).circle(d.barrel_r_in).extrude(d.barrel_len)
    )
    shell = outer.cut(inner)
    keep_top = d.barrel_r_out * 0.18
    cutter = (
        cq.Workplane("XY")
        .box(d.barrel_len * 1.4, d.barrel_r_out * 2.4, d.barrel_r_out * 2.0)
        .translate((d.barrel_x0 + d.barrel_len / 2.0, 0.0, keep_top + d.barrel_r_out))
    )
    return shell.cut(cutter)


def _a_barrel_tube_closed(d: _ADims) -> cq.Workplane:
    """Closed_barrel: full enclosed tube + bottom longitudinal loading slot."""
    outer = (
        cq.Workplane("YZ").workplane(offset=d.barrel_x0).circle(d.barrel_r_out).extrude(d.barrel_len)
    )
    inner = (
        cq.Workplane("YZ").workplane(offset=d.barrel_x0).circle(d.barrel_r_in).extrude(d.barrel_len)
    )
    shell = outer.cut(inner)
    slot = (
        cq.Workplane("XY")
        .box(d.barrel_len * 1.02, d.slot_half_w * 2.0, d.slot_depth * 1.1)
        .translate((d.barrel_x0 + d.barrel_len / 2.0, 0.0, -d.barrel_r_out + d.slot_depth / 2.0))
    )
    return shell.cut(slot)


def _a_barrel_tube_sausage(d: _ADims) -> cq.Workplane:
    """Sausage_tube: lathe-revolved fully closed aluminium tube."""
    wall_t = 0.003
    r_in = d.tube_r
    r_out = d.tube_r + wall_t
    x0 = d.tube_x0
    x1 = d.tube_x1
    profile = (
        cq.Workplane("XZ")
        .moveTo(x0, r_in)
        .lineTo(x1, r_in)
        .lineTo(x1, r_out)
        .lineTo(x0, r_out)
        .close()
    )
    return profile.revolve(360, (0, 0), (1, 0))


def _a_front_cone_cap(d: _ADims) -> cq.Workplane:
    """Sausage front_cap: revolved threaded nose cap (replaces cartridge nose)."""
    wall_t = 0.003
    r_in = d.tube_r
    r_out = d.tube_r + wall_t
    cap_x0 = d.tube_x1
    ring_len = 0.010
    cone_len = 0.028
    cap_r_out = r_out + 0.004
    tip_r = 0.008
    x_ring_end = cap_x0 + ring_len
    x_tip = cap_x0 + ring_len + cone_len
    profile = (
        cq.Workplane("XZ")
        .moveTo(cap_x0, r_in)
        .lineTo(cap_x0, cap_r_out)
        .lineTo(x_ring_end, cap_r_out)
        .lineTo(x_tip, tip_r + wall_t)
        .lineTo(x_tip, tip_r)
        .lineTo(x_ring_end, r_in)
        .close()
    )
    return profile.revolve(360, (0, 0), (1, 0))


def _a_front_collar(d: _ADims) -> cq.Workplane:
    ring_out = (
        cq.Workplane("YZ")
        .workplane(offset=d.front_collar_x)
        .circle(d.front_collar_r_out)
        .extrude(d.front_collar_t)
    )
    ring_in = (
        cq.Workplane("YZ")
        .workplane(offset=d.front_collar_x - 0.001)
        .circle(d.front_collar_r_in)
        .extrude(d.front_collar_t + 0.002)
    )
    return ring_out.cut(ring_in)


def _a_rear_cap(d: _ADims) -> cq.Workplane:
    cap = (
        cq.Workplane("YZ").workplane(offset=d.rear_cap_x).circle(d.rear_cap_r).extrude(d.rear_cap_t)
    )
    bore = (
        cq.Workplane("YZ")
        .workplane(offset=d.rear_cap_x - 0.001)
        .circle(d.rod_r + 0.0012)
        .extrude(d.rear_cap_t + 0.002)
    )
    return cap.cut(bore)


def _a_handle_frame(d: _ADims) -> cq.Workplane:
    """Bracket_wing U-yoke straddling the rod, carrying the trigger pivot."""
    half_gap = d.rod_r + 0.0025 + d.frame_t / 2.0
    z_lo = -d.rear_cap_r * 0.55
    z_hi = d.pivot_z + 0.006
    plate_h = z_hi - z_lo
    plate_cz = (z_lo + z_hi) / 2.0
    side_plate = cq.Workplane("XY").box(d.frame_w_x, d.frame_t, plate_h).edges("|Y").fillet(0.005)
    left = side_plate.translate((d.frame_x, +half_gap, plate_cz))
    right = side_plate.translate((d.frame_x, -half_gap, plate_cz))
    lug_inner = half_gap - d.frame_t / 2.0 - 0.0015
    lug_len = (half_gap + d.frame_t / 2.0 + 0.001) - lug_inner
    lug_left = (
        cq.Workplane("XZ").workplane(offset=lug_inner).circle(0.011).extrude(lug_len)
        .translate((d.pivot_x, 0.0, d.pivot_z))
    )
    lug_right = (
        cq.Workplane("XZ").workplane(offset=-(lug_inner + lug_len)).circle(0.011).extrude(lug_len)
        .translate((d.pivot_x, 0.0, d.pivot_z))
    )
    boss = lug_left.union(lug_right)
    web = (
        cq.Workplane("XY")
        .box(d.frame_w_x, 2.0 * half_gap + d.frame_t, 0.012)
        .translate((d.frame_x, 0.0, z_lo + 0.006))
    )
    boss_x0 = -0.026
    boss_x1 = -0.002
    guide = (
        cq.Workplane("YZ").workplane(offset=boss_x0).circle(0.013).extrude(boss_x1 - boss_x0)
    )
    guide_bore = (
        cq.Workplane("YZ")
        .workplane(offset=boss_x0 - 0.001)
        .circle(d.rod_r + 0.0012)
        .extrude(boss_x1 - boss_x0 + 0.002)
    )
    guide = guide.cut(guide_bore)
    return left.union(right).union(boss).union(web).union(guide)


def _a_grip_wing(d: _ADims) -> cq.Workplane:
    profile = (
        cq.Workplane("XZ")
        .moveTo(-0.045, 0.090)
        .lineTo(-0.057, 0.094)
        .lineTo(-0.096, 0.034)
        .lineTo(-0.081, 0.028)
        .close()
    )
    return profile.extrude(d.frame_half_w, both=True)


def _a_pivot_pin(d: _ADims) -> cq.Workplane:
    return (
        cq.Workplane("XZ").workplane(offset=-d.pin_len / 2.0).circle(d.pin_r).extrude(d.pin_len)
        .translate((d.pivot_x, 0.0, d.pivot_z))
    )


def _a_cartridge_tube(d: _ADims) -> cq.Workplane:
    return cq.Workplane("YZ").workplane(offset=d.tube_x0).circle(d.tube_r).extrude(d.tube_len)


def _a_cartridge_label(d: _ADims) -> cq.Workplane:
    band_x0 = d.tube_x0 + 0.045
    band_len = min(0.110, d.tube_len * 0.5)
    band = (
        cq.Workplane("YZ").workplane(offset=band_x0).circle(d.tube_r + 0.0006).extrude(band_len)
    )
    inner = (
        cq.Workplane("YZ").workplane(offset=band_x0 - 0.001).circle(d.tube_r - 0.0004).extrude(band_len + 0.002)
    )
    band = band.cut(inner)
    keep = (
        cq.Workplane("XY")
        .box(band_len * 1.3, d.tube_r * 1.2, d.tube_r * 1.4)
        .translate((band_x0 + band_len / 2.0, 0.0, d.tube_r * 0.55 + d.tube_r * 0.7))
    )
    return band.intersect(keep)


def _a_nozzle_cone(d: _ADims) -> cq.Workplane:
    cone = (
        cq.Workplane("YZ")
        .workplane(offset=d.nozzle_x0)
        .circle(d.nozzle_base_r)
        .workplane(offset=d.nozzle_len)
        .circle(0.0045)
        .loft(combine=True)
    )
    shoulder = (
        cq.Workplane("YZ")
        .workplane(offset=d.nozzle_x0 - 0.004)
        .circle(d.tube_r * 0.82)
        .workplane(offset=0.004)
        .circle(d.nozzle_base_r)
        .loft(combine=True)
    )
    return cone.union(shoulder)


def _a_white_tip(d: _ADims) -> cq.Workplane:
    return (
        cq.Workplane("YZ")
        .workplane(offset=d.nozzle_x0 + d.nozzle_len)
        .circle(0.0045)
        .workplane(offset=d.tip_len)
        .circle(0.0018)
        .loft(combine=True)
    )


def _a_sausage_nozzle_cone(d: _ADims) -> cq.Workplane:
    """Nozzle cone for the sausage front_cap (base at the cap tip)."""
    cap_x0 = d.tube_x1
    nozzle_x0 = cap_x0 + 0.010 + 0.028
    cone = (
        cq.Workplane("YZ")
        .workplane(offset=nozzle_x0)
        .circle(0.008)
        .workplane(offset=d.nozzle_len)
        .circle(0.0045)
        .loft(combine=True)
    )
    return cone


def _a_sausage_white_tip(d: _ADims) -> cq.Workplane:
    cap_x0 = d.tube_x1
    nozzle_x0 = cap_x0 + 0.010 + 0.028
    return (
        cq.Workplane("YZ")
        .workplane(offset=nozzle_x0 + d.nozzle_len)
        .circle(0.0045)
        .workplane(offset=d.tip_len)
        .circle(0.0018)
        .loft(combine=True)
    )


def _a_cart_plunger(d: _ADims) -> cq.Workplane:
    return cq.Workplane("YZ").workplane(offset=0.0).circle(d.tube_r - 0.001).extrude(0.006)


def _a_plunger_rod(d: _ADims) -> cq.Workplane:
    total_len = d.rod_front_x - d.rod_back_x
    rod = cq.Workplane("YZ").workplane(offset=-total_len).circle(d.rod_r).extrude(total_len)
    push = cq.Workplane("YZ").workplane(offset=-d.rod_push_t).circle(d.rod_push_r).extrude(d.rod_push_t)
    return rod.union(push)


def _a_hook_handle(d: _ADims) -> cq.Workplane:
    total_len = d.rod_front_x - d.rod_back_x
    tail_x = -total_len
    pts: list[tuple[float, float]] = [
        (tail_x + 0.010, 0.0),
        (tail_x + 0.003, 0.0),
    ]
    for i in range(1, 9):
        a = math.pi * (i / 8.0)
        x = tail_x - _A_HOOK_CURVE_R * math.sin(a)
        z = _A_HOOK_CURVE_R - _A_HOOK_CURVE_R * math.cos(a)
        pts.append((x, z))
    pts.append((tail_x + 0.006, 2.0 * _A_HOOK_CURVE_R))
    pts.append((tail_x + _A_HOOK_TAIL, 2.0 * _A_HOOK_CURVE_R))
    wire = cq.Workplane("XZ").moveTo(pts[0][0], pts[0][1]).spline(pts[1:]).val()
    sweep = (
        cq.Workplane("YZ").workplane(offset=pts[0][0]).center(0.0, pts[0][1]).circle(_A_HOOK_R)
    )
    return sweep.sweep(cq.Workplane(obj=wire), multisection=False)


def _a_ring_handle(d: _ADims) -> cq.Workplane:
    total_len = d.rod_front_x - d.rod_back_x
    tail_x = -total_len
    ring_cx = tail_x - _A_RING_R + 0.001
    section = cq.Workplane("XY").moveTo(tail_x, 0.0).circle(_A_RING_WIRE_R)
    return section.revolve(360, (ring_cx, -0.1), (ring_cx, 0.1))


def _a_trigger_blade(d: _ADims) -> cq.Workplane:
    trigger_w = 0.013
    trigger_h = 0.026
    trigger_len = 0.060
    blade = (
        cq.Workplane("XY")
        .workplane(offset=-0.006)
        .rect(trigger_w, trigger_h)
        .workplane(offset=-trigger_len)
        .rect(trigger_w * 1.3, trigger_h * 1.55)
        .loft(combine=True)
    )
    hub = cq.Workplane("XZ").workplane(offset=-0.011).circle(0.011).extrude(0.022)
    neck = cq.Workplane("XY").box(trigger_w, trigger_h, 0.012).translate((0.0, 0.0, -0.004))
    lever = blade.union(hub).union(neck)
    pin_bore = cq.Solid.makeCylinder(
        d.pin_r + 0.0006, 0.030, cq.Vector(0.0, -0.015, 0.0), cq.Vector(0.0, 1.0, 0.0)
    )
    lever = lever.cut(cq.Workplane(obj=pin_bore))
    lever = lever.edges("|Y and <Z").fillet(0.003)
    return lever


# ===========================================================================
# B-FAMILY geometry (frame root; authored about barrel axis z=0, no lift).
# ===========================================================================
@dataclass(frozen=True)
class _BDims:
    barrel_r: float
    barrel_len: float
    cart_r: float
    cart_len: float
    front_x: float
    back_x: float
    cradle_wall: float
    cradle_outer_r: float
    grip_top_z: float
    grip_x: float
    grip_len: float
    grip_front_x: float
    pivot_x: float
    pivot_z: float
    pivot_y_half: float
    rod_len: float
    plate_x: float
    rib_rod_r: float
    grip_drop_scale: float
    # inline-handle specifics
    handle_len: float
    handle_rear_x: float
    handle_front_x: float
    handle_top_z: float
    handle_bot_z: float
    handle_y_half: float
    trig_pivot_x: float
    trig_pivot_z: float


def _b_dims(r: ResolvedCaulkingGunConfig) -> _BDims:
    barrel_r = _B_BARREL_R
    barrel_len = _B_BARREL_LEN * (r.tube_len / _B_CART_LEN)
    cart_r = r.tube_r
    cart_len = r.tube_len
    front_x = barrel_len / 2.0
    back_x = -barrel_len / 2.0
    cradle_wall = _B_CRADLE_WALL
    cradle_outer_r = barrel_r + cradle_wall
    grip_len = 0.115 * r.grip_drop_scale
    grip_top_z = -0.014
    grip_x = back_x + 0.040
    grip_front_x = grip_x + 0.030
    pivot_x = grip_front_x + 0.018
    pivot_z = -0.040
    pivot_y_half = 0.012
    rod_len = r.rod_len
    plate_x = back_x + 0.006
    handle_len = 0.110
    handle_rear_x = back_x - handle_len
    # Reach the handle front into the rear-plate / cradle so the inline frame
    # fuses solidly (a thin face contact splits into a mesh island).
    handle_front_x = back_x + 0.010
    handle_top_z = cradle_outer_r + 0.008
    handle_bot_z = -(cradle_outer_r + 0.008)
    handle_y_half = 0.017
    trig_pivot_x = back_x - 0.002
    trig_pivot_z = cradle_outer_r + 0.020
    return _BDims(
        barrel_r=barrel_r, barrel_len=barrel_len, cart_r=cart_r, cart_len=cart_len,
        front_x=front_x, back_x=back_x, cradle_wall=cradle_wall,
        cradle_outer_r=cradle_outer_r, grip_top_z=grip_top_z, grip_x=grip_x,
        grip_len=grip_len, grip_front_x=grip_front_x, pivot_x=pivot_x,
        pivot_z=pivot_z, pivot_y_half=pivot_y_half, rod_len=rod_len, plate_x=plate_x,
        rib_rod_r=r.rib_rod_r, grip_drop_scale=r.grip_drop_scale,
        handle_len=handle_len, handle_rear_x=handle_rear_x,
        handle_front_x=handle_front_x, handle_top_z=handle_top_z,
        handle_bot_z=handle_bot_z, handle_y_half=handle_y_half,
        trig_pivot_x=trig_pivot_x, trig_pivot_z=trig_pivot_z,
    )


def _b_cradle_halfpipe(d: _BDims) -> cq.Workplane:
    tube = (
        cq.Workplane("XY")
        .circle(d.cradle_outer_r)
        .circle(d.barrel_r)
        .extrude(d.barrel_len)
        .translate((0, 0, -d.barrel_len / 2.0))
    )
    gap = (
        cq.Workplane("XY")
        .box(2 * d.cradle_outer_r, 2 * d.cradle_outer_r, d.barrel_len + 0.01)
        .translate((0, d.cradle_outer_r * 0.92, 0))
    )
    cradle = tube.cut(gap)
    return cradle.rotate((0, 0, 0), (0, 1, 0), 90.0)


def _b_front_ring(d: _BDims) -> cq.Workplane:
    # Start 3 mm inside the cradle front face so the ring fuses into the cradle
    # wall (avoids a knife-edge face contact that splits into an island).
    return (
        cq.Workplane("YZ")
        .workplane(offset=d.front_x - 0.003)
        .circle(d.cradle_outer_r + 0.004)
        .circle(0.012)
        .extrude(0.017)
    )


def _b_rear_plate(d: _BDims) -> cq.Workplane:
    # Overlap the cradle rear face by 3 mm for solid fusion.
    return (
        cq.Workplane("YZ")
        .workplane(offset=d.back_x - 0.010)
        .circle(d.cradle_outer_r + 0.004)
        .circle(0.006)
        .extrude(0.015)
    )


def _b_spine_rail(d: _BDims) -> cq.Workplane:
    length = d.barrel_len + 0.020
    cz = -0.032
    return cq.Workplane("XY").box(length, 0.030, 0.006).translate((0.0, 0.0, cz))


def _b_rib_rod_geometry(d: _BDims, angle_rad: float) -> cq.Workplane:
    """One thin longitudinal rib rod (shared geometry helper, ribframe L70-82)."""
    y = d.barrel_r * math.cos(angle_rad)
    z = d.barrel_r * math.sin(angle_rad)
    return (
        cq.Workplane("YZ")
        .workplane(offset=d.back_x - 0.003)
        .center(y, z)
        .circle(d.rib_rod_r)
        .extrude(d.barrel_len + 0.006)
    )


def _b_grip_pistol(d: _BDims) -> cq.Workplane:
    gl = d.grip_len
    pts = [
        (d.grip_x - 0.020, d.grip_top_z),
        (d.grip_x + 0.030, d.grip_top_z),
        (d.grip_x + 0.018, d.grip_top_z - gl * 0.55),
        (d.grip_x + 0.002, d.grip_top_z - gl),
        (d.grip_x - 0.030, d.grip_top_z - gl * 0.95),
        (d.grip_x - 0.034, d.grip_top_z - gl * 0.4),
        (d.grip_x - 0.022, d.grip_top_z - 0.006),
    ]
    return (
        cq.Workplane("XZ")
        .polyline(pts)
        .close()
        .extrude(0.020)
        .translate((0, 0.010, 0))
        .edges("|Y")
        .fillet(0.006)
    )


def _b_pivot_lugs(d: _BDims) -> cq.Workplane:
    strut_top_z = -d.cradle_outer_r + 0.002
    plate_h = abs(strut_top_z - d.pivot_z) + 0.012
    plate_cz = (d.pivot_z + strut_top_z) / 2.0

    def side_plate(y_inner: float, thickness: float):
        return (
            cq.Workplane("XZ")
            .workplane(offset=y_inner)
            .center(d.pivot_x, plate_cz)
            .rect(0.018, plate_h)
            .extrude(thickness)
            .edges("|Y")
            .fillet(0.004)
        )

    left_plate = side_plate(d.pivot_y_half, 0.006)
    right_plate = side_plate(-d.pivot_y_half - 0.006, 0.006)
    left_lug = (
        cq.Workplane("XZ").workplane(offset=d.pivot_y_half).center(d.pivot_x, d.pivot_z).circle(0.0095).extrude(0.006)
    )
    right_lug = (
        cq.Workplane("XZ").workplane(offset=-d.pivot_y_half - 0.006).center(d.pivot_x, d.pivot_z).circle(0.0095).extrude(0.006)
    )
    return left_plate.union(right_plate).union(left_lug).union(right_lug)


def _b_pivot_pin(d: _BDims) -> cq.Workplane:
    return (
        cq.Workplane("XZ")
        .workplane(offset=d.pivot_y_half + 0.005)
        .center(d.pivot_x, d.pivot_z)
        .circle(0.0035)
        .extrude(-(2 * d.pivot_y_half + 0.010))
    )


# D-ring loop grip (dgrip).
def _b_dring_path(d: _BDims) -> list[tuple[float, float, float]]:
    top_z = -0.032
    gd = d.grip_drop_scale
    return [
        (-0.110, 0.0, top_z),
        (-0.076, 0.0, top_z + 0.004),
        (-0.048, 0.0, top_z),
        (-0.014, 0.0, -0.052 * gd),
        (-0.008, 0.0, -0.092 * gd),
        (-0.035, 0.0, -0.130 * gd),
        (-0.068, 0.0, -0.140 * gd),
        (-0.108, 0.0, -0.130 * gd),
        (-0.128, 0.0, -0.065 * gd),
    ]


def _b_dring_loop_mesh(d: _BDims, assets):
    loop = tube_from_spline_points(
        _b_dring_path(d),
        radius=0.005,
        samples_per_segment=18,
        radial_segments=20,
        closed_spline=True,
        cap_ends=False,
        up_hint=(0.0, 1.0, 0.0),
    )
    return mesh_from_geometry(loop, "dring_loop")


def _b_dring_bosses(d: _BDims) -> cq.Workplane:
    path = _b_dring_path(d)
    boss_r = 0.005 + 0.003

    def boss_at(x: float, z: float):
        return (
            cq.Workplane("XZ").workplane(offset=0.008).center(x, z).circle(boss_r).extrude(-0.016)
        )

    rear = boss_at(path[0][0], path[0][2])
    front = boss_at(path[2][0], path[2][2])
    return rear.union(front)


# Inline handle grip.
def _b_d_handle(d: _BDims) -> cq.Workplane:
    wall_front = 0.018
    wall_rear = 0.014
    wall_top = 0.010
    wall_bot = 0.010
    hx0 = d.handle_front_x
    hx1 = d.handle_rear_x
    hz0 = d.handle_bot_z
    hz1 = d.handle_top_z
    hy0 = -d.handle_y_half
    hy1 = d.handle_y_half
    outer_cx = (hx0 + hx1) / 2.0
    outer_cz = (hz0 + hz1) / 2.0
    outer_wx = hx0 - hx1
    outer_wz = hz1 - hz0
    outer = (
        cq.Workplane("XZ")
        .workplane(offset=hy0)
        .center(outer_cx, outer_cz)
        .rect(outer_wx, outer_wz)
        .extrude(hy1 - hy0)
        .edges("|Y")
        .fillet(0.005)
    )
    cx0 = hx0 - wall_front
    cx1 = hx1 + wall_rear
    cz0 = hz0 + wall_bot
    cz1 = hz1 - wall_top
    cut_cx = (cx0 + cx1) / 2.0
    cut_cz = (cz0 + cz1) / 2.0
    cut_wx = cx0 - cx1
    cut_wz = cz1 - cz0
    # Cut the D-hole all the way through in Y (a few mm past both faces) so the
    # window is open, not an enclosed cavity. An enclosed cavity tessellates as
    # a separate inner mesh shell (a disconnected island); an open window keeps
    # the handle a single connected surface.
    inner = (
        cq.Workplane("XZ")
        .workplane(offset=hy0 - 0.002)
        .center(cut_cx, cut_cz)
        .rect(cut_wx, cut_wz)
        .extrude((hy1 - hy0) + 0.004)
    )
    return outer.cut(inner)


def _b_inline_pivot_lugs(d: _BDims) -> cq.Workplane:
    lug_base_z = d.handle_top_z - 0.008
    lug_top_z = d.trig_pivot_z + 0.005
    lug_height = lug_top_z - lug_base_z
    lug_cz = (lug_base_z + lug_top_z) / 2.0
    lug_x_len = 0.018
    lug_thickness = 0.005

    def side_lug(y_inner: float):
        return (
            cq.Workplane("XZ")
            .workplane(offset=y_inner)
            .center(d.trig_pivot_x, lug_cz)
            .rect(lug_x_len, lug_height)
            .extrude(lug_thickness)
            .edges("|Y")
            .fillet(0.002)
        )

    left_lug = side_lug(d.pivot_y_half)
    right_lug = side_lug(-(d.pivot_y_half + lug_thickness))
    bar_z = lug_base_z + 0.004
    bar_h = 0.006
    bar_span = 2 * d.pivot_y_half + 2 * lug_thickness
    bridge = (
        cq.Workplane("XZ")
        .workplane(offset=-(d.pivot_y_half + lug_thickness))
        .center(d.trig_pivot_x, bar_z + bar_h / 2.0)
        .rect(lug_x_len, bar_h)
        .extrude(bar_span)
    )
    return left_lug.union(right_lug).union(bridge)


def _b_inline_pivot_pin(d: _BDims) -> cq.Workplane:
    return (
        cq.Workplane("XZ")
        .workplane(offset=d.pivot_y_half + 0.004)
        .center(d.trig_pivot_x, d.trig_pivot_z)
        .circle(0.003)
        .extrude(-(2 * d.pivot_y_half + 0.008))
    )


def _b_rivet(d: _BDims, x: float, z: float) -> cq.Workplane:
    # Start the rivet 1 mm inside the handle outer face so it straddles the
    # surface (embeds) and is never a floating island.
    return (
        cq.Workplane("XZ")
        .workplane(offset=d.handle_y_half - 0.0012)
        .center(x, z)
        .circle(0.0025)
        .extrude(0.0032)
    )


def _b_cartridge_mesh(d: _BDims, assets):
    body = (
        cq.Workplane("XY")
        .circle(d.cart_r)
        .extrude(d.cart_len)
        .translate((0, 0, -d.cart_len / 2.0))
        .edges(">Z or <Z")
        .fillet(0.004)
    )
    body = body.rotate((0, 0, 0), (0, 1, 0), 90.0)
    return mesh_from_cadquery(body, "cartridge_body", assets=assets)


def _b_front_collar_mesh(d: _BDims, assets):
    collar = (
        cq.Workplane("YZ")
        .workplane(offset=d.cart_len / 2.0 - 0.006)
        .circle(d.cart_r)
        .workplane(offset=0.022)
        .circle(0.011)
        .loft()
    )
    return mesh_from_cadquery(collar, "front_collar", assets=assets)


def _b_nozzle_mesh(d: _BDims, assets):
    # Start the nozzle base a few mm back inside the collar's narrow front so the
    # two visuals fuse (avoids a disconnected nozzle island at knife-edge tol).
    nz_base_x = d.cart_len / 2.0 + 0.012
    nozzle = (
        cq.Workplane("YZ")
        .workplane(offset=nz_base_x)
        .circle(0.011)
        .workplane(offset=0.059)
        .circle(0.0045)
        .loft()
    )
    bore = (
        cq.Workplane("YZ").workplane(offset=nz_base_x + 0.030).circle(0.0028).extrude(0.030)
    )
    nozzle = nozzle.cut(bore)
    return mesh_from_cadquery(nozzle, "nozzle", assets=assets)


def _b_trigger_pistol(d: _BDims, assets):
    pts = [
        (0.009, 0.008),
        (0.016, -0.006),
        (0.020, -0.040),
        (0.014, -0.078),
        (0.000, -0.080),
        (-0.002, -0.045),
        (-0.012, -0.012),
        (-0.011, 0.006),
    ]
    blade = (
        cq.Workplane("XZ")
        .polyline(pts)
        .close()
        .extrude(0.014)
        .translate((0, 0.007, 0))
        .edges("|Y")
        .fillet(0.0035)
    )
    hub = cq.Workplane("XZ").workplane(offset=0.011).circle(0.0095).extrude(-0.022)
    return mesh_from_cadquery(blade.union(hub), "trigger_blade", assets=assets)


def _b_trigger_inline(d: _BDims, assets):
    lever_w = 0.014
    pts = [
        (0.005, -0.004),
        (0.006, 0.028),
        (0.009, 0.038),
        (0.004, 0.046),
        (-0.004, 0.046),
        (-0.009, 0.038),
        (-0.006, 0.028),
        (-0.005, -0.004),
    ]
    lever = (
        cq.Workplane("XZ")
        .workplane(offset=-lever_w / 2.0)
        .polyline(pts)
        .close()
        .extrude(lever_w)
        .edges("|Y")
        .fillet(0.003)
    )
    hub = cq.Workplane("XZ").workplane(offset=-0.020 / 2.0).circle(0.007).extrude(0.020)
    return mesh_from_cadquery(lever.union(hub), "trigger_blade", assets=assets)


def _b_plunger_mesh(d: _BDims, assets):
    plate = (
        cq.Workplane("YZ").workplane(offset=d.plate_x).circle(d.cart_r - 0.002).extrude(-0.008)
    )
    rod = (
        cq.Workplane("YZ").workplane(offset=d.plate_x - 0.008).circle(0.0045).extrude(-d.rod_len)
    )
    plunger = plate.union(rod)
    rear_x = d.plate_x - 0.008 - d.rod_len
    handle = (
        cq.Workplane("XZ")
        .workplane(offset=0.006)
        .center(rear_x - 0.010, 0)
        .rect(0.020, 0.055)
        .extrude(-0.012)
        .edges("|Y")
        .fillet(0.004)
    )
    return mesh_from_cadquery(plunger.union(handle), "plunger_rod", assets=assets)


# ===========================================================================
# A-FAMILY assembly
# ===========================================================================
def _build_a_family(model: ArticulatedObject, r: ResolvedCaulkingGunConfig, mats, *, assets):
    d = _a_dims(r)
    lift = (0.0, 0.0, d.axis_z)
    body = model.part("barrel_body")

    # Main shell mesh by cradle choice.
    if r.cradle == "half_barrel":
        shell = _a_barrel_cradle(d)
    elif r.cradle == "closed_barrel":
        shell = _a_barrel_tube_closed(d)
    else:  # sausage_tube
        shell = _a_barrel_tube_sausage(d)
    body.visual(
        mesh_from_cadquery(shell.translate(lift), "barrel_cradle", assets=assets),
        material=mats["shell"],
        name="barrel_cradle", material_class_id=("metal.aluminum_bare" if r.palette_style == "aluminum_sausage" else "metal.paint_coated"),
    )
    body.visual(
        mesh_from_cadquery(_a_front_collar(d).translate(lift), "front_collar", assets=assets),
        material=mats["collar"],
        name="front_collar", material_class_id="metal.paint_coated",
    )
    body.visual(
        mesh_from_cadquery(_a_rear_cap(d).translate(lift), "rear_cap", assets=assets),
        material=mats["cap"],
        name="rear_cap", material_class_id="plastic.opaque_glossy_molded",
    )
    body.visual(
        mesh_from_cadquery(_a_handle_frame(d).translate(lift), "handle_frame", assets=assets),
        material=mats["grip"],
        name="handle_frame", material_class_id="metal.paint_coated",
    )
    body.visual(
        mesh_from_cadquery(_a_grip_wing(d).translate(lift), "grip_wing", assets=assets),
        material=mats["grip"],
        name="grip_wing", material_class_id="plastic.opaque_glossy_molded",
    )
    body.visual(
        mesh_from_cadquery(_a_pivot_pin(d).translate(lift), "pivot_pin", assets=assets),
        material=mats["rod"],
        name="pivot_pin", material_class_id="metal.steel_bare",
    )
    body.inertial = Inertial.from_geometry(
        Box((d.barrel_len, 2.0 * d.rear_cap_r, 2.0 * d.rear_cap_r)),
        mass=0.45,
        origin=Origin(xyz=(d.barrel_x0 + d.barrel_len / 2.0, 0.0, d.axis_z)),
    )

    # Cartridge (FIXED) — for sausage_tube use a front_cap part instead.
    if r.cradle == "sausage_tube":
        # Anchor the FIXED seat on the cap base ring WALL (the barrel axis is
        # hollow there): a point in the annular wall at x=tube_x1, z just below
        # the axis. Both the barrel tube wall and the cap base ring have solid
        # surface there. Shift the cap meshes so the world rest pose is unchanged.
        front_cap = model.part("front_cap")
        fc_wall_z = d.tube_r + 0.0015
        fc_orig = Origin(xyz=(-d.tube_x1, 0.0, fc_wall_z))
        front_cap.visual(
            mesh_from_cadquery(_a_front_cone_cap(d), "front_cone", assets=assets),
            origin=fc_orig,
            material=mats["cap"],
            name="front_cone", material_class_id="plastic.opaque_glossy_molded",
        )
        front_cap.visual(
            mesh_from_cadquery(_a_sausage_nozzle_cone(d), "nozzle_cone", assets=assets),
            origin=fc_orig,
            material=mats["nozzle"],
            name="nozzle_cone", material_class_id="plastic.opaque_glossy_molded",
        )
        front_cap.visual(
            mesh_from_cadquery(_a_sausage_white_tip(d), "white_tip", assets=assets),
            origin=fc_orig,
            material=mats["tip"],
            name="white_tip", material_class_id="plastic.opaque_glossy_molded",
        )
        front_cap.inertial = Inertial.from_geometry(
            Box((0.06, 2.0 * d.tube_r, 2.0 * d.tube_r)),
            mass=0.05,
            origin=Origin(xyz=(0.02, 0.0, -fc_wall_z)),
        )
        model.articulation(
            "front_cap_seat",
            ArticulationType.FIXED,
            parent=body,
            child=front_cap,
            origin=Origin(xyz=(d.tube_x1, 0.0, d.axis_z - fc_wall_z)),
        )
    else:
        cartridge = model.part("cartridge")
        cartridge.visual(
            mesh_from_cadquery(_a_cartridge_tube(d), "cartridge_tube", assets=assets),
            material=mats["cartridge"],
            name="cartridge_tube", material_class_id="plastic.opaque_glossy_molded",
        )
        cartridge.visual(
            mesh_from_cadquery(_a_cartridge_label(d), "cartridge_label", assets=assets),
            material=mats["label"],
            name="cartridge_label", material_class_id="paper.plain_sheet",
        )
        cartridge.visual(
            mesh_from_cadquery(_a_nozzle_cone(d), "nozzle_cone", assets=assets),
            material=mats["nozzle"],
            name="nozzle_cone", material_class_id="plastic.opaque_glossy_molded",
        )
        cartridge.visual(
            mesh_from_cadquery(_a_white_tip(d), "white_tip", assets=assets),
            material=mats["tip"],
            name="white_tip", material_class_id="plastic.opaque_glossy_molded",
        )
        cartridge.inertial = Inertial.from_geometry(
            Box((d.tube_len, 2.0 * d.tube_r, 2.0 * d.tube_r)),
            mass=0.30,
            origin=Origin(xyz=(d.tube_x0 + d.tube_len / 2.0, 0.0, 0.0)),
        )
        model.articulation(
            "cartridge_seat",
            ArticulationType.FIXED,
            parent=body,
            child=cartridge,
            origin=Origin(xyz=(0.0, 0.0, d.axis_z)),
        )

    # Plunger (PRISMATIC) — ratchet_jhook or ring_pull tail.
    # Anchor the joint origin on the bored rear cap (real frame surface near the
    # rod) instead of the hollow barrel axis; shift the rod-local meshes so the
    # world rest pose is unchanged.
    plunger = model.part("plunger")
    p_shift = d.rod_front_x - d.rear_cap_x
    p_orig = Origin(xyz=(p_shift, 0.0, 0.0))
    plunger.visual(
        mesh_from_cadquery(_a_plunger_rod(d), "plunger_rod", assets=assets),
        origin=p_orig,
        material=mats["shell"],
        name="plunger_rod", material_class_id="metal.steel_bare",
    )
    plunger.visual(
        mesh_from_cadquery(_a_cart_plunger(d), "cart_plunger", assets=assets),
        origin=p_orig,
        material=mats["cartridge"],
        name="cart_plunger", material_class_id="plastic.opaque_glossy_molded",
    )
    if r.plunger_drive == "ring_pull":
        plunger.visual(
            mesh_from_cadquery(_a_ring_handle(d), "pull_ring", assets=assets),
            origin=p_orig,
            material=mats["rod"],
            name="pull_ring", material_class_id="metal.steel_bare",
        )
    else:  # ratchet_jhook
        plunger.visual(
            mesh_from_cadquery(_a_hook_handle(d), "hook_handle", assets=assets),
            origin=p_orig,
            material=mats["shell"],
            name="hook_handle", material_class_id="metal.steel_bare",
        )
    total_len = d.rod_front_x - d.rod_back_x
    plunger.inertial = Inertial.from_geometry(
        Box((total_len, 2.0 * d.rod_push_r, 2.0 * d.rod_push_r)),
        mass=0.08,
        origin=Origin(xyz=(p_shift - total_len / 2.0, 0.0, 0.0)),
    )
    model.articulation(
        "plunger_drive",
        ArticulationType.PRISMATIC,
        parent=body,
        child=plunger,
        origin=Origin(xyz=(d.rear_cap_x, 0.0, d.axis_z)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=300.0, velocity=0.05, lower=0.0, upper=r.plunger_travel),
    )

    # Trigger (REVOLUTE) — bracket_wing high pivot.
    trigger = model.part("trigger")
    trigger.visual(
        mesh_from_cadquery(_a_trigger_blade(d), "trigger_blade", assets=assets),
        material=mats["grip"],
        name="trigger_blade", material_class_id="plastic.opaque_glossy_molded",
    )
    trigger.inertial = Inertial.from_geometry(
        Box((0.02, 0.026, 0.060)),
        mass=0.02,
        origin=Origin(xyz=(0.0, 0.0, -0.030)),
    )
    model.articulation(
        "trigger_pivot",
        ArticulationType.REVOLUTE,
        parent=body,
        child=trigger,
        origin=Origin(xyz=(d.pivot_x, 0.0, d.axis_z + d.pivot_z)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=40.0, velocity=2.0, lower=0.0, upper=r.trigger_open),
    )


# ===========================================================================
# B-FAMILY assembly
# ===========================================================================
def _build_b_family(model: ArticulatedObject, r: ResolvedCaulkingGunConfig, mats, *, assets):
    d = _b_dims(r)
    frame = model.part("frame")

    # Frame shell: cradle/cage + front ring + rear plate + grip + lugs.
    use_inline = r.grip == "inline_handle"
    if r.cradle == "rib_cage":
        shell = _b_front_ring(d)
        shell = shell.union(_b_rear_plate(d))
        shell = shell.union(_b_spine_rail(d))
    else:  # skeleton_halfpipe
        shell = _b_cradle_halfpipe(d)
        shell = shell.union(_b_front_ring(d))
        shell = shell.union(_b_rear_plate(d))

    if use_inline:
        shell = shell.union(_b_d_handle(d))
        shell = shell.union(_b_inline_pivot_lugs(d))
        # Connector collar: a solid block from the rear plate into the handle
        # front, guaranteeing a thick fusion (the half-pipe wall alone meets the
        # handle along a thin seam that splits into a mesh island).
        collar = (
            cq.Workplane("XZ")
            .workplane(offset=-d.handle_y_half)
            .center((d.back_x - 0.006 + d.handle_front_x) / 2.0, 0.0)
            .rect(abs(d.handle_front_x - (d.back_x - 0.006)) + 0.004, 2.0 * d.cradle_outer_r)
            .extrude(2.0 * d.handle_y_half)
        )
        shell = shell.union(collar)
    elif r.grip == "pistol_grip":
        shell = shell.union(_b_grip_pistol(d))
        shell = shell.union(_b_pivot_lugs(d))
    else:  # d_ring_loop — bosses union into frame; loop is a separate mesh visual
        shell = shell.union(_b_dring_bosses(d))
        shell = shell.union(_b_pivot_lugs(d))

    # clean() merges coincident faces so the union meshes as one connected
    # shell (otherwise internal seams can tessellate into mesh islands).
    try:
        shell = shell.clean()
    except Exception:
        pass
    frame.visual(mesh_from_cadquery(shell, "frame_shell", assets=assets), material=mats["shell"], name="frame_shell", material_class_id=("metal.aluminum_bare" if r.palette_style == "aluminum_sausage" else "metal.paint_coated"))

    # Pivot pin (inline uses its own top-mounted pin).
    if use_inline:
        frame.visual(
            mesh_from_cadquery(_b_inline_pivot_pin(d), "pivot_pin", assets=assets),
            material=mats["rod"],
            name="pivot_pin", material_class_id="metal.steel_bare",
        )
    else:
        frame.visual(
            mesh_from_cadquery(_b_pivot_pin(d), "pivot_pin", assets=assets),
            material=mats["rod"],
            name="pivot_pin", material_class_id="metal.steel_bare",
        )

    # D-ring loop bar (a separate non-moving steel visual welded onto frame).
    if r.grip == "d_ring_loop":
        frame.visual(
            _b_dring_loop_mesh(d, assets),
            material=mats["grip"],
            name="dring_loop", material_class_id="metal.steel_bare",
        )

    # Rib cage rods (multiplicity, Rule 1: frame visuals).
    if r.cradle == "rib_cage":
        n = r.rib_count
        for i in range(n):
            angle_deg = (
                _B_RIB_ARC_START_DEG
                + i * (_B_RIB_ARC_END_DEG - _B_RIB_ARC_START_DEG) / max(n - 1, 1)
            )
            frame.visual(
                mesh_from_cadquery(
                    _b_rib_rod_geometry(d, math.radians(angle_deg)), f"rib_rod_{i}", assets=assets
                ),
                material=mats["rod"],
                name=f"rib_rod_{i}", material_class_id="metal.steel_bare",
            )

    # Inline rivet decorations (Rule 1: fixed visuals).
    if use_inline:
        # Rivets along the solid top rail (z in the top-rail wall band) so they
        # always embed into solid handle material, not the open window.
        rivet_z = d.handle_top_z - 0.005
        for i in range(4):
            rivet_x = d.handle_rear_x + 0.012 + i * 0.018
            frame.visual(
                mesh_from_cadquery(_b_rivet(d, rivet_x, rivet_z), f"rivet_{i}", assets=assets),
                material=mats["rod"],
                name=f"rivet_{i}", material_class_id="metal.steel_bare",
            )

    frame.inertial = Inertial.from_geometry(
        Box((d.barrel_len, 2.0 * d.cradle_outer_r, 2.0 * (d.cradle_outer_r + d.grip_len))),
        mass=0.45,
        origin=Origin(xyz=(0.0, 0.0, -d.grip_len / 3.0)),
    )

    # Cartridge (FIXED). Anchor the seat at the cartridge rear face (where the
    # rear-plate bore solid and the cartridge rear disc both have surface near
    # the axis); shift the cartridge meshes so the world rest pose is unchanged.
    cartridge = model.part("cartridge")
    cart_anchor_x = -d.cart_len / 2.0
    cart_orig = Origin(xyz=(-cart_anchor_x, 0.0, 0.0))
    cartridge.visual(
        _b_cartridge_mesh(d, assets), origin=cart_orig, material=mats["cartridge"], name="cartridge_body", material_class_id="plastic.opaque_glossy_molded"
    )
    cartridge.visual(
        _b_front_collar_mesh(d, assets), origin=cart_orig, material=mats["collar"], name="front_collar", material_class_id="plastic.opaque_glossy_molded"
    )
    cartridge.visual(_b_nozzle_mesh(d, assets), origin=cart_orig, material=mats["nozzle"], name="nozzle", material_class_id="plastic.opaque_glossy_molded")
    cartridge.inertial = Inertial.from_geometry(
        Box((d.cart_len, 2.0 * d.cart_r, 2.0 * d.cart_r)),
        mass=0.30,
        origin=Origin(xyz=(-cart_anchor_x, 0.0, 0.0)),
    )
    model.articulation(
        "frame_to_cartridge",
        ArticulationType.FIXED,
        parent=frame,
        child=cartridge,
        origin=Origin(xyz=(cart_anchor_x, 0.0, 0.0)),
    )

    # Trigger (REVOLUTE).
    trigger = model.part("trigger")
    if use_inline:
        trigger.visual(_b_trigger_inline(d, assets), material=mats["grip"], name="trigger_blade", material_class_id="plastic.opaque_glossy_molded")
        trig_origin = Origin(xyz=(d.trig_pivot_x, 0.0, d.trig_pivot_z))
        trig_inertia_z = 0.025
    else:
        trigger.visual(_b_trigger_pistol(d, assets), material=mats["shell"], name="trigger_blade", material_class_id="metal.paint_coated")
        trig_origin = Origin(xyz=(d.pivot_x, 0.0, d.pivot_z))
        trig_inertia_z = -0.040
    trigger.inertial = Inertial.from_geometry(
        Box((0.03, 0.014, 0.08)),
        mass=0.02,
        origin=Origin(xyz=(0.0, 0.0, trig_inertia_z)),
    )
    model.articulation(
        "frame_to_trigger",
        ArticulationType.REVOLUTE,
        parent=frame,
        child=trigger,
        origin=trig_origin,
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=15.0, velocity=3.0, lower=0.0, upper=r.trigger_open),
    )

    # Plunger (PRISMATIC) — thumb_plate. Anchor the joint origin at the rear
    # plate bore plane (real frame surface near the rod) and shift the plunger
    # mesh so the world rest pose is unchanged.
    plunger = model.part("plunger")
    pl_anchor_x = d.back_x
    pl_orig = Origin(xyz=(-pl_anchor_x, 0.0, 0.0))
    plunger.visual(_b_plunger_mesh(d, assets), origin=pl_orig, material=mats["rod"], name="plunger_rod", material_class_id="metal.steel_bare")
    plunger.inertial = Inertial.from_geometry(
        Box((d.rod_len, 2.0 * d.cart_r, 2.0 * d.cart_r)),
        mass=0.10,
        origin=Origin(xyz=(-pl_anchor_x + d.plate_x - d.rod_len / 2.0, 0.0, 0.0)),
    )
    model.articulation(
        "frame_to_plunger",
        ArticulationType.PRISMATIC,
        parent=frame,
        child=plunger,
        origin=Origin(xyz=(pl_anchor_x, 0.0, 0.0)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=300.0, velocity=0.05, lower=0.0, upper=r.plunger_travel),
    )


# ===========================================================================
# Build
# ===========================================================================
def build_caulking_gun(
    config: CaulkingGunConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    palette = PALETTES[r.palette_style]
    mats = {
        key: model.material(f"caulk_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in palette.items()
    }

    if r.is_a_family:
        _build_a_family(model, r, mats, assets=assets)
    else:
        _build_b_family(model, r, mats, assets=assets)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_caulking_gun(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_caulking_gun(config_from_seed(seed), assets=assets)


# ===========================================================================
# Tests
# ===========================================================================
def run_caulking_gun_tests(
    object_model: ArticulatedObject,
    config: CaulkingGunConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)

    root_name = "barrel_body" if r.is_a_family else "frame"
    body = object_model.get_part(root_name)
    plunger = object_model.get_part("plunger")
    trigger = object_model.get_part("trigger")

    # ---- Captured-shaft / pin / seated allowances (element-scoped). ----
    if r.is_a_family:
        # Rod slides through the bored rear cap (captured shaft).
        ctx.expect_overlap(
            plunger, body, axes="x", elem_a="plunger_rod", elem_b="rear_cap",
            min_overlap=0.004, name="rod stays inserted through the rear cap bore",
        )
        ctx.allow_overlap(
            plunger, body, elem_a="plunger_rod", elem_b="rear_cap",
            reason="The steel plunger rod intentionally slides through the bored rear cap.",
        )
        ctx.allow_overlap(
            plunger, body, elem_a="plunger_rod", elem_b="handle_frame",
            reason="The plunger rod passes through the rod-guide boss in the handle frame.",
        )
        ctx.allow_overlap(
            plunger, body, elem_a="cart_plunger", elem_b="barrel_cradle",
            reason="The push disc rides captured inside the barrel / cartridge bore.",
        )
        if r.cradle == "sausage_tube":
            consumable = object_model.get_part("front_cap")
            ctx.allow_overlap(
                consumable, body, elem_a="front_cone", elem_b="barrel_cradle",
                reason="The threaded front cap screws onto / overlaps the barrel tube front wall.",
            )
            ctx.allow_overlap(
                plunger, consumable, reason="Push disc seals against the barrel/front-cap bore.",
            )
            ctx.allow_overlap(
                plunger, body, elem_a="plunger_rod", elem_b="barrel_cradle",
                reason="The push disc seals against the closed sausage barrel bore wall.",
            )
        else:
            consumable = object_model.get_part("cartridge")
            ctx.allow_overlap(
                consumable, body, reason="Cartridge is a consumable seated inside the cradle.",
            )
            ctx.allow_overlap(
                plunger, consumable,
                reason="The push disc / cart plunger ride captured inside the cartridge tube.",
            )
        # Trigger hub captures the pivot pin and rotates between the frame lugs.
        ctx.allow_overlap(
            trigger, body, elem_a="trigger_blade", elem_b="pivot_pin",
            reason="The trigger hub pivots captured on the steel pin.",
        )
        ctx.allow_overlap(
            trigger, body, elem_a="trigger_blade", elem_b="handle_frame",
            reason="The trigger hub rotates between the frame pivot lugs (captured pivot).",
        )
    else:
        # B family: plunger rod/plate slide inside the cradle + through rear plate.
        ctx.allow_overlap(
            plunger, body, elem_a="plunger_rod", elem_b="frame_shell",
            reason="Plunger rod/plate slides inside the cradle and through the rear plate bore.",
        )
        cartridge = object_model.get_part("cartridge")
        ctx.allow_overlap(
            plunger, cartridge, elem_a="plunger_rod", elem_b="cartridge_body",
            reason="Push plate bears on the rear of the cartridge contents (solid proxy).",
        )
        ctx.allow_overlap(
            cartridge, body, elem_a="cartridge_body", elem_b="frame_shell",
            reason="Silicone cartridge is seated/nested inside the open cradle.",
        )
        ctx.allow_overlap(
            cartridge, body, elem_a="front_collar", elem_b="frame_shell",
            reason="Cartridge front shoulder seats into the front cap ring bore.",
        )
        if r.cradle == "rib_cage":
            for i in range(r.rib_count):
                ctx.allow_overlap(
                    cartridge, body, elem_a="cartridge_body", elem_b=f"rib_rod_{i}",
                    reason="Cartridge nests inside the open rib cage (rib rods cradle it).",
                )
                ctx.allow_overlap(
                    cartridge, body, elem_a="front_collar", elem_b=f"rib_rod_{i}",
                    reason="Cartridge front shoulder passes between the cage rib rods.",
                )
                ctx.allow_overlap(
                    plunger, body, elem_a="plunger_rod", elem_b=f"rib_rod_{i}",
                    reason="Plunger rod runs down the rib cage axis between the ribs.",
                )
        ctx.allow_overlap(
            trigger, body, elem_a="trigger_blade", elem_b="pivot_pin",
            reason="Trigger pivot hub captures the steel pivot pin.",
        )
        ctx.allow_overlap(
            trigger, body, elem_a="trigger_blade", elem_b="frame_shell",
            reason="Trigger hub rotates between the frame pivot lugs (captured pivot fit).",
        )
        if r.grip == "d_ring_loop":
            ctx.allow_overlap(
                trigger, body, elem_a="trigger_blade", elem_b="dring_loop",
                reason="The trigger swings inside the D-ring loop opening.",
            )
            ctx.allow_overlap(
                cartridge, body, elem_a="cartridge_body", elem_b="dring_loop",
                reason="The D-ring loop welds onto the cradle underside beneath the seated cartridge.",
            )

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    # All captured hinge/shaft/seated joints omit MatingContract (grandfathered);
    # the flat 0.015 m articulation-origin baseline runs in the compiler.
    ctx.fail_if_joint_mating_has_gap()

    # ---- slot_choices recorded. ----
    ctx.check(
        "slot_choices recorded (rib_count encoded for rib_cage)",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    # ---- Joint topology / semantics. ----
    plunger_joint_name = "plunger_drive" if r.is_a_family else "frame_to_plunger"
    trigger_joint_name = "trigger_pivot" if r.is_a_family else "frame_to_trigger"
    pj = object_model.get_articulation(plunger_joint_name)
    tj = object_model.get_articulation(trigger_joint_name)
    ctx.check(
        "plunger is PRISMATIC along +X",
        pj.articulation_type == ArticulationType.PRISMATIC and round(abs(pj.axis[0]), 3) == 1.0,
        details=f"type={pj.articulation_type} axis={tuple(pj.axis)}",
    )
    ctx.check(
        "trigger is REVOLUTE about +Y",
        tj.articulation_type == ArticulationType.REVOLUTE and round(abs(tj.axis[1]), 3) == 1.0,
        details=f"type={tj.articulation_type} axis={tuple(tj.axis)}",
    )

    # ---- Cartridge / front_cap FIXED seat. ----
    seat_name = "front_cap_seat" if r.cradle == "sausage_tube" else (
        "cartridge_seat" if r.is_a_family else "frame_to_cartridge"
    )
    sj = object_model.get_articulation(seat_name)
    ctx.check(
        "consumable is FIXED-seated",
        sj.articulation_type == ArticulationType.FIXED,
        details=f"type={sj.articulation_type}",
    )

    # ---- Plunger advances toward the muzzle (+X). ----
    rest_p = ctx.part_world_position(plunger)
    with ctx.pose({pj: r.plunger_travel * 0.9}):
        adv_p = ctx.part_world_position(plunger)
    if rest_p is not None and adv_p is not None:
        ctx.check(
            "driving the plunger advances the rod toward the muzzle (+X)",
            adv_p[0] > rest_p[0] + r.plunger_travel * 0.5,
            details=f"rest_x={rest_p[0]:.4f} adv_x={adv_p[0]:.4f}",
        )

    # ---- Trigger swings when squeezed (lower blade moves rearward / tips). ----
    with ctx.pose({tj: 0.0}):
        t_rest = ctx.part_world_aabb(trigger)
    with ctx.pose({tj: r.trigger_open * 0.85}):
        t_sq = ctx.part_world_aabb(trigger)
    if t_rest is not None and t_sq is not None:
        moved_x = abs(t_sq[0][0] - t_rest[0][0]) + abs(t_sq[1][0] - t_rest[1][0])
        ctx.check(
            "squeezing the trigger swings the lever",
            moved_x > 0.004,
            details=f"rest_x=({t_rest[0][0]:.4f},{t_rest[1][0]:.4f}) sq_x=({t_sq[0][0]:.4f},{t_sq[1][0]:.4f})",
        )

    # ---- Nozzle / tip points forward past the shell (+X muzzle identity). ----
    muzzle_part = (
        object_model.get_part("front_cap")
        if r.cradle == "sausage_tube"
        else object_model.get_part("cartridge")
    )
    tip_aabb = ctx.part_element_world_aabb(muzzle_part, elem="white_tip" if r.is_a_family else "nozzle")
    body_aabb = ctx.part_world_aabb(body)
    if tip_aabb is not None and body_aabb is not None:
        ctx.check(
            "nozzle/tip points forward past the shell (+X muzzle)",
            tip_aabb[1][0] >= body_aabb[1][0] - 0.004,
            details=f"tip_max_x={tip_aabb[1][0]:.4f} body_max_x={body_aabb[1][0]:.4f}",
        )

    # ---- Rib cage: N rib rods present (multiplicity). ----
    if r.cradle == "rib_cage":
        rib_names = [v.name for v in body.visuals if v.name and v.name.startswith("rib_rod_")]
        ctx.check(
            "rib cage emits N rib rods (Rule 1, no per-rib joint)",
            len(rib_names) == r.rib_count,
            details=f"emitted={sorted(rib_names)} expected N={r.rib_count}",
        )

    # ---- Gun rests near the ground. ----
    if body_aabb is not None:
        ctx.check(
            "gun root rests near the ground",
            body_aabb[0][2] < 0.03,
            details=f"z_min={body_aabb[0][2]:.4f}",
        )

    return ctx.report()


__all__ = (
    "CaulkingGunConfig",
    "ResolvedCaulkingGunConfig",
    "build_caulking_gun",
    "build_seeded_caulking_gun",
    "config_from_seed",
    "resolve_config",
    "run_caulking_gun_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
