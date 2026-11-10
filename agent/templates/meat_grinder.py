# SPDX-License-Identifier: Apache-2.0

"""Manual meat grinder — modular procedural template.

A hand-cranked meat grinder: one grounded grind-chamber ``body`` (a hollow
cylindrical housing whose bore runs along world +X) carries a vertical feed
hopper on +Z, a perforated cutting plate + retaining ring at the −X outlet, an
internal helical auger cranked about the chamber axis, and a mount (table
clamp / bolt-down countertop foot / freestanding pedestal) hung below on −Z.
The auger + cutter + crank turn as one rigid CONTINUOUS drive about +X; a
free-spinning grip rides the crank pin.

Structure = ``parallel_children`` — mount / hopper / output visuals fuse onto
the one grounded ``body``; ``auger_drive``, ``retaining_ring`` and (for the
table clamp) ``clamp_screw`` are children of ``body``; ``crank_grip`` is a
child of ``auger_drive``.

Slots (see ``articraft_template_authoring/specs_modular_v1/meat_grinder.md``):

  * ``mount`` (3): table_clamp / countertop_base / freestanding_pedestal.
    ``table_clamp`` adds a ``clamp_screw`` PART + PRISMATIC +Z joint (①/②).
  * ``hopper_form`` (3, ③ Primary Form Family): wide_tray_hopper (Planar
    Boundary) / covered_deep_funnel (Volumetric Envelope) / guarded_feed_chute
    (Macro Surface Construction).
  * ``drive`` (3): bent_hand_crank / spoked_handwheel / geared_crank.
  * ``output`` (4): plain_ring / bayonet_ring / sausage_nozzle / kibbe_former.
    ``bayonet_ring`` flips the ring joint CONTINUOUS→REVOLUTE [0, 0.42] (②).
  * palette (6): stainless_rubber / cast_aluminum_offwhite / stainless_yellow /
    tinned_high_contrast / red_enamel / bronze_and_brass.

Sources (all 14 read): 3 origin anchors (001/002/003) + 11 forked_anchor
variants. Unified onto the 003 chassis datum (chamber axis at world z=0).

Rule-3 primitives preserved: ``twistExtrude`` auger flight, spline crank arm
(``tube_from_spline_points`` → ``mesh_from_geometry``), lofted hoppers / sausage
horn / kibbe cone, and boolean-cut perforated cutting plate — none downgraded.

Captured pin/journal joints (auger flight in the chamber bore, ring on the
front flange, grip on the crank pin, screw in the clamp boss) have no clean
axis-aligned face pair, so those joints omit ``mating=`` (grandfathered) and are
guarded by element-scoped ``allow_overlap`` mirroring the source records.
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
    MotionLimits,
    Origin,
    Sphere,
    TestContext,
    TestReport,
    mesh_from_cadquery,
    mesh_from_geometry,
    tube_from_spline_points,
)

__modular__ = True

# --------------------------------------------------------------------------- #
# Slot enums                                                                   #
# --------------------------------------------------------------------------- #
Mount = Literal["table_clamp", "countertop_base", "freestanding_pedestal"]
HopperForm = Literal["wide_tray_hopper", "covered_deep_funnel", "guarded_feed_chute"]
Drive = Literal["bent_hand_crank", "spoked_handwheel", "geared_crank"]
Output = Literal["plain_ring", "bayonet_ring", "sausage_nozzle", "kibbe_former"]
PaletteStyle = Literal[
    "stainless_rubber",
    "cast_aluminum_offwhite",
    "stainless_yellow",
    "tinned_high_contrast",
    "red_enamel",
    "bronze_and_brass",
]

MOUNTS: tuple[Mount, ...] = ("table_clamp", "countertop_base", "freestanding_pedestal")
HOPPER_FORMS: tuple[HopperForm, ...] = (
    "wide_tray_hopper",
    "covered_deep_funnel",
    "guarded_feed_chute",
)
DRIVES: tuple[Drive, ...] = ("bent_hand_crank", "spoked_handwheel", "geared_crank")
OUTPUTS: tuple[Output, ...] = (
    "plain_ring",
    "bayonet_ring",
    "sausage_nozzle",
    "kibbe_former",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "stainless_rubber",
    "cast_aluminum_offwhite",
    "stainless_yellow",
    "tinned_high_contrast",
    "red_enamel",
    "bronze_and_brass",
)

# Six palettes drawn from the observed 5-star colorways. Keys map onto every
# visual material (body_metal / steel_light / dark_steel / accent / accent2).
# Category identity is carried by the geometry; palettes only decorate.
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "stainless_rubber": {
        "body_metal": (0.68, 0.72, 0.75, 1.0),
        "steel_light": (0.84, 0.87, 0.89, 1.0),
        "dark_steel": (0.28, 0.30, 0.31, 1.0),
        "accent": (0.045, 0.048, 0.052, 1.0),
        "accent2": (0.52, 0.53, 0.55, 1.0),
    },
    "cast_aluminum_offwhite": {
        "body_metal": (0.59, 0.61, 0.63, 1.0),
        "steel_light": (0.78, 0.80, 0.82, 1.0),
        "dark_steel": (0.22, 0.23, 0.24, 1.0),
        "accent": (0.83, 0.84, 0.84, 1.0),
        "accent2": (0.40, 0.41, 0.43, 1.0),
    },
    "stainless_yellow": {
        "body_metal": (0.72, 0.75, 0.77, 1.0),
        "steel_light": (0.86, 0.88, 0.89, 1.0),
        "dark_steel": (0.23, 0.25, 0.26, 1.0),
        "accent": (0.96, 0.70, 0.08, 1.0),
        "accent2": (0.96, 0.42, 0.05, 1.0),
    },
    "tinned_high_contrast": {
        "body_metal": (0.86, 0.88, 0.89, 1.0),
        "steel_light": (0.92, 0.93, 0.94, 1.0),
        "dark_steel": (0.23, 0.25, 0.26, 1.0),
        "accent": (0.30, 0.32, 0.34, 1.0),
        "accent2": (0.55, 0.57, 0.59, 1.0),
    },
    "red_enamel": {
        "body_metal": (0.66, 0.15, 0.12, 1.0),
        "steel_light": (0.86, 0.87, 0.88, 1.0),
        "dark_steel": (0.20, 0.20, 0.22, 1.0),
        "accent": (0.90, 0.90, 0.90, 1.0),
        "accent2": (0.78, 0.22, 0.18, 1.0),
    },
    "bronze_and_brass": {
        "body_metal": (0.55, 0.42, 0.24, 1.0),
        "steel_light": (0.78, 0.62, 0.34, 1.0),
        "dark_steel": (0.30, 0.24, 0.16, 1.0),
        "accent": (0.62, 0.44, 0.26, 1.0),
        "accent2": (0.80, 0.62, 0.28, 1.0),
    },
}

# --------------------------------------------------------------------------- #
# Nominal geometry (meters, scale=1). World frame: chamber axis on +X at z=0,  #
# outlet −X, crank +X, hopper +Z, mount −Z.                                    #
# --------------------------------------------------------------------------- #
CHAMBER_X0, CHAMBER_X1 = -0.100, 0.100
CHAMBER_RO, CHAMBER_RI = 0.044, 0.034
FRONT_COLLAR_X0, FRONT_COLLAR_X1 = -0.130, -0.092  # overlaps the chamber so the union fuses
FRONT_COLLAR_RO, FRONT_COLLAR_RI = 0.052, 0.040
REAR_BEARING_X0, REAR_BEARING_X1 = 0.090, 0.130
THROAT_Z0, THROAT_Z1 = 0.020, 0.128
THROAT_RO, THROAT_RI = 0.032, 0.024
THROAT_X = -0.010
THROAT_TOP_Z = 0.128

PLATE_X0, PLATE_X1 = -0.112, -0.106
PLATE_R = 0.038

AUGER_X0, AUGER_X1 = -0.100, 0.150   # shaft passes through the rear bearing and emerges
AUGER_SHAFT_R = 0.008
FLIGHT_X0, FLIGHT_LEN = -0.092, 0.152
CUTTER_X = -0.097

RING_X0, RING_X1 = -0.132, -0.104
RING_RO, RING_RI = 0.060, 0.049

# Crank pin nominal offset from the axis (bent / geared drives). The crank
# emerges from the shaft PAST the rear bearing (which ends at x=0.130).
CRANK_ROOT_X = 0.144
CRANK_PIN = (0.156, 0.050, -0.105)   # base of the grip pin
# Handwheel drive x-plane (past the rear bearing) + spinner pin.
WHEEL_X = 0.148
SPINNER_PIN = (0.178, 0.000, -0.066)


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


# --------------------------------------------------------------------------- #
# Config dataclasses                                                           #
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class MeatGrinderConfig:
    mount: Mount | None = None
    hopper_form: HopperForm | None = None
    drive: Drive | None = None
    output: Output | None = None
    palette_style: PaletteStyle = "stainless_rubber"
    body_scale: float = 1.0
    hopper_scale: float = 1.0
    crank_reach_scale: float = 1.0
    name: str = "meat_grinder"


@dataclass(frozen=True)
class ResolvedMeatGrinderConfig:
    mount: Mount
    hopper_form: HopperForm
    drive: Drive
    output: Output
    palette_style: PaletteStyle
    body_scale: float
    hopper_scale: float
    crank_reach_scale: float
    name: str

    @property
    def has_clamp_screw(self) -> bool:
        return self.mount == "table_clamp"

    @property
    def ring_is_bayonet(self) -> bool:
        return self.output == "bayonet_ring"


# --------------------------------------------------------------------------- #
# Procedural sampling (Contract 4).                                            #
# --------------------------------------------------------------------------- #
def config_from_seed(seed: int) -> MeatGrinderConfig:
    rng = random.Random(seed)
    return MeatGrinderConfig(
        mount=rng.choice(MOUNTS),
        hopper_form=rng.choice(HOPPER_FORMS),
        drive=rng.choice(DRIVES),
        output=rng.choice(OUTPUTS),
        palette_style=rng.choice(PALETTE_STYLES),
        body_scale=round(rng.uniform(0.90, 1.10), 4),
        hopper_scale=round(rng.uniform(0.90, 1.15), 4),
        crank_reach_scale=round(rng.uniform(0.85, 1.15), 4),
        name=f"seeded_meat_grinder_{seed}",
    )


def resolve_config(config: MeatGrinderConfig | None = None) -> ResolvedMeatGrinderConfig:
    cfg = config or MeatGrinderConfig()
    mount = _pick(cfg.mount, MOUNTS)
    hopper_form = _pick(cfg.hopper_form, HOPPER_FORMS)
    drive = _pick(cfg.drive, DRIVES)
    output = _pick(cfg.output, OUTPUTS)
    palette = _pick(cfg.palette_style, PALETTE_STYLES)

    body_scale = _clamp(cfg.body_scale, 0.90, 1.10)
    hopper_scale = _clamp(cfg.hopper_scale, 0.90, 1.15)
    crank_reach_scale = _clamp(cfg.crank_reach_scale, 0.85, 1.15)

    # conditional: the spoked handwheel spinner pin must stay just outside the
    # rim; cap its reach so the grip does not fly off the wheel.
    if drive == "spoked_handwheel":
        crank_reach_scale = min(crank_reach_scale, 1.05)

    # inequality (Rule 5): the crank pin must stay clear of the chamber barrel
    # so the grip sweeps a full circle without hitting the body. For the bent /
    # geared crank the pin radial is sqrt(py^2 + pz^2); the handwheel spinner is
    # already outboard of the rim. Both nominal geometries clear comfortably, so
    # this only raises reach on the (unreachable) degenerate case.
    pin_radial = math.hypot(CRANK_PIN[1], CRANK_PIN[2]) * crank_reach_scale
    min_radial = CHAMBER_RO + 0.016 + 0.008  # chamber_r + grip_r + clearance
    if drive != "spoked_handwheel" and pin_radial < min_radial:
        crank_reach_scale = min_radial / max(math.hypot(CRANK_PIN[1], CRANK_PIN[2]), 1e-6)
        crank_reach_scale = _clamp(crank_reach_scale, 0.85, 1.30)

    return ResolvedMeatGrinderConfig(
        mount=mount,
        hopper_form=hopper_form,
        drive=drive,
        output=output,
        palette_style=palette,
        body_scale=body_scale,
        hopper_scale=hopper_scale,
        crank_reach_scale=crank_reach_scale,
        name=cfg.name or "meat_grinder",
    )


def with_overrides(config: MeatGrinderConfig, **kwargs: object) -> MeatGrinderConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: MeatGrinderConfig | ResolvedMeatGrinderConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedMeatGrinderConfig) else resolve_config(config)
    return (
        ("mount", r.mount),
        ("hopper_form", r.hopper_form),
        ("drive", r.drive),
        ("output", r.output),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# --------------------------------------------------------------------------- #
# CadQuery primitives (mirroring the 003 lineage idioms).                      #
# --------------------------------------------------------------------------- #
def _x_tube(x0: float, x1: float, ro: float, ri: float = 0.0):
    profile = cq.Workplane("YZ").circle(ro)
    if ri > 0.0:
        profile = profile.circle(ri)
    return profile.extrude(x1 - x0).translate((x0, 0.0, 0.0))


def _z_tube(z0: float, z1: float, ro: float, ri: float = 0.0, *, x: float = 0.0, y: float = 0.0):
    profile = cq.Workplane("XY").circle(ro)
    if ri > 0.0:
        profile = profile.circle(ri)
    return profile.extrude(z1 - z0).translate((x, y, z0))


def _box(size: tuple[float, float, float], center: tuple[float, float, float]):
    return cq.Workplane("XY").box(*size).translate(center)


# --------------------------------------------------------------------------- #
# Chassis meshes (always present).                                            #
# --------------------------------------------------------------------------- #
def _housing_cast_shape():
    """Hollow grind chamber + front collar + rear bearing + vertical throat.

    A single fused casting with the auger chamber and feed throat cut as true
    open bores (Rule 3 — real passages, not capped cylinders)."""
    housing = _x_tube(CHAMBER_X0, CHAMBER_X1, CHAMBER_RO, CHAMBER_RI)
    front_collar = _x_tube(FRONT_COLLAR_X0, FRONT_COLLAR_X1, FRONT_COLLAR_RO, FRONT_COLLAR_RI)
    # Rear bearing outer radius exceeds the chamber bore (0.034) so it fuses to
    # the chamber wall instead of floating inside the hollow bore.
    rear_bearing = _x_tube(REAR_BEARING_X0, REAR_BEARING_X1, 0.038, 0.009)
    throat = _z_tube(THROAT_Z0, THROAT_Z1, THROAT_RO, THROAT_RI, x=THROAT_X)
    cast = housing.union(front_collar).union(rear_bearing).union(throat)
    # Open the throat into the chamber.
    cast = cast.cut(_z_tube(-0.006, THROAT_Z1 + 0.004, THROAT_RI, x=THROAT_X))
    # Internal shoulder that locates the perforated plate; overlaps the collar
    # bore radially (ro > collar ri) so it fuses into one solid.
    cast = cast.union(_x_tube(-0.108, -0.103, FRONT_COLLAR_RI + 0.004, 0.028))
    return cast


def _cutting_plate_shape():
    """Perforated stainless cutting plate at the −X outlet (boolean holes)."""
    plate = _x_tube(PLATE_X0, PLATE_X1, PLATE_R)
    plate = plate.cut(_x_tube(PLATE_X0 - 0.002, PLATE_X1 + 0.002, 0.0085))
    for radius, count in ((0.015, 6), (0.026, 12)):
        for index in range(count):
            angle = 2.0 * math.pi * index / count
            y, z = radius * math.cos(angle), radius * math.sin(angle)
            cutter = (
                cq.Workplane("YZ").center(y, z).circle(0.0026).extrude(0.010)
                .translate((PLATE_X0 - 0.002, 0.0, 0.0))
            )
            plate = plate.cut(cutter)
    return plate


def _auger_core_shape():
    """Auger shaft + twist-extruded helical flight (Rule 3 — real screw)."""
    shaft = _x_tube(AUGER_X0, AUGER_X1, AUGER_SHAFT_R)
    flight = (
        cq.Workplane("YZ")
        .moveTo(0.0165, 0.0)
        .rect(0.022, 0.004)
        .twistExtrude(FLIGHT_LEN, 720.0)
        .translate((FLIGHT_X0, 0.0, 0.0))
    )
    return shaft.union(flight)


def _cutter_blade_shape(dual: bool):
    """Cross knife (default) or two-wing swept paddle (folded dual variant)."""
    if not dual:
        blade = cq.Workplane("YZ").rect(0.050, 0.009).extrude(0.006)
        blade = blade.union(cq.Workplane("YZ").rect(0.009, 0.050).extrude(0.006))
        return blade.rotate((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), 45.0).translate((CUTTER_X, 0.0, 0.0))
    wing = cq.Workplane("YZ").rect(0.062, 0.013).extrude(0.006)
    hub = cq.Workplane("YZ").circle(0.010).extrude(0.006)
    blade = wing.union(hub)
    return blade.rotate((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), 30.0).translate((CUTTER_X, 0.0, 0.0))


def _grip_shape():
    """Free-spinning hand grip sleeve + rounded end cap.

    Authored to extend outboard (+X) from the crank pin so it clears the crank
    arm; placed at the pin's world x in ``_build_grip``."""
    shell = _x_tube(-0.008, 0.085, 0.016, 0.0046)
    cap = cq.Workplane("XY").sphere(0.016).translate((0.085, 0.0, 0.0))
    return shell.union(cap)


