# SPDX-License-Identifier: Apache-2.0

"""Agricultural / Seed spreader modular template.

Broadcast/drop seed (fertilizer) spreader: a hopper feeds seed through a sliding
flow gate and chute onto a rotary broadcast spinner (disc + N radial vanes) — or
a drop bar (with an internal agitator) — and rolls on ground wheels, pushed by a
T-handle or towed by a drawbar/hitch.

Sourced from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/seed_spreader.md`` and the
``seed_spreader`` 5-star pool (2 origins + 5 slot-fork variants), all synced under
``data/records/``:

  * push origin  A ``rec_use-..._155130`` — square_taper hopper + T-handle + 2 white
    wheels + broadcast spinner; wheels/spinner CONTINUOUS, lever REVOLUTE, gate
    PRISMATIC.  Loop-clean base; hopper/frame/chute fused into one ``spreader`` part.
  * tow origin   B ``rec_use-..._034216`` — rounded_square hopper + red tube frame +
    drawbar/hitch + big turf wheels + disc+3-vane spinner.
  * variants: ``hopper_conical`` (③ Lathe funnel), ``frame_caster`` (wheels 2→3),
    ``handle_fold`` (push handle → REVOLUTE part), ``mech_dropbar`` (spinner → drop
    bar + agitator), ``spinner_vanes6`` (vanes 3→6).

Structure (pattern = ``mixed``): a single grounded root ``spreader`` part carries
the hopper form (Slot A), chassis (Slot B), chute + gate rails + static mechanism
hardware — everything that does NOT move is a visual on it (Rule 1: origin B's
``frame_to_hopper`` FIXED is the anti-pattern we fuse away).  Parallel children:

  * ``wheel_{i}`` × N (CONTINUOUS x)         — 2 drive wheels, +``caster_wheel`` when N=3.
  * ``spinner`` | ``agitator`` (CONTINUOUS)  — the mechanism moving part.
  * ``control_lever`` (REVOLUTE x)           — rate lever on a chassis bracket.
  * ``flow_gate`` (PRISMATIC -y)             — sliding metering gate.
  * ``handle`` (REVOLUTE x, push_folding only) — folding push handle.

One unified coordinate frame (origin A's): throat ≈ z0.36, spinner/gate below it,
axle_z = tire radius (per chassis).  All non-FIXED joints are captured-pin / hub /
slide geometry, so they omit ``MatingContract`` (grandfathered) and are guarded by
element-scoped ``allow_overlap`` mirroring each source record's run_tests.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Literal

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    BoltPattern,
    Box,
    Cylinder,
    Inertial,
    KnobGeometry,
    KnobGrip,
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
    TorusGeometry,
    WheelBore,
    WheelFace,
    WheelGeometry,
    WheelHub,
    WheelRim,
    WheelSpokes,
    mesh_from_geometry,
    rounded_rect_profile,
    tube_from_spline_points,
)

__modular__ = True

HopperForm = Literal["square_taper", "rounded_square", "round_conical"]
Chassis = Literal["push_fixed_handle", "push_folding_handle", "tow_drawbar"]
Mechanism = Literal["broadcast_spinner", "drop_bar"]
PaletteStyle = Literal[
    "black_poly_red_frame",
    "black_poly_green_frame",
    "black_poly_black_frame",
    "grey_poly_yellow_frame",
    "galvanized",
]

HOPPER_FORMS: tuple[HopperForm, ...] = ("square_taper", "rounded_square", "round_conical")
CHASSIS: tuple[Chassis, ...] = ("push_fixed_handle", "push_folding_handle", "tow_drawbar")
MECHANISMS: tuple[Mechanism, ...] = ("broadcast_spinner", "drop_bar")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "black_poly_red_frame",
    "black_poly_green_frame",
    "black_poly_black_frame",
    "grey_poly_yellow_frame",
    "galvanized",
)

VANE_COUNTS: tuple[int, ...] = (3, 4, 6)
VANE_WEIGHTS: tuple[float, ...] = (0.34, 0.33, 0.33)
WHEEL_COUNTS: tuple[int, ...] = (2, 3)
WHEEL_WEIGHTS: tuple[float, ...] = (0.6, 0.4)
DROP_HOLE_COUNTS: tuple[int, ...] = (6, 8, 10)
DROP_HOLE_WEIGHTS: tuple[float, ...] = (0.34, 0.33, 0.33)

# --- Fixed unified layout (origin A frame; meters). Everything except axle_z is
#     invariant so the mechanism / gate / chute stay wired across chassis. ---
THROAT_Z = 0.360
GATE_ORIGIN = (0.0, -0.040, 0.334)
GATE_TRAVEL = 0.130
SPINNER_ORIGIN = (0.0, -0.170, 0.270)
DROP_BAR_ORIGIN = (0.0, -0.040, 0.240)
DROP_BAR_LENGTH = 0.640

PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "black_poly_red_frame": {
        "hopper": (0.030, 0.032, 0.028, 1.0),
        "frame": (0.86, 0.07, 0.03, 1.0),
        "tire": (0.018, 0.018, 0.015, 1.0),
        "rim": (0.88, 0.86, 0.82, 1.0),
        "hub": (0.72, 0.72, 0.68, 1.0),
        "spinner": (0.70, 0.70, 0.66, 1.0),
        "hardware": (0.02, 0.02, 0.018, 1.0),
        "label": (1.0, 0.85, 0.10, 1.0),
    },
    "black_poly_green_frame": {
        "hopper": (0.030, 0.032, 0.028, 1.0),
        "frame": (0.09, 0.44, 0.14, 1.0),
        "tire": (0.018, 0.018, 0.015, 1.0),
        "rim": (0.90, 0.88, 0.84, 1.0),
        "hub": (0.72, 0.72, 0.68, 1.0),
        "spinner": (0.70, 0.70, 0.66, 1.0),
        "hardware": (0.02, 0.02, 0.018, 1.0),
        "label": (1.0, 0.80, 0.05, 1.0),
    },
    "black_poly_black_frame": {
        "hopper": (0.020, 0.020, 0.018, 1.0),
        "frame": (0.05, 0.05, 0.045, 1.0),
        "tire": (0.010, 0.010, 0.008, 1.0),
        "rim": (0.88, 0.86, 0.82, 1.0),
        "hub": (0.70, 0.70, 0.66, 1.0),
        "spinner": (0.14, 0.14, 0.13, 1.0),
        "hardware": (0.02, 0.02, 0.018, 1.0),
        "label": (1.0, 0.34, 0.02, 1.0),
    },
    "grey_poly_yellow_frame": {
        "hopper": (0.42, 0.43, 0.44, 1.0),
        "frame": (0.94, 0.78, 0.05, 1.0),
        "tire": (0.020, 0.020, 0.017, 1.0),
        "rim": (0.30, 0.31, 0.33, 1.0),
        "hub": (0.60, 0.60, 0.57, 1.0),
        "spinner": (0.30, 0.31, 0.33, 1.0),
        "hardware": (0.05, 0.05, 0.045, 1.0),
        "label": (0.05, 0.05, 0.05, 1.0),
    },
    "galvanized": {
        "hopper": (0.66, 0.67, 0.64, 1.0),
        "frame": (0.72, 0.73, 0.70, 1.0),
        "tire": (0.020, 0.020, 0.017, 1.0),
        "rim": (0.80, 0.81, 0.78, 1.0),
        "hub": (0.58, 0.58, 0.55, 1.0),
        "spinner": (0.78, 0.79, 0.76, 1.0),
        "hardware": (0.10, 0.10, 0.09, 1.0),
        "label": (0.10, 0.28, 0.62, 1.0),
    },
}


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class SeedSpreaderConfig:
    hopper_form: HopperForm | None = None
    chassis: Chassis | None = None
    mechanism: Mechanism | None = None
    wheel_count: int | None = None
    vane_count: int | None = None
    drop_hole_count: int | None = None
    palette_style: PaletteStyle = "black_poly_black_frame"
    hopper_width_scale: float = 1.0
    hopper_height_scale: float = 1.0
    wheel_radius_scale: float = 1.0
    gate_travel_scale: float = 1.0
    vane_length_scale: float = 1.0
    name: str = "seed_spreader"


@dataclass(frozen=True)
class ResolvedSeedSpreaderConfig:
    hopper_form: HopperForm
    chassis: Chassis
    mechanism: Mechanism
    wheel_count: int
    vane_count: int
    drop_hole_count: int
    palette_style: PaletteStyle
    hopper_width_scale: float
    hopper_height_scale: float
    wheel_radius_scale: float
    gate_travel_scale: float
    vane_length_scale: float
    # Derived geometry.
    axle_z: float
    wheel_x: float
    tire_radius: float
    lever_pivot: tuple[float, float, float]
    name: str

    @property
    def is_push(self) -> bool:
        return self.chassis in ("push_fixed_handle", "push_folding_handle")


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _pick(value, choices):
    return value if value in choices else choices[0]


def config_from_seed(seed: int) -> SeedSpreaderConfig:
    rng = random.Random(seed)
    return SeedSpreaderConfig(
        hopper_form=rng.choice(HOPPER_FORMS),
        chassis=rng.choice(CHASSIS),
        mechanism=rng.choice(MECHANISMS),
        wheel_count=rng.choices(WHEEL_COUNTS, weights=WHEEL_WEIGHTS, k=1)[0],
        vane_count=rng.choices(VANE_COUNTS, weights=VANE_WEIGHTS, k=1)[0],
        drop_hole_count=rng.choices(DROP_HOLE_COUNTS, weights=DROP_HOLE_WEIGHTS, k=1)[0],
        palette_style=rng.choice(PALETTE_STYLES),
        hopper_width_scale=round(rng.uniform(0.92, 1.10), 4),
        hopper_height_scale=round(rng.uniform(0.92, 1.10), 4),
        wheel_radius_scale=round(rng.uniform(0.90, 1.10), 4),
        gate_travel_scale=round(rng.uniform(0.85, 1.12), 4),
        vane_length_scale=round(rng.uniform(0.90, 1.10), 4),
        name=f"seeded_seed_spreader_{seed}",
    )


def resolve_config(config: SeedSpreaderConfig | None = None) -> ResolvedSeedSpreaderConfig:
    cfg = config or SeedSpreaderConfig()
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)
    hopper_form = _pick(cfg.hopper_form, HOPPER_FORMS)
    chassis = _pick(cfg.chassis, CHASSIS)
    mechanism = _pick(cfg.mechanism, MECHANISMS)

    is_push = chassis in ("push_fixed_handle", "push_folding_handle")

    wheel_count = int(cfg.wheel_count) if cfg.wheel_count is not None else 2
    wheel_count = 3 if wheel_count >= 3 else 2
    # Compatibility gating (spec §9): a front-center caster only makes sense on a
    # push spreader — a tow spreader's front is the hitch.  Force N=2 for tow.
    if not is_push:
        wheel_count = 2

    vane_count = int(cfg.vane_count) if cfg.vane_count is not None else 4
    vane_count = _pick(vane_count, VANE_COUNTS)
    drop_hole_count = int(cfg.drop_hole_count) if cfg.drop_hole_count is not None else 8
    drop_hole_count = _pick(drop_hole_count, DROP_HOLE_COUNTS)

    width_scale = _clamp(cfg.hopper_width_scale, 0.92, 1.10)
    height_scale = _clamp(cfg.hopper_height_scale, 0.92, 1.10)
    wheel_radius_scale = _clamp(cfg.wheel_radius_scale, 0.90, 1.10)
    gate_travel_scale = _clamp(cfg.gate_travel_scale, 0.85, 1.12)
    vane_length_scale = _clamp(cfg.vane_length_scale, 0.90, 1.10)

    # Wheel geometry: tow uses big turf tires (origin B), push small utility tires
    # (origin A).  axle_z = tire radius so the wheel bottom sits on the ground.
    base_tire_r = 0.245 if not is_push else 0.185
    tire_radius = base_tire_r * wheel_radius_scale
    axle_z = tire_radius
    wheel_x = 0.520 if not is_push else 0.435

    # Rate-control lever pivot: on a front control post clear of the hopper for
    # push, on the front drawbar mast quadrant for tow (chassis emits the real
    # bracket there).  x=0.20 sits outboard of the throat hardware and forward of
    # the hopper front wall so the lever + knob never intersect the hopper solid.
    if is_push:
        lever_pivot = (0.220, -0.300, 0.460)
    else:
        lever_pivot = (0.060, -0.420, 0.520)

    return ResolvedSeedSpreaderConfig(
        hopper_form=hopper_form,
        chassis=chassis,
        mechanism=mechanism,
        wheel_count=wheel_count,
        vane_count=vane_count,
        drop_hole_count=drop_hole_count,
        palette_style=palette_style,
        hopper_width_scale=width_scale,
        hopper_height_scale=height_scale,
        wheel_radius_scale=wheel_radius_scale,
        gate_travel_scale=gate_travel_scale,
        vane_length_scale=vane_length_scale,
        axle_z=axle_z,
        wheel_x=wheel_x,
        tire_radius=tire_radius,
        lever_pivot=lever_pivot,
        name=cfg.name or "seed_spreader",
    )


def slot_choices_for_config(
    config: SeedSpreaderConfig | ResolvedSeedSpreaderConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedSeedSpreaderConfig) else resolve_config(config)
    choices: list[tuple[str, str]] = [
        ("hopper_form", r.hopper_form),
        ("chassis", r.chassis),
        ("mechanism", r.mechanism),
        ("wheel_count", f"n{r.wheel_count}"),
    ]
    if r.mechanism == "broadcast_spinner":
        choices.append(("vane_count", f"n{r.vane_count}"))
    else:
        choices.append(("drop_hole_count", f"n{r.drop_hole_count}"))
    return tuple(choices)


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Mesh helpers (Rule 3: keep source primitive families).
# ---------------------------------------------------------------------------
def _add_quad(mesh: MeshGeometry, a: int, b: int, c: int, d: int) -> None:
    mesh.add_face(a, b, c)
    mesh.add_face(a, c, d)


def _loop_vertices(mesh: MeshGeometry, profile: list[tuple[float, float]], z: float) -> list[int]:
    return [mesh.add_vertex(x, y, z) for x, y in profile]


def _zmap(z: float, height_scale: float) -> float:
    """Scale hopper heights about the fixed throat plane."""
    return THROAT_Z + (z - THROAT_Z) * height_scale


def _shell_mesh(sections: list[tuple[float, float, float, float]], wall: float) -> MeshGeometry:
    """Hollow rounded-rect hopper shell (origin A L51-90 / origin B L69-115).

    ``sections`` = list of (z, width, depth, corner_radius) top->throat.
    """
    mesh = MeshGeometry()
    outer_loops: list[list[int]] = []
    inner_loops: list[list[int]] = []
    for z, width, depth, radius in sections:
        outer = rounded_rect_profile(width, depth, radius, corner_segments=7)
        inner = rounded_rect_profile(
            max(width - 2.0 * wall, 0.04),
            max(depth - 2.0 * wall, 0.04),
            max(radius - wall * 0.55, 0.012),
            corner_segments=7,
        )
        inner_z = z - (0.030 if z == sections[0][0] else 0.018)
        outer_loops.append(_loop_vertices(mesh, outer, z))
        inner_loops.append(_loop_vertices(mesh, inner, inner_z))

    count = len(outer_loops[0])
    for i in range(len(sections) - 1):
        for j in range(count):
            n = (j + 1) % count
            _add_quad(mesh, outer_loops[i][j], outer_loops[i][n], outer_loops[i + 1][n], outer_loops[i + 1][j])
            _add_quad(mesh, inner_loops[i][n], inner_loops[i][j], inner_loops[i + 1][j], inner_loops[i + 1][n])
    for j in range(count):
        n = (j + 1) % count
        _add_quad(mesh, outer_loops[0][n], outer_loops[0][j], inner_loops[0][j], inner_loops[0][n])
        _add_quad(mesh, outer_loops[-1][j], outer_loops[-1][n], inner_loops[-1][n], inner_loops[-1][j])
    return mesh


def _hopper_loop_mesh(width: float, depth: float, z: float, radius: float, tube_radius: float, name: str):
    """Rounded-rect tube reinforcing ring (origin A L93-104)."""
    profile = rounded_rect_profile(width, depth, radius, corner_segments=8)
    points = [(x, y, z) for x, y in profile]
    tube = tube_from_spline_points(
        points, radius=tube_radius, samples_per_segment=4, closed_spline=True,
        radial_segments=12, cap_ends=False,
    )
    return mesh_from_geometry(tube, name)


def _tube_mesh(points: list[tuple[float, float, float]], radius: float, name: str, *, samples: int = 6):
    tube = tube_from_spline_points(
        points, radius=radius, samples_per_segment=samples, radial_segments=12, cap_ends=True,
    )
    return mesh_from_geometry(tube, name)


def _conical_hopper_mesh(height_scale: float, width_scale: float) -> MeshGeometry:
    """Round-conical funnel shell (variant hopper_conical L53-84). LatheGeometry
    surface of revolution about +Z; MUST stay Lathe (Rule 3)."""
    outer = [
        (0.380, 0.845), (0.360, 0.720), (0.300, 0.580),
        (0.220, 0.470), (0.150, 0.400), (0.110, THROAT_Z),
    ]
    wall = 0.026
    outer_p = [(r * width_scale, _zmap(z, height_scale)) for r, z in outer]
    inner_p = [(max(r * width_scale - wall, 0.02), _zmap(z, height_scale)) for r, z in outer]
    return LatheGeometry.from_shell_profiles(
        outer_p, inner_p, segments=36, start_cap="flat", end_cap="flat"
    )


# --- Hopper section tables (top -> throat) per ③ form prototype. ---
_SQUARE_TAPER_SECTIONS = [
    (0.840, 0.760, 0.540, 0.070),
    (0.630, 0.720, 0.500, 0.060),
    (0.450, 0.430, 0.300, 0.045),
    (THROAT_Z, 0.230, 0.160, 0.030),
]
_ROUNDED_SQUARE_SECTIONS = [
    (0.845, 0.880, 0.580, 0.100),
    (0.640, 0.840, 0.540, 0.090),
    (0.470, 0.640, 0.400, 0.062),
    (THROAT_Z, 0.320, 0.200, 0.045),
]


def _scaled_sections(sections, width_scale: float, height_scale: float):
    return [
        (_zmap(z, height_scale), w * width_scale, d * width_scale, r * width_scale)
        for (z, w, d, r) in sections
    ]


def _hopper_half_depth_at(r: ResolvedSeedSpreaderConfig, z: float) -> float:
    """Front (–y) face half-depth of the hopper at height ``z`` (host-conformal
    decoration derives from this — Rule 4)."""
    if r.hopper_form == "round_conical":
        prof = [(0.380, 0.845), (0.360, 0.720), (0.300, 0.580),
                (0.220, 0.470), (0.150, 0.400), (0.110, THROAT_Z)]
        pts = [(_zmap(zz, r.hopper_height_scale), rr * r.hopper_width_scale) for rr, zz in prof]
    else:
        table = _SQUARE_TAPER_SECTIONS if r.hopper_form == "square_taper" else _ROUNDED_SQUARE_SECTIONS
        pts = [(_zmap(zz, r.hopper_height_scale), (d * 0.5) * r.hopper_width_scale)
               for (zz, w, d, rr) in table]
    pts.sort()
    for (z0, h0), (z1, h1) in zip(pts, pts[1:]):
        if z0 <= z <= z1:
            t = 0.0 if z1 == z0 else (z - z0) / (z1 - z0)
            return h0 + t * (h1 - h0)
    return pts[0][1] if z < pts[0][0] else pts[-1][1]


def _hopper_half_width_at(r: ResolvedSeedSpreaderConfig, z: float) -> float:
    """Side (+x) face half-width of the realized hopper at height ``z`` (mirror of
    ``_hopper_half_depth_at``; conical=radius*width_scale, square/rounded=w*0.5*
    width_scale).  Used so the tow frame welds to the actual scaled wall at every
    hopper form/scale instead of a fixed x that the conical wall pulls inboard of."""
    if r.hopper_form == "round_conical":
        prof = [(0.380, 0.845), (0.360, 0.720), (0.300, 0.580),
                (0.220, 0.470), (0.150, 0.400), (0.110, THROAT_Z)]
        pts = [(_zmap(zz, r.hopper_height_scale), rr * r.hopper_width_scale) for rr, zz in prof]
    else:
        table = _SQUARE_TAPER_SECTIONS if r.hopper_form == "square_taper" else _ROUNDED_SQUARE_SECTIONS
        pts = [(_zmap(zz, r.hopper_height_scale), (w * 0.5) * r.hopper_width_scale)
               for (zz, w, d, rr) in table]
    pts.sort()
    for (z0, h0), (z1, h1) in zip(pts, pts[1:]):
        if z0 <= z <= z1:
            t = 0.0 if z1 == z0 else (z - z0) / (z1 - z0)
            return h0 + t * (h1 - h0)
    return pts[0][1] if z < pts[0][0] else pts[-1][1]


# ---------------------------------------------------------------------------
# Hopper builders (Slot A). All emit visuals on the root ``spreader`` part.
# ---------------------------------------------------------------------------
def _emit_brand_decal(spreader, r: ResolvedSeedSpreaderConfig, mats) -> None:
    """Raised brand block + label lines on the hopper front wall (Rule 4:
    host-conformal — front_y derives from the realized hopper face)."""
    # Each element straddles the hopper front face at its OWN z (front_y derives
    # from the realized face — Rule 4), embedding into the wall so it never floats.
    block_z = _zmap(0.700, r.hopper_height_scale)
    block_fy = -_hopper_half_depth_at(r, block_z)
    spreader.visual(
        Box((0.145, 0.010, 0.050)),
        origin=Origin(xyz=(0.0, block_fy + 0.003, block_z)),
        material=mats["label"],
        name="brand_block", material_class_id="plastic.opaque_glossy_molded",
    )
    for i in range(3):
        lz = block_z - 0.032 - i * 0.014
        lfy = -_hopper_half_depth_at(r, lz)
        spreader.visual(
            Box((0.095 - i * 0.015, 0.014, 0.006)),
            origin=Origin(xyz=(0.0, lfy + 0.004, lz)),
            material=mats["label"],
            name=f"label_line_{i}", material_class_id="plastic.opaque_glossy_molded",
        )


def _emit_throat_collar(spreader, r: ResolvedSeedSpreaderConfig, mats) -> None:
    """Metering-throat collar walls that bridge hopper -> chute -> frame for every
    ③ form (origin B L244-246), so a swapped hopper is never a floating island.
    The throat plane is fixed (only sections ABOVE it scale), so zc is fixed too —
    keeping the collar welded to the fixed-z gate rails / chute for every scale."""
    zc = THROAT_Z + 0.015
    # Sides span x in [0.055, 0.145] so the collar reaches the narrow round_conical
    # throat (radius ~0.11*width) as well as the wider square throats -> the hopper
    # shell is welded to the fixed-z chute for every form/scale (was a thin wall at
    # x=0.145 that missed the conical throat at narrow width scales -> floating island).
    for i, x in enumerate((-0.10, 0.10)):
        spreader.visual(
            Box((0.090, 0.230, 0.075)),
            origin=Origin(xyz=(x, -0.040, zc)),
            material=mats["hardware"],
            name=f"throat_collar_side_{i}", material_class_id="metal.blackened_gunmetal",
        )
    spreader.visual(
        Box((0.320, 0.016, 0.075)),
        origin=Origin(xyz=(0.0, -0.150, zc)),
        material=mats["hardware"],
        name="throat_collar_front", material_class_id="metal.blackened_gunmetal",
    )
    spreader.visual(
        Box((0.320, 0.016, 0.075)),
        origin=Origin(xyz=(0.0, 0.070, zc)),
        material=mats["hardware"],
        name="throat_collar_rear", material_class_id="metal.blackened_gunmetal",
    )


def _build_hopper_square(spreader, r: ResolvedSeedSpreaderConfig, mats, *, rounded: bool) -> None:
    table = _ROUNDED_SQUARE_SECTIONS if rounded else _SQUARE_TAPER_SECTIONS
    sections = _scaled_sections(table, r.hopper_width_scale, r.hopper_height_scale)
    spreader.visual(
        mesh_from_geometry(_shell_mesh(sections, wall=0.030), "hopper_shell"),
        material=mats["hopper"], name="hopper_shell", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"black_poly_red_frame", "black_poly_green_frame", "black_poly_black_frame", "grey_poly_yellow_frame"} else "metal.steel_galvanized"),
    )
    ws, hs = r.hopper_width_scale, r.hopper_height_scale
    tube = 0.024 if rounded else 0.018
    spreader.visual(
        _hopper_loop_mesh(0.86 * ws if rounded else 0.79 * ws, 0.66 * ws if rounded else 0.57 * ws,
                          _zmap(0.845, hs), 0.09 * ws, tube, "top_rolled_rim"),
        material=mats["hopper"], name="top_rolled_rim", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"black_poly_red_frame", "black_poly_green_frame", "black_poly_black_frame", "grey_poly_yellow_frame"} else "metal.steel_galvanized"),
    )
    spreader.visual(
        _hopper_loop_mesh(0.80 * ws if rounded else 0.73 * ws, 0.60 * ws if rounded else 0.51 * ws,
                          _zmap(0.620, hs), 0.06 * ws, 0.016, "middle_seam_rib"),
        material=mats["hopper"], name="middle_seam_rib", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"black_poly_red_frame", "black_poly_green_frame", "black_poly_black_frame", "grey_poly_yellow_frame"} else "metal.steel_galvanized"),
    )
    spreader.visual(
        _hopper_loop_mesh(0.34 * ws, 0.25 * ws, _zmap(0.410, hs), 0.035 * ws, 0.018, "lower_support_ring"),
        material=mats["hardware"], name="lower_support_ring", material_class_id="metal.blackened_gunmetal",
    )


def _build_hopper_conical(spreader, r: ResolvedSeedSpreaderConfig, mats) -> None:
    spreader.visual(
        mesh_from_geometry(_conical_hopper_mesh(r.hopper_height_scale, r.hopper_width_scale), "hopper_shell"),
        material=mats["hopper"], name="hopper_shell", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"black_poly_red_frame", "black_poly_green_frame", "black_poly_black_frame", "grey_poly_yellow_frame"} else "metal.steel_galvanized"),
    )
    ws, hs = r.hopper_width_scale, r.hopper_height_scale
    spreader.visual(
        mesh_from_geometry(TorusGeometry(0.38 * ws, 0.018, radial_segments=12, tubular_segments=32), "top_rolled_rim"),
        origin=Origin(xyz=(0.0, 0.0, _zmap(0.845, hs))),
        material=mats["hopper"], name="top_rolled_rim", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"black_poly_red_frame", "black_poly_green_frame", "black_poly_black_frame", "grey_poly_yellow_frame"} else "metal.steel_galvanized"),
    )
    spreader.visual(
        mesh_from_geometry(TorusGeometry(0.30 * ws, 0.016, radial_segments=12, tubular_segments=28), "middle_seam_rib"),
        origin=Origin(xyz=(0.0, 0.0, _zmap(0.580, hs))),
        material=mats["hopper"], name="middle_seam_rib", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"black_poly_red_frame", "black_poly_green_frame", "black_poly_black_frame", "grey_poly_yellow_frame"} else "metal.steel_galvanized"),
    )
    spreader.visual(
        mesh_from_geometry(TorusGeometry(0.15 * ws, 0.018, radial_segments=12, tubular_segments=24), "lower_support_ring"),
        origin=Origin(xyz=(0.0, 0.0, _zmap(0.410, hs))),
        material=mats["hardware"], name="lower_support_ring", material_class_id="metal.blackened_gunmetal",
    )


def _build_hopper(spreader, r: ResolvedSeedSpreaderConfig, mats) -> None:
    if r.hopper_form == "round_conical":
        _build_hopper_conical(spreader, r, mats)
    else:
        _build_hopper_square(spreader, r, mats, rounded=(r.hopper_form == "rounded_square"))
    _emit_throat_collar(spreader, r, mats)
    _emit_brand_decal(spreader, r, mats)


# ---------------------------------------------------------------------------
# Chassis builders (Slot B). Emit frame visuals on root; push_folding also emits a
# ``handle`` REVOLUTE child part. Each emits a real lever mount bracket at
# r.lever_pivot.  Returns the (optional) folding handle part name.
# ---------------------------------------------------------------------------
def _emit_axle_and_common_frame(spreader, r: ResolvedSeedSpreaderConfig, mats) -> None:
    az = r.axle_z
    spreader.visual(
        Cylinder(radius=0.016, length=2.0 * r.wheel_x - 0.02),
        origin=Origin(xyz=(0.0, 0.0, az), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["hub"], name="wheel_axle", material_class_id="metal.stainless_matte",
    )
    # Central gearbox drives the spinner from below the throat. Push only: its
    # bulge sits just under the disc; on the taller tow chassis (high axle) it
    # would rise into the spinner disc, so tow drives the spinner off the drawbar.
    if r.is_push:
        # Cap the gearbox height so its top stays below the drop bar rod (z0.23)
        # and spinner disc (z0.263) even at the tallest push axle.
        gz = min(az - 0.015, 0.170)
        spreader.visual(
            Cylinder(radius=0.045, length=0.135),
            origin=Origin(xyz=(0.0, -0.010, gz), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["frame"], name="gearbox_bulge", material_class_id=("metal.paint_coated" if r.palette_style in {"black_poly_red_frame", "black_poly_green_frame", "black_poly_black_frame", "grey_poly_yellow_frame"} else "metal.steel_galvanized"),
        )
        spreader.visual(
            Box((0.100, 0.080, 0.100)),
            origin=Origin(xyz=(0.0, -0.020, gz - 0.035)),
            material=mats["frame"], name="gearbox_case", material_class_id=("metal.paint_coated" if r.palette_style in {"black_poly_red_frame", "black_poly_green_frame", "black_poly_black_frame", "grey_poly_yellow_frame"} else "metal.steel_galvanized"),
        )
    for i, x in enumerate((-0.391, 0.391)):
        spreader.visual(
            Cylinder(radius=0.070, length=0.006),
            origin=Origin(xyz=(x, 0.0, az), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["hub"], name=f"axle_spacer_{i}", material_class_id="metal.stainless_matte",
        )


def _emit_push_frame_tubes(spreader, r: ResolvedSeedSpreaderConfig, mats) -> None:
    az = r.axle_z
    spreader.visual(_tube_mesh([(-0.31, 0.01, az), (-0.285, -0.08, 0.285), (-0.255, -0.18, 0.430), (-0.225, -0.18, 0.520)], 0.014, "frame_side_0"),
                    material=mats["frame"], name="frame_side_0", material_class_id=("metal.paint_coated" if r.palette_style in {"black_poly_red_frame", "black_poly_green_frame", "black_poly_black_frame", "grey_poly_yellow_frame"} else "metal.steel_galvanized"))
    spreader.visual(_tube_mesh([(0.31, 0.01, az), (0.285, -0.08, 0.285), (0.255, -0.18, 0.430), (0.225, -0.18, 0.520)], 0.014, "frame_side_1"),
                    material=mats["frame"], name="frame_side_1", material_class_id=("metal.paint_coated" if r.palette_style in {"black_poly_red_frame", "black_poly_green_frame", "black_poly_black_frame", "grey_poly_yellow_frame"} else "metal.steel_galvanized"))
    spreader.visual(_tube_mesh([(-0.26, 0.055, az), (-0.18, 0.160, 0.360), (-0.10, 0.190, 0.560)], 0.013, "rear_brace_0"),
                    material=mats["frame"], name="rear_brace_0", material_class_id=("metal.paint_coated" if r.palette_style in {"black_poly_red_frame", "black_poly_green_frame", "black_poly_black_frame", "grey_poly_yellow_frame"} else "metal.steel_galvanized"))
    spreader.visual(_tube_mesh([(0.26, 0.055, az), (0.18, 0.160, 0.360), (0.10, 0.190, 0.560)], 0.013, "rear_brace_1"),
                    material=mats["frame"], name="rear_brace_1", material_class_id=("metal.paint_coated" if r.palette_style in {"black_poly_red_frame", "black_poly_green_frame", "black_poly_black_frame", "grey_poly_yellow_frame"} else "metal.steel_galvanized"))


def _emit_lever_bracket(spreader, r: ResolvedSeedSpreaderConfig, mats) -> None:
    """Front control post carrying the rate-lever pivot, bridged to the frame_side
    top so it is never a floating island."""
    lx, ly, lz = r.lever_pivot
    spreader.visual(
        _tube_mesh([(0.225, -0.18, 0.520), (lx + 0.02, ly + 0.05, lz + 0.02), (lx, ly, lz)], 0.012, "lever_post"),
        material=mats["frame"], name="lever_post", material_class_id=("metal.paint_coated" if r.palette_style in {"black_poly_red_frame", "black_poly_green_frame", "black_poly_black_frame", "grey_poly_yellow_frame"} else "metal.steel_galvanized"),
    )
    spreader.visual(
        Box((0.055, 0.055, 0.060)),
        origin=Origin(xyz=(lx, ly, lz - 0.005)),
        material=mats["frame"], name="lever_mount_bracket", material_class_id=("metal.paint_coated" if r.palette_style in {"black_poly_red_frame", "black_poly_green_frame", "black_poly_black_frame", "grey_poly_yellow_frame"} else "metal.steel_galvanized"),
    )
    # Visible control cable routed from the lever post down to the gate throat.
    spreader.visual(
        _tube_mesh([(lx, ly, lz - 0.02), (0.10, -0.10, 0.42), (0.04, -0.03, 0.372)], 0.0035, "control_cable", samples=8),
        material=mats["hub"], name="control_cable", material_class_id="tech.cable_pipe_bundle",
    )


def _build_chassis_push_fixed(model, spreader, r: ResolvedSeedSpreaderConfig, mats) -> str | None:
    _emit_axle_and_common_frame(spreader, r, mats)
    _emit_push_frame_tubes(spreader, r, mats)
    _emit_lever_bracket(spreader, r, mats)
    # Connector stubs bridge the rear_brace ends (+/-0.10, 0.190, 0.560) to the handle
    # base (0, 0.140, 0.560) so the fixed T-handle is structurally tied to the frame
    # independent of hopper scale (mirrors the folding variant's handle_mount_arm).
    for i, x_sign in enumerate((-1.0, 1.0)):
        spreader.visual(_tube_mesh([(x_sign * 0.10, 0.190, 0.560), (0.0, 0.150, 0.560)], 0.016, f"handle_mount_arm_{i}"),
                        material=mats["frame"], name=f"handle_mount_arm_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"black_poly_red_frame", "black_poly_green_frame", "black_poly_black_frame", "grey_poly_yellow_frame"} else "metal.steel_galvanized"))
    # Fixed T-handle group (Rule 1: does not move -> fused visuals on root).
    spreader.visual(_tube_mesh([(0.0, 0.140, 0.560), (0.0, 0.350, 0.820), (0.0, 0.560, 1.085)], 0.019, "handle_stem"),
                    material=mats["frame"], name="handle_stem", material_class_id=("metal.paint_coated" if r.palette_style in {"black_poly_red_frame", "black_poly_green_frame", "black_poly_black_frame", "grey_poly_yellow_frame"} else "metal.steel_galvanized"))
    spreader.visual(Cylinder(radius=0.017, length=0.72), origin=Origin(xyz=(0.0, 0.625, 1.120), rpy=(0.0, math.pi / 2.0, 0.0)),
                    material=mats["frame"], name="handlebar_tube", material_class_id=("metal.paint_coated" if r.palette_style in {"black_poly_red_frame", "black_poly_green_frame", "black_poly_black_frame", "grey_poly_yellow_frame"} else "metal.steel_galvanized"))
    for i, x in enumerate((-0.290, 0.290)):
        spreader.visual(Cylinder(radius=0.031, length=0.240), origin=Origin(xyz=(x, 0.625, 1.120), rpy=(0.0, math.pi / 2.0, 0.0)),
                        material=mats["tire"], name=f"handle_grip_{i}", material_class_id="rubber.smooth_plain")
    spreader.visual(Box((0.170, 0.060, 0.070)), origin=Origin(xyz=(0.0, 0.585, 1.085)),
                    material=mats["frame"], name="handlebar_bracket", material_class_id=("metal.paint_coated" if r.palette_style in {"black_poly_red_frame", "black_poly_green_frame", "black_poly_black_frame", "grey_poly_yellow_frame"} else "metal.steel_galvanized"))
    return None


def _build_chassis_push_folding(model, spreader, r: ResolvedSeedSpreaderConfig, mats) -> str | None:
    _emit_axle_and_common_frame(spreader, r, mats)
    _emit_push_frame_tubes(spreader, r, mats)
    _emit_lever_bracket(spreader, r, mats)
    # Fork mount arms + pivot pin anchor the fold pivot behind the hopper on the
    # welded frame (pivot y=0.22 sits at the hopper rear).
    for i, x_sign in enumerate((-1.0, 1.0)):
        spreader.visual(_tube_mesh([(x_sign * 0.10, 0.190, 0.560), (0.0, 0.220, 0.560)], 0.016, f"handle_mount_arm_{i}"),
                        material=mats["frame"], name=f"handle_mount_arm_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"black_poly_red_frame", "black_poly_green_frame", "black_poly_black_frame", "grey_poly_yellow_frame"} else "metal.steel_galvanized"))
    spreader.visual(Cylinder(radius=0.025, length=0.058), origin=Origin(xyz=(0.0, 0.220, 0.560), rpy=(0.0, math.pi / 2.0, 0.0)),
                    material=mats["hub"], name="handle_pivot_pin", material_class_id="metal.stainless_matte")

    # Folding handle child part (authored in the pivot frame; local origin = pivot).
    handle = model.part("handle")
    handle.visual(_tube_mesh([(0.0, 0.0, 0.0), (0.0, 0.220, 0.260), (0.0, 0.440, 0.525)], 0.019, "handle_stem"),
                  material=mats["frame"], name="handle_stem", material_class_id=("metal.paint_coated" if r.palette_style in {"black_poly_red_frame", "black_poly_green_frame", "black_poly_black_frame", "grey_poly_yellow_frame"} else "metal.steel_galvanized"))
    handle.visual(Cylinder(radius=0.017, length=0.72), origin=Origin(xyz=(0.0, 0.505, 0.560), rpy=(0.0, math.pi / 2.0, 0.0)),
                  material=mats["frame"], name="handlebar_tube", material_class_id=("metal.paint_coated" if r.palette_style in {"black_poly_red_frame", "black_poly_green_frame", "black_poly_black_frame", "grey_poly_yellow_frame"} else "metal.steel_galvanized"))
    for i, x in enumerate((-0.290, 0.290)):
        handle.visual(Cylinder(radius=0.031, length=0.240), origin=Origin(xyz=(x, 0.505, 0.560), rpy=(0.0, math.pi / 2.0, 0.0)),
                      material=mats["tire"], name=f"handle_grip_{i}", material_class_id="rubber.smooth_plain")
    handle.visual(Box((0.170, 0.060, 0.070)), origin=Origin(xyz=(0.0, 0.465, 0.525)),
                  material=mats["frame"], name="handlebar_bracket", material_class_id=("metal.paint_coated" if r.palette_style in {"black_poly_red_frame", "black_poly_green_frame", "black_poly_black_frame", "grey_poly_yellow_frame"} else "metal.steel_galvanized"))
    handle.inertial = Inertial.from_geometry(Box((0.60, 0.50, 0.60)), mass=2.2, origin=Origin(xyz=(0.0, 0.30, 0.36)))
    model.articulation(
        "spreader_to_handle", ArticulationType.REVOLUTE, parent=spreader, child=handle,
        origin=Origin(xyz=(0.0, 0.220, 0.560)), axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=8.0, velocity=1.5, lower=0.0, upper=2.2),
    )
    return "handle"


def _build_chassis_tow(model, spreader, r: ResolvedSeedSpreaderConfig, mats) -> str | None:
    _emit_axle_and_common_frame(spreader, r, mats)
    az = r.axle_z
    # Red tubular side rails from axle up to the hopper lower body. Bases sit on the
    # front_cross_tube (y=0.02, z=az, spans x+/-0.31) which is rigidly clamped to the
    # wheel_axle, so the axle group stays connected to the frame at all wheel/axle scales
    # (was starting at y=0.05 -> detached at corner scales).
    spreader.visual(_tube_mesh([(-0.30, 0.02, az), (-0.30, -0.06, 0.34), (-0.24, -0.14, 0.520)], 0.020, "frame_side_0"),
                    material=mats["frame"], name="frame_side_0", material_class_id=("metal.paint_coated" if r.palette_style in {"black_poly_red_frame", "black_poly_green_frame", "black_poly_black_frame", "grey_poly_yellow_frame"} else "metal.steel_galvanized"))
    spreader.visual(_tube_mesh([(0.30, 0.02, az), (0.30, -0.06, 0.34), (0.24, -0.14, 0.520)], 0.020, "frame_side_1"),
                    material=mats["frame"], name="frame_side_1", material_class_id=("metal.paint_coated" if r.palette_style in {"black_poly_red_frame", "black_poly_green_frame", "black_poly_black_frame", "grey_poly_yellow_frame"} else "metal.steel_galvanized"))
    spreader.visual(_tube_mesh([(-0.30, 0.16, az), (-0.12, 0.20, 0.400), (-0.06, 0.20, 0.540)], 0.018, "rear_brace_0"),
                    material=mats["frame"], name="rear_brace_0", material_class_id=("metal.paint_coated" if r.palette_style in {"black_poly_red_frame", "black_poly_green_frame", "black_poly_black_frame", "grey_poly_yellow_frame"} else "metal.steel_galvanized"))
    spreader.visual(_tube_mesh([(0.30, 0.16, az), (0.12, 0.20, 0.400), (0.06, 0.20, 0.540)], 0.018, "rear_brace_1"),
                    material=mats["frame"], name="rear_brace_1", material_class_id=("metal.paint_coated" if r.palette_style in {"black_poly_red_frame", "black_poly_green_frame", "black_poly_black_frame", "grey_poly_yellow_frame"} else "metal.steel_galvanized"))
    # Hopper cradle: weld each frame_side TOP to the realized hopper SIDE wall
    # (y=0, widest x) so the frame stays embedded in the shell at every hopper
    # form/scale. The conical (circular) wall pulls inboard of the fixed frame top
    # at narrow width scales, detaching the whole frame+axle assembly from the
    # hopper (corner-seed disconnected island); deriving the endpoint x from
    # _hopper_half_width_at guarantees ~tube-radius embedding for every form.
    z_top = 0.520
    hw = _hopper_half_width_at(r, z_top)
    for i, x_sign in enumerate((-1.0, 1.0)):
        spreader.visual(
            _tube_mesh([(x_sign * 0.24, -0.14, z_top), (x_sign * hw, 0.0, z_top)], 0.018, f"hopper_cradle_{i}"),
            material=mats["frame"], name=f"hopper_cradle_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"black_poly_red_frame", "black_poly_green_frame", "black_poly_black_frame", "grey_poly_yellow_frame"} else "metal.steel_galvanized"),
        )
    # Front cross tube + drawbar tongue + hitch clevis (origin B L181-228).
    spreader.visual(Cylinder(radius=0.020, length=0.62), origin=Origin(xyz=(0.0, 0.02, az), rpy=(0.0, math.pi / 2.0, 0.0)),
                    material=mats["frame"], name="front_cross_tube", material_class_id=("metal.paint_coated" if r.palette_style in {"black_poly_red_frame", "black_poly_green_frame", "black_poly_black_frame", "grey_poly_yellow_frame"} else "metal.steel_galvanized"))
    # Drawbar tongue dips below the spinner shaft / drop bar (z~0.15 at the
    # centerline crossing) so it never intersects the mechanism.
    spreader.visual(_tube_mesh([(0.0, -0.58, 0.120), (0.0, -0.34, 0.140), (0.0, -0.10, 0.160), (0.0, 0.0, 0.200)], 0.022, "drawbar_tongue"),
                    material=mats["frame"], name="drawbar_tongue", material_class_id=("metal.paint_coated" if r.palette_style in {"black_poly_red_frame", "black_poly_green_frame", "black_poly_black_frame", "grey_poly_yellow_frame"} else "metal.steel_galvanized"))
    # Hitch clevis at the drawbar tongue front end (z0.12).
    spreader.visual(Box((0.16, 0.055, 0.012)), origin=Origin(xyz=(0.0, -0.58, 0.120)),
                    material=mats["frame"], name="hitch_flat_bar", material_class_id=("metal.paint_coated" if r.palette_style in {"black_poly_red_frame", "black_poly_green_frame", "black_poly_black_frame", "grey_poly_yellow_frame"} else "metal.steel_galvanized"))
    for i, x in enumerate((-0.035, 0.035)):
        spreader.visual(Box((0.028, 0.16, 0.022)), origin=Origin(xyz=(x, -0.62, 0.120)),
                        material=mats["frame"], name=f"hitch_clevis_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"black_poly_red_frame", "black_poly_green_frame", "black_poly_black_frame", "grey_poly_yellow_frame"} else "metal.steel_galvanized"))
        spreader.visual(Cylinder(radius=0.012, length=0.036), origin=Origin(xyz=(x, -0.66, 0.120), rpy=(0.0, math.pi / 2.0, 0.0)),
                        material=mats["hardware"], name=f"clevis_hole_boss_{i}", material_class_id="metal.blackened_gunmetal")
    # Front mast + lever quadrant (carries the flow lever pivot).
    spreader.visual(_tube_mesh([(0.0, -0.42, 0.22), (0.0, -0.42, 0.40), (0.0, -0.42, 0.56)], 0.022, "front_mast"),
                    material=mats["frame"], name="front_mast", material_class_id=("metal.paint_coated" if r.palette_style in {"black_poly_red_frame", "black_poly_green_frame", "black_poly_black_frame", "grey_poly_yellow_frame"} else "metal.steel_galvanized"))
    spreader.visual(Box((0.16, 0.030, 0.24)), origin=Origin(xyz=(0.0, -0.420, 0.520)),
                    material=mats["frame"], name="lever_quadrant", material_class_id=("metal.paint_coated" if r.palette_style in {"black_poly_red_frame", "black_poly_green_frame", "black_poly_black_frame", "grey_poly_yellow_frame"} else "metal.steel_galvanized"))
    spreader.visual(_tube_mesh([(0.06, -0.42, 0.47), (0.05, -0.25, 0.42), (0.03, -0.05, 0.372)], 0.0035, "control_cable", samples=8),
                    material=mats["hub"], name="control_cable", material_class_id="tech.cable_pipe_bundle")
    return None


_CHASSIS_BUILDERS = {
    "push_fixed_handle": _build_chassis_push_fixed,
    "push_folding_handle": _build_chassis_push_folding,
    "tow_drawbar": _build_chassis_tow,
}


# ---------------------------------------------------------------------------
# Mechanism builders (Slot C). Each emits its chute + gate rails on root, and a
# CONTINUOUS moving child part. Returns (mech_part_name, mech_joint_name).
# ---------------------------------------------------------------------------
def _chute_spinner_mesh() -> MeshGeometry:
    """Sloped chute from gate to the broadcast spinner (origin A L118-141)."""
    mesh = MeshGeometry()
    hi, ho = 0.13, 0.18
    y_in, z_in = -0.055, 0.342
    y_out, z_out = -0.185, 0.303
    wall = 0.055
    p = {
        "bi_l": mesh.add_vertex(-hi, y_in, z_in), "bi_r": mesh.add_vertex(hi, y_in, z_in),
        "bo_l": mesh.add_vertex(-ho, y_out, z_out), "bo_r": mesh.add_vertex(ho, y_out, z_out),
        "li_t": mesh.add_vertex(-hi, y_in, z_in + wall), "lo_t": mesh.add_vertex(-ho, y_out, z_out + wall * 0.72),
        "ri_t": mesh.add_vertex(hi, y_in, z_in + wall), "ro_t": mesh.add_vertex(ho, y_out, z_out + wall * 0.72),
    }
    _add_quad(mesh, p["bi_l"], p["bi_r"], p["bo_r"], p["bo_l"])
    _add_quad(mesh, p["li_t"], p["bi_l"], p["bo_l"], p["lo_t"])
    _add_quad(mesh, p["bi_r"], p["ri_t"], p["ro_t"], p["bo_r"])
    return mesh


def _chute_dropbar_mesh() -> MeshGeometry:
    """Wide distribution tray from gate to the drop bar (variant mech_dropbar L112-133)."""
    mesh = MeshGeometry()
    hi, ho = 0.14, 0.28
    y_in, z_in = -0.040, 0.338
    y_out, z_out = -0.040, 0.290
    wall = 0.035
    p = {
        "bi_l": mesh.add_vertex(-hi, y_in, z_in), "bi_r": mesh.add_vertex(hi, y_in, z_in),
        "bo_l": mesh.add_vertex(-ho, y_out, z_out), "bo_r": mesh.add_vertex(ho, y_out, z_out),
        "li_t": mesh.add_vertex(-hi, y_in, z_in + wall), "lo_t": mesh.add_vertex(-ho, y_out, z_out + wall * 0.72),
        "ri_t": mesh.add_vertex(hi, y_in, z_in + wall), "ro_t": mesh.add_vertex(ho, y_out, z_out + wall * 0.72),
    }
    _add_quad(mesh, p["bi_l"], p["bi_r"], p["bo_r"], p["bo_l"])
    _add_quad(mesh, p["li_t"], p["bi_l"], p["bo_l"], p["lo_t"])
    _add_quad(mesh, p["bi_r"], p["ri_t"], p["ro_t"], p["bo_r"])
    return mesh


def _emit_gate_rails(spreader, r: ResolvedSeedSpreaderConfig, mats) -> None:
    for i, x in enumerate((-0.165, 0.165)):
        spreader.visual(Box((0.014, 0.270, 0.016)), origin=Origin(xyz=(x, -0.065, 0.345)),
                        material=mats["hardware"], name=f"flow_gate_side_rail_{i}", material_class_id="metal.blackened_gunmetal")
    spreader.visual(Box((0.300, 0.014, 0.018)), origin=Origin(xyz=(0.0, 0.040, 0.345)),
                    material=mats["hardware"], name="flow_gate_rear_stop", material_class_id="metal.blackened_gunmetal")


def _build_mechanism_spinner(model, spreader, r: ResolvedSeedSpreaderConfig, mats) -> tuple[str, str]:
    spreader.visual(mesh_from_geometry(_chute_spinner_mesh(), "chute_tray"),
                    material=mats["hardware"], name="chute_tray", material_class_id="metal.blackened_gunmetal")
    _emit_gate_rails(spreader, r, mats)
    # Spinner bearing column: a vertical housing that bridges the axle/gearbox (or
    # tow drawbar) up to the bearing ring just below the disc (stays below z0.263 so
    # it never touches the disc), keeping the ring supported for every chassis/axle.
    spreader.visual(Box((0.030, 0.180, 0.155)), origin=Origin(xyz=(0.0, -0.100, 0.1775)),
                    material=mats["hardware"], name="spinner_bearing_arm", material_class_id="metal.blackened_gunmetal")
    spreader.visual(mesh_from_geometry(TorusGeometry(0.015, 0.004, radial_segments=16, tubular_segments=12), "spinner_bearing_ring"),
                    origin=Origin(xyz=SPINNER_ORIGIN[:2] + (0.245,)), material=mats["hub"], name="spinner_bearing_ring", material_class_id="metal.stainless_matte")

    spinner = model.part("spinner")
    disc_r = 0.150
    spinner.visual(Cylinder(radius=disc_r, length=0.014), origin=Origin(xyz=(0.0, 0.0, 0.0)),
                   material=mats["spinner"], name="spinner_disc", material_class_id="metal.stainless_matte")
    spinner.visual(Cylinder(radius=0.011, length=0.075), origin=Origin(xyz=(0.0, 0.0, -0.018)),
                   material=mats["hub"], name="spinner_shaft", material_class_id="metal.stainless_matte")
    spinner.visual(Cylinder(radius=0.045, length=0.024), origin=Origin(xyz=(0.0, 0.0, 0.012)),
                   material=mats["hub"], name="spinner_hub", material_class_id="metal.stainless_matte")
    vane_r = 0.100
    vane_len = 0.085 * r.vane_length_scale
    for i in range(r.vane_count):
        angle = i * 2.0 * math.pi / r.vane_count
        spinner.visual(
            Box((vane_len, 0.012, 0.006)),
            origin=Origin(xyz=(math.cos(angle) * vane_r, math.sin(angle) * vane_r, 0.008),
                          rpy=(0.0, 0.0, angle + math.radians(12))),
            material=mats["spinner"], name=f"low_radial_spreader_vane_{i}", material_class_id="metal.stainless_matte",
        )
    spinner.inertial = Inertial.from_geometry(Cylinder(radius=disc_r, length=0.04), mass=1.1, origin=Origin())
    model.articulation(
        "spreader_to_spinner", ArticulationType.CONTINUOUS, parent=spreader, child=spinner,
        origin=Origin(xyz=SPINNER_ORIGIN), axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=6.0, velocity=20.0),
    )
    return "spinner", "spreader_to_spinner"


def _build_mechanism_dropbar(model, spreader, r: ResolvedSeedSpreaderConfig, mats) -> tuple[str, str]:
    spreader.visual(mesh_from_geometry(_chute_dropbar_mesh(), "chute_tray"),
                    material=mats["hardware"], name="chute_tray", material_class_id="metal.blackened_gunmetal")
    _emit_gate_rails(spreader, r, mats)
    bx, by, bz = DROP_BAR_ORIGIN
    spreader.visual(Box((DROP_BAR_LENGTH, 0.058, 0.058)), origin=Origin(xyz=(bx, by, bz)),
                    material=mats["frame"], name="drop_bar_body", material_class_id=("metal.paint_coated" if r.palette_style in {"black_poly_red_frame", "black_poly_green_frame", "black_poly_black_frame", "grey_poly_yellow_frame"} else "metal.steel_galvanized"))
    for i, x in enumerate((-0.326, 0.326)):
        spreader.visual(Box((0.012, 0.062, 0.062)), origin=Origin(xyz=(x, by, bz)),
                        material=mats["hub"], name=f"drop_bar_endcap_{i}", material_class_id="metal.stainless_matte")
    for i, x in enumerate((-0.20, 0.20)):
        spreader.visual(Box((0.018, 0.018, max(0.030, bz - r.axle_z))),
                        origin=Origin(xyz=(x, by, (bz + r.axle_z) * 0.5)),
                        material=mats["frame"], name=f"drop_bar_bracket_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"black_poly_red_frame", "black_poly_green_frame", "black_poly_black_frame", "grey_poly_yellow_frame"} else "metal.steel_galvanized"))
    span = 0.52
    start = -span / 2.0
    step = span / (r.drop_hole_count - 1)
    for i in range(r.drop_hole_count):
        spreader.visual(Cylinder(radius=0.013, length=0.006), origin=Origin(xyz=(start + i * step, by, bz - 0.029)),
                        material=mats["hardware"], name=f"drop_hole_{i}", material_class_id="metal.blackened_gunmetal")

    agitator = model.part("agitator")
    agitator.visual(Cylinder(radius=0.010, length=0.52), origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
                    material=mats["hub"], name="agitator_rod", material_class_id="metal.stainless_matte")
    for i in range(6):
        x_p = -0.22 + i * 0.088
        z_off = 0.016 if i % 2 == 0 else -0.016
        agitator.visual(Box((0.008, 0.024, 0.016)), origin=Origin(xyz=(x_p, 0.0, z_off)),
                        material=mats["hub"], name=f"agitator_paddle_{i}", material_class_id="metal.stainless_matte")
    for i, x_j in enumerate((-0.265, 0.265)):
        agitator.visual(Cylinder(radius=0.016, length=0.012), origin=Origin(xyz=(x_j, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
                        material=mats["hardware"], name=f"agitator_journal_{i}", material_class_id="metal.blackened_gunmetal")
    agitator.inertial = Inertial.from_geometry(Cylinder(radius=0.03, length=0.52), mass=0.6, origin=Origin(rpy=(0.0, math.pi / 2.0, 0.0)))
    model.articulation(
        "spreader_to_agitator", ArticulationType.CONTINUOUS, parent=spreader, child=agitator,
        origin=Origin(xyz=DROP_BAR_ORIGIN), axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=4.0, velocity=15.0),
    )
    return "agitator", "spreader_to_agitator"


_MECHANISM_BUILDERS = {
    "broadcast_spinner": _build_mechanism_spinner,
    "drop_bar": _build_mechanism_dropbar,
}


# ---------------------------------------------------------------------------
# Common child parts: lever, gate, wheels.
# ---------------------------------------------------------------------------
def _build_lever(model, spreader, r: ResolvedSeedSpreaderConfig, mats) -> None:
    lever = model.part("control_lever")
    lever.visual(Cylinder(radius=0.007, length=0.150), origin=Origin(xyz=(0.0, 0.0, -0.075)),
                 material=mats["hub"], name="lever_arm", material_class_id="metal.stainless_matte")
    lever.visual(
        mesh_from_geometry(KnobGeometry(0.048, 0.048, body_style="cylindrical",
                                        grip=KnobGrip(style="fluted", count=16, depth=0.0022)), "lever_knob"),
        origin=Origin(xyz=(0.0, 0.0, -0.160), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["tire"], name="lever_knob", material_class_id="rubber.directional_grooved",
    )
    lever.inertial = Inertial.from_geometry(Box((0.05, 0.05, 0.18)), mass=0.15, origin=Origin(xyz=(0.0, 0.0, -0.09)))
    model.articulation(
        "spreader_to_lever", ArticulationType.REVOLUTE, parent=spreader, child=lever,
        origin=Origin(xyz=r.lever_pivot), axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=4.0, velocity=1.5, lower=0.0, upper=0.65),
    )


def _build_gate(model, spreader, r: ResolvedSeedSpreaderConfig, mats) -> None:
    gate = model.part("flow_gate")
    gate.visual(Box((0.285, 0.180, 0.008)), origin=Origin(xyz=(0.0, 0.0, 0.0)),
                material=mats["hub"], name="slide_plate", material_class_id="metal.stainless_matte")
    gate.inertial = Inertial.from_geometry(Box((0.285, 0.180, 0.02)), mass=0.4, origin=Origin())
    model.articulation(
        "lever_to_gate", ArticulationType.PRISMATIC, parent=spreader, child=gate,
        origin=Origin(xyz=GATE_ORIGIN), axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=12.0, velocity=0.18, lower=0.0, upper=GATE_TRAVEL * r.gate_travel_scale),
    )


def _drive_wheel_meshes(r: ResolvedSeedSpreaderConfig):
    tr = r.tire_radius
    if r.is_push:
        tire = TireGeometry(
            tr, 0.082, inner_radius=tr * 0.69,
            carcass=TireCarcass(belt_width_ratio=0.68, sidewall_bulge=0.055),
            tread=TireTread(style="block", depth=0.010, count=22, land_ratio=0.52),
            grooves=(TireGroove(center_offset=0.0, width=0.008, depth=0.004),),
            sidewall=TireSidewall(style="square", bulge=0.035),
            shoulder=TireShoulder(width=0.010, radius=0.004),
        )
        rim = WheelGeometry(
            tr * 0.69, 0.060,
            rim=WheelRim(inner_radius=tr * 0.43, flange_height=0.010, flange_thickness=0.004, bead_seat_depth=0.004),
            hub=WheelHub(radius=0.034, width=0.038, cap_style="domed",
                         bolt_pattern=BoltPattern(count=5, circle_diameter=0.052, hole_diameter=0.006)),
            face=WheelFace(dish_depth=0.010, front_inset=0.004, rear_inset=0.003),
            spokes=WheelSpokes(style="split_y", count=5, thickness=0.004, window_radius=0.018),
            bore=WheelBore(style="round", diameter=0.040),
        )
    else:
        tire = TireGeometry(
            tr, 0.175, inner_radius=tr * 0.59,
            carcass=TireCarcass(belt_width_ratio=0.72, sidewall_bulge=0.08),
            tread=TireTread(style="block", depth=0.014, count=22, land_ratio=0.52),
            sidewall=TireSidewall(style="square", bulge=0.035),
            shoulder=TireShoulder(width=0.014, radius=0.004),
        )
        rim = WheelGeometry(
            tr * 0.59, 0.105,
            rim=WheelRim(inner_radius=tr * 0.32, flange_height=0.012, flange_thickness=0.006, bead_seat_depth=0.004),
            hub=WheelHub(radius=0.040, width=0.075, cap_style="domed",
                         bolt_pattern=BoltPattern(count=5, circle_diameter=0.060, hole_diameter=0.006)),
            face=WheelFace(dish_depth=0.018, front_inset=0.010, rear_inset=0.004),
            spokes=WheelSpokes(style="split_y", count=5, thickness=0.006, window_radius=0.018),
            bore=WheelBore(style="round", diameter=0.044),
        )
    return mesh_from_geometry(tire, "drive_tire"), mesh_from_geometry(rim, "drive_rim")


def _build_wheels(model, spreader, r: ResolvedSeedSpreaderConfig, mats) -> None:
    tire_mesh, rim_mesh = _drive_wheel_meshes(r)
    for i, x in enumerate((-r.wheel_x, r.wheel_x)):
        wheel = model.part(f"wheel_{i}")
        wheel.visual(tire_mesh, material=mats["tire"], name="tire", material_class_id="rubber.directional_grooved")
        wheel.visual(rim_mesh, material=mats["rim"], name="rim", material_class_id=("metal.paint_coated" if r.palette_style in {"black_poly_red_frame", "black_poly_green_frame", "black_poly_black_frame", "grey_poly_yellow_frame"} else "metal.steel_galvanized"))
        # Sleeve radius > rim bore radius so it touches the rim hub (stays connected).
        wheel.visual(Cylinder(radius=0.024, length=0.066), origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
                     material=mats["hardware"], name="bearing_sleeve", material_class_id="metal.blackened_gunmetal")
        wheel.inertial = Inertial.from_geometry(Cylinder(radius=r.tire_radius, length=0.10), mass=3.0,
                                                origin=Origin(rpy=(0.0, math.pi / 2.0, 0.0)))
        model.articulation(
            f"spreader_to_wheel_{i}", ArticulationType.CONTINUOUS, parent=spreader, child=wheel,
            origin=Origin(xyz=(x, 0.0, r.axle_z)), axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=20.0, velocity=12.0),
        )

    if r.wheel_count < 3:
        return
    # Front-center caster (push only; wheel_count == 3). Origin frame_caster L326-504.
    # Fork legs straddle the thin caster tire in X (tire half-width 0.016 << 0.045).
    caster_r = 0.075
    cz = caster_r
    cy = -0.30
    mount_z = cz + 0.11
    spreader.visual(_tube_mesh([(0.0, -0.05, r.axle_z), (0.0, -0.20, mount_z), (0.0, cy, mount_z)], 0.013, "caster_front_brace"),
                    material=mats["frame"], name="caster_front_brace", material_class_id=("metal.paint_coated" if r.palette_style in {"black_poly_red_frame", "black_poly_green_frame", "black_poly_black_frame", "grey_poly_yellow_frame"} else "metal.steel_galvanized"))
    spreader.visual(Box((0.100, 0.050, 0.020)), origin=Origin(xyz=(0.0, cy, mount_z)),
                    material=mats["frame"], name="caster_mount_plate", material_class_id=("metal.paint_coated" if r.palette_style in {"black_poly_red_frame", "black_poly_green_frame", "black_poly_black_frame", "grey_poly_yellow_frame"} else "metal.steel_galvanized"))
    for i, xl in enumerate((-0.045, 0.045)):
        spreader.visual(_tube_mesh([(xl, cy, mount_z - 0.010), (xl, cy, cz)], 0.009, f"caster_fork_leg_{i}"),
                        material=mats["frame"], name=f"caster_fork_leg_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"black_poly_red_frame", "black_poly_green_frame", "black_poly_black_frame", "grey_poly_yellow_frame"} else "metal.steel_galvanized"))
    spreader.visual(Cylinder(radius=0.005, length=0.100), origin=Origin(xyz=(0.0, cy, cz), rpy=(0.0, math.pi / 2.0, 0.0)),
                    material=mats["hub"], name="caster_axle", material_class_id="metal.stainless_matte")

    caster = model.part("caster_wheel")
    caster.visual(mesh_from_geometry(TireGeometry(
        caster_r, 0.032, inner_radius=0.050,
        carcass=TireCarcass(belt_width_ratio=0.60, sidewall_bulge=0.030),
        tread=TireTread(style="block", depth=0.005, count=14, land_ratio=0.50),
        sidewall=TireSidewall(style="square", bulge=0.020),
        shoulder=TireShoulder(width=0.004, radius=0.003),
    ), "caster_tire"), material=mats["tire"], name="caster_tire", material_class_id="rubber.directional_grooved")
    caster.visual(mesh_from_geometry(WheelGeometry(
        0.050, 0.025,
        rim=WheelRim(inner_radius=0.032, flange_height=0.005, flange_thickness=0.003, bead_seat_depth=0.003),
        hub=WheelHub(radius=0.014, width=0.018, cap_style="flat",
                     bolt_pattern=BoltPattern(count=4, circle_diameter=0.022, hole_diameter=0.004)),
        face=WheelFace(dish_depth=0.004, front_inset=0.002, rear_inset=0.002),
        spokes=WheelSpokes(style="split_y", count=4, thickness=0.003, window_radius=0.009),
        bore=WheelBore(style="round", diameter=0.012),
    ), "caster_rim"), material=mats["rim"], name="caster_rim", material_class_id=("metal.paint_coated" if r.palette_style in {"black_poly_red_frame", "black_poly_green_frame", "black_poly_black_frame", "grey_poly_yellow_frame"} else "metal.steel_galvanized"))
    caster.visual(Cylinder(radius=0.007, length=0.028), origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
                  material=mats["hardware"], name="caster_bearing", material_class_id="metal.blackened_gunmetal")
    caster.inertial = Inertial.from_geometry(Cylinder(radius=caster_r, length=0.05), mass=0.6, origin=Origin(rpy=(0.0, math.pi / 2.0, 0.0)))
    model.articulation(
        "spreader_to_caster", ArticulationType.CONTINUOUS, parent=spreader, child=caster,
        origin=Origin(xyz=(0.0, cy, cz)), axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=8.0, velocity=10.0),
    )


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def build_seed_spreader(
    config: SeedSpreaderConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={"category": "Agricultural", "small_class": "Seed spreader"},
    )
    mats = {
        key: model.material(f"spreader_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in PALETTES[r.palette_style].items()
    }

    spreader = model.part("spreader")
    spreader.inertial = Inertial.from_geometry(
        Box((0.9, 0.9, 0.9)), mass=12.0, origin=Origin(xyz=(0.0, 0.0, 0.45))
    )

    _build_hopper(spreader, r, mats)
    _CHASSIS_BUILDERS[r.chassis](model, spreader, r, mats)
    _MECHANISM_BUILDERS[r.mechanism](model, spreader, r, mats)
    _build_lever(model, spreader, r, mats)
    _build_gate(model, spreader, r, mats)
    _build_wheels(model, spreader, r, mats)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_seed_spreader(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_seed_spreader(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def run_seed_spreader_tests(
    object_model: ArticulatedObject,
    config: SeedSpreaderConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    spreader = object_model.get_part("spreader")

    # ---- Captured-pin / slide allowances (element-scoped, source-backed). ----
    for i in range(2):
        wheel = object_model.get_part(f"wheel_{i}")
        ctx.allow_overlap(wheel, spreader, elem_a="bearing_sleeve", elem_b="wheel_axle",
                          reason="Wheel bearing sleeve is captured around the through axle.")
        ctx.allow_overlap(wheel, spreader, elem_a="rim", elem_b="wheel_axle",
                          reason="Through axle passes into the wheel rim hub bore (captured).")
    if r.wheel_count >= 3:
        caster = object_model.get_part("caster_wheel")
        ctx.allow_overlap(caster, spreader, elem_a="caster_bearing", elem_b="caster_axle",
                          reason="Caster bearing sleeve is captured around the caster axle.")

    if r.mechanism == "broadcast_spinner":
        spinner = object_model.get_part("spinner")
        ctx.allow_overlap(spinner, spreader, elem_a="spinner_shaft", elem_b="spinner_bearing_ring",
                          reason="Spinner drive shaft is captured by the stationary bearing ring.")
        ctx.allow_overlap(spinner, spreader, elem_a="spinner_shaft", elem_b="spinner_bearing_arm",
                          reason="Spinner drive shaft passes through the bearing arm below the disc.")
    else:
        agitator = object_model.get_part("agitator")
        ctx.allow_overlap(agitator, spreader, elem_a="agitator_rod", elem_b="drop_bar_body",
                          reason="Agitator rod runs through the drop bar body as a captured shaft.")
        for i in range(2):
            ctx.allow_overlap(agitator, spreader, elem_a=f"agitator_journal_{i}", elem_b="drop_bar_body",
                              reason="Agitator journal bearing nests inside the drop bar end region.")
        for i in range(6):
            ctx.allow_overlap(agitator, spreader, elem_a=f"agitator_paddle_{i}", elem_b="drop_bar_body",
                              reason="Agitator paddle is captured inside the drop bar body.")
        for i in range(2):
            ctx.allow_overlap(agitator, spreader, elem_a="agitator_rod", elem_b=f"drop_bar_bracket_{i}",
                              reason="Agitator rod runs through the drop bar the mounting brackets are welded to.")

    gate = object_model.get_part("flow_gate")
    ctx.allow_overlap(gate, spreader, elem_a="slide_plate", elem_b="chute_tray",
                      reason="Sliding flow gate is captured in the chute slot.")

    # Rate lever pivot captured in its mount bracket + cable tied to the lever.
    lever = object_model.get_part("control_lever")
    lever_bracket = "lever_quadrant" if not r.is_push else "lever_mount_bracket"
    ctx.allow_overlap(lever, spreader, elem_a="lever_arm", elem_b=lever_bracket,
                      reason="Rate-lever pivot pin is captured in the control mount bracket.")
    ctx.allow_overlap(lever, spreader, elem_a="lever_arm", elem_b="control_cable",
                      reason="Control cable is anchored to the lever arm.")
    if r.is_push:
        ctx.allow_overlap(lever, spreader, elem_a="lever_arm", elem_b="lever_post",
                          reason="Rate-lever pivot is captured on the front control post.")

    if r.chassis == "push_folding_handle":
        handle = object_model.get_part("handle")
        ctx.allow_overlap(handle, spreader, elem_a="handle_stem", elem_b="handle_pivot_pin",
                          reason="Handle stem base is captured around the fold pivot pin.")
        ctx.allow_overlap(handle, spreader, elem_a="handle_stem", elem_b="hopper_shell",
                          reason="Fold pivot is bolted to the hopper rear; stem-base embedding is intentional.")
        for rib in ("middle_seam_rib", "top_rolled_rim"):
            ctx.allow_overlap(handle, spreader, elem_a="handle_stem", elem_b=rib,
                              reason="Folding handle stem passes the hopper rear reinforcing ring.")
        for i in range(2):
            ctx.allow_overlap(handle, spreader, elem_a="handle_stem", elem_b=f"handle_mount_arm_{i}",
                              reason="Handle stem base nests through the fork mount arms at the fold pivot.")
        for i in range(3):
            ctx.allow_overlap(handle, spreader, elem_a="handle_stem", elem_b=f"label_line_{i}",
                              reason="At full fold the handle stem rests on the hopper face over the brand decals.")

    # ---- Baseline stack. ----
    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)
    ctx.fail_if_joint_mating_has_gap()

    # ---- Identity / structure. ----
    part_names = {p.name for p in object_model.parts}
    ctx.check("spreader root present", "spreader" in part_names, details=str(sorted(part_names)))
    ctx.check(
        "classified as seed spreader",
        object_model.meta.get("category") == "Agricultural"
        and object_model.meta.get("small_class") == "Seed spreader",
        details=f"meta={object_model.meta}",
    )
    ctx.check(
        "wheel_count drive wheels present",
        all(f"wheel_{i}" in part_names for i in range(2)),
        details=str(sorted(part_names)),
    )
    ctx.check(
        "caster present iff wheel_count==3",
        ("caster_wheel" in part_names) == (r.wheel_count == 3),
        details=f"wheel_count={r.wheel_count} parts={sorted(part_names)}",
    )
    # Caster only on push chassis (compatibility gating).
    ctx.check(
        "caster only on push chassis",
        r.wheel_count == 2 or r.is_push,
        details=f"chassis={r.chassis} wheel_count={r.wheel_count}",
    )

    # ---- Mechanism topology + multiplicity. ----
    if r.mechanism == "broadcast_spinner":
        j = object_model.get_articulation("spreader_to_spinner")
        ctx.check("spinner is CONTINUOUS about +Z",
                  j.articulation_type == ArticulationType.CONTINUOUS and abs(j.axis[2]) > 0.99,
                  details=f"type={j.articulation_type} axis={tuple(j.axis)}")
        vanes = [v.name for v in object_model.get_part("spinner").visuals
                 if v.name and v.name.startswith("low_radial_spreader_vane_")]
        ctx.check("N broadcast vanes emitted (Rule 1 inline)",
                  len(vanes) == r.vane_count, details=f"vanes={sorted(vanes)} N={r.vane_count}")
    else:
        j = object_model.get_articulation("spreader_to_agitator")
        ctx.check("agitator is CONTINUOUS about +X",
                  j.articulation_type == ArticulationType.CONTINUOUS and abs(j.axis[0]) > 0.99,
                  details=f"type={j.articulation_type} axis={tuple(j.axis)}")
        holes = [v.name for v in spreader.visuals if v.name and v.name.startswith("drop_hole_")]
        ctx.check("N drop holes emitted (Rule 1 inline)",
                  len(holes) == r.drop_hole_count, details=f"holes={sorted(holes)} N={r.drop_hole_count}")

    gate_j = object_model.get_articulation("lever_to_gate")
    lever_j = object_model.get_articulation("spreader_to_lever")
    wheel_j = object_model.get_articulation("spreader_to_wheel_0")
    ctx.check(
        "core joints have expected types",
        gate_j.articulation_type == ArticulationType.PRISMATIC
        and abs(gate_j.axis[1]) > 0.99
        and lever_j.articulation_type == ArticulationType.REVOLUTE
        and wheel_j.articulation_type == ArticulationType.CONTINUOUS,
        details=f"gate={gate_j.articulation_type}/{tuple(gate_j.axis)} lever={lever_j.articulation_type} wheel={wheel_j.articulation_type}",
    )
    if r.chassis == "push_folding_handle":
        hj = object_model.get_articulation("spreader_to_handle")
        ctx.check("folding handle is REVOLUTE about X",
                  hj.articulation_type == ArticulationType.REVOLUTE and abs(hj.axis[0]) > 0.99,
                  details=f"type={hj.articulation_type} axis={tuple(hj.axis)}")

    # ---- Targeted motion poses (Rule 5). ----
    # Gate opens rearward (-y).
    rest_gate = ctx.part_world_position(gate)
    with ctx.pose({gate_j: GATE_TRAVEL * r.gate_travel_scale * 0.9}):
        open_gate = ctx.part_world_position(gate)
    if rest_gate is not None and open_gate is not None:
        ctx.check("gate opens rearward (-y)", open_gate[1] < rest_gate[1] - 0.06,
                  details=f"rest={rest_gate} open={open_gate}")

    # Lever visibly pivots (knob z moves).
    rest_knob = ctx.part_element_world_aabb(object_model.get_part("control_lever"), elem="lever_knob")
    with ctx.pose({lever_j: 0.60}):
        moved_knob = ctx.part_element_world_aabb(object_model.get_part("control_lever"), elem="lever_knob")
    if rest_knob is not None and moved_knob is not None:
        ctx.check("lever visibly pivots",
                  abs((moved_knob[0][2] + moved_knob[1][2]) - (rest_knob[0][2] + rest_knob[1][2])) * 0.5 > 0.02,
                  details=f"rest={rest_knob} moved={moved_knob}")

    # Mechanism spins (a non-axisymmetric reference element moves).
    if r.mechanism == "broadcast_spinner":
        mech = object_model.get_part("spinner")
        mj = object_model.get_articulation("spreader_to_spinner")
        ref = "low_radial_spreader_vane_0"
    else:
        mech = object_model.get_part("agitator")
        mj = object_model.get_articulation("spreader_to_agitator")
        ref = "agitator_paddle_0"
    rest_ref = ctx.part_element_world_aabb(mech, elem=ref)
    with ctx.pose({mj: math.pi / 2.0}):
        turned_ref = ctx.part_element_world_aabb(mech, elem=ref)
    if rest_ref is not None and turned_ref is not None:
        moved = (abs((turned_ref[0][0] + turned_ref[1][0]) - (rest_ref[0][0] + rest_ref[1][0])) * 0.5 > 0.01
                 or abs((turned_ref[0][1] + turned_ref[1][1]) - (rest_ref[0][1] + rest_ref[1][1])) * 0.5 > 0.01
                 or abs((turned_ref[0][2] + turned_ref[1][2]) - (rest_ref[0][2] + rest_ref[1][2])) * 0.5 > 0.01)
        ctx.check("mechanism visibly rotates", moved, details=f"rest={rest_ref} turned={turned_ref}")

    # Folding handle swings the handlebar backward/forward.
    if r.chassis == "push_folding_handle":
        handle = object_model.get_part("handle")
        hj = object_model.get_articulation("spreader_to_handle")
        rest_h = ctx.part_element_world_aabb(handle, elem="handlebar_tube")
        with ctx.pose({hj: 1.4}):
            fold_h = ctx.part_element_world_aabb(handle, elem="handlebar_tube")
        if rest_h is not None and fold_h is not None:
            ctx.check("folding handle swings handlebar",
                      abs((fold_h[0][1] + fold_h[1][1]) - (rest_h[0][1] + rest_h[1][1])) * 0.5 > 0.15,
                      details=f"rest={rest_h} fold={fold_h}")

    # ---- Ground / proportion. ----
    aabb = ctx.part_world_aabb(spreader)
    if aabb is not None:
        ctx.check("hopper reads tall enough to be a spreader", (aabb[1][2] - aabb[0][2]) > 0.35,
                  details=f"z-extent={aabb[1][2] - aabb[0][2]:.3f}")

    # ---- slot_choices recorded. ----
    ctx.check(
        "slot_choices recorded", tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    return ctx.report()


__all__ = (
    "SeedSpreaderConfig",
    "ResolvedSeedSpreaderConfig",
    "build_seed_spreader",
    "build_seeded_seed_spreader",
    "config_from_seed",
    "resolve_config",
    "run_seed_spreader_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
)
