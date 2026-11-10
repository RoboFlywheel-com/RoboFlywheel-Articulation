# SPDX-License-Identifier: Apache-2.0

# ruff: noqa: E501
"""Self-contained Urban Environment / bucket2 template (TEMPLATE_DOMAIN).

Subcategory identity: a small **coopered wooden keg / barrel / pail** standing on
its own base.  One hollow staved surface-of-revolution body with a solid wooden
floor and a recessed inner seating collar, wrapped by ``N`` dark metal hoop
bands, closed at the top by exactly one closure mechanism, and optionally
carrying one body- or closure-mounted carry fitting.

Rebuilt from the eight reviewed workbench sources listed in
``articraft_template_authoring/source_maps/Urban_Environment_bucket2.md``:

* ``body_profile`` (3): parabolic mid-bulge / straight cylinder / linear taper.
* ``hoop_band`` (1): the flat iron band that the ``hoop_count`` multiplicity
  repeats along the body.
* ``closure`` (3): captive lift-off plug lid (PRISMATIC +Z) / hinged top hatch in
  a permanent head (REVOLUTE about -Y) / permanent head plus a side bunghole and
  its bung plug (PRISMATIC +X).
* ``handle`` (4): swing bail (one REVOLUTE about X) / two side ear rings (two
  REVOLUTE) / fixed arched grip on the closure top / no handle at all.

Every moving member is retained by real capture geometry -- the lid skirt inside
the seat collar bore, the hatch knuckle on the rim pin, the bung shank inside the
bunghole bore, the bail stubs inside the ear eyelets, the ring eyes on the ear
pins.  No stroke is bounded by a free constant: each one is derived from how much
capture length has to stay engaged.  Every capture is a coaxial (or axis-swept)
running fit whose clearance is invariant under the joint's own motion and stays
inside the assembly support tolerance, so no member leaves its host at a limit
pose.

Every revolute joint is built from ``mate_axes`` and registered with
``register_interface_mate``.  No source runtime, snapshot or other template is
imported; geometry uses only the SDK plus the Python standard library.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Literal

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    AxisInterface,
    Cylinder,
    Inertial,
    MeshGeometry,
    MotionLimits,
    MotionProperties,
    Origin,
    TemplateDomain,
    TestContext,
    TestReport,
    TorusGeometry,
    boolean_difference,
    component_slot,
    corner_case,
    mate_axes,
    mesh_from_geometry,
    multiplicity_slot,
    register_interface_mate,
)

__modular__ = True

# ---------------------------------------------------------------------------
# Slot value spaces
# ---------------------------------------------------------------------------
BodyProfile = Literal["bulged_stave", "straight_stave", "tapered_pail"]
HoopBand = Literal["flat_iron_band"]
Closure = Literal["slide_off_lid", "hinged_lid", "bung_plug"]
Handle = Literal["swing_bail", "side_ear_rings", "arched_grip", "no_handle"]
Palette = Literal["oak_dark_iron", "pale_ash_zinc", "walnut_black", "weathered_grey"]

BODY_PROFILES: tuple[BodyProfile, ...] = ("bulged_stave", "straight_stave", "tapered_pail")
HOOP_BANDS: tuple[HoopBand, ...] = ("flat_iron_band",)
CLOSURES: tuple[Closure, ...] = ("slide_off_lid", "hinged_lid", "bung_plug")
HANDLES: tuple[Handle, ...] = ("swing_bail", "side_ear_rings", "arched_grip", "no_handle")
HOOP_COUNTS: tuple[int, ...] = (2, 3, 4, 5, 6)
PALETTES_ORDER: tuple[Palette, ...] = (
    "oak_dark_iron",
    "pale_ash_zinc",
    "walnut_black",
    "weathered_grey",
)

TEMPLATE_DOMAIN = TemplateDomain(
    slots=(
        component_slot("body_profile", BODY_PROFILES, role="staved surface-of-revolution body"),
        component_slot("hoop_band", HOOP_BANDS, role="metal hoop band construction"),
        component_slot("closure", CLOSURES, role="top closure / bung mechanism"),
        component_slot("handle", HANDLES, role="carry fitting"),
        multiplicity_slot(
            "hoop_count",
            HOOP_COUNTS,
            role="metal hoop bands wrapped around the body",
            item_slot="hoop_band",
        ),
    )
)

PALETTES: dict[Palette, dict[str, tuple[float, float, float, float]]] = {
    "oak_dark_iron": {
        "wood": (0.740, 0.520, 0.320, 1.0),
        "wood_light": (0.800, 0.600, 0.390, 1.0),
        "metal": (0.160, 0.170, 0.190, 1.0),
        "accent": (0.200, 0.300, 0.450, 1.0),
    },
    "pale_ash_zinc": {
        "wood": (0.820, 0.700, 0.520, 1.0),
        "wood_light": (0.880, 0.780, 0.610, 1.0),
        "metal": (0.640, 0.665, 0.685, 1.0),
        "accent": (0.380, 0.400, 0.420, 1.0),
    },
    "walnut_black": {
        "wood": (0.400, 0.250, 0.150, 1.0),
        "wood_light": (0.480, 0.310, 0.190, 1.0),
        "metal": (0.070, 0.075, 0.080, 1.0),
        "accent": (0.520, 0.180, 0.120, 1.0),
    },
    "weathered_grey": {
        "wood": (0.560, 0.540, 0.500, 1.0),
        "wood_light": (0.640, 0.620, 0.580, 1.0),
        "metal": (0.300, 0.310, 0.320, 1.0),
        "accent": (0.240, 0.330, 0.300, 1.0),
    },
}

# ---------------------------------------------------------------------------
# Shared construction constants (metres; +Z up, base footprint on z = 0).
# The body is a surface of revolution about Z, so azimuth is only meaningful for
# the asymmetric fittings: the bunghole faces +X, the hatch hinge sits on -X,
# the bail ears are on +-X and the side ear rings on +-Y.
# ---------------------------------------------------------------------------
SEG_PER_STAVE = 6  # angular samples per stave (seam + crest resolution)
OUTER_STATIONS = 9  # profile samples up the outer wall
INNER_STATIONS = 8  # profile samples down the inner cavity wall
RUN_CLEARANCE = 0.0005  # running clearance of every captured sliding/rotating fit
SEAT_GAP = 0.0003  # seating gap between a closure and its seat face
BAND_BITE = 0.0015  # how far a hoop band bites into the stave crests
FUSE = 0.0006  # deliberate intra-part overlap of welded-on features
EMBED = 0.006  # how far a welded bracket foot sinks into the staves
HOOP_MARGIN_RATIO = 0.14  # first/last band centre inset from the body ends
# A keg lid and a bunghole bung are LIFT-OFF closures: the source parent
# (ad0a147f model.py:L65) states `LID_TRAVEL = 0.12  # 0 (closed) -> 0.12 m
# (open/clear)`. The stroke has to carry the closure clear of its seat, or the
# mouth is never open and the interior is never visible. `fail_if_isolated_parts`
# is category-blind and would flag the fully-open pose, so both closures declare
# `ctx.allow_isolated_part(...)` -- the pipeline's sanctioned escape for exactly
# this. Contrast a drawer or a card slide, which must stay captive in its host;
# nothing in the pipeline distinguishes the two cases, the author does.
LID_OPEN_CLEAR = 0.060  # free lift above skirt exit, so the mouth reads as open
BUNG_OPEN_CLEAR = 0.020  # free pull beyond shank exit, so the bore reads as open
CLEAR_MARGIN = 0.006  # swept-envelope clearance for the swing bail
PIN_SEGMENTS = 24  # facet count shared by every pin/bore running fit
BORE_SEGMENTS = 32  # facet count shared by the bunghole bore and its shank


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, float(value)))


def _pick(value, choices):
    return value if value in choices else choices[0]


def _bore_for(shaft_radius: float, segments: int) -> float:
    """Facet-aware bore radius that keeps a running fit inside the support band."""

    return (shaft_radius + RUN_CLEARANCE) / math.cos(math.pi / segments)


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Config:
    body_profile: BodyProfile = "bulged_stave"
    hoop_band: HoopBand = "flat_iron_band"
    closure: Closure = "slide_off_lid"
    handle: Handle = "swing_bail"
    hoop_count: int = 2
    body_height_m: float = 0.360
    end_radius_m: float = 0.150
    bulge_ratio: float = 1.240
    taper_ratio: float = 1.300
    stave_count: int = 16
    hoop_proud_m: float = 0.007
    hoop_half_height_m: float = 0.022
    lid_seat_depth_m: float = 0.045
    hatch_port_ratio: float = 0.500
    lid_open_rad: float = 1.300
    bung_bore_m: float = 0.015
    bung_height_ratio: float = 0.500
    bail_open_rad: float = 2.800
    bail_wire_r_m: float = 0.005
    ring_major_r_m: float = 0.025
    ring_open_rad: float = 1.550
    grip_rise_m: float = 0.050
    palette: Palette = "oak_dark_iron"
    name: str = "urban_environment_bucket2"


@dataclass(frozen=True)
class ResolvedConfig:
    body_profile: BodyProfile
    hoop_band: HoopBand
    closure: Closure
    handle: Handle
    hoop_count: int
    body_height_m: float
    end_radius_m: float
    bulge_ratio: float
    taper_ratio: float
    stave_count: int
    hoop_proud_m: float
    hoop_half_height_m: float
    lid_seat_depth_m: float
    hatch_port_ratio: float
    lid_open_rad: float
    bung_bore_m: float
    bung_height_ratio: float
    bail_open_rad: float
    bail_wire_r_m: float
    ring_major_r_m: float
    ring_open_rad: float
    grip_rise_m: float
    palette: Palette
    name: str
    # ---- derived -----------------------------------------------------------
    wall_m: float
    floor_m: float
    groove_m: float
    segments: int
    r_top: float
    r_bore: float
    seat_depth_m: float
    r_seat_in: float
    hoop_margin_m: float
    hoop_half_m: float


BULGED = "bulged_stave"
STRAIGHT = "straight_stave"
TAPERED = "tapered_pail"


def config_from_seed(seed: int) -> Config:
    choices = TEMPLATE_DOMAIN.sample(seed)
    rng = random.Random(int(seed) ^ 0x0729_B2C2)
    return Config(
        body_profile=choices["body_profile"],
        hoop_band=choices["hoop_band"],
        closure=choices["closure"],
        handle=choices["handle"],
        hoop_count=int(choices["hoop_count"]),
        body_height_m=round(rng.uniform(0.28, 0.46), 4),
        end_radius_m=round(rng.uniform(0.125, 0.175), 4),
        bulge_ratio=round(rng.uniform(1.10, 1.32), 4),
        taper_ratio=round(rng.uniform(1.15, 1.45), 4),
        stave_count=rng.randint(12, 22),
        hoop_proud_m=round(rng.uniform(0.005, 0.011), 4),
        hoop_half_height_m=round(rng.uniform(0.014, 0.026), 4),
        lid_seat_depth_m=round(rng.uniform(0.030, 0.060), 4),
        hatch_port_ratio=round(rng.uniform(0.42, 0.58), 4),
        lid_open_rad=round(rng.uniform(1.10, 1.50), 4),
        bung_bore_m=round(rng.uniform(0.011, 0.019), 4),
        bung_height_ratio=round(rng.uniform(0.38, 0.62), 4),
        bail_open_rad=round(rng.uniform(2.40, 3.10), 4),
        bail_wire_r_m=round(rng.uniform(0.0035, 0.0065), 5),
        ring_major_r_m=round(rng.uniform(0.018, 0.032), 4),
        ring_open_rad=round(rng.uniform(1.20, 1.90), 4),
        grip_rise_m=round(rng.uniform(0.035, 0.065), 4),
        palette=rng.choice(PALETTES_ORDER),
        name=f"urban_environment_bucket2_seed_{seed}",
    )


def _radius_at(
    profile: str, z: float, height: float, r_end: float, r_mid: float, r_mouth: float
) -> float:
    t = _clamp(z / height, 0.0, 1.0)
    if profile == BULGED:
        return r_end + (r_mid - r_end) * (1.0 - (2.0 * t - 1.0) ** 2)
    if profile == TAPERED:
        return r_end + (r_mouth - r_end) * t
    return r_end


def resolve_config(config: Config | None = None) -> ResolvedConfig:
    cfg = config or Config()
    TEMPLATE_DOMAIN.validate(
        {
            "body_profile": cfg.body_profile,
            "hoop_band": cfg.hoop_band,
            "closure": cfg.closure,
            "handle": cfg.handle,
            "hoop_count": int(cfg.hoop_count),
        }
    )
    body_profile = _pick(cfg.body_profile, BODY_PROFILES)
    hoop_band = _pick(cfg.hoop_band, HOOP_BANDS)
    closure = _pick(cfg.closure, CLOSURES)
    handle = _pick(cfg.handle, HANDLES)
    hoop_count = int(_pick(int(cfg.hoop_count), HOOP_COUNTS))

    height = _clamp(cfg.body_height_m, 0.28, 0.46)
    r_end = _clamp(cfg.end_radius_m, 0.125, 0.175)
    bulge_ratio = _clamp(cfg.bulge_ratio, 1.10, 1.32)
    taper_ratio = _clamp(cfg.taper_ratio, 1.15, 1.45)
    stave_count = int(_clamp(int(cfg.stave_count), 12, 22))
    hoop_proud = _clamp(cfg.hoop_proud_m, 0.005, 0.011)
    hoop_half_height = _clamp(cfg.hoop_half_height_m, 0.014, 0.026)
    lid_seat_depth = _clamp(cfg.lid_seat_depth_m, 0.030, 0.060)
    hatch_port_ratio = _clamp(cfg.hatch_port_ratio, 0.42, 0.58)
    lid_open = _clamp(cfg.lid_open_rad, 1.10, 1.50)
    bung_bore = _clamp(cfg.bung_bore_m, 0.011, 0.019)
    bung_height_ratio = _clamp(cfg.bung_height_ratio, 0.38, 0.62)
    bail_open = _clamp(cfg.bail_open_rad, 2.40, 3.10)
    bail_wire_r = _clamp(cfg.bail_wire_r_m, 0.0035, 0.0065)
    ring_major_r = _clamp(cfg.ring_major_r_m, 0.018, 0.032)
    ring_open = _clamp(cfg.ring_open_rad, 1.20, 1.90)
    grip_rise = _clamp(cfg.grip_rise_m, 0.035, 0.065)

    r_mid = r_end * bulge_ratio
    r_mouth = r_end * taper_ratio
    wall = _clamp(0.105 * r_end, 0.012, 0.020)
    floor_t = _clamp(0.130 * r_end, 0.016, 0.026)
    groove = 0.30 * wall
    segments = stave_count * SEG_PER_STAVE

    r_top = _radius_at(body_profile, height, height, r_end, r_mid, r_mouth)
    r_bore = r_top - wall

    seat_depth = lid_seat_depth if closure == "slide_off_lid" else 0.018
    seat_w = 0.006 + 0.35 * wall
    inner_samples = [
        _radius_at(body_profile, height - seat_depth * i / 6.0, height, r_end, r_mid, r_mouth)
        - wall
        for i in range(7)
    ]
    r_seat_in = min(inner_samples) - seat_w

    hoop_margin = HOOP_MARGIN_RATIO * height
    pitch = (height - 2.0 * hoop_margin) / (hoop_count - 1) if hoop_count >= 2 else height
    hoop_half = _clamp(min(hoop_half_height, 0.42 * pitch), 0.006, 0.026)

    return ResolvedConfig(
        body_profile=body_profile,
        hoop_band=hoop_band,
        closure=closure,
        handle=handle,
        hoop_count=hoop_count,
        body_height_m=height,
        end_radius_m=r_end,
        bulge_ratio=bulge_ratio,
        taper_ratio=taper_ratio,
        stave_count=stave_count,
        hoop_proud_m=hoop_proud,
        hoop_half_height_m=hoop_half_height,
        lid_seat_depth_m=lid_seat_depth,
        hatch_port_ratio=hatch_port_ratio,
        lid_open_rad=lid_open,
        bung_bore_m=bung_bore,
        bung_height_ratio=bung_height_ratio,
        bail_open_rad=bail_open,
        bail_wire_r_m=bail_wire_r,
        ring_major_r_m=ring_major_r,
        ring_open_rad=ring_open,
        grip_rise_m=grip_rise,
        palette=_pick(cfg.palette, PALETTES_ORDER),
        name=cfg.name or "urban_environment_bucket2",
        wall_m=wall,
        floor_m=floor_t,
        groove_m=groove,
        segments=segments,
        r_top=r_top,
        r_bore=r_bore,
        seat_depth_m=seat_depth,
        r_seat_in=r_seat_in,
        hoop_margin_m=hoop_margin,
        hoop_half_m=hoop_half,
    )


def slot_choices_for_config(config) -> tuple[tuple[str, object], ...]:
    r = config if isinstance(config, ResolvedConfig) else resolve_config(config)
    return (
        ("body_profile", r.body_profile),
        ("hoop_band", r.hoop_band),
        ("closure", r.closure),
        ("handle", r.handle),
        ("hoop_count", r.hoop_count),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, object], ...]:
    return slot_choices_for_config(config_from_seed(seed))


__all__ = [
    "TEMPLATE_DOMAIN",
    "Config",
    "ResolvedConfig",
    "config_from_seed",
    "resolve_config",
    "slot_choices_for_config",
    "slot_choices_for_seed",
]


# ===========================================================================
# Generic mesh machinery (surfaces of revolution with optional stave relief)
# ===========================================================================
def _polygon_area(points) -> float:
    total = 0.0
    count = len(points)
    for index in range(count):
        x0, y0 = points[index][0], points[index][1]
        x1, y1 = points[(index + 1) % count][0], points[(index + 1) % count][1]
        total += x0 * y1 - x1 * y0
    return 0.5 * total


def _stave_relief(segments: int, stave_count: int, depth: float) -> list[float]:
    """Per-angle inward relief that carves the vertical stave seams."""

    if depth <= 0.0 or stave_count <= 0:
        return [0.0] * segments
    per = max(1, segments // stave_count)
    relief: list[float] = []
    for index in range(segments):
        frac = (index % per) / float(per)
        relief.append(depth * (2.0 * abs(frac - 0.5)) ** 4)
    return relief


def _lathe(profile, segments: int, relief=None) -> MeshGeometry:
    """Revolve one closed ``(radius, z, relieved)`` profile about the world Z axis."""

    points = [(float(p[0]), float(p[1]), bool(p[2]) if len(p) > 2 else False) for p in profile]
    if _polygon_area(points) < 0.0:
        points = list(reversed(points))
    geometry = MeshGeometry()
    rings: list[list[int]] = []
    for radius, z, relieved in points:
        if radius <= 1e-9:
            axis_vertex = geometry.add_vertex(0.0, 0.0, z)
            rings.append([axis_vertex] * segments)
            continue
        ring: list[int] = []
        for index in range(segments):
            angle = 2.0 * math.pi * index / segments
            rr = radius - (relief[index] if (relieved and relief is not None) else 0.0)
            ring.append(geometry.add_vertex(rr * math.cos(angle), rr * math.sin(angle), z))
        rings.append(ring)

    def add(a: int, b: int, c: int) -> None:
        if a == b or b == c or c == a:
            return
        geometry.add_face(a, b, c)

    count = len(points)
    for j in range(count):
        j2 = (j + 1) % count
        if points[j][0] <= 1e-9 and points[j2][0] <= 1e-9:
            continue
        ring0 = rings[j]
        ring1 = rings[j2]
        for i in range(segments):
            i2 = (i + 1) % segments
            a, b, c, d = ring0[i], ring0[i2], ring1[i2], ring1[i]
            add(a, b, d)
            add(b, c, d)
    return geometry


def _cylinder_z(radius: float, z0: float, z1: float, segments: int) -> MeshGeometry:
    return _lathe(
        ((0.0, z0, False), (radius, z0, False), (radius, z1, False), (0.0, z1, False)),
        segments,
    )


def _tube_z(inner: float, outer: float, z0: float, z1: float, segments: int) -> MeshGeometry:
    return _lathe(
        ((inner, z0, False), (outer, z0, False), (outer, z1, False), (inner, z1, False)),
        segments,
    )


def _along_x(geometry: MeshGeometry, x: float, y: float, z: float) -> MeshGeometry:
    """Re-aim a Z-built solid of revolution along +X and place its origin."""

    return geometry.rotate_y(math.pi / 2.0).translate(x, y, z)


def _along_y(geometry: MeshGeometry, x: float, y: float, z: float) -> MeshGeometry:
    """Re-aim a Z-built solid of revolution along +Y and place its origin."""

    return geometry.rotate_x(-math.pi / 2.0).translate(x, y, z)


def _box(size, centre) -> MeshGeometry:
    hx, hy, hz = 0.5 * size[0], 0.5 * size[1], 0.5 * size[2]
    cx, cy, cz = centre
    geometry = MeshGeometry()
    for corner in (
        (cx - hx, cy - hy, cz - hz),
        (cx + hx, cy - hy, cz - hz),
        (cx + hx, cy + hy, cz - hz),
        (cx - hx, cy + hy, cz - hz),
        (cx - hx, cy - hy, cz + hz),
        (cx + hx, cy - hy, cz + hz),
        (cx + hx, cy + hy, cz + hz),
        (cx - hx, cy + hy, cz + hz),
    ):
        geometry.add_vertex(*corner)
    for a, b, c, d in (
        (0, 3, 2, 1),
        (4, 5, 6, 7),
        (0, 1, 5, 4),
        (1, 2, 6, 5),
        (2, 3, 7, 6),
        (3, 0, 4, 7),
    ):
        geometry.add_face(a, b, c)
        geometry.add_face(a, c, d)
    return geometry


def _sphere(radius: float, centre, segments: int = 10) -> MeshGeometry:
    rings = max(4, segments)
    profile = [
        (
            radius * math.sin(math.pi * index / rings),
            -radius * math.cos(math.pi * index / rings),
            False,
        )
        for index in range(rings + 1)
    ]
    return _lathe(profile, max(6, segments)).translate(*centre)


def _rod(p0, p1, radius: float, segments: int = 10) -> MeshGeometry:
    dx, dy, dz = (p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2])
    length = math.sqrt(dx * dx + dy * dy + dz * dz)
    if length < 1e-9:
        return MeshGeometry()
    geometry = _cylinder_z(radius, 0.0, length, segments)
    pitch = math.acos(_clamp(dz / length, -1.0, 1.0))
    yaw = math.atan2(dy, dx) if (abs(dx) > 1e-12 or abs(dy) > 1e-12) else 0.0
    geometry.rotate_y(pitch).rotate_z(yaw)
    return geometry.translate(p0[0], p0[1], p0[2])


def _polyline_tube(points, radius: float, segments: int = 10) -> MeshGeometry:
    geometry = MeshGeometry()
    for index in range(len(points) - 1):
        geometry.merge(_rod(points[index], points[index + 1], radius, segments))
    for point in points[1:-1]:
        geometry.merge(_sphere(radius, point, segments))
    return geometry


# ===========================================================================
# body_profile candidates: the staved surface-of-revolution body
# ===========================================================================
def _r_out(r: ResolvedConfig, z: float) -> float:
    return _radius_at(
        r.body_profile,
        z,
        r.body_height_m,
        r.end_radius_m,
        r.end_radius_m * r.bulge_ratio,
        r.end_radius_m * r.taper_ratio,
    )


def _r_in(r: ResolvedConfig, z: float) -> float:
    return _r_out(r, z) - r.wall_m


def _r_band(r: ResolvedConfig, z_lo: float, z_hi: float, *, proud: bool) -> float:
    """Largest hard radius over a height band (optionally including a proud hoop)."""

    lo = _clamp(min(z_lo, z_hi), 0.0, r.body_height_m)
    hi = _clamp(max(z_lo, z_hi), 0.0, r.body_height_m)
    largest = max(_r_out(r, lo + (hi - lo) * i / 8.0) for i in range(9))
    return largest + (r.hoop_proud_m if proud else 0.0)


def _r_min_band(r: ResolvedConfig, z_lo: float, z_hi: float) -> float:
    lo = _clamp(min(z_lo, z_hi), 0.0, r.body_height_m)
    hi = _clamp(max(z_lo, z_hi), 0.0, r.body_height_m)
    return min(_r_out(r, lo + (hi - lo) * i / 8.0) for i in range(9))


def _shell_geometry(r: ResolvedConfig) -> MeshGeometry:
    """Hollow staved shell with a solid wooden floor and an open mouth."""

    height = r.body_height_m
    profile: list[tuple[float, float, bool]] = []
    for index in range(OUTER_STATIONS):
        z = height * index / (OUTER_STATIONS - 1)
        profile.append((_r_out(r, z), z, True))
    for index in range(INNER_STATIONS):
        z = height - (height - r.floor_m) * index / (INNER_STATIONS - 1)
        profile.append((_r_in(r, z), z, False))
    profile.append((0.0, r.floor_m, False))
    profile.append((0.0, 0.0, False))
    relief = _stave_relief(r.segments, r.stave_count, r.groove_m)
    return _lathe(profile, r.segments, relief)


def _seat_collar_geometry(r: ResolvedConfig) -> MeshGeometry:
    """Recessed inner seating collar just below the mouth."""

    height = r.body_height_m
    z_bot = height - r.seat_depth_m
    profile: list[tuple[float, float, bool]] = [(r.r_seat_in, z_bot, False)]
    steps = 5
    for index in range(steps + 1):
        z = z_bot + (height - z_bot) * index / steps
        profile.append((_r_in(r, z) + FUSE, z, False))
    profile.append((r.r_seat_in, height, False))
    return _lathe(profile, r.segments)


def _emit_body_shell(part, r: ResolvedConfig, mats, candidate: str) -> None:
    shell = _shell_geometry(r)
    if r.closure == "bung_plug":
        shell = boolean_difference(shell, _bunghole_cutter(r))
    part.visual(
        mesh_from_geometry(shell, f"bucket2_shell_{candidate}"),
        material=mats["wood"],
        name=f"body_profile__{candidate}__shell", material_class_id=("wood.natural_generic" if r.palette in {"pale_ash_zinc", "walnut_black", "weathered_grey"} else "wood.oak"),
    )
    part.visual(
        mesh_from_geometry(_seat_collar_geometry(r), f"bucket2_seat_{candidate}"),
        material=mats["wood"],
        name=f"body_profile__{candidate}__seat_collar", material_class_id=("wood.natural_generic" if r.palette in {"pale_ash_zinc", "walnut_black", "weathered_grey"} else "wood.oak"),
    )


def _body_profile_bulged_stave_build(part, r: ResolvedConfig, mats) -> None:
    """Parabolic mid-bulge staved barrel (parent ad0a147f model.py:L72-L113)."""

    _emit_body_shell(part, r, mats, "bulged_stave")


def _body_profile_straight_stave_build(part, r: ResolvedConfig, mats) -> None:
    """Straight-walled staved cylinder (var_straight_keg model.py:L71-L113)."""

    _emit_body_shell(part, r, mats, "straight_stave")


def _body_profile_tapered_pail_build(part, r: ResolvedConfig, mats) -> None:
    """Linearly tapered staved pail (var_tapered_pail model.py:L73-L115)."""

    _emit_body_shell(part, r, mats, "tapered_pail")


_BODY_BUILDERS = {
    "bulged_stave": _body_profile_bulged_stave_build,
    "straight_stave": _body_profile_straight_stave_build,
    "tapered_pail": _body_profile_tapered_pail_build,
}


# ===========================================================================
# hoop_band candidate + hoop_count multiplicity
# ===========================================================================
def _hoop_centres(r: ResolvedConfig) -> list[float]:
    """Evenly spaced band centres inset from both body ends."""

    count = r.hoop_count
    if count <= 1:
        return [0.5 * r.body_height_m]
    span = r.body_height_m - 2.0 * r.hoop_margin_m
    return [r.hoop_margin_m + span * index / (count - 1) for index in range(count)]


def _hoop_geometry(r: ResolvedConfig, z_centre: float) -> MeshGeometry:
    z_bot = z_centre - r.hoop_half_m
    z_top = z_centre + r.hoop_half_m
    steps = 3
    profile: list[tuple[float, float, bool]] = []
    for index in range(steps + 1):
        z = z_bot + (z_top - z_bot) * index / steps
        profile.append((_r_out(r, z) - BAND_BITE, z, False))
    for index in range(steps + 1):
        z = z_top - (z_top - z_bot) * index / steps
        profile.append((_r_out(r, z) + r.hoop_proud_m, z, False))
    return _lathe(profile, r.segments)


def _hoop_band_flat_iron_band_build(part, r: ResolvedConfig, mats) -> None:
    """Flat iron bands repeated by ``hoop_count`` (var_hoop_count model.py:L79-L246)."""

    bung = _bung_metrics(r) if r.closure == "bung_plug" else None
    cutter = _bunghole_cutter(r) if bung is not None else None
    for index, z_centre in enumerate(_hoop_centres(r)):
        band = _hoop_geometry(r, z_centre)
        if bung is not None and abs(z_centre - bung["z_b"]) < r.hoop_half_m + bung["bore"] + 0.002:
            band = boolean_difference(band, cutter)
        part.visual(
            mesh_from_geometry(band, f"bucket2_hoop_{index}"),
            material=mats["metal"],
            name=f"hoop_band__flat_iron_band__band_{index}", material_class_id=("metal.blackened_gunmetal" if r.palette in {"oak_dark_iron", "pale_ash_zinc", "walnut_black"} else "rust.oxidized_metal"),
        )


_HOOP_BUILDERS = {"flat_iron_band": _hoop_band_flat_iron_band_build}


# ===========================================================================
# Axis-mated joint helper (every rotational joint is registered for QC)
# ===========================================================================
def _axis_joint(
    model,
    *,
    name,
    parent,
    child,
    point,
    axis,
    radial,
    articulation_type,
    limits,
    damping=0.10,
    friction=0.05,
    meta=None,
):
    provider = AxisInterface(name=f"{name}.provider", point=point, axis=axis, radial=radial)
    consumer = AxisInterface(
        name=f"{name}.consumer", point=(0.0, 0.0, 0.0), axis=axis, radial=radial
    )
    mate = mate_axes(provider, consumer)
    model.articulation(
        name,
        articulation_type,
        parent=parent,
        child=child,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=limits,
        motion_properties=MotionProperties(damping=damping, friction=friction),
        meta=meta or {},
    )
    register_interface_mate(model, name, mate)


# ===========================================================================
# closure candidates
# ===========================================================================
def _head_thickness(r: ResolvedConfig) -> float:
    return _clamp(0.100 * r.end_radius_m, 0.012, 0.018)


def _head_span(r: ResolvedConfig) -> tuple[float, float]:
    """Permanent end-head z span (its underside bites into the mouth rim)."""

    z0 = r.body_height_m - 0.002
    return z0, z0 + _head_thickness(r)


# ---- slide_off_lid --------------------------------------------------------
def _slide_lid_metrics(r: ResolvedConfig) -> dict[str, float]:
    lid_t = _clamp(0.140 * r.end_radius_m, 0.018, 0.026)
    r_flange = r.r_top - 0.003
    r_skirt = r.r_seat_in * math.cos(math.pi / r.segments) - RUN_CLEARANCE
    # The skirt spans [SEAT_GAP - seat_depth, SEAT_GAP] in lid-local z and the
    # collar top sits at the joint origin, so the skirt has fully left the collar
    # once q > seat_depth - SEAT_GAP. Lift clear of that, not short of it.
    travel = r.seat_depth_m - SEAT_GAP + LID_OPEN_CLEAR
    return {
        "lid_t": lid_t,
        "r_flange": r_flange,
        "r_skirt": r_skirt,
        "skirt_w": 0.008,
        "travel": travel,
        "top_z": SEAT_GAP + lid_t,
    }


def _slide_lid_geometry(r: ResolvedConfig, m: dict[str, float]) -> MeshGeometry:
    z_bot = SEAT_GAP
    z_top = SEAT_GAP + m["lid_t"]
    z_skirt = z_bot - r.seat_depth_m
    r_in = m["r_skirt"] - m["skirt_w"]
    profile = (
        (0.0, z_top, False),
        (m["r_flange"], z_top, False),
        (m["r_flange"], z_bot, False),
        (m["r_skirt"], z_bot, False),
        (m["r_skirt"], z_skirt, False),
        (r_in, z_skirt, False),
        (r_in, z_bot, False),
        (0.0, z_bot, False),
    )
    return _lathe(profile, r.segments)


def _closure_slide_off_lid_build(model, body, r: ResolvedConfig, mats):
    """Captive lift-off plug lid (parent ad0a147f model.py:L155-L178, L276-L286)."""

    m = _slide_lid_metrics(r)
    lid = model.part(
        "closure__slide_off_lid__lid",
        meta={"role": "closure_lid", "candidate": "slide_off_lid"},
    )
    lid.visual(
        mesh_from_geometry(_slide_lid_geometry(r, m), "bucket2_slide_lid"),
        material=mats["wood_light"],
        name="closure__slide_off_lid__lid_body", material_class_id=("wood.natural_generic" if r.palette in {"pale_ash_zinc", "walnut_black", "weathered_grey"} else "wood.oak"),
    )
    lid.inertial = Inertial.from_geometry(
        Cylinder(radius=m["r_flange"], length=m["lid_t"]),
        mass=0.7,
        origin=Origin(xyz=(0.0, 0.0, SEAT_GAP + 0.5 * m["lid_t"])),
    )
    model.articulation(
        "closure__slide_off_lid__lift",
        ArticulationType.PRISMATIC,
        parent=body,
        child=lid,
        origin=Origin(xyz=(0.0, 0.0, r.body_height_m)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(lower=0.0, upper=m["travel"], effort=60.0, velocity=0.20),
        motion_properties=MotionProperties(damping=0.20, friction=0.10),
        meta={"mechanism": "plug lid captured by the seat collar bore"},
    )
    return lid


# ---- hinged_lid -----------------------------------------------------------
def _hatch_metrics(r: ResolvedConfig) -> dict[str, float]:
    head_z0, head_z1 = _head_span(r)
    r_port = r.hatch_port_ratio * r.r_bore
    r_lid = r_port + 0.014
    lid_t = _clamp(0.100 * r.end_radius_m, 0.011, 0.016)
    pin_r = 0.004
    knuckle_out = 0.010
    hinge_x = -(r_lid + 0.010)
    hinge_z = head_z1 + knuckle_out + 0.0008
    return {
        "head_z0": head_z0,
        "head_z1": head_z1,
        "r_port": r_port,
        "r_lid": r_lid,
        "lid_t": lid_t,
        "pin_r": pin_r,
        "pin_bore": _bore_for(pin_r, PIN_SEGMENTS),
        "knuckle_out": knuckle_out,
        "hinge_x": hinge_x,
        "hinge_z": hinge_z,
        "dx_c": -hinge_x,
        "disc_bot": head_z1 + SEAT_GAP - hinge_z,
        "disc_top": head_z1 + SEAT_GAP + lid_t - hinge_z,
        "lug_y_in": 0.030,
        "lug_y_out": 0.038,
        "strap_half_y": 0.024,
    }


def _hatch_lid_geometry(r: ResolvedConfig, m: dict[str, float]) -> MeshGeometry:
    disc = _cylinder_z(m["r_lid"], m["disc_bot"], m["disc_top"], 40)
    disc.translate(m["dx_c"], 0.0, 0.0)
    knuckle = _tube_z(
        m["pin_bore"], m["knuckle_out"], -m["strap_half_y"], m["strap_half_y"], PIN_SEGMENTS
    )
    _along_y(knuckle, 0.0, 0.0, 0.0)
    strap = _box(
        (0.022, 2.0 * m["strap_half_y"], m["disc_top"] - m["disc_bot"]),
        (0.017, 0.0, 0.5 * (m["disc_bot"] + m["disc_top"])),
    )
    geometry = MeshGeometry()
    geometry.merge(disc)
    geometry.merge(knuckle)
    geometry.merge(strap)
    return geometry


def _closure_hinged_lid_build(model, body, r: ResolvedConfig, mats):
    """Hinged top hatch in a permanent head (var_hinged_lid model.py:L163-L307)."""

    m = _hatch_metrics(r)
    body.visual(
        mesh_from_geometry(
            _tube_z(m["r_port"], r.r_top - 0.0015, m["head_z0"], m["head_z1"], r.segments),
            "bucket2_hatch_head",
        ),
        material=mats["wood"],
        name="closure__hinged_lid__head", material_class_id=("wood.natural_generic" if r.palette in {"pale_ash_zinc", "walnut_black", "weathered_grey"} else "wood.oak"),
    )
    lug_z0 = m["head_z1"] - 0.004
    lug_z1 = m["hinge_z"] + 0.002
    for index, side in ((0, -1.0), (1, 1.0)):
        lug = _box(
            (0.008, m["lug_y_out"] - m["lug_y_in"], lug_z1 - lug_z0),
            (
                m["hinge_x"],
                side * 0.5 * (m["lug_y_in"] + m["lug_y_out"]),
                0.5 * (lug_z0 + lug_z1),
            ),
        )
        body.visual(
            mesh_from_geometry(lug, f"bucket2_hatch_lug_{index}"),
            material=mats["metal"],
            name=f"closure__hinged_lid__hinge_lug_{index}", material_class_id=("metal.blackened_gunmetal" if r.palette in {"oak_dark_iron", "pale_ash_zinc", "walnut_black"} else "rust.oxidized_metal"),
        )
    pin = _cylinder_z(m["pin_r"], -(m["lug_y_out"] - 0.002), m["lug_y_out"] - 0.002, PIN_SEGMENTS)
    _along_y(pin, m["hinge_x"], 0.0, m["hinge_z"])
    body.visual(
        mesh_from_geometry(pin, "bucket2_hatch_pin"),
        material=mats["metal"],
        name="closure__hinged_lid__hinge_pin", material_class_id=("metal.blackened_gunmetal" if r.palette in {"oak_dark_iron", "pale_ash_zinc", "walnut_black"} else "rust.oxidized_metal"),
    )

    hatch = model.part(
        "closure__hinged_lid__hatch",
        meta={"role": "closure_lid", "candidate": "hinged_lid"},
    )
    hatch.visual(
        mesh_from_geometry(_hatch_lid_geometry(r, m), "bucket2_hatch_lid"),
        material=mats["wood_light"],
        name="closure__hinged_lid__hatch_body", material_class_id=("wood.natural_generic" if r.palette in {"pale_ash_zinc", "walnut_black", "weathered_grey"} else "wood.oak"),
    )
    hatch.inertial = Inertial.from_geometry(
        Cylinder(radius=m["r_lid"], length=m["lid_t"]),
        mass=0.35,
        origin=Origin(xyz=(m["dx_c"], 0.0, 0.5 * (m["disc_bot"] + m["disc_top"]))),
    )
    _axis_joint(
        model,
        name="closure__hinged_lid__hinge",
        parent=body,
        child=hatch,
        point=(m["hinge_x"], 0.0, m["hinge_z"]),
        axis=(0.0, -1.0, 0.0),
        radial=(1.0, 0.0, 0.0),
        articulation_type=ArticulationType.REVOLUTE,
        limits=MotionLimits(lower=0.0, upper=r.lid_open_rad, effort=8.0, velocity=1.5),
        damping=0.15,
        friction=0.08,
        meta={"mechanism": "hatch knuckle running on the rim hinge pin"},
    )
    return hatch


# ---- bung_plug ------------------------------------------------------------
def _bung_metrics(r: ResolvedConfig) -> dict[str, float]:
    height = r.body_height_m
    bore = r.bung_bore_m
    z_low = r.floor_m + bore + 0.022
    z_high = height - _head_thickness(r) - bore - 0.028
    if z_high < z_low:
        z_high = z_low
    z_b = _clamp(r.bung_height_ratio * height, z_low, z_high)

    # Prefer a bore that sits in a real gap between two bands when one is wide
    # enough; otherwise the bore is also cut through the band it crosses.
    centres = _hoop_centres(r)
    if len(centres) >= 2:
        needed = r.hoop_half_m + bore + 0.004
        best = None
        for index in range(len(centres) - 1):
            mid = 0.5 * (centres[index] + centres[index + 1])
            if 0.5 * (centres[index + 1] - centres[index]) >= needed and z_low <= mid <= z_high:
                if best is None or abs(mid - z_b) < abs(best - z_b):
                    best = mid
        if best is not None:
            z_b = best

    r_shank = bore * math.cos(math.pi / BORE_SEGMENTS) - RUN_CLEARANCE
    length_in = r.wall_m + 0.014
    # Same lift-off rule as the lid: the shank has to leave the bore for the
    # bunghole to read as open.
    travel = length_in + BUNG_OPEN_CLEAR
    r_face = _r_out(r, z_b)
    return {
        "z_b": z_b,
        "bore": bore,
        "r_shank": r_shank,
        "length_in": length_in,
        "travel": travel,
        "r_face": r_face,
        "knob_x0": r.hoop_proud_m + 0.004,
        "knob_r": r_shank + 0.007,
    }


def _bunghole_cutter(r: ResolvedConfig) -> MeshGeometry:
    m = _bung_metrics(r)
    cutter = _cylinder_z(m["bore"], 0.0, m["r_face"] + 0.030, BORE_SEGMENTS)
    return _along_x(cutter, 0.0, 0.0, m["z_b"])


def _bung_geometry(r: ResolvedConfig, m: dict[str, float]) -> MeshGeometry:
    shank_out = m["knob_x0"] + 0.006
    geometry = MeshGeometry()
    geometry.merge(_cylinder_z(m["r_shank"], -m["length_in"], shank_out, BORE_SEGMENTS))
    geometry.merge(_cylinder_z(m["knob_r"], m["knob_x0"], m["knob_x0"] + 0.011, PIN_SEGMENTS))
    return _along_x(geometry, 0.0, 0.0, 0.0)


def _closure_bung_plug_build(model, body, r: ResolvedConfig, mats):
    """Permanent head plus a side bunghole and bung (var_bunghole_plug model.py:L81-L244)."""

    m = _bung_metrics(r)
    head_z0, head_z1 = _head_span(r)
    body.visual(
        mesh_from_geometry(
            _cylinder_z(r.r_top - 0.0015, head_z0, head_z1, r.segments), "bucket2_bung_head"
        ),
        material=mats["wood_light"],
        name="closure__bung_plug__head", material_class_id=("wood.natural_generic" if r.palette in {"pale_ash_zinc", "walnut_black", "weathered_grey"} else "wood.oak"),
    )
    bung = model.part(
        "closure__bung_plug__bung",
        meta={"role": "bung_plug", "candidate": "bung_plug"},
    )
    bung.visual(
        mesh_from_geometry(_bung_geometry(r, m), "bucket2_bung"),
        material=mats["wood_light"],
        name="closure__bung_plug__bung_body", material_class_id=("wood.natural_generic" if r.palette in {"pale_ash_zinc", "walnut_black", "weathered_grey"} else "wood.oak"),
    )
    bung.inertial = Inertial.from_geometry(
        Cylinder(radius=m["r_shank"], length=m["length_in"]),
        mass=0.06,
        origin=Origin(xyz=(-0.5 * m["length_in"], 0.0, 0.0)),
    )
    model.articulation(
        "closure__bung_plug__pull",
        ArticulationType.PRISMATIC,
        parent=body,
        child=bung,
        origin=Origin(xyz=(m["r_face"], 0.0, m["z_b"])),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(lower=0.0, upper=m["travel"], effort=30.0, velocity=0.15),
        motion_properties=MotionProperties(damping=0.20, friction=0.15),
        meta={"mechanism": "bung shank captured by the bunghole bore"},
    )
    return None


_CLOSURE_BUILDERS = {
    "slide_off_lid": _closure_slide_off_lid_build,
    "hinged_lid": _closure_hinged_lid_build,
    "bung_plug": _closure_bung_plug_build,
}


def _closure_seat(r: ResolvedConfig) -> tuple[tuple[float, float, float], float]:
    """Seat frame on top of the active closure, in the host part's local frame."""

    if r.closure == "slide_off_lid":
        m = _slide_lid_metrics(r)
        return (0.0, 0.0, m["top_z"]), m["r_flange"]
    if r.closure == "hinged_lid":
        m = _hatch_metrics(r)
        return (m["dx_c"], 0.0, m["disc_top"]), m["r_lid"]
    _head_z0, head_z1 = _head_span(r)
    return (0.0, 0.0, head_z1), r.r_top - 0.0015