# --------------------------------------------------------------------------- #
# Hopper meshes (Slot B — ③ Primary Form Family). Authored from local z=0 up,  #
# placed on the throat top; hopper_scale multiplies mouth width + height.      #
# --------------------------------------------------------------------------- #
def _wide_tray_hopper_shape(k: float):
    """Shallow wide elliptical loading pan — Planar Boundary Form."""
    outer = (
        cq.Workplane("XY")
        .circle(0.026)
        .workplane(offset=0.040 * k)
        .ellipse(0.088 * k, 0.063 * k)
        .workplane(offset=0.018 * k)
        .ellipse(0.098 * k, 0.071 * k)
        .loft(combine=True)
    )
    inner = (
        cq.Workplane("XY")
        .circle(0.019)
        .workplane(offset=0.040 * k)
        .ellipse(0.079 * k, 0.054 * k)
        .workplane(offset=0.024 * k)
        .ellipse(0.092 * k, 0.065 * k)
        .loft(combine=True)
        .translate((0.0, 0.0, -0.002))
    )
    rim = (
        cq.Workplane("XY").ellipse(0.101 * k, 0.074 * k).extrude(0.006)
        .cut(cq.Workplane("XY").ellipse(0.091 * k, 0.064 * k).extrude(0.006))
        .translate((0.0, 0.0, 0.056 * k))
    )
    return outer.cut(inner).union(rim)


