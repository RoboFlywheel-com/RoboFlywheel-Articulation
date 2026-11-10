# SPDX-License-Identifier: Apache-2.0

"""Self-contained wearable badge / ID holder clip.

The rigid ``clip_body`` is the root.  One moving clamp member grips clothing
against it: three of the four ``clamp_build`` candidates hang a sprung metal jaw
on a real hinge pin (REVOLUTE about world X), the fourth slides a magnet backer
onto the body's guide pins (PRISMATIC about world Y).  One ``badge_connector``
hangs from the tail swivel and turns freely in the badge plane (CONTINUOUS about
world Y).

The object is laid out standing up and facing -Y: X is the clip width, Z is the
clip length (mouth at +Z, swivel tail at -Z) and the badge plane is the world XZ
plane, so the preview camera sees the clip face and the badge face at once.

``grip_build`` changes how the two clamping faces bite, ``swivel_build`` changes
the swivel hardware on both sides of the button, and ``connector_build`` changes
what hangs off it.  ``clamp_stage_count`` is the number of clamping-force
stations across the clip: torsion coil stations threaded on the hinge pin
(with the jaw barrel split into N+1 segments between them) or magnet pole
stations on the backer.

Every moving member is captured by real geometry at every pose: the jaw barrel
is a tube running on the pin with a 0.4 mm clearance, the magnet backer's
sleeves run on headed guide pins, and the connector's hub ring closes around the
swivel boss.  No source-replay import, no overlap allowance, no frozen motion.
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
    AxisInterface,
    Box,
    Cylinder,
    MotionLimits,
    Origin,
    TemplateDomain,
    TestContext,
    TestReport,
    TorusGeometry,
    component_slot,
    corner_case,
    mate_axes,
    mesh_from_cadquery,
    mesh_from_geometry,
    multiplicity_slot,
    register_interface_mate,
)

# The clip face, the badge face and the swivel all look down -Y.
__preview_front_axis__ = "-y"

ClampBuild = Literal["alligator_yoke", "ear_hinge_thumb", "bulldog_lever", "magnet_backer"]
GripBuild = Literal["serrated_bar", "discrete_teeth"]
SwivelBuild = Literal["post_boss", "bridge_mount"]
ConnectorBuild = Literal["perforated_strap", "slotted_strap", "card_frame", "ring_loop"]
PaletteStyle = Literal["chrome_vinyl", "nickel_smoke", "black_oxide", "brass_amber"]

CLAMP_BUILDS: tuple[ClampBuild, ...] = (
    "alligator_yoke",
    "ear_hinge_thumb",
    "bulldog_lever",
    "magnet_backer",
)
GRIP_BUILDS: tuple[GripBuild, ...] = ("serrated_bar", "discrete_teeth")
SWIVEL_BUILDS: tuple[SwivelBuild, ...] = ("post_boss", "bridge_mount")
CONNECTOR_BUILDS: tuple[ConnectorBuild, ...] = (
    "perforated_strap",
    "slotted_strap",
    "card_frame",
    "ring_loop",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "chrome_vinyl",
    "nickel_smoke",
    "black_oxide",
    "brass_amber",
)

TEMPLATE_DOMAIN = TemplateDomain(
    slots=(
        component_slot("clamp_build", CLAMP_BUILDS, role="clamp mechanism"),
        component_slot("grip_build", GRIP_BUILDS, role="grip face"),
        component_slot("swivel_build", SWIVEL_BUILDS, role="swivel mount"),
        component_slot("connector_build", CONNECTOR_BUILDS, role="badge connector"),
        multiplicity_slot(
            "clamp_stage_count",
            (1, 2, 3),
            role="clamping force stations",
            item_slot="clamp_build",
        ),
    )
)

PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "chrome_vinyl": {
        "metal": (0.80, 0.81, 0.79, 1.0),
        "dark": (0.29, 0.30, 0.31, 1.0),
        "accent": (0.16, 0.17, 0.19, 1.0),
        "panel": (0.78, 0.92, 1.00, 0.42),
    },
    "nickel_smoke": {
        "metal": (0.72, 0.73, 0.71, 1.0),
        "dark": (0.34, 0.35, 0.36, 1.0),
        "accent": (0.22, 0.24, 0.27, 1.0),
        "panel": (0.60, 0.64, 0.70, 0.55),
    },
    "black_oxide": {
        "metal": (0.30, 0.31, 0.33, 1.0),
        "dark": (0.14, 0.15, 0.16, 1.0),
        "accent": (0.62, 0.63, 0.64, 1.0),
        "panel": (0.20, 0.22, 0.25, 0.62),
    },
    "brass_amber": {
        "metal": (0.74, 0.61, 0.31, 1.0),
        "dark": (0.42, 0.34, 0.16, 1.0),
        "accent": (0.24, 0.21, 0.16, 1.0),
        "panel": (0.92, 0.80, 0.52, 0.48),
    },
}

# --- fixed sheet-metal stock, not diversity axes -----------------------------
PLATE_T = 0.0012  # stamped plate thickness
JAW_GAP = 0.0032  # clear gap between the two clamping faces when closed
CHEEK_T = 0.0020  # folded cheek / hinge ear wall thickness
PIN_R = 0.0018  # hinge pin radius
BARREL_RI = 0.0022  # jaw barrel bore: 0.4 mm running clearance on the pin
BARREL_RO = 0.0034
POST_R = 0.0032  # slim swivel post radius
BOSS_T = 0.0010  # swivel boss / receiver disc thickness
HINGE_FRONT = JAW_GAP + PLATE_T + 0.0028  # forward offset of the hinge axis
SLEEVE_RI = 0.0019  # magnet backer guide sleeve bore
SLEEVE_RO = 0.0032
GUIDE_R = 0.0016  # magnet guide pin radius
POLE_H = 0.0030  # magnet pole height, also the magnet clamping gap
BULLDOG_LEVER_REACH = 0.0078

_WIDTH_FACTOR: dict[str, float] = {
    "alligator_yoke": 1.00,
    "ear_hinge_thumb": 1.04,
    "bulldog_lever": 1.35,
    "magnet_backer": 1.15,
}
_LENGTH_FACTOR: dict[str, float] = {
    "alligator_yoke": 1.00,
    "ear_hinge_thumb": 0.94,
    "bulldog_lever": 0.78,
    "magnet_backer": 0.92,
}
_MOUTH_FRACTION: dict[str, float] = {
    "alligator_yoke": 0.44,
    "ear_hinge_thumb": 0.46,
    "bulldog_lever": 0.45,
    "magnet_backer": 0.50,
}
_CONNECTOR_FACTOR: dict[str, float] = {
    "perforated_strap": 1.00,
    "slotted_strap": 0.72,
    "card_frame": 1.00,
    "ring_loop": 0.42,
}


@dataclass(frozen=True)
class Config:
    clamp_build: ClampBuild = "alligator_yoke"
    grip_build: GripBuild = "serrated_bar"
    swivel_build: SwivelBuild = "post_boss"
    connector_build: ConnectorBuild = "perforated_strap"
    clamp_stage_count: int = 1
    clip_length_m: float | None = None
    clip_width_m: float | None = None
    jaw_open_rad: float | None = None
    connector_drop_m: float | None = None
    palette_style: PaletteStyle = "chrome_vinyl"
    name: str = "badge_id_holder_clip"


@dataclass(frozen=True)
class ResolvedConfig:
    clamp_build: ClampBuild
    grip_build: GripBuild
    swivel_build: SwivelBuild
    connector_build: ConnectorBuild
    clamp_stage_count: int
    palette_style: PaletteStyle
    palette: dict[str, tuple[float, float, float, float]]
    clip_length_m: float
    clip_width_m: float
    jaw_open_rad: float
    connector_drop_m: float
    body_width_m: float
    body_length_m: float
    mouth_z_m: float
    tail_z_m: float
    swivel_z_m: float
    grip_station_z_m: float
    grip_half_span_m: float
    grip_height_m: float
    hinge_front_m: float
    front_envelope_m: float
    swivel_post_len_m: float
    boss_radius_m: float
    swivel_point_y_m: float
    pin_span_m: float
    stage_pitch_m: float
    stage_tube_m: float
    stage_half_m: float
    clamp_travel_m: float
    guide_pin_len_m: float
    guide_station_m: float
    backer_width_m: float
    backer_length_m: float
    lever_width_m: float
    lever_offset_x_m: float
    lever_tail_z_m: float
    connector_len_m: float
    connector_width_m: float
    name: str


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(value)))


def config_from_seed(seed: int) -> Config:
    rng = random.Random(int(seed) ^ 0x5AD9_E17C)
    choices = TEMPLATE_DOMAIN.sample(rng)
    return Config(
        clamp_build=choices["clamp_build"],
        grip_build=choices["grip_build"],
        swivel_build=choices["swivel_build"],
        connector_build=choices["connector_build"],
        clamp_stage_count=choices["clamp_stage_count"],
        clip_length_m=round(rng.uniform(0.052, 0.086), 4),
        clip_width_m=round(rng.uniform(0.018, 0.034), 4),
        jaw_open_rad=round(rng.uniform(0.26, 0.50), 4),
        connector_drop_m=round(rng.uniform(0.058, 0.118), 4),
        palette_style=rng.choice(PALETTE_STYLES),
        name=f"badge_id_holder_clip_seed_{int(seed)}",
    )


def resolve_config(config: Config) -> ResolvedConfig:
    TEMPLATE_DOMAIN.validate(
        {
            "clamp_build": config.clamp_build,
            "grip_build": config.grip_build,
            "swivel_build": config.swivel_build,
            "connector_build": config.connector_build,
            "clamp_stage_count": config.clamp_stage_count,
        }
    )
    if config.palette_style not in PALETTES:
        raise ValueError(f"unsupported palette_style: {config.palette_style}")
    if config.clip_length_m is not None and not 0.052 <= float(config.clip_length_m) <= 0.086:
        raise ValueError("clip_length_m must be in [0.052, 0.086]")
    if config.clip_width_m is not None and not 0.018 <= float(config.clip_width_m) <= 0.034:
        raise ValueError("clip_width_m must be in [0.018, 0.034]")
    if config.jaw_open_rad is not None and not 0.26 <= float(config.jaw_open_rad) <= 0.50:
        raise ValueError("jaw_open_rad must be in [0.26, 0.50]")
    if config.connector_drop_m is not None and not 0.058 <= float(config.connector_drop_m) <= 0.118:
        raise ValueError("connector_drop_m must be in [0.058, 0.118]")

    length = (
        _clamp(config.clip_length_m, 0.052, 0.086) if config.clip_length_m is not None else 0.068
    )
    width = _clamp(config.clip_width_m, 0.018, 0.034) if config.clip_width_m is not None else 0.026
    open_rad = _clamp(config.jaw_open_rad, 0.26, 0.50) if config.jaw_open_rad is not None else 0.38
    drop = (
        _clamp(config.connector_drop_m, 0.058, 0.118)
        if config.connector_drop_m is not None
        else 0.085
    )

    clamp_build = config.clamp_build
    stages = int(config.clamp_stage_count)
    hinged = clamp_build != "magnet_backer"

    body_w = width * _WIDTH_FACTOR[clamp_build]
    body_l = length * _LENGTH_FACTOR[clamp_build]
    mouth_frac = _MOUTH_FRACTION[clamp_build]
    mouth_z = mouth_frac * body_l
    tail_z = -(1.0 - mouth_frac) * body_l

    boss_r = _clamp(0.15 * body_w, 0.0042, 0.0055)

    # Swivel station: as far down the tail as the plate allows, but always clear
    # of the hinge barrel envelope so the mount never touches the moving jaw.
    swivel_lo = tail_z + boss_r + 0.0014
    swivel_hi = -(BARREL_RO + 0.0008) - boss_r - 0.0018 if hinged else tail_z + 0.55 * abs(tail_z)
    swivel_target = tail_z + max(0.0090, 0.20 * body_l)
    swivel_z = _clamp(swivel_target, swivel_lo, max(swivel_hi, swivel_lo))

    if clamp_build == "bulldog_lever":
        envelope = HINGE_FRONT + BULLDOG_LEVER_REACH + 0.0022
    elif hinged:
        envelope = HINGE_FRONT + 0.0050
    else:
        envelope = 0.0026
    post_len = envelope + 0.0022
    swivel_point_y = -(post_len + BOSS_T)

    if hinged:
        pin_span = body_w - 2.0 * CHEEK_T - 0.0016
        grip_z = mouth_z - 0.0045
        grip_gap = JAW_GAP
    else:
        pin_span = body_w - 2.0 * CHEEK_T - 0.0016
        grip_z = 0.30 * body_l
        grip_gap = POLE_H
    pitch = pin_span / float(stages + 1)
    tube = _clamp(0.22 * pitch, 0.0005, 0.0013)
    stage_half = tube + 0.0003

    travel = 0.0026 + 0.0034 * (open_rad - 0.26) / (0.50 - 0.26)
    guide_pin_len = 0.0105 + travel
    backer_w = 0.80 * body_w
    backer_l = 0.72 * body_l
    guide_station = 0.30 * backer_l

    lever_w = min(
        _clamp(0.26 * body_w, 0.005, 0.012),
        max(0.0040, body_w * 0.5 - boss_r - 0.0030),
    )
    lever_x = boss_r + 0.0012 + lever_w * 0.5
    lever_tail = -min(
        0.0135,
        0.85
        * max(
            0.004,
            ((HINGE_FRONT + BULLDOG_LEVER_REACH) * math.cos(open_rad) - 0.0010)
            / max(1e-6, math.sin(open_rad)),
        ),
    )

    # Both source straps are about as wide as the clip they hang from
    # (002: 24 mm strap on a 30 mm body; 001: 20 mm strap on an 18 mm body).
    connector_len = drop * _CONNECTOR_FACTOR[config.connector_build]
    connector_w = max(_clamp(0.82 * body_w, 0.016, 0.032), 2.0 * boss_r + 0.0090)

    return ResolvedConfig(
        clamp_build=clamp_build,
        grip_build=config.grip_build,
        swivel_build=config.swivel_build,
        connector_build=config.connector_build,
        clamp_stage_count=stages,
        palette_style=config.palette_style,
        palette=dict(PALETTES[config.palette_style]),
        clip_length_m=length,
        clip_width_m=width,
        jaw_open_rad=open_rad,
        connector_drop_m=drop,
        body_width_m=body_w,
        body_length_m=body_l,
        mouth_z_m=mouth_z,
        tail_z_m=tail_z,
        swivel_z_m=swivel_z,
        grip_station_z_m=grip_z,
        grip_half_span_m=(
            body_w * 0.5 - 0.0045 if hinged else min(body_w * 0.5 - 0.0045, 0.40 * body_w - 0.0028)
        ),
        grip_height_m=(grip_gap - 0.0008) * 0.5,
        hinge_front_m=HINGE_FRONT,
        front_envelope_m=envelope,
        swivel_post_len_m=post_len,
        boss_radius_m=boss_r,
        swivel_point_y_m=swivel_point_y,
        pin_span_m=pin_span,
        stage_pitch_m=pitch,
        stage_tube_m=tube,
        stage_half_m=stage_half,
        clamp_travel_m=travel,
        guide_pin_len_m=guide_pin_len,
        guide_station_m=guide_station,
        backer_width_m=backer_w,
        backer_length_m=backer_l,
        lever_width_m=lever_w,
        lever_offset_x_m=lever_x,
        lever_tail_z_m=lever_tail,
        connector_len_m=connector_len,
        connector_width_m=connector_w,
        name=config.name,
    )


def slot_choices_for_config(config: Config | ResolvedConfig) -> tuple[tuple[str, object], ...]:
    return (
        ("clamp_build", config.clamp_build),
        ("grip_build", config.grip_build),
        ("swivel_build", config.swivel_build),
        ("connector_build", config.connector_build),
        ("clamp_stage_count", config.clamp_stage_count),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, object], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# --- geometry helpers -------------------------------------------------------
def _materials(model: ArticulatedObject, r: ResolvedConfig) -> dict[str, str]:
    mats: dict[str, str] = {}
    for key, rgba in r.palette.items():
        model.material(f"bidhc_{r.palette_style}_{key}", rgba=rgba)
        mats[key] = f"bidhc_{r.palette_style}_{key}"
    return mats


def _rounded_plate(
    span_x: float,
    span_y: float,
    thickness: float,
    *,
    cx: float = 0.0,
    cy: float = 0.0,
    radius: float = 0.0020,
) -> cq.Workplane:
    """Thin plate in the CQ XY plane extruded up +Z, later stood into world XZ."""

    wp = cq.Workplane("XY").center(cx, cy).rect(span_x, span_y).extrude(thickness)
    fillet_r = min(radius, span_x * 0.45, span_y * 0.45)
    if fillet_r > 1e-5:
        wp = wp.edges("|Z").fillet(fillet_r)
    return wp


def _polyline_plate(points, thickness: float, *, radius: float = 0.0015) -> cq.Workplane:
    wp = cq.Workplane("XY").polyline(list(points)).close().extrude(thickness)
    if radius > 1e-5:
        try:
            wp = wp.edges("|Z").fillet(radius)
        except Exception:  # noqa: BLE001 - degenerate taper, keep the sharp plate
            pass
    return wp


def _cut_circles(wp: cq.Workplane, thickness: float, points, radius: float) -> cq.Workplane:
    points = [tuple(p) for p in points]
    if not points or radius <= 1e-5:
        return wp
    cutter = (
        cq.Workplane("XY")
        .pushPoints(points)
        .circle(radius)
        .extrude(thickness * 3.0)
        .translate((0.0, 0.0, -thickness))
    )
    return wp.cut(cutter)


def _cut_rects(wp: cq.Workplane, thickness: float, points, sx: float, sy: float) -> cq.Workplane:
    points = [tuple(p) for p in points]
    if not points or sx <= 1e-5 or sy <= 1e-5:
        return wp
    cutter = (
        cq.Workplane("XY")
        .pushPoints(points)
        .rect(sx, sy)
        .extrude(thickness * 3.0)
        .translate((0.0, 0.0, -thickness))
    )
    return wp.cut(cutter)


def _cut_slot(
    wp: cq.Workplane, thickness: float, cx: float, cy: float, length: float, width: float
) -> cq.Workplane:
    if length <= width * 1.05 or width <= 1e-5:
        return _cut_circles(wp, thickness, [(cx, cy)], max(width * 0.5, 1e-4))
    cutter = (
        cq.Workplane("XY")
        .center(cx, cy)
        .slot2D(length, width, 90.0)
        .extrude(thickness * 3.0)
        .translate((0.0, 0.0, -thickness))
    )
    return wp.cut(cutter)


def _tube(outer: float, inner: float, length: float) -> cq.Workplane:
    return cq.Workplane("XY").circle(outer).circle(inner).extrude(length)


def _tooth_bar(count: int, pitch: float, tooth_w: float, depth: float, height: float):
    """One welded serrated bar: a backing strip with rectangular teeth on it."""

    total = (count - 1) * pitch + tooth_w
    wp = cq.Workplane("XY").rect(total + 0.0008, depth).extrude(height * 0.34)
    teeth = (
        cq.Workplane("XY")
        .pushPoints([(-total / 2.0 + tooth_w / 2.0 + i * pitch, 0.0) for i in range(count)])
        .rect(tooth_w, depth * 0.82)
        .extrude(height)
    )
    return wp.union(teeth)


def _local_origin(origin: Origin | None, offset: tuple[float, float, float]) -> Origin:
    base = origin or Origin()
    return Origin(
        xyz=tuple(value - shift for value, shift in zip(base.xyz, offset)),
        rpy=base.rpy,
    )


_ZERO_OFFSET = (0.0, 0.0, 0.0)


def _plate_visual(
    part,
    offset,
    wp,
    *,
    y_near: float,
    material: str,
    name: str,
    tolerance=0.00035,
):
    """Stand a CQ XY plate into the world XZ plane; solid spans y in [y_near-t, y_near]."""

    part.visual(
        mesh_from_cadquery(wp, name, tolerance=tolerance),
        origin=_local_origin(
            Origin(xyz=(0.0, y_near, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
            offset,
        ),
        material=material,
        name=name, material_class_id="metal.patterned_sheet_panel",
    )


def _face_visual(
    part, offset, wp, *, y_face: float, direction: float, z: float, material: str, name: str
):
    """Place a CQ XY solid on a clamping face; +Z of the solid grows along `direction`."""

    if direction < 0.0:
        origin = Origin(xyz=(0.0, y_face, z), rpy=(math.pi / 2.0, 0.0, 0.0))
    else:
        origin = Origin(xyz=(0.0, y_face, z), rpy=(-math.pi / 2.0, 0.0, 0.0))
    part.visual(
        mesh_from_cadquery(wp, name, tolerance=0.00030),
        origin=_local_origin(origin, offset),
        material=material,
        name=name, material_class_id="metal.blackened_gunmetal",
    )


def _tube_along_x(
    part,
    offset,
    *,
    x_start: float,
    length: float,
    y: float,
    z: float,
    outer: float,
    inner: float,
    material: str,
    name: str,
):
    part.visual(
        mesh_from_cadquery(_tube(outer, inner, length), name, tolerance=0.00025),
        origin=_local_origin(
            Origin(xyz=(x_start, y, z), rpy=(0.0, math.pi / 2.0, 0.0)), offset
        ),
        material=material,
        name=name, material_class_id="metal.stainless_matte",
    )


def _cyl_along_y(
    part,
    offset,
    *,
    radius: float,
    y0: float,
    y1: float,
    x: float,
    z: float,
    material: str,
    name: str,
):
    part.visual(
        Cylinder(radius=radius, length=abs(y1 - y0)),
        origin=_local_origin(
            Origin(
                xyz=(x, (y0 + y1) * 0.5, z), rpy=(math.pi / 2.0, 0.0, 0.0)
            ),
            offset,
        ),
        material=material,
        name=name, material_class_id="metal.generic_plain",
    )


def _cyl_along_x(
    part,
    offset,
    *,
    radius: float,
    length: float,
    x: float,
    y: float,
    z: float,
    material: str,
    name: str,
):
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=_local_origin(
            Origin(xyz=(x, y, z), rpy=(0.0, math.pi / 2.0, 0.0)), offset
        ),
        material=material,
        name=name, material_class_id="metal.generic_plain",
    )


def _stage_stations(r: ResolvedConfig) -> list[float]:
    span = r.pin_span_m
    return [-span * 0.5 + r.stage_pitch_m * (k + 1) for k in range(r.clamp_stage_count)]


def _barrel_segments(r: ResolvedConfig) -> list[tuple[float, float]]:
    span = r.pin_span_m
    edges = [-span * 0.5]
    for station in _stage_stations(r):
        edges.append(station - r.stage_half_m)
        edges.append(station + r.stage_half_m)
    edges.append(span * 0.5)
    return [(edges[2 * i], edges[2 * i + 1]) for i in range(len(edges) // 2)]


# --- clamp candidates -------------------------------------------------------
def _hinge_core(
    r: ResolvedConfig, mats, body, body_offset, jaw, jaw_offset, tag: str
) -> None:
    """Pin + N torsion coil stations on the body, N+1 barrel/wrap segments on the jaw."""

    hinge_y = -r.hinge_front_m
    pin_len = r.body_width_m - 2.0 * CHEEK_T + 0.0014
    _cyl_along_x(
        body,
        body_offset,
        radius=PIN_R,
        length=pin_len,
        x=0.0,
        y=hinge_y,
        z=0.0,
        material=mats["dark"],
        name=f"clamp_build__{tag}__hinge_pin",
    )
    coil_r = PIN_R + r.stage_tube_m - 0.0002
    for index, station in enumerate(_stage_stations(r)):
        body.visual(
            mesh_from_geometry(
                TorusGeometry(coil_r, r.stage_tube_m, radial_segments=8, tubular_segments=18),
                f"clamp_build__{tag}__torsion_coil_{index}",
            ),
            origin=_local_origin(
                Origin(
                    xyz=(station, hinge_y, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)
                ),
                body_offset,
            ),
            material=mats["dark"],
            name=f"clamp_build__{tag}__stage_{index}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"chrome_vinyl", "nickel_smoke", "black_oxide"} else "metal.brass_aged"),
        )

    wrap_top = 0.35 * r.mouth_z_m
    wrap_z0 = -0.0015
    for index, (x0, x1) in enumerate(_barrel_segments(r)):
        seg_len = x1 - x0
        if seg_len <= 0.0004:
            continue
        _tube_along_x(
            jaw,
            jaw_offset,
            x_start=x0,
            length=seg_len,
            y=hinge_y,
            z=0.0,
            outer=BARREL_RO,
            inner=BARREL_RI,
            material=mats["metal"],
            name=f"clamp_build__{tag}__barrel_segment_{index}",
        )
        jaw.visual(
            Box((seg_len, 0.0018, wrap_top - wrap_z0)),
            origin=_local_origin(
                Origin(
                    xyz=(
                        (x0 + x1) * 0.5,
                        hinge_y + 0.0031,
                        (wrap_top + wrap_z0) * 0.5,
                    )
                ),
                jaw_offset,
            ),
            material=mats["metal"],
            name=f"clamp_build__{tag}__barrel_wrap_{index}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"chrome_vinyl", "nickel_smoke", "black_oxide"} else "metal.brass_aged"),
        )


def _body_back_plate(
    r: ResolvedConfig, mats, body, body_offset, tag: str, *, hole: bool
) -> None:
    span_z = r.mouth_z_m - r.tail_z_m
    wp = _rounded_plate(
        r.body_width_m,
        span_z,
        PLATE_T,
        cy=(r.mouth_z_m + r.tail_z_m) * 0.5,
        radius=min(0.0035, r.body_width_m * 0.22),
    )
    if hole:
        wp = _cut_circles(wp, PLATE_T, [(0.0, r.mouth_z_m * 0.62)], 0.0022)
    _plate_visual(
        body,
        body_offset,
        wp,
        y_near=PLATE_T,
        material=mats["metal"],
        name=f"clamp_build__{tag}__body_plate",
    )


def _jaw_plate(r: ResolvedConfig, mats, jaw, jaw_offset, tag: str, wp) -> None:
    _plate_visual(
        jaw,
        jaw_offset,
        wp,
        y_near=-JAW_GAP,
        material=mats["metal"],
        name=f"clamp_build__{tag}__jaw_plate",
    )


def _clamp_build_alligator_yoke_build(
    model, r, mats, body, body_offset, jaw, jaw_offset
) -> None:
    tag = "alligator_yoke"
    hinge_y = -r.hinge_front_m
    _body_back_plate(r, mats, body, body_offset, tag, hole=False)

    cheek_x = r.body_width_m * 0.5 - CHEEK_T * 0.5
    cheek_y0, cheek_y1 = hinge_y - 0.0012, 0.0006
    cheek_z0, cheek_z1 = -0.0060, 0.0100
    for index, sign in enumerate((-1.0, 1.0)):
        body.visual(
            Box((CHEEK_T, cheek_y1 - cheek_y0, cheek_z1 - cheek_z0)),
            origin=_local_origin(
                Origin(
                    xyz=(
                        sign * cheek_x,
                        (cheek_y0 + cheek_y1) * 0.5,
                        (cheek_z0 + cheek_z1) * 0.5,
                    )
                ),
                body_offset,
            ),
            material=mats["metal"],
            name=f"clamp_build__{tag}__side_cheek_{index}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"chrome_vinyl", "nickel_smoke", "black_oxide"} else "metal.brass_aged"),
        )
        _cyl_along_x(
            body,
            body_offset,
            radius=0.0028,
            length=0.0007,
            x=sign * (r.body_width_m * 0.5 - 0.0002),
            y=hinge_y,
            z=0.0,
            material=mats["accent"],
            name=f"clamp_build__{tag}__cheek_eye_{index}",
        )

    _hinge_core(r, mats, body, body_offset, jaw, jaw_offset, tag)

    half_w = r.body_width_m * 0.5 - 0.0030
    wp = _polyline_plate(
        [
            (-half_w * 0.74, 0.0006),
            (half_w * 0.74, 0.0006),
            (half_w, r.mouth_z_m * 0.45),
            (half_w, r.mouth_z_m),
            (-half_w, r.mouth_z_m),
            (-half_w, r.mouth_z_m * 0.45),
        ],
        PLATE_T,
        radius=0.0012,
    )
    wp = _cut_circles(wp, PLATE_T, [(0.0, r.mouth_z_m * 0.60)], 0.0020)
    _jaw_plate(r, mats, jaw, jaw_offset, tag, wp)

    fold_z0 = r.mouth_z_m - 0.0020
    fold_z1 = r.mouth_z_m + 0.0012
    jaw.visual(
        Box((2.0 * half_w * 0.9, 0.0028, fold_z1 - fold_z0)),
        origin=_local_origin(
            Origin(xyz=(0.0, -JAW_GAP - 0.0016, (fold_z0 + fold_z1) * 0.5)),
            jaw_offset,
        ),
        material=mats["metal"],
        name=f"clamp_build__{tag}__front_fold", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"chrome_vinyl", "nickel_smoke", "black_oxide"} else "metal.brass_aged"),
    )
    jaw.visual(
        Box((2.0 * half_w * 0.8, 0.0016, 0.0055)),
        origin=_local_origin(
            Origin(
                xyz=(0.0, -JAW_GAP - 0.0034, r.mouth_z_m + 0.0032),
                rpy=(0.55, 0.0, 0.0),
            ),
            jaw_offset,
        ),
        material=mats["metal"],
        name=f"clamp_build__{tag}__front_blade", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"chrome_vinyl", "nickel_smoke", "black_oxide"} else "metal.brass_aged"),
    )


def _clamp_build_ear_hinge_thumb_build(
    model, r, mats, body, body_offset, jaw, jaw_offset
) -> None:
    tag = "ear_hinge_thumb"
    hinge_y = -r.hinge_front_m
    _body_back_plate(r, mats, body, body_offset, tag, hole=True)

    rail_x = r.body_width_m * 0.5 - 0.0011
    rail_y0, rail_y1 = -0.0035, 0.0006
    rail_z0, rail_z1 = -0.0040, r.mouth_z_m - 0.0020
    ear_y0, ear_y1 = hinge_y - 0.0012, 0.0006
    for index, sign in enumerate((-1.0, 1.0)):
        body.visual(
            Box((0.0022, rail_y1 - rail_y0, rail_z1 - rail_z0)),
            origin=_local_origin(
                Origin(
                    xyz=(
                        sign * rail_x,
                        (rail_y0 + rail_y1) * 0.5,
                        (rail_z0 + rail_z1) * 0.5,
                    )
                ),
                body_offset,
            ),
            material=mats["metal"],
            name=f"clamp_build__{tag}__side_rail_{index}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"chrome_vinyl", "nickel_smoke", "black_oxide"} else "metal.brass_aged"),
        )
        body.visual(
            Box((0.0018, ear_y1 - ear_y0, 0.0100)),
            origin=_local_origin(
                Origin(
                    xyz=(
                        sign * (r.body_width_m * 0.5 - 0.0009),
                        (ear_y0 + ear_y1) * 0.5,
                        0.0012,
                    )
                ),
                body_offset,
            ),
            material=mats["metal"],
            name=f"clamp_build__{tag}__hinge_ear_{index}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"chrome_vinyl", "nickel_smoke", "black_oxide"} else "metal.brass_aged"),
        )
        _cyl_along_x(
            body,
            body_offset,
            radius=0.0026,
            length=0.0008,
            x=sign * (r.body_width_m * 0.5 - 0.0001),
            y=hinge_y,
            z=0.0,
            material=mats["accent"],
            name=f"clamp_build__{tag}__ear_rivet_{index}",
        )

    _hinge_core(r, mats, body, body_offset, jaw, jaw_offset, tag)

    half_w = r.body_width_m * 0.5 - 0.0030
    wp = _rounded_plate(
        2.0 * half_w,
        r.mouth_z_m - 0.0006,
        PLATE_T,
        cy=(r.mouth_z_m + 0.0006) * 0.5,
        radius=0.0016,
    )
    _jaw_plate(r, mats, jaw, jaw_offset, tag, wp)

    pad_z = r.mouth_z_m * 0.55
    jaw.visual(
        Box((2.0 * half_w * 0.78, 0.0010, r.mouth_z_m * 0.30)),
        origin=_local_origin(
            Origin(xyz=(0.0, -JAW_GAP - PLATE_T - 0.0005, pad_z)), jaw_offset
        ),
        material=mats["metal"],
        name=f"clamp_build__{tag}__thumb_pad", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"chrome_vinyl", "nickel_smoke", "black_oxide"} else "metal.brass_aged"),
    )
    _cyl_along_y(
        jaw,
        jaw_offset,
        radius=min(0.0042, half_w * 0.55),
        y0=-JAW_GAP - PLATE_T - 0.0020,
        y1=-JAW_GAP - PLATE_T - 0.0008,
        x=0.0,
        z=pad_z,
        material=mats["accent"],
        name=f"clamp_build__{tag}__thumb_rivet",
    )


def _clamp_build_bulldog_lever_build(
    model, r, mats, body, body_offset, jaw, jaw_offset
) -> None:
    tag = "bulldog_lever"
    hinge_y = -r.hinge_front_m
    _body_back_plate(r, mats, body, body_offset, tag, hole=False)

    cheek_x = r.body_width_m * 0.5 - CHEEK_T * 0.5
    cheek_y0, cheek_y1 = hinge_y - 0.0012, 0.0006
    cheek_z0, cheek_z1 = -0.0050, 0.0080
    for index, sign in enumerate((-1.0, 1.0)):
        body.visual(
            Box((CHEEK_T, cheek_y1 - cheek_y0, cheek_z1 - cheek_z0)),
            origin=_local_origin(
                Origin(
                    xyz=(
                        sign * cheek_x,
                        (cheek_y0 + cheek_y1) * 0.5,
                        (cheek_z0 + cheek_z1) * 0.5,
                    )
                ),
                body_offset,
            ),
            material=mats["metal"],
            name=f"clamp_build__{tag}__side_cheek_{index}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"chrome_vinyl", "nickel_smoke", "black_oxide"} else "metal.brass_aged"),
        )

    _hinge_core(r, mats, body, body_offset, jaw, jaw_offset, tag)

    half_w = r.body_width_m * 0.5 - 0.0030
    wp = _rounded_plate(
        2.0 * half_w,
        r.mouth_z_m - 0.0006,
        PLATE_T,
        cy=(r.mouth_z_m + 0.0006) * 0.5,
        radius=0.0026,
    )
    wp = _cut_circles(wp, PLATE_T, [(0.0, r.mouth_z_m * 0.58)], 0.0024)
    _jaw_plate(r, mats, jaw, jaw_offset, tag, wp)

    jaw.visual(
        Box((2.0 * half_w * 0.86, 0.0022, 0.0030)),
        origin=_local_origin(
            Origin(xyz=(0.0, -JAW_GAP - 0.0013, r.mouth_z_m - 0.0018)),
            jaw_offset,
        ),
        material=mats["metal"],
        name=f"clamp_build__{tag}__front_fold", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"chrome_vinyl", "nickel_smoke", "black_oxide"} else "metal.brass_aged"),
    )

    lever_w = r.lever_width_m
    base_tail = max(r.lever_tail_z_m * 0.45, -0.0060)
    tip_tail = r.lever_tail_z_m
    tip_y = hinge_y - BULLDOG_LEVER_REACH
    root_y = hinge_y + 0.0008
    for index, sign in enumerate((-1.0, 1.0)):
        x = sign * r.lever_offset_x_m
        for local_name, p0, p1 in (
            (f"clamp_build__{tag}__lever_root_{index}", (0.0030, root_y), (base_tail, root_y)),
            (f"clamp_build__{tag}__finger_lever_{index}", (base_tail, root_y), (tip_tail, tip_y)),
        ):
            dz = p1[0] - p0[0]
            dy = p1[1] - p0[1]
            length = math.hypot(dz, dy)
            theta = math.atan2(-dy, dz)
            jaw.visual(
                Box((lever_w, 0.0016, length + 0.0012)),
                origin=_local_origin(
                    Origin(
                        xyz=(x, (p0[1] + p1[1]) * 0.5, (p0[0] + p1[0]) * 0.5),
                        rpy=(theta, 0.0, 0.0),
                    ),
                    jaw_offset,
                ),
                material=mats["metal"],
                name=local_name, material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"chrome_vinyl", "nickel_smoke", "black_oxide"} else "metal.brass_aged"),
            )


def _clamp_build_magnet_backer_build(
    model, r, mats, body, body_offset, backer, backer_offset
) -> None:
    tag = "magnet_backer"
    _body_back_plate(r, mats, body, body_offset, tag, hole=False)

    backer_w = r.backer_width_m
    backer_l = r.backer_length_m
    backer_front = PLATE_T + POLE_H
    pin_top = PLATE_T + r.guide_pin_len_m

    for index, sign in enumerate((-1.0, 1.0)):
        _cyl_along_y(
            body,
            body_offset,
            radius=GUIDE_R,
            y0=PLATE_T * 0.4,
            y1=pin_top,
            x=0.0,
            z=sign * r.guide_station_m,
            material=mats["dark"],
            name=f"clamp_build__{tag}__guide_pin_{index}",
        )
        _cyl_along_y(
            body,
            body_offset,
            radius=SLEEVE_RI + 0.0007,
            y0=pin_top - 0.0010,
            y1=pin_top,
            x=0.0,
            z=sign * r.guide_station_m,
            material=mats["accent"],
            name=f"clamp_build__{tag}__guide_head_{index}",
        )

    wp = _rounded_plate(backer_w, backer_l, 0.0018, radius=0.0030)
    wp = _cut_circles(
        wp,
        0.0018,
        [(0.0, r.guide_station_m), (0.0, -r.guide_station_m)],
        SLEEVE_RI,
    )
    backer.visual(
        mesh_from_cadquery(wp, f"clamp_build__{tag}__backer_plate", tolerance=0.00035),
        origin=_local_origin(
            Origin(
                xyz=(0.0, backer_front + 0.0018, 0.0),
                rpy=(math.pi / 2.0, 0.0, 0.0),
            ),
            backer_offset,
        ),
        material=mats["metal"],
        name=f"clamp_build__{tag}__backer_plate", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"chrome_vinyl", "nickel_smoke", "black_oxide"} else "metal.brass_aged"),
    )
    for index, sign in enumerate((-1.0, 1.0)):
        backer.visual(
            mesh_from_cadquery(
                _tube(SLEEVE_RO, SLEEVE_RI, 0.0055),
                f"clamp_build__{tag}__guide_sleeve_{index}",
                tolerance=0.00025,
            ),
            origin=_local_origin(
                Origin(
                    xyz=(0.0, backer_front + 0.0055, sign * r.guide_station_m),
                    rpy=(math.pi / 2.0, 0.0, 0.0),
                ),
                backer_offset,
            ),
            material=mats["metal"],
            name=f"clamp_build__{tag}__guide_sleeve_{index}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"chrome_vinyl", "nickel_smoke", "black_oxide"} else "metal.brass_aged"),
        )

    stages = r.clamp_stage_count
    pole_span = backer_w * 0.55
    pole_r = min(0.0044, max(0.0016, pole_span / max(1, stages) * 0.42))
    for index in range(stages):
        x = 0.0 if stages == 1 else -pole_span * 0.5 + pole_span * index / (stages - 1)
        _cyl_along_y(
            backer,
            backer_offset,
            radius=pole_r,
            y0=PLATE_T + 0.0008,
            y1=backer_front + 0.0008,
            x=x,
            z=0.0,
            material=mats["accent"],
            name=f"clamp_build__{tag}__stage_{index}",
        )
        _cyl_along_y(
            body,
            body_offset,
            radius=pole_r * 1.15,
            y0=PLATE_T * 0.4,
            y1=PLATE_T + 0.0004,
            x=x,
            z=0.0,
            material=mats["dark"],
            name=f"clamp_build__{tag}__pole_seat_{index}",
        )


_CLAMP_BUILDERS = {
    "alligator_yoke": _clamp_build_alligator_yoke_build,
    "ear_hinge_thumb": _clamp_build_ear_hinge_thumb_build,
    "bulldog_lever": _clamp_build_bulldog_lever_build,
    "magnet_backer": _clamp_build_magnet_backer_build,
}


# --- grip candidates --------------------------------------------------------
def _grip_mounts(
    r: ResolvedConfig,
) -> tuple[tuple[float, float, float], tuple[float, float, float]]:
    """((body_face_y, body_dir, body_far_y), (jaw_face_y, jaw_dir, jaw_far_y))."""

    if r.clamp_build == "magnet_backer":
        backer_front = PLATE_T + POLE_H
        return (
            (PLATE_T, 1.0, 0.0),
            (backer_front, -1.0, backer_front + 0.0018),
        )
    return (
        (0.0, -1.0, PLATE_T),
        (-JAW_GAP, 1.0, -JAW_GAP - PLATE_T),
    )


def _grip_build_serrated_bar_build(r, mats, part, offset, mount, side: str) -> None:
    face_y, direction, _far_y = mount
    span = 2.0 * r.grip_half_span_m
    count = int(_clamp(span / 0.0042, 4, 9))
    tooth_w = span / (count * 1.9)
    pitch = (span - tooth_w) / max(1, count - 1)
    height = max(0.0006, r.grip_height_m)
    wp = _tooth_bar(count, pitch, tooth_w, 0.0030, height)
    _face_visual(
        part,
        offset,
        wp,
        y_face=face_y - direction * 0.0003,
        direction=direction,
        z=r.grip_station_z_m,
        material=mats["dark"],
        name=f"grip_build__serrated_bar__{side}_tooth_bar",
    )


def _grip_build_discrete_teeth_build(r, mats, part, offset, mount, side: str) -> None:
    face_y, direction, far_y = mount
    span = 2.0 * r.grip_half_span_m
    count = int(_clamp(span / 0.0060, 3, 6))
    tooth_w = span / (count * 2.1)
    pitch = (span - tooth_w) / max(1, count - 1)
    height = max(0.0006, r.grip_height_m)
    for index in range(count):
        x = -span * 0.5 + tooth_w * 0.5 + index * pitch
        part.visual(
            Box((tooth_w, height + 0.0003, 0.0028)),
            origin=_local_origin(
                Origin(
                    xyz=(
                        x,
                        face_y + direction * (height - 0.0003) * 0.5,
                        r.grip_station_z_m,
                    )
                ),
                offset,
            ),
            material=mats["dark"],
            name=f"grip_build__discrete_teeth__{side}_tooth_{index}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"chrome_vinyl", "nickel_smoke", "black_oxide"} else "metal.brass_aged"),
        )
    part.visual(
        Box((span * 0.98, 0.0016, 0.0026)),
        origin=_local_origin(
            Origin(
                xyz=(0.0, far_y - direction * 0.0004, r.grip_station_z_m + 0.0035),
                rpy=(direction * 0.22, 0.0, 0.0),
            ),
            offset,
        ),
        material=mats["metal"],
        name=f"grip_build__discrete_teeth__{side}_rolled_lip", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"chrome_vinyl", "nickel_smoke", "black_oxide"} else "metal.brass_aged"),
    )


_GRIP_BUILDERS = {
    "serrated_bar": _grip_build_serrated_bar_build,
    "discrete_teeth": _grip_build_discrete_teeth_build,
}


# --- swivel candidates ------------------------------------------------------
def _swivel_build_post_boss_build(r, mats, body, connector) -> None:
    boss_r = r.boss_radius_m
    post_len = r.swivel_post_len_m
    _cyl_along_y(
        body,
        _ZERO_OFFSET,
        radius=POST_R,
        y0=-post_len,
        y1=PLATE_T * 0.6,
        x=0.0,
        z=r.swivel_z_m,
        material=mats["dark"],
        name="swivel_build__post_boss__swivel_post",
    )
    _cyl_along_y(
        body,
        _ZERO_OFFSET,
        radius=boss_r,
        y0=-(post_len + BOSS_T),
        y1=-post_len,
        x=0.0,
        z=r.swivel_z_m,
        material=mats["metal"],
        name="swivel_build__post_boss__swivel_boss",
    )
    connector.visual(
        mesh_from_cadquery(
            _tube(boss_r + 0.0028, boss_r + 0.0005, BOSS_T + 0.0012),
            "swivel_build__post_boss__button_ring",
            tolerance=0.00022,
        ),
        origin=Origin(xyz=(0.0, BOSS_T + 0.0004, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["metal"],
        name="swivel_build__post_boss__button_ring", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"chrome_vinyl", "nickel_smoke", "black_oxide"} else "metal.brass_aged"),
    )
    _cyl_along_y(
        connector,
        _ZERO_OFFSET,
        radius=boss_r * 0.8,
        y0=-0.0018,
        y1=-0.0004,
        x=0.0,
        z=0.0,
        material=mats["accent"],
        name="swivel_build__post_boss__button_window",
    )


def _swivel_build_bridge_mount_build(r, mats, body, connector) -> None:
    boss_r = r.boss_radius_m
    post_len = r.swivel_post_len_m
    sw_z = r.swivel_z_m
    ceiling = -(BARREL_RO + 0.0010) if r.clamp_build != "magnet_backer" else r.mouth_z_m * 0.45
    bridge_z0 = sw_z - (boss_r + 0.0018)
    bridge_z1 = max(sw_z + boss_r + 0.0018, min(sw_z + 0.018, ceiling))
    bridge_y0 = -post_len + 0.0016
    bridge_y1 = PLATE_T * 0.4
    body.visual(
        Box((2.0 * (boss_r + 0.0002), bridge_y1 - bridge_y0, bridge_z1 - bridge_z0)),
        origin=_local_origin(
            Origin(
                xyz=(
                    0.0,
                    (bridge_y0 + bridge_y1) * 0.5,
                    (bridge_z0 + bridge_z1) * 0.5,
                )
            ),
            _ZERO_OFFSET,
        ),
        material=mats["metal"],
        name="swivel_build__bridge_mount__swivel_bridge", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"chrome_vinyl", "nickel_smoke", "black_oxide"} else "metal.brass_aged"),
    )
    wp = _rounded_plate(2.6 * boss_r, 3.0 * boss_r, PLATE_T, cy=sw_z, radius=boss_r * 0.45)
    _plate_visual(
        body,
        _ZERO_OFFSET,
        wp,
        y_near=-post_len + 0.0020,
        material=mats["metal"],
        name="swivel_build__bridge_mount__swivel_mount_plate",
    )
    _cyl_along_y(
        body,
        _ZERO_OFFSET,
        radius=boss_r,
        y0=-(post_len + BOSS_T),
        y1=-post_len + 0.0012,
        x=0.0,
        z=sw_z,
        material=mats["dark"],
        name="swivel_build__bridge_mount__swivel_receiver",
    )

    wp = _rounded_plate(2.4 * boss_r, 2.4 * boss_r, PLATE_T, radius=boss_r * 0.5)
    _plate_visual(
        connector,
        _ZERO_OFFSET,
        wp,
        y_near=-0.0004,
        material=mats["metal"],
        name="swivel_build__bridge_mount__snap_plate",
    )
    connector.visual(
        mesh_from_cadquery(
            _tube(boss_r + 0.0028, boss_r + 0.0006, BOSS_T + 0.0014),
            "swivel_build__bridge_mount__retainer_lip",
            tolerance=0.00022,
        ),
        origin=Origin(xyz=(0.0, BOSS_T + 0.0004, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["metal"],
        name="swivel_build__bridge_mount__retainer_lip", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"chrome_vinyl", "nickel_smoke", "black_oxide"} else "metal.brass_aged"),
    )
    _cyl_along_y(
        connector,
        _ZERO_OFFSET,
        radius=boss_r * 0.8,
        y0=-0.0028,
        y1=-0.0014,
        x=0.0,
        z=0.0,
        material=mats["metal"],
        name="swivel_build__bridge_mount__button_cap",
    )
    _cyl_along_y(
        connector,
        _ZERO_OFFSET,
        radius=boss_r * 0.34,
        y0=-0.0034,
        y1=-0.0026,
        x=0.0,
        z=0.0,
        material=mats["accent"],
        name="swivel_build__bridge_mount__button_dimple",
    )


_SWIVEL_BUILDERS = {
    "post_boss": _swivel_build_post_boss_build,
    "bridge_mount": _swivel_build_bridge_mount_build,
}


# --- badge connector candidates ---------------------------------------------
def _connector_top_extension(r: ResolvedConfig) -> float:
    return r.boss_radius_m + 0.0038


def _swivel_eye_radius(r: ResolvedConfig) -> float:
    """Both source straps are punched at the swivel and the snap hardware
    closes over that eye (002 ``round_holes=((0,0,0.0045),)`` under a
    ``_ring(0.0076, 0.0046, ...)`` and a 4.8 mm ``button_window``; 001
    ``holes=((0,-0.027,0.0065),)`` under ``_annular_button()``).

    The source sizes the eye *under* the button window (4.5 mm hole, 4.8 mm
    window) so the window plugs the eye and the ring flange still lands on
    vinyl.  Keep that relation: the eye stays 0.5 mm inside the window disc,
    which is what holds the connector's hub to its panel as one solid.
    """

    return r.boss_radius_m * 0.8 - 0.0005


def _connector_build_perforated_strap_build(r, mats, connector) -> None:
    length = r.connector_len_m
    width = r.connector_width_m
    top = _connector_top_extension(r)
    wp = _rounded_plate(width, length, PLATE_T, cy=top - length * 0.5, radius=0.0055)
    wp = _cut_circles(wp, PLATE_T, [(0.0, 0.0)], _swivel_eye_radius(r))
    grid = [
        (col * width * 0.27, -length * row)
        for col in (-1.0, 0.0, 1.0)
        for row in (0.22, 0.32, 0.42, 0.52)
    ]
    wp = _cut_rects(wp, PLATE_T, grid, width * 0.13, length * 0.035)
    wp = _cut_slot(wp, PLATE_T, 0.0, -length * 0.72, length * 0.18, width * 0.30)
    _plate_visual(
        connector,
        _ZERO_OFFSET,
        wp,
        y_near=-0.0004,
        material=mats["panel"],
        name="connector_build__perforated_strap__strap_panel",
    )


def _connector_build_slotted_strap_build(r, mats, connector) -> None:
    length = r.connector_len_m
    width = r.connector_width_m
    top = _connector_top_extension(r)
    wp = _rounded_plate(width, length, PLATE_T, cy=top - length * 0.5, radius=0.0042)
    wp = _cut_circles(wp, PLATE_T, [(0.0, 0.0)], _swivel_eye_radius(r))
    wp = _cut_slot(wp, PLATE_T, 0.0, -length * 0.66, length * 0.24, width * 0.34)
    _plate_visual(
        connector,
        _ZERO_OFFSET,
        wp,
        y_near=-0.0004,
        material=mats["panel"],
        name="connector_build__slotted_strap__strap_panel",
    )
    rail_z0 = -(length - top) + 0.0020
    rail_z1 = -0.0020
    for index, sign in enumerate((-1.0, 1.0)):
        connector.visual(
            Box((0.0012, 0.0009, rail_z1 - rail_z0)),
            origin=Origin(xyz=(sign * (width * 0.5 - 0.0007), -0.00185, (rail_z0 + rail_z1) * 0.5)),
            material=mats["panel"],
            name=f"connector_build__slotted_strap__strap_edge_{index}", material_class_id="plastic.frosted_translucent",
        )


def _connector_build_card_frame_build(r, mats, connector) -> None:
    length = r.connector_len_m
    tab_h = max(0.010, r.boss_radius_m * 2.4)
    frame_h = max(0.020, length - tab_h)
    # Source frame is a portrait CR80 pocket, 62 mm wide x 94 mm tall (aspect
    # 0.66) on a 28 mm clip body -- the holder always reads much wider than the
    # clip it hangs from.  Keep that aspect, but never let a short drop or a
    # wide clamp shrink the frame down to the body width, which makes the seed
    # read as two stacked slabs instead of a badge holder.
    frame_w = max(frame_h * 0.66, r.body_width_m * 1.30, 2.0 * r.boss_radius_m + 0.010)
    rail_w = max(0.0035, frame_w * 0.065)
    back_t = 0.0010
    rail_h = 0.0016
    total_t = back_t + rail_h
    wp = _rounded_plate(
        frame_w, tab_h + frame_h, total_t, cy=(tab_h - frame_h) * 0.5, radius=0.0030
    )
    # Raised left, right and bottom rails only: the pocket is cut out of the
    # rail layer all the way through the swivel tab so the top edge stays open
    # and a portrait card can be slid in, exactly as the source frame does
    # (`pocket_h = frame_h - rail_w  # leave only the bottom rail`).  The 1 mm
    # back panel runs unbroken behind the whole frame, tab included.
    pocket_bottom = -(frame_h - rail_w)
    # Overshoot the top edge so the opening is a clean through-cut, never a
    # coincident-face boolean.
    pocket_h = (tab_h + 0.0020) - pocket_bottom
    pocket = (
        cq.Workplane("XY")
        .center(0.0, pocket_bottom + pocket_h * 0.5)
        .rect(frame_w - 2.0 * rail_w, pocket_h)
        .extrude(rail_h + 0.0006)
        .translate((0.0, 0.0, back_t))
    )
    wp = wp.cut(pocket)
    _plate_visual(
        connector,
        _ZERO_OFFSET,
        wp,
        y_near=-0.0004,
        material=mats["panel"],
        name="connector_build__card_frame__card_frame",
        tolerance=0.00040,
    )


def _connector_build_ring_loop_build(r, mats, connector) -> None:
    length = r.connector_len_m
    ring_r = 0.30 * length
    tube = max(0.0013, ring_r * 0.16)
    shank_len = max(0.0055, length - 2.0 * ring_r - tube + 0.0016)
    _cyl_along_y(
        connector,
        _ZERO_OFFSET,
        radius=r.boss_radius_m * 0.9,
        y0=-0.0016,
        y1=-0.0004,
        x=0.0,
        z=0.0,
        material=mats["metal"],
        name="connector_build__ring_loop__neck_collar",
    )
    connector.visual(
        Cylinder(radius=0.0017, length=shank_len),
        origin=Origin(xyz=(0.0, -0.0010, -(shank_len * 0.5) + 0.0006)),
        material=mats["metal"],
        name="connector_build__ring_loop__neck_shank", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"chrome_vinyl", "nickel_smoke", "black_oxide"} else "metal.brass_aged"),
    )
    connector.visual(
        mesh_from_geometry(
            TorusGeometry(ring_r, tube, radial_segments=10, tubular_segments=26),
            "connector_build__ring_loop__ring_loop",
        ),
        origin=Origin(xyz=(0.0, -0.0010, -(length - ring_r)), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["metal"],
        name="connector_build__ring_loop__ring_loop", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"chrome_vinyl", "nickel_smoke", "black_oxide"} else "metal.brass_aged"),
    )


_CONNECTOR_BUILDERS = {
    "perforated_strap": _connector_build_perforated_strap_build,
    "slotted_strap": _connector_build_slotted_strap_build,
    "card_frame": _connector_build_card_frame_build,
    "ring_loop": _connector_build_ring_loop_build,
}


# --- assembly ---------------------------------------------------------------
_CLAMP_MARKERS: dict[str, str] = {
    "alligator_yoke": "clamp_build__alligator_yoke__side_cheek_0",
    "ear_hinge_thumb": "clamp_build__ear_hinge_thumb__hinge_ear_0",
    "bulldog_lever": "clamp_build__bulldog_lever__finger_lever_0",
    "magnet_backer": "clamp_build__magnet_backer__guide_sleeve_0",
}
_SWIVEL_MARKERS: dict[str, str] = {
    "post_boss": "swivel_build__post_boss__swivel_post",
    "bridge_mount": "swivel_build__bridge_mount__swivel_bridge",
}
_CONNECTOR_MARKERS: dict[str, str] = {
    "perforated_strap": "connector_build__perforated_strap__strap_panel",
    "slotted_strap": "connector_build__slotted_strap__strap_edge_0",
    "card_frame": "connector_build__card_frame__card_frame",
    "ring_loop": "connector_build__ring_loop__ring_loop",
}


# The ring loop is rotationally symmetric about the swivel, so its sweep is read
# from the off-axis neck shank instead of the ring itself.
_CONNECTOR_SWEEP_MARKERS: dict[str, str] = dict(_CONNECTOR_MARKERS)
_CONNECTOR_SWEEP_MARKERS["ring_loop"] = "connector_build__ring_loop__neck_shank"


def _grip_marker(r: ResolvedConfig, side: str) -> str:
    if r.grip_build == "serrated_bar":
        return f"grip_build__serrated_bar__{side}_tooth_bar"
    return f"grip_build__discrete_teeth__{side}_tooth_0"


def build_badge_id_holder_clip(
    config: Config | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config or Config())
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={
            "category": "badge_id_holder_clip",
            "slot_choices": slot_choices_for_config(r),
            "mechanism": "sprung clip body with a clamping member and a swivelling badge connector",
        },
    )
    mats = _materials(model, r)

    body = model.part(f"clamp_build__{r.clamp_build}__clip_body", meta={"role": "clip_body"})
    jaw = model.part(f"clamp_build__{r.clamp_build}__clamp_jaw", meta={"role": "clamp_jaw"})
    connector = model.part(
        f"connector_build__{r.connector_build}__badge_connector",
        meta={"role": "badge_connector"},
    )

    body_offset = _ZERO_OFFSET
    jaw_offset = (
        0.0,
        0.0 if r.clamp_build == "magnet_backer" else -r.hinge_front_m,
        0.0,
    )
    _CLAMP_BUILDERS[r.clamp_build](
        model, r, mats, body, body_offset, jaw, jaw_offset
    )
    body_mount, jaw_mount = _grip_mounts(r)
    _GRIP_BUILDERS[r.grip_build](
        r, mats, body, body_offset, body_mount, "body"
    )
    _GRIP_BUILDERS[r.grip_build](r, mats, jaw, jaw_offset, jaw_mount, "jaw")
    _SWIVEL_BUILDERS[r.swivel_build](r, mats, body, connector)
    _CONNECTOR_BUILDERS[r.connector_build](r, mats, connector)

    if r.clamp_build == "magnet_backer":
        model.articulation(
            "body_to_clamp_jaw",
            ArticulationType.PRISMATIC,
            parent=body,
            child=jaw,
            origin=Origin(),
            axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(
                lower=0.0, upper=r.clamp_travel_m, effort=12.0, velocity=0.12
            ),
            meta={
                "positive_motion": "slides the magnet backer off the carrier plate "
                "along its guide pins so cloth can pass between them"
            },
        )
    else:
        provider = AxisInterface(
            name="clip_body__hinge_pin_axis",
            point=(0.0, -r.hinge_front_m, 0.0),
            axis=(1.0, 0.0, 0.0),
            radial=(0.0, 0.0, 1.0),
            radius=BARREL_RI,
        )
        consumer = AxisInterface(
            name="clamp_jaw__barrel_bore",
            point=(0.0, 0.0, 0.0),
            axis=(1.0, 0.0, 0.0),
            radial=(0.0, 0.0, 1.0),
            radius=PIN_R,
        )
        mate = mate_axes(provider, consumer)
        model.articulation(
            "body_to_clamp_jaw",
            ArticulationType.REVOLUTE,
            parent=body,
            child=jaw,
            origin=mate.origin,
            axis=mate.axis,
            motion_limits=MotionLimits(lower=0.0, upper=r.jaw_open_rad, effort=8.0, velocity=4.0),
            meta={"positive_motion": "swings the sprung jaw open at the mouth"},
        )
        register_interface_mate(model, "body_to_clamp_jaw", mate)

    swivel_provider = AxisInterface(
        name="clip_body__swivel_boss_axis",
        point=(0.0, r.swivel_point_y_m, r.swivel_z_m),
        axis=(0.0, -1.0, 0.0),
        radial=(0.0, 0.0, -1.0),
        radius=r.boss_radius_m + 0.0028,
    )
    swivel_consumer = AxisInterface(
        name="badge_connector__button_bore",
        point=(0.0, 0.0, 0.0),
        axis=(0.0, -1.0, 0.0),
        radial=(0.0, 0.0, -1.0),
        radius=r.boss_radius_m + 0.0005,
    )
    swivel_mate = mate_axes(swivel_provider, swivel_consumer)
    model.articulation(
        "body_to_badge_connector",
        ArticulationType.CONTINUOUS,
        parent=body,
        child=connector,
        origin=swivel_mate.origin,
        axis=swivel_mate.axis,
        motion_limits=MotionLimits(effort=2.0, velocity=8.0),
        meta={"positive_motion": "turns the badge connector in the badge plane"},
    )
    register_interface_mate(model, "body_to_badge_connector", swivel_mate)

    clamp_edge = r.clamp_travel_m if r.clamp_build == "magnet_backer" else r.jaw_open_rad
    model.meta["risk_poses"] = (
        {"body_to_clamp_jaw": clamp_edge, "body_to_badge_connector": math.pi / 2.0},
        {"body_to_clamp_jaw": clamp_edge, "body_to_badge_connector": math.pi},
        {"body_to_clamp_jaw": 0.0, "body_to_badge_connector": -math.pi / 2.0},
    )
    model.meta["coupled_joint_pairs"] = (("body_to_clamp_jaw", "body_to_badge_connector"),)
    return model


def build_seeded_badge_id_holder_clip(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_badge_id_holder_clip(config_from_seed(seed), assets=assets)


# --- authored tests ---------------------------------------------------------
def _parts_by_role(model: ArticulatedObject, role: str):
    return [p for p in model.parts if p.meta.get("role") == role]


def run_badge_id_holder_clip_tests(model: ArticulatedObject, config: Config) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)

    bodies = _parts_by_role(model, "clip_body")
    jaws = _parts_by_role(model, "clamp_jaw")
    connectors = _parts_by_role(model, "badge_connector")
    joints = {j.name: j for j in model.articulations}
    clamp_joint = joints.get("body_to_clamp_jaw")
    swivel_joint = joints.get("body_to_badge_connector")
    expected_type = (
        ArticulationType.PRISMATIC
        if r.clamp_build == "magnet_backer"
        else ArticulationType.REVOLUTE
    )

    ctx.check(
        "category_anchor: one clip body carries the clamp member and the badge connector",
        len(bodies) == 1
        and len(jaws) == 1
        and len(connectors) == 1
        and bool(model.root_parts())
        and model.root_parts()[0].name == bodies[0].name
        and clamp_joint is not None
        and swivel_joint is not None
        and clamp_joint.articulation_type == expected_type
        and clamp_joint.parent == bodies[0].name
        and clamp_joint.child == jaws[0].name
        and swivel_joint.articulation_type == ArticulationType.CONTINUOUS
        and swivel_joint.parent == bodies[0].name
        and swivel_joint.child == connectors[0].name
        and tuple(round(abs(v), 6) for v in swivel_joint.axis) == (0.0, 1.0, 0.0),
        details=f"roles={len(bodies)}/{len(jaws)}/{len(connectors)} clamp={expected_type}",
    )

    body, jaw, connector = bodies[0], jaws[0], connectors[0]
    body_grip = _grip_marker(r, "body")
    jaw_grip = _grip_marker(r, "jaw")
    clamp_edge = r.clamp_travel_m if r.clamp_build == "magnet_backer" else r.jaw_open_rad

    closed_body = ctx.part_element_world_aabb(body, elem=body_grip)
    closed_jaw = ctx.part_element_world_aabb(jaw, elem=jaw_grip)
    with ctx.pose({clamp_joint: clamp_edge}):
        open_jaw = ctx.part_element_world_aabb(jaw, elem=jaw_grip)
    if closed_body is not None and closed_jaw is not None and open_jaw is not None:
        closed_sep = abs(
            (closed_body[0][1] + closed_body[1][1]) * 0.5
            - (closed_jaw[0][1] + closed_jaw[1][1]) * 0.5
        )
        open_sep = abs(
            (closed_body[0][1] + closed_body[1][1]) * 0.5 - (open_jaw[0][1] + open_jaw[1][1]) * 0.5
        )
    else:
        closed_sep = open_sep = 0.0
    ctx.check(
        "category_anchor: the clamp opens its two gripping faces apart",
        open_sep > closed_sep + 0.0012 and closed_sep > 0.0,
        details=f"closed_sep={closed_sep:.5f} open_sep={open_sep:.5f} edge={clamp_edge:.4f}",
    )

    marker = _CONNECTOR_MARKERS[r.connector_build]
    sweep_marker = _CONNECTOR_SWEEP_MARKERS[r.connector_build]
    rest = ctx.part_element_world_aabb(connector, elem=sweep_marker)
    with ctx.pose({swivel_joint: math.pi / 2.0}):
        turned = ctx.part_element_world_aabb(connector, elem=sweep_marker)
    if rest is not None and turned is not None:
        rest_dx = rest[1][0] - rest[0][0]
        rest_dz = rest[1][2] - rest[0][2]
        turn_dx = turned[1][0] - turned[0][0]
        turn_dz = turned[1][2] - turned[0][2]
    else:
        rest_dx = rest_dz = turn_dx = turn_dz = 0.0
    ctx.check(
        "category_anchor: the badge connector swivels in the badge plane",
        rest_dz > rest_dx * 1.4 and turn_dx > turn_dz * 1.4,
        details=f"rest=({rest_dx:.4f},{rest_dz:.4f}) turned=({turn_dx:.4f},{turn_dz:.4f})",
    )

    limit = -r.front_envelope_m
    clamp_intrusions: list[str] = []
    for part in (body, jaw):
        for visual in part.visuals:
            name = visual.name or ""
            if name.startswith("swivel_build__"):
                continue
            aabb = ctx.part_element_world_aabb(part, elem=name)
            if aabb is not None and aabb[0][1] < limit - 0.0008:
                clamp_intrusions.append(f"{name}:{aabb[0][1]:.5f}")
    connector_intrusions: list[str] = []
    for visual in connector.visuals:
        name = visual.name or ""
        aabb = ctx.part_element_world_aabb(connector, elem=name)
        if aabb is not None and aabb[1][1] > limit - 0.0004:
            connector_intrusions.append(f"{name}:{aabb[1][1]:.5f}")
    ctx.check(
        "category_anchor: the badge connector plane clears the whole clamp envelope",
        not clamp_intrusions and not connector_intrusions,
        details=(
            f"envelope={limit:.5f} clamp_front={clamp_intrusions!r} "
            f"connector_back={connector_intrusions!r}"
        ),
    )

    visual_names = {v.name or "" for p in model.parts for v in p.visuals}
    ctx.check(
        "category_anchor: clamp_build identity",
        _CLAMP_MARKERS[r.clamp_build] in visual_names,
        details=f"clamp_build={r.clamp_build}",
    )
    ctx.check(
        "category_anchor: grip_build identity",
        body_grip in visual_names and jaw_grip in visual_names,
        details=f"grip_build={r.grip_build}",
    )
    ctx.check(
        "category_anchor: swivel_build identity",
        _SWIVEL_MARKERS[r.swivel_build] in visual_names,
        details=f"swivel_build={r.swivel_build}",
    )
    ctx.check(
        "category_anchor: connector_build identity",
        marker in visual_names,
        details=f"connector_build={r.connector_build}",
    )

    stage_prefix = f"clamp_build__{r.clamp_build}__stage_"
    stage_count = sum(1 for name in visual_names if name.startswith(stage_prefix))
    ctx.check(
        "category_anchor: clamping stations match clamp_stage_count",
        stage_count == r.clamp_stage_count,
        details=f"stages={stage_count} expected={r.clamp_stage_count}",
    )

    ctx.check(
        "clip stations stay inside the stamped body plate",
        r.tail_z_m + r.boss_radius_m + 0.0006 <= r.swivel_z_m <= r.mouth_z_m - 0.0060
        and r.grip_station_z_m < r.mouth_z_m
        and r.pin_span_m > 0.004
        and r.stage_pitch_m > r.stage_half_m * 2.0 + 0.0006,
        details=(
            f"tail={r.tail_z_m:.4f} swivel={r.swivel_z_m:.4f} mouth={r.mouth_z_m:.4f} "
            f"pitch={r.stage_pitch_m:.5f} half={r.stage_half_m:.5f}"
        ),
    )

    ctx.check(
        "domain choices recorded on the model",
        model.meta.get("slot_choices") == slot_choices_for_config(r),
    )
    return ctx.report()


TEMPLATE_CORNERS = (
    corner_case(
        "widest_bulldog_three_stage_card",
        {
            "clamp_build": "bulldog_lever",
            "grip_build": "discrete_teeth",
            "swivel_build": "bridge_mount",
            "connector_build": "card_frame",
            "clamp_stage_count": 3,
            "clip_length_m": 0.052,
            "clip_width_m": 0.034,
            "jaw_open_rad": 0.50,
            "connector_drop_m": 0.118,
        },
        reason=(
            "shortest widest bulldog at full opening with three coil stations, the "
            "bulkiest swivel bridge and the largest rigid card frame"
        ),
    ),
    corner_case(
        "narrowest_alligator_single_ring",
        {
            "clamp_build": "alligator_yoke",
            "grip_build": "serrated_bar",
            "swivel_build": "post_boss",
            "connector_build": "ring_loop",
            "clamp_stage_count": 1,
            "clip_length_m": 0.086,
            "clip_width_m": 0.018,
            "jaw_open_rad": 0.26,
            "connector_drop_m": 0.058,
        },
        reason="longest and narrowest alligator leaf with the tightest opening and the smallest ring",
    ),
    corner_case(
        "magnet_full_travel_three_poles",
        {
            "clamp_build": "magnet_backer",
            "grip_build": "discrete_teeth",
            "swivel_build": "bridge_mount",
            "clamp_stage_count": 3,
            "connector_build": "perforated_strap",
            "clip_length_m": 0.052,
            "clip_width_m": 0.018,
            "jaw_open_rad": 0.50,
            "connector_drop_m": 0.118,
        },
        reason="smallest magnetic carrier at maximum backer travel with three pole stations",
    ),
    corner_case(
        "ear_hinge_widest_slotted",
        {
            "clamp_build": "ear_hinge_thumb",
            "grip_build": "serrated_bar",
            "swivel_build": "post_boss",
            "connector_build": "slotted_strap",
            "clamp_stage_count": 2,
            "clip_length_m": 0.086,
            "clip_width_m": 0.034,
            "jaw_open_rad": 0.50,
            "connector_drop_m": 0.058,
        },
        reason="largest ear-hinge body at full opening with the shortest reinforced tab",
    ),
)


__all__ = [
    "TEMPLATE_CORNERS",
    "TEMPLATE_DOMAIN",
    "Config",
    "ResolvedConfig",
    "build_badge_id_holder_clip",
    "build_seeded_badge_id_holder_clip",
    "config_from_seed",
    "resolve_config",
    "run_badge_id_holder_clip_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
]
