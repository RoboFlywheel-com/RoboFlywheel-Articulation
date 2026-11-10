# SPDX-License-Identifier: Apache-2.0

"""Single-wheel wheelbarrow — modular procedural template.

A SINGLE-wheel wheelbarrow (Agricultural / Single-Wheelbarrow). Structure family
(pattern = ``mixed``): a kinematic root ``wheel_axle_pivot`` at the front axle
centre carries the fixed steel through-``axle`` (its only geometry — the captured
pin everything articulates about) and TWO parallel children that both articulate
about the same lateral (X) axle line:

  * ``barrow`` (body) — ``axle_pivot_to_barrow`` REVOLUTE (body-tip / dump,
    axis=(1,0,0), lower=0 -> upper≈1.05). Its visuals fuse the ``tub_body`` slot
    (the tub/tray/deck/box) AND the ``frame_build`` slot (handles + legs +
    brackets) into one rigid part; they connect through a shared ``tub_bearer``
    plate + ``tray_mount_*`` pads. The frame's rails/brackets embrace the root's
    fixed axle (link-pair overlap allowance below).
  * ``wheel`` — ``axle_pivot_to_wheel`` CONTINUOUS (wheel spin, axis=(1,0,0)).
    The ``wheel_type`` slot lives here; tyre/rim/disc symmetry axis is local X so
    the joint needs no rpy.

Both joints share ``origin=AXLE_PIVOT`` and ``axis=(1,0,0)`` for every seed
(uniform joint frame). The steel ``axle`` cylinder (on ``wheel_axle_pivot``,
rotationally symmetric about the tip axis so it reads as fixed in every pose) is
captured through the wheel hub/rim/disc bore — a captured-pin fit, so the joints
omit a ``MatingContract`` (grandfathered) and the overlap is declared
element-scoped in ``run_single_wheelbarrow_tests``.

Sourced from ``articraft_template_authoring/specs_modular_v1/single_wheelbarrow.md``
and the ``picture/Agricultural/Single-Wheelbarrow`` 5-star pool (2 origins + 6
slot-fork variants), all synced under ``data/records/``. Origin A (steel pan /
pneumatic / tube frame, long axis +Y) and origin B (wood slat box / wood-spoked /
wood runner, long axis +X) use different coordinate conventions; this template
adopts the **A convention** (AXLE_PIVOT=(0,-0.60,0.25), long axis +Y) and
re-expresses the wood modules into it.

Slots (spec §4):
  * ``tub_body`` (4, ③ primary form): steel_pressed_pan / plastic_molded_tub /
    flatbed_deck / wood_slat_box — barrow visuals.
  * ``wheel_type`` (3): pneumatic_steel_rim / solid_disc (LatheGeometry, never a
    Box) / wood_spoked_cart — wheel visuals.
  * ``frame_build`` (3, ① skeleton): tube_rail / welded_flatbar / wood_runner —
    barrow visuals.
  * ``side_slat_count`` (N in {2,3,5}, [2,8]) — wood-box side/end slat
    multiplicity; encoded ``("side_slat_count", f"n{N}")`` (``n0`` for non-wood
    tubs, spec §8).
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, replace
from typing import Literal

from sdk import (
    AppearanceOnlySpec,
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    BoltPattern,
    Box,
    Cylinder,
    LatheGeometry,
    MeshGeometry,
    MotionLimits,
    Origin,
    Sphere,
    TestContext,
    TestReport,
    TireCarcass,
    TireGeometry,
    TireGroove,
    TireShoulder,
    TireSidewall,
    TireTread,
    WheelBore,
    WheelFace,
    WheelGeometry,
    WheelHub,
    WheelRim,
    WheelSpokes,
    mesh_from_geometry,
    tube_from_spline_points,
)

__modular__ = True

TubBody = Literal["steel_pressed_pan", "plastic_molded_tub", "flatbed_deck", "wood_slat_box"]
WheelType = Literal["pneumatic_steel_rim", "solid_disc", "wood_spoked_cart"]
FrameBuild = Literal["tube_rail", "welded_flatbar", "wood_runner"]
PaletteStyle = Literal[
    "galvanized_green",
    "natural_wood_black",
    "red_painted",
    "blue_orange_contractor",
    "green_poly",
    "yellow_builder",
]

TUB_BODIES: tuple[TubBody, ...] = (
    "steel_pressed_pan",
    "plastic_molded_tub",
    "flatbed_deck",
    "wood_slat_box",
)
WHEEL_TYPES: tuple[WheelType, ...] = ("pneumatic_steel_rim", "solid_disc", "wood_spoked_cart")
FRAME_BUILDS: tuple[FrameBuild, ...] = ("tube_rail", "welded_flatbar", "wood_runner")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "galvanized_green",
    "natural_wood_black",
    "red_painted",
    "blue_orange_contractor",
    "green_poly",
    "yellow_builder",
)

# side_slat_count (wood box) multiplicity axis (spec §8).
N_MIN = 2
N_MAX = 8
SLAT_SAMPLE_VALUES = (2, 3, 5)
SLAT_SAMPLE_WEIGHTS = (0.50, 0.32, 0.18)

# Shared frame / axle geometry (A convention, world-at-rest coords).
AXLE_PIVOT = (0.0, -0.60, 0.25)
AXLE_R = 0.022
AXLE_LEN = 0.74
RAIL_X = 0.31
# Tub seat plane: the tub_bearer plate top the tray_mount pads rest on.
BEARER_Z = 0.315

PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "galvanized_green": {
        "tub": (0.58, 0.62, 0.62, 1.0),
        "tub_edge": (0.42, 0.45, 0.45, 1.0),
        "wood": (0.72, 0.47, 0.22, 1.0),
        "wood_grain": (0.18, 0.11, 0.055, 1.0),
        "frame": (0.02, 0.18, 0.11, 1.0),
        "frame_edge": (0.04, 0.25, 0.16, 1.0),
        "rim": (0.04, 0.25, 0.16, 1.0),
        "tire": (0.02, 0.02, 0.02, 1.0),
        "grip": (0.20, 0.20, 0.22, 1.0),
        "hardware": (0.03, 0.03, 0.03, 1.0),
        "marker": (0.47, 0.08, 0.16, 1.0),
    },
    "natural_wood_black": {
        "tub": (0.66, 0.45, 0.22, 1.0),
        "tub_edge": (0.47, 0.28, 0.12, 1.0),
        "wood": (0.73, 0.48, 0.22, 1.0),
        "wood_grain": (0.18, 0.11, 0.055, 1.0),
        "frame": (0.22, 0.14, 0.07, 1.0),
        "frame_edge": (0.015, 0.017, 0.018, 1.0),
        "rim": (0.66, 0.42, 0.18, 1.0),
        "tire": (0.015, 0.014, 0.012, 1.0),
        "grip": (0.47, 0.08, 0.16, 1.0),
        "hardware": (0.06, 0.065, 0.07, 1.0),
        "marker": (0.47, 0.08, 0.16, 1.0),
    },
    "red_painted": {
        "tub": (0.62, 0.07, 0.05, 1.0),
        "tub_edge": (0.44, 0.05, 0.04, 1.0),
        "wood": (0.66, 0.45, 0.22, 1.0),
        "wood_grain": (0.20, 0.12, 0.06, 1.0),
        "frame": (0.34, 0.03, 0.03, 1.0),
        "frame_edge": (0.50, 0.05, 0.05, 1.0),
        "rim": (0.75, 0.75, 0.77, 1.0),
        "tire": (0.03, 0.03, 0.03, 1.0),
        "grip": (0.05, 0.05, 0.06, 1.0),
        "hardware": (0.03, 0.03, 0.03, 1.0),
        "marker": (0.90, 0.90, 0.20, 1.0),
    },
    "blue_orange_contractor": {
        "tub": (0.06, 0.20, 0.52, 1.0),
        "tub_edge": (0.03, 0.12, 0.34, 1.0),
        "wood": (0.66, 0.45, 0.22, 1.0),
        "wood_grain": (0.20, 0.12, 0.06, 1.0),
        "frame": (0.85, 0.35, 0.03, 1.0),
        "frame_edge": (0.95, 0.45, 0.06, 1.0),
        "rim": (0.10, 0.10, 0.11, 1.0),
        "tire": (0.02, 0.02, 0.02, 1.0),
        "grip": (0.90, 0.40, 0.05, 1.0),
        "hardware": (0.05, 0.05, 0.05, 1.0),
        "marker": (0.95, 0.95, 0.90, 1.0),
    },
    "green_poly": {
        "tub": (0.08, 0.30, 0.12, 1.0),
        "tub_edge": (0.05, 0.06, 0.05, 1.0),
        "wood": (0.66, 0.45, 0.22, 1.0),
        "wood_grain": (0.20, 0.12, 0.06, 1.0),
        "frame": (0.06, 0.06, 0.07, 1.0),
        "frame_edge": (0.11, 0.11, 0.12, 1.0),
        "rim": (0.10, 0.10, 0.11, 1.0),
        "tire": (0.02, 0.02, 0.02, 1.0),
        "grip": (0.20, 0.20, 0.22, 1.0),
        "hardware": (0.03, 0.03, 0.03, 1.0),
        "marker": (0.90, 0.90, 0.20, 1.0),
    },
    "yellow_builder": {
        "tub": (0.92, 0.78, 0.06, 1.0),
        "tub_edge": (0.78, 0.65, 0.04, 1.0),
        "wood": (0.66, 0.45, 0.22, 1.0),
        "wood_grain": (0.20, 0.12, 0.06, 1.0),
        "frame": (0.06, 0.06, 0.07, 1.0),
        "frame_edge": (0.12, 0.12, 0.13, 1.0),
        "rim": (0.78, 0.65, 0.04, 1.0),
        "tire": (0.02, 0.02, 0.02, 1.0),
        "grip": (0.20, 0.20, 0.22, 1.0),
        "hardware": (0.03, 0.03, 0.03, 1.0),
        "marker": (0.10, 0.10, 0.10, 1.0),
    },
}


# ---------------------------------------------------------------------------
# Config.
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class SingleWheelbarrowConfig:
    tub_body: TubBody | None = None
    wheel_type: WheelType | None = None
    frame_build: FrameBuild | None = None
    side_slat_count: int | None = None
    palette_style: PaletteStyle = "galvanized_green"
    tub_width_scale: float = 1.0
    tub_length_scale: float = 1.0
    tub_depth_scale: float = 1.0
    handle_reach_scale: float = 1.0
    wheel_size_scale: float = 1.0
    body_tip_upper: float = 1.05
    name: str = "single_wheelbarrow"


@dataclass(frozen=True)
class ResolvedSingleWheelbarrowConfig:
    tub_body: TubBody
    wheel_type: WheelType
    frame_build: FrameBuild
    side_slat_count: int  # effective: 0 for non-wood tubs
    palette_style: PaletteStyle
    tub_width_scale: float
    tub_length_scale: float
    tub_depth_scale: float
    handle_reach_scale: float
    wheel_size_scale: float
    body_tip_upper: float
    name: str


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _pick(v, choices):
    return v if v in choices else choices[0]


def config_from_seed(seed: int) -> SingleWheelbarrowConfig:
    rng = random.Random(seed)
    return SingleWheelbarrowConfig(
        tub_body=rng.choice(TUB_BODIES),
        wheel_type=rng.choice(WHEEL_TYPES),
        frame_build=rng.choice(FRAME_BUILDS),
        side_slat_count=rng.choices(SLAT_SAMPLE_VALUES, weights=SLAT_SAMPLE_WEIGHTS, k=1)[0],
        palette_style=rng.choice(PALETTE_STYLES),
        tub_width_scale=round(rng.uniform(0.90, 1.12), 4),
        tub_length_scale=round(rng.uniform(0.90, 1.12), 4),
        tub_depth_scale=round(rng.uniform(0.88, 1.15), 4),
        handle_reach_scale=round(rng.uniform(0.92, 1.10), 4),
        wheel_size_scale=round(rng.uniform(0.90, 1.12), 4),
        body_tip_upper=round(rng.uniform(1.00, 1.15), 4),
        name=f"seeded_single_wheelbarrow_{seed}",
    )


def resolve_config(
    config: SingleWheelbarrowConfig | None = None,
) -> ResolvedSingleWheelbarrowConfig:
    cfg = config or SingleWheelbarrowConfig()
    tub_body = _pick(cfg.tub_body, TUB_BODIES)
    wheel_type = _pick(cfg.wheel_type, WHEEL_TYPES)
    frame_build = _pick(cfg.frame_build, FRAME_BUILDS)

    raw_n = int(cfg.side_slat_count) if cfg.side_slat_count is not None else 3
    raw_n = int(_clamp(raw_n, N_MIN, N_MAX))
    # side_slat_count is conditional on wood_slat_box (spec §9): non-wood tubs
    # have no slat walls -> effective N = 0 (encoded n0), no slats emitted.
    slat_count = raw_n if tub_body == "wood_slat_box" else 0

    return ResolvedSingleWheelbarrowConfig(
        tub_body=tub_body,
        wheel_type=wheel_type,
        frame_build=frame_build,
        side_slat_count=slat_count,
        palette_style=_pick(cfg.palette_style, PALETTE_STYLES),
        tub_width_scale=_clamp(cfg.tub_width_scale, 0.90, 1.12),
        tub_length_scale=_clamp(cfg.tub_length_scale, 0.90, 1.12),
        tub_depth_scale=_clamp(cfg.tub_depth_scale, 0.88, 1.15),
        handle_reach_scale=_clamp(cfg.handle_reach_scale, 0.92, 1.10),
        wheel_size_scale=_clamp(cfg.wheel_size_scale, 0.90, 1.12),
        body_tip_upper=_clamp(cfg.body_tip_upper, 1.00, 1.15),
        name=cfg.name or "single_wheelbarrow",
    )


def with_overrides(config: SingleWheelbarrowConfig, **kwargs: object) -> SingleWheelbarrowConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: SingleWheelbarrowConfig | ResolvedSingleWheelbarrowConfig,
) -> tuple[tuple[str, str], ...]:
    r = (
        config
        if isinstance(config, ResolvedSingleWheelbarrowConfig)
        else resolve_config(config)
    )
    return (
        ("tub_body", r.tub_body),
        ("frame_build", r.frame_build),
        ("wheel_type", r.wheel_type),
        ("side_slat_count", f"n{r.side_slat_count}"),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Coordinate helpers (A convention). Barrow visuals authored in world-at-rest
# coords and shifted by -AXLE_PIVOT into the barrow part frame (its joint origin
# is AXLE_PIVOT). Wheel visuals are authored directly in the wheel-local frame
# (centre == AXLE_PIVOT).
# ---------------------------------------------------------------------------
def _origin(x: float, y: float, z: float, rpy=(0.0, 0.0, 0.0)) -> Origin:
    return Origin(xyz=(x, y, z), rpy=rpy)


def _barrow_origin(x: float, y: float, z: float, rpy=(0.0, 0.0, 0.0)) -> Origin:
    return Origin(
        xyz=(x - AXLE_PIVOT[0], y - AXLE_PIVOT[1], z - AXLE_PIVOT[2]),
        rpy=rpy,
    )


def _barrow_point(p):
    return (p[0] - AXLE_PIVOT[0], p[1] - AXLE_PIVOT[1], p[2] - AXLE_PIVOT[2])


def _barrow_mesh(geometry: MeshGeometry) -> MeshGeometry:
    return geometry.translate(-AXLE_PIVOT[0], -AXLE_PIVOT[1], -AXLE_PIVOT[2])


def _add_quad(geom: MeshGeometry, a: int, b: int, c: int, d: int) -> None:
    geom.add_face(a, b, c)
    geom.add_face(a, c, d)


def _add_box_to_mesh(geom, x0, x1, y0, y1, z0, z1) -> None:
    v = [
        geom.add_vertex(x0, y0, z0),
        geom.add_vertex(x1, y0, z0),
        geom.add_vertex(x1, y1, z0),
        geom.add_vertex(x0, y1, z0),
        geom.add_vertex(x0, y0, z1),
        geom.add_vertex(x1, y0, z1),
        geom.add_vertex(x1, y1, z1),
        geom.add_vertex(x0, y1, z1),
    ]
    geom.add_face(v[0], v[2], v[1])
    geom.add_face(v[0], v[3], v[2])
    geom.add_face(v[4], v[5], v[6])
    geom.add_face(v[4], v[6], v[7])
    geom.add_face(v[0], v[1], v[5])
    geom.add_face(v[0], v[5], v[4])
    geom.add_face(v[2], v[3], v[7])
    geom.add_face(v[2], v[7], v[6])
    geom.add_face(v[0], v[4], v[7])
    geom.add_face(v[0], v[7], v[3])
    geom.add_face(v[1], v[2], v[6])
    geom.add_face(v[1], v[6], v[5])


def _rounded_rect_loop(width, length, z, segments=64, exponent=3.6):
    pts = []
    for i in range(segments):
        t = 2.0 * math.pi * i / segments
        ct = math.cos(t)
        st = math.sin(t)
        x = (width * 0.5) * math.copysign(abs(ct) ** (2.0 / exponent), ct)
        y = (length * 0.5) * math.copysign(abs(st) ** (2.0 / exponent), st)
        pts.append((x, y, z))
    return pts


def _barrow_tube_mesh(points, radius, name, radial=16, per_seg=12):
    shifted = [_barrow_point(p) for p in points]
    return mesh_from_geometry(
        tube_from_spline_points(
            shifted,
            radius=radius,
            samples_per_segment=per_seg,
            radial_segments=radial,
            cap_ends=True,
        ),
        name,
    )


def _barrow_beam_yz(part, name, p0, p1, section_x, section_z, material):
    """Box beam whose long axis follows a line in the world YZ plane (pitch about X)."""
    x0, y0, z0 = _barrow_point(p0)
    x1, y1, z1 = _barrow_point(p1)
    dy = y1 - y0
    dz = z1 - z0
    length = math.hypot(dy, dz)
    pitch = math.atan2(dz, dy)
    part.visual(
        Box((section_x, length, section_z)),
        origin=_origin((x0 + x1) * 0.5, (y0 + y1) * 0.5, (z0 + z1) * 0.5, (pitch, 0.0, 0.0)),
        material=material,
        name=name, material_class_id="metal.paint_coated",
    )


# ---------------------------------------------------------------------------
# Shared hardware: the through-axle (owned by the fixed kinematic root) + the
# tub bearer plate (tub<->frame bridge, on the barrow).
# ---------------------------------------------------------------------------
def _emit_axle(pivot, mats) -> None:
    # Steel through-axle centred on AXLE_PIVOT, along X, owned by the fixed
    # kinematic root ``wheel_axle_pivot``. It is the captured pin the wheel
    # spins on, and it is rotationally symmetric about the tip/dump (X) axis,
    # so it reads as fixed in every pose. The root frame is the world-at-rest
    # frame, so the axle is placed directly at AXLE_PIVOT.
    pivot.visual(
        Cylinder(radius=AXLE_R, length=AXLE_LEN),
        origin=_origin(*AXLE_PIVOT, (0.0, math.pi / 2.0, 0.0)),
        material=mats["hardware"],
        name="axle", material_class_id="metal.steel_bare",
    )


def _emit_tub_bearer(barrow, mats) -> None:
    # Full-width flat bearer plate at the tub seat plane. Overlaps both rails
    # (x=±RAIL_X) and receives the tub tray_mount pads -> single connected island.
    barrow.visual(
        Box((0.68, 0.40, 0.045)),
        origin=_barrow_origin(0.0, 0.03, BEARER_Z),
        material=mats["frame"],
        name="tub_bearer", material_class_id="metal.paint_coated",
    )


def _emit_tray_mounts(barrow, mats, floor_bottom_z: float) -> None:
    # Pads bridge the tub_bearer (z≈0.315) up into the tub floor. Reach from
    # z=0.30 (inside the bearer) to floor_bottom_z+embed.
    z_bot = 0.30
    z_top = max(floor_bottom_z + 0.02, z_bot + 0.05)
    zc = 0.5 * (z_bot + z_top)
    h = z_top - z_bot
    for i, (x, y) in enumerate([(-0.18, -0.10), (0.18, -0.10), (-0.18, 0.16), (0.18, 0.16)]):
        barrow.visual(
            Box((0.09, 0.08, h)),
            origin=_barrow_origin(x, y, zc),
            material=mats["frame"],
            name=f"tray_mount_{i}", material_class_id="metal.paint_coated",
        )


# ---------------------------------------------------------------------------
# tub_body slot (barrow visuals). Each returns the tub shell element name and
# the floor-bottom z used to size the tray_mount pads.
# ---------------------------------------------------------------------------
def _steel_pan_geometry(w, l, d, segments=64):
    floor_z = 0.32

    def zc(z):
        return floor_z + (z - floor_z) * d

    outer_bottom = _rounded_rect_loop(0.42 * w, 0.58 * l, zc(0.32), segments)
    inner_bottom = _rounded_rect_loop(0.32 * w, 0.48 * l, zc(0.36), segments)
    inner_top = _rounded_rect_loop(0.72 * w, 1.04 * l, zc(0.67), segments)
    outer_lip = _rounded_rect_loop(0.86 * w, 1.18 * l, zc(0.70), segments)
    geom = MeshGeometry()
    n = segments
    loops = []
    for loop in (outer_bottom, inner_bottom, inner_top, outer_lip):
        loops.append([geom.add_vertex(*p) for p in loop])
    ob, ib, it, ol = loops
    center_under = geom.add_vertex(0.0, 0.0, zc(0.32))
    center_floor = geom.add_vertex(0.0, 0.0, zc(0.36))
    for i in range(n):
        j = (i + 1) % n
        _add_quad(geom, ob[i], ob[j], ol[j], ol[i])
        _add_quad(geom, it[i], it[j], ib[j], ib[i])
        _add_quad(geom, ol[i], ol[j], it[j], it[i])
        _add_quad(geom, ib[i], ib[j], ob[j], ob[i])
        geom.add_face(center_under, ob[j], ob[i])
        geom.add_face(center_floor, ib[i], ib[j])
    return geom


def _emit_steel_pan(barrow, r, mats) -> tuple[str, float]:
    w, l, d = r.tub_width_scale, r.tub_length_scale, r.tub_depth_scale
    barrow.visual(
        mesh_from_geometry(_barrow_mesh(_steel_pan_geometry(w, l, d)), "steel_tray_shell"),
        material=mats["tub"],
        name="tray_shell", material_class_id="metal.paint_coated",
    )
    # Reinforcing straps / seams (④). Thickness embeds the strap into the tapered
    # side wall (was 0.012 → floated ~0.013m off the shell; 0.05 straddles it).
    for x, name in [(-0.36 * w, "side_rib_0"), (0.36 * w, "side_rib_1")]:
        barrow.visual(
            Box((0.05, 0.80 * l, 0.028)),
            origin=_barrow_origin(x, 0.05, 0.55),
            material=mats["tub_edge"],
            name=name, material_class_id="metal.paint_coated",
        )
    barrow.visual(
        Box((0.58 * w, 0.030, 0.026)),
        origin=_barrow_origin(0.0, -0.535 * l, 0.63),
        material=mats["tub_edge"],
        name="front_seam", material_class_id="metal.paint_coated",
    )
    barrow.visual(
        Box((0.52 * w, 0.035, 0.026)),
        origin=_barrow_origin(0.0, 0.535 * l, 0.63),
        material=mats["tub_edge"],
        name="rear_seam", material_class_id="metal.paint_coated",
    )
    _emit_tray_mounts(barrow, mats, floor_bottom_z=0.32)
    return "tray_shell", 0.32


def _poly_tub_geometry(w, l, d, segments=64):
    floor_z = 0.30
    exp = 2.8

    def zc(z):
        return floor_z + (z - floor_z) * d

    outer_bottom = _rounded_rect_loop(0.40 * w, 0.56 * l, zc(0.30), segments, exp)
    inner_bottom = _rounded_rect_loop(0.28 * w, 0.44 * l, zc(0.36), segments, exp)
    inner_top = _rounded_rect_loop(0.68 * w, 1.00 * l, zc(0.68), segments, exp)
    outer_rim = _rounded_rect_loop(0.82 * w, 1.14 * l, zc(0.72), segments, exp)
    geom = MeshGeometry()
    n = segments
    loops = []
    for loop in (outer_bottom, inner_bottom, inner_top, outer_rim):
        loops.append([geom.add_vertex(*p) for p in loop])
    ob, ib, it, ol = loops
    center_under = geom.add_vertex(0.0, 0.0, zc(0.30))
    center_floor = geom.add_vertex(0.0, 0.0, zc(0.36))
    for i in range(n):
        j = (i + 1) % n
        _add_quad(geom, ob[i], ob[j], ol[j], ol[i])
        _add_quad(geom, it[i], it[j], ib[j], ib[i])
        _add_quad(geom, ol[i], ol[j], it[j], it[i])
        _add_quad(geom, ib[i], ib[j], ob[j], ob[i])
        geom.add_face(center_under, ob[j], ob[i])
        geom.add_face(center_floor, ib[i], ib[j])
    return geom


def _emit_plastic_tub(barrow, r, mats) -> tuple[str, float]:
    w, l, d = r.tub_width_scale, r.tub_length_scale, r.tub_depth_scale
    barrow.visual(
        mesh_from_geometry(_barrow_mesh(_poly_tub_geometry(w, l, d)), "poly_tub_shell"),
        material=mats["tub"],
        name="tray_shell", material_class_id="plastic.opaque_glossy_molded",
    )
    # Molded structural flutes (④) straddling the outer walls (intentional local
    # overlap with the shell, declared in run_tests). Sampled off the final wall.
    flute_idx = 0
    for x_sign in (-1, 1):
        for y_off, z_off in [(-0.12, 0.44), (0.06, 0.50), (0.28, 0.56)]:
            frac = (z_off - 0.30) / (0.72 - 0.30)
            half_w = (0.20 + frac * (0.41 - 0.20)) * w
            half_l = (0.28 + frac * (0.57 - 0.28)) * l
            y_frac = abs(y_off) / max(half_l, 0.01)
            se = max(0.0, 1.0 - y_frac**2.8) ** (1.0 / 2.8)
            barrow.visual(
                Box((0.030, 0.16, 0.024)),
                origin=_barrow_origin(x_sign * half_w * se, y_off, 0.30 + (z_off - 0.30) * d),
                material=mats["tub_edge"],
                name=f"molded_flute_{flute_idx}", material_class_id="plastic.opaque_glossy_molded",
            )
            flute_idx += 1
    _emit_tray_mounts(barrow, mats, floor_bottom_z=0.30)
    return "tray_shell", 0.30


def _flat_deck_geometry(w, l):
    geom = MeshGeometry()
    pw = 0.70 * w
    pl = 0.86 * l
    z_bot = 0.380
    z_top = z_bot + 0.007
    rw = 0.014
    z_rail_top = z_top + 0.030
    hw = pw * 0.5
    hl = pl * 0.5
    yc = 0.17
    _add_box_to_mesh(geom, -hw, hw, yc - hl, yc + hl, z_bot, z_top)
    _add_box_to_mesh(geom, -hw, hw, yc - hl, yc - hl + rw, z_top, z_rail_top)
    _add_box_to_mesh(geom, -hw, hw, yc + hl - rw, yc + hl, z_top, z_rail_top)
    _add_box_to_mesh(geom, -hw, -hw + rw, yc - hl + rw, yc + hl - rw, z_top, z_rail_top)
    _add_box_to_mesh(geom, hw - rw, hw, yc - hl + rw, yc + hl - rw, z_top, z_rail_top)
    return geom


def _emit_flatbed_deck(barrow, r, mats) -> tuple[str, float]:
    w, l = r.tub_width_scale, r.tub_length_scale
    barrow.visual(
        mesh_from_geometry(_barrow_mesh(_flat_deck_geometry(w, l)), "flat_deck_plate"),
        material=mats["tub"],
        name="tray_shell", material_class_id="wood.plywood",
    )
    # Anti-slip tread strips (④).
    n_tread = 8
    y_start = 0.17 - 0.86 * l * 0.5 + 0.06
    y_end = 0.17 + 0.86 * l * 0.5 - 0.06
    for i in range(n_tread):
        frac = (i + 1) / (n_tread + 1)
        ty = y_start + frac * (y_end - y_start)
        barrow.visual(
            Box((0.70 * w - 0.08, 0.012, 0.006)),
            origin=_barrow_origin(0.0, ty, 0.386),
            material=mats["tub_edge"],
            name=f"tread_strip_{i}", material_class_id="rubber.directional_grooved",
        )
    _emit_tray_mounts(barrow, mats, floor_bottom_z=0.38)
    return "tray_shell", 0.38


def _emit_wood_slat_box(barrow, r, mats) -> tuple[str, float]:
    """Assembled wooden slat box (Macro Surface). side/end walls are the N-slat
    multiplicity axis. Re-expressed into A convention: floor planks run along Y,
    side walls at ±X, end walls at ±Y.

    The box is seated rearward (centre yc=0.15) so its front wall stays behind the
    front wheel: every box point is then farther from AXLE_PIVOT than the wheel
    radius, so it clears the wheel at ALL body-tip angles (rotation about the
    pivot preserves radius)."""
    w, l, d = r.tub_width_scale, r.tub_length_scale, r.tub_depth_scale
    n = max(r.side_slat_count, 2)
    floor_z = 0.40
    floor_bottom = floor_z - 0.0175
    yc = 0.15
    half_x = 0.34 * w
    half_y = 0.40 * l
    front_y = yc - half_y
    rear_y = yc + half_y
    box_len_y = 2.0 * half_y
    pitch = 0.11 * d
    slat_h = 0.075
    first_row_z = floor_z + 0.05

    # Floor planks (along Y) + binding ties (along X) so they read as one floor.
    for i, x in enumerate((-0.24 * w, 0.0, 0.24 * w)):
        barrow.visual(
            Box((0.16 * w, box_len_y, 0.035)),
            origin=_barrow_origin(x, yc, floor_z),
            material=mats["wood"],
            name=f"floor_plank_{i}", material_class_id="wood.plank_floor",
        )
    for i, y in enumerate((front_y + 0.06, yc, rear_y - 0.06)):
        barrow.visual(
            Box((0.68 * w, 0.09, 0.045)),
            origin=_barrow_origin(0.0, y, floor_z),
            material=mats["wood"],
            name=f"floor_tie_{i}", material_class_id="wood.natural_generic",
        )

    top_z = first_row_z + n * pitch
    # Side walls (±X): N slat rows along Y.
    for side, x in (("side_0", -half_x), ("side_1", half_x)):
        for row in range(n):
            z_row = first_row_z + pitch * (row + 0.5)
            barrow.visual(
                Box((0.05, box_len_y + 0.04, slat_h)),
                origin=_barrow_origin(x, yc, z_row),
                material=mats["wood"],
                name=f"{side}_slat_{row}", material_class_id="wood.natural_generic",
            )
            barrow.visual(
                Box((0.006, box_len_y * 0.75, 0.006)),
                origin=_barrow_origin(x + (0.028 if x > 0 else -0.028), yc, z_row + 0.010),
                material=mats["wood_grain"],
                name=f"{side}_grain_{row}", material_class_id="wood.walnut_dark",
            )
        barrow.visual(
            Box((0.06, box_len_y + 0.08, 0.06)),
            origin=_barrow_origin(x, yc, top_z),
            material=mats["wood"],
            name=f"{side}_top_lip", material_class_id="wood.natural_generic",
        )
    # End walls (±Y): N slat rows along X.
    for end, y in (("front", front_y), ("rear", rear_y)):
        for row in range(n):
            z_row = first_row_z + pitch * (row + 0.5)
            barrow.visual(
                Box((0.68 * w, 0.06, slat_h)),
                origin=_barrow_origin(0.0, y, z_row),
                material=mats["wood"],
                name=f"{end}_slat_{row}", material_class_id="wood.natural_generic",
            )
        barrow.visual(
            Box((0.72 * w, 0.07, 0.06)),
            origin=_barrow_origin(0.0, y, top_z),
            material=mats["wood"],
            name=f"{end}_top_lip", material_class_id="wood.natural_generic",
        )
    # Corner + mid uprights tie walls to floor.
    post_h = top_z - floor_bottom
    post_zc = 0.5 * (floor_bottom + top_z)
    post_xy = [
        (-half_x, front_y),
        (half_x, front_y),
        (-half_x, rear_y),
        (half_x, rear_y),
        (-half_x, yc),
        (half_x, yc),
    ]
    for idx, (x, y) in enumerate(post_xy):
        barrow.visual(
            Box((0.06, 0.06, post_h)),
            origin=_barrow_origin(x, y, post_zc),
            material=mats["wood"],
            name=f"upright_post_{idx}", material_class_id="wood.natural_generic",
        )
    _emit_tray_mounts(barrow, mats, floor_bottom_z=floor_bottom)
    return "floor_plank_1", floor_bottom


_TUB_BUILDERS = {
    "steel_pressed_pan": _emit_steel_pan,
    "plastic_molded_tub": _emit_plastic_tub,
    "flatbed_deck": _emit_flatbed_deck,
    "wood_slat_box": _emit_wood_slat_box,
}


# ---------------------------------------------------------------------------
# frame_build slot (barrow visuals). Rails start on the axle (x=±RAIL_X, y,z of
# AXLE_PIVOT) so they overlap it; they stay low through the tub region then rise
# to the grips. Every frame emits the shared tub_bearer; the through-axle is
# owned by the kinematic root (emitted in build_single_wheelbarrow).
# ---------------------------------------------------------------------------
def _grip_bands(barrow, mats, x, gy, gz) -> None:
    barrow.visual(
        Cylinder(radius=0.035, length=0.18),
        origin=_barrow_origin(x, gy, gz, (-math.pi / 2.0, 0.0, 0.0)),
        material=mats["grip"],
        name=f"grip_{0 if x < 0 else 1}", material_class_id="rubber.smooth_plain",
    )
    for ring_i, dy in enumerate((-0.06, -0.02, 0.02, 0.06)):
        barrow.visual(
            Cylinder(radius=0.037, length=0.008),
            origin=_barrow_origin(x, gy + dy, gz, (-math.pi / 2.0, 0.0, 0.0)),
            material=mats["hardware"],
            name=f"grip_ring_{0 if x < 0 else 1}_{ring_i}", material_class_id="metal.blackened_gunmetal",
        )


def _emit_tube_rail(barrow, r, mats) -> None:
    reach = r.handle_reach_scale
    _emit_tub_bearer(barrow, mats)

    def rail_pts(sx):
        return [
            (sx * RAIL_X, AXLE_PIVOT[1], AXLE_PIVOT[2]),  # on the axle
            (sx * RAIL_X, -0.20, 0.30),
            (sx * RAIL_X, 0.28, 0.35),
            (sx * RAIL_X, 0.58 * reach, 0.56),
            (sx * RAIL_X, 1.08 * reach, 0.88),
            (sx * RAIL_X, 1.42 * reach, 0.95),
        ]

    for sx, idx in ((-1.0, 0), (1.0, 1)):
        barrow.visual(
            _barrow_tube_mesh(rail_pts(sx), 0.018, f"handle_rail_{idx}"),
            material=mats["frame"],
            name=f"handle_rail_{idx}", material_class_id="metal.paint_coated",
        )
        _grip_bands(barrow, mats, sx * RAIL_X, 1.50 * reach, 0.955)

    # Front guard loop ahead of the wheel (touches the rails on the axle).
    barrow.visual(
        _barrow_tube_mesh(
            [
                (-RAIL_X, AXLE_PIVOT[1], AXLE_PIVOT[2]),
                (-0.18, -0.90, 0.21),
                (0.0, -0.94, 0.205),
                (0.18, -0.90, 0.21),
                (RAIL_X, AXLE_PIVOT[1], AXLE_PIVOT[2]),
            ],
            0.018,
            "front_guard_loop",
        ),
        material=mats["frame"],
        name="front_guard", material_class_id="metal.paint_coated",
    )
    # Cross tubes (connect rails, add realism).
    for y, z, nm in [(-0.22, 0.30, "front_cross_tube"), (0.28, 0.355, "rear_cross_tube")]:
        barrow.visual(
            Cylinder(radius=0.016, length=0.68),
            origin=_barrow_origin(0.0, y, z, (0.0, math.pi / 2.0, 0.0)),
            material=mats["frame"],
            name=nm, material_class_id="metal.paint_coated",
        )
    # Bent tube legs from the rails down to the feet.
    for sx, idx in ((-1.0, 0), (1.0, 1)):
        leg_pts = [
            (sx * RAIL_X, 0.06, 0.33),
            (sx * RAIL_X, 0.30, 0.18),
            (sx * RAIL_X, 0.55, 0.05),
        ]
        barrow.visual(
            _barrow_tube_mesh(leg_pts, 0.016, f"support_leg_{idx}"),
            material=mats["frame_edge"],
            name=f"support_leg_{idx}", material_class_id="metal.blackened_gunmetal",
        )
        barrow.visual(
            Box((0.07, 0.055, 0.014)),
            origin=_barrow_origin(sx * RAIL_X, 0.55, 0.04),
            material=mats["frame_edge"],
            name=f"foot_pad_{idx}", material_class_id="rubber.smooth_plain",
        )
    _emit_front_struts(barrow, mats, style="tube")


def _emit_welded_flatbar(barrow, r, mats) -> None:
    reach = r.handle_reach_scale
    _emit_tub_bearer(barrow, mats)

    # Straight flat-bar rails: two segments (low tub run + rising handle run).
    for sx, idx in ((-1.0, 0), (1.0, 1)):
        _barrow_beam_yz(
            barrow,
            f"handle_rail_{idx}",
            (sx * RAIL_X, AXLE_PIVOT[1], AXLE_PIVOT[2]),
            (sx * RAIL_X, 0.34, 0.36),
            0.035,
            0.025,
            mats["frame"],
        )
        _barrow_beam_yz(
            barrow,
            f"handle_upper_{idx}",
            (sx * RAIL_X, 0.28, 0.35),
            (sx * RAIL_X, 1.48 * reach, 0.95),
            0.035,
            0.025,
            mats["frame"],
        )
        _grip_bands(barrow, mats, sx * RAIL_X, 1.52 * reach, 0.955)

    # Straight front guard bar + nose bars.
    barrow.visual(
        Box((0.62, 0.025, 0.040)),
        origin=_barrow_origin(0.0, -0.90, 0.21),
        material=mats["frame"],
        name="front_guard", material_class_id="metal.paint_coated",
    )
    for sx, idx in ((-1.0, 0), (1.0, 1)):
        _barrow_beam_yz(
            barrow,
            f"nose_bar_{idx}",
            (sx * RAIL_X, AXLE_PIVOT[1], AXLE_PIVOT[2]),
            (sx * RAIL_X, -0.90, 0.21),
            0.030,
            0.025,
            mats["frame"],
        )
    # Flat-bar cross members.
    for y, z, nm in [(-0.22, 0.31, "front_cross_bar"), (0.28, 0.35, "rear_cross_bar")]:
        barrow.visual(
            Box((0.62, 0.025, 0.025)),
            origin=_barrow_origin(0.0, y, z),
            material=mats["frame"],
            name=nm, material_class_id="metal.paint_coated",
        )
    # A-frame legs: front + rear diverging bars per side from a rail apex.
    for sx, idx in ((-1.0, 0), (1.0, 1)):
        apex = (sx * RAIL_X, 0.20, 0.325)
        _barrow_beam_yz(barrow, f"support_leg_{idx}", apex, (sx * RAIL_X, 0.02, 0.045), 0.030, 0.008, mats["frame_edge"])
        _barrow_beam_yz(barrow, f"aframe_rear_{idx}", apex, (sx * RAIL_X, 0.52, 0.045), 0.030, 0.008, mats["frame_edge"])
        barrow.visual(
            Box((0.038, 0.06, 0.010)),
            origin=_barrow_origin(sx * RAIL_X, 0.20, 0.305),
            material=mats["frame"],
            name=f"aframe_gusset_{idx}", material_class_id="metal.paint_coated",
        )
        for fy, pad_idx in ((0.02, idx), (0.52, idx + 2)):
            barrow.visual(
                Box((0.07, 0.055, 0.014)),
                origin=_barrow_origin(sx * RAIL_X, fy, 0.04),
                material=mats["frame_edge"],
                name=f"foot_pad_{pad_idx}", material_class_id="rubber.smooth_plain",
            )
    _emit_front_struts(barrow, mats, style="flatbar")


def _emit_wood_runner(barrow, r, mats) -> None:
    reach = r.handle_reach_scale
    _emit_tub_bearer(barrow, mats)

    rx = 0.30
    for sx, idx in ((-1.0, 0), (1.0, 1)):
        # Heavy wood runner: low front segment (on axle) + rising rear segment.
        _barrow_beam_yz(
            barrow,
            f"handle_rail_{idx}",
            (sx * rx, AXLE_PIVOT[1], AXLE_PIVOT[2]),
            (sx * rx, 0.40, 0.37),
            0.07,
            0.07,
            mats["wood"],
        )
        _barrow_beam_yz(
            barrow,
            f"handle_upper_{idx}",
            (sx * rx, 0.34, 0.36),
            (sx * rx, 1.42 * reach, 0.80),
            0.07,
            0.07,
            mats["wood"],
        )
        # Rubber-wrapped grip on the runner end.
        _barrow_beam_yz(
            barrow,
            f"grip_{idx}",
            (sx * rx, 1.22 * reach, 0.745),
            (sx * rx, 1.46 * reach, 0.815),
            0.088,
            0.088,
            mats["grip"],
        )
    # Wood legs from the low runner down to feet + foot cross bar.
    for sx, idx in ((-1.0, 0), (1.0, 1)):
        _barrow_beam_yz(
            barrow,
            f"support_leg_{idx}",
            (sx * rx, 0.30, 0.34),
            (sx * rx, 0.44, 0.05),
            0.07,
            0.07,
            mats["wood"],
        )
        barrow.visual(
            Box((0.145, 0.085, 0.045)),
            origin=_barrow_origin(sx * rx, 0.46, 0.042),
            material=mats["wood_grain"],
            name=f"foot_pad_{idx}", material_class_id="wood.walnut_dark",
        )
    barrow.visual(
        Box((0.68, 0.08, 0.045)),
        origin=_barrow_origin(0.0, 0.46, 0.05),
        material=mats["wood"],
        name="rear_foot_crossbar", material_class_id="wood.natural_generic",
    )
    # Cross ties across the runners at the tub region (redundant with bearer).
    for y, nm in ((-0.22, "front_cross_tie"), (0.28, "rear_cross_tie")):
        barrow.visual(
            Box((0.66, 0.07, 0.05)),
            origin=_barrow_origin(0.0, y, 0.33),
            material=mats["wood"],
            name=nm, material_class_id="wood.natural_generic",
        )
    _emit_front_struts(barrow, mats, style="wood")


def _emit_axle_brackets(pivot, mats, *, style: str) -> None:
    # Axle brackets (+ bolts / end caps) belong to the kinematic root together
    # with the through-axle: they are the fixed mounts carrying the captured
    # pin. The root frame is the world-at-rest frame, so they are authored in
    # world coordinates (no -AXLE_PIVOT rebase).
    if style == "triangular":
        plate_yz = [
            (-0.735, 0.185),
            (-0.505, 0.205),
            (-0.475, 0.318),
            (-0.630, 0.355),
            (-0.750, 0.292),
        ]
        for x, idx in ((-0.09, 0), (0.09, 1)):
            pivot.visual(
                mesh_from_geometry(
                    _triangular_plate_geometry(x, 0.018, plate_yz),
                    f"axle_bracket_{idx}",
                ),
                material=mats["frame"],
                name=f"axle_bracket_{idx}", material_class_id="metal.paint_coated",
            )
            _emit_bracket_bolts(pivot, mats, x, idx)
    elif style == "flatbar":
        for x, idx in ((-0.09, 0), (0.09, 1)):
            pivot.visual(
                Box((0.006, 0.150, 0.200)),
                origin=_origin(x, -0.575, 0.305),
                material=mats["frame"],
                name=f"axle_bracket_{idx}", material_class_id="metal.paint_coated",
            )
            _emit_bracket_bolts(pivot, mats, x, idx)
    else:  # fork (wood runner) — black steel fork plates + end caps
        for x, idx in ((-0.09, 0), (0.09, 1)):
            pivot.visual(
                Box((0.020, 0.125, 0.230)),
                origin=_origin(x, AXLE_PIVOT[1], 0.30),
                material=mats["frame_edge"],
                name=f"axle_bracket_{idx}", material_class_id="metal.blackened_gunmetal",
            )
            pivot.visual(
                Cylinder(radius=0.032, length=0.010),
                origin=_origin(
                    x * 1.9, AXLE_PIVOT[1], AXLE_PIVOT[2], (0.0, math.pi / 2.0, 0.0)
                ),
                material=mats["hardware"],
                name=f"axle_end_cap_{idx}", material_class_id="metal.blackened_gunmetal",
            )


def _emit_bracket_bolts(pivot, mats, x, idx) -> None:
    # Bolt heads straddle the (thin) bracket plate: length 0.024 with a small
    # 0.005 outward offset so they overlap the plate for both bracket styles.
    for y, z, rad, bolt_idx in [
        (-0.600, 0.250, 0.026, 0),
        (-0.560, 0.290, 0.015, 1),
        (-0.540, 0.230, 0.015, 2),
    ]:
        pivot.visual(
            Cylinder(radius=rad, length=0.024),
            origin=_origin(
                x + (0.005 if x > 0 else -0.005), y, z, (0.0, math.pi / 2.0, 0.0)
            ),
            material=mats["hardware"],
            name=f"bracket_bolt_{idx}_{bolt_idx}", material_class_id="metal.blackened_gunmetal",
        )


def _emit_front_struts(barrow, mats, *, style: str) -> None:
    # Diagonal brace from the front cross member (y=-0.22) down onto the axle
    # axis (y=-0.60, z=0.25); both ends land on real hardware so it never floats.
    top = (-0.22, 0.31)
    bot = (-0.60, 0.25)
    for sx, idx in ((-1.0, 0), (1.0, 1)):
        if style == "tube":
            barrow.visual(
                _barrow_tube_mesh(
                    [
                        (sx * 0.27, top[0], top[1]),
                        (sx * 0.27, -0.41, 0.28),
                        (sx * 0.27, bot[0], bot[1]),
                    ],
                    0.014,
                    f"front_strut_{idx}",
                ),
                material=mats["frame"],
                name=f"front_strut_{idx}", material_class_id="metal.paint_coated",
            )
        elif style == "flatbar":
            _barrow_beam_yz(
                barrow,
                f"front_strut_{idx}",
                (sx * 0.27, top[0], top[1]),
                (sx * 0.27, bot[0], bot[1]),
                0.025,
                0.006,
                mats["frame"],
            )
        else:  # wood
            _barrow_beam_yz(
                barrow,
                f"front_strut_{idx}",
                (sx * 0.27, top[0], top[1]),
                (sx * 0.27, bot[0], bot[1]),
                0.05,
                0.05,
                mats["wood"],
            )


def _triangular_plate_geometry(x_center, thickness, yz_points):
    geom = MeshGeometry()
    x0 = x_center - thickness * 0.5
    x1 = x_center + thickness * 0.5
    front = [geom.add_vertex(x0, y, z) for y, z in yz_points]
    back = [geom.add_vertex(x1, y, z) for y, z in yz_points]
    n = len(yz_points)
    for i in range(1, n - 1):
        geom.add_face(front[0], front[i], front[i + 1])
        geom.add_face(back[0], back[i + 1], back[i])
    for i in range(n):
        j = (i + 1) % n
        _add_quad(geom, front[i], front[j], back[j], back[i])
    return geom


_FRAME_BUILDERS = {
    "tube_rail": _emit_tube_rail,
    "welded_flatbar": _emit_welded_flatbar,
    "wood_runner": _emit_wood_runner,
}


# ---------------------------------------------------------------------------
# wheel_type slot (wheel part). All centred at the wheel-local origin (==
# AXLE_PIVOT); symmetry axis local X so the CONTINUOUS joint needs no rpy.
# Returns the list of hub-ish element names that the axle is captured through.
# ---------------------------------------------------------------------------
def _emit_pneumatic(wheel, r, mats) -> list[str]:
    ws = r.wheel_size_scale
    tire = TireGeometry(
        0.235 * ws,
        0.112,
        inner_radius=0.158 * ws,
        carcass=TireCarcass(belt_width_ratio=0.70, sidewall_bulge=0.08),
        tread=TireTread(style="block", depth=0.010, count=24, land_ratio=0.55),
        grooves=(
            TireGroove(center_offset=0.0, width=0.010, depth=0.004),
            TireGroove(center_offset=-0.030, width=0.006, depth=0.0025),
            TireGroove(center_offset=0.030, width=0.006, depth=0.0025),
        ),
        sidewall=TireSidewall(style="rounded", bulge=0.06),
        shoulder=TireShoulder(width=0.012, radius=0.004),
    )
    wheel.visual(mesh_from_geometry(tire, "rubber_tire"), material=mats["tire"], name="rubber_tire", material_class_id="rubber.directional_grooved")
    rim = WheelGeometry(
        0.154 * ws,
        0.082,
        rim=WheelRim(inner_radius=0.080 * ws, flange_height=0.012, flange_thickness=0.006, bead_seat_depth=0.005),
        hub=WheelHub(
            radius=0.048,
            width=0.074,
            cap_style="domed",
            bolt_pattern=BoltPattern(count=5, circle_diameter=0.062, hole_diameter=0.006),
        ),
        face=WheelFace(dish_depth=0.010, front_inset=0.004, rear_inset=0.004),
        spokes=WheelSpokes(style="split_y", count=5, thickness=0.006, window_radius=0.020),
        bore=WheelBore(style="round", diameter=0.044),
    )
    wheel.visual(mesh_from_geometry(rim, "metal_rim"), material=mats["rim"], name="metal_rim", material_class_id="metal.steel_galvanized")
    wheel.visual(
        Cylinder(radius=0.004, length=0.016),
        origin=_origin(0.063, 0.055, 0.145 * ws, (0.0, math.pi / 2.0, 0.0)),
        material=mats["hardware"],
        name="spin_marker", appearance_only=AppearanceOnlySpec(kind="overlay"),
    )
    return ["metal_rim"]


def _solid_disc_wheel_geometry(ws):
    profile = [
        (0.000, -0.0425),
        (0.215 * ws, -0.0425),
        (0.228 * ws, -0.038),
        (0.235 * ws, -0.028),
        (0.238 * ws, 0.000),
        (0.235 * ws, 0.028),
        (0.228 * ws, 0.038),
        (0.215 * ws, 0.0425),
        (0.000, 0.0425),
    ]
    geom = LatheGeometry(profile, segments=48)
    geom.rotate_y(math.pi / 2.0)
    return geom


def _emit_solid_disc(wheel, r, mats) -> list[str]:
    ws = r.wheel_size_scale
    wheel.visual(
        mesh_from_geometry(_solid_disc_wheel_geometry(ws), "solid_disc"),
        material=mats["tire"],
        name="solid_disc", material_class_id="rubber.smooth_plain",
    )
    wheel.visual(
        Cylinder(radius=0.050, length=0.092),
        origin=_origin(0.0, 0.0, 0.0, (0.0, math.pi / 2.0, 0.0)),
        material=mats["rim"],
        name="closed_hub", material_class_id="metal.steel_galvanized",
    )
    wheel.visual(
        Cylinder(radius=0.010, length=0.008),
        origin=_origin(0.042, 0.0, 0.160 * ws, (0.0, math.pi / 2.0, 0.0)),
        material=mats["marker"],
        name="spin_marker", appearance_only=AppearanceOnlySpec(kind="overlay"),
    )
    return ["solid_disc", "closed_hub"]


def _emit_wood_spoked(wheel, r, mats) -> list[str]:
    ws = r.wheel_size_scale
    tire = TireGeometry(
        0.235 * ws,
        0.092,
        inner_radius=0.170 * ws,
        carcass=TireCarcass(belt_width_ratio=0.66, sidewall_bulge=0.05),
        tread=TireTread(style="block", depth=0.010, count=20, land_ratio=0.55),
        grooves=(TireGroove(center_offset=0.0, width=0.008, depth=0.004),),
        sidewall=TireSidewall(style="rounded", bulge=0.05),
        shoulder=TireShoulder(width=0.010, radius=0.004),
    )
    wheel.visual(mesh_from_geometry(tire, "block_tread_tire"), material=mats["tire"], name="block_tread_tire", material_class_id="rubber.directional_grooved")
    rim = WheelGeometry(
        0.172 * ws,
        0.078,
        rim=WheelRim(inner_radius=0.105 * ws, flange_height=0.011, flange_thickness=0.005, bead_seat_depth=0.004),
        hub=WheelHub(
            radius=0.043,
            width=0.078,
            cap_style="domed",
            bolt_pattern=BoltPattern(count=6, circle_diameter=0.060, hole_diameter=0.006),
        ),
        face=WheelFace(dish_depth=0.010, front_inset=0.004, rear_inset=0.004),
        spokes=WheelSpokes(style="straight", count=8, thickness=0.010, window_radius=0.020),
        bore=WheelBore(style="round", diameter=0.052),
    )
    wheel.visual(mesh_from_geometry(rim, "wood_spoked_rim"), material=mats["rim"], name="wood_spoked_rim", material_class_id="wood.natural_generic")
    wheel.visual(
        Cylinder(radius=0.048, length=0.118),
        origin=_origin(0.0, 0.0, 0.0, (0.0, math.pi / 2.0, 0.0)),
        material=mats["frame_edge"],
        name="dark_hub_shell", material_class_id="metal.blackened_gunmetal",
    )
    wheel.visual(
        Sphere(0.018),
        origin=_origin(0.049, 0.0, 0.235 * ws),
        material=mats["marker"],
        name="spin_marker", appearance_only=AppearanceOnlySpec(kind="overlay"),
    )
    return ["wood_spoked_rim", "dark_hub_shell"]


_WHEEL_BUILDERS = {
    "pneumatic_steel_rim": _emit_pneumatic,
    "solid_disc": _emit_solid_disc,
    "wood_spoked_cart": _emit_wood_spoked,
}


# ---------------------------------------------------------------------------
# Build.
# ---------------------------------------------------------------------------
def build_single_wheelbarrow(
    config: SingleWheelbarrowConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(
        name=r.name,
        meta={"category": "Agricultural", "small_class": "Single-Wheelbarrow"},
        assets=assets,
    )
    mats = {
        key: model.material(f"swb_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in PALETTES[r.palette_style].items()
    }

    axle_pivot = model.part("wheel_axle_pivot")
    barrow = model.part("barrow")
    wheel = model.part("wheel")

    # The fixed through-axle and its brackets live on the kinematic root (the
    # captured pin both children articulate about); the frame builders then hang
    # the rails / bearer / struts that embrace them off the barrow.
    _emit_axle(axle_pivot, mats)
    _emit_axle_brackets(
        axle_pivot,
        mats,
        style={
            "tube_rail": "triangular",
            "welded_flatbar": "flatbar",
            "wood_runner": "fork",
        }[r.frame_build],
    )

    # Frame (emits bearer + rails/legs/struts the tub sits on), then the tub.
    _FRAME_BUILDERS[r.frame_build](barrow, r, mats)
    _TUB_BUILDERS[r.tub_body](barrow, r, mats)
    hub_elems = _WHEEL_BUILDERS[r.wheel_type](wheel, r, mats)

    model.articulation(
        "axle_pivot_to_barrow",
        ArticulationType.REVOLUTE,
        parent=axle_pivot,
        child=barrow,
        origin=_origin(*AXLE_PIVOT),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=34.0, velocity=1.0, lower=0.0, upper=r.body_tip_upper),
    )
    model.articulation(
        "axle_pivot_to_wheel",
        ArticulationType.CONTINUOUS,
        parent=axle_pivot,
        child=wheel,
        origin=_origin(*AXLE_PIVOT),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=12.0, velocity=25.0),
    )

    model.meta["slot_choices"] = slot_choices_for_config(r)
    model.meta["wheel_hub_elems"] = hub_elems
    return model


def build_seeded_single_wheelbarrow(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_single_wheelbarrow(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests.
# ---------------------------------------------------------------------------
def _tub_shell_elem(tub_body: TubBody) -> str:
    return "floor_plank_1" if tub_body == "wood_slat_box" else "tray_shell"


def _tire_elem(wheel_type: WheelType) -> str:
    return {
        "pneumatic_steel_rim": "rubber_tire",
        "solid_disc": "solid_disc",
        "wood_spoked_cart": "block_tread_tire",
    }[wheel_type]


def run_single_wheelbarrow_tests(
    object_model: ArticulatedObject,
    config: SingleWheelbarrowConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    axle_pivot = object_model.get_part("wheel_axle_pivot")
    barrow = object_model.get_part("barrow")
    wheel = object_model.get_part("wheel")
    body_tip = object_model.get_articulation("axle_pivot_to_barrow")
    wheel_spin = object_model.get_articulation("axle_pivot_to_wheel")

    # Captured-pin: the fixed axle (owned by the kinematic root) is captured
    # inside the rotating wheel hub/bore.
    hub_elems = list(object_model.meta.get("wheel_hub_elems", ()))
    for elem in hub_elems:
        ctx.allow_overlap(
            axle_pivot,
            wheel,
            elem_a="axle",
            elem_b=elem,
            reason=(
                "The fixed steel axle is intentionally captured inside the wheel "
                f"{elem}; this hidden fit supports the rotating wheel."
            ),
        )
    # The barrow's frame (rails, nose bars, axle brackets + bolts, front guard,
    # struts) embraces the root's fixed through-axle and tips about it. The root
    # carries only the axle, so a link-pair allowance is effectively scoped to
    # that pin.
    ctx.allow_overlap(
        axle_pivot,
        barrow,
        reason=(
            "The barrow frame (rails, axle brackets, guard, struts) embraces the "
            "fixed through-axle carried by the kinematic root and tips about it."
        ),
    )
    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.020)
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=64, ignore_fixed=True)

    # ---- Structure / identity. ----
    ctx.check(
        "small class is Single-Wheelbarrow",
        object_model.meta.get("small_class") == "Single-Wheelbarrow",
        details=f"meta={object_model.meta}",
    )
    ctx.check(
        "three parts: axle pivot root + tipping barrow + one spinning wheel",
        len(object_model.parts) == 3
        and body_tip.parent == "wheel_axle_pivot"
        and body_tip.child == "barrow"
        and wheel_spin.parent == "wheel_axle_pivot"
        and wheel_spin.child == "wheel",
        details=f"parts={[p.name for p in object_model.parts]}",
    )
    ctx.check(
        "kinematic root carries the fixed through-axle geometry",
        any(v.name == "axle" for v in axle_pivot.visuals)
        and all(v.name != "axle" for v in barrow.visuals),
        details=f"root visuals={[v.name for v in axle_pivot.visuals]}",
    )
    ctx.check(
        "front wheel joint is CONTINUOUS about the lateral axle",
        wheel_spin.articulation_type == ArticulationType.CONTINUOUS
        and abs(wheel_spin.axis[0]) > 0.99,
        details=f"type={wheel_spin.articulation_type}, axis={tuple(wheel_spin.axis)}",
    )
    ctx.check(
        "barrow body tips forward (REVOLUTE) around the wheel axle",
        body_tip.articulation_type == ArticulationType.REVOLUTE
        and abs(body_tip.axis[0]) > 0.99
        and body_tip.motion_limits.lower == 0.0
        and body_tip.motion_limits.upper >= 1.0,
        details=f"type={body_tip.articulation_type}, axis={tuple(body_tip.axis)}, limits={body_tip.motion_limits}",
    )

    # ---- Tub identity / proportions. ----
    if r.tub_body == "wood_slat_box":
        # No single wood element is both wide and long; check a full-width tie
        # (X footprint) and a side wall (Y footprint) together.
        tie = ctx.part_element_world_aabb(barrow, elem="floor_tie_1")
        wall = ctx.part_element_world_aabb(barrow, elem="side_0_slat_0")
        ctx.check(
            "wood_slat_box present with barrow-scale footprint",
            tie is not None
            and wall is not None
            and (tie[1][0] - tie[0][0]) > 0.40
            and (wall[1][1] - wall[0][1]) > 0.30,
            details=f"tie={tie}, wall={wall}",
        )
    else:
        tub_aabb = ctx.part_element_world_aabb(barrow, elem="tray_shell")
        ctx.check(
            f"tub_body '{r.tub_body}' present with barrow-scale footprint",
            tub_aabb is not None
            and (tub_aabb[1][0] - tub_aabb[0][0]) > 0.20
            and (tub_aabb[1][1] - tub_aabb[0][1]) > 0.30,
            details=f"tub_aabb={tub_aabb}",
        )

    # ---- Key frame + wheel visuals present. ----
    for nm in ("handle_rail_0", "handle_rail_1", "support_leg_0", "support_leg_1", "tub_bearer"):
        ctx.check(
            f"frame visual {nm} present",
            ctx.part_element_world_aabb(barrow, elem=nm) is not None,
            details=nm,
        )
    ctx.check(
        "fixed axle present on the kinematic root",
        ctx.part_element_world_aabb(axle_pivot, elem="axle") is not None,
        details="axle",
    )
    tire_elem = _tire_elem(r.wheel_type)
    ctx.check(
        f"wheel tyre/disc {tire_elem} present",
        ctx.part_element_world_aabb(wheel, elem=tire_elem) is not None,
        details=tire_elem,
    )

    # ---- wood_slat_box multiplicity ----
    if r.tub_body == "wood_slat_box":
        side0 = [v for v in barrow.visuals if v.name.startswith("side_0_slat_")]
        side1 = [v for v in barrow.visuals if v.name.startswith("side_1_slat_")]
        ctx.check(
            f"wood box has exactly N={r.side_slat_count} slat rows per side",
            len(side0) == r.side_slat_count and len(side1) == r.side_slat_count,
            details=f"side_0={len(side0)}, side_1={len(side1)}, N={r.side_slat_count}",
        )

    # ---- Wheel spin displaces the spin marker (targeted pose). ----
    def _center_yz(aabb):
        return None if aabb is None else ((aabb[0][1] + aabb[1][1]) * 0.5, (aabb[0][2] + aabb[1][2]) * 0.5)

    m0 = _center_yz(ctx.part_element_world_aabb(wheel, elem="spin_marker"))
    with ctx.pose({wheel_spin: 1.25}):
        m1 = _center_yz(ctx.part_element_world_aabb(wheel, elem="spin_marker"))
    ctx.check(
        "wheel spin moves the marker around the axle",
        m0 is not None and m1 is not None and (abs(m1[0] - m0[0]) > 0.03 or abs(m1[1] - m0[1]) > 0.03),
        details=f"rest={m0}, spun={m1}",
    )

    # ---- Body tip swings the whole barrow up/forward (targeted pose). ----
    def _center_xyz(aabb):
        return None if aabb is None else tuple((aabb[0][i] + aabb[1][i]) * 0.5 for i in range(3))

    g0 = _center_xyz(ctx.part_element_world_aabb(barrow, elem="grip_0"))
    with ctx.pose({body_tip: 0.65}):
        g1 = _center_xyz(ctx.part_element_world_aabb(barrow, elem="grip_0"))
    ctx.check(
        "body tip swings the barrow forward around the wheel",
        g0 is not None and g1 is not None and g1[2] > g0[2] + 0.4 and g1[1] < g0[1] - 0.2,
        details=f"rest={g0}, tipped={g1}",
    )

    # ---- slot_choices recorded (with N encoded). ----
    ctx.check(
        "slot_choices recorded with side_slat_count encoded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    return ctx.report()


__all__ = (
    "SingleWheelbarrowConfig",
    "ResolvedSingleWheelbarrowConfig",
    "build_single_wheelbarrow",
    "build_seeded_single_wheelbarrow",
    "config_from_seed",
    "resolve_config",
    "run_single_wheelbarrow_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