def _covered_deep_funnel_shape(k: float):
    """Deep round funnel + rolled rim + fixed rear hood — Volumetric Envelope."""
    height = 0.130 * k
    outer = (
        cq.Workplane("XY").circle(0.026)
        .workplane(offset=height).circle(0.078 * k)
        .loft(combine=True)
    )
    inner = (
        cq.Workplane("XY").circle(0.019)
        .workplane(offset=height + 0.004).circle(0.073 * k)
        .loft(combine=True).translate((0.0, 0.0, -0.002))
    )
    funnel = outer.cut(inner)
    rim = (
        cq.Workplane("XY").circle(0.081 * k).extrude(0.006)
        .cut(cq.Workplane("XY").circle(0.0725 * k).extrude(0.006))
        .translate((0.0, 0.0, height - 0.002))
    )
    # Rear hood: a shallow dished plate clipped to the rear half, overlapping the
    # rim so it reads as one supported casting (host-conformal — Rule 4).
    cover = cq.Workplane("XY").circle(0.076 * k).extrude(0.0045).translate((0.0, 0.0, height + 0.004))
    rear_half = _box((0.090 * k, 0.170 * k, 0.014), (-0.010 - 0.045 * k, 0.0, height))
    hood = cover.intersect(rear_half)
    rib = _box((0.066 * k, 0.010, 0.007), (-0.009 - 0.033 * k, 0.0, height + 0.006))
    return funnel.union(rim).union(hood).union(rib)