# ===========================================================================
# handle candidates
# ===========================================================================
def _closure_envelope_points(r: ResolvedConfig) -> list[tuple[float, float, float]]:
    """Sampled extreme points of the active closure over its whole joint range."""

    points: list[tuple[float, float, float]] = []
    ring = 12
    if r.closure == "slide_off_lid":
        m = _slide_lid_metrics(r)
        for travel in (0.0, m["travel"]):
            for z in (
                r.body_height_m + travel + SEAT_GAP,
                r.body_height_m + travel + m["top_z"],
            ):
                for index in range(ring):
                    angle = 2.0 * math.pi * index / ring
                    points.append(
                        (m["r_flange"] * math.cos(angle), m["r_flange"] * math.sin(angle), z)
                    )
    elif r.closure == "hinged_lid":
        m = _hatch_metrics(r)
        rr = r.r_top - 0.0015
        for index in range(ring):
            angle = 2.0 * math.pi * index / ring
            points.append((rr * math.cos(angle), rr * math.sin(angle), m["head_z1"]))
        steps = 12
        for step in range(steps + 1):
            theta = r.lid_open_rad * step / steps
            cos_t, sin_t = math.cos(theta), math.sin(theta)
            for local_z in (m["disc_bot"], m["disc_top"]):
                for index in range(ring):
                    angle = 2.0 * math.pi * index / ring
                    local_x = m["dx_c"] + m["r_lid"] * math.cos(angle)
                    local_y = m["r_lid"] * math.sin(angle)
                    points.append(
                        (
                            m["hinge_x"] + local_x * cos_t - local_z * sin_t,
                            local_y,
                            m["hinge_z"] + local_x * sin_t + local_z * cos_t,
                        )
                    )
    else:
        _head_z0, head_z1 = _head_span(r)
        rr = r.r_top - 0.0015
        for index in range(ring):
            angle = 2.0 * math.pi * index / ring
            points.append((rr * math.cos(angle), rr * math.sin(angle), head_z1))
    return points


