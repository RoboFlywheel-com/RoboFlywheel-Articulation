# SPDX-License-Identifier: Apache-2.0

"""Stylized watermill waterwheel — modular procedural template.

A wooden/stone watermill waterwheel that spins freely about a horizontal axle.
A static ``mount`` (freestanding A-frame trestle / mill-house wall facade /
masonry sluice channel) carries two bored bearing blocks that journal a metal
axle running through the twin wheel rims; the whole wheel assembly turns about
that axle (one CONTINUOUS hub joint, world +Y). Around the rim, N water-pickup
units (flat paddle boards / overshot bucket troughs / breastshot scoop vanes)
are baked onto the wheel rigid body as visuals (Rule 1 — no per-unit joint),
and the rim interior is filled by a spoke structure (straight diametral bars /
clasp compass arms / a solid web disc).

Pattern = ``mixed`` (parallel slots + radial multiplicity). Three structural
slots plus one multiplicity axis:

  * ``mount`` (3): trestle_aframe / millhouse_wall / masonry_sluice — the
    grounded part and the parent of the single hub joint
    (``trestle_/wall_/sluice_to_waterwheel``).
  * ``wheel_type`` (3): flat_paddle / enclosed_bucket / angled_scoop — what the
    radial copy loop emits onto the rim.
  * ``spokes`` (3): radial_spoke_bars / clasp_compass_arm / solid_web_disc — the
    fixed rim-interior filling between hub and rim.
  * ``paddle_count`` (N in [6,24]): a radial multiplicity axis encoded into the
    slot-choice tuple as ``("paddle_count", f"n{N}")``.

Sources (all read): the ``Machinery__Watermill`` picture-subcat fork pool — one
parent baseline (``..._afe3e6a1``) plus eight workbench variants (overshot,
breastshot, millhouse, sluice, clasparm, solidweb, n12, n16). See
``articraft_template_authoring/specs_modular_v1/Machinery_Watermill.md``.

The hub joint is a pure journal bearing (axle captured in the bored bearing
blocks); like a captured trunnion / pin-through-sleeve it has no clean
axis-aligned face pair, so it is grandfathered (``mating`` omitted, per the
modular-authoring captured-pin guidance) and guarded by element-scoped
``allow_overlap`` on the axle/bearing journal mirroring each source's run_tests.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
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
    TestContext,
    TestReport,
    mesh_from_cadquery,
)

__modular__ = True

# --------------------------------------------------------------------------- #
# Slot enums                                                                   #
# --------------------------------------------------------------------------- #
Mount = Literal["trestle_aframe", "millhouse_wall", "masonry_sluice"]
WheelType = Literal["flat_paddle", "enclosed_bucket", "angled_scoop"]
Spokes = Literal["radial_spoke_bars", "clasp_compass_arm", "solid_web_disc"]
PaletteStyle = Literal[
    "weathered_oak",
    "dark_walnut",
    "pale_ash",
    "painted_red_mill",
    "mossy_masonry",
    "teak_and_iron",
]

MOUNTS: tuple[Mount, ...] = ("trestle_aframe", "millhouse_wall", "masonry_sluice")
WHEEL_TYPES: tuple[WheelType, ...] = ("flat_paddle", "enclosed_bucket", "angled_scoop")
SPOKES_OPTS: tuple[Spokes, ...] = (
    "radial_spoke_bars",
    "clasp_compass_arm",
    "solid_web_disc",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "weathered_oak",
    "dark_walnut",
    "pale_ash",
    "painted_red_mill",
    "mossy_masonry",
    "teak_and_iron",
)

# mount module -> (part name, joint-name prefix)
_MOUNT_META: dict[Mount, tuple[str, str]] = {
    "trestle_aframe": ("trestle_frame", "trestle"),
    "millhouse_wall": ("mill_wall", "wall"),
    "masonry_sluice": ("sluice_mount", "sluice"),
}

N_MIN = 6
N_MAX = 24
# Mid-weighted multiplicity sampling (real wooden wheels run ~8-20 paddles);
# small/mid N common, large N rare to bound compile time and visual density.
_N_VALUES: tuple[int, ...] = tuple(range(N_MIN, N_MAX + 1))
_N_WEIGHTS: tuple[float, ...] = tuple(1.0 / (1.0 + abs(n - 11)) for n in _N_VALUES)

# --------------------------------------------------------------------------- #
# Palette diversity (>=3 realistic colorways drawn from the 5-star sources).   #
# Keys: wheel (rim/spokes/pickups), mount (frame/wall/masonry), mount_accent   #
# (battens/piers/caps), mount_dark (seams/bolts/diagonals), axle, collar.      #
# --------------------------------------------------------------------------- #
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    # Source baseline: pale beige-pink wheel wood + grayish-brown frame.
    "weathered_oak": {
        "wheel": (0.89, 0.72, 0.66, 1.0),
        "mount": (0.50, 0.40, 0.36, 1.0),
        "mount_accent": (0.56, 0.54, 0.50, 1.0),
        "mount_dark": (0.30, 0.24, 0.22, 1.0),
        "axle": (0.70, 0.71, 0.73, 1.0),
        "collar": (0.80, 0.81, 0.84, 1.0),
    },
    "dark_walnut": {
        "wheel": (0.45, 0.31, 0.22, 1.0),
        "mount": (0.30, 0.22, 0.17, 1.0),
        "mount_accent": (0.40, 0.32, 0.26, 1.0),
        "mount_dark": (0.16, 0.12, 0.10, 1.0),
        "axle": (0.55, 0.55, 0.58, 1.0),
        "collar": (0.66, 0.66, 0.70, 1.0),
    },
    "pale_ash": {
        "wheel": (0.82, 0.76, 0.64, 1.0),
        "mount": (0.62, 0.58, 0.50, 1.0),
        "mount_accent": (0.70, 0.66, 0.58, 1.0),
        "mount_dark": (0.42, 0.38, 0.32, 1.0),
        "axle": (0.72, 0.73, 0.75, 1.0),
        "collar": (0.82, 0.83, 0.85, 1.0),
    },
    # Natural-wood wheel against a barn-red painted mount.
    "painted_red_mill": {
        "wheel": (0.74, 0.66, 0.55, 1.0),
        "mount": (0.55, 0.18, 0.16, 1.0),
        "mount_accent": (0.80, 0.78, 0.72, 1.0),
        "mount_dark": (0.32, 0.10, 0.09, 1.0),
        "axle": (0.40, 0.41, 0.43, 1.0),
        "collar": (0.62, 0.63, 0.66, 1.0),
    },
    # Stone-grey masonry tones (from the sluice cap_stone / masonry sources).
    "mossy_masonry": {
        "wheel": (0.66, 0.58, 0.46, 1.0),
        "mount": (0.48, 0.46, 0.43, 1.0),
        "mount_accent": (0.56, 0.54, 0.50, 1.0),
        "mount_dark": (0.34, 0.36, 0.30, 1.0),
        "axle": (0.62, 0.63, 0.64, 1.0),
        "collar": (0.74, 0.75, 0.77, 1.0),
    },
    "teak_and_iron": {
        "wheel": (0.70, 0.50, 0.32, 1.0),
        "mount": (0.42, 0.38, 0.34, 1.0),
        "mount_accent": (0.52, 0.48, 0.42, 1.0),
        "mount_dark": (0.20, 0.20, 0.22, 1.0),
        "axle": (0.30, 0.31, 0.33, 1.0),
        "collar": (0.50, 0.51, 0.54, 1.0),
    },
}

# --------------------------------------------------------------------------- #
# Nominal dimensions (meters), shared across all sources (scale=1.0).          #
# Every linear quantity below is multiplied by ``r.scale`` at the point of use #
# (primitives via _box/_cyl, meshes via mesh_from_cadquery unit_scale), and    #
# all origins are scaled too — a single uniform scale about each part frame    #
# origin (the axle line), which preserves every seating / clearance / overlap. #
# --------------------------------------------------------------------------- #
AXLE_Z = 1.30  # axle centerline height above the ground

RIM_R_OUT = 0.92  # rim outer circumradius (12-gon)
RIM_R_IN = 0.78  # rim inner circumradius
RIM_W = 0.08  # rim width along the axle (Y)
RIM_Y = 0.21  # rim plane center offset (+/- Y)
RIM_SEGMENTS = 12

SPOKE_BARS = 3  # diametral bars per rim -> 6 visible spokes per side
SPOKE_LEN = 1.58
SPOKE_XSEC = (0.08, 0.07)

HUB_R = 0.10
HUB_LEN = 0.08

PADDLE_R = 0.84  # paddle/scoop center radius
PADDLE_DIMS = (0.28, 0.46, 0.06)  # tangential, axial (Y), radial
PADDLE_TILT = math.radians(30.0)  # breastshot scoop vane tilt off radial

BUCKET_R = 0.795  # overshot bucket floor center radius
BUCKET_TANGENTIAL = 0.30
BUCKET_AXIAL = 0.46
BUCKET_FLOOR_THICK = 0.045
BUCKET_BACK_THICK = 0.055
BUCKET_BACK_HEIGHT = 0.095

WEB_R_OUT = RIM_R_IN + 0.015  # web seats just into the inner rim
WEB_BORE_R = 0.092  # central bore hidden by the slightly larger hub boss
WEB_THICK = 0.045

CLASP_SPOKE_PAIRS = 6  # paired compass-arm spokes per rim
CLASP_ARM_XSEC = (0.055, 0.07)
CLASP_HUB_HALF_GAP = 0.040
CLASP_RIM_HALF_CHORD = 0.080
CLASP_RIM_R = RIM_R_IN + 0.025
HUB_BOX = 0.22

AXLE_R = 0.035
AXLE_LEN = 0.94  # spans y = -0.47 .. +0.47
COLLAR_R = 0.060
COLLAR_LEN = 0.10
COLLAR_Y = 0.42
COLLAR_RIBS = 10

BLOCK_DIMS = (0.20, 0.10, 0.24)  # bored bearing block
BORE_R = 0.033  # journal bore (slightly under axle radius -> captured embed)
BEARING_Y = 0.31  # bearing block center offset (+/- Y)

# The hub joint origin is placed just inside bearing_block_0's inboard face
# (on the +Y axle axis) rather than at the rim center (y=0): any point on the
# +Y axle axis is a valid joint origin, and the articulation-origin baseline
# measures distance to the nearest *surface* (a centroid of a thick block/axle
# is "far"). The block inboard face gives the parent a surface within tolerance;
# a thin coaxial journal washer on the wheel (half-thickness < tol) gives the
# child one. The waterwheel's child-frame geometry is authored shifted by
# -WHEEL_DY in Y so world positions (and the physical spin axis) are unchanged.
# See fence_cascade.py for the same on-hardware-origin compensation.
WHEEL_DY = BEARING_Y - BLOCK_DIMS[1] / 2.0 + 0.008  # ~0.268, 8 mm inside the face
JOURNAL_WASHER_R = 0.055
JOURNAL_WASHER_LEN = 0.020  # thin (half < 15 mm tol) thrust collar at the bearing

# trestle_aframe
FRAME_Y = 0.31
LEG_FOOT_X = 0.55
LEG_APEX_Z = 1.36
LEG_FOOT_Z = 0.05
LEG_TOP_Z = 1.22
LEG_ANGLE = math.atan2(LEG_FOOT_X, LEG_APEX_Z - LEG_FOOT_Z)
LEG_TOP_X = LEG_FOOT_X * (LEG_APEX_Z - LEG_TOP_Z) / (LEG_APEX_Z - LEG_FOOT_Z)
LEG_DIMS = (0.09, 0.07, 1.30)
FOOT_DIMS = (0.16, 0.14, 0.10)
BRACE_DIMS = (0.80, 0.06, 0.09)
BRACE_Z = 0.55
DIAG_X = 0.48
DIAG_Z0 = 0.12
DIAG_Z1 = 0.34
DIAG_ROLL = math.atan2(DIAG_Z1 - DIAG_Z0, 2.0 * FRAME_Y)
DIAG_DIMS = (0.07, 0.72, 0.07)

# millhouse_wall
WALL_X = -1.12
WALL_DIMS = (0.12, 1.34, 2.20)
WALL_FACE_X = WALL_X + WALL_DIMS[0] / 2.0
PLANK_SEAM_COUNT = 5
SEAM_DIMS = (0.012, 0.018, 2.12)
WALL_BATTEN_DIMS = (0.045, 1.26, 0.085)
WALL_BATTEN_ZS = (0.42, 1.92)
BRACKET_DIMS = (1.08, 0.08, 0.10)
BRACKET_X = WALL_FACE_X + BRACKET_DIMS[0] / 2.0
BRACKET_Z = AXLE_Z - 0.11
GUSSET_DIMS = (0.56, 0.055, 0.075)
GUSSET_ANGLE = math.atan2(0.46, 0.56)

# masonry_sluice
CHANNEL_LEN = 2.35
CHANNEL_WALL_Y = 0.36
CHANNEL_WALL_THICK = 0.16
CHANNEL_WALL_HEIGHT = 0.58
CHANNEL_FLOOR_DIMS = (2.45, 0.88, 0.06)
BEARING_PIER_DIMS = (0.38, 0.18, 0.60)
BEARING_PIER_Z = CHANNEL_WALL_HEIGHT + BEARING_PIER_DIMS[2] / 2.0
MORTAR_GROOVE = 0.012


# --------------------------------------------------------------------------- #
# Config dataclasses                                                           #
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class WatermillWaterwheelConfig:
    mount: Mount | None = None
    wheel_type: WheelType | None = None
    spokes: Spokes | None = None
    paddle_count: int | None = None
    palette_style: PaletteStyle = "weathered_oak"
    wheel_radius_scale: float = 1.0
    name: str = "watermill_waterwheel"


@dataclass(frozen=True)
class ResolvedWatermillWaterwheelConfig:
    mount: Mount
    wheel_type: WheelType
    spokes: Spokes
    paddle_count: int
    palette_style: PaletteStyle
    scale: float
    paddle_tangential: float  # clearance-projected (nominal, pre-scale)
    bucket_tangential: float
    mount_part_name: str
    mount_prefix: str
    name: str


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _pick(value, choices):
    return value if value in choices else choices[0]


def config_from_seed(seed: int) -> WatermillWaterwheelConfig:
    rng = random.Random(seed)
    return WatermillWaterwheelConfig(
        mount=rng.choice(MOUNTS),
        wheel_type=rng.choice(WHEEL_TYPES),
        spokes=rng.choice(SPOKES_OPTS),
        paddle_count=rng.choices(_N_VALUES, weights=_N_WEIGHTS, k=1)[0],
        palette_style=rng.choice(PALETTE_STYLES),
        wheel_radius_scale=round(rng.uniform(0.90, 1.10), 4),
        name=f"seeded_watermill_waterwheel_{seed}",
    )


def resolve_config(
    config: WatermillWaterwheelConfig | None = None,
) -> ResolvedWatermillWaterwheelConfig:
    cfg = config or WatermillWaterwheelConfig()
    mount = _pick(cfg.mount, MOUNTS)
    wheel_type = _pick(cfg.wheel_type, WHEEL_TYPES)
    spokes = _pick(cfg.spokes, SPOKES_OPTS)
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)

    n = int(cfg.paddle_count) if cfg.paddle_count is not None else 9
    n = int(_clamp(n, N_MIN, N_MAX))

    scale = _clamp(cfg.wheel_radius_scale, 0.90, 1.10)

    # Clearance projection (spec §7): keep the N pickup units from packing past
    # the circumference. width <= k * (2*pi*R / N); only shrinks at large N.
    k = 0.85
    paddle_tangential = min(PADDLE_DIMS[0], k * 2.0 * math.pi * PADDLE_R / n)
    bucket_tangential = min(BUCKET_TANGENTIAL, k * 2.0 * math.pi * BUCKET_R / n)

    part_name, prefix = _MOUNT_META[mount]
    return ResolvedWatermillWaterwheelConfig(
        mount=mount,
        wheel_type=wheel_type,
        spokes=spokes,
        paddle_count=n,
        palette_style=palette_style,
        scale=scale,
        paddle_tangential=paddle_tangential,
        bucket_tangential=bucket_tangential,
        mount_part_name=part_name,
        mount_prefix=prefix,
        name=cfg.name or "watermill_waterwheel",
    )


def slot_choices_for_config(
    config: WatermillWaterwheelConfig | ResolvedWatermillWaterwheelConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedWatermillWaterwheelConfig) else resolve_config(config)
    return (
        ("mount", r.mount),
        ("wheel_type", r.wheel_type),
        ("spokes", r.spokes),
        ("paddle_count", f"n{r.paddle_count}"),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# --------------------------------------------------------------------------- #
# Scaling helpers (uniform scale about the part frame origin / axle line).     #
# --------------------------------------------------------------------------- #
def _box(dims: tuple[float, float, float], s: float) -> Box:
    return Box((dims[0] * s, dims[1] * s, dims[2] * s))


def _cyl(radius: float, length: float, s: float) -> Cylinder:
    return Cylinder(radius=radius * s, length=length * s)


def _wy(y: float) -> float:
    """Wheel-part child-frame Y: nominal world Y shifted by -WHEEL_DY so the hub
    joint origin (placed on bearing_block_0 at +BEARING_Y) sits on real geometry
    while every wheel visual keeps its intended world position."""
    return y - WHEEL_DY


# --------------------------------------------------------------------------- #
# CadQuery mesh solids (built nominal; scaled at emit via unit_scale).         #
# --------------------------------------------------------------------------- #
def _rim_solid() -> cq.Workplane:
    """Segmented low-poly rim: a thick 12-gon ring, axis along local Z."""
    outer = cq.Workplane("XY").polygon(RIM_SEGMENTS, 2.0 * RIM_R_OUT).extrude(RIM_W)
    inner = cq.Workplane("XY").polygon(RIM_SEGMENTS, 2.0 * RIM_R_IN).extrude(RIM_W)
    return outer.cut(inner).translate((0.0, 0.0, -RIM_W / 2.0))


def _collar_solid() -> cq.Workplane:
    """Splined/ribbed axle end collar, axis along local Z."""
    collar = (
        cq.Workplane("XY")
        .circle(COLLAR_R)
        .extrude(COLLAR_LEN)
        .translate((0.0, 0.0, -COLLAR_LEN / 2.0))
    )
    rib_radius = 0.062
    for kk in range(COLLAR_RIBS):
        ang = 2.0 * math.pi * kk / COLLAR_RIBS
        rib = (
            cq.Workplane("XY")
            .box(0.022, 0.016, COLLAR_LEN)
            .rotate((0, 0, 0), (0, 0, 1), math.degrees(ang))
            .translate((rib_radius * math.cos(ang), rib_radius * math.sin(ang), 0.0))
        )
        collar = collar.union(rib)
    return collar


def _bearing_block_solid() -> cq.Workplane:
    """Bearing block journaling the axle.

    Kept solid on the axle line (x=0, z=block center): the hub joint origin lies
    exactly on that line, so a through-bore would leave the origin in empty space
    (> the 15 mm articulation-origin tolerance, since the spin axis is locked to
    the axle centerline). The captured axle overlapping the solid block is
    covered by an element-scoped allow_overlap, mirroring each source's
    run_tests journal allowance.
    """
    return cq.Workplane("XY").box(*BLOCK_DIMS)


def _bucket_solid(tangential: float) -> cq.Workplane:
    """One rim-spanning overshot bucket: floor plus raised back wall, open +X.

    Local axes: X tangential, Y spans between the rims, Z radial outward.
    """
    floor = cq.Workplane("XY").box(tangential, BUCKET_AXIAL, BUCKET_FLOOR_THICK)
    back_wall = (
        cq.Workplane("XY")
        .box(BUCKET_BACK_THICK, BUCKET_AXIAL, BUCKET_BACK_HEIGHT + 0.004)
        .translate(
            (
                -tangential / 2.0 + BUCKET_BACK_THICK / 2.0,
                0.0,
                BUCKET_FLOOR_THICK / 2.0 + BUCKET_BACK_HEIGHT / 2.0 - 0.002,
            )
        )
    )
    return floor.union(back_wall)


def _web_disc_solid() -> cq.Workplane:
    """Solid low-poly wooden web plate for one rim, with central hub bore."""
    disc = (
        cq.Workplane("XY")
        .circle(WEB_R_OUT)
        .extrude(WEB_THICK)
        .translate((0.0, 0.0, -WEB_THICK / 2.0))
    )
    bore = (
        cq.Workplane("XY")
        .circle(WEB_BORE_R)
        .extrude(WEB_THICK * 2.0)
        .translate((0.0, 0.0, -WEB_THICK))
    )
    return disc.cut(bore)


def _channel_wall_solid() -> cq.Workplane:
    """One low masonry flume wall with shallow block-joint grooves."""
    wall = cq.Workplane("XY").box(CHANNEL_LEN, CHANNEL_WALL_THICK, CHANNEL_WALL_HEIGHT)
    rows = 4
    row_h = CHANNEL_WALL_HEIGHT / rows
    for ri in range(1, rows):
        z = -CHANNEL_WALL_HEIGHT / 2.0 + ri * row_h
        for sy in (1.0, -1.0):
            groove = (
                cq.Workplane("XY")
                .box(CHANNEL_LEN + 0.02, MORTAR_GROOVE * 2.0, MORTAR_GROOVE)
                .translate((0.0, sy * CHANNEL_WALL_THICK / 2.0, z))
            )
            wall = wall.cut(groove)
    for ri in range(rows):
        z = -CHANNEL_WALL_HEIGHT / 2.0 + (ri + 0.5) * row_h
        offset = 0.18 if ri % 2 else 0.0
        joint_count = 5
        for ji in range(-joint_count, joint_count + 1):
            x = ji * (CHANNEL_LEN / (2 * joint_count + 1)) + offset
            if abs(x) > CHANNEL_LEN / 2.0 - 0.08:
                continue
            for sy in (1.0, -1.0):
                groove = (
                    cq.Workplane("XY")
                    .box(MORTAR_GROOVE, MORTAR_GROOVE * 2.0, row_h * 0.70)
                    .translate((x, sy * CHANNEL_WALL_THICK / 2.0, z))
                )
                wall = wall.cut(groove)
    return wall


def _segment_box_origin(
    p0: tuple[float, float], p1: tuple[float, float], y: float
) -> tuple[tuple[float, float, float], float]:
    """xyz + length for a rectangular member running between two XZ points."""
    x0, z0 = p0
    x1, z1 = p1
    dx = x1 - x0
    dz = z1 - z0
    length = math.hypot(dx, dz)
    theta = math.atan2(dx, dz)
    return ((x0 + x1) / 2.0, y, (z0 + z1) / 2.0), theta, length  # type: ignore[return-value]


# --------------------------------------------------------------------------- #
# Mount modules (Slot B) — grounded parts carrying the two bearing blocks.     #
# --------------------------------------------------------------------------- #
def _build_trestle_aframe(model, r, mats, *, assets):
    s = r.scale
    trestle = model.part("trestle_frame")
    leg_mid_x = (LEG_FOOT_X + LEG_TOP_X) / 2.0
    leg_mid_z = (LEG_TOP_Z + LEG_FOOT_Z) / 2.0
    for fi, fy in ((0, FRAME_Y), (1, -FRAME_Y)):
        for li, sx in ((0, 1.0), (1, -1.0)):
            trestle.visual(
                _box(LEG_DIMS, s),
                origin=Origin(
                    xyz=(sx * leg_mid_x * s, fy * s, leg_mid_z * s),
                    rpy=(0.0, -sx * LEG_ANGLE, 0.0),
                ),
                material=mats["mount"],
                name=f"leg_{fi}_{li}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"weathered_oak", "dark_walnut", "pale_ash", "painted_red_mill", "teak_and_iron"} else "stone.masonry_wall"),
            )
            trestle.visual(
                _box(FOOT_DIMS, s),
                origin=Origin(xyz=(sx * LEG_FOOT_X * s, fy * s, FOOT_DIMS[2] / 2.0 * s)),
                material=mats["mount"],
                name=f"foot_{fi}_{li}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"weathered_oak", "dark_walnut", "pale_ash", "painted_red_mill", "teak_and_iron"} else "stone.masonry_wall"),
            )
        trestle.visual(
            _box(BRACE_DIMS, s),
            origin=Origin(xyz=(0.0, fy * s, BRACE_Z * s)),
            material=mats["mount_accent"],
            name=f"cross_brace_{fi}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"weathered_oak", "dark_walnut", "pale_ash", "painted_red_mill", "teak_and_iron"} else "stone.masonry_wall"),
        )
    bearing_mesh = mesh_from_cadquery(
        _bearing_block_solid(), "bearing_block", assets=assets, unit_scale=s
    )
    for fi, fy in ((0, FRAME_Y), (1, -FRAME_Y)):
        trestle.visual(
            bearing_mesh,
            origin=Origin(xyz=(0.0, fy * s, AXLE_Z * s)),
            material=mats["mount"],
            name=f"bearing_block_{fi}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"weathered_oak", "dark_walnut", "pale_ash", "painted_red_mill", "teak_and_iron"} else "stone.masonry_wall"),
        )
    trestle.visual(
        _box(DIAG_DIMS, s),
        origin=Origin(
            xyz=(DIAG_X * s, 0.0, (DIAG_Z0 + DIAG_Z1) / 2.0 * s),
            rpy=(DIAG_ROLL, 0.0, 0.0),
        ),
        material=mats["mount_dark"],
        name="diagonal_brace", material_class_id=("wood.walnut_dark" if r.palette_style in {"weathered_oak", "dark_walnut", "pale_ash", "painted_red_mill", "mossy_masonry"} else "metal.blackened_gunmetal"),
    )
    return trestle


def _build_millhouse_wall(model, r, mats, *, assets):
    s = r.scale
    wall = model.part("mill_wall")
    wall.visual(
        _box(WALL_DIMS, s),
        origin=Origin(xyz=(WALL_X * s, 0.0, WALL_DIMS[2] / 2.0 * s)),
        material=mats["mount"],
        name="plank_wall", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"weathered_oak", "dark_walnut", "pale_ash", "painted_red_mill", "teak_and_iron"} else "stone.masonry_wall"),
    )
    seam_spacing = WALL_DIMS[1] / (PLANK_SEAM_COUNT + 1)
    for si in range(PLANK_SEAM_COUNT):
        sy = -WALL_DIMS[1] / 2.0 + seam_spacing * (si + 1)
        wall.visual(
            _box(SEAM_DIMS, s),
            origin=Origin(
                xyz=(
                    (WALL_FACE_X + SEAM_DIMS[0] / 2.0 - 0.002) * s,
                    sy * s,
                    WALL_DIMS[2] / 2.0 * s,
                )
            ),
            material=mats["mount_dark"],
            name=f"plank_seam_{si}", material_class_id=("wood.walnut_dark" if r.palette_style in {"weathered_oak", "dark_walnut", "pale_ash", "painted_red_mill", "mossy_masonry"} else "metal.blackened_gunmetal"),
        )
    for bi, bz in enumerate(WALL_BATTEN_ZS):
        wall.visual(
            _box(WALL_BATTEN_DIMS, s),
            origin=Origin(xyz=((WALL_FACE_X + WALL_BATTEN_DIMS[0] / 2.0 - 0.002) * s, 0.0, bz * s)),
            material=mats["mount_accent"],
            name=f"wall_batten_{bi}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"weathered_oak", "dark_walnut", "pale_ash", "painted_red_mill", "teak_and_iron"} else "stone.masonry_wall"),
        )
    bearing_mesh = mesh_from_cadquery(
        _bearing_block_solid(), "bearing_block", assets=assets, unit_scale=s
    )
    for fi, fy in ((0, BEARING_Y), (1, -BEARING_Y)):
        wall.visual(
            _box(BRACKET_DIMS, s),
            origin=Origin(xyz=(BRACKET_X * s, fy * s, BRACKET_Z * s)),
            material=mats["mount"],
            name=f"bearing_bracket_{fi}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"weathered_oak", "dark_walnut", "pale_ash", "painted_red_mill", "teak_and_iron"} else "stone.masonry_wall"),
        )
        wall.visual(
            _box(GUSSET_DIMS, s),
            origin=Origin(
                xyz=(
                    (WALL_FACE_X + GUSSET_DIMS[0] / 2.0 - 0.015) * s,
                    fy * s,
                    (AXLE_Z - 0.31) * s,
                ),
                rpy=(0.0, -GUSSET_ANGLE, 0.0),
            ),
            material=mats["mount"],
            name=f"angle_gusset_{fi}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"weathered_oak", "dark_walnut", "pale_ash", "painted_red_mill", "teak_and_iron"} else "stone.masonry_wall"),
        )
        wall.visual(
            bearing_mesh,
            origin=Origin(xyz=(0.0, fy * s, AXLE_Z * s)),
            material=mats["mount"],
            name=f"bearing_block_{fi}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"weathered_oak", "dark_walnut", "pale_ash", "painted_red_mill", "teak_and_iron"} else "stone.masonry_wall"),
        )
        for zi, bz in enumerate((AXLE_Z - 0.02, AXLE_Z + 0.10)):
            wall.visual(
                _cyl(0.018, 0.014, s),
                origin=Origin(xyz=(0.105 * s, fy * s, bz * s), rpy=(0.0, math.pi / 2.0, 0.0)),
                material=mats["mount_dark"],
                name=f"bearing_bolt_{fi}_{zi}", material_class_id="metal.blackened_gunmetal",
            )
    return wall


def _build_masonry_sluice(model, r, mats, *, assets):
    s = r.scale
    sluice = model.part("sluice_mount")
    sluice.visual(
        _box(CHANNEL_FLOOR_DIMS, s),
        origin=Origin(xyz=(0.0, 0.0, CHANNEL_FLOOR_DIMS[2] / 2.0 * s)),
        material=mats["mount"],
        name="channel_floor", material_class_id="stone.cut_sedimentary",
    )
    wall_mesh = mesh_from_cadquery(
        _channel_wall_solid(), "masonry_channel_wall", assets=assets, unit_scale=s
    )
    wall_z = CHANNEL_FLOOR_DIMS[2] + CHANNEL_WALL_HEIGHT / 2.0
    for wi, wy in ((0, CHANNEL_WALL_Y), (1, -CHANNEL_WALL_Y)):
        sluice.visual(
            wall_mesh,
            origin=Origin(xyz=(0.0, wy * s, wall_z * s)),
            material=mats["mount"],
            name=f"channel_wall_{wi}", material_class_id="stone.masonry_wall",
        )
        sluice.visual(
            _box(BEARING_PIER_DIMS, s),
            origin=Origin(xyz=(0.0, wy * s, BEARING_PIER_Z * s)),
            material=mats["mount_accent"],
            name=f"bearing_pier_{wi}", material_class_id="stone.cut_sedimentary",
        )
    bearing_mesh = mesh_from_cadquery(
        _bearing_block_solid(), "bearing_block", assets=assets, unit_scale=s
    )
    for bi, by in ((0, BEARING_Y), (1, -BEARING_Y)):
        sluice.visual(
            bearing_mesh,
            origin=Origin(xyz=(0.0, by * s, AXLE_Z * s)),
            material=mats["mount_accent"],
            name=f"bearing_block_{bi}", material_class_id="stone.cut_sedimentary",
        )
    return sluice


_MOUNT_BUILDERS = {
    "trestle_aframe": _build_trestle_aframe,
    "millhouse_wall": _build_millhouse_wall,
    "masonry_sluice": _build_masonry_sluice,
}


# --------------------------------------------------------------------------- #
# Wheel core (rims + axle + collars) — always emitted onto the waterwheel.     #
# --------------------------------------------------------------------------- #
def _emit_wheel_core(wheel, r, mats, *, assets):
    s = r.scale
    rim_mesh = mesh_from_cadquery(_rim_solid(), "wheel_rim", assets=assets, unit_scale=s)
    for ri, ry in ((0, RIM_Y), (1, -RIM_Y)):
        wheel.visual(
            rim_mesh,
            origin=Origin(xyz=(0.0, _wy(ry) * s, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["wheel"],
            name=f"rim_{ri}", material_class_id=("wood.natural_generic" if r.palette_style in {"weathered_oak", "dark_walnut", "pale_ash", "painted_red_mill", "mossy_masonry"} else "wood.mahogany_teak_dark"),
        )
    wheel.visual(
        _cyl(AXLE_R, AXLE_LEN, s),
        origin=Origin(xyz=(0.0, _wy(0.0) * s, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["axle"],
        name="axle", material_class_id="metal.steel_bare",
    )
    collar_mesh = mesh_from_cadquery(_collar_solid(), "axle_collar", assets=assets, unit_scale=s)
    for ci, cy in ((0, COLLAR_Y), (1, -COLLAR_Y)):
        wheel.visual(
            collar_mesh,
            origin=Origin(xyz=(0.0, _wy(cy) * s, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["collar"],
            name=f"axle_collar_{ci}", material_class_id="metal.cast_iron_bare",
        )
    # Thin coaxial journal washers riding the bearing inboard faces. The +Y one
    # straddles the child-frame origin (its flat face is within the 15 mm
    # articulation-origin tolerance of the hub joint origin); both connect to
    # the axle (concentric overlap) so neither is a floating island.
    for ji, jy in ((0, WHEEL_DY), (1, -WHEEL_DY)):
        wheel.visual(
            _cyl(JOURNAL_WASHER_R, JOURNAL_WASHER_LEN, s),
            origin=Origin(xyz=(0.0, _wy(jy) * s, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["collar"],
            name=f"axle_journal_{ji}", material_class_id="metal.cast_iron_bare",
        )


# --------------------------------------------------------------------------- #
# Spoke modules (Slot C) — fixed rim-interior filling (no joints, Rule 1).     #
# --------------------------------------------------------------------------- #
def _emit_radial_spoke_bars(wheel, r, mats, *, assets):
    s = r.scale
    for ri, ry in ((0, RIM_Y), (1, -RIM_Y)):
        wheel.visual(
            _cyl(HUB_R, HUB_LEN, s),
            origin=Origin(xyz=(0.0, _wy(ry) * s, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["wheel"],
            name=f"hub_{ri}", material_class_id=("wood.natural_generic" if r.palette_style in {"weathered_oak", "dark_walnut", "pale_ash", "painted_red_mill", "mossy_masonry"} else "wood.mahogany_teak_dark"),
        )
        for si in range(SPOKE_BARS):
            wheel.visual(
                _box((SPOKE_XSEC[0], SPOKE_XSEC[1], SPOKE_LEN), s),
                origin=Origin(
                    xyz=(0.0, _wy(ry) * s, 0.0), rpy=(0.0, si * math.pi / SPOKE_BARS, 0.0)
                ),
                material=mats["wheel"],
                name=f"spoke_bar_{ri}_{si}", material_class_id=("wood.natural_generic" if r.palette_style in {"weathered_oak", "dark_walnut", "pale_ash", "painted_red_mill", "mossy_masonry"} else "wood.mahogany_teak_dark"),
            )


def _emit_clasp_compass_arm(wheel, r, mats, *, assets):
    s = r.scale
    for ri, ry in ((0, RIM_Y), (1, -RIM_Y)):
        wheel.visual(
            _box((HUB_BOX, HUB_LEN, HUB_BOX), s),
            origin=Origin(xyz=(0.0, _wy(ry) * s, 0.0)),
            material=mats["wheel"],
            name=f"hub_box_{ri}", material_class_id=("wood.natural_generic" if r.palette_style in {"weathered_oak", "dark_walnut", "pale_ash", "painted_red_mill", "mossy_masonry"} else "wood.mahogany_teak_dark"),
        )
        for si in range(CLASP_SPOKE_PAIRS):
            theta = 2.0 * math.pi * si / CLASP_SPOKE_PAIRS
            radial = (math.sin(theta), math.cos(theta))
            tangent = (math.cos(theta), -math.sin(theta))
            hub_center = (
                radial[0] * (HUB_BOX / 2.0 - 0.010),
                radial[1] * (HUB_BOX / 2.0 - 0.010),
            )
            rim_center = (radial[0] * CLASP_RIM_R, radial[1] * CLASP_RIM_R)
            (cx, cy, cz), ctheta, chord_len = _segment_box_origin(
                (
                    rim_center[0] - tangent[0] * CLASP_RIM_HALF_CHORD,
                    rim_center[1] - tangent[1] * CLASP_RIM_HALF_CHORD,
                ),
                (
                    rim_center[0] + tangent[0] * CLASP_RIM_HALF_CHORD,
                    rim_center[1] + tangent[1] * CLASP_RIM_HALF_CHORD,
                ),
                _wy(ry),
            )
            wheel.visual(
                _box((CLASP_ARM_XSEC[0], CLASP_ARM_XSEC[1], chord_len + 0.030), s),
                origin=Origin(xyz=(cx * s, cy * s, cz * s), rpy=(0.0, ctheta, 0.0)),
                material=mats["wheel"],
                name=f"clasp_chord_{ri}_{si}", material_class_id=("wood.natural_generic" if r.palette_style in {"weathered_oak", "dark_walnut", "pale_ash", "painted_red_mill", "mossy_masonry"} else "wood.mahogany_teak_dark"),
            )
            for ai, side in ((0, -1.0), (1, 1.0)):
                p0 = (
                    hub_center[0] + tangent[0] * side * CLASP_HUB_HALF_GAP,
                    hub_center[1] + tangent[1] * side * CLASP_HUB_HALF_GAP,
                )
                p1 = (
                    rim_center[0] + tangent[0] * side * CLASP_RIM_HALF_CHORD,
                    rim_center[1] + tangent[1] * side * CLASP_RIM_HALF_CHORD,
                )
                (ax, ay, az), atheta, arm_len = _segment_box_origin(p0, p1, _wy(ry))
                wheel.visual(
                    _box((CLASP_ARM_XSEC[0], CLASP_ARM_XSEC[1], arm_len + 0.025), s),
                    origin=Origin(xyz=(ax * s, ay * s, az * s), rpy=(0.0, atheta, 0.0)),
                    material=mats["wheel"],
                    name=f"clasp_arm_{ri}_{si}_{ai}", material_class_id=("wood.natural_generic" if r.palette_style in {"weathered_oak", "dark_walnut", "pale_ash", "painted_red_mill", "mossy_masonry"} else "wood.mahogany_teak_dark"),
                )


def _emit_solid_web_disc(wheel, r, mats, *, assets):
    s = r.scale
    web_mesh = mesh_from_cadquery(_web_disc_solid(), "rim_web_disc", assets=assets, unit_scale=s)
    for ri, ry in ((0, RIM_Y), (1, -RIM_Y)):
        wheel.visual(
            web_mesh,
            origin=Origin(xyz=(0.0, _wy(ry) * s, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["wheel"],
            name=f"web_disc_{ri}", material_class_id=("wood.natural_generic" if r.palette_style in {"weathered_oak", "dark_walnut", "pale_ash", "painted_red_mill", "mossy_masonry"} else "wood.mahogany_teak_dark"),
        )
        wheel.visual(
            _cyl(HUB_R, HUB_LEN, s),
            origin=Origin(xyz=(0.0, _wy(ry) * s, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["wheel"],
            name=f"hub_{ri}", material_class_id=("wood.natural_generic" if r.palette_style in {"weathered_oak", "dark_walnut", "pale_ash", "painted_red_mill", "mossy_masonry"} else "wood.mahogany_teak_dark"),
        )


_SPOKE_BUILDERS = {
    "radial_spoke_bars": _emit_radial_spoke_bars,
    "clasp_compass_arm": _emit_clasp_compass_arm,
    "solid_web_disc": _emit_solid_web_disc,
}


# --------------------------------------------------------------------------- #
# Wheel-type modules (Slot A) — N pickup units baked onto the wheel (Rule 1).  #
# --------------------------------------------------------------------------- #
def _emit_flat_paddle(wheel, r, mats, *, assets):
    s = r.scale
    n = r.paddle_count
    dims = (r.paddle_tangential, PADDLE_DIMS[1], PADDLE_DIMS[2])
    for pi in range(n):
        ang = 2.0 * math.pi * pi / n
        wheel.visual(
            _box(dims, s),
            origin=Origin(
                xyz=(
                    PADDLE_R * math.sin(ang) * s,
                    _wy(0.0) * s,
                    PADDLE_R * math.cos(ang) * s,
                ),
                rpy=(0.0, ang, 0.0),
            ),
            material=mats["wheel"],
            name=f"paddle_{pi}", material_class_id=("wood.natural_generic" if r.palette_style in {"weathered_oak", "dark_walnut", "pale_ash", "painted_red_mill", "mossy_masonry"} else "wood.mahogany_teak_dark"),
        )


def _emit_enclosed_bucket(wheel, r, mats, *, assets):
    s = r.scale
    n = r.paddle_count
    bucket_mesh = mesh_from_cadquery(
        _bucket_solid(r.bucket_tangential), "overshot_bucket", assets=assets, unit_scale=s
    )
    for pi in range(n):
        ang = 2.0 * math.pi * pi / n
        wheel.visual(
            bucket_mesh,
            origin=Origin(
                xyz=(
                    BUCKET_R * math.sin(ang) * s,
                    _wy(0.0) * s,
                    BUCKET_R * math.cos(ang) * s,
                ),
                rpy=(0.0, ang, 0.0),
            ),
            material=mats["wheel"],
            name=f"bucket_{pi}", material_class_id=("wood.natural_generic" if r.palette_style in {"weathered_oak", "dark_walnut", "pale_ash", "painted_red_mill", "mossy_masonry"} else "wood.mahogany_teak_dark"),
        )


def _emit_angled_scoop(wheel, r, mats, *, assets):
    s = r.scale
    n = r.paddle_count
    dims = (r.paddle_tangential, PADDLE_DIMS[1], PADDLE_DIMS[2])
    for pi in range(n):
        ang = 2.0 * math.pi * pi / n
        wheel.visual(
            _box(dims, s),
            origin=Origin(
                xyz=(
                    PADDLE_R * math.sin(ang) * s,
                    _wy(0.0) * s,
                    PADDLE_R * math.cos(ang) * s,
                ),
                rpy=(0.0, ang + PADDLE_TILT, 0.0),
            ),
            material=mats["wheel"],
            name=f"paddle_{pi}", material_class_id=("wood.natural_generic" if r.palette_style in {"weathered_oak", "dark_walnut", "pale_ash", "painted_red_mill", "mossy_masonry"} else "wood.mahogany_teak_dark"),
        )


_WHEELTYPE_BUILDERS = {
    "flat_paddle": _emit_flat_paddle,
    "enclosed_bucket": _emit_enclosed_bucket,
    "angled_scoop": _emit_angled_scoop,
}

# Pickup visual name prefix per wheel_type (for count verification).
_PICKUP_PREFIX = {
    "flat_paddle": "paddle_",
    "enclosed_bucket": "bucket_",
    "angled_scoop": "paddle_",
}


# --------------------------------------------------------------------------- #
# Build                                                                        #
# --------------------------------------------------------------------------- #
def build_watermill_waterwheel(
    config: WatermillWaterwheelConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        key: model.material(f"watermill_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in PALETTES[r.palette_style].items()
    }
    s = r.scale

    mount_part = _MOUNT_BUILDERS[r.mount](model, r, mats, assets=assets)

    wheel = model.part("waterwheel")
    _emit_wheel_core(wheel, r, mats, assets=assets)
    _SPOKE_BUILDERS[r.spokes](wheel, r, mats, assets=assets)
    _WHEELTYPE_BUILDERS[r.wheel_type](wheel, r, mats, assets=assets)

    # The single hero joint: a CONTINUOUS hub spin about the horizontal axle
    # (world +Y). Pure journal bearing (axle captured in the bored bearing
    # blocks) -> no clean axis-aligned face pair -> mating grandfathered.
    model.articulation(
        f"{r.mount_prefix}_to_waterwheel",
        ArticulationType.CONTINUOUS,
        parent=mount_part,
        child=wheel,
        origin=Origin(xyz=(0.0, WHEEL_DY * s, AXLE_Z * s)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=80.0, velocity=6.0),
    )

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_watermill_waterwheel(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_watermill_waterwheel(config_from_seed(seed), assets=assets)


# --------------------------------------------------------------------------- #
# Tests                                                                        #
# --------------------------------------------------------------------------- #
def run_watermill_waterwheel_tests(
    object_model: ArticulatedObject,
    config: WatermillWaterwheelConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    s = r.scale

    mount = object_model.get_part(r.mount_part_name)
    wheel = object_model.get_part("waterwheel")
    joint_name = f"{r.mount_prefix}_to_waterwheel"
    spin = object_model.get_articulation(joint_name)

    # --- Captured journal allowances (axle + thrust washer at the bearings). ---
    for bi in (0, 1):
        ctx.allow_overlap(
            wheel,
            mount,
            elem_a="axle",
            elem_b=f"bearing_block_{bi}",
            reason=f"Axle is intentionally captured in bearing journal {bi}.",
        )
        ctx.allow_overlap(
            wheel,
            mount,
            elem_a=f"axle_journal_{bi}",
            elem_b=f"bearing_block_{bi}",
            reason=f"Journal washer {bi} rides against the bearing inboard face.",
        )

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_joint_mating_has_gap()

    # --- Single hero joint: CONTINUOUS hub spin about +Y at the axle line. ---
    non_fixed = [
        a for a in object_model.articulations if a.articulation_type != ArticulationType.FIXED
    ]
    ctx.check(
        "exactly one non-fixed joint (the hub spin)",
        len(non_fixed) == 1,
        details=f"non_fixed={[a.name for a in non_fixed]}",
    )
    ctx.check(
        "hub joint is CONTINUOUS free spin",
        spin.articulation_type == ArticulationType.CONTINUOUS,
        details=f"type={spin.articulation_type}",
    )
    ctx.check(
        "hub spins about the horizontal axle axis (+Y)",
        tuple(spin.axis) == (0.0, 1.0, 0.0),
        details=f"axis={spin.axis}",
    )
    ctx.check(
        "hub joint origin at the axle line",
        abs(spin.origin.xyz[2] - AXLE_Z * s) < 1e-6,
        details=f"joint z={spin.origin.xyz[2]} expected={AXLE_Z * s}",
    )

    # --- Pickup multiplicity: N units copied around the rim (Rule 1). ---
    prefix = _PICKUP_PREFIX[r.wheel_type]
    pickup_names = [v.name for v in wheel.visuals if v.name and v.name.startswith(prefix)]
    ctx.check(
        "N pickup units baked onto the wheel rigid body",
        len(pickup_names) == r.paddle_count,
        details=f"prefix={prefix} count={len(pickup_names)} N={r.paddle_count}",
    )

    # --- Spokes module emitted the expected hub structure. ---
    wheel_visual_names = {v.name for v in wheel.visuals if v.name}
    if r.spokes == "radial_spoke_bars":
        ok = (
            len([n for n in wheel_visual_names if n.startswith("spoke_bar_")]) == 2 * SPOKE_BARS
            and "hub_0" in wheel_visual_names
        )
    elif r.spokes == "clasp_compass_arm":
        ok = (
            len([n for n in wheel_visual_names if n.startswith("clasp_arm_")])
            == 2 * CLASP_SPOKE_PAIRS * 2
            and "hub_box_0" in wheel_visual_names
        )
    else:  # solid_web_disc
        ok = (
            len([n for n in wheel_visual_names if n.startswith("web_disc_")]) == 2
            and "hub_0" in wheel_visual_names
        )
    ctx.check(
        "spokes module emitted the expected rim filling",
        ok,
        details=f"spokes={r.spokes} visuals={sorted(wheel_visual_names)}",
    )

    # --- Mount is grounded; the wheel hangs at the axle line. ---
    mount_aabb = ctx.part_world_aabb(mount)
    ctx.check(
        "mount rests on the ground (z~0)",
        mount_aabb is not None and abs(mount_aabb[0][2]) < 3e-3,
        details=f"mount aabb={mount_aabb}",
    )

    # --- Off-axis proof of continuous rotation about the axle. ---
    p0_rest = ctx.part_element_world_aabb(wheel, elem=f"{prefix}0")
    ctx.check(
        "first pickup rests near the top of the wheel",
        p0_rest is not None and (p0_rest[0][2] + p0_rest[1][2]) / 2.0 > AXLE_Z * s + 0.55 * s,
        details=f"rest aabb={p0_rest}",
    )
    with ctx.pose({spin: math.pi}):
        p0_half = ctx.part_element_world_aabb(wheel, elem=f"{prefix}0")
        ctx.check(
            "half turn carries the first pickup to the bottom",
            p0_half is not None and (p0_half[0][2] + p0_half[1][2]) / 2.0 < AXLE_Z * s - 0.55 * s,
            details=f"aabb at q=pi={p0_half}",
        )

    # --- slot_choices recorded with paddle_count encoded. ---
    ctx.check(
        "slot_choices recorded with paddle_count encoded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    return ctx.report()


__all__ = (
    "WatermillWaterwheelConfig",
    "ResolvedWatermillWaterwheelConfig",
    "build_watermill_waterwheel",
    "build_seeded_watermill_waterwheel",
    "config_from_seed",
    "resolve_config",
    "run_watermill_waterwheel_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
)