def _guarded_feed_chute_shape(k: float):
    """Tall rectangular feed chute + integral finger-guard grid — Macro Surface."""
    height = 0.116 * k
    outer = (
        cq.Workplane("XY").rect(0.052, 0.048)
        .workplane(offset=0.060 * k).rect(0.132 * k, 0.102 * k)
        .workplane(offset=height - 0.060 * k).rect(0.132 * k, 0.102 * k)
        .loft(combine=True)
    )
    inner = (
        cq.Workplane("XY").rect(0.038, 0.034)
        .workplane(offset=0.064 * k).rect(0.116 * k, 0.086 * k)
        .workplane(offset=height - 0.060 * k).rect(0.116 * k, 0.086 * k)
        .loft(combine=True).translate((0.0, 0.0, -0.004))
    )
    shell = outer.cut(inner)
    rim = (
        cq.Workplane("XY").rect(0.144 * k, 0.114 * k).extrude(0.006)
        .cut(cq.Workplane("XY").rect(0.116 * k, 0.086 * k).extrude(0.008).translate((0, 0, -0.001)))
        .translate((0.0, 0.0, height))
    )
    guard = None
    for x in (-0.037 * k, 0.005, 0.047 * k):
        bar = _box((0.007, 0.106 * k, 0.007), (x, 0.0, height + 0.006))
        guard = bar if guard is None else guard.union(bar)
    guard = guard.union(_box((0.134 * k, 0.007, 0.007), (0.005, 0.0, height + 0.006)))
    return shell.union(rim).union(guard)


_HOPPER_SHAPES = {
    "wide_tray_hopper": _wide_tray_hopper_shape,
    "covered_deep_funnel": _covered_deep_funnel_shape,
    "guarded_feed_chute": _guarded_feed_chute_shape,
}


# --------------------------------------------------------------------------- #
# Output meshes (Slot D).                                                      #
# --------------------------------------------------------------------------- #
def _plain_ring_shape():
    """Threaded scallop/lug retaining collar wrapping the front flange."""
    ring = _x_tube(RING_X0, RING_X1, RING_RO, RING_RI)
    for y, z, dy, dz in (
        (0.056, 0.0, 0.016, 0.012),
        (-0.056, 0.0, 0.016, 0.012),
        (0.0, 0.056, 0.012, 0.016),
        (0.0, -0.056, 0.012, 0.016),
    ):
        ring = ring.union(_box((0.022, dy, dz), ((RING_X0 + RING_X1) / 2.0, y, z)))
    return ring


def _bayonet_ring_shape():
    """Bayonet collar: 3 broad ears + 3 internal locking bosses (quarter-turn)."""
    ring = _x_tube(RING_X0, RING_X1, RING_RO - 0.002, RING_RI)
    xc = (RING_X0 + RING_X1) / 2.0
    for index in range(3):
        angle = 2.0 * math.pi * index / 3.0
        ear = (
            cq.Workplane("YZ").center(0.064 * math.cos(angle), 0.064 * math.sin(angle))
            .circle(0.012).extrude(0.024).translate((RING_X0 + 0.002, 0.0, 0.0))
        )
        boss = (
            cq.Workplane("YZ").center(0.050 * math.cos(angle), 0.050 * math.sin(angle))
            .circle(0.005).extrude(0.010).translate((xc, 0.0, 0.0))
        )
        ring = ring.union(ear).union(boss)
    return ring


def _sausage_nozzle_shape():
    """Lofted tapered stuffing horn (open both ends) + capture flange (body)."""
    outer = (
        cq.Workplane("YZ").circle(0.0105)
        .workplane(offset=0.115).circle(0.030)
        .loft(combine=True).translate((-0.244, 0.0, 0.0))
    )
    inner = (
        cq.Workplane("YZ").circle(0.0075)
        .workplane(offset=0.119).circle(0.0265)
        .loft(combine=True).translate((-0.246, 0.0, 0.0))
    )
    horn = outer.cut(inner)
    flange = _x_tube(-0.134, -0.128, 0.046, 0.027)
    return horn.union(flange)


def _kibbe_former_shape():
    """Hollow annular kibbe cone + rear flange + center mandrel on 3 spokes."""
    tip_x, length = -0.226, 0.098
    outer = (
        cq.Workplane("YZ").circle(0.024)
        .workplane(offset=length).circle(0.037)
        .loft(combine=True).translate((tip_x, 0.0, 0.0))
    )
    inner = (
        cq.Workplane("YZ").circle(0.018)
        .workplane(offset=length + 0.002).circle(0.030)
        .loft(combine=True).translate((tip_x - 0.001, 0.0, 0.0))
    )
    former = outer.cut(inner)
    former = former.union(_x_tube(-0.134, -0.126, 0.047, 0.036))
    mandrel = (
        cq.Workplane("YZ").circle(0.009)
        .workplane(offset=0.088).circle(0.014)
        .loft(combine=True).translate((tip_x - 0.002, 0.0, 0.0))
    )
    former = former.union(mandrel)
    spoke = _box((0.010, 0.068, 0.0045), (-0.135, 0.0, 0.0))
    for angle in (0.0, 60.0, 120.0):
        former = former.union(spoke.rotate((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), angle))
    return former