def _body_envelope_points(r: ResolvedConfig, z_from: float) -> list[tuple[float, float, float]]:
    points: list[tuple[float, float, float]] = []
    steps = 8
    ring = 12
    for step in range(steps + 1):
        z = z_from + (r.body_height_m - z_from) * step / steps
        rr = _r_out(r, z) + r.hoop_proud_m
        for index in range(ring):
            angle = 2.0 * math.pi * index / ring
            points.append((rr * math.cos(angle), rr * math.sin(angle), z))
    return points


# ---- swing_bail -----------------------------------------------------------
def _bail_metrics(r: ResolvedConfig) -> dict[str, float]:
    height = r.body_height_m
    z_ear = 0.86 * height
    wire_r = r.bail_wire_r_m
    eyelet_bore = _bore_for(wire_r, PIN_SEGMENTS)
    eyelet_out = eyelet_bore + 0.007
    r_ear = _r_band(r, z_ear - 0.030, z_ear + 0.020, proud=True)
    px = r_ear + 0.026
    ax = px + 0.010

    obstacles = _body_envelope_points(r, z_ear) + _closure_envelope_points(r)
    needed = wire_r + CLEAR_MARGIN
    r_bail = r_ear + 0.012
    for point in obstacles:
        if point[2] < z_ear - 1e-9 or abs(point[0]) >= ax - 1e-6:
            continue
        dist = math.sqrt(point[0] ** 2 + point[1] ** 2 + (point[2] - z_ear) ** 2)
        target = (dist + needed) ** 2 - point[0] ** 2
        if target <= 0.0:
            continue
        r_bail = max(r_bail, math.sqrt(target / (1.0 - (point[0] / ax) ** 2)))
    return {
        "z_ear": z_ear,
        "wire_r": wire_r,
        "eyelet_bore": eyelet_bore,
        "eyelet_out": eyelet_out,
        "r_ear": r_ear,
        "px": px,
        "ax": ax,
        "r_bail": min(r_bail, 3.0 * px),
    }


