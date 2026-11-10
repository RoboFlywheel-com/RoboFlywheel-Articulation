# SPDX-License-Identifier: Apache-2.0

"""Astronomy / Astronaut helmet — modular procedural template.

A wearable astronaut / spacesuit helmet: a hollow white shell dome (spherical /
cylindrical-barrel "diving bell" / big-opening "fishbowl" / rectangular-window)
with a front face aperture, carrying — as parallel children parented directly to
the shell — a movable transparent visor (a flip-up bubble, or a
dual nested inner+outer pair) and a neck base (a collar fused into the shell, or
a separate bayonet locking ring on a rotary joint). A black interior chin lip,
ribbed EVA connector ports, a stepped ribbed neck ring and NASA logo / US flag
decals complete the identity.

Slot graph (pattern = mixed: root shell + 2 parallel-children slots + 2
multiplicity axes ``collar_rib_count`` / ``eva_port_count``):

    shell (root; sphere_dome / cyl_barrel / fishbowl / rect_window)
        |-- visor      (flip_visor / dual_flip_visor)
        +-- neck_base  (fused_collar / twist_lock_ring)

Adapted per AUTHORING.md §A/§B from the confirmed 5-star Astronaut helmet pool
(spec: specs_modular_v1/Astronomy_Astronaut_helmet.md). Geometry uses CadQuery
booleans (``mesh_from_cadquery``) exactly like the 5-star sources (Rule 3 — no
downgrade to Box/Cylinder placeholders). Sources (model.py:Lx-Ly in the spec
Module Source Index):

  S1  origin 母本 rec_costume-...2b95133f  — sphere shell, small circular opening,
      flip REVOLUTE amber visor, fused 14-rib collar, rear hose, decals, lip.
  S2  collar_ribs      — collar rib count multiplicity.
  S3  cyl_shell        — cylindrical-barrel + hemisphere dome shell (③).
  S4  dual_visor       — nested inner clear visor + independent REVOLUTE (①).
  S5  full_bubble      — large fishbowl opening + hemispherical dome visor (③).
  S6  neck_ports       — N evenly spaced EVA connector ports (multiplicity).
  S7  rect_window      — wide rectangular wraparound window + rect pane (③).
  S9  twist_lock_ring  — separate bayonet locking ring on REVOLUTE(Z) (①/②).

Coordinate frame: the shell is authored around its own sphere center; the shell
visuals and the visor articulation sit at ``CENTER_Z`` (= 0.160 * shell_scale)
above the ground so the neck ring rests on z = 0.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Literal

import cadquery as cq

from agent.templates._modular import (
    InterfaceSpec,
    ModuleBuild,
    ModuleBuildContext,
    SlotSpec,
    assemble,
)
from sdk import (
    AppearanceOnlySpec,
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
)

# Modular template: sweep coverage uses module_topology_diversity.
__modular__ = True


ShellForm = Literal["sphere_dome", "cyl_barrel", "fishbowl", "rect_window"]
VisorModule = Literal["flip_visor", "dual_flip_visor"]
NeckModule = Literal["fused_collar", "twist_lock_ring"]
HelmetPalette = Literal[
    "nasa_white",
    "mercury_silver",
    "eva_orange",
    "soviet_white",
    "matte_black",
    "lunar_gold",
]

SHELL_FORM_VALUES: tuple[ShellForm, ...] = (
    "sphere_dome",
    "cyl_barrel",
    "fishbowl",
    "rect_window",
)
VISOR_MODULE_VALUES: tuple[VisorModule, ...] = (
    "flip_visor",
    "dual_flip_visor",
)
NECK_MODULE_VALUES: tuple[NeckModule, ...] = ("fused_collar", "twist_lock_ring")
COLLAR_RIB_VALUES = (12, 14, 18, 24, 30)
EVA_PORT_VALUES = (1, 2, 3, 4, 5, 6)


# --------------------------------------------------------------------------- #
# Canonical base dimensions (origin 母本 rec_costume-...2b95133f); everything is
# scaled uniformly by ``shell_scale`` at emit time.
# --------------------------------------------------------------------------- #

R_OUT = 0.150          # shell outer radius
R_IN = 0.142           # shell inner radius (hollow)
CENTER_Z = 0.160       # sphere-center height above ground (base scale)
NECK_CUT_Z = -0.105    # shell cut flat below this local z (neck ring takes over)
DOME_START_Z = 0.080   # cyl wall -> hemisphere dome transition (cyl_barrel)

VISOR_R_IN = 0.152     # amber bubble inner radius (2 mm clear of shell)
VISOR_R_OUT = 0.157
FRAME_R_IN = 0.154     # raised white frame sits proud of the bubble
FRAME_R_OUT = 0.161
PIVOT_Y = 0.1498       # inner face of each pivot disk (0.2 mm embed on the shell)

# Inner clear protective visor radii (dual_visor S4).
INNER_VISOR_R_IN = 0.1505
INNER_VISOR_R_OUT = 0.1518
INNER_ARM_R_IN = 0.1495
INNER_ARM_R_OUT = 0.1518
# The same proud band expressed radially, for the cylinder envelope.
INNER_LENS_PROUD_OUT = INNER_VISOR_R_OUT - R_OUT   # +1.8 mm
INNER_LENS_PROUD_IN = INNER_VISOR_R_IN - R_OUT     # +0.5 mm

ARM_R_IN = 0.148     # visor side-arm inner radius (embeds 2 mm into the shell)
ARM_R_OUT = 0.163

# Brow-hinge lugs (cyl_barrel only; see ``visor_hinge`` in resolve_config).
BROW_LUG_R = 0.016
BROW_LUG_Y0 = 0.046
BROW_LUG_Y1 = 0.062
BROW_KNOB_R = 0.009

# EVA connector port (neck_ports S6).
PORT_LOCAL_Z = -0.050
PORT_REAR_ARC = 1.6  # base rear arc (rad) for <=4 ports, clear of the front
PORT_ARC_MAX = 2.6   # widest rear spread; still clear of every realized aperture
PORT_PITCH_MIN = 0.052  # min arc-length pitch between port stubs (stub dia 46 mm)

# Small circular opening / large fishbowl / rect window aperture bases.
OPENING_R_SMALL = 0.092
OPENING_ZC_SMALL = 0.010
OPENING_R_LARGE = 0.120
OPENING_ZC_LARGE = 0.050
WIN_HALF_W = 0.100
WIN_HALF_H = 0.075
WIN_ZC = 0.005


# --------------------------------------------------------------------------- #
# Palettes (>=6 colorways; every token defined so all .visual materials resolve;
# visor_amber / visor_clear keep alpha < 0.9 = glass class)
# --------------------------------------------------------------------------- #

PALETTES: dict[str, dict[str, tuple[float, float, float, float]]] = {
    "nasa_white": {
        "helmet_white": (0.93, 0.93, 0.90, 1.0),
        "frame_white": (0.96, 0.96, 0.94, 1.0),
        "visor_amber": (0.85, 0.55, 0.12, 0.55),
        "visor_clear": (0.88, 0.92, 0.96, 0.30),
        "interior_black": (0.07, 0.07, 0.07, 1.0),
        "hub_gray": (0.72, 0.73, 0.74, 1.0),
        "logo_red": (0.86, 0.10, 0.08, 1.0),
        "flag_blue": (0.13, 0.18, 0.45, 1.0),
        "flag_stripes": (0.80, 0.15, 0.15, 1.0),
    },
    "mercury_silver": {
        "helmet_white": (0.74, 0.76, 0.79, 1.0),
        "frame_white": (0.82, 0.84, 0.87, 1.0),
        "visor_amber": (0.80, 0.62, 0.20, 0.50),
        "visor_clear": (0.85, 0.90, 0.95, 0.28),
        "interior_black": (0.10, 0.11, 0.12, 1.0),
        "hub_gray": (0.60, 0.62, 0.65, 1.0),
        "logo_red": (0.80, 0.12, 0.10, 1.0),
        "flag_blue": (0.14, 0.20, 0.46, 1.0),
        "flag_stripes": (0.78, 0.16, 0.16, 1.0),
    },
    "eva_orange": {
        "helmet_white": (0.90, 0.45, 0.10, 1.0),
        "frame_white": (0.95, 0.93, 0.90, 1.0),
        "visor_amber": (0.88, 0.58, 0.14, 0.52),
        "visor_clear": (0.88, 0.92, 0.96, 0.30),
        "interior_black": (0.08, 0.08, 0.08, 1.0),
        "hub_gray": (0.70, 0.71, 0.72, 1.0),
        "logo_red": (0.85, 0.11, 0.09, 1.0),
        "flag_blue": (0.12, 0.17, 0.44, 1.0),
        "flag_stripes": (0.80, 0.15, 0.15, 1.0),
    },
    "soviet_white": {
        "helmet_white": (0.90, 0.90, 0.86, 1.0),
        "frame_white": (0.93, 0.92, 0.86, 1.0),
        "visor_amber": (0.82, 0.60, 0.16, 0.53),
        "visor_clear": (0.86, 0.91, 0.95, 0.30),
        "interior_black": (0.09, 0.09, 0.08, 1.0),
        "hub_gray": (0.66, 0.67, 0.66, 1.0),
        "logo_red": (0.82, 0.10, 0.08, 1.0),
        "flag_blue": (0.15, 0.16, 0.40, 1.0),
        "flag_stripes": (0.78, 0.14, 0.14, 1.0),
    },
    "matte_black": {
        "helmet_white": (0.13, 0.14, 0.15, 1.0),
        "frame_white": (0.22, 0.23, 0.24, 1.0),
        "visor_amber": (0.75, 0.50, 0.12, 0.50),
        "visor_clear": (0.70, 0.78, 0.85, 0.28),
        "interior_black": (0.04, 0.04, 0.05, 1.0),
        "hub_gray": (0.45, 0.46, 0.48, 1.0),
        "logo_red": (0.80, 0.12, 0.10, 1.0),
        "flag_blue": (0.12, 0.16, 0.40, 1.0),
        "flag_stripes": (0.74, 0.14, 0.14, 1.0),
    },
    "lunar_gold": {
        "helmet_white": (0.80, 0.66, 0.28, 1.0),
        "frame_white": (0.88, 0.80, 0.55, 1.0),
        "visor_amber": (0.86, 0.60, 0.14, 0.55),
        "visor_clear": (0.88, 0.90, 0.80, 0.30),
        "interior_black": (0.09, 0.07, 0.05, 1.0),
        "hub_gray": (0.72, 0.62, 0.42, 1.0),
        "logo_red": (0.84, 0.12, 0.09, 1.0),
        "flag_blue": (0.14, 0.18, 0.42, 1.0),
        "flag_stripes": (0.80, 0.15, 0.15, 1.0),
    },
}
PALETTE_NAMES = tuple(PALETTES.keys())


# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class AstronomyAstronautHelmetConfig:
    shell_form: ShellForm = "sphere_dome"
    visor_module: VisorModule = "flip_visor"
    neck_module: NeckModule = "fused_collar"
    palette_style: HelmetPalette = "nasa_white"

    collar_rib_count: int = 14
    eva_port_count: int = 1

    shell_scale: float = 1.0
    flip_range: float = 1.31    # REVOLUTE flip upper (rad)
    bayonet_range: float = math.pi / 2.0  # REVOLUTE bayonet upper (rad)


@dataclass(frozen=True)
class ResolvedAstronomyAstronautHelmetConfig:
    shell_form: ShellForm
    visor_module: VisorModule
    neck_module: NeckModule
    palette_style: str

    collar_rib_count: int
    eva_port_count: int

    shell_scale: float
    flip_range: float
    bayonet_range: float

    # Derived aperture / envelope (single-sourced; Contract 3c).
    envelope: str          # "sphere" | "cylinder"
    aperture_kind: str      # "circular" | "rect"
    opening_r: float        # circular aperture radius (base scale)
    opening_zc: float
    win_half_w: float       # rect aperture half-width (base scale)
    win_half_h: float
    win_zc: float
    face_zc: float          # realized face-aperture center height (base scale)

    # Derived visor hinge (cross-slot adaptation; see resolve_config).
    visor_hinge: str        # "center" | "brow"
    hinge_x: float          # hinge axis position (base scale, local frame)
    hinge_z: float

    # Derived multiplicity spread.
    port_arc: float         # rear arc (rad) the EVA ports are spread across

    palette: dict[str, tuple[float, float, float, float]]

    @property
    def s(self) -> float:
        return self.shell_scale

    @property
    def center_z(self) -> float:
        return CENTER_Z * self.shell_scale


# --------------------------------------------------------------------------- #
# Seed-driven sampling (procedural-first)
# --------------------------------------------------------------------------- #


def config_from_seed(seed: int) -> AstronomyAstronautHelmetConfig:
    """Deterministic procedural sampling.

    seed 0 is pinned to the origin 母本 combination (sphere_dome + flip_visor +
    fused_collar, 14 ribs, 1 port, nasa_white) as a documented regression anchor
    (a sparse override; every other seed is fully procedural).
    """
    if seed == 0:
        return AstronomyAstronautHelmetConfig()

    rng = random.Random(seed)

    shell_form: ShellForm = rng.choice(SHELL_FORM_VALUES)
    visor_module: VisorModule = rng.choice(VISOR_MODULE_VALUES)
    neck_module: NeckModule = rng.choice(NECK_MODULE_VALUES)
    palette_style = rng.choice(PALETTE_NAMES)

    # N ranges are set by whether the rule is index-general and by host capacity,
    # not by the integers that happen to appear in the source pool (AUTHORING S3).
    # Collar: notch pitch at r=0.114 stays above the 16 mm notch width up to 30.
    # Ports: pitch stays above the 46 mm stub diameter up to 6 once the rear arc
    # widens (see ``port_arc``).
    collar_rib_count = rng.choices(
        COLLAR_RIB_VALUES, weights=(0.12, 0.3, 0.16, 0.22, 0.2)
    )[0]
    eva_port_count = rng.choices(
        EVA_PORT_VALUES, weights=(0.3, 0.16, 0.18, 0.12, 0.12, 0.12)
    )[0]

    shell_scale = round(rng.uniform(0.90, 1.05), 4)
    flip_range = round(rng.uniform(1.15, 1.35), 4)
    bayonet_range = round(rng.uniform(1.35, 1.60), 4)

    return AstronomyAstronautHelmetConfig(
        shell_form=shell_form,
        visor_module=visor_module,
        neck_module=neck_module,
        palette_style=palette_style,
        collar_rib_count=collar_rib_count,
        eva_port_count=eva_port_count,
        shell_scale=shell_scale,
        flip_range=flip_range,
        bayonet_range=bayonet_range,
    )


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(float(v), hi))


def resolve_config(
    config: AstronomyAstronautHelmetConfig,
) -> ResolvedAstronomyAstronautHelmetConfig:
    if str(config.shell_form) not in SHELL_FORM_VALUES:
        raise ValueError(f"Unsupported shell_form: {config.shell_form}")
    if str(config.visor_module) not in VISOR_MODULE_VALUES:
        raise ValueError(f"Unsupported visor_module: {config.visor_module}")
    if str(config.neck_module) not in NECK_MODULE_VALUES:
        raise ValueError(f"Unsupported neck_module: {config.neck_module}")
    if str(config.palette_style) not in PALETTES:
        raise ValueError(f"Unsupported palette_style: {config.palette_style}")

    shell_scale = _clamp(config.shell_scale, 0.90, 1.05)
    # The cylindrical barrel is the least axisymmetric shell; at larger scale
    # its principal axis tilts just past the 15 mm origin-honesty floor for the
    # bayonet REVOLUTE(Z) axis, so cap it to <=1.0 when a locking ring is used.
    if config.shell_form == "cyl_barrel" and config.neck_module == "twist_lock_ring":
        shell_scale = min(shell_scale, 1.0)
    flip_range = _clamp(config.flip_range, 1.15, 1.35)
    bayonet_range = _clamp(config.bayonet_range, 1.35, 1.60)

    collar_rib_count = int(_clamp(config.collar_rib_count, min(COLLAR_RIB_VALUES), max(COLLAR_RIB_VALUES)))
    eva_port_count = int(_clamp(config.eva_port_count, min(EVA_PORT_VALUES), max(EVA_PORT_VALUES)))

    # Envelope + aperture derivation (single-sourced).
    if config.shell_form == "cyl_barrel":
        envelope = "cylinder"
    else:
        envelope = "sphere"

    if config.shell_form == "fishbowl":
        aperture_kind = "circular"
        opening_r, opening_zc = OPENING_R_LARGE, OPENING_ZC_LARGE
    elif config.shell_form == "rect_window":
        aperture_kind = "rect"
        opening_r, opening_zc = OPENING_R_SMALL, OPENING_ZC_SMALL
    else:  # sphere_dome / cyl_barrel
        aperture_kind = "circular"
        opening_r, opening_zc = OPENING_R_SMALL, OPENING_ZC_SMALL

    # No visor compatibility gate: every declared shell x visor combination is
    # built by LOCAL PARAMETER / SHAPE DERIVATION (AUTHORING S4,
    # MECHANICAL_PRIORS S3). Each visor element takes the same envelope branch
    # (sphere band / cylinder band) and the same aperture branch (circular cap /
    # rect pane) as the shell it rides on.
    visor_module = config.visor_module

    face_zc = WIN_ZC if aperture_kind == "rect" else opening_zc

    # --- Visor hinge, derived from the shell's axis of revolution -----------
    # A REVOLUTE visor can only stay seated on its host if the host is a
    # surface of revolution ABOUT THAT AXIS. sphere_dome / fishbowl /
    # rect_window are spheres, so the origin's centre pivot (axis Y through the
    # sphere centre) keeps the cap concentric at every angle — measured solid
    # intersection is flat across the whole sweep.
    #
    # cyl_barrel is a surface of revolution about Z, NOT about Y, and its dome
    # centre is offset +DOME_START_Z from the pivot. A centre pivot therefore
    # drives the visor straight through the wall (measured: 13.8% of the visor
    # volume buried at 10 deg, vs a flat 3.5% for the sphere) and no clearance
    # value can fix it. So the barrel gets a BROW HINGE instead: the axis moves
    # to the top edge of the bezel, on the shell surface, and the visor lifts
    # forward-and-up away from the shell like a real flip-front helmet. That is
    # host-shape agnostic — every point below the hinge moves outward.
    if envelope == "cylinder":
        visor_hinge = "brow"
        hinge_z = opening_zc + opening_r + 0.014
        # Shell outer surface radius at the hinge height (wall, or dome above
        # it), then the surface X at the LUG's mid-Y — the lugs sit at
        # y=+-0.054, where the surface has already curved inboard, so taking the
        # y=0 radius would leave them floating ~10 mm off the shell.
        if hinge_z <= DOME_START_Z:
            surf_r = R_OUT
        else:
            surf_r = math.sqrt(max(R_OUT**2 - (hinge_z - DOME_START_Z) ** 2, 1e-6))
        lug_y_mid = 0.5 * (BROW_LUG_Y0 + BROW_LUG_Y1)
        hinge_x = math.sqrt(max(surf_r**2 - lug_y_mid**2, 1e-6))
    else:
        visor_hinge = "center"
        hinge_x = 0.0
        hinge_z = 0.0

    # EVA ports: widen the rear arc so the stub pitch stays clear at high N.
    r_at_port = (
        R_OUT
        if envelope == "cylinder"
        else math.sqrt(max(R_OUT * R_OUT - PORT_LOCAL_Z * PORT_LOCAL_Z, 1e-6))
    )
    if eva_port_count <= 1:
        port_arc = 0.0
    else:
        # Two constraints, both derived from N:
        #  - pitch floor: adjacent stubs must not touch;
        #  - origin honesty: a tightly bunched rear bank pulls the shell's
        #    symmetry centerline off the bayonet REVOLUTE(Z) axis, so the arc
        #    widens with N to keep the array centred (worst case is the least
        #    axisymmetric cyl_barrel shell). The origin 3-port spread is the
        #    anchor, so N <= 4 keeps the source arc exactly.
        needed_pitch = PORT_PITCH_MIN * (eva_port_count - 1) / r_at_port
        needed_balance = PORT_REAR_ARC * (eva_port_count - 1) / 3.0
        port_arc = min(
            PORT_ARC_MAX, max(PORT_REAR_ARC, needed_pitch, needed_balance)
        )

    return ResolvedAstronomyAstronautHelmetConfig(
        shell_form=config.shell_form,
        visor_module=visor_module,
        neck_module=config.neck_module,
        palette_style=config.palette_style,
        collar_rib_count=collar_rib_count,
        eva_port_count=eva_port_count,
        shell_scale=shell_scale,
        flip_range=flip_range,
        bayonet_range=bayonet_range,
        envelope=envelope,
        aperture_kind=aperture_kind,
        opening_r=opening_r,
        opening_zc=opening_zc,
        win_half_w=WIN_HALF_W,
        win_half_h=WIN_HALF_H,
        win_zc=WIN_ZC,
        face_zc=face_zc,
        visor_hinge=visor_hinge,
        hinge_x=hinge_x,
        hinge_z=hinge_z,
        port_arc=port_arc,
        palette=dict(PALETTES[config.palette_style]),
    )


# --------------------------------------------------------------------------- #
# CadQuery primitive helpers (adapted verbatim from the 5-star sources)
# --------------------------------------------------------------------------- #


def _sphere(radius: float) -> cq.Shape:
    return cq.Workplane("XY").sphere(radius).val()


def _sphere_shell(r_out: float, r_in: float) -> cq.Shape:
    return _sphere(r_out).cut(_sphere(r_in))


def _x_cylinder(radius: float, x0: float, x1: float, zc: float = 0.0) -> cq.Shape:
    return cq.Solid.makeCylinder(
        radius, x1 - x0, cq.Vector(x0, 0.0, zc), cq.Vector(1.0, 0.0, 0.0)
    )


def _y_cylinder(radius: float, y0: float, y1: float) -> cq.Shape:
    lo, hi = min(y0, y1), max(y0, y1)
    return cq.Solid.makeCylinder(
        radius, hi - lo, cq.Vector(0.0, lo, 0.0), cq.Vector(0.0, 1.0, 0.0)
    )


def _z_cylinder(radius: float, z0: float, z1: float) -> cq.Shape:
    lo, hi = min(z0, z1), max(z0, z1)
    return cq.Solid.makeCylinder(
        radius, hi - lo, cq.Vector(0.0, 0.0, lo), cq.Vector(0.0, 0.0, 1.0)
    )


def _box(sx: float, sy: float, sz: float, center: tuple[float, float, float]) -> cq.Shape:
    return cq.Workplane("XY").box(sx, sy, sz).translate(center).val()


def _hollow_hemisphere(r: float, z_center: float) -> cq.Shape:
    """Top hemisphere of a sphere of radius r, centered at z=z_center (cyl_shell S3)."""
    dome = _sphere(r).translate(cq.Vector(0.0, 0.0, z_center))
    return dome.cut(_box(0.5, 0.5, 0.5, (0.0, 0.0, z_center - 0.25)))


def _scaled(shape: cq.Shape, s: float) -> cq.Shape:
    """Uniform scale about the origin (sphere center) by ``s`` (skip when ~1)."""
    if abs(s - 1.0) < 1e-9:
        return shape
    m = cq.Matrix([[s, 0.0, 0.0, 0.0], [0.0, s, 0.0, 0.0], [0.0, 0.0, s, 0.0]])
    return shape.transformGeometry(m)


# --------------------------------------------------------------------------- #
# Slot A — shell body / interior lip / decals / EVA ports
# --------------------------------------------------------------------------- #


def _cut_opening(shell: cq.Shape, r: ResolvedAstronomyAstronautHelmetConfig) -> cq.Shape:
    if r.aperture_kind == "circular":
        return shell.cut(_x_cylinder(r.opening_r, 0.02, 0.25, r.opening_zc))
    # wide rectangular wraparound window (rect_window S7)
    return shell.cut(_box(0.24, r.win_half_w * 2.0, r.win_half_h * 2.0, (0.14, 0.0, r.win_zc)))


def _shell_body_shape(r: ResolvedAstronomyAstronautHelmetConfig) -> cq.Shape:
    if r.envelope == "cylinder":
        outer = _z_cylinder(R_OUT, NECK_CUT_Z, DOME_START_Z).fuse(
            _hollow_hemisphere(R_OUT, DOME_START_Z)
        )
        inner = _z_cylinder(R_IN, NECK_CUT_Z - 0.001, DOME_START_Z).fuse(
            _hollow_hemisphere(R_IN, DOME_START_Z)
        )
        shell = outer.cut(inner)
        shoulder = _z_cylinder(R_OUT, NECK_CUT_Z - 0.004, NECK_CUT_Z + 0.004).cut(
            _z_cylinder(0.110, NECK_CUT_Z - 0.004, NECK_CUT_Z + 0.004)
        )
        shell = shell.fuse(shoulder)
        return _cut_opening(shell, r)

    # sphere envelope (sphere_dome / fishbowl / rect_window)
    shell = _sphere_shell(R_OUT, R_IN)
    shell = shell.cut(_box(0.5, 0.5, 0.4, (0.0, 0.0, NECK_CUT_Z - 0.2)))  # flat bottom
    return _cut_opening(shell, r)


def _interior_lip_shape(r: ResolvedAstronomyAstronautHelmetConfig) -> cq.Shape:
    if r.envelope == "cylinder":
        lip = _z_cylinder(0.147, -0.085, 0.065).cut(_z_cylinder(0.1405, -0.085, 0.065))
        lip = lip.intersect(_box(0.4, 0.4, 0.045, (0.0, 0.0, -0.0575)))
        return lip.intersect(_x_cylinder(0.096, 0.01, 0.20, r.opening_zc))
    lip = _sphere_shell(0.147, 0.1405)
    lip = lip.intersect(_box(0.4, 0.4, 0.050, (0.0, 0.0, -0.0575)))
    clip = min(r.opening_r + 0.004, 0.140)
    return lip.intersect(_x_cylinder(clip, 0.01, 0.25, r.opening_zc))


def _decal_frame(r: ResolvedAstronomyAstronautHelmetConfig, az: float, elev: float):
    """Return (center_xyz_base, rpy, y_axis, z_axis) for a tangent decal on the
    realized shell surface (sphere tangent, or cylinder wall) — Rule 4 conformal."""
    if r.envelope == "cylinder":
        x = R_OUT * math.cos(az)
        y = R_OUT * math.sin(az)
        z = R_OUT * math.sin(elev)
        center = (x, y, z + CENTER_Z)
        rpy = (0.0, 0.0, az)
        y_axis = (-math.sin(az), math.cos(az), 0.0)
        z_axis = (0.0, 0.0, 1.0)
        return center, rpy, y_axis, z_axis
    x = R_OUT * math.cos(elev) * math.cos(az)
    y = R_OUT * math.cos(elev) * math.sin(az)
    z = R_OUT * math.sin(elev)
    center = (x, y, z + CENTER_Z)
    rpy = (0.0, -elev, az)
    y_axis = (-math.sin(az), math.cos(az), 0.0)
    z_axis = (
        -math.sin(elev) * math.cos(az),
        -math.sin(elev) * math.sin(az),
        math.cos(elev),
    )
    return center, rpy, y_axis, z_axis


def _port_stub_shape() -> cq.Shape:
    """One ribbed EVA port stub along +X, base near the origin (neck_ports S6)."""
    stub = _x_cylinder(0.017, -0.010, 0.030)
    for i in range(3):
        x_rib = -0.006 + 0.012 * i
        stub = stub.fuse(_x_cylinder(0.023, x_rib, x_rib + 0.007))
    return stub


def _emit_shell_mesh(shell, shape, name, material, s) -> None:
    shell.visual(
        mesh_from_cadquery(_scaled(shape, s), name),
        origin=Origin(xyz=(0.0, 0.0, CENTER_Z * s)),
        material=material,
        name=name, material_class_id="plastic.opaque_glossy_molded",
    )


def _shell_downstream(r: ResolvedAstronomyAstronautHelmetConfig) -> InterfaceSpec:
    return InterfaceSpec(
        interface_name="downstream",
        part_name="shell",
        visual_name="shell_body",
        face_side="positive_z",
        anchor_local=(0.0, 0.0, r.center_z),
        contact_tol=0.004,
    )


def _build_shell(ctx: ModuleBuildContext) -> ModuleBuild:
    model = ctx.model
    r: ResolvedAstronomyAstronautHelmetConfig = ctx.config  # type: ignore[assignment]
    s = r.s
    shell = model.part("shell")

    _emit_shell_mesh(shell, _shell_body_shape(r), "shell_body", "helmet_white", s)
    _emit_shell_mesh(shell, _interior_lip_shape(r), "interior_lip", "interior_black", s)

    # --- Red NASA worm-logo decal on the jaw (4 letter blocks) ---
    logo_az = math.radians(47.0)
    logo_el = math.radians(-32.0)
    lc, lrpy, ly, _lz = _decal_frame(r, logo_az, logo_el)
    for i in range(4):
        dy = -0.0180 + 0.0120 * i
        pos = (
            (lc[0] + dy * ly[0]) * s,
            (lc[1] + dy * ly[1]) * s,
            (lc[2] + dy * ly[2]) * s,
        )
        shell.visual(
            Box((0.0015 * s, 0.0090 * s, 0.014 * s)),
            origin=Origin(xyz=pos, rpy=lrpy),
            material="logo_red",
            name=f"nasa_logo_letter_{i}", appearance_only=AppearanceOnlySpec(kind="decal"),
        )

    # --- US flag decal beside the pivot (white base, blue canton, red stripes) ---
    flag_az = math.radians(65.0)
    flag_el = math.radians(-11.5)
    fc, frpy, fy, fz = _decal_frame(r, flag_az, flag_el)
    shell.visual(
        Box((0.0015 * s, 0.030 * s, 0.020 * s)),
        origin=Origin(xyz=(fc[0] * s, fc[1] * s, fc[2] * s), rpy=frpy),
        material="frame_white",
        name="flag_decal_base", appearance_only=AppearanceOnlySpec(kind="decal"),
    )

    def _flag_pos(dy: float, dz: float) -> tuple[float, float, float]:
        return (
            (fc[0] + dy * fy[0] + dz * fz[0]) * s,
            (fc[1] + dy * fy[1] + dz * fz[1]) * s,
            (fc[2] + dy * fy[2] + dz * fz[2]) * s,
        )

    shell.visual(
        Box((0.0016 * s, 0.012 * s, 0.009 * s)),
        origin=Origin(xyz=_flag_pos(-0.0085, 0.0053), rpy=frpy),
        material="flag_blue",
        name="flag_decal_canton", appearance_only=AppearanceOnlySpec(kind="decal"),
    )
    for i in range(3):
        shell.visual(
            Box((0.0016 * s, 0.020 * s, 0.0028 * s)),
            origin=Origin(xyz=_flag_pos(0.0045, 0.0068 - 0.0068 * i), rpy=frpy),
            material="flag_stripes",
            name=f"flag_decal_stripe_{i}", appearance_only=AppearanceOnlySpec(kind="decal"),
        )

    # --- Symmetric neck-ring seat (always present) ---
    # A short annular ring at the neck cut plane. It gives the collar / bayonet
    # ring a real seating surface AND keeps the shell's neck region symmetric so
    # the bayonet REVOLUTE axis reads as the part's symmetry centerline
    # (origin-honesty, Rule 2 / joint-anchor).
    seat = _z_cylinder(0.112, -0.135, -0.100).cut(_z_cylinder(0.100, -0.140, -0.095))
    _emit_shell_mesh(shell, seat, "neck_seat", "helmet_white", s)

    # --- EVA connector ports (multiplicity eva_port_count) ---
    # Distributed across the REAR arc so they never intrude on the front face
    # aperture / visor (a front port would collide with the visor bubble).
    port_mesh = mesh_from_cadquery(_scaled(_port_stub_shape(), s), "eva_port_stub")
    n = r.eva_port_count
    if r.envelope == "cylinder":
        r_at = R_OUT
    else:
        r_at = math.sqrt(max(R_OUT * R_OUT - PORT_LOCAL_Z * PORT_LOCAL_Z, 0.0))
    for i in range(n):
        az = math.pi if n == 1 else math.pi + r.port_arc * (i / (n - 1) - 0.5)
        pos = (
            r_at * math.cos(az) * s,
            r_at * math.sin(az) * s,
            (PORT_LOCAL_Z + CENTER_Z) * s,
        )
        shell.visual(
            port_mesh,
            origin=Origin(xyz=pos, rpy=(0.0, 0.0, az)),
            material="helmet_white",
            name=f"port_{i}", material_class_id="metal.paint_coated",
        )

    return ModuleBuild(
        module_name=r.shell_form,
        parts_emitted=["shell"],
        interfaces={"downstream": _shell_downstream(r)},
    )


# --------------------------------------------------------------------------- #
# Slot B — visor (parallel children on the shell aperture)
# --------------------------------------------------------------------------- #


def _visor_bubble_shape(r: ResolvedAstronomyAstronautHelmetConfig) -> cq.Shape:
    if r.aperture_kind == "rect":
        return _sphere_shell(VISOR_R_OUT, VISOR_R_IN).intersect(
            _box(
                0.22,
                (r.win_half_w - 0.001) * 2.0,
                (r.win_half_h - 0.001) * 2.0,
                (0.11, 0.0, r.win_zc),
            )
        )
    if r.envelope == "cylinder":
        outer = _z_cylinder(
            R_OUT + 0.012, r.opening_zc - r.opening_r - 0.008, r.opening_zc + r.opening_r + 0.008
        )
        inner = _z_cylinder(
            R_OUT + 0.005, r.opening_zc - r.opening_r - 0.008, r.opening_zc + r.opening_r + 0.008
        )
        bubble = outer.cut(inner)
        return bubble.intersect(_x_cylinder(r.opening_r + 0.002, 0.0, 0.20, r.opening_zc))
    # sphere circular (small bubble or large fishbowl dome)
    return _sphere_shell(VISOR_R_OUT, VISOR_R_IN).intersect(
        _x_cylinder(r.opening_r + 0.002, 0.0, 0.25, r.opening_zc)
    )


def _bezel_shape(r: ResolvedAstronomyAstronautHelmetConfig) -> cq.Shape:
    if r.aperture_kind == "rect":
        outer_box = _box(
            0.24, (r.win_half_w + 0.018) * 2.0, (r.win_half_h + 0.018) * 2.0, (0.12, 0.0, r.win_zc)
        )
        inner_box = _box(
            0.25, (r.win_half_w - 0.003) * 2.0, (r.win_half_h - 0.003) * 2.0, (0.12, 0.0, r.win_zc)
        )
        return _sphere_shell(FRAME_R_OUT, FRAME_R_IN).intersect(outer_box.cut(inner_box))
    if r.envelope == "cylinder":
        z_lo = r.opening_zc - r.opening_r - 0.014
        z_hi = r.opening_zc + r.opening_r + 0.014
        bezel_outer = _z_cylinder(R_OUT + 0.016, z_lo, z_hi)
        # The cutting cylinder must OVERRUN the outer one in Z. If it is shorter
        # (as it was: +-8 mm short at each end) the difference leaves a
        # FULL-RADIUS SOLID DISC capping each end of the band instead of an open
        # annulus — invisible while the visor is closed and lying on the shell,
        # but a pair of flat slabs flying off it once the visor swings open.
        # The sphere and rect branches below already overrun; this one did not.
        bezel_inner = _z_cylinder(R_OUT + 0.004, z_lo - 0.010, z_hi + 0.010)
        bezel = bezel_outer.cut(bezel_inner)
        bezel = bezel.intersect(_x_cylinder(r.opening_r + 0.016, 0.0, 0.20, r.opening_zc))
        return bezel.cut(_x_cylinder(r.opening_r - 0.004, -0.01, 0.21, r.opening_zc))
    # sphere circular
    annulus = _x_cylinder(r.opening_r + 0.012, 0.0, 0.25, r.opening_zc).cut(
        _x_cylinder(r.opening_r - 0.016, -0.01, 0.26, r.opening_zc)
    )
    return _sphere_shell(FRAME_R_OUT, FRAME_R_IN).intersect(annulus)


def _arm_shape(r: ResolvedAstronomyAstronautHelmetConfig, side: float) -> cq.Shape:
    # Arm inner radius is set BELOW the shell outer radius so the arm band
    # embeds ~2 mm into the shell exterior and robustly contacts it along its
    # length (fail_if_isolated_parts, 1um) — the round pivot disk only grazes
    # the shell's Y-pole, which is fragile under scaling.
    arm_zc = r.win_zc if r.aperture_kind == "rect" else 0.0
    arm_h = 0.028
    rect_x_c, round_x_c = 0.060, 0.070

    if r.aperture_kind == "rect":
        arm_y_mid = side * (r.win_half_w + 0.018 + PIVOT_Y) * 0.5
        arm_y_span = PIVOT_Y - r.win_half_w - 0.018 + 0.020
        return _sphere_shell(ARM_R_OUT, ARM_R_IN).intersect(
            _box(0.20, arm_y_span, arm_h, (rect_x_c, arm_y_mid, arm_zc))
        )
    if r.envelope == "cylinder":
        z_lo, z_hi = arm_zc - arm_h / 2.0, arm_zc + arm_h / 2.0
        arm = _z_cylinder(R_OUT + 0.011, z_lo, z_hi).cut(_z_cylinder(R_OUT - 0.004, z_lo, z_hi))
        return arm.intersect(_box(0.20, 0.090, arm_h, (round_x_c, side * 0.125, arm_zc)))
    return _sphere_shell(ARM_R_OUT, ARM_R_IN).intersect(
        _box(0.20, 0.090, arm_h, (round_x_c, side * 0.125, arm_zc))
    )


def _inner_hinge_z(r: ResolvedAstronomyAstronautHelmetConfig) -> float:
    """Inner visor hinge, nested just below the outer brow hinge."""
    return r.hinge_z - 0.008


def _y_cylinder_at(radius: float, y0: float, y1: float, xc: float, zc: float) -> cq.Shape:
    """Cylinder along Y whose axis passes through (xc, *, zc)."""
    return _y_cylinder(radius, y0, y1).translate(cq.Vector(xc, 0.0, zc))


def _brow_lug_stack(r: ResolvedAstronomyAstronautHelmetConfig, side: float) -> cq.Shape:
    """Hinge ear straddling the shell surface at the top edge of the bezel.

    Centred ON the hinge axis, so it stays seated on the shell at every angle
    (this is what keeps the visor attached — the bezel band itself stands a few
    mm proud and would otherwise float).
    """
    return _y_cylinder_at(
        BROW_LUG_R, side * BROW_LUG_Y0, side * BROW_LUG_Y1, r.hinge_x, r.hinge_z
    )


def _brow_knob_shape(r: ResolvedAstronomyAstronautHelmetConfig, side: float) -> cq.Shape:
    knob = _y_cylinder_at(
        BROW_KNOB_R, side * (BROW_LUG_Y1 + 0.002), side * (BROW_LUG_Y1 + 0.010),
        r.hinge_x, r.hinge_z,
    )
    bar = _box(0.016, 0.005, 0.005, (r.hinge_x, side * (BROW_LUG_Y1 + 0.008), r.hinge_z))
    return knob.fuse(bar)


def _brow_strap_shape(r: ResolvedAstronomyAstronautHelmetConfig, side: float) -> cq.Shape:
    """Short band tying each hinge lug into the bezel top."""
    band = _z_cylinder(R_OUT + 0.016, r.hinge_z - 0.030, r.hinge_z + 0.006).cut(
        _z_cylinder(R_OUT + 0.002, r.hinge_z - 0.030, r.hinge_z + 0.006)
    )
    return band.intersect(
        _box(0.20, 0.028, 0.040, (0.10, side * (BROW_LUG_Y0 + BROW_LUG_Y1) * 0.5, r.hinge_z - 0.012))
    )


def _pivot_disk_stack(side: float) -> cq.Shape:
    disk = _y_cylinder(0.036, side * PIVOT_Y, side * (PIVOT_Y + 0.013))
    return disk.fuse(_y_cylinder(0.026, side * (PIVOT_Y + 0.013), side * (PIVOT_Y + 0.019)))


def _pivot_knob_shape(side: float) -> cq.Shape:
    knob = _y_cylinder(0.015, side * (PIVOT_Y + 0.017), side * (PIVOT_Y + 0.026))
    bar = _box(0.020, 0.005, 0.006, (0.0, side * (PIVOT_Y + 0.0245), 0.0))
    return knob.fuse(bar)


def _flip_frame_shape(r: ResolvedAstronomyAstronautHelmetConfig) -> cq.Shape:
    frame = _bezel_shape(r)
    if r.visor_hinge == "brow":
        for side in (1.0, -1.0):
            frame = frame.fuse(_brow_strap_shape(r, side))
            frame = frame.fuse(_brow_lug_stack(r, side))
        return frame
    for side in (1.0, -1.0):
        frame = frame.fuse(_arm_shape(r, side))
        frame = frame.fuse(_pivot_disk_stack(side))
    return frame


def _inner_visor_lens_shape(r: ResolvedAstronomyAstronautHelmetConfig) -> cq.Shape:
    # Nested clear pressure visor. It takes the SAME envelope branch (sphere
    # band / cylinder band) AND the same aperture branch (circular cap / rect
    # pane) the outer bubble and bezel already have. A spherical cap on a
    # CYLINDRICAL wall sinks deeper the further it gets from the equator
    # (h-radius sqrt(r^2 - z^2) vs a constant wall radius: -22 mm at z=0.08),
    # which the concentric-cap allow_overlap would otherwise silently mask.
    if r.envelope == "cylinder":
        band = _z_cylinder(R_OUT + INNER_LENS_PROUD_OUT, -0.10, 0.12).cut(
            _z_cylinder(R_OUT + INNER_LENS_PROUD_IN, -0.10, 0.12)
        )
        return band.intersect(
            _x_cylinder(min(0.086, r.opening_r - 0.006), 0.0, 0.20, r.opening_zc)
        )
    if r.aperture_kind == "rect":
        return _sphere_shell(INNER_VISOR_R_OUT, INNER_VISOR_R_IN).intersect(
            _box(
                0.22,
                (r.win_half_w - 0.010) * 2.0,
                (r.win_half_h - 0.010) * 2.0,
                (0.11, 0.0, r.win_zc),
            )
        )
    return _sphere_shell(INNER_VISOR_R_OUT, INNER_VISOR_R_IN).intersect(
        _x_cylinder(min(0.086, r.opening_r - 0.006), 0.0, 0.20, r.opening_zc)
    )


def _inner_visor_frame_shape(r: ResolvedAstronomyAstronautHelmetConfig) -> cq.Shape:
    # Same envelope branch as the lens: on a cylinder the arms/brow are wall
    # bands, not spherical bands (see _inner_visor_lens_shape).
    if r.envelope == "cylinder":
        def _band(z0: float, z1: float) -> cq.Shape:
            return _z_cylinder(R_OUT + INNER_LENS_PROUD_OUT, z0, z1).cut(
                _z_cylinder(R_OUT - 0.0005, z0, z1)
            )
        # Brow-hinged like the outer visor (see resolve_config): the lugs sit on
        # the inner hinge axis so the nested visor stays seated at every angle.
        hz = _inner_hinge_z(r)
        cyl_frame = _band(hz - 0.026, hz + 0.004).intersect(
            _box(0.20, 0.20, 0.040, (0.10, 0.0, hz - 0.011))
        )
        for side in (1.0, -1.0):
            cyl_frame = cyl_frame.fuse(
                _y_cylinder_at(0.011, side * 0.028, side * 0.041, r.hinge_x, hz)
            )
        return cyl_frame

    frame = None
    for side in (1.0, -1.0):
        arm = _sphere_shell(INNER_ARM_R_OUT, INNER_ARM_R_IN).intersect(
            _box(0.20, 0.065, 0.018, (0.060, side * 0.118, 0.0))
        )
        tab = _y_cylinder(0.024, side * 0.143, side * 0.149)
        piece = arm.fuse(tab)
        frame = piece if frame is None else frame.fuse(piece)
    brow = _sphere_shell(INNER_ARM_R_OUT, INNER_ARM_R_IN).intersect(
        _box(0.08, 0.18, 0.022, (0.120, 0.0, 0.008))
    )
    return frame.fuse(brow)


def _visor_knob_shape(r: ResolvedAstronomyAstronautHelmetConfig, side: float) -> cq.Shape:
    return _brow_knob_shape(r, side) if r.visor_hinge == "brow" else _pivot_knob_shape(side)


def _visor_hinge_xyz(r: ResolvedAstronomyAstronautHelmetConfig) -> tuple[float, float, float]:
    if r.visor_hinge == "brow":
        return (r.hinge_x * r.s, 0.0, (r.hinge_z + CENTER_Z) * r.s)
    return (0.0, 0.0, r.center_z)


def _inner_visor_hinge_xyz(r: ResolvedAstronomyAstronautHelmetConfig) -> tuple[float, float, float]:
    if r.visor_hinge == "brow":
        return (r.hinge_x * r.s, 0.0, (_inner_hinge_z(r) + CENTER_Z) * r.s)
    return (0.0, 0.0, r.center_z)


def _visor_child_offset(r: ResolvedAstronomyAstronautHelmetConfig, hinge_z: float) -> Origin:
    """Visor geometry is authored in SHELL-local coordinates, but a URDF child
    link's frame is the joint origin. With the centre pivot the two coincide;
    with the brow hinge they do not, so shift the visuals back by the hinge."""
    if r.visor_hinge != "brow":
        return Origin(xyz=(0.0, 0.0, 0.0))
    return Origin(xyz=(-r.hinge_x * r.s, 0.0, -hinge_z * r.s))


def _emit_visor_mesh(part, shape, name, material, s, origin=None) -> None:
    part.visual(
        mesh_from_cadquery(_scaled(shape, s), name),
        origin=origin or Origin(xyz=(0.0, 0.0, 0.0)),
        material=material,
        name=name, material_class_id="glass.clear_transparent",
    )


def _build_flip_visor(ctx: ModuleBuildContext) -> ModuleBuild:
    model = ctx.model
    r: ResolvedAstronomyAstronautHelmetConfig = ctx.config  # type: ignore[assignment]
    s = r.s
    shell = model.get_part("shell")
    visor = model.part("visor")

    off = _visor_child_offset(r, r.hinge_z)
    _emit_visor_mesh(visor, _flip_frame_shape(r), "visor_frame", "frame_white", s, off)
    _emit_visor_mesh(visor, _visor_bubble_shape(r), "visor_bubble", "visor_amber", s, off)
    for i, side in enumerate((1.0, -1.0)):
        _emit_visor_mesh(visor, _visor_knob_shape(r, side), f"pivot_knob_{i}", "hub_gray", s, off)

    # Bubble extends along local +X; -Y makes positive q open the visor
    # (concentric flip-up on a sphere; forward-and-up lid on the brow hinge).
    model.articulation(
        "visor_pivot",
        ArticulationType.REVOLUTE,
        parent=shell,
        child=visor,
        origin=Origin(xyz=_visor_hinge_xyz(r)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=4.0, velocity=2.0, lower=0.0, upper=r.flip_range),
    )
    return ModuleBuild(
        module_name="flip_visor",
        parts_emitted=["visor"],
        internal_articulations=["visor_pivot"],
        interfaces={"downstream": _shell_downstream(r)},
    )


def _build_dual_flip_visor(ctx: ModuleBuildContext) -> ModuleBuild:
    model = ctx.model
    r: ResolvedAstronomyAstronautHelmetConfig = ctx.config  # type: ignore[assignment]
    s = r.s
    shell = model.get_part("shell")

    # Outer amber sun visor (same as flip).
    visor = model.part("visor")
    off = _visor_child_offset(r, r.hinge_z)
    _emit_visor_mesh(visor, _flip_frame_shape(r), "visor_frame", "frame_white", s, off)
    _emit_visor_mesh(visor, _visor_bubble_shape(r), "visor_bubble", "visor_amber", s, off)
    for i, side in enumerate((1.0, -1.0)):
        _emit_visor_mesh(visor, _visor_knob_shape(r, side), f"pivot_knob_{i}", "hub_gray", s, off)
    model.articulation(
        "visor_pivot", ArticulationType.REVOLUTE, parent=shell, child=visor,
        origin=Origin(xyz=_visor_hinge_xyz(r)), axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=4.0, velocity=2.0, lower=0.0, upper=r.flip_range),
    )

    # Inner clear pressure visor on its own independent hinge.
    inner = model.part("inner_visor")
    inner_off = _visor_child_offset(r, _inner_hinge_z(r))
    _emit_visor_mesh(inner, _inner_visor_frame_shape(r), "inner_visor_frame", "frame_white", s, inner_off)
    _emit_visor_mesh(inner, _inner_visor_lens_shape(r), "inner_visor_lens", "visor_clear", s, inner_off)
    model.articulation(
        "inner_visor_pivot", ArticulationType.REVOLUTE, parent=shell, child=inner,
        origin=Origin(xyz=_inner_visor_hinge_xyz(r)), axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=3.0, velocity=2.0, lower=0.0, upper=min(1.22, r.flip_range)),
    )

    return ModuleBuild(
        module_name="dual_flip_visor",
        parts_emitted=["visor", "inner_visor"],
        internal_articulations=["visor_pivot", "inner_visor_pivot"],
        interfaces={"downstream": _shell_downstream(r)},
    )


# --------------------------------------------------------------------------- #
# Slot C — neck_base (parallel child at the shell base)
# --------------------------------------------------------------------------- #


def _collar_shape(rib_count: int) -> cq.Shape:
    """Stepped 2-tier neck ring with N rib notches (origin S1 / collar_ribs S2)."""
    collar = _z_cylinder(0.112, -0.160, -0.100)
    collar = collar.fuse(_z_cylinder(0.118, -0.160, -0.140))
    collar = collar.cut(_z_cylinder(0.095, -0.165, -0.095))
    for i in range(rib_count):
        ang = 2.0 * math.pi * i / rib_count
        collar = collar.cut(
            _box(0.016, 0.016, 0.030, (0.114, 0.0, -0.118)).rotate(
                cq.Vector(0, 0, 0), cq.Vector(0, 0, 1.0), math.degrees(ang)
            )
        )
    return collar


def _build_fused_collar(ctx: ModuleBuildContext) -> ModuleBuild:
    """Collar fused into the shell as a static visual (no part, no joint; Rule 1)."""
    model = ctx.model
    r: ResolvedAstronomyAstronautHelmetConfig = ctx.config  # type: ignore[assignment]
    shell = model.get_part("shell")
    _emit_shell_mesh(shell, _collar_shape(r.collar_rib_count), "neck_collar", "helmet_white", r.s)
    return ModuleBuild(
        module_name="fused_collar",
        parts_emitted=[],
        interfaces={"downstream": _shell_downstream(r)},
    )


def _build_twist_lock_ring(ctx: ModuleBuildContext) -> ModuleBuild:
    """Collar as a separate bayonet locking ring on a REVOLUTE(Z) joint (twist S9)."""
    model = ctx.model
    r: ResolvedAstronomyAstronautHelmetConfig = ctx.config  # type: ignore[assignment]
    s = r.s
    shell = model.get_part("shell")

    bayonet_z = (CENTER_Z + NECK_CUT_Z) * s  # world z of the shell cut plane
    ring = model.part("locking_ring")
    ring.visual(
        mesh_from_cadquery(_scaled(_collar_shape(r.collar_rib_count), s), "locking_ring_body"),
        origin=Origin(xyz=(0.0, 0.0, -NECK_CUT_Z * s)),
        material="helmet_white",
        name="locking_ring_body", material_class_id="metal.paint_coated",
    )
    model.articulation(
        "shell_to_ring",
        ArticulationType.REVOLUTE,
        parent=shell,
        child=ring,
        origin=Origin(xyz=(0.0, 0.0, bayonet_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=6.0, velocity=1.5, lower=0.0, upper=r.bayonet_range),
    )
    return ModuleBuild(
        module_name="twist_lock_ring",
        parts_emitted=["locking_ring"],
        internal_articulations=["shell_to_ring"],
        interfaces={"downstream": _shell_downstream(r)},
    )


# --------------------------------------------------------------------------- #
# Factory registries + assembly
# --------------------------------------------------------------------------- #

VISOR_FACTORIES = {
    "flip_visor": _build_flip_visor,
    "dual_flip_visor": _build_dual_flip_visor,
}
NECK_FACTORIES = {
    "fused_collar": _build_fused_collar,
    "twist_lock_ring": _build_twist_lock_ring,
}


def _slots_for_config(r: ResolvedAstronomyAstronautHelmetConfig) -> list[SlotSpec]:
    return [
        SlotSpec(slot_name="shell", candidates={r.shell_form: _build_shell}, anchor_choice=r.shell_form),
        SlotSpec(
            slot_name="visor",
            candidates={r.visor_module: VISOR_FACTORIES[r.visor_module]},
            anchor_choice=r.visor_module,
        ),
        SlotSpec(
            slot_name="neck_base",
            candidates={r.neck_module: NECK_FACTORIES[r.neck_module]},
            anchor_choice=r.neck_module,
        ),
    ]


def build_astronomy_astronaut_helmet(
    config: AstronomyAstronautHelmetConfig,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name="astronomy_astronaut_helmet", assets=assets)
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


def build_seeded_astronomy_astronaut_helmet(seed: int) -> ArticulatedObject:
    return build_astronomy_astronaut_helmet(config_from_seed(seed))


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    r = resolve_config(config_from_seed(seed))
    return [
        ("shell", r.shell_form),
        ("visor", r.visor_module),
        ("neck_base", r.neck_module),
        ("collar_rib_count", f"ribs_{r.collar_rib_count}"),
        ("eva_port_count", f"ports_{r.eva_port_count}"),
    ]


# --------------------------------------------------------------------------- #
# Author-layer QC
# --------------------------------------------------------------------------- #


def _declare_overlaps(ctx: TestContext, model: ArticulatedObject, r: ResolvedAstronomyAstronautHelmetConfig) -> None:
    parts = {p.name for p in model.parts}
    shell = model.get_part("shell")

    # Shell front-region surface elements the movable visor cap rides over. The
    # visor frame/bubble sit ~2-5 mm proud of these surfaces and ride over them
    # across the flip arc (concentric surface-riding contact) — the same
    # captured-hinge exception every 5-star source declares.
    ride_elems = ["shell_body", "interior_lip"]

    visor = model.get_part("visor") if "visor" in parts else None
    if visor is not None:
        shell_visnames = {v.name for v in shell.visuals}
        for shell_elem in ride_elems:
            if shell_elem not in shell_visnames:
                continue
            for visor_elem in ("visor_frame", "visor_bubble"):
                ctx.allow_overlap(
                    shell, visor, elem_a=shell_elem, elem_b=visor_elem,
                    reason="Movable visor cap seats/rides on the shell front surface "
                    "(pivot disks mount here; the thin cap sits a few mm "
                    "proud and rides over the surface across its travel).")

    # Fishbowl: decals on the shell sit inside the dome clearance (visible through it).
    if r.shell_form == "fishbowl" and visor is not None:
        decals = [f"nasa_logo_letter_{i}" for i in range(4)] + [
            "flag_decal_base", "flag_decal_canton", "flag_decal_stripe_0",
            "flag_decal_stripe_1", "flag_decal_stripe_2",
        ]
        for d in decals:
            ctx.allow_overlap(shell, visor, elem_a=d, elem_b="visor_bubble",
                              reason="Decal on the shell sits inside the fishbowl dome clearance; visible through the visor.")

    # Dual nested visors: inner clear visor seats on the shell and nests
    # concentrically inside the outer amber visor (LEVA pair).
    if r.visor_module == "dual_flip_visor" and "inner_visor" in parts and visor is not None:
        inner = model.get_part("inner_visor")
        shell_visnames = {v.name for v in shell.visuals}
        for shell_elem in ("shell_body", "interior_lip"):
            if shell_elem not in shell_visnames:
                continue
            for inner_elem in ("inner_visor_frame", "inner_visor_lens"):
                ctx.allow_overlap(shell, inner, elem_a=shell_elem, elem_b=inner_elem,
                                  reason="Inner visor arms/lens seat on and ride the shell front surface (concentric cap on its own hinge).")
        for i_elem in ("inner_visor_frame", "inner_visor_lens"):
            for o_elem in ("visor_frame", "visor_bubble"):
                ctx.allow_overlap(inner, visor, elem_a=i_elem, elem_b=o_elem,
                                  reason="Inner and outer visors are concentric spherical-shell bands on the same pivot line (LEVA nesting; ~1-2 mm radial gap).")

    # Twist bayonet: locking ring rides the neck-seat ring bearing and its upper
    # tier engages the shell cut plane.
    if r.neck_module == "twist_lock_ring" and "locking_ring" in parts:
        ring = model.get_part("locking_ring")
        for shell_elem in ("shell_body", "neck_seat"):
            ctx.allow_overlap(shell, ring, elem_a=shell_elem, elem_b="locking_ring_body",
                              reason="Locking ring rotates on the neck-seat ring bearing; its upper tier engages the shell cut plane as the bayonet twist-lock lug.")


def _visor_opened(ctx, rest, opened, hinge: str) -> tuple[bool, str]:
    """Did the visor actually clear the face aperture?

    Centre pivot (sphere shells): the cap rides concentrically onto the crown,
    so the defining signature is a rise in Z.
    Brow hinge (cyl_barrel): the visor is a lid rotating about the top edge of
    the bezel, so it swings FORWARD and up. Requiring a Z rise would encode the
    wrong mechanism, so assert its real signature instead — a large total
    displacement AND forward travel along +X.
    """
    if rest is None or opened is None:
        return False, "missing aabb"
    if hinge == "brow":
        moved = _center_dist(rest, opened)
        forward = opened[1][0] - rest[1][0]
        return (moved > 0.05 and forward > 0.05), f"moved={moved:.4f} forward={forward:.4f}"
    return (opened[1][2] > rest[1][2] + 0.02), f"rise={opened[1][2] - rest[1][2]:.4f}"


def _center_dist(a, b) -> float:
    if a is None or b is None:
        return 0.0
    ca = [(a[0][i] + a[1][i]) / 2.0 for i in range(3)]
    cb = [(b[0][i] + b[1][i]) / 2.0 for i in range(3)]
    return math.dist(ca, cb)


def _expect_visor(ctx, model, r) -> None:
    visor = model.get_part("visor")
    bubble = visor.get_visual("visor_bubble")
    ctx.check("visor bubble present", bubble is not None)

    # amber visor is transparent glass (alpha < 0.9).
    amber = next(m for m in model.materials if m.name == "visor_amber")
    ctx.check("visor bubble is transparent", amber.rgba is not None and amber.rgba[3] < 0.9,
              details=f"visor_amber rgba={amber.rgba}")

    pivot = model.get_articulation("visor_pivot")
    ctx.check("visor pivot is revolute", pivot.articulation_type == ArticulationType.REVOLUTE,
              details=str(pivot.articulation_type))
    rest = ctx.part_element_world_aabb(visor, elem="visor_bubble")
    with ctx.pose({pivot: r.flip_range}):
        opened = ctx.part_element_world_aabb(visor, elem="visor_bubble")
    ok, why = _visor_opened(ctx, rest, opened, r.visor_hinge)
    ctx.check("visor opens clear of the face aperture", ok,
              details=f"hinge={r.visor_hinge}, {why}, rest={rest}, opened={opened}")

    if r.visor_module == "dual_flip_visor":
        inner = model.get_part("inner_visor")
        inner_pivot = model.get_articulation("inner_visor_pivot")
        ctx.check("inner visor has its own revolute", inner_pivot is not pivot
                  and inner_pivot.articulation_type == ArticulationType.REVOLUTE)
        i_rest = ctx.part_element_world_aabb(inner, elem="inner_visor_lens")
        # inner opens independently while outer stays closed
        with ctx.pose({inner_pivot: min(1.1, r.flip_range), pivot: 0.0}):
            i_open = ctx.part_element_world_aabb(inner, elem="inner_visor_lens")
        ok, why = _visor_opened(ctx, i_rest, i_open, r.visor_hinge)
        ctx.check("inner visor flips independently", ok,
                  details=f"hinge={r.visor_hinge}, {why}, rest={i_rest}, open={i_open}")


def _expect_neck(ctx, model, r) -> None:
    if r.neck_module == "twist_lock_ring":
        ring = model.get_part("locking_ring")
        bayonet = model.get_articulation("shell_to_ring")
        ctx.check("bayonet joint is revolute", bayonet.articulation_type == ArticulationType.REVOLUTE,
                  details=str(bayonet.articulation_type))
        # rotation about Z: azimuth changes, height (z) stays put.
        p_lock = ctx.part_world_aabb(ring)
        with ctx.pose({bayonet: r.bayonet_range}):
            p_turn = ctx.part_world_aabb(ring)
        z_stable = (p_lock is not None and p_turn is not None
                    and abs(p_lock[0][2] - p_turn[0][2]) < 0.01)
        ctx.check("bayonet rotates the ring about Z (height stable)", z_stable,
                  details=f"lock={p_lock}, turn={p_turn}")
    else:
        collar = model.get_part("shell").get_visual("neck_collar")
        ctx.check("fused neck collar present", collar is not None)

    # Neck ring rests on the ground plane (lowest part bottom ~ 0).
    lowest = min(
        (ctx.part_world_aabb(p)[0][2] for p in model.parts if ctx.part_world_aabb(p) is not None),
        default=None,
    )
    ctx.check("neck ring sits on the ground", lowest is not None and abs(lowest) < 0.01,
              details=f"lowest z={lowest}")


def run_astronomy_astronaut_helmet_tests(
    model: ArticulatedObject,
    config: AstronomyAstronautHelmetConfig,
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

    _expect_visor(ctx, model, r)
    _expect_neck(ctx, model, r)

    # Rule 5: dynamic collision across sampled joint poses.
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=48, ignore_fixed=True)

    return ctx.report()


__all__ = [
    "AstronomyAstronautHelmetConfig",
    "ResolvedAstronomyAstronautHelmetConfig",
    "ShellForm",
    "VisorModule",
    "NeckModule",
    "HelmetPalette",
    "build_astronomy_astronaut_helmet",
    "build_seeded_astronomy_astronaut_helmet",
    "config_from_seed",
    "resolve_config",
    "run_astronomy_astronaut_helmet_tests",
    "slot_choices_for_seed",
]