# --------------------------------------------------------------------------- #
# Mount meshes (Slot A).                                                       #
# --------------------------------------------------------------------------- #
def _mount_neck_shape():
    """Short cast pedestal neck bridging the chamber bottom to the mount foot."""
    return (
        cq.Workplane("XZ")
        .polyline([(-0.056, -0.028), (0.056, -0.028), (0.046, -0.110), (-0.046, -0.110)])
        .close()
        .extrude(0.046, both=True)
    )


def _countertop_base_shape():
    mount = _mount_neck_shape()
    mount = mount.union(cq.Workplane("XY").rect(0.180, 0.130).extrude(0.016).translate((0.0, 0.0, -0.126)))
    for y in (-0.024, 0.024):
        gusset = (
            cq.Workplane("XZ").polyline([(-0.050, -0.118), (0.050, -0.118), (0.0, -0.060)]).close()
            .extrude(0.014, both=True).translate((0.0, y, 0.0))
        )
        mount = mount.union(gusset)
    for x in (-0.066, 0.066):
        for y in (-0.045, 0.045):
            mount = mount.cut(_z_tube(-0.135, -0.101, 0.0052, x=x, y=y))
            mount = mount.cut(_z_tube(-0.116, -0.110, 0.0095, x=x, y=y))
    return mount


def _freestanding_pedestal_shape():
    mount = _mount_neck_shape()
    # Cast plinth: chamfered shoulders down to a flat workbench sole.
    shoulder = (
        cq.Workplane("XY").circle(0.055)
        .workplane(offset=0.030).circle(0.076)
        .loft(combine=True).translate((0.0, 0.0, -0.140))
    )
    sole = _z_tube(-0.150, -0.140, 0.078)
    return mount.union(shoulder).union(sole)


def _clamp_frame_shape():
    """Table C/U-clamp frame descending below the chamber + threaded boss.

    Legs overlap the mount neck at the top so the frame fuses into one solid."""
    frame = _mount_neck_shape()
    frame = frame.union(_box((0.014, 0.014, 0.170), (0.035, -0.044, -0.180)))
    frame = frame.union(_box((0.014, 0.014, 0.170), (0.035, 0.044, -0.180)))
    frame = frame.union(_box((0.014, 0.102, 0.014), (0.035, 0.0, -0.262)))
    frame = frame.union(_z_tube(-0.276, -0.248, 0.015, 0.0078, x=0.035))
    return frame


def _screw_stem_shape():
    # Long stem so the T-handle rides well below the clamp frame (clears it
    # across the full +0.045 tightening travel).
    return _z_tube(-0.340, -0.190, 0.006, x=0.035)


def _clamp_pad_shape():
    return _z_tube(-0.196, -0.187, 0.023, x=0.035)


# --------------------------------------------------------------------------- #
# Mesh instantiation helper (unit_scale = body_scale; content-addressed cache).#
# --------------------------------------------------------------------------- #
def _mesh(shape, name, s, assets, tol=0.0009, ang=0.09):
    return mesh_from_cadquery(shape, name, assets=assets, unit_scale=s, tolerance=tol, angular_tolerance=ang)


def _v(xyz: tuple[float, float, float], s: float) -> tuple[float, float, float]:
    return (xyz[0] * s, xyz[1] * s, xyz[2] * s)


# --------------------------------------------------------------------------- #
# Builders                                                                     #
# --------------------------------------------------------------------------- #
def _build_body(model, r, mats, *, assets):
    s = r.body_scale
    body = model.part("body")
    body.visual(_mesh(_housing_cast_shape(), "mg_housing", s, assets, tol=0.0009),
                material=mats["body_metal"], name="housing_cast", material_class_id=("metal.stainless_matte" if r.palette_style in {"stainless_rubber", "stainless_yellow", "tinned_high_contrast", "red_enamel", "bronze_and_brass"} else "metal.aluminum_bare"))
    body.visual(_mesh(_cutting_plate_shape(), "mg_plate", s, assets, tol=0.0007),
                material=mats["steel_light"], name="cutting_plate", material_class_id=("metal.stainless_matte" if r.palette_style in {"stainless_rubber", "cast_aluminum_offwhite", "stainless_yellow", "tinned_high_contrast", "red_enamel"} else "metal.brass_polished"))

    # Hopper (Slot B) — fused body visual on the throat top (Rule 1: no motion).
    hopper_shape = _HOPPER_SHAPES[r.hopper_form](r.hopper_scale)
    body.visual(
        _mesh(hopper_shape, f"mg_hopper_{r.hopper_form}", s, assets, tol=0.0009),
        origin=Origin(xyz=_v((THROAT_X, 0.0, THROAT_TOP_Z - 0.006), s)),
        material=mats["body_metal"], name="hopper_shell", material_class_id=("metal.stainless_matte" if r.palette_style in {"stainless_rubber", "stainless_yellow", "tinned_high_contrast", "red_enamel", "bronze_and_brass"} else "metal.aluminum_bare"),
    )

    # Mount (Slot A) — fused body visuals on −Z.
    if r.mount == "table_clamp":
        body.visual(_mesh(_clamp_frame_shape(), "mg_clampframe", s, assets, tol=0.0009),
                    material=mats["body_metal"], name="clamp_frame", material_class_id=("metal.stainless_matte" if r.palette_style in {"stainless_rubber", "stainless_yellow", "tinned_high_contrast", "red_enamel", "bronze_and_brass"} else "metal.aluminum_bare"))
    elif r.mount == "countertop_base":
        body.visual(_mesh(_countertop_base_shape(), "mg_counterbase", s, assets, tol=0.0009),
                    material=mats["body_metal"], name="mount_cast", material_class_id=("metal.stainless_matte" if r.palette_style in {"stainless_rubber", "stainless_yellow", "tinned_high_contrast", "red_enamel", "bronze_and_brass"} else "metal.aluminum_bare"))
    else:  # freestanding_pedestal
        body.visual(_mesh(_freestanding_pedestal_shape(), "mg_pedestal", s, assets, tol=0.0009),
                    material=mats["body_metal"], name="mount_cast", material_class_id=("metal.stainless_matte" if r.palette_style in {"stainless_rubber", "stainless_yellow", "tinned_high_contrast", "red_enamel", "bronze_and_brass"} else "metal.aluminum_bare"))

    # Output attachment (Slot D) — sausage / kibbe are fused body outlet visuals.
    if r.output == "sausage_nozzle":
        body.visual(_mesh(_sausage_nozzle_shape(), "mg_sausage", s, assets, tol=0.0009),
                    material=mats["steel_light"], name="sausage_nozzle", material_class_id=("metal.stainless_matte" if r.palette_style in {"stainless_rubber", "cast_aluminum_offwhite", "stainless_yellow", "tinned_high_contrast", "red_enamel"} else "metal.brass_polished"))
    elif r.output == "kibbe_former":
        body.visual(_mesh(_kibbe_former_shape(), "mg_kibbe", s, assets, tol=0.0009),
                    material=mats["steel_light"], name="kibbe_former", material_class_id=("metal.stainless_matte" if r.palette_style in {"stainless_rubber", "cast_aluminum_offwhite", "stainless_yellow", "tinned_high_contrast", "red_enamel"} else "metal.brass_polished"))
    return body