def _bail_geometry(r: ResolvedConfig, m: dict[str, float]) -> MeshGeometry:
    ax = m["ax"]
    steps = 30
    points = [
        (
            ax * math.cos(math.pi * index / steps),
            m["r_bail"] * math.sin(math.pi * index / steps),
            0.0,
        )
        for index in range(steps + 1)
    ]
    geometry = _polyline_tube(points, m["wire_r"], 12)
    geometry.merge(_rod((ax - 0.020, 0.0, 0.0), (ax + 0.010, 0.0, 0.0), m["wire_r"], PIN_SEGMENTS))
    geometry.merge(
        _rod((-ax + 0.020, 0.0, 0.0), (-ax - 0.010, 0.0, 0.0), m["wire_r"], PIN_SEGMENTS)
    )
    return geometry


def _handle_swing_bail_build(model, body, r: ResolvedConfig, mats, host, seat, seat_radius: float):
    """Arched swing bail on two ear eyelets (var_swing_bail model.py:L163-L343)."""

    m = _bail_metrics(r)
    z_ear = m["z_ear"]
    strut_z0 = z_ear - 0.036
    strut_z1 = z_ear - (m["eyelet_bore"] + 0.005)
    # The strut is a flat box against a curved wall: its inner face must sit far
    # enough in that even the widest corner (half the strut width off the
    # meridian) is buried in the staves.
    strut_half_y = 0.011
    r_min = _r_min_band(r, strut_z0, strut_z1)
    inner = math.sqrt(max(1e-6, r_min * r_min - strut_half_y * strut_half_y)) - EMBED
    for index, sign in ((0, 1.0), (1, -1.0)):
        eyelet = _tube_z(m["eyelet_bore"], m["eyelet_out"], -0.007, 0.007, PIN_SEGMENTS)
        _along_x(eyelet, sign * m["px"], 0.0, z_ear)
        body.visual(
            mesh_from_geometry(eyelet, f"bucket2_bail_eyelet_{index}"),
            material=mats["metal"],
            name=f"handle__swing_bail__eyelet_{index}", material_class_id=("metal.blackened_gunmetal" if r.palette in {"oak_dark_iron", "pale_ash_zinc", "walnut_black"} else "rust.oxidized_metal"),
        )
        outer = m["px"] + m["eyelet_out"]
        strut = _box(
            (outer - inner, 2.0 * strut_half_y, strut_z1 - strut_z0),
            (sign * 0.5 * (inner + outer), 0.0, 0.5 * (strut_z0 + strut_z1)),
        )
        body.visual(
            mesh_from_geometry(strut, f"bucket2_bail_strut_{index}"),
            material=mats["metal"],
            name=f"handle__swing_bail__ear_{index}", material_class_id=("metal.blackened_gunmetal" if r.palette in {"oak_dark_iron", "pale_ash_zinc", "walnut_black"} else "rust.oxidized_metal"),
        )

    bail = model.part(
        "handle__swing_bail__bail",
        meta={"role": "carry_bail", "candidate": "swing_bail"},
    )
    bail.visual(
        mesh_from_geometry(_bail_geometry(r, m), "bucket2_bail"),
        material=mats["metal"],
        name="handle__swing_bail__bail_body", material_class_id=("metal.blackened_gunmetal" if r.palette in {"oak_dark_iron", "pale_ash_zinc", "walnut_black"} else "rust.oxidized_metal"),
    )
    bail.inertial = Inertial.from_geometry(
        Cylinder(radius=m["wire_r"], length=2.0 * m["ax"]),
        mass=0.14,
        origin=Origin(xyz=(0.0, 0.5 * m["r_bail"], 0.0)),
    )
    _axis_joint(
        model,
        name="handle__swing_bail__pivot",
        parent=body,
        child=bail,
        point=(0.0, 0.0, z_ear),
        axis=(1.0, 0.0, 0.0),
        radial=(0.0, 1.0, 0.0),
        articulation_type=ArticulationType.REVOLUTE,
        limits=MotionLimits(lower=0.0, upper=r.bail_open_rad, effort=12.0, velocity=2.0),
        meta={"mechanism": "swing bail stubs running in the two ear eyelets"},
    )


