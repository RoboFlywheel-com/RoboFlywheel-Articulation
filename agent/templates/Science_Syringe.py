# SPDX-License-Identifier: Apache-2.0

"""Medical hypodermic syringe modular template.

NOTE on the slug: ``syringe`` here = a **medical hypodermic syringe** — a
graduated transparent barrel with finger flanges, a needle / nozzle tip at the
front, and a plunger that slides (PRISMATIC) inside the bore to dispense. It is
NOT a vial / dropper (no sliding piston), NOT an insulin pen / dose-dial pen
(no rotary dose mechanism), and NOT a pipette (no button + tip ejector).

Sourced from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/Science_Syringe.md`` and the syringe
5-star pool (1 parent + 10 slot-fork variants), all synced under
``data/records/`` (parent
``rec_build-...-syri_..._042137c8`` + ``rec_syringe_var_*``).

Structure (pattern = ``mixed``: 4 parallel visual-swap slots + 1 multiplicity
axis on a FIXED 2-part skeleton). The hero mechanism — present in EVERY seed —
is the plunger sliding (PRISMATIC ``barrel_to_plunger``) inside the barrel bore:

  * root ``barrel_assembly`` — barrel shell + liquid + scale marks + flange +
    tip/hub + needle, all visuals carrying the same root rest transform.
  * child ``plunger`` — gasket + rod + thumb-rest, joined to the barrel by the
    single non-FIXED articulation ``barrel_to_plunger`` (PRISMATIC, the
    identity joint).

Orientation (all source records): geometry is authored along a local +Z axis
(needle toward local -Z, plunger entering from local +Z), then the whole
assembly is rolled -90 deg about X (barrel axis -> world +Y, needle toward -Y)
and lifted so the lowest surface sits at z = 0. The prismatic axis is joint-
local -Z (world -Y in the rest pose), so positive q pushes toward the needle.

Slots (all are visual-element swaps on the two skeleton parts, never part
replacement; Rule 1: non-articulating decorations are ``parent.visual``):

  * Slot A ``tip_hub`` — luer_lock_needle / slip_tip / blunt_cannula /
    safety_shield (front-end visuals on ``barrel_assembly``).
  * Slot B ``flange`` — flat_wings / ring_collar / ribbed_grip (rear grip
    visual on ``barrel_assembly``).
  * Slot C ``plunger_rod`` — plus_cross / flat_plate (rod section on
    ``plunger``).
  * Slot D ``barrel_form`` — straight_cylindrical / slim_insulin / wide_stepped
    (barrel shell geometry family; drives barrel radius/length equation).

Multiplicity: ``tick_count`` in {10, 16, 24} (N_range [6, 40]) controls the
graduation tick count, merged into the SINGLE ``scale_marks`` visual (no joint;
Rule 1). Encoded into the slot_choice tuple as ``("tick_count", f"n{N}")``.

A(4) x B(3) x C(2) x D(3) = 72 slot topology combinations (>> diversity floor
of 10). The gasket-in-bore seal fit is an intentional element-scoped overlap.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, replace
from typing import Literal

import cadquery as cq

from sdk import (
    AppearanceOnlySpec,
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
)

__modular__ = True

# ---------------------------------------------------------------------------
# Slot enums
# ---------------------------------------------------------------------------
TipHub = Literal["luer_lock_needle", "slip_tip", "blunt_cannula", "safety_shield"]
Flange = Literal["flat_wings", "ring_collar", "ribbed_grip"]
PlungerRod = Literal["plus_cross", "flat_plate"]
BarrelForm = Literal["straight_cylindrical", "slim_insulin", "wide_stepped"]
PaletteStyle = Literal[
    "clear_blue_plunger",
    "amber_body",
    "orange_cap",
    "all_white",
    "teal_clinical",
    "insulin_clear",
]

TIP_HUBS: tuple[TipHub, ...] = (
    "luer_lock_needle",
    "slip_tip",
    "blunt_cannula",
    "safety_shield",
)
FLANGES: tuple[Flange, ...] = ("flat_wings", "ring_collar", "ribbed_grip")
PLUNGER_RODS: tuple[PlungerRod, ...] = ("plus_cross", "flat_plate")
BARREL_FORMS: tuple[BarrelForm, ...] = (
    "straight_cylindrical",
    "slim_insulin",
    "wide_stepped",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "clear_blue_plunger",
    "amber_body",
    "orange_cap",
    "all_white",
    "teal_clinical",
    "insulin_clear",
)

# tick_count multiplicity domain (spec): N_range [6, 40], sampled {10, 16, 24}
# (parent = 16). Small N weighted heavier.
TICK_COUNTS: tuple[int, ...] = (10, 16, 24)
TICK_WEIGHTS: tuple[float, ...] = (0.45, 0.35, 0.20)
N_TICK_MIN, N_TICK_MAX = 6, 40

# ---------------------------------------------------------------------------
# Palettes (>=3 colorways drawn from the source records). Keys:
#   liquid, barrel, steel, rubber, plastic, ink, shield.
# Every .visual(material=...) is driven off one of these keys.
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "clear_blue_plunger": {
        "liquid": (0.18, 0.78, 0.74, 0.85),
        "barrel": (0.86, 0.92, 0.93, 0.34),
        "steel": (0.74, 0.76, 0.78, 1.0),
        "rubber": (0.10, 0.10, 0.11, 1.0),
        "plastic": (0.20, 0.42, 0.78, 1.0),
        "ink": (0.10, 0.12, 0.14, 1.0),
        "shield": (0.80, 0.88, 0.95, 0.38),
    },
    "amber_body": {
        "liquid": (0.92, 0.66, 0.20, 0.80),
        "barrel": (0.86, 0.70, 0.44, 0.40),
        "steel": (0.74, 0.76, 0.78, 1.0),
        "rubber": (0.12, 0.10, 0.08, 1.0),
        "plastic": (0.93, 0.93, 0.91, 1.0),
        "ink": (0.16, 0.10, 0.06, 1.0),
        "shield": (0.90, 0.78, 0.55, 0.40),
    },
    "orange_cap": {
        "liquid": (0.20, 0.70, 0.86, 0.82),
        "barrel": (0.88, 0.93, 0.94, 0.34),
        "steel": (0.74, 0.76, 0.78, 1.0),
        "rubber": (0.10, 0.10, 0.11, 1.0),
        "plastic": (0.95, 0.52, 0.14, 1.0),
        "ink": (0.10, 0.12, 0.14, 1.0),
        "shield": (0.97, 0.62, 0.30, 0.42),
    },
    "all_white": {
        "liquid": (0.95, 0.96, 0.97, 0.70),
        "barrel": (0.90, 0.92, 0.93, 0.36),
        "steel": (0.80, 0.82, 0.84, 1.0),
        "rubber": (0.30, 0.30, 0.32, 1.0),
        "plastic": (0.94, 0.95, 0.96, 1.0),
        "ink": (0.40, 0.42, 0.45, 1.0),
        "shield": (0.92, 0.94, 0.96, 0.40),
    },
    "teal_clinical": {
        "liquid": (0.10, 0.62, 0.58, 0.85),
        "barrel": (0.82, 0.93, 0.91, 0.32),
        "steel": (0.72, 0.75, 0.77, 1.0),
        "rubber": (0.08, 0.10, 0.10, 1.0),
        "plastic": (0.12, 0.56, 0.52, 1.0),
        "ink": (0.06, 0.18, 0.16, 1.0),
        "shield": (0.74, 0.92, 0.90, 0.38),
    },
    "insulin_clear": {
        "liquid": (0.96, 0.97, 0.98, 0.55),
        "barrel": (0.88, 0.93, 0.95, 0.30),
        "steel": (0.76, 0.78, 0.80, 1.0),
        "rubber": (0.86, 0.32, 0.30, 1.0),
        "plastic": (0.86, 0.32, 0.30, 1.0),
        "ink": (0.20, 0.22, 0.26, 1.0),
        "shield": (0.86, 0.92, 0.96, 0.36),
    },
}


# ---------------------------------------------------------------------------
# Public / resolved config
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class SyringeConfig:
    tip_hub: TipHub | None = None
    flange: Flange | None = None
    plunger_rod: PlungerRod | None = None
    barrel_form: BarrelForm | None = None
    tick_count: int | None = None
    palette_style: PaletteStyle = "clear_blue_plunger"
    barrel_len_scale: float = 1.0
    barrel_girth_scale: float = 1.0
    plunger_travel_scale: float = 1.0
    name: str = "syringe"


@dataclass(frozen=True)
class _BarrelDims:
    """Per-barrel-form geometry, scaled. All other helpers derive from these."""

    outer_r: float
    wall: float
    inner_r: float
    length: float
    liquid_level: float
    z0: float
    # rim
    rim_extra: float
    # hub / front interface
    hub_top_r: float
    hub_bot_r: float
    hub_len: float
    # needle
    needle_r: float
    needle_len: float
    # plunger
    gasket_len: float
    gasket_r: float
    rod_rib_w: float
    rod_rib_t: float
    rod_plate_w: float
    rod_plate_t: float
    thumb_r: float
    thumb_thick: float
    flange_depth: float
    flange_thick: float
    # derived plunger travel
    gasket_rest_z: float
    rod_len: float
    plunger_travel: float
    rest_lift: float
    # wide-stepped only
    is_stepped: bool
    bore_r: float
    mid_outer_r: float
    step1_z: float
    step2_z: float

    @property
    def z1(self) -> float:
        return self.z0 + self.length


@dataclass(frozen=True)
class ResolvedSyringeConfig:
    tip_hub: TipHub
    flange: Flange
    plunger_rod: PlungerRod
    barrel_form: BarrelForm
    tick_count: int
    palette_style: PaletteStyle
    dims: _BarrelDims
    name: str


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


# ---------------------------------------------------------------------------
# Barrel-form dimension equations (Slot D drives everything else)
# ---------------------------------------------------------------------------
def _barrel_dims(
    form: BarrelForm,
    *,
    flange: Flange = "flat_wings",
    len_scale: float,
    girth_scale: float,
    travel_scale: float,
) -> _BarrelDims:
    if form == "straight_cylindrical":
        outer_r = 0.0058 * girth_scale
        wall = 0.0009
        length = 0.060 * len_scale
        liquid_level = 0.044 * len_scale
        hub_top_r = 0.0050 * girth_scale
        hub_bot_r = 0.0034 * girth_scale
        hub_len = 0.0150
        needle_r = 0.00045
        needle_len = 0.040
        gasket_len = 0.0060
        rod_rib_w = 0.0078 * girth_scale
        thumb_r = 0.0072 * girth_scale
        flange_depth = 0.0085 * girth_scale
        is_stepped = False
        bore_r = mid_outer_r = step1_z = step2_z = 0.0
    elif form == "slim_insulin":
        outer_r = 0.0024 * girth_scale
        wall = 0.0006
        length = 0.080 * len_scale
        liquid_level = 0.060 * len_scale
        hub_top_r = 0.0025 * girth_scale
        hub_bot_r = 0.0018 * girth_scale
        hub_len = 0.012
        needle_r = 0.00020
        needle_len = 0.025
        gasket_len = 0.004
        rod_rib_w = 0.0040 * girth_scale
        thumb_r = 0.0040 * girth_scale
        flange_depth = 0.0060 * girth_scale
        is_stepped = False
        bore_r = mid_outer_r = step1_z = step2_z = 0.0
    else:  # wide_stepped
        bore_r = 0.0100 * girth_scale
        wall = 0.0012
        outer_r = bore_r + wall  # lower / upper neck outer radius
        mid_outer_r = 0.0140 * girth_scale  # wide mid chamber (thinner wall: less solid-lump read)
        length = 0.095 * len_scale
        liquid_level = 0.068 * len_scale
        hub_top_r = bore_r  # slip-fits into the barrel bore at the neck
        hub_bot_r = 0.0034 * girth_scale
        hub_len = 0.0180
        needle_r = 0.00045
        needle_len = 0.040
        gasket_len = 0.0075
        rod_rib_w = 0.0100 * girth_scale
        thumb_r = 0.0095 * girth_scale
        flange_depth = 0.0110 * girth_scale
        is_stepped = True
        step1_z = 0.020 * len_scale
        step2_z = 0.072 * len_scale

    z0 = 0.0
    inner_r = (bore_r if is_stepped else outer_r) - (0.0 if is_stepped else wall)
    if is_stepped:
        inner_r = bore_r
    rim_extra = 0.0007 if outer_r > 0.004 else 0.0005

    # Gasket: snug seal interference in the bore.
    gasket_r = inner_r + 0.00006
    if is_stepped:
        gasket_r = bore_r + 0.00008

    z1 = z0 + length
    gasket_rest_z = liquid_level - gasket_len
    plunger_travel = gasket_rest_z - (z0 + (0.005 if is_stepped else 0.004))
    plunger_travel = max(0.006, plunger_travel * travel_scale)
    # Never let the gasket exit the bore at full stroke (keep it short of neck).
    plunger_travel = min(plunger_travel, gasket_rest_z - (z0 + 0.004))

    thumb_thick = 0.0017 if outer_r > 0.004 else 0.0012
    flange_thick = 0.0016
    rod_rib_t = 0.0011 if outer_r > 0.004 else 0.0008
    rod_plate_w = rod_rib_w * 0.9
    rod_plate_t = rod_rib_t + 0.0009

    # Rod length: at FULL stroke the thumb-rest bottom face must stay at/just
    # above the barrel rim (z1); otherwise the thumb drives ~2-4 cm into the
    # barrel and 穿模s the shell / flanges / scale / liquid.  Thumb-top world_y
    # at rest = liquid_level + rod_len; at full depression subtract
    # plunger_travel.  Size rod_len so the thumb BOTTOM sits >= rim + clearance
    # after the full stroke (this is >> the old (z1 + 0.012) - liquid_level, so
    # the rod still spans the gasket->thumb range and keeps the two connected).
    rim_clear = 0.0010
    rod_len = (z1 - liquid_level) + plunger_travel + thumb_thick + rim_clear

    # rest_lift: after the -90deg X roll a local radius r maps to world
    # z = rest_lift - y_local, so the assembly's lowest point is
    # rest_lift - (widest radial extent).  It MUST cover the true widest part
    # (barrel mid-chamber / rim, ring or ribbed flange, gasket, thumb, rod),
    # not just the thumb disc, or the wide barrel/flange sinks through z=0.
    if is_stepped:
        barrel_ext = max(mid_outer_r, outer_r + 0.0009)  # mid chamber vs rim_r
    else:
        barrel_ext = outer_r + rim_extra
    if flange == "ring_collar":
        flange_ext = max(outer_r * 2.2, (outer_r - 0.0003) + 0.0040)
    elif flange == "ribbed_grip":
        flange_ext = max(flange_depth * 1.15, 0.0085) / 2.0
    else:  # flat_wings
        flange_ext = flange_depth / 2.0
    rest_lift = (
        max(thumb_r, gasket_r, barrel_ext, flange_ext, rod_rib_w / 2.0) + 0.0002
    )

    return _BarrelDims(
        outer_r=outer_r,
        wall=wall,
        inner_r=inner_r,
        length=length,
        liquid_level=liquid_level,
        z0=z0,
        rim_extra=rim_extra,
        hub_top_r=hub_top_r,
        hub_bot_r=hub_bot_r,
        hub_len=hub_len,
        needle_r=needle_r,
        needle_len=needle_len,
        gasket_len=gasket_len,
        gasket_r=gasket_r,
        rod_rib_w=rod_rib_w,
        rod_rib_t=rod_rib_t,
        rod_plate_w=rod_plate_w,
        rod_plate_t=rod_plate_t,
        thumb_r=thumb_r,
        thumb_thick=thumb_thick,
        flange_depth=flange_depth,
        flange_thick=flange_thick,
        gasket_rest_z=gasket_rest_z,
        rod_len=rod_len,
        plunger_travel=plunger_travel,
        rest_lift=rest_lift,
        is_stepped=is_stepped,
        bore_r=bore_r,
        mid_outer_r=mid_outer_r,
        step1_z=step1_z,
        step2_z=step2_z,
    )


# ---------------------------------------------------------------------------
# Seed sampling
# ---------------------------------------------------------------------------
def config_from_seed(seed: int) -> SyringeConfig:
    rng = random.Random(seed)
    tip = rng.choice(TIP_HUBS)
    flange = rng.choice(FLANGES)
    rod = rng.choice(PLUNGER_RODS)
    form = rng.choice(BARREL_FORMS)
    tick = rng.choices(TICK_COUNTS, weights=TICK_WEIGHTS, k=1)[0]
    return SyringeConfig(
        tip_hub=tip,
        flange=flange,
        plunger_rod=rod,
        barrel_form=form,
        tick_count=tick,
        palette_style=rng.choice(PALETTE_STYLES),
        barrel_len_scale=round(rng.uniform(0.92, 1.10), 4),
        barrel_girth_scale=round(rng.uniform(0.92, 1.08), 4),
        plunger_travel_scale=round(rng.uniform(0.88, 1.08), 4),
        name=f"seeded_syringe_{seed}",
    )


def resolve_config(config: SyringeConfig | None = None) -> ResolvedSyringeConfig:
    cfg = config or SyringeConfig()
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)
    tip = _pick(cfg.tip_hub, TIP_HUBS)
    flange = _pick(cfg.flange, FLANGES)
    rod = _pick(cfg.plunger_rod, PLUNGER_RODS)
    form = _pick(cfg.barrel_form, BARREL_FORMS)

    tick = int(cfg.tick_count) if cfg.tick_count is not None else 16
    tick = int(_clamp(tick, N_TICK_MIN, N_TICK_MAX))

    len_scale = _clamp(cfg.barrel_len_scale, 0.92, 1.10)
    girth_scale = _clamp(cfg.barrel_girth_scale, 0.92, 1.08)
    travel_scale = _clamp(cfg.plunger_travel_scale, 0.88, 1.08)

    dims = _barrel_dims(
        form,
        flange=flange,
        len_scale=len_scale,
        girth_scale=girth_scale,
        travel_scale=travel_scale,
    )

    return ResolvedSyringeConfig(
        tip_hub=tip,
        flange=flange,
        plunger_rod=rod,
        barrel_form=form,
        tick_count=tick,
        palette_style=palette_style,
        dims=dims,
        name=cfg.name or "syringe",
    )


def with_overrides(config: SyringeConfig, **kwargs: object) -> SyringeConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: SyringeConfig | ResolvedSyringeConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedSyringeConfig) else resolve_config(config)
    return (
        ("barrel_form", r.barrel_form),
        ("tip_hub", r.tip_hub),
        ("flange", r.flange),
        ("plunger_rod", r.plunger_rod),
        ("tick_count", f"n{r.tick_count}"),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ===========================================================================
# Geometry helpers (adapted verbatim from the 5-star sources, literal
# dimensions promoted to the resolved _BarrelDims namespace).
# ===========================================================================
def PLUNGER_Z_SHIFT(d: _BarrelDims) -> float:
    """The plunger geometry is authored about the bore axis at the gasket rest
    height; we shift it DOWN so the gasket bottom sits at the child-link origin
    (local z = 0). The joint origin is then offset by the same amount along the
    bore so the world placement is unchanged. This guarantees the child link's
    AABB contains (0,0,0), satisfying
    ``fail_if_articulation_origin_far_from_geometry`` (the joint origin lands on
    real gasket geometry, not in the air above the bore)."""
    return d.gasket_rest_z
def _barrel_shell(d: _BarrelDims) -> cq.Workplane:
    """Hollow open-top transparent barrel tube (revolved wall profile)."""
    if d.is_stepped:
        return _barrel_shell_stepped(d)
    outer = d.outer_r
    inner = d.inner_r
    rim = d.outer_r + d.rim_extra
    profile = (
        cq.Workplane("XZ")
        .moveTo(inner, d.z0)
        .lineTo(outer, d.z0)
        .lineTo(outer, d.z1 - 0.0016)
        .lineTo(rim, d.z1 - 0.0012)
        .lineTo(rim, d.z1)
        .lineTo(inner, d.z1)
        .close()
    )
    return profile.revolve(360.0, (0.0, 0.0, 0.0), (0.0, 1.0, 0.0))


def _barrel_shell_stepped(d: _BarrelDims) -> cq.Workplane:
    """Wide-stepped barrel: uniform bore + stepped-out wider mid section.

    Adapted from rec_syringe_var_widebody _barrel_shell L102-L156.
    """
    bore = d.bore_r
    lower_r = d.outer_r
    mid_r = d.mid_outer_r
    upper_r = d.outer_r
    rim_r = upper_r + 0.0009
    step_fillet = 0.0008

    neck_z0 = -0.004
    neck_inner_bot = d.hub_top_r
    neck_outer_bot = d.hub_top_r + 0.0008

    profile = (
        cq.Workplane("XZ")
        .moveTo(neck_inner_bot, neck_z0)
        .lineTo(neck_outer_bot, neck_z0)
        .lineTo(lower_r, d.z0)
        .lineTo(lower_r, d.step1_z - step_fillet)
        .lineTo(lower_r + step_fillet, d.step1_z)
        .lineTo(mid_r - step_fillet, d.step1_z)
        .lineTo(mid_r, d.step1_z + step_fillet)
        .lineTo(mid_r, d.step2_z - step_fillet)
        .lineTo(mid_r - step_fillet, d.step2_z)
        .lineTo(upper_r + step_fillet, d.step2_z)
        .lineTo(upper_r, d.step2_z + step_fillet)
        .lineTo(upper_r, d.z1 - 0.0020)
        .lineTo(rim_r, d.z1 - 0.0015)
        .lineTo(rim_r, d.z1)
        .lineTo(bore, d.z1)
        .lineTo(bore, d.z0)
        .lineTo(neck_inner_bot, neck_z0)
        .close()
    )
    return profile.revolve(360.0, (0.0, 0.0, 0.0), (0.0, 1.0, 0.0))


def _graduation_marks(d: _BarrelDims, n_ticks: int) -> cq.Workplane:
    """Embossed scale tick marks (multiplicity = n_ticks), merged into ONE
    visual (Rule 1: no joint). Major tick (longer) every 5."""
    marks = None
    r = d.mid_outer_r if d.is_stepped else d.outer_r
    if d.is_stepped:
        z_lo = d.step1_z + 0.005
        z_hi = d.step2_z - 0.005
    else:
        z_lo = 0.012 * (d.length / (0.060)) if not d.is_stepped else 0.012
        z_lo = max(0.008, min(z_lo, 0.012))
        z_hi = d.liquid_level + 0.001
    n = max(2, int(n_ticks))
    for i in range(n + 1):
        z = z_lo + (z_hi - z_lo) * i / n
        major = i % 5 == 0
        half_len = 0.0026 if major else 0.0014
        tick = (
            cq.Workplane("XY")
            .workplane(offset=z)
            .box(0.0008, half_len, 0.0006, centered=(True, True, True))
            .translate((r - 0.0001, 0.0, 0.0))
        )
        marks = tick if marks is None else marks.union(tick)
    return marks


def _liquid(d: _BarrelDims) -> cq.Workplane:
    """Medication column inside the barrel, meeting the inner wall."""
    liq_bot = d.z0 + 0.0002
    liq_top = d.gasket_rest_z - 0.0002
    r = d.bore_r if d.is_stepped else d.inner_r
    return (
        cq.Workplane("XY")
        .workplane(offset=liq_bot)
        .circle(r)
        .extrude(liq_top - liq_bot)
    )


# ---- Slot B: flange family -------------------------------------------------
def _flange_flat_wings(d: _BarrelDims) -> cq.Workplane:
    """Two flat thumb-and-forefinger wings (parent _finger_flanges L134-153)."""
    z = d.z1 - 0.0020
    flange_w = max(d.outer_r * 4.4, 0.014)
    plate = (
        cq.Workplane("XY")
        .workplane(offset=z)
        .box(flange_w, d.flange_depth, d.flange_thick, centered=(True, True, True))
        .edges("|Z")
        .fillet(min(0.0020, d.flange_depth * 0.4))
    )
    bore = (
        cq.Workplane("XY")
        .workplane(offset=z)
        .circle(d.outer_r - 0.0003)  # tight: flange wraps + overlaps barrel wall
        .extrude(d.flange_thick * 3, both=True)
    )
    return plate.cut(bore)


def _flange_ring_collar(d: _BarrelDims) -> cq.Workplane:
    """Full annular thumb-collar ring (rec_syringe_var_ringflng _thumb_collar)."""
    z = d.z1 - 0.0020
    r_in = d.outer_r - 0.0003  # tight: collar inner overlaps the barrel wall
    r_out = max(d.outer_r * 2.2, r_in + 0.0040)
    thick = d.flange_thick
    half = thick / 2.0
    profile = (
        cq.Workplane("XZ")
        .moveTo(r_in, z - half)
        .lineTo(r_out, z - half)
        .lineTo(r_out, z + half)
        .lineTo(r_in, z + half)
        .close()
    )
    disc = profile.revolve(360.0, (0.0, 0.0, 0.0), (0.0, 1.0, 0.0))
    return disc.edges(">Z or <Z").fillet(0.0004)


def _flange_ribbed_grip(d: _BarrelDims) -> cq.Workplane:
    """Ergonomic ribbed grip flange (rec_syringe_var_ribgrip
    _ergonomic_grip_flange L135-196): stadium plate + finger notches + ribs."""
    z_center = d.z1 - 0.0020
    grip_w = max(d.outer_r * 5.0, 0.016)
    grip_d = max(d.flange_depth * 1.15, 0.0085)
    grip_t = max(d.flange_thick + 0.0004, 0.0020)

    plate = (
        cq.Workplane("XY")
        .workplane(offset=z_center - grip_t / 2.0)
        .slot2D(grip_w, grip_d)
        .extrude(grip_t)
    )
    bore = (
        cq.Workplane("XY")
        .workplane(offset=z_center - grip_t)
        .circle(d.outer_r - 0.0003)  # tight: grip wraps + overlaps barrel wall
        .extrude(grip_t * 3)
    )
    plate = plate.cut(bore)

    notch_r = grip_d * 0.18
    n_notches = 2
    notch_spacing = grip_w * 0.27
    for i in range(n_notches):
        x_pos = (i - (n_notches - 1) / 2.0) * notch_spacing
        for y_sign in (1.0, -1.0):
            y_pos = y_sign * (grip_d / 2.0)
            notch = (
                cq.Workplane("XY")
                .workplane(offset=z_center - grip_t)
                .circle(notch_r)
                .extrude(grip_t * 3)
                .translate((x_pos, y_pos, 0.0))
            )
            plate = plate.cut(notch)

    n_ribs = 5
    rib_h = 0.0004
    rib_w = 0.0005
    rib_span = grip_w * 0.60
    for i in range(n_ribs):
        y_offset = -grip_d * 0.3 + i * (grip_d * 0.6 / (n_ribs - 1))
        rib = (
            cq.Workplane("XY")
            .workplane(offset=z_center + grip_t / 2.0)
            .box(rib_span, rib_w, rib_h, centered=(True, True, False))
            .translate((0.0, y_offset, 0.0))
        )
        plate = plate.union(rib)
    return plate


def _build_flange(d: _BarrelDims, flange: Flange) -> cq.Workplane:
    if flange == "ring_collar":
        return _flange_ring_collar(d)
    if flange == "ribbed_grip":
        return _flange_ribbed_grip(d)
    return _flange_flat_wings(d)


# ---- Slot A: tip / hub family ---------------------------------------------
def _hub(d: _BarrelDims) -> cq.Workplane:
    """Stainless Luer hub: stepped tapered collar with open throat
    (parent _hub L154-188)."""
    hub_z1 = d.z0
    hub_z0 = hub_z1 - d.hub_len
    top_r = d.hub_top_r
    body = (
        cq.Workplane("XZ")
        .moveTo(0.0, hub_z1)
        .lineTo(top_r, hub_z1)
        .lineTo(top_r, hub_z1 - 0.0030)
        .lineTo(top_r - 0.0008, hub_z1 - 0.0042)
        .lineTo(d.hub_bot_r, hub_z0 + 0.0030)
        .lineTo(d.hub_bot_r, hub_z0)
        .lineTo(0.0, hub_z0)
        .close()
        .revolve(360.0, (0.0, 0.0, 0.0), (0.0, 1.0, 0.0))
    )
    # Throat (Luer slip socket): keep a thick surrounding wall so the body
    # never reduces to a fragile shell — radius is the smaller of the source
    # 1.4mm-wall rule and 55% of the top radius (the latter dominates for the
    # wide-bore stepped hub where top_r is large).
    throat_r = max(0.0006, min(top_r - 0.0014, top_r * 0.55))
    throat = (
        cq.Workplane("XY")
        .workplane(offset=hub_z1 + 0.0005)
        .circle(throat_r)
        .extrude(-min(0.0080, d.hub_len * 0.5))
    )
    body = body.cut(throat)
    # Two side reliefs (Luer-lock window detail). Only emit them on the small /
    # slim hubs where the wall is thin enough that they read; on the wide-bore
    # hub they would sever the collar, so skip them (the spec's reject case for
    # disconnected islands). Slot length spans only the wall annulus, not the
    # full diameter, so it never cuts the hub in two.
    if not d.is_stepped:
        slot_len = min(top_r * 2.4, (top_r - throat_r) * 1.6 + throat_r * 2.0)
        for ang in (0.0, math.pi / 2):
            slot = (
                cq.Workplane("XY")
                .workplane(offset=hub_z1 - 0.0050)
                .box(0.0016, slot_len, 0.0070, centered=(True, True, True))
                .rotate((0, 0, 0), (0, 0, 1), math.degrees(ang))
            )
            body = body.cut(slot)
    return body


def _needle(d: _BarrelDims, *, base_z: float, insert: float = 0.0025) -> cq.Workplane:
    """Thin stainless needle with a beveled cutting tip (parent _needle
    L189-216). ``base_z`` is the needle base (toward the barrel); the shaft
    extends UP by ``insert`` into the hub/nozzle bore so it overlaps and stays
    connected to the supporting tip part (press-fit seating)."""
    nr = d.needle_r
    n_z1 = base_z + insert  # top inserted into the hub for contact
    n_z0 = base_z - d.needle_len
    shaft = (
        cq.Workplane("XY")
        .workplane(offset=n_z1)
        .circle(nr)
        .extrude(-((n_z1 - n_z0) - 0.0030))
    )
    tip = (
        cq.Workplane("XY")
        .workplane(offset=n_z0 + 0.0030)
        .circle(nr)
        .extrude(-0.0030)
    )
    cutter = (
        cq.Workplane("XZ")
        .workplane(offset=-nr * 2)
        .moveTo(-nr * 2, n_z0)
        .lineTo(nr * 2, n_z0)
        .lineTo(nr * 2, n_z0 + 0.0042)
        .close()
        .extrude(nr * 4)
    )
    tip = tip.cut(cutter)
    return shaft.union(tip)


def _slip_tip_nozzle(d: _BarrelDims) -> cq.Workplane:
    """Integrated slip-tip nozzle cone (rec_syringe_var_sliptip
    _slip_tip_nozzle L154-178)."""
    nozzle_top_r = d.outer_r
    nozzle_bot_r = max(0.0012 * (d.outer_r / 0.0058), 0.0008)
    nozzle_len = 0.0120 * (d.length / 0.060)
    nozzle_len = max(0.0070, min(nozzle_len, 0.016))
    nz1 = d.z0
    nz0 = nz1 - nozzle_len
    profile = (
        cq.Workplane("XZ")
        .moveTo(0.0, nz1)
        .lineTo(nozzle_top_r, nz1)
        .lineTo(nozzle_bot_r, nz0)
        .lineTo(0.0, nz0)
        .close()
        .revolve(360.0, (0.0, 0.0, 0.0), (0.0, 1.0, 0.0))
    )
    bore = (
        cq.Workplane("XY")
        .workplane(offset=nz1 + 0.0002)
        .circle(d.needle_r)
        .extrude(-(nozzle_len + 0.0004))
    )
    return profile.cut(bore), nz0


def _cannula(d: _BarrelDims) -> cq.Workplane:
    """Blunt cannula: straight tube + hemispherical tip + visible bore
    (rec_syringe_var_bluntcan _cannula L190-226)."""
    outer_r = max(0.00075 * (d.needle_r / 0.00045), 0.0005)
    bore_r = outer_r * 0.66
    hub_z0 = d.z0 - d.hub_len
    insert = 0.0025  # press-fit up into the hub bore for contact
    c_z1 = hub_z0 + insert
    c_z0 = hub_z0 - d.needle_len
    shaft = (
        cq.Workplane("XY")
        .workplane(offset=c_z1)
        .circle(outer_r)
        .extrude(-((c_z1 - c_z0) - outer_r))
    )
    tip_sphere = (
        cq.Workplane("XY")
        .workplane(offset=c_z0 + outer_r)
        .sphere(outer_r)
    )
    lower_half = (
        cq.Workplane("XY")
        .workplane(offset=c_z0 + outer_r)
        .circle(outer_r * 1.5)
        .extrude(-outer_r * 1.5)
    )
    tip_cap = tip_sphere.intersect(lower_half)
    body = shaft.union(tip_cap)
    bore = (
        cq.Workplane("XY")
        .workplane(offset=c_z1 + 0.001)
        .circle(bore_r)
        .extrude(-(d.needle_len + 0.002))
    )
    return body.cut(bore)


def _safety_shield(d: _BarrelDims) -> cq.Workplane:
    """Translucent guard sleeve around the needle (rec_syringe_var_safetysh
    _safety_shield L226-263)."""
    shield_outer_r = max(d.hub_bot_r + 0.0006, d.needle_r + 0.0030)
    shield_wall = 0.0008
    shield_inner_r = shield_outer_r - shield_wall
    shield_len = d.needle_len + 0.004  # cover past the needle tip to guard the point
    shield_len = max(0.015, shield_len)
    hub_z0 = d.z0 - d.hub_len
    s_z1 = hub_z0

    outer = (
        cq.Workplane("XY")
        .workplane(offset=s_z1)
        .circle(shield_outer_r)
        .extrude(-shield_len)
    )
    bore = (
        cq.Workplane("XY")
        .workplane(offset=s_z1 + 0.001)
        .circle(shield_inner_r)
        .extrude(-(shield_len + 0.002))
    )
    tube = outer.cut(bore)
    # Mounting collar: a ring that slips OVER the hub bottom neck and overlaps
    # it so the shield is physically connected to the hub (no floating island).
    # It extends UP into the hub region (z > s_z1) and DOWN to meet the tube.
    collar_inner_r = max(0.0004, d.hub_bot_r - 0.0004)  # grips the hub neck
    collar_outer_r = max(d.hub_bot_r + 0.0012, shield_inner_r + 0.0006)
    collar = (
        cq.Workplane("XY")
        .workplane(offset=s_z1 + 0.0018)  # reach up into the hub for overlap
        .circle(collar_outer_r)
        .extrude(-(0.0018 + 0.0035))
    )
    collar_bore = (
        cq.Workplane("XY")
        .workplane(offset=s_z1 + 0.0028)
        .circle(collar_inner_r)
        .extrude(-(0.0028 + 0.0045))
    )
    collar = collar.cut(collar_bore)
    # Web ring bridging the collar (at collar_outer_r) to the tube wall
    # (at shield_outer_r) so the two annuli are one connected solid.
    web_outer = max(collar_outer_r, shield_outer_r)
    web = (
        cq.Workplane("XY")
        .workplane(offset=s_z1)
        .circle(web_outer)
        .extrude(-0.0012)
    )
    web_bore = (
        cq.Workplane("XY")
        .workplane(offset=s_z1 + 0.001)
        .circle(shield_inner_r)
        .extrude(-0.004)
    )
    web = web.cut(web_bore)
    return tube.union(collar).union(web)


# ---- Slot C: plunger rod family -------------------------------------------
def _plunger_rod_plus_cross(d: _BarrelDims) -> cq.Workplane:
    """Cross-rib ('+') plunger spine (parent _plunger_rod L234-249)."""
    z0 = d.gasket_rest_z + d.gasket_len - PLUNGER_Z_SHIFT(d)
    rib_a = (
        cq.Workplane("XY")
        .workplane(offset=z0)
        .box(d.rod_rib_w, d.rod_rib_t, d.rod_len, centered=(True, True, False))
    )
    rib_b = (
        cq.Workplane("XY")
        .workplane(offset=z0)
        .box(d.rod_rib_t, d.rod_rib_w, d.rod_len, centered=(True, True, False))
    )
    return rib_a.union(rib_b)


def _plunger_rod_flat_plate(d: _BarrelDims) -> cq.Workplane:
    """Flat solid plate plunger rod (rec_syringe_var_flatrod _plunger_rod)."""
    z0 = d.gasket_rest_z + d.gasket_len - PLUNGER_Z_SHIFT(d)
    return (
        cq.Workplane("XY")
        .workplane(offset=z0)
        .box(d.rod_plate_w, d.rod_plate_t, d.rod_len, centered=(True, True, False))
    )


def _build_plunger_rod(d: _BarrelDims, rod: PlungerRod) -> cq.Workplane:
    if rod == "flat_plate":
        return _plunger_rod_flat_plate(d)
    return _plunger_rod_plus_cross(d)


def _gasket(d: _BarrelDims) -> cq.Workplane:
    """Black rubber stopper at the bottom of the plunger (parent _gasket)."""
    g = (
        cq.Workplane("XY")
        .workplane(offset=d.gasket_rest_z - PLUNGER_Z_SHIFT(d))
        .circle(d.gasket_r)
        .extrude(d.gasket_len)
    )
    fil = min(0.0008, d.gasket_r * 0.4, d.gasket_len * 0.35)
    try:
        g = g.edges("%CIRCLE").fillet(fil)
    except Exception:
        pass
    return g


def _thumb_rest(d: _BarrelDims) -> cq.Workplane:
    """Round thumb-press disc at the top of the rod (parent _thumb_rest)."""
    z = d.gasket_rest_z + d.gasket_len + d.rod_len - PLUNGER_Z_SHIFT(d)
    disc = (
        cq.Workplane("XY")
        .workplane(offset=z - d.thumb_thick)
        .circle(d.thumb_r)
        .extrude(d.thumb_thick)
    )
    # Ease the top/bottom rim edges; keep the radius safely under half the disc
    # thickness so thin (insulin) discs don't fail the fillet operation.
    fil = min(0.0006, d.thumb_thick * 0.35)
    try:
        disc = disc.edges(">Z or <Z").fillet(fil)
    except Exception:
        pass
    return disc


# ===========================================================================
# Build
# ===========================================================================
def build_syringe(
    config: SyringeConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    d = r.dims
    model = ArticulatedObject(name=r.name, assets=assets)
    palette = PALETTES[r.palette_style]
    mats = {
        key: model.material(f"syr_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in palette.items()
    }

    # Rest transform: lay flat (roll -90 about X) and lift so z-min = 0.
    rest = Origin(xyz=(0.0, 0.0, d.rest_lift), rpy=(-math.pi / 2.0, 0.0, 0.0))

    # ---- Root: barrel assembly (all visuals carry the rest transform) ----
    barrel = model.part("barrel_assembly")
    barrel.visual(
        mesh_from_cadquery(_barrel_shell(d), "barrel_shell", assets=assets),
        origin=rest, material=mats["barrel"], name="barrel_shell", material_class_id="plastic.clear_rigid",
    )
    barrel.visual(
        mesh_from_cadquery(_liquid(d), "liquid", assets=assets),
        origin=rest, material=mats["liquid"], name="liquid", material_class_id="liquid.water_wave_foam",
    )
    barrel.visual(
        mesh_from_cadquery(_graduation_marks(d, r.tick_count), "scale_marks", assets=assets),
        origin=rest, material=mats["ink"], name="scale_marks", appearance_only=AppearanceOnlySpec(kind="overlay"),
    )
    barrel.visual(
        mesh_from_cadquery(_build_flange(d, r.flange), "finger_flanges", assets=assets),
        origin=rest, material=mats["plastic"], name="finger_flanges", material_class_id="plastic.opaque_glossy_molded",
    )

    # ---- Slot A: tip / hub front-end visuals ----
    if r.tip_hub == "slip_tip":
        nozzle, needle_base_z = _slip_tip_nozzle(d)
        barrel.visual(
            mesh_from_cadquery(nozzle, "luer_hub", assets=assets),
            origin=rest, material=mats["plastic"], name="luer_hub", material_class_id="plastic.opaque_glossy_molded",
        )
        barrel.visual(
            mesh_from_cadquery(_needle(d, base_z=needle_base_z + 0.0010), "needle", assets=assets),
            origin=rest, material=mats["steel"], name="needle", material_class_id="metal.stainless_matte",
        )
    elif r.tip_hub == "blunt_cannula":
        barrel.visual(
            mesh_from_cadquery(_hub(d), "luer_hub", assets=assets),
            origin=rest, material=mats["steel"], name="luer_hub", material_class_id="metal.stainless_matte",
        )
        barrel.visual(
            mesh_from_cadquery(_cannula(d), "needle", assets=assets),
            origin=rest, material=mats["plastic"], name="needle", material_class_id="plastic.opaque_glossy_molded",
        )
    elif r.tip_hub == "safety_shield":
        barrel.visual(
            mesh_from_cadquery(_hub(d), "luer_hub", assets=assets),
            origin=rest, material=mats["steel"], name="luer_hub", material_class_id="metal.stainless_matte",
        )
        barrel.visual(
            mesh_from_cadquery(_needle(d, base_z=d.z0 - d.hub_len), "needle", assets=assets),
            origin=rest, material=mats["steel"], name="needle", material_class_id="metal.stainless_matte",
        )
        barrel.visual(
            mesh_from_cadquery(_safety_shield(d), "safety_shield", assets=assets),
            origin=rest, material=mats["shield"], name="safety_shield", material_class_id="plastic.frosted_translucent",
        )
    else:  # luer_lock_needle
        barrel.visual(
            mesh_from_cadquery(_hub(d), "luer_hub", assets=assets),
            origin=rest, material=mats["steel"], name="luer_hub", material_class_id="metal.stainless_matte",
        )
        barrel.visual(
            mesh_from_cadquery(_needle(d, base_z=d.z0 - d.hub_len), "needle", assets=assets),
            origin=rest, material=mats["steel"], name="needle", material_class_id="metal.stainless_matte",
        )

    # ---- Child: plunger (gasket + rod + thumb rest), authored vertical ----
    plunger = model.part("plunger")
    plunger.visual(
        mesh_from_cadquery(_gasket(d), "gasket", assets=assets),
        material=mats["rubber"], name="gasket", material_class_id="rubber.smooth_plain",
    )
    plunger.visual(
        mesh_from_cadquery(_build_plunger_rod(d, r.plunger_rod), "plunger_rod", assets=assets),
        material=mats["plastic"], name="plunger_rod", material_class_id="plastic.opaque_glossy_molded",
    )
    plunger.visual(
        mesh_from_cadquery(_thumb_rest(d), "thumb_rest", assets=assets),
        material=mats["plastic"], name="thumb_rest", material_class_id="plastic.opaque_glossy_molded",
    )

    # ---- Hero joint: plunger slides DOWN the bore (PRISMATIC, every seed) ----
    # The plunger geometry is authored shifted DOWN by PLUNGER_Z_SHIFT (gasket
    # bottom at local z=0). Compensate the joint origin by the same shift along
    # the bore so the world placement is unchanged. With the rest roll of -90deg
    # about X, R(rest_rpy)*(0,0,shift) = (0, +shift, 0), so the joint xyz gains
    # +shift on the world Y component (the bore axis in the rest pose).
    shift = PLUNGER_Z_SHIFT(d)
    joint_origin = Origin(
        xyz=(0.0, 0.0 + shift, d.rest_lift),
        rpy=(-math.pi / 2.0, 0.0, 0.0),
    )
    model.articulation(
        "barrel_to_plunger",
        ArticulationType.PRISMATIC,
        parent=barrel,
        child=plunger,
        origin=joint_origin,
        axis=(0.0, 0.0, -1.0),
        motion_limits=MotionLimits(
            effort=30.0,
            velocity=0.1,
            lower=0.0,
            upper=d.plunger_travel,
        ),
    )

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_syringe(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_syringe(config_from_seed(seed), assets=assets)


# ===========================================================================
# Tests
# ===========================================================================
def run_syringe_tests(
    object_model: ArticulatedObject,
    config: SyringeConfig,
) -> TestReport:
    r = resolve_config(config)
    d = r.dims
    ctx = TestContext(object_model)

    barrel = object_model.get_part("barrel_assembly")
    plunger = object_model.get_part("plunger")
    joint = object_model.get_articulation("barrel_to_plunger")

    # --- Hero joint: PRISMATIC, along the bore axis (every seed). ---
    ctx.check(
        "plunger joint is prismatic",
        joint.articulation_type == ArticulationType.PRISMATIC,
        details=f"type={joint.articulation_type}",
    )
    ax = joint.axis
    ctx.check(
        "plunger slides along the barrel bore axis (joint-local -Z)",
        abs(ax[0]) < 1e-6 and abs(ax[1]) < 1e-6 and abs(ax[2]) > 0.99,
        details=f"axis={ax}",
    )

    # --- Tip extends beyond the hub/neck toward the needle (-Y) end. ---
    tip_box = ctx.part_element_world_aabb(barrel, elem="needle")
    barrel_box = ctx.part_element_world_aabb(barrel, elem="barrel_shell")
    ctx.check(
        "tip extends beyond the barrel toward the needle end (-Y)",
        tip_box is not None and barrel_box is not None and tip_box[0][1] < barrel_box[0][1] - 0.005,
        details=f"tip_min_y={None if tip_box is None else tip_box[0][1]}",
    )

    # --- Liquid sits inside the barrel along the bore. ---
    liquid_box = ctx.part_element_world_aabb(barrel, elem="liquid")
    ctx.check(
        "liquid is inside the barrel between neck and rim",
        liquid_box is not None
        and barrel_box is not None
        and liquid_box[1][1] < barrel_box[1][1] + 0.001
        and liquid_box[0][1] > barrel_box[0][1] - 0.001,
        details=f"liquid_y={None if liquid_box is None else (liquid_box[0][1], liquid_box[1][1])}",
    )

    # --- Flange spans wider than the barrel near the rim. ---
    flange_box = ctx.part_element_world_aabb(barrel, elem="finger_flanges")
    ctx.check(
        "flange is wider than the barrel",
        flange_box is not None and (flange_box[1][0] - flange_box[0][0]) > d.outer_r * 2.2,
        details=f"flange_x_span={None if flange_box is None else flange_box[1][0]-flange_box[0][0]}",
    )

    # --- Whole object rests on/above the floor (rest_lift covers widest part). ---
    b_world = ctx.part_world_aabb(barrel)
    p_world = ctx.part_world_aabb(plunger)
    world_zmin = (
        min(b_world[0][2], p_world[0][2])
        if b_world is not None and p_world is not None
        else None
    )
    ctx.check(
        "object rests on/above the floor plane (no z<0 penetration)",
        world_zmin is not None and world_zmin >= -0.001,
        details=f"world_zmin={world_zmin}",
    )

    # --- Thumb rest sits past the barrel rim at the +Y (plunger) end. ---
    thumb_box = ctx.part_element_world_aabb(plunger, elem="thumb_rest")
    ctx.check(
        "thumb rest is beyond the barrel rim",
        thumb_box is not None and barrel_box is not None and thumb_box[0][1] > barrel_box[1][1] - 0.002,
        details=f"thumb_min_y={None if thumb_box is None else thumb_box[0][1]}",
    )

    # --- Gasket retained snugly inside the bore (cross-section + insertion). ---
    ctx.expect_within(
        plunger, barrel, axes="xz",
        inner_elem="gasket", outer_elem="barrel_shell",
        margin=0.0006,
        name="gasket stays within the barrel bore",
    )
    ctx.expect_overlap(
        plunger, barrel, axes="y",
        elem_a="gasket", elem_b="barrel_shell",
        min_overlap=0.003,
        name="gasket is inserted in the barrel at rest",
    )

    # --- Decisive: pushing the plunger moves the gasket toward the needle. ---
    rest_pos = ctx.part_world_position(plunger)
    with ctx.pose({joint: d.plunger_travel}):
        pushed_pos = ctx.part_world_position(plunger)
        ctx.expect_within(
            plunger, barrel, axes="xz",
            inner_elem="gasket", outer_elem="barrel_shell",
            margin=0.0006,
            name="gasket centered in bore at full stroke",
        )
        ctx.expect_overlap(
            plunger, barrel, axes="y",
            elem_a="gasket", elem_b="barrel_shell",
            min_overlap=0.003,
            name="gasket retained in barrel at full stroke",
        )
        # Thumb-rest must NOT sink below the rim at full depression (else it
        # 穿模s the barrel shell / flanges / scale / liquid). +Y is the plunger
        # end, so the thumb BOTTOM (min-y) must stay >= the barrel rim (max-y).
        thumb_full = ctx.part_element_world_aabb(plunger, elem="thumb_rest")
        rim_full = ctx.part_element_world_aabb(barrel, elem="barrel_shell")
        ctx.check(
            "thumb-rest stays at/above the barrel rim at full stroke",
            thumb_full is not None
            and rim_full is not None
            and thumb_full[0][1] >= rim_full[1][1] - 0.0005,
            details=(
                f"thumb_min_y={None if thumb_full is None else thumb_full[0][1]}, "
                f"rim_max_y={None if rim_full is None else rim_full[1][1]}"
            ),
        )
    ctx.check(
        "pushing plunger dispenses (moves gasket toward the needle end, -Y)",
        rest_pos is not None and pushed_pos is not None and pushed_pos[1] < rest_pos[1] - 0.003,
        details=f"rest_y={None if rest_pos is None else rest_pos[1]}, pushed_y={None if pushed_pos is None else pushed_pos[1]}",
    )

    # --- Intentional seal fit: the gasket nests snugly in the bore. ---
    ctx.allow_overlap(
        plunger, barrel,
        elem_a="gasket", elem_b="barrel_shell",
        reason="The rubber gasket is intentionally seated snugly inside the barrel bore to seal the plunger.",
    )
    # The plunger rod passes through the open barrel rim while sliding.
    ctx.allow_overlap(
        plunger, barrel,
        elem_a="plunger_rod", elem_b="barrel_shell",
        reason="The plunger rod slides through the open barrel rim / bore.",
    )
    # The plunger seal sweeps the full bore length, staying in sliding contact
    # with the barrel shell along its travel.
    ctx.allow_overlap(
        plunger, barrel,
        reason="plunger seal rides inside the barrel bore in sliding contact along its travel",
    )

    return ctx.report()


# Default object_model so the module can be inspected standalone.
object_model = build_seeded_syringe(0)