def _build_auger(model, r, mats, *, body, assets):
    s = r.body_scale
    k = r.crank_reach_scale
    auger = model.part("auger_drive")
    dual = r.output == "kibbe_former"  # dual-blade cutter reads best on kibbe extrusion; else cross knife
    auger.visual(_mesh(_auger_core_shape(), "mg_auger", s, assets, tol=0.0009),
                 material=mats["dark_steel"], name="auger_flight", material_class_id="metal.blackened_gunmetal")
    auger.visual(_mesh(_cutter_blade_shape(dual), f"mg_cutter_{'dual' if dual else 'cross'}", s, assets, tol=0.0006),
                 material=mats["dark_steel"], name="cutter_blade", material_class_id="metal.blackened_gunmetal")

    # Drive geometry (Slot C) rigid on the auger shaft; sets the grip pin point.
    if r.drive == "spoked_handwheel":
        pin = (SPINNER_PIN[0], SPINNER_PIN[1], SPINNER_PIN[2] * k)
        auger.visual(Cylinder(radius=0.022 * s, length=0.020 * s),
                     origin=Origin(xyz=_v((WHEEL_X, 0.0, 0.0), s), rpy=(0.0, math.pi / 2.0, 0.0)),
                     material=mats["steel_light"], name="handwheel_hub", material_class_id=("metal.stainless_matte" if r.palette_style in {"stainless_rubber", "cast_aluminum_offwhite", "stainless_yellow", "tinned_high_contrast", "red_enamel"} else "metal.brass_polished"))
        auger.visual(_mesh(_x_tube(-0.007, 0.007, 0.072, 0.060), "mg_wheel_rim", s, assets, tol=0.0006),
                     origin=Origin(xyz=_v((WHEEL_X, 0.0, 0.0), s)),
                     material=mats["steel_light"], name="handwheel_rim", material_class_id=("metal.stainless_matte" if r.palette_style in {"stainless_rubber", "cast_aluminum_offwhite", "stainless_yellow", "tinned_high_contrast", "red_enamel"} else "metal.brass_polished"))
        for index in range(6):
            angle = 2.0 * math.pi * index / 6.0
            cy, cz = math.cos(angle), math.sin(angle)
            mid_r = 0.040
            auger.visual(
                Box((0.012 * s, 0.052 * s, 0.008 * s)),
                origin=Origin(xyz=_v((WHEEL_X, mid_r * cy, mid_r * cz), s), rpy=(angle, 0.0, 0.0)),
                material=mats["steel_light"], name=f"handwheel_spoke_{index}", material_class_id=("metal.stainless_matte" if r.palette_style in {"stainless_rubber", "cast_aluminum_offwhite", "stainless_yellow", "tinned_high_contrast", "red_enamel"} else "metal.brass_polished"),
            )
        auger.visual(Cylinder(radius=0.0046 * s, length=0.100 * s),
                     origin=Origin(xyz=_v((pin[0], pin[1], pin[2]), s), rpy=(0.0, math.pi / 2.0, 0.0)),
                     material=mats["steel_light"], name="grip_pin", material_class_id=("metal.stainless_matte" if r.palette_style in {"stainless_rubber", "cast_aluminum_offwhite", "stainless_yellow", "tinned_high_contrast", "red_enamel"} else "metal.brass_polished"))
        grip_pin_world = pin
    else:
        if r.drive == "geared_crank":
            auger.visual(_mesh(_geared_wheel_shape(), "mg_gear", s, assets, tol=0.0008),
                         material=mats["steel_light"], name="gear_disc", material_class_id=("metal.stainless_matte" if r.palette_style in {"stainless_rubber", "cast_aluminum_offwhite", "stainless_yellow", "tinned_high_contrast", "red_enamel"} else "metal.brass_polished"))
        pin = (CRANK_PIN[0], CRANK_PIN[1] * k, CRANK_PIN[2] * k)
        crank_path = [
            _v((CRANK_ROOT_X, 0.0, 0.0), s),
            _v((CRANK_ROOT_X + 0.006, 0.018 * k, -0.045 * k), s),
            _v((pin[0], pin[1], pin[2]), s),
        ]
        auger.visual(
            mesh_from_geometry(
                tube_from_spline_points(crank_path, radius=0.0050 * s, samples_per_segment=14,
                                        radial_segments=16, cap_ends=True),
                "mg_crank_arm",
            ),
            material=mats["steel_light"], name="crank_arm", material_class_id=("metal.stainless_matte" if r.palette_style in {"stainless_rubber", "cast_aluminum_offwhite", "stainless_yellow", "tinned_high_contrast", "red_enamel"} else "metal.brass_polished"),
        )
        auger.visual(Cylinder(radius=0.0048 * s, length=0.070 * s),
                     origin=Origin(xyz=_v((pin[0] + 0.030, pin[1], pin[2]), s), rpy=(0.0, math.pi / 2.0, 0.0)),
                     material=mats["steel_light"], name="grip_pin", material_class_id=("metal.stainless_matte" if r.palette_style in {"stainless_rubber", "cast_aluminum_offwhite", "stainless_yellow", "tinned_high_contrast", "red_enamel"} else "metal.brass_polished"))
        grip_pin_world = pin

    # Joint origin on the X-axis at the world origin: the auger is coaxial with
    # +X so the axis IS its symmetry centerline (origin-honesty passes) and the
    # child-local frame == world, so auger visuals land where authored.
    model.articulation(
        "body_to_auger", ArticulationType.CONTINUOUS, parent=body, child=auger,
        origin=Origin(xyz=(0.0, 0.0, 0.0)), axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=45.0, velocity=5.0),
        meta={"mechanism": "auger + cutter + crank spin about the grind axis"},
    )
    return auger, grip_pin_world