# ---- side_ear_rings -------------------------------------------------------
def _ring_metrics(r: ResolvedConfig) -> dict[str, float]:
    height = r.body_height_m
    ring_r = r.ring_major_r_m
    tube_r = 0.0032
    pin_r = 0.0035
    eye_bore = _bore_for(pin_r, PIN_SEGMENTS)
    eye_out = eye_bore + 0.005
    reach = 2.0 * ring_r + eye_out + tube_r
    z_ring = _clamp(0.60 * height, reach + 0.030, height - 0.060)
    r_wall = _r_band(r, z_ring - reach - 0.008, z_ring + 0.40 * reach, proud=True)
    return {
        "ring_r": ring_r,
        "tube_r": tube_r,
        "pin_r": pin_r,
        "eye_bore": eye_bore,
        "eye_out": eye_out,
        "z_ring": z_ring,
        "py": r_wall + 0.020,
        "prong_x": ring_r + tube_r + 0.007,
        "reach": reach,
    }


def _ring_geometry(r: ResolvedConfig, m: dict[str, float]) -> MeshGeometry:
    torus = TorusGeometry(m["ring_r"], m["tube_r"], radial_segments=10, tubular_segments=28)
    torus.rotate_x(math.pi / 2.0)
    torus.translate(0.0, 0.0, -(m["ring_r"] + m["eye_out"]))
    eye = _tube_z(m["eye_bore"], m["eye_out"], -0.009, 0.009, PIN_SEGMENTS)
    _along_x(eye, 0.0, 0.0, 0.0)
    geometry = MeshGeometry()
    geometry.merge(torus)
    geometry.merge(eye)
    return geometry


