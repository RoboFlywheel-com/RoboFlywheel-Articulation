# SPDX-License-Identifier: Apache-2.0

"""Hair dryer — modular procedural template (Bathroom / Hair dryer).

Hand-held compact hair dryer: a barrel along +X (front/nozzle at +X, rear
intake at -X), a handle hanging down (-Z) with two PRISMATIC slide switches,
and a drooping power cord + plug. Three independent select-slots drive the
topology (36 combos):

  Slot A  nozzle_attachment   concentrator / diffuser / comb / wide_smoothing
                              — front outlet part, CONTINUOUS spin about +X.
  Slot B  handle_grip         pistol / folding / open_loop
                              — pistol/open_loop fuse the grip into `body`
                                (switches/cord parent to body, `body_to_*`);
                                folding splits the grip into a separate
                                `handle` part on a REVOLUTE hinge (axis -Y)
                                and reparents the switches/cord to it
                                (`handle_to_*`).
  Slot C  rear_intake_filter  radial_fixed_grille / twist_ring / hinged_lint
                              — fixed = body visual (no joint); twist = a
                                `rear_grille` part on a REVOLUTE +X bayonet;
                                hinged = a `lint_screen` part on a REVOLUTE +Y
                                flip hinge.

Every seed always has at least the nozzle CONTINUOUS joint + 2 switch
PRISMATIC joints, so a non-fixed articulation is guaranteed.

This is a parallel-children template (all slots parent to the single root
`body`), built with an explicit per-slot dispatch (the `_modular.assemble`
chain-joint helper is for serial chains; here the joint types/axes differ per
slot and the switches/cord reparent on Slot B, so the dispatch is explicit).

Source records (5-star), adapted per AUTHORING.md §A Rule 3
(loft/mesh primitives preserved, literals parameterised by scale):
  S1  core body + pistol + concentrator + fixed grille + switch + cord
      rec_pink-compact-hair-dryer-...-8f70ba30  model.py:L52-L212
  S3  diffuser_nozzle          rec_hair_dryer_var_diffuser_nozzle   L101-L235
  S4  comb_pick_nozzle         rec_hair_dryer_var_comb_nozzle       L91-L196
  S5  wide_smoothing_nozzle    rec_hair_dryer_var_wide_smoothing_nozzle L91-L206
  S7  folding_travel_handle    rec_hair_dryer_var_folding_handle    L80-L298
  S8  open_loop_grip           rec_hair_dryer_var_loop_grip_handle  L90-L231
  S10 twist_ring_filter        rec_hair_dryer_var_twist_rear_filter L91-L226
  S11 hinged_lint_screen       rec_hair_dryer_var_hinged_rear_filter L91-L203
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
    BoxGeometry,
    CapsuleGeometry,
    CylinderGeometry,
    Inertial,
    MatingContract,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    TorusGeometry,
    mesh_from_cadquery,
    mesh_from_geometry,
    tube_from_spline_points,
)

__modular__ = True

# --------------------------------------------------------------------------- #
# Slot enums / palette.
# --------------------------------------------------------------------------- #

NozzleAttachment = Literal["concentrator", "diffuser", "comb", "wide_smoothing"]
HandleGrip = Literal["pistol", "folding", "open_loop"]
RearIntakeFilter = Literal["radial_fixed_grille", "twist_ring", "hinged_lint_screen"]
PaletteStyle = Literal["salon_pink", "matte_black", "travel_white", "chrome_teal", "rose_gold"]

NOZZLE_ATTACHMENTS: tuple[NozzleAttachment, ...] = (
    "concentrator",
    "diffuser",
    "comb",
    "wide_smoothing",
)
HANDLE_GRIPS: tuple[HandleGrip, ...] = ("pistol", "folding", "open_loop")
REAR_INTAKE_FILTERS: tuple[RearIntakeFilter, ...] = (
    "radial_fixed_grille",
    "twist_ring",
    "hinged_lint_screen",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "salon_pink",
    "matte_black",
    "travel_white",
    "chrome_teal",
    "rose_gold",
)

# Weighted sampling (spec §拓扑多样性审计). Every value retains substantial
# probability so the 36-combo pool is exercised within 0-49.
_NOZZLE_WEIGHTS = (0.34, 0.22, 0.20, 0.24)
_GRIP_WEIGHTS = (0.50, 0.22, 0.28)
_REAR_WEIGHTS = (0.44, 0.30, 0.26)

# palette_style -> {shell, dark, switch} rgba.  shell = barrel + handle;
# dark = nozzle/grille/cord/plug accents; switch = the two slide nubs.
PALETTES: dict[str, dict[str, tuple[float, float, float, float]]] = {
    "salon_pink": {
        "shell": (0.96, 0.71, 0.78, 1.0),
        "dark": (0.24, 0.24, 0.26, 1.0),
        "switch": (0.32, 0.32, 0.34, 1.0),
    },
    "matte_black": {
        "shell": (0.13, 0.13, 0.14, 1.0),
        "dark": (0.05, 0.05, 0.06, 1.0),
        "switch": (0.40, 0.40, 0.42, 1.0),
    },
    "travel_white": {
        "shell": (0.94, 0.94, 0.95, 1.0),
        "dark": (0.20, 0.22, 0.26, 1.0),
        "switch": (0.55, 0.57, 0.60, 1.0),
    },
    "chrome_teal": {
        "shell": (0.10, 0.45, 0.46, 1.0),
        "dark": (0.78, 0.80, 0.83, 1.0),
        "switch": (0.20, 0.22, 0.24, 1.0),
    },
    "rose_gold": {
        "shell": (0.86, 0.62, 0.55, 1.0),
        "dark": (0.30, 0.28, 0.27, 1.0),
        "switch": (0.45, 0.42, 0.40, 1.0),
    },
}

# --------------------------------------------------------------------------- #
# Nominal geometry stations (pre-scale).  All from S1.
# --------------------------------------------------------------------------- #

BARREL_FRONT_X = 0.175
NOZZLE_MOUNT_X_NOM = 0.163  # nozzle back sleeve overlaps the barrel front lip
HINGE_X_NOM = 0.063  # folding hinge station along barrel underside
HINGE_Z_NOM = -0.041  # barrel bottom surface at the hinge


def _clamp(value: float, lo: float, hi: float) -> float:
    if lo > hi:
        lo, hi = hi, lo
    return max(lo, min(hi, float(value)))


def _pick(value, choices):
    return value if value in choices else choices[0]


# --------------------------------------------------------------------------- #
# Config.
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class HairDryerConfig:
    """Public configuration sampled by ``config_from_seed`` or supplied directly."""

    nozzle_attachment: NozzleAttachment = "concentrator"
    handle_grip: HandleGrip = "pistol"
    rear_intake_filter: RearIntakeFilter = "radial_fixed_grille"
    palette_style: PaletteStyle = "salon_pink"

    barrel_length_scale: float = 1.0
    barrel_radius_scale: float = 1.0
    handle_length_scale: float = 1.0

    n_fingers: int = 10  # diffuser only
    n_teeth: int = 11  # comb only
    n_ribs: int = 8  # twist grille only
    fold_upper: float = 1.5  # folding only
    twist_upper: float = 1.05  # twist only

    name: str = "reference_hair_dryer"


@dataclass(frozen=True)
class ResolvedHairDryerConfig:
    nozzle_attachment: NozzleAttachment
    handle_grip: HandleGrip
    rear_intake_filter: RearIntakeFilter
    palette_style: PaletteStyle

    barrel_length_scale: float
    barrel_radius_scale: float
    handle_length_scale: float

    n_fingers: int
    n_teeth: int
    n_ribs: int
    fold_upper: float
    twist_upper: float

    name: str
    palette: dict[str, tuple[float, float, float, float]]

    # derived
    nozzle_mount_x: float
    front_lip_r: float  # outer barrel radius at the front lip (scaled)
    nozzle_sleeve_r: float
    hinge_x: float
    hinge_z: float


def config_from_seed(seed: int) -> HairDryerConfig:
    """Deterministic per-seed sampling. ``seed=0`` is not special.

    Order per spec §7 sampling contract: independent main scales + conditional
    counts/limits first; nozzle_mount_x / sleeve_r are equation-derived and the
    seating inequality is projected back in ``resolve_config``.
    """
    rng = random.Random(seed)

    nozzle: NozzleAttachment = rng.choices(NOZZLE_ATTACHMENTS, weights=_NOZZLE_WEIGHTS, k=1)[0]
    grip: HandleGrip = rng.choices(HANDLE_GRIPS, weights=_GRIP_WEIGHTS, k=1)[0]
    rear: RearIntakeFilter = rng.choices(REAR_INTAKE_FILTERS, weights=_REAR_WEIGHTS, k=1)[0]
    palette: PaletteStyle = rng.choice(PALETTE_STYLES)

    barrel_length_scale = round(rng.uniform(0.90, 1.12), 4)
    barrel_radius_scale = round(rng.uniform(0.92, 1.08), 4)
    handle_length_scale = round(rng.uniform(0.90, 1.15), 4)

    n_fingers = rng.randint(8, 12)
    n_teeth = rng.randint(9, 13)
    n_ribs = rng.randint(6, 10)
    fold_upper = round(rng.uniform(1.2, 1.6), 4)
    twist_upper = round(rng.uniform(0.9, 1.2), 4)

    return HairDryerConfig(
        nozzle_attachment=nozzle,
        handle_grip=grip,
        rear_intake_filter=rear,
        palette_style=palette,
        barrel_length_scale=barrel_length_scale,
        barrel_radius_scale=barrel_radius_scale,
        handle_length_scale=handle_length_scale,
        n_fingers=n_fingers,
        n_teeth=n_teeth,
        n_ribs=n_ribs,
        fold_upper=fold_upper,
        twist_upper=twist_upper,
        name=f"seeded_hair_dryer_{seed}",
    )


def resolve_config(config: HairDryerConfig) -> ResolvedHairDryerConfig:
    if config.palette_style not in PALETTES:
        raise ValueError(f"Unsupported palette_style: {config.palette_style}")

    nozzle = _pick(config.nozzle_attachment, NOZZLE_ATTACHMENTS)
    grip = _pick(config.handle_grip, HANDLE_GRIPS)
    rear = _pick(config.rear_intake_filter, REAR_INTAKE_FILTERS)

    bls = _clamp(config.barrel_length_scale, 0.90, 1.12)
    brs = _clamp(config.barrel_radius_scale, 0.92, 1.08)
    hls = _clamp(config.handle_length_scale, 0.90, 1.15)

    n_fingers = int(_clamp(config.n_fingers, 8, 12))
    n_teeth = int(_clamp(config.n_teeth, 9, 13))
    n_ribs = int(_clamp(config.n_ribs, 6, 10))
    fold_upper = _clamp(config.fold_upper, 1.2, 1.6)
    twist_upper = _clamp(config.twist_upper, 0.9, 1.2)

    # equation: front lip radius (nominal 0.030) and rear-sleeve radius scale
    # with barrel_radius_scale; the nozzle back sleeve must seat over the lip.
    front_lip_r = 0.030 * brs
    nozzle_sleeve_r = front_lip_r + 0.003

    # equation: nozzle mount station scales with barrel length, front lip at
    # 0.175*bls.  inequality (spec §参数范围): the back sleeve must overlap the
    # front lip by >= 0.006 in X, i.e. mount_x in [front-0.018, front-0.006].
    front_lip_x = BARREL_FRONT_X * bls
    nozzle_mount_x = NOZZLE_MOUNT_X_NOM * bls
    lo = front_lip_x - 0.018
    hi = front_lip_x - 0.006
    nozzle_mount_x = _clamp(nozzle_mount_x, lo, hi)

    hinge_x = HINGE_X_NOM * bls
    hinge_z = HINGE_Z_NOM  # barrel underside; radius scale handled in builder

    return ResolvedHairDryerConfig(
        nozzle_attachment=nozzle,
        handle_grip=grip,
        rear_intake_filter=rear,
        palette_style=config.palette_style,
        barrel_length_scale=bls,
        barrel_radius_scale=brs,
        handle_length_scale=hls,
        n_fingers=n_fingers,
        n_teeth=n_teeth,
        n_ribs=n_ribs,
        fold_upper=fold_upper,
        twist_upper=twist_upper,
        name=config.name,
        palette=dict(PALETTES[config.palette_style]),
        nozzle_mount_x=nozzle_mount_x,
        front_lip_r=front_lip_r,
        nozzle_sleeve_r=nozzle_sleeve_r,
        hinge_x=hinge_x,
        hinge_z=hinge_z,
    )


# --------------------------------------------------------------------------- #
# Shared loft helper (S1 _loft, verbatim) + scaled section builders.
# --------------------------------------------------------------------------- #


def _loft(sections) -> cq.Workplane:
    """Loft along +X through YZ-plane sections.

    sections: list of ("circle", x, r) or ("rect", x, w, h).  Verbatim from
    every 5-star source's `_loft`.
    """
    wp = cq.Workplane("YZ")
    prev = 0.0
    for i, s in enumerate(sections):
        x = s[1]
        off = x if i == 0 else x - prev
        if i > 0 or abs(off) > 1e-12:
            wp = wp.workplane(offset=off)
        if s[0] == "circle":
            wp = wp.circle(s[2])
        else:
            wp = wp.rect(s[2], s[3])
        prev = x
    return wp.loft(ruled=False)


def _barrel_solid(r: ResolvedHairDryerConfig) -> cq.Workplane:
    """Hollow barrel housing (S1 _barrel_solid). X stations scale with barrel
    length, radii with barrel radius."""
    bl = r.barrel_length_scale
    br = r.barrel_radius_scale
    outer = _loft(
        [
            ("circle", 0.0, 0.037 * br),
            ("circle", 0.030 * bl, 0.042 * br),
            ("circle", 0.100 * bl, 0.040 * br),
            ("circle", 0.150 * bl, 0.033 * br),
            ("circle", 0.175 * bl, 0.030 * br),
        ]
    )
    inner = _loft(
        [
            ("circle", -0.006 * bl, 0.034 * br),
            ("circle", 0.030 * bl, 0.039 * br),
            ("circle", 0.100 * bl, 0.037 * br),
            ("circle", 0.150 * bl, 0.030 * br),
            ("circle", 0.181 * bl, 0.027 * br),
        ]
    )
    return outer.cut(inner)


def _pistol_handle_solid(r: ResolvedHairDryerConfig) -> cq.Workplane:
    """Tapered pistol handle (S1 _handle_solid).  -Z height scales with
    handle_length_scale; hinge/handle x station scales with barrel length."""
    hl = r.handle_length_scale
    return (
        cq.Workplane("XY")
        .center(r.hinge_x, 0.0)
        .rect(0.050, 0.030)
        .workplane(offset=-0.055 * hl)
        .rect(0.046, 0.030)
        .workplane(offset=-0.060 * hl)
        .rect(0.040, 0.032)
        .loft(ruled=False)
    )


def _open_loop_handle_solid(r: ResolvedHairDryerConfig) -> cq.Workplane:
    """Open-loop grip frame with oval hand cutout (S8 _handle_solid)."""
    hl = r.handle_length_scale
    cx = r.hinge_x
    outer = (
        cq.Workplane("XY")
        .center(cx, 0.0)
        .rect(0.056, 0.038)
        .workplane(offset=-0.025 * hl)
        .rect(0.052, 0.044)
        .workplane(offset=-0.045 * hl)
        .rect(0.050, 0.046)
        .workplane(offset=-0.045 * hl)
        .rect(0.044, 0.036)
        .loft(ruled=False)
    )
    cutout = (
        cq.Workplane("XZ")
        .center(cx, -0.072 * hl)
        .ellipse(0.014, 0.022 * hl)
        .extrude(0.060, both=True)
    )
    return outer.cut(cutout)


def _front_mount_hub_geom(r: ResolvedHairDryerConfig):
    """Central front nozzle-mount post + 3 radial support spokes (a spider).

    On the barrel axis at the nozzle-mount station; spokes reach the barrel
    inner wall so the post is connected to the shell and the on-axis spin joint
    origin lands on solid geometry. Built in a local frame centered at x=0 and
    translated to nozzle_mount_x by the caller's visual origin... but the joint
    origin is in the BODY frame, so we build it already at nozzle_mount_x.
    """
    cx = r.nozzle_mount_x
    hub_r = 0.009
    # Central post: the axisymmetric spin bearing the nozzle clips onto. Extended
    # forward (+X) so it still overlaps the recessed wall-spokes below.
    hub_len = 0.030
    hub = CylinderGeometry(hub_r, hub_len, radial_segments=20).rotate_y(math.pi / 2.0)
    hub.translate(cx + 0.002, 0.0, 0.0)  # spans ~[cx-0.013, cx+0.017]
    # Barrel inner radius near the mount station (inner loft ~0.028 * brs here).
    wall_r = 0.028 * r.barrel_radius_scale
    spoke_len = wall_r - hub_r + 0.004  # +0.004 so it embeds into the wall
    spoke_mid = hub_r + spoke_len / 2.0 - 0.002
    # The 3 wall spokes are the only NON-axisymmetric static feature in the
    # nozzle's spin path. Recess them deep into the barrel (+X) so they sit
    # axially BEHIND the spinning nozzle back-spider band (which reaches only to
    # ~cx+0.004); the nozzle then spins past a clear annulus and only its central
    # bore rubs the post (an axisymmetric bearing). Thinner in X to keep the gap.
    SPOKE_DX = 0.012  # axial recess: spoke band ~[cx+0.008, cx+0.016]
    for i in range(3):
        angle = i * 2.0 * math.pi / 3.0
        spoke = BoxGeometry((0.008, spoke_len, 0.003))
        spoke.translate(0.0, spoke_mid, 0.0)
        spoke.rotate_x(angle)
        spoke.translate(cx + SPOKE_DX, 0.0, 0.0)
        hub.merge(spoke)
    return hub


def _rear_center_hub_geom(r: ResolvedHairDryerConfig):
    """Central rear intake post + 3-spoke spider at x=-0.003 (twist bearing)."""
    cx = -0.003
    hub_r = 0.006
    hub = CylinderGeometry(hub_r, 0.016, radial_segments=18).rotate_y(math.pi / 2.0)
    hub.translate(cx, 0.0, 0.0)
    wall_r = 0.030 * r.barrel_radius_scale  # barrel inner radius at the rear bore
    spoke_len = wall_r - hub_r + 0.004
    spoke_mid = hub_r + spoke_len / 2.0 - 0.002
    for i in range(3):
        angle = i * 2.0 * math.pi / 3.0
        spoke = BoxGeometry((0.010, spoke_len, 0.003))
        spoke.translate(0.0, spoke_mid, 0.0)
        spoke.rotate_x(angle)
        spoke.translate(cx, 0.0, 0.0)
        hub.merge(spoke)
    return hub


def _rear_filter_geom(r: ResolvedHairDryerConfig):
    """Fixed rear intake cap + 3 concentric torus ribs (S1 / radial_fixed_grille)."""
    br = r.barrel_radius_scale
    cap = CylinderGeometry(0.037 * br, 0.012, radial_segments=48).rotate_y(math.pi / 2.0)
    cap.translate(-0.004, 0.0, 0.0)
    for rr in (0.014, 0.022, 0.030):
        ring = TorusGeometry(rr * br, 0.0016, radial_segments=10, tubular_segments=40).rotate_y(
            math.pi / 2.0
        )
        ring.translate(-0.011, 0.0, 0.0)
        cap.merge(ring)
    return cap


# --------------------------------------------------------------------------- #
# Slot A nozzle meshes (one helper per candidate; primitives preserved).
# --------------------------------------------------------------------------- #


def _nozzle_back_mount_cq(r: ResolvedHairDryerConfig) -> cq.Workplane:
    """Central nozzle-mount post + back spider disc as a single cadquery solid.

    Unioned into each nozzle shell so the whole nozzle is one watertight solid:
    the central post crosses the part-frame origin (x=0) — giving the on-axis
    CONTINUOUS spin joint solid geometry — and the back disc reaches the shell
    back rim so the union is connected for every candidate. Three radial gaps in
    the disc keep the back airflow readable rather than a sealed plate.
    """
    sr = r.nozzle_sleeve_r
    # Central post on the axis, long enough to overlap the shell bore.
    post = (
        cq.Workplane("YZ").workplane(offset=-0.014).circle(0.0090).extrude(0.030)
    )
    # Back ring straddling the shell back wall (radius ~sr) so the boolean union
    # fuses cleanly into the shell. Kept thin radially and just at the back so it
    # never dominates the outlet AABB (the spin-reorientation test reads the
    # flat outlet, which must stay the widest feature).
    ring = (
        cq.Workplane("YZ")
        .workplane(offset=-0.008)
        .circle(sr + 0.002)
        .circle(sr - 0.008)
        .extrude(0.012)
    )
    mount = post.union(ring)
    # Three radial spokes bridging post → ring (boxes along Y, rotated about X).
    for i in range(3):
        ang = i * 2.0 * math.pi / 3.0
        spoke = (
            cq.Workplane("XY")
            .rect(0.011, 2.0 * (sr + 0.001))
            .extrude(0.005)
            .rotate((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), math.degrees(ang))
            .translate((-0.002, 0.0, 0.0))
        )
        mount = mount.union(spoke)
    return mount


def _concentrator_mesh(r: ResolvedHairDryerConfig):
    """Round back -> wide thin slot, hollow (S1/S2 _nozzle_mesh).  Back rim
    radius scales with barrel radius so it keeps seating over the front lip."""
    sr = r.nozzle_sleeve_r
    outer = _loft(
        [
            ("circle", 0.0, sr),
            ("rect", 0.028, 0.070, 0.030),
            ("rect", 0.052, 0.082, 0.013),
        ]
    )
    inner = _loft(
        [
            ("circle", -0.006, sr - 0.003),
            ("rect", 0.028, 0.064, 0.024),
            ("rect", 0.058, 0.078, 0.008),
        ]
    )
    shell = outer.cut(inner).union(_nozzle_back_mount_cq(r))
    return mesh_from_cadquery(shell, "nozzle_shell")


# Diffuser geometry constants (S3).
_BOWL_R = 0.056
_FACE_X = 0.027
_FACE_THICKNESS = 0.003
_FINGER_RING_R = 0.036
_FINGER_R = 0.004
_FINGER_LEN = 0.014


def _diffuser_bowl_solid(r: ResolvedHairDryerConfig) -> cq.Workplane:
    """Bowl shell with perforated face plate (S3 _diffuser_bowl_solid)."""
    sr = r.nozzle_sleeve_r
    outer = _loft(
        [
            ("circle", -0.010, sr + 0.001),
            ("circle", 0.004, sr + 0.002),
            ("circle", 0.018, 0.050),
            ("circle", 0.030, _BOWL_R),
        ]
    )
    inner = _loft(
        [
            ("circle", -0.016, sr - 0.002),
            ("circle", 0.004, sr - 0.002),
            ("circle", 0.018, 0.044),
            ("circle", 0.035, _BOWL_R - 0.006),
        ]
    )
    shell = outer.cut(inner)

    face = (
        cq.Workplane("YZ")
        .workplane(offset=_FACE_X)
        .circle(_BOWL_R - 0.003)
        .extrude(_FACE_THICKNESS)
    )
    hole_points_inner = [
        (0.020 * math.cos(2 * math.pi * i / 6), 0.020 * math.sin(2 * math.pi * i / 6))
        for i in range(6)
    ]
    hole_points_outer = [
        (0.042 * math.cos(2 * math.pi * i / 8 + 0.2), 0.042 * math.sin(2 * math.pi * i / 8 + 0.2))
        for i in range(8)
    ]
    hole_cutters = (
        cq.Workplane("YZ")
        .workplane(offset=_FACE_X - 0.005)
        .pushPoints(hole_points_inner + hole_points_outer)
        .circle(0.004)
        .extrude(_FACE_THICKNESS + 0.010)
    )
    center_hole = (
        cq.Workplane("YZ")
        .workplane(offset=_FACE_X - 0.005)
        .circle(0.007)
        .extrude(_FACE_THICKNESS + 0.010)
    )
    face = face.cut(hole_cutters).cut(center_hole)
    return shell.union(face).union(_nozzle_back_mount_cq(r))


def _finger_mesh(name: str):
    """Single capsule finger extending +X from origin (S3 _finger_mesh)."""
    finger = CapsuleGeometry(_FINGER_R, _FINGER_LEN, radial_segments=12, height_segments=4)
    finger.rotate_y(-math.pi / 2.0)
    half_span = _FINGER_LEN / 2.0 + _FINGER_R
    finger.translate(_FACE_X + _FACE_THICKNESS + half_span - 0.003, 0.0, 0.0)
    return finger


def _comb_nozzle_body(r: ResolvedHairDryerConfig):
    """Short round collar -> narrow slit duct (S4 _comb_nozzle_body)."""
    sr = r.nozzle_sleeve_r
    outer = _loft(
        [
            ("circle", 0.0, sr - 0.001),
            ("circle", 0.010, sr - 0.003),
            ("rect", 0.025, 0.052, 0.024),
            ("rect", 0.050, 0.046, 0.016),
        ]
    )
    inner = _loft(
        [
            ("circle", -0.006, sr - 0.005),
            ("circle", 0.010, sr - 0.007),
            ("rect", 0.025, 0.044, 0.017),
            ("rect", 0.056, 0.038, 0.010),
        ]
    )
    shell = outer.cut(inner).union(_nozzle_back_mount_cq(r))
    return mesh_from_cadquery(shell, "nozzle_shell")


def _comb_lip_rail():
    """Low rectangular rail under the slit (S4 _comb_lip_rail).

    Raised so its top overlaps the comb duct outlet bottom (z≈-0.008), keeping
    the rail+teeth connected to the duct (no float island).
    """
    rail = (
        cq.Workplane("XY")
        .box(0.018, 0.050, 0.010, centered=(True, True, True))
        .translate((0.043, 0.0, -0.010))
    )
    return mesh_from_cadquery(rail, "comb_lip_rail")


def _tooth_geom():
    """Single comb tooth: short straight cylindrical peg, -Z (S4 _make_tooth)."""
    tooth = CylinderGeometry(0.0018, 0.020, radial_segments=10)
    tooth.translate(0.0, 0.0, -0.010)
    return tooth


def _wide_nozzle_mesh(r: ResolvedHairDryerConfig):
    """Round collar -> broad flat slit (S5 _nozzle_mesh)."""
    sr = r.nozzle_sleeve_r
    noz_len = 0.052
    outlet_w = 0.104
    outlet_h = 0.018
    wall = 0.004
    outer = _loft(
        [
            ("circle", 0.0, sr - 0.001),
            ("circle", 0.010, sr - 0.003),
            ("rect", 0.028, 0.080, 0.030),
            ("rect", noz_len, outlet_w, outlet_h + 2.0 * wall),
        ]
    )
    inner = _loft(
        [
            ("circle", -0.006, sr - 0.005),
            ("circle", 0.010, sr - 0.007),
            ("rect", 0.028, 0.072, 0.022),
            ("rect", noz_len + 0.006, outlet_w - 2.0 * wall, outlet_h),
        ]
    )
    shell = outer.cut(inner).union(_nozzle_back_mount_cq(r))
    return mesh_from_cadquery(shell, "nozzle_shell")


def _wide_slit_lip_mesh():
    """Four shallow bars framing the wide slit (S5 _slit_lip_mesh)."""
    noz_len = 0.052
    outlet_w = 0.104
    outlet_h = 0.018
    wall = 0.004
    lip_depth = 0.006
    half_w = outlet_w / 2.0
    half_h = outlet_h / 2.0
    lip_x = noz_len - lip_depth / 2.0
    top = (
        cq.Workplane("XY")
        .box(lip_depth, outlet_w + 0.006, wall, centered=(True, True, True))
        .translate((lip_x, 0.0, half_h + wall / 2.0))
    )
    bottom = (
        cq.Workplane("XY")
        .box(lip_depth, outlet_w + 0.006, wall, centered=(True, True, True))
        .translate((lip_x, 0.0, -half_h - wall / 2.0))
    )
    left = (
        cq.Workplane("XY")
        .box(lip_depth, wall, outlet_h + 2.0 * wall, centered=(True, True, True))
        .translate((lip_x, -half_w - wall / 2.0, 0.0))
    )
    right = (
        cq.Workplane("XY")
        .box(lip_depth, wall, outlet_h + 2.0 * wall, centered=(True, True, True))
        .translate((lip_x, half_w + wall / 2.0, 0.0))
    )
    lip = top.union(bottom).union(left).union(right)
    lip = lip.edges().fillet(0.0015)
    return mesh_from_cadquery(lip, "slit_lip")


# --------------------------------------------------------------------------- #
# Slot C twist/hinged geometry.
# --------------------------------------------------------------------------- #


def _bayonet_ring_cq(r: ResolvedHairDryerConfig) -> cq.Workplane:
    """Annular bayonet receiver ring at the barrel rear (S10, body-mounted).

    Extruded forward (+X, length 0.012) so its inner bore wall is present at the
    recessed grille disc's axial station (~body x 0.005). The spinning grille's
    contact collar rides just inside this bore (an axisymmetric journal bearing),
    so the grille keeps its bayonet contact without any feature poking back past
    the rear rim. Placed at visual origin -0.006 -> body x in [-0.006, +0.006].
    """
    br = r.barrel_radius_scale
    return cq.Workplane("YZ").circle(0.038 * br).circle(0.031 * br).extrude(0.012)


def _grille_mesh(r: ResolvedHairDryerConfig):
    """Twist intake grille: twist ring + hub + n ribs + axisymmetric collar (S10).

    The spinning bladed disc (torus + ribs + hub) is RECESSED inward (+X) into
    the barrel bore by ``DISC_X`` so it sits staggered behind the rear rim
    instead of flush in the rim plane (which read as a穿模 z-fight against the
    barrel / bayonet collar). Its bayonet contact is provided by a single
    AXISYMMETRIC contact collar that rides just inside the (forward-extruded)
    bayonet receiver ring's bore — a journal bearing. This replaces the old 3
    discrete standoff tabs, which were non-axisymmetric and poked back past the
    rear rim, so they swept through the ring / rear cap on every revolution
    (穿模). Radial features scale with barrel_radius so the bore clearance ratio
    is preserved across seeds.
    """
    br = r.barrel_radius_scale
    DISC_X = 0.008  # recess of the bladed disc plane into the bore (+X)

    grille = TorusGeometry(0.029 * br, 0.0025, radial_segments=10, tubular_segments=40)
    grille.rotate_y(math.pi / 2.0)
    grille.translate(DISC_X, 0.0, 0.0)

    # Center hub elongated along X so it spans from the recessed disc back to the
    # central rear-intake post (the twist bearing) for a real seated contact.
    # Front-biased so its back face stays at body x ~ -0.004 — INSIDE the rear
    # rim plane (~-0.006): no rotating feature pokes out the back of the dryer.
    hub = CylinderGeometry(0.006, 0.016, radial_segments=16)
    hub.rotate_y(math.pi / 2.0)
    hub.translate(DISC_X - 0.001, 0.0, 0.0)
    grille.merge(hub)

    rib_inner = 0.004
    rib_outer = 0.029 * br
    rib_len = rib_outer - rib_inner
    rib_mid = (rib_inner + rib_outer) / 2.0
    for i in range(r.n_ribs):
        angle = i * 2.0 * math.pi / r.n_ribs
        rib = BoxGeometry((0.0025, rib_len, 0.002))
        rib.translate(0.0, rib_mid, 0.0)
        rib.rotate_x(angle)
        rib.translate(DISC_X, 0.0, 0.0)
        grille.merge(rib)

    # Axisymmetric contact collar: a continuous ring seated in the disc plane
    # whose outer reach (~ring_inner + 0.001 across the radius-scale range) rides
    # just inside the bayonet receiver ring's forward-extruded bore. As a surface
    # of revolution it keeps the grille_disc<->bayonet_ring contact at EVERY spin
    # angle without sweeping into the ring or poking past the rear rim. Its inner
    # reach (~0.028*br) overlaps the disc torus/ribs so it merges into one solid.
    collar = TorusGeometry(0.030 * br, 0.002, radial_segments=12, tubular_segments=48)
    collar.rotate_y(math.pi / 2.0)
    collar.translate(DISC_X, 0.0, 0.0)
    grille.merge(collar)

    return mesh_from_geometry(grille, "grille_disc")


def _perforated_disc(r: ResolvedHairDryerConfig) -> cq.Workplane:
    """Hinged lint-screen disc, top edge at hinge origin (S11 _perforated_disc)."""
    R = 0.035 * r.barrel_radius_scale
    thickness = 0.003
    disc = cq.Workplane("YZ").center(0, -R).circle(R).extrude(thickness)
    disc = disc.translate((-thickness / 2, 0, 0))
    hole_pts = []
    for ring_r, count in [(0.010, 5), (0.018, 8), (0.026, 12)]:
        for i in range(count):
            angle = 2 * math.pi * i / count
            hole_pts.append((ring_r * math.cos(angle), ring_r * math.sin(angle)))
    disc = disc.faces(">X").workplane().pushPoints(hole_pts).hole(0.004)
    return disc


def _hinge_knuckle(y_offset: float, r: ResolvedHairDryerConfig):
    """Hinge knuckle cylinder at barrel rear top (S11 _hinge_knuckle)."""
    knuckle = CylinderGeometry(0.003, 0.008, radial_segments=16)
    knuckle.rotate_x(math.pi / 2.0)
    knuckle.translate(0.0, y_offset, 0.037 * r.barrel_radius_scale)
    return knuckle


# --------------------------------------------------------------------------- #
# Cord geometry (body-mounted and handle-local versions).
# --------------------------------------------------------------------------- #


def _cord_geom_local():
    """Drooping cable + strain relief + plug + pins in CORD-LOCAL frame (S1/S7).

    The cord part frame origin coincides with the FIXED-joint origin (the cord
    exit at the handle base). Built so local (0,0,0) is INSIDE the strain-relief
    sleeve: the sleeve straddles the origin (embeds +Z into the handle) and the
    cable droops -Z to the plug. This puts the joint origin on solid cord
    geometry and—because the joint origin is itself placed on the handle base in
    the body/handle frame—keeps the cord in real contact with the parent.
    """
    # Strain-relief sleeve straddling the origin (+Z embeds into the handle).
    relief = CylinderGeometry(0.0090, 0.040).translate(0.0, 0.0, 0.008)
    cord = relief
    cord_pts = [
        (0.0, 0.0, -0.012),
        (0.007, 0.0, -0.046),
        (-0.015, 0.0, -0.086),
        (-0.065, 0.0, -0.104),
        (-0.105, 0.0, -0.104),
        (-0.135, 0.0, -0.104),
    ]
    cable = tube_from_spline_points(
        cord_pts, radius=0.0042, samples_per_segment=16, radial_segments=14
    )
    cord.merge(cable)
    plug = BoxGeometry((0.040, 0.028, 0.022)).translate(-0.135, 0.0, -0.104)
    cord.merge(plug)
    for py in (-0.008, 0.008):
        pin = CylinderGeometry(0.0035, 0.020).rotate_y(math.pi / 2.0)
        pin.translate(-0.164, py, -0.104)
        cord.merge(pin)
    return cord


def _folding_handle_solid(r: ResolvedHairDryerConfig) -> cq.Workplane:
    """Folding handle in local frame: hinge at origin, grip extends -Z, with
    integrated hinge ear (S7 _handle_solid)."""
    hl = r.handle_length_scale
    grip = (
        cq.Workplane("XY")
        .rect(0.050, 0.032)
        .workplane(offset=-0.015 * hl)
        .rect(0.048, 0.030)
        .workplane(offset=-0.030 * hl)
        .rect(0.046, 0.030)
        .workplane(offset=-0.035 * hl)
        .rect(0.040, 0.032)
        .loft(ruled=False)
    )
    ear = cq.Workplane("XZ").circle(0.009).extrude(0.018, both=True)
    return grip.union(ear)


# --------------------------------------------------------------------------- #
# Inertials.
# --------------------------------------------------------------------------- #


def _body_inertial(r: ResolvedHairDryerConfig) -> Inertial:
    return Inertial.from_geometry(
        Box((0.20 * r.barrel_length_scale, 0.085, 0.085)),
        mass=0.45,
        origin=Origin(xyz=(0.085 * r.barrel_length_scale, 0.0, 0.0)),
    )


# --------------------------------------------------------------------------- #
# Slot B: switch + cord wiring (parent is body or handle).
# --------------------------------------------------------------------------- #

# face-plate outer-Y for the switch nub seating.  pistol/folding's narrow
# handle puts the housing close in (center 0.0145, outer 0.017); the open_loop
# frame is wider in Y so its shelf must sit further out (center 0.021, outer
# 0.023) to keep the nub hardware clear of the frame wall (spec §备注 / S8).
_SWITCH_HOUSING_DEPTH = 0.005
_NARROW_HOUSING_Y_CENTER = 0.0145
_NARROW_MOUNT_Y = _NARROW_HOUSING_Y_CENTER + _SWITCH_HOUSING_DEPTH / 2.0  # 0.017
_LOOP_HOUSING_Y_CENTER = 0.021
_LOOP_MOUNT_Y = _LOOP_HOUSING_Y_CENTER + _SWITCH_HOUSING_DEPTH / 2.0  # 0.0235
_SWITCH_NUB_HALF_Y = 0.0035  # nub 0.007 deep
_SWITCH_NUB = (0.013, 0.007, 0.011)

# Switch z-stations on the body-fused grips. The barrel reaches down to
# z ≈ -0.045 (outer radius), so the switches sit clearly below it on the
# handle's front face to avoid burying the nubs in the barrel shell.
_BODY_SWITCH_ZS = (-0.058, -0.080)
_BODY_HOUSING_Z_CENTER = -0.069
_BODY_HOUSING_Z_SPAN = 0.060  # housing tall enough to underlie both switches


def _add_switches(
    model: ArticulatedObject,
    *,
    parent,
    prefix: str,
    mount_x: float,
    mount_y: float,
    z_positions: tuple[float, float],
    switch_mat,
) -> list[str]:
    """Emit the two slide switches as PRISMATIC children of ``parent``.

    The nub inner (-Y) face is flush with the housing outer face: joint origin
    sits at the housing outer Y, and the nub is offset +Y by its half-depth.
    """
    names = []
    for idx, sz in enumerate(z_positions):
        name = f"{prefix}_switch_{idx}"
        sw = model.part(name)
        sw.visual(
            Box(_SWITCH_NUB),
            origin=Origin(xyz=(0.0, _SWITCH_NUB_HALF_Y, 0.0)),
            material=switch_mat,
            name=f"{name}_nub", material_class_id="tech.control_interface",
        )
        sw.inertial = Inertial.from_geometry(Box(_SWITCH_NUB), mass=0.003)
        model.articulation(
            f"{parent.name}_to_{name}",
            ArticulationType.PRISMATIC,
            parent=parent,
            child=sw,
            origin=Origin(xyz=(mount_x, mount_y, sz)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=2.0, velocity=0.1, lower=-0.007, upper=0.007),
        )
        names.append(name)
    return names


# --------------------------------------------------------------------------- #
# Top-level build.
# --------------------------------------------------------------------------- #


def build_hair_dryer(
    config: HairDryerConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    config = config or HairDryerConfig()
    r = resolve_config(config)
    if assets is None:
        assets = AssetContext(Path(tempfile.mkdtemp(prefix="articraft-hair-dryer-")))
    model = ArticulatedObject(name=r.name, assets=assets)
    model.meta["slot_choices"] = [list(t) for t in slot_choices_for_config(r)]

    shell = model.material(f"hd_shell_{r.palette_style}", rgba=r.palette["shell"])
    dark = model.material(f"hd_dark_{r.palette_style}", rgba=r.palette["dark"])
    switch_mat = model.material(f"hd_switch_{r.palette_style}", rgba=r.palette["switch"])

    body = model.part("body")
    body.inertial = _body_inertial(r)

    # ---- Root body shell: barrel + (fused handle unless folding) ---------- #
    folding = r.handle_grip == "folding"
    if folding:
        # Barrel-only shell; the grip is a separate hinged part.
        body.visual(
            mesh_from_cadquery(_barrel_solid(r), "barrel_shell"),
            material=shell,
            name="body_shell", material_class_id="plastic.opaque_glossy_molded",
        )
    elif r.handle_grip == "open_loop":
        fused = _barrel_solid(r).union(_open_loop_handle_solid(r))
        body.visual(mesh_from_cadquery(fused, "body_shell"), material=shell, name="body_shell", material_class_id="plastic.opaque_glossy_molded")
    else:  # pistol
        fused = _barrel_solid(r).union(_pistol_handle_solid(r))
        body.visual(mesh_from_cadquery(fused, "body_shell"), material=shell, name="body_shell", material_class_id="plastic.opaque_glossy_molded")

    # Central front mount hub + 3-spoke spider: a solid post on the barrel axis
    # at the nozzle-mount station, held to the barrel inner wall by three thin
    # radial spokes (a real hair-dryer central nozzle post). The nozzles clip
    # onto this post, it gives the on-axis CONTINUOUS spin origin solid parent
    # geometry, and the spider keeps it connected to the body (no float island).
    body.visual(
        mesh_from_geometry(_front_mount_hub_geom(r), "front_mount_hub"),
        material=dark,
        name="front_mount_hub", material_class_id="plastic.opaque_glossy_molded",
    )

    # ---- Slot C rear-mount visuals on the body --------------------------- #
    _build_rear_mount_visuals(model, body, r, dark)

    # ---- Slot B switch mount visual on the body / handle ----------------- #
    # pistol/open_loop carry the switch housing/shelf on the body; folding's
    # housing rides on the handle part (added in _build_folding_handle).
    if r.handle_grip == "pistol":
        body.visual(
            Box((0.032, _SWITCH_HOUSING_DEPTH, _BODY_HOUSING_Z_SPAN)),
            origin=Origin(
                xyz=(0.060 * r.barrel_length_scale, _NARROW_HOUSING_Y_CENTER, _BODY_HOUSING_Z_CENTER)
            ),
            material=dark,
            name="switch_housing", material_class_id="plastic.opaque_glossy_molded",
        )
    elif r.handle_grip == "open_loop":
        body.visual(
            Box((0.032, _SWITCH_HOUSING_DEPTH, _BODY_HOUSING_Z_SPAN)),
            origin=Origin(
                xyz=(0.060 * r.barrel_length_scale, _LOOP_HOUSING_Y_CENTER, _BODY_HOUSING_Z_CENTER)
            ),
            material=dark,
            name="switch_shelf", material_class_id="plastic.opaque_glossy_molded",
        )

    # ---- Slot A nozzle ---------------------------------------------------- #
    _build_nozzle(model, body, r, dark)

    # ---- Slot C separate part (twist rear_grille / hinged lint_screen) --- #
    _build_rear_filter_part(model, body, r, dark)

    # ---- Slot B handle + switches + cord --------------------------------- #
    if folding:
        _build_folding_handle(model, body, r, shell, dark, switch_mat)
    else:
        # pistol / open_loop: switches + cord parent to body.
        mount_x = 0.060 * r.barrel_length_scale
        mount_y = _LOOP_MOUNT_Y if r.handle_grip == "open_loop" else _NARROW_MOUNT_Y
        _add_switches(
            model,
            parent=body,
            prefix="body",
            mount_x=mount_x,
            mount_y=mount_y,
            z_positions=_BODY_SWITCH_ZS,
            switch_mat=switch_mat,
        )
        # FIXED joint origin on the handle base (real cord-exit hardware). The
        # cord geometry is authored in cord-local coords with the relief at
        # (0,0,0), so the joint origin sits on both the handle solid and the
        # cord — satisfying isolation + articulation-origin checks.
        handle_bottom_z = -0.115 * r.handle_length_scale
        cord_attach = (r.hinge_x, 0.0, handle_bottom_z + 0.012)
        power_cord = model.part("power_cord")
        power_cord.visual(
            mesh_from_geometry(_cord_geom_local(), "power_cord"),
            material=dark,
            name="cord_shell", material_class_id="rubber.smooth_plain",
        )
        power_cord.inertial = Inertial.from_geometry(Box((0.18, 0.03, 0.12)), mass=0.06)
        model.articulation(
            "body_to_cord",
            ArticulationType.FIXED,
            parent=body,
            child=power_cord,
            origin=Origin(xyz=cord_attach),
        )

    return model


def _build_rear_mount_visuals(model, body, r: ResolvedHairDryerConfig, dark) -> None:
    """Slot C body-side visuals.  fixed = cap+ribs; twist = bayonet ring;
    hinged = two knuckles.  The separate parts/joints are added later."""
    if r.rear_intake_filter == "radial_fixed_grille":
        body.visual(
            mesh_from_geometry(_rear_filter_geom(r), "rear_filter"),
            material=dark,
            name="rear_filter", material_class_id="plastic.patterned_textured",
        )
    elif r.rear_intake_filter == "twist_ring":
        body.visual(
            mesh_from_cadquery(_bayonet_ring_cq(r), "bayonet_ring"),
            origin=Origin(xyz=(-0.006, 0.0, 0.0)),
            material=dark,
            name="bayonet_ring", material_class_id="plastic.opaque_glossy_molded",
        )
        # Central rear intake post + spider on the rear axis: real central hub
        # the grille spins on, gives the on-axis REVOLUTE bayonet origin solid
        # parent geometry, and the spokes keep it connected to the barrel wall.
        body.visual(
            mesh_from_geometry(_rear_center_hub_geom(r), "rear_center_hub"),
            material=dark,
            name="rear_center_hub", material_class_id="plastic.opaque_glossy_molded",
        )
    else:  # hinged_lint_screen
        for i in range(2):
            dy = -0.010 + i * 0.020
            body.visual(
                mesh_from_geometry(_hinge_knuckle(dy, r), f"hinge_knuckle_{i}"),
                material=dark,
                name=f"hinge_knuckle_{i}", material_class_id="plastic.opaque_glossy_molded",
            )


def _build_nozzle(model, body, r: ResolvedHairDryerConfig, dark) -> None:
    """Slot A: front nozzle part + CONTINUOUS barrel_to_nozzle joint (+X)."""
    nozzle = model.part("nozzle")
    kind = r.nozzle_attachment

    # The central mount post + back spider is unioned INTO each nozzle shell
    # (see _nozzle_back_mount_cq) so the nozzle is one connected solid and the
    # on-axis CONTINUOUS spin joint origin lands on the post.

    if kind == "concentrator":
        nozzle.visual(_concentrator_mesh(r), material=dark, name="nozzle_shell", material_class_id="plastic.opaque_glossy_molded")
        nozzle.inertial = Inertial.from_geometry(
            Box((0.05, 0.082, 0.07)), mass=0.04, origin=Origin(xyz=(0.025, 0.0, 0.0))
        )
    elif kind == "diffuser":
        nozzle.visual(
            mesh_from_cadquery(_diffuser_bowl_solid(r), "diffuser_bowl"),
            material=dark,
            name="nozzle_shell", material_class_id="plastic.opaque_glossy_molded",
        )
        for i in range(r.n_fingers):
            angle = 2.0 * math.pi * i / r.n_fingers
            fy = _FINGER_RING_R * math.cos(angle)
            fz = _FINGER_RING_R * math.sin(angle)
            finger = _finger_mesh(f"finger_{i}")
            finger.translate(0.0, fy, fz)
            nozzle.visual(
                mesh_from_geometry(finger, f"finger_{i}"), material=dark, name=f"finger_{i}", material_class_id="plastic.opaque_glossy_molded"
            )
        nozzle.inertial = Inertial.from_geometry(
            Box((0.06, 0.112, 0.112)), mass=0.05, origin=Origin(xyz=(0.025, 0.0, 0.0))
        )
    elif kind == "comb":
        nozzle.visual(_comb_nozzle_body(r), material=dark, name="nozzle_shell", material_class_id="plastic.opaque_glossy_molded")
        nozzle.visual(_comb_lip_rail(), material=dark, name="comb_lip_rail", material_class_id="plastic.opaque_glossy_molded")
        tooth_geom = _tooth_geom()
        ty0, ty1 = -0.021, 0.021
        for i in range(r.n_teeth):
            t = i / (r.n_teeth - 1)
            ty = ty0 + t * (ty1 - ty0)
            nozzle.visual(
                mesh_from_geometry(tooth_geom.copy(), f"tooth_{i}"),
                origin=Origin(xyz=(0.043, ty, -0.012)),
                material=dark,
                name=f"tooth_{i}", material_class_id="plastic.opaque_glossy_molded",
            )
        nozzle.inertial = Inertial.from_geometry(
            Box((0.07, 0.05, 0.06)), mass=0.04, origin=Origin(xyz=(0.030, 0.0, -0.01))
        )
    else:  # wide_smoothing
        nozzle.visual(_wide_nozzle_mesh(r), material=dark, name="nozzle_shell", material_class_id="plastic.opaque_glossy_molded")
        nozzle.visual(_wide_slit_lip_mesh(), material=dark, name="slit_lip", material_class_id="plastic.opaque_glossy_molded")
        nozzle.inertial = Inertial.from_geometry(
            Box((0.065, 0.116, 0.026)), mass=0.045, origin=Origin(xyz=(0.032, 0.0, 0.0))
        )

    model.articulation(
        "barrel_to_nozzle",
        ArticulationType.CONTINUOUS,
        parent=body,
        child=nozzle,
        origin=Origin(xyz=(r.nozzle_mount_x, 0.0, 0.0)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=0.5, velocity=6.0),
    )


def _build_rear_filter_part(model, body, r: ResolvedHairDryerConfig, dark) -> None:
    """Slot C separate parts: twist rear_grille / hinged lint_screen."""
    if r.rear_intake_filter == "twist_ring":
        rear_grille = model.part("rear_grille")
        rear_grille.visual(
            _grille_mesh(r),
            origin=Origin(xyz=(-0.003, 0.0, 0.0)),
            material=dark,
            name="grille_disc", material_class_id="plastic.patterned_textured",
        )
        rear_grille.inertial = Inertial.from_geometry(
            Box((0.072, 0.072, 0.008)), mass=0.015, origin=Origin(xyz=(-0.003, 0.0, 0.0))
        )
        model.articulation(
            "body_to_rear_grille",
            ArticulationType.REVOLUTE,
            parent=body,
            child=rear_grille,
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=2.0, velocity=2.0, lower=0.0, upper=r.twist_upper),
        )
    elif r.rear_intake_filter == "hinged_lint_screen":
        lint_screen = model.part("lint_screen")
        lint_screen.visual(
            mesh_from_cadquery(_perforated_disc(r), "screen_disc"),
            material=dark,
            name="screen_disc", material_class_id="plastic.patterned_textured",
        )
        lint_screen.visual(
            Box((0.005, 0.010, 0.008)),
            origin=Origin(xyz=(0.0, 0.0, 0.001)),
            material=dark,
            name="hinge_tab", material_class_id="plastic.opaque_glossy_molded",
        )
        lint_screen.inertial = Inertial.from_geometry(
            Box((0.006, 0.072, 0.072)), mass=0.012, origin=Origin(xyz=(0.0, 0.0, -0.035 * r.barrel_radius_scale))
        )
        model.articulation(
            "body_to_lint_screen",
            ArticulationType.REVOLUTE,
            parent=body,
            child=lint_screen,
            origin=Origin(xyz=(0.0, 0.0, 0.037 * r.barrel_radius_scale)),
            axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(effort=2.0, velocity=2.0, lower=0.0, upper=1.5),
        )


def _build_folding_handle(model, body, r: ResolvedHairDryerConfig, shell, dark, switch_mat) -> None:
    """Slot B folding: separate handle part + REVOLUTE hinge, switches + cord
    reparented to the handle, body carries hinge_barrel + lock_tab visuals."""
    hinge_x = r.hinge_x
    hinge_z = HINGE_Z_NOM

    # Body-side hinge hardware.
    hinge_barrel = (
        cq.Workplane("XZ").center(hinge_x, hinge_z).circle(0.007).extrude(0.016, both=True)
    )
    body.visual(
        mesh_from_cadquery(hinge_barrel, "hinge_barrel"), material=dark, name="hinge_barrel", material_class_id="plastic.opaque_glossy_molded"
    )
    # Lock tab (locked-open detent) abutting the hinge barrel: overlap it in X
    # so the tab is connected to the body (no float island).
    body.visual(
        Box((0.014, 0.010, 0.006)),
        origin=Origin(xyz=(hinge_x - 0.010, 0.0, hinge_z)),
        material=dark,
        name="lock_tab", material_class_id="plastic.opaque_glossy_molded",
    )

    # Handle part (local frame: hinge at origin, grip extends -Z).
    handle = model.part("handle")
    handle.visual(
        mesh_from_cadquery(_folding_handle_solid(r), "handle_shell"),
        material=shell,
        name="handle_shell", material_class_id="plastic.opaque_glossy_molded",
    )
    handle.visual(
        Box((0.032, _SWITCH_HOUSING_DEPTH, 0.040)),
        origin=Origin(xyz=(-0.003, _NARROW_HOUSING_Y_CENTER, -0.040)),
        material=dark,
        name="switch_housing", material_class_id="plastic.opaque_glossy_molded",
    )
    handle.inertial = Inertial.from_geometry(
        Box((0.05, 0.036, 0.08)), mass=0.12, origin=Origin(xyz=(0.0, 0.0, -0.040))
    )

    model.articulation(
        "body_to_handle",
        ArticulationType.REVOLUTE,
        parent=body,
        child=handle,
        origin=Origin(xyz=(hinge_x, 0.0, hinge_z)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=5.0, velocity=2.0, lower=0.0, upper=r.fold_upper),
    )

    # Switches reparent to the handle.
    _add_switches(
        model,
        parent=handle,
        prefix="handle",
        mount_x=-0.003,
        mount_y=_NARROW_MOUNT_Y,
        z_positions=(-0.028, -0.052),
        switch_mat=switch_mat,
    )

    # Cord reparents (FIXED) to the handle. The folding handle bottom (local
    # frame) is at z=-0.080*hls; the joint origin sits on the handle base and
    # the cord-local relief embeds up into it.
    handle_bottom_z = -0.080 * r.handle_length_scale
    cord_attach = (-0.018, 0.0, handle_bottom_z + 0.012)
    power_cord = model.part("power_cord")
    power_cord.visual(
        mesh_from_geometry(_cord_geom_local(), "power_cord"),
        material=dark,
        name="cord_shell", material_class_id="rubber.smooth_plain",
    )
    power_cord.inertial = Inertial.from_geometry(Box((0.18, 0.03, 0.12)), mass=0.06)
    model.articulation(
        "handle_to_cord",
        ArticulationType.FIXED,
        parent=handle,
        child=power_cord,
        origin=Origin(xyz=cord_attach),
    )


def build_seeded_hair_dryer(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_hair_dryer(config_from_seed(seed), assets=assets)


# --------------------------------------------------------------------------- #
# Slot choices.
# --------------------------------------------------------------------------- #


def slot_choices_for_config(r: ResolvedHairDryerConfig) -> tuple[tuple[str, str], ...]:
    return (
        ("nozzle_attachment", r.nozzle_attachment),
        ("handle_grip", r.handle_grip),
        ("rear_intake_filter", r.rear_intake_filter),
        ("palette_style", r.palette_style),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(resolve_config(config_from_seed(seed)))


# Wire the Slot C separate part into the build *after* nozzle so it appears in
# a stable order; called at the end of build via monkey-extension.  (Kept as a
# distinct function for readability — invoked inside build_hair_dryer below.)


# --------------------------------------------------------------------------- #
# Tests.
# --------------------------------------------------------------------------- #


def _ext(aabb):
    mn, mx = aabb
    return (mx[0] - mn[0], mx[1] - mn[1], mx[2] - mn[2])


def _declare_overlap_allowances(ctx, model, r: ResolvedHairDryerConfig) -> None:
    body = model.get_part("body")
    nozzle = model.get_part("nozzle")

    # Nozzle back rim slips over the barrel front lip (captured). All nozzle
    # candidates expose their main shell as the visual "nozzle_shell".
    noz_elem = "nozzle_shell"
    ctx.allow_overlap(
        nozzle,
        body,
        elem_a=noz_elem,
        elem_b="body_shell",
        reason="Nozzle back rim is intentionally slipped over the barrel front lip.",
    )
    # The nozzle's integral back post/spider clips onto the body's central
    # front mount post (the spin bearing) and reaches into the barrel bore.
    ctx.allow_overlap(
        nozzle,
        body,
        elem_a="nozzle_shell",
        elem_b="front_mount_hub",
        reason="Nozzle back post + spider clip onto the central front mount post (spin bearing).",
    )

    if r.handle_grip == "folding":
        handle = model.get_part("handle")
        ctx.allow_overlap(
            body,
            handle,
            elem_a="hinge_barrel",
            elem_b="handle_shell",
            reason="Hinge barrel is intentionally nested inside the handle hinge ear.",
        )
        ctx.allow_overlap(
            body,
            handle,
            elem_a="body_shell",
            elem_b="handle_shell",
            reason="Handle hinge ear passes through the barrel bottom wall at the hinge.",
        )
        ctx.allow_overlap(
            body,
            handle,
            elem_a="lock_tab",
            elem_b="handle_shell",
            reason="Lock tab is the locked-open detent that catches the handle ear.",
        )
        cord = model.get_part("power_cord")
        ctx.allow_overlap(
            handle,
            cord,
            elem_a="handle_shell",
            elem_b="cord_shell",
            reason="Strain-relief sleeve and cord top intentionally enter the handle base.",
        )
    else:
        cord = model.get_part("power_cord")
        ctx.allow_overlap(
            body,
            cord,
            elem_a="body_shell",
            elem_b="cord_shell",
            reason="Strain-relief sleeve and cord top intentionally enter the handle base.",
        )

    if r.rear_intake_filter == "twist_ring":
        grille = model.get_part("rear_grille")
        ctx.allow_overlap(
            grille,
            body,
            elem_a="grille_disc",
            elem_b="bayonet_ring",
            reason="Grille contact collar rides just inside the receiver ring bore (axisymmetric journal bearing).",
        )
        ctx.allow_overlap(
            grille,
            body,
            elem_a="grille_disc",
            elem_b="rear_center_hub",
            reason="Grille center hub seats on the central intake post (the twist bearing).",
        )
    elif r.rear_intake_filter == "hinged_lint_screen":
        lint = model.get_part("lint_screen")
        for i in range(2):
            ctx.allow_overlap(
                body,
                lint,
                elem_a=f"hinge_knuckle_{i}",
                elem_b="hinge_tab",
                reason="Hinge knuckle and tab intentionally interleave at the pivot.",
            )


def run_hair_dryer_tests(object_model: ArticulatedObject, config: HairDryerConfig) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    _declare_overlap_allowances(ctx, object_model, r)

    body = object_model.get_part("body")
    nozzle = object_model.get_part("nozzle")
    spin = object_model.get_articulation("barrel_to_nozzle")
    part_names = {p.name for p in object_model.parts}

    # ---- Identity: nozzle CONTINUOUS spin + seated over the front lip ----- #
    ctx.check(
        "barrel_to_nozzle is CONTINUOUS about +X",
        spin.articulation_type == ArticulationType.CONTINUOUS and abs(spin.axis[0]) > 0.99,
        details=f"type={spin.articulation_type}, axis={spin.axis}",
    )
    ctx.expect_overlap(
        nozzle, body, axes="x", min_overlap=0.006, name="nozzle seated over barrel front"
    )
    noz_pos = ctx.part_world_position(nozzle)
    ctx.check(
        "nozzle mounted at the barrel front",
        noz_pos is not None and noz_pos[0] > 0.15 * r.barrel_length_scale,
        details=f"nozzle origin={noz_pos}",
    )

    # Spinning reorients the nozzle. Track a NON-axisymmetric reference element
    # (the flat slot shell / a comb tooth / a diffuser finger) so the central
    # axisymmetric mount hub doesn't wash out the asymmetry in the part AABB.
    if r.nozzle_attachment == "comb":
        # A comb tooth hangs down (-Z) at rest, swings to +Y after a quarter turn.
        rest = ctx.part_element_world_aabb(nozzle, elem="tooth_0")
        with ctx.pose({spin: math.pi / 2.0}):
            spun = ctx.part_element_world_aabb(nozzle, elem="tooth_0")
        rest_c = (0.5 * (rest[0][1] + rest[1][1]), 0.5 * (rest[0][2] + rest[1][2]))
        spun_c = (0.5 * (spun[0][1] + spun[1][1]), 0.5 * (spun[0][2] + spun[1][2]))
        ctx.check(
            "nozzle spin swings the comb teeth",
            abs(rest_c[0] - spun_c[0]) > 0.010 or abs(rest_c[1] - spun_c[1]) > 0.010,
            details=f"rest_yz={rest_c}, spun_yz={spun_c}",
        )
    elif r.nozzle_attachment != "diffuser":
        # concentrator / wide_smoothing: the broad flat outlet dominates the part
        # AABB; its wide axis swaps Y<->Z under a quarter turn.
        ext0 = _ext(ctx.part_world_aabb(nozzle))
        with ctx.pose({spin: math.pi / 2.0}):
            ext90 = _ext(ctx.part_world_aabb(nozzle))
        ctx.check(
            "nozzle spin reorients the outlet",
            abs(ext90[1] - ext0[1]) > 0.004 or abs(ext90[2] - ext0[2]) > 0.004,
            details=f"rest={ext0}, quarter={ext90}",
        )
    else:
        # Round bowl: a finger must move under rotation.
        f0 = nozzle.get_visual("finger_0")
        rest = ctx.part_element_world_aabb(nozzle, elem=f0)
        with ctx.pose({spin: math.pi}):
            spun = ctx.part_element_world_aabb(nozzle, elem=f0)
        ctx.check(
            "diffuser spin rotates finger_0",
            rest is not None
            and spun is not None
            and (abs(rest[0][1] - spun[0][1]) > 0.005 or abs(rest[0][2] - spun[0][2]) > 0.005),
            details=f"rest={rest[0][1:]}, spun={spun[0][1:]}",
        )

    # ---- Slot B: two PRISMATIC switches on the correct parent ------------- #
    if r.handle_grip == "folding":
        sw_parent_name = "handle"
        sw_prefix = "handle"
        ctx.check("folding handle is a separate part", "handle" in part_names, details=str(sorted(part_names)))
        hinge = object_model.get_articulation("body_to_handle")
        ctx.check(
            "body_to_handle is REVOLUTE about -Y, locked-open at 0",
            hinge.articulation_type == ArticulationType.REVOLUTE
            and abs(hinge.axis[1]) > 0.99
            and hinge.motion_limits is not None
            and abs(hinge.motion_limits.lower) < 1e-6,
            details=f"type={hinge.articulation_type}, axis={hinge.axis}, "
            f"lower={hinge.motion_limits.lower if hinge.motion_limits else None}",
        )
        # Handle hangs below barrel when deployed (q=0), folds up at upper.
        handle = object_model.get_part("handle")
        h_aabb0 = ctx.part_world_aabb(handle)
        b_aabb = ctx.part_world_aabb(body)
        ctx.check(
            "handle hangs below barrel when deployed",
            h_aabb0 is not None
            and b_aabb is not None
            and (h_aabb0[0][2] + h_aabb0[1][2]) / 2.0 < (b_aabb[0][2] + b_aabb[1][2]) / 2.0 - 0.02,
            details=f"handle_cz={(h_aabb0[0][2] + h_aabb0[1][2]) / 2.0:.4f}",
        )
        with ctx.pose({hinge: r.fold_upper}):
            h_aabb1 = ctx.part_world_aabb(handle)
        ctx.check(
            "handle rises at max fold",
            h_aabb1 is not None
            and (h_aabb1[0][2] + h_aabb1[1][2]) / 2.0
            > (h_aabb0[0][2] + h_aabb0[1][2]) / 2.0 + 0.02,
            details=f"rest_cz={(h_aabb0[0][2] + h_aabb0[1][2]) / 2.0:.4f}, "
            f"fold_cz={(h_aabb1[0][2] + h_aabb1[1][2]) / 2.0:.4f}",
        )
    else:
        sw_parent_name = "body"
        sw_prefix = "body"
        ctx.check(
            "no separate handle part for fused grips",
            "handle" not in part_names,
            details=str(sorted(part_names)),
        )

    sw_parent = object_model.get_part(sw_parent_name)
    sw0 = object_model.get_part(f"{sw_prefix}_switch_0")
    sw1 = object_model.get_part(f"{sw_prefix}_switch_1")
    sw0_joint = object_model.get_articulation(f"{sw_parent_name}_to_{sw_prefix}_switch_0")
    ctx.check(
        "switch joints are PRISMATIC about +X",
        sw0_joint.articulation_type == ArticulationType.PRISMATIC and abs(sw0_joint.axis[0]) > 0.99,
        details=f"type={sw0_joint.articulation_type}, axis={sw0_joint.axis}",
    )
    ctx.expect_contact(sw0, sw_parent, name="switch_0 rests on housing")
    ctx.expect_contact(sw1, sw_parent, name="switch_1 rests on housing")
    rest_x = ctx.part_world_position(sw0)[0]
    with ctx.pose({sw0_joint: 0.007}):
        slid_x = ctx.part_world_position(sw0)[0]
    ctx.check(
        "switch_0 slides forward",
        slid_x > rest_x + 0.004,
        details=f"rest_x={rest_x}, slid_x={slid_x}",
    )

    # ---- Slot C: rear filter behavior ------------------------------------ #
    if r.rear_intake_filter == "twist_ring":
        grille = object_model.get_part("rear_grille")
        gjoint = object_model.get_articulation("body_to_rear_grille")
        ctx.check(
            "body_to_rear_grille is REVOLUTE about +X",
            gjoint.articulation_type == ArticulationType.REVOLUTE and abs(gjoint.axis[0]) > 0.99,
            details=f"type={gjoint.articulation_type}, axis={gjoint.axis}",
        )
        ctx.expect_contact(
            grille, body, elem_a="grille_disc", elem_b="bayonet_ring",
            name="grille contacts bayonet ring",
        )
        gpos = ctx.part_world_position(grille)
        ctx.check(
            "grille mounted at barrel rear",
            gpos is not None and gpos[0] < 0.02,
            details=f"grille origin={gpos}",
        )
        # The rotating disc must stay IN FRONT of the rear rim plane (~-0.006) at
        # every spin angle. The old 3 bayonet standoff tabs poked back to ~-0.008
        # and swept through the rim / receiver ring (穿模); the axisymmetric
        # contact collar keeps both rim clearance and bayonet contact at any
        # angle. Spinning is about +X so min-x is angle-invariant, but sample the
        # twisted extreme too as a guard against future non-axisymmetric features.
        rim_x = -0.006
        for q in (0.0, r.twist_upper):
            with ctx.pose({"body_to_rear_grille": q}):
                gd = ctx.part_element_world_aabb(grille, elem="grille_disc")
            ctx.check(
                f"grille stays in front of the rear rim @q={q:.3f}",
                gd is not None and gd[0][0] >= rim_x - 1e-4,
                details=f"grille_disc min_x={None if gd is None else round(gd[0][0], 5)} rim_x={rim_x}",
            )
        with ctx.pose({"body_to_rear_grille": r.twist_upper}):
            ctx.expect_contact(
                grille, body, elem_a="grille_disc", elem_b="bayonet_ring",
                name="grille still contacts bayonet ring at full twist",
            )
    elif r.rear_intake_filter == "hinged_lint_screen":
        lint = object_model.get_part("lint_screen")
        hjoint = object_model.get_articulation("body_to_lint_screen")
        ctx.check(
            "body_to_lint_screen is REVOLUTE about +Y",
            hjoint.articulation_type == ArticulationType.REVOLUTE and abs(hjoint.axis[1]) > 0.99,
            details=f"type={hjoint.articulation_type}, axis={hjoint.axis}",
        )
        ctx.expect_contact(
            lint, body, elem_a="screen_disc", elem_b="body_shell",
            name="lint screen seated at barrel rear",
        )
        closed = ctx.part_world_aabb(lint)
        with ctx.pose({hjoint: 1.2}):
            opened = ctx.part_world_aabb(lint)
        ctx.check(
            "lint screen swings open away from rear",
            closed is not None and opened is not None and opened[0][0] < closed[0][0] - 0.015,
            details=f"closed_min_x={closed[0][0]:.4f}, open_min_x={opened[0][0]:.4f}",
        )
    else:
        ctx.check(
            "fixed grille has no rear part/joint",
            "rear_grille" not in part_names and "lint_screen" not in part_names,
            details=str(sorted(part_names)),
        )

    # Swept-motion sensor: sample every articulation through its range and flag
    # any parent/child overlap NOT covered by a declared allowance — i.e. a
    # rotating part (nozzle spin / twist grille) sweeping into the shell/cover.
    # Warn-level: the intended bearings/sleeves are allow_overlap'd, so this
    # surfaces穿模 regressions during sweep review rather than masking them.
    ctx.warn_if_articulation_overlaps()

    return ctx.report()


__all__ = [
    "NozzleAttachment",
    "HandleGrip",
    "RearIntakeFilter",
    "PaletteStyle",
    "HairDryerConfig",
    "ResolvedHairDryerConfig",
    "build_hair_dryer",
    "build_seeded_hair_dryer",
    "config_from_seed",
    "resolve_config",
    "slot_choices_for_seed",
    "run_hair_dryer_tests",
    "__modular__",
]