def _geared_wheel_shape():
    thickness, root_r, tooth_d = 0.016, 0.043, 0.010
    gear = cq.Workplane("YZ").circle(root_r).extrude(thickness)
    gear = gear.union(cq.Workplane("YZ").circle(0.016).extrude(thickness + 0.006).translate((-0.003, 0.0, 0.0)))
    for index in range(18):
        angle = 360.0 * index / 18.0
        tooth = (
            cq.Workplane("XY").box(thickness, 0.012, tooth_d, centered=(False, True, True))
            .translate((0.0, root_r + tooth_d * 0.5, 0.0)).rotate((0, 0, 0), (1, 0, 0), angle)
        )
        gear = gear.union(tooth)
    for index in range(5):
        angle = 2.0 * math.pi * index / 5.0
        gear = gear.cut(cq.Workplane("YZ").center(0.027 * math.cos(angle), 0.027 * math.sin(angle)).circle(0.006).extrude(thickness))
    return gear.translate((WHEEL_X, 0.0, 0.0))


def _build_grip(model, r, mats, *, auger, grip_pin_world, assets):
    s = r.body_scale
    grip = model.part("crank_grip")
    # Grip visuals authored in the grip's LOCAL frame (joint origin = the crank
    # pin world point, in the auger's frame which is identity). The grip sleeve
    # is coaxial with +X about the pin line so the axis is its symmetry
    # centerline (origin-honesty passes).
    grip.visual(
        _mesh(_grip_shape(), "mg_grip", s, assets, tol=0.0008),
        material=mats["accent"], name="grip_sleeve", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"cast_aluminum_offwhite", "stainless_yellow", "red_enamel", "bronze_and_brass"} else "rubber.smooth_plain"),
    )
    model.articulation(
        "auger_to_grip", ArticulationType.CONTINUOUS, parent=auger, child=grip,
        origin=Origin(xyz=_v((grip_pin_world[0], grip_pin_world[1], grip_pin_world[2]), s)),
        axis=(1.0, 0.0, 0.0), motion_limits=MotionLimits(effort=2.0, velocity=8.0),
        meta={"mechanism": "free-spinning hand grip on the crank pin"},
    )
    return grip


def _build_ring(model, r, mats, *, body, assets):
    s = r.body_scale
    ring = model.part("retaining_ring")
    if r.ring_is_bayonet:
        ring.visual(_mesh(_bayonet_ring_shape(), "mg_ring_bayonet", s, assets, tol=0.0007),
                    material=mats["body_metal"], name="ring_shell", material_class_id=("metal.stainless_matte" if r.palette_style in {"stainless_rubber", "stainless_yellow", "tinned_high_contrast", "red_enamel", "bronze_and_brass"} else "metal.aluminum_bare"))
        model.articulation(
            "body_to_ring", ArticulationType.REVOLUTE, parent=body, child=ring,
            origin=Origin(xyz=(0.0, 0.0, 0.0)), axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=12.0, velocity=2.0, lower=0.0, upper=0.42),
            meta={"mechanism": "quarter-turn bayonet retaining collar"},
        )
    else:
        ring.visual(_mesh(_plain_ring_shape(), "mg_ring_plain", s, assets, tol=0.0007),
                    material=mats["body_metal"], name="ring_shell", material_class_id=("metal.stainless_matte" if r.palette_style in {"stainless_rubber", "stainless_yellow", "tinned_high_contrast", "red_enamel", "bronze_and_brass"} else "metal.aluminum_bare"))
        model.articulation(
            "body_to_ring", ArticulationType.CONTINUOUS, parent=body, child=ring,
            origin=Origin(xyz=(0.0, 0.0, 0.0)), axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=12.0, velocity=2.0),
            meta={"mechanism": "threaded retaining collar screws on and off"},
        )
    return ring


def _build_clamp_screw(model, r, mats, *, body, assets):
    s = r.body_scale
    screw = model.part("clamp_screw")
    screw.visual(_mesh(_screw_stem_shape(), "mg_screw_stem", s, assets, tol=0.0007),
                 material=mats["steel_light"], name="screw_stem", material_class_id=("metal.stainless_matte" if r.palette_style in {"stainless_rubber", "cast_aluminum_offwhite", "stainless_yellow", "tinned_high_contrast", "red_enamel"} else "metal.brass_polished"))
    screw.visual(_mesh(_clamp_pad_shape(), "mg_clamp_pad", s, assets, tol=0.0007),
                 material=mats["steel_light"], name="clamp_pad", material_class_id=("metal.stainless_matte" if r.palette_style in {"stainless_rubber", "cast_aluminum_offwhite", "stainless_yellow", "tinned_high_contrast", "red_enamel"} else "metal.brass_polished"))
    screw.visual(Box((0.012 * s, 0.072 * s, 0.010 * s)),
                 origin=Origin(xyz=_v((0.035, 0.0, -0.335), s)),
                 material=mats["accent2"], name="clamp_handle", material_class_id=("metal.brushed_silver" if r.palette_style in {"stainless_rubber", "cast_aluminum_offwhite", "tinned_high_contrast", "red_enamel", "bronze_and_brass"} else "plastic.opaque_glossy_molded"))
    # Prismatic origin is gauge freedom (origin-honesty exempt); child-local ==
    # world so the screw stem lands inside the clamp boss (connectivity).
    model.articulation(
        "body_to_clamp_screw", ArticulationType.PRISMATIC, parent=body, child=screw,
        origin=Origin(xyz=(0.0, 0.0, 0.0)), axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=400.0, velocity=0.05, lower=0.0, upper=0.045),
        meta={"mechanism": "clamp screw tightens up against the table edge"},
    )
    return screw