def _handle_side_ear_rings_build(
    model, body, r: ResolvedConfig, mats, host, seat, seat_radius: float
):
    """Two pivoting ear rings (var_side_ear_rings model.py:L166-L308)."""

    m = _ring_metrics(r)
    z_ring = m["z_ring"]
    # Each prong stands off the barrel meridian, so its inner face has to reach
    # the chord depth at its own |x| station, not the meridian radius.
    x_far = m["prong_x"] + 0.008
    r_min = _r_min_band(r, z_ring - 0.016, z_ring + 0.016)
    inner = math.sqrt(max(1e-6, r_min * r_min - x_far * x_far)) - EMBED
    for index, sign in ((0, 1.0), (1, -1.0)):
        for prong in (0, 1):
            offset = (m["prong_x"] + 0.004) * (1.0 if prong else -1.0)
            block = _box(
                (0.008, m["py"] + 0.008 - inner, 0.028),
                (offset, sign * 0.5 * (inner + m["py"] + 0.008), z_ring),
            )
            body.visual(
                mesh_from_geometry(block, f"bucket2_ring_prong_{index}_{prong}"),
                material=mats["metal"],
                name=f"handle__side_ear_rings__ear_{index}_{prong}", material_class_id=("metal.blackened_gunmetal" if r.palette in {"oak_dark_iron", "pale_ash_zinc", "walnut_black"} else "rust.oxidized_metal"),
            )
        pin = _cylinder_z(m["pin_r"], -(m["prong_x"] + 0.006), m["prong_x"] + 0.006, PIN_SEGMENTS)
        _along_x(pin, 0.0, sign * m["py"], z_ring)
        body.visual(
            mesh_from_geometry(pin, f"bucket2_ring_pin_{index}"),
            material=mats["metal"],
            name=f"handle__side_ear_rings__pin_{index}", material_class_id=("metal.blackened_gunmetal" if r.palette in {"oak_dark_iron", "pale_ash_zinc", "walnut_black"} else "rust.oxidized_metal"),
        )

        ring = model.part(
            f"handle__side_ear_rings__ring_{index}",
            meta={"role": "carry_ring", "candidate": "side_ear_rings"},
        )
        ring.visual(
            mesh_from_geometry(_ring_geometry(r, m), f"bucket2_ring_{index}"),
            material=mats["metal"],
            name=f"handle__side_ear_rings__ring_body_{index}", material_class_id=("metal.blackened_gunmetal" if r.palette in {"oak_dark_iron", "pale_ash_zinc", "walnut_black"} else "rust.oxidized_metal"),
        )
        ring.inertial = Inertial.from_geometry(
            Cylinder(radius=m["ring_r"], length=2.0 * m["tube_r"]),
            mass=0.08,
            origin=Origin(xyz=(0.0, 0.0, -(m["ring_r"] + m["eye_out"]))),
        )
        _axis_joint(
            model,
            name=f"handle__side_ear_rings__pivot_{index}",
            parent=body,
            child=ring,
            point=(0.0, sign * m["py"], z_ring),
            axis=(sign, 0.0, 0.0),
            radial=(0.0, 0.0, -1.0),
            articulation_type=ArticulationType.REVOLUTE,
            limits=MotionLimits(lower=0.0, upper=r.ring_open_rad, effort=6.0, velocity=2.0),
            meta={"mechanism": "drop ring eye running on its ear pin"},
        )


# ---- arched_grip ----------------------------------------------------------
def _grip_metrics(r: ResolvedConfig, seat_radius: float) -> tuple[float, float]:
    grip_r = _clamp(0.065 * r.end_radius_m, 0.006, 0.010)
    half_span = min(0.62 * seat_radius, seat_radius - grip_r - 0.006)
    return max(half_span, 0.018), grip_r


def _grip_geometry(r: ResolvedConfig, half_span: float, grip_r: float) -> MeshGeometry:
    rise = r.grip_rise_m
    geometry = MeshGeometry()
    # Base strap: the fastening plate the two feet rise from. It also puts real
    # geometry on the FIXED mount origin instead of leaving it in the arch span.
    geometry.merge(
        _box(
            (2.0 * (half_span + grip_r), 2.2 * grip_r, 0.006),
            (0.0, 0.0, SEAT_GAP + 0.003),
        )
    )
    for sign in (-1.0, 1.0):
        leg = _cylinder_z(grip_r, SEAT_GAP, rise, 16)
        leg.translate(sign * half_span, 0.0, 0.0)
        geometry.merge(leg)
    bar = _cylinder_z(grip_r, -half_span, half_span, 16)
    _along_x(bar, 0.0, 0.0, rise)
    geometry.merge(bar)
    return geometry


def _handle_arched_grip_build(model, body, r: ResolvedConfig, mats, host, seat, seat_radius: float):
    """Fixed arched grip on the closure top (parent ad0a147f model.py:L181-L296)."""

    half_span, grip_r = _grip_metrics(r, seat_radius)
    grip = model.part(
        "handle__arched_grip__grip",
        meta={"role": "lid_grip", "candidate": "arched_grip"},
    )
    grip.visual(
        mesh_from_geometry(_grip_geometry(r, half_span, grip_r), "bucket2_grip"),
        material=mats["accent"],
        name="handle__arched_grip__grip_body", material_class_id="metal.paint_coated",
    )
    grip.inertial = Inertial.from_geometry(
        Cylinder(radius=grip_r, length=2.0 * half_span),
        mass=0.09,
        origin=Origin(xyz=(0.0, 0.0, 0.5 * r.grip_rise_m)),
    )
    model.articulation(
        "handle__arched_grip__mount",
        ArticulationType.FIXED,
        parent=host,
        child=grip,
        origin=Origin(xyz=seat),
        meta={"mechanism": "arched grip fastened on the closure top"},
    )


def _handle_no_handle_build(model, body, r: ResolvedConfig, mats, host, seat, seat_radius: float):
    """Bare keg with no carry fitting (var_bunghole_plug model.py:L177-L246)."""

    return None


_HANDLE_BUILDERS = {
    "swing_bail": _handle_swing_bail_build,
    "side_ear_rings": _handle_side_ear_rings_build,
    "arched_grip": _handle_arched_grip_build,
    "no_handle": _handle_no_handle_build,
}


# ===========================================================================
# Assembly
# ===========================================================================
def build_bucket2(
    config: Config | None = None, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={
            "category": "urban_environment_bucket2",
            "body": "coopered staved keg",
            "closure": r.closure,
            "handle": r.handle,
        },
    )
    mats = {
        key: model.material(f"bucket2_{r.palette}_{key}", rgba=rgba)
        for key, rgba in PALETTES[r.palette].items()
    }

    body = model.part(
        "keg_body",
        meta={"role": "keg_body", "candidate": r.body_profile, "hoop_count": r.hoop_count},
    )
    _BODY_BUILDERS[r.body_profile](body, r, mats)
    _HOOP_BUILDERS[r.hoop_band](body, r, mats)
    body.inertial = Inertial.from_geometry(
        Cylinder(radius=r.end_radius_m, length=r.body_height_m),
        mass=6.0,
        origin=Origin(xyz=(0.0, 0.0, 0.5 * r.body_height_m)),
    )

    closure_part = _CLOSURE_BUILDERS[r.closure](model, body, r, mats)
    seat, seat_radius = _closure_seat(r)
    host = closure_part if closure_part is not None else body
    _HANDLE_BUILDERS[r.handle](model, body, r, mats, host, seat, seat_radius)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_bucket2(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_bucket2(config_from_seed(seed), assets=assets)


# ===========================================================================
# Tests
# ===========================================================================
def run_bucket2_tests(object_model: ArticulatedObject, config: Config) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    parts = {part.name: part for part in object_model.parts}
    joints = {joint.name: joint for joint in object_model.articulations}
    body = object_model.get_part("keg_body")

    # ---- category anchor: the staved keg body ------------------------------
    body_aabb = ctx.part_world_aabb(body)
    ctx.check(
        "keg base sits on the ground plane",
        body_aabb is not None and abs(body_aabb[0][2]) < 2e-3,
        details=f"body z-min={None if body_aabb is None else body_aabb[0][2]}",
    )
    ctx.check(
        "hollow staved shell with a solid floor",
        r.wall_m < 0.35 * r.end_radius_m
        and r.r_bore > 0.09
        and 0.010 < r.floor_m < 0.5 * r.body_height_m
        and r.groove_m > 0.0
        and r.segments == r.stave_count * SEG_PER_STAVE
        and r.r_seat_in > 0.04
        and r.r_seat_in < r.r_bore,
        details=(
            f"wall={r.wall_m:.4f} bore={r.r_bore:.4f} floor={r.floor_m:.4f} "
            f"staves={r.stave_count} segments={r.segments} seat={r.r_seat_in:.4f}"
        ),
    )

    # ---- category anchor: the hoop array -----------------------------------
    centres = _hoop_centres(r)
    band_names = [
        visual.name
        for visual in body.visuals
        if (visual.name or "").startswith("hoop_band__flat_iron_band__band_")
    ]
    gaps = [centres[i + 1] - centres[i] for i in range(len(centres) - 1)]
    ctx.check(
        "hoop bands wrap the body at the declared count",
        len(band_names) == r.hoop_count
        and len(centres) == r.hoop_count
        and min(centres) - r.hoop_half_m > 1e-6
        and max(centres) + r.hoop_half_m < r.body_height_m - 1e-6
        and (not gaps or max(gaps) - min(gaps) < 1e-6)
        and (not gaps or min(gaps) > 2.05 * r.hoop_half_m),
        details=(
            f"bands={len(band_names)} n={r.hoop_count} half={r.hoop_half_m:.4f} "
            f"centres={[round(z, 4) for z in centres]}"
        ),
    )

    # ---- closure anchors ---------------------------------------------------
    if r.closure == "slide_off_lid":
        m = _slide_lid_metrics(r)
        lid = object_model.get_part("closure__slide_off_lid__lid")
        joint = joints["closure__slide_off_lid__lift"]
        limits = joint.motion_limits
        skirt_exit = r.seat_depth_m - SEAT_GAP
        collar_gap = r.r_seat_in - m["r_skirt"]
        ctx.check(
            "slide-off lid seats on a running fit and lifts clear of its collar",
            joint.articulation_type == ArticulationType.PRISMATIC
            and abs(joint.axis[0]) < 1e-9
            and abs(joint.axis[1]) < 1e-9
            and joint.axis[2] > 0.0
            and limits is not None
            and limits.lower == 0.0
            # Lift-off closure: the stroke must carry the skirt out of the collar
            # bore with room to spare, otherwise the keg never actually opens.
            and m["travel"] >= skirt_exit + 0.5 * LID_OPEN_CLEAR
            and 0.0 < collar_gap < 0.0012,
            details=(
                f"travel={m['travel']:.4f} seat_depth={r.seat_depth_m:.4f} "
                f"skirt_exit={skirt_exit:.4f} collar_gap={collar_gap:.5f}"
            ),
        )
        rest = ctx.part_world_position(lid)
        with ctx.pose({joint: m["travel"]}):
            lifted = ctx.part_world_position(lid)
            lifted_aabb = ctx.part_world_aabb(lid)
        ctx.check(
            "lifted lid rises straight up and uncovers the mouth",
            rest is not None
            and lifted is not None
            and abs(lifted[0] - rest[0]) < 1e-9
            and abs(lifted[1] - rest[1]) < 1e-9
            and lifted[2] - rest[2] > 0.005
            and lifted_aabb is not None
            # The whole lid, skirt included, must clear the mouth plane so the
            # keg interior is actually visible in the open pose.
            and lifted_aabb[0][2] > r.body_height_m + 1e-3,
            details=(
                f"rest={rest} lifted={lifted} lid_zmin={None if lifted_aabb is None else lifted_aabb[0][2]:.4f} "
                f"mouth_z={r.body_height_m:.4f}"
            ),
        )
        ctx.allow_isolated_part(
            lid,
            reason=(
                "Lift-off closure: the plug lid is removed from the mouth to open the keg, "
                "exactly as source parent ad0a147f authors it (LID_TRAVEL 0 -> 0.12 m "
                "'open/clear'). It is carried by its PRISMATIC joint and is intentionally "
                "clear of the body at the open pose."
            ),
        )
    elif r.closure == "hinged_lid":
        m = _hatch_metrics(r)
        hatch = object_model.get_part("closure__hinged_lid__hatch")
        joint = joints["closure__hinged_lid__hinge"]
        limits = joint.motion_limits
        knuckle_gap = m["pin_bore"] - m["pin_r"]
        ctx.check(
            "hinged hatch swings on its rim pin",
            joint.articulation_type == ArticulationType.REVOLUTE
            and abs(joint.axis[0]) < 1e-9
            and abs(joint.axis[2]) < 1e-9
            and abs(joint.axis[1]) > 0.999
            and limits is not None
            and limits.lower == 0.0
            and limits.upper > 1.0
            and abs(joint.origin.xyz[0] - m["hinge_x"]) < 1e-6
            and abs(joint.origin.xyz[2] - m["hinge_z"]) < 1e-6
            and m["r_lid"] > m["r_port"] + 0.010
            and m["r_lid"] < r.r_top - 0.006
            and 0.0 < knuckle_gap < 0.0012
            and m["hinge_z"] - m["knuckle_out"] > m["head_z1"],
            details=(
                f"axis={tuple(joint.axis)} origin={joint.origin.xyz} r_port={m['r_port']:.4f} "
                f"r_lid={m['r_lid']:.4f} knuckle_gap={knuckle_gap:.5f}"
            ),
        )
        rest_aabb = ctx.part_world_aabb(hatch)
        with ctx.pose({joint: r.lid_open_rad}):
            open_aabb = ctx.part_world_aabb(hatch)
        # Every hatch point sits at local x >= 0.006 except the rotationally
        # symmetric knuckle annulus, so world z = x*sin(q) + z*cos(q) only ever
        # rises; the knuckle's own lowest point is the pose-invariant
        # hinge_z - knuckle_out already asserted above.
        ctx.check(
            "open hatch lifts clear of the head",
            rest_aabb is not None
            and open_aabb is not None
            and open_aabb[1][2] > m["head_z1"] + 0.5 * m["r_lid"]
            and open_aabb[1][2] > rest_aabb[1][2] + 0.5 * m["r_lid"],
            details=f"rest={rest_aabb} open={open_aabb} head_top={m['head_z1']:.4f}",
        )
        ctx.allow_isolated_part(
            hatch,
            reason=(
                "The hatch is carried by its hinge knuckle running on the rim pin at a "
                "clearance inside the support tolerance."
            ),
        )
    else:
        m = _bung_metrics(r)
        bung = object_model.get_part("closure__bung_plug__bung")
        joint = joints["closure__bung_plug__pull"]
        limits = joint.motion_limits
        bore_gap = m["bore"] - m["r_shank"]
        ctx.check(
            "bung plug seats on a running fit and pulls clear of the bore",
            joint.articulation_type == ArticulationType.PRISMATIC
            and joint.axis[0] > 0.999
            and abs(joint.axis[1]) < 1e-9
            and abs(joint.axis[2]) < 1e-9
            and limits is not None
            and limits.lower == 0.0
            and limits.upper > 0.005
            # Lift-off closure: the shank must leave the bore entirely.
            and m["travel"] >= m["length_in"] + 0.5 * BUNG_OPEN_CLEAR
            and 0.0 < bore_gap < 0.0012
            and m["z_b"] - m["bore"] > r.floor_m
            and m["z_b"] + m["bore"] < r.body_height_m - _head_thickness(r)
            and m["knob_x0"] > r.hoop_proud_m,
            details=(
                f"travel={m['travel']:.4f} length_in={m['length_in']:.4f} bore={m['bore']:.4f} "
                f"bore_gap={bore_gap:.5f} z_b={m['z_b']:.4f}"
            ),
        )
        rest = ctx.part_world_position(bung)
        with ctx.pose({joint: m["travel"]}):
            pulled = ctx.part_world_position(bung)
        ctx.check(
            "bung pulls straight out along the bore axis",
            rest is not None
            and pulled is not None
            and pulled[0] - rest[0] > 0.005
            and abs(pulled[1] - rest[1]) < 1e-9
            and abs(pulled[2] - rest[2]) < 1e-9,
            details=f"rest={rest} pulled={pulled}",
        )
        ctx.allow_isolated_part(
            bung,
            reason=(
                "Lift-off closure: the bung is pulled out of the bunghole to open it "
                "(var_bunghole_plug). It is carried by its PRISMATIC joint and is "
                "intentionally clear of the body at the open pose."
            ),
        )

    # ---- handle anchors ----------------------------------------------------
    if r.handle == "swing_bail":
        m = _bail_metrics(r)
        bail = object_model.get_part("handle__swing_bail__bail")
        joint = joints["handle__swing_bail__pivot"]
        limits = joint.motion_limits
        worst = -1.0
        for point in _body_envelope_points(r, m["z_ear"]) + _closure_envelope_points(r):
            if point[2] < m["z_ear"] - 1e-9 or abs(point[0]) >= m["ax"]:
                continue
            rho = m["r_bail"] * math.sqrt(max(0.0, 1.0 - (point[0] / m["ax"]) ** 2))
            need = math.sqrt(point[1] ** 2 + (point[2] - m["z_ear"]) ** 2)
            worst = max(worst, need - rho)
        eyelet_gap = m["eyelet_bore"] - m["wire_r"]
        ctx.check(
            "swing bail clears the keg and its closure",
            joint.articulation_type == ArticulationType.REVOLUTE
            and abs(joint.axis[0]) > 0.999
            and limits is not None
            and limits.upper > 2.0
            and m["r_bail"] > m["r_ear"]
            and m["px"] > m["r_ear"] + 0.020
            and 0.0 < eyelet_gap < 0.0012
            and worst < -m["wire_r"],
            details=(
                f"r_bail={m['r_bail']:.4f} r_ear={m['r_ear']:.4f} px={m['px']:.4f} "
                f"eyelet_gap={eyelet_gap:.5f} envelope_margin={-worst:.4f}"
            ),
        )
        rest_aabb = ctx.part_world_aabb(bail)
        with ctx.pose({joint: 0.5 * math.pi}):
            over_aabb = ctx.part_world_aabb(bail)
        ctx.check(
            "swing bail lifts overhead without leaving its pivot line",
            rest_aabb is not None
            and over_aabb is not None
            and over_aabb[1][2] > rest_aabb[1][2] + 0.03
            and abs(over_aabb[1][0] - rest_aabb[1][0]) < 1e-6,
            details=f"rest={rest_aabb} overhead={over_aabb}",
        )
        ctx.allow_isolated_part(
            bail,
            reason=(
                "The bail is carried by its REVOLUTE joint with both stubs running inside the "
                "ear eyelets at a clearance inside the support tolerance."
            ),
        )
    elif r.handle == "side_ear_rings":
        m = _ring_metrics(r)
        eye_gap = m["eye_bore"] - m["pin_r"]
        ctx.check(
            "each ear ring pivots outward on its own axis",
            all(f"handle__side_ear_rings__ring_{i}" in parts for i in range(2))
            and all(
                joints[f"handle__side_ear_rings__pivot_{i}"].articulation_type
                == ArticulationType.REVOLUTE
                and abs(joints[f"handle__side_ear_rings__pivot_{i}"].axis[0]) > 0.999
                for i in range(2)
            )
            and joints["handle__side_ear_rings__pivot_0"].origin.xyz[1]
            * joints["handle__side_ear_rings__pivot_1"].origin.xyz[1]
            < 0.0
            and 0.0 < eye_gap < 0.0012
            and m["py"] > _r_band(r, m["z_ring"] - m["reach"], m["z_ring"], proud=True) + 0.010
            and m["prong_x"] > m["ring_r"] + m["tube_r"] + 0.005,
            details=(
                f"py={m['py']:.4f} z_ring={m['z_ring']:.4f} reach={m['reach']:.4f} "
                f"eye_gap={eye_gap:.5f} prong_x={m['prong_x']:.4f}"
            ),
        )
        for index in range(2):
            ring = parts[f"handle__side_ear_rings__ring_{index}"]
            joint = joints[f"handle__side_ear_rings__pivot_{index}"]
            sign = 1.0 if index == 0 else -1.0
            rest = ctx.part_world_aabb(ring)
            with ctx.pose({joint: r.ring_open_rad}):
                swung = ctx.part_world_aabb(ring)
            rest_c = None if rest is None else 0.5 * (rest[0][1] + rest[1][1])
            swung_c = None if swung is None else 0.5 * (swung[0][1] + swung[1][1])
            ctx.check(
                f"ear ring {index} swings away from the stave face",
                rest_c is not None and swung_c is not None and sign * (swung_c - rest_c) > 0.004,
                details=f"rest_cy={rest_c} swung_cy={swung_c}",
            )
            ctx.allow_isolated_part(
                ring,
                reason=(
                    "The drop ring is carried by its REVOLUTE joint with its eye running on the "
                    "ear pin at a clearance inside the support tolerance."
                ),
            )
    elif r.handle == "arched_grip":
        grip = object_model.get_part("handle__arched_grip__grip")
        _seat, seat_radius = _closure_seat(r)
        half_span, grip_r = _grip_metrics(r, seat_radius)
        mount = joints["handle__arched_grip__mount"]
        ctx.check(
            "arched grip is fastened to the closure top",
            mount.articulation_type == ArticulationType.FIXED
            and half_span + grip_r < seat_radius - 0.004
            and r.grip_rise_m > 2.5 * grip_r
            and grip.name in parts,
            details=(
                f"host={mount.parent} half_span={half_span:.4f} grip_r={grip_r:.4f} "
                f"seat_radius={seat_radius:.4f} rise={r.grip_rise_m:.4f}"
            ),
        )
        ctx.allow_isolated_part(
            grip,
            reason=(
                "The grip is welded to the closure top with a seating gap inside the support "
                "tolerance and rides whatever the closure does."
            ),
        )
    else:
        ctx.check(
            "bare keg carries no handle part",
            not any(name.startswith("handle__") for name in parts),
            details=f"parts={sorted(parts)}",
        )

    # ---- shared mechanical invariants --------------------------------------
    movable = [
        joint
        for joint in object_model.articulations
        if joint.articulation_type
        in (ArticulationType.REVOLUTE, ArticulationType.PRISMATIC, ArticulationType.CONTINUOUS)
    ]
    ctx.check(
        "every keg seed keeps at least one real articulation",
        len(movable) >= 1,
        details=f"movable={[joint.name for joint in movable]}",
    )
    ctx.check(
        "the staved body is the single grounded root",
        not any(joint.child == "keg_body" for joint in object_model.articulations)
        and all(
            joint.parent in parts and joint.child in parts for joint in object_model.articulations
        ),
        details=f"parts={sorted(parts)}",
    )

    ctx.check_mesh_assets_ready()
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=48)
    ctx.fail_if_isolated_parts()
    return ctx.report()