# --------------------------------------------------------------------------- #
# Top-level builder                                                            #
# --------------------------------------------------------------------------- #
def build_meat_grinder(
    config: MeatGrinderConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        key: model.material(f"meat_grinder_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in PALETTES[r.palette_style].items()
    }

    body = _build_body(model, r, mats, assets=assets)
    auger, grip_pin_world = _build_auger(model, r, mats, body=body, assets=assets)
    _build_grip(model, r, mats, auger=auger, grip_pin_world=grip_pin_world, assets=assets)
    _build_ring(model, r, mats, body=body, assets=assets)
    if r.has_clamp_screw:
        _build_clamp_screw(model, r, mats, body=body, assets=assets)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_meat_grinder(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_meat_grinder(config_from_seed(seed), assets=assets)


# --------------------------------------------------------------------------- #
# Tests                                                                        #
# --------------------------------------------------------------------------- #
def run_meat_grinder_tests(
    object_model: ArticulatedObject,
    config: MeatGrinderConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)

    body = object_model.get_part("body")
    auger = object_model.get_part("auger_drive")
    grip = object_model.get_part("crank_grip")
    ring = object_model.get_part("retaining_ring")

    auger_joint = object_model.get_articulation("body_to_auger")
    grip_joint = object_model.get_articulation("auger_to_grip")
    ring_joint = object_model.get_articulation("body_to_ring")

    # --- Captured pin / journal allowances (element-scoped). ---
    ctx.allow_overlap(auger, body, elem_a="auger_flight", elem_b="housing_cast",
                      reason="Auger shaft/flight is captured inside the grind chamber bore.")
    ctx.allow_overlap(auger, body, elem_a="cutter_blade", elem_b="housing_cast",
                      reason="Cutter blade rides just behind the plate inside the chamber mouth.")
    ctx.allow_overlap(auger, body, elem_a="cutter_blade", elem_b="cutting_plate",
                      reason="Cutter face presses against the perforated plate (grinding contact).")
    ctx.allow_overlap(ring, body, elem_a="ring_shell", elem_b="housing_cast",
                      reason="Retaining ring is intentionally captured on the front collar.")
    ctx.allow_overlap(ring, body, elem_a="ring_shell", elem_b="cutting_plate",
                      reason="Retaining ring holds the perforated cutting plate in the outlet.")
    if r.output in ("sausage_nozzle", "kibbe_former"):
        outlet = "sausage_nozzle" if r.output == "sausage_nozzle" else "kibbe_former"
        ctx.allow_overlap(ring, body, elem_a="ring_shell", elem_b=outlet,
                          reason="Retaining ring captures the outlet attachment flange.")
    ctx.allow_overlap(grip, auger, elem_a="grip_sleeve", elem_b="grip_pin",
                      reason="Hand grip sleeve is captured on the crank pin.")
    ctx.allow_overlap(grip, auger, elem_a="grip_sleeve", elem_b="crank_arm",
                      reason="Grip sleeve seats against the crank arm end at the pin root.")
    if r.has_clamp_screw:
        clamp_screw = object_model.get_part("clamp_screw")
        ctx.allow_overlap(clamp_screw, body, elem_a="screw_stem", elem_b="clamp_frame",
                          reason="Clamp screw stem threads through the clamp boss.")

    # --- Category identity checks. ---
    expected_parts = {"body", "auger_drive", "crank_grip", "retaining_ring"}
    if r.has_clamp_screw:
        expected_parts.add("clamp_screw")
    ctx.check(
        "part hierarchy matches the resolved slots",
        {p.name for p in object_model.parts} == expected_parts,
        details=f"parts={[p.name for p in object_model.parts]} expected={sorted(expected_parts)}",
    )
    ctx.check(
        "auger + crank share the grind axis (CONTINUOUS +X)",
        auger_joint.articulation_type == ArticulationType.CONTINUOUS
        and tuple(auger_joint.axis) == (1.0, 0.0, 0.0),
        details=f"type={auger_joint.articulation_type} axis={auger_joint.axis}",
    )
    ctx.check(
        "grip free-spins on its pin (CONTINUOUS +X)",
        grip_joint.articulation_type == ArticulationType.CONTINUOUS
        and tuple(grip_joint.axis) == (1.0, 0.0, 0.0),
        details=f"type={grip_joint.articulation_type} axis={grip_joint.axis}",
    )
    if r.ring_is_bayonet:
        ok = (
            ring_joint.articulation_type == ArticulationType.REVOLUTE
            and tuple(ring_joint.axis) == (1.0, 0.0, 0.0)
            and ring_joint.motion_limits is not None
            and abs(ring_joint.motion_limits.upper - 0.42) < 1e-6
        )
    else:
        ok = (
            ring_joint.articulation_type == ArticulationType.CONTINUOUS
            and tuple(ring_joint.axis) == (1.0, 0.0, 0.0)
        )
    ctx.check("retaining ring joint matches the output slot", ok,
              details=f"output={r.output} type={ring_joint.articulation_type} lims={ring_joint.motion_limits}")

    # --- Targeted motion: a half turn carries the grip around the axis. ---
    rest = ctx.part_world_position(grip)
    with ctx.pose({auger_joint: math.pi}):
        turned = ctx.part_world_position(grip)
    ctx.check(
        "cranking the auger carries the grip around the grind axis",
        rest is not None and turned is not None
        and ((turned[1] - rest[1]) ** 2 + (turned[2] - rest[2]) ** 2) ** 0.5 > 0.02,
        details=f"rest={rest} half_turn={turned}",
    )
    if r.ring_is_bayonet:
        with ctx.pose({ring_joint: 0.42}):
            pass  # exercised by sampled-pose QC below; presence check above suffices
    if r.has_clamp_screw:
        clamp_joint = object_model.get_articulation("body_to_clamp_screw")
        cs = object_model.get_part("clamp_screw")
        rest_s = ctx.part_world_position(cs)
        with ctx.pose({clamp_joint: 0.045}):
            up_s = ctx.part_world_position(cs)
        ctx.check(
            "clamp screw rises when tightened",
            rest_s is not None and up_s is not None and (up_s[2] - rest_s[2]) > 0.02,
            details=f"rest={rest_s} tight={up_s}",
        )

    # --- Motion QC + slot_choices. ---
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=48, ignore_fixed=True)
    ctx.check(
        "slot_choices recorded on meta",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )
    return ctx.report()


__all__ = (
    "MeatGrinderConfig",
    "ResolvedMeatGrinderConfig",
    "build_meat_grinder",
    "build_seeded_meat_grinder",
    "config_from_seed",
    "resolve_config",
    "run_meat_grinder_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "Mount",
    "HopperForm",
    "Drive",
    "Output",
    "PaletteStyle",
    "MOUNTS",
    "HOPPER_FORMS",
    "DRIVES",
    "OUTPUTS",
    "PALETTE_STYLES",
    "PALETTES",
)