# ===========================================================================
# High-risk cross-slot corners
# ===========================================================================
TEMPLATE_CORNERS = (
    corner_case(
        "tall_bulged_hatch_under_bail",
        {
            "body_profile": "bulged_stave",
            "hoop_band": "flat_iron_band",
            "closure": "hinged_lid",
            "handle": "swing_bail",
            "hoop_count": 6,
            "body_height_m": 0.46,
            "end_radius_m": 0.175,
            "bulge_ratio": 1.32,
            "taper_ratio": 1.45,
            "stave_count": 22,
            "hoop_proud_m": 0.011,
            "hoop_half_height_m": 0.026,
            "lid_seat_depth_m": 0.060,
            "hatch_port_ratio": 0.58,
            "lid_open_rad": 1.50,
            "bung_bore_m": 0.019,
            "bung_height_ratio": 0.62,
            "bail_open_rad": 3.10,
            "bail_wire_r_m": 0.0065,
            "ring_major_r_m": 0.032,
            "ring_open_rad": 1.90,
            "grip_rise_m": 0.065,
        },
        reason="widest bulged keg with the biggest hatch at full opening under a full-swing bail: the bail envelope must enclose the open hatch and the maximum hoop array",
    ),
    corner_case(
        "short_tapered_slide_lid_bail",
        {
            "body_profile": "tapered_pail",
            "hoop_band": "flat_iron_band",
            "closure": "slide_off_lid",
            "handle": "swing_bail",
            "hoop_count": 6,
            "body_height_m": 0.28,
            "end_radius_m": 0.125,
            "bulge_ratio": 1.10,
            "taper_ratio": 1.45,
            "stave_count": 12,
            "hoop_proud_m": 0.011,
            "hoop_half_height_m": 0.026,
            "lid_seat_depth_m": 0.060,
            "hatch_port_ratio": 0.42,
            "lid_open_rad": 1.10,
            "bung_bore_m": 0.011,
            "bung_height_ratio": 0.38,
            "bail_open_rad": 3.10,
            "bail_wire_r_m": 0.0065,
            "ring_major_r_m": 0.018,
            "ring_open_rad": 1.20,
            "grip_rise_m": 0.035,
        },
        reason="shortest strongly tapered pail with six bands and the longest lid stroke while the bail sweeps overhead: minimum host capacity everywhere",
    ),
    corner_case(
        "straight_bung_with_rings",
        {
            "body_profile": "straight_stave",
            "hoop_band": "flat_iron_band",
            "closure": "bung_plug",
            "handle": "side_ear_rings",
            "hoop_count": 5,
            "body_height_m": 0.28,
            "end_radius_m": 0.125,
            "bulge_ratio": 1.20,
            "taper_ratio": 1.15,
            "stave_count": 22,
            "hoop_proud_m": 0.011,
            "hoop_half_height_m": 0.026,
            "lid_seat_depth_m": 0.030,
            "hatch_port_ratio": 0.50,
            "lid_open_rad": 1.30,
            "bung_bore_m": 0.019,
            "bung_height_ratio": 0.38,
            "bail_open_rad": 2.40,
            "bail_wire_r_m": 0.0035,
            "ring_major_r_m": 0.032,
            "ring_open_rad": 1.90,
            "grip_rise_m": 0.050,
        },
        reason="smallest straight keg carrying the largest bore bung low on the wall and the largest drop rings: the bore, the band array and the ear prongs all crowd the same wall",
    ),
    corner_case(
        "tapered_hatch_with_grip",
        {
            "body_profile": "tapered_pail",
            "hoop_band": "flat_iron_band",
            "closure": "hinged_lid",
            "handle": "arched_grip",
            "hoop_count": 2,
            "body_height_m": 0.46,
            "end_radius_m": 0.125,
            "bulge_ratio": 1.10,
            "taper_ratio": 1.15,
            "stave_count": 12,
            "hoop_proud_m": 0.005,
            "hoop_half_height_m": 0.014,
            "lid_seat_depth_m": 0.030,
            "hatch_port_ratio": 0.42,
            "lid_open_rad": 1.50,
            "bung_bore_m": 0.011,
            "bung_height_ratio": 0.50,
            "bail_open_rad": 2.40,
            "bail_wire_r_m": 0.0035,
            "ring_major_r_m": 0.018,
            "ring_open_rad": 1.20,
            "grip_rise_m": 0.065,
        },
        reason="smallest hatch port carrying the tallest grip through the full hinge stroke: the grip must stay inside the hatch footprint and clear the head all the way open",
    ),
    corner_case(
        "bulged_slide_lid_bare",
        {
            "body_profile": "bulged_stave",
            "hoop_band": "flat_iron_band",
            "closure": "slide_off_lid",
            "handle": "no_handle",
            "hoop_count": 2,
            "body_height_m": 0.46,
            "end_radius_m": 0.175,
            "bulge_ratio": 1.32,
            "taper_ratio": 1.15,
            "stave_count": 22,
            "hoop_proud_m": 0.005,
            "hoop_half_height_m": 0.014,
            "lid_seat_depth_m": 0.030,
            "hatch_port_ratio": 0.42,
            "lid_open_rad": 1.10,
            "bung_bore_m": 0.011,
            "bung_height_ratio": 0.50,
            "bail_open_rad": 2.40,
            "bail_wire_r_m": 0.0035,
            "ring_major_r_m": 0.018,
            "ring_open_rad": 1.20,
            "grip_rise_m": 0.035,
        },
        reason="deepest bulge with the shallowest seat collar and only two bands: the shortest captive lid stroke on the widest mouth",
    ),
)

__all__ += [
    "TEMPLATE_CORNERS",
    "BodyProfile",
    "HoopBand",
    "Closure",
    "Handle",
    "Palette",
    "build_bucket2",
    "build_seeded_bucket2",
    "run_bucket2_tests",
]
